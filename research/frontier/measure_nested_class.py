"""Verify every observed loss in the packed sequential and GPU class-exception scorers."""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np
from causal_state import binary_sizes, compile_libraries
from measure_addresses import measure_cpu, measure_gpu
from text_nested_class import (
    END,
    REPORT_START,
    SELECTION_END,
    frozen,
    load_data,
    restore,
)
from threadpoolctl import threadpool_limits


def workload(data, receipt):
    rows, outputs, _, _, _, raw = frozen(data[:SELECTION_END])
    np.testing.assert_array_equal(outputs, receipt["output_ids"])
    ids = np.frombuffer(data, dtype=np.uint16)
    c = rows.common
    obs = c.observe(ids, REPORT_START, END)
    base = -np.log(obs.readout(rows.tables[0]))
    belongs = np.zeros(c.vocab, dtype=bool)
    belongs[outputs] = True
    mass = rows.apply(belongs.astype(float))[obs.query]
    hit = belongs[obs.target]
    arms = {"pooled": (np.frombuffer(rows.base, dtype=np.uint8), 1, base)}
    probes = {}
    for name, info in receipt["installations"].items():
        model = restore(info)
        packet = model.pack(rows, outputs)
        assert len(packet) + model.live() == info["bytes"]
        assert hashlib.sha256(packet).hexdigest() == info["sha256"]
        arms[name] = (
            np.frombuffer(packet, dtype=np.uint8),
            7,
            base - model.gain(obs, mass, hit),
        )
        active = model.odds(obs) != 1
        degrees = np.diff(rows.count.indptr)[obs.query[active]]
        probes[name] = {
            "nonneutral_odds": int(active.sum()),
            "normalizer_membership_probes": int(degrees[degrees <= len(outputs)].sum()),
            "normalizer_count_probes": int(
                (degrees > len(outputs)).sum() * len(outputs)
            ),
        }
    for name, (tri, m, _) in raw.items():
        arms[name] = (
            np.frombuffer(m.payload, dtype=np.uint8),
            3 if len(m.active) else 1,
            m.losses(tri, obs),
        )
    for name, (_, _, loss) in arms.items():
        assert abs(loss.mean() - receipt["mean"][name]["nll"]) < 2e-10
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
    return shared, arms, probes


def run(data, receipt, gpu):
    with threadpool_limits(limits=1):
        shared, arms, probes = workload(data, receipt)
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        src = path / "nested.c"
        src.write_text(
            (root / "nested_class_score.c")
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
            "output_bytes": shared[1] * 8,
            "normalizer_work": probes,
            "binary": binary_sizes(lib),
            "cpu_ms": measure_cpu(lib, shared, arms, "nested_stream"),
        }
        if gpu:
            report["gpu"] = measure_gpu(src, shared, arms, "nested_batch")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path(__file__).with_name("text_nested_class_result.json"),
    )
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = run(
        load_data(args.data_dir),
        json.loads(args.receipt.read_text(encoding="utf8")),
        args.gpu,
    )
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    else:
        print(output, end="")
