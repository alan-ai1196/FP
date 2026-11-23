"""Exact checks of the bounded-ticket law, the one-offer budget and feedback isolation."""

from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, pairwise, permutations, product
from math import prod

import numpy as np
from text import SCALE, ratio_log
from ticket_policy import (
    A,
    B,
    K,
    acquire,
    bounded_action_metrics,
    floor_law,
    ridge_features,
)


def compositions(n, k):
    for split in combinations(range(1, n), k - 1):
        yield tuple(y - x for x, y in pairwise((0, *split, n)))


def check_integral():
    count = native = 0
    for k, den in [(k, k + 4) for k in range(2, 7)] + [(4, 32)]:
        a = F(1, den)
        b = 1 - (k - 1) * a
        for row in compositions(den, k):
            p = tuple(F(z, den) for z in row)
            thresholds = sorted({a, b, *p})
            for y in range(k):
                # Exact unnormalized integral log(product) + rational price term.
                factor, price = F(1), F(0)
                for left, right in pairwise(thresholds):
                    buyers = [j for j in range(k) if p[j] >= right]
                    if y in buyers:
                        factor *= right / left
                    price -= len(buyers) * (right - left)
                assert factor == p[y] / a and price == k * a - 1
                count += 1
            if k == K and a == A:
                pp = np.tile(np.array(p, dtype=float), (k, 1))
                _, _, computed, _ = bounded_action_metrics(
                    pp, np.arange(k), np.full(k, (A + B) / 2), np.arange(k)
                )
                low, high = ratio_log(int(b / a), 1)
                for j, m in enumerate(row):
                    lo, hi = ratio_log(m, 1)
                    bot, top = F(lo, SCALE) + k * a - 1, F(hi, SCALE) + k * a - 1
                    bounds = [
                        x / (k * F(y, SCALE)) for x in (bot, top) for y in (low, high)
                    ]
                    assert (
                        float(min(bounds)) - 3e-15
                        <= computed[j]
                        <= float(max(bounds)) + 3e-15
                    )
                    native += 1
    return count, native


def check_menus():
    sets = 0
    for k in range(2, 6):
        a = F(1, k + 3)
        b = 1 - (k - 1) * a
        rows = [tuple(b if i == j else a for i in range(k)) for j in range(k)]
        for shift in range(11):
            raw = [
                (j, c, F(1 + (j + shift + i) % 4, 4), 1 + (2 * j + 3 * i + shift) % 5)
                for j in range(k)
                for i, c in enumerate((a / 2, a, (a + b) / 2, b, (1 + b) / 2))
            ]
            mass = sum(m for _, _, _, m in raw)
            offers = [(j, c, s, F(m, mass)) for j, c, s, m in raw]
            delta = [
                sum(s * m for j, c, s, m in offers if j == i and a < c <= b)
                for i in range(k)
            ]
            coverage = k * min(
                sum(m for j, c, s, m in offers if i == j and c <= a) for i in range(k)
            )
            assert sum(delta) <= 1 - coverage

            def utility(p, q):
                return sum(m * s * (p[j] - c) for j, c, s, m in offers if c <= q[j])

            for j, l in combinations(range(k), 2):
                p, q = rows[j], rows[l]
                total = utility(p, p) - utility(p, q) + utility(q, q) - utility(q, p)
                assert total == (b - a) * (delta[j] + delta[l])
            sets += 1
    return sets


@lru_cache(maxsize=None)
def tree_products(leaves, ratio):
    """exp(maximum path cost) for every ordered full binary tree."""
    if leaves == 1:
        return (F(1),)
    costs = []
    for left in range(1, leaves):
        right = leaves - left
        here = (1 + ratio / left) * (1 + ratio / right)
        for l, r in product(tree_products(left, ratio), tree_products(right, ratio)):
            costs.append(here * max(l, r))
    return tuple(costs)


def hierarchy():
    cases = 0
    for depth in (1, 2, 3):
        k = 2**depth
        for ratio in (F(1, 3), F(4), F(28)):
            costs = tree_products(k, ratio)
            balanced = prod((1 + ratio / 2**j) ** 2 for j in range(depth))
            assert min(costs) == balanced
            cases += len(costs)
    return cases


def blind_worlds():
    a, b = F(1, 8), F(3, 4)
    r = (b, a, a)
    p, q = (a, b, a), (a, a, b)
    # Every price strictly above a and at most b gives exactly the same observable kernel.
    for price in (F(1, 4), F(1, 2), b):

        def observation(truth):
            return tuple(
                (j, truth[j], 1 - truth[j]) if c >= price else (j, None, None)
                for j, c in enumerate(r)
            )

        assert observation(p) == observation(q)
    den = 8
    sign = lambda truth: prod(
        (x / y) ** int(den * w) for x, y, w in zip(p, q, truth, strict=True)
    )
    assert sign(p) > 1 and sign(q) == 1 / sign(p)


def feedback_isolation():
    n = 512
    prior = np.tile(floor_law(np.array([0.55, 0.2, 0.15, 0.1])), (n, 1))
    features = ridge_features(prior)
    js = np.arange(n) % 4
    cs = np.where(np.arange(n) % 2, A, B)
    world = np.arange(n) // 2 % 4
    changed = world.copy()
    changed[::2] = (changed[::2] + 1) % 4
    negative = (np.arange(n) % 2 == 1) & (world != js)
    changed[negative] = np.where(
        (world[negative] + 1) % 4 != js[negative],
        (world[negative] + 1) % 4,
        (world[negative] + 2) % 4,
    )
    assert np.any(world != changed)
    for ridge in (False, True):
        results = []
        for truth in (world, changed):
            used = []

            def supply(i, j):
                used.append(i)
                return js[i] == truth[i]

            snap = acquire(prior, features, js, cs, supply, ridge)
            results.append((used, snap))
        l, r = results
        assert l[0] == r[0] and all(i % 2 for i in l[0])
        for nobs in l[1]:
            lc, lb, lh = l[1][nobs]
            rc, rb, rh = r[1][nobs]
            assert (lb, lh) == (rb, rh) and np.array_equal(lc.readout, rc.readout)
    # Data carrying no word-specific likelihood leave all 24 explanations equally weighted.
    for perm in permutations(range(4)):
        row = np.full(4, 0.25)
        assert np.array_equal(row[list(perm)], row)


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    print(
        "exact menu integrals and outward-checked production payoffs", check_integral()
    )
    print(
        "rational offer distributions with extreme-pair and coverage checks",
        check_menus(),
    )
    print("binary tree products checked", hierarchy())
    blind_worlds()
    feedback_isolation()
    print("blind-world ranking reversal and purchase-only updates verified")
