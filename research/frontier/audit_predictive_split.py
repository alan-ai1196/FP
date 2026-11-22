"""Check the one-bit predictive-split reduction directly on ordinary probability rows."""

from fractions import Fraction as F
from itertools import combinations
from random import Random

from text import log_bounds, ratio_log


def entropy_mass(counts):
    total = sum(counts)
    low = high = 0
    for count in counts:
        if count:
            a, b = ratio_log(total, count)
            low += count * a
            high += count * b
    return low, high


def risk(rows, mask, binary_scale=0):
    """Optimized likelihood from conditional counts, without using the graph formula."""
    groups = [[0] * len(rows[0]) for _ in range(2)]
    for i, row in enumerate(rows):
        group = groups[(mask >> i) & 1]
        for j, value in enumerate(row):
            group[j] += value
    low = high = 0
    for group in groups:
        if binary_scale:
            total = binary_scale * sum(group)
            for positive in group:
                a, b = entropy_mass((positive, total - positive))
                low += a
                high += b
        else:
            a, b = entropy_mass(group)
            low += a
            high += b
    denom = sum(map(sum, rows)) * (len(rows[0]) * binary_scale if binary_scale else 1)
    return F(low, denom), F(high, denom)


def graph_test(n, edges):
    outcomes = n + len(edges)
    rows = [[0] * outcomes for _ in range(n)]
    for u in range(n):
        rows[u][u] = n**3
    for j, (u, v) in enumerate(edges, n):
        for endpoint in (u, v):
            rows[endpoint][j] = 1
            rows[endpoint][endpoint] -= 1
    smooth = [[(n**12 - 1) * outcomes * x + n**3 for x in row] for row in rows]
    assert all(min(row) > 0 for row in smooth)
    full = list(zip(*(entropy_mass(row) for row in rows), strict=True))
    base = tuple(F(sum(z), n**4) for z in full)
    two = log_bounds(2)
    records = []
    for mask in range(1 << (n - 1)):
        sizes = (mask.bit_count(), n - mask.bit_count())
        cut = sum(((mask >> i) ^ (mask >> j)) & 1 for i, j in edges)
        internal = len(edges) - cut
        ent = tuple(
            sum(F(s * log_bounds(s)[j], n) for s in sizes if s) for j in range(2)
        )
        formula = tuple(
            base[j] + ent[j] - F(2 * internal * two[1 - j], n**4) for j in range(2)
        )
        direct = risk(rows, mask)
        assert max(direct[0], formula[0]) <= min(direct[1], formula[1])
        records.append(
            (2 * sizes[0] == n, cut, risk(smooth, mask), risk(smooth, mask, n**6))
        )
    mincut = min(cut for balanced, cut, _, _ in records if balanced)
    best = [x for x in records if x[0] and x[1] == mincut]
    other = [x for x in records if not x[0] or x[1] != mincut]
    for index, scale in ((2, 1), (3, outcomes * n**6)):
        gap = min(x[index][0] for x in other) - min(x[index][1] for x in best)
        assert gap > F(two[1], 2 * n**4 * scale)
    return len(records)


def line_test(rng):
    # The verification uses nonuniform history masses and explicit full output rows.
    comparisons = 0
    for k in (3, 4, 6):
        for _ in range(16):
            v = [rng.randrange(-4, 5) for _ in range(k - 1)]
            v.append(-sum(v))
            origin = [8 * abs(x) + rng.randrange(1, 12) for x in v]
            t = list(range(7))
            rng.shuffle(t)
            rows = []
            for level in t:
                weight = rng.randrange(1, 7)
                rows.append(
                    [weight * (a + level * b) for a, b in zip(origin, v, strict=True)]
                )
            all_masks = [risk(rows, mask) for mask in range(64)]
            thresholds = [
                risk(rows, sum(1 << i for i, s in enumerate(t) if s < j))
                for j in range(8)
            ]
            exact = (min(x[0] for x in all_masks), min(x[1] for x in all_masks))
            swept = (min(x[0] for x in thresholds), min(x[1] for x in thresholds))
            assert max(exact[0], swept[0]) <= min(exact[1], swept[1])
            comparisons += len(all_masks)
    return comparisons


def query_scope():
    """One underlying process, with the query either free or scored as a token."""
    result = {}
    for noise in (0, 1):
        rows = []
        query_rows = []
        for u in range(4):
            right = 2 * u + 1
            weights = [1024 - noise if q == u // 2 else noise for q in range(2)]
            rows.append([w * p for w in weights for p in (8 - right, right)])
            query_rows.append(weights)
        joint = {m: risk(rows, m) for m in range(0, 16, 2)}
        conditional = {}
        for m, j in joint.items():
            q = risk(query_rows, m)
            conditional[m] = (j[0] - q[1], j[1] - q[0])

        def optima(loss):
            best = min(x[1] for x in loss.values())
            return [m for m, x in loss.items() if x[0] <= best]

        j, c = optima(joint), optima(conditional)
        assert j == [12] and all(m in (6, 10) for m in c)
        assert noise or c == [6, 10]
        result[noise] = (j, c)
    return result


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    rng = Random(84192)
    cases = comparisons = 0
    for n in (2, 4, 6, 8):
        possible = list(combinations(range(n), 2))
        masks = (
            range(1 << len(possible))
            if n <= 4
            else [
                0,
                (1 << len(possible)) - 1,
                *(rng.getrandbits(len(possible)) for _ in range(8)),
            ]
        )
        for mask in masks:
            edges = [edge for j, edge in enumerate(possible) if (mask >> j) & 1]
            comparisons += graph_test(n, edges)
            cases += 1
    print("graph channels", cases, "partitions per channel summed", comparisons)
    print("partitions compared to affine-line thresholds", line_test(rng))
    print(
        "query noise units over 1024 -> best joint and conditional masks", query_scope()
    )
