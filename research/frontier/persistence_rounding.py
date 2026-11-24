"""Sum rounding loss over every short observable word and stochastic rounding choice."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.special import expit, logit, rel_entr


def assignments(value, lo, step, levels, stochastic):
    location = np.clip((logit(value) - lo) / step, 0, levels - 1)
    if stochastic:
        left = np.floor(location).astype(int)
        return left, np.minimum(left + 1, levels - 1), location - left
    nearest = np.floor(location + 0.5).astype(int)
    return nearest, nearest, np.zeros_like(location)


def exact_tree(h, levels, stochastic, depth=12):
    pi = 0.29
    lo, hi = logit(h * pi), logit(1 - h * (1 - pi))
    step = (hi - lo) / (levels - 1)
    grid = expit(np.linspace(lo, hi, levels))
    prior, reach, last = np.array([pi]), np.ones(1), np.array([0])
    rounded = np.zeros((1, levels))
    l, r, f = assignments(pi, lo, step, levels, stochastic)
    rounded[0, l] += 1 - f
    rounded[0, r] += f
    cumulative = 0.0
    for t in range(depth):
        # The emissions depend on public history and differ at consecutive steps.
        base = 0.2 + 0.28 * last + 0.04 * (t % 3)
        p0, p1 = expit(logit(base) - 1.3), expit(logit(base) + 0.85)
        p = (1 - prior) * p0 + prior * p1
        q = p0[:, None] + (p1 - p0)[:, None] * grid
        kl = rel_entr(p[:, None], q) + rel_entr(1 - p[:, None], 1 - q)
        cumulative += float(reach @ (rounded * kl).sum(axis=1))
        nxt, exact, weights = [], [], []
        ids = np.broadcast_to(np.arange(len(prior))[:, None], q.shape)
        for y in (0, 1):
            e = p1 if y else 1 - p1
            target = p if y else 1 - p
            x = q if y else 1 - q
            exact.append((1 - h) * prior * e / target + h * pi)
            weights.append(reach * target)
            v = (1 - h) * grid * e[:, None] / x + h * pi
            left, right, frac = assignments(v, lo, step, levels, stochastic)
            dist = np.zeros_like(q)
            np.add.at(dist, (ids, left), (1 - frac) * rounded)
            np.add.at(dist, (ids, right), frac * rounded)
            nxt.append(dist)
        last = np.repeat([0, 1], len(prior))
        prior, reach, rounded = (
            np.concatenate(exact),
            np.concatenate(weights),
            np.concatenate(nxt),
        )
        np.testing.assert_allclose(rounded.sum(axis=1), 1, rtol=0, atol=3e-14)
        assert abs(reach.sum() - 1) < 2e-14
    bound = depth * step**2 / 32 * (1 if stochastic else (1 + (1 - h) ** 2 / h))
    assert 0 <= cumulative <= bound
    return {
        "refresh": h,
        "levels": levels,
        "randomized": stochastic,
        "horizon": depth,
        "operational_kl": cumulative,
        "bound": bound,
    }


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    args = p.parse_args()
    rows = [
        exact_tree(h, l, s)
        for h in (0.03, 0.32)
        for l in (4, 16)
        for s in (False, True)
    ]
    if args.write:
        args.write.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf8")
    elif args.check:
        assert compare(rows, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched exact finite-tree expected scores.")
    else:
        print(json.dumps(rows, indent=2))
