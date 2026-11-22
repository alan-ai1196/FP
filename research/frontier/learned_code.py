"""Learn the check columns of a packed delayed predictor from ordinary future bits."""

import argparse
import ctypes
import json
import os
import tempfile
from collections import deque
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

import causal_state as cs
import numpy as np
from text import SCALE

WIDTH = 63
CHECKS = 6
STATES = 1 << CHECKS
EPISODES = 64
PIVOTS = 1 << np.arange(CHECKS, dtype=np.uint8)


def correction_tree(columns, states=STATES):
    """Breadth-first syndrome paths. Each parent is an actual input coordinate."""
    generators = {}
    for j, column in enumerate(columns.tolist()):
        if column:
            generators.setdefault(column, j)
    parent = np.full(states, 255, dtype=np.uint8)
    corrections = np.zeros((states, len(columns)), dtype=np.uint8)
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for generator, coordinate in generators.items():
            target = current ^ generator
            if target and parent[target] == 255:
                parent[target] = coordinate
                corrections[target] = corrections[current]
                corrections[target, coordinate] ^= 1
                queue.append(target)
    assert np.all(parent[1:] != 255)
    return parent, corrections


def syndromes(bits, columns):
    return np.bitwise_xor.reduce(np.where(bits, columns, 0), axis=1)


def fit_pairs(lag):
    """Return observed aligned history/target pairs in complete stationary episodes."""
    rng = np.random.Generator(np.random.PCG64(2026112321))
    if lag != cs.DELAY or lag % WIDTH:
        raise ValueError(
            "the registered trial needs the correctly fitted multiple-of-63 lag"
        )
    groups = lag // WIDTH
    histories = np.empty((EPISODES * groups, WIDTH), dtype=np.uint8)
    targets = np.empty_like(histories)
    for j in range(EPISODES):
        rows = slice(j * groups, (j + 1) * groups)
        initial = rng.integers(2, size=lag, dtype=np.uint8)
        future = initial ^ (rng.integers(8, size=lag, dtype=np.uint8) == 0)
        histories[rows] = initial.reshape(-1, WIDTH)
        targets[rows] = future.reshape(-1, WIDTH)
    return histories, targets


def fit_matrices(histories, targets):
    initial = np.zeros(WIDTH, dtype=np.uint8)
    initial[:CHECKS] = PIVOTS
    columns = initial.copy()
    conventional = initial.copy()
    syndrome = syndromes(histories[:, :CHECKS], PIVOTS)
    # Delta in the actual number of label errors if this prototype bit is flipped.
    observed_errors = histories ^ targets
    raw_errors = int(observed_errors.sum())
    signed = np.ascontiguousarray((1 - 2 * observed_errors.astype(np.int8)).T)
    assert 2 * raw_errors < observed_errors.size
    keys = np.arange(2 * STATES, dtype=np.uint8)
    trace = {"training_errors": [], "covering_radius": []}
    for coordinate in range(CHECKS, WIDTH):
        new_bit = histories[:, coordinate]
        cell = (2 * syndrome + new_bit).astype(np.intp)
        sums = np.empty((2 * STATES, WIDTH), dtype=np.int32)
        for j in range(WIDTH):
            # Bincount sums integers of magnitude one, exactly representable in float64.
            sums[:, j] = np.bincount(cell, weights=signed[j], minlength=2 * STATES)
        empirical_scores = []
        mean_distance_sums = []
        radii = []
        for value in range(STATES):
            columns[coordinate] = value
            conventional[coordinate] = value
            _, flips = correction_tree(columns)
            proposed = (keys // 2) ^ ((keys & 1) * value)
            empirical_scores.append(raw_errors + int((sums * flips[proposed]).sum()))
            radii.append(int(flips.sum(axis=1).max()))
            _, comparator_flips = correction_tree(conventional)
            mean_distance_sums.append(int(comparator_flips.sum()))
        choice = int(np.argmin(empirical_scores))
        columns[coordinate] = choice
        conventional[coordinate] = int(np.argmin(mean_distance_sums))
        syndrome ^= new_bit * choice
        trace["training_errors"].append(empirical_scores[choice])
        trace["covering_radius"].append(radii[choice])
    _, installed = correction_tree(columns)
    direct = int(
        np.count_nonzero(
            (histories ^ installed[syndromes(histories, columns)]) != targets
        )
    )
    assert direct == trace["training_errors"][-1]
    random = initial.copy()
    rng = np.random.Generator(np.random.PCG64(2026112322))
    random[CHECKS:] = rng.integers(STATES, size=WIDTH - CHECKS, dtype=np.uint8)
    return {
        "initial": initial,
        "random": random,
        "conventional": conventional,
        "learned": columns,
    }, trace


def streaming_errors(tape, lag, matrices):
    """Reference predicts each block from the preceding raw block, for checking the packed stream."""
    original = cs.errors(tape, lag)
    result = {"raw": original["raw"], "supplied": original["coded"]}
    for name, columns in matrices.items():
        _, flips = correction_tree(columns)
        errors = 0
        for pos in range(lag, len(tape), lag):
            past = tape[pos - lag : pos].copy()
            length = lag // WIDTH * WIDTH
            bits = past[:length].reshape(-1, WIDTH)
            bits ^= flips[syndromes(bits, columns)]
            target = tape[pos : pos + lag]
            errors += int(np.count_nonzero(past[: len(target)] != target))
        result[name] = errors
    return result


def native_check(tapes, lag, matrices):
    import _ctypes

    pointer = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags="C_CONTIGUOUS")
    args = [pointer, ctypes.c_size_t, ctypes.c_uint32, pointer]
    rng = np.random.default_rng(629)
    checks = [
        (rng.integers(2, size=4 * d + 7, dtype=np.uint8), d)
        for d in (1, 8, 33, 62, 63, 64, 91, 126, 127)
    ]
    times = {}
    with tempfile.TemporaryDirectory() as temp:
        raw, fixed, general = cs.compile_libraries(
            Path(temp), ("raw", "both", "matrix")
        )
        sizes = {p.stem: cs.binary_sizes(p) for p in (raw, fixed, general)}
        libs = [ctypes.CDLL(str(path)) for path in (raw, fixed, general)]
        try:
            raw_fn, fixed_fn, matrix_fn = (
                libs[0].raw_errors,
                libs[1].coded_errors,
                libs[2].matrix_errors,
            )
            for fn in (raw_fn, fixed_fn, matrix_fn):
                fn.restype = ctypes.c_uint64
            raw_fn.argtypes = fixed_fn.argtypes = args
            matrix_fn.argtypes = [*args, pointer, pointer]
            specs = {"raw": (raw_fn, ()), "supplied": (fixed_fn, ())}
            for name, cols in matrices.items():
                parent, _ = correction_tree(cols)
                specs[name] = (matrix_fn, (cols, parent))
            items = [*checks, *[(tape, lag) for tape in tapes]]
            for k, (data, d) in enumerate(items):
                expected = streaming_errors(data, d, matrices)
                packed = np.packbits(data, bitorder="little")
                for name, (fn, parameters) in specs.items():
                    stored = (
                        d
                        if name == "raw"
                        else (WIDTH - CHECKS) * (d // WIDTH) + d % WIDTH
                    )
                    samples = []
                    for _ in range(5 if k == len(items) - 1 else 1):
                        ring = np.zeros((stored + 7) // 8, dtype=np.uint8)
                        start = perf_counter()
                        actual = fn(packed, len(data), d, ring, *parameters)
                        samples.append(round(1000 * (perf_counter() - start), 3))
                        assert actual == expected[name], (
                            d,
                            name,
                            actual,
                            expected[name],
                        )
                    if k == len(items) - 1:
                        times[name] = samples
            return {
                "build": sizes,
                "report_kernel_ms_including_warmup": times,
                "matched_tapes": len(items),
            }
        finally:
            for library in libs:
                (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(
                    library._handle
                )


def metrics(counts, total, budget, calibration, price, lag):
    scores = {}
    for name, bits in budget.items():
        error_rate = F(1, 2) if name == "fair" else F(counts[name], total)
        rent = price * bits * SCALE / lag
        scores[name] = tuple(
            x + rent for x in cs.binary_cost(error_rate, calibration[name])
        )
    winner = min(scores, key=lambda name: scores[name][1])
    assert all(scores[winner][1] < v[0] for k, v in scores.items() if k != winner)
    return winner, {name: cs.printed(v) for name, v in scores.items()}


def experiment(native):
    lag, _, _ = cs.identify()
    histories, targets = fit_pairs(lag)
    matrices, trace = fit_matrices(histories, targets)
    training_groups = len(histories)
    del histories, targets
    tapes = [
        cs.stream(blocks, seed, lag)
        for blocks, seed in ((8, 2026112323), (4, 2026112324), (16, 2026112325))
    ]
    lengths = [len(tape) - lag for tape in tapes]
    counts = [streaming_errors(tape, lag, matrices) for tape in tapes]
    calibration = {
        "fair": F(1, 2),
        **{k: F(2 * n + 1, 2 * lengths[0] + 2) for k, n in counts[0].items()},
    }
    cost = cs.charges(lag)
    bits = {"fair": 0, "raw": cost["raw"], "supplied": cost["coded"]}
    bits.update(dict.fromkeys(matrices, cost["coded"] + 8 * (256 - 128)))
    comparisons = {}
    tables = {}
    population = {"fair": F(1, 2), "raw": F(1, 8), "supplied": F(35, 256)}
    for name, columns in matrices.items():
        _, leaders = correction_tree(columns)
        distances = leaders.sum(axis=1).astype(int)
        population[name] = F(1, 8) + F(3, 4) * F(int(distances.sum()), WIDTH * STATES)
        tables[name] = {
            "columns": columns.tolist(),
            "distance_histogram": np.bincount(distances).tolist(),
            "distinct_nonzero_columns": len(set(columns.tolist()) - {0}),
        }
    for price in cs.PRICES:
        winner, selection = metrics(
            counts[1], lengths[1], bits, calibration, price, lag
        )
        _, report = metrics(counts[2], lengths[2], bits, calibration, price, lag)
        expected = {
            k: cs.printed(
                tuple(
                    x + price * bits[k] * SCALE / lag
                    for x in cs.binary_cost(v, calibration[k])
                )
            )
            for k, v in population.items()
        }
        comparisons[str(price)] = {
            "selected": winner,
            "selection": selection,
            "reporting": report,
            "population": expected,
        }
    if native:
        print(json.dumps(native_check(tapes, lag, matrices), indent=2))
    return {
        "registration": "491388e",
        "reused_fitted_lag": lag,
        "training_episodes": EPISODES,
        "matrix_fit_tokens": 2 * WIDTH * training_groups,
        "training_group_pairs": training_groups,
        "trials_per_greedy_design": (WIDTH - CHECKS) * STATES,
        "learned_trace": trace,
        "models": tables,
        "scored_target_counts": lengths,
        "errors": counts,
        "fitted_error_probabilities": {k: str(v) for k, v in calibration.items()},
        "charged_bits": bits,
        "population_error_probabilities": {k: str(v) for k, v in population.items()},
        "comparisons": comparisons,
    }


def audit_small_codes():
    # Independent direct nearest-center search in all 8^4 systematic seven-bit codes.
    words = np.arange(128, dtype=np.uint8)
    bits = (words[:, None] >> np.arange(7, dtype=np.uint8)) & 1
    total = {}
    for free in product(range(8), repeat=4):
        cols = np.array([1, 2, 4, *free], dtype=np.uint8)
        s = syndromes(bits, cols)
        centers = words[s == 0]
        exact = np.bitwise_count(words[:, None] ^ centers).min(axis=1)
        _, flips = correction_tree(cols, 8)
        assert np.array_equal(flips[s].sum(axis=1), exact)
        assert not np.any(syndromes(bits ^ flips[s], cols))
        total[free] = int(exact.sum())
        assert (total[free] == 112) == (len(set(cols.tolist()) - {0}) == 7)
    checked = 0
    for k in range(4):
        for prefix in product(range(8), repeat=k):
            if len({1, 2, 4, *prefix, 0}) != 4 + k:
                continue
            scores = [total[(*prefix, c, *((0,) * (3 - k)))] for c in range(8)]
            present = {0, 1, 2, 4, *prefix}
            assert all((scores[c] < scores[0]) == (c not in present) for c in range(8))
            checked += 1
    # All three-step deterministic forecast trees and every fixed noise word.
    policies = 0
    for policy in range(128):
        for noise in range(8):
            histogram = [0] * 4
            for word in range(8):
                node = errors = 0
                for j in range(3):
                    raw = (word >> j) & 1
                    errors += raw ^ ((policy >> node) & 1)
                    received = raw ^ ((noise >> j) & 1)
                    node = 2 * node + 1 + received
                histogram[errors] += 1
            assert histogram == [1, 3, 3, 1]
            policies += 1
    # Literal encoder outputs occupy the low eight bits; two three-bit prototypes follow.
    start = sum((u & 1) << u for u in range(8)) | (1 << 11)

    def table_cost(table):
        prototypes = [(table >> 8) & 7, (table >> 11) & 7]
        return sum((u ^ prototypes[(table >> u) & 1]).bit_count() for u in range(8))

    local = [
        min(table_cost(start ^ sum(1 << j for j in edits)) for edits in combinations(range(14), k))
        for k in range(4)
    ]
    assert local == [8, 8, 8, 7]
    return {
        "systematic_matrices": len(total),
        "distinct_prefixes": checked,
        "causal_policy_noise_pairs": policies,
        "best_three_bit_table_cost_by_edit_distance": local,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    if args.audit:
        print(json.dumps(audit_small_codes()))
    else:
        result = experiment(args.native)
        if args.check:
            assert result == json.loads(args.check.read_text(encoding="utf-8"))
        output = json.dumps(result, indent=2) + "\n"
        if args.write:
            args.write.write_text(output, encoding="utf-8")
        elif not args.native:
            print(output, end="")
