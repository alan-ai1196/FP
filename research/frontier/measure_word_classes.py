"""Replay learned word classes and matched raw rows from serialized installations."""

import argparse
import hashlib
import json
import struct
import tempfile
from pathlib import Path

import numpy as np
from causal_state import binary_sizes, compile_libraries
from measure_addresses import measure_cpu, measure_gpu
from packed_trigram import Trigram
from text_addresses import SELECT_END, fit, fit_calibrated_trigram
from text_word_classes import END, FIT_END, REPORT_START, START, load_data
from threadpoolctl import threadpool_limits
from word_classes import CAP, UNIT, Gate, ProbabilityRows


def restore(info):
    return Gate(
        None
        if info["active_ids"] is None
        else np.array(info["active_ids"], dtype=np.uint16),
        np.array(info["output_ids"], dtype=np.uint16),
        np.array(info["odds_units"], dtype=np.uint16),
        info["current_token"],
    )


def add_caches(arms, work, rows, model, name, train, obs):
    packet = model.install(rows)
    fit_active, _ = model.masks(train)
    active, _ = model.masks(obs)
    degree = np.diff(rows.count.indptr)
    probes = np.minimum(degree, len(model.outputs))
    saved = np.bincount(train.query[fit_active], minlength=len(degree)) * probes
    eligible = np.flatnonzero(saved > 0)
    ranked = eligible[np.lexsort((eligible, -saved[eligible]))]
    room = (CAP - model.size(rows) - 2) // 6
    delta = rows.count @ (UNIT * model.weights())
    for k in sorted({min(n, room, len(eligible)) for n in (16, 64, room)}):
        if k <= 0:
            continue
        q = np.sort(ranked[:k])
        fields = bytearray(struct.pack("<H", len(q)))
        for x in q:
            assert delta[x] == int(delta[x])
            fields.extend(struct.pack("<Hi", int(x), int(delta[x])))
        key = f"{name}_cache_{k}"
        arms[key] = (np.frombuffer(packet + fields, dtype=np.uint8), 6, arms[name][2])
        hits = active & np.isin(obs.query, q)
        work[key] = {
            "cache_rows": k,
            "bytes_including_live": model.size(rows) + len(fields),
            "cache_hits": int(hits.sum()),
            "normalizer_probes_avoided": int(probes[obs.query[hits]].sum()),
        }


def workload(data, receipt, cache):
    old = fit(data[:SELECT_END])
    rows = ProbabilityRows(old)
    c = rows.common
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = c.observe(ids, REPORT_START, END)
    losses = -np.log(obs.readout(rows.tables[0]))
    train = c.observe(ids, START, FIT_END) if cache else None
    arms = {}
    lookup_sizes = {}
    for name, info in receipt["installations"].items():
        model = restore(info)
        packet = model.install(rows)
        assert hashlib.sha256(packet).hexdigest() == info["packet_sha256"]
        arms[name] = (
            np.frombuffer(packet, dtype=np.uint8),
            5 if len(model.outputs) else 1,
            losses - model.gain(rows, obs),
        )
        active, _ = model.masks(obs)
        if len(model.outputs):
            degrees = np.diff(rows.count.indptr)[obs.query[active]]
            lookup_sizes[name] = {
                "active": len(degrees),
                "raw_successor_membership_probes": int(
                    degrees[degrees <= len(model.outputs)].sum()
                ),
                "named_output_bigram_probes": int(
                    (degrees > len(model.outputs)).sum() * len(model.outputs)
                ),
            }
        if cache and name in ("multiword", "global"):
            add_caches(arms, lookup_sizes, rows, model, name, train, obs)
    split = START + 3 * (FIT_END - START) // 4
    purchase = c.observe(ids, split, FIT_END)
    val = c.observe(ids, FIT_END, REPORT_START)
    raw = {"historical": old.trigram, "fresh": Trigram(ids[START - 2 : split])}
    for name, info in receipt["raw_installations"].items():
        tri = raw[info["count_source"]]
        m, _ = fit_calibrated_trigram(
            c, [("pooled", rows.tables)], tri, purchase, val, info["cap"]
        )
        assert hashlib.sha256(m.payload).hexdigest() == info["sha256"]
        arms[name] = (
            np.frombuffer(m.payload, dtype=np.uint8),
            3 if len(m.active) else 1,
            m.losses(tri, obs),
        )
    shared = (
        ids[REPORT_START - 2 : END],
        len(obs.target),
        c.counts.astype(np.uint32),
        c.outgoing.astype(np.uint32),
        rows.count.indptr.astype(np.uint32),
        rows.count.indices.astype(np.uint16),
        c.values,
        c.rows.den,
    )
    assert np.array_equal(rows.count.data, c.values)
    for name, (_, _, expected) in arms.items():
        assert (
            abs(expected.mean() - receipt["mean"][name.split("_cache_")[0]]["nll"])
            < 2e-10
        )
    return shared, arms, lookup_sizes


def run(data, receipt, gpu, cache):
    with threadpool_limits(limits=1):
        shared, arms, lookups = workload(data, receipt, cache)
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        src = path / "class.c"
        src.write_text(
            (root / "word_class_score.c")
            .read_text()
            .replace(
                '#include "address_score.c"', (root / "address_score.c").read_text()
            ),
            encoding="utf8",
        )
        (lib,) = compile_libraries(path, ("address",), src)
        report = {
            "positions": shared[1],
            "raw_lookup_bytes": sum(a.nbytes for a in shared[2:-1]),
            "normalizer_work": lookups,
            "binary": binary_sizes(lib),
            "cpu_ms": measure_cpu(lib, shared, arms, "class_stream"),
        }
        if gpu:
            report["gpu"] = measure_gpu(src, shared, arms, "class_batch")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument(
        "--receipt", type=Path, default=root / "text_word_classes_result.json"
    )
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="benchmark query masses bought from the training context frequencies",
    )
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = run(
        load_data(args.data_dir),
        json.loads(args.receipt.read_text(encoding="utf8")),
        args.gpu,
        args.cache,
    )
    s = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(s, encoding="utf8")
    else:
        print(s, end="")
