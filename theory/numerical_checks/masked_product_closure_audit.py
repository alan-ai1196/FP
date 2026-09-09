"""Exact visible-factor and closure certificates; independent small-cycle audit."""
from collections import deque
from copy import deepcopy
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import argparse
import json


def path_edges(forest, start, end):
    queue, parents = deque([start]), {start: None}
    while queue:
        vertex = queue.popleft()
        if vertex == end:
            result = []
            while parents[vertex] is not None:
                previous, edge = parents[vertex]
                result.append(edge)
                vertex = previous
            return result[::-1]
        for neighbor, edge in forest[vertex]:
            if neighbor not in parents:
                parents[neighbor] = vertex, edge
                queue.append(neighbor)
    raise AssertionError('positive path missing')


def classify(rows, columns, table):
    assert type(rows) is int and type(columns) is int and rows > 0 and columns > 0
    assert all(0 <= i < rows and 0 <= j < columns and type(q) in (int, F) and q >= 0
               for (i, j), q in table.items())
    table = {edge: F(q) for edge, q in table.items()}
    size = rows+columns
    adjacent, forest = [[] for _ in range(size)], [[] for _ in range(size)]
    active = set()
    for (i, j), q in table.items():
        if q:
            left, right = i, rows+j
            adjacent[left].append((right, (i, j)))
            adjacent[right].append((left, (i, j)))
            active.update((left, right))
    component, factor = [-1]*size, [F(1)]*size
    count = 0
    for start in range(size):
        if component[start] != -1:
            continue
        component[start] = count
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor, edge in adjacent[vertex]:
                if component[neighbor] == -1:
                    component[neighbor] = count
                    factor[neighbor] = table[edge]/factor[vertex]
                    forest[vertex].append((neighbor, edge))
                    forest[neighbor].append((vertex, edge))
                    queue.append(neighbor)
        count += 1
    for (i, j), q in table.items():
        if q and factor[i]*factor[rows+j] != q:
            path = path_edges(forest, i, rows+j)
            return {'status': 'OUTSIDE_CLOSURE', 'left': [(i, j), *path[1::2]], 'right': path[::2]}
    zero_active = next((edge for edge, q in table.items()
                        if not q and edge[0] in active and rows+edge[1] in active), None)
    if zero_active is None:
        return {'status': 'EXACT_FACTORIZATION',
                'row_factors': tuple(factor[i] if i in active else F(0) for i in range(rows)),
                'column_factors': tuple(factor[rows+j] if rows+j in active else F(0) for j in range(columns))}

    arcs = [[] for _ in range(count)]
    for (i, j), q in table.items():
        if not q:
            arcs[component[i]].append((component[rows+j], (i, j)))
    color, stack, stack_edges = [0]*count, [], []
    cycle = None
    def visit(vertex):
        nonlocal cycle
        color[vertex] = 1
        stack.append(vertex)
        for neighbor, edge in arcs[vertex]:
            if color[neighbor] == 1:
                index = stack.index(neighbor)
                cycle = stack_edges[index:]+[edge]
                return True
            if color[neighbor] == 0:
                stack_edges.append(edge)
                if visit(neighbor):
                    return True
                stack_edges.pop()
        stack.pop()
        color[vertex] = 2
        return False
    for vertex in range(count):
        if color[vertex] == 0 and visit(vertex):
            break
    if cycle is not None:
        left, right = list(cycle), []
        for k, outgoing in enumerate(cycle):
            incoming = cycle[k-1]
            path = path_edges(forest, outgoing[0], rows+incoming[1])
            left.extend(path[1::2])
            right.extend(path[::2])
        return {'status': 'OUTSIDE_CLOSURE', 'left': left, 'right': right}
    height = [None]*count
    def depth(vertex):
        if height[vertex] is None:
            height[vertex] = max((1+depth(neighbor) for neighbor, _ in arcs[vertex]), default=0)
        return height[vertex]
    for vertex in range(count):
        depth(vertex)
    return {'status': 'LIMIT_ONLY', 'row_factors': tuple(factor[:rows]),
            'column_factors': tuple(factor[rows:]),
            'row_exponents': tuple(height[component[i]] for i in range(rows)),
            'column_exponents': tuple(-height[component[rows+j]] for j in range(columns)),
            'active_zero_edge': zero_active}


def verify(rows, columns, table, certificate):
    """Check the evidence against external dimensions/mask/values, not the flag."""
    try:
        assert type(rows) is int and type(columns) is int and rows > 0 and columns > 0
        assert all(type(i) is int and type(j) is int and 0 <= i < rows and 0 <= j < columns
                   and type(q) in (int, F) and q >= 0 for (i, j), q in table.items())
        status = certificate['status']
        if status == 'OUTSIDE_CLOSURE':
            incidences, values = [], []
            for side in ('left', 'right'):
                incidence, value = [0]*(rows+columns), F(1)
                assert certificate[side]
                for edge in certificate[side]:
                    assert edge in table
                    i, j = edge
                    incidence[i] += 1
                    incidence[rows+j] += 1
                    value *= table[edge]
                incidences.append(incidence)
                values.append(value)
            return incidences[0] == incidences[1] and values[0] != values[1]
        u, v = certificate['row_factors'], certificate['column_factors']
        assert len(u) == rows and len(v) == columns
        assert all(type(a) in (int, F) and a >= 0 for a in (*u, *v))
        if status == 'EXACT_FACTORIZATION':
            return all(u[i]*v[j] == q for (i, j), q in table.items())
        assert status == 'LIMIT_ONLY' and min((*u, *v)) > 0
        a, b = certificate['row_exponents'], certificate['column_exponents']
        assert len(a) == rows and len(b) == columns and all(type(e) is int for e in (*a, *b))
        for (i, j), q in table.items():
            assert (u[i]*v[j] == q and a[i]+b[j] == 0) if q else a[i]+b[j] >= 1
        i, j = certificate['active_zero_edge']
        assert table[(i, j)] == 0
        assert any(r == i and q > 0 for (r, _), q in table.items())
        assert any(c == j and q > 0 for (_, c), q in table.items())
        return True
    except (AssertionError, KeyError, IndexError, TypeError, ValueError):
        return False


def simple_cycles(rows, columns):
    """Independent binomial checks, with no support contraction or factor BFS."""
    result = set()
    for length in range(2, min(rows, columns)+1):
        for r in permutations(range(rows), length):
            if r[0] != min(r):
                continue
            for c in permutations(range(columns), length):
                first = tuple(sorted((r[i], c[i]) for i in range(length)))
                second = tuple(sorted((r[(i+1)%length], c[i]) for i in range(length)))
                result.add(tuple(sorted((first, second))))
    return tuple(result)


def cycle_test(table, cycles):
    for left, right in cycles:
        if all(edge in table for edge in (*left, *right)):
            a = b = F(1)
            for edge in left:
                a *= table[edge]
            for edge in right:
                b *= table[edge]
            if a != b:
                return False
    return True


def is_biclique_union(rows, columns, table):
    adjacency = [set() for _ in range(rows+columns)]
    for i, j in table:
        adjacency[i].add(rows+j)
        adjacency[rows+j].add(i)
    unseen = set(range(rows+columns))
    while unseen:
        start = min(unseen)
        component, pending = set(), [start]
        while pending:
            v = pending.pop()
            if v not in component:
                component.add(v)
                pending.extend(adjacency[v]-component)
        unseen -= component
        r = [v for v in component if v < rows]
        c = [v-rows for v in component if v >= rows]
        if any((i, j) not in table for i in r for j in c):
            return False
    return True


def audit():
    totals = {'EXACT_FACTORIZATION': 0, 'LIMIT_ONLY': 0, 'OUTSIDE_CLOSURE': 0}
    closed_masks, mask_tables = {}, {}
    for rows, columns, alphabet in ((2, 3, (-1, 0, 1, 2)), (3, 3, (-1, 0, 1))):
        edges = tuple(product(range(rows), range(columns)))
        cycles = simple_cycles(rows, columns)
        for entries in product(alphabet, repeat=len(edges)):
            table = {edge: F(value) for edge, value in zip(edges, entries) if value >= 0}
            cert = classify(rows, columns, table)
            assert verify(rows, columns, table, cert)
            assert (cert['status'] != 'OUTSIDE_CLOSURE') == cycle_test(table, cycles)
            totals[cert['status']] += 1
            if rows == columns == 3:
                mask = sum(1 << i for i, edge in enumerate(edges) if edge in table)
                closed_masks.setdefault(mask, True)
                closed_masks[mask] &= cert['status'] != 'LIMIT_ONLY'
                mask_tables[mask] = table
    assert len(closed_masks) == 512
    assert all(value == is_biclique_union(3, 3, mask_tables[mask]) for mask, value in closed_masks.items())

    path = {(0, 0): F(1), (1, 0): F(0), (1, 1): F(1)}
    limit = classify(2, 2, path)
    assert limit['status'] == 'LIMIT_ONLY'
    square = {(0, 0): F(1), (0, 1): F(0), (1, 0): F(0), (1, 1): F(1)}
    bad_cycle = classify(2, 2, square)
    assert bad_cycle['status'] == 'OUTSIDE_CLOSURE'
    weighted = dict(square)
    weighted[(0, 1)], weighted[(1, 0)], weighted[(1, 1)] = F(1), F(1), F(2)
    assert classify(2, 2, weighted)['status'] == 'OUTSIDE_CLOSURE'
    for epsilon in (F(1, 2), F(1, 8), F(1, 64)):
        u = [factor*epsilon**e for factor, e in zip(limit['row_factors'], limit['row_exponents'])]
        v = [factor*epsilon**e for factor, e in zip(limit['column_factors'], limit['column_exponents'])]
        assert u[0]*v[0] == u[1]*v[1] == 1 and u[1]*v[0] == epsilon
        assert u[0]*v[1] == 1/epsilon  # Invisible product diverges.
        for x, z, w in product((0, 1), repeat=3):
            h = (u[0]*(1-x)+u[1]*(1-w))*(v[0]*(1-z)+v[1]*x)
            selector = (1-x)*(1-z)+x*(1-w)
            assert h == selector+epsilon*(1-w)*(1-z)
            excess = h/(1+epsilon)
            assert 2+excess <= 3
            assert abs((1+excess)/(2+excess)-F(1+selector, 2+selector)) <= epsilon/9
        for x, z in product((0, 1), repeat=2):
            assert (1-x)*(1-z)+x*(1-z) == 1-z  # Different observable lift, exact SUM.

    forgeries = []
    forged = deepcopy(limit)
    forged['row_exponents'] = (0, 0)
    forgeries.append((path, forged))
    forged = deepcopy(limit)
    forged['status'] = 'EXACT_FACTORIZATION'
    forgeries.append((path, forged))
    forged = deepcopy(limit)
    forged['row_factors'] = (F(2), F(1))
    forgeries.append((path, forged))
    forged = deepcopy(bad_cycle)
    forged['left'] = forged['left'][:-1]
    forgeries.append((square, forged))
    forged = classify(2, 2, {(0, 0): F(1), (1, 1): F(1)})
    forgeries.append((path, forged))  # Certificate cannot delete an external zero edge.
    assert all(not verify(2, 2, table, cert) for table, cert in forgeries)
    return {'status': 'PASS', 'scope': 'given rational visible coefficient table of one PRODUCT of two positive SUMs',
            'complete_2_by_3_weighted_grid_cases': 4**6,
            'complete_3_by_3_binary_support_grid_cases': 3**9,
            'classifications': totals,
            'independent_all_simple_cycle_checks': True,
            'all_3_by_3_visibility_masks_checked': len(closed_masks),
            'closed_masks': sum(closed_masks.values()),
            'closed_iff_disjoint_bicliques_verified': True,
            'induced_path_limit_row_exponents': limit['row_exponents'],
            'induced_path_limit_column_exponents': limit['column_exponents'],
            'rational_epsilon_families_checked': 3,
            'forged_certificates_rejected': len(forgeries),
            'observable_projection_can_remove_coefficient_obstruction': True,
            'not_claimed': ['given-coefficient rejection rejects every mass lift',
                            'efficient complete implementation of the existential mass/probability solver',
                            'free zero-product knowledge from a sample', 'registered construction/install or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_MASKED_PRODUCT_CLOSURE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
