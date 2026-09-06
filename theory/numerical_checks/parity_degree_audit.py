"""Exact parity moments, likelihood bounds and native edge-hierarchy witnesses."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from math import log
import argparse
import json


def cube(d):
    return tuple(product((0, 1), repeat=d))


def edges(d):
    vertices = cube(d)
    return tuple((u, v) for u, x in enumerate(vertices) for v, z in enumerate(vertices)
                 if u < v and sum(a != b for a, b in zip(x, z)) == 1)


def likelihood(masses):
    value = F(1)
    d = (len(masses)-1).bit_length()
    for x, m in zip(cube(d), masses):
        correct = F(m[sum(x) % 2], sum(m))
        value *= correct**3*(1-correct)
    return value


def envelope_likelihood(n):
    return F(1, 16)**2*F(27, 256)**(n-2)


def check_mass_moment(masses, d):
    for y in range(2):
        assert sum(((-1)**sum(x)*m[y] for x, m in zip(cube(d), masses)), F(0)) == 0


def hierarchy(d, k, eta=F(1, 4)):
    vertices = cube(d)
    index = {x: i for i, x in enumerate(vertices)}
    other_root = index[(1,)+(0,)*(d-1)]
    selected = [(0, other_root, k**d, F(1, 2))]
    for v, x in enumerate(vertices):
        depth = sum(x[1:])
        if depth:
            axis = next(i for i in range(1, d) if x[i])
            parent = x[:axis]+(0,)+x[axis+1:]
            probability = 1-eta if sum(x) % 2 else eta
            selected.append((index[parent], v, k**(d-depth), probability))
    assert len(selected) == len(vertices)-1
    masses = [[F(1), F(1)] for _ in vertices]
    for u, v, weight, p in selected:
        assert sum(a != b for a, b in zip(vertices[u], vertices[v])) == 1
        for j in (u, v):
            masses[j][0] += weight*(1-p)
            masses[j][1] += weight*p
    limiting = [1-eta if sum(x) % 2 else eta for x in vertices]
    limiting[0] = limiting[other_root] = F(1, 2)
    error = max(abs(m[1]/sum(m)-p) for m, p in zip(masses, limiting))
    assert error <= F(d+1, k)
    assert max(map(sum, masses)) <= 2+k**d+(d-1)*k**(d-1)
    check_mass_moment(masses, d)
    return masses, error


def audit():
    moment_cases = 0
    for d in range(2, 9):
        vertices = cube(d)
        # Every proper-subset ordinary monomial has zero top parity moment.
        for mask in range((1 << d)-1):
            assert sum((-1)**sum(x)*all(x[i] for i in range(d) if mask >> i & 1)
                       for x in vertices) == 0
            moment_cases += 1
        for u, v in edges(d):
            assert (-1)**sum(vertices[u])+(-1)**sum(vertices[v]) == 0

    d, sparse_cases = 3, 0
    atoms = tuple(product(edges(d), range(2)))
    for count in range(3):
        for chosen in combinations(atoms, count):
            for weights in product((1, 3), repeat=count):
                masses = [[F(1), F(1)] for _ in cube(d)]
                for ((u, v), label), weight in zip(chosen, weights):
                    masses[u][label] += weight
                    masses[v][label] += weight
                check_mass_moment(masses, d)
                assert likelihood(masses) < envelope_likelihood(8)
                sparse_cases += 1

    rows = []
    hierarchy_cases = 0
    for d in range(2, 9):
        for k in (2, 4, 16, 256):
            masses, error = hierarchy(d, k)
            assert likelihood(masses) < envelope_likelihood(len(masses))
            hierarchy_cases += 1
            if k == 256:
                h = -F(1, 4)*log(.25)-F(3, 4)*log(.75)
                optimum = h+2**(1-d)*(log(2)-h)
                loss = -sum(3*log(float(m[sum(x) % 2]/sum(m)))
                            +log(float(m[1-sum(x) % 2]/sum(m)))
                            for x, m in zip(cube(d), masses))/(4*len(masses))
                rows.append({'bits': d, 'K': k, 'maximum_prediction_error': str(error),
                             'proved_prediction_error_upper': str(F(d+1, k)),
                             'ce_float64_display': loss, 'infimum_float64_display': optimum})
        hierarchy(d, 256, F(0))  # Deterministic-label construction is also legal.

    return {'status': 'PASS', 'arithmetic': 'exact Fraction decisions; CE floats are displays only',
            'scope': 'all mass polynomials of multilinear degree < d; uniform noisy parity',
            'proper_monomial_parity_moments_checked': moment_cases,
            'exhaustive_three_bit_edge_assignments_with_at_most_two_active_slots': sparse_cases,
            'positive_noise_hierarchies_checked': hierarchy_cases,
            'noise_one_quarter_witnesses': rows,
            'not_claimed': ['unary-SUM conjecture for d>=3 proved',
                            'sharp semantic PRODUCT count or physical resource minimum',
                            'finite attainment of the infimum', 'registered value/build/install reachability',
                            'complete runtime, fresh persistence or AMP bridge']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_PARITY_DEGREE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
