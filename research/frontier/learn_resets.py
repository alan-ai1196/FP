"""Learn a same-episode or reset decision from randomized ordinary bit sequences."""

import argparse
import json
from fractions import Fraction as F
from functools import cache
from pathlib import Path

import numpy as np
from grouped_forecast import (
    UNIT,
    count_kl,
    fit_grid,
    fit_harmonics,
    grid_law,
    harmonic_law,
    kt_counts,
    thinning,
)
from scipy.stats import binom
from threadpoolctl import threadpool_limits

FAMILIES = ("bright", "reflected", "contracted", "fixed")
SEEDS = (401, 587, 821, 1033)
BUDGETS = (512, 8192, 65536)
HORIZONS = (1, 8, 32, 128)
COSTS = (0.0, 0.00025, 0.001, 0.004, 0.016)


def environment(family):
    coins = np.array([[1 / 8, 7 / 8], [1 / 2, 7 / 8]])
    weights = np.array([[7 / 12, 5 / 12], [7 / 15, 8 / 15]])
    if family == "reflected":
        coins = 1 - coins
    elif family == "contracted":
        coins = 0.5 + (coins - 0.5) / 4
    elif family == "fixed":
        coins = np.array([[0.25, 0.25], [0.75, 0.75]])
    elif family != "bright":
        raise ValueError(family)
    return coins, weights


def calibration_logs(family, m, seed, n):
    coins, weights = environment(family)
    rng = np.random.default_rng([seed, FAMILIES.index(family), m])
    world = rng.integers(0, 2, n)

    def sample_coin():
        component = (rng.random(n) >= weights[world, 0]).astype(int)
        return coins[world, component]

    first = sample_coin()
    x = (rng.random(n) < first).astype(np.int8)
    a = rng.integers(0, 2, n, dtype=np.int8)
    second = np.where(a, sample_coin(), first)
    b = (rng.random(n) < second).astype(np.int8)
    fresh = sample_coin()
    report = (rng.random((n, m)) < fresh[:, None]).sum(axis=1)
    # The trainer is given only the action receipt and observed bits/count.
    return (4 * x + 2 * a + b).astype(np.int64), report


def histogram(h, k, m):
    return np.bincount((m + 1) * h + k, minlength=8 * (m + 1)).reshape(8, m + 1)


@cache
def population(family, t):
    coins, weights = environment(family)
    law = (binom.pmf(np.arange(t + 1)[:, None, None], t, coins) * weights).sum(axis=2).T
    mass = np.empty((2, 2, 2, 2))
    mean = (weights * coins).sum(axis=1)
    for x in (0, 1):
        first = coins if x else 1 - coins
        for action in (0, 1):
            for b in (0, 1):
                second = coins if b else 1 - coins
                if action:
                    mass[x, action, b] = (
                        0.5 * (weights * first).sum(axis=1) * (mean if b else 1 - mean)
                    )
                else:
                    mass[x, action, b] = 0.5 * (weights * first * second).sum(axis=1)
    px = mass.sum(axis=(2, 3))[:, 0]
    raw = mass.sum(axis=-1)
    pb = raw / raw.sum(axis=-1, keepdims=True)
    history_law = (mass @ law) / raw[:, :, :, None]
    oracle = (
        mass * count_kl(law[None, None, None, :, :], history_law[:, :, :, None, :])
    ).sum(axis=(2, 3)) / px[:, None]
    info = information(history_law, pb)
    np.testing.assert_allclose(
        oracle[:, 0] - oracle[:, 1], info[:, 1] - info[:, 0], atol=5e-13
    )
    return px, pb, history_law, oracle, info


def information(laws, responses):
    mean = (laws * responses[:, :, :, None]).sum(axis=2, keepdims=True)
    return (responses * count_kl(laws, mean)).sum(axis=2)


def certificate():
    weights = ((F(7, 12), F(5, 12)), (F(7, 15), F(8, 15)))
    biases = ((F(1, 8), F(7, 8)), (F(1, 2), F(7, 8)))
    mean = [sum(w * p for w, p in zip(ws, ps)) for ws, ps in zip(weights, biases)]
    squared = [
        sum(w * p * p for w, p in zip(ws, ps)) for ws, ps in zip(weights, biases)
    ]
    after_one = [v / u for v, u in zip(squared, mean)]
    after_zero = [(u - v) / (1 - u) for v, u in zip(squared, mean)]
    assert mean == [F(7, 16), F(7, 10)]
    assert after_one == [F(3, 4)] * 2
    assert after_zero == [F(7, 36), F(7, 12)]
    assert [F(49, 160) + (F(157, 160) - F(49, 160)) * p for p in after_zero] == mean
    return {
        "reset": list(map(str, mean)),
        "continue_after_zero": list(map(str, after_zero)),
        "continue_after_one": list(map(str, after_one)),
        "garbling": ["49/160", "157/160"],
    }


def fit_acquisition(hist):
    counts = hist.sum(axis=-1).reshape(2, 2, 2)
    q = (counts + 0.5) / (counts.sum(axis=-1, keepdims=True) + 1)
    # The logged action was an independent fair choice.
    first = (counts.sum(axis=(1, 2)) + 0.5) / (counts.sum() + 1)
    return first, q


def acquisition_score(family, first, q):
    px, pb, *_ = population(family, 1)
    first_loss = float(-px @ np.log(first))
    second_loss = float(-(px[:, None, None] * pb * np.log(q)).sum() / 2)
    return first_loss, second_loss


def costs_for_readout(family, t, laws, estimated_responses):
    _, pb, truth, oracle, _ = population(family, t)
    models = laws.reshape(2, 2, 2, -1)
    estimated = information(models, estimated_responses)
    excess = (pb * count_kl(truth, models)).sum(axis=2)
    return {"gain": estimated[:, 1] - estimated[:, 0], "loss": oracle + excess}


def hist_forecast(family, t, hist, m, responses):
    fitted = (hist + 0.5) / (hist.sum(axis=1, keepdims=True) + (m + 1) / 2)
    u = min(m, t)
    low = fitted @ thinning(m, u)
    ans = costs_for_readout(family, u, low, responses)
    if t > m:
        # After m observations all history-specific histograms use the same
        # half-count conditional process for the remaining report.
        _, pb, p0, old, _ = population(family, m)
        _, _, p1, new, _ = population(family, t)
        adapt = count_kl(p1, kt_counts(t)) - count_kl(p0, kt_counts(m))
        ans["loss"] += new - old + (pb * adapt).sum(axis=2)
    return ans


def serialize(item):
    return {"gain": [float(x) for x in item["gain"]], "loss": item["loss"].tolist()}


def fitting(family, m, seed, n, logs):
    h, k = logs
    cut = 3 * n // 4
    fit = histogram(h[:cut], k[:cut], m)
    val = histogram(h[cut:n], k[cut:n], m)
    assert fit.sum() == cut and val.sum() == n - cut and fit.sum(axis=1).min() > 0
    forecast, responses = fit_acquisition(fit)
    first, second = acquisition_score(family, forecast, responses)
    packed, hfloor, shift = fit_harmonics(fit, val)
    fitted, gfloor, gap = fit_grid(fit, val)
    row = {
        "family": family,
        "seed": seed,
        "m": m,
        "N": n,
        "degree": packed.shape[1],
        "harmonic_floor": hfloor,
        "maximum_shift": float(shift.max()),
        "grid_floor": gfloor,
        "grid_duality_gap": gap,
        "grid_support": [int((w > 0).sum()) for w in fitted],
        "first_nll": first,
        "second_logged_nll": second,
        "panels": {},
    }
    for t in HORIZONS:
        laws = {
            "harmonic": harmonic_law(t, packed.astype(float) / UNIT),
            "grid": grid_law(t, fitted, gfloor),
            "half": np.broadcast_to(kt_counts(t), (8, t + 1)),
        }
        panel = {
            name: serialize(costs_for_readout(family, t, p, responses))
            for name, p in laws.items()
        }
        panel["histogram"] = serialize(hist_forecast(family, t, fit, m, responses))
        row["panels"][str(t)] = panel
    if seed == SEEDS[0] and m == 16 and n == BUDGETS[-1]:
        row["install"] = {
            "harmonic_q15": packed.tolist(),
            "grid_weights": fitted.tolist(),
            "seen": fit.sum(axis=1).tolist(),
            "hist_counts": fit.tolist(),
            "estimated_responses": responses.tolist(),
        }
    return row


def law_oracles():
    ans = {}
    for f in FAMILIES:
        ans[f] = {}
        for t in HORIZONS:
            px, _, _, loss, information_ = population(f, t)
            gain = information_[:, 1] - information_[:, 0]
            ans[f][str(t)] = {
                "px": px.tolist(),
                "gain": gain.tolist(),
                "loss": loss.tolist(),
            }
    return ans


def value(px, matrix, policy, cost):
    return float(px @ (matrix[np.arange(2), policy] + cost * policy))


def evaluation(row, oracle, t, cost, name):
    raw = oracle[row["family"]][str(t)]
    prob = np.array(raw["px"])
    base = np.array(raw["loss"])
    optimal = (np.array(raw["gain"]) > cost + 1e-14).astype(int)
    fixed = min(value(prob, base, np.full(2, a), cost) for a in (0, 1))
    panel = row["panels"][str(t)][name]
    policy = (np.array(panel["gain"]) > cost + 1e-14).astype(int)
    return {
        "fixed": fixed,
        "oracle": value(prob, base, optimal, cost),
        "policy": policy.tolist(),
        "oracle_policy_value": value(prob, base, policy, cost),
        "deployed": value(prob, np.array(panel["loss"]), policy, cost),
        "right": int(np.array_equal(policy, optimal)),
    }


def run():
    data = []
    with threadpool_limits(limits=1):
        for f in FAMILIES:
            for m in (4, 16):
                for seed in SEEDS:
                    logs = calibration_logs(f, m, seed, max(BUDGETS))
                    for n in BUDGETS:
                        data.append(fitting(f, m, seed, n, logs))
    return {
        "unit": "total future excess nats plus reset rent, relative to knowing environment but not the fresh coin",
        "costs": COSTS,
        "oracles": law_oracles(),
        "certificate": certificate(),
        "fits": data,
    }


if __name__ == "__main__":
    from coin_memory import compare

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run(), allow_nan=False))
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched all ordinary-data fits and population decisions.")
    elif args.output:
        # One experiment per line; field names and precision are retained.
        header = {k: v for k, v in result.items() if k != "fits"}
        text = json.dumps(header, indent=2)[:-2] + ',\n  "fits": [\n'
        text += ",\n".join(
            "    " + json.dumps(r, separators=(",", ":")) for r in result["fits"]
        )
        args.output.write_text(text + "\n  ]\n}\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
