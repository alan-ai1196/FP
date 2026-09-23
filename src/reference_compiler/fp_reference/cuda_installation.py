"""Registered same-device installation and private identity-transport checks.

No public certificate or endpoint is accepted here. Runtime pays preparation,
binds the owned proposal/evidence and publishes the complete next root. The
device arena is already shared in full by both roles. Paid readback checks
precede identity transport; no CUDA state is written, relocated or released.
"""
from dataclasses import dataclass, field

from .core import ContractError
from .installation import CpuInstallReceipt, CpuInstallResult
from .profile import ProfileUnresolved
from . import cuda_learner as gpu
from .cuda_device import DEVICE_FIELDS, _CudaDevice


@dataclass(frozen=True)
class CudaInstallContract:
    work_role: str = 'deployment'
    workspace_role: str = 'deployment'
    machine_transition: str = field(default='serialized-cpython-root-and-quiescent-CUDA-arena-v1', init=False)
    proposal: str = field(default='owned-paired-persistence-start-with-optional-historical-selection-v2', init=False)
    transport: str = field(default='preserve-complete-learners-and-resident-CUDA-views-v1', init=False)
    shadow_policy: str = field(default='retain-all-demote-old-base-v1', init=False)
    search_policy: str = field(default='stop-all-retain-frontier-and-evidence-v1', init=False)
    persistence_policy: str = field(default='invalidate-all-no-rebase-no-refund-v1', init=False)

    def __post_init__(self):
        if (type(self.work_role) is not str or type(self.workspace_role) is not str
                or self.work_role not in ('deployment', 'compiler')
                or self.workspace_role not in ('deployment', 'compiler')):
            raise ContractError('CUDA installation requires registered physical/work roles')
        policies = {
            'machine_transition': 'serialized-cpython-root-and-quiescent-CUDA-arena-v1',
            'proposal': 'owned-paired-persistence-start-with-optional-historical-selection-v2',
            'transport': 'preserve-complete-learners-and-resident-CUDA-views-v1',
            'shadow_policy': 'retain-all-demote-old-base-v1',
            'search_policy': 'stop-all-retain-frontier-and-evidence-v1',
            'persistence_policy': 'invalidate-all-no-rebase-no-refund-v1',
        }
        if any(type(getattr(self, key)) is not str or getattr(self, key) != value for key, value in policies.items()):
            raise ContractError('unimplemented CUDA installation policy or machine transition')


@dataclass(frozen=True)
class CudaInstallAttempt:
    attempt_id: str
    cursor: int
    old_deployed_id: str
    target_id: str
    proposal_proof_id: str | None
    reference_identity: str
    cuda_identity: str
    status: str
    reason: str = ''


@dataclass(frozen=True)
class CudaTransport:
    current: tuple
    storage_pointer: int
    default_stream: int
    allocation_counter: tuple
    tensor_arena_bytes: int
    allocator_reserved_bytes: int
    consumed_arena_bytes: int
    retained_phases: int
    retained_values: int
    ownership: str = field(default='unchanged whole tensor arena shared by both registered roles', init=False)


@dataclass(frozen=True, kw_only=True)
class CudaInstallReceipt(CpuInstallReceipt):
    attempt: CudaInstallAttempt = field(kw_only=False)
    cuda_transport: CudaTransport


@dataclass(frozen=True)
class CudaInstallResult(CpuInstallResult):
    authority_scope: str = field(default='executed serialized reference/CUDA identity installation under the declared tensor and host-payload model; no current global optimum, total-device or complete release authority', init=False)


PREFIX_FIELDS = frozenset(('contract', 'arena', '_device', 'current', 'staged', 'predicted', 'phases', '_values'))
ARENA_FIELDS = frozenset(('contract', 'device', '_failure', '_last_usage', '_stream', '_settings',
    '_reserved_cap', '_reserved_extent', '_storage', '_pointer', '_counter', '_cursor', '_active',
    '_regions', '_starts', '_phases'))
MAPPINGS = ('current', 'staged', 'predicted', 'phases', '_values')


def _frame(prefix, candidates):
    from .cuda_prefix import _CudaPrefix
    from .cuda_storage import CudaArena
    import torch
    if type(prefix) is not _CudaPrefix or type(prefix.arena) is not CudaArena:
        raise ContractError('registered private CUDA owner and arena required')
    arena = prefix.arena
    if (set(vars(prefix)) != PREFIX_FIELDS or set(vars(arena)) != ARENA_FIELDS
            or type(prefix._device) is not _CudaDevice or set(vars(prefix._device)) != DEVICE_FIELDS):
        raise ProfileUnresolved('CUDA install has no transition proof for an unregistered device state coordinate')
    try:
        prefix.check()
        ready = torch.cuda.default_stream(arena.device).query()
    except MemoryError:
        raise
    except Exception:
        if arena._failure is None:
            arena._failure = 'CUDA installation could not establish its actual device/stream premises'
        raise
    if arena._active is not None or not ready:
        raise ProfileUnresolved('CUDA installation requires a completed arena phase and quiescent registered stream')
    if set(prefix.current) != {c.candidate_id for c in candidates}:
        arena._fail('CUDA installation found a lost or additional published learner binding')
    current = []
    from .indexed_amp import ResidentState
    from .joint_amp import ResidentState as JointResidentState
    state_type = JointResidentState if prefix.joint else ResidentState if prefix.indexed else gpu.CudaLearnerState
    for candidate in candidates:
        phase_id = prefix.current[candidate.candidate_id]
        record, value = prefix.phases.get(phase_id), prefix._values.get(phase_id)
        try:
            if (record is None or type(value) is not state_type
                    or record.status != 'CHECKED_CUDA_PREFIX_PHASE' or record.phase.endswith(':predict')
                    or record.candidate_id != candidate.candidate_id or record.program_id != candidate.program_id
                    or value.cursor != candidate.learner.cursor):
                arena._fail('CUDA installation lost an actual complete learner or its retained state encoding')
            leases = []
            for label, tensor in prefix.state_tensors(value):
                # Ownership/extent checks precede even finite-value readback.
                arena.require_initialized(tensor)
                region = arena._regions[arena._region_for(tensor)]
                leases.append((label, region.sequence, tensor.storage_offset()*tensor.element_size(),
                               tensor.numel()*tensor.element_size(), tuple(tensor.shape), str(tensor.dtype)))
            value.__post_init__()
            if record.raw_state != prefix.raw_state(value):
                arena._fail('CUDA installation changed its retained complete learner encoding')
        except MemoryError:
            raise
        except Exception:
            # A lost resident value/shape cannot leave old crossings live.
            # Preserve an unexpected original exception as well as terminality.
            if arena._failure is None:
                arena._failure = 'CUDA installation could not verify its actual complete resident learner'
            raise
        current.append((candidate.candidate_id, phase_id, record.raw_state, tuple(leases)))
    storage = arena.snapshot()
    result = CudaTransport(tuple(current), arena._pointer, arena._stream, arena._counter,
        storage['actual_tensor_arena_bytes'], storage['actual_allocator_reserved_bytes'],
        storage['consumed_arena_extent'], len(prefix.phases), len(prefix._values))
    return result, storage


def prepare_transport(prefix, candidates):
    """Read actual complete device states; return a private reference witness."""
    frame, storage = _frame(prefix, candidates)
    maps = tuple((key, tuple(getattr(prefix, key).items())) for key in MAPPINGS)
    return (prefix, prefix.contract, prefix.arena, prefix.arena._storage, maps, storage,
            prefix._device, prefix._device.initial, frame)


def verify_transport(witness, prefix, candidates):
    """Only identity transport is implemented; any observed corruption is terminal."""
    previous, contract, arena, backing, maps, storage, device, device_identity, frame = witness
    if (prefix is not previous or prefix.contract is not contract or prefix.arena is not arena
            or prefix.arena._storage is not backing or prefix._device is not device
            or prefix._device.initial is not device_identity):
        arena._fail('CUDA installation substituted its registered prefix or backing arena')
    for key, values in maps:
        current = tuple(getattr(prefix, key).items())
        if key in ('phases', '_values'):
            same = len(values) == len(current) and all(a == c and b is d for (a, b), (c, d) in zip(values, current))
        else:
            same = values == current
        if not same:
            arena._fail('CUDA installation changed retained learner, forecast or phase history')
    observed, current_storage = _frame(prefix, candidates)
    if observed != frame or current_storage != storage:
        arena._fail('CUDA installation changed current state, extents or allocation history')
    return frame
