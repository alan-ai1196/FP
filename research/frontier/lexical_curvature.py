"""Choose the direction of a lexical split from ordinary prediction errors."""

import argparse
import ctypes as ct
import hashlib
import json
from itertools import pairwise, product
from math import prod
from pathlib import Path

import numpy as np
from lexical_switch import (
    BACKGROUND,
    FIT_END,
    FIT_SHA,
    FIT_START,
    HERE,
    POOLED,
    RANGES,
    TRAIN,
    VALID,
    Background,
    R,
    checksum,
    fit,
    native,
    summarize,
    tokens,
    windows,
)
from scipy.linalg import eigh
from scipy.signal import lfilter

REGISTRATION = "4cfe00c"
HOLDS = (1 / 2, 7 / 8, 31 / 32, 127 / 128)
STRENGTHS = (0, 1 / 8, 1 / 4, 1 / 2, 1)
WEIGHT = 1 / 4
ORDERS = ("chronological", "permuted")
RULES = ("exact", "linear")


def configure(lib):
    vector = np.ctypeslib.ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS")
    bins = np.ctypeslib.ndpointer(np.int32, ndim=1, flags="C_CONTIGUOUS")
    matrix = np.ctypeslib.ndpointer(np.float64, ndim=2, flags="C_CONTIGUOUS")
    lib.lag_matrix.argtypes = [
        ct.c_int,
        ct.c_int,
        ct.c_double,
        bins,
        vector,
        vector,
        matrix,
    ]
    lib.split_gains.argtypes = [
        ct.c_int,
        ct.c_double,
        ct.c_double,
        vector,
        vector,
        vector,
    ]
    lib.lag_matrix.restype = lib.split_gains.restype = None


def observed(background, row, window):
    _, _, y = window
    _, bigram, trigram = background.forecasts(*window)
    part = WEIGHT * row[y]
    pooled = (1 - WEIGHT) * trigram + part
    return background.bins[y].astype(np.int32), part / pooled, pooled, bigram, trigram


def lag_matrix(lib, bins, resp, hold, groups):
    work = np.zeros(groups)
    result = np.zeros((groups, groups))
    lib.lag_matrix(len(bins), groups, hold, bins, resp, work, result)
    return (result + result.T) / 2


def discover(lib, bins, resp, hold, mass):
    gram = lag_matrix(lib, bins, resp, hold, len(mass))
    root = np.sqrt(mass)
    # A Householder reflection sends sqrt(mass) to the last axis. The other
    # columns form an orthonormal basis of the mass-centering constraint.
    v = root.copy()
    v[-1] += 1
    v /= np.linalg.norm(v)
    basis = np.eye(len(mass))[:, :-1] - 2 * np.outer(v, v[:-1])
    basis /= root[:, None]
    reduced = basis.T @ gram @ basis
    values, vecs = eigh((reduced + reduced.T) / 2)
    w = basis @ vecs[:, -1]
    w -= mass @ w
    w /= w[np.argmax(abs(w))]
    assert abs(mass @ w) < 2e-13 and np.max(abs(w)) == 1
    feat = resp * w[bins]
    past = lfilter([0, hold], [1, -hold], feat)
    direct = float(past @ feat)
    squared_norm = float(mass @ (w * w))
    assert abs(direct - values[-1] * squared_norm) < 1e-8 * (1 + abs(direct))
    w.flags.writeable = False
    return w, {
        "smallest_eigenvalue": float(values[0]),
        "largest_eigenvalue": float(values[-1]),
        "runner_up_eigenvalue": float(values[-2]),
        "direct_quadratic_after_scaling": direct,
        "mass_squared_norm_after_scaling": squared_norm,
        "direction_sha256": hashlib.sha256(w.astype("<f8").tobytes()).hexdigest(),
    }


def gains(lib, feature, hold, strength):
    exact, linear = np.empty(len(feature)), np.empty(len(feature))
    lib.split_gains(len(feature), hold, strength, feature, exact, linear)
    return exact, linear


def experiment(lib, directory):
    tape = tokens("train_source", FIT_END, FIT_SHA, directory)
    bg = Background(*windows(tape, FIT_START, BACKGROUND))
    training = windows(tape, FIT_START + BACKGROUND, TRAIN)
    validation = windows(tape, FIT_START + BACKGROUND + TRAIN, VALID)
    y = training[2]
    model = fit(
        lib,
        POOLED,
        "pooled",
        WEIGHT,
        y,
        bg.forecasts(*training)[2],
        bg.bins[y],
        bg.unigram,
    )
    row = model[0][0]
    row.flags.writeable = False
    assert (
        checksum(*model, WEIGHT)
        == "58b7826c6cb9728620bc08d8bf996b1e03384a86049377570fb80935726c5f93"
    )
    mass = np.bincount(bg.bins, weights=row)
    ids, resp = observed(bg, row, training)[:2]
    vid, vr, pooled = observed(bg, row, validation)[:3]
    vloss = -np.log(pooled)
    permutation = np.random.default_rng(20261126).permutation(TRAIN)
    summaries, directions, chosen, grid = {}, {}, {}, []
    for order in ORDERS:
        indices, weights = (
            (ids, resp) if order == ORDERS[0] else (ids[permutation], resp[permutation])
        )
        for hold in HOLDS:
            w, record = discover(lib, indices, weights, hold, mass)
            key = f"{order}/{hold}"
            highest = np.argsort(-abs(w), kind="stable")[:5]
            record["largest_loading_token_ids"] = [
                int(bg.names[j]) if j < len(bg.names) else "tail" for j in highest
            ]
            record["largest_loadings"] = w[highest].tolist()
            record["training_gain_at_strength_one"] = float(
                gains(lib, weights * w[indices], hold, 1)[0].sum()
            )
            summaries[key], directions[key] = record, w
            feature = vr * w[vid]
            for strength in STRENGTHS:
                for rule, gain in zip(RULES, gains(lib, feature, hold, strength)):
                    nll = float((vloss - gain).mean())
                    entry = {
                        "order": order,
                        "rule": rule,
                        "hold": hold,
                        "strength": strength,
                        "validation": nll,
                        "direction": key,
                    }
                    grid.append(entry)
                    name = f"{order}_{rule}"
                    if name not in chosen or nll < chosen[name]["validation"]:
                        chosen[name] = entry
    # All choices are fixed before opening a reporting window. Historical
    # static averages are included only as already published control scores.
    previous = json.loads((HERE / "lexical_switch_result.json").read_bytes())
    reports = []
    for (role, start, digest), old in zip(RANGES, previous["reports"], strict=True):
        assert (old["role"], old["start"], old["prefix_sha256"]) == (
            role,
            start,
            digest,
        )
        data = tokens(role, start + R, digest, directory)
        ids, resp, pooled, bigram, trigram = observed(bg, row, windows(data, start, R))
        baseline = -np.log(pooled)
        scores = {
            key: summarize(values)
            for key, values in (
                ("pooled", baseline),
                ("bigram", -np.log(bigram)),
                ("trigram", -np.log(trigram)),
            )
        }
        for k in scores:
            assert abs(scores[k]["total"] - old["losses"][k]["total"]) < 1e-7
        scores["static_EM_average"] = old["postregistration_controls"][
            "fixed_rows_balanced_nll"
        ]
        for name, selected in chosen.items():
            feature = resp * directions[selected["direction"]][ids]
            out = gains(lib, feature, selected["hold"], selected["strength"])
            scores[name] = summarize(baseline - out[RULES.index(selected["rule"])])
        reports.append(
            {
                "role": role,
                "start": start,
                "tokens": R,
                "prefix_sha256": digest,
                "losses": scores,
            }
        )
    return {
        "registration": REGISTRATION,
        "selection": chosen,
        "directions": summaries,
        "validation": grid,
        "one_training_matrix_bytes": len(mass) ** 2 * 8,
        "matrix_coordinate_visits": len(ORDERS) * len(HOLDS) * TRAIN * len(mass),
        "one_stored_direction_bytes": len(mass) * 8,
        "reports": reports,
    }


def check(lib):
    bins = np.array([0, 1, 0, 2, 1, 0], dtype=np.int32)
    resp = np.array([1 / 2, 1, 1 / 4, 3 / 4, 1 / 2, 1])
    for hold in (0.0, -0.75, 0.5, 1.0):
        g = lag_matrix(lib, bins, resp, hold, 3)
        direct = np.zeros_like(g)
        for t, x in enumerate(bins):
            for s in range(t):
                direct[x, bins[s]] += hold ** (t - s) * resp[t] * resp[s]
        np.testing.assert_array_equal(g, (direct + direct.T) / 2)
    tests = 0
    for signs in product((-1, 1), repeat=4):
        feature = np.array(signs, dtype=float)
        for hold in (-0.75, 0.0, 0.5, 0.875):
            for strength in (0, 0.125, 0.5):
                exact, linear = gains(lib, feature, hold, strength)
                # Sum the 16 latent paths with their actual transition mass.
                ratio = sum(
                    prod(1 + strength * s * y for s, y in zip(path, signs))
                    / 2
                    * prod((1 + hold * s * t) / 2 for s, t in pairwise(path))
                    for path in product((-1, 1), repeat=4)
                )
                assert abs(np.exp(exact.sum()) - ratio) < 2e-14
                u = 0.0
                for i, sign in enumerate(signs):
                    assert abs(np.expm1(linear[i]) - u * strength * sign) < 2e-14
                    u = np.clip(hold * (u + strength * sign), -1, 1)
                tests += 1
    return {
        "lag_matrix_entries": 4 * 9,
        "direct_hidden_path_comparisons": tests,
        "independent_linear_token_checks": 4 * tests,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with native() as library:
        configure(library)
        result = (
            check(library)
            if args.command == "check"
            else experiment(library, args.directory)
        )
    data = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(data.encode())
    else:
        print(data, end="")
