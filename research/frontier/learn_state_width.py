"""Fit deterministic recurrent updates and unrestricted controls to ordinary sign records."""

import argparse
import json
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import ceil, log, log2, prod, sqrt
from pathlib import Path

import numpy as np
from scipy.special import gammaln
from stochastic_identities import contrast, identities
from transfer_dictionary import walsh

REGISTRATION = "e164129"
SIZES = (512, 4096, 32768)
REPEATS = 32
PRICE = 1 / 1024
INPUTS = tuple(product((1, -1), repeat=6))


def partitions(k):
    """All tables from reset zero; name terminal classes by first word reaching them."""
    maps = np.array(list(product(range(k), repeat=2 * k)), dtype=np.uint8)
    rows = np.arange(len(maps))[:, None, None]
    ends = np.zeros((len(maps), 1), dtype=np.uint8)
    for _ in range(6):
        ends = maps[rows, 2 * ends[:, :, None] + np.array([0, 1], dtype=np.uint8)]
        ends = ends.reshape(len(maps), -1)
    first = []
    for state in range(k):
        hits = ends == state
        first.append(np.where(hits.any(axis=1), hits.argmax(axis=1), len(INPUTS)))
    rename = np.argsort(np.argsort(np.column_stack(first), axis=1), axis=1)
    names = np.take_along_axis(rename, ends, axis=1).astype(np.uint8)
    keys, idx = np.unique(names, axis=0, return_index=True)
    return zip(keys, maps[idx], strict=True)


class Machines:
    def __init__(self):
        distinct = {}
        for k in range(1, 5):
            for key, table in partitions(k):
                distinct.setdefault(key.tobytes(), (k, table))
        self.ends = np.array([list(key) for key in distinct], dtype=np.uint8)
        self.width = np.array([k for k, _ in distinct.values()])
        self.tables = [m for _, m in distinct.values()]
        self.classes = [np.flatnonzero(self.width == k) for k in range(1, 5)]
        self.members = (
            (self.ends[:, None, :] == np.arange(4)[None, :, None])
            .reshape(-1, len(INPUTS))
            .astype(np.float64)
        )

    def group(self, counts):
        # Every entry is an integer sum bounded by the sample size; float64 is exact here.
        return (self.members @ counts).astype(np.int32).reshape(len(self.ends), 4, -1)

    def deployed(self, idx, means):
        k, table = int(self.width[idx]), self.tables[idx]
        head = [F(0)] * k
        for s, group in zip(INPUTS, self.ends[idx], strict=True):
            state = 0
            for sign in s:
                state = table[2 * state + int(sign < 0)]
            head[state] = means[group]
        for s, group in zip(INPUTS, self.ends[idx], strict=True):
            state = 0
            for sign in s:
                state = table[2 * state + int(sign < 0)]
            assert head[state] == means[group]
        return {
            "destinations_plus_minus": list(map(int, table)),
            "signed_head": list(map(str, head)),
        }


@lru_cache(None)
def exponentiated_gain(occupancy, magnitude):
    # The exact group contribution to exp(256 * population gain), beta = 1/2.
    if not magnitude:
        return F(1)
    twice = 2 * occupancy
    return F(twice + magnitude, twice) ** (twice + magnitude) * F(
        twice - magnitude, twice
    ) ** (twice - magnitude)


def population(bank, units):
    occupancies = bank.group(np.ones((64, 1), dtype=int))[:, :, 0]
    signed = bank.group(units[:, None])[:, :, 0]
    values = [
        prod(exponentiated_gain(int(n), abs(int(s))) for n, s in zip(count, masses))
        for count, masses in zip(occupancies, signed)
    ]
    best = max(values)
    idx = values.index(best)
    unique = sorted(set(values))
    means = [
        F(int(s), 2 * int(n)) if n else F(0)
        for n, s in zip(occupancies[idx], signed[idx])
    ]
    assert all(values[i] == 1 for i in np.flatnonzero(bank.width <= 3))
    gain = log(float(best)) / 256
    counts = [(int(n), int(s)) for n, s in zip(occupancies[idx], signed[idx]) if n]
    report = {
        "optimal_population_gain": gain,
        "critical_price_per_live_bit": gain / 2,
        "exp_256_times_optimal_gain": str(best),
        "occupied_raw_histories_and_signed_unit_sums": counts,
        "second_distinct_gain": log(float(unique[-2])) / 256
        if len(unique) > 1
        else None,
        "tied_optimal_terminal_partitions": sum(v == best for v in values),
        "representative": bank.deployed(idx, means),
        "full_law_gain": float(score(units / 2, units / 2)),
    }
    return report, np.array([v == best for v in values])


def score(truth, forecast):
    return np.mean(
        (1 + truth) * np.log1p(forecast) / 2 + (1 - truth) * np.log1p(-forecast) / 2,
        axis=-1,
    )


def draws(units, source, split):
    probabilities = np.concatenate((1 + units / 2, 1 - units / 2)) / 128
    rng = np.random.default_rng(np.random.SeedSequence([20261126, 604, source, split]))
    counts = np.zeros((REPEATS, 128), dtype=np.int32)
    previous = 0
    for size in SIZES:
        counts += rng.multinomial(size - previous, probabilities, size=REPEATS).astype(
            np.int32
        )
        previous = size
        yield counts[:, :64].copy(), counts[:, 64:].copy()


def fit_widths(bank, plus, minus):
    positives, negatives = bank.group(plus.T), bank.group(minus.T)
    total = positives + negatives
    n = int(total[0, :, 0].sum())
    gamma_half = gammaln(np.arange(n + 1) + 0.5)
    gamma_one = gammaln(np.arange(n + 1) + 1)
    integrated = (
        gamma_half[positives] + gamma_half[negatives] - gamma_one[total] - log(np.pi)
    ).sum(axis=1)
    # Lexicographic terminal partition wins training likelihood ties at a fixed width.
    best = []
    reps = np.arange(REPEATS)
    for ids in bank.classes:
        values = integrated[ids]
        local = (values >= values.max(axis=0) - 1e-9).argmax(axis=0)
        best.append(ids[local])
    chosen = np.array(best)
    forecasts = []
    for ids in chosen:
        head = (positives[ids, :, reps] - negatives[ids, :, reps]) / (
            1 + total[ids, :, reps]
        )
        forecasts.append(np.take_along_axis(head, bank.ends[ids], axis=1))
    return np.array(forecasts), chosen


def choose(forecasts, vplus, vminus, n):
    validation = (vplus * np.log1p(forecasts) + vminus * np.log1p(-forecasts)).sum(
        axis=2
    ) / n
    net = validation - PRICE * np.array([0, 1, 2, 2])[:, None]
    joint = np.argmax(net, axis=0)
    greedy = np.zeros(REPEATS, dtype=int)
    for k in range(1, 4):
        advance = (greedy == k - 1) & (net[k] > net[k - 1])
        greedy[advance] += 1
    return joint, greedy


def walsh_fits(plus, minus, n):
    signed = np.array([walsh(row) for row in plus - minus]) / n
    signed[np.abs(signed) <= sqrt(2 * log(128 / 0.05) / n)] = 0
    return np.clip(np.array([walsh(row) for row in signed]), -0.95, 0.95), np.sign(
        signed
    )


def fit_experiment(bank, units, source, optimal):
    truth = units / 2
    exact_signs = np.sign(walsh(units))
    train, validation = draws(units, source, 0), draws(units, source, 1)
    results = []
    for n, (plus, minus), (vplus, vminus) in zip(SIZES, train, validation, strict=True):
        forecasts, chosen = fit_widths(bank, plus, minus)
        joint, greedy = choose(forecasts, vplus, vminus, n)
        by_width = score(truth, forecasts)
        reps = np.arange(REPEATS)
        joint_score = by_width[joint, reps]
        free, signed = walsh_fits(plus, minus, n)
        results.append(
            {
                "per_split": n,
                "joint_width_histogram": np.bincount(joint + 1, minlength=5)[
                    1:
                ].tolist(),
                "greedy_width_histogram": np.bincount(greedy + 1, minlength=5)[
                    1:
                ].tolist(),
                "joint_positive_gain": int((joint_score > 0).sum()),
                "joint_optimal_partition": int(optimal[chosen[joint, reps]].sum()),
                "joint_gain": float(joint_score.mean()),
                "greedy_gain": float(by_width[greedy, reps].mean()),
                "always_four_gain": float(by_width[3].mean()),
                "direct_word_gain": float(
                    score(truth, (plus - minus) / (1 + plus + minus)).mean()
                ),
                "walsh_gain": float(score(truth, free).mean()),
                "walsh_exact_signed_support": int(
                    np.all(signed == exact_signs, axis=1).sum()
                ),
            }
        )
    return results


def audit():
    bank = Machines()
    raw = sum(k ** (2 * k) for k in range(1, 5))
    sources = [np.array([contrast(p, x) // 4 for x in INPUTS]) for p in identities()]
    sources.append(np.zeros(64, dtype=int))
    detail = {}
    for i, (name, units) in enumerate(
        zip(("first_identity", "second_identity", "fair"), sources)
    ):
        report, optimal = population(bank, units)
        detail[name] = {
            "population": report,
            "learning": fit_experiment(bank, units, i, optimal),
        }
    return {
        "registration": REGISTRATION,
        "raw_tables": raw,
        "prefix_transition_lookups": raw * (2**7 - 2),
        "partitions_at_minimum_widths": [len(ids) for ids in bank.classes],
        "dense_search_membership_bytes_as_executed": int(bank.members.nbytes),
        "maximum_count_bits_per_stored_integer": ceil(log2(max(SIZES) + 2)),
        "repetitions_per_source": REPEATS,
        "price_nats_per_live_bit": PRICE,
        "sources": detail,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
