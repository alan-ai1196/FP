"""Learn and execute a two-state non-synchronizing predictive update from raw triples."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import ceil, isqrt
from pathlib import Path

import numpy as np
from audit_unifilar import exact_blocks, law
from symbol_refinement import WORDS, N, V, draw, raw_counts, sample_columns
from text import SCALE, ratio_log
from unifilar import Blocks, determinant, operators, ratios

REGISTRATION = "63f6f8f"


def window_blocks(hist):
    n = int(hist.sum())
    one = [F(int(v), 3 * n) for v in raw_counts(hist)]
    counts = hist.sum(axis=0) + hist.sum(axis=2)
    pair = [[F(int(v), 2 * n) for v in row] for row in counts]
    p, s = max(
        product(range(len(one)), repeat=2),
        key=lambda k: abs(pair[k[0]][k[1]] - one[k[0]] * one[k[1]]),
    )
    basis = [[F(1), one[s]], [one[p], pair[p][s]]]
    if not determinant(basis):
        return None
    blocks = [
        [[one[a], pair[a][s]], [pair[p][a], F(int(hist[p, a, s]), n)]]
        for a in range(len(one))
    ]
    return Blocks((p, s), basis, blocks, one[s])


def anchor(blocks):
    ops, _ = operators(blocks)
    matrices = [np.array(op, dtype=object) for op in ops]
    determinants = ratios(blocks)
    if 0 in determinants:
        return None
    flip = np.array([int(x < 0) for x in determinants], dtype=np.int32)
    candidates = [((a,), m) for a, m in enumerate(matrices) if not flip[a]]
    candidates.extend(
        ((a, b), matrices[a] @ matrices[b])
        for a, b in product(np.flatnonzero(flip).tolist(), repeat=2)
    )

    def gap(candidate):
        m = candidate[1]
        return m.trace() ** 2 - 4 * determinant(m)

    for word, m in sorted(candidates, key=gap, reverse=True):
        disc = gap((word, m))
        # The terminal vector is (1,0) in empty / one-letter suffix coordinates.
        if disc > 0 and m[1, 0]:
            return matrices, flip, word, m, disc
    return None


def norm_rows(a, floor):
    a = np.maximum(a, floor)
    return a / a.sum(axis=-1, keepdims=True)


def spectral(hist):
    n = int(hist.sum())
    blocks = window_blocks(hist)
    witness = anchor(blocks) if blocks else None
    floor = 1 / (2 * n)
    if witness is None:
        pooled = norm_rows(raw_counts(hist), floor)
        return (
            np.zeros(hist.shape[0], dtype=np.int32),
            np.tile(pooled, (2, 1)),
            np.full(2, 0.5),
            {"fallback": True},
        )
    ops, flip, word, mat, disc = witness
    m = np.asarray(mat, dtype=float)
    terminal = np.array([1.0, 0.0])
    displacement = (2 * m - m.trace() * np.eye(2)) @ terminal / np.sqrt(float(disc))
    transform = np.stack(
        [(terminal + displacement) / 2, (terminal - displacement) / 2], axis=1
    )
    emission = np.stack(
        [
            np.linalg.solve(transform, np.asarray(op, dtype=float) @ terminal)
            for op in ops
        ],
        axis=1,
    )
    initial = np.array([1.0, float(blocks.initial)]) @ transform
    stats = {
        "fallback": False,
        "prefix_suffix": list(blocks.anchor),
        "spectral_word": list(word),
        "eigenvalue_gap": round(float(np.sqrt(float(disc))), 12),
        "basis_condition": round(float(np.linalg.cond(transform)), 9),
        "positive_floor": floor,
        "floor_hits": int((emission < floor).sum() + (initial < floor).sum()),
        "determinant_signs": [int(np.sign(x)) for x in ratios(blocks)],
    }
    return flip, norm_rows(emission, floor), norm_rows(initial, floor), stats


def em(hist, flip, emission, initial):
    words = np.array(WORDS, dtype=int)
    counts = hist.ravel()
    paths = np.zeros((2, len(words), 3), dtype=int)
    paths[0, :, 1:] = np.bitwise_xor.accumulate(flip[words[:, :-1]], axis=1)
    paths[1] = 1 - paths[0]
    index = (V * paths + words).reshape(2, -1)
    costs = []
    for step in range(26):
        joint = initial[:, None] * emission[paths, words].prod(axis=-1)
        total = joint.sum(axis=0)
        prior = -0.5 * (np.log(initial).sum() + np.log(emission).sum())
        costs.append(float(-np.dot(counts, np.log(total)) + prior))
        if step == 25:
            break
        responsibility = counts * joint / total
        totals = np.full(2 * V, 0.5)
        for hidden in (0, 1):
            totals += np.bincount(
                index[hidden],
                weights=np.repeat(responsibility[hidden], 3),
                minlength=2 * V,
            )
        initial = norm_rows(responsibility.sum(axis=1) + 0.5, 0)
        emission = norm_rows(totals.reshape((2, V)), 0)
    assert max(np.diff(costs)) < 1e-8
    return emission, initial, [round(costs[0], 8), round(costs[-1], 8)]


def serialize(flip, emission, initial):
    mask = sum(int(v) << i for i, v in enumerate(flip))
    return (
        bytes([mask]) + np.asarray([initial[0], *emission.flat], dtype="<f8").tobytes()
    )


def scalar_forecast(tape, payload):
    params = np.frombuffer(payload, offset=1, dtype="<f8")
    e = params[1:].reshape(2, V)
    k = np.full(len(tape), np.log(params[0] / (1 - params[0])))
    sign = np.array([1 - 2 * ((payload[0] >> a) & 1) for a in range(V)])
    increment = np.log(e[0] / e[1])
    forecasts = np.empty(tape.shape)
    for j, token in enumerate(tape.T):
        p = np.exp(-np.logaddexp(0, -k))
        forecasts[:, j] = p * e[0, token] + (1 - p) * e[1, token]
        k = sign[token] * (k + increment[token])
    return forecasts


def categorical_forecast(tape, flip, e, pi):
    state = np.tile(pi[:, None], (1, len(tape)))
    forecasts = np.empty(tape.shape)
    for j, token in enumerate(tape.T):
        joint = state * e[:, token]
        mass = joint.sum(axis=0)
        forecasts[:, j] = mass
        state = np.where(flip[token], joint[::-1], joint) / mass
    return forecasts


def markov(tape, hist):
    table = 2 * hist + 1
    pair = table.sum(axis=2)
    first = pair.sum(axis=1)
    forecasts = np.empty(tape.shape)
    forecasts[:, 0] = first[tape[:, 0]] / first.sum()
    forecasts[:, 1] = pair[tape[:, 0], tape[:, 1]] / first[tape[:, 0]]
    for j in range(2, tape.shape[1]):
        u, v, w = tape[:, j - 2 : j + 1].T
        forecasts[:, j] = table[u, v, w] / pair[u, v]
    return forecasts


def score(prob):
    loss = -np.log(prob)
    return {
        name: round(float(loss[:, slice(lo, hi)].mean()), 9)
        for name, lo, hi in (
            ("all", 0, 64),
            ("1-3", 0, 3),
            ("4-16", 3, 16),
            ("17-64", 16, 64),
        )
    }


def exact_swap_case():
    # Both inputs swap. A separating eigenbasis exists only after composition.
    mats = [[[F(0), F(3, 4)], [F(1, 4), F(0)]], [[F(0), F(1, 4)], [F(3, 4), F(0)]]]
    blocks = exact_blocks((F(1, 2), F(1, 2)), mats)
    ops, flip, word, m, disc = anchor(blocks)
    assert tuple(flip) == (1, 1) and len(word) == 2
    root = F(isqrt(disc.numerator), isqrt(disc.denominator))
    assert root**2 == disc and root > 0
    identity = np.array([[F(1), F(0)], [F(0), F(1)]], dtype=object)
    contrast = (2 * m - m.trace() * identity) / root
    basis = np.stack(
        ((identity + contrast)[:, 0] / 2, (identity - contrast)[:, 0] / 2), axis=1
    )
    a, b = basis[0]
    c, d = basis[1]
    inverse = np.array([[d, -b], [-c, a]], dtype=object) / determinant(basis)
    restored = [inverse @ op @ basis for op in ops]
    assert any(
        all(
            np.array_equal(observed, np.array(target)[np.ix_(order, order)])
            for observed, target in zip(restored, mats, strict=True)
        )
        for order in ([0, 1], [1, 0])
    )
    return {
        "separating_word": list(word),
        "eigenvalue_gap": str(root),
        "reconstructed_exactly": True,
    }


def reconstruct_moments(probability, k):
    mu = [probability((a,)) for a in range(k)]
    diagonal = [probability((a, a)) - p * p for a, p in enumerate(mu)]
    x = max(range(k), key=lambda a: abs(diagonal[a]))
    cov = diagonal[x]
    differences = []
    actions = []
    products = []
    for a in range(k):
        xa, ax = probability((x, a)), probability((a, x))
        determinant_ratio = (mu[a] * probability((x, a, x)) - xa * ax) / cov
        actions.append(int(determinant_ratio < 0))
        products.append(abs(determinant_ratio))
        differences.append((xa - mu[x] * mu[a]) / cov)
    indices = (
        next(i for i, v in enumerate(differences) if v > 0),
        next(i for i, v in enumerate(differences) if v < 0),
    )
    (a, b), (c, d) = [(mu[i] * differences[i], -(differences[i] ** 2)) for i in indices]
    h, j = [products[i] - mu[i] ** 2 for i in indices]
    det = a * d - b * c
    z, w = (h * d - b * j) / det, (a * j - c * h) / det
    squared = z * z + 4 * w
    # These audit sources have rational emissions. The theorem allows a real square root.
    delta = F(isqrt(squared.numerator), isqrt(squared.denominator))
    assert delta * delta == squared and delta > 0
    p = (1 - z / delta) / 2
    emission = [
        [m + factor * g / 2 for m, g in zip(mu, differences, strict=True)]
        for factor in (z + delta, z - delta)
    ]
    return actions, p, emission


def moment_audit():
    checked = 0
    for k in range(2, 6):
        for flips in product(range(2), repeat=k):
            for j in range(8):
                rows = [
                    [(a + 1) * (j + 1) + 1 for a in range(k)],
                    [(k - a) * (j + 2) + 1 for a in range(k)],
                ]
                rates = [[F(v, sum(row)) for v in row] for row in rows]
                moving = [sum(row[a] for a in range(k) if flips[a]) for row in rates]
                p = moving[1] / sum(moving) if any(flips) else F(j + 1, j + 3)
                matrices = [
                    [
                        [rates[i][a] if to == i ^ flips[a] else F(0) for to in (0, 1)]
                        for i in (0, 1)
                    ]
                    for a in range(k)
                ]

                def probability(word, initial=(p, 1 - p), ops=matrices):
                    return law(word, initial, ops)

                actions, estimated, emissions = reconstruct_moments(probability, k)
                assert tuple(actions) == flips
                assert (estimated, emissions) in ((p, rates), (1 - p, rates[::-1]))
                checked += 1
    return checked


def population_kl_upper(learned, initial, truth):
    # Interpret the serialized binary64 masses as exact rationals and normalize.
    fitted = [[F(float(v)) for v in row] for row in learned]
    totals = [sum(row) for row in fitted]
    fitted = [
        [v / total for v in row] for row, total in zip(fitted, totals, strict=True)
    ]
    pi0 = F(float(initial[0]))
    pi = (pi0, 1 - pi0)

    def upper_row(target, candidate):
        bound = F()
        for value, estimate in zip(target, candidate, strict=True):
            q = F(float(value))
            ratio = q / estimate
            bound += q * ratio_log(ratio.numerator, ratio.denominator)[1]
        return bound

    start = upper_row((0.5, 0.5), pi)
    emission = min(
        sum(upper_row(truth[i], fitted[order[i]]) for i in (0, 1)) / 2
        for order in ((0, 1), (1, 0))
    )

    def upper_nats(scaled):
        return ceil(scaled * 10**12 / SCALE) / 10**12

    return {
        "initial_kl_upper": upper_nats(start),
        "stationary_emission_kl_upper": upper_nats(emission),
        "per_token_at_64_upper": upper_nats(emission + start / 64),
        "maximum_row_normalization_error": float(max(abs(t - 1) for t in totals)),
    }


def experiment():
    hist = draw(N, 2026112303)
    flip, emission, initial, stats = spectral(hist)
    emission, initial, loss = em(hist, flip, emission, initial)
    payload = serialize(flip, emission, initial)
    tape = np.stack(list(sample_columns(4096, 64, 2026112304)), axis=1)
    learned = scalar_forecast(tape, payload)
    conventional = categorical_forecast(tape, flip, emission, initial)
    diff = float(np.abs(learned - conventional).max())
    assert diff < 1e-12
    rates = np.array([[3, 1, 1, 1, 1, 1], [1, 1, 1, 3, 1, 1]]) / 8
    true_flip = np.array([0, 0, 1, 0, 0, 1])
    oracle = categorical_forecast(tape, true_flip, rates, np.full(2, 0.5))
    raw = markov(tape, hist)
    uni = (raw_counts(hist) + 0.5) / (3 * N + 0.5 * V)
    results = {
        name: score(y)
        for name, y in (
            ("learned", learned),
            ("categorical", conventional),
            ("raw_order_two", raw),
            ("unigram", uni[tape]),
            ("known_source", oracle),
        )
    }
    correct = bool(np.array_equal(flip, true_flip))
    return {
        "registration": REGISTRATION,
        "training_windows": N,
        "training_tokens": 3 * N,
        "report_episodes": len(tape),
        "report_tokens": int(tape.size),
        "statistics": stats,
        "em_steps": 25,
        "penalized_training_nll": loss,
        "flip": flip.tolist(),
        "emissions": emission.round(12).tolist(),
        "initial": initial.round(12).tolist(),
        "expected_loss_certificate": population_kl_upper(emission, initial, rates)
        if correct
        else None,
        "packed_bytes": len(payload),
        "scalar_state_bytes": 8,
        "raw_order_two_count_bytes": 4 * V**3,
        "max_observed_probability_difference_below_1e_12": diff < 1e-12,
        "nll": results,
        "exact_all_swapping": exact_swap_case(),
        "registered_success": correct
        and all(
            results["learned"][k] < results["raw_order_two"][k]
            for k in ("all", "17-64")
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--moment-audit", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    if args.moment_audit:
        print("exact reconstructions up to hidden-state naming", moment_audit())
        raise SystemExit(0)
    result = experiment()
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf-8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
