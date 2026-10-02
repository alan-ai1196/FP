"""Passive typed-value DAG model; no Runtime, ledger or device authority.

``owned_records=True`` is a theorem premise, NOT an ownership certificate:
the caller must establish that supported private records cannot change under
legal continuations. The default never binds record wrappers. Only bytes go
to the producer; the reader and expected-source walk have independent state.
"""
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from fractions import Fraction as F
import struct

from fp_reference import encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.token_values import CapturedTokenValues

MAGIC = b'FPVGm1\0\0'
HEADER = struct.Struct('>8s4Q')
U64 = struct.Struct('>Q')
WORD = struct.Struct('<I')
ATOMS = (bool, int, F, str, bytes)


@dataclass(frozen=True)
class Limits:
    nodes: int = 1 << 22
    bindings: int = 1 << 20
    page_bytes: int = 128 << 20
    expanded: int = 128 << 20
    depth: int = 64
    integer_bits: int = 32768

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not int or
               not 0 < getattr(self, f.name) < 1 << 64 for f in fields(self)):
            raise ContractError('positive bounded graph-model allowances required')


@dataclass(frozen=True)
class Metrics:
    size: int
    traversal: int
    depth: int
    integer_bits: int


@dataclass(frozen=True)
class Fact:
    source: object
    root: int
    metrics: Metrics

    # The existing canonical guard accepts exactly these derived coordinates.
    @property
    def size(self): return self.metrics.size
    @property
    def traversal(self): return self.metrics.traversal
    @property
    def depth(self): return self.metrics.depth
    @property
    def integer_bits(self): return self.metrics.integer_bits


def scalar_metrics(value):
    kind = type(value)
    if value is None or kind is bool:
        return Metrics(encoding.packed_size(value), 1, 0, 0)
    if kind in (bytes, str):
        return Metrics(encoding.packed_size(value), 1+len(value)*(2 if kind is bytes else 1), 0, 0)
    numbers = (value,) if kind is int else (value.numerator, value.denominator)
    return Metrics(encoding.packed_size(value),
        1+sum(max(1, (n.bit_length()+3)//4) for n in numbers),
        0, max(n.bit_length() for n in numbers))


def aggregate(size, children):
    children = tuple(children)
    return Metrics(size, 1+sum(x.traversal for x in children),
        max((1+x.depth for x in children), default=0),
        max((x.integer_bits for x in children), default=0))


def vector(tag, values):
    return tag+b''.join(U64.pack(value) for value in values)


class Producer:
    """No source objects, source bindings, expected roots or reader handles."""
    def __init__(self, limits):
        self.limits = replace(limits)
        self.nodes, self.index = [], {}
        self.ordinal = self.first = self.used = 0

    def begin(self):
        self.first, self.used = len(self.nodes), HEADER.size

    def send(self, raw):
        if type(raw) is not bytes or not raw:
            raise ContractError('nonempty immutable node message required')
        old = self.index.get(raw)
        if old is not None:
            return U64.pack(old)
        if len(self.nodes) >= self.limits.nodes or self.used+8+len(raw) > self.limits.page_bytes:
            raise ResourceExceeded('graph producer node/page allowance exhausted')
        identity = len(self.nodes)
        self.nodes.append(raw)
        self.index[raw] = identity
        self.used += 8+len(raw)
        return U64.pack(identity)

    def finish(self, root):
        return HEADER.pack(MAGIC, self.ordinal, self.first, len(self.nodes)-self.first, root)+b''.join(
            U64.pack(len(raw))+raw for raw in self.nodes[self.first:])

    def accept(self):
        self.ordinal += 1


class Reader:
    """Rebuilt solely from pages; exact byte-key equality, no digest authority."""
    def __init__(self, limits):
        self.limits = replace(limits)
        self.nodes, self.index, self.metrics, self.pages, self.roots = [], {}, [], [], []
        self.counts = Counter()

    def find(self, raw):
        try:
            return self.index[raw]
        except KeyError as error:
            raise ContractError('page omits the independently expected node') from error

    def _atomic(self, raw):
        tag, data = raw[:1], raw[1:]
        if tag in (b'n', b't', b'f') and not data:
            return {b'n': None, b't': True, b'f': False}[tag]
        if tag == b'i':
            value = int(data, 16)
            if format(value, 'x').encode() == data:
                return value
        if tag == b'q':
            a, b = data.split(b'/')
            value = F(int(a, 16), int(b, 16))
            if (format(value.numerator, 'x')+'/'+format(value.denominator, 'x')).encode() == data:
                return value
        if tag == b's':
            value = data.decode('utf-8', 'surrogatepass')
            if value.encode('utf-8', 'surrogatepass') == data:
                return value
        if tag == b'b':
            return data
        raise ContractError('noncanonical graph atom')

    def _primitive(self, identity):
        tag, value = self.nodes[identity]
        if tag == b'u':
            return tuple(self._primitive(child) for child in value)
        if tag in (b'n', b't', b'f', b'i', b'q', b's', b'b'):
            return value
        raise ContractError('capture requires exact scalar/tuple operands')

    def capture(self, children):
        if len(children) != 5:
            raise ContractError('capture lost one of its five operands')
        data, width, past, grid, tail = (self._primitive(child) for child in children)
        if (type(data) is not bytes or type(width) is not int or width <= 0
                or not data or len(data) % (4*width) or type(past) is not tuple
                or type(grid) is not int or not 0 < grid <= 1 << 32 or grid & (grid-1)
                or type(tail) is not tuple or any(type(x) is not F for x in tail)
                or any(type(x) is not int or not 0 <= x < len(data)//(4*width) for x in past)):
            raise ContractError('invalid immutable capture operands')
        return data, width, past, grid, tail

    def captured_values(self, children, *, recovering=False):
        data, width, past, grid, tail = self.capture(children)
        for token in past:
            for channel in range(width):
                self.counts['recovery_input_words' if recovering else 'metric_input_words'] += 1
                yield F(WORD.unpack_from(data, 4*(token*width+channel))[0], grid)
        yield from tail

    def _parse(self, raw):
        tag = raw[:1]
        if tag in (b'n', b't', b'f', b'i', b'q', b's', b'b'):
            value = self._atomic(raw)
            return (tag, value), scalar_metrics(value)
        if tag not in (b'u', b'l', b'm', b'd', b'c') or (len(raw)-1) % 8:
            raise ContractError('unregistered graph node or truncated child')
        children = tuple(x[0] for x in struct.iter_unpack('>Q', raw[1:]))
        if any(child >= len(self.nodes) for child in children):
            raise ContractError('graph child is not in the strict prefix')
        metrics = [self.metrics[child] for child in children]
        if tag in (b'u', b'l'):
            size = (12 if tag == b'u' else 11)+max(0, len(children)-1)+sum(x.size for x in metrics)
        elif tag == b'm':
            if len(children) % 2:
                raise ContractError('mapping lost a key/value member')
            size = 14+3*(len(children)//2)+max(0, len(children)//2-1)+sum(x.size for x in metrics)
        elif tag == b'd':
            if len(children) < 3:
                raise ContractError('record lost its type or field names')
            module, name, names = (self._primitive(child) for child in children[:3])
            if (type(module) is not str or type(name) is not str or type(names) is not tuple
                    or any(type(x) is not str for x in names) or len(names) != len(children)-3):
                raise ContractError('record field schema differs from its values')
            metrics = [scalar_metrics(module), scalar_metrics(name)]
            metrics += [m for field, child in zip(names, children[3:])
                        for m in (scalar_metrics(field), self.metrics[child])]
            size = 18+encoding._string_size(module)+encoding._string_size(name)+max(0, len(names)-1)
            size += sum(3+encoding._string_size(field)+self.metrics[child].size
                        for field, child in zip(names, children[3:]))
        else:
            # Only input rationals are decoded from exact captured operands.
            # Every executed node result is an explicit retained tail value.
            metrics = [scalar_metrics(value) for value in self.captured_values(children)]
            size = 12+max(0, len(metrics)-1)+sum(x.size for x in metrics)
        return (tag, children), aggregate(size, metrics)

    def add(self, page):
        if type(page) is not bytes or not HEADER.size <= len(page) <= self.limits.page_bytes:
            raise ContractError('complete bounded graph page required')
        magic, ordinal, first, count, root = HEADER.unpack_from(page)
        if magic != MAGIC or (ordinal, first) != (len(self.pages), len(self.nodes)):
            raise ContractError('graph page lost its ordered prefix')
        if first+count > self.limits.nodes:
            raise ResourceExceeded('graph reader node allowance exhausted')
        offset = HEADER.size
        for _ in range(count):
            if offset+8 > len(page):
                raise ContractError('truncated graph node extent')
            size = U64.unpack_from(page, offset)[0]
            offset += 8
            if not size or offset+size > len(page):
                raise ContractError('truncated graph node')
            raw, offset = page[offset:offset+size], offset+size
            if raw in self.index:
                raise ContractError('duplicate graph definition')
            try:
                value, metrics = self._parse(raw)
            except (ValueError, ZeroDivisionError, UnicodeError) as error:
                raise ContractError('invalid graph scalar') from error
            if (max(metrics.size, metrics.traversal) > self.limits.expanded
                    or metrics.depth > self.limits.depth or metrics.integer_bits > self.limits.integer_bits):
                raise ResourceExceeded('graph node exceeds its complete canonical guard')
            self.index[raw] = len(self.nodes)
            self.nodes.append(value)
            self.metrics.append(metrics)
            self.counts['node_payload_bytes_parsed'] += size
        if offset != len(page) or root >= len(self.nodes):
            raise ContractError('graph page lost its root or exact extent')
        self.pages.append(page)
        self.roots.append(root)
        return root

    def expanded(self, root, *, byte_cap, visit_cap):
        if type(root) is not int or not 0 <= root < len(self.nodes):
            raise ContractError('retained graph root required')
        if self.metrics[root].size > byte_cap:
            raise ResourceExceeded('complete graph recovery byte allowance exhausted')
        visits = 0
        def visit(identity):
            nonlocal visits
            visits += 1
            if visits > visit_cap:
                raise ResourceExceeded('complete graph recovery visit allowance exhausted')
            tag, value = self.nodes[identity]
            if tag in (b'n', b't', b'f', b'i', b'q', b's', b'b'):
                yield from encoding.fragments(value, packed=True)
                return
            if tag == b'd':
                module, name, names = (self._primitive(child) for child in value[:3])
                yield '["dataclass",'
                yield from encoding._string(module)
                yield ','
                yield from encoding._string(name)
                yield ',['
                for i, (field, child) in enumerate(zip(names, value[3:])):
                    yield '[' if not i else ',['
                    yield from encoding._string(field)
                    yield ','
                    yield from visit(child)
                    yield ']'
            elif tag == b'm':
                yield '["mapping",['
                for i in range(0, len(value), 2):
                    yield '[' if not i else ',['
                    yield from visit(value[i])
                    yield ','
                    yield from visit(value[i+1])
                    yield ']'
            else:
                yield '["'+('list' if tag == b'l' else 'tuple')+'",['
                children = self.captured_values(value, recovering=True) if tag == b'c' else value
                for i, child in enumerate(children):
                    if i:
                        yield ','
                    if tag == b'c':
                        visits += 1
                        if visits > visit_cap:
                            raise ResourceExceeded('complete graph recovery visit allowance exhausted')
                        yield from encoding.fragments(child, packed=True)
                    else:
                        yield from visit(child)
            yield ']]'
        yield from (part.encode('utf-8', 'surrogatepass') for part in visit(root))


class Walk:
    def __init__(self, emit, bindings, limits, owned_records):
        self.emit, self.bindings, self.limits, self.owned_records = emit, bindings, limits, owned_records
        self.proposals, self.active, self.counts = {}, set(), Counter()

    def value(self, value, *, bind_source=True):
        self.counts['source_visits'] += 1
        identity, kind = id(value), type(value)
        known = self.bindings.get(identity) or self.proposals.get(identity)
        if known is not None and known[0] is value:
            self.counts['source_hits'] += 1
            return known[1], True
        if identity in self.active:
            raise ContractError('cyclic graph source')
        self.active.add(identity)
        try:
            bind = False
            pure = value is None or kind in ATOMS
            if value is None:
                raw = b'n'
            elif kind is bool:
                raw = b't' if value else b'f'
            elif kind is int:
                raw = b'i'+format(value, 'x').encode()
            elif kind is F:
                raw = b'q'+(format(value.numerator, 'x')+'/'+format(value.denominator, 'x')).encode()
            elif kind is str:
                raw = b's'+value.encode('utf-8', 'surrogatepass')
            elif kind is bytes:
                raw, bind = b'b'+value, True
            else:
                if kind is CapturedTokenValues:
                    tag, values, pure = b'c', value.validate(), True
                elif kind in (tuple, list):
                    tag, values, pure = (b'u' if kind is tuple else b'l'), value, kind is tuple
                elif isinstance(value, Mapping):
                    keys = sorted(value, key=lambda k: ''.join(encoding.fragments(k, packed=True)))
                    tag, values, pure = b'm', (child for key in keys for child in (key, value[key])), False
                elif is_dataclass(value) and not isinstance(value, type):
                    declared = fields(value)
                    names = tuple(f.name for f in declared)
                    tag = b'd'
                    values = (kind.__module__, kind.__qualname__, names)+tuple(getattr(value, f) for f in names)
                    pure = bool(self.owned_records and kind.__module__.startswith('fp_reference.')
                        and kind.__dataclass_params__.frozen and hasattr(value, '__dict__')
                        and set(vars(value)) == set(names))
                else:
                    raise ContractError('unsupported complete graph source')
                children = []
                for position, child in enumerate(values):
                    # Field-name tuples are generated syntax, not additional
                    # persistent source identities belonging to the owner.
                    node, eligible = self.value(child, bind_source=not (tag == b'd' and position == 2))
                    children.append(node)
                    pure = pure and eligible
                self.counts['source_child_edges'] += len(children)
                raw, bind = vector(tag, children), pure
            self.counts['node_message_bytes'] += len(raw)
            root = self.emit(raw)
            if bind and bind_source:
                if len(self.bindings)+len(self.proposals) >= self.limits.bindings:
                    raise ResourceExceeded('graph source-binding allowance exhausted')
                self.proposals[identity] = value, root
            return root, pure
        finally:
            self.active.remove(identity)


class Owner:
    def __init__(self, limits=Limits(), *, owned_records=False):
        self.limits, self.owned_records = replace(limits), owned_records
        self.producer, self.reader = Producer(limits), Reader(limits)
        self.bindings, self.roots, self.counts = {}, [], Counter()
        self.failed = False

    def retain(self, value):
        if self.failed:
            raise ContractError('failed graph model cannot continue')
        try:
            self.producer.begin()
            def emit(raw):
                reply = self.producer.send(raw)
                if type(reply) is not bytes or len(reply) != 8:
                    raise ContractError('invalid graph producer byte handle')
                return U64.unpack(reply)[0]
            proposed = Walk(emit, self.bindings, self.limits, self.owned_records)
            root, _ = proposed.value(value)
            actual = self.reader.add(self.producer.finish(root))
            expected = Walk(self.reader.find, self.bindings, self.limits, self.owned_records)
            wanted, _ = expected.value(value)
            if actual != wanted:
                raise ContractError('graph root differs from the complete expected value')
            # Prefix publication, with no copy of prior roots or bindings.
            # All failures are terminal; this is not a rollback guarantee.
            self.producer.accept()
            self.roots.append(actual)
            self.bindings.update(expected.proposals)
            self.counts.update(expected.counts)
            self.counts['root_appends'] += 1
            self.counts['binding_inserts'] += len(expected.proposals)
            return actual
        except Exception:
            self.failed = True
            raise

    def find(self, value):
        known = self.bindings.get(id(value))
        if known is not None and known[0] is value:
            return Fact(value, known[1], self.reader.metrics[known[1]])
        return None
