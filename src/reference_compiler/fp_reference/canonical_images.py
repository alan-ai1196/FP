"""Owned encodings of exact immutable builtin subtrees; no device authority.

Only None/bool/int/Fraction/str/bytes and recursively pure exact tuples may
bind an image. Dataclasses (including frozen ones), mappings and lists never
bind: a frozen wrapper does not establish immutable descendants. Every image
has paid immutable bytes and a strong source binding; no checksum proves it.
"""
import codecs
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction as F

from . import encoding
from .core import ContractError
from .resources import ObjectSpec


MIN_IMAGE = 8192
CHUNK = 8192


@dataclass(frozen=True)
class Image:
    source: object
    buffer: str
    size: int
    traversal: int
    depth: int
    integer_bits: int


class _CanonicalImages:
    def __init__(self, runtime, deployment_owner, cap):
        self.runtime, self.deployment_owner, self.cap = runtime, deployment_owner, cap
        self.entries, self.index, self.used = [], {}, 0

    def snapshot(self):
        # The source and byte identity, not a process-local id, are complete
        # state. The strong-id lookup below is a reconstructible acceleration.
        return tuple(self.entries)

    def find(self, value):
        entry = self.index.get(id(value))
        return entry if entry is not None and entry.source is value else None

    def fragments(self, entry):
        raw = self.runtime._buffers[entry.buffer]
        if type(raw) is not bytes or len(raw) != entry.size:
            raise ContractError('canonical image lost its complete immutable owned bytes')
        decoder = codecs.getincrementaldecoder('utf-8')('surrogatepass')
        for offset in range(0, len(raw), CHUNK):
            yield decoder.decode(raw[offset:offset+CHUNK])
        tail = decoder.decode(b'', final=True)
        if tail:
            yield tail

    def _metrics(self, value, memo):
        saved = self.find(value)
        if saved is not None:
            return saved.size, saved.traversal, saved.depth, saved.integer_bits
        previous = memo.get(id(value))
        if previous is not None and previous[0] is value:
            return previous[1]
        kind = type(value)
        if value is None or kind is bool:
            result = encoding.packed_size(value), 1, 0, 0
        elif kind in (str, bytes):
            result = encoding.packed_size(value), 1+len(value)*(2 if kind is bytes else 1), 0, 0
        elif kind in (int, F):
            numbers = (value,) if kind is int else (value.numerator, value.denominator)
            result = (encoding.packed_size(value),
                1+sum(max(1, (n.bit_length()+3)//4) for n in numbers),
                0, max(n.bit_length() for n in numbers))
        elif kind is tuple:
            size, traversal, depth, bits = 12+max(0, len(value)-1), 1, 0, 0
            for child in value:
                part = self._metrics(child, memo)
                if part is None:
                    result = None
                    break
                size += part[0]
                traversal += part[1]
                depth, bits = max(depth, part[2]+1), max(bits, part[3])
            else:
                result = size, traversal, depth, bits
        else:
            result = None
        memo[id(value)] = (value, result)
        return result

    def prepare(self, value, *, role):
        """Called only after the owner pays and bounds the whole value walk.

        Retain maximal eligible subtrees of at least MIN_IMAGE bytes that fit
        the remaining registered capacity. A full cache stops admission; all
        existing entries remain and misses follow the original serializer.
        This policy promises correctness, not optimal cache placement.
        """
        memo = {}
        stack = [value]
        while stack and self.cap-self.used >= MIN_IMAGE:
            item = stack.pop()
            if self.find(item) is not None:
                continue
            metrics = self._metrics(item, memo)
            if metrics is not None:
                if MIN_IMAGE <= metrics[0] <= self.cap-self.used:
                    self._retain(item, metrics, role=role)
                    continue
                if metrics[0] < MIN_IMAGE:
                    continue
            if type(item) in (tuple, list):
                stack.extend(reversed(item))
            elif isinstance(item, Mapping):
                stack.extend(child for pair in reversed(tuple(item.items())) for child in reversed(pair))
            elif is_dataclass(item) and not isinstance(item, type):
                stack.extend(getattr(item, f.name) for f in reversed(fields(item)))

    def _retain(self, value, metrics, *, role):
        rt, size = self.runtime, metrics[0]
        ledger = rt._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
                   +len(ledger._owners)+len(ledger._retired)+len(rt._buffers)+16)
        ledger.charge_work(role, {'work': 64*size+128*entries}, note='owned-canonical-image')
        identity = rt._runtime_id+f':canonical-image:{len(self.entries)}'
        scratch = identity+':copy'
        extent = {'reference_payload_bytes': size, 'physical_objects': 1}
        rt._ledger.allocate(rt._data_owner, (
            ObjectSpec(scratch, 'canonical_image_copy_workspace', extent, rt._chi),))
        rt._buffers[scratch] = bytearray(size)
        rt._ledger.acquire(self.deployment_owner, scratch)
        # No existing image supplies this initial binding. Both traversals
        # use the original trusted encoder, independently of the archive.
        encoding.write_packed(value, rt._buffers[scratch])
        rt._ledger.allocate(rt._data_owner, (
            ObjectSpec(identity, 'immutable_canonical_image', extent, rt._chi),))
        rt._buffers[identity] = bytes(rt._buffers[scratch])
        rt._ledger.acquire(self.deployment_owner, identity)
        offset = 0
        for fragment in encoding.fragments(value, packed=True):
            part = fragment.encode('utf-8', 'surrogatepass')
            if rt._buffers[identity][offset:offset+len(part)] != part:
                raise ContractError('canonical image differs from its immutable source')
            offset += len(part)
        if offset != size:
            raise ContractError('canonical image changed its complete source extent')
        entry = Image(value, identity, *metrics)
        # Both copies stay paid until validation and index publication finish.
        # Any failure is handled by the owning Runtime's terminal boundary.
        self.entries.append(entry)
        self.index[id(value)] = entry
        self.used += size
        rt._ledger.release_many(((rt._data_owner, scratch, 1),
                                 (self.deployment_owner, scratch, 1)))
        rt._buffers.pop(scratch)
