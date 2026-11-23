"""Verify packed two-stage controllers and time their sensor and confidence lookups."""

import _ctypes
import argparse
import ctypes
import json
import os
import tempfile
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


def run(receipt):
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
            queries = np.indices((8, 8, 3), dtype=np.uint8).reshape(3, -1)
            rng = np.random.default_rng([701, 123])
            n = 1048576
            timing_inputs = [
                rng.integers(cap, size=n, dtype=np.uint8) for cap in (8, 8, 3)
            ]
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
                                forecast[
                                    np.arange(len(means))[:, None], TASKS, m.policy
                                ]
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
                            assert np.array_equal(
                                prob[: len(j)], chosen[m.states[u, v], j]
                            )
                            verified += len(j)
                            if (
                                seed != SEEDS[0]
                                or name != "rank_one"
                                or cost != COSTS[0]
                            ):
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
                                samples.append(
                                    round((perf_counter() - start) * 1000, 4)
                                )
                            timings[arm] = samples
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)
    return {
        "verified_seed_model_contexts": verified,
        "timed_decisions": n,
        "input_bytes": 3 * n,
        "output_bytes": 3 * n,
        "binary": size,
        "warm_cpu_ms": timings,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    receipt = json.loads(
        Path(__file__).with_name("controlled_sensing_result.json").read_text()
    )
    data = json.dumps(run(receipt), indent=2) + "\n"
    if args.write:
        args.write.write_text(data, encoding="utf8")
    else:
        print(data, end="")
