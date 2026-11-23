"""Measure earlier-token exceptions after calibrating a frozen output class."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from nested_class import CURRENT, EARLIER, PAIR, Exceptions, Model, fit_models
from packed_trigram import Trigram
from text import git_json, tape
from text_addresses import CAL, RENT, SELECT_END, fit, fit_calibrated_trigram
from text_word_classes import END as REPORT_START
from text_word_classes import FIT_END, START
from text_word_classes import REPORT_START as SELECTION_END
from text_word_classes import SHA as OLD_SHA
from threadpoolctl import threadpool_limits
from word_classes import Gate, ProbabilityRows

REGISTRATION = "ae87e2f"
END = REPORT_START + 2 * CAL
SHA = "39f62de0a38e9163d92ca3b4381256447289ffe84963dd2946307fb6ed4e397e"
PARENT = Path(__file__).with_name("text_word_classes_result.json")
KINDS = {EARLIER: "earlier", CURRENT: "current", PAIR: "pair"}
CODE = {v: k for k, v in KINDS.items()}


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(
            np.asarray(data[:REPORT_START], dtype="<u2").tobytes()
        ).hexdigest()
        == OLD_SHA
    )
    return data


def report_starts():
    return range(REPORT_START, END, CAL)


def frozen(data):
    assert len(data) == SELECTION_END
    old = fit(data[:SELECT_END])
    rows = ProbabilityRows(old)
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = rows.common.observe(ids, START, FIT_END)
    val = rows.common.observe(ids, FIT_END, SELECTION_END)
    previous = json.loads(PARENT.read_text(encoding="utf8"))
    src = previous["installations"]["global"]
    outputs = np.array(src["output_ids"], dtype=np.uint16)
    ref = Gate(None, outputs, np.array(src["odds_units"], dtype=np.uint16))
    assert hashlib.sha256(ref.install(rows)).hexdigest() == src["packet_sha256"]
    split = START + 3 * (FIT_END - START) // 4
    purchase = rows.common.observe(ids, split, FIT_END)
    counts = {"historical": old.trigram, "fresh": Trigram(ids[START - 2 : split])}
    raw = {}
    for name, info in previous["raw_installations"].items():
        tri = counts[info["count_source"]]
        m, _ = fit_calibrated_trigram(
            rows.common, [("pooled", rows.tables)], tri, purchase, val, info["cap"]
        )
        assert hashlib.sha256(m.payload).hexdigest() == info["sha256"]
        raw[name] = (tri, m, info)
    return rows, outputs, int(ref.units[0]), obs, val, raw


def describe(model, rows, outputs):
    packet = model.pack(rows, outputs)
    return {
        "scalar_q10": model.scalar,
        "installed_bytes": len(packet),
        "live_bytes": model.live(),
        "bytes": model.size(rows, outputs),
        "sha256": hashlib.sha256(packet).hexdigest(),
        "tables": [
            {"kind": KINDS[t.kind], "keys": t.keys.tolist(), "codes": t.codes.tolist()}
            for t in model.tables
        ],
    }


def restore(info):
    tables = []
    for t in info["tables"]:
        kind = CODE[t["kind"]]
        keys = np.array(t["keys"], dtype=np.uint32 if kind == PAIR else np.uint16)
        tables.append(Exceptions(kind, keys, np.array(t["codes"], dtype=np.uint8)))
    return Model(info["scalar_q10"], tuple(tables))


def experiment(data):
    rows, outputs, reference, train, val, raw = frozen(data[:SELECTION_END])
    mass, belongs, models = fit_models(rows, outputs, train, val, reference)
    ids = np.frombuffer(data, dtype=np.uint16)

    def score(start):
        obs = rows.common.observe(ids, start, start + CAL)
        base = -np.log(obs.readout(rows.tables[0]))
        block = {}

        def record(name, loss, size):
            block[name] = {
                "nll": round(float(loss.mean()), 10),
                "priced": round(float(loss.mean() + 8 * RENT * size / CAL), 10),
                "anchor_subpanel_nll": round(float(loss[:4096].mean()), 10),
            }

        record("pooled", base, len(rows.base))
        for name, m in models.items():
            loss = base - m.gain(obs, mass[obs.query], belongs[obs.target])
            record(name, loss, m.size(rows, outputs))
            act = [t.read(obs) != 1 for t in m.tables]
            block[name]["exception_visits"] = [int(a.sum()) for a in act]
            block[name]["joint_exception_visits"] = (
                int(np.logical_and.reduce(act).sum()) if len(act) == 2 else None
            )
        for name, (tri, m, _) in raw.items():
            record(name, m.losses(tri, obs), m.bits // 8)
        return block

    selection = score(FIT_END)

    def best_current(names):
        return min(
            names,
            key=lambda k: (selection[k]["priced"], models[k].size(rows, outputs), k),
        )

    refitted = best_current(("current", "twice_current", "global"))
    current = best_current((refitted, "previous"))
    blocks = [score(start) for start in report_starts()]
    return {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "fit_targets": [START, FIT_END],
        "selection_targets": [FIT_END, SELECTION_END],
        "first_report_targets": list(report_starts()),
        "targets_per_block": CAL,
        "pooled_bytes": len(rows.base),
        "output_ids": outputs.tolist(),
        "installations": {
            name: describe(m, rows, outputs) for name, m in models.items()
        },
        "raw_installations": {name: info for name, (_, _, info) in raw.items()},
        "best_refitted_current_on_selection": refitted,
        "best_current_on_selection": current,
        "selection": selection,
        "blocks": blocks,
        "mean": {
            name: {
                k: round(float(np.mean([b[name][k] for b in blocks])), 10)
                for k in ("nll", "priced", "anchor_subpanel_nll")
            }
            for name in selection
        },
    }


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
