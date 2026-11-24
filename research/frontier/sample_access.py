"""Evaluate probability reads, sampled residual updates and sample-only raw-word generation."""

import _ctypes
import argparse
import ctypes
import hashlib
import json
import os
from math import factorial
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

import numpy as np
import torch
from address_anchors import load_archived_transformer
from causal_state import compile_libraries
from scipy.signal import lfilter
from sparse_directions import unpack
from sparse_transfer import REGISTRATION as REPLAY
from sparse_transfer import REPORT, WARM, WINDOWS, source_identity
from text import git_json, tape

REGISTRATION = "d87a5b1"
SEEDS = (211, 401, 587, 821, 1033, 1301, 1553, 1789)
BUDGETS = (1, 4, 16, 64)


class Kernel:
    def __enter__(self):
        self.tmp = TemporaryDirectory()
        (path,) = compile_libraries(
            Path(self.tmp.name),
            ("address",),
            Path(__file__).with_name("sample_access.c"),
        )
        self.lib = ctypes.CDLL(str(path))
        u = ctypes.c_uint32
        pd = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
        py = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
        self.lib.access_stream.argtypes = [
            u,
            pd,
            py,
            py,
            u,
            u,
            pd,
            ctypes.c_void_p,
            pd,
            pd,
        ]
        self.lib.access_stream.restype = None
        return self

    def __exit__(self, *exc):
        (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(self.lib._handle)
        self.tmp.cleanup()

    def run(self, q, y, draws, budget, packed, gain):
        carry = np.zeros(2, np.int16 if packed else np.float64)
        loss = np.empty(len(q))
        proposals = np.empty(len(q))
        self.lib.access_stream(
            len(q),
            q,
            y,
            draws,
            budget,
            int(packed),
            gain,
            carry.ctypes.data,
            loss,
            proposals,
        )
        return loss, proposals, carry


def variance_bounds(q, gain, rate, budget):
    noise = q * (1 - q) / budget
    prior_var = lfilter([0.0, rate**2], [1.0, -((1 - rate) ** 2)], noise, axis=0)
    return prior_var @ (gain**2) / 4


def exact_small():
    q = np.array([[0.2, 0.3], [0.35, 0.08], [0.17, 0.4], [0.4, 0.11], [0.12, 0.46]])
    y = np.array([0, 2, 1, 1, 2])
    g = np.array([2.0, -1.5])
    rows = []
    for rate in (0.125, 0.5):
        for budget in (1, 2, 3):
            sample = np.zeros((1, 2))
            mass = np.ones(1)
            exact = np.zeros(2)
            gap = 0.0
            for t, p in enumerate(q):

                def loss(states, base=p, target=y[t]):
                    z = states * g
                    return np.log(1 - base.sum() + np.exp(z) @ base) - (
                        z[:, target] if target < 2 else 0
                    )

                gap += float(mass @ loss(sample) - loss(exact[None, :])[0])
                if t + 1 == len(q):
                    break
                draw = []
                weights = []
                for i in range(budget + 1):
                    for j in range(budget - i + 1):
                        l = budget - i - j
                        draw.append([i / budget, j / budget])
                        weights.append(
                            factorial(budget)
                            / (factorial(i) * factorial(j) * factorial(l))
                            * p[0] ** i
                            * p[1] ** j
                            * (1 - p.sum()) ** l
                        )
                hit = (np.arange(2) == y[t]).astype(float)
                sample = (
                    (1 - rate) * sample[:, None, :]
                    + rate * (hit - np.array(draw)[None, :, :])
                ).reshape(-1, 2)
                mass = (mass[:, None] * weights).ravel()
                exact += (hit - p - exact) * rate
                np.testing.assert_allclose(mass @ sample, exact, atol=1e-13)
            bound = float(variance_bounds(q, g, rate, budget).sum())
            assert 0 <= gap <= bound
            rows.append(
                {
                    "rate": rate,
                    "budget": budget,
                    "terminal_sample_paths": len(mass),
                    "expected_gap": gap,
                    "upper": bound,
                }
            )
    return rows


def by_block(v, mean=False):
    f = np.mean if mean else np.sum
    return [float(f(v[a : a + REPORT])) for a in (WARM, WARM + REPORT)]


def replay(path, col, gain, lib, tape_id):
    with np.load(path, allow_pickle=False) as arrays:
        meta = source_identity(arrays)
        q = np.ascontiguousarray(arrays["mass"][:, col])
        y = np.full(len(q), 2, np.uint8)
        target = arrays["target"]
        for j, i in enumerate(col):
            y[target == i] = j
    zero = np.zeros((len(q), 2), np.uint8)
    ref = {}
    results = []
    for packed in (False, True):
        loss, proposals, _ = lib.run(q, y, zero, 0, packed, gain)
        ref[packed] = loss
        results.append(
            {
                "budget": 0,
                "packed": packed,
                "delta_to_base": by_block(loss),
                "expected_rejection_proposals": by_block(proposals, True),
            }
        )
    for budget in BUDGETS:
        for seed in SEEDS:
            rng = np.random.default_rng([seed, budget, tape_id])
            a = rng.binomial(budget, q[:, 0])
            b = rng.binomial(budget - a, q[:, 1] / (1 - q[:, 0]))
            draws = np.column_stack([a, b]).astype(np.uint8)
            for packed in (False, True):
                loss, proposals, _ = lib.run(q, y, draws, budget, packed, gain)
                results.append(
                    {
                        "budget": budget,
                        "seed": seed,
                        "packed": packed,
                        "delta_to_base": by_block(loss),
                        "gap_to_exact_reads": by_block(loss - ref[packed]),
                        "expected_rejection_proposals": by_block(proposals, True),
                    }
                )
    return {
        "source_arrays": meta["arrays_sha256"],
        "rows": results,
        "upper_on_mean_gap_float64": {
            str(b): by_block(variance_bounds(q, gain, 1 / 512, b)) for b in BUDGETS
        },
    }


def round_code(values):
    grid = np.clip(values * 32767, -32767, 32767)
    return (np.sign(grid) * np.floor(np.abs(grid) + 0.5)).astype(np.int16)


def sample_only(draw, shifts, indices, rng):
    upper = max(0.0, float(np.max(shifts)))
    proposals = 0
    while True:
        raw = draw()
        cls = indices.get(raw, 2)
        applied = shifts[cls] if cls < 2 else 0.0
        proposals += 1
        if rng.random() < np.exp(applied - upper):
            break
    purchased = draw()
    return raw, purchased, proposals


def generator(ids, gain, lib):
    ledger = {
        e["case"]: e["result"]
        for e in git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")["results"]
    }
    window = WINDOWS["separate_validation"]
    src = ledger["ngram"]["reporting_source"]
    data = np.frombuffer(
        tape(dict(src, bytes_read=2 * window.stop, prefix_sha256=window.sha), None),
        dtype=np.uint16,
    )
    starts = np.array([65536, 81920, 98304, 114688])
    indices = {int(raw): j for j, raw in enumerate(ids)}
    context = np.stack([data[p - 256 : p] for p in starts])
    rng = np.random.default_rng(71209)
    n = len(starts)
    steps = 128
    generated = np.empty((n, steps), dtype="<u2")
    bought = np.empty_like(generated)
    ntry = np.zeros((n, steps), np.uint32)
    expected = np.empty((n, steps))
    qlog = np.empty((n, steps, 2))
    dlog = np.empty((n, steps))
    state = np.zeros((n, 2), np.int16)
    max_error = 0.0
    selected = ledger["report"]["selected"]
    with TemporaryDirectory() as tmp:
        model, spec, _ = load_archived_transformer(
            selected, ledger[selected["case"]], None, Path(tmp)
        )
        assert spec.context == 256
        start = perf_counter()
        with (
            torch.inference_mode(),
            torch.autocast(device_type="cuda", dtype=torch.float16),
        ):
            for t in range(steps):
                x = torch.as_tensor(context.astype(np.int64), device="cuda")
                logits = model(x, last_only=True).double().cpu().numpy()
                for stream in range(n):
                    raw = logits[stream]
                    p = np.exp(raw - raw.max())
                    p /= p.sum()
                    cdf = np.cumsum(p)
                    cdf[-1] = 1
                    shifts = gain * state[stream].astype(float) / 32767
                    qlog[stream, t] = p[ids]
                    norm = 1 + float(p[ids] @ np.expm1(shifts))
                    expected[stream, t] = np.exp(max(0.0, shifts.max())) / norm

                    # The sampler sees only a base-draw callback, its names and its internal state.
                    def draw(cumulative=cdf):
                        return int(
                            np.searchsorted(cumulative, rng.random(), side="right")
                        )

                    y, extra, attempts = sample_only(draw, shifts, indices, rng)
                    generated[stream, t], bought[stream, t], ntry[stream, t] = (
                        y,
                        extra,
                        attempts,
                    )
                    tilted = raw.copy()
                    tilted[ids] += shifts
                    direct = np.exp(tilted - tilted.max())
                    direct /= direct.sum()
                    sparse = p.copy()
                    sparse[ids] *= np.exp(shifts)
                    sparse /= norm
                    max_error = max(
                        max_error,
                        float(np.abs(sparse - direct).max()),
                        abs(sparse.sum() - 1),
                    )
                    applied = shifts[indices[y]] if y in indices else 0.0
                    dlog[stream, t] = np.log(norm) - applied
                    s = state[stream].astype(float) / 32767
                    state[stream] = round_code(
                        s
                        + ((ids == y).astype(float) - (ids == extra).astype(float) - s)
                        / 512
                    )
                context = np.column_stack([context[:, 1:], generated[:, t]])
        seconds = perf_counter() - start
    assert max_error < 2e-14
    for stream in range(n):
        yy = np.array([indices.get(int(t), 2) for t in generated[stream]], np.uint8)
        bb = (bought[stream, :, None] == ids[None, :]).astype(np.uint8)
        loss, tries, end = lib.run(qlog[stream], yy, bb, 1, True, gain)
        np.testing.assert_array_equal(end, state[stream])
        np.testing.assert_allclose(loss, dlog[stream], rtol=0, atol=2e-15)
        np.testing.assert_allclose(tries, expected[stream], rtol=0, atol=3e-15)
    return {
        "seed": 71209,
        "starts": starts.tolist(),
        "continuation_tokens": steps * n,
        "base_proposals": int(ntry.sum()),
        "proposals_by_stream": ntry.sum(axis=1).tolist(),
        "additional_update_draws": steps * n,
        "conditional_expected_proposals": float(expected.sum()),
        "elapsed_seconds": seconds,
        "max_raw_probability_error": max_error,
        "final_q15": state.tolist(),
        "generated_ids_sha256": hashlib.sha256(generated.tobytes()).hexdigest(),
        "update_draws_sha256": hashlib.sha256(bought.tobytes()).hexdigest(),
    }


def run(directory):
    sel = json.loads(Path(__file__).with_name("sparse_selection.json").read_text())
    word = sel["selected"]["installed_and_live"]["2"]
    ids = np.array(sel["ids"], np.uint16)
    col, gain, packed = unpack(bytes.fromhex(word), ids)
    assert packed and len(col) == 2
    with Kernel() as lib:
        study = {
            n: replay(directory / f"sparse_{REPLAY}_{n}.npz", col, gain, lib, i)
            for i, n in enumerate(WINDOWS)
        }
        generated = generator(ids[col], gain, lib)
    elapsed = generated.pop("elapsed_seconds")
    return {
        "registration": REGISTRATION,
        "frozen_packet": word,
        "finite": exact_small(),
        "tapes": study,
        "generated": generated,
    }, elapsed


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    p.add_argument("--timing", type=Path)
    args = p.parse_args()
    result, elapsed = run(args.cache_dir)
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched sampled access, finite expectations and autoregressive replay.")
    elif args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
    if args.timing:
        args.timing.write_text(
            json.dumps({"autoregressive_seconds": elapsed}, indent=2) + "\n",
            encoding="utf8",
        )
