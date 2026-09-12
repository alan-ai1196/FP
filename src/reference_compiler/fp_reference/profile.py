"""Preregistered finite replay used only inside new-candidate construction.

Logged source contexts keep their original observation identity and causal
origin. Profile events have their own local clock; they do not consume new
exogenous observations. The final boundary attachment preserves all value,
optimizer, accumulator and delayed coordinates, changing only clock namespace.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .core import ContractError, natural
from .data_usage import DataContract
from .learner import LearnerSpec, ReferenceLearnerState
from .program import name
from .semantics import Evaluation


class ProfileUnresolved(ContractError):
    pass


@dataclass(frozen=True)
class ProfileSpec:
    profile_id: str
    observation_ids: tuple[str, ...]
    passes: int
    method_id: str = 'ordered-retained-data-v1'

    def __post_init__(self):
        name(self.profile_id, 'profile ID')
        ids = tuple(name(value, 'profile observation ID') for value in self.observation_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ContractError('one profile pass requires distinct registered observation identities')
        natural(self.passes, 'registered profile passes', positive=True)
        if self.method_id != 'ordered-retained-data-v1':
            raise ContractError('unimplemented registered profile semantics')
        object.__setattr__(self, 'observation_ids', ids)

    @property
    def event_count(self):
        return len(self.observation_ids)*self.passes

    def validate(self, data: DataContract, learner: LearnerSpec):
        roles = {obs: stream.role for stream in data.streams for obs in stream.observation_ids}
        if any(roles.get(obs) not in ('train', 'online') for obs in self.observation_ids):
            raise ContractError('profile cannot use undeclared or reporting-only observations')
        if self.event_count % learner.update_unit:
            raise ContractError('profile must finish a whole registered optimizer unit')


@dataclass(frozen=True)
class ProfileEvent:
    candidate_id: str
    profile_id: str
    program_id: str
    ordinary_cursor: int
    position: int
    observation_id: str
    before: ReferenceLearnerState
    prediction: Evaluation
    after_observe: ReferenceLearnerState | None = None
    after_commit: ReferenceLearnerState | None = None


@dataclass(frozen=True)
class ProfileExecution:
    candidate_id: str
    profile_id: str
    program_id: str
    ordinary_cursor: int
    total_events: int
    events_completed: int
    stage: str
    status: str
    initial: ReferenceLearnerState
    local: ReferenceLearnerState
    attached: ReferenceLearnerState | None = None
    reason: str = ''


def attach_boundary(state: ReferenceLearnerState, ordinary_cursor: int, learner: LearnerSpec) -> ReferenceLearnerState:
    natural(ordinary_cursor, 'ordinary profile attachment cursor')
    if state.unit_count or state.cursor % learner.update_unit or ordinary_cursor % learner.update_unit:
        raise ContractError('profile endpoint and ordinary birth must both be complete update-unit boundaries')
    # There is no learned-state reset, parameter injection or implicit replay.
    # This is the declared endpoint of a newborn value constructor, not a
    # state-equivalence assertion or transport of an existing ordinary lineage.
    return replace(state, cursor=ordinary_cursor)
