"""Fit one named error state using only observed classes and purchased sample counts."""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.signal import lfilter
from sparse_transfer import REGISTRATION as REPLAY
from sparse_transfer import REPORT, WARM, source_identity
from threadpoolctl import threadpool_limits

RATE = 1 / 512
SEEDS = (211, 401, 587, 821)
BUDGETS = (1, 4, 16, 64, 1024)


def scores(frequencies, targets):
    errors = -frequencies.copy()
    errors[np.arange(len(errors)), targets] += 1
    before = lfilter([0.0, RATE], [1.0, RATE - 1], errors, axis=0)
    return -(before * errors).sum(axis=0), (before * before).sum(axis=0)


def empirical(slope, energy):
    g = np.clip(-4 * slope / np.maximum(energy, 1e-20), -64, 64)
    code = np.rint(256 * g).astype(int)
    g = code / 256
    value = -g * slope - g**2 * energy / 8
    i = int(np.argmax(value))
    return i, int(code[i]), float(value[i])


def acquire(targets, counts, budget):
    n, d = counts.shape
    assert np.all(counts.sum(axis=1) == budget)
    grad, energy = scores(counts.astype(float) / budget, targets)
    boundary = float(np.sqrt(2 * n / budget * np.log(2 * d / 0.05)))
    excess = np.maximum(abs(grad) - boundary, 0)
    j = int(np.argmax(excess))
    safe = -4 * np.sign(grad[j]) * excess[j] / n
    row = empirical(grad, energy)
    return {
        "index": row[0],
        "slope_Q8": row[1],
        "training_surrogate_gain": row[2],
        "maximum_abs_estimated_gradient": float(abs(grad).max()),
        "simultaneous_boundary": boundary,
        "certified_coordinate": j if excess[j] > 0 else None,
        "conservative_gain": float(safe),
        "certified_total_nats": float(2 * excess[j] ** 2 / n),
    }


def test(i, gamma, q, y, state):
    z = gamma * state[:, i]
    loss = np.log1p(q[:, i] * np.expm1(z)) - (y == i) * z
    return [float(loss[j : j + REPORT].sum()) for j in (WARM, WARM + REPORT)]


def run(directory):
    with (
        np.load(
            directory / "transformer_class_5907fd5.npz", allow_pickle=False
        ) as train,
        np.load(
            directory / f"sparse_{REPLAY}_separate_validation.npz", allow_pickle=False
        ) as val,
    ):
        train_meta = source_identity(train)
        val_meta = source_identity(val)
        q = train["mass"][:32768]
        y = train["target"][:32768]
        vq, vy, ids = val["mass"], val["target"], val["ids"]
        assert np.array_equal(ids, train["ids"])
    ve = -vq.copy()
    ve[np.arange(len(vq)), vy] += 1
    vst = lfilter([0.0, RATE], [1.0, RATE - 1], ve, axis=0)
    exact = empirical(*scores(q, y))
    oracle = {
        "index": exact[0],
        "slope_Q8": exact[1],
        "training_surrogate_gain": exact[2],
        "test_delta": test(exact[0], exact[1] / 256, vq, vy, vst),
    }
    rows = []
    start = perf_counter()
    for b in BUDGETS:
        for seed in SEEDS:
            rng = np.random.default_rng([seed, b])
            counts = rng.multinomial(b, q).astype(np.uint16)
            row = acquire(y, counts, b)
            i = row["index"]
            row.update(
                {
                    "seed": seed,
                    "samples_per_update": b,
                    "paid_base_draws": b * len(y),
                    "raw_id": int(ids[i]) if i < len(ids) else None,
                    "test_delta": test(i, row["slope_Q8"] / 256, vq, vy, vst),
                }
            )
            j = row["certified_coordinate"]
            row["conservative_test_delta"] = (
                test(j, row["conservative_gain"], vq, vy, vst)
                if j is not None
                else [0.0, 0.0]
            )
            rows.append(row)
    elapsed = perf_counter() - start
    return {
        "registration": "789f8ec",
        "train_arrays": train_meta["arrays_sha256"],
        "validation_arrays": val_meta["arrays_sha256"],
        "names": ids.tolist(),
        "exact_read": oracle,
        "fits": rows,
    }, elapsed


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache-dir", required=True, type=Path)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    args = p.parse_args()
    with threadpool_limits(limits=1):
        result, elapsed = run(args.cache_dir)
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched sample-only acquisition and validation.")
    elif args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
    print("Sampled fit and evaluation seconds", round(elapsed, 4))
