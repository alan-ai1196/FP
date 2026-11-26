"""Exact bounds for a sampled binary state and for a reported state probability."""

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path

import sympy as sp

REGISTRATION = "9ba8046"
WORDS = tuple(product((1, -1), repeat=3))


def selector(a, b, c):
    return b if a == 1 else c


def direct_channel(kernel, start):
    ends = []
    for word in WORDS:
        p = start
        for s in word:
            row0, row1 = kernel[int(s < 0)], kernel[2 + int(s < 0)]
            p = (1 - p) * row0 + p * row1
        ends.append(2 * p - 1)
    return sum(ends) / 8, sum(selector(*word) * z for word, z in zip(WORDS, ends)) / 8


def moments(kernel, start):
    u, v = (kernel[0] + kernel[1]) / 2, (kernel[2] + kernel[3]) / 2
    h0, h1 = (kernel[0] - kernel[1]) / 2, (kernel[2] - kernel[3]) / 2
    ell = v - u
    first = u + ell * start
    second = u + ell * first
    b = ell * first + second
    return 2 * (u + ell * second) - 1, (1 + ell - b) * h0 + b * h1


def check_kernels():
    count = 0
    for kernel in product([F(i, 4) for i in range(5)], repeat=4):
        for start in (F(0), F(1, 2), F(1)):
            m, c = direct_channel(kernel, start)
            assert (m, c) == moments(kernel, start)
            # The global entropy proof needs the reset endpoints only.
            if start in (0, 1):
                assert 12 * c**2 <= 3 - 5 * m**2 + 2 * m**4
            count += 1
    return count


def bernstein():
    x, y = sp.symbols("x y")
    records = []
    for i, j, e in product((0, 1), (0, 1), (-1, 1)):
        u, v = (i + x) / 2, (j + y) / 2
        h0 = u if i == 0 else 1 - u
        h1 = v if j == 0 else 1 - v
        ell = v - u
        m = 2 * u * (1 + ell + ell**2) - 1
        b = u * (1 + 2 * ell)
        c = (1 + ell - b) * h0 + e * b * h1
        polynomial = sp.Poly(3 - 5 * m**2 + 2 * m**4 - 12 * c**2, x, y, domain=sp.QQ)
        assert polynomial.degree(x) <= 12 and polynomial.degree(y) <= 8
        power = {indices: F(q) for indices, q in polynomial.terms()}
        coefficients = []
        test_value = F(0)
        x0, y0 = F(1, 3), F(2, 5)
        for k, l in product(range(13), range(9)):
            bkl = sum(
                v * F(comb(k, a), comb(12, a)) * F(comb(l, d), comb(8, d))
                for (a, d), v in power.items()
                if a <= k and d <= l
            )
            assert bkl >= 0
            coefficients.append(bkl)
            test_value += (
                bkl
                * comb(12, k)
                * x0**k
                * (1 - x0) ** (12 - k)
                * comb(8, l)
                * y0**l
                * (1 - y0) ** (8 - l)
            )
        assert test_value == sum(v * x0**a * y0**d for (a, d), v in power.items())
        records.append(
            {
                "quadrant": [i, j],
                "contrast_sign": e,
                "coefficients": len(coefficients),
                "zeros": coefficients.count(0),
                "least_positive": str(min(v for v in coefficients if v > 0)),
            }
        )
    return records


def log_bounds(x, terms=24):
    # Directed rational series bounds followed by directed decimal rounding.
    z = (x - 1) / (x + 1)
    s = 2 * sum(z ** (2 * i + 1) / (2 * i + 1) for i in range(terms))
    err = 2 * abs(z) ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z))
    scale = 10**18
    return F((scale * (s - err)) // 1, scale), F(-((-scale * (s + err)) // 1), scale)


def outcomes(beta, replicas):
    # Conditional state mean after three half-overwrites from a fair reset.
    law = defaultdict(F)
    for word in WORDS:
        mean = F(word[0] + 2 * word[1] + 4 * word[2], 8)
        p = (1 + mean) / 2
        if replicas is None:
            values = [(mean, F(1))]
        else:
            values = [
                (
                    F(2 * k, replicas) - 1,
                    comb(replicas, k) * p**k * (1 - p) ** (replicas - k),
                )
                for k in range(replicas + 1)
            ]
        for value, mass in values:
            for sign in (1, -1):
                law[sign * value] += mass * (1 + sign * beta * selector(*word)) / 16
    assert sum(law.values()) == 1
    return law


def gain_bounds(law, a):
    bounds = [(w, log_bounds(1 + a * x)) for x, w in law.items()]
    return tuple(sum(w * b[j] for w, b in bounds) for j in (0, 1))


def slope(law, a):
    return sum(w * x / (1 + a * x) for x, w in law.items())


def optimize(law):
    lo, hi = F(0), F(1)
    assert slope(law, lo) > 0
    assert F(-1) in law or slope(law, hi) <= 0
    for _ in range(40):
        mid = (lo + hi) / 2
        if slope(law, mid) > 0:
            lo = mid
        else:
            hi = mid
    mid = (lo + hi) / 2
    lower, upper = gain_bounds(law, mid)
    # Tangent upper bound on the entire final bracket by concavity.
    upper += abs(slope(law, mid)) * (hi - lo)
    return mid, lower, upper


def entropy_bounds(a):
    lo1, hi1 = log_bounds(1 + a)
    lo2, hi2 = log_bounds(1 - a)
    return ((1 + a) * lo1 + (1 - a) * lo2) / 2, ((1 + a) * hi1 + (1 - a) * hi2) / 2


def comparisons(beta):
    reference = entropy_bounds(beta / 2)
    full = entropy_bounds(beta)
    rows = []
    for m in (1, 2, 3, 4, 5, None):
        law = outcomes(beta, m)
        a, lo, hi = optimize(law)
        ea = sum(w * x for x, w in law.items())
        e2 = sum(w * x * x for x, w in law.items())
        explained = ea**2 / (beta**2 * e2)
        assert explained == (F(3, 7) if m is None else F(9 * m, 21 * m + 43))
        comparison = (
            "above"
            if lo > reference[1]
            else "below"
            if hi < reference[0]
            else "unresolved"
        )
        assert comparison != "unresolved"
        assert hi < full[0] / 2
        rows.append(
            {
                "replicas": m,
                "strength_midpoint": float(a),
                "gain_midpoint": float((lo + hi) / 2),
                "width_of_gain_interval_less_than": "1e-15",
                "compared_to_best_sampled_bit": comparison,
                "weak_signal_oracle_fraction": str(explained),
            }
        )
        assert hi - lo < F(1, 10**15)
    return {
        "contrast": str(beta),
        "best_sampled_bit": float(sum(reference) / 2),
        "full_three_state_gain": float(sum(full) / 2),
        "readouts": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "registration": REGISTRATION,
        "rational_kernel_checks": check_kernels(),
        "bernstein_boxes": bernstein(),
        "replica_comparisons": [comparisons(F(1, 4)), comparisons(F(1, 2))],
    }
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
