"""Learn named bit values from independent aggregate reports at finite precision."""

import argparse
import json
import struct
import subprocess
import sys
from fractions import Fraction
from functools import cache
from io import BytesIO
from math import comb, exp, expm1, log, pi, sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from positive_comparison import SOURCE, categorical_program
from scipy.special import xlogy
from scipy.stats import binom
from threadpoolctl import threadpool_limits

N = 12
Q16 = 65536
BINARY_UNITS = Q16 - (N - 2)
CONTEXTS = (1, 3, 6)
BUDGETS = (192, 3072, 49152, 786432, 12582912)
MODELS = (
    "fair",
    "empirical_weights",
    "fitted_order_Bayes",
    "fitted_order_round",
    "known_order_Bayes",
)


@cache
def design(q):
    grid = np.arange(2**q)
    ranks = np.arange(q)
    bits = ((grid[:, None] >> ranks) & 1).astype(float)
    return grid / grid[-1], bits, (2.0**ranks) / grid[-1]


def posterior(success, n, means, bits):
    values = xlogy(success, means) + xlogy(n - success, 1 - means)
    masses = np.exp(values - np.max(values))
    return np.clip((masses @ bits) / masses.sum(), 0, 1)


def fitted_rounding(success, n, q):
    largest = 2**q - 1
    estimate = (2 * largest * int(success) + n) // (2 * n)
    sigma = largest / sqrt(n)
    # One-sided Hoeffding over both sides of all internal bit boundaries.
    envelope = min(sigma * sqrt(pi / 2), exp(-0.5 / sigma**2) / -expm1(-4 / sigma**2))
    rank = np.arange(q)
    factor = 2.0 ** (-rank)
    decoding = 2 * envelope * factor
    sorting = 16 * (factor * sigma) ** 2
    soft = np.minimum(0.5, decoding + sorting)
    return np.where((estimate >> rank) & 1, 1 - soft, soft)


def assign_order(values, indices):
    named = np.empty_like(values)
    named[indices] = values
    return named


def fit_group(counts, success, n, true_order):
    q = len(counts)
    grid, bits, _ = design(q)
    empirical = (counts + 0.5) / (n + q / 2)
    order = np.argsort(counts, kind="stable")
    grid_bayes = posterior(success, n, grid, bits)
    # The diagnostic uses the simulator order only after fitting the shared grid.
    return (
        np.full(q, 0.5),
        posterior(success, n, np.clip(bits @ empirical, 0, 1), bits),
        assign_order(grid_bayes, order),
        assign_order(fitted_rounding(success, n, q), order),
        assign_order(grid_bayes, true_order),
    )


def install(probabilities):
    units = np.clip(np.rint(BINARY_UNITS * probabilities), 1, BINARY_UNITS - 1)
    return units.astype("<u2").tobytes()


def release(packet, state):
    if state == 0:
        each, remainder = divmod(Q16, N)
        return tuple(each + (j < remainder) for j in range(N))
    ones = struct.unpack_from("<H", packet, 2 * (state - 1))[0]
    return (BINARY_UNITS - ones, ones, *((1,) * (N - 2)))


def gain_and_loss(packet, target):
    rows = [release(packet, name + 1) for name in range(N)]
    issued = np.array([rows[i][y] for i, y in enumerate(target)])
    binary_gain = log(2) + float(np.log(issued / BINARY_UNITS).mean())
    raw_nll = (
        -float(
            np.log(np.array(release(packet, 0)) / Q16).mean()
            + np.log(issued / Q16).mean()
        )
        / 2
    )
    return binary_gain, raw_nll


def simulate(s, m, budget):
    q, per = N // m, budget // m
    _, _, weights = design(q)
    labels = np.random.default_rng([s, 4811]).integers(2, size=N)
    channel = np.random.default_rng([s, m, 4812])
    rng = np.random.default_rng([s, m, budget, 4813])
    predictions = np.empty((len(MODELS), N))
    for group in range(m):
        names = slice(group * q, (group + 1) * q)
        permutation = channel.permutation(q)
        rates = assign_order(weights, permutation)
        counts = rng.multinomial(per, rates)
        success = int(rng.binomial(per, np.clip(rates @ labels[names], 0, 1)))
        predictions[:, names] = fit_group(counts, success, per, permutation)
    packets = [install(row) for row in predictions]
    scores = [gain_and_loss(packet, labels) for packet in packets]
    return scores, packets


def complementary():
    rows = []
    for q in (4, 8, 12):
        largest = 2**q - 1
        left = (largest - 1) // 2
        right = left + 1
        assert left ^ right == largest
        p = left / largest
        n = largest**2
        error = float(binom.sf(n // 2, n, p))
        divergence = log(1 + 2 / (largest - 1)) / largest
        rows.append(
            {
                "q": q,
                "complementary_indices": [left, right],
                "target_reports": n,
                "one_report_KL": divergence,
                "optimal_two_world_error": error,
                "sum_of_bit_log_losses_lower": 2 * q * log(2) * error,
            }
        )
    return rows


def exact_check():
    comparisons = 0
    for q in range(1, 6):
        largest = 2**q - 1
        for n in (1, 2, 5, 12, 32, 64):
            wrong = [0] * q
            for value in range(largest + 1):
                for count in range(n + 1):
                    paths = (
                        comb(n, count) * value**count * (largest - value) ** (n - count)
                    )
                    observed = (2 * largest * count + n) // (2 * n)
                    for j in range(q):
                        if (value ^ observed) & (1 << j):
                            wrong[j] += paths
            sigma = largest / sqrt(n)
            envelope = min(
                sigma * sqrt(pi / 2), exp(-0.5 / sigma**2) / -expm1(-4 / sigma**2)
            )
            for j, numerator in enumerate(wrong):
                error = Fraction(numerator, (largest + 1) * largest**n)
                assert float(error) <= 2 ** (1 - j) * envelope + 1e-14
                comparisons += 1
    for n in range(65):
        bound = Fraction(4**n, comb(2 * n, n))
        assert bound**2 <= 4 * n + 1
    return {"exact_average_bit_errors": comparisons, "half_count_squared_bounds": 65}


def run():
    result = []
    for m in CONTEXTS:
        q = N // m
        for b in BUDGETS:
            panel = []
            for s in range(256):
                scores, packets = simulate(s, m, b)
                if s == 0:
                    first = {
                        key: p.hex() for key, p in zip(MODELS, packets, strict=True)
                    }
                panel.append(scores)
            samples = np.array(panel)
            models = {
                name: {
                    "mean_binary_gain": float(samples[:, i, 0].mean()),
                    "source_standard_error": float(
                        samples[:, i, 0].std(ddof=1) / sqrt(len(samples))
                    ),
                    "mean_installed_nll_per_raw_token": float(samples[:, i, 1].mean()),
                }
                for i, name in enumerate(MODELS)
            }
            upper = min(log(2), b * log(2) / N, m / (2 * N) * log(1 + 4 * b / m))
            result.append(
                {
                    "contexts": m,
                    "target_reports": b,
                    "paid_reports_and_resets": 2 * b,
                    "enumerated_rows_per_exhaustive_fit": m * 2**q,
                    "names_ranked_per_fit": N,
                    "population_gain_upper": upper,
                    "models": models,
                    "source_0_packets": first,
                }
            )
    return {
        "registration": "f7aa7dd",
        "independent_sources": 256,
        "complementary": complementary(),
        "conditions": result,
    }


def r4_audit():
    here = Path(__file__).resolve().parent
    results = json.loads((here / "aggregate_bits_result.json").read_text())
    chosen = [r for r in results["conditions"] if r["target_reports"] == 49152]
    alphabet = tuple(map(str, range(N)))
    transitions = [tuple(range(1, N + 1)), *((0,) * N for _ in range(N))]
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        for condition in chosen:
            packet = bytes.fromhex(condition["source_0_packets"]["fitted_order_round"])
            rows = [release(packet, state) for state in range(N + 1)]
            slots = [Fraction(1), *(Fraction(2 * v - 1) for row in rows for v in row)]
            heads = [[(i, 1 + i * N + j) for i in range(N + 1)] for j in range(N)]
            event, start, sizes = categorical_program(
                alphabet, transitions, heads, slots
            )
            states = [start, *(event(token, start.delayed) for token in alphabet)]
            for i, state in enumerate(states):
                assert state.probabilities == tuple(Fraction(x, Q16) for x in rows[i])
                for token, dest in zip(alphabet, transitions[i], strict=True):
                    observed = event(token, state.delayed)
                    assert (
                        observed.delayed == states[dest].delayed
                        and observed.probabilities == states[dest].probabilities
                    )
    return {
        "packets": len(chosen),
        "reset_and_transition_checks": len(chosen) * (1 + (N + 1) * N),
        "R4_nodes": sizes["nodes"],
        "R4_delayed_cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--r4", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        if args.r4:
            result = r4_audit()
        elif args.check:
            result = exact_check()
        else:
            result = run()
        receipt = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(receipt, encoding="utf-8")
    else:
        print(receipt, end="")
