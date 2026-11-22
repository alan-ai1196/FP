"""Learn which raw output to correct and which earlier histories should adjust its odds."""

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass, replace
from math import log
from pathlib import Path

import numpy as np
from mixture_addresses import FRESH_END, FRESH_HASH, train
from packed_trigram import lookup, pair_ids
from scipy.sparse import coo_matrix
from text import git_json, tape
from text_addresses import (
    ADDRESS_END,
    CAL,
    READOUT_END,
    RENT,
    SELECT_END,
    TOTAL_MASS,
    CalibratedTrigram,
    fit_calibrated_trigram,
    measure,
    serialize,
)

END = FRESH_END + 2 * CAL
END_HASH = "7d33b1c095c6bb94dfb9cc3bfae24abfb08b2b2fdce5b4532bc625cd0e9f5983"
CODES = np.array([1, 2, 3, 4, 5, 6, 8, 12, 16], dtype=np.uint8)
HEADER = struct.Struct("<HBBHH")


def load_data(directory):
    anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in anchor["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=END_HASH), directory)
    assert (
        hashlib.sha256(np.asarray(data[:FRESH_END], dtype="<u2").tobytes()).hexdigest()
        == FRESH_HASH
    )
    return data


def base_backoff(common, mass):
    tail = common.category == len(common.top)
    return (
        mass[common.category]
        / TOTAL_MASS
        * np.where(tail, common.unigram / common.tail, 1.0)
    )


def fixed_output_probability(common, backoff, obs, token):
    targets = np.full(len(obs.target), token, dtype=np.uint16)
    seen = lookup(common.keys, common.values, pair_ids(obs.query, targets))
    return (seen + 64 * backoff[token]) / (obs.outgoing + 64)


def acquire_output(common, mass, purchase):
    """Sum the normalized forecast over sparse query rows in blocks of output IDs."""
    u = common.category[purchase.history]
    rows = len(common.top) + 1
    vocab = common.vocab
    counts = np.bincount(u, minlength=rows)
    n = len(u)
    inv = np.divide(1.0, counts, out=np.zeros(rows), where=counts != 0)
    counts_uq = coo_matrix(
        (np.ones(n), (u, purchase.query)), shape=(rows, vocab)
    ).tocsr()
    weighted = counts_uq.multiply(1 / (common.outgoing + 64)).tocsr()
    q_counts = coo_matrix(
        (common.values.astype(np.float64), (common.keys >> 16, common.keys & 65535)),
        shape=(vocab, vocab),
    ).tocsc()
    actual = coo_matrix((np.ones(n), (u, purchase.target)), shape=(rows, vocab)).tocsc()
    remaining = 64 * np.asarray(weighted.sum(axis=1)).ravel()
    backoff = base_backoff(common, mass)
    scores = np.zeros(vocab)
    for j in range(0, vocab, 512):
        part = slice(j, min(j + 512, vocab))
        residual = (actual[:, part] - weighted @ q_counts[:, part]).toarray()
        residual -= remaining[:, None] * backoff[part]
        centered = residual * inv[:, None] - residual.sum(axis=0) / n
        scores[part] = np.sum(counts[:, None] * centered**2, axis=0) / n
    ranked = np.lexsort((np.arange(vocab), -scores))[:2]
    assert scores[ranked[0]] > scores[ranked[1]] > 0
    for j in ranked:
        prob = fixed_output_probability(common, backoff, purchase, j)
        means = (
            np.bincount(u, weights=(purchase.target == j) - prob, minlength=rows) * inv
        )
        expected = float(
            np.average((means - np.average(means, weights=counts)) ** 2, weights=counts)
        )
        assert abs(expected - scores[j]) < 1e-13
    return int(ranked[0]), {
        "total_raw_output_candidates": vocab,
        "occupied_history_types": int((counts > 0).sum()),
        "top_two_ids": ranked.tolist(),
        "top_two_centered_squared_residuals": [
            round(float(scores[j]), 14) for j in ranked
        ],
        "occupied_history_query_pairs": int(counts_uq.nnz),
        "occupied_history_target_pairs": int(actual.nnz),
    }


@dataclass
class Correction:
    token: int
    default: int
    codes: np.ndarray
    payload: bytes
    mode: str
    beta: int
    rule: str
    carry: bool = True

    @property
    def bits(self):
        return 8 * (
            len(self.payload) + int(self.carry and self.mode in ("sparse", "dense"))
        )

    def adjustment(self, common, obs, prob):
        if self.mode == "pooled":
            return np.zeros(len(obs.target))
        mult = self.codes[common.category[obs.history]] / 4
        return (obs.target == self.token) * np.log(mult) - np.log1p((mult - 1) * prob)


def install(base, token, default, codes, beta, rule, carry):
    ids = np.flatnonzero(codes != default)
    mode = "constant"
    extra = b""
    if len(ids):
        sparse = b"".join(struct.pack("<HB", int(u), int(codes[u])) for u in ids)
        mode, extra = (
            ("sparse", sparse)
            if len(sparse) <= len(codes)
            else ("dense", codes.tobytes())
        )
    number = {"constant": 0, "sparse": 1, "dense": 2}[mode]
    head = HEADER.pack(
        token, default, number | (0 if carry else 128), len(ids), len(codes)
    )
    return Correction(
        token, default, codes, base + head + extra, mode, beta, rule, carry
    )


def fit_response(fitted, purchase, validation, token, carry=True):
    c = fitted.common
    mass = fitted.constant[0]
    backoff = base_backoff(c, mass)
    prob = fixed_output_probability(c, backoff, purchase, token)
    u = c.category[purchase.history]
    ntypes = len(c.top) + 1
    all_gain = np.stack(
        [
            (purchase.target == token) * log(int(k) / 4)
            - np.log1p((int(k) / 4 - 1) * prob)
            for k in CODES
        ]
    )
    global_index = int(np.argmax(all_gain.sum(axis=1)))
    default = int(CODES[global_index])
    totals, squares = [], []
    for row in all_gain - all_gain[global_index]:
        totals.append(np.bincount(u, weights=row, minlength=ntypes))
        squares.append(np.bincount(u, weights=row**2, minlength=ntypes))
    totals, roots = np.stack(totals), np.sqrt(squares)
    base = serialize(c, fitted.constant)
    initial = np.full(ntypes, default, dtype=np.uint8)
    constant = install(base, token, default, initial, 0, "constant", carry)
    pooled = Correction(
        token, 4, np.full(ntypes, 4, dtype=np.uint8), base, "pooled", 0, "pooled"
    )
    proposed = []
    for beta in (0, 1, 2):
        adjusted = totals - beta * roots
        ix = np.argmax(adjusted, axis=0)
        net = adjusted[ix, np.arange(ntypes)]
        for rule, rent in (("sparse", 24 * RENT * len(u) / CAL), ("dense", 0)):
            codes = np.where(net > rent, CODES[ix], default).astype(np.uint8)
            proposed.append(install(base, token, default, codes, beta, rule, carry))
    val_prob = fixed_output_probability(c, backoff, validation, token)
    val_loss = -np.log(validation.readout(mass)).sum()

    def ordering(a):
        return (
            val_loss - a.adjustment(c, validation, val_prob).sum() + RENT * a.bits,
            a.bits,
            a.beta,
            a.rule != "sparse",
        )

    conditional = min(
        (a for a in proposed if a.mode in ("sparse", "dense")),
        key=ordering,
        default=constant,
    )
    winner = min([pooled, constant, *proposed], key=ordering)
    models = {
        "pooled": pooled,
        "constant": constant,
        "conditional": conditional,
        "selected": winner,
    }
    details = {
        "selection": {
            k: round(float(ordering(a)[0]) / CAL, 10) for k, a in models.items()
        },
        "global_purchase_multiplier": default / 4,
    }
    return models, details


def match_rows(fitted, purchase, validation, models):
    c, pooled, winner = fitted.common, models["pooled"], models["selected"]
    base = pooled.payload
    val_loss = -np.log(validation.readout(fitted.constant[0])).sum()
    groups, _ = fit_calibrated_trigram(
        c,
        [("pooled", fitted.constant)],
        fitted.trigram,
        purchase,
        validation,
        winner.bits // 8,
    )
    if (
        val_loss + RENT * pooled.bits
        <= fitted.trigram.score(
            groups.observations(validation), groups.tau, groups.active
        )
        + RENT * groups.bits
    ):
        groups = CalibratedTrigram(
            fitted.constant, 4, np.empty(0, dtype=np.int64), base, pooled.bits
        )
    raw_info = {
        "tau": groups.tau,
        "rows": len(groups.active),
        "entries": int(fitted.trigram.degree[groups.active].sum()),
        "bytes": groups.bits // 8,
    }
    return groups, raw_info


def train_study(prefix):
    assert len(prefix) == SELECT_END
    fitted, fraction, _, _ = train(prefix)
    tokens = np.frombuffer(prefix, dtype=np.uint16)
    purchase = fitted.common.observe(tokens, READOUT_END, ADDRESS_END)
    val = fitted.common.observe(tokens, ADDRESS_END, SELECT_END)
    token, details = acquire_output(fitted.common, fitted.constant[0], purchase)
    models, selection = fit_response(fitted, purchase, val, token)
    details.update(selection)
    matched, raw_info = match_rows(fitted, purchase, val, models)
    return fitted, fraction, models, matched, details, raw_info


def scalar_check(model, fitted, tokens, lo, hi, expected):
    c = fitted.common
    base = serialize(c, fitted.constant)
    assert model.payload[: len(base)] == base
    current = False
    if model.mode == "pooled":
        token, default, mode, extra, n = 0, 4, 0, b"", len(c.top) + 1
    else:
        token, default, mode, nstored, n = HEADER.unpack_from(model.payload, len(base))
        current, mode = bool(mode & 128), mode & 127
        extra = model.payload[len(base) + HEADER.size :]
        assert n == len(c.top) + 1
        if mode == 1:
            assert len(extra) == 3 * nstored
        elif mode == 2:
            assert len(extra) == n
        else:
            assert not extra
    remap = np.full(n, default, dtype=np.uint8)
    if mode == 1:
        for group, k in struct.iter_unpack("<HB", extra):
            remap[group] = k
    if mode == 2:
        remap = np.frombuffer(extra, dtype=np.uint8)
    cover = {int(tok): i for i, tok in enumerate(c.top)}
    mass = fitted.constant[0]

    def numerator(q, y):
        j = cover.get(y, len(cover))
        refine = c.rows.base[y] + 1 if j == len(cover) else c.tail
        return c.rows.pairs[q, y] * (TOTAL_MASS * c.tail) + 64 * int(mass[j]) * refine

    for q in np.argsort(c.outgoing)[[0, len(c.outgoing) // 2, -1]].tolist():
        full = (c.rows.outgoing[q] + 64) * TOTAL_MASS * c.tail
        other = sum(numerator(q, y) for y in range(c.vocab) if y != token)
        nj = numerator(q, token)
        for k in CODES.tolist():
            assert 4 * other + k * nj == 4 * full + (k - 4) * nj
    old = int(remap[cover.get(int(tokens[lo - 2]), n - 1)])
    q = int(tokens[lo - 1])
    error = 0.0
    for i in range(lo, hi):
        y = int(tokens[i])
        if current:
            old = int(remap[cover.get(q, n - 1)])
        den = (c.rows.outgoing[q] + 64) * TOTAL_MASS * c.tail
        nj = numerator(q, token)
        actual = log(
            (4 * den + (old - 4) * nj) / ((old if y == token else 4) * numerator(q, y))
        )
        error = max(error, abs(actual - expected[i - lo]))
        old, q = int(remap[cover.get(q, n - 1)]), y
    assert error < 1e-11


def describe(a):
    return {
        "token": a.token,
        "mode": a.mode,
        "default_numerator": a.default,
        "training_rule": a.rule,
        "beta": a.beta,
        "changed_types": int(np.count_nonzero(a.codes != a.default)),
        "bytes_with_live": a.bits // 8,
        "code_counts": {
            str(int(k)): int(np.count_nonzero(a.codes == k))
            for k in CODES
            if np.any(a.codes == k)
        },
        "sha256": hashlib.sha256(a.payload).hexdigest(),
    }


def current_only_control(fitted, prefix, previous_target):
    c = fitted.common
    observations = []
    for start, end in ((READOUT_END, ADDRESS_END), (ADDRESS_END, SELECT_END)):
        obs = c.observe(prefix, start, end)
        observations.append(replace(obs, history=obs.query))
    purchase, validation = observations
    own, details = acquire_output(c, fitted.constant[0], purchase)
    candidates = []
    for token in dict.fromkeys((own, previous_target)):
        models, info = fit_response(fitted, purchase, validation, token, carry=False)
        model = models["selected"]
        backoff = base_backoff(c, fitted.constant[0])
        prob = fixed_output_probability(c, backoff, validation, token)
        val_gain = (
            float(model.adjustment(c, validation, prob).sum()) - RENT * model.bits
        )
        candidates.append((val_gain, model, info["selection"]["selected"]))
    _, chosen, _ = max(candidates, key=lambda x: x[0])
    return chosen, {
        "acquired_output": own,
        "top_two_scores": details["top_two_centered_squared_residuals"],
        "candidate_validation": {str(a.token): score for _, a, score in candidates},
    }


def experiment(data):
    fitted, fraction, models, raw, details, raw_info = train_study(data[:SELECT_END])
    c = fitted.common
    mass = fitted.constant[0]
    tokens = np.frombuffer(data, dtype=np.uint16)
    backoff = base_backoff(c, mass)
    current, current_info = current_only_control(
        fitted, tokens[:SELECT_END], models["selected"].token
    )
    current_blocks = []
    blocks = []
    outside = []
    responses = []
    for lo in range(FRESH_END, END, CAL):
        obs = c.observe(tokens, lo, lo + CAL)
        p = obs.readout(mass)
        prob = fixed_output_probability(c, backoff, obs, models["selected"].token)
        ends = tuple(obs.readout(m) for m in fitted.pair)
        arms = {}
        for name, a in models.items():
            loss = -np.log(p) - a.adjustment(c, obs, prob)
            arms[name] = measure(loss.sum(), a.bits, CAL)
            if name == "selected":
                scalar_check(a, fitted, tokens, lo, lo + CAL, loss)
                predicted = p * np.exp(a.adjustment(c, obs, prob))
                high = np.maximum.reduce((p, *ends))
                low = np.minimum.reduce((p, *ends))
                outside.append(
                    int(((predicted > high + 1e-12) | (predicted < low - 1e-12)).sum())
                )
                responses.append(
                    int(np.count_nonzero(a.codes[c.category[obs.history]] != a.default))
                )
        for name, model in (("matched_raw", raw), ("earlier_raw", fitted.hybrid)):
            arms[name] = measure(
                model.losses(fitted.trigram, obs).sum(), model.bits, CAL
            )
        arms["earlier_fraction"] = measure(
            fraction.losses(obs, ends).sum(), fraction.bits, CAL
        )
        blocks.append(arms)
        q_only = replace(obs, history=obs.query)
        pj = fixed_output_probability(c, backoff, q_only, current.token)
        current_loss = -np.log(p) - current.adjustment(c, q_only, pj)
        scalar_check(current, fitted, tokens, lo, lo + CAL, current_loss)
        current_blocks.append(measure(current_loss.sum(), current.bits, CAL))
    return {
        "registration": "218c31e",
        "reporting_prefix_sha256": END_HASH,
        "first_targets": [FRESH_END, FRESH_END + CAL],
        "acquisition": details,
        "models": {k: describe(v) for k, v in models.items()},
        "matched_raw": raw_info,
        "changed_from_fitted_default_occurrences": responses,
        "outside_old_pair_and_pooled_by_more_than_1e-12": outside,
        "blocks": blocks,
        "posthoc_current_only": {
            "fit": current_info,
            "model": describe(current),
            "blocks": current_blocks,
            "mean_priced_nll": round(
                sum(b["priced_nll"] for b in current_blocks) / len(current_blocks), 10
            ),
        },
        "mean": {
            name: {
                key: round(sum(b[name][key] for b in blocks) / 2, 10)
                for key in ("nll", "priced_nll")
            }
            for name in blocks[0]
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment(load_data(args.data_dir))
    if args.check:
        assert json.loads(args.check.read_text(encoding="utf8")) == result
    value = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(value, encoding="utf8")
    elif not args.check:
        print(value, end="")
