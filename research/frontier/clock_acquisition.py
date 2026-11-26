"""Price unit ticks and destructive or nondestructive color reads on adjacent clock periods."""

import json
from functools import cache
from math import exp, sqrt

import numpy as np


def probabilities(k, j):
    return (1 + 0.5 * np.cos(2 * np.pi * j / k)) / 2


def information(k, ages):
    p, q = probabilities(k, ages), probabilities(k + 1, ages)
    distance = (
        (np.sqrt(p) - np.sqrt(q)) ** 2 + (np.sqrt(1 - p) - np.sqrt(1 - q)) ** 2
    ) / 2
    return -np.log1p(-distance)


def budget_exponent(k, budget, destructive):
    j = np.arange(budget)
    gain = information(k, j)
    if not destructive:
        return max((budget - j) * gain, default=0)
    best = np.zeros(budget + 1)
    for t in range(1, budget + 1):
        best[t] = np.max(gain[:t] + best[t - 1 :: -1])
    return best[-1]


def brute(k, destructive):
    # Every read allows independent policy subtrees after a red or a blue mark.
    @cache
    def trees(t, age):
        if t == 0:
            return np.ones(1)
        after_tick = trees(t - 1, age + 1)
        after_read = trees(t - 1, 0 if destructive else age)
        p, q = probabilities(k, age), probabilities(k + 1, age)
        choices = (
            sqrt(p * q) * after_read[:, None]
            + sqrt((1 - p) * (1 - q)) * after_read[None, :]
        )
        return np.r_[1.0, after_tick, choices.ravel()]

    for t in range(1, 5):
        direct = trees(t, 0)
        assert abs(min(direct) - exp(-budget_exponent(k, t, destructive))) < 2e-14
    return len(trees(4, 0))


def main():
    checks = [brute(k, kind) for k in (4, 7) for kind in (False, True)]
    rows = []
    for k in (16, 32, 64, 128, 256, 512):
        period = k * (k + 1)
        j = np.arange(period)
        gain = information(k, j)
        efficacy = gain / (j + 1)
        best = int(efficacy.argmax())
        # Repeating any later age has the same color law and a larger access cost.
        useful = gain > 0
        payment = j[useful] + np.ceil(1 / gain[useful])
        best_nondestructive = int(payment.min())
        # Colors at all ages over a full joint period are exactly orthogonal cosines.
        p, q = probabilities(k, j), probabilities(k + 1, j)
        square_sum = float(np.sum((p - q) ** 2))
        assert abs(square_sum - period / 16) < 1e-11 * period
        rows.append(
            {
                "k": k,
                "best_destructive_age": best,
                "k2_times_best_destructive_exponent_per_payment": float(
                    k * k * efficacy[best]
                ),
                "nondestructive_payments_for_unit_exponent": best_nondestructive,
                "nondestructive_payments_over_k_to_four_thirds": best_nondestructive
                / k ** (4 / 3),
            }
        )
    return {"adaptive_trees_per_four_payment_case": checks, "rows": rows}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
