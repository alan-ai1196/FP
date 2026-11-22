"""Exact small learning controls and outward log-loss bounds for the frozen readout pair."""

import argparse
import json
from fractions import Fraction as F
from itertools import pairwise, product
from math import gcd, log, prod
from pathlib import Path

import numpy as np
from mixture_addresses import SUBPANEL, replication_data, starts, train
from text import SCALE, outward, ratio_log
from text_addresses import CAL, TOTAL_MASS


def logs(x, y):
    if x == y:
        return 0, 0
    divisor = gcd(x, y)
    return ratio_log(x // divisor, y // divisor)


def bern_kl(p, q):
    a = p / q
    b = (1 - p) / (1 - q)
    first = logs(a.numerator, a.denominator)
    second = logs(b.numerator, b.denominator)
    return tuple((p * first[j] + (1 - p) * second[j]) / SCALE for j in (0, 1))


def check_precision():
    verified = sharp = 0
    for m in (2, 3, 8, 32):
        for low, high in product((F(1, m), F(m + 1, 2 * m)), (F(m), F(m + 1, 2))):
            # A binary alphabet realizes these two likelihood ratios exactly.
            d0 = (1 - low) / (high - low)
            d1 = high * d0
            assert 0 < d0 < d1 < 1 and (1 - d1) / (1 - d0) == low
            for iw in range(1, 12):
                w = F(iw, 12)
                p = (1 - w) * d0 + w * d1
                t = (1 + (m - 1) * w) / (m + 1)
                for iv in range(13):
                    v = F(iv, 12)
                    q = (1 - v) * d0 + v * d1
                    s = (1 + (m - 1) * v) / (m + 1)
                    observed = bern_kl(p, q)
                    ceiling = bern_kl(t, s)
                    if low == F(1, m) and high == m:
                        assert observed == ceiling
                        sharp += 1
                    elif w != v:
                        assert observed[1] < ceiling[0]
                    else:
                        assert observed == ceiling == (0, 0)
                    verified += 1
    return verified, sharp


def check_purchase():
    grid = [F(k, 4) for k in range(5)]
    d0, d1 = F(1, 5), F(4, 5)
    prob = [(1 - w) * d0 + w * d1 for w in grid]
    base = [0, 4, 2]
    rules = list(product(range(5), repeat=3))
    checked = 0
    for positives in product((0, 2, 4), repeat=3):
        likelihood = [[p**n * (1 - p) ** (4 - n) for p in prob] for n in positives]
        savings = []
        for i, row in enumerate(likelihood):
            best = max(range(5), key=lambda j: row[j])
            savings.append(row[best] / row[base[i]] / 2)
        for k in range(4):
            chosen = sorted((x for x in savings if x > 1), reverse=True)[:k]
            value = prod(chosen)
            oracle = max(
                prod(
                    likelihood[i][j]
                    / likelihood[i][base[i]]
                    / (2 if j != base[i] else 1)
                    for i, j in enumerate(rule)
                )
                for rule in rules
                if sum(j != b for j, b in zip(rule, base, strict=True)) <= k
            )
            assert value == oracle
            checked += 1
    r = (F(2), F(1, 2), F(1))
    for truth, interior in [
        ((F(15, 100), F(5, 100), F(80, 100)), False),
        ((F(35, 100), F(25, 100), F(40, 100)), True),
    ]:
        assert truth[0] - truth[1] == F(1, 10)
        assert (
            sum(a * b for a, b in zip(truth, r, strict=True)) > 1
            and sum(a / b for a, b in zip(truth, r, strict=True)) > 1
        ) == interior
    return checked


def grid_radius(m, intervals):
    """At each cell's worst point its divergences to the two endpoints agree."""
    levels = [(1 + (m - 1) * F(k, intervals)) / (m + 1) for k in range(intervals + 1)]
    radius = 0.0
    for left, right in pairwise(levels):
        a = log((1 - left) / (1 - right))
        p = a / (a + log(right / left))
        radius = max(radius, p * log(p / left) + (1 - p) * log((1 - p) / (1 - left)))
    return radius


def text_checks(data):
    fitted, model, _, _ = train(data)
    c, pair = fitted.common, fitted.pair
    tokens = np.frombuffer(data, dtype=np.uint16)

    def terms(q, y):
        j = int(c.category[y])
        num, tail = (int(c.unigram[y]), c.tail) if j == len(c.top) else (1, 1)
        denominator = TOTAL_MASS * tail
        seen = c.rows.pairs[q, y] * denominator
        return (
            seen + 64 * int(pair[0, j]) * num,
            seen + 64 * int(pair[1, j]) * num,
            (c.rows.outgoing[q] + 64) * denominator,
        )

    normalization = 0
    for q in np.argsort(c.outgoing)[[0, len(c.outgoing) // 2, -1]].tolist():
        common_den = 4 * TOTAL_MASS * c.tail * (c.rows.outgoing[q] + 64)
        sums = [0] * 5
        for y in range(c.vocab):
            left, right, den = terms(q, y)
            scale, remain = divmod(common_den, 4 * den)
            assert remain == 0
            for w in range(5):
                sums[w] += scale * ((4 - w) * left + w * right)
        assert sums == [common_den] * 5
        normalization += len(sums)

    bounds = []
    # Each interior type gets a separate hindsight choice of either endpoint.
    relative = {
        int(u): [[0, 0], [0, 0]]
        for u in np.flatnonzero((model.levels > 0) & (model.levels < 4))
    }
    events = 0
    for start in starts():
        lo = hi = 0
        for i in range(start, start + CAL):
            u = int(tokens[i - 2])
            inside = u in relative
            if not inside and i >= start + SUBPANEL:
                continue
            left, right, den = terms(int(tokens[i - 1]), int(tokens[i]))
            if i < start + SUBPANEL:
                l, h = logs(den, max(left, right))
                lo += l
                hi += h
            if inside:
                events += 1
                w = int(model.levels[u])
                extension = (4 - w) * left + w * right
                for j, reference in enumerate((left, right)):
                    l, h = logs(extension, 4 * reference)
                    relative[u][j][0] += l
                    relative[u][j][1] += h
        bounds.append((lo, hi))
    gains = [
        tuple(min(row[b] for row in two) for b in (0, 1)) for two in relative.values()
    ]
    positive = sum(v[0] > 0 for v in gains)
    assert all(lo > 0 or hi < 0 or (lo == 0 and hi == 0) for lo, hi in gains)
    max_ratio = max(
        F(max(int(a), int(b)), min(int(a), int(b))) for a, b in zip(*pair, strict=True)
    )
    return {
        "exact_backoff_ratio_bound": str(max_ratio),
        "five_level_worst_case_radius_from_bound": round(grid_radius(max_ratio, 4), 12),
        "full_alphabet_exact_normalizations": normalization,
        "subpanel_pair_envelope_block_nll": [outward(b, SUBPANEL) for b in bounds],
        "subpanel_pair_envelope_mean_nll": outward(
            tuple(map(sum, zip(*bounds, strict=True))), SUBPANEL * len(bounds)
        ),
        "interior_types": len(relative),
        "interior_targets": events,
        "interior_beats_both_pure_types": positive,
        "hindsight_hard_excess_on_fixed_interior_types_total_nats": outward(
            tuple(map(sum, zip(*gains, strict=True))), 1
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    tests, sharp = check_precision()
    result = {
        "normalized_precision_examples": tests,
        "extremal_equalities": sharp,
        "exact_small_purchases": check_purchase(),
    }
    if args.text:
        result["text"] = text_checks(replication_data(args.data_dir))
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    report = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(report, encoding="utf8")
    elif not args.check:
        print(report, end="")
