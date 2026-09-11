"""Exact fixed-bank universality: partial colorings, positive margins, and checked primals."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from conditional_product_universality_audit import left_null, mobius, monomial_bank, rank, row_reduce
from decoder_exact_limit_audit import predictions
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_support_border_audit import add_product, add_sum, sources


SCOPE = 'known finite nonnegative frozen bank, constant available, positive k-label readouts, unrestricted finite SUM work and normalizer range'


def bank_table(table):
    rows = tuple(tuple(map(F, row)) for row in table)
    if not rows or any(len(row) != len(rows[0]) for row in rows) or any(value < 0 for row in rows for value in row):
        raise ValueError('a rectangular finite nonnegative bank is required')
    # The declared class includes a variable constant feature as well as base one.
    return tuple((F(1),)+row for row in rows)


def verify_coloring(table, k, colors):
    if type(k) is not int or k < 2 or len(colors) != len(table) or any(type(c) is not int or c < 0 or c > k for c in colors):
        return False
    if len(set(colors)-{0}) < 2:
        return False
    for column in zip(*bank_table(table)):
        active = {c for c, value in zip(colors, column) if c and value > 0}
        if len(active) == 1:
            return False
    return True


def partial_colorings(n, k):
    """Every color-permutation orbit once; zero means uncolored, not a deleted row."""
    def visit(prefix, maximum):
        if len(prefix) == n:
            if maximum >= 2:
                yield tuple(prefix)
            return
        for color in range(min(k, maximum+1)+1):
            yield from visit(prefix+[color], max(maximum, color))
    yield from visit([], 0)


def decide_universality(table, k, work_budget):
    """Standalone scoped theorem audit; never a Compiler/installation authorization."""
    bank_table(table)
    if type(k) is not int or k < 2 or type(work_budget) is not int or work_budget < 0:
        raise ValueError('at least two labels and a nonnegative work budget are required')
    checked = 0
    for colors in partial_colorings(len(table), k):
        if checked >= work_budget:
            return {'status': 'UNRESOLVED', 'scope': SCOPE, 'colorings_checked': checked}
        checked += 1
        if verify_coloring(table, k, colors):
            return {'status': 'NOT_UNIVERSAL', 'scope': SCOPE, 'colorings_checked': checked, 'colors': colors}
    return {'status': 'UNIVERSAL', 'scope': SCOPE, 'colorings_checked': checked}


def coloring_margin(table, k, colors):
    if not verify_coloring(table, k, colors):
        raise ValueError('the coloring is not a valid obstruction for this complete bank')
    ratios = []
    for column in zip(*bank_table(table)):
        for label in range(1, k+1):
            correct = sum(v for c, v in zip(colors, column) if c == label)
            wrong = sum(v for c, v in zip(colors, column) if c and c != label)
            if correct:
                assert wrong > 0
                ratios.append(correct/wrong)
    ratio = max(ratios)
    epsilon = 1/(2*(ratio+1))
    target = tuple(tuple((1-epsilon if label == c else epsilon/(k-1)) if c else F(1, k)
                         for label in range(1, k+1)) for c in colors)
    return ratio, epsilon, target


def exact_primal(table, target):
    """Float64 LP proposes an active set; only exact reconstructed primals are accepted."""
    import numpy as np
    from scipy.optimize import linprog
    g = bank_table(table)
    target = tuple(tuple(map(F, row)) for row in target)
    n, k, m = len(g), len(target[0]), len(g[0])
    assert len(target) == n and all(len(row) == k and min(row) > 0 and sum(row) == 1 for row in target)
    matrix, rhs = [], [F(-1)]*(n*k)
    for label in range(k):
        for context in range(n):
            row = [F(0)]*(k*m+n)
            row[label*m:(label+1)*m] = g[context]
            row[k*m+context] = -target[context][label]
            matrix.append(row)
    proposal = linprog([1.]*(k*m)+[0.]*n, A_eq=np.asarray(matrix, dtype=float),
                       b_eq=np.asarray(rhs, dtype=float), bounds=[(0, None)]*(k*m)+[(None, None)]*n,
                       method='highs')
    if not proposal.success or not np.isfinite(proposal.x).all():
        return {'status': 'UNRESOLVED'}
    active = [j for j in range(k*m) if proposal.x[j] > 1.e-9]+list(range(k*m, k*m+n))
    reduced, pivots = row_reduce([[row[j] for j in active]+[value] for row, value in zip(matrix, rhs)])
    if len(active) in pivots:
        return {'status': 'UNRESOLVED'}
    solution = [F(0)]*(k*m+n)
    for row, pivot in enumerate(pivots):
        solution[active[pivot]] = reduced[row][-1]
    if min(solution[:k*m]) < 0 or min(solution[k*m:]) <= 0:
        return {'status': 'UNRESOLVED'}
    assert all(sum(a*b for a, b in zip(row, solution)) == value for row, value in zip(matrix, rhs))
    weights = [solution[label*m:(label+1)*m] for label in range(k)]
    masses = [[1+sum(a*b for a, b in zip(g[context], weights[label])) for label in range(k)] for context in range(n)]
    assert all(tuple(v/sum(row) for v in row) == target[i] for i, row in enumerate(masses))
    return {'status': 'EXACT_PRIMAL', 'weights': weights, 'normalizers': solution[k*m:]}


def source_and_product_bank(d, nodes):
    values = evaluate_tables(nodes, binary_tables(d))
    features = list(range(2*d))+[i for i, node in enumerate(nodes) if node[0] == 'product']
    return tuple(tuple(values[feature][i] for feature in features) for i in range(2**d))


def shifted_bank(t):
    t = F(t)
    nodes = sources(2)
    one = add_sum(nodes, ((0, 1), (1, 1)))
    left = add_sum(nodes, ((one, t), (1, 1)))
    right = add_sum(nodes, ((one, t), (3, 1)))
    h = add_product(nodes, left, right)
    return nodes, h, source_and_product_bank(2, nodes)


def pair_bank():
    nodes = sources(2)
    a = add_product(nodes, add_sum(nodes, ((1, 1), (3, 1))), add_sum(nodes, ((0, 1), (2, 1))))
    b = add_product(nodes, add_sum(nodes, ((0, 1), (3, 1))), add_sum(nodes, ((1, 1), (2, 1))))
    assert a != b and sum(node[0] == 'product' for node in nodes) == 2
    return nodes, source_and_product_bank(2, nodes)


def check_margin_readout(table, k, colors, rng):
    g = bank_table(table)
    ratio, epsilon, target = coloring_margin(table, k, colors)
    # Independent exact Farkas certificate for this same adversarial target.
    large = 2*ratio+1
    dual = [[F(-1) if c == label else large if c else F(0) for label in range(1, k+1)] for c in colors]
    assert all(sum(row[j]*feature for row, feature in zip(dual, column)) >= 0
               for j in range(k) for column in zip(*g))
    assert all(sum(a*b for a, b in zip(row, probability)) == 0 for row, probability in zip(dual, target))
    assert sum(sum(row) for row in dual) > 0
    weights = [[F(rng.randrange(8), rng.choice((1, 2, 3)))*F(2)**rng.randrange(-60, 61)
                for _ in g[0]] for _ in range(k)]
    masses = [[1+sum(v*w for v, w in zip(row, weights[label])) for label in range(k)] for row in g]
    q = [tuple(v/sum(row) for v in row) for row in masses]
    for label in range(1, k+1):
        correct = sum(row[label-1] for color, row in zip(colors, masses) if color == label)
        wrong = sum(row[label-1] for color, row in zip(colors, masses) if color and color != label)
        assert correct <= ratio*wrong
    assert min(q[i][c-1] for i, c in enumerate(colors) if c) <= ratio/(ratio+1)
    assert max(abs(a-b) for row, goal in zip(q, target) for a, b in zip(row, goal)) >= epsilon


def finite_validation_audit(rng):
    targets = [tuple((F(1)-p, p) for p in values) for values in product((F(1, 4), F(3, 4)), repeat=4)]
    targets.extend(tuple((1-p, p) for p in [F(rng.randrange(1, 20), 20) for _ in range(4)]) for _ in range(24))
    records, limit = [], F(1)
    for target in targets:
        gamma = max(max(column)/min(column) for column in zip(*target))
        c, growth = 2*max(1/v for v in target[0]), 4*(1+gamma)
        masses = tuple(tuple(c*growth**i.bit_count()*p for p in row) for i, row in enumerate(target))
        coefficients = [mobius([row[j]-1 for row in masses]) for j in range(2)]
        for b0, by, bx, bxy in coefficients:
            assert min(b0, by, bx, bxy) > 0
            limit = min(limit, b0/(2*bxy), by/(2*bxy), bx/(2*bxy))
        records.append((target, masses, coefficients))
    t = F(1)
    while t > limit:
        t /= 2
    graph_cases = 0
    for target, masses, coefficients in records:
        nodes, h, table = shifted_bank(t)
        one = add_sum(nodes, ((0, 1), (1, 1)))
        heads = []
        for b0, by, bx, bxy in coefficients:
            adjusted = (b0-t*t*bxy, by-t*bxy, bx-t*bxy, bxy)
            assert min(adjusted) > 0
            heads.append(add_sum(nodes, zip((one, 3, 1, h), adjusted)))
        values = evaluate_tables(nodes, binary_tables(2))
        for i in range(4):
            excess = [values[head][i] for head in heads]
            assert tuple(1+v for v in excess) == masses[i]
            assert predictions(excess)[0] == target[i]
        assert sum(node[0] == 'product' for node in nodes) == 1
        graph_cases += 1
    decision = decide_universality(table, 2, 100)
    assert decision['status'] == 'NOT_UNIVERSAL'
    ratio, epsilon, _ = coloring_margin(table, 2, decision['colors'])
    return {'finite_target_graphs_realized_exactly': graph_cases, 'shared_positive_shift': str(t),
            'PRODUCTs': 1, 'still_not_binary_universal': True,
            'new_adversarial_target_probability_gap': str(epsilon), 'coloring_ratio_K': str(ratio)}


def audit():
    rng = random.Random(2026091112)
    support_cases, rejected_cases, primal_cases, margin_cases = 0, 0, 0, 0
    # All three-row support banks, plus four-row banks with arbitrary positive values.
    models = []
    for subset in range(2**6):
        masks = [mask for mask in range(1, 7) if subset & (1 << (mask-1))]
        table = [[F(int(mask & (1 << i) != 0)) for mask in masks] for i in range(3)]
        models.extend((table, k) for k in (2, 3))
    for _ in range(40):
        masks = rng.sample(range(1, 16), rng.randrange(1, 10))
        table = [[F(rng.randrange(1, 6), rng.randrange(1, 6)) if mask & (1 << i) else F(0) for mask in masks] for i in range(4)]
        models.extend((table, k) for k in (2, 3, 4))
    for table, k in models:
        result = decide_universality(table, k, 100000)
        raw = next((colors for colors in product(range(k+1), repeat=len(table)) if verify_coloring(table, k, colors)), None)
        assert (result['status'] == 'NOT_UNIVERSAL') == (raw is not None)
        support_cases += 1
        if raw is not None:
            assert verify_coloring(table, k, result['colors'])
            check_margin_readout(table, k, result['colors'], rng)
            margin_cases += 1
            rejected_cases += 1
        elif primal_cases < 45:
            rows = [[rng.randrange(1, 8) for _ in range(k)] for _ in table]
            target = [tuple(F(v, sum(row)) for v in row) for row in rows]
            assert exact_primal(table, target)['status'] == 'EXACT_PRIMAL'
            primal_cases += 1

    original_cases = 80
    for _ in range(original_cases):
        d = rng.randrange(2, 6)
        p = rng.randrange(min(5, 2**d-d-2)+1)
        nodes = sources(d)
        random_graph(rng, nodes, p)
        table = bank_table(source_and_product_bank(d, nodes))
        w = left_null(table)
        assert sum(w) == 0 and any(v > 0 for v in w) and any(v < 0 for v in w)
        assert all(sum(a*b for a, b in zip(w, column)) == 0 for column in zip(*table))
        colors = tuple(2 if v > 0 else 1 if v < 0 else 0 for v in w)
        assert verify_coloring(table, 2, colors)
        weights = [[F(rng.randrange(10), 3)*F(2)**rng.randrange(-400, 401) for _ in table[0]] for _ in range(2)]
        masses = [[1+sum(v*a for v, a in zip(row, weights[j])) for j in range(2)] for row in table]
        assert all(sum(w[i]*row[j] for i, row in enumerate(masses)) == 0 for j in range(2))
        q = [row[1]/sum(row) for row in masses]
        positive, negative = [i for i, v in enumerate(w) if v > 0], [i for i, v in enumerate(w) if v < 0]
        a, b = min(positive, key=lambda i: q[i]), max(negative, key=lambda i: q[i])
        assert q[a] <= q[b]
        assert (q[a]-F(3, 4))**2+(q[b]-F(1, 4))**2 >= F(1, 8)
        target = [F(3, 4) if v > 0 else F(1, 4) for v in w]
        assert max(abs(a-b) for a, b in zip(q, target)) >= F(1, 4)

    zero_nodes, zero_feature, unshifted = shifted_bank(F(0))
    _, _, shifted = shifted_bank(F(1))
    assert rank(bank_table(unshifted)) == rank(bank_table(shifted)) == 4
    assert decide_universality(unshifted, 2, 100)['status'] == 'UNIVERSAL'
    assert decide_universality(unshifted, 5, 100)['status'] == 'UNIVERSAL'
    decision = decide_universality(shifted, 2, 100)
    assert decision['status'] == 'NOT_UNIVERSAL'
    k_ratio, _, _ = coloring_margin(shifted, 2, (1, 2, 2, 1))
    assert k_ratio == F(5, 4) and F(3, 4)-k_ratio/(k_ratio+1) == F(7, 36)
    assert not verify_coloring(unshifted, 2, (1, 2, 2, 1))
    assert not verify_coloring(shifted, 2, (1, 1, 1, 1))
    assert not verify_coloring(shifted, 2, (1, 2, 3, 1))
    assert not verify_coloring(shifted, 2, (1, 2, 2))
    assert decide_universality(unshifted, 2, 0)['status'] == 'UNRESOLVED'
    assert decide_universality(unshifted, 2, 1)['status'] == 'UNRESOLVED'
    invalid_budgets = 0
    for bad_budget in (-1, float('nan'), float('inf'), F(1, 2)):
        try:
            decide_universality(unshifted, 2, bad_budget)
        except ValueError:
            invalid_budgets += 1
        else:
            raise AssertionError('invalid coloring budget accepted')

    _, pairs = pair_bank()
    pair_status = {k: decide_universality(pairs, k, 100)['status'] for k in (2, 3, 4, 5)}
    assert pair_status == {2: 'UNIVERSAL', 3: 'UNIVERSAL', 4: 'NOT_UNIVERSAL', 5: 'NOT_UNIVERSAL'}
    ratio, epsilon, pair_target = coloring_margin(pairs, 4, (1, 2, 3, 4))
    assert ratio == 1 and epsilon == F(1, 4)
    pair_upper = exact_primal(unshifted, pair_target)
    assert pair_upper['status'] == 'EXACT_PRIMAL'
    # Attach these mathematical readout weights to the actual native audit DAG.
    # This is a standalone evaluator, not a registered Runtime installation.
    one = add_sum(zero_nodes, ((0, 1), (1, 1)))
    features = (one, 0, 1, 2, 3, zero_feature)
    upper_heads = [add_sum(zero_nodes, zip(features, weights)) for weights in pair_upper['weights']]
    upper_values = evaluate_tables(zero_nodes, binary_tables(2))
    assert sum(node[0] == 'product' for node in zero_nodes) == 1
    for context in range(4):
        q, total = predictions([upper_values[head][context] for head in upper_heads])
        assert q == pair_target[context] and total == pair_upper['normalizers'][context]
    for k in (2, 3):
        for _ in range(10):
            rows = [[rng.randrange(1, 20) for _ in range(k)] for _ in range(4)]
            target = [tuple(F(v, sum(row)) for v in row) for row in rows]
            assert exact_primal(pairs, target)['status'] == 'EXACT_PRIMAL'
            primal_cases += 1
    primal_cases += 1

    partial_example = ((F(1),), (F(0),), (F(0),))
    assert all(not verify_coloring(partial_example, 2, colors) for colors in product((1, 2), repeat=3))
    assert verify_coloring(partial_example, 2, (0, 1, 2))
    assert decide_universality(partial_example, 2, 100)['status'] == 'NOT_UNIVERSAL'

    native_complete_checks = []
    for d, k in ((1, 2), (2, 3), (3, 2), (3, 3)):
        nodes, _ = monomial_bank(d)
        table = source_and_product_bank(d, nodes)
        result = decide_universality(table, k, 100000)
        assert result['status'] == 'UNIVERSAL'
        assert rank(bank_table(table)) == 2**d
        native_complete_checks.append({'d': d, 'labels': k, 'PRODUCTs': 2**d-d-1,
                                       'colorings_checked': result['colorings_checked']})
    validation = finite_validation_audit(rng)
    return {'status': 'PASS', 'scope': SCOPE,
            'support_criterion': 'no obstructing partial coloring iff exact and approximate universality',
            'exact_frozen_bank_universal_PRODUCT_minimum': '2^d-d-1 for every fixed k>=2',
            'independently_cross_checked_support_models': support_cases,
            'models_with_checked_obstructions': rejected_cases, 'quantitative_mass_readout_checks': margin_cases,
            'exact_target_Farkas_duals': margin_cases,
            'checked_exact_LP_primals': primal_cases, 'original_DAG_annihilator_checks': original_cases,
            'annihilator_binary_probability_gap': '1/4', 'annihilator_uniform_CE_gap': '1/(4N)',
            'full_span_shift_counterexample': {'unshifted_PRODUCTs': 1, 'shifted_PRODUCTs': 1, 'both_ranks': 4,
                                              'positive_shift': '1', 'shifted_K': '5/4',
                                              'XOR_noise_one_quarter_probability_gap': '7/36', 'CE_gap': '49/2592'},
            'two_PRODUCT_pair_bank_status_by_labels': pair_status,
            'four_label_pair_bank_probability_gap': '1/4', 'four_label_pair_bank_CE_gap': '1/32',
            'one_PRODUCT_exact_four_label_counterpart_cap': str(max(pair_upper['normalizers'])),
            'partial_domain_counterexample_checked': True, 'forged_colorings_rejected': 4,
            'insufficient_budget_UNRESOLVED_checks': 2, 'native_universal_banks': native_complete_checks,
            'invalid_or_nonfinite_coloring_budgets_rejected': invalid_budgets,
            'finite_validation_counterexample': validation,
            'not_claimed': ['a common hard binary target for all variable-feature graphs',
                            'full numerical span suffices for a particular positive bank',
                            'finite target testing is a universal certificate',
                            'target acquisition, registered value/install/persistence or AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_FROZEN_FEATURE_UNIVERSALITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
