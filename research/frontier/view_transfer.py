"""Predict a never jointly observed target and view with matched calibration budgets."""

import argparse
import json
import subprocess
import sys
from fractions import Fraction as F
from io import BytesIO
from itertools import combinations, product
from math import log, sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import sympy as sp
from positive_comparison import SOURCE, categorical_program
from scipy.optimize import minimize_scalar
from scipy.special import expit, xlogy

SEEDS = (173, 419, 773)
ALPHAS = (0.5, 0.125, 0.03125)
BUDGETS = (256, 4096, 65536, 1048576, 16777216, 67108864)
COMPARISONS = 4 * len(SEEDS) * len(ALPHAS) * len(BUDGETS)


def pairs(rng, n, correlation):
    signs = np.array([1, -1, -1, 1])
    return rng.multinomial(n, (1 + correlation * signs) / 4)


def collect(seed, index, n):
    rng = np.random.default_rng([seed, index, n, 2811])
    a, b, g = ALPHAS[index], 0.75, (1 if seed == 419 else -1) * 2 / 3
    tables = [pairs(rng, n, c) for c in (a * b, a * g, a * a)]
    phase = 2 * int(rng.integers(2)) - 1
    reads = int(rng.binomial(2 * n, (1 + a * phase) / 2))
    return tables, reads


def interval(value, count):
    radius = sqrt(2 * log(2 * COMPARISONS / 0.05) / count)
    return max(-1.0, value - radius), min(1.0, value + radius)


def minabs(lo, hi):
    return max(0.0, lo, -hi)


def structural_interval(p, q, scale):
    # For each a>0 the feasible b and g intervals vary only at these breakpoints.
    low = max(scale[0], minabs(*p), minabs(*q))
    high = scale[1]
    if low > high:
        return (-1.0, 1.0), False
    if low == 0:
        return (-1.0, 1.0), True
    cuts = sorted({low, high, *(abs(z) for z in (*p, *q) if low < abs(z) < high)})
    extrema = []
    for a in cuts:
        left = (max(-1.0, p[0] / a), min(1.0, p[1] / a))
        right = (max(-1.0, q[0] / a), min(1.0, q[1] / a))
        extrema.extend(x * y for x in left for y in right)
    return (min(extrema), max(extrema)), True


def entropy(p):
    return float(-xlogy(p, p) - xlogy(1 - p, 1 - p))


def center(bounds):
    lo, hi = ((1 + x) / 2 for x in bounds)
    if hi - lo <= 1e-12:
        return lo + hi - 1
    return float(2 * expit((entropy(lo) - entropy(hi)) / (hi - lo)) - 1)


def loss(truth, fitted):
    p, q = (1 + truth) / 2, (1 + fitted) / 2
    return float(xlogy(p, p / q) + xlogy(1 - p, (1 - p) / (1 - q)))


def install(r):
    cap = int(0.98 * 32768)
    value = max(-cap, min(cap, round(32768 * r)))
    return value.to_bytes(2, "little", signed=True)


def release(packet, state):
    coefficient = int.from_bytes(packet, "little", signed=True)
    return 32768 + (0, -coefficient, coefficient)[state]


def binomial_log(hat, value, count):
    # Discard common factors from the likelihood, including the count multiplicity.
    p, q = (1 + hat) / 2, (1 + np.asarray(value)) / 2
    return count * (xlogy(p, q) + xlogy(1 - p, 1 - q))


def estimate(p, q, a):
    if a == 0:
        return 0.0
    return float(np.clip(p / a, -1, 1) * np.clip(q / a, -1, 1))


def profile(p, q, observed, n, persistent):
    def likelihood(a):
        left = np.clip(p, -a, a)
        right = np.clip(q, -a, a)
        value = binomial_log(p, left, n) + binomial_log(q, right, n)
        if persistent:
            old = np.logaddexp(
                binomial_log(observed, a, 2 * n), binomial_log(observed, -a, 2 * n)
            ) - log(2)
        else:
            old = binomial_log(observed, a * a, n)
        return value + old

    anchor = abs(observed) if persistent else sqrt(max(0.0, observed))
    grid = np.unique(np.r_[np.linspace(0, 1, 257), abs(p), abs(q), anchor])
    vals = likelihood(grid)
    candidates = [(float(vals.max()), float(grid[vals.argmax()]))]
    for i in range(1, len(grid) - 1):
        if vals[i] >= vals[i - 1] and vals[i] >= vals[i + 1]:
            fit = minimize_scalar(
                lambda a: -likelihood(a),
                bounds=(grid[i - 1], grid[i + 1]),
                method="bounded",
                options={"xatol": 1e-13},
            )
            if fit.success:
                candidates.append((-fit.fun, float(fit.x)))
    a = max(candidates)[1]
    return estimate(p, q, a), a


def fit_arm(p, q, observed, n, persistent):
    raw = interval(observed, 2 * n if persistent else n)
    if persistent:
        scale = (minabs(*raw), max(abs(raw[0]), abs(raw[1])))
    elif raw[1] < 0:
        scale = (1.0, 0.0)
    else:
        scale = (sqrt(max(0.0, raw[0])), sqrt(raw[1]))
    bounds, consistent = structural_interval(interval(p, n), interval(q, n), scale)
    fitted, amplitude = profile(p, q, observed, n, persistent)
    return {
        "interval": bounds,
        "consistent": consistent,
        "center": center(bounds),
        "profile": fitted,
        "profile_alpha": amplitude,
        "resets": 2 * n + (1 if persistent else n),
    }


def exact_couplings():
    # A linear feasibility check independent of the scalar correlation parametrization.
    latent = list(product((-1, 1), repeat=3))
    matrix = sp.Matrix([[1, t, d, y, t * d, t * y] for t, d, y in latent]).T
    rhs = sp.Matrix([1, 0, 0, 0, -sp.Rational(1, 2), -sp.Rational(1, 2)])
    attainable = []
    for support in combinations(range(len(latent)), matrix.rank()):
        cols = matrix[:, support]
        if cols.det():
            masses = cols.inv() * rhs
            if min(masses) >= 0:
                attainable.append(
                    sum(
                        w * latent[i][1] * latent[i][2]
                        for w, i in zip(masses, support, strict=True)
                    )
                )
    assert (min(attainable), max(attainable)) == (0, 1)
    # Fix the missing moment and minimize the number of positive latent masses.
    constrained = matrix.col_join(sp.Matrix([[d * y for _, d, y in latent]]))
    minima = {}
    for numerator in range(5):
        correlation = sp.Rational(numerator, 4)
        target = rhs.col_join(sp.Matrix([correlation]))
        counts = []
        for support in combinations(range(len(latent)), constrained.rows):
            submatrix = constrained[:, support]
            if submatrix.det():
                masses = submatrix.inv() * target
                if min(masses) >= 0:
                    counts.append(sum(1 for mass in masses if mass > 0))
        minima[str(correlation)] = min(counts)
    assert list(minima.values()) == [6, 7, 5, 6, 4]
    half = sp.Rational(1, 2)
    false_gram = sp.Matrix([[1, -half, -half], [-half, 1, -half], [-half, -half, 1]])
    assert false_gram.is_positive_semidefinite
    # Lift signs to the one-hot indicators (1±sign)/2. This is a PSD congruence.
    lift = sp.Matrix(
        [
            [half, *(half * z if j == i else 0 for j in range(3))]
            for i in range(3)
            for z in (1, -1)
        ]
    )
    lifted = lift * sp.diag(1, false_gram) * lift.T
    assert min(lifted) >= 0 and lifted.is_positive_semidefinite
    physical, relaxed = (0, 1), (-0.5, 1)
    models = {
        "positive_completion": center(physical),
        "PSD_completion": center(relaxed),
        "projection": 0.25,
        "fair": 0.0,
    }
    return {
        "physical_bounds": physical,
        "relaxation_bounds": relaxed,
        "exact_feasible_bases": len(attainable),
        "minimum_latent_atoms_at_fixed_correlation": minima,
        "forecasts": {
            name: {
                "probability_of_agreement": (1 + r) / 2,
                "worst_physical_excess": max(loss(t, r) for t in physical),
            }
            for name, r in models.items()
        },
    }


def run():
    results = []
    for i, a in enumerate(ALPHAS):
        for seed in SEEDS:
            truth = 0.5 if seed == 419 else -0.5
            for n in BUDGETS:
                tables, reads = collect(seed, i, n)
                p, q, v = [float(row @ [1, -1, -1, 1]) / n for row in tables]
                burst = reads / n - 1
                row = {
                    "alpha": a,
                    "seed": seed,
                    "pairs_per_cross": n,
                    "paid_reports": 6 * n,
                    "observed": [p, q, v, burst],
                }
                arms = {
                    "twins": fit_arm(p, q, v, n, False),
                    "persistent": fit_arm(p, q, burst, n, True),
                }
                for arm in arms.values():
                    interval_ = arm["interval"]
                    arm["covers"] = bool(interval_[0] <= truth <= interval_[1])
                    arm["center"] = float(np.clip(arm["center"], -0.98, 0.98))
                    arm["profile"] = float(np.clip(arm["profile"], -0.98, 0.98))
                    arm["center_excess"] = loss(truth, arm["center"])
                    arm["profile_excess"] = loss(truth, arm["profile"])
                    arm["q15_hex"] = [
                        install(arm[key]).hex() for key in ("center", "profile")
                    ]
                    for key, packet in zip(
                        ("center", "profile"), arm["q15_hex"], strict=True
                    ):
                        encoded = bytes.fromhex(packet)
                        assert release(encoded, 1) + release(encoded, 2) == 65536
                        assert (
                            abs(release(encoded, 2) / 65536 - (1 + arm[key]) / 2)
                            <= 1 / 65536
                        )
                row["arms"] = arms
                row["controls"] = {
                    name: loss(truth, float(np.clip(r, -0.98, 0.98)))
                    for name, r in (
                        ("fair", 0),
                        ("uncorrected", p * q),
                        ("known_alpha", estimate(p, q, a)),
                        ("oracle", truth),
                    )
                }
                results.append(row)
    return {
        "registration": "71df582",
        "exact_categorical": exact_couplings(),
        "fits": results,
    }


def format_result(result):
    header = {k: v for k, v in result.items() if k != "fits"}
    intro = json.dumps(header, indent=2, allow_nan=False).rstrip()[:-1].rstrip()
    rows = [json.dumps(row, allow_nan=False) for row in result["fits"]]
    return intro + ',\n  "fits": [\n    ' + ",\n    ".join(rows) + "\n  ]\n}\n"


def r4_audit():
    here = Path(__file__).resolve().parent
    result = json.loads((here / "view_transfer_result.json").read_text())
    packets = {
        p
        for row in result["fits"]
        for arm in row["arms"].values()
        for p in arm["q15_hex"]
    }
    packets.add(install(0.6).hex())
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    events = 0
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        edges = [(1, 2), (0, 0), (0, 0)]
        for entry in sorted(packets):
            packet = bytes.fromhex(entry)
            probs = [F(release(packet, s), 65536) for s in range(3)]
            # Scale by one full Q16 denominator so every excess over R4 base one is positive.
            slots, heads = [F(1)], [[], []]
            for i, p in enumerate(probs):
                for head, mass in zip(heads, (1 - p, p), strict=True):
                    v = 65536 * mass - 1
                    if v not in slots:
                        slots.append(v)
                    head.append((i, slots.index(v)))
            event, start, sizes = categorical_program(("0", "1"), edges, heads, slots)
            states = [start, event("0", start.delayed), event("1", start.delayed)]
            for i, s in enumerate(states):
                assert s.probabilities[1] == probs[i]
                for bit, dest in enumerate(edges[i]):
                    nxt = event(str(bit), s.delayed)
                    assert (
                        nxt.delayed == states[dest].delayed
                        and nxt.probabilities[1] == probs[dest]
                    )
            events += 7
    return {
        "distinct_packets": len(packets),
        "state_and_output_checks_reset_and_edges": events,
        "nodes": sizes["nodes"],
        "cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--r4", action="store_true")
    args = parser.parse_args()
    result = (
        json.dumps(r4_audit(), indent=2) + "\n" if args.r4 else format_result(run())
    )
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
