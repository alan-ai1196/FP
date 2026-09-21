"""Byte-only phase compression: the encoder gets no phase, iterator or frame.

The owner serializes its fixed record and checks the complete expansion.
This module cannot attest execution, acquire resources or publish a phase.
"""
import zlib

from .core import ContractError
from .resources import ResourceExceeded

BLOCK = 65536
EXPANDED_CAP = 128 << 20
LIBRARY = (zlib.ZLIB_VERSION,zlib.ZLIB_RUNTIME_VERSION)
ENCODING_ID = 'typed-reference-json-v4-zlib-'+ '-'.join(LIBRARY)+'-l6-w15-m8-s0-v1'


class _Encoder:
    def __init__(self):
        if (zlib.ZLIB_VERSION,zlib.ZLIB_RUNTIME_VERSION)!=LIBRARY:
            raise ContractError('phase compression library identity changed')
        self._stream = zlib.compressobj(6,zlib.DEFLATED,15,8,zlib.Z_DEFAULT_STRATEGY)
        self._received, self._closed = 0,False

    def compress(self,part):
        if self._closed or type(part) is not bytes or not 0<len(part)<=BLOCK:
            raise ContractError('phase compressor requires a bounded immutable byte chunk')
        self._received += len(part)
        if self._received > EXPANDED_CAP:
            raise ResourceExceeded('phase compression input allowance exhausted')
        return self._stream.compress(part)

    def finish(self):
        if self._closed:
            raise ContractError('phase compression stream already finished')
        self._closed = True
        return self._stream.flush(zlib.Z_FINISH)


def new_encoder():
    """No native/physical owner data is supplied to this delegated constructor."""
    return _Encoder()


def decoded_fragments(payload, *, expanded_cap=EXPANDED_CAP):
    """One complete zlib stream, with bounded output chunks and exact EOF.

    This is the trusted independent format reader, not the delegated writer.
    Checksum validity does not establish equality to any execution input.
    Runtime compares every byte with its own canonical record separately.
    """
    if type(payload) not in (bytes,bytearray,memoryview):
        raise ContractError('raw compressed phase bytes required')
    if type(expanded_cap) is not int or expanded_cap<=0:
        raise ContractError('positive phase expansion allowance required')
    raw = memoryview(payload).cast('B')
    stream = zlib.decompressobj(15)
    total = 0
    try:
        for offset in range(0,len(raw),BLOCK):
            data = bytes(raw[offset:offset+BLOCK])
            while data:
                result = stream.decompress(data,min(BLOCK,expanded_cap-total+1))
                total += len(result)
                if total>expanded_cap:
                    raise ResourceExceeded('phase expansion exceeds its prepaid allowance')
                if stream.unused_data:
                    raise ContractError('compressed phase has trailing input or a second stream')
                if result:
                    yield result
                data = stream.unconsumed_tail
            if stream.eof and offset+BLOCK<len(raw):
                raise ContractError('compressed phase has trailing input')
    except zlib.error as exc:
        raise ContractError('invalid compressed phase stream') from exc
    if not stream.eof:
        raise ContractError('truncated compressed phase stream')
