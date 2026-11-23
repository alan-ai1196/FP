"""Learn both sides of a normalized full-vocabulary correction from raw targets."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from packed_trigram import Trigram
from text import VOCAB, git_json, tape
from text_addresses import CAL, RENT, SELECT_END, fit, fit_calibrated_trigram
from text_update_subspace import END as START
from text_update_subspace import SHA as OLD_SHA
from threadpoolctl import threadpool_limits
from word_classes import (
    CAP,
    EMPTY,
    HEADER,
    FitData,
    ProbabilityRows,
    choose,
    empty_gate,
    free_candidates,
)

FIT_END = START + 262144
REPORT_START = FIT_END + CAL
END = REPORT_START + 4 * CAL
SHA = "d55772903cb35c2f51911676685855a72293f5cb5e0e5912cbb4d77358616d1c"
REGISTRATION = "0f45141"


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == OLD_SHA
    )
    return data


def report_starts():
    return range(REPORT_START, END, CAL)


def initials(rows):
    out = [None, np.flatnonzero(rows.common.seed)]
    for seed in (17, 29):
        rng = np.random.Generator(np.random.PCG64(seed))
        out.append(np.flatnonzero(rng.integers(2, size=VOCAB, dtype=np.uint8)))
    return out


def class_selection(rows, train, val):
    chosen = {}
    cache = {}
    train_best = {n: (0.0, EMPTY) for n in (64, 256)}
    counts = {}

    def consider(family, model):
        size = model.size(rows)
        if size > CAP:
            return
        key = model.signature()
        if key not in cache:
            cache[key] = (-model.gain(rows, val).mean() + 8 * RENT * size / CAL, size)
        criterion = cache[key]
        counts[family] = counts.get(family, 0) + 1
        if family not in chosen or criterion < chosen[family][0]:
            chosen[family] = (criterion, model)

    for family in ("pooled", "multiword", "singleton", "global", "current", "free"):
        consider(family, empty_gate())
    options = initials(rows)
    for variant in ("earlier", "global", "current"):
        data = FitData(rows, train, variant == "current")
        active = [data.active(v) for v in options]
        residual = [a.y - rows.adjoint(a.q) for a in active]
        for rho in (0.5, 0.75, 1.5, 2.0):
            for kb in (1, 32, 256):
                seeds = set()
                for a, r in zip(active, residual, strict=True):
                    seeds.add((int(np.argmax(np.sign(rho - 1) * r)),))
                    seeds.add(
                        tuple(choose(data.linearized(a, EMPTY, rho), kb, data.price))
                    )
                for ka in (0,) if variant == "global" else (64, 256):
                    for seed in sorted(seeds):
                        model, value, _ = data.fit_sets(
                            np.asarray(seed, dtype=np.uint16),
                            ka,
                            kb,
                            rho,
                            variant == "global",
                        )
                        family = (
                            ("singleton" if kb == 1 else "multiword")
                            if variant == "earlier"
                            else variant
                        )
                        consider(family, model)
                        if variant == "earlier" and value > train_best[ka][0]:
                            train_best[ka] = (value, model.types)
    data = FitData(rows, train)
    rank = np.lexsort((np.arange(VOCAB), -rows.common.counts))
    for ka, (_, types) in train_best.items():
        largest = (CAP - len(rows.base) - HEADER.size - 2 * ka - 1) // 4
        for start in (types, np.sort(rank[:ka]).astype(np.uint16)):
            for cap_outputs in sorted({min(k, largest) for k in (32, 128, largest)}):
                for model in free_candidates(data, start, ka, cap_outputs):
                    consider("free", model)
    return {k: r[1] for k, r in chosen.items()}, counts, len(cache)


def train_models(data):
    assert len(data) == REPORT_START
    old = fit(data[:SELECT_END])
    rows = ProbabilityRows(old)
    tokens = np.frombuffer(data, dtype=np.uint16)
    train = rows.common.observe(tokens, START, FIT_END)
    val = rows.common.observe(tokens, FIT_END, REPORT_START)
    models, counts, distinct = class_selection(rows, train, val)
    purchase_begin = START + (FIT_END - START) * 3 // 4
    purchase = rows.common.observe(tokens, purchase_begin, FIT_END)
    trigrams = [old.trigram, Trigram(tokens[START - 2 : purchase_begin])]
    raw = {}
    for tag, cap in (("raw_matched", models["multiword"].size(rows)), ("raw_cap", CAP)):
        opts = []
        for label, tri in zip(("historical", "fresh"), trigrams, strict=True):
            model, meta = fit_calibrated_trigram(
                rows.common, [("pooled", rows.tables)], tri, purchase, val, cap
            )
            losses = model.losses(tri, val)
            opts.append(
                (
                    losses.mean() + RENT * model.bits / CAL,
                    model.bits,
                    label,
                    tri,
                    model,
                    meta,
                )
            )
        _, _, label, tri, model, meta = min(opts, key=lambda e: e[:3])
        raw[tag] = (tri, model, dict(meta, count_source=label, cap=cap))
    return (
        rows,
        models,
        raw,
        {"candidate_visits": counts, "distinct_installations_evaluated": distinct},
    )


def report_model(rows, m):
    packet = m.install(rows)
    return {
        "bytes": m.size(rows),
        "carried_bytes": m.live(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
        "active_ids": None if m.types is None else list(map(int, m.types)),
        "output_ids": list(map(int, m.outputs)),
        "odds_units": list(map(int, m.units)),
        "current_token": m.current,
    }


def experiment(data):
    rows, models, raw, acq = train_models(data[:REPORT_START])
    tokens = np.frombuffer(data, dtype=np.uint16)
    receipt = {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "fit_targets": FIT_END - START,
        "selection_targets": CAL,
        "first_report_targets": list(report_starts()),
        "pooled_bytes": len(rows.base),
        "acquisition": acq,
        "installations": {k: report_model(rows, v) for k, v in models.items()},
        "raw_installations": {k: v[2] for k, v in raw.items()},
        "blocks": [],
    }

    def score(start):
        obs = rows.common.observe(tokens, start, start + CAL)
        base = -np.log(obs.readout(rows.tables[0]))
        block = {}

        def record(name, loss, size):
            block[name] = {
                "nll": round(float(loss.mean()), 10),
                "priced": round(float(loss.mean() + 8 * RENT * size / CAL), 10),
                "anchor_subpanel_nll": round(float(loss[:4096].mean()), 10),
            }

        for name, m in models.items():
            loss = base - m.gain(rows, obs)
            record(name, loss, m.size(rows))
            a, b = m.masks(obs)
            block[name]["active_predictions"] = int(a.sum()) if len(m.outputs) else 0
            block[name]["active_output_hits"] = int((a & b).sum())
        for name, (tri, m, _) in raw.items():
            record(name, m.losses(tri, obs), m.bits // 8)
        return block

    receipt["selection"] = score(FIT_END)
    for start in report_starts():
        receipt["blocks"].append(score(start))
    receipt["mean"] = {
        name: {
            key: round(float(np.mean([b[name][key] for b in receipt["blocks"]])), 10)
            for key in ("nll", "priced", "anchor_subpanel_nll")
        }
        for name in receipt["selection"]
    }
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    with threadpool_limits(limits=1):
        result = experiment(load_data(args.data_dir))
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    elif not args.check:
        print(json.dumps(result, indent=2))
