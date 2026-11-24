"""Evaluate learned input/output directions on fresh normalized Transformer forecasts."""

import argparse
import hashlib
import json
from itertools import pairwise
from pathlib import Path
from time import perf_counter

import numpy as np
from direction_learning import decode, fit_words, history, loss_shift
from measure_directions import Native, initial, reference_logits
from text_addresses import RENT
from text_persistence import score_delta
from threadpoolctl import threadpool_limits
from transformer_class_features import (
    BLOCK,
    CHECKPOINT,
    FIT_SIZE,
    REGISTRATION,
    SHA,
    extract,
)
from word_persistence import Kernels, unpack
from word_persistence import fit as fit_old
from word_persistence import initial as old_initial
from word_persistence import packet as old_packet

REPORT = FIT_SIZE + BLOCK
CUTS = (0, FIT_SIZE, REPORT, REPORT + BLOCK, REPORT + 2 * BLOCK)


def metrics(base, delta, word, live):
    loss = base + delta
    block_losses = [float(loss[a:b].mean()) for a, b in pairwise(CUTS)]
    return {
        "packet_hex": word.hex(),
        "bytes": len(word),
        "live_bytes": live,
        "block_nll": block_losses,
        "selection_priced_nll": block_losses[1] + 8 * len(word) * RENT / BLOCK,
        "report_delta_nats": [float(delta[a : a + BLOCK].sum()) for a in CUTS[2:4]],
        "anchor_nll": [float(loss[a : a + 4096].mean()) for a in CUTS[2:4]],
    }


def dense_check(cache, ids, z, score):
    ix = cache["dense_indices"]
    raw = cache["dense"]
    targets = cache["dense_targets"]
    mapping = np.full(raw.shape[1], len(ids), np.int32)
    mapping[ids] = np.arange(len(ids))
    corrected = raw * np.exp(z[ix][:, mapping])
    corrected /= corrected.sum(axis=1, keepdims=True)
    error = float(
        np.max(np.abs(-np.log(corrected[np.arange(len(ix)), targets]) - score[ix]))
    )
    assert error < 1e-11
    return error


def run(cache):
    meta = json.loads(str(cache["metadata"]))
    assert (meta["registration"], meta["prefix_sha256"], meta["checkpoint_sha256"]) == (
        REGISTRATION,
        SHA,
        CHECKPOINT,
    )
    sig = hashlib.sha256()
    for name in ("mass", "target", "old_mass", "old_hits", "nll", "ids", "old_ids"):
        sig.update(name.encode())
        sig.update(cache[name].tobytes())
    assert sig.hexdigest() == meta["arrays_sha256"]
    q, y, ids, base = (cache[k] for k in ("mass", "target", "ids", "nll"))
    errors = -q.copy()
    errors[np.arange(len(q)), y] += 1
    signature = {
        "arrays_sha256": meta["arrays_sha256"],
        "prefix_sha256": SHA,
        "checkpoint_sha256": CHECKPOINT,
    }
    candidate = {"base": metrics(base, np.zeros(len(y)), b"", 0)}
    train = perf_counter()
    words, certificates = fit_words(q[:FIT_SIZE], y[:FIT_SIZE], ids)
    fit_ms = (perf_counter() - train) * 1000
    timing = {}
    discrepancy = raw_error = 0.0
    keyed = {}
    states = {}
    with Native() as lib:
        binary = lib.binary
        for word in words:
            decoded = decode(word)
            kind, rate, named, _ = decoded
            np.testing.assert_array_equal(named, ids)
            key = kind if kind == "static" else f"{kind}/{rate:g}"
            keyed[key] = decoded
            carry = initial(decoded)
            parts = []
            for a, b in pairwise(CUTS):
                parts.append(lib.release(decoded, q[a:b], y[a:b], carry))
            measured = np.concatenate(parts)
            init = initial(decoded)
            first = lib.release(decoded, q[:37], y[:37], init)
            rest = lib.release(decoded, q[37:], y[37:], init)
            np.testing.assert_allclose(np.r_[first, rest], measured, atol=2e-13, rtol=0)
            np.testing.assert_allclose(carry, init, atol=3e-14, rtol=0)
            if rate not in states:
                states[rate] = history(errors, rate)
            z = reference_logits(word, states[rate], errors)
            direct = loss_shift(q, y, z)
            err = float(np.abs(direct - measured).max())
            assert err < 2e-11, (key, err)
            discrepancy = max(discrepancy, err)
            raw_error = max(raw_error, dense_check(cache, ids, z, base + measured))
            candidate[key] = metrics(base, measured, word, carry.nbytes)
            candidate[key]["rate"] = rate
        timing_names = {}
        for kind in ("static", "scalar", "scalar_i16", "common", "diagonal"):
            available = [k for k in keyed if k.split("/")[0] == kind]
            win = min(available, key=lambda k: candidate[k]["selection_priced_nll"])
            timing_names[kind] = win
            decoded = keyed[win]
            start = initial(decoded)
            lib.release(decoded, q[:REPORT], y[:REPORT], start)
            samples = []
            for j in range(8):
                carry = start.copy()
                begin = perf_counter()
                out = lib.release(decoded, q[REPORT:], y[REPORT:], carry)
                elapsed = (perf_counter() - begin) * 1000
                if j:
                    samples.append(round(elapsed, 4))
            assert abs(out.sum() - sum(candidate[win]["report_delta_nats"])) < 1e-8
            timing[win] = samples
    # The earlier 256-word set is a separate hypothesis and its names are charged.
    old_r, old_y, old_ids = (cache[k] for k in ("old_mass", "old_hits", "old_ids"))
    with Kernels() as old:
        start = perf_counter()
        x, old_traces = fit_old("residual", old, old_r[:FIT_SIZE], old_y[:FIT_SIZE])
        old_ms = (perf_counter() - start) * 1000
        word = old_packet("residual", x)
        carry = old_initial(*unpack(word))
        pred = old.release(word, old_r, old_y, carry)
        delta = score_delta(pred, old_r, old_y)
        complete = word + old_ids.astype("<u2").tobytes()
        candidate["older_class"] = metrics(base, delta, complete, carry.nbytes)
        mem = old_initial(*unpack(word))
        old.release(word, old_r[:REPORT], old_y[:REPORT], mem)
        samples = []
        for i in range(8):
            carry = mem.copy()
            begin = perf_counter()
            old.release(word, old_r[REPORT:], old_y[REPORT:], carry)
            elapsed = (perf_counter() - begin) * 1000
            if i:
                samples.append(round(elapsed, 4))
        timing["older_class"] = samples
    selected = min(candidate, key=lambda k: candidate[k]["selection_priced_nll"])
    metadata = {
        k: v
        for k, v in meta.items()
        if k not in ("extraction_seconds", "gpu_peak_allocated_bytes")
    }
    results = {
        "registration": REGISTRATION,
        "source": metadata,
        "raw_ids": ids.tolist(),
        "quadratic_certificates": certificates,
        "models": candidate,
        "best_in_family": timing_names,
        "selected": selected,
        "older_class_starts": old_traces,
        "max_reference_score_error": discrepancy,
        "dense_raw_word_max_error": raw_error,
    }
    times = {
        "source": signature,
        "feature_extraction_seconds": meta["extraction_seconds"],
        "gpu_peak_allocated_bytes": meta["gpu_peak_allocated_bytes"],
        "all_named_fits_ms": fit_ms,
        "older_class_fit_ms": old_ms,
        "cpu_replay_ms": timing,
        "report_predictive_category_bytes": q[REPORT:].nbytes,
        "report_class_input_bytes": y[REPORT:].nbytes,
        "report_correction_output_bytes": base[REPORT:].nbytes,
        "compiled_binary": binary,
    }
    return results, times


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    p.add_argument("--timing", type=Path)
    args = p.parse_args()
    if not args.cache.exists():
        extract(args.cache)
    with np.load(args.cache, allow_pickle=False) as arrays, threadpool_limits(limits=1):
        results, times = run(arrays)
    if args.check:
        assert compare(results, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched chronological Transformer corrections and charged selection.")
    elif args.write:
        args.write.write_text(json.dumps(results, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(results, indent=2))
    if args.timing:
        args.timing.write_text(json.dumps(times, indent=2) + "\n", encoding="utf8")
