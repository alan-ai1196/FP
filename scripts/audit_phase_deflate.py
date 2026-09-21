"""Exact byte-only codec and owned-retention audit; CPU owner mocks are explicit."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import json
import random
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime,phase_deflate as codec
from fp_reference.cuda_prefix import IndexedCudaPhase,DEFLATE_PHASE_ENCODING_ID,BINARY_PHASE_ENCODING_ID
from fp_reference.encoding import pack,bounded_packed_size
from fp_reference.resources import ObjectSpec,ResourceExceeded,ResourceLedger
from fp_reference.core import ContractError
from audit_cuda_runtime import cuda_contract,phase_payload
from audit_reference_construction import contract,limits,zero_program,validate_residency,rejects
from audit_reference_events import online
from audit_phase_encoding import phase_fixture,CountState

FAULTS = ('output-count','plan-position','readout','input-mutation','nonbytes','oversized','truncated','trailing')


def encoded(raw):
    encoder = codec.new_encoder()
    return b''.join([encoder.compress(raw[k:k+codec.BLOCK]) for k in range(0,len(raw),codec.BLOCK)]+[encoder.finish()])


def primitive_audit():
    rng = random.Random(621)
    payloads = [b'',bytes(range(256)),b'x'*300000,bytes(range(256))*2049]
    payloads += [rng.randbytes(n) for n in (1,2,31,255,16384,65535,65536,65537,131072)]
    payloads += [pack(v) for v in (None,False,True,0,-1,1<<32767,'\x00\x7f\ud800\U0001f600',
        (),[],{'x':(1,True),'y':[0,None]})]
    checked = 0
    for raw in payloads:
        code = encoded(raw)
        chunks = tuple(codec.decoded_fragments(code,expanded_cap=max(1,len(raw))))
        assert all(type(p) is bytes and 0<len(p)<=codec.BLOCK for p in chunks)
        assert b''.join(chunks)==raw and zlib.decompress(code)==raw
        checked += len(raw)
    encoder = codec.new_encoder()
    for wrong in (bytearray(b'x'),memoryview(b'x'),'x',(),b'',b'x'*(codec.BLOCK+1)):
        rejects(lambda:encoder.compress(wrong))
    encoder.compress(b'x')
    encoder.finish()
    rejects(encoder.finish)
    rejects(lambda:encoder.compress(b'x'))
    raw = pack(('complete','phase',tuple(range(32))))
    code = encoded(raw)
    faults = refused = equivalent = different = 0
    for k in range(len(code)):
        for bit in range(8):
            changed = bytearray(code)
            changed[k] ^= 1<<bit
            try:
                output = b''.join(codec.decoded_fragments(changed,expanded_cap=len(raw)))
            except (ContractError,ResourceExceeded):
                refused += 1
            else:
                # Deflate has noncanonical representations and unused padding
                # bits. Equality is the obligation, not rejecting every bit.
                if output==raw:
                    equivalent += 1
                else:
                    different += 1
            faults += 1
    assert refused+equivalent+different==faults
    for end in range(len(code)):
        rejects(lambda end=end:b''.join(codec.decoded_fragments(code[:end])),ContractError)
    for suffix in (b'x',code):
        rejects(lambda:b''.join(codec.decoded_fragments(code+suffix)),ContractError)
    rejects(lambda:b''.join(codec.decoded_fragments(encoded(b'x'*1000000),expanded_cap=1024)),ResourceExceeded)
    import fp_reference.encoding as canonical
    with patch.object(canonical,'packed_size',side_effect=AssertionError('unfunded expanded traversal')):
        rejects(lambda:bounded_packed_size(('x'*1024,)*1024,byte_limit=65536),ResourceExceeded)
    rejects(lambda:cuda_contract(evidence_encoding=BINARY_PHASE_ENCODING_ID))
    return {'round_trips':len(payloads),'full_bytes_checked':checked,'single_bit_variants_checked':faults,
        'bit_variants_refused_by_decoder':refused,'bit_variants_with_identical_expansion':equivalent,
        'bit_variants_requiring_owner_content_refusal':different,
        'all_truncations_refused':len(code),'trailing_or_second_stream_refusals':2,
        'immutable_chunk_and_lifecycle_refusals':8,'expansion_bomb_refused':True,
        'aggregate_input_guard_precedes_size_traversal':True,'old_mutable_record_codec_registration_refused':True}


class FaultEncoder:
    """Audit-only substitute, acting solely on the byte chunks it receives."""
    def __init__(self,case,cap,seen,stage='predict'):
        self.case,self.cap,self.seen,self.parts,self.stage = case,cap,seen,[],stage

    def compress(self,part):
        assert type(part) is bytes and 0<len(part)<=codec.BLOCK
        assert not hasattr(part,'execution_plan') and not hasattr(part,'__dict__')
        self.parts.append(part)
        assert sum(map(len,self.parts))<=1<<20, 'bounded small adversary fixture'
        return b''

    def finish(self):
        raw = b''.join(self.parts)
        tree = json.loads(raw.decode('utf-8','surrogatepass'))
        if tree[0]!='dataclass' or tree[2]!='IndexedCudaPhase' or not dict(tree[3])['phase'][1].endswith(':'+self.stage):
            return zlib.compress(raw,6)
        self.seen.append(self.case)
        fields = dict(tree[3])
        if self.case=='input-mutation':
            self.parts[0].output_cells = 57
        elif self.case=='output-count':
            fields['output_cells'][1] = format(int(fields['output_cells'][1],16)-1,'x')
        elif self.case=='plan-position':
            positions = dict(fields['execution_plan'][3])['positions'][1]
            assert positions==[['integer_hex','2']]
            positions[0][1] = '0'
        elif self.case=='readout':
            words = dict(fields['raw_prediction'][3])['words'][1]
            words[5][1] = format(int(words[5][1],16)^1,'x')
        elif self.case=='gradient':
            words = dict(fields['raw_state'][3])['gradient_words'][1]
            words[0][1] = format(int(words[0][1],16)^1,'x')
        new = json.dumps(tree,ensure_ascii=False,separators=(',',':')).encode('utf-8','surrogatepass')
        result = zlib.compress(new,6)
        if self.case=='nonbytes':
            return bytearray(result)
        if self.case=='oversized':
            return b'!'*(self.cap+1)
        if self.case=='truncated':
            return result[:-1]
        if self.case=='trailing':
            return result+b'x'
        return result


def fixture(template, *, frame_bytes=4096,work_cap=10**12,byte_cap=32<<20):
    cfg = replace(contract(),limits=limits(byte_cap=byte_cap,work_cap=work_cap))
    root = ReferenceCompilerRuntime(cfg,zero_program(2),online=online(cfg,2))
    cuda = cuda_contract(evidence_encoding=DEFLATE_PHASE_ENCODING_ID,phase_evidence_bytes=frame_bytes)
    calls,accepted,phases = [],[],{}
    def execute(label,kind,program,candidate,reference,**kwargs):
        calls.append(kind)
        phase = replace(template,object_id=label,candidate_id=candidate,program_id=program.program_id)
        phases[label] = phase
        return phase,None
    root._cuda = SimpleNamespace(contract=cuda,phases=phases,relation_work=lambda *a:0,
        forward_work=lambda *a:0,execute=execute,accept=lambda phase:accepted.append(phase.object_id),snapshot=lambda:None)
    for suffix,size in (('cuda-raw-readout',1),('cuda-phase-byte-staging',codec.BLOCK)):
        key = root._runtime_id+':'+suffix
        root._ledger.allocate(root._data_owner,(ObjectSpec(key,'mocked_bound_workspace',
            {'reference_payload_bytes':size,'physical_objects':1},root._chi),))
        root._buffers[key] = bytearray(size)
    return root,calls,accepted


def retain(root):
    root._cuda_execute('predict',root._programs[next(iter(root._programs))],root._deployed_id,None,
        origin='construction',observation_id=None,sources=None,reference_prediction=None,target=None)


def retention_audit():
    template,_ = phase_fixture(3,CountState(3,(0,0,1),None,1,1),(0,1),(0,1))
    original = pack(template)
    root,calls,accepted = fixture(template)
    retain(root)
    first = validate_residency(root)
    record = next(iter(root._cuda.phases.values()))
    frame = dict(first.buffers)[record.object_id]
    size = int.from_bytes(frame[:8],'big')
    assert b''.join(codec.decoded_fragments(frame[8:8+size]))==pack(record)
    assert type(root._buffers[record.object_id]) is bytes and not any(frame[8+size:])
    retain(root)
    assert len(accepted)==2 and dict(root.snapshot().buffers)[record.object_id] is frame
    validate_residency(root)
    # Exercise the actual paid staging loop across several boundaries,
    # including cuts inside surrogatepass UTF-8. No large encoded body is
    # used inside Runtime; materialization here is only the independent audit.
    large = replace(template,reason=('x\ud800\U0001f600'*40000))
    big,_,_ = fixture(large)
    original_factory = codec.new_encoder
    sizes = []
    class SeenEncoder:
        def __init__(self):
            self.encoder = original_factory()
        def compress(self,part):
            assert type(part) is bytes
            sizes.append(len(part))
            return self.encoder.compress(part)
        def finish(self):
            return self.encoder.finish()
    with patch.object(codec,'new_encoder',SeenEncoder):
        retain(big)
    big_snapshot = validate_residency(big)
    big_record = next(iter(big._cuda.phases.values()))
    big_frame = dict(big_snapshot.buffers)[big_record.object_id]
    big_size = int.from_bytes(big_frame[:8],'big')
    assert max(sizes)==codec.BLOCK and len(sizes)>3
    assert b''.join(codec.decoded_fragments(big_frame[8:8+big_size]))==pack(big_record)
    failures = []
    for case in FAULTS:
        broken,calls,accepted = fixture(template)
        seen = []
        with patch.object(codec,'new_encoder',lambda:FaultEncoder(case,4096,seen)):
            rejects(lambda:retain(broken),(RuntimeError,ResourceExceeded,AttributeError))
        snapshot = validate_residency(broken)
        phase = next(iter(broken._cuda.phases.values()))
        assert calls==['predict'] and seen==[case] and not accepted
        assert phase.status==('UNRESOLVED' if case=='oversized' else 'EXECUTION_FAILED')
        assert phase.output_cells==template.output_cells and phase.execution_plan==template.execution_plan
        assert phase.raw_prediction==template.raw_prediction and pack(template)==original
        assert type(broken._buffers[phase.object_id]) is bytearray
        failures.append({'case':case,'status':phase.status,'original_record_and_plan_unchanged':True})
    resource_refusals = []
    for size in range(1,9):
        limited,calls,accepted = fixture(template,frame_bytes=size)
        with patch.object(codec,'new_encoder',side_effect=AssertionError('unfunded encoder')):
            rejects(lambda:retain(limited),ResourceExceeded)
        assert not calls and not accepted
        validate_residency(limited)
        resource_refusals.append('frame-'+str(size))
    limited,calls,accepted = fixture(template,frame_bytes=256)
    rejects(lambda:retain(limited),ResourceExceeded)
    assert calls==['predict'] and not accepted
    validate_residency(limited)
    resource_refusals.append('final-frame')
    limited,calls,accepted = fixture(template,work_cap=10**8)
    before = dict(limited.snapshot().buffers)
    with patch.object(codec,'new_encoder',side_effect=AssertionError('unpaid encoder')):
        rejects(lambda:retain(limited),ResourceExceeded)
    assert not calls and not accepted and dict(validate_residency(limited).buffers)==before
    resource_refusals.append('prepaid-work')
    return {'scope':'real Runtime retention with explicitly mocked numerical owner; no CUDA authority',
        'successful_frames':2,'older_immutable_frame_preserved':True,'paid_reusable_staging_bytes':codec.BLOCK,
        'additional_multiblock_UTF8_frame_bytes':len(pack(big_record)),
        'multiblock_immutable_encoder_input_lengths':sizes,
        'faults':failures,'resource_refusals':resource_refusals}


def audit():
    import fp_reference.runtime as execution
    cfg = replace(contract(),limits=limits(byte_cap=60000,work_cap=10**12))
    cuda = cuda_contract(evidence_encoding=DEFLATE_PHASE_ENCODING_ID,phase_output_cells=2)
    seen = []
    allocate = ResourceLedger.allocate
    def observed_allocate(self,owner,objects):
        values = tuple(objects)
        seen.extend(v.kind for v in values)
        return allocate(self,owner,values)
    with patch.object(execution,'_CudaPrefix',side_effect=AssertionError('unfunded CUDA binding')), \
            patch.object(ResourceLedger,'allocate',observed_allocate):
        rejects(lambda:ReferenceCompilerRuntime(cfg,zero_program(2),online=online(cfg,2),cuda=cuda),ResourceExceeded)
    assert seen[-1]=='cuda_phase_byte_staging'
    result = {'status':'PASS_BYTE_ONLY_PHASE_CPU','encoding':codec.ENCODING_ID,
        'primitive':primitive_audit(),'retention':retention_audit(),
        'staging_refused_before_CUDA_binding':True,'staging_admission_allocation_kinds':seen}
    assert 'torch' not in sys.modules
    return result


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'evidence/minimal/FP_PHASE_DEFLATE_CPU.json')
    args = parser.parse_args()
    result = audit()
    if args.output.exists():
        assert json.loads(args.output.read_text())==json.loads(json.dumps(result))
    else:
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
