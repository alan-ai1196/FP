"""Exact audit of the relation-forecast to unweighted MAX CUT reduction.

This is a mathematical decoder audit, not a Runtime, source producer, fresh
evidence protocol, timing experiment, or proof that a fixed job cannot finish.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from simplex_gradient import relation_graph, context
from fp_reference.learner import (LearnerSpec, SIMPLEX_GRADIENT, initial_state,
                                  observe_event, commit_event)
from fp_reference.semantics import evaluate

ERRORS = (F(0), F(1, 1000), F(39, 100), F(399, 1000))


def boost(n, error):
    assert 0 <= error < F(2, 5)
    gamma = F(1, 2)-error/F(4, 5)
    repetitions, factor = 0, 1
    while gamma*factor < 2**n:
        repetitions += 1
        factor *= 9
    return gamma, repetitions, factor


def allowed_labels(probability, error):
    """Every threshold decision possible for any valid approximate forecast.

    The decoder chooses 1 at a tie of one half; choosing 0 requires a strict
    inequality. The two endpoints also witness the respective choices.
    """
    assert F(1, 10) <= probability <= F(9, 10)
    return tuple(y for y, allowed in ((0, probability-error < F(1, 2)),
                                      (1, probability+error >= F(1, 2))) if allowed)


def count_weights(worlds, pairs, counts):
    exponents = tuple(sum(d for (i, j), d in zip(pairs, counts) if z[i] == z[j])
                      for z in worlds)
    low = min(exponents)
    return tuple(9**(v-low) for v in exponents)


def same_weights(left, right):
    # Compare exact ratios without manufacturing expected native successors.
    assert len(left) == len(right) and min(left) > 0 and min(right) > 0
    return all(a*right[0] == b*left[0] for a, b in zip(left, right))


def exhaustive():
    rows = []
    for error in ERRORS:
        checked_graphs = states = branches = leaves = 0
        max_history = max_counter = max_weight_bits = 0
        worst_bad_mass = F(0)
        for n in range(2, 6):
            worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
            pairs = tuple(combinations(range(n), 2))
            pair_index = {pair: i for i, pair in enumerate(pairs)}
            gamma, repetitions, factor = boost(n, error)
            uniform_bad_bound = F(len(worlds), factor)
            assert uniform_bad_bound <= gamma/2
            for mask in range(1 << len(pairs)):
                edges = tuple(pair for j, pair in enumerate(pairs) if mask & (1 << j))
                cuts = tuple(sum(z[i] != z[j] for i, j in edges) for z in worlds)
                optimum = max(cuts)
                counts = tuple(-repetitions if pair in edges else 0 for pair in pairs)
                weights = tuple(factor**cut for cut in cuts)
                pending = [((), weights, counts)]
                while pending:
                    prefix, weights, counts = pending.pop()
                    states += 1
                    assert same_weights(weights, count_weights(worlds, pairs, counts))
                    good = tuple(cut == optimum and z[1:len(prefix)+1] == prefix
                                 for z, cut in zip(worlds, cuts))
                    assert any(good), (n, mask, error, prefix)
                    total = sum(weights)
                    bad_mass = F(sum(w for w, ok in zip(weights, good) if not ok), total)
                    assert bad_mass <= uniform_bad_bound < gamma
                    worst_bad_mass = max(worst_bad_mass, bad_mass)
                    history = repetitions*(len(edges)+len(prefix))
                    assert sum(map(abs, counts)) <= history
                    assert max(map(abs, counts)) <= 2*repetitions
                    max_history = max(max_history, history)
                    max_counter = max(max_counter, *map(abs, counts))
                    max_weight_bits = max(max_weight_bits, *(w.bit_length() for w in weights))
                    if len(prefix) == n-1:
                        assert sum(prefix[i-1] != prefix[j-1] if i else prefix[j-1]
                                   for i, j in edges) == optimum
                        leaves += 1
                        continue
                    query_index = len(prefix)+1
                    latent = F(sum(w for z, w in zip(worlds, weights) if z[query_index]), total)
                    probability = F(1, 10)+F(4, 5)*latent
                    for label in allowed_labels(probability, error):
                        chosen_mass = latent if label else 1-latent
                        assert chosen_mass >= gamma and chosen_mass > bad_mass
                        assert any(ok and z[query_index] == label for z, ok in zip(worlds, good))
                        updated = tuple(w*(factor if z[query_index] == label else 1)
                                        for z, w in zip(worlds, weights))
                        new_counts = list(counts)
                        new_counts[pair_index[0, query_index]] += repetitions*(1-2*label)
                        pending.append((prefix+(label,), updated, tuple(new_counts)))
                        branches += 1
                checked_graphs += 1
        rows.append({'forecast_error': str(error), 'all_graphs_n2_through_n5': checked_graphs,
                     'all_permitted_adaptive_states': states, 'permitted_decisions': branches,
                     'terminal_optimal_cuts': leaves, 'max_actual_history_length': max_history,
                     'max_absolute_signed_count': max_counter,
                     'max_integer_weight_bits': max_weight_bits,
                     'maximum_bad_posterior_mass': str(worst_bad_mass)})
    return rows


def native_checks():
    checked = queries = graphs = 0
    for n in (2, 3):
        rules, graph, worlds = relation_graph(n)
        pairs = tuple(combinations(range(n), 2))
        theta = (F(1),)+(F(1, len(worlds)),)*len(worlds)
        spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                          simplex_slots=tuple(range(1, len(worlds)+1)))
        for error in (F(1, 1000), F(399, 1000)):
            _, repetitions, _ = boost(n, error)
            for mask in range(1 << len(pairs)):
                edges = tuple(pair for j, pair in enumerate(pairs) if mask & (1 << j))
                state = initial_state(graph, rules, theta, 0, spec=spec, bit_limit=32768)
                weights = [1]*len(worlds)

                def event(i, j, label):
                    nonlocal state, checked
                    prediction = evaluate(graph, rules, state.theta, context(n, i, j), bit_limit=32768)
                    expected = F(1, 10)+F(4, 5)*F(sum(w for w, z in zip(weights, worlds)
                                                          if z[i]^z[j] == label), sum(weights))
                    assert prediction.probabilities[label] == expected
                    observed = observe_event(graph, state, spec, prediction, label, bit_limit=32768)
                    state = commit_event(observed, spec, bit_limit=32768)
                    weights[:] = [w*(9 if z[i]^z[j] == label else 1) for w, z in zip(weights, worlds)]
                    assert state.theta == (F(1),)+tuple(F(w, sum(weights)) for w in weights)
                    assert state.unit_count == 0 and not any(state.gradient_sum)
                    checked += 1

                for i, j in edges:
                    for _ in range(repetitions):
                        event(i, j, 1)
                assignment = [0]
                for i in range(1, n):
                    prediction = evaluate(graph, rules, state.theta, context(n, 0, i), bit_limit=32768)
                    # One maximally upward allowed error at each cut. The full
                    # exhaustive audit separately covers both possible choices.
                    label = int(min(F(1), prediction.probabilities[1]+error) >= F(1, 2))
                    assert label in allowed_labels(prediction.probabilities[1], error)
                    assignment.append(label)
                    queries += 1
                    for _ in range(repetitions):
                        event(0, i, label)
                assert sum(assignment[i] != assignment[j] for i, j in edges) == max(
                    sum(z[i] != z[j] for i, j in edges) for z in worlds)
                assert state.optimizer_steps == state.cursor == repetitions*(len(edges)+n-1)
                graphs += 1
    return {'graphs_and_error_settings': graphs, 'complete_native_units': checked,
            'native_decision_queries': queries, 'whole_state_weight_and_clock_checks': checked}


def audit():
    rows = exhaustive()
    native = native_checks()
    # At the excluded threshold a uniform decoder is valid for every history.
    # Its tie rule sets all anchor parities to 1 and misses this single-edge cut.
    assignment, edges = (0, 1, 1), ((1, 2),)
    assert sum(assignment[i] != assignment[j] for i, j in edges) == 0
    assert max(abs(F(1, 2)-p) for p in (F(1, 10), F(9, 10))) == F(2, 5)
    assert 'torch' not in sys.modules
    return {'status': 'PASS', 'arithmetic': 'exact integers and Fraction; native guards 32768 bits',
            'exhaustive': rows, 'native': native,
            'threshold_counterexample': {'n': 3, 'edges': [[1, 2]], 'uniform_forecast': '1/2',
                'uniform_error_bound': '2/5', 'returned_cut': 0, 'optimum': 1},
            'scope': 'worst-case uniform compact-model decoding; no Runtime, IID hardness, timing or fixed-job lower bound'}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
