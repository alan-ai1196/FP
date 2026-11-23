"""Sparse exception tables around an already calibrated vocabulary class."""

import struct
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq
from shared_readout import MULTIPLIERS, NEUTRAL, nibbles
from text import VOCAB
from text_addresses import CAL, RENT
from word_classes import CAP, UNIT

BASE = struct.Struct("<HHqBBH")
TABLE = struct.Struct("<BBH")
EARLIER, CURRENT, PAIR = 1, 2, 3


def event_prob(mass, odds):
    return odds * mass / (1 + (odds - 1) * mass)


def best_scalar(mass, hit):
    def derivative(x):
        return float(event_prob(mass, np.exp(x)).sum() - hit.sum())

    bound = np.log(4.0)
    x = (
        -bound
        if derivative(-bound) >= 0
        else bound
        if derivative(bound) <= 0
        else brentq(derivative, -bound, bound)
    )
    return int(np.rint(UNIT * np.exp(x)))


def key_array(obs, kind):
    if kind == PAIR:
        return (obs.history.astype(np.uint32) << 16) | obs.query
    return obs.history if kind == EARLIER else obs.query


@dataclass
class Exceptions:
    kind: int
    keys: np.ndarray
    codes: np.ndarray

    def read(self, obs):
        query = key_array(obs, self.kind)
        if self.kind != PAIR:
            lookup = np.full(VOCAB, NEUTRAL, dtype=np.uint8)
            lookup[self.keys] = self.codes
            return MULTIPLIERS[lookup[query]]
        idx = np.minimum(np.searchsorted(self.keys, query), len(self.keys) - 1)
        return MULTIPLIERS[np.where(self.keys[idx] == query, self.codes[idx], NEUTRAL)]

    def packet(self):
        fmt = "<u4" if self.kind == PAIR else "<u2"
        return (
            TABLE.pack(self.kind, NEUTRAL, len(self.keys))
            + self.keys.astype(fmt).tobytes()
            + nibbles(self.codes)
        )


@dataclass
class Model:
    scalar: int
    tables: tuple

    def live(self):
        kinds = {t.kind for t in self.tables}
        return 2 if PAIR in kinds else int(EARLIER in kinds)

    def odds(self, obs):
        odds = np.full(len(obs.target), self.scalar / UNIT)
        for t in self.tables:
            odds *= t.read(obs)
        return odds

    def gain(self, obs, mass, hit):
        odds = self.odds(obs)
        return hit * np.log(odds) - np.log1p((odds - 1) * mass)

    def pack(self, rows, ids):
        back = int(rows.back_num[ids].sum())
        h = BASE.pack(len(ids), self.scalar, back, len(self.tables), self.live(), 0)
        return (
            rows.base
            + h
            + ids.astype("<u2").tobytes()
            + b"".join(t.packet() for t in self.tables)
        )

    def size(self, rows, ids):
        return len(self.pack(rows, ids)) + self.live()


class Training:
    def __init__(self, obs, mass, hit):
        self.mass, self.hit = mass, hit
        self.index = {}
        for k in (EARLIER, CURRENT, PAIR):
            keys, inverse = np.unique(key_array(obs, k), return_inverse=True)
            self.index[k] = keys, inverse

    def exceptions(self, kind, other, beta, cap):
        keys, index = self.index[kind]
        p = event_prob(self.mass, other)
        n = len(keys)
        best = np.zeros(n)
        codes = np.full(n, NEUTRAL, dtype=np.uint8)
        for z, g in enumerate(MULTIPLIERS):
            if z == NEUTRAL:
                continue
            change = self.hit * np.log(g) - np.log1p((g - 1) * p)
            value = np.bincount(index, weights=change, minlength=n)
            if beta:
                value -= beta * np.sqrt(
                    np.bincount(index, weights=change**2, minlength=n)
                )
            improved = value > best
            codes[improved] = z
            best[improved] = value[improved]
        bits = 36 if kind == PAIR else 20
        price = bits * RENT * len(p) / CAL
        selected = np.flatnonzero(best > price)
        if len(selected) > cap:
            selected = selected[np.lexsort((keys[selected], -best[selected]))[:cap]]
            selected.sort()
        return (
            Exceptions(kind, keys[selected], codes[selected]) if len(selected) else None
        )


def maximum_entries(room, key_bytes):
    # One response nibble per key. The last byte can hold an odd entry alone.
    return max(0, 2 * room // (2 * key_bytes + 1))


def fit_models(rows, ids, obs, val, reference):
    belongs = np.zeros(rows.common.vocab, dtype=bool)
    belongs[ids] = True
    bc = rows.apply(belongs.astype(float))
    train = Training(obs, bc[obs.query], belongs[obs.target])
    test = bc[val.query], belongs[val.target]
    s = best_scalar(train.mass, train.hit)
    empty = Model(s, ())
    initial = empty.size(rows, ids)
    families = {}

    def consider(name, model):
        size = model.size(rows, ids)
        assert size <= CAP
        criterion = -model.gain(val, *test).mean() + 8 * RENT * size / CAL, size
        if name not in families or criterion < families[name][0]:
            families[name] = criterion, model

    for name in ("global", "earlier", "current", "pair", "joint", "twice_current"):
        consider(name, empty)
    consider("previous", Model(reference, ()))
    for k, name in ((EARLIER, "earlier"), (CURRENT, "current"), (PAIR, "pair")):
        live = 0 if k == CURRENT else (2 if k == PAIR else 1)
        n = maximum_entries(CAP - initial - TABLE.size - live, 4 if k == PAIR else 2)
        for beta in (0, 1, 2):
            for cap in (n // 2, n):
                t = train.exceptions(k, s / UNIT, beta, cap)
                if t is None:
                    continue
                m = Model(s, (t,))
                consider(name, m)
                if k in (EARLIER, CURRENT):
                    consider("joint", m)
                if k == CURRENT:
                    consider("twice_current", m)

    for kinds, family in (
        ((CURRENT, EARLIER), "joint"),
        ((CURRENT, CURRENT), "twice_current"),
    ):
        live = int(EARLIER in kinds)
        room = CAP - initial - 2 * TABLE.size - live
        slots = maximum_entries(room, 2)
        for fraction in (0.25, 0.5, 0.75):
            capacities = [int(slots * fraction), slots - int(slots * fraction)]
            while sum(2 * n + (n + 1) // 2 for n in capacities) > room:
                capacities[1] -= 1
            for order in ((0, 1), (1, 0)):
                for beta in (0, 1, 2):
                    factors = [None, None]
                    for _ in range(4):
                        for i in order:
                            other = factors[1 - i]
                            multiplier = (s / UNIT) * (
                                1 if other is None else other.read(obs)
                            )
                            factors[i] = train.exceptions(
                                kinds[i], multiplier, beta, capacities[i]
                            )
                    consider(
                        family, Model(s, tuple(t for t in factors if t is not None))
                    )
    return bc, belongs, {name: c[1] for name, c in families.items()}
