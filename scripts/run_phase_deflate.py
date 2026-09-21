"""Fresh actual CUDA protocol for the byte-only phase evidence boundary.

Only the registered raw-byte compressor is faulted. Phase objects, owner
globals and the trusted canonical serializer/decoder are never altered.
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
from fp_reference import phase_deflate as codec
from fp_reference.cuda_prefix import LEGACY_PHASE_ENCODING_ID
from audit_phase_deflate import FaultEncoder,FAULTS
from audit_reference_construction import validate_residency,rejects
from ingress_audit_support import deliver_context
import audit_indexed_amp as indexed
import run_phase_encoding as base

CASES = ('generic-legacy-profile','generic-deflate-profile',
    'indexed-legacy-profiles','indexed-deflate-profiles','projected-deflate-profiles',
    'indexed-deflate-large','projected-deflate-install','indexed-deflate-endpoint-binding',
    'indexed-deflate-plan-binding','projected-deflate-foreign-plan','byte-input-interface',
    *(f'fault-predict-{case}' for case in FAULTS),
    'fault-observe-output-count','fault-observe-gradient',
    'model-global-legacy','model-global-deflate')
DEPENDENCIES = base.DEPENDENCIES+('theory/proofs/BYTE_ONLY_PHASE_EVIDENCE.md',)


def encoding(name):
    return LEGACY_PHASE_ENCODING_ID if 'legacy' in name else codec.ENCODING_ID


def preflight():
    from dataclasses import replace
    baseline,_ = base.model.controls()
    assert any(tuple(row['case'])==base.MODEL_CASE for row in baseline)
    old = base.model.setup(base.MODEL_CASE,'global')[3]
    new = replace(old,evidence_encoding=codec.ENCODING_ID)
    assert {k for k in vars(old) if getattr(old,k)!=getattr(new,k)}=={'evidence_encoding','work_model'}
    assert old.backend_id==new.backend_id and old.forward_id==new.forward_id
    assert 'torch' not in sys.modules
    return {'status':'REGISTERED_BEFORE_BYTE_ONLY_CUDA_EXECUTION','cases':CASES,
        'encoding':codec.ENCODING_ID,'compression_library':codec.LIBRARY,
        'encoder_inputs':'only immutable bytes of at most65536; no native record, iterator, frame or owner',
        'paid_reusable_staging_bytes':codec.BLOCK,'expanded_cap':codec.EXPANDED_CAP,
        'extra_work_per_phase':'32*134217728 + 16*frame_bytes; registered primitive tariff, not a bit-time/heap bound',
        'trusted_boundary':['Runtime owner','canonical serialization','independent zlib format reader and owner byte comparison'],
        'certificate_class':'entire canonical execution record recovered from retained bytes; no unique compressed-bit-pattern claim',
        'fault_scope':'provided byte arguments and returned data only; no arbitrary Python stack/global-memory attack',
        'fixture_job_cap':indexed.CAP,'fixture_deadline_ms':900000,
        'generic_work_cap_for_both_encodings':10**14,'model_case':base.MODEL_CASE,
        'model_job_cap':base.model.CAP,'model_deadline_ms':base.model.DEADLINE,
        'model_packed_cap':base.model.PACKED,'model_frame_bytes':base.model.FRAME,
        'model_output_cells':base.model.CELLS,'model_work_per_role':base.model.WORK,
        'matched_differences':['codec/work identity','paid65536-byte staging on the compressed path'],
        'unchanged':['native learner','data and targets','reference/AMP schedule','numerical tolerances',
            'uniform frames and padding','join/live/tape/output caps'],
        'old_writer_alias_witnesses':'retained at ba48cb3; retired record-taking codec cannot be registered',
        'not_claimed':['all n16 completion','new full release','isolated runtime/memory dominance','model superiority']}


def local_worker(case):
    rt,schema = indexed.configuration(3,2,evidence_encoding=codec.ENCODING_ID)
    if case=='byte-input-interface':
        sizes = []
        original = codec.new_encoder
        class Seen:
            def __init__(self):
                self.encoder = original()
            def compress(self,data):
                assert type(data) is bytes and 0<len(data)<=codec.BLOCK
                assert not hasattr(data,'__dict__') and not hasattr(data,'execution_plan')
                sizes.append(len(data))
                return self.encoder.compress(data)
            def finish(self):
                return self.encoder.finish()
        with patch.object(codec,'new_encoder',Seen):
            indexed.step(rt,schema,(1,2,0))
            indexed.step(rt,schema,(0,1,0))
        result = {**indexed.check_phases(rt),'checked_immutable_chunks':len(sizes),
            'largest_chunk':max(sizes),'no_record_or_frame_supplied_to_encoder':True}
    else:
        _,stage,attack = case.split('-',2)
        if attack=='plan-position':
            indexed.step(rt,schema,(1,2,0))
        before = rt.snapshot()
        key = before.online.data.active.observation_ids[before.cursor]
        context = tuple(schema.source_row(1).values())
        if stage=='observe':
            assert deliver_context(rt,key,context).status=='PREDICTED_REFERENCE'
            before = rt.snapshot()
        seen = []
        with patch.object(codec,'new_encoder',lambda:FaultEncoder(attack,262144,seen,stage)):
            if attack=='oversized':
                event = deliver_context(rt,key,context)
                assert event.status=='UNRESOLVED'
            else:
                rejects(lambda:rt.observe(0) if stage=='observe' else deliver_context(rt,key,context),
                    (RuntimeError,AttributeError))
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert seen==[attack]
        assert phase.status==('UNRESOLVED' if attack=='oversized' else 'EXECUTION_FAILED')
        assert after.cursor==before.cursor and after.candidates==before.candidates and after.cuda.current==before.cuda.current
        assert after.pending.record.target==(0 if stage=='observe' else None)
        assert stage=='observe' or not after.pending.predictions
        assert type(rt._buffers[phase.object_id]) is bytearray
        # The attack can change its byte copy only. The original actual record
        # still satisfies the fixed numerical schedule and complete plan.
        from fp_reference import indexed_amp as amp
        if stage=='predict':
            raw = phase.raw_prediction
            amp.check_prediction_plan(phase.execution_plan,schema,amp.IndexedAmpState(raw.before),
                schema.rules(),schema.source_row(1),output_cap=65536)
            amp.check_prediction_execution(phase.execution_plan,amp.IndexedAmpState(raw.before),
                raw,phase.raw_operations,bit_limit=32768)
            assert phase.output_cells==phase.execution_plan.output_cells
        else:
            prior = {p.object_id:p for p in before.cuda.phases}
            amp.check_observation_execution(prior[phase.input_phase].raw_state,
                prior[phase.prediction_phase].raw_prediction,0,phase.raw_state,phase.raw_operations,bit_limit=32768)
        result = {'status':'PASS_BYTE_ONLY_FAULT_REFUSAL','stage':stage,'attack':attack,
            'phase_status':phase.status,'original_executed_record_still_valid':True,
            'actual_output_cells':phase.output_cells,'published_learner_advances':0,
            'received_target':after.pending.record.target,'retained_failed_frame_bytes':len(rt._buffers[phase.object_id])}
    return {'status':'EXECUTED_AND_AUDITED','case':case,'process_id':os.getpid(),
        'result':result,'frame_audit':base.frames(rt)}


def worker(case):
    if case=='byte-input-interface' or case.startswith('fault-'):
        return local_worker(case)
    # Reuse all existing substantive numerical/lineage/fresh/install readers.
    # The harness changes only the explicitly registered codec/work identity.
    with patch.object(base,'mode',encoding):
        return base.worker(case)


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
            result['traceback']=traceback.format_exc()
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        if result['status']=='FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(),indent=2))
    elif args.attempt is not None:
        base.matrix(args.attempt,script=__file__,journal_prefix='FP_PHASE_DEFLATE_CUDA',
            cases=CASES,registration_fn=preflight,dependencies=DEPENDENCIES)
    else:
        parser.error('select --preflight, --attempt or --worker')
