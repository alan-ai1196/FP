"""Rational checks for residual-driven corrections, normalization and maximum-cut slopes."""

from fractions import Fraction as F
from itertools import combinations, product
from math import log
from random import Random

from text import SCALE, ratio_log


def logged(x):
    return tuple(F(y, SCALE) for y in ratio_log(x.numerator, x.denominator))


def normalized(values):
    return [F(v, sum(values)) for v in values]


def dot(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True))


def check_table(rng):
    histories, queries, outcomes = 3, 2, 5
    mass = normalized([rng.randrange(1, 9) for _ in range(histories)])
    truth, base = {}, {}
    for u, q in product(range(histories), range(queries)):
        truth[u, q] = normalized([rng.randrange(1, 16) for _ in range(outcomes)])
        base[u, q] = normalized([rng.randrange(1, 16) for _ in range(outcomes)])
    residual = [
        [
            sum(truth[u, q][y] - base[u, q][y] for q in range(queries)) / queries
            for y in range(outcomes)
        ]
        for u in range(histories)
    ]
    current = [F(0)] * histories
    direction = []
    for y in range(outcomes):
        sign = (
            1
            if sum(mass[u] * current[u] * residual[u][y] for u in range(histories)) >= 0
            else -1
        )
        direction.append(sign)
        current = [v + sign * row[y] for v, row in zip(current, residual, strict=True)]
    assert dot(mass, [v * v for v in current]) >= sum(
        mass[u] * dot(row, row) for u, row in enumerate(residual)
    )
    floor = ceiling = F(0)
    step = tuple(v / 2 for v in logged(F(2)))
    any_step = False
    for u, s in enumerate(current):
        k = round(2 * float(s) / log(2))
        any_step |= k != 0
        group_factor = F(2) ** k
        h_lo, h_hi = sorted(k * v for v in step)
        closest = 0 if h_lo <= 0 <= h_hi else min(abs(h_lo), abs(h_hi))
        # Upper endpoint of the asserted lower bound. A disjoint interval certifies it.
        ceiling += mass[u] * (max(s * h_lo, s * h_hi) - closest**2 / 2)
        for q in range(queries):
            scaled = [
                p * (group_factor if sign == 1 else 1)
                for p, sign in zip(base[u, q], direction, strict=True)
            ]
            z = sum(scaled)
            assert sum(v / z for v in scaled) == 1
            for ref, obs, new in zip(base[u, q], truth[u, q], scaled, strict=True):
                floor += mass[u] * obs * logged(new / (z * ref))[0] / queries
    assert floor >= ceiling or not any_step
    return any_step


def graph_checks():
    count = exhaust = 0
    for n in (3, 4):
        edges = list(combinations(range(n), 2))
        for mask in range(1, 1 << len(edges)):
            active = [e for i, e in enumerate(edges) if mask >> i & 1]
            cut = max(
                sum(bits[i] != bits[j] for i, j in active)
                for bits in product((0, 1), repeat=n)
            )
            oriented = [(a, b) for i, j in active for a, b in ((i, j), (j, i))]
            eps = F(1, 2 * n)
            ordinary = [
                [F(1, n) + eps * (int(y == i) - int(y == j)) for y in range(n)]
                for i, j in oriented
            ]
            assert all(sum(row) == 1 and min(row) > 0 for row in ordinary)
            residual = [[p - F(1, n) for p in row] for row in ordinary]
            assert all(sum(col) == 0 for col in zip(*residual, strict=True))
            best = F(0)
            for b in product((-1, 1), repeat=n):
                gains = [dot(row, b) for row in residual]
                by_address = sum(abs(v) for v in gains)
                if n == 3:
                    assert by_address == max(
                        dot(a, gains) for a in product((-1, 1), repeat=len(gains))
                    )
                    exhaust += 1
                best = max(best, by_address / len(oriented))
            assert best == 2 * eps * cut / len(active)
            count += 1
    return count, exhaust


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    rng = Random(1729)
    changed = sum(check_table(rng) for _ in range(128))
    graphs, exhaust = graph_checks()
    print(
        f"128 positive tables, {changed} nonzero quantized moves, {graphs} graph channels, {exhaust} exhaustive sign fits"
    )
