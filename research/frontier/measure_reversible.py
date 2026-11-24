"""Check resumed native recurrences, cached periods and the learned Bayesian quotient."""

import _ctypes
import argparse
import ctypes as ct
import json
import os
from functools import partial
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter

import numpy as np
from causal_state import binary_sizes, compile_libraries
from reversible_pairs import stream
from reversible_reports import decode, forward, test_draw

HERE = Path(__file__).resolve().parent


def divisor_compilation(table):
    period = len(table)
    weights = {}
    for d in range(1, period + 1):
        if period % d == 0:
            increment = int(table[d % period]) - sum(
                w for h, w in weights.items() if d % h == 0
            )
            if increment:
                weights[d] = increment
    if any(
        sum(w for h, w in weights.items() if t % h == 0) != value
        for t, value in enumerate(table)
    ):
        return None
    base = weights.pop(1, 0)
    return (
        base,
        np.array(list(weights), np.uint16),
        np.array(list(weights.values()), np.int8),
    )


def ptr(dtype):
    return np.ctypeslib.ndpointer(dtype=dtype, flags="C_CONTIGUOUS")


def timed(prepare, execute):
    times = []
    for k in range(10):
        prepare()
        start = perf_counter()
        execute()
        if k:
            times.append((perf_counter() - start) * 1000)
    return round(median(times), 5)


def pairs(lib, packet):
    u8, u16, u32, i8 = ct.c_uint8, ct.c_uint16, ct.c_uint32, ct.c_int8
    pi, pb, ph = ptr(np.int8), ptr(np.uint8), ptr(np.uint16)
    coef = np.array(packet["coefficients"], np.int8)
    initial = np.array(packet["initial"], np.int8)
    d, period = len(initial), packet["period"]
    assert d < 255 and period < 65536 and packet["denominator"] <= 127
    assert (
        coef.tolist() == packet["coefficients"]
        and initial.tolist() == packet["initial"]
    )
    assert sum(abs(int(x)) for x in coef) * packet["denominator"] < 2**31
    table = np.array(stream(packet, period), np.int8)
    base, divisors, weights = divisor_compilation(table)
    count = 1048576
    expected = np.resize(table, count)
    out = np.empty(count, np.int8)
    state = initial.copy()
    pos8 = np.zeros(1, np.uint8)
    pos16 = np.zeros(1, np.uint16)
    arms = {
        "rec": ([u32, u8, pi, pi, pb, pi], [d, coef, state, pos8], 2 + 2 * d, d + 1),
        "table": ([u32, u16, pi, ph, pi], [period, table, pos16], 3 + period, 2),
        "divisors": (
            [u32, u16, u8, i8, ph, pi, ph, pi],
            [period, len(weights), base, divisors, weights, pos16],
            5 + 3 * len(weights),
            2,
        ),
    }

    def reset():
        state[:] = initial
        pos8.fill(0)
        pos16.fill(0)

    rows = {}
    for arm, (types, arguments, size, carry) in arms.items():
        fn = getattr(lib, "pair_" + arm)
        fn.argtypes, fn.restype = types, None
        reset()
        for start, end in ((0, 37), (37, count)):
            fn(end - start, *arguments, out[start:end])
        np.testing.assert_array_equal(out, expected)
        elapsed = timed(reset, partial(fn, count, *arguments, out))
        np.testing.assert_array_equal(out, expected)
        rows[arm] = {
            "installed_shape_bytes": size,
            "carry_bytes": carry,
            "median_ms": elapsed,
        }
    return {
        "steps": count,
        "resumed_after": 37,
        "output_bytes": out.nbytes,
        "implementations": rows,
        "shared_readout_bytes": 16,
        "divisor_base": base,
        "divisors": divisors.tolist(),
        "weights": weights.tolist(),
        "absolute_accumulator_bound": sum(abs(int(x)) for x in coef)
        * packet["denominator"],
    }


def reports(lib, fit):
    packet = bytes.fromhex(fit["packet_hex"])
    model = decode(packet)
    edges, f, g, prior = model
    actions, raw, _ = test_draw(fit["seed"], 1024)
    expected, terminal = forward(model, actions, raw)
    edges = np.ascontiguousarray(np.vstack([edges, np.arange(len(f))]), np.uint8)
    actions = np.ascontiguousarray(
        np.vstack([actions, np.full(raw.shape[1], len(edges) - 1)]), np.uint8
    )
    raw = np.ascontiguousarray(raw, np.uint8)
    steps, n = raw.shape
    belief = np.tile(prior, (n, 1))
    out = np.empty(raw.shape)
    fn = lib.report_stream
    fn.argtypes = [
        ct.c_uint32,
        ct.c_uint32,
        ct.c_uint8,
        ptr(np.uint8),
        ptr(np.float64),
        ptr(np.uint8),
        ptr(np.uint8),
        ptr(np.float64),
        ptr(np.float64),
    ]
    fn.restype = None

    def call(start, end):
        fn(
            end - start,
            n,
            len(f),
            edges,
            f,
            raw[start:end],
            actions[start:end],
            belief,
            out[start:end],
        )

    for start, end in ((0, 37), (37, steps)):
        call(start, end)
    old_error = float(np.max(np.abs(expected - out)))
    new_error = float(np.max(np.abs(terminal - belief @ g)))
    assert max(old_error, new_error) < 2e-14

    def reset():
        belief[:] = prior

    elapsed = timed(reset, lambda: call(0, steps))
    np.testing.assert_allclose(out, expected, atol=2e-14, rtol=0)
    return {
        "events": steps * n,
        "streams": n,
        "resumed_after": 37,
        "median_ms": elapsed,
        "prediction_bytes": out.nbytes,
        "input_bytes": raw.nbytes + actions.nbytes,
        "installed_bytes": len(packet),
        "decoded_bytes_including_identity": edges.nbytes + f.nbytes + g.nbytes,
        "carry_bytes": belief.nbytes // n,
        "max_f_error": old_error,
        "max_g_error": new_error,
    }


def run():
    pairs_result = json.loads((HERE / "reversible_pairs_result.json").read_text())
    reportfits = json.loads((HERE / "reversible_reports_result.json").read_text())[
        "fits"
    ]
    packet = pairs_result["installations"][0]
    with TemporaryDirectory() as tmp:
        (dll,) = compile_libraries(
            Path(tmp), ("address",), HERE / "reversible_stream.c"
        )
        lib = ct.CDLL(str(dll))
        try:
            return {
                "binary": binary_sizes(dll),
                "pair_prediction": pairs(lib, packet),
                "all_reports": reports(lib, reportfits[0]),
            }
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(run(), indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
