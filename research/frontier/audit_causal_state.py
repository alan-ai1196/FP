"""Exact tests for linear summaries and for identifying an unknown observed delay."""

from collections import Counter
from itertools import combinations
from math import prod

from text import log_bounds


def row_spaces(d):
    spaces = {frozenset([0]): ()}
    for mask in range(1, 1 << d):
        for span, rows in list(spaces.items()):
            if mask not in span:
                extended = span | {x ^ mask for x in span}
                spaces.setdefault(extended, (*rows, mask))
    return list(spaces.values())


def nonnegative_log_sum(terms):
    lo = hi = 0
    for value, mult in terms.items():
        l, h = log_bounds(value)
        lo += mult * (l if mult >= 0 else h)
        hi += mult * (h if mult >= 0 else l)
    if lo >= 0:
        return True
    if hi < 0:
        return False
    return prod(n**c for n, c in terms.items() if c > 0) >= prod(
        n ** (-c) for n, c in terms.items() if c < 0
    )


def linear_summaries(d):
    values = range(1 << d)
    noise = [7 ** (d - v.bit_count()) for v in values]
    denom = 8**d
    checked = 0
    for rows in row_spaces(d):
        rank = len(rows)
        projection = [
            sum((((u & a).bit_count() & 1) << j) for j, a in enumerate(rows))
            for u in values
        ]
        marginal = Counter()
        for u, mass in enumerate(noise):
            marginal[projection[u]] += mass
        for y in values:
            joint = Counter()
            for u in values:
                joint[projection[u]] += noise[u ^ y]
            assert all(joint[c] == marginal[c ^ projection[y]] for c in marginal)
        # denom * [H(AE)-rank h(1/8)] with one common integer log denominator.
        terms = Counter({denom: denom})
        for mass in marginal.values():
            terms[mass] -= mass
        terms[8] -= rank * denom
        terms[7] += rank * denom * 7 // 8
        assert nonnegative_log_sum(terms)
        checked += 1
    return checked


def forest():
    checks = 0
    for largest in range(3, 12):
        n = largest + 1
        for a, b in combinations(range(largest // 2 + 1, largest + 1), 2):
            edges = [(i, i + d) for d in (a, b) for i in range(n - d)]
            counts = Counter(
                sum(
                    ((((word >> i) ^ (word >> j)) & 1) << t)
                    for t, (i, j) in enumerate(edges)
                )
                for word in range(1 << n)
            )
            assert len(counts) == 2 ** len(edges) and len(set(counts.values())) == 1
            checks += 1
    return checks


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("audit requires assertions")
    print("five-bit linear subspaces", linear_summaries(5))
    print("uniform forest observations", forest())
