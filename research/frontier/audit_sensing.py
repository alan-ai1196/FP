"""Exact finite frontiers for late sensors, and quantifier checks for controlled simulators."""

from fractions import Fraction as F
from itertools import pairwise, product
from math import comb

import numpy as np


def statistics(d):
    n = 2**d
    for mask in range(1 << n):
        counts = np.zeros((2, d, 2), dtype=int)
        for x in range(n):
            for j in range(d):
                counts[(mask >> x) & 1, j, (x >> j) & 1] += 1
        yield counts


def statistic_gain(counts, rho):
    return sum(
        max(F(0), int(max(pair)) - rho * int(sum(pair)))
        for state in counts
        for pair in state
    ) / int(counts.sum())


def two_plans(d, rho):
    b = F(1, 2) - rho
    best = F(0)
    for opposed in range(d + 1):
        for one in range(d - opposed + 1):
            e = sum(
                comb(opposed, i)
                * comb(one, j)
                * abs(2 * i - opposed + F(2 * j - one, 2) + one * b)
                for i in range(opposed + 1)
                for j in range(one + 1)
            ) / 2 ** (opposed + one)
            score = (
                (d - opposed - one) * max(0, b) + (opposed + F(one, 2)) * b + e / 2
            ) / d
            best = max(best, score)
    return best


def finite_optima():
    tensors = list(statistics(3))
    for rho in (F(0), F(1, 3), F(1, 2), F(5, 8), F(3, 4), F(1)):
        values = [statistic_gain(t, rho) for t in tensors]
        coordinate = (max(0, 1 - rho) + 2 * max(0, F(1, 2) - rho)) / 3
        majority = max(0, F(3, 4) - rho)
        assert max(values) == two_plans(3, rho) == max(coordinate, majority)
        assert values[170] == coordinate and values[232] == majority
    # All distinct posterior cells and actual two-stage terminal actions, including inverting the purchased bit.
    posteriors = {
        F(int(pair[1]), int(sum(pair)))
        for t in tensors
        for state in t
        for pair in state
        if sum(pair)
    }
    delta = F(3, 8)
    for p, cost in product(posteriors, (F(0), F(1, 8), F(9, 32), F(3, 8))):
        options = [F(1, 2)] * 2
        for selected in (p, 1 - p):
            correct = F(1, 2) + delta * selected
            for prediction in product((0, 1), repeat=2):
                acc = sum(
                    (correct if z == y else 1 - correct) / 2
                    for z, y in product(range(2), repeat=2)
                    if prediction[z] == y
                )
                options.append(acc - cost)
        assert max(options) == F(1, 2) + max(0, delta * max(p, 1 - p) - cost)
    chars = np.array([[1 - 2 * ((x >> j) & 1) for j in range(3)] for x in range(8)])
    earlier = np.array(list(product((-1, 1), repeat=8))) @ chars
    later = np.array(list(product((-1, 0, 1), repeat=8))) @ chars
    bounds = np.abs(earlier) @ np.abs(later).T
    assert bounds.max() == 64
    for i in np.flatnonzero(bounds.max(axis=1) == 64):
        assert max(abs(earlier[i])) == 8
    return len(tensors), len(posteriors) * 4 * 10, bounds.size


def overlap_segments(p, xprob, labels):
    # Put additional probability on the reported label with the largest remaining marginal overlap.
    parts = []
    for label in (0, 1):
        ids = [i for i, v in enumerate(labels) if v == label]
        last = F(0)
        for level in sorted({xprob[i] for i in ids}):
            parts.append((sum(p[i] for i in ids if xprob[i] >= level), level - last))
            last = level
    return sorted(parts, reverse=True)


def overlap(parts, mass):
    value = F(0)
    for slope, width in parts:
        add = min(mass, width)
        value += slope * add
        mass -= add
    return value


def acquisition_bound():
    # One fixed task per hypothesis. The row gauge fixes the first sign.
    from math import fsum, sqrt

    names = np.arange(8)
    train = (names[None, :] - names[:, None]) % 8
    train = (train != 0) & (train != 3)
    rows = np.array([(0, *v) for v in product(range(2), repeat=7)], dtype=int)
    cols = np.array(list(product(range(2), repeat=8)), dtype=int)
    sizes = np.count_nonzero(
        (rows[:, None, :, None] ^ cols[None, :, None, :]) & train, axis=(2, 3)
    )
    count = np.bincount(sizes.ravel(), minlength=49)
    assert count[0] == 1 and np.flatnonzero(count)[1] == 6

    def aff(p, h):
        return sqrt(p * h) + sqrt((1 - p) * (1 - h))

    def one(k, h):
        z = k / 48
        return (
            7 + (1 - z) * (1 + aff(0.875, h)) + z * (aff(0.875, 0.5) + aff(0.5, h))
        ) / 9

    return [
        min(
            1,
            3
            * fsum(
                n * one(k, h) ** N
                for k, n in enumerate(count)
                if k and n
                for h in (0.625, 0.75, 0.875, 0.9375)
            ),
        )
        for N in (384, 3072, 24576)
    ]


def causal_comparison():
    p = (F(4, 9), F(3, 9), F(2, 9))
    zero = (F(1, 4), F(3, 4), F(1, 2))
    one = tuple(1 - x for x in zero)
    default = (1, 0, 0)
    branches = [overlap_segments(p, zero, x) for x in (default, (0, 1, 0))]
    tail = overlap_segments(p, one, default)

    def success(q, a):
        return overlap(branches[a], q) + overlap(tail, 1 - q)

    breaks = {F(0), F(1)}
    for i, parts in enumerate([*branches, tail]):
        x = F(0)
        for _, width in parts:
            x += width
            if x < 1:
                breaks.add(1 - x if i == 2 else x)
    points = sorted(breaks)
    for l, r in pairwise(points):
        g, h = (success(v, 0) - success(v, 1) for v in (l, r))
        if g * h < 0:
            breaks.add(l + (r - l) * g / (g - h))
    specific = max(1 - max(success(q, a) for q in breaks) for a in (0, 1))
    shared = 1 - max(min(success(q, a) for a in (0, 1)) for q in breaks)
    mixed = 1 - max((success(q, 0) + success(q, 1)) / 2 for q in breaks)
    assert (specific, shared, mixed) == (F(17, 36), F(35, 72), F(35, 72))
    assert min(success(F(3, 8), a) for a in (0, 1)) == 1 - shared
    return specific, shared, mixed


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    print(
        "final statistics, local terminal policies, binary cut spectra", finite_optima()
    )
    print("union bounds on any erroneous routing matrix", acquisition_bound())
    print(
        "policy-specific pure, shared, and private mixed full-transcript deficits",
        causal_comparison(),
    )
