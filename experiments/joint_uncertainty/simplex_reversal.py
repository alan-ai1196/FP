"""Registered dynamic underflow/reversal audit of the owned simplex learner.

The blind rounded continuation is an independent numerical counterexample;
the real Runtime must retain the failed prefix and stop before the next label.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),str(Path(__file__).resolve().parent)]
import simplex_gradient as exact
from predictive_counts import normalize,weights_from_history
from audit_simplex_learner import fixture,HOST_CAPS,TIMEOUT
from audit_reference_construction import validate_residency
from audit_float64_runtime import replay
from audit_cuda_learner import model_initial,model_predict,model_observe,model_commit
from audit_cuda_runtime import raw_model,raw_model_prediction,cuda_contract,no_device_handles
from ingress_audit_support import deliver_context
from fp_reference import ReferenceCompilerRuntime,CompilerPolicy,CudaCompilerPolicy
from fp_reference.data_usage import StreamSpec
from fp_reference.encoding import pack
from fp_reference.host_resources import HostResourceContract
from fp_reference.learner import ce_gradient
from fp_reference.cuda_prefix import output_cells

TAPE = ((0,1,0),)*50+((0,1,1),)*50
OUTPUT = ROOT/'evidence/minimal/FP_SIMPLEX_REVERSAL_AUDIT.json'
DEPENDENCIES = ('src/reference_compiler','scripts',
    'experiments/joint_uncertainty/simplex_gradient.py','experiments/joint_uncertainty/predictive_counts.py',
    'experiments/joint_uncertainty/simplex_reversal.py','theory/proofs/SIMPLEX_REVERSAL.md')


def configuration():
    cfg,graph,online,_ = fixture(2)
    ids = tuple(f'reversal-{i}' for i in range(len(TAPE)))
    data = replace(online.data,streams=(StreamSpec('online','online',ids),))
    return cfg,graph,replace(online,data=data,profiles=())


def preflight():
    cfg,graph,online = configuration()
    amp = model_initial(graph,cfg.semantics,cfg.initializer_pattern)
    history = (); first_zero = first_violation = None
    for at,(i,j,y) in enumerate(TAPE):
        weights = exact.native_history_state(2,history)
        ref = exact.native_prediction(2,weights,(i,j))
        pred = model_predict(graph,cfg.semantics,amp,exact.context(2,i,j))
        native = max(abs(a-b) for key in ('values','excesses','masses')
                     for a,b in zip(getattr(ref,key),pred[key]))
        total = abs(ref.normalizer-pred['normalizer'])
        prob = max(abs(a-b/sum(pred['masses'])) for a,b in zip(ref.probabilities,pred['masses']))
        if first_violation is None and (max(native,total)>F(1,100) or prob>F(1,1000)):
            first_violation = {'phase':'predict','observed_events':at,'native_error':str(native),'probability_error':str(prob)}
        amp = model_observe(graph,amp,pred,y)
        gradient = ce_gradient(graph,(F(1),)+weights,ref,y,bit_limit=32768)
        gerr = max(abs(a-b) for a,b in zip(gradient,amp.gradient))
        if first_violation is None and gerr>F(1,100):
            first_violation = {'phase':'observe','observed_events':at,'state_error':str(gerr)}
        amp = model_commit(amp,online.learner)
        history += ((i,j,y),)
        next_weights = exact.native_history_state(2,history)
        if first_violation is None and max(abs(a-b) for a,b in zip(next_weights,amp.theta[1:]))>F(1,100):
            first_violation = {'phase':'commit','observed_events':at+1}
        if first_zero is None and amp.theta[2]==0:
            first_zero = at+1
    assert first_zero==48 and first_violation=={'phase':'predict','observed_events':97,'native_error':'4/365','probability_error':'2/1825'}
    assert next_weights==(F(1,2),)*2 and amp.theta==(F(1),F(1),F(0))
    assert 'torch' not in sys.modules
    return {'cases':['cpu','cuda'],'tape':'50 copies of (0,1,label0), then 50 copies of (0,1,label1)',
        'ordinary_events':100,'predicted_first_zero_event':first_zero,'predicted_first_violation':first_violation,
        'blind_oracle_final_weights':['1','0'],'exact_final_weights':['1/2','1/2'],
        'blind_scope':'independent rounded arithmetic after refusal; not an owned continuation or a model score',
        'host_caps':HOST_CAPS,'timeout_ms':TIMEOUT,'packed_cap':512<<20,'work_per_role':10**11,
        'integer_bits':32768,'native_caps':'16','binary64_tolerances':'1/1000000000',
        'AMP_state_native_normalizer_tolerance':'1/100','AMP_probability_tolerance':'1/1000',
        'arena_bytes':16<<20,'allocator_bytes':32<<20,'output_cells':4096,'phase_frame_bytes':262144,
        'no_search_profile_persistence_install':True}


def audit_cuda_prefix(rt):
    """Replay every raw phase, retaining and checking the refused prediction."""
    snap = validate_residency(rt)
    no_device_handles(snap)
    assert snap.pending.record.target is None
    records = {r.observation_id:r for r in snap.observations}
    records[snap.pending.record.observation_id] = snap.pending.record
    graphs,buffers = dict(snap.programs),dict(snap.buffers)
    expected = {}; first_zero = None
    for index,phase in enumerate(snap.cuda.phases):
        last = index==len(snap.cuda.phases)-1
        assert phase.status==('UNRESOLVED' if last else 'CHECKED_CUDA_PREFIX_PHASE')
        graph = graphs[phase.program_id]; kind = phase.phase.split(':')[1]
        before = None if phase.input_phase is None else expected[phase.input_phase]
        if kind=='initialize':
            assert phase.reference.theta==rt.contract.initializer_pattern
            result = model_initial(graph,rt.contract.semantics,rt.contract.initializer_pattern,0)
        elif kind=='predict':
            row = records[phase.observation_id]
            result = model_predict(graph,rt.contract.semantics,before,dict(row.sources))
            assert phase.raw_prediction==raw_model_prediction(result) and phase.raw_state==raw_model(before)
            if last:
                assert phase.ordinary_cursor==97 and row.target is None
                native = max(abs(a-b) for key in ('values','excesses','masses')
                    for a,b in zip(getattr(phase.reference_prediction,key),result[key]))
                prob = max(abs(a-b/sum(result['masses'])) for a,b in zip(phase.reference_prediction.probabilities,result['masses']))
                assert native==F(4,365) and prob==F(2,1825)
        elif kind=='observe':
            result = model_observe(graph,before,expected[phase.prediction_phase],records[phase.observation_id].target)
        else:
            assert kind=='commit'
            result = model_commit(before,rt.online_contract.learner)
            if first_zero is None and not result.theta[2]:
                first_zero = phase.reference.cursor
        if kind!='predict':
            assert not last and phase.raw_state==raw_model(result)
        assert phase.output_cells==output_cells(kind,graph,rt.contract.semantics,rt.online_contract.learner)
        frame = buffers[phase.object_id]; size = int.from_bytes(frame[:8],'big')
        assert frame[8:8+size]==pack(phase) and not any(frame[8+size:])
        assert len(frame)==snap.cuda.contract.phase_evidence_bytes and phase.arena_phase is not None
        assert last or phase.relation is not None
        expected[phase.object_id] = result
    assert first_zero==48
    current = expected[dict(snap.cuda.current)[snap.deployed_id]]
    assert current.cursor==97 and current.theta==(F(1),F(1),F(0))
    assert len(snap.cuda.phases)==293
    return {'independent_raw_phases':293,'checked_phases':292,'refused_phase_replayed':True,
            'first_zero_event':first_zero,'native_error':'4/365','mass_normalized_probability_error':'2/1825',
            'maximum_output_cells':max(p.output_cells for p in snap.cuda.phases),
            'maximum_frame_used':max(int.from_bytes(buffers[p.object_id][:8],'big')+8 for p in snap.cuda.phases)}


def worker(path):
    cfg,graph,online = configuration()
    cap = HOST_CAPS[path]
    host = HostResourceContract(cap,{'deployment':cap,'compiler':cap})
    cuda = None if path=='cpu' else cuda_contract(state_atol=F(1,100),probability_atol=F(1,1000),
        phase_output_cells=4096,phase_evidence_bytes=262144)
    policy = CompilerPolicy(()) if cuda is None else CudaCompilerPolicy(())
    rt = ReferenceCompilerRuntime(cfg,graph,online=online,host=host,policy=policy,cuda=cuda)
    forecasts = 0; refusal = None
    for at,(i,j,y) in enumerate(TAPE):
        before = rt.snapshot().candidates
        current = None if cuda is None else rt.snapshot().cuda.current
        event = deliver_context(rt,online.data.active.observation_ids[at],tuple(exact.context(2,i,j).values()))
        if event.status!='PREDICTED_REFERENCE':
            assert path=='cuda' and event.status=='UNRESOLVED' and at==97,event
            snap = rt.snapshot()
            assert snap.candidates==before and snap.cuda.current==current
            assert snap.pending.record.target is None
            refusal = {'phase':'predict','observed_events':at,'reason':event.reason}
            break
        snap = rt.snapshot()
        assert snap.pending.record.target is None
        weights = normalize(weights_from_history(2,TAPE[:at])[:2])
        candidate = next(c for c in snap.candidates if c.candidate_id==snap.deployed_id)
        assert candidate.theta==(F(1),)+weights
        wanted = exact.native_prediction(2,weights,(i,j)).probabilities
        assert dict(event.predictions)[snap.deployed_id]==wanted
        forecasts += 1
        result = rt.observe(y)
        assert result.status=='OBSERVED_REFERENCE',result
    snap = validate_residency(rt)
    assert not snap.install_receipts and not snap.reference_proofs and not snap.persistence_identities
    assert len(snap.observations)==(100 if path=='cpu' else 97)
    if path=='cpu':
        assert refusal is None and snap.run.status=='SEALED_REFERENCE_STREAM' and snap.halted is None
        assert snap.candidates[0].theta==(F(1),F(1,2),F(1,2))
    else:
        assert refusal and snap.halted and not snap.run.status.startswith('SEALED')
        assert snap.candidates[0].theta==(F(1),F(729,730),F(1,730))
    phases = replay(rt)[0]
    cuda_audit = None if cuda is None else audit_cuda_prefix(rt)
    snap = validate_residency(rt)
    host = snap.host_resources
    return {'path':path,'run_status':snap.run.status,'refusal':refusal,'retained_observations':len(snap.observations),
        'reference_posterior_forecasts':forecasts,'independent_binary64_phases':phases,'CUDA_audit':cuda_audit,
        'parameter_values_remain_owned':True,'no_target_revealed_after_refusal':path=='cuda',
        'class_or_install_claim':False,'packed_peak':snap.resources['peak']['reference_payload_bytes'],
        'device':None if cuda is None else {'identity':asdict(snap.cuda.device.identity),
            'execution_identity':snap.cuda.contract.execution_identity,'physical_vram_upper':snap.cuda.device.physical_vram_upper,
            'scope':snap.cuda.device.scope},
        'host':{key:getattr(host,key) for key in ('process_id','creation_100ns','lifetime_process_commit_peak','job_commit_peak',
            'process_user_100ns','process_kernel_100ns','job_user_100ns','job_kernel_100ns')},'process_id':os.getpid()}


def run(write):
    from windows_job_audit_support import run_in_job
    def git(*args):
        return subprocess.run(('git',*args),cwd=ROOT,capture_output=True,encoding='utf-8',check=True).stdout.strip()
    source = git('rev-parse','HEAD')
    def clean():
        assert git('rev-parse','HEAD')==source
        assert not git('status','--porcelain','--',*DEPENDENCIES),'register committed execution dependencies first'
    clean()
    assert not write or not OUTPUT.exists(),'preserve previous outcomes'
    report = {'status':'PARTIAL_EXECUTION','registration_source':source,'registration':preflight(),'workers':[]}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for path in ('cpu','cuda'):
        clean()
        directory = Path(tempfile.mkdtemp(prefix='fp-simplex-reversal-',dir=ROOT))
        assert directory.resolve().parent==ROOT.resolve()
        output = directory/'result.json'
        job = run_in_job(__file__,('--worker',path,'--output',str(output)),commit_limit=HOST_CAPS[path],timeout_ms=TIMEOUT)
        row = {'path':path,'worker_status':'FAILED','execution_source':source,'completed_job':asdict(job)}
        try:
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                assert len(payload)<=65536
                row['result'] = json.loads(payload)
            if job.exit_code==0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes:
                result = row['result']; host = result['host']
                assert result['process_id']==job.process_id
                assert (host['process_id'],host['creation_100ns'])==(job.process_id,job.process_creation_100ns)
                assert host['lifetime_process_commit_peak']<=job.peak_process_commit<=HOST_CAPS[path]
                assert host['job_commit_peak']<=job.peak_job_commit<=HOST_CAPS[path]
                for clock in ('user','kernel'):
                    assert max(host[f'process_{clock}_100ns'],host[f'job_{clock}_100ns'])<=getattr(job,f'{clock}_100ns')
                row['worker_status']='EXECUTED'
        except Exception:
            row['validation_error']=traceback.format_exc()
        report['workers'].append(row)
        clean(); publish()
        if output.exists():
            output.unlink()
        directory.rmdir()
        print(json.dumps({'case':path,'status':row['worker_status']}),flush=True)
    report['status']='COMPLETE_EXECUTION' if all(w['worker_status']=='EXECUTED' for w in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status':report['status'],'workers':len(report['workers'])}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--worker',choices=('cpu','cuda'))
    parser.add_argument('--output')
    args=parser.parse_args()
    assert bool(args.worker)==bool(args.output) and not(args.worker and (args.preflight or args.write))
    if args.worker:
        try:
            result=worker(args.worker)
        except Exception:
            Path(args.output).write_text(json.dumps({'process_id':os.getpid(),'traceback':traceback.format_exc()}),encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8')
    else:
        print(json.dumps(preflight() if args.preflight else run(args.write),indent=2))
