"""Coefficient-normalized carry-free histogram schedule, without authority."""
from fractions import Fraction as F

from . import packed_histogram_decoder as decoder, indexed_amp as amp
from .core import ContractError
from .indexed_relation import IndexedRelation, allowance

BACKEND_ID = 'owned-indexed-carry-free-histogram-half-products-single-readout-v1'
FORWARD_ID = 'packed-count-coefficient-normalized-histogram-rne16-rne32-v1'


def forward_work(n, budget, output_cap):
    terms = min(1 << (n-1), 2*(budget.span_cap+1))
    return 2*decoder.construction_work(n, budget)+1024*(terms+1)+128*(n+1)*output_cap


def _prepare_prediction(program, state, rules, sources, *, output_cap, budget, workspace, bit_limit):
    if type(program) is not IndexedRelation or type(state) is not amp.IndexedAmpState or state.unit_count:
        raise ContractError('owned indexed syntax and committed AMP state required')
    state.__post_init__()
    if state.encoded.n != program.n:
        raise ContractError('carry-free AMP predecessor differs from its native program')
    query, _ = program.source_query(rules, sources)
    with memoryview(workspace) as borrowed:
        plan = decoder.prepare(state.encoded, query, budget, borrowed, bit_limit=bit_limit)
    allowance(plan.output_cells, output_cap, 'carry-free histogram AMP output allowance')
    return plan


def check_prediction_plan(plan, program, state, rules, sources, **kwargs):
    expected = _prepare_prediction(program, state, rules, sources, **kwargs)
    decoder.check_plan(plan, expected)


def _prediction_schedule(plan, state, arith):
    if type(plan) is not decoder.PackedHistogramPlan or plan.before != state.encoded or state.unit_count:
        raise ContractError('carry-free schedule lost its committed physical predecessor')
    top = max(k for part in plan.terms for k, _ in part)
    common = max(h.bit_length()+1-(9**(top-k)).bit_length() for part in plan.terms for k, h in part)
    sums = []
    for part in plan.terms:
        terms = []
        for k, h in part:
            denominator = 9**(top-k)
            eh, bd = h.bit_length(), denominator.bit_length()
            exponent = eh+1-bd-common
            a = arith.op('constant', constant=F(h, 1 << eh))
            b = arith.op('constant', constant=F(1 << (bd-1), denominator))
            product = arith.op('cast', arith.op('mul',
                arith.op('cast', a, half=True), arith.op('cast', b, half=True), half=True))
            scale = F(0) if exponent < -149 else F(1, 1 << -exponent)
            terms.append(arith.op('mul', product, arith.op('constant', constant=scale)))
        if not terms:
            terms = [arith.op('constant', constant=0)]
        while len(terms) > 1:
            terms = [arith.op('add', terms[i], terms[i+1]) if i+1 < len(terms) else terms[i]
                     for i in range(0, len(terms), 2)]
        sums.append(terms[0])
    denominator = arith.op('add', *sums)
    marginals = tuple(arith.op('div', value, denominator) for value in sums)
    one, eight = (arith.op('constant', constant=value) for value in (1, 8))
    excesses = tuple(arith.op('mul', eight, value) for value in marginals)
    masses = tuple(arith.op('add', one, value) for value in excesses)
    normalizer = arith.op('add', *masses)
    probabilities = tuple(arith.op('div', value, normalizer) for value in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    output = arith.stack(columns)
    raw = amp.IndexedAmpPrediction(state.encoded, plan.query, tuple(v.word for v in columns))
    return raw, None if output is None else amp.ResidentPrediction(state.encoded, plan.query, output)


def check_prediction_execution(plan, before, actual, operations, *, bit_limit):
    arithmetic = amp._Arithmetic(bit_limit)
    expected, _ = _prediction_schedule(plan, before, arithmetic)
    return amp._check_execution(expected, actual, arithmetic, operations)
