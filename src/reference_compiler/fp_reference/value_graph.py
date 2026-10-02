"""Typed value pages with independent parsing and private owner traversal.

These components issue no execution, resource or certificate authority.
Only the private Runtime owner may use _OwnedWalk's record-stability premise.
Producers receive byte messages and one admitted output workspace only.
"""
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from fractions import Fraction as F
import struct
import zlib

from . import encoding
from .core import ContractError
from .resources import ResourceExceeded
from .token_values import CapturedTokenValues

MAGIC = b'FPVGv1\0\0'
ENCODING_ID = 'complete-owned-typed-value-graph-u64-pages-v1'
HEADER = struct.Struct('>8s4Q')
U64 = struct.Struct('>Q')
WORD = struct.Struct('<I')
ATOMS = (bool, int, F, str, bytes)
U64_MAX = (1 << 64)-1


@dataclass(frozen=True)
class Limits:
    nodes: int = 1 << 22
    bindings: int = 1 << 20
    page_bytes: int = 128 << 20
    expanded: int = 128 << 20
    depth: int = 64
    integer_bits: int = 32768
    comparisons: int = 1 << 30
    references: int = 1 << 30

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


class _Index:
    """Only full equality binds a node; comparison bytes have a page cap."""
    def __init__(self, limits):
        self.limits = replace(limits)
        self.raw, self.buckets, self.compared = [], {}, 0

    def find(self, raw):
        for identity in self.buckets.get((len(raw), zlib.crc32(raw)), ()):
            if self.compared+len(raw) > self.limits.comparisons:
                raise ResourceExceeded('graph exact-comparison allowance exhausted')
            self.compared += len(raw)
            if self.raw[identity] == raw:
                return identity
        return None

    def add(self, raw):
        if len(self.raw) >= self.limits.nodes:
            raise ResourceExceeded('graph node allowance exhausted')
        identity = len(self.raw)
        self.raw.append(raw)
        self.buckets.setdefault((len(raw), zlib.crc32(raw)), []).append(identity)
        return identity


class Producer:
    """No source objects, source bindings, expected roots or reader handles."""
    def __init__(self, limits):
        self.limits = replace(limits)
        self.index = _Index(limits)
        self.ordinal = self.first = self.used = 0
        self.pending, self.finished, self.written = None, False, False

    def begin(self, workspace):
        if (self.pending is not None or type(workspace) is not bytearray
                or len(workspace) != self.limits.page_bytes or self.ordinal > U64_MAX):
            raise ContractError('one complete admitted graph workspace required')
        self.first, self.used = len(self.index.raw), HEADER.size
        self.pending, self.finished, self.written = workspace, False, False
        self.index.compared = 0
        return self

    def send(self, raw):
        if type(raw) is not bytes or not raw or self.pending is None or self.finished:
            raise ContractError('nonempty immutable node message required')
        old = self.index.find(raw)
        if old is not None:
            return U64.pack(old)
        if len(self.index.raw) >= self.limits.nodes or self.used+8+len(raw) > self.limits.page_bytes:
            raise ResourceExceeded('graph producer node/page allowance exhausted')
        U64.pack_into(self.pending, self.used, len(raw))
        self.pending[self.used+8:self.used+8+len(raw)] = raw
        self.used += 8+len(raw)
        return U64.pack(self.index.add(raw))

    def finish(self, root):
        if (self.pending is None or self.finished or type(root) is not bytes or len(root) != 8
                or U64.unpack(root)[0] >= len(self.index.raw)):
            raise ContractError('one complete graph root required')
        HEADER.pack_into(self.pending, 0, MAGIC, self.ordinal, self.first,
                         len(self.index.raw)-self.first, U64.unpack(root)[0])
        self.finished = True

    @property
    def extent(self):
        if not self.finished:
            raise ContractError('unfinished graph page')
        return self.used

    def write(self, output):
        if (not self.finished or self.written or type(output) is not bytearray
                or len(output) != self.used):
            raise ContractError('one exact admitted graph output required')
        output[:] = memoryview(self.pending)[:self.used]
        self.written = True

    def accept(self):
        if not self.finished or not self.written:
            raise ContractError('graph producer has no complete written page')
        self.ordinal += 1
        self.pending = None


class Reader:
    """Rebuilt solely from pages; exact byte-key equality, no digest authority."""
    def __init__(self, limits):
        self.limits = replace(limits)
        self.index = _Index(limits)
        self.nodes, self.metrics, self.references, self.pages, self.roots = [], [], [], [], []
        self.semantic_work = 0

    def find(self, raw):
        identity = self.index.find(raw)
        if identity is None:
            raise ContractError('page omits the independently expected node')
        return identity

    def _atomic(self, raw):
        tag, data = raw[:1], raw[1:]
        digits = (self.limits.integer_bits+3)//4
        if tag == b'i' and len(data) > digits+1 or tag == b'q' and len(data) > 2*digits+3:
            raise ResourceExceeded('graph integer syntax exceeds its bit allowance')
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

    def captured_values(self, children, *, operands=None):
        data, width, past, grid, tail = self.capture(children) if operands is None else operands
        for token in past:
            for channel in range(width):
                yield F(WORD.unpack_from(data, 4*(token*width+channel))[0], grid)
        yield from tail

    def _parse(self, raw):
        tag = raw[:1]
        if tag in (b'n', b't', b'f', b'i', b'q', b's', b'b'):
            value = self._atomic(raw)
            return (tag, value), scalar_metrics(value)
        if tag not in (b'u', b'l', b'm', b'd', b'c', b'x', b'v') or (len(raw)-1) % 8:
            raise ContractError('unregistered graph node or truncated child')
        children = tuple(x[0] for x in struct.iter_unpack('>Q', raw[1:]))
        if any(child >= len(self.nodes) for child in children):
            raise ContractError('graph child is not in the strict prefix')
        if tag not in (b'x', b'v') and any(self.nodes[child][0] in (b'x', b'v') for child in children):
            raise ContractError('raw/frame nodes are not typed value children')
        metrics = [self.metrics[child] for child in children]
        if tag == b'x':
            if len(children) != 2:
                raise ContractError('raw concatenation needs exactly two children')
            size = sum(self.raw_size(child) for child in children)
            return (tag, children), Metrics(size, size, 0, 0)
        if tag == b'v':
            if (len(children) != 3 or self.nodes[children[0]][0] != b'b'
                    or self.nodes[children[1]][0] in (b'x', b'v')):
                raise ContractError('complete frame prefix/body/tail required')
            prefix = self.nodes[children[0]][1]
            body = metrics[1]
            if len(prefix) != 8 or int.from_bytes(prefix, 'big') != body.size:
                raise ContractError('frame prefix differs from complete body extent')
            size = 8+body.size+self.raw_size(children[2])
            return (tag, children), Metrics(size, size, body.depth, body.integer_bits)
        if tag in (b'u', b'l'):
            size = (12 if tag == b'u' else 11)+max(0, len(children)-1)+sum(x.size for x in metrics)
        elif tag == b'm':
            if len(children) % 2:
                raise ContractError('mapping lost a key/value member')
            size = 14+3*(len(children)//2)+max(0, len(children)//2-1)+sum(x.size for x in metrics)
        elif tag == b'd':
            if len(children) < 3:
                raise ContractError('record lost its type or field names')
            if (any(self.nodes[child][0] != b's' for child in children[:2])
                    or self.nodes[children[2]][0] != b'u'):
                raise ContractError('record field schema differs from its values')
            names = self.nodes[children[2]][1]
            if len(names) != len(children)-3 or any(self.nodes[n][0] != b's' for n in names):
                raise ContractError('record field schema differs from its values')
            # Reuse derived scalar sizes; an unused record cannot make us
            # rescan a huge prior module/name string for every tiny definition.
            metrics = [self.metrics[child] for child in children[:2]]
            metrics += [m for field, child in zip(names, children[3:])
                        for m in (self.metrics[field], self.metrics[child])]
            size = 18+sum(self.metrics[child].size-8 for child in children[:2])+max(0, len(names)-1)
            size += sum(3+self.metrics[field].size-8+self.metrics[child].size
                        for field, child in zip(names, children[3:]))
        else:
            # Only input rationals are decoded from exact captured operands.
            # Every executed node result is an explicit retained tail value.
            self._semantic_debit(sum(self.references[child] for child in children))
            operands = self.capture(children)
            _, width, past, _, tail = operands
            self._semantic_debit(width*len(past)+len(tail))
            metrics = [scalar_metrics(value) for value in self.captured_values(children, operands=operands)]
            size = 12+max(0, len(metrics)-1)+sum(x.size for x in metrics)
        return (tag, children), aggregate(size, metrics)

    def _semantic_debit(self, count):
        if self.semantic_work+count > self.limits.references:
            raise ResourceExceeded('graph page semantic traversal allowance exhausted')
        self.semantic_work += count

    def raw_size(self, identity):
        tag, value = self.nodes[identity]
        if tag == b'b':
            return len(value)
        if tag == b'x':
            return self.metrics[identity].size
        raise ContractError('raw byte child required')

    def raw_parts(self, identity):
        stack = [identity]
        while stack:
            tag, value = self.nodes[stack.pop()]
            if tag == b'b':
                yield value
            elif tag == b'x':
                stack.extend(reversed(value))
            else:
                raise ContractError('raw byte child required')

    def add(self, page):
        if type(page) is not bytes or not HEADER.size <= len(page) <= self.limits.page_bytes:
            raise ContractError('complete bounded graph page required')
        magic, ordinal, first, count, root = HEADER.unpack_from(page)
        if magic != MAGIC or (ordinal, first) != (len(self.pages), len(self.nodes)):
            raise ContractError('graph page lost its ordered prefix')
        if first+count > self.limits.nodes:
            raise ResourceExceeded('graph reader node allowance exhausted')
        offset = HEADER.size
        self.index.compared = 0
        self.semantic_work = 0
        for _ in range(count):
            if offset+8 > len(page):
                raise ContractError('truncated graph node extent')
            size = U64.unpack_from(page, offset)[0]
            offset += 8
            if not size or offset+size > len(page):
                raise ContractError('truncated graph node')
            raw, offset = page[offset:offset+size], offset+size
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
                # Operand shape/type checks above already establish flat
                # tuples and an integer width; no second operand expansion.
                width = self.nodes[payload[1]][1]
                references += width*len(self.nodes[payload[2]][1])+len(self.nodes[payload[4]][1])
            if references > self.limits.references:
                raise ResourceExceeded('graph unfolded-reference allowance exhausted')
            self.index.add(raw)
            self.nodes.append(value)
            self.metrics.append(metrics)
            self.references.append(references)
        if offset != len(page) or root >= len(self.nodes):
            raise ContractError('graph page lost its root or exact extent')
        self.pages.append(page)
        self.roots.append(root)
        return root

    def expanded(self, root, *, byte_cap, visit_cap):
        if (type(root) is not int or not 0 <= root < len(self.nodes)
                or any(type(n) is not int or n <= 0 for n in (byte_cap, visit_cap))):
            raise ContractError('retained graph root required')
        if self.metrics[root].size > byte_cap or self.references[root] > visit_cap:
            raise ResourceExceeded('complete graph recovery byte allowance exhausted')
        visits = 0
        def visit(identity):
            nonlocal visits
            visits += 1
            if visits > visit_cap:
                raise ResourceExceeded('complete graph recovery visit allowance exhausted')
            tag, value = self.nodes[identity]
            if tag == b'x':
                for raw in self.raw_parts(identity):
                    yield raw
                return
            if tag == b'v':
                yield self.nodes[value[0]][1]
                yield from visit(value[1])
                yield from self.raw_parts(value[2])
                return
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
                children = self.captured_values(value) if tag == b'c' else value
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
        yield from (part if type(part) is bytes else part.encode('utf-8', 'surrogatepass') for part in visit(root))

    def decoded(self, ordinal, *, byte_cap, reference_cap):
        if type(ordinal) is not int or not 0 <= ordinal < len(self.roots):
            raise ContractError('retained graph page required')
        yield from self.expanded(self.roots[ordinal], byte_cap=byte_cap, visit_cap=reference_cap)


class _OwnedWalk:
    """Private Runtime traversal; no caller-supplied ownership assertion."""
    def __init__(self, emit, bindings, limits):
        self.emit, self.bindings, self.limits = emit, bindings, limits
        self.proposals, self.active = {}, set()

    def value(self, value, *, bind_source=True):
        identity, kind = id(value), type(value)
        known = self.bindings.get(identity) or self.proposals.get(identity)
        if known is not None and known[0] is value:
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
                if len(value)+1 > self.limits.page_bytes:
                    raise ResourceExceeded('graph byte operand exceeds its node allowance')
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
                    pure = bool(kind.__module__.startswith('fp_reference.')
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
                raw, bind = vector(tag, children), pure
            root = self.emit(raw)
            if bind and bind_source:
                # A full memo changes work, never the structural expression.
                # Persistent and transient memos each have this declared cap.
                if len(self.proposals) < self.limits.bindings:
                    self.proposals[identity] = value, root
            return root, pure
        finally:
            self.active.remove(identity)
