"""Exact positive elimination for the count-encoded relation learner.

This passive decoder preserves correlated laws. It is not a new native
Program, Runtime encoding, raw phase evidence format or AMP bridge.
"""
from fractions import Fraction as F
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
import count_learner_encoding as counts
import factor_query_matroid as matroid
import simplex_gradient as native
from fp_reference.learner import ReferenceLearnerState, observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import ArithmeticUnresolved, Evaluation, evaluate

BITS = 32768


def edges(n):
    return tuple(combinations(range(n), 2))


def adjacency(n, signed):
    """Anchor0 is pinned, so incident factors are unary on the free graph."""
    result = [0]*(n-1)
    for (u, v), d in zip(edges(n), signed):
        if d and u:
            result[u-1] |= 1 << (v-1)
            result[v-1] |= 1 << (u-1)
    return tuple(result)


def fill_order(adj, order):
    remaining = (1 << len(adj))-1
    graph = list(adj)
    width = 0
    for v in order:
        neighbors = graph[v] & remaining & ~(1 << v)
        width = max(width, neighbors.bit_count())
        for u in range(len(adj)):
            if neighbors >> u & 1:
                graph[u] |= neighbors & ~(1 << u)
        remaining &= ~(1 << v)
    assert not remaining
    return width


def greedy_order(adj):
    graph = list(adj)
    remaining = (1 << len(adj))-1
    order = []
    while remaining:
        choices = []
        for v in range(len(adj)):
            if remaining >> v & 1:
                neighbors = graph[v] & remaining & ~(1 << v)
                missing = sum((neighbors & ~graph[u] & ~(1 << u)).bit_count()
                              for u in range(len(adj)) if neighbors >> u & 1)//2
                choices.append((missing, neighbors.bit_count(), v, neighbors))
        _, _, v, neighbors = min(choices)
        for u in range(len(adj)):
            if neighbors >> u & 1:
                graph[u] |= neighbors & ~(1 << u)
        remaining &= ~(1 << v)
        order.append(v)
    return tuple(order)


def exact_order(adj):
    """Subset minimax DP; connectivity through an eliminated set is order-free."""
    n = len(adj)
    if n > 15:
        raise ArithmeticUnresolved('passive exact-order audit is capped at15 free vertices')
    full = (1 << n)-1
    best = [n]*(full+1)
    previous = [-1]*(full+1)
    best[0] = 0
    for removed in range(full):
        left = full ^ removed
        components = []
        unexplored = removed
        while unexplored:
            seed = unexplored & -unexplored
            component, boundary, fringe = 0, 0, seed
            while fringe:
                bit = fringe & -fringe
                fringe ^= bit
                v = bit.bit_length()-1
                component |= bit
                boundary |= adj[v]
                fringe |= adj[v] & removed & ~component
            unexplored &= ~component
            components.append((component, boundary & left))
        for v in range(n):
            bit = 1 << v
            if not left & bit:
                continue
            neighbors = adj[v] & left
            for component, boundary in components:
                if adj[v] & component:
                    neighbors |= boundary
            width = (neighbors & ~bit).bit_count()
            following = removed | bit
            score = max(best[removed], width)
            if score < best[following]:
                best[following], previous[following] = score, v
    order, mask = [], full
    while mask:
        v = previous[mask]
        assert v >= 0
        order.append(v)
        mask ^= 1 << v
    order.reverse()
    assert fill_order(adj, order) == best[full]
    return tuple(order), best[full]


def decode(n, signed, query, order=None):
    """Positive integer joins/sums, followed by the scalar probability division."""
    assert len(signed) == n*(n-1)//2 and all(type(d) is int for d in signed)
    counts.query(n, *query)
    height = sum(map(abs, signed))
    if n+4*height+4 > BITS:
        raise ArithmeticUnresolved('positive integer decoder exponent envelope exceeds its bit cap')
    order = greedy_order(adjacency(n, signed)) if order is None else tuple(order)
    assert sorted(order) == list(range(n-1))
    kept = tuple(sorted({v for v in query if v}))
    factors = []
    for (i, j), d in zip(edges(n), signed):
        if not d:
            continue
        scope = tuple(v for v in (i, j) if v)
        scale = 9**abs(d)
        table = []
        for word in range(1 << len(scope)):
            values = {v: (word >> k) & 1 for k, v in enumerate(scope)}
            parity = values.get(i, 0) ^ values.get(j, 0)
            table.append(scale if parity == int(d < 0) else 1)
        factors.append((scope, tuple(table)))
    multiply = add = 0
    peak_join = 1
    peak_live = sum(len(table) for _, table in factors)
    maximum_bits = max((v.bit_length() for _, table in factors for v in table), default=1)

    def join(items, scope):
        nonlocal multiply, peak_join, maximum_bits
        positions = {v: k for k, v in enumerate(scope)}
        projections = [tuple(positions[v] for v in fs) for fs, _ in items]
        result = []
        for word in range(1 << len(scope)):
            value = 1
            for (_, table), positions in zip(items, projections):
                index = sum(((word >> p) & 1) << k for k, p in enumerate(positions))
                value *= table[index]
                multiply += 1
                maximum_bits = max(maximum_bits, value.bit_length())
            result.append(value)
        peak_join = max(peak_join, len(result))
        return tuple(result)

    for zero_based in order:
        v = zero_based+1
        if v in kept:
            continue
        bucket = [f for f in factors if v in f[0]]
        rest = [f for f in factors if v not in f[0]]
        scope = tuple(sorted({v}.union(*(set(s) for s, _ in bucket))))
        joined = join(bucket, scope)
        out_scope = tuple(u for u in scope if u != v)
        position = scope.index(v)
        out = []
        for word in range(1 << len(out_scope)):
            low = word & ((1 << position)-1)
            index = low | ((word >> position) << (position+1))
            value = joined[index]+joined[index | (1 << position)]
            add += 1
            maximum_bits = max(maximum_bits, value.bit_length())
            out.append(value)
        # Logical integer cells, including coexistence, not Python heap bytes.
        peak_live = max(peak_live, sum(len(t) for _, t in factors)+len(joined)+len(out))
        factors = rest+[(out_scope, tuple(out))]
    final = join(factors, kept)
    peak_live = max(peak_live, sum(len(t) for _, t in factors)+len(final))
    partition = [0, 0]
    for word, value in enumerate(final):
        assignment = {v: (word >> k) & 1 for k, v in enumerate(kept)}
        parity = assignment.get(query[0], 0) ^ assignment.get(query[1], 0)
        partition[parity] += value
        add += 1
    total = partition[0]+partition[1]
    add += 1
    maximum_bits = max(maximum_bits, total.bit_length())
    assert total > 0 and maximum_bits <= n+4*height <= BITS
    return tuple(partition), {'positive_multiplications': multiply, 'positive_additions': add,
        'largest_join_cells': peak_join, 'peak_live_integer_cells': peak_live,
        'maximum_integer_bits': maximum_bits, 'base_order_width': fill_order(adjacency(n, signed), order)}


def forecast(parts):
    a, b = parts
    return F(9*a+b, 10*(a+b))


def enumeration(n, signed, queries):
    """Independent full-world integer oracle; no message tables or fill graph."""
    active = [(i, j, d) for (i, j), d in zip(edges(n), signed) if d]
    powers = [9**h for h in range(sum(map(abs, signed))+1)]
    result = [[0, 0] for _ in queries]
    for word in range(1 << (n-1)):
        z = (0,)+tuple((word >> i) & 1 for i in range(n-1))
        exponent = sum(abs(d) for i, j, d in active if (z[i] ^ z[j]) == int(d < 0))
        weight = powers[exponent]
        for row, (i, j) in zip(result, queries):
            row[z[i] ^ z[j]] += weight
    return tuple(tuple(row) for row in result)


def width_audit():
    checked = orders = 0
    for n in range(1, 6):
        pairs = edges(n)
        for mask in range(1 << len(pairs)):
            adj = [0]*n
            for e, (i, j) in enumerate(pairs):
                if mask >> e & 1:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
            _, width = exact_order(tuple(adj))
            exhaustive = min(fill_order(adj, order) for order in permutations(range(n)))
            assert width == exhaustive
            checked += 1
            orders += math.factorial(n)
    return {'graphs': checked, 'independent_elimination_orders': orders,
            'exact_order_free_vertex_cap': 15}


def complete_decode(state, query):
    parts, stats = decode(state.n, state.counts, query)
    total = sum(parts)
    worlds = tuple((0,)+z for z in product((0, 1), repeat=state.n-1))
    active = [(e, d) for e, d in zip(edges(state.n), state.counts) if d]
    weights = tuple(F(9**sum(abs(d) for (i, j), d in active if (z[i] ^ z[j]) == int(d < 0)), total)
                    for z in worlds)
    gradient = (F(0),)*(len(worlds)+1)
    if state.pending is not None:
        i, j, y = state.pending
        pending_parts, _ = decode(state.n, state.counts, (i, j))
        mass = 1+8*F(pending_parts[y], sum(pending_parts))
        gradient = (1/mass-F(1, 5),)+tuple(F(4, 5)-8*int(z[i] ^ z[j] == y)/mass for z in worlds)
    learner = ReferenceLearnerState((F(1),)+weights, (), gradient, int(state.pending is not None), state.cursor, state.steps)
    n = state.n
    source = tuple(F(k == query[side]) for side in (0, 1) for k in range(n))
    pair = tuple(F((i, j) == query) for i, j in product(range(n), repeat=2))
    indicators = tuple(F(z[query[0]] ^ z[query[1]] == y) for z in worlds for y in (0, 1))
    excesses = tuple(8*F(p, total) for p in parts)
    masses = tuple(1+v for v in excesses)
    cache = Evaluation(source+pair+indicators+excesses, excesses, masses, F(10), tuple(v/10 for v in masses), ())
    return learner, cache, stats


def native_audit():
    units = 0
    for n, depth in ((2, 3), (3, 2)):
        rules, graph, _ = native.relation_graph(n)
        spec = counts.spec(n)
        start = counts.native_initial(n), counts.initialize(n)
        frontier = [start]
        for _ in range(depth):
            following = []
            for original, encoded in frontier:
                for i, j, label in product(range(n), range(n), (0, 1)):
                    predicted = evaluate(graph, rules, original.theta, native.context(n, i, j), (), bit_limit=BITS)
                    decoded, cache, _ = complete_decode(encoded, (i, j))
                    assert decoded == original and cache == predicted
                    observed = observe_event(graph, original, spec, predicted, label, bit_limit=BITS)
                    pending = counts.observe(encoded, i, j, label)
                    assert complete_decode(pending, (i, j))[0] == observed
                    committed = commit_event(observed, spec, bit_limit=BITS)
                    next_encoded = counts.commit(pending)
                    assert complete_decode(next_encoded, (i, j))[0] == committed
                    following.append((committed, next_encoded))
                    units += 1
            frontier = following
    # Replayed profiles, ordinary clock reattachment, cancellations and diagonals.
    profile_units = 0
    for repeats in (1, 2, 3):
        n = 4
        rules, graph, _ = native.relation_graph(n)
        spec = counts.spec(n)
        original, encoded = counts.native_initial(n), counts.initialize(n)
        history = ((0, 1, 0), (1, 2, 1), (2, 3, 0))*repeats
        for event in history+((0, 1, 1), (3, 3, 0), (0, 3, 0)):
            if encoded.steps == len(history):
                original, encoded = attach_boundary(original, 20, spec), counts.attach(encoded, 20)
            i, j, label = event
            before, prediction, _ = complete_decode(encoded, (i, j))
            assert before == original
            assert prediction == evaluate(graph, rules, original.theta, native.context(n, i, j), (), bit_limit=BITS)
            original = observe_event(graph, original, spec, prediction, label, bit_limit=BITS)
            encoded = counts.observe(encoded, i, j, label)
            assert complete_decode(encoded, (i, j))[0] == original
            original, encoded = commit_event(original, spec, bit_limit=BITS), counts.commit(encoded)
            assert complete_decode(encoded, (i, j))[0] == original
            profile_units += 1
    return {'exhaustive_native_units': units, 'profile_and_continuation_units': profile_units,
            'complete_native_caches': units+profile_units,
            'complete_observed_and_committed_states': 2*(units+profile_units), 'profile_attachments': 3}


def signed_tensor_audit():
    checks = 0
    for n in (2, 3, 4):
        queries = tuple(product(range(n), repeat=2))
        for signed in product((-1, 0, 1), repeat=n*(n-1)//2):
            reference = enumeration(n, signed, queries)
            for query, expected in zip(queries, reference):
                actual, stats = decode(n, signed, query)
                assert actual == expected
                assert stats['largest_join_cells'] <= 1 << (stats['base_order_width']+3)
                checks += 1
    return {'signed_count_profiles': 3+27+729, 'all_pair_integer_partition_checks': checks}


def cycle_arc(factors):
    even, odd = 1, 0
    for a, b in factors:
        even, odd = even*a+odd*b, even*b+odd*a
    return even, odd


def cycle_audit():
    rows = []
    for n in (3, 4, 8, 16, 32, 64):
        edge_map = {tuple(sorted((i, (i+1) % n))): 1 if i % 2 else -2 for i in range(n)}
        signed = tuple(edge_map.get(e, 0) for e in edges(n))
        arc_factors = [((9**abs(edge_map[tuple(sorted((i, (i+1) % n)))]), 1)
                        if edge_map[tuple(sorted((i, (i+1) % n)))] > 0 else
                        (1, 9**abs(edge_map[tuple(sorted((i, (i+1) % n)))]))) for i in range(n)]
        queries = tuple(dict.fromkeys(((0, 1), (0, n-1), (1, n//2), (n//2, n-1), (1, 1), (2, 1))))
        maximum_cells = maximum_work = maximum_bits = 0
        for query in queries:
            i, j = sorted(query)
            a, b = cycle_arc(arc_factors[i:j]), cycle_arc(arc_factors[j:]+arc_factors[:i])
            expected = (a[0]*b[0], a[1]*b[1])
            actual, stats = decode(n, signed, query)
            assert actual == expected
            maximum_cells = max(maximum_cells, stats['largest_join_cells'])
            maximum_work = max(maximum_work, stats['positive_multiplications']+stats['positive_additions'])
            maximum_bits = max(maximum_bits, stats['maximum_integer_bits'])
        vectors = tuple(matroid.edge_vector(e) for e in edge_map)
        assert len(matroid.components(vectors)) == 1 and matroid.rank(vectors) == n-1
        rows.append({'n': n, 'query_component_rank': n-1, 'fixed_product_required_categories': 1 << (n-1),
                     'anchored_elimination_width': fill_order(adjacency(n, signed), greedy_order(adjacency(n, signed))),
                     'exact_query_checks': len(queries), 'maximum_join_cells': maximum_cells,
                     'maximum_positive_scalar_operations': maximum_work, 'maximum_integer_bits': maximum_bits})
    return rows


def retained_tape_audit():
    import joint_model as model
    rows = []
    for case in model.new_cases():
        n = case[0]
        _, _, training, evaluation = model.data(case)
        signed = [0]*len(edges(n))
        locations = {e: i for i, e in enumerate(edges(n))}
        first_joint = None
        snapshots = []
        for cursor, (i, j, y) in enumerate(training+evaluation, 1):
            if i != j:
                signed[locations[tuple(sorted((i, j)))]] += 1-2*y
            vectors = tuple(matroid.edge_vector(e) for e, d in zip(edges(n), signed) if d)
            newly_joint = (cursor >= len(training) and first_joint is None
                and len(matroid.components(vectors)) == 1 and matroid.rank(vectors) == n-1)
            if newly_joint:
                first_joint = cursor
            if cursor in (len(training), len(training)+len(evaluation)) or newly_joint:
                order, width = exact_order(adjacency(n, signed))
                queries = tuple(dict.fromkeys(((0, 1), (0, n-1), (1, n//2), (n//2, n-1), (1, 1), (n-1, 1))))
                reference = enumeration(n, signed, queries)
                stats_rows = []
                for query, expected in zip(queries, reference):
                    result, stats = decode(n, signed, query, order)
                    assert result == expected
                    assert stats['largest_join_cells'] <= 1 << (width+3)
                    stats_rows.append(stats)
                snapshots.append({'cursor': cursor, 'stage': 'training' if cursor == len(training) else
                    'final' if cursor == len(training)+len(evaluation) else 'first_full_rank_query_component',
                    'active_nonloop_edges': sum(d != 0 for d in signed),
                    'exact_anchored_treewidth': width, 'witness_order_zero_based_free_vertices': list(order),
                    'audited_queries': queries, 'exact_partition_checks': len(queries),
                    'maximum_join_cells': max(s['largest_join_cells'] for s in stats_rows),
                    'maximum_live_integer_cells': max(s['peak_live_integer_cells'] for s in stats_rows),
                    'maximum_positive_scalar_operations': max(s['positive_multiplications']+s['positive_additions'] for s in stats_rows),
                    'maximum_integer_bits': max(s['maximum_integer_bits'] for s in stats_rows)})
        rows.append({'case': case, 'worlds': 1 << (n-1), 'first_full_rank_query_component_cursor': first_joint,
                     'snapshots': snapshots})
    return {'scope': 'passive fixed-tape structure and exact scalar decoding; no model rerun or physical outcome', 'cases': rows}


def refusal_audit():
    reasons = []
    for operation in (lambda: exact_order((0,)*16), lambda: decode(2, (10**12,), (0, 1))):
        try:
            operation()
        except ArithmeticUnresolved as exc:
            reasons.append(str(exc))
        else:
            raise AssertionError('an unfunded passive exact computation was accepted')
    return {'checks': len(reasons), 'reasons': reasons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--skip-tapes', action='store_true')
    args = parser.parse_args()
    result = {'status': 'PASS', 'scope': 'exact count decoder; no native graph substitution or Runtime/AMP authority',
              'operation_count_scope': 'positive integer table joins/sums only; excludes factor powers, order search, scalar readout division, metadata and full native output',
              'integer_bit_scope': 'factors, table products/sums and partition Z; scalar readout needs at most four more bits',
              'live_cell_scope': 'logical integer table cells with coexistence, not process bytes or a Runtime reservation',
              'reference_integer_bits': BITS, 'exact_width': width_audit(),
              'signed_tensors': signed_tensor_audit(), 'complete_native': native_audit(),
              'irreducible_cycles': cycle_audit()}
    if not args.skip_tapes:
        result['retained_tapes'] = retained_tape_audit()
    result['refusals'] = refusal_audit()
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
