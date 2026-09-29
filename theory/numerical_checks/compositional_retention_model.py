"""Bounded research model of compositional canonical-byte retention.

Not used by ReferenceCompilerRuntime. No resource ownership, phase, bridge,
search, persistence or installation authority. The producer receives byte
messages only; the owner and separate reader retain all checking authority.
"""
from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass
from fractions import Fraction as F
import struct
import zlib

from fp_reference import encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded

MAGIC = b'FPDGv1\0\0'
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

    def __post_init__(self):
        if any(type(x) is not int or not 0 < x <= U64_MAX for x in
               (self.expanded, self.nodes, self.page_bytes, self.comparisons)):
            raise ContractError('positive uint64 term-model allowances required')
        if self.page_bytes < HEADER.size:
            raise ContractError('term page allowance omits its header')


class Index:
    """Derived immutable-term index; a hash only selects literal candidates."""
    def __init__(self, limits):
        self.limits = limits
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
        self.nodes.append((0, raw, len(raw)))
        self.literal_buckets.setdefault((len(raw), zlib.crc32(raw)), []).append(identity)
        return identity

    def add_pair(self, left, right):
        if any(type(n) is not int or not 0 <= n < len(self.nodes) for n in (left, right)):
            raise ContractError('term children must be defined in the strict prefix')
        if self.pair(left, right) is not None:
            raise ContractError('term dictionary contains a duplicate concatenation')
        size = self.nodes[left][2]+self.nodes[right][2]
        self._room(size)
        identity = len(self.nodes)
        self.nodes.append((1, (left, right), size))
        self.pairs[left, right] = identity
        return identity

    def _room(self, size):
        if len(self.nodes) >= self.limits.nodes or size > self.limits.expanded:
            raise ResourceExceeded('term node or expanded extent allowance exhausted')


class Producer:
    """Byte-message producer. Never receives a source, iterator or owner."""
    def __init__(self, limits):
        self.index, self.pages = Index(limits), 0
        self.start, self.pending, self.finished = 0, None, False

    def begin(self):
        if self.pending is not None:
            raise ContractError('term producer already has an unfinished page')
        if self.pages > U64_MAX:
            raise ResourceExceeded('term page ordinal exceeds its format')
        self.start, self.pending, self.finished = len(self.index.nodes), bytearray(), False
        self.index.compared = 0

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
        if HEADER.size+len(self.pending)+len(raw) > self.index.limits.page_bytes:
            raise ResourceExceeded('term page byte allowance exhausted')
        self.pending.extend(raw)

    def finish(self, root):
        if type(root) is not bytes or len(root) != 8 or self.pending is None or self.finished:
            raise ContractError('one complete opaque term root required')
        identity = U64.unpack(root)[0]
        if identity >= len(self.index.nodes):
            raise ContractError('term root has no definition')
        self.finished = True
        return HEADER.pack(MAGIC, self.pages, self.start, len(self.index.nodes)-self.start,
                           identity, self.index.nodes[identity][2])+bytes(self.pending)

    def accept(self):
        if not self.finished:
            raise ContractError('term producer has no finished page')
        self.pages += 1
        self.pending = None


class Reader:
    """Separate parser/index. Rebuildable from the immutable page bytes alone."""
    def __init__(self, limits):
        self.index, self.pages = Index(limits), []

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
        return root

    def expand(self, root):
        if type(root) is not int or not 0 <= root < len(self.index.nodes):
            raise ContractError('retained term root required')
        stack = [root]
        while stack:
            tag, value, _ = self.index.nodes[stack.pop()]
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
    def __init__(self, literal, pair, bindings):
        self.literal, self.pair, self.bindings = literal, pair, bindings
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
                self.proposals[identity] = value, root
            return root, pure
        finally:
            self.active.remove(identity)


class Owner:
    """Passive model only. Its limits are not a Runtime ledger or host bound."""
    def __init__(self, limits=Limits()):
        self.limits = limits
        self.producer, self.reader = Producer(limits), Reader(limits)
        self.bindings, self.roots, self.failed = {}, (), False
        self.diagnostic = None
        self.statistics = ()

    def retain(self, value):
        if self.failed:
            raise ContractError('failed term owner cannot continue')
        try:
            # Keep the original complete guard. This model does not claim
            # to remove its field/occurrence work or its refusal decisions.
            size = encoding.bounded_packed_size(value, byte_limit=self.limits.expanded)
            self.producer.begin()
            before = len(self.reader.index.nodes)
            def handle(message):
                result = self.producer.send(message)
                if type(result) is not bytes or len(result) != 8:
                    raise ContractError('producer returned a non-byte opaque node handle')
                return U64.unpack(result)[0]
            emit = Walk(lambda raw: handle(b'L'+raw),
                lambda a, b: handle(b'C'+U64.pack(a)+U64.pack(b)), self.bindings)
            proposed, _ = emit.value(value)
            raw = self.producer.finish(U64.pack(proposed))
            self.diagnostic = raw
            root = self.reader.add(raw)
            # Neither producer handles nor its index supply this expectation.
            check = Walk(self.reader.literal, self.reader.pair, self.bindings)
            expected, _ = check.value(value)
            if root != expected or self.reader.index.nodes[root][2] != size:
                raise ContractError('term root differs from the complete owned record')
            updated = dict(self.bindings)
            updated.update(check.proposals)
            roots = self.roots+(root,)
            row = dict(expanded=size, page_bytes=len(raw), new_nodes=len(self.reader.index.nodes)-before,
                value_visits=check.visits, immutable_binding_hits=check.hits,
                expected_literal_bytes=check.literal_bytes, expected_pair_checks=check.pair_calls)
            next_state = dict(self.__dict__, bindings=updated, roots=roots,
                              statistics=self.statistics+(row,))
            self.producer.accept()
            # All accepted bindings come from the independent expected walk.
            self.__dict__ = next_state
            return root
        except Exception:
            self.failed = True
            raise

    def snapshot(self):
        # Source values here belong to the recursively immutable exact algebra.
        # No mutable index/entry wrapper is exported to a caller.
        return tuple(self.reader.pages), self.roots, tuple(self.bindings.values())
