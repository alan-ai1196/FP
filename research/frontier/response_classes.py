"""Infer which opaque row names share future sensor response laws."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

import controlled_sensing as cs
import numpy as np
from scipy.special import betaln

REGISTRATION = "28e5a3d"
SEEDS = (3011, 4001, 5003, 6007)
LAWS = ("xor", "switch", "address")


def partitions(prefix=(0,)):
    if len(prefix) == 8:
        yield prefix
    else:
        for label in range(min(3, max(prefix) + 1) + 1):
            yield from partitions((*prefix, label))


LABELS = np.array(list(partitions()), dtype=np.uint8)
SIZES = LABELS.max(axis=1) + 1
SUBSETS = (np.arange(256)[:, None] >> np.arange(8)) & 1
BLOCKS = np.stack([(LABELS == k) @ (1 << np.arange(8)) for k in range(4)], axis=1)
LOG_COUNTS = np.log(np.bincount(SIZES)[1:])[SIZES - 1]


def environment(seed, family):
    rng = np.random.default_rng([seed, 0])
    u, v = rng.permutation(8), rng.permutation(8)
    row = ((u[:, None] >> cs.TASKS) & 1)[:, None, :]
    col = ((v[:, None] >> cs.TASKS) & 1)[None, :, :]
    if family == "xor":
        x = row ^ col
    elif family == "switch":
        x = (row & np.roll(col, -1, axis=2)) ^ col
    else:
        assert family == "address"
        x = np.where(np.roll(col, -2, axis=2), np.roll(row, -1, axis=2), row) ^ col
    return 0.5 + 0.375 * (x[:, :, :, None] == np.arange(2))


def observations(logged, n):
    u, v, j, a, z, y = (arr[:n] for arr in logged)
    buy = a != 0
    keys = (((8 * u[buy] + v[buy]) * 3 + j[buy]) * 2 + a[buy] - 1) * 2 + z[buy]
    shape = (8, 8, 3, 2, 2)
    count = np.bincount(keys, minlength=768).reshape(shape)
    hits = np.bincount(keys, weights=(z[buy] == y[buy]), minlength=768).reshape(shape)
    return count, hits


def true_labels(route, j):
    ids = {}
    return tuple(ids.setdefault(tuple(row), len(ids)) for row in route[:, :, j])


def anchored(route, labels, u, v):
    return set(route[np.logical_and(labels == labels[u], cs.SEEN[:, v]), v])


def identified(route, labels):
    valid = np.ones(len(labels), dtype=bool)
    for u in range(8):
        for w in range(u):
            if np.any((route[u] != route[w]) & cs.SEEN[u] & cs.SEEN[w]):
                valid &= labels[:, u] != labels[:, w]
    feasible = labels[valid]
    assert len(feasible)
    # Count the occupied response parameters in each compatible row partition.
    used = np.stack([(feasible == k).astype(int) @ cs.SEEN for k in range(4)], axis=1)
    dim = (used > 0).sum(axis=(1, 2))
    answers = {}
    for name, candidates in (
        ("all", feasible),
        ("min_dimension", feasible[dim == min(dim)]),
    ):
        forced = 0
        witness = None
        for u, v in zip(*np.where(~cs.SEEN), strict=True):
            values = set()
            examples = {}
            for part in candidates:
                arrived = anchored(route, part, u, v)
                assert len(arrived) <= 1
                for outcome in arrived or (0, 1):
                    values.add(outcome)
                    examples[int(outcome)] = part.tolist()
                if len(values) == 2:
                    break
            forced += len(values) == 1
            if len(values) == 2 and witness is None:
                witness = {
                    "row": int(u),
                    "column": int(v),
                    "completion_partitions": examples,
                }
        answers[name] = {
            "partitions": len(candidates),
            "identified_of_16": forced,
            "ambiguous_example": witness,
        }
    return answers


def fit(count, hits, oracle=None):
    """Group predictive Bernoulli events. Final dimension is one or two observed-bit channels."""
    predict = np.empty_like(hits)
    selections = []
    for j in range(3):
        n = (SUBSETS @ count[:, :, j].reshape(8, -1)).reshape(256, 8, 2, -1)
        h = (SUBSETS @ hits[:, :, j].reshape(8, -1)).reshape(n.shape)
        if oracle is None:
            evidence = (betaln(h + 0.5, n - h + 0.5) - betaln(0.5, 0.5)).sum(
                axis=(1, 2, 3)
            )
            scores = evidence[BLOCKS].sum(axis=1) - LOG_COUNTS
            # Enumeration is lexicographic. Floating residuals from regrouping equal terms average below this tolerance.
            index = int(np.flatnonzero(scores >= scores.max() - 1e-9)[0])
            labels = LABELS[index]
            masks = BLOCKS[index]
        else:
            labels = np.array(oracle[j])
            masks = np.array(
                [
                    sum(1 << u for u in range(8) if labels[u] == k)
                    for k in range(max(labels) + 1)
                ]
            )
        cells = masks[labels]
        predict[:, :, j] = (h[cells] + 0.5) / (n[cells] + 1)
        selections.append(labels.tolist())
    return predict, selections


def installation(conditional, m):
    channels = conditional.shape[-1]
    means = np.full((len(m.policy), 3, 2, channels), 0.5)
    for s in np.unique(m.states):
        means[s] = conditional[m.states == s].mean(axis=0)
    forecast = np.concatenate(
        [np.full((len(means), 3, 1, channels), 0.5), means], axis=2
    )
    selected = cs.quantize(forecast[np.arange(len(means))[:, None], cs.TASKS, m.policy])
    action = bytearray(m.packet)
    action[3] = channels
    wire = bytes(action) + selected.tobytes()
    return means, selected, wire


def class_packet(labels, policy, selected):
    """Store one action and conditional readout per acquired class and later column."""
    starts = []
    members = np.asarray(labels, dtype=np.uint8)
    actions = []
    probs = []
    for j, row_labels in enumerate(members):
        starts.append(len(actions) // 8)
        for block in range(int(max(row_labels)) + 1):
            rows = np.flatnonzero(row_labels == block)
            indices = 8 * rows[:, None] + np.arange(8)
            block_actions = policy[indices, j]
            block_probs = selected[indices, j]
            assert np.all(block_actions == block_actions[0]) and np.all(
                block_probs == block_probs[0]
            )
            actions.extend(block_actions[0])
            probs.extend(block_probs[0])
    header = bytes((5, len(actions), 3, selected.shape[-1]))
    routing = bytes(starts) + cs.packed(members.ravel(), 2)
    decision = header + routing + cs.packed(actions, 2)
    return decision + np.asarray(probs, dtype="<u2").tobytes(), len(decision)


def metrics(truth, conditional, m, cost, verify=None, labels=None):
    means, selected, wire = installation(conditional, m)
    if verify is not None:
        verify(wire, m, selected)
    actions = m.policy[m.states]
    true = np.concatenate([np.full((8, 8, 3, 1), 0.5), truth], axis=3)
    observed = np.take_along_axis(true, actions[:, :, :, None], axis=3)
    chosen = selected[m.states].astype(float) / cs.UNIT
    forced = cs.quantize(means)[m.states].astype(float) / cs.UNIT

    def nll(t, p):
        return -t * np.log(p) - (1 - t) * np.log1p(-p)

    values = {
        "forced_nll": nll(truth[:, :, :, :, None], forced).mean(axis=(3, 4)),
        "payoff": observed[:, :, :, 0] - cost * (actions != 0),
        "on_policy_nll": nll(observed, chosen).mean(axis=3),
        "buy": actions != 0,
    }
    result = {
        f"{k}_{which}": float(arr[panel].mean())
        for k, arr in values.items()
        for which, panel in (
            ("all", np.ones((8, 8), dtype=bool)),
            ("withheld", ~cs.SEEN),
        )
    }
    result["action_bytes"] = len(wire) - selected.nbytes
    result["selected_prediction_bytes"] = len(wire)
    if labels is not None and m.kind == cs.RAW:
        compact, size = class_packet(labels, m.policy, selected)
        result["profile_action_bytes"] = size
        result["profile_prediction_bytes"] = len(compact)
        if verify is not None:
            verify(compact, m, selected)
    return result


def run(verify=None):
    assert np.bincount(SIZES).tolist() == [0, 1, 127, 966, 1701]
    all_values = defaultdict(list)
    details = {}
    ambiguity = {}
    purchases = {}
    seeds_raw = {}
    for seed, family in product(SEEDS, LAWS):
        truth = environment(seed, family)
        route = truth.argmax(axis=3)
        known = [true_labels(route, j) for j in range(3)]
        logged = cs.episodes(seed, truth)
        for j in range(3):
            for k in {max(known[j]) + 1, 4}:
                ambiguity[f"{seed}/{family}/{j}/{k}"] = identified(
                    route[:, :, j], LABELS[SIZES <= k]
                )
        for budget in (0, *cs.BUDGETS):
            key = f"{seed}/{family}/{budget}"
            count, hits = observations(logged, budget)
            purchases[key] = int(count.sum())
            summed = count.sum(axis=4, keepdims=True), hits.sum(axis=4, keepdims=True)
            free, free_labels = fit(count, hits)
            sym, sym_labels = fit(*summed)
            given, _ = fit(count, hits, known)
            rank, codes = cs.rank_model(
                summed[0][:, :, :, :, 0], summed[1][:, :, :, :, 0]
            )
            tab = (summed[1] + 0.5) / (summed[0] + 1)
            for name, forecast, labels in (
                ("free", free, free_labels),
                ("symmetric", sym, sym_labels),
                ("given_partition", given, known),
                ("rank_one", rank[:, :, :, :, None], None),
                ("tabular", tab, None),
            ):
                if labels is not None:
                    details[f"{key}/{name}"] = {
                        "classes": [max(l) + 1 for l in labels],
                        "exact_partition": [
                            tuple(l) == tuple(k)
                            for l, k in zip(labels, known, strict=True)
                        ],
                    }
                avg = forecast.mean(axis=4)
                for cost in cs.COSTS:
                    arms = cs.control_tables(avg, cost)
                    if name == "rank_one":
                        arms["factored"] = cs.conventional_factor(avg, codes, cost)
                    for arm, m in arms.items():
                        val = metrics(
                            truth,
                            forecast,
                            m,
                            cost,
                            verify if budget == cs.BUDGETS[-1] else None,
                            labels,
                        )
                        all_values[f"{family}/{budget}/{name}/{cost}/{arm}"].append(val)
                        if (
                            arm == "raw_pair"
                            and budget in cs.BUDGETS
                            and cost == cs.COSTS[0]
                        ):
                            seeds_raw[f"{key}/{name}"] = {
                                k: round(val[k], 9)
                                for k in (
                                    "forced_nll_all",
                                    "forced_nll_withheld",
                                    "payoff_withheld",
                                )
                            }
    avg = {
        k: {s: round(float(np.mean([x[s] for x in vs])), 9) for s in vs[0]}
        for k, vs in all_values.items()
    }
    return {
        "registration": REGISTRATION,
        "partitions_by_size": dict(Counter(map(int, SIZES))),
        "seeds": SEEDS,
        "budgets": cs.BUDGETS,
        "costs": cs.COSTS,
        "purchases": purchases,
        "fitted_partitions": details,
        "population_identification": ambiguity,
        "raw_pair_by_seed": seeds_raw,
        "mean": avg,
    }


def section(name, value):
    """Keep per-fit records together in the machine-readable receipt."""
    if isinstance(value, dict):
        rows = (
            f"    {json.dumps(str(k))}: {json.dumps(v, separators=(',', ':'))}"
            for k, v in value.items()
        )
        body = "{\n" + ",\n".join(rows) + "\n  }"
    else:
        body = json.dumps(value)
    return f"  {json.dumps(name)}: {body}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("verification requires assertions")
    data = run()
    result = "{\n" + ",\n".join(section(k, v) for k, v in data.items()) + "\n}\n"
    if args.check:
        assert json.loads(result) == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(result, encoding="utf8")
    elif not args.check:
        print(result, end="")
