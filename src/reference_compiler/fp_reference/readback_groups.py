"""Bounded fresh transport for named initialized views; no numerical authority.

The caller supplies the private arena and paid host buffer. Opaque gaps are
cleared and never returned. A plan groups intervals, not semantic states.
"""
from .core import ContractError, natural
from .cuda_storage import CudaStorageUnresolved


def resident_view_bound(definition):
    n, context = definition.output.update_unit, definition.sources.context
    return 11+7*n+(n*(context+1)+2)*n.bit_length()


def resident_work(definition, arena_bytes):
    """Prepay four captures, opaque transport/clearing and bounded sorting.

    Each forest has at most bit_length(N) blocks; at most N*L embedding and
    N correction keys occur. Named-byte processing keeps its original tariff.
    """
    views = resident_view_bound(definition)
    return 16*arena_bytes+256*views*(views+1).bit_length()


def plan(layout, capacity):
    """Greedy contiguous partition of start-sorted, indivisible named extents."""
    natural(capacity, 'readback workspace bytes', positive=True)
    if type(layout) is not tuple:
        raise ContractError('complete immutable named readback layout required')
    ordered = []
    for index, row in enumerate(layout):
        if type(row) is not tuple or len(row) != 2:
            raise ContractError('exact offset/size readback pair required')
        offset, size = row
        natural(offset, 'readback byte offset')
        natural(size, 'readback byte size')
        if size > capacity:
            raise CudaStorageUnresolved('named CUDA observation exceeds its prepaid host workspace')
        if size:
            ordered.append((offset, offset+size, index))
    ordered.sort()
    groups = []
    first = end = None
    members = []
    for low, high, index in ordered:
        if first is not None and max(end, high)-first > capacity:
            groups.append((first, end, tuple(members)))
            first, members = None, []
        if first is None:
            first, end = low, high
        else:
            end = max(end, high)
        members.append(index)
    if first is not None:
        groups.append((first, end, tuple(members)))
    return tuple(groups)


def read(workspace, values, buffer):
    import torch
    if type(values) is not tuple or type(buffer) is not bytearray:
        raise ContractError('complete named views and admitted host readout buffer required')
    workspace.arena._require_stream()
    layout = []
    for value in values:
        # Dynamic dispatch includes exact live-generation checks in token reuse.
        index = workspace.arena._region_for(value)
        if not workspace.arena._regions[index].initialized:
            raise ContractError('grouped raw bytes require an initialized owned extent')
        layout.append((value.storage_offset()*value.element_size(), value.numel()*value.element_size()))
    layout = tuple(layout)
    groups = plan(layout, len(buffer))
    result = [b'']*len(layout)
    for first, end, members in groups:
        host = torch.frombuffer(buffer, dtype=torch.uint8, count=end-first)
        try:
            host.copy_(workspace.arena._storage[first:end], non_blocking=False)
            data = memoryview(buffer)
            for index in members:
                offset, size = layout[index]
                result[index] = bytes(data[offset-first:offset-first+size])
        finally:
            # Includes opaque gaps, even if transfer or byte extraction fails.
            host.zero_()
    return tuple(result)
