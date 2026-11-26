"""Exact finite observations for a weak binary latent-state distinction."""

import argparse
import json
from decimal import ROUND_CEILING, Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path


def probability(word, a, rho, linear=False):
    m, p = F(0), F(1)
    for y in word:
        factor = 1 + m * rho * y
        p *= factor / 2
        m = a * (m + rho * y) / (1 if linear else factor)
        if linear:
            m = max(F(-1), min(F(1), m))
    return p


def decimal(q):
    return Decimal(q.numerator) / Decimal(q.denominator)


def panels(exact, other):
    with localcontext() as ctx:
        ctx.prec = 70
        affinity = sum(decimal(p * q).sqrt() for p, q in zip(exact, other))
        exponent = -affinity.ln()
        sufficient = (Decimal(20).ln() / exponent).to_integral_value(
            rounding=ROUND_CEILING
        )
        return {
            "negative_log_affinity": float(exponent),
            "panels_sufficient_at_error_0.05": int(sufficient),
        }


def check():
    checks = 0
    word6 = tuple(product((-1, 1), repeat=6))
    outcomes = []
    for a in (F(-3, 4), F(-1, 4), F(1, 2), F(7, 8)):
        for rho in (F(1, 4), F(1, 8), F(1, 16)):
            exact, linear, refitted = [], [], []
            for x in product((-1, 1), repeat=3):
                p, q = probability(x, a, rho), probability(x, a, rho, True)
                assert q - p == a * a * rho**4 * (a * x[1] + x[0]) * x[2] / 8
                # C=alpha*eta² fixes the first two outcomes. Carry eta times
                # the linear state to keep the refitted calculation rational.
                alpha, c = a * (1 - rho * rho), a * rho * rho
                mean, mass = F(0), F(1)
                for sign in x:
                    mass *= (1 + mean * sign) / 2
                    mean = alpha * mean + c * sign
                assert mass - p == alpha * c * c * x[1] * x[2] / 8
                exact.append(p)
                linear.append(q)
                refitted.append(mass)
                checks += 1
            assert sum(exact) == sum(linear) == sum(refitted) == 1
            if a == F(1, 2):
                outcomes.append(
                    {
                        "contrast": float(rho),
                        "exact_versus_fair": panels(exact, [F(1, 8)] * 8),
                        "exact_versus_linear": panels(exact, linear),
                        "exact_versus_two_moment_matched_linear": panels(
                            exact, refitted
                        ),
                    }
                )
        # Orthogonality of the quadratic score under the independent null.
        q = [
            sum(a ** (t - s) * x[t] * x[s] for t in range(len(x)) for s in range(t))
            for x in word6
        ]
        assert sum(q) == 0
        assert sum(v * v for v in q) / len(q) == sum(
            (6 - l) * a ** (2 * l) for l in range(1, 6)
        )
    # Exact analytic four-word witness, with a=sqrt(2)-1 represented via
    # polynomial reduction modulo a²+2a−1. Its quadratic term is zero.
    from sympy import Poly, rem, symbols

    a, r = symbols("a r")
    x = (1, 1, -1, -1)
    ratio = 0
    for s in product((-1, 1), repeat=4):
        ratio += (
            prod((1 + a * s[i] * s[i + 1]) / 2 for i in range(3))
            * prod(1 + r * y * z for y, z in zip(x, s))
            / 2
        )
    terms = Poly(ratio.expand(), r)
    assert rem(terms.nth(2), a * a + 2 * a - 1, a) == 0
    assert terms.nth(4) == a * a and terms.nth(0) == 1
    assert terms.nth(2).expand() == (a * (1 - 2 * a - a * a)).expand()

    # Two separated length-two blocks cancel every unknown iid bias. Check
    # the same statistic on all raw words under both possible hold signs.
    block_words = tuple(product((-1, 1), repeat=5))

    def statistic(x):
        left, right = sum(x[:2]), sum(x[-2:])
        return F((left - right) ** 2 + left * right, 2) - 2

    for bias in (F(-1), F(-1, 3), F(0), F(2, 5), F(1)):
        assert (
            sum(statistic(x) * prod((1 + bias * y) / 2 for y in x) for x in block_words)
            == 0
        )
    for hold in (F(-3, 4), F(-1, 4), F(1, 2), F(7, 8), F(1)):
        rho = F(1, 3)
        cross = rho * rho * sum(hold ** (j - i) for i in range(2) for j in range(3, 5))
        assert (
            sum(statistic(x) * probability(x, hold, rho) for x in block_words)
            == 2 * rho * rho * hold - cross / 2
        )
    return {
        "three_token_exact_difference_checks": checks,
        "six_token_null_second_moments": 4,
        "quartic_witness_checked_symbolically": True,
        "two_block_nuisance_mean_checks": 10,
        "three_token_independent_panels_at_hold_one_half": outcomes,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.dumps(check(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(data.encode())
    else:
        print(data, end="")
