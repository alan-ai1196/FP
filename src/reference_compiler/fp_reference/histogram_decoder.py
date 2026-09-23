"""Paid integer realization of the complete native count family.

This module owns no Runtime authority. Runtime supplies its prepaid, pinned
workspace and charges the declared work before entering the fixed kernel.
The immutable histogram is a query plan, never a replacement learner state.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import struct
import sys

from .core import ContractError, natural
from .indexed_count import CountState, query as require_query, world_count
from .semantics import ArithmeticUnresolved, _guard
from .packed_histogram_decoder import PackedHistogramAllowance, PackedHistogramPlan
from .integer_partition_decoder import DirectPartitionAllowance, DirectPartitionPlan

MODEL_ID = 'packed-indexed-histogram-reference-payload-v1'
WORK_MODEL = 'prepaid-packed-exponent-histogram-visits-v1'
WORKSPACE_KIND = 'exponent_histogram_workspace'
MAX_WORLDS, MAX_BITS = 32768, 32768
CELL = struct.Struct('<I')


@dataclass(frozen=True)
class HistogramAllowance:
    world_cap: int = MAX_WORLDS
    span_cap: int = 396
    integer_bits: int = MAX_BITS

    def __post_init__(self):
        natural(self.world_cap, 'histogram world allowance', positive=True)
        natural(self.span_cap, 'histogram span allowance')
        natural(self.integer_bits, 'histogram integer allowance', positive=True)
        if self.world_cap > MAX_WORLDS or self.integer_bits > MAX_BITS:
            raise ContractError('histogram implementation declares at most32768 worlds/bits')
        if self.span_cap > (MAX_BITS-1040)//16:
            raise ContractError('histogram declared span exceeds its finite integer implementation')


def workspace_bytes(budget, *, n=None):
    if type(budget) is not HistogramAllowance:
        raise ContractError('immutable histogram allowance required')
    budget.__post_init__()
    return 2*(budget.span_cap+1)*CELL.size


def enumeration_work(n, budget):
    """Conservative scalar/index visits, not bit time or total Python heap."""
    workspace_bytes(budget)
    K = world_count(n, budget.world_cap)
    return 64*(n+1)*K+32*(2*(budget.span_cap+1)+n*(n-1)//2+1)


def construction_work(n, budget):
    return enumeration_work(n, budget)


@dataclass(frozen=True)
class HistogramPlan:
    before: CountState
    query: tuple[int, int]
    span: int
    terms: tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]
    world_visits: int
    incident_visits: int
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
    if type(state) is not CountState or set(vars(state)) != {'n', 'counts', 'pending', 'cursor', 'steps'}:
        raise ContractError('complete immutable native count predecessor required')
    state.__post_init__()
    if type(query) is not tuple or len(query) != 2:
        raise ContractError('complete ordered histogram query required')
    require_query(state.n, *query)
    workspace_bytes(budget)
    natural(bit_limit, 'histogram reference integer limit', positive=True)
    K = world_count(state.n, budget.world_cap)
    H = sum(map(abs, state.counts))
    bits = min(bit_limit, budget.integer_bits)
    if H > budget.span_cap:
        raise ArithmeticUnresolved('histogram span allowance insufficient')
    if bits < max(1024, 16*H+8*state.n+1024):
        raise ArithmeticUnresolved('histogram conservative integer allowance insufficient')
    return K, H, bits


def prepare(state, query, budget, workspace, *, bit_limit):
    """Fixed Gray traversal in the actual supplied uint32 histogram extent.

    Pending counts are allowed for passive full-coordinate decoding. Prediction
    entry points separately require a committed complete predecessor. No
    adjacency list or K-world table is allocated by this integer kernel.
    """
    K, H, bits = _preflight(state, query, budget, bit_limit)
    if (type(workspace) is not memoryview or workspace.readonly or workspace.ndim != 1
            or not workspace.c_contiguous or workspace.format != 'B'
            or len(workspace) != workspace_bytes(budget)):
        raise ContractError('complete writable owned histogram byte extent required')
    # Clear the full funded extent, including currently unused exponent cells.
    for offset in range(0, len(workspace), CELL.size):
        CELL.pack_into(workspace, offset, 0)
    stride = budget.span_cap+1
    n, values = state.n, state.counts
    energy = sum(d for d in values if d > 0)
    mask = parity = visits = 0
    CELL.pack_into(workspace, CELL.size*energy, 1)
    for t in range(1, K):
        v = (t & -t).bit_length()
        bit = (mask >> (v-1)) & 1
        for j in range(n):
            if j == v:
                continue
            i, k = (j, v) if j < v else (v, j)
            d = values[i*(2*n-i-1)//2+k-i-1]
            other = 0 if j == 0 else (mask >> (j-1)) & 1
            energy += -abs(d) if (bit ^ other) == int(d < 0) else abs(d)
            visits += 1
        mask ^= 1 << (v-1)
        parity ^= int(query[0] != query[1] and v in query)
        if not 0 <= energy <= H:
            raise ContractError('histogram traversal escaped its exact energy envelope')
        offset = CELL.size*(parity*stride+energy)
        CELL.pack_into(workspace, offset, CELL.unpack_from(workspace, offset)[0]+1)
    parts = []
    for y in (0, 1):
        part = []
        for k in range(H+1):
            h = CELL.unpack_from(workspace, CELL.size*(y*stride+k))[0]
            if h:
                part.append((k, h))
        parts.append(tuple(part))
    terms = tuple(parts)
    if sum(h for part in terms for _, h in part) != K or visits != (n-1)*(K-1):
        raise ContractError('histogram traversal lost a complete native assignment')
    return HistogramPlan(state, query, H, terms, K, visits, bits)


def passive_plan(state, query, budget=HistogramAllowance(), *, bit_limit=MAX_BITS):
    """Explicit caller-owned point read; no Runtime payment or admission."""
    _preflight(state, query, budget, bit_limit)
    with memoryview(bytearray(workspace_bytes(budget))) as scratch:
        return prepare(state, query, budget, scratch, bit_limit=bit_limit)


def exact_parts(plan):
    totals = []
    for part in plan.terms:
        value, position = 0, len(part)-1
        for k in range(plan.span, -1, -1):
            h = part[position][1] if position >= 0 and part[position][0] == k else 0
            position -= int(bool(h))
            value = 9*value+h
        totals.append(value)
    return tuple(totals)


def execution_work(plan):
    return 64*(plan.span+1)+128*(plan.n*(plan.n-1)//2+16)


def table_statistics(plan):
    return {'world_visits': plan.world_visits, 'incident_visits': plan.incident_visits,
            'histogram_terms': plan.term_count}


def reference(plan):
    from .indexed_execution import IndexedEvaluation
    if type(plan) is not HistogramPlan or plan.before.pending is not None:
        raise ContractError('owned committed histogram prediction plan required')
    parts = exact_parts(plan)
    excesses = tuple(F(8*z, sum(parts)) for z in parts)
    masses = tuple(1+v for v in excesses)
    probabilities = tuple(v/10 for v in masses)
    _guard(*excesses, *masses, *probabilities, F(10), bit_limit=plan.bit_limit)
    return IndexedEvaluation(plan.before, plan.query, excesses, masses, F(10), probabilities,
        (('world_visits', plan.world_visits), ('incident_visits', plan.incident_visits),
         ('histogram_terms', plan.term_count)))


def check_plan(plan, expected):
    from .indexed_amp import _same_plan_value
    if type(plan) is not HistogramPlan or vars(plan).keys() != vars(expected).keys():
        raise ContractError('complete histogram execution plan required')
    _preflight(plan.before, plan.query, HistogramAllowance(span_cap=expected.span), plan.bit_limit)
    if plan.before != expected.before or any(not _same_plan_value(value, vars(expected)[key])
            for key, value in vars(plan).items() if key != 'before'):
        raise ContractError('histogram plan differs from its complete native input')


ALLOWANCES = (HistogramAllowance, PackedHistogramAllowance, DirectPartitionAllowance)
PLANS = (HistogramPlan, PackedHistogramPlan, DirectPartitionPlan)
HistogramBudget = HistogramAllowance | PackedHistogramAllowance | DirectPartitionAllowance


def implementation(budget):
    """Fixed integer realizations; no external engine registration.

    The existing configuration field retains its historical histogram name.
    A direct-partition registration computes no coefficient histogram.
    """
    if type(budget) is HistogramAllowance:
        return sys.modules[__name__]
    if type(budget) is PackedHistogramAllowance:
        from . import packed_histogram_decoder
        return packed_histogram_decoder
    if type(budget) is DirectPartitionAllowance:
        from . import integer_partition_decoder
        return integer_partition_decoder
    raise ContractError('registered histogram allowance required')


def plan_implementation(plan):
    if type(plan) is HistogramPlan:
        return sys.modules[__name__]
    if type(plan) is PackedHistogramPlan:
        from . import packed_histogram_decoder
        return packed_histogram_decoder
    if type(plan) is DirectPartitionPlan:
        from . import integer_partition_decoder
        return integer_partition_decoder
    raise ContractError('registered histogram execution plan required')
