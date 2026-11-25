"""Learn a clean binary operation or identify one errant report using separated tapes."""

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from functools import reduce
from io import BytesIO
from itertools import product
from math import log
from operator import xor
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from positive_comparison import SOURCE, categorical_program

N = 4096
NAMES = 64
BITS = 86
Q16 = 65536
BINARY = Q16 - (NAMES - 2)
MODELS = (
    ("affine", False, 17),
    ("affine", True, 29),
    ("lookup", False, 74),
    ("lookup", True, 86),
)
AFFINE = np.array(
    [[(w & (d | 64)).bit_count() % 2 for d in range(NAMES)] for w in range(128)],
    dtype=np.uint8,
)


def source(seed, kind):
    rng = np.random.default_rng([seed, 8211])
    names = np.r_[np.tile(np.arange(NAMES), 3), rng.integers(16, size=N - 3 * NAMES)]
    names = rng.permutation(names)
    truth_rng = np.random.default_rng([seed, kind, 8212])
    if kind == 0:
        slope = int(truth_rng.integers(1, 64))
        truth = AFFINE[slope | (int(truth_rng.integers(2)) << 6)]
    else:
        while True:
            truth = truth_rng.integers(2, size=NAMES).astype(np.uint8)
            if not np.any(np.all(AFFINE == truth, axis=1)):
                break
    flip = int(np.random.default_rng([seed, kind, 8213]).integers(N))
    alternatives = (
        (),
        (flip,),
        (int(np.flatnonzero(names == 0)[0]), int(np.flatnonzero(names == 1)[0])),
    )
    return names, truth, alternatives


def public_columns(seed):
    raw = np.random.default_rng([seed, 8214]).bytes(11 * N)
    return [
        int.from_bytes(raw[i : i + 11], "little") & ((1 << BITS) - 1)
        for i in range(0, len(raw), 11)
    ]


def features(names, columns):
    names_basis = [0] * NAMES
    for name, column in zip(names, columns, strict=True):
        names_basis[name] ^= column
    affine_basis = [
        reduce(xor, (v for d, v in enumerate(names_basis) if (d | 64) & (1 << j)), 0)
        for j in range(7)
    ]
    return {"lookup": names_basis, "affine": affine_basis}


def decompose(columns, bits):
    pivots = {}
    work = 0
    limit = (1 << bits) - 1
    for i, column in enumerate(columns):
        row, rule = column & limit, 1 << i
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (row, rule)
                break
            other, witness = pivots[pivot]
            row ^= other
            rule ^= witness
            work += 1
    ordered = sorted(pivots, reverse=True)

    def quotient(value):
        row, rule = value & limit, 0
        xors = 0
        for pivot in ordered:
            if row & (1 << pivot):
                other, witness = pivots[pivot]
                row ^= other
                rule ^= witness
                xors += 1
        return row, rule, xors

    return len(pivots), quotient, work


def decode(sketch, columns, feature_columns):
    operations = 0
    probes = 0
    for _, _, budget in MODELS:
        visited = {}
        for kind, error, entry in MODELS:
            if entry > budget:
                break
            if kind not in visited:
                rank, quotient, work = decompose(feature_columns[kind], budget)
                operations += work
                target, rule, work = quotient(sketch)
                operations += work
                visited[kind] = (rank, quotient, target, rule)
            rank, quotient, target, rule = visited[kind]
            if rank < len(feature_columns[kind]):
                continue
            if not error and target == 0:
                return kind, rule, None, budget, operations, probes
            if error:
                found = []
                for i, column in enumerate(columns):
                    residual, correction, work = quotient(column)
                    operations += work
                    probes += 1
                    if residual == target:
                        found.append((rule ^ correction, i))
                        if len(found) == 2:
                            break
                if len(found) == 1:
                    return kind, *found[0], budget, operations, probes
    return None, None, None, BITS, operations, probes


def rule_table(kind, rule):
    if kind == "affine":
        return AFFINE[rule]
    return np.array([(rule >> d) & 1 for d in range(NAMES)], dtype=np.uint8)


def fit_sample(names, reports):
    """Marginalize four model families and the unknown single error location."""
    count = len(names)
    matches = np.count_nonzero(AFFINE[:, names] != reports, axis=1)
    clean = (matches == 0).astype(float)
    repaired = (1 - count / N) * clean + (matches == 1) / N
    affine = (clean + repaired) / len(AFFINE)
    total = affine.sum()
    numer = affine @ AFFINE
    visits = np.bincount(names, minlength=NAMES)
    ones = np.bincount(names, weights=reports, minlength=NAMES).astype(int)
    weight = 2.0 ** (-int(np.count_nonzero(visits)))

    def lookup(success, mult):
        if np.any((success > 0) & (success < visits)):
            return 0.0, np.zeros(NAMES)
        w = weight * mult
        return w, w * np.where(visits > 0, (success > 0).astype(float), 0.5)

    value, contrib = lookup(ones, 2 - count / N)
    total += value
    numer += contrib
    for d, y in zip(names, reports, strict=True):
        changed = ones.copy()
        changed[d] += 1 - 2 * int(y)
        value, contrib = lookup(changed, 1 / N)
        total += value
        numer += contrib
    return np.clip(numer / total, 0, 1) if total else np.full(NAMES, 0.5)


def gain(truth, probability):
    pos = np.clip(np.rint(BINARY * np.asarray(probability, dtype=float)), 1, BINARY - 1)
    assigned = np.where(truth == 1, pos, BINARY - pos)
    return log(2) + float(np.log(assigned / BINARY).mean())


def native_packet(kind, rule):
    return bytes([0 if kind == "affine" else 1]) + int(rule).to_bytes(
        1 if kind == "affine" else 8, "little"
    )


def after_name(packet, d):
    code = int.from_bytes(packet[1:], "little")
    return 1 + (
        (code & (d | 64)).bit_count() % 2 if packet[0] == 0 else ((code >> d) & 1)
    )


def released(state):
    if state == 0:
        return (Q16 // NAMES,) * NAMES
    p = 1 if state == 1 else BINARY - 1
    return (BINARY - p, p, *((1,) * (NAMES - 2)))


def run():
    rows = []
    for seed in range(32):
        cols = public_columns(seed)
        sample_order = np.random.default_rng([seed, 8215]).permutation(N)
        for typ in (0, 1):
            names, truth, flips = source(seed, typ)
            design = features(names, cols)
            for locations in flips:
                y = truth[names].copy()
                if locations:
                    y[list(locations)] ^= 1
                positives = np.flatnonzero(y)
                sketch = reduce(xor, (cols[i] for i in positives), 0)
                kind, rule, err, bits, xors, probes = decode(sketch, cols, design)
                selected = sample_order[:bits]
                sampled = fit_sample(names[selected], y[selected])
                learned = rule_table(kind, rule) if kind else np.full(NAMES, 0.5)
                packet = native_packet(kind, rule) if kind else None
                if packet:
                    for d in range(NAMES):
                        assert after_name(packet, d) == 1 + learned[d]
                rows.append(
                    {
                        "seed": seed,
                        "source": ("affine", "lookup")[typ],
                        "flips": len(locations),
                        "installed": kind,
                        "packet_hex": packet.hex() if packet else None,
                        "bits": bits,
                        "correct_rule": bool(kind and np.array_equal(learned, truth)),
                        "correct_error_positions": bool(
                            kind and (() if err is None else (err,)) == locations
                        ),
                        "error_index": err,
                        "sketch_gain": gain(truth, learned),
                        "sample_Bayes_gain": gain(truth, sampled),
                        "sample_names": len(np.unique(names[selected])),
                        "sender_86bit_xors": len(positives),
                        "elimination_pivot_xors": xors,
                        "error_columns_reduced": probes,
                    }
                )
    return {"registration": "97fef68", "rows": rows}


def exact_check():
    # Every nonzero residual collides on exactly half of all possible linear rows.
    for n in range(1, 8):
        for diff in range(1, 1 << n):
            assert sum((r & diff).bit_count() % 2 == 0 for r in range(1 << n)) == 1 << (
                n - 1
            )
    names = np.array([0, 1, 0, 1, 0, 1])
    possibilities = set()
    for s in product((0, 1), repeat=2):
        tape = sum(s[d] << i for i, d in enumerate(names))
        for e in [0, *(1 << i for i in range(6))]:
            assert tape ^ e not in possibilities
            possibilities.add(tape ^ e)
    # Independently enumerate the tiny two-class likelihood of one uniform tape flip.
    obs = np.array([0, 1, 1], dtype=np.uint8)
    inds = np.array([0, 0, 1])
    z = 0
    for s in product(range(2), repeat=2):
        for e in range(6):
            z += all((s[d] ^ (e == i)) == int(obs[i]) for i, d in enumerate(inds))
    assert z == 2
    # Integrate over only the visited lookup bits. Unvisited bits retain fair priors.
    test_names = np.array([0, 3, 0, 3, 9])
    visited = np.unique(test_names)
    vectors = []
    for assignment in product(range(2), repeat=len(visited)):
        table = np.full(NAMES, 0.5)
        table[visited] = assignment
        vectors.append(table)
    posterior_cases = 0
    for reports in product(range(2), repeat=len(test_names)):
        reports = np.array(reports)
        numerator = np.zeros(NAMES)
        denominator = 0.0
        for family in (AFFINE, vectors):
            for table in family:
                noiseless = table[test_names]
                mass = (2 * N - len(test_names)) * int(np.array_equal(noiseless, reports))
                for location in range(len(test_names)):
                    corrupted = noiseless.copy()
                    corrupted[location] = 1 - corrupted[location]
                    mass += int(np.array_equal(corrupted, reports))
                numerator += (mass / len(family)) * table
                denominator += mass / len(family)
        expected = numerator / denominator if denominator else np.full(NAMES, 0.5)
        np.testing.assert_allclose(fit_sample(test_names, reports), expected, atol=1e-14)
        posterior_cases += 1
    return {
        "nonzero_collision_tests": sum(2**n - 1 for n in range(1, 8)),
        "distinct_tapes_in_toy_radius_one_balls": len(possibilities),
        "independently_enumerated_full_predictive_posteriors": posterior_cases,
    }


def r4_audit():
    here = Path(__file__).resolve().parent
    rows = json.loads((here / "outcome_sketch_result.json").read_text())["rows"]
    examples = [
        next(
            r
            for r in rows
            if r["source"] == k
            and r["correct_rule"]
            and r["installed"] == k
            and r["flips"] == 1
        )
        for k in ("affine", "lookup")
    ]
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    alphabet = tuple(map(str, range(NAMES)))
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as files:
            files.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        for row in examples:
            p = bytes.fromhex(row["packet_hex"])
            transitions = [
                tuple(after_name(p, d) for d in range(NAMES)),
                (0,) * NAMES,
                (0,) * NAMES,
            ]
            releases = [released(i) for i in range(3)]
            slots = [Fraction(1), *(Fraction(2 * v - 1) for r in releases for v in r)]
            heads = [[(i, 1 + i * NAMES + j) for i in range(3)] for j in range(NAMES)]
            event, start, sizes = categorical_program(
                alphabet, transitions, heads, slots
            )
            states = [
                start,
                *(
                    event(alphabet[transitions[0].index(i)], start.delayed)
                    for i in (1, 2)
                ),
            ]
            for i, state in enumerate(states):
                assert state.probabilities == tuple(
                    Fraction(x, Q16) for x in releases[i]
                )
                for a, dest in zip(alphabet, transitions[i], strict=True):
                    new = event(a, state.delayed)
                    assert (
                        new.delayed == states[dest].delayed
                        and new.probabilities == states[dest].probabilities
                    )
    return {
        "packets": len(examples),
        "complete_resets_and_edges": len(examples) * (1 + 3 * NAMES),
        "nodes": sizes["nodes"],
        "delayed_cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--r4", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.r4 or args.check:
        encoded = json.dumps(r4_audit() if args.r4 else exact_check(), indent=2) + "\n"
    else:
        result = run()
        encoded = (
            '{"registration":"'
            + result["registration"]
            + '","rows":[\n'
            + ",\n".join(json.dumps(r, allow_nan=False) for r in result["rows"])
            + "]}\n"
        )
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
