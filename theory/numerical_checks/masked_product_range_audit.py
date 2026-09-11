"""Exact finite-range PRODUCT certificates and guarded triangular loss audit.

Static, known-source arithmetic only. This is not a Reference Compiler gate.
Run from any directory; --write persists only the deterministic minimal audit.
"""
from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random

BASE_COMMIT = "992d7a2328908879d2ed387940b90fee7b487e0a"


def _rational(value, *, positive=False):
    if type(value) not in (int, F) or value < 0 or (positive and value == 0):
        raise ValueError("expected a nonnegative exact rational (positive when required)")
    return F(value)


def _inputs(rows, columns, table, tolerances):
    if type(rows) is not int or type(columns) is not int or min(rows, columns) < 1:
        raise ValueError("positive integer dimensions required")
    if not isinstance(table, dict) or not isinstance(tolerances, dict):
        raise ValueError("coefficient and zero-tolerance dictionaries required")
    q = {}
    for edge, value in table.items():
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError("edge must be a pair")
        i, j = edge
        if type(i) is not int or type(j) is not int or not (0 <= i < rows and 0 <= j < columns):
            raise ValueError("edge outside the external dimensions")
        q[edge] = _rational(value)
    zeros = {edge for edge, value in q.items() if value == 0}
    if set(tolerances) != zeros:
        raise ValueError("exactly one external positive tolerance per visible zero required")
    tau = {edge: _rational(tolerances[edge], positive=True) for edge in sorted(zeros)}
    return dict(sorted(q.items())), tau


def _forest_path(forest, start, end):
    parents, queue = {start: None}, deque([start])
    while queue:
        vertex = queue.popleft()
        if vertex == end:
            path = []
            while parents[vertex] is not None:
                previous, edge = parents[vertex]
                path.append(edge)
                vertex = previous
            return path[::-1]
        for neighbor, edge in forest[vertex]:
            if neighbor not in parents:
                parents[neighbor] = vertex, edge
                queue.append(neighbor)
    raise ValueError("no positive forest path")


def _geometry(rows, columns, q):
    """Only S-active components count. Inactive vertices remain component -1."""
    size = rows + columns
    adjacent, forest = [[] for _ in range(size)], [[] for _ in range(size)]
    for (i, j), value in q.items():
        if value:
            adjacent[i].append((rows+j, (i, j)))
            adjacent[rows+j].append((i, (i, j)))
    component, factor, depth = [-1]*size, [F(0)]*size, [0]*size
    count = 0
    for start in range(size):
        if not adjacent[start] or component[start] != -1:
            continue
        component[start], factor[start] = count, F(1)
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor, edge in adjacent[vertex]:
                if component[neighbor] == -1:
                    component[neighbor] = count
                    factor[neighbor] = q[edge]/factor[vertex]
                    depth[neighbor] = depth[vertex]+1
                    forest[vertex].append((neighbor, edge))
                    forest[neighbor].append((vertex, edge))
                    queue.append(neighbor)
        count += 1
    for (i, j), value in q.items():
        if value and factor[i]*factor[rows+j] != value:
            path = _forest_path(forest, i, rows+j)
            return {"contradiction": {"status": "INFEASIBLE_POSITIVE",
                                     "left": [(i, j), *path[1::2]], "right": path[::2]}}
    a = [max((factor[i] for i in range(rows) if component[i] == c), default=F(0))
         for c in range(count)]
    b = [max((factor[rows+j] for j in range(columns) if component[rows+j] == c), default=F(0))
         for c in range(count)]
    return {"component": component, "factor": factor, "count": count,
            "a": a, "b": b, "depth": max(depth, default=0)}


def _arcs(rows, q, tau, geometry):
    component, factor = geometry["component"], geometry["factor"]
    return [(component[i], component[rows+j], factor[i]*factor[rows+j]/tau[(i, j)], (i, j))
            for (i, j), value in q.items()
            if not value and component[i] != -1 and component[rows+j] != -1]


def solve(rows, columns, table, tolerances):
    """Attained minimum max(u)*max(v), or an exact inconsistency/cycle proof.

    Positive visible coefficients are fixed exactly; each visible zero has
    the supplied upper tolerance. Rational input only; no numerical optimizer.
    """
    q, tau = _inputs(rows, columns, table, tolerances)
    g = _geometry(rows, columns, q)
    if "contradiction" in g:
        return g["contradiction"]
    n = g["count"]
    if n == 0:
        return {"status": "OPTIMAL", "value": F(0), "u": [F(0)]*rows,
                "v": [F(0)]*columns, "path": [], "lower_row": None, "lower_column": None}
    arcs = _arcs(rows, q, tau, g)
    potential, paths = list(g["b"]), [[] for _ in range(n)]
    # Synchronous passes retain paths of at most the pass count in edges.
    for _ in range(n-1):
        updated, new_paths = list(potential), deepcopy(paths)
        for c, d, weight, edge in arcs:
            value = potential[c]*weight
            if value > updated[d]:
                updated[d], new_paths[d] = value, [*paths[c], edge]
        potential, paths = updated, new_paths
    arc_map = {edge: (c, d, weight) for c, d, weight, edge in arcs}
    for c, d, weight, edge in arcs:
        if potential[c]*weight > potential[d]:
            walk = [*paths[c], edge]
            vertices = [arc_map[walk[0]][0]] + [arc_map[e][1] for e in walk]
            for left in range(len(walk)):
                gain = F(1)
                for right in range(left+1, len(walk)+1):
                    gain *= arc_map[walk[right-1]][2]
                    if vertices[left] == vertices[right] and gain > 1:
                        return {"status": "INFEASIBLE_CYCLE", "cycle": walk[left:right]}
            raise RuntimeError("violated Bellman inequality without a profitable cycle")
    component, factor = g["component"], g["factor"]
    u = [factor[i]*potential[component[i]] if component[i] != -1 else F(0) for i in range(rows)]
    v = [factor[rows+j]/potential[component[rows+j]] if component[rows+j] != -1 else F(0)
         for j in range(columns)]
    end = max(range(n), key=lambda c: g["a"][c]*potential[c])
    path = paths[end]
    start = arc_map[path[0]][0] if path else end
    lower_row = next(i for i in range(rows) if component[i] == end and factor[i] == g["a"][end])
    lower_column = next(j for j in range(columns)
                        if component[rows+j] == start and factor[rows+j] == g["b"][start])
    return {"status": "OPTIMAL", "value": max(u)*max(v), "u": u, "v": v,
            "path": path, "lower_row": lower_row, "lower_column": lower_column}


def verify(rows, columns, table, tolerances, certificate):
    """Evidence checking, without solve(), floating tolerances or Python asserts.

    Bounds/mask/values come from the caller, never from certificate metadata.
    Shared geometry is revalidated; the optimizer's paths/potentials are not trusted.
    """
    try:
        q, tau = _inputs(rows, columns, table, tolerances)
        status = certificate["status"]
        if status == "INFEASIBLE_POSITIVE":
            signatures, values = [], []
            for side in ("left", "right"):
                edges = certificate[side]
                if not edges:
                    return False
                signature, value = [0]*(rows+columns), F(1)
                for edge in edges:
                    if edge not in q or q[edge] <= 0:
                        return False
                    i, j = edge
                    signature[i] += 1
                    signature[rows+j] += 1
                    value *= q[edge]
                signatures.append(signature)
                values.append(value)
            return signatures[0] == signatures[1] and values[0] != values[1]
        g = _geometry(rows, columns, q)
        if "contradiction" in g:
            return False
        arcs = {edge: (c, d, weight) for c, d, weight, edge in _arcs(rows, q, tau, g)}
        def checked_walk(edges):
            if not edges or any(edge not in arcs for edge in edges):
                return None
            start, current, gain = arcs[edges[0]][0], arcs[edges[0]][0], F(1)
            for edge in edges:
                c, d, weight = arcs[edge]
                if current != c:
                    return None
                gain *= weight
                current = d
            return start, current, gain
        if status == "INFEASIBLE_CYCLE":
            walk = checked_walk(certificate["cycle"])
            return walk is not None and walk[0] == walk[1] and walk[2] > 1
        if status != "OPTIMAL":
            return False
        u, v = certificate["u"], certificate["v"]
        if len(u) != rows or len(v) != columns:
            return False
        u, v = [_rational(x) for x in u], [_rational(x) for x in v]
        value = _rational(certificate["value"])
        if max(u)*max(v) != value:
            return False
        for (i, j), target in q.items():
            actual = u[i]*v[j]
            if (target and actual != target) or (not target and actual > tau[(i, j)]):
                return False
        if g["count"] == 0:
            return value == 0 and certificate["path"] == [] and certificate["lower_row"] is None and certificate["lower_column"] is None
        i, j = certificate["lower_row"], certificate["lower_column"]
        if type(i) is not int or type(j) is not int or not (0 <= i < rows and 0 <= j < columns):
            return False
        component, factor = g["component"], g["factor"]
        if component[i] == -1 or component[rows+j] == -1:
            return False
        path = certificate["path"]
        if path:
            walk = checked_walk(path)
            if walk is None or walk[:2] != (component[rows+j], component[i]):
                return False
            gain = walk[2]
        else:
            if component[i] != component[rows+j]:
                return False
            gain = F(1)
        # Any valid path is a lower bound; equality with a primal proves optimum.
        return factor[i]*factor[rows+j]*gain == value
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError, OverflowError):
        return False


def independent_floyd(rows, columns, table, tolerances):
    """Independent max-product closure on ORIGINAL row/column vertices.

    Variables are u_i and 1/v_j. This does not contract positive components,
    construct alpha/beta, inspect solver evidence, or run Bellman-Ford.
    None means infeasible. Otherwise the returned Fraction is the optimum.
    """
    q, tau = _inputs(rows, columns, table, tolerances)
    active = sorted({vertex for (i, j), value in q.items() if value for vertex in (i, rows+j)})
    if not active:
        return F(0)
    position = {vertex: index for index, vertex in enumerate(active)}
    size = len(active)
    distance = [[F(int(i == j)) for j in range(size)] for i in range(size)]
    for (i, j), value in q.items():
        if i not in position or rows+j not in position:
            continue
        left, right = position[i], position[rows+j]
        if value:
            distance[right][left] = max(distance[right][left], value)
            distance[left][right] = max(distance[left][right], 1/value)
        else:
            distance[left][right] = max(distance[left][right], 1/tau[(i, j)])
    for middle in range(size):
        for start in range(size):
            for end in range(size):
                distance[start][end] = max(distance[start][end], distance[start][middle]*distance[middle][end])
        if any(distance[i][i] > 1 for i in range(size)):
            return None
    return max(distance[position[rows+j]][position[i]]
               for i in range(rows) for j in range(columns) if i in position and rows+j in position)


def guarded_sources(n):
    contexts = [(i, j) for i in range(n) for j in range(i, n)]
    contexts += [(i, None) for i in range(n)] + [(None, j) for j in range(n)]
    return [(tuple(F(int(i == row)) for i in range(n)),
             tuple(F(int(j == column)) for j in range(n)),
             F(int(row is not None and row == column))) for row, column in contexts]


def grouped_factors(n, k, epsilon):
    if not (type(n) is int and type(k) is int and 1 <= k <= n):
        raise ValueError("require 1 <= k <= n")
    epsilon = _rational(epsilon, positive=True)
    if epsilon > 1:
        raise ValueError("epsilon must be <= 1")
    # Contiguous balanced groups; the theorem does not assume competitors use these.
    sizes = [n//k+int(r < n % k) for r in range(k)]
    factors, start = [], 0
    for size in sizes:
        u, v = [F(0)]*n, [F(0)]*n
        for index in range(size):
            exponent = size-1-index
            u[start+index], v[start+index] = epsilon**exponent, epsilon**(-exponent)
        factors.append((u, v))
        start += size
    return factors


def grouped_mixed_factors(n, k, eta):
    """Pack two disjoint A-times-B groups into each actual mixed PRODUCT.

    eta is the square root of the residual epsilon, so balancing stays rational.
    The same-type cross terms vanish by the declared one-hot source identities.
    """
    if type(n) is not int or type(k) is not int or not (n >= 2 and 1 <= k <= (n+1)//2):
        raise ValueError("require n>=2 and 1<=k<=ceil(n/2)")
    eta = _rational(eta, positive=True)
    if eta > 1:
        raise ValueError("eta must be <=1")
    groups = grouped_factors(n, min(2*k, n), eta*eta)
    balanced = []
    for u, v in groups:
        size = sum(value > 0 for value in u)
        scale = eta**(size-1)
        balanced.append(([value/scale for value in u], [value*scale for value in v]))
    if len(balanced) % 2:
        balanced.append(([F(0)]*n, [F(0)]*n))
    return [(balanced[r][0]+balanced[r+1][1], balanced[r+1][0]+balanced[r][1])
            for r in range(0, len(balanced), 2)]


def _dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def log_bounds(x, terms=24):
    """Rational outward enclosure of log(x), x>=1, by the atanh series."""
    x = _rational(x, positive=True)
    if x < 1 or type(terms) is not int or terms < 1:
        raise ValueError("x>=1 and positive integer term count required")
    z = (x-1)/(x+1)
    low = 2*sum((z**(2*j+1)/(2*j+1) for j in range(terms)), F(0))
    remainder = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return low, low+remainder


def _triangle_audit():
    count, logarithm_checks, exponent_examples = 0, 0, []
    for n in range(2, 11):
        sources = guarded_sources(n)
        assert len(sources) == n*(n+5)//2
        for k in range(1, n+1):
            m = (n+k-1)//k
            for epsilon in (F(1, 2), F(1, 4), F(1, 16), F(1, 64)):
                factors = grouped_factors(n, k, epsilon)
                cap = max(max(u)*max(v) for u, v in factors)
                assert cap == epsilon**(-(m-1))
                error, low_sum, high_sum = F(0), F(0), F(0)
                for a, b, target in sources:
                    h = sum((_dot(u, a)*_dot(v, b) for u, v in factors), F(0))
                    assert 0 <= h <= 1
                    error = max(error, abs(h-target))
                    if target:
                        assert h == 1
                    elif h:
                        lo, hi = log_bounds(1+h*h/(4*(1+h)))
                        low_sum += lo/2
                        high_sum += hi/2
                        assert hi/2 <= h*h/8
                        logarithm_checks += 1
                if k < n:
                    assert error == epsilon
                    assert cap*error**(m-1) == 1
                    if error <= F(1, 6):
                        assert cap*error**(m-1)*(2*k)**m >= 1
                    assert low_sum/len(sources) >= 2*error*error/(81*len(sources))
                    assert high_sum/len(sources) <= epsilon*epsilon/8
                else:
                    assert error == low_sum == high_sum == 0 and cap == 1
                count += 1
            if n == 8 and k in (1, 2, 3, 4, 8):
                exponent_examples.append({"n": n, "products": k, "longest_group_path": m-1,
                                          "loss_power_of_K": str(F(-2, m-1)) if m > 1 else "exact at K=1"})
    # Scope attacks: no guards permits a SUM shortcut; mixed parents defeat n count.
    for a, b, target in guarded_sources(2)[:3]:
        assert a[1]+b[0] == target
    for a, b, target in guarded_sources(2):
        assert (a[0]+b[1])*(b[0]+a[1]) == target
    return count, logarithm_checks, exponent_examples


def _mixed_audit():
    count, examples = 0, []
    for n in range(2, 13):
        sources = guarded_sources(n)
        for k in range(1, (n+1)//2+1):
            m = (n+2*k-1)//(2*k)
            for eta in (F(1, 2), F(1, 4), F(1, 8)):
                epsilon = eta*eta
                factors = grouped_mixed_factors(n, k, eta)
                assert len(factors) == k
                K = max(max(left)*max(right) for left, right in factors)
                assert K == epsilon**(-(m-1))
                error, low_sum, high_sum = F(0), F(0), F(0)
                for a, b, target in sources:
                    h = sum((_dot(left, a+b)*_dot(right, a+b) for left, right in factors), F(0))
                    assert 0 <= h <= 1
                    error = max(error, abs(h-target))
                    if target:
                        assert h == 1
                    elif h:
                        lo, hi = log_bounds(1+h*h/(4*(1+h)))
                        low_sum += lo/2
                        high_sum += hi/2
                if 2*k < n:
                    assert error == epsilon and K*error**(m-1) == 1
                    if error <= F(1, 6):
                        assert K*error**(m-1)*(4*k)**m >= 1
                    assert low_sum/len(sources) >= 2*error*error/(81*len(sources))
                    assert high_sum/len(sources) <= epsilon*epsilon/8
                else:
                    assert error == low_sum == high_sum == 0 and K == 1
                count += 1
            if n == 12 and k in (1, 2, 3, 6):
                examples.append({"n": n, "actual_mixed_PRODUCTs": k,
                                 "longest_group_path": m-1,
                                 "loss_power_of_K": str(F(-2, m-1)) if m > 1 else "exact at K=1"})
    # Exhaustively check the general mixed-parent expansion, including same-source
    # squares, which must be charged to the additive guard remainder.
    expansions = 0
    for coefficients in product((F(0), F(1)), repeat=8):
        left, right = coefficients[:4], coefficients[4:]
        u, s, t, v = left[:2], left[2:], right[:2], right[2:]
        for a, b, _ in guarded_sources(2):
            original = _dot(left, a+b)*_dot(right, a+b)
            additive = sum((u[i]*t[i]*a[i]+s[i]*v[i]*b[i] for i in range(2)), F(0))
            cross = sum(((u[i]*v[j]+t[i]*s[j])*a[i]*b[j] for i in range(2) for j in range(2)), F(0))
            assert original == additive+cross
            expansions += 1
    return count, expansions, examples


def audit():
    if not __debug__:
        raise RuntimeError("Run the audit without -O; verify() itself never relies on asserts")
    totals = {"OPTIMAL": 0, "INFEASIBLE_POSITIVE": 0, "INFEASIBLE_CYCLE": 0}
    cases = 0
    def check(rows, columns, q, tau):
        nonlocal cases
        certificate = solve(rows, columns, q, tau)
        assert verify(rows, columns, q, tau, certificate)
        expected = independent_floyd(rows, columns, q, tau)
        assert (expected is None) == (certificate["status"] != "OPTIMAL")
        if expected is not None:
            assert certificate["value"] == expected
        totals[certificate["status"]] += 1
        cases += 1
        return certificate
    for rows, columns, tolerances in ((2, 2, (F(1, 2), F(1), F(2))),
                                      (2, 3, (F(1, 2), F(2)))):
        edges = list(product(range(rows), range(columns)))
        for values in product((-1, 0, 1, 2), repeat=len(edges)):
            q = {edge: F(value) for edge, value in zip(edges, values) if value >= 0}
            for tolerance in tolerances:
                check(rows, columns, q, {edge: tolerance for edge, value in q.items() if not value})
    random = Random(20260911)
    for _ in range(400):
        q, tau = {}, {}
        for edge in product(range(3), repeat=2):
            choice = random.randrange(4)
            if choice:
                q[edge] = F(0) if choice == 1 else F(random.randrange(1, 8), random.randrange(1, 6))
                if not q[edge]:
                    tau[edge] = F(random.randrange(1, 8), random.randrange(1, 6))
        check(3, 3, q, tau)
    # A graph with inactive endpoints has fake height two in the old full graph,
    # but neither inactive edge incurs a range cost: exact zero factors suffice.
    inactive_q = {(0, 0): F(1), (1, 0): F(0), (0, 1): F(0)}
    inactive = check(2, 2, inactive_q, {(1, 0): F(1, 1000), (0, 1): F(1, 1000)})
    assert inactive["value"] == 1
    diagonal = {(0, 0): F(1), (1, 1): F(1), (0, 1): F(0), (1, 0): F(0)}
    unit_cycle = check(2, 2, diagonal, {(0, 1): F(2), (1, 0): F(1, 2)})
    assert unit_cycle["value"] == 2  # Gain exactly one is feasible, no epsilon tie.
    bad_cycle = check(2, 2, diagonal, {(0, 1): F(1, 2), (1, 0): F(1, 2)})
    path_q = {(0, 0): F(2), (1, 1): F(3), (0, 1): F(0)}
    path_tau = {(0, 1): F(1, 8)}
    path = check(2, 2, path_q, path_tau)
    assert path["value"] == 48
    positive_q = {(0, 0): F(1), (0, 1): F(1), (1, 0): F(1), (1, 1): F(2)}
    positive_bad = check(2, 2, positive_q, {})
    selfloop_q = {(0, 0): F(1), (0, 1): F(1), (1, 0): F(1), (1, 1): F(0)}
    assert check(2, 2, selfloop_q, {(1, 1): F(1)})["status"] == "OPTIMAL"
    assert check(2, 2, selfloop_q, {(1, 1): F(1, 2)})["status"] == "INFEASIBLE_CYCLE"

    forgeries = []
    def forge(original, key, value, q=path_q, tau=path_tau):
        cert = deepcopy(original)
        cert[key] = value
        forgeries.append((2, 2, q, tau, cert))
    forge(path, "value", F(47))
    forge(path, "u", [F(1), F(1)])
    forge(path, "path", [])
    forge(path, "path", [(1, 0)])
    forge(path, "lower_row", True)
    forge(path, "lower_column", 1)
    forge(path, "status", "INFEASIBLE_CYCLE")
    forge(path, "v", [float("nan"), F(1)])
    forge(bad_cycle, "cycle", [(0, 1)], diagonal, {(0, 1): F(1, 2), (1, 0): F(1, 2)})
    forge(positive_bad, "left", [], positive_q, {})
    forgeries.append((2, 2, path_q, {(0, 1): F(1, 16)}, path))  # Changed external requirement.
    forgeries.append((2, 2, diagonal, {(0, 1): F(1, 8), (1, 0): F(1, 8)}, path))  # Mask replay.
    forgeries.append((2, 3, path_q, path_tau, path))
    forgeries.append((2, 2, path_q, {}, path))
    forgeries.append((2, 2, path_q, {(0, 1): 0.125}, path))
    assert all(not verify(*item) for item in forgeries)
    invalid_inputs = [(True, 2, {}, {}), (2, 2, {(True, 0): 1}, {}),
                      (2, 2, {(0, 0): -1}, {}), (2, 2, {(0, 0): float("inf")}, {}),
                      (2, 2, {(0, 0): 0}, {(0, 0): 0})]
    for invalid in invalid_inputs:
        try:
            solve(*invalid)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("invalid exact input accepted")
    triangle_count, log_count, examples = _triangle_audit()
    mixed_count, mixed_expansions, mixed_examples = _mixed_audit()
    # Direct rational path identities survive small positive-edge perturbations.
    robust_checks = 0
    for n in range(2, 9):
        for epsilon in (F(1, 16), F(1, 64)):
            u = [(1-epsilon)*epsilon**(n-1-i) for i in range(n)]
            v = [epsilon**(-(n-1-i)) for i in range(n)]
            K = max(u)*max(v)
            assert all(u[i]*v[i] == 1-epsilon for i in range(n))
            assert all(u[i]*v[j] <= epsilon for i in range(n) for j in range(i+1, n))
            assert K*epsilon**(n-1) >= (1-epsilon)**n
            robust_checks += 1
    return {"status": "PASS", "base_commit": BASE_COMMIT,
            "scope": "static known visible coefficients; guarded parallel PRODUCT classes, including arbitrary mixed SUM parents and fixed readout",
            "arithmetic": "fractions.Fraction; rational outward log series; no floating optimizer",
            "independent_original_vertex_floyd_cases": cases,
            "classifications": totals,
            "exhaustive_2_by_2_cases": 4**4*3, "exhaustive_2_by_3_cases": 4**6*2,
            "seeded_rational_3_by_3_cases": 400, "seed": 20260911,
            "inactive_vertices_do_not_raise_exponent": True,
            "unit_gain_cycles_and_selfloops_checked": True,
            "forged_or_replayed_certificates_rejected": len(forgeries),
            "invalid_exact_inputs_rejected": len(invalid_inputs),
            "guarded_triangular_constructions": triangle_count,
            "rational_log_enclosures_checked": log_count,
            "positive_edge_perturbation_checks": robust_checks,
            "mixed_parent_native_constructions": mixed_count,
            "mixed_parent_expansion_checks": mixed_expansions,
            "mixed_parent_sharp_count_range_exponents": mixed_examples,
            "sharp_count_range_exponent_examples": examples,
            "scope_counterexamples": ["without guards a two-index target is SUM-only",
                                       "the oriented n-PRODUCT bound fails with mixed parents; the proved mixed bound is ceil(n/2)"],
            "not_claimed": ["unrestricted or nested FP DAG PRODUCT-count lower bound",
                            "efficient search over all alternative mass or conditional lifts",
                            "complete hardware budget, reachable value, Runtime freeze, fresh persistence or AMP bridge"],
            "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = json.dumps(audit(), indent=2)+"\n"
    if args.write:
        root = Path(__file__).resolve().parents[2]
        destination = root/"evidence/minimal/FP_MASKED_PRODUCT_RANGE_AUDIT.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    print(text, end="")
