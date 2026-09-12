"""Authority-owned construction and registered exact causal event execution.

Complete search/proof, fresh persistence, actual AMP and install integration
remain open. This endpoint never issues CERTIFIED_COMPLETE or accepts helper
certificates as installation authority. Its packed-payload machine contract is
not a measurement of total host/device memory or elapsed computation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
import secrets
from typing import Mapping

from .core import ContractError, freeze_data, natural, stable_hash
from .data_usage import DataContract, DataUsageLedger, ObservationRecord, read_sources
from .info import QueryRecord, QueryResult, QuerySpec, evaluate_query
from .learner import LearnerSpec, ReferenceLearnerState, commit_event, initial_state, observe_event
from .machine import PackedObject, ReferenceMachineModel
from .program import Program, SemanticRules, name, rational
from .profile import ProfileEvent, ProfileExecution, ProfileSpec, ProfileUnresolved, attach_boundary
from .resources import CostRouter, ResourceExceeded, ResourceLedger, ResourceLimits
from .semantics import ArithmeticUnresolved, Evaluation, RangeBound, _guard, enclose, evaluate, reset_delayed


@dataclass(frozen=True)
class ConstructionContract:
    """The enforced construction slice of ERC-1, not its complete run manifest."""
    semantics: SemanticRules
    limits: ResourceLimits
    work_roles: Mapping[str, str]
    graph_limits: Mapping[str, int]
    initializer_pattern: tuple[F, ...]
    normalizer_cap: F
    activation_cap: F
    reference_integer_bits: int
    source_domain: tuple[tuple[F, ...], ...] | None = None

    def __post_init__(self):
        if type(self.semantics) is not SemanticRules or type(self.limits) is not ResourceLimits:
            raise ContractError('immutable semantic and resource declarations required')
        if set(self.limits.role_residency) != {'deployment', 'compiler'}:
            raise ContractError('deployment and compiler resource roles must stay distinct')
        if set(self.limits.global_residency) != ReferenceMachineModel.residency_dimensions:
            raise ContractError('the recovered machine measures packed reference payloads, not total host/GPU memory')
        if set(self.work_roles) != {'construct', 'range_audit'} or any(role not in self.limits.role_cumulative for role in self.work_roles.values()):
            raise ContractError('construction and range-audit work roles must be fixed before execution')
        if any('work' not in caps for caps in self.limits.role_cumulative.values()):
            raise ContractError('every work role requires its cumulative work cap')
        required = {'nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots'}
        if set(self.graph_limits) != required:
            raise ContractError('declare every separate native graph budget')
        object.__setattr__(self, 'graph_limits', freeze_data({key: natural(value, key) for key, value in self.graph_limits.items()}))
        object.__setattr__(self, 'work_roles', freeze_data(self.work_roles))
        pattern = tuple(rational(v, 'registered initializer') for v in self.initializer_pattern)
        if not pattern:
            raise ContractError('registered initializer pattern is empty')
        object.__setattr__(self, 'initializer_pattern', pattern)
        object.__setattr__(self, 'normalizer_cap', rational(self.normalizer_cap, 'normalizer cap', positive=True))
        object.__setattr__(self, 'activation_cap', rational(self.activation_cap, 'activation cap', positive=True))
        natural(self.reference_integer_bits, 'exact reference integer work limit', positive=True)
        if self.source_domain is not None:
            domain = tuple(tuple(rational(v, 'declared source-domain value') for v in row) for row in self.source_domain)
            if not domain or any(len(row) != len(self.semantics.sources) for row in domain):
                raise ContractError('complete nonempty source-domain rows required')
            if any(v > spec.upper for row in domain for v, spec in zip(row, self.semantics.sources)):
                raise ContractError('declared source domain exceeds its source ranges')
            object.__setattr__(self, 'source_domain', domain)


@dataclass(frozen=True)
class OnlineContract:
    """A deterministic revealed-data learner, not the full ERC-1 run manifest."""
    data: DataContract
    learner: LearnerSpec
    queries: tuple[QuerySpec, ...] = ()
    profiles: tuple[ProfileSpec, ...] = ()

    def __post_init__(self):
        if type(self.data) is not DataContract or type(self.learner) is not LearnerSpec:
            raise ContractError('immutable data and learner declarations required')
        queries = tuple(self.queries)
        if any(type(q) is not QuerySpec for q in queries) or len({q.query_id for q in queries}) != len(queries):
            raise ContractError('distinct registered query implementations required')
        object.__setattr__(self, 'queries', queries)
        profiles = tuple(self.profiles)
        if any(type(p) is not ProfileSpec for p in profiles) or len({p.profile_id for p in profiles}) != len(profiles):
            raise ContractError('distinct immutable profile declarations required')
        for profile in profiles:
            profile.validate(self.data, self.learner)
        object.__setattr__(self, 'profiles', profiles)

    def validate(self, construction: ConstructionContract):
        self.data.validate(construction.semantics)
        if self.learner.commit_grid_bits is not None and self.learner.commit_grid_bits >= construction.reference_integer_bits:
            raise ContractError('registered commit grid exceeds reference integer work limit')
        for query in self.queries:
            query.validate(construction.semantics, construction.reference_integer_bits)


@dataclass(frozen=True)
class ConstructedState:
    candidate_id: str
    physical_owner: str
    program_id: str
    birth_cursor: int
    learner: ReferenceLearnerState
    range_evidence: tuple[RangeBound, ...]
    range_safe: bool
    object_ids: tuple[str, ...]
    initializer_id: str
    machine_id: str
    profile_id: str | None = None

    @property
    def theta(self):
        return self.learner.theta

    @property
    def delayed(self):
        return self.learner.delayed


@dataclass(frozen=True)
class ConstructionResult:
    status: str
    candidate_id: str | None
    reason: str


@dataclass(frozen=True)
class PendingEvent:
    record: ObservationRecord
    predictions: tuple[tuple[str, Evaluation], ...]
    target_object_id: str
    object_ids: tuple[str, ...]
    stage: str


@dataclass(frozen=True)
class EventTrace:
    observation_id: str
    candidate_id: str
    program_id: str
    before: ReferenceLearnerState
    prediction: Evaluation
    after_observe: ReferenceLearnerState
    after_commit: ReferenceLearnerState | None


@dataclass(frozen=True)
class PredictionResult:
    status: str
    observation_id: str
    cursor: int
    predictions: tuple[tuple[str, tuple[F, ...]], ...]
    reason: str


@dataclass(frozen=True)
class ObservationResult:
    status: str
    observation_id: str
    cursor_before: int
    cursor_after: int
    committed: bool
    reason: str


@dataclass(frozen=True)
class RuntimeSnapshot:
    chi: str
    runtime_id: str
    phase: str
    cursor: int
    deployed_id: str
    next_candidate: int
    programs: tuple[tuple[str, Program], ...]
    candidates: tuple[ConstructedState, ...]
    resources: Mapping
    buffers: tuple[tuple[str, bytes], ...]
    attempts: tuple[tuple[str, str, str], ...]
    online: OnlineContract | None
    event_phase: str
    pending: PendingEvent | None
    observations: tuple[ObservationRecord, ...]
    event_traces: tuple[EventTrace, ...]
    data_uses: tuple
    queries: tuple[QueryRecord, ...]
    halted: tuple[str, str] | None
    retained_programs: tuple[tuple[str, str], ...]
    profiles: tuple[ProfileExecution, ...]
    profile_events: tuple[ProfileEvent, ...]


class ReferenceCompilerRuntime:
    recovery_phase = 'native-construction-causal-reference'

    def __init__(self, contract: ConstructionContract, initial_program: Program, *, online: OnlineContract | None = None):
        if type(contract) is not ConstructionContract:
            raise ContractError('registered construction contract required')
        self._contract = contract
        if online is not None:
            if type(online) is not OnlineContract:
                raise ContractError('registered online continuation required')
            online.validate(contract)
        self._online = online
        self._chi = stable_hash(('ERC-1 construction recovery', self.recovery_phase,
                                 ReferenceMachineModel.model_id, ReferenceMachineModel.initializer_id, contract, online))
        self._runtime_id = secrets.token_hex(12)
        self._ledger = ResourceLedger(contract.limits)
        self._router = CostRouter(self._ledger, contract.work_roles)
        # Event, retained evidence and query roles are fixed by this machine
        # implementation before outcomes. No public action can route a debit.
        self._event_router = CostRouter(self._ledger, {'deployment_event': 'deployment',
                                       'compiler_event': 'compiler', 'information': 'compiler'})
        self._machine = ReferenceMachineModel()
        self._cursor = 0
        self._next_candidate = 0
        self._programs: dict[str, Program] = {}
        self._retained_programs: dict[str, str] = {}
        self._candidates: dict[str, ConstructedState] = {}
        self._buffers: dict[str, bytes | bytearray] = {}
        self._attempts: list[tuple[str, str, str]] = []
        self._deployed_id = ''
        self._event_phase = 'idle'
        self._pending: PendingEvent | None = None
        self._observations: list[ObservationRecord] = []
        self._event_traces: list[EventTrace] = []
        self._profile_executions: dict[str, ProfileExecution] = {}
        self._profile_events: list[ProfileEvent] = []
        self._query_records: list[QueryRecord] = []
        self._data_usage = DataUsageLedger()
        self._halted: tuple[str, str] | None = None
        self._data_owner = f'{self._runtime_id}:retained-information'
        if online is not None:
            self._ledger.register_owner(self._data_owner, 'compiler')
        initial = self._construct(initial_program, 'deployment')
        if initial.status != 'BUILT_REFERENCE':
            raise ContractError(f'initial registered reference realization failed: {initial.status}: {initial.reason}')
        self._deployed_id = initial.candidate_id

    @property
    def contract(self):
        return self._contract

    @property
    def chi(self):
        return self._chi

    @property
    def online_contract(self):
        return self._online

    def _allocate(self, owner: str, objects: tuple[PackedObject, ...]):
        if any(type(obj) is not PackedObject or type(obj.payload) is not bytes or obj.spec.residency != {
                'reference_payload_bytes': len(obj.payload), 'physical_objects': 1} for obj in objects):
            raise ContractError('registered packed-object size disagrees with its actual payload')
        self._ledger.allocate(owner, tuple(obj.spec for obj in objects))
        self._buffers.update((obj.spec.object_id, bytearray(obj.payload) if obj.spec.kind == 'reserved_target' else obj.payload)
                             for obj in objects)

    def _release_owner(self, owner: str):
        self._ledger.close_owner(owner)
        live = self._ledger.snapshot()['objects']
        self._buffers = {key: value for key, value in self._buffers.items() if key in live}

    def _range(self, program: Program, theta, label: str) -> tuple[RangeBound, ...]:
        evidence = []
        rows = (None,) if self._contract.source_domain is None else self._contract.source_domain
        for index, row in enumerate(rows):
            self._router.charge_work('range_audit', {'work': self._machine.evaluation_work(program, self._contract.semantics)}, f'{label}:range:{index}')
            point = None if row is None else {spec.source_id: value for spec, value in zip(self._contract.semantics.sources, row)}
            evidence.append(enclose(program, self._contract.semantics, theta, source_point=point,
                                    bit_limit=self._contract.reference_integer_bits))
        return tuple(evidence)

    def _safe(self, evidence: tuple[RangeBound, ...]) -> bool:
        return all(bound.sufficient(normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap)
                   for bound in evidence)

    def _construct(self, program: Program, role: str, profile_id: str | None = None) -> ConstructionResult:
        number = self._next_candidate
        self._next_candidate += 1
        candidate = f'{self._runtime_id}:candidate:{number}'
        owner = f'{candidate}:owner'
        self._ledger.register_owner(owner, role)
        try:
            # Request inspection is itself an executed, immutable-role debit.
            self._router.charge_work('construct', {'work': 1}, f'{candidate}:inspect')
            profile = None
            if profile_id is not None:
                name(profile_id, 'requested profile ID')
                if self._online is None or role != 'compiler':
                    raise ContractError('profile belongs only to registered newborn candidate construction')
                profile = next((p for p in self._online.profiles if p.profile_id == profile_id), None)
                if profile is None:
                    raise ContractError('unregistered profile implementation')
            if type(program) is not Program:
                raise ContractError('candidate structure must use the native Program grammar')
            if len(program.nodes) > self._contract.graph_limits['nodes'] or program.slot_count > self._contract.graph_limits['slots']:
                raise ContractError('candidate header exceeds a registered native budget')
            counts = program.counts()
            self._router.charge_work('construct', {'work': self._machine.construction_work(program, self._contract.semantics)}, f'{candidate}:construct')
            program.validate(self._contract.semantics)
            if any(counts[key] > cap for key, cap in self._contract.graph_limits.items()):
                raise ContractError('candidate exceeds a registered P/S/edge/slot budget')
            program_id = program.program_id
            delayed = reset_delayed(self._contract.semantics)
            zero = (F(0),)*program.slot_count
            code = self._machine.realize(f'{candidate}:code', 'native_program', program, program_id)
            initial = self._machine.realize(f'{candidate}:zero', 'zero_slot_state', (zero, delayed), program_id)
            self._allocate(owner, (code, initial))
            # Numerical values begin at the immutable initializer. An optional
            # registered profile is executed below, never supplied as theta.
            theta = self._machine.initializer(program.slot_count, self._contract.initializer_pattern)
            learner = initial_state(program, self._contract.semantics, theta, self._cursor)
            initialized = self._machine.realize(f'{candidate}:values', 'initialized_reference_state', learner, program_id)
            self._router.charge_work('construct', {'work': program.slot_count}, f'{candidate}:registered-initialize')
            self._allocate(owner, (initialized,))
            self._ledger.release(owner, initial.spec.object_id)
            del self._buffers[initial.spec.object_id]
            evidence = self._range(program, theta, candidate)
            checked = self._machine.realize(f'{candidate}:range', 'range_evidence', tuple(evidence), program_id)
            self._allocate(owner, (checked,))
            safe = self._safe(evidence)
            state = ConstructedState(candidate, owner, program_id, self._cursor, learner,
                                     tuple(evidence), safe, (code.spec.object_id, initialized.spec.object_id, checked.spec.object_id),
                                     self._machine.initializer_id, self._machine.model_id)
            if profile is not None:
                state = self._profile_newborn(program, state, profile)
                safe = state.range_safe
            self._candidates[candidate] = state
            self._programs[program_id] = program
            status = 'BUILT_REFERENCE' if safe else 'UNRESOLVED_RANGE'
            reason = ('native construction and registered profile endpoint checked' if profile is not None else
                      'native construction and fixed-value range bound checked') if safe else 'conservative full-domain range bound does not establish feasibility'
            self._attempts.append((candidate, status, reason))
            return ConstructionResult(status, candidate, reason)
        except (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved) as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'UNRESOLVED', str(exc)))
            return ConstructionResult('UNRESOLVED', None, str(exc))
        except ContractError as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'REJECTED_ADMISSIBILITY', str(exc)))
            return ConstructionResult('REJECTED_ADMISSIBILITY', None, str(exc))
        except Exception as exc:
            # Programming/backend failures are visible failures, not a fake
            # mathematical rejection. Retire the partial physical build while
            # retaining all spent work/peak and the failed attempt in Omega.
            self._release_owner(owner)
            self._attempts.append((candidate, 'EXECUTION_FAILED', f'{type(exc).__name__}: {exc}'))
            raise

    def construct_candidate(self, program: Program, *, profile_id: str | None = None) -> ConstructionResult:
        self._require_idle()
        if self._online is not None and self._cursor % self._online.learner.update_unit:
            raise ContractError('new online lineages start at a registered update-unit boundary')
        self._event_phase = 'constructing'
        try:
            return self._construct(program, 'compiler', profile_id)
        finally:
            self._event_phase = 'idle'

    def retire_candidate(self, candidate_id: str):
        self._require_idle()
        if candidate_id == self._deployed_id or candidate_id not in self._candidates:
            raise ContractError('cannot retire the deployed or an unknown candidate')
        state = self._candidates.pop(candidate_id)
        self._release_owner(state.physical_owner)
        if state.program_id not in self._retained_programs and not any(other.program_id == state.program_id for other in self._candidates.values()):
            del self._programs[state.program_id]
        self._attempts.append((candidate_id, 'RETIRED', 'explicit release; spent work and peak residency retained'))

    def _require_idle(self):
        if self._event_phase != 'idle':
            raise ContractError('the owned event prefix is pending or halted')

    def _require_online(self):
        if self._online is None:
            raise ContractError('this Runtime has no registered ordinary learner/data interface')

    def _halt(self, stage: str, error: Exception):
        self._halted = (stage, f'{type(error).__name__}: {error}')
        self._event_phase = 'halted'
        self._attempts.append((f'event:{self._cursor}', 'UNRESOLVED' if isinstance(error, (ArithmeticUnresolved, ResourceExceeded)) else 'EXECUTION_FAILED', self._halted[1]))

    def _event_work(self, candidate: ConstructedState, work: int, stage: str):
        purpose = 'deployment_event' if candidate.candidate_id == self._deployed_id else 'compiler_event'
        self._event_router.charge_work(purpose, {'work': work}, f'{candidate.candidate_id}:event:{self._cursor}:{stage}')

    def _retain_program(self, state: ConstructedState):
        # Past execution evidence must retain the actual graph it describes,
        # even after its learner is retired. Sharing is an owned physical lease.
        self._retain_code(self._programs[state.program_id], state.program_id, state.object_ids[0], state.candidate_id)

    def _retain_code(self, program: Program, program_id: str, object_id: str, origin: str):
        if program_id not in self._retained_programs:
            self._event_router.charge_work('information', {'work': 1}, f'{origin}:retain-code-for-evidence')
            self._ledger.acquire(self._data_owner, object_id)
            self._retained_programs[program_id] = object_id
            self._programs[program_id] = program

    def _profile_newborn(self, program: Program, initial: ConstructedState, profile: ProfileSpec) -> ConstructedState:
        """Private value constructor; cannot modify a published ordinary lineage."""
        candidate, owner = initial.candidate_id, initial.physical_owner
        spec, rules = self._online.learner, self._contract.semantics
        record = ProfileExecution(candidate, profile.profile_id, initial.program_id, self._cursor,
                                  profile.event_count, 0, 'admission', 'RUNNING', initial.learner, initial.learner)
        self._profile_executions[candidate] = record
        prefix = f'{candidate}:profile'

        def update(**changes):
            self._profile_executions[candidate] = replace(self._profile_executions[candidate], **changes)

        def work(amount, stage):
            self._event_router.charge_work('compiler_event', {'work': amount}, f'{prefix}:{stage}')

        def retain(event, stage):
            obj = self._machine.realize(f'{prefix}:{event.position}:{stage}', 'profile_event_phase', event, self._chi)
            self._allocate(self._data_owner, (obj,))

        try:
            work(len(profile.observation_ids)+1, 'admit')
            available = {r.observation_id: r for r in self._observations}
            if any(obs not in available or available[obs].target is None for obs in profile.observation_ids):
                raise ProfileUnresolved('registered profile data are not all revealed yet')
            if not initial.range_safe:
                raise ProfileUnresolved('profile initialization lacks a sufficient full-domain range/invariant bound')
            if candidate in self._candidates or initial.birth_cursor != self._cursor or initial.learner.unit_count:
                raise ContractError('profile cannot replace a published ordinary learner trajectory')
            self._retain_code(program, initial.program_id, initial.object_ids[0], candidate)
            # Local replay clock starts at zero. All numerical/causal fields
            # are the registered newborn state, with no copied trained values.
            local = replace(initial.learner, cursor=0)
            work(program.slot_count+sum(s.delay for s in rules.states)+1, 'local-clock')
            local_object = self._machine.realize(f'{prefix}:local-initial', 'profile_initial_state', local, initial.program_id)
            self._allocate(owner, (local_object,))
            self._ledger.release(owner, initial.object_ids[1])
            del self._buffers[initial.object_ids[1]]
            current_ids = (initial.object_ids[0], local_object.spec.object_id, initial.object_ids[2])
            evidence = initial.range_evidence
            update(stage='replay', local=local)
            for position in range(profile.event_count):
                observation = available[profile.observation_ids[position % len(profile.observation_ids)]]
                work(1, f'{position}:read')
                self._data_usage.record((observation,), 'profile', candidate, self._cursor)
                update(stage='predict')
                work(self._machine.evaluation_work(program, rules), f'{position}:predict')
                prediction = evaluate(program, rules, local.theta, dict(observation.sources), local.delayed,
                                      bit_limit=self._contract.reference_integer_bits)
                if prediction.normalizer > self._contract.normalizer_cap or any(v > self._contract.activation_cap for v in prediction.values):
                    raise ContractError('profile execution contradicts a sufficient native range bound')
                event = ProfileEvent(candidate, profile.profile_id, initial.program_id, self._cursor,
                                     position, observation.observation_id, local, prediction)
                self._profile_events.append(event)
                retain(event, 'predicted')
                update(stage='observe')
                work(self._machine.observation_work(program), f'{position}:observe')
                observed = observe_event(program, local, spec, prediction, observation.target,
                                         bit_limit=self._contract.reference_integer_bits)
                event = replace(event, after_observe=observed)
                self._profile_events[-1] = event
                update(local=observed)
                retain(event, 'observed')
                successor = observed
                if (position+1) % spec.update_unit == 0:
                    update(stage='commit')
                    work(self._machine.commit_work(program), f'{position}:commit')
                    successor = commit_event(observed, spec, bit_limit=self._contract.reference_integer_bits)
                    event = replace(event, after_commit=successor)
                    self._profile_events[-1] = event
                    update(local=successor, stage='range')
                    retain(event, 'committed')
                    evidence = self._range(program, successor.theta, f'{prefix}:{position}')
                    if not self._safe(evidence):
                        raise ProfileUnresolved('profile optimizer successor lacks a sufficient full-domain range/invariant bound')
                values = self._machine.realize(f'{prefix}:{position}:values', 'profile_current_state', successor, initial.program_id)
                checked = self._machine.realize(f'{prefix}:{position}:range', 'profile_range_evidence', evidence, initial.program_id)
                self._allocate(owner, (values, checked))
                self._ledger.release_many(tuple((owner, object_id, 1) for object_id in current_ids[1:]))
                for object_id in current_ids[1:]:
                    del self._buffers[object_id]
                current_ids = (current_ids[0], values.spec.object_id, checked.spec.object_id)
                local = successor
                update(events_completed=position+1, stage='replay', local=local)
            update(stage='attach')
            work(program.slot_count+sum(s.delay for s in rules.states)+1, 'attach-boundary')
            attached = attach_boundary(local, self._cursor, spec)
            attached_object = self._machine.realize(f'{prefix}:attached', 'profiled_newborn_state', attached, initial.program_id)
            self._allocate(owner, (attached_object,))
            # Retain the checked pair of local and ordinary clock coordinates.
            completed = replace(self._profile_executions[candidate], attached=attached, stage='complete', status='PROFILED_REFERENCE')
            completed_object = self._machine.realize(f'{prefix}:complete', 'profile_construction_record', completed, self._chi)
            self._allocate(self._data_owner, (completed_object,))
            self._ledger.release(owner, current_ids[1])
            del self._buffers[current_ids[1]]
            self._profile_executions[candidate] = completed
            return replace(initial, learner=attached, range_evidence=evidence, range_safe=True,
                           object_ids=(current_ids[0], attached_object.spec.object_id, current_ids[2]), profile_id=profile.profile_id)
        except Exception as exc:
            expected = isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved))
            update(status='UNRESOLVED' if expected else 'EXECUTION_FAILED', reason=f'{type(exc).__name__}: {exc}')
            if isinstance(exc, ContractError) and not expected:
                raise RuntimeError('registered profile execution violated its checked inputs') from exc
            raise

    def _target_slot(self, target: int | None):
        width = max(1, ((len(self._contract.semantics.base)-1).bit_length()+3)//4)
        return f'{int(target is not None)}:{(0 if target is None else target):0{width}x}'

    def predict_next(self, observation_id: str, inputs) -> PredictionResult:
        """Accept the next registered context; the signature has no target."""
        self._require_online()
        self._require_idle()
        data, rules = self._online.data, self._contract.semantics
        name(observation_id, 'observation ID')
        if self._cursor >= len(data.active.observation_ids) or observation_id != data.active.observation_ids[self._cursor]:
            raise ContractError('ordinary observation skips/reuses its fixed stream identity or data role')
        inputs = tuple(rational(v, 'pre-target exogenous input') for v in inputs)
        if len(inputs) != len(data.input_upper) or any(v > cap for v, cap in zip(inputs, data.input_upper)):
            raise ContractError('input differs from its registered range/interface')
        # Preconditions reject malformed input before beginning a legal event.
        sources = read_sources(data, self._cursor, inputs, tuple(self._observations))
        source_map = dict(sources)
        if self._contract.source_domain is not None and tuple(source_map[s.source_id] for s in rules.sources) not in self._contract.source_domain:
            raise ContractError('actual causal context is outside the complete registered source domain')
        if any(s.learner.cursor != self._cursor for s in self._candidates.values() if s.range_safe):
            raise ContractError('an active reference lineage lost the common exogenous cursor')
        record = ObservationRecord(observation_id, data.active.stream_id, data.active.role, self._cursor, inputs, sources, None)
        prefix = f'{self._runtime_id}:event:{self._cursor}'
        predictions, object_ids = [], []
        self._pending = PendingEvent(record, (), f'{prefix}:target', (), 'context-revealed')
        self._event_phase = 'predicting'
        try:
            _guard(*inputs, bit_limit=self._contract.reference_integer_bits)
            # Reserve the bounded target slot and its write work before the
            # target arrives. A later backend/resource failure cannot unread it.
            self._event_router.charge_work('information', {'work': len(inputs)+len(sources)+2}, f'{prefix}:ingress')
            context = self._machine.realize(f'{prefix}:context', 'revealed_context', record, self._chi)
            target_slot = self._machine.realize(f'{prefix}:target', 'reserved_target', self._target_slot(None), self._chi)
            self._allocate(self._data_owner, (context, target_slot))
            object_ids.extend((context.spec.object_id, target_slot.spec.object_id))
            for state in self._candidates.values():
                if not state.range_safe:
                    continue  # retained unresolved construction is not a live trajectory
                self._retain_program(state)
                program = self._programs[state.program_id]
                self._event_work(state, self._machine.evaluation_work(program, rules), 'predict')
                prediction = evaluate(program, rules, state.theta, source_map, state.delayed,
                                      bit_limit=self._contract.reference_integer_bits)
                if prediction.normalizer > self._contract.normalizer_cap or any(v > self._contract.activation_cap for v in prediction.values):
                    raise ContractError('a certified range enclosure disagrees with actual native execution')
                predictions.append((state.candidate_id, prediction))
                tape = self._machine.realize(f'{prefix}:{state.candidate_id}:prediction', 'pre_target_prediction',
                                             (state.candidate_id, state.program_id, state.learner, prediction), self._chi)
                self._allocate(self._data_owner, (tape,))
                object_ids.append(tape.spec.object_id)
            self._pending = replace(self._pending, predictions=tuple(predictions), object_ids=tuple(object_ids), stage='predicted')
            self._event_phase = 'awaiting-target'
            return PredictionResult('PREDICTED_REFERENCE', observation_id, self._cursor,
                                    tuple((candidate, pred.probabilities) for candidate, pred in predictions), 'all active reference predictions precede the target')
        except Exception as exc:
            self._pending = replace(self._pending, predictions=tuple(predictions), object_ids=tuple(object_ids), stage='prediction-failed')
            self._halt('predict', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return PredictionResult('UNRESOLVED', observation_id, self._cursor, (), str(exc))

    def observe(self, target: int) -> ObservationResult:
        """Reveal exactly one target; Runtime alone determines optimizer commit."""
        self._require_online()
        if self._event_phase != 'awaiting-target':
            raise ContractError('target reveal requires the owned preceding prediction')
        natural(target, 'target label')
        if target >= len(self._contract.semantics.base):
            raise ContractError('target outside the registered label set')
        pending, cursor = self._pending, self._cursor
        record = replace(pending.record, target=target)
        self._pending = replace(pending, record=record, stage='target-revealed')
        self._event_phase = 'observing'
        self._observations.append(record)
        self._data_usage.record((record,), 'ordinary', self._runtime_id, cursor)
        spec, rules = self._online.learner, self._contract.semantics
        do_commit = (cursor+1) % spec.update_unit == 0
        staged = []
        try:
            # An in-place write to the already paid, fixed-size owned slot.
            filled = self._machine.realize(pending.target_object_id, 'reserved_target', self._target_slot(target), self._chi)
            if len(filled.payload) != len(self._buffers[pending.target_object_id]):
                raise ContractError('target ingress changed its reserved physical extent')
            slot = self._buffers[pending.target_object_id]
            if type(slot) is not bytearray:
                raise ContractError('target ingress lacks its owned mutable reserved buffer')
            slot[:] = filled.payload
            for candidate, prediction in pending.predictions:
                state = self._candidates[candidate]
                program = self._programs[state.program_id]
                self._event_work(state, self._machine.observation_work(program), 'observe-and-accumulate')
                observed = observe_event(program, state.learner, spec, prediction, target,
                                         bit_limit=self._contract.reference_integer_bits)
                trace = EventTrace(record.observation_id, candidate, state.program_id, state.learner, prediction, observed, None)
                self._event_traces.append(trace)
                prefix = f'{candidate}:event:{cursor}'
                observed_object = self._machine.realize(f'{prefix}:observed', 'after_observation_phase', trace, self._chi)
                self._allocate(self._data_owner, (observed_object,))
                committed = None
                evidence = state.range_evidence
                if do_commit:
                    self._event_work(state, self._machine.commit_work(program), 'optimizer-commit')
                    committed = commit_event(observed, spec, bit_limit=self._contract.reference_integer_bits)
                    trace = replace(trace, after_commit=committed)
                    self._event_traces[-1] = trace
                    trace_object = self._machine.realize(f'{prefix}:committed', 'after_optimizer_phase', trace, self._chi)
                    self._allocate(self._data_owner, (trace_object,))
                    evidence = self._range(program, committed.theta, f'{candidate}:commit:{cursor+1}')
                    if not self._safe(evidence):
                        raise ArithmeticUnresolved('registered optimizer successor lacks a sufficient full-domain range/invariant bound')
                final_state = committed if committed is not None else observed
                values = self._machine.realize(f'{prefix}:values', 'ordinary_reference_state', final_state, state.program_id)
                checked = self._machine.realize(f'{prefix}:range', 'current_range_evidence', evidence, state.program_id)
                self._allocate(state.physical_owner, (values, checked))
                staged.append(replace(state, learner=final_state, range_evidence=evidence,
                                      object_ids=(state.object_ids[0], values.spec.object_id, checked.spec.object_id)))
            # Publish every successor together only after every required phase
            # and coexistence check succeeded. Failed work/targets stay retained.
            releases = tuple((self._candidates[s.candidate_id].physical_owner, object_id, 1)
                             for s in staged for object_id in self._candidates[s.candidate_id].object_ids[1:])
            self._ledger.release_many(releases)
            live = self._ledger.snapshot()['objects']
            self._buffers = {key: value for key, value in self._buffers.items() if key in live}
            self._candidates = {**self._candidates, **{s.candidate_id: s for s in staged}}
            self._cursor = cursor+1
            self._pending = None
            self._event_phase = 'idle'
            return ObservationResult('OBSERVED_REFERENCE', record.observation_id, cursor, self._cursor,
                                     do_commit, 'continuous exact ordinary event; no AMP/persistence authority')
        except Exception as exc:
            self._pending = replace(self._pending, stage='observation-failed')
            self._halt('observe', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return ObservationResult('UNRESOLVED', record.observation_id, cursor, self._cursor, False, str(exc))

    def query(self, query_id: str, observation_ids) -> QueryResult:
        self._require_online()
        self._require_idle()
        name(query_id, 'query ID')
        spec = next((q for q in self._online.queries if q.query_id == query_id), None)
        if spec is None:
            raise ContractError('unregistered query implementation')
        ids = tuple(name(v, 'query observation ID') for v in observation_ids)
        available = {r.observation_id: r for r in self._observations}
        if not 0 < len(ids) <= spec.max_records or len(set(ids)) != len(ids) or any(value not in available for value in ids):
            raise ContractError('query skips the revealed legal data interface or duplicates observations')
        records = tuple(available[value] for value in ids)
        prefix = f'{self._runtime_id}:query:{len(self._query_records)}'
        result = QueryResult(query_id, 'UNRESOLVED', (), (), 'query did not finish')
        error = None
        try:
            self._event_router.charge_work('information', {'work': spec.work(len(records))}, prefix)
            # Mark before computation, including range/backend failures. The
            # observation cannot become fresh again because no answer arrived.
            self._data_usage.record(records, 'proposal', prefix, self._cursor)
            result = evaluate_query(spec, records, bit_limit=self._contract.reference_integer_bits)
        except (ContractError, ResourceExceeded) as exc:
            result = replace(result, reason=str(exc))
        except Exception as exc:
            error = exc
            result = replace(result, status='EXECUTION_FAILED', reason=f'{type(exc).__name__}: {exc}')
        query_record = QueryRecord(self._cursor, ids, result)
        self._query_records.append(query_record)
        try:
            retained = self._machine.realize(prefix, 'query_transcript', query_record, self._chi)
            self._allocate(self._data_owner, (retained,))
        except Exception as exc:
            self._halt('retain-query', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return replace(result, status='UNRESOLVED', indices=(), values=(), reason=str(exc))
        if error is not None:
            raise error
        return result

    def install(self, candidate_id: str, *unused_authority, **unused_payload) -> ConstructionResult:
        # This method accepts no helper token as a substitute for the still
        # missing complete learning/persistence/AMP/atomic-install chain.
        return ConstructionResult('UNRESOLVED', None, 'complete Runtime continuation, actual AMP, persistence and atomic install are not yet integrated')

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(self._chi, self._runtime_id, self.recovery_phase, self._cursor,
                               self._deployed_id, self._next_candidate, tuple(self._programs.items()),
                               tuple(self._candidates.values()), self._ledger.snapshot(),
                               tuple((key, bytes(value) if type(value) is bytearray else value) for key, value in self._buffers.items()), tuple(self._attempts),
                               self._online, self._event_phase, self._pending, tuple(self._observations),
                               tuple(self._event_traces), self._data_usage.snapshot(), tuple(self._query_records), self._halted,
                               tuple(self._retained_programs.items()), tuple(self._profile_executions.values()), tuple(self._profile_events))
