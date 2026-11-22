"""Learn a shared Boolean statistic of three observable history bits on ordinary text."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from math import fsum, log
from pathlib import Path

import numpy as np
from partitions import fit_sparse_cells, fit_sparse_trigram
from text import FIT, TAU, VOCAB, Rows, git_json, log_bounds, outward, tape
from text_memory import CAL, GRID, fitted_masses
from text_operation import (
    BUY_END,
    CAL_END,
    PREFIX_HASH,
    Score,
    apply_gate,
    fit_gate,
    histogram,
    shared_loss,
    unpack,
    vectors,
    winner,
)
from text_operation import (
    REPORT_END as PREVIOUS_END,
)

CHOOSE_END = PREVIOUS_END + CAL
REPORT_END = CHOOSE_END + CAL
SELECT_HASH = "319adf9f6910bf06e4e7c1f5f49852334b5897e940ef95e3100bb17b7819b146"
REPORT_HASH = "f450babb24e2576c647833d1819073dfd3d7461d1ceb605136d4a13acea8730a"
COPIES = (170, 204, 240)


def truth(table):
    return (table >> np.arange(8, dtype=np.uint8)) & 1


def automaton(table):
    outputs = truth(table).tolist()
    cells = outputs.copy()
    while True:
        names = {}
        refined = []
        for h in range(8):
            key = (cells[h], cells[(2 * h) & 7], cells[(2 * h + 1) & 7])
            refined.append(names.setdefault(key, len(names)))
        if refined == cells:
            break
        cells = refined
    representatives = [cells.index(i) for i in range(len(set(cells)))]
    return {
        "history_to_state": cells,
        "outputs": [outputs[h] for h in representatives],
        "transitions": [
            [cells[(2 * h + b) & 7] for b in (0, 1)] for h in representatives
        ],
    }


def dependencies(table):
    values = truth(table)
    return [
        bit for bit in range(3) if np.any(values != values[np.arange(8) ^ (1 << bit)])
    ]


def block(tokens, bits, lo, hi):
    history = (
        (bits[lo - 4 : hi - 4] << 2)
        | (bits[lo - 3 : hi - 3] << 1)
        | bits[lo - 2 : hi - 2]
    )
    return tokens[lo - 1 : hi - 1], history, bits[lo:hi]


def counts(obs):
    current, history, target = obs
    indices = 16 * current.astype(np.int32) + 2 * history + target
    return np.bincount(indices, minlength=16 * VOCAB).reshape(VOCAB, 8, 2)


def pooled(count, table):
    ones = count[:, truth(table).astype(bool), :].sum(axis=1)
    return np.stack((count.sum(axis=1) - ones, ones), axis=1)


def occupied(count):
    return {
        (int(x), int(h)): tuple(map(int, count[x, h]))
        for x, h in zip(*np.nonzero(count.sum(axis=2)), strict=True)
    }


def table_score(payload, base, obs, shared_bits):
    current, history, target = obs
    if not payload:
        return Score(histogram(base[current], target), 0)
    values = truth(payload[0])[history]
    return Score(
        apply_gate(payload, base, current, values, target),
        40 * len(unpack(payload)) + shared_bits,
    )


def sparse_score(rates, bits, base, current, context, target):
    p = np.fromiter(
        (
            rates.get((int(x), int(h)), base[x])
            for x, h in zip(current, context, strict=True)
        ),
        dtype=np.int32,
        count=len(current),
    )
    return Score(histogram(p, target), bits)


def calibration_geometry(count):
    """Post-hoc geometry of the calibration contingency table, with unpriced Bayes readouts."""
    raw = count.transpose(1, 0, 2).reshape(8, -1)
    raw = raw[:, raw.any(axis=0)]
    totals = raw.sum(axis=1)
    rows = raw / totals[:, None]
    best = None
    for a, b in combinations(range(8), 2):
        direction = rows[b] - rows[a]
        varying = np.flatnonzero(direction)
        if not len(varying):
            continue
        weights = np.abs(direction[varying])
        fitted, medians = [], []
        for row in rows:
            ratios = (row[varying] - rows[a, varying]) / direction[varying]
            ordered = np.argsort(ratios, kind="stable")
            split = np.searchsorted(np.cumsum(weights[ordered]), weights.sum() / 2)
            j = ordered[split]
            medians.append(int(varying[j]))
            fitted.append(np.clip(ratios[j], 0, 1))
        residual = (
            np.abs(rows - rows[a] - np.outer(fitted, direction)).sum(axis=1).max() / 2
        )
        if best is None or residual < best[0]:
            best = (residual, a, b, medians)
    if best is None:
        a = b = 0
        medians = [0] * 8
    else:
        _, a, b, medians = best
    exact_rows = raw.tolist()
    na, nb = int(totals[a]), int(totals[b])
    positions, errors = [], []
    for u, j in enumerate(medians):
        nu = int(totals[u])
        d = exact_rows[b][j] * na - exact_rows[a][j] * nb
        t = (
            F((exact_rows[u][j] * na - exact_rows[a][j] * nu) * nb, nu * d)
            if d
            else F(0)
        )
        t = min(F(1), max(F(0), t))
        v, w = t.numerator, t.denominator
        numerator = sum(
            abs(x * na * nb * w - nu * ((w - v) * y * nb + v * z * na))
            for x, y, z in zip(exact_rows[u], exact_rows[a], exact_rows[b], strict=True)
        )
        positions.append(t)
        errors.append(F(numerator, 2 * nu * na * nb * w))
    thresholds = {0}
    for pos in positions:
        mask = sum(1 << i for i, t in enumerate(positions) if t < pos)
        thresholds.add(mask ^ (255 if mask & 1 else 0))

    def conditional_entropy(mask):
        grouped = pooled(count, mask)
        positive = np.bincount(grouped.sum(axis=2).ravel())
        negative = np.bincount(grouped.ravel(), minlength=len(positive))
        lo = hi = 0
        for k in np.flatnonzero(positive[1:] != negative[1:]) + 1:
            factor = int(k) * int(positive[k] - negative[k])
            x, y = log_bounds(int(k))
            lo += min(factor * x, factor * y)
            hi += max(factor * x, factor * y)
        return lo, hi

    scores = {m: conditional_entropy(m) for m in range(0, 256, 2)}

    def minimum(masks):
        mask = min(masks, key=lambda k: (scores[k][1], k))
        bounds = min(scores[k][0] for k in masks), scores[mask][1]
        return {
            "mask": mask,
            "empirical_conditional_nll": outward(bounds, int(totals.sum())),
        }

    return {
        "sample": [FIT, CAL_END],
        "occupied_joint_coordinates": raw.shape[1],
        "endpoint_history_indices": [a, b],
        "positions": [str(t) for t in positions],
        "max_total_variation": str(max(errors)),
        "distinct_threshold_tables": len(thresholds),
        "threshold_optimum": minimum(thresholds),
        "unrestricted_optimum": minimum(scores),
    }


def fit(data):
    assert len(data) == CHOOSE_END
    rows = Rows(data[:FIT], VOCAB, TAU)
    membership, numerator, fitted, _ = fitted_masses(
        rows, data[FIT:CAL_END], data[FIT - 1]
    )
    base = np.asarray(fitted, dtype=np.int32)
    tokens, bits = vectors(data, membership)
    cal = counts(block(tokens, bits, FIT, CAL_END))
    buy = counts(block(tokens, bits, CAL_END, BUY_END))
    select = block(tokens, bits, PREVIOUS_END, CHOOSE_END)
    within, _ = shared_loss(rows, numerator, membership, data, PREVIOUS_END, CHOOSE_END)
    scores, payloads, copies, copy_payloads = {}, {}, {}, {}
    for table in range(0, 256, 2):
        a, b = pooled(cal, table), pooled(buy, table)
        payloads[table], _ = fit_gate(table, a, b, base, shared_bits=16)
        scores[table] = table_score(payloads[table], base, select, 16)
        if table in COPIES:
            copy_payloads[table], _ = fit_gate(table, a, b, base, shared_bits=8)
            copies[table] = table_score(copy_payloads[table], base, select, 8)
    selected = winner(scores)
    copy = winner(copies)
    budget = scores[selected].bits
    full, full_cost = fit_sparse_cells(
        occupied(cal), occupied(buy), fitted, budget, record_bits=32, live_bits=8
    )
    raw, raw_cost = fit_sparse_trigram(data[:BUY_END], membership, fitted, budget)
    full_score = sparse_score(full, full_cost["installed_bits"], base, *select)
    raw_score = sparse_score(
        raw,
        raw_cost["installed_bits"],
        base,
        select[0],
        tokens[PREVIOUS_END - 2 : CHOOSE_END - 2],
        select[2],
    )
    work = {
        "candidate_tables": len(scores),
        "fit_block_target_count": CAL,
        "row_purchase_target_count": CAL,
        "selection_target_count_per_table": CAL,
        "smoothed_pairs": len(rows.pairs),
        "frequency_group_types": sum(membership),
        "full_history_exceptions": full_cost,
        "raw_trigram": raw_cost,
    }
    selected_scores = {
        k: s.report(within, CAL)
        for k, s in (
            ("table", scores[selected]),
            ("copy", copies[copy]),
            ("full_history", full_score),
            ("raw_trigram", raw_score),
        )
    }
    return (
        rows,
        membership,
        numerator,
        base,
        selected,
        payloads,
        copy,
        copy_payloads[copy],
        full,
        raw,
        work,
        selected_scores,
        calibration_geometry(cal),
    )


def scalar_replay(data, rows, membership, numerator, base, payload, autom):
    rates = unpack(payload)
    state = autom["history_to_state"][
        sum(membership[data[CHOOSE_END - 2 - j]] << j for j in range(3))
    ]
    masses = Counter()
    losses = []
    for i in range(CHOOSE_END, REPORT_END):
        x, y = data[i - 1], data[i]
        bit = autom["outputs"][state]
        p = rates[x][bit] if x in rates else int(base[x])
        k = p if membership[y] else GRID - p
        masses[k] += 1
        raw_num, raw_den = rows.mass(x, y, True)
        group_mass = numerator[x] if membership[y] else raw_den - numerator[x]
        losses.append(log(group_mass / raw_num) + log(GRID / k))
        state = autom["transitions"][state][membership[x]]
    return masses, fsum(losses) / CAL


def report(data, fitted):
    (
        rows,
        membership,
        numerator,
        base,
        selected,
        payloads,
        copy,
        copy_payload,
        full,
        raw,
        work,
        selection,
        geometry,
    ) = fitted
    payload = payloads[selected]
    tokens, bits = vectors(data, membership)
    obs = block(tokens, bits, CHOOSE_END, REPORT_END)
    within, plain = shared_loss(
        rows, numerator, membership, data, CHOOSE_END, REPORT_END
    )
    scores = {
        "table": table_score(payload, base, obs, 16),
        "copy": table_score(copy_payload, base, obs, 8),
        "full_history": sparse_score(
            full, work["full_history_exceptions"]["installed_bits"], base, *obs
        ),
        "raw_trigram": sparse_score(
            raw,
            work["raw_trigram"]["installed_bits"],
            base,
            obs[0],
            tokens[CHOOSE_END - 2 : REPORT_END - 2],
            obs[2],
        ),
        "calibrated": Score(histogram(base[obs[0]], obs[2]), 0),
    }
    report_scores = {name: s.report(within, CAL) for name, s in scores.items()}
    report_scores["smoothed_successor"] = {"nll": outward(plain, CAL)}
    autom = automaton(selected)
    masses, scalar_nll = scalar_replay(
        data, rows, membership, numerator, base, payload, autom
    )
    assert masses == scores["table"].hist
    lo, hi = map(float, report_scores["table"]["nll"])
    assert lo <= scalar_nll <= hi
    depends = dependencies(selected)
    wins = {
        name: scores["table"].beats(scores[name])
        for name in ("copy", "full_history", "raw_trigram")
    }
    assert all(
        scores[n].bits <= scores["table"].bits for n in ("raw_trigram", "full_history")
    )
    alternatives = {
        key: table_score(value, base, obs, 16)
        for key, value in payloads.items()
        if len(dependencies(key)) >= 2
    }
    best_other = winner(alternatives)
    return {
        "registration": "0680d73",
        "vocabulary": VOCAB,
        "prefix_hashes": {
            str(PREVIOUS_END): PREFIX_HASH,
            str(CHOOSE_END): SELECT_HASH,
            str(REPORT_END): REPORT_HASH,
        },
        "split_points": [
            0,
            FIT,
            CAL_END,
            BUY_END,
            PREVIOUS_END,
            CHOOSE_END,
            REPORT_END,
        ],
        "selected_mask": selected,
        "selected_truth_values_in_history_order": truth(selected).tolist(),
        "selected_history_bits_from_newest": depends,
        "selected_copy_mask": copy,
        "minimal_automaton": autom,
        "active_rows": len(unpack(payload)),
        "selected_payload_bytes_including_live_byte": len(payload) + bool(payload),
        "selected_packed_rows_sha256": hashlib.sha256(payload).hexdigest(),
        "selection": selection,
        "reporting": report_scores,
        "acquisition": work,
        "posthoc_calibration_geometry": geometry,
        "priced_score_beats": wins,
        "preregistered_success": len(depends) >= 2 and all(wins.values()),
        "posthoc_frozen_multibit_tables": {
            "count": len(alternatives),
            "best_mask": best_other,
            "best_score": alternatives[best_other].report(within, CAL),
            "beat_selected_copy": sum(
                s.beats(scores["copy"]) for s in alternatives.values()
            ),
            "beat_raw_trigram": sum(
                s.beats(scores["raw_trigram"]) for s in alternatives.values()
            ),
        },
    }


def audit():
    state_counts = Counter()
    for table in range(256):
        a = automaton(table)
        cells = a["history_to_state"]
        outputs = truth(table).tolist()
        signatures = []
        for h in range(8):
            sig = []
            for k in range(3):
                for extension in product((0, 1), repeat=k):
                    raw = h
                    state = cells[h]
                    for b in extension:
                        raw = (2 * raw + b) & 7
                        state = a["transitions"][state][b]
                    assert a["outputs"][state] == outputs[raw]
                    sig.append(outputs[raw])
            signatures.append(tuple(sig))
        assert all(
            (cells[u] == cells[v]) == (signatures[u] == signatures[v])
            for u, v in product(range(8), repeat=2)
        )
        assert (len(set(cells)) == 8) == all(
            outputs[u] != outputs[u ^ 4] for u in range(4)
        )
        state_counts[len(set(cells))] += 1
    return {
        "tables": 256,
        "minimal_state_histogram": {str(k): v for k, v in sorted(state_counts.items())},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = {"controls": audit()}
    if not args.audit:
        anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
        src = next(r for r in anchor["results"] if r["case"] == "ngram")["result"][
            "train_source"
        ]
        data = tape(
            dict(src, bytes_read=2 * REPORT_END, prefix_sha256=REPORT_HASH),
            args.data_dir,
        )
        for n, digest in (
            (BUY_END, src["prefix_sha256"]),
            (PREVIOUS_END, PREFIX_HASH),
            (CHOOSE_END, SELECT_HASH),
        ):
            prefix = data[:n]
            if sys.byteorder != "little":
                prefix.byteswap()
            assert hashlib.sha256(prefix.tobytes()).hexdigest() == digest
        result["text"] = report(data, fit(data[:CHOOSE_END]))
    if args.check:
        assert json.loads(args.check.read_text(encoding="utf8")) == result
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    elif not args.check:
        print(output, end="")


if __name__ == "__main__":
    main()
