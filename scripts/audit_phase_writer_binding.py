"""Can a lossless writer mutate the record that its own checker trusts?

The byte-codec theorem is conditional on a fixed input. This adversary
changes only the phase object supplied to the writer, never owner globals.
CPU mocked-owner and actual fresh-CUDA outcomes have separate scopes.
"""
from dataclasses import asdict,replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import phase_encoding as codec,indexed_amp as amp
from fp_reference.cuda_prefix import IndexedCudaPhase
from fp_reference.encoding import pack
from fp_reference.core import ContractError
from audit_cuda_runtime import phase_payload
from audit_reference_construction import validate_residency,rejects
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job
import audit_indexed_amp as indexed
import run_phase_encoding as registration

CASES = ('output-count','plan-position')


def corrupting_writer(case,captured):
    original = codec.write
    def write(value,output,**kwargs):
        if type(value) is IndexedCudaPhase and value.phase.endswith(':predict'):
            assert not captured
            old = replace(value,execution_plan=replace(value.execution_plan))
            prior_bytes = pack(value)
            extent = codec.extent(value,encoded_cap=len(output)-kwargs.get('start',0))
            if case=='output-count':
                object.__setattr__(value,'output_cells',value.output_cells-1)
            else:
                assert value.execution_plan.support==((1,2),) and value.execution_plan.positions==(2,)
                object.__setattr__(value.execution_plan,'positions',(0,))
            assert codec.extent(value,encoded_cap=len(output)-kwargs.get('start',0))==extent
            assert pack(value)!=prior_bytes
            captured.append((old,prior_bytes))
        return original(value,output,**kwargs)
    return write


def inspect(case,phase,old,prior_bytes,frame,snapshot=None):
    size = int.from_bytes(frame[:8],'big')
    decoded = (b''.join(codec.decoded_fragments(frame[8:8+size])) if snapshot is None
        else phase_payload(snapshot,frame))
    assert decoded==pack(phase) and decoded!=prior_bytes and not any(frame[8+size:])
    assert phase.raw_prediction==old.raw_prediction and phase.raw_operations==old.raw_operations
    before = amp.IndexedAmpState(old.raw_prediction.before)
    amp.check_prediction_execution(old.execution_plan,before,old.raw_prediction,old.raw_operations,bit_limit=32768)
    if case=='output-count':
        assert phase.output_cells==old.output_cells-1 and phase.execution_plan.output_cells==old.output_cells
        changed = {'actual_plan_output_cells':old.output_cells,'retained_phase_output_cells':phase.output_cells}
    else:
        rejects(lambda:amp.check_prediction_execution(phase.execution_plan,before,
            phase.raw_prediction,phase.raw_operations,bit_limit=32768),ContractError)
        changed = {'support':phase.execution_plan.support,'actual_count_addresses':old.execution_plan.positions,
            'retained_count_addresses':phase.execution_plan.positions,
            'retained_plan_rejects_unchanged_actual_operations':True}
    return {**changed,'decoded_bytes_match_mutated_record':True,
        'decoded_bytes_differ_from_pre_writer_record':True,'raw_readout_and_operations_unchanged':True,
        'encoded_and_expanded_extents_unchanged':True,'padding_unchanged':True}


def cpu():
    from audit_phase_retention import phase_fixture,CountState,retention_fixture,retain
    rows = []
    for case in CASES:
        template,_ = phase_fixture(3,CountState(3,(0,0,1),None,1,1),(0,1),(0,1))
        root,_ = retention_fixture(template)
        captured = []
        with patch.object(codec,'write',corrupting_writer(case,captured)):
            retain(root)
        snapshot = validate_residency(root)
        phase = next(iter(root._cuda.phases.values()))
        assert len(root._cuda.accepted)==1 and len(captured)==1
        assert type(root._buffers[phase.object_id]) is bytes
        rows.append({'case':case,'mocked_owner_accept_calls':1,
            **inspect(case,phase,*captured[0],dict(snapshot.buffers)[phase.object_id])})
    assert 'torch' not in sys.modules
    return {'status':'COUNTEREXAMPLES_IN_REAL_RETENTION_WITH_MOCKED_NUMERICAL_OWNER',
        'scope':'no actual CUDA or complete learner authority; input/output alias in the real retention hook',
        'rows':rows}


def worker(case):
    rt,schema = indexed.configuration(3,2,evidence_encoding=codec.ENCODING_ID)
    if case=='plan-position':
        indexed.step(rt,schema,(1,2,0))
    before = rt.snapshot()
    key = before.online.data.active.observation_ids[before.cursor]
    captured = []
    with patch.object(codec,'write',corrupting_writer(case,captured)):
        result = deliver_context(rt,key,tuple(schema.source_row(1).values()))
    after = validate_residency(rt)
    phase = after.cuda.phases[-1]
    assert result.status=='PREDICTED_REFERENCE' and phase.status=='CHECKED_CUDA_PREFIX_PHASE'
    assert after.cursor==before.cursor and after.pending.record.target is None and after.pending.predictions
    assert after.candidates==before.candidates and after.cuda.current==before.cuda.current
    assert dict(after.cuda.predicted)[after.deployed_id]==phase.object_id
    assert len(captured)==1 and type(rt._buffers[phase.object_id]) is bytes
    details = inspect(case,phase,*captured[0],dict(after.buffers)[phase.object_id],snapshot=after)
    return {'status':'ACTUAL_WRITER_INPUT_ALIAS_COUNTEREXAMPLE','process_id':os.getpid(),'case':case,
        'published_status':result.status,'phase_status':phase.status,'cursor':after.cursor,
        'next_target_revealed':False,'native_learner_advanced':False,
        'phase_output_conformance_or_plan_binding':'FALSE_BUT_ACCEPTED',
        'numerical_point_probability_counterexample':False,**details}


def preflight():
    assert 'torch' not in sys.modules
    return {'cases':CASES,'status':'REGISTERED_BEFORE_ACTUAL_ALIAS_PROBES',
        'production_anchor':'3d3711e','only_injected_interface':'codec.write receives a mutable phase/plan object',
        'attack':'mutate only the supplied input, preserve both declared lengths, then call the honest writer',
        'expected_class':'counterexample to evidence/execution binding, not to byte-codec invertibility',
        'job_cap':indexed.CAP,'deadline_ms':900000,'fresh_owner_per_job':True}


def matrix(attempt, *, script=None, cases=None, journal_prefix='FP_PHASE_WRITER_ALIAS_CUDA',
           registration_fn=None, production_anchor='3d3711e',
           result_status='ACTUAL_WRITER_INPUT_ALIAS_COUNTEREXAMPLE',
           final_status='FALSIFIED_WRITER_INPUT_BINDING'):
    assert attempt>0
    script = Path(__file__).resolve() if script is None else Path(script).resolve()
    cases = CASES if cases is None else cases
    registration_fn = preflight if registration_fn is None else registration_fn
    output = ROOT/f'evidence/minimal/{journal_prefix}_A{attempt}.json'
    assert not output.exists(), 'do not overwrite any actual attempt'
    git = registration.model.git
    source = git('rev-parse','HEAD')
    def clean():
        assert git('rev-parse','HEAD')==source
        assert not git('status','--porcelain','--',*registration.DEPENDENCIES)
        assert not git('diff',production_anchor,'--','src/reference_compiler'), 'probe the unchanged production source'
    clean()
    report = {'status':'REGISTERED_NOT_COMPLETED','execution_source':source,'registration':registration_fn(),'workers':[]}
    def publish():
        temp = output.with_suffix('.tmp')
        temp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        temp.replace(output)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-phase-alias-',dir=ROOT)).resolve()
    assert directory.parent==ROOT.resolve()
    stop = False
    for case in cases:
        path = directory/(case+'.json')
        row = {'case':case,'worker_status':'FAILED'}
        print('START '+case,flush=True)
        try:
            clean()
            job = run_in_job(str(script),('--worker',case,'--output',path),
                commit_limit=indexed.CAP,timeout_ms=900000)
            row['completed_job'] = asdict(job)
            if path.exists():
                raw = path.read_bytes()
                assert len(raw)<=32768
                row['result'] = json.loads(raw)
            report['workers'].append(row)
            publish()
            clean()
            if job.exit_code==0 and not job.timed_out and not job.limit_terminated_processes:
                assert job.attached_before_resume and job.peak_job_commit<=indexed.CAP
                assert row['result']['process_id']==job.process_id
                assert row['result']['status']==result_status
                row['worker_status']='COUNTEREXAMPLE_REPRODUCED'
            else:
                stop = True
        except Exception:
            if not any(item is row for item in report['workers']):
                report['workers'].append(row)
            row['collection_traceback']=traceback.format_exc()
            stop = True
        publish()
        print(row['worker_status']+' '+case,flush=True)
        if path.exists():
            assert path.resolve().parent==directory
            path.unlink()
        if stop:
            break
    report['status']='STOPPED_EXECUTION_OR_AUDIT_FAILURE' if stop else final_status
    publish()
    directory.rmdir()
    if stop:
        raise SystemExit(1)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--attempt',type=int)
    parser.add_argument('--worker',choices=CASES)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.worker:
        if args.output is None:
            parser.error('--worker requires --output')
        result = {'status':'FAILED_AUDIT','case':args.worker,'process_id':os.getpid()}
        try:
            result = worker(args.worker)
        except Exception:
            result['traceback']=traceback.format_exc()
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        if result['status']=='FAILED_AUDIT':
            raise SystemExit(1)
    elif args.cpu:
        result = cpu()
        path = args.output or ROOT/'evidence/minimal/FP_PHASE_WRITER_ALIAS_CPU.json'
        if path.exists():
            assert json.loads(path.read_text())==json.loads(json.dumps(result))
        else:
            path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)
    elif args.preflight:
        print(json.dumps(preflight()),flush=True)
    elif args.attempt is not None:
        matrix(args.attempt)
    else:
        parser.error('select --cpu, --preflight, --attempt or --worker')
