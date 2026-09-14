"""Exact native audits of the distribution-wide likelihood characterization.

Polynomial substitution is a passive proof calculation. It never changes a
native Program, supplies a Runtime state, or narrows the constructor class.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).parent)]
from fp_reference.learner import LearnerSpec, SIMPLEX_GRADIENT, initial_state, observe_event, commit_event
from fp_reference.core import ContractError
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Program, Product, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import evaluate
from audit_reference_search import brute_grammar
from audit_reference_construction import rejects
from audit_likelihood_encoding import reverse_bank
import simplex_gradient as native

BITS = 32768


def affine_probability_identity(graph, rules, theta, slots, point):
    """Prove M_y = T sum_k w_k p_y(e_k) modulo sum(w)-1.

    Finite exact polynomials use K-1 free variables after substituting the
    last selected weight. Signed coefficients belong only to this auditor.
    """
    dimension = len(slots)-1
    zero = (0,)*dimension

    def constant(value):
        return {zero: F(value)} if value else {}

    def add(left, right):
        result = dict(left)
        for degree, value in right.items():
            result[degree] = result.get(degree, F(0))+value
            if not result[degree]:
                del result[degree]
        assert len(result) <= 4096
        assert all(max(x.numerator.bit_length(), x.denominator.bit_length()) <= BITS for x in result.values())
        return result

    def multiply(left, right):
        result = {}
        for a, x in left.items():
            for b, y in right.items():
                key = tuple(i+j for i, j in zip(a, b))
                result = add(result, {key: x*y})
        return result

    def total(values):
        result = {}
        for value in values:
            result = add(result, value)
        return result

    variables = [{tuple(int(i == k) for i in range(dimension)): F(1)} for k in range(dimension)]
    variables.append(add(constant(1), total(multiply(constant(-1), value) for value in variables)))
    selected = dict(zip(slots, variables))
    sources = dict(zip((s.source_id for s in rules.sources), point))
    values = []
    for node in graph.nodes:
        if type(node) is Source:
            value = constant(sources[node.source_id])
        elif type(node) is Product:
            value = multiply(values[node.left], values[node.right])
        else:
            assert type(node) is Sum and not rules.states
            value = total(multiply(selected[t.slot] if t.slot in selected else constant(theta[t.slot]), values[t.parent])
                          for t in node.terms)
        values.append(value)
    masses = tuple(add(constant(base), values[head]) for base, head in zip(rules.base, graph.heads))
    denominator = total(masses)
    experts = []
    for k in range(len(slots)):
        vertex = list(theta)
        for j, slot in enumerate(slots):
            vertex[slot] = F(j == k)
        experts.append(evaluate(graph, rules, tuple(vertex), sources, bit_limit=BITS).probabilities)
    bank = tuple(tuple(row[y] for row in experts) for y in range(len(graph.heads)))
    residuals = tuple(add(mass, multiply(constant(-1), multiply(denominator,
        total(multiply(constant(q), w) for q, w in zip(row, variables))))) for mass, row in zip(masses, bank))
    return bank, residuals


def native_unit(graph, rules, theta, slots, sources, label, rate=F(1)):
    spec = LearnerSpec(1, rate, optimizer_id=SIMPLEX_GRADIENT, simplex_slots=slots)
    state = initial_state(graph, rules, theta, 0, spec=spec, bit_limit=BITS)
    return native_event(graph, rules, state, spec, sources, label)


def native_event(graph, rules, state, spec, sources, label):
    prediction = evaluate(graph, rules, state.theta, sources, bit_limit=BITS)
    observed = observe_event(graph, state, spec, prediction, label, bit_limit=BITS)
    return prediction, observed, commit_event(observed, spec, bit_limit=BITS)


def fixtures():
    rules = SemanticRules((SourceSpec('one', 'mass', 0, F(1)),), ('mass',),
                          (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    affine = Program((Source('one'), Sum('mass', (Term(0, 1),)*8), Sum('mass', (Term(0, 2),)*8)), 3, (1, 2))
    factored = Program((Source('one'), Sum('mass', (Term(0, 1),)), Sum('mass', (Term(0, 2),)),
        Product('mass', 1, 2), Sum('mass', (Term(0, 1),)*8+(Term(3, 0),)+(Term(3, 1),)*8),
        Sum('mass', (Term(0, 2),)*8+(Term(3, 0),)+(Term(3, 2),)*8)), 3, (4, 5))
    return rules, affine, factored


def grammar_audit(max_sums):
    rules, _, _ = fixtures()
    theta, slots, point = (F(1), F(1, 2), F(1, 2)), (1, 2), (F(1),)
    graphs = tuple(g for g in brute_grammar(rules, GrammarLimits(3, max_sums, 1, 3, 3)) if g.slot_count == 3)
    accepted = additional = informative = additional_informative = units = witnesses = 0
    samples = (F(1, 5), F(1, 2), F(4, 5))
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=slots)
    for graph in graphs:
        bank, residuals = affine_probability_identity(graph, rules, theta, slots, point)
        certified = not any(residuals)
        try:
            strict = reverse_bank(graph, rules, theta, spec, (point,))
        except AssertionError:
            strict = None
        assert strict is None or certified and strict == bank
        if certified:
            accepted += 1
            additional += strict is None
            informative += any(len(set(row)) > 1 for row in bank)
            additional_informative += strict is None and any(len(set(row)) > 1 for row in bank)
            for w in samples:
                parameters = (F(1), w, 1-w)
                for label in (0, 1):
                    predicted, _, committed = native_unit(graph, rules, parameters, slots, {'one': F(1)}, label)
                    mixture = tuple(sum(p*q for p, q in zip(parameters[1:], row)) for row in bank)
                    assert predicted.probabilities == mixture
                    posterior = tuple(p*q/mixture[label] for p, q in zip(parameters[1:], bank[label]))
                    assert committed.theta == (F(1),)+posterior
                    units += 1
        else:
            degree = max(sum(key) for row in residuals for key in row)
            found = False
            for index in range(degree+1):
                w = F(index+1, degree+2)
                predicted = evaluate(graph, rules, (F(1), w, 1-w), {'one': F(1)}, bit_limit=BITS)
                mixture = tuple(w*row[0]+(1-w)*row[1] for row in bank)
                found |= predicted.probabilities != mixture
            assert found, 'symbolic refusal has no independent native witness'
            witnesses += 1
    return {'maximum_SUMs': max_sums, 'complete_three_slot_graphs': len(graphs), 'normalized_affine_certificates': accepted,
            'informative_certificates': informative, 'beyond_strict_affine_mass_verifier': additional,
            'informative_beyond_strict_verifier': additional_informative,
            'exact_native_unit_checks': units, 'native_nonaffinity_witnesses': witnesses,
            'source_domain': ['one=1'], 'fixed_feature': '1', 'selected_slots': [1, 2]}


def nonlinear_audit():
    rules, affine, factored = fixtures()
    slots, sources = (1, 2), {'one': F(1)}
    theta = (F(1), F(1, 2), F(1, 2))
    first, second = (affine_probability_identity(g, rules, theta, slots, (F(1),)) for g in (affine, factored))
    assert first[0] == second[0] == ((F(9, 10), F(1, 10)), (F(1, 10), F(9, 10)))
    assert not any(first[1]) and not any(second[1])
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=slots)
    rejects(lambda: reverse_bank(factored, rules, theta, spec, ((F(1),),)), AssertionError)
    transitions = 0
    for labels in product((0, 1), repeat=5):
        states = tuple(initial_state(g, rules, theta, 0, spec=spec, bit_limit=BITS) for g in (affine, factored))
        for cursor, label in enumerate(labels):
            a, b = (native_event(g, rules, state, spec, sources, label) for g, state in zip((affine, factored), states))
            assert a[0].probabilities == b[0].probabilities and a[2].theta == b[2].theta
            assert a[1].gradient_sum[1:] == b[1].gradient_sum[1:]
            states = a[2], b[2]
            assert all(s.cursor == s.optimizer_steps == cursor+1 for s in states)
            transitions += 1
    # A reachable second observed phase has different complete gradients even
    # though both current forecasts and selected-coordinate updates coincide.
    states = tuple(native_unit(g, rules, theta, slots, sources, 0)[2] for g in (affine, factored))
    a, b = (native_event(g, rules, state, spec, sources, 0) for g, state in zip((affine, factored), states))
    assert a[1].gradient_sum[0] == 0 and b[1].gradient_sum[0] == F(144, 22345)
    assert a[1].cursor == b[1].cursor == 2 and a[1].optimizer_steps == b[1].optimizer_steps == 1
    assert a[0].normalizer != b[0].normalizer
    implied = []
    half = LearnerSpec(1, F(1, 2), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=slots)
    state = initial_state(affine, rules, theta, 0, spec=half, bit_limit=BITS)
    for w in (F(1, 2), F(7, 10)):
        assert state.theta[1] == w
        state = native_event(affine, rules, state, half, sources, 0)[2]
        after = state.theta
        implied.append(after[1]/after[2]*(1-w)/w)
    assert implied == [F(7, 3), F(39, 19)]
    rejects(lambda: native_unit(affine, rules, theta, slots, sources, 0, F(2)), ContractError)
    return {'common_factor': '1+w1*w2 at fixed feature t=1',
            'equal_native_forecast_and_selected_update_pairs': transitions,
            'strict_mass_verifier_refuses': True,
            'reachable_fixed_slot_gradients': ['0', '144/22345'],
            'half_rate_incompatible_fixed_likelihood_ratios': list(map(str, implied)),
            'double_rate_registration_refusal': True}


def multivariate_audit():
    rules, graph, worlds = native.relation_graph(3)
    slots = tuple(range(1, len(worlds)+1))
    theta = (F(1),)+(F(1, len(worlds)),)*len(worlds)
    rows = 0
    for i, j in product(range(3), repeat=2):
        source = native.context(3, i, j)
        bank, residuals = affine_probability_identity(graph, rules, theta, slots, tuple(source.values()))
        assert not any(residuals)
        for weights in ((F(1, 4),)*4, (F(1, 2), F(1, 4), F(1, 8), F(1, 8))):
            for label in (0, 1):
                predicted, _, state = native_unit(graph, rules, (F(1),)+weights, slots, source, label)
                assert predicted.probabilities == tuple(sum(w*p for w, p in zip(weights, row)) for row in bank)
                assert state.theta[1:] == tuple(w*p/predicted.probabilities[label] for w, p in zip(weights, bank[label]))
                rows += 1
    return {'four_world_complete_source_rows': 9, 'multivariate_native_units': rows}


def reachable_orbit_audit():
    rules, _, _ = fixtures()
    affine = Program((Source('one'), Sum('mass', (Term(0, 1),)*8),
        Sum('mass', (Term(0, 2),)*8+(Term(0, 3),)*8)), 4, (1, 2))
    curved = Program((Source('one'), Sum('mass', (Term(0, 2),)), Sum('mass', (Term(0, 3),)),
        Product('mass', 1, 1), Product('mass', 2, 2), Product('mass', 1, 2),
        Sum('mass', (Term(0, 1),)*8+(Term(3, 0), Term(4, 0))+(Term(5, 1),)*16),
        Sum('mass', (Term(0, 2),)*8+(Term(0, 3),)*8+(Term(5, 0),)*2
            +(Term(5, 2),)*16+(Term(5, 3),)*16)), 4, (6, 7))
    theta, slots, sources = (F(1), F(1, 3), F(1, 3), F(1, 3)), (1, 2, 3), {'one': F(1)}
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=slots)
    _, residuals = affine_probability_identity(curved, rules, theta, slots, (F(1),))
    assert any(residuals), 'the distribution-wide criterion must reject this nonaffine readout'
    checked = 0
    for labels in product((0, 1), repeat=5):
        states = tuple(initial_state(g, rules, theta, 0, spec=spec, bit_limit=BITS) for g in (affine, curved))
        for cursor, label in enumerate(labels):
            a, b = (native_event(g, rules, state, spec, sources, label) for g, state in zip((affine, curved), states))
            assert a[0].probabilities == b[0].probabilities and a[2].theta == b[2].theta
            assert a[1].gradient_sum[1:] == b[1].gradient_sum[1:]
            assert b[2].theta[2] == b[2].theta[3]
            states = a[2], b[2]
            assert all(s.cursor == s.optimizer_steps == cursor+1 for s in states)
            checked += 1
    a, b = (native_unit(g, rules, theta, slots, sources, 0) for g in (affine, curved))
    assert b[2].theta[1:] == (F(9, 11), F(1, 11), F(1, 11))
    assert a[1].gradient_sum[0] == 0 and b[1].gradient_sum[0] == F(-8, 605)
    outside = (F(1), F(1, 2), F(3, 8), F(1, 8))
    a, b = (evaluate(g, rules, outside, sources, bit_limit=BITS) for g in (affine, curved))
    assert a.probabilities[0] == F(1, 2) and b.probabilities[0] == F(177, 352)
    return {'invariant': 'w2=w3', 'informative_native_update_pairs': checked,
            'first_selected_successor': ['9/11', '1/11', '1/11'],
            'full_simplex_identity_rejects': True,
            'outside_invariant_forecasts': ['1/2', '177/352'],
            'initial_fixed_slot_gradients': ['0', '-8/605']}


def audit():
    result = {'status': 'PASS', 'arithmetic': 'exact Fraction and native32768-bit guards',
              'grammar_audits': [grammar_audit(1), grammar_audit(2)], 'nonlinear': nonlinear_audit(),
              'multivariate': multivariate_audit(), 'reachable_orbit_counterexample': reachable_orbit_audit()}
    assert 'torch' not in sys.modules
    result['scope'] = 'distribution-wide exact theorem and passive polynomial audit; no Runtime extension or complete-state quotient'
    return result


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
