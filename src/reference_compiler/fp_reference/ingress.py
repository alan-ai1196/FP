"""Bounded exact rational wire format and passive ingress records.

Encoding is a producer utility. Only Runtime can receive/own a prefix and
authorize ordinary prediction. The grammar represents every nonnegative
rational vector; byte/arithmetic budgets may leave its execution unresolved.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F
from math import gcd

from .core import ContractError, natural
from .program import rational
from .semantics import ArithmeticUnresolved


MAGIC = b'FP1'
STATES = ('RECEIVING', 'DECODED', 'PREDICTED', 'UNRESOLVED', 'INVALID_INPUT', 'EXECUTION_FAILED')


@dataclass(frozen=True)
class IngressContract:
    capacity: int = 4096
    chunk_bytes: int = 64
    codec: str = field(default='canonical-nonnegative-rational-vector-v1', init=False)

    def __post_init__(self):
        natural(self.capacity, 'prepaid input byte capacity', positive=True)
        natural(self.chunk_bytes, 'maximum incoming byte chunk', positive=True)
        if self.chunk_bytes > self.capacity or self.capacity < len(MAGIC):
            raise ContractError('ingress needs a bounded chunk within a nonempty frame window')

    @property
    def control_bytes(self):
        return 1+max(1, (self.capacity.bit_length()+7)//8)

    def work(self, dimensions):
        # Fixed partial reference metric: reserve worst one-byte chunking,
        # copying and bounded parsing. This is not total CPython bit-time.
        return 4*self.capacity+16*dimensions+32


@dataclass(frozen=True)
class IngressIdentity:
    ingress_id: str
    observation_id: str
    cursor: int
    capacity: int
    body_id: str
    control_id: str
    record_id: str
    candidate_ids: tuple[str, ...]
    persistence_ids: tuple[str, ...]


@dataclass(frozen=True)
class IngressSnapshot:
    identity: IngressIdentity
    received: int
    status: str


@dataclass(frozen=True)
class IngressResult:
    status: str
    ingress_id: str | None
    observation_id: str
    cursor: int
    next_offset: int
    max_bytes: int
    reason: str = ''


def control_payload(received: int, status: str, spec: IngressContract) -> bytes:
    natural(received, 'received prefix length')
    if received > spec.capacity or status not in STATES:
        raise ContractError('invalid owned ingress control state')
    return bytes((STATES.index(status),))+received.to_bytes(spec.control_bytes-1, 'big')


def read_control(payload, spec: IngressContract):
    if type(payload) not in (bytes, bytearray) or len(payload) != spec.control_bytes:
        raise ContractError('ingress control lost its prepaid physical extent')
    received = int.from_bytes(payload[1:], 'big')
    if payload[0] >= len(STATES) or received > spec.capacity:
        raise ContractError('invalid owned ingress control encoding')
    return received, STATES[payload[0]]


def _uvarint(value):
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return bytes(result)


def encode_context(values) -> bytes:
    """External producer serialization, never an input/admission certificate."""
    result = bytearray(MAGIC)
    for value in values:
        value = rational(value, 'producer rational context')
        for integer in (value.numerator, value.denominator):
            length = (integer.bit_length()+7)//8
            result.extend(_uvarint(length))
            result.extend(integer.to_bytes(length, 'big'))
    return bytes(result)


def decode_context(payload: bytes, dimensions: int, bit_limit: int) -> tuple[F, ...]:
    """Decode only an already owned finite prefix; no authority is returned.

Length fields are bounded before integer materialization. Nonminimal
integers, nonreduced rationals and extra bytes are not canonical frames.
"""
    if type(payload) is not bytes:
        raise ContractError('the decoder reads an owned immutable byte prefix')
    natural(dimensions, 'input dimension')
    natural(bit_limit, 'input integer work limit', positive=True)
    if len(payload) < len(MAGIC):
        raise ArithmeticUnresolved('input frame ended before its fixed header')
    if payload[:len(MAGIC)] != MAGIC:
        raise ContractError('unregistered exact input wire format')
    offset = len(MAGIC)
    max_length = (bit_limit+7)//8

    def integer():
        nonlocal offset
        length, shift, groups = 0, 0, 0
        while True:
            if offset == len(payload):
                raise ArithmeticUnresolved('input length prefix is incomplete')
            byte = payload[offset]
            offset += 1
            part = byte & 127
            # Check before the shift/add; a huge length field never creates
            # a huge integer or asks the machine to allocate its body.
            if shift >= max_length.bit_length()+7 or part > (max_length-length) >> shift:
                raise ArithmeticUnresolved('input integer body exceeds the registered arithmetic capacity')
            length += part << shift
            groups += 1
            if not byte & 128:
                if groups > 1 and part == 0:
                    raise ContractError('nonminimal input length encoding')
                break
            shift += 7
        if len(payload)-offset < length:
            raise ArithmeticUnresolved('input integer body is incomplete within the received prefix')
        if not length:
            return 0
        leading = payload[offset]
        if not leading:
            raise ContractError('nonminimal input integer encoding')
        if 8*(length-1)+leading.bit_length() > bit_limit:
            raise ArithmeticUnresolved('input integer exceeds the registered arithmetic capacity')
        value = int.from_bytes(payload[offset:offset+length], 'big')
        offset += length
        return value

    result = []
    for _ in range(dimensions):
        numerator, denominator = integer(), integer()
        if not denominator or gcd(numerator, denominator) != 1:
            raise ContractError('input rational must have a positive denominator and be reduced')
        result.append(F(numerator, denominator))
    if offset != len(payload):
        raise ContractError('input frame has bytes beyond its registered dimensions')
    return tuple(result)
