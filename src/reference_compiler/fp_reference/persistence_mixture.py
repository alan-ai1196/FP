"""Guarded positive mixture arithmetic; no observation or evidence authority.

Only Runtime may bind a curve to its fresh identity and current trajectory.
No float integration, extra scalar wealth rounding or supplied bet occurs.
All returned state must be retained in the same owned identity as its wealth.
"""
from fractions import Fraction as F

from .core import ContractError, natural
from .persistence import ArcsinePersistenceRule, threshold_crossed
from .semantics import ArithmeticUnresolved, _guard, _operation


def initial_work():
    return 1024


def step_work(epochs):
    """Prepaid primitive charge, including two streamed guarded readouts.

    Each readout has two linear loops of guarded integer arithmetic. Each
    update cell adds one guarded product, quotient and sum. 1024 per cell
    covers these, the input/state scans, normalizing the gain and threshold.
    Integer bit limits and actual host memory remain separate constraints.
    """
    natural(epochs, 'completed evidence epochs')
    return 1024*(epochs+3)


class _Integers:
    def __init__(self, bits):
        natural(bits, 'reference integer work limit', positive=True)
        self.bits = bits

    def guard(self, value):
        if type(value) is not int or value < 0:
            raise ContractError('nonnegative exact mixture integer required')
        if value.bit_length() > self.bits:
            raise ArithmeticUnresolved('mixture integer work limit exceeded')
        return value

    def add(self, a, b):
        self.guard(a)
        self.guard(b)
        if max(a.bit_length(), b.bit_length())+1 > self.bits:
            raise ArithmeticUnresolved('mixture sum may exceed its integer work limit')
        return self.guard(a+b)

    def mul(self, a, b):
        self.guard(a)
        self.guard(b)
        if a.bit_length()+b.bit_length() > self.bits:
            raise ArithmeticUnresolved('mixture product may exceed its integer work limit')
        return self.guard(a*b)

    def divide(self, a, b, *, exact=False):
        self.guard(a)
        self.guard(b)
        if not b:
            raise ContractError('zero mixture divisor')
        value, remainder = divmod(a, b)
        if exact and remainder:
            raise ContractError('registered mixture weight lost its exact divisibility')
        return self.guard(value)

    def dyadic(self, exponent):
        natural(exponent, 'mixture dyadic exponent')
        if exponent >= self.bits:
            raise ArithmeticUnresolved('mixture dyadic extent exceeds its integer work limit')
        return 1 << exponent


def _declaration(rule):
    if type(rule) is not ArcsinePersistenceRule:
        raise ContractError('exact immutable arcsine persistence declaration required')


def _readout(numbers, grid, arith):
    """Stream dyadic integral weights; no weight table or symbolic cache."""
    t = len(numbers)-1
    denominator = arith.dyadic(grid+2*t)
    weight = 1
    for j in range(1, t+1):
        weight = arith.divide(arith.mul(weight, 2*(2*j-1)), j, exact=True)
    total = 0
    for k, value in enumerate(numbers):
        total = arith.add(total, arith.mul(value, weight))
        if k < t:
            weight = arith.divide(arith.mul(weight, 2*k+1), 2*(t-k)-1, exact=True)
    result = F(total, denominator)
    _guard(result, bit_limit=arith.bits)
    return result


def initial_coefficients(rule, *, bit_limit):
    _declaration(rule)
    arith = _Integers(bit_limit)
    return (arith.dyadic(rule.coefficient_grid_bits),)


def next_mixture(numbers, wealth, gain_lower, epochs, rule, *, bit_limit):
    """One closed epoch. Caller must prepay step_work and own both outputs."""
    _declaration(rule)
    natural(epochs, 'completed evidence epochs')
    if epochs >= rule.max_epochs:
        raise ContractError('registered mixture horizon already ended')
    if type(numbers) is not tuple or len(numbers) != epochs+1:
        raise ContractError('mixture lost its complete coefficient state')
    if type(wealth) is not F or type(gain_lower) is not F:
        raise ContractError('exact owned wealth and score required')
    arith = _Integers(bit_limit)
    initial = arith.dyadic(rule.coefficient_grid_bits)
    for value in numbers:
        arith.guard(value)
    if numbers[0] != initial:
        raise ContractError('mixture lost its unit starting coefficient')
    _guard(wealth, gain_lower, rule.bound, rule.alpha, bit_limit=bit_limit)
    if _readout(numbers, rule.coefficient_grid_bits, arith) != wealth:
        raise ContractError('mixture coefficients and retained wealth disagree')
    if threshold_crossed(wealth, rule.alpha, bit_limit=bit_limit):
        raise ContractError('a crossed mixture identity must stop before another update')
    normalized = _operation(gain_lower, F(rule.bound.denominator, rule.bound.numerator),
                            multiply=True, bit_limit=bit_limit)
    if not -1 <= normalized <= 1:
        raise ContractError('mixture score lies outside its proved common bound')
    z = _operation(F(1), normalized, multiply=False, bit_limit=bit_limit)
    following = [initial]
    for k in range(1, len(numbers)+1):
        product = arith.mul(z.numerator, numbers[k-1])
        weighted = arith.divide(product, z.denominator)
        following.append(arith.add(numbers[k] if k < len(numbers) else 0, weighted))
    following = tuple(following)
    return following, _readout(following, rule.coefficient_grid_bits, arith)
