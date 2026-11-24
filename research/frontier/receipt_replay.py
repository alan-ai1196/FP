"""Evaluate frozen sample-acquired directed programs on two new chronological text tapes."""

import argparse
import ctypes
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from direction_learning import decode as dense_decode
from receipt_program import REGISTRATION, program_indices
from sample_acquisition import RATE
from sparse_directions import Native, unpack
from sparse_transfer import REPORT, WARM, WINDOWS, source_identity
from threadpoolctl import threadpool_limits
from transformer_class_features import Window, extract

FROZEN = "dd990a1"
HERE = Path(__file__).resolve().parent
END_HASH = {
    "next_training": "609b678cec8bc841e27120f61244e55c21d0265ae2c00ab373bd585d81bf4a26",
    "separate_validation": "08b2d9ef425f94df288664d3ec3c4f1c01206b0f592ceecfd236b2ec5f9ad26d",
}


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf8"))


def new_window(key):
    old = WINDOWS[key]
    start = old.stop
    return Window(
        REGISTRATION,
        old.source,
        start - WARM,
        start + REPORT // 2,
        start + 2 * REPORT,
        start,
        old.sha,
        END_HASH[key],
        (start, start + REPORT),
    )


def blocks(values, mean=False):
    op = np.mean if mean else np.sum
    return [float(op(values[i : i + REPORT])) for i in (WARM, WARM + REPORT)]


def columns(edges):
    states = sorted({(src, h) for src, _, h, _ in edges})
    return (
        np.array([i for i, _ in states], np.uint8),
        np.array([2.0**-h for _, h in states]),
        np.array([dst for _, dst, _, _ in edges], np.uint8),
        np.array([states.index((src, h)) for src, _, h, _ in edges], np.uint8),
        np.array([g for _, _, _, g in edges]),
    )


class Replay(Native):
    def __enter__(self):
        super().__enter__()
        pd = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
        pu = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
        ps = np.ctypeslib.ndpointer(np.int16, flags="C_CONTIGUOUS")
        u = ctypes.c_uint32
        self.lib.directed_stream.argtypes = [
            u,
            u,
            pd,
            pd,
            pu,
            u,
            pu,
            pd,
            u,
            pu,
            pu,
            pd,
            ps,
            pd,
            pd,
        ]
        self.lib.directed_stream.restype = u
        return self

    def directed(self, q, frequency, y, plan, carry):
        src, rate, dest, owner, gain = plan
        if len(src) > 3 or len(dest) > 3:
            raise ValueError("packet exceeds the supported rule count")
        loss, prop = np.empty(len(y)), np.empty(len(y))
        fixes = self.lib.directed_stream(
            len(y),
            q.shape[1],
            q,
            frequency,
            y,
            len(src),
            src,
            rate,
            len(dest),
            dest,
            owner,
            gain,
            carry,
            loss,
            prop,
        )
        return loss, prop, int(fixes)


def inspect(arrays, q, y, frequency, ids, words, old_cols, old_gain, one_gain, lib):
    edges = {w: program_indices(bytes.fromhex(w), ids) for w in words}
    shifts = {h for rules in edges.values() for _, _, h, _ in rules} | {9}
    states = {h: lib.histories(frequency, y, True, 2.0**-h) for h in shifts}
    checks = {"dense_probability_nll": 0.0, "stream_loss": 0.0}
    base = arrays["nll"]
    dense, ix, target = (
        arrays["dense"],
        arrays["dense_indices"],
        arrays["dense_targets"],
    )
    mapping = np.full(dense.shape[1], len(ids), np.int32)
    mapping[ids] = np.arange(len(ids))

    def verify(z, loss):
        tilted = dense * np.exp(z[ix][:, mapping])
        tilted /= tilted.sum(axis=1, keepdims=True)
        gap = float(
            abs(-np.log(tilted[np.arange(len(ix)), target]) - base[ix] - loss[ix]).max()
        )
        checks["dense_probability_nll"] = max(checks["dense_probability_nll"], gap)
        assert gap < 2e-11

    packets = {}
    for w, rules in edges.items():
        plan = columns(rules)
        carry = np.zeros(len(plan[0]), np.int16)
        loss, proposals, repairs = lib.directed(q, frequency, y, plan, carry)
        reset = np.zeros_like(carry)
        first, _, _ = lib.directed(q[:37], frequency[:37], y[:37], plan, reset)
        rest, _, _ = lib.directed(q[37:], frequency[37:], y[37:], plan, reset)
        np.testing.assert_array_equal(np.r_[first, rest], loss)
        np.testing.assert_array_equal(carry, reset)
        z = np.zeros_like(q)
        for src, dst, h, g in rules:
            z[:, dst] = g * states[h][:, src]
        applied = z[np.arange(len(y)), y]
        log_total = np.log((q * np.exp(z)).sum(axis=1))
        err = float(abs(loss - (log_total - applied)).max())
        assert err < 1e-12
        checks["stream_loss"] = max(checks["stream_loss"], err)
        verify(z, loss)
        ablations = []
        for _, dst, _, _ in rules:
            old = z[:, dst].copy()
            z[:, dst] = 0
            dropped = np.log((q * np.exp(z)).sum(axis=1)) - z[np.arange(len(y)), y]
            ablations.append(blocks(dropped - loss))
            z[:, dst] = old
        packets[w] = {
            "saved_nats": blocks(-loss),
            "rule_marginal_saved_nats": ablations,
            "mean_proposals": blocks(proposals, True),
            "live_state_bytes": carry.nbytes,
            "stable_normalizer_fallbacks": repairs,
        }
    # The old two-name learner is quantized. The old complementary state is binary64.
    z = np.zeros_like(q)
    z[:, old_cols] = states[9][:, old_cols] * old_gain
    loss = np.log((q * np.exp(z)).sum(axis=1)) - z[np.arange(len(y)), y]
    verify(z, loss)
    pair = blocks(-loss)
    from scipy.signal import lfilter

    tail = lfilter(
        [0.0, RATE], [1.0, RATE - 1], (y == len(ids)).astype(float) - frequency[:, -1]
    )
    complements = {}
    for code in sorted(set(one_gain)):
        value = tail * (code / 256)
        complements[str(code)] = blocks(
            (y == len(ids)) * value - np.log1p(q[:, -1] * np.expm1(value))
        )
    return {
        "programs": packets,
        "prior_two_name_saved_nats": pair,
        "prior_complement_saved_nats_by_Q8": complements,
        "checks": checks,
    }


def run(directory):
    frozen = read("receipt_selection.json")
    assert frozen["registration"] == REGISTRATION
    original = read("sample_acquisition_result.json")
    previous = {
        (r["samples_per_update"], r["seed"]): r["slope_Q8"] for r in original["fits"]
    }
    assert all(r["index"] == len(frozen["ids"]) for r in original["fits"])
    pair = read("sparse_selection.json")["selected"]["installed_and_live"]["2"]
    old_cols, old_gain, packed = unpack(bytes.fromhex(pair), frozen["ids"])
    assert packed
    static_bytes = bytes.fromhex(
        read("transformer_directions_result.json")["models"]["static"]["packet_hex"]
    )
    kind, _, static_ids, (static_gain,) = dense_decode(static_bytes)
    assert kind == "static" and list(static_ids) == frozen["ids"]
    words = sorted(
        {rec["packet"] for r in frozen["fits"] for rec in r["programs"].values()}
    )
    tapes, timings = {}, {}
    for index, name in enumerate(END_HASH):
        window = new_window(name)
        path = directory / f"receipt_{REGISTRATION}_{name}.npz"
        if not path.exists():
            extract(path, window=window, fixed_ids=frozen["ids"])
        with np.load(path, allow_pickle=False) as arrays, Replay() as lib:
            meta = source_identity(arrays)
            assert (
                meta["prefix_sha256"] == window.sha
                and meta["registration"] == REGISTRATION
            )
            q, y, ids = arrays["mass"], arrays["target"], arrays["ids"]
            np.testing.assert_array_equal(ids, frozen["ids"])
            static = static_gain[y] - np.log((q * np.exp(static_gain)).sum(axis=1))
            exact = inspect(
                arrays, q, y, q, ids, words, old_cols, old_gain, previous.values(), lib
            )
            rows = []
            eval_start = perf_counter()
            for r in frozen["fits"]:
                b, seed = r["budget"], r["seed"]
                frequency = (
                    np.random.default_rng([seed, b, 2525, index])
                    .multinomial(b, q)
                    .astype(float)
                    / b
                )
                selected = sorted({v["packet"] for v in r["programs"].values()})
                gain = previous[b, seed]
                data = inspect(
                    arrays,
                    q,
                    y,
                    frequency,
                    ids,
                    selected,
                    old_cols,
                    old_gain,
                    [gain],
                    lib,
                )
                rows.append(
                    {
                        "budget": b,
                        "seed": seed,
                        "packets_by_cap": {
                            c: v["packet"] for c, v in r["programs"].items()
                        },
                        "prior_complement_Q8": gain,
                        **data,
                    }
                )
            elapsed = perf_counter() - eval_start
            primary = frozen["fits"][-1]["programs"]["32"]["packet"]
            plan = columns(program_indices(bytes.fromhex(primary), ids))
            warm = np.zeros(len(plan[0]), np.int16)
            lib.directed(q[:WARM], q[:WARM], y[:WARM], plan, warm)
            times = []
            for rep in range(8):
                carry = warm.copy()
                start = perf_counter()
                lib.directed(q[WARM:], q[WARM:], y[WARM:], plan, carry)
                if rep:
                    times.append((perf_counter() - start) * 1000)
            stable = {
                k: v
                for k, v in meta.items()
                if k not in ("extraction_seconds", "gpu_peak_allocated_bytes")
            }
            tapes[name] = {
                "source": stable,
                "base_nll_per_word": blocks(arrays["nll"], True),
                "static_saved_nats": blocks(static),
                "exact_updates": exact,
                "sampled_updates": rows,
            }
            timings[name] = {
                "extraction_seconds": meta["extraction_seconds"],
                "gpu_peak_allocated_bytes": meta["gpu_peak_allocated_bytes"],
                "all_sampled_evaluator_seconds": elapsed,
                "timed_packet": primary,
                "native_report_ms": times,
                "compiled_library": lib.binary,
            }
    return {
        "registration": REGISTRATION,
        "frozen_selection_commit": FROZEN,
        "warmup": WARM,
        "block_size": REPORT,
        "static_installation_bytes": len(static_bytes),
        "prior_two_name_packet": pair,
        "tapes": tapes,
    }, timings


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache-dir", type=Path, required=True)
    dest = p.add_mutually_exclusive_group(required=True)
    dest.add_argument("--write", type=Path)
    dest.add_argument("--check", type=Path)
    p.add_argument("--timing", type=Path)
    a = p.parse_args()
    with threadpool_limits(limits=1):
        result, timing = run(a.cache_dir)
    if a.check:
        assert compare(result, json.loads(a.check.read_text(encoding="utf8")))
    else:
        a.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    if a.timing:
        a.timing.write_text(json.dumps(timing, indent=2) + "\n", encoding="utf8")
    print(
        "Scored both tapes, with every registered deletion, sampled history, and exact-update control."
    )
