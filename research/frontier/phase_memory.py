"""Observable phase moments of raw finite-clock words, with destructive or preserving reads."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import cos, fsum, log, pi, prod
from pathlib import Path

import numpy as np
import sympy as sp


def add_exact(basis, row):
    row = list(row)
    for i in range(len(row)):
        value = row[i]
        if not value:
            continue
        if i not in basis:
            basis[i] = tuple(v / value for v in row)
            return True
        row = [v - value * b for v, b in zip(row, basis[i], strict=True)]
    return False


def exact_dimensions(k, reset, cap):
    radical = {5: 5, 8: 2}.get(k)
    field = sp.QQ.algebraic_field(sp.sqrt(radical)) if radical else sp.QQ
    red = [
        field.from_sympy(sp.Rational(1, 2) + sp.cos(2 * sp.pi * j / k) / 4)
        for j in range(k)
    ]
    ones = (field.one,) * k
    basis = {0: ones}
    ranks = [1]
    for _ in range(cap):
        old = list(basis.values())
        for vector in old:
            for probabilities in (red, [field.one - v for v in red]):
                read = tuple(
                    q * (vector[0] if reset else vector[j])
                    for j, q in enumerate(probabilities)
                )
                for j in range(k):
                    add_exact(basis, read[j:] + read[:j])
        ranks.append(len(basis))
    return ranks


def modular_witnesses(k, reset, cap):
    # A separate exhaustive word evaluator over F_241. All tested periods divide 240.
    prime = 241
    generator = next(
        g
        for g in range(2, prime)
        if all(pow(g, 240 // p, prime) != 1 for p in (2, 3, 5))
    )
    z = pow(generator, 240 // k, prime)
    half = pow(2, -1, prime)
    red = [
        (half + (pow(z, j, prime) + pow(z, (-j) % k, prime)) * pow(8, -1, prime))
        % prime
        for j in range(k)
    ]
    results = []
    for n in range(cap + 1):
        basis = {}
        shifted = {}
        lengths = []
        for gaps in product(range(k), repeat=n):
            row = []
            tick_powers = pow(half, sum(gaps) + n, prime)
            for start in range(k):
                state = start
                likelihood = tick_powers
                for gap in gaps:
                    state = (state + gap) % k
                    likelihood = likelihood * red[state] % prime
                    if reset:
                        state = 0
                row.append(likelihood)
            if insert_modular(basis, row, prime):
                lengths.append(sum(gaps) + n)
            if not any(gaps[1:]):
                insert_modular(shifted, row, prime)
        results.append((len(basis), max(lengths), len(shifted)))
    return results


def insert_modular(basis, row, prime):
    for i in range(len(row)):
        pivot = row[i]
        if pivot == 0:
            continue
        if i not in basis:
            inv = pow(pivot, -1, prime)
            basis[i] = [(v * inv) % prime for v in row]
            return True
        row = [(v - pivot * a) % prime for v, a in zip(row, basis[i], strict=True)]
    return False


def raw_information(reset, cap=8):
    # All four phase emission numerators have denominator eight, including the tick.
    red = (3, 2, 1, 2)
    counts = [0] * (cap + 1)
    absolute = [0] * (cap + 1)
    js = [[] for _ in range(cap + 1)]

    def visit(a, b, n):
        pa, pb = sum(a), sum(b)
        total = pa + pb
        counts[n] += 1
        absolute[n] += abs(pa - pb)
        if pa != pb:
            js[n].append(pa * log(2 * pa / total) + pb * log(2 * pb / total))
        if n == cap:
            return
        visit(
            tuple(4 * v for v in (a[-1], *a[:-1])),
            tuple(4 * v for v in (b[-1], *b[:-1])),
            n + 1,
        )
        for rates in (red, tuple(4 - v for v in red)):
            a1 = tuple(v * q for v, q in zip(a, rates, strict=True))
            b1 = tuple(v * q for v, q in zip(b, rates, strict=True))
            if reset:
                a1 = (sum(a1), 0, 0, 0)
                b1 = (sum(b1), 0, 0, 0)
            visit(a1, b1, n + 1)

    visit((1, 0, 1, 0), (0, 1, 0, 1), 0)
    answer = []
    for n in range(1, cap + 1):
        assert counts[n] == 3**n
        # Both phase priors have denominator two.
        tv = F(absolute[n], 4 * 8**n)
        info = fsum(js[n]) / (4 * 8**n)
        if reset or n == 1:
            assert tv == 0 and info == 0
        answer.append(
            {"tokens": n, "total_variation": str(tv), "information_nats": info}
        )
    return answer


def highest_mode_check():
    cases = 0
    largest = 0.0
    for m, k in ((1, 3), (2, 5), (3, 8), (4, 11), (3, 6)):
        amplitude = 0.375
        contrast = 0.5
        theta = [2 * pi * j / k for j in range(k)]
        for gaps in (
            (0,) * m,
            tuple(range(1, m + 1)),
            tuple((2 * i + 1) % k for i in range(m)),
        ):
            angles = [2 * pi * sum(gaps[: i + 1]) / k for i in range(m)]
            for signs in product((-1, 1), repeat=m):
                direct = fsum(
                    2
                    * amplitude
                    * cos(m * u)
                    / k
                    * prod(
                        (1 + t * contrast * cos(u + v)) / 2
                        for t, v in zip(signs, angles, strict=True)
                    )
                    for u in theta
                )
                theory = (
                    2 * amplitude * (contrast / 4) ** m * prod(signs) * cos(sum(angles))
                )
                if k == 2 * m:
                    theory *= 2
                largest = max(largest, abs(direct - theory))
                cases += 1
    assert largest < 1e-14
    return {"cases": cases, "max_absolute_error": largest}


def parity_information(m):
    k = 2 * m
    c = 0.5
    phase = np.arange(k)
    weights = 0.5 ** (1 + phase) / (1 - 0.5**k)
    signs = np.array(list(product((-1, 1), repeat=m)))
    total = []
    max_error = 0.0
    cosine_squared = 0.0
    for gaps in product(range(k), repeat=m):
        ages = np.cumsum(gaps)
        weight = prod(weights[list(gaps)])
        cosines = np.cos(2 * np.pi * (phase[:, None] + ages) / k)
        colors = ((1 + c * signs[None, :, :] * cosines[:, None, :]) / 2).prod(axis=2)
        common = colors.mean(axis=0)
        signed = (((-1) ** phase) @ colors) / k
        cosine = np.cos(2 * np.pi * sum(ages) / k)
        formula = 2 * (c / 4) ** m * signs.prod(axis=1) * cosine
        max_error = max(max_error, float(np.max(np.abs(formula - signed))))
        total.append(weight * float(np.sum(signed**2 / common)))
        cosine_squared += weight * cosine**2
    assert max_error < 2e-15 and abs(cosine_squared - (1 + 1 / (2**m - 1)) / 2) < 2e-13
    return {
        "reads": m,
        "residue_and_color_transcripts": (2 * k) ** m,
        "parity_information": fsum(total),
        "mean_cosine_squared": float(cosine_squared),
        "signed_probability_formula_max_error": max_error,
    }


def stopped_two_marks():
    red = (F(3, 4), F(1, 2), F(1, 4), F(1, 2))
    tick_weights = (F(8, 15), F(4, 15), F(2, 15), F(1, 15))
    squared = F(0)
    mutual = []
    for u, v in product(range(4), repeat=2):
        for a, b in product((0, 1), repeat=2):
            values = []
            for j in range(4):
                x = red[(j + u) % 4]
                y = red[(j + u + v) % 4]
                values.append((x if a else 1 - x) * (y if b else 1 - y))
            even = (values[0] + values[2]) / 2
            odd = (values[1] + values[3]) / 2
            mean = (odd + even) / 2
            weight = tick_weights[u] * tick_weights[v]
            squared += weight * (even - odd) ** 2 / (4 * mean)
            mutual.append(
                float(weight)
                * (float(even) * log(even / mean) + float(odd) * log(odd / mean))
                / 2
            )
    assert squared == F(2, 189)
    return {
        "uniform_phase_parity_information": str(squared),
        "pooled_equal_prior_loss_nats": fsum(mutual),
    }


def longer_rows():
    rng = np.random.Generator(np.random.PCG64(261128))
    rows = []
    trials = 512
    for k in (4, 8, 16, 32):
        offset = np.arange(k)
        root = np.exp(2j * np.pi * offset / k)
        start = rng.integers(k, size=trials)
        turns = 8 * k
        ticks = k * turns
        marks = rng.binomial(turns, 0.5, size=(trials, k))
        red = rng.binomial(
            marks, (1 + 0.5 * np.cos(2 * np.pi * (start[:, None] + offset) / k)) / 2
        )
        estimate = (2 * red - marks) @ np.conjugate(root)
        projection = (estimate[:, None] * np.conjugate(root[None, :])).real
        largest = projection.max(axis=1, keepdims=True)
        ties = abs(projection - largest) <= 1e-9
        unique = ties.sum(axis=1) == 1
        decoded = projection.argmax(axis=1)
        # Additional waiting time to a tick when the first observation was a mark.
        initial_marks = int(marks.sum())
        raw = (
            trials * ticks
            + initial_marks
            + int(rng.negative_binomial(initial_marks, 0.5))
        )
        rows.append(
            {
                "k": k,
                "panels": trials,
                "ticks_per_panel": ticks,
                "unique_correct_phases": int(np.sum(unique & (decoded == start))),
                "unique_correct_parities": int(
                    np.sum(unique & (decoded % 2 == start % 2))
                ),
                "ties": int(np.sum(~unique)),
                "total_raw_tokens": raw,
            }
        )
    return rows


def audit():
    rows = {}
    for k in (3, 4, 5, 8):
        for reset in (False, True):
            ranks = exact_dimensions(k, reset, 4)
            independent = modular_witnesses(k, reset, 4)
            expected = [
                1 if j == 0 else 3 if reset else min(k, 2 * j + 1) for j in range(5)
            ]
            assert (
                ranks
                == expected
                == [r for r, _, _ in independent]
                == [s for _, _, s in independent]
            )
            rows[f"{k}_{'reset' if reset else 'hold'}"] = {
                "ranks_by_reads": ranks,
                "longest_independent_witness_in_tick_gap_order": [
                    l for _, l, _ in independent
                ],
            }
    hold = raw_information(False)
    assert hold[1]["total_variation"] == "1/32"
    return {
        "registration": "53c10ef",
        "ranks": rows,
        "reset_raw_prefixes": raw_information(True),
        "hold_raw_prefixes": hold,
        "four_phase_stop_at_second_mark": stopped_two_marks(),
        "first_visible_harmonic": highest_mode_check(),
        "first_informative_panels": [parity_information(m) for m in (2, 3, 4)],
        "supplemental_longer_panels_pcg64_261128": longer_rows(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(encoded.encode())
    else:
        print(encoded, end="")
