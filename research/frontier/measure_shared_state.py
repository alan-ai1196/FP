"""Replay every budget and installation from its packed bytes on native CPU and CUDA."""

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
from causal_state import binary_sizes, compile_libraries
from measure_addresses import measure_cpu, measure_gpu
from shared_readout import Model
from text_shared_state import (
    REPORT_START,
    REPORT_STOP,
    load_data,
    source_gain,
    train_study,
)
from threadpoolctl import threadpool_limits


def workload(data):
    study = train_study(data[:REPORT_START])
    base = study.base
    common = base.common
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = common.observe(ids, REPORT_START, REPORT_STOP)
    groups = base.group_data(ids, REPORT_START, REPORT_STOP)
    degrees = np.bincount((common.keys >> 16).astype(np.intp), minlength=common.vocab)
    offset = np.concatenate(([0], np.cumsum(degrees))).astype(np.uint32)
    arrays = (
        ids[REPORT_START - 2 : REPORT_STOP],
        len(obs.target),
        common.counts.astype(np.uint32),
        common.outgoing.astype(np.uint32),
        offset,
        (common.keys & 65535).astype(np.uint16),
        common.values,
        common.rows.den,
    )
    loss = -np.log(obs.readout(base.mass))
    gain = source_gain(base, obs, study.source)
    arms = {}

    def add(name, model, src, total, group_ids):
        packet, _ = model.install(base.payload, group_ids, src)
        arms[name] = np.frombuffer(packet, dtype=np.uint8), 0, total

    empty = Model((), ())
    add("pooled", empty, None, loss, ())
    add(
        "constant_source",
        empty,
        study.constant,
        loss - source_gain(base, obs, study.constant),
        (),
    )
    add("source", empty, study.source, loss - gain, ())
    for n, models in study.models.items():
        for name, model in models.items():
            d = loss.copy()
            for g, changes in zip(groups, model.target_gains(groups), strict=True):
                d[g.position] -= changes
            add(f"{n}_{name}_destination", model, None, d, base.groups)
            add(f"{n}_{name}_joint", model, study.source, d - gain, base.groups)
    return arrays, arms


def bench(data, gpu):
    with threadpool_limits(limits=1):
        arrays, arms = workload(data)
    parent = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        source = directory / "shared.c"
        source.write_text(
            (parent / "shared_state_score.c")
            .read_text(encoding="utf8")
            .replace(
                '#include "address_score.c"',
                (parent / "address_score.c").read_text(encoding="utf8"),
            ),
            encoding="utf8",
        )
        (lib,) = compile_libraries(directory, ("address",), source)
        result = {
            "targets": arrays[1],
            "raw_lookup_bytes": sum(a.nbytes for a in arrays[2:-1]),
            "output_bytes": 8 * arrays[1],
            "binary": binary_sizes(lib),
            "cpu_ms": measure_cpu(lib, arrays, arms, "shared_stream"),
        }
        if gpu:
            result["gpu"] = measure_gpu(source, arrays, arms, "shared_batch")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    report = json.dumps(bench(load_data(args.data_dir), args.gpu), indent=2) + "\n"
    if args.write:
        args.write.write_text(report, encoding="utf8")
    else:
        print(report, end="")
