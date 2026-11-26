"""Finite randomized gates. Forward occupancy gives expected issued loss on a fixed tape."""

import argparse
import json
from bisect import bisect_left
from fractions import Fraction as F
from itertools import combinations, pairwise, product
from math import cos, fsum, log, pi
from pathlib import Path

from block_rescue import BlockPredictor, cut_weight, guarded_finite

HERE = Path(__file__).resolve().parent


def grid(h):
    return tuple(F(j * j, j * j + (h + 1 - j) ** 2) for j in range(1, h + 1))


def variance(z):
    return z * (1 - z)


def right_probability(z, x, y):
    a = (z - x) * variance(y)
    return a / (a + (y - z) * variance(x))


def allocation(z, levels, coins=None):
    right = bisect_left(levels, z)
    if right == 0:
        return ((0, F(1)),)
    if right == len(levels):
        return ((right - 1, F(1)),)
    if levels[right] == z:
        return ((right, F(1)),)
    left = right - 1
    prob = right_probability(z, levels[left], levels[right])
    if coins:
        prob = F(
            (2 * coins * prob.numerator + prob.denominator) // (2 * prob.denominator),
            coins,
        )
    if not prob:
        return ((left, F(1)),)
    if prob == 1:
        return ((right, F(1)),)
    return ((left, 1 - prob), (right, prob))


def inverse(z, x, y, prob):
    return max(
        z * ((1 - prob) / x + prob / y),
        (1 - z) * ((1 - prob) / (1 - x) + prob / (1 - y)),
    )


def envelope(h, coins=None):
    levels = grid(h)
    largest = max(1 / (1 - levels[0]), 1 / levels[-1])
    for j, (x, y) in enumerate(pairwise(levels), 1):
        if coins:
            # Each rounded probability is constant between rational thresholds.
            # The two inverse costs are affine there. Check both one-sided limits.
            for left in range(coins):
                t = F(2 * left + 1, 2 * coins)
                z = (t * y * variance(x) + (1 - t) * x * variance(y)) / (
                    t * variance(x) + (1 - t) * variance(y)
                )
                largest = max(
                    largest,
                    inverse(z, x, y, F(left, coins)),
                    inverse(z, x, y, F(left + 1, coins)),
                )
        else:
            z = F(j * (j + 1), j * (j + 1) + (h + 1 - j) * (h - j))
            largest = max(largest, inverse(z, x, y, right_probability(z, x, y)))
    return largest


def three_component_check():
    # Three reported vectors permute (2/3,1/6,1/6). Coordinate constraints directly
    # give lower bounds on the rounding probabilities allocated to each large entry.
    records = {}
    for power in (1, 2, 3):
        large, small = F(2, 3), F(1, 6)
        high = small ** (-power)
        spread = high - large ** (-power)
        cover = max(
            (large ** (-power) + (j - 1) * high) / j ** (1 + power) for j in (1, 2, 3)
        )
        worst = 0
        for i in range(21):
            for j in range(21 - i):
                z = sorted((F(i, 20), F(j, 20), F(20 - i - j, 20)), reverse=True)
                nonzero = [v for v in z if v]
                local = max(
                    (k * high - spread) / sum(v ** (-power) for v in nonzero[:k])
                    for k in range(1, len(nonzero) + 1)
                )
                assert local <= cover
                worst = max(worst, local)
        # Check the simplex barycenter as well as the mesh (20 is not divisible by 3).
        center = (3 * high - spread) / 3 ** (power + 1)
        assert max(worst, center) == cover
        records[power] = str(cover)
    return records


def coin_lower_check():
    # All two-state kernels whose four token-conditioned probabilities lie on this grid.
    def classification_error(pair):
        x, y = pair
        return (min(x, y) + min(1 - x, 1 - y)) / 2

    checks = 0
    for kernel in product((F(0), F(1, 2), F(1)), repeat=4):
        for n in (4, 8, 16):
            epsilon = F(2, n)
            discounted = []
            finite = []
            for bias in (F(7, 16), F(9, 16)):
                a = (1 - bias) * kernel[0] + bias * kernel[1]
                b = (1 - bias) * kernel[2] + bias * kernel[3]
                discounted.append((1 - epsilon) * a / (1 + (1 - epsilon) * (a - b)))
                state = total = F(0)
                for _ in range(n):
                    total += state
                    state = (1 - state) * a + state * b
                finite.append(total / n)
            assert classification_error(discounted) >= 1 / (1 + F(9, 7) ** 2)
            assert classification_error(finite) >= F(1, 20)
            checks += 1
    return checks


def check():
    choices = adversaries = 0
    for h in (2, 4, 8):
        levels = grid(h)
        exact = envelope(h)
        assert exact == (1 + F(2, h * (h + 2))) ** 2
        limited = envelope(h, h * h)
        assert (
            exact <= limited
            and float(exact) >= 1 / cos(pi / (2 * (h + 1))) ** 2 - 1e-15
        )
        assert float(exact) <= 1 / cos(2 / (h + 1)) ** 2 + 1e-15
        for i in range(129):
            z = F(i, 128)
            values = [max(z / q, (1 - z) / (1 - q)) for q in levels]
            for x, y in combinations(levels, 2):
                if x < z < y:
                    values.append(inverse(z, x, y, right_probability(z, x, y)))
            for coins, bound in ((None, exact), (h * h, limited)):
                parts = allocation(z, levels, coins)
                assert sum(p for _, p in parts) == 1
                ratio = max(
                    sum(p * z / levels[j] for j, p in parts),
                    sum(p * (1 - z) / (1 - levels[j]) for j, p in parts),
                )
                assert ratio <= bound
                if not coins:
                    assert ratio == min(values)
                choices += 1
        if h <= 4:
            for coins in (None, h * h):
                for steps in (1, 2, 3):
                    value = adaptive_ratio(levels, coins, steps)
                    bound = limited if coins else exact
                    assert value <= 2 * bound**steps
                    adversaries += 1
    return {
        "randomized_two_state_coin_kernel_checks": coin_lower_check(),
        "three_component_renyi_game_factors": three_component_check(),
        "independent_local_linear_program_checks": choices // 2,
        "all_local_coin_checks": choices,
        "adaptive_max_expected_ratio_checks": adversaries,
    }


def adaptive_ratio(levels, coins, n):
    # At each step the adversary sees the reported gate before choosing the bit.
    left, right = (F(3, 4), F(1, 4)), (F(1, 5), F(4, 5))

    def game(z, l, r, q, steps):
        result = F(0)
        for j, prob in allocation(z, levels, coins):
            v = levels[j]
            losses = []
            for a in range(2):
                p = (1 - v) * left[a] + v * right[a]
                l2, r2, q2 = l * left[a], r * right[a], q * p
                if steps == 1:
                    losses.append((l2 + r2) / q2)
                else:
                    losses.append(game(v * right[a] / p, l2, r2, q2, steps - 1))
            result += prob * max(losses)
        return result

    return game(F(1, 3), F(2, 3), F(1, 3), F(1), n)


def components(x):
    retained = [2, 1]
    blocks = BlockPredictor(2, 2, 16)
    scores = []
    for a in x:
        scores.append((F(retained[a] + 1, sum(retained) + 2), blocks.forecast()[a]))
        retained[a] += 1
        cleared = blocks.clears
        blocks.observe(a)
        if blocks.clears != cleared:
            retained = [2, 1]
    return scores


def prepared(scores, h, coins):
    levels = grid(h)
    # The same pair of expert probabilities often occurs at multiple positions.
    steps = {}
    for left, right in set(scores):
        rows = []
        for v in levels:
            prob = (1 - v) * left + v * right
            rows.append((-log(prob), allocation(v * right / prob, levels, coins)))
        steps[left, right] = rows
    return levels, steps


def expected(scores, eta, levels, steps, coins):
    # Joint probability of a gate index under its private draws on THIS fixed tape.
    live = [0.0] * len(levels)
    start = allocation(eta, levels, coins)
    for j, p in start:
        live[j] = float(p)
    random_updates = float(len(start) > 1)
    losses = []
    for t, key in enumerate(scores):
        rows = steps[key]
        losses.append(fsum(mass * row[0] for mass, row in zip(live, rows, strict=True)))
        if t + 1 == len(scores):
            break
        following = [0.0] * len(live)
        for mass, (_, choices) in zip(live, rows, strict=True):
            if len(choices) > 1:
                random_updates += mass
            for j, p in choices:
                following[j] += mass * float(p)
        assert abs(fsum(following) - 1) < 3e-13
        live = following
    return fsum(losses), random_updates


def exact_short(scores, eta, h, coins):
    levels = grid(h)

    def branch(t, j):
        l, r = scores[t]
        v = levels[j]
        p = (1 - v) * l + v * r
        if t + 1 == len(scores):
            return -log(p)
        return -log(p) + fsum(
            float(w) * branch(t + 1, k) for k, w in allocation(v * r / p, levels, coins)
        )

    return fsum(float(w) * branch(0, j) for j, w in allocation(eta, levels, coins))


def experiment():
    archived = json.loads((HERE / "block_rescue_result.json").read_text())
    answers = {}
    bounds = {}
    for bits in (1, 2, 3, 4):
        h = 2**bits
        bounds[bits] = {
            "levels": h,
            "optimal_real_grid_drift_nats": -2 * log(cos(pi / (2 * (h + 1)))),
            "rational_exact_gamma": str(envelope(h)),
            "rational_limited_gamma": str(envelope(h, h * h)),
        }
    for name, record in archived["tapes"].items():
        x = tuple(map(int, record["tape"]))
        scores = components(x)
        answers[name] = []
        for bits, bound in bounds.items():
            h = 2**bits
            for coins in (None, h * h):
                levels, steps = prepared(scores, h, coins)
                gamma = F(
                    bound["rational_limited_gamma" if coins else "rational_exact_gamma"]
                )
                for beta in (F(1, 4), F(1, 128)):
                    eta = cut_weight(beta)
                    control = guarded_finite(x, 2, 16, eta, bits)
                    nll, draws = expected(scores, eta, levels, steps, coins)
                    short, _ = expected(scores[:8], eta, levels, steps, coins)
                    assert abs(short - exact_short(scores[:8], eta, h, coins)) < 4e-13
                    ideal = control["same_experts_exact_gate_nats"]
                    assert nll - ideal <= len(x) * log(gamma) + 2e-10
                    answers[name].append(
                        {
                            "bits": bits,
                            "beta": str(beta),
                            "coin": "dyadic" if coins else "exact",
                            "expected_issued_nats": nll,
                            "exact_mixture_nats": ideal,
                            "deterministic_gate_nats": control["finite_mixture_nats"],
                            "expected_excess_nats": nll - ideal,
                            "allowance_nats": len(x) * log(gamma),
                            "expected_nontrivial_roundings": draws,
                        }
                    )
    return {"registration": "beccdb0", "grids": bounds, "tapes": answers}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = check() if args.command == "check" else experiment()
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(encoded.encode())
    else:
        print(encoded, end="")
