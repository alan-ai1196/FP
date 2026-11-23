"""Acquire symmetric coin biases from two ordinary draws per training episode."""

import argparse
import json
import re
from fractions import Fraction
from functools import cache
from itertools import product
from math import ceil, log
from pathlib import Path

import numpy as np
from coin_memory import compare, passive
from scipy.special import betaln, expit, rel_entr, roots_legendre
from scipy.stats import binom
from threadpoolctl import threadpool_limits

A, B = 5 / 8, 7 / 8
THETAS = (A, 0.68, 0.75, 0.82, B)
HORIZONS = (64, 1024, 16384)
CENTER = 4
PRECISION = 4096


def agreement(p):
    return p * p + (1 - p) ** 2


def packet_grid(n, bits):
    levels = 1 << bits
    cuts = 5 * levels + 2 * np.arange(1, levels, dtype=np.int64)
    den = 8 * levels
    threshold = n * (cuts**2 + (den - cuts) ** 2)
    edges = np.r_[0, (threshold + den**2 - 1) // den**2, n + 1]
    means = A + (B - A) * (np.arange(levels) + 0.5) / levels
    return means, edges


def packet_law(p, n, edges):
    v = agreement(np.asarray(p))[:, None]
    lo, hi = edges[:-1] - 1, edges[1:] - 1
    left, right = binom.cdf(lo, n, v), binom.cdf(hi, n, v)
    masses = np.where(lo < n * v, right - left, binom.sf(lo, n, v) - binom.sf(hi, n, v))
    assert masses.min() > -1e-13
    masses = np.maximum(masses, 0)
    np.testing.assert_allclose(masses.sum(axis=1), 1, atol=2e-12, rtol=0)
    return masses


def log_paths(k, t, p):
    p = np.asarray(p)
    hi = k[:, None] * np.log(p) + (t - k[:, None]) * np.log1p(-p)
    lo = (t - k[:, None]) * np.log(p) + k[:, None] * np.log1p(-p)
    return np.logaddexp(hi, lo) - log(2)


@cache
def quadrature(order):
    nodes, weights = roots_legendre(order)
    return (A + B) / 2 + (B - A) / 2 * nodes, weights / 2


@cache
def joint_packet(n, bits, order):
    nodes, prior = quadrature(order)
    _, edges = packet_grid(n, bits)
    return packet_law(nodes, n, edges) * prior[:, None]


@cache
def report(theta, t):
    # The reported mixture and all comparators are invariant under reflection.
    lo = int(binom.ppf(1e-14, t, theta))
    hi = int(binom.isf(1e-14, t, theta))
    k = np.arange(lo, hi + 1)
    weights = binom.pmf(k, t, theta)
    assert 1 - weights.sum() < 4e-14
    true = log_paths(k, t, [theta])[:, 0]
    half = float(weights @ (true - betaln(k + 0.5, t - k + 0.5) + betaln(0.5, 0.5)))
    return k, weights, true, half


@cache
def continuous_paths(theta, t, order):
    nodes, _ = quadrature(order)
    k, _, _, _ = report(theta, t)
    laws = log_paths(k, t, nodes)
    maximum = laws.max(axis=1)
    return np.exp(laws - maximum[:, None]), maximum


@cache
def counter_visits(theta, t):
    limit = ceil(log(t) / log(A / (1 - A)))
    s = np.arange(-limit, limit + 1)
    step = np.zeros((len(s), len(s)))
    for i in range(1, len(s) - 1):
        step[i, i - 1], step[i, i + 1] = 1 - theta, theta
    step[0, 0] = step[-1, -1] = 1
    total = np.eye(len(s))
    power = step
    remaining = 1
    while remaining < t:
        total += power @ total
        power = power @ power
        remaining *= 2
    assert remaining == t
    np.testing.assert_allclose(total[limit].sum(), t, rtol=3e-12)
    return s, total[limit], passive(0.5, 1 - theta, theta, t)[1]


def counters(theta, t, parameters):
    p = np.asarray(parameters)[None, :]
    s, occupancy, info = counter_visits(theta, t)
    posterior = expit(s[:, None] * np.log(p / (1 - p)))
    full = (1 - p) + (2 * p - 1) * posterior
    full[0], full[-1] = 1 - p, p
    packed = np.where(
        np.abs(s[:, None]) <= CENTER,
        np.rint(PRECISION * full) / PRECISION,
        np.where(s[:, None] < 0, 1 - p, p),
    )

    def price(emit):
        return (
            occupancy @ (rel_entr(theta, emit) + rel_entr(1 - theta, 1 - emit)) - info
        )

    return price(full), price(packed)


def conditioned(prior, theta, t, order):
    laws, maximum = continuous_paths(theta, t, order)
    _, w, truth, _ = report(theta, t)
    normalized = prior / prior.sum(axis=0)
    assert np.all(np.isfinite(normalized))
    likelihood = laws @ normalized
    assert np.all(likelihood > 0)
    return w @ (truth[:, None] - maximum[:, None] - np.log(likelihood))


def comparison(theta, n, t, bits):
    values, edges = packet_grid(n, bits)
    weights = packet_law([theta], n, edges)[0]
    keep = weights > 1e-15
    assert weights[~keep].sum() < 2e-13
    weights, selected = weights[keep], values[keep]
    k, report_weight, true, half = report(theta, t)
    fitted = float(
        report_weight @ (true[:, None] - log_paths(k, t, selected)) @ weights
    )
    full, packed = counters(theta, t, selected)
    oracle, oracle_packed = counters(theta, t, [theta])
    answers = []
    for order in (512, 1024):
        _, prior = quadrature(order)
        joint = joint_packet(n, bits, order)[:, keep]
        integrated = float(conditioned(joint, theta, t, order) @ weights)
        singleton = float(conditioned(prior[:, None], theta, t, order)[0])
        answers.append((integrated, singleton))
    diff = float(np.max(np.abs(np.subtract(*answers))))
    assert diff < 6e-6, (theta, n, t, bits, diff)
    return {
        "bayes_same_packet": answers[-1][0],
        "singleton_training_bayes": answers[-1][1],
        "plug_in_full": fitted,
        "fitted_counter": float(full @ weights),
        "packed_fitted_counter": float(packed @ weights),
        "true_counter": float(oracle[0]),
        "true_amplitude_limited_center": float(oracle_packed[0]),
        "half_count": half,
        "amplitude_mse": float(weights @ ((selected - theta) ** 2)),
        "quadrature_max_difference": diff,
    }


def pair_audit():
    verified = 0
    for n in range(1, 5):
        for raw in product((0, 1), repeat=2 * n):
            theta = 0.71
            pairprob = 1.0
            matches = 0
            for u, v in zip(raw[::2], raw[1::2]):
                counts = u + v
                pairprob *= (
                    theta**counts * (1 - theta) ** (2 - counts)
                    + (1 - theta) ** counts * theta ** (2 - counts)
                ) / 2
                matches += u == v
            other = (
                agreement(theta) ** matches
                * (1 - agreement(theta)) ** (n - matches)
                / (2**n)
            )
            assert abs(pairprob - other) < 1e-15
            verified += 1
    return verified


def missing_moment():
    """Two different four-bias sources sharing every three-draw training law."""

    def probability(radii, word):
        ones = sum(word)
        biases = [Fraction(10 + sign * r, 20) for r in radii for sign in (-1, 1)]
        return sum(p**ones * (1 - p) ** (len(word) - ones) for p in biases) / 4

    checked = {}
    for size in range(1, 5):
        gaps = {
            abs(probability((1, 8), w) - probability((4, 7), w))
            for w in product((0, 1), repeat=size)
        }
        assert gaps == {Fraction(0) if size < 4 else Fraction(9, 2000)}
        checked[str(size)] = str(gaps.pop())
    return checked


def r4_fitted_counter(receipt):
    from positive_comparison import categorical_program

    p = Fraction(receipt["snapped_amplitude"])
    limit = receipt["limit"]
    states = [0, *range(1, limit + 1), *range(-1, -limit - 1, -1)]
    slots = [1]
    readouts = [[], []]
    update, probabilities = [], []
    for i, s in enumerate(states):
        next_counts = [s, s] if abs(s) == limit else [s - 1, s + 1]
        update.append([states.index(count) for count in next_counts])
        if abs(s) <= CENTER and abs(s) < limit:
            odds = (p / (1 - p)) ** s
            q = (p * odds + 1 - p) / (1 + odds)
        else:
            q = p if s > 0 else 1 - p
        k = round(PRECISION * q)
        probabilities.append(Fraction(k, PRECISION))
        for head, weight in zip(readouts, (PRECISION - k - 1, k - 1)):
            if weight not in slots:
                slots.append(weight)
            head.append((i, slots.index(weight)))
    event, start, size = categorical_program(("0", "1"), update, readouts, slots)
    reached = {0: start}
    todo = [0]
    for i in todo:
        current = reached[i]
        assert current.probabilities[1] == probabilities[i]
        for y in (0, 1):
            j = update[i][y]
            successor = event(str(y), current.delayed)
            assert successor.probabilities[1] == probabilities[j]
            assert [v[0] for _, v in successor.delayed] == [
                int(k == j) for k in range(len(states))
            ]
            if j not in reached:
                reached[j] = successor
                todo.append(j)
    assert len(reached) == len(states)
    return {"reachable_edges": 2 * len(states), **size}


def run():
    cases = []
    with threadpool_limits(limits=1):
        for t in HORIZONS:
            baseline_bits = (t.bit_length() - 1) // 2
            for n in (t // 16, t, 16 * t):
                for delta in (-2, 0, 2):
                    bits = baseline_bits + delta
                    rows = [comparison(theta, n, t, bits) for theta in THETAS]
                    keys = rows[0].keys()
                    case = {
                        "T": t,
                        "N": n,
                        "bits": bits,
                        "values": {
                            k: [float(f"{r[k]:.12g}") for r in rows] for k in keys
                        },
                    }
                    cases.append(case)
    return {
        "true_amplitudes": THETAS,
        "interval": (A, B),
        "unit": "expected total excess nats over the known-amplitude mixture",
        "boundary": "clipped inverse agreement frequency; equally spaced midpoint packet, ties upper",
        "quadrature_orders": [512, 1024],
        "counter_center": CENTER,
        "packed_levels": PRECISION,
        "prior": "uniform amplitude on the interval, independent fair orientations",
        "raw_training_logs_checked": pair_audit(),
        "four_bias_absolute_path_gaps": missing_moment(),
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run(), allow_nan=False))
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched calibration and prediction.")
    else:
        body = json.dumps(result, indent=2) + "\n"
        # A measurement row holds five amplitudes and is read as one series.
        numeric_list = r"\[\s*([-+0-9.eE]+(?:,\s*[-+0-9.eE]+)*)\s*\]"
        body = re.sub(numeric_list, lambda m: "[" + " ".join(m[1].split()) + "]", body)
        if args.output:
            args.output.write_text(body, encoding="utf8")
        else:
            print(body, end="")
