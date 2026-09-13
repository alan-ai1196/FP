"""Exact native-gradient study of a different, unregistered learner rule.

The categorical simplex metric and uniform initializer are explicit model
choices. This is not the Runtime's projected SGD, a proposer, or an AMP audit.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.core import ContractError
from fp_reference.learner import LearnerSpec, ce_gradient
from fp_reference.program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import evaluate
from predictive_counts import normalize, weights_from_history


def simplex_step(weights, gradient, rate=F(1)):
    assert len(weights) == len(gradient) and sum(weights) == 1 and min(weights) >= 0
    mean = sum(w*g for w, g in zip(weights, gradient))
    # No clipping or renormalization is inserted. Positivity at a unit step
    # requires the theorem's affine, equal-normalizer hypothesis.
    return tuple(w*(1-rate*(g-mean)) for w, g in zip(weights, gradient))


@lru_cache(maxsize=None)
def relation_graph(n):
    worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
    specs = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1))
                  for side in (0, 1) for i in range(n))
    rules = SemanticRules(specs, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in specs]
    def emit(node):
        nodes.append(node)
        return len(nodes)-1
    pairs = {(i, j): emit(Product('mass', i, n+j)) for i, j in product(range(n), repeat=2)}
    terms = [[], []]
    for k, z in enumerate(worlds):
        for y in (0, 1):
            indicator = emit(Sum('mass', tuple(Term(pairs[i, j], 0) for i, j in pairs if z[i]^z[j] == y)))
            # Eight actual incidences, not an unregistered coefficient slot.
            terms[y].extend([Term(indicator, k+1)]*8)
    heads = tuple(emit(Sum('mass', tuple(t))) for t in terms)
    graph = Program(tuple(nodes), len(worlds)+1, heads)
    graph.validate(rules)
    return rules, graph, worlds


def context(n, i, j):
    return {f'x{side}:{k}': F(k == value) for side, value in enumerate((i, j)) for k in range(n)}


def native_prediction(n, weights, query):
    rules, graph, _ = relation_graph(n)
    return evaluate(graph, rules, (F(1),)+weights, context(n, *query), (), bit_limit=32768)


@lru_cache(maxsize=None)
def native_history_state(n, history):
    rules, graph, worlds = relation_graph(n)
    if not history:
        # This initializer is declared for this study; Gamma1/8 from the old
        # recurrent controls does not authorize a 1/K parameter value.
        return (F(1, len(worlds)),)*len(worlds)
    weights = native_history_state(n, history[:-1])
    i, j, y = history[-1]
    prediction = native_prediction(n, weights, (i, j))
    gradient = ce_gradient(graph, (F(1),)+weights, prediction, y, bit_limit=32768)
    # Unit feature slot stays fixed by the proposed learner specification.
    result = simplex_step(weights, gradient[1:])
    assert sum(result) == 1 and min(result) > 0
    return result


def relation_audit():
    histories_checked = forecasts_checked = 0
    maximum_activation = F(0)
    maximum_weight_bits = 0
    rows = []
    for n, depth in ((2, 3), (3, 2), (4, 3)):
        rules, graph, worlds = relation_graph(n)
        if n < 4:
            alphabet = tuple(product(range(n), range(n), (0, 1)))
            histories = tuple(h for t in range(depth+1) for h in product(alphabet, repeat=t))
        else:
            patterns = (((0, 1), (1, 2), (2, 3)), ((0, 1), (1, 2), (0, 2)),
                        ((0, 1),)*3, ((0, 0),)*3)
            histories = ((),)+tuple(tuple((i, j, y) for (i, j), y in zip(pattern, labels))
                for pattern in patterns for labels in product((0, 1), repeat=3))
        for history in histories:
            weights = native_history_state(n, history)
            all_weights = weights_from_history(n, history)
            expected = normalize(all_weights[:len(worlds)])
            assert weights == expected
            maximum_weight_bits = max(maximum_weight_bits,
                *(max(w.numerator.bit_length(), w.denominator.bit_length()) for w in weights))
            full_worlds = tuple(product((0, 1), repeat=n))
            for query in product(range(n), repeat=2):
                prediction = native_prediction(n, weights, query)
                p0 = F(1, 10)+F(4, 5)*sum(w for z, w in zip(full_worlds, all_weights)
                                         if z[query[0]] == z[query[1]])/sum(all_weights)
                assert prediction.probabilities == (p0, 1-p0)
                assert prediction.normalizer == 10
                assert max(prediction.values) <= 8
                maximum_activation = max(maximum_activation, *prediction.values)
                forecasts_checked += 1
            histories_checked += 1
        rows.append({'n': n, 'history_cases': len(histories), 'graph': graph.counts(),
                     'source_rows': n*n, 'simplex_slots': len(worlds), 'fixed_feature_slots': 1,
                     'initial_simplex_value': str(F(1, len(worlds)))})
    # Long-history correctness is checked at the same small graph, with no
    # window eviction. This is exact rational work, not fixed-precision cost.
    reversal = ((0, 1, 0),)*40+((0, 1, 1),)*40
    for cut in (40, 80):
        weights = native_history_state(2, reversal[:cut])
        assert weights == normalize(weights_from_history(2, reversal[:cut])[:2])
    assert native_prediction(2, native_history_state(2, reversal), (0, 1)).probabilities == (F(1, 2),)*2
    return {'histories': histories_checked, 'native_forecasts': forecasts_checked,
            'native_gradient_successors': native_history_state.cache_info().currsize-3,
            'maximum_native_activation': str(maximum_activation), 'normalizer': '10',
            'maximum_short_case_parameter_integer_bits': maximum_weight_bits,
            'long_reversal_events': len(reversal), 'cases': rows}


def diagonal_step(weights, gradient, preconditioner, rate):
    inverse_metric = tuple(preconditioner(w) for w in weights)
    multiplier = sum(a*g for a, g in zip(inverse_metric, gradient))/sum(inverse_metric)
    return tuple(w-rate*a*(g-multiplier) for w, a, g in zip(weights, inverse_metric, gradient))


def affine_evaluation(columns, base, weights):
    heads = len(base)
    specs = tuple(SourceSpec(f'a{y}:{k}', 'mass', 0, max(F(1), F(column[y])))
                  for k, column in enumerate(columns) for y in range(heads))
    inputs = {f'a{y}:{k}': F(column[y]) for k, column in enumerate(columns) for y in range(heads)}
    rules = SemanticRules(specs, ('mass',), (('mass', 'mass', 'mass'),), 'mass', tuple(map(F, base)))
    nodes = tuple(Source(s.source_id) for s in specs)
    nodes += tuple(Sum('mass', tuple(Term(k*heads+y, k) for k in range(len(columns)))) for y in range(heads))
    graph = Program(nodes, len(weights), tuple(range(len(specs), len(nodes))))
    graph.validate(rules)
    prediction = evaluate(graph, rules, weights, inputs, (), bit_limit=32768)
    return graph, prediction


def affine_audit():
    checks = 0
    weight_cases = ((F(1, 3),)*3, (F(1, 2), F(1, 3), F(1, 6)), (F(0), F(1, 2), F(1, 2)))
    for total in (0, 1, 2, 8):
        for first in product(range(total+1), repeat=3):
            columns = tuple((a, total-a) for a in first)
            for weights in weight_cases:
                graph, prediction = affine_evaluation(columns, (1, 2), weights)
                for y in (0, 1):
                    gradient = ce_gradient(graph, weights, prediction, y, bit_limit=32768)
                    expected = normalize(tuple(w*(1+y+column[y]) for w, column in zip(weights, columns)))
                    for rate in (F(1, 4), F(1)):
                        result = simplex_step(weights, gradient, rate)
                        assert result == tuple((1-rate)*w+rate*p for w, p in zip(weights, expected))
                        assert min(result) >= 0 and sum(result) == 1
                        checks += 1
    # Non-binary readout, unequal positive base, common total coefficients.
    columns = ((0, 1, 2), (2, 1, 0), (1, 0, 2))
    weights = weight_cases[1]
    graph, prediction = affine_evaluation(columns, (1, 2, 3), weights)
    for y in range(3):
        gradient = ce_gradient(graph, weights, prediction, y, bit_limit=32768)
        assert simplex_step(weights, gradient) == normalize(tuple(w*(y+1+column[y]) for w, column in zip(weights, columns)))
        checks += 1
    return {'native_affine_gradient_steps': checks, 'includes_zero_weights': True, 'maximum_readout_labels': 3}


def refinement_audit():
    checks = 0
    for a in range(1, 7):
        for b in range(1, 8-a):
            split = (F(a, 8), F(b, 8), F(8-a-b, 8))
            merged = (split[0]+split[1], split[2])
            for p, q in product(range(3), repeat=2):
                columns = ((p, 2-p), (q, 2-q))
                left_graph, left_prediction = affine_evaluation(columns, (1, 1), merged)
                right_graph, right_prediction = affine_evaluation((columns[0],)+columns, (1, 1), split)
                assert left_prediction.probabilities == right_prediction.probabilities
                for y in (0, 1):
                    left_gradient = ce_gradient(left_graph, merged, left_prediction, y, bit_limit=32768)
                    right_gradient = ce_gradient(right_graph, split, right_prediction, y, bit_limit=32768)
                    assert right_gradient == (left_gradient[0],)+left_gradient
                    left = simplex_step(merged, left_gradient)
                    right = simplex_step(split, right_gradient)
                    assert left == (right[0]+right[1], right[2])
                    assert left == diagonal_step(merged, left_gradient, lambda w: w, F(1))
                    checks += 1
    columns = ((8, 0), (0, 8))
    coarse = (F(1, 2),)*2
    fine = (F(1, 4), F(1, 4), F(1, 2))
    results = []
    for table, weights in ((columns, coarse), ((columns[0],)+columns, fine)):
        graph, prediction = affine_evaluation(table, (1, 1), weights)
        gradient = ce_gradient(graph, weights, prediction, 0, bit_limit=32768)
        updated = diagonal_step(weights, gradient, lambda w: F(1), F(1, 8))
        assert min(updated) > 0
        results.append(updated[0] if len(updated) == 2 else updated[0]+updated[1])
    assert results == [F(3, 5), F(19, 30)]
    return {'native_split_merge_gradient_checks': checks,
            'Euclidean_tangent_step_merged_expert_weights': list(map(str, results)),
            'scope': 'identical fixed whole-continuation experts; no Compiler or physical equivalence'}


def boundaries():
    weights = (F(9, 10), F(1, 10))
    columns = ((0, 0), (0, 20))
    graph, prediction = affine_evaluation(columns, (1, 1), weights)
    gradient = ce_gradient(graph, weights, prediction, 0, bit_limit=32768)
    invalid = simplex_step(weights, gradient)
    assert invalid == (F(27, 20), F(-7, 20))
    # The latent categorical Fisher metric differs from the Fisher metric
    # of the currently visible pair forecasts. The latter has a null direction.
    n = 4
    _, graph, worlds = relation_graph(n)
    K = len(worlds)
    tangent = tuple(F((-1)**sum(z), K) for z in worlds)
    assert sum(tangent) == 0
    assert sum(v*v/F(1, K) for v in tangent) == 1
    for i, j in product(range(n), repeat=2):
        assert sum(v for z, v in zip(worlds, tangent) if z[i] == z[j]) == 0
    successors = []
    for sign in (-1, 1):
        weights = tuple(F(1, K)+sign*F(3, 5)*v for v in tangent)
        assert all(native_prediction(n, weights, pair).probabilities[0] == (F(9, 10) if pair[0] == pair[1] else F(1, 2))
                   for pair in product(range(n), repeat=2))
        first = native_prediction(n, weights, (0, 1))
        gradient = ce_gradient(graph, (F(1),)+weights, first, 0, bit_limit=32768)
        updated = simplex_step(weights, gradient[1:])
        successors.append(native_prediction(n, updated, (2, 3)).probabilities[0])
    assert successors == [F(77, 250), F(173, 250)]
    replay_predictions = tuple(native_prediction(2, native_history_state(2, ((0, 1, 0),)*passes), (0, 1)).probabilities[0]
                               for passes in (1, 2))
    assert replay_predictions == (F(41, 50), F(73, 82))
    _, fixed_graph, _ = relation_graph(2)
    uniform = (F(1, 2),)*2
    diagonal = native_prediction(2, uniform, (0, 0))
    unit_gradient = ce_gradient(fixed_graph, (F(1),)+uniform, diagonal, 0, bit_limit=32768)[0]
    assert unit_gradient == F(-4, 45)
    refused = False
    try:
        LearnerSpec(1, F(1), optimizer_id='categorical-natural-gradient-v1')
    except ContractError:
        refused = True
    assert refused
    return {'unequal_normalizers_unit_step': list(map(str, invalid)),
            'visible_pair_Fisher_null_but_categorical_norm_squared': '1',
            'same_pair_forecasts_next_label_successors': list(map(str, successors)),
            'one_record_replayed_once_or_twice': list(map(str, replay_predictions)),
            'fixed_unit_has_nonzero_native_gradient': str(unit_gradient),
            'current_Runtime_refuses_unregistered_optimizer': refused,
            'scope': 'different declared learner/initializer; no Foundation or graph-only emergence claim'}


if __name__ == '__main__':
    report = {'relation_model': relation_audit(), 'affine_law': affine_audit(),
              'refinement': refinement_audit(), 'boundaries': boundaries()}
    assert 'torch' not in sys.modules
    print(json.dumps(report, indent=2))
