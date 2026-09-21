"""Lossless typed phase coding; these helpers provide no Runtime authority.

The independent reader reconstructs the existing packed JSON byte stream.
Strings are interned by exact code-point equality. No native coordinate,
field, integer, plan node, operation word or source identity is projected.
"""
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction
from math import gcd

from .core import ContractError
from .resources import ResourceExceeded
from .encoding import fragments, packed_size

ENCODING_ID = 'typed-phase-varints-interned-strings-short-sequences-v1'
MAX_STRINGS, MAX_DEPTH, INTEGER_BITS = 4096, 64, 32768
EXPANDED_CAP = 128 << 20


@dataclass(frozen=True)
class PhaseExtent:
    encoded_bytes: int
    expanded_bytes: int
    string_definitions: int


def _uint(value):
    while value >= 128:
        yield bytes(((value & 127) | 128,))
        value >>= 7
    yield bytes((value,))


def _guard(value, *, expanded_cap):
    charged = 0
    def debit(amount):
        nonlocal charged
        charged += amount
        if charged > expanded_cap:
            raise ResourceExceeded('phase encoding traversal allowance exhausted')
    def walk(value, depth):
        debit(1)
        if depth > MAX_DEPTH:
            raise ResourceExceeded('phase encoding traversal allowance exhausted')
        if value is None or type(value) is bool:
            return
        if type(value) is str:
            # Count every occurrence, including repeated/internable strings.
            # A per-string limit alone would allow unbounded aggregate work
            # in the legacy size traversal before noticing the expansion cap.
            debit(len(value))
            return
        if type(value) is int or type(value) is Fraction:
            numbers = (value,) if type(value) is int else (value.numerator,value.denominator)
            if any(abs(n).bit_length() > INTEGER_BITS for n in numbers):
                raise ResourceExceeded('phase integer exceeds its encoding bit allowance')
            debit(sum(max(1,(abs(n).bit_length()+3)//4) for n in numbers))
            return
        if type(value) in (tuple,list):
            children = iter(value)
        elif isinstance(value,Mapping):
            children = (child for pair in value.items() for child in pair)
        elif is_dataclass(value) and not isinstance(value,type):
            walk(type(value).__module__,depth+1)
            walk(type(value).__qualname__,depth+1)
            children = (child for f in fields(value) for child in (f.name,getattr(value,f.name)))
        else:
            raise ContractError('unsupported typed phase coordinate')
        for child in children:
            walk(child,depth+1)
    walk(value,0)


def _chunks(value, strings, depth=0):
    if depth > MAX_DEPTH:
        raise ResourceExceeded('phase encoding depth allowance exhausted')
    if value is None or type(value) is bool:
        yield bytes((0 if value is None else 2 if value else 1,))
    elif type(value) is int:
        yield b'\x03'
        yield from _uint(2*value if value >= 0 else -2*value-1)
    elif type(value) is Fraction:
        yield b'\x04'
        n = value.numerator
        yield from _uint(2*n if n >= 0 else -2*n-1)
        yield from _uint(value.denominator)
    elif type(value) is str:
        if value in strings:
            yield b'\x06'
            yield from _uint(strings[value])
        else:
            if len(strings) >= MAX_STRINGS:
                raise ResourceExceeded('phase string table allowance exhausted')
            strings[value] = len(strings)
            yield b'\x05'
            size = sum(1 if ord(c)<128 else 2 if ord(c)<2048 else 3 if ord(c)<65536 else 4 for c in value)
            yield from _uint(size)
            for start in range(0,len(value),256):
                yield value[start:start+256].encode('utf-8','surrogatepass')
    elif type(value) in (tuple,list):
        if len(value) < 16:
            yield bytes(((0x20 if type(value) is tuple else 0x30)+len(value),))
        else:
            yield b'\x09' if type(value) is tuple else b'\x0a'
            yield from _uint(len(value))
        for child in value:
            yield from _chunks(child,strings,depth+1)
    elif isinstance(value,Mapping):
        yield b'\x07'
        yield from _uint(len(value))
        keys = sorted(value,key=lambda key: ''.join(fragments(key,packed=True)))
        for key in keys:
            yield from _chunks(key,strings,depth+1)
            yield from _chunks(value[key],strings,depth+1)
    elif is_dataclass(value) and not isinstance(value,type):
        yield b'\x08'
        yield from _chunks(type(value).__module__,strings,depth+1)
        yield from _chunks(type(value).__qualname__,strings,depth+1)
        attributes = fields(value)
        yield from _uint(len(attributes))
        for f in attributes:
            yield from _chunks(f.name,strings,depth+1)
            yield from _chunks(getattr(value,f.name),strings,depth+1)
    else:
        raise ContractError('unsupported typed phase coordinate')


def extent(value, *, encoded_cap, expanded_cap=EXPANDED_CAP):
    if any(type(cap) is not int or cap <= 0 for cap in (encoded_cap,expanded_cap)):
        raise ContractError('positive finite phase encoding allowances required')
    _guard(value,expanded_cap=expanded_cap)
    expanded = packed_size(value)
    if expanded > expanded_cap:
        raise ResourceExceeded('phase record exceeds its expanded encoding allowance')
    strings, size = {}, 0
    for part in _chunks(value,strings):
        size += len(part)
        if size > encoded_cap:
            raise ResourceExceeded('encoded phase exceeds its prepaid frame')
    return PhaseExtent(size,expanded,len(strings))


def write(value, output, *, start=0, expanded_cap=EXPANDED_CAP):
    """Preflight, then fill only the admitted prefix without resizing output."""
    if (type(output) not in (bytearray,memoryview) or
            (type(output) is memoryview and (output.readonly or output.ndim!=1 or output.format!='B')) or
            type(start) is not int or not 0<=start<len(output)):
        raise ContractError('owned mutable phase extent and offset required')
    measured = extent(value,encoded_cap=len(output)-start,expanded_cap=expanded_cap)
    offset = start
    for part in _chunks(value,{}):
        end = offset+len(part)
        if end > start+measured.encoded_bytes:
            raise ContractError('phase writer exceeded its independently measured prefix')
        output[offset:end] = part
        offset = end
    if offset != start+measured.encoded_bytes:
        raise ContractError('phase writer did not fill its measured prefix')
    return measured


class _Reader:
    def __init__(self,payload,expanded_cap):
        if type(payload) not in (bytes,bytearray,memoryview):
            raise ContractError('complete raw phase bytes required')
        if type(expanded_cap) is not int or expanded_cap <= 0:
            raise ContractError('positive finite expanded phase allowance required')
        self.raw, self.offset = memoryview(payload).cast('B'), 0
        self.strings, self.seen = [], set()
        self.expanded_cap, self.produced = expanded_cap, 0

    def byte(self):
        if self.offset == len(self.raw):
            raise ContractError('truncated binary phase')
        result = self.raw[self.offset]
        self.offset += 1
        return result

    def uint(self, bits):
        value = shift = 0
        while True:
            digit = self.byte()
            value |= (digit & 127) << shift
            if value.bit_length() > bits:
                raise ContractError('binary phase integer exceeds its declared width')
            if digit < 128:
                if shift and digit == 0:
                    raise ContractError('nonminimal binary phase integer')
                return value
            shift += 7
            if shift > bits:
                raise ContractError('unterminated binary phase integer')

    def signed(self):
        word = self.uint(INTEGER_BITS+1)
        value = word//2 if not (word & 1) else -(word//2)-1
        if abs(value).bit_length() > INTEGER_BITS:
            raise ContractError('binary phase signed integer exceeds its width')
        return value

    def count(self):
        count = self.uint(max(1,len(self.raw).bit_length()))
        if count > len(self.raw)-self.offset:
            raise ContractError('binary phase count exceeds its remaining input')
        return count

    def string(self,tag=None):
        tag = self.byte() if tag is None else tag
        if tag == 6:
            index = self.uint(max(1,MAX_STRINGS.bit_length()))
            if index >= len(self.strings):
                raise ContractError('binary phase uses an undefined string')
            return self.strings[index]
        if tag != 5:
            raise ContractError('binary phase schema lost a string coordinate')
        length = self.count()
        if length > self.expanded_cap-self.produced:
            raise ResourceExceeded('binary phase string exceeds its remaining expanded allowance')
        try:
            value = self.raw[self.offset:self.offset+length].tobytes().decode('utf-8','surrogatepass')
        except UnicodeDecodeError as error:
            raise ContractError('binary phase has invalid UTF-8/surrogatepass') from error
        self.offset += length
        if value in self.seen:
            raise ContractError('binary phase duplicates a string definition')
        if len(self.strings) >= MAX_STRINGS:
            raise ResourceExceeded('binary phase string table allowance exhausted')
        self.seen.add(value)
        self.strings.append(value)
        return value

    def quoted(self,value):
        # Reconstruct the old JSON escaping, independently of the binary writer.
        import json
        yield b'"'
        for start in range(0,len(value),256):
            text = json.encoder.encode_basestring(value[start:start+256])[1:-1]
            yield text.replace('\x7f','\\u007f').encode('utf-8','surrogatepass')
        yield b'"'

    def value(self,depth=0):
        if depth > MAX_DEPTH:
            raise ResourceExceeded('binary phase depth allowance exhausted')
        tag = self.byte()
        if tag in (0,1,2):
            yield (b'["NoneType",null]',b'["bool",false]',b'["bool",true]')[tag]
        elif tag == 3:
            yield b'["integer_hex","'+format(self.signed(),'x').encode('ascii')+b'"]'
        elif tag == 4:
            numerator,denominator = self.signed(),self.uint(INTEGER_BITS)
            if not denominator or gcd(numerator,denominator)!=1:
                raise ContractError('binary phase fraction is not canonical')
            yield b'["rational_hex","'+format(numerator,'x').encode('ascii')+b'","'+format(denominator,'x').encode('ascii')+b'"]'
        elif tag in (5,6):
            yield b'["str",'
            yield from self.quoted(self.string(tag))
            yield b']'
        elif tag in (9,10) or 0x20<=tag<0x40:
            if tag in (9,10):
                count = self.count()
                if count < 16:
                    raise ContractError('nonminimal binary phase sequence')
                sequence = b'tuple' if tag==9 else b'list'
            else:
                count = tag & 15
                sequence = b'tuple' if tag<0x30 else b'list'
            yield b'["'+sequence+b'",['
            for k in range(count):
                if k:
                    yield b','
                yield from self.value(depth+1)
            yield b']]'
        elif tag == 7:
            count = self.count()
            yield b'["mapping",['
            for k in range(count):
                if k:
                    yield b','
                yield b'['
                yield from self.value(depth+1)
                yield b','
                yield from self.value(depth+1)
                yield b']'
            yield b']]'
        elif tag == 8:
            yield b'["dataclass",'
            yield from self.quoted(self.string())
            yield b','
            yield from self.quoted(self.string())
            count = self.count()
            yield b',['
            for k in range(count):
                if k:
                    yield b','
                yield b'['
                yield from self.quoted(self.string())
                yield b','
                yield from self.value(depth+1)
                yield b']'
            yield b']]'
        else:
            raise ContractError('unregistered binary phase tag')


def decoded_fragments(payload, *, expanded_cap=EXPANDED_CAP):
    reader = _Reader(payload,expanded_cap)
    for part in reader.value():
        reader.produced += len(part)
        if reader.produced > expanded_cap:
            raise ResourceExceeded('binary phase expansion exceeds its prepaid allowance')
        yield part
    if reader.offset != len(reader.raw):
        raise ContractError('binary phase has trailing input')


def check(payload, expected, *, expanded_cap=EXPANDED_CAP):
    """Compare independently decoded bytes with the entire old typed record."""
    if type(expanded_cap) is not int or expanded_cap <= 0:
        raise ContractError('positive finite expanded phase allowance required')
    _guard(expected,expanded_cap=expanded_cap)
    expected_size = packed_size(expected)
    if expected_size > expanded_cap:
        raise ResourceExceeded('expected phase exceeds its expanded allowance')
    chunks = iter(part.encode('utf-8','surrogatepass') for part in fragments(expected,packed=True))
    current, offset, compared = b'', 0, 0
    for actual in decoded_fragments(payload,expanded_cap=expanded_cap):
        start = 0
        while start < len(actual):
            if offset == len(current):
                current = next(chunks,None)
                if current is None:
                    raise ContractError('binary phase exceeds the complete expected record')
                offset = 0
                if not current:
                    continue
            count = min(len(actual)-start,len(current)-offset)
            if actual[start:start+count] != current[offset:offset+count]:
                raise ContractError('binary phase differs from the complete expected record')
            start += count
            offset += count
            compared += count
    if compared != expected_size or offset != len(current) or any(chunks):
        raise ContractError('binary phase does not contain the entire expected record')
    return compared
