"""Learning and retaining an unknown balanced distinction from ordinary pairs."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations
from math import comb, log, log1p, prod
from pathlib import Path

import numpy as np

REGISTRATION = "0566b90"
KAPPA = 0.5


def representatives(d):
    # Fix the first sign at +1 because simultaneous sign reversal has no effect.
    labels = []
    for rest in combinations(range(1, d), d // 2 - 1):
        s = -np.ones(d, np.int64)
        s[0] = 1
        s[list(rest)] = 1
        labels.append(s)
    return np.array(labels)


def conditional_gain(correlation):
    ratio = 1 + KAPPA * correlation
    return float(np.mean(ratio * np.log1p(KAPPA * correlation)))


def oracle_gain():
    return ((1 + KAPPA) * log1p(KAPPA) + (1 - KAPPA) * log1p(-KAPPA)) / 2


def equality_gain(d):
    corr = np.full((d, d), -1 / (d - 1))
    np.fill_diagonal(corr, 1)
    return conditional_gain(corr)


def message_value(members):
    return conditional_gain(members.T @ members / len(members))


def exact_message_factor(members):
    # The logarithm of this rational is the cell contribution to 2*k*d²*gain.
    size = len(members)
    masses, counts = np.unique(2 * size + members.T @ members, return_counts=True)
    return prod(F(int(w), 2 * size) ** int(w * n) for w, n in zip(masses, counts))


def second_moment(d, n):
    half = d // 2
    return sum(
        F(comb(half, j) ** 2, comb(d, half)) * (1 + F((4 * j - d) ** 2, 4 * d * d)) ** n
        for j in range(half + 1)
    )


def histories(scaled, d):
    # Exact integer likelihood numerators, followed by floating-point logs.
    # Columns are all possible tapes of n ordered raw pairs.
    k, cells = scaled.shape
    joint = np.ones((k, 1), dtype=np.int64)
    divergences = [0.0]
    for n in range(1, 4):
        joint = (joint[:, :, None] * scaled[:, None, :]).reshape(k, -1)
        likelihood = joint.sum(axis=0) / (k * 2**n)
        assert abs(likelihood.mean() - 1) < 1e-14
        divergences.append(float(np.mean(likelihood * np.log(likelihood))))
    gains = np.diff(divergences)
    assert cells == d * d and abs(gains[0] - equality_gain(d)) < 2e-14
    assert np.min(np.diff(gains)) > 0
    return gains.tolist()


def finite(d):
    labels = representatives(d)
    k = len(labels)
    # Twice the likelihood ratio is exactly integral at contrast 1/2.
    scaled = (2 + labels[:, :, None] * labels[:, None, :]).reshape(k, d * d)
    sums = scaled.sum(axis=0)
    gram = scaled.T @ scaled
    direct = [
        F(int(sums @ sums), (2 * k) ** 2 * d * d),
        F(int((gram * gram).sum()), (4 * k) ** 2 * d**4),
    ]
    assert direct == [second_moment(d, n) for n in (1, 2)]
    # The zero-training equality predictor treats diagonal and off-diagonal
    # cells differently. Verify its two-pair second moment with rational sums.
    centered = F(0)
    for left in np.unique(sums):
        for right in np.unique(sums):
            entries = gram[np.ix_(sums == left, sums == right)]
            centered += F(
                int((entries * entries).sum()), 4 * d**4 * int(left) * int(right)
            )
    alpha = F(d - 1, 2 * (2 * d - 3))
    half = d // 2
    predicted = sum(
        F(comb(half, j) ** 2, comb(d, half))
        * (1 + alpha * (F((4 * j - d) ** 2, d * d) - F(1, d - 1))) ** 2
        for j in range(half + 1)
    )
    assert centered == predicted
    tags = np.zeros(k, np.int64)
    gains = []
    for b in range(d):
        if b:
            tags = 2 * tags + (labels[:, b] == 1)
        value = 0.0
        for tag in np.unique(tags):
            subset = labels[tags == tag]
            value += len(subset) * message_value(subset) / k
        gains.append(value)
    assert abs(gains[0] - equality_gain(d)) < 2e-15
    assert abs(gains[-1] - oracle_gain()) < 2e-15
    assert np.min(np.diff(gains)) >= -1e-14
    result = {
        "distinct_unlabelled_assignments": k,
        "direct_second_moments": [str(v) for v in direct],
        "two_pair_second_moment_relative_to_equality": str(centered),
        "relative_sign_code_gains": gains,
    }
    if d <= 6:
        result["bayes_gain_after_zero_one_two_pairs"] = histories(scaled, d)
        best = F(0)
        ties = 0
        # Make the last representative's message zero to quotient exchange.
        for mask in range(1, 1 << (k - 1)):
            first = np.array([bool(mask & (1 << j)) for j in range(k)])
            factor = exact_message_factor(labels[first]) * exact_message_factor(
                labels[~first]
            )
            if factor > best:
                best, choice, ties = factor, mask, 1
            elif factor == best:
                ties += 1
        size = choice.bit_count()
        chosen = np.array([bool(choice & (1 << j)) for j in range(k)])
        gain = (
            size * message_value(labels[chosen])
            + (k - size) * message_value(labels[~chosen])
        ) / k
        assert gain >= gains[1] - 1e-14
        result["optimal_two_message"] = {
            "gain": gain,
            "cell_sizes": [size, k - size],
            "cell_mask": choice,
            "exactly_tied_best_encoders": ties,
            "encoders_compared": (1 << (k - 1)) - 1,
        }
    return result


def learn(counts):
    d = len(counts)
    edges = counts + counts.T
    np.fill_diagonal(edges, 0)
    means = edges.mean(axis=1)
    centered = edges - means[:, None] - means[None, :] + means.mean()
    _, vectors = np.linalg.eigh(centered)
    initial = vectors[:, -1]
    s = -np.ones(d, dtype=np.int64)
    s[np.argsort(initial, kind="stable")[d // 2 :]] = 1
    swaps = 0
    while True:
        field = s * (edges @ s)
        improvement = -2 * (field[:, None] + field[None, :]) - 4 * edges
        improvement[(s[:, None] != 1) | (s[None, :] != -1)] = 0
        i, j = np.unravel_index(improvement.argmax(), improvement.shape)
        if improvement[i, j] <= 0:
            return s, swaps
        s[i], s[j] = -1, 1
        swaps += 1


def gain_for_overlap(q):
    return (log1p(-(KAPPA**2)) + KAPPA * log((1 + KAPPA) / (1 - KAPPA)) * q * q) / 2


def samples(rng, s, n):
    d = len(s)
    x = rng.integers(d, size=n)
    same = rng.random(n) < (1 + KAPPA) / 2
    sign_y = np.where(same, s[x], -s[x])
    pick = rng.integers(d // 2, size=n)
    plus, minus = np.flatnonzero(s == 1), np.flatnonzero(s == -1)
    y = np.where(sign_y == 1, plus[pick], minus[pick])
    return np.bincount(d * x + y, minlength=d * d).reshape(d, d)


def simulations():
    rng = np.random.default_rng(20261126)
    results = []
    for d in (12, 24):
        labels = representatives(d) if d == 12 else None
        for multiple in (1, 4, 16, 64):
            gains, overlaps, best, bayes, changes = [], [], [], [], []
            for _ in range(128):
                truth = rng.permutation(np.tile([-1, 1], d // 2))
                c = samples(rng, truth, d * multiple)
                learned, swaps = learn(c)
                q = abs(int(truth @ learned)) / d
                gains.append(gain_for_overlap(q))
                overlaps.append(q)
                changes.append(swaps)
                if labels is not None:
                    scores = np.sum((labels @ c) * labels, axis=1)
                    selected = labels[scores.argmax()]
                    assert int(learned @ c @ learned) <= int(scores.max())
                    best.append(gain_for_overlap(abs(int(truth @ selected)) / d))
                    # Supplemental comparison to the entire posterior over
                    # the same supplied candidate class, using only the tape.
                    posterior = np.exp(np.arctanh(KAPPA) * (scores - scores.max()))
                    posterior /= posterior.sum()
                    predicted = labels.T @ (posterior[:, None] * labels)
                    actual = 1 + KAPPA * np.outer(truth, truth)
                    bayes.append(float((actual * np.log1p(KAPPA * predicted)).mean()))
            results.append(
                {
                    "vocabulary": d,
                    "training_pairs": d * multiple,
                    "fits": 128,
                    "uniform_gain": 0.0,
                    "equality_gain": equality_gain(d),
                    "supplied_gain": oracle_gain(),
                    "learned_mean_gain": float(np.mean(gains)),
                    "learned_gain_standard_error": float(
                        np.std(gains, ddof=1) / np.sqrt(len(gains))
                    ),
                    "mean_absolute_overlap": float(np.mean(overlaps)),
                    "max_balanced_swaps": max(changes),
                    "exhaustive_fit_mean_gain": float(np.mean(best)) if best else None,
                    "supplemental_full_posterior_mean_gain": float(np.mean(bayes))
                    if bayes
                    else None,
                }
            )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "registration": REGISTRATION,
        "contrast": KAPPA,
        "finite": {d: finite(d) for d in (4, 6, 8, 12)},
        "simulation": simulations(),
    }
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
