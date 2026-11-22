"""Acquire a shared internal alphabet by ordinary causal window likelihood."""

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path

import numpy as np
from text import log_bounds, outward, ratio_log

V = 6
N = 262144
REPORT = 65536
TRUE = (0, 1, 2, 3, 1, 2)
WORDS = list(product(range(V), repeat=3))


def sample_columns(n, length, seed):
    rng = np.random.Generator(np.random.PCG64(seed))
    state = rng.integers(2, size=n, dtype=np.uint8)
    neutral = np.array([1, 4, 2, 5, 0, 0, 0, 0], dtype=np.uint8)
    for _ in range(length):
        event = rng.integers(8, size=n, dtype=np.uint8)
        symbol = np.where(
            event < 4, neutral[event], np.where(event < 7 - 2 * state, 0, 3)
        )
        state ^= (event == 2) | (event == 3)
        yield symbol


def draw(n, seed):
    code = np.zeros(n, dtype=np.int32)
    for symbol in sample_columns(n, 3, seed):
        code = V * code + symbol
    return np.bincount(code, minlength=V**3).reshape((V,) * 3)


def partitions(labels=(0,)):
    if len(labels) == V:
        yield labels
    else:
        for cell in range(max(labels) + 2):
            yield from partitions((*labels, cell))


def cells(observed, mapping):
    length = observed.ndim
    k = 1 + max(mapping)
    indices = np.asarray(list(product(mapping, repeat=length)), dtype=np.int32)
    codes = np.ravel_multi_index(indices.T, (k,) * length)
    result = np.zeros(k**length, dtype=np.int64)
    np.add.at(result, codes, observed.ravel())
    return result.reshape((k,) * length)


def raw_counts(observed):
    return sum(
        observed.sum(axis=tuple(j for j in range(observed.ndim) if j != i))
        for i in range(observed.ndim)
    )


def coding_cost(observed, raw, mapping):
    coarse = cells(observed, mapping)
    n = int(observed.sum())
    k = 1 + max(mapping)
    # Twice the fitted negative log likelihood plus the BIC charge, in log integers.
    df = k**observed.ndim - 1 + V - k
    exponents = Counter({n: 2 * n + df})
    group = [0] * k
    for a, c in enumerate(mapping):
        group[c] += int(raw[a])
    for value in group:
        exponents[value] += 2 * value
    for value in (*coarse.flat, *raw):
        value = int(value)
        exponents[value] -= 2 * value
    lo = hi = 0
    for value, power in exponents.items():
        if power:
            l, h = log_bounds(value)
            lo += power * (l if power > 0 else h)
            hi += power * (h if power > 0 else l)
    return (lo, hi), exponents


def lower(left, right):
    if left[0][1] < right[0][0]:
        return True
    if right[0][1] < left[0][0]:
        return False
    powers = left[1].copy()
    powers.subtract(right[1])
    return prod(k**p for k, p in powers.items() if p > 0) < prod(
        k ** (-p) for k, p in powers.items() if p < 0
    )


def choose(observed):
    raw = raw_counts(observed)
    best = second = None
    for mapping in partitions():
        candidate = coding_cost(observed, raw, mapping)
        if best is None or lower(candidate, best):
            second, best = best, candidate
            selected = mapping
        elif second is None or lower(candidate, second):
            second = candidate
    gap = outward((second[0][0] - best[0][1], second[0][1] - best[0][0]), 2)
    return selected, gap


def install(hist, mapping):
    k = 1 + max(mapping)
    raw = raw_counts(hist)
    sizes = Counter(mapping)
    paid = [raw[a] for a, c in enumerate(mapping) if sizes[c] > 1]
    body = np.array([*cells(hist, mapping).flat, *paid], dtype="<u4")
    return bytes((k, *mapping)) + body.tobytes()


def decode(payload):
    k = payload[0]
    mapping = tuple(payload[1 : 1 + V])
    counts = np.frombuffer(payload, dtype="<u4", offset=1 + V).astype(np.int64)
    table = 2 * counts[: k**3].reshape((k,) * 3) + 1
    extras = iter(counts[k**3 :])
    group = Counter(mapping)
    raw = [int(2 * next(extras) + 1) if group[c] > 1 else 1 for c in mapping]
    totals = [
        sum(value for c, value in zip(mapping, raw, strict=True) if c == g)
        for g in range(k)
    ]
    prefix = {(): int(table.sum())}
    for length in range(1, 4):
        for word in product(range(k), repeat=length):
            prefix[word] = int(table[word].sum())

    def conditional(history, a):
        coarse = tuple(mapping[x] for x in history)
        return Fraction(
            prefix[(*coarse, mapping[a])] * raw[a], prefix[coarse] * totals[mapping[a]]
        )

    for word in WORDS:
        probability = prod(conditional(word[:j], a) for j, a in enumerate(word))
        direct = Fraction(int(table[tuple(mapping[x] for x in word)]), int(table.sum()))
        direct *= prod(Fraction(raw[x], totals[mapping[x]]) for x in word)
        assert probability == direct
    return conditional


def teacher(word):
    mass = Fraction()
    for initial in (0, 1):
        state = initial
        probability = Fraction(1, 2)
        for a in word:
            numerator = (3 if a == 3 * state else 1) if a in (0, 3) else 1
            probability *= Fraction(numerator, 8)
            state ^= a in (2, 5)
        mass += probability
    return mass


def score(hist, conditional):
    for length in range(3):
        for history in product(range(V), repeat=length):
            assert sum(conditional(history, a) for a in range(V)) == 1
    position = [[0, 0] for _ in range(3)]
    for word in WORDS:
        for j, a in enumerate(word):
            p = conditional(word[:j], a)
            lo, hi = ratio_log(p.denominator, p.numerator)
            position[j][0] += int(hist[word]) * lo
            position[j][1] += int(hist[word]) * hi
    n = int(hist.sum())
    return {
        "per_token": outward(tuple(map(sum, zip(*position))), 3 * n),
        "by_position": [outward(p, n) for p in position],
    }


def experiment():
    training = draw(N, 2026112301)
    deployed = {}
    searches = {}
    for name, view in (("pairs", training.sum(axis=2)), ("triples", training)):
        choice, gap = choose(view)
        searches[name] = {
            "assignment": list(choice),
            "runner_up_total_BIC_half_gap_nats": gap,
        }
        deployed[name] = install(training, choice)
    deployed["raw"] = install(training, tuple(range(V)))
    deployed["given_partition"] = install(training, TRUE)
    reporting = draw(REPORT, 2026112302)
    result = {
        name: {**score(reporting, decode(payload)), "packed_bytes": len(payload)}
        for name, payload in deployed.items()
    }
    result["source_oracle"] = score(
        reporting, lambda prefix, a: teacher((*prefix, a)) / teacher(prefix)
    )
    population = np.array([int(1024 * teacher(word)) for word in WORDS]).reshape(
        (V,) * 3
    )
    assert population.sum() == 1024
    population_nll = {
        name: score(population, decode(payload))["per_token"]
        for name, payload in deployed.items()
    }
    population_nll["source_oracle"] = score(
        population, lambda prefix, a: teacher((*prefix, a)) / teacher(prefix)
    )["per_token"]
    success = searches["triples"]["assignment"] == list(TRUE) and (
        Fraction(result["triples"]["per_token"][1])
        < Fraction(result["pairs"]["per_token"][0])
    )
    return {
        "registration": "4c5aa39",
        "training_windows": N,
        "reporting_windows": REPORT,
        "tested_partitions_per_view": sum(1 for _ in partitions()),
        "distinct_raw_window_cells_evaluated": 203 * (V**2 + V**3),
        "population_cac": str(teacher((0, 1, 0)) / teacher((1,))),
        "population_cbc": str(teacher((0, 2, 0)) / teacher((2,))),
        "selection": searches,
        "reporting": result,
        "postfit_population_nll": population_nll,
        "registered_success": success,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment()
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf-8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
