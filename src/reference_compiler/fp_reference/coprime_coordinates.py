"""Bounded rational factor coordinates and a jointly scaled integer readout.

These pure helpers have no Runtime, ingress, installation or AMP authority.
An owner must fund their allowances and bind every input to its native state.
They do not factor integers into primes or evaluate floating logarithms.
"""
from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError, natural
from .semantics import ArithmeticUnresolved


class _Meter:
    def __init__(self, bits, work, cells):
        for label, value in (('integer bits', bits), ('work', work), ('cells', cells)):
            natural(value, 'coprime '+label+' allowance', positive=True)
        self.bits, self.limit, self.cells = bits, work, cells
        self.operations = self.peak_cells = 0

    def take(self, count=1):
        if self.operations+count > self.limit:
            raise ArithmeticUnresolved('coprime arithmetic exhausted its supplied work allowance')
        self.operations += count

    def integer(self, value):
        self.take()
        if type(value) is not int:
            raise ContractError('exact coprime integer required')
        if value.bit_length() > self.bits:
            raise ArithmeticUnresolved('coprime integer precision exhausted')

    def extent(self, count):
        self.take()
        if count > self.cells:
            raise ArithmeticUnresolved('coprime working-cell allowance exhausted')
        self.peak_cells = max(self.peak_cells, count)

    def gcd(self, a, b):
        while b:
            self.take(3)  # comparison, remainder and reassignment tariff
            a, b = b, a % b
        return a

    def ordered(self, values):
        # Explicit comparison/index tariff; not a bit-time or heap theorem.
        self.take(16*(len(values)+1)*max(1, len(values).bit_length()))
        return tuple(sorted(values))


@dataclass(frozen=True)
class CoprimeFactorization:
    bases: tuple[int, ...]
    exponents: tuple[tuple[int, ...], ...]
    operations: int
    splits: int
    peak_basis_cells: int


def factor(values, *, bit_limit, work_limit, cell_limit):
    """Encode positive rational values in a deterministic coprime basis.

    Cell allowance bounds the working basis, including intermediate splits.
    Input/output ratio tables require their own enclosing storage allowance.
    """
    meter = _Meter(bit_limit, work_limit, cell_limit)
    if type(values) is not tuple:
        raise ContractError('ordered positive exact rational inputs required')
    meter.take(4*(len(values)+1))
    if any(type(v) is not F or v <= 0 for v in values):
        raise ContractError('ordered positive exact rational inputs required')
    current = set()
    for value in values:
        for number in (value.numerator, value.denominator):
            meter.integer(number)
            if number > 1 and number not in current:
                meter.extent(len(current)+1)
                current.add(number)
    # This bounds log2(product(current)) without building that large product.
    meter.take(2*(len(current)+1))
    split_limit = sum(number.bit_length() for number in current)
    splits = 0
    while True:
        ordered = meter.ordered(current)
        changed = False
        for i, a in enumerate(ordered):
            for j in range(i+1, len(ordered)):
                b = ordered[j]
                meter.take()
                common = meter.gcd(a, b)
                if common == 1:
                    continue
                meter.take(8)
                parts = {v for v in (common, a//common, b//common) if v > 1}
                count = len(current)-2+len(parts-current)
                # a or b can themselves be one of the replacement parts.
                count += len(parts & {a, b})
                meter.extent(count)
                current.difference_update((a, b))
                current.update(parts)
                assert len(current) == count
                splits += 1
                assert splits <= split_limit
                changed = True
                break
            if changed:
                break
        if not changed:
            break
    bases = ordered
    encoded = []
    for value in values:
        numerator, denominator = value.numerator, value.denominator
        row = []
        for base in bases:
            exponent = 0
            for sign in (1, -1):
                number = numerator if sign == 1 else denominator
                while True:
                    meter.take(2)
                    quotient, remainder = divmod(number, base)
                    if remainder:
                        break
                    number = quotient
                    exponent += sign
                if sign == 1:
                    numerator = number
                else:
                    denominator = number
            row.append(exponent)
        if numerator != 1 or denominator != 1:
            raise ContractError('coprime refinement failed to reconstruct an actual input')
        encoded.append(tuple(row))
    return CoprimeFactorization(bases, tuple(encoded), meter.operations, splits, meter.peak_cells)


@dataclass(frozen=True)
class IntegerWeightPlan:
    weights: tuple[int, ...]
    binary_shift: int
    operations: int
    peak_weight_cells: int
    integer_envelopes: tuple[int, ...]


def integer_weights(bases, exponents, *, bit_limit, work_limit, cell_limit):
    """Remove common rational denominators, then select one joint binary scale.

    Never clamp or normalize the separate bases in floating point. The
    returned integers are transient weights, not the persistent learner.
    """
    meter = _Meter(bit_limit, work_limit, cell_limit)
    if type(bases) is not tuple or type(exponents) is not tuple or not exponents:
        raise ContractError('complete integer factor/exponent rows required')
    meter.take(4*(len(bases)+1)*(len(exponents)+1))
    if (any(type(b) is not int or b < 2 for b in bases)
            or any(type(row) is not tuple or len(row) != len(bases)
                   or any(type(e) is not int for e in row) for row in exponents)):
        raise ContractError('complete integer factor/exponent rows required')
    meter.extent(len(exponents))
    for base in bases:
        meter.integer(base)
    for row in exponents:
        for exponent in row:
            meter.integer(exponent)
    meter.take((len(exponents)+1)*(len(bases)+1))
    minima = tuple(min(row[j] for row in exponents) for j in range(len(bases)))
    meter.take(4*(len(exponents)+1)*(len(bases)+1))
    differences = tuple(tuple(e-m for e, m in zip(row, minima)) for row in exponents)
    envelopes = tuple(max(1, sum(base.bit_length()*e for base, e in zip(bases, row))) for row in differences)
    if max(envelopes)+1 > bit_limit:
        raise ArithmeticUnresolved('joint integer weights or their binary scale exceed the precision allowance')

    def multiply(a, b):
        meter.take()
        # The whole-row envelope proves every MSB-prefix product fits before
        # execution; this check detects an internal violation of that plan.
        value = a*b
        if value.bit_length() > bit_limit:
            raise ContractError('proved integer-weight envelope was violated')
        return value

    def power(base, exponent):
        result = 1
        for position in range(exponent.bit_length()-1, -1, -1):
            meter.take(2)
            result = multiply(result, result)
            if exponent >> position & 1:
                result = multiply(result, base)
        return result

    weights = []
    for row in differences:
        value = 1
        for base, exponent in zip(bases, row):
            value = multiply(value, power(base, exponent))
        weights.append(value)
    shift = max(value.bit_length() for value in weights)
    assert shift+1 <= bit_limit
    return IntegerWeightPlan(tuple(weights), shift, meter.operations, meter.peak_cells, envelopes)
