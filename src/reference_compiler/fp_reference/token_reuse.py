"""Token-only physical reuse after the owner seals complete phase evidence.

No installation, historical replay or external tensor handles are admitted.
The full backing allocation and all region/retirement metadata stay owned.
"""
from .array_generations import ArrayGenerations
from .core import ContractError, freeze_data
from .cuda_storage import CudaArena, CudaRegion, CudaWorkspace, CudaStorageUnresolved
from .program import name


class TokenReuseArena(CudaArena):
    allocation_id = 'owned-token-buddy-generation-arena-v1'

    def __init__(self, contract):
        if contract.arena_bytes & (contract.arena_bytes-1):
            raise ContractError('token buddy storage requires a power-of-two backing extent')
        super().__init__(contract)
        self._init_reuse()

    def _init_reuse(self):
        # Also used by the CPU audit after binding an actual CPU tensor buffer.
        self._order = self.contract.arena_bytes.bit_length()-1
        self._free = {order: set() for order in range(3, self._order+1)}
        self._free[self._order].add(0)
        self._generations = ArrayGenerations()
        self._generation_regions, self._region_generations = {}, []
        self._pins, self._headers = {}, {}
        self._header_history = []
        self._sealed, self._accepted = set(), set()
        self._retirements = []
        self._allocated_bytes = self._live_bytes = self._peak_live_bytes = 0

    def _reserve(self, size):
        order = max(3, (max(1, size)-1).bit_length())
        found = next((i for i in range(order, self._order+1) if self._free[i]), None)
        if found is None:
            raise CudaStorageUnresolved('token buddy arena has no admitted contiguous extent')
        try:
            offset = self._free[found].pop()
            while found > order:
                found -= 1
                self._free[found].add(offset+(1 << found))
            reserved = 1 << order
            self._allocated_bytes += reserved
            self._live_bytes += reserved
            self._peak_live_bytes = max(self._peak_live_bytes, self._live_bytes)
            self._cursor = max(self._cursor, offset+reserved)
            return offset, reserved
        except Exception:
            self._failure = 'token reuse allocation metadata failed'
            raise

    def _release(self, offset, reserved):
        order = reserved.bit_length()-1
        self._live_bytes -= reserved
        while order < self._order and (offset ^ (1 << order)) in self._free[order]:
            self._free[order].remove(offset ^ (1 << order))
            offset = min(offset, offset ^ (1 << order))
            order += 1
        self._free[order].add(offset)

    def phase(self, owner):
        name(owner, 'CUDA phase owner')
        self.check()
        if self._active is not None:
            raise ContractError('a CUDA arena cannot overlap execution phases')
        index, beginning = len(self._phases), self._allocated_bytes
        offset, reserved = self._reserve(8)
        self._header_history.append((index, offset, reserved))
        self._headers[index] = (offset, reserved)
        self._phases.append((index, owner, beginning, None, 'EXECUTING'))
        workspace = TokenReuseWorkspace(self, index, owner)
        self._active = workspace
        return workspace

    def _geometry(self, value, index):
        import torch
        if (type(value) is not torch.Tensor or value.device != self.device
                or value.requires_grad or not value.is_contiguous()
                or value.is_neg() or value.is_conj()
                or value.untyped_storage().data_ptr() != self._pointer):
            raise ContractError('token operand is not an owned contiguous tensor view')
        offset, size = value.storage_offset()*value.element_size(), value.numel()*value.element_size()
        region = self._regions[index]
        if (offset < region.offset or offset+size > region.offset+region.byte_size
                or str(value.dtype) != region.dtype):
            raise ContractError('token view crosses its generation extent or changes dtype')

    def _region_for(self, value):
        generation = self._generations.require(value)
        index = self._generation_regions[generation]
        self._geometry(value, index)
        return index

    def derive(self, parent, view):
        index = self._region_for(parent)
        self._geometry(view, index)
        self._generations.derive(parent, view)
        return view

    def seal(self, record):
        # Only Runtime calls this after actual canonical-frame retention.
        index = record.arena_phase
        if (type(index) is not int or not 0 <= index < len(self._phases)
                or self._phases[index][1] != record.object_id
                or self._phases[index][-1] != 'EXECUTED'
                or record.status != 'CHECKED_CUDA_PREFIX_PHASE' or index in self._sealed):
            raise ContractError('token reuse requires a newly retained complete successful phase')
        self._sealed.add(index)
        self._pins = {generation: value for generation, value in self._pins.items()
                      if self._regions[self._generation_regions[generation]].phase != index}

    def accept(self, record):
        if record.arena_phase not in self._sealed or record.arena_phase in self._accepted:
            raise ContractError('an unsealed or historical token phase cannot gain physical authority')
        self._accepted.add(record.arena_phase)

    def collect(self, roots):
        self.check()
        if self._active is not None:
            raise ContractError('token collection requires a boundary with no active workspace')
        keep = set()
        for value in roots:
            self.require_initialized(value)
            keep.add(self._generations.require(value))
        retired = tuple(sorted(g for g in self._generations._live if g not in keep
            and self._regions[self._generation_regions[g]].phase in self._sealed))
        headers = tuple(sorted(i for i in self._headers if i in self._sealed))
        # Allocate the full retirement record before invalidating any handle.
        self._retirements.append((len(self._phases), retired, headers))
        try:
            for generation in retired:
                region = self._regions[self._generation_regions[generation]]
                self._generations.retire(generation)  # Invalidate before reuse.
                self._release(region.offset, region.reserved_size)
            for index in headers:
                self._release(*self._headers.pop(index))
            self._generations.prune_dead_views()
        except Exception:
            # A partial metadata failure cannot resume allocation/collection.
            self._failure = 'token reuse retirement metadata failed'
            raise

    def reuse_snapshot(self):
        return dict(storage_lowering=self.allocation_id,
            phase_extent_coordinates='cumulative buddy-reserved allocation bytes',
            cumulative_reserved_bytes=self._allocated_bytes,
            live_reserved_bytes=self._live_bytes, peak_live_reserved_bytes=self._peak_live_bytes,
            region_generations=tuple(self._region_generations),
            live_generations=tuple(sorted(self._generations._live)),
            sealed_phases=tuple(sorted(self._sealed)), accepted_phases=tuple(sorted(self._accepted)),
            unsealed_pins=tuple(sorted(self._pins)), live_headers=tuple(sorted(self._headers.items())),
            header_history=tuple(self._header_history),
            retirements=tuple(self._retirements))

    def snapshot(self):
        return freeze_data(dict(super().snapshot(), **self.reuse_snapshot()))


class TokenReuseWorkspace(CudaWorkspace):
    def empty(self, shape, dtype, operation):
        import torch
        self._open()
        if type(shape) is not tuple or any(type(v) is not int or v < 0 for v in shape):
            raise ContractError('exact bounded token CUDA output shape required')
        widths = {torch.float16: 2, torch.float32: 4, torch.int64: 8}
        if dtype not in widths:
            raise ContractError('unregistered token reuse format')
        elements = 1
        for size in shape:
            if size and elements > self.arena.contract.arena_bytes//widths[dtype]//size:
                raise CudaStorageUnresolved('token tensor exceeds its complete backing extent')
            elements *= size
        size = elements*widths[dtype]
        offset, reserved = self.arena._reserve(size)
        try:
            view = self.arena._storage.narrow(0, offset, size).view(dtype).reshape(shape)
            generation = self.arena._generations.issue(view)
            index = len(self.arena._regions)
            self.arena._regions.append(CudaRegion(index, self.index, self.owner, operation,
                offset, size, reserved, shape, str(dtype)))
            self.arena._region_generations.append(generation)
            self.arena._generation_regions[generation] = index
            self.arena._pins[generation] = view
            return view
        except Exception:
            self.arena._failure = 'token reuse view admission failed'
            raise

    def finish(self, status):
        if self._closed or self.arena._active is not self:
            raise ContractError('CUDA workspace no longer has current phase ownership')
        if status not in ('EXECUTED', 'FAILED'):
            raise ContractError('a CUDA phase needs its actual terminal status')
        prior = self.arena._phases[self.index]
        self.arena._phases[self.index] = (*prior[:3], self.arena._allocated_bytes, status)
        self.arena._active, self._closed = None, True
        try:
            self.arena.check()
        except Exception:
            self.arena._phases[self.index] = (*prior[:3], self.arena._allocated_bytes, 'FAILED')
            raise


def collection_work(prefix):
    # A prepaid primitive tariff for root enumeration, all live-view metadata,
    # buddy levels and pruning. Not a hash-table bit-time or host-heap theorem.
    arena = prefix.arena
    maps = len(prefix.current)+len(prefix.staged)+len(prefix.predicted)
    return (256*(maps+1)*(len(arena._regions)+len(arena._generations._views)
        +len(prefix._values)+len(arena._phases)+1)
        +64*prefix.contract.phase_output_cells)*(arena._order+1)


def collect(prefix):
    from .token_cuda_state import Resident, PredictionResident, ReadoutResident
    prefix.check()
    identities = set(prefix.current.values()) | set(prefix.staged.values()) | set(prefix.predicted.values())
    stack = [prefix._values[identity] for identity in identities]
    seen, arrays = set(), []
    while stack:
        value = stack.pop()
        if id(value) in seen:
            continue
        seen.add(id(value))
        if type(value) not in (Resident, PredictionResident, ReadoutResident):
            raise ContractError('token continuation root has an unregistered physical resident')
        arrays.extend(tensor for _, tensor in value.tensors())
        if type(value) is PredictionResident:
            stack.append(value.predecessor)
        elif type(value) is ReadoutResident:
            stack.append(value.prediction)
    prefix.arena.collect(arrays)
    # Failed/unsealed objects and all historical phase words remain. Only the
    # private physical lookup loses successful residents unreachable by maps.
    prefix._values = {identity: value for identity, value in prefix._values.items()
        if identity in identities or prefix.phases[identity].arena_phase not in prefix.arena._sealed}
