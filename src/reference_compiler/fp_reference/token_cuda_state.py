"""Complete immutable token CUDA phase data; no public execution authority.

Each origin is encoded once per state. Leaves refer to it by the enclosing
state, rather than serializing another full model for every observed event.
Prepared operands, all leaf words, all forest blocks and current basis stay.
"""
from dataclasses import dataclass
import math
import numpy as np

from .core import ContractError
from .token_execution import closed, definition_check
from .token_causal import TokenWindow
from . import token_amp as amp, token_batch as ref, token_streaming as stream
from .token_array_events import Prepared, Forecast


@dataclass(frozen=True)
class ArrayWords:
    shape: tuple[int, ...]
    dtype: str
    data: bytes

    @classmethod
    def capture(cls, value, arithmetic):
        raw = arithmetic.raw(value)
        return cls(tuple(raw.shape), str(raw.dtype), raw.tobytes())

    def array(self):
        closed(self, ArrayWords)
        if (self.dtype not in ('float16', 'float32', 'int64') or type(self.shape) is not tuple
                or any(type(n) is not int or n < 0 for n in self.shape) or type(self.data) is not bytes
                or len(self.data) != math.prod(self.shape)*np.dtype(self.dtype).itemsize):
            raise ContractError('complete immutable token array words required')
        return np.frombuffer(self.data, dtype=np.dtype(self.dtype)).reshape(self.shape)


@dataclass(frozen=True)
class LeafWords:
    window: object
    target: int
    values: ArrayWords
    normalizer: ArrayWords
    target_mass: ArrayWords
    embedding_ids: tuple[int, ...]
    embedding: ArrayWords
    core: ArrayWords
    common: ArrayWords
    correction_ids: tuple[int, ...]
    corrections: ArrayWords

    @classmethod
    def capture(cls, leaf, a):
        if type(leaf) is not amp.Pending or len(leaf.windows) != 1 or len(leaf.targets) != 1:
            raise ContractError('one complete event workspace required')
        closed(leaf, amp.Pending)
        closed(leaf.windows[0], TokenWindow)
        leaf.windows[0].__post_init__()
        fields = []
        for key in ('values', 'normalizer', 'target_mass', 'embedding_ids', 'embedding', 'core', 'common', 'correction_ids', 'corrections'):
            value = getattr(leaf, key)
            if key.endswith('_ids') and (type(value) is not np.ndarray or value.dtype != np.int64 or value.ndim != 1):
                raise ContractError('complete exact int64 incidence coordinates required')
            fields.append(tuple(map(int, value)) if key.endswith('_ids') else ArrayWords.capture(value, a))
        return cls(leaf.windows[0], leaf.targets[0], *fields)

    def cpu(self, origin):
        return amp.Pending(origin, (self.window,), (self.target,), self.values.array(), self.normalizer.array(),
            self.target_mass.array(), np.asarray(self.embedding_ids, dtype=np.int64), self.embedding.array(),
            self.core.array(), self.common.array(), np.asarray(self.correction_ids, dtype=np.int64), self.corrections.array())


@dataclass(frozen=True)
class ForestWords:
    count: int
    blocks: tuple[tuple[int, ArrayWords], ...]

    @classmethod
    def capture(cls, forest, a):
        if type(forest) is not stream.Forest:
            raise ContractError('complete registered gradient forest required')
        closed(forest, stream.Forest)
        if type(forest.count) is not int or forest.count < 1 or type(forest.blocks) is not tuple:
            raise ContractError('complete nonempty integer carry decomposition required')
        counts = tuple(1 << bit for bit in range(forest.count.bit_length()-1, -1, -1) if forest.count >> bit & 1)
        if tuple(b.count for b in forest.blocks) != counts:
            raise ContractError('gradient carry tree lost its exact interval topology')
        for block in forest.blocks:
            closed(block, stream.Block)
            if type(block.count) is not int:
                raise ContractError('exact integer carry interval required')
        return cls(forest.count, tuple((b.count, ArrayWords.capture(b.value, a)) for b in forest.blocks))

    def cpu(self):
        return stream.Forest(self.count, tuple(stream.Block(n, value.array()) for n, value in self.blocks))


@dataclass(frozen=True)
class StateWords:
    origin: ref.Origin
    prepared: tuple[ArrayWords, ...]
    leaves: tuple[LeafWords, ...]
    core: ForestWords | None
    common: ForestWords | None
    embedding: tuple[tuple[int, ForestWords], ...]
    corrections: tuple[tuple[int, ForestWords], ...]
    basis: tuple[object, ...]

    @property
    def cursor(self):
        return self.origin.cursor+len(self.leaves)

    @property
    def unit_count(self):
        return len(self.leaves)

    @property
    def source(self):
        return self.origin.source if not self.leaves else self.leaves[-1].window.append(self.leaves[-1].target)

    def cpu(self):
        master = amp.State(self.origin.definition, *(getattr(self.origin, key).astype(np.int64) for key in ('E', 'C', 'W')),
            self.origin.cursor, self.origin.optimizer_steps, self.origin.source)
        prepared = Prepared(master, *(x.array() for x in self.prepared))
        if not self.leaves:
            if self.core is not None or self.common is not None or self.embedding or self.corrections or self.basis:
                raise ContractError('committed token state has unexpected pending caches')
            return Resident(master, prepared, None, None)
        pending = stream.Pending(master, tuple(leaf.cpu(master) for leaf in self.leaves), self.core.cpu(), self.common.cpu(),
            tuple((key, value.cpu()) for key, value in self.embedding), tuple((key, value.cpu()) for key, value in self.corrections))
        ids, embedding, core, common, targets, corrections = self.basis
        basis = stream.Basis(np.asarray(ids, dtype=np.int64), embedding.array(), core.array(), common.array(),
                            np.asarray(targets, dtype=np.int64), corrections.array())
        return Resident(pending, prepared, basis, None)

    def diagnostic(self):
        """Old-format coordinates; the enclosing StateWords keeps every cache."""
        value = self.cpu()
        if not self.leaves:
            return value.state
        p, b = value.state, value.basis
        return amp.Pending(p.origin, p.windows, p.targets, np.concatenate([leaf.values for leaf in p.leaves], axis=1),
            np.concatenate([leaf.normalizer for leaf in p.leaves]), np.concatenate([leaf.target_mass for leaf in p.leaves]),
            b.embedding_ids, b.embedding, b.core, b.common, b.correction_ids, b.corrections)


@dataclass(frozen=True)
class PredictionWords:
    window: object
    values: ArrayWords
    normalizer: ArrayWords

    def cpu(self, prepared):
        return Forecast(prepared, self.window, self.values.array(), self.normalizer.array())


@dataclass(frozen=True)
class ReadoutWords:
    label: int
    mass: ArrayWords
    division: ArrayWords


@dataclass(frozen=True)
class Resident:
    state: object
    prepared: Prepared
    basis: stream.Basis | None
    arithmetic: object

    @property
    def origin(self):
        return self.state.origin if type(self.state) is stream.Pending else self.state

    def raw(self, arithmetic=None):
        a = self.arithmetic if arithmetic is None else arithmetic
        if type(self.state) not in (amp.State, stream.Pending) or self.prepared.origin is not self.origin:
            raise ContractError('token resident lost its actual complete prepared origin')
        closed(self, Resident)
        closed(self.state, type(self.state))
        closed(self.origin, amp.State)
        definition_check(self.origin.definition)
        closed(self.prepared, Prepared)
        if type(self.state) is stream.Pending and any(leaf.origin is not self.origin for leaf in self.state.leaves):
            raise ContractError('token event workspace lost its actual shared master origin')
        old = self.origin
        d, masters = old.definition, []
        for key, shape in (('E', (d.sources.vocabulary+1, d.width)), ('C', (d.slots,)), ('W', (d.output.labels, d.output.features))):
            raw = a.raw(getattr(old, key))
            if raw.dtype != np.int64 or raw.shape != shape:
                raise ContractError('physical token master encoding requires complete int64 grid storage')
            masters.append(ref.words(raw))
        origin = ref.Origin(old.definition, *masters, old.cursor, old.optimizer_steps, old.source)
        prepared = tuple(ArrayWords.capture(getattr(self.prepared, key), a) for key in ('theta', 'totals', 'base', 'base_total'))
        if type(self.state) is amp.State:
            if self.basis is not None:
                raise ContractError('committed token resident has an unexpected gradient basis')
            return StateWords(origin, prepared, (), None, None, (), (), ())
        if type(self.basis) is not stream.Basis:
            raise ContractError('pending token resident lost its complete current coordinates')
        p, b = self.state, self.basis
        closed(b, stream.Basis)
        if any(type(ids) is not np.ndarray or ids.dtype != np.int64 or ids.ndim != 1 for ids in (b.embedding_ids, b.correction_ids)):
            raise ContractError('complete typed integer basis incidence required')
        basis = (tuple(map(int, b.embedding_ids)), *(ArrayWords.capture(getattr(b, key), a) for key in ('embedding', 'core', 'common')),
                 tuple(map(int, b.correction_ids)), ArrayWords.capture(b.corrections, a))
        return StateWords(origin, prepared, tuple(LeafWords.capture(leaf, a) for leaf in p.leaves),
            ForestWords.capture(p.core, a), ForestWords.capture(p.common, a),
            tuple((key, ForestWords.capture(value, a)) for key, value in p.embedding),
            tuple((key, ForestWords.capture(value, a)) for key, value in p.corrections), basis)

    def tensors(self):
        rows = [(key, getattr(self.origin, key)) for key in ('E', 'C', 'W')]
        rows += [('prepared:'+key, getattr(self.prepared, key)) for key in ('theta', 'totals', 'base', 'base_total')]
        if type(self.state) is stream.Pending:
            for index, leaf in enumerate(self.state.leaves):
                rows += [(f'leaf:{index}:{key}', getattr(leaf, key)) for key in
                         ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections')]
            forests = (self.state.core, self.state.common)+tuple(f for _, f in self.state.embedding+self.state.corrections)
            rows += [(f'forest:{i}:{j}', b.value) for i, f in enumerate(forests) for j, b in enumerate(f.blocks)]
            rows += [('basis:'+key, getattr(self.basis, key)) for key in ('embedding', 'core', 'common', 'corrections')]
        return tuple(rows)


@dataclass(frozen=True)
class PredictionResident:
    predecessor: Resident
    forecast: Forecast
    arithmetic: object

    def raw(self, arithmetic=None):
        a = self.arithmetic if arithmetic is None else arithmetic
        if self.forecast.prepared is not self.predecessor.prepared:
            raise ContractError('token forecast lost its complete prepared predecessor')
        return PredictionWords(self.forecast.window, ArrayWords.capture(self.forecast.values, a),
                               ArrayWords.capture(self.forecast.normalizer, a))

    def tensors(self):
        return (('values', self.forecast.values), ('normalizer', self.forecast.normalizer))


@dataclass(frozen=True)
class ReadoutResident:
    prediction: PredictionResident
    label: int
    mass: object
    division: object
    arithmetic: object

    def raw(self, arithmetic=None):
        a = self.arithmetic if arithmetic is None else arithmetic
        return ReadoutWords(self.label, ArrayWords.capture(self.mass, a), ArrayWords.capture(self.division, a))

    def tensors(self):
        return (('mass', self.mass), ('division', self.division))
