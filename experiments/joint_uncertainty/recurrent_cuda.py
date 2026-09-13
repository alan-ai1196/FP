"""Source-bound native finite-window posterior on the owned RTX 3090 path.

The 48 rounded-interpreter controls and one explicit suffix control are fixed
before target execution. Each worker starts inside a fresh process/job fence.
The shared-board contract does not assert exclusive GPU availability or speed.
"""
from dataclasses import asdict
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import tempfile
import traceback

import recurrent_control as control
from fp_reference import ReferenceCompilerRuntime,CudaCompilerPolicy
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.cuda_prefix import output_cells
from fp_reference.host_resources import HostResourceContract
from audit_cuda_runtime import cuda_contract,audit_snapshot,HALF,SINGLE
from audit_cuda_policy_run import owned
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

ROOT=control.ROOT
OUTPUT=ROOT/'evidence/minimal/FP_NATIVE_RECURRENT_POSTERIOR_CUDA_AUDIT.json'
HOST_CAP=4<<30
TIMEOUT=120000
DEPENDENCIES=control.DEPENDENCIES+('experiments/joint_uncertainty/recurrent_cuda.py',)
QUERIES=(((0,1),(1,2),(0,2),(0,1)),((0,1),(0,1),(1,2),(0,2)),
         ((0,0),(0,1),(1,1),(0,1)))
CASES=tuple((3,tuple((i,j,y) for (i,j),y in zip(queries,labels)))
    for queries,labels in product(QUERIES,product((0,1),repeat=4)))+(
        (2,((0,1,0),(0,1,0),(0,1,1),(0,1,0))),)


def device_contract():
    return cuda_contract(install=CudaInstallContract())


def preflight():
    cuda=device_contract()
    bounds=[]
    for window in (2,3):
        cfg,graph,online,_=control.fixture(window=window,horizon=4)
        cells={kind:output_cells(kind,graph,cfg.semantics,online.learner)
            for kind in ('initialize','predict','observe','commit')}
        assert max(cells.values())<=cuda.phase_output_cells
        bounds.append({'window':window,'normalizer_and_activation_cap':str(cfg.normalizer_cap),
            'graph':graph.counts(),'output_cells':cells})
    assert len(CASES)==49
    return {'workers':len(CASES),'ordinary_events_per_worker':4,'host_cap':HOST_CAP,
        'timeout_ms':TIMEOUT,'packed_cap':256<<20,'work_per_role':10**10,
        'arena_bytes':cuda.storage.arena_bytes,'allocator_reserved_cap':cuda.storage.allocator_reserved_cap,
        'phase_output_cells':cuda.phase_output_cells,'phase_evidence_bytes':cuda.phase_evidence_bytes,
        'state_native_normalizer_tolerance':str(cuda.state_atol),'probability_tolerance':str(cuda.probability_atol),
        'board_vram_upper':cuda.device.vram_cap,'execution_identity':cuda.execution_identity,'bounds':bounds}


def worker(index):
    window,sequence=CASES[index]
    cfg,graph,online,_=control.fixture(window=window,horizon=4)
    rt=ReferenceCompilerRuntime(cfg,graph,online=online,policy=CudaCompilerPolicy(()),
        cuda=device_contract(),host=HostResourceContract(HOST_CAP,{'deployment':HOST_CAP,'compiler':HOST_CAP}))
    history=[];forecasts=[];maximum_division=F(0)
    for cursor,(i,j,label) in enumerate(sequence):
        forecast=deliver_context(rt,f'bayes-{cursor}',control.context(3,i,j))
        if forecast.status!='PREDICTED_REFERENCE':
            assert forecast.status=='UNRESOLVED'
            break
        pending=rt.snapshot()
        expected=control.posterior(3,history[-window:],i,j)
        assert dict(forecast.predictions)[pending.deployed_id]==expected
        assert pending.pending.record.target is None
        actual=next(p for p in reversed(pending.cuda.phases) if p.raw_prediction is not None
            and p.observation_id==f'bayes-{cursor}' and p.candidate_id==pending.deployed_id)
        assert actual.status=='CHECKED_CUDA_PREFIX_PHASE'
        masses=tuple(SINGLE.decode(v) for v in actual.raw_prediction[3])
        assert masses==actual.reference_prediction.masses
        assert tuple(v/sum(masses) for v in masses)==expected
        delayed=tuple((key,tuple(HALF.decode(v) for v in row)) for key,row in actual.raw_prediction[6])
        assert delayed==actual.reference_prediction.delayed
        raw=tuple(SINGLE.decode(v) for v in actual.raw_prediction[5])
        maximum_division=max(maximum_division,*(abs(a-b) for a,b in zip(raw,expected)))
        forecasts.append(str(expected[0]))
        if index==48 and cursor==3:
            assert expected==(F(1,2),F(1,2)) and control.posterior(3,history,i,j)==(F(41,50),F(9,50))
        observed=rt.observe(label)
        if observed.status!='OBSERVED_REFERENCE':
            assert observed.status=='UNRESOLVED'
            break
        history.append((i,j,label))
    final=owned(rt)
    complete=final.run.status=='SEALED_CUDA_STREAM' and final.halted is None
    assert complete or final.run.status=='HALTED_UNRESOLVED'
    assert not final.install_receipts and not final.reference_proofs
    assert final.candidates[0].theta==(F(1),F(8))
    cuda_audit=audit_snapshot(rt) if complete else None
    cpu_phases=replay(rt)[0] if complete else None
    if complete:
        assert len(final.observations)==4 and len(forecasts)==4
        assert tuple(r.target for r in final.observations)==tuple(r[2] for r in sequence)
        assert cuda_audit['phases']==cpu_phases==13
    final=owned(rt)
    host=final.host_resources
    maxima=lambda traces:{key:str(max((getattr(t.relation,key) for t in traces if t.relation is not None),default=F(0)))
        for key in ('state_error','native_error','normalizer_error','probability_error','division_error')}
    return {'run_status':final.run.status,'halted':final.halted,'window':window,
        'reference_and_actual_mass_forecasts_p0':forecasts,'retained_observations':len(final.observations),
        'maximum_raw_division_error':str(maximum_division),'CUDA_audit':cuda_audit,
        'independent_binary64_phases':cpu_phases,'CUDA_relation_maxima':maxima(final.cuda.phases),
        'binary64_relation_maxima':maxima(final.float64_traces),
        'packed_peak':final.resources['peak']['reference_payload_bytes'],
        'consumed_arena_extent':final.cuda.storage['consumed_arena_extent'],
        'class_or_install_certificate':False,
        'host':{key:getattr(host,key) for key in ('process_id','creation_100ns','lifetime_process_commit_peak',
            'job_commit_peak','process_user_100ns','process_kernel_100ns','job_user_100ns','job_kernel_100ns')},
        'device':{'identity':asdict(final.cuda.device.identity),'execution_identity':final.cuda.contract.execution_identity,
            'physical_vram_upper':final.cuda.device.physical_vram_upper,'scope':final.cuda.device.scope}}


def summary(report):
    successful=[r['result'] for r in report['workers'] if r['worker_status']=='EXECUTED']
    return {'status':report['status'],'attempts':len(report['workers']),
        'failed_jobs':sum(r['worker_status']=='FAILED' for r in report['workers']),
        'sealed_streams':sum(r['run_status']=='SEALED_CUDA_STREAM' for r in successful),
        'unresolved_streams':sum(r['run_status']=='HALTED_UNRESOLVED' for r in successful),
        'independent_CUDA_phases':sum(r['CUDA_audit']['phases'] for r in successful if r['CUDA_audit'] is not None),
        'independent_binary64_phases':sum(r['independent_binary64_phases'] or 0 for r in successful),
        'forecasts_in_sealed_streams':sum(len(r['reference_and_actual_mass_forecasts_p0']) for r in successful if r['run_status']=='SEALED_CUDA_STREAM'),
        'maximum_completed_job_commit':max((r['completed_job']['peak_job_commit'] for r in report['workers']),default=0)}


def run(write,resume):
    source=control.git('rev-parse','HEAD')
    def source_clean():
        assert control.git('rev-parse','HEAD')==source
        assert not control.git('status','--porcelain','--',*DEPENDENCIES)
    source_clean()
    registration=json.loads(json.dumps(preflight()))
    if resume:
        report=json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status']=='PARTIAL_EXECUTION' and report['registration_source']==source
        assert report['registration']==registration
        assert [r['case_index'] for r in report['workers']]==list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(),'retain the existing journal; do not silently rerun workers'
        report={'status':'PARTIAL_EXECUTION','registration_source':source,'registration':registration,
            'scope':'initial known-prior native finite-window model; actual owned AMP and binary64; no construction/install/class optimum or timing comparison',
            'device':None,'workers':[]}
    def publish():
        if write:
            temporary=OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']),len(CASES)):
        with tempfile.TemporaryDirectory(prefix='fp-recurrent-cuda-',dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent==ROOT.resolve()
            output=Path(temporary)/'result.json'
            job=run_in_job(__file__,('--worker',index,'--output',output),commit_limit=HOST_CAP,timeout_ms=TIMEOUT)
            row={'case_index':index,'completed_job':asdict(job),'worker_status':'FAILED'}
            try:
                if output.exists():
                    with output.open('rb') as stream:
                        payload=stream.read(32769)
                    assert len(payload)<=32768
                    row['result']=json.loads(payload)
                if job.exit_code==0 and not job.timed_out:
                    observed=row['result']['host']
                    assert job.attached_before_resume and not job.limit_terminated_processes
                    assert (observed['process_id'],observed['creation_100ns'])==(job.process_id,job.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak']<=job.peak_process_commit<=HOST_CAP
                    assert observed['job_commit_peak']<=job.peak_job_commit<=HOST_CAP
                    for clock in ('user','kernel'):
                        assert max(observed[f'process_{clock}_100ns'],observed[f'job_{clock}_100ns'])<=getattr(job,f'{clock}_100ns')
                    device=row['result']['device']
                    if report['device'] is None:
                        report['device']=device
                    assert device==report['device']
                    del row['result']['device']
                    row['device_matches_common_identity']=True
                    row['worker_status']='EXECUTED'
            except Exception:
                row['audit_failure']=traceback.format_exc()
            report['workers'].append(row)
        source_clean()
        publish()
        print(json.dumps({'case':index,'worker_status':row['worker_status'],
            'run_status':row.get('result',{}).get('run_status')}),flush=True)
    report['status']='COMPLETE_EXECUTION'
    publish()
    return summary(report)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--worker',type=int,choices=range(len(CASES)))
    parser.add_argument('--output')
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    assert not args.resume or args.write
    assert bool(args.output)==(args.worker is not None)
    if args.worker is not None:
        assert not (args.preflight or args.write or args.resume)
        try:
            result=worker(args.worker)
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback':traceback.format_exc()}),encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8')
    elif args.preflight:
        assert not (args.write or args.resume)
        print(json.dumps(preflight(),indent=2))
    else:
        print(json.dumps(run(args.write,args.resume),indent=2))
