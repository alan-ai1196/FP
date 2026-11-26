"""Test trained program values on new normalized readouts inside old word classes."""

import argparse
import base64
import json
import zlib
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import numpy as np
from joint_word_value import (
    HIGH,
    LOW,
    ClassMass,
    DirectRows,
    Sample,
    both_signs,
    minimize_scaled,
    refine,
    residual,
    scalar_fit,
)
from lexical_switch import tokens
from reuse_word_value import HERE, G, Prior, packed, reconstruct, unpack_signs
from text import VOCAB
from threadpoolctl import threadpool_limits
from word_value import Base, quantized, sign_string

REGISTRATION = "51aa0d9"
START, TRAIN, N = 43000000, 131072, 32768
SHA = "ec403e94b15004f56e139205994adb1f5e9c602e10f27c65355327585c59d1a6"
REPORTS = {
    45000000: "61b7899014dcf0163c211f07cadb3a8b338d7d13bc95e380ada14e469fa1df0d",
    47000000: "8fdc4dd370394fabbcfe9ab39064fe3fcd6ecc10aefbbb1a6fd40d8ab2214b35",
    49000000: "e88ddff9c6bce8c7cfb63969017ffd6c7761011205862080ff823b92688a8dae",
}
NODES = (12, 24)
FEATURES = {
    "one": np.ones(4),
    "a": np.array([-1, -1, 1, 1]),
    "b": np.array([-1, 1, -1, 1]),
    "c": np.array([1, -1, -1, 1]),
}
MENUS = {
    "static": ("one",),
    "a": ("one", "a"),
    "b": ("one", "b"),
    "c": ("one", "c"),
    "additive": ("one", "a", "b"),
    "all_bits": ("one", "a", "b", "c"),
}
POLICIES = {
    "constituents": ("unchanged", "static", "a", "b", "additive"),
    "product_available": ("unchanged", *MENUS),
    "fresh_names": ("unchanged", "static", "fresh", "direct"),
    "all": ("unchanged", *MENUS, "fresh", "direct"),
}


class Program:
    def __init__(self):
        old = Prior()
        r = json.loads((HERE / "reuse_word_value_result.json").read_text())
        self.name = r["selected"]["either_priced"]["model"]
        spec = r["models"][self.name]
        assert spec["lag"] == 2 and spec["inputs"] == 16
        assert [atom["op"] for atom in spec["atoms"]] == ["constant", "product"]
        self.z = old.z
        self.w = unpack_signs(spec["atoms"][1]["w"])
        self.logits = np.empty((4, G + 1))
        table = reconstruct(spec)
        for ai, bi in product(range(2), repeat=2):
            block = table[ai * 17 : (ai + 1) * 17][(self.w > 0) == bi]
            assert np.all(block == block[0])
            self.logits[ai * 2 + bi] = old.logits[ai] + block[0]
        self.bits = old.spec["incremental_bits"] + spec["bits"]
        self.standalone = old.spec["standalone_bits"] + spec["bits"]


class Tape:
    def __init__(self, raw, start, n, base, groups, program):
        self.raw = Sample(raw, start, n, base, groups)
        data = self.raw
        a = program.z[data.inputs(64, 1)]
        b = program.w[data.inputs(16, 2)]
        self.state = 2 * (a > 0).astype(int) + (b > 0)
        self.rank = {lag: data.inputs(64, lag) for lag in (1, 2)}
        shifts = program.logits[self.state]
        q = data.q[data.context]
        coarse = np.column_stack((q[:, :G], q[:, G:].sum(axis=1)))
        gain = shifts[np.arange(n), np.minimum(data.y, G)] - np.log(
            np.einsum("ij,ij->i", coarse, np.exp(shifts))
        )
        self.nll = data.base_nll - gain
        self.nodes = {cut: Node(self, cut) for cut in NODES}


class Node:
    def __init__(self, tape, cut):
        data = tape.raw
        self.active = data.y >= cut
        self.y = np.minimum(data.y[self.active] - cut, G)
        self.state = tape.state[self.active]
        self.rank = {lag: r[self.active] for lag, r in tape.rank.items()}
        keys, self.context = np.unique(data.context[self.active], return_inverse=True)
        base = data.q[keys]
        q = np.column_stack((base[:, cut : cut + G], base[:, cut + G :].sum(axis=1)))
        self.q = q / q.sum(axis=1)[:, None]
        self.cal = self.q
        self.bias = np.zeros(G, dtype=np.int16)
        self.pair, self.trace, self.freq = np.unique(
            self.state * len(q) + self.context, return_inverse=True, return_counts=True
        )
        self.rows = self.pair // len(q)
        self.cell_q = self.q[self.pair % len(q)]
        self.observed = np.bincount(
            self.state * (G + 1) + self.y, minlength=4 * (G + 1)
        ).reshape(4, G + 1)

    def grouped(self, values):
        return np.stack(
            [np.bincount(self.rows, weights=col, minlength=4) for col in values.T],
            axis=1,
        )

    def moments(self, table):
        mass = self.cell_q * np.exp(table)[self.rows]
        prob = mass / mass.sum(axis=1)[:, None]
        return prob, self.observed - self.grouped(prob * self.freq[:, None])

    def gains(self, spec, table):
        i = self.rank[spec["lag"]] if "lag" in spec else self.state
        shifts = table[i]
        return shifts[np.arange(len(i)), self.y] - np.log(
            np.einsum("ij,ij->i", self.q[self.context], np.exp(shifts))
        )


def compact_step(node, table, features):
    q, r = node.moments(table)
    rows = [FEATURES[v] @ r for v in features]
    j = int(np.argmax([np.abs(v).sum() for v in rows]))
    key, moment = features[j], rows[j]
    h = FEATURES[key]
    output = np.where(moment >= 0, 1, -1).astype(np.int8)
    raw_target = h @ node.observed @ output
    mean = h[node.rows] * (q @ output)
    lo, hi = 0, 8191
    while lo < hi:
        mid = (lo + hi) // 2
        t = np.tanh(mid / 4096)
        if raw_target - (mean + t) / (1 + t * mean) @ node.freq > 0:
            lo = mid + 1
        else:
            hi = mid

    def gain(beta_q):
        v = beta_q / 4096
        return v * raw_target - node.freq @ np.log(np.cosh(v) + mean * np.sinh(v))

    beta = max((max(0, lo - 1), lo), key=gain)
    spec = {
        "feature": key,
        "s": sign_string(output * output[-1]),
        "beta_q12": int(beta * int(output[-1])),
    }
    return spec, h[:, None] * output * (beta / 4096)


def real_fit(node, features, ridge, start):
    design = np.stack([FEATURES[k] for k in features], axis=1)

    def objective(x):
        table = np.pad(design @ x, ((0, 0), (0, 1)))
        mass = node.cell_q * np.exp(table)[node.rows]
        den = mass.sum(axis=1)
        loss = (
            node.freq @ np.log(den)
            - np.sum(table * node.observed)
            + 0.5 * ridge * np.sum(x * x)
        )
        grad = (
            node.grouped(mass[:, :-1] * (node.freq / den)[:, None])
            - node.observed[:, :-1]
        )
        return loss, design.T @ grad + ridge * x

    info = node.freq @ (node.cell_q[:, :-1] * (1 - node.cell_q[:, :-1]))
    scale = np.sqrt(ridge + np.broadcast_to(info, start.shape))
    x, work = minimize_scaled(objective, start, scale, LOW, HIGH)
    grid = quantized(x)
    return x, grid, np.pad(design @ (grid / 4096), ((0, 0), (0, 1))), work


class Book:
    def __init__(self):
        self.best = {}
        self.counts = {}
        self.work = {
            "compact_steps": 0,
            "real_objectives": 0,
            "direct_objectives": 0,
            "fresh_sign_masks": 0,
            "scalar_objectives": 0,
        }

    def consider(self, node, family, spec, bits, table):
        gain = float(node.gains(spec, table).sum())
        self.counts[family] = self.counts.get(family, 0) + 1
        info = {**spec, "family": family, "bits": bits, "validation_gain": gain}
        for group in [family, *[k for k, v in POLICIES.items() if family in v]]:
            for mode, price in (("gross", 0.0), ("priced", np.log(2))):
                order = gain - price * bits, -bits
                key = group + "_" + mode
                if key not in self.best or order > self.best[key][0]:
                    self.best[key] = (order, info, table.copy())


def fit(train, valid):
    book = Book()
    book.consider(valid, "unchanged", {"method": "none"}, 0, np.zeros((4, G + 1)))
    for family, features in MENUS.items():
        table = np.zeros((4, G + 1))
        atoms = []
        for k in range(1, 5):
            atom, delta = compact_step(train, table, features)
            book.work["compact_steps"] += 1
            atoms.append(atom)
            table += delta
            book.consider(
                valid,
                family,
                {"method": "sign", "atoms": atoms.copy()},
                7 + 28 * k,
                table,
            )
        basis_sets = [features]
        if len(features) > 1:
            basis_sets.append(features[1:])
        for subset in basis_sets:
            start = np.zeros((len(subset), G))
            for ridge in (256, 32, 4):
                start, grid, table, work = real_fit(train, subset, ridge, start)
                book.work["real_objectives"] += work
                book.consider(
                    valid,
                    family,
                    {
                        "method": "real",
                        "features": subset,
                        "q12": grid.tolist(),
                        "ridge": ridge,
                    },
                    7 + 14 * grid.size,
                    table,
                )
    for lag in (1, 2):
        i = train.rank[lag]
        s, z, _ = both_signs(residual(train, i, 65))
        book.work["fresh_sign_masks"] += 1 << G
        z, beta, work = scalar_fit(train, i, z, s)
        book.work["scalar_objectives"] += work
        book.consider(
            valid,
            "fresh",
            {
                "method": "fresh_sign",
                "lag": lag,
                "z": sign_string(z),
                "s": sign_string(s),
                "q12": beta,
            },
            7 + 65 + G + 14,
            z[:, None] * s * (beta / 4096),
        )
        init = np.clip((s[:-1] - s[-1]) * (beta / 4096), LOW, HIGH)
        for ridge in (16, 256):
            zr, grid, work = refine(train, i, z, init, ridge)
            book.work["real_objectives"] += work
            book.consider(
                valid,
                "fresh",
                {
                    "method": "fresh_real",
                    "lag": lag,
                    "z": sign_string(zr),
                    "q12": grid.tolist(),
                    "ridge": ridge,
                },
                7 + 65 + 14 * G,
                zr[:, None] * np.r_[grid / 4096, 0.0],
            )
        direct = DirectRows(train, i, 65)
        start = np.zeros((65, G))
        for ridge in (256, 32, 4):
            start, grid, work = direct.fit(ridge, start)
            book.work["direct_objectives"] += work
            book.consider(
                valid,
                "direct",
                {
                    "method": "rows",
                    "lag": lag,
                    "q12_zlib_base64": packed(grid),
                    "ridge": ridge,
                },
                7 + 14 * grid.size,
                np.pad(grid / 4096, ((0, 0), (0, 1))),
            )
    return book


def decode(spec):
    method = spec["method"]
    if method == "none":
        return np.zeros((4, G + 1))
    if method == "sign":
        return sum(
            FEATURES[a["feature"]][:, None]
            * unpack_signs(a["s"])
            * (a["beta_q12"] / 4096)
            for a in spec["atoms"]
        )
    if method == "real":
        design = np.stack([FEATURES[v] for v in spec["features"]], axis=1)
        return np.pad(design @ (np.asarray(spec["q12"]) / 4096), ((0, 0), (0, 1)))
    if method == "rows":
        blob = zlib.decompress(base64.b64decode(spec["q12_zlib_base64"]))
        return np.pad(
            np.frombuffer(blob, dtype="<i2").reshape(65, G) / 4096, ((0, 0), (0, 1))
        )
    z = unpack_signs(spec["z"])
    if method == "fresh_sign":
        return z[:, None] * unpack_signs(spec["s"]) * (spec["q12"] / 4096)
    return z[:, None] * np.r_[np.asarray(spec["q12"]) / 4096, 0.0]


def exact_audit():
    base = [F(k, 21) for k in range(1, 7)]
    checked = 0
    for z1, z2 in product((-1, 1), repeat=2):
        for s, t in product(product((-1, 1), repeat=3), repeat=2):
            row = base.copy()
            factors = [F(1)] * len(row)
            for cut, head, state in ((1, s, z1), (3, t, z2)):
                mass = sum(row[cut:])
                raw = [F(2) ** (state * head[min(j, 2)]) for j in range(len(row) - cut)]
                norm = sum(p * f for p, f in zip(row[cut:], raw)) / mass
                ratio = [f / norm for f in raw]
                row[cut:] = [p * f for p, f in zip(row[cut:], ratio)]
                factors[cut:] = [p * f for p, f in zip(factors[cut:], ratio)]
                assert sum(row[cut:]) == mass and sum(row) == 1
            assert all(row[y] == base[y] * factors[y] for y in range(6))
            checked += 1
    return checked


def experiment(directory):
    checked = exact_audit()
    base, program = Base(directory), Program()
    grouping = ClassMass(base, 36)
    raw = tokens("train_source", START + TRAIN + N, SHA, directory)
    fit_tape = Tape(raw, START, TRAIN, base, grouping, program)
    valid = Tape(raw, START + TRAIN, N, base, grouping, program)
    books = {cut: fit(fit_tape.nodes[cut], valid.nodes[cut]) for cut in NODES}
    installs, selections = {}, {}
    for cut, book in books.items():
        installs[cut] = {}
        selections[cut] = {}
        for k, (order, spec, table) in book.best.items():
            assert np.array_equal(decode(spec), table)
            name = next((n for n, v in installs[cut].items() if v == spec), None)
            if name is None:
                name = spec["family"] + "-" + str(len(installs[cut]) + 1)
                installs[cut][name] = spec
            selections[cut][k] = {
                "model": name,
                "validation_score_after_price": order[0],
            }
    reports = []
    for start, sha in REPORTS.items():
        raw = tokens("train_source", start + N, sha, directory)
        tape = Tape(raw, start, N, base, grouping, program)
        pos = 1234
        raw_q = base.point(
            np.full(VOCAB, int(raw[start + pos - 2])),
            np.full(VOCAB, int(raw[start + pos - 1])),
            np.arange(VOCAB),
        )
        coarse = np.minimum(grouping.bins, G)
        raw_old = raw_q * np.exp(program.logits[tape.state[pos], coarse])
        raw_old /= raw_old.sum()
        worst = max(
            abs(raw_q.sum() - 1),
            abs(-np.log(raw_old[raw[start + pos]]) - tape.nll[pos]),
        )
        methods = {}
        for k in books[NODES[0]].best:
            total = np.zeros(N)
            ref = raw_old.copy()
            node_gains = []
            node_blocks = []
            for cut in NODES:
                _, spec, table = books[cut].best[k]
                node = tape.nodes[cut]
                delta = node.gains(spec, table)
                full = np.zeros(N)
                full[node.active] = delta
                total += full
                node_gains.append(float(delta.sum()))
                node_blocks.append(full.reshape(8, -1).sum(axis=1).tolist())
                i = tape.rank[spec["lag"]][pos] if "lag" in spec else tape.state[pos]
                parent = grouping.bins >= cut
                classes = np.minimum(grouping.bins[parent] - cut, G)
                mass = ref[parent].sum()
                ref[parent] *= np.exp(table[i, classes])
                ref[parent] *= mass / ref[parent].sum()
                worst = max(worst, abs(ref[parent].sum() - mass))
            worst = max(
                worst,
                abs(ref.sum() - 1),
                abs(ref[~(grouping.bins >= G)] - raw_old[~(grouping.bins >= G)]).max(),
                abs(
                    np.log(ref[raw[start + pos]] / raw_old[raw[start + pos]])
                    - total[pos]
                ),
            )
            methods[k] = {
                "node_gains": node_gains,
                "joint_gain": float(total.sum()),
                "nll_per_word": float(np.mean(tape.nll - total)),
                "gain_by_4096_words": total.reshape(8, -1).sum(axis=1).tolist(),
                "node_block_gains": node_blocks,
            }
        assert worst < 2e-12
        reports.append(
            {
                "offset": start,
                "sha256": sha,
                "parent_occurrences": [len(tape.nodes[c].y) for c in NODES],
                "frozen_nll": float(tape.nll.mean()),
                "full_row_and_parent_error": float(worst),
                "methods": methods,
            }
        )
    return {
        "registration": REGISTRATION,
        "training_offset": START,
        "training_words": TRAIN,
        "validation_words": N,
        "fit_validation_sha256": SHA,
        "frozen_program": program.name,
        "frozen_bits_shared": program.bits,
        "frozen_bits_standalone": program.standalone,
        "rational_normalized_trees": checked,
        "training_parent_occurrences": [len(fit_tape.nodes[c].y) for c in NODES],
        "validation_parent_occurrences": [len(valid.nodes[c].y) for c in NODES],
        "work": {c: b.work for c, b in books.items()},
        "candidates": {c: b.counts for c, b in books.items()},
        "models": installs,
        "selected": selections,
        "reports": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = experiment(args.data_dir)
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(serialized.encode())
    else:
        print(serialized, end="")
