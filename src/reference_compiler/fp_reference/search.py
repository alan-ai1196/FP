"""Finite reachable reference decision classes and retained solver records.

This is a fixed-state empirical CE comparison of registered constructor
endpoints on logged contexts. It is not a population, future-trajectory,
AMP, persistence, physical-install or arbitrary-value optimum certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError
from .data_usage import DataContract, ObservationRecord
from .learner import ReferenceLearnerState
from .native_search import GrammarCursor, GrammarLimits
from .program import Program, name
from .semantics import _operation, evaluate


@dataclass(frozen=True)
class ReferenceSearchSpec:
    search_name: str
    grammar: GrammarLimits
    observation_ids: tuple[str, ...]
    profile_id: str | None = None
    objective_id: str = 'fixed-state-empirical-ce-on-logged-contexts-v1'

    def __post_init__(self):
        name(self.search_name, 'reference search name')
        if type(self.grammar) is not GrammarLimits:
            raise ContractError('a complete finite native grammar declaration is required')
        ids = tuple(name(value, 'objective observation ID') for value in self.observation_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ContractError('the reference objective uses a fixed nonempty set of distinct observation IDs')
        object.__setattr__(self, 'observation_ids', ids)
        if self.profile_id is not None:
            name(self.profile_id, 'reference value constructor profile')
        if self.objective_id != 'fixed-state-empirical-ce-on-logged-contexts-v1':
            raise ContractError('unimplemented reference objective')

    def validate(self, data: DataContract, profiles, construction_limits):
        if any(getattr(self.grammar, key) > construction_limits[key] for key in construction_limits):
            raise ContractError('search grammar exceeds its enclosing native construction declaration')
        roles = {obs: stream.role for stream in data.streams for obs in stream.observation_ids}
        if any(roles.get(obs) not in ('train', 'online') for obs in self.observation_ids):
            raise ContractError('reporting or undeclared labels cannot drive reference search')
        if self.profile_id is not None and self.profile_id not in {p.profile_id for p in profiles}:
            raise ContractError('search refers to an unregistered value constructor')


@dataclass(frozen=True)
class ComparisonRow:
    ordinal: int
    program: Program
    program_id: str
    candidate_id: str | None
    status: str
    learner: ReferenceLearnerState | None
    likelihood: F | None
    reason: str


@dataclass(frozen=True)
class ReferenceSearchSession:
    search_id: str
    decision_class_id: str
    spec: ReferenceSearchSpec
    ordinary_cursor: int
    base_lineage_id: str
    base_state: ReferenceLearnerState
    base_likelihood: F | None
    expected_revision: int
    cursor: GrammarCursor
    rows: tuple[ComparisonRow, ...]
    best_candidate_id: str
    best_likelihood: F | None
    unresolved: int
    status: str
    owner: str
    object_id: str
    generation: int
    proof_id: str | None = None
    reason: str = ''


@dataclass(frozen=True)
class ReferenceSearchResult:
    status: str
    search_id: str | None
    decision_class_id: str
    programs_compared: int
    unresolved_programs: int
    best_candidate_id: str | None
    best_likelihood: F | None
    proof_id: str | None
    reason: str


def likelihood(program: Program, rules, learner: ReferenceLearnerState,
               records: tuple[ObservationRecord, ...], *, bit_limit: int) -> F:
    """Exact ordering of equal-sized empirical CE sums, with no floating log.

    Every context uses the same frozen delayed/parameter state. The body
    computed by evaluate does not advance an ordinary or profile trajectory.
    The owning Runtime handles legal acquisition, work and result residency.
    """
    value = F(1)
    for record in records:
        if record.target is None or record.role not in ('train', 'online'):
            raise ContractError('reference objective requires revealed legal observations')
        prediction = evaluate(program, rules, learner.theta, dict(record.sources), learner.delayed, bit_limit=bit_limit)
        value = _operation(value, prediction.probabilities[record.target], multiply=True, bit_limit=bit_limit)
    return value


def compare_likelihoods(left: F, right: F, *, bit_limit: int) -> int:
    # The cross-products are also charged reference integer operations, not an
    # unchecked comparison that can silently exceed the arithmetic model.
    a = _operation(F(left.numerator), F(right.denominator), multiply=True, bit_limit=bit_limit)
    b = _operation(F(right.numerator), F(left.denominator), multiply=True, bit_limit=bit_limit)
    return int(a > b)-int(a < b)
