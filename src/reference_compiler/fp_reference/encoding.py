"""Typed streaming JSON encodings and exact packed extents.

Typed UTF-8 JSON uses surrogatepass to distinguish every Python string code
point, including explicit surrogate code units. Extent calculation does not
serialize atoms or sort mapping keys. These helpers carry no authority.
"""
from dataclasses import fields, is_dataclass
from enum import Enum
from fractions import Fraction as F
import json
from collections.abc import Mapping


def _invalid(message):
    # core imports the streaming encoder lazily for identity hashing.
    from .core import ContractError
    raise ContractError(message)


def _string_size(value):
    size = 2
    for char in value:
        code = ord(char)
        size += (2 if char in '\"\\\b\f\n\r\t' else 6 if code < 32 or code == 127 else
                 1 if code < 128 else 2 if code < 2048 else 3 if code < 65536 else 4)
    return size


def _hex_size(value):
    return max(1, (value.bit_length()+3)//4)+int(value < 0)+2


def _array_size(sizes):
    size, count = 2, 0
    for child in sizes:
        size += child
        count += 1
    return size+max(0, count-1)


def packed_size(value):
    """Exact byte extent of the typed packed encoding, with no output tree."""
    if type(value) is F:
        return _array_size((_string_size('rational_hex'), _hex_size(value.numerator), _hex_size(value.denominator)))
    if type(value) is int:
        return _array_size((_string_size('integer_hex'), _hex_size(value)))
    if value is None or type(value) in (str, bool):
        atom = 4 if value is None or value is True else 5 if value is False else _string_size(value)
        return _array_size((_string_size(type(value).__name__), atom))
    if type(value) in (tuple, list):
        return _array_size((_string_size(type(value).__name__), _array_size(packed_size(x) for x in value)))
    if isinstance(value, Mapping):
        pairs = (_array_size((packed_size(k), packed_size(v))) for k, v in value.items())
        return _array_size((_string_size('mapping'), _array_size(pairs)))
    if is_dataclass(value) and not isinstance(value, type):
        entries = (_array_size((_string_size(f.name), packed_size(getattr(value, f.name)))) for f in fields(value))
        return _array_size((_string_size('dataclass'), _string_size(type(value).__module__),
                            _string_size(type(value).__qualname__), _array_size(entries)))
    _invalid('unsupported packed reference payload')


def bounded_packed_size(value, *, byte_limit, depth_limit=64, integer_bits=32768):
    """Bound aggregate traversal before computing the exact canonical extent.

This belongs to the trusted canonical serializer. A delegated compressor
never receives the value or the iterator used to traverse it.
"""
    from .resources import ResourceExceeded
    if any(type(n) is not int or n<=0 for n in (byte_limit,depth_limit,integer_bits)):
        _invalid('positive canonical traversal limits required')
    charged = 0
    def debit(amount):
        nonlocal charged
        charged += amount
        if charged>byte_limit:
            raise ResourceExceeded('canonical phase traversal allowance exhausted')
    def walk(item,depth):
        debit(1)
        if depth>depth_limit:
            raise ResourceExceeded('canonical phase depth allowance exhausted')
        if item is None or type(item) is bool:
            return
        if type(item) is str:
            debit(len(item))
            return
        if type(item) in (int,F):
            numbers = (item,) if type(item) is int else (item.numerator,item.denominator)
            if any(n.bit_length()>integer_bits for n in numbers):
                raise ResourceExceeded('canonical phase integer allowance exhausted')
            debit(sum(max(1,(n.bit_length()+3)//4) for n in numbers))
            return
        if type(item) in (tuple,list):
            children = iter(item)
        elif isinstance(item,Mapping):
            children = (child for pair in item.items() for child in pair)
        elif is_dataclass(item) and not isinstance(item,type):
            walk(type(item).__module__,depth+1)
            walk(type(item).__qualname__,depth+1)
            children = (child for f in fields(item) for child in (f.name,getattr(item,f.name)))
        else:
            _invalid('unsupported packed reference payload')
        for child in children:
            walk(child,depth+1)
    walk(value,0)
    result = packed_size(value)
    if result>byte_limit:
        raise ResourceExceeded('canonical phase exceeds its expanded allowance')
    return result


def _string(value):
    yield '"'
    # Raw non-ASCII code points remain distinct. ensure_ascii=True would
    # collapse an astral character and two explicit surrogate code units.
    for start in range(0, len(value), 256):
        yield json.encoder.encode_basestring(value[start:start+256])[1:-1].replace('\x7f', '\\u007f')
    yield '"'


def _array(items, *, spaced=False):
    yield '['
    first = True
    for item in items:
        if not first:
            yield ', ' if spaced else ','
        first = False
        yield from item
    yield ']'


def fragments(value, *, packed=False, spaced=False):
    """Yield typed JSON before UTF-8/surrogatepass encoding or hashing.

    Preserve each encoder's key-sort spacing. Sorting retains encoded keys
    only; values are streamed. Scalar integer text and those keys remain
    workspace, not a complete host-memory theorem. ASCII artifacts stay
    compatible; non-ASCII encodings change to preserve source identities.
"""
    def sequence(items):
        return _array(items, spaced=spaced)

    def nested(value, *, spaced=spaced):
        return fragments(value, packed=packed, spaced=spaced)

    if not packed and isinstance(value, Enum):
        yield from sequence((_string('enum'), _string(type(value).__module__),
                             _string(type(value).__qualname__), nested(value.value)))
    elif type(value) is F:
        if packed:
            items = (_string('rational_hex'), _string(format(value.numerator, 'x')), _string(format(value.denominator, 'x')))
        else:
            items = (_string('rational'), iter((str(value.numerator),)), iter((str(value.denominator),)))
        yield from sequence(items)
    elif type(value) is int and packed:
        yield from sequence((_string('integer_hex'), _string(format(value, 'x'))))
    elif value is None or type(value) in (bool, str, int):
        atom = (_string(value) if type(value) is str else iter((
            'null' if value is None else 'true' if value is True else 'false' if value is False else str(value),)))
        yield from sequence((_string(type(value).__name__), atom))
    elif type(value) is float and not packed:
        from .core import require_finite
        require_finite(value, 'state coordinate')
        yield from sequence((_string('float'), _string(value.hex())))
    elif type(value) is bytes and not packed:
        yield from sequence((_string('bytes'), _string(value.hex())))
    elif type(value) in (tuple, list):
        yield from sequence((_string(type(value).__name__), sequence(nested(x) for x in value)))
    elif isinstance(value, Mapping):
        # The historical packed key sort was compact; the identity key sort
        # used json.dumps' default spaces. Preserve both artifact orders.
        keys = sorted(value, key=lambda k: ''.join(nested(k, spaced=not packed)))
        pairs = (sequence((nested(k), nested(value[k]))) for k in keys)
        yield from sequence((_string('mapping'), sequence(pairs)))
    elif is_dataclass(value) and not isinstance(value, type):
        entries = (sequence((_string(f.name), nested(getattr(value, f.name)))) for f in fields(value))
        yield from sequence((_string('dataclass'), _string(type(value).__module__),
                             _string(type(value).__qualname__), sequence(entries)))
    else:
        _invalid('unsupported packed reference payload' if packed else
                 f'unsupported complete-state coordinate type: {type(value).__name__}')


def write_packed(value, output):
    """Fill an already admitted exact-size bytearray without resizing it."""
    if type(output) is not bytearray:
        _invalid('packed materialization requires owned mutable byte storage')
    offset = 0
    for fragment in fragments(value, packed=True):
        part = fragment.encode('utf-8', 'surrogatepass')
        end = offset+len(part)
        if end > len(output):
            _invalid('packed materialization exceeds its admitted extent')
        output[offset:end] = part
        offset = end
    if offset != len(output):
        _invalid('packed materialization did not fill its admitted extent')


def pack(value):
    """Producer/audit convenience; Runtime writes to its paid buffer directly."""
    result = bytearray(packed_size(value))
    write_packed(value, result)
    return bytes(result)
