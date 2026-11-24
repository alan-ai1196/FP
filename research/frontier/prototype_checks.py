"""Check the prototype lower bound and replay finite-packet acquisition."""

import argparse
import json
from fractions import Fraction as F
from math import comb
from pathlib import Path

import numpy as np
from prototype_learning import BIASES, HIGH, LOW, curve, fit_and_test, moment_projection
from scipy.special import rel_entr, roots_legendre
from scipy.stats import binom
from threadpoolctl import threadpool_limits


def jacobi(k, s):
    return (
        np.diag([0] * (k - 1) + [s])
        + np.diag(np.ones(k - 1, int), 1)
        + np.diag(np.ones(k - 1, int), -1)
    )


def component_moments(k, s, depth):
    mat = jacobi(k, s)
    v = np.array([F(1)] + [F(0)] * (k - 1))
    moments = []
    for _ in range(depth + 1):
        moments.append(v[0])
        v = mat @ v
    return moments


def ordered_path(moments, t, k):
    # Map x to p=1/2+x/8, then integrate p^k(1-p)^(t-k).
    return sum(
        F(
            comb(k, j) * comb(t - k, ell) * (-1) ** ell,
            8 ** (j + ell) * 2 ** (t - j - ell),
        )
        * moments[j + ell]
        for j in range(k + 1)
        for ell in range(t - k + 1)
    )


def exact_fibers():
    moments_checked = paths_checked = first_changes = 0
    for k in range(1, 5):
        critical = 2 * k - 1
        base = component_moments(k, F(0), critical + 1)
        for s in (F(-1, 2), F(-1, 7), F(1, 5), F(1, 2)):
            vals = component_moments(k, s, critical + 1)
            assert (
                vals[:critical] == base[:critical]
                and vals[critical] - base[critical] == s
            )
            moments_checked += critical + 1
            for t in range(critical + 1):
                for hits in range(t + 1):
                    change = ordered_path(vals, t, hits) - ordered_path(base, t, hits)
                    expected = F(0) if t < critical else (-1) ** (t - hits) * s / 8**t
                    assert change == expected
                    paths_checked += 1
                    first_changes += int(t == critical)
    feasible = 0
    for p, w in [
        *BIASES.values(),
        ([LOW, HIGH], [0.02, 0.98]),
        ([LOW], [1.0]),
        ([HIGH], [1.0]),
    ]:
        scaled = (np.asarray(p) - LOW) / (HIGH - LOW)
        y = curve(scaled) @ np.array(w)
        pp, ww, gap = moment_projection(y)
        np.testing.assert_allclose(curve((pp - LOW) / (HIGH - LOW)) @ ww, y, atol=1e-11)
        assert gap < 1e-10
        feasible += 1
    return {
        "rational_moment_equations": moments_checked,
        "rational_count_path_equations": paths_checked,
        "including_first_changes": first_changes,
        "noiseless_fits": feasible,
    }


def spectral_population(k, n, t, order):
    z, weights = roots_legendre(order)
    weights /= 2
    delta = n ** (-1 / (4 * k - 2)) / 8

    def count_law(s, length):
        vals, vec = np.linalg.eigh(jacobi(k, s))
        return binom.pmf(np.arange(length + 1)[:, None], length, 0.5 + delta * vals) @ (
            vec[0] ** 2
        )

    train = []
    for m in (2 * k - 2, 2 * k - 1):
        p0 = count_law(0.0, m)
        laws = np.stack([count_law(s / 2, m) for s in z])
        diff = (laws - p0) / p0
        # (1+x)log(1+x)-x, keeping the leading square at small x.
        phi = np.empty_like(diff)
        use = np.abs(diff) < 1e-3
        v = diff[use]
        phi[use] = v**2 * (0.5 + v * (-1 / 6 + v * (1 / 12 - v / 20)))
        phi[~use] = (1 + diff[~use]) * np.log1p(diff[~use]) - diff[~use]
        train.append(
            {
                "m": m,
                "N_times_mean_reference_kl": float(n * weights @ (phi @ p0)),
                "max_count_difference": float(np.abs(laws - p0).max()),
            }
        )
    laws = np.stack([count_law(s / 2, t) for s in z])
    mean = weights @ laws
    # Below this mass the sum of per-count information is bounded by the
    # discarded mixture mass times log(1/minimum quadrature-node weight).
    use = mean > 1e-28
    contributions = rel_entr(laws[:, use], mean[use]).sum(axis=1)
    info = float(weights @ contributions)
    return info, train


def run():
    with threadpool_limits(limits=1):
        exact = exact_fibers()
        spectral = []
        for k in range(1, 5):
            for n in (64, 4096):
                for t in (64, 1024, 16384):
                    i1, _ = spectral_population(k, n, t, 48)
                    i2, train = spectral_population(k, n, t, 96)
                    assert abs(i2 - i1) < 2e-7
                    assert train[0]["max_count_difference"] < 3e-14
                    spectral.append(
                        {
                            "K": k,
                            "N": n,
                            "T": t,
                            "future_information": i2,
                            "quadrature_difference": abs(i2 - i1),
                            "training": train,
                        }
                    )
        fits = fit_and_test()
    return {
        "unit": "total expected excess nats per fresh report",
        "exact": exact,
        "spectral": spectral,
        "fits": fits,
    }


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    p.add_argument("--check", type=Path)
    args = p.parse_args()
    result = run()
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched rational, spectral, and charged-packet comparisons.")
    elif args.output:
        head = {k: v for k, v in result.items() if k != "fits"}
        text = json.dumps(head, indent=2)[:-2] + ',\n  "fits": [\n'
        text += ",\n".join(
            "    " + json.dumps(r, separators=(",", ":")) for r in result["fits"]
        )
        args.output.write_text(text + "\n  ]\n}\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
