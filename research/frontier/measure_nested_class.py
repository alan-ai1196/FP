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


def workload(data, receipt, response_classes=False, posterior=False):
    rows, outputs, _, _, _, raw = frozen(data[:SELECTION_END])
    if posterior:
        from text_partition_posterior import END as upper
        from text_partition_posterior import START as lower
    elif response_classes:
        from text_response_classes import END as upper
        from text_response_classes import REPORT_START as lower
    else:
        lower, upper = REPORT_START, END
        np.testing.assert_array_equal(outputs, receipt["output_ids"])
    ids = np.frombuffer(data, dtype=np.uint16)
    c = rows.common
    obs = c.observe(ids, lower, upper)
    base = -np.log(obs.readout(rows.tables[0]))
    belongs = np.zeros(c.vocab, dtype=bool)
    belongs[outputs] = True
    mass = rows.apply(belongs.astype(float))[obs.query]
    hit = belongs[obs.target]
    arms = {"pooled": (np.frombuffer(rows.base, dtype=np.uint8), 1, base)}
    probes = {}
    old = (
        json.loads(
            Path(__file__).with_name("text_nested_class_result.json").read_text()
        )
        if response_classes
        else receipt
    )
    for name, info in old["installations"].items():
        if posterior and name != "previous":
            continue
        if response_classes and name not in ("previous", "joint"):
            continue
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
        if posterior or (response_classes and name != "raw_cap"):
            continue
        arms[name] = (
            np.frombuffer(m.payload, dtype=np.uint8),
            3 if len(m.active) else 1,
            m.losses(tri, obs),
        )
    if response_classes:
        from text_response_classes import UNIT, ranks

        del arms["pooled"]
        arms["global"] = arms.pop("previous")
        glob_packet, _, glob_loss = arms["global"]
        # Recover the multiplier from the installed global comparator.
        previous = restore(old["installations"]["previous"])
        odds = previous.scalar / 1024
        p = odds * mass / (1 + (odds - 1) * mass)
        ru = ranks(np.array(receipt["early_ids"]), obs.history)
        rv = ranks(np.array(receipt["current_ids"]), obs.query)
        mask = (ru < 8) & (rv < 8)
        if posterior:
            installations = {
                f"{k}/frozen": info
                for k, info in receipt["frozen_installations"].items()
            }
        else:
            installations = {
                k: receipt["installations"][k]
                for k in receipt["alpha_selection"].values()
            }
        for name, info in installations.items():
            packet = bytes.fromhex(info["packet_hex"])
            labels = np.array(info["labels"])
            k = 1 + int(max(labels))
            rates = np.frombuffer(packet[-16 * k :], dtype="<u2").reshape(k, 8)
            prediction = rates[labels[ru[mask]], rv[mask]].astype(float) / UNIT
            loss = glob_loss.copy()
            loss[mask] -= np.where(
                hit[mask],
                np.log(prediction / p[mask]),
                np.log((1 - prediction) / (1 - p[mask])),
            )
            arms[name] = (
                np.frombuffer(glob_packet.tobytes() + packet, dtype=np.uint8),
                8,
                loss,
            )
    for name, (_, _, loss) in arms.items():
        mean = (
            receipt["scores"][name]["all"]["nll"]
            if posterior
            else receipt["mean"][name]["nll"]
        )
        assert abs(loss.mean() - mean) < 2e-10
    shared = (
        ids[lower - 2 : upper],
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


def run(data, receipt, gpu, response_classes=False, posterior=False):
    with threadpool_limits(limits=1):
        shared, arms, probes = workload(
            data, receipt, response_classes or posterior, posterior
        )
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
        default=None,
    )
    study = parser.add_mutually_exclusive_group()
    study.add_argument("--response-classes", action="store_true")
    study.add_argument("--partition-posterior", action="store_true")
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    if args.partition_posterior:
        from text_partition_posterior import load_data as read

        default = "text_partition_posterior_result.json"
    elif args.response_classes:
        from text_response_classes import load_data as read

        default = "text_response_classes_result.json"
    else:
        read, default = load_data, "text_nested_class_result.json"
    receipt = (
        args.receipt if args.receipt is not None else Path(__file__).with_name(default)
    )
    result = run(
        read(args.data_dir),
        json.loads(receipt.read_text(encoding="utf8")),
        args.gpu,
        args.response_classes,
        args.partition_posterior,
    )
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    else:
        print(output, end="")
