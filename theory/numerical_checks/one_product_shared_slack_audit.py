"""Exact one-PRODUCT mass classification, shared-slack counterexamples and rank witnesses."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

CELLS = tuple(product((0, 1), repeat=2))


def classify(mass):
    assert len(mass) == 4 and len(mass[0]) >= 1
    k = len(mass[0])
    assert all(len(row) == k and min(row) >= 1 for row in mass)
    excess = tuple(tuple(F(v)-1 for v in row) for row in mass)
    delta = tuple(excess[0][y]+excess[3][y]-excess[1][y]-excess[2][y] for y in range(k))
    signs = {1 if d > 0 else -1 for d in delta if d}
    if len(signs) > 1:
        return {'status': 'MORE_THAN_ONE_REQUIRED', 'reason': 'opposite_mixed_signs'}
    if not signs:
        return {'status': 'ZERO_PRODUCT', 'excess': excess, 'coefficients': (F(0),)*k,
                'product_table': (F(0),)*4}
    sigma = signs.pop()
    corners = (0, 3) if sigma == 1 else (1, 2)
    bounds = tuple(min(excess[i][y]/(sigma*d) for y, d in enumerate(delta) if d) for i in corners)
    if sum(bounds) < 1:
        return {'status': 'MORE_THAN_ONE_REQUIRED', 'reason': 'insufficient_shared_slack',
                'common_corner_bounds': bounds}
    parameter = max(F(0), 1-bounds[1])
    assert parameter <= min(F(1), bounds[0])
    h = tuple((parameter*(1-x)+(1-parameter)*(z if sigma == 1 else 1-z))
              *(x+(1-z if sigma == 1 else z)) for x, z in CELLS)
    assert h[corners[0]] == parameter and h[corners[1]] == 1-parameter
    coefficients = tuple(sigma*d for d in delta)
    remainder = tuple(tuple(excess[i][y]-coefficients[y]*h[i] for y in range(k)) for i in range(4))
    return {'status': 'ONE_PRODUCT', 'excess': remainder, 'coefficients': coefficients,
            'product_table': h, 'parent_parameter': parameter, 'orientation': sigma}


def verify_construction(mass, result):
    assert result['status'] in ('ZERO_PRODUCT', 'ONE_PRODUCT')
    excess, h, coefficients = result['excess'], result['product_table'], result['coefficients']
    assert all(min(row) >= 0 for row in excess) and min(h) >= 0 and min(coefficients) >= 0
    for y in range(len(mass[0])):
        row_weights = (min(excess[0][y], excess[1][y]), min(excess[2][y], excess[3][y]))
        column_weights = (excess[0][y]-row_weights[0], excess[1][y]-row_weights[0])
        for i, (x, z) in enumerate(CELLS):
            assert row_weights[x]+column_weights[z] == excess[i][y]
            assert 1+row_weights[x]+column_weights[z]+coefficients[y]*h[i] == mass[i][y]


def indicator_program(d):
    """A real scalar SUM/PRODUCT-compatible DAG, not a supplied joint source table."""
    nodes = [('source', i, bit) for i in range(d) for bit in (0, 1)]
    def build(axes):
        if len(axes) == 1:
            return {(bit,): 2*axes[0]+bit for bit in (0, 1)}
        split = len(axes)//2
        left, right = build(axes[:split]), build(axes[split:])
        result = {}
        for a, i in left.items():
            for b, j in right.items():
                result[a+b] = len(nodes)
                nodes.append(('product', i, j))
        return result
    outputs = build(tuple(range(d)))
    for x in product((0, 1), repeat=d):
        values = []
        for kind, a, b in nodes:
            values.append(int(x[a] == b) if kind == 'source' else values[a]*values[b])
        assert sum(values[i] for i in outputs.values()) == 1
        for assignment, i in outputs.items():
            assert values[i] == int(assignment == x)
    return len(nodes)-2*d


def audit():
    counts = {'ZERO_PRODUCT': 0, 'ONE_PRODUCT': 0, 'opposite_mixed_signs': 0, 'insufficient_shared_slack': 0}
    for entries in product(range(3), repeat=8):
        mass = tuple((F(1+entries[i]), F(1+entries[4+i])) for i in range(4))
        result = classify(mass)
        key = result.get('reason', result['status'])
        counts[key] += 1
        if result['status'] != 'MORE_THAN_ONE_REQUIRED':
            verify_construction(mass, result)
    assert counts == {'ZERO_PRODUCT': 361, 'ONE_PRODUCT': 3922,
                      'opposite_mixed_signs': 1922, 'insufficient_shared_slack': 356}

    rng = random.Random(20260908)
    generated = 0
    for k in range(1, 7):
        for _ in range(200):
            parents = [tuple(F(rng.randrange(5), 3) for _ in range(4)) for _ in range(2)]
            h = tuple((parents[0][x]+parents[0][2+z])*(parents[1][x]+parents[1][2+z]) for x, z in CELLS)
            readouts = [tuple(F(rng.randrange(5), 3) for _ in range(5)) for _ in range(k)]
            mass = tuple(tuple(1+w[x]+w[2+z]+w[4]*h[i] for w in readouts) for i, (x, z) in enumerate(CELLS))
            result = classify(mass)
            assert result['status'] != 'MORE_THAN_ONE_REQUIRED'
            verify_construction(mass, result)
            generated += 1

    disjoint = ((F(2), F(1)), (F(1), F(1)), (F(1), F(1)), (F(1), F(2)))
    assert classify(disjoint)['reason'] == 'insufficient_shared_slack'
    for i, (x, z) in enumerate(CELLS):
        alternative = (2-F(x+z, 2), 1+F(x+z, 2))
        assert alternative[1]/sum(alternative) == disjoint[i][1]/sum(disjoint[i])

    target = tuple(tuple(F(1+int(i == y), 5) for y in range(4)) for i in range(4))
    one_scales = (F(5), F(15, 2), F(15, 2), F(35, 2))
    one_mass = tuple(tuple(t*p for p in row) for t, row in zip(one_scales, target))
    one_result = classify(one_mass)
    assert one_result['status'] == 'ONE_PRODUCT' and one_result['parent_parameter'] == 0
    verify_construction(one_mass, one_result)
    relaxed_scales = (F(15, 2), F(5), F(5), F(15, 2))
    relaxed = tuple(tuple(t*p for p in row) for t, row in zip(relaxed_scales, target))
    assert classify(relaxed)['reason'] == 'insufficient_shared_slack'
    assert classify(relaxed)['common_corner_bounds'] == (F(1, 5), F(1, 5))

    def quadratic(u, v):
        return 8*u*u-11*u*v+8*v*v-75*u-75*v
    for cap in (F(5), F(15, 2), F(10), F(17), F(1749, 100), F(35, 2)):
        assert quadratic(5, cap) == (2*cap-35)*(4*cap+5)
        maximum = max(quadratic(u, v) for u, v in product((F(5), cap), repeat=2))
        assert (maximum < 0) == (cap < F(35, 2))
    assert F(8)*8-F(11, 2)**2 > 0  # Positive definite quadratic part.

    # Independent matrix/table calculations for the many-output rank obstruction.
    rank_rows = []
    for d in range(2, 9):
        vertices = tuple(product((0, 1), repeat=d))
        n = len(vertices)
        for j, own in enumerate(vertices):
            for axis in range(d):
                for bit in (0, 1):
                    diagonal = int(own[axis] == bit)
                    off = sum(int(x[axis] == bit) for i, x in enumerate(vertices) if i != j)
                    assert diagonal <= off
        delta = F(1, (n+1)*(n+2))
        t = (n+1)*delta
        surplus_numerator = 1-(n+1)*t-(n-1)*t*t
        assert surplus_numerator == F(3, (n+2)**2) > 0
        count = indicator_program(d)
        assert count >= n and (d != 2 or count == 4)
        rank_rows.append({'bits': d, 'contexts_and_labels': n, 'proved_product_lower': n,
                          'constructed_product_upper': count, 'minimal_readout_range': n+1,
                          'proved_supnorm_separation_for_fewer_products': str(delta),
                          'proved_uniform_ce_gap': str(2*delta*delta/n)})
    delta = F(1, 28)
    assert 1-25*delta-75*delta*delta == F(9, 784) > 0
    assert 2*delta*delta/4 == F(1, 1568)
    return {'status': 'PASS', 'scope': 'fixed scalar unary-source mass tables; positive base and shared scalar PRODUCT nodes',
            'complete_small_mass_grid': {'tables': 6561, 'classification': counts},
            'independently_generated_product_of_sum_models': generated,
            'generated_output_alphabet_sizes': list(range(1, 7)),
            'minimal_disjoint_slack_counterexample_exact': True,
            'four_label_task': {'unrestricted_minimum_range': '5', 'sign_relaxation_minimum_range': '15/2',
                                'actual_one_product_minimum_range': '35/2',
                                'one_product_witness_normalizers': [str(v) for v in one_scales],
                                'minimum_product_count_at_range_5': 4,
                                'all_at_most_three_product_ce_gap_lower_at_range_5': '1/1568'},
            'general_rank_obstruction_and_native_constructions': rank_rows,
            'not_claimed': ['mass normal form preserves learner/physical state', 'sign invariant suffices for one PRODUCT',
                            'sharp two/three-PRODUCT intermediate range thresholds',
                            'sharp general product count for more than two inputs',
                            'dimension-independent language-model margin', 'registered value/install or AMP certification']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_ONE_PRODUCT_SHARED_SLACK_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
