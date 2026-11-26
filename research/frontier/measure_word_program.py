"""Replay the frozen three-stage word predictor with matched fused CUDA scorers."""

import argparse
import hashlib
import json
import time
from pathlib import Path

import cupy as cp
import numpy as np
from joint_word_value import ClassMass
from lexical_switch import tokens
from reuse_word_value import HERE, G, Prior
from text import VOCAB
from threadpoolctl import threadpool_limits
from word_value import Base
from word_value_readers import NODES, REPORTS, N, Program, Tape, decode

REGISTRATION = "e6c4af2"
MODES = (
    "base_score",
    "group_fp32",
    "group_mixed",
    "all_states_fp32",
    "all_states_mixed",
    "reachable_fp32",
    "reachable_mixed",
    "reachable_u16",
    "on_demand",
    "packed_program",
)


def weights(total, types):
    inv = np.divide(1.0, total, out=np.zeros(len(total)), where=total > 0)
    back = np.where(total > 0, 0.9 * types * inv, 1.0)
    return np.asarray(np.stack((inv, back), axis=1), dtype=np.float32)


def point_tables(base):
    kn = base.kn
    high, total = base.bg.ab
    triple, counts = base.bg.aby
    lower, nlower = kn.bigram
    assert counts.max() <= 65535 and nlower.max() <= 65535 and high.max() < 2**32
    high_types = kn.higher_types[1]
    assert np.array_equal(kn.higher_types[0], high)
    return {
        "contexts": high.astype(np.uint32),
        "high_ptr": np.r_[0, np.cumsum(high_types)].astype(np.uint32),
        "high_y": (triple % VOCAB).astype(np.uint16),
        "high_count": counts.astype(np.uint16),
        "high_weights": weights(total, high_types),
        "low_ptr": np.r_[0, np.cumsum(kn.lower_types)].astype(np.uint32),
        "low_y": (lower % VOCAB).astype(np.uint16),
        "low_count": nlower.astype(np.uint16),
        "low_weights": weights(kn.lower_total, kn.lower_types),
        "lexical": np.stack((kn.unigram, base.lexical), axis=1).astype(np.float32),
    }


def read_heads():
    r = json.loads((HERE / "word_value_readers_result.json").read_text())
    infos = {
        cut: r["models"][str(cut)][r["selected"][str(cut)]["all_priced"]["model"]]
        for cut in NODES
    }
    assert all(s["method"] == "sign" and len(s["atoms"]) == 1 for s in infos.values())
    return {cut: decode(s) for cut, s in infos.items()}, sum(
        s["bits"] for s in infos.values()
    )


def packed_program(base):
    prior = Prior().spec
    study = json.loads((HERE / "reuse_word_value_result.json").read_text())
    grow = study["models"][study["selected"]["either_priced"]["model"]]
    read = json.loads((HERE / "word_value_readers_result.json").read_text())
    atoms = grow["atoms"]
    assert (prior["outputs"], prior["inputs"], prior["lag"]) == (12, 64, 1)
    assert grow["inputs"] == 16 and grow["lag"] == 2 and len(atoms) == 2
    word_tables = list(dict.fromkeys(a["w"] for a in atoms if a["w"] is not None))
    heads = list(dict.fromkeys(a["s"] for a in atoms if a["s"] != prior["s"]))
    assert len(word_tables) == 1 and len(heads) == 2
    value, width = 0, 0

    def put(x, n):
        nonlocal value, width
        assert -(1 << (n - 1)) <= int(x) < (1 << n)
        value |= (int(x) & ((1 << n) - 1)) << width
        width += n

    def mask(s):
        for c in s:
            put(c == "-", 1)

    # Family, output-size, input-size and lag selects precede the first table.
    for x, n in ((3, 3), (1, 1), (0, 1), (0, 2)):
        put(x, n)
    for bias in prior["bias_q12"]:
        put(bias, 14)
    mask(prior["z"])
    put(prior["beta_q12"], 14)
    mask(prior["s"][:-1])
    assert width == 266 and prior["s"][-1] == "+"
    # Family, size, lag, operation count, two dictionary sizes and spare bits.
    for x, n in ((3, 3), (0, 1), (0, 2), (2, 4), (1, 4), (2, 4), (0, 2)):
        put(x, n)
    for table in word_tables + heads:
        assert table[-1] == "+"
        mask(table[:-1])
    for a in atoms:
        put(("constant", "bit", "main", "product").index(a["op"]), 2)
        put(a["q12"], 14)
        put(0 if a["w"] is None else word_tables.index(a["w"]) + 1, 4)
        put(0 if a["s"] == prior["s"] else heads.index(a["s"]) + 1, 4)
    assert width == 374
    for cut in NODES:
        s = read["models"][str(cut)][read["selected"][str(cut)]["all_priced"]["model"]]
        assert s["method"] == "sign" and len(s["atoms"]) == 1
        a = s["atoms"][0]
        put(1, 7)
        put(("one", "a", "b", "c").index(a["feature"]), 2)
        put(a["beta_q12"], 14)
        assert a["s"][-1] == "+"
        mask(a["s"][:-1])
    assert width == 444
    names = np.asarray(base.bg.names[:64], dtype="<u2").tobytes()
    return np.frombuffer(
        names + value.to_bytes((width + 7) // 8, "little"), dtype=np.uint8
    )


class Compiled:
    def __init__(self, base, groups, program, heads):
        j = np.arange(37)
        root = program.logits[:, np.minimum(j, G)]
        layers = [root]
        for cut in NODES:
            table = np.zeros((4, 37))
            table[:, cut:] = heads[cut][:, np.minimum(j[cut:] - cut, G)]
            layers.append(table)
        self.shifts = sum(layers)
        self.packet = packed_program(base)
        self.factors = np.exp(np.stack(layers, axis=1))
        ranks = np.minimum(base.bg.bins, 64).astype(np.uint8)
        self.head_tables = {
            "ranks": ranks,
            "first_bit": (program.z > 0).astype(np.uint8),
            "second_bit": (program.w > 0).astype(np.uint8),
            "shifts": self.shifts.astype(np.float32),
        }
        q = groups.rows
        h = len(groups.keys)
        full = np.empty((len(q), 4, 3), dtype=np.float64)
        p1 = q[:, 12:].sum(axis=1)
        p2 = q[:, 24:].sum(axis=1)
        for s, f in enumerate(self.factors):
            root = np.log((q @ f[0]) / q.sum(axis=1))
            first = root + np.log((q[:, 12:] @ f[1, 12:]) / p1)
            full[:, s] = np.stack(
                (root, first, first + np.log((q[:, 24:] @ f[2, 24:]) / p2)), axis=1
            )
        a, b = np.divmod(groups.keys, VOCAB)
        latest = (program.z[ranks] > 0).astype(int)
        older = (program.w[np.minimum(ranks, 16)] > 0).astype(int)
        state = 2 * latest[b] + older[a]
        high = full[np.arange(h), state]
        low = full[h + np.arange(VOCAB)[:, None], 2 * latest[:, None] + np.arange(2)]
        reachable = np.vstack((high, low.reshape(-1, 3)))
        state_rows = np.r_[state, (2 * latest[:, None] + np.arange(2)).ravel()]
        self.scale = np.empty((4, 3, 2), dtype=np.float32)
        self.codes = np.empty(reachable.shape, dtype=np.uint16)
        largest_error = 0.0
        for s in range(4):
            subset = state_rows == s
            target = reachable[subset]
            offset = target.min(axis=0).astype(np.float32)
            step = np.maximum((target.max(axis=0) - offset) / 65535, 1e-12).astype(
                np.float32
            )
            self.scale[s, :, 0], self.scale[s, :, 1] = offset, step
            code = np.clip(np.rint((target - offset) / step), 0, 65535).astype(
                np.uint16
            )
            self.codes[subset] = code
            approx = (code.astype(float) * step + offset).astype(np.float32)
            largest_error = max(largest_error, float(abs(approx - target).max()))
        by_rank = base.bg.names[:64].astype(np.uint16)
        order = np.argsort(by_rank).astype(np.uint8)
        self.small_names = np.concatenate(
            (by_rank.view(np.uint8), by_rank[order].view(np.uint8), order)
        )
        self.arrays = {"group": q, "all_states": full, "reachable": reachable}
        self.info = {
            "seen_contexts": h,
            "backoff_types": VOCAB,
            "reachable_normalizer_rows": len(reachable),
            "all_state_normalizer_rows": len(full) * 4,
            "group_mass_rows": len(q),
            "u16_max_normalizer_error_all_reachable_rows": largest_error,
        }


class Device:
    def __init__(self, point, compiled):
        props = cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)
        self.hardware = {
            "name": props["name"].decode(),
            "SMs": props["multiProcessorCount"],
            "L2_bytes": props["l2CacheSize"],
            "cupy": cp.__version__,
            "cuda_runtime": cp.cuda.runtime.runtimeGetVersion(),
            "cuda_driver": cp.cuda.runtime.driverGetVersion(),
        }
        t = time.perf_counter()
        mod = cp.RawModule(
            code=(HERE / "word_program_score.cu").read_text(), options=("--std=c++14",)
        )
        self.kernels = {mode: mod.get_function(mode) for mode in MODES}
        self.kernel_resources = {
            m: {
                k: v
                for k, v in kernel.attributes.items()
                if k
                in (
                    "num_regs",
                    "local_size_bytes",
                    "shared_size_bytes",
                    "const_size_bytes",
                )
            }
            for m, kernel in self.kernels.items()
        }
        self.module_ms = (time.perf_counter() - t) * 1000
        start = time.perf_counter()
        self.point = [cp.asarray(a) for a in point.values()]
        self.head = [cp.asarray(a) for a in compiled.head_tables.values()]
        self.weights = cp.asarray(compiled.factors, dtype=cp.float32)
        self.scale = cp.asarray(compiled.scale)
        self.small_names = cp.asarray(compiled.small_names)
        self.dummy = cp.zeros(1, dtype=cp.float32)
        self.storage = {
            "packed_program": cp.asarray(compiled.packet),
            "base_score": self.dummy,
            "on_demand": self.dummy,
            "reachable_u16": cp.asarray(compiled.codes),
        }
        for prefix, table in compiled.arrays.items():
            for typ, dtype in (("fp32", np.float32), ("mixed", np.float16)):
                self.storage[prefix + "_" + typ] = cp.asarray(table.astype(dtype))
        self.h = np.uint32(len(point["contexts"]))
        cp.cuda.get_current_stream().synchronize()
        self.upload_ms = (time.perf_counter() - start) * 1000
        raw = sum(v.nbytes for v in self.point)
        head = sum(v.nbytes for v in self.head)
        self.resident = {
            m: {
                "raw_point_bytes": raw,
                "head_and_lookup_bytes": head if m != "base_score" else 0,
                "factor_bytes": self.weights.nbytes if m.startswith("group") else 0,
                "mass_or_cache_bytes": self.storage[m].nbytes
                if m != "base_score"
                else 0,
            }
            for m in MODES
        }
        self.resident["on_demand"].update(
            head_and_lookup_bytes=head - self.head[0].nbytes + self.small_names.nbytes,
            factor_bytes=self.weights.nbytes,
            mass_or_cache_bytes=0,
        )
        self.resident["reachable_u16"]["factor_bytes"] = self.scale.nbytes
        self.resident["packed_program"].update(
            head_and_lookup_bytes=compiled.packet.nbytes, mass_or_cache_bytes=0
        )
        for row in self.resident.values():
            row["total_model_bytes"] = sum(row.values())
        for mode in MODES:
            arrays = [*self.point, self.storage[mode]]
            if mode in ("packed_program", "base_score"):
                arrays.append(self.dummy)
            else:
                arrays.extend(
                    self.head
                    if mode != "on_demand"
                    else [self.small_names, *self.head[1:]]
                )
                arrays.append(
                    self.scale
                    if mode == "reachable_u16"
                    else self.weights
                    if mode.startswith("group") or mode == "on_demand"
                    else self.dummy
                )
            blocks = {a.data.mem.ptr: a.data.mem.size for a in arrays}
            self.resident[mode]["array_allocations_including_launch_dummy"] = sum(
                blocks.values()
            )

    def call(self, mode, raw, out, fixed=False):
        header = (raw, np.uint32(out.size), np.uint32(fixed), self.h)
        head = self.head if mode != "on_demand" else [self.small_names, *self.head[1:]]
        params = self.scale if mode == "reachable_u16" else self.weights
        if mode in ("packed_program", "base_score"):
            head = [self.dummy] * 4
            params = self.dummy
        elif mode.startswith(("all_states", "reachable")) and mode != "reachable_u16":
            params = self.dummy
        self.kernels[mode](
            ((out.size + 255) // 256,),
            (256,),
            (*header, *self.point, *head, params, self.storage[mode], out),
        )

    def timings(self, raw, n, capture=False):
        out = cp.empty(n, dtype=np.float32)
        result = {m: [] for m in MODES}
        rng = np.random.default_rng(20261127)
        stream = (
            cp.cuda.Stream(non_blocking=True)
            if capture
            else cp.cuda.get_current_stream()
        )
        for m in MODES:
            self.call(m, raw, out)
        cp.cuda.get_current_stream().synchronize()
        graphs = {}
        if capture:
            with stream:
                for mode in MODES:
                    stream.begin_capture()
                    for _ in range(20):
                        self.call(mode, raw, out)
                    graphs[mode] = stream.end_capture()
                    graphs[mode].launch(stream)
            stream.synchronize()
        for _ in range(7):
            for j in rng.permutation(len(MODES)):
                mode = MODES[j]
                start, stop = cp.cuda.Event(), cp.cuda.Event()
                start.record(stream)
                if capture:
                    graphs[mode].launch(stream)
                else:
                    for _ in range(20):
                        self.call(mode, raw, out)
                stop.record(stream)
                stop.synchronize()
                result[mode].append(float(cp.cuda.get_elapsed_time(start, stop)) / 20)
        return result


def full_reference(base, program, groups, heads, a, b):
    raw = base.point(np.full(VOCAB, int(a)), np.full(VOCAB, int(b)), np.arange(VOCAB))
    ranks = base.bg.bins
    state = 2 * int(program.z[min(64, ranks[b])] > 0) + int(
        program.w[min(16, ranks[a])] > 0
    )
    old = raw * np.exp(program.logits[state, np.minimum(groups.bins, G)])
    old /= old.sum()
    for cut in NODES:
        mask = groups.bins >= cut
        total = old[mask].sum()
        old[mask] *= np.exp(heads[cut][state, np.minimum(groups.bins[mask] - cut, G)])
        old[mask] *= total / old[mask].sum()
    return raw, old


def rollout(device, base, program, groups, heads, seed_words):
    draws = np.random.default_rng(20261127).random(16)
    expected = list(map(int, seed_words))
    for u in draws:
        _, p = full_reference(base, program, groups, heads, *expected[-2:])
        expected.append(int(np.searchsorted(np.cumsum(p), u * p.sum())))
    paths = {}
    output = cp.empty(VOCAB, dtype=np.float32)

    def run(mode):
        history = list(map(int, seed_words))
        tic = time.perf_counter()
        for u in draws:
            tape = cp.asarray(history[-2:], dtype=cp.uint16)
            device.call(mode, tape, output, True)
            cdf = cp.cumsum(cp.exp(-output).astype(cp.float64))
            history.append(int(cp.searchsorted(cdf, u * cdf[-1]).item()))
        return history[2:], time.perf_counter() - tic

    modes = (
        "group_fp32",
        "reachable_fp32",
        "reachable_mixed",
        "reachable_u16",
        "on_demand",
        "packed_program",
    )
    for mode in modes:
        observed, _ = run(mode)
        prefix = next(
            (i for i, (a, b) in enumerate(zip(observed, expected[2:])) if a != b),
            len(observed),
        )
        paths[mode] = {
            "warm_seconds_including_host_and_sampling": [],
            "matching_reference_tokens": sum(
                a == b for a, b in zip(observed, expected[2:])
            ),
            "matching_reference_prefix": prefix,
            "tokens": observed,
        }
    rng = np.random.default_rng(8421)
    for _ in range(5):
        for i in rng.permutation(len(modes)):
            mode = modes[i]
            observed, elapsed = run(mode)
            assert observed == paths[mode]["tokens"]
            paths[mode]["warm_seconds_including_host_and_sampling"].append(elapsed)
    return {
        "initial_tokens": expected[:2],
        "binary64_reference": expected[2:],
        "device_paths": paths,
        "full_row_f32_bytes": 4 * VOCAB,
        "cdf_f64_bytes": 8 * VOCAB,
        "sampling_implementation": "CuPy also materializes exponential/cast temporaries and may allocate scan workspace.",
    }


def experiment(directory):
    start = time.perf_counter()
    base = Base(directory)
    program = Program()
    heads, bits = read_heads()
    point = point_tables(base)
    point_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    groups = ClassMass(base, 36)
    mass_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    compiled = Compiled(base, groups, program, heads)
    compile_ms = (time.perf_counter() - start) * 1000
    device = Device(point, compiled)
    reports = []
    for offset, digest in REPORTS.items():
        data = tokens("train_source", offset + N, digest, directory)
        tape = Tape(data, offset, N, base, groups, program)
        reference = tape.nll.copy()
        for cut, node in tape.nodes.items():
            reference[node.active] -= node.gains({}, heads[cut])
        raw = cp.asarray(data[offset - 2 : offset + N])
        out = cp.empty(N, dtype=cp.float32)
        metrics = {}
        for mode in MODES:
            device.call(mode, raw, out)
            actual = cp.asnumpy(out).astype(float)
            target = tape.raw.base_nll if mode == "base_score" else reference
            error = actual - target
            metrics[mode] = {
                "nll_per_token": float(actual.mean()),
                "maximum_token_error_nats": float(abs(error).max()),
                "mean_absolute_token_error_nats": float(abs(error).mean()),
                "summed_log_loss_error_nats": float(error.sum()),
                "full_rows": [],
            }
            assert np.max(abs(error)) < (0.002 if "mixed" in mode else 1.6e-5), (
                mode,
                metrics[mode],
            )
        rows = cp.empty(VOCAB, dtype=cp.float32)
        for pos in (0, 1234, N - 1):
            seed = data[offset + pos - 2 : offset + pos]
            plain, learned = full_reference(base, program, groups, heads, *seed)
            prefix = cp.asarray(seed)
            for mode in MODES:
                device.call(mode, prefix, rows, True)
                prob = np.exp(-cp.asnumpy(rows).astype(float))
                target = plain if mode == "base_score" else learned
                err = float(abs(np.log(prob / target)).max())
                mass_error = float(abs(prob.sum() - 1))
                metrics[mode]["full_rows"].append(
                    {
                        "position": pos,
                        "mass_error": mass_error,
                        "max_log_error_nats": err,
                    }
                )
                assert err < (0.002 if "mixed" in mode else 1.6e-5)
        times = device.timings(raw, N)
        reports.append(
            {
                "offset": offset,
                "sha256": digest,
                "tokens": N,
                "input_bytes": raw.nbytes,
                "output_bytes": out.nbytes,
                "base_binary64_nll": float(tape.raw.base_nll.mean()),
                "learned_binary64_nll": float(reference.mean()),
                "metrics": metrics,
                "gpu_batch_ms": times,
                "captured_gpu_batch_ms": device.timings(raw, N, capture=True),
            }
        )
        if len(reports) == 1:
            single = device.timings(raw, 1)
            single_graph = device.timings(raw, 1, capture=True)
            generated = rollout(
                device, base, program, groups, heads, data[offset - 2 : offset]
            )
    setup = {
        "read_base_and_point_pack_ms": point_ms,
        "group_mass_setup_ms": mass_ms,
        "normalizer_materialization_ms": compile_ms,
        "module_acquisition_ms": device.module_ms,
        "device_upload_all_modes_ms": device.upload_ms,
    }
    return {
        "registration": REGISTRATION,
        "bits_shared": program.bits + bits,
        "bits_standalone": program.standalone + bits,
        "hardware": device.hardware,
        "kernel_resources": device.kernel_resources,
        "standalone_packet_hex": compiled.packet.tobytes().hex(),
        "setup": setup,
        "table_shapes": compiled.info,
        "point_array_bytes": {n: a.nbytes for n, a in point.items()},
        "resident_per_mode": device.resident,
        "kernel_source_sha256": hashlib.sha256(
            (HERE / "word_program_score.cu").read_text().encode()
        ).hexdigest(),
        "timing_protocol": "Seven shuffled warm rounds, 20 kernel calls per CUDA event pair, pretransferred inputs and result buffer.",
        "single_teacher_forced_token_ms": single,
        "captured_single_token_ms": single_graph,
        "rollout": generated,
        "reports": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = experiment(args.data_dir)
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(text.encode())
    else:
        print(text, end="")
