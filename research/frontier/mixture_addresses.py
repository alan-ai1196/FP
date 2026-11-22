"""Fit and replay a stored, finite-precision mixture of two conditional forecasts."""

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from text import git_json, tape
from text_addresses import (
    ADDRESS_END,
    CAL,
    HEADER,
    READOUT_END,
    RENT,
    REPORT_END,
    REPORT_HASH,
    SELECT_END,
    TOTAL_MASS,
    fit,
    measure,
    serialize,
)

BLOCKS = 4
SUBPANEL = 4096
FRESH_END = REPORT_END + BLOCKS * CAL
FRESH_HASH = "43173bd2089d81a40bf5fb46dae4ba3347f774e9dba7883d7c92862fbb62c954"


def replication_data(directory=None):
    anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(e["result"] for e in anchor["results"] if e["case"] == "ngram")[
        "train_source"
    ]
    data = tape(
        dict(src, bytes_read=2 * FRESH_END, prefix_sha256=FRESH_HASH), directory
    )
    assert (
        hashlib.sha256(np.asarray(data[:REPORT_END], dtype="<u2").tobytes()).hexdigest()
        == REPORT_HASH
    )
    return data


def starts():
    return range(REPORT_END, FRESH_END, CAL)


def blended_row(pair, level):
    # The convex combination already gives every category at least one integer unit.
    mass, remainder = np.divmod((4 - level) * pair[0] + level * pair[1], 4)
    ordered = np.lexsort((np.arange(len(mass)), -remainder))
    mass[ordered[: TOTAL_MASS - int(mass.sum())]] += 1
    assert mass.min() >= 1 and mass.sum() == TOTAL_MASS
    return mass


@dataclass
class MixtureAddress:
    levels: np.ndarray
    payload: bytes
    row: np.ndarray | None
    default: int
    beta: int

    @property
    def bits(self):
        return 8 * (len(self.payload) + int(self.row is None))

    def losses(self, obs, forecasts):
        if self.row is not None:
            return -np.log(obs.readout(self.row))
        zero, one = forecasts
        return -np.log(zero + (self.levels[obs.history] / 4) * (one - zero))


def default_levels(common, default):
    return (
        4 * common.seed
        if default == 5
        else np.full(common.vocab, default, dtype=np.uint8)
    )


def install(common, pair, default, levels, beta):
    if np.all(levels == levels[0]):
        row = blended_row(pair, int(levels[0]))
        return MixtureAddress(
            levels, serialize(common, row[None, :]), row, default, beta
        )
    records = np.flatnonzero(levels != default_levels(common, default))
    base = serialize(common, pair, common.seed)
    header = list(HEADER.unpack_from(base))
    header[1:4] = [3, default, len(records)]
    data = bytearray(HEADER.pack(*header) + base[24 : 24 + 8 * len(common.top)])
    for i in records:
        data.extend(struct.pack("<HB", int(i), int(levels[i])))
    return MixtureAddress(levels, bytes(data), None, default, beta)


def fit_fractions(common, pair, purchase, validation, cap):
    zero, one = (purchase.readout(m) for m in pair)
    forecasts = tuple(validation.readout(m) for m in pair)
    all_log = np.stack([np.log(zero + (k / 4) * (one - zero)) for k in range(5)])
    log_ids = np.arange(len(zero))
    types = np.arange(common.vocab)
    cap_entries = (cap - (24 + 8 * len(common.top)) - 1) // 3
    table_rent = 24 * RENT * len(purchase.target) / CAL
    choices, constants = [], []

    def criterion(a):
        return float(a.losses(validation, forecasts).sum()) + RENT * a.bits

    for default in range(6):
        initial = default_levels(common, default)
        if default < 5:
            a = install(common, pair, default, initial, 0)
            constants.append((criterion(a), a))
        ref = all_log[initial[purchase.history], log_ids]
        totals, squares = [], []
        for log_p in all_log:
            gain = log_p - ref
            totals.append(
                np.bincount(purchase.history, weights=gain, minlength=common.vocab)
            )
            squares.append(
                np.bincount(purchase.history, weights=gain**2, minlength=common.vocab)
            )
        totals, roots = np.stack(totals), np.sqrt(squares)
        for beta in (0, 1, 2):
            adjusted = totals - beta * roots
            best = np.argmax(adjusted, axis=0).astype(np.uint8)
            net = adjusted[best, types] - table_rent
            ranked = np.lexsort((types, -net))
            selected = ranked[net[ranked] > 0][:cap_entries]
            levels = initial.copy()
            levels[selected] = best[selected]
            model = install(common, pair, default, levels, beta)
            assert model.bits <= 8 * cap
            choices.append((criterion(model), model))
    winner = min(choices + constants, key=lambda c: c[0])
    constant = min(constants, key=lambda c: c[0])
    return (
        winner[1],
        constant[1],
        {
            "cap_bytes": cap,
            "maximum_three_byte_entries": cap_entries,
            "validation_priced_nll": round(winner[0] / CAL, 10),
            "validation_constant_priced_nll": round(constant[0] / CAL, 10),
            "candidate_rules": len(choices),
            "single_row_constants": len(constants),
        },
    )


def describe(model, common):
    return {
        "default": "seed" if model.default == 5 else model.default,
        "beta": model.beta,
        "level_type_counts": np.bincount(model.levels, minlength=5).tolist(),
        "changed_types": int(
            np.count_nonzero(model.levels != default_levels(common, model.default))
        ),
        "payload_bytes": len(model.payload),
        "bytes_including_live": model.bits // 8,
        "sha256": hashlib.sha256(model.payload).hexdigest(),
    }


def fraction_replay(model, common, tokens, lo, hi):
    """Deliberately independent scalar decoding of packed fractions and both integer backoffs."""
    from math import log

    data = model.payload
    named, mode, fallback, n, last, cutoff, tail, t0, t1 = HEADER.unpack_from(data)
    ptr, rows, routes = HEADER.size, {}, {}
    for _ in range(named):
        y = int.from_bytes(data[ptr : ptr + 2], "little")
        left = int.from_bytes(data[ptr + 2 : ptr + 5], "little")
        right = int.from_bytes(data[ptr + 5 : ptr + 8], "little") if mode else left
        rows[y] = (left, right)
        ptr += 8 if mode else 5
    for _ in range(n):
        u, level = struct.unpack_from("<HB", data, ptr)
        routes[u] = level
        ptr += 3
    assert ptr == len(data) and mode in (0, 3)

    def state(u):
        if not mode:
            return 0
        if u in routes:
            return routes[u]
        if fallback != 5:
            return fallback
        count = common.rows.base[u]
        return 4 * int(count > cutoff or (count == cutoff and u <= last))

    out = np.empty(hi - lo)
    old = state(int(tokens[lo - 2]))
    q = int(tokens[lo - 1])
    for i in range(lo, hi):
        y = int(tokens[i])
        den = 4 * TOTAL_MASS
        if y in rows:
            left, right = rows[y]
            num = (4 - old) * left + old * right
        else:
            num = ((4 - old) * t0 + old * t1) * (common.rows.base[y] + 1)
            den *= tail
        numerator = common.rows.pairs[q, y] * den + 64 * num
        out[i - lo] = log((common.rows.outgoing[q] + 64) * den / numerator)
        old, q = state(q), y
    return out


def train(data):
    fitted = fit(data[:SELECT_END])
    tokens = np.frombuffer(data[:SELECT_END], dtype=np.uint16)
    purchase = fitted.common.observe(tokens, READOUT_END, ADDRESS_END)
    validation = fitted.common.observe(tokens, ADDRESS_END, SELECT_END)
    fraction, constant, details = fit_fractions(
        fitted.common,
        fitted.pair,
        purchase,
        validation,
        fitted.routes["conditional"].bits // 8,
    )
    return fitted, fraction, constant, details


def experiment(data):
    fitted, fraction, mix_constant, details = train(data)
    common, pair, pooled, routes = (
        fitted.common,
        fitted.pair,
        fitted.constant,
        fitted.routes,
    )
    tri, active, info, hybrid = (
        fitted.trigram,
        fitted.active,
        fitted.info,
        fitted.hybrid,
    )
    tokens = np.frombuffer(data, dtype=np.uint16)
    reports, subpanels = [], []
    visits = np.zeros(5, dtype=np.int64)
    for lo in starts():
        obs = common.observe(tokens, lo, lo + CAL)
        forecasts = tuple(obs.readout(m) for m in pair)
        log_probs = tuple(-np.log(p) for p in forecasts)
        arms = {
            k: (np.where(a.route[obs.history], log_probs[1], log_probs[0]), a.bits)
            for k, a in routes.items()
        }
        arms["bigram"] = -np.log(obs.base), 0
        arms["pooled"] = (
            -np.log(obs.readout(pooled[0])),
            8 * len(serialize(common, pooled)),
        )
        arms["calibrated_trigram"] = hybrid.losses(tri, obs), hybrid.bits
        row, found, gains = tri.combined(obs, info["raw_tau"])
        admitted = np.zeros(len(tri.pairs), dtype=bool)
        admitted[active] = True
        arms["raw_trigram"] = (
            -np.log(obs.base) - np.where(found & admitted[row], gains, 0),
            tri.bits(active),
        )
        for name, model in (
            ("fraction", fraction),
            ("constant_fraction", mix_constant),
        ):
            values = model.losses(obs, forecasts)
            assert (
                np.max(
                    np.abs(
                        values - fraction_replay(model, common, tokens, lo, lo + CAL)
                    )
                )
                < 1e-11
            )
            arms[name] = values, model.bits
        visits += np.bincount(fraction.levels[obs.history], minlength=5)
        reports.append(
            {
                name: measure(loss.sum(), bits, CAL)
                for name, (loss, bits) in arms.items()
            }
        )
        subpanels.append(
            {
                name: round(float(loss[:SUBPANEL].mean()), 9)
                for name, (loss, _) in arms.items()
            }
        )
    means = {
        k: {
            metric: round(sum(block[k][metric] for block in reports) / len(reports), 10)
            for metric in ("nll", "priced_nll")
        }
        for k in reports[0]
    }
    pairs = (
        ("conditional", "seed"),
        ("calibrated_trigram", "conditional"),
        ("marginal", "conditional"),
        ("fraction", "conditional"),
        ("fraction", "calibrated_trigram"),
        ("fraction", "constant_fraction"),
    )
    ratio = pair[1] / pair[0]
    return {
        "registration": "ed60c61",
        "prefix_sha256": FRESH_HASH,
        "first_targets": list(starts()),
        "targets_per_block": CAL,
        "training": details,
        "fraction": describe(fraction, common),
        "constant_fraction": describe(mix_constant, common),
        "full_vocabulary_ratio_bound": float(max(np.max(ratio), np.max(1 / ratio))),
        "reporting_level_occurrences": visits.tolist(),
        "block_results": reports,
        "mean": means,
        "priced_block_wins": {
            a + "_over_" + b: sum(
                r[a]["priced_nll"] < r[b]["priced_nll"] for r in reports
            )
            for a, b in pairs
        },
        "subpanel_positions_per_block": SUBPANEL,
        "subpanel_nll": subpanels,
        "mean_subpanel_nll": {
            k: round(sum(r[k] for r in subpanels) / len(subpanels), 9)
            for k in subpanels[0]
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment(replication_data(args.data_dir))
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    elif not args.check:
        print(output, end="")
