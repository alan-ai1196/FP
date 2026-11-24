"""Exact spectral identities and population calculations for moment-limited prediction."""

import argparse
import json
from fractions import Fraction as F
from math import comb, log
from pathlib import Path

import numpy as np
from grouped_forecast import coefficient, conditional_modes, eigenvalue, kt_counts
from scipy.special import rel_entr, roots_legendre, xlogy
from scipy.stats import binom
from threadpoolctl import threadpool_limits


def exact_spectrum():
    entries = pairs = 0
    for m in range(19):
        counts = [
            F(comb(2 * k, k) * comb(2 * (m - k), m - k), 4**m) for k in range(m + 1)
        ]
        modes = []
        for k in range(m + 1):
            signed = 2 * k - m
            hs = [F(1), F(signed, m + 1)]
            for j in range(1, m + 1):
                hs.append((2 * signed * hs[-1] - (m + 1 - j) * hs[-2]) / (m + 1 + j))
            for j in range(m + 1):
                assert hs[j] == eigenvalue(m, j) * coefficient(m, j, k)
                entries += 1
            assert hs[m + 1] == 0
            modes.append(hs)
        for j in range(m + 1):
            for ell in range(j + 1):
                val = sum(w * h[j] * h[ell] for w, h in zip(counts, modes))
                ref = (
                    F(1)
                    if j == ell == 0
                    else eigenvalue(m, j) / 2
                    if j == ell
                    else F(0)
                )
                assert val == ref
                pairs += 1
    return {"recurrence_inverse_entries": entries, "inner_products": pairs}


def phase_information(t, n, order):
    nodes, weights = roots_legendre(order)
    u = (nodes + 1) * np.pi / (2 * n)
    angles = 2 * np.pi * np.arange(n) / n
    k = np.arange(t + 1)
    kt = kt_counts(t)
    risk = []
    for shift in u:
        p = np.cos((angles + shift) / 2) ** 2
        law = binom.pmf(k[:, None], t, p).mean(axis=1)
        risk.append(rel_entr(law, kt).sum())
    return float(weights @ risk / 2)


def smooth_lower(t, n):
    if n > t:
        return 0.0, 0.0
    h = np.clip(conditional_modes(t, n)[:, n], -1.0, 1.0)
    tiny = np.abs(h) < 1e-3
    v = h[tiny] ** 2
    info = np.empty_like(h)
    info[tiny] = v * (0.5 + v * (1 / 12 + v / 30))
    h2 = h[~tiny]
    info[~tiny] = (xlogy(1 + h2, 1 + h2) + xlogy(1 - h2, 1 - h2)) / 2
    js = float(kt_counts(t) @ info)
    lower = float(eigenvalue(t, n)) / 4
    assert js >= lower * (1 - 2e-9)
    return js, lower


def likelihood_check(t, m):
    theta = np.linspace(0, np.pi, 515)
    k = np.arange(t + 1)
    p = np.cos(theta / 2) ** 2
    p[-1] = 0
    law = binom.pmf(k[:, None], t, p)
    j = np.arange(1, m + 1)
    taper = 1 - j / (m + 1)
    harmonic = 1 + 2 * (conditional_modes(t, m)[:, 1:] * taper) @ np.cos(
        j[:, None] * theta
    )
    approx = kt_counts(t)[:, None] * harmonic
    assert approx.min() > 0
    ratio = np.divide(law, approx)
    high = float(np.max(ratio))
    assert high < 600 * max(1, np.sqrt(t) / (m + 1))
    # Integrate the actual convolution independently with enough circle nodes
    # to integrate a trig polynomial of joint degree m+t exactly.
    M = 2 * (t + m + 1)
    ang = 2 * np.pi * (np.arange(M) + 0.371) / M
    pp = np.cos(ang / 2) ** 2
    base = binom.pmf(k[:, None], t, pp)
    for index in (0, 71, 257, 514):
        delta = (ang - theta[index] + np.pi) % (2 * np.pi) - np.pi
        kernel = (m + 1) * (
            np.sinc((m + 1) * delta / (2 * np.pi)) / np.sinc(delta / (2 * np.pi))
        ) ** 2
        direct = base @ kernel / M
        np.testing.assert_allclose(direct, approx[:, index], rtol=2e-10, atol=5e-14)
    return high


def run():
    with threadpool_limits(limits=1):
        phase = []
        for t in (16, 256, 4096):
            for m in (0, 3, 15, 31):
                v1 = phase_information(t, m + 1, 96)
                v2 = phase_information(t, m + 1, 192)
                js, lower = smooth_lower(t, m + 1)
                assert abs(v1 - v2) < 2e-6
                assert v2 + 1e-9 >= log(np.sqrt(t) / (m + 1)) - 0.5 * log(
                    2 * np.pi * np.e
                )
                if t <= m:
                    assert abs(v2) < 1e-10
                phase.append(
                    {
                        "T": t,
                        "m": m,
                        "phase_information": v2,
                        "quadrature_difference": abs(v1 - v2),
                        "smooth_pair_information": js,
                        "spectral_lower": lower,
                    }
                )
        ratios = [
            {"T": t, "m": m, "max_ratio": likelihood_check(t, m)}
            for t in (1, 8, 32, 128, 256)
            for m in (0, 1, 3, 7, 15, 31)
        ]
    return {"exact": exact_spectrum(), "phase": phase, "fejer_tests": ratios}


if __name__ == "__main__":
    from coin_memory import compare

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = run()
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched spectral and predictive calculations.")
    elif args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
