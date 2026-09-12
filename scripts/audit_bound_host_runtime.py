"""Live host registration through Runtime, with independently observed jobs."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import ctypes as C
from ctypes import wintypes as W
import json
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE, HOST_RESOURCE_FAILURE
from fp_reference.host_resources import HostResourceContract, HostExecutionUnresolved, _WindowsProcessHost, ExtendedLimit, ProcessMemory
from fp_reference.ingress import IngressContract
from audit_reference_construction import contract, limits, rejects, validate_residency, zero_program
from audit_reference_events import online
from audit_cpu_installation import fixture, install
from audit_reference_persistence import event
from windows_job_audit_support import run_in_job


CAP = 1 << 26


def registration():
    # Three distinct registered caps. The physical fence is their minimum,
    # not a role the caller can choose after a result or a failure.
    return HostResourceContract(CAP*2, {'deployment': CAP+CAP//2, 'compiler': CAP})


def observation(rt):
    snapshot = rt.snapshot()
    host = snapshot.host_resources
    assert host.contract == registration() and host.contract.enforced_cap == CAP
    assert 0 < host.process_commit <= host.lifetime_process_commit_peak <= CAP
    assert 0 < host.job_commit_peak <= CAP
    assert host.role_current == {'deployment': host.process_commit, 'compiler': host.process_commit}
    assert host.role_peak == {'deployment': host.lifetime_process_commit_peak, 'compiler': host.lifetime_process_commit_peak}
    assert all(value == {'user_100ns': host.process_user_100ns, 'kernel_100ns': host.process_kernel_100ns}
               for value in host.role_cpu.values())
    return host


def numeric_record(host):
    return {name: getattr(host, name) for name in (
        'process_id', 'creation_100ns', 'process_commit', 'lifetime_process_commit_peak', 'job_commit_peak',
        'process_user_100ns', 'process_kernel_100ns', 'job_user_100ns', 'job_kernel_100ns', 'total_job_processes')}


def worker(mode):
    cfg = contract()
    host = registration()
    if mode == 'late-fence':
        # The outer job permits this real, transient 80 MiB allocation. After
        # freeing it, install a stricter nested fence in the same process.
        transient = bytearray(CAP+CAP//4)
        del transient
        kernel = C.WinDLL('kernel32', use_last_error=True)
        def bind(name, result, arguments):
            fn = getattr(kernel, name)
            fn.restype, fn.argtypes = result, arguments
            return fn
        create = bind('CreateJobObjectW', W.HANDLE, [C.c_void_p, W.LPCWSTR])
        set_limits = bind('SetInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD])
        current = bind('GetCurrentProcess', W.HANDLE, [])
        assign = bind('AssignProcessToJobObject', W.BOOL, [W.HANDLE, W.HANDLE])
        memory_info = bind('K32GetProcessMemoryInfo', W.BOOL, [W.HANDLE, C.c_void_p, W.DWORD])
        query = bind('QueryInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p])
        job, declared = create(None, None), ExtendedLimit()
        assert job
        declared.basic.flags, declared.basic.processes = 0x2308, 1
        declared.process_memory = declared.job_memory = CAP
        assert set_limits(job, 9, C.byref(declared), C.sizeof(declared))
        assert assign(job, current())
        # Keep this job handle until process exit: closing a kill-on-close
        # job while inside it would kill the worker before reporting the test.
        memory, live = ProcessMemory(), ExtendedLimit()
        memory.size = C.sizeof(memory)
        assert memory_info(current(), C.byref(memory), C.sizeof(memory))
        assert query(None, 9, C.byref(live), C.sizeof(live), None)
        assert memory.private < CAP < memory.peak_pagefile
        assert live.process_memory == live.job_memory == CAP
        assert max(live.peak_process, live.peak_job) < CAP
        rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), host=host), HostExecutionUnresolved)
        return {'current_process_commit': memory.private, 'lifetime_process_commit_peak': memory.peak_pagefile,
                'new_job_process_peak': live.peak_process, 'new_job_peak': live.peak_job,
                'late_fence_cap': CAP, 'low_current_memory_cannot_erase_prior_peak': True}
    if mode == 'memory':
        cfg = replace(cfg, limits=limits(byte_cap=1 << 30, work_cap=1 << 34))
        run = online(cfg, 2, unit=1)
        run = replace(run, data=replace(run.data, ingress=IngressContract(capacity=1 << 27, chunk_bytes=64)))
        rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run, host=host)
        before = observation(rt)
        rejects(lambda: rt.begin_context('observation-0'), MemoryError)
        assert rt.snapshot().halted == HOST_ALLOCATION_FAILURE
        rejects(lambda: rt.begin_context('observation-0'))
        with patch.object(_WindowsProcessHost, 'observe', side_effect=HostExecutionUnresolved('later diagnostic fault')):
            rejects(lambda: rt.snapshot(), HostExecutionUnresolved)
        assert rt.snapshot().halted == HOST_ALLOCATION_FAILURE
        return {'before': numeric_record(before), 'after': numeric_record(observation(rt)),
                'registered_window_refused_by_actual_host': True,
                'failed_diagnostic_preserves_original_allocation_halt': True,
                'reference_work_retained': rt.snapshot().resources['spent']['compiler']['work']}
    if mode == 'binding':
        rt = ReferenceCompilerRuntime(cfg, zero_program(2), host=host)
        measured = observation(rt)
        wrong = HostResourceContract(CAP*2, {'deployment': CAP*2, 'compiler': CAP*2})
        rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), host=wrong), HostExecutionUnresolved)
        # Data objects, including a genuine older observation, cannot replace
        # Runtime's fixed live binding or offer fake cheap counter values.
        for fake in (True, {'commit_cap': CAP}, measured, replace(measured, process_commit=0, lifetime_process_commit_peak=0)):
            rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), host=fake))
        unbound = ReferenceCompilerRuntime(cfg, zero_program(2))
        assert unbound.snapshot().host_resources is None and unbound.chi != rt.chi
        before = rt.snapshot()
        with patch.object(_WindowsProcessHost, 'observe', side_effect=HostExecutionUnresolved('injected native observation failure')):
            rejects(lambda: rt.construct_candidate(zero_program(2)), HostExecutionUnresolved)
        failed = rt.snapshot()
        assert failed.halted == HOST_RESOURCE_FAILURE and failed.candidates == before.candidates
        assert failed.resources == before.resources and failed.revision == before.revision
        rejects(lambda: rt.construct_candidate(zero_program(2)))
        with patch.object(_WindowsProcessHost, 'observe', side_effect=MemoryError('later diagnostic allocation fault')):
            rejects(lambda: rt.snapshot(), MemoryError)
        assert rt.snapshot().halted == HOST_RESOURCE_FAILURE
        return {'before': numeric_record(measured), 'after': numeric_record(observation(rt)),
                'mismatched_actual_caps_rejected': True, 'supplied_flags_maps_and_counter_records_rejected': 4,
                'host_registration_bound_into_claim_identity': True,
                'failed_diagnostic_preserves_original_resource_halt': True,
                'native_observation_failure_closes_authority_before_control_debit': True}
    assert mode == 'install'
    rt, proposal, ids = fixture(host=host)
    before = observation(rt)
    original = rt.snapshot()
    result = install(rt, proposal, ids)
    assert result.status == 'INSTALLED_CPU'
    installed = validate_residency(rt)
    assert installed.host_resources.contract == host
    assert installed.host_resources.process_identity == before.process_identity
    assert installed.alpha_spent == original.alpha_spent
    event(rt, 0)
    after = observation(rt)
    assert after.process_identity == before.process_identity
    assert after.lifetime_process_commit_peak >= before.lifetime_process_commit_peak
    assert after.job_user_100ns >= before.job_user_100ns
    return {'before': numeric_record(before), 'after': numeric_record(after),
            'complete_native_class_programs': proposal.programs_compared,
            'four_path_persistence_and_cpu_install_executed_in_same_bound_process': True,
            'ordinary_continuation_after_install': True,
            'alpha_spent': str(installed.alpha_spent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('binding', 'memory', 'install', 'late-fence', 'failed-exit'))
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker:
        result = worker('install' if args.worker == 'failed-exit' else args.worker)
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
        if args.worker == 'failed-exit':
            raise SystemExit(17)
        return
    rows = {}
    for mode in ('binding', 'memory', 'install', 'late-fence', 'failed-exit'):
        with tempfile.TemporaryDirectory(prefix='fp-bound-host-audit-', dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent == ROOT
            output = Path(temporary)/'result.json'
            outer_cap = CAP*2 if mode == 'late-fence' else CAP
            run = run_in_job(__file__, ('--worker', mode, '--output', output), commit_limit=outer_cap)
            if mode == 'failed-exit':
                assert run.exit_code == 17 and not run.timed_out and output.exists()
                rows[mode] = {'completed_looking_child_file_not_accepted_as_run_success': True, 'job': asdict(run)}
                continue
            assert run.exit_code == 0 and not run.timed_out, (mode, run)
            # Bounded diagnostic transport, not a general snapshot or an
            # authority decoder. A missing/truncated result cannot pass.
            with output.open('rb') as source:
                payload = source.read(8193)
            assert len(payload) <= 8192
            row = json.loads(payload)
            if mode == 'late-fence':
                assert row['lifetime_process_commit_peak'] <= run.peak_process_commit <= outer_cap
                rows[mode] = dict(row, completed_job=asdict(run))
                continue
            for stage in ('before', 'after'):
                observed = row[stage]
                assert (observed['process_id'], observed['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                assert observed['lifetime_process_commit_peak'] <= run.peak_process_commit <= CAP
                assert observed['job_commit_peak'] <= run.peak_job_commit <= CAP
                assert observed['job_user_100ns'] <= run.user_100ns
                assert observed['job_kernel_100ns'] <= run.kernel_100ns
                assert observed['process_user_100ns'] <= run.user_100ns
                assert observed['process_kernel_100ns'] <= run.kernel_100ns
            rows[mode] = dict(row, completed_job=asdict(run))
    result = {'status': 'PASS', 'scope': 'live Runtime host policy/process binding and declared commitment observations',
              'cases': rows, 'not_closed': ['complete ERC-1 manifest and run-level publication/error ownership',
                  'total-machine/shared-platform/device resources', 'target AMP and Runtime freeze']}
    if args.write:
        (ROOT/'evidence/minimal/FP_BOUND_HOST_RUNTIME_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
