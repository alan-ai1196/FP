"""Positive joint-noise elimination in one caller-owned integer extent.

All rates reuse the same live table region. Three separate root cells retain
the unnormalized joint excesses and normalization. Rational-feature programs
also retain every rate/parity root for their complete fixed gradients. No Runtime admission,
physical backend registration or device authority is provided here.
"""
from dataclasses import dataclass, fields
from fractions import Fraction as F
from itertools import combinations

from .core import ContractError, natural
from .indexed_relation import DecodeAllowance, partition_shape_plan
from .joint_relation import JointRelation, JointCountState, require_state
from .semantics import ArithmeticUnresolved, _guard

MAX_BITS, MAX_CELLS, MAX_ARITHMETIC = 32768, 32768, 2_000_000
WORKSPACE_KIND = 'joint_noise_integer_partition_workspace'


@dataclass(frozen=True)
class JointPartitionAllowance:
    join_cells: int = 4096
    live_cells: int = MAX_CELLS
    arithmetic: int = MAX_ARITHMETIC
    step_cap: int = 2000
    integer_bits: int = MAX_BITS

    def __post_init__(self):
        if set(vars(self)) != {f.name for f in fields(self)}:
            raise ContractError('unregistered joint partition allowance coordinate')
        for key in ('join_cells', 'live_cells', 'arithmetic', 'integer_bits'):
            natural(getattr(self, key), 'joint partition '+key, positive=True)
        natural(self.step_cap, 'joint partition committed-step allowance')
        if (max(self.join_cells, self.live_cells) > MAX_CELLS
                or self.arithmetic > MAX_ARITHMETIC or self.integer_bits > MAX_BITS
                or self.step_cap > MAX_BITS):
            raise ContractError('joint partition allowance exceeds its finite implementation class')


def _layout(model, budget):
    if type(model) is not JointRelation or type(budget) is not JointPartitionAllowance:
        raise ContractError('complete joint native description and decoder allowance required')
    model.__post_init__()
    budget.__post_init__()
    envelope = (model.n+model.prior_scale.bit_length()+(budget.step_cap+1)*(model.scale-1).bit_length()
                +model.partition_extra_bits)
    cell = (min(budget.integer_bits, envelope)+7)//8
    # Two reusable parity roots and three joint roots follow the shared tables.
    # Rational-feature gradients additionally need the 2J unnormalized parts.
    return cell, (budget.live_cells+5+_retained_parts(model))*cell


def _retained_parts(model):
    return 0 if model.feature_scale is None else 2*len(model.rates)


def workspace_bytes(model, budget):
    return _layout(model, budget)[1]


def construction_work(model, budget):
    """Conservative scalar/index/byte tariff, not bigint time or host memory.

    A future owner must debit this before preparation and fund the extent,
    metadata, output records, verification and failure lifetime separately.
    """
    cell, size = _layout(model, budget)
    n, j = model.n, len(model.rates)
    d = n*(n-1)//2
    return (64*(n+1)**2*(d+n+j+1)
            +32*(j*size+(budget.arithmetic+j*n*budget.live_cells+d+32)*(n+1+cell)))


@dataclass(frozen=True)
class JointPartitionPlan:
    before: JointCountState
    query: tuple[int, int]
    order: tuple[int, ...]
    excesses: tuple[int, int]
    normalization: int
    shape: tuple[tuple[str, int], ...]
    integer_envelope: int
    maximum_integer_bits: int
    multiplications: int
    additions: int
    compacted_cells: int
    cell_bytes: int
    workspace_bytes: int
    bit_limit: int
    rate_parts: tuple[tuple[int, int], ...] = ()

    @property
    def output_cells(self):
        return 21+4*sum(bool(v) for v in self.excesses)


def _preflight(state, query, budget, bit_limit, order):
    require_state(state)
    if state.pending is not None:
        raise ContractError('joint partition construction requires a committed predecessor')
    model = state.model
    model.query(query)
    _layout(model, budget)
    natural(bit_limit, 'joint reference arithmetic limit', positive=True)
    bits = min(bit_limit, budget.integer_bits)
    height = sum(map(abs, state.counts))
    envelope = (model.n+model.prior_scale.bit_length()+(state.steps+1)*(model.scale-1).bit_length()
                +model.partition_extra_bits)
    if state.steps > budget.step_cap:
        raise ArithmeticUnresolved('joint committed-step allowance exhausted; canceled evidence remains')
    if max(envelope+1024, 1075) > bits:
        raise ArithmeticUnresolved('joint integer or scalar-readout precision allowance exhausted')
    support = tuple(edge for edge, d in zip(combinations(range(model.n), 2), state.counts) if d)
    order = tuple(range(model.n-1)) if order is None else order
    shape = partition_shape_plan(model.n, support, query, order,
        DecodeAllowance(budget.join_cells, budget.live_cells, budget.arithmetic, bits))
    a, b = (state.steps+state.diagonal-height)//2, (state.steps-state.diagonal-height)//2
    power_work = lambda e: e.bit_count()+e.bit_length()-1 if e else 0
    multiplies = len(model.rates)*(shape['positive_multiplications']
        +2*sum(power_work(abs(d)) for d in state.counts)+power_work(a)+power_work(b)+8)
    # This engine also evaluates the per-rate raw partition sum; the passive
    # tape prototype omits that one addition and therefore has a different fee.
    adds = len(model.rates)*(shape['positive_additions']+6)
    if multiplies+adds > budget.arithmetic:
        raise ArithmeticUnresolved('whole joint powers/tables/aggregation exceed the arithmetic allowance')
    return envelope, bits, order, shape, (a, b), (multiplies, adds)


def prepare(state, query, budget, workspace, *, bit_limit=MAX_BITS, order=None):
    """Preflight before writes, then evaluate one rate at a time in-place.

    A table descriptor contains scope/start/length only. Every numeric table
    read and write goes through the supplied contiguous byte extent; wide
    values are never retained in a parallel tape-value array. Constant-count
    bigint temporaries and Python metadata still need whole-host accounting.
    """
    envelope, bits, order, expected_shape, (A, B), expected_ops = _preflight(
        state, query, budget, bit_limit, order)
    cell, size = _layout(state.model, budget)
    if (type(workspace) is not memoryview or workspace.readonly or workspace.ndim != 1
            or not workspace.c_contiguous or workspace.format != 'B' or len(workspace) != size):
        raise ContractError('complete writable contiguous joint integer byte extent required')
    roots = budget.live_cells
    root_cells = 5+_retained_parts(state.model)
    zero = bytes(4096)

    def clear(start, length):
        for offset in range(start, start+length, len(zero)):
            width = min(len(zero), start+length-offset)
            workspace[offset:offset+width] = zero[:width]

    clear(0, size)
    maximum = 1
    multiplies = adds = compacted = 0

    def guard(value):
        nonlocal maximum
        if type(value) is not int or value < 0:
            raise ContractError('positive joint integer coordinate required')
        maximum = max(maximum, value.bit_length())
        if maximum > envelope:
            raise ArithmeticUnresolved('joint integer exceeds its proved envelope')
        return value

    def mul(a, b):
        nonlocal multiplies
        multiplies += 1
        return guard(a*b)

    def add(a, b):
        nonlocal adds
        adds += 1
        return guard(a+b)

    def power(base, exponent):
        value = 1
        while exponent:
            if exponent & 1:
                value = mul(value, base)
            exponent >>= 1
            if exponent:
                base = mul(base, base)
        return value

    def get(index):
        if not 0 <= index < budget.live_cells+root_cells:
            raise ContractError('joint table read outside its supplied extent')
        start = index*cell
        return int.from_bytes(workspace[start:start+cell], 'little')

    def put(index, value):
        if not 0 <= index < budget.live_cells+root_cells:
            raise ContractError('joint table write outside its supplied extent')
        start = index*cell
        workspace[start:start+cell] = guard(value).to_bytes(cell, 'little')

    model, n = state.model, state.n
    kept = tuple(sorted({v for v in query if v}))
    for rate_index, (rate, prior) in enumerate(zip(model.rates, model.prior)):
        # Preserve the three accumulated joint roots; clear the reusable rate
        # tables and parity roots, including unused cells from the last rate.
        if rate_index:
            clear(0, (roots+2)*cell)
        a, b = int(model.scale*rate), int(model.scale*(1-rate))
        factors, live = [], 0
        for (i, j), count in zip(combinations(range(n), 2), state.counts):
            if not count:
                continue
            scope = tuple(v for v in (i, j) if v)
            length = 1 << len(scope)
            high, low = power(b, abs(count)), power(a, abs(count))
            for word in range(length):
                parity = (0 if i == 0 else word & 1) ^ ((word >> (len(scope)-1)) & 1)
                put(live+word, high if parity == int(count < 0) else low)
            factors.append((scope, live, length))
            live += length
        geometry_mul, geometry_add = multiplies, adds
        peak_join, peak_live = 1, live

        def join(items, scope, start):
            nonlocal peak_join
            length = 1 << len(scope)
            if start+length > budget.live_cells:
                raise ContractError('joint table escaped the complete geometry preflight')
            positions = {v: k for k, v in enumerate(scope)}
            projections = tuple(tuple(positions[v] for v in fs) for fs, _, _ in items)
            for word in range(length):
                value = 1
                for (_, source, _), indices in zip(items, projections):
                    index = sum(((word >> p) & 1) << k for k, p in enumerate(indices))
                    value = mul(value, get(source+index))
                put(start+word, value)
            peak_join = max(peak_join, length)
            return length

        for zero_based in order:
            vertex = zero_based+1
            if vertex in kept:
                continue
            bucket = [item for item in factors if vertex in item[0]]
            rest = [item for item in factors if vertex not in item[0]]
            scope = tuple(sorted({vertex}.union(*(set(s) for s, _, _ in bucket))))
            joined = join(bucket, scope, live)
            out_scope, out_start = tuple(v for v in scope if v != vertex), live+joined
            length, position = joined//2, scope.index(vertex)
            if out_start+length > budget.live_cells:
                raise ContractError('joint reduced table escaped its geometry preflight')
            for word in range(length):
                index = (word & ((1 << position)-1)) | ((word >> position) << (position+1))
                put(out_start+word, add(get(live+index), get(live+index+(1 << position))))
            peak_live = max(peak_live, out_start+length)
            factors, live = [], 0
            for fs, source, count in rest+[(out_scope, out_start, length)]:
                if live > source:
                    raise ContractError('joint compaction would overwrite unread table values')
                for k in range(count):
                    put(live+k, get(source+k))
                    compacted += 1
                factors.append((fs, live, count))
                live += count
        final = join(factors, kept, live)
        peak_live = max(peak_live, live+final)
        for word in range(final):
            values = {v: (word >> k) & 1 for k, v in enumerate(kept)}
            parity = values.get(query[0], 0)^values.get(query[1], 0)
            put(roots+parity, add(get(roots+parity), get(live+word)))
        add(get(roots), get(roots+1))
        actual_shape = {'positive_multiplications': multiplies-geometry_mul,
            'positive_additions': adds-geometry_add, 'largest_join_cells': peak_join,
            'peak_live_integer_cells': peak_live}
        if actual_shape != expected_shape:
            raise ContractError('joint table execution differs from its complete geometry')
        constant = mul(int(prior*model.prior_scale), mul(power(b, A), power(a, B)))
        z0, z1 = mul(constant, get(roots)), mul(constant, get(roots+1))
        if model.feature_scale is not None:
            put(roots+5+2*rate_index, z0)
            put(roots+6+2*rate_index, z1)
        matching, other = model.coefficient_integers(rate_index)
        put(roots+2, add(get(roots+2), add(mul(matching, z0), mul(other, z1))))
        put(roots+3, add(get(roots+3), add(mul(other, z0), mul(matching, z1))))
        put(roots+4, add(get(roots+4), add(z0, z1)))
    excesses, normalization = (get(roots+2), get(roots+3)), get(roots+4)
    if ((multiplies, adds) != expected_ops or compacted > len(model.rates)*(n-1)*budget.live_cells
            or normalization <= 0 or sum(excesses) != (model.native_scale-2)*model.excess_denominator*normalization):
        raise ContractError('joint positive execution lost its complete aggregation or resource binding')
    parts = tuple((get(roots+5+2*j), get(roots+6+2*j)) for j in range(len(model.rates))) if model.feature_scale is not None else ()
    return JointPartitionPlan(state, query, order, excesses, normalization, tuple(expected_shape.items()),
        envelope, maximum, multiplies, adds, compacted, cell, size, bits, parts)


def prepare_bound(program, state, rules, sources, budget, workspace, *, bit_limit=MAX_BITS, order=None):
    """Resolve the ordered query from independent complete native inputs."""
    require_state(state)
    if type(program) is not JointRelation:
        raise ContractError('complete joint native syntax required')
    program.__post_init__()
    if program != state.model:
        raise ContractError('joint state differs from the actual ordered model/prior')
    query, _ = program.source_query(rules, sources)
    return prepare(state, query, budget, workspace, bit_limit=bit_limit, order=order)


def _same(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is tuple:
        return len(actual) == len(expected) and all(_same(a, b) for a, b in zip(actual, expected))
    if type(expected) in (JointRelation, JointCountState, JointPartitionPlan):
        return vars(actual).keys() == vars(expected).keys() and all(
            _same(vars(actual)[k], v) for k, v in vars(expected).items())
    return type(expected) in (int, str, F, type(None)) and actual == expected


def check_bound_plan(plan, program, state, rules, sources, budget, workspace, *, bit_limit=MAX_BITS, order=None):
    # Reconstruct from independently retained complete inputs. A plan cannot
    # choose its own predecessor, model, query, order, resources or precision.
    expected = prepare_bound(program, state, rules, sources, budget, workspace, bit_limit=bit_limit, order=order)
    if not _same(plan, expected):
        raise ContractError('joint partition plan differs from its complete native input and execution')


def reference(plan):
    """Passive exact readout; a supplied plan is not authority to run a phase."""
    if type(plan) is not JointPartitionPlan:
        raise ContractError('complete joint partition plan required')
    excess = tuple(F(v, plan.normalization*plan.before.model.excess_denominator) for v in plan.excesses)
    masses = tuple(1+v for v in excess)
    scale = plan.before.model.native_scale
    probabilities = tuple(v/scale for v in masses)
    _guard(*excess, *masses, scale, *probabilities, bit_limit=plan.bit_limit)
    return excess+masses+(scale,)+probabilities


def passive_plan(state, query, budget=JointPartitionAllowance(), *, bit_limit=MAX_BITS, order=None):
    """Explicit caller-allocated convenience; never registers a Runtime lease."""
    _preflight(state, query, budget, bit_limit, order)
    with memoryview(bytearray(workspace_bytes(state.model, budget))) as scratch:
        return prepare(state, query, budget, scratch, bit_limit=bit_limit, order=order)
