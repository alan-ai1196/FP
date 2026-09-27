"""Private owned retention of exact packed values in lossless shared pages.

No native or floating learner is changed. This lowering is registered only
for token Runtime events/profiles; search, persistence and installation have
no authority here. All page dependencies stay resident in both resource roles.
"""
from dataclasses import dataclass, fields, replace

from .core import ContractError, natural
from .resources import ObjectSpec
from .encoding import bounded_packed_size, fragments
from . import byte_archive as archive


ROOT_MAGIC = b'FPBRv1\0\0'
ROOT_BYTES = len(ROOT_MAGIC)+archive.U64.size
ROOT_KIND = 'shared_reference_root:'


@dataclass(frozen=True)
class SharedReferenceContract:
    literal_workspace: int
    program_workspace: int
    expanded_cap: int
    reference_cap: int
    comparison_cap: int
    encoding: str = archive.ENCODING_ID

    def __post_init__(self):
        if type(self) is not SharedReferenceContract or set(vars(self)) != {f.name for f in fields(self)}:
            raise ContractError('closed immutable shared reference registration required')
        for field in fields(self):
            if field.name != 'encoding':
                natural(getattr(self, field.name), 'shared reference '+field.name, positive=True)
        if (self.encoding != archive.ENCODING_ID or self.literal_workspace < archive.HEADER.size
                or archive.U64.size*self.reference_cap > archive.phase_deflate.EXPANDED_CAP):
            raise ContractError('registered archive format and bounded reference expansion required')


@dataclass(frozen=True)
class SharedReferenceManifest:
    reference: object
    storage: SharedReferenceContract


@dataclass(frozen=True)
class SharedReferenceSnapshot:
    contract: SharedReferenceContract
    pages: tuple[str, ...]
    workspaces: tuple[str, ...]


@dataclass(frozen=True)
class SharedPlannedObject:
    """A root/value recipe; its body is traversed only after Runtime payment."""
    spec: ObjectSpec
    value: object


def _packed_parts(value, staging):
    """Canonical owner traversal; only emitted bytes reach the producer.

    Coalesce short syntax fragments while keeping substantial literal pieces
    aligned across occurrences. This affects storage only, never decoding.
    """
    used = 0
    for fragment in fragments(value, packed=True):
        part = fragment.encode('utf-8', 'surrogatepass')
        if len(part) >= 256:
            if used:
                yield bytes(memoryview(staging)[:used])
                used = 0
            yield from archive.byte_pieces(part)
        else:
            if used+len(part) > len(staging):
                yield bytes(memoryview(staging)[:used])
                used = 0
            staging[used:used+len(part)] = part
            used += len(part)
    if used:
        yield bytes(memoryview(staging)[:used])


def _compare_stream(actual, expected, size):
    expected = iter(expected)
    current, position, compared = b'', 0, 0
    for piece in actual:
        offset = 0
        while offset < len(piece):
            if position == len(current):
                current = next(expected, None)
                if current is None:
                    raise ContractError('shared reference expansion added bytes')
                position = 0
                if not current:
                    continue
            count = min(len(piece)-offset, len(current)-position)
            if piece[offset:offset+count] != current[position:position+count]:
                raise ContractError('shared reference differs from the complete owned record')
            offset += count
            position += count
            compared += count
    if compared != size or position != len(current) or any(expected):
        raise ContractError('shared reference expansion lost bytes')


class _SharedReference:
    def __init__(self, runtime, contract):
        contract.__post_init__()
        self.contract = contract
        self.encoder, self.reader = archive.Encoder(), archive.Reader()
        self.pages = []
        prefix = runtime._runtime_id+':shared-reference'
        self.deployment_owner = prefix+':deployment-dependencies'
        runtime._ledger.register_owner(self.deployment_owner, 'deployment')
        sizes = (contract.literal_workspace, contract.program_workspace,
                 archive.phase_deflate.BLOCK, 512)
        self.workspaces = tuple(prefix+':'+name for name in ('literals', 'program', 'references', 'canonical-staging'))
        specs = tuple(ObjectSpec(identity, 'shared_reference_workspace',
            {'reference_payload_bytes': size, 'physical_objects': 1}, runtime._chi)
            for identity, size in zip(self.workspaces, sizes))
        runtime._ledger.allocate(runtime._data_owner, specs)
        for identity, size in zip(self.workspaces, sizes):
            runtime._buffers[identity] = bytearray(size)
        for identity in self.workspaces:
            runtime._ledger.acquire(self.deployment_owner, identity)

    def snapshot(self):
        return SharedReferenceSnapshot(self.contract, tuple(self.pages), self.workspaces)

    def allocate(self, runtime, owner, planned):
        """All fallible retention precedes any caller's learner publication."""
        cfg = self.contract
        # Pay bounded traversal, compression, complete independent decoding,
        # collision comparisons, page copies and metadata before any work.
        # Python heap/library workspace remain under the separate host model.
        work = (32*cfg.expanded_cap+16*cfg.reference_cap+4*cfg.comparison_cap
                +8*(cfg.literal_workspace+cfg.program_workspace)
                +64*(len(runtime._ledger._objects)+len(self.encoder._pieces)+1))
        runtime._ledger.charge_work(runtime._ledger._owners[owner], {'work': work},
                                   note=planned.spec.object_id+':shared-reference')
        try:
            size = bounded_packed_size(planned.value, byte_limit=cfg.expanded_cap,
                                       integer_bits=runtime._contract.reference_integer_bits)
            literals, program, refs, staging = (runtime._buffers[key] for key in self.workspaces)
            builder = self.encoder.begin(literals, program, refs, byte_cap=max(1, size),
                reference_cap=cfg.reference_cap, comparison_cap=cfg.comparison_cap)
            for part in _packed_parts(planned.value, staging):
                builder.push(part)
            header = builder.finish()
            if header.expanded_bytes != size:
                raise ContractError('shared reference encoder changed the complete extent')
            page_id = runtime._runtime_id+f':shared-reference:page:{len(self.pages)}'
            scratch_id = page_id+':copy'
            extent = {'reference_payload_bytes': builder.extent, 'physical_objects': 1}
            runtime._ledger.allocate(runtime._data_owner, (
                ObjectSpec(scratch_id, 'shared_reference_copy_workspace', extent, runtime._chi),))
            runtime._buffers[scratch_id] = bytearray(builder.extent)
            runtime._ledger.acquire(self.deployment_owner, scratch_id)
            builder.write(runtime._buffers[scratch_id])
            runtime._ledger.allocate(runtime._data_owner, (
                ObjectSpec(page_id, 'immutable_shared_reference_page', extent, runtime._chi),))
            runtime._buffers[page_id] = bytes(runtime._buffers[scratch_id])
            # All dependencies are retained under both roles, conservatively.
            # A tiny deployment root cannot hide a compiler-owned dictionary.
            runtime._ledger.acquire(self.deployment_owner, page_id)
            root = replace(planned.spec, kind=ROOT_KIND+planned.spec.kind,
                residency={'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1})
            runtime._ledger.allocate(owner, (root,))
            runtime._buffers[root.object_id] = bytearray(ROOT_BYTES)
            # This reader never receives producer indices or expected values.
            self.reader.add(runtime._buffers[page_id])
            _compare_stream(self.reader.decoded(header.ordinal, byte_cap=cfg.expanded_cap,
                reference_cap=cfg.reference_cap),
                (s.encode('utf-8', 'surrogatepass') for s in fragments(planned.value, packed=True)), size)
            self.encoder.add(runtime._buffers[page_id])
            self.pages.append(page_id)
            # Fill the admitted mutable 16-byte root in place. It is never
            # rewritten later; public snapshots receive their own byte value.
            runtime._buffers[root.object_id][:] = ROOT_MAGIC+archive.U64.pack(header.ordinal)
            runtime._ledger.release_many(((runtime._data_owner, scratch_id, 1),
                                         (self.deployment_owner, scratch_id, 1)))
            runtime._buffers.pop(scratch_id)
        except MemoryError:
            raise
        except Exception as error:
            # A failed producer may retain its workspaces through traceback;
            # keep every lease and target and forbid another page/continuation.
            runtime._halt('shared-reference-retention', error)
            raise


def decoded_buffer(snapshot, object_id, *, byte_cap, reference_cap):
    """Passive snapshot inspection. No Runtime query or evidence authority."""
    config = snapshot.reference_archive
    if type(config) is not SharedReferenceSnapshot:
        raise ContractError('snapshot lacks its complete shared reference registration')
    buffers = dict(snapshot.buffers)
    raw = buffers[object_id]
    kind = snapshot.resources['objects'][object_id]['kind']
    if not kind.startswith(ROOT_KIND) or len(raw) != ROOT_BYTES or raw[:8] != ROOT_MAGIC:
        raise ContractError('owned shared reference root required')
    ordinal = archive.U64.unpack_from(raw, 8)[0]
    if ordinal >= len(config.pages):
        raise ContractError('shared reference root has no retained page')
    reader = archive.Reader()
    for identity in config.pages[:ordinal+1]:
        reader.add(buffers[identity])
    yield from reader.decoded(ordinal, byte_cap=byte_cap, reference_cap=reference_cap)
