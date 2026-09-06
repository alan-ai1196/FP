"""Exact audit of a finite-range task-forced native PRODUCT phase.

Only the final readout normalizer is capped; no hardware-resource claim is made.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from normalized_sum_xor_audit import sum_probabilities

CELLS = tuple(product((0, 1), repeat=2))
TARGET = (F(1, 2), F(1, 2), F(3, 4), F(1, 4))


def mixed(values):
    return values[0]+values[3]-values[1]-values[2]


def inspect(masses):
    assert all(len(row) == 2 and min(row) >= 1 for row in masses)
    totals = tuple(sum(row) for row in masses)
    p = tuple(row[1]/total for row, total in zip(masses, totals))
    return p, max(totals), max(abs(v-t) for v, t in zip(p, TARGET))


def sum_range(delta):
    assert delta > 0
    if delta <= F(1, 8):
        return (1-4*delta)/(delta*(1+4*delta))
    if delta <= F(1, 4):
        return 4/(1+4*delta)
    return F(2)


def sum_witness(delta):
    if delta <= F(1, 8):
        s = 4/(1+4*delta)
        t = s*(F(1, 4)-delta)/delta
        totals = (t, t, s, s)
        q = (F(1, 2)+delta, F(1, 2)-delta, F(3, 4)-delta, F(1, 4)+delta)
    elif delta <= F(1, 4):
        totals = (4/(1+4*delta),)*4
        q = (F(3, 4)-delta, F(1, 4)+delta)*2
    else:
        totals, q = (F(2),)*4, (F(1, 2),)*4
    masses = tuple((t*(1-v), t*v) for t, v in zip(totals, q))
    assert all(mixed(tuple(row[y] for row in masses)) == 0 for y in (0, 1))
    # Construct actual nonnegative unary SUM weights after subtracting the base.
    weights = [F(0)]*8
    for y in (0, 1):
        values = [row[y]-1 for row in masses]
        k = min(range(4), key=values.__getitem__)
        ir, jc = CELLS[k]
        for i in (0, 1):
            weights[2*i+y] = values[2*i+jc]
        for j in (0, 1):
            weights[4+2*j+y] = values[2*ir+j]-values[k]
    assert min(weights) >= 0 and sum_probabilities(weights) == q
    return masses


def audit():
    tradeoff = []
    for delta in (F(1, 100), F(1, 32), F(1, 16), F(1, 8), F(3, 16), F(1, 4), F(1, 3)):
        p, peak, error = inspect(sum_witness(delta))
        assert error <= delta and peak == sum_range(delta)
        tradeoff.append({'error_budget': str(delta), 'attained_peak_normalizer': str(peak),
                         'actual_error': str(error)})

    nontrivial = 0
    for weights in product(range(3), repeat=8):
        masses = tuple(tuple(F(1+weights[2*i+y]+weights[4+2*j+y]) for y in (0, 1))
                       for i, j in CELLS)
        p, peak, error = inspect(masses)
        assert error > 0 and peak >= sum_range(error)
        nontrivial += error < F(1, 4)

    two = tuple((F(1+2*x*z), F(1+2*x*(1-z))) for x, z in CELLS)
    one = []
    for x, z in CELLS:
        h = (1-x+z)*(3*x+F(5, 3)*(1-z))
        one.append((1+h, 1+F(1, 3)*x+F(5, 3)*(1-z)))
    assert inspect(two) == (TARGET, F(4), F(0))
    assert inspect(one) == (TARGET, F(16, 3), F(0))
    assert mixed(tuple(row[1] for row in one)) == 0

    # Generic native PRODUCT of two arbitrary unary SUMs, routed to both heads.
    # Scale all evidence to obey each R; this is a legal nonnegative SUM scaling.
    rng = random.Random(20260906)
    checked = 0
    for cap in (F(4), F(5)):
        for _ in range(1000):
            left = [rng.randrange(6) for _ in range(4)]
            right = [rng.randrange(6) for _ in range(4)]
            unary = [rng.randrange(6) for _ in range(8)]
            routing = [rng.randrange(6) for _ in range(2)]
            raw = []
            for x, z in CELLS:
                h = (left[x]+left[2+z])*(right[x]+right[2+z])
                raw.append(tuple(F(unary[2*x+y]+unary[4+2*z+y]+routing[y]*h) for y in (0, 1)))
            largest = max(sum(row) for row in raw)
            scale = (cap-2)/largest if largest else F(0)
            masses = tuple(tuple(1+scale*v for v in row) for row in raw)
            d0, d1 = (mixed(tuple(row[y] for row in masses)) for y in (0, 1))
            assert d0*d1 >= 0
            _, peak, error = inspect(masses)
            assert peak <= cap
            assert error >= (16-3*cap)/(48+16*cap)
            checked += 1

    # Rational bracketing of an irrational optimum; comparisons are exact.
    lower, upper = F(103553390593, 10**12), F(103553390594, 10**12)
    assert sum_range(lower) > 4 > sum_range(upper)
    # The robust all-one-PRODUCT gap at cap 4, using the proved KL inequality.
    d4 = (16-3*F(4))/(48+16*F(4))
    assert d4 == F(1, 28) and d4*d4/2 == F(1, 1568)
    return {
        'status': 'PASS', 'arithmetic': 'exact rational',
        'resource_scope': 'final normalizer cap only, fixed base (1,1)',
        'target_class_one_probability': [str(v) for v in TARGET],
        'sharp_sum_range_error_witnesses': tradeoff,
        'exhaustive_unary_sum_assignments': 3**8,
        'assignments_testing_nontrivial_range_bound': nontrivial,
        'exact_one_product_threshold': '16/3', 'exact_two_product_threshold': '4',
        'one_product_witness_mass_pairs': [[str(v) for v in row] for row in one],
        'two_product_witness_mass_pairs': [[str(v) for v in row] for row in two],
        'generic_product_of_sums_random_controls': checked,
        'random_seed': 20260906,
        'cap_four_sum_optimal_error': {'algebraic': '(sqrt(2)-1)/4',
                                     'certified_lower': str(lower), 'certified_upper': str(upper)},
        'cap_four_at_most_one_product_supnorm_lower_bound': '1/28',
        'cap_four_at_most_one_product_excess_ce_lower_bound': '1/1568',
        'not_claimed': ['sharp one-product approximation curve', 'one-product uniqueness at larger cap',
                        'intermediate-activation bound', 'hardware bytes/FLOPs optimum',
                        'registered optimizer reachability', 'Compiler/AMP closure'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_RANGE_PRODUCT_PHASE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
