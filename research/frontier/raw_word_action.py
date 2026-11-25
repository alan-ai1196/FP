"""Learn deterministic raw-name updates by profiled one-coordinate comparisons."""

import argparse
import base64
import ctypes as c
import hashlib
import json
import os
import struct
import zlib
from contextlib import contextmanager
from functools import partial
from math import log
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from causal_state import compile_libraries
from scipy.special import gammaln, logsumexp
from text import VOCAB
from text_aggregate import FIT_SHA, FIT_START, HISTORY, TAU, K, tokens
from word_token_action import Q16, base_words, fixed_counts, pack, read_head, units

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "raw_word_action_fits.json"
N, V, R = 262144, 32768, 65536
REGISTRATION = "a4c1f9f"
RANGES = (
    (
        "train_source",
        11262144,
        "c8fb3cb4738470487659b9829bd88eb97c0e3d6ff158d4140e4bef4925efa775",
    ),
    (
        "reporting_source",
        524288,
        "d6e685d68cb5e07060ee4c5c181dec6e41429a79e496b04bfe0893366f8a407c",
    ),
)
MODES = (
    "actions",
    "last_bit",
    "last_two_bits",
    "constant",
    "class_bigram",
    "class_trigram",
    "raw_bigram",
)
PRICE = 8 * log(2) / R


def sha(b):
    return hashlib.sha256(b).hexdigest()


@contextmanager
def native():
    with TemporaryDirectory() as directory:
        (path,) = compile_libraries(
            Path(directory), ("address",), HERE / "raw_word_action.c"
        )
        lib = c.CDLL(str(path))
        ptr = partial(np.ctypeslib.ndpointer, ndim=1, flags="C_CONTIGUOUS")
        u8, u16, i32, f64 = map(ptr, (np.uint8, np.uint16, np.int32, np.float64))
        lib.fit_actions.argtypes = [
            c.c_int,
            c.c_int,
            c.c_int,
            u16,
            u8,
            f64,
            c.c_int,
            i32,
            c.c_int,
            c.c_double,
            c.c_int,
            u8,
            i32,
            f64,
            c.POINTER(c.c_uint64),
        ]
        lib.fit_actions.restype = c.c_int
        lib.states.argtypes = [c.c_int, c.c_int, c.c_int, u16, u8, u8]
        lib.states.restype = None
        try:
            yield lib
        finally:
            if os.name == "nt":
                import _ctypes

                _ctypes.FreeLibrary(lib._handle)


def states(lib, mode, actions, x, initial=0):
    assert mode in (0, 1, 2) and 0 <= initial < (4 if mode == 2 else 2)
    assert len(actions) > x.max() and actions.max() < (2 if mode else 4)
    out = np.empty(len(x), dtype=np.uint8)
    lib.states(len(x), mode, initial, x, actions, out)
    return out


def hist(state, y, rows):
    return fixed_counts(state.astype(np.int32), y, rows)


def objective(ct, alpha):
    return float(
        (gammaln(ct + alpha) - gammaln(alpha)).sum()
        - (gammaln(ct.sum(axis=1) + alpha.sum()) - gammaln(alpha.sum())).sum()
    )


def optimize(lib, x, y, alpha, mode, initial, default, order, price, sweeps=8):
    actions = initial.copy()
    assert (
        len(x) == len(y) and len(x) < 2**31 and x.max() < len(actions) and y.max() < K
    )
    assert len(alpha) == K and min(alpha) > 0 and actions.max() < (2 if mode else 4)
    assert len(order) and min(order) >= 0 and max(order) < len(actions)
    penalty = price * (16 if mode else 18) * log(2)
    moves = np.zeros(sweeps, dtype=np.int32)
    history = np.zeros(sweeps + 1)
    visited = c.c_uint64()
    used = lib.fit_actions(
        len(x),
        len(actions),
        mode,
        x,
        y,
        alpha,
        len(order),
        order,
        default,
        penalty,
        sweeps,
        actions,
        moves,
        history,
        c.byref(visited),
    )
    if used < 1:
        raise MemoryError("coordinate fit workspace unavailable")
    a = states(lib, mode, actions, x)
    ct = hist(a, y, 4 if mode == 2 else 2)
    check = objective(ct, alpha) - np.count_nonzero(actions != default) * penalty
    np.testing.assert_allclose(history[used], check, rtol=0, atol=3e-6)
    assert np.all(np.diff(history[: used + 1]) >= -1e-8)
    return (
        actions,
        ct,
        {
            "moves": moves[:used].tolist(),
            "final_objective": check,
            "trial_coordinates": used * len(order) * (1 if mode else 3),
            "influence_positions_visited": visited.value,
        },
    )


def packed_values(a, width):
    bits = (a[:, None] >> np.arange(width, dtype=np.uint8)) & 1
    return np.packbits(bits.reshape(-1), bitorder="little").tobytes()


def unpacked_values(b, n, width):
    bits = np.unpackbits(np.frombuffer(b, dtype=np.uint8), bitorder="little")[
        : n * width
    ]
    return np.sum(
        bits.reshape(n, width) << np.arange(width, dtype=np.uint8),
        axis=1,
        dtype=np.uint8,
    )


def encode(mode, a, heads):
    if mode == 0 and a.max() <= 1:
        mode = 1
    width = 1 if mode else 2
    default = int(np.bincount(a).argmax())
    ids = np.flatnonzero(a != default).astype("<u2")
    sparse = struct.pack("<BBH", mode, default, len(ids)) + ids.tobytes()
    if not mode:
        sparse += packed_values(a[ids], width)
    dense = struct.pack("<BBH", mode | 128, 0, 0) + packed_values(a, width)
    return min((sparse, dense), key=len) + bytes.fromhex(pack(heads))


def decode(b, d=VOCAB):
    mode = b[0] & 127
    if mode > 2:
        if mode == 6:
            size = int.from_bytes(b[1:3], "little")
            ids = np.frombuffer(b, dtype="<u2", count=size, offset=3)
            a = np.zeros(d, dtype=np.int32)
            a[ids] = np.arange(1, size + 1)
            pos = 3 + 2 * size
        else:
            a, pos = None, 1
    else:
        _, default, size = struct.unpack_from("<BBH", b)
        width, pos = (1 if mode else 2), 4
        if b[0] & 128:
            stop = pos + (d * width + 7) // 8
            a = unpacked_values(b[pos:stop], d, width)
            pos = stop
        else:
            ids = np.frombuffer(b, dtype="<u2", count=size, offset=pos)
            pos += 2 * size
            a = np.full(d, default, dtype=np.uint8)
            if mode:
                a[ids] = 1 - default
            else:
                stop = pos + (size * width + 7) // 8
                a[ids] = unpacked_values(b[pos:stop], size, width)
                pos = stop
    return mode, a, read_head(b[pos:].hex())


def contexts(lib, mode, a, x, classes, initial=None):
    if mode <= 2:
        return states(lib, mode, a, x, 0 if initial is None else initial)
    if mode == 3:
        return np.zeros(len(x), dtype=np.uint8)
    if mode == 6:
        return a[x]
    now = classes[x]
    if mode == 4:
        return now
    assert mode == 5
    before = np.r_[K - 1 if initial is None else initial % K, now[:-1]]
    return K * before + now


def fit_sequence(directory):
    data, names, classes, within = base_words(directory)
    clip = data[FIT_START - 1 : FIT_START + N + V]
    alpha = (
        TAU
        * (np.bincount(classes[data[:HISTORY]], minlength=K) + 0.5)
        / (HISTORY + K / 2)
    )
    return clip, classes[clip[1:]].astype(np.uint8), names, classes, within, alpha


def direct(mode, x, y, classes, prior):
    if mode == 6:
        ids, addr = np.unique(x, return_inverse=True)
        ct = hist(1 + addr, y, len(ids) + 1)
        return (
            struct.pack("<BH", mode, len(ids))
            + ids.astype("<u2").tobytes()
            + bytes.fromhex(pack(units(ct, prior)))
        )
    addr = contexts(None, mode, None, x, classes)
    ct = hist(addr, y, K ** (mode - 3))
    return bytes((mode,)) + bytes.fromhex(pack(units(ct, prior)))


def compiled_mixture(packets, logits):
    return struct.pack("<BH", 7, len(packets)) + b"".join(
        struct.pack("<Id", len(b), w) + b for b, w in zip(packets, logits, strict=True)
    )


def mixture_members(b):
    assert b[0] == 7
    count = int.from_bytes(b[1:3], "little")
    pos = 3
    for _ in range(count):
        length, w = struct.unpack_from("<Id", b, pos)
        pos += 12
        yield b[pos : pos + length], w
        pos += length
    assert pos == len(b)


def fit(lib, directory):
    clip, y, names, classes, within, alpha = fit_sequence(directory)
    words = clip[:-1]
    x, targets = words[:N], y[:N]
    freq = np.bincount(x, minlength=VOCAB)
    order = np.flatnonzero(freq)
    order = order[np.argsort(-freq[order], kind="stable")].astype(np.int32)
    frequent = (classes < 8).astype(np.uint8)
    association = np.bincount(x, weights=(targets < 8), minlength=VOCAB)
    associated = ((freq >= 8) & (association > freq * np.mean(targets < 8))).astype(
        np.uint8
    )
    hold = np.full(VOCAB, 2, dtype=np.uint8)
    hold[names] = frequent[names]
    candidates = {0: set(), 1: set(), 2: set()}
    programs, vals, runs = {}, {}, []
    # The lexical term is common to every program, including the mixture.
    lexical = float(-np.log(within[clip[N + 1 :]]).mean())

    def register(b):
        key = sha(b)
        if key not in programs:
            mode, a, rows = decode(b)
            last = int(contexts(lib, mode, a, x, classes)[-1])
            vs = contexts(lib, mode, a, words[N:], classes, last)
            vals[key] = float(-np.log(rows[vs, y[N:]] / Q16).sum())
            programs[key] = b
        return key

    def search(mode, start, tag, default, price):
        a, ct, info = optimize(
            lib, x, targets, alpha, mode, start, default, order, price
        )
        b = encode(mode, a, units(ct, alpha / TAU))
        key = register(b)
        candidates[mode].add(key)
        runs.append(
            dict(info, mode=MODES[mode], seed=tag, nominal_price=price, sha256=key)
        )
        if mode == 1:
            candidates[0].add(key)
        return a

    for price in (0.0, 0.25, 1.0):
        for tag, seed in (("frequent", frequent), ("associated", associated)):
            part = search(1, seed, tag, 0, price)
            search(2, seed, tag, 0, price)
            search(0, part, "fitted_" + tag, 0, price)
        search(0, hold, "hold_and_two_reset_sets", 2, price)

    selected = {}
    for mode, members in candidates.items():
        for priced in (False, True):
            key = min(
                members,
                key=lambda h: (
                    vals[h] / V + (PRICE * len(programs[h]) if priced else 0),
                    len(programs[h]),
                    h,
                ),
            )
            selected[MODES[mode] + ("_priced" if priced else "")] = key
    chosen = programs[selected["actions"]]
    mode, actions, _ = decode(chosen)
    after = states(lib, mode, actions, x)
    ones = np.bincount(x, weights=after, minlength=VOCAB)
    ablated = np.where(actions < 2, actions, (ones > freq / 2)).astype(np.uint8)
    ct = hist(ablated[x], targets, 2)
    selected["feedback_removed"] = register(encode(1, ablated, units(ct, alpha / TAU)))
    for mode in (3, 4, 5, 6):
        selected[MODES[mode]] = register(direct(mode, x, targets, classes, alpha / TAU))
    members = sorted(candidates[0])
    logits = [min(vals[h] for h in members) - vals[key] for key in members]
    mix = compiled_mixture([programs[h] for h in members], logits)
    kept = sorted(set(selected.values()) | set(members))
    first = np.full(VOCAB, N, dtype=np.int32)
    last = np.full(VOCAB, -1, dtype=np.int32)
    sequence = np.arange(N, dtype=np.int32)
    np.minimum.at(first, x, sequence)
    np.maximum.at(last, x, sequence)
    live = np.bincount(first[order], minlength=N) - np.bincount(
        last[order], minlength=N
    )
    return {
        "registration": REGISTRATION,
        "fit_prefix": FIT_SHA,
        "train": N,
        "validation": V,
        "vocabulary": VOCAB,
        "fit_input_names": len(order),
        "class_names": names.tolist(),
        "max_names_crossing_a_training_cut": int(np.cumsum(live).max()),
        "runs": runs,
        "selected": selected,
        "programs": {
            h: {
                "bytes": len(programs[h]),
                "validation_word_nll": lexical + vals[h] / V,
                # The large direct bigram is determined byte-for-byte by the fit tape alone.
                "zlib_b85": (
                    None
                    if h == selected["raw_bigram"]
                    else base64.b85encode(zlib.compress(programs[h], 9)).decode("ascii")
                ),
            }
            for h in kept
        },
        "mixture": {
            "members": members,
            "relative_log_weights": logits,
            "bytes": len(mix),
            "sha256": sha(mix),
        },
    }


def score(lib, directory, frozen):
    f = json.loads(frozen.read_text())
    assert f["registration"] == REGISTRATION
    clip, y, names, classes, within, alpha = fit_sequence(directory)
    assert names.tolist() == f["class_names"]
    programs = {}
    for h, record in f["programs"].items():
        payload = record["zlib_b85"]
        b = (
            zlib.decompress(base64.b85decode(payload))
            if payload is not None
            else direct(6, clip[:N], y[:N], classes, alpha / TAU)
        )
        assert sha(b) == h and len(b) == record["bytes"]
        programs[h] = b
    mixture = f["mixture"]
    mix = compiled_mixture(
        [programs[h] for h in mixture["members"]], mixture["relative_log_weights"]
    )
    assert sha(mix) == mixture["sha256"] and len(mix) == mixture["bytes"]
    parts = list(mixture_members(mix))
    weights = np.array([w for _, w in parts])
    weights = np.exp(weights - logsumexp(weights))
    total_within = np.bincount(classes, weights=within, minlength=K)
    assert max(abs(total_within - 1)) < 1e-11
    out = []
    for role, start, digest in RANGES:
        words = tokens(role, start + R, digest, directory)[start - 1 :]
        x, y = words[:-1], classes[words[1:]]
        lexical = -np.log(within[words[1:]])
        forecasts, diagnostics = {}, {}
        for h, b in programs.items():
            mode, a, rows = decode(b)
            address = contexts(lib, mode, a, x, classes)
            assert np.max(np.abs((rows / Q16) @ total_within - 1)) < 1e-11
            forecasts[h] = rows[address, y] / Q16
            if h in (f["selected"]["actions"], f["selected"]["actions_priced"]):
                updates = a[x]
                prev = np.r_[0, address[:-1]]
                feedback = updates >= 2
                # For the same last two raw words, can both fitted states occur?
                key = x[:-1].astype(np.int64) * VOCAB + x[1:]
                _, idx = np.unique(key, return_inverse=True)
                bybit = np.zeros((2, int(idx.max()) + 1), dtype=np.int64)
                np.add.at(bybit, (address[1:], idx), 1)
                diagnostics[h] = {
                    "alphabet_update_counts": np.bincount(a, minlength=4).tolist(),
                    "token_update_counts": np.bincount(updates, minlength=4).tolist(),
                    "feedback_by_prestate": np.bincount(
                        prev[feedback], minlength=2
                    ).tolist(),
                    "ambiguous_observed_raw_pairs": int(
                        np.count_nonzero(bybit.min(axis=0))
                    ),
                    "occurrences_of_ambiguous_pairs": int(
                        bybit[:, bybit.min(axis=0) > 0].sum()
                    ),
                }
        pmix = weights @ np.stack([forecasts[sha(b)] for b, _ in parts])
        against = {name: forecasts[h] for name, h in f["selected"].items()}
        against["mixture"] = pmix
        losses = {}
        for name, probabilities in against.items():
            loss = lexical - np.log(probabilities)
            losses[name] = {
                "word_nll": float(loss.mean()),
                "blocks": loss.reshape(8, -1).mean(axis=1).tolist(),
            }
        out.append(
            {
                "role": role,
                "start": start,
                "words": R,
                "prefix_sha256": digest,
                "losses": losses,
                "action_diagnostics": diagnostics,
            }
        )
    return {
        "registration": REGISTRATION,
        "frozen_sha256": sha(frozen.read_text(encoding="utf-8").encode("utf-8")),
        "mixture_max_weight": float(weights.max()),
        "mixture_effective_members": float(1 / (weights @ weights)),
        "sources": out,
    }


def direct_score(v, mode, x, y, alpha, price):
    s, path = 0, []
    for token in x:
        op = int(v[token])
        s = (2 * s + op) % 4 if mode == 2 else (op if op < 2 else s ^ (op - 2))
        path.append(s)
    ct = hist(np.array(path), y, 4 if mode == 2 else 2)
    return objective(ct, alpha) - np.count_nonzero(v) * price * (
        16 if mode else 18
    ) * log(2)


def reference(lib):
    from itertools import product

    rng = np.random.default_rng(251126)
    checked = 0
    for mode, seed, price in product(range(3), range(9), (0, 0.25)):
        d = 5
        x = rng.integers(d, size=47, dtype=np.uint16)
        x[2:7] = 1
        y = rng.integers(0, K, size=len(x), dtype=np.uint8)
        alpha = np.linspace(0.25, 2.25, K)
        a = rng.integers(2 if mode else 4, size=d, dtype=np.uint8)
        if seed == 0:
            a[:] = 0 if mode else 2
        start = a.copy()
        order = np.arange(d, dtype=np.int32)
        for i in order:
            high, winner = direct_score(a, mode, x, y, alpha, price), a[i]
            for op in range(2 if mode else 4):
                trial = a.copy()
                trial[i] = op
                val = direct_score(trial, mode, x, y, alpha, price)
                if val > high + 1e-8:
                    high, winner = val, op
            a[i] = winner
            checked += 1
        got, ct, _ = optimize(lib, x, y, alpha, mode, start, 0, order, price, sweeps=1)
        np.testing.assert_array_equal(got, a)
        rows = units(ct, alpha / alpha.sum())
        b = encode(mode, got, rows)
        decoded, actions, heads = decode(b, d=d)
        np.testing.assert_array_equal(got, actions)
        np.testing.assert_array_equal(heads, rows)
        np.testing.assert_array_equal(
            states(lib, decoded, actions, x), states(lib, mode, got, x)
        )
    return {"brute_sequential_coordinates": checked, "sweeps": 54}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "fit", "score"))
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--frozen", type=Path, default=FROZEN)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with native() as lib:
        if args.command == "check":
            result = reference(lib)
        elif args.command == "fit":
            result = fit(lib, args.directory)
        else:
            result = score(lib, args.directory, args.frozen)
    s = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(s.encode("utf-8"))
    else:
        print(s, end="")


if __name__ == "__main__":
    main()
