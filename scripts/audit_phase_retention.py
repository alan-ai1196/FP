"""CPU tests of the real retention hook with a mocked numerical owner.

No CUDA execution, bridge, complete learner or installation is certified by
these fixtures. Actual owned integration has a separate registered runner.
"""
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import phase_encoding as codec
from fp_reference import ReferenceCompilerRuntime
from fp_reference.encoding import pack
from fp_reference.resources import ObjectSpec,ResourceExceeded
from fp_reference.core import ContractError
from fp_reference.cuda_prefix import BINARY_PHASE_ENCODING_ID,IndexedCudaPhase
from audit_cuda_runtime import cuda_contract
from audit_reference_construction import validate_residency,contract,limits,zero_program
from audit_reference_events import online
from audit_phase_encoding import phase_fixture,refuses,CountState


def retention_fixture(template, *, frame_bytes=4096, work_cap=10**12):
    native = replace(contract(),limits=limits(byte_cap=32<<20,work_cap=work_cap))
    root = ReferenceCompilerRuntime(native,zero_program(2),online=online(native,2))
    cfg = cuda_contract(evidence_encoding=BINARY_PHASE_ENCODING_ID,phase_evidence_bytes=frame_bytes)
    phases,calls,accepted = {},[],[]
    def execute(label,kind,program,candidate,reference,**kwargs):
        calls.append(kind)
        phase = replace(template,object_id=label,candidate_id=candidate,program_id=program.program_id)
        phases[label] = phase
        return phase,None
    # Explicitly mocked numerical owner: only the actual paid writer/sealer
    # and their resource/failure transitions are under test here.
    root._cuda = SimpleNamespace(contract=cfg,phases=phases,relation_work=lambda *a:0,
        forward_work=lambda *a:0,execute=execute,snapshot=lambda:None,
        accept=lambda record:accepted.append(record.object_id),accepted=accepted)
    key = root._runtime_id+':cuda-raw-readout'
    root._ledger.allocate(root._data_owner,(ObjectSpec(key,'mocked_readout',
        {'reference_payload_bytes':1,'physical_objects':1},root._chi),))
    root._buffers[key] = bytearray(1)
    return root,calls


def retain(root):
    root._cuda_execute('predict',root._programs[next(iter(root._programs))],root._deployed_id,None,
        origin='construction',observation_id=None,sources=None,reference_prediction=None,target=None)


def audit():
    template,_ = phase_fixture(3,CountState(3,(1,-1,2),None,4,4),(1,2),(0,1))
    root,calls = retention_fixture(template)
    retain(root)
    snapshot = validate_residency(root)
    phase = next(iter(root._cuda.phases.values()))
    frame = dict(snapshot.buffers)[phase.object_id]
    size = int.from_bytes(frame[:8],'big')
    assert calls==['predict'] and type(root._buffers[phase.object_id]) is bytes
    assert b''.join(codec.decoded_fragments(frame[8:8+size]))==pack(phase)
    assert not any(frame[8+size:]) and len(frame)==4096
    old = root.snapshot()
    retain(root)
    # The mock execute label normally depends on the retained phase count.
    assert dict(root.snapshot().buffers)[phase.object_id] is dict(old.buffers)[phase.object_id]
    validate_residency(root)
    assert len(root._cuda.accepted)==2

    resources = []
    for size in range(1,9):
        limited,calls = retention_fixture(template,frame_bytes=size)
        refuses(lambda:retain(limited),ResourceExceeded)
        assert not calls
        validate_residency(limited)
        resources.append('frame-'+str(size))
    limited,calls = retention_fixture(template,frame_bytes=512)
    refuses(lambda:retain(limited),ResourceExceeded)
    assert calls==['predict']
    failed = next(iter(limited._cuda.phases.values()))
    assert failed.status=='UNRESOLVED'
    frame = dict(validate_residency(limited).buffers)[failed.object_id]
    size = int.from_bytes(frame[:8],'big')
    assert b''.join(codec.decoded_fragments(frame[8:8+size]))==pack((failed.object_id,'ADMITTED_CUDA_PHASE'))
    resources.append('final-frame')
    limited,calls = retention_fixture(template,work_cap=10**8)
    before = dict(limited.snapshot().buffers)
    with patch.object(codec,'extent',side_effect=AssertionError('unpaid encoding')):
        refuses(lambda:retain(limited),ResourceExceeded)
    assert not calls and dict(validate_residency(limited).buffers)==before
    resources.append('prepaid-work')

    faults = []
    original = codec.write
    for attack in ('payload','header','padding','extent','extent-type','resize'):
        broken,calls = retention_fixture(template)
        def write(value,output,*,start=0,expanded_cap=codec.EXPANDED_CAP):
            measured = original(value,output,start=start,expanded_cap=expanded_cap)
            if type(value) is not IndexedCudaPhase:
                return measured
            if attack=='payload':
                output[start+measured.encoded_bytes-1] ^= 1
            elif attack=='header':
                output[0] ^= 1
            elif attack=='padding':
                output[-1] ^= 1
            elif attack=='extent':
                return replace(measured,encoded_bytes=measured.encoded_bytes+1)
            elif attack=='extent-type':
                class Integer(int):
                    pass
                return replace(measured,encoded_bytes=Integer(measured.encoded_bytes))
            else:
                output.obj.append(0)
            return measured
        with patch.object(codec,'write',write):
            refuses(lambda:retain(broken),(RuntimeError,BufferError))
        assert calls==['predict']
        failed = next(iter(broken._cuda.phases.values()))
        assert failed.status=='EXECUTION_FAILED'
        assert not broken._cuda.accepted
        assert type(broken._buffers[failed.object_id]) is bytearray
        assert len(broken._buffers[failed.object_id])==4096
        validate_residency(broken)
        faults.append(attack)
    assert 'torch' not in sys.modules
    return {'status':'PASS_OWNED_PHASE_RETENTION_HOOK_CPU',
        'scope':'real Runtime retention hook with explicitly mocked numerical owner; no actual CUDA authority',
        'successful_complete_frames':2,'resource_refusals':resources,'writer_fault_refusals':faults,
        'old_immutable_snapshot_preserved':True,'all_actual_buffers_remain_owned':True}


if __name__=='__main__':
    report = audit()
    path = ROOT/'evidence/minimal/FP_PHASE_RETENTION_CPU.json'
    if path.exists():
        assert json.loads(path.read_text())==report
    else:
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)
