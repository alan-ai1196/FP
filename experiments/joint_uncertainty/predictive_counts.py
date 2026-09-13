"""Exact whole-history predictive state and future-sensitive memory audit.

Known fair latent bits and noise1/10; model-state statements only. Nothing in
this module constructs a Runtime candidate or authorizes deleting raw records.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from audit_cuda_primitives import SINGLE


def edges(n):
    return tuple(combinations(range(n), 2))


def statistics(n, history):
    indices = {pair: k for k, pair in enumerate(edges(n))}
    counts = [0]*len(indices)
    diagonal_balance = 0
    for i, j, y in history:
        sign = 1 if y == 0 else -1
        if i == j:
            diagonal_balance += sign
        else:
            counts[indices[tuple(sorted((i, j)))]] += sign
    return tuple(counts), len(history), diagonal_balance


def weights_from_counts(n, counts, epsilon=F(1, 10)):
    assert len(counts) == len(edges(n)) and 0 < epsilon < 1
    odds = (1-epsilon)/epsilon
    return tuple(odds ** sum(d for (i, j), d in zip(edges(n), counts) if z[i] == z[j])
                 for z in product((0, 1), repeat=n))


def weights_from_history(n, history, epsilon=F(1, 10)):
    result = []
    for z in product((0, 1), repeat=n):
        value = F(1)
        for i, j, y in history:
            value *= 1-epsilon if (z[i] ^ z[j]) == y else epsilon
        result.append(value)
    return tuple(result)


def normalize(weights):
    total = sum(weights)
    return tuple(value/total for value in weights)


def forecasts(n, weights, epsilon=F(1, 10)):
    worlds = tuple(product((0, 1), repeat=n))
    total = sum(weights)
    return tuple(epsilon+(1-2*epsilon)*sum(w for z, w in zip(worlds, weights) if z[i] == z[j])/total
                 for i, j in edges(n))


def mixed_forecast(n, history, query):
    total = numerator = F(0)
    for epsilon in (F(1, 10), F(1, 4)):
        for z, w in zip(product((0, 1), repeat=n), weights_from_history(n, history, epsilon)):
            total += w
            numerator += w*(1-epsilon if z[query[0]] == z[query[1]] else epsilon)
    return numerator/total  # equal model and uniform latent priors cancel


def lattice_ball(dimension, budget):
    if dimension == 0:
        yield ()
    else:
        for value in range(-budget, budget+1):
            for tail in lattice_ball(dimension-1, budget-abs(value)):
                yield (value,)+tail


def class_count(dimension, horizon):
    return sum(2**j*comb(dimension, j)*comb(horizon, j)
               for j in range(min(dimension, horizon)+1))


def history_audit():
    history_checks = joint_checks = transitions = 0
    n = 3
    alphabet = tuple(product(range(n), range(n), (0, 1)))
    for length in range(4):
        for history in product(alphabet, repeat=length):
            d, t, diagonal = statistics(n, history)
            # This common scalar is invisible to a fixed-noise normalized
            # posterior, but cannot be discarded from a noise comparison.
            exponent2 = t-sum(d)+diagonal
            assert exponent2 % 2 == 0 and exponent2 >= 0
            for epsilon in (F(1, 10), F(1, 4)):
                raw = weights_from_history(n, history, epsilon)
                reduced = weights_from_counts(n, d, epsilon)
                assert normalize(raw) == normalize(reduced)
                common = epsilon**t*((1-epsilon)/epsilon)**(exponent2//2)
                assert raw == tuple(common*w for w in reduced)
                joint_checks += 1
            if history:
                before = statistics(n, history[:-1])[0]
                i, j, y = history[-1]
                expected = list(before)
                if i != j:
                    expected[edges(n).index(tuple(sorted((i, j))))] += 1 if y == 0 else -1
                assert d == tuple(expected)
                transitions += 1
            history_checks += 1
    return {'histories': history_checks, 'known_and_unknown_noise_weight_checks': joint_checks,
            'append_statistic_transitions': transitions}


def minimality_audit():
    cases = []
    pair_tables = 0
    for n, horizon in ((2, 8), (3, 5), (4, 3), (5, 2)):
        dimension = len(edges(n))
        points = tuple(lattice_ball(dimension, horizon))
        assert len(set(points)) == len(points) == class_count(dimension, horizon)
        observed = {}
        for d in points:
            # Canonical exact-horizon representative: |d| signed edge labels,
            # then diagonal labels to fill the remaining fixed clock.
            history = tuple((i, j, 0 if value > 0 else 1)
                            for (i, j), value in zip(edges(n), d) for _ in range(abs(value)))
            history += ((0, 0, 0),)*(horizon-len(history))
            assert statistics(n, history)[0] == d and len(history) == horizon
            w = weights_from_counts(n, d)
            assert normalize(w) == normalize(weights_from_history(n, history))
            table = forecasts(n, w)
            assert table not in observed, (d, observed.get(table))
            observed[table] = d
            pair_tables += 1
        cases.append({'n': n, 'cut': horizon, 'signed_coordinates': dimension,
                      'distinct_exact_forecast_classes': len(observed),
                      'minimum_binary_state_bits': (len(observed)-1).bit_length()})
    # Character orthogonality directly checks the minimal-family premise;
    # positive reweighting preserves absence of a constant linear combination.
    gram_entries = 0
    for n in range(2, 7):
        characters = tuple(tuple(1 if z[i] == z[j] else -1 for i, j in edges(n))
                           for z in product((0, 1), repeat=n))
        for a, b in product(range(len(edges(n))), repeat=2):
            assert sum(row[a]*row[b] for row in characters) == (2**n if a == b else 0)
            gram_entries += 1
        assert all(sum(row[a] for row in characters) == 0 for a in range(len(edges(n))))
    return {'exact_distinct_pair_forecast_tables': pair_tables, 'cases': cases,
            'character_Gram_entries': gram_entries}


def future_audit():
    n, bound = 4, 3
    tree = ((0, 1), (1, 2), (2, 3))
    states = tuple(product(range(bound+1), repeat=len(tree)))
    tables = {}
    for state in states:
        d = tuple(state[tree.index(e)] if e in tree else 0 for e in edges(n))
        tables[state] = forecasts(n, weights_from_counts(n, d))
    minimum = F(1)
    pairs = 0
    for left, right in combinations(states, 2):
        coordinate = next(i for i, (a, b) in enumerate(zip(left, right)) if a != b)
        cancel = min(left[coordinate], right[coordinate])
        successors = []
        for state in (left, right):
            successor = list(state)
            successor[coordinate] -= cancel
            successors.append(tables[tuple(successor)][edges(n).index(tree[coordinate])])
        gap = abs(successors[0]-successors[1])
        assert gap >= F(8, 25)
        minimum = min(minimum, gap)
        pairs += 1
    assert minimum == F(8, 25)
    # Ideal binary32 forecast equality is not an AMP Runtime execution claim.
    initial = tuple(forecasts(2, weights_from_counts(2, (d,)))[0] for d in (8, 9))
    words = tuple(SINGLE.rounded(value) for value in initial)
    assert words[0] == words[1]
    future = tuple(forecasts(2, weights_from_counts(2, (d-8,)))[0] for d in (8, 9))
    assert future == (F(1, 2), F(41, 50))
    assert abs(initial[0]-initial[1]) < F(1, 10**7)
    return {'fixed_cut': len(tree)*bound, 'packed_tree_count_states': len(states),
            'separated_state_pairs': pairs, 'minimum_future_probability_gap': str(minimum),
            'maximum_witness_future_labels': bound,
            'binary32_current_collision': {'counts': [8, 9], 'word': words[0],
                'exact_current_gap': str(abs(initial[0]-initial[1])), 'same_future': 'eight label1 observations on (0,1)',
                'exact_future_forecasts': list(map(str, future)), 'scope': 'rounded ideal probabilities, not native GPU phases'}}


def separating_future(n, left, right, horizon, leakage=F(1, 100)):
    """A common legal suffix exposes any unequal signed-count vectors.

    This is a distinguishability witness, not a chosen-data acquisition
    policy: its labels are possible, potentially very rare observations.
    """
    pairs = edges(n)
    assert left != right and max(sum(map(abs, left)), sum(map(abs, right))) <= horizon
    delta = {e: b-a for e, a, b in zip(pairs, left, right)}
    vertex, anchor = next(e for e in pairs if delta[e])
    orientation = 1 if delta[vertex, anchor] > 0 else -1
    signs = {}
    for j in range(n):
        if j != vertex:
            value = delta[tuple(sorted((vertex, j)))]
            signs[j] = orientation*(1 if value >= 0 else -1)
    assert signs[anchor] == 1
    field = sum(left[pairs.index(tuple(sorted((vertex, j))))]*signs[j] for j in signs)
    contrast = sum(delta[tuple(sorted((vertex, j)))]*signs[j] for j in signs)
    assert abs(contrast) == sum(abs(delta[tuple(sorted((vertex, j)))]) for j in signs) >= 1
    history = [(vertex, anchor, 0 if field < 0 else 1)]*abs(field)
    extra = 0
    while F(2**(n-2), 9**extra) > leakage:
        extra += 1
    strength = 2*horizon+extra
    for j, sign in signs.items():
        if j != anchor:
            history.extend([(anchor, j, 0 if sign > 0 else 1)]*strength)
    return tuple(history), (vertex, anchor), signs, contrast, strength


def full_future_packing_audit():
    cases = []
    minimum_gap = F(1)
    maximum_bad = F(0)
    checks = 0
    for n, horizon in ((2, 8), (3, 2), (4, 2), (5, 1)):
        points = tuple(lattice_ball(len(edges(n)), horizon))
        worlds = tuple(product((0, 1), repeat=n))
        maximum_suffix = pairs_checked = 0
        for left, right in combinations(points, 2):
            history, query, signs, contrast, strength = separating_future(n, left, right, horizon)
            change = statistics(n, history)[0]
            future_likelihood = weights_from_history(n, history)
            predictions = []
            for state, ideal_count in ((left, 0), (right, contrast)):
                weights = weights_from_counts(n, tuple(a+b for a, b in zip(state, change)))
                assert normalize(weights) == normalize(tuple(w*l for w, l in
                    zip(weights_from_counts(n, state), future_likelihood)))
                total = sum(weights)
                good = tuple(all((1 if z[j] == z[query[1]] else -1) == sign
                                 for j, sign in signs.items()) for z in worlds)
                assert sum(good) == 4
                good_total = sum(w for w, keep in zip(weights, good) if keep)
                bad = (total-good_total)/total
                assert bad <= F(1, 100)
                ratio_bound = F(2**n-4, 4)*F(9)**(2*horizon-strength)
                assert (total-good_total)/good_total <= ratio_bound
                conditional = F(1, 10)+F(4, 5)*sum(w for z, w, keep in zip(worlds, weights, good)
                                                  if keep and z[query[0]] == z[query[1]])/good_total
                ideal = forecasts(2, weights_from_counts(2, (ideal_count,)))[0]
                assert conditional == ideal
                prediction = forecasts(n, weights)[edges(n).index(tuple(sorted(query)))]
                assert abs(prediction-conditional) <= F(4, 5)*bad
                predictions.append(prediction)
                maximum_bad = max(maximum_bad, bad)
            gap = abs(predictions[0]-predictions[1])
            assert gap >= F(8, 25)-2*F(4, 5)*F(1, 100) == F(38, 125)
            minimum_gap = min(minimum_gap, gap)
            maximum_suffix = max(maximum_suffix, len(history))
            pairs_checked += 1
        checks += pairs_checked
        cases.append({'n': n, 'cut': horizon, 'classes': len(points),
                      'all_pairs_separated': pairs_checked, 'maximum_common_suffix_labels': maximum_suffix})
    return {'cases': cases, 'state_pairs_checked': checks,
            'minimum_exact_forecast_gap': str(minimum_gap),
            'minimum_exact_forecast_gap_binary64': float(minimum_gap),
            'maximum_off_constraint_posterior_mass': str(maximum_bad),
            'certified_gap_lower': '38/125', 'declared_leakage_upper': '1/100',
            'scope': 'all count classes, common positive-probability suffix; uniform future error, not expected risk'}


def boundaries():
    first = ((0, 1, 0), (0, 1, 1))
    second = ((0, 0, 0), (0, 0, 0))
    assert statistics(2, first) == ((0,), 2, 0)
    assert statistics(2, second) == ((0,), 2, 2)
    assert mixed_forecast(2, first, (0, 1)) == mixed_forecast(2, second, (0, 1)) == F(1, 2)
    future = tuple(mixed_forecast(2, history+((0, 1, 0),), (0, 1)) for history in (first, second))
    assert future == (F(5093, 7400), F(9029, 12200))
    # At noise1/2, distinct signed statistics have identical laws: strict
    # nonzero interaction/noise contrast is an indispensable assumption.
    assert forecasts(3, weights_from_counts(3, (1, 2, -1), F(1, 2)), F(1, 2)) == (F(1, 2),)*3
    return {'unknown_noise_same_d_and_clock': [statistics(2, first), statistics(2, second)],
            'unknown_noise_same_next_label_forecasts': list(map(str, future)),
            'noise_half_identifiability_failure': True,
            'scope': 'known-noise posterior quotient only; no deletion of Compiler history, gradients, profiles or evidence'}


if __name__ == '__main__':
    report = {'history': history_audit(), 'minimality': minimality_audit(),
              'future_packing': future_audit(), 'full_future_packing': full_future_packing_audit(),
              'boundaries': boundaries()}
    assert 'torch' not in sys.modules
    print(json.dumps(report, indent=2))
