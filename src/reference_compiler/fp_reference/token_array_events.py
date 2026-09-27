"""The token single-event half/single schedule using explicit array outputs.

CUDAArrays supplies admitted immutable arena extents. This numerical kernel
does not own Runtime ingress, lineages, bridge or installation authority.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import numpy as np

from .core import ContractError
from .semantics import ArithmeticUnresolved
from .token_execution import definition_check
from .token_causal import TokenWindow
from .token_arrays import CPUArrays, CudaArrays
from . import token_amp as amp
from . import token_batch as reference
from . import token_streaming as streaming


@dataclass(frozen=True)
class Prepared:
    origin: amp.State
    theta: object
    totals: object
    base: object
    base_total: object


@dataclass(frozen=True)
class Forecast:
    prepared: Prepared
    window: TokenWindow
    values: object
    normalizer: object


class Kernel:
    schedule_id = 'token-half-single-one-event-explicit-arena-arrays-v1'

    def __init__(self, definition, *, element_cap):
        definition_check(definition)
        self.definition = definition
        self.element_cap = element_cap
        # Same topological grouping and edge order as the audited event kernel.
        self.levels = reference.Kernel(definition, element_cap=element_cap).levels

    def _arrays(self, a):
        if type(a) not in (CPUArrays, CudaArrays) or a.element_cap != self.element_cap:
            raise ContractError('closed matching token array execution contract required')

    def upload(self, origin, a):
        """Component ingress; the enclosing owner must derive the actual Gamma."""
        self._arrays(a)
        if type(origin) is not reference.Origin or origin.definition != self.definition:
            raise ContractError('complete matching packed master origin required')
        return amp.State(origin.definition, *(a.ingress(getattr(origin, k).astype(np.int64), 'int64') for k in ('E', 'C', 'W')),
                         origin.cursor, origin.optimizer_steps, origin.source)

    def prepare(self, origin, a):
        self._arrays(a)
        d = self.definition
        if type(origin) is not amp.State or origin.definition != d:
            raise ContractError('matching complete physical token origin required')
        for key, shape in (('E', (d.sources.vocabulary+1, d.width)), ('C', (d.slots,)), ('W', (d.output.labels, d.output.features))):
            value = getattr(origin, key)
            a._input(value)
            raw = a.raw(value)
            if a.dtype(value) != 'int64' or tuple(value.shape) != shape or np.any(raw < 0) or np.any(raw > reference.WORD_MAX):
                raise ContractError('complete uint32-valued token master blocks required')
        theta = a.cast(a.scaled_master(origin.C, d.output.grid_bits), 'float16')
        totals = a.scaled_master(a.columns(origin.W), d.output.grid_bits)
        base, base_total = a.rational(d.output.base), a.constant(sum(d.output.base, F(0)))
        if np.any(a.raw(base) <= 0) or not np.all(np.isfinite(a.raw(base))):
            raise ArithmeticUnresolved('token readout base cache lost positivity')
        return Prepared(origin, theta, totals, base, base_total)

    def _prepared(self, prepared, a):
        self._arrays(a)
        d = self.definition
        if type(prepared) is not Prepared or prepared.origin.definition != d:
            raise ContractError('complete matching prepared token operands required')
        for value, shape, dtype in ((prepared.theta, (d.slots,), 'float16'),
                                   (prepared.totals, (d.output.features,), 'float32'),
                                   (prepared.base, (d.output.labels,), 'float32'),
                                   (prepared.base_total, (), 'float32')):
            a._input(value)
            if tuple(value.shape) != shape or a.dtype(value) != dtype:
                raise ContractError('token preparation cache lost a complete typed coordinate')

    @staticmethod
    def _ids(values):
        return tuple(map(int, values))

    def predict(self, prepared, window, a):
        self._prepared(prepared, a)
        d = self.definition
        if type(window) is not TokenWindow or window.schema != d.sources:
            raise ContractError('complete actual token source point required')
        window.__post_init__()
        embedded = a.cast(a.scaled_master(a.take(prepared.origin.E, window.past), d.output.grid_bits), 'float16')
        values = a.cat((a.reshape(embedded, (d.input_nodes,)), a.zeros((len(d.nodes),), 'float16')))
        for sums, products in self.levels:
            if len(sums):
                terms = a.cast(a.mul(a.take(prepared.theta, self._ids(sums[:, 2])), a.take(values, self._ids(sums[:, 1]))), 'float32')
                ids, combined = a.segments(self._ids(sums[:, 0]), terms)
                values = a.replace_rows(values, ids, a.cast(combined, 'float16'))
            if len(products):
                result = a.mul(a.take(values, self._ids(products[:, 1])), a.take(values, self._ids(products[:, 2])))
                values = a.replace_rows(values, self._ids(products[:, 0]), result)
        features = a.take(a.cast(values, 'float32'), d.features)
        z = a.add(prepared.base_total, a.reduce(a.mul(prepared.totals, features)))
        if not np.isfinite(a.raw(z)).all() or a.raw(z) <= 0:
            raise ArithmeticUnresolved('token physical normalizer lost positivity')
        return Forecast(prepared, window, values, z)

    def observe(self, prepared, prediction, window, target, a):
        self._prepared(prepared, a)
        d = self.definition
        if (type(prediction) is not Forecast or prediction.prepared is not prepared
                or prediction.window != window or type(target) is not int or not 0 <= target < d.output.labels):
            raise ContractError('token observation lost its complete actual forecast/source/target')
        a._input(prediction.values)
        a._input(prediction.normalizer)
        if tuple(prediction.values.shape) != (d.input_nodes+len(d.nodes),) or a.dtype(prediction.values) != 'float16':
            raise ContractError('token forecast lost its complete stored half values')
        if tuple(prediction.normalizer.shape) != () or a.dtype(prediction.normalizer) != 'float32':
            raise ContractError('token forecast lost its scalar single normalizer')
        stored = a.cast(prediction.values, 'float32')
        features = a.take(stored, d.features)
        selected = a.reshape(a.scaled_master(a.take(prepared.origin.W, (target,)), d.output.grid_bits), (d.output.features,))
        mass = a.add(a.reshape(a.take(prepared.base, (target,)), ()), a.reduce(a.mul(selected, features)))
        if not np.isfinite(a.raw(mass)).all() or a.raw(mass) <= 0:
            raise ArithmeticUnresolved('token target mass lost positivity')
        z = prediction.normalizer
        common, correction = a.div(features, z), a.div(features, mass)
        seeds = a.sub(a.div(prepared.totals, z), a.div(selected, mass))
        count = d.input_nodes+len(d.nodes)
        ids, combined = a.segments(d.features, seeds)
        adjoints = a.replace_rows(a.zeros((count,)), ids, combined)
        gradient, theta = a.zeros((d.slots,)), a.cast(prepared.theta, 'float32')
        for sums, products in reversed(self.levels):
            if len(sums):
                edge = a.mul(a.take(adjoints, self._ids(sums[:, 0])), a.take(stored, self._ids(sums[:, 1])))
                ids, combined = a.segments(self._ids(sums[:, 2]), edge)
                gradient = a.replace_rows(gradient, ids, a.add(a.take(gradient, ids), combined))
                credits = a.mul(a.take(adjoints, self._ids(sums[:, 0])), a.take(theta, self._ids(sums[:, 2])))
                ids, combined = a.segments(self._ids(sums[:, 1]), credits)
                adjoints = a.replace_rows(adjoints, ids, a.add(a.take(adjoints, ids), combined))
            if len(products):
                left = a.mul(a.take(adjoints, self._ids(products[:, 0])), a.take(stored, self._ids(products[:, 2])))
                right = a.mul(a.take(adjoints, self._ids(products[:, 0])), a.take(stored, self._ids(products[:, 1])))
                ids, combined = a.segments(self._ids(np.r_[products[:, 1], products[:, 2]]), a.cat((left, right)))
                adjoints = a.replace_rows(adjoints, ids, a.add(a.take(adjoints, ids), combined))
        rows = a.reshape(a.take(adjoints, tuple(range(d.input_nodes))), (d.sources.context, d.width))
        embedding_ids, embedding = a.segments(window.past, rows)
        return amp.Pending(prepared.origin, (window,), (target,), a.reshape(prediction.values, (count, 1)),
                           a.reshape(z, (1,)), a.reshape(mass, (1,)), np.asarray(embedding_ids, dtype=np.int64),
                           embedding, gradient, common, np.asarray((target,), dtype=np.int64),
                           a.reshape(correction, (1, d.output.features)))

    def append(self, previous, leaf, a):
        """Extend all complete carry caches using fresh owned additions."""
        self._arrays(a)
        if type(leaf) is not amp.Pending or len(leaf.targets) != 1 or leaf.origin.definition != self.definition:
            raise ContractError('complete one-event derivative workspace required')
        if previous is not None and (type(previous) is not streaming.Pending or previous.origin is not leaf.origin
                or previous.unit_count >= self.definition.output.update_unit):
            raise ContractError('matching eligible complete carry predecessor required')
        def update(entries, ids, values):
            result = dict(entries)
            for index, key in enumerate(ids):
                row = a.reshape(a.take(values, (index,)), tuple(values.shape[1:]))
                result[int(key)] = result.get(int(key), streaming.Forest()).append(row, a)
            return tuple(sorted(result.items()))
        return streaming.Pending(leaf.origin, (() if previous is None else previous.leaves)+(leaf,),
            (streaming.Forest() if previous is None else previous.core).append(leaf.core, a),
            (streaming.Forest() if previous is None else previous.common).append(leaf.common, a),
            update(() if previous is None else previous.embedding, leaf.embedding_ids, leaf.embedding),
            update(() if previous is None else previous.corrections, leaf.correction_ids, leaf.corrections))

    def basis(self, pending, a):
        self._arrays(a)
        if type(pending) is not streaming.Pending or pending.origin.definition != self.definition:
            raise ContractError('complete matching streaming token state required')
        def rows(entries):
            ids = tuple(key for key, _ in entries)
            values = tuple(a.reshape(forest.root(a), (1,)+tuple(forest.blocks[0].value.shape)) for _, forest in entries)
            return ids, a.cat(values)
        ids, embedding = rows(pending.embedding)
        targets, corrections = rows(pending.corrections)
        return streaming.Basis(np.asarray(ids, dtype=np.int64), embedding, pending.core.root(a), pending.common.root(a),
                               np.asarray(targets, dtype=np.int64), corrections)

    def commit(self, pending, a):
        self._arrays(a)
        d = self.definition
        if type(pending) is not streaming.Pending or pending.unit_count != d.output.update_unit or pending.origin.definition != d:
            raise ContractError('complete registered token update unit required')
        old, b = pending.origin, self.basis(pending, a)
        scale = a.constant(d.output.grid*d.output.learning_rate/d.output.update_unit)
        ids, targets = self._ids(b.embedding_ids), self._ids(b.correction_ids)
        E = a.replace_rows(old.E, ids, a.project(a.take(old.E, ids), b.embedding, scale))
        C = a.project(old.C, b.core, scale)
        W = a.project(old.W, b.common, scale)
        corrected = a.project(a.take(old.W, targets), a.sub(b.common, b.corrections), scale)
        W = a.replace_rows(W, targets, corrected)
        return amp.State(d, E, C, W, pending.cursor, old.optimizer_steps+1, pending.source)
