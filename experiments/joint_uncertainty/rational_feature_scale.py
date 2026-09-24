"""Passive native rational-feature construction and complete rounding basis.

The likelihood integer scale and the native head scale are distinct. This
defines a different G/Gamma, not a quotient of the existing integer-copy bank.
No Runtime registration, device execution or constructor certificate follows.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from math import ceil, lcm
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference.core import ContractError
from fp_reference.learner import LearnerSpec, SIMPLEX_GRADIENT
from fp_reference.program import Program, Product, Source, SourceSpec, SemanticRules, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference import indexed_amp as scalar
import mixture_partition_bridge as old

BITS = 32768


@dataclass(frozen=True)
class Bank:
    n: int
    rates: tuple
    prior: tuple
    native_scale: F

    def __post_init__(self):
        if (type(self.n) is not int or self.n < 2 or type(self.rates) is not tuple
                or type(self.prior) is not tuple or not self.rates or len(self.rates) != len(self.prior)
                or any(type(v) is not F for v in self.rates+self.prior+(self.native_scale,))
                or len(set(self.rates)) != len(self.rates) or not all(0 < r < F(1, 2) for r in self.rates)
                or min(self.prior) <= 0 or sum(self.prior) != 1
                or self.native_scale*min(self.rates) < 1):
            raise ContractError('complete positive bank and base-one admissible native scale required')

    @property
    def likelihood_scale(self):
        return lcm(*(r.denominator for r in self.rates))

    @property
    def coefficients(self):
        return tuple((self.native_scale*(1-r)-1, self.native_scale*r-1) for r in self.rates)

    @property
    def fixed(self):
        return tuple(c for row in self.coefficients for c in row)


def minimum_integer_bank(n, rates, prior):
    return Bank(n, rates, prior, F(ceil(1/min(rates))))


def native_graph(bank, *, world_cap=4096):
    count = len(bank.rates)*(1 << (bank.n-1))
    if type(world_cap) is not int or world_cap < 1 or count > world_cap:
        raise ArithmeticUnresolved('passive literal materialization exceeds the declared world cap')
    n, fixed_count = bank.n, 2*len(bank.rates)
    worlds = tuple((j, (0,)+tail) for j in range(len(bank.rates)) for tail in product((0, 1), repeat=n-1))
    sources = tuple(SourceSpec(f'x{side}:{i}', 'mass', 0, F(1)) for side in (0, 1) for i in range(n))
    rules = SemanticRules(sources, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source(s.source_id) for s in sources]
    nodes += [Product('mass', u, n+v) for u, v in product(range(n), repeat=2)]
    start = len(nodes)
    nodes += [Sum('mass', tuple(Term(2*n+u*n+v, 2*j+int((z[u]^z[v]) != y))
                              for u, v in product(range(n), repeat=2))) for j, z in worlds for y in (0, 1)]
    heads = (len(nodes), len(nodes)+1)
    nodes += [Sum('mass', tuple(Term(start+2*k+y, fixed_count+k) for k in range(count))) for y in (0, 1)]
    graph = Program(tuple(nodes), fixed_count+count, heads)
    graph.validate(rules)
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                       simplex_slots=tuple(range(fixed_count, graph.slot_count)))
    theta = bank.fixed+tuple(bank.prior[j]/(1 << (n-1)) for j, _ in worlds)
    return rules, graph, spec, theta, worlds


def parts_total(bank, parts):
    """Validate integer data without invoking a reference forecast/gradient."""
    if (type(bank) is not Bank or type(parts) is not tuple or len(parts) != len(bank.rates)
            or any(type(row) is not tuple or len(row) != 2 for row in parts)
            or any(type(v) is not int or v < 0 for row in parts for v in row)):
        raise ContractError('complete nonnegative joint integer parts required')
    total = sum(map(sum, parts))
    if not total:
        raise ContractError('positive joint integer normalization required')
    return total


def reference(bank, parts):
    """All rate/parity parts include their actual joint prior and evidence."""
    total = parts_total(bank, parts)
    excess = tuple(sum(F(row[y]*c[0]+row[1-y]*c[1], total)
                       for row, c in zip(parts, bank.coefficients)) for y in (0, 1))
    masses = tuple(1+v for v in excess)
    assert sum(masses) == bank.native_scale
    return excess+masses+(bank.native_scale,)+tuple(v/bank.native_scale for v in masses)


def gradient_basis(bank, parts, target):
    if type(target) is not int or target not in (0, 1):
        raise ContractError('actual binary target required')
    mass, scale = reference(bank, parts)[2+target], bank.native_scale
    total = sum(map(sum, parts))
    fixed = tuple(F(sum(row), total)/scale-F(row[y], total)/mass
                  for row in parts for y in (target, 1-target))
    selected = tuple((scale-2)/scale-c/mass for row in bank.coefficients for c in row)
    return fixed+selected


def excess_integers(bank, parts):
    total = parts_total(bank, parts)
    scale = bank.native_scale
    if scale.denominator != 1 or not 3 <= scale <= 1 << 24:
        raise ArithmeticUnresolved('this passive floating schedule needs an exact binary32 integer native scale')
    C, S = int(scale), bank.likelihood_scale
    coefficients = tuple((C*int(S*(1-r))-S, C*int(S*r)-S) for r in bank.rates)
    assert min(c for row in coefficients for c in row) >= 0
    excess = tuple(sum(c[0]*row[y]+c[1]*row[1-y] for row, c in zip(parts, coefficients)) for y in (0, 1))
    assert sum(excess) == (C-2)*S*total
    return excess


def prediction_schedule(bank, parts, arithmetic):
    excess = excess_integers(bank, parts)
    common = max(v.bit_length() for v in excess)
    scaled = []
    for value in excess:
        if not value:
            scaled.append(arithmetic.op('constant', constant=0))
            continue
        bits = value.bit_length()
        mantissa = arithmetic.op('constant', constant=F(value, 1 << bits))
        half = arithmetic.op('cast', mantissa, half=True)
        power = F(0) if bits-common < -149 else F(1, 1 << (common-bits))
        scaled.append(arithmetic.op('mul', arithmetic.op('cast', half), arithmetic.op('constant', constant=power)))
    total = arithmetic.op('add', *scaled)
    fractions = tuple(arithmetic.op('div', v, total) for v in scaled)
    one, amount = (arithmetic.op('constant', constant=v) for v in (1, bank.native_scale-2))
    heads = tuple(arithmetic.op('mul', amount, v) for v in fractions)
    masses = tuple(arithmetic.op('add', one, v) for v in heads)
    normalizer = arithmetic.op('add', *masses)
    probabilities = tuple(arithmetic.op('div', v, normalizer) for v in masses)
    return heads+masses+(normalizer,)+probabilities


def observation_schedule(bank, parts, prediction, target, arithmetic):
    total = parts_total(bank, parts)
    if type(target) is not int or target not in (0, 1):
        raise ContractError('actual binary target required')
    scale = bank.native_scale
    one, common, inverse_scale, negative = (arithmetic.op('constant', constant=v)
        for v in (1, (scale-2)/scale, 1/scale, -1))
    inverse_mass = arithmetic.op('div', one, prediction[2+target])
    total_bits = total.bit_length()
    denominator = arithmetic.op('constant', constant=F(total, 1 << total_bits))

    def fraction(numerator):
        if not numerator:
            return arithmetic.op('constant', constant=0)
        bits = numerator.bit_length()
        mantissa = arithmetic.op('constant', constant=F(numerator, 1 << bits))
        quotient = arithmetic.op('div', mantissa, denominator)
        power = F(0) if bits-total_bits < -149 else F(1, 1 << (total_bits-bits))
        return arithmetic.op('mul', quotient, arithmetic.op('constant', constant=power))

    fixed = []
    for row in parts:
        marginal = fraction(sum(row))
        first = arithmetic.op('mul', marginal, inverse_scale)
        for y in (target, 1-target):
            match = fraction(row[y])
            second = arithmetic.op('mul', match, inverse_mass)
            fixed.append(arithmetic.op('add', first, arithmetic.op('mul', negative, second)))
    selected = tuple(arithmetic.op('add', common, arithmetic.op('mul', inverse_mass,
                      arithmetic.op('constant', constant=-coefficient)))
                     for row in bank.coefficients for coefficient in row)
    return tuple(fixed)+selected


def rounded(bank, parts, target):
    prediction_ops = scalar._Arithmetic(BITS)
    prediction = prediction_schedule(bank, parts, prediction_ops)
    gradient_ops = scalar._Arithmetic(BITS)
    gradient = observation_schedule(bank, parts, prediction, target, gradient_ops)
    return prediction, gradient, (tuple(prediction_ops.trace), tuple(gradient_ops.trace))


def errors(bank, parts, prediction, gradient, target):
    exact, basis = reference(bank, parts), gradient_basis(bank, parts, target)
    actual = tuple(v.value for v in prediction)
    gradients = tuple(v.value for v in gradient)
    J, stored = len(bank.rates), sum(actual[2:4])
    return dict(native=max(abs(a-b) for a, b in zip(exact[:4], actual[:4])),
        normalizer=max(abs(exact[4]-actual[4]), abs(exact[4]-stored), abs(actual[4]-stored)),
        probability=max(abs(exact[5+y]-v) for y in (0, 1) for v in (actual[5+y], actual[2+y]/stored)),
        proper_mass_division=max(abs(actual[5+y]-actual[2+y]/stored) for y in (0, 1)),
        fixed_gradient=max(abs(a-b) for a, b in zip(basis[:2*J], gradients[:2*J])),
        selected_gradient=max(abs(a-b) for a, b in zip(basis[2*J:], gradients[2*J:])))


def precision_bound(C):
    """All-history bounds conditional on exact parts and this RNE schedule."""
    base = old.precision_bound(C)
    a, u, tau = C-2, F(1, 1 << 24), F(1, 1 << 150)
    epsilon = (1+u)*(1+F(1, 1 << 11))-1
    D1, D0 = 2*epsilon/(1-epsilon-4*tau), 4*tau/(1-epsilon-4*tau)
    D = D1/4+D0
    R = a*(2*u/(1-u)+tau)+(2*a+1)*u+2*tau
    selected_rounding = (4*a+1)*u+3*tau
    fraction_error = (3*u+u*u)/(1-u)+2*tau
    fixed_rounding = (1+F(1, C))*(2*u+u*u)+u+3*tau
    return {k: v for k, v in base.items() if k != 'gradient'} | {
        'selected_gradient': a*a*(D1/(4*(a+1))+D0)/(1-a*D)+a*R+selected_rounding,
        'fixed_gradient': (1+F(1, C))*fraction_error+base['native']+fixed_rounding,
        'coefficient_cache': a*u+tau}
