"""Prospectively transfer a raw-token history state to two disjoint within-group decisions."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
from output_correction import END, END_HASH, base_backoff
from packed_trigram import lookup, pair_ids
from shared_readout import (
    MULTIPLIERS,
    Address,
    Group,
    Model,
    RawRows,
    address,
    alternate,
    assignment_scores,
    binary_gains,
    choose_codes,
    fit_head,
    frequency_address,
    initial_codes,
)
from text import VOCAB, git_json, tape
from text_addresses import CAL, READOUT_END, RENT, SELECT_END, fit, serialize

SOURCE = 286
SOURCE_FIT_END = END + 3 * 262144
ADAPT_START = SOURCE_FIT_END + 3 * 65536
REPORT_START = ADAPT_START + 262144
REPORT_STOP = REPORT_START + 4 * CAL
REPORT_HASH = "cfe4d44db84b293759bce050f541c976de1a9f19556bf1359fd63a6b5b2593fa"
SUBPANEL = 4096
REGISTRATION = "45f3338"


def load_data(directory):
    anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in anchor["results"] if e["case"] == "ngram"
    )
    data = tape(
        dict(src, bytes_read=2 * REPORT_STOP, prefix_sha256=REPORT_HASH), directory
    )
    assert (
        hashlib.sha256(np.asarray(data[:END], dtype="<u2").tobytes()).hexdigest()
        == END_HASH
    )
    return data


def report_starts():
    return range(REPORT_START, REPORT_STOP, CAL)


class Base:
    def __init__(self, prefix):
        prior = fit(prefix)
        self.common, self.mass = prior.common, prior.constant[0]
        self.payload = serialize(self.common, prior.constant)
        ranked = np.lexsort((np.arange(VOCAB), -self.common.counts))
        names = ranked[ranked != SOURCE][:8]
        self.groups = (names[::2], names[1::2])
        query = np.arange(VOCAB, dtype=np.uint16)
        backoff = base_backoff(self.common, self.mass)

        def probability(j):
            key = pair_ids(query, np.full(VOCAB, j, dtype=np.uint16))
            counts = lookup(self.common.keys, self.common.values, key)
            return (counts + 64 * backoff[j]) / (self.common.outgoing + 64)

        self.source_prob = probability(SOURCE)
        self.members = []
        self.conditional = []
        for ids in self.groups:
            mapping = np.full(VOCAB, -1, dtype=np.int8)
            mapping[ids] = np.arange(4)
            self.members.append(mapping)
            raw = np.stack([probability(j) for j in ids], axis=1)
            self.conditional.append(raw / raw.sum(axis=1, keepdims=True))

    def group_data(self, tokens, start, end):
        u, q, y = (
            tokens[start - 2 : end - 2],
            tokens[start - 1 : end - 1],
            tokens[start:end],
        )
        groups = []
        for ids, member, d in zip(
            self.groups, self.members, self.conditional, strict=True
        ):
            label = member[y]
            idx = np.flatnonzero(label >= 0)
            groups.append(Group(ids, idx, u[idx], q[idx], label[idx], d[q[idx]]))
        return groups

    def source_panel(self, tokens, lo, hi):
        triples = tokens[lo:hi].reshape(-1, 3)
        # These three arrays are the entire interface to the source-state learner.
        return (
            triples[:, 0].copy(),
            self.source_prob[triples[:, 1]],
            triples[:, 2] == SOURCE,
        )


def source_fit(base, train_panel, selection):
    u, p, hit = train_panel
    n = len(hit)
    gains = binary_gains(p, hit)
    default = int(np.argmax(gains.sum(axis=1)))
    constant = address(np.full(VOCAB, default, dtype=np.uint8))
    proposals = [(constant, 0, "constant")]
    for beta in (0, 1, 2):
        scores = assignment_scores(u, gains, default, beta)
        for rule, rent in (("sparse", 20 * RENT * n / CAL), ("dense", 0.0)):
            proposals.append((address(choose_codes(scores, default, rent)), beta, rule))
    vu, vp, vhit = selection
    val_gain = binary_gains(vp, vhit)
    val_base = -np.where(vhit, np.log(vp), np.log1p(-vp)).mean()

    def criterion(item):
        a, beta, _ = item
        loss = val_base - val_gain[a.codes[vu], np.arange(len(vu))].mean()
        size = Model((), ()).size(base.payload, (), a)
        return loss + 8 * RENT * size / CAL, size, beta

    chosen = min(proposals, key=criterion)
    a, beta, rule = chosen
    return (
        a,
        constant,
        {
            "default_multiplier": float(MULTIPLIERS[default]),
            "beta": beta,
            "rule": rule,
            "training_examples": n,
            "training_source_hits": int(hit.sum()),
            "selection_examples": len(vu),
            "selection_hits": int(vhit.sum()),
            "selection_binary_priced_nll": round(float(criterion(chosen)[0]), 10),
            "constant_selection_binary_priced_nll": round(
                float(criterion(proposals[0])[0]), 10
            ),
            "type_counts": np.bincount(a.codes, minlength=9).tolist(),
            "map_bytes": len(a.payload),
            "sha256": hashlib.sha256(a.payload).hexdigest(),
        },
    )


def counts_for_rows(groups):
    keys = []
    for i, g in enumerate(groups):
        key = (i << 32) | (g.history.astype(np.int64) << 16) | g.query
        keys.append((key << 2) | g.label)
    return np.concatenate(keys)


def raw_options(
    base, global_model, original_keys, train_half, purchase, maximum, purchase_n
):
    keys, count = np.unique(
        np.concatenate((original_keys, counts_for_rows(train_half))), return_counts=True
    )
    rows, indices = np.unique(keys >> 2, return_inverse=True)
    assert count.max() <= 65535
    matrix = np.zeros((len(rows), 4), dtype=np.uint16)
    matrix[indices, keys & 3] = count
    available = maximum - global_model.size(base.payload, base.groups) - 2
    options = [global_model]
    for tau in (1, 8, 32):
        gains = np.zeros(len(rows))
        for i, (g, h) in enumerate(zip(purchase, global_model.heads, strict=True)):
            key = (i << 32) | (g.history.astype(np.int64) << 16) | g.query
            p = np.minimum(np.searchsorted(rows, key), len(rows) - 1)
            present = rows[p] == key
            fitted = g.prob * h.odds[0]
            observed = fitted[g.index, g.label] / fitted.sum(axis=1)
            r = matrix[p]
            gain = np.log(
                (r[g.index, g.label] / observed + tau) / (r.sum(axis=1) + tau)
            )
            gains += np.bincount(p[present], weights=gain[present], minlength=len(rows))
        net = gains - RENT * 8 * 13 * purchase_n / CAL
        ranked = np.lexsort((rows, -net))
        selected = np.sort(ranked[net[ranked] > 0][: max(0, available // 13)])
        if len(selected):
            raw = RawRows(tau, rows[selected], matrix[selected])
            options.append(Model(global_model.maps, global_model.heads, raw))
    return options


def fit_destinations(base, tokens, n, source, original_keys):
    start = ADAPT_START
    split = start + 3 * n // 4
    train = base.group_data(tokens, start, split)
    validation = base.group_data(tokens, split, start + n)
    global_heads = tuple(fit_head(g, None, 0) for g in train)
    pooled = Model((None, None), global_heads)
    frequency = frequency_address(base.common.counts)

    def shared(a):
        return Model(
            (a, a),
            tuple(
                fit_head(g, a.codes, 1, h)
                for g, h in zip(train, global_heads, strict=True)
            ),
        )

    reuse = shared(source)
    sizes = n // 4

    def order(model):
        gain = sum(a.sum() for a in model.target_gains(validation))
        size = model.size(base.payload, base.groups, source)
        return -gain / sizes + 8 * RENT * size / CAL, size

    rank = []
    separate = [[], []]
    for penalty in (0.5, 2.0, 6.0):
        for i, g in enumerate(train):
            init = initial_codes(g, penalty)
            a, heads = alternate(train, init, global_heads, 2, penalty)
            rank.append(
                (Model((a, a), heads), {"penalty": penalty, "initial_group": i})
            )
            a, heads = alternate([g], init, [global_heads[i]], 1, penalty)
            separate[i].append((a, heads[0], penalty))
    ranks = min(rank, key=lambda item: order(item[0]))
    pairs = []
    for l, r in product(*separate):
        pairs.append((Model((l[0], r[0]), (l[1], r[1])), [l[2], r[2]]))
    sep = min(pairs, key=lambda item: order(item[0]))
    raw = raw_options(
        base,
        pooled,
        original_keys,
        base.group_data(tokens, start, start + n // 2),
        base.group_data(tokens, start + n // 2, split),
        reuse.size(base.payload, base.groups),
        n // 4,
    )
    chosen_raw = min(raw, key=order)
    models = {
        "global": pooled,
        "reuse": reuse,
        "frequency": shared(frequency),
        "rank_one": ranks[0],
        "separate": sep[0],
        "raw": chosen_raw,
    }
    detail = {
        "fit_and_validation_raw": [3 * n // 4, n // 4],
        "fit_group_events": [len(g.label) for g in train],
        "validation_group_events": [len(g.label) for g in validation],
        "rank_one_selection": ranks[1],
        "separate_penalties": sep[1],
        "raw_rows": len(chosen_raw.raw.keys) if chosen_raw.raw else 0,
        "raw_tau": chosen_raw.raw.tau if chosen_raw.raw else None,
        "raw_standalone_cap": reuse.size(base.payload, base.groups),
    }
    return models, detail


@dataclass
class Study:
    base: Base
    source: Address
    constant: Address
    models: dict
    info: dict


def train_study(prefix):
    assert len(prefix) == REPORT_START
    base = Base(prefix[:SELECT_END])
    tokens = np.frombuffer(prefix, dtype=np.uint16)
    source, constant, source_info = source_fit(
        base,
        base.source_panel(tokens, END, SOURCE_FIT_END),
        base.source_panel(tokens, SOURCE_FIT_END, ADAPT_START),
    )
    original_keys = counts_for_rows(base.group_data(tokens, 2, READOUT_END))
    models, details = {}, {}
    for n in (16384, 262144):
        models[n], details[str(n)] = fit_destinations(
            base, tokens, n, source, original_keys
        )
    return Study(
        base, source, constant, models, {"source": source_info, "destination": details}
    )


def source_gain(base, obs, address):
    rho = MULTIPLIERS[address.codes[obs.history]]
    p = base.source_prob[obs.query]
    return (obs.target == SOURCE) * np.log(rho) - np.log1p((rho - 1) * p)


def rounded(x):
    return round(float(x), 10)


def experiment(data):
    study = train_study(data[:REPORT_START])
    base, source = study.base, study.source
    tokens = np.frombuffer(data, dtype=np.uint16)
    result = {
        "registration": REGISTRATION,
        "prefix_sha256": REPORT_HASH,
        "first_targets": list(report_starts()),
        "source_token": SOURCE,
        "destination_tokens": [list(map(int, g)) for g in base.groups],
        "common_pooled_bytes": len(base.payload),
        "acquisition": study.info,
        "source_blocks": [],
        "adaptation": {},
    }
    for n, models in study.models.items():
        installs = {}
        for k, m in models.items():
            standalone, live = m.install(base.payload, base.groups)
            joint, jlive = m.install(base.payload, base.groups, source)
            installs[k] = {
                "destination_bytes": len(standalone) + live,
                "joint_bytes": len(joint) + jlive,
                "joint_live_bytes": jlive,
                "joint_sha256": hashlib.sha256(joint).hexdigest(),
            }
        result["adaptation"][str(n)] = {"installations": installs, "blocks": []}
    for start in report_starts():
        obs = base.common.observe(tokens, start, start + CAL)
        loss = -np.log(obs.readout(base.mass))
        gain = source_gain(base, obs, source)
        c_gain = source_gain(base, obs, study.constant)
        raw_groups = base.group_data(tokens, start, start + CAL)
        binary = np.where(
            obs.target == SOURCE,
            -np.log(base.source_prob[obs.query]),
            -np.log1p(-base.source_prob[obs.query]),
        )
        result["source_blocks"].append(
            {
                "pooled_nll": rounded(loss.mean()),
                "source_only_nll": rounded((loss - gain).mean()),
                "source_binary_nll": rounded((binary - gain).mean()),
                "constant_source_binary_nll": rounded((binary - c_gain).mean()),
                "base_binary_nll": rounded(binary.mean()),
                "source_subpanel": rounded((loss - gain)[:SUBPANEL].mean()),
                "group_events": [len(g.label) for g in raw_groups],
            }
        )
        for n, models in study.models.items():
            dest = result["adaptation"][str(n)]
            block = {}
            for name, model in models.items():
                group_gain = model.target_gains(raw_groups)
                change = np.zeros(CAL)
                conditionals = []
                for g, a in zip(raw_groups, group_gain, strict=True):
                    change[g.position] = a
                    conditionals.append(
                        rounded((-np.log(g.prob[g.index, g.label]) - a).mean())
                    )
                separate = loss - change
                joint = separate - gain
                size = dest["installations"][name]
                block[name] = {
                    "within_group_nll": conditionals,
                    "destination_nll": rounded(separate.mean()),
                    "destination_priced": rounded(
                        separate.mean() + 8 * RENT * size["destination_bytes"] / CAL
                    ),
                    "joint_nll": rounded(joint.mean()),
                    "joint_priced": rounded(
                        joint.mean() + 8 * RENT * size["joint_bytes"] / CAL
                    ),
                    "joint_subpanel_nll": rounded(joint[:SUBPANEL].mean()),
                }
            dest["blocks"].append(block)
    for dest in result["adaptation"].values():
        blocks = dest["blocks"]
        dest["mean"] = {
            k: {
                metric: rounded(np.mean([b[k][metric] for b in blocks]))
                for metric in (
                    "destination_nll",
                    "destination_priced",
                    "joint_nll",
                    "joint_priced",
                    "joint_subpanel_nll",
                )
            }
            for k in blocks[0]
        }
        counts = np.array([b["group_events"] for b in result["source_blocks"]])
        for k, row in dest["mean"].items():
            conditionals = np.array([b[k]["within_group_nll"] for b in blocks])
            row["within_group_nll"] = [
                rounded(v)
                for v in (counts * conditionals).sum(axis=0) / counts.sum(axis=0)
            ]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        receipt = experiment(load_data(args.data_dir))
    if args.check:
        assert receipt == json.loads(args.check.read_text(encoding="utf8"))
    text = json.dumps(receipt, indent=2) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf8")
    elif not args.check:
        print(text, end="")
