"""Learn a unary endpoint recurrence from short, noisy, unlabelled report pairs."""

import json
from collections import deque
from fractions import Fraction
from math import lcm, log, sqrt
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.optimize import minimize

SEEDS = (173, 419, 773)
BUDGETS = (4096, 65536, 1048576, 16777216)
LIMIT = 20
RHO_RANGE = (0.5, 0.875)
X = sp.Symbol("x")


class PairSource:
    """Uniform hidden reset. This side alone knows the cycles and report law."""

    def __init__(self, cycles=(3, 4, 5, 7), rho=0.75):
        self.cycles = [np.array([1] + [-1] * (m - 1)) for m in cycles]
        self.n = sum(cycles)
        self.rho = rho
        self.mu = rho * sum(c.sum() for c in self.cycles) / self.n

    def c(self, lag):
        return Fraction(sum(int(c @ np.roll(c, lag)) for c in self.cycles), self.n)

    def pairs(self, seed, budget, lags):
        counts = []
        for lag in lags:
            corr = self.rho**2 * float(self.c(lag))
            joint = [
                (1 + (z + y) * self.mu + z * y * corr) / 4
                for z in (-1, 1)
                for y in (-1, 1)
            ]
            rng = np.random.default_rng([seed, budget, lag, 2511])
            counts.append(rng.multinomial(budget, joint))
        return np.array(counts)


def observations(counts):
    per_lag = counts.sum(axis=1)
    products = counts @ [1, -1, -1, 1] / per_lag
    mu = counts.sum(axis=0) @ [-1, 0, 0, 1] / per_lag.sum()
    scale = np.clip(products[0], *np.square(RHO_RANGE))
    return products, float(mu), float(scale)


def grid_options(products, uncertainty, cap):
    low = max(RHO_RANGE[0] ** 2, products[0] - uncertainty)
    high = min(RHO_RANGE[1] ** 2, products[0] + uncertainty)
    possible = [set() for _ in products]
    sizes = []
    if low > high:
        return sizes, possible
    intervals = [(1.0, 1.0)]
    for value in products[1:]:
        corners = [
            (value + e) / s for e in (-uncertainty, uncertainty) for s in (low, high)
        ]
        intervals.append((min(corners), max(corners)))
    for n in range(1, cap + 1):
        grid = [Fraction(n - 4 * k, n) for k in range(n // 2 + 1)]
        compatible = [{g for g in grid if lo <= float(g) <= hi} for lo, hi in intervals]
        if all(compatible):
            sizes.append(n)
            for values, matches in zip(possible, compatible, strict=True):
                values.update(matches)
    return sizes, possible


def certificate(products, budget, cap=LIMIT, comparisons=12):
    error = sqrt(2 * log(2 * comparisons * len(products) / 0.05) / budget)
    sizes, possible = grid_options(products, error, cap)
    diagnostic = {
        "possible_sizes": sizes,
        "radius": error,
        "ambiguous_lags": [i for i, s in enumerate(possible) if len(s) != 1],
    }
    if not sizes:
        return None, diagnostic
    known = [Fraction(1)]
    for d in range(1, cap + 1):
        if d == cap:
            # Full Krylov dimension n=cap forces the permutation to be a single cycle.
            coefficients = [1] + [0] * (d - 1)
            break
        if d >= len(possible) or len(possible[d]) != 1:
            return None, diagnostic
        known.append(next(iter(possible[d])))
        gram = sp.Matrix(d, d, lambda i, j: known[abs(i - j)])
        cross = sp.Matrix(known[d:0:-1])
        coef = gram.inv() * cross
        residual = 1 - (cross.T * coef)[0]
        if residual < 0:
            return None, diagnostic
        if residual == 0:
            if not all(t.is_Integer for t in coef):
                return None, diagnostic
            coefficients = [int(t) for t in coef]
            break
    poly = sp.Poly(X**d - sum(a * X**i for i, a in enumerate(coefficients)), X)
    roots = []
    for order in range(1, cap + 1):
        cyclo = sp.Poly(sp.cyclotomic_poly(order, X), X)
        quotient, rem = poly.div(cyclo)
        if rem.is_zero:
            roots.append(order)
            poly = quotient
    if poly != sp.Poly(1, X):
        return None, diagnostic
    denominator = lcm(*(t.denominator for t in known[:d]))
    packet = {
        "coefficients": coefficients,
        "denominator": denominator,
        "initial": [int(t * denominator) for t in known[:d]],
        "orders": roots,
        "period": lcm(*roots),
    }
    cycle = stream(packet, packet["period"] + d)
    # Check the arithmetic orbit and all observed intervals against the SAME prior size.
    if cycle[:d] != cycle[-d:] or max(map(abs, cycle)) > denominator:
        return None, diagnostic
    observed = [
        Fraction(cycle[i % packet["period"]], denominator) for i in range(len(products))
    ]
    feasible = [
        n for n in sizes if all((n * (1 - v) / 4).denominator == 1 for v in observed)
    ]
    if not feasible or not all(v in s for v, s in zip(observed, possible, strict=True)):
        return None, diagnostic
    return packet, diagnostic


def stream(packet, count):
    ring = deque(packet["initial"])
    coefficients = packet["coefficients"]
    out = []
    for _ in range(count):
        out.append(ring[0])
        successor = sum(a * z for a, z in zip(coefficients, ring, strict=True))
        ring.popleft()
        ring.append(successor)
    return out


def confidence_forecast(mu, corr, sign):
    p = 0.5 * (1 + (mu + sign * corr) / (1 + sign * mu))
    floor = (1 - RHO_RANGE[1]) / 2
    return np.clip(p, floor, 1 - floor)


def mean_kl(source, lags, true_corr, fitted_mu, fitted_corr):
    loss = 0.0
    for sign in (-1, 1):
        weight = (1 + sign * source.mu) / 2
        p = confidence_forecast(source.mu, true_corr, sign)
        q = confidence_forecast(fitted_mu, fitted_corr, sign)
        assert np.shape(q) in ((), np.shape(lags))
        loss += weight * np.mean(
            p * np.log(p / q) + (1 - p) * np.log((1 - p) / (1 - q))
        )
    return float(loss)


def period_fit(counts):
    trials = counts.sum(axis=1)
    equal = counts[:, 0] + counts[:, 3]
    lengths = np.arange(len(counts))
    best = None
    for p in range(1, len(counts) + 1):
        bins = lengths % p
        totals = np.bincount(bins, weights=trials)
        hits = np.bincount(bins, weights=equal)
        probs = np.clip(hits / totals, 1e-15, 1 - 1e-15)
        criterion = -np.sum(hits * np.log(probs) + (totals - hits) * np.log1p(-probs))
        criterion += 0.5 * p * np.log(trials.sum())
        if best is None or criterion < best[0]:
            best = criterion, 2 * probs - 1
    return best[1]


def two_state_fit(raw, scale):
    values = np.linspace(-1, 1, 4097)
    powers = values[:, None] ** np.arange(len(raw))
    delta = 1 - powers
    norms = np.sum(delta**2, axis=1)
    weight = np.clip(
        np.sum(delta * (raw / scale - powers), axis=1) / np.where(norms > 0, norms, 1),
        0,
        1,
    )
    loss = np.sum((weight[:, None] * delta + powers - raw / scale) ** 2, axis=1)
    i = loss.argmin()
    return float(weight[i]), float(values[i])


def frequency_fit(raw, scale, cap):
    frequencies = sorted(
        {Fraction(j, m) for m in range(1, cap + 1) for j in range(m // 2 + 1)}
    )
    angular = 2 * np.pi * np.array(frequencies, dtype=float)
    design = np.cos(np.outer(np.arange(len(raw)), angular))
    target = raw / scale

    def objective(w):
        delta = design @ w - target
        return 0.5 * (delta @ delta + 1e-9 * (w @ w)), design.T @ delta + 1e-9 * w

    initial = np.full(len(angular), 1 / len(angular))
    fit = minimize(
        objective,
        initial,
        jac=True,
        method="SLSQP",
        bounds=[(0, 1)] * len(angular),
        constraints=[
            {
                "type": "eq",
                "fun": lambda w: w.sum() - 1,
                "jac": lambda w: np.ones_like(w),
            }
        ],
        options={"maxiter": 3000, "ftol": 1e-13},
    )
    if not fit.success:
        raise RuntimeError(fit.message)
    return angular, fit.x


def run():
    source = PairSource()
    spans = [np.arange(21, 441), np.arange(100001, 100421)]
    lags = np.concatenate(spans)
    truth = source.rho**2 * np.array([float(source.c(int(i))) for i in lags])
    fits, installations = [], []
    for seed in SEEDS:
        for budget in BUDGETS:
            counts = source.pairs(seed, budget, range(LIMIT + 1))
            raw, mu, scale = observations(counts)
            packet, diag = certificate(raw, budget)
            period_table = period_fit(counts)
            a, rate = two_state_fit(raw, scale)
            angular, weights = frequency_fit(raw, scale, LIMIT)
            pred = {
                "marginal": np.full(lags.size, mu**2),
                "period_table": period_table[lags % len(period_table)],
                "two_state": scale * (a + (1 - a) * rate**lags),
                "frequency_mixture": scale
                * (np.cos(np.outer(lags, angular)) @ weights),
            }
            if packet:
                # No externally supplied test-length modulus for the learned forecast.
                seq = np.array(stream(packet, int(lags[-1]) + 1))
                pred["certified"] = scale * seq[lags] / packet["denominator"]
                oracle_period = lcm(*(len(c) for c in source.cycles))
                exact = [
                    source.c(i) * packet["denominator"] for i in range(oracle_period)
                ]
                assert all(v.denominator == 1 for v in exact)
                np.testing.assert_array_equal(
                    seq, np.resize(np.array(exact, dtype=int), len(seq))
                )
            else:
                pred["certified"] = pred["marginal"]
            scores = {
                name: [
                    mean_kl(
                        source,
                        h,
                        truth[j * 420 : (j + 1) * 420],
                        mu,
                        corr[j * 420 : (j + 1) * 420],
                    )
                    for j, h in enumerate(spans)
                ]
                for name, corr in pred.items()
            }
            if packet is not None and packet not in installations:
                installations.append(packet)
            fits.append(
                {
                    "seed": seed,
                    "episodes_per_lag": budget,
                    "mean_sign": mu,
                    "scale": scale,
                    "certificate": None
                    if packet is None
                    else installations.index(packet),
                    **diag,
                    "period_fit": len(period_table),
                    "two_state": [a, rate],
                    "frequency_weights_above_1e-5": int(sum(weights > 1e-5)),
                    "reports": 2 * len(raw) * budget,
                    "raw_advances": sum(range(len(raw))) * budget,
                    "conditional_excess_nats": scores,
                }
            )
    return {
        "registration": "3d4b9a2",
        "length_ranges": [[21, 440], [100001, 100420]],
        "installations": installations,
        "fits": fits,
    }


if __name__ == "__main__":
    Path(__file__).with_name("reversible_pairs_result.json").write_text(
        json.dumps(run(), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
