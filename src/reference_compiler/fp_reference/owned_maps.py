"""Private lossless ordered maps with immutable, augmented AVL versions.

This is storage, never resource or Compiler authority. A caller that uses the
augmentation must establish the leaf weights from its complete owned values.
All values and insertion order remain accessible; a copy shares immutable
index nodes and has an independent publication slot. Values themselves follow
their owner's existing mutation protocol (for example, paid ingress bytes).
"""
from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class _Node:
    key: object
    value: object
    weight: tuple[int, ...]
    left: _Node | None
    right: _Node | None
    height: int
    size: int
    total: tuple[int, ...]


def _height(node):
    return 0 if node is None else node.height


def _size(node):
    return 0 if node is None else node.size


def _make(key, value, weight, left=None, right=None):
    total = tuple(x + (0 if left is None else left.total[i])
        + (0 if right is None else right.total[i]) for i, x in enumerate(weight))
    return _Node(key, value, weight, left, right,
        1+max(_height(left), _height(right)), 1+_size(left)+_size(right), total)


def _left(node):
    pivot = node.right
    return _make(pivot.key, pivot.value, pivot.weight,
        _make(node.key, node.value, node.weight, node.left, pivot.left), pivot.right)


def _right(node):
    pivot = node.left
    return _make(pivot.key, pivot.value, pivot.weight, pivot.left,
        _make(node.key, node.value, node.weight, pivot.right, node.right))


def _balance(node):
    difference = _height(node.left)-_height(node.right)
    if difference > 1:
        if _height(node.left.left) < _height(node.left.right):
            node = _make(node.key, node.value, node.weight, _left(node.left), node.right)
        return _right(node)
    if difference < -1:
        if _height(node.right.right) < _height(node.right.left):
            node = _make(node.key, node.value, node.weight, node.left, _right(node.right))
        return _left(node)
    return node


def _put(node, key, value, weight):
    if node is None:
        return _make(key, value, weight)
    if key == node.key:
        return _make(key, value, weight, node.left, node.right)
    if key < node.key:
        return _balance(_make(node.key, node.value, node.weight,
            _put(node.left, key, value, weight), node.right))
    return _balance(_make(node.key, node.value, node.weight,
        node.left, _put(node.right, key, value, weight)))


def _find(node, key):
    while node is not None:
        if key == node.key:
            return node
        node = node.left if key < node.key else node.right
    raise KeyError(key)


def _remove(node, key):
    if node is None:
        raise KeyError(key)
    if key < node.key:
        return _balance(_make(node.key, node.value, node.weight,
            _remove(node.left, key), node.right))
    if key > node.key:
        return _balance(_make(node.key, node.value, node.weight,
            node.left, _remove(node.right, key)))
    if node.left is None:
        return node.right
    if node.right is None:
        return node.left
    successor = node.right
    while successor.left is not None:
        successor = successor.left
    return _balance(_make(successor.key, successor.value, successor.weight,
        node.left, _remove(node.right, successor.key)))


def _walk(node):
    stack = []
    while stack or node is not None:
        if node is not None:
            stack.append(node)
            node = node.left
        else:
            node = stack.pop()
            yield node
            node = node.right


@dataclass(frozen=True, slots=True)
class _Entry:
    ordinal: int
    key: object
    value: object


@dataclass(frozen=True, slots=True)
class _Version:
    lookup: _Node | None
    order: _Node | None
    next_ordinal: int


class OwnedMap(MutableMapping):
    """A serialized private publication slot over complete immutable indices.

    String keys or integer keys are used in a given map, never mixed. Ordinary
    assignment is for unweighted maps. A trusted accounting caller explicitly
    supplies a nonnegative exact weight for each weighted insertion/replacement.
    All fallible node preparation precedes the one version-pointer assignment.
    """
    __slots__ = ('_version', '_width')

    def __init__(self, entries=(), *, width=0):
        if type(width) is not int or width < 0:
            raise ValueError('nonnegative augmentation width required')
        self._version, self._width = _Version(None, None, 0), width
        self.update(entries)

    def __len__(self):
        return _size(self._version.lookup)

    def __getitem__(self, key):
        return _find(self._version.lookup, key).value.value

    def __iter__(self):
        return (node.value.key for node in _walk(self._version.order))

    def items(self):
        return ((node.value.key, node.value.value) for node in _walk(self._version.order))

    def values(self):
        return (node.value.value for node in _walk(self._version.order))

    def __setitem__(self, key, value):
        self.set_weighted(key, value, ())

    def set_weighted(self, key, value, weight):
        if type(key) not in (str, int):
            raise TypeError('owned map keys must be exact strings or integers')
        if type(weight) is not tuple or len(weight) != self._width or any(type(x) is not int or x < 0 for x in weight):
            raise ValueError('complete nonnegative exact leaf weight required')
        before = self._version
        if before.lookup is not None and type(key) is not type(before.lookup.key):
            raise TypeError('one owned map cannot mix key types')
        try:
            ordinal = _find(before.lookup, key).value.ordinal
            next_ordinal = before.next_ordinal
        except KeyError:
            ordinal, next_ordinal = before.next_ordinal, before.next_ordinal+1
        entry = _Entry(ordinal, key, value)
        lookup = _put(before.lookup, key, entry, weight)
        order = _put(before.order, ordinal, entry, ())
        self._version = _Version(lookup, order, next_ordinal)

    def __delitem__(self, key):
        before = self._version
        ordinal = _find(before.lookup, key).value.ordinal
        lookup = _remove(before.lookup, key)
        order = _remove(before.order, ordinal)
        self._version = _Version(lookup, order, before.next_ordinal)

    def copy(self):
        result = object.__new__(OwnedMap)
        result._version, result._width = self._version, self._width
        return result

    @property
    def total(self):
        root = self._version.lookup
        return (0,)*self._width if root is None else root.total


class OwnedLog(Sequence):
    """Immutable complete append history; append returns an independent root.

    Reverse links give constant node work per append, without copying old
    events. Full forward iteration constructs the requested diagnostic order.
    """
    __slots__ = ('_tail', '_length')

    def __init__(self):
        self._tail, self._length = None, 0

    def __len__(self):
        return self._length

    def appended(self, value):
        result = object.__new__(OwnedLog)
        result._tail, result._length = (value, self._tail), self._length+1
        return result

    def __iter__(self):
        values, tail = [], self._tail
        while tail is not None:
            values.append(tail[0])
            tail = tail[1]
        return reversed(values)

    def __getitem__(self, index):
        if type(index) is slice:
            return tuple(self)[index]
        if type(index) is not int:
            raise TypeError('integer event position required')
        position = index if index >= 0 else self._length+index
        if not 0 <= position < self._length:
            raise IndexError(index)
        tail = self._tail
        for _ in range(self._length-position-1):
            tail = tail[1]
        return tail[0]
