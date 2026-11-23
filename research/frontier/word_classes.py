"""Sparse full-vocabulary normalization and fitting for learned history and output sets."""

import struct
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.sparse import csr_matrix
from text import VOCAB
from text_addresses import CAL, RENT, TOTAL_MASS, serialize

UNIT = 1024
CAP = 4096
HEADER = struct.Struct("<BBHHHq")
EMPTY = np.empty(0, dtype=np.uint16)


class ProbabilityRows:
    def __init__(self, fitted):
        c = fitted.common
        self.common = c
        self.tables = fitted.constant
        self.base = serialize(c, self.tables)
        mass = self.tables[0]
        self.back_den = TOTAL_MASS * c.tail
        scale = np.where(c.category == len(c.top), c.unigram, c.tail)
        self.back_num = mass[c.category].astype(np.int64) * scale
        assert self.back_num.sum() == self.back_den
        self.back = self.back_num / self.back_den
        self.den = c.outgoing + 64.0
        self.count = csr_matrix(
            (c.values.astype(float), (c.keys >> 16, c.keys & 65535)),
            shape=(VOCAB, VOCAB),
        )
        self.transpose = self.count.T.tocsr()

    def apply(self, weights):
        return (self.count @ weights + 64 * (self.back @ weights)) / self.den

    def adjoint(self, query_weights):
        a = query_weights / self.den
        return self.transpose @ a + 64 * a.sum() * self.back


def vector(ids, values=1.0):
    v = np.zeros(VOCAB)
    v[ids] = values
    return v


def choose(score, k, price=0.0):
    ids = np.flatnonzero(score > price)
    if len(ids) > k:
        ids = ids[np.lexsort((ids, -score[ids]))[:k]]
    return np.sort(ids).astype(np.uint16)


def top_residual(residual, k):
    return choose(np.abs(residual), k)


@dataclass
class Gate:
    types: np.ndarray | None
    outputs: np.ndarray
    units: np.ndarray
    current: bool = False

    def weights(self):
        if not len(self.outputs):
            return np.zeros(VOCAB)
        return vector(self.outputs, self.units.astype(float) / UNIT - 1.0)

    def live(self):
        return int(
            bool(len(self.outputs)) and self.types is not None and not self.current
        )

    def install(self, rows):
        if not len(self.outputs):
            return rows.base
        types = EMPTY if self.types is None else self.types
        shared = len(self.units) == 1
        flags = int(self.types is None) + 2 * int(self.current)
        offsets = self.units.astype(np.int64) - UNIT
        back = sum(
            int(rows.back_num[j]) * int(v)
            for j, v in zip(
                self.outputs, np.broadcast_to(offsets, len(self.outputs)), strict=True
            )
        )
        fixed = int(self.units[0]) if shared else 0
        wire = HEADER.pack(
            1 if shared else 2, flags, len(types), len(self.outputs), fixed, back
        )
        if shared:
            output = self.outputs.astype("<u2").tobytes()
        else:
            output = np.column_stack((self.outputs, self.units)).astype("<u2").tobytes()
        return rows.base + wire + types.astype("<u2").tobytes() + output

    def size(self, rows):
        return len(self.install(rows)) + self.live()

    def masks(self, obs):
        active = (
            np.ones(len(obs.target), dtype=bool)
            if self.types is None
            else vector(self.types)[obs.query if self.current else obs.history].astype(
                bool
            )
        )
        return active, vector(self.outputs)[obs.target].astype(bool)

    def gain(self, rows, obs):
        w = self.weights()
        active, _ = self.masks(obs)
        return active * (np.log1p(w[obs.target]) - np.log1p(rows.apply(w)[obs.query]))

    def signature(self):
        return (
            None if self.types is None else self.types.tobytes(),
            self.outputs.tobytes(),
            self.units.tobytes(),
            self.current,
        )


def empty_gate():
    return Gate(None, EMPTY, EMPTY)


@dataclass
class Active:
    q: np.ndarray
    y: np.ndarray


class FitData:
    def __init__(self, rows, obs, current=False):
        self.rows, self.obs, self.current = rows, obs, current
        self.u = obs.query if current else obs.history
        self.price = 16 * RENT * len(obs.target) / CAL
        self.all = Active(
            np.bincount(obs.query, minlength=VOCAB),
            np.bincount(obs.target, minlength=VOCAB),
        )

    def active(self, types):
        if types is None:
            return self.all
        keep = np.zeros(VOCAB, dtype=bool)
        keep[types] = True
        mask = keep[self.u]
        return Active(
            np.bincount(self.obs.query[mask], minlength=VOCAB),
            np.bincount(self.obs.target[mask], minlength=VOCAB),
        )

    def fit_gate(self, w, k):
        u = np.bincount(
            self.u,
            weights=np.log1p(w[self.obs.target])
            - np.log1p(self.rows.apply(w)[self.obs.query]),
            minlength=VOCAB,
        )
        return choose(u, k, self.price)

    def linearized(self, active, ids, rho):
        theta = np.log(rho)
        mass = self.rows.apply(vector(ids))
        return theta * active.y - self.rows.adjoint(
            active.q * (rho - 1) / (1 + (rho - 1) * mass)
        )

    def gain(self, active, w):
        return active.y @ np.log1p(w) - active.q @ np.log1p(self.rows.apply(w))

    def fit_sets(self, seed, ka, kb, rho, global_gate):
        ids = seed
        best = empty_gate()
        previous = -np.inf
        trace = []
        for _ in range(12):
            w = vector(ids, rho - 1)
            types = None if global_gate else self.fit_gate(w, ka)
            a = self.active(types)
            tangent = self.linearized(a, ids, rho)
            proposal = choose(tangent, kb, self.price)
            if (tangent[proposal] - self.price).sum() > (
                tangent[ids] - self.price
            ).sum() + 1e-10:
                ids = proposal
                w = vector(ids, rho - 1)
            objective = self.gain(a, w) - self.price * (
                len(ids) + (0 if types is None else len(types))
            )
            assert objective + 1e-8 >= previous
            trace.append(float(objective))
            if objective <= previous + 1e-9:
                break
            best = Gate(
                types, ids, np.array([round(rho * UNIT)], dtype=np.uint16), self.current
            )
            previous = objective
        if len(best.outputs) == 0 or (best.types is not None and not len(best.types)):
            return empty_gate(), 0.0, trace
        return best, previous, trace


def fit_free_head(data, active, ids):
    if not len(ids):
        return EMPTY
    rows = data.rows
    keep = np.flatnonzero(active.q)
    if not len(keep):
        return np.full(len(ids), UNIT, dtype=np.uint16)
    sub = rows.count[keep][:, ids].tocsr()
    prior = rows.back[ids]
    count = active.q[keep]
    den = rows.den[keep]
    y = active.y[ids]

    def objective(logits):
        odds = np.exp(logits)
        residual = odds - 1
        z = 1 + (sub @ residual + 64 * (prior @ residual)) / den
        u = count / (den * z)
        expected = odds * (sub.T @ u + 64 * u.sum() * prior)
        return float(
            count @ np.log(z) - y @ logits + logits @ logits
        ), expected - y + 2 * logits

    bound = np.log(4.0)
    fit = minimize(
        objective,
        np.zeros(len(ids)),
        method="L-BFGS-B",
        jac=True,
        bounds=[(-bound, bound)] * len(ids),
        options={"maxiter": 350, "ftol": 1e-13, "gtol": 1e-5, "maxls": 80},
    )
    if not fit.success:
        raise RuntimeError(fit.message)
    gradient = fit.jac.copy()
    gradient[(fit.x == -bound) & (gradient > 0)] = 0
    gradient[(fit.x == bound) & (gradient < 0)] = 0
    assert gradient @ gradient / 4 < 0.01
    return np.rint(np.exp(fit.x) * UNIT).astype(np.uint16)


def free_candidates(data, start, ka, cap_outputs):
    types = start
    for _ in range(4):
        if types is not None and len(types) == 0:
            return
        a = data.active(types)
        ids = top_residual(a.y - data.rows.adjoint(a.q), cap_outputs)
        units = fit_free_head(data, a, ids)
        keep = units != UNIT
        ids, units = ids[keep], units[keep]
        if not len(ids):
            return
        w = vector(ids, units.astype(float) / UNIT - 1)
        gate = data.fit_gate(w, ka)
        if not len(gate):
            return
        yield Gate(gate, ids, units)
        if np.array_equal(gate, types):
            return
        types = gate
