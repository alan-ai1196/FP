"""Select a causal recurrent writer on continuous stationary binary training tapes."""

import _ctypes
import argparse
import ctypes
import json
import os
import tempfile
from itertools import product
from math import log
from pathlib import Path

import numpy as np
from audit_stream import ctw
from autonomous_state_width import REGISTRATION, UNITS
from causal_state import compile_libraries
from scipy.special import betaln

SIZES = (4096, 32768)
REPORT = 131072
REPEATS = 8
PRICE = 1 / 1024
BITS = np.arange(5, -1, -1)


def accessible_tables():
    """Rooted reachable machines, named by breadth-first discovery in sign order."""
    tables, widths = [], []
    for k in range(1, 5):
        for flat in product(range(k), repeat=2 * k):
            largest = 0
            for i, dest in enumerate(flat):
                if i // 2 > largest or dest > largest + 1:
                    break
                largest = max(largest, dest)
            else:
                if largest == k - 1:
                    tables.append(flat + (0,) * (8 - 2 * k))
                    widths.append(k)
    return np.array(tables, dtype=np.uint8), np.array(widths)


def tape(units, size, seed):
    rng = np.random.default_rng(np.random.SeedSequence([20261126, 706, *seed]))
    initial = int(rng.integers(64))
    bits = np.empty(size + 6, dtype=np.uint8)
    bits[:6] = (initial >> BITS) & 1
    draws = rng.integers(4, size=size, dtype=np.uint8)
    # At beta = 1/2, the probability of plus is (2+v)/4.
    chances = (2 + units).tolist()
    old = initial
    for i, u in enumerate(draws):
        b = int(u) >= chances[old]
        bits[6 + i] = b
        old = (2 * old + b) % 64
    return bits


def suffix_counts(bits, n):
    rows = np.lib.stride_tricks.sliding_window_view(bits[: n + 6], 7)
    words = rows[:, :6] @ (1 << BITS)
    return np.bincount(2 * words + rows[:, 6], minlength=128).reshape(64, 2)


def context_tree(counts):
    """Posterior stop weights for the full depth-six binary context-tree mixture."""
    levels = []
    cells = counts.copy()
    subtree = None
    for k in reversed(range(7)):
        local = betaln(cells[:, 0] + 0.5, cells[:, 1] + 0.5) - log(np.pi)
        positive = (cells[:, 0] + 0.5) / (cells.sum(axis=1) + 1)
        if subtree is None:
            stop, subtree = np.ones_like(local), local
        else:
            left, right = np.split(subtree, 2)
            joint = np.logaddexp(local, left + right)
            stop, subtree = np.exp(local - joint), joint - log(2)
        levels.append((positive, stop))
        if k:
            left, right = np.split(cells, 2)
            cells = left + right
    forecast = np.zeros(64)
    for local, stop in levels:
        idx = np.arange(64) % len(local)
        forecast = stop[idx] * local[idx] + (1 - stop[idx]) * forecast
    return forecast


def reader(lib):
    f = lib.state_counts
    u8 = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
    u32 = np.ctypeslib.ndpointer(dtype=np.uint32, flags="C_CONTIGUOUS")
    f.argtypes = [u8, ctypes.c_size_t, u8, ctypes.c_size_t, ctypes.c_size_t, u32]
    f.restype = None

    def tally(models, bits, n):
        cells = np.zeros((len(models), 4, 2), dtype=np.uint32)
        f(np.ascontiguousarray(models), len(models), bits, 6, n, cells)
        return cells

    return tally


def check(tally, tables):
    bits = tape(UNITS[0], 71, (99,))
    subset = tables[:: max(1, len(tables) // 27)]
    actual = tally(subset, bits, 71)
    for k, m in enumerate(subset):
        counts = np.zeros((4, 2), dtype=np.uint32)
        state = 0
        for i, bit in enumerate(bits):
            if i >= 6:
                counts[state, bit] += 1
            state = m[2 * state + bit]
        assert np.array_equal(counts, actual[k])
    counts = suffix_counts(bits, 71)
    _, ref = ctw(counts.tolist(), 6)
    assert np.max(np.abs(context_tree(counts) - [float(row[0]) for row in ref])) < 1e-13


def gain(counts, positive):
    return (
        counts[..., 0] * np.log(2 * positive)
        + counts[..., 1] * np.log(2 * (1 - positive))
    ).sum(axis=-1)


def choose_tables(counts, widths):
    evidence = (betaln(counts[:, :, 0] + 0.5, counts[:, :, 1] + 0.5) - log(np.pi)).sum(
        axis=1
    )
    chosen = []
    for k in range(1, 5):
        ids = np.flatnonzero(widths == k)
        local = evidence[ids]
        chosen.append(ids[np.flatnonzero(local >= local.max() - 1e-9)[0]])
    cells = counts[chosen]
    return chosen, (cells[:, :, 0] + 0.5) / (cells.sum(axis=-1) + 1)


def fit_source(units, source, tally, tables, widths):
    records = {n: [] for n in SIZES}
    for rep in range(REPEATS):
        train = tape(units, max(SIZES), (source, rep, 0))
        valid = tape(units, max(SIZES), (source, rep, 1))
        report = tape(units, REPORT, (source, rep, 2))
        test_context = suffix_counts(report, REPORT)
        for n in SIZES:
            models, h = choose_tables(tally(tables, train, n), widths)
            best = tables[models]
            validation = gain(tally(best, valid, n), h) / n
            net = validation - PRICE * np.array([0, 1, 2, 2])
            choice = int(np.argmax(net))
            test = gain(tally(best, report, REPORT), h) / REPORT
            ctx = suffix_counts(train, n)
            direct = (ctx[:, 0] + 0.5) / (ctx.sum(axis=1) + 1)
            true = (2 + units) / 4
            row = {
                "width": choice + 1,
                "joint": float(test[choice]),
                "fitted_four": float(test[3]),
                "direct": float(gain(test_context, direct) / REPORT),
                "context_tree": float(gain(test_context, context_tree(ctx)) / REPORT),
                "generating": float(gain(test_context, true) / REPORT),
            }
            records[n].append(row)
    return [
        {
            "train_and_validation_each": n,
            "joint_width_histogram": np.bincount(
                [r["width"] for r in rows], minlength=5
            )[1:].tolist(),
            "positive_joint_reporting_tapes": sum(r["joint"] > 0 for r in rows),
            "mean_gain_per_raw_token": {
                name: float(np.mean([r[name] for r in rows]))
                for name in (
                    "joint",
                    "fitted_four",
                    "direct",
                    "context_tree",
                    "generating",
                )
            },
            "range_joint_gain_per_token": [
                min(r["joint"] for r in rows),
                max(r["joint"] for r in rows),
            ],
        }
        for n, rows in records.items()
    ]


def audit():
    tables, widths = accessible_tables()
    with tempfile.TemporaryDirectory() as temp:
        (path,) = compile_libraries(
            Path(temp),
            modes=("both",),
            source=Path(__file__).with_name("rolling_state_counts.c"),
        )
        lib = ctypes.CDLL(str(path))
        try:
            tally = reader(lib)
            check(tally, tables)
            runs = {
                name: fit_source(units, i, tally, tables, widths)
                for i, (name, units) in enumerate(
                    zip(("first", "second", "fair"), [*UNITS, np.zeros(64, dtype=int)])
                )
            }
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)
    return {
        "registration": REGISTRATION,
        "reachable_tables_by_width": np.bincount(widths)[1:].tolist(),
        "repetitions_per_source": REPEATS,
        "report_length": REPORT,
        "training_transitions_all_sizes_per_repetition": int(
            len(tables) * sum(n + 6 for n in SIZES)
        ),
        "validation_transitions_all_sizes_per_repetition": 4
        * sum(n + 6 for n in SIZES),
        "test_transitions_all_sizes_per_repetition": len(SIZES) * 4 * (REPORT + 6),
        "sources": runs,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
