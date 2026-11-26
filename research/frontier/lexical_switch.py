"""Learn lexical state lifetimes from causal full-vocabulary word prediction."""

import argparse
import ctypes as ct
import hashlib
import json
import os
from contextlib import contextmanager
from fractions import Fraction as F
from itertools import pairwise, product
from math import log, prod
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from causal_state import compile_libraries
from raw_word_action import RANGES, R
from text import VOCAB
from text_aggregate import FIT_END, FIT_SHA, FIT_START, tokens

HERE = Path(__file__).resolve().parent
BACKGROUND, TRAIN, VALID = 524288, 262144, 65536
POOLED, GLOBAL, WORD = "pooled", "global", "word"


@contextmanager
def native():
    with TemporaryDirectory() as temp:
        (path,) = compile_libraries(Path(temp), ("address",), HERE / "lexical_switch.c")
        lib = ct.CDLL(str(path))
        ptr = np.ctypeslib.ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS")
        for name, args in (("forward", 5), ("smooth", 6), ("finite_gate_scores", 5)):
            fn = getattr(lib, name)
            fn.argtypes = [ct.c_int] + [ptr] * args
            fn.restype = None
        try:
            yield lib
        finally:
            if os.name == "nt":
                import _ctypes

                _ctypes.FreeLibrary(lib._handle)


def windows(data, start, n):
    a = data[start - 2 : start - 2 + n].astype(np.int64)
    b = data[start - 1 : start - 1 + n].astype(np.int64)
    y = data[start : start + n].astype(np.int64)
    assert a.shape == b.shape == y.shape == (n,)
    return a, b, y


def counted(keys):
    return np.unique(keys, return_counts=True)


def lookup(table, keys):
    names, counts = table
    indices = np.minimum(np.searchsorted(names, keys), len(names) - 1)
    return np.where(names[indices] == keys, counts[indices], 0)


class Background:
    def __init__(self, a, b, y):
        counts = np.bincount(y, minlength=VOCAB)
        self.unigram = (counts + 0.5) / (len(y) + VOCAB / 2)
        self.b_context = np.bincount(b, minlength=VOCAB)
        self.by = counted(b * VOCAB + y)
        self.ab = counted(a * VOCAB + b)
        self.aby = counted((a * VOCAB + b) * VOCAB + y)
        self.names = np.argsort(-counts, kind="stable")[:256]
        self.bins = np.full(VOCAB, 256, np.int64)
        self.bins[self.names] = np.arange(256)

    def forecasts(self, a, b, y):
        p0 = self.unigram[y]
        p1 = (lookup(self.by, b * VOCAB + y) + 16 * p0) / (self.b_context[b] + 16)
        pair = a * VOCAB + b
        p2 = (lookup(self.aby, pair * VOCAB + y) + 16 * p1) / (
            lookup(self.ab, pair) + 16
        )
        return p0, p1, p2


def vectors(rows, weight, base, y):
    shared = (1 - weight) * base
    return shared + weight * rows[0, y], shared + weight * rows[1, y]


def filter_state(lib, e0, e1, r, smooth=False):
    n = len(e0)
    filtered = np.empty(n)
    loss = np.empty(n)
    lib.forward(n, e0, e1, r, filtered, loss)
    if not smooth:
        return loss
    posterior = np.empty(n)
    switches = np.empty(n)
    lib.smooth(n, e0, e1, r, filtered, posterior, switches)
    return loss, posterior, switches


def lexical(counts, unigram):
    return (counts + 64 * unigram) / (counts.sum() + 64)


def fit(lib, mode, init, weight, y, base, bins, unigram):
    if mode == POOLED:
        head = lexical(np.bincount(y, minlength=VOCAB), unigram)
        for _ in range(12):
            tail = weight * head[y]
            selected = tail / ((1 - weight) * base + tail)
            head = lexical(np.bincount(y, weights=selected, minlength=VOCAB), unigram)
        return np.vstack((head, head)), np.full(1, 0.5)
    ids = np.zeros_like(y) if mode == GLOBAL else bins
    groups = 1 if mode == GLOBAL else 257
    visits = np.bincount(ids[:-1], minlength=groups)
    i = np.arange(len(y))
    mask = i >= len(y) // 2 if init == "halves" else ((i // 128) % 2).astype(bool)
    rows = np.array(
        [lexical(np.bincount(y[m], minlength=VOCAB), unigram) for m in (~mask, mask)]
    )
    rates = np.full(groups, 1 / 32)
    for _ in range(12):
        e0, e1 = vectors(rows, weight, base, y)
        _, post, switch = filter_state(lib, e0, e1, rates[ids], True)
        for s, (prob, resp) in enumerate(((e0, 1 - post), (e1, post))):
            selection = resp * weight * rows[s, y] / prob
            rows[s] = lexical(
                np.bincount(y, weights=selection, minlength=VOCAB), unigram
            )
        changes = np.bincount(ids[:-1], weights=switch[:-1], minlength=groups)
        rates = (changes + 0.5) / (visits + 16)
    return rows, rates


def score(lib, model, bins, base, y, rate_override=None):
    rows, rates, weight = model
    e0, e1 = vectors(rows, weight, base, y)
    if rate_override is not None:
        r = np.full(len(y), rate_override)
    elif len(rates) == 1:
        r = np.full(len(y), rates[0])
    else:
        r = rates[bins]
    return filter_state(lib, e0, e1, r)


def checksum(rows, rates, weight):
    blob = b"".join(
        np.ascontiguousarray(z, dtype="<f8").tobytes() for z in (rows, rates, [weight])
    )
    return hashlib.sha256(blob).hexdigest()


def summarize(loss):
    return {
        "mean": float(loss.mean()),
        "total": float(loss.sum()),
        "block_means": loss.reshape(8, -1).mean(axis=1).tolist(),
    }


def learn(lib, bg, training, validation):
    _, _, y = training
    _, _, v = validation
    base = bg.forecasts(*training)[2]
    vbase = bg.forecasts(*validation)[2]
    fits = {}
    candidates = {}
    for mode in (POOLED, GLOBAL, WORD):
        entries = []
        best = float("inf")
        for weight in (1 / 16, 1 / 4):
            for init in ("pooled",) if mode == POOLED else ("halves", "blocks128"):
                rows, rates = fit(
                    lib, mode, init, weight, y, base, bg.bins[y], bg.unigram
                )
                model = rows, rates, weight
                valid_loss = float(score(lib, model, bg.bins[v], vbase, v).mean())
                entries.append(
                    {
                        "lambda": weight,
                        "initialization": init,
                        "validation": valid_loss,
                        "array_sha256": checksum(*model),
                    }
                )
                if valid_loss < best:
                    best = valid_loss
                    fits[mode] = model
        candidates[mode] = entries
    return fits, candidates


def experiment(lib, directory):
    data = tokens("train_source", FIT_END, FIT_SHA, directory)
    bg = Background(*windows(data, FIT_START, BACKGROUND))
    training = windows(data, FIT_START + BACKGROUND, TRAIN)
    validation = windows(data, FIT_START + BACKGROUND + TRAIN, VALID)
    fits, candidates = learn(lib, bg, training, validation)
    for rows, rates, _ in fits.values():
        rows.flags.writeable = False
        rates.flags.writeable = False
    rows, rates, weight = fits[WORD]
    visits = np.bincount(bg.bins[training[2][:-1]], minlength=257)
    average = float(visits @ rates / visits.sum())
    rate_order = np.argsort(rates[:256], kind="stable")
    selected = {
        key: min(entries, key=lambda e: e["validation"])
        for key, entries in candidates.items()
    }
    for name, model in fits.items():
        assert selected[name]["array_sha256"] == checksum(*model)
    reports = []
    for role, start, digest in RANGES:
        data = tokens(role, start + R, digest, directory)
        window = windows(data, start, R)
        y = window[2]
        p0, p1, p2 = bg.forecasts(*window)
        bins = bg.bins[y]
        losses = {
            k: -np.log(p) for k, p in (("unigram", p0), ("bigram", p1), ("trigram", p2))
        }
        for mode, model in fits.items():
            losses[mode] = score(lib, model, bins, p2, y)
        losses["word_mean_rate"] = score(lib, fits[WORD], bins, p2, y, average)
        e0, e1 = vectors(rows, weight, p2, y)
        spin = 0.0
        spin_error = 0.0
        for i in range(257):
            mid = (e0[i] + e1[i]) / 2
            contrast = (e1[i] - e0[i]) / (2 * mid)
            observed = mid * (1 + spin * contrast)
            spin_error = max(spin_error, abs(-log(observed) - losses[WORD][i]))
            spin = (1 - 2 * rates[bins[i]]) * (spin + contrast) / (1 + spin * contrast)
        assert spin_error < 1e-13
        det = np.empty(R)
        rand = np.empty(R)
        lib.finite_gate_scores(R, e0, e1, rates[bins], det, rand)
        losses["word_det4"], losses["word_random4"] = det, rand
        constant = np.full(R, average)
        direction = rates[bins] - average
        _, _, smoothed_switch = filter_state(lib, e0, e1, constant, True)
        slope = -float(direction[:-1] @ (smoothed_switch[:-1] - average)) / (
            R * average * (1 - average)
        )
        distance = 1e-3
        below = filter_state(lib, e0, e1, constant - distance * direction).mean()
        above = filter_state(lib, e0, e1, constant + distance * direction).mean()
        assert abs((above - below) / (2 * distance) - slope) < 2e-9
        supplemental = {
            "fixed_rows_balanced_nll": summarize(-np.log((e0 + e1) / 2)),
            "mean_rate_directional_nll_slope": slope,
            "independent_257_token_max_error": spin_error,
        }
        reports.append(
            {
                "role": role,
                "start": start,
                "tokens": R,
                "prefix_sha256": digest,
                "postregistration_controls": supplemental,
                "losses": {k: summarize(v) for k, v in losses.items()},
            }
        )
    tables = (bg.by, bg.ab, bg.aby)
    return {
        "registration": "319888a",
        "validation": candidates,
        "selected": selected,
        "global_rate": float(fits[GLOBAL][1][0]),
        "word_mean_rate": average,
        "word_rate_min_max": [float(rates.min()), float(rates.max())],
        "word_tail_rate": float(rates[-1]),
        "top256_rates_above_half": int(sum(rates[:256] > 0.5)),
        "lowest_highest_rate_word_ids": bg.names[rate_order[[0, -1]]].tolist(),
        "word_head_total_variation": float(abs(rows[0] - rows[1]).sum() / 2),
        "background_sparse_key_counts": [len(k) for k, _ in tables],
        "background_count_and_probability_array_bytes": int(
            sum(k.nbytes + c.nbytes for k, c in tables)
            + bg.b_context.nbytes
            + bg.unigram.nbytes
        ),
        "word_head_and_rate_bytes": rows.nbytes + rates.nbytes,
        "word_group_lookup_bytes": bg.bins.nbytes,
        "reports": reports,
    }


def check_reset_words():
    # The reset distribution is uniform, while the literal background varies
    # with the last word. Name 2 has identical emissions in the two states.
    delta = (F(1, 16), F(-1, 24), F(0), F(-1, 48))
    hold = (F(1, 3), F(-1, 4), F(3, 4), F(0))
    symbols = range(len(delta))

    def center(prefix, x):
        return F(1, 4) + F((x == prefix[-1]) * 4 - 1, 32)

    def mass(tape, d):
        weights = [F(1, 2), F(1, 2)]
        h = [0]
        for x in tape:
            avg = center(h, x)
            lo, hi = weights[0] * (avg - d[x]), weights[1] * (avg + d[x])
            same = (1 + hold[x]) / 2
            weights = [same * lo + (1 - same) * hi, (1 - same) * lo + same * hi]
            h.append(x)
        return sum(weights)

    k = {}
    for x, y in product(symbols, repeat=2):
        k[x, y] = mass((x, y), delta) - center([0], x) * center([x], y)
        assert k[x, y] == hold[x] * delta[x] * delta[y]
    rates = {}
    for x, y, z in product(symbols, repeat=3):
        ax, ay, az = center([0], x), center([x], y), center([y], z)
        residual = mass((x, y, z), delta) - ax * ay * az - ax * k[y, z] - k[x, y] * az
        assert residual == ay * hold[y] * k[x, z]
        if k[x, z]:
            rates[y] = residual / (ay * k[x, z])
    assert [rates[x] for x in symbols] == list(hold)
    assert all(k[0, y] / (rates[0] * delta[0]) == delta[y] for y in symbols)
    # All informative names reset. The two nonzero emission contrasts cancel
    # in a fair state. Other names can preserve the state but never polarize it.
    pooled_delta = (F(0), F(0), F(1, 24), F(-1, 24))
    hold = (F(1, 3), F(-1, 4), F(0), F(0))
    for word in product(symbols, repeat=4):
        past = (0,) + word
        assert mass(word, pooled_delta) == prod(
            center(past[: i + 1], x) for i, x in enumerate(word)
        )
    return len(k), len(symbols) ** 3, len(symbols) ** 4


def check(lib):
    # Exact latent-path summation tests the forward/backward updates independently.
    n = 6
    e0 = [F(1, 4), F(2, 3), F(3, 4), F(2, 5), F(5, 8), F(1, 3)]
    e1 = [F(2, 3), F(1, 3), F(1, 6), F(4, 5), F(1, 4), F(2, 3)]
    rates = [F(0), F(1, 7), F(1), F(2, 3), F(1, 2), F(1, 7)]
    emissions = (e0, e1)
    mass = F(0)
    posterior = [F(0)] * n
    switches = [F(0)] * n
    for path in product((0, 1), repeat=n):
        w = F(1, 2) * prod(emissions[s][i] for i, s in enumerate(path))
        w *= prod(
            (rates[i] if a != b else 1 - rates[i])
            for i, (a, b) in enumerate(pairwise(path))
        )
        mass += w
        for i, s in enumerate(path):
            posterior[i] += s * w
            if i + 1 < n:
                switches[i] += (s != path[i + 1]) * w
    arrays = [np.array(v, dtype=float) for v in (e0, e1, rates)]
    loss, post, switch = filter_state(lib, *arrays, True)
    assert abs(loss.sum() + log(mass)) < 2e-14
    np.testing.assert_allclose(
        post, [float(v / mass) for v in posterior], atol=2e-14, rtol=0
    )
    np.testing.assert_allclose(
        switch, [float(v / mass) for v in switches], atol=2e-14, rtol=0
    )
    a = np.array([1, 2, 1, 2, 3], dtype=np.int64)
    b = np.array([2, 1, 2, 3, 1], dtype=np.int64)
    y = np.array([1, 2, 3, 1, 4], dtype=np.int64)
    bg = Background(a, b, y)
    possible = np.arange(VOCAB)
    for u, v in ((1, 2), (3, 1), (20, 20)):
        for law in bg.forecasts(np.full(VOCAB, u), np.full(VOCAB, v), possible):
            assert abs(law.sum() - 1) < 3e-15 and np.all(law > 0)
    from block_rescue import rounded_weight
    from random_gate import allocation, grid

    det = np.empty(n)
    rand = np.empty(n)
    lib.finite_gate_scores(n, *arrays, det, rand)
    levels = grid(16)
    live = dict(allocation(F(1, 2), levels, 256))
    d = rounded_weight(F(1, 2), 16)
    for t in range(n):
        combined = (1 - d) * e0[t] + d * e1[t]
        assert abs(det[t] + log(combined)) < 2e-14
        d = rounded_weight(rates[t] + (1 - 2 * rates[t]) * d * e1[t] / combined, 16)
        expected = 0.0
        after = {}
        for j, w in live.items():
            v = levels[j]
            p = (1 - v) * e0[t] + v * e1[t]
            expected -= float(w) * log(p)
            z = rates[t] + (1 - 2 * rates[t]) * v * e1[t] / p
            for dest, chance in allocation(z, levels, 256):
                after[dest] = after.get(dest, F(0)) + w * chance
        assert abs(rand[t] - expected) < 2e-14
        live = after
    pairs, triples, degenerate = check_reset_words()
    reactive = {}
    for h in (2, 4, 8, 16, 32):
        levels = grid(h)
        choices = allocation(F(1, 2), levels, h * h)
        assert [w for _, w in choices] == [F(1, 2), F(1, 2)]
        for j, _ in choices:
            least = min(levels[j], 1 - levels[j])
            assert F(1, 2) / least == 1 + F(2, h) + F(2, h * h)
        reactive[h] = log(F(1, 2) / least)
    return {
        "exact_hidden_paths": 2**n,
        "exact_position_posteriors_and_switches": 2 * n,
        "finite_gate_token_losses": 2 * n,
        "full_vocabulary_normalization_checks": 9,
        "reset_word_pairs_triples_and_degenerate_quads": [pairs, triples, degenerate],
        "report_reactive_excess_per_round": reactive,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with native() as lib:
        report = (
            check(lib) if args.command == "check" else experiment(lib, args.directory)
        )
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(encoded.encode())
    else:
        print(encoded, end="")
