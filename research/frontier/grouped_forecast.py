"""Moment-based causal prediction for a population of unlabeled Bernoulli sources."""

from fractions import Fraction
from functools import cache
from math import comb, prod

import numpy as np
from scipy.special import betaln, gammaln, rel_entr
from scipy.stats import binom

UNIT = 32767
ATOMS = np.linspace(0.0, 1.0, 65)


@cache
def binomial_table(t):
    return binom.pmf(np.arange(t + 1)[:, None], t, ATOMS)


@cache
def kt_counts(t):
    k = np.arange(t + 1)
    return np.exp(
        gammaln(t + 1)
        - gammaln(k + 1)
        - gammaln(t - k + 1)
        + betaln(k + 0.5, t - k + 0.5)
        - betaln(0.5, 0.5)
    )


def eigenvalue(m, j):
    if j > m:
        return Fraction(0)
    return Fraction(prod(range(m - j + 1, m + 1)), prod(range(m + 1, m + j + 1)))


def coefficient(m, j, k):
    """Degree-elevated Bernstein coefficient of the shifted Chebyshev polynomial."""
    lo, hi = max(0, k - (m - j)), min(j, k)
    return Fraction(
        sum(
            (-1) ** (j - i) * comb(2 * j, 2 * i) * comb(m - j, k - i)
            for i in range(lo, hi + 1)
        ),
        comb(m, k),
    )


@cache
def inverse_bank(m):
    return np.array(
        [[float(coefficient(m, j, k)) for j in range(1, m + 1)] for k in range(m + 1)]
    )


@cache
def conditional_modes(t, degree):
    """Posterior cos(j theta) for an arcsine reference prior and a success count."""
    result = np.zeros((t + 1, degree + 1))
    result[:, 0] = 1
    signed = 2 * np.arange(t + 1) - t
    if degree:
        result[:, 1] = signed / (t + 1)
    for j in range(1, min(degree, t)):
        result[:, j + 1] = (
            2 * signed * result[:, j] - (t + 1 - j) * result[:, j - 1]
        ) / (t + 1 + j)
    return result


def harmonic_law(t, weights):
    """Each weight row contains the Fourier cosine coefficients after smoothing."""
    weights = np.atleast_2d(weights)
    h = conditional_modes(t, weights.shape[1])[:, 1:]
    probs = (1 + 2 * weights @ h.T) * kt_counts(t)
    assert np.all(probs > 0)
    np.testing.assert_allclose(probs.sum(axis=1), 1, atol=5e-12, rtol=0)
    return probs


def fit_harmonics(hist, selection):
    m = hist.shape[1] - 1
    freq = hist / hist.sum(axis=1, keepdims=True)
    empirical = np.clip(freq @ inverse_bank(m), -1, 1)
    best = None
    for degree in [d for d in (0, 1, 2, 4, 8, 16) if d <= m]:
        offsets = np.abs(np.arange(degree + 1)[:, None] - np.arange(degree + 1))
        moments = np.column_stack([np.ones(len(hist)), empirical[:, :degree]])
        least = np.linalg.eigvalsh(moments[:, offsets])[:, 0]
        shift = np.maximum(-least, 0)
        taper = 1 - np.arange(1, degree + 1) / (degree + 1)
        for floor in (1 / 64, 1 / 8, 1 / 2):
            real = (1 - floor) * empirical[:, :degree] * taper / (1 + shift[:, None])
            packet = np.rint(UNIT * real).astype(np.int16)
            installed = packet.astype(float) / UNIT
            assert floor - degree / UNIT > 0
            probs = harmonic_law(m, installed)
            nll = float(-np.sum(selection * np.log(probs)))
            if best is None or nll < best[0] - 1e-10:
                best = nll, packet, floor, shift.copy()
    return best[1:]


def grid_fit(hist):
    """Fully corrective support search with a likelihood directional-gap certificate."""
    from scipy.optimize import minimize

    m = len(hist) - 1
    use = hist > 0
    frequency = hist[use] / hist.sum()
    emissions = binomial_table(m)[use, :]
    initial = int(
        np.clip(np.rint(64 * (hist @ np.arange(m + 1)) / (m * hist.sum())), 1, 63)
    )
    support = [initial]
    weights = np.ones(1)
    for _ in range(120):
        subset = emissions[:, support]
        predictive = subset @ weights
        gradient = (frequency / predictive) @ emissions
        gap = float(gradient.max() - 1)
        if gap <= 5e-7:
            result = np.zeros(len(ATOMS))
            result[support] = weights
            return result, max(gap, 0)
        j = int(np.argmax(gradient))
        if j not in support:
            support.append(j)
            weights = np.r_[0.99 * weights, 0.01]
        subset = emissions[:, support]

        def objective(w, subset=subset):
            q = np.maximum(subset @ w, 1e-150)
            return float(-frequency @ np.log(q)), -(frequency / q) @ subset

        constraint = {
            "type": "eq",
            "fun": lambda w: w.sum() - 1,
            "jac": lambda w: np.ones_like(w),
        }
        opt = minimize(
            objective,
            weights,
            jac=True,
            method="SLSQP",
            bounds=[(0.0, 1.0)] * len(weights),
            constraints=[constraint],
            options={"ftol": 1e-14, "maxiter": 300},
        )
        weights = np.maximum(opt.x, 0)
        weights /= weights.sum()
        keep = weights > 1e-12
        support = [s for s, positive in zip(support, keep) if positive]
        weights = weights[keep] / weights[keep].sum()
    raise ArithmeticError(f"grid likelihood gap {gap} at m={m}")


def grid_law(t, fitted, floor):
    return (1 - floor) * (fitted @ binomial_table(t).T) + floor * kt_counts(t)


def fit_grid(hist, selection):
    solutions = [grid_fit(row) for row in hist]
    weights = np.stack([s[0] for s in solutions])
    m = hist.shape[1] - 1
    floors = (1 / 4096, 1 / 64, 1 / 8, 1 / 2)
    costs = [-np.sum(selection * np.log(grid_law(m, weights, v))) for v in floors]
    return weights, floors[int(np.argmin(costs))], max(s[1] for s in solutions)


@cache
def thinning(m, t):
    assert t <= m
    return np.array(
        [
            [
                comb(k, j) * comb(m - k, t - j) / comb(m, t)
                if j <= k and t - j <= m - k
                else 0
                for j in range(t + 1)
            ]
            for k in range(m + 1)
        ]
    )


def count_kl(a, b):
    return rel_entr(a, b).sum(axis=-1)
