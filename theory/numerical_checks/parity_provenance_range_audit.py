"""Exact primal/dual range optima and positive-provenance counterexample audit."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random


def problem(d, r):
    vertices = tuple(product((0, 1), repeat=d))
    target = tuple((1 if sum(x[1:]) == 0 else r)/(r+1)
                   if sum(x) % 2 else (r if sum(x[1:]) == 0 else 1)/(r+1)
                   for x in vertices)
    edges = tuple((i, j) for i, x in enumerate(vertices) for j, z in enumerate(vertices)
                  if i < j and sum(a != b for a, b in zip(x, z)) == 1)
    return vertices, target, edges


def thresholds(d, r):
    return r+1, (r+1)*(2**(d-1)-1), (r+1)*((r+1)**(d-1)-1)/r


def check(masses, target, vertices, degree_below_d=False):
    assert all(min(m) >= 1 and m[1]/sum(m) == p for m, p in zip(masses, target))
    if degree_below_d:
        for y in range(2):
            assert sum((-1)**sum(x)*m[y] for x, m in zip(vertices, masses)) == 0
    return max(map(sum, masses))


def constructions(d, r):
    vertices, target, edges = problem(d, r)
    m = d-1
    all_masses, degree_masses = [], []
    for x in vertices:
        root, parity = not any(x[1:]), sum(x) % 2
        correct, other = (F(1), r) if root else (r, F(1))
        all_masses.append((other, correct) if parity else (correct, other))
        scale = 2**m-1 if root else 1
        degree_masses.append(tuple(scale*v for v in all_masses[-1]))
    u = [F(0)]*(m+2)
    for k in range(m, 0, -1):
        u[k] = ((r-1)+(m-k)*r*u[k+1])/k
    s = ((r+1)**m-1)/r
    assert m*u[1] == (r-1)*s
    assert all(u[k] >= u[k+1] >= 0 for k in range(1, m))
    edge_masses = [[F(1), F(1)] for _ in vertices]
    for i, j in edges:
        x, z = vertices[i], vertices[j]
        if x[0] != z[0]:
            if not any(x[1:]):
                for v in (i, j):
                    edge_masses[v][0] += s-1
                    edge_masses[v][1] += s-1
        else:
            child = max((i, j), key=lambda v: sum(vertices[v][1:]))
            depth = sum(vertices[child][1:])
            label = sum(vertices[child]) % 2
            for v in (i, j):
                edge_masses[v][label] += u[depth]
    actual = (check(all_masses, target, vertices),
              check(degree_masses, target, vertices, True),
              check(edge_masses, target, vertices, True))
    assert actual == thresholds(d, r)
    return actual, u[1:], edge_masses


def certified_lp(d, r, kind):
    import numpy as np
    from scipy.optimize import linprog
    vertices, target, edges = problem(d, r)
    n = len(vertices)
    features = (tuple(tuple(F(i in e) for e in edges) for i in range(n)) if kind == 'support'
                else tuple(tuple(F(i == j) for j in range(n)) for i in range(n)))
    width = 2*len(features[0])+1  # Independent mass slots, then peak R.
    eq, rhs, ub, limits = [], [], [], []
    for row, p in zip(features, target):
        eq.append(tuple(f*(F(y == 1)-p) for f in row for y in range(2))+(F(0),))
        rhs.append(2*p-1)
        ub.append(tuple(f for f in row for _ in range(2))+(F(-1),))
        limits.append(F(-2))
    if kind == 'degree':
        for label in range(2):
            eq.append(tuple(sum((-1)**sum(x)*features[i][j]*F(y == label)
                                for i, x in enumerate(vertices))
                            for j in range(len(features[0])) for y in range(2))+(F(0),))
            rhs.append(F(0))
    objective = (F(0),)*(width-1)+(F(1),)
    result = linprog(np.array(objective, float), A_eq=np.array(eq, float), b_eq=np.array(rhs, float),
                     A_ub=np.array(ub, float), b_ub=np.array(limits, float), bounds=(0, None), method='highs')
    if not result.success:
        raise RuntimeError('UNRESOLVED: LP proposed no optimal primal/dual pair')
    rational = lambda v: F(float(v)).limit_denominator(10**7)
    primal = tuple(map(rational, result.x))
    equality_dual = tuple(map(rational, result.eqlin.marginals))
    inequality_dual = tuple(map(rational, result.ineqlin.marginals))
    dot = lambda a, b: sum((x*y for x, y in zip(a, b)), F(0))
    assert min(primal) >= 0 and max(inequality_dual) <= 0
    assert all(dot(a, primal) == b for a, b in zip(eq, rhs))
    assert all(dot(a, primal) <= b for a, b in zip(ub, limits))
    for j in range(width):
        assert sum(a[j]*y for a, y in zip(eq, equality_dual))+sum(a[j]*z for a, z in zip(ub, inequality_dual)) <= objective[j]
    dual_value = dot(rhs, equality_dual)+dot(limits, inequality_dual)
    assert dot(objective, primal) == dual_value
    expected = thresholds(d, r)[{'all': 0, 'degree': 1, 'support': 2}[kind]]
    assert dual_value == expected
    return {'bits': d, 'odds': str(r), 'class': kind, 'exact_optimum': str(dual_value),
            'original_rational_primal_and_dual_verified': True}


def audit():
    construction_cases, display = 0, []
    for d, r in product(range(3, 9), (F(3, 2), F(2), F(3), F(5))):
        values, u, _ = constructions(d, r)
        assert values[0] < values[1] < values[2]
        construction_cases += 1
        if r == 3:
            display.append({'bits': d, 'all': str(values[0]), 'reduced_degree': str(values[1]),
                            'proper_positive_support': str(values[2])})
    lp_checks = [certified_lp(d, r, kind) for d, r in ((3, F(3)), (4, F(3)), (5, F(3)), (3, F(3, 2)))
                 for kind in ('all', 'degree', 'support')]

    cap, r, support_peak = F(12), F(3), F(20)
    delta = (r-1)*(support_peak-cap)/((r+1)*cap*(support_peak+2*r))
    assert delta == F(1, 78) and 2*delta**2/8 == F(1, 24336)
    vertices, target, edges = problem(3, r)
    # Independent infeasibility audit strictly inside the analytic exclusion ball.
    from positive_cone_closure_audit import checked_feasibility
    trial_delta = F(1, 79)
    inequalities, limits = [], []
    for i, p in enumerate(target):
        row = tuple(F(i in e) for e in edges)
        for endpoint, sign in ((p+trial_delta, F(1)), (p-trial_delta, F(-1))):
            inequalities.append(tuple(sign*f*(F(y == 1)-endpoint) for f in row for y in range(2)))
            limits.append(sign*(2*endpoint-1))
        inequalities.append(tuple(f for f in row for _ in range(2)))
        limits.append(cap-2)
    equations = [row+tuple(F(i == j) for j in range(len(inequalities)))
                 for i, row in enumerate(inequalities)]
    alternative, _ = checked_feasibility(equations, limits)
    assert alternative == 'dual'
    rng, checked = random.Random(20260908), 0
    for _ in range(1000):
        masses = [[F(1), F(1)] for _ in vertices]
        for i, j in edges:
            for y in range(2):
                weight = rng.randrange(3)
                masses[i][y] += weight
                masses[j][y] += weight
        actual_cap = max(map(sum, masses))
        if actual_cap <= cap:
            assert max(abs(m[1]/sum(m)-p) for m, p in zip(masses, target)) >= delta
            checked += 1
    assert checked > 0
    return {'status': 'PASS', 'scope': 'static reversed-root noisy parity; final-normalizer cap',
            'exact_three_class_construction_cases': construction_cases,
            'odds_three_thresholds': display, 'independent_exact_primal_dual_lp_checks': lp_checks,
            'three_bit_cap_12_proper_support_distance_lower': str(delta),
            'three_bit_cap_12_proper_support_excess_ce_lower': '1/24336',
            'independent_exact_farkas_exclusion_at_distance_1_over_79': True,
            'finite_random_edge_models_within_cap_checked': checked,
            'not_claimed': ['reduced polynomial degree preserves positive derivation support',
                            'sharp approximation margin', 'minimal physical implementation costs',
                            'registered value/build/install reachability', 'complete runtime or AMP certification']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_PARITY_PROVENANCE_RANGE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
