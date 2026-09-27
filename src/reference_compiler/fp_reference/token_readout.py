"""Exact passive refinement of an untied positive linear readout and its U.

No Runtime, AMP, ingress, freshness or installation authority. Immutable AVL
indexes implement value storage, not semantic architecture actions. All
native parameters and pending gradients remain individually decodable.
Refinement is proved for initialized states and their pure transitions;
passive dataclass construction is not a certificate of a reached state.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F


@dataclass(frozen=True)
class Node:
    key: int
    value: int
    left: 'Node | None'
    right: 'Node | None'
    height: int
    nodes: int
    weight: int
    total: int


def field(node, name):
    return getattr(node, name) if node is not None else 0


def node(key, value, left=None, right=None):
    return Node(key, value, left, right, 1+max(field(left, 'height'), field(right, 'height')),
        1+field(left, 'nodes')+field(right, 'nodes'), value+field(left, 'weight')+field(right, 'weight'),
        key*value+field(left, 'total')+field(right, 'total'))


def left(root):
    pivot = root.right
    return node(pivot.key, pivot.value, node(root.key, root.value, root.left, pivot.left), pivot.right)


def right(root):
    pivot = root.left
    return node(pivot.key, pivot.value, pivot.left, node(root.key, root.value, pivot.right, root.right))


def balance(root):
    difference = field(root.left, 'height')-field(root.right, 'height')
    if difference > 1:
        if field(root.left.left, 'height') < field(root.left.right, 'height'):
            root = node(root.key, root.value, left(root.left), root.right)
        return right(root)
    if difference < -1:
        if field(root.right.right, 'height') < field(root.right.left, 'height'):
            root = node(root.key, root.value, root.left, right(root.right))
        return left(root)
    return root


def get(root, key):
    while root is not None:
        if key == root.key:
            return root.value
        root = root.left if key < root.key else root.right
    return None


def put(root, key, value):
    """Persistent exact ordered-map update; None deletes a key."""
    if root is None:
        return None if value is None else node(key, value)
    if key < root.key:
        return balance(node(root.key, root.value, put(root.left, key, value), root.right))
    if key > root.key:
        return balance(node(root.key, root.value, root.left, put(root.right, key, value)))
    if value is not None:
        return node(key, value, root.left, root.right)
    if root.left is None:
        return root.right
    if root.right is None:
        return root.left
    following = root.right
    while following.left is not None:
        following = following.left
    return balance(node(following.key, following.value, root.left, put(root.right, following.key, None)))


def frequency(root, key, delta):
    following = (get(root, key) or 0)+delta
    if following < 0:
        raise ValueError('negative indexed multiplicity')
    return put(root, key, following or None)


def above(root, threshold):
    """Return multiplicity and weighted sum of keys strictly above threshold."""
    count = total = 0
    while root is not None:
        if root.key > threshold:
            count += root.value+field(root.right, 'weight')
            total += root.key*root.value+field(root.right, 'total')
            root = root.left
        else:
            root = root.right
    return count, total


def natural(value, positive=False):
    if type(value) is not int or value < int(positive):
        raise ValueError('exact nonnegative/positive integer required')
    return value


def exact(value, positive=False):
    if type(value) is not F or value < 0 or (positive and value == 0):
        raise ValueError('exact nonnegative/positive Fraction required')
    return value


@dataclass(frozen=True)
class Spec:
    base: tuple[F, ...]
    features: int
    grid_bits: int
    learning_rate: F
    update_unit: int

    def __post_init__(self):
        if type(self.base) is not tuple or len(self.base) < 2:
            raise ValueError('complete fixed readout bases required')
        for b in self.base:
            exact(b, positive=True)
        natural(self.features, positive=True)
        natural(self.grid_bits)
        exact(self.learning_rate)
        natural(self.update_unit, positive=True)

    @property
    def labels(self):
        return len(self.base)

    @property
    def grid(self):
        return 1 << self.grid_bits


@dataclass(frozen=True)
class Column:
    default: int
    offset: int
    # label -> raw value, for exceptions to the default raw value.
    labels: Node | None
    # raw value -> multiplicity, including every implicit default label.
    values: Node

    def raw(self, label):
        value = get(self.labels, label)
        return self.default if value is None else value

    def master(self, label):
        return max(0, self.raw(label)-self.offset)

    def total(self):
        count, weighted = above(self.values, self.offset)
        return weighted-self.offset*count

    def write(self, label, master):
        natural(master)
        old = self.raw(label)
        default_master = max(0, self.default-self.offset)
        new = self.default if master == default_master else self.offset+master
        if old == new:
            return self
        labels = put(self.labels, label, None if new == self.default else new)
        values = frequency(frequency(self.values, old, -1), new, 1)
        return Column(self.default, self.offset, labels, values)


@dataclass(frozen=True)
class State:
    spec: Spec
    columns: tuple[Column, ...]
    base_total: F
    common: tuple[F, ...]
    corrections: tuple[tuple[int, tuple[F, ...]], ...] = ()
    unit_count: int = 0
    cursor: int = 0
    optimizer_steps: int = 0

    def parameter(self, label, feature):
        self.index(label, feature)
        return F(self.columns[feature].master(label), self.spec.grid)

    def gradient(self, label, feature):
        self.index(label, feature)
        correction = next((row[feature] for y, row in self.corrections if y == label), F(0))
        return self.common[feature]-correction

    def index(self, label, feature):
        natural(label)
        natural(feature)
        if label >= self.spec.labels or feature >= self.spec.features:
            raise ValueError('undeclared native parameter coordinate')

    def predict(self, features):
        if self.unit_count >= self.spec.update_unit:
            raise ValueError('registered optimizer commit is due')
        if type(features) is not tuple or len(features) != self.spec.features:
            raise ValueError('complete feature tuple required')
        for z in features:
            exact(z)
        totals = tuple(F(column.total(), self.spec.grid) for column in self.columns)
        normalizer = self.base_total+sum((w*z for w, z in zip(totals, features)), F(0))
        return Prediction(self, features, totals, normalizer)

    def observe(self, prediction, target):
        if type(prediction) is not Prediction or prediction.state is not self:
            raise ValueError('prediction lost its actual complete predecessor')
        self.index(target, 0)
        if self.unit_count >= self.spec.update_unit:
            raise ValueError('registered optimizer commit is due')
        expected = self.predict(prediction.features)
        if (type(prediction.normalizer) is not F or prediction.column_totals != expected.column_totals
                or prediction.normalizer != expected.normalizer):
            raise ValueError('readout cache differs from its complete actual parameters/features')
        mass = prediction.mass(target)
        common = tuple(a+z/prediction.normalizer for a, z in zip(self.common, prediction.features))
        corrections = dict(self.corrections)
        old = corrections.get(target, (F(0),)*self.spec.features)
        corrections[target] = tuple(a+z/mass for a, z in zip(old, prediction.features))
        adjoints = tuple(w/prediction.normalizer-self.parameter(target, i)/mass
            for i, w in enumerate(prediction.column_totals))
        return replace(self, common=common, corrections=tuple(sorted(corrections.items())),
            unit_count=self.unit_count+1, cursor=self.cursor+1), adjoints

    def commit(self):
        if self.unit_count != self.spec.update_unit or self.cursor % self.spec.update_unit:
            raise ValueError('commit outside the complete registered update unit')
        scale = self.spec.grid*self.spec.learning_rate/self.spec.update_unit
        columns = []
        for feature, column in enumerate(self.columns):
            alpha = scale*self.common[feature]
            shift = -(-alpha.numerator//alpha.denominator)
            following = replace(column, offset=column.offset+shift)
            for label, correction in self.corrections:
                # Use the old master and the combined signed step. Projecting
                # a common decrement before adding a target correction is false.
                value = column.master(label)-alpha+scale*correction[feature]
                master = max(0, value.numerator//value.denominator)
                following = following.write(label, master)
            if following.values.weight != self.spec.labels:
                raise ValueError('column index lost native label multiplicity')
            columns.append(following)
        return State(self.spec, tuple(columns), self.base_total, (F(0),)*self.spec.features,
            cursor=self.cursor, optimizer_steps=self.optimizer_steps+1)


@dataclass(frozen=True)
class Prediction:
    state: State
    features: tuple[F, ...]
    column_totals: tuple[F, ...]
    normalizer: F

    def mass(self, label):
        self.state.index(label, 0)
        return self.state.spec.base[label]+sum((self.state.parameter(label, i)*z
            for i, z in enumerate(self.features)), F(0))

    def probability(self, label):
        return self.mass(label)/self.normalizer


def initialize(spec, defaults, overrides=()):
    """Explicit grid initializer; overrides are (label, feature, integer master)."""
    if type(spec) is not Spec or type(defaults) is not tuple or len(defaults) != spec.features:
        raise ValueError('closed complete readout initialization required')
    spec.__post_init__()
    columns = []
    for value in defaults:
        natural(value)
        columns.append(Column(value, 0, None, node(value, spec.labels)))
    seen = set()
    for label, feature, master in overrides:
        natural(label)
        natural(feature)
        natural(master)
        if label >= spec.labels or feature >= spec.features or (label, feature) in seen:
            raise ValueError('duplicate or foreign initialized coordinate')
        seen.add((label, feature))
        columns[feature] = columns[feature].write(label, master)
    return State(spec, tuple(columns), sum(spec.base, F(0)), (F(0),)*spec.features)
