"""Learn a shared word distinction when each new task hides its sign."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import comb, log, log1p
from pathlib import Path

import numpy as np
from pair_dictionary import KAPPA, learn, representatives

REGISTRATION = "5bbf626"
BETA = KAPPA**2


def walsh(values):
    """Unnormalized sign-parity transform, indexed by subsets of the names."""
    a = values.copy()
    step = 1
    while step < len(a):
        chunks = a.reshape(-1, 2, step)
        left = chunks[:, 0].copy()
        right = chunks[:, 1].copy()
        chunks[:, 0] = left + right
        chunks[:, 1] = left - right
        step *= 2
    return a


class Law:
    def __init__(self, d):
        self.d = d
        self.bits = 1 << np.arange(d, dtype=np.int64)
        self.size = 1 << d
        self.labels = representatives(d)
        self.masks = (self.labels < 0) @ self.bits
        counts = np.fromiter((k.bit_count() for k in range(self.size)), dtype=np.int64)
        self.sign = 1 - 2 * (counts % 2)
        self.types = np.flatnonzero((counts % 2 == 0) & (counts <= 4))
        self.multiplicity = np.choose(
            counts[self.types] // 2, [3 * d * d - 2 * d, 12 * d - 16, 24]
        )
        assert self.multiplicity.sum() == d**4 and len(self.types) == 1 + comb(
            d, 2
        ) + comb(d, 4)
        self.raw = np.array(list(product(range(d), repeat=4)), dtype=np.int64)
        self.raw_type = np.bitwise_xor.reduce(self.bits[self.raw], axis=1)
        assert np.array_equal(
            np.bincount(self.raw_type, minlength=self.size)[self.types],
            self.multiplicity,
        )
        uniform = np.full(len(self.labels), 1 / len(self.labels))
        self.prior = self.mean_products(uniform)

    def mean_products(self, posterior):
        weights = np.zeros(self.size)
        weights[self.masks] = posterior
        return walsh(weights)[self.types]

    def gain(self, truth_mask, predict):
        truth = 1 + BETA * self.sign[truth_mask & self.types]
        return float((self.multiplicity * truth) @ np.log1p(BETA * predict) / self.d**4)

    def scores(self, raw):
        feature = np.bitwise_xor.reduce(self.bits[raw], axis=1)
        counts = np.bincount(feature, minlength=self.size)
        return walsh(counts)[self.masks]


def tasks(rng, truth, n):
    d = len(truth)
    latent = rng.choice([-1, 1], size=n)
    raw = np.empty((n, 4), dtype=np.int64)
    plus, minus = np.flatnonzero(truth == 1), np.flatnonzero(truth == -1)
    for i in (0, 2):
        x = rng.integers(d, size=n)
        copy = rng.random(n) < (1 + KAPPA) / 2
        y_sign = truth[x] * latent * np.where(copy, 1, -1)
        pos = rng.integers(d // 2, size=n)
        raw[:, i], raw[:, i + 1] = x, np.where(y_sign == 1, plus[pos], minus[pos])
    return raw


def fitted_gains(law, raw, truth):
    d = law.d
    truth_mask = int((truth < 0) @ law.bits)
    scores = law.scores(raw)
    best = int(law.masks[scores.argmax()])
    posterior = np.exp(np.arctanh(BETA) * (scores - scores.max()))
    posterior /= posterior.sum()
    # Remove the true link from the objective while retaining every raw pair.
    shifted = raw.copy()
    shifted[:, 2:] = np.roll(raw[:, 2:], -1, axis=0)
    other = int(law.masks[law.scores(shifted).argmax()])
    raw_id = ((raw[:, 0] * d + raw[:, 1]) * d + raw[:, 2]) * d + raw[:, 3]
    c = np.bincount(raw_id, minlength=d**4).reshape(-1, d)
    ratio = (c + 1) * d / (c.sum(axis=1, keepdims=True) + d)
    mass = 1 + BETA * law.sign[truth_mask & law.raw_type]
    # Supplemental polynomial comparator. It fits one sign per ordered pair
    # and is free of the factorization t_ij=s_i*s_j. Normalize its last row
    # because a balanced pair table can have unbalanced individual word rows.
    pair_counts = c.reshape(d * d, d * d)
    pair_sign, _ = learn(pair_counts)
    row = pair_sign.reshape(d, d)
    a, b, u, v = law.raw.T
    current = row[a, b]
    pair_ratio = (1 + BETA * current * row[u, v]) / (
        1 + BETA * current * row.mean(axis=1)[u]
    )
    assert np.max(abs(pair_ratio.reshape(-1, d).mean(axis=1) - 1)) < 1e-14
    return {
        "uniform": 0.0,
        "prior": law.gain(truth_mask, law.prior),
        "oracle": law.gain(truth_mask, law.sign[truth_mask & law.types]),
        "partition": law.gain(truth_mask, law.sign[best & law.types]),
        "posterior": law.gain(truth_mask, law.mean_products(posterior)),
        "shifted_partition": law.gain(truth_mask, law.sign[other & law.types]),
        "literal_three_token_context": float(np.mean(mass * np.log(ratio.ravel()))),
        "supplemental_unfactorized_pair_spectral": float(
            np.mean(mass * np.log(pair_ratio))
        ),
    }


def check(d):
    law = Law(d)
    x = law.raw
    # Numerators relative to uniform are scaled by four. Averaging the
    # opposite task signs reproduces the four-word law exactly.
    for truth in law.labels:
        first, second = truth[x[:, 0]] * truth[x[:, 1]], truth[x[:, 2]] * truth[x[:, 3]]
        numerator = ((2 + first) * (2 + second) + (2 - first) * (2 - second)) // 2
        assert np.array_equal(numerator, 4 + first * second)
        for length in (1, 2, 3):
            marginal = numerator.reshape(d**length, -1).sum(axis=1)
            assert np.all(marginal == 4 * d ** (4 - length))
    assert np.array_equal(
        law.scores(x[:37]), np.sum(np.prod(law.labels[:, x[:37]], axis=2), axis=1)
    )
    table = law.sign[law.masks[:, None] & law.types]
    assert np.max(abs(table.mean(axis=0) - law.prior)) < 1e-14
    # Compute the two-task mixture second moment over the no-training law
    # from exact raw-type likelihoods. Independently evaluate it by overlaps.
    beta = F(1, 4)
    mu2, mu4 = F(-1, d - 1), F(3, (d - 1) * (d - 3))
    k = len(law.labels)
    prior = [F(int(v), k) for v in table.sum(axis=0)]
    centered_moment = F(0)
    overlap = [F(int(law.labels[0] @ t), d) for t in law.labels]
    r2 = sum(r**2 for r in overlap) / k
    r4 = sum(r**4 for r in overlap) / k
    a = F(12 * d - 16, 2 * d * d) * (1 / (1 + beta * mu2) - 1 / (1 + beta * mu4))
    for j, r in enumerate(overlap):
        direct = (
            sum(
                int(mult) * (1 + beta * int(u)) * (1 + beta * int(v)) / (1 + beta * m)
                for mult, u, v, m in zip(law.multiplicity, table[0], table[j], prior)
            )
            / d**4
        )
        predicted = 1 + beta**2 * ((r**4 - r4) / (1 + beta * mu4) + a * (r**2 - r2))
        assert direct == predicted
        centered_moment += direct**2 / k
    assert centered_moment > 1
    tags = np.zeros(len(law.labels), dtype=np.int64)
    gains = []
    for b in range(d):
        if b:
            tags = 2 * tags + (law.labels[:, b] == 1)
        g = 0.0
        for tag in np.unique(tags):
            inside = tags == tag
            mean = table[inside].mean(axis=0)
            g += inside.mean() * float(
                (law.multiplicity * (1 + BETA * mean)) @ np.log1p(BETA * mean) / d**4
            )
        gains.append(g)
    assert np.all(np.diff(gains) >= -1e-15)
    return {
        "assignments": len(law.labels),
        "raw_words_per_assignment": d**4,
        "relative_label_gains": gains,
        "second_moment_two_tasks_over_prior": str(centered_moment),
    }


def sample():
    rng = np.random.default_rng(20261126)
    records = []
    for d in (6, 12):
        law = Law(d)
        for factor in (1, 16, 64, 256):
            rows = []
            for _ in range(128):
                truth = rng.permutation(np.tile([-1, 1], d // 2))
                rows.append(fitted_gains(law, tasks(rng, truth, factor * d), truth))
            scores = {}
            for name in rows[0]:
                values = np.array([row[name] for row in rows])
                scores[name] = {
                    "mean_gain": float(values.mean()),
                    "standard_error": float(values.std(ddof=1) / np.sqrt(len(values))),
                }
            records.append(
                {
                    "vocabulary": d,
                    "tasks": factor * d,
                    "fits": len(rows),
                    "scores": scores,
                }
            )
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "registration": REGISTRATION,
        "contrast": KAPPA,
        "oracle_gain": ((1 + BETA) * log1p(BETA) + (1 - BETA) * log(1 - BETA)) / 2,
        "exact_checks": {d: check(d) for d in (4, 6)},
        "reports": sample(),
    }
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
