"""Passive batched enclosure kernel for complete retained native token units.

Only existing SUM/PRODUCT and grid-SGD semantics. The uint32 master and
per-array element limits are realization/solver limits, not semantic caps.
Records must already be revealed; no online freshness, Runtime, AMP or
whole-host resource authority is supplied by this numerical component.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import math
import numpy as np

from .program import Sum, Product
from . import token_native as tokens
from . import token_readout as readout
from .token_enclosures import Interval, EnclosureUnresolved

WORD_MAX = (1 << 32)-1


def size_check(shape, cap):
    if math.prod(shape) > cap:
        raise EnclosureUnresolved('declared array element allowance exhausted')


def finite(value):
    if not np.all(np.isfinite(value)):
        raise EnclosureUnresolved('nonfinite array enclosure operation')
    return value


@dataclass(frozen=True)
class ArrayInterval:
    lower: np.ndarray
    upper: np.ndarray

    def __post_init__(self):
        if (type(self.lower) is not np.ndarray or type(self.upper) is not np.ndarray
                or self.lower.dtype != np.float64 or self.upper.dtype != np.float64
                or self.lower.shape != self.upper.shape or np.any(self.lower > self.upper)):
            raise ValueError('complete equally shaped binary64 interval arrays required')
        finite(self.lower)
        finite(self.upper)

    @classmethod
    def point(cls, value):
        value = np.asarray(value, dtype=np.float64)
        return cls(value, value)

    @classmethod
    def rational(cls, value):
        scalar = Interval.exact(value)
        return cls(np.asarray(scalar.lower), np.asarray(scalar.upper))

    @classmethod
    def zero(cls, shape):
        return cls.point(np.zeros(shape, dtype=np.float64))

    def __getitem__(self, key):
        return ArrayInterval(np.asarray(self.lower[key]), np.asarray(self.upper[key]))

    def __neg__(self):
        return ArrayInterval(-self.upper, -self.lower)

    def __add__(self, other):
        with np.errstate(over='ignore', under='ignore', invalid='ignore'):
            low = finite(self.lower+other.lower)
            high = finite(self.upper+other.upper)
            low, high = np.nextafter(low, -np.inf), np.nextafter(high, np.inf)
        a_zero = (self.lower == 0) & (self.upper == 0)
        b_zero = (other.lower == 0) & (other.upper == 0)
        low = np.where(b_zero, self.lower, np.where(a_zero, other.lower, low))
        high = np.where(b_zero, self.upper, np.where(a_zero, other.upper, high))
        return ArrayInterval(np.asarray(low), np.asarray(high))

    def __sub__(self, other):
        return self+(-other)

    def __mul__(self, other):
        with np.errstate(over='ignore', under='ignore', invalid='ignore'):
            products = tuple(finite(a*b) for a in (self.lower, self.upper) for b in (other.lower, other.upper))
            low = high = products[0]
            # Reducing the Python tuple would first stack four full arrays.
            # Pairwise selection keeps every temporary within the array quota.
            for value in products[1:]:
                low, high = np.minimum(low, value), np.maximum(high, value)
            low = np.nextafter(low, -np.inf)
            high = np.nextafter(high, np.inf)
        a_zero = (self.lower == 0) & (self.upper == 0)
        b_zero = (other.lower == 0) & (other.upper == 0)
        a_one = (self.lower == 1) & (self.upper == 1)
        b_one = (other.lower == 1) & (other.upper == 1)
        low = np.where(a_zero | b_zero, 0.0, np.where(a_one, other.lower, np.where(b_one, self.lower, low)))
        high = np.where(a_zero | b_zero, 0.0, np.where(a_one, other.upper, np.where(b_one, self.upper, high)))
        return ArrayInterval(np.asarray(low), np.asarray(high))

    def reciprocal(self):
        if np.any((self.lower <= 0) & (self.upper >= 0)):
            raise EnclosureUnresolved('array denominator contains zero')
        with np.errstate(over='ignore', under='ignore', invalid='ignore', divide='ignore'):
            low, high = finite(1.0/self.upper), finite(1.0/self.lower)
            low, high = np.nextafter(low, -np.inf), np.nextafter(high, np.inf)
        one = (self.lower == 1) & (self.upper == 1)
        return ArrayInterval(np.asarray(np.where(one, 1.0, low)), np.asarray(np.where(one, 1.0, high)))

    def __truediv__(self, other):
        return self*other.reciprocal()

    def positive(self):
        if np.any(self.upper < 0):
            raise EnclosureUnresolved('nonnegative native quantity has negative bound')
        return ArrayInterval(np.maximum(0.0, self.lower), self.upper)

    def transpose(self, axes=None):
        return ArrayInterval(self.lower.transpose(axes), self.upper.transpose(axes))

    def reshape(self, shape):
        return ArrayInterval(self.lower.reshape(shape), self.upper.reshape(shape))

    def scalar(self, index=()):
        return Interval(float(self.lower[index]), float(self.upper[index]))


def join(values, axis=0):
    return ArrayInterval(np.concatenate([v.lower for v in values], axis=axis), np.concatenate([v.upper for v in values], axis=axis))


def reduce_rows(values):
    """Explicit balanced addition tree along axis zero; no opaque sum kernel."""
    if not len(values.lower):
        return ArrayInterval.zero(values.lower.shape[1:])
    while len(values.lower) > 1:
        pairs = len(values.lower)//2
        following = values[:2*pairs:2]+values[1:2*pairs:2]
        values = join((following, values[-1:])) if len(values.lower) % 2 else following
    return values[0]


def segment_rows(keys, values):
    """Stable grouped balanced sums, preserving every repeated incidence."""
    keys = np.asarray(keys, dtype=np.int64)
    if keys.ndim != 1 or len(keys) != len(values.lower):
        raise ValueError('one complete segment key per row required')
    if not len(keys):
        return keys, values
    order = np.argsort(keys, kind='stable')
    keys, values = keys[order], values[order]
    while np.any(keys[1:] == keys[:-1]):
        index = np.arange(len(keys), dtype=np.int64)
        start = np.r_[True, keys[1:] != keys[:-1]]
        within = index-np.maximum.accumulate(np.where(start, index, 0))
        take = index[within % 2 == 0]
        has_pair = (take+1 < len(keys)) & (keys[np.minimum(take+1, len(keys)-1)] == keys[take])
        low, high = values.lower[take].copy(), values.upper[take].copy()
        paired = values[take[has_pair]]+values[take[has_pair]+1]
        low[has_pair], high[has_pair] = paired.lower, paired.upper
        keys, values = keys[take], ArrayInterval(low, high)
    return keys, values


def words(values):
    values = np.asarray(values)
    if (values.dtype.kind not in 'iuf' or not np.all(np.isfinite(values)) or np.any(values < 0)
            or np.any(values > WORD_MAX) or np.any(values != np.floor(values))):
        raise EnclosureUnresolved('uint32 exact master representation exhausted')
    return np.asarray(values, dtype=np.uint32).tobytes(order='C')


def walk(root):
    stack = []
    while stack or root is not None:
        while root is not None:
            stack.append(root)
            root = root.left
        root = stack.pop()
        yield root.key, root.value
        root = root.right


@dataclass(frozen=True)
class Origin:
    definition: tokens.Definition
    embedding: bytes
    core: bytes
    output: bytes
    cursor: int
    optimizer_steps: int
    source: tokens.TokenWindow

    def __post_init__(self):
        d = self.definition
        if type(d) is not tokens.Definition or type(self.source) is not tokens.TokenWindow:
            raise ValueError('closed native definition and source point required')
        d.__post_init__()
        if d.output.grid_bits > 32 or d.output.labels > 1 << 20:
            raise EnclosureUnresolved('registered packed master/grid/column-total realization limit exceeded')
        for payload, count in ((self.embedding, d.embedding_slots), (self.core, d.slots), (self.output, d.output.labels*d.output.features)):
            if type(payload) is not bytes or len(payload) != 4*count:
                raise ValueError('complete immutable uint32 master buffers required')
        readout.natural(self.cursor)
        readout.natural(self.optimizer_steps)
        if self.cursor % d.output.update_unit or self.source.schema != d.sources:
            raise ValueError('complete committed origin and matching source schema required')
        self.source.__post_init__()

    @property
    def E(self):
        d = self.definition
        return np.frombuffer(self.embedding, dtype=np.uint32).reshape(d.sources.vocabulary+1, d.width)

    @property
    def C(self):
        return np.frombuffer(self.core, dtype=np.uint32)

    @property
    def W(self):
        d = self.definition
        return np.frombuffer(self.output, dtype=np.uint32).reshape(d.output.labels, d.output.features)

    def parameter(self, slot):
        readout.natural(slot)
        d = self.definition
        if slot >= d.slot_count:
            raise ValueError('undeclared native parameter')
        if slot < d.embedding_slots:
            value = self.E.flat[slot]
        elif slot < d.embedding_slots+d.slots:
            value = self.C[slot-d.embedding_slots]
        else:
            value = self.W.flat[slot-d.embedding_slots-d.slots]
        return F(int(value), d.output.grid)

    @classmethod
    def from_native(cls, state, *, element_cap):
        readout.natural(element_cap, positive=True)
        d = state.definition
        if d.output.grid_bits > 32 or d.output.labels > 1 << 20:
            raise EnclosureUnresolved('registered packed master/grid/column-total realization limit exceeded')
        for shape in ((d.embedding_slots,), (d.slots,), (d.output.labels, d.output.features)):
            size_check(shape, element_cap)
        if (state.output.unit_count or state.embedding_gradient or any(state.core_gradient)
                or any(state.output.common) or state.output.corrections):
            raise ValueError('packed origin needs a complete native commit boundary')
        E = np.tile(np.frombuffer(words(state.embedding.defaults), dtype=np.uint32), (d.sources.vocabulary+1, 1))
        for index, value in walk(state.embedding.overrides):
            if not 0 <= index < d.embedding_slots:
                raise ValueError('foreign embedding coordinate')
            E.flat[index] = np.frombuffer(words((value,)), dtype=np.uint32)[0]
        W = np.empty((d.output.labels, d.output.features), dtype=np.uint32)
        for k, column in enumerate(state.output.columns):
            W[:, k] = np.frombuffer(words((max(0, column.default-column.offset),)), dtype=np.uint32)[0]
            for label, raw in walk(column.labels):
                if not 0 <= label < d.output.labels:
                    raise ValueError('foreign output coordinate')
                W[label, k] = np.frombuffer(words((max(0, raw-column.offset),)), dtype=np.uint32)[0]
        return cls(d, E.tobytes(), words(state.theta), W.tobytes(), state.cursor, state.output.optimizer_steps, state.source_window())

    def to_native(self):
        """Explicit expensive state materialization, not a newborn constructor."""
        d = self.definition
        E, W = self.E, self.W
        e_rows, e_columns = np.nonzero(E != E[0])
        w_rows, w_columns = np.nonzero(W != W[0])
        state = tokens.initialize(d, tuple(map(int, E[0])), tuple(map(int, self.C)), tuple(map(int, W[0])),
            embedding_overrides=((int(v), int(k), int(E[v, k])) for v, k in zip(e_rows, e_columns)),
            output_overrides=((int(v), int(k), int(W[v, k])) for v, k in zip(w_rows, w_columns)))
        return replace(state, output=replace(state.output, cursor=self.cursor, optimizer_steps=self.optimizer_steps),
            past=self.source.past, source_position=self.source.position)


@dataclass(frozen=True)
class Unit:
    origin: Origin
    windows: tuple[tokens.TokenWindow, ...]
    targets: tuple[int, ...]

    def exact_decoder(self):
        if len(self.windows) != len(self.targets):
            raise ValueError('complete source point required for every retained target')
        state = self.origin.to_native()
        for window, target in zip(self.windows, self.targets):
            state = state.observe(state.predict(window), target, window=window)
        return state


@dataclass(frozen=True)
class GradientBounds:
    """Pending-gradient projection, with the complete exact replay recipe.

    This passive value has no historical activation/mass or commit interface.
    Its producer must establish enclosure; construction is not a certificate.
    """
    unit: Unit
    embedding_ids: np.ndarray
    embedding: ArrayInterval
    core: ArrayInterval
    common: ArrayInterval
    correction_ids: np.ndarray
    corrections: ArrayInterval

    @property
    def unit_count(self):
        return len(self.unit.targets)

    @property
    def cursor(self):
        return self.unit.origin.cursor+self.unit_count

    @property
    def source(self):
        return self.unit.windows[-1].append(self.unit.targets[-1])

    def gradient(self, slot):
        return Bounds.gradient(self, slot)


@dataclass(frozen=True)
class Bounds:
    unit: Unit
    values: ArrayInterval
    normalizer: ArrayInterval
    target_mass: ArrayInterval
    embedding_ids: np.ndarray
    embedding: ArrayInterval
    core: ArrayInterval
    common: ArrayInterval
    correction_ids: np.ndarray
    corrections: ArrayInterval

    @property
    def unit_count(self):
        return len(self.unit.targets)

    @property
    def cursor(self):
        return self.unit.origin.cursor+self.unit_count

    @property
    def source(self):
        return self.unit.windows[-1].append(self.unit.targets[-1])

    def mass(self, event, label):
        d = self.unit.origin.definition
        readout.natural(event)
        readout.natural(label)
        if event >= len(self.unit.targets) or label >= d.output.labels:
            raise ValueError('undeclared batch event or output coordinate')
        weights = ArrayInterval.point(np.ldexp(self.unit.origin.W[label].astype(np.float64), -d.output.grid_bits))
        features = self.values[np.asarray(d.features), event]
        return (ArrayInterval.rational(d.output.base[label])+reduce_rows(weights*features)).scalar()

    def gradient(self, slot):
        readout.natural(slot)
        d = self.unit.origin.definition
        if slot >= d.slot_count:
            raise ValueError('undeclared native gradient')
        if slot < d.embedding_slots:
            token, k = divmod(slot, d.width)
            index = int(np.searchsorted(self.embedding_ids, token))
            return self.embedding.scalar((index, k)) if index < len(self.embedding_ids) and self.embedding_ids[index] == token else Interval.exact(0)
        slot -= d.embedding_slots
        if slot < d.slots:
            return self.core.scalar(slot)
        token, k = divmod(slot-d.slots, d.output.features)
        index = int(np.searchsorted(self.correction_ids, token))
        correction = self.corrections.scalar((index, k)) if index < len(self.correction_ids) and self.correction_ids[index] == token else Interval.exact(0)
        return self.common.scalar(k)-correction

    def commit(self):
        try:
            return self._commit()
        except EnclosureUnresolved as error:
            error.retained_unit = self.unit
            raise

    def _commit(self):
        origin, d = self.unit.origin, self.unit.origin.definition
        if self.unit_count != d.output.update_unit:
            raise ValueError('only the complete registered update unit can commit')
        scale = ArrayInterval.rational(d.output.grid*d.output.learning_rate/d.output.update_unit)
        def project(value, label):
            low, high = np.floor(np.maximum(0.0, value.lower)), np.floor(np.maximum(0.0, value.upper))
            if np.any(low != high):
                raise EnclosureUnresolved('batched grid cell unresolved for '+label)
            return np.frombuffer(words(low), dtype=np.uint32).reshape(low.shape)
        E = origin.E.copy()
        E[self.embedding_ids] = project(ArrayInterval.point(origin.E[self.embedding_ids])-scale*self.embedding, 'embedding')
        C = project(ArrayInterval.point(origin.C)-scale*self.core, 'core')
        # Keep the combined signed expression on every corrected row. Nothing
        # is projected/clipped before the target correction is included.
        value = ArrayInterval.point(origin.W)-scale*self.common
        corrected = ArrayInterval.point(origin.W[self.correction_ids])-scale*(self.common-self.corrections)
        low, high = value.lower.copy(), value.upper.copy()
        low[self.correction_ids], high[self.correction_ids] = corrected.lower, corrected.upper
        W = project(ArrayInterval(low, high), 'readout')
        source = self.unit.windows[-1].append(self.unit.targets[-1])
        return Origin(d, E.tobytes(), C.tobytes(), W.tobytes(), origin.cursor+d.output.update_unit, origin.optimizer_steps+1, source)


@dataclass(frozen=True)
class Prediction:
    predecessor: object
    window: tokens.TokenWindow
    values: ArrayInterval
    normalizer: ArrayInterval

    @property
    def origin(self):
        return self.predecessor.unit.origin if type(self.predecessor) in (Bounds, GradientBounds) else self.predecessor

    def mass(self, label):
        readout.natural(label)
        d = self.origin.definition
        if label >= d.output.labels:
            raise ValueError('undeclared output label')
        weights = ArrayInterval.point(np.ldexp(self.origin.W[label].astype(np.float64), -d.output.grid_bits))
        return (ArrayInterval.rational(d.output.base[label])+reduce_rows(weights*self.values[np.asarray(d.features), 0])).scalar()


class Kernel:
    """A fixed native DAG schedule, with an explicit per-array element quota."""
    def __init__(self, definition, *, element_cap):
        definition.__post_init__()
        readout.natural(element_cap, positive=True)
        self.definition, self.element_cap = definition, element_cap
        d, N = definition, definition.output.update_unit
        count = d.input_nodes+len(d.nodes)
        edges = sum(len(n.terms) if type(n) is Sum else 2 for n in d.nodes)
        for shape in ((count, N), (max(1, edges), N), (max(1, edges), 3), (d.slots,),
                      (d.sources.vocabulary+1, d.width), (d.output.labels, d.output.features),
                      (d.output.features, N), (N, d.sources.context, d.width)):
            size_check(shape, element_cap)
        depths = [0]*d.input_nodes
        levels = {}
        for index, node in enumerate(d.nodes, d.input_nodes):
            parents = [t.parent for t in node.terms] if type(node) is Sum else [node.left, node.right]
            depth = 1+max((depths[p] for p in parents), default=0)
            depths.append(depth)
            sums, products = levels.setdefault(depth, ([], []))
            if type(node) is Sum:
                sums.extend((index, t.parent, t.slot) for t in node.terms)
            else:
                products.append((index, node.left, node.right))
        self.levels = tuple((np.asarray(sums, dtype=np.int64).reshape(-1, 3),
                             np.asarray(products, dtype=np.int64).reshape(-1, 3)) for _, (sums, products) in sorted(levels.items()))
        cache = {value: Interval.exact(value) for value in set(d.output.base)}
        self.base = ArrayInterval(np.asarray([cache[v].lower for v in d.output.base]), np.asarray([cache[v].upper for v in d.output.base]))
        from .token_base_facts import known_total
        total = known_total(d.output.base, None)
        self.base_total = ArrayInterval.rational(sum(d.output.base, F(0)) if total is None else total)

    def bound(self, origin, windows, targets):
        if type(targets) is not tuple or len(targets) != self.definition.output.update_unit:
            raise ValueError('one complete registered retained update unit required')
        return self.prefix(origin, windows, targets)

    def prefix(self, origin, windows, targets):
        """Complete pending state for an actually retained nonempty prefix."""
        d = self.definition
        if type(origin) is not Origin or origin.definition != d:
            raise ValueError('actual complete packed origin required')
        if type(windows) is not tuple or type(targets) is not tuple or len(windows) != len(targets) or not 1 <= len(targets) <= d.output.update_unit:
            raise ValueError('matching revealed nonempty prefix within the registered unit required')
        for window, target in zip(windows, targets):
            if type(window) is not tokens.TokenWindow or window.schema != d.sources:
                raise ValueError('complete matching retained source points required')
            window.__post_init__()
            readout.natural(target)
            if target >= d.output.labels:
                raise ValueError('undeclared target label')
        unit = Unit(origin, windows, targets)
        try:
            return self._bound(unit)
        except EnclosureUnresolved as error:
            error.retained_unit = unit
            raise

    def predict(self, predecessor, window=None):
        if type(predecessor) not in (Origin, Bounds, GradientBounds):
            raise ValueError('complete committed or pending native predecessor required')
        pending = type(predecessor) in (Bounds, GradientBounds)
        origin = predecessor.unit.origin if pending else predecessor
        if origin.definition != self.definition or pending and predecessor.unit_count >= self.definition.output.update_unit:
            raise ValueError('matching learner must commit its full unit before another prediction')
        window = predecessor.source if window is None else window
        if type(window) is not tokens.TokenWindow or window.schema != self.definition.sources:
            raise ValueError('complete matching source point required')
        window.__post_init__()
        values, features, totals, _, _ = self._forward(origin, (window,))
        normalizer = (self.base_total+reduce_rows(totals[:, None]*features)).positive()
        return Prediction(predecessor, window, values, normalizer)

    def observe(self, predecessor, prediction, target, *, window=None):
        """Bind a pre-target cache to one next retained record."""
        if type(prediction) is not Prediction or prediction.predecessor is not predecessor:
            raise ValueError('prediction must belong to the complete current predecessor')
        previous = predecessor.unit if type(predecessor) in (Bounds, GradientBounds) else Unit(predecessor, (), ())
        actual_window = predecessor.source if window is None else window
        try:
            expected = self.predict(predecessor, actual_window)
        except EnclosureUnresolved as error:
            error.retained_unit = Unit(previous.origin, previous.windows+(actual_window,), previous.targets+(target,))
            raise
        if prediction.window != expected.window or any(
                type(getattr(prediction, field)) is not ArrayInterval
                or getattr(prediction, field).lower.shape != getattr(expected, field).lower.shape
                or getattr(prediction, field).upper.shape != getattr(expected, field).upper.shape
                or getattr(prediction, field).lower.dtype != np.float64 or getattr(prediction, field).upper.dtype != np.float64
                or getattr(prediction, field).lower.tobytes() != getattr(expected, field).lower.tobytes()
                or getattr(prediction, field).upper.tobytes() != getattr(expected, field).upper.tobytes()
                for field in ('values', 'normalizer')):
            raise ValueError('prediction differs from its actual source point or native cache')
        return self.prefix(previous.origin, previous.windows+(expected.window,), previous.targets+(target,))

    def _forward(self, origin, windows):
        d = self.definition
        N, D, L = len(windows), d.width, d.sources.context
        node_count = d.input_nodes+len(d.nodes)
        history = np.asarray([w.past for w in windows], dtype=np.int64)
        theta = np.ldexp(origin.C.astype(np.float64), -d.output.grid_bits)
        low, high = np.zeros((node_count, N)), np.zeros((node_count, N))
        inputs = np.ldexp(origin.E[history].astype(np.float64), -d.output.grid_bits).transpose(1, 2, 0).reshape(d.input_nodes, N)
        low[:d.input_nodes], high[:d.input_nodes] = inputs, inputs
        for sums, products in self.levels:
            values = ArrayInterval(low, high)
            if len(sums):
                terms = ArrayInterval.point(theta[sums[:, 2], None])*values[sums[:, 1]]
                ids, combined = segment_rows(sums[:, 0], terms)
                combined = combined.positive()
                low[ids], high[ids] = combined.lower, combined.upper
            if len(products):
                combined = (values[products[:, 1]]*values[products[:, 2]]).positive()
                low[products[:, 0]], high[products[:, 0]] = combined.lower, combined.upper
        values = ArrayInterval(low, high)
        features = values[np.asarray(d.features)]
        # V<=2^20 and uint32 masters keep each integer column sum below2^52.
        totals = ArrayInterval.point(np.ldexp(origin.W.sum(axis=0, dtype=np.uint64).astype(np.float64), -d.output.grid_bits))
        return values, features, totals, theta, history

    def _bound(self, unit):
        origin, d = unit.origin, self.definition
        N, D, L = len(unit.targets), d.width, d.sources.context
        node_count = d.input_nodes+len(d.nodes)
        targets = np.asarray(unit.targets, dtype=np.int64)
        values, features, totals, theta, history = self._forward(origin, unit.windows)
        selected = ArrayInterval.point(np.ldexp(origin.W[targets].astype(np.float64), -d.output.grid_bits)).transpose()
        normalizer = (self.base_total+reduce_rows(totals[:, None]*features)).positive()
        mass = (self.base[targets]+reduce_rows(selected*features)).positive()
        common = reduce_rows((features/normalizer).transpose())
        correction_ids, corrections = segment_rows(targets, (features/mass).transpose())
        seeds = totals[:, None]/normalizer-selected/mass
        adj_low, adj_high = np.zeros((node_count, N)), np.zeros((node_count, N))
        ids, combined = segment_rows(np.asarray(d.features), seeds)
        adj_low[ids], adj_high[ids] = combined.lower, combined.upper
        grad_low, grad_high = np.zeros(d.slots), np.zeros(d.slots)
        for sums, products in reversed(self.levels):
            adjoints = ArrayInterval(adj_low, adj_high)
            if len(sums):
                gradients = reduce_rows((adjoints[sums[:, 0]]*values[sums[:, 1]]).transpose())
                ids, combined = segment_rows(sums[:, 2], gradients)
                accumulated = ArrayInterval(grad_low[ids], grad_high[ids])+combined
                grad_low[ids], grad_high[ids] = accumulated.lower, accumulated.upper
                credits = adjoints[sums[:, 0]]*ArrayInterval.point(theta[sums[:, 2], None])
                ids, combined = segment_rows(sums[:, 1], credits)
                accumulated = ArrayInterval(adj_low[ids], adj_high[ids])+combined
                adj_low[ids], adj_high[ids] = accumulated.lower, accumulated.upper
            if len(products):
                left = adjoints[products[:, 0]]*values[products[:, 2]]
                right = adjoints[products[:, 0]]*values[products[:, 1]]
                ids, combined = segment_rows(np.r_[products[:, 1], products[:, 2]], join((left, right)))
                accumulated = ArrayInterval(adj_low[ids], adj_high[ids])+combined
                adj_low[ids], adj_high[ids] = accumulated.lower, accumulated.upper
        embedding_adjoints = ArrayInterval(adj_low[:d.input_nodes], adj_high[:d.input_nodes])
        rows = embedding_adjoints.reshape((L, D, N)).transpose((0, 2, 1)).reshape((L*N, D))
        embedding_ids, embedding = segment_rows(history.T.reshape(-1), rows)
        return Bounds(unit, values, normalizer, mass, embedding_ids, embedding, ArrayInterval(grad_low, grad_high),
            common, correction_ids, corrections)
