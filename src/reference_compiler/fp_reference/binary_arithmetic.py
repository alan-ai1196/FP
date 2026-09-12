"""Guarded binary rounding and checked actual CPU binary64 scalar execution.

The format oracle is exact arithmetic; the binary64 backend executes Python
float operations and checks their raw outputs against that oracle. Neither
layer has observation, learner, bridge-issuance or installation authority.
Flush-output models only result flushing, not GPU input DAZ/FTZ or FMA.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import math
import struct

from .core import ContractError, natural
from .numerics import compare_exact
from .semantics import ArithmeticUnresolved, _guard, _operation


@dataclass(frozen=True)
class BinaryFormat:
    precision: int
    emin: int
    emax: int
    subnormal_mode: str = 'gradual'

    def __post_init__(self):
        natural(self.precision, 'binary significand precision', positive=True)
        if type(self.emin) is not int or type(self.emax) is not int or self.emin > self.emax:
            raise ContractError('ordered exact binary exponent limits required')
        if type(self.subnormal_mode) is not str or self.subnormal_mode not in ('gradual', 'flush-output'):
            raise ContractError('unregistered binary output subnormal policy')


BINARY64 = BinaryFormat(53, -1022, 1023)


@dataclass(frozen=True)
class RoundedBinary:
    value: F
    negative_zero: bool = False

    def __post_init__(self):
        if type(self.value) is not F or type(self.negative_zero) is not bool or self.negative_zero and self.value:
            raise ContractError('exact rounded value and explicit zero sign required')


def _power(exponent: int, bit_limit: int) -> F:
    if abs(exponent)+1 > bit_limit:
        raise ArithmeticUnresolved('binary scale exceeds reference integer work limit')
    return F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent)


def round_binary(value: F, fmt: BinaryFormat, *, bit_limit: int, negative_zero=False) -> RoundedBinary:
    """One exact nearest/ties-even rounding, then optional output flushing.

Overflow is unresolved, including its half-ulp tie; no finite saturation or
unbounded backend is substituted. Exact zero sign is an operation coordinate
supplied by the registered scalar executor, not recoverable from Fraction(0).
"""
    if type(value) is not F or type(fmt) is not BinaryFormat or type(negative_zero) is not bool:
        raise ContractError('exact rational, format and zero-sign declarations required')
    if negative_zero and value:
        raise ContractError('an exact nonzero already determines its sign')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(value, bit_limit=bit_limit)
    if max(fmt.precision+1, abs(fmt.emin-fmt.precision+1)+1, abs(fmt.emax-fmt.precision+1)+1) > bit_limit:
        raise ArithmeticUnresolved('binary format cannot be encoded under the integer limit')
    if not value:
        return RoundedBinary(F(0), negative_zero)
    sign = value < 0
    magnitude = abs(value)
    exponent = magnitude.numerator.bit_length()-magnitude.denominator.bit_length()
    if compare_exact(magnitude, _power(exponent, bit_limit), bit_limit=bit_limit) < 0:
        exponent -= 1
    if exponent > fmt.emax:
        raise ArithmeticUnresolved('registered binary result overflows')
    step = _power(max(exponent, fmt.emin)-fmt.precision+1, bit_limit)
    scaled = _operation(magnitude, F(step.denominator, step.numerator), multiply=True, bit_limit=bit_limit)
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    complement = scaled.denominator-remainder
    # r versus D-r avoids an extra unchecked 2*r temporary at a half tie.
    increment = remainder > complement or remainder == complement and quotient % 2
    rounded_integer = _operation(F(quotient), F(int(bool(increment))), multiply=False, bit_limit=bit_limit)
    rounded = _operation(rounded_integer, step, multiply=True, bit_limit=bit_limit)
    maximum = _operation(F((1 << fmt.precision)-1), _power(fmt.emax-fmt.precision+1, bit_limit), multiply=True, bit_limit=bit_limit)
    if compare_exact(rounded, maximum, bit_limit=bit_limit) > 0:
        raise ArithmeticUnresolved('registered binary result overflows at rounding')
    if fmt.subnormal_mode == 'flush-output' and compare_exact(rounded, _power(fmt.emin, bit_limit), bit_limit=bit_limit) < 0:
        rounded = F(0)
    return RoundedBinary(-rounded if sign else rounded, bool(sign and not rounded))


@dataclass(frozen=True)
class Float64Value:
    """The complete finite binary64 encoding, including the sign of zero."""
    bits: int

    def __post_init__(self):
        if type(self.bits) is not int or not 0 <= self.bits < 1 << 64:
            raise ContractError('exact uint64 floating encoding required')
        if (self.bits >> 52) & 2047 == 2047:
            raise ArithmeticUnresolved('nonfinite binary64 state is not certifiable')

    @property
    def negative(self):
        return bool(self.bits >> 63)

    @property
    def exact(self):
        exponent = (self.bits >> 52) & 2047
        mantissa = self.bits & ((1 << 52)-1)
        if exponent:
            mantissa += 1 << 52
        shift = exponent-1023-52 if exponent else -1074
        result = F(mantissa << shift) if shift >= 0 else F(mantissa, 1 << -shift)
        return -result if self.negative else result

    def as_float(self):
        return struct.unpack('>d', self.bits.to_bytes(8, 'big'))[0]


class BinaryExecutionMismatch(ArithmeticUnresolved):
    """The actual backend output disagrees with its registered scalar model."""


class Float64Arithmetic:
    """Ordered CPU binary64 primitives, with an exact check of every result.

Runtime prepays a conservative scalar-call allowance before entering a phase.
Operation count and largest exact local rounding error are phase diagnostics;
they are not a CPU elapsed-time, heap or GPU accounting claim.
"""
    backend_id = 'checked-cpython-binary64-rne-gradual-separate-ops-v1'
    scalar_work = 256

    def __init__(self, bit_limit: int):
        natural(bit_limit, 'reference integer work limit', positive=True)
        if bit_limit < 1075:
            raise ArithmeticUnresolved('binary64 raw encoding requires a reference integer limit of at least 1075 bits')
        self.bit_limit = bit_limit
        self.operations = 0
        self.max_round_error = F(0)

    def _value(self, value):
        if type(value) is not Float64Value:
            raise ContractError('exact finite binary64 state encoding required')
        if self.bit_limit < 1075:
            raise ArithmeticUnresolved('binary64 decode exceeds the reference integer work limit')
        result = value.exact
        _guard(result, bit_limit=self.bit_limit)
        return result

    def _finish(self, exact, actual, *, negative_zero=False):
        expected = round_binary(exact, BINARY64, bit_limit=self.bit_limit, negative_zero=negative_zero)
        if type(actual) is not float or not math.isfinite(actual):
            raise ArithmeticUnresolved('actual CPU binary64 produced a nonfinite result')
        decoded = Float64Value(int.from_bytes(struct.pack('>d', actual), 'big'))
        if decoded.exact != expected.value or (not expected.value and decoded.negative != expected.negative_zero):
            raise BinaryExecutionMismatch('actual CPU binary64 differs from its exact registered rounding')
        error = abs(_operation(expected.value, -exact, multiply=False, bit_limit=self.bit_limit))
        if compare_exact(error, self.max_round_error, bit_limit=self.bit_limit) > 0:
            self.max_round_error = error
        return decoded

    def cast(self, value: F):
        if type(value) is not F:
            raise ContractError('registered binary64 cast requires an exact Fraction')
        self.operations += 1
        # Check reference affordability/overflow before invoking the real cast.
        round_binary(value, BINARY64, bit_limit=self.bit_limit)
        try:
            actual = float(value)
        except OverflowError as exc:
            raise ArithmeticUnresolved('actual CPU binary64 cast overflowed') from exc
        return self._finish(value, actual)

    def add(self, left, right):
        self.operations += 1
        a, b = self._value(left), self._value(right)
        exact = _operation(a, b, multiply=False, bit_limit=self.bit_limit)
        minus_zero = not exact and not a and not b and left.negative and right.negative
        return self._finish(exact, left.as_float()+right.as_float(), negative_zero=bool(minus_zero))

    def mul(self, left, right):
        self.operations += 1
        a, b = self._value(left), self._value(right)
        exact = _operation(a, b, multiply=True, bit_limit=self.bit_limit)
        return self._finish(exact, left.as_float()*right.as_float(), negative_zero=bool(not exact and left.negative != right.negative))

    def div(self, left, right):
        self.operations += 1
        a, b = self._value(left), self._value(right)
        if not b:
            raise ArithmeticUnresolved('binary64 division has zero denominator')
        exact = _operation(a, F(b.denominator, b.numerator), multiply=True, bit_limit=self.bit_limit)
        return self._finish(exact, left.as_float()/right.as_float(), negative_zero=bool(not exact and left.negative != right.negative))

    def neg(self, value):
        self.operations += 1
        exact = -self._value(value)
        return self._finish(exact, -value.as_float(), negative_zero=bool(not exact and not value.negative))

    def positive_part(self, value):
        self.operations += 1
        exact = self._value(value)
        return self._finish(max(F(0), exact), max(0.0, value.as_float()))

    def floor_grid(self, value, bits: int):
        """Registered floor-to-dyadic-grid value operation by raw-bit clearing.

This is deliberately explicit; it is not ordinary nearest floating rounding
and is not claimed to be a CUDA kernel or a free optimizer transport.
"""
        self.operations += 1
        natural(bits, 'registered dyadic grid bits')
        exact = self._value(value)
        if exact < 0 or bits+1 > self.bit_limit:
            raise ArithmeticUnresolved('unsupported binary64 grid projection')
        scale = F(1 << bits)
        scaled = _operation(exact, scale, multiply=True, bit_limit=self.bit_limit)
        expected = F(scaled.numerator//scaled.denominator, scale.numerator)
        exponent = (value.bits >> 52) & 2047
        shift = exponent-1023-52 if exponent else -1074
        drop = max(0, -bits-shift)
        word = 0 if drop >= 53 else value.bits & ~((1 << drop)-1)
        # Projection canonicalizes either signed zero to positive zero.
        actual = Float64Value(word & ((1 << 63)-1)).as_float()
        return self._finish(expected, actual)
