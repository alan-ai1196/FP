"""Construct and check minimal-dimensional weak finite-memory mixture predictors."""

import argparse
import json
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import lcm
from pathlib import Path

import numpy as np
import sympy as sp
from autonomous_state_width import UNITS

REGISTRATION = "769f929"


class Responses:
    """Affine coordinates chosen from increasingly short continuation queries."""

    def __init__(self, table):
        self.table = sp.Matrix(table)
        n = len(table)
        self.horizon = n.bit_length() - 1
        assert n == 2**self.horizon
        ws = list(range(n))
        self.next = [[(2 * w + b) % n for w in ws] for b in (0, 1)]
        columns = [sp.ones(n, 1)]
        for length in reversed(range(self.horizon)):
            for tail in range(2**length):
                columns.append(
                    sp.Matrix([table[((w << length) + tail) % n] for w in ws])
                )
        full = sp.Matrix.hstack(*columns)
        self.rows = full[:, list(full.rref()[1])]
        indices = list(self.rows.T.rref()[1])
        inv = self.rows[indices, :].inv()
        self.maps = [
            inv * self.rows[[successors[i] for i in indices], :]
            for successors in self.next
        ]
        self.head = inv * self.table[indices, :]
        self.d = self.rows.cols - 1
        for a, successors in zip(self.maps, self.next):
            assert self.rows * a == self.rows[successors, :]
            assert a[0, 0] == 1 and not any(
                a[i, j] for i in range(1, self.d + 1) for j in range(i + 1)
            )
        assert self.rows * self.head == self.table


def check_machine(chart, encoded, kernels, head, strength):
    assert encoded * head == strength * chart.table
    assert min(encoded) >= 0 and max(map(abs, head)) <= 1
    k = encoded.cols
    for t, successors in zip(kernels, chart.next):
        assert min(t) >= 0 and t * sp.ones(k, 1) == sp.ones(k, 1)
        assert encoded * t == encoded[successors, :]
    # Replay all words from every pure initial state by integer matrix multiplication.
    den = lcm(*(int(sp.denom(z)) for t in kernels for z in t))
    mats = [np.array((den * t).tolist(), dtype=object).astype(object) for t in kernels]
    mats = [np.array([[int(x) for x in row] for row in t], dtype=object) for t in mats]
    paths = [np.eye(k, dtype=object)]
    for _ in range(chart.horizon):
        paths = [p @ t for p in paths for t in mats]
    expected = encoded * den**chart.horizon
    for i, p in enumerate(paths):
        assert all(x.q == 1 for x in expected[i, :])
        assert np.all(p == np.array([int(v) for v in expected[i, :]], dtype=object))


def construct(chart):
    d, k = chart.d, chart.d + 1
    if d == 0:
        eye = sp.eye(1)
        check_machine(chart, chart.rows, [eye, eye], chart.head / 2, F(1, 2))
        return {"affine_dimension": 0, "weak_strength": "1/2", "states": 1}
    center = [sp.Rational(1, 2)] + [sp.Rational(1, 2 * d)] * d
    embedding = sp.zeros(k)
    embedding[0, :] = sp.Matrix([center])
    decode = sp.ones(k, 1)
    for j in range(1, k):
        # Strict upper triangularity means all required vertex coordinates already exist.
        values = [abs(v) for a in chart.maps for v in decode * a[:j, j]]
        bound = max(1, *values, *map(abs, chart.rows[:, j]))
        scale = sp.Rational(1, 4 * d) / bound
        embedding[j, j], embedding[j, 0] = scale, -scale
        vertex = sp.Matrix([(int(i == j) - center[j]) / scale for i in range(k)])
        decode = decode.row_join(vertex)
    assert decode * embedding == sp.eye(k)
    kernels = [decode * a * embedding for a in chart.maps]
    head = decode * chart.head
    strength = 1 / (2 * max(max(map(abs, head)), sp.Integer(1)))
    head *= strength
    encoded = chart.rows * embedding
    check_machine(chart, encoded, kernels, head, strength)
    parameters = [v for t in kernels for v in t] + list(head)
    return {
        "affine_dimension": d,
        "states": k,
        "history_profiles": len(set(map(tuple, chart.rows.tolist()))),
        "weak_strength": str(strength),
        "minimum_transition": str(min(map(min, kernels))),
        "maximum_transition": str(max(map(max, kernels))),
        "maximum_parameter_numerator_bits": max(
            abs(int(sp.numer(v))).bit_length() for v in parameters
        ),
        "maximum_parameter_denominator_bits": max(
            int(sp.denom(v)).bit_length() for v in parameters
        ),
        "all_pure_start_word_products": 2**chart.horizon,
    }


def critical_delay(d):
    if d == 1:
        return F(1)
    return F(1, d) * F(d - 1, d) ** (d - 1)


def delay_check(maps, head, d, strength):
    paths = [head]
    for _ in range(d):
        paths = [t * v for t in maps for v in paths]
    for w, v in enumerate(paths):
        target = strength if w < 2 ** (d - 1) else -strength
        assert all(z == target for z in v)


def countdown(d):
    if d == 1:
        maps = [sp.Matrix([[1, 0], [1, 0]]), sp.Matrix([[0, 1], [0, 1]])]
        delay_check(maps, sp.Matrix([1, -1]), d, 1)
        return {"threshold": "1", "words_checked": 2}
    psi = sp.Rational(d - 1, d)
    peak = sp.Rational(critical_delay(d))
    c = (1 - peak) / (2 * (1 - psi ** (d - 1)))
    assert 0 < c < 1
    p = sp.zeros(d + 1)
    for i in range(d + 1):
        p[i, max(0, i - 1)] = 1
    qp, qm = sp.zeros(1, d + 1), sp.zeros(1, d + 1)
    qp[d], qm[0] = 1, (1 - c) ** (d - 1)
    for i in range(1, d):
        qm[i] = c * (1 - c) ** (d - 1 - i)
    one = sp.ones(d + 1, 1)
    h = sp.Matrix([0, 1, *[c] * (d - 1)])
    head = 2 * h - one
    assert sum(qm) == 1
    for j in range(d - 1):
        assert (qp * p**j * h)[0] == (qm * p**j * h)[0] == c
    maps = [psi * p + (1 - psi) * one * q for q in (qp, qm)]
    delay_check(maps, head, d, peak)
    center = psi**d * sp.eye(d + 1)[0, :]
    for j in range(d):
        center += (1 - psi) * psi**j * (qp + qm) * p**j / 2
    assert min(center) > 0 and sum(center) == 1 and (center * head)[0] == 0
    assert center * (maps[0] + maps[1]) / 2 == center
    positive = [(7 * t + one * center) / 8 for t in maps]
    softened = peak * sp.Rational(7, 8) ** d
    delay_check(positive, head, d, softened)
    overlap = sum(
        min(t[i, j] for t in positive for i in range(d + 1)) for j in range(d + 1)
    )
    assert overlap == sp.Rational(1, 8)
    return {
        "threshold": str(peak),
        "words_checked": 2**d,
        "rational_head_parameter": str(c),
        "common_refresh": "1/8",
        "positive_transition_strength": str(softened),
        "minimum_refreshed_entry": str(min(map(min, positive))),
        "largest_exact_kernel_denominator_bits": max(
            int(sp.denom(v)).bit_length() for t in maps for v in t
        ),
    }


def generative_rank(d, beta=F(1, 4)):
    # Independent direct integer evaluations of full block conditional probabilities.
    a, b = beta.numerator, beta.denominator
    bits = np.array(list(product((1, -1), repeat=d)), dtype=np.int64)
    kernel = np.prod(b + a * bits[:, None, :] * bits[None, :, :], axis=2)
    from pair_memory import modular_rank

    rank = int(modular_rank(kernel))
    assert rank == 2**d
    return rank


def triangle_matrices(chart, vertices):
    x = sp.Matrix([[1, *v] for v in vertices])
    inv = x.inv()
    kernels = [x * a * inv for a in chart.maps]
    return chart.rows * inv, kernels, x * chart.head


@lru_cache(None)
def fit_geometry(levels, strength):
    """Search a fixed family of rational triangles in the learned response coordinates."""
    chart = Responses([sp.Rational(strength) * v for v in levels])
    if chart.d == 0:
        return {"states": 1, "head": list(map(str, chart.head))}
    if chart.d == 1:
        lo, hi = min(chart.rows[:, 1]), max(chart.rows[:, 1])
        vertices = [[2 * lo - hi], [2 * hi - lo]]
        enc, ts, head = triangle_matrices(chart, vertices)
        if min(map(min, ts)) > 0 and max(map(abs, head)) < 1:
            check_machine(chart, enc, ts, head, 1)
            return {"states": 2, "vertices": list(map(str, (2 * lo - hi, 2 * hi - lo)))}
        return None
    # Grid units are eighths. Use both axis orientations for the flat side.
    from itertools import combinations

    grid = range(-7, 8)
    # Unit clipping at the vertices and invariance are evaluated on the inferred maps.
    for base, tip in product((-6, -4, -2, 0, 2, 4, 6), repeat=2):
        if base == tip:
            continue
        group = np.array(
            [
                [(left, base), (right, base), (top, tip)]
                for left, right in combinations(grid, 2)
                for top in grid
            ]
        )
        for vs in (group, group[:, :, ::-1]):
            vertices = np.concatenate((np.ones((*vs.shape[:2], 1)), vs / 8), axis=2)
            h = (vertices @ np.array(chart.head, dtype=float))[:, :, 0]
            keep = np.max(np.abs(h), axis=1) < 1 - 1e-8
            inverse = np.linalg.inv(vertices)
            for a in chart.maps:
                t = vertices @ np.array(a, dtype=float) @ inverse
                keep &= np.min(t, axis=(1, 2)) > 1e-8
            for idx in np.flatnonzero(keep):
                z = [[sp.Rational(int(v), 8) for v in row] for row in vs[idx]]
                enc, ts, head = triangle_matrices(chart, z)
                if min(enc) >= 0 and min(map(min, ts)) > 0 and max(map(abs, head)) < 1:
                    check_machine(chart, enc, ts, head, 1)
                    return {
                        "states": 3,
                        "response_vertices": [list(map(str, p)) for p in z],
                        "kernels": [
                            [list(map(str, row)) for row in t.tolist()] for t in ts
                        ],
                        "head": list(map(str, head)),
                    }
    return None


def learned_delay():
    from fit_autonomous_width import context_tree, suffix_counts

    a = F(1, 8)
    rng = np.random.default_rng(7288176)
    sizes = (512, 4096, 32768)
    out = {}
    for name, units in (("delay", (1, 1, -1, -1)), ("fair", (0, 0, 0, 0))):
        weights, truth = [], []
        for bits in product((0, 1), repeat=6):
            w = 2 * bits[0] + bits[1]
            mass = F(1, 4)
            for b in bits[2:]:
                mass *= (1 + (1 - 2 * b) * a * units[w]) / 2
                w = (2 * w + b) % 4
            weights.append(float(mass))
            truth.append(float(a * units[w]))
        weights, truth = np.array(weights), np.array(truth)

        def test_gain(m, truth=truth, weights=weights):
            return float(weights @ (truth * np.arctanh(m) + 0.5 * np.log1p(-m * m)))

        rows = {n: [] for n in sizes}
        for _ in range(32):
            bits = np.empty(max(sizes) + 6, dtype=np.uint8)
            bits[:2] = rng.integers(2, size=2)
            w = 2 * int(bits[0]) + int(bits[1])
            for t, v in enumerate(rng.integers(16, size=len(bits) - 2), 2):
                b = int(v) >= 8 + units[w]
                bits[t] = b
                w = (2 * w + b) % 4
            for n in sizes:
                counts = suffix_counts(bits, n)
                short = counts.reshape(16, 4, 2).sum(axis=0)
                local = (short[:, 0] - short[:, 1]) / (short.sum(axis=1) + 1)
                levels = tuple(map(int, np.clip(np.rint(local / float(a)), -1, 1)))
                geometry = fit_geometry(levels, a)
                m = np.tile(float(a) * np.array(levels), 16)
                rows[n].append(
                    (
                        levels == units,
                        geometry is not None,
                        test_gain(m),
                        test_gain(np.tile(local, 16)),
                        test_gain(2 * context_tree(counts) - 1),
                    )
                )
        out[name] = {
            "realization_from_recovered_table": fit_geometry(units, a),
            "sizes": [
                {
                    "raw_tokens": n,
                    "exact_table": sum(x[0] for x in records),
                    "certified_grid_or_constant_realization": sum(
                        x[1] for x in records
                    ),
                    "quantized_table_gain": float(np.mean([x[2] for x in records])),
                    "direct_smoothed_gain": float(np.mean([x[3] for x in records])),
                    "depth_six_tree_gain": float(np.mean([x[4] for x in records])),
                }
                for n, records in rows.items()
            ],
        }
    return out


def audit():
    rng = np.random.default_rng(6492)
    tables = {}
    for i, units in enumerate(UNITS):
        tables[f"six_sign_{i + 1}"] = construct(Responses(units.tolist()))
    delays = []
    for d in range(1, 7):
        table = [1] * (2 ** (d - 1)) + [-1] * (2 ** (d - 1))
        weak = construct(Responses(table))
        assert weak["affine_dimension"] == d
        delays.append(
            {
                "lag": d,
                "weak": weak,
                "critical": countdown(d),
                "generator_rank": generative_rank(d),
            }
        )
    random_rules = []
    for d in range(1, 7):
        # Integer numerator tables with a common scale, kept within the signed-head domain.
        f = [sp.Rational(int(v), 32) for v in rng.integers(-32, 33, size=2**d)]
        found = construct(Responses(f))
        bound = 2 ** (d // 2) + 2 ** ((d + 1) // 2) - 2
        assert found["affine_dimension"] <= bound
        odd_table = [
            (1 - 2 * x[0])
            * (-1) ** sum(x[i] * x[d - i] for i in range(1, (d - 1) // 2 + 1))
            for x in product((0, 1), repeat=d)
        ]
        odd_rank = Responses(odd_table).d
        assert odd_rank == bound
        random_rules.append(
            {
                "horizon": d,
                "generic_maximum": bound,
                "explicit_odd_table_rank": odd_rank,
                **found,
            }
        )
    return {
        "registration": REGISTRATION,
        "six_sign_rules": tables,
        "delays": delays,
        "unrestricted_sample_tables": random_rules,
        "same_strength_passive_fits": learned_delay(),
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
