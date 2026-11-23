"""Finite audits for transcript KL, state budgets and universal Bernoulli predictions."""

import argparse
import json
from fractions import Fraction
from functools import cache
from itertools import combinations_with_replacement, product
from math import comb, fsum, inf, log
from pathlib import Path

import numpy as np
from scipy.special import betaln, entr, expit, rel_entr
from scipy.stats import binom

P = 0.75
PRIORS = (Fraction(1, 2),) * 2
ROWS = ((Fraction(0), Fraction(1, 2)), (Fraction(1, 2), Fraction(0)))
HORIZONS = (16, 64, 1024, 65536)


def kl(p, q):
    return float(rel_entr(p, q) + rel_entr(1 - p, 1 - q))


def entropy(p):
    return float(entr(p) + entr(1 - p))


@cache
def passive(prior, p0, p1, horizon):
    """Count is sufficient for the path likelihood ratio and the posterior."""
    k = np.arange(horizon + 1)
    q = (1 - prior) * p0 + prior * p1
    left = np.log1p(-prior) + binom.logpmf(k, horizon, p0) if prior < 1 else -np.inf
    right = np.log(prior) + binom.logpmf(k, horizon, p1) if prior else -np.inf
    joint = np.logaddexp(left, right)
    possible = np.isfinite(joint)
    weights = np.exp(joint[possible])
    reference = binom.logpmf(k[possible], horizon, q)
    direct = float(weights @ (joint[possible] - reference))
    posterior = np.exp(np.broadcast_to(right, joint.shape)[possible] - joint[possible])
    posterior = np.clip(posterior, 0, 1)
    info = entropy(prior) - float(weights @ (entr(posterior) + entr(1 - posterior)))
    slope = entropy(q) - (1 - prior) * entropy(p0) - prior * entropy(p1)
    assert np.isclose(direct, horizon * slope - info, atol=2e-9, rtol=4e-10)
    if p0 == p1 or prior in (0, 1):
        assert abs(direct) + abs(info) < 1e-10
        return 0.0, 0.0, 0.0
    if horizon == 1:
        assert abs(direct) + abs(info - slope) < 1e-10
        return 0.0, slope, slope
    return direct, info, slope


def universal(horizon):
    """Expected KL of a half-count learner against a persistent fair mixture."""
    k = np.arange(horizon + 1)
    counts = (binom.pmf(k, horizon, P) + binom.pmf(k, horizon, 1 - P)) / 2
    high = k * log(P) + (horizon - k) * log(1 - P)
    law = np.logaddexp(high, high[::-1]) - log(2)
    reference = betaln(k + 0.5, horizon - k + 0.5) - betaln(0.5, 0.5)
    return float(counts @ (law - reference))


def child(belief, action, y):
    joint = tuple(
        b * (row[action] if y else 1 - row[action]) for b, row in zip(belief, ROWS)
    )
    prob = sum(joint)
    return prob, tuple(x / prob for x in joint) if prob else belief


def controlled(q):
    """Bellman recursion and a separate enumeration of transcript likelihoods."""

    @cache
    def optimal(belief, horizon):
        if not horizon:
            return 0.0
        values = []
        for a in (0, 1):
            branches = [child(belief, a, y) for y in (0, 1)]
            values.append(
                kl(float(branches[1][0]), float(q))
                + fsum(float(m) * optimal(b, horizon - 1) for m, b in branches if m)
            )
        return max(values)

    def paths(plan):
        transcript, oracle, info = [], [], []

        def visit(index, depth, row_mass, reference):
            mixture = sum(row_mass)
            if not mixture:
                return
            if depth == 3:
                transcript.append(float(mixture) * log(mixture / reference))
                for z, mass in enumerate(row_mass):
                    if mass:
                        oracle.append(float(mass) * log(mass / (PRIORS[z] * reference)))
                        info.append(float(mass) * log(mass / (PRIORS[z] * mixture)))
                return
            a = plan[index]
            for y in (0, 1):
                next_mass = tuple(
                    m * (row[a] if y else 1 - row[a]) for m, row in zip(row_mass, ROWS)
                )
                visit(
                    2 * index + 1 + y,
                    depth + 1,
                    next_mass,
                    reference * (q if y else 1 - q),
                )

        visit(0, 0, PRIORS, Fraction(1))
        assert abs(fsum(transcript) - (fsum(oracle) - fsum(info))) < 1e-13
        return fsum(transcript)

    exhaustive = max(paths(plan) for plan in product((0, 1), repeat=7))
    assert abs(exhaustive - optimal(PRIORS, 3)) < 1e-13
    assert np.isclose(0.6 * 0 + 0.4 * 0.5, 0.2)
    rates = [kl(p, float(q)) for p in (0.0, 0.5)]
    if q == Fraction(1, 5):
        assert np.allclose(rates, log(5 / 4), rtol=0, atol=1e-15)
    return {
        "q": str(q),
        "nonadaptive_rate": sum(rates) / 2,
        "adaptive_rate": max(rates),
        "three_step_exhaustive": exhaustive,
        "optimal_by_horizon": {str(t): optimal(PRIORS, t) for t in (1, 2, 3, 8, 32)},
    }


def best_automata(size):
    """Minimize the horizon-averaged KL exactly over readouts for each graph."""
    best = {h: (inf, None, None) for h in HORIZONS}
    total = size ** (2 * size)
    oracle_info = {t: passive(0.5, 1 - P, P, t)[1] for t in HORIZONS}
    base = size ** np.arange(2 * size)
    for start in range(0, total, 512):
        ids = np.arange(start, min(start + 512, total))
        graph = ((ids[:, None] // base) % size).reshape(-1, size, 2)
        matrices = []
        index = np.arange(len(ids))[:, None]
        for p in (1 - P, P):
            step = np.zeros((len(ids), size, size))
            for y, chance in enumerate((1 - p, p)):
                step[index, np.arange(size), graph[:, :, y]] += chance
            matrices.append(step)
        powers = np.array(matrices)
        sums = np.broadcast_to(np.eye(size), powers.shape).copy()
        t = 1
        while t <= max(HORIZONS):
            if t in best:
                counts = sums[:, :, 0, :]
                assert np.allclose(counts.sum(axis=-1), t, rtol=2e-11)
                weights = counts.sum(axis=0)
                q = np.divide(
                    (1 - P) * counts[0] + P * counts[1],
                    weights,
                    out=np.full_like(weights, 0.5),
                    where=weights > 0,
                )
                regret = np.zeros(len(ids))
                for c, p in zip(counts, (1 - P, P)):
                    regret += (c * (rel_entr(p, q) + rel_entr(1 - p, 1 - q))).sum(
                        axis=-1
                    ) / 2
                divergence = regret - oracle_info[t]
                lower = max(
                    0,
                    (t - size + 1) * (1 - P) ** (size - 1) * (log(2) - entropy(P))
                    - log(2),
                )
                assert np.all(divergence > lower - 1e-7)
                i = int(np.argmin(divergence))
                value = float(divergence[i])
                if value < best[t][0] - 1e-9:
                    best[t] = value, graph[i].tolist(), q[i].tolist()
            if t == max(HORIZONS):
                break
            sums += powers @ sums
            powers = powers @ powers
            t *= 2
    return {
        "size": size,
        "graphs": total,
        "best": {
            str(t): {"divergence": loss, "graph": graph, "readout": q}
            for t, (loss, graph, q) in best.items()
        },
    }


def stopped_counter(limit, horizon, central=None, bits=8):
    """Compute exact-expectation state occupancies by powering its transition matrix."""
    s = np.arange(-limit, limit + 1)
    posterior = expit(s * log(P / (1 - P)))
    forecast = 1 - P + (2 * P - 1) * posterior
    if central is not None:
        levels = 2**bits
        forecast = np.where(
            np.abs(s) <= central,
            np.round(forecast * levels) / levels,
            np.where(s > 0, P, 1 - P),
        )
    forecast[[0, -1]] = [1 - P, P]
    excess = 0.0
    for p in (1 - P, P):
        matrix = np.eye(len(s))
        for i in range(1, len(s) - 1):
            matrix[i] = 0
            matrix[i, i - 1], matrix[i, i + 1] = 1 - p, p
        base = np.zeros((len(s) + 1, len(s) + 1))
        base[:-1, :-1] = matrix
        base[:-1, -1] = rel_entr(p, forecast) + rel_entr(1 - p, 1 - forecast)
        base[-1, -1] = 1.0
        excess += np.linalg.matrix_power(base, horizon)[limit, -1] / 2
    value = float(excess - passive(0.5, 1 - P, P, horizon)[1])
    exact_bound = horizon * kl(P, 1 - P) / (1 + (P / (1 - P)) ** limit)
    if central is None:
        assert -1e-9 < value < exact_bound + 1e-8
    return value


def path_checks():
    """Independent rational path probabilities for a stopped counter and passive mixtures."""
    checked = 0
    for horizon in range(1, 10):
        mix_div = []
        counter_div = []
        for path in product((0, 1), repeat=horizon):
            k = sum(path)
            w = Fraction(3**k + 3 ** (horizon - k), 2 * 4**horizon)
            mix_div.append(float(w) * log(w * 2**horizon))
            state = 0
            mass = Fraction(1)
            for y in path:
                if abs(state) == 2:
                    q = Fraction(3 if state > 0 else 1, 4)
                else:
                    odds = Fraction(3) ** state
                    q = (3 * odds + 1) / (4 * (1 + odds))
                mass *= q if y else 1 - q
                if abs(state) < 2:
                    state += 2 * y - 1
            counter_div.append(float(w) * log(w / mass))
            checked += 1
        assert abs(fsum(mix_div) - passive(0.5, 1 - P, P, horizon)[0]) < 1e-12
        assert abs(fsum(counter_div) - stopped_counter(2, horizon)) < 1e-12
    return checked


def kt_checks():
    """Test the exact worst-path likelihood ratio of the half-count predictor."""
    b = [Fraction(4**n, comb(2 * n, n)) for n in range(65)]
    count = 0
    for n, envelope in enumerate(b):
        ratios = []
        for k in range(n + 1):
            ml = (
                Fraction(k, n) ** k * Fraction(n - k, n) ** (n - k)
                if n
                else Fraction(1)
            )
            kt = Fraction(comb(2 * k, k) * comb(2 * (n - k), n - k), 4**n * comb(n, k))
            ratios.append(ml / kt)
            count += 1
        assert max(ratios) == envelope
    for t in range(33):
        candidates = [
            b[a] * b[c] * b[t - a - c]
            for a, c in combinations_with_replacement(range(t + 1), 2)
            if a + c <= t
        ]
        q, r = divmod(t, 3)
        assert max(candidates) == b[q] ** (3 - r) * b[q + 1] ** r
    return count


def run():
    passive_cases = {}
    for w, p0, p1 in (
        (0.5, 0.25, 0.75),
        (0.001, 0.25, 0.75),
        (0.5, 0.0, 1.0),
        (0.5, 0.45, 0.45),
        (0.0, 0.25, 0.75),
        (1.0, 0.0, 1.0),
    ):
        values = [passive(w, p0, p1, t)[0] for t in range(34)]
        assert max(-np.diff(values, n=2)) < 1e-11
        passive_cases[f"{w:g},{p0:g},{p1:g}"] = {
            str(t): passive(w, p0, p1, t)[0] for t in (1, 2, 8, 64, 1024)
        }
    return {
        "unit": "total expected transcript KL in nats; sampled latent row persists throughout",
        "passive": passive_cases,
        "controlled": [controlled(q) for q in (Fraction(1, 4), Fraction(1, 5))],
        "three_step_policy_trees_per_reference": 128,
        "rational_passive_and_counter_paths": path_checks(),
        "kt_count_types_checked": kt_checks(),
        "fair_quarter_coins_half_count": {str(t): universal(t) for t in HORIZONS},
        "automata": [best_automata(size) for size in range(1, 5)],
        "fair_quarter_coins_stopped_counter": {
            str(t): {
                str(l): {
                    "exact_interior": stopped_counter(l, t),
                    "three_central_states_Q8": stopped_counter(l, t, 1),
                }
                for l in (1, 2, 4, 8, 12)
            }
            for t in HORIZONS
        },
    }


def compare(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(compare(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(compare(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return np.isclose(a, b, atol=1e-8, rtol=1e-10)
    return a == b


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched the finite study.")
    elif args.output:
        args.output.write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf8"
        )
    else:
        print(json.dumps(result, indent=2, allow_nan=False))
