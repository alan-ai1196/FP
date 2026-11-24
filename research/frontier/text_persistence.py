"""Fit a word-class persistence filter on one chronological block and score two new ones."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from nested_class import event_prob
from scipy.special import expit, logit
from text import git_json, tape
from text_addresses import CAL, RENT
from text_nested_class import SELECTION_END, frozen
from text_partition_posterior import END as START
from text_partition_posterior import SHA as PREVIOUS_SHA
from threadpoolctl import threadpool_limits
from word_classes import Gate, vector
from word_persistence import (
    Kernels,
    fit,
    initial,
    levels,
    packet,
    reference_hidden,
    unpack,
)

REGISTRATION = "a6063e0"
END = START + 4 * CAL
SHA = "b84d18d7274bd69134041cceb653344329c52765cfbef8626782f80b836a1bbf"


def report_starts():
    return range(START + 2 * CAL, END, CAL)


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == PREVIOUS_SHA
    )
    return data


def score_delta(pred, r, y):
    assert np.all((pred > 0) & (pred < 1))
    return np.where(y, np.log(r) - np.log(pred), np.log1p(-r) - np.log1p(-pred))


def features(data):
    rows, outputs, odds, *_ = frozen(data[:SELECTION_END])
    member = vector(outputs)
    global_word = Gate(None, outputs, np.array([odds], np.uint16)).install(rows)
    obs = rows.common.observe(np.frombuffer(data, dtype=np.uint16), START, END)
    raw = rows.apply(member)[obs.query]
    r = event_prob(raw, odds / 1024)
    y = member[obs.target].astype(np.uint8)
    loss = (
        -np.log(obs.readout(rows.tables[0]))
        - y * np.log(odds / 1024)
        + np.log1p((odds / 1024 - 1) * raw)
    )
    return rows, member, odds / 1024, obs, r, y, loss, global_word


def check_gradients(lib, r, y):
    errors = {}
    points = {
        "static": [0.13],
        "iid": [-0.42, 0.71, 0.45],
        "persistent": [-0.42, 0.71, 0.45, 0.08],
        "residual": [0.17, 2.13, 0.15],
    }
    for kind, values in points.items():
        x = np.array(values)
        _, analytic = lib.objective(kind, x, r, y)
        estimate = np.empty_like(x)
        for j in range(len(x)):
            d = np.zeros_like(x)
            d[j] = 1e-5
            hi = lib.objective(kind, x + d, r, y)[0]
            lo = lib.objective(kind, x - d, r, y)[0]
            estimate[j] = (hi - lo) / (2e-5)
        errors[kind] = float(np.max(np.abs(estimate - analytic)))
        assert errors[kind] < 1e-7
    return errors


def full_vocab_check(rows, member, odds, obs, r, y, base, x, lib, word):
    count = 600
    pred, w = reference_hidden(x, r[:count], y[:count])
    measured = lib.release(word, r[:count], y[:count], initial(*unpack(word)))
    np.testing.assert_allclose(measured, pred, atol=2e-14, rtol=0)
    delta = score_delta(pred, r[:count], y[:count])
    high = 0.0
    for t in (0, 1, 2, 5, 11, 37, 106, 259, 511, 599):
        wordrow = obs.query[t]
        dense = (
            rows.count.getrow(wordrow).toarray().ravel() + 64 * rows.back
        ) / rows.den[wordrow]
        dense *= np.where(member, odds, 1.0)
        dense /= dense.sum()
        arms = np.stack([dense * np.where(member, np.exp(beta), 1.0) for beta in x[:2]])
        arms /= arms.sum(axis=1, keepdims=True)
        mixture = (1 - w[t]) * arms[0] + w[t] * arms[1]
        high = max(
            high,
            abs(mixture.sum() - 1),
            abs(mixture[member.astype(bool)].sum() - pred[t]),
            abs(-np.log(mixture[obs.target[t]]) - base[t] - delta[t]),
        )
    assert high < 2e-12
    return high


def rounding_bound(x, size, t):
    _, _, p, h = x
    lo, hi = h * p, 1 - h * (1 - p)
    aa, bb = np.sqrt(hi * (1 - lo)), np.sqrt(lo * (1 - hi))
    contraction = (aa - bb) / (aa + bb)
    delta = (logit(hi) - logit(lo)) / (size - 1)
    return {
        "levels": size,
        "sharp_contraction": contraction,
        "log_odds_spacing": delta,
        "pathwise_nll_bound": t * delta / (2 * (1 - contraction)),
        "expected_kl_if_model_true": t * delta**2 / 32 * (1 + (1 - h) ** 2 / h),
    }


def study(data, lib):
    rows, member, old_odds, obs, r, y, base, shared = features(data)
    grad = check_gradients(lib, r[:1001], y[:1001])
    words, traces, train_ms = {"base": b""}, {}, {}
    for name in ("static", "iid", "persistent", "residual"):
        start = perf_counter()
        x, traces[name] = fit(name, lib, r[:CAL], y[:CAL])
        train_ms[name] = (perf_counter() - start) * 1000
        words[name] = packet(name, x)
        if name == "persistent":
            for alt in ("persistent_u8", "persistent_u16", "iid_ablation"):
                words[alt] = packet(alt, x)
    hidden = unpack(words["persistent"])[1]
    dense = full_vocab_check(
        rows, member, old_odds, obs, r, y, base, hidden, lib, words["persistent"]
    )
    models, cpu, stream_end, deltas = {}, {}, {}, {}
    for name, word in words.items():
        label, x = unpack(word)
        carry = initial(label, x)
        releases, before_report = [], None
        for b in range(4):
            if b == 2:
                before_report = carry.copy()
            sl = slice(b * CAL, (b + 1) * CAL)
            releases.append(lib.release(word, r[sl], y[sl], carry))
        preds = np.concatenate(releases)
        init = initial(label, x)
        first = lib.release(word, r[:37], y[:37], init)
        rest = lib.release(word, r[37:], y[37:], init)
        np.testing.assert_allclose(np.r_[first, rest], preds, rtol=0, atol=2e-14)
        np.testing.assert_allclose(carry, init, atol=1e-15, rtol=0)
        if name.startswith("persistent"):
            exact, _ = reference_hidden(x, r[:600], y[:600], levels(name))
            np.testing.assert_allclose(preds[:600], exact, atol=2e-14, rtol=0)
        if name == "residual":
            state = 0.0
            for t in range(600):
                assert abs(preds[t] - expit(logit(r[t]) + x[0] + x[1] * state)) < 2e-14
                state += x[2] * (y[t] - r[t] - state)
        d = score_delta(preds, r, y)
        deltas[name] = d
        loss = base + d
        nll = loss.reshape(4, CAL).mean(axis=1)
        priced = float(nll[1] + 8 * len(word) * RENT / CAL)
        live = (
            carry.nbytes if name == "residual" or name.startswith("persistent") else 0
        )
        models[name] = {
            "packet_hex": word.hex(),
            "extra_bytes": len(word),
            "carry_bytes": live,
            "parameters": x.tolist(),
            "block_nll": nll.tolist(),
            "selection_with_incremental_rent": priced,
            "report_delta_nats": d[2 * CAL :].reshape(2, CAL).sum(axis=1).tolist(),
            "anchor_block_nll": [
                float(loss[i : i + 4096].mean()) for i in (2 * CAL, 3 * CAL)
            ],
        }
        if levels(name):
            models[name]["rounding"] = rounding_bound(x, levels(name), 2 * CAL)
            models[name]["carry_code_at_report_end"] = int(carry[0])
        samples = []
        for i in range(8):
            state = before_report.copy()
            start = perf_counter()
            got = lib.release(word, r[2 * CAL :], y[2 * CAL :], state)
            elapsed = (perf_counter() - start) * 1000
            if i:
                samples.append(round(elapsed, 4))
        np.testing.assert_allclose(got, preds[2 * CAL :], atol=2e-14, rtol=0)
        cpu[name] = samples
        stream_end[name] = float(carry[0]) if live else None
    for name in ("persistent_u8", "persistent_u16"):
        gap = deltas[name][2 * CAL :] - deltas["persistent"][2 * CAL :]
        models[name]["realized_rounding_difference_nats"] = float(gap.sum())
        assert (
            np.abs(gap).sum() <= models[name]["rounding"]["pathwise_nll_bound"] + 1e-10
        )
    selected = min(
        (name for name in words if name != "iid_ablation"),
        key=lambda v: models[v]["selection_with_incremental_rent"],
    )
    result = {
        "registration": REGISTRATION,
        "first_target": START,
        "block_length": CAL,
        "prefix_sha256": SHA,
        "shared_packet_bytes": len(shared),
        "shared_packet_sha256": hashlib.sha256(shared).hexdigest(),
        "contrast_size": int(member.sum()),
        "class_hits_by_block": y.reshape(4, CAL).sum(axis=1).tolist(),
        "selection_winner": selected,
        "fits": traces,
        "models": models,
        "end_state": stream_end,
        "gradient_max_error": grad,
        "full_vocabulary_check_error": dense,
    }
    timings = {
        "train_ms": train_ms,
        "forward_ms": cpu,
        "compiled_binary": lib.binary,
        "report_prefetched_mass_bytes": r[2 * CAL :].nbytes,
        "report_observation_bytes": y[2 * CAL :].nbytes,
        "report_output_class_mass_bytes": r[2 * CAL :].nbytes,
    }
    return result, timings


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    p.add_argument("--timing", type=Path)
    args = p.parse_args()
    with threadpool_limits(limits=1), Kernels() as lib:
        result, timings = study(load_data(args.data_dir), lib)
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched installed filters and chronological full-vocabulary losses.")
    elif args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
    if args.timing:
        args.timing.write_text(json.dumps(timings, indent=2) + "\n", encoding="utf8")
