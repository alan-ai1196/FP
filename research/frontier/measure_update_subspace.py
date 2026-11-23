"""Time byte-counted native learning states on the identical registered feedback streams."""

import argparse
import ctypes
import json
import os
import tempfile
from pathlib import Path
from time import perf_counter

import numpy as np
from causal_state import binary_sizes, compile_libraries
from text_update_subspace import BANK, N, load_data, loglik, prepare, replay
from threadpoolctl import threadpool_limits
from ticket_policy import A, B
from update_subspace import DiscoveredAssignment, PivotCode


def control_trajectory(state, word, offers, incidence):
    p = np.empty((N, 4))
    buy = np.zeros(N, dtype=bool)
    bank = word[:, BANK]
    for i, j in enumerate(offers.names):
        p[i] = state.weights() @ bank[i]
        buy[i] = np.clip(p[i, j], A, B) >= offers.prices[i]
        if buy[i]:
            v = loglik(bank[i, :, j], offers.purchase(i, j))
            if incidence:
                state.observe(j, v)
            else:
                state.observe(v)
    return p, buy


def run(data):
    import _ctypes

    with threadpool_limits(limits=1):
        controls = {}
        snaps, streams, _ = prepare(data, controls)
        methods = ("posterior", "ratios", "learned_512", "semantic")
        expected = {}
        for name in methods:
            records = [replay(name, word, off, snaps) for _, _, _, word, off in streams]
            expected[name] = (
                np.stack([v[0] for v in records]),
                np.stack([v[1] >= 0 for v in records]),
            )
        pivot = PivotCode(snaps[512][0])
        incidence = controls[512][1]
        if incidence is None:
            raise ValueError("anonymous incidence could not be recovered")
        for label in ("pivot", "incidence"):
            is_incidence = label == "incidence"
            records = [
                control_trajectory(
                    DiscoveredAssignment(incidence) if is_incidence else pivot.state(),
                    word,
                    off,
                    is_incidence,
                )
                for _, _, _, word, off in streams
            ]
            expected[label] = tuple(
                np.stack(part) for part in zip(*records, strict=True)
            )
        methods = (*methods, "pivot", "incidence")
    basis = np.require(snaps[512][0].ravel(), requirements=["A", "C"])
    header = np.frombuffer(bytes([9, 23]), dtype=np.uint8)
    index_bytes = 5
    pivot_head = np.frombuffer(pivot.packet[:index_bytes], dtype=np.uint8)
    pivot_decoder = np.frombuffer(pivot.packet[index_bytes:], dtype="<f8").copy()
    incidence_head = np.frombuffer(incidence, dtype=np.uint8)
    words = np.ascontiguousarray([word for _, _, _, word, _ in streams])
    names = np.ascontiguousarray([off.names for *_, off in streams])
    prices = np.ascontiguousarray([off.prices for *_, off in streams])
    # This is an environment-side buffer. Native code reads its bit only after committing to buy.
    rewards = np.ascontiguousarray(
        [[off.purchase(i, int(off.names[i])) for i in range(N)] for *_, off in streams],
        dtype=np.uint8,
    )
    count = len(streams)
    out = np.empty((count, N, 4))
    buy = np.empty((count, N), dtype=np.uint8)
    u = ctypes.c_uint32

    def ptr(dtype):
        return np.ctypeslib.ndpointer(dtype=dtype, ndim=1, flags="C_CONTIGUOUS")

    d, b = ptr(np.float64), ptr(np.uint8)
    report = {
        "group_streams": count,
        "opportunities_per_stream": N,
        "compared_forecasts": 4 * count * N,
        "paid_bits": int(expected["posterior"][1].sum()),
        "cpu_ms": {},
        "native_allocated_state_bytes": {},
        "post_hoc_controls": {
            "groups_per_arm": {str(n): v[0] for n, v in controls.items()},
            "incidence_recognized": {
                str(n): v[1] is not None for n, v in controls.items()
            },
            "pivot_shared_bytes": len(pivot.packet),
            "pivot_condition_number": pivot.condition,
            "incidence_shared_bytes": len(incidence),
            "reference_differences": {},
        },
    }
    source = Path(__file__).with_name("update_replay.c")
    with tempfile.TemporaryDirectory() as td:
        (path,) = compile_libraries(Path(td), ("both",), source)
        report["binary"] = binary_sizes(path)
        dll = ctypes.CDLL(str(path))
        try:
            fn = dll.replay_updates
            fn.argtypes = [u, u, u, u, d, b, b, d, b, d, b, d, d, b]
            fn.restype = None
            for mode, (name, width) in enumerate(
                zip(methods, (24, 23, 9, 9, 9, 9), strict=True)
            ):
                state = np.empty((count, width))
                args = (
                    mode,
                    count,
                    N,
                    9,
                    pivot_decoder if name == "pivot" else basis,
                    pivot_head
                    if name == "pivot"
                    else (incidence_head if name == "incidence" else header),
                    BANK.ravel(),
                    words.ravel(),
                    names.ravel(),
                    prices.ravel(),
                    rewards.ravel(),
                    state.ravel(),
                    out.ravel(),
                    buy.ravel(),
                )
                fn(*args)
                prediction, decisions = expected[name]
                assert np.max(np.abs(out - prediction)) < 1e-11 and np.array_equal(
                    buy, decisions
                ), name
                if name in ("pivot", "incidence"):
                    ref, actions = expected["posterior"]
                    report["post_hoc_controls"]["reference_differences"][name] = {
                        "max_abs_probability": float(np.max(np.abs(out - ref))),
                        "buy_differences": int(np.count_nonzero(buy != actions)),
                    }
                samples = []
                for _ in range(7):
                    start = perf_counter()
                    fn(*args)
                    samples.append(round((perf_counter() - start) * 1000, 4))
                report["cpu_ms"][name] = samples
                report["native_allocated_state_bytes"][name] = state.nbytes
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(dll._handle)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    s = json.dumps(run(load_data(args.data_dir)), indent=2) + "\n"
    if args.write:
        args.write.write_text(s, encoding="utf8")
    else:
        print(s, end="")
