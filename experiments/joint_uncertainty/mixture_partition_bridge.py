"""Positive joint-noise partitions and a complete scalar mixed-precision basis.

Passive algorithm/rounding research. Counts encode the original native
parameters; no posterior-valued source, Runtime backend or device authority.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import combinations
from math import lcm
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).parent)]
from fp_reference.core import ContractError
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference.positive_tape import compile_tape
from fp_reference import indexed_amp as amp
from shared_noise_factor_closure import Arithmetic

BITS = 32768
IDENTITY = 'joint-noise-integer-excess-half-mantissas-single-readout-v1'


def require(condition, message):
    if not condition:
        raise ContractError(message)


@dataclass(frozen=True)
class Model:
    n: int
    rates: tuple
    prior: tuple

    def __post_init__(self):
        require(type(self.n) is int and 2 <= self.n <= 1024, 'declared finite vertex count required')
        require(type(self.rates) is tuple and type(self.prior) is tuple
                and len(self.rates) == len(self.prior) and bool(self.rates), 'complete ordered noise bank required')
        require(all(type(v) is F for v in self.rates+self.prior), 'exact rational model data required')
        require(len(set(self.rates)) == len(self.rates) and all(0 < v < F(1, 2) for v in self.rates),
                'distinct positive sub-half rates required')
        require(min(self.prior) > 0 and sum(self.prior) == 1, 'positive normalized rate prior required')
        require(self.scale <= 1 << 24, 'this scalar schedule requires exact binary32 integer coefficients')

    @property
    def scale(self):
        return lcm(*(eta.denominator for eta in self.rates))

    @property
    def prior_scale(self):
        return lcm(*(pi.denominator for pi in self.prior))

    @property
    def edges(self):
        return tuple(combinations(range(self.n), 2))

    def query(self, query):
        require(type(query) is tuple and len(query) == 2 and
                all(type(v) is int and 0 <= v < self.n for v in query), 'complete ordered pair required')


@dataclass(frozen=True)
class State:
    model: Model
    counts: tuple
    diagonal: int = 0
    cursor: int = 0
    steps: int = 0
    pending: tuple | None = None

    def __post_init__(self):
        require(type(self.model) is Model, 'complete declared model required')
        require(type(self.counts) is tuple and len(self.counts) == len(self.model.edges)
                and all(type(v) is int for v in self.counts), 'all signed count coordinates required')
        require(all(type(v) is int for v in (self.diagonal, self.cursor, self.steps))
                and min(self.cursor, self.steps) >= 0, 'exact clocks and diagonal evidence required')
        height = sum(map(abs, self.counts))
        require(height+abs(self.diagonal) <= self.steps and (self.steps-height-self.diagonal) % 2 == 0,
                'counts and actual optimizer-step clock are inconsistent')
        if self.pending is not None:
            require(type(self.pending) is tuple and len(self.pending) == 3, 'complete pending event required')
            self.model.query(self.pending[:2])
            require(type(self.pending[2]) is int and self.pending[2] in (0, 1), 'binary actual target required')


def initialize(model, birth=0):
    return State(model, (0,)*len(model.edges), cursor=birth)


def observe(before, query, target):
    require(type(before) is State and before.pending is None, 'complete committed predecessor required')
    before.model.query(query)
    require(type(target) is int and target in (0, 1), 'independently supplied binary target required')
    return replace(before, cursor=before.cursor+1, pending=(*query, target))


def commit(observed):
    require(type(observed) is State and observed.pending is not None, 'complete observed predecessor required')
    i, j, y = observed.pending
    signed = list(observed.counts)
    diagonal = observed.diagonal
    if i == j:
        diagonal += 1-2*y
    else:
        signed[observed.model.edges.index(tuple(sorted((i, j))))] += 1-2*y
    return replace(observed, counts=tuple(signed), diagonal=diagonal, steps=observed.steps+1, pending=None)


def attach(before, cursor):
    require(type(before) is State and before.pending is None, 'attachment requires an empty update unit')
    return replace(before, cursor=cursor)


@dataclass(frozen=True)
class Plan:
    before: State
    query: tuple
    order: tuple
    rate_parts: tuple
    excess_parts: tuple
    normalization: int
    coefficients: tuple
    integer_envelope: int
    shape: tuple
    integer_stats: tuple
    tape_nodes: int
    reference_bits: int

    @property
    def output_cells(self):
        return 21+4*sum(bool(v) for v in self.excess_parts)


def prepare(before, query, *, budget=DecodeAllowance(), order=None, tape_cap=262144):
    require(type(before) is State and before.pending is None, 'complete committed predecessor required')
    before.__post_init__()
    require(type(budget) is DecodeAllowance, 'declared passive work/cell/bit limits required')
    budget.__post_init__()
    model, n = before.model, before.model.n
    model.query(query)
    require(type(tape_cap) is int and tape_cap > 0, 'positive tape-node allowance required')
    scale = model.scale
    envelope = n+model.prior_scale.bit_length()+(before.steps+1)*(scale-1).bit_length()
    if max(envelope+1024, 1075) > budget.integer_bits:
        raise ArithmeticUnresolved('joint integer construction or scalar-rounding envelope exceeds its allowance')
    support = tuple(e for e, d in zip(model.edges, before.counts) if d)
    active = tuple(d for d in before.counts if d)
    order = tuple(range(n-1)) if order is None else order
    shape = partition_shape_plan(n, support, query, order, budget)
    nodes = 2+sum(2 if u == 0 else 4 for u, _ in support)+shape['positive_multiplications']+shape['positive_additions']
    if nodes > tape_cap:
        raise ArithmeticUnresolved('positive joint tape exceeds its declared node allowance')
    height = sum(map(abs, active))
    A, B = (before.steps+before.diagonal-height)//2, (before.steps-before.diagonal-height)//2
    power_work = lambda exponent: exponent.bit_count()+exponent.bit_length()-1 if exponent else 0
    multiplications = len(model.rates)*(shape['positive_multiplications']
        +2*sum(power_work(abs(d)) for d in active)+power_work(A)+power_work(B)+8)
    additions = len(model.rates)*(shape['positive_additions']+5)
    if multiplications+additions > budget.arithmetic:
        raise ArithmeticUnresolved('whole joint positive integer evaluation exceeds its operation allowance')
    # Every structural/counter envelope is checked before powers and tables.
    tape, heads = compile_tape(n, support, query, order=order, readout=False)
    assert len(tape.nodes) == nodes
    arithmetic = Arithmetic(envelope)
    rate_parts, coefficients = [], []
    for eta, pi in zip(model.rates, model.prior):
        a, b = int(scale*eta), int(scale*(1-eta))
        factors = tuple((arithmetic.power(b, abs(d)), arithmetic.power(a, abs(d))) if d > 0
                        else (arithmetic.power(a, abs(d)), arithmetic.power(b, abs(d))) for d in active)
        # The old geometry module's unused 'nine' sentinel has no role here.
        values = [0, 1, None]
        for tag, *args in tape.nodes[3:]:
            if tag == 'factor':
                edge, parity = args
                value = factors[edge][parity]
            else:
                left, right = (values[i] for i in args)
                assert left is not None and right is not None and tag in ('add', 'mul')
                value = arithmetic.add(left, right) if tag == 'add' else arithmetic.mul(left, right)
            values.append(value)
        constant = arithmetic.mul(int(pi*model.prior_scale), arithmetic.mul(
            arithmetic.power(b, A), arithmetic.power(a, B)))
        rate_parts.append(tuple(arithmetic.mul(constant, values[h]) for h in heads))
        coefficients.append((b-1, a-1))  # Native matching, mismatching feature values.
    excess, normalization = [0, 0], 0
    for (z0, z1), (matching, mismatching) in zip(rate_parts, coefficients):
        normalization = arithmetic.add(normalization, arithmetic.add(z0, z1))
        excess[0] = arithmetic.add(excess[0], arithmetic.add(arithmetic.mul(matching, z0), arithmetic.mul(mismatching, z1)))
        excess[1] = arithmetic.add(excess[1], arithmetic.add(arithmetic.mul(mismatching, z0), arithmetic.mul(matching, z1)))
    assert sum(excess) == (scale-2)*normalization and normalization > 0
    assert (arithmetic.multiplies, arithmetic.adds) == (multiplications, additions)
    stats = {'positive_multiplications': arithmetic.multiplies, 'positive_additions': arithmetic.adds,
             'maximum_integer_bits': arithmetic.largest}
    return Plan(before, query, order, tuple(rate_parts), tuple(excess), normalization,
                tuple(coefficients), envelope, tuple(shape.items()), tuple(stats.items()), nodes, budget.integer_bits)


def reference(plan):
    excess = tuple(F(v, plan.normalization) for v in plan.excess_parts)
    masses = tuple(1+v for v in excess)
    total = F(plan.before.model.scale)
    assert sum(masses) == total
    return excess+masses+(total,)+tuple(m/total for m in masses)


def weight(plan, rate, world):
    """Point decoder; logical exact coordinates are not floating master slots."""
    model = plan.before.model
    require(type(rate) is int and 0 <= rate < len(model.rates), 'declared rate index required')
    require(type(world) is tuple and len(world) == model.n and world[0] == 0
            and all(type(v) is int and v in (0, 1) for v in world), 'anchored native world required')
    score = plan.before.diagonal+sum(d*(1-2*(world[i]^world[j])) for (i, j), d in zip(model.edges, plan.before.counts))
    matches = (plan.before.steps+score)//2
    assert 2*matches == plan.before.steps+score and 0 <= matches <= plan.before.steps
    eta = model.rates[rate]
    raw = int(model.prior[rate]*model.prior_scale)*int(model.scale*(1-eta))**matches*int(model.scale*eta)**(plan.before.steps-matches)
    return F(raw, plan.normalization)


def prediction_schedule(plan, arithmetic):
    require(arithmetic.bits == plan.reference_bits, 'scalar reference precision differs from the plan')
    common = max(v.bit_length() for v in plan.excess_parts)
    scaled = []
    for value in plan.excess_parts:
        if not value:
            scaled.append(arithmetic.op('constant', constant=0))
            continue
        bits = value.bit_length()
        mantissa = arithmetic.op('constant', constant=F(value, 1 << bits))
        quantized = arithmetic.op('cast', arithmetic.op('cast', mantissa, half=True))
        power = F(0) if bits-common < -149 else F(1, 1 << (common-bits))
        scaled.append(arithmetic.op('mul', quantized, arithmetic.op('constant', constant=power)))
    total = arithmetic.op('add', *scaled)
    fractions = tuple(arithmetic.op('div', v, total) for v in scaled)
    one, excess_scale = (arithmetic.op('constant', constant=v) for v in (1, plan.before.model.scale-2))
    excess = tuple(arithmetic.op('mul', excess_scale, q) for q in fractions)
    masses = tuple(arithmetic.op('add', one, v) for v in excess)
    normalizer = arithmetic.op('add', *masses)
    probabilities = tuple(arithmetic.op('div', v, normalizer) for v in masses)
    columns = excess+masses+(normalizer,)+probabilities
    return columns, arithmetic.stack(columns)


def observation_schedule(plan, prediction, target, arithmetic):
    require(arithmetic.bits == plan.reference_bits, 'scalar reference precision differs from the plan')
    require(type(target) is int and target in (0, 1), 'independent actual target required')
    scale = plan.before.model.scale
    one, common, fixed_constant = (arithmetic.op('constant', constant=v)
                                  for v in (1, F(scale-2, scale), F(-2, scale)))
    reciprocal = arithmetic.op('div', one, prediction[2+target])
    fixed = arithmetic.op('add', reciprocal, fixed_constant)
    gradients = tuple(arithmetic.op('add', common, arithmetic.op('mul', reciprocal,
                      arithmetic.op('constant', constant=-coefficient)))
                      for row in plan.coefficients for coefficient in row)
    columns = (fixed,)+gradients
    return columns, arithmetic.stack(columns)


def rounded(plan, target=None, *, prediction_output_cap=65536, observation_output_cap=65536):
    if target is not None:
        require(type(target) is int and target in (0, 1), 'independent actual binary target required')
    require(all(type(v) is int and v > 0 for v in (prediction_output_cap, observation_output_cap)),
            'declared floating output allowances required')
    if plan.output_cells > prediction_output_cap or (target is not None and
            6+8*len(plan.before.model.rates) > observation_output_cap):
        raise ArithmeticUnresolved('joint scalar schedule exceeds its declared output allowance')
    arithmetic = amp._Arithmetic(plan.reference_bits)
    prediction, _ = prediction_schedule(plan, arithmetic)
    assert len(arithmetic.trace)+7 == plan.output_cells
    traces = [tuple(arithmetic.trace)]
    gradient = None
    if target is not None:
        arithmetic = amp._Arithmetic(plan.reference_bits)
        gradient, _ = observation_schedule(plan, prediction, target, arithmetic)
        assert len(arithmetic.trace)+len(gradient) == 6+8*len(plan.before.model.rates)
        traces.append(tuple(arithmetic.trace))
    return prediction, gradient, tuple(traces)


def gradient_reference(plan, target):
    mass = reference(plan)[2+target]
    scale = plan.before.model.scale
    return (1/mass-F(2, scale),)+tuple(F(scale-2, scale)-c/mass for row in plan.coefficients for c in row)


def errors(plan, prediction, gradient, target):
    exact = reference(plan)
    values = tuple(v.value for v in prediction)
    stored = sum(values[2:4])
    result = {'native': max(abs(a-b) for a, b in zip(exact[:4], values[:4])),
              'normalizer': max(abs(exact[4]-values[4]), abs(exact[4]-stored), abs(values[4]-stored)),
              'probability': max(abs(exact[5+y]-p) for y in (0, 1)
                                 for p in (values[5+y], values[2+y]/stored)),
              'proper_mass_division': max(abs(values[2+y]/stored-values[5+y]) for y in (0, 1)),
              'gradient': max(abs(a-b.value) for a, b in zip(gradient_reference(plan, target), gradient))}
    return result


def precision_bound(scale):
    require(type(scale) is int and 3 <= scale <= 1 << 24, 'exact binary32 native scale required')
    a = scale-2
    u, v, tau = F(1, 1 << 24), F(1, 1 << 11), F(1, 1 << 150)
    epsilon = (1+u)*(1+v)-1
    tail = 4*tau
    A, B = 2*epsilon/(1-epsilon-tail), tail/(1-epsilon-tail)
    D = A/4+B
    kappa = 2*u/(1-u)
    R = a*(kappa+tau)+(2*a+1)*u+2*tau
    if 1-a*D <= 0 or scale-2*R <= 0:
        raise ArithmeticUnresolved('this sufficient all-gradient bound does not resolve the declared native scale')
    rounding = (3*a+1)*u+a*u*u+(a*(1+u)+2)*tau
    return {'native': a*D+R, 'normalizer': 2*R+2*(a+1)*u,
            'probability': F(a, scale)*D+R/(scale-2*R)+kappa+tau,
            'proper_mass_division': kappa+tau,
            'gradient': a*a*(A/F(4*(a+1))+B)/(1-a*D)+a*R+rounding}


def check_observation_binding(plan, actual_before, query, target, actual_observed):
    """Passive discrete relation: an output cannot certify its own target."""
    require(plan.before == actual_before and plan.query == query, 'predecessor or ordered source query was substituted')
    require(actual_observed == observe(actual_before, query, target), 'actual observed complete state differs')
