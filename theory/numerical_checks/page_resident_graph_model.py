"""Passive page-resident realization of the existing typed graph grammar.

No production selection, corpus access or whole-Runtime host-fit claim. The
eager parser is the grammar oracle; complete immutable pages are authoritative.
Offsets, open-address indices and checked metrics are separately derived.
"""
from collections.abc import Sequence
from contextvars import ContextVar
from dataclasses import replace
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'src/reference_compiler'))
from fp_reference import value_graph as eager
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.value_graph_reference import _ValueGraphReference

BLOCK = 4096
Q = struct.Struct('<Q')


def metadata_work(contract):
    # Both indices: bounded probes include locator/table accesses, exact
    # comparisons and a possible table rebuild/zero-fill. Lookup bytes and
    # block allocation are funded before the page producer is invoked.
    return (256*contract.comparison_cap+8*contract.reference_cap
        +32*contract.literal_workspace+104*BLOCK)


class Rows:
    """Append-only fixed-width rows; old blocks never move or gain aliases."""
    def __init__(self, width):
        self.width = width
        self.row = struct.Struct('<'+'Q'*width)
        self.blocks, self.count = [], 0

    def __len__(self):
        return self.count

    def __getitem__(self, key):
        if type(key) is not int or not 0 <= key < self.count:
            raise IndexError(key)
        return self.row.unpack_from(self.blocks[key//BLOCK], key%BLOCK*self.row.size)

    def append(self, *values):
        if len(values) != self.width or any(
                type(x) is not int or not 0 <= x <= eager.U64_MAX for x in values):
            raise ContractError('bounded complete uint64 row required')
        # Pack/allocate before making a new row visible. Old rows survive
        # failures; a subsequently halted owner retains the paid prefix.
        encoded = self.row.pack(*values)
        if self.count%BLOCK == 0:
            self.blocks.append(bytearray(BLOCK*self.row.size))
        offset = self.count%BLOCK*self.row.size
        self.blocks[-1][offset:offset+self.row.size] = encoded
        self.count += 1

    @property
    def capacity_bytes(self):
        return len(self.blocks)*BLOCK*self.row.size


class Raw(Sequence):
    def __init__(self, index):
        self.index = index

    def __len__(self):
        return len(self.index.rows)

    def __getitem__(self, key):
        if type(key) is slice:
            return [self[i] for i in range(*key.indices(len(self)))]
        return bytes(self.index.view(key))

    def __eq__(self, other):
        return len(self) == len(other) and all(a == b for a, b in zip(self, other))


class Index:
    def __init__(self, limits):
        self.limits = replace(limits)
        self.rows, self.raw = Rows(4), Raw(self)
        self.pages, self.pending = [], None
        self.table = bytearray(16*8)
        self.compared = self.probes = 0
        self.peak_table_bytes = len(self.table)

    def _probe(self):
        if self.probes >= self.limits.comparisons:
            raise ResourceExceeded('page-resident index probe allowance exhausted')
        self.probes += 1

    def view(self, identity):
        page, offset, size, _ = self.rows[identity]
        data = self.pending if page == len(self.pages) else self.pages[page]
        if data is None or offset+size > len(data):
            raise ContractError('graph locator lost its complete page')
        return memoryview(data)[offset:offset+size]

    def _slot(self, crc, table):
        mask = len(table)//8-1
        # Multiplication distributes low-bit patterns. CRC never authorizes
        # equality: matching entries still compare all actual page bytes.
        return (crc*0x9e3779b97f4a7c15) & mask

    def find(self, raw):
        crc = eager.zlib.crc32(raw)
        slot, mask = self._slot(crc, self.table), len(self.table)//8-1
        while True:
            self._probe()
            entry = Q.unpack_from(self.table, slot*8)[0]
            if not entry:
                return None
            identity = entry-1
            _, _, size, saved = self.rows[identity]
            if saved == crc and size == len(raw):
                if self.compared+size > self.limits.comparisons:
                    raise ResourceExceeded('graph exact-comparison allowance exhausted')
                self.compared += size
                if self.view(identity) == raw:
                    return identity
            slot = (slot+1)&mask

    def _insert(self, identity, crc, table):
        slot, mask = self._slot(crc, table), len(table)//8-1
        while True:
            self._probe()
            if not Q.unpack_from(table, slot*8)[0]:
                Q.pack_into(table, slot*8, identity+1)
                return
            slot = (slot+1)&mask

    def add(self, raw, offset):
        if len(self.rows) >= self.limits.nodes:
            raise ResourceExceeded('graph node allowance exhausted')
        if self.pending is None or memoryview(self.pending)[offset:offset+len(raw)] != raw:
            raise ContractError('new locator differs from its actual complete bytes')
        if 2*(len(self.rows)+1) > len(self.table)//8:
            before = self.table
            table = bytearray(2*len(before))
            self.peak_table_bytes = max(self.peak_table_bytes, len(before)+len(table))
            for identity in range(len(self.rows)):
                self._insert(identity, self.rows[identity][3], table)
            self.table = table
        identity, crc = len(self.rows), eager.zlib.crc32(raw)
        self.rows.append(len(self.pages), offset, len(raw), crc)
        self._insert(identity, crc, self.table)
        return identity

    def accept(self, page):
        if type(page) is not bytes or self.pending is None:
            raise ContractError('complete immutable accepted page required')
        self.pages.append(page)
        self.pending = None


class Producer(eager.Producer):
    def __init__(self, limits):
        super().__init__(limits)
        self.index = Index(limits)

    def begin(self, workspace):
        super().begin(workspace)
        self.index.pending = workspace
        self.index.probes = 0
        return self

    def send(self, raw):
        if type(raw) is not bytes or not raw or self.pending is None or self.finished:
            raise ContractError('nonempty immutable node message required')
        old = self.index.find(raw)
        if old is not None:
            return eager.U64.pack(old)
        if len(self.index.raw) >= self.limits.nodes or self.used+8+len(raw) > self.limits.page_bytes:
            raise ResourceExceeded('graph producer node/page allowance exhausted')
        eager.U64.pack_into(self.pending, self.used, len(raw))
        offset = self.used+8
        self.pending[offset:offset+len(raw)] = raw
        self.used = offset+len(raw)
        return eager.U64.pack(self.index.add(raw, offset))

    def accept(self, page):
        if (not self.finished or not self.written or type(page) is not bytes
                or len(page) != self.used or memoryview(self.pending)[:self.used] != page):
            raise ContractError('actual immutable page differs from the written producer page')
        self.index.accept(page)
        super().accept()


class Column(Sequence):
    def __init__(self, rows, metric):
        self.rows, self.metric = rows, metric

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, key):
        row = self.rows[key]
        return eager.Metrics(*row[:4]) if self.metric else row[4]

    def __eq__(self, other):
        return len(self) == len(other) and all(a == b for a, b in zip(self, other))


class Node(Sequence):
    """A field projection: asking for a tag does not decode its value."""
    __slots__ = ('reader', 'identity')

    def __init__(self, reader, identity):
        self.reader, self.identity = reader, identity

    def __len__(self):
        return 2

    def __getitem__(self, field):
        if type(field) is not int or field not in (0, 1):
            raise IndexError(field)
        raw = self.reader.index.view(self.identity)
        self.reader._lookup_debit(1 if field == 0 else len(raw))
        tag = bytes(raw[:1])
        if field == 0:
            return tag
        if tag in (b'n', b't', b'f', b'i', b'q', b's', b'b'):
            return self.reader._atomic(bytes(raw))
        return tuple(x[0] for x in struct.iter_unpack('>Q', raw[1:]))

    def __eq__(self, other):
        if type(other) not in (tuple, Node):
            return NotImplemented
        return tuple(self) == tuple(other)


class Nodes(Sequence):
    def __init__(self, reader):
        self.reader = reader

    def __len__(self):
        return len(self.reader.checked)

    def __getitem__(self, key):
        if type(key) is not int or not 0 <= key < len(self):
            raise IndexError(key)
        return Node(self.reader, key)

    def __eq__(self, other):
        return len(self) == len(other) and all(a == b for a, b in zip(self, other))


class Reader(eager.Reader):
    def __init__(self, limits):
        super().__init__(limits)
        self.index, self.checked = Index(limits), Rows(5)
        self.nodes = Nodes(self)
        self.metrics, self.references = Column(self.checked, True), Column(self.checked, False)
        self.lookup_work, self.lookup_cap = 0, limits.references
        self._recovery = ContextVar('page-resident-recovery', default=None)

    def _lookup_debit(self, count):
        meter = self._recovery.get()
        if meter is not None:
            if meter[0]+count > meter[1]:
                raise ResourceExceeded('page-resident recovery reconstruction allowance exhausted')
            meter[0] += count
            return
        if self.lookup_work+count > self.lookup_cap:
            raise ResourceExceeded('page-resident reconstruction allowance exhausted')
        self.lookup_work += count

    def add(self, page):
        if self.index.pending is not None:
            raise ContractError('page-resident reader already has a failed pending page')
        if type(page) is not bytes or not eager.HEADER.size <= len(page) <= self.limits.page_bytes:
            raise ContractError('complete bounded graph page required')
        magic, ordinal, first, count, root = eager.HEADER.unpack_from(page)
        if magic != eager.MAGIC or (ordinal, first) != (len(self.pages), len(self.nodes)):
            raise ContractError('graph page lost its ordered prefix')
        if first+count > self.limits.nodes:
            raise ResourceExceeded('graph reader node allowance exhausted')
        self.index.pending = page
        self.index.compared = self.index.probes = self.semantic_work = self.lookup_work = 0
        self.lookup_cap = self.limits.references
        offset = eager.HEADER.size
        for _ in range(count):
            if offset+8 > len(page):
                raise ContractError('truncated graph node extent')
            size = eager.U64.unpack_from(page, offset)[0]
            offset += 8
            if not size or offset+size > len(page):
                raise ContractError('truncated graph node')
            raw = page[offset:offset+size]
            if self.index.find(raw) is not None:
                raise ContractError('duplicate graph definition')
            try:
                value, metrics = self._parse(raw)
            except ResourceExceeded:
                raise
            except (ValueError, ZeroDivisionError, UnicodeError) as error:
                raise ContractError('invalid graph scalar') from error
            if (max(metrics.size, metrics.traversal) > self.limits.expanded
                    or metrics.depth > self.limits.depth or metrics.integer_bits > self.limits.integer_bits):
                raise ResourceExceeded('graph node exceeds its complete canonical guard')
            tag, payload = value
            references = 1
            if tag in (b'u', b'l', b'm', b'd', b'c', b'x', b'v'):
                references += sum(self.references[child] for child in payload)
            if tag == b'c':
                width = self.nodes[payload[1]][1]
                references += width*len(self.nodes[payload[2]][1])+len(self.nodes[payload[4]][1])
            if references > self.limits.references:
                raise ResourceExceeded('graph unfolded-reference allowance exhausted')
            self.index.add(raw, offset)
            self.checked.append(metrics.size, metrics.traversal, metrics.depth, metrics.integer_bits, references)
            offset += size
        if offset != len(page) or root >= len(self.nodes):
            raise ContractError('graph page lost its root or exact extent')
        self.index.accept(page)
        self.pages.append(page)
        self.roots.append(root)
        return root

    def expanded(self, root, *, byte_cap, visit_cap):
        if any(type(n) is not int or n <= 0 for n in (byte_cap, visit_cap)):
            raise ContractError('positive recovery allowances required')
        # A suspended generator must not leave an ambient allowance installed.
        # Context-local activation also separates simultaneous reader threads.
        meter = [0, byte_cap+visit_cap]
        iterator = super().expanded(root, byte_cap=byte_cap, visit_cap=visit_cap)
        try:
            while True:
                token = self._recovery.set(meter)
                try:
                    try:
                        piece = next(iterator)
                    except StopIteration:
                        return
                finally:
                    self._recovery.reset(token)
                yield piece
        finally:
            token = self._recovery.set(meter)
            try:
                iterator.close()
            finally:
                self._recovery.reset(token)


class Owner(_ValueGraphReference):
    """Audit-only substitution at the existing private owner boundary."""
    def __init__(self, runtime, contract):
        super().__init__(runtime, contract)
        self.encoder, self.reader = Producer(self.limits), Reader(self.limits)

    def _charge(self, runtime, role, label):
        cfg, ledger = self.contract, runtime._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
            +len(ledger._owners)+len(ledger._retired)+len(runtime._buffers)
            +len(runtime.__dict__)+len(self.encoder.index.raw)+len(self.bindings)+len(self.pages)+16)
        work = (128*cfg.expanded_cap+64*cfg.reference_cap+8*cfg.comparison_cap
            +8*(cfg.literal_workspace+cfg.program_workspace)+128*entries)
        if self.images is not None:
            work += 64*cfg.expanded_cap+64*len(self.images.entries)
        ledger.charge_work(role, {'work': work+metadata_work(cfg)}, note=label+':owned-value-graph')

    def _accept(self, runtime, page_id):
        if self._pending_bindings is None:
            raise ContractError('graph page has no independent binding')
        self.encoder.accept(runtime._buffers[page_id])
        self.pages.append(page_id)
        for identity, fact in self._pending_bindings.items():
            if len(self.bindings) >= self.contract.expression_bindings:
                self.bindings.popitem(last=False)
            self.bindings[identity] = fact
        self._pending_bindings = None


def resident_payload(owner):
    """Exact committed capacities of compact tables; pages counted once."""
    encoder, reader = owner.encoder, owner.reader
    assert encoder.index.pages == reader.index.pages
    assert all(a is b for a, b in zip(encoder.index.pages, reader.index.pages))
    return dict(nodes=len(reader.nodes), pages=len(reader.pages),
        immutable_page_bytes=sum(map(len, reader.pages)),
        locator_capacity_bytes=encoder.index.rows.capacity_bytes+reader.index.rows.capacity_bytes,
        metric_capacity_bytes=reader.checked.capacity_bytes,
        hash_capacity_bytes=len(encoder.index.table)+len(reader.index.table),
        largest_index_growth_pair=max(encoder.index.peak_table_bytes, reader.index.peak_table_bytes),
        retained_raw_node_copies=0, retained_parsed_value_objects=0)
