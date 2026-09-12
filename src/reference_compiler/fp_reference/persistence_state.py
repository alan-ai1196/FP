"""Runtime-owned reference evidence records, not paired AMP/install tokens."""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .data_usage import StochasticStreamLaw
from .learner import ReferenceLearnerState
from .numerics import LogInterval
from .persistence import PersistenceRule


@dataclass(frozen=True)
class AlphaAllocation:
    allocation_id: str
    identity_id: str
    alpha: F
    cursor: int
    law: StochasticStreamLaw
    path: str = field(default='exact-reference', init=False)


@dataclass(frozen=True)
class ReferencePersistenceIdentity:
    identity_id: str
    rule: PersistenceRule
    allocation_id: str
    base_lineage_id: str
    candidate_lineage_id: str
    base_program_id: str
    candidate_program_id: str
    initial_base: ReferenceLearnerState
    initial_candidate: ReferenceLearnerState
    current_base: ReferenceLearnerState
    current_candidate: ReferenceLearnerState
    start_cursor: int
    cursor: int
    epoch_events: int
    epochs_completed: int
    gain_lower_sum: F
    gain_upper_sum: F
    wealth: F
    ratio_bound: F | None
    crossing_cursor: int | None
    crossing_wealth: F | None
    status: str
    owner: str
    object_id: str
    generation: int
    reason: str = ''


@dataclass(frozen=True)
class ReferencePersistenceEvent:
    identity_id: str
    observation_id: str
    cursor: int
    base_lineage_id: str
    candidate_lineage_id: str
    base_probability: F
    candidate_probability: F
    gain: LogInterval
    epoch_finished: bool
    wealth_before: F
    wealth_after: F


@dataclass(frozen=True)
class ReferencePersistenceResult:
    status: str
    identity_id: str | None
    alpha_spent: F
    epochs_completed: int
    wealth_lower: F
    crossing_cursor: int | None
    reason: str
    authority_scope: str = field(default='conditional reference mean-null evidence only; no paired AMP or installation authority', init=False)
