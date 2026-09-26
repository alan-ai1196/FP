"""Passive binary64 enclosures of exact native token gradients and commits.

A resolved grid commit is an exact native endpoint, not a floating learner
endpoint. Pending exact gradients remain defined by the immutable unit
origin and retained source/target records. Ambiguity refuses without erasing them.
No Runtime, owned resource, AMP or installation authority is supplied.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
import math
import sys

from fp_reference.program import Sum
import native_readout as readout
import native_tokens as tokens


class EnclosureUnresolved(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.retained_unit = None


def outward(value, direction):
    if not math.isfinite(value):
        raise EnclosureUnresolved('nonfinite binary64 enclosure operation')
    result = math.nextafter(value, direction)
    if not math.isfinite(result):
        raise EnclosureUnresolved('binary64 outward endpoint exhausted')
    return result


@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float

    def __post_init__(self):
        if (type(self.lower) is not float or type(self.upper) is not float
                or not math.isfinite(self.lower) or not math.isfinite(self.upper)
                or self.lower > self.upper):
            raise EnclosureUnresolved('finite ordered binary64 endpoints required')

    @classmethod
    def exact(cls, value):
        if type(value) not in (int, F):
            raise ValueError('exact integer/rational ingress required')
        value = F(value)
        try:
            rounded = float(value)
        except OverflowError as error:
            raise EnclosureUnresolved('exact ingress exceeds binary64') from error
        if not math.isfinite(rounded):
            raise EnclosureUnresolved('nonfinite exact ingress')
        actual = F(rounded)
        result = cls(outward(rounded, -math.inf) if actual > value else rounded,
                     outward(rounded, math.inf) if actual < value else rounded)
        if not result.contains(value):
            raise EnclosureUnresolved('adjacent binary64 ingress failed its exact enclosure check')
        return result

    def is_point(self, value):
        return self.lower == self.upper == value

    def __neg__(self):
        return Interval(-self.upper, -self.lower)

    def __add__(self, other):
        if self.is_point(0):
            return other
        if other.is_point(0):
            return self
        return Interval(outward(self.lower+other.lower, -math.inf), outward(self.upper+other.upper, math.inf))

    def __sub__(self, other):
        # Equal bounds do not prove equal exact quantities: no x-x shortcut.
        return self+(-other)

    def __mul__(self, other):
        if self.is_point(0) or other.is_point(0):
            return ZERO
        if self.is_point(1):
            return other
        if other.is_point(1):
            return self
        values = (self.lower*other.lower, self.lower*other.upper,
                  self.upper*other.lower, self.upper*other.upper)
        if not all(math.isfinite(v) for v in values):
            raise EnclosureUnresolved('nonfinite enclosure multiplication')
        return Interval(outward(min(values), -math.inf), outward(max(values), math.inf))

    def reciprocal(self):
        if self.lower <= 0 <= self.upper:
            raise EnclosureUnresolved('enclosed denominator contains zero')
        if self.is_point(1):
            return ONE
        return Interval(outward(1.0/self.upper, -math.inf), outward(1.0/self.lower, math.inf))

    def __truediv__(self, other):
        return self*other.reciprocal()

    def nonnegative(self):
        if self.upper < 0:
            raise EnclosureUnresolved('positive semantic value has a negative enclosure')
        return Interval(max(0.0, self.lower), self.upper)

    def contains(self, value):
        return F(self.lower) <= value <= F(self.upper)


ZERO, ONE = Interval(0.0, 0.0), Interval(1.0, 1.0)


def project_grid(value, label):
    lower = math.floor(max(0.0, value.lower))
    upper = math.floor(max(0.0, value.upper))
    if lower != upper:
        raise EnclosureUnresolved(f'grid cell unresolved for {label}')
    return lower


@dataclass(frozen=True)
class RetainedUnit:
    origin: tokens.Learner
    targets: tuple[int, ...]
    past: tuple[int, ...]
    windows: tuple[tokens.TokenWindow, ...]

    def exact_decoder(self):
        if len(self.windows) != len(self.targets):
            raise ValueError('complete source point required for every retained target')
        state = self.origin
        for window, target in zip(self.windows, self.targets):
            state = state.observe(state.predict(window), target, window=window)
        return state


@dataclass(frozen=True)
class Pending:
    origin: tokens.Learner
    targets: tuple[int, ...]
    past: tuple[int, ...]
    common: tuple[Interval, ...]
    corrections: tuple[tuple[int, tuple[Interval, ...]], ...]
    embedding_gradient: tuple[tuple[int, Interval], ...]
    core_gradient: tuple[Interval, ...]
    windows: tuple[tokens.TokenWindow, ...]

    @property
    def cursor(self):
        return self.origin.cursor+len(self.targets)

    @property
    def source_position(self):
        return self.windows[-1].position+1 if self.windows else self.origin.source_position

    def retained_unit(self):
        return RetainedUnit(self.origin, self.targets, self.past, self.windows)

    def source_window(self, window=None):
        if window is None:
            window = tokens.TokenWindow(self.origin.definition.sources, self.source_position, self.past)
        return self.origin.source_window(window)

    def predict(self, window=None):
        try:
            return self._predict(self.source_window(window))
        except EnclosureUnresolved as error:
            error.retained_unit = self.retained_unit()
            raise

    def _predict(self, window):
        d, grid = self.origin.definition, self.origin.definition.output.grid
        if len(self.targets) >= d.output.update_unit:
            raise ValueError('registered optimizer commit is due')
        values = [Interval.exact(F(self.origin.embedding.master(token*d.width+k), grid))
                  for token in window.past for k in range(d.width)]
        for node in d.nodes:
            if type(node) is Sum:
                value = sum((Interval.exact(F(self.origin.theta[t.slot], grid))*values[t.parent]
                             for t in node.terms), ZERO)
            else:
                value = values[node.left]*values[node.right]
            values.append(value.nonnegative())
        totals = tuple(Interval.exact(F(column.total(), grid)) for column in self.origin.output.columns)
        normalizer = Interval.exact(self.origin.output.base_total)+sum(
            (total*values[i] for total, i in zip(totals, d.features)), ZERO)
        return Prediction(self, tuple(values), totals, normalizer.nonnegative(), window)

    def gradient(self, slot):
        readout.natural(slot)
        d = self.origin.definition
        if slot < d.embedding_slots:
            return next((g for s, g in self.embedding_gradient if s == slot), ZERO)
        slot -= d.embedding_slots
        if slot < d.slots:
            return self.core_gradient[slot]
        slot -= d.slots
        label, feature = divmod(slot, d.output.features)
        self.origin.output.index(label, feature)
        row = next((row for y, row in self.corrections if y == label), (ZERO,)*d.output.features)
        return self.common[feature]-row[feature]

    def observe(self, prediction, target, *, window=None):
        if type(prediction) is not Prediction or prediction.state is not self:
            raise ValueError('enclosure prediction lost its actual predecessor')
        self.origin.output.index(target, 0)
        if len(self.targets) >= self.origin.definition.output.update_unit:
            raise ValueError('registered optimizer commit is due')
        window = self.source_window(window)
        following_window = window.append(target)
        retained = RetainedUnit(self.origin, self.targets+(target,), following_window.past, self.windows+(window,))
        try:
            return self._observe(prediction, target, window)
        except EnclosureUnresolved as error:
            # The exact unit remains defined even when no new gradient
            # enclosure can be published. This is not an old-bound fallback.
            error.retained_unit = retained
            raise

    def _observe(self, prediction, target, window):
        expected = self.predict(window)
        if ((prediction.values, prediction.totals, prediction.normalizer, prediction.window)
                != (expected.values, expected.totals, expected.normalizer, expected.window)):
            raise ValueError('enclosure cache differs from actual execution')
        d, grid = self.origin.definition, self.origin.definition.output.grid
        features, mass = prediction.features, prediction.mass(target)
        common = tuple(a+z/prediction.normalizer for a, z in zip(self.common, features))
        corrections = dict(self.corrections)
        old = corrections.get(target, (ZERO,)*d.output.features)
        corrections[target] = tuple(a+z/mass for a, z in zip(old, features))
        adjoints = [ZERO]*len(prediction.values)
        for k, index in enumerate(d.features):
            adjoints[index] = adjoints[index]+prediction.totals[k]/prediction.normalizer-Interval.exact(self.origin.output.parameter(target, k))/mass
        core_gradient = list(self.core_gradient)
        for index in range(len(prediction.values)-1, d.input_nodes-1, -1):
            node, seed = d.nodes[index-d.input_nodes], adjoints[index]
            if type(node) is Sum:
                for term in node.terms:
                    core_gradient[term.slot] = core_gradient[term.slot]+seed*prediction.values[term.parent]
                    adjoints[term.parent] = adjoints[term.parent]+seed*Interval.exact(F(self.origin.theta[term.slot], grid))
            else:
                adjoints[node.left] = adjoints[node.left]+seed*prediction.values[node.right]
                adjoints[node.right] = adjoints[node.right]+seed*prediction.values[node.left]
        embedding_gradient = dict(self.embedding_gradient)
        for lag, token in enumerate(window.past):
            for k in range(d.width):
                coordinate = token*d.width+k
                embedding_gradient[coordinate] = embedding_gradient.get(coordinate, ZERO)+adjoints[lag*d.width+k]
        return replace(self, targets=self.targets+(target,), past=window.append(target).past, windows=self.windows+(window,), common=common,
            corrections=tuple(sorted(corrections.items())), embedding_gradient=tuple(sorted(embedding_gradient.items())),
            core_gradient=tuple(core_gradient))

    def exact_decoder(self):
        """Replay the complete retained unit on demand; no decoder cost claim."""
        return self.retained_unit().exact_decoder()

    def commit(self):
        try:
            return self._commit()
        except EnclosureUnresolved as error:
            error.retained_unit = self.retained_unit()
            raise

    def _commit(self):
        d = self.origin.definition
        if len(self.targets) != d.output.update_unit or self.cursor % d.output.update_unit:
            raise ValueError('commit outside the complete registered update unit')
        scale = Interval.exact(d.output.grid*d.output.learning_rate/d.output.update_unit)
        embedding = self.origin.embedding
        for coordinate, gradient in self.embedding_gradient:
            master = project_grid(Interval.exact(embedding.master(coordinate))-scale*gradient, f'embedding {coordinate}')
            embedding = embedding.write(coordinate, master)
        theta = tuple(project_grid(Interval.exact(q)-scale*g, f'core {i}')
                      for i, (q, g) in enumerate(zip(self.origin.theta, self.core_gradient)))
        columns = []
        for k, column in enumerate(self.origin.output.columns):
            alpha = (scale*self.common[k]).nonnegative()
            shift, upper_shift = math.ceil(alpha.lower), math.ceil(alpha.upper)
            if shift != upper_shift:
                raise EnclosureUnresolved(f'common readout shift unresolved for column {k}')
            following = replace(column, offset=column.offset+shift)
            for label, row in self.corrections:
                value = Interval.exact(column.master(label))-alpha+scale*row[k]
                master = project_grid(value, f'readout {label}/{k}')
                following = following.write(label, master)
            columns.append(following)
        output = readout.State(d.output, tuple(columns), self.origin.output.base_total, (F(0),)*d.output.features,
            cursor=self.cursor, optimizer_steps=self.origin.output.optimizer_steps+1)
        return replace(self.origin, embedding=embedding, theta=theta, output=output, past=self.past, source_position=self.source_position,
            embedding_gradient=(), core_gradient=(F(0),)*d.slots)


@dataclass(frozen=True)
class Prediction:
    state: Pending
    values: tuple[Interval, ...]
    totals: tuple[Interval, ...]
    normalizer: Interval
    window: tokens.TokenWindow

    @property
    def features(self):
        return tuple(self.values[i] for i in self.state.origin.definition.features)

    def mass(self, label):
        origin = self.state.origin
        origin.output.index(label, 0)
        return Interval.exact(origin.definition.output.base[label])+sum(
            (Interval.exact(origin.output.parameter(label, k))*z for k, z in enumerate(self.features)), ZERO)


def begin(origin):
    if (sys.float_info.radix, sys.float_info.mant_dig, sys.float_info.rounds) != (2, 53, 1):
        raise EnclosureUnresolved('binary64 nearest-rounding environment required')
    if type(origin) is not tokens.Learner:
        raise ValueError('complete exact native unit origin required')
    d = origin.definition
    if (origin.output.unit_count or origin.cursor % d.output.update_unit or origin.embedding_gradient
            or any(origin.core_gradient) or any(origin.output.common) or origin.output.corrections):
        raise ValueError('enclosure unit requires a committed complete origin')
    return Pending(origin, (), origin.past, (ZERO,)*d.output.features, (), (), (ZERO,)*d.slots, ())
