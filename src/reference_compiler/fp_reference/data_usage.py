"""Registered exogenous observation identities, causal reads and retained use.

This recovery supports exact, revealed train/online data access. Future targets
are supplied only after prediction. A finite identity schedule is a provenance
contract, not proof that an external producer sampled independent observations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from .core import ContractError, QueryError, natural
from .ingress import IngressContract
from .program import SemanticRules, name, rational
from .token_sources import TokenAtomFamily, TokenSourceReads, TokenContext, TokenValues


@dataclass(frozen=True)
class StreamSpec:
    stream_id: str
    role: str
    observation_ids: tuple[str, ...]

    def __post_init__(self):
        name(self.stream_id, 'stream ID')
        if self.role not in ('train', 'online', 'validation', 'test'):
            raise ContractError('unregistered data role')
        ids = tuple(name(value, 'observation ID') for value in self.observation_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ContractError('nonempty distinct physical observation identities required')
        object.__setattr__(self, 'observation_ids', ids)


@dataclass(frozen=True)
class SourceRead:
    source_id: str
    kind: str
    index: int
    lag: int

    def __post_init__(self):
        name(self.source_id, 'source evaluation ID')
        if self.kind not in ('input', 'target_atom', 'target_missing'):
            raise ContractError('unimplemented causal source evaluation rule')
        natural(self.index, 'input coordinate or target atom')
        natural(self.lag, 'source lag')
        if self.kind in ('target_atom', 'target_missing') and self.lag == 0:
            raise ContractError('the current target is not a primitive score-time source')
        if self.kind == 'target_missing' and self.index != 0:
            raise ContractError('missing-history predicate has no selectable token coordinate')


@dataclass(frozen=True)
class StochasticStreamLaw:
    """Explicit external assumption, never inferred from finite observations.

    The producer is a stochastic branch-invariant exogenous process relative
    to the complete Runtime filtration before each incoming context. An
    exposed deterministic future tape or seed is not fresh randomness under
    this declaration. The conditional mean-null is defined by each admitted
    comparison; this object neither asserts that null nor proves the producer.
    """
    assumption_id: str
    family: str = field(default='branch-invariant-exogenous-stochastic-process-v1', init=False)

    def __post_init__(self):
        name(self.assumption_id, 'external stochastic-law assumption')


@dataclass(frozen=True)
class DataContract:
    streams: tuple[StreamSpec, ...]
    active_stream: str
    input_upper: tuple[F, ...]
    source_reads: tuple[SourceRead, ...] | TokenSourceReads
    access_id: str = 'bounded-exact-revealed-train-online-v2'
    stream_law: str | StochasticStreamLaw = 'declared-exogenous-no-probability-guarantee'
    ingress: IngressContract = field(default_factory=IngressContract)

    def __post_init__(self):
        streams = tuple(self.streams)
        if not streams or any(type(s) is not StreamSpec for s in streams):
            raise ContractError('immutable stream declarations required')
        if len({s.stream_id for s in streams}) != len(streams):
            raise ContractError('duplicate stream ID')
        all_ids = [value for stream in streams for value in stream.observation_ids]
        if len(set(all_ids)) != len(all_ids):
            raise ContractError('an observation cannot be relabelled across data splits')
        name(self.active_stream, 'active stream ID')
        active = next((s for s in streams if s.stream_id == self.active_stream), None)
        if active is None or active.role not in ('train', 'online'):
            raise ContractError('reporting labels cannot drive ordinary learning or discovery')
        if type(self.source_reads) is TokenSourceReads:
            reads = self.source_reads
            reads.__post_init__()
            if self.input_upper:
                raise ContractError('indexed token sources use only owned past targets')
        else:
            reads = tuple(self.source_reads)
            if any(type(r) is not SourceRead for r in reads) or len({r.source_id for r in reads}) != len(reads):
                raise ContractError('distinct registered source evaluators required')
        if self.access_id != 'bounded-exact-revealed-train-online-v2' or type(self.ingress) is not IngressContract:
            raise ContractError('registered bounded exact ingress is required; no raw-value or query-only bypass')
        if not (type(self.stream_law) is StochasticStreamLaw or
                type(self.stream_law) is str and self.stream_law == 'declared-exogenous-no-probability-guarantee'):
            raise ContractError('use the supported explicit stochastic assumption or the deterministic no-guarantee declaration')
        object.__setattr__(self, 'streams', streams)
        object.__setattr__(self, 'input_upper', tuple(rational(v, 'input range') for v in self.input_upper))
        object.__setattr__(self, 'source_reads', reads)

    @property
    def active(self):
        return next(s for s in self.streams if s.stream_id == self.active_stream)

    def validate(self, rules: SemanticRules):
        if type(self.source_reads) is TokenSourceReads:
            self.source_reads.__post_init__()
            if rules.sources != self.source_reads.family or type(rules.sources) is not TokenAtomFamily or len(rules.base) != rules.sources.vocabulary or self.input_upper:
                raise ContractError('indexed token readers and complete semantic family differ')
            return
        if type(rules.sources) is TokenAtomFamily:
            raise ContractError('indexed token family requires its complete registered reader')
        if {r.source_id for r in self.source_reads} != {s.source_id for s in rules.sources}:
            raise ContractError('every source needs its registered causal evaluation rule')
        specs = {s.source_id: s for s in rules.sources}
        for read in self.source_reads:
            # Passive frozen metadata is not authority; validate its closed
            # rule again before Runtime adopts the actual causal interface.
            read.__post_init__()
            if read.kind == 'input':
                if read.index >= len(self.input_upper):
                    raise ContractError('source reads an undeclared input coordinate')
                upper = self.input_upper[read.index]
            elif read.kind == 'target_atom':
                if read.index >= len(rules.base):
                    raise ContractError('source reads an undeclared target atom')
                upper = F(1)
            else:
                upper = F(1)
            if read.lag != specs[read.source_id].availability_delay or upper > specs[read.source_id].upper:
                raise ContractError('source evaluator delay/range disagrees with native registration')


@dataclass(frozen=True)
class ObservationRecord:
    observation_id: str
    stream_id: str
    role: str
    cursor: int
    inputs: tuple[F, ...]
    sources: tuple[tuple[str, F], ...] | TokenContext
    target: int | None


def read_sources(contract: DataContract, cursor: int, inputs: tuple[F, ...],
                 history: tuple[ObservationRecord, ...]) -> tuple[tuple[str, F], ...] | TokenContext:
    if len(history) != cursor or any(record.cursor != i or record.target is None for i, record in enumerate(history)):
        raise ContractError('causal source history is not a continuous revealed prefix')
    if type(contract.source_reads) is TokenSourceReads:
        if inputs:
            raise ContractError('external history atoms cannot replace owned token history')
        family = contract.source_reads.family
        return TokenContext(family, cursor, tuple(
            family.vocabulary if lag > cursor else history[cursor-lag].target
            for lag in range(1, family.context+1)))
    values = []
    for read in contract.source_reads:
        origin = cursor-read.lag
        if origin < 0:
            # Missingness is an explicitly declared causal predicate. Existing
            # input/token atoms keep their original zero-prefix semantics.
            value = F(read.kind == 'target_missing')
        elif read.kind == 'input':
            value = inputs[read.index] if read.lag == 0 else history[origin].inputs[read.index]
        elif read.kind == 'target_missing':
            value = F(0)
        else:
            value = F(history[origin].target == read.index)
        values.append((read.source_id, value))
    return tuple(values)


def source_mapping(sources):
    return TokenValues(sources) if type(sources) is TokenContext else dict(sources)


def indexed_source_read_work(contract, cursor):
    """Fund history-copy/check visits, lag decoding and context validation.

    These are reference work charges, not processor cycles. Query/prediction
    decoder validations have their own additional charges at the call site.
    """
    if type(contract.source_reads) is not TokenSourceReads:
        raise ContractError('registered indexed source reader required')
    natural(cursor, 'source read cursor')
    return 2*cursor+3*(contract.source_reads.family.context+1)


@dataclass(frozen=True)
class DataUse:
    observation_ids: tuple[str, ...]
    purpose: str
    consumer: str
    cursor: int


class DataUsageLedger:
    """Retained use facts only; no public helper can authorize fresh evidence."""

    def __init__(self):
        self._uses: list[DataUse] = []

    def record(self, records: tuple[ObservationRecord, ...], purpose: str, consumer: str, cursor: int):
        if purpose not in ('ordinary', 'proposal', 'profile', 'persistence', 'report'):
            raise QueryError('unregistered observation use')
        name(consumer, 'data consumer')
        natural(cursor, 'data-use cursor')
        roles = ('validation', 'test') if purpose == 'report' else ('train', 'online')
        if not records or any(r.role not in roles or r.target is None for r in records):
            raise QueryError('revealed records must keep their registered learning or reporting role')
        ids = tuple(r.observation_id for r in records)
        if len(set(ids)) != len(ids):
            raise QueryError('duplicate physical observation in one data use')
        self._uses.append(DataUse(ids, purpose, consumer, cursor))

    def snapshot(self) -> tuple[DataUse, ...]:
        return tuple(self._uses)
