"""Exact all-coordinate audit of joint-noise excess partitions and RNE readout."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

import mixture_partition_bridge as m
from fp_reference.core import ContractError
from fp_reference.learner import ReferenceLearnerState, initial_state, observe_event, commit_event
from fp_reference.program import Program, Product, Source, SourceSpec, SemanticRules, Sum, Term
from fp_reference.semantics import Evaluation, evaluate, ArithmeticUnresolved
from fp_reference.profile import attach_boundary
from fp_reference.indexed_relation import DecodeAllowance
from unknown_noise_decoding import Joint, DEFAULT, OTHER
from shared_noise_factor_closure import counter_states, forest_decode, OutsideForest
import likelihood_information as flat
import noise_acquisition as previous
import audit_packed_count_histogram as histogram_oracle

OUTPUT = m.ROOT/'evidence/minimal/FP_MIXTURE_PARTITION_BRIDGE.json'


def outward(value):
    scale = 10**9
    numerator = (value.numerator*scale+value.denominator-1)//value.denominator
    return f'{numerator//scale}.{numerator%scale:09d}'


class Audit:
    def __init__(self):
        self.predictions = self.observations = self.words = self.half = 0
        self.maxima = {}

    def check(self, plan):
        bound = m.precision_bound(plan.before.model.scale)
        prediction, _, traces = m.rounded(plan)
        assert len(traces[0])+7 == plan.output_cells <= 29
        self.predictions += 1
        self.words += plan.output_cells
        self.half += sum(width == 16 for _, width, _ in traces[0])
        for y in (0, 1):
            arithmetic = m.amp._Arithmetic(m.BITS)
            gradient, _ = m.observation_schedule(plan, prediction, y, arithmetic)
            errors = m.errors(plan, prediction, gradient, y)
            for key, error in errors.items():
                assert error <= bound[key], (plan.before, plan.query, y, key, error, bound[key])
                self.maxima[key] = max(self.maxima.get(key, F(0)), error)
            self.observations += 1
            self.words += len(arithmetic.trace)+len(gradient)
        return prediction

    def report(self):
        return {'predictions': self.predictions, 'both_target_observations': self.observations,
                'floating_words_including_copies': self.words, 'half_words': self.half,
                'maximum_errors_exact': {k: str(v) for k, v in self.maxima.items()}}


def small_native(model):
    n = model.n
    worlds = tuple((j, (0,)+z) for j in range(len(model.rates)) for z in product((0, 1), repeat=n-1))
    table = tuple(tuple(tuple(1-model.rates[j] if z[u]^z[v] == y else model.rates[j]
                             for j, z in worlds) for y in (0, 1)) for u, v in product(range(n), repeat=2))
    bank = flat.Model(table, tuple(model.prior[j]/2**(n-1) for j, _ in worlds))
    _, old, spec, scale = flat.native_graph(bank)
    sources = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1)) for side in (0, 1) for i in range(n))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]
    nodes += [Product('mass', u, n+v) for u, v in product(range(n), repeat=2)]
    nodes += [Sum('mass', tuple(Term(t.parent+2*n, t.slot) for t in node.terms)) for node in old.nodes[n*n:]]
    graph = Program(tuple(nodes), old.slot_count, tuple(h+2*n for h in old.heads))
    graph.validate(rules)
    assert scale == model.scale
    if (model.rates, model.prior) == DEFAULT:
        assert (bank, rules, graph, spec, scale) == previous.native_contract(n)
    return bank, rules, graph, spec, worlds


def full_cache(plan, worlds):
    model = plan.before.model
    query = plan.query
    point = tuple(F(i == q) for q in query for i in range(model.n))
    pairs = tuple(point[u]*point[model.n+v] for u, v in product(range(model.n), repeat=2))
    features = tuple(F(plan.coefficients[j][int((z[query[0]]^z[query[1]]) != y)])
                     for j, z in worlds for y in (0, 1))
    values = m.reference(plan)
    return Evaluation(point+pairs+features+values[:2], values[:2], values[2:4], values[4], values[5:], ())


def full_gradient(plan, worlds, target, basis=None):
    basis = m.gradient_reference(plan, target) if basis is None else basis
    return (basis[0],)+tuple(basis[1+2*j+int((z[plan.query[0]]^z[plan.query[1]]) != target)] for j, z in worlds)


def native_step(bundle, before, state, query, target, audit):
    bank, rules, graph, spec, worlds = bundle
    assert (state.cursor, state.optimizer_steps, state.unit_count) == (before.cursor, before.steps, 0)
    plan = m.prepare(before, query)
    weights = tuple(m.weight(plan, j, z) for j, z in worlds)
    assert state.theta == (F(1),)+weights
    point = previous.source_point(before.model.n, query)
    cache = evaluate(graph, rules, state.theta, dict(zip((s.source_id for s in rules.sources), point)), (), bit_limit=m.BITS)
    assert cache == full_cache(plan, worlds)
    observed = observe_event(graph, state, spec, cache, target, bit_limit=m.BITS)
    assert observed == ReferenceLearnerState(state.theta, (), full_gradient(plan, worlds, target), 1, before.cursor+1, before.steps)
    encoded_observed = m.observe(before, query, target)
    m.check_observation_binding(plan, before, query, target, encoded_observed)
    prediction = audit.check(plan)
    arithmetic = m.amp._Arithmetic(m.BITS)
    actual_gradient, _ = m.observation_schedule(plan, prediction, target, arithmetic)
    point_gradient = full_gradient(plan, worlds, target, tuple(v.value for v in actual_gradient))
    assert max(abs(a-b) for a, b in zip(observed.gradient_sum, point_gradient)) <= m.precision_bound(before.model.scale)['gradient']
    next_count = m.commit(encoded_observed)
    following = commit_event(observed, spec, bit_limit=m.BITS)
    successor = m.prepare(next_count, query)
    expected = (F(1),)+tuple(m.weight(successor, j, z) for j, z in worlds)
    assert following == ReferenceLearnerState(expected, (), (F(0),)*graph.slot_count, 0, next_count.cursor, next_count.steps)
    assert following.theta[1:] == bank.step(state.theta[1:], (query[0]*before.model.n+query[1], target))
    return next_count, following, plan


def integer_audit(audit):
    rows = []
    for rates, prior in (DEFAULT, OTHER):
        cuts = partitions = worlds = forest_checks = cyclic_queries = 0
        largest_bits = largest_tape = 0
        for n in (2, 3, 4):
            model = m.Model(n, rates, prior)
            independent = Joint(n, rates, prior)
            for total, states in counter_states(len(model.edges)+1, 3):
                for counts in sorted(states):
                    before = m.State(model, counts[:-1], counts[-1], cursor=total, steps=total)
                    expected_weights = independent.counts(total, counts[:-1], counts[-1])
                    for query in product(range(n), repeat=2):
                        plan = m.prepare(before, query)
                        parts = tuple(tuple(sum(w for w, (eta, z) in zip(expected_weights, independent.hypotheses)
                                                if eta == rate and z[query[0]]^z[query[1]] == bit)
                                            for bit in (0, 1)) for rate in rates)
                        assert plan.rate_parts == parts and plan.normalization == sum(expected_weights)
                        assert m.reference(plan)[5:] == tuple(independent.forecast(expected_weights, (*query, y)) for y in (0, 1))
                        try:
                            forest = forest_decode(n, total, counts[:-1], counts[-1], query, rates, prior)
                        except OutsideForest:
                            cyclic_queries += 1
                        else:
                            assert forest['parts'] == parts
                            forest_checks += 1
                        partitions += 1
                        largest_bits = max(largest_bits, dict(plan.integer_stats)['maximum_integer_bits'])
                        largest_tape = max(largest_tape, plan.tape_nodes)
                        if query in ((0, 0), (0, n-1)):
                            audit.check(plan)
                        if query == (0, 0):
                            for at, (eta, z) in enumerate(independent.hypotheses):
                                assert m.weight(plan, rates.index(eta), z) == F(expected_weights[at], sum(expected_weights))
                                worlds += 1
                    cuts += 1
        rows.append({'rates': tuple(map(str, rates)), 'prior': tuple(map(str, prior)),
                     'all_reachable_cuts_n2_to_n4_through_time3': cuts,
                     'all_ordered_query_partition_pairs': partitions, 'full_weight_points': worlds,
                     'independent_forest_comparisons': forest_checks, 'cyclic_queries_now_decoded': cyclic_queries,
                     'maximum_integer_bits': largest_bits, 'maximum_tape_nodes': largest_tape})
    return rows


def native_audit(audit):
    rows = []
    for n, (rates, prior) in ((2, DEFAULT), (3, DEFAULT), (2, OTHER)):
        model = m.Model(n, rates, prior)
        bundle = small_native(model)
        bank, rules, graph, spec, worlds = bundle
        count = m.initialize(model, birth=7)
        initial = initial_state(graph, rules, (F(1),)+bank.prior, 7, spec=spec, bit_limit=m.BITS)
        levels = [(count, initial)]
        triples = 0
        for _ in range(2):
            following = []
            for count, state in levels:
                for u, v, y in product(range(n), range(n), (0, 1)):
                    after, native_after, _ = native_step(bundle, count, state, (u, v), y, audit)
                    following.append((after, native_after))
                    triples += 1
            levels = following
        rows.append({'n': n, 'rates': tuple(map(str, rates)), 'birth_cursor': 7,
                     'complete_native_triples': triples, 'native_graph': graph.counts()})
    # Actual changing support, long reinforcement, profile clock and reversal.
    model = m.Model(3, *DEFAULT)
    bundle = small_native(model)
    bank, rules, graph, spec, _ = bundle
    count = m.initialize(model)
    state = initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=m.BITS)
    word = ((0, 1, 0), (1, 2, 0))*2+((0, 2, 1),)*36+((0, 2, 0),)*36+((2, 2, 1),)*4
    maxima = {key: F(0) for key in m.precision_bound(model.scale)}
    for index, (u, v, y) in enumerate(word):
        if index == 4:
            count, state = m.attach(count, 2), attach_boundary(state, 2, spec)
        count, state, plan = native_step(bundle, count, state, (u, v), y, audit)
        prediction, gradient, _ = m.rounded(plan, y)
        for key, value in m.errors(plan, prediction, gradient, y).items():
            maxima[key] = max(maxima[key], value)
    assert count.cursor == 78 and count.steps == 80
    assert count.counts == (2, 0, 2) and count.diagonal == -4
    rows.append({'n': 3, 'word': '01:0,12:0 twice; attach cursor2; 02:1 x36; 02:0 x36; 22:1 x4',
                 'complete_native_triples': len(word), 'final_cursor': count.cursor, 'final_steps': count.steps,
                 'final_counts': count.counts, 'final_diagonal': count.diagonal,
                 'maximum_errors_exact': {k: str(v) for k, v in maxima.items()}})
    return rows


def witnesses(audit):
    # The old A1 refusal remains terminal. This is a different passive schedule
    # at the same mathematical cut, not a resumption of its owned device job.
    rows = []
    for name, rates_prior, total, count in (('old-A1-step29-cut', DEFAULT, 29, 29),
                                          ('scale120-two-label-one-events', OTHER, 2, -2)):
        model = m.Model(2, *rates_prior)
        cursor = total-2 if name == 'old-A1-step29-cut' else total
        before = m.State(model, (count,), cursor=cursor, steps=total)
        plan = m.prepare(before, (0, 1))
        bank, rules, graph, spec, worlds = small_native(model)
        state = initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=m.BITS)
        inputs = dict(zip((s.source_id for s in rules.sources), previous.source_point(2, (0, 1))))
        for step in range(total):
            if name == 'old-A1-step29-cut' and step == 4:
                state = attach_boundary(state, 2, spec)
            cache = evaluate(graph, rules, state.theta, inputs, (), bit_limit=m.BITS)
            observed = observe_event(graph, state, spec, cache, int(count < 0), bit_limit=m.BITS)
            point = previous.source_point(2, (0, 1))
            original = flat.cache_oracle(bank, state.theta[1:], 1, model.scale)
            assert cache == replace(original, values=point+tuple(point[u]*point[2+v]
                for u, v in product(range(2), repeat=2))+original.values[4:])
            mass = cache.masses[int(count < 0)]
            gradient_exact = (1/mass-F(2, model.scale),)+tuple(F(model.scale-2, model.scale)
                -(model.scale*p-1)/mass for p in bank.table[1][int(count < 0)])
            assert observed == ReferenceLearnerState(state.theta, (), gradient_exact, 1, state.cursor+1, state.optimizer_steps)
            expected = bank.step(state.theta[1:], (1, int(count < 0)))
            state = commit_event(observed, spec, bit_limit=m.BITS)
            assert state == ReferenceLearnerState((F(1),)+expected, (), (F(0),)*graph.slot_count, 0,
                                                   step+1-(2 if name == 'old-A1-step29-cut' and step >= 4 else 0), step+1)
        assert state.theta[1:] == tuple(m.weight(plan, j, z) for j, z in worlds)
        assert (state.cursor, state.optimizer_steps) == (before.cursor, before.steps)
        cache = evaluate(graph, rules, state.theta, inputs, (), bit_limit=m.BITS)
        assert cache == full_cache(plan, worlds)
        for target in (0, 1):
            observed = observe_event(graph, state, spec, cache, target, bit_limit=m.BITS)
            assert observed == ReferenceLearnerState(state.theta, (), full_gradient(plan, worlds, target),
                                                    1, before.cursor+1, before.steps)
        prediction, gradient, _ = m.rounded(plan, 0)
        errors = m.errors(plan, prediction, gradient, 0)
        audit.check(plan)
        if name == 'old-A1-step29-cut':
            assert all(value < (F(1, 1000) if key in ('probability', 'proper_mass_division') else F(1, 100))
                       for key, value in errors.items())
        else:
            assert errors['native'] == F(65863667, 4117889024) > F(1, 100)
            assert errors['probability'] < F(1, 1000)
        rows.append({'case': name, 'native_scale': model.scale, 'complete_counts': (total, count, 0),
                     'ordinary_cursor': before.cursor, 'witness_prefix_native_triples': total,
                     'final_full_native_predictions': 1, 'final_full_native_observations': 2,
                     'prediction_words': tuple(v.word for v in prediction),
                     'exact_errors': {k: str(v) for k, v in errors.items()}})
    # Two positive parts with a separation beyond binary32's exponent range.
    # A known-rate diagonal gives a genuine zero part; counts remain intact.
    for rates_prior, query in (((DEFAULT[0][:1], (F(1),)), (0, 0)),
                               ((DEFAULT[0][:1], (F(1),)), (0, 1))):
        model = m.Model(2, *rates_prior)
        state = m.State(model, (396,), cursor=396, steps=396)
        plan = m.prepare(state, query)
        prediction = audit.check(plan)
        assert prediction[1].value == 0
    model = m.Model(2, (F(1, 10), F(1, 5)), (F(1, 2), F(1, 2)))
    saturated = m.State(model, (1000,), cursor=1000, steps=1000)
    recovered = m.State(model, (0,), cursor=2000, steps=2000)
    plans = m.prepare(saturated, (0, 1)), m.prepare(recovered, (0, 1))
    first, second = (audit.check(plan) for plan in plans)
    assert plans[0].excess_parts[1] > 0 and first[1].value == 0
    assert tuple(v.value for v in second[5:]) == (F(1, 2), F(1, 2))
    rate_mass = F(sum(plans[1].rate_parts[0]), plans[1].normalization)
    assert rate_mass == F(9**1000, 9**1000+16**1000) < F(1, 2)
    rows.append({'case': 'mixed-rate-temporary-underflow-and-reversal', 'rates': ['1/10', '1/5'],
                 'declared_reachable_word': '01 label0 x1000, then label1 x1000',
                 'first_exact_excess_one_positive': True, 'first_rounded_excess_one_word': first[1].word,
                 'recovered_probability_words': tuple(v.word for v in second[5:]),
                 'recovered_counts': (recovered.steps, recovered.counts[0], recovered.diagonal),
                 'recovered_first_rate_mass_formula': '9^1000/(9^1000+16^1000)',
                 'scope': 'two exact/RNE snapshots and independent repeated-word likelihood; no 2000-event device trajectory'})
    model = m.Model(3, *DEFAULT)
    initial = m.initialize(model)
    left = m.commit(m.observe(initial, (0, 1), 0))
    right = m.commit(m.observe(initial, (1, 2), 0))
    a, b = m.prepare(left, (0, 2)), m.prepare(right, (0, 2))
    assert a.excess_parts == b.excess_parts == (720, 720)
    assert a.normalization == b.normalization == 80 and m.reference(a) == m.reference(b)
    future = tuple(m.reference(m.prepare(s, (0, 1)))[5] for s in (left, right))
    assert future == (F(289, 400), F(1, 2))
    rows.append({'case': 'equal-current-excesses-are-not-a-persistent-state',
                 'left_history': '01 label0', 'right_history': '12 label0',
                 'current_query': (0, 2), 'equal_excess_integers': a.excess_parts,
                 'equal_normalization': a.normalization, 'next_query': (0, 1),
                 'different_next_zero_probabilities': tuple(map(str, future))})
    return rows


def larger_cyclic_audit(audit):
    rows = []
    for n in (32, 64):
        old, query = histogram_oracle.fixture(n, 'band')
        histogram = histogram_oracle.band_oracle(old, query, 2)
        height = sum(map(abs, old.counts))
        for rates, prior in (DEFAULT, OTHER):
            model = m.Model(n, rates, prior)
            before = m.State(model, old.counts, diagonal=-3, cursor=height+7, steps=height+7)
            plan = m.prepare(before, query)
            parts = []
            for eta, pi in zip(rates, prior):
                a, b = int(model.scale*eta), int(model.scale*(1-eta))
                constant = int(pi*model.prior_scale)*b**2*a**5
                parts.append(tuple(constant*sum(multiplicity*a**(height-energy)*b**energy
                    for energy, multiplicity in part) for part in histogram))
            assert plan.rate_parts == tuple(parts)
            audit.check(plan)
            rows.append({'n': n, 'rates': tuple(map(str, rates)), 'steps': before.steps,
                         'diagonal': before.diagonal, 'query': query, 'native_worlds': str(len(rates)*2**(n-1)),
                         'prediction_outputs': plan.output_cells, 'tape_nodes': plan.tape_nodes,
                         'integer_envelope': plan.integer_envelope, 'table_geometry_per_rate': dict(plan.shape),
                         'tape_value_slots_per_rate': plan.tape_nodes, 'integer_evaluation': dict(plan.integer_stats),
                         'oracle': 'independent vertex/energy coefficient DP, evaluated at every rational rate'})
    return rows


def refusal_audit():
    before = m.initialize(m.Model(3, *DEFAULT))
    plan = m.prepare(before, (0, 1))
    observed = m.observe(before, (0, 1), 0)
    cost = dict(plan.integer_stats)
    whole_operations = cost['positive_multiplications']+cost['positive_additions']
    assert whole_operations-1 >= dict(plan.shape)['positive_multiplications']+dict(plan.shape)['positive_additions']
    checks = [lambda: m.check_observation_binding(plan, before, (0, 1), 1, observed),
              lambda: m.check_observation_binding(plan, before, (1, 0), 0, observed),
              lambda: m.check_observation_binding(plan, replace(before, cursor=1), (0, 1), 0, observed),
              lambda: m.check_observation_binding(plan, before, (0, 1), 0, replace(observed, cursor=2)),
              lambda: m.check_observation_binding(plan, before, (0, 1), 0,
                   replace(observed, model=m.Model(3, tuple(reversed(DEFAULT[0])), DEFAULT[1]))),
              lambda: m.attach(observed, 3), lambda: m.prepare(observed, (0, 1)),
              lambda: m.rounded(plan, prediction_output_cap=plan.output_cells-1),
              lambda: m.rounded(plan, 0, observation_output_cap=6+8*len(before.model.rates)-1),
              lambda: m.prediction_schedule(plan, m.amp._Arithmetic(2048)),
              lambda: m.prepare(before, (0, 1), tape_cap=1),
              lambda: m.prepare(before, (0, 1), budget=DecodeAllowance(arithmetic=1)),
              lambda: m.prepare(before, (0, 1), budget=DecodeAllowance(arithmetic=whole_operations-1)),
              lambda: m.prepare(m.State(m.Model(2, *DEFAULT), (1000,), cursor=1000, steps=1000),
                                (0, 1), budget=DecodeAllowance(integer_bits=64)),
              lambda: m.prepare(m.State(m.Model(16, *DEFAULT), (1,)*120, cursor=120, steps=120), (0, 1))]
    for check in checks:
        try:
            check()
        except (ContractError, ArithmeticUnresolved):
            pass
        else:
            raise AssertionError('unsupported or substituted complete input was accepted')
    assert before == m.initialize(before.model) and observed == m.observe(before, (0, 1), 0)
    return {'distinct_binding_or_resource_refusals': len(checks), 'input_states_unchanged': True,
            'dense_n16_4096_join_status': 'UNRESOLVED'}


def run():
    audit = Audit()
    integer = integer_audit(audit)
    native = native_audit(audit)
    cases = witnesses(audit)
    larger = larger_cyclic_audit(audit)
    refusals = refusal_audit()
    bounds = {str(scale): {key: outward(value) for key, value in m.precision_bound(scale).items()}
              for scale in (10, 20, 40, 120)}
    assert all(v <= (F(1, 1000) if k in ('probability', 'proper_mass_division') else F(1, 100))
               for k, v in m.precision_bound(20).items())
    assert 'torch' not in sys.modules
    return {'status': 'PASS_SCOPED_JOINT_EXCESS_BRIDGE', 'arithmetic_identity': m.IDENTITY,
            'precision': 'exact integers/Fraction native oracle and scalar RNE16/RNE32; no actual CUDA',
            'integer_decoding': integer, 'native_continuations': native, 'rounding': audit.report(),
            'larger_cyclic_decoding': larger,
            'uniform_bounds_outward': bounds, 'directed_witnesses': cases, 'refusals': refusals,
            'scope': 'Complete native coordinate basis and conditional all-history arithmetic bound for this schedule. No owned Runtime, new semantic Program/U, supplied reference posterior, constructor certificate or physical release.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(encoded, encoding='utf-8', newline='\n')
    print(json.dumps({'status': result['status'], 'rounding': result['rounding'], 'bounds': result['uniform_bounds_outward'],
                      'artifact_bytes': len(encoded.encode('utf-8'))}, indent=2))
