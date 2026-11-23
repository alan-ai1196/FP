"""Learn a two-stage state from the future agreement of a purchased signal and target."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np

REGISTRATION = "54506ee"
SEEDS = (257, 509, 1021, 2039)
BUDGETS = (384, 3072, 24576)
COSTS = (1 / 8, 9 / 32)
BITS = np.array([(0, *rest) for rest in product(range(2), repeat=7)], dtype=np.uint8)
PLANS = np.array(list(product(range(3), repeat=3)), dtype=np.uint8)
ROWS, COLS = np.indices((8, 8))
SEEN = (COLS - ROWS) % 8
SEEN = (SEEN != 0) & (SEEN != 3)
TASKS = np.arange(3)
UNIT = 65536
CONSTANT, NARROW, WIDE, RAW, FACTOR = range(5)


def population(seed):
    rng = np.random.default_rng([seed, 0])
    rows, cols = rng.permutation(8), rng.permutation(8)
    route = ((rows[:, None] ^ cols[None, :])[:, :, None] >> TASKS) & 1
    return 0.5 + 0.375 * (route[:, :, :, None] == np.arange(2))


def episodes(seed, law):
    rng = np.random.default_rng([seed, 1])
    n = BUDGETS[-1]
    pairs = rng.choice(np.flatnonzero(SEEN), n)
    u, v = pairs // 8, pairs % 8
    j = rng.integers(3, size=n)
    a = rng.integers(3, size=n)
    y = rng.integers(2, size=n)
    z = np.full(n, 2)
    b = a != 0
    z[b] = y[b] ^ (rng.random(b.sum()) >= law[u[b], v[b], j[b], a[b] - 1])
    return u, v, j, a, z, y


def purchased(log, n):
    u, v, j, a, z, y = (x[:n] for x in log)
    b = a != 0
    index = ((8 * u[b] + v[b]) * 3 + j[b]) * 2 + a[b] - 1
    counts = np.bincount(index, minlength=384).reshape(8, 8, 3, 2)
    hits = np.bincount(index, weights=(y[b] == z[b]), minlength=384).reshape(
        counts.shape
    )
    return counts, hits


def rank_model(n, h):
    row_code = np.zeros(8, dtype=np.uint8)
    col_code = np.zeros(8, dtype=np.uint8)
    high = []
    for j in range(3):
        best = -np.inf
        choice = None
        for p in (0.625, 0.75, 0.875, 0.9375):
            gains = h[:, :, j] * np.log(2 * p) + (n[:, :, j] - h[:, :, j]) * np.log(
                2 * (1 - p)
            )
            score0 = (1 - BITS) @ gains[:, :, 0] + BITS @ gains[:, :, 1]
            score1 = (1 - BITS) @ gains[:, :, 1] + BITS @ gains[:, :, 0]
            values = np.maximum(score0, score1).sum(axis=1)
            r = int(np.flatnonzero(values >= values.max() - 1e-10)[0])
            if values[r] > best + 1e-10:
                best = values[r]
                choice = (p, BITS[r], (score1[r] > score0[r] + 1e-10).astype(np.uint8))
        p, r, c = choice
        row_code |= r << j
        col_code |= c << j
        high.append(p)
    x = ((row_code[:, None] ^ col_code[None, :])[:, :, None] >> TASKS) & 1
    model = 0.5 + (np.array(high)[None, None, :, None] - 0.5) * (
        x[:, :, :, None] == np.arange(2)
    )
    return model, (row_code, col_code)


def packed(values, width):
    result = bytearray((len(values) * width + 7) // 8)
    for i, value in enumerate(values):
        v = int(value)
        assert 0 <= v < 1 << width
        bit = i * width
        result[bit // 8] |= (v << (bit % 8)) & 255
        if bit % 8 + width > 8:
            result[bit // 8 + 1] |= v >> (8 - bit % 8)
    return bytes(result)


@dataclass
class Controller:
    kind: int
    states: np.ndarray
    policy: np.ndarray
    tables: bytes
    peak_bits: int
    final_bits: int

    @property
    def packet(self):
        header = bytes((self.kind, len(self.policy), 3, 1))
        return header + self.tables + packed(self.policy.ravel(), 2)


def make(kind, states, policy, tables, peak, final):
    return Controller(
        kind,
        states.astype(int),
        np.asarray(policy, dtype=np.uint8),
        tables,
        peak,
        final,
    )


def control_tables(predict, cost):
    # Each possible final state has one choice for each later task.
    outcomes = np.concatenate([np.full((8, 8, 3, 1), 0.5), predict - cost], axis=3)
    scores = np.stack(
        [sum(outcomes[:, :, j, a] for j, a in enumerate(plan)) for plan in PLANS]
    )
    wide_best = narrow_best = -np.inf
    wide = narrow = None
    groups = np.stack([1 - BITS, BITS], axis=1)
    by_group = np.einsum("ghu,puv->ghpv", groups, scores)
    for i in range(len(PLANS)):
        for k in range(i, len(PLANS)):
            value = np.maximum(scores[i], scores[k]).sum()
            if value > wide_best + 1e-10:
                wide_best = value
                states = (scores[k] > scores[i] + 1e-12).astype(np.uint8)
                wide = make(
                    WIDE, states, PLANS[[i, k]], packed(states.ravel(), 1), 3, 1
                )
            value = np.maximum(by_group[:, :, i], by_group[:, :, k]).sum(axis=(1, 2))
            idx = int(np.flatnonzero(value >= value.max() - 1e-10)[0])
            if value[idx] > narrow_best + 1e-10:
                narrow_best = value[idx]
                bits = BITS[idx]
                second = (by_group[idx, :, k] > by_group[idx, :, i] + 1e-12).astype(
                    np.uint8
                )
                narrow = make(
                    NARROW,
                    second[bits, :],
                    PLANS[[i, k]],
                    packed(bits, 1) + packed(second.ravel(), 1),
                    1,
                    1,
                )
    constant = make(
        CONSTANT,
        np.zeros((8, 8)),
        outcomes.mean(axis=(0, 1)).argmax(axis=-1)[None, :],
        b"",
        0,
        0,
    )
    direct = make(
        RAW, ROWS * 8 + COLS, outcomes.argmax(axis=-1).reshape(64, 3), b"", 6, 6
    )
    return {
        "constant": constant,
        "one_then_one": narrow,
        "three_then_one": wide,
        "raw_pair": direct,
    }


def state_means(model, controller):
    means = np.full((len(controller.policy), 3, 2), 0.5)
    for s in np.unique(controller.states):
        means[s] = model[controller.states == s].mean(axis=0)
    return means


def conventional_factor(model, codes, cost):
    rows, cols = codes
    states = rows[:, None] ^ cols[None, :]
    dummy = make(
        FACTOR, states, np.zeros((8, 3)), packed(rows, 3) + packed(cols, 3), 3, 3
    )
    means = state_means(model, dummy)
    values = np.concatenate([np.full((8, 3, 1), 0.5), means - cost], axis=-1)
    dummy.policy = values.argmax(axis=-1).astype(np.uint8)
    return dummy


def quantize(p):
    return np.clip(np.rint(p * UNIT), 1, UNIT - 1).astype("<u2")


def score(truth, model, m, cost):
    means = state_means(model, m)
    allrates = np.concatenate([np.full((len(means), 3, 1), 0.5), means], axis=-1)
    chosen = allrates[np.arange(len(means))[:, None], TASKS, m.policy]
    wire = quantize(chosen)
    a = m.policy[m.states]
    true = np.concatenate([np.full((8, 8, 3, 1), 0.5), truth], axis=-1)
    accuracy = np.take_along_axis(true, a[:, :, :, None], axis=-1)[:, :, :, 0]
    prob = wire[m.states].astype(float) / UNIT
    fixed = quantize(means)[m.states].astype(float) / UNIT

    def nll(t, p):
        return -t * np.log(p) - (1 - t) * np.log1p(-p)

    values = {
        "payoff": accuracy - cost * (a != 0),
        "buy": a != 0,
        "nll": nll(accuracy, prob),
        "common_probe_nll": nll(truth, fixed).mean(axis=-1),
    }
    panels = (np.ones((8, 8), dtype=bool), ~SEEN)
    data = {
        f"{key}_{which}": float(array[mask].mean())
        for key, array in values.items()
        for which, mask in zip(("all", "unseen"), panels, strict=True)
    }
    packet = m.packet
    info = {
        "action_bytes": len(packet),
        "prediction_bytes": len(packet) + wire.nbytes,
        "first_bits": (0, 1, 3, 3, 3)[m.kind],
        "peak_bits": m.peak_bits,
        "final_bits": m.final_bits,
        "action_hex": packet.hex(),
        "q16_hex": wire.tobytes().hex(),
        "prediction_sha256": hashlib.sha256(packet + wire.tobytes()).hexdigest(),
    }
    return data, info


def experiment():
    all_metrics = {}
    installations = {}
    bought = {}
    factor_recovery = {}
    for seed in SEEDS:
        truth = population(seed)
        log = episodes(seed, truth)
        for n in (0, *BUDGETS):
            counts, hits = purchased(log, n)
            bought[f"{seed}/{n}"] = int(counts.sum())
            rank, codes = rank_model(counts, hits)
            errors = rank.argmax(axis=3) != truth.argmax(axis=3)
            factor_recovery[f"{seed}/{n}"] = {
                "route_errors_of_192": int(errors.sum()),
                "withheld_errors_of_48": int(errors[~SEEN].sum()),
                "agreement_by_task": rank.max(axis=(0, 1, 3)).tolist(),
            }
            for name, model in (
                ("tabular", (hits + 0.5) / (counts + 1)),
                ("rank_one", rank),
            ):
                for c in COSTS:
                    controllers = control_tables(model, c)
                    if name == "rank_one":
                        controllers["factored"] = conventional_factor(model, codes, c)
                    for arm, m in controllers.items():
                        data, info = score(truth, model, m, c)
                        key = f"{n}/{name}/{c}/{arm}"
                        all_metrics.setdefault(key, []).append(data)
                        if n == BUDGETS[-1]:
                            installations[f"{seed}/{name}/{c}/{arm}"] = info
    summary = {
        k: {
            field: round(float(np.mean([p[field] for p in vals])), 9)
            for field in vals[0]
        }
        for k, vals in all_metrics.items()
    }
    individual = {
        k: [round(p["payoff_unseen"], 9) for p in vals]
        for k, vals in all_metrics.items()
        if k.startswith(str(BUDGETS[-1]) + "/")
    }
    return {
        "registration": REGISTRATION,
        "seeds": SEEDS,
        "budgets": BUDGETS,
        "costs": COSTS,
        "eligible_pairs": int(SEEN.sum()),
        "purchased_episodes": bought,
        "fitted_factor_recovery": factor_recovery,
        "mean": summary,
        "largest_budget_unseen_payoff_by_seed": individual,
        "largest_budget_installations": installations,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    data = json.dumps(experiment(), indent=2) + "\n"
    if args.check:
        assert json.loads(data) == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(data, encoding="utf8")
    elif not args.check:
        print(data, end="")
