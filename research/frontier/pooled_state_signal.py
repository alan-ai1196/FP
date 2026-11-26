"""Resolve training signal near a common stochastic reset with exact raw records."""

import argparse
import json
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

import numpy as np
import sympy as sp
from learn_state_width import INPUTS, score, walsh_fits
from stochastic_identities import contrast, identities
from transfer_dictionary import walsh

REGISTRATION = "8e162c2"
BETA = F(1, 2)
WITNESS = identities()[0]
UNITS = np.array([F(contrast(WITNESS, x), 4) for x in INPUTS])
EPSILONS = [F(1, 2**i) for i in range(1, 5)]


@lru_cache(None)
def log_gain(t, m):
    """Directed bounds for t atanh(m) + log(1-m*m)/2, in ordinary nats."""
    assert abs(m) < 1
    terms = 15
    value = sum(
        t * m ** (2 * j + 1) / (2 * j + 1) - m ** (2 * j + 2) / (2 * j + 2)
        for j in range(terms)
    )
    tail = (
        abs(t) * abs(m) ** (2 * terms + 1) / (2 * terms + 1)
        + m ** (2 * terms + 2) / (2 * terms + 2)
    ) / (1 - m * m)
    scale = 10**42
    return F((scale * (value - tail)) // 1, scale), F(
        -((-scale * (value + tail)) // 1), scale
    )


def gain(truth, forecasts, mass):
    bounds = [log_gain(t, m) for t, m in zip(truth, forecasts, strict=True)]
    lo, hi = (sum(p * z[j] for p, z in zip(mass, bounds, strict=True)) for j in (0, 1))
    assert hi - lo < F(1, 10**22)
    return float((lo + hi) / 2)


def states(reset, minus, plus):
    rows = []
    for x in INPUTS:
        z = reset.copy()
        for sign in x:
            z = z @ (plus if sign == 1 else minus)
        rows.append(z)
    return np.stack(rows)


def setup(name):
    uniform = np.array([F(1, 4)] * 4)
    e0 = np.array([F(1), F(0), F(0), F(0)])
    if name == "stationary":
        minus, plus = (2, 1, 1, 0), (3, 0, 1, 3)
        center = reset = np.array([F(i, 7) for i in (2, 2, 1, 2)])
    else:
        minus, plus = (1, 2, 3, 0), (3, 1, 0, 2)
        reset = e0
        center = e0 if name == "boundary" else uniform
    eye = np.eye(4, dtype=int)
    km, kp = [
        np.array([F(1) if v else F(0) for v in eye[list(p)].flat]).reshape(4, 4)
        for p in (minus, plus)
    ]
    if name == "boundary":
        km, kp = [(3 * k + uniform) / 4 for k in (km, kp)]
    return reset, center, km, kp


def terminal_profile(rows):
    mass = rows.sum(axis=0) / 64
    slope = UNITS @ rows / 64
    conditional = BETA * slope / mass
    fisher = sum(slope * slope / mass)
    return mass, slope, fisher, gain(conditional, conditional, mass)


def stationary_direction(rows, eps, mass, slope):
    centered = rows - mass
    gram = centered.T @ centered / 64
    # The last coordinate is minus the sum of the first three.
    reduced = sp.Matrix(gram[:3, :3])
    cov = sp.Matrix(slope[:3])
    squared = F((cov.T * reduced.inv() * cov)[0]) * BETA**2
    eigenvalues = np.linalg.eigvalsh(np.array(reduced, dtype=float))
    assert mass[0] == F(2, 7)
    rho = BETA * slope[0]
    v = gram[0, 0]
    assert v >= F(5, 98) * eps**4
    a = rho / v
    forecast = a * centered[:, 0]
    assert max(map(abs, forecast)) < 1
    attained = gain(BETA * UNITS, forecast, [F(1, 64)] * 64)
    upper = squared / (2 * (1 - BETA**2))
    assert 0 < attained <= float(upper)
    return {
        "centered_eigenvalues_normalized_small_to_large": (
            eigenvalues / np.array([float(eps**4), float(eps**4), float(eps**2)])
        ).tolist(),
        "scalar_head_gain_over_epsilon8": attained / float(eps**8),
        "unrestricted_affine_upper_over_epsilon8": float(upper / eps**8),
        "scalar_head_amplitude": str(a),
    }


def paired_gradients(rows, clean_contrast, eps, reset, mean_difference, dm, dp):
    # Flipping the first input interchanges the two 32-word halves.
    paired = (rows - np.roll(rows, 32, axis=0)) / (2 * eps**6)
    for x, actual in zip(INPUTS, paired, strict=True):
        expected = x[0] * (reset @ mean_difference)
        for sign in x[1:]:
            expected = expected @ (dp if sign == 1 else dm)
        assert np.array_equal(expected, actual)
    assert np.array_equal(UNITS @ paired / 64, clean_contrast)
    return paired


def audit_ray(name):
    reset, center, km, kp = setup(name)
    clean = states(reset, km, kp)
    clean_mass, clean_contrast, clean_fisher, clean_gain = terminal_profile(clean)
    col = np.array([F(-1), F(1), F(-1), F(1)])
    results = []
    for eps in EPSILONS:
        tm, tp = [(1 - eps) * center + eps * k for k in (km, kp)]
        assert min(tm.min(), tp.min()) > 0
        z = states(reset, tm, tp)
        mass, slope, fisher, sampled = terminal_profile(z)
        assert np.array_equal(slope, eps**6 * clean_contrast)
        paired = paired_gradients(
            z, clean_contrast, eps, reset, (kp - km) / 2, km - center, kp - center
        )
        variances = np.sum(paired * paired, axis=0) / 64 - (BETA * clean_contrast) ** 2
        expected_power = 11 if name == "boundary" else 12
        row = {
            "epsilon": str(eps),
            "sampled_gain": sampled,
            "sampled_gain_over_epsilon_power": sampled / float(eps**expected_power),
            "terminal_fisher": float(fisher),
            "sampled_positive_probability_fair_after_float32_rounding": int(
                np.count_nonzero(
                    np.array((1 + BETA * slope / mass) / 2, dtype=np.float32) == 0.5
                )
            ),
            "flag_and_terminal_gain": float(eps**6) * clean_gain,
            "flag_and_terminal_fisher": float(eps**6 * clean_fisher),
            "normalized_paired_gradient_variances": list(map(str, variances)),
        }
        # Directly condition on a refresh, marginalizing its first occurrence and all word signs.
        failed = (z - eps**6 * clean) / (1 - eps**6)
        assert min(failed.flat) >= 0 and np.all(UNITS @ failed == 0)
        if name == "permutations":
            assert np.array_equal(z, (1 - eps**6) * center + eps**6 * clean)
            rho = BETA * (clean_contrast @ col)
            assert rho == BETA / 8
            v = min(eps**6, rho)
            low = gain([rho], [v], [F(1)])
            upper = BETA * eps**6 / 8
            assert 0 < low <= float(upper)
            calibrated = BETA * clean_contrast / clean_mass
            intercept = center @ calibrated
            h = intercept + (calibrated - intercept) / eps**6
            assert np.array_equal(z @ h, clean @ calibrated)
            row.update(
                {
                    "bounded_mixture_gain_lower": low,
                    "bounded_mixture_gain_upper": float(upper),
                    "unrestricted_affine_exact_gain": clean_gain,
                    "largest_affine_coefficient": float(max(map(abs, h))),
                    "belief_separation": str(eps**6),
                }
            )
        if name == "stationary":
            row["affine"] = stationary_direction(z, eps, mass, slope)
        results.append(row)
    return {"clean_unit_contrast": list(map(str, clean_contrast)), "rows": results}


def score_heads(forecast, target, mass):
    # Stable per-state expected log gain near zero.
    gains = np.arctanh(forecast) * target + 0.5 * np.log1p(-(forecast**2))
    return gains @ mass.astype(float)


def observed_training():
    """Paired ordinary-record versus sampled endpoint calibration at the same deployment."""
    reset, center, km, kp = setup("permutations")
    clean = states(reset, km, kp)
    paired = (clean - np.roll(clean, 32, axis=0)) / 2
    n, trials = 4096, 64
    probs = np.concatenate((1 + BETA * UNITS, 1 - BETA * UNITS)).astype(float) / 128
    rng = np.random.default_rng(827362611)
    counts = rng.multinomial(n, probs, size=trials)
    plus, minus = counts[:, :64], counts[:, 64:]
    learned_raw, signed = walsh_fits(plus, minus, n)
    normalized = (plus - minus) @ paired.astype(float) / n
    all_raw_gain = score((BETA * UNITS).astype(float), learned_raw)
    exact_signed = np.sign(walsh(UNITS.astype(float)))
    result = []
    for eps in EPSILONS:
        z = (1 - eps**6) * center + eps**6 * clean
        mass, slope, _, best = terminal_profile(z)
        target = (BETA * slope / mass).astype(float)
        head = normalized * float(eps**6) / mass.astype(float)
        sampled_counts = np.zeros((trials, 2, 4), dtype=int)
        for i in range(64):
            sampled_counts[:, 0] += rng.multinomial(plus[:, i], z[i].astype(float))
            sampled_counts[:, 1] += rng.multinomial(minus[:, i], z[i].astype(float))
        sampled_head = (sampled_counts[:, 0] - sampled_counts[:, 1]) / (
            1 + sampled_counts.sum(1)
        )
        paired_gains = score_heads(head, target, mass)
        sampled_gains = score_heads(sampled_head, target, mass)
        result.append(
            {
                "epsilon": str(eps),
                "paired_positive": int((paired_gains > 0).sum()),
                "paired_mean_fraction_of_best": float(paired_gains.mean() / best),
                "sampled_positive": int((sampled_gains > 0).sum()),
                "sampled_mean_gain": float(sampled_gains.mean()),
            }
        )
    return {
        "training_records": n,
        "repetitions": trials,
        "raw_walsh_gain": float(all_raw_gain.mean()),
        "raw_walsh_exact_support": int(np.all(signed == exact_signed, axis=1).sum()),
        "rows": result,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "registration": REGISTRATION,
        "source_strength": str(BETA),
        "raw_fisher": str(sum(UNITS**2) / 64),
        "rays": {k: audit_ray(k) for k in ("permutations", "stationary", "boundary")},
        "training": observed_training(),
    }
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
