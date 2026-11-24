"""Acquire at most two persistent probabilities from ordinary grouped counts."""

from dataclasses import dataclass
from functools import cache
from math import comb

import numpy as np
from grouped_forecast import ATOMS, grid_fit
from scipy.optimize import minimize_scalar
from scipy.special import betaln, logsumexp, xlog1py, xlogy
from scipy.stats import binom

LOW, HIGH = 1 / 8, 7 / 8
BIASES = {
    "separated": ([0.23, 0.71], [0.37, 0.63]),
    "close": ([0.47, 0.54], [0.37, 0.63]),
    "single": ([0.53], [1.0]),
}
BUDGETS = (256, 4096, 65536)
PACKETS = (8, 16)
FUTURES = (64, 1024, 16384)
SEEDS = (401, 587, 821, 1033)


def scaled_moments(hist):
    m = len(hist) - 1
    raw = np.array(
        [
            sum(int(v) * comb(k, j) for k, v in enumerate(hist))
            / (hist.sum() * comb(m, j))
            for j in range(4)
        ]
    )
    return np.array(
        [
            sum(comb(j, k) * (-LOW) ** (j - k) * raw[k] for k in range(j + 1))
            / (HIGH - LOW) ** j
            for j in range(1, 4)
        ]
    )


def curve(z):
    return np.array([z, z * z, z**3])


def gaussian_nodes(y):
    """Return a feasible two-point representation on [0,1], if it exists."""
    mean, second, third = y
    variance = second - mean**2
    if not 0 <= mean <= 1:
        return None
    if variance <= 1e-13:
        if np.max(np.abs(y - curve(mean))) <= 1e-12:
            return np.array([mean]), np.ones(1)
        return None
    last = (third - mean**3 - 2 * mean * variance) / variance
    nodes, vec = np.linalg.eigh([[mean, np.sqrt(variance)], [np.sqrt(variance), last]])
    if nodes[0] < -1e-11 or nodes[1] > 1 + 1e-11:
        return None
    return np.clip(nodes, 0, 1), vec[0] ** 2


def segment_fit(y, anchor, z):
    start = curve(anchor)
    move = curve(z) - start
    norm = float(move @ move)
    weight = np.clip(((y - start) @ move) / norm, 0, 1) if norm else 0.0
    err = start + weight * move - y
    return float(err @ err), float(weight)


def moment_projection(y):
    """Euclidean projection onto the compact cubic moment body.

    A supporting cubic can touch the moment curve at a single interior point,
    or at an interior point and an endpoint, or at both endpoints. The linear
    oracle gap independently certifies proximity to the global minimum.
    """
    nodes = gaussian_nodes(y)
    if nodes is None:
        best = None
        mesh = np.linspace(0, 1, 65)
        for a in (0.0, 1.0):

            def obj(z, anchor=a):
                return segment_fit(y, anchor, z)[0]

            errors = np.array([obj(z) for z in mesh])
            candidates = [0.0, 1.0, mesh[errors.argmin()]]
            for j in range(1, len(mesh) - 1):
                if errors[j] <= min(errors[j - 1], errors[j + 1]) and (
                    errors[j] < max(errors[j - 1], errors[j + 1])
                ):
                    opt = minimize_scalar(
                        obj,
                        bounds=(mesh[j - 1], mesh[j + 1]),
                        method="bounded",
                        options={"xatol": 1e-14},
                    )
                    candidates.append(float(opt.x))
            for z in candidates:
                err, w = segment_fit(y, a, z)
                if best is None or err < best[0]:
                    best = err, np.array([a, z]), np.array([1 - w, w])
        _, points, weights = best
    else:
        points, weights = nodes
    keep = weights > 1e-14
    points, weights = points[keep], weights[keep] / weights[keep].sum()
    order = np.argsort(points)
    points, weights = points[order], weights[order]
    actual = curve(points) @ weights
    residual = actual - y
    roots = np.polynomial.polynomial.polyroots(residual * np.arange(1, 4))
    critical = [
        0.0,
        1.0,
        *(z.real for z in roots if abs(z.imag) < 1e-10 and 0 < z.real < 1),
    ]
    gap = float(residual @ actual - min(residual @ curve(z) for z in critical))
    assert gap < 5e-8, (y, points, gap)
    return LOW + (HIGH - LOW) * points, weights, max(gap, 0.0)


def packet(points, bits):
    levels = 1 << (bits // 2)
    centers = np.resize(points, 2)
    codes = np.rint((centers - LOW) * (levels - 1) / (HIGH - LOW)).astype(int)
    installed = LOW + (HIGH - LOW) * codes / (levels - 1)
    return codes.tolist(), installed


def decoder(centers, t, n, bits):
    divisions = int(np.ceil((HIGH - LOW) * np.sqrt(t)))
    grid = np.linspace(LOW, HIGH, divisions + 1)
    indices = np.rint((centers - LOW) * divisions / (HIGH - LOW)).astype(int)
    width = max(n ** (-1 / 6), 2 ** (-bits / 2), t ** (-0.5))
    block = int(np.ceil(width * np.sqrt(t)))
    displacements = np.abs(np.arange(divisions + 1)[:, None] - indices)
    weights = np.exp2(-(displacements // block).astype(float)).sum(axis=1)
    return grid, weights / weights.sum()


def path_logs(k, t, ps):
    p = np.asarray(ps)
    return xlogy(k[:, None], p) + xlog1py((t - k)[:, None], -p)


def mixture_log(paths, w):
    return logsumexp(paths + np.log(w), axis=1)


@dataclass
class CountExperiment:
    t: int
    k: np.ndarray
    mass: np.ndarray
    truth: np.ndarray
    kt: np.ndarray

    def risk(self, points, weights, floor=0.0):
        use = np.asarray(weights) > 0
        pred = mixture_log(
            path_logs(self.k, self.t, np.asarray(points)[use]), np.asarray(weights)[use]
        )
        if floor:
            pred = np.logaddexp(np.log1p(-floor) + pred, np.log(floor) + self.kt)
        return float(self.mass @ (self.truth - pred))


@cache
def experiment(family, t):
    p, w = (np.asarray(v) for v in BIASES[family])
    k = np.arange(t + 1)
    mass = binom.pmf(k[:, None], t, p) @ w
    use = mass > 1e-23
    assert abs(mass[use].sum() - 1) < 3e-12
    k = k[use]
    true = mixture_log(path_logs(k, t, p), w)
    kt = betaln(k + 0.5, t - k + 0.5) - betaln(0.5, 0.5)
    return CountExperiment(t, k, mass[use], true, kt)


def fit_and_test():
    fits = []
    for f, (p, w) in BIASES.items():
        for m in (3, 5):
            for seed in SEEDS:
                rng = np.random.default_rng([seed, m, list(BIASES).index(f)])
                # Generate the individual binary observations, then discard the
                # sampled bias. The two trainers receive the same count histogram.
                prior = rng.choice(p, max(BUDGETS), p=w)
                observed = (rng.random((len(prior), m)) < prior[:, None]).sum(axis=1)
                for n in BUDGETS:
                    hist = np.bincount(observed[:n], minlength=m + 1)
                    points, weights, pgap = moment_projection(scaled_moments(hist))
                    fitted, ggap = grid_fit(hist)
                    panels, words = {}, {}
                    for t in FUTURES:
                        panel = experiment(f, t)
                        values = {
                            "fitted_atoms": panel.risk(points, weights),
                            "grid65": panel.risk(ATOMS, fitted, 1 / 4096),
                            "half": float(panel.mass @ (panel.truth - panel.kt)),
                        }
                        for bits in PACKETS:
                            code, centers = packet(points, bits)
                            words[str(bits)] = code
                            values[f"packet_atoms_{bits}"] = panel.risk(
                                centers, [0.5, 0.5]
                            )
                            grid, prior_weights = decoder(centers, t, n, bits)
                            values[f"packet_smooth_{bits}"] = panel.risk(
                                grid, prior_weights
                            )
                        assert min(values.values()) > -1e-8
                        panels[str(t)] = values
                    fits.append(
                        {
                            "family": f,
                            "m": m,
                            "seed": seed,
                            "N": n,
                            "raw_counts": hist.tolist(),
                            "fitted_points": points.tolist(),
                            "fitted_weights": weights.tolist(),
                            "moment_duality_gap": pgap,
                            "grid_duality_gap": ggap,
                            "support_grid65": np.flatnonzero(fitted).tolist(),
                            "codes": words,
                            "risk": panels,
                        }
                    )
    return fits
