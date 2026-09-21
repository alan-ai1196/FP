"""Positive integer partition schedule with explicit width/height guards.

The scheduler and logical work counters supply no owned resource authority.
"""
from fractions import Fraction as F
from itertools import combinations
from . import indexed_count as counts
from .semantics import ArithmeticUnresolved

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
