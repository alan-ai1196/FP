"""Exact construction audit for ONE_PRODUCT_CONDITIONAL_TABLE.md."""
from fractions import Fraction as F
from itertools import product
import argparse
import json
from pathlib import Path
import random

from normalized_sum_xor_audit import finite_sum_representation, closed_intersection


def construct(table):
    assert len(table) == 4
    k = len(table[0])
    assert k >= 2 and all(len(row) == k and min(row) > 0 and sum(row) == 1 for row in table)
    p00, p01, p10, p11 = table
    c00 = max(1/p for p in p00)
    a = tuple(c00*p for p in p00)
    c01 = max(v/p for v, p in zip(a, p01))
    c10 = max(v/p for v, p in zip(a, p10))
    b, c = tuple(c01*p for p in p01), tuple(c10*p for p in p10)
    d = tuple(bv+cv-av for av, bv, cv in zip(a, b, c))
    c11 = max(v/p for v, p in zip(d, p11))
    e = tuple(c11*p-v for p, v in zip(p11, d))
    return a, tuple(cv-av for cv, av in zip(c, a)), tuple(bv-av for bv, av in zip(b, a)), e


def verify(table):
    a, u, v, e = construct(table)
    assert min(a) >= 1 and all(min(row) >= 0 for row in (u, v, e))
    assert 0 in e
    for index, (x, z) in enumerate(product((0, 1), repeat=2)):
        masses = tuple(av+uv*x+vv*z+ev*x*z for av, uv, vv, ev in zip(a, u, v, e))
        assert min(masses) >= 1
        assert tuple(m/sum(masses) for m in masses) == table[index]
    return sum(value != 0 for value in e)


def audit():
    counts = {'zero_products_exact': 0, 'one_product_exact_but_zero_in_closure': 0,
              'one_product_with_disjoint_binary_intervals': 0}
    for p in product((F(1, 5), F(2, 5), F(3, 5), F(4, 5)), repeat=4):
        table = tuple((1-v, v) for v in p)
        used_edges = verify(table)
        if finite_sum_representation(p) is not None:
            counts['zero_products_exact'] += 1
        else:
            assert used_edges == 1
            if closed_intersection(p):
                counts['one_product_exact_but_zero_in_closure'] += 1
            else:
                counts['one_product_with_disjoint_binary_intervals'] += 1
    rng = random.Random(20260906)
    multiclass = 0
    for k in range(2, 9):
        for _ in range(100):
            raw = [[rng.randrange(1, 21) for _ in range(k)] for _ in range(4)]
            table = tuple(tuple(F(v, sum(row)) for v in row) for row in raw)
            assert verify(table) <= k-1
            multiclass += 1

    # Two diagonal segments whose every coordinate interval overlaps, but the
    # joint vector segments are disjoint. All probabilities are strictly positive.
    # D endpoints = center +/- u; O endpoints = center + w +/- v.
    # w is independent of u,v in the three-dimensional simplex (4 labels).
    center = (F(1, 4),)*4
    u = (F(1, 10), F(-1, 10), F(1, 10), F(-1, 10))
    v = (F(1, 10), F(1, 10), F(-1, 10), F(-1, 10))
    w = (F(1, 100), F(-1, 100), F(-1, 100), F(1, 100))
    table = tuple(tuple(center[y]+su*u[y]+sv*v[y]+sw*w[y] for y in range(4))
                  for su, sv, sw in ((-1, 0, 0), (0, -1, 1), (0, 1, 1), (1, 0, 0)))
    assert all(closed_intersection(tuple(row[y] for row in table)) for y in range(4))
    # Exact separating functional w: w.u=w.v=0, w.w>0.
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    assert dot(w, u) == dot(w, v) == 0 and dot(w, w) > 0
    projections = tuple(dot(w, row) for row in table)
    assert projections[0] == projections[3] < projections[1] == projections[2]
    verify(table)

    xor = ((F(3, 4), F(1, 4)), (F(1, 4), F(3, 4)),
           (F(1, 4), F(3, 4)), (F(3, 4), F(1, 4)))
    assert construct(xor) == ((3, 1), (0, 8), (0, 8), (48, 0))
    return {'status': 'PASS', 'arithmetic': 'exact rational',
            'scope': 'strictly positive static 2x2 conditional table; fixed unary sources and base 1 per label',
            'positive_binary_grid_tables': 256, 'binary_minimum_product_counts': counts,
            'random_positive_tables': multiclass, 'output_labels': '2 through 8',
            'seed': 20260906, 'maximum_product_nodes_in_construction': 1,
            'nonzero_product_head_edges_bound': 'k-1',
            'multiclass_coordinatewise_interval_shortcut_falsified': True,
            'multiclass_separating_functional_projections': [str(v) for v in projections],
            'noisy_xor_integer_construction_recovered': True,
            'not_claimed': ['minimum physical resources', 'registered coefficient reachability',
                            'information acquisition', 'runtime closure', 'GPU/AMP science']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_ONE_PRODUCT_TABLE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
