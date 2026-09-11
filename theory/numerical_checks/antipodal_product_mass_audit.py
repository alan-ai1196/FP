"""Exact static observable-mass decisions; no Runtime or finite-encoding authority."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json
import random

from masked_product_closure_audit import classify, verify
from normalizer_chord_audit import log_bounds


def cube(d):
    return tuple(product((0, 1), repeat=d))


def observed(d, q):
    return tuple(sum(value*x[i]*(1-x[j]) for (i, j), value in q.items()) for x in cube(d))


def margins(d, table):
    assert type(d) is int and d >= 2 and len(table) == 2**d
    assert all(type(v) in (int, F) and v >= 0 for v in table)
    assert table[0] == table[-1] == 0
    lookup = dict(zip(cube(d), map(F, table)))
    r = tuple(lookup[tuple(int(k == i) for k in range(d))] for i in range(d))
    c = tuple(lookup[tuple(int(k != i) for k in range(d))] for i in range(d))
    return r, c


def family_three(r, c):
    a = (F(0), r[1]-c[0]+r[2]-c[1], r[2]-c[1])
    b = (r[0], c[0]-r[2]+c[1], c[1])
    return a, b, max(-v for v in a), min(b)


def fiber_table(a, b, t):
    forward = ((0, 1), (1, 2), (2, 0))
    reverse = ((0, 2), (1, 0), (2, 1))
    return {**{edge: t+v for edge, v in zip(forward, a)},
            **{edge: v-t for edge, v in zip(reverse, b)}}


def phi(a, b, t):
    return prod(t+v for v in a)-prod(v-t for v in b)


def classify_three(table):
    """Complete real-coefficient decision for rational f>=0 with f(000)=f(111)=0."""
    r, c = margins(3, table)
    if sum(r) != sum(c):
        return {'status': 'OUTSIDE_CLOSURE', 'reason': 'MARGIN_TOTALS'}
    a, b, lower, upper = family_three(r, c)
    if lower > upper:
        return {'status': 'OUTSIDE_CLOSURE', 'reason': 'EMPTY_TRANSPORT_INTERVAL',
                'interval': (lower, upper)}
    if lower < upper:
        return {'status': 'EXACT_REAL_FACTORIZATION', 'reason': 'INTERIOR_CUBIC_ROOT',
                'interval': (lower, upper)}
    q = fiber_table(a, b, lower)
    certificate = classify(3, 3, q)
    assert certificate['status'] != 'OUTSIDE_CLOSURE'
    status = ('EXACT_REAL_FACTORIZATION' if certificate['status'] == 'EXACT_FACTORIZATION'
              else 'LIMIT_ONLY')
    return {'status': status, 'reason': 'UNIQUE_BOUNDARY_LIFT', 'interval': (lower, upper),
            'coefficients': q, 'coefficient_certificate': certificate}


def verify_three(table, certificate):
    """Check external mass, a real-root existence interval, or a boundary lift."""
    try:
        r, c = margins(3, table)
        status, reason = certificate['status'], certificate['reason']
        if reason == 'MARGIN_TOTALS':
            return status == 'OUTSIDE_CLOSURE' and sum(r) != sum(c)
        if sum(r) != sum(c):
            return False
        a, b, lower, upper = family_three(r, c)
        if certificate['interval'] != (lower, upper):
            return False
        if reason == 'EMPTY_TRANSPORT_INTERVAL':
            # Independent Hall obstruction for the off-diagonal mask.
            return (status == 'OUTSIDE_CLOSURE' and lower > upper
                    and any(r[i]+c[i] > sum(r) for i in range(3)))
        if reason == 'INTERIOR_CUBIC_ROOT':
            # Every entry has slope +1 or -1. All six are positive inside;
            # Phi is strictly increasing there. No rounded root is accepted.
            return (status == 'EXACT_REAL_FACTORIZATION' and lower < upper
                    and phi(a, b, lower) < 0 < phi(a, b, upper)
                    and observed(3, fiber_table(a, b, (lower+upper)/2)) == tuple(table))
        if reason == 'UNIQUE_BOUNDARY_LIFT':
            return (lower == upper
                    and certificate['coefficients'] == fiber_table(a, b, lower)
                    and verify_observable(3, table, certificate['coefficients'],
                                          certificate['coefficient_certificate'], status))
        return False
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def verify_observable(d, table, q, coefficient_certificate, status):
    """A checked rational margin lift can reject ALL observable alternatives."""
    try:
        r, c = margins(d, table)
        if set(q) != {(i, j) for i in range(d) for j in range(d) if i != j}:
            return False
        if not verify(d, d, q, coefficient_certificate):
            return False
        coefficient_status = coefficient_certificate['status']
        if coefficient_status not in ('EXACT_FACTORIZATION', 'LIMIT_ONLY'):
            return False
        if any(sum(q[i, j] for j in range(d) if j != i) != r[i] for i in range(d)):
            return False
        if any(sum(q[i, j] for i in range(d) if i != j) != c[j] for j in range(d)):
            return False
        if observed(d, q) != tuple(table):
            return status == 'OUTSIDE_CLOSURE'
        expected = ('EXACT_REAL_FACTORIZATION' if coefficient_status == 'EXACT_FACTORIZATION'
                    else 'LIMIT_ONLY')
        return status == expected
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def isolate_root(a, b, lower, upper, bits=48):
    """Rational enclosure only; exact existence is proved before bisection."""
    assert lower < upper and phi(a, b, lower) < 0 < phi(a, b, upper)
    while upper-lower > F(1, 2**bits):
        middle = (lower+upper)/2
        value = phi(a, b, middle)
        if value == 0:
            return middle, middle
        if value < 0:
            lower = middle
        else:
            upper = middle
    return lower, upper


def literals(x):
    return tuple(v for bit in x for v in (1-bit, bit))


def affine(coefficients, x):
    return sum(a*b for a, b in zip(coefficients, literals(x)))


def xor_sum(x):
    return F((x[0] != x[1])+(x[2] != x[3]))


def transfer_bound(delta):
    leakage = 8*delta+8*delta/(1-16*delta)
    return (16*delta+leakage*(3+4*delta))/(1-4*delta)


def audit():
    decisions = Counter()
    for values in product(range(3), repeat=6):
        table = (F(0), *map(F, values), F(0))
        result = classify_three(table)
        assert verify_three(table, result)
        r, c = margins(3, table)
        cone = sum(r) == sum(c) and all(r[i]+c[i] <= sum(r) for i in range(3))
        assert (result['status'] != 'OUTSIDE_CLOSURE') == cone
        decisions[result['status']] += 1

    edges = tuple((i, j) for i in range(3) for j in range(3) if i != j)
    rejected_coefficients_but_exact_mass = 0
    original_decisions = Counter()
    boundary_example = None
    for weights in product(range(3), repeat=6):
        q = dict(zip(edges, map(F, weights)))
        table = observed(3, q)
        old = classify(3, 3, q)
        result = classify_three(table)
        assert verify_three(table, result) and result['status'] != 'OUTSIDE_CLOSURE'
        original_decisions[old['status']] += 1
        if old['status'] == 'OUTSIDE_CLOSURE' and result['status'] == 'EXACT_REAL_FACTORIZATION':
            rejected_coefficients_but_exact_mass += 1
        if result['status'] == 'LIMIT_ONLY':
            boundary_example = (table, result)
        r, c = margins(3, table)
        a, b, lower, upper = family_three(r, c)
        for t in {lower, (lower+upper)/2, upper}:
            assert observed(3, fiber_table(a, b, t)) == table
        if lower < upper:
            lo, hi = isolate_root(a, b, lower, upper, bits=12)
            assert phi(a, b, lo) <= 0 <= phi(a, b, hi) and hi-lo <= F(1, 4096)
        else:
            assert phi(a, b, lower) == 0

    r, c = tuple(map(F, (2, 3, 4))), (F(3),)*3
    a, b, lower, upper = family_three(r, c)
    endpoint = fiber_table(a, b, lower)
    irrational_table = observed(3, endpoint)
    assert classify(3, 3, endpoint)['status'] == 'OUTSIDE_CLOSURE'
    assert classify_three(irrational_table)['status'] == 'EXACT_REAL_FACTORIZATION'
    for t in map(F, range(-3, 4)):
        assert phi(a, b, t) == 2*t**3-5*t**2+17*t-12
    rational_candidates = {F(sign*p, q) for sign in (-1, 1) for p in (1, 2, 3, 4, 6, 12)
                           for q in (1, 2)}
    assert all(phi(a, b, t) != 0 for t in rational_candidates)
    root_interval = isolate_root(a, b, lower, upper)

    # Full four-bit mass: the unique margin lift is checked independently of
    # the supplied target, including its non-singleton contexts.
    contexts = cube(4)
    target = tuple(xor_sum(x) for x in contexts)
    canonical = {(i, j): F(1, 3) for i in range(4) for j in range(4) if i != j}
    canonical_certificate = classify(4, 4, canonical)
    assert verify_observable(4, target, canonical, canonical_certificate, 'OUTSIDE_CLOSURE')
    assert all(observed(4, canonical)[k] == F(sum(x)*(4-sum(x)), 3)
               for k, x in enumerate(contexts))
    for x in contexts:
        native = ((x[0]+x[1])*((1-x[0])+(1-x[1]))
                  +(x[2]+x[3])*((1-x[2])+(1-x[3])))
        assert native == xor_sum(x) and 2+native <= 4

    zero = [x for x in contexts if xor_sum(x) == 0]
    double = [x for x in contexts if xor_sum(x) == 2]
    assert len(zero) == len(double) == 4
    assert all(sum(x[i] for x in zero) == sum(x[i] for x in double) == 2 for i in range(4))
    visible, signal, bad = [], [], []
    for i, j in product(range(8), repeat=2):
        atom = [literals(x)[i]*literals(x)[j] for x in contexts]
        if not any(atom):
            continue
        visible.append((i, j))
        mean = sum(F(literals(x)[i]*literals(x)[j], 4) for x in zero)
        if mean == 0:
            signal.append((i, j))
            assert i//4 == j//4 and i//2 != j//2 and i % 2 != j % 2
        else:
            bad.append((i, j))
            assert mean >= F(1, 4)
    assert (len(visible), len(signal), len(bad)) == (56, 8, 48)
    first = [edge for edge in signal if edge[0]//4 == 0]
    second = [edge for edge in signal if edge[0]//4 == 1]
    for (i, j), (k, l) in product(first, second):
        assert (i, l) in bad and (k, j) in bad

    rng = random.Random(20260911)
    alphabet = (F(0), F(1, 16), F(1, 4), F(1), F(4), F(16))
    scalar_cases, conditional_cases, supplied_lifts = 400, 600, 300
    for _ in range(scalar_cases):
        remainder, u, v = [[rng.choice(alphabet) for _ in range(8)] for _ in range(3)]
        values = [affine(remainder, x)+affine(u, x)*affine(v, x) for x in contexts]
        delta = max(abs(g-xor_sum(x)) for g, x in zip(values, contexts))
        leakage = max(affine(remainder, x)+affine(u, x)*affine(v, x) for x in zero)
        assert delta >= F(1, 7)
        assert sum(remainder)+sum(u[i]*v[j] for i, j in bad) <= 4*leakage
        assert all(u[i]*v[j] <= leakage for i, j in bad)
        for (i, j), (k, l) in product(first, second):
            assert (u[i]*v[j])*(u[k]*v[l]) == (u[i]*v[l])*(u[k]*v[j])

    for _ in range(conditional_cases):
        a0, a1, u, v = [[rng.choice(alphabet) for _ in range(8)] for _ in range(4)]
        theta = F(rng.randrange(17), 16)
        h = [affine(u, x)*affine(v, x) for x in contexts]
        excess = [(affine(a0, x)+theta*z, affine(a1, x)+(1-theta)*z)
                  for x, z in zip(contexts, h)]
        maximum = max(sum(pair) for pair in excess)
        scale = min(F(1), F(2)/maximum) if maximum else F(1)
        masses = [(1+scale*e0, 1+scale*e1) for e0, e1 in excess]
        assert all(sum(pair) <= 4 for pair in masses)
        delta = max(abs(m1/(m0+m1)-(1+f)/(2+f))
                    for (m0, m1), f in zip(masses, target))
        assert delta > F(1, 500)

    for _ in range(supplied_lifts):
        u, v = [[rng.choice(alphabet) for _ in range(4)] for _ in range(2)]
        q = {(i, j): u[i]*v[j] for i in range(4) for j in range(4) if i != j}
        assert verify_observable(4, observed(4, q), q, classify(4, 4, q), 'EXACT_REAL_FACTORIZATION')

    # Exact constants, rather than a floating loss difference.
    bound = transfer_bound(F(1, 500))
    assert bound < F(1, 7)
    assert F(2, 16)*F(1, 500)**2 == F(1, 2000000)
    for delta in (F(0), F(1, 100000), F(1, 1000), F(1, 500)):
        assert transfer_bound(delta) <= bound

    # A float64 local search suggested this simple rational one-PRODUCT
    # control. Its feasibility and CE upper bound are independently exact;
    # no optimizer success flag or global optimality claim is used.
    a0 = tuple(map(F, (0, '7/400', '77/400', 0, 0, 0, 0, 0)))
    a1 = tuple(map(F, ('83/200', 0, 0, '1/50', 0, 0, 0, 0)))
    u = tuple(map(F, (0, '1/15', '1/15', 0, 0, '13/30', 0, '13/30')))
    v = tuple(map(F, (0, '3/8', '3/8', 0, '12/5', 0, '12/5', 0)))
    risk_lower = risk_upper = F(0)
    control_peak = F(0)
    for x in contexts:
        m0 = 1+affine(a0, x)
        m1 = 1+affine(a1, x)+affine(u, x)*affine(v, x)
        control_peak = max(control_peak, m0+m1)
        assert m0+m1 <= 4
        p = (1+xor_sum(x))/(2+xor_sum(x))
        q = m1/(m0+m1)
        for weight, ratio in ((p, p/q), (1-p, (1-p)/(1-q))):
            lo, hi = log_bounds(ratio, bits=64, terms=24)
            risk_lower += weight*lo/16
            risk_upper += weight*hi/16
    assert F('0.00889241107354') < risk_lower <= risk_upper < F('0.00889241107355')

    forgeries = []
    forgeries.append(verify_observable(4, target, canonical, canonical_certificate, 'EXACT_REAL_FACTORIZATION'))
    wrong = dict(canonical)
    wrong[0, 1] += 1
    forgeries.append(verify_observable(4, target, wrong, canonical_certificate, 'OUTSIDE_CLOSURE'))
    omitted = dict(canonical)
    del omitted[0, 1]
    forgeries.append(verify_observable(4, target, omitted, canonical_certificate, 'OUTSIDE_CLOSURE'))
    forgeries.append(verify_observable(3, irrational_table, endpoint, classify(3, 3, endpoint), 'OUTSIDE_CLOSURE'))
    forged = deepcopy(classify_three(irrational_table))
    forged['interval'] = (F(0), F(0))
    forgeries.append(verify_three(irrational_table, forged))
    assert boundary_example is not None
    boundary_table, certificate = boundary_example
    forged = deepcopy(certificate)
    forged['status'] = 'EXACT_REAL_FACTORIZATION'
    forgeries.append(verify_three(boundary_table, forged))
    changed = list(irrational_table)
    changed[1] += 1
    forgeries.append(verify_three(changed, classify_three(irrational_table)))
    assert not any(forgeries)

    return {'status': 'PASS',
            'scope': 'static scalar mass on the full cube with both antipodal values zero; real nonnegative coefficients',
            'three_input_mass_grid_cases': 3**6, 'three_input_decisions': dict(decisions),
            'independent_transport_Hall_checks': 3**6,
            'three_input_original_coefficient_grid_cases': 3**6,
            'original_coefficient_decisions': dict(original_decisions),
            'rejected_original_coefficients_with_exact_alternative_mass_lifts': rejected_coefficients_but_exact_mass,
            'irrational_lift_polynomial_ascending': [-12, 17, -5, 2],
            'irrational_root_exact_interval': list(map(str, root_interval)),
            'rational_root_candidates_excluded': len(rational_candidates),
            'four_input_target_mass': list(map(int, target)),
            'four_input_unique_margin_lift_off_diagonal': '1/3',
            'visible_signal_other_literal_pairs': [len(visible), len(signal), len(bad)],
            'exact_scalar_mass_bound': '1/7', 'exact_probability_separation': '1/500',
            'exact_conditional_to_mass_bound_at_threshold': str(bound),
            'exact_CE_gap_lower_bound_nats': '1/2000000',
            'rational_one_PRODUCT_control': {
                'literal_order': '(1-x1),x1,(1-x2),x2,(1-x3),x3,(1-x4),x4',
                'A0': list(map(str, a0)), 'A1': list(map(str, a1)),
                'U': list(map(str, u)), 'V': list(map(str, v)),
                'masses': '(1+A0,1+A1+UV)', 'exact_peak_normalizer': str(control_peak),
                'outward_CE_excess_interval_nats': ['0.00889241107354', '0.00889241107355'],
                'not_claimed_globally_optimal': True},
            'exact_scalar_expansion_cases': scalar_cases, 'exact_capped_conditional_cases': conditional_cases,
            'checked_supplied_four_input_lifts': supplied_lifts,
            'forged_certificates_rejected': len(forgeries),
            'not_claimed': ['sharp separation constants', 'finite-rational exact realization of irrational lift',
                            'complete arbitrary-d algebraic margin solver', 'all unrestricted conditional tables',
                            'registered value construction, installation, fresh persistence or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_ANTIPODAL_PRODUCT_MASS_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
