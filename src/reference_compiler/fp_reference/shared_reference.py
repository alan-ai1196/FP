"""Private owned retention of exact packed values in lossless shared pages.

No native or floating learner is changed. This lowering is registered only
for token Runtime events/profiles; search, persistence and installation have
no authority here. All page dependencies stay resident in both resource roles.
"""
from dataclasses import dataclass, fields, replace

from .core import ContractError, natural
from .resources import ObjectSpec, ResourceExceeded, CostRouter
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
    canonical_image_bytes: int = 0
    token_invariant_bytes: int = 0

    def __post_init__(self):
        if type(self) is not SharedReferenceContract or set(vars(self)) != {f.name for f in fields(self)}:
            raise ContractError('closed immutable shared reference registration required')
        for field in fields(self):
            if field.name != 'encoding':
                natural(getattr(self, field.name), 'shared reference '+field.name,
                        positive=field.name not in ('canonical_image_bytes', 'token_invariant_bytes'))
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
    canonical_images: tuple = ()
    token_base_facts: tuple = ()


@dataclass(frozen=True)
class SharedPlannedObject:
    """A root/value recipe; its body is traversed only after Runtime payment."""
    spec: ObjectSpec
    value: object


def _packed_parts(value, staging, images=None):
    """Canonical owner traversal; only emitted bytes reach the producer.

    Coalesce short syntax fragments while keeping substantial literal pieces
    aligned across occurrences. This affects storage only, never decoding.
    """
    used = 0
    for fragment in fragments(value, packed=True, images=images):
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
        # Reader yields bounded unsigned-byte views of immutable owned pages.
        # One local copy preserves every byte and the independent expected
        # traversal while making overlap comparisons ordinary bytes equality.
        piece = bytes(piece)
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


def _raw_parts(raw, start=0):
    for offset in range(start, len(raw), archive.PIECE_LIMIT):
        yield bytes(memoryview(raw)[offset:offset+archive.PIECE_LIMIT])


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
        from .canonical_images import _CanonicalImages
        self.images = (_CanonicalImages(runtime, self.deployment_owner, contract.canonical_image_bytes)
                       if contract.canonical_image_bytes else None)
        from .token_base_facts import _TokenBaseFacts
        self.base_facts = (_TokenBaseFacts(runtime, self.deployment_owner, contract.token_invariant_bytes)
                           if contract.token_invariant_bytes else None)

    def snapshot(self):
        return SharedReferenceSnapshot(self.contract, tuple(self.pages), self.workspaces,
            () if self.images is None else self.images.snapshot(),
            () if self.base_facts is None else self.base_facts.snapshot())

    def _charge(self, runtime, role, label):
        cfg = self.contract
        # Pay bounded traversal, compression, complete independent decoding,
        # collision comparisons, page copies and metadata before any work.
        # Python heap/library workspace remain under the separate host model.
        ledger = runtime._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
                   +len(ledger._owners)+len(ledger._retired)+len(runtime._buffers)
                   +len(runtime.__dict__)+len(self.encoder._pieces)+16)
        work = (32*cfg.expanded_cap+16*cfg.reference_cap+4*cfg.comparison_cap
                +8*(cfg.literal_workspace+cfg.program_workspace)
                +64*entries)
        if self.images is not None:
            work += 64*cfg.expanded_cap+64*len(self.images.entries)
        ledger.charge_work(role, {'work': work}, note=label+':shared-reference')

    def prepare_frame(self, runtime, label, value, *, role):
        if self.images is None:
            return
        self._charge(runtime, role, label+':canonical-images')
        bounded_packed_size(value, byte_limit=self.contract.expanded_cap,
            integer_bits=runtime._contract.reference_integer_bits, images=self.images)
        self.images.prepare(value, role=role)

    def _begin(self, runtime, size):
        cfg = self.contract
        if size > cfg.expanded_cap:
            raise ResourceExceeded('complete archive input exceeds its registered allowance')
        literals, program, refs = (runtime._buffers[key] for key in self.workspaces[:3])
        return self.encoder.begin(literals, program, refs, byte_cap=max(1, size),
            reference_cap=cfg.reference_cap, comparison_cap=cfg.comparison_cap)

    def _materialize(self, runtime, builder):
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
        # A tiny root cannot hide its dictionary in the other role's budget.
        runtime._ledger.acquire(self.deployment_owner, page_id)
        return page_id, scratch_id

    def _read(self, runtime, page_id, expected, size):
        cfg = self.contract
        header = self.reader.add(runtime._buffers[page_id])
        _compare_stream(self.reader.decoded(header.ordinal, byte_cap=cfg.expanded_cap,
            reference_cap=cfg.reference_cap), expected, size)
        return header

    def _accept(self, runtime, page_id):
        self.encoder.add(runtime._buffers[page_id])
        self.pages.append(page_id)

    def _scratch_releases(self, runtime, scratch_id):
        return ((runtime._data_owner, scratch_id, 1), (self.deployment_owner, scratch_id, 1))

    def allocate(self, runtime, owner, planned):
        """All fallible retention precedes any caller's learner publication."""
        cfg = self.contract
        self._charge(runtime, runtime._ledger._owners[owner], planned.spec.object_id)
        try:
            size = bounded_packed_size(planned.value, byte_limit=cfg.expanded_cap,
                                       integer_bits=runtime._contract.reference_integer_bits, images=self.images)
            if self.images is not None:
                self.images.prepare(planned.value, role=runtime._ledger._owners[owner])
            staging = runtime._buffers[self.workspaces[3]]
            builder = self._begin(runtime, size)
            for part in _packed_parts(planned.value, staging, self.images):
                builder.push(part)
            header = builder.finish()
            if header.expanded_bytes != size:
                raise ContractError('shared reference encoder changed the complete extent')
            page_id, scratch_id = self._materialize(runtime, builder)
            root = replace(planned.spec, kind=ROOT_KIND+planned.spec.kind,
                residency={'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1})
            runtime._ledger.allocate(owner, (root,))
            runtime._buffers[root.object_id] = bytearray(ROOT_BYTES)
            # This reader never receives producer indices or expected values.
            self._read(runtime, page_id,
                (s.encode('utf-8', 'surrogatepass') for s in fragments(planned.value, packed=True, images=self.images)), size)
            self._accept(runtime, page_id)
            # Fill the admitted mutable 16-byte root in place. It is never
            # rewritten later; public snapshots receive their own byte value.
            runtime._buffers[root.object_id][:] = ROOT_MAGIC+archive.U64.pack(header.ordinal)
            runtime._ledger.release_many(self._scratch_releases(runtime, scratch_id))
            runtime._buffers.pop(scratch_id)
        except MemoryError:
            raise
        except Exception as error:
            # A failed producer may retain its workspaces through traceback;
            # keep every lease and target and forbid another page/continuation.
            runtime._halt('shared-reference-retention', error)
            raise

    def seal_cuda_frame(self, runtime, label, record, *, role):
        """Reencode the whole paid frame, then relocate its root atomically.

        The original writer has already dropped every mutable alias. Neither
        the tensor arena nor any learner's physical storage is relocated.
        """
        self._charge(runtime, role, label)
        extent = runtime._ledger._objects[label]
        if (extent.kind != 'owned_cuda_phase_frame' or extent.provenance != runtime._chi
                or runtime._ledger._refs[label] != {runtime._data_owner: 1}
                or type(runtime._buffers[label]) is not bytearray
                or extent.residency != {'reference_payload_bytes': len(runtime._buffers[label]), 'physical_objects': 1}):
            raise ContractError('shared sealing requires the single complete owned CUDA frame')
        size = len(runtime._buffers[label])
        builder = self._begin(runtime, size)
        used = bounded_packed_size(record, byte_limit=min(self.contract.expanded_cap, size-8),
                                   integer_bits=runtime._contract.reference_integer_bits, images=self.images)
        if int.from_bytes(memoryview(runtime._buffers[label])[:8], 'big') != used:
            raise ContractError('CUDA frame length lost its complete original record')
        builder.push(bytes(memoryview(runtime._buffers[label])[:8]))
        for part in _packed_parts(record, runtime._buffers[self.workspaces[3]], self.images):
            builder.push(part)
        # Keep every actual tail byte, including nonzero padding. No zero-tail
        # assumption, prefix trimming or interpretation of old data is used.
        for part in _raw_parts(runtime._buffers[label], 8+used):
            builder.push(part)
        header = builder.finish()
        if header.expanded_bytes != size:
            raise ContractError('shared CUDA frame lost its full admitted extent')
        page_id, scratch_id = self._materialize(runtime, builder)
        self._read(runtime, page_id, _raw_parts(runtime._buffers[label]), size)
        root_id = label+':shared-root-copy'
        root_extent = {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}
        runtime._ledger.allocate(runtime._data_owner, (
            ObjectSpec(root_id, 'shared_cuda_frame_root_copy', root_extent, runtime._chi),))
        runtime._buffers[root_id] = ROOT_MAGIC+archive.U64.pack(header.ordinal)
        self._accept(runtime, page_id)
        # Before publication the full original frame, mutable page, immutable
        # page and new root all coexist with live leases. Failure keeps them.
        releases = self._scratch_releases(runtime, scratch_id)+((runtime._data_owner, root_id, 1),)
        ledger = runtime._ledger.prepare_transfer((), releases)
        # This trusted machine relocation preserves the same semantic label
        # via its exact decoder. The ledger itself attests only accounting.
        ledger._objects[label] = replace(extent, kind=ROOT_KIND+extent.kind, residency=root_extent)
        ledger._check_residency(ledger._objects, ledger._refs)
        ledger._event('reencode_buffer', runtime._data_owner, (label,),
                      note='complete CUDA frame retained through immutable shared bytes')
        buffers = dict(runtime._buffers)
        buffers[label] = buffers.pop(root_id)
        buffers.pop(scratch_id)
        next_root = dict(runtime.__dict__)
        next_root.update(_ledger=ledger, _router=CostRouter(ledger, runtime._contract.work_roles),
            _event_router=CostRouter(ledger, runtime._event_router.snapshot()), _buffers=buffers)
        runtime.__dict__ = next_root


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
