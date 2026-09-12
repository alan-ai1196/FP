"""Owned construction, causal events, reference selection, evidence and CPU install.

Full Compiler decisions and actual AMP persistence/installation remain open.
This endpoint never issues CERTIFIED_COMPLETE or accepts helper
certificates as installation authority. Its packed-payload machine contract is
not a measurement of total host/device memory or elapsed computation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
import secrets
import sys
from typing import Mapping

from .core import ContractError, IdentityUnresolved, freeze_data, natural, stable_hash
from .data_usage import DataContract, DataUsageLedger, ObservationRecord, StochasticStreamLaw, read_sources
from .info import QueryRecord, QueryResult, QuerySpec, evaluate_query
from .learner import LearnerSpec, ReferenceLearnerState, commit_event, initial_state, observe_event
from .machine import PackedObject, PlannedObject, ReferenceMachineModel
from .encoding import packed_size, write_packed
from .host_failure import guard_host_allocations
from .host_resources import HostResourceContract, HostResourceObservation, _WindowsProcessHost
from .program import Program, SemanticRules, name, rational
from .profile import ProfileEvent, ProfileExecution, ProfileSpec, ProfileUnresolved, attach_boundary
from .numerics import LogInterval, compare_exact, compare_exact_work, log_enclosure, log_enclosure_work
from .persistence import PersistenceContract, REFERENCE_PATH, FLOAT64_PATH, next_wealth, threshold_crossed
from .persistence_state import AlphaAllocation, PersistenceEvent, PersistenceIdentity, PersistenceResult, PairedPersistenceResult
from .binary_arithmetic import Float64Arithmetic
from . import float64_learner as finite
from .float64_bridge import Float64Contract, Float64Relation, check_state, check_prediction, relation_work
from .float64_range import enclose_float64, enclosure_operations, stored_probability
from .installation import CpuInstallContract, CpuInstallAttempt, CpuInstallReceipt, CpuInstallResult
from .ingress import IngressIdentity, IngressSnapshot, IngressResult, control_payload, read_control, decode_context
from . import native_search as grammar
from .proof import ReferenceClassProof, verify_maximum
from .search import ComparisonRow, ReferenceSearchResult, ReferenceSearchSession, ReferenceSearchSpec, compare_likelihoods, likelihood
from .resources import CostRouter, ObjectSpec, ResourceExceeded, ResourceLedger, ResourceLimits
from .semantics import ArithmeticUnresolved, Evaluation, RangeBound, _guard, _operation, enclose, evaluate, reset_delayed


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
    """Registered revealed-data continuation, not the full ERC-1 run manifest."""
    data: DataContract
    learner: LearnerSpec
    queries: tuple[QuerySpec, ...] = ()
    profiles: tuple[ProfileSpec, ...] = ()
    searches: tuple[ReferenceSearchSpec, ...] = ()
    persistence: PersistenceContract | None = None
    float64: Float64Contract | None = None
    cpu_install: CpuInstallContract | None = None

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
        searches = tuple(self.searches)
        if any(type(s) is not ReferenceSearchSpec for s in searches) or len({s.search_name for s in searches}) != len(searches):
            raise ContractError('distinct immutable reference decision classes required')
        object.__setattr__(self, 'searches', searches)
        if self.persistence is not None and type(self.persistence) is not PersistenceContract:
            raise ContractError('registered persistence rules and global error budget required')
        if self.float64 is not None and type(self.float64) is not Float64Contract:
            raise ContractError('registered checked CPU binary64 execution required')
        if self.cpu_install is not None and type(self.cpu_install) is not CpuInstallContract:
            raise ContractError('registered serialized CPU install transition required')

    def validate(self, construction: ConstructionContract):
        self.data.validate(construction.semantics)
        if self.cpu_install is not None:
            self.cpu_install.__post_init__()
            if sys.implementation.name != 'cpython':
                raise ContractError('the registered CPU root-publication machine requires CPython')
            if self.float64 is None or self.persistence is None or not self.searches:
                raise ContractError('CPU install requires owned reference search, two numerical paths and persistence')
            if {r.score_path for r in self.persistence.rules} != {REFERENCE_PATH, FLOAT64_PATH}:
                raise ContractError('CPU install requires both registered same-path evidence rules')
        if self.learner.commit_grid_bits is not None and self.learner.commit_grid_bits >= construction.reference_integer_bits:
            raise ContractError('registered commit grid exceeds reference integer work limit')
        for query in self.queries:
            query.validate(construction.semantics, construction.reference_integer_bits)
        for search in self.searches:
            search.validate(self.data, self.profiles, construction.graph_limits)
        if self.persistence is not None:
            for rule in self.persistence.rules:
                if rule.score_path == FLOAT64_PATH and self.float64 is None:
                    raise ContractError('binary64 persistence requires its independently executed registered learner')
                if rule.wealth_grid_bits >= construction.reference_integer_bits:
                    raise ContractError('persistence wealth grid exceeds reference integer work limit')


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
    float64: finite.Float64LearnerState | None = None

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
    persistence_ids: tuple[str, ...] = ()
    float64_predictions: tuple[tuple[str, finite.Float64Evaluation], ...] = ()


@dataclass(frozen=True)
class Float64Trace:
    candidate_id: str
    program_id: str
    phase: str
    ordinary_cursor: int
    observation_id: str | None
    reference: ReferenceLearnerState
    float64: finite.Float64LearnerState | None
    reference_prediction: Evaluation | None
    float64_prediction: finite.Float64Evaluation | None
    relation: Float64Relation | None
    scalar_operations: int
    max_local_round_error: F
    status: str = 'CHECKED_FLOAT64_PHASE'
    reason: str = ''


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
    revision: int
    next_search: int
    searches: tuple[ReferenceSearchSession, ...]
    reference_proofs: tuple[ReferenceClassProof, ...]
    next_persistence: int
    alpha_spent: F
    alpha_allocations: tuple[AlphaAllocation, ...]
    persistence_identities: tuple[PersistenceIdentity, ...]
    persistence_events: tuple[PersistenceEvent, ...]
    float64_traces: tuple[Float64Trace, ...]
    next_install: int
    install_attempts: tuple[CpuInstallAttempt, ...]
    install_receipts: tuple[CpuInstallReceipt, ...]
    ingress: tuple[IngressSnapshot, ...]
    active_ingress: str | None
    host_resources: HostResourceObservation | None = None


@guard_host_allocations
class ReferenceCompilerRuntime:
    recovery_phase = 'native-construction-causal-reference'

    def __init__(self, contract: ConstructionContract, initial_program: Program, *, online: OnlineContract | None = None,
                 host: HostResourceContract | None = None):
        if type(contract) is not ConstructionContract:
            raise ContractError('registered construction contract required')
        self._contract = contract
        self._host = None if host is None else _WindowsProcessHost(host)
        if online is not None:
            if type(online) is not OnlineContract:
                raise ContractError('registered online continuation required')
            online.validate(contract)
        self._online = online
        self._chi = stable_hash(('ERC-1 construction recovery', self.recovery_phase,
                                 ReferenceMachineModel.model_id, ReferenceMachineModel.initializer_id, contract, online, host))
        self._runtime_id = secrets.token_hex(12)
        self._ledger = ResourceLedger(contract.limits)
        self._router = CostRouter(self._ledger, contract.work_roles)
        # Event, retained evidence and query roles are fixed by this machine
        # implementation before outcomes. No public action can route a debit.
        self._event_router = CostRouter(self._ledger, {'deployment_event': 'deployment',
                                       'compiler_event': 'compiler', 'information': 'compiler'})
        self._machine = ReferenceMachineModel()
        self._cursor = 0
        self._revision = 0
        self._next_search = 0
        self._searches: dict[str, ReferenceSearchSession] = {}
        self._reference_proofs: dict[str, ReferenceClassProof] = {}
        self._next_persistence = 0
        self._alpha_spent = F(0)
        self._alpha_allocations: list[AlphaAllocation] = []
        self._persistence_identities: dict[str, PersistenceIdentity] = {}
        self._persistence_events: list[PersistenceEvent] = []
        self._float64_traces: list[Float64Trace] = []
        self._next_install = 0
        self._install_attempts: list[CpuInstallAttempt] = []
        self._install_receipts: list[CpuInstallReceipt] = []
        self._ingress_identities: dict[str, IngressIdentity] = {}
        self._active_ingress: str | None = None
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

    def _allocate(self, owner: str, objects: tuple[PackedObject | PlannedObject, ...]):
        for obj in objects:
            if type(obj) is PlannedObject:
                size = packed_size(obj.value)
            elif type(obj) is PackedObject and type(obj.payload) is bytes:
                size = len(obj.payload)
            else:
                raise ContractError('registered materialization plan or raw reserved payload required')
            if obj.spec.residency != {'reference_payload_bytes': size, 'physical_objects': 1}:
                raise ContractError('registered packed-object size disagrees with its actual payload')
        self._ledger.allocate(owner, tuple(obj.spec for obj in objects))
        for obj in objects:
            if type(obj) is PlannedObject:
                output = bytearray(obj.spec.residency['reference_payload_bytes'])
                self._buffers[obj.spec.object_id] = output
                write_packed(obj.value, output)
            else:
                self._buffers[obj.spec.object_id] = bytearray(obj.payload)

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

    def _float64_execute(self, kind, program, candidate, reference, floating=None, *,
                         origin='ordinary', observation_id=None, sources=None,
                         reference_prediction=None, floating_prediction=None, target=None):
        """Execute one registered phase; no supplied endpoint or public signer."""
        if self._online is None or self._online.float64 is None:
            return None
        rules, spec = self._contract.semantics, self._online.learner
        if kind == 'initialize':
            allowance = finite.initialize_operations(program, rules)
        elif kind == 'predict':
            allowance = finite.evaluate_operations(program, rules)
        elif kind == 'observe':
            allowance = finite.observe_operations(program)
        elif kind == 'commit':
            allowance = finite.commit_operations(floating, spec)
        elif kind == 'attach':
            allowance = 0
        else:
            raise ContractError('unregistered internal binary64 execution phase')
        label = f'{candidate}:float64:{origin}:{kind}:{len(self._float64_traces)}'
        # Fixed scalar implementation + fixed relation checks, all paid before
        # execution. This retains the existing partial packed-reference model.
        charge = allowance*Float64Arithmetic.scalar_work+2*relation_work(program, rules)+24*len(rules.sources)
        if origin == 'construction':
            self._router.charge_work('construct', {'work': charge}, label)
        else:
            role = 'deployment_event' if origin == 'ordinary' and candidate == self._deployed_id else 'compiler_event'
            self._event_router.charge_work(role, {'work': charge}, label)
        arith = Float64Arithmetic(self._contract.reference_integer_bits)
        result, relation, error = floating, None, None
        actual_prediction = None
        try:
            if kind == 'initialize':
                result = finite.initialize(program, rules, reference.theta, reference.cursor, arith)
            elif kind == 'predict':
                state_relation = check_state(reference, floating, self._online.float64, bit_limit=arith.bit_limit)
                actual_prediction = finite.evaluate(program, rules, floating, sources, arith)
                relation = check_prediction(reference_prediction, actual_prediction, self._online.float64, rules,
                    normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap,
                    bit_limit=arith.bit_limit)
                relation = replace(relation, state_error=state_relation.state_error)
            elif kind == 'observe':
                result = finite.observe_event(program, floating, spec, floating_prediction, target, arith)
            elif kind == 'commit':
                result = finite.commit_event(floating, spec, arith)
            else:
                # Registered newborn profile clock attachment transports every
                # numeric bit unchanged; it does not recast a trained endpoint.
                result = replace(floating, cursor=reference.cursor)
            if kind != 'predict':
                relation = check_state(reference, result, self._online.float64, bit_limit=arith.bit_limit)
            if arith.operations != allowance:
                raise ContractError('binary64 executor did not complete its registered scalar operation schedule')
        except MemoryError:
            raise
        except Exception as exc:
            error = exc
        trace = Float64Trace(candidate, program.program_id, f'{origin}:{kind}', self._cursor, observation_id,
            reference, result, reference_prediction, actual_prediction, relation,
            arith.operations, arith.max_round_error,
            'CHECKED_FLOAT64_PHASE' if error is None else ('UNRESOLVED' if isinstance(error, (ArithmeticUnresolved, ResourceExceeded)) else 'EXECUTION_FAILED'),
            '' if error is None else f'{type(error).__name__}: {error}')
        packed = self._machine.realize(label, 'executed_float64_phase', trace, self._chi)
        try:
            self._allocate(self._data_owner, (packed,))
        except MemoryError:
            raise
        except Exception as retain_error:
            # A successful numerical check is not owned retained evidence if
            # its allocation failed. Keep only a terminal diagnostic, with the
            # same explicit out-of-payload limitation as other failed prefixes.
            # A second resource failure must not downgrade or erase an already
            # observed unexpected executor failure.
            expected = (ArithmeticUnresolved, ResourceExceeded)
            failure = error if error is not None and not isinstance(error, expected) else retain_error
            self._float64_traces.append(replace(trace,
                status='UNRESOLVED' if isinstance(failure, expected) else 'EXECUTION_FAILED',
                reason=(trace.reason+'; ' if trace.reason else '')+
                       f'phase evidence retention failed: {type(retain_error).__name__}: {retain_error}'))
            if isinstance(failure, ContractError) and not isinstance(failure, expected):
                raise RuntimeError('registered binary64 execution violated its admitted inputs') from failure
            raise failure
        self._float64_traces.append(trace)
        if error is not None:
            if isinstance(error, ContractError) and not isinstance(error, (ArithmeticUnresolved, ResourceExceeded)):
                raise RuntimeError('registered binary64 execution violated its admitted inputs') from error
            raise error
        return actual_prediction if kind == 'predict' else result

    @staticmethod
    def _learner_payload(reference, floating):
        return reference if floating is None else (reference, floating)

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
            if program_id in self._programs and self._programs[program_id] != program:
                raise IdentityUnresolved('content address collision cannot identify distinct native programs')
            delayed = reset_delayed(self._contract.semantics)
            zero = (F(0),)*program.slot_count
            code = self._machine.realize(f'{candidate}:code', 'native_program', program, program_id)
            initial = self._machine.realize(f'{candidate}:zero', 'zero_slot_state', (zero, delayed), program_id)
            self._allocate(owner, (code, initial))
            # Numerical values begin at the immutable initializer. An optional
            # registered profile is executed below, never supplied as theta.
            theta = self._machine.initializer(program.slot_count, self._contract.initializer_pattern)
            learner = initial_state(program, self._contract.semantics, theta, self._cursor)
            if self._online is not None and self._online.float64 is not None:
                self._retain_code(program, program_id, code.spec.object_id, candidate)
            floating = self._float64_execute('initialize', program, candidate, learner, origin='construction')
            initialized = self._machine.realize(f'{candidate}:values', 'initialized_reference_state', self._learner_payload(learner, floating), program_id)
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
                                     self._machine.initializer_id, self._machine.model_id, float64=floating)
            if profile is not None:
                state = self._profile_newborn(program, state, profile)
                safe = state.range_safe
            status = 'BUILT_REFERENCE' if safe else 'UNRESOLVED_RANGE'
            reason = ('native construction and registered profile endpoint checked' if profile is not None else
                      'native construction and fixed-value range bound checked') if safe else 'conservative full-domain range bound does not establish feasibility'
            result = ConstructionResult(status, candidate, reason)
            self._candidates[candidate] = state
            self._programs[program_id] = program
            self._attempts.append((candidate, status, reason))
            return result
        except (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved, IdentityUnresolved) as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'UNRESOLVED', str(exc)))
            return ConstructionResult('UNRESOLVED', None, str(exc))
        except ContractError as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'REJECTED_ADMISSIBILITY', str(exc)))
            return ConstructionResult('REJECTED_ADMISSIBILITY', None, str(exc))
        except MemoryError:
            raise
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
        try:
            self._admit_control('construct')
        except ResourceExceeded as exc:
            return ConstructionResult('UNRESOLVED', None, str(exc))
        self._revision += 1
        self._event_phase = 'constructing'
        try:
            return self._construct(program, 'compiler', profile_id)
        finally:
            self._event_phase = 'idle'

    def retire_candidate(self, candidate_id: str):
        self._require_idle()
        name(candidate_id, 'owned candidate identity')
        if candidate_id == self._deployed_id or candidate_id not in self._candidates:
            raise ContractError('cannot retire the deployed or an unknown candidate')
        self._admit_control('retire')
        self._revision += 1
        self._retire(candidate_id)

    def _retire(self, candidate_id: str):
        if candidate_id == self._deployed_id or candidate_id not in self._candidates:
            raise ContractError('cannot retire the deployed or an unknown candidate')
        for identity in tuple(self._persistence_identities.values()):
            if identity.status in ('ACTIVE', 'REFERENCE_CROSSED', 'FLOAT64_CROSSED') and candidate_id in (identity.base_lineage_id, identity.candidate_lineage_id):
                self._stop_persistence(identity, 'lineage retired; its alpha and historical evidence remain spent')
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

    def _admit_control(self, operation: str):
        """Pay before control mutation; denial leaves owned Runtime state intact.

This is the fixed machine's admission boundary, not a resource refund or
erasure of an executed attempt. Ordinary ingress has its separate finite
stream/terminal-prefix protocol; target observation must remain prepaid.
"""
        if operation in ('construct', 'retire'):
            role = self._contract.work_roles['construct']
        elif operation == 'install':
            role = self._online.cpu_install.work_role
        elif operation in ('query', 'admit-persistence', 'cancel-persistence',
                           'start-search', 'advance-search', 'cancel-search'):
            role = self._event_router.snapshot()['information']
        else:
            raise ContractError('unregistered control admission operation')
        self._ledger.charge_work(role, {'work': self._machine.control_admission_work},
                                 note=f'control-admission:{operation}')

    def _halt(self, stage: str, error: Exception):
        self._halted = (stage, f'{type(error).__name__}: {error}')
        self._event_phase = 'halted'
        self._attempts.append((f'event:{self._cursor}', 'UNRESOLVED' if isinstance(error, (ArithmeticUnresolved, ResourceExceeded)) else 'EXECUTION_FAILED', self._halted[1]))
        for identity in tuple(self._persistence_identities.values()):
            if identity.status in ('ACTIVE', 'REFERENCE_CROSSED', 'FLOAT64_CROSSED'):
                self._stop_persistence(identity, f'ordinary trajectory failed at {stage}: {error}')

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
            local_float64 = self._float64_execute('attach', program, candidate, local, initial.float64, origin='profile')
            work(program.slot_count+sum(s.delay for s in rules.states)+1, 'local-clock')
            local_object = self._machine.realize(f'{prefix}:local-initial', 'profile_initial_state', self._learner_payload(local, local_float64), initial.program_id)
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
                float64_prediction = self._float64_execute('predict', program, candidate, local, local_float64,
                    origin='profile', observation_id=observation.observation_id, sources=dict(observation.sources), reference_prediction=prediction)
                event = ProfileEvent(candidate, profile.profile_id, initial.program_id, self._cursor,
                                     position, observation.observation_id, local, prediction)
                self._profile_events.append(event)
                retain(event, 'predicted')
                update(stage='observe')
                work(self._machine.observation_work(program), f'{position}:observe')
                observed = observe_event(program, local, spec, prediction, observation.target,
                                         bit_limit=self._contract.reference_integer_bits)
                floating_successor = self._float64_execute('observe', program, candidate, observed, local_float64,
                    origin='profile', observation_id=observation.observation_id, floating_prediction=float64_prediction, target=observation.target)
                event = replace(event, after_observe=observed)
                self._profile_events[-1] = event
                update(local=observed)
                retain(event, 'observed')
                successor = observed
                if (position+1) % spec.update_unit == 0:
                    update(stage='commit')
                    work(self._machine.commit_work(program), f'{position}:commit')
                    successor = commit_event(observed, spec, bit_limit=self._contract.reference_integer_bits)
                    floating_successor = self._float64_execute('commit', program, candidate, successor, floating_successor,
                        origin='profile', observation_id=observation.observation_id)
                    event = replace(event, after_commit=successor)
                    self._profile_events[-1] = event
                    update(local=successor, stage='range')
                    retain(event, 'committed')
                    evidence = self._range(program, successor.theta, f'{prefix}:{position}')
                    if not self._safe(evidence):
                        raise ProfileUnresolved('profile optimizer successor lacks a sufficient full-domain range/invariant bound')
                values = self._machine.realize(f'{prefix}:{position}:values', 'profile_current_state', self._learner_payload(successor, floating_successor), initial.program_id)
                checked = self._machine.realize(f'{prefix}:{position}:range', 'profile_range_evidence', evidence, initial.program_id)
                self._allocate(owner, (values, checked))
                self._ledger.release_many(tuple((owner, object_id, 1) for object_id in current_ids[1:]))
                for object_id in current_ids[1:]:
                    del self._buffers[object_id]
                current_ids = (current_ids[0], values.spec.object_id, checked.spec.object_id)
                local = successor
                local_float64 = floating_successor
                update(events_completed=position+1, stage='replay', local=local)
            update(stage='attach')
            work(program.slot_count+sum(s.delay for s in rules.states)+1, 'attach-boundary')
            attached = attach_boundary(local, self._cursor, spec)
            attached_float64 = self._float64_execute('attach', program, candidate, attached, local_float64, origin='profile')
            attached_object = self._machine.realize(f'{prefix}:attached', 'profiled_newborn_state', self._learner_payload(attached, attached_float64), initial.program_id)
            self._allocate(owner, (attached_object,))
            # Retain the checked pair of local and ordinary clock coordinates.
            completed = replace(self._profile_executions[candidate], attached=attached, stage='complete', status='PROFILED_REFERENCE')
            completed_object = self._machine.realize(f'{prefix}:complete', 'profile_construction_record', completed, self._chi)
            self._allocate(self._data_owner, (completed_object,))
            self._ledger.release(owner, current_ids[1])
            del self._buffers[current_ids[1]]
            self._profile_executions[candidate] = completed
            return replace(initial, learner=attached, range_evidence=evidence, range_safe=True,
                           object_ids=(current_ids[0], attached_object.spec.object_id, current_ids[2]), profile_id=profile.profile_id,
                           float64=attached_float64)
        except MemoryError:
            raise
        except Exception as exc:
            expected = isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved))
            update(status='UNRESOLVED' if expected else 'EXECUTION_FAILED', reason=f'{type(exc).__name__}: {exc}')
            if isinstance(exc, ContractError) and not expected:
                raise RuntimeError('registered profile execution violated its checked inputs') from exc
            raise

    def _target_slot(self, target: int | None):
        width = max(1, ((len(self._contract.semantics.base)-1).bit_length()+3)//4)
        return f'{int(target is not None)}:{(0 if target is None else target):0{width}x}'

    def begin_context(self, observation_id: str) -> IngressResult:
        """Reserve byte storage, diagnostics and work before receiving context."""
        self._require_online()
        self._require_idle()
        data = self._online.data
        name(observation_id, 'observation ID')
        if self._cursor >= len(data.active.observation_ids) or observation_id != data.active.observation_ids[self._cursor]:
            raise ContractError('ordinary observation skips/reuses its fixed stream identity or data role')
        spec = data.ingress
        try:
            self._event_router.charge_work('information', {'work': spec.work(len(data.input_upper))}, 'prepay-context-window-copy-decode-and-diagnostics')
        except ResourceExceeded as exc:
            return IngressResult('UNRESOLVED', None, observation_id, self._cursor, 0, 0, str(exc))
        self._revision += 1
        ingress_id = f'{self._runtime_id}:ingress:{self._revision}'
        allocated_ids = ()
        try:
            candidates = tuple(s.candidate_id for s in self._candidates.values() if s.range_safe)
            if any(self._candidates[key].learner.cursor != self._cursor for key in candidates):
                raise ContractError('an active reference lineage lost the common exogenous cursor')
            admitted = tuple(key for key, state in self._persistence_identities.items()
                             if state.status in ('ACTIVE', 'REFERENCE_CROSSED', 'FLOAT64_CROSSED'))
            for key in admitted:
                self._check_persistence_lineages(self._persistence_identities[key])
            identity = IngressIdentity(ingress_id, observation_id, self._cursor, spec.capacity,
                f'{ingress_id}:bytes', f'{ingress_id}:control', f'{ingress_id}:identity', candidates, admitted)
            metadata = self._machine.realize(identity.record_id, 'context_ingress_identity', identity, self._chi)
            body = ObjectSpec(identity.body_id, 'reserved_context',
                {'reference_payload_bytes': spec.capacity, 'physical_objects': 1}, self._chi)
            control = ObjectSpec(identity.control_id, 'ingress_control',
                {'reference_payload_bytes': spec.control_bytes, 'physical_objects': 1}, self._chi)
            # The capacity check precedes creation of the potentially large
            # zero window. No input byte has been offered or received yet.
            self._ledger.prepare_allocation(self._data_owner, (body, control, metadata.spec))
            allocated_ids = (body.object_id, control.object_id, metadata.spec.object_id)
            self._allocate(self._data_owner, (PackedObject(body, bytes(spec.capacity)),
                PackedObject(control, control_payload(0, 'RECEIVING', spec)), metadata))
            identities = dict(self._ingress_identities)
            identities[ingress_id] = identity
            next_root = dict(self.__dict__)
            next_root.update(_ingress_identities=identities, _active_ingress=ingress_id,
                             _event_phase='receiving-context')
            result = IngressResult('RECEIVING', ingress_id, observation_id, self._cursor, 0, spec.chunk_bytes)
        except MemoryError:
            raise
        except Exception as exc:
            # Only predetermined empty storage can be discarded here: no
            # receive operation has run. Preserve paid work/peak/retired IDs.
            live = self._ledger.snapshot()['objects']
            releases = tuple((self._data_owner, key, 1) for key in allocated_ids if key in live)
            self._ledger.release_many(releases)
            for _, key, _ in releases:
                self._buffers.pop(key, None)
            expected = isinstance(exc, (ResourceExceeded, ArithmeticUnresolved))
            self._attempts.append((ingress_id, 'UNRESOLVED' if expected else 'EXECUTION_FAILED', str(exc)))
            if not expected:
                raise
            return IngressResult('UNRESOLVED', None, observation_id, self._cursor, 0, 0, str(exc))
        # Publish only after every fallible preparation and the return value
        # exist. Failed empty-window preparation cannot publish a dangling ID.
        self.__dict__ = next_root
        return result

    def _receiving(self, ingress_id: str):
        name(ingress_id, 'owned ingress identity')
        if self._event_phase != 'receiving-context' or self._active_ingress != ingress_id:
            raise ContractError('context bytes require their current owned receiving window')
        identity = self._ingress_identities[ingress_id]
        received, status = read_control(self._buffers[identity.control_id], self._online.data.ingress)
        if status != 'RECEIVING' or identity.cursor != self._cursor:
            raise ContractError('context ingress is closed or has a different cursor')
        return identity, received

    def receive_context(self, ingress_id: str, offset: int, chunk: bytes) -> IngressResult:
        """Receive exactly the offered bounded prefix; no hidden input suffix."""
        identity, received = self._receiving(ingress_id)
        spec = self._online.data.ingress
        natural(offset, 'context byte offset')
        if type(chunk) is not bytes or not 0 < len(chunk) <= min(spec.chunk_bytes, spec.capacity-received) or offset != received:
            raise ContractError('context chunk violates its fixed byte type, offered window or next offset')
        end = received+len(chunk)
        header = control_payload(end, 'RECEIVING', spec)
        result = IngressResult('RECEIVING', ingress_id, identity.observation_id, self._cursor,
                               end, min(spec.chunk_bytes, spec.capacity-end))
        # Both fixed-size writes were prepaid at admission. No record/counter
        # depends on chunk segmentation. Serialized CPython calls are assumed;
        # arbitrary asynchronous interruption/crash recovery is not claimed.
        self._buffers[identity.body_id][received:end] = chunk
        self._buffers[identity.control_id][:] = header
        return result

    def finish_context(self, ingress_id: str) -> PredictionResult:
        """Decode owned bytes once, then execute the actual ordinary predictor."""
        identity, received = self._receiving(ingress_id)
        spec = self._online.data.ingress
        try:
            payload = bytes(self._buffers[identity.body_id][:received])
            inputs = decode_context(payload, len(self._online.data.input_upper), self._contract.reference_integer_bits)
            self._buffers[identity.control_id][:] = control_payload(received, 'DECODED', spec)
            result = self._predict_received(identity, inputs)
            status = 'PREDICTED' if result.status == 'PREDICTED_REFERENCE' else 'UNRESOLVED'
            self._buffers[identity.control_id][:] = control_payload(received, status, spec)
            if result.status == 'PREDICTED_REFERENCE':
                self._active_ingress = None
            return result
        except MemoryError:
            raise
        except Exception as exc:
            status = 'UNRESOLVED' if isinstance(exc, (ArithmeticUnresolved, ResourceExceeded)) else (
                'INVALID_INPUT' if isinstance(exc, ContractError) and self._event_phase != 'halted' else 'EXECUTION_FAILED')
            self._buffers[identity.control_id][:] = control_payload(received, status, spec)
            if self._event_phase != 'halted':
                self._halt('context-ingress', exc)
            if status != 'UNRESOLVED':
                raise
            return PredictionResult('UNRESOLVED', identity.observation_id, self._cursor, (), str(exc))

    def predict_next(self, observation_id: str, encoded: bytes) -> PredictionResult:
        """One-chunk convenience port; raw values never bypass paid ingress."""
        self._require_online()
        self._require_idle()
        if type(encoded) is not bytes or len(encoded) > self._online.data.ingress.chunk_bytes:
            raise ContractError('predict_next accepts one bounded encoded chunk; use begin/receive/finish for larger frames')
        offer = self.begin_context(observation_id)
        if offer.status == 'UNRESOLVED':
            return PredictionResult('UNRESOLVED', observation_id, self._cursor, (), offer.reason)
        if encoded:
            self.receive_context(offer.ingress_id, 0, encoded)
        return self.finish_context(offer.ingress_id)

    def _predict_received(self, identity: IngressIdentity, inputs) -> PredictionResult:
        data, rules = self._online.data, self._contract.semantics
        observation_id = identity.observation_id
        inputs = tuple(rational(v, 'pre-target exogenous input') for v in inputs)
        if len(inputs) != len(data.input_upper) or any(v > cap for v, cap in zip(inputs, data.input_upper)):
            raise ContractError('input differs from its registered range/interface')
        # Inputs have already arrived through the owned canonical wire. A
        # failed domain/numeric check retains that prefix and halts ingress.
        sources = read_sources(data, self._cursor, inputs, tuple(self._observations))
        source_map = dict(sources)
        if self._contract.source_domain is not None and tuple(source_map[s.source_id] for s in rules.sources) not in self._contract.source_domain:
            raise ContractError('actual causal context is outside the complete registered source domain')
        if any(s.learner.cursor != self._cursor for s in self._candidates.values() if s.range_safe):
            raise ContractError('an active reference lineage lost the common exogenous cursor')
        if tuple(s.candidate_id for s in self._candidates.values() if s.range_safe) != identity.candidate_ids:
            raise ContractError('the active learner set changed during context ingress')
        record = ObservationRecord(observation_id, data.active.stream_id, data.active.role, self._cursor, inputs, sources, None)
        prefix = f'{self._runtime_id}:event:{self._cursor}'
        predictions, float64_predictions, object_ids = [], [], []
        self._event_phase = 'predicting'
        try:
            for identity_id in identity.persistence_ids:
                self._check_persistence_lineages(self._persistence_identities[identity_id])
            _guard(*inputs, bit_limit=self._contract.reference_integer_bits)
            # Reserve the bounded target slot and its write work before the
            # target arrives. A later backend/resource failure cannot unread it.
            self._event_router.charge_work('information', {'work': len(inputs)+len(sources)+2}, f'{prefix}:ingress')
            context = self._machine.realize(f'{prefix}:context', 'revealed_context', record, self._chi)
            target_slot = self._machine.realize(f'{prefix}:target', 'reserved_target', self._target_slot(None), self._chi)
            self._allocate(self._data_owner, (context, target_slot))
            object_ids.extend((context.spec.object_id, target_slot.spec.object_id))
            self._pending = PendingEvent(record, (), f'{prefix}:target', tuple(object_ids), 'context-revealed', identity.persistence_ids)
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
                floating_prediction = self._float64_execute('predict', program, state.candidate_id, state.learner, state.float64,
                    observation_id=observation_id, sources=source_map, reference_prediction=prediction)
                if floating_prediction is not None:
                    float64_predictions.append((state.candidate_id, floating_prediction))
                predictions.append((state.candidate_id, prediction))
                tape = self._machine.realize(f'{prefix}:{state.candidate_id}:prediction', 'pre_target_prediction',
                                             (state.candidate_id, state.program_id, state.learner, prediction), self._chi)
                self._allocate(self._data_owner, (tape,))
                object_ids.append(tape.spec.object_id)
            self._pending = replace(self._pending, predictions=tuple(predictions), float64_predictions=tuple(float64_predictions), object_ids=tuple(object_ids), stage='predicted')
            self._event_phase = 'awaiting-target'
            return PredictionResult('PREDICTED_REFERENCE', observation_id, self._cursor,
                                    tuple((candidate, pred.probabilities) for candidate, pred in predictions), 'all active reference predictions precede the target')
        except MemoryError:
            raise
        except Exception as exc:
            if self._pending is not None:
                self._pending = replace(self._pending, predictions=tuple(predictions), float64_predictions=tuple(float64_predictions), object_ids=tuple(object_ids), stage='prediction-failed')
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
        self._revision += 1
        pending, cursor = self._pending, self._cursor
        record = replace(pending.record, target=target)
        self._pending = replace(pending, record=record, stage='target-revealed')
        self._event_phase = 'observing'
        self._observations.append(record)
        self._data_usage.record((record,), 'ordinary', self._runtime_id, cursor)
        spec, rules = self._online.learner, self._contract.semantics
        do_commit = (cursor+1) % spec.update_unit == 0
        staged = []
        float64_predictions = dict(pending.float64_predictions)
        try:
            # An in-place write to the already paid, fixed-size owned slot.
            filled = self._machine.realize(pending.target_object_id, 'reserved_target', self._target_slot(target), self._chi)
            if filled.spec.residency['reference_payload_bytes'] != len(self._buffers[pending.target_object_id]):
                raise ContractError('target ingress changed its reserved physical extent')
            slot = self._buffers[pending.target_object_id]
            if type(slot) is not bytearray:
                raise ContractError('target ingress lacks its owned mutable reserved buffer')
            write_packed(filled.value, slot)
            for candidate, prediction in pending.predictions:
                state = self._candidates[candidate]
                program = self._programs[state.program_id]
                self._event_work(state, self._machine.observation_work(program), 'observe-and-accumulate')
                observed = observe_event(program, state.learner, spec, prediction, target,
                                         bit_limit=self._contract.reference_integer_bits)
                floating_successor = self._float64_execute('observe', program, candidate, observed, state.float64,
                    observation_id=record.observation_id, floating_prediction=float64_predictions.get(candidate), target=target)
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
                    floating_successor = self._float64_execute('commit', program, candidate, committed, floating_successor,
                        observation_id=record.observation_id)
                    trace = replace(trace, after_commit=committed)
                    self._event_traces[-1] = trace
                    trace_object = self._machine.realize(f'{prefix}:committed', 'after_optimizer_phase', trace, self._chi)
                    self._allocate(self._data_owner, (trace_object,))
                    evidence = self._range(program, committed.theta, f'{candidate}:commit:{cursor+1}')
                    if not self._safe(evidence):
                        raise ArithmeticUnresolved('registered optimizer successor lacks a sufficient full-domain range/invariant bound')
                final_state = committed if committed is not None else observed
                values = self._machine.realize(f'{prefix}:values', 'ordinary_reference_state', self._learner_payload(final_state, floating_successor), state.program_id)
                checked = self._machine.realize(f'{prefix}:range', 'current_range_evidence', evidence, state.program_id)
                self._allocate(state.physical_owner, (values, checked))
                staged.append(replace(state, learner=final_state, float64=floating_successor, range_evidence=evidence,
                                      object_ids=(state.object_ids[0], values.spec.object_id, checked.spec.object_id)))
            # Evidence uses the sealed pre-target probabilities, only after
            # every learner successor has completed its registered phases.
            # A numerical evidence failure ends that identity; it cannot skip
            # this outcome and continue betting with its old wealth.
            self._observe_persistence(pending, record, {s.candidate_id: s for s in staged})
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
                                     do_commit, 'continuous exact ordinary event; no paired AMP/install authority')
        except MemoryError:
            raise
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
        try:
            self._admit_control('query')
        except ResourceExceeded as exc:
            return QueryResult(query_id, 'UNRESOLVED', (), (), str(exc))
        self._revision += 1
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
        except MemoryError:
            raise
        except Exception as exc:
            error = exc
            result = replace(result, status='EXECUTION_FAILED', reason=f'{type(exc).__name__}: {exc}')
        query_record = QueryRecord(self._cursor, ids, result)
        self._query_records.append(query_record)
        try:
            retained = self._machine.realize(prefix, 'query_transcript', query_record, self._chi)
            self._allocate(self._data_owner, (retained,))
        except MemoryError:
            raise
        except Exception as exc:
            self._halt('retain-query', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return replace(result, status='UNRESOLVED', indices=(), values=(), reason=str(exc))
        if error is not None:
            raise error
        return result

    def _save_persistence(self, identity: PersistenceIdentity):
        previous = self._persistence_identities.get(identity.identity_id)
        generation = 0 if previous is None else previous.generation+1
        object_id = f'{identity.identity_id}:state:{generation}'
        current = replace(identity, object_id=object_id, generation=generation)
        kind = 'reference_persistence_state' if identity.rule.score_path == REFERENCE_PATH else 'binary64_persistence_state'
        packed = self._machine.realize(object_id, kind, current, self._chi)
        self._allocate(identity.owner, (packed,))
        if previous is not None and previous.object_id:
            self._ledger.release(previous.owner, previous.object_id)
            del self._buffers[previous.object_id]
        self._persistence_identities[identity.identity_id] = current
        return current

    def _stop_persistence(self, identity: PersistenceIdentity, reason: str):
        stopped = replace(identity, status='UNRESOLVED', reason=reason)
        try:
            return self._save_persistence(stopped)
        except MemoryError:
            raise
        except Exception as exc:
            # The spent allocation and terminal diagnostic cannot disappear
            # because residency ran out. This fallback has no authority and
            # shares the existing partial model's diagnostic limitation.
            previous = self._persistence_identities.get(identity.identity_id)
            stopped = replace(stopped, object_id='' if previous is None else previous.object_id,
                              reason=f'{reason}; diagnostic retention failed: {type(exc).__name__}: {exc}')
            self._persistence_identities[identity.identity_id] = stopped
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return stopped

    def _check_persistence_lineages(self, identity: PersistenceIdentity):
        base = self._candidates.get(identity.base_lineage_id)
        candidate = self._candidates.get(identity.candidate_lineage_id)
        if (self._deployed_id != identity.base_lineage_id or base is None or candidate is None
                or not base.range_safe or not candidate.range_safe or identity.cursor != self._cursor
                or base.program_id != identity.base_program_id or candidate.program_id != identity.candidate_program_id
                or base.learner != identity.current_base or candidate.learner != identity.current_candidate
                or base.float64 != identity.current_base_float64 or candidate.float64 != identity.current_candidate_float64
                or base.learner.cursor != self._cursor or candidate.learner.cursor != self._cursor):
            raise ContractError('persistence lost its continuous registered candidate/base trajectory')
        if identity.rule.score_path == FLOAT64_PATH:
            for state, bounds in ((base, identity.base_float64_range), (candidate, identity.candidate_float64_range)):
                if state.float64 is None or not bounds or any(b.theta != state.float64.theta for b in bounds):
                    raise ContractError('binary64 persistence lost its current whole-domain invariant')

    def _persistence_float64_range(self, state):
        """Paid proof computation on the declared domain, never fresh data."""
        if state.float64 is None:
            raise ContractError('binary64 persistence has no executed learner')
        program, rules = self._programs[state.program_id], self._contract.semantics
        if tuple((key, len(values)) for key, values in state.float64.delayed) != tuple((s.state_id, s.delay) for s in rules.states):
            raise ContractError('binary64 persistence lost its complete delayed interface')
        rows = (None,) if self._contract.source_domain is None else self._contract.source_domain
        result = []
        for index, row in enumerate(rows):
            work = enclosure_operations(program, rules)*Float64Arithmetic.scalar_work+relation_work(program, rules)
            self._event_router.charge_work('information', {'work': work}, f'{state.candidate_id}:binary64-domain:{index}')
            arith = Float64Arithmetic(self._contract.reference_integer_bits)
            bound = enclose_float64(program, rules, state.float64.theta, source_point=row,
                normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap, arith=arith)
            # A box invariant also needs its actual current complete queue.
            for spec, (state_id, values) in zip(rules.states, state.float64.delayed):
                if state_id != spec.state_id or len(values) != spec.delay:
                    raise ContractError('binary64 persistence lost its complete delayed interface')
                for value in values:
                    if compare_exact(value.exact, spec.upper, bit_limit=arith.bit_limit) > 0:
                        raise ArithmeticUnresolved('current binary64 queue violates its whole-domain invariant')
            result.append(bound)
        return tuple(result)

    def admit_reference_persistence(self, candidate_id: str, rule_id: str) -> PersistenceResult:
        """Admit future reference evidence before context ingress; no AMP token."""
        return self._admit_persistence(candidate_id, rule_id, REFERENCE_PATH)

    def admit_float64_persistence(self, candidate_id: str, rule_id: str) -> PersistenceResult:
        """Admit CPU stored-mass CE evidence with its own global alpha debit."""
        return self._admit_persistence(candidate_id, rule_id, FLOAT64_PATH)

    def _admit_persistence(self, candidate_id: str, rule_id: str, score_path: str) -> PersistenceResult:
        self._require_online()
        self._require_idle()
        name(candidate_id, 'persistence candidate lineage')
        name(rule_id, 'registered persistence rule')
        registration = self._online.persistence
        if registration is None:
            raise ContractError('no registered persistence protocol')
        rule = next((r for r in registration.rules if r.rule_id == rule_id), None)
        if rule is None or rule.score_path != score_path:
            raise ContractError('unregistered or wrong-path persistence rule')
        candidate = self._candidates.get(candidate_id)
        base = self._candidates[self._deployed_id]
        if candidate is None or candidate_id == self._deployed_id:
            raise ContractError('persistence requires an owned distinct candidate lineage')
        if self._cursor % self._online.learner.update_unit or candidate.learner.cursor != self._cursor:
            raise ContractError('persistence starts at a shared ordinary update boundary')
        if not candidate.range_safe or not base.range_safe:
            raise ContractError('persistence requires whole-domain range-safe reference trajectories')
        law = self._online.data.stream_law
        if type(law) is not StochasticStreamLaw:
            return PersistenceResult('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                              'deterministic unread observations do not supply a stochastic persistence law', score_path)
        if rule.epoch_events*rule.max_epochs > len(self._online.data.active.observation_ids)-self._cursor:
            return PersistenceResult('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                              'registered future horizon does not fit the remaining observation schedule', score_path)
        try:
            self._admit_control('admit-persistence')
        except ResourceExceeded as exc:
            return PersistenceResult('UNRESOLVED', None, self._alpha_spent, 0, F(1), None, str(exc), score_path)
        self._revision += 1
        bit_limit = self._contract.reference_integer_bits
        try:
            self._event_router.charge_work('information', {'work': compare_exact_work()+8}, 'persistence:admission-inspection')
            _guard(registration.alpha_total, bit_limit=bit_limit)
            total = _operation(self._alpha_spent, rule.alpha, multiply=False, bit_limit=bit_limit)
            if compare_exact(total, registration.alpha_total, bit_limit=bit_limit) > 0:
                return PersistenceResult('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                                  'global alpha is spent; old identities cannot refund their allocation', score_path)
        except (ResourceExceeded, ArithmeticUnresolved) as exc:
            return PersistenceResult('UNRESOLVED', None, self._alpha_spent, 0, F(1), None, str(exc), score_path)
        identity_id = f'{self._runtime_id}:persistence:{self._next_persistence}'
        self._next_persistence += 1
        owner = f'{identity_id}:owner'
        self._ledger.register_owner(owner, 'compiler')
        allocation = AlphaAllocation(f'{identity_id}:alpha', identity_id, rule.alpha, self._cursor, law, score_path)
        # Allocate the statistical risk before any outcome or fallible physical
        # materialization. Failed admission retains this spent fact forever.
        self._alpha_spent = total
        self._alpha_allocations.append(allocation)
        identity = PersistenceIdentity(identity_id, rule, allocation.allocation_id,
            base.candidate_id, candidate_id, base.program_id, candidate.program_id,
            base.learner, candidate.learner, base.learner, candidate.learner,
            self._cursor, self._cursor, 0, 0, F(0), F(0), F(1), None, None, None,
            'INITIALIZING', owner, '', 0,
            initial_base_float64=base.float64, initial_candidate_float64=candidate.float64,
            current_base_float64=base.float64, current_candidate_float64=candidate.float64)
        self._event_phase = 'admitting-persistence'
        try:
            debit = self._machine.realize(allocation.allocation_id, 'spent_persistence_alpha', allocation, self._chi)
            self._allocate(self._data_owner, (debit,))
            identity = self._save_persistence(identity)
            self._retain_program(base)
            self._retain_program(candidate)
            native_base = self._contract.semantics.base
            if score_path == FLOAT64_PATH:
                base_bounds = self._persistence_float64_range(base)
                candidate_bounds = self._persistence_float64_range(candidate)
                identity = self._save_persistence(replace(identity,
                    base_float64_range=base_bounds, candidate_float64_range=candidate_bounds))
                native_base = tuple(v.exact for v in base_bounds[0].base_lower)
            self._event_router.charge_work('information', {'work': log_enclosure_work(rule.log_terms)+(compare_exact_work()+16)*len(self._contract.semantics.base)+48},
                                          f'{identity_id}:whole-domain-gain-bound')
            add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
            mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
            base_sum = F(0)
            for value in native_base:
                base_sum = add(base_sum, value)
            slack = add(self._contract.normalizer_cap, -base_sum)
            if slack < 0:
                raise ContractError('normalizer cap is below its positive base')
            ratios = tuple(mul(add(slack, b), F(b.denominator, b.numerator)) for b in native_base)
            ratio_bound = ratios[0]
            for ratio in ratios[1:]:
                if compare_exact(ratio, ratio_bound, bit_limit=bit_limit) > 0:
                    ratio_bound = ratio
            bound = log_enclosure(ratio_bound, terms=rule.log_terms, bit_limit=bit_limit)
            if compare_exact(bound.upper, rule.bound, bit_limit=bit_limit) > 0:
                raise ArithmeticUnresolved('registered gain bound is not proved over the full native range class')
            identity = self._save_persistence(replace(identity, ratio_bound=ratio_bound, status='ACTIVE',
                reason=f'future {score_path} epochs admitted under the retained external stochastic-law assumption'))
        except MemoryError:
            raise
        except Exception as exc:
            self._stop_persistence(identity, f'admission failed: {type(exc).__name__}: {exc}')
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
        finally:
            self._event_phase = 'idle'
        return self._persistence_result(identity_id, score_path)

    def _observe_persistence(self, pending: PendingEvent, record: ObservationRecord, successors):
        predictions = dict(pending.predictions)
        finite_predictions = dict(pending.float64_predictions)
        bit_limit = self._contract.reference_integer_bits
        for identity_id in pending.persistence_ids:
            identity = self._persistence_identities[identity_id]
            try:
                self._check_persistence_lineages(identity)
                next_identity = replace(identity, cursor=record.cursor+1,
                    current_base=successors[identity.base_lineage_id].learner,
                    current_candidate=successors[identity.candidate_lineage_id].learner,
                    current_base_float64=successors[identity.base_lineage_id].float64,
                    current_candidate_float64=successors[identity.candidate_lineage_id].float64)
                if identity.rule.score_path == FLOAT64_PATH:
                    for lineage_id, previous, field in (
                        (identity.base_lineage_id, identity.current_base_float64, 'base_float64_range'),
                        (identity.candidate_lineage_id, identity.current_candidate_float64, 'candidate_float64_range')):
                        successor = successors[lineage_id]
                        if successor.float64.theta != previous.theta:
                            next_identity = replace(next_identity, **{field: self._persistence_float64_range(successor)})
                if identity.status in ('REFERENCE_CROSSED', 'FLOAT64_CROSSED'):
                    # Stop the statistic at first crossing, but keep tracking
                    # the same complete learner trajectories. No later reset
                    # or failed ordinary transition inherits a live crossing.
                    self._save_persistence(next_identity)
                    continue
                if identity.status != 'ACTIVE':
                    raise ContractError('an inactive evidence identity reached target scoring')
                # Six guarded interval/ratio comparisons plus fixed rational
                # accumulation, threshold and grid work. This is a primitive
                # reference charge, not a total bit-time/host-heap bound.
                self._event_router.charge_work('information', {'work': log_enclosure_work(identity.rule.log_terms)+6*compare_exact_work()+112+32*len(self._contract.semantics.base)},
                                              f'{identity_id}:score:{record.cursor}')
                self._data_usage.record((record,), 'persistence', identity_id, record.cursor)
                if identity.rule.score_path == REFERENCE_PATH:
                    base = predictions[identity.base_lineage_id].probabilities[record.target]
                    candidate = predictions[identity.candidate_lineage_id].probabilities[record.target]
                else:
                    base = stored_probability(finite_predictions[identity.base_lineage_id], record.target, bit_limit=bit_limit)
                    candidate = stored_probability(finite_predictions[identity.candidate_lineage_id], record.target, bit_limit=bit_limit)
                ratio = _operation(candidate, F(base.denominator, base.numerator), multiply=True, bit_limit=bit_limit)
                k = identity.ratio_bound
                if (compare_exact(ratio, k, bit_limit=bit_limit) > 0
                        or compare_exact(ratio, F(k.denominator, k.numerator), bit_limit=bit_limit) < 0):
                    raise ContractError('actual paired forecasts violate the admitted full-domain gain bound')
                raw = log_enclosure(ratio, terms=identity.rule.log_terms, bit_limit=bit_limit)
                # Intersect only with an already established true-gain bound;
                # never clip a genuinely out-of-range observation into a null.
                lower_bound = -identity.rule.bound if compare_exact(raw.lower, -identity.rule.bound, bit_limit=bit_limit) < 0 else raw.lower
                upper_bound = identity.rule.bound if compare_exact(raw.upper, identity.rule.bound, bit_limit=bit_limit) > 0 else raw.upper
                if compare_exact(lower_bound, upper_bound, bit_limit=bit_limit) > 0:
                    raise ContractError('sound logarithm and native range enclosures do not intersect')
                gain = LogInterval(lower_bound, upper_bound)
                lower = _operation(identity.gain_lower_sum, gain.lower, multiply=False, bit_limit=bit_limit)
                upper = _operation(identity.gain_upper_sum, gain.upper, multiply=False, bit_limit=bit_limit)
                count = identity.epoch_events+1
                finished = count == identity.rule.epoch_events
                wealth = identity.wealth
                epochs = identity.epochs_completed
                if finished:
                    mean = _operation(lower, F(1, count), multiply=True, bit_limit=bit_limit)
                    wealth = next_wealth(wealth, mean, identity.rule, bit_limit=bit_limit)
                    epochs += 1
                event = PersistenceEvent(identity_id, record.observation_id, record.cursor,
                    identity.base_lineage_id, identity.candidate_lineage_id, base, candidate, gain,
                    finished, identity.wealth, wealth, identity.rule.score_path)
                self._persistence_events.append(event)
                kind = 'fresh_reference_persistence_event' if identity.rule.score_path == REFERENCE_PATH else 'fresh_binary64_persistence_event'
                packed = self._machine.realize(f'{identity_id}:event:{record.cursor}', kind, event, self._chi)
                self._allocate(self._data_owner, (packed,))
                next_identity = replace(next_identity, epoch_events=0 if finished else count,
                    epochs_completed=epochs, gain_lower_sum=F(0) if finished else lower,
                    gain_upper_sum=F(0) if finished else upper, wealth=wealth)
                if finished and threshold_crossed(wealth, identity.rule.alpha, bit_limit=bit_limit):
                    crossing = 'REFERENCE_CROSSED' if identity.rule.score_path == REFERENCE_PATH else 'FLOAT64_CROSSED'
                    next_identity = replace(next_identity, status=crossing, crossing_cursor=record.cursor+1,
                        crossing_wealth=wealth, reason=f'conditional {identity.rule.score_path} mean-null crossed; actual AMP and installation remain unverified')
                elif finished and epochs == identity.rule.max_epochs:
                    next_identity = replace(next_identity, status='UNRESOLVED', reason='finite persistence horizon ended without crossing; no rejection')
                self._save_persistence(next_identity)
            except MemoryError:
                raise
            except Exception as exc:
                self._stop_persistence(identity, f'evidence prefix failed at {record.observation_id}: {type(exc).__name__}: {exc}')
                if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                    raise

    def reference_persistence_result(self, identity_id: str) -> PersistenceResult:
        return self._persistence_result(identity_id, REFERENCE_PATH)

    def float64_persistence_result(self, identity_id: str) -> PersistenceResult:
        return self._persistence_result(identity_id, FLOAT64_PATH)

    def _persistence_result(self, identity_id: str, score_path: str) -> PersistenceResult:
        name(identity_id, 'owned persistence identity')
        identity = self._persistence_identities.get(identity_id)
        if identity is None or identity.rule.score_path != score_path:
            raise ContractError('unknown or wrong-path owned persistence identity')
        status = 'UNRESOLVED'
        reason = identity.reason
        crossing = 'REFERENCE_CROSSED' if score_path == REFERENCE_PATH else 'FLOAT64_CROSSED'
        if identity.status == crossing and self._event_phase == 'idle':
            try:
                self._check_persistence_lineages(identity)
                status = crossing
            except ContractError:
                reason = 'historical crossing has no current matching complete trajectory'
        return PersistenceResult(status, identity_id, self._alpha_spent, identity.epochs_completed,
                                          identity.wealth, identity.crossing_cursor, reason, score_path)

    def paired_persistence_result(self, reference_id: str, float64_id: str) -> PairedPersistenceResult:
        """Read two owned same-path crossings; no supplied certificate/token."""
        ref = self._persistence_result(reference_id, REFERENCE_PATH)
        physical = self._persistence_result(float64_id, FLOAT64_PATH)
        a, b = self._persistence_identities[reference_id], self._persistence_identities[float64_id]
        coordinates = ('base_lineage_id', 'candidate_lineage_id', 'base_program_id', 'candidate_program_id',
                       'start_cursor', 'initial_base', 'initial_candidate',
                       'initial_base_float64', 'initial_candidate_float64')
        if any(getattr(a, key) != getattr(b, key) for key in coordinates):
            raise ContractError('paired persistence identities do not start on the same four trajectories')
        if a.rule.epoch_events != b.rule.epoch_events or a.rule.max_epochs != b.rule.max_epochs:
            raise ContractError('paired persistence identities have different registered event schedules')
        crossed = ref.status == 'REFERENCE_CROSSED' and physical.status == 'FLOAT64_CROSSED'
        return PairedPersistenceResult('PAIRED_CPU_CROSSED' if crossed else 'UNRESOLVED', reference_id, float64_id,
            self._cursor, self._alpha_spent, 'both independent same-path statistics crossed on continuous checked CPU learners'
            if crossed else 'both owned current path crossings are required; no evidence is copied between paths')

    def cancel_reference_persistence(self, identity_id: str):
        self._cancel_persistence(identity_id, REFERENCE_PATH)

    def cancel_float64_persistence(self, identity_id: str):
        self._cancel_persistence(identity_id, FLOAT64_PATH)

    def _cancel_persistence(self, identity_id: str, score_path: str):
        self._require_idle()
        name(identity_id, 'owned persistence identity')
        identity = self._persistence_identities.get(identity_id)
        if identity is None or identity.rule.score_path != score_path:
            raise ContractError('unknown or wrong-path owned persistence identity')
        self._admit_control('cancel-persistence')
        self._revision += 1
        self._stop_persistence(identity, 'cancelled; alpha, used observation identities and owned history are retained')

    def _score_reference(self, state: ConstructedState, spec: ReferenceSearchSpec, consumer: str) -> F:
        if not state.range_safe:
            raise ArithmeticUnresolved('reference comparison lacks whole-domain range feasibility')
        available = {r.observation_id: r for r in self._observations}
        if any(obs not in available for obs in spec.observation_ids):
            raise ProfileUnresolved('reference objective observations are not all revealed')
        records = tuple(available[obs] for obs in spec.observation_ids)
        program = self._programs[state.program_id]
        self._retain_program(state)
        work = len(records)*(self._machine.evaluation_work(program, self._contract.semantics)+2)+1
        self._event_router.charge_work('information', {'work': work}, f'{consumer}:reference-objective')
        self._data_usage.record(records, 'proposal', consumer, self._cursor)
        return likelihood(program, self._contract.semantics, state.learner, records,
                          bit_limit=self._contract.reference_integer_bits)

    def _save_search(self, session: ReferenceSearchSession) -> ReferenceSearchSession:
        previous = self._searches.get(session.search_id)
        generation = 0 if previous is None else previous.generation+1
        object_id = f'{session.search_id}:workspace:{generation}'
        current = replace(session, expected_revision=self._revision, generation=generation, object_id=object_id)
        packed = self._machine.realize(object_id, 'complete_reference_search_state', current, session.decision_class_id)
        self._allocate(session.owner, (packed,))
        if previous is not None and previous.object_id:
            self._ledger.release(previous.owner, previous.object_id)
            del self._buffers[previous.object_id]
        self._searches[session.search_id] = current
        return current

    def _search_failure(self, session: ReferenceSearchSession, error: Exception, *, stale=False):
        expected = isinstance(error, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved))
        status = 'STALE_CONTEXT' if stale else ('UNRESOLVED' if expected else 'EXECUTION_FAILED')
        stopped = replace(session, status=status, expected_revision=self._revision, reason=f'{type(error).__name__}: {error}')
        try:
            stopped = self._save_search(stopped)
        except MemoryError:
            raise
        except Exception as retain_error:
            # No successful proof can be activated on this terminal diagnostic
            # state. Python diagnostics are outside the partial payload model.
            previous = self._searches.get(session.search_id)
            stopped = replace(stopped, object_id='' if previous is None else previous.object_id,
                              reason=f'{stopped.reason}; diagnostic retention failed: {type(retain_error).__name__}: {retain_error}')
            self._searches[session.search_id] = stopped
            if not isinstance(retain_error, (ResourceExceeded, ArithmeticUnresolved)):
                raise
        return stopped

    @staticmethod
    def _search_result(session: ReferenceSearchSession) -> ReferenceSearchResult:
        status = session.status if session.status == 'REFERENCE_CLASS_EXHAUSTED' else 'UNRESOLVED'
        compared = sum(row.status == 'COMPARED_REFERENCE' for row in session.rows)
        return ReferenceSearchResult(status, session.search_id, session.decision_class_id, compared,
                                     session.unresolved, session.best_candidate_id, session.best_likelihood,
                                     session.proof_id if status == 'REFERENCE_CLASS_EXHAUSTED' else None,
                                     session.reason or 'a live native region remains; no global or installation authority')

    def start_reference_search(self, search_name: str) -> ReferenceSearchResult:
        self._require_online()
        self._require_idle()
        name(search_name, 'registered reference search name')
        if self._cursor % self._online.learner.update_unit:
            raise ContractError('constructor-class search starts at an ordinary update-unit boundary')
        spec = next((s for s in self._online.searches if s.search_name == search_name), None)
        if spec is None:
            raise ContractError('unregistered native reference decision class')
        try:
            self._admit_control('start-search')
        except ResourceExceeded as exc:
            return ReferenceSearchResult('UNRESOLVED', None, '', 0, 0, None, None, None, str(exc))
        self._revision += 1
        search_id = f'{self._runtime_id}:search:{self._next_search}'
        self._next_search += 1
        class_id = stable_hash(('ordered-native-reference-class-and-baseline-v1', self._chi, spec))
        owner = f'{search_id}:owner'
        self._ledger.register_owner(owner, 'compiler')
        base = self._candidates[self._deployed_id]
        session = ReferenceSearchSession(search_id, class_id, spec, self._cursor, base.candidate_id, base.learner,
                                         None, self._revision, grammar.GrammarCursor(), (), base.candidate_id,
                                         None, 0, 'RUNNING', owner, '', 0)
        self._event_phase = 'searching'
        try:
            self._event_router.charge_work('information', {'work': 1}, f'{search_id}:start')
            session = self._save_search(session)
            if spec.profile_id is not None:
                profile = next(p for p in self._online.profiles if p.profile_id == spec.profile_id)
                self._event_router.charge_work('information', {'work': len(profile.observation_ids)+1}, f'{search_id}:profile-data-admission')
                available = {r.observation_id for r in self._observations}
                if not set(profile.observation_ids) <= available:
                    raise ProfileUnresolved('reference class requires profile observations that are not yet revealed')
            baseline = self._score_reference(base, spec, f'{search_id}:baseline')
            session = self._save_search(replace(session, base_likelihood=baseline, best_likelihood=baseline))
            return self._search_result(session)
        except MemoryError:
            raise
        except Exception as exc:
            session = self._search_failure(session, exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved)):
                raise
            return self._search_result(session)
        finally:
            self._event_phase = 'idle'

    def _compare_native_program(self, session: ReferenceSearchSession, program: Program) -> tuple[ReferenceSearchSession, Exception | None]:
        result = self._construct(program, 'compiler', session.spec.profile_id)
        state = self._candidates.get(result.candidate_id)
        score = None
        error = None
        status, reason = result.status, result.reason
        if result.status == 'BUILT_REFERENCE':
            try:
                score = self._score_reference(state, session.spec, f'{session.search_id}:{session.cursor.emitted}')
                self._event_router.charge_work('information', {'work': 2}, f'{session.search_id}:compare')
                order = compare_likelihoods(score, session.best_likelihood, bit_limit=self._contract.reference_integer_bits)
                status = 'COMPARED_REFERENCE'
            except (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved) as exc:
                status, reason = 'UNRESOLVED', str(exc)
            except MemoryError:
                raise
            except Exception as exc:
                status, reason, error = 'EXECUTION_FAILED', f'{type(exc).__name__}: {exc}', exc
        row = ComparisonRow(session.cursor.emitted, program, program.program_id if state is None else state.program_id, result.candidate_id,
                            status, None if state is None else state.learner, score, reason)
        best_id, best_score = session.best_candidate_id, session.best_likelihood
        if status == 'COMPARED_REFERENCE' and order > 0:
            if best_id != session.base_lineage_id:
                self._retire(best_id)
            best_id, best_score = state.candidate_id, score
        elif state is not None:
            self._retire(state.candidate_id)
        # A constructor's loose range bound, numeric limit or exhaustion is
        # not a negative theorem about that member, much less its descendants.
        unresolved = session.unresolved+int(status != 'COMPARED_REFERENCE')
        return replace(session, rows=session.rows+(row,), best_candidate_id=best_id,
                       best_likelihood=best_score, unresolved=unresolved), error

    def _finish_reference_search(self, session: ReferenceSearchSession) -> ReferenceSearchSession:
        if not session.cursor.done or session.cursor.emitted != len(session.rows):
            raise ContractError('reference proof lacks a closed executed enumeration prefix')
        if session.unresolved or any(r.status != 'COMPARED_REFERENCE' for r in session.rows):
            return self._save_search(replace(session, status='UNRESOLVED', reason='syntax exhausted, but at least one value/feasibility/comparison remains unresolved'))
        if session.base_likelihood is None or session.best_likelihood is None:
            raise ContractError('reference comparison has no evaluated deployed baseline')
        best = self._candidates.get(session.best_candidate_id)
        if best is None or best.learner.cursor != session.ordinary_cursor:
            raise ContractError('winning reference state is not an owned current constructor endpoint')
        if self._cursor != session.ordinary_cursor or self._deployed_id != session.base_lineage_id or self._candidates[self._deployed_id].learner != session.base_state:
            raise ContractError('the compared deployed trajectory changed during reference search')
        available = {r.observation_id: r for r in self._observations}
        records = tuple(available[obs] for obs in session.spec.observation_ids)
        # Verify the fixed proposition, not a solver-provided "best" bit. Every
        # retained endpoint is rebound to its registered value path and rescored.
        values = []
        base_program = self._programs[self._candidates[self._deployed_id].program_id]
        self._event_router.charge_work('information', {'work': len(records)*(self._machine.evaluation_work(base_program, self._contract.semantics)+2)+1}, f'{session.search_id}:verify-baseline')
        self._data_usage.record(records, 'proposal', f'{session.search_id}:verify-baseline', self._cursor)
        checked_base = likelihood(base_program, self._contract.semantics, session.base_state, records,
                                  bit_limit=self._contract.reference_integer_bits)
        if checked_base != session.base_likelihood:
            raise ContractError('retained baseline likelihood differs from its executed reference state')
        values.append(checked_base)
        winner_state = session.base_state if session.best_candidate_id == session.base_lineage_id else None
        winner_score = checked_base if winner_state is not None else None
        winner_program = base_program if winner_state is not None else None
        for ordinal, row in enumerate(session.rows):
            if row.ordinal != ordinal or row.learner is None or self._programs.get(row.program_id) != row.program or not session.spec.grammar.admits(row.program):
                raise ContractError('reference proof contains a missing, reordered or out-of-class endpoint')
            row.program.validate(self._contract.semantics)
            if session.spec.profile_id is None:
                expected = initial_state(row.program, self._contract.semantics,
                                         self._machine.initializer(row.program.slot_count, self._contract.initializer_pattern), self._cursor)
            else:
                profile_record = self._profile_executions.get(row.candidate_id)
                if (profile_record is None or profile_record.status != 'PROFILED_REFERENCE'
                        or profile_record.profile_id != session.spec.profile_id or profile_record.ordinary_cursor != self._cursor
                        or profile_record.program_id != row.program_id or profile_record.candidate_id != row.candidate_id
                        or profile_record.events_completed != profile_record.total_events):
                    raise ContractError('reference row lacks its executed registered profile endpoint')
                expected = profile_record.attached
            if row.learner != expected:
                raise ContractError('reference comparison used a value outside its registered constructor path')
            work = len(records)*(self._machine.evaluation_work(row.program, self._contract.semantics)+2)+row.program.slot_count+1
            self._event_router.charge_work('information', {'work': work}, f'{session.search_id}:verify-row:{ordinal}')
            self._data_usage.record(records, 'proposal', f'{session.search_id}:verify-row:{ordinal}', self._cursor)
            checked = likelihood(row.program, self._contract.semantics, row.learner, records,
                                 bit_limit=self._contract.reference_integer_bits)
            if checked != row.likelihood:
                raise ContractError('retained objective differs from its registered point computation')
            if row.candidate_id == session.best_candidate_id:
                winner_state = row.learner
                winner_score = checked
                winner_program = row.program
            values.append(checked)
        if (winner_state != best.learner or winner_score != session.best_likelihood
                or winner_program != self._programs[best.program_id]):
            raise ContractError('winner is an unexecuted replacement for the compared endpoint')
        self._event_router.charge_work('information', {'work': 2*len(values)}, f'{session.search_id}:verify-reference-maximum')
        verify_maximum(session.best_likelihood, tuple(values), bit_limit=self._contract.reference_integer_bits)
        proof_id = f'{session.search_id}:reference-class-proof'
        proof = ReferenceClassProof(proof_id, self._chi, self._runtime_id, self._revision, session.search_id,
                                    session.decision_class_id, self._cursor, session.base_lineage_id,
                                    session.best_candidate_id, len(session.rows), session.best_likelihood)
        packed = self._machine.realize(proof_id, 'reference_class_proof', proof, session.decision_class_id)
        self._event_router.charge_work('information', {'work': len(session.rows)+1}, f'{session.search_id}:prove-reference-class')
        self._allocate(self._data_owner, (packed,))
        session = self._save_search(replace(session, status='REFERENCE_CLASS_EXHAUSTED', proof_id=proof_id,
                                           reason='all ordered native programs in the registered constructor class compared exactly with the deployed baseline; no install/AMP/population claim'))
        self._reference_proofs[proof_id] = proof
        return session

    def advance_reference_search(self, search_id: str, *, transitions: int) -> ReferenceSearchResult:
        self._require_online()
        self._require_idle()
        name(search_id, 'owned reference search ID')
        natural(transitions, 'reference enumeration step allowance', positive=True)
        if search_id not in self._searches:
            raise ContractError('unknown owned reference search')
        session = self._searches[search_id]
        if session.status != 'RUNNING':
            if session.expected_revision != self._revision:
                return replace(self._search_result(session), status='UNRESOLVED', proof_id=None,
                               reason='historical search result is stale for the complete Runtime context')
            return self._search_result(session)
        stale = session.expected_revision != self._revision
        try:
            self._admit_control('advance-search')
        except ResourceExceeded as exc:
            return replace(self._search_result(session), status='UNRESOLVED', proof_id=None, reason=str(exc))
        self._revision += 1
        if stale:
            session = self._search_failure(session, ProfileUnresolved('complete Runtime context changed outside this search prefix'), stale=True)
            return self._search_result(session)
        self._event_phase = 'searching'
        try:
            for _ in range(transitions):
                # The full cursor and comparison history are owned packed state;
                # no opaque generator frame or caller-supplied frontier is used.
                work = len(session.cursor.nodes)+len(session.cursor.frames)+len(self._contract.semantics.states)+len(self._contract.semantics.base)+3
                self._event_router.charge_work('information', {'work': work}, f'{search_id}:native-step')
                action = grammar.plan(session.cursor, self._contract.semantics, session.spec.grammar)
                successor, program = grammar.apply_checked(session.cursor, action, self._contract.semantics, session.spec.grammar)
                error = None
                if program is not None:
                    updated, error = self._compare_native_program(session, program)
                    if (len(updated.rows) != len(session.rows)+1 or updated.rows[:-1] != session.rows
                            or updated.rows[-1].ordinal != session.cursor.emitted or updated.rows[-1].program != program):
                        raise ContractError('reference comparison substituted a different executed grammar member')
                    session = updated
                session = self._save_search(replace(session, cursor=successor))
                if error is not None:
                    raise error
                if successor.done:
                    session = self._finish_reference_search(session)
                    break
            return self._search_result(session)
        except MemoryError:
            raise
        except Exception as exc:
            session = self._search_failure(session, exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved)):
                raise
            return self._search_result(session)
        finally:
            self._event_phase = 'idle'

    def cancel_reference_search(self, search_id: str):
        self._require_idle()
        name(search_id, 'owned reference search ID')
        if search_id not in self._searches:
            raise ContractError('unknown owned reference search')
        session = self._searches[search_id]
        if session.status == 'CANCELLED':
            return
        self._admit_control('cancel-search')
        self._revision += 1
        # Cancellation terminates continuation, not historical evidence use.
        # Snapshots still expose these records, so their actual packed payload
        # must remain owned. There is no unproved free-and-retain shortcut.
        try:
            self._save_search(replace(session, status='CANCELLED', proof_id=None,
                                      reason='search closed; owned history, constructed winner and spent work retained'))
        except MemoryError:
            raise
        except Exception as exc:
            self._search_failure(session, exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise

    def reference_class_proof(self, proof_id: str, *, decision_class_id: str) -> ReferenceClassProof:
        name(proof_id, 'issued reference proof ID')
        proof = self._reference_proofs.get(proof_id)
        if proof is None:
            raise ContractError('no Runtime-issued reference proof with this identity')
        return self.verify_reference_class_proof(proof, decision_class_id=decision_class_id)

    def verify_reference_class_proof(self, proof: ReferenceClassProof, *, decision_class_id: str) -> ReferenceClassProof:
        name(decision_class_id, 'reference decision class ID')
        if type(proof) is not ReferenceClassProof:
            raise ContractError('a helper-created or altered object is not a Runtime-issued reference proof')
        proof.validate()
        if self._reference_proofs.get(proof.proof_id) != proof:
            raise ContractError('a helper-created or altered object is not a Runtime-issued reference proof')
        session = self._searches.get(proof.search_id)
        if (proof.chi != self._chi or proof.runtime_id != self._runtime_id or proof.issued_revision != self._revision
                or proof.decision_class_id != decision_class_id or session is None
                or session.status != 'REFERENCE_CLASS_EXHAUSTED' or session.proof_id != proof.proof_id
                or session.expected_revision != self._revision or self._event_phase != 'idle'):
            raise ContractError('reference proof has a different class, stale complete context or inactive issuance')
        return proof

    def install(self, candidate_id: str, *unused_authority, **unused_payload) -> ConstructionResult:
        # CPU transition receipts cannot substitute for the complete target
        # resource, numerical and same-path AMP installation obligations.
        return ConstructionResult('UNRESOLVED', None, 'complete ERC-1 enforcement and actual AMP persistence/installation are not yet integrated')

    def install_cpu(self, candidate_id: str, *, proposal_proof_id: str,
                    reference_identity: str, float64_identity: str) -> CpuInstallResult:
        """Execute the registered CPU transaction from owned evidence IDs.

The proposal proof is historical selection provenance, never a claim that
its trained successor is still optimal. Target AMP installation is separate.
The machine is serialized CPython: the complete next root is published once,
after all fallible construction, checks and physical preparation complete.
"""
        self._require_online()
        self._require_idle()
        for value in (candidate_id, proposal_proof_id, reference_identity, float64_identity):
            name(value, 'owned CPU installation identity')
        registration = self._online.cpu_install
        if registration is None:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor, 'no registered CPU install transition')
        registration.__post_init__()
        # Fixed transition schema: a future scheduler/job/cache coordinate
        # cannot silently acquire this version's quiescence/frame proof.
        root_fields = {
            '_contract', '_online', '_host', '_chi', '_runtime_id', '_ledger', '_router', '_event_router', '_machine',
            '_cursor', '_revision', '_next_search', '_searches', '_reference_proofs', '_next_persistence',
            '_alpha_spent', '_alpha_allocations', '_persistence_identities', '_persistence_events',
            '_float64_traces', '_next_install', '_install_attempts', '_install_receipts', '_next_candidate',
            '_ingress_identities', '_active_ingress',
            '_programs', '_retained_programs', '_candidates', '_buffers', '_attempts', '_deployed_id',
            '_event_phase', '_pending', '_observations', '_event_traces', '_profile_executions',
            '_profile_events', '_query_records', '_data_usage', '_halted', '_data_owner',
        }
        if set(self.__dict__) != root_fields:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor, 'CPU install has no transition proof for an unregistered Runtime state coordinate')
        if self._cursor % self._online.learner.update_unit:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor, 'installation cannot discard a partial optimizer unit')
        # Unknown strings cannot become arbitrarily large owned diagnostics.
        # Historical/current authority checks still follow independently.
        if candidate_id not in self._candidates or proposal_proof_id not in self._reference_proofs:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor, 'no owned target or completed reference-class proposal')
        if reference_identity not in self._persistence_identities or float64_identity not in self._persistence_identities:
            raise ContractError('unknown owned persistence identity')
        try:
            self._admit_control('install')
        except ResourceExceeded as exc:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor, str(exc))
        attempt_id = f'{self._runtime_id}:install:{self._next_install}'
        self._next_install += 1
        revision_before = self._revision
        self._revision += 1
        attempt = CpuInstallAttempt(attempt_id, self._cursor, self._deployed_id, candidate_id,
            proposal_proof_id, reference_identity, float64_identity, 'PREPARING')
        self._install_attempts.append(attempt)
        stage_owner = f'{attempt_id}:workspace'
        target_owner, old_owner = f'{attempt_id}:deployment', f'{attempt_id}:old-shadow'
        registered_owners = []
        try:
            # Fixed prepaid work charge in the packed-reference machine.
            # This metric is not elapsed bit-time or complete host accounting.
            objects = self._ledger.snapshot()['objects']
            work = 4096+16*sum(len(buf) for buf in self._buffers.values())+1024*(
                len(objects)+len(self._candidates)+len(self._persistence_identities)+len(self._searches))
            self._ledger.charge_work(registration.work_role, {'work': work}, note=f'{attempt_id}:prepare-complete-root')
            proof = self._reference_proofs.get(proposal_proof_id)
            if proof is None:
                raise ProfileUnresolved('no owned completed reference-class proposal')
            proof.validate()
            search = self._searches.get(proof.search_id)
            if (search is None or search.status != 'REFERENCE_CLASS_EXHAUSTED' or search.proof_id != proof.proof_id
                    or proof.winner_lineage_id != candidate_id or candidate_id == self._deployed_id
                    or proof.base_lineage_id != self._deployed_id or search.best_candidate_id != candidate_id):
                raise ProfileUnresolved('installation target is not the owned selected reference-class proposal')
            paired = self.paired_persistence_result(reference_identity, float64_identity)
            if paired.status != 'PAIRED_CPU_CROSSED':
                raise ProfileUnresolved('both current same-path CPU persistence crossings are required')
            persistence = self._persistence_identities[reference_identity]
            row = next((r for r in search.rows if r.candidate_id == candidate_id), None)
            if (persistence.candidate_lineage_id != candidate_id or row is None
                    or proof.ordinary_cursor != persistence.start_cursor
                    or row.learner != persistence.initial_candidate or search.base_state != persistence.initial_base):
                raise ProfileUnresolved('fresh evidence did not start from the selected proposal and its comparator')
            before = tuple(self._candidates.values())
            target, base = self._candidates[candidate_id], self._candidates[self._deployed_id]
            for state in (target, base):
                if state.learner.unit_count or state.float64.unit_count:
                    raise ProfileUnresolved('installation requires both actual optimizer accumulators to be at a full boundary')
                self._ledger.charge_work(registration.work_role,
                    {'work': relation_work(self._programs[state.program_id], self._contract.semantics)},
                    note=f'{attempt_id}:current-complete-state-bridge')
                check_state(state.learner, state.float64, self._online.float64, bit_limit=self._contract.reference_integer_bits)
            self._event_phase = 'installing'
            for owner, role in ((stage_owner, registration.workspace_role), (target_owner, 'deployment'), (old_owner, 'compiler')):
                self._ledger.register_owner(owner, role)
                registered_owners.append(owner)
            candidates = dict(self._candidates)
            candidates[candidate_id] = replace(target, physical_owner=target_owner)
            candidates[base.candidate_id] = replace(base, physical_owner=old_owner)
            moves, releases = [], []
            for source, destination in ((target.physical_owner, target_owner), (base.physical_owner, old_owner)):
                for obj, info in objects.items():
                    count = info['references'].get(source, 0)
                    if count:
                        moves.append((source, destination, obj, count))
            persistent = dict(self._persistence_identities)
            searches = dict(self._searches)
            invalidated, stopped = [], []
            for key, identity in self._persistence_identities.items():
                if identity.status not in ('ACTIVE', 'REFERENCE_CROSSED', 'FLOAT64_CROSSED'):
                    continue
                obj = f'{attempt_id}:{key}:state:{identity.generation+1}'
                successor = replace(identity, status='UNRESOLVED', generation=identity.generation+1,
                    object_id=obj, reason=f'deployed base changed by {attempt_id}; historical wealth and alpha cannot be rebased')
                self._allocate(stage_owner, (self._machine.realize(obj, 'invalidated_persistence_state', successor, self._chi),))
                persistent[key] = successor
                invalidated.append(key)
                moves.append((stage_owner, identity.owner, obj, 1))
                releases.append((identity.owner, identity.object_id, 1))
            for key, session in self._searches.items():
                if session.status in ('CANCELLED', 'CLOSED_BY_INSTALL'):
                    continue
                obj = f'{attempt_id}:{key}:workspace:{session.generation+1}'
                successor = replace(session, status='CLOSED_BY_INSTALL', expected_revision=self._revision,
                    generation=session.generation+1, object_id=obj, proof_id=None,
                    reason=f'closed by {attempt_id}; frontier, constructed witnesses and history retained without continuation')
                self._allocate(stage_owner, (self._machine.realize(obj, 'closed_reference_search_state', successor, session.decision_class_id),))
                searches[key] = successor
                stopped.append(key)
                moves.append((stage_owner, session.owner, obj, 1))
                if session.object_id:
                    releases.append((session.owner, session.object_id, 1))
            receipt_id = f'{attempt_id}:receipt'
            moves.append((stage_owner, self._data_owner, receipt_id, 1))
            close = (target.physical_owner, base.physical_owner, stage_owner)
            completed = replace(attempt, status='INSTALLED_CPU', reason='owned complete CPU root and buffer leases published at the same cursor')
            receipt = CpuInstallReceipt(completed, revision_before, self._revision, before, tuple(candidates.values()),
                tuple(moves), tuple(releases), close, tuple(invalidated), tuple(stopped), receipt_id)
            self._allocate(stage_owner, (self._machine.realize(receipt_id, 'prepared_cpu_install_receipt', receipt, self._chi),))
            ledger = self._ledger.prepare_transfer(tuple(moves), tuple(releases), close)
            live = ledger.snapshot()['objects']
            buffers = {key: value for key, value in self._buffers.items() if key in live}
            if set(buffers) != set(live):
                raise ContractError('prepared installation has ledger objects without actual retained buffers')
            # Only role ownership changes. No learner numerical buffer is
            # recast, copied, reset, freed, or replaced during installation.
            for prior in before:
                successor = candidates[prior.candidate_id]
                if replace(successor, physical_owner=prior.physical_owner) != prior:
                    raise ContractError('installation changed a certified complete learner')
                if any(buffers[obj] is not self._buffers[obj] for obj in prior.object_ids):
                    raise ContractError('installation substituted a learner buffer')
            result = CpuInstallResult('INSTALLED_CPU', attempt_id, candidate_id, self._cursor,
                'registered CPU transaction completed; past class selection and fresh two-path evidence remain distinct claims')
            next_root = dict(self.__dict__)
            next_root.update(_ledger=ledger, _router=CostRouter(ledger, self._contract.work_roles),
                _event_router=CostRouter(ledger, self._event_router.snapshot()), _buffers=buffers,
                _candidates=candidates, _deployed_id=candidate_id, _persistence_identities=persistent,
                _searches=searches, _install_attempts=self._install_attempts[:-1]+[completed],
                _install_receipts=self._install_receipts+[receipt], _event_phase='idle')
        except MemoryError:
            raise
        except Exception as exc:
            # All allocations happened against the live old root. Abort frees
            # only prepared objects; real work/peak/attempt history stay spent.
            cleanup_errors = []
            for owner in registered_owners:
                try:
                    self._release_owner(owner)
                except MemoryError:
                    raise
                except Exception as cleanup:
                    cleanup_errors.append(f'{type(cleanup).__name__}: {cleanup}')
            expected = isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved))
            failed = replace(attempt, status='UNRESOLVED' if expected else 'EXECUTION_FAILED',
                reason=f'{type(exc).__name__}: {exc}'+(' ; cleanup: '+'; '.join(cleanup_errors) if cleanup_errors else ''))
            self._install_attempts[-1] = failed
            self._event_phase = 'idle'
            if cleanup_errors:
                self._halt('install-cleanup', RuntimeError(failed.reason))
            if not expected:
                raise
            return CpuInstallResult('UNRESOLVED', attempt_id, None, self._cursor, failed.reason)
        # The only publication point. Everything fallible and the result
        # object have been prepared. The registered API has serialized calls;
        # crash recovery or concurrent external readers are not claimed.
        self.__dict__ = next_root
        return result

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(self._chi, self._runtime_id, self.recovery_phase, self._cursor,
                               self._deployed_id, self._next_candidate, tuple(self._programs.items()),
                               tuple(self._candidates.values()), self._ledger.snapshot(),
                               tuple((key, bytes(value) if type(value) is bytearray else value) for key, value in self._buffers.items()), tuple(self._attempts),
                               self._online, self._event_phase, self._pending, tuple(self._observations),
                               tuple(self._event_traces), self._data_usage.snapshot(), tuple(self._query_records), self._halted,
                               tuple(self._retained_programs.items()), tuple(self._profile_executions.values()), tuple(self._profile_events),
                               self._revision, self._next_search, tuple(self._searches.values()), tuple(self._reference_proofs.values()),
                               self._next_persistence, self._alpha_spent, tuple(self._alpha_allocations),
                               tuple(self._persistence_identities.values()), tuple(self._persistence_events), tuple(self._float64_traces),
                               self._next_install, tuple(self._install_attempts), tuple(self._install_receipts),
                               tuple(IngressSnapshot(identity, *read_control(self._buffers[identity.control_id], self._online.data.ingress))
                                     for identity in self._ingress_identities.values()), self._active_ingress,
                               None if self._host is None else self._host.observe())
