"""Closed lossless encoding of the complete delayed token-indicator family.

These dataclasses are passive metadata/data. Only Runtime's read_sources
derives a live context from its owned revealed history. They do not acquire
targets, publish predictions or issue a resource/bridge certificate.
"""
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction as F
import sys

from .core import ContractError, natural


@dataclass(frozen=True)
class TokenAtomFamily:
    vocabulary: int
    context: int
    type_id: str = 'f'

    def __post_init__(self):
        if set(vars(self)) != {'vocabulary', 'context', 'type_id'}:
            raise ContractError('closed token source-family fields required')
        natural(self.vocabulary, 'token vocabulary', positive=True)
        natural(self.context, 'token context', positive=True)
        if self.vocabulary < 2 or type(self.type_id) is not str or not self.type_id:
            raise ContractError('at least two token labels and a fixed source type required')
        if (self.vocabulary+1)*self.context > sys.maxsize:
            from .semantics import ArithmeticUnresolved
            raise ArithmeticUnresolved('indexed source family exceeds this realization index range')

    def __len__(self):
        return (self.vocabulary+1)*self.context

    def __getitem__(self, index):
        if type(index) is not int or not 0 <= index < len(self):
            raise IndexError(index)
        from .program import SourceSpec
        lag, token = divmod(index, self.vocabulary+1)
        return SourceSpec(f'lag{lag+1}/token{token}', self.type_id, lag+1, F(1))

    def coordinates(self, source_id):
        if type(source_id) is not str or len(source_id) > len(str(self.context))+len(str(self.vocabulary))+9:
            raise ContractError('undeclared token source ID')
        left, separator, right = source_id.partition('/token')
        if separator != '/token' or not left.startswith('lag'):
            raise ContractError('undeclared token source ID')
        try:
            lag, token = int(left[3:]), int(right)
        except ValueError as error:
            raise ContractError('undeclared token source ID') from error
        if not 1 <= lag <= self.context or not 0 <= token <= self.vocabulary or source_id != f'lag{lag}/token{token}':
            raise ContractError('undeclared token source ID')
        return lag, token

    def source_type(self, source_id):
        self.coordinates(source_id)
        return self.type_id


@dataclass(frozen=True)
class TokenSourceReads:
    family: TokenAtomFamily

    def __post_init__(self):
        if set(vars(self)) != {'family'}:
            raise ContractError('closed token source-reader fields required')
        if type(self.family) is not TokenAtomFamily:
            raise ContractError('closed complete token source family required')
        self.family.__post_init__()


@dataclass(frozen=True)
class TokenContext:
    family: TokenAtomFamily
    position: int
    past: tuple[int, ...]

    def __post_init__(self):
        if set(vars(self)) != {'family', 'position', 'past'}:
            raise ContractError('closed indexed token-context fields required')
        if type(self.family) is not TokenAtomFamily:
            raise ContractError('closed token family required')
        self.family.__post_init__()
        natural(self.position, 'original source position')
        if type(self.past) is not tuple or len(self.past) != self.family.context:
            raise ContractError('every retained token lag must be encoded')
        for lag, value in enumerate(self.past, 1):
            natural(value, 'retained token label')
            if value > self.family.vocabulary or (value == self.family.vocabulary) != (lag > self.position):
                raise ContractError('PAD must occur exactly before the original stream origin')


class TokenValues(Mapping):
    """Transient read-only complete scalar interface; retained data is context."""
    __slots__ = ('context',)

    def __init__(self, context):
        if type(context) is not TokenContext:
            raise ContractError('complete indexed token context required')
        context.__post_init__()
        self.context = context

    def __getitem__(self, source_id):
        lag, token = self.context.family.coordinates(source_id)
        return F(int(self.context.past[lag-1] == token))

    def __iter__(self):
        for spec in self.context.family:
            yield spec.source_id

    def __len__(self):
        return len(self.context.family)


class TokenSourceTypes:
    __slots__ = ('family',)

    def __init__(self, family):
        self.family = family

    def __contains__(self, source_id):
        try:
            self.family.coordinates(source_id)
            return True
        except ContractError:
            return False

    def __getitem__(self, source_id):
        return self.family.source_type(source_id)


class TokenSourceBounds:
    __slots__ = ('family',)

    def __init__(self, family):
        self.family = family

    def __getitem__(self, source_id):
        from .semantics import Interval
        self.family.coordinates(source_id)
        return Interval(F(0), F(1))
