"""Lossless shared byte pages. No value, resource, or execution authority.

The producer accepts immutable byte pieces only. A separate reader expands
each page's ordered piece references to exactly its original byte stream.
Piece equality, never a checksum alone, permits sharing. Every page contains
its new literal pieces as well as its own independently compressed reference
sequence. Earlier pages remain indispensable data, not an external cache.

Workspaces and output buffers belong to the caller. These helpers neither
allocate a retained output nor decide that any Runtime object may be freed.
"""
from dataclasses import dataclass
import struct
import zlib

from .core import ContractError
from .resources import ResourceExceeded
from . import phase_deflate


ENCODING_ID = 'shared-immutable-byte-pieces-u64-pages-v1+'+phase_deflate.ENCODING_ID
PIECE_LIMIT = 8192
HEADER = struct.Struct('>8s7Q')
MAGIC = b'FPBPv1\0\0'
U32, U64 = struct.Struct('>I'), struct.Struct('>Q')


def _positive(value, label):
    if type(value) is not int or value <= 0:
        raise ContractError('positive '+label+' required')


def _workspace(value):
    if type(value) is not bytearray or not value:
        raise ContractError('complete caller-owned mutable byte workspace required')
    return value


@dataclass(frozen=True)
class Page:
    ordinal: int
    first_piece: int
    pieces: int
    expanded_bytes: int
    references: int
    literal_bytes: int
    program_bytes: int


def _page(raw):
    if type(raw) is not bytes or len(raw) < HEADER.size:
        raise ContractError('complete immutable archive page required')
    magic, *values = HEADER.unpack_from(raw)
    if magic != MAGIC:
        raise ContractError('unregistered archive page header')
    result = Page(*values)
    if (len(raw) != HEADER.size+result.literal_bytes+result.program_bytes
            or result.pieces > result.literal_bytes//5 or not result.program_bytes
            or (result.references == 0) != (result.expanded_bytes == 0)
            or not result.references <= result.expanded_bytes <= PIECE_LIMIT*result.references):
        raise ContractError('inconsistent archive page extent')
    return result


def _literals(raw, page):
    offset, end = HEADER.size, HEADER.size+page.literal_bytes
    for _ in range(page.pieces):
        if offset+U32.size > end:
            raise ContractError('truncated archive literal header')
        size = U32.unpack_from(raw, offset)[0]
        offset += U32.size
        if not 0 < size <= PIECE_LIMIT or offset+size > end:
            raise ContractError('truncated or oversized archive literal')
        yield offset, size
        offset += size
    if offset != end:
        raise ContractError('archive literal table has trailing bytes')


class Reader:
    """Independent byte decoder; rebuilding it requires only retained pages.

    This index is a derived acceleration structure. Page bytes define every
    coordinate. A caller must still compare the decoded stream with its own
    expected bytes before treating a newly produced page as correct evidence.
    """
    def __init__(self):
        self._pages, self._headers, self._pieces = [], [], []

    def add(self, raw):
        header = _page(raw)
        if (header.ordinal, header.first_piece) != (len(self._pages), len(self._pieces)):
            raise ContractError('archive pages must retain their complete original order')
        entries = tuple(_literals(raw, header))
        # Input is immutable; no view of a producer's workspace is retained.
        self._pages.append(raw)
        self._headers.append(header)
        self._pieces.extend((header.ordinal, offset, size) for offset, size in entries)
        return header

    def decoded(self, ordinal, *, byte_cap, reference_cap):
        _positive(byte_cap, 'archive expansion allowance')
        _positive(reference_cap, 'archive reference allowance')
        if type(ordinal) is not int or not 0 <= ordinal < len(self._pages):
            raise ContractError('an actually retained archive page is required')
        page, raw = self._headers[ordinal], self._pages[ordinal]
        if page.expanded_bytes > byte_cap or page.references > reference_cap:
            raise ResourceExceeded('archive expansion exceeds its admitted allowance')
        size, count, partial = 0, 0, b''
        start = HEADER.size+page.literal_bytes
        for block in phase_deflate.decoded_fragments(memoryview(raw)[start:],
                expanded_cap=max(1, U64.size*page.references)):
            block = partial+block
            end = len(block)//U64.size*U64.size
            for offset in range(0, end, U64.size):
                identity = U64.unpack_from(block, offset)[0]
                # A later page must never retroactively define an old piece.
                if identity >= page.first_piece+page.pieces:
                    raise ContractError('archive reference uses undefined future data')
                source, position, length = self._pieces[identity]
                size += length
                count += 1
                if size > page.expanded_bytes or count > page.references:
                    raise ContractError('archive program exceeds its declared complete stream')
                yield memoryview(self._pages[source])[position:position+length]
            partial = block[end:]
        if partial or (size, count) != (page.expanded_bytes, page.references):
            raise ContractError('archive program omits part of its complete stream')


class Encoder:
    """Producer-side exact interning; a checksum is only a lookup bucket.

    This object receives no reference values, expected-output iterators,
    Runtime root, evidence authority, or decoder index. Accepted page bytes
    may be shared; its index is independent of Reader's index.
    """
    def __init__(self):
        self._pages, self._pieces, self._index = [], [], {}
        self._active = None

    def add(self, raw):
        if self._active is not None and not self._active._written:
            raise ContractError('archive page must finish its single owned write first')
        header = _page(raw)
        if (header.ordinal, header.first_piece) != (len(self._pages), len(self._pieces)):
            raise ContractError('encoder lost the immutable archive prefix')
        entries = tuple(_literals(raw, header))
        self._pages.append(raw)
        for offset, size in entries:
            identity = len(self._pieces)
            piece = memoryview(raw)[offset:offset+size]
            self._pieces.append((header.ordinal, offset, size))
            self._index.setdefault((size, zlib.crc32(piece)), []).append(identity)
        self._active = None

    def begin(self, literals, program, references, *, byte_cap, reference_cap, comparison_cap=None):
        if self._active is not None:
            raise ContractError('archive has an unfinished or unaccepted page')
        result = Builder(self, literals, program, references,
                         byte_cap=byte_cap, reference_cap=reference_cap,
                         comparison_cap=4*byte_cap if comparison_cap is None else comparison_cap)
        self._active = result
        return result


class Builder:
    """One unaccepted page written only inside three admitted workspaces."""
    def __init__(self, encoder, literals, program, references, *, byte_cap, reference_cap, comparison_cap):
        if type(encoder) is not Encoder:
            raise ContractError('closed byte archive encoder required')
        _positive(byte_cap, 'archive input allowance')
        _positive(reference_cap, 'archive reference allowance')
        _positive(comparison_cap, 'archive exact-comparison allowance')
        self._literals, self._program, self._refs = map(_workspace, (literals, program, references))
        if (len({id(v) for v in (literals, program, references)}) != 3
                or len(references) != phase_deflate.BLOCK or len(literals) < HEADER.size):
            raise ContractError('three disjoint complete archive workspaces required')
        self._encoder, self._stream = encoder, phase_deflate.new_encoder()
        self._page_count, self._first_piece = len(encoder._pages), len(encoder._pieces)
        self._local, self._new = {}, []
        self._literal_end, self._program_end, self._ref_end = HEADER.size, 0, 0
        self._bytes, self._count = 0, 0
        self._byte_cap, self._reference_cap = byte_cap, reference_cap
        self._comparison_cap, self.comparison_bytes = comparison_cap, 0
        self._finished = False
        self._written = False

    def _compare(self, left, right):
        if self.comparison_bytes+len(right) > self._comparison_cap:
            raise ResourceExceeded('archive exact-comparison allowance exhausted')
        self.comparison_bytes += len(right)
        return left == right

    def _append_program(self, part):
        if type(part) is not bytes:
            raise ContractError('byte-only archive compressor returned another type')
        end = self._program_end+len(part)
        if end > len(self._program):
            raise ResourceExceeded('archive reference program exceeded its paid workspace')
        self._program[self._program_end:end] = part
        self._program_end = end

    def _flush_refs(self):
        if self._ref_end:
            self._append_program(self._stream.compress(bytes(memoryview(self._refs)[:self._ref_end])))
            self._ref_end = 0

    def push(self, part):
        if self._finished or type(part) is not bytes or not 0 < len(part) <= PIECE_LIMIT:
            raise ContractError('bounded immutable archive byte piece required')
        if (len(self._encoder._pages), len(self._encoder._pieces)) != (self._page_count, self._first_piece):
            raise ContractError('serialized archive writer lost its original prefix')
        if self._bytes+len(part) > self._byte_cap or self._count+1 > self._reference_cap:
            raise ResourceExceeded('archive input exceeds its prepaid allowance')
        key = (len(part), zlib.crc32(part))
        identity = None
        for candidate in self._encoder._index.get(key, ()):
            page, offset, size = self._encoder._pieces[candidate]
            if self._compare(memoryview(self._encoder._pages[page])[offset:offset+size], part):
                identity = candidate
                break
        if identity is None:
            for candidate in self._local.get(key, ()):
                offset, size = self._new[candidate]
                if self._compare(memoryview(self._literals)[offset:offset+size], part):
                    identity = self._first_piece+candidate
                    break
        if identity is None:
            end = self._literal_end+U32.size+len(part)
            if end > len(self._literals):
                raise ResourceExceeded('archive literals exceed their paid workspace')
            candidate = len(self._new)
            U32.pack_into(self._literals, self._literal_end, len(part))
            self._literals[self._literal_end+U32.size:end] = part
            self._new.append((self._literal_end+U32.size, len(part)))
            self._local.setdefault(key, []).append(candidate)
            self._literal_end = end
            identity = self._first_piece+candidate
        if self._ref_end == len(self._refs):
            self._flush_refs()
        U64.pack_into(self._refs, self._ref_end, identity)
        self._ref_end += U64.size
        self._bytes += len(part)
        self._count += 1

    def finish(self):
        if self._finished:
            raise ContractError('archive page already finished')
        self._flush_refs()
        self._append_program(self._stream.finish())
        header = Page(self._page_count, self._first_piece, len(self._new), self._bytes,
                      self._count, self._literal_end-HEADER.size, self._program_end)
        HEADER.pack_into(self._literals, 0, MAGIC, *vars(header).values())
        self._finished = True
        return header

    @property
    def extent(self):
        if not self._finished:
            raise ContractError('unfinished archive page has no final extent')
        return self._literal_end+self._program_end

    def write(self, output):
        if (self._written or self._encoder._active is not self
                or type(output) is not bytearray or len(output) != self.extent):
            raise ContractError('exact admitted archive output extent required')
        output[:self._literal_end] = memoryview(self._literals)[:self._literal_end]
        output[self._literal_end:] = memoryview(self._program)[:self._program_end]
        self._written = True


def byte_pieces(fragment):
    """Trusted owner-side splitting, before the byte-only producer boundary."""
    if type(fragment) is not bytes:
        raise ContractError('immutable serialized bytes required')
    for start in range(0, len(fragment), PIECE_LIMIT):
        yield fragment[start:start+PIECE_LIMIT]
