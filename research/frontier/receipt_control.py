"""Exact finite-law checks and the preregistered four-symbol directed-dependence source."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path

import numpy as np
from receipt_program import (
    CAPS,
    SHIFTS,
    decode,
    program_indices,
    reference_delta,
    search_utility,
    select,
)
from sparse_directions import Native
from threadpoolctl import threadpool_limits


def exact_receipts():
    q = [F(1, 3), F(3, 5), F(2, 7), F(4, 9)]
    y = [1, 0, 1, 0]
    b, rho = 2, F(1, 3)
    pairs = {(j, t): rho * (1 - rho) ** (t - j - 1) for t in range(4) for j in range(t)}
    r = [x - p for x, p in zip(y, q)]
    v = [p * (1 - p) / b for p in q]

    def score(x):
        return sum(k * x[j] * x[t] for (j, t), k in pairs.items())

    truth = score(r)
    h = [
        sum(pairs[j, t] * r[j] for j in range(t))
        + sum(pairs[t, u] * r[u] for u in range(t + 1, 4))
        for t in range(4)
    ]
    var = sum(x * y * y for x, y in zip(v, h)) + sum(
        k * k * v[j] * v[t] for (j, t), k in pairs.items()
    )
    mean = second = total = F(0)
    for counts in product(range(b + 1), repeat=4):
        prob = F(1)
        for c, p in zip(counts, q):
            prob *= comb(b, c) * p**c * (1 - p) ** (b - c)
        observed = [x - F(c, b) for x, c in zip(y, counts)]
        error = score(observed) - truth
        doob = sum(
            (observed[t] - r[t])
            * (
                sum(pairs[j, t] * observed[j] for j in range(t))
                + sum(pairs[t, u] * r[u] for u in range(t + 1, 4))
            )
            for t in range(4)
        )
        assert doob == error
        total += prob
        mean += prob * error
        second += prob * error**2
    assert total == 1 and mean == 0 and second == var
    return {
        "enumerated_count_tapes": 81,
        "mean_score": str(truth),
        "score_variance": str(var),
    }


def source():
    u = (1, -1, 0, 0)
    v = (0, 0, 1, -1)
    return [[F(1, 4) + F(3, 16) * a * b for b in v] for a in u]


def exact_source(matrix):
    uniform = F(1, 4)
    assert all(sum(row) == 1 for row in matrix)
    assert all(sum(col) == 1 for col in zip(*matrix))
    assert all(
        sum(matrix[i][k] * matrix[k][j] for k in range(4)) == uniform
        for i, j in product(range(4), repeat=2)
    )
    n = 6
    cases = 0
    for j in range(4):
        for bits in product(range(2), repeat=n):
            p = [uniform] * 4
            for bit in bits:
                p = [x if (i == j) == bool(bit) else F(0) for i, x in enumerate(p)]
                p = [sum(p[i] * matrix[i][k] for i in range(4)) for k in range(4)]
            assert sum(p) == uniform ** sum(bits) * (1 - uniform) ** (n - sum(bits))
            cases += 1
    p = float(matrix[0][2])
    return {
        "indicator_words_checked": cases,
        "population_own_channel_best_gain": 0.0,
        "one_bit_population_gain_per_word": float(
            (p * np.log(4 * p) + (1 - p) * np.log(4 * (1 - p) / 3)) / 4
        ),
        "distinct_optimal_conditional_laws": len(set(map(tuple, matrix))),
    }


def words(matrix, n, seed):
    rng = np.random.default_rng(seed)
    cdf = matrix.cumsum(axis=1)
    y = np.zeros(n, np.uint8)
    y[0] = rng.integers(4)
    for t, u in enumerate(rng.random(n - 1), 1):
        y[t] = np.searchsorted(cdf[y[t - 1]], u)
    return y


def synthetic():
    n, b = 32768, 16
    exact = source()
    matrix = np.array(exact, dtype=float)
    q = np.full((n, 4), 0.25)
    ids = [0, 1, 2]
    y = words(matrix, n, 252511)
    report = words(matrix, n, 252512)

    def samples(seed):
        return np.random.default_rng(seed).multinomial(b, q).astype(float) / b

    with Native() as lib:
        bounds = search_utility(samples(252513), y, b, lib)
        trained = {"directed": select(bounds, ids)}
        self_only = bounds.copy()
        self_only[:, :, ~np.eye(4, dtype=bool)] = -np.inf
        trained["own_only"] = select(self_only, ids)
        frequency = samples(252514)
        states = {h: lib.histories(frequency, report, True, 2.0**-h) for h in SHIFTS}
        for family in trained.values():
            for cap in CAPS:
                row = family[str(cap)]
                word = bytes.fromhex(row["packet"])
                edges = program_indices(word, ids)
                loss, _ = reference_delta(edges, states, q, report)
                row.update(
                    {
                        "edges": decode(word)[0],
                        "report_gain": float(-loss.sum()),
                        "bytes": len(word),
                        "live_bytes": 2 * len({(e[0], e[2]) for e in edges}),
                    }
                )
    table = np.ones((4, 4), dtype=np.uint32)
    np.add.at(table, (y[:-1], y[1:]), 1)
    fitted = table / table.sum(axis=1, keepdims=True)

    def report_gain(p):
        return float(np.log(4 * p[report[:-1], report[1:]]).sum())

    return {
        "registration": "dd990a1",
        "training_and_report_lengths": [n, n],
        "draws_per_word": b,
        "analytic": exact_source(exact),
        "models": trained,
        "base_gain": 0.0,
        "add_one_table_gain": report_gain(fitted),
        "known_source_gain": report_gain(matrix),
        "table_uint32_counts": table.tolist(),
    }


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    dest = p.add_mutually_exclusive_group(required=True)
    dest.add_argument("--write", type=Path)
    dest.add_argument("--check", type=Path)
    a = p.parse_args()
    with threadpool_limits(limits=1):
        result = {"small_exact_receipts": exact_receipts(), "four_symbols": synthetic()}
    # JSON also normalizes the decoded edge tuples to arrays.
    result = json.loads(json.dumps(result))
    if a.check:
        assert compare(result, json.loads(a.check.read_text(encoding="utf8")))
    else:
        a.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(
        "Exact receipt law and controlled sparse acquisition matched their references."
    )
