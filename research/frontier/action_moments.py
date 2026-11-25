"""Recover two-state deterministic actions and emission rows from stationary raw token triples."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import isqrt, log
from pathlib import Path

import numpy as np
from action_cut import step
from categorical_assignment import quantize
from raw_word_action import Q16, native, states


def stationary(a, p):
    rise = sum(p[0][k] for k, op in enumerate(a) if step(op, 0))
    fall = sum(p[1][k] for k, op in enumerate(a) if not step(op, 1))
    if not (rise or fall):
        return F(2, 5)
    return F(rise, rise + fall)


def word_mass(a, p, q, w):
    mass = [1 - q, q]
    for v in w:
        new = [0, 0]
        for s in (0, 1):
            new[step(a[v], s)] += mass[s] * p[s][v]
        mass = new
    return sum(mass)


def swapped(a):
    return tuple(1 - v if v < 2 else v for v in a)


def rational_sqrt(x):
    r = F(isqrt(x.numerator), isqrt(x.denominator))
    assert r * r == x
    return r


def recover(mu, pair, triple):
    d = len(mu)
    names = range(d)
    k = {(c, b): pair[c, b] - mu[c] * mu[b] for c, b in product(names, repeat=2)}
    c, b = max(k, key=lambda ab: abs(k[ab]))
    assert k[c, b]
    coeff = [
        (mu[a] * triple[c, a, b] - pair[c, a] * pair[a, b]) / k[c, b] for a in names
    ]
    a = [2 if v > 0 else 3 if v < 0 else 0 for v in coeff]
    cond = lambda last: tuple(pair[last, j] / mu[last] for j in names)
    resets = [v for v in names if coeff[v] == 0]
    if resets:
        ordered = sorted(resets, key=lambda v: cond(v)[b])
        low = ordered[0]
        p0, p1 = cond(low), cond(ordered[-1])
        if p1 == p0:
            flipper = a.index(3)
            p1 = tuple(triple[low, flipper, j] / pair[low, flipper] for j in names)
        for v in resets:
            a[v] = int(cond(v) != p0)
    else:
        w = [k[c, j] / k[c, b] for j in names]
        i, j = next(v for v in names if w[v] < 0), b

        def point(v):
            return mu[v] / w[v], (abs(coeff[v]) - mu[v] ** 2) / (w[v] ** 2)

        xi, yi = point(i)
        xj, yj = point(j)
        total = (yi - yj) / (xi - xj)
        prod = yi - xi * total
        gap = rational_sqrt(total**2 - 4 * prod)
        p0, p1 = (
            tuple(mu[v] + t * w[v] for v in names)
            for t in ((total - gap) / 2, (total + gap) / 2)
        )
    q = (mu[b] - p0[b]) / (p1[b] - p0[b])
    return tuple(a), (p0, p1), q, coeff, (c, b)


def moments(a, p, q):
    names = range(len(a))

    def block(k):
        return {w: word_mass(a, p, q, w) for w in product(names, repeat=k)}

    return tuple(word_mass(a, p, q, (i,)) for i in names), block(2), block(3)


def exact():
    fits = filters = synchronization = 0
    for d in (2, 3):
        names = range(d)
        total = d * (d + 1) // 2
        p0 = tuple(F(i + 1, total) for i in names)
        p = p0, tuple(reversed(p0))
        for a in product(range(4), repeat=d):
            q = stationary(a, p)
            if not 0 < q < 1:
                continue
            mu, pairs, triples = moments(a, p, q)
            got, rows, initial, coeff, (c, b) = recover(mu, pairs, triples)
            assert (got, rows, initial) in ((a, p, q), (swapped(a), p[::-1], 1 - q))
            assert all(
                coeff[i] == (0, 0, 1, -1)[op] * p[0][i] * p[1][i]
                for i, op in enumerate(a)
            )
            # Reconstruct out-of-sample word probabilities using only observed moments.
            delta = pairs[c, b] / mu[c] - mu[b]
            linear = [(pairs[c, i] / mu[c] - mu[i]) / delta for i in names]
            joint = [(triples[c, i, b] / mu[c] - pairs[i, b]) / delta for i in names]
            for w in product(names, repeat=4):
                mass, forecast = 1, mu[b]
                for i in w:
                    chance = mu[i] + (forecast - mu[b]) * linear[i]
                    following = (pairs[i, b] + (forecast - mu[b]) * joint[i]) / chance
                    forecast, mass = following, mass * chance
                assert mass == word_mass(a, p, q, w)
                filters += 1
            fits += 1
    # Every remaining square root for this binary family is a rational number.
    p = (F(9, 25), F(16, 25)), (F(16, 25), F(9, 25))
    for a in product(range(4), repeat=2):
        q = stationary(a, p)
        if not 0 < q < 1:
            continue
        mu, pairs, triples = moments(a, p, q)
        coeff = recover(mu, pairs, triples)[3]
        factor = sum(rational_sqrt(abs(v)) for v in coeff)
        for length in range(8):
            overlap = F(0)
            for w in product(range(2), repeat=length):
                if all(a[v] >= 2 for v in w):
                    overlap += rational_sqrt(
                        word_mass(a, p, F(0), w) * word_mass(a, p, F(1), w)
                    )
            assert overlap == factor**length
            synchronization += 1
    p = (F(5, 8), F(3, 8)), (F(1, 4), F(3, 4))
    cases = [
        ((2, 3), p),
        ((3, 2), tuple(row[::-1] for row in p)),
        ((0, 1), ((F(9, 16), F(7, 16)), (F(7, 16), F(9, 16)))),
    ]
    blocks = [moments(a, p, stationary(a, p)) for a, p in cases]
    assert all(
        list(x[1].values()) == [F(9, 32), F(7, 32), F(7, 32), F(9, 32)] for x in blocks
    )
    assert len({tuple(x[2].values()) for x in blocks}) == 3
    return {
        "exact_model_recoveries": fits,
        "four_word_filter_checks": filters,
        "exact_overlap_horizons": synchronization,
        "identical_pair_distinct_triple_sources": 3,
    }


SIZES = (4096, 32768, 131072)
SOURCES = (
    ("four_actions", (0, 1, 2, 3), ((6, 2, 5, 3), (2, 6, 3, 5))),
    ("one_reset_destination", (0, 0, 2, 3), ((6, 2, 5, 3), (2, 6, 3, 5))),
    ("permutations", (2, 2, 3, 3), ((6, 2, 4, 4), (2, 6, 4, 4))),
)


def draw(rng, n, table, counts):
    q = stationary(table, counts.tolist())
    s = int(rng.random() < q)
    uniforms = rng.integers(16, size=n)
    possible = np.array(
        [np.searchsorted(np.cumsum(row), uniforms, side="right") for row in counts]
    )
    result = np.empty(n, dtype=np.uint16)
    for i in range(n):
        v = possible[s, i]
        result[i] = v
        s = step(table[v], s)
    return result


def nominees(x):
    d = 4
    ct = np.bincount(d * d * x[:-2] + d * x[1:-1] + x[2:], minlength=d**3).reshape(
        d, d, d
    )
    pair = ct.sum(axis=0)
    covariance = (
        pair / pair.sum()
        - np.outer(pair.sum(axis=1), pair.sum(axis=0)) / pair.sum() ** 2
    )
    c, b = np.unravel_index(np.abs(covariance).argmax(), covariance.shape)
    out = set()
    for z in (0.5, 2, 4, 8):
        a, unknown = [0] * d, []
        for v in range(d):
            n1, n0 = ct[c, v].sum(), pair[v].sum() - ct[c, v].sum()
            avg = pair[v, b] / max(1, pair[v].sum())
            counts = ct[c, v, b]
            if n0 and n1:
                diff = counts / n1 - (pair[v, b] - counts) / n0
                threshold = z * np.sqrt(avg * (1 - avg) * (1 / n0 + 1 / n1))
                if abs(diff) > threshold:
                    a[v] = 2 if diff * covariance[c, b] > 0 else 3
                    continue
            unknown.append((avg, v))
        ordered = [v for _, v in sorted(unknown)]
        for split in range(len(ordered) + 1):
            for i, v in enumerate(ordered):
                a[v] = int(i >= split)
            out.update((tuple(a), swapped(a)))
    return out


def visits(lib, a, x, start):
    path = states(lib, 0, a, x, start)
    before = np.empty(len(x), dtype=np.uint16)
    before[0], before[1:] = start, path[:-1]
    return 4 * before + x


def heads(ct):
    return np.stack([quantize(row + 0.5) for row in ct])


def marginal_nll(rows, trials):
    joint = trials @ np.log(rows.ravel() / Q16)
    return float(log(2) - np.logaddexp(joint[0], joint[1]))


def markov_loss(x, test, order):
    # On each fresh sequence back off at the first one or two words.
    loss = 0.0
    for depth in range(order + 1):
        t = np.zeros(len(x) - depth, dtype=np.int32)
        v = np.zeros(len(test) - depth, dtype=np.int32)
        for j in range(depth):
            t = 4 * t + x[j : len(x) - depth + j]
            v = 4 * v + test[j : len(test) - depth + j]
        ct = np.bincount(4 * t + x[depth:], minlength=4 ** (depth + 1)).reshape(-1, 4)
        rows = heads(ct)
        stop = len(v) if depth == order else 1
        loss -= float(np.log(rows[v[:stop], test[depth : depth + stop]] / Q16).sum())
    return loss / len(test)


def tested_runs(lib, restricted=False):
    bank = list(product(range(4), repeat=4))
    output = []
    passes = 0
    for family, (name, truth, p) in enumerate(SOURCES):
        for seed in range(6):
            rng = np.random.default_rng([20261126, family, seed])
            perm = rng.permutation(4)
            a = tuple(truth[j] for j in perm)
            raw = np.array(p)[:, perm]
            x, val, test = (draw(rng, n, a, raw) for n in (SIZES[-1], 8192, 16384))
            candidates = [nominees(x[:n]) for n in SIZES]
            evaluated = [{} for _ in SIZES]
            available = sorted(set.union(*candidates)) if restricted else bank
            for t in available:
                action = np.array(t, dtype=np.uint8)
                sizes = [
                    (i, n)
                    for i, n in enumerate(SIZES)
                    if not restricted or t in candidates[i]
                ]
                stop = sizes[-1][1]
                coded = visits(lib, action, x[:stop], 0)
                passes += stop + 2 * len(val)
                validation = np.stack(
                    [
                        np.bincount(visits(lib, action, val, s), minlength=8)
                        for s in (0, 1)
                    ]
                )
                for i, n in sizes:
                    rows = heads(np.bincount(coded[:n], minlength=8).reshape(2, 4))
                    evaluated[i][t] = (marginal_nll(rows, validation), rows)
            for i, n in enumerate(SIZES):
                info = {
                    "source": name,
                    "repeat": seed,
                    "words": n,
                    "moment_candidates": len(candidates[i]),
                    "truth": a,
                    "markov_nll": [markov_loss(x[:n], test, o) for o in range(3)],
                }
                for algorithm, menu in (
                    ("moments", candidates[i]),
                    ("exhaustive", bank),
                ):
                    if restricted and algorithm == "exhaustive":
                        continue
                    selected = min(menu, key=lambda t: (evaluated[i][t][0], t))
                    action = np.array(selected, dtype=np.uint8)
                    reporting = np.stack(
                        [
                            np.bincount(visits(lib, action, test, s), minlength=8)
                            for s in (0, 1)
                        ]
                    )
                    info[algorithm] = {
                        "table": selected,
                        "recovered": selected in (a, swapped(a)),
                        "report_nll": marginal_nll(evaluated[i][selected][1], reporting)
                        / len(test),
                    }
                output.append(info)
    return {
        "registration": "1f9a9cf",
        "training_and_validation_state_steps": passes,
        "records": output,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--moments-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        result = exact()
    else:
        with native() as lib:
            result = tested_runs(lib, args.moments_only)
    s = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(s.encode())
    else:
        print(s, end="")


if __name__ == "__main__":
    main()
