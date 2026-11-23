"""Frozen text priors learn hidden action names from purchased one-bit rewards."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from text import git_json, tape
from text_shared_state import REPORT_HASH, REPORT_START, REPORT_STOP, train_study
from threadpoolctl import threadpool_limits
from ticket_policy import (
    CHECKPOINTS,
    PERMS,
    K,
    acquire,
    bounded_action_metrics,
    floor_law,
    menu,
    ridge_features,
)

START = REPORT_STOP
ACQUISITION_END = START + 3 * 32768
BLOCK = 65536
END = ACQUISITION_END + 3 * 4 * BLOCK
SHA = "29e518850593e8ae3d094695a0d08e5b4a8ab61d3aa53bf4fa6943927e749c19"
REGISTRATION = "f912975"
REPLICATES = 8
EPSILONS = (0, 0.25, 1)
METHODS = (
    "uniform",
    "pooled",
    "global",
    "reuse",
    "frequency",
    "rank_one",
    "separate",
    "raw",
    "reward_ridge",
)
METRICS = ("buy_rate", "realized_reward", "integrated_reward", "one_choice_accuracy")


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == REPORT_HASH
    )
    return data


@dataclass
class Context:
    history: np.ndarray
    query: np.ndarray


class Environment:
    def __init__(self, triples, member):
        labels = member[triples[:, 2]]
        positions = np.flatnonzero(labels >= 0)
        self.context = Context(
            triples[positions, 0].copy(), triples[positions, 1].copy()
        )
        self.block = positions // BLOCK
        self._word = labels[positions].copy()

    def purchase_channel(self, mapping):
        # This is the only outcome-bearing object passed to the training routine.
        def bit(i, j):
            return bool(self._word[i] == mapping[j])

        return bit

    def reporting_winner(self, mapping):
        return np.argsort(mapping)[self._word]


def probabilities(study, group, context):
    base = study.base
    u, q = context.history, context.query
    p = base.conditional[group][q]
    priors = {"uniform": np.full_like(p, 1 / K), "pooled": floor_law(p)}
    for name, model in study.models[262144].items():
        head = model.heads[group]
        address = model.maps[group]
        odds = head.odds[0 if address is None else address.codes[u]]
        fitted = p * odds
        fitted /= fitted.sum(axis=1, keepdims=True)
        if model.raw is not None:
            raw = model.raw
            keys = (group << 32) | (u.astype(np.int64) << 16) | q
            i = np.minimum(np.searchsorted(raw.keys, keys), len(raw.keys) - 1)
            mask = raw.keys[i] == keys
            counts = raw.counts[i[mask]]
            fitted[mask] = (counts + raw.tau * fitted[mask]) / (
                counts.sum(axis=1) + raw.tau
            )[:, None]
        priors[name] = floor_law(fitted)
    priors["reward_ridge"] = priors["pooled"]
    for d in priors.values():
        assert np.max(np.abs(d.sum(axis=1) - 1)) < 1e-12
    return priors, ridge_features(p)


def random_stream(namespace, replicate, group):
    return np.random.Generator(np.random.PCG64([namespace, replicate, group]))


def generate_groups(study, triples):
    groups = []
    for g, member in enumerate(study.base.members):
        env = Environment(triples, member)
        priors, features = probabilities(study, g, env.context)
        groups.append((env, priors, features))
    return groups


def block_sums(metrics, blocks):
    return np.array([np.bincount(blocks, weights=m, minlength=4) for m in metrics]).T


def r(x):
    return round(float(x), 9)


def summary(data):
    study = train_study(data[:REPORT_START])
    tokens = np.frombuffer(data, dtype=np.uint16)
    adaptation = generate_groups(study, tokens[START:ACQUISITION_END].reshape(-1, 3))
    reporting = generate_groups(study, tokens[ACQUISITION_END:END].reshape(-1, 3))
    shape = (len(EPSILONS), len(CHECKPOINTS), len(METHODS), REPLICATES, 4)
    scores = np.zeros((*shape, len(METRICS)))
    map_scores = np.zeros((*shape, len(METRICS)))
    informed = np.zeros((len(METHODS) - 1, REPLICATES, 4, len(METRICS)))
    stats = np.zeros((*shape[:-1], 3), dtype=np.int64)
    nblocks = sum(np.bincount(item[0].block, minlength=4) for item in reporting)
    train_counts = [len(item[0].context.query) for item in adaptation]
    for rep in range(REPLICATES):
        for g, ((env, priors, features), (test, holdout, test_x)) in enumerate(
            zip(adaptation, reporting, strict=True)
        ):
            mapping = random_stream(0, rep, g).permutation(K)
            winner = test.reporting_winner(mapping)
            count = len(winner)
            names, prices = menu(random_stream(2, rep, g), count, 0)
            purchase = env.purchase_channel(mapping)
            for mi, method in enumerate(METHODS):
                p = holdout[method]
                is_ridge = method == "reward_ridge"
                if not is_ridge:
                    metrics = bounded_action_metrics(
                        p[:, mapping], names, prices, winner
                    )
                    informed[mi, rep] += block_sums(metrics, test.block)
                for ei, eps in enumerate(EPSILONS):
                    js, cs = menu(random_stream(1, rep, g), CHECKPOINTS[-1], eps)
                    snapshots = acquire(
                        priors[method][: len(js)],
                        features[: len(js)],
                        js,
                        cs,
                        purchase,
                        is_ridge,
                    )
                    for bi, b in enumerate(CHECKPOINTS):
                        policy, buys, hits = snapshots[b]
                        dst = ei, bi, mi, rep
                        prediction = policy.probabilities(p, test_x)
                        metrics = bounded_action_metrics(
                            prediction, names, prices, winner
                        )
                        scores[dst] += block_sums(metrics, test.block)
                        stats[dst][0] += buys
                        stats[dst][1] += hits
                        if not is_ridge:
                            chosen = PERMS[policy.map_index]
                            stats[dst][2] += int(np.array_equal(chosen, mapping))
                            metrics = bounded_action_metrics(
                                p[:, chosen], names, prices, winner
                            )
                            map_scores[dst] += block_sums(metrics, test.block)

    total = REPLICATES * nblocks.sum()
    # Uniform reports stay uninformative under every feedback and exploration history.
    assert np.allclose(scores[:, :, 0], scores[0, 0, 0], rtol=0, atol=1e-10)
    assert np.array_equal(
        stats[2, :, :, :, 0],
        np.broadcast_to(
            (2 * np.array(CHECKPOINTS))[:, None, None], stats[2, :, :, :, 0].shape
        ),
    )
    result = {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "acquisition_triples": 32768,
        "acquisition_group_opportunities": train_counts,
        "report_first_raw_indices": [ACQUISITION_END + 3 * BLOCK * b for b in range(4)],
        "report_triples_per_block": BLOCK,
        "group_opportunities_by_block": [
            np.bincount(item[0].block, minlength=4).tolist() for item in reporting
        ],
        "replicates": REPLICATES,
        "columns": [
            *METRICS,
            "mean_purchases_across_two_groups",
            "mean_hits_across_two_groups",
            "correct_map_count_out_of_16",
            "map_realized_reward",
            "map_integrated_reward",
            "map_one_choice_accuracy",
        ],
        "informed_columns": list(METRICS),
        "informed": {
            name: [r(x) for x in informed[i].sum(axis=(0, 1)) / total]
            for i, name in enumerate(METHODS[:-1])
        },
        "menus": {},
        "primary_paired_columns": [
            "mean_realized_difference",
            "mean_integrated_difference",
            "mean_one_choice_difference",
            "realized_difference_by_environment",
            "integrated_difference_by_environment",
            "one_choice_difference_by_environment",
            "realized_difference_by_block",
            "integrated_difference_by_block",
            "one_choice_difference_by_block",
        ],
        "primary_paired": {},
    }
    for ei, eps in enumerate(EPSILONS):
        panels = result["menus"][str(eps)] = {}
        for bi, b in enumerate(CHECKPOINTS):
            panel = panels[str(b)] = {}
            for mi, name in enumerate(METHODS):
                m = scores[ei, bi, mi].sum(axis=(0, 1)) / total
                s = stats[ei, bi, mi].sum(axis=0)
                ma = map_scores[ei, bi, mi].sum(axis=(0, 1)) / total
                extra = (
                    [int(s[2]), *(r(v) for v in ma[1:])]
                    if name != "reward_ridge"
                    else [None] * 4
                )
                panel[name] = [
                    *map(r, m),
                    r(s[0] / REPLICATES),
                    r(s[1] / REPLICATES),
                    *extra,
                ]
            if eps != 0.25:
                continue
            paired = result["primary_paired"][str(b)] = {}
            for left, right in (
                ("reuse", "global"),
                ("rank_one", "reuse"),
                ("reuse", "reward_ridge"),
                ("rank_one", "reward_ridge"),
            ):
                diff = (
                    scores[ei, bi, METHODS.index(left)]
                    - scores[ei, bi, METHODS.index(right)]
                )
                envdiff = diff.sum(axis=1) / nblocks.sum()
                blockdiff = diff.mean(axis=0) / nblocks[:, None]
                paired[left + "_minus_" + right] = [
                    *(r(x) for x in envdiff.mean(axis=0)[1:]),
                    *[[r(x) for x in envdiff[:, j]] for j in (1, 2, 3)],
                    *[[r(x) for x in blockdiff[:, j]] for j in (1, 2, 3)],
                ]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    with threadpool_limits(limits=1):
        result = summary(load_data(args.data_dir))
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    elif not args.check:
        print(json.dumps(result, indent=2))
