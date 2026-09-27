"""Guarded half/single primitive decisions for the owned token phase checker.

CPU arrays interpret the explicit operation graph; these checks verify its
floating primitives. They never provide an actual device successor. The
binary64 enclosure assumptions are the existing token reference contract.
"""
import numpy as np

from .core import ContractError
from .token_enclosures import EnclosureUnresolved
from .token_readout_relation import Binary32Decoder


class CheckedPrimitives:
    def __init__(self, exact_cell_cap):
        self.decoder = Binary32Decoder(exact_cell_cap)
        self.words = 0

    def __call__(self, tag, output, *inputs):
        if not np.all(np.isfinite(output)):
            raise EnclosureUnresolved('nonfinite token primitive result')
        if tag == 'cast':
            value = inputs[0]
            # Registered q/column integers are <=2**52. Wider caller integers
            # must not silently use a double-rounded int64 -> float64 -> f32.
            if value.dtype == np.int64 and np.any(np.abs(value) > 1 << 53):
                raise EnclosureUnresolved('integer cast exceeds the exact binary64 decoder domain')
            expected = value.astype(np.float64).astype(output.dtype)
        elif tag == 'ceil':
            expected = np.ceil(inputs[0].astype(np.float64)).astype(output.dtype)
        elif output.dtype == np.float32:
            left, right = inputs
            expected = self.decoder.op('add' if tag == 'sub' else tag, left, -right if tag == 'sub' else right)
        elif output.dtype == np.float16 and tag in ('add', 'sub', 'mul'):
            # A half product has <=22 significand bits. An exact half sum or
            # difference spans <=41 bits, including subnormals: binary64 is
            # exact here, before the single specified nearest-even half cast.
            left, right = (value.astype(np.float64) for value in inputs)
            value = left+right if tag == 'add' else left-right if tag == 'sub' else left*right
            expected = value.astype(np.float16)
        else:
            raise ContractError('unregistered checked token primitive')
        if (expected.shape != output.shape or expected.dtype != output.dtype
                or expected.tobytes() != output.tobytes()):
            raise EnclosureUnresolved('token primitive differs from its registered RNE decision')
        self.words += output.size
