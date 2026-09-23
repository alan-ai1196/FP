"""Matched complete native learners: global versus projected indexed AMP.

Previously exposed RN-5 tapes; no construction-search or installation claim.
Every registered attempt, numerical refusal and physical failure is retained.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),str(Path(__file__).parent)]
from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy
from fp_reference import indexed_amp as amp, projected_amp
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation
from fp_reference.cuda_prefix import IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.float64_bridge import Float64Contract
from fp_reference.host_resources import HostResourceContract
from audit_indexed_runtime import fixture
from audit_reference_construction import validate_residency
from audit_cuda_runtime import no_device_handles
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job
from joint_model import new_cases, data, support, unseen_pairs, score, AdaptivePosterior, counts_from_training

CASES, MODES = new_cases(), ('global','projected')
CAP, DEADLINE, PACKED, WORK = 16<<30, 7200000, 8<<30, 10**15
ARENA, FRAME, CELLS = 256<<20, 4<<20, 65536
BASELINE = 'evidence/minimal/FP_JOINT_UNCERTAINTY_EXPERIMENT.json'
BASELINE_ANCHOR = '7ebfea1'
DEPENDENCIES = ('src/reference_compiler','scripts','experiments/joint_uncertainty',
    'experiments/adaptive_uncertainty','experiments/relation_noise','theory/numerical_checks',BASELINE)


def git(*args):
    return subprocess.run(('git',*args),cwd=ROOT,capture_output=True,encoding='utf-8',check=True).stdout.strip()


def controls():
    retained = json.loads(git('show',BASELINE_ANCHOR+':'+BASELINE))
    current = json.loads((ROOT/BASELINE).read_text(encoding='utf-8'))
    assert current == retained, 'retained strong controls changed'
    rows = [row for row in retained['workers'] if row.get('kind') == 'posterior' and tuple(row['case']) in CASES]
    assert tuple(tuple(row['case']) for row in rows) == CASES
    for row in rows:
        job = row['completed_job']
        assert row['worker_status'] == 'EXECUTED' and row['rate'] == 'none'
        assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
        assert not job['limit_terminated_processes'] and job['peak_job_commit'] <= job['commit_limit']
        assert row['process_id'] == job['process_id']
        assert row['complete_domain_raw_predictions_checked'] == row['case'][0]**2
    return rows,retained['registration_source']


def scoring_groups(case):
    _, edges, _, _ = data(case)
    n = case[0]
    return (('unseen', unseen_pairs(n, edges)),
            ('full_domain', tuple((i, j) for i in range(n) for j in range(n))))


def setup(case,mode):
    assert case in CASES and mode in MODES
    n = case[0]
    length = 10*len(support(case))+n*n
    cfg,schema,online = fixture(n,length,byte_cap=PACKED,work_cap=WORK)
    cfg = replace(cfg,normalizer_cap=F(18))
    storage = CudaStorageContract(ARENA,2*ARENA,{role:(ARENA,2*ARENA) for role in ('deployment','compiler')})
    kind = IndexedCudaPrefixContract if mode == 'global' else ProjectedIndexedCudaPrefixContract
    cuda = kind(storage,F(1,100),F(1,1000),n=n,phase_output_cells=CELLS,phase_evidence_bytes=FRAME)
    host = HostResourceContract(CAP,{role:CAP for role in ('deployment','compiler')})
    return cfg,schema,online,cuda,CudaCompilerPolicy(()),host


def preflight():
    rows,source = controls()
    cases = []
    for case in CASES:
        a,b = (setup(case,mode) for mode in MODES)
        assert a[:3] == b[:3] and a[4:] == b[4:]
        left,right = vars(a[3]),vars(b[3])
        assert left.keys() == right.keys()
        different = {key for key in left if left[key] != right[key]}
        assert different == {'backend_id','forward_id'}
        _,_,train,evaluation = data(case)
        assert len(evaluation) == case[0]**2 and len(train) == 10*len(support(case))
        baseline = next(row for row in rows if tuple(row['case']) == case)
        assert baseline['counts'] == json.loads(json.dumps(counts_from_training(case[0],train)))
        cases.append({'case':case,'training_events':len(train),'evaluation_events':len(evaluation),
            'native_program_counts':a[1].counts(),
            'reference_control_unseen_CE':baseline['adaptive_exact_unseen']['expected_CE_binary64'],
            'AMP_readout_control_unseen_CE':baseline['adaptive_AMP_unseen']['expected_CE_binary64']})
    assert 'torch' not in sys.modules
    return {'status':'REGISTERED_BEFORE_EXECUTION','cases':cases,'modes':MODES,
        'native_initial_program':'complete indexed literal relation; uniform Gamma; unit-one rate-one simplex U',
        'ordinary_training':True,'profiles':0,'compiler_policy_steps':0,'class_certificate':False,
        'construction_search':'NOT_INVOKED','installations':0,
        'sole_matched_configuration_differences':['CUDA backend_id','CUDA forward_id'],
        'host_job_cap':CAP,'deadline_ms':DEADLINE,'packed_bytes':PACKED,'work_per_role':WORK,
        'arena_bytes':ARENA,'allocator_cap':2*ARENA,'phase_frame_bytes':FRAME,'phase_output_cells':CELLS,
        'reference_integer_bits':32768,'normalizer_cap':18,'activation_cap':8,
        'AMP_state_atol':'1/100','AMP_probability_atol':'1/1000',
        'baseline_journal':BASELINE,'baseline_anchor':git('rev-parse',BASELINE_ANCHOR),
        'baseline_execution_source':source,
        'baseline_scope':'retained full adaptive exact posterior and its actual AMP readout; no new baseline execution or matched memory claim',
        'scientific_scope':'retrospective complete execution and predictive quality on all eight exposed IID RN-5 cases; no population, search or installation claim'}


def audit_prefix(snapshot,case,mode):
    """Independently bind actual history, native count U and fixed RNE phases."""
    n = case[0]
    _,_,train,evaluation = data(case)
    tape = train+evaluation
    schema = IndexedRelation(n)
    edges = tuple(combinations(range(n),2))
    def observed_state(before,i,j,target):
        assert before.pending is None
        return CountState(n,before.counts,(i,j,target),before.cursor+1,before.steps)
    def committed_state(before):
        i,j,target = before.pending
        values = list(before.counts)
        if i != j:
            values[edges.index(tuple(sorted((i,j))))] += 1-2*target
        return CountState(n,tuple(values),None,before.cursor,before.steps+1)
    ids = snapshot.online.data.active.observation_ids
    by_id = {key:event for key,event in zip(ids,tape)}
    observed = {row.observation_id:row for row in snapshot.observations}
    for k,row in enumerate(snapshot.observations):
        i,j,y = tape[k]
        assert row.observation_id == ids[k] and row.target == y
        assert dict(row.sources) == schema.source_row(i*n+j)
    expected = CountState(n,(0,)*(n*(n-1)//2),None,0,0)
    committed = local_commits = 0
    for k,trace in enumerate(snapshot.event_traces):
        assert trace.observation_id == ids[k] and k <= snapshot.cursor
        i,j,y = by_id[trace.observation_id]
        assert trace.before.encoded == expected and trace.prediction.before == expected
        assert trace.prediction.query == (i,j)
        if trace.after_observe is not None:
            following = observed_state(expected,i,j,y)
            assert trace.after_observe.encoded == following
            mass = trace.prediction.masses[y]
            assert trace.after_observe.gradient_forms == (1/mass-F(1,5),F(4,5)-8/mass,F(4,5))
        if trace.after_commit is not None:
            successor = committed_state(following)
            assert trace.after_commit.encoded == successor
            if k < snapshot.cursor:
                expected = successor
                committed += 1
            else:
                assert snapshot.halted is not None
                local_commits += 1
        else:
            assert k == snapshot.cursor and snapshot.halted is not None
    assert committed == snapshot.cursor
    assert len(snapshot.candidates) == 1 and snapshot.candidates[0].learner.encoded == expected
    assert not snapshot.searches and not snapshot.reference_proofs and not snapshot.install_receipts
    assert not snapshot.persistence_identities and snapshot.alpha_spent == 0
    if snapshot.run.closure is not None:
        assert not snapshot.run.closure.decisions
    phases = {phase.object_id:phase for phase in snapshot.cuda.phases}
    planner = amp if mode == 'global' else projected_amp
    ordered = snapshot.cuda.contract.order_search
    histogram_budget = snapshot.cuda.contract.histogram
    kernel, scratch = amp, None
    if histogram_budget is not None:
        from fp_reference import histogram_decoder, histogram_amp
        assert not ordered and mode == 'global'
        planner = kernel = histogram_amp.implementation(histogram_budget)
        engine = histogram_decoder.implementation(histogram_budget)
        scratch = memoryview(bytearray(engine.workspace_bytes(histogram_budget, n=n)))
    assert snapshot.cuda.contract.forward_id == (planner.ORDERED_FORWARD_ID if ordered else planner.FORWARD_ID)
    tolerance = Float64Contract(F(1,100),F(1,1000))
    checked = words = half = maximum_cells = maximum_nodes = maximum_join = maximum_blocks = 0
    maximum_terms = maximum_worlds = maximum_span = 0
    maximum_integer_envelope = maximum_compacted = 0
    failures = []
    for phase in snapshot.cuda.phases:
        if phase.status != 'CHECKED_CUDA_PREFIX_PHASE':
            failures.append({'phase':phase.phase,'status':phase.status,'reason':phase.reason})
            continue
        kind = phase.phase.split(':')[-1]
        before = None if phase.input_phase is None else phases[phase.input_phase].raw_state
        if kind == 'initialize':
            assert phase.raw_state.encoded == CountState(n,(0,)*(n*(n-1)//2),None,0,0)
        elif kind == 'predict':
            i,j,_ = by_id[phase.observation_id]
            sources = schema.source_row(i*n+j)
            if histogram_budget is None:
                planner.check_prediction_plan(phase.execution_plan,schema,before,schema.rules(),sources,
                    output_cap=CELLS,allow_orders=ordered)
            else:
                planner.check_prediction_plan(phase.execution_plan,schema,before,schema.rules(),sources,
                    output_cap=CELLS, budget=histogram_budget, workspace=scratch, bit_limit=32768)
            assert phase.raw_prediction.before == before.encoded and phase.raw_prediction.query == (i,j)
            operations = kernel.check_prediction_execution(phase.execution_plan,before,phase.raw_prediction,
                phase.raw_operations,bit_limit=32768)
            assert phase.forward_operations == operations and phase.output_cells == phase.execution_plan.output_cells
            relation = amp.check_prediction(phase.reference_prediction,phase.raw_prediction,tolerance,
                normalizer_cap=F(18),activation_cap=F(8),bit_limit=32768)
            assert relation == phase.relation
            if histogram_budget is None:
                shape = dict(phase.execution_plan.table_shape)
                maximum_nodes = max(maximum_nodes,len(phase.execution_plan.nodes))
                maximum_join = max(maximum_join,shape['largest_join_cells'])
                maximum_blocks = max(maximum_blocks,shape.get('projected_blocks',0))
            else:
                maximum_terms = max(maximum_terms,phase.execution_plan.term_count)
                stats = engine.table_statistics(phase.execution_plan)
                maximum_worlds = max(maximum_worlds,stats.get('world_visits',0))
                maximum_span = max(maximum_span,phase.execution_plan.span)
                maximum_join = max(maximum_join,stats.get('largest_join_cells',0))
                maximum_integer_envelope = max(maximum_integer_envelope,stats.get('integer_envelope',0))
                maximum_compacted = max(maximum_compacted,stats.get('compacted_cells',0))
        elif kind == 'observe':
            prediction = phases[phase.prediction_phase].raw_prediction
            target = observed[phase.observation_id].target
            amp.check_observation_execution(before,prediction,target,phase.raw_state,phase.raw_operations,bit_limit=32768)
            assert phase.raw_state.encoded == observed_state(before.encoded,*prediction.query,target)
        elif kind == 'commit':
            assert phase.raw_state.encoded == committed_state(before.encoded)
        else:
            raise AssertionError('an undeclared model phase executed')
        if kind != 'predict':
            assert amp.check_state(phase.reference,phase.raw_state,tolerance,bit_limit=32768) == phase.relation
        maximum_cells = max(maximum_cells,phase.output_cells)
        for _,width,values in phase.raw_operations:
            words += len(values)
            half += len(values) if width == 16 else 0
        checked += 1
    if scratch is not None:
        scratch.release()
    return {'native_committed_units':committed,'retained_unpublished_local_commits':local_commits,'checked_CUDA_phases':checked,
        'actual_floating_words':words,'actual_half_words':half,'maximum_prediction_tape_nodes':maximum_nodes,
        'maximum_phase_output_cells':maximum_cells,'maximum_join_cells':maximum_join,
        'maximum_projected_blocks':maximum_blocks,'retained_failed_phases':failures,
        'complete_global_count_coordinates':len(expected.counts),'class_decisions':0,
        'maximum_histogram_terms':maximum_terms,'maximum_histogram_world_visits':maximum_worlds,
        'maximum_histogram_span':maximum_span,
        'maximum_histogram_integer_envelope':maximum_integer_envelope,
        'maximum_histogram_compacted_cells':maximum_compacted}


def worker(case,mode):
    cfg,schema,online,cuda,policy,host = setup(case,mode)
    hidden,edges,train,evaluation = data(case)
    def forbidden(*args,**kwargs):
        raise AssertionError('production materialized the literal native world program or learner')
    with patch.object(IndexedRelation,'materialize_program',forbidden),patch.object(IndexedRelation,'materialize_learner',forbidden):
        rt = ReferenceCompilerRuntime(cfg,schema,online=online,cuda=cuda,policy=policy,host=host)
        base = rt.snapshot().deployed_id
        oracle = AdaptivePosterior(case[0],(),case[1])
        exact, checks, refusal = {},0,None
        for cursor,(i,j,target) in enumerate(train+evaluation):
            event = deliver_context(rt,online.data.active.observation_ids[cursor],tuple(schema.source_row(i*schema.n+j).values()))
            if event.status != 'PREDICTED_REFERENCE':
                assert event.status == 'UNRESOLVED',event
                refusal = {'stage':'predict','cursor':cursor,'query':[i,j],'reason':event.reason}
                break
            expected = oracle.predict(i,j)
            assert dict(event.predictions)[base] == expected, 'native reference differs from the independent full posterior'
            checks += 1
            if cursor >= len(train):
                exact[i,j] = expected
            result = rt.observe(target)
            if result.status != 'OBSERVED_REFERENCE':
                assert result.status == 'UNRESOLVED',result
                refusal = {'stage':'observe','cursor':cursor,'query':[i,j],'reason':result.reason}
                break
            oracle.observe(target)
            if (cursor+1) % 20 == 0:
                print('MODEL '+mode+' '+str(case)+' cursor '+str(cursor+1),flush=True)
        snapshot = validate_residency(rt)
        no_device_handles(snapshot)
        complete = snapshot.run.status == 'SEALED_CUDA_STREAM' and snapshot.halted is None
        assert complete or snapshot.run.status == 'HALTED_UNRESOLVED'
        if complete:
            assert snapshot.cursor == len(train)+len(evaluation) and oracle.pending is None
        audit = audit_prefix(snapshot,case,mode)
        readouts,proper,raw = [],{},{}
        eval_ids = {online.data.active.observation_ids[len(train)+k]:event[:2] for k,event in enumerate(evaluation)}
        for phase in snapshot.cuda.phases:
            if phase.phase != 'ordinary:predict' or phase.observation_id not in eval_ids or phase.status != 'CHECKED_CUDA_PREFIX_PHASE':
                continue
            pair = eval_ids[phase.observation_id]
            if pair not in exact:
                continue
            words = phase.raw_prediction.words
            masses = tuple(amp.single(word) for word in words[2:4])
            proper[pair] = tuple(v/sum(masses) for v in masses)
            raw[pair] = tuple(amp.single(word) for word in words[5:])
            readouts.append(list(words[2:4]+words[5:]))
        scores = {}
        if complete:
            assert len(readouts) == len(exact) == len(evaluation)
            for name,pairs in scoring_groups(case):
                scores['reference_'+name] = score(exact,None,hidden,pairs)
                scores['AMP_'+name] = score(proper,raw,hidden,pairs)
        result = {'status':'COMPLETE_MODEL' if complete else 'UNRESOLVED_MODEL','case':case,'mode':mode,
            'process_id':os.getpid(),'run_status':snapshot.run.status,'cursor':snapshot.cursor,'refusal':refusal,
            'received_pending_target':None if snapshot.pending is None else snapshot.pending.record.target,
            'training_events':len(train),'evaluation_events':len(evaluation),'reference_posterior_checks':checks,
            'completed_evaluation_predictions':len(readouts),'scores':scores,'evaluation_readouts':readouts,
            'audit':audit,'initial_program_is_deployment':snapshot.deployed_id == base,'class_certificate':False,
            'construction_search':'NOT_INVOKED','installations':0,'alpha_spent':'0',
            'packed_peak':snapshot.resources['peak']['reference_payload_bytes'],
            'packed_current':snapshot.resources['current']['reference_payload_bytes'],
            'consumed_arena_bytes':snapshot.cuda.storage['consumed_arena_extent'],
            'declared_forward_id':snapshot.cuda.contract.forward_id,
            'oracle_scope':getattr(oracle, 'scope', 'independent full-assignment integer posterior; no values supplied to Runtime'),
            'oracle_assignment_visits':oracle.work,
            'oracle_statistics':oracle.statistics() if hasattr(oracle, 'statistics') else None}
        return result


def compare_score(actual,expected):
    assert actual.keys() == expected.keys()
    for key,value in actual.items():
        if type(value) is float:
            assert abs(value-expected[key]) <= 1e-12,(key,value,expected[key])
        else:
            assert value == expected[key],(key,value,expected[key])


def read_result(result,case,mode,baseline):
    assert result['case'] == list(case) and result['mode'] == mode
    assert result['status'] in ('COMPLETE_MODEL','UNRESOLVED_MODEL')
    assert not result['class_certificate'] and result['construction_search'] == 'NOT_INVOKED'
    assert result['installations'] == 0 and result['alpha_spent'] == '0' and result['initial_program_is_deployment']
    assert result['audit']['complete_global_count_coordinates'] == case[0]*(case[0]-1)//2
    assert result['audit']['native_committed_units'] == result['cursor'] and result['audit']['class_decisions'] == 0
    hidden,edges,train,evaluation = data(case)
    readouts = result['evaluation_readouts']
    assert len(readouts) == result['completed_evaluation_predictions'] <= len(evaluation)
    assert result['packed_peak'] <= PACKED and result['consumed_arena_bytes'] <= ARENA
    if result['status'] != 'COMPLETE_MODEL':
        assert result['scores'] == {} and result['run_status'] == 'HALTED_UNRESOLVED'
        return {'status':'VALIDATED_UNRESOLVED_PREFIX','complete_model_scores':0}
    assert result['run_status'] == 'SEALED_CUDA_STREAM' and result['refusal'] is None
    assert result['cursor'] == result['reference_posterior_checks'] == len(train)+len(evaluation)
    assert not result['audit']['retained_failed_phases'] and len(readouts) == len(evaluation)
    assert result['audit']['checked_CUDA_phases'] == 1+3*result['cursor']
    proper,raw = {},{}
    for (i,j,_),words in zip(evaluation,readouts):
        assert type(words) is list and len(words) == 4
        masses = tuple(amp.single(word) for word in words[:2])
        proper[i,j] = tuple(m/sum(masses) for m in masses)
        raw[i,j] = tuple(amp.single(word) for word in words[2:])
    for name,pairs in scoring_groups(case):
        compare_score(result['scores']['AMP_'+name],score(proper,raw,hidden,pairs))
        compare_score(result['scores']['reference_'+name],baseline['adaptive_exact_'+name])
    return {'status':'PASS_COMPLETE_MODEL_READER','actual_readout_pairs_recomputed':len(readouts),
        'retained_exact_posterior_score_controls_checked':2,'decision_class':'empty registered compiler policy; no optimization certificate'}


def matrix(attempt):
    assert attempt > 0
    output = ROOT/f'evidence/minimal/FP_INDEXED_MODEL_A{attempt}.json'
    assert not output.exists(), 'executed or pending attempts are never overwritten or silently restarted'
    source = git('rev-parse','HEAD')
    def clean():
        assert git('rev-parse','HEAD') == source
        assert not git('status','--porcelain','--',*DEPENDENCIES), 'commit every execution input first'
    clean()
    registration = preflight()
    baselines,_ = controls()
    report = {'status':'REGISTERED_NOT_COMPLETED','execution_source':source,'registration':registration,'workers':[]}
    def publish():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        temporary.replace(output)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-indexed-model-',dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    stop = False
    for index,case in enumerate(CASES):
        for mode in MODES:
            raw_path = directory/(str(index)+'-'+mode+'.json')
            row = {'case':case,'mode':mode,'execution_source':source,'worker_status':'FAILED'}
            print('START '+str(case)+' '+mode,flush=True)
            try:
                job = run_in_job(str(Path(__file__).resolve()),('--worker',index,'--mode',mode,'--output',raw_path),
                    commit_limit=CAP,timeout_ms=DEADLINE)
                row['completed_job'] = asdict(job)
                if raw_path.exists():
                    raw = raw_path.read_bytes()
                    assert len(raw) <= 262144, 'bounded complete scalar evidence required'
                    row['raw_result_bytes'] = len(raw)
                    row['result'] = json.loads(raw)
                # Retain completed physical execution before its reader.
                report['workers'].append(row)
                publish()
                clean()
                if job.timed_out or job.limit_terminated_processes:
                    row['worker_status'] = 'RESOURCE_TERMINATED'
                elif job.exit_code == 0:
                    result = row['result']
                    assert job.attached_before_resume and job.peak_job_commit <= CAP
                    assert result['process_id'] == job.process_id
                    baseline = next(value for value in baselines if tuple(value['case']) == case)
                    row['reader'] = read_result(result,case,mode,baseline)
                    row['worker_status'] = result['status']
                else:
                    stop = True
            except Exception:
                if not any(value is row for value in report['workers']):
                    report['workers'].append(row)
                row['collection_traceback'] = traceback.format_exc()
                stop = True
            publish()
            print(row['worker_status']+' '+str(case)+' '+mode,flush=True)
            if raw_path.exists():
                assert raw_path.resolve().parent == directory
                raw_path.unlink()
            if stop:
                break
        if stop:
            break
    report['status'] = ('STOPPED_EXECUTION_OR_AUDIT_FAILURE' if stop else
        'COMPLETE_WITH_UNRESOLVED' if any(row['worker_status'] != 'COMPLETE_MODEL' for row in report['workers']) else 'COMPLETE_EXECUTION')
    publish()
    assert directory.parent == ROOT.resolve()
    directory.rmdir()
    print(json.dumps({'status':report['status'],'workers':len(report['workers'])}),flush=True)
    if stop:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--attempt',type=int)
    parser.add_argument('--worker',type=int,choices=range(len(CASES)))
    parser.add_argument('--mode',choices=MODES)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.worker is not None:
        if args.mode is None or args.output is None:
            parser.error('--worker requires --mode and --output')
        result = {'status':'FAILED_AUDIT','process_id':os.getpid(),'case':CASES[args.worker],'mode':args.mode}
        try:
            result = worker(CASES[args.worker],args.mode)
        except Exception:
            result['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':result['status'],'case':result['case'],'mode':args.mode}),flush=True)
        if result['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(),indent=2))
    elif args.attempt is not None:
        matrix(args.attempt)
    else:
        parser.error('select --preflight, --attempt, or --worker')
