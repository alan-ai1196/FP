"""Verify packed two-stage controllers and time their sensor and confidence lookups."""

import _ctypes
import argparse
import ctypes
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter

import numpy as np
from causal_state import binary_sizes, compile_libraries
from controlled_sensing import (
    BUDGETS,
    COSTS,
    SEEDS,
    TASKS,
    control_tables,
    conventional_factor,
    episodes,
    population,
    purchased,
    quantize,
    rank_model,
    state_means,
)


@contextmanager
def native_batch():
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as tmp:
        (path,) = compile_libraries(Path(tmp), ("address",), root / "sensing_score.c")
        size = binary_sizes(path)
        lib = ctypes.CDLL(str(path))
        try:
            fn = lib.sense_batch

            def ptr(t):
                return np.ctypeslib.ndpointer(dtype=t, ndim=1, flags="C_CONTIGUOUS")

            fn.argtypes = [ptr(np.uint8)] * 4 + [
                ctypes.c_uint32,
                ptr(np.uint8),
                ptr(np.uint16),
            ]
            fn.restype = None
            yield fn, size
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)


def run(receipt):
    with native_batch() as (fn, size):
        queries = np.indices((8, 8, 3), dtype=np.uint8).reshape(3, -1)
        rng = np.random.default_rng([701, 123])
        n = 1048576
        timing_inputs = [rng.integers(cap, size=n, dtype=np.uint8) for cap in (8, 8, 3)]
        action = np.empty(n, dtype=np.uint8)
        prob = np.empty(n, dtype=np.uint16)
        timings = {}
        verified = 0
        for seed in SEEDS:
            counts, hits = purchased(episodes(seed, population(seed)), BUDGETS[-1])
            rank, codes = rank_model(counts, hits)
            for name, model in (
                ("rank_one", rank),
                ("tabular", (hits + 0.5) / (counts + 1)),
            ):
                for cost in COSTS:
                    arms = control_tables(model, cost)
                    if name == "rank_one":
                        arms["factored"] = conventional_factor(model, codes, cost)
                    for arm, m in arms.items():
                        info = receipt["largest_budget_installations"][
                            f"{seed}/{name}/{cost}/{arm}"
                        ]
                        means = state_means(model, m)
                        forecast = np.concatenate(
                            [np.full((len(means), 3, 1), 0.5), means], axis=-1
                        )
                        chosen = quantize(
                            forecast[np.arange(len(means))[:, None], TASKS, m.policy]
                        )
                        wire = m.packet + chosen.tobytes()
                        assert wire.hex() == info["action_hex"] + info["q16_hex"]
                        packet = np.frombuffer(wire, dtype=np.uint8)
                        u, v, j = queries
                        fn(
                            packet,
                            u,
                            v,
                            j,
                            len(j),
                            action[: len(j)],
                            prob[: len(j)],
                        )
                        assert np.array_equal(
                            action[: len(j)], m.policy[m.states[u, v], j]
                        )
                        assert np.array_equal(prob[: len(j)], chosen[m.states[u, v], j])
                        verified += len(j)
                        if seed != SEEDS[0] or name != "rank_one" or cost != COSTS[0]:
                            continue
                        args = (packet, *timing_inputs, n, action, prob)
                        fn(*args)
                        u, v, j = timing_inputs
                        assert np.array_equal(action, m.policy[m.states[u, v], j])
                        assert np.array_equal(prob, chosen[m.states[u, v], j])
                        samples = []
                        for _ in range(9):
                            start = perf_counter()
                            fn(*args)
                            samples.append(round((perf_counter() - start) * 1000, 4))
                        timings[arm] = samples
    return {
        "verified_seed_model_contexts": verified,
        "timed_decisions": n,
        "input_bytes": 3 * n,
        "output_bytes": 3 * n,
        "binary": size,
        "warm_cpu_ms": timings,
    }


def verify_response_classes():
    from response_classes import run as refit

    queries = np.indices((8, 8, 3), dtype=np.uint8).reshape(3, -1)
    u, v, j = queries
    a = np.empty(192, dtype=np.uint8)
    p = np.empty(384, dtype=np.uint16)
    checked = predictions = 0
    n = 1048576
    rng = np.random.default_rng([231124, 79])
    batch = [rng.integers(high, size=n, dtype=np.uint8) for high in (8, 8, 3)]
    batch_a = np.empty(n, dtype=np.uint8)
    batch_p = np.empty(n * 2, dtype=np.uint16)
    timings = {}
    with native_batch() as (fn, size):

        def verify(wire, controller, selected):
            nonlocal checked, predictions
            model = np.frombuffer(wire, dtype=np.uint8)
            channels = int(model[3])
            fn(model, u, v, j, len(j), a, p)
            states = controller.states[u, v]
            assert np.array_equal(a, controller.policy[states, j])
            assert np.array_equal(
                p[: len(j) * channels].reshape(-1, channels), selected[states, j]
            )
            checked += len(j)
            predictions += len(j) * channels
            key = f"{model[0]}/{model[1]}/{channels}"
            if channels == 2 and model[0] in (3, 5) and key not in timings:
                args = (model, *batch, n, batch_a, batch_p)
                fn(*args)
                row, col, task = batch
                expected = controller.states[row, col]
                assert np.array_equal(batch_a, controller.policy[expected, task])
                assert np.array_equal(batch_p.reshape(-1, 2), selected[expected, task])
                timings[key] = []
                for _ in range(9):
                    start = perf_counter()
                    fn(*args)
                    timings[key].append(round(1000 * (perf_counter() - start), 4))

        refit(verify)
    return {
        "context_decisions": checked,
        "q16_forecasts": predictions,
        "binary": size,
        "batch_size": n,
        "input_bytes": 3 * n,
        "output_bytes": 5 * n,
        "warm_ms_by_packet_kind_entries_channels": timings,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--response-classes", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    if args.response_classes:
        output = verify_response_classes()
    else:
        receipt = json.loads(
            Path(__file__).with_name("controlled_sensing_result.json").read_text()
        )
        output = run(receipt)
    data = json.dumps(output, indent=2) + "\n"
    if args.write:
        args.write.write_text(data, encoding="utf8")
    else:
        print(data, end="")
