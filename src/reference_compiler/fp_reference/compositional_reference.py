"""Private complete byte-expression retention for the existing token owner.

All physical execution, fresh reads, original phase writing and learner
publication remain in Runtime. Full frames still compare every actual byte.
"""
from dataclasses import replace

from . import byte_terms as terms
from .core import ContractError
from .encoding import bounded_packed_size
from .resources import ResourceExceeded
from .shared_reference import (_SharedReference, ROOT_BYTES, ROOT_KIND, ROOT_MAGIC,
                               _compare_stream, _raw_parts)


class _CompositionalReference(_SharedReference):
    def __init__(self, runtime, contract):
        # Retain the existing admitted workspaces in both roles. Only the
        # literal workspace is used by the term producer; no credit is claimed
        # for the other workspaces or optional canonical images.
        super().__init__(runtime, contract)
        limits = terms.Limits(expanded=contract.expanded_cap, nodes=contract.expression_nodes,
            page_bytes=contract.literal_workspace, comparisons=contract.comparison_cap,
            references=contract.reference_cap)
        self.encoder, self.reader = terms.Producer(limits), terms.Reader(limits)
        self.bindings, self._pending_bindings = {}, None

    def snapshot(self):
        return replace(super().snapshot(), expression_bindings=tuple(self.bindings.values()))

    def _charge(self, runtime, role, label):
        cfg, ledger = self.contract, runtime._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
            +len(ledger._owners)+len(ledger._retired)+len(runtime._buffers)
            +len(runtime.__dict__)+len(self.encoder.index.nodes)+len(self.bindings)+len(self.pages)+16)
        # Primitive traversal/map/copy tariff; not a bit-time, Python-heap or
        # worst-case hash-table theorem. Actual host/job limits remain binding.
        work = (128*cfg.expanded_cap+64*cfg.reference_cap+8*cfg.comparison_cap
            +8*(cfg.literal_workspace+cfg.program_workspace)+128*entries)
        if self.images is not None:
            work += 64*cfg.expanded_cap+64*len(self.images.entries)
        ledger.charge_work(role, {'work': work}, note=label+':compositional-reference')

    def _expression(self, value, walk, frame, size):
        body, _ = walk.value(value)
        if frame is None:
            return body
        # The owner alone reads this frame. Every actual padding byte remains,
        # including nonzero padding; the producer receives immutable copies.
        def parts():
            yield walk.literal(bytes(memoryview(frame)[:8]))
            yield body
            for raw in _raw_parts(frame, 8+size):
                yield walk.literal(raw)
        return walk.join(parts())

    def _build(self, runtime, value, size, frame=None):
        builder = self.encoder.begin(runtime._buffers[self.workspaces[0]])
        def handle(message):
            result = builder.send(message)
            if type(result) is not bytes or len(result) != 8:
                raise ContractError('term producer returned a non-byte handle')
            return terms.U64.unpack(result)[0]
        walk = terms.Walk(lambda raw: handle(b'L'+raw),
            lambda a, b: handle(b'C'+terms.U64.pack(a)+terms.U64.pack(b)), self.bindings,
            self.contract.expression_bindings)
        root = self._expression(value, walk, frame, size)
        builder.finish(terms.U64.pack(root))
        if not terms.HEADER.size <= builder.extent <= self.contract.literal_workspace:
            raise ContractError('term producer exceeded its complete paid page')
        return self._materialize(runtime, builder)

    def _verify(self, runtime, page_id, value, size, frame=None):
        actual = self.reader.add(runtime._buffers[page_id])
        walk = terms.Walk(self.reader.literal, self.reader.pair, self.bindings,
                          self.contract.expression_bindings)
        expected = self._expression(value, walk, frame, size)
        if (actual != expected or self.reader.index.nodes[actual][2] !=
                (size if frame is None else len(frame))):
            raise ContractError('retained expression differs from the complete owned record')
        if frame is not None:
            # Structural binding proves the record expression. A separate full
            # comparison still binds it to the actual original phase frame.
            _compare_stream(self.reader.decoded(len(self.pages), byte_cap=self.contract.expanded_cap,
                reference_cap=self.contract.reference_cap), _raw_parts(frame), len(frame))
        bindings = dict(self.bindings)
        bindings.update(walk.proposals)
        self._pending_bindings = bindings

    def _accept(self, runtime, page_id):
        if self._pending_bindings is None:
            raise ContractError('term page has no independently checked binding')
        updated = dict(self.__dict__, pages=self.pages+[page_id],
                       bindings=self._pending_bindings, _pending_bindings=None)
        self.encoder.accept()
        self.__dict__ = updated

    def allocate(self, runtime, owner, planned):
        role, value = runtime._ledger._owners[owner], planned.value
        self._charge(runtime, role, planned.spec.object_id)
        try:
            size = bounded_packed_size(value, byte_limit=self.contract.expanded_cap,
                integer_bits=runtime._contract.reference_integer_bits, images=self.images)
            if self.images is not None:
                self.images.prepare(value, role=role)
            page_id, scratch_id = self._build(runtime, value, size)
            root = replace(planned.spec, kind=ROOT_KIND+planned.spec.kind,
                residency={'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1})
            runtime._ledger.allocate(owner, (root,))
            runtime._buffers[root.object_id] = bytearray(ROOT_BYTES)
            self._verify(runtime, page_id, value, size)
            ordinal = len(self.pages)
            self._accept(runtime, page_id)
            runtime._buffers[root.object_id][:] = ROOT_MAGIC+terms.U64.pack(ordinal)
            runtime._ledger.release_many(self._scratch_releases(runtime, scratch_id))
            runtime._buffers.pop(scratch_id)
        except MemoryError:
            raise
        except Exception as error:
            runtime._halt('compositional-reference-retention', error)
            raise

    def seal_cuda_frame(self, runtime, label, record, *, role):
        self._charge(runtime, role, label)
        extent, frame = runtime._ledger._objects[label], runtime._buffers[label]
        if (extent.kind != 'owned_cuda_phase_frame' or extent.provenance != runtime._chi
                or runtime._ledger._refs[label] != {runtime._data_owner: 1}
                or type(frame) is not bytearray
                or extent.residency != {'reference_payload_bytes': len(frame), 'physical_objects': 1}):
            raise ContractError('term sealing requires the single complete owned CUDA frame')
        if len(frame) > self.contract.expanded_cap:
            raise ResourceExceeded('term frame exceeds its complete expansion allowance')
        size = bounded_packed_size(record, byte_limit=min(self.contract.expanded_cap, len(frame)-8),
            integer_bits=runtime._contract.reference_integer_bits, images=self.images)
        if int.from_bytes(memoryview(frame)[:8], 'big') != size:
            raise ContractError('term frame length lost its complete original record')
        page_id, scratch_id = self._build(runtime, record, size, frame)
        self._verify(runtime, page_id, record, size, frame)
        # Drop our mutable alias before the existing paid atomic relocation.
        frame = None
        self._relocate_frame(runtime, label, extent, page_id, scratch_id, len(self.pages))
