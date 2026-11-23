"""Check resumable CPU forecasts for the stopped counter, finite graph and half-count rule."""

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


def reference(bits, graph, emit, limit):
    n, steps = bits.shape
    successes = bits.cumsum(axis=1, dtype=np.int32) - bits
    before = np.arange(steps)[None, :]
    signed = (2 * successes - before).astype(np.int32)
    reached = np.abs(signed) == limit
    first = np.argmax(reached, axis=1)
    absorbed = reached.any(axis=1)[:, None] & (before >= first[:, None])
    actual = np.where(absorbed, signed[np.arange(n), first, None], signed)
    counter = np.where(
        actual < -1, 0.25, np.where(actual > 1, 0.75, 0.5 + 0.125 * actual)
    )
    state = np.zeros(n, np.uint8)
    outputs = np.empty(bits.shape)
    for t in range(steps):
        outputs[:, t] = emit[state]
        state = graph[state, bits[:, t]]
    return {
        "counter": counter,
        "graph": outputs,
        "half_count": (successes + 0.5) / (before + 1),
    }


def run(receipt):
    n = steps = 1024
    limit = 12
    rng = np.random.default_rng(12427)
    bits = (rng.random((n, steps)) < np.repeat([0.25, 0.75], n // 2)[:, None]).astype(
        np.uint8
    )
    chosen = receipt["automata"][3]["best"][str(steps)]
    graph = np.array(chosen["graph"], np.uint8)
    emit = np.array(chosen["readout"])
    expected = reference(bits, graph, emit, limit)
    with TemporaryDirectory() as tmp:
        (dll,) = compile_libraries(
            Path(tmp), ("address",), Path(__file__).with_name("coin_predict.c")
        )
        size = binary_sizes(dll)
        lib = ctypes.CDLL(str(dll))
        try:
            pu = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
            pi = np.ctypeslib.ndpointer(dtype=np.int8, flags="C_CONTIGUOUS")
            pn = np.ctypeslib.ndpointer(dtype=np.uint32, flags="C_CONTIGUOUS")
            pd = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
            types = {
                "counter": [ctypes.c_int8, pu, pi, pd],
                "graph": [pu, pd, pu, pu, pd],
                "half_count": [pu, pn, pd],
            }
            args = {"counter": (limit,), "graph": (graph, emit), "half_count": ()}
            states = {
                "counter": np.zeros(n, np.int8),
                "graph": np.zeros(n, np.uint8),
                "half_count": np.zeros((n, 2), np.uint32),
            }
            samples = {}
            for name, state in states.items():
                fn = getattr(lib, name + "_stream")
                fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, *types[name]]
                fn.restype = None
                for start, end in ((0, 37), (37, steps)):
                    outputs = np.empty((n, end - start))
                    block = np.ascontiguousarray(bits[:, start:end])
                    fn(n, end - start, *args[name], block, state, outputs)
                    np.testing.assert_array_equal(outputs, expected[name][:, start:end])
                final = state.copy()
                outputs = np.empty(bits.shape)
                samples[name] = []
                for i in range(10):
                    state.fill(0)
                    start = perf_counter()
                    fn(n, steps, *args[name], bits, state, outputs)
                    elapsed = perf_counter() - start
                    if i:
                        samples[name].append(round(elapsed * 1000, 4))
                np.testing.assert_array_equal(state, final)
                np.testing.assert_array_equal(outputs, expected[name])
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)
    return {
        "streams": n,
        "steps": steps,
        "restart_after": 37,
        "seed": 12427,
        "input_bytes": bits.nbytes,
        "output_bytes_per_arm": outputs.nbytes,
        "counter_limit": limit,
        "counter_release": "Q3 exactly represented in binary64",
        "installed_graph_bytes": graph.nbytes + emit.nbytes,
        "live_bytes_per_stream": {k: s.nbytes // n for k, s in states.items()},
        "binary": size,
        "warm_cpu_ms": samples,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = Path(__file__).with_name("coin_memory_result.json")
    result = run(json.loads(source.read_text(encoding="utf8")))
    value = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(value, encoding="utf8")
    else:
        print(value, end="")
