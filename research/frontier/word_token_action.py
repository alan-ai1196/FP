"""Fit finite token updates on chronological text, freeze them, and score new blocks."""

import argparse
import json
from itertools import product
from math import log
from pathlib import Path

import numpy as np
from categorical_assignment import quantize
from text_aggregate import (
    FIT_END,
    FIT_SHA,
    FIT_START,
    HISTORY,
    TAU,
    K,
    tokens,
    vocabulary,
)
from token_action import laws, transition_tables

NTRAIN = 65536
NVAL = 16384
SCORED = 65536
Q16 = 65536
HERE = Path(__file__).resolve().parent
FROZEN = HERE / "word_token_action_fits.json"
RANGES = (
    (
        "train_source",
        11196608,
        "e98695002e61f5057b10ad84199a21b117bd0a3033d13e556f850c24591c88b2",
    ),
    (
        "reporting_source",
        458752,
        "bccf652efb1b1432a911ae5f057c44cb89ff973db8a0bcadb30de6b662c11543",
    ),
)


def transition_header(table):
    q = len(table)
    width = (q - 1).bit_length()
    value, bit = q - 1, 2
    for pair in table:
        for s in pair:
            value |= s << bit
            bit += width
    return value.to_bytes((bit + 7) // 8, "little").hex()


def from_header(encoded):
    value = int.from_bytes(bytes.fromhex(encoded), "little")
    q = 1 + (value & 3)
    width = (q - 1).bit_length()
    value >>= 2
    mask = (1 << width) - 1
    rows = []
    for _ in range(q):
        rows.append((value & mask, (value >> width) & mask))
        value >>= 2 * width
    return tuple(rows)


def counts_all(catalog, letters, y, split):
    # Each machine occupies four private addresses. Different machines never
    # update the same histogram entry during a vectorized chronological step.
    n = len(catalog)
    initial = 4 * np.arange(n, dtype=np.int32)
    pos = initial.copy()
    destinations = np.zeros((2, n * 4), dtype=np.int32)
    for i, t in enumerate(catalog):
        destinations[:, 4 * i : 4 * i + len(t)] = np.array(t).T + 4 * i
    train = np.zeros((K, n * 4), dtype=np.int32)
    validation = np.zeros_like(train)
    for j, (symbol, target) in enumerate(zip(letters, y, strict=True)):
        pos = destinations[symbol, pos]
        hist = train if j < split else validation
        hist[target, pos] += 1
    return tuple(z.T.reshape(n, 4, K) for z in (train, validation))


def context_sequence(coded, mode, order, table=()):
    state = 16 if mode == "word" and order == 2 else 0
    limit = (2 if mode == "binary" else K) ** order
    out = np.empty(len(coded), dtype=np.int32)
    for i, word in enumerate(coded):
        bit = int(word < 8)
        if mode == "learned":
            state = table[state][bit]
        elif mode == "binary":
            state = (2 * state + bit) % limit
        elif mode == "word":
            state = (K * state + int(word)) % limit
        else:
            raise ValueError(mode)
        out[i] = state
    return out


def fixed_counts(address, y, nrows):
    return np.bincount(address * K + y, minlength=nrows * K).reshape(nrows, K)


def units(counts, prior):
    rows = counts.reshape(-1, K) + TAU * prior
    return np.array([quantize(row) for row in rows], dtype=np.int32).reshape(
        counts.shape
    )


def pack(rows):
    return rows[:, :-1].astype("<u2").tobytes().hex()


def read_head(head):
    prefix = (
        np.frombuffer(bytes.fromhex(head), dtype="<u2")
        .astype(np.int32)
        .reshape(-1, K - 1)
    )
    rows = np.column_stack((prefix, Q16 - prefix.sum(axis=1)))
    assert np.all(rows > 0) and np.all(rows.sum(axis=1) == Q16)
    return rows


def base_words(directory):
    data = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, lexical = vocabulary(data[:HISTORY])
    totals = np.bincount(classes, weights=lexical, minlength=K)
    within = lexical / totals[classes]
    return data, names, classes, within


def fit(directory):
    data, names, classes, within = base_words(directory)
    clip = data[FIT_START - 1 : FIT_START + NTRAIN + NVAL]
    d, y = classes[clip[:-1]], classes[clip[1:]]
    global_prior = (np.bincount(y[:NTRAIN], minlength=K) + 0.5) / (NTRAIN + K / 2)
    lexical_loss = -float(np.log(within[clip[1 + NTRAIN :]]).mean())
    catalog = [t for q in range(1, 5) for t in transition_tables(q)]
    train, val = counts_all(catalog, (d < 8).astype(int), y, NTRAIN)
    forecasts = units(train, global_prior)
    nll = (-np.log(forecasts / Q16) * val).sum(axis=(1, 2)) / NVAL + lexical_loss
    encoded = [transition_header(t) for t in catalog]
    sizes = np.array(
        [
            len(h) // 2 + 2 * (K - 1) * len(t)
            for h, t in zip(encoded, catalog, strict=True)
        ]
    )
    allowed = [all(laws(t)) for t in catalog]
    models = {}
    for name, priced in product(("unrestricted", "toggles"), (False, True)):
        eligible = (
            range(len(catalog))
            if name == "unrestricted"
            else [j for j, v in enumerate(allowed) if v]
        )
        criterion = nll + sizes * (8 * log(2) / SCORED if priced else 0)
        chosen = min(eligible, key=lambda j: (criterion[j], sizes[j], j))
        table = catalog[chosen]
        header = encoded[chosen]
        assert from_header(header) == table
        model = {
            "mode": "learned",
            "header": header,
            "rows": pack(forecasts[chosen, : len(table)]),
            "bytes": int(sizes[chosen]),
            "states": len(table),
            "transitions": table,
            "laws": laws(table),
            "validation_word_nll": float(nll[chosen]),
            "validation_criterion": float(criterion[chosen]),
        }
        models[name + ("_priced" if priced else "")] = model
    for mode, order in (
        ("binary", 0),
        ("binary", 1),
        ("binary", 2),
        ("binary", 3),
        ("word", 1),
        ("word", 2),
    ):
        key = "constant" if order == 0 else f"{mode}_{order}"
        a = context_sequence(d, mode, order)
        nstates = (2 if mode == "binary" else K) ** order
        ct = fixed_counts(a[:NTRAIN], y[:NTRAIN], nstates)
        rows = units(ct, global_prior)
        vloss = lexical_loss - float(np.log(rows[a[NTRAIN:], y[NTRAIN:]] / Q16).mean())
        models[key] = {
            "mode": mode,
            "order": order,
            "rows": pack(rows),
            "states": nstates,
            "bytes": 2 * (K - 1) * nstates,
            "validation_word_nll": vloss,
        }
    return {
        "registration": "27b9ef9",
        "fit_prefix": FIT_SHA,
        "class_names": names.tolist(),
        "catalog_size": len(catalog),
        "eligible_toggle_tables": sum(allowed),
        "machine_transitions_at_fit_and_validation": len(catalog) * (NTRAIN + NVAL),
        "models": models,
    }


def score(directory):
    receipt = json.loads(FROZEN.read_text())
    _, names, classes, within = base_words(directory)
    assert names.tolist() == receipt["class_names"]
    out = []
    class_total = np.bincount(classes, weights=within, minlength=K)
    for role, start, digest in RANGES:
        data = tokens(role, start + SCORED, digest, directory)
        words = data[start - 1 :]
        d, y = classes[words[:-1]], classes[words[1:]]
        lexical = -np.log(within[words[1:]])
        losses = {}
        for name, model in receipt["models"].items():
            rows = read_head(model["rows"])
            norm = np.abs((rows / Q16) @ class_total - 1).max()
            assert norm < 1e-12
            t = from_header(model["header"]) if model["mode"] == "learned" else ()
            a = context_sequence(d, model["mode"], model.get("order", 0), t)
            loss = -np.log(rows[a, y] / Q16) + lexical
            losses[name] = {
                "word_nll": float(loss.mean()),
                "blocks": loss.reshape(8, -1).mean(axis=1).tolist(),
                "max_normalization_error": float(norm),
            }
        base = losses["constant"]["word_nll"]
        for v in losses.values():
            v["gain"] = base - v["word_nll"]
        out.append(
            {
                "role": role,
                "start": start,
                "words": SCORED,
                "prefix_sha256": digest,
                "losses": losses,
            }
        )
    return {"registration": receipt["registration"], "reports": out}


def audit():
    catalog = [t for q in range(1, 4) for t in transition_tables(q)]
    rng = np.random.default_rng(9617)
    d = rng.integers(K, size=100)
    y = rng.integers(K, size=100)
    first, last = counts_all(catalog, (d < 8).astype(int), y, 61)
    for i, t in enumerate(catalog):
        a = context_sequence(d, "learned", 0, t)
        for z, sl in ((first, slice(0, 61)), (last, slice(61, None))):
            ref = fixed_counts(a[sl], y[sl], len(t))
            assert np.array_equal(z[i, : len(t)], ref)
        assert from_header(transition_header(t)) == t
    return {
        "directly_recomputed_tapes": len(catalog),
        "chronological_partition_counts": 2 * len(catalog),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("fit", "score", "check"))
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = (
        fit(args.data_dir)
        if args.operation == "fit"
        else score(args.data_dir)
        if args.operation == "score"
        else audit()
    )
    data = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
