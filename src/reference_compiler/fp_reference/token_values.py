"""Immutable captured operands for the exact logical token value tuple.

The five physical coordinates contain only exact immutable values. Capture
the actual byte/string operands, never a mutable Origin or Window wrapper.
Canonical encoders and public exports observe the complete logical tuple.
This representation neither merges causal/parameter coordinates nor grants
execution authority through a scalar value or its physical identity.
"""
from fractions import Fraction as F
import operator
import struct


_WORD = struct.Struct('<I')


def _invalid():
    from .core import ContractError
    raise ContractError('complete immutable captured token operands required')


class CapturedTokenValues(tuple):
    """A closed immutable representation; ordinary exports are exact tuples.

    Tuple backing gives this class no writable instance dictionary or slots.
    Its physical five-tuple is private implementation state. The supported
    value operations below operate on the full decoded logical sequence.
    """
    __slots__ = ()

    def __new__(cls, embedding, width, past, grid, tail=()):
        if cls is not CapturedTokenValues:
            _invalid()
        result = tuple.__new__(cls, (embedding, width, past, grid, tail))
        result.validate()
        return result

    def validate(self):
        # Validate forged tuple.__new__ instances too. No image can acquire
        # an immutable-source binding through unchecked mutable descendants.
        if type(self) is not CapturedTokenValues or tuple.__len__(self) != 5:
            _invalid()
        parts = tuple.__getitem__(self, slice(None))
        embedding, width, past, grid, tail = parts
        if (type(embedding) is not bytes or type(width) is not int or width <= 0
                or not embedding or len(embedding) % (4*width)
                or type(past) is not tuple or type(grid) is not int
                or not 0 < grid <= 1 << 32 or grid & (grid-1)
                or type(tail) is not tuple or any(type(v) is not F for v in tail)):
            _invalid()
        rows = len(embedding)//(4*width)
        if any(type(token) is not int or not 0 <= token < rows for token in past):
            _invalid()
        return parts

    def __len__(self):
        _, width, past, _, tail = self.validate()
        return len(past)*width+len(tail)

    def with_tail(self, tail):
        embedding, width, past, grid, _ = self.validate()
        return CapturedTokenValues(embedding, width, past, grid, tail)

    def __iter__(self):
        embedding, width, past, grid, tail = self.validate()
        for token in past:
            start = 4*token*width
            for channel in range(width):
                yield F(_WORD.unpack_from(embedding, start+4*channel)[0], grid)
        yield from tail

    def __getitem__(self, key):
        embedding, width, past, grid, tail = self.validate()
        inputs = len(past)*width
        size = inputs+len(tail)
        if isinstance(key, slice):
            return tuple(self[i] for i in range(*key.indices(size)))
        index = operator.index(key)
        if index < 0:
            index += size
        if not 0 <= index < size:
            raise IndexError('tuple index out of range')
        if index >= inputs:
            return tail[index-inputs]
        token, channel = past[index//width], index % width
        return F(_WORD.unpack_from(embedding, 4*(token*width+channel))[0], grid)

    def __eq__(self, other):
        self.validate()
        if type(other) is CapturedTokenValues:
            other.validate()
            if tuple.__eq__(self, other):
                return True
            other = tuple(other)
        if type(other) is tuple:
            return tuple(self) == other
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def _order(self, other, operation):
        if type(other) not in (tuple, CapturedTokenValues):
            return NotImplemented
        return operation(tuple(self), tuple(other))

    def __lt__(self, other):
        return self._order(other, operator.lt)

    def __le__(self, other):
        return self._order(other, operator.le)

    def __gt__(self, other):
        return self._order(other, operator.gt)

    def __ge__(self, other):
        return self._order(other, operator.ge)

    def __hash__(self):
        return hash(tuple(self))

    def __contains__(self, value):
        return any(item == value for item in self)

    def count(self, value):
        return sum(item == value for item in self)

    def index(self, value, *bounds):
        return tuple(self).index(value, *bounds)

    def __add__(self, other):
        if type(other) not in (tuple, CapturedTokenValues):
            return NotImplemented
        return tuple(self)+tuple(other)

    def __radd__(self, other):
        if type(other) not in (tuple, CapturedTokenValues):
            return NotImplemented
        return tuple(other)+tuple(self)

    def __mul__(self, count):
        return tuple(self)*count

    __rmul__ = __mul__

    def __reversed__(self):
        return reversed(tuple(self))

    def __repr__(self):
        return repr(tuple(self))

    def __getnewargs__(self):
        return self.validate()
