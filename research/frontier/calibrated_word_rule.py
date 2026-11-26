"""Refit the rolling lexical rule after selecting the static full-vocabulary model."""

import argparse
import hashlib
import json
from copy import copy
from pathlib import Path

import numpy as np
from lexical_switch import (
    BACKGROUND,
    FIT_END,
    FIT_SHA,
    FIT_START,
    POOLED,
    TRAIN,
    VALID,
    WORD,
    Background,
    checksum,
    counted,
    fit,
    lookup,
    native,
    summarize,
    tokens,
    windows,
)
from pair_dictionary import representatives
from rolling_word_rule import (
    WEIGHT,
    D,
    R,
    Window,
    fit_rules,
    history_codes,
    incremental,
    select,
)
from text import VOCAB

REGISTRATION = "6c623ca"
DISCOUNTS = (0.25, 0.5, 0.75, 0.9)
WEIGHTS = (1 / 16, 1 / 8, 1 / 4, 1 / 2, 3 / 4, 1.0)
TAUS = (64, 1024, 8192, 65536, 262144, 1048576, None)
REPORTS = (
    (
        "train_source",
        23000000,
        "09e677b7d238c0be7e5b9c2baed808270adc31eb9cebd0ea91c142b554dd6daa",
    ),
    (
        "reporting_source",
        1710000,
        "9122dd93250446a4d95c637bf34283c21ba64aae4be3df8af17b55c82b6bce8e",
    ),
)


class Trigrams:
    def __init__(self, bg):
        self.bg = bg
        self.bigram = counted(bg.aby[0] % VOCAB**2)
        self.lower_total = np.bincount(
            self.bigram[0] // VOCAB, weights=self.bigram[1], minlength=VOCAB
        )
        self.lower_types = np.bincount(self.bigram[0] // VOCAB, minlength=VOCAB)
        self.higher_types = counted(bg.aby[0] // VOCAB)
        continuations = np.bincount(bg.by[0] % VOCAB, minlength=VOCAB)
        self.unigram = (continuations + 0.5) / (continuations.sum() + VOCAB / 2)

    def forecasts(self, a, b, y):
        history = a * VOCAB + b
        lower = lookup(self.bigram, b * VOCAB + y)
        lower_total = self.lower_total[b]
        count = lookup(self.bg.aby, history * VOCAB + y)
        total = lookup(self.bg.ab, history)
        types = lookup(self.higher_types, history)
        probs = {"additive": self.bg.forecasts(a, b, y)[2]}
        for d in DISCOUNTS:
            first = (
                np.maximum(lower - d, 0) + d * self.lower_types[b] * self.unigram[y]
            ) / np.maximum(lower_total, 1)
            first = np.where(lower_total > 0, first, self.unigram[y])
            second = (np.maximum(count - d, 0) + d * types * first) / np.maximum(
                total, 1
            )
            probs[f"kn_{d}"] = np.where(total > 0, second, first)
        return probs


def calibrated(w, base, weight, q):
    result = copy(w)
    result.base = base
    part = weight * q[w.y]
    result.pool = (1 - weight) * base + part
    result.resp = part / result.pool
    return result


def estimate_row(y, counts, prior, base, weight, tau):
    if tau is None:
        return prior
    q = (counts + tau * prior) / (len(y) + tau)
    # At unit weight the responsibility is identically one.
    if weight == 1:
        return q
    shared = (1 - weight) * base
    for _ in range(12):
        part = weight * q[y]
        soft = np.bincount(y, weights=part / (shared + part), minlength=VOCAB)
        q = (soft + tau * prior) / (soft.sum() + tau)
    return q


def base_search(train, val, bg, training_bases, validation_bases, old_average):
    counts = np.bincount(train.y, minlength=VOCAB)
    best, best_positive, pure = None, None, None
    grid = []

    def consider(name, weight, tau, q, origin):
        nonlocal best, best_positive, pure
        p = (1 - weight) * validation_bases[name] + weight * q[val.y]
        nll = float(-np.log(p).sum())
        info = {
            "base": name,
            "weight": weight,
            "pseudocount": tau,
            "row_source": origin,
            "nll": nll,
        }
        grid.append(info)
        if best is None or nll < best[0]["nll"]:
            best = (info, q.copy())
        if weight > 0 and (best_positive is None or nll < best_positive[0]["nll"]):
            best_positive = (info, q.copy())
        if weight == 0 and (pure is None or nll < pure["nll"]):
            pure = info

    for name, base in training_bases.items():
        consider(name, 0, None, bg.unigram, "pure")
        for weight in WEIGHTS:
            for tau in TAUS:
                q = estimate_row(train.y, counts, bg.unigram, base, weight, tau)
                consider(name, weight, tau, q, "prior" if tau is None else "em")
    consider("additive", WEIGHT, None, old_average, "previous_static_average")
    return best, best_positive, pure, grid


def continuous_rows(w, mass, bisections=26):
    best = None
    for t in representatives(D):
        mean = mass @ t
        residual = w.resp * (t[w.group] - mean)
        z = history_codes(t)[w.history]
        lo = np.full(8, -0.75 / (1 - 0.75 * mean))
        hi = np.full(8, 0.75 / (1 + 0.75 * mean))
        for _ in range(bisections):
            mid = (lo + hi) / 2
            deriv = np.bincount(
                z, weights=residual / (1 + mid[z] * residual), minlength=8
            )
            lo = np.where(deriv > 0, mid, lo)
            hi = np.where(deriv > 0, hi, mid)
        eta = (lo + hi) / 2
        # Include exact endpoints and zero so a constant or monotone row is
        # handled directly, including rows without a single nonzero residual.
        choices = np.stack(
            (
                np.zeros(8),
                eta,
                np.full(8, -0.75 / (1 - 0.75 * mean)),
                np.full(8, 0.75 / (1 + 0.75 * mean)),
            )
        )
        rows = np.stack(
            [
                np.bincount(z, weights=np.log1p(e[z] * residual), minlength=8)
                for e in choices
            ]
        )
        winners = rows.argmax(axis=0)
        eta = choices[winners, np.arange(8)]
        value = float(rows[winners, np.arange(8)].sum())
        if best is None or value > best[0]:
            best = (value, t.copy(), eta.copy())
    return best


def fit_history(train, v, base_train, base_valid, candidate, group):
    info, q = candidate
    train = calibrated(train, base_train[info["base"]], info["weight"], q)
    v = calibrated(v, base_valid[info["base"]], info["weight"], q)
    mass = np.bincount(group, weights=q, minlength=D)
    models, details = select(fit_rules(train, mass), train, v, mass)
    score, t, eta = continuous_rows(train, mass)
    mean = mass @ t
    best_v = -np.inf
    candidates = []
    for scale in (0.0, 0.5, 1.0):
        e = scale * eta
        u = e / (1 - e * mean)
        held = float(incremental(v, t, u, mass).sum())
        candidates.append(held)
        if held > best_v:
            best_v = held
            models["continuous_rows"] = (t.copy(), u.copy())
    c, u = models["continuous_rows"]
    assert abs(score - incremental(train, t, eta / (1 - eta * mean), mass).sum()) < 1e-7
    details["continuous_rows"] = {
        "training_gain": score,
        "bisections": 26,
        "validation_gains": candidates,
        "group_signs": c.tolist(),
        "context_tilts": u.tolist(),
        "validation_gain": best_v,
    }
    return models, details, mass


def complete_rows(data, offset, group, trigrams, q, info, models, scored):
    y = np.arange(VOCAB)
    max_error = 0.0
    for i in (0, 31, 127):
        a, b = data[offset + i - 2 : offset + i].astype(np.int64)
        base = trigrams.forecasts(np.full(VOCAB, a), np.full(VOCAB, b), y)
        assert all(abs(p.sum() - 1) < 2e-13 for p in base.values())
        h = group[data[offset + i - 3 : offset + i]]
        for key, (t, u) in models.items():
            z = int((t[h] < 0) @ np.array([4, 2, 1]))
            lexical = q * (1 + u[z] * t[group])
            full = (1 - info["weight"]) * base[info["base"]] + info[
                "weight"
            ] * lexical / lexical.sum()
            p = np.exp(-scored[key][i])
            max_error = max(
                max_error, abs(full.sum() - 1), abs(p - full[data[offset + i]])
            )
    assert max_error < 2e-13
    return max_error


def experiment(directory):
    data = tokens("train_source", FIT_END, FIT_SHA, directory)
    bg = Background(*windows(data, FIT_START, BACKGROUND))
    trigrams = Trigrams(bg)
    start = FIT_START + BACKGROUND
    group = np.minimum(bg.bins, D - 1)
    sizes = (TRAIN, VALID // 2, VALID // 2)
    starts = (start, start + TRAIN, start + TRAIN + VALID // 2)
    training, first, second = [
        Window(data, h, n, bg, group, bg.unigram) for h, n in zip(starts, sizes)
    ]
    bases = [trigrams.forecasts(*windows(data, h, n)) for h, n in zip(starts, sizes)]
    old = fit(
        None,
        POOLED,
        "pooled",
        WEIGHT,
        training.y,
        bases[0]["additive"],
        bg.bins[training.y],
        bg.unigram,
    )
    assert (
        checksum(*old, WEIGHT)
        == "58b7826c6cb9728620bc08d8bf996b1e03384a86049377570fb80935726c5f93"
    )
    with native() as lib:
        rows, rates = fit(
            lib,
            WORD,
            "blocks128",
            WEIGHT,
            training.y,
            bases[0]["additive"],
            bg.bins[training.y],
            bg.unigram,
        )
    assert (
        checksum(rows, rates, WEIGHT)
        == "7154a3bfcb1db6762ac05ce932087f069c2b3c9734fbea8fc5dbcc2a85a0a1d6"
    )
    best, positive, pure, grid = base_search(
        training, first, bg, bases[0], bases[1], rows.mean(axis=0)
    )
    info, q = best
    models, details, mass = fit_history(
        training, second, bases[0], bases[2], best, group
    )
    diagnostic = None
    if info["weight"] == 0:
        diagnostic = fit_history(training, second, bases[0], bases[2], positive, group)
    registered = json.loads(
        Path(__file__).with_name("rolling_word_rule_result.json").read_bytes()
    )
    bit = registered["fits"]["rolling_two_state"]
    models["old_transplant"] = (
        np.array(bit["group_signs"]),
        np.array(bit["context_tilts"]),
    )
    # Postregistration ablation: give every context the most common installed
    # row value, preserving the partition and its dominant lexical correction.
    static_ablations = {}
    for key in ("independent_rows", "continuous_rows"):
        t, u = models[key]
        distinct, counts = np.unique(u, return_counts=True)
        level = float(distinct[counts.argmax()])
        static_ablations[key] = (t, np.full(8, level))
    reports = []
    for role, offset, digest in REPORTS:
        data = tokens(role, offset + R, digest, directory)
        base = trigrams.forecasts(*windows(data, offset, R))
        raw = Window(data, offset, R, bg, group, old[0][0])
        w = calibrated(raw, base[info["base"]], info["weight"], q)
        pooled = -np.log(w.pool)
        scored = {
            k: pooled - incremental(w, t, u, mass) for k, (t, u) in models.items()
        }
        err = complete_rows(data, offset, group, trigrams, q, info, models, scored)
        scored.update(
            {
                "selected_static": pooled,
                "old_pooled": -np.log(raw.pool),
                "best_pure_trigram": -np.log(base[pure["base"]]),
            }
        )
        extra = {}
        if diagnostic is not None:
            pos_info, pos_q = positive
            test = calibrated(raw, base[pos_info["base"]], pos_info["weight"], pos_q)
            vals, _, pos_mass = diagnostic
            extra = {"static": summarize(-np.log(test.pool))}
            extra.update(
                {
                    k: summarize(-np.log(test.pool) - incremental(test, t, u, pos_mass))
                    for k, (t, u) in vals.items()
                }
            )
        reports.append(
            {
                "role": role,
                "start": offset,
                "prefix_sha256": digest,
                "tokens": R,
                "full_row_max_error": err,
                "losses": {k: summarize(x) for k, x in scored.items()},
                "postregistration_constant_rows": {
                    k: summarize(pooled - incremental(w, t, u, mass))
                    for k, (t, u) in static_ablations.items()
                },
                "positive_weight_diagnostic": extra,
            }
        )
    return {
        "registration": REGISTRATION,
        "static_grid_size": len(grid),
        "best_static": info,
        "best_positive_static": positive[0],
        "best_pure": pure,
        "best_per_base": {
            name: min((x for x in grid if x["base"] == name), key=lambda x: x["nll"])
            for name in bases[0]
        },
        "static_grid_sha256": hashlib.sha256(
            json.dumps(grid, sort_keys=True).encode()
        ).hexdigest(),
        "row_sha256": hashlib.sha256(q.astype("<f8").tobytes()).hexdigest(),
        "fits": details,
        "reports": reports,
        "positive_weight_fits": diagnostic[1] if diagnostic else None,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(experiment(args.directory), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
