"""Time ordinary paired-bit calibration and deployment from the same learned packet."""

import _ctypes
import argparse
import ctypes
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

import numpy as np
from causal_state import binary_sizes, compile_libraries
from coin_calibration import (
    CENTER,
    HORIZONS,
    PRECISION,
    A,
    agreement,
    packet_grid,
    quadrature,
)
from scipy.special import logsumexp
from scipy.stats import binom


def expanded(code, n, bits):
    values, edges = packet_grid(n, bits)
    p = values[code]
    odds = (p / (1 - p)) ** np.arange(CENTER + 1)
    positive = (p * odds + 1 - p) / (odds + 1)
    release = np.rint(PRECISION * np.r_[positive, p]).astype(np.uint16)
    nodes, weights = quadrature(1024)
    # Sum in log space over the agreement counts mapping to this received code.
    likelihood = np.full(len(nodes), -np.inf)
    for offset in range(edges[code], edges[code + 1], 128):
        counts = np.arange(offset, min(edges[code + 1], offset + 128))
        block = binom.logpmf(counts[:, None], n, agreement(nodes))
        likelihood = np.logaddexp(likelihood, logsumexp(block, axis=0))
    logw = np.log(weights) + likelihood
    logw -= logsumexp(logw) + np.log(2)
    biases = np.r_[nodes, 1 - nodes]
    table = np.stack([biases, np.log(biases), np.log1p(-biases), np.tile(logw, 2)])
    return release, table


def references(raw, limit, release, table):
    steps = raw.shape[1]
    counts = np.cumsum(raw, axis=1, dtype=np.int32) - raw
    s = 2 * counts - np.arange(steps)
    hit = np.abs(s) == limit
    first = np.argmax(hit, axis=1)
    stopped = hit.any(axis=1)[:, None] & (np.arange(steps) >= first[:, None])
    state = np.where(stopped, s[np.arange(len(raw)), first, None], s)
    magn = np.abs(state)
    q = release[np.where((magn <= CENTER) & (magn < limit), magn, CENTER + 1)]
    counter = np.where(state >= 0, q, PRECISION - q) / PRECISION
    probs = np.empty(raw.shape)
    bias, lp, lq, logw = table
    for i in range(len(raw)):
        for start in range(0, steps, 128):
            times = np.arange(start, min(steps, start + 128))
            ones = counts[i, times, None]
            logpost = logw + ones * lp + (times[:, None] - ones) * lq
            probs[i, times] = np.exp(
                logsumexp(logpost + np.log(bias), axis=1) - logsumexp(logpost, axis=1)
            )
    return {"counter": counter, "bayes": probs}


def run():
    n = steps = 16384
    bits = 7
    streams = 2
    limit = int(np.ceil(np.log(steps) / np.log(A / (1 - A))))
    rng = np.random.default_rng(31717)
    theta = 0.76
    train = (rng.random((n, 2)) < rng.choice([theta, 1 - theta], n)[:, None]).astype(
        np.uint8
    )
    raw = (rng.random((streams, steps)) < np.array([theta, 1 - theta])[:, None]).astype(
        np.uint8
    )
    count = int((train[:, 0] == train[:, 1]).sum())
    _, edges = packet_grid(n, bits)
    code = int(np.searchsorted(edges[1:-1], count, side="right"))
    release, table = expanded(code, n, bits)
    reference = references(raw, limit, release, table)
    u32 = ctypes.c_uint32

    def ptr(kind):
        return np.ctypeslib.ndpointer(dtype=kind, flags="C_CONTIGUOUS")

    pu, pi, pq, pn, pd = (
        ptr(k) for k in (np.uint8, np.int8, np.uint16, np.uint32, np.float64)
    )
    with TemporaryDirectory() as tmp:
        (dll,) = compile_libraries(
            Path(tmp), ("address",), Path(__file__).with_name("coin_predict.c")
        )
        binary = binary_sizes(dll)
        lib = ctypes.CDLL(str(dll))
        try:
            acquire = lib.pair_packet
            acquire.argtypes = [pu, u32, u32]
            acquire.restype = u32
            boundary = lib.packet_for_matches
            boundary.argtypes = [u32, u32, u32]
            boundary.restype = u32
            count_checks = 0
            for t in HORIZONS:
                middle = (t.bit_length() - 1) // 2
                for size in (t // 16, t, 16 * t):
                    for b in (middle - 2, middle, middle + 2):
                        _, cuts = packet_grid(size, b)
                        for successes in np.unique(
                            np.clip(np.r_[cuts, cuts - 1], 0, size)
                        ):
                            assert boundary(int(successes), size, b) == np.searchsorted(
                                cuts[1:-1], successes, side="right"
                            )
                            count_checks += 1
            acquisition = []
            for _ in range(9):
                start = perf_counter()
                actual = acquire(train, n, bits)
                acquisition.append(round((perf_counter() - start) * 1000, 4))
                assert actual == code
            functions = {
                "counter": lib.calibrated_stream,
                "bayes": lib.grid_from_counts,
                "cached_bayes": lib.grid_with_weights,
            }
            functions["counter"].argtypes = [u32, u32, ctypes.c_int8, pq, pu, pi, pd]
            functions["bayes"].argtypes = [u32, u32, u32, pd, pu, pn, pd]
            functions["cached_bayes"].argtypes = [u32, u32, u32, pd, pu, pn, pd, pd]
            grid_args = (table.shape[1], table)
            args = {
                "counter": (limit, release),
                "bayes": grid_args,
                "cached_bayes": grid_args,
            }
            reference["cached_bayes"] = reference["bayes"]
            states = {
                "counter": (np.zeros(streams, np.int8),),
                "bayes": (np.zeros((streams, 2), np.uint32),),
                "cached_bayes": (
                    np.zeros((streams, 2), np.uint32),
                    np.zeros((streams, table.shape[1])),
                ),
            }
            samples, errors = {}, {}
            for name, fn in functions.items():
                fn.restype = None
                state = states[name]
                for a, b in ((0, 37), (37, steps)):
                    block = np.ascontiguousarray(raw[:, a:b])
                    output = np.empty(block.shape)
                    fn(streams, b - a, *args[name], block, *state, output)
                    np.testing.assert_allclose(
                        output, reference[name][:, a:b], rtol=0, atol=5e-12
                    )
                final = [a.copy() for a in state]
                samples[name] = []
                output = np.empty(raw.shape)
                for i in range(6):
                    for a in state:
                        a.fill(0)
                    start = perf_counter()
                    fn(streams, steps, *args[name], raw, *state, output)
                    elapsed = (perf_counter() - start) * 1000
                    if i:
                        samples[name].append(round(elapsed, 4))
                errors[name] = float(np.abs(output - reference[name]).max())
                assert errors[name] < 5e-12
                for a, end in zip(state, final):
                    np.testing.assert_array_equal(a, end)
            # An extreme prefix can temporarily suppress a component which later recovers.
            reversal = np.repeat(np.array([0, 1, 0], np.uint8), [1024, 2048, 1024])
            stress = []
            for name in ("bayes", "cached_bayes"):
                carry = [np.zeros_like(a[0:1]) for a in states[name]]
                forecast = np.empty(len(reversal))
                functions[name](
                    1, len(reversal), *grid_args, reversal, *carry, forecast
                )
                stress.append(forecast)
            reversal_error = float(np.abs(stress[0] - stress[1]).max())
            assert reversal_error < 5e-12
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)
    return {
        "N": n,
        "T": steps,
        "streams": streams,
        "seed": 31717,
        "true_amplitude": theta,
        "matches": count,
        "packet_bits": bits,
        "packet_code": code,
        "snapped_amplitude": packet_grid(n, bits)[0][code],
        "limit": limit,
        "expanded_Q12_bytes": release.nbytes,
        "bayes_table_bytes": table.nbytes,
        "live_bytes_per_stream": {
            k: sum(a.nbytes for a in s) // streams for k, s in states.items()
        },
        "reversed_prefix_draws": len(reversal),
        "reversed_prefix_cache_difference": reversal_error,
        "threshold_count_checks": count_checks,
        "training_input_bytes": train.nbytes,
        "report_input_bytes": raw.nbytes,
        "output_bytes_per_predictor": output.nbytes,
        "acquisition_cpu_ms": acquisition,
        "warm_cpu_ms": samples,
        "max_probability_difference": errors,
        "binary": binary,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(run(), indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf8")
    else:
        print(text, end="")
