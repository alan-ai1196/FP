"""Owned actual device identity, full-board VRAM upper and native failures.

These are device correctness/resource audits, not model-science results.
Every allocating case starts a fresh process. No caller sample enters Runtime.
"""
import argparse
import ctypes as C
from dataclasses import asdict, replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.cuda_device import CudaDeviceContract
from fp_reference.cuda_storage import CudaStorageUnresolved
from fp_reference.host_failure import CUDA_RESOURCE_FAILURE
from fp_reference.host_resources import HostResourceContract
from audit_cuda_runtime import configuration, cuda_contract, no_device_handles, audit_snapshot
from audit_reference_events import online
from audit_reference_construction import zero_program, rejects
from audit_reference_persistence import event
from audit_cuda_installation import fixture, install, ownership
from windows_job_audit_support import run_in_job


BOARD = 24 << 30


def root(device=None):
    cfg = configuration()
    return ReferenceCompilerRuntime(cfg, zero_program(2), online=online(cfg, 4),
        cuda=cuda_contract(**({} if device is None else {'device': device})))


def admission(case):
    import torch
    contract = cuda_contract().device
    if case == 'runtime':
        contract = replace(contract, runtime_version=13020)
    elif case == 'driver-api':
        contract = replace(contract, driver_api_version=13030)
    elif case == 'driver':
        contract = replace(contract, driver_version='616.91')
    elif case == 'capacity':
        contract = replace(contract, vram_cap=BOARD-1)
    else:
        assert case == 'role'
        contract = replace(contract, vram_cap=BOARD+2,
            role_vram_caps={'deployment': BOARD+1, 'compiler': BOARD-1})
    rejects(lambda: root(contract), CudaStorageUnresolved)
    assert torch.cuda.memory_allocated() == torch.cuda.memory_reserved() == 0
    stats = torch.cuda.memory_stats()
    assert all(stats[key] == 0 for key in ('allocation.all.allocated', 'allocated_bytes.all.allocated', 'segment.all.allocated'))
    return {'rejected_before_first_native_tensor_allocation': True, 'case': case}


def binding():
    caps = CudaDeviceContract(BOARD+2, {'deployment': BOARD+1, 'compiler': BOARD})
    rt = root(caps)
    initial = rt.snapshot()
    device = initial.cuda.device
    assert device.physical_vram_upper == device.identity.physical_vram_bytes == BOARD
    assert dict(device.role_physical_vram_upper) == {'deployment': BOARD, 'compiler': BOARD}
    assert (device.identity.runtime_version, device.identity.driver_api_version, device.identity.driver_version) == (13040, 13040, '616.92')
    assert initial.cuda.contract.execution_identity[2] == '13.2'
    no_device_handles(initial)
    event(rt, 0)
    event(rt, 1)
    assert rt.snapshot().cuda.device == device
    return {'actual_identity': asdict(device.identity), 'unequal_caps_keep_both_full_board_charges': True,
            'independent_CUDA_phases': audit_snapshot(rt)['phases']}


def foreign():
    rt = root()
    import torch
    before = rt.snapshot()
    lib = C.CDLL(str(Path(torch.__file__).parent/'lib/cudart64_13.dll'))
    signatures = {'cudaMalloc': [C.POINTER(C.c_void_p), C.c_size_t],
        'cudaMemset': [C.c_void_p, C.c_int, C.c_size_t], 'cudaFree': [C.c_void_p], 'cudaDeviceSynchronize': []}
    for key, types in signatures.items():
        getattr(lib, key).argtypes, getattr(lib, key).restype = types, C.c_int
    pointer, size = C.c_void_p(), 32 << 20
    assert lib.cudaMalloc(C.byref(pointer), size) == 0
    try:
        assert lib.cudaMemset(pointer, 0, size) == lib.cudaDeviceSynchronize() == 0
        during = rt.snapshot()
        assert during.cuda.storage == before.cuda.storage and during.cuda.device == before.cuda.device
        # This foreign call is outside FP's API. The proved board upper
        # covers both histories without assuming that the call did not occur.
        event(rt, 0)
    finally:
        assert lib.cudaFree(pointer) == 0
    after = rt.snapshot()
    assert after.halted is None and after.cuda.device.physical_vram_upper == BOARD
    assert after.cuda.storage['native_allocation_counter_current'] == (1, 16 << 20, 1)
    return {'foreign_CUDA_bytes': size, 'native_observations_unchanged_while_live': True,
            'whole_board_upper_covers_foreign_allocation_without_claiming_its_exact_residency': True}


def failure(case):
    rt, selected, ids = fixture()
    before = rt.snapshot()
    functions = rt._cuda._device._functions
    exception = RuntimeError('injected original native observer failure')
    diagnostic = case.startswith('snapshot-')
    kind = case.removeprefix('snapshot-')
    action = rt.snapshot if diagnostic else lambda: rt.cuda_persistence_result(ids[1])
    if kind == 'query-failure':
        callback = lambda *args: 999
    elif kind == 'changed':
        def callback(output):
            C.cast(output, C.POINTER(C.c_int))[0] = 13020
            return 0
    else:
        def callback(*args):
            raise exception
    key = 'cudaRuntimeGetVersion' if kind == 'changed' else 'nvmlDeviceGetMemoryInfo'
    mutations = {key: callback}
    if kind == 'combined':
        mutations['nvmlShutdown'] = lambda: 999
    with patch.dict(functions, mutations):
        if kind in ('unexpected', 'combined'):
            try:
                action()
            except RuntimeError as exc:
                assert exc is exception
            else:
                raise AssertionError('original native exception was lost')
        else:
            rejects(action, CudaStorageUnresolved)
    after = rt.snapshot()
    assert after.halted is CUDA_RESOURCE_FAILURE and after.event_phase == 'halted'
    assert after.candidates == before.candidates and after.alpha_spent == before.alpha_spent
    assert after.persistence_identities == before.persistence_identities
    rejects(lambda: rt.paired_cuda_persistence_result(*ids))
    rejects(lambda: install(rt, selected, ids))
    return {'restored_native_API_cannot_revive_old_crossings_or_install': True,
            'original_unexpected_exception_preserved': kind in ('unexpected', 'combined'), 'case': case}


def hosted(output):
    cap = 4 << 30
    rt, selected, ids = fixture(host=HostResourceContract(cap,
        {'deployment': cap, 'compiler': cap}))
    assert install(rt, selected, ids).status == 'INSTALLED_CUDA'
    event(rt, 0)
    event(rt, 1)
    state = ownership(rt)
    observed = state.host_resources
    assert observed.lifetime_process_commit_peak <= cap
    assert state.cuda.device.physical_vram_upper == BOARD
    report = {'same_registered_host_process_and_device_after_install': True,
        'host_process_id': observed.process_id, 'host_creation_100ns': observed.creation_100ns,
        'host_lifetime_commit_peak': observed.lifetime_process_commit_peak,
        'board_VRAM_upper': BOARD, 'native_arena_bytes': state.cuda.storage['actual_tensor_arena_bytes'],
        'independent_CUDA_phases': audit_snapshot(rt)['phases']}
    Path(output).write_text(json.dumps(report), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case')
    parser.add_argument('--worker-output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker_output:
        hosted(args.worker_output)
        return
    if args.case:
        assert not args.write
        if args.case in ('runtime', 'driver-api', 'driver', 'capacity', 'role'):
            result = admission(args.case)
        elif args.case == 'binding':
            result = binding()
        elif args.case == 'foreign':
            result = foreign()
        else:
            result = failure(args.case)
        print(json.dumps(result))
        return
    report = {'status': 'PASS', 'scope': 'actual device binding and conservative whole-board VRAM envelope; process commitment separate; no exact total allocation history or complete target release'}
    for case in ('runtime', 'driver-api', 'driver', 'capacity', 'role', 'binding', 'foreign',
                 'query-failure', 'changed', 'unexpected', 'combined',
                 'snapshot-query-failure', 'snapshot-unexpected', 'snapshot-combined'):
        process = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--case', case],
                                 capture_output=True, text=True, timeout=90)
        assert process.returncode == 0, process.stdout+process.stderr
        report[case] = json.loads(process.stdout)
        print(case+' PASS', flush=True)
    with tempfile.TemporaryDirectory(prefix='fp-cuda-device-', dir=ROOT) as temporary:
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--worker-output', output), commit_limit=4 << 30, timeout_ms=90000)
        assert job.exit_code == 0 and not job.timed_out, job
        raw = output.read_bytes()
        assert len(raw) < 4096
        result = json.loads(raw)
        assert (result['host_process_id'], result['host_creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert result['host_lifetime_commit_peak'] <= job.peak_process_commit <= 4 << 30
        report['hosted-install'] = {'worker': result, 'completed_job': asdict(job)}
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_DEVICE_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
