"""Exact checks of the minimum window that can distinguish token actions."""

from fractions import Fraction
from itertools import product
from math import ceil, comb, floor, lcm, prod

import numpy as np
from symbol_refinement import WORDS, V, partitions, teacher
from text import log_bounds, outward, ratio_log


def rank(matrix):
    rows = [[Fraction(x) for x in row] for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        i = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if i is None:
            continue
        rows[pivot], rows[i] = rows[i], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            mult = rows[i][col] / rows[pivot][col]
            rows[i] = [a - mult * b for a, b in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def instance(d):
    z = np.array([(-1) ** i * comb(d - 1, i) for i in range(d)], dtype=object)
    scale_s = 2 * d * (d + 1)
    scale_delta = 8 * d * max(abs(v) for v in z) ** 2
    den = lcm(2 * scale_s, scale_delta)
    ones = np.ones(d, dtype=object)
    unit = np.outer(ones, ones)
    s = (unit + np.diag(range(1, d + 1))) * (den // scale_s)
    original = (unit * (den // d) - s) // 2
    change = np.outer(z, z) * (den // scale_delta)
    base = (original, original, s)
    changed = (original + change, original - change, s)
    assert all((m > 0).all() for m in changed) and np.array_equal(
        sum(changed), unit * (den // d)
    )
    reachable = [ones]
    for _ in range(d - 1):
        reachable.append(reachable[-1] @ s)
    assert rank(reachable) == d
    assert all(row @ z == 0 for row in reachable[:-1]) and reachable[-1] @ z != 0
    left = right = ones[None, :]
    checked = 1
    for _ in range(2 * d - 2):
        left = np.concatenate([left @ matrix for matrix in base])
        right = np.concatenate([right @ matrix for matrix in changed])
        assert np.array_equal(left.sum(axis=1), right.sum(axis=1))
        checked += len(left)
    flank = reachable[-1]
    p = Fraction(flank @ (changed[0] - changed[1]) @ flank, d * den ** (2 * d - 1))
    assert p > 0
    return checked, p


def lossless_partitions(length):
    words = list(product(range(V), repeat=length))
    law = {w: teacher(w) for w in words}
    margin = [teacher((a,)) for a in range(V)]
    accepted = []
    for labels in partitions():
        # If refinement is lossless, word probability divided by the product of
        # its fine letter probabilities is constant across each coarse-word fiber.
        ratios = {}
        for word in words:
            coarse = tuple(labels[a] for a in word)
            ratio = law[word] / prod(margin[a] for a in word)
            if ratios.setdefault(coarse, ratio) != ratio:
                break
        else:
            accepted.append(labels)
    coarsest = min(accepted, key=lambda g: len(set(g)))
    assert all(
        all(
            coarsest[a] == coarsest[b]
            for a, b in product(range(V), repeat=2)
            if g[a] == g[b]
        )
        for g in accepted
    )
    return len(accepted), coarsest


def bernoulli_entropy(p):
    terms = [(v, ratio_log(v.denominator, v.numerator)) for v in (p, 1 - p) if v]
    return tuple(sum(v * bound[i] for v, bound in terms) for i in (0, 1))


def merged_action_cost():
    labels = (0, 1, 1, 2, 1, 1)
    coarse = {}
    for w in WORDS:
        key = tuple(labels[a] for a in w)
        coarse[key] = coarse.get(key, Fraction()) + teacher(w)
    direct = [0, 0]
    for w in WORDS:
        key = tuple(labels[a] for a in w)
        q = coarse[key] / 4 ** key.count(1)
        p = teacher(w)
        ratio = p / q
        gap = ratio_log(ratio.numerator, ratio.denominator)
        for j in (0, 1):
            direct[j] += p * gap[j]
    fresh = bernoulli_entropy(Fraction(3, 4))
    base = bernoulli_entropy(Fraction(5, 8))
    assert direct[0] <= (log_bounds(2)[1] - base[0]) / Fraction(8)
    assert direct[1] >= (log_bounds(2)[0] - base[1]) / Fraction(8)
    # Before the next observation the number of informative symbols since a
    # hidden reset is geometric. Bound the entire uncomputed remainder.
    total = [0, 0]
    max_run = 40
    for k in range(max_run + 1):
        for m in range(k + 1):
            denominator = 3**m + 3 ** (k - m)
            weight = Fraction(comb(k, m) * denominator, 2 ** (k + 3) * 4**k)
            posterior = Fraction(3**m, denominator)
            h = bernoulli_entropy(Fraction(1, 4) + posterior / 2)
            total[0] += weight * (h[0] - fresh[1])
            total[1] += weight * (h[1] - fresh[0])
    total[1] += Fraction(log_bounds(2)[1] - fresh[0], 2 ** (max_run + 2))
    return outward((floor(direct[0]), ceil(direct[1])), 3), outward(
        (floor(total[0]), ceil(total[1])), 1
    )


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    for d in range(2, 6):
        count, difference = instance(d)
        print(
            f"rank {d}, identical probabilities on {count} words, first length {2 * d - 1}, gap {difference}"
        )
    print("per-token excess, length three and infinite history", merged_action_cost())
    for length in (2, 3):
        print("population lossless partitions", length, lossless_partitions(length))
