"""Independent finite channel laws, visibility of tasks, and physical read designs."""

import argparse
import json
import subprocess
import sys
from fractions import Fraction as F
from functools import cache
from io import BytesIO
from itertools import combinations, pairwise, product
from math import comb, log, prod
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import mpmath as mp
import numpy as np
import sympy as sp
from affine_reports import likelihoods, parse_model
from positive_comparison import SOURCE, categorical_program


def conditional(reads, ones, bit, rho):
    probability_one = (1 + (2 * bit - 1) * rho) / 2
    return (
        comb(reads, ones)
        * probability_one**ones
        * (1 - probability_one) ** (reads - ones)
    )


@cache
def posteriors(m, rho):
    law = []
    for hits in range(m + 1):
        plus, minus = (conditional(m, hits, b, rho) for b in (0, 1))
        law.append(((plus + minus) / 2, (plus - minus) / (plus + minus)))
    return law


@cache
def exposure(m, rho):
    return sum(p * b * b for p, b in posteriors(m, rho))


def direct_likelihood():
    checks = 0
    rho = F(1, 2)
    for m in (1, 3):
        for obs in product(range(m + 1), repeat=3):
            x = np.array([obs[:2]], dtype=np.uint8)
            y = np.array(obs[-1:], dtype=np.uint8)
            computed = likelihoods(x, y, m)
            null = prod(posteriors(m, rho)[n][0] for n in obs)
            for mask in range(4):
                for offset in (0, 1):
                    total = F(0)
                    for a in range(4):
                        latent = (
                            a & 1,
                            (a >> 1) & 1,
                            ((mask & a).bit_count() + offset) % 2,
                        )
                        total += (
                            prod(
                                conditional(m, n, b, rho)
                                for n, b in zip(obs, latent, strict=True)
                            )
                            / 4
                        )
                    assert abs(computed[offset, mask] - log(total / null)) < 2e-13
                    checks += 1
    return checks


def signs(d):
    return list(product((1, -1), repeat=d))


def character(row, mask):
    return prod(x for i, x in enumerate(row) if mask & (1 << i))


def direct_gram(schedule, rho):
    d = len(schedule)
    hidden = signs(d)
    characters = [[character(row, s) for s in range(1 << d)] for row in hidden]
    result = [[0 for _ in characters[0]] for _ in characters[0]]
    for count in product(*(range(m + 1) for m in schedule)):
        joint = [
            prod(
                conditional(m, y, int(x == -1), rho)
                for m, y, x in zip(schedule, count, row, strict=True)
            )
            / len(hidden)
            for row in hidden
        ]
        total = sum(joint)
        mean = [
            sum(w * cs[s] for w, cs in zip(joint, characters, strict=True)) / total
            for s in range(1 << d)
        ]
        for i in range(1 << d):
            for j in range(1 << d):
                result[i][j] += total * mean[i] * mean[j]
    for s in range(1 << d):
        for t in range(1 << d):
            expect = (
                prod(exposure(m, rho) for i, m in enumerate(schedule) if s & (1 << i))
                if s == t
                else 0
            )
            assert result[s][t] == expect
    return result


def balanced_and_adaptive():
    minimum = {}
    comparisons = 0
    for rho in (F(1, 10), F(1, 2), F(3, 4), F(9, 10), F(99, 100)):
        values = [exposure(m, rho) for m in range(18)]
        second = [2 * v - u - w for u, v, w in zip(values, values[1:], values[2:])]
        assert min(second) > 0
        minimum[str(rho)] = float(min(second))
    rho = F(1, 2)
    n = 4

    def weights(allocation):
        a = [exposure(m, rho) for m in allocation]
        return [
            sum(prod(v) for v in combinations(a, k)) / comb(n, k)
            for k in range(1, n + 1)
        ]

    for cap in range(11):
        balanced = [cap // n + int(i < cap % n) for i in range(n)]
        optimum = weights(balanced)
        for allocation in combinations(range(cap + n - 1), n - 1):
            ends = (-1, *allocation, cap + n - 1)
            counts = [b - a - 1 for a, b in pairwise(ends)]
            score = weights(counts)
            assert all(v <= target for v, target in zip(score, optimum, strict=True))
            comparisons += len(score)

    # Full direct read-path enumeration for the four-purchase repair policy.
    value = F(0)
    for z in signs(4):
        ix = [0, 0, 1, 0 if z[0] != z[1] else 1]
        rows = [
            prod((1 + rho * x[i] * out) / 2 for i, out in zip(ix, z, strict=True)) / 4
            for x in signs(2)
        ]
        p = sum(rows)
        posterior = sum(w * prod(x) for w, x in zip(rows, signs(2), strict=True)) / p
        value += p * posterior**2
    fixed = exposure(2, rho) ** 2
    assert value == fixed + (1 - rho**2) * rho**4 / 2
    return {
        "strict_concavity_min_gap": minimum,
        "allocation_comparisons": comparisons,
        "four_read_fixed": str(fixed),
        "four_read_adaptive": str(value),
    }


def gain(bias):
    return ((1 + bias) * np.log1p(bias) + (1 - bias) * np.log1p(-bias)) / 2


def log_design_checks():
    def mpq(x):
        return mp.mpf(x.numerator) / x.denominator

    tested = 0
    with mp.workdps(75):
        for r in (F(1, 10), F(1, 2), F(3, 4), F(9, 10), F(99, 100)):
            for target in (F(1, 10), F(1, 2), F(9, 10), F(99, 100), F(1)):
                values = []
                for m in range(18):
                    total = mp.mpf(0)
                    for mass, bias in posteriors(m, r):
                        v = mpq(target * bias)
                        total += (
                            mpq(mass)
                            * ((1 + v) * mp.log1p(v) + (1 - v) * mp.log1p(-v))
                            / 2
                        )
                    values.append(total)
                assert all(
                    2 * v > u + w for u, v, w in zip(values, values[1:], values[2:])
                )
                tested += len(values) - 2

    @cache
    def subset_gain(counts):
        result = 0.0
        for views in product(*(posteriors(m, F(1, 2)) for m in counts)):
            p = prod(v[0] for v in views)
            bias = prod(v[1] for v in views)
            result += float(p) * gain(float(bias) / 2)
        return result

    comparisons = 0
    n = 3
    for limit in range(10):
        balanced = [limit // n + int(i < limit % n) for i in range(n)]
        for ends in combinations(range(limit + n - 1), n - 1):
            depths = [j - i - 1 for i, j in pairwise((-1, *ends, limit + n - 1))]
            for k in range(1, n + 1):
                lhs = sum(
                    subset_gain(tuple(sorted(s))) for s in combinations(depths, k)
                )
                rhs = sum(
                    subset_gain(tuple(sorted(s))) for s in combinations(balanced, k)
                )
                assert lhs <= rhs + 1e-13
                comparisons += 1
    return {
        "scalar_second_differences": tested,
        "precision_digits": 75,
        "hard_log_gain_comparisons": comparisons,
    }


def two_read_information():
    r, t, b = sp.symbols("r t b")
    R, T = r**2, t**2
    x = b**2
    y = x / (1 - x)
    p, q = 1 - R, 1 - T
    poly = (
        (1 - R * T) * (2 - R - T)
        + p * q * (3 * R + 3 * T - 2 * R * T) * y
        - 6 * p**2 * q**2 * y**2
        - 4 * p**2 * q**2 * y**3
    )
    factors = [(1 + z * r * t) ** 2 - x * (r + z * t) ** 2 for z in (-1, 1)]
    denominator = (1 - R * x) * (1 - T * x) * prod(factors)
    second = (
        R / (1 - R * x)
        + T / (1 - T * x)
        - sum(
            (1 + z * r * t) * (r + z * t) ** 2 / (2 * factor)
            for z, factor in zip((-1, 1), factors, strict=True)
        )
    )
    assert sp.cancel(second - R * T * (1 - x) ** 3 * poly / denominator) == 0


def feedback_design():
    rho = F(1, 2)
    kappa = F(1, 2)

    def values(b):
        return b * b, gain(float(kappa * b))

    def fixed(left, right):
        outcomes = [
            (p * q, b * c)
            for p, b in posteriors(left, rho)
            for q, c in posteriors(right, rho)
        ]
        return tuple(sum(p * values(b)[j] for p, b in outcomes) for j in (0, 1))

    @cache
    def highest(margins, remaining, criterion):
        odds = (1 + rho) / (1 - rho)
        local = [(odds**j - 1) / (odds**j + 1) for j in margins]
        if not remaining:
            return values(prod(local))[criterion]
        candidates = []
        for i, j in enumerate(margins):
            align = (1 + rho * local[i]) / 2
            rest = list(margins)
            rest.pop(i)
            upward = tuple(sorted([*rest, j + 1]))
            down = tuple(sorted([*rest, abs(j - 1)]))
            candidates.append(
                align * highest(upward, remaining - 1, criterion)
                + (1 - align) * highest(down, remaining - 1, criterion)
            )
        return max(candidates)

    rows = [fixed(i, 4 - i) for i in range(5)]
    best = max(v[0] for v in rows), max(v[1] for v in rows)
    adaptive = [highest((0, 0), 4, j) for j in (0, 1)]
    assert best == rows[2] and adaptive[0] == F(587, 3200)
    assert abs(adaptive[1] - best[1] - 3 / 8 * gain(1 / 8)) < 1e-14
    return {
        "best_fixed_energy": str(best[0]),
        "best_adaptive_energy": str(adaptive[0]),
        "best_fixed_log_gain": float(best[1]),
        "best_adaptive_log_gain": float(adaptive[1]),
    }


def run():
    two_read_information()
    gram = direct_gram((0, 1, 3), F(1, 2))
    other = direct_gram((2, 2, 1), F(3, 4))
    # Observe x1, then observe x2 exactly only when x1=+1.
    proj = [(F(1, 4), 1, 1), (F(1, 4), -1, -1), (F(1, 2), 0, 0)]
    adaptive_cross = sum(p * b * c for p, b, c in proj)
    assert adaptive_cross == F(1, 2)
    r = F(1, 2)
    high = 2 * r / (1 + r * r)
    mass = r * r / (high * high)
    assert mass * high**2 == r * r
    kl1, kl2 = gain(0.5 * float(r)), float(mass) * gain(0.5 * float(high))
    assert kl2 > kl1
    return {
        "direct_likelihood_checks": direct_likelihood(),
        "exact_gram_diagonals": [
            [str(g[i][i]) for i in range(len(g))] for g in (gram, other)
        ],
        "adaptive_cross_term": str(adaptive_cross),
        "equal_energy_log_gains": [kl1, kl2],
        "optimal_feedback_design": feedback_design(),
        "log_gain_design": log_design_checks(),
        **balanced_and_adaptive(),
    }


def r4_table(d, mask, offset):
    states = [(0, offset)]
    index = {states[0]: 0}
    table, probs = [], []
    amplitude = F(1, 2) ** (mask.bit_count() + 1)
    for j, bit in states:
        p = (1 - (-1) ** bit * amplitude) / 2 if j == d - 1 else F(1, 2)
        probs.append(p)
        row = []
        for observed in (0, 1):
            nxt = (0, offset) if j == d - 1 else (j + 1, bit ^ ((mask >> j) & observed))
            if nxt not in index:
                index[nxt] = len(states)
                states.append(nxt)
            row.append(index[nxt])
        table.append(row)
    slots, heads = [F(1)], [[], []]
    for i, p in enumerate(probs):
        for head, prob in zip(heads, (1 - p, p), strict=True):
            excess = 4 * prob - 1
            assert excess >= 0
            if excess not in slots:
                slots.append(excess)
            head.append((i, slots.index(excess)))
    event, start, stats = categorical_program(("0", "1"), table, heads, slots)
    reached = {0: start}
    assert start.probabilities[1] == probs[0]
    for i, row in enumerate(table):
        for symbol, dest in enumerate(row):
            after = event(str(symbol), reached[i].delayed)
            assert after.probabilities[1] == probs[dest]
            assert tuple(v[0] for _, v in after.delayed) == tuple(
                int(h == dest) for h in range(len(table))
            )
            reached.setdefault(dest, after)
    assert len(reached) == len(table)
    return {
        "dimension": d,
        "states": len(table),
        "tested_events": 1 + 2 * len(table),
        **stats,
    }


def r4():
    here = Path(__file__).resolve().parent
    source = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, source]
    )
    panels = json.loads((here / "affine_reports_result.json").read_text())["panels"]
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / source))
        return [
            r4_table(
                p["d"],
                *parse_model(
                    next(
                        f["fits"]["elimination"]["model"]
                        for f in p["acquisition"]
                        if f["fits"]["elimination"]["correct"]
                    )
                ),
            )
            for p in panels
            if p["seed"] == 173
        ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r4", action="store_true")
    args = parser.parse_args()
    print(json.dumps(r4() if args.r4 else run(), indent=2))
