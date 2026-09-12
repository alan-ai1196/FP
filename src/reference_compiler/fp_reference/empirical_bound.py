"""A passive exact upper on the registered frozen-context CE objective.

Identical complete source rows have one prediction for any fixed learner
endpoint. Relaxing the native grammar to arbitrary categorical predictions
per row gives the saturated multinomial likelihood. This helper has no
data acquisition, completion or installation authority.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .core import ContractError, natural
from .data_usage import ObservationRecord
from .program import SemanticRules
from .semantics import _guard, _operation


@dataclass(frozen=True)
class EmpiricalCell:
    sources: tuple[tuple[str, F], ...]
    counts: tuple[int, ...]


@dataclass(frozen=True)
class EmpiricalUpper:
    observation_ids: tuple[str, ...]
    cells: tuple[EmpiricalCell, ...]
    likelihood: F
    kind: str = field(default='complete-source-row-multinomial-likelihood-upper-v1', init=False)
    scope: str = field(default='frozen learner endpoint on these revealed source contexts; no population or future prediction claim', init=False)


def empirical_upper(records, rules, *, bit_limit):
    """Runtime must pay/retain its input use and result before using this bound.

    All originals remain owned. Row grouping is only an optimistic objective
    calculation, never a quotient of complete Runtime/learner state.
    """
    if type(records) is not tuple or not records or type(rules) is not SemanticRules:
        raise ContractError('a nonempty tuple of registered reference observations is required')
    natural(bit_limit, 'empirical bound integer limit', positive=True)
    labels, declared = len(rules.base), {source.source_id for source in rules.sources}
    counts, ids = {}, set()
    for record in records:
        if type(record) is not ObservationRecord or record.role not in ('train', 'online'):
            raise ContractError('empirical upper uses revealed legal proposal observations only')
        natural(record.target, 'revealed empirical target')
        if record.target >= labels or type(record.observation_id) is not str or record.observation_id in ids:
            raise ContractError('distinct observations and registered target alphabet required')
        ids.add(record.observation_id)
        if (type(record.sources) is not tuple or len(record.sources) != len(declared)
                or any(type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str or type(pair[1]) is not F
                       for pair in record.sources)
                or {key for key, _ in record.sources} != declared):
            raise ContractError('each objective row needs the complete exact typed source context')
        for _, value in record.sources:
            _guard(value, bit_limit=bit_limit)
        cell = counts.setdefault(record.sources, [0]*labels)
        cell[record.target] += 1
    upper = F(1)
    for cell in counts.values():
        total = sum(cell)
        _guard(F(total), bit_limit=bit_limit)
        for count in cell:
            if not count:
                continue  # zero-count factors are one, including at q=0
            factor, exponent = F(count, total), count
            while exponent:
                if exponent & 1:
                    upper = _operation(upper, factor, multiply=True, bit_limit=bit_limit)
                exponent >>= 1
                if exponent:
                    factor = _operation(factor, factor, multiply=True, bit_limit=bit_limit)
    return EmpiricalUpper(tuple(record.observation_id for record in records),
                          tuple(EmpiricalCell(context, tuple(row)) for context, row in counts.items()), upper)


def verify_empirical_upper(bound, records, rules, *, bit_limit):
    """Recompose counts and one factor per original event, without the producer.

    In particular, a copied/forged count table or a favorable raw upper value
    cannot stand in for the complete retained observations. This verifies a
    passive proposition; only Runtime can bind its result to a current class.
    """
    if (type(bound) is not EmpiricalUpper or type(bound.cells) is not tuple
            or type(bound.observation_ids) is not tuple or type(bound.likelihood) is not F
            or type(bound.kind) is not str or type(bound.scope) is not str
            or bound.kind != 'complete-source-row-multinomial-likelihood-upper-v1'
            or bound.scope != 'frozen learner endpoint on these revealed source contexts; no population or future prediction claim'):
        raise ContractError('wrong empirical upper proposition/encoding')
    if type(records) is not tuple or not records or type(rules) is not SemanticRules:
        raise ContractError('complete empirical verification inputs required')
    natural(bit_limit, 'empirical verification integer limit', positive=True)
    _guard(bound.likelihood, bit_limit=bit_limit)
    if (any(type(record) is not ObservationRecord or type(record.observation_id) is not str for record in records)
            or any(type(value) is not str for value in bound.observation_ids)
            or bound.observation_ids != tuple(record.observation_id for record in records)):
        raise ContractError('empirical upper does not cover the ordered objective identities')
    if len(set(bound.observation_ids)) != len(records):
        raise ContractError('empirical upper repeats an observation')
    table, totals = {}, {}
    declared = {source.source_id for source in rules.sources}
    for cell in bound.cells:
        if (type(cell) is not EmpiricalCell or type(cell.counts) is not tuple
                or len(cell.counts) != len(rules.base) or any(type(n) is not int or n < 0 for n in cell.counts)
                or type(cell.sources) is not tuple or len(cell.sources) != len(declared)
                or any(type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str or type(pair[1]) is not F
                       for pair in cell.sources)
                or {key for key, _ in cell.sources} != declared or cell.sources in table or not sum(cell.counts)):
            raise ContractError('empirical cells require distinct contexts and exact nonnegative counts')
        table[cell.sources] = cell.counts
        totals[cell.sources] = sum(cell.counts)
        for _, value in cell.sources:
            _guard(value, bit_limit=bit_limit)
        _guard(F(totals[cell.sources]), bit_limit=bit_limit)
    observed = {}
    check = F(1)
    for record in records:
        if type(record) is not ObservationRecord or record.role not in ('train', 'online'):
            raise ContractError('illegal observation role in empirical proof')
        if (type(record.sources) is not tuple or len(record.sources) != len(declared)
                or any(type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str or type(pair[1]) is not F
                       for pair in record.sources)
                or {key for key, _ in record.sources} != declared):
            raise ContractError('the verified observation must retain its complete exact typed source context')
        natural(record.target, 'empirical verification label')
        if record.target >= len(rules.base) or record.sources not in table:
            raise ContractError('missing complete source context or target in empirical proof')
        key = record.sources, record.target
        observed[key] = observed.get(key, 0)+1
        # One exact event factor, deliberately not the producer's exponent
        # loop. Counts are checked against the actual observations below.
        factor = F(table[record.sources][record.target], totals[record.sources])
        check = _operation(check, factor, multiply=True, bit_limit=bit_limit)
    for context, counts in table.items():
        if any(count != observed.get((context, label), 0) for label, count in enumerate(counts)):
            raise ContractError('empirical counts differ from the retained complete observations')
    if check != bound.likelihood:
        raise ContractError('raw upper differs from its exact recomposed likelihood')
    return bound
