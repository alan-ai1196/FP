"""Guarded exact rational arithmetic for owned reference calculations.

These pure helpers have no observation, e-process, bridge or installation
authority. Their work count is a conservative reference primitive charge,
not CPython heap accounting, bit-time or a physical performance bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import gcd

from .core import ContractError, natural
from .semantics import ArithmeticUnresolved, _guard, _operation


@dataclass(frozen=True)
class LogInterval:
    """Signed exact bounds; unlike activation bounds, logarithms may be negative.

This data constructor has no bit/work budget or authority. Its ordinary
ordering validation is unbudgeted. Owned calculations must check ordering
with compare_exact before construction; log_enclosure does so internally.
    """

    lower: F
    upper: F

    def __post_init__(self):
        if type(self.lower) is not F or type(self.upper) is not F:
            raise ContractError('logarithm endpoints must be exact Fractions')
        if self.lower > self.upper:
            raise ContractError('reversed logarithm enclosure')


def log_enclosure_work(terms: int) -> int:
    """Paid-before-execution upper charge for one fixed-term log calculation.

Two series use at most six rational operations per term in total. Each uses
its existing internal preflight/result guards; the larger charge covers these,
reduction, scalar/control operations, guarded interval ordering and the final
signed interval combination.
Operand sizes retain their independent integer-work cap. This is not a bound
on integer arithmetic running time.
    """
    natural(terms, 'registered logarithm terms', positive=True)
    return 32*terms+288


def _fraction(value, name: str, *, nonnegative=False, positive=False):
    if type(value) is not F:
        raise ContractError(f'{name} must be an exact Fraction')
    if positive and value <= 0 or nonnegative and value < 0:
        raise ContractError(f'{name} is outside its registered range')
    return value


def compare_exact(left: F, right: F, *, bit_limit: int) -> int:
    """Return -1, 0 or 1 using guarded signed integer cross products.

Even sign/equality cases use the same fixed calculation, so a successful
comparison also establishes that a subsequent ordinary Fraction comparison
of these same endpoints has affordable integer products. This conservative
reference primitive may be unresolved when a more specialized solver could
decide the signs without constructing those products.
    """
    _fraction(left, 'left comparison operand')
    _fraction(right, 'right comparison operand')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(left, right, bit_limit=bit_limit)
    first = _operation(F(left.numerator), F(right.denominator), multiply=True, bit_limit=bit_limit)
    second = _operation(F(right.numerator), F(left.denominator), multiply=True, bit_limit=bit_limit)
    # Fraction denominators are positive. Comparing the guarded integer
    # numerators performs no further rational cross multiplication.
    return (first.numerator > second.numerator)-(first.numerator < second.numerator)


def compare_exact_work() -> int:
    """Conservative fixed reference charge, including both products' guards."""
    return 24


def compare_reduced_exact(left: F, right: F, *, bit_limit: int) -> int:
    """Exact order after canceling factors shared by both cross products.

    Unlike compare_exact, this proves only the order, not affordability of
    later unreduced Fraction comparisons. Inputs are retained unchanged.
    GCD/remainders and quotients never exceed the guarded operand widths;
    every remaining product has the original preflight and result guards.
    """
    _fraction(left, 'left reduced comparison operand')
    _fraction(right, 'right reduced comparison operand')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(left, right, bit_limit=bit_limit)
    denominator_factor = gcd(left.denominator, right.denominator)
    numerator_factor = gcd(abs(left.numerator), abs(right.numerator)) or 1
    first = _operation(F(left.numerator//numerator_factor), F(right.denominator//denominator_factor),
                       multiply=True, bit_limit=bit_limit)
    second = _operation(F(right.numerator//numerator_factor), F(left.denominator//denominator_factor),
                        multiply=True, bit_limit=bit_limit)
    return (first.numerator > second.numerator)-(first.numerator < second.numerator)


def add_reduced_exact(left: F, right: F, *, bit_limit: int) -> F:
    """Guarded canonical rational addition without first multiplying b*d.

    For g=gcd(b,d), s=a*(d/g)+c*(b/g), all possible final denominator
    cancellation is in gcd(s,g). Guard the signed numerator work first,
    then form the already reduced denominator. This may still be UNRESOLVED
    when those guarded numerator operations do not fit.
    """
    _fraction(left, 'left reduced sum operand')
    _fraction(right, 'right reduced sum operand')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(left, right, bit_limit=bit_limit)
    g = gcd(left.denominator, right.denominator)
    first = _operation(F(left.numerator), F(right.denominator//g), multiply=True, bit_limit=bit_limit)
    second = _operation(F(right.numerator), F(left.denominator//g), multiply=True, bit_limit=bit_limit)
    total = _operation(first, second, multiply=False, bit_limit=bit_limit).numerator
    cancel = gcd(total, g)
    denominator = _operation(F(left.denominator//g), F(right.denominator//cancel),
                             multiply=True, bit_limit=bit_limit).numerator
    result = F(total//cancel, denominator)
    _guard(result, bit_limit=bit_limit)
    return result


def reduced_exact_work(*, addition=False) -> int:
    """Fixed guarded integer/GCD/quotient tariff, excluding bigint bit-time."""
    return 96 if addition else 64


def log_enclosure(value: F, *, terms: int, bit_limit: int) -> LogInterval:
    """Enclose log(value), without floating point or an unbounded exact backend.

Write value = 2**e * r with 1 <= r < 2. For z=(r-1)/(r+1),
the first `terms` terms of 2*atanh(z) give a lower bound, and
2*z**(2*terms+1)/((2*terms+1)*(1-z*z)) bounds the positive tail.
The same formula at r=2 bounds log(2). Signed interval multiplication by e
then encloses the original logarithm, including arbitrarily small rationals.

All rational arithmetic uses the existing conservative preflight guard.
Exceeding it means ArithmeticUnresolved; cancellation is never presumed to
make an unexecuted arithmetic operation affordable.
    """
    _fraction(value, 'logarithm argument', positive=True)
    natural(terms, 'registered logarithm terms', positive=True)
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(value, F(2*terms+1), bit_limit=bit_limit)

    def add(a, b):
        return _operation(a, b, multiply=False, bit_limit=bit_limit)

    def mul(a, b):
        return _operation(a, b, multiply=True, bit_limit=bit_limit)

    def inverse(a):
        _guard(a, bit_limit=bit_limit)
        if a == 0:
            raise ContractError('zero divisor in logarithm enclosure')
        result = F(a.denominator, a.numerator)
        _guard(result, bit_limit=bit_limit)
        return result

    def interval(lower, upper):
        if compare_exact(lower, upper, bit_limit=bit_limit) > 0:
            raise ContractError('guarded logarithm calculation produced reversed bounds')
        return LogInterval(lower, upper)

    def series(r):
        if r == 1:
            return interval(F(0), F(0))
        z = mul(add(r, F(-1)), inverse(add(r, F(1))))
        square = mul(z, z)
        power, total = z, F(0)
        for j in range(terms):
            total = add(total, mul(power, F(1, 2*j+1)))
            power = mul(power, square)
        center = mul(F(2), total)
        denominator = mul(F(2*terms+1), add(F(1), mul(F(-1), square)))
        tail = mul(mul(F(2), power), inverse(denominator))
        return interval(center, add(center, tail))

    if value == 1:
        return interval(F(0), F(0))
    exponent = value.numerator.bit_length()-value.denominator.bit_length()
    _guard(F(exponent), bit_limit=bit_limit)
    # Input guards imply this shift fits, but retain an explicit preflight so
    # a future change to reduction cannot allocate an unchecked huge integer.
    if abs(exponent)+1 > bit_limit:
        raise ArithmeticUnresolved('logarithm reduction scale exceeds integer work limit')
    scale = F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent)
    _guard(scale, bit_limit=bit_limit)
    reduced = mul(value, inverse(scale))
    if reduced < 1:
        reduced = mul(F(2), reduced)
        exponent -= 1
        _guard(F(exponent), bit_limit=bit_limit)
    if not F(1) <= reduced < F(2):
        raise ContractError('logarithm reduction failed to establish its series domain')
    residual, two = series(reduced), series(F(2))
    low, high = (two.lower, two.upper) if exponent >= 0 else (two.upper, two.lower)
    return interval(add(residual.lower, mul(F(exponent), low)),
                    add(residual.upper, mul(F(exponent), high)))


def floor_nonnegative_dyadic(value: F, *, bits: int, bit_limit: int) -> F:
    """Round down a nonnegative value; no cap, wealth or probability is assumed.

The caller owns its actual wealth bound and resource/evidence policy. This
helper proves only 0 <= result <= value < result+2**(-bits), and monotonicity.
Rounding cannot create evidence; affordable computation can still return zero.
    """
    _fraction(value, 'dyadic floor argument', nonnegative=True)
    natural(bits, 'dyadic fractional bits')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(value, bit_limit=bit_limit)
    if bits+1 > bit_limit:
        raise ArithmeticUnresolved('dyadic floor scale exceeds integer work limit')
    scale = F(1 << bits)
    _guard(scale, bit_limit=bit_limit)
    scaled = _operation(value, scale, multiply=True, bit_limit=bit_limit)
    # The floor quotient cannot have more bits than its guarded numerator.
    integral = scaled.numerator//scaled.denominator
    _guard(F(integral), bit_limit=bit_limit)
    result = F(integral, scale.numerator)
    _guard(result, bit_limit=bit_limit)
    return result
