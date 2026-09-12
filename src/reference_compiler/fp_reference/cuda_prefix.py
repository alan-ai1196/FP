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


@dataclass(frozen=True)
class CudaPrefixContract:
    storage: CudaStorageContract
    state_atol: F
    probability_atol: F
    phase_output_cells: int = 4096
    phase_evidence_bytes: int = 131072
    execution_identity: tuple = ('2.12.0+cu132', '7661cd9c6b841b62b7f411aa52ec51f05457263b',
                                 '13.2', 'NVIDIA GeForce RTX 3090', (8, 6))
    install: CudaInstallContract | None = None
    device: CudaDeviceContract = field(default_factory=lambda: CudaDeviceContract(24 << 30,
        {role: 24 << 30 for role in ('deployment', 'compiler')}))
    backend_id: str = field(default=gpu.BACKEND_ID, init=False)
    work_model: str = field(default='prepaid-output-cells-packed-evidence-and-exact-forward-v2', init=False)
    forward_id: str = field(default=FORWARD_ID, init=False)

    def __post_init__(self):
        if (self.backend_id != gpu.BACKEND_ID or self.forward_id != FORWARD_ID
                or self.work_model != 'prepaid-output-cells-packed-evidence-and-exact-forward-v2'):
            raise ContractError('CUDA prefix cannot replace the registered executor or work model')
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
    theta, delayed, gradient, count, cursor, steps = raw
    return Float64LearnerState(tuple(widen(v, 32) for v in theta),
        tuple((key, tuple(widen(v, 16) for v in values)) for key, values in delayed),
        tuple(widen(v, 32) for v in gradient), count, cursor, steps)


def raw_prediction(value):
    return (gpu.raw_tensor(value.values), gpu.raw_tensor(value.theta_half), gpu.raw_tensor(value.excesses),
            gpu.raw_tensor(value.masses), gpu.raw_tensor(value.normalizer), gpu.raw_tensor(value.probabilities),
            tuple((key, gpu.raw_tensor(values)) for key, values in value.delayed))


def widened_prediction(raw):
    values, theta, excesses, masses, normalizer, probabilities, delayed = raw
    return Float64Evaluation(tuple(widen(v, 16) for v in values), tuple(widen(v, 16) for v in excesses),
        tuple(widen(v, 32) for v in masses), widen(normalizer[0], 32),
        tuple(widen(v, 32) for v in probabilities),
        tuple((key, tuple(widen(v, 16) for v in row)) for key, row in delayed))


def output_cells(kind, program, rules, spec):
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
        if type(contract) is not CudaPrefixContract:
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
        self.arena = CudaArena(contract.storage)
        self.current, self.staged, self.predicted = {}, {}, {}
        self.phases, self._values = {}, {}

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
                normalizer_cap, activation_cap):
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
        try:
            if state is not None and gpu.raw_state(state) != self.phases[input_id].raw_state:
                raise ContractError('private CUDA predecessor changed after its owned phase')
            if prediction is not None and raw_prediction(prediction) != self.phases[prediction_id].raw_prediction:
                raise ContractError('private sealed CUDA prediction changed before observation')
            with self.arena.phase(object_id) as workspace:
                arithmetic = gpu.CudaArithmetic(bit_limit, self.contract.storage.device,
                    workspace=workspace, output_cell_limit=self.contract.phase_output_cells)
                tolerance = Float64Contract(self.contract.state_atol, self.contract.probability_atol)
                if kind == 'initialize':
                    result = gpu.initialize(program, rules, reference.theta, reference.cursor, arithmetic)
                elif kind == 'predict':
                    state_relation = check_state(reference, widened_state(gpu.raw_state(state)), tolerance, bit_limit=bit_limit)
                    actual_prediction = gpu.evaluate(program, rules, state, sources, arithmetic)
                    forward_operations = check_forward(program, rules, gpu.raw_state(state), sources,
                        raw_prediction(actual_prediction), bit_limit=bit_limit)
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
                if arithmetic.output_cells != output_cells(kind, program, rules, spec):
                    raise ContractError('CUDA endpoint did not execute its registered output schedule')
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
            '' if error is None else f'{type(error).__name__}: {error}', forward_operations)
        # Even failed completed outputs retain their physical handle. Only
        # Runtime may retain/check this record and advance staged/current IDs.
        self._values[object_id] = actual_prediction if kind == 'predict' else result
        self.phases[object_id] = record
        return record, error

    def accept(self, record):
        if record.status != 'CHECKED_CUDA_PREFIX_PHASE' or self.phases.get(record.object_id) != record:
            raise ContractError('only the actual retained phase can advance a CUDA prefix')
        if record.phase.endswith(':predict'):
            self.predicted[record.candidate_id] = record.object_id
        else:
            self.staged[record.candidate_id] = record.object_id
