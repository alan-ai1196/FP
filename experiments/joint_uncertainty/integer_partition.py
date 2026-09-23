"""Passive exact integer partitions with half mantissas and single readout.

All elimination is paid exact-integer host work in any eventual realization.
This prototype has no Runtime authority, resource ownership or CUDA evidence.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.core import ContractError, natural
from fp_reference.indexed_count import CountState, query as require_query
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference.indexed_execution import IndexedEvaluation
from fp_reference import indexed_amp as amp
from fp_reference.semantics import ArithmeticUnresolved, _guard


@dataclass(frozen=True)
class Plan:
    before: CountState
    query: tuple
    order: tuple
    span: int
    integer_envelope: int
    parts: tuple
    shape: tuple
    maximum_integer_bits: int

    @property
    def output_cells(self):
        return 21+4*sum(bool(value) for value in self.parts)


def prepare(before, query, *, budget=DecodeAllowance(), order=None, span_cap=396):
    if type(before) is not CountState or type(budget) is not DecodeAllowance:
        raise ContractError('complete count state and decoder allowance required')
    before.__post_init__()
    budget.__post_init__()
    if before.pending is not None or type(query) is not tuple or len(query) != 2:
        raise ContractError('committed predecessor and ordered query required')
    require_query(before.n, *query)
    natural(span_cap, 'direct partition span allowance')
    n, counts = before.n, before.counts
    height = sum(map(abs, counts))
    if height > span_cap:
        raise ArithmeticUnresolved('direct partition span allowance insufficient')
    envelope = n+4*height
    if max(envelope, 16*height+8*n+1024) > budget.integer_bits:
        raise ArithmeticUnresolved('direct partition/readout integer allowance insufficient')
    order = tuple(range(n-1)) if order is None else order
    support = tuple(edge for edge, count in zip(combinations(range(n), 2), counts) if count)
    shape = partition_shape_plan(n, support, query, order, budget)
    parts, statistics, maximum = _eliminate(n, counts, query, order, envelope)
    assert statistics == shape and sum(parts) > 0
    return Plan(before, query, order, height, envelope, parts, tuple(shape.items()), maximum)

def _eliminate(n, counts, query, order, envelope):
    factors = []
    maximum = 1
    multiply = add = 0

    def guard(value):
        nonlocal maximum
        maximum = max(maximum, value.bit_length())
        if maximum > envelope:
            raise ArithmeticUnresolved('direct partition integer escaped its proved bit envelope')
        return value

    for (i, j), count in zip(combinations(range(n), 2), counts):
        if not count:
            continue
        scope = tuple(v for v in (i, j) if v)
        scale = guard(9**abs(count))
        table = []
        for word in range(1 << len(scope)):
            values = {v: (word >> k) & 1 for k, v in enumerate(scope)}
            parity = values.get(i, 0) ^ values.get(j, 0)
            table.append(scale if parity == int(count < 0) else 1)
        factors.append((scope, tuple(table)))
    peak_join, peak_live = 1, sum(len(table) for _, table in factors)

    def join(items, scope):
        nonlocal multiply, peak_join
        positions = {v: k for k, v in enumerate(scope)}
        projections = [tuple(positions[v] for v in fs) for fs, _ in items]
        table = []
        for word in range(1 << len(scope)):
            value = 1
            for (_, values), indices in zip(items, projections):
                index = sum(((word >> p) & 1) << k for k, p in enumerate(indices))
                value = guard(value*values[index])
                multiply += 1
            table.append(value)
        peak_join = max(peak_join, len(table))
        return tuple(table)

    kept = tuple(sorted({v for v in query if v}))
    for zero_based in order:
        v = zero_based+1
        if v in kept:
            continue
        bucket = [item for item in factors if v in item[0]]
        rest = [item for item in factors if v not in item[0]]
        scope = tuple(sorted({v}.union(*(set(s) for s, _ in bucket))))
        joined = join(bucket, scope)
        out_scope = tuple(u for u in scope if u != v)
        position = scope.index(v)
        out = []
        for word in range(1 << len(out_scope)):
            low = word & ((1 << position)-1)
            index = low | ((word >> position) << (position+1))
            out.append(guard(joined[index]+joined[index | (1 << position)]))
            add += 1
        peak_live = max(peak_live, sum(len(t) for _, t in factors)+len(joined)+len(out))
        factors = rest+[(out_scope, tuple(out))]
    final = join(factors, kept)
    peak_live = max(peak_live, sum(len(t) for _, t in factors)+len(final))
    packed = [0, 0]
    for word, value in enumerate(final):
        values = {v: (word >> k) & 1 for k, v in enumerate(kept)}
        parity = values.get(query[0], 0) ^ values.get(query[1], 0)
        packed[parity] = guard(packed[parity]+value)
        add += 1
    guard(sum(packed))
    add += 1
    return tuple(packed), {'positive_multiplications': multiply, 'positive_additions': add,
        'largest_join_cells': peak_join, 'peak_live_integer_cells': peak_live}, maximum



def reference(plan, bit_limit=32768):
    excesses = tuple(F(8*z, sum(plan.parts)) for z in plan.parts)
    masses = tuple(1+v for v in excesses)
    probabilities = tuple(v/10 for v in masses)
    _guard(*excesses, *masses, *probabilities, F(10), bit_limit=bit_limit)
    return IndexedEvaluation(plan.before, plan.query, excesses, masses, F(10),
                             probabilities, plan.shape)


def schedule(plan, arithmetic):
    # This receives partitions independently computed from this path's counts.
    # It does not receive a reference cache or a normalized reference forecast.
    common = max(value.bit_length() for value in plan.parts)
    scaled = []
    for value in plan.parts:
        if value == 0:
            scaled.append(arithmetic.op('constant', constant=0))
            continue
        bits = value.bit_length()
        mantissa = arithmetic.op('constant', constant=F(value, 1 << bits))
        quantized = arithmetic.op('cast', arithmetic.op('cast', mantissa, half=True))
        exponent = bits-common
        power = F(0) if exponent < -149 else F(1, 1 << -exponent)
        scaled.append(arithmetic.op('mul', quantized, arithmetic.op('constant', constant=power)))
    denominator = arithmetic.op('add', *scaled)
    marginals = tuple(arithmetic.op('div', value, denominator) for value in scaled)
    one, eight = (arithmetic.op('constant', constant=value) for value in (1, 8))
    excesses = tuple(arithmetic.op('mul', eight, value) for value in marginals)
    masses = tuple(arithmetic.op('add', one, value) for value in excesses)
    normalizer = arithmetic.op('add', *masses)
    probabilities = tuple(arithmetic.op('div', value, normalizer) for value in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    output = arithmetic.stack(columns)
    raw = amp.IndexedAmpPrediction(plan.before, plan.query, tuple(v.word for v in columns))
    return raw, None if output is None else amp.ResidentPrediction(plan.before, plan.query, output)


def rounded_prediction(plan, *, output_cap=65536, bit_limit=32768):
    natural(output_cap, 'direct partition floating output allowance')
    if plan.output_cells > output_cap:
        raise ArithmeticUnresolved('direct partition floating output allowance insufficient')
    arithmetic = amp._Arithmetic(bit_limit)
    raw, _ = schedule(plan, arithmetic)
    assert len(arithmetic.trace)+7 == plan.output_cells
    assert sum(width == 16 for _, width, _ in arithmetic.trace) == sum(bool(v) for v in plan.parts)
    return raw, tuple(arithmetic.trace)


def precision_bound():
    u, v, tau = F(1, 1 << 24), F(1, 1 << 11), F(1, 1 << 150)
    epsilon = (1+v)*(1+u)-1
    eta = 4*tau
    A, B = 2*epsilon/(1-epsilon-eta), eta/(1-epsilon-eta)
    D = A/4+B
    kappa = 2*u/(1-u)
    R = 8*(kappa+tau)+9*u
    assert 1-epsilon-eta > 0 and 1-8*D > 0
    return {'epsilon': epsilon, 'underflow': eta,
        'native': 8*D+R, 'normalizer': 2*R+18*u,
        'probability': F(4, 5)*D+R/(10-2*R)+kappa+tau,
        'proper_mass_division': kappa+tau,
        'gradient': 64*(A/36+B)/(1-8*D)+8*R+18*u}
