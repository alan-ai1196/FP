"""Projected AMP: exact tape semantics, native coordinates and owned workers."""
from dataclasses import replace
from fractions import Fraction as F
from functools import partial
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import indexed_amp as amp, projected_amp as projected, query_projection
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance
from fp_reference.indexed_execution import IndexedState, IndexedEvaluation
from fp_reference.cuda_prefix import IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.float64_bridge import Float64Contract
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.learner import observe_event
from audit_reference_construction import rejects, validate_residency
from audit_indexed_runtime import literal as native_fixture
from audit_indexed_amp_plan_validation import audit as validate_plans
from audit_indexed_amp_plan_binding import evaluate_plan
from ingress_audit_support import deliver_context
from query_block_projection import literal
import audit_indexed_amp as legacy
import count_learner_encoding as native_counts

SHARED_CASES = ('profiles','large','install','closure','unfunded','target-swap','second-commit',
    'endpoint-binding','gradient-binding','trace-binding','predecessor-binding','old-output')
PROJECTED_CASES = SHARED_CASES+('star','future-0','future-1','foreign-plan','executor-plan-binding')


def arguments(n,values,query):
    schema = IndexedRelation(n)
    height = sum(map(abs,values))
    state = amp.IndexedAmpState(CountState(n,values,None,height,height))
    return schema,state,schema.rules(),schema.source_row(query[0]*n+query[1])


def exact_tape(plan,state):
    values = []
    for tag,*args in plan.nodes:
        if tag in ('zero','one','nine'):
            value = {'zero':0,'one':1,'nine':9}[tag]
        elif tag == 'factor':
            edge,parity = args
            d = state.encoded.counts[plan.positions[edge]]
            value = 9**(max(d,0) if parity == 0 else max(-d,0))
        else:
            a,b = (values[j] for j in args)
            value = a*b if tag == 'mul' else a+b
        values.append(value)
    a,b = (values[j] for j in plan.partitions)
    return F(a,a+b)


def exhaustive():
    states = queries = 0
    for n in range(2,5):
        for counts in product((-1,0,1),repeat=n*(n-1)//2):
            moments,_ = literal(n,counts)
            states += 1
            for query in product(range(n),repeat=2):
                args = arguments(n,counts,query)
                plan = projected.prepare_prediction(*args,output_cap=262144)
                assert exact_tape(plan,args[1]) == moments[tuple(sorted(query))]
                assert dict(plan.table_shape)['complete_counts_scanned'] == len(counts)
                assert dict(plan.table_shape)['partition_tape_cells'] == len(plan.nodes)
                for edge,position in zip(plan.support,plan.positions):
                    assert tuple(combinations(range(n),2))[position] == edge and counts[position]
                queries += 1
    return {'ternary_count_states':states,'complete_ordered_query_tapes_against_native_world_sums':queries}


def numeric():
    cases = [(3,counts,query) for counts in product((-1,0,1),repeat=3)
             for query in product(range(3),repeat=2)]
    for a,b in product((-2,0,2),repeat=2):
        counts = (a,-1,b,0,a,0,0,0,0,b)
        cases.extend((5,counts,q) for q in ((0,4),(1,4),(4,1),(2,2)))
    cases.append((5,(-2,-2,-2,-2,-2,0,0,0,0,-1),(1,2)))
    predictions = observations = half = 0
    maximum = {key:F(0) for key in ('native','probability','gradient')}
    examples = []
    tolerance = Float64Contract(F(1,100),F(1,1000))
    fixtures = {n:native_fixture(n) for n in (3,5)}
    for n,counts,query in cases:
        args = arguments(n,counts,query)
        schema,state,rules,sources = args
        plan = projected.prepare_prediction(*args,output_cap=262144)
        projected.check_prediction_plan(plan,*args,output_cap=262144)
        raw,operations = evaluate_plan(plan,state)
        assert len(operations)+7 == plan.output_cells
        amp.check_prediction_execution(plan,state,raw,operations,bit_limit=32768)
        half += sum(len(words) for _,width,words in operations if width == 16)
        _,graph,spec,_ = fixtures[n]
        native = native_counts.decode(state.encoded)
        exact = evaluate(graph,rules,native.theta,sources,(),bit_limit=32768)
        reference = IndexedEvaluation(state.encoded,query,exact.excesses,exact.masses,exact.normalizer,exact.probabilities,())
        relation = amp.check_prediction(reference,raw,tolerance,normalizer_cap=F(18),activation_cap=F(8),bit_limit=32768)
        materialized = raw.decoded().materialize(scalar_cap=10000)
        error = max(abs(a-b) for a,b in zip(exact.values+exact.masses,materialized.values+materialized.masses))
        assert relation.native_error == error
        maximum['native'] = max(maximum['native'],error)
        maximum['probability'] = max(maximum['probability'],relation.probability_error)
        predictions += 1
        for target in (0,1):
            arithmetic = amp._Arithmetic(32768)
            observed,_ = amp.execute_observation(state,raw,target,arithmetic)
            full = observe_event(graph,native,spec,exact,target,bit_limit=32768)
            mass = exact.masses[target]
            ref = IndexedState(observed.encoded,(1/mass-F(1,5),F(4,5)-8/mass,F(4,5)))
            relation = amp.check_state(ref,observed,tolerance,bit_limit=32768)
            decoded = legacy.component.CompactState(observed.encoded,observed.gradient_words).materialize(scalar_cap=10000)
            error = max(abs(a-b) for a,b in zip(full.gradient_sum,decoded.gradient_sum))
            assert error == relation.state_error and full.theta == decoded.theta
            maximum['gradient'] = max(maximum['gradient'],error)
            observations += 1
        if counts == (-2,-2,-2,-2,-2,0,0,0,0,-1):
            old = amp.prepare_prediction(*args,output_cap=262144)
            prior,_ = evaluate_plan(old,state)
            assert prior.words != raw.words
            examples.append({'n':n,'counts':list(counts),'query':list(query),
                'exact_parity_probability':str(exact_tape(plan,state)),
                'global_words':list(prior.words),'projected_words':list(raw.words),
                'global_output_cells':old.output_cells,'projected_output_cells':plan.output_cells})
    assert half > 0 and examples
    return {'predictions':predictions,'observations':observations,'half_precision_outputs':half,
        'maximum_complete_coordinate_errors':{key:str(value) for key,value in maximum.items()},
        'distinct_registered_rounding_example':examples}


def guards():
    def forbidden(*args,**kwargs):
        raise AssertionError('a numerical or unregistered builder was entered')
    small = arguments(3,(1,0,1),(0,2))
    with patch.object(query_projection,'prepare',forbidden),patch.object(query_projection.partition,'decode',forbidden):
        projected.prepare_prediction(*small,output_cap=65536)
    large = arguments(2,(10**9,),(0,1))
    with patch.object(query_projection,'prepare',forbidden):
        plan = projected.prepare_prediction(*large,output_cap=65536)
    raw,_ = evaluate_plan(plan,large[1])
    assert abs(amp.single(raw.words[5])-F(9,10)) < F(1,10**6)
    rejects(lambda: query_projection.prepare(large[1].encoded,(0,1),DecodeAllowance()),ArithmeticUnresolved)
    dense = arguments(15,(1,)*105,(0,1))
    exponent = arguments(2,(amp.COUNTER_CAP-1,),(0,1))
    with patch.object(projected,'compile_tape',forbidden):
        rejects(lambda: projected.prepare_prediction(*dense,output_cap=65536),ArithmeticUnresolved)
        rejects(lambda: projected.prepare_prediction(*exponent,output_cap=65536),ArithmeticUnresolved)
        with patch.object(amp,'MAX_TAPE_CELLS',3):
            rejects(lambda: projected.prepare_prediction(*small,output_cap=65536),ArithmeticUnresolved)
    plan = projected.prepare_prediction(*small,output_cap=65536)
    rejects(lambda: projected.prepare_prediction(*small,output_cap=plan.output_cells-1),ArithmeticUnresolved)
    original = amp.prepare_prediction(*small,output_cap=65536)
    rejects(lambda: projected.check_prediction_plan(original,*small,output_cap=65536))
    rejects(lambda: amp.check_prediction_plan(plan,*small,output_cap=65536))
    storage = CudaStorageContract(1<<20,2<<20,{role:(1<<20,2<<20) for role in ('deployment','compiler')})
    old = IndexedCudaPrefixContract(storage,F(1,100),F(1,1000),n=3)
    new = ProjectedIndexedCudaPrefixContract(storage,F(1,100),F(1,1000),n=3)
    assert old.forward_id != new.forward_id and old.backend_id != new.backend_id
    object.__setattr__(new,'forward_id',old.forward_id)
    rejects(new.__post_init__)
    return {'exact_reference_numeric_calls_during_physical_preparation':0,
        'independent_mantissa_exponent_height':10**9,'reference_integer_height_refusal':True,
        'hard_block_tape_and_exponent_refusals_before_tape_construction':3,
        'output_allowance_refusals':1,'foreign_schedule_plan_refusals':2,'foreign_arithmetic_identity_refusals':1,
        'large_exponent_scope':'passive physical schedule only; owned reference height may refuse the phase'}


def cpu_audit():
    return {'status':'PASS_PROJECTED_AMP_CPU','scope':'exact projected tape semantics and exact RNE/native coordinate audit; actual CUDA evidence separate',
        'backend_id':projected.BACKEND_ID,'forward_id':projected.FORWARD_ID,
        'exhaustive':exhaustive(),'numerical':numeric(),'guards':guards(),'complete_plan_binding':validate_plans(projected)}


def worker(case):
    if case in SHARED_CASES:
        # Reuse the full original fixtures and assertions. Only their declared
        # physical contract and independent expected-plan audit change.
        original = legacy.configuration
        def configuration(*args,**kwargs):
            rt,schema = original(*args,projected=True,**kwargs)
            assert rt._cuda.contract.forward_id == projected.FORWARD_ID
            return rt,schema
        with patch.object(legacy,'configuration',configuration), \
                patch.object(legacy,'check_phases',partial(legacy.check_phases,projected=True)):
            result = legacy.worker(case)
        return {**result,'declared_forward_id':projected.FORWARD_ID}
    if case == 'star':
        rt,schema = legacy.configuration(15,15,projected=True)
        for leaf in range(2,15):
            legacy.step(rt,schema,(1,leaf,0))
        before = rt.snapshot()
        key = before.online.data.active.observation_ids[before.cursor]
        assert deliver_context(rt,key,tuple(schema.source_row(2*15+3).values())).status == 'PREDICTED_REFERENCE'
        first = validate_residency(rt)
        phase = first.cuda.phases[-1]
        assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
        assert phase.reference_prediction.probabilities[0] == F(189,250)
        assert len(phase.execution_plan.positions) == 2 and sum(d != 0 for d in phase.raw_prediction.before.counts) == 13
        args = (schema,amp.IndexedAmpState(phase.raw_prediction.before),schema.rules(),schema.source_row(2*15+3))
        rejects(lambda: amp.prepare_prediction(*args,output_cap=65536),ArithmeticUnresolved)
        first_word,first_cells = phase.raw_prediction.words[5],phase.output_cells
        assert first.pending.record.target is None and first.cursor == 13
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        following = rt.snapshot()
        key = following.online.data.active.observation_ids[following.cursor]
        assert deliver_context(rt,key,tuple(schema.source_row(2*15+4).values())).status == 'PREDICTED_REFERENCE'
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert sum(d != 0 for d in phase.raw_prediction.before.counts) == 14
        assert phase.raw_prediction.before.counts[27] == 1  # global edge(2,3)
        assert after.cursor == 14 and after.pending.record.target is None
        return {**legacy.check_phases(rt,projected=True),'actual_star_observations':13,
            'first_reference_forecast':'189/250','first_actual_forecast_word':first_word,
            'first_prediction_output_cells':first_cells,'first_projected_active_edges':2,
            'first_retained_nonzero_counts':13,'global_schedule_preflight':'UNRESOLVED',
            'post_prediction_observation':[2,3,0],'following_query':[2,4],
            'following_reference_forecast':str(phase.reference_prediction.probabilities[0]),
            'following_projected_active_edges':len(phase.execution_plan.positions),
            'following_retained_nonzero_counts':14,'final_target_revealed':False}
    if case in ('future-0','future-1'):
        # Each complete history gets its own fresh process/allocator. No
        # second root, cache clearing, counter reset or altered arena guard.
        target = int(case[-1])
        rt,schema = legacy.configuration(4,4,projected=True)
        for event in ((1,2,target),(0,1,0),(2,3,0)):
            legacy.step(rt,schema,event)
        before = rt.snapshot()
        key = before.online.data.active.observation_ids[before.cursor]
        assert deliver_context(rt,key,tuple(schema.source_row(3).values())).status == 'PREDICTED_REFERENCE'
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        expected = F(881 if target == 0 else 369,1250)
        assert phase.reference_prediction.probabilities[0] == expected
        assert phase.raw_prediction.before.counts[3] == 1-2*target  # edge(1,2)
        assert after.cursor == 3 and after.pending.record.target is None
        return {**legacy.check_phases(rt,projected=True),'initial_event':[1,2,target],
            'common_suffix':[[0,1,0],[2,3,0]],'final_query':[0,3],
            'reference_forecast':str(expected),'actual_forecast_word':phase.raw_prediction.words[5],
            'retained_complete_count_coordinates':6,'target_revealed':False,
            'discarded_off_path_information':False}
    if case in ('foreign-plan','executor-plan-binding'):
        rt,schema = legacy.configuration(3,2,projected=True)
        legacy.step(rt,schema,(1,2,0))
        before = rt.snapshot()
        original = amp.execute_prediction
        def forbidden(*args,**kwargs):
            raise AssertionError('a foreign declared schedule entered numerical execution')
        def changed(plan,*args,**kwargs):
            result = original(plan,*args,**kwargs)
            object.__setattr__(plan,'output_cells',plan.output_cells-1)
            return result
        key = before.online.data.active.observation_ids[before.cursor]
        if case == 'foreign-plan':
            with patch.object(projected,'prepare_prediction',amp.prepare_prediction),patch.object(amp,'execute_prediction',forbidden):
                rejects(lambda: deliver_context(rt,key,tuple(schema.source_row(1).values())),RuntimeError)
        else:
            with patch.object(amp,'execute_prediction',changed):
                rejects(lambda: deliver_context(rt,key,tuple(schema.source_row(1).values())),RuntimeError)
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED' and 'plan differs' in phase.reason
        assert after.cursor == 1 and after.pending.record.target is None and not after.pending.predictions
        assert after.candidates == before.candidates and after.cuda.current == before.cuda.current
        if case == 'foreign-plan':
            assert phase.output_cells == 0 and not phase.raw_operations and phase.raw_prediction is None
        else:
            raw = phase.raw_prediction
            args = (schema,amp.IndexedAmpState(raw.before),schema.rules(),schema.source_row(1))
            honest = projected.prepare_prediction(*args,output_cap=65536)
            expected,operations = evaluate_plan(honest,args[1])
            assert raw == expected and phase.raw_operations == operations
            assert phase.output_cells == honest.output_cells == phase.execution_plan.output_cells+1
        return {'certificate_claim':'REFUSED','attack':case,'phase_status':phase.status,
            'actual_output_cells':phase.output_cells,'declared_plan_output_cells':phase.execution_plan.output_cells,
            'target_revealed':False,'published_predictions_or_learner_advances':0}
    raise AssertionError('unregistered projected worker')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = cpu_audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_PROJECTED_AMP_CPU.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
