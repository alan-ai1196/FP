"""Execute the acquired affine rule on every raw report, including within-coordinate reads."""

import _ctypes
import argparse
import ctypes as ct
import json
import os
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from affine_reports import Source, parse_model, probability
from causal_state import binary_sizes, compile_libraries
from measure_reversible import ptr, timed

HERE = Path(__file__).resolve().parent
Q = 1 << 31


def encode(d, b, model):
    head = bytes((d, b, int(model is not None)))
    if model is None:
        return head
    mask, offset = model
    if not 0 <= mask < 1 << (d - 1) or offset not in (0, 1):
        raise ValueError("model does not fit the packet")
    return head + (mask | (offset << (d - 1))).to_bytes((d + 7) // 8, "little")


def test_tape(panel, b):
    seed, d = panel["seed"], panel["d"]
    source = Source(seed, d, panel["support_size_including_target"])
    x, y = source.sample(np.random.default_rng([seed, d, b, 8102]), 2048, b, 1)
    # Conditional on the count, every ordering of independent readings is equiprobable.
    rng = np.random.default_rng([seed, d, b, 4482])
    permutation = rng.random((*x.shape, b)).argsort(axis=2)
    bits = (permutation < x[:, :, None]).astype(np.uint8)
    previous_ones = bits.cumsum(axis=2, dtype=np.int16) - bits
    margin = np.arange(b) - 2 * previous_ones
    p_input = 0.5 - 0.25 * np.tanh(margin * np.log(3) / 2)
    tape = np.column_stack((bits.reshape(len(x), -1), y))
    return x, np.ascontiguousarray(tape.T), p_input.reshape(len(x), -1)


def setup(lib):
    lib.affine_carry_size.argtypes = []
    lib.affine_carry_size.restype = ct.c_uint32
    assert lib.affine_carry_size() == 8
    lib.affine_reset.argtypes = [ptr(np.uint8), ct.c_uint32, ptr(np.uint32)]
    lib.affine_reset.restype = None
    lib.affine_stream.argtypes = [
        ptr(np.uint8),
        ptr(np.uint32),
        ct.c_uint32,
        ct.c_uint32,
        ptr(np.uint8),
        ptr(np.uint32),
        ptr(np.float64),
    ]
    lib.affine_stream.restype = None


def replay(lib, panel, b, model, measure):
    d = panel["d"]
    packet = np.frombuffer(encode(d, b, model), np.uint8)
    lookup = np.array(
        [round(Q * F(3**j - 1, 3**j + 1)) for j in range(b + 1)], dtype=np.uint32
    )
    x, tape, p_input = test_tape(panel, b)
    reference = np.column_stack((p_input, probability(model, x, b))).T
    steps, n = tape.shape
    carry = np.zeros((n, 2), np.uint32)
    out = np.empty(tape.shape, dtype=np.float64)

    def reset():
        lib.affine_reset(packet, n, carry)

    def block(lo, hi):
        lib.affine_stream(packet, lookup, hi - lo, n, tape[lo:hi], carry, out[lo:hi])

    reset()
    start = carry.copy()
    cut = min(37, steps // 2)
    block(0, cut)
    block(cut, steps)
    np.testing.assert_array_equal(carry, start)
    err = np.abs(reference - out)
    bound = max(1, (int(model[0]).bit_count() if model else 0)) / (4 * Q)
    assert err.max() <= bound + 2e-16
    elapsed = timed(reset, lambda: block(0, steps)) if measure else None
    return {
        "seed": panel["seed"],
        "dimension": d,
        "reads_per_input": b,
        "installed": model is not None,
        "packet_hex": packet.tobytes().hex(),
        "packet_bytes": packet.nbytes,
        "channel_table_bytes": lookup.nbytes,
        "carry_bytes_per_stream": carry.nbytes // n,
        "events": int(tape.size),
        "output_bytes": out.nbytes,
        "split_after": cut,
        "max_input_error": float(err[:-1].max()),
        "max_terminal_error": float(err[-1].max()),
        "uniform_probability_error_bound": bound,
        "median_ms": elapsed,
    }


def run():
    panels = json.loads((HERE / "affine_reports_result.json").read_text())["panels"]
    with TemporaryDirectory() as tmp:
        (dll,) = compile_libraries(
            Path(tmp), ("address",), HERE / "affine_report_stream.c"
        )
        lib = ct.CDLL(str(dll))
        try:
            setup(lib)
            fits = []
            for panel in panels:
                successful = next(
                    x["fits"]["elimination"]["model"]
                    for x in panel["acquisition"]
                    if x["fits"]["elimination"]["correct"]
                )
                for b in (1, 17):
                    fits.append(
                        replay(
                            lib, panel, b, parse_model(successful), panel["seed"] == 173
                        )
                    )
            # The same normal entry point also installs the abstaining learner.
            abstention = replay(lib, panels[0], 17, None, False)
            return {"binary": binary_sizes(dll), "fits": fits, "abstention": abstention}
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
