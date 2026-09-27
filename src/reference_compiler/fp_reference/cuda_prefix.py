"""Private Runtime CUDA prefix mechanics and passive immutable records.

No object here signs a bridge or grants persistence/install authority. Runtime
prepays each phase, retains its record, and publishes all learners together.
Binary16/32 encodings widen exactly only for the existing rational comparison;
that comparison never supplies a device successor or CPU evidence wealth.
"""
from dataclasses import dataclass, field, replace
from fractions import Fraction as F

from .core import ContractError, natural
from .program import Product, Sum, rational
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved
from .cuda_range import FORWARD_ID, check_forward, widen
from .cuda_installation import CudaInstallContract
from .cuda_device import CudaDeviceContract, CudaDeviceSnapshot, _CudaDevice
from .float64_bridge import Float64Contract, check_state, check_prediction
from .float64_learner import Float64LearnerState, Float64Evaluation
from .cuda_storage import CudaArena, CudaStorageContract, CudaStorageUnresolved
from . import cuda_learner as gpu
from .likelihood_encoding import (LikelihoodEncodingContract, LikelihoodModel,
    BACKEND_ID as COUNT_BACKEND_ID, ENCODING_ID, prepare_model, preparation_work,
    power_schedule, RationalLikelihoodContract, RationalLikelihoodModel,
    RATIONAL_BACKEND_ID, RATIONAL_WORK_ID, RATIONAL_ENCODING_ID,
    CONTRACTS as LIKELIHOOD_CONTRACTS, MODELS as LIKELIHOOD_MODELS,
    preparation_workspace, require_workspace)
from .indexed_amp import FORWARD_ID as INDEXED_FORWARD_ID
from .projected_amp import FORWARD_ID as PROJECTED_FORWARD_ID
from .phase_encoding import ENCODING_ID as BINARY_PHASE_ENCODING_ID
from .phase_deflate import ENCODING_ID as DEFLATE_PHASE_ENCODING_ID
from .histogram_decoder import HistogramBudget
from .joint_relation import JointRelation
from .joint_partition_decoder import JointPartitionAllowance

LEGACY_PHASE_ENCODING_ID = 'typed-reference-json-v4'


@dataclass(frozen=True)
class CudaPrefixContract:
    storage: CudaStorageContract
    state_atol: F
    probability_atol: F
    phase_output_cells: int = 4096
    phase_evidence_bytes: int = 131072
    evidence_encoding: str = field(default=LEGACY_PHASE_ENCODING_ID, kw_only=True)
    execution_identity: tuple = ('2.12.0+cu132', '7661cd9c6b841b62b7f411aa52ec51f05457263b',
                                 '13.2', 'NVIDIA GeForce RTX 3090', (8, 6))
    install: CudaInstallContract | None = None
    device: CudaDeviceContract = field(default_factory=lambda: CudaDeviceContract(24 << 30,
        {role: 24 << 30 for role in ('deployment', 'compiler')}))
    likelihood_encoding: LikelihoodEncodingContract | RationalLikelihoodContract | None = None
    backend_id: str = field(default='', init=False)
    work_model: str = field(default='', init=False)
    forward_id: str = field(default=FORWARD_ID, init=False)

    def _arithmetic_ids(self):
        if type(self.likelihood_encoding) is RationalLikelihoodContract:
            return RATIONAL_BACKEND_ID, RATIONAL_WORK_ID, FORWARD_ID
        return (gpu.BACKEND_ID if self.likelihood_encoding is None else COUNT_BACKEND_ID,
            'prepaid-output-cells-packed-evidence-and-exact-forward-v2' if self.likelihood_encoding is None
            else 'prepaid-likelihood-factorization-coordinates-and-CUDA-output-v1', FORWARD_ID)

    def __post_init__(self):
        if (type(self.evidence_encoding) is not str or self.evidence_encoding not in
                (LEGACY_PHASE_ENCODING_ID,DEFLATE_PHASE_ENCODING_ID)):
            raise ContractError('fixed registered CUDA evidence encoding required')
        if self.likelihood_encoding is not None:
            if type(self.likelihood_encoding) not in LIKELIHOOD_CONTRACTS:
                raise ContractError('registered immutable likelihood encoding contract required')
            self.likelihood_encoding.__post_init__()
        backend, work_model, forward = self._arithmetic_ids()
        if self.evidence_encoding == DEFLATE_PHASE_ENCODING_ID:
            work_model += '+prepaid-byte-only-phase-compression-v1'
        if (self.backend_id not in ('', backend) or self.forward_id not in ('', forward)
                or self.work_model not in ('', work_model)):
            raise ContractError('CUDA prefix cannot replace the registered executor or work model')
        object.__setattr__(self, 'backend_id', backend)
        object.__setattr__(self, 'work_model', work_model)
        object.__setattr__(self, 'forward_id', forward)
        if type(self.storage) is not CudaStorageContract:
            raise ContractError('immutable physical CUDA storage contract required')
        self.storage.__post_init__()
        if type(self.device) is not CudaDeviceContract:
            raise ContractError('immutable actual CUDA device/resource binding required')
        self.device.__post_init__()
        if self.install is not None:
            if type(self.install) is not CudaInstallContract:
                raise ContractError('immutable registered CUDA installation required')
            self.install.__post_init__()
        for key in ('state_atol', 'probability_atol'):
            object.__setattr__(self, key, rational(getattr(self, key), 'registered CUDA '+key))
        for key in ('phase_output_cells', 'phase_evidence_bytes'):
            natural(getattr(self, key), 'CUDA '+key, positive=True)
        if (type(self.execution_identity) is not tuple or len(self.execution_identity) != 5
                or any(type(v) is not str for v in self.execution_identity[:4])
                or type(self.execution_identity[4]) is not tuple
                or len(self.execution_identity[4]) != 2
                or any(type(v) is not int or v < 0 for v in self.execution_identity[4])):
            raise ContractError('immutable actual Torch/build/device/SM identity required')


@dataclass(frozen=True, kw_only=True)
class IndexedCudaPrefixContract(CudaPrefixContract):
    n: int
    order_search: bool = False
    histogram: HistogramBudget | None = None
    forward_id: str = field(default='', init=False)

    def _arithmetic_ids(self):
        from . import indexed_amp as indexed
        from .query_order import WORK_MODEL
        indexed.IndexedRelation(self.n)
        if self.likelihood_encoding is not None:
            raise ContractError('indexed native lowering cannot borrow a dense likelihood encoding')
        if type(self.order_search) is not bool:
            raise ContractError('immutable indexed order-search registration required')
        if self.histogram is not None:
            from . import histogram_amp, histogram_decoder
            if (type(self.histogram) not in histogram_decoder.ALLOWANCES or self.order_search
                    or type(self) is not IndexedCudaPrefixContract):
                raise ContractError('histogram schedule has one fixed complete traversal class')
            self.histogram.__post_init__()
            engine = histogram_decoder.implementation(self.histogram)
            physical = histogram_amp.implementation(self.histogram)
            engine.construction_work(self.n, self.histogram)
            return physical.BACKEND_ID, engine.WORK_MODEL, physical.FORWARD_ID
        work = 'prepaid-indexed-owned-plan-and-scalar-arena-v2'
        return (indexed.BACKEND_ID, work+('+'+WORK_MODEL if self.order_search else ''),
                indexed.ORDERED_FORWARD_ID if self.order_search else indexed.FORWARD_ID)


@dataclass(frozen=True, kw_only=True)
class ProjectedIndexedCudaPrefixContract(IndexedCudaPrefixContract):
    """Distinct fixed physical schedule for the same complete native learner."""
    forward_id: str = field(default='', init=False)

    def _arithmetic_ids(self):
        from . import projected_amp
        _,work,_ = super()._arithmetic_ids()
        return (projected_amp.BACKEND_ID,work,
                projected_amp.ORDERED_FORWARD_ID if self.order_search else projected_amp.FORWARD_ID)


@dataclass(frozen=True, kw_only=True)
class JointCudaPrefixContract(CudaPrefixContract):
    schema: JointRelation
    partitions: JointPartitionAllowance
    forward_id: str = field(default='', init=False)

    def _arithmetic_ids(self):
        from .joint_execution import closed
        from . import joint_amp
        closed(self.schema, JointRelation)
        closed(self.partitions, JointPartitionAllowance)
        self.schema.__post_init__()
        self.partitions.__post_init__()
        physical = joint_amp.implementation(self.schema)
        if self.likelihood_encoding is not None:
            raise ContractError('joint indexed lowering cannot substitute a dense likelihood representation')
        return physical.BACKEND_ID, physical.WORK_MODEL, physical.FORWARD_ID

    def __post_init__(self):
        super().__post_init__()
        from .joint_execution import closed
        closed(self, JointCudaPrefixContract)


@dataclass(frozen=True, kw_only=True)
class TokenCudaPrefixContract(CudaPrefixContract):
    initializer: object
    exact_cell_cap: int = 4096
    reuse_regions: bool = False
    forward_id: str = field(default='', init=False)

    def _arithmetic_ids(self):
        from .token_execution import TokenInitializer, closed
        closed(self.initializer, TokenInitializer)
        self.initializer.__post_init__()
        natural(self.exact_cell_cap, 'token exact rounding-cell allowance')
        if type(self.reuse_regions) is not bool:
            raise ContractError('exact token storage reuse registration required')
        if self.reuse_regions and (type(self.storage) is not CudaStorageContract
                or self.storage.arena_bytes & (self.storage.arena_bytes-1)):
            raise ContractError('token reuse requires a power-of-two backing extent')
        if self.likelihood_encoding is not None or self.install is not None:
            raise ContractError('token events cannot borrow a likelihood encoding or an installation release')
        return ('token-half-core-event-gradient-sparse-balanced-carry-integer-grid-v2',
                'prepaid-complete-token-array-graph-and-cache-relation-v1'+
                    ('+sealed-token-generation-reuse-v1' if self.reuse_regions else ''),
                'token-half-single-one-event-explicit-arena-arrays-v1')

    def __post_init__(self):
        super().__post_init__()
        from .token_execution import closed
        closed(self, TokenCudaPrefixContract)


@dataclass(frozen=True)
class CudaRunManifest:
    reference: object
    cuda: CudaPrefixContract
    target_amp: str = field(default='owned CUDA prefix/range/evidence, resident installation and finite policy/run; complete target release UNRESOLVED', init=False)


@dataclass(frozen=True)
class CudaPhase:
    object_id: str
    candidate_id: str
    program_id: str
    phase: str
    ordinary_cursor: int
    observation_id: str | None
    input_phase: str | None
    prediction_phase: str | None
    reference: object
    reference_prediction: object
    raw_state: tuple | None
    raw_prediction: tuple | None
    raw_operations: tuple
    relation: object
    output_cells: int
    arena_phase: int | None
    status: str
    reason: str
    forward_operations: int = 0
    encoding_model: LikelihoodModel | None = None


@dataclass(frozen=True, kw_only=True)
class IndexedCudaPhase(CudaPhase):
    execution_plan: object = None


@dataclass(frozen=True)
class CudaPrefixSnapshot:
    contract: CudaPrefixContract
    current: tuple
    staged: tuple
    predicted: tuple
    phases: tuple[CudaPhase, ...]
    storage: object
    device: CudaDeviceSnapshot
    scope: str = field(default='owned executed CUDA prefix and exact forecasts; range/persistence authority belongs to Runtime identities; no installation or total-device authority', init=False)


def widened_state(raw):
    """Numeric component only; Runtime separately proves encoded transitions."""
    if type(raw) is not tuple or len(raw) not in (6, 7):
        raise ContractError('registered complete CUDA state encoding required')
    if len(raw) == 7:
        _encoded_raw(raw[6])
    theta, delayed, gradient, count, cursor, steps = raw[:6]
    return Float64LearnerState(tuple(widen(v, 32) for v in theta),
        tuple((key, tuple(widen(v, 16) for v in values)) for key, values in delayed),
        tuple(widen(v, 32) for v in gradient), count, cursor, steps)


def raw_prediction(value):
    numeric = (gpu.raw_tensor(value.values), gpu.raw_tensor(value.theta_half), gpu.raw_tensor(value.excesses),
            gpu.raw_tensor(value.masses), gpu.raw_tensor(value.normalizer), gpu.raw_tensor(value.probabilities),
            tuple((key, gpu.raw_tensor(values)) for key, values in value.delayed))
    return numeric if value.encoding_query is None else numeric+(value.encoding_query,)


def widened_prediction(raw):
    if type(raw) is not tuple or len(raw) not in (7, 8):
        raise ContractError('registered complete CUDA prediction encoding required')
    if len(raw) == 8:
        natural(raw[7], 'retained likelihood prediction source row')
    values, theta, excesses, masses, normalizer, probabilities, delayed = raw[:7]
    return Float64Evaluation(tuple(widen(v, 16) for v in values), tuple(widen(v, 16) for v in excesses),
        tuple(widen(v, 32) for v in masses), widen(normalizer[0], 32),
        tuple(widen(v, 32) for v in probabilities),
        tuple((key, tuple(widen(v, 16) for v in row)) for key, row in delayed))


def _encoded_raw(raw):
    if (type(raw) is not tuple or len(raw) != 4 or raw[0] not in (ENCODING_ID, RATIONAL_ENCODING_ID)
            or type(raw[1]) is not str or len(raw[1]) != 64
            or type(raw[2]) is not tuple or any(type(v) is not int for v in raw[2])):
        raise ContractError('complete raw likelihood coordinate encoding required')
    if raw[3] is not None:
        natural(raw[3], 'retained uncommitted likelihood event')


def output_cells(kind, program, rules, spec, *, encoded_state=None, steps=None, bit_limit=None):
    """Exact output-extent count of this fixed lowering, including empty views.

    Derived by summing its explicit output/cast/copy/mask allocations. This
    is not a lower bound over alternative legal physical implementations.
    """
    slots = max(1, program.slot_count)
    delays = sum(s.delay for s in rules.states)
    if kind == 'initialize':
        return 2*slots+2+delays
    if kind == 'attach':
        return 0
    if kind == 'commit':
        if encoded_state is not None:
            successor = encoded_state.commit()
            if type(successor.model) is RationalLikelihoodModel:
                return 1+3*len(spec.simplex_slots)+2*slots
            differences, bits = power_schedule(successor, steps+1, bit_limit=bit_limit)
            return 3+max(bits-1, 0)+sum(v.bit_count() for v in differences)+3*len(spec.simplex_slots)+2*slots
        from .learner import SIMPLEX_GRADIENT
        if spec.optimizer_id == SIMPLEX_GRADIENT:
            return 7+15*len(spec.simplex_slots)+2*slots
        return 4+(14 if spec.commit_grid_bits is not None else 7)*slots
    sums = tuple(node for node in program.nodes if type(node) is Sum)
    edges = sum(len(node.terms) for node in sums)
    products = sum(type(node) is Product for node in program.nodes)
    if kind == 'predict':
        return slots+2*max(1, len(rules.sources))+1+products+3*edges+len(sums)+len(program.nodes)+6*len(program.heads)+delays
    if kind == 'observe':
        return 6+len(program.heads)+len(program.nodes)+3*slots+4*(edges+products)
    raise ContractError('unregistered CUDA output schedule')


class _CudaPrefix:
    def __init__(self, contract):
        if type(contract) not in (CudaPrefixContract, IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract, JointCudaPrefixContract, TokenCudaPrefixContract):
            raise ContractError('registered private CUDA prefix contract required')
        contract.__post_init__()
        import torch
        device = contract.storage.device
        if not torch.cuda.is_available() or device >= torch.cuda.device_count():
            raise CudaStorageUnresolved('registered CUDA device unavailable')
        actual = (str(torch.__version__), torch.version.git_version, torch.version.cuda,
                  torch.cuda.get_device_name(device), tuple(torch.cuda.get_device_capability(device)))
        if actual != contract.execution_identity:
            raise CudaStorageUnresolved('actual CUDA execution identity differs from registration')
        self.contract = contract
        self._device = _CudaDevice(contract.device, device)
        if type(contract) is TokenCudaPrefixContract and contract.reuse_regions:
            from .token_reuse import TokenReuseArena
            self.arena = TokenReuseArena(contract.storage)
        else:
            self.arena = CudaArena(contract.storage)
        self.current, self.staged, self.predicted = {}, {}, {}
        self.phases, self._values = {}, {}

    @property
    def indexed(self):
        return type(self.contract) in (IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract, JointCudaPrefixContract)

    @property
    def joint(self):
        return type(self.contract) is JointCudaPrefixContract

    @property
    def token(self):
        return type(self.contract) is TokenCudaPrefixContract

    @property
    def reuses_token_storage(self):
        return self.token and self.contract.reuse_regions

    @property
    def joint_implementation(self):
        from .joint_amp import implementation
        return implementation(self.contract.schema)

    def relation_work(self, program, rules):
        if self.token:
            from .token_cuda_prefix import relation_work
            return relation_work(program, self.contract)
        if self.joint:
            return self.joint_implementation.relation_work(program)
        if self.indexed:
            return 512*(program.n*(program.n-1)//2+2*program.n+16)
        from .float64_bridge import relation_work
        return relation_work(program, rules)

    def forward_work(self, program, rules):
        if self.token:
            return self.relation_work(program, rules)
        if self.joint:
            return self.joint_implementation.forward_work(program, self.contract.partitions, self.contract.phase_output_cells)
        if self.indexed:
            if self.contract.histogram is not None:
                from .histogram_amp import implementation
                return implementation(self.contract.histogram).forward_work(
                    program.n, self.contract.histogram, self.contract.phase_output_cells)
            n, d = program.n, program.n*(program.n-1)//2
            return 256*(n+1)**2*(d+n+1)+128*(n+1)*self.contract.phase_output_cells
        from .cuda_range import forward_work
        return forward_work(program, rules)

    def state_cursor(self, raw):
        return raw.cursor if self.indexed or self.token else raw[4]

    def state_unit(self, raw):
        return raw.unit_count if self.indexed or self.token else raw[3]

    def theta_binding(self, raw):
        if self.token:
            return raw.origin.embedding, raw.origin.core, raw.origin.output
        return raw.theta if self.indexed else raw[0]

    def queue_work(self, program, rules):
        return self.relation_work(program, rules) if self.indexed or self.token else 128*(1+sum(s.delay for s in rules.states))

    def check_queue(self, rules, raw, *, bit_limit):
        if self.token:
            from .token_cuda_state import StateWords
            from .token_execution import closed
            closed(raw, StateWords)
            if rules.states or raw.origin.definition.sources.vocabulary != rules.sources.vocabulary:
                raise ContractError('token CUDA lost its complete indexed source and empty recurrent interface')
            return
        if self.indexed:
            from .indexed_amp import IndexedAmpState
            if type(raw) is not (self.joint_implementation.JointAmpState if self.joint else IndexedAmpState) or rules.states:
                raise ContractError('indexed CUDA lost its declared empty delayed interface')
            raw.__post_init__()
            return
        from .cuda_range import check_queue
        return check_queue(rules, raw[1], bit_limit=bit_limit)

    def stored_probability(self, raw, target, *, bit_limit):
        if self.token:
            raise ContractError('token CUDA persistence probability decoding is not registered')
        if self.joint:
            stored_probability = self.joint_implementation.stored_probability
        elif self.indexed:
            from .indexed_amp import stored_probability
        else:
            from .cuda_range import stored_probability
        return stored_probability(raw, target, bit_limit=bit_limit)

    def raw_state(self, value):
        return value.raw() if self.indexed or self.token else gpu.raw_state(value)

    def state_tensors(self, value):
        return value.tensors() if self.indexed or self.token else (('theta', value.theta), ('gradient', value.gradient_sum), *value.delayed)

    def check_state(self, reference, raw, *, bit_limit):
        if self.token:
            from .token_cuda_prefix import check_state
            return check_state(reference, raw, self.contract)
        tolerance = Float64Contract(self.contract.state_atol, self.contract.probability_atol)
        if self.joint:
            return self.joint_implementation.check_state(reference, raw, tolerance, bit_limit=bit_limit)
        if self.indexed:
            from .indexed_amp import check_state as indexed_check
            return indexed_check(reference, raw, tolerance, bit_limit=bit_limit)
        return check_state(reference, widened_state(raw), tolerance, bit_limit=bit_limit)

    def snapshot(self):
        try:
            return CudaPrefixSnapshot(self.contract, tuple(self.current.items()), tuple(self.staged.items()),
                                      tuple(self.predicted.items()), tuple(self.phases.values()), self.arena.snapshot(),
                                      self._device.snapshot())
        except MemoryError:
            raise
        except Exception:
            # Diagnostics have no continuation authority, but observing a
            # failed native premise must still close every live authority.
            if self.arena._failure is None:
                self.arena._failure = 'CUDA device/storage binding could not be established'
            raise

    def check(self):
        try:
            self._device.check()
            self.arena.check()
        except MemoryError:
            raise
        except Exception:
            if self.arena._failure is None:
                self.arena._failure = 'CUDA device/storage binding could not be established'
            raise

    def execute(self, object_id, kind, program, candidate, reference, *, rules, spec, bit_limit,
                ordinary_cursor, origin, observation_id, sources, reference_prediction, target,
                normalizer_cap, activation_cap, source_domain=None, readout_buffer=None, order_search=None,
                histogram_workspace=None, likelihood_workspace=None, joint_workspace=None):
        if self.token:
            if any(x is not None for x in (order_search, histogram_workspace, likelihood_workspace, joint_workspace)):
                raise ContractError('token CUDA cannot borrow a foreign constructor workspace')
            from .token_cuda_prefix import execute
            return execute(self, object_id, kind, program, candidate, reference, rules=rules, spec=spec,
                bit_limit=bit_limit, ordinary_cursor=ordinary_cursor, origin=origin,
                observation_id=observation_id, sources=sources, reference_prediction=reference_prediction,
                target=target, normalizer_cap=normalizer_cap, activation_cap=activation_cap,
                source_domain=source_domain, readout_buffer=readout_buffer)
        if self.joint:
            if order_search is not None or histogram_workspace is not None or likelihood_workspace is not None:
                raise ContractError('joint CUDA requires only its registered fixed integer workspace')
            from .joint_cuda_prefix import execute
            return execute(self, object_id, kind, program, candidate, reference, rules=rules, spec=spec,
                bit_limit=bit_limit, ordinary_cursor=ordinary_cursor, origin=origin,
                observation_id=observation_id, sources=sources, reference_prediction=reference_prediction,
                target=target, normalizer_cap=normalizer_cap, activation_cap=activation_cap,
                source_domain=source_domain, readout_buffer=readout_buffer, workspace=joint_workspace)
        if self.indexed:
            from .indexed_cuda_prefix import execute
            return execute(self, object_id, kind, program, candidate, reference, rules=rules, spec=spec,
                bit_limit=bit_limit, ordinary_cursor=ordinary_cursor, origin=origin,
                observation_id=observation_id, sources=sources, reference_prediction=reference_prediction,
                target=target, normalizer_cap=normalizer_cap, activation_cap=activation_cap,
                source_domain=source_domain, readout_buffer=readout_buffer, order_search=order_search,
                histogram_workspace=histogram_workspace)
        if bit_limit < 1075:
            raise ArithmeticUnresolved('exact raw-value relation decoder exceeds its reference integer allowance')
        use_staged = origin == 'profile' or kind == 'commit'
        source = self.staged if use_staged else self.current
        input_id = None if kind == 'initialize' else source[candidate]
        prediction_id = self.predicted.get(candidate) if kind == 'observe' else None
        state = None if input_id is None else self._values[input_id]
        prediction = None if prediction_id is None else self._values[prediction_id]
        result, actual_prediction, relation, error, arithmetic, workspace = state, None, None, None, None, None
        forward_operations = 0
        encoding_model = None
        before_raw = None
        try:
            if state is not None:
                before_raw = gpu.raw_state(state)
                if before_raw != self.phases[input_id].raw_state:
                    raise ContractError('private CUDA predecessor changed after its owned phase')
                if (state.encoding is None) != (self.contract.likelihood_encoding is None):
                    raise ContractError('CUDA predecessor lost or changed its registered physical representation')
                if state.encoding is not None:
                    model = state.encoding.model
                    if (model.contract != self.contract.likelihood_encoding or model.learner != spec
                            or model.program_id != program.program_id or model.semantics != rules):
                        raise ContractError('CUDA likelihood predecessor changed its complete encoding binding')
            if prediction is not None and raw_prediction(prediction) != self.phases[prediction_id].raw_prediction:
                raise ContractError('private sealed CUDA prediction changed before observation')
            if state is not None and state.encoding is not None and kind == 'observe':
                if (prediction is None or self.phases[prediction_id].input_phase != input_id
                        or self.phases[prediction_id].observation_id != observation_id):
                    raise ContractError('likelihood observation lost its actual predecessor prediction or event identity')
            if kind == 'initialize' and self.contract.likelihood_encoding is not None:
                if type(self.contract.likelihood_encoding) is RationalLikelihoodContract:
                    require_workspace(likelihood_workspace, preparation_workspace(program, rules, spec,
                        source_domain, bit_limit, self.contract.likelihood_encoding))
                encoding_model = prepare_model(program, rules, reference.theta, spec, source_domain,
                    self.contract.likelihood_encoding, bit_limit=bit_limit,
                    work_limit=preparation_work(program, rules, spec, source_domain, bit_limit,
                                                self.contract.likelihood_encoding))
                actual_domain = ((),) if source_domain is None and not rules.sources else tuple(dict.fromkeys(source_domain))
                if (type(encoding_model) not in LIKELIHOOD_MODELS or encoding_model.program_id != program.program_id
                        or encoding_model.semantics != rules or encoding_model.initial_theta != reference.theta
                        or encoding_model.learner != spec or encoding_model.contract != self.contract.likelihood_encoding
                        or encoding_model.source_domain != actual_domain):
                    raise ContractError('derived likelihood model changed the actual program, Gamma, U or complete source domain')
            with self.arena.phase(object_id) as workspace:
                arithmetic = gpu.CudaArithmetic(bit_limit, self.contract.storage.device,
                    workspace=workspace, output_cell_limit=self.contract.phase_output_cells,
                    readout_buffer=readout_buffer, likelihood_workspace=likelihood_workspace)
                tolerance = Float64Contract(self.contract.state_atol, self.contract.probability_atol)
                if kind == 'initialize':
                    result = gpu.initialize(program, rules, reference.theta, reference.cursor, arithmetic,
                                            encoding_model=encoding_model)
                elif kind == 'predict':
                    state_relation = check_state(reference, widened_state(gpu.raw_state(state)), tolerance, bit_limit=bit_limit)
                    actual_prediction = gpu.evaluate(program, rules, state, sources, arithmetic)
                    forward_operations = check_forward(program, rules, gpu.raw_state(state), sources,
                        raw_prediction(actual_prediction)[:7], bit_limit=bit_limit)
                    relation = check_prediction(reference_prediction, widened_prediction(raw_prediction(actual_prediction)),
                        tolerance, rules, normalizer_cap=normalizer_cap, activation_cap=activation_cap, bit_limit=bit_limit)
                    relation = replace(relation, state_error=state_relation.state_error)
                elif kind == 'observe':
                    result = gpu.observe_event(program, rules, state, spec, prediction, target, arithmetic)
                elif kind == 'commit':
                    result = gpu.commit_event(state, spec, arithmetic)
                elif kind == 'attach':
                    result = gpu.attach_clock(state, reference.cursor, spec)
                else:
                    raise ContractError('unregistered owned CUDA phase')
                arithmetic.check()
                if arithmetic.output_cells != output_cells(kind, program, rules, spec,
                        encoded_state=None if state is None else state.encoding,
                        steps=None if state is None else state.optimizer_steps, bit_limit=bit_limit):
                    raise ContractError('CUDA endpoint did not execute its registered output schedule')
                if self.contract.likelihood_encoding is not None:
                    self._check_encoding_transition(kind, before_raw, state, result, actual_prediction,
                        prediction, encoding_model, sources, target)
                if kind != 'predict':
                    relation = check_state(reference, widened_state(gpu.raw_state(result)), tolerance, bit_limit=bit_limit)
                if state is not None and gpu.raw_state(state) != self.phases[input_id].raw_state:
                    raise ContractError('CUDA execution mutated its owned predecessor')
        except MemoryError:
            raise
        except Exception as exc:
            error = exc
        record = CudaPhase(object_id, candidate, program.program_id, origin+':'+kind, ordinary_cursor,
            observation_id, input_id, prediction_id, reference, reference_prediction,
            None if result is None else gpu.raw_state(result),
            None if actual_prediction is None else raw_prediction(actual_prediction),
            () if arithmetic is None else arithmetic.raw_trace(), relation,
            0 if arithmetic is None else arithmetic.output_cells,
            None if workspace is None else workspace.index,
            'CHECKED_CUDA_PREFIX_PHASE' if error is None else
                'UNRESOLVED' if isinstance(error, (ResourceExceeded, ArithmeticUnresolved)) else 'EXECUTION_FAILED',
            '' if error is None else f'{type(error).__name__}: {error}', forward_operations, encoding_model)
        # Even failed completed outputs retain their physical handle. Only
        # Runtime may retain/check this record and advance staged/current IDs.
        self._values[object_id] = actual_prediction if kind == 'predict' else result
        self.phases[object_id] = record
        return record, error

    def _check_encoding_transition(self, kind, before_raw, state, result, actual_prediction,
                                   prediction, encoding_model, sources, target):
        """Exact coordinate/event relation, separate from numerical closeness."""
        from .core import stable_hash
        if kind == 'initialize':
            expected = (encoding_model.encoding_id, stable_hash(encoding_model), (0,)*encoding_model.rank, None)
        else:
            before = before_raw[6]
            _encoded_raw(before)
            if kind == 'observe':
                query = prediction.encoding_query
                natural(query, 'actual owned pre-target likelihood query')
                if query >= len(state.encoding.model.source_domain):
                    raise ContractError('owned likelihood prediction has an invalid source row')
                expected = before[:3]+(query*state.encoding.model.labels+target,)
            elif kind == 'commit':
                pending = before[3]
                if pending is None:
                    raise ContractError('owned likelihood commit lost its uncommitted event')
                increment = state.encoding.model.event_increments[pending]
                expected = before[:2]+(tuple(a+b for a, b in zip(before[2], increment)), None)
            else:
                expected = before
        if kind == 'predict':
            if actual_prediction.encoding_query != state.encoding.model.query_index(sources):
                raise ContractError('CUDA likelihood prediction mislabeled its actual complete source input')
        if result is None or result.encoding is None or result.encoding.raw() != expected:
            raise ContractError('CUDA likelihood coordinates did not follow the registered complete event transition')

    def accept(self, record):
        if record.status != 'CHECKED_CUDA_PREFIX_PHASE' or self.phases.get(record.object_id) != record:
            raise ContractError('only the actual retained phase can advance a CUDA prefix')
        if type(self.contract) is TokenCudaPrefixContract and self.contract.reuse_regions:
            self.arena.accept(record)
        if record.phase.endswith(':predict'):
            self.predicted[record.candidate_id] = record.object_id
        elif record.phase != 'report:readout':
            self.staged[record.candidate_id] = record.object_id
