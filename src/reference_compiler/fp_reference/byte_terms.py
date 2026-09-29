"""Exact byte-expression pages and trusted canonical traversal.

No Runtime authority. Producer state and the independent reader are disjoint.
The producer receives byte packets and one paid private output workspace only.
Source bindings belong to the trusted owner, never to the producer.
"""
from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass, replace
from fractions import Fraction as F
import struct
import zlib

from . import encoding
from .core import ContractError
from .resources import ResourceExceeded

MAGIC = b'FPDGv1\0\0'
ENCODING_ID = 'complete-canonical-byte-expression-u64-pages-v1'
HEADER = struct.Struct('>8s5Q')
U32, U64 = struct.Struct('>I'), struct.Struct('>Q')
PIECE = 8192
U64_MAX = (1 << 64)-1


@dataclass(frozen=True)
class Limits:
    expanded: int = 128 << 20
    nodes: int = 1 << 20
    page_bytes: int = 64 << 20
    comparisons: int = 1 << 30
    references: int = 1 << 30

    def __post_init__(self):
        if any(type(x) is not int or not 0 < x <= U64_MAX for x in
               (self.expanded, self.nodes, self.page_bytes, self.comparisons, self.references)):
            raise ContractError('positive uint64 term-model allowances required')
        if self.page_bytes < HEADER.size:
            raise ContractError('term page allowance omits its header')


class Index:
    """Derived immutable-term index; a hash only selects literal candidates."""
    def __init__(self, limits):
        # A frozen dataclass still has writable metadata. The producer must
        # not share that wrapper with the independent reader or the owner.
        self.limits = replace(limits)
        self.nodes, self.literal_buckets, self.pairs = [], {}, {}
        self.compared = 0

    def literal(self, raw):
        key = len(raw), zlib.crc32(raw)
        for identity in self.literal_buckets.get(key, ()):
            candidate = self.nodes[identity][1]
            if self.compared+len(raw) > self.limits.comparisons:
                raise ResourceExceeded('term literal comparison allowance exhausted')
            self.compared += len(raw)
            if candidate == raw:
                return identity
        return None

    def pair(self, left, right):
        return self.pairs.get((left, right))

    def add_literal(self, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= PIECE:
            raise ContractError('bounded nonempty immutable term literal required')
        if self.literal(raw) is not None:
            raise ContractError('term dictionary contains a duplicate literal')
        self._room(len(raw))
        identity = len(self.nodes)
        self.nodes.append((0, raw, len(raw), 1))
        self.literal_buckets.setdefault((len(raw), zlib.crc32(raw)), []).append(identity)
        return identity

    def add_pair(self, left, right):
        if any(type(n) is not int or not 0 <= n < len(self.nodes) for n in (left, right)):
            raise ContractError('term children must be defined in the strict prefix')
        if self.pair(left, right) is not None:
            raise ContractError('term dictionary contains a duplicate concatenation')
        size = self.nodes[left][2]+self.nodes[right][2]
        references = self.nodes[left][3]+self.nodes[right][3]
        self._room(size, references)
        identity = len(self.nodes)
        self.nodes.append((1, (left, right), size, references))
        self.pairs[left, right] = identity
        return identity

    def _room(self, size, references=1):
        if (len(self.nodes) >= self.limits.nodes or size > self.limits.expanded
                or references > self.limits.references):
            raise ResourceExceeded('term node, reference or expanded extent allowance exhausted')


class Producer:
    """Byte-message producer using a disjoint admitted page workspace."""
    def __init__(self, limits):
        self.index, self.pages = Index(limits), 0
        self.start, self.pending, self.finished = 0, None, False
        self.used, self.written = 0, False

    def begin(self, workspace):
        if self.pending is not None:
            raise ContractError('term producer already has an unfinished page')
        if self.pages > U64_MAX:
            raise ResourceExceeded('term page ordinal exceeds its format')
        if type(workspace) is not bytearray or len(workspace) != self.index.limits.page_bytes:
            raise ContractError('exact admitted term page workspace required')
        self.start, self.pending, self.finished = len(self.index.nodes), workspace, False
        self.used, self.written = HEADER.size, False
        self.index.compared = 0
        return self

    def send(self, message):
        if type(message) is not bytes or self.pending is None or self.finished:
            raise ContractError('one active byte-message term page required')
        if message[:1] == b'L' and 1 < len(message) <= PIECE+1:
            raw = message[1:]
            identity = self.index.literal(raw)
            if identity is None:
                self._append(b'L'+U32.pack(len(raw))+raw)
                identity = self.index.add_literal(raw)
        elif message[:1] == b'C' and len(message) == 17:
            left, right = struct.unpack('>2Q', message[1:])
            identity = self.index.pair(left, right)
            if identity is None:
                # Bounds/type checks happen before publication into this index.
                if left >= len(self.index.nodes) or right >= len(self.index.nodes):
                    raise ContractError('term producer received an undefined child')
                self._append(message)
                identity = self.index.add_pair(left, right)
        else:
            raise ContractError('unregistered term byte message')
        return U64.pack(identity)

    def _append(self, raw):
        if self.used+len(raw) > len(self.pending):
            raise ResourceExceeded('term page byte allowance exhausted')
        self.pending[self.used:self.used+len(raw)] = raw
        self.used += len(raw)

    def finish(self, root):
        if type(root) is not bytes or len(root) != 8 or self.pending is None or self.finished:
            raise ContractError('one complete opaque term root required')
        identity = U64.unpack(root)[0]
        if identity >= len(self.index.nodes):
            raise ContractError('term root has no definition')
        self.finished = True
        HEADER.pack_into(self.pending, 0, MAGIC, self.pages, self.start,
                         len(self.index.nodes)-self.start, identity, self.index.nodes[identity][2])

    @property
    def extent(self):
        if not self.finished:
            raise ContractError('unfinished term page has no final extent')
        return self.used

    def write(self, output):
        if not self.finished or self.written or type(output) is not bytearray or len(output) != self.used:
            raise ContractError('one exact admitted term page output required')
        output[:] = memoryview(self.pending)[:self.used]
        self.written = True

    def accept(self):
        if not self.finished or not self.written:
            raise ContractError('term producer has no finished page')
        self.pages += 1
        self.pending = None


class Reader:
    """Separate parser/index. Rebuildable from the immutable page bytes alone."""
    def __init__(self, limits):
        self.index, self.pages, self.roots = Index(limits), [], []

    def add(self, raw):
        if type(raw) is not bytes or not HEADER.size <= len(raw) <= self.index.limits.page_bytes:
            raise ContractError('complete bounded immutable term page required')
        magic, ordinal, first, count, root, expanded = HEADER.unpack_from(raw)
        if magic != MAGIC or (ordinal, first) != (len(self.pages), len(self.index.nodes)):
            raise ContractError('term page lost its complete ordered prefix')
        if first+count > self.index.limits.nodes or expanded > self.index.limits.expanded:
            raise ResourceExceeded('term page exceeds its declared allowance')
        self.index.compared = 0
        offset = HEADER.size
        for _ in range(count):
            tag, offset = raw[offset:offset+1], offset+1
            if tag == b'L':
                if offset+4 > len(raw):
                    raise ContractError('truncated term literal extent')
                size = U32.unpack_from(raw, offset)[0]
                offset += 4
                if not 0 < size <= PIECE or offset+size > len(raw):
                    raise ContractError('truncated or oversized term literal')
                self.index.add_literal(raw[offset:offset+size])
                offset += size
            elif tag == b'C':
                if offset+16 > len(raw):
                    raise ContractError('truncated term concatenation')
                self.index.add_pair(*struct.unpack_from('>2Q', raw, offset))
                offset += 16
            else:
                raise ContractError('unregistered term node tag')
        if (offset != len(raw) or root >= len(self.index.nodes)
                or self.index.nodes[root][2] != expanded):
            raise ContractError('term page lost its exact root or complete extent')
        self.pages.append(raw)
        self.roots.append(root)
        return root

    def decoded(self, ordinal, *, byte_cap, reference_cap):
        if (type(ordinal) is not int or not 0 <= ordinal < len(self.roots)
                or type(byte_cap) is not int or byte_cap <= 0
                or type(reference_cap) is not int or reference_cap <= 0):
            raise ContractError('retained term page and positive recovery allowances required')
        root = self.roots[ordinal]
        if self.index.nodes[root][2] > byte_cap or self.index.nodes[root][3] > reference_cap:
            raise ResourceExceeded('term recovery exceeds its complete declared allowances')
        # Each nonempty expanded leaf is a reference occurrence. Bound actual
        # unfolding, not just the number of unique dictionary nodes.
        for count, part in enumerate(self.expand(root), 1):
            if count > reference_cap:
                raise ResourceExceeded('term recovery exceeds its reference allowance')
            yield part

    def expand(self, root):
        if type(root) is not int or not 0 <= root < len(self.index.nodes):
            raise ContractError('retained term root required')
        stack = [root]
        while stack:
            tag, value, _, _ = self.index.nodes[stack.pop()]
            if tag == 0:
                yield value
            else:
                left, right = value
                stack.extend((right, left))

    def literal(self, raw):
        identity = self.index.literal(raw)
        if identity is None:
            raise ContractError('term page omits the complete expected literal')
        return identity

    def pair(self, left, right):
        identity = self.index.pair(left, right)
        if identity is None:
            raise ContractError('term page omits the complete expected concatenation')
        return identity


def compose(parts, pair):
    """Fixed binary carry tree; no empty or identity concatenation nodes."""
    stack = []
    for value in parts:
        count = 1
        while stack and stack[-1][0] == count:
            _, left = stack.pop()
            value, count = pair(left, value), 2*count
        stack.append((count, value))
    if not stack:
        raise ContractError('empty canonical term has no representation')
    result = stack[0][1]
    for _, right in stack[1:]:
        result = pair(result, right)
    return result


class Walk:
    """Trusted owner traversal; only literal bytes and opaque IDs leave it."""
    def __init__(self, literal, pair, bindings, binding_limit=U64_MAX):
        self.literal, self.pair, self.bindings = literal, pair, bindings
        self.binding_limit = binding_limit
        self.proposals, self.active = {}, set()
        self.visits = self.hits = self.literal_bytes = self.pair_calls = 0

    def join(self, parts):
        def counted(left, right):
            self.pair_calls += 1
            return self.pair(left, right)
        return compose(parts, counted)

    def text(self, parts):
        def emitted():
            for part in parts:
                raw = part.encode('utf-8', 'surrogatepass')
                for start in range(0, len(raw), PIECE):
                    piece = raw[start:start+PIECE]
                    self.literal_bytes += len(piece)
                    yield self.literal(piece)
        return self.join(emitted())

    def value(self, value):
        self.visits += 1
        identity = id(value)
        known = self.bindings.get(identity) or self.proposals.get(identity)
        if known is not None and known[0] is value:
            self.hits += 1
            return known[1], True
        if identity in self.active:
            raise ContractError('cyclic complete value has no finite term')
        self.active.add(identity)
        try:
            kind = type(value)
            pure = value is None or kind in (bool, int, F, str, bytes, tuple)
            if value is None or kind in (bool, int, F, str, bytes):
                root = self.text(encoding.fragments(value, packed=True))
            else:
                if kind in (tuple, list):
                    prefix = ('["'+kind.__name__+'",[',)
                    children = encoding._elements(value, ',')
                elif isinstance(value, Mapping):
                    prefix = ('["mapping",[',)
                    children = encoding._members(value, ',', packed=True)
                    pure = False
                elif is_dataclass(value) and not isinstance(value, type):
                    # Metadata and every mutable field are observed afresh.
                    def header():
                        yield '["dataclass",'
                        yield from encoding._string(type(value).__module__)
                        yield ','
                        yield from encoding._string(type(value).__qualname__)
                        yield ',['
                    prefix, children, pure = header(), encoding._fields(value, ','), False
                else:
                    raise ContractError('unsupported packed reference payload')
                def sequence():
                    nonlocal pure
                    yield self.text(prefix)
                    for visit, child in children:
                        if visit:
                            node, eligible = self.value(child)
                            pure = pure and eligible
                            yield node
                        elif child:
                            yield self.text((child,))
                root = self.join(sequence())
            if pure:
                if len(self.bindings)+len(self.proposals) >= self.binding_limit:
                    raise ResourceExceeded('complete source-binding allowance exhausted')
                self.proposals[identity] = value, root
            return root, pure
        finally:
            self.active.remove(identity)
