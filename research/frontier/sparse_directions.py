"""Freeze a subset of an existing diagonal error filter using only its old fit and selection."""

import _ctypes
import argparse
import ctypes
import json
import os
import struct
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from causal_state import binary_sizes, compile_libraries
from direction_learning import decode
from scipy.signal import lfilter
from text_addresses import RENT
from threadpoolctl import threadpool_limits

FIT, VAL = 32768, 16384
RATE = 1 / 512
CAPS = (1, 2, 4, 8, 16, 33)
REGISTRATION = "c0bf3a0"


class Native:
    def __enter__(self):
        self.tmp = TemporaryDirectory()
        (path,) = compile_libraries(
            Path(self.tmp.name),
            ("address",),
            Path(__file__).with_name("sparse_direction.c"),
        )
        self.binary = binary_sizes(path)
        self.lib = ctypes.CDLL(str(path))
        pd = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
        py = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
        pi = np.ctypeslib.ndpointer(np.int16, flags="C_CONTIGUOUS")
        u = ctypes.c_uint32
        self.lib.error_grid.argtypes = [u, u, pd, py, ctypes.c_double, pi, pd]
        self.lib.error_grid.restype = None
        self.lib.subset_stream.argtypes = [
            u,
            u,
            pd,
            py,
            u,
            py,
            pd,
            ctypes.c_double,
            u,
            ctypes.c_void_p,
            pd,
        ]
        self.lib.subset_stream.restype = u
        return self

    def __exit__(self, *exc):
        (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(self.lib._handle)
        self.tmp.cleanup()

    def histories(self, q, y, packed):
        d = q.shape[1]
        if packed:
            out = np.empty(q.shape)
            self.lib.error_grid(len(q), d, q, y, RATE, np.zeros(d, np.int16), out)
            return out
        errors = -q.copy()
        errors[np.arange(len(y)), y] += 1
        return lfilter([0.0, RATE], [1.0, RATE - 1.0], errors, axis=0)

    def stream(self, q, y, col, gamma, carry):
        out = np.empty(len(y))
        repairs = self.lib.subset_stream(
            len(y),
            q.shape[1],
            q,
            y,
            len(col),
            col,
            gamma,
            RATE,
            int(carry.dtype == np.int16),
            carry.ctypes.data,
            out,
        )
        return out, int(repairs)


def encode(chosen, ids, gamma, packed):
    if not chosen:
        return b""
    tail = len(ids) in chosen
    active = [c for c in sorted(chosen) if c < len(ids)]
    word = struct.pack("<BBBB", 2 if packed else 1, 9, len(active), int(tail))
    for c in active:
        word += struct.pack("<Hh", int(ids[c]), round(256 * gamma[c]))
    if tail:
        word += struct.pack("<h", round(256 * gamma[-1]))
        word += np.asarray(
            [v for c, v in enumerate(ids) if c not in chosen], dtype="<u2"
        ).tobytes()
    return word


def unpack(word, ids):
    if not word:
        return np.empty(0, np.uint8), np.empty(0), False
    kind, shift, n, tail = struct.unpack_from("<BBBB", word)
    assert kind in (1, 2) and shift == 9 and tail in (0, 1)
    lookup = {int(v): c for c, v in enumerate(ids)}
    idx, vals = [], []
    for j in range(n):
        raw, g = struct.unpack_from("<Hh", word, 4 + 4 * j)
        idx.append(lookup[raw])
        vals.append(g / 256)
    off = 4 + 4 * n
    if tail:
        idx.append(len(ids))
        vals.append(struct.unpack_from("<h", word, off)[0] / 256)
        others = np.frombuffer(word, dtype="<u2", offset=off + 2)
        assert sorted(lookup[x] for x in others) == [
            c for c in range(len(ids)) if c not in idx
        ]
    else:
        assert len(word) == off
    assert idx == sorted(set(idx))
    return np.array(idx, np.uint8), np.array(vals), kind == 2


class Score:
    def __init__(self, q, y, z):
        self.a = np.ascontiguousarray((q * np.expm1(z)).T)
        self.hit = np.bincount(y, weights=z[np.arange(len(y)), y], minlength=q.shape[1])
        self.size = len(y)

    def cost(self, subset):
        if not subset:
            return 0.0
        subset = list(subset)
        return float(
            np.log1p(self.a[subset].sum(axis=0)).sum() - self.hit[subset].sum()
        )

    def nested(self, growing):
        d = len(self.a)
        kept = set() if growing else set(range(d))
        v = np.zeros(self.size) if growing else self.a.sum(axis=0)
        sign = 1 if growing else -1
        path = [tuple(sorted(kept))]
        for _ in range(d):
            options = sorted(set(range(d)) - kept if growing else kept)
            # Terms already shared by all candidates drop out.
            j = min(
                options,
                key=lambda c: float(
                    np.log1p(v + sign * self.a[c]).sum() - sign * self.hit[c]
                ),
            )
            if growing:
                kept.add(j)
            else:
                kept.remove(j)
            v += sign * self.a[j]
            path.append(tuple(sorted(kept)))
        return path

    def exhaustive(self, k):
        best = float("inf")
        answer = ()
        # Keeping the first k-1 contributions in a contiguous temporary avoids
        # repeatedly copying full status matrices for each candidate subset.
        for prefix in combinations(range(len(self.a)), k - 1):
            start = prefix[-1] + 1 if prefix else 0
            v = self.a[list(prefix)].sum(axis=0) if prefix else np.zeros(self.size)
            g = float(self.hit[list(prefix)].sum()) if prefix else 0
            for c in range(start, len(self.a)):
                loss = float(np.log1p(v + self.a[c]).sum() - g - self.hit[c])
                if loss < best:
                    best, answer = loss, (*prefix, c)
        assert abs(best - self.cost(answer)) < 1e-8
        return answer, best


def selection(arrays):
    old = json.loads(
        Path(__file__).with_name("transformer_directions_result.json").read_text()
    )
    name = old["selected"]
    kind, rate, ids, (gamma,) = decode(bytes.fromhex(old["models"][name]["packet_hex"]))
    assert kind == "diagonal" and rate == RATE and np.array_equal(ids, arrays["ids"])
    q = arrays["mass"][: FIT + VAL]
    y = arrays["target"][: FIT + VAL]
    rows = {}
    checks = {}
    with Native() as lib:
        for packed in (False, True):
            z = lib.histories(q, y, packed) * gamma
            train = Score(q[:FIT], y[:FIT], z[:FIT])
            val = Score(q[FIT:], y[FIT:], z[FIT:])
            order = {}
            for path in (train.nested(True), train.nested(False)):
                for subset in path:
                    order[subset] = True
            stats = []
            for k in (1, 2, 3):
                sub, cost = train.exhaustive(k)
                best_nested = min(train.cost(s) for s in order if len(s) == k)
                stats.append(
                    {
                        "size": k,
                        "indices": list(sub),
                        "exact_nats": cost,
                        "best_nested_extra": best_nested - cost,
                    }
                )
                order[sub] = True
            checks[str(int(packed))] = stats
            for subset in order:
                word = encode(subset, ids, gamma, packed)
                ix, g, is_q = unpack(word, ids)
                assert list(ix) == list(subset) and np.array_equal(g, gamma[ix])
                carry = len(subset) * (2 if is_q else 8)
                loss = val.cost(subset)
                rows[word.hex()] = {
                    "indices": list(subset),
                    "packed": is_q,
                    "installed_bytes": len(word),
                    "live_bytes": carry,
                    "selection_delta_nats": loss,
                    "training_delta_nats": train.cost(subset),
                }
    selected = {}
    for charge_live in (False, True):

        def key(item, include_live=charge_live):
            word, row = item
            size = row["installed_bytes"] + (row["live_bytes"] if include_live else 0)
            return (row["selection_delta_nats"] + 8 * RENT * size, size, word)

        selected["installed_and_live" if charge_live else "installed"] = {
            str(cap): min(
                ((w, r) for w, r in rows.items() if len(r["indices"]) <= cap), key=key
            )[0]
            for cap in CAPS
        }
    return {
        "registration": REGISTRATION,
        "source_arrays": old["source"]["arrays_sha256"],
        "source_model": name,
        "rate": rate,
        "ids": ids.tolist(),
        "ordinary_fit_positions": FIT,
        "ordinary_selection_positions": VAL,
        "exhaustive": checks,
        "selected": selected,
        "candidates": rows,
    }


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", required=True, type=Path)
    p.add_argument("--write", type=Path)
    p.add_argument("--check", type=Path)
    args = p.parse_args()
    with np.load(args.cache, allow_pickle=False) as arrays, threadpool_limits(limits=1):
        result = selection(arrays)
    if args.check:
        assert compare(result, json.loads(args.check.read_text(encoding="utf8")))
        print("Matched frozen training paths, exhaustive minima and selection packets.")
    elif args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    else:
        print(json.dumps(result, indent=2))
