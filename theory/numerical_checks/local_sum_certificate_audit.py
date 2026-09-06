"""Exact global SUM counterexample despite local face and threshold certificates."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json

VERTICES = tuple(product((0, 1), repeat=3))
TARGET = tuple(F(k, 30) for k in (3, 11, 19, 11, 19, 11, 19, 27))


def audit():
    faces = []
    for axis, bit in product(range(3), (0, 1)):
        indices = [i for i, x in enumerate(VERTICES) if x[axis] == bit]
        values = [TARGET[i] for i in indices]
        diagonal, off = sorted((values[0], values[3])), sorted((values[1], values[2]))
        lo, hi = max(diagonal[0], off[0]), min(diagonal[1], off[1])
        assert lo <= hi
        faces.append({'fixed_axis': axis, 'fixed_bit': bit,
                      'intersection': [str(lo), str(hi)]})

    threshold_tests = ((F(1, 10), (2, 2, 2), 1),
                       (F(11, 30), (4, 4, -2), 3),
                       (F(19, 30), (2, 2, 2), 5))
    for cutoff, coefficients, threshold in threshold_tests:
        for x, p in zip(VERTICES, TARGET):
            score = sum(a*b for a, b in zip(coefficients, x))
            assert (score > threshold) == (p > cutoff)
            assert score != threshold

    minimum_gap = min(TARGET[1:])-TARGET[0]
    maximum_gap = TARGET[-1]-max(TARGET[:-1])
    decreasing_edge_gap = TARGET[2]-TARGET[3]
    assert minimum_gap == maximum_gap == decreasing_edge_gap == F(4, 15)
    distance = min(minimum_gap, maximum_gap, decreasing_edge_gap)/2
    assert distance == F(2, 15) and 2*distance**2/8 == F(1, 225)

    chi = tuple((-1)**sum(x) for x in VERTICES)
    affine = tuple(F(7+8*x[0]+8*x[1], 30) for x in VERTICES)
    assert all(p == r-distance*s for p, r, s in zip(TARGET, affine, chi))
    assert all(abs(p-r) == distance for p, r in zip(TARGET, affine))
    # Exact Farkas dual for the original homogeneous mass equations, including base.
    alpha = tuple(F(15, 2)*s for s in chi)
    atoms = [[(F(1), F(1)) for _ in VERTICES]]
    for axis, bit, label in product(range(3), (0, 1), (0, 1)):
        atoms.append([tuple(F(x[axis] == bit and y == label) for y in range(2)) for x in VERTICES])
    for atom in atoms:
        assert sum(a*(m[1]-p*sum(m)) for a, p, m in zip(alpha, TARGET, atom)) == sum(map(sum, atom))

    checked, antipodal_cases = 0, 0
    for weights in product((0, 1), repeat=12):
        q, masses = [], []
        for x in VERTICES:
            mass = tuple(1+sum(weights[4*i+2*x[i]+y] for i in range(3)) for y in range(2))
            q.append(F(mass[1], sum(mass)))
            masses.append(mass)
        assert sum(s*(m[1]-p*sum(m)) for s, p, m in zip(chi, TARGET, masses)) == distance*sum(map(sum, masses))
        assert max(abs(a-b) for a, b in zip(q, TARGET)) >= distance
        checked += 1
        if q.count(min(q)) != 1 or q.count(max(q)) != 1:
            continue
        low, high = q.index(min(q)), q.index(max(q))
        if low ^ high != 7:
            continue
        antipodal_cases += 1
        for i, x in enumerate(VERTICES):
            for axis in range(3):
                if x[axis] == VERTICES[low][axis]:
                    j = i ^ (1 << (2-axis))
                    assert q[j] >= q[i]
    assert antipodal_cases > 0
    return {'status': 'PASS', 'arithmetic': 'exact Fraction',
            'target_lexicographic': [str(p) for p in TARGET],
            'coordinate_faces_in_sum_closure': faces,
            'all_three_nontrivial_threshold_cuts_exactly_separated': True,
            'sharp_global_sup_norm_distance': str(distance),
            'matching_finite_sum_mass_total': 30,
            'explicit_global_cone_dual': [str(a) for a in alpha],
            'exact_dual_atom_equalities': len(atoms),
            'proved_uniform_excess_ce_lower_nats': '1/225',
            'small_sum_coefficient_assignments_checked': checked,
            'unique_antipodal_extrema_monotonicity_cases': antipodal_cases,
            'not_claimed': ['each face is finitely exactly representable',
                            'finite weight enumeration proves the universal lemma',
                            'failure of the complete residual-cone solver or Foundation R4']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_LOCAL_SUM_CERTIFICATE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
