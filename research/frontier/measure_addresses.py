"""Replay frozen packed address and trigram models sequentially and in a teacher-forced GPU batch."""

import argparse
import ctypes
import json
import os
import tempfile
from pathlib import Path
from time import perf_counter

import numpy as np
from causal_state import binary_sizes, compile_libraries
from text_addresses import REPORT_END, SELECT_END, fit, load_data, serialize


def measure_cpu(path, common_arrays, arms, symbol="score_stream"):
    import _ctypes

    lib = ctypes.CDLL(str(path))
    try:
        fn = getattr(lib, symbol)
        fn.restype = None

        def ptr(dtype):
            return np.ctypeslib.ndpointer(dtype=dtype, ndim=1, flags="C_CONTIGUOUS")

        fn.argtypes = [
            ptr(np.uint16),
            ctypes.c_uint32,
            ptr(np.uint32),
            ptr(np.uint32),
            ptr(np.uint32),
            ptr(np.uint16),
            ptr(np.uint32),
            ctypes.c_uint32,
            ptr(np.uint8),
            ctypes.c_uint32,
            ptr(np.float64),
        ]
        result = {}
        out = np.empty(int(common_arrays[1]), dtype=np.float64)
        for name, (model, kind, expected) in arms.items():
            args = (*common_arrays, model, kind, out)
            fn(*args)
            assert np.max(np.abs(out - expected)) < 1e-11, name
            samples = []
            for _ in range(5):
                start = perf_counter()
                fn(*args)
                samples.append(round(1e3 * (perf_counter() - start), 4))
            result[name] = samples
        return result
    finally:
        (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)


def measure_gpu(source, common_arrays, arms, symbol="score_batch"):
    import cupy as cp

    module = cp.RawModule(
        code=source.read_text(encoding="utf8"), options=("--std=c++14",)
    )
    kernel = module.get_function(symbol)
    base = tuple(
        cp.asarray(a) if isinstance(a, np.ndarray) else np.uint32(a)
        for a in common_arrays
    )
    n = int(common_arrays[1])
    out = cp.empty(n, dtype=cp.float64)
    result = {}
    for name, (model, kind, expected) in arms.items():
        args = (*base, cp.asarray(model), np.uint32(kind), out)
        grid, block = ((n + 255) // 256,), (256,)
        kernel(grid, block, args)
        assert np.max(np.abs(cp.asnumpy(out) - expected)) < 1e-11, name
        samples = []
        for _ in range(5):
            start, stop = cp.cuda.Event(), cp.cuda.Event()
            start.record()
            for _ in range(10):
                kernel(grid, block, args)
            stop.record()
            stop.synchronize()
            samples.append(round(float(cp.cuda.get_elapsed_time(start, stop)) / 10, 4))
        result[name] = samples
    props = cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)
    return {
        "device": props["name"].decode(),
        "cupy": cp.__version__,
        "cuda_runtime": cp.cuda.runtime.runtimeGetVersion(),
        "milliseconds": result,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--gpu", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--precision",
        action="store_true",
        help="replay the four subsequent blocks with learned fractions",
    )
    group.add_argument(
        "--correction",
        action="store_true",
        help="replay the learned output correction and its matched raw rows",
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    if args.correction:
        from mixture_addresses import FRESH_END
        from output_correction import (
            END,
            base_backoff,
            current_only_control,
            fixed_output_probability,
            train_study,
        )
        from output_correction import load_data as correction_data

        data = correction_data(args.data_dir)
        fitted, fraction, models, matched, _, _ = train_study(data[:SELECT_END])
        start, stop = FRESH_END, END
    elif args.precision:
        from mixture_addresses import FRESH_END, replication_data, train

        data = replication_data(args.data_dir)
        fitted, fraction, constant_fraction, _ = train(data)
        start, stop = REPORT_END, FRESH_END
    else:
        data = load_data(args.data_dir)
        fitted = fit(data[:SELECT_END])
        start, stop = SELECT_END, REPORT_END
    common, pair, constant, routes = (
        fitted.common,
        fitted.pair,
        fitted.constant,
        fitted.routes,
    )
    tri, active, info, hybrid = (
        fitted.trigram,
        fitted.active,
        fitted.info,
        fitted.hybrid,
    )
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = common.observe(ids, start, stop)
    tape = ids[start - 2 : stop]
    degrees = np.bincount((common.keys >> 16).astype(np.intp), minlength=common.vocab)
    offset = np.concatenate(([0], np.cumsum(degrees))).astype(np.uint32)
    shared = (
        tape,
        len(obs.target),
        common.counts.astype(np.uint32),
        common.outgoing.astype(np.uint32),
        offset,
        (common.keys & 65535).astype(np.uint16),
        common.values,
        common.rows.den,
    )
    arms = {"bigram": (np.zeros(1, dtype=np.uint8), 0, -np.log(obs.base))}
    if args.correction:
        from dataclasses import replace

        backoff = base_backoff(common, constant[0])
        chosen = fixed_output_probability(
            common, backoff, obs, models["selected"].token
        )
        for key in ("selected", "constant"):
            model = models[key]
            arms["output_" + key] = (
                np.frombuffer(model.payload, dtype=np.uint8),
                1 if model.mode == "pooled" else 4,
                -np.log(obs.readout(constant[0]))
                - model.adjustment(common, obs, chosen),
            )
        arms["matched_output_trigram"] = (
            np.frombuffer(matched.payload, dtype=np.uint8),
            3 if len(matched.active) else 1,
            matched.losses(tri, obs),
        )
        current, _ = current_only_control(
            fitted, ids[:SELECT_END], models["selected"].token
        )
        current_obs = replace(obs, history=obs.query)
        current_prob = fixed_output_probability(common, backoff, obs, current.token)
        arms["current_only"] = (
            np.frombuffer(current.payload, dtype=np.uint8),
            1 if current.mode == "pooled" else 4,
            -np.log(obs.readout(constant[0]))
            - current.adjustment(common, current_obs, current_prob),
        )
    if args.precision:
        forecasts = tuple(obs.readout(m) for m in pair)
        for name, model in (
            ("fraction", fraction),
            ("constant_fraction", constant_fraction),
        ):
            arms[name] = (
                np.frombuffer(model.payload, dtype=np.uint8),
                1,
                model.losses(obs, forecasts),
            )
    for name in ("conditional", "marginal", "seed"):
        a = routes[name]
        expected = np.where(
            a.route[obs.history],
            -np.log(obs.readout(pair[1])),
            -np.log(obs.readout(pair[0])),
        )
        arms[name] = (np.frombuffer(a.payload, dtype=np.uint8), 1, expected)
    arms["constant"] = (
        np.frombuffer(serialize(common, constant), dtype=np.uint8),
        1,
        -np.log(obs.readout(constant[0])),
    )
    arms["calibrated_trigram"] = (
        np.frombuffer(hybrid.payload, dtype=np.uint8),
        3 if len(hybrid.active) else 1,
        hybrid.losses(tri, obs),
    )
    for name, tau, indices in (
        ("matched_trigram", info["raw_tau"], active),
        ("unpruned_trigram", info["full_tau"], np.arange(len(tri.pairs))),
    ):
        row, found, gain = tri.combined(obs, tau)
        admitted = np.zeros(len(tri.pairs), dtype=bool)
        admitted[indices] = True
        expected = -np.log(obs.base) - np.where(found & admitted[row], gain, 0)
        arms[name] = (
            np.frombuffer(tri.pack(tau, indices), dtype=np.uint8),
            2,
            expected,
        )
    source = Path(__file__).with_name("address_score.c")
    with tempfile.TemporaryDirectory() as temp:
        (lib,) = compile_libraries(Path(temp), ("address",), source)
        result = {
            "raw_lookup_bytes": sum(a.nbytes for a in shared[2:-1]),
            "output_bytes": obs.base.nbytes,
            "binary": binary_sizes(lib),
            "cpu_ms": measure_cpu(lib, shared, arms),
        }
    if args.gpu:
        result["gpu"] = measure_gpu(source, shared, arms)
    print(json.dumps(result, indent=2))
