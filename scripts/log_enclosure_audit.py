"""Bounded independent exact verification of a claimed log-ratio interval.

No Decimal comparison, production log_enclosure call or Runtime authority.
Containment certifies only this scalar claim. Inconclusive arithmetic fails
unresolved; it is never converted into an accepted numerical check.
"""
from dataclasses import dataclass
from fractions import Fraction as F


class LogAuditUnresolved(RuntimeError):
    pass


@dataclass(frozen=True)
class LogAudit:
    terms: int
    maximum_operand_bits: int
    # Number of scalar preflight checks, not physical work or a Runtime charge.
    operations: int


class _Rationals:
    def __init__(self, max_bits):
        if type(max_bits) is not int or max_bits < 8:
            raise ValueError('positive exact audit bit allowance of at least eight required')
        self.max_bits = max_bits
        self.maximum_operand_bits = 0
        self.operations = 0

    def check(self, value):
        if type(value) is not F:
            raise TypeError('exact Fraction audit operands required')
        bits = max(value.numerator.bit_length(), value.denominator.bit_length())
        if bits > self.max_bits:
            raise LogAuditUnresolved('exact log audit operand exceeds its bit allowance')
        self.maximum_operand_bits = max(self.maximum_operand_bits, bits)
        return value

    def reserve(self, bits):
        if bits > self.max_bits:
            raise LogAuditUnresolved('exact log audit operation exceeds its bit allowance')
        self.operations += 1

    def add(self, a, b):
        self.check(a); self.check(b)
        self.reserve(max(a.numerator.bit_length()+b.denominator.bit_length(),
                         b.numerator.bit_length()+a.denominator.bit_length())+1)
        self.reserve(a.denominator.bit_length()+b.denominator.bit_length())
        return self.check(a+b)

    def mul(self, a, b):
        self.check(a); self.check(b)
        self.reserve(max(a.numerator.bit_length()+b.numerator.bit_length(),
                         a.denominator.bit_length()+b.denominator.bit_length()))
        return self.check(a*b)

    def div(self, a, b):
        self.check(b)
        if b == 0:
            raise ValueError('nonzero audit divisor required')
        return self.mul(a, F(b.denominator, b.numerator))

    def le(self, a, b):
        self.check(a); self.check(b)
        self.reserve(max(a.numerator.bit_length()+b.denominator.bit_length(),
                         b.numerator.bit_length()+a.denominator.bit_length()))
        return a <= b

    def power_two(self, exponent):
        self.reserve(abs(exponent)+1)
        return self.check(F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent))


def _series(value, terms, arithmetic):
    """Signed direct atanh series; no production range/log2 decomposition."""
    a = arithmetic
    z = a.div(a.add(value, F(-1)), a.add(value, F(1)))
    if z == 0:
        return F(0), F(0)
    square = a.mul(z, z)
    power, center = z, F(0)
    for j in range(terms):
        center = a.add(center, a.div(a.mul(F(2), power), F(2*j+1)))
        power = a.mul(power, square)
    tail = a.div(a.mul(F(2), abs(power)), a.mul(F(2*terms+1), a.add(F(1), -square)))
    return (center, a.add(center, tail)) if z > 0 else (a.add(center, -tail), center)


def _interval(value, terms, arithmetic):
    a = arithmetic
    exponent = value.numerator.bit_length()-value.denominator.bit_length()
    residual = a.div(value, a.power_two(exponent))
    if a.le(F(3, 2), residual):
        residual = a.div(residual, F(2))
        exponent += 1
    elif not a.le(F(3, 4), residual):
        residual = a.mul(residual, F(2))
        exponent -= 1
    assert a.le(F(3, 4), residual) and not a.le(F(3, 2), residual)
    lo, hi = _series(residual, terms, a)
    if exponent:
        # Independent log2 identity uses z=1/5 and z=1/7. The production
        # kernel uses z=1/3 and a nonnegative residual in [1,2).
        first, second = _series(F(3, 2), terms, a), _series(F(4, 3), terms, a)
        lower, upper = a.add(first[0], second[0]), a.add(first[1], second[1])
        if exponent < 0:
            lower, upper = upper, lower
        lo = a.add(lo, a.mul(F(exponent), lower))
        hi = a.add(hi, a.mul(F(exponent), upper))
    assert a.le(lo, hi)
    return lo, hi


def verify_log_ratio(numerator, denominator, lower, upper, *, max_terms=128, max_bits=262144):
    """Prove log(numerator/denominator) in [lower,upper] or fail closed.

The returned record is audit metadata, not a persistence certificate. Both
budgets bound this verifier, independently of the producer's numeric guards.
"""
    if type(max_terms) is not int or max_terms < 1:
        raise ValueError('positive finite series budget required')
    a = _Rationals(max_bits)
    for value in (numerator, denominator, lower, upper):
        a.check(value)
    if numerator <= 0 or denominator <= 0:
        raise ValueError('positive exact log-ratio operands required')
    if not a.le(lower, upper):
        raise AssertionError('claimed logarithm interval is reversed')
    value = a.div(numerator, denominator)
    if value == 1:
        if not a.le(lower, F(0)) or not a.le(F(0), upper):
            raise AssertionError('claimed interval excludes exact log(1)=0')
        return LogAudit(0, a.maximum_operand_bits, a.operations)
    terms = min(8, max_terms)
    while True:
        lo, hi = _interval(value, terms, a)
        if a.le(lower, lo) and a.le(hi, upper):
            return LogAudit(terms, a.maximum_operand_bits, a.operations)
        if not a.le(lower, hi) or not a.le(lo, upper):
            raise AssertionError('claimed logarithm interval is disjoint from an independent exact enclosure')
        if terms == max_terms:
            raise LogAuditUnresolved('independent exact enclosure is inconclusive within the series allowance')
        terms = min(terms*2, max_terms)
