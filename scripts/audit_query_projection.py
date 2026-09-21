"""Exact block projection, complete native phases, and owned admission attacks."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.indexed_count import CountState
from fp_reference.indexed_execution import IndexedReferenceMachine, IndexedState
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance, bound_view, partition_plan
from fp_reference import query_projection as projected
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_indexed_runtime import fixture, literal as native_fixture, step, check_prediction
from audit_reference_construction import validate_residency, rejects
from ingress_audit_support import deliver_context
from query_block_projection import simple_path_edges, literal


def structural():
    supports = queries = 0
    for n in range(2,6):
        edges = tuple(combinations(range(n),2))
        for signs in product((0,1),repeat=len(edges)):
            support = tuple(e for e,d in zip(edges,signs) if d)
            state = CountState(n,signs,None,sum(signs),sum(signs))
            supports += 1
            for query in combinations(range(n),2):
                plan = projected.prepare(state,query,DecodeAllowance())
                selected = {e for block in plan.blocks for e in combinations(block.vertices,2) if e in support}
                expected = {support[k] for k in simple_path_edges(n,support,*query)}
                assert selected == expected
                assert dict(plan.shape)['complete_counts_scanned'] == len(signs)
                queries += 1
    return {'all_supports_n2_through_n5': supports,'independent_simple_path_edge_union_checks': queries}


def exhaustive_native():
    states = queries = 0
    for n in range(2,5):
        schema, budget = IndexedRelation(n), DecodeAllowance()
        machine = IndexedReferenceMachine(n,budget)
        rules,graph,spec,_ = native_fixture(n)
        for values in product((-1,0,1),repeat=n*(n-1)//2):
            clock = sum(map(abs,values))
            state = IndexedState(CountState(n,values,None,clock,clock))
            pair_moments,weights = literal(n,values)
            states += 1
            for query in product(range(n),repeat=2):
                sources = schema.source_row(query[0]*n+query[1])
                plan = machine.prepare_prediction(schema,rules,state,sources,bit_limit=32768)
                assert machine.prediction_execution_work(plan) > 0
                actual = machine.execute_prediction(plan)
                check_prediction(actual,evaluate(graph,rules,(F(1),)+weights,sources,(),bit_limit=32768))
                assert actual.before is state.encoded and actual.query == query
                assert actual.probabilities[0] == F(1,10)+F(4,5)*pair_moments[tuple(sorted(query))]
                queries += 1
    return {'ternary_count_states': states,'complete_native_cache_comparisons': queries}


def own_prediction(runtime,schema,query):
    before = runtime.snapshot()
    observation = before.online.data.active.observation_ids[before.cursor]
    result = deliver_context(runtime,observation,tuple(schema.source_row(query[0]*schema.n+query[1]).values()))
    assert result.status == 'PREDICTED_REFERENCE',result
    after = validate_residency(runtime)
    assert after.pending.record.target is None and after.cursor == before.cursor
    assert after.candidates == before.candidates
    return after.pending.predictions[0][1],after


def future_information():
    rows = []
    for target in (0,1):
        cfg,schema,online = fixture(4,4)
        runtime = ReferenceCompilerRuntime(cfg,schema,online=online)
        candidate = runtime.snapshot().deployed_id
        models = {candidate:native_fixture(4)}
        step(runtime,schema,(1,2,target),models)
        original = runtime.snapshot().candidates[0].learner
        # This first response is a passive read; the later three predictions
        # execute through actual owned ingress and independent native phases.
        plan = runtime._machine.prepare_prediction(schema,cfg.semantics,original,schema.source_row(3),bit_limit=32768)
        runtime._machine.prediction_execution_work(plan)
        current = runtime._machine.execute_prediction(plan)
        assert current.probabilities[0] == F(1,2) and not plan.projection.blocks
        first_theta = bound_view(schema,original.encoded,(0,3)).theta(1)
        assert first_theta == F(9 if target == 0 else 1,40)
        for event in ((0,1,0),(2,3,0)):
            step(runtime,schema,event,models)
        prediction,after = own_prediction(runtime,schema,(0,3))
        rules,graph,spec,state = models[candidate]
        check_prediction(prediction,evaluate(graph,rules,state.theta,schema.source_row(3),(),bit_limit=32768))
        expected = F(881 if target == 0 else 369,1250)
        assert prediction.probabilities[0] == expected
        rows.append({'initial_actual_event':[1,2,target], 'initial_current_query_forecast':'1/2',
            'initial_native_theta_1':str(first_theta), 'common_actual_suffix':[[0,1,0],[2,3,0]],
            'owned_final_query':[0,3], 'owned_final_forecast':str(expected),
            'full_native_caches_checked':4,'full_observed_and_committed_states_checked_each':3,
            'retained_complete_count_coordinates':len(prediction.before.counts),
            'actual_cursor':after.cursor,'final_target_revealed':False})
    return rows


def off_path_height():
    cfg,schema,online = fixture(4,5)
    cfg = replace(cfg,reference_integer_bits=24)
    runtime = ReferenceCompilerRuntime(cfg,schema,online=online)
    models = {runtime.snapshot().deployed_id:native_fixture(4)}
    for _ in range(4):
        step(runtime,schema,(2,3,0),models)
    before = runtime.snapshot()
    encoded = before.candidates[0].learner.encoded
    rejects(lambda: bound_view(schema,encoded,(0,1),budget=DecodeAllowance(integer_bits=24)).theta(1),ArithmeticUnresolved)
    def forbidden(*args,**kwargs):
        raise AssertionError('irrelevant integer tables were executed')
    with patch.object(projected.partition,'decode',forbidden):
        prediction,after = own_prediction(runtime,schema,(0,1))
    assert prediction.before == encoded and prediction.probabilities[0] == F(1,2)
    return {'actual_observations':4,'registered_reference_bits':24,
        'global_parameter_reader_still_guarded':True,'owned_query_forecast':'1/2',
        'irrelevant_partition_kernel_calls':0,'retained_counts':list(encoded.counts),
        'packed_current_bytes':after.resources['current']['reference_payload_bytes']}


def binding_attacks():
    rows = []
    for kind in ('plan-query','plan-state','plan-bits','plan-shape','plan-block-omission',
                 'plan-block-vertices','plan-block-query'):
        cfg,schema,online = fixture(3,3)
        runtime = ReferenceCompilerRuntime(cfg,schema,online=online)
        if kind.startswith('plan-block-'):
            models = {runtime.snapshot().deployed_id:native_fixture(3)}
            step(runtime,schema,(0,1,0),models)
            step(runtime,schema,(1,2,0),models)
        before = runtime.snapshot()
        query = (0,2) if kind.startswith('plan-block-') else (0,1)
        method = 'prepare_prediction'
        original = getattr(IndexedReferenceMachine,method)
        def changed(machine,*args,**kwargs):
            result = original(machine,*args,**kwargs)
            if kind.startswith('plan-block-'):
                blocks = result.projection.blocks
                assert len(blocks) == 2
                if kind.endswith('omission'):
                    blocks = blocks[:1]
                elif kind.endswith('vertices'):
                    blocks = (replace(blocks[0],vertices=(0,2)),)+blocks[1:]
                else:
                    blocks = (replace(blocks[0],query=(0,0)),)+blocks[1:]
                return replace(result,projection=replace(result.projection,blocks=blocks))
            if kind.endswith('query'):
                return replace(result,query=(0,0))
            if kind.endswith('state'):
                return replace(result,before=replace(result.before,cursor=before.cursor+1))
            if kind.endswith('bits'):
                return replace(result,bit_limit=result.bit_limit+1)
            shape = tuple((key,value+1 if key == 'positive_multiplications' else value) for key,value in result.projection.shape)
            return replace(result,projection=replace(result.projection,shape=shape))
        with patch.object(IndexedReferenceMachine,method,changed):
            rejects(lambda: own_prediction(runtime,schema,query))
        after = validate_residency(runtime)
        assert after.halted and after.cursor == before.cursor and after.candidates == before.candidates
        assert after.pending.record.target is None and after.pending.record.sources
        assert not after.pending.predictions
        planning = runtime._machine.evaluation_work(schema,cfg.semantics)
        spent = after.resources['spent']['deployment']['work']
        phase_spent = spent-before.resources['spent']['deployment']['work']
        assert phase_spent == planning
        rows.append({'attack':kind,'published_predictions':0,'actual_cursor':after.cursor,
            'spent_deployment_work':spent,'phase_deployment_work':phase_spent,
            'received_context_and_spent_work_retained':True})
    return rows


def guard_cases():
    def forbidden(*args,**kwargs):
        raise AssertionError('unfunded integer partition executed')
    n = 15
    dense = CountState(n,(1,)*(n*(n-1)//2),None,n*(n-1)//2,n*(n-1)//2)
    with patch.object(projected.partition,'decode',forbidden):
        rejects(lambda: projected.prepare(dense,(0,1),DecodeAllowance()),ArithmeticUnresolved)
    # Each block fits8 cells, but the owned convolution also needs its
    # retained response and temporaries. Aggregate work must fit as well.
    chain = CountState(3,(1,0,1),None,2,2)
    for budget in (DecodeAllowance(live_cells=8),DecodeAllowance(arithmetic=10),DecodeAllowance(integer_bits=16)):
        with patch.object(projected.partition,'decode',forbidden):
            rejects(lambda: projected.prepare(chain,(0,2),budget),ArithmeticUnresolved)
    return {'hard_block_preflight_refusals':1,'aggregate_convolution_preflight_refusals':3,
        'unfunded_numerical_kernel_calls':0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = {'status':'PASS_OWNED_QUERY_PROJECTION',
        'scope':'fixed owned exact reference block decoder; full global state retained; no new AMP schedule, total resource or complete-class certificate',
        'structural':structural(),'exhaustive_native':exhaustive_native(),
        'off_path_future_information':future_information(),'off_path_height':off_path_height(),
        'binding_attacks':binding_attacks(),'guard_cases':guard_cases()}
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_QUERY_PROJECTION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
