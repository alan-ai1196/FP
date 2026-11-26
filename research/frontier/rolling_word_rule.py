"""Fit grouped rolling word rules by normalized full-vocabulary lexical likelihood."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from learned_word_rule import PRODUCT, TABLES, TRIPLES, contexts, rolling_width
from lexical_curvature import WEIGHT
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
    fit,
    native,
    summarize,
    tokens,
    windows,
)
from pair_dictionary import representatives
from text import VOCAB

REGISTRATION = "52c2310"
D = 12
R = 65536
REPORTS = (
    (
        "train_source",
        17000000,
        "ee1c4fd74f5371a27fa1124786ce776fd47b4149d69047b8e4101002e9149996",
    ),
    (
        "reporting_source",
        1179648,
        "4bcc4bf13fd15b26306ed792385d1b9c8f7209c4673ffede81c70d0c8a9d45ab",
    ),
)
STRENGTHS = (0.25, 0.5, 0.75)
FAMILIES = {
    "free": TABLES,
    "last_two": TABLES[np.all(TABLES[:, :4] == TABLES[:, 4:], axis=1)],
    "rolling_two_state": np.array(
        [np.ones(8), -np.ones(8), TRIPLES[:, 2], -TRIPLES[:, 2]]
    ),
    "product": PRODUCT[None, :],
}
SHIFT = 131073


class Window:
    def __init__(self, data, start, length, bg, group, row):
        a, b, y = windows(data, start, length)
        oldest = data[start - 3 : start - 3 + length]
        self.history = (group[oldest] * D + group[a]) * D + group[b]
        self.group = group[y]
        self.y = y
        self.base = bg.forecasts(a, b, y)[2]
        part = WEIGHT * row[y]
        self.pool = (1 - WEIGHT) * self.base + part
        self.resp = part / self.pool


def history_codes(t):
    z = (t < 0).astype(np.int64)
    return (4 * z[:, None, None] + 2 * z[None, :, None] + z[None, None, :]).reshape(-1)


def incremental(w, t, u, mass, shift=False):
    z = history_codes(t)[w.history]
    if shift:
        z = np.roll(z, SHIFT)
    value = u[z]
    mean = mass @ t
    return np.log1p(w.resp * value * (t[w.group] - mean) / (1 + value * mean))


def fit_rules(w, mass):
    # For each candidate the plus and minus log gains per context suffice.
    fits = {k: {} for k in (*FAMILIES, "shifted_free", "independent_rows")}
    for t in representatives(D):
        z = history_codes(t)[w.history]
        far = np.roll(z, SHIFT)
        mean = mass @ t
        residual = w.resp * (t[w.group] - mean)
        all_gains = [np.zeros(8)]
        levels = [0.0]
        for strength in STRENGTHS:
            plus = np.log1p(residual * (strength / (1 + strength * mean)))
            minus = np.log1p(residual * (-strength / (1 - strength * mean)))
            row_plus = np.bincount(z, weights=plus, minlength=8)
            row_minus = np.bincount(z, weights=minus, minlength=8)
            all_gains.extend((row_plus, row_minus))
            levels.extend((strength, -strength))
            shift_plus = np.bincount(far, weights=plus, minlength=8)
            shift_minus = np.bincount(far, weights=minus, minlength=8)
            for name, tables in (*FAMILIES.items(), ("shifted_free", TABLES)):
                a, b = (
                    (shift_plus, shift_minus)
                    if name == "shifted_free"
                    else (row_plus, row_minus)
                )
                score = (a + b).sum() / 2 + tables @ ((a - b) / 2)
                j = int(score.argmax())
                prev = fits[name].get(strength)
                if prev is None or score[j] > prev[0]:
                    fits[name][strength] = (
                        float(score[j]),
                        t.copy(),
                        strength * tables[j],
                    )
        grid = np.array(all_gains)
        j = grid.argmax(axis=0)
        score = float(grid[j, np.arange(8)].sum())
        prev = fits["independent_rows"].get(1.0)
        if prev is None or score > prev[0]:
            fits["independent_rows"][1.0] = (score, t.copy(), np.array(levels)[j])
    return fits


def rows_fit(w, t, row, tau):
    if t is None:
        z = np.zeros_like(w.y)
        p = (np.bincount(w.y, minlength=VOCAB) + tau * row)[None, :] / (len(w.y) + tau)
    else:
        z = history_codes(t)[w.history]
        p = np.tile(row, (8, 1))
    idx = z * VOCAB + w.y
    for _ in range(12):
        part = WEIGHT * p[z, w.y]
        resp = part / ((1 - WEIGHT) * w.base + part)
        counts = np.bincount(idx, weights=resp, minlength=p.size).reshape(p.shape)
        p = counts + tau * row[None, :]
        p /= p.sum(axis=1, keepdims=True)
    assert np.max(abs(p.sum(axis=1) - 1)) < 2e-14
    return p


def static_controls(train, validation, bg, pooled):
    strengths = (64, 1024, 8192, 65536)
    smoothed = [rows_fit(train, None, bg.unigram, tau)[0] for tau in strengths]
    assert np.max(abs(smoothed[0] - pooled)) < 2e-15
    losses = [
        float(-np.log((1 - WEIGHT) * validation.base + WEIGHT * q[validation.y]).sum())
        for q in smoothed
    ]
    best = int(np.argmin(losses))
    with native() as lib:
        rows, rates = fit(
            lib,
            WORD,
            "blocks128",
            WEIGHT,
            train.y,
            train.base,
            bg.bins[train.y],
            bg.unigram,
        )
        assert (
            checksum(rows, rates, WEIGHT)
            == "7154a3bfcb1db6762ac05ce932087f069c2b3c9734fbea8fc5dbcc2a85a0a1d6"
        )
    return {
        "previous_static_average": rows.mean(axis=0),
        "smoothed_lexical": smoothed[best],
    }, {"taus": strengths, "validation_nll": losses, "selected_tau": strengths[best]}


def supplemental_scores(w, group, statics, t, u):
    z = history_codes(t)[w.history]
    value = u[z]
    result = {}
    for name, q in statics.items():
        part = WEIGHT * q[w.y]
        common = (1 - WEIGHT) * w.base
        mean = q @ t[group]
        tilt = (1 + value * t[w.group]) / (1 + value * mean)
        result[name] = summarize(-np.log(common + part))
        result[name + "_with_frozen_bit"] = summarize(-np.log(common + part * tilt))
    return result


def row_prediction(w, t, rows):
    z = history_codes(t)[w.history]
    return (1 - WEIGHT) * w.base + WEIGHT * rows[z, w.y]


def select(fits, train, validation, mass):
    models = {}
    details = {}
    default_t = representatives(D)[0]
    for name, entries in fits.items():
        chosen = (0.0, default_t, np.zeros(8))
        metrics = []
        for strength, (training, t, u) in entries.items():
            check = incremental(train, t, u, mass, name == "shifted_free").sum()
            assert abs(check - training) < 2e-8
            attenuations = (0.5, 1.0) if name == "independent_rows" else (1.0,)
            for scale in attenuations:
                values = scale * u
                v = float(incremental(validation, t, values, mass).sum())
                metrics.append(
                    {
                        "strength": strength,
                        "validation_scale": scale,
                        "training_gain_before_attenuation": training,
                        "validation_gain": v,
                    }
                )
                if v > chosen[0]:
                    chosen = (v, t.copy(), values.copy())
        val, t, u = chosen
        models[name] = (t, u)
        details[name] = {
            "group_signs": t.tolist(),
            "context_tilts": u.tolist(),
            "validation_gain": val,
            "rolling_states": rolling_width(u),
            "candidates": metrics,
        }
    return models, details


def verify_rows(data, start, bg, group, row, models, w):
    max_error = 0.0
    y = np.arange(VOCAB, dtype=np.int64)
    for i in (0, 31, 127):
        a, b = data[start + i - 2 : start + i].astype(np.int64)
        base = bg.forecasts(np.full(VOCAB, a), np.full(VOCAB, b), y)[2]
        assert abs(base.sum() - 1) < 1e-13
        for t, u in models.values():
            z = contexts(t[group[data[start + i - 3 : start + i]]])
            tilt = u[z]
            lexical = row * (1 + tilt * t[group])
            full = (1 - WEIGHT) * base + WEIGHT * lexical / lexical.sum()
            mass = np.bincount(group, weights=row, minlength=D)
            actual = w.pool[i] * np.exp(incremental(w, t, u, mass)[i])
            max_error = max(max_error, abs(full.sum() - 1), abs(full[w.y[i]] - actual))
    assert max_error < 2e-13
    return max_error


def experiment(directory):
    data = tokens("train_source", FIT_END, FIT_SHA, directory)
    bg = Background(*windows(data, FIT_START, BACKGROUND))
    start = FIT_START + BACKGROUND
    win = windows(data, start, TRAIN)
    y = win[2]
    model = fit(
        None, POOLED, "pooled", WEIGHT, y, bg.forecasts(*win)[2], bg.bins[y], bg.unigram
    )
    assert (
        checksum(*model, WEIGHT)
        == "58b7826c6cb9728620bc08d8bf996b1e03384a86049377570fb80935726c5f93"
    )
    row = model[0][0]
    group = np.minimum(bg.bins, D - 1)
    mass = np.bincount(group, weights=row, minlength=D)
    assert abs(mass.sum() - 1) < 2e-13
    train = Window(data, start, TRAIN, bg, group, row)
    validation = Window(data, start + TRAIN, VALID, bg, group, row)
    models, selection = select(fit_rules(train, mass), train, validation, mass)
    t = models["free"][0]
    best = float(np.log(validation.pool).sum())
    chosen_rows = row[None, :].repeat(8, axis=0)
    chosen_tau = None
    full_scores = {}
    for tau in (64, 1024, 8192):
        rows = rows_fit(train, t, row, tau)
        score = float(np.log(row_prediction(validation, t, rows)).sum())
        full_scores[tau] = score - float(np.log(validation.pool).sum())
        if score > best:
            best, chosen_rows, chosen_tau = score, rows, tau
    statics, shrink = static_controls(train, validation, bg, row)
    reports = []
    for role, offset, digest in REPORTS:
        data = tokens(role, offset + R, digest, directory)
        w = Window(data, offset, R, bg, group, row)
        loss = -np.log(w.pool)
        losses = {
            "pooled": loss,
            "trigram": -np.log(w.base),
            "eight_full_rows": -np.log(row_prediction(w, t, chosen_rows)),
        }
        losses.update(
            {key: loss - incremental(w, c, u, mass) for key, (c, u) in models.items()}
        )
        error = verify_rows(data, offset, bg, group, row, models, w)
        reports.append(
            {
                "role": role,
                "start": offset,
                "tokens": R,
                "prefix_sha256": digest,
                "direct_full_row_max_error": error,
                "losses": {k: summarize(v) for k, v in losses.items()},
                "postregistration_controls": supplemental_scores(
                    w, group, statics, *models["rolling_two_state"]
                ),
            }
        )
    return {
        "registration": REGISTRATION,
        "vocabulary": VOCAB,
        "eleven_word_ids": bg.names[:11].tolist(),
        "lexical_group_mass": mass.tolist(),
        "fit_tokens": TRAIN,
        "fits": selection,
        "validation_tokens": VALID,
        "full_rows_tau": chosen_tau,
        "full_rows_validation_gains": full_scores,
        "postregistration_lexical_shrinkage": shrink,
        "acquisition": {
            "partitions": len(representatives(D)),
            "strengths": STRENGTHS,
            "two_tilt_log_evaluations": 2
            * len(representatives(D))
            * len(STRENGTHS)
            * TRAIN,
            "full_row_cells": 8 * VOCAB,
            "grid_families": {k: len(v) for k, v in FAMILIES.items()},
        },
        "full_rows_sha256": hashlib.sha256(
            chosen_rows.astype("<f8").tobytes()
        ).hexdigest(),
        "reports": reports,
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
