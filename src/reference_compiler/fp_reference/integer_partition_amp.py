"""Half-mantissa direct integer partition readout, without authority."""
from fractions import Fraction as F

from . import integer_partition_decoder as decoder, indexed_amp as amp
from .core import ContractError
from .indexed_relation import IndexedRelation, allowance

BACKEND_ID = 'owned-indexed-direct-partition-half-mantissas-single-readout-v1'
FORWARD_ID = 'indexed-positive-integer-partition-half-mantissa-single-readout-v1'


def forward_work(n, budget, output_cap):
    return (2*decoder.construction_work(n, budget)
            +1024*(n+4*budget.span_cap+1)+128*(n+1)*output_cap)


def _prepare_prediction(program, state, rules, sources, *, output_cap, budget, workspace, bit_limit):
    if type(program) is not IndexedRelation or type(state) is not amp.IndexedAmpState or state.unit_count:
        raise ContractError('owned indexed syntax and committed AMP state required')
    state.__post_init__()
    if state.encoded.n != program.n:
        raise ContractError('direct-partition AMP predecessor differs from its native program')
    query, _ = program.source_query(rules, sources)
    with memoryview(workspace) as borrowed:
        plan = decoder.prepare(state.encoded, query, budget, borrowed, bit_limit=bit_limit)
    allowance(plan.output_cells, output_cap, 'direct-partition AMP output allowance')
    return plan


def check_prediction_plan(plan, program, state, rules, sources, **kwargs):
    expected = _prepare_prediction(program, state, rules, sources, **kwargs)
    decoder.check_plan(plan, expected)


def _prediction_schedule(plan, state, arithmetic):
    if type(plan) is not decoder.DirectPartitionPlan or plan.before != state.encoded or state.unit_count:
        raise ContractError('direct partition schedule lost its complete committed predecessor')
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


def check_prediction_execution(plan, before, actual, operations, *, bit_limit):
    arithmetic = amp._Arithmetic(bit_limit)
    expected, _ = _prediction_schedule(plan, before, arithmetic)
    return amp._check_execution(expected, actual, arithmetic, operations)
