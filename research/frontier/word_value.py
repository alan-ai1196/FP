"""Construct and compare shared Boolean corrections to an ordinary word predictor."""

import argparse
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path

import numpy as np
from calibrated_word_rule import Trigrams, estimate_row
from lexical_switch import (
    BACKGROUND,
    FIT_END,
    FIT_SHA,
    FIT_START,
    TRAIN,
    Background,
    tokens,
    windows,
)
from linked_table import Words
from text import VOCAB
from threadpoolctl import threadpool_limits

REGISTRATION = "6cd3363"
GROUPS = (8, 32, 128)
MEMORIES = (1, 3, 5, 7)
BETAS = (1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2)
GAMMAS = (4, 32, 256, 2048, 16384)
SPAN = 8
WIDTH = 1 << SPAN
LENGTH = 65536
FIT_OFFSET = 24000000
FIT_HASH = "a7bd7e3a8c50a24055580bd9d66c374859a43b66fe501414a108551954497c48"
REPORTS = (
    (
        "train_source",
        26000000,
        "c79d8896d20098963ccf5e16d3e39932bd06b9598580518c9ae6eea7f90f3e7d",
    ),
    (
        "reporting_source",
        1900000,
        "e08b01b3393c877e9c05ca42c56f9f5aa8b4c44e240c5ab71be000c0ed67f42d",
    ),
)


def quantized(values):
    return np.clip(np.rint(4096 * values), -8192, 8191).astype(np.int16)


def tilt_gain(target, mean, theta):
    return theta * target - np.log(np.cosh(theta) + mean * np.sinh(theta))


class Base:
    def __init__(self, directory):
        raw = tokens("train_source", FIT_END, FIT_SHA, directory)
        self.bg = Background(*windows(raw, FIT_START, BACKGROUND))
        self.kn = Trigrams(self.bg)
        fit = windows(raw, FIT_START + BACKGROUND, TRAIN)
        y = fit[-1]
        p = self.kn.forecasts(*fit)["kn_0.9"]
        self.lexical = estimate_row(
            y, np.bincount(y, minlength=VOCAB), self.bg.unigram, p, 1 / 16, 65536
        )
        self.mix = 1 / 16
        recounted = np.bincount(
            self.bg.aby[0] % VOCAB, weights=self.bg.aby[1], minlength=VOCAB
        )
        assert np.array_equal(
            np.argsort(-recounted, kind="stable")[:128], self.bg.names[:128]
        )

    def point(self, a, b, y):
        return (1 - self.mix) * self.kn.forecasts(a, b, y)[
            "kn_0.9"
        ] + self.mix * self.lexical[y]


class Group:
    def __init__(self, base, size):
        self.size = size
        self.member = np.zeros(VOCAB, dtype=bool)
        self.member[base.bg.names[:size]] = True
        self.names = base.bg.names[:size].tolist()
        kn = base.kn
        d = 0.9
        raw, value = kn.bigram
        first = np.bincount(
            raw // VOCAB,
            weights=(value - d) * self.member[raw % VOCAB],
            minlength=VOCAB,
        )
        mass = kn.unigram[self.member].sum()
        self.lower = np.divide(
            first + d * kn.lower_types * mass,
            kn.lower_total,
            out=np.full(VOCAB, mass),
            where=kn.lower_total > 0,
        )
        ab, total = base.bg.ab
        triples, counts = base.bg.aby
        pos = np.searchsorted(ab, triples // VOCAB)
        assert np.all(ab[pos] == triples // VOCAB)
        top = np.bincount(
            pos, weights=(counts - d) * self.member[triples % VOCAB], minlength=len(ab)
        )
        types = np.bincount(pos, minlength=len(ab))
        high = (top + d * types * self.lower[ab % VOCAB]) / total
        lexical = base.lexical[self.member].sum()
        self.high = (1 - base.mix) * high + base.mix * lexical
        self.lower = (1 - base.mix) * self.lower + base.mix * lexical
        self.contexts = ab

    def mean(self, a, b):
        key = a * VOCAB + b
        pos = np.minimum(np.searchsorted(self.contexts, key), len(self.contexts) - 1)
        return (
            2 * np.where(self.contexts[pos] == key, self.high[pos], self.lower[b]) - 1
        )


class Window:
    def __init__(self, data, start, n, group):
        a, b, y = windows(data, start, n)
        self.target = 2 * group.member[y].astype(np.int8) - 1
        self.original = group.mean(a, b)
        self.code = np.zeros(n, dtype=np.uint16)
        for j in range(SPAN):
            negative = ~group.member[data[start - j - 1 : start + n - j - 1]]
            self.code |= negative.astype(np.uint16) << j

    def calibrate(self, intercept):
        self.mean = np.tanh(np.arctanh(self.original) + intercept)
        self.static = tilt_gain(self.target, self.original, intercept)

    def totals(self, beta):
        positive = tilt_gain(self.target, self.mean, beta)
        negative = tilt_gain(self.target, self.mean, -beta)
        return np.stack(
            [
                np.bincount(self.code, weights=row, minlength=WIDTH)
                for row in ((positive + negative) / 2, (positive - negative) / 2)
            ]
        )

    def increments(self, offset_q, intercept_q):
        theta = (intercept_q + offset_q[self.code].astype(np.int32)) / 4096
        return tilt_gain(self.target, self.original, theta)


def intercept(train):
    natural = np.arctanh(train.original)
    target_sum = train.target.sum()
    lo, hi = -8192, 8191
    while lo < hi:
        mid = (lo + hi) // 2
        if np.tanh(natural + mid / 4096).sum() < target_sum:
            lo = mid + 1
        else:
            hi = mid
    return max(
        (max(-8192, lo - 1), lo),
        key=lambda t: tilt_gain(train.target, train.original, t / 4096).sum(),
    )


def reduce_rows(rows, width):
    return rows.reshape(2, -1, width).sum(axis=1)


def sign_string(labels):
    return "".join("+" if x > 0 else "-" for x in labels)


class Selection:
    """Rank complete installed models on one validation slice before examining reports."""

    def __init__(self):
        self.best = {}
        self.candidates = {}
        self.coordinate_checks = 0
        self.eigenproblems = 0

    def consider(self, family, info, delta, bits, validation_gain):
        self.candidates[family] = self.candidates.get(family, 0) + 1
        for pricing in ("unpriced", "priced", "shared_ranks"):
            key = (family, pricing)
            transmitted = bits - (16 * info["group"] if bits else 0)
            paid = bits if pricing == "priced" else transmitted
            score = validation_gain - (np.log(2) * paid if pricing != "unpriced" else 0)
            # Prefer fewer installed bits on an exact validation tie.
            order = (float(score), -bits)
            if key not in self.best or order > self.best[key][0]:
                self.best[key] = (
                    order,
                    {
                        **info,
                        "bits": bits,
                        "bits_with_ranks_rebuilt_from_base": transmitted,
                        "validation_gain": float(validation_gain),
                        "selection_score": float(score),
                    },
                    delta.copy(),
                )


def suffix_tree(rows, price):
    width = rows.shape[1]
    span = width.bit_length() - 1
    assert 1 << span == width
    levels = [reduce_rows(rows, 1 << j) for j in range(span + 1)]
    codes = np.arange(width)
    best = np.empty(width, dtype=float)
    signs = np.zeros(width, dtype=np.int8)
    tree = [""] * width
    costs = np.zeros(width, dtype=int)
    for depth in range(span, -1, -1):
        size = 1 << depth
        constant, slope = levels[depth]
        for node in range(size):
            sign = 1 if slope[node] > 0 else -1
            gross = constant[node] + abs(slope[node])
            if gross <= 0:
                gross, sign = 0.0, 0
            leaf = gross - 3 * price
            if depth < span and best[node] + best[node + size] - price > leaf + 1e-12:
                best[node] += best[node + size] - price
                tree[node] = "(" + tree[node] + tree[node + size] + ")"
                costs[node] += costs[node + size] + 1
            else:
                best[node] = leaf
                tree[node] = "+" if sign > 0 else "-" if sign < 0 else "0"
                costs[node] = 3
                signs[(codes % size) == node] = sign
    return signs, str(tree[0]), int(costs[0])


def continuous(train, depth, penalty):
    size = 1 << depth
    contexts = train.code % size
    sufficient = np.bincount(contexts, weights=train.target, minlength=size)
    natural = np.arctanh(train.mean)
    lo, hi = np.full(size, -2.0), np.full(size, 8191 / 4096)
    for _ in range(20):
        mid = (lo + hi) / 2
        fitted = np.bincount(
            contexts, weights=np.tanh(natural + mid[contexts]), minlength=size
        )
        up = sufficient > fitted + penalty * mid
        lo = np.where(up, mid, lo)
        hi = np.where(up, hi, mid)
    return quantized((lo + hi) / 2)


def fit_group(book, train, valid, k):
    initial = intercept(train)
    train.calibrate(initial / 4096)
    valid.calibrate(initial / 4096)
    static = float(valid.static.sum())
    # Family, group selector and a signed Q12 intercept, followed by packed raw word IDs.
    header = 4 + 2 + 14 + 16 * k
    common = {"group": k, "intercept_q12": int(initial)}
    zero = np.zeros(WIDTH, dtype=np.int16)
    codes = np.arange(WIDTH)
    last = 1 - 2 * (codes % 2)
    book.consider("static", common, zero, header, static)
    for family in (
        "last_sign",
        "free_edge",
        "same_window",
        "boundary_pair",
        "shared",
        "motif",
        "suffix_tree",
        "ridge",
    ):
        book.consider(family, {**common, "fallback": "static"}, zero, header, static)
    for beta in BETAS:
        trains = train.totals(beta)
        vals = valid.totals(beta)
        beta_q = int(4096 * beta)

        def discrete(family, info, signs, bits, vals=vals, beta=beta, beta_q=beta_q):
            gain = static + vals[0] @ (signs != 0) + vals[1] @ signs
            book.consider(
                family,
                {**common, **info, "beta": beta},
                (beta_q * signs.astype(np.int16)),
                header + bits,
                gain,
            )

        for direction in (-1, 1):
            discrete("last_sign", {"direction": direction}, direction * last, 4)
        for memory in MEMORIES:
            nvertex = 1 << memory
            history = codes % (2 * nvertex)
            for name, depth in (("free_edge", memory + 1), ("same_window", memory)):
                values = np.sign(reduce_rows(trains, 1 << depth)[1]).astype(np.int8)
                values[values == 0] = 1
                discrete(
                    name,
                    {"memory": memory, "signs": sign_string(values)},
                    values[codes % len(values)],
                    2 + 3 + len(values),
                )
            for ell in sorted({memory, *range(1, min(3, memory - 1) + 1)}):
                width = 1 << ell
                old, new = history >> (memory + 1 - ell), history % width
                idx = old * width + new
                directed = np.bincount(
                    idx, weights=trains[1] * last, minlength=width**2
                ).reshape(width, width)
                if ell < memory:
                    signs = np.where(directed.ravel() >= 0, 1, -1)
                    discrete(
                        "boundary_pair",
                        {"memory": memory, "subword": ell, "signs": sign_string(signs)},
                        last * signs[idx],
                        2 + 2 + 3 + width**2,
                    )
                graph = Words(ell)
                for direction in (-1, 1):
                    matrix = direction * (directed + directed.T)
                    np.fill_diagonal(matrix, 0)
                    _, start, _ = graph.forest(matrix, 0.5)
                    labels, checks = graph.spectral(matrix, start)
                    book.coordinate_checks += checks
                    book.eigenproblems += 1
                    labels *= labels[0]
                    model = "shared" if ell == memory else "motif"
                    discrete(
                        model,
                        {
                            "memory": memory,
                            "subword": ell,
                            "direction": direction,
                            "labels": sign_string(labels),
                        },
                        direction * last * labels[old] * labels[new],
                        2 + (2 if ell < memory else 0) + 4 + width - 1,
                    )
        for scale in (0.5, 2.0, 8.0, 32.0):
            signs, tree, tree_bits = suffix_tree(trains, scale * np.log(2))
            discrete(
                "suffix_tree",
                {"tree": tree, "training_price_log2": scale},
                signs,
                tree_bits + 3,
            )
    for memory in MEMORIES:
        depth = memory + 1
        for penalty in GAMMAS:
            q = continuous(train, depth, penalty)
            delta = q[codes % len(q)]
            validation = valid.increments(delta, initial).sum()
            book.consider(
                "ridge",
                {**common, "depth": depth, "ridge": penalty, "q12_rows": q.tolist()},
                delta,
                header + 2 + 14 * len(q),
                validation,
            )


def verify_full_row(base, group, data, start, position, theta, predicted_ratio):
    a = int(data[start + position - 2])
    b = int(data[start + position - 1])
    y = np.arange(VOCAB)
    row = base.point(np.full(VOCAB, a), np.full(VOCAB, b), y)
    signs = 2 * group.member.astype(np.int8) - 1
    m = group.mean(np.array([a]), np.array([b]))[0]
    adjusted = row * np.exp(theta * signs) / (np.cosh(theta) + m * np.sinh(theta))
    obs = int(data[start + position])
    error = max(
        abs(row.sum() - 1),
        abs(adjusted.sum() - 1),
        abs(row @ signs - m),
        abs(np.log(adjusted[obs] / row[obs]) - predicted_ratio),
    )
    assert error < 3e-12
    return float(error)


def exact_checks():
    # Evaluate full normalized likelihoods and compare ratios with edge odds products.
    checked = 0
    for memory in (1, 2, 3):
        vertices = 1 << memory
        ratios, individual = [], []
        for e in range(2 * vertices):
            p = F(1 + e % 5, 7)
            y = 1 if e % 3 else -1
            x = 1 - 2 * (e % 2)
            outcome = p if y > 0 else 1 - p
            probs = []
            for f in (1, -1):
                r = F(2) ** (x * f)
                probs.append(outcome * r**y / (p * r + (1 - p) / r))
            individual.append(probs)
            ratios.append(probs[1] / probs[0])
        pooled = prod(values[0] for values in individual)
        for tail in product((-1, 1), repeat=vertices - 1):
            f = (1, *tail)
            anti = [f[e // 2] != f[e % vertices] for e in range(2 * vertices)]
            exact = prod(
                values[int(b)] for values, b in zip(individual, anti, strict=True)
            )
            assert exact / pooled == prod(
                r for r, b in zip(ratios, anti, strict=True) if b
            )
            checked += 1

    # Compare all 147 ternary trees of depth at most two with the dynamic program.
    def trees(depth):
        candidates = [(np.full(1 << depth, s), 3) for s in (-1, 0, 1)]
        if depth:
            child = trees(depth - 1)
            for (left, bl), (right, br) in product(child, repeat=2):
                combined = np.empty(1 << depth, dtype=int)
                combined[::2], combined[1::2] = left, right
                candidates.append((combined, bl + br + 1))
        return candidates

    options = trees(2)
    assert len(options) == 147
    rows = np.array([[-0.75, -0.125, -0.375, -2.5], [-2.0, 0.25, 1.25, 0.75]])
    for price in (0, 0.03125, 0.25, 1):

        def merit(s, bits, price=price):
            return rows[0] @ (s != 0) + rows[1] @ s - price * bits

        signs, _, bits = suffix_tree(rows, price)
        assert merit(signs, bits) == max(merit(s, b) for s, b in options)
    cancellations = 0
    for memory in (2, 3, 5):
        for ell in range(1, min(3, memory) + 1):
            for bits in range(2 ** ((1 << ell) - 1)):
                f = [1 - 2 * ((bits << 1 >> i) & 1) for i in range(1 << ell)]
                mask = (1 << ell) - 1
                for e in range(2 << memory):
                    older, newer = e >> 1, e % (1 << memory)
                    before = prod(
                        f[(older >> j) & mask] for j in range(memory + 1 - ell)
                    )
                    after = prod(
                        f[(newer >> j) & mask] for j in range(memory + 1 - ell)
                    )
                    assert before * after == f[e >> (memory + 1 - ell)] * f[e & mask]
                    cancellations += 1
    return {
        "rational_normalized_likelihood_ratios": checked,
        "tree_score_comparisons": 4 * len(options),
        "exact_composed_window_cancellations": cancellations,
    }


def experiment(directory):
    exact = exact_checks()
    base = Base(directory)
    groups = {s: Group(base, s) for s in GROUPS}
    raw = tokens("train_source", FIT_OFFSET + TRAIN + LENGTH, FIT_HASH, directory)
    book = Selection()
    empty = np.zeros(WIDTH, dtype=np.int16)
    book.consider("base", {"group": GROUPS[0], "intercept_q12": 0}, empty, 0, 0)
    with threadpool_limits(limits=1):
        for k, group in groups.items():
            train = Window(raw, FIT_OFFSET, TRAIN, group)
            val = Window(raw, FIT_OFFSET + TRAIN, LENGTH, group)
            fit_group(book, train, val, k)
        reports = []
        for role, start, digest in REPORTS:
            data = tokens(role, start + LENGTH, digest, directory)
            stats = {
                k: Window(data, start, LENGTH, group) for k, group in groups.items()
            }
            base_nll = -np.log(base.point(*windows(data, start, LENGTH)))
            rows = {}
            max_error = 0.0
            for (family, mode), (_, spec, delta) in book.best.items():
                k = spec["group"]
                w = stats[k]
                gains = w.increments(delta, spec["intercept_q12"])
                block_gain = gains.reshape(8, -1).sum(axis=1)
                rows[family + "_" + mode] = {
                    "nll_per_word": float(np.mean(base_nll - gains)),
                    "gain_nats": float(gains.sum()),
                    "gain_by_8192_words": block_gain.tolist(),
                }
                if family in ("shared", "motif") and "labels" in spec:
                    pooled = (
                        spec["direction"]
                        * spec["beta"]
                        * (1 - 2 * (w.code.astype(int) % 2))
                    )
                    old = tilt_gain(
                        w.target, w.original, spec["intercept_q12"] / 4096 + pooled
                    )
                    rows[family + "_" + mode]["gain_over_constant_f_same_scale"] = (
                        float((gains - old).sum())
                    )
                pos = 1234
                theta = (spec["intercept_q12"] + int(delta[w.code[pos]])) / 4096
                max_error = max(
                    max_error,
                    verify_full_row(
                        base, groups[k], data, start, pos, theta, gains[pos]
                    ),
                )
            reports.append(
                {
                    "role": role,
                    "start": start,
                    "prefix_sha256": digest,
                    "complete_row_max_error": max_error,
                    "methods": rows,
                }
            )
    return {
        "exact_checks": exact,
        "registration": REGISTRATION,
        "background_base": "kn_0.9 with previous 1/16 lexical row, prior mass 65536",
        "fit_start": FIT_OFFSET,
        "fit_and_select_prefix_sha256": FIT_HASH,
        "train_tokens": TRAIN,
        "select_tokens": LENGTH,
        "frozen_lexical_row_sha256": hashlib.sha256(
            np.asarray(base.lexical, dtype="<f8").tobytes()
        ).hexdigest(),
        "group_words": {k: g.names for k, g in groups.items()},
        "candidate_counts": book.candidates,
        "spectral_proposals": book.eigenproblems,
        "coordinate_checks": book.coordinate_checks,
        "fits": {f + "_" + p: spec for (f, p), (_, spec, _) in book.best.items()},
        "reports": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(experiment(args.data_dir), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
