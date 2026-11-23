"""Acquire an unfamiliar ticket mapping from the bit received on each purchase."""

from dataclasses import dataclass
from itertools import permutations
from math import log

import numpy as np

K = 4
A = 1 / 32
B = 1 - (K - 1) * A
L = log(B / A)
PERMS = np.array(list(permutations(range(K))), dtype=np.uint8)
CHECKPOINTS = (0, 8, 64, 512)


def floor_law(p):
    return A + (1 - K * A) * p


def ridge_features(p):
    return np.column_stack((np.ones(len(p)), p[:, :3] - p[:, 3:]))


def project_simplex(x):
    """Euclidean projection of each row, including possible ties on the boundary."""
    v = np.sort(x, axis=-1)[..., ::-1]
    t = (np.cumsum(v, axis=-1) - 1) / np.arange(1, K + 1)
    last = np.sum(v > t, axis=-1) - 1
    threshold = np.take_along_axis(t, last[..., None], axis=-1)
    return np.maximum(x - threshold, 0)


@dataclass
class Compiled:
    readout: np.ndarray
    map_index: int | None

    def probabilities(self, prior, features):
        if self.map_index is None:
            return floor_law(project_simplex(1 / K + features @ self.readout.T))
        return prior @ self.readout.T


class PermutationLearner:
    def __init__(self):
        self.log_weights = np.zeros(len(PERMS))

    def weights(self):
        w = np.exp(self.log_weights - self.log_weights.max())
        return w / w.sum()

    def price_threshold(self, prior, features, name):
        return self.weights() @ prior[PERMS[:, name]]

    def buy_feedback(self, prior, features, name, hit):
        p = prior[PERMS[:, name]]
        self.log_weights += np.log(p) if hit else np.log1p(-p)

    def compile(self):
        w = self.weights()
        matrix = np.stack([np.bincount(col, weights=w, minlength=K) for col in PERMS.T])
        return Compiled(matrix, int(np.argmax(self.log_weights)))


class RewardRidge:
    def __init__(self):
        self.gram = np.tile(np.eye(K), (K, 1, 1))
        self.target = np.zeros((K, K))
        self.coef = np.zeros((K, K))

    def price_threshold(self, prior, features, name):
        return floor_law(project_simplex(1 / K + self.coef @ features))[name]

    def buy_feedback(self, prior, features, name, hit):
        self.gram[name] += np.outer(features, features)
        self.target[name] += features * (hit - 1 / K)
        self.coef[name] = np.linalg.solve(self.gram[name], self.target[name])

    def compile(self):
        return Compiled(self.coef.copy(), None)


def acquire(prior, features, names, prices, purchase, ridge=False):
    learner = RewardRidge() if ridge else PermutationLearner()
    snapshots = {}
    buys = hits = 0

    def checkpoint(n):
        compiled = learner.compile()
        # Independently evaluate four available actions through the online entry point.
        for i in (0, len(prior) - 1):
            scores = compiled.probabilities(prior[i : i + 1], features[i : i + 1])[0]
            direct = [
                learner.price_threshold(prior[i], features[i], j) for j in range(K)
            ]
            assert np.allclose(scores, direct, atol=2e-14, rtol=0)
            assert abs(scores.sum() - 1) < 2e-14
        snapshots[n] = compiled, buys, hits

    checkpoint(0)
    for i in range(CHECKPOINTS[-1]):
        j = int(names[i])
        threshold = np.clip(learner.price_threshold(prior[i], features[i], j), A, B)
        if threshold >= prices[i]:
            hit = purchase(i, j)
            learner.buy_feedback(prior[i], features[i], j, hit)
            buys += 1
            hits += int(hit)
        if i + 1 in CHECKPOINTS:
            checkpoint(i + 1)
    return snapshots


def menu(rng, n, epsilon):
    names = rng.integers(K, size=n, dtype=np.uint8)
    low = rng.random(n) < epsilon
    prices = np.where(low, A, A * np.exp(L * rng.random(n)))
    return names, prices


def bounded_action_metrics(p, names, prices, winning_name):
    index = np.arange(len(p))
    buy = p[index, names] >= prices
    reward = buy * ((names == winning_name).astype(float) - prices)
    expected = (np.log(p[index, winning_name] / A) - 1 + K * A) / (K * L)
    # Equal probabilities to numerical precision use the lowest action name.
    greedy = np.argmax(p >= p.max(axis=1, keepdims=True) - 1e-14, axis=1)
    return buy, reward, expected, greedy == winning_name
