"""Exact native and scalar-RNE audit of denominator-independent native scale."""
from fractions import Fraction as F
from itertools import product
from math import lcm, prod
from pathlib import Path
import argparse
import json
import random
import sys

import rational_feature_scale as m
from unknown_noise_decoding import Joint, DEFAULT, OTHER
from fp_reference.core import ContractError
from fp_reference.learner import ReferenceLearnerState, initial_state, observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import Evaluation, evaluate, ArithmeticUnresolved
from fp_reference.binary_arithmetic import round_binary
from fp_reference.cuda_range import SINGLE
import likelihood_information as flat

OUTPUT = m.ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_SCALE.json'


def outward(value, digits=12):
    unit = 10**digits
    top = (value.numerator*unit+value.denominator-1)//value.denominator
    return f'{top//unit}.{top%unit:0{digits}d}'


def integer_parts(control, weights, query):
    width = len(control.worlds)
    return tuple(tuple(sum(weights[j*width+k] for k, z in enumerate(control.worlds)
                           if z[query[0]]^z[query[1]] == y) for y in (0, 1))
                 for j in range(len(control.rates)))


class Audit:
    def __init__(self):
        self.triples = self.predictions = self.observations = self.words = self.half = 0
        self.zero_fixed_nonzero_gradients = 0
        self.maxima = {}
        self.coefficients_checked = set()
        self.maximum_prediction_words = self.maximum_observation_words = 0

    def numerical(self, bank, parts, targets=(0, 1)):
        bounds = m.precision_bound(int(bank.native_scale))
        for coefficient in bank.fixed:
            assert abs(round_binary(coefficient, SINGLE, bit_limit=m.BITS).value-coefficient) <= bounds['coefficient_cache']
            self.coefficients_checked.add((bank.native_scale, coefficient))
        for target in targets:
            prediction, gradient, traces = m.rounded(bank, parts, target)
            errors = m.errors(bank, parts, prediction, gradient, target)
            for name, error in errors.items():
                assert error <= bounds[name], (bank, parts, target, name, error, bounds[name])
                key = str(bank.native_scale), name
                self.maxima[key] = max(self.maxima.get(key, F(0)), error)
            pwords, gwords = len(traces[0])+7, len(traces[1])+len(gradient)
            assert pwords <= 29 and gwords <= 6+29*len(bank.rates)
            assert len(gradient) == 4*len(bank.rates)
            self.maximum_prediction_words = max(self.maximum_prediction_words, pwords)
            self.maximum_observation_words = max(self.maximum_observation_words, gwords)
            self.predictions += 1
            self.observations += 1
            self.words += pwords+gwords
            self.half += sum(width == 16 for _, width, _ in traces[0])

    def step(self, bank, bundle, control, weights, state, event, *, numerical=True):
        rules, graph, spec, _, worlds = bundle
        query, target = event[:2], event[2]
        assert state.theta == bank.fixed+tuple(F(w, sum(weights)) for w in weights)
        source = tuple(F(i == q) for q in query for i in range(bank.n))
        pairs = tuple(source[u]*source[bank.n+v] for u, v in product(range(bank.n), repeat=2))
        parts = integer_parts(control, weights, query)
        reference = m.reference(bank, parts)
        feature = tuple(bank.coefficients[j][int((z[query[0]]^z[query[1]]) != y)] for j, z in worlds for y in (0, 1))
        expected_cache = Evaluation(source+pairs+feature+reference[:2], reference[:2], reference[2:4], reference[4], reference[5:], ())
        cache = evaluate(graph, rules, state.theta, dict(zip((s.source_id for s in rules.sources), source)), (), bit_limit=m.BITS)
        assert cache == expected_cache
        assert cache.probabilities == tuple(control.forecast(weights, (*query, y)) for y in (0, 1))
        J, basis = len(bank.rates), m.gradient_basis(bank, parts, target)
        decoded_gradient = basis[:2*J]+tuple(basis[2*J+2*j+int((z[query[0]]^z[query[1]]) != target)] for j, z in worlds)
        observed = observe_event(graph, state, spec, cache, target, bit_limit=m.BITS)
        assert observed == ReferenceLearnerState(state.theta, (), decoded_gradient, 1, state.cursor+1, state.optimizer_steps)
        self.zero_fixed_nonzero_gradients += sum(c == 0 and g != 0 for c, g in zip(bank.fixed, observed.gradient_sum))
        next_weights = control.update(weights, event)
        following = commit_event(observed, spec, bit_limit=m.BITS)
        expected_theta = bank.fixed+tuple(F(w, sum(next_weights)) for w in next_weights)
        assert following == ReferenceLearnerState(expected_theta, (), (F(0),)*graph.slot_count, 0, state.cursor+1, state.optimizer_steps+1)
        if numerical:
            self.numerical(bank, parts, (target,))
        self.triples += 1
        return next_weights, following

    def report(self):
        return dict(complete_native_triples=self.triples,
            nonzero_ambient_derivatives_at_fixed_zero_coefficients=self.zero_fixed_nonzero_gradients,
            scalar_RNE_predictions=self.predictions, scalar_RNE_observations=self.observations,
            scalar_words_including_copies=self.words, half_rounding_operations=self.half,
            maximum_prediction_words=self.maximum_prediction_words,
            maximum_observation_words=self.maximum_observation_words,
            distinct_fixed_coefficient_cache_roundings=len(self.coefficients_checked),
            maximum_errors_outward={C: {name: outward(value) for (scale, name), value in self.maxima.items() if scale == C}
                                   for C in sorted({key[0] for key in self.maxima}, key=F)})


def native_audit(audit):
    rows = []
    for rates, prior in (DEFAULT, OTHER):
        for n in (2, 3, 4):
            bank = m.minimum_integer_bank(n, rates, prior)
            bundle = m.native_graph(bank)
            rules, graph, spec, theta, _ = bundle
            control = Joint(n, rates, prior)
            init = initial_state(graph, rules, theta, 7, spec=spec, bit_limit=m.BITS)
            start = audit.triples
            levels = [(control.initial, init)]
            for _ in range(2 if n < 4 else 1):
                next_level = []
                for weights, state in levels:
                    for event in product(range(n), range(n), (0, 1)):
                        next_level.append(audit.step(bank, bundle, control, weights, state, event))
                levels = next_level
            exhaustive = audit.triples-start
            weights, state = control.initial, init
            rng = random.Random(913+n)
            for k in range(80):
                if k == 4:
                    state = attach_boundary(state, 2, spec)
                event = (rng.randrange(n), rng.randrange(n), rng.randrange(2))
                weights, state = audit.step(bank, bundle, control, weights, state, event)
            assert (state.cursor, state.optimizer_steps) == (78, 80)
            count = len(rates)*(1 << (n-1))
            sums = sum(len(node.terms) for node in graph.nodes if type(node) is m.Sum)
            assert sums == 2*count*(n*n+1)
            rows.append(dict(n=n, rates=list(map(str, rates)), likelihood_scale=bank.likelihood_scale,
                native_scale=str(bank.native_scale), graph=graph.counts(), SUM_incidences=sums,
                exhaustive_native_triples=exhaustive, profile_word_triples=80,
                final_cursor=state.cursor, final_optimizer_steps=state.optimizer_steps))
    # Exact rational minimum need not be an integer. This has no inherited RNE schedule.
    rates, prior = (F(2, 5), F(3, 7)), (F(1, 3), F(2, 3))
    bank = m.Bank(2, rates, prior, F(5, 2))
    bundle = m.native_graph(bank)
    rules, graph, spec, theta, _ = bundle
    control = Joint(2, rates, prior)
    state = initial_state(graph, rules, theta, 0, spec=spec, bit_limit=m.BITS)
    weights = control.initial
    for event in ((0, 1, 0), (1, 1, 1), (1, 0, 1), (0, 0, 0))*4:
        weights, state = audit.step(bank, bundle, control, weights, state, event, numerical=False)
    try:
        m.excess_integers(bank, integer_parts(control, weights, (0, 1)))
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('noninteger native scale acquired the integer RNE schedule')
    return rows


def denominator_family(audit):
    rows = []
    for q in (3, 17, 1000000007, (1 << 200)+1):
        rates, prior = (F(1, 4), F(q+1, 4*q)), (F(1, 2),)*2
        bank = m.minimum_integer_bank(2, rates, prior)
        assert bank.native_scale == 4 and bank.likelihood_scale == 4*q
        assert bank.fixed == (2, 0, 2-F(1, q), F(1, q))
        bundle = m.native_graph(bank)
        rules, graph, spec, theta, _ = bundle
        control = Joint(2, rates, prior)
        state = initial_state(graph, rules, theta, 0, spec=spec, bit_limit=m.BITS)
        start = audit.triples
        levels = [(control.initial, state)]
        for _ in range(2):
            following = []
            for weights, before in levels:
                for event in product(range(2), range(2), (0, 1)):
                    following.append(audit.step(bank, bundle, control, weights, before, event))
            levels = following
        rows.append(dict(q=str(q), likelihood_scale_bits=bank.likelihood_scale.bit_length(),
            native_scale=4, maximum_coefficient=2, graph=graph.counts(),
            complete_native_triples=audit.triples-start))
    return rows


def rounding_boundaries(audit):
    count = 0
    for rates, prior in (DEFAULT, OTHER):
        bank = m.minimum_integer_bank(2, rates, prior)
        # Include boundary simplex points, exact zeros, and rare positive classes.
        for values in product(range(3), repeat=2*len(rates)):
            if not sum(values):
                continue
            parts = tuple(tuple(values[2*j:2*j+2]) for j in range(len(rates)))
            audit.numerical(bank, parts)
            count += 1
        for exponent in (149, 150, 151, 500, 4000):
            for index in range(2*len(rates)):
                values = [1]*(2*len(rates))
                values[index] = 1 << exponent
                audit.numerical(bank, tuple(tuple(values[2*j:2*j+2]) for j in range(len(rates))))
                count += 1
    return count


def directed_witness(audit):
    bank = m.minimum_integer_bank(2, *OTHER)
    control = Joint(2, *OTHER)
    weights = control.update(control.initial, (0, 1, 1), 2)
    parts = integer_parts(control, weights, (0, 1))
    observed = []
    for target in (0, 1):
        prediction, gradient, _ = m.rounded(bank, parts, target)
        error = m.errors(bank, parts, prediction, gradient, target)
        assert all(value < (F(1, 1000) if key in ('probability', 'proper_mass_division') else F(1, 100))
                   for key, value in error.items())
        observed.append({k: str(v) for k, v in error.items()})
    old_state = m.old.State(m.old.Model(2, *OTHER), (-2,), cursor=2, steps=2)
    plan = m.old.prepare(old_state, (0, 1))
    prediction, gradient, _ = m.old.rounded(plan, 1)
    old_error = m.old.errors(plan, prediction, gradient, 1)['native']
    assert old_error == F(65863667, 4117889024) > F(1, 100)
    assert m.reference(bank, parts)[5:] == m.old.reference(plan)[5:]
    simple = m.minimum_integer_bank(2, *DEFAULT)
    initial = Joint(2, *DEFAULT)
    diagonal = integer_parts(initial, initial.initial, (0, 0))
    zero_gradient = m.gradient_basis(simple, diagonal, 0)[1]
    assert simple.fixed[1] == 0 and zero_gradient == F(1, 20)
    # Two free simplex states, not asserted reachable from the fixed prior.
    first, second = ((30, 10), (20, 20)), ((25, 15), (28, 12))
    assert m.excess_integers(simple, first) == m.excess_integers(simple, second) == (8000, 4800)
    assert m.reference(simple, first) == m.reference(simple, second)
    difference = m.gradient_basis(simple, first, 0)[0]-m.gradient_basis(simple, second, 0)[0]
    assert difference == F(-1, 96)
    return dict(history='01:label1 twice; query01', old_S120_native_error=str(old_error),
        new_C8_errors_by_target=observed,
        fixed_zero_slot_gradient_on_initial_diagonal_label0=str(zero_gradient),
        equal_excess_different_fixed_gradient=dict(first_parts=first, second_parts=second,
            excess=(8000, 4800), normalization=80, first_fixed_gradient_difference=str(difference),
            scope='two free positive simplex states; no fixed-Gamma reachability claim'),
        scope='different native G/Gamma and passive scalar schedule; no original device verdict changed')


def general_bank_audit():
    """Unequal bases, three labels, duplicate signatures and a rational prior."""
    experts = (
        ((F(1, 2), F(1, 3), F(1, 6)), (F(1, 3), F(1, 2), F(1, 6)),
         (F(1, 5), F(2, 5), F(2, 5)), (F(1, 2), F(1, 3), F(1, 6))),
        ((F(1, 4), F(1, 4), F(1, 2)), (F(1, 2), F(1, 4), F(1, 4)),
         (F(1, 3),)*3, (F(1, 4), F(1, 4), F(1, 2))))
    bank = flat.Model(tuple(tuple(tuple(experts[x][h][y] for h in range(4)) for y in range(3)) for x in range(2)),
                      (F(1, 10), F(1, 5), F(3, 10), F(2, 5)))
    bases = (F(1), F(2), F(3))
    C = max(bases[y]/bank.table[x][y][h] for x, y in bank.events for h in range(bank.worlds))
    assert C == 18
    specs = tuple(m.SourceSpec(f'q:{x}', 'mass', 0, F(1)) for x in range(2))
    rules = m.SemanticRules(specs, ('mass',), (('mass', 'mass', 'mass'),), 'mass', bases)
    fixed_keys = tuple(product(range(2), range(3), range(4)))
    slot = {key: k for k, key in enumerate(fixed_keys)}
    fixed = tuple(C*bank.table[x][y][h]-bases[y] for x, y, h in fixed_keys)
    nodes = [m.Source(s.source_id) for s in specs]
    nodes += [m.Sum('mass', tuple(m.Term(x, slot[x, y, h]) for x in range(2))) for h in range(4) for y in range(3)]
    heads = tuple(range(len(nodes), len(nodes)+3))
    nodes += [m.Sum('mass', tuple(m.Term(2+3*h+y, len(fixed)+h) for h in range(4))) for y in range(3)]
    graph = m.Program(tuple(nodes), len(fixed)+4, heads)
    graph.validate(rules)
    spec = m.LearnerSpec(1, F(1), optimizer_id=m.SIMPLEX_GRADIENT, simplex_slots=tuple(range(len(fixed), graph.slot_count)))
    init = initial_state(graph, rules, fixed+bank.prior, 0, spec=spec, bit_limit=m.BITS)
    levels, triples = [init], 0
    for _ in range(2):
        following = []
        for state in levels:
            w = state.theta[len(fixed):]
            for x, target in bank.events:
                cache = evaluate(graph, rules, state.theta, {f'q:{k}': F(x == k) for k in range(2)}, (), bit_limit=m.BITS)
                p = tuple(bank.forecast(w, (x, y)) for y in range(3))
                masses = tuple(C*v for v in p)
                excess = tuple(v-b for v, b in zip(masses, bases))
                features = tuple(C*bank.table[x][y][h]-bases[y] for h in range(4) for y in range(3))
                assert cache == Evaluation(tuple(F(x == k) for k in range(2))+features+excess, excess, masses, C, p, ())
                gradient = tuple(F(q == x)*w[h]*(1/C-F(y == target)/masses[target]) for q, y, h in fixed_keys)
                gradient += tuple((C-sum(bases))/C-(C*bank.table[x][target][h]-bases[target])/masses[target] for h in range(4))
                observed = observe_event(graph, state, spec, cache, target, bit_limit=m.BITS)
                assert observed == ReferenceLearnerState(state.theta, (), gradient, 1, state.cursor+1, state.optimizer_steps)
                successor = commit_event(observed, spec, bit_limit=m.BITS)
                assert successor == ReferenceLearnerState(fixed+bank.step(w, (x, target)), (), (F(0),)*graph.slot_count,
                                                         0, state.cursor+1, state.optimizer_steps+1)
                following.append(successor)
                triples += 1
        levels = following
    denominator = lcm(*(v.denominator for row in bank.factors for v in row))
    calibration = []
    for h in range(4):
        word_counts = tuple(int(denominator*bank.table[x][y][h]) for x, y in bank.events)
        block = tuple(prod(bank.table[x][y][k]**count for (x, y), count in zip(bank.events, word_counts)) for k in range(4))
        group = tuple(k for k in range(4) if all(bank.table[x][y][k] == bank.table[x][y][h] for x, y in bank.events))
        assert all(block[k] == block[h] if k in group else block[k] < block[h] for k in range(4))
        repeat = 1
        while True:
            raw = tuple(pi*value**repeat for pi, value in zip(bank.prior, block))
            posterior = tuple(v/sum(raw) for v in raw)
            outside = 1-sum(posterior[k] for k in group)
            if outside < F(1, 10**8):
                break
            repeat += 1
            assert repeat <= 16
        x, y = max(bank.events, key=lambda e: bases[e[1]]/bank.table[e[0]][e[1]][h])
        limit = bases[y]/bank.table[x][y][h]
        lower = bases[y]/bank.forecast(posterior, (x, y))
        assert abs(lower-limit) < F(1, 10000)
        calibration.append(dict(hypothesis=h, identical_signature_group=group,
            block_length=sum(word_counts), repetitions=repeat,
            outside_group_mass_upper=outward(outside), limiting_normalizer_lower=str(limit),
            finite_prefix_gap_upper=outward(abs(lower-limit))))
    return dict(labels=3, queries=2, hypotheses=4, bases=list(map(str, bases)),
        sharp_scale=str(C), complete_native_triples=triples, calibration=calibration)


def main():
    audit = Audit()
    native = native_audit(audit)
    family = denominator_family(audit)
    boundaries = rounding_boundaries(audit)
    witness = directed_witness(audit)
    general = general_bank_audit()
    refused = 0
    for build in (lambda: m.Bank(2, *DEFAULT, F(9)),
                  lambda: m.native_graph(m.minimum_integer_bank(20, *DEFAULT), world_cap=4096)):
        try:
            build()
        except (ContractError, ArithmeticUnresolved):
            refused += 1
        else:
            raise AssertionError('inadmissible scale or unfunded literal expansion passed')
    assert 'torch' not in sys.modules
    return dict(status='PASS_RATIONAL_FEATURE_SCALE_NATIVE_AND_SCALAR_AUDIT', native=native,
        exact_noninteger_C5_over2_triples=16, noninteger_RNE_schedule_refused=True,
        denominator_family=family, integer_part_boundary_cases=boundaries, **audit.report(),
        all_history_bounds_outward={str(C): {k: outward(v) for k, v in m.precision_bound(C).items()} for C in (4, 8, 10)},
        directed_witness=witness, inadmissible_scale_and_materialization_refusals=refused,
        general_bank=general,
        scope='passive native G/Gamma/U and exact RNE law; no Runtime/AMP ownership, device job, lineage transport or constructor decision')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    encoded = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(encoded, encoding='utf-8')
    print(encoded)
