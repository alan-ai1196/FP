"""Fit raw next-word forecasts from crossed count tables, then replay frozen heads."""

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from io import BytesIO
from math import log, sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from categorical_assignment import quantize
from positive_comparison import SOURCE, categorical_program
from text import VOCAB, git_json, tape
from threadpoolctl import threadpool_limits

K = 17
TAU = 64
HISTORY = 1048576
FIT_START = 9000000
FIT_END = FIT_START + 1048576
FIT_SHA = "be533658c8850f1a5a50f35981a369f5d5a69944e4726fe49e0b01141b078957"
BUDGETS = (8192, 65536, 524288)
CHANNELS = ("uniform", "eighth_copy", "half_copy", "earlier_word")
REPORTS = (
    (
        "train_source",
        11000000,
        "40f586a5016363714c2fc950f2202c5a67938625ff3d015f02638a6b1095a030",
    ),
    (
        "reporting_source",
        262144,
        "c13f864650df4e782af578430da4e36b00d542db0a3ba0014ad5fde568386a1d",
    ),
)
HERE = Path(__file__).resolve().parent
FITS = HERE / "text_aggregate_fits.json"


def tokens(role, stop, digest, directory):
    anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    record = next(x["result"] for x in anchor["results"] if x["case"] == "ngram")
    raw = tape(dict(record[role], bytes_read=2 * stop, prefix_sha256=digest), directory)
    return np.frombuffer(raw, dtype=np.uint16)


def vocabulary(prefix):
    counts = np.bincount(prefix, minlength=VOCAB)
    names = np.argsort(-counts, kind="stable")[: K - 1]
    classes = np.full(VOCAB, K - 1, dtype=np.int64)
    classes[names] = np.arange(K - 1)
    lexical_weights = 2 * counts + 1
    return names, classes, lexical_weights


def tables(tag, values):
    return np.bincount(tag * K + values, minlength=K * K).reshape(K, K)


def tags(channel, d, earlier, file_id):
    if channel == "earlier_word":
        return earlier
    j = CHANNELS.index(channel)
    rng = np.random.default_rng([1217, 5212, j, file_id])
    copy = rng.random(len(d)) < (0, 0.125, 0.5)[j]
    return np.where(copy, d, rng.integers(K, size=len(d)))


def stochastic(counts, fallback):
    totals = counts.sum(axis=1, keepdims=True)
    return np.divide(
        counts,
        totals,
        out=np.broadcast_to(fallback, counts.shape).astype(float).copy(),
        where=totals > 0,
    )


def em_fit(td, ty):
    count = ty.sum()
    dm = (td.sum(axis=0) + 0.5) / (td.sum() + 0.5 * K)
    u = (ty.sum(axis=0) + 0.5) / (count + 0.5 * K)
    weights = stochastic(td + dm, dm)
    theta = np.tile(u, (K, 1))
    for step in range(20001):
        fitted = weights @ theta
        factors = weights.T @ (ty / fitted)
        gradient = -(factors + TAU * u / theta)
        gap = float(
            ((gradient * theta).sum(axis=1) - gradient.min(axis=1)).sum()
            / (count + K * TAU)
        )
        if gap <= 1e-7 or step == 20000:
            break
        contributions = theta * factors + TAU * u
        theta = stochastic(contributions, u)
    observed_ty = ty.sum(axis=1)
    objective = -float(
        (ty * np.log(fitted)).sum() + TAU * (u * np.log(theta)).sum()
    ) / (count + K * TAU)
    return theta, {
        "em_steps": step,
        "convex_gap_per_effective_target": gap,
        "target_gap_met": gap <= 1e-7,
        "objective_per_effective_target": objective,
        "W_singular_values": np.linalg.svd(weights, compute_uv=False).tolist(),
        "W_rank": int(np.linalg.matrix_rank(weights)),
        "fit_excess_over_saturated_TY": float(
            (ty * np.log(stochastic(ty, u).clip(1e-300) / fitted)).sum()
            / observed_ty.sum()
        ),
        "fit_gain_over_marginal_TY": float((ty * np.log(fitted / u)).sum() / count),
    }


def deconvolve(td, ty, u):
    n = td.sum()
    match = np.trace(td) / n
    rate = float(np.clip((K * match - 1) / (K - 1), 0, 1))
    radius = K / (K - 1) * sqrt(log(40) / (2 * n))
    if rate <= radius:
        return np.tile(u, (K, 1)), rate, radius
    joint = (
        np.maximum(ty / ty.sum() - (1 - rate) * ty.sum(axis=0) / (K * ty.sum()), 0)
        / rate
    )
    prediction = stochastic(joint, u)
    return stochastic(td.sum(axis=0)[:, None] * prediction + TAU * u, u), rate, radius


def install(theta):
    return b"".join(quantize(row)[:-1].astype("<u2").tobytes() for row in theta).hex()


def unpack(packet):
    first = (
        np.frombuffer(bytes.fromhex(packet), dtype="<u2")
        .astype(np.int64)
        .reshape(K, K - 1)
    )
    return np.column_stack((first, 65536 - first.sum(axis=1)))


def fit_all(directory):
    words = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, _ = vocabulary(words[:HISTORY])
    coded = classes[words[FIT_START - 2 : FIT_END]]
    earlier, d, y = coded[:-2], coded[1:-1], coded[2:]
    difference = tables(earlier, d) - tables(d, y)
    endpoints = np.zeros((K, K), dtype=int)
    endpoints[earlier[0], d[0]] += 1
    endpoints[d[-1], y[-1]] -= 1
    assert np.array_equal(difference, endpoints)
    targets = np.random.default_rng([1217, 5211]).permutation(len(y))
    half = len(y) // 2
    sensors = {key: tags(key, d, earlier, 0) for key in CHANNELS}
    fits = []
    for n in BUDGETS:
        left, right = targets[:n], targets[half : half + n]
        paired = tables(d[right], y[right])
        u = (paired.sum(axis=0) + 0.5) / (n + 0.5 * K)
        row = {
            "positions_per_panel": n,
            "marginal": install(np.tile(u, (K, 1))),
            "paired": install(stochastic(paired + TAU * u, u)),
            "weak": {},
        }
        for key, tag in sensors.items():
            td, ty = tables(tag[left], d[left]), tables(tag[right], y[right])
            theta, details = em_fit(td, ty)
            model = {"packet": install(theta), **details}
            if key != "earlier_word":
                correction, rate, radius = deconvolve(td, ty, u)
                model.update(
                    deconvolution_packet=install(correction),
                    fitted_copy_rate=rate,
                    rate_radius=radius,
                )
            else:
                model["shifted_bigram_packet"] = install(stochastic(td + TAU * u, u))
            row["weak"][key] = model
        fits.append(row)
    return {
        "registration": ["7b8ff15", "48ec968"],
        "fit_prefix": FIT_SHA,
        "full_window_shifted_bigram_TV": float(np.abs(difference).sum() / (2 * len(y))),
        "class_names": names.tolist(),
        "fits": fits,
    }


def discrepancy(tag, d, y):
    td, ty, dy = (tables(*rows) for rows in ((tag, d), (tag, y), (d, y)))
    marginal = (dy.sum(axis=0) + 0.5) / (len(d) + K / 2)
    by_name = stochastic(dy, marginal)
    predicted = td @ by_name
    return float(np.abs(ty - predicted).sum() / (2 * len(d)))


def flat_score(packet, d, y, lexical_log, classes, within):
    mass = unpack(packet) / 65536
    assert np.all(mass > 0) and np.all(mass.sum(axis=1) == 1)
    residual = max(abs((row[classes] * within).sum() - 1) for row in mass)
    assert residual < 1e-12
    terms = -np.log(mass[d, y]) - lexical_log
    return {
        "mean_word_nll": float(terms.mean()),
        "block_nll": terms.reshape(8, -1).mean(axis=1).tolist(),
        "max_normalization_error": float(residual),
    }


def score_all(directory):
    receipt = json.loads(FITS.read_text())
    training = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, lexical = vocabulary(training[:HISTORY])
    assert names.tolist() == receipt["class_names"]
    totals = np.bincount(classes, weights=lexical, minlength=K)
    within = lexical / totals[classes]
    out = []
    for file_id, (role, start, digest) in enumerate(REPORTS, start=1):
        words = tokens(role, start + 65536, digest, directory)[start - 2 :]
        coded = classes[words]
        earlier, d, y = coded[:-2], coded[1:-1], coded[2:]
        lexical_log = np.log(within[words[2:]])
        base = -np.log(lexical[words[2:]] / lexical.sum())
        tags_tv = {
            key: discrepancy(tags(key, d, earlier, file_id), d, y) for key in CHANNELS
        }
        scores = []
        for fit in receipt["fits"]:
            packets = {"marginal": fit["marginal"], "paired": fit["paired"]}
            for key, model in fit["weak"].items():
                packets[key] = model["packet"]
                if "deconvolution_packet" in model:
                    packets[key + "_corrected"] = model["deconvolution_packet"]
                if "shifted_bigram_packet" in model:
                    packets["earlier_word_shifted_bigram"] = model[
                        "shifted_bigram_packet"
                    ]
            models = {
                k: flat_score(p, d, y, lexical_log, classes, within)
                for k, p in packets.items()
            }
            scores.append(
                {"positions_per_panel": fit["positions_per_panel"], "models": models}
            )
        out.append(
            {
                "file": role,
                "start": start,
                "prefix_sha256": digest,
                "word_targets": len(d),
                "lexical_unigram_nll": float(base.mean()),
                "observed_closure_TV": tags_tv,
                "scores": scores,
            }
        )
    return {
        "frozen_fit_sha256": hashlib.sha256(
            FITS.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        "reports": out,
    }


def r4_audit():
    receipt = json.loads(FITS.read_text())
    models = receipt["fits"][-1]["weak"]
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(HERE.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    alphabet = tuple(map(str, range(K)))
    transitions = [tuple(range(K)) for _ in range(K)]
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        for model in ("half_copy", "earlier_word"):
            rows = unpack(models[model]["packet"])
            slots = [Fraction(1), *(Fraction(2 * int(v) - 1) for v in rows.ravel())]
            heads = [[(i, 1 + i * K + j) for i in range(K)] for j in range(K)]
            event, start, sizes = categorical_program(
                alphabet, transitions, heads, slots
            )
            states = [event(token, start.delayed) for token in alphabet]
            assert start.probabilities == states[0].probabilities
            for i, state in enumerate(states):
                assert state.probabilities == tuple(
                    Fraction(int(v), 65536) for v in rows[i]
                )
                for j, token in enumerate(alphabet):
                    observed = event(token, state.delayed)
                    assert (
                        observed.delayed == states[j].delayed
                        and observed.probabilities == states[j].probabilities
                    )
    return {
        "raw_class_packets": 2,
        "state_output_checks_reset_and_edges": 2 * (1 + K * K),
        "nodes": sizes["nodes"],
        "delayed_cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["fit", "score", "r4"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        if args.operation == "fit":
            result = fit_all(args.data_dir)
        elif args.operation == "score":
            result = score_all(args.data_dir)
        else:
            result = r4_audit()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
