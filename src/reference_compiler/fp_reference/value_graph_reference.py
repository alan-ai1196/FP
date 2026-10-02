"""Private typed-graph owner for the existing complete token Runtime path.

The inward/outward value boundary and trusted persistent record transitions
establish source stability. No public ownership flag, alternate learner port,
certificate, frame shortcut or source supplied by a producer is accepted.
"""
from collections import OrderedDict
from dataclasses import replace

from . import value_graph as graph
from .byte_terms import compose
from .core import ContractError
from .encoding import bounded_packed_size
from .resources import ResourceExceeded
from .shared_reference import (_SharedReference, ROOT_BYTES, ROOT_KIND, ROOT_MAGIC,
                               _compare_stream, _raw_parts)


class _ValueGraphReference(_SharedReference):
    def __init__(self, runtime, contract):
        super().__init__(runtime, contract)
        self.limits = graph.Limits(nodes=contract.expression_nodes,
            bindings=contract.expression_bindings, page_bytes=contract.literal_workspace,
            expanded=contract.expanded_cap, integer_bits=runtime._contract.reference_integer_bits,
            comparisons=contract.comparison_cap, references=contract.reference_cap)
        self.encoder, self.reader = graph.Producer(self.limits), graph.Reader(self.limits)
        self.bindings, self._pending_bindings = OrderedDict(), None

    def snapshot(self):
        return replace(super().snapshot(), expression_bindings=tuple(self.bindings.values()))

    def find(self, value):
        saved = self.bindings.get(id(value))
        if saved is not None and saved[0] is value:
            return graph.Fact(value, saved[1], self.reader.metrics[saved[1]])
        return None if self.images is None else self.images.find(value)

    def _charge(self, runtime, role, label):
        cfg, ledger = self.contract, runtime._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
            +len(ledger._owners)+len(ledger._retired)+len(runtime._buffers)
            +len(runtime.__dict__)+len(self.encoder.index.raw)+len(self.bindings)+len(self.pages)+16)
        work = (128*cfg.expanded_cap+64*cfg.reference_cap+8*cfg.comparison_cap
            +8*(cfg.literal_workspace+cfg.program_workspace)+128*entries)
        if self.images is not None:
            work += 64*cfg.expanded_cap+64*len(self.images.entries)
        ledger.charge_work(role, {'work': work}, note=label+':owned-value-graph')

    def _expression(self, value, walk, frame, size):
        root, _ = walk.value(value)
        if frame is None:
            return root
        # Frame bytes are synthetic copies, not persistent source identities.
        # Binary composition shares repeated raw padding without erasing it.
        prefix = walk.emit(b'b'+bytes(memoryview(frame)[:8]))
        def parts():
            for part in _raw_parts(frame, 8+size):
                yield walk.emit(b'b'+part)
        if 8+size == len(frame):
            tail = walk.emit(b'b')
        else:
            tail = compose(parts(), lambda a, b: walk.emit(graph.vector(b'x', (a, b))))
        return walk.emit(graph.vector(b'v', (prefix, root, tail)))

    def _build(self, runtime, value, size, frame=None):
        builder = self.encoder.begin(runtime._buffers[self.workspaces[0]])
        def emit(raw):
            reply = builder.send(raw)
            if type(reply) is not bytes or len(reply) != 8:
                raise ContractError('graph producer returned a non-byte handle')
            return graph.U64.unpack(reply)[0]
        walk = graph._OwnedWalk(emit, self.bindings, self.limits)
        root = self._expression(value, walk, frame, size)
        builder.finish(graph.U64.pack(root))
        if not graph.HEADER.size <= builder.extent <= self.contract.literal_workspace:
            raise ContractError('graph producer exceeded its complete paid page')
        return self._materialize(runtime, builder)

    def _verify(self, runtime, page_id, value, size, frame=None):
        actual = self.reader.add(runtime._buffers[page_id])
        walk = graph._OwnedWalk(self.reader.find, self.bindings, self.limits)
        expected = self._expression(value, walk, frame, size)
        if actual != expected or self.reader.metrics[actual].size != (size if frame is None else len(frame)):
            raise ContractError('graph differs from the complete owned value')
        if frame is not None:
            _compare_stream(self.reader.decoded(len(self.pages), byte_cap=self.contract.expanded_cap,
                reference_cap=self.contract.reference_cap), _raw_parts(frame), len(frame))
        self._pending_bindings = walk.proposals

    def _accept(self, runtime, page_id):
        if self._pending_bindings is None:
            raise ContractError('graph page has no independent binding')
        self.encoder.accept()
        self.pages.append(page_id)
        # Deterministic FIFO memo, not a semantic state/history deletion.
        # Publish only checked facts after their page. Failure retains the
        # actual prefix and halts before the caller's numerical publication.
        for identity, fact in self._pending_bindings.items():
            if len(self.bindings) >= self.contract.expression_bindings:
                self.bindings.popitem(last=False)
            self.bindings[identity] = fact
        self._pending_bindings = None

    def allocate(self, runtime, owner, planned):
        value, role = planned.value, runtime._ledger._owners[owner]
        self._charge(runtime, role, planned.spec.object_id)
        try:
            size = bounded_packed_size(value, byte_limit=self.contract.expanded_cap,
                integer_bits=runtime._contract.reference_integer_bits, images=self)
            # Graph pages retain complete typed operands directly. No canonical
            # image is created merely to feed this native representation.
            page_id, scratch_id = self._build(runtime, value, size)
            root = replace(planned.spec, kind=ROOT_KIND+planned.spec.kind,
                residency={'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1})
            runtime._ledger.allocate(owner, (root,))
            runtime._buffers[root.object_id] = bytearray(ROOT_BYTES)
            self._verify(runtime, page_id, value, size)
            ordinal = len(self.pages)
            self._accept(runtime, page_id)
            runtime._buffers[root.object_id][:] = ROOT_MAGIC+graph.U64.pack(ordinal)
            runtime._ledger.release_many(self._scratch_releases(runtime, scratch_id))
            runtime._buffers.pop(scratch_id)
        except MemoryError:
            raise
        except Exception as error:
            runtime._halt('owned-value-graph-retention', error)
            raise

    def seal_cuda_frame(self, runtime, label, record, *, role):
        self._charge(runtime, role, label)
        extent, frame = runtime._ledger._objects[label], runtime._buffers[label]
        if (extent.kind != 'owned_cuda_phase_frame' or extent.provenance != runtime._chi
                or runtime._ledger._refs[label] != {runtime._data_owner: 1}
                or type(frame) is not bytearray
                or extent.residency != {'reference_payload_bytes': len(frame), 'physical_objects': 1}):
            raise ContractError('graph sealing requires the complete single owned frame')
        if len(frame) > self.contract.expanded_cap:
            raise ResourceExceeded('graph frame exceeds its complete expansion allowance')
        size = bounded_packed_size(record, byte_limit=min(self.contract.expanded_cap, len(frame)-8),
            integer_bits=runtime._contract.reference_integer_bits, images=self)
        if int.from_bytes(memoryview(frame)[:8], 'big') != size:
            raise ContractError('graph frame lost its complete original body')
        page_id, scratch_id = self._build(runtime, record, size, frame)
        self._verify(runtime, page_id, record, size, frame)
        frame = None
        self._relocate_frame(runtime, label, extent, page_id, scratch_id, len(self.pages))
