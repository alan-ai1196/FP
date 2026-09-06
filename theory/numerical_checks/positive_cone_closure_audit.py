"""LP proposals checked by exact primal/dual arithmetic for the closure theorem.

Requires NumPy/SciPy for proposals; a numerical status alone proves nothing.
No returned status authorizes an FP Compiler decision or installation.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

import numpy as np
from scipy.optimize import linprog

from normalized_sum_xor_audit import closed_intersection, finite_sum_representation


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def checked_feasibility(equations, rhs):
    """E x=b, x>=0: return an exactly verified primal or Farkas alternative."""
    e = np.array(equations, dtype=np.float64)
    b = np.array(rhs, dtype=np.float64)
    primal = linprog(np.zeros(e.shape[1]), A_eq=e, b_eq=b, bounds=(0, None), method='highs')
    if primal.success:
        x = tuple(F(float(v)).limit_denominator(10**9) for v in primal.x)
        if min(x) >= 0 and all(dot(row, x) == value for row, value in zip(equations, rhs)):
            return 'primal', x
    # E.T y >= 0 and b.T y <= -1. Verify against original rationals.
    dual = linprog(np.zeros(e.shape[0]), A_ub=np.vstack((-e.T, b)),
                   b_ub=np.r_[np.zeros(e.shape[1]), -1.0], bounds=(None, None), method='highs')
    if dual.success:
        y = tuple(F(float(v)).limit_denominator(10**9) for v in dual.x)
        if dot(rhs, y) < 0 and all(dot(column, y) >= 0 for column in zip(*equations)):
            return 'dual', y
    raise RuntimeError('UNRESOLVED: numerical solver supplied no exactly verified alternative')


class PositiveTable:
    def __init__(self, features, target):
        self.target = tuple(tuple(F(v) for v in row) for row in target)
        self.n, self.k = len(target), len(target[0])
        self.j = len(features[0])
        assert len(features) == self.n
        assert all(len(row) == self.k and min(row) >= 0 and sum(row) == 1 for row in self.target)
        assert all(len(row) == self.j and min(row) >= 0 for row in features)
        self.atoms = tuple(tuple(tuple(
            [F(1)] + [F(features[x][j]) if y == z else F(0)
                      for j in range(self.j) for z in range(self.k)])
            for y in range(self.k)) for x in range(self.n))
        self.totals = tuple(tuple(sum(self.atoms[x][y][d] for y in range(self.k))
                                  for d in range(1+self.j*self.k)) for x in range(self.n))

    def equations(self, residual):
        return [tuple(self.atoms[x][y][d]-self.target[x][y]*self.totals[x][d]
                      for d in range(1+self.j*self.k))
                for x in residual for y in range(1, self.k)]

    def exact(self):
        a = self.equations(range(self.n))
        # lambda=1+u, u>=0; no unsupported endpoint with lambda=0.
        status, point = checked_feasibility(a, [-row[0] for row in a])
        if status == 'primal':
            point = (point[0]+1,)+point[1:]
            assert point[0] >= 1
            assert all(dot(row, point) == 0 for row in a)
        return status, point

    def closure(self):
        residual = tuple(range(self.n))
        layers, covered = [], []
        while residual:
            a = self.equations(residual)
            s = tuple(sum(self.totals[x][d] for x in residual) for d in range(1+self.j*self.k))
            status, point = checked_feasibility(a+[s], [F(0)]*len(a)+[F(1)])
            if status == 'dual':
                assert point[-1] < 0
                alpha = tuple(v/(-point[-1]) for v in point[:-1])
                assert all(dot(column, alpha) >= value for column, value in zip(zip(*a), s))
                c = max(sum(abs(alpha[i*(self.k-1)+y]) for y in range(self.k-1))
                        for i in range(len(residual)))
                assert c > 0
                return {'in_closure': False, 'layers': tuple(layers), 'covered': tuple(covered),
                        'residual': residual, 'alpha': alpha, 'supnorm_separation': 1/c}
            newly = tuple(x for x in residual if dot(self.totals[x], point) > 0)
            assert newly
            layers.append(point)
            covered.append(newly)
            residual = tuple(x for x in residual if x not in newly)
        return {'in_closure': True, 'layers': tuple(layers), 'covered': tuple(covered), 'residual': ()}

    def approximation(self, certificate, epsilon):
        assert certificate['in_closure'] and 0 < epsilon <= 1
        layers, covered = certificate['layers'], certificate['covered']
        v = tuple(sum(epsilon**j*layer[d] for j, layer in enumerate(layers))
                  + (epsilon**len(layers) if d == 0 else 0)
                  for d in range(1+self.j*self.k))
        assert v[0] > 0 and min(v) >= 0
        error, bound_constant = F(0), F(0)
        for l, contexts in enumerate(covered):
            for x in contexts:
                t0 = dot(self.totals[x], layers[l])
                assert t0 > 0 and all(dot(self.totals[x], earlier) == 0 for earlier in layers[:l])
                remainder = sum(max(abs(dot(self.atoms[x][y], layer)-self.target[x][y]*dot(self.totals[x], layer))
                                    for y in range(self.k)) for layer in layers[l+1:])
                remainder += max(abs(1-self.target[x][y]*self.k) for y in range(self.k))
                bound_constant = max(bound_constant, remainder/t0)
                prediction = tuple(dot(self.atoms[x][y], v)/dot(self.totals[x], v) for y in range(self.k))
                error = max(error, max(abs(q-p) for q, p in zip(prediction, self.target[x])))
        assert error <= bound_constant*epsilon
        return error, bound_constant


def grid_features(n, m):
    return tuple(tuple(int(i == r) for r in range(n))+tuple(int(j == c) for c in range(m))
                 for i, j in product(range(n), range(m)))


def audit():
    exact_yes, closure_only, outside = 0, 0, 0
    max_layers = 0
    for p in product((F(1, 5), F(2, 5), F(3, 5), F(4, 5)), repeat=4):
        model = PositiveTable(grid_features(2, 2), tuple((1-v, v) for v in p))
        exact, _ = model.exact()
        result = model.closure()
        assert (exact == 'primal') == (finite_sum_representation(p) is not None)
        assert result['in_closure'] == closed_intersection(p)
        max_layers = max(max_layers, len(result['layers']))
        if exact == 'primal':
            exact_yes += 1
        elif result['in_closure']:
            closure_only += 1
        else:
            outside += 1
        if result['in_closure']:
            model.approximation(result, F(1, 100))
    endpoint_tables = 0
    for p in product((F(0), F(1, 2), F(1)), repeat=4):
        model = PositiveTable(grid_features(2, 2), tuple((1-v, v) for v in p))
        result = model.closure()
        assert result['in_closure'] == closed_intersection(p)
        assert (model.exact()[0] == 'primal') == (finite_sum_representation(p) is not None)
        if result['in_closure']:
            model.approximation(result, F(1, 100))
        endpoint_tables += 1
    # Known feasible rational models: independent construction, larger table/heads.
    rng = random.Random(20260906)
    for _ in range(40):
        features = grid_features(2, 3)
        w = [[rng.randrange(6) for _ in range(3)] for _ in range(5)]
        mass = [[1+sum(f[j]*w[j][y] for j in range(5)) for y in range(3)] for f in features]
        target = tuple(tuple(F(v, sum(row)) for v in row) for row in mass)
        model = PositiveTable(features, target)
        assert model.exact()[0] == 'primal'
        result = model.closure()
        assert result['in_closure']
        model.approximation(result, F(1, 100))

    def nested(interior):
        p = tuple(F(1, 2) if i == 0 or j == 0 else interior[2*(i-1)+j-1]
                  for i, j in product(range(3), repeat=2))
        return PositiveTable(grid_features(3, 3), tuple((1-v, v) for v in p))

    false_positive = nested((F(1, 4), F(3, 4), F(3, 4), F(1, 4)))
    failed = false_positive.closure()
    assert not failed['in_closure'] and failed['layers']
    assert set((4, 5, 7, 8)) <= set(failed['residual'])
    # The simple exact separating functional is independent of LP pivot choices.
    a = false_positive.equations((4, 5, 7, 8))
    s = tuple(sum(false_positive.totals[x][d] for x in (4, 5, 7, 8)) for d in range(13))
    alpha = (F(4), F(-4), F(-4), F(4))
    assert all(dot(column, alpha) == value for column, value in zip(zip(*a), s))

    approaching = nested((F(1, 2), F(1, 2), F(3, 4), F(1, 4)))
    success = approaching.closure()
    assert success['in_closure'] and approaching.exact()[0] == 'dual'
    approximation = [approaching.approximation(success, F(1, n)) for n in (10, 100, 1000)]
    assert approximation[-1][0] < approximation[0][0]
    # A solver-returned coordinate is never accepted just because it is labeled exact.
    inconsistent = ((F(1), F(1)), (F(1), F(1)))
    status, dual = checked_feasibility(inconsistent, (F(0), F(1)))
    assert status == 'dual' and dot((F(0), F(1)), dual) < 0
    return {
        'status': 'PASS', 'decision_scope': 'known finite rational nonnegative mass atoms with fixed positive base',
        'solver_role': 'float64 LP proposes; exact rational primal/dual checking authorizes only mathematical conclusions',
        'binary_rational_tables': 256,
        'additional_tables_including_probability_zero_and_one': endpoint_tables,
        'comparison_to_independent_interval_theorem': {'exact': exact_yes, 'closure_only': closure_only, 'outside': outside},
        'maximum_layers_on_binary_grid': max_layers,
        'independently_generated_three_label_2x3_models': 40,
        'three_by_three_false_single_pass_certificate': {
            'initial_lp_feasible': bool(failed['layers']), 'actually_in_closure': failed['in_closure'],
            'covered_before_obstruction': failed['covered'], 'unresolved_context_indices': failed['residual'],
            'explicit_interior_dual': [str(v) for v in alpha], 'sharp_supnorm_distance': '1/4'},
        'three_by_three_closure_only_witness': {
            'layers': len(success['layers']), 'covered_by_layer': success['covered'],
            'finite_realization': False, 'epsilon_values': ['1/10', '1/100', '1/1000'],
            'exact_supnorm_errors': [str(e) for e, _ in approximation],
            'verified_error_constant': str(approximation[0][1])},
        'contradictory_linear_equalities_certified_infeasible': True,
        'not_claimed': ['unknown table acquisition', 'bounded coefficient realizability',
                        'general FP polynomial-time compilation', 'Compiler freeze', 'AMP science'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_POSITIVE_CONE_CLOSURE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
