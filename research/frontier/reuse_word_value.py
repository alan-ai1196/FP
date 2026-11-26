"""Use a previously learned lexical bit in new prediction operations."""

import argparse
import base64
import json
import zlib
from itertools import product
from pathlib import Path

import numpy as np
from joint_word_value import HIGH, LOW, ClassMass, Sample, both_signs, minimize_scaled
from lexical_switch import tokens
from text import VOCAB
from threadpoolctl import threadpool_limits
from word_value import Base, quantized, sign_string

HERE = Path(__file__).resolve().parent
REGISTRATION = "5ce71e8"
TRAIN, N, START = 131072, 32768, 35000000
SHA = "ed3db66445a7ca1475fa6c46c0ceec2e292fc05e66eed2df4b19b7b8a44f7f72"
REPORTS = {
    37000000: "162bfcc0c18dc9fdfd9a84f34c17b3f3b8399d4f3ccf2b2e4189d9c540e4c8e7",
    39000000: "ee4f1d70b8239101d6a25609abdc47517ec3bf34d34323028f51ace55e804a8f",
    41000000: "327643717c2768cc872145219e731316625ad8de4393e7a2ad6a3f83da3e2306",
}
SIZES, LAGS, STAGES = (16, 64), (2, 4, 8), (1, 2, 4, 8)
G = 12
SIGN = np.array([-1, 1], dtype=np.int8)


def unpack_signs(string):
    return np.array([1 if c == "+" else -1 for c in string], dtype=np.int8)


class Prior:
    def __init__(self):
        results = json.loads((HERE / "joint_word_value_result.json").read_text())
        key = results["selected"]["joint_sign_shared_ranks"]["model"]
        self.spec = results["installed"][key]
        self.key = key
        self.names = results["ranked_raw_names"]
        self.z = unpack_signs(self.spec["z"])
        self.s = unpack_signs(self.spec["s"])
        b = np.r_[np.asarray(self.spec["bias_q12"]) / 4096, 0.0]
        self.logits = b + SIGN[:, None] * self.s * (self.spec["beta_q12"] / 4096)
        assert (
            self.spec["inputs"] == 64
            and self.spec["lag"] == 1
            and self.spec["outputs"] == G
        )


class Observations:
    def __init__(self, raw, start, n, base, grouping, prior):
        data = Sample(raw, start, n, base, grouping)
        self.input_rank, self.y = data.input_rank, data.y
        self.a = (prior.z[data.inputs(64, 1)] > 0).astype(np.int64)
        keys, self.context = np.unique(
            self.a * len(data.q) + data.context, return_inverse=True
        )
        parent, side = keys % len(data.q), keys // len(data.q)
        mass = data.q[parent] * np.exp(prior.logits[side])
        norm = mass.sum(axis=1)
        self.q = mass / norm[:, None]
        self.old_gain = prior.logits[self.a, self.y] - np.log(norm[self.context])
        self.nll = data.base_nll - self.old_gain


class Cells:
    """Compress repeated observations without changing any candidate likelihood."""

    def __init__(self, data, size, lag):
        self.size = size + 1
        self.cell = self.size * data.a + np.minimum(data.input_rank[lag], size)
        encoded, self.trace, self.freq = np.unique(
            self.cell * len(data.q) + data.context,
            return_inverse=True,
            return_counts=True,
        )
        self.rows = encoded // len(data.q)
        self.q = data.q[encoded % len(data.q)]
        self.y = data.y
        self.observed = np.bincount(
            self.cell * (G + 1) + self.y, minlength=2 * self.size * (G + 1)
        ).reshape(2 * self.size, G + 1)
        self.zero = np.zeros_like(self.observed, dtype=float)

    def grouped(self, values):
        return np.stack(
            [
                np.bincount(self.rows, weights=col, minlength=2 * self.size)
                for col in values.T
            ],
            axis=1,
        )

    def adjusted(self, logits):
        mass = self.q * np.exp(logits)[self.rows]
        return mass, mass.sum(axis=1)

    def moments(self, logits):
        mass, denom = self.adjusted(logits)
        probs = mass / denom[:, None]
        residual = self.observed - self.grouped(self.freq[:, None] * probs)
        return probs, residual.reshape(2, self.size, G + 1)

    def gains(self, logits):
        _, denom = self.adjusted(logits)
        return logits[self.cell, self.y] - np.log(denom[self.trace])


def simple_proposal(row_totals, name, h):
    moment = h @ row_totals
    s = np.where(moment >= 0, 1, -1).astype(np.int8)
    return float(np.abs(moment).sum()), name, None, s * s[-1], int(s[-1])


def proposals(r, menu):
    choices = []
    if menu != "product":
        totals = r.sum(axis=1)
        choices.extend(
            (
                simple_proposal(totals, "constant", np.ones(2, dtype=np.int8)),
                simple_proposal(totals, "bit", SIGN),
            )
        )
    for name in ("main", "product"):
        if menu not in (name, "either"):
            continue
        projected = r.sum(axis=0) if name == "main" else r[1] - r[0]
        s, w, value = both_signs(projected)
        direction = int(w[-1])
        w = direction * w
        if np.all(w == 1):
            name = "constant" if name == "main" else "bit"
            w = None
        choices.append((float(value), name, w, s, direction))
    return max(choices, key=lambda item: item[0])


def input_values(name, w, size):
    if name == "constant":
        return np.ones(2 * size, dtype=np.int8)
    if name == "bit":
        return np.repeat(SIGN, size)
    values = np.tile(w, 2)
    return values if name == "main" else values * np.repeat(SIGN, size)


def learn_atom(cells, current, menu, work):
    q, r = cells.moments(current)
    contrast, name, w, s, direction = proposals(r, menu)
    h = input_values(name, w, cells.size)
    signed = direction * h
    observed = float(signed @ cells.observed @ s)
    m = (q @ s) * signed[cells.rows]
    assert abs(observed - cells.freq @ m - contrast) < 2e-7

    def gain(beta):
        return beta * observed - np.log(np.cosh(beta) + m * np.sinh(beta)) @ cells.freq

    lo, hi = 0, 8191
    while lo < hi:
        mid = (lo + hi) // 2
        slope = np.tanh(mid / 4096)
        if observed - (m + slope) / (1 + m * slope) @ cells.freq > 0:
            lo = mid + 1
        else:
            hi = mid
    beta = max((max(0, lo - 1), lo), key=lambda v: gain(v / 4096))
    work["residual_tables"] += 1
    work["output_masks"] += (1 << G) * (2 if menu == "either" else 1)
    work["compressed_observations_per_residual_pass"] += len(q)
    size = cells.freq.sum()
    assert gain(contrast / size) + 1e-7 >= contrast**2 / (2 * size)
    return (
        {
            "op": name,
            "w": sign_string(w) if w is not None else None,
            "s": sign_string(s),
            "q12": direction * beta,
            "contrast": contrast,
        },
        (direction * beta / 4096) * h[:, None] * s,
    )


def packet_bits(atoms, size, prior):
    # Four-bit reference fields select among eight new entries and the old table.
    heads = {a["s"] for a in atoms} - {sign_string(prior.s)}
    names = {a["w"] for a in atoms if a["w"] is not None}
    if size == 64:
        names.discard(sign_string(prior.z * prior.z[-1]))
    # Fixed header carries family, lag, size, stage and the two dictionary lengths.
    return 20 + size * len(names) + G * len(heads) + 24 * len(atoms)


def packed(table):
    return base64.b64encode(
        zlib.compress(np.asarray(table, dtype="<i2").tobytes())
    ).decode("ascii")


class Dense:
    def __init__(self, cells, additive):
        self.cells = cells
        self.additive = additive
        weight = cells.freq[:, None] * cells.q[:, :-1] * (1 - cells.q[:, :-1])
        info = cells.grouped(weight)
        self.info = (
            np.concatenate(
                (info[: cells.size] + info[cells.size :], info.sum(axis=0)[None, :])
            )
            if additive
            else info
        )

    def table(self, values):
        if self.additive:
            out = np.vstack((values[:-1] - values[-1], values[:-1] + values[-1]))
        else:
            out = values
        return np.pad(out, ((0, 0), (0, 1)))

    def fit(self, ridge, start):
        cells = self.cells

        def objective(x):
            logits = self.table(x)
            mass, norm = cells.adjusted(logits)
            val = (
                cells.freq @ np.log(norm)
                - np.sum(cells.observed * logits)
                + 0.5 * ridge * np.sum(x * x)
            )
            gradient = (
                cells.grouped(mass[:, :-1] * (cells.freq / norm)[:, None])
                - cells.observed[:, :-1]
            )
            if self.additive:
                lo, hi = gradient[: cells.size], gradient[cells.size :]
                gradient = np.vstack((lo + hi, (hi - lo).sum(axis=0)))
            return val, gradient + ridge * x

        start, work = minimize_scaled(
            objective, start, np.sqrt(ridge + self.info), LOW, HIGH
        )
        q12 = quantized(start)
        return start, q12, self.table(q12.astype(float) / 4096), work


class Selection:
    def __init__(self):
        self.selected = {}
        self.counts = {}
        self.work = {
            "residual_tables": 0,
            "output_masks": 0,
            "compressed_observations_per_residual_pass": 0,
            "dense_objectives": 0,
            "largest_compressed_panel": 0,
        }

    def consider(self, valid, spec, bits, table):
        family = spec["family"]
        self.counts[family] = self.counts.get(family, 0) + 1
        gain = float(valid.gains(table).sum())
        for mode, price in (("gross", 0.0), ("priced", np.log(2))):
            key = family + "_" + mode
            order = (gain - price * bits, -bits)
            if key not in self.selected or order > self.selected[key][0]:
                self.selected[key] = (
                    order,
                    {**spec, "bits": bits, "validation_gain": gain},
                    table.copy(),
                )


def fit(train, val, prior, book):
    for ni, lag in product(SIZES, LAGS):
        fit, valid = Cells(train, ni, lag), Cells(val, ni, lag)
        common = {"inputs": ni, "lag": lag}
        book.work["largest_compressed_panel"] = max(
            book.work["largest_compressed_panel"], len(fit.freq)
        )
        if ni == SIZES[0] and lag == LAGS[0]:
            book.consider(valid, {**common, "family": "installed"}, 0, fit.zero)
        for menu in ("main", "product", "either"):
            table = fit.zero.copy()
            atoms = []
            for stage in range(1, max(STAGES) + 1):
                atom, delta = learn_atom(fit, table, menu, book.work)
                atoms.append(atom)
                table += delta
                if stage in STAGES:
                    book.consider(
                        valid,
                        {**common, "family": menu, "atoms": atoms.copy()},
                        packet_bits(atoms, ni, prior),
                        table,
                    )
                    if ni == 16 and lag == 2 and stage == 2 and menu == "main":
                        book.consider(
                            valid,
                            {
                                **common,
                                "family": "matched_additive_two",
                                "atoms": atoms.copy(),
                            },
                            packet_bits(atoms, ni, prior),
                            table,
                        )
        for add, family in ((True, "dense_add"), (False, "dense_full")):
            dense = Dense(fit, add)
            start = np.zeros_like(dense.info)
            for ridge in (256, 32, 4):
                start, q12, table, work = dense.fit(ridge, start)
                book.work["dense_objectives"] += work
                info = {
                    **common,
                    "ridge": ridge,
                    "family": family,
                    "q12_zlib_base64": packed(q12),
                }
                bits = 7 + 14 * q12.size
                book.consider(valid, info, bits, table)
                if add:
                    atom, delta = learn_atom(fit, table, "product", book.work)
                    book.consider(
                        valid,
                        {**info, "family": "dense_add_product", "atoms": [atom]},
                        bits + packet_bits([atom], ni, prior),
                        table + delta,
                    )


def reconstruct(spec):
    n = spec["inputs"] + 1
    table = np.zeros((2 * n, G + 1))
    if "q12_zlib_base64" in spec:
        blob = zlib.decompress(base64.b64decode(spec["q12_zlib_base64"]))
        values = np.frombuffer(blob, dtype="<i2").reshape(-1, G).astype(float) / 4096
        if spec["family"] == "dense_full":
            table[:, :-1] = values
        else:
            table[:n, :-1], table[n:, :-1] = (
                values[:-1] - values[-1],
                values[:-1] + values[-1],
            )
    for atom in spec.get("atoms", []):
        w = unpack_signs(atom["w"]) if atom["w"] else None
        h = input_values(atom["op"], w, n)
        table += (atom["q12"] / 4096) * h[:, None] * unpack_signs(atom["s"])
    return table


def cross_odds(table):
    lower, upper = np.split(table, 2)
    diff = upper - lower
    return float(np.ptp(diff[:, None] - diff[None, :], axis=2).max())


def population_checks():
    # Balanced marginals make every one-input feature exactly uninformative.
    cases = 0
    for w0, s0 in product(product((-1, 1), repeat=4), repeat=2):
        if sum(w0) or sum(s0):
            continue
        w, s = np.array(w0), np.array(s0)
        signed = SIGN[:, None, None] * w[None, :, None] * s[None, None, :]
        counts = 2 + signed
        assert np.all(counts > 0) and np.all(counts.sum(axis=2) == 8)
        residual = counts - 2
        assert np.all(residual.sum(axis=0) == 0) and np.all(residual.sum(axis=1) == 0)
        value, op, wi, sj, direction = proposals(residual, "either")
        assert op == "product" and value == 32
        recovered = direction * input_values(op, wi, 4).reshape(2, 4, 1) * sj
        assert np.array_equal(recovered, signed)
        cases += 1
    # The conditional-gradient algorithm has an explicit sparse, bounded comparator.
    B = 1.0
    true = sum(
        coef * np.outer(w, s)
        for coef, w, s in (
            (0.42, [1, 1, -1, -1], [1, -1, 1, -1]),
            (0.31, [1, -1, -1, 1], [-1, -1, 1, 1]),
            (0.22, [-1, 1, 1, 1], [1, -1, -1, 1]),
        )
    )

    def probs(h):
        mass = np.exp(SIGN[:, None, None] * h)
        return mass / mass.sum(axis=2, keepdims=True)

    actual = probs(true)
    h = np.zeros_like(true)
    path = []
    for k in range(65):
        current = probs(h)
        r = (actual - current) / 8
        matrix = r[1] - r[0]
        s, w, norm = both_signs(matrix)
        primal = np.sum(actual * np.log(actual / current)) / 8
        dual_gap = B * norm - np.sum(matrix * h)
        assert primal <= dual_gap + 1e-14 and primal <= 8 * B * B / (k + 2) + 1e-14
        if k in (0, 1, 2, 4, 8, 16, 32, 64):
            path.append(
                {
                    "steps": k,
                    "excess_nats": float(primal),
                    "gradient_gap": float(dual_gap),
                }
            )
        step = 2 / (k + 2)
        h = (1 - step) * h + step * B * np.outer(w, s)
    return {
        "balanced_integer_sources_recovered": cases,
        "bounded_radius": B,
        "conditional_gradient_path": path,
    }


def experiment(directory):
    checks = population_checks()
    prior, base = Prior(), Base(directory)
    assert prior.names == base.bg.names.tolist()
    grouping = ClassMass(base, G)
    raw = tokens("train_source", START + TRAIN + N, SHA, directory)
    train = Observations(raw, START, TRAIN, base, grouping, prior)
    val = Observations(raw, START + TRAIN, N, base, grouping, prior)
    book = Selection()
    fit(train, val, prior, book)
    models, selected = {}, {}
    for key, (order, info, table) in book.selected.items():
        assert np.array_equal(reconstruct(info), table)
        name = next((n for n, v in models.items() if v == info), None)
        if name is None:
            name = info["family"] + "-" + str(len(models) + 1)
            models[name] = info
        selected[key] = {
            "model": name,
            "validation_score_after_price": order[0],
            "maximum_interaction_log_odds_contrast": cross_odds(table),
        }
    reports = []
    for start, digest in REPORTS.items():
        raw = tokens("train_source", start + N, digest, directory)
        data = Observations(raw, start, N, base, grouping, prior)
        pos = 1234
        words = np.arange(VOCAB)
        raw_q = base.point(
            np.full(VOCAB, int(raw[start + pos - 2])),
            np.full(VOCAB, int(raw[start + pos - 1])),
            words,
        )
        raw_old = raw_q * np.exp(prior.logits[data.a[pos], grouping.bins])
        raw_old /= raw_old.sum()
        y = int(raw[start + pos])
        worst = max(abs(raw_q.sum() - 1), abs(-np.log(raw_old[y]) - data.nll[pos]))
        panel, methods = {}, {}
        for key, (_, info, table) in book.selected.items():
            c = info["inputs"], info["lag"]
            if c not in panel:
                panel[c] = Cells(data, *c)
            sample = panel[c]
            g = sample.gains(table)
            shifts = table[sample.cell[pos], grouping.bins]
            ref = raw_old * np.exp(shifts)
            ref /= ref.sum()
            worst = max(
                worst, abs(ref.sum() - 1), abs(np.log(ref[y] / raw_old[y]) - g[pos])
            )
            methods[key] = {
                "gain_over_installed": float(g.sum()),
                "gain_over_original_base": float((g + data.old_gain).sum()),
                "nll_per_word": float((data.nll - g).mean()),
                "gain_by_4096_words": g.reshape(8, -1).sum(axis=1).tolist(),
            }
        assert worst < 2e-12
        reports.append(
            {
                "start": start,
                "prefix_sha256": digest,
                "original_rule_gain": float(data.old_gain.sum()),
                "full_row_max_error": float(worst),
                "methods": methods,
            }
        )
    return {
        "registration": REGISTRATION,
        "frozen_model": prior.key,
        "frozen_bits_rank_reuse": prior.spec["incremental_bits"],
        "frozen_bits_standalone": prior.spec["standalone_bits"],
        "train_offset": START,
        "train_size": TRAIN,
        "validation_size": N,
        "fit_validation_sha256": SHA,
        "audits": checks,
        "work": book.work,
        "candidates": book.counts,
        "models": models,
        "selected": selected,
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
