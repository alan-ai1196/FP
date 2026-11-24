"""Replay frozen sparse packets on the next training-file and separate validation-file tapes."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from direction_learning import decode, loss_shift
from measure_directions import Native as DirectionNative
from measure_directions import initial as initial_direction
from sparse_directions import REGISTRATION, Native, encode, unpack
from threadpoolctl import threadpool_limits
from transformer_class_features import Window, extract

WARM, REPORT = 4096, 32768
WINDOWS = {
    "next_training": Window(
        REGISTRATION,
        "train_source",
        8568832 - WARM,
        8568832 + REPORT // 2,
        8634368,
        8568832,
        "465c041d897528e706cca4ba39aa3126496cebb07a3aa7886ec5019899d2083a",
        "42a01239aec27ccf2da459f34857995ace9ea627dc435fcfefcf0c77cd5d4993",
        (8568832, 8568832 + REPORT),
    ),
    "separate_validation": Window(
        REGISTRATION,
        "reporting_source",
        65536 - WARM,
        65536 + REPORT // 2,
        131072,
        65536,
        "60ce3d7f22480d6b6699f223c37279ac137fbeb18b431dbc0cdf2c9ebb912180",
        "a2a7b20166f93aea0f345d25c3543b0079348de283b87d6a627075dc6d1b7b48",
        (65536, 65536 + REPORT),
    ),
}


def summarize(base, delta):
    sl = (slice(WARM, WARM + REPORT), slice(WARM + REPORT, None))
    return {
        "block_nll": [float(np.mean((base + delta)[s])) for s in sl],
        "delta_nats": [float(np.sum(delta[s])) for s in sl],
        "anchor_nll": [
            float(np.mean((base + delta)[s.start : s.start + 4096])) for s in sl
        ],
    }


def source_identity(arrays):
    meta = json.loads(str(arrays["metadata"]))
    h = hashlib.sha256()
    for k in ("mass", "target", "old_mass", "old_hits", "nll", "ids", "old_ids"):
        h.update(k.encode())
        h.update(arrays[k].tobytes())
    assert h.hexdigest() == meta["arrays_sha256"]
    return meta


def score(arrays, selection, old, lib, direction):
    meta = source_identity(arrays)
    ids = np.asarray(selection["ids"], np.uint16)
    np.testing.assert_array_equal(arrays["ids"], ids)
    q, y, base = arrays["mass"], arrays["target"], arrays["nll"]
    chosen = {v for rules in selection["selected"].values() for v in rules.values()}
    _, _, _, (gamma,) = decode(
        bytes.fromhex(old["models"][old["selected"]]["packet_hex"])
    )
    full = encode(tuple(range(len(ids) + 1)), ids, gamma, False).hex()
    chosen.update(("", full))
    rows, timing = {}, {}
    dense = arrays["dense"]
    mapping = np.full(dense.shape[1], len(ids), np.int32)
    mapping[ids] = np.arange(len(ids))
    ix = arrays["dense_indices"]
    targets = arrays["dense_targets"]
    all_states = {packed: lib.histories(q, y, packed) for packed in (False, True)}
    exact_error = 0.0
    for word in sorted(chosen):
        col, coef, packed = unpack(bytes.fromhex(word), ids)
        carry = np.zeros(len(col), np.int16 if packed else np.float64)
        prefix, _ = lib.stream(q[:WARM], y[:WARM], col, coef, carry)
        initial = carry.copy()
        report, repairs = lib.stream(q[WARM:], y[WARM:], col, coef, carry)
        whole = np.r_[prefix, report]
        state = np.zeros_like(carry)
        first, _ = lib.stream(q[:37], y[:37], col, coef, state)
        rest, _ = lib.stream(q[37:], y[37:], col, coef, state)
        np.testing.assert_array_equal(state, carry)
        np.testing.assert_allclose(np.r_[first, rest], whole, atol=2e-13, rtol=0)
        z = np.zeros(q.shape)
        z[:, col] = all_states[packed][:, col] * coef
        direct = loss_shift(q, y, z)
        err = float(np.max(np.abs(direct - whole)))
        assert err < 2e-12
        tilted = dense * np.exp(z[ix][:, mapping])
        tilted /= tilted.sum(axis=1, keepdims=True)
        dense_err = float(
            np.max(
                np.abs(
                    -np.log(tilted[np.arange(len(ix)), targets]) - (base + whole)[ix]
                )
            )
        )
        assert dense_err < 2e-11
        exact_error = max(exact_error, dense_err, err)
        rows[word] = {
            **summarize(base, whole),
            "coordinates": len(col),
            "packed": packed,
            "bytes": len(bytes.fromhex(word)),
            "live": carry.nbytes,
            "tail": bool(len(ids) in col),
            "positive_normalizer_fallbacks": repairs,
        }
        samples = []
        for j in range(8):
            state = initial.copy()
            start = perf_counter()
            got, _ = lib.stream(q[WARM:], y[WARM:], col, coef, state)
            spent = (perf_counter() - start) * 1000
            if j:
                samples.append(round(spent, 4))
        np.testing.assert_allclose(got, report, atol=1e-14, rtol=0)
        timing[word] = samples
    rank = old["best_in_family"]["scalar"]
    radial = decode(bytes.fromhex(old["models"][rank]["packet_hex"]))
    scalar = direction.release(radial, q, y, initial_direction(radial))
    rows["previous_scalar"] = summarize(base, scalar)
    dense_full = decode(bytes.fromhex(old["models"][old["selected"]]["packet_hex"]))
    check = direction.release(dense_full, q, y, initial_direction(dense_full))
    np.testing.assert_allclose(
        rows[full]["delta_nats"],
        summarize(base, check)["delta_nats"],
        atol=3e-9,
        rtol=0,
    )
    stable = {
        k: v
        for k, v in meta.items()
        if k not in ("extraction_seconds", "gpu_peak_allocated_bytes")
    }
    return {
        "source": stable,
        "packets": rows,
        "original_full": full,
        "max_dense_or_reference_error": exact_error,
    }, {
        "gpu_extraction_seconds": meta["extraction_seconds"],
        "gpu_allocated_bytes": meta["gpu_peak_allocated_bytes"],
        "cpu_ms_per_packet": timing,
        "checked_native_binary": lib.binary,
    }


def run(directory, only_extract=False):
    here = Path(__file__).resolve().parent
    choice = json.loads((here / "sparse_selection.json").read_text(encoding="utf8"))
    old = json.loads(
        (here / "transformer_directions_result.json").read_text(encoding="utf8")
    )
    assert choice["registration"] == REGISTRATION
    outputs, timings = {}, {}
    for name, window in WINDOWS.items():
        path = directory / f"sparse_{REGISTRATION}_{name}.npz"
        if not path.exists():
            extract(path, window=window, fixed_ids=choice["ids"])
        if not only_extract:
            with (
                np.load(path, allow_pickle=False) as arrays,
                Native() as lib,
                DirectionNative() as direction,
            ):
                assert (
                    json.loads(str(arrays["metadata"]))["prefix_sha256"] == window.sha
                )
                outputs[name], timings[name] = score(
                    arrays, choice, old, lib, direction
                )
    return {
        "registration": REGISTRATION,
        "frozen_selection_commit": "d3cb0fc",
        "warm_targets": WARM,
        "report_targets_per_block": REPORT,
        "selected": choice["selected"],
        "tapes": outputs,
    }, timings


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache-dir", required=True, type=Path)
    p.add_argument("--extract", action="store_true")
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    p.add_argument("--timing", type=Path)
    args = p.parse_args()
    with threadpool_limits(limits=1):
        result, times = run(args.cache_dir, args.extract)
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched both independent tape replays and all installed subsets.")
    elif args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    elif not args.extract:
        print(json.dumps(result, indent=2))
    if args.timing:
        args.timing.write_text(json.dumps(times, indent=2) + "\n", encoding="utf8")
