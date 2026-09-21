"""Exact current-query projection, boundary response, and AMP non-equivalence.

Diagnostic only: full counts are immutable inputs, never a discarded state.
No Runtime, physical execution, resource certificate or model advantage.
"""
from collections import deque
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference import indexed_amp as amp
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation


def blocks(n, support):
    """Iterative undirected DFS; each returned block contains edge indices."""
    adjacency = [[] for _ in range(n)]
    for e, (u, v) in enumerate(support):
        adjacency[u].append((v, e))
        adjacency[v].append((u, e))
    seen, low, parent, parent_edge = ([-1]*n for _ in range(4))
    clock = 0
    result, edge_stack = [], []
    for root in range(n):
        if seen[root] >= 0:
            continue
        seen[root] = low[root] = clock
        clock += 1
        stack = [(root, iter(adjacency[root]))]
        while stack:
            v, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                p = parent[v]
                if p >= 0:
                    low[p] = min(low[p], low[v])
                    if low[v] >= seen[p]:
                        block = []
                        while True:
                            e = edge_stack.pop()
                            block.append(e)
                            if e == parent_edge[v]:
                                break
                        result.append(tuple(sorted(block)))
                continue
            u, e = child
            if e == parent_edge[v]:
                continue
            if seen[u] < 0:
                parent[u], parent_edge[u] = v, e
                seen[u] = low[u] = clock
                clock += 1
                edge_stack.append(e)
                stack.append((u, iter(adjacency[u])))
            elif seen[u] < seen[v]:
                low[v] = min(low[v], seen[u])
                edge_stack.append(e)
        assert not edge_stack
    result = tuple(sorted(result))
    assert sorted(e for row in result for e in row) == list(range(len(support)))
    return result


def paths(n, support):
    components = blocks(n, support)
    tree = [[] for _ in range(n+len(components))]
    for k, component in enumerate(components):
        for v in sorted({v for e in component for v in support[e]}):
            tree[v].append(n+k)
            tree[n+k].append(v)
    result = {}
    for i in range(n):
        parents = {i: None}
        queue = deque((i,))
        while queue:
            v = queue.popleft()
            for u in tree[v]:
                if u not in parents:
                    parents[u] = v
                    queue.append(u)
                else:
                    assert parents[v] == u or parents[u] == v
        for j in range(i, n):
            if j not in parents:
                result[i, j] = None
                continue
            path, v = [], j
            while v is not None:
                path.append(v)
                v = parents[v]
            path.reverse()
            result[i, j] = tuple((components[path[k]-n], path[k-1], path[k+1])
                                for k in range(1, len(path), 2))
    return result


def simple_path_edges(n, support, start, finish):
    """Independent exhaustive graph oracle, used once per small support."""
    adjacency = [[] for _ in range(n)]
    for e, (u, v) in enumerate(support):
        adjacency[u].append((v, e))
        adjacency[v].append((u, e))
    included = set()
    stack = [(start, frozenset((start,)), ())]
    while stack:
        v, visited, used = stack.pop()
        if v == finish:
            included.update(used)
            continue
        stack.extend((u, visited | {u}, used+(e,)) for u, e in adjacency[v] if u not in visited)
    return included


def block_messages(support, values, component):
    """Positive integer products and sums, with any one block vertex anchored."""
    vertices = sorted({v for e in component for v in support[e]})
    pairs = tuple(combinations(vertices, 2))
    result = {pair: [0, 0] for pair in pairs}
    for assignment in product((0, 1), repeat=len(vertices)-1):
        bits = dict(zip(vertices, (0,)+assignment))
        weight = 1
        for e in component:
            u, v = support[e]
            d = values[e]
            weight *= 9**(max(d, 0) if bits[u] == bits[v] else max(-d, 0))
        for u, v in pairs:
            result[u, v][bits[u] ^ bits[v]] += weight
    return {pair: tuple(value) for pair, value in result.items()}


def projected(n, support, values, plans):
    messages = {}
    result = {}
    for pair, path in plans.items():
        if pair[0] == pair[1]:
            result[pair] = F(1)
            continue
        if path is None:
            result[pair] = F(1, 2)
            continue
        A, B = 1, 0
        for component, u, v in path:
            if component not in messages:
                messages[component] = block_messages(support, values, component)
            a, b = messages[component][tuple(sorted((u, v)))]
            A, B = A*a+B*b, A*b+B*a
        result[pair] = F(A, A+B)
    return result


def literal(n, d):
    """Independent full-world exponent oracle with the native z0=0 anchor."""
    edges = tuple(combinations(range(n), 2))
    rows = []
    totals = {pair: 0 for pair in combinations(range(n), 2)}
    for word in range(1 << (n-1)):
        z = (0,)+tuple((word >> (n-1-v)) & 1 for v in range(1, n))
        exponent = sum(max(value, 0) if z[u] == z[v] else max(-value, 0)
                       for (u, v), value in zip(edges, d))
        weight = 9**exponent
        rows.append(weight)
        for u, v in totals:
            if z[u] == z[v]:
                totals[u, v] += weight
    total = sum(rows)
    return {**{pair: F(v, total) for pair, v in totals.items()},
            **{(v, v): F(1) for v in range(n)}}, tuple(F(w, total) for w in rows)


def boundary_audit():
    sizes = []
    for b in range(2, 8):
        q = b-1
        weights = tuple(1+(7*k+3*k*k) % 17 for k in range(1 << q))
        responses = [F(sum(w*9**((subset & ~word).bit_count()) for word, w in enumerate(weights)), sum(weights))
                     for subset in range(1 << q)]
        decoded = responses[:]
        for k in range(q):
            for low in range(1 << q):
                if low & (1 << k):
                    continue
                high = low | (1 << k)
                a, c = decoded[low], decoded[high]
                decoded[low], decoded[high] = (c-a)/8, (9*a-c)/8
        assert decoded == [F(w, sum(weights)) for w in weights]
        sizes.append({'boundary_vertices': b, 'positive_message_coordinates': len(weights),
                      'exact_star_responses': len(responses)})
    def forecast(weights, i, j):
        equal = sum(w for r, w in enumerate(weights) if ((r >> i) & 1) == ((r >> j) & 1))
        return F(1, 10)+F(4, 5)*F(equal, sum(weights))
    # Four boundary vertices; bit0 is the anchor, words store the other three.
    first = tuple(2+(-1)**word.bit_count() for word in range(8))
    second = tuple(2-(-1)**word.bit_count() for word in range(8))
    full = lambda row: tuple(row[word >> 1] if not word & 1 else 0 for word in range(16))
    assert all(forecast(full(first), i, j) == forecast(full(second), i, j)
               for i, j in combinations(range(4), 2))
    updated = [tuple(w*(9 if not word & 1 else 1) for word, w in enumerate(row)) for row in (first, second)]
    future = tuple(forecast(full(row), 2, 3) for row in updated)
    assert future == (F(33, 50), F(17, 50))
    horizons = []
    for b, h in ((4, 0), (6, 1), (8, 2)):
        pairs = tuple(combinations(range(b), 2))
        bits = [(0,)+tuple((r >> k) & 1 for k in range(b-1)) for r in range(1 << (b-1))]
        plus = tuple(2+(-1)**sum(z) for z in bits)
        minus = tuple(2-(-1)**sum(z) for z in bits)
        equal = [tuple(r for r,z in enumerate(bits) if z[i] == z[j]) for i,j in pairs]
        likelihoods = [tuple(9 if (z[i] ^ z[j]) == y else 1 for z in bits)
                       for i,j in pairs for y in (0,1)]
        checked = 0
        for length in range(h+1):
            for history in product(range(len(likelihoods)), repeat=length):
                multipliers = [1]*len(bits)
                for action in history:
                    multipliers = [a*c for a,c in zip(multipliers, likelihoods[action])]
                a = tuple(w*c for w,c in zip(plus, multipliers))
                c = tuple(w*d for w,d in zip(minus, multipliers))
                za, zc = sum(a), sum(c)
                for indices in equal:
                    assert sum(a[k] for k in indices)*zc == sum(c[k] for k in indices)*za
                    checked += 1
        suffix = tuple((2*k,2*k+1,0) for k in range(h+1))
        u, v = 2*h+2, 2*h+3
        results = []
        for row in (plus, minus):
            weighted = list(row)
            for i,j,y in suffix:
                weighted = [w*(9 if (z[i] ^ z[j]) == y else 1) for w,z in zip(weighted,bits)]
            mass = sum(w for w,z in zip(weighted,bits) if z[u] == z[v])
            results.append(F(1,10)+F(4,5)*F(mass,sum(weighted)))
        assert results == [F(1,2)+F(1,4)*F(4,5)**(h+2), F(1,2)-F(1,4)*F(4,5)**(h+2)]
        horizons.append({'boundary_vertices': b, 'indistinguishable_through_future_observations': h,
            'all_history_next_pair_checks': checked, 'first_distinguishing_suffix': list(map(list,suffix)),
            'next_pair': [u,v], 'different_forecasts': list(map(str, results))})
    return {'invertible_positive_star_response_checks': sizes, 'strict_finite_horizon_ladder': horizons,
        'equal_current_pair_moments_do_not_determine_arbitrary_boundary_messages': {
            'messages_on_anchored_assignments': [list(first), list(second)],
            'common_legal_boundary_observation': [0, 1, 0], 'next_query': [2, 3],
            'future_noisy_probabilities': list(map(str, future)),
            'scope': 'arbitrary positive flip-symmetric messages; count-family reachability of these two tables is not claimed'}}


def examples():
    rows = ((0, 0, 0, 1, 0, 0), (0, 0, 0, -1, 0, 0))
    current, theta, future = [], [], []
    for row in rows:
        marginals, weights = literal(4, row)
        current.append(F(1, 10)+F(4, 5)*marginals[0, 3])
        theta.append(weights[0])
        following = list(row)
        following[0] += 1  # actual common future (0,1,0)
        following[5] += 1  # actual common future (2,3,0)
        marginals, _ = literal(4, tuple(following))
        future.append(F(1, 10)+F(4, 5)*marginals[0, 3])
    assert current == [F(1, 2)]*2 and theta == [F(9, 40), F(1, 40)]
    assert future == [F(881, 1250), F(369, 1250)]
    d = (-2, -2, -2, -2, -2, 0, 0, 0, 0, -1)
    local = (-2, -2, -2)
    assert literal(5, d)[0][1, 2] == literal(3, local)[0][1, 2]
    records = []
    for n, values in ((5, d), (3, local)):
        c = CountState(n, values, None, sum(map(abs, values)), sum(map(abs, values)))
        schema, raw = IndexedRelation(n), amp.IndexedAmpState(c)
        plan = amp.prepare_prediction(schema, raw, schema.rules(), schema.source_row(n+2), output_cap=65536)
        prediction, _ = amp.execute_prediction(plan, raw, amp._Arithmetic(32768))
        records.append({'n': n, 'counts': list(values), 'words': list(prediction.words), 'output_cells': plan.output_cells})
    assert records[0]['words'] != records[1]['words']
    return {'current_query_projection_is_not_a_full_state_quotient': {
        'n': 4, 'counts': list(map(list, rows)), 'query': [0, 3],
        'current_forecasts': list(map(str, current)), 'current_first_world_theta': list(map(str, theta)),
        'common_suffix': [[0, 1, 0], [2, 3, 0]], 'future_forecasts': list(map(str, future))},
        'exact_cancellation_does_not_preserve_the_fixed_AMP_words': {
            'query': [1, 2], 'exact_latent_equal_probability': str(literal(5, d)[0][1, 2]),
            'executions': records, 'scope': 'exact RNE simulation; no new actual CUDA or transfer of the A4 certificate'}}


def audit():
    groups = []
    for n in range(2, 6):
        edges = tuple(combinations(range(n), 2))
        geometries = {}
        for mask in range(1 << len(edges)):
            support = tuple(e for k, e in enumerate(edges) if mask & (1 << k))
            plan = paths(n, support)
            for (i, j), path in plan.items():
                actual = set() if path is None else {e for block, _, _ in path for e in block}
                assert actual == simple_path_edges(n, support, i, j)
            geometries[mask] = (support, plan)
        count = projected_queries = smaller = 0
        for d in product((-1, 0, 1), repeat=len(edges)):
            mask = sum((1 << k) for k, value in enumerate(d) if value)
            support, plan = geometries[mask]
            values = tuple(value for value in d if value)
            observed = projected(n, support, values, plan)
            exact, _ = literal(n, d)
            assert observed == exact
            for (i, j), path in plan.items():
                multiplicity = 1 if i == j else 2
                projected_queries += multiplicity
                kept = set() if path is None else {e for block, _, _ in path for e in block}
                smaller += multiplicity*int(len(kept) < len(support))
            count += 1
        groups.append({'n': n, 'all_graph_supports': len(geometries), 'all_ternary_count_states': count,
                       'all_ordered_queries_checked': projected_queries, 'strictly_smaller_query_edge_sets': smaller})
        print(f'n{n} PASS', flush=True)
    return {'status': 'PASS_EXACT_QUERY_PROJECTION', 'scope': 'current exact normalized readout and restricted boundary futures; full count/state/provenance retained; no Runtime integration',
            'groups': groups, 'boundary_response': boundary_audit(), 'counterexamples': examples()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_QUERY_BLOCK_PROJECTION.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
