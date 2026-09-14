"""A bounded actual CUDA tensor arena with explicit initialized view extents.

This storage component has no Runtime authority. One real backing allocation
is shared in full by deployment and compiler. TensorAllocator counters must
not record any further allocation while its phases execute. Driver/context,
non-PyTorch allocations and total-device accounting are separate obligations.
No counters are reset, no cache is emptied and no old view address is reused.
"""
from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_right
from typing import Mapping

from .core import ContractError, freeze_data, natural
from .program import name
from .resources import ResourceExceeded


@dataclass(frozen=True)
class CudaStorageContract:
    arena_bytes: int
    allocator_reserved_cap: int
    role_caps: Mapping[str, tuple[int, int]]
    device: int = 0

    def __post_init__(self):
        natural(self.arena_bytes, 'CUDA tensor arena bytes', positive=True)
        natural(self.allocator_reserved_cap, 'CUDA allocator reservation cap', positive=True)
        natural(self.device, 'CUDA device ordinal')
        if self.arena_bytes % 512 or self.arena_bytes >= 1 << 63:
            raise ContractError('CUDA arena needs a bounded 512-byte multiple')
        if not isinstance(self.role_caps, Mapping) or set(self.role_caps) != {'deployment', 'compiler'}:
            raise ContractError('CUDA shared arena needs both fixed resource roles')
        caps = {}
        for role, values in self.role_caps.items():
            if type(values) is not tuple or len(values) != 2:
                raise ContractError('each CUDA role needs arena and allocator-reservation caps')
            caps[role] = tuple(natural(value, 'CUDA role cap', positive=True) for value in values)
        object.__setattr__(self, 'role_caps', freeze_data(caps))


@dataclass(frozen=True, slots=True)
class CudaRegion:
    sequence: int
    phase: int
    owner: str
    operation: str
    offset: int
    byte_size: int
    reserved_size: int
    shape: tuple[int, ...]
    dtype: str
    initialized: bool = False


class CudaStorageUnresolved(ResourceExceeded):
    """The actual tensor storage no longer establishes its declared bound."""


def initial_reservation_bytes(arena_bytes):
    """PyTorch 2.12 native allocator with explicit 20 MiB large segments.

    Contract requires a 512-byte request multiple. No active/cached block,
    allocator setting change or captured/replayed allocation is substituted.
    """
    natural(arena_bytes, 'CUDA arena bytes', positive=True)
    if arena_bytes % 512:
        raise ContractError('initial CUDA allocation needs its declared rounding quantum')
    mib = 1 << 20
    if arena_bytes <= mib:
        return 2*mib
    if arena_bytes < 10*mib:
        return 20*mib
    return ((arena_bytes+2*mib-1)//(2*mib))*2*mib


class CudaArena:
    allocation_id = 'single-cuda-tensor-arena-ordered-out-v1'
    allocator_configuration = 'large_segment_size_mb:20'

    def __init__(self, contract: CudaStorageContract):
        if type(contract) is not CudaStorageContract:
            raise ContractError('immutable CUDA storage declaration required')
        contract.__post_init__()
        if any(contract.arena_bytes > caps[0] for caps in contract.role_caps.values()):
            raise CudaStorageUnresolved('actual shared arena exceeds a registered role cap')
        import torch
        if not torch.cuda.is_available() or contract.device >= torch.cuda.device_count():
            raise CudaStorageUnresolved('actual registered CUDA device unavailable')
        self.contract = contract
        self.device = torch.device('cuda', contract.device)
        self._failure = None
        self._last_usage = None
        if torch.cuda.get_allocator_backend() != 'native':
            raise CudaStorageUnresolved('unimplemented CUDA allocator counters')
        if str(torch.__version__).split('+')[0] != '2.12.0':
            raise CudaStorageUnresolved('initial allocator extent model requires the audited PyTorch 2.12 build family')
        self._stream = torch.cuda.default_stream(self.device).cuda_stream
        self._require_stream()
        self._settings = torch.cuda.memory._snapshot().get('allocator_settings')
        if (not isinstance(self._settings, dict) or self._settings.get('PYTORCH_CUDA_ALLOC_CONF') != ''
                or self._settings.get('expandable_segments') is not False
                or self._settings.get('max_split_size') != -1
                or self._settings.get('garbage_collection_threshold') != 0.0
                or not isinstance(self._settings.get('roundup_power2_divisions'), dict)
                or any(self._settings['roundup_power2_divisions'].values())):
            raise CudaStorageUnresolved('initial CUDA extent model requires the actual default allocator settings')
        if (self._allocation_counter() != (0, 0, 0) or torch.cuda.memory_allocated(self.device)
                or torch.cuda.memory_reserved(self.device) or torch.cuda.max_memory_reserved(self.device)):
            raise CudaStorageUnresolved('fresh native CUDA allocation history required; no cache or counter reset')
        if torch.cuda.is_current_stream_capturing():
            raise CudaStorageUnresolved('CUDA arena cannot bind during a graph capture')
        self._reserved_cap = min(contract.allocator_reserved_cap, *(caps[1] for caps in contract.role_caps.values()))
        self._reserved_extent = initial_reservation_bytes(contract.arena_bytes)
        if self._reserved_extent > self._reserved_cap:
            raise CudaStorageUnresolved('initial CUDA allocator segment exceeds a registered reservation cap before allocation')
        # An empty last-config string does NOT restore large_segment_size.
        # Bind that hidden persistent setting explicitly before any allocation.
        # Clearing configuration/history or trusting a snapshot alias is not
        # an alternative proof of this first-allocation extent.
        torch._C._accelerator_setAllocatorSettings(self.allocator_configuration)
        self._settings = freeze_data(torch.cuda.memory._snapshot()['allocator_settings'])
        if self._settings['PYTORCH_CUDA_ALLOC_CONF'] != self.allocator_configuration:
            raise CudaStorageUnresolved('explicit native allocator configuration was not bound')
        self._storage = torch.empty(contract.arena_bytes, dtype=torch.uint8, device=self.device)
        self._pointer = self._storage.untyped_storage().data_ptr()
        self._counter = self._allocation_counter()
        if (self._counter != (1, contract.arena_bytes, 1)
                or torch.cuda.memory_reserved(self.device) != self._reserved_extent):
            self._fail('actual initial CUDA allocation differs from the registered default segment model')
        self._cursor = 0
        self._active = None
        self._regions = []
        self._starts = []
        self._phases = []
        self.check()

    def _require_stream(self):
        import torch
        if torch.cuda.current_stream(self.device).cuda_stream != self._stream:
            self._fail('CUDA arena requires its serialized default stream')

    def _fail(self, reason):
        if self._failure is None:
            self._failure = reason
        raise CudaStorageUnresolved(self._failure)

    def _allocation_counter(self):
        import torch
        stats = torch.cuda.memory_stats(self.device)
        keys = ('allocation.all.allocated', 'allocated_bytes.all.allocated', 'segment.all.allocated')
        if any(key not in stats for key in keys):
            raise CudaStorageUnresolved('required native allocator history is unavailable')
        return tuple(stats[key] for key in keys)

    def check(self):
        import torch
        if self._failure is not None:
            raise CudaStorageUnresolved(self._failure)
        self._require_stream()
        self._last_usage = {'allocation_counter': self._allocation_counter(),
            'actual_tensor_arena_bytes': torch.cuda.memory_allocated(self.device),
            'actual_allocator_reserved_bytes': torch.cuda.memory_reserved(self.device),
            'lifetime_tensor_peak_bytes': torch.cuda.max_memory_allocated(self.device),
            'lifetime_allocator_reserved_peak_bytes': torch.cuda.max_memory_reserved(self.device)}
        if torch.cuda.get_allocator_backend() != 'native' or self._last_usage['allocation_counter'] != self._counter:
            self._fail('a CUDA allocation escaped the owned tensor arena')
        if torch.cuda.memory._snapshot().get('allocator_settings') != self._settings:
            self._fail('CUDA allocator settings changed after immutable arena binding')
        if self._last_usage['actual_tensor_arena_bytes'] != self.contract.arena_bytes:
            self._fail('actual CUDA tensor residency differs from the owned backing buffer')
        if max(self._last_usage['actual_allocator_reserved_bytes'], self._last_usage['lifetime_allocator_reserved_peak_bytes']) > self._reserved_cap:
            self._fail('actual lifetime CUDA allocator reservation exceeds its declared cap')

    def phase(self, owner: str):
        name(owner, 'CUDA phase owner')
        self.check()
        if self._active is not None:
            raise ContractError('a CUDA arena cannot overlap execution phases')
        # An empty attempted phase still consumes an extent and a new identity.
        # Neither a failed control loop nor an empty tensor recycles metadata.
        if self._cursor+8 > self.contract.arena_bytes:
            raise CudaStorageUnresolved('CUDA arena has no room for another owned phase')
        index = len(self._phases)
        self._phases.append((index, owner, self._cursor, None, 'EXECUTING'))
        self._cursor += 8
        workspace = CudaWorkspace(self, index, owner)
        self._active = workspace
        return workspace

    def _region_for(self, value):
        import torch
        if (type(value) is not torch.Tensor or value.device != self.device
                or value.requires_grad or not value.is_contiguous()
                or value.is_neg() or value.is_conj()
                or value.untyped_storage().data_ptr() != self._pointer):
            raise ContractError('CUDA operand is not a view of its owned arena')
        offset, size = value.storage_offset()*value.element_size(), value.numel()*value.element_size()
        index = bisect_right(self._starts, offset)-1
        if index < 0:
            raise ContractError('CUDA operand has no declared initialized extent')
        region = self._regions[index]
        if offset+size > region.offset+region.byte_size or str(value.dtype) != region.dtype:
            raise ContractError('CUDA view crosses an extent or changes its declared dtype')
        return index

    def require_initialized(self, value):
        index = self._region_for(value)
        if not self._regions[index].initialized:
            raise ContractError('uninitialized CUDA storage cannot become a numeric input')

    def _mark(self, value, phase):
        from dataclasses import replace
        index = self._region_for(value)
        region = self._regions[index]
        if region.phase != phase or region.initialized:
            raise ContractError('a CUDA phase cannot initialize an old or already written extent')
        if (value.storage_offset()*value.element_size() != region.offset
                or value.numel()*value.element_size() != region.byte_size):
            raise ContractError('a partial write cannot initialize an entire CUDA extent')
        self._regions[index] = replace(region, initialized=True)

    def snapshot(self):
        import torch
        if self._failure is None:
            self.check()
        return freeze_data({'allocation_id': self.allocation_id,
            'contract': {'arena_bytes': self.contract.arena_bytes,
                         'allocator_reserved_cap': self.contract.allocator_reserved_cap,
                         'role_caps': self.contract.role_caps, 'device': self.contract.device},
            'status': 'ACTIVE' if self._failure is None else 'UNRESOLVED', 'failure': self._failure,
            'device_name': torch.cuda.get_device_name(self.device),
            'capability': tuple(torch.cuda.get_device_capability(self.device)),
            'torch': str(torch.__version__), 'torch_git_version': torch.version.git_version,
            'CUDA_runtime': torch.version.cuda, 'default_stream': self._stream,
            'initial_allocator_settings': self._settings,
            'allocator_configuration': self.allocator_configuration,
            'prepaid_initial_allocator_segment_bytes': self._reserved_extent,
            **self._last_usage,
            'role_tensor_arena_bytes': {role: self.contract.arena_bytes for role in self.contract.role_caps},
            'role_allocator_reserved_bytes': {role: self._last_usage['actual_allocator_reserved_bytes'] for role in self.contract.role_caps},
            'native_allocation_counter_at_binding': self._counter,
            'native_allocation_counter_current': self._last_usage['allocation_counter'],
            'consumed_arena_extent': self._cursor,
            'regions': tuple((r.sequence, r.phase, r.owner, r.operation, r.offset, r.byte_size,
                              r.reserved_size, r.shape, r.dtype, r.initialized) for r in self._regions),
            'phases': tuple(self._phases)})


class CudaWorkspace:
    """One private phase's new extents; old initialized views stay readable."""
    def __init__(self, arena, index, owner):
        self.arena, self.index, self.owner = arena, index, owner
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        try:
            self.finish('EXECUTED' if kind is None else 'FAILED')
        except Exception as close_error:
            # A resource refusal at closure cannot downgrade an earlier
            # unexpected kernel/programming exception into budget uncertainty.
            from .semantics import ArithmeticUnresolved
            if value is not None and not isinstance(value, (ResourceExceeded, ArithmeticUnresolved)):
                value.add_note(f'CUDA phase closure also failed: {type(close_error).__name__}: {close_error}')
                raise value.with_traceback(traceback) from close_error
            raise

    def _open(self):
        if self._closed or self.arena._active is not self:
            raise ContractError('CUDA workspace no longer has current phase ownership')
        self.arena._require_stream()

    def empty(self, shape, dtype, operation):
        import torch
        self._open()
        if type(shape) is not tuple or any(type(v) is not int or v < 0 for v in shape):
            raise ContractError('exact bounded CUDA output shape required')
        widths = {torch.float16: 2, torch.float32: 4, torch.int32: 4, torch.bool: 1}
        if dtype not in widths:
            raise ContractError('unregistered CUDA arena storage format')
        available = self.arena.contract.arena_bytes-self.arena._cursor
        elements = 1
        for size in shape:
            if size and elements > available//widths[dtype]//size:
                raise CudaStorageUnresolved('CUDA tensor extent exceeds remaining arena storage')
            elements *= size
        size = elements*widths[dtype]
        reserved = max(8, ((size+7)//8)*8)
        if reserved > available:
            raise CudaStorageUnresolved('CUDA tensor extent/padding exceeds remaining arena storage')
        offset = self.arena._cursor
        view = self.arena._storage.narrow(0, offset, size).view(dtype).reshape(shape)
        region = CudaRegion(len(self.arena._regions), self.index, self.owner, operation,
                            offset, size, reserved, shape, str(dtype))
        self.arena._regions.append(region)
        self.arena._starts.append(offset)
        self.arena._cursor += reserved
        return view

    def written(self, value):
        self._open()
        self.arena._mark(value, self.index)
        return value

    def require_initialized(self, value):
        self._open()
        self.arena.require_initialized(value)

    def finish(self, status):
        if self._closed or self.arena._active is not self:
            raise ContractError('CUDA workspace no longer has current phase ownership')
        if status not in ('EXECUTED', 'FAILED'):
            raise ContractError('a CUDA phase needs its actual terminal status')
        prior = self.arena._phases[self.index]
        self.arena._phases[self.index] = (*prior[:3], self.arena._cursor, status)
        self.arena._active = None
        self._closed = True
        try:
            self.arena.check()
        except Exception:
            self.arena._phases[self.index] = (*prior[:3], self.arena._cursor, 'FAILED')
            raise
