"""Fit probability-preserving group readouts and serialize their shared history lookups."""

import struct
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from text import VOCAB

MULTIPLIERS = np.array([0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0])
SCALAR = np.log(MULTIPLIERS)
NEUTRAL = 3
MAP_HEADER = struct.Struct("<BBH")
HEAD_HEADER = struct.Struct("<BB4H")
HEADER = struct.Struct("<HBBBBHI")


def nibbles(values):
    data = np.zeros((len(values) + 1) // 2, dtype=np.uint8)
    data[:] = values[::2]
    data[: len(values) // 2] |= values[1::2] << 4
    return data.tobytes()


@dataclass
class Address:
    codes: np.ndarray
    payload: bytes

    @property
    def varying(self):
        return self.payload[0] != 0


def address(codes):
    codes = np.asarray(codes, dtype=np.uint8)
    assert len(codes) == VOCAB and np.max(codes) < 9
    counts = np.bincount(codes, minlength=9)
    default = int(np.argmax(counts))
    changes = np.flatnonzero(codes != default)
    if not len(changes):
        return Address(codes, MAP_HEADER.pack(0, default, 0))
    sparse = (
        MAP_HEADER.pack(1, default, len(changes))
        + changes.astype("<u2").tobytes()
        + nibbles(codes[changes])
    )
    dense = MAP_HEADER.pack(2, 0, 0) + nibbles(codes)
    return Address(codes, min((sparse, dense), key=len))


def frequency_address(counts):
    ids = np.arange(len(counts))
    rank = np.lexsort((ids, -counts))
    cumulative = np.cumsum(counts[rank])
    limits = np.searchsorted(cumulative, (cumulative[-1] * np.arange(1, 9) + 8) // 9)
    cuts = rank[limits]
    codes = np.zeros(len(counts), dtype=np.uint8)
    wire = bytearray(MAP_HEADER.pack(3, 0, 8))
    for t in cuts:
        codes += (counts < counts[t]) | ((counts == counts[t]) & (ids > t))
        wire.extend(struct.pack("<IH", int(counts[t]), int(t)))
    return Address(codes, bytes(wire))


def binary_gains(p, hit):
    return np.stack([hit * np.log(m) - np.log1p((m - 1) * p) for m in MULTIPLIERS])


def assignment_scores(history, gains, prior, beta):
    values = []
    for row in gains - gains[prior]:
        total = np.bincount(history, weights=row, minlength=VOCAB)
        if beta:
            total -= beta * np.sqrt(
                np.bincount(history, weights=row**2, minlength=VOCAB)
            )
        values.append(total)
    return np.stack(values)


def choose_codes(scores, prior, price):
    best = np.argmax(scores, axis=0)
    return np.where(scores[best, np.arange(VOCAB)] > price, best, prior).astype(
        np.uint8
    )


@dataclass
class Group:
    ids: np.ndarray
    position: np.ndarray
    history: np.ndarray
    query: np.ndarray
    label: np.ndarray
    prob: np.ndarray

    @property
    def index(self):
        return np.arange(len(self.label))


@dataclass
class Head:
    kind: int
    parameters: np.ndarray
    odds: np.ndarray

    def gains(self, group, codes):
        states = 0 if self.kind == 0 else codes[group.history]
        r = self.odds[states]
        z = (group.prob * r).sum(axis=1)
        return np.log(
            r[group.label] if self.kind == 0 else r[group.index, group.label]
        ) - np.log(z)

    def packet(self, ids, index):
        return HEAD_HEADER.pack(self.kind, index, *ids) + self.parameters.tobytes()


def fit_head(group, codes, kind, prior=None):
    """Fit exact conditional likelihood aggregated at equal state and current token."""
    k = 1 if kind == 0 else 9
    states = (
        np.zeros(len(group.label), dtype=np.uint8)
        if kind == 0
        else codes[group.history]
    )
    keys = (states.astype(np.int64) << 16) | group.query
    packed, index, counts = np.unique(keys, return_index=True, return_counts=True)
    bucket = packed >> 16
    prob = group.prob[index]
    hit = np.bincount(
        states.astype(np.int64) * 4 + group.label, minlength=4 * k
    ).reshape(k, 4)[:, :3]
    reference = np.zeros(3) if prior is None else np.log(prior.odds[0, :3])
    shape = (2 if kind == 2 else k, 3)
    center = np.tile(reference, (shape[0], 1))
    if kind == 2:
        center[1] = 0

    def objective(x):
        params = x.reshape(shape)
        logits = params if kind != 2 else params[0] + SCALAR[:, None] * params[1]
        mult = np.column_stack((np.exp(logits), np.ones(k)))
        weights = prob * mult[bucket]
        z = weights.sum(axis=1)
        expected = weights[:, :3] * (counts / z)[:, None]
        grad = (
            np.stack(
                [
                    np.bincount(bucket, weights=expected[:, j], minlength=k)
                    for j in range(3)
                ],
                axis=1,
            )
            - hit
        )
        if kind == 2:
            grad = np.stack((grad.sum(axis=0), SCALAR @ grad))
        diff = params - center
        loss = np.sum(counts * np.log(z)) - np.sum(hit * logits) + np.sum(diff**2)
        return float(loss), (grad + 2 * diff).ravel()

    bound = np.log(16)
    result = minimize(
        objective,
        center.ravel(),
        jac=True,
        method="L-BFGS-B",
        bounds=[(-bound, bound)] * center.size,
        options={"ftol": 1e-12, "gtol": 2e-5, "maxiter": 300, "maxls": 80},
    )
    if not result.success:
        raise RuntimeError(f"conditional likelihood fit failed: {result.message}")
    projected = result.jac.copy()
    projected[(result.x == -bound) & (projected > 0)] = 0
    projected[(result.x == bound) & (projected < 0)] = 0
    # The quadratic penalty gives strong convexity two on the fitted box.
    assert float(projected @ projected) / 4 < 0.001
    params = result.x.reshape(shape)
    if kind == 2:
        quant = np.rint(1024 * params).astype("<i2")
        logits = (quant[0].astype(float) + SCALAR[:, None] * quant[1]) / 1024
        values = np.exp(logits)
    else:
        quant = np.rint(1024 * np.exp(params)).astype("<u2")
        values = quant.astype(float) / 1024
    return Head(kind, quant, np.column_stack((values, np.ones(k))))


def initial_codes(group, penalty):
    hit = group.label == 0
    gains = binary_gains(group.prob[:, 0], hit)
    default = int(np.argmax(gains.sum(axis=1)))
    return choose_codes(
        assignment_scores(group.history, gains, default, 0), default, penalty
    )


def alternate(groups, initial, global_heads, kind, penalty):
    codes = initial
    for _ in range(6):
        score = np.zeros((9, VOCAB))
        for g, p in zip(groups, global_heads, strict=True):
            h = fit_head(g, codes, kind, p)
            for z, r in enumerate(h.odds):
                gain = np.log(r[g.label]) - np.log((g.prob * r).sum(axis=1))
                score[z] += np.bincount(g.history, weights=gain, minlength=VOCAB)
        codes = choose_codes(score - score[NEUTRAL], NEUTRAL, penalty)
    a = address(codes)
    return a, tuple(
        fit_head(g, codes, kind, p) for g, p in zip(groups, global_heads, strict=True)
    )


@dataclass
class RawRows:
    tau: int
    keys: np.ndarray
    counts: np.ndarray

    def packet(self):
        result = bytearray()
        for key, row in zip(self.keys.tolist(), self.counts.tolist(), strict=True):
            result.extend(
                struct.pack("<BHH4H", key >> 32, (key >> 16) & 65535, key & 65535, *row)
            )
        return bytes(result)

    def gain(self, g, which, head):
        if not len(self.keys):
            return np.zeros(len(g.label))
        query = (which << 32) | (g.history.astype(np.int64) << 16) | g.query
        i = np.minimum(np.searchsorted(self.keys, query), len(self.keys) - 1)
        retained = self.keys[i] == query
        counts = self.counts[i]
        probs = g.prob * head.odds[0]
        observed = probs[g.index, g.label] / probs.sum(axis=1)
        change = np.log(
            (counts[g.index, g.label] / observed + self.tau)
            / (counts.sum(axis=1) + self.tau)
        )
        return np.where(retained, change, 0.0)


@dataclass
class Model:
    maps: tuple
    heads: tuple
    raw: RawRows | None = None

    def target_gains(self, groups):
        values = []
        for i, (g, a, h) in enumerate(zip(groups, self.maps, self.heads, strict=True)):
            gain = h.gains(g, None if a is None else a.codes)
            if self.raw is not None:
                gain += self.raw.gain(g, i, h)
            values.append(gain)
        return values

    def install(self, base, group_ids, source=None):
        entries = []
        for a in (source, *self.maps):
            if a is not None and all(old.payload != a.payload for old in entries):
                entries.append(a)
        by_payload = {a.payload: i for i, a in enumerate(entries)}
        row_count = len(self.raw.keys) if self.raw is not None else 0
        source_id = 286 if source is not None else 65535
        src = by_payload[source.payload] if source is not None else 255
        header = HEADER.pack(
            source_id,
            len(entries),
            len(self.heads),
            src,
            self.raw.tau if row_count else 0,
            0,
            row_count,
        )
        chunks = [base, header, *(a.payload for a in entries)]
        for ids, a, h in zip(group_ids, self.maps, self.heads, strict=True):
            chunks.append(
                h.packet(ids, by_payload[a.payload] if a is not None else 255)
            )
        if row_count:
            chunks.append(self.raw.packet())
        n = sum(a.varying for a in entries)
        live = 2 if row_count or n > 2 else (n + 1) // 2
        return b"".join(chunks), live

    def size(self, base, ids, source=None):
        payload, live = self.install(base, ids, source)
        return len(payload) + live
