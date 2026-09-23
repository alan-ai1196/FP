"""Exact noise-information, sufficient-state and native continuation audit.

The mixture is a new declared native Program, not a reinterpretation of the
fixed-noise indexed learner. No Runtime values, backend or decisions change.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement, product
from math import comb, prod
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference import CompilerPolicy, ReferenceCompilerRuntime
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.float64_bridge import Float64Contract
from fp_reference import indexed_count as known
from fp_reference.learner import ReferenceLearnerState, initial_state, observe_event, commit_event
from fp_reference.program import Program, Product, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.runtime import OnlineContract
from fp_reference.semantics import Evaluation, evaluate
from audit_reference_construction import contract, limits, validate_residency
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context
import likelihood_information as finite

NOISES = (F(1, 10), F(1, 4))
OUTPUT = ROOT/'evidence/minimal/FP_NOISE_ACQUISITION.json'


def worlds(n):
    return tuple((noise, (0,)+bits) for noise in NOISES for bits in product((0, 1), repeat=n-1))


def likelihood(noise, z, history):
    return prod((1-noise if z[i]^z[j] == y else noise for i, j, y in history), start=F(1))


def marginal(n, history, noise):
    return sum((likelihood(noise, z, history) for z in product((0, 1), repeat=n)), F(0))/2**n


def posterior(n, history):
    # Full latent assignments, independently of the anchored native graph.
    full = {(noise, z): likelihood(noise, z, history)
            for noise in NOISES for z in product((0, 1), repeat=n)}
    total = sum(full.values(), F(0))
    return tuple((full[noise, z]+full[noise, tuple(1-v for v in z)])/total for noise, z in worlds(n))


def coordinates(n, history):
    pairs = tuple(combinations(range(n), 2))
    counts = [0]*(len(pairs)+1)
    for i, j, y in history:
        at = len(pairs) if i == j else pairs.index(tuple(sorted((i, j))))
        counts[at] += 1-2*y
    return len(history), tuple(counts)


def decode(n, time, counts):
    pairs = tuple(combinations(range(n), 2))
    result = []
    for noise, z in worlds(n):
        score = counts[-1]+sum(d*(1-2*(z[i]^z[j])) for d, (i, j) in zip(counts, pairs))
        assert (time+score) % 2 == 0
        matches = (time+score)//2
        assert 0 <= matches <= time
        result.append((1-noise)**matches*noise**(time-matches))
    return finite.normalize(result)


def integer_mixture(n, time, counts):
    """Fixed-denominator positive integer lift; no histogram or normalization per rate."""
    pairs = tuple(combinations(range(n), 2))
    span = sum(abs(d) for d in counts[:-1])
    common_match = (time+counts[-1]-span)//2
    common_mismatch = (time-counts[-1]-span)//2
    assert 2*common_match == time+counts[-1]-span and min(common_match, common_mismatch) >= 0
    values = []
    for noise, z in worlds(n):
        matched, mismatched = int(20*(1-noise)), int(20*noise)
        value = matched**common_match*mismatched**common_mismatch
        for d, (i, j) in zip(counts, pairs):
            base = matched if (d >= 0) == (z[i] == z[j]) else mismatched
            value *= base**abs(d)
        values.append(value)
    assert sum(values).bit_length() <= n+5*time+1
    return finite.normalize(tuple(map(F, values)))


def lattice_count(dimension, time):
    result = int(time % 2 == 0)
    for radius in range(1, time+1):
        if radius % 2 == time % 2:
            result += sum(2**k*comb(dimension, k)*comb(radius-1, k-1)
                          for k in range(1, min(dimension, radius)+1))
    return result


def cycle_masks(n, edges):
    boundary = tuple((1 << i) ^ (1 << j) for i, j in edges)
    masks = []
    for mask in range(1 << len(edges)):
        image = 0
        for e, column in enumerate(boundary):
            if mask >> e & 1:
                image ^= column
        if image == 0:
            masks.append(mask)
    basis, pivots = [], {}
    for mask in masks[1:]:
        reduced = mask
        while reduced:
            pivot = reduced.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = reduced
                basis.append(mask)
                break
            reduced ^= pivots[pivot]
    assert len(masks) == 2**len(basis)
    return tuple(masks), tuple(basis)


def information_audit():
    graphs = checks = 0
    for n in (2, 3, 4):
        available = tuple(combinations_with_replacement(range(n), 2)) if n < 4 else tuple(combinations(range(n), 2))
        sizes = range(4) if n < 4 else range(len(available)+1)
        enumerate_edges = combinations_with_replacement if n < 4 else combinations
        for size in sizes:
            for edges in enumerate_edges(available, size):
                masks, basis = cycle_masks(n, edges)
                grouped = {}
                for labels in product((0, 1), repeat=size):
                    label_mask = sum(y << e for e, y in enumerate(labels))
                    syndrome = tuple((mask & label_mask).bit_count() % 2 for mask in basis)
                    history = tuple((i, j, y) for (i, j), y in zip(edges, labels))
                    row = []
                    for noise in (F(1, 10), F(1, 4), F(1, 2)):
                        rho = 1-2*noise
                        expected = sum(((-1)**((mask & label_mask).bit_count())*rho**mask.bit_count()
                                        for mask in masks), F(0))/2**size
                        actual = marginal(n, history, noise)
                        assert actual == expected and actual > 0
                        row.append(actual)
                        checks += 1
                    row = tuple(row)
                    assert syndrome not in grouped or grouped[syndrome][0] == row
                    grouped[syndrome] = row, grouped.get(syndrome, (None, 0))[1]+1
                assert len(grouped) == 2**len(basis)
                assert all(count == 2**(size-len(basis)) for _, count in grouped.values())
                assert all(sum(row[i]*count for row, count in grouped.values()) == 1 for i in range(3))
                graphs += 1

    # A causal choice can depend on earlier labels. Test the conditional
    # bridge claim on its actual transcript, not P(labels | final graph).
    adaptive = bridges = 0
    def visit(history):
        nonlocal adaptive, bridges
        if len(history) == 4:
            return
        at = len(history)
        query = ((0, 1) if at == 0 else (1, 2) if at == 1 else
                 ((0, 2) if history[-1][2] == 0 else (2, 3)) if at == 2 else (0, 3))
        old_edges = tuple((i, j) for i, j, _ in history)
        old_rank = len(cycle_masks(4, old_edges)[1])
        new_rank = len(cycle_masks(4, old_edges+(query,))[1])
        if new_rank == old_rank:
            for noise in NOISES:
                assert marginal(4, history+((*query, 0),), noise)/marginal(4, history, noise) == F(1, 2)
            bridges += 1
        for y in (0, 1):
            visit(history+((*query, y),))
        adaptive += 1
    visit(())
    return {'graphs': graphs, 'exact_label_noise_likelihoods': checks,
            'cycle_syndrome_fibers_checked': True, 'adaptive_pre_target_cuts': adaptive,
            'adaptive_bridge_cuts_without_noise_information': bridges}


def acquisition_audit():
    rows, comparisons = [], 0
    for length in (1, 2, 3, 8, 16, 32):
        a, b = ((1-2*noise)**length for noise in NOISES)
        gap = a-b
        chi2 = gap**2/(1-b*b)
        # For R independent cycles, chi^2=(1+chi2)^R-1. If R*chi2<1/2,
        # the geometric-series upper is <1, hence TV<1/2 and error>1/4.
        lower = F(1, 2)/chi2
        upper = F(16)/gap**2  # Chebyshev at the midpoint of the two means.
        rows.append({'cycle_length': length, 'one_cycle_TV': str(gap/2),
            'one_cycle_chi_squared': str(chi2),
            'cycles_required_for_equal_prior_error_at_most_one_quarter_lower': -(-lower.numerator//lower.denominator),
            'cycles_sufficient_via_sample_mean_upper': -(-upper.numerator//upper.denominator)})
        p, q = (1+a)/2, (1+b)/2
        for repetitions in range(1, 17):
            left = tuple(F(comb(repetitions, k))*p**k*(1-p)**(repetitions-k) for k in range(repetitions+1))
            right = tuple(F(comb(repetitions, k))*q**k*(1-q)**(repetitions-k) for k in range(repetitions+1))
            actual_chi = sum((x-y)**2/y for x, y in zip(left, right))
            error = sum(map(min, left, right))/2
            assert actual_chi == (1+chi2)**repetitions-1
            if repetitions < lower:
                assert error > F(1, 4)
            assert F(4)/(upper*gap**2) == F(1, 4)
            comparisons += 1
    return {'exact_binomial_testing_checks': comparisons, 'independent_cycle_bounds': rows}


def native_contract(n):
    bank = tuple(tuple(tuple(1-noise if z[i]^z[j] == y else noise for noise, z in worlds(n))
                       for y in (0, 1)) for i, j in product(range(n), repeat=2))
    model = finite.Model(bank, (F(1, len(worlds(n))),)*len(worlds(n)))
    _, literal, spec, scale = finite.native_graph(model)
    sources = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1)) for side in (0, 1) for i in range(n))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]
    nodes += [Product('mass', i, n+j) for i, j in product(range(n), repeat=2)]
    # The complete pair interface is native PRODUCT syntax, not an external
    # likelihood/one-hot-pair source supplied to Runtime.
    translate = lambda index: 2*n+index
    for node in literal.nodes[n*n:]:
        assert type(node) is Sum
        nodes.append(Sum('mass', tuple(Term(translate(t.parent), t.slot) for t in node.terms)))
    graph = Program(tuple(nodes), literal.slot_count, tuple(map(translate, literal.heads)))
    graph.validate(rules)
    assert scale == 20
    return model, rules, graph, spec, scale


def source_point(n, query):
    return tuple(F(i == chosen) for chosen in query for i in range(n))


def native_step(n, bundle, state, event):
    model, rules, graph, spec, scale = bundle
    i, j, y = event
    point = source_point(n, (i, j))
    actual = evaluate(graph, rules, state.theta, dict(zip((s.source_id for s in rules.sources), point)), (), bit_limit=32768)
    original = finite.cache_oracle(model, state.theta[1:], i*n+j, scale)
    pairs = tuple(point[a]*point[n+b] for a, b in product(range(n), repeat=2))
    expected = replace(original, values=point+pairs+original.values[n*n:])
    assert actual == expected
    observed = observe_event(graph, state, spec, actual, y, bit_limit=32768)
    mass = actual.masses[y]
    gradient = (1/mass-F(2, scale),)+tuple(F(scale-2, scale)-(scale*p-1)/mass for p in model.table[i*n+j][y])
    assert observed == ReferenceLearnerState(state.theta, (), gradient, 1, state.cursor+1, state.optimizer_steps)
    successor = commit_event(observed, spec, bit_limit=32768)
    assert successor.theta[0] == 1 and successor.gradient_sum == (F(0),)*graph.slot_count
    assert successor.cursor == state.cursor+1 and successor.optimizer_steps == state.optimizer_steps+1
    return successor


def state_audit():
    histories = transitions = 0
    shapes = []
    for n, depth in ((2, 3), (3, 2)):
        bundle = native_contract(n)
        model, rules, graph, spec, _ = bundle
        affine_rank = finite.Coordinates(model).rho
        assert affine_rank == n*(n-1)//2+1
        alphabet = tuple(product(range(n), range(n), (0, 1)))
        counts_by_time = []
        for time in range(depth+1):
            representatives, posterior_keys = {}, {}
            for history in product(alphabet, repeat=time):
                _, key = coordinates(n, history)
                expected = posterior(n, history)
                assert decode(n, time, key) == expected
                assert integer_mixture(n, time, key) == expected
                assert expected not in posterior_keys or posterior_keys[expected] == key
                posterior_keys[expected] = key
                representatives.setdefault(key, history)
                histories += 1
            dimension = n*(n-1)//2+1
            assert len(representatives) == lattice_count(dimension, time)
            counts_by_time.append(len(representatives))
            for history in representatives.values():
                state = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=spec, bit_limit=32768)
                for event in history:
                    state = native_step(n, bundle, state, event)
                assert state.theta[1:] == posterior(n, history)
                for event in alphabet:
                    after = native_step(n, bundle, state, event)
                    assert after.theta[1:] == posterior(n, history+(event,))
                    transitions += 1
        shapes.append({'n': n, 'coordinate_dimension': dimension, 'states_at_each_clock': counts_by_time,
                       'independent_likelihood_valuation_affine_rank': affine_rank,
                       'native_graph': graph.counts(), 'declared_noise_hypotheses': list(map(str, NOISES))})
    equal = tuple(known.commit(known.observe(known.initialize(2), 0, 0, y)) for y in (0, 1))
    assert equal[0] == equal[1]
    outcomes = []
    model = native_contract(2)[0]
    for y in (0, 1):
        weights = posterior(2, ((0, 0, y),))
        outcomes.append({'first_diagonal_label': y,
            'noise_one_tenth_posterior': str(sum(weights[:2])),
            'next_diagonal_zero_probability': str(model.forecast(weights, (0, 0)))})
    assert outcomes[0]['next_diagonal_zero_probability'] != outcomes[1]['next_diagonal_zero_probability']
    balanced = posterior(2, ((0, 1, 0), (0, 1, 1)))
    assert sum(balanced[:2]) == F(12, 37)
    model = native_contract(3)[0]
    forest_forecasts = []
    for y in (0, 1):
        weights = posterior(3, ((0, 1, y), (1, 2, 0)))
        assert sum(weights[:4]) == F(1, 2)
        forest_forecasts.append(str(model.forecast(weights, (2, 0))))
    assert forest_forecasts == ['2637/4000', '1363/4000']
    # Two actual expert likelihood ratios already preclude every single
    # rational radix: their prime-valuation vectors are independent.
    ratios = (F(9), F(5, 6))
    independent = finite.rank(tuple(tuple(finite.valuations(ratio).get(prime, 0) for prime in (2, 3, 5)) for ratio in ratios))
    assert independent == 2
    return {'history_checks': histories, 'native_full_cache_gradient_successor_checks': transitions,
        'positive_integer_mixture_checks': histories, 'single_rational_radix_obstruction_rank': independent,
        'cases': shapes, 'known_noise_committed_count_states_equal': True,
        'diagonal_continuations': outcomes, 'balanced_pair_noise_one_tenth_posterior': str(sum(balanced[:2])),
        'equal_noise_posterior_forest_different_next_query': forest_forecasts}


def runtime_case(name, n, history):
    model, rules, graph, spec, _ = native_contract(n)
    cfg = replace(contract(source_domain=False, pattern=(F(1),)+model.prior), semantics=rules,
        source_domain=tuple(source_point(n, query) for query in product(range(n), repeat=2)),
        normalizer_cap=F(22), activation_cap=F(18), reference_integer_bits=32768,
        limits=limits(byte_cap=256 << 20, work_cap=10**10))
    data = DataContract((StreamSpec('online', 'online', tuple(f'noise-{t}' for t in range(len(history)))),),
        'online', (F(1),)*(2*n), tuple(SourceRead(s.source_id, 'input', i, 0) for i, s in enumerate(rules.sources)))
    online = OnlineContract(data, spec, float64=Float64Contract(F(1, 100), F(1, 100)))
    rt = ReferenceCompilerRuntime(cfg, graph, online=online, policy=CompilerPolicy(()))
    forecasts, noise_path = [], [F(1, 2)]
    for t, (i, j, y) in enumerate(history):
        result = deliver_context(rt, f'noise-{t}', source_point(n, (i, j)))
        assert result.status == 'PREDICTED_REFERENCE', result
        snapshot = rt.snapshot()
        assert snapshot.pending.record.target is None
        p = dict(result.predictions)[snapshot.deployed_id]
        expected = posterior(n, history[:t])
        assert p == tuple(model.forecast(expected, (i*n+j, label)) for label in (0, 1))
        forecasts.append(str(p[0]))
        assert rt.observe(y).status == 'OBSERVED_REFERENCE'
        state = rt.snapshot().candidates[0].learner
        assert state.theta[1:] == posterior(n, history[:t+1])
        noise_path.append(sum(state.theta[1:1+2**(n-1)]))
    snapshot = validate_residency(rt)
    assert snapshot.run.status == 'SEALED_REFERENCE_STREAM' and snapshot.halted is None
    assert tuple(row.target for row in snapshot.observations) == tuple(y for _, _, y in history)
    assert not snapshot.reference_proofs and not snapshot.install_receipts
    phases, *_ = replay(rt)
    assert phases == 1+3*len(history)
    return {'case': name, 'events': len(history), 'status': snapshot.run.status,
        'binary64_phases': phases, 'forecast_zero_probabilities': forecasts,
        'noise_one_tenth_posterior_path': list(map(str, noise_path)),
        'host_scope': snapshot.run.host_scope, 'class_decisions': 0, 'installations': 0}


def run():
    result = {'status': 'PASS_EXACT_NOISE_ACQUISITION_AND_NATIVE_CONTINUATIONS',
        'scope': 'exact information/state law and functional Reference/binary64 evidence; no new AMP, whole-host release, search or installation claim',
        'information': information_audit(), 'acquisition': acquisition_audit(), 'state': state_audit(),
        'runtime': [runtime_case('diagonal-'+str(y), 2, ((0, 0, y), (0, 0, 0))) for y in (0, 1)]
            +[runtime_case('forest-cycle-'+str(y), 3, ((0, 1, y), (1, 2, 0), (0, 2, 0))) for y in (0, 1)]
            +[runtime_case('balanced-pair', 2, ((0, 1, 0), (0, 1, 1), (0, 0, 0)))]}
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = run()
    if args.output.exists():
        assert json.loads(args.output.read_text(encoding='utf-8')) == report
    else:
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
