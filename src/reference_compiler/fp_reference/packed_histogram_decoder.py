"""Carry-free positive elimination in a prepaid contiguous wide-cell extent.

Tables and unpacked coefficients use the owner's actual pinned byte buffer.
Scopes and bounded integer operands remain host scratch, covered by the whole
host job, not by a claim that this buffer measures all Python heap usage.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations

from .core import ContractError, natural
from .indexed_count import CountState, query as require_query
from .semantics import ArithmeticUnresolved, _guard

MODEL_ID = 'packed-indexed-carry-free-histogram-reference-payload-v1'
WORK_MODEL = 'prepaid-contiguous-carry-free-histogram-v1'
MAX_BITS, MAX_CELLS, MAX_ARITHMETIC = 32768, 32768, 2_000_000


@dataclass(frozen=True)
class PackedHistogramAllowance:
    join_cells: int = 4096
    live_cells: int = MAX_CELLS
    arithmetic: int = MAX_ARITHMETIC
    span_cap: int = 396
    integer_bits: int = MAX_BITS

    def __post_init__(self):
        for name in ('join_cells', 'live_cells', 'arithmetic', 'integer_bits'):
            natural(getattr(self, name), name, positive=True)
        natural(self.span_cap, 'carry-free histogram span allowance')
        if (max(self.join_cells, self.live_cells) > MAX_CELLS
                or self.arithmetic > MAX_ARITHMETIC or self.integer_bits > MAX_BITS
                or self.span_cap > (MAX_BITS-1040)//16):
            raise ContractError('carry-free histogram allowance exceeds its finite implementation class')


def _layout(n, budget):
    from .indexed_relation import IndexedRelation
    IndexedRelation(n)
    if type(budget) is not PackedHistogramAllowance:
        raise ContractError('immutable carry-free histogram allowance required')
    budget.__post_init__()
    cell = (min(budget.integer_bits, n*(budget.span_cap+1))+7)//8
    coefficient = (n+7)//8
    offset = (budget.live_cells+2)*cell
    return cell, coefficient, offset, offset+2*(budget.span_cap+1)*coefficient


def workspace_bytes(budget, *, n):
    return _layout(n, budget)[3]


def construction_work(n, budget):
    """Prepaid scalar/index/byte tariff; not a bigint bit-time bound."""
    cell, _, _, size = _layout(n, budget)
    d, span = n*(n-1)//2, budget.span_cap
    return (64*(n+1)**2*(d+n+1)
            +32*(size+(budget.arithmetic+n*budget.live_cells+2*(span+1)+d+16)*(n+1+cell)))


@dataclass(frozen=True)
class PackedHistogramPlan:
    before: CountState
    query: tuple[int, int]
    span: int
    terms: tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]
    shape: tuple[tuple[str, int], ...]
    integer_envelope: int
    maximum_integer_bits: int
    compacted_cells: int
    bit_limit: int

    @property
    def n(self):
        return self.before.n

    @property
    def term_count(self):
        return sum(map(len, self.terms))

    @property
    def output_cells(self):
        return 9*self.term_count+21-2*sum(bool(part) for part in self.terms)


def _preflight(state, query, budget, bit_limit):
    from .indexed_relation import DecodeAllowance, partition_shape_plan
    if type(state) is not CountState or set(vars(state)) != {'n', 'counts', 'pending', 'cursor', 'steps'}:
        raise ContractError('complete immutable native count predecessor required')
    state.__post_init__()
    if type(query) is not tuple or len(query) != 2:
        raise ContractError('complete ordered carry-free histogram query required')
    require_query(state.n, *query)
    _layout(state.n, budget)
    natural(bit_limit, 'carry-free histogram reference integer limit', positive=True)
    height = sum(map(abs, state.counts))
    envelope = state.n*(height+1)
    bits = min(bit_limit, budget.integer_bits)
    if height > budget.span_cap:
        raise ArithmeticUnresolved('carry-free histogram span allowance insufficient')
    if max(envelope, 16*height+8*state.n+1024) > bits:
        raise ArithmeticUnresolved('carry-free histogram integer envelope exceeds allowance')
    support = tuple(e for e, d in zip(combinations(range(state.n), 2), state.counts) if d)
    shape = partition_shape_plan(state.n, support, query, tuple(range(state.n-1)),
        DecodeAllowance(budget.join_cells, budget.live_cells, budget.arithmetic, bits))
    return height, envelope, bits, shape


def prepare(state, query, budget, workspace, *, bit_limit):
    """Natural-order elimination with forward compaction of remaining tables.

    Each table is a (scope, start, length) descriptor into the paid extent.
    No tuple of wide table values or assignment enumeration is constructed.
    All refusal preflights precede clearing even one old workspace byte.
    """
    height, envelope, bits, expected_shape = _preflight(state, query, budget, bit_limit)
    cell, coefficient, coefficient_offset, size = _layout(state.n, budget)
    if (type(workspace) is not memoryview or workspace.readonly or workspace.ndim != 1
            or not workspace.c_contiguous or workspace.format != 'B' or len(workspace) != size):
        raise ContractError('complete writable owned carry-free histogram byte extent required')
    zero = bytes(4096)
    for offset in range(0, size, len(zero)):
        width = min(len(zero), size-offset)
        workspace[offset:offset+width] = zero[:width]
    maximum = 1

    def guard(value):
        nonlocal maximum
        if type(value) is not int or value < 0:
            raise ContractError('positive integer table coordinate required')
        maximum = max(maximum, value.bit_length())
        if maximum > envelope:
            raise ArithmeticUnresolved('carry-free integer escaped its proved bit envelope')
        return value

    def get(index):
        if not 0 <= index < budget.live_cells+2:
            raise ContractError('wide table read outside its paid extent')
        offset = index*cell
        return int.from_bytes(workspace[offset:offset+cell], 'little')

    def put(index, value):
        if not 0 <= index < budget.live_cells+2:
            raise ContractError('wide table write outside its paid extent')
        offset = index*cell
        workspace[offset:offset+cell] = guard(value).to_bytes(cell, 'little')

    n, factors, live = state.n, [], 0
    for (i, j), count in zip(combinations(range(n), 2), state.counts):
        if not count:
            continue
        scope = tuple(v for v in (i, j) if v)
        length = 1 << len(scope)
        scale = guard(1 << (n*abs(count)))
        for word in range(length):
            parity = (0 if i == 0 else word & 1) ^ ((word >> (len(scope)-1)) & 1)
            put(live+word, scale if parity == int(count < 0) else 1)
        factors.append((scope, live, length))
        live += length
    multiply = add = compacted = 0
    peak_join, peak_live = 1, live

    def join(items, scope, start):
        nonlocal multiply, peak_join
        length = 1 << len(scope)
        if start+length > budget.live_cells:
            raise ContractError('joined table escaped its prepaid cell plan')
        positions = {v: k for k, v in enumerate(scope)}
        projections = tuple(tuple(positions[v] for v in fs) for fs, _, _ in items)
        for word in range(length):
            value = 1
            for (_, source, _), indices in zip(items, projections):
                index = sum(((word >> p) & 1) << k for k, p in enumerate(indices))
                value = guard(value*get(source+index))
                multiply += 1
            put(start+word, value)
        peak_join = max(peak_join, length)
        return length

    kept = tuple(sorted({v for v in query if v}))
    for v in range(1, n):
        if v in kept:
            continue
        bucket = [item for item in factors if v in item[0]]
        rest = [item for item in factors if v not in item[0]]
        scope = tuple(sorted({v}.union(*(set(s) for s, _, _ in bucket))))
        joined = join(bucket, scope, live)
        out_scope, out_start = tuple(u for u in scope if u != v), live+joined
        length, position = joined//2, scope.index(v)
        if out_start+length > budget.live_cells:
            raise ContractError('reduced table escaped its prepaid cell plan')
        for word in range(length):
            low = word & ((1 << position)-1)
            index = low | ((word >> position) << (position+1))
            put(out_start+word, get(live+index)+get(live+index+(1 << position)))
            add += 1
        peak_live = max(peak_live, out_start+length)
        # Increasing source order and destination <= source make these moves
        # safe even when the old and new intervals overlap.
        factors, live = [], 0
        for fs, source, count in rest+[(out_scope, out_start, length)]:
            if live > source:
                raise ContractError('forward table compaction would destroy unread values')
            for k in range(count):
                put(live+k, get(source+k))
                compacted += 1
            factors.append((fs, live, count))
            live += count
    final = join(factors, kept, live)
    peak_live = max(peak_live, live+final)
    for word in range(final):
        values = {v: (word >> k) & 1 for k, v in enumerate(kept)}
        parity = values.get(query[0], 0) ^ values.get(query[1], 0)
        root = budget.live_cells+parity
        put(root, get(root)+get(live+word))
        add += 1
    guard(get(budget.live_cells)+get(budget.live_cells+1))
    add += 1
    shape = {'positive_multiplications': multiply, 'positive_additions': add,
        'largest_join_cells': peak_join, 'peak_live_integer_cells': peak_live}
    if shape != expected_shape or compacted > (n-1)*budget.live_cells:
        raise ContractError('carry-free execution differs from its complete resource plan')
    mask, stride = (1 << n)-1, budget.span_cap+1
    for y in (0, 1):
        value = get(budget.live_cells+y)
        for k in range(height+1):
            offset = coefficient_offset+(y*stride+k)*coefficient
            workspace[offset:offset+coefficient] = ((value >> (n*k)) & mask).to_bytes(coefficient, 'little')
    parts = []
    for y in (0, 1):
        part = []
        for k in range(height+1):
            offset = coefficient_offset+(y*stride+k)*coefficient
            h = int.from_bytes(workspace[offset:offset+coefficient], 'little')
            if h:
                part.append((k, h))
        parts.append(tuple(part))
    terms = tuple(parts)
    if sum(h for part in terms for _, h in part) != 1 << (n-1):
        raise ContractError('carry-free histogram lost a complete native assignment')
    return PackedHistogramPlan(state, query, height, terms, tuple(shape.items()),
                               envelope, maximum, compacted, bits)


def passive_plan(state, query, budget=PackedHistogramAllowance(), *, bit_limit=MAX_BITS):
    """Explicit caller-owned point read; no Runtime payment or admission."""
    _preflight(state, query, budget, bit_limit)
    with memoryview(bytearray(workspace_bytes(budget, n=state.n))) as scratch:
        return prepare(state, query, budget, scratch, bit_limit=bit_limit)


def exact_parts(plan):
    from .histogram_decoder import exact_parts as horner
    return horner(plan)


def execution_work(plan):
    return 64*(plan.span+1)+128*(plan.n*(plan.n-1)//2+16)


def table_statistics(plan):
    return dict(plan.shape, histogram_terms=plan.term_count, compacted_cells=plan.compacted_cells,
                integer_envelope=plan.integer_envelope, maximum_integer_bits=plan.maximum_integer_bits)


def reference(plan):
    from .indexed_execution import IndexedEvaluation
    if type(plan) is not PackedHistogramPlan or plan.before.pending is not None:
        raise ContractError('owned committed carry-free histogram prediction plan required')
    parts = exact_parts(plan)
    excesses = tuple(F(8*z, sum(parts)) for z in parts)
    masses = tuple(1+v for v in excesses)
    probabilities = tuple(v/10 for v in masses)
    _guard(*excesses, *masses, *probabilities, F(10), bit_limit=plan.bit_limit)
    return IndexedEvaluation(plan.before, plan.query, excesses, masses, F(10), probabilities,
                             tuple(table_statistics(plan).items()))


def check_plan(plan, expected):
    from .indexed_amp import _same_plan_value
    if (type(plan) is not PackedHistogramPlan or type(expected) is not PackedHistogramPlan
            or vars(plan).keys() != vars(expected).keys()
            or type(plan.before) is not CountState
            or set(vars(plan.before)) != {'n', 'counts', 'pending', 'cursor', 'steps'}):
        raise ContractError('complete carry-free histogram execution plan required')
    plan.before.__post_init__()
    if plan.before != expected.before or any(not _same_plan_value(value, vars(expected)[key])
            for key, value in vars(plan).items() if key != 'before'):
        raise ContractError('carry-free histogram plan differs from its complete native input')
