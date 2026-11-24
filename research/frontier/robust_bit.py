"""Learn a private one-bit cue memory from ordinary data in several observed sources."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations, pairwise, product
from math import log
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

REGISTRATION = "91849de"
SIZES = (4096, 65536, 1048576)
SEEDS = (117, 503, 991)
LATTICE, PRECISION = 256, 65536


def models(m):
    rng = np.random.default_rng([25252026, m])
    order = rng.permutation(m + 1)
    environments = rng.permutation(m)
    p = np.full((m, m + 1), 0.5)
    for e, i in enumerate(environments):
        p[e, order[i]] -= 0.25
        p[e, order[i + 1]] += 0.25
    return p, order


def learn(counts):
    # Counts indexed by source, cue, and observed next bit. No source law enters.
    m, h, _ = counts.shape
    n = counts.sum(axis=(1, 2))
    signed = (counts[:, :, 1].astype(float) - counts[:, :, 0]) / (2 * n[:, None])
    bounds = [(-1, 1)] * h + [(-0.5, 0.5)]
    fit = linprog(
        np.r_[np.zeros(h), -1],
        A_ub=np.column_stack((-signed, np.ones(m))),
        b_ub=np.zeros(m),
        bounds=bounds,
        method="highs",
    )
    if not fit.success:
        raise ArithmeticError(fit.message)
    beta = np.rint((fit.x[:h] + 1) * (LATTICE / 2)).astype(int)
    empirical = float(np.min(signed @ (2 * beta / LATTICE - 1)))
    radius = float(np.sqrt((h * log(2) + log(27 * m / 0.05)) / (2 * min(n))))
    safe = max(0, empirical - radius)
    upper = min(PRECISION - 1, int(np.floor(PRECISION * (0.5 + safe))))
    if upper == PRECISION // 2:
        return b"", empirical, radius, 0.0
    p = upper / PRECISION
    lower = agreement_gain(0.5 + safe, p)
    # The known cue alphabet is contiguous from 0. Its size is in the header.
    word = bytes((1, h)) + np.array([upper, *beta], dtype="<u2").tobytes()
    return word, empirical, radius, float(lower)


def decode(word, h):
    if not word:
        return np.zeros(h), 0.5
    if word[:2] != bytes((1, h)) or len(word) != 4 + 2 * h:
        raise ValueError("invalid binary encoder packet")
    fields = np.frombuffer(word, offset=2, dtype="<u2")
    if not (PRECISION // 2 < fields[0] < PRECISION) or np.any(fields[1:] > LATTICE):
        raise ValueError("out-of-range bit encoder")
    return fields[1:] / LATTICE, fields[0] / PRECISION


def agreement_gain(agreement, readout):
    return agreement * np.log(2 * readout) + (1 - agreement) * np.log(2 * (1 - readout))


def pooled_rule(counts):
    pooled = counts.sum(axis=0)
    h = len(pooled)
    total = pooled.sum()
    best = (float("inf"), None)
    # Complements tie after exchanging the two messages.
    for v in product(range(2), repeat=h - 1):
        mask = np.array((0, *v), dtype=bool)
        table = np.array([pooled[~mask].sum(axis=0), pooled[mask].sum(axis=0)])
        p = (table[:, 1] + 1) / (table.sum(axis=1) + 2)
        nll = float(-(table[:, 1] @ np.log(p) + table[:, 0] @ np.log1p(-p)) / total)
        if nll < best[0]:
            best = nll, p[mask.astype(int)]
    return best[1]


def fair_bits(beta):
    """Minimal mean prefix bits for each Q8 Bernoulli write using fresh fair coins."""
    from math import gcd

    denominators = [LATTICE // gcd(round(LATTICE * x), LATTICE) for x in beta]
    return float(np.mean([2 * (1 - 1 / d) for d in denominators]))


def reports(p, beta, upper):
    # Per-source exact expectation of scoring the probability conditional on the bit.
    agreement = (p * beta + (1 - p) * (1 - beta)).mean(axis=1)
    gain = agreement_gain(agreement, upper)
    averaged = (1 - upper) + (2 * upper - 1) * beta
    held_cue = agreement_gain(p, averaged).mean(axis=1)
    return gain, held_cue


def replay(p, beta, upper, seed):
    m, h = p.shape
    obs = []
    for e in range(m):
        n = 32768
        rng = np.random.default_rng([seed, m, 252521, e])
        cues = rng.integers(h, size=n)
        y = rng.random(n) < p[e, cues]
        # One independent uniform byte per write, even when a table entry is deterministic.
        writer = rng.integers(0, LATTICE, n, dtype=np.uint8)
        bit = writer < np.rint(LATTICE * beta[cues]).astype(np.uint16)
        agreement = float(np.mean(bit == y))
        obs.append(float(agreement_gain(agreement, upper)))
    return obs


def exact_garblings():
    verified = improving = 0
    for m in (2, 3, 4):
        for encoder in product((F(0), F(1, 4), F(1, 2), F(3, 4), F(1)), repeat=m + 1):
            w = sum(encoder) / (m + 1)
            step = min(b - a for a, b in pairwise(encoder))
            if step > 0:
                improving += 1
                ratio = m * step
                f0, f1 = w - ratio / 2, w + ratio / 2
                assert 0 <= f0 < f1 <= 1 and (f0 + f1) / 2 == w
                c_star = F(1, 4 * m * (m + 1))
                # P(Y=1,B=1) in the garbled law and in the worse adjacent source.
                joint = f0 * (F(1, 4) - c_star) + f1 * (F(1, 4) + c_star)
                assert joint == w / 2 + step * F(1, 4 * (m + 1))
            verified += 1
    return {"exact_grid_encoders": verified, "positive_oriented_encoders": improving}


def clocks():
    """Enumerate every deterministic homogeneous update through four states."""
    results = {}
    for modulus in range(2, 10):
        first = None
        checked = 0
        for size in range(1, 5):
            feasible = False
            for transition in product(range(size), repeat=size):
                for reset in range(size):
                    constraints = set()
                    seen = set()
                    state = reset
                    while state not in seen:
                        seen.add(state)
                        constraints.add((state, transition[state]))
                        for _ in range(modulus):
                            state = transition[state]
                    # Strictly increasing reader logits require an acyclic order.
                    remaining = set(constraints)
                    while remaining:
                        tops = {a for a, _ in remaining} - {b for _, b in remaining}
                        if not tops:
                            break
                        remaining = {(a, b) for a, b in remaining if a not in tops}
                    feasible |= not remaining
                    checked += 1
            if feasible and first is None:
                first = size
        prime = next(d for d in range(2, modulus + 1) if modulus % d == 0)
        assert first == (prime if prime <= 4 else None)
        results[str(modulus)] = {
            "first_feasible_up_to_four": first,
            "proved_minimum": prime,
            "maps_and_resets": checked,
        }
    return results


def finite_prices():
    def bit_info(w, c):
        if not c:
            return 0.0
        high, low = 0.5 + c / w, 0.5 - c / (1 - w)
        return w * agreement_gain(high, high) + (1 - w) * agreement_gain(low, low)

    checked = 0
    for m, bits in product(range(2, 6), range(1, 5)):
        levels = 2**bits
        best = 0.0
        for enc in combinations(range(levels + 1), m + 1):
            w = sum(enc) / ((m + 1) * levels)
            step = min(b - a for a, b in pairwise(enc)) / levels
            best = max(best, bit_info(w, step / (4 * (m + 1))))
            checked += 1
        r = m * (levels // m) / levels
        predicted = bit_info(r / 2, r / (4 * m * (m + 1)))
        assert abs(best - predicted) < 1e-13

    windows = []
    eps = 0.25
    for size in (2, 4, 8, 16, 64):
        n = 3 * (size - 1)
        a = n / (n + 1)
        d = eps * (1 - a) / (1 + a)
        transient = a**n * (1 + a) * agreement_gain(0.5 + d, 0.5 + d) / 2
        lower = eps**2 / (np.e * (2 * n + 1) ** 2)
        upper = 2 * eps**2 * (4 / (n + 2) ** 2 + 1 / (n * (n + 1)))
        max_at_last = 0.0
        for x, y in product(np.linspace(0, 1, 9), repeat=2):
            if x + y > 1:  # Negative eigenvalues have alternating tangents.
                continue
            P = np.array([[1 - x, x], [y, 1 - y]])
            short = np.linalg.matrix_power(P, n)
            long = short @ P
            for u, v in zip(short, long):
                w = (u[1] + v[1]) / 2
                c = eps * (v[1] - u[1]) / 2
                max_at_last = max(max_at_last, bit_info(w, c))
        assert lower <= transient <= upper and max_at_last <= upper + 1e-14
        windows.append(
            {
                "last_length": n,
                "proved_lower": lower,
                "transient_gain": transient,
                "proved_upper": upper,
                "largest_last_environment_grid_oracle": max_at_last,
            }
        )
    return {"strict_grid_encoders": checked, "two_state_odd_windows": windows}


def run():
    rows = []
    for m in (2, 4, 8):
        p, order = models(m)
        joint = np.stack([1 - p, p], axis=-1) / (m + 1)
        distance = 0.5 / (m * (m + 1))
        optimum = float(agreement_gain(0.5 + distance, 0.5 + distance))
        ideal_beta = np.empty(m + 1)
        ideal_beta[order] = np.arange(m + 1) / m
        ideal_gain, _ = reports(p, ideal_beta, 0.5 + distance)
        np.testing.assert_allclose(ideal_gain, optimum, atol=1e-15)
        for n in SIZES:
            for seed in SEEDS:
                rng = np.random.default_rng([seed, m, n])
                counts = np.array(
                    [rng.multinomial(n, law.ravel()).reshape(m + 1, 2) for law in joint]
                )
                word, empirical, radius, lower = learn(counts)
                beta, upper = decode(word, m + 1)
                robust, cue = reports(p, beta, upper)
                pool = agreement_gain(p, pooled_rule(counts)).mean(axis=1)
                item = {
                    "m": m,
                    "pairs_per_source": n,
                    "seed": seed,
                    "packet_hex": word.hex(),
                    "empirical_rounded_margin": empirical,
                    "margin_radius": radius,
                    "certified_worst_source_gain": lower,
                    "optimal_private_bit_gain": optimum,
                    "source_gains": robust.tolist(),
                    "pooled_deterministic_source_gains": pool.tolist(),
                    "held_cue_source_gains": cue.tolist(),
                    "ordered_write_probabilities": beta[order].tolist(),
                    "mean_exact_sampler_coin_bits": fair_bits(beta),
                    "carried_bits": int(bool(word)),
                }
                if n == max(SIZES):
                    item["fresh_32768_sample_gain_per_word"] = replay(
                        p, beta, upper, seed
                    )
                rows.append(item)
    return {
        "registration": REGISTRATION,
        "exact_check": exact_garblings(),
        "posthoc_unary_clock_check": clocks(),
        "posthoc_precision_and_window_checks": finite_prices(),
        "fits": rows,
    }


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    dest = p.add_mutually_exclusive_group(required=True)
    dest.add_argument("--write", type=Path)
    dest.add_argument("--check", type=Path)
    a = p.parse_args()
    result = run()
    if a.check:
        assert compare(result, json.loads(a.check.read_text(encoding="utf8")))
    else:
        a.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(
        "Checked exact garblings, finite-sample acquisition, and all independent source outcomes."
    )
