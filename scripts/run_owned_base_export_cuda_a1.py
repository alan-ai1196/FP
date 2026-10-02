"""One fact-enabled actual AMP ownership control; no corpus or timing comparison."""
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from run_public_value_cuda_a1 import exercise, publish, HOST, DEADLINE, ARENA
from audit_public_value_regression import git

JOURNAL = ROOT/'evidence/minimal/FP_OWNED_BASE_EXPORT_CUDA_A1.json'
HARNESS = ROOT/'evidence/minimal/FP_OWNED_BASE_EXPORT_DEVICE_HARNESS_CPU.json'
CAP = 1 << 20


def control(*, cuda):
    import audit_token_reporting as fixture
    from fp_reference import token_base_facts as facts, public_values
    from fp_reference.encoding import pack
    known, shortcuts, owners = facts.positive_base_known, [0], set()
    def observed(value):
        answer = known(value)
        frame = sys._getframe(1)
        if answer and frame.f_code.co_name == 'visit' and frame.f_globals.get('__name__') == public_values.__name__:
            fact = facts._ACTIVE.get()
            assert fact is not None and fact.source is value
            shortcuts[0] += 1
            owners.add(id(fact))
        return answer
    with patch.object(fixture, 'STORAGE', replace(fixture.STORAGE, token_invariant_bytes=CAP)), \
            patch.object(facts, 'positive_base_known', observed):
        result, rt = exercise('shared', cuda=cuda)
    fact = rt._reference_archive.base_facts
    assert shortcuts[0] > 0 and owners == {id(fact)} and facts._ACTIVE.get() is None
    assert fact.source is rt._contract.initializer_pattern.output.base
    body = (facts.FACT_ID, fact.source, fact.total, fact.required_bits)
    assert rt._buffers[fact.buffer] == pack(body) and len(rt._buffers[fact.buffer]) == fact.size <= CAP
    leases = rt._ledger._refs[fact.buffer]
    assert rt._data_owner in leases and rt._reference_archive.deployment_owner in leases
    result['owned_base_export'] = dict(actual_immutable_source_shortcuts=shortcuts[0],
        actual_owner_count=len(owners), paid_fact_bytes=fact.size, both_roles_hold_complete_bound_artifact=True,
        exact_tuple_identity_bound=True, scope_cleared_after_control=True)
    return result, rt


def worker(output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')}))
    started = time.perf_counter()
    result = dict(status='RUNNING', before=measured(host))
    publish(output, result)
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = control(cuda=True)
        result.update(status='PASS_ACTUAL_OWNED_BASE_EXPORT', outcome=outcome,
            device=asdict(rt._cuda._device.check()))
    except Exception as error:
        result.update(status='UNRESOLVED', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    publish(output, result)
    return 0 if result['status'] == 'PASS_ACTUAL_OWNED_BASE_EXPORT' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('original journal exists; never replay')
    if git('status', '--porcelain'):
        raise RuntimeError('commit all execution inputs before launch')
    for name, status in (('FP_OWNED_BASE_EXPORT_CPU.json', 'PASS_OWNED_BASE_EXPORT_CPU'),
            ('FP_OWNED_BASE_EXPORT_DEVICE_HARNESS_CPU.json', 'PASS_OWNED_BASE_EXPORT_DEVICE_HARNESS_CPU'),
            ('FP_OWNED_BASE_EXPORT_REGRESSION_CPU.json', 'PASS_OWNED_BASE_EXPORT_REGRESSION_CPU')):
        receipt = json.loads((ROOT/'evidence/minimal'/name).read_text(encoding='utf-8'))
        assert receipt['status'] == status
    assert receipt['audit_count'] == 19 and not receipt['failures']
    source = git('rev-parse', 'HEAD')
    # A later receipt/doc commit is allowed; changed production or harness
    # inputs cannot borrow the earlier fixed-source CPU qualification.
    assert not git('diff', receipt['source_commit'], source, '--', 'src/reference_compiler',
        'scripts/audit_owned_base_export.py', 'scripts/run_owned_base_export_cuda_a1.py')
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, host_cap=HOST, deadline_ms=DEADLINE,
        arena_bytes=ARENA, allocator_reserved_cap=ARENA, whole_board_VRAM_upper=24 << 30,
        token_base_fact_cap=CAP, protocol='experiments/next_token/OWNED_BASE_EXPORT_CUDA_A1.md',
        scope=__doc__.strip())
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-owned-base-export-') as directory:
            output = Path(directory)/'worker.json'
            started = time.perf_counter()
            job = run_in_job(__file__, ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
            journal.update(job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            if output.exists():
                raw = output.read_bytes()
                if len(raw) > 65536:
                    raise RuntimeError('unexpected oversized worker receipt')
                journal['result'] = json.loads(raw)
            result = journal.get('result', {})
            accepted = job.exit_code == 0 and not job.timed_out and result.get('status') == 'PASS_ACTUAL_OWNED_BASE_EXPORT'
            if accepted:
                assert job.attached_before_resume and job.peak_job_commit <= HOST
                for moment in ('before', 'after'):
                    sample = result[moment]
                    assert (sample['process_id'], sample['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                    assert sample['job_commit_peak'] <= job.peak_job_commit
                    assert sample['lifetime_process_commit_peak'] <= job.peak_process_commit
                outcome = result['outcome']
                assert (outcome['training_events'], outcome['optimizer_commits'], outcome['report_events'],
                        outcome['checked_phases']) == (4, 2, 4, 19)
                assert outcome['complete_frame_bytes'] == 19 << 20
                assert outcome['arena']['native_allocation_counter'] == outcome['arena']['current_allocation_counter'] == [1, ARENA, 1]
                assert outcome['owned_base_export']['actual_immutable_source_shortcuts'] > 0
            journal.update(status='COMPLETE_OWNED_BASE_EXPORT_CUDA_A1' if accepted else 'UNRESOLVED_OWNED_BASE_EXPORT_CUDA_A1',
                accepted_execution=accepted)
        assert git('rev-parse', 'HEAD') == source and not git('status', '--porcelain', '--untracked-files=no')
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--cpu', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.cpu:
        if HARNESS.exists():
            parser.error('original harness receipt exists')
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('worker attempted subprocess')):
            result, _ = control(cuda=False)
        assert 'torch' not in sys.modules
        receipt = dict(status='PASS_OWNED_BASE_EXPORT_DEVICE_HARNESS_CPU', outcome=result,
            subprocess_creation_forbidden_across_control=True, actual_cuda_execution=False)
        with HARNESS.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, indent=2)+'\n')
        print(receipt['status'], flush=True)
    elif args.worker:
        if args.output is None:
            parser.error('worker output is required')
        raise SystemExit(worker(args.output))
    else:
        launch()
