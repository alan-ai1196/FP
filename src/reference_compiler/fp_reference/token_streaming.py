"""Incremental token AMP with retained binary-carry gradient forests.

This is a NEW physical reduction schedule, not an alias for the lag-major
batched schedule. It preserves the exact native gradient definition while
making its floating association explicit. No Runtime or storage authority.
"""
from dataclasses import dataclass
import numpy as np

from . import token_amp as amp
from .token_enclosures import EnclosureUnresolved

SCHEDULE = 'token-half-core-event-gradient-sparse-balanced-carry-integer-grid-v2'


@dataclass(frozen=True)
class Block:
    count: int
    value: object


@dataclass(frozen=True)
class Forest:
    count: int = 0
    blocks: tuple[Block, ...] = ()

    def append(self, value, arithmetic):
        # A block represents a perfect balanced tree over consecutive leaves.
        # Equal-sized adjacent blocks are the only permissible carry merge.
        if value.dtype != arithmetic.xp.float32:
            raise ValueError('single-precision gradient leaf required')
        blocks = list(self.blocks)
        size = 1
        while blocks and blocks[-1].count == size:
            previous = blocks.pop()
            if previous.value.shape != value.shape:
                raise ValueError('gradient forest changed its complete coordinate shape')
            value = arithmetic.add(previous.value, value)
            size *= 2
        if blocks and (blocks[-1].count <= size or blocks[-1].value.shape != value.shape):
            raise ValueError('gradient forest lost its ordered binary decomposition')
        return Forest(self.count+1, tuple(blocks)+(Block(size, value),))

    def root(self, arithmetic):
        if (not self.blocks or sum(b.count for b in self.blocks) != self.count
                or tuple(b.count for b in self.blocks) != tuple(1 << bit for bit in range(self.count.bit_length()-1, -1, -1) if self.count >> bit & 1)):
            raise ValueError('complete nonempty binary-carry forest required')
        # Odd leaves survive each level of the original balanced reducer.
        # Its ragged right spine is a RIGHT fold, not a left fold.
        value = self.blocks[-1].value
        for block in reversed(self.blocks[:-1]):
            value = arithmetic.add(block.value, value)
        return value


@dataclass(frozen=True)
class Basis:
    embedding_ids: np.ndarray
    embedding: object
    core: object
    common: object
    correction_ids: np.ndarray
    corrections: object


@dataclass(frozen=True)
class Pending:
    origin: amp.State
    # Complete independent event workspaces, in actual reveal order. No old
    # source, target, prediction or per-event derivative is discarded.
    leaves: tuple[amp.Pending, ...]
    core: Forest
    common: Forest
    # The immutable outer tuples are metadata; numeric arrays are never copied
    # or mutated by an append. Missing rows are exact zero contributions.
    embedding: tuple[tuple[int, Forest], ...]
    corrections: tuple[tuple[int, Forest], ...]

    @property
    def unit_count(self):
        return len(self.leaves)

    @property
    def cursor(self):
        return self.origin.cursor+self.unit_count

    @property
    def source(self):
        return self.leaves[-1].source

    @property
    def windows(self):
        return tuple(leaf.windows[0] for leaf in self.leaves)

    @property
    def targets(self):
        return tuple(leaf.targets[0] for leaf in self.leaves)

    def basis(self, arithmetic):
        """Materialize current coordinates, retaining all continuation caches."""
        def rows(entries):
            ids = np.asarray([key for key, _ in entries], dtype=np.int64)
            values = arithmetic.cat(tuple(forest.root(arithmetic)[None, :] for _, forest in entries))
            return ids, values
        ids, embedding = rows(self.embedding)
        targets, corrections = rows(self.corrections)
        return Basis(ids, embedding, self.core.root(arithmetic), self.common.root(arithmetic), targets, corrections)

    def diagnostic_view(self, arithmetic):
        """Explicit caller-allocated old-format coordinate view, not an owner state.

        This does not contain the carry caches and CANNOT replace Pending or
        establish a complete transition relation for the new physical schedule.
        """
        b = self.basis(arithmetic)
        values = arithmetic.transpose(arithmetic.cat(tuple(arithmetic.transpose(leaf.values) for leaf in self.leaves)))
        z = arithmetic.cat(tuple(leaf.normalizer for leaf in self.leaves))
        mass = arithmetic.cat(tuple(leaf.target_mass for leaf in self.leaves))
        return amp.Pending(self.origin, self.windows, self.targets, values, z, mass,
                           b.embedding_ids, b.embedding, b.core, b.common, b.correction_ids, b.corrections)


@dataclass(frozen=True)
class Prediction:
    predecessor: object
    event: amp.Prediction

    @property
    def window(self):
        return self.event.window


class Kernel:
    def __init__(self, definition, arithmetic, *, element_cap):
        self.event_kernel = amp.Kernel(definition, arithmetic, element_cap=element_cap)
        self.a, self.definition = arithmetic, definition
        self.element_cap = element_cap
        # Count semantic per-event derivative evaluations, independent of
        # diagnostic root reads or cache-audit recomputations in another kernel.
        self.event_evaluations = 0

    def _origin(self, predecessor):
        if type(predecessor) not in (amp.State, Pending):
            raise ValueError('complete registered streaming physical predecessor required')
        origin = predecessor.origin if type(predecessor) is Pending else predecessor
        self.event_kernel._require_origin(origin)
        if type(predecessor) is Pending and not 1 <= predecessor.unit_count < self.definition.output.update_unit:
            raise ValueError('complete physical unit must commit before another event')
        return origin

    def predict(self, predecessor, window=None):
        origin = self._origin(predecessor)
        actual_window = predecessor.source if window is None else window
        return Prediction(predecessor, self.event_kernel.predict(origin, actual_window))

    def observe(self, predecessor, prediction, target, *, window=None):
        origin = self._origin(predecessor)
        if type(prediction) is not Prediction or prediction.predecessor is not predecessor:
            raise ValueError('forecast lost its actual complete streaming predecessor')
        actual_window = predecessor.source if window is None else window
        old = predecessor if type(predecessor) is Pending else None
        leaf = None
        try:
            # The old one-event reverse schedule has no cross-event reduction.
            # Its exact real decoder is one native gradient, including all
            # tied slots, repeated features, squares and zero-factor faces.
            leaf = self.event_kernel.observe(origin, prediction.event, target, window=actual_window)
            self.event_evaluations += 1
            def update(entries, ids, values):
                result = dict(entries)
                for index, key in enumerate(ids):
                    key = int(key)
                    result[key] = result.get(key, Forest()).append(values[index], self.a)
                return tuple(sorted(result.items()))
            return Pending(origin, (() if old is None else old.leaves)+(leaf,),
                (Forest() if old is None else old.core).append(leaf.core, self.a),
                (Forest() if old is None else old.common).append(leaf.common, self.a),
                update(() if old is None else old.embedding, leaf.embedding_ids, leaf.embedding),
                update(() if old is None else old.corrections, leaf.correction_ids, leaf.corrections))
        except EnclosureUnresolved as error:
            # Include the previous forests, not just their current rounded sum.
            error.retained_unit = (predecessor, prediction, actual_window, target, leaf)
            raise

    def commit(self, pending):
        a, d = self.a, self.definition
        if type(pending) is not Pending or pending.unit_count != d.output.update_unit or pending.origin.definition != d:
            raise ValueError('one complete registered streaming unit required for commit')
        old = pending.origin
        try:
            b = pending.basis(a)
            scale = a.constant(d.output.grid*d.output.learning_rate/d.output.update_unit)
            E = a.copy(old.E)
            indices = a.index(b.embedding_ids)
            E[indices] = a.project(old.E[indices], b.embedding, scale)
            C = a.project(old.C, b.core, scale)
            W = a.project(old.W, b.common, scale)
            ids = a.index(b.correction_ids)
            W[ids] = a.project(old.W[ids], a.sub(b.common, b.corrections), scale)
            return amp.State(d, E, C, W, pending.cursor, old.optimizer_steps+1, pending.source)
        except EnclosureUnresolved as error:
            error.retained_unit = pending
            raise


def audit_cache(pending, arithmetic, *, element_cap):
    """Independent CPU replay checks EVERY retained leaf and carry block.

    This diagnostic costs a complete replay. An eventual owner can use
    immutable storage plus checked append induction, but cannot replace
    Pending by its current Basis and borrow the old state predicate.
    """
    if type(pending) is not Pending:
        raise ValueError('complete streaming cache required')
    origin, a = pending.origin, amp.Arithmetic()
    if type(origin) is not amp.State:
        raise ValueError('complete physical origin required')
    d = origin.definition
    masters = []
    for key, shape in (('E', (d.sources.vocabulary+1, d.width)), ('C', (d.slots,)), ('W', (d.output.labels, d.output.features))):
        amp.reference.size_check(shape, element_cap)
        raw = arithmetic.raw(getattr(origin, key))
        if raw.dtype != np.int64 or raw.shape != shape or np.any(raw < 0) or np.any(raw > amp.reference.WORD_MAX):
            raise ValueError('stream cache lost a complete uint32-valued integer master block')
        masters.append(a.array(raw, 'int64'))
    copied = amp.State(origin.definition, *masters,
                       origin.cursor, origin.optimizer_steps, origin.source)
    control = Kernel(origin.definition, a, element_cap=element_cap)
    expected = copied
    for window, target in zip(pending.windows, pending.targets):
        expected = control.observe(expected, control.predict(expected, window), target, window=window)
    if (not pending.leaves or pending.unit_count != expected.unit_count or pending.cursor != expected.cursor
            or pending.source != expected.source):
        raise ValueError('stream cache lost complete records or clocks')
    words = 0
    def same(actual, wanted):
        nonlocal words
        raw = arithmetic.raw(actual)
        if raw.dtype != wanted.dtype or raw.shape != wanted.shape or raw.tobytes() != wanted.tobytes():
            raise ValueError('stream cache differs from its complete physical event decoder')
        words += raw.size
    def forest(actual, wanted):
        if type(actual) is not Forest or actual.count != wanted.count or len(actual.blocks) != len(wanted.blocks):
            raise ValueError('stream cache lost its binary-carry topology')
        for left, right in zip(actual.blocks, wanted.blocks):
            if type(left) is not Block or left.count != right.count:
                raise ValueError('stream cache lost a dyadic leaf interval')
            same(left.value, right.value)
    for actual, wanted in zip(pending.leaves, expected.leaves):
        if (actual.origin is not origin or actual.windows != wanted.windows or actual.targets != wanted.targets):
            raise ValueError('stream event lost its complete origin or actual source/target')
        for key in ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections'):
            same(getattr(actual, key), getattr(wanted, key))
        for key in ('embedding_ids', 'correction_ids'):
            ids = getattr(actual, key)
            if type(ids) is not np.ndarray or ids.dtype != np.int64 or not np.array_equal(ids, getattr(wanted, key)):
                raise ValueError('stream event lost a gradient incidence')
    forest(pending.core, expected.core)
    forest(pending.common, expected.common)
    for key in ('embedding', 'corrections'):
        actual, wanted = getattr(pending, key), getattr(expected, key)
        if tuple(k for k, _ in actual) != tuple(k for k, _ in wanted):
            raise ValueError('stream cache lost a persistent gradient row')
        for (_, left), (_, right) in zip(actual, wanted):
            forest(left, right)
    return dict(physical_leaf_and_carry_words=words, complete_cache_replay=True)
