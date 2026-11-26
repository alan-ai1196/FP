"""Learn the argument set and all sign tables of a word-history product."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations
from math import ceil, log2
from pathlib import Path
from time import perf_counter

import numpy as np
from joint_word_value import (
    HIGH,
    LOW,
    ClassMass,
    Sample,
    both_signs,
    fit_direction,
    minimize_scaled,
)
from lexical_switch import tokens
from product_residual import sign
from reuse_word_value import packed, unpack_signs
from scipy.sparse import csr_matrix
from text import VOCAB
from threadpoolctl import threadpool_limits
from word_value import Base, quantized, sign_string

REGISTRATION = "4ba2bd4"
START, TRAIN, N = 51000000, 131072, 32768
DIGEST = "f3b053cb1ab66b0d42e1ad8dfd39238573417efee8eefc7186fb95f83c11d8d2"
REPORTS = {
    53000000: "6837ffa3abfd44dcb9addd95533a299c05dab66969462b1a3053a1504e22dd9c",
    55000000: "0ece7d984689eed7a0b12050873bd5e387784f10f311e5600c0a02b663c8a68c",
    57000000: "f44bde345c3b8077fb9c4ee8b5eaba600dcca78631c57464287b592581b1ad4a",
}
G, POOL_BITS = 12, 4 + 14 * 12
PRICES = ("unpriced", "shared_ranks", "standalone")


def sample(raw, start, n, base, group):
    data = Sample(raw, start, n, base, group)
    data.input_rank[3] = base.bg.bins[raw[start - 3 : start + n - 3]]
    return data


def coordinates(data, size, lags):
    return np.column_stack([data.inputs(size, lag) for lag in lags])


def encode(x, radix):
    keys = np.zeros(len(x), dtype=np.int64)
    for col in x.T:
        keys = keys * radix + col
    return keys


def decode(keys, radix, width):
    x = np.empty((len(keys), width), dtype=np.int64)
    for axis in reversed(range(width)):
        keys, x[:, axis] = np.divmod(keys, radix)
    return x


class Cells:
    def __init__(self, data, size, lags):
        self.radix = size + 1
        x = coordinates(data, size, lags)
        self.keys, cell = np.unique(encode(x, self.radix), return_inverse=True)
        self.x = decode(self.keys, self.radix, len(lags))
        self.count = np.bincount(cell)
        self.observed = np.bincount(
            cell * (G + 1) + data.y, minlength=len(self.x) * (G + 1)
        ).reshape(-1, G + 1)
        pair, self.freq = np.unique(
            cell * len(data.cal) + data.context, return_counts=True
        )
        self.row, ctx = np.divmod(pair, len(data.cal))
        self.q = data.cal[ctx]
        self.expected = self.group(self.freq[:, None] * self.q)
        self.r = self.observed - self.expected
        assert np.max(abs(self.r.sum(axis=1))) < 1e-8

    def group(self, a):
        return np.stack(
            [np.bincount(self.row, col, minlength=len(self.x)) for col in a.T], axis=1
        )


def history_sign(x, masks):
    h = np.ones(len(x), dtype=np.int8)
    for col, mask in zip(x.T, masks, strict=True):
        h *= mask[col]
    return h


def contrast(cells, masks, head):
    return float(history_sign(cells.x, masks) @ (cells.r @ head))


def factor_fibers(cells, order, work):
    x, r = cells.x, cells.r
    original = list(range(x.shape[1]))
    masks = [None] * len(original)
    for axis in order:
        at = original.index(axis)
        names = x[:, at]
        rest = np.delete(x, at, axis=1)
        keys, group = np.unique(encode(rest, cells.radix), return_inverse=True)
        accum = np.zeros((len(keys), G + 1))
        norms = np.bincount(names, np.einsum("ij,ij->i", r, r), minlength=cells.radix)
        labels = np.ones(cells.radix, dtype=np.int8)
        by_name = np.argsort(names, kind="stable")
        offsets = np.r_[0, np.bincount(names, minlength=cells.radix).cumsum()]
        for name in np.argsort(-norms, kind="stable"):
            ids = by_name[offsets[name] : offsets[name + 1]]
            gs, fiber = group[ids], r[ids]
            if np.sum(accum[gs] * fiber) < 0:
                labels[name] = -1
            accum[gs] += labels[name] * fiber
        work["fiber_row_visits"] += len(r)
        masks[axis] = labels
        original.pop(at)
        x, r = decode(keys, cells.radix, len(original)), accum
    head = sign(r[0])
    u = contrast(cells, masks, head)
    assert u + 1e-7 >= np.sqrt(2) * np.linalg.norm(cells.r)
    return masks, head


def spectral(cells, work):
    x, r = cells.x, cells.r
    masks = []
    for axis, names in enumerate(x.T):
        rest = np.delete(x, axis, axis=1)
        keys, group = np.unique(encode(rest, cells.radix), return_inverse=True)
        cols = (group[:, None] * (G + 1) + np.arange(G + 1)).ravel()
        layer = csr_matrix(
            (r.ravel(), (names.repeat(G + 1), cols)),
            shape=(cells.radix, len(keys) * (G + 1)),
        )
        gram = (layer @ layer.T).toarray()
        masks.append(sign(np.linalg.eigh(gram)[1][:, -1]))
        work["spectral_sparse_entries"] += layer.nnz
    head = sign(np.linalg.eigh(r.T @ r)[1][:, -1])
    if contrast(cells, masks, head) < 0:
        head *= -1
    return masks, head


def alternate(cells, initial, work):
    x, r = cells.x, cells.r
    masks = [s.copy() for s in initial[0]]
    head = initial[1].copy()
    h = history_sign(x, masks)
    before = float(h @ (r @ head))
    for _ in range(64):
        projected = r @ head
        changed = False
        for axis, col in enumerate(x.T):
            h *= masks[axis][col]
            votes = np.bincount(col, projected * h, minlength=cells.radix)
            new = np.where(votes == 0, masks[axis], sign(votes))
            changed |= bool(np.any(new != masks[axis]))
            masks[axis] = new
            h *= new[col]
        votes = r.T @ h
        new = np.where(votes == 0, head, sign(votes))
        changed |= bool(np.any(new != head))
        head = new
        work["alternating_sweeps"] += 1
        work["alternating_row_slot_visits"] += len(r) * (len(masks) + 1)
        if not changed:
            break
    assert contrast(cells, masks, head) + 1e-7 >= before
    return masks, head


def amplitude(cells, masks, head, work):
    h = history_sign(cells.x, masks)
    obs = float(h @ cells.observed @ head)
    m = np.clip(cells.q @ head, -1, 1) * h[cells.row]
    n = int(cells.freq.sum())
    score = contrast(cells, masks, head)
    assert abs(obs - cells.freq @ m - score) < 1e-7

    def gain(b):
        return b * obs - n * np.log(np.cosh(b)) - cells.freq @ np.log1p(m * np.tanh(b))

    lo, hi = 0, 8191
    while lo < hi:
        mid = (lo + hi) // 2
        t = np.tanh(mid / 4096)
        if obs > cells.freq @ ((m + t) / (1 + m * t)):
            lo = mid + 1
        else:
            hi = mid
        work["amplitude_derivatives"] += 1
    assert gain(score / n) + 1e-7 >= score * score / (2 * n)
    return max((max(0, lo - 1), lo), key=lambda v: gain(v / 4096))


def canonical(lags, masks, head, beta):
    active, tables = [], []
    b = int(beta) * int(head[-1])
    for lag, mask in zip(lags, masks, strict=True):
        b *= int(mask[-1])
        if np.any(mask != mask[-1]):
            active.append(lag)
            tables.append(sign_string(mask * mask[-1]))
    return {
        "lags": active,
        "tables": tables,
        "head": sign_string(head * head[-1]),
        "q12": b,
    }


def atom_features(atom, x, lags):
    h = np.ones(len(x), dtype=np.int8)
    for lag, table in zip(atom["lags"], atom["tables"], strict=True):
        h *= unpack_signs(table)[x[:, lags.index(lag)]]
    return h, unpack_signs(atom["head"])


def dense_fit(cells, ridge, start, work):
    x = cells.x
    info = cells.group(cells.freq[:, None] * cells.q[:, :-1] * (1 - cells.q[:, :-1]))

    def by_name(matrix):
        return np.array(
            [
                [np.bincount(col, v, minlength=cells.radix) for v in matrix.T]
                for col in x.T
            ]
        ).transpose(0, 2, 1)

    def loss(w):
        logits = np.zeros((len(x), G))
        for slope, col in zip(w, x.T, strict=True):
            logits += slope[col]
        mass = cells.q[:, :-1] * np.exp(logits)[cells.row]
        norm = cells.q[:, -1] + mass.sum(axis=1)
        val = cells.freq @ np.log(norm) - np.sum(cells.observed[:, :-1] * logits)
        residual = (
            cells.group(mass * (cells.freq / norm)[:, None]) - cells.observed[:, :-1]
        )
        return val + 0.5 * ridge * np.sum(w * w), by_name(residual) + ridge * w

    w, steps = minimize_scaled(loss, start, np.sqrt(ridge + by_name(info)), LOW, HIGH)
    work["dense_objective_evaluations"] += steps
    work["dense_pair_evaluations"] += steps * len(cells.q)
    return w, quantized(w)


def compact_fit(cells, atoms, lags, work):
    features = [atom_features(a, cells.x, lags) for a in atoms]
    n = int(cells.freq.sum())
    observed = np.array([float(h @ cells.observed @ s) for h, s in features])
    hs = np.stack([h for h, _ in features], axis=1)
    heads = np.stack([s for _, s in features])

    # Each lag independently proposes a unary transformation. Refit their strengths jointly.
    def loss(w):
        logits = (hs * w) @ heads
        mass = cells.q * np.exp(logits)[cells.row]
        denom = mass.sum(axis=1)
        agg = cells.group(mass * (cells.freq / denom)[:, None])
        expected = np.sum(hs * (agg @ heads.T), axis=0)
        return cells.freq @ np.log(denom) - w @ observed, expected - observed

    start = np.array([a["q12"] / 4096 for a in atoms])
    coef, steps = minimize_scaled(
        loss, start, np.full(len(atoms), np.sqrt(n)), LOW, HIGH
    )
    work["compact_objective_evaluations"] += steps
    work["compact_pair_evaluations"] += steps * len(cells.q)
    return [
        dict(a, q12=int(b)) for a, b in zip(atoms, quantized(coef), strict=True) if b
    ]


def direct_fit(cells, tau):
    mean = cells.expected / cells.count[:, None]
    assert mean.min() > 0
    tilt = np.log((cells.observed + tau * mean) / ((cells.count + tau)[:, None] * mean))
    table = quantized(tilt[:, :-1] - tilt[:, -1:])
    keep = np.any(table != 0, axis=1)
    return cells.keys[keep], table[keep]


class Model:
    def __init__(
        self, family, size=0, lags=(), *, atoms=(), dense=None, direct=None, **details
    ):
        self.family, self.size, self.lags = family, size, tuple(lags)
        self.atoms, self.dense, self.direct = atoms, dense, direct
        self.spec = {"family": family, **details}
        self.active = ()
        bits = 0 if family == "base" else POOL_BITS
        if family in ("product", "independent"):
            self.active = tuple(sorted({lag for a in atoms for lag in a["lags"]}))
            masks = {w for a in atoms for w in a["tables"]}
            heads = {a["head"] for a in atoms}
            if family == "product":
                bits += (
                    3 + 4 + 1 + 3 + 2 * len(self.active) + size * len(masks) + G + 14
                )
            else:
                bits += (
                    3
                    + 1
                    + 3
                    + 3
                    + 3
                    + size * len(masks)
                    + G * len(heads)
                    + (3 + 2 + 2 + 14) * len(atoms)
                )
            self.spec.update(
                atoms=list(atoms),
                nonconstant_lags=list(self.active),
                input_exceptions_per_table={w: w.count("-") for w in sorted(masks)},
                output_exceptions_per_head={s: s.count("-") for s in sorted(heads)},
            )
        elif family == "dense":
            self.active = self.lags
            bits += 3 + 4 + 1 + 14 * dense.size
            self.spec["table_q12_i16le_zlib_base64"] = packed(dense)
        elif family == "direct":
            self.active = self.lags
            keys, table = direct
            domain = (size + 1) ** len(lags)
            bits += (
                3
                + 4
                + 1
                + ceil(log2(domain + 1))
                + len(keys) * (ceil(log2(domain)) + 14 * G)
            )
            digest = hashlib.sha256(keys.astype("<i8").tobytes())
            digest.update(table.astype("<i2").tobytes())
            self.spec.update(
                stored_rows=len(keys),
                key_i64le_then_table_i16le_sha256=digest.hexdigest(),
            )
        names = 0 if family == "base" else max(G, size if self.active else 0)
        self.bits, self.standalone = bits, bits + 16 * names
        self.spec.update(shared_rank_bits=bits, standalone_bits=self.standalone)
        if size:
            self.spec.update(input_named_classes=size, searched_lags=list(lags))

    def offsets(self, data, positions):
        n = len(data.y) if positions is None else len(positions)
        table = np.zeros((n, G + 1))
        if self.family == "base":
            return table
        table[:, :-1] = data.bias / 4096
        if not self.lags:
            return table
        x = coordinates(data, self.size, self.lags)
        if positions is not None:
            x = x[positions]
        if self.family in ("product", "independent"):
            for atom in self.atoms:
                h, s = atom_features(atom, x, self.lags)
                table += (atom["q12"] / 4096) * h[:, None] * s
        elif self.family == "dense":
            for w, col in zip(self.dense, x.T, strict=True):
                table[:, :-1] += w[col] / 4096
        elif self.family == "direct":
            keys, w = self.direct
            k = encode(x, self.size + 1)
            if len(keys):
                pos = np.minimum(np.searchsorted(keys, k), len(keys) - 1)
                present = keys[pos] == k
                table[present, :-1] += w[pos[present]] / 4096
        return table

    def gain(self, data):
        if self.family == "base":
            return np.zeros(len(data.y))
        if self.family == "pooled":
            return data.static
        table = self.offsets(data, None)
        norm = (data.q[data.context] * np.exp(table)).sum(axis=1)
        return table[np.arange(len(table)), data.y] - np.log(norm)


class Selection:
    def __init__(self):
        self.selected, self.matched = {}, {}
        self.counts, self.work = Counter(), Counter()
        self.panels = []

    def consider(self, model, valid):
        family = model.family
        groups = ["overall", family]
        if family == "product":
            groups.extend([model.spec["solver"], f"arity_{len(model.active)}"])
            if len(model.active) > 1:
                groups.append("multi_input")
        self.counts[model.spec.get("solver", family)] += 1
        gain = float(model.gain(valid).sum())
        model.spec["validation_gain_nats"] = gain
        for price, bits in zip(PRICES, (0, model.bits, model.standalone), strict=True):
            order = (gain - np.log(2) * bits, -model.bits)
            for group in groups:
                k = group + "_" + price
                if k not in self.selected or self.selected[k][0] < order:
                    self.selected[k] = (order, model)
            if family in ("independent", "dense", "direct"):
                k = (model.size, model.lags, family, price)
                if k not in self.matched or self.matched[k][0] < order:
                    self.matched[k] = (order, model)

    def matched_controls(self):
        for label, (_, winner) in list(self.selected.items()):
            if winner.family != "product" or not winner.active:
                continue
            if not label.startswith(("arity_", "multi_input_", "product_")):
                continue
            price = next(p for p in PRICES if label.endswith("_" + p))
            for family in ("independent", "dense", "direct"):
                self.selected[label + "_matched_" + family] = self.matched[
                    winner.size, winner.active, family, price
                ]


def fit_panel(cells, size, lags, book, valid, unary):
    work = book.work
    axes = tuple(range(len(lags)))
    methods = {
        "forward": factor_fibers(cells, axes, work),
        "reverse": factor_fibers(cells, reversed(axes), work),
        "spectral": spectral(cells, work),
    }
    rng = np.random.default_rng(27000 + size * 16 + sum(1 << (lag - 1) for lag in lags))
    starts = list(methods.values())
    for _ in range(3):
        starts.append(
            (
                [sign(rng.standard_normal(cells.radix)) for _ in lags],
                sign(rng.standard_normal(G + 1)),
            )
        )
    methods["alternating"] = max(
        (alternate(cells, init, work) for init in starts),
        key=lambda pair: contrast(cells, *pair),
    )
    if len(lags) == 1:
        # Finite exact two-index direction also sets the independent additive comparator.
        r = np.zeros((cells.radix, G + 1))
        r[cells.x[:, 0]] = cells.r
        head, w, _ = both_signs(r)
        methods["exact_unary"] = ([w], head)
        work["exact_unary_output_masks"] += 1 << G
    for solver, (masks, head) in methods.items():
        b = amplitude(cells, masks, head, work)
        atom = canonical(lags, masks, head, b)
        h, s = atom_features(atom, cells.x, lags)
        assert np.array_equal(
            atom["q12"] * h[:, None].astype(np.int32) * s,
            b * history_sign(cells.x, masks)[:, None].astype(np.int32) * head,
        )
        if solver == "exact_unary":
            unary[lags[0]] = atom
        model = Model(
            "product",
            size,
            lags,
            atoms=[atom],
            solver=solver,
            training_contrast=contrast(cells, masks, head),
        )
        book.consider(model, valid)
    fitted = compact_fit(cells, [unary[lag] for lag in lags], lags, work)
    book.consider(Model("independent", size, lags, atoms=fitted), valid)
    for tau in (16, 128, 1024):
        book.consider(
            Model("direct", size, lags, direct=direct_fit(cells, tau), tau=tau), valid
        )
    start = np.zeros((len(lags), cells.radix, G))
    for ridge in (1024, 128, 16):
        start, q12 = dense_fit(cells, ridge, start, work)
        book.consider(Model("dense", size, lags, dense=q12, ridge=ridge), valid)
    book.panels.append(
        {
            "input_names": size,
            "lags": list(lags),
            "occupied_cells": len(cells.x),
            "cell_context_pairs": len(cells.q),
            "residual_frobenius": float(np.linalg.norm(cells.r)),
        }
    )


def experiment(directory):
    start_time = perf_counter()
    base = Base(directory)
    group = ClassMass(base, G)
    raw = tokens("train_source", START + TRAIN + N, DIGEST, directory)
    train = sample(raw, START, TRAIN, base, group)
    valid = sample(raw, START + TRAIN, N, base, group)
    bias, steps = fit_direction(train, np.ones(TRAIN, dtype=np.int8), 0.0, np.zeros(G))
    train.set_bias(bias)
    valid.set_bias(bias)
    book = Selection()
    book.work["pooled_objective_evaluations"] = steps
    for family in ("base", "pooled"):
        book.consider(Model(family), valid)
    for size in (16, 64):
        unary = {}
        for length in (1, 2, 3, 4):
            for lags in combinations((1, 2, 3, 4), length):
                fit_panel(Cells(train, size, lags), size, lags, book, valid, unary)
    fit_seconds = perf_counter() - start_time
    book.matched_controls()
    chosen, models = {}, {}
    for key, (order, model) in book.selected.items():
        identity = (
            model.family
            + "-"
            + hashlib.sha256(
                json.dumps(model.spec, sort_keys=True).encode()
            ).hexdigest()[:12]
        )
        models[identity] = model
        chosen[key] = {"model": identity, "validation_score_after_price": order[0]}
    reports = []
    for offset, digest in REPORTS.items():
        raw = tokens("train_source", offset + N, digest, directory)
        data = sample(raw, offset, N, base, group)
        data.set_bias(bias)
        positions = np.array([1234, 17117, N - 1])
        raw_rows = []
        for t in positions:
            q = base.point(
                np.full(VOCAB, int(raw[offset + t - 2])),
                np.full(VOCAB, int(raw[offset + t - 1])),
                np.arange(VOCAB),
            )
            raw_rows.append(q)
        worst = max(abs(q.sum() - 1) for q in raw_rows)
        evaluated = {}
        for identity, model in models.items():
            gain = model.gain(data)
            delta = model.offsets(data, positions)
            for row, pos, q in zip(delta, positions, raw_rows, strict=True):
                y = int(raw[offset + pos])
                mass = q * np.exp(row[group.bins])
                p = mass / mass.sum()
                worst = max(
                    worst,
                    abs(p.sum() - 1),
                    abs(np.log(p[y] / q[y]) - gain[pos]),
                    abs(np.log(q[y]) + data.base_nll[pos]),
                    np.max(abs(np.bincount(group.bins, q) - data.q[data.context[pos]])),
                )
            out = {
                "gain_nats": float(gain.sum()),
                "nll_per_word": float(np.mean(data.base_nll - gain)),
                "gain_by_4096_words": gain.reshape(8, -1).sum(axis=1).tolist(),
            }
            if model.direct is not None:
                keys = encode(coordinates(data, model.size, model.lags), model.size + 1)
                out["instances_with_stored_row"] = int(
                    np.isin(keys, model.direct[0]).sum()
                )
            evaluated[identity] = out
        assert worst < 2e-12, worst
        reports.append(
            {
                "offset": offset,
                "prefix_sha256": digest,
                "full_row_max_error": float(worst),
                "models": evaluated,
            }
        )
    return {
        "registration": REGISTRATION,
        "train_offset": START,
        "train_size": TRAIN,
        "validation_size": N,
        "fit_validation_sha256": DIGEST,
        "pooled_bias_q12": bias.tolist(),
        "raw_rank_ids": base.bg.names[:64].tolist(),
        "fit_wall_seconds_one_cpu_thread": fit_seconds,
        "work": dict(book.work),
        "panels": book.panels,
        "candidates": dict(book.counts),
        "models": {k: v.spec for k, v in models.items()},
        "selected": chosen,
        "reports": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = experiment(args.data_dir)
    result_text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(result_text.encode())
    else:
        print(result_text, end="")
