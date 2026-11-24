"""Measure normalized causal forecasts learned from anonymous grouped observations."""

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
from grouped_forecast import (
    ATOMS,
    UNIT,
    fit_grid,
    fit_harmonics,
    grid_law,
    harmonic_law,
    kt_counts,
    thinning,
)
from learn_resets import (
    calibration_logs,
    environment,
    fit_acquisition,
    histogram,
    information,
)
from scipy.stats import binom
from threadpoolctl import threadpool_limits


def logged_reports(streams, steps, seed):
    rng = np.random.default_rng(seed)
    coin, weights = environment("bright")
    worlds = rng.integers(2, size=streams)

    def pick():
        return coin[worlds, (rng.random(streams) >= weights[worlds, 0]).astype(int)]

    initial = pick()
    x = rng.random(streams) < initial
    a = rng.integers(2, size=streams)
    b = rng.random(streams) < np.where(a, pick(), initial)
    report = (rng.random((streams, steps)) < pick()[:, None]).astype(np.uint8)
    return (4 * x + 2 * a + b).astype(np.uint8), report


def reference_tables(row, steps):
    data = row["install"]
    coeff = np.array(data["harmonic_q15"]) / UNIT
    j = np.arange(1, coeff.shape[1] + 1)
    nodes = 2 * (steps + len(j) + 1)
    angle = (np.arange(nodes) + 0.375) * (2 * np.pi / nodes)
    density = (1 + 2 * coeff @ np.cos(j[:, None] * angle)) / nodes
    grid = np.array(data["grid_weights"])
    hist = np.array(data["hist_counts"]) + 0.5
    hist /= hist.sum(axis=1, keepdims=True)
    m = row["m"]
    tables = {name: [] for name in ("harmonic", "grid", "histogram", "half")}
    old = {}
    for t in range(steps + 1):
        k = np.arange(t + 1)
        direct = binom.pmf(k[:, None], t, np.cos(angle / 2) ** 2)
        mass = {
            "harmonic": density @ direct.T,
            "grid": grid_law(t, grid, row["grid_floor"]),
            "half": np.broadcast_to(kt_counts(t), (8, t + 1)),
        }
        if t <= m:
            mass["histogram"] = hist @ thinning(m, t)
        for name, law in mass.items():
            np.testing.assert_allclose(law.sum(axis=1), 1, rtol=0, atol=4e-13)
            if t:
                yes = (k[1:] / t) * law[:, 1:] / old[name]
                no = ((t - k[:-1]) / t) * law[:, :-1] / old[name]
                np.testing.assert_allclose(yes + no, 1, rtol=0, atol=4e-12)
                tables[name].append(yes)
        if t > m:
            tables["histogram"].append(tables["half"][-1])
        old = mass
    return tables


def expand_grid(row):
    weights = np.array(row["install"]["grid_weights"])
    offsets = np.r_[0, (weights > 0).sum(axis=1).cumsum()].astype(np.uint16)
    rr, aa = np.nonzero(weights)
    p = ATOMS[aa]
    floor = row["grid_floor"]
    with np.errstate(divide="ignore"):
        expanded = np.column_stack(
            [p, np.log((1 - floor) * weights[rr, aa]), np.log(p), np.log1p(-p)]
        )
    return offsets, np.ascontiguousarray(expanded), np.log(floor)


def acquisition(row):
    n, m = row["N"], row["m"]
    h, k = calibration_logs(row["family"], m, row["seed"], n)
    cut = 3 * n // 4
    samples = {
        name: [] for name in ("histograms", "harmonic", "grid", "histogram", "half")
    }
    for repetition in range(4):
        start = perf_counter()
        fit, val = histogram(h[:cut], k[:cut], m), histogram(h[cut:], k[cut:], m)
        _, response = fit_acquisition(fit)
        elapsed = (perf_counter() - start) * 1000
        if repetition:
            samples["histograms"].append(round(elapsed, 4))
        for name in ("harmonic", "grid", "histogram", "half"):
            start = perf_counter()
            if name == "harmonic":
                coeff, _, _ = fit_harmonics(fit, val)
                laws = harmonic_law(128, coeff.astype(float) / UNIT)
            elif name == "grid":
                weights, floor, _ = fit_grid(fit, val)
                laws = grid_law(128, weights, floor)
            elif name == "histogram":
                # Later predictions depend only on the first m bits, so all
                # action-relevant conditional information is in those m.
                laws = (fit + 0.5) / (fit.sum(axis=1, keepdims=True) + (m + 1) / 2)
            else:
                laws = np.broadcast_to(kt_counts(128), (8, 129))
            info = information(laws.reshape(2, 2, 2, -1), response)
            gain = info[:, 1] - info[:, 0]
            elapsed = (perf_counter() - start) * 1000
            np.testing.assert_allclose(
                gain, row["panels"]["128"][name]["gain"], atol=1e-10, rtol=0
            )
            if repetition:
                samples[name].append(round(elapsed, 4))
    return {
        "ordinary_training_and_selection_bits": n * (m + 2),
        "action_receipts": n,
        "numpy_histogram_bytes": fit.nbytes + val.nbytes,
        "warm_fit_and_decision_ms": samples,
    }


def run(path):
    data = json.loads(path.read_text(encoding="utf8"))
    row = next(r for r in data["fits"] if r["family"] == "bright" and "install" in r)
    n, steps, seed = 2048, 128, 46211
    history, raw = logged_reports(n, steps, seed)
    assert raw.shape == (n, steps) and len(np.unique(history)) == 8
    with threadpool_limits(limits=1):
        tabs = reference_tables(row, steps)
        train = acquisition(row)
    counts = np.cumsum(raw, axis=1, dtype=np.uint32) - raw
    ref = {
        name: np.column_stack(
            [tab[history, counts[:, t]] for t, tab in enumerate(series)]
        )
        for name, series in tabs.items()
    }
    m = row["m"]
    harmonic = np.array(row["install"]["harmonic_q15"], dtype=np.int16)
    offsets, gtable, floor_log = expand_grid(row)
    htable = np.concatenate(tabs["histogram"][:m], axis=1)
    degrees = harmonic.shape[1]
    stride = int(np.diff(offsets).max()) + 1
    hist_train = np.asarray(row["install"]["hist_counts"], dtype=np.uint32)

    def ptr(dtype):
        return np.ctypeslib.ndpointer(dtype, flags="C_CONTIGUOUS")

    u32, u8 = ctypes.c_uint32, ctypes.c_uint8
    p8, p16, pi16, p32, pd = (
        ptr(t) for t in (np.uint8, np.uint16, np.int16, np.uint32, np.float64)
    )
    with TemporaryDirectory() as tmp:
        (dll,) = compile_libraries(
            Path(tmp), ("address",), Path(__file__).with_name("grouped_predict.c")
        )
        binary = binary_sizes(dll)
        lib = ctypes.CDLL(str(dll))
        try:
            buy = lib.purchase
            buy.argtypes = [u32, u8, p8, p8]
            buy.restype = None
            first = (history // 4).astype(np.uint8)
            action = np.empty_like(first)
            policies = []
            for word in range(4):
                buy(n, word, first, action)
                np.testing.assert_array_equal(action, (word >> first) & 1)
                policies.append(int(action.sum()))

            fh, fg, ft = lib.harmonic_stream, lib.grid_stream, lib.prefix_stream
            fh.argtypes = [u32, u32, u32, pi16, p8, p8, p32, pd]
            ft.argtypes = [u32, u32, u32, pd, p8, p8, p32, pd]
            fg.argtypes = [u32, u32, u32, ctypes.c_double, p16, pd, p8, p8, p32, pd, pd]
            for f in (fh, fg, ft):
                f.restype = None
            entries = {
                "harmonic": (fh, (degrees, harmonic)),
                "grid_two_counts": (fg, (0, floor_log, offsets, gtable)),
                "grid_cached": (fg, (stride, floor_log, offsets, gtable)),
                "histogram": (ft, (m, htable)),
                "half": (ft, (0, np.zeros(1))),
            }
            timing, errors, live, scratch = {}, {}, {}, {}
            for name, (fn, args) in entries.items():
                is_grid = name.startswith("grid")
                target = ref["grid" if is_grid else name]
                carry = np.zeros((n, 2), np.uint32)
                extra = []
                live[name], scratch[name] = 8, 0
                if is_grid:
                    cache = np.zeros((n if name == "grid_cached" else 1, stride))
                    extra.append(cache)
                    if name == "grid_cached":
                        live[name] += cache.nbytes // n
                    else:
                        scratch[name] = cache.nbytes
                for start, stop in ((0, 37), (37, steps)):
                    block = np.ascontiguousarray(raw[:, start:stop])
                    got = np.empty(block.shape)
                    fn(n, stop - start, *args, history, block, carry, *extra, got)
                    np.testing.assert_allclose(
                        got, target[:, start:stop], atol=5e-12, rtol=0
                    )
                end_state = carry.copy()
                timing[name] = []
                got = np.empty(raw.shape)
                for i in range(8):
                    carry.fill(0)
                    for a in extra:
                        a.fill(0)
                    start = perf_counter()
                    fn(n, steps, *args, history, raw, carry, *extra, got)
                    elapsed = (perf_counter() - start) * 1000
                    if i:
                        timing[name].append(round(elapsed, 4))
                errors[name] = float(np.abs(got - target).max())
                np.testing.assert_array_equal(carry, end_state)
                np.testing.assert_array_equal(carry[:, 1], raw.sum(axis=1))
                assert np.all(carry[:, 0] == steps) and errors[name] < 5e-12
            reversal = np.repeat(np.array([0, 1, 0], np.uint8), [1024, 2048, 1024])
            grids = []
            for width in (0, stride):
                got = np.empty(len(reversal))
                fg(
                    1,
                    len(reversal),
                    width,
                    floor_log,
                    offsets,
                    gtable,
                    history[:1],
                    reversal,
                    np.zeros(2, np.uint32),
                    np.zeros(stride),
                    got,
                )
                grids.append(got)
            diff = float(np.max(np.abs(grids[0] - grids[1])))
            assert diff < 5e-12, (diff, int(np.argmax(np.abs(grids[0] - grids[1]))))
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)

    atoms = int(offsets[-1])
    # Each installation includes the packed decision for the selected rent/horizon.
    grid_packed = 1 + 8 + offsets.nbytes + atoms * 9
    grid_expanded = 1 + 8 + offsets.nbytes + gtable.nbytes
    return {
        "platform": os.name,
        "acquisition": train,
        "family": row["family"],
        "training_seed": row["seed"],
        "m": m,
        "N": row["N"],
        "streams": n,
        "steps": steps,
        "seed": seed,
        "history_counts": np.bincount(history).tolist(),
        "purchases_for_all_four_words": policies,
        "harmonic_degree": degrees,
        "grid_atoms_across_rows": atoms,
        "grid_max_row_atoms": stride - 1,
        "packed_model_bytes_including_policy": {
            "harmonic": 2 + harmonic.nbytes,
            "grid": grid_packed,
            "histogram": 2 + hist_train.nbytes,
            "half": 1,
        },
        "expanded_model_bytes_including_policy": {
            "harmonic": 2 + harmonic.nbytes,
            "grid": grid_expanded,
            "histogram": 2 + htable.nbytes,
            "half": 1,
        },
        "report_live_bytes_per_stream": live,
        "shared_serial_scratch_bytes": scratch,
        "history_selector_bytes_per_stream": 1,
        "draw_input_bytes": raw.nbytes,
        "forecast_output_bytes_per_method": 8 * raw.size,
        "warm_forward_ms": timing,
        "max_probability_error": errors,
        "reversed_draws": len(reversal),
        "reversed_grid_difference": diff,
        "binary": binary,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fits",
        type=Path,
        default=Path(__file__).with_name("learn_resets_result.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = json.dumps(run(args.fits), indent=2) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf8")
    else:
        print(content, end="")
