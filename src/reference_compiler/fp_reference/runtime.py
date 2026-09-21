"""Owned construction, causal events, reference selection, evidence and installation.

Registered CPU/CUDA installation executes; complete target release remains open.
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
from .learner import SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState, commit_event, initial_state, observe_event
from .machine import PackedObject, PlannedObject, ReferenceMachineModel
from .indexed_relation import IndexedRelation, DecodeAllowance
from .indexed_execution import (IndexedInitializer, IndexedLearner, CategoricalPairDomain,
    IndexedState, IndexedEvaluation, IndexedRangeBound, IndexedReferenceMachine)
from .encoding import packed_size, write_packed, fragments
from .host_failure import guard_host_allocations
from .host_resources import HostResourceContract, HostResourceObservation, HostExecutionUnresolved, _WindowsProcessHost
from .policy import (CompilerPolicy, CudaCompilerPolicy, CompilerPolicyState, CompilerPolicySnapshot,
                     CompilationState, CudaCompilationState, TERMINAL_STAGES)
from .run_state import ReferenceRunManifest, ReferenceRunClosure, ReferenceRunSnapshot, RunDecision, prediction_diagnostics
from .program import Program, SemanticRules, name, rational
from .profile import ProfileEvent, ProfileExecution, ProfileSpec, ProfileUnresolved, attach_boundary
from .numerics import LogInterval, compare_exact, compare_exact_work, log_enclosure, log_enclosure_work
from .persistence import PersistenceContract, ArcsinePersistenceRule, REFERENCE_PATH, FLOAT64_PATH, CUDA_PATH, CROSSINGS, LIVE_STATUSES, next_wealth, threshold_crossed
from .persistence_state import AlphaAllocation, PersistenceEvent, PersistenceIdentity, PersistenceResult, PairedPersistenceResult
from .persistence_bounds import paired_mass_ratio_bound, mass_box_work
from . import persistence_mixture as mixture
from .binary_arithmetic import BINARY64, Float64Arithmetic
from . import float64_learner as finite
from .cuda_prefix import (CudaPrefixContract, IndexedCudaPrefixContract, CudaRunManifest,
    CudaPrefixSnapshot, _CudaPrefix, widened_state)
from .cuda_range import forward_work, enclose_cuda, check_queue, stored_probability as cuda_stored_probability
from .cuda_persistence import CudaPersistenceIdentity, CudaPersistenceResult, PairedCudaPersistenceResult
from .cuda_installation import CudaInstallAttempt, CudaInstallReceipt, CudaInstallResult, prepare_transport, verify_transport
from .cuda_storage import CudaStorageUnresolved
from .cuda_run import CudaRunClosure, CudaRunSnapshot, cuda_diagnostics
from .float64_bridge import Float64Contract, Float64Relation, check_state, check_prediction, relation_work
from .float64_range import enclose_float64, enclosure_operations, stored_probability
from .installation import CpuInstallContract, CpuInstallAttempt, CpuInstallReceipt, CpuInstallResult
from .ingress import IngressIdentity, IngressSnapshot, IngressResult, control_payload, read_control, decode_context
from . import native_search as grammar
from .proof import ReferenceClassProof, BoundedReferenceProof, verify_maximum
from .search import ComparisonRow, ReferenceSearchResult, ReferenceSearchSession, ReferenceSearchSpec, REFERENCE_SELECTION_COMPLETE, compare_likelihoods, likelihood
from .empirical_bound import empirical_upper, verify_empirical_upper
from .relation_proposal import relation_proposal
from .causal_relation_proposal import SOLVER as CAUSAL_RELATION_SOLVER, causal_relation_proposal, proposal_work_bound
from .simplex_relation_proposal import (SOLVERS as SIMPLEX_RELATION_SOLVERS,
    simplex_relation_proposal, proposal_work_bound as simplex_proposal_work_bound)
from .resources import CostRouter, ObjectSpec, ResourceExceeded, ResourceLedger, ResourceLimits
from .semantics import ArithmeticUnresolved, Evaluation, RangeBound, _guard, _operation, enclose, evaluate, reset_delayed
from .likelihood_encoding import (require_learner as require_likelihood_learner,
    preparation_work as likelihood_preparation_work,
    preparation_workspace as likelihood_preparation_workspace,
    phase_work as likelihood_phase_work)


@dataclass(frozen=True)
class ConstructionContract:
    """The enforced construction slice of ERC-1, not its complete run manifest."""
    semantics: SemanticRules
    limits: ResourceLimits
    work_roles: Mapping[str, str]
    graph_limits: Mapping[str, int]
    initializer_pattern: tuple[F, ...] | IndexedInitializer
    normalizer_cap: F
    activation_cap: F
    reference_integer_bits: int
    source_domain: tuple[tuple[F, ...], ...] | CategoricalPairDomain | None = None

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
        if type(self.initializer_pattern) is IndexedInitializer:
            pattern = self.initializer_pattern
            pattern.__post_init__()
            IndexedRelation(pattern.n).validate(self.semantics)
            if type(self.source_domain) is not CategoricalPairDomain or self.source_domain != CategoricalPairDomain(pattern.n):
                raise ContractError('indexed Gamma requires the complete matching categorical domain')
            self.source_domain.__post_init__()
        else:
            pattern = tuple(rational(v, 'registered initializer') for v in self.initializer_pattern)
            if not pattern:
                raise ContractError('registered initializer pattern is empty')
            if type(self.source_domain) is CategoricalPairDomain:
                raise ContractError('indexed source domain requires its registered indexed realization')
        object.__setattr__(self, 'initializer_pattern', pattern)
        object.__setattr__(self, 'normalizer_cap', rational(self.normalizer_cap, 'normalizer cap', positive=True))
        object.__setattr__(self, 'activation_cap', rational(self.activation_cap, 'activation cap', positive=True))
        natural(self.reference_integer_bits, 'exact reference integer work limit', positive=True)
        if self.source_domain is not None and type(self.source_domain) is not CategoricalPairDomain:
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
    learner: LearnerSpec | IndexedLearner
    queries: tuple[QuerySpec, ...] = ()
    profiles: tuple[ProfileSpec, ...] = ()
    searches: tuple[ReferenceSearchSpec, ...] = ()
    persistence: PersistenceContract | None = None
    float64: Float64Contract | None = None
    cpu_install: CpuInstallContract | None = None

    def __post_init__(self):
        if type(self.data) is not DataContract or type(self.learner) not in (LearnerSpec, IndexedLearner):
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
        indexed = type(construction.initializer_pattern) is IndexedInitializer
        if indexed != (type(self.learner) is IndexedLearner):
            raise ContractError('initializer and learner require the same registered realization')
        if indexed:
            self.learner.__post_init__()
            if self.learner.n != construction.initializer_pattern.n:
                raise ContractError('indexed Gamma and U describe different native slots')
            if self.float64 is not None or self.cpu_install is not None or self.searches:
                raise ContractError('indexed reference realization has no registered physical or native-class search integration yet')
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
                grid = rule.coefficient_grid_bits if type(rule) is ArcsinePersistenceRule else rule.wealth_grid_bits
                if grid >= construction.reference_integer_bits:
                    raise ContractError('persistence numerical grid exceeds reference integer work limit')


@dataclass(frozen=True)
class ConstructedState:
    candidate_id: str
    physical_owner: str
    program_id: str
    birth_cursor: int
    learner: ReferenceLearnerState | IndexedState
    range_evidence: tuple[RangeBound | IndexedRangeBound, ...]
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
    programs: tuple[tuple[str, Program | IndexedRelation], ...]
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
    reference_proofs: tuple[ReferenceClassProof | BoundedReferenceProof, ...]
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
    compiler_policy: CompilerPolicySnapshot | None = None
    run: ReferenceRunSnapshot | None = None
    cuda: CudaPrefixSnapshot | None = None


@guard_host_allocations
class ReferenceCompilerRuntime:
    recovery_phase = 'native-construction-causal-reference'
    # Complete CPU/CUDA installation and terminal run closure use this fixed
    # frame. Adding a scheduler/job/cache requires an explicit transition
    # argument; an unknown coordinate cannot inherit either authority.
    _root_fields = frozenset({
        '_contract', '_online', '_host', '_cuda', '_chi', '_runtime_id', '_ledger', '_router', '_event_router', '_machine',
        '_policy_contract', '_policy_state', '_policy_running',
        '_manifest', '_manifest_object_id', '_run_closure',
        '_cursor', '_revision', '_next_search', '_searches', '_reference_proofs', '_next_persistence',
        '_alpha_spent', '_alpha_allocations', '_persistence_identities', '_persistence_events',
        '_float64_traces', '_next_install', '_install_attempts', '_install_receipts', '_next_candidate',
        '_ingress_identities', '_active_ingress',
        '_programs', '_retained_programs', '_candidates', '_buffers', '_attempts', '_deployed_id',
        '_event_phase', '_pending', '_observations', '_event_traces', '_profile_executions',
        '_profile_events', '_query_records', '_data_usage', '_halted', '_data_owner',
    })

    def __init__(self, contract: ConstructionContract, initial_program: Program, *, online: OnlineContract | None = None,
                 host: HostResourceContract | None = None, policy: CompilerPolicy | CudaCompilerPolicy | None = None,
                 cuda: CudaPrefixContract | None = None):
        if type(contract) is not ConstructionContract:
            raise ContractError('registered construction contract required')
        self._contract = contract
        self._cuda = None
        if cuda is not None:
            if type(cuda) not in (CudaPrefixContract, IndexedCudaPrefixContract) or online is None:
                raise ContractError('actual CUDA prefix needs immutable registration and the ordinary learner interface')
            cuda.__post_init__()
            if cuda.likelihood_encoding is not None:
                require_likelihood_learner(online.learner)
            if policy is not None:
                if type(policy) is not CudaCompilerPolicy:
                    raise ContractError('the CPU install/run policy has no transition proof for a target CUDA root')
                if host is None or policy.steps and cuda.install is None:
                    raise ContractError('owned CUDA policy requires a bound host and registered transport for compilation')
            if contract.reference_integer_bits < 1075:
                raise ArithmeticUnresolved('registered CUDA relation decoding exceeds the reference integer budget')
            if cuda.install is not None:
                if (sys.implementation.name != 'cpython' or online.persistence is None
                        or not {REFERENCE_PATH, CUDA_PATH}.issubset(r.score_path for r in online.persistence.rules)):
                    raise ContractError('CUDA install requires serialized CPython, owned candidate starts and both fresh score paths')
        indexed = type(contract.initializer_pattern) is IndexedInitializer
        if indexed and online is None:
            raise ContractError('indexed realization requires its registered reference learner')
        if cuda is not None and (indexed != (type(cuda) is IndexedCudaPrefixContract)
                or indexed and cuda.n != contract.initializer_pattern.n):
            raise ContractError('reference and CUDA registrations require the same complete native representation')
        machine = (IndexedReferenceMachine(contract.initializer_pattern.n,
            DecodeAllowance(integer_bits=min(32768, contract.reference_integer_bits))) if indexed else ReferenceMachineModel())
        self._host = None if host is None else _WindowsProcessHost(host)
        if online is not None:
            if type(online) is not OnlineContract:
                raise ContractError('registered online continuation required')
            online.validate(contract)
            if (online.persistence is not None and cuda is None
                    and any(r.score_path == CUDA_PATH for r in online.persistence.rules)):
                raise ContractError('CUDA persistence requires its independently executed registered device prefix')
        self._online = online
        if policy is not None:
            if type(policy) is not (CompilerPolicy if cuda is None else CudaCompilerPolicy):
                raise ContractError('registered strategy data required; no policy callback or supplied execution state')
            policy.validate(online)
        self._policy_contract = policy
        self._policy_state = None
        self._policy_running = False
        self._manifest = ReferenceRunManifest(contract, initial_program, online, host, policy,
            machine.model_id, machine.initializer_id,
            (sys.implementation.name, tuple(sys.version_info)),
            None if online is None or online.float64 is None else
            (Float64Arithmetic.backend_id, BINARY64,
             'binary64 storage/source-and-value-casts/PRODUCT/SUM/base/normalizer/division/gradient/optimizer',
             'ordered separate scalar operations, round-nearest-ties-even, gradual subnormals; no FMA or reassociation',
             'each actual primitive checked against exact rounding; nonfinite or mismatch is UNRESOLVED'))
        if cuda is not None:
            self._manifest = CudaRunManifest(self._manifest, cuda)
        self._chi = stable_hash(self._manifest)
        self._runtime_id = secrets.token_hex(12)
        self._manifest_object_id = f'{self._runtime_id}:manifest'
        self._run_closure = None
        self._ledger = ResourceLedger(contract.limits)
        self._router = CostRouter(self._ledger, contract.work_roles)
        # Event, retained evidence and query roles are fixed by this machine
        # implementation before outcomes. No public action can route a debit.
        self._event_router = CostRouter(self._ledger, {'deployment_event': 'deployment',
                                       'compiler_event': 'compiler', 'information': 'compiler'})
        self._machine = machine
        self._cursor = 0
        self._revision = 0
        self._next_search = 0
        self._searches: dict[str, ReferenceSearchSession] = {}
        self._reference_proofs: dict[str, ReferenceClassProof | BoundedReferenceProof] = {}
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
        self._ledger.register_owner(self._data_owner, 'compiler')
        registered = self._machine.realize(self._manifest_object_id, 'immutable_run_manifest', self._manifest, self._chi)
        self._event_router.charge_work('information', {'work': registered.spec.residency['reference_payload_bytes']+1},
                                      'retain-immutable-run-manifest')
        self._allocate(self._data_owner, (registered,))
        if cuda is not None:
            readout_bytes = 8*cuda.phase_output_cells
            self._event_router.charge_work('information', {'work': 4096+readout_bytes}, 'bind-actual-CUDA-prefix-storage')
            readout_id = f'{self._runtime_id}:cuda-raw-readout'
            readout = ObjectSpec(readout_id, 'cuda_raw_readout_workspace',
                {'reference_payload_bytes': readout_bytes, 'physical_objects': 1}, self._chi)
            self._ledger.allocate(self._data_owner, (readout,))
            self._buffers[readout_id] = bytearray(readout_bytes)
            self._cuda = _CudaPrefix(cuda)
        initial = self._construct(initial_program, 'deployment')
        if initial.status != 'BUILT_REFERENCE':
            raise ContractError(f'initial registered reference realization failed: {initial.status}: {initial.reason}')
        self._deployed_id = initial.candidate_id
        if policy is not None:
            state_type = CompilationState if cuda is None else CudaCompilationState
            self._save_policy(tuple(state_type() for _ in policy.steps))

    @property
    def contract(self):
        return self._contract

    @property
    def chi(self):
        return self._chi

    @property
    def online_contract(self):
        return self._online

    def _seal_run(self):
        """Close the registered ordinary horizon after the owned control phase.

        This is a separate transition from a successful event or installation.
        On failure those completed prefixes survive; no run closure is issued.
        Manual endpoint mode has no owned complete strategy to close here.
        """
        if (self._policy_contract is None or self._halted is not None
                or self._cursor != len(self._online.data.active.observation_ids)):
            return
        try:
            self._require_idle()
            if set(self.__dict__) != self._root_fields:
                raise ContractError('run closure has no frame proof for an unregistered Runtime coordinate')
            if self._pending is not None or self._active_ingress is not None or self._policy_running:
                raise ContractError('a pending Runtime phase cannot become a completed run')
            # Reporting is real work and storage. The complete snapshot's
            # ledger includes this debit and the closure buffer itself.
            work = 4096+64*sum(len(value) for value in self._buffers.values())
            self._event_router.charge_work('information', {'work': work}, 'complete-reference-run-report')
            before = tuple(self._candidates.values()) if self._cuda is not None else ()
            transport = prepare_transport(self._cuda, before) if self._cuda is not None else None
            historical = {proof.search_id: proof for proof in self._reference_proofs.values()}
            decisions = tuple(RunDecision(s.search_id, s.decision_class_id, s.spec,
                s.ordinary_cursor, s.base_lineage_id, s.status,
                ('HISTORICAL_REFERENCE_CLASS_BOUNDED' if type(historical.get(s.search_id)) is BoundedReferenceProof
                 else 'HISTORICAL_REFERENCE_CLASS_EXHAUSTED') if s.search_id in historical else 'UNRESOLVED',
                historical.get(s.search_id))
                for s in self._searches.values())
            stages = tuple((i, stage.status if stage.status in TERMINAL_STAGES else 'UNRESOLVED',
                            stage.reason if stage.status in TERMINAL_STAGES else 'registered stream ended before this policy stage concluded')
                           for i, stage in enumerate(self._policy_state.stages))
            reference = (trace.prediction for traces in (self._event_traces, self._profile_events) for trace in traces)
            diagnostics = [prediction_diagnostics(reference, 'exact-reference', self._contract.reference_integer_bits)]
            if self._online.float64 is not None:
                floating = (trace.float64_prediction for trace in self._float64_traces if trace.float64_prediction is not None)
                diagnostics.append(prediction_diagnostics(floating, 'cpu-binary64', self._contract.reference_integer_bits))
            target_fields = {}
            if self._cuda is not None:
                for state in before:
                    # Includes every retained shadow at its own local clock;
                    # partial optimizer units survive the horizon unchanged.
                    raw = self._cuda_learner_record(state).raw_state
                    self._cuda.check_state(state.learner, raw, bit_limit=self._contract.reference_integer_bits)
                diagnostics.append(cuda_diagnostics(self._cuda, self._contract.reference_integer_bits))
                checked = sum(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in self._cuda.phases.values())
                target_fields = dict(cuda_device=self._cuda._device.snapshot(), cuda_transport=transport[-1],
                    checked_cuda_phases=checked, unresolved_cuda_phases=len(self._cuda.phases)-checked)
            closure_type = ReferenceRunClosure if self._cuda is None else CudaRunClosure
            closure = closure_type(f'{self._runtime_id}:run-closure', self._cursor, self._deployed_id,
                self._policy_state.generation, stages, decisions,
                tuple((key, tuple(program.counts().items())) for key, program in self._programs.items()),
                tuple(diagnostics), self._cursor % self._online.learner.update_unit, self._alpha_spent, **target_fields)
            packed = self._machine.realize(closure.object_id, 'owned_run_closure', closure, self._chi)
            self._event_router.charge_work('information', {'work': packed.spec.residency['reference_payload_bytes']+1},
                                          'retain-reference-run-report')
            self._allocate(self._data_owner, (packed,))
            if self._cuda is not None:
                verify_transport(transport, self._cuda, before)
        except CudaStorageUnresolved:
            raise
        except HostExecutionUnresolved:
            raise
        except MemoryError:
            raise
        except Exception as exc:
            self._halt('run-closure', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise
            return
        # Last, nonallocating publication. No history/lease/alpha is erased.
        # The common public boundary now denies every continuation port.
        self._run_closure = closure

    def _run_snapshot(self):
        status = ('HALTED_UNRESOLVED' if self._halted is not None else
                  self._run_closure.execution if self._run_closure is not None else
                  'MANUAL_PARTIAL' if self._policy_contract is None else 'OPEN_OWNED_STREAM')
        snapshot_type = ReferenceRunSnapshot if self._cuda is None else CudaRunSnapshot
        return snapshot_type(self._manifest, self._manifest_object_id, status, self._run_closure,
            'process/job commitment and observed lifetime CPU; no time cap or GPU claim' if self._host is not None
            else 'UNRESOLVED: packed payload accounting only; no live host resource binding')

    def _next_policy_state(self, stages):
        generation = 0 if self._policy_state is None else self._policy_state.generation+1
        return CompilerPolicyState(stages, generation, f'{self._runtime_id}:policy:{generation}')

    def _save_policy(self, stages):
        current = self._next_policy_state(stages)
        packed = self._machine.realize(current.object_id, 'owned_compiler_policy', current, self._chi)
        self._event_router.charge_work('information', {'work': packed.spec.residency['reference_payload_bytes']+1},
                                      'retain-owned-compiler-policy')
        self._allocate(self._data_owner, (packed,))
        if self._policy_state is not None:
            self._ledger.release(self._data_owner, self._policy_state.object_id)
            del self._buffers[self._policy_state.object_id]
        self._policy_state = current

    def _update_policy(self, index, **values):
        stages = self._policy_state.stages
        self._save_policy(stages[:index]+(replace(stages[index], **values),)+stages[index+1:])

    def _end_policy_evidence(self, index, reason, *, install_attempt=None):
        stage = self._policy_state.stages[index]
        physical_path = FLOAT64_PATH if self._cuda is None else CUDA_PATH
        for identity_id, path in ((stage.reference_identity, REFERENCE_PATH), (stage.physical_identity, physical_path)):
            if identity_id is not None and self._persistence_identities[identity_id].status in LIVE_STATUSES:
                self._cancel_persistence(identity_id, path)
        self._update_policy(index, status='UNRESOLVED', ended_cursor=self._cursor, reason=reason, install_attempt=install_attempt)

    def _advance_policy(self):
        """One deterministic strategy stage at an owned post-commit boundary.

        This executes no user callback and sees no future context/target.
        Existing search/admission/install methods retain all their checks.
        A failed policy-state write halts; its preceding action is never retried.
        """
        if self._cursor % self._online.learner.update_unit:
            return
        cuda = self._cuda is not None
        field = 'cuda_identity' if cuda else 'float64_identity'
        path = CUDA_PATH if cuda else FLOAT64_PATH
        try:
            self._event_router.charge_work('information', {'work': len(self._policy_contract.steps)+1}, 'compiler-policy-boundary')
            index = next((i for i, stage in enumerate(self._policy_state.stages) if stage.status not in TERMINAL_STAGES), None)
            if index is None:
                return
            step, stage = self._policy_contract.steps[index], self._policy_state.stages[index]
            if self._cursor < step.after_cursor:
                return
            self._policy_running = True
            if stage.status == 'WAITING':
                self._update_policy(index, status='STARTING', started_cursor=self._cursor)
                opened = self.start_reference_search(step.search_name)
                self._update_policy(index, status='SEARCHING', search_id=opened.search_id)
                if opened.search_id is None or self._searches[opened.search_id].status != 'RUNNING':
                    self._update_policy(index, status='UNRESOLVED', ended_cursor=self._cursor, reason=opened.reason)
                    return
                selected = self.advance_reference_search(opened.search_id, transitions=step.search_transitions)
                complete = selected.status in REFERENCE_SELECTION_COMPLETE
                if not complete:
                    # An exhausted policy allowance is not grammar exhaustion.
                    # End the actual owned frontier; no hidden caller can resume it.
                    if self._searches[opened.search_id].status == 'RUNNING':
                        self.cancel_reference_search(opened.search_id)
                    # A paid actually compared candidate may enter a new fresh
                    # decision while the full class remains unresolved. This
                    # grants no maximum, pruning or inherited evidence claim.
                    if selected.best_candidate_id in (None, self._deployed_id):
                        self._update_policy(index, status='UNRESOLVED', ended_cursor=self._cursor,
                            candidate_id=selected.best_candidate_id,
                            reason='native class unresolved and no compared proposal improves the observed baseline')
                        return
                values = dict(candidate_id=selected.best_candidate_id, proof_id=selected.proof_id)
                if selected.best_candidate_id == self._deployed_id:
                    self._update_policy(index, status='BASELINE_SELECTED', ended_cursor=self._cursor, **values)
                    return
                self._update_policy(index, status='ADMITTING_REFERENCE', **values)
                reference = self.admit_reference_persistence(selected.best_candidate_id, step.reference_rule)
                self._update_policy(index, status='ADMITTING_CUDA' if cuda else 'ADMITTING_FLOAT64', reference_identity=reference.identity_id)
                admission = self.admit_cuda_persistence if cuda else self.admit_float64_persistence
                floating = admission(selected.best_candidate_id, step.physical_rule)
                self._update_policy(index, status='EVIDENCE', **{field: floating.identity_id})
                ids = reference.identity_id, floating.identity_id
                if any(key is None or self._persistence_identities[key].status != 'ACTIVE' for key in ids):
                    self._end_policy_evidence(index,
                        f'reference admission {reference.status}: {reference.reason}; '
                        f'{path} admission {floating.status}: {floating.reason}; allocations stay spent')
                return
            if stage.status != 'EVIDENCE':
                raise ContractError('incomplete strategy action cannot resume as a new attempt')
            ids = stage.reference_identity, stage.physical_identity
            if any(self._persistence_identities[key].status not in ('ACTIVE', CROSSINGS[REFERENCE_PATH], CROSSINGS[path]) for key in ids):
                self._end_policy_evidence(index, 'paired evidence ended without both current crossings')
                return
            paired = self.paired_cuda_persistence_result if cuda else self.paired_persistence_result
            if paired(*ids).status != ('PAIRED_CUDA_CROSSED' if cuda else 'PAIRED_CPU_CROSSED'):
                return
            self._update_policy(index, status='INSTALLING')
            install = self.install_cuda if cuda else self.install_cpu
            result = install(stage.candidate_id, proposal_proof_id=stage.proof_id,
                             reference_identity=ids[0], **{field: ids[1]})
            if result.status != ('INSTALLED_CUDA' if cuda else 'INSTALLED_CPU'):
                self._end_policy_evidence(index, result.reason, install_attempt=result.attempt_id)
            # Success publishes the completed policy record inside the owned
            # root/lease transaction. There is no allocating bookkeeping here.
        except CudaStorageUnresolved:
            raise
        except HostExecutionUnresolved:
            raise
        except MemoryError:
            raise
        except Exception as exc:
            self._halt('compiler-policy', exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved)):
                raise
        finally:
            self._policy_running = False

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
        if type(self._machine) is IndexedReferenceMachine:
            self._router.charge_work('range_audit', {'work': self._machine.state_work(program)+2*program.n+1},
                                     f'{label}:indexed-all-categorical-range')
            return (self._machine.range_bound(program, self._contract.semantics, theta, self._contract.source_domain),)
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
        # Every existing native phase passes this common private hook even
        # when CPU binary64 is unregistered. CUDA keeps its own lineage state;
        # neither the optional CPU result nor a trained reference endpoint is
        # supplied as its next state.
        result = self._float64_only_execute(kind, program, candidate, reference, floating,
            origin=origin, observation_id=observation_id, sources=sources,
            reference_prediction=reference_prediction, floating_prediction=floating_prediction, target=target)
        if self._cuda is not None:
            self._cuda_execute(kind, program, candidate, reference, origin=origin,
                observation_id=observation_id, sources=sources, reference_prediction=reference_prediction, target=target)
        return result

    def _cuda_execute(self, kind, program, candidate, reference, *, origin, observation_id,
                      sources, reference_prediction, target):
        cfg = self._cuda.contract
        label = f'{candidate}:cuda:{origin}:{kind}:{len(self._cuda.phases)}'
        # In addition to the existing phase charge, prepay six complete raw
        # readbacks, byte decoding/clearing and view/extent checks. This primitive
        # allowance is not a CPU wall-time or total Python-heap theorem.
        # Unencoded simplex commits check both normalizers and their proposal,
        # then the endpoint, prefix and retained trace: six captures in total.
        charge = 320*cfg.phase_output_cells+2*self._cuda.relation_work(program, self._contract.semantics)+cfg.phase_evidence_bytes
        likelihood_workspace = 0
        if cfg.likelihood_encoding is not None:
            # The registered alternative lowering owns its actual program/Gamma
            # derivation and integer state. No caller supplies a likelihood bank
            # or trained value. Descriptor integrity checks are paid by the
            # same finite evidence envelope that retains its initial body.
            charge += 8*cfg.phase_evidence_bytes
            if kind == 'initialize':
                charge += likelihood_preparation_work(program, self._contract.semantics,
                    self._online.learner, self._contract.source_domain, self._contract.reference_integer_bits)
                likelihood_workspace = likelihood_preparation_workspace(program, self._contract.semantics,
                    self._online.learner, self._contract.source_domain, self._contract.reference_integer_bits)
            else:
                handles = self._cuda.staged if origin == 'profile' or kind == 'commit' else self._cuda.current
                physical = self._cuda._values[handles[candidate]]
                if physical.encoding is None:
                    raise ContractError('registered likelihood lowering lost its owned coordinates')
                charge += 4*likelihood_phase_work(physical.encoding.model)
        if kind == 'predict':
            charge += self._cuda.forward_work(program, self._contract.semantics)
        if origin == 'construction':
            self._router.charge_work('construct', {'work': charge}, label)
        else:
            purpose = 'deployment_event' if origin == 'ordinary' and candidate == self._deployed_id else 'compiler_event'
            self._event_router.charge_work(purpose, {'work': charge}, label)
        # A fixed retained frame is paid before any actual device phase. The
        # first eight bytes contain the used encoded length; padding remains
        # part of the physical charge, never an optimistic after-the-fact size.
        extent = ObjectSpec(label, 'owned_cuda_phase_frame',
            {'reference_payload_bytes': cfg.phase_evidence_bytes, 'physical_objects': 1}, self._chi)
        self._ledger.allocate(self._data_owner, (extent,))
        frame = bytearray(cfg.phase_evidence_bytes)
        self._buffers[label] = frame
        # The complete reusable readout extent was owned before CUDA binding.
        # Keep it resident, including when an error traceback retains an alias.
        readout_id = f'{self._runtime_id}:cuda-raw-readout'
        workspace_id = label+':likelihood-scratch' if likelihood_workspace else None
        if workspace_id is not None:
            scratch = ObjectSpec(workspace_id, 'likelihood_derivation_scratch',
                {'reference_payload_bytes': likelihood_workspace, 'physical_objects': 1}, self._chi)
            self._ledger.allocate(self._data_owner, (scratch,))
            self._buffers[workspace_id] = bytearray(likelihood_workspace)

        def write(value):
            size = packed_size(value)
            if size+8 > len(frame):
                raise ResourceExceeded('actual CUDA phase evidence exceeds its prepaid frame')
            offset = 8
            for fragment in fragments(value, packed=True):
                part = fragment.encode('utf-8', 'surrogatepass')
                frame[offset:offset+len(part)] = part
                offset += len(part)
            frame[:8] = size.to_bytes(8, 'big')

        try:
            write((label, 'ADMITTED_CUDA_PHASE'))
            try:
                record, error = self._cuda.execute(label, kind, program, candidate, reference,
                    rules=self._contract.semantics, spec=self._online.learner,
                    bit_limit=self._contract.reference_integer_bits, ordinary_cursor=self._cursor,
                    origin=origin, observation_id=observation_id, sources=sources,
                    reference_prediction=reference_prediction, target=target,
                    normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap,
                    source_domain=self._contract.source_domain, readout_buffer=self._buffers[readout_id])
            except (ResourceExceeded, ArithmeticUnresolved):
                raise
            except ContractError as error:
                # Malformed backend output can also fail raw-record extraction.
                # Already admitted native input cannot become an admissibility
                # rejection just because that internal diagnostic failed too.
                raise RuntimeError('registered CUDA execution or raw capture violated its admitted inputs') from error
            try:
                write(record)
                # The final writer must retain no mutable alias across the
                # publication below, including through a later traceback.
                frame = None
                self._seal_cuda_frame(label, origin=origin, candidate=candidate)
            except MemoryError:
                raise
            except Exception as retain_error:
                expected = (ArithmeticUnresolved, ResourceExceeded)
                failure = error if error is not None and not isinstance(error, expected) else retain_error
                self._cuda.phases[label] = replace(record,
                    status='UNRESOLVED' if isinstance(failure, expected) else 'EXECUTION_FAILED',
                    reason=record.reason+'; CUDA evidence retention failed: '+str(retain_error))
                if isinstance(failure, ContractError) and not isinstance(failure, expected):
                    raise RuntimeError('registered CUDA execution violated its admitted inputs') from failure
                raise failure
            if error is not None:
                if isinstance(error, ContractError) and not isinstance(error, (ArithmeticUnresolved, ResourceExceeded)):
                    raise RuntimeError('registered CUDA execution violated its admitted inputs') from error
                raise error
            self._cuda.accept(record)
        finally:
            if workspace_id is not None:
                self._ledger.release(self._data_owner, workspace_id)
                self._buffers.pop(workspace_id, None)

    def _seal_cuda_frame(self, label, *, origin, candidate):
        """Retain every completed frame byte once, with paid copy coexistence.

        Only the registered final CUDA writer calls this private operation.
        Snapshots already expose bytes; immutable frames can be shared by all
        future snapshots. This does not seal a run or grant phase authority.
        """
        extent = self._ledger._objects[label]
        if (extent.kind != 'owned_cuda_phase_frame' or extent.provenance != self._chi
                or self._ledger._refs[label] != {self._data_owner: 1}
                or type(self._buffers[label]) is not bytearray
                or extent.residency != {'reference_payload_bytes': len(self._buffers[label]), 'physical_objects': 1}):
            raise ContractError('finalization requires the single owned mutable CUDA evidence frame')
        # Count a conservative envelope for the detached ledger/root copies as
        # well as every copied payload byte. This is primitive work, not a
        # bit-time or complete Python-heap bound. No old frame bytes are read
        # while deriving the fee.
        ledger = self._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)
                   +len(ledger._events)+len(ledger._owners)+len(ledger._retired)
                   +len(self._buffers)+len(self.__dict__)+16)
        work = len(self._buffers[label])+64*entries
        if origin == 'construction':
            self._router.charge_work('construct', {'work': work}, label+':seal-frame')
        else:
            purpose = 'deployment_event' if origin == 'ordinary' and candidate == self._deployed_id else 'compiler_event'
            self._event_router.charge_work(purpose, {'work': work}, label+':seal-frame')
        copy_id = label+':immutable-copy'
        self._ledger.allocate(self._data_owner, (ObjectSpec(copy_id, 'cuda_frame_copy_workspace',
            extent.residency, self._chi),))
        # Exact builtins on an exact bytearray; allocation failure retains the
        # failed paid prefix and is handled by the public MemoryError guard.
        self._buffers[copy_id] = bytes(self._buffers[label])
        # Before the sole publication point, any failure leaves both actual
        # buffers in the old root with live leases. The new root keeps the
        # immutable payload under the same frame label and retires the
        # temporary extent. No local retains the old mutable buffer.
        ledger = self._ledger.prepare_transfer((), ((self._data_owner, copy_id, 1),))
        buffers = dict(self._buffers)
        buffers[label] = buffers.pop(copy_id)
        next_root = dict(self.__dict__)
        next_root.update(_ledger=ledger, _router=CostRouter(ledger, self._contract.work_roles),
            _event_router=CostRouter(ledger, self._event_router.snapshot()), _buffers=buffers)
        self.__dict__ = next_root

    def _float64_only_execute(self, kind, program, candidate, reference, floating=None, *,
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
        except HostExecutionUnresolved:
            raise
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
        except HostExecutionUnresolved:
            raise
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

    def _reference_initial_state(self, program, rules, theta, cursor, *, spec, bit_limit):
        if type(self._machine) is IndexedReferenceMachine:
            return self._machine.initial_state(program, rules, theta, cursor, spec=spec, bit_limit=bit_limit)
        return initial_state(program, rules, theta, cursor, spec=spec, bit_limit=bit_limit)

    def _reference_predict(self, program, rules, state, sources, *, bit_limit, execution_debit):
        if type(self._machine) is IndexedReferenceMachine:
            plan = self._machine.prepare_prediction(program, rules, state, sources, bit_limit=bit_limit)
            # This private debit comes from the already fixed ordinary or
            # profile role. No supplied plan or callback enters a public API.
            execution_debit(self._machine.prediction_execution_work(plan))
            return self._machine.execute_prediction(plan)
        return evaluate(program, rules, state.theta, sources, state.delayed, bit_limit=bit_limit)

    def _reference_observe(self, program, state, spec, prediction, target, *, bit_limit):
        if type(self._machine) is IndexedReferenceMachine:
            return self._machine.observe(program, state, spec, prediction, target, bit_limit=bit_limit)
        return observe_event(program, state, spec, prediction, target, bit_limit=bit_limit)

    def _reference_commit(self, state, spec, *, bit_limit):
        if type(self._machine) is IndexedReferenceMachine:
            return self._machine.commit(state, spec, bit_limit=bit_limit)
        return commit_event(state, spec, bit_limit=bit_limit)

    def _reference_attach(self, state, cursor, spec):
        if type(self._machine) is IndexedReferenceMachine:
            return self._machine.attach(state, cursor, spec)
        return attach_boundary(state, cursor, spec)

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
            if type(program) is not self._machine.program_type:
                if type(program) in (Program, IndexedRelation):
                    raise ArithmeticUnresolved('registered machine has no funded translation for this native-code representation')
                raise ContractError('candidate structure differs from the registered native-code representation')
            if self._machine.node_count(program) > self._contract.graph_limits['nodes'] or program.slot_count > self._contract.graph_limits['slots']:
                raise ContractError('candidate header exceeds a registered native budget')
            counts = program.counts()
            self._router.charge_work('construct', {'work': self._machine.construction_work(program, self._contract.semantics)}, f'{candidate}:construct')
            program.validate(self._contract.semantics)
            if any(counts[key] > cap for key, cap in self._contract.graph_limits.items()):
                raise ContractError('candidate exceeds a registered P/S/edge/slot budget')
            program_id = program.program_id
            if program_id in self._programs and self._programs[program_id] != program:
                raise IdentityUnresolved('content address collision cannot identify distinct native programs')
            zero, delayed = self._machine.zero_payload(program, self._contract.semantics)
            code = self._machine.realize(f'{candidate}:code', 'native_program', program, program_id)
            initial = self._machine.realize(f'{candidate}:zero', 'zero_slot_state', (zero, delayed), program_id)
            self._allocate(owner, (code, initial))
            # Numerical values begin at the immutable initializer. An optional
            # registered profile is executed below, never supplied as theta.
            theta = self._machine.initializer(program.slot_count, self._contract.initializer_pattern)
            spec = None if self._online is None else self._online.learner
            validation_work = self._machine.initializer_validation_work(program, spec)
            if validation_work:
                self._router.charge_work('construct', {'work': validation_work}, f'{candidate}:simplex-initializer-validation')
            learner = self._reference_initial_state(program, self._contract.semantics, theta, self._cursor,
                                    spec=spec, bit_limit=self._contract.reference_integer_bits)
            if self._cuda is not None or self._online is not None and self._online.float64 is not None:
                self._retain_code(program, program_id, code.spec.object_id, candidate)
            floating = self._float64_execute('initialize', program, candidate, learner, origin='construction')
            initialized = self._machine.realize(f'{candidate}:values', 'initialized_reference_state', self._learner_payload(learner, floating), program_id)
            self._router.charge_work('construct', {'work': self._machine.state_work(program)}, f'{candidate}:registered-initialize')
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
            cuda_current = None if self._cuda is None else {**self._cuda.current, candidate: self._cuda.staged[candidate]}
            self._candidates[candidate] = state
            self._programs[program_id] = program
            self._attempts.append((candidate, status, reason))
            if self._cuda is not None:
                self._cuda.current = cuda_current
            return result
        except (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved, IdentityUnresolved) as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'UNRESOLVED', str(exc)))
            return ConstructionResult('UNRESOLVED', None, str(exc))
        except ContractError as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'REJECTED_ADMISSIBILITY', str(exc)))
            return ConstructionResult('REJECTED_ADMISSIBILITY', None, str(exc))
        except HostExecutionUnresolved:
            raise
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
        if self._cuda is not None:
            self._cuda.current = {key: value for key, value in self._cuda.current.items() if key != candidate_id}
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
            registration = self._cuda.contract.install if self._cuda is not None else self._online.cpu_install
            role = registration.work_role
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
            if identity.status in LIVE_STATUSES:
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
            local = (self._reference_attach(initial.learner, 0, spec) if type(self._machine) is IndexedReferenceMachine
                     else replace(initial.learner, cursor=0))
            local_float64 = self._float64_execute('attach', program, candidate, local, initial.float64, origin='profile')
            work(self._machine.state_work(program)+sum(s.delay for s in rules.states)+1, 'local-clock')
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
                prediction = self._reference_predict(program, rules, local, dict(observation.sources),
                                      bit_limit=self._contract.reference_integer_bits,
                                      execution_debit=lambda amount: work(amount, f'{position}:indexed-table-execution'))
                if prediction.normalizer > self._contract.normalizer_cap or any(v > self._contract.activation_cap for v in self._machine.activation_values(prediction)):
                    raise ContractError('profile execution contradicts a sufficient native range bound')
                float64_prediction = self._float64_execute('predict', program, candidate, local, local_float64,
                    origin='profile', observation_id=observation.observation_id, sources=dict(observation.sources), reference_prediction=prediction)
                event = ProfileEvent(candidate, profile.profile_id, initial.program_id, self._cursor,
                                     position, observation.observation_id, local, prediction)
                self._profile_events.append(event)
                retain(event, 'predicted')
                update(stage='observe')
                work(self._machine.observation_work(program), f'{position}:observe')
                observed = self._reference_observe(program, local, spec, prediction, observation.target,
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
                    work(self._machine.commit_work(program, spec), f'{position}:commit')
                    successor = self._reference_commit(observed, spec, bit_limit=self._contract.reference_integer_bits)
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
            work(self._machine.state_work(program)+sum(s.delay for s in rules.states)+1, 'attach-boundary')
            attached = self._reference_attach(local, self._cursor, spec)
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
        except HostExecutionUnresolved:
            raise
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
                             if state.status in LIVE_STATUSES)
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
        except HostExecutionUnresolved:
            raise
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
        except HostExecutionUnresolved:
            raise
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
        domain = self._contract.source_domain
        source_values = tuple(source_map[s.source_id] for s in rules.sources)
        valid_domain = (domain.contains(source_values) if type(domain) is CategoricalPairDomain
                        else domain is None or source_values in domain)
        if not valid_domain:
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
                prediction = self._reference_predict(program, rules, state.learner, source_map,
                                      bit_limit=self._contract.reference_integer_bits,
                                      execution_debit=lambda amount: self._event_work(state, amount, 'indexed-table-execution'))
                if prediction.normalizer > self._contract.normalizer_cap or any(v > self._contract.activation_cap for v in self._machine.activation_values(prediction)):
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
        except HostExecutionUnresolved:
            raise
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
                observed = self._reference_observe(program, state.learner, spec, prediction, target,
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
                    self._event_work(state, self._machine.commit_work(program, spec), 'optimizer-commit')
                    committed = self._reference_commit(observed, spec, bit_limit=self._contract.reference_integer_bits)
                    floating_successor = self._float64_execute('commit', program, candidate, committed, floating_successor,
                        observation_id=record.observation_id)
                    trace = replace(trace, after_commit=committed)
                    self._event_traces[-1] = trace
                    trace_object = self._machine.realize(f'{prefix}:committed', 'after_optimizer_phase', trace, self._chi)
                    self._allocate(self._data_owner, (trace_object,))
                final_state = committed if committed is not None else observed
                # Whole-domain bounds depend on this fixed Program/contract
                # and theta, not the changing optimizer accumulator or actual
                # delayed queue. They already quantify over every registered
                # source point and the declared delayed invariant. Preserve
                # the actual owned proof object when those dependencies agree.
                self._event_work(state, self._machine.state_work(program)+1, 'range-dependency-check')
                unchanged_range = final_state.theta == state.learner.theta
                if not unchanged_range:
                    evidence = self._range(program, final_state.theta, f'{candidate}:commit:{cursor+1}')
                    if not self._safe(evidence):
                        raise ArithmeticUnresolved('registered optimizer successor lacks a sufficient full-domain range/invariant bound')
                values = self._machine.realize(f'{prefix}:values', 'ordinary_reference_state', self._learner_payload(final_state, floating_successor), state.program_id)
                range_id = state.object_ids[2]
                objects = (values,)
                if not unchanged_range:
                    checked = self._machine.realize(f'{prefix}:range', 'current_range_evidence', evidence, state.program_id)
                    range_id = checked.spec.object_id
                    objects += (checked,)
                self._allocate(state.physical_owner, objects)
                staged.append(replace(state, learner=final_state, float64=floating_successor, range_evidence=evidence,
                                      object_ids=(state.object_ids[0], values.spec.object_id, range_id)))
            # Evidence uses the sealed pre-target probabilities, only after
            # every learner successor has completed its registered phases.
            # A numerical evidence failure ends that identity; it cannot skip
            # this outcome and continue betting with its old wealth.
            self._observe_persistence(pending, record, {s.candidate_id: s for s in staged})
            cuda_current = None if self._cuda is None else {
                **self._cuda.current, **{s.candidate_id: self._cuda.staged[s.candidate_id] for s in staged}}
            candidate_successors = {**self._candidates, **{s.candidate_id: s for s in staged}}
            # Publish every successor together only after every required phase
            # and coexistence check succeeded. Failed work/targets stay retained.
            releases = tuple((self._candidates[s.candidate_id].physical_owner, object_id, 1)
                             for s in staged for object_id in self._candidates[s.candidate_id].object_ids[1:]
                             if object_id not in s.object_ids)
            self._ledger.release_many(releases)
            live = self._ledger.snapshot()['objects']
            self._buffers = {key: value for key, value in self._buffers.items() if key in live}
            self._candidates = candidate_successors
            if self._cuda is not None:
                self._cuda.current = cuda_current
            self._cursor = cursor+1
            self._pending = None
            self._event_phase = 'idle'
            return ObservationResult('OBSERVED_REFERENCE', record.observation_id, cursor, self._cursor,
                                     do_commit, 'continuous exact ordinary event; no paired AMP/install authority')
        except HostExecutionUnresolved:
            raise
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
        except HostExecutionUnresolved:
            raise
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
        except HostExecutionUnresolved:
            raise
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
        kind = {REFERENCE_PATH: 'reference_persistence_state', FLOAT64_PATH: 'binary64_persistence_state',
                CUDA_PATH: 'cuda_persistence_state'}[identity.rule.score_path]
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
        except HostExecutionUnresolved:
            raise
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
        if identity.ratio_bound_kind not in ('native-class-cap', 'current-native-mass-box'):
            raise ContractError('persistence lost its registered ratio-bound proof scope')
        if type(identity.rule) is ArcsinePersistenceRule:
            if (type(identity.mixture_coefficients) is not tuple
                    or len(identity.mixture_coefficients) != identity.epochs_completed+1):
                raise ContractError('persistence lost its owned complete mixture state')
        elif identity.mixture_coefficients is not None:
            raise ContractError('constant persistence acquired an undeclared mixture state')
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
        if type(identity) is CudaPersistenceIdentity:
            if self._cuda is None:
                raise ContractError('CUDA persistence lost its owned device prefix')
            for state, phase_id, bounds in (
                    (base, identity.current_base_cuda, identity.base_cuda_range),
                    (candidate, identity.current_candidate_cuda, identity.candidate_cuda_range)):
                current = self._cuda_learner_record(state)
                if current.object_id != phase_id:
                    raise ContractError('persistence lost its continuous complete CUDA trajectory')
                if identity.rule.score_path == CUDA_PATH and (not bounds or any(b.theta != self._cuda.theta_binding(current.raw_state) for b in bounds)):
                    raise ContractError('CUDA persistence lost its current whole-domain invariant')
        elif identity.rule.score_path == CUDA_PATH:
            raise ContractError('CUDA score identity has no owned CUDA trajectory')

    def _cuda_learner_record(self, state, *, staged=False):
        if self._cuda is None:
            raise ContractError('no registered owned CUDA learner')
        phase_id = (self._cuda.staged if staged else self._cuda.current).get(state.candidate_id)
        record = self._cuda.phases.get(phase_id)
        if (record is None or record.status != 'CHECKED_CUDA_PREFIX_PHASE' or record.raw_state is None
                or record.phase.endswith(':predict') or record.candidate_id != state.candidate_id
                or record.program_id != state.program_id or self._cuda.state_cursor(record.raw_state) != state.learner.cursor):
            raise ContractError('CUDA evidence lost its owned complete learner phase')
        return record

    def _persistence_cuda_range(self, state, *, staged=False):
        """Paid whole-domain proof bound to this root's current device state."""
        program, rules = self._programs[state.program_id], self._contract.semantics
        record = self._cuda_learner_record(state, staged=staged)
        if self._cuda.indexed:
            from .indexed_amp import range_bound
            self._event_router.charge_work('information', {'work': self._cuda.relation_work(program, rules)},
                                          f'{state.candidate_id}:indexed-CUDA-domain')
            return (range_bound(program, rules, record.raw_state, self._contract.source_domain,
                normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap),)
        rows = (None,) if self._contract.source_domain is None else self._contract.source_domain
        bounds = []
        for index, row in enumerate(rows):
            work = forward_work(program, rules, enclosure=True)+relation_work(program, rules)
            self._event_router.charge_work('information', {'work': work}, f'{state.candidate_id}:CUDA-domain:{index}')
            bounds.append(enclose_cuda(program, rules, record.raw_state, source_point=row,
                normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap,
                bit_limit=self._contract.reference_integer_bits))
        return tuple(bounds)

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

    def _persistence_mass_ratio(self, identity, base, candidate):
        """Paid refinement from owned whole-domain bounds, before next ingress.

        The original class cap is tried first at admission. This refinement
        applies to current learners and must be refreshed while evidence is
        active. It never relies on a successful next-query AMP relation.
        """
        rows = 1 if self._contract.source_domain is None or type(self._contract.source_domain) is CategoricalPairDomain else len(self._contract.source_domain)
        labels = len(self._contract.semantics.base)
        bits = self._contract.reference_integer_bits
        self._event_router.charge_work('information', {'work': mass_box_work(rows, labels)
            +log_enclosure_work(identity.rule.log_terms)+compare_exact_work()},
            f'{identity.identity_id}:current-whole-domain-mass-ratio:{identity.cursor}')
        if identity.rule.score_path == REFERENCE_PATH:
            boxes = tuple(tuple(tuple((m.lower, m.upper) for m in bound.masses)
                                for bound in state.range_evidence) for state in (base, candidate))
        else:
            if identity.rule.score_path == FLOAT64_PATH:
                bounds = (identity.base_float64_range, identity.candidate_float64_range)
                read = lambda value: value.exact
            else:
                bounds = (identity.base_cuda_range, identity.candidate_cuda_range)
                read = lambda value: value
            boxes = tuple(tuple(tuple((read(lower), read(upper))
                                      for lower, upper in zip(bound.base_lower, bound.masses_upper))
                                for bound in side) for side in bounds)
        if (any(len(side) != rows for side in boxes)
                or any(len(row) != labels for side in boxes for row in side)):
            raise ContractError('owned mass bounds lost complete source/label coverage')
        ratio = paired_mass_ratio_bound(*boxes, bit_limit=bits)
        bound = log_enclosure(ratio, terms=identity.rule.log_terms, bit_limit=bits)
        if compare_exact(bound.upper, identity.rule.bound, bit_limit=bits) > 0:
            raise ArithmeticUnresolved('current whole-domain mass boxes do not prove the registered gain bound')
        return ratio

    def admit_reference_persistence(self, candidate_id: str, rule_id: str) -> PersistenceResult:
        """Admit future reference evidence before context ingress; no AMP token."""
        return self._admit_persistence(candidate_id, rule_id, REFERENCE_PATH)

    def admit_float64_persistence(self, candidate_id: str, rule_id: str) -> PersistenceResult:
        """Admit CPU stored-mass CE evidence with its own global alpha debit."""
        return self._admit_persistence(candidate_id, rule_id, FLOAT64_PATH)

    def admit_cuda_persistence(self, candidate_id: str, rule_id: str) -> CudaPersistenceResult:
        """Admit fresh actual stored-mass evidence with independent spent alpha."""
        return self._admit_persistence(candidate_id, rule_id, CUDA_PATH)

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
        result_type = CudaPersistenceResult if score_path == CUDA_PATH else PersistenceResult
        if type(law) is not StochasticStreamLaw:
            return result_type('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                              'deterministic unread observations do not supply a stochastic persistence law', score_path)
        if rule.epoch_events*rule.max_epochs > len(self._online.data.active.observation_ids)-self._cursor:
            return result_type('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                              'registered future horizon does not fit the remaining observation schedule', score_path)
        try:
            self._admit_control('admit-persistence')
        except ResourceExceeded as exc:
            return result_type('UNRESOLVED', None, self._alpha_spent, 0, F(1), None, str(exc), score_path)
        self._revision += 1
        bit_limit = self._contract.reference_integer_bits
        try:
            self._event_router.charge_work('information', {'work': compare_exact_work()+8}, 'persistence:admission-inspection')
            _guard(registration.alpha_total, bit_limit=bit_limit)
            total = _operation(self._alpha_spent, rule.alpha, multiply=False, bit_limit=bit_limit)
            if compare_exact(total, registration.alpha_total, bit_limit=bit_limit) > 0:
                return result_type('UNRESOLVED', None, self._alpha_spent, 0, F(1), None,
                                                  'global alpha is spent; old identities cannot refund their allocation', score_path)
        except (ResourceExceeded, ArithmeticUnresolved) as exc:
            return result_type('UNRESOLVED', None, self._alpha_spent, 0, F(1), None, str(exc), score_path)
        identity_id = f'{self._runtime_id}:persistence:{self._next_persistence}'
        self._next_persistence += 1
        owner = f'{identity_id}:owner'
        self._ledger.register_owner(owner, 'compiler')
        allocation = AlphaAllocation(f'{identity_id}:alpha', identity_id, rule.alpha, self._cursor, law, score_path)
        # Allocate the statistical risk before any outcome or fallible physical
        # materialization. Failed admission retains this spent fact forever.
        self._alpha_spent = total
        self._alpha_allocations.append(allocation)
        identity_type, cuda_coordinates = PersistenceIdentity, {}
        if self._cuda is not None:
            identity_type = CudaPersistenceIdentity
            base_phase, candidate_phase = self._cuda.current[base.candidate_id], self._cuda.current[candidate_id]
            cuda_coordinates = dict(initial_base_cuda=base_phase, initial_candidate_cuda=candidate_phase,
                                    current_base_cuda=base_phase, current_candidate_cuda=candidate_phase)
        identity = identity_type(identity_id, rule, allocation.allocation_id,
            base.candidate_id, candidate_id, base.program_id, candidate.program_id,
            base.learner, candidate.learner, base.learner, candidate.learner,
            self._cursor, self._cursor, 0, 0, F(0), F(0), F(1), None, None, None,
            'INITIALIZING', owner, '', 0,
            initial_base_float64=base.float64, initial_candidate_float64=candidate.float64,
            current_base_float64=base.float64, current_candidate_float64=candidate.float64, **cuda_coordinates)
        self._event_phase = 'admitting-persistence'
        try:
            debit = self._machine.realize(allocation.allocation_id, 'spent_persistence_alpha', allocation, self._chi)
            self._allocate(self._data_owner, (debit,))
            identity = self._save_persistence(identity)
            self._retain_program(base)
            self._retain_program(candidate)
            if type(rule) is ArcsinePersistenceRule:
                self._event_router.charge_work('information', {'work': mixture.initial_work()},
                                              f'{identity_id}:mixture-initialization')
                identity = replace(identity, mixture_coefficients=mixture.initial_coefficients(rule, bit_limit=bit_limit))
            native_base = self._contract.semantics.base
            if score_path == FLOAT64_PATH:
                base_bounds = self._persistence_float64_range(base)
                candidate_bounds = self._persistence_float64_range(candidate)
                identity = self._save_persistence(replace(identity,
                    base_float64_range=base_bounds, candidate_float64_range=candidate_bounds))
                native_base = tuple(v.exact for v in base_bounds[0].base_lower)
            elif score_path == CUDA_PATH:
                base_bounds = self._persistence_cuda_range(base)
                candidate_bounds = self._persistence_cuda_range(candidate)
                identity = self._save_persistence(replace(identity,
                    base_cuda_range=base_bounds, candidate_cuda_range=candidate_bounds))
                native_base = base_bounds[0].base_lower
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
                ratio_bound = self._persistence_mass_ratio(identity, base, candidate)
                identity = replace(identity, ratio_bound_kind='current-native-mass-box')
            identity = self._save_persistence(replace(identity, ratio_bound=ratio_bound, status='ACTIVE',
                reason=f'future {score_path} epochs admitted under the retained external stochastic-law assumption'))
        except HostExecutionUnresolved:
            raise
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
                if type(identity) is CudaPersistenceIdentity:
                    next_identity = replace(next_identity,
                        current_base_cuda=self._cuda_learner_record(successors[identity.base_lineage_id], staged=True).object_id,
                        current_candidate_cuda=self._cuda_learner_record(successors[identity.candidate_lineage_id], staged=True).object_id)
                if identity.rule.score_path == FLOAT64_PATH:
                    for lineage_id, previous, field in (
                        (identity.base_lineage_id, identity.current_base_float64, 'base_float64_range'),
                        (identity.candidate_lineage_id, identity.current_candidate_float64, 'candidate_float64_range')):
                        successor = successors[lineage_id]
                        if successor.float64.theta != previous.theta:
                            next_identity = replace(next_identity, **{field: self._persistence_float64_range(successor)})
                if identity.rule.score_path == CUDA_PATH:
                    for lineage_id, previous_id, field in (
                            (identity.base_lineage_id, identity.current_base_cuda, 'base_cuda_range'),
                            (identity.candidate_lineage_id, identity.current_candidate_cuda, 'candidate_cuda_range')):
                        successor = successors[lineage_id]
                        following = self._cuda_learner_record(successor, staged=True)
                        if self._cuda.theta_binding(following.raw_state) != self._cuda.theta_binding(self._cuda.phases[previous_id].raw_state):
                            next_identity = replace(next_identity, **{field: self._persistence_cuda_range(successor, staged=True)})
                        else:
                            self._event_router.charge_work('information',
                                {'work': self._cuda.queue_work(self._programs[successor.program_id], self._contract.semantics)},
                                f'{identity_id}:CUDA-queue:{record.cursor}')
                            self._cuda.check_queue(self._contract.semantics, following.raw_state, bit_limit=bit_limit)
                if identity.status in CROSSINGS.values():
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
                elif identity.rule.score_path == FLOAT64_PATH:
                    base = stored_probability(finite_predictions[identity.base_lineage_id], record.target, bit_limit=bit_limit)
                    candidate = stored_probability(finite_predictions[identity.candidate_lineage_id], record.target, bit_limit=bit_limit)
                else:
                    probabilities = []
                    for lineage_id, input_id in ((identity.base_lineage_id, identity.current_base_cuda),
                                                  (identity.candidate_lineage_id, identity.current_candidate_cuda)):
                        forecast = self._cuda.phases[self._cuda.predicted[lineage_id]]
                        if (forecast.status != 'CHECKED_CUDA_PREFIX_PHASE' or forecast.forward_operations <= 0
                                or forecast.observation_id != record.observation_id or forecast.input_phase != input_id):
                            raise ContractError('CUDA evidence lost its pre-target exact-checked owned forecast')
                        probabilities.append(self._cuda.stored_probability(forecast.raw_prediction, record.target, bit_limit=bit_limit))
                    base, candidate = probabilities
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
                    if type(identity.rule) is ArcsinePersistenceRule:
                        self._event_router.charge_work('information', {'work': mixture.step_work(epochs)},
                            f'{identity_id}:mixture-epoch:{epochs}')
                        coefficients, wealth = mixture.next_mixture(identity.mixture_coefficients,
                            wealth, mean, epochs, identity.rule, bit_limit=bit_limit)
                        next_identity = replace(next_identity, mixture_coefficients=coefficients)
                    else:
                        wealth = next_wealth(wealth, mean, identity.rule, bit_limit=bit_limit)
                    epochs += 1
                event = PersistenceEvent(identity_id, record.observation_id, record.cursor,
                    identity.base_lineage_id, identity.candidate_lineage_id, base, candidate, gain,
                    finished, identity.wealth, wealth, identity.rule.score_path)
                self._persistence_events.append(event)
                kind = {REFERENCE_PATH: 'fresh_reference_persistence_event', FLOAT64_PATH: 'fresh_binary64_persistence_event',
                        CUDA_PATH: 'fresh_cuda_persistence_event'}[identity.rule.score_path]
                packed = self._machine.realize(f'{identity_id}:event:{record.cursor}', kind, event, self._chi)
                self._allocate(self._data_owner, (packed,))
                next_identity = replace(next_identity, epoch_events=0 if finished else count,
                    epochs_completed=epochs, gain_lower_sum=F(0) if finished else lower,
                    gain_upper_sum=F(0) if finished else upper, wealth=wealth)
                if finished and threshold_crossed(wealth, identity.rule.alpha, bit_limit=bit_limit):
                    crossing = CROSSINGS[identity.rule.score_path]
                    next_identity = replace(next_identity, status=crossing, crossing_cursor=record.cursor+1,
                        crossing_wealth=wealth, reason=(f'conditional {identity.rule.score_path} mean-null crossed; actual AMP and installation remain unverified'
                            if identity.rule.score_path != CUDA_PATH else
                            'conditional CUDA stored-mass mean-null crossed; complete AMP bridge, installation and release remain unverified'))
                elif finished and epochs == identity.rule.max_epochs:
                    next_identity = replace(next_identity, status='UNRESOLVED', reason='finite persistence horizon ended without crossing; no rejection')
                if next_identity.status == 'ACTIVE' and next_identity.ratio_bound_kind == 'current-native-mass-box':
                    next_identity = replace(next_identity, ratio_bound=self._persistence_mass_ratio(next_identity,
                        successors[identity.base_lineage_id], successors[identity.candidate_lineage_id]))
                self._save_persistence(next_identity)
            except HostExecutionUnresolved:
                raise
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

    def cuda_persistence_result(self, identity_id: str) -> CudaPersistenceResult:
        return self._persistence_result(identity_id, CUDA_PATH)

    def _persistence_result(self, identity_id: str, score_path: str) -> PersistenceResult:
        name(identity_id, 'owned persistence identity')
        identity = self._persistence_identities.get(identity_id)
        if identity is None or identity.rule.score_path != score_path:
            raise ContractError('unknown or wrong-path owned persistence identity')
        status = 'UNRESOLVED'
        reason = identity.reason
        crossing = CROSSINGS[score_path]
        if identity.status == crossing and self._event_phase == 'idle':
            try:
                self._check_persistence_lineages(identity)
                status = crossing
            except ContractError:
                reason = 'historical crossing has no current matching complete trajectory'
        result_type = CudaPersistenceResult if score_path == CUDA_PATH else PersistenceResult
        return result_type(status, identity_id, self._alpha_spent, identity.epochs_completed,
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

    def paired_cuda_persistence_result(self, reference_id: str, cuda_id: str) -> PairedCudaPersistenceResult:
        """Read current independent owned crossings on the same four learners."""
        ref = self._persistence_result(reference_id, REFERENCE_PATH)
        physical = self._persistence_result(cuda_id, CUDA_PATH)
        a, b = self._persistence_identities[reference_id], self._persistence_identities[cuda_id]
        if type(a) is not CudaPersistenceIdentity or type(b) is not CudaPersistenceIdentity:
            raise ContractError('paired CUDA persistence needs the same owned device root')
        coordinates = ('base_lineage_id', 'candidate_lineage_id', 'base_program_id', 'candidate_program_id',
                       'start_cursor', 'initial_base', 'initial_candidate', 'initial_base_float64', 'initial_candidate_float64',
                       'initial_base_cuda', 'initial_candidate_cuda')
        if any(getattr(a, key) != getattr(b, key) for key in coordinates):
            raise ContractError('paired CUDA persistence identities do not start on the same complete trajectories')
        if a.rule.epoch_events != b.rule.epoch_events or a.rule.max_epochs != b.rule.max_epochs:
            raise ContractError('paired CUDA persistence identities have different registered event schedules')
        crossed = ref.status == 'REFERENCE_CROSSED' and physical.status == 'CUDA_CROSSED'
        return PairedCudaPersistenceResult('PAIRED_CUDA_CROSSED' if crossed else 'UNRESOLVED', reference_id, cuda_id,
            self._cursor, self._alpha_spent, 'both independent same-path statistics crossed on continuous exact-checked CUDA forecasts'
            if crossed else 'both owned current path crossings are required; no evidence is copied between paths')

    def cancel_cuda_persistence(self, identity_id: str):
        self._cancel_persistence(identity_id, CUDA_PATH)

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
        except HostExecutionUnresolved:
            raise
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
        status = session.status if session.status in REFERENCE_SELECTION_COMPLETE else 'UNRESOLVED'
        compared = sum(row.status == 'COMPARED_REFERENCE' for row in session.rows)
        return ReferenceSearchResult(status, session.search_id, session.decision_class_id, compared,
                                     session.unresolved, session.best_candidate_id, session.best_likelihood,
                                     session.proof_id if status in REFERENCE_SELECTION_COMPLETE else None,
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
        except HostExecutionUnresolved:
            raise
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
            except HostExecutionUnresolved:
                raise
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
                self._event_router.charge_work('information',
                    {'work': row.program.slot_count+len(self._online.learner.simplex_slots)+1},
                    f'{session.search_id}:verify-initializer:{ordinal}')
                expected = initial_state(row.program, self._contract.semantics,
                    self._machine.initializer(row.program.slot_count, self._contract.initializer_pattern), self._cursor,
                    spec=self._online.learner, bit_limit=self._contract.reference_integer_bits)
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

    def _advance_bounded_search(self, session: ReferenceSearchSession) -> ReferenceSearchResult:
        """One paid data-derived proposal and an independent universal upper.

        This solver never marks the unexecuted syntax cursor exhausted. Its
        only completion route is a feasible actual endpoint attaining the
        checked upper over a larger class of categorical predictions.
        """
        self._event_phase = 'searching'
        try:
            if session.cursor != grammar.GrammarCursor() or session.rows or session.empirical_upper is not None:
                raise ContractError('bounded solver cannot resume an unrecorded partial action as fresh')
            # Fixed conservative reference allowance for the bounded number
            # of scans/counts/proposal/verification/packed-state copies in this
            # phase. Constructor/profile work is charged separately below.
            work = (4096+64*sum(len(value) for value in self._buffers.values())
                    +64*len(self._contract.initializer_pattern)*(len(session.spec.observation_ids)+1))
            if session.spec.relation_sources.solver == 'empirical-binary-relation-balanced-readout-v4':
                # This registered proposal emits all token-pair products,
                # even when the observed/context buffers are only linear.
                work += 64*len(session.spec.relation_sources.token_atoms)**2
            if session.spec.relation_sources.solver == 'empirical-binary-relation-joint-polynomial-v5':
                # The proposer admits at most one world per available unit
                # coefficient, before expanding its orientation family.
                prefix_slots = min(len(self._contract.initializer_pattern), session.spec.grammar.slots)
                work += 64*len(session.spec.relation_sources.token_atoms)**2*(1+prefix_slots)
            if session.spec.relation_sources.solver == CAUSAL_RELATION_SOLVER:
                work += proposal_work_bound(len(session.spec.relation_sources.token_atoms),
                    len(self._contract.semantics.sources), len(self._contract.semantics.states),
                    len(self._contract.source_domain or ()), session.spec.grammar,
                    len(self._contract.initializer_pattern), len(session.spec.observation_ids), self._cursor)
            if session.spec.relation_sources.solver in SIMPLEX_RELATION_SOLVERS:
                work += simplex_proposal_work_bound(len(session.spec.relation_sources.token_atoms),
                    len(self._contract.source_domain or ()), session.spec.grammar)
            self._event_router.charge_work('information', {'work': work}, f'{session.search_id}:empirical-upper-and-proposal')
            available = {record.observation_id: record for record in self._observations}
            if any(key not in available for key in session.spec.observation_ids):
                raise ProfileUnresolved('the bound requires all registered objective observations to be revealed')
            records = tuple(available[key] for key in session.spec.observation_ids)
            self._data_usage.record(records, 'proposal', f'{session.search_id}:empirical-upper', self._cursor)
            upper = empirical_upper(records, self._contract.semantics, bit_limit=self._contract.reference_integer_bits)
            session = replace(session, empirical_upper=upper)
            session = self._save_search(session)
            verify_empirical_upper(upper, records, self._contract.semantics, bit_limit=self._contract.reference_integer_bits)
            if session.base_likelihood != upper.likelihood:
                self._data_usage.record(records, 'proposal', f'{session.search_id}:relation-derivation', self._cursor)
                if session.spec.relation_sources.solver == CAUSAL_RELATION_SOLVER:
                    profile = next((p for p in self._online.profiles if p.profile_id == session.spec.profile_id), None)
                    range_cap = self._contract.activation_cap
                    if compare_exact(self._contract.normalizer_cap, range_cap,
                                     bit_limit=self._contract.reference_integer_bits) < 0:
                        range_cap = self._contract.normalizer_cap
                    proposal = causal_relation_proposal(upper, self._contract.semantics, session.spec.grammar,
                        self._contract.initializer_pattern, session.spec.relation_sources,
                        data=self._online.data, learner=self._online.learner,
                        source_domain=self._contract.source_domain,
                        range_cap=range_cap,
                        profile=profile, ordinary_cursor=self._cursor,
                        bit_limit=self._contract.reference_integer_bits)
                elif session.spec.relation_sources.solver in SIMPLEX_RELATION_SOLVERS:
                    profile = next((p for p in self._online.profiles if p.profile_id == session.spec.profile_id), None)
                    proposal = simplex_relation_proposal(upper, self._contract.semantics, session.spec.grammar,
                        self._contract.initializer_pattern, session.spec.relation_sources,
                        data=self._online.data, learner=self._online.learner,
                        source_domain=self._contract.source_domain, profile=profile,
                        bit_limit=self._contract.reference_integer_bits)
                else:
                    proposal = relation_proposal(upper, self._contract.semantics, session.spec.grammar,
                        self._contract.initializer_pattern, session.spec.relation_sources,
                        bit_limit=self._contract.reference_integer_bits)
                session = replace(session, relation_proposal=proposal)
                session = self._save_search(session)
                if proposal.program is not None:
                    proposal.program.validate(self._contract.semantics)
                    if not session.spec.grammar.admits(proposal.program):
                        raise ContractError('proposal is outside the complete registered native class')
                    updated, error = self._compare_native_program(session, proposal.program)
                    fixed = replace(updated, rows=session.rows, best_candidate_id=session.best_candidate_id,
                                    best_likelihood=session.best_likelihood, unresolved=session.unresolved)
                    if (fixed != session or len(updated.rows) != len(session.rows)+1
                            or updated.rows[:-1] != session.rows or updated.rows[-1].ordinal != session.cursor.emitted
                            or updated.rows[-1].program != proposal.program):
                        raise ContractError('bounded comparison changed its class/frame or substituted its executed proposal')
                    session = updated
                    session = self._save_search(session)
                    if error is not None:
                        raise error
            if session.best_likelihood != upper.likelihood:
                session = replace(session, status='UNRESOLVED', reason='native proposal did not attain the universal empirical upper; the unsearched grammar remains unresolved')
                return self._search_result(self._save_search(session))

            # Recheck the actual current witness and its constructor origin.
            # The proposal's own status/group labels are not proof premises.
            best = self._candidates.get(session.best_candidate_id)
            base = self._candidates.get(session.base_lineage_id)
            if (best is None or base is None or self._cursor != session.ordinary_cursor
                    or self._deployed_id != session.base_lineage_id or base.learner != session.base_state
                    or best.learner.cursor != self._cursor):
                raise ContractError('bounded comparison changed its deployed or selected complete endpoint')
            if best.candidate_id != base.candidate_id:
                row = next((row for row in session.rows if row.candidate_id == best.candidate_id), None)
                program = self._programs[best.program_id]
                if (row is None or row.status != 'COMPARED_REFERENCE' or row.likelihood != session.best_likelihood
                        or row.program_id != best.program_id or row.program != program or row.learner != best.learner
                        or not session.spec.grammar.admits(program)):
                    raise ContractError('bounded winner lacks its owned in-class construction row')
                if session.spec.profile_id is None:
                    self._event_router.charge_work('information',
                        {'work': program.slot_count+len(self._online.learner.simplex_slots)+1},
                        f'{session.search_id}:verify-bounded-initializer')
                    expected = initial_state(program, self._contract.semantics,
                        self._machine.initializer(program.slot_count, self._contract.initializer_pattern), self._cursor,
                        spec=self._online.learner, bit_limit=self._contract.reference_integer_bits)
                else:
                    profile = self._profile_executions.get(best.candidate_id)
                    if (profile is None or profile.status != 'PROFILED_REFERENCE'
                            or profile.profile_id != session.spec.profile_id or profile.program_id != best.program_id
                            or profile.candidate_id != best.candidate_id
                            or profile.ordinary_cursor != self._cursor or profile.events_completed != profile.total_events):
                        raise ContractError('bounded winner lacks its actual complete registered value profile')
                    expected = profile.attached
                if best.learner != expected:
                    raise ContractError('bounded witness is outside its registered initializer/profile value path')
            checked = self._score_reference(best, session.spec, f'{session.search_id}:verify-bounded-witness')
            checked_base = self._score_reference(base, session.spec, f'{session.search_id}:verify-bounded-base')
            verify_empirical_upper(upper, records, self._contract.semantics, bit_limit=self._contract.reference_integer_bits)
            if checked != upper.likelihood or checked_base != session.base_likelihood:
                raise ContractError('an independently checked endpoint does not attain the universal empirical upper')
            proof_id = f'{session.search_id}:bounded-reference-proof'
            proof = BoundedReferenceProof(proof_id, self._chi, self._runtime_id, self._revision, session.search_id,
                session.decision_class_id, self._cursor, session.base_lineage_id, session.best_candidate_id,
                len(session.rows), checked)
            self._allocate(self._data_owner, (self._machine.realize(proof_id, 'bounded_reference_class_proof', proof, session.decision_class_id),))
            session = replace(session, status='REFERENCE_CLASS_BOUNDED', proof_id=proof_id,
                reason='owned feasible witness attains the checked all-categorical empirical upper; unvisited native syntax was not declared constructed')
            session = self._save_search(session)
            self._reference_proofs[proof_id] = proof
            return self._search_result(session)
        except HostExecutionUnresolved:
            raise
        except MemoryError:
            raise
        except Exception as exc:
            session = self._search_failure(session, exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved)):
                raise
            return self._search_result(session)
        finally:
            self._event_phase = 'idle'

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
        if session.spec.relation_sources is not None:
            # This registered solver has one bounded phase, admitted by any
            # positive phase allowance. It is not one grammar emission or
            # one free work unit: its scans/build/profile are paid below.
            return self._advance_bounded_search(session)
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
        except HostExecutionUnresolved:
            raise
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
        except HostExecutionUnresolved:
            raise
        except MemoryError:
            raise
        except Exception as exc:
            self._search_failure(session, exc)
            if not isinstance(exc, (ResourceExceeded, ArithmeticUnresolved)):
                raise

    def reference_class_proof(self, proof_id: str, *, decision_class_id: str) -> ReferenceClassProof | BoundedReferenceProof:
        name(proof_id, 'issued reference proof ID')
        proof = self._reference_proofs.get(proof_id)
        if proof is None:
            raise ContractError('no Runtime-issued reference proof with this identity')
        return self.verify_reference_class_proof(proof, decision_class_id=decision_class_id)

    def verify_reference_class_proof(self, proof: ReferenceClassProof | BoundedReferenceProof, *, decision_class_id: str) -> ReferenceClassProof | BoundedReferenceProof:
        name(decision_class_id, 'reference decision class ID')
        if type(proof) not in (ReferenceClassProof, BoundedReferenceProof):
            raise ContractError('a helper-created or altered object is not a Runtime-issued reference proof')
        proof.validate()
        if self._reference_proofs.get(proof.proof_id) != proof:
            raise ContractError('a helper-created or altered object is not a Runtime-issued reference proof')
        session = self._searches.get(proof.search_id)
        if (proof.chi != self._chi or proof.runtime_id != self._runtime_id or proof.issued_revision != self._revision
                or proof.decision_class_id != decision_class_id or session is None
                or session.status != ('REFERENCE_CLASS_BOUNDED' if type(proof) is BoundedReferenceProof else 'REFERENCE_CLASS_EXHAUSTED')
                or session.proof_id != proof.proof_id
                or session.expected_revision != self._revision or self._event_phase != 'idle'):
            raise ContractError('reference proof has a different class, stale complete context or inactive issuance')
        return proof

    def install(self, candidate_id: str, *unused_authority, **unused_payload) -> ConstructionResult:
        # CPU transition receipts cannot substitute for the complete target
        # resource, numerical and same-path AMP installation obligations.
        return ConstructionResult('UNRESOLVED', None, 'complete ERC-1 enforcement, target AMP bridge and installation are not yet integrated')

    def install_cpu(self, candidate_id: str, *, proposal_proof_id: str | None = None,
                    reference_identity: str, float64_identity: str) -> CpuInstallResult:
        """Execute the registered CPU transaction from owned evidence IDs.

The proposal proof is historical selection provenance, never a claim that
its trained successor is still optimal. Target AMP installation is separate.
The machine is serialized CPython: the complete next root is published once,
after all fallible construction, checks and physical preparation complete.
"""
        self._require_online()
        self._require_idle()
        if self._cuda is not None:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor,
                                    'CPU install cannot transfer or omit the registered actual CUDA prefix')
        return self._install_owned(candidate_id, proposal_proof_id, reference_identity, float64_identity, FLOAT64_PATH)

    def install_cuda(self, candidate_id: str, *, proposal_proof_id: str | None = None,
                     reference_identity: str, cuda_identity: str) -> CudaInstallResult:
        """Publish an owned complete CUDA learner by registered resident identity transport."""
        return self._install_owned(candidate_id, proposal_proof_id, reference_identity, cuda_identity, CUDA_PATH)

    def _install_owned(self, candidate_id, proposal_proof_id, reference_identity, physical_identity, path):
        self._require_online()
        self._require_idle()
        if path not in (FLOAT64_PATH, CUDA_PATH):
            raise ContractError('unregistered physical installation path')
        cuda = path == CUDA_PATH
        if not cuda and self._cuda is not None:
            return CpuInstallResult('UNRESOLVED', None, None, self._cursor,
                                    'CPU install cannot transfer or omit the registered actual CUDA prefix')
        result_type = CudaInstallResult if cuda else CpuInstallResult
        attempt_type = CudaInstallAttempt if cuda else CpuInstallAttempt
        receipt_type = CudaInstallReceipt if cuda else CpuInstallReceipt
        installed = 'INSTALLED_CUDA' if cuda else 'INSTALLED_CPU'
        for value in (candidate_id, reference_identity, physical_identity):
            name(value, 'owned installation identity')
        if proposal_proof_id is not None:
            name(proposal_proof_id, 'optional historical selection assertion')
        registration = (None if self._cuda is None else self._cuda.contract.install) if cuda else self._online.cpu_install
        if registration is None:
            return result_type('UNRESOLVED', None, None, self._cursor, 'no registered CUDA install transition' if cuda else 'no registered CPU install transition')
        registration.__post_init__()
        # Fixed transition schema: a future scheduler/job/cache coordinate
        # cannot silently acquire this version's quiescence/frame proof.
        if set(self.__dict__) != self._root_fields:
            return result_type('UNRESOLVED', None, None, self._cursor, 'install has no transition proof for an unregistered Runtime state coordinate')
        if self._cursor % self._online.learner.update_unit:
            return result_type('UNRESOLVED', None, None, self._cursor, 'installation cannot discard a partial optimizer unit')
        # Unknown strings cannot become arbitrarily large owned diagnostics.
        # Historical/current authority checks still follow independently.
        if (candidate_id not in self._candidates or candidate_id == self._deployed_id
                or proposal_proof_id is not None and proposal_proof_id not in self._reference_proofs):
            return result_type('UNRESOLVED', None, None, self._cursor, 'no distinct owned target or invalid optional historical selection')
        if reference_identity not in self._persistence_identities or physical_identity not in self._persistence_identities:
            raise ContractError('unknown owned persistence identity')
        try:
            self._admit_control('install')
        except ResourceExceeded as exc:
            return result_type('UNRESOLVED', None, None, self._cursor, str(exc))
        attempt_id = f'{self._runtime_id}:install:{self._next_install}'
        self._next_install += 1
        revision_before = self._revision
        self._revision += 1
        attempt = attempt_type(attempt_id, self._cursor, self._deployed_id, candidate_id,
            proposal_proof_id, reference_identity, physical_identity, 'PREPARING')
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
            paired = (self.paired_cuda_persistence_result(reference_identity, physical_identity) if cuda else
                      self.paired_persistence_result(reference_identity, physical_identity))
            if paired.status != ('PAIRED_CUDA_CROSSED' if cuda else 'PAIRED_CPU_CROSSED'):
                raise ProfileUnresolved('both current same-path persistence crossings are required')
            persistence = self._persistence_identities[reference_identity]
            if (persistence.candidate_lineage_id != candidate_id
                    or persistence.base_lineage_id != self._deployed_id):
                raise ProfileUnresolved('fresh evidence belongs to a different target or deployed comparator')
            # Admission already owns the complete initialized/profiled starts;
            # paired_* verifies both paths share those same starts, and each
            # current crossing checks its continuous complete learners. A past
            # empirical maximum is an optional extra assertion, never a token
            # that substitutes for the current evidence or physical transition.
            if proposal_proof_id is not None:
                proof = self._reference_proofs[proposal_proof_id]
                proof.validate()
                search = self._searches.get(proof.search_id)
                if (search is None or search.status not in REFERENCE_SELECTION_COMPLETE or search.proof_id != proof.proof_id
                        or proof.winner_lineage_id != candidate_id or proof.base_lineage_id != self._deployed_id
                        or search.best_candidate_id != candidate_id):
                    raise ProfileUnresolved('installation target is not the asserted historical reference-class selection')
                row = next((r for r in search.rows if r.candidate_id == candidate_id), None)
                if (row is None or proof.ordinary_cursor != persistence.start_cursor
                        or row.learner != persistence.initial_candidate or search.base_state != persistence.initial_base):
                    raise ProfileUnresolved('fresh evidence did not start from the asserted historical selection and comparator')
            before = tuple(self._candidates.values())
            target, base = self._candidates[candidate_id], self._candidates[self._deployed_id]
            transport = prepare_transport(self._cuda, before) if cuda else None
            for state in (target, base):
                if state.learner.unit_count or state.float64 is not None and state.float64.unit_count:
                    raise ProfileUnresolved('installation requires both actual optimizer accumulators to be at a full boundary')
                self._ledger.charge_work(registration.work_role,
                    {'work': self._cuda.relation_work(self._programs[state.program_id], self._contract.semantics) if cuda
                     else relation_work(self._programs[state.program_id], self._contract.semantics)},
                    note=f'{attempt_id}:current-complete-state-bridge')
                if state.float64 is not None:
                    check_state(state.learner, state.float64, self._online.float64, bit_limit=self._contract.reference_integer_bits)
                if cuda:
                    raw = self._cuda_learner_record(state).raw_state
                    if self._cuda.state_unit(raw):
                        raise ProfileUnresolved('CUDA installation cannot erase an actual partial gradient unit')
                    self._ledger.charge_work(registration.work_role,
                        {'work': self._cuda.relation_work(self._programs[state.program_id], self._contract.semantics)},
                        note=f'{attempt_id}:current-CUDA-state-bridge')
                    self._cuda.check_state(state.learner, raw, bit_limit=self._contract.reference_integer_bits)
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
                if identity.status not in LIVE_STATUSES:
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
            completed = replace(attempt, status=installed, reason=('owned complete CPU/CUDA root and resident state published at the same cursor'
                if cuda else 'owned complete CPU root and buffer leases published at the same cursor'))
            receipt = receipt_type(completed, revision_before, self._revision, before, tuple(candidates.values()),
                tuple(moves), tuple(releases), close, tuple(invalidated), tuple(stopped), receipt_id,
                **({'cuda_transport': transport[-1]} if cuda else {}))
            policy_state = self._policy_state
            if self._policy_contract is not None:
                index = next((i for i, stage in enumerate(policy_state.stages) if stage.status not in TERMINAL_STAGES), None)
                stage = None if index is None else policy_state.stages[index]
                if (not self._policy_running or stage is None or stage.status != 'INSTALLING'
                        or (stage.candidate_id, stage.proof_id, stage.reference_identity, stage.physical_identity)
                        != (candidate_id, proposal_proof_id, reference_identity, physical_identity)):
                    raise ContractError('installation does not complete the owned current policy action')
                stages = policy_state.stages
                policy_state = self._next_policy_state(stages[:index]+(replace(stage, status=installed,
                    ended_cursor=self._cursor, install_attempt=attempt_id),)+stages[index+1:])
                self._allocate(stage_owner, (self._machine.realize(policy_state.object_id, 'owned_compiler_policy', policy_state, self._chi),))
                moves.append((stage_owner, self._data_owner, policy_state.object_id, 1))
                releases.append((self._data_owner, self._policy_state.object_id, 1))
                receipt = replace(receipt, ownership_moves=tuple(moves), releases=tuple(releases))
            self._allocate(stage_owner, (self._machine.realize(receipt_id,
                'prepared_cuda_install_receipt' if cuda else 'prepared_cpu_install_receipt', receipt, self._chi),))
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
            if cuda:
                verify_transport(transport, self._cuda, before)
            result = result_type(installed, attempt_id, candidate_id, self._cursor,
                'registered CUDA identity transaction completed; no current class optimum or full device release'
                if cuda else 'registered CPU transaction completed; fresh two-path evidence grants no class-optimality claim')
            next_root = dict(self.__dict__)
            next_root.update(_ledger=ledger, _router=CostRouter(ledger, self._contract.work_roles),
                _event_router=CostRouter(ledger, self._event_router.snapshot()), _buffers=buffers,
                _candidates=candidates, _deployed_id=candidate_id, _persistence_identities=persistent,
                _searches=searches, _install_attempts=self._install_attempts[:-1]+[completed],
                _install_receipts=self._install_receipts+[receipt], _event_phase='idle', _policy_state=policy_state)
        except HostExecutionUnresolved:
            raise
        except MemoryError:
            raise
        except Exception as exc:
            # All allocations happened against the live old root. Abort frees
            # only prepared objects; real work/peak/attempt history stay spent.
            cleanup_errors = []
            for owner in registered_owners:
                try:
                    self._release_owner(owner)
                except HostExecutionUnresolved:
                    raise
                except MemoryError:
                    raise
                except Exception as cleanup:
                    cleanup_errors.append(f'{type(cleanup).__name__}: {cleanup}')
            expected = isinstance(exc, (ResourceExceeded, ArithmeticUnresolved, ProfileUnresolved))
            failed = replace(attempt, status='UNRESOLVED' if expected else 'EXECUTION_FAILED',
                reason=f'{type(exc).__name__}: {exc}'+(' ; cleanup: '+'; '.join(cleanup_errors) if cleanup_errors else ''))
            self._install_attempts[-1] = failed
            self._event_phase = 'idle'
            if cuda and self._cuda.arena._failure is not None:
                self._halt('CUDA-install-state', exc)
            elif cleanup_errors:
                self._halt('install-cleanup', RuntimeError(failed.reason))
            if not expected:
                raise
            return result_type('UNRESOLVED', attempt_id, None, self._cursor, failed.reason)
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
                               None if self._host is None else self._host.observe(),
                               None if self._policy_contract is None else CompilerPolicySnapshot(
                                   self._policy_contract, self._policy_state, self._policy_running), self._run_snapshot(),
                               None if self._cuda is None else self._cuda.snapshot())
