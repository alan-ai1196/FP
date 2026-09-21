"""Supplied-input alias attacks against real owned indexed predictions.

No owner globals, stack inspection, numerical kernel or byte encoder is
changed. The helper mutates only its supplied source mapping or count record.
CPU Runtime evidence and actual fresh-CUDA evidence have separate scopes.
"""
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime,indexed_amp as amp
from fp_reference.indexed_execution import IndexedReferenceMachine
from fp_reference.encoding import pack
from fp_reference.semantics import evaluate
from fp_reference.learner import observe_event,commit_event
from fp_reference import phase_deflate
from audit_indexed_runtime import fixture,literal
from audit_reference_construction import validate_residency,rejects
from audit_cuda_runtime import phase_payload
from ingress_audit_support import deliver_context
import audit_indexed_amp as indexed
import audit_phase_writer_binding as runner

CASES = ('planner-sources','planner-counts','executor-counts')


def predict(rt,schema,query):
    snapshot = rt.snapshot()
    key = snapshot.online.data.active.observation_ids[snapshot.cursor]
    return deliver_context(rt,key,tuple(schema.source_row(query[0]*schema.n+query[1]).values()))


def native(schema,history,query):
    rules,graph,spec,state = literal(schema.n)
    for i,j,y in history:
        prediction = evaluate(graph,rules,state.theta,schema.source_row(i*schema.n+j),(),bit_limit=32768)
        state = commit_event(observe_event(graph,state,spec,prediction,y,bit_limit=32768),spec,bit_limit=32768)
    prediction = evaluate(graph,rules,state.theta,schema.source_row(query[0]*schema.n+query[1]),(),bit_limit=32768)
    return prediction,state


def probe(case,*,cuda=False):
    if cuda:
        rt,schema = indexed.configuration(3,2,evidence_encoding=phase_deflate.ENCODING_ID)
    else:
        cfg,schema,online = fixture(3,2)
        rt = ReferenceCompilerRuntime(cfg,schema,online=online)
    assert predict(rt,schema,(1,2)).status=='PREDICTED_REFERENCE'
    assert rt.observe(0).status=='OBSERVED_REFERENCE'
    before = validate_residency(rt)
    saved_native = pack(before.candidates[0].learner)
    prior_counts = before.candidates[0].learner.encoded.counts
    assert prior_counts==(0,0,1)
    query = (0,1) if case=='planner-sources' else (1,2)
    expected,_ = native(schema,((1,2,0),),query)
    method = 'execute_prediction' if case=='executor-counts' else 'prepare_prediction'
    honest = getattr(IndexedReferenceMachine,method)
    touched = []
    def altered(machine,*args,**kwargs):
        assert not touched
        if case=='planner-sources':
            program,rules,state,sources = args
            assert program.source_query(rules,sources)[0]==query
            sources.clear()
            sources.update(program.source_row(5))
            touched.append('ordinary writes to the supplied mapping only')
        else:
            encoded = args[0].before if case=='executor-counts' else args[2].encoded
            assert encoded.counts==prior_counts
            object.__setattr__(encoded,'counts',(0,0,-1))
            touched.append('mutation of the supplied CountState only')
        return honest(machine,*args,**kwargs)
    failure = None
    with patch.object(IndexedReferenceMachine,method,altered):
        try:
            result = predict(rt,schema,query)
        except Exception as exc:
            result = None
            failure = type(exc).__name__+': '+str(exc)
    after = validate_residency(rt)
    assert len(touched)==1 and after.cursor==1 and after.pending.record.target is None
    recorded_query = schema.source_query(schema.rules(),dict(after.pending.record.sources))[0]
    assert recorded_query==query
    published = bool(after.pending.predictions)
    if cuda and case!='planner-sources':
        assert failure and result is None and not published and after.halted
        phase = after.cuda.phases[-1]
        assert phase.status=='EXECUTION_FAILED'
        prediction = phase.reference_prediction
    else:
        assert failure is None and result.status=='PREDICTED_REFERENCE' and published
        prediction = after.pending.predictions[0][1]
    assert prediction.probabilities!=expected.probabilities
    mutated = pack(before.candidates[0].learner)!=saved_native
    assert mutated==(case!='planner-sources')
    row = {'case':case,'status':'OWNED_INPUT_ALIAS_COUNTEREXAMPLE',
        'method':method,'only_mutated_argument':touched[0],
        'recorded_actual_query':recorded_query,'produced_reference_query':prediction.query,
        'legal_history_probabilities':tuple(map(str,expected.probabilities)),
        'produced_reference_probabilities':tuple(map(str,prediction.probabilities)),
        'published_prediction':published,'prediction_status':None if result is None else result.status,
        'failure':failure,'original_counts':prior_counts,
        'retained_counts_before_next_target':after.candidates[0].learner.encoded.counts,
        'earlier_snapshot_native_payload_changed':mutated,
        'pre_target_cursor':after.cursor,'pre_target_received_target':after.pending.record.target}
    if cuda:
        phase = after.cuda.phases[-1]
        row['phase_status'] = phase.status
        if case=='planner-sources':
            assert phase.status=='CHECKED_CUDA_PREFIX_PHASE' and phase.raw_prediction.query==(1,2)
            rejects(lambda:amp.check_prediction_plan(phase.execution_plan,schema,
                amp.IndexedAmpState(phase.raw_prediction.before),schema.rules(),schema.source_row(1),output_cap=65536))
            row['actual_source_rejects_checked_AMP_plan'] = True
            row['published_AMP_probabilities'] = tuple(str(amp.single(w)) for w in phase.raw_prediction.words[-2:])
        buffers = dict(after.buffers)
        sealed = [p for p in after.cuda.phases if type(rt._buffers[p.object_id]) is bytes]
        mismatches = sum(phase_payload(after,buffers[p.object_id])!=pack(p) for p in sealed)
        row['older_sealed_records_no_longer_matching_live_metadata'] = mismatches
        assert (mismatches>0)==mutated
    if case=='planner-sources':
        # Record the pre-target forgery first, then check a complete real
        # observation/commit against the unchanged literal native learner.
        assert rt.observe(0).status=='OBSERVED_REFERENCE'
        final = validate_residency(rt)
        _,legal_state = native(schema,((1,2,0),(0,1,0)),(0,1))
        actual_state = final.candidates[0].learner.materialize(scalar_cap=1000)
        assert final.cursor==2 and final.candidates[0].learner.encoded.counts==(0,0,2)
        assert actual_state.theta!=legal_state.theta
        row['continuation'] = {'actual_received_history':((1,2,0),(0,1,0)),
            'legal_counts':(1,0,1),'published_counts':(0,0,2),'cursor':2,
            'literal_native_theta':tuple(map(str,legal_state.theta)),
            'published_native_theta':tuple(map(str,actual_state.theta)),
            'full_native_update_is_wrong':True}
        if cuda:
            assert dict(final.cuda.current)[final.deployed_id]==final.cuda.phases[-1].object_id
            assert final.cuda.phases[-1].raw_state.encoded.counts==(0,0,2)
            row['continuation']['published_AMP_commit_is_wrong'] = True
    return row


def preflight():
    assert 'torch' not in sys.modules
    return {'status':'REGISTERED_BEFORE_ACTUAL_INDEXED_INPUT_ALIAS_PROBES','cases':CASES,
        'production_anchor':'a559d7a','job_cap':indexed.CAP,'deadline_ms':900000,
        'unchanged':['production','native learner','byte-only evidence codec','RNE checks','numerical tolerances'],
        'faults':'only supplied source mapping or CountState; no owner globals, stack or arbitrary process memory',
        'expected_source_case':'false source-bound prediction and complete native/AMP update',
        'expected_count_cases':'AMP refuses count mismatch but live native history and earlier snapshots are corrupted',
        'not_claimed':['Foundation counterexample','optimization completeness','false fresh-evidence certificate','installation']}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--attempt',type=int)
    parser.add_argument('--worker',choices=CASES)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        result = {'status':'FAILED_AUDIT','case':args.worker,'process_id':os.getpid()}
        try:
            result.update(status='ACTUAL_INDEXED_SOURCE_ALIAS_COUNTEREXAMPLE',result=probe(args.worker,cuda=True))
        except Exception:
            result['status']='FAILED_AUDIT'
            result['traceback']=traceback.format_exc()
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        if result['status']=='FAILED_AUDIT':
            raise SystemExit(1)
    elif args.cpu:
        result = {'status':'FALSIFIED_OWNED_REFERENCE_INPUT_BINDING','scope':'actual CPU Runtime; no numerical owner mock',
            'production_source':runner.registration.model.git('rev-parse','HEAD'),
            'rows':[probe(case) for case in CASES]}
        assert 'torch' not in sys.modules
        output = args.output or ROOT/'evidence/minimal/FP_INDEXED_SOURCE_ALIAS_CPU.json'
        if output.exists():
            old = json.loads(output.read_text(encoding='utf-8'))
            result['production_source'] = old['production_source']
            assert old==json.loads(json.dumps(result))
        else:
            output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    elif args.preflight:
        print(json.dumps(preflight(),indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt,script=__file__,cases=CASES,journal_prefix='FP_INDEXED_SOURCE_ALIAS_CUDA',
            registration_fn=preflight,production_anchor='a559d7a',
            result_status='ACTUAL_INDEXED_SOURCE_ALIAS_COUNTEREXAMPLE',final_status='FALSIFIED_OWNED_INDEXED_INPUT_BINDING')
    else:
        parser.error('select --cpu, --preflight, --attempt or --worker')
