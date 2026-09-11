"""Exact finite-budget PRODUCT certificates and guarded triangular loss audit.

Standalone theorem audit, not a ReferenceCompilerRuntime authority. No floats
are accepted as proof inputs. Run from any directory; --write saves minimal JSON.
"""
from collections import deque
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import random


def _fraction(value, positive=False):
    if type(value) not in (int, F) or value < 0 or (positive and value == 0):
        raise ValueError('expected an exact nonnegative rational (positive when required)')
    return F(value)


def _calibrate(rows, columns, table, tolerances):
    if type(rows) is not int or type(columns) is not int or min(rows, columns) < 1:
        raise ValueError('positive integer dimensions required')
    q = {}
    for edge, value in table.items():
        if (type(edge) is not tuple or len(edge) != 2 or
                any(type(v) is not int for v in edge) or
                not (0 <= edge[0] < rows and 0 <= edge[1] < columns)):
            raise ValueError('invalid visible edge')
        q[edge] = _fraction(value)
    zeros = {edge for edge, value in q.items() if value == 0}
    if set(tolerances) != zeros:
        raise ValueError('supply a positive tolerance for every and only visible zero')
    eps = {edge: _fraction(value, positive=True) for edge, value in tolerances.items()}
    adjacency = [[] for _ in range(rows+columns)]
    for (i, j), value in sorted(q.items()):
        if value:
            adjacency[i].append((rows+j, value))
            adjacency[rows+j].append((i, value))
    component, factors = [-1]*(rows+columns), [F(0)]*(rows+columns)
    count = 0
    for root in range(rows+columns):
        if not adjacency[root] or component[root] >= 0:
            continue
        component[root], factors[root] = count, F(1)
        queue = deque([root])
        while queue:
            node = queue.popleft()
            for neighbor, value in adjacency[node]:
                proposed = value/factors[node]
                if component[neighbor] < 0:
                    component[neighbor], factors[neighbor] = count, proposed
                    queue.append(neighbor)
                elif factors[neighbor] != proposed:
                    raise ValueError('positive-edge factors are inconsistent')
        count += 1
    a, b = factors[:rows], factors[rows:]
    row_max = [max(a[i] for i in range(rows) if component[i] == c) for c in range(count)]
    col_max = [max(b[j] for j in range(columns) if component[rows+j] == c) for c in range(count)]
    arcs = []
    for (i, j), tolerance in sorted(eps.items()):
        c, d = component[i], component[rows+j]
        if c >= 0 and d >= 0:
            arcs.append((c, d, i, j, a[i]*b[j]/tolerance))
    return q, eps, component, a, b, row_max, col_max, arcs


def solve_budget(rows, columns, table, tolerances):
    """Minimize max(u)*max(v), fitting positive entries exactly and zeros from above.

    The positive subtable must be multiplicatively consistent. Invalid inputs,
    including inconsistent positives, raise ValueError. Returned certificates
    concern only this fixed coefficient problem, never all observable lifts.
    """
    q, eps, comp, a, b, aa, bb, arcs = _calibrate(rows, columns, table, tolerances)
    n = len(aa)
    if not n:
        return {'status': 'OPTIMAL', 'budget': F(0), 'row_factors': [F(0)]*rows,
                'column_factors': [F(0)]*columns, 'start': None, 'path': []}
    potential, starts, paths = bb[:], list(range(n)), [() for _ in range(n)]
    for _ in range(n-1):
        new, new_starts, new_paths = potential[:], starts[:], paths[:]
        for index, (c, d, _, _, weight) in enumerate(arcs):
            proposal = potential[c]*weight
            if proposal > new[d]:
                new[d], new_starts[d], new_paths[d] = proposal, starts[c], paths[c]+(index,)
        potential, starts, paths = new, new_starts, new_paths
    for index, (c, d, _, _, weight) in enumerate(arcs):
        if potential[c]*weight <= potential[d]:
            continue
        walk = paths[c]+(index,)
        vertices = [starts[c]]+[arcs[e][1] for e in walk]
        for left in range(len(walk)):
            ratio = F(1)
            for right in range(left+1, len(walk)+1):
                ratio *= arcs[walk[right-1]][4]
                if vertices[left] == vertices[right] and ratio > 1:
                    return {'status': 'INFEASIBLE',
                            'cycle': [(arcs[e][2], arcs[e][3]) for e in walk[left:right]]}
        raise AssertionError('violated relaxation without a positive multiplicative cycle')
    end = max(range(n), key=lambda c: aa[c]*potential[c])
    u = [a[i]*potential[comp[i]] if comp[i] >= 0 else F(0) for i in range(rows)]
    v = [b[j]/potential[comp[rows+j]] if comp[rows+j] >= 0 else F(0) for j in range(columns)]
    return {'status': 'OPTIMAL', 'budget': aa[end]*potential[end],
            'row_factors': u, 'column_factors': v, 'start': starts[end],
            'path': [(arcs[e][2], arcs[e][3]) for e in paths[end]]}


def verify_budget(rows, columns, table, tolerances, certificate):
    """Verify explicit factors and a path lower bound, or a closed-walk contradiction.

    Does not invoke the optimizer, trust its optimum flag, or silently remove
    external zero constraints. Rational input calibration is deterministic.
    """
    try:
        q, eps, comp, a, b, aa, bb, arcs = _calibrate(rows, columns, table, tolerances)
        by_edge = {(i, j): (c, d, weight) for c, d, i, j, weight in arcs}
        status = certificate['status']
        if status == 'INFEASIBLE':
            cycle = certificate['cycle']
            if not cycle:
                return False
            start = by_edge[tuple(cycle[0])][0]
            current, ratio = start, F(1)
            for edge in cycle:
                c, d, weight = by_edge[tuple(edge)]
                if c != current:
                    return False
                current, ratio = d, ratio*weight
            return current == start and ratio > 1
        if status != 'OPTIMAL':
            return False
        k = _fraction(certificate['budget'])
        u, v = certificate['row_factors'], certificate['column_factors']
        if len(u) != rows or len(v) != columns:
            return False
        u, v = [_fraction(x) for x in u], [_fraction(x) for x in v]
        if max(u)*max(v) != k:
            return False
        for (i, j), value in q.items():
            if (u[i]*v[j] != value) if value else (u[i]*v[j] > eps[(i, j)]):
                return False
        if not aa:
            return k == 0 and certificate['start'] is None and certificate['path'] == []
        start = certificate['start']
        if type(start) is not int or not 0 <= start < len(aa):
            return False
        current, lower = start, bb[start]
        for edge in certificate['path']:
            c, d, weight = by_edge[tuple(edge)]
            if c != current:
                return False
            current, lower = d, lower*weight
        return lower*aa[current] == k
    except (ValueError, KeyError, IndexError, TypeError, AttributeError, ZeroDivisionError):
        return False


def exhaustive_path_oracle(rows, columns, table, tolerances):
    """Independent optimization by enumerating simple paths and simple cycles."""
    _, _, _, _, _, aa, bb, arcs = _calibrate(rows, columns, table, tolerances)
    adjacency = [[] for _ in aa]
    for c, d, _, _, weight in arcs:
        adjacency[c].append((d, weight))
    optimum = max((x*y for x, y in zip(aa, bb)), default=F(0))
    feasible = True
    for start in range(len(aa)):
        def visit(current, visited, ratio):
            nonlocal optimum, feasible
            optimum = max(optimum, bb[start]*aa[current]*ratio)
            for neighbor, weight in adjacency[current]:
                if neighbor == start and ratio*weight > 1:
                    feasible = False
                if neighbor not in visited:
                    visit(neighbor, visited | {neighbor}, ratio*weight)
        visit(start, {start}, F(1))
    return optimum if feasible else None


def guarded_contexts(n):
    # None denotes a guard at which only one parent family is nonzero.
    return [(i, j) for i in range(n) for j in range(i, n)]+[(i, None) for i in range(n)]+[(None, j) for j in range(n)]


def balanced_factors(n, k, epsilon):
    if not (type(n) is int and type(k) is int and 1 <= k <= n):
        raise ValueError('require 1 <= k <= n')
    epsilon = _fraction(epsilon, positive=True)
    if epsilon > 1:
        raise ValueError('epsilon must not exceed one')
    sizes = [n//k+(r < n % k) for r in range(k)]
    factors, start = [], 0
    for size in sizes:
        u, v = [F(0)]*n, [F(0)]*n
        for rank, i in enumerate(range(start, start+size)):
            u[i], v[i] = epsilon**(size-1-rank), epsilon**(-(size-1-rank))
        factors.append((u, v))
        start += size
    return factors


def mass_table(n, factors, additive_rows=None, additive_columns=None, constant=F(0)):
    additive_rows = additive_rows if additive_rows is not None else [F(0)]*n
    additive_columns = additive_columns if additive_columns is not None else [F(0)]*n
    out = []
    for i, j in guarded_contexts(n):
        value = constant+(additive_rows[i] if i is not None else F(0))+(additive_columns[j] if j is not None else F(0))
        if i is not None and j is not None:
            value += sum((u[i]*v[j] for u, v in factors), F(0))
        out.append(value)
    return out


@lru_cache(maxsize=None)
def log_interval(z, terms=18):
    """Exact atanh-series enclosure; this audit only needs 1 <= z <= 32/27."""
    z = _fraction(z, positive=True)
    if not 1 <= z <= F(32, 27):
        raise ValueError('log input outside audited interval')
    t = (z-1)/(z+1)
    lower = 2*sum((t**(2*j+1)/F(2*j+1) for j in range(terms)), F(0))
    remainder = 2*t**(2*terms+1)/(F(2*terms+1)*(1-t*t))
    return lower, lower+remainder


def constructed_loss_interval(n, h):
    lo = hi = F(0)
    contexts = guarded_contexts(n)
    for (i, j), value in zip(contexts, h):
        if i is not None and i == j:
            if value != 1:
                raise ValueError('construction must match diagonal exactly')
            continue
        # KL(1/2 || (1+h)/(2+h)) = log((2+h)^2/(4(1+h)))/2.
        a, b = log_interval((2+value)**2/(4*(1+value)))
        lo, hi = lo+a/2, hi+b/2
    return lo/len(contexts), hi/len(contexts)


def arbitrary_loss_interval(n, h):
    """Exact KL intervals for arbitrary h in [0,1], including inexact diagonals."""
    lo = hi = F(0)
    contexts = guarded_contexts(n)
    if len(h) != len(contexts) or not all(0 <= value <= 1 for value in h):
        raise ValueError('invalid capped mass table')
    for (i, j), value in zip(contexts, h):
        if i is not None and i == j:
            argument, divisor = F(4, 27)*(2+value)**3/(1+value)**2, 3
        else:
            argument, divisor = (2+value)**2/(4*(1+value)), 2
        a, b = log_interval(argument)
        lo, hi = lo+a/divisor, hi+b/divisor
    return lo/len(contexts), hi/len(contexts)


def perturbed_class_audit():
    """Check the all-class inequality away from exact diagonals and zero SUMs."""
    rng = random.Random(20260911)
    informative = 0
    for _ in range(96):
        n = rng.randrange(2, 9)
        k = rng.randrange(1, n)
        m = (n+k-1)//k
        epsilon = F(1, 2**rng.randrange(4, 8))
        delta = epsilon/F(100*n)
        factors = balanced_factors(n, k, epsilon)
        perturbed = []
        for u, v in factors:
            umax, vmax = max(u), max(v)
            u = [x*(1+delta*rng.randrange(4)) if x else delta*rng.randrange(4)/vmax for x in u]
            v = [x*(1+delta*rng.randrange(4)) if x else delta*rng.randrange(4)/umax for x in v]
            perturbed.append((u, v))
        r = [delta*rng.randrange(4) for _ in range(n)]
        s = [delta*rng.randrange(4) for _ in range(n)]
        c = delta*rng.randrange(4)
        h = mass_table(n, perturbed, r, s, c)
        contraction = min(F(1), 1/max(h))
        factors = [([x*contraction for x in u], v) for u, v in perturbed]
        r, s, c = [x*contraction for x in r], [x*contraction for x in s], c*contraction
        h = mass_table(n, factors, r, s, c)
        contexts = guarded_contexts(n)
        error = max(abs(value-(i is not None and i == j)) for (i, j), value in zip(contexts, h))
        budget = max(max(u)*max(v) for u, v in factors)
        assert error < F(1, 6)
        informative += 1
        # Guards bound the full nonnegative SUM background, including constants.
        assert all(c+r[i]+s[i] <= 2*error for i in range(n))
        owners = [max(range(k), key=lambda t: factors[t][0][i]*factors[t][1][i]) for i in range(n)]
        owner = max(range(k), key=owners.count)
        chosen = [i for i in range(n) if owners[i] == owner][:m]
        assert len(chosen) == m
        u, v = factors[owner]
        diagonal_product = F(1)
        for i in chosen:
            assert u[i]*v[i] >= (1-3*error)/k
            diagonal_product *= u[i]*v[i]
        reverse_product = u[chosen[-1]]*v[chosen[0]]
        cross_product = F(1)
        for left, right in zip(chosen, chosen[1:]):
            assert u[left]*v[right] <= error
            cross_product *= u[left]*v[right]
        assert reverse_product*cross_product == diagonal_product
        assert budget*error**(m-1) >= ((1-3*error)/k)**m
        lo, hi = arbitrary_loss_interval(n, h)
        assert lo >= 2*error**2/F(81*len(contexts))
        assert hi-lo < F(1, 10**35)
    return informative


def audit():
    counts = {'optimal': 0, 'infeasible': 0, 'inconsistent_positive_inputs': 0}
    # Includes inactive vertices, self-loops, disconnected graphs and nontrivial cycles.
    for rows, columns, alphabet in ((2, 3, (-1, 0, 1, 2)), (3, 3, (-1, 0, 1))):
        edges = list(product(range(rows), range(columns)))
        for entries in product(alphabet, repeat=len(edges)):
            table = {edge: F(q) for edge, q in zip(edges, entries) if q >= 0}
            for tolerance in (F(1, 2), F(1), F(2)):
                eps = {edge: tolerance for edge, q in table.items() if q == 0}
                try:
                    certificate = solve_budget(rows, columns, table, eps)
                except ValueError as error:
                    assert 'positive-edge factors are inconsistent' in str(error)
                    counts['inconsistent_positive_inputs'] += 1
                    continue
                assert verify_budget(rows, columns, table, eps, certificate)
                oracle = exhaustive_path_oracle(rows, columns, table, eps)
                assert (oracle is None) == (certificate['status'] == 'INFEASIBLE')
                if oracle is not None:
                    assert oracle == certificate['budget']
                counts['infeasible' if oracle is None else 'optimal'] += 1

    weighted = {(i, i): F(q) for i, q in enumerate((2, 3, 5, 7))}
    weighted.update({edge: F(0) for edge in ((0, 1), (0, 2), (1, 3), (2, 3))})
    wt = {edge: F(1, d) for edge, d in zip(((0, 1), (0, 2), (1, 3), (2, 3)), (2, 3, 5, 7))}
    cert_w = solve_budget(4, 4, weighted, wt)
    assert verify_budget(4, 4, weighted, wt, cert_w)
    assert cert_w['budget'] == exhaustive_path_oracle(4, 4, weighted, wt) == 1470

    inactive = {(0, 0): F(1), (1, 1): F(1), (0, 1): F(0), (2, 0): F(0), (1, 2): F(0)}
    inactive_eps = {edge: F(1, 8) for edge, q in inactive.items() if not q}
    cert_i = solve_budget(3, 3, inactive, inactive_eps)
    assert cert_i['budget'] == 8  # NOT 8^3: inactive endpoint factors can be zero.
    assert verify_budget(3, 3, inactive, inactive_eps, cert_i)

    forgeries = []
    forged = deepcopy(cert_w)
    forged['budget'] -= 1
    forgeries.append((4, 4, weighted, wt, forged))
    forged = deepcopy(cert_w)
    forged['path'] = []
    forgeries.append((4, 4, weighted, wt, forged))
    forged = deepcopy(cert_i)
    forged['row_factors'][2] = F(100)
    forgeries.append((3, 3, inactive, inactive_eps, forged))
    forged = deepcopy(cert_w)
    forged['budget'] = float('nan')
    forgeries.append((4, 4, weighted, wt, forged))
    strict_wt = {edge: value/2 for edge, value in wt.items()}
    forgeries.append((4, 4, weighted, strict_wt, cert_w))
    square = {(0, 0): F(1), (1, 1): F(1), (0, 1): F(0), (1, 0): F(0)}
    square_eps = {(0, 1): F(1, 2), (1, 0): F(1, 2)}
    cert_s = solve_budget(2, 2, square, square_eps)
    assert cert_s['status'] == 'INFEASIBLE' and verify_budget(2, 2, square, square_eps, cert_s)
    forged = deepcopy(cert_s)
    forged['cycle'] = forged['cycle'][:1]
    forgeries.append((2, 2, square, square_eps, forged))
    # A gain-one cycle is feasible, so reusing its stricter certificate must fail.
    unit_eps = {edge: F(1) for edge in square_eps}
    forgeries.append((2, 2, square, unit_eps, cert_s))
    assert solve_budget(2, 2, square, unit_eps)['budget'] == 1
    assert all(not verify_budget(*entry) for entry in forgeries)

    construction_count, sample = 0, []
    for n in range(2, 10):
        contexts = guarded_contexts(n)
        assert len(contexts) == n*(n+5)//2
        for k in range(1, n+1):
            m = (n+k-1)//k
            for denominator in (2, 4, 8, 16):
                epsilon = F(1, denominator)
                factors = balanced_factors(n, k, epsilon)
                h = mass_table(n, factors)
                error = max(abs(value-(i is not None and i == j)) for (i, j), value in zip(contexts, h))
                budget = max(max(u)*max(v) for u, v in factors)
                assert budget == epsilon**(-(m-1))
                assert max(h) == 1 and min(h) >= 0 and error == (epsilon if k < n else 0)
                lo, hi = constructed_loss_interval(n, h)
                assert hi <= epsilon**2/8
                if k < n:
                    rational_error_lower = min(F(1, 6), epsilon/F((2*k)**m))
                    ce_lower = 2*rational_error_lower**2/F(81*len(contexts))
                    assert lo >= ce_lower > 0
                else:
                    assert lo == hi == 0
                # Independent original-parameter product identity, not fitted coefficient logs.
                for u, v in factors:
                    chosen = [i for i in range(n) if u[i]*v[i] > 0]
                    lhs = u[chosen[-1]]*v[chosen[0]]
                    rhs = F(1)
                    for i in chosen:
                        rhs *= u[i]*v[i]
                    for left, right in zip(chosen, chosen[1:]):
                        lhs *= u[left]*v[right]
                    assert lhs == rhs
                construction_count += 1
                if n == 8 and k in (1, 2, 4, 8) and denominator == 16:
                    sample.append({'n': n, 'products': k, 'longest_group_path': m-1,
                                   'final_normalizer_cap': 3, 'amplification_budget': str(budget),
                                   'mass_sup_error': str(error),
                                   'excess_ce_lower_float64_display': float(lo),
                                   'excess_ce_upper_float64_display': float(hi),
                                   'log_interval_width_less_than': '1e-40'})
                    assert hi-lo < F(1, 10**40)
    perturbed_count = perturbed_class_audit()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {'status': 'PASS', 'scope': 'fixed visible coefficient budget; guarded triangular parallel PRODUCT family',
            'base_commit': '992d7a2328908879d2ed387940b90fee7b487e0a',
            'source_sha256': source_hash, 'arithmetic': 'Fraction; exact rational log enclosures; floats only for display',
            'grid_inputs_including_tolerance_choices': 3*(4**6+3**9),
            'grid_classifications': counts, 'independent_simple_path_cycle_oracle': True,
            'weighted_heterogeneous_tolerance_optimum': str(cert_w['budget']),
            'inactive_vertex_counterexample_optimum': str(cert_i['budget']),
            'forged_certificates_rejected': len(forgeries),
            'guarded_task_constructions': construction_count,
            'inexact_positive_with_nonzero_sum_background_audits': perturbed_count, 'examples': sample,
            'not_claimed': ['general variable-parent nested PRODUCT grammar completeness',
                            'coefficient rejection excludes alternative observable lifts',
                            'AMP bridge, registered value/build/install, or GPU execution',
                            'amplification is an unspecified hardware resource']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_MASKED_PRODUCT_BUDGET_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
