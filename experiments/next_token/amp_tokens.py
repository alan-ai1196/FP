"""Passive retained-unit half/single token schedule, with integer grid masters.

CPU NumPy is an audit executor; CUDA uses actual Torch device operations.
No native reference endpoint or gradient enters a device successor. These
helpers supply no Runtime/data/resource/bridge/installation authority.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import math
import numpy as np

import batched_tokens as reference
import native_readout as readout
from causal_tokens import TokenWindow
from enclosed_tokens import EnclosureUnresolved
from fp_reference.binary_arithmetic import BinaryFormat, round_binary

SCHEDULE = 'token-half-core-single-balanced-gradient-integer-grid-v1'
SINGLE = BinaryFormat(24, -126, 127)


class Arithmetic:
    def __init__(self, *, cuda=False, audit=None):
        self.cuda, self.audit, self.operations = cuda, audit, 0
        if cuda:
            import torch
            if not torch.cuda.is_available():
                raise EnclosureUnresolved('actual CUDA required; no CPU fallback')
            self.xp = torch
        else:
            self.xp = np

    def array(self, value, dtype):
        if self.cuda:
            return self.xp.tensor(np.asarray(value).copy(), dtype=getattr(self.xp, dtype), device='cuda:0')
        return np.array(value, dtype=getattr(np, dtype), copy=True)

    def raw(self, value):
        return value.detach().cpu().numpy().copy() if self.cuda else np.asarray(value).copy()

    def index(self, value):
        return self.array(value, 'int64')

    def zeros(self, shape, dtype='float32'):
        return self.xp.zeros(shape, dtype=getattr(self.xp, dtype), **({'device': 'cuda:0'} if self.cuda else {}))

    def copy(self, value):
        return value.clone() if self.cuda else value.copy()

    def transpose(self, value, axes=None):
        axes = tuple(reversed(range(value.ndim))) if axes is None else axes
        return value.permute(*axes) if self.cuda else value.transpose(axes)

    def cat(self, values):
        return self.xp.cat(values, dim=0) if self.cuda else np.concatenate(values, axis=0)

    def keep(self, tag, value, *operands):
        # Check each actual primitive before any projection could hide a bad
        # result. This synchronous audit executor is not a throughput claim.
        if not bool(self.xp.isfinite(value).all()):
            raise EnclosureUnresolved('nonfinite physical primitive: '+tag)
        self.operations += 1
        if self.audit is not None:
            self.audit(tag, self.raw(value), *(self.raw(v) for v in operands))
        return value

    def cast(self, value, dtype):
        result = value.to(getattr(self.xp, dtype)) if self.cuda else value.astype(dtype)
        return self.keep('cast', result, value)

    def add(self, a, b):
        return self.keep('add', a+b, a, b)

    def sub(self, a, b):
        return self.keep('sub', a-b, a, b)

    def mul(self, a, b):
        return self.keep('mul', a*b, a, b)

    def div(self, a, b):
        return self.keep('div', a/b, a, b)

    def constant(self, value):
        rounded = round_binary(F(value), SINGLE, bit_limit=4096)
        return self.array(float(rounded.value), 'float32')

    def scaled_master(self, q, p):
        return self.mul(self.cast(q, 'float32'), self.constant(F(1, 1 << p)))

    def reduce(self, values):
        if not len(values):
            return self.zeros(tuple(values.shape[1:]))
        while len(values) > 1:
            pairs = len(values)//2
            following = self.add(values[:2*pairs:2], values[1:2*pairs:2])
            values = self.cat((following, values[-1:])) if len(values) % 2 else following
        return values[0]

    def segments(self, keys, values):
        keys = np.asarray(keys, dtype=np.int64)
        order = np.argsort(keys, kind='stable')
        keys, values = keys[order], values[self.index(order)]
        while np.any(keys[1:] == keys[:-1]):
            index = np.arange(len(keys), dtype=np.int64)
            start = np.r_[True, keys[1:] != keys[:-1]]
            within = index-np.maximum.accumulate(np.where(start, index, 0))
            take = index[within % 2 == 0]
            paired = (take+1 < len(keys)) & (keys[np.minimum(take+1, len(keys)-1)] == keys[take])
            result = self.copy(values[self.index(take)])
            result[self.index(np.flatnonzero(paired))] = self.add(values[self.index(take[paired])], values[self.index(take[paired]+1)])
            keys, values = keys[take], result
        return keys, values

    def project(self, q, gradient, scale):
        step = self.mul(gradient, scale)
        # q-ceil(step) is exactly floor(q-step) for an integer q. Do not
        # subtract in floating master coordinates before taking the floor.
        if bool((abs(step) >= 1 << 62).any()):
            raise EnclosureUnresolved('integer shift envelope exhausted')
        shift = self.keep('ceil', self.xp.ceil(step), step)
        shift = shift.to(self.xp.int64) if self.cuda else shift.astype(np.int64)
        result = q-shift
        result = result.clamp(min=0) if self.cuda else np.maximum(result, 0)
        if bool((result > reference.WORD_MAX).any()):
            raise EnclosureUnresolved('physical uint32 master envelope exhausted')
        return result


@dataclass(frozen=True)
class State:
    definition: object
    E: object
    C: object
    W: object
    cursor: int
    optimizer_steps: int
    source: TokenWindow

    @classmethod
    def initialize(cls, origin, arithmetic):
        if type(origin) is not reference.Origin or origin.cursor or origin.optimizer_steps:
            raise ValueError('physical initialization requires the declared birth origin')
        return cls(origin.definition, arithmetic.array(origin.E, 'int64'), arithmetic.array(origin.C, 'int64'),
            arithmetic.array(origin.W, 'int64'), 0, 0, origin.source)

    def read(self, arithmetic):
        """Passive complete endpoint reader; never fed back as a successor."""
        return reference.Origin(self.definition, reference.words(arithmetic.raw(self.E)),
            reference.words(arithmetic.raw(self.C)), reference.words(arithmetic.raw(self.W)),
            self.cursor, self.optimizer_steps, self.source)


@dataclass(frozen=True)
class Pending:
    origin: State
    windows: tuple
    targets: tuple
    values: object
    normalizer: object
    target_mass: object
    embedding_ids: np.ndarray
    embedding: object
    core: object
    common: object
    correction_ids: np.ndarray
    corrections: object

    @property
    def unit_count(self):
        return len(self.targets)

    @property
    def cursor(self):
        return self.origin.cursor+self.unit_count

    @property
    def source(self):
        return self.windows[-1].append(self.targets[-1])

    def commit(self, arithmetic):
        a, old, d = arithmetic, self.origin, self.origin.definition
        if self.unit_count != d.output.update_unit:
            raise ValueError('only the complete registered physical update unit can commit')
        try:
            scale = a.constant(d.output.grid*d.output.learning_rate/d.output.update_unit)
            E = a.copy(old.E)
            indices = a.index(self.embedding_ids)
            E[indices] = a.project(old.E[indices], self.embedding, scale)
            C = a.project(old.C, self.core, scale)
            W = a.project(old.W, self.common, scale)
            ids = a.index(self.correction_ids)
            W[ids] = a.project(old.W[ids], a.sub(self.common, self.corrections), scale)
            return State(d, E, C, W, old.cursor+len(self.targets), old.optimizer_steps+1,
                self.windows[-1].append(self.targets[-1]))
        except EnclosureUnresolved as error:
            error.retained_unit = self
            raise


@dataclass(frozen=True)
class Prediction:
    predecessor: object
    window: TokenWindow
    values: object
    normalizer: object

    @property
    def origin(self):
        return self.predecessor.origin if type(self.predecessor) is Pending else self.predecessor

    @property
    def windows(self):
        return (self.window,)


class Kernel:
    def __init__(self, definition, arithmetic, *, element_cap):
        # Reuse only the registered native geometry and shape preflight. No
        # reference prediction, gradient or endpoint enters this schedule.
        geometry = reference.Kernel(definition, element_cap=element_cap)
        self.definition, self.levels, self.a = definition, geometry.levels, arithmetic
        self.element_cap = element_cap
        cache = {v: float(round_binary(v, SINGLE, bit_limit=4096).value) for v in set(definition.output.base)}
        self.base = arithmetic.array([cache[v] for v in definition.output.base], 'float32')
        self.base_total = arithmetic.constant(sum(definition.output.base, F(0)))

    def mass_block(self, pending, first, stop):
        """Actual complete-label readout slice of the retained prediction.

        This read-only physical decoder costs operations/storage of its own;
        a caller cannot treat it as an owned or already-issued prediction.
        """
        d, a = self.definition, self.a
        readout.natural(first)
        readout.natural(stop, positive=True)
        if type(pending) not in (Pending, Prediction) or pending.origin.definition != d or not first < stop <= d.output.labels:
            raise ValueError('matching retained prediction and declared label block required')
        reference.size_check((d.output.features, stop-first, len(pending.windows)), self.element_cap)
        weights = a.transpose(a.scaled_master(pending.origin.W[first:stop], d.output.grid_bits))
        features = a.cast(pending.values[a.index(d.features)], 'float32')
        excess = a.reduce(a.mul(weights[:, :, None], features[:, None, :]))
        masses = a.add(self.base[first:stop, None], excess)
        probabilities = a.div(masses, pending.normalizer[None, :])
        if bool((masses <= 0).any()) or bool((probabilities <= 0).any()) or bool((probabilities > 1).any()):
            raise EnclosureUnresolved('complete physical readout lost positive finite probability range')
        return excess, masses, probabilities

    def unit(self, origin, windows, targets):
        if type(targets) is not tuple or len(targets) != self.definition.output.update_unit:
            raise ValueError('one complete retained source/target update unit required')
        return self.prefix(origin, windows, targets)

    def _require_origin(self, origin):
        d, a = self.definition, self.a
        if type(origin) is not State or origin.definition != d or origin.cursor % d.output.update_unit:
            raise ValueError('complete committed physical origin required')
        readout.natural(origin.cursor)
        readout.natural(origin.optimizer_steps)
        if type(origin.source) is not TokenWindow or origin.source.schema != d.sources:
            raise ValueError('physical default source context is incomplete')
        origin.source.__post_init__()
        for value, shape in ((origin.E, (d.sources.vocabulary+1, d.width)), (origin.C, (d.slots,)),
                             (origin.W, (d.output.labels, d.output.features))):
            if tuple(value.shape) != shape or value.dtype != a.xp.int64:
                raise ValueError('complete physical integer master block required')
            if a.cuda and (not value.is_cuda or value.device.index != 0 or value.requires_grad):
                raise ValueError('actual same-device manual-gradient state required')
            if bool((value < 0).any()) or bool((value > reference.WORD_MAX).any()):
                raise ValueError('physical master outside the registered word range')

    def prefix(self, origin, windows, targets):
        """Recompute the declared reduction for only the revealed prefix."""
        self._require_origin(origin)
        d = self.definition
        if type(windows) is not tuple or type(targets) is not tuple or len(windows) != len(targets) or not 1 <= len(targets) <= d.output.update_unit:
            raise ValueError('matching revealed nonempty prefix within the registered unit required')
        for window, target in zip(windows, targets):
            if type(window) is not TokenWindow or window.schema != d.sources:
                raise ValueError('actual matching retained source points required')
            window.__post_init__()
            readout.natural(target)
            if target >= d.output.labels:
                raise ValueError('undeclared target')
        try:
            return self._unit(origin, windows, targets)
        except EnclosureUnresolved as error:
            # Complete actual AMP origin and records, not an exact native
            # decoder or fabricated pre-failure gradients.
            error.retained_unit = (origin, windows, targets)
            raise

    def predict(self, predecessor, window=None):
        if type(predecessor) not in (State, Pending):
            raise ValueError('complete committed or pending physical predecessor required')
        origin = predecessor.origin if type(predecessor) is Pending else predecessor
        self._require_origin(origin)
        if type(predecessor) is Pending and predecessor.unit_count >= self.definition.output.update_unit:
            raise ValueError('physical learner must commit its full unit before another prediction')
        window = predecessor.source if window is None else window
        if type(window) is not TokenWindow or window.schema != self.definition.sources:
            raise ValueError('complete matching source point required')
        window.__post_init__()
        values, features, totals, _, _, _ = self._forward(origin, (window,))
        normalizer = self.a.add(self.base_total, self.a.reduce(self.a.mul(totals[:, None], features)))
        if bool((normalizer <= 0).any()):
            raise EnclosureUnresolved('physical prediction normalizer lost positivity')
        return Prediction(predecessor, window, values, normalizer)

    def observe(self, predecessor, prediction, target, *, window=None):
        if type(prediction) is not Prediction or prediction.predecessor is not predecessor:
            raise ValueError('prediction must belong to the complete current physical predecessor')
        origin = predecessor.origin if type(predecessor) is Pending else predecessor
        windows = predecessor.windows if type(predecessor) is Pending else ()
        targets = predecessor.targets if type(predecessor) is Pending else ()
        actual_window = predecessor.source if window is None else window
        try:
            expected = self.predict(predecessor, actual_window)
        except EnclosureUnresolved as error:
            error.retained_unit = (origin, windows+(actual_window,), targets+(target,))
            raise
        if prediction.window != expected.window or any(
                getattr(prediction, field).dtype != getattr(expected, field).dtype
                or getattr(prediction, field).shape != getattr(expected, field).shape
                or self.a.raw(getattr(prediction, field)).tobytes() != self.a.raw(getattr(expected, field)).tobytes()
                for field in ('values', 'normalizer')):
            raise ValueError('prediction differs from its actual source point or physical cache')
        return self.prefix(origin, windows+(expected.window,), targets+(target,))

    def _forward(self, origin, windows):
        d, a = self.definition, self.a
        N, L, D = len(windows), d.sources.context, d.width
        count = d.input_nodes+len(d.nodes)
        history = np.asarray([w.past for w in windows])
        theta = a.cast(a.scaled_master(origin.C, d.output.grid_bits), 'float16')
        values = a.zeros((count, N), 'float16')
        embedded = a.cast(a.scaled_master(origin.E[a.index(history)], d.output.grid_bits), 'float16')
        values[:d.input_nodes] = a.transpose(embedded, (1, 2, 0)).reshape(d.input_nodes, N)
        for sums, products in self.levels:
            if len(sums):
                terms = a.cast(a.mul(theta[a.index(sums[:, 2]), None], values[a.index(sums[:, 1])]), 'float32')
                ids, combined = a.segments(sums[:, 0], terms)
                values[a.index(ids)] = a.cast(combined, 'float16')
            if len(products):
                values[a.index(products[:, 0])] = a.mul(values[a.index(products[:, 1])], values[a.index(products[:, 2])])
        stored = a.cast(values, 'float32')
        features = stored[a.index(d.features)]
        integer_totals = origin.W.sum(dim=0) if a.cuda else origin.W.sum(axis=0, dtype=np.int64)
        totals = a.scaled_master(integer_totals, d.output.grid_bits)
        return values, features, totals, theta, stored, history

    def _unit(self, origin, windows, targets):
        d, a = self.definition, self.a
        N, L, D = len(targets), d.sources.context, d.width
        count = d.input_nodes+len(d.nodes)
        labels = np.asarray(targets)
        values, features, totals, theta, stored, history = self._forward(origin, windows)
        selected = a.transpose(a.scaled_master(origin.W[a.index(labels)], d.output.grid_bits))
        normalizer = a.add(self.base_total, a.reduce(a.mul(totals[:, None], features)))
        mass = a.add(self.base[a.index(labels)], a.reduce(a.mul(selected, features)))
        if bool((normalizer <= 0).any()) or bool((mass <= 0).any()):
            raise EnclosureUnresolved('physical mass or normalizer lost positivity')
        common = a.reduce(a.transpose(a.div(features, normalizer)))
        correction_ids, corrections = a.segments(labels, a.transpose(a.div(features, mass)))
        seeds = a.sub(a.div(totals[:, None], normalizer), a.div(selected, mass))
        adjoints = a.zeros((count, N))
        ids, combined = a.segments(d.features, seeds)
        adjoints[a.index(ids)] = combined
        gradient = a.zeros((d.slots,))
        stored_theta = a.cast(theta, 'float32')
        for sums, products in reversed(self.levels):
            if len(sums):
                gradients = a.reduce(a.transpose(a.mul(adjoints[a.index(sums[:, 0])], stored[a.index(sums[:, 1])])))
                ids, combined = a.segments(sums[:, 2], gradients)
                idx = a.index(ids)
                gradient[idx] = a.add(gradient[idx], combined)
                credits = a.mul(adjoints[a.index(sums[:, 0])], stored_theta[a.index(sums[:, 2]), None])
                ids, combined = a.segments(sums[:, 1], credits)
                idx = a.index(ids)
                adjoints[idx] = a.add(adjoints[idx], combined)
            if len(products):
                left = a.mul(adjoints[a.index(products[:, 0])], stored[a.index(products[:, 2])])
                right = a.mul(adjoints[a.index(products[:, 0])], stored[a.index(products[:, 1])])
                ids, combined = a.segments(np.r_[products[:, 1], products[:, 2]], a.cat((left, right)))
                idx = a.index(ids)
                adjoints[idx] = a.add(adjoints[idx], combined)
        rows = a.transpose(adjoints[:d.input_nodes].reshape(L, D, N), (0, 2, 1)).reshape(L*N, D)
        embedding_ids, embedding = a.segments(history.T.reshape(-1), rows)
        return Pending(origin, windows, targets, values, normalizer, mass, embedding_ids, embedding,
            gradient, common, correction_ids, corrections)
