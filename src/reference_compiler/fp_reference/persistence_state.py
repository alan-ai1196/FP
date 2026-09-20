"""Runtime-owned same-path evidence records, not AMP/install tokens."""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .data_usage import StochasticStreamLaw
from .learner import ReferenceLearnerState
from .float64_learner import Float64LearnerState
from .float64_range import Float64Range
from .numerics import LogInterval
from .persistence import PersistenceRule, ArcsinePersistenceRule, REFERENCE_PATH


@dataclass(frozen=True)
class AlphaAllocation:
    allocation_id: str
    identity_id: str
    alpha: F
    cursor: int
    law: StochasticStreamLaw
    path: str = REFERENCE_PATH


@dataclass(frozen=True)
class PersistenceIdentity:
    identity_id: str
    rule: PersistenceRule | ArcsinePersistenceRule
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
    initial_base_float64: Float64LearnerState | None = None
    initial_candidate_float64: Float64LearnerState | None = None
    current_base_float64: Float64LearnerState | None = None
    current_candidate_float64: Float64LearnerState | None = None
    base_float64_range: tuple[Float64Range, ...] = ()
    candidate_float64_range: tuple[Float64Range, ...] = ()
    ratio_bound_kind: str = 'native-class-cap'
    mixture_coefficients: tuple[int, ...] | None = None


@dataclass(frozen=True)
class PersistenceEvent:
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
    score_path: str = REFERENCE_PATH


@dataclass(frozen=True)
class PersistenceResult:
    status: str
    identity_id: str | None
    alpha_spent: F
    epochs_completed: int
    wealth_lower: F
    crossing_cursor: int | None
    reason: str
    score_path: str = REFERENCE_PATH
    authority_scope: str = field(default='conditional same-path mean-null evidence only; no actual AMP or installation authority', init=False)


@dataclass(frozen=True)
class PairedPersistenceResult:
    status: str
    reference_identity: str
    float64_identity: str
    cursor: int
    alpha_spent: F
    reason: str
    authority_scope: str = field(default='two same-path CPU persistence crossings on four continuous learners; no target AMP or install authority', init=False)
