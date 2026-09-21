"""Registered fresh-job CUDA integration for lossless complete phase records.

All inputs must be committed before --attempt. No attempt is overwritten;
model refusals remain outcomes. The numerical owner is never mocked here.
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),
    str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import phase_encoding as codec
from fp_reference.cuda_prefix import LEGACY_PHASE_ENCODING_ID,IndexedCudaPhase
from fp_reference.encoding import pack,packed_size
from audit_reference_construction import validate_residency,rejects
from audit_cuda_runtime import phase_payload
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job
import audit_cuda_runtime as generic
import audit_indexed_amp as indexed
import run_indexed_model as model

CASES = (
    'generic-legacy-profile','generic-binary-profile',
    'indexed-legacy-profiles','indexed-binary-profiles','projected-binary-profiles',
    'indexed-binary-large','projected-binary-install',
    'indexed-binary-endpoint-binding','indexed-binary-plan-binding','projected-binary-foreign-plan',
    'fault-predict-payload','fault-observe-header','fault-observe-padding',
    'fault-predict-extent','fault-predict-resize',
    'model-global-legacy','model-global-binary')
MODEL_CASE = (16,'iid-c2',16)
DEPENDENCIES = model.DEPENDENCIES+('theory/proofs/LOSSLESS_PHASE_ENCODING.md',)


def mode(name):
    return LEGACY_PHASE_ENCODING_ID if 'legacy' in name else codec.ENCODING_ID


def fund_generic(cfg):
    return replace(cfg,limits=replace(cfg.limits,role_cumulative={role:{**caps,'work':10**14}
        for role,caps in cfg.limits.role_cumulative.items()}))


def preflight():
    baseline,_ = model.controls()
    assert any(tuple(row['case'])==MODEL_CASE for row in baseline)
    cfg,schema,online,cuda,policy,host = model.setup(MODEL_CASE,'global')
    binary = replace(cuda,evidence_encoding=codec.ENCODING_ID)
    assert {k for k in vars(cuda) if getattr(cuda,k)!=getattr(binary,k)}=={'evidence_encoding','work_model'}
    assert binary.forward_id==cuda.forward_id and binary.backend_id==cuda.backend_id
    original = generic.configuration()
    funded = fund_generic(original)
    assert funded.limits.global_residency==original.limits.global_residency
    assert funded.limits.role_residency==original.limits.role_residency
    assert all(caps['work']==10**14 for caps in funded.limits.role_cumulative.values())
    for factory in (generic.cuda_contract,):
        old,new = factory(),factory(evidence_encoding=codec.ENCODING_ID)
        assert {k for k in vars(old) if getattr(old,k)!=getattr(new,k)}=={'evidence_encoding','work_model'}
    assert 'torch' not in sys.modules
    return {'status':'REGISTERED_BEFORE_CUDA_EXECUTION','cases':CASES,
        'encoding':codec.ENCODING_ID,'decoded_bytes':'entire legacy typed phase record',
        'expansion_cap':codec.EXPANDED_CAP,'depth_cap':codec.MAX_DEPTH,'string_cap':codec.MAX_STRINGS,
        'integer_bits':codec.INTEGER_BITS,'extra_work_per_phase':'32*134217728 + 16*frame_bytes',
        'fixture_job_cap':indexed.CAP,'fixture_deadline_ms':900000,
        'generic_work_cap_for_both_encodings':10**14,
        'model_case':MODEL_CASE,'model_job_cap':model.CAP,'model_deadline_ms':model.DEADLINE,
        'model_packed_cap':model.PACKED,'model_frame_bytes':model.FRAME,
        'model_output_cells':model.CELLS,'model_work_cap_per_role':model.WORK,
        'matched_changes':['declared evidence encoding','prepaid encoding work tariff'],
        'unchanged':['native G/Gamma/U','source and target tape','physical forward schedule',
            'reference/AMP tolerances','full uniform frame and padding','join/live/tape/output caps'],
        'model_scope':'retrospective n16/c2/16 retention frontier; all original A1 failures retained; no incomplete score',
        'not_claimed':['all n16 completion','whole-memory improvement','new full release','population superiority']}


def frames(rt):
    snapshot = validate_residency(rt)
    buffers = dict(snapshot.buffers)
    sealed = mutable = encoded = expanded = maximum = maximum_old = 0
    for phase in snapshot.cuda.phases:
        frame = buffers[phase.object_id]
        assert len(frame)==snapshot.cuda.contract.phase_evidence_bytes
        if type(rt._buffers[phase.object_id]) is not bytes:
            assert phase.status!='CHECKED_CUDA_PREFIX_PHASE'
            mutable += 1
            continue
        size = int.from_bytes(frame[:8],'big')
        assert phase_payload(snapshot,frame)==pack(phase) and not any(frame[8+size:])
        old = packed_size(phase)
        sealed += 1
        encoded += size
        expanded += old
        maximum,maximum_old = max(maximum,size),max(maximum_old,old)
    return {'sealed_complete_records_checked':sealed,'failed_mutable_frames_retained':mutable,
        'used_payload_bytes':encoded,'reconstructed_legacy_bytes':expanded,
        'largest_payload_bytes':maximum,'largest_legacy_record_bytes':maximum_old,
        'declared_encoding':snapshot.cuda.contract.evidence_encoding,
        'physical_frame_bytes':snapshot.cuda.contract.phase_evidence_bytes,
        'all_padding_and_owned_extents_checked':True}


def fault_worker(name,roots):
    _,stage,attack = name.split('-')
    rt,schema = indexed.configuration(3,2,evidence_encoding=codec.ENCODING_ID)
    roots.append(rt)
    key = rt.snapshot().online.data.active.observation_ids[0]
    context = tuple(schema.source_row(1).values())
    if stage=='observe':
        assert deliver_context(rt,key,context).status=='PREDICTED_REFERENCE'
    before = rt.snapshot()
    write = codec.write
    calls = 0
    def corrupt(value,output,**kwargs):
        nonlocal calls
        extent = write(value,output,**kwargs)
        if type(value) is not IndexedCudaPhase or not value.phase.endswith(':'+stage):
            return extent
        calls += 1
        assert extent.encoded_bytes+8<len(output)
        if attack=='payload':
            output[8+extent.encoded_bytes-1] ^= 1
        elif attack=='header':
            output[0] ^= 1
        elif attack=='padding':
            output[-1] ^= 1
        elif attack=='extent':
            return replace(extent,encoded_bytes=extent.encoded_bytes+1)
        else:
            assert attack=='resize'
            output.obj.append(0)
        return extent
    with patch.object(codec,'write',corrupt):
        rejects(lambda:rt.observe(0) if stage=='observe' else deliver_context(rt,key,context),
            (RuntimeError,BufferError))
    after = validate_residency(rt)
    phase = after.cuda.phases[-1]
    assert calls==1 and phase.status=='EXECUTION_FAILED'
    assert after.cursor==0 and after.candidates==before.candidates and after.cuda.current==before.cuda.current
    assert after.pending.record.target==(0 if stage=='observe' else None)
    if stage=='predict':
        assert not after.pending.predictions
    assert type(rt._buffers[phase.object_id]) is bytearray
    assert len(rt._buffers[phase.object_id])==after.cuda.contract.phase_evidence_bytes
    return {'status':'PASS_WRITER_FAULT_REFUSAL','stage':stage,'attack':attack,
        'phase_status':phase.status,'actual_output_cells_before_writer_fault':phase.output_cells,
        'published_learner_advances':0,'received_target':after.pending.record.target,
        'retained_failed_frame_bytes':len(rt._buffers[phase.object_id])}


def worker(name):
    roots = []
    if name.startswith('fault-'):
        result = fault_worker(name,roots)
    elif name.startswith('generic-'):
        constructor,configuration,contract = generic.ReferenceCompilerRuntime,generic.configuration,generic.cuda_contract
        def capture(*args,**kwargs):
            rt = constructor(*args,**kwargs)
            roots.append(rt)
            return rt
        def funded():
            return fund_generic(configuration())
        def encoded(**kwargs):
            return contract(evidence_encoding=mode(name),**kwargs)
        with patch.object(generic,'ReferenceCompilerRuntime',capture),patch.object(generic,'configuration',funded), \
                patch.object(generic,'cuda_contract',encoded):
            result = generic.profile_case()
    elif name.startswith('model-'):
        setup,constructor = model.setup,model.ReferenceCompilerRuntime
        def configuration(*args):
            cfg,schema,online,cuda,policy,host = setup(*args)
            return cfg,schema,online,replace(cuda,evidence_encoding=mode(name)),policy,host
        def capture(*args,**kwargs):
            rt = constructor(*args,**kwargs)
            roots.append(rt)
            return rt
        with patch.object(model,'setup',configuration),patch.object(model,'ReferenceCompilerRuntime',capture):
            result = model.worker(MODEL_CASE,'global')
    else:
        configuration = indexed.configuration
        def encoded(*args,**kwargs):
            rt,schema = configuration(*args,evidence_encoding=mode(name),**kwargs)
            roots.append(rt)
            return rt,schema
        parts = name.split('-')
        case = '-'.join(parts[2:])
        if parts[0]=='projected':
            case = 'projected-'+case
        with patch.object(indexed,'configuration',encoded):
            result = indexed.worker(case)
    assert len(roots)==1, 'one real numerical owner and fresh allocator per child'
    return {'status':'EXECUTED_AND_AUDITED','case':name,'process_id':os.getpid(),
        'result':result,'frame_audit':frames(roots[0])}


def matrix(attempt, *, script=None, journal_prefix='FP_PHASE_ENCODING_CUDA',
           cases=None, registration_fn=None, dependencies=None):
    assert attempt>0
    script = Path(__file__).resolve() if script is None else Path(script).resolve()
    cases = CASES if cases is None else cases
    registration_fn = preflight if registration_fn is None else registration_fn
    dependencies = DEPENDENCIES if dependencies is None else dependencies
    output = ROOT/f'evidence/minimal/{journal_prefix}_A{attempt}.json'
    assert not output.exists(), 'all attempted jobs are retained; never overwrite or silently restart'
    source = model.git('rev-parse','HEAD')
    def clean():
        assert model.git('rev-parse','HEAD')==source
        assert not model.git('status','--porcelain','--',*dependencies), 'commit every execution input first'
    clean()
    report = {'status':'REGISTERED_NOT_COMPLETED','execution_source':source,'registration':registration_fn(),'workers':[]}
    def publish():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        temporary.replace(output)
    publish()
    baselines,_ = model.controls()
    baseline = next(row for row in baselines if tuple(row['case'])==MODEL_CASE)
    directory = Path(tempfile.mkdtemp(prefix='fp-phase-encoding-',dir=ROOT)).resolve()
    assert directory.parent==ROOT.resolve()
    stop = False
    for case in cases:
        path = directory/(case+'.json')
        row = {'case':case,'worker_status':'FAILED'}
        print('START '+case,flush=True)
        cap,deadline = (model.CAP,model.DEADLINE) if case.startswith('model-') else (indexed.CAP,900000)
        try:
            clean()
            job = run_in_job(str(script),('--worker',case,'--output',path),
                commit_limit=cap,timeout_ms=deadline)
            row['completed_job'] = asdict(job)
            if path.exists():
                raw = path.read_bytes()
                assert len(raw)<=262144
                row['raw_result_bytes'] = len(raw)
                row['result'] = json.loads(raw)
            report['workers'].append(row)
            publish()  # Completed physical execution is retained before its reader.
            clean()
            if job.timed_out or job.limit_terminated_processes:
                row['worker_status'] = 'RESOURCE_TERMINATED'
            elif job.exit_code==0:
                result = row['result']
                assert job.attached_before_resume and job.peak_job_commit<=cap
                assert result['process_id']==job.process_id and result['case']==case
                assert result['status']=='EXECUTED_AND_AUDITED'
                row['worker_status'] = 'PASS'
                if case.startswith('model-'):
                    row['reader'] = model.read_result(result['result'],MODEL_CASE,'global',baseline)
                    row['worker_status'] = result['result']['status']
            else:
                stop = True
        except Exception:
            if not any(value is row for value in report['workers']):
                report['workers'].append(row)
            row['collection_traceback'] = traceback.format_exc()
            stop = True
        publish()
        print(row['worker_status']+' '+case,flush=True)
        if path.exists():
            assert path.resolve().parent==directory
            path.unlink()
        if stop:
            break
    report['status'] = 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' if stop else 'COMPLETE_WITH_RETAINED_OUTCOMES'
    if not stop:
        try:
            pairs = {}
            by_case = {row['case']:row for row in report['workers']}
            for first,second in ((cases[0],cases[1]),(cases[2],cases[3]),(cases[-2],cases[-1])):
                a,b = by_case[first],by_case[second]
                if a['worker_status'] not in ('PASS','COMPLETE_MODEL','UNRESOLVED_MODEL') or b['worker_status'] not in ('PASS','COMPLETE_MODEL','UNRESOLVED_MODEL'):
                    continue
                x,y = a['result']['result'],b['result']['result']
                if first.startswith('model-'):
                    length = min(len(x['evaluation_readouts']),len(y['evaluation_readouts']))
                    assert x['evaluation_readouts'][:length]==y['evaluation_readouts'][:length]
                    pairs[first] = {'legacy_cursor':x['cursor'],'encoded_cursor':y['cursor'],
                        'identical_common_evaluation_readouts':length,
                        'legacy_refusal':x['refusal'],'encoded_refusal':y['refusal']}
                else:
                    field = 'phases' if first.startswith('generic-') else 'checked_phases'
                    assert x[field]==y[field]
                    pairs[first] = {'both_independently_checked_phases':x[field]}
            report['paired_readers'] = pairs
        except Exception:
            report['paired_reader_traceback'] = traceback.format_exc()
            report['status'] = 'STOPPED_PAIRED_READER_FAILURE'
            stop = True
    publish()
    directory.rmdir()
    print(json.dumps({'status':report['status'],'workers':len(report['workers'])}),flush=True)
    if stop:
        raise SystemExit(1)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
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
            result['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':result['status'],'case':args.worker}),flush=True)
        if result['status']=='FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(),indent=2))
    elif args.attempt is not None:
        matrix(args.attempt)
    else:
        parser.error('select --preflight, --attempt or --worker')
