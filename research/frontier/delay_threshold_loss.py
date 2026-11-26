"""Predictive loss and raw-token acquisition near an exact stochastic width threshold."""

import argparse
import json
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.stats import binom

REGISTRATION = "da74cc3"
SIZES = (256, 4096, 65536)
MARGINS = (F(1, 64), F(1, 32), F(1, 16))
REPEATS = 64


def decimal(x):
    return Decimal(x.numerator) / Decimal(x.denominator)


def critical(lag):
    return F(lag - 1, lag) ** (lag - 1) / lag


def signed_kl(a, b):
    """Binary KL, with signed means instead of positive-outcome probabilities."""
    difference = decimal(b - a)
    a, b = decimal(a), decimal(b)
    if abs(difference) < (1 - abs(a)) * Decimal("1e-8"):
        # The linear terms cancel. Ten terms retain over sixty relative digits here.
        positive = difference / (1 + a)
        negative = difference / (1 - a)
        return sum(
            ((1 + a) * (-positive) ** j + (1 - a) * negative**j) / (2 * j)
            for j in range(2, 12)
        )
    return ((1 + a) * ((1 + a) / (1 + b)).ln() + (1 - a) * ((1 - a) / (1 - b)).ln()) / 2


def triangle(a):
    """Build barycentric kernels from the two horizontal images of the pure vertices."""
    vertices = sp.Matrix([[-1, -1, 1], [1, -1, 1], [F(1, 2), 3, 1]])
    head = vertices[:, 0]
    slopes = {1: F(1, 4), -1: a}
    actions = {}
    for sign, slope in slopes.items():
        target = sp.Matrix([[slope * y, sign, 1] for y in vertices[:, 1]])
        k = target * vertices.inv()
        assert min(k) >= 0 and k * sp.ones(3, 1) == sp.ones(3, 1)
        actions[sign] = k
    for u, v in product((-1, 1), repeat=2):
        assert actions[u] * actions[v] * head == u * slopes[v] * sp.ones(3, 1)
    return {
        str(s): [[str(x) for x in row] for row in k.tolist()]
        for s, k in actions.items()
    }


def extra_component(lag):
    """One extra protected capture state with an initialized, input-independent phase mass."""
    capture = F(1, lag - 1)
    p = 1 - capture
    r = (1 + p) / 2
    strength = p ** (lag - 2) / lag
    refractory = F(lag, 2) - sum(
        p ** (j - 1) * r ** (lag - 1 - j) for j in range(1, lag - 1)
    )
    refractory -= p ** (lag - 2) / 2
    head = sp.Matrix(
        [refractory, refractory, 0] + [r ** (i - 1) for i in range(1, lag)]
    )
    head = 2 * head - sp.ones(lag + 2, 1)
    assert min(head) >= -1 and max(head) <= 1 and strength > critical(lag)
    law = [F(1, 2 * lag), F(1, 2 * lag), F(0)]
    for i in range(1, lag):
        mass = p ** (lag - 1 - i)
        if i <= lag - 2:
            mass += r * p ** (lag - 2 - i)
        law.append(mass / (2 * lag))
    law[2] = 1 - sum(law)
    pi = sp.Matrix([law])
    kernels = {}
    for sign in (-1, 1):
        k = sp.zeros(lag + 2)
        k[0, lag + 1] = 1
        k[1, lag] = r
        k[1, 2] = 1 - r
        for i in range(lag):
            k[i + 2, int(sign == -1)] = capture
            k[i + 2, 2 + max(i - 1, 0)] = p
        assert k * sp.ones(lag + 2, 1) == sp.ones(lag + 2, 1)
        kernels[sign] = k
    assert min(pi) > 0 and pi * (kernels[1] + kernels[-1]) == 2 * pi
    count = 0
    for refresh in (F(0), F(1, 2)):
        current = {
            s: (1 - refresh) * k + refresh * sp.ones(lag + 2, 1) * pi
            for s, k in kernels.items()
        }
        if refresh:
            assert all(min(k) > 0 for k in current.values())
        frontier = [((), pi)]
        for length in range(lag + 3):
            for word, belief in frontier:
                expected = (
                    word[-lag] * strength * (1 - refresh) ** lag if length >= lag else 0
                )
                assert (belief * head)[0] == expected
                count += 1
            if length < lag + 2:
                frontier = [
                    (word + (sign,), belief * k)
                    for word, belief in frontier
                    for sign, k in current.items()
                ]
    return {
        "lag": lag,
        "components": lag + 2,
        "capture_probability": str(capture),
        "countdown_head_ratio": str(r),
        "refractory_head_probability": str(refractory),
        "attained_signed_strength": str(strength),
        "exact_word_checks_including_refresh": count,
    }


def analytic(lag, delta):
    cap = critical(lag)
    a = cap + delta
    eta = (1 - a) / 2
    root = (decimal(a / cap).ln() / lag).exp()
    conditional = min(decimal(a) / 2, decimal(a) ** 2 * (root - 1) / 8)
    lower = conditional**2 * decimal(eta / 2) ** lag / (2 * (lag + 1))
    clipped = signed_kl(a, cap)
    assert 0 < lower < clipped and signed_kl(a, a) == 0
    ans = {
        "lag": lag,
        "margin": str(delta),
        "critical_strength": str(cap),
        "above_strength": str(a),
        "proved_stationary_nll_lower_bound": float(lower),
        "clipped_oracle_nll_excess": float(clipped),
        "shift_register_oracle_nll_excess": 0,
    }
    if lag == 2:
        ans["adaptive_triangle"] = triangle(a)
        ans["best_two_word_three_component_excess"] = float(clipped / 2)
    return ans


def count_threshold(n, low, high, unknown_orientation):
    """First positive-side count that prefers the stronger source at equal prior odds."""
    lp = [decimal((1 + s) / 2).ln() for s in (low, high)]
    lm = [decimal((1 - s) / 2).ln() for s in (low, high)]

    def loglike(k, j):
        value = k * lp[j] + (n - k) * lm[j]
        if unknown_orientation:
            value += (1 + (-(2 * k - n) * (lp[j] - lm[j])).exp()).ln()
        return value

    def likelihood(s, k):
        q = (1 + s) / 2
        value = q**k * (1 - q) ** (n - k)
        if unknown_orientation:
            value += q ** (n - k) * (1 - q) ** k
        return value

    left = (n + 1) // 2 if unknown_orientation else 0
    right = n + 1
    while left < right:
        k = (left + right) // 2
        gap = loglike(k, 1) - loglike(k, 0)
        if abs(gap) < Decimal("1e-50"):
            above = likelihood(high, k) > likelihood(low, k)
        else:
            above = gap > 0
        if above:
            right = k
        else:
            left = k + 1
    return left


def tail(n, p, k, down):
    """Sum the binomial tail from its boundary, bounding discarded mass by 1e-58 relative."""
    q = 1 - p
    term = Decimal(comb(n, k)) * p**k * q ** (n - k)
    total = term
    for _ in range(k if down else n - k):
        ratio = k * q / ((n - k + 1) * p) if down else (n - k) * p / ((k + 1) * q)
        term *= ratio
        k += -1 if down else 1
        if ratio <= 1 and term * (n + 1) < total * Decimal("1e-58"):
            break
        total += term
    return total


def decision(n, low, high):
    ans = {}
    for unknown in (False, True):
        k = count_threshold(n, low, high, unknown)
        lp, hp = decimal((1 + low) / 2), decimal((1 + high) / 2)
        false_large = tail(n, lp, k, False)
        false_small = tail(n, hp, k - 1, True)
        check_large = binom.sf(k - 1, n, float(lp))
        check_small = binom.cdf(k - 1, n, float(hp))
        if unknown:
            false_large += tail(n, lp, n - k, True)
            false_small -= tail(n, hp, n - k, True)
            check_large += binom.cdf(n - k, n, float(lp))
            check_small -= binom.cdf(n - k, n, float(hp))
        assert abs(float(false_large) - check_large) < 1e-9 * float(false_large)
        assert abs(float(false_small) - check_small) < 1e-9 * float(false_small)
        ans["unknown_orientation" if unknown else "supplied_orientation"] = {
            "first_high_agreement_count": k,
            "false_large_probability": float(false_large),
            "false_small_probability": float(false_small),
            "bayes_error": float((false_large + false_small) / 2),
        }
    return ans


def raw_tapes(rng, lag, amplitude):
    """Interleave L independent chains. The learner receives their raw token matrix."""
    n = SIZES[-1]
    orientations = rng.permutation(
        np.tile(np.array([1, -1], dtype=np.int8), REPEATS // 2)
    )
    p = (1 + amplitude) / 2
    draws = rng.integers(p.denominator, size=(REPEATS, n), dtype=np.int16)
    innovations = (2 * (draws < p.numerator).astype(np.int8) - 1) * orientations[
        :, None
    ]
    raw = np.empty((REPEATS, n + lag), dtype=np.int8)
    raw[:, :lag] = 2 * rng.integers(2, size=(REPEATS, lag), dtype=np.int8) - 1
    for j in range(lag):
        jumps = np.cumprod(innovations[:, j::lag], axis=1, dtype=np.int8)
        raw[:, lag + j :: lag] = jumps * raw[:, j, None]
    assert np.array_equal(raw[:, lag:] * raw[:, :-lag], innovations)
    return raw, orientations


def fits(raw, orientations, lag, n, magnitude, cap, tests):
    counts = (raw[:, lag : lag + n] == raw[:, :n]).sum(axis=1)
    oriented = np.where(orientations > 0, counts, n - counts)
    folded = np.maximum(counts, n - counts)
    known_large = (
        oriented >= tests["supplied_orientation"]["first_high_agreement_count"]
    )
    large = folded >= tests["unknown_orientation"]["first_high_agreement_count"]
    unpriced, clipped, selected, adaptive = [], [], [], []
    margin = abs(magnitude - cap)
    brackets = [s * m for s in (-1, 1) for m in (cap - margin, cap + margin)]
    bracket_logs = [
        (decimal((1 + b) / 2).ln(), decimal((1 - b) / 2).ln()) for b in brackets
    ]
    bracket_kl = []
    for i, k in enumerate(counts):
        k = int(k)
        a = int(orientations[i]) * magnitude
        fit = F(2 * k - n, n + 1)
        limited = max(-cap, min(fit, cap))
        unpriced.append(signed_kl(a, fit))
        clipped.append(signed_kl(a, limited))
        selected.append(unpriced[-1] if large[i] else clipped[-1])
        scores = [k * lp + (n - k) * lm for lp, lm in bracket_logs]
        pivot = max(scores)
        weights = [(x - pivot).exp() for x in scores]
        # Center before summation to resolve a posterior arbitrarily near the truth.
        error = sum(w * decimal(b - a) for w, b in zip(weights, brackets)) / sum(
            weights
        )
        bracket_kl.append(signed_kl(a, a + F(error)))
        if lag == 2:
            flexible = max(F(-1, 3), min(fit, F(1, 3)))
            adaptive.append((clipped[-1] + signed_kl(a, flexible)) / 2)
    always_large = bool(magnitude > cap)
    result = {
        "signed_agreement_count_sum": int(counts.sum()),
        "correct_oriented_likelihood_decisions": int(
            (known_large == always_large).sum()
        ),
        "correct_orientation_blind_likelihood_decisions": int(
            (large == always_large).sum()
        ),
        "correct_empirical_magnitude_decisions": int(
            ((np.abs(2 * counts - n) > float(cap) * (n + 1)) == always_large).sum()
        ),
        "population_kl_empirical_shift": float(sum(unpriced) / REPEATS),
        "population_kl_empirical_clipped": float(sum(clipped) / REPEATS),
        "population_kl_width_selected": float(sum(selected) / REPEATS),
        "population_kl_known_brackets_posterior_mean": format(
            sum(bracket_kl) / REPEATS, ".14E"
        ),
    }
    if adaptive:
        result["population_kl_empirical_adaptive_triangle"] = float(
            sum(adaptive) / REPEATS
        )
    return result


def audit():
    with localcontext() as context:
        context.prec = 75
        extras = [extra_component(lag) for lag in range(3, 7)]
        results = []
        for lag in (2, 3):
            cap = critical(lag)
            for j, delta in enumerate(MARGINS):
                bounds = analytic(lag, delta)
                rows = [
                    {
                        "n": n,
                        "exact_binomial_tail_tests": decision(
                            n, cap - delta, cap + delta
                        ),
                    }
                    for n in SIZES
                ]
                for side, magnitude in enumerate((cap - delta, cap + delta)):
                    seed = 2026112600 + 100 * lag + 10 * j + side
                    raw, orientations = raw_tapes(
                        np.random.default_rng(seed), lag, magnitude
                    )
                    for row in rows:
                        n = row["n"]
                        row["above" if side else "below"] = fits(
                            raw,
                            orientations,
                            lag,
                            n,
                            magnitude,
                            cap,
                            row["exact_binomial_tail_tests"],
                        )
                        row["raw_symbols_per_training_stream"] = n + lag
                        row["online_logical_bits_including_success_count"] = (
                            lag + n.bit_length()
                        )
                results.append({"bounds": bounds, "acquisition": rows})
        return {
            "registration": REGISTRATION,
            "repetitions_per_side": REPEATS,
            "orientation": "32 positive and 32 negative streams per side, shuffled before learning",
            "population_evaluation": "exact integration over a fresh stationary history and next token",
            "protected_capture_exact_checks": extras,
            "results": results,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    blob = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(blob.encode())
    else:
        print(blob, end="")
