"""Finite-alphabet registered moment queries over Runtime-owned legal records.

No callback, caller-computed answer or caller-supplied data role is accepted.
These are pure query computations, not certificates. The current Runtime also
declares raw revealed train/online access; a query's bit count is not a bound on
information in that full observation/learner interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError, QueryError, natural
from .data_usage import ObservationRecord, source_mapping
from .program import SemanticRules, name, rational
from .semantics import _guard, _operation
from .token_sources import TokenAtomFamily, TokenSourceTypes


@dataclass(frozen=True)
class Moment:
    sources: tuple[str, ...]
    target_atom: int | None = None

    def __post_init__(self):
        object.__setattr__(self, 'sources', tuple(name(v, 'moment source') for v in self.sources))
        if self.target_atom is not None:
            natural(self.target_atom, 'moment target atom')


@dataclass(frozen=True)
class QuerySpec:
    query_id: str
    coordinates: tuple[Moment, ...]
    lower: tuple[F, ...]
    upper: tuple[F, ...]
    bits: int
    max_records: int

    def __post_init__(self):
        name(self.query_id, 'query ID')
        coords = tuple(self.coordinates)
        lo = tuple(rational(v, 'query lower bound') for v in self.lower)
        hi = tuple(rational(v, 'query upper bound') for v in self.upper)
        if not coords or any(type(c) is not Moment for c in coords) or len(coords) != len(lo) or len(lo) != len(hi):
            raise ContractError('query coordinates and every output range must be fixed')
        if any(a >= b for a, b in zip(lo, hi)):
            raise ContractError('query ranges must have positive width')
        natural(self.bits, 'query precision bits', positive=True)
        natural(self.max_records, 'query record limit', positive=True)
        object.__setattr__(self, 'coordinates', coords)
        object.__setattr__(self, 'lower', lo)
        object.__setattr__(self, 'upper', hi)

    def validate(self, rules: SemanticRules, bit_limit: int):
        names = TokenSourceTypes(rules.sources) if type(rules.sources) is TokenAtomFamily else {s.source_id for s in rules.sources}
        if self.bits >= bit_limit:
            raise ContractError('query levels exceed the registered integer work representation')
        if any(any(source not in names for source in c.sources) or (c.target_atom is not None and c.target_atom >= len(rules.base)) for c in self.coordinates):
            raise ContractError('query uses an undeclared source or target atom')

    def work(self, record_count: int) -> int:
        return record_count*sum(len(c.sources)+2 for c in self.coordinates)+10*len(self.coordinates)+1


@dataclass(frozen=True)
class QueryResult:
    query_id: str
    status: str
    indices: tuple[int, ...]
    values: tuple[F, ...]
    reason: str


@dataclass(frozen=True)
class QueryRecord:
    cursor: int
    observation_ids: tuple[str, ...]
    result: QueryResult


def quantize(value: F, lo: F, hi: F, bits: int, *, bit_limit: int) -> tuple[int, F]:
    """Exact nearest-level, ties-to-even quantization; at most 2**bits outputs."""
    natural(bits, 'query precision', positive=True)
    value, lo, hi = (rational(v, 'query arithmetic') for v in (value, lo, hi))
    if not lo <= value <= hi or lo >= hi:
        raise QueryError('computed query lies outside its registered range')
    if bits >= bit_limit:
        raise QueryError('query precision exceeds its registered integer representation')
    add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
    mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
    levels = (1 << bits)-1
    width = add(hi, -lo)
    inverse = F(1)/width
    _guard(inverse, bit_limit=bit_limit)
    scaled = mul(mul(add(value, -lo), inverse), F(levels))
    index, remainder = divmod(scaled.numerator, scaled.denominator)
    twice = remainder*2
    if twice > scaled.denominator or (twice == scaled.denominator and index % 2):
        index += 1
    return index, add(lo, mul(width, F(index, levels)))


def evaluate_query(spec: QuerySpec, records: tuple[ObservationRecord, ...], *, bit_limit: int) -> QueryResult:
    if not 0 < len(records) <= spec.max_records or any(r.target is None or r.role not in ('train', 'online') for r in records):
        raise QueryError('query needs a bounded nonempty set of revealed legal observations')
    add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
    mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
    indices, values = [], []
    for coord, lo, hi in zip(spec.coordinates, spec.lower, spec.upper):
        total = F(0)
        for record in records:
            product = F(1) if coord.target_atom is None else F(record.target == coord.target_atom)
            sources = source_mapping(record.sources)
            for source in coord.sources:
                product = mul(product, sources[source])
            total = add(total, product)
        mean = mul(total, F(1, len(records)))
        index, value = quantize(mean, lo, hi, spec.bits, bit_limit=bit_limit)
        indices.append(index)
        values.append(value)
    return QueryResult(spec.query_id, 'ANSWERED', tuple(indices), tuple(values), 'exact registered quantization')
