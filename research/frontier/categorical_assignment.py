"""Learn a missing categorical prediction from twin and crossed ordinary counts."""

import argparse
import json
import struct
import subprocess
import sys
from fractions import Fraction
from io import BytesIO
from itertools import product
from math import log, sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from positive_comparison import SOURCE, categorical_program
from scipy.stats import beta

SEEDS = (173, 419, 773)
BUDGETS = (4096, 65536, 1048576, 16777216)
PANELS = ("TT", "DD", "YY", "TD", "TY")
TESTS = len(SEEDS) * len(BUDGETS) * (12 + 9 + 3)
Q16 = 1 << 16


def source(seed):
    """Only the simulator sees latent masses, label assignments and noise."""
    rng = np.random.default_rng([seed, 3711])
    weights = np.array([rng.permutation([1, 2, 4, 8]) for _ in range(3)]) / 45
    assignment = np.array([rng.permutation([0, 0, 1, 2]) for _ in range(3)])
    t, d = np.indices((3, 4)).reshape(2, -1)
    labels = {"T": (t, 3), "D": (d, 4), "Y": (assignment.ravel(), 3)}
    noise = 1 / 4096
    emissions = {
        key: np.where(values[:, None] == np.arange(size), 1 - noise, noise / (size - 1))
        for key, (values, size) in labels.items()
    }
    tables = {
        a + b: emissions[a].T @ (weights.reshape(-1, 1) * emissions[b])
        for a, b in (*PANELS, "DY")
    }
    return weights, assignment, tables


def observe(rng, count, law):
    return rng.multinomial(count, law.ravel()).reshape(law.shape)


def upper_disagreement(table):
    total = table.sum()
    wrong = total - np.trace(table)
    return (
        1.0
        if wrong == total
        else float(beta.ppf(1 - 0.05 / TESTS, wrong + 1, total - wrong))
    )


def pushed_joint(td, assignment, target_size):
    joint = np.zeros((td.shape[1], target_size))
    for t, row in enumerate(assignment):
        joint[np.arange(td.shape[1]), row] += td[t]
    return joint


def row_conditional(joint):
    positive = np.maximum(joint, 0)
    totals = positive.sum(axis=1, keepdims=True)
    return np.divide(
        positive,
        totals,
        out=np.full_like(positive, 1 / positive.shape[1]),
        where=totals > 0,
    )


def learn(counts):
    tt, td, ty = [counts[k] / counts[k].sum() for k in ("TT", "TD", "TY")]
    n = counts["TD"].sum()
    nt, nd = td.shape
    ny = ty.shape[1]
    eta = sqrt(log(2 * TESTS / 0.05) / (2 * n))
    upper = [upper_disagreement(counts[key]) for key in ("TT", "DD", "YY")]
    mismatch = sum(upper)
    coverage = bool(td.min() > eta + upper[0] + upper[1])
    eps = min(1.0, mismatch + td.size * eta / 2)
    smoothing = min(0.5, eps)
    feasible_rows, likelihood_rows = [], []
    for t in range(nt):
        feasible = []
        best_value, best = np.inf, None
        for assignment in product(range(ny), repeat=nd):
            row = np.bincount(assignment, weights=counts["TD"][t], minlength=ny)
            partition_sizes = np.bincount(assignment, minlength=ny)
            if np.all(
                np.abs(row / n - ty[t]) <= mismatch + (1 + partition_sizes) * eta
            ):
                feasible.append(assignment)
            conditional = (row + 0.5) / (row.sum() + ny / 2)
            value = -counts["TY"][t] @ np.log(conditional)
            if value < best_value:
                best_value, best = value, assignment
        feasible_rows.append(feasible)
        likelihood_rows.append(best)
    certified = coverage and all(len(rows) == 1 for rows in feasible_rows)
    chosen = [rows[0] for rows in feasible_rows] if certified else None
    d_marginal = td.sum(axis=0)
    independent = np.outer(d_marginal, ty.sum(axis=0))
    projection = td.T @ np.linalg.pinv((tt + tt.T) / 2, hermitian=True) @ ty
    models = {
        "certified": pushed_joint(td, chosen, ny) if certified else independent,
        "cross_log_loss": pushed_joint(td, likelihood_rows, ny),
        "projection": projection,
        "independent": independent,
    }
    predictions = {}
    for name, joint in models.items():
        normalized = d_marginal[:, None] * row_conditional(joint)
        smooth = (1 - smoothing) * normalized + smoothing / (nd * ny)
        predictions[name] = row_conditional(smooth)
    certificate = {
        "eta": eta,
        "twin_disagreement_upper": upper,
        "all_cells_covered": coverage,
        "feasible_per_row": [len(rows) for rows in feasible_rows],
        "certified_assignment": chosen,
        "cross_log_loss_assignment": likelihood_rows,
        "assignments_evaluated": nt * ny**nd,
        "TV_upper_if_certified": eps if certified else None,
        "mean_KL_upper_if_certified": (1 + log(nd * ny)) * eps
        if certified and eps <= 0.5
        else None,
        "joint_smoothing": smoothing,
    }
    return certificate, d_marginal, predictions


def quantize(probabilities):
    probabilities = np.asarray(probabilities)
    raw = (Q16 - len(probabilities)) * probabilities / probabilities.sum()
    units = np.floor(raw).astype(int) + 1
    order = np.argsort(-(raw - np.floor(raw)), kind="stable")
    units[order[: Q16 - units.sum()]] += 1
    assert min(units) > 0 and sum(units) == Q16
    return units


def install(d_marginal, conditional):
    rows = [quantize(d_marginal), *(quantize([*row, 0]) for row in conditional)]
    return b"".join(struct.pack("<3H", *row[:3]) for row in rows)


def release(packet, state):
    masses = struct.unpack_from("<3H", packet, state * 6)
    return *masses, Q16 - sum(masses)


def after(state, raw_letter):
    return raw_letter + 1 if state == 0 else 0


def score(d_marginal, predicted, population, held):
    packet = install(d_marginal, predicted)
    all_rows = [release(packet, state) for state in range(5)]
    installed = np.array(all_rows, dtype=float) / Q16
    oracle = row_conditional(population)
    weights = held / held.sum()
    conditional = installed[1:, :3]
    probabilities = np.pad(predicted, ((0, 0), (0, 1)))
    assert np.max(np.abs(installed - np.vstack([d_marginal, probabilities]))) <= 4 / Q16
    assert all_rows[0][-1] > 1 and all(row[-1] == 1 for row in all_rows[1:])
    return {
        "conditional_KL": float(np.sum(population * np.log(oracle / predicted))),
        "test_conditional_excess": float(np.sum(weights * np.log(oracle / predicted))),
        "Q16_conditional_KL": float(np.sum(population * np.log(oracle / conditional))),
        "Q16_test_nll_per_raw_token": float(
            -np.sum(weights * (np.log(installed[0])[:, None] + np.log(conditional))) / 2
        ),
        "distinct_live_forecasts": len(set(all_rows)),
        "packet_hex": packet.hex(),
    }


def run():
    batches = []
    for seed in SEEDS:
        weights, assignment, laws = source(seed)
        held = observe(np.random.default_rng([seed, 3713]), 4096, laws["DY"])
        fits = []
        for n in BUDGETS:
            rng = np.random.default_rng([seed, n, 3712])
            counts = {key: observe(rng, n, laws[key]) for key in PANELS}
            certificate, marginal, predictions = learn(counts)
            results = {
                key: score(marginal, pred, laws["DY"], held)
                for key, pred in predictions.items()
            }
            recovered = certificate["certified_assignment"]
            if recovered is not None:
                assert np.array_equal(recovered, assignment)
                bound = certificate["mean_KL_upper_if_certified"]
                if bound is not None:
                    assert results["certified"]["conditional_KL"] <= bound
            fits.append(
                {
                    "pairs_per_panel": n,
                    "paid_resets": 5 * n,
                    "paid_reports": 10 * n,
                    "counts": {key: table.tolist() for key, table in counts.items()},
                    "fit": certificate,
                    "cross_log_loss_exact_map": bool(
                        np.array_equal(
                            certificate["cross_log_loss_assignment"], assignment
                        )
                    ),
                    "models": results,
                }
            )
        oracle = np.log(row_conditional(laws["DY"]))
        batches.append(
            {
                "seed": seed,
                "simulator_weights_over_45": np.rint(45 * weights).astype(int).tolist(),
                "simulator_assignment": assignment.tolist(),
                "evaluation_only_DY_counts": held.tolist(),
                "oracle_nll_per_target": float(-np.sum(laws["DY"] * oracle)),
                "oracle_test_nll_per_target": float(
                    -np.sum(held * oracle) / held.sum()
                ),
                "fits": fits,
            }
        )
    return {"registration": "2532ab0", "sources": batches}


def serialize(result):
    parts = []
    for batch in result["sources"]:
        header = {key: value for key, value in batch.items() if key != "fits"}
        prefix = json.dumps(header, allow_nan=False)[:-1]
        fits = [json.dumps(fit, allow_nan=False) for fit in batch["fits"]]
        parts.append(
            prefix + ', "fits": [\n      ' + ",\n      ".join(fits) + "\n    ]}"
        )
    return (
        '{\n  "registration": "'
        + result["registration"]
        + '",\n  "sources": [\n    '
        + ",\n    ".join(parts)
        + "\n  ]\n}\n"
    )


def exact_check():
    # These two ordinary sources have equal TT, DD, YY, TD, TY tables.
    # Each triple includes the latent mass in thirds and two deterministic labels.
    def panels(atoms):
        results = {}
        for key in (*PANELS, "DY"):
            table = {}
            for mass, d, y in atoms:
                labels = {"T": 0, "D": d, "Y": y}
                cell = tuple(labels[k] for k in key)
                table[cell] = table.get(cell, 0) + Fraction(mass, 3)
            results[key] = table
        return results

    small = panels(((1, 0, 0), (2, 1, 1)))
    split = panels(((1, 0, 1), (1, 1, 0), (1, 1, 1)))
    assert all(small[key] == split[key] for key in PANELS)
    assert small["DY"].get((0, 0), 0) == Fraction(1, 3)
    assert split["DY"].get((0, 0), 0) == 0
    # Verify the noiseless row-sum certificate at every possible assignment.
    keys = set()
    for labels in product(range(3), repeat=4):
        sums = tuple(
            sum(2**i for i, v in enumerate(labels) if v == y) for y in range(3)
        )
        assert sums not in keys
        keys.add(sums)
    for denomin in (3, 5, 8):
        for x in range(denomin + 1):
            for y in range(denomin - x + 1):
                p = [Fraction(z, denomin) for z in (x, y, denomin - x - y)]
                assert 1 - max(p) <= 1 - sum(z * z for z in p)
    return {
        "identical_training_panels": len(PANELS),
        "uniquely_encoded_three_label_rows": len(keys),
    }


def r4_audit():
    here = Path(__file__).resolve().parent
    result = json.loads((here / "categorical_assignment_result.json").read_text())
    packets = {
        scores["packet_hex"]
        for source_ in result["sources"]
        for fit in source_["fits"]
        for scores in fit["models"].values()
    }
    alphabet = tuple(map(str, range(4)))
    transitions = [tuple(after(i, j) for j in range(4)) for i in range(5)]
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        for hex_packet in sorted(packets):
            packet = bytes.fromhex(hex_packet)
            rows = [release(packet, i) for i in range(5)]
            slots = [Fraction(1), *(Fraction(2 * x - 1) for row in rows for x in row)]
            heads = [[(i, 1 + 4 * i + j) for i in range(5)] for j in range(4)]
            event, start, sizes = categorical_program(
                alphabet, transitions, heads, slots
            )
            states = [start, *(event(token, start.delayed) for token in alphabet)]
            for i, state in enumerate(states):
                assert state.probabilities == tuple(Fraction(x, Q16) for x in rows[i])
                for j, token in enumerate(alphabet):
                    dest = states[after(i, j)]
                    observed = event(token, state.delayed)
                    assert (
                        observed.delayed == dest.delayed
                        and observed.probabilities == dest.probabilities
                    )
    return {
        "distinct_30_byte_packets": len(packets),
        "reset_and_transition_checks": 21 * len(packets),
        "R4_nodes": sizes["nodes"],
        "R4_delayed_cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--r4", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.r4 or args.check:
        result = json.dumps(r4_audit() if args.r4 else exact_check(), indent=2) + "\n"
    else:
        result = serialize(run())
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
