"""Two fixed actual-device controls for detached Runtime public values.

Packed/shared toy histories test ownership during training and frozen reporting.
No corpus, performance comparison, installation or whole-release claim.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
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
CASES = ('packed', 'shared')
HOST, DEADLINE, ARENA = 4 << 30, 180000, 32 << 20
JOURNAL = ROOT/'evidence/minimal/FP_PUBLIC_VALUE_CUDA_A1.json'


def exercise(case, *, cuda):
    from audit_token_reporting import report_registration, cuda_contract, STORAGE
    from audit_public_value_boundary import wrappers
    from audit_reference_construction import limits, validate_residency
    from fp_reference import ReferenceCompilerRuntime, host_failure
    from fp_reference.core import ContractError
    from fp_reference.encoding import pack
    from fp_reference.host_resources import HostResourceContract
    from fp_reference.ingress import encode_context
    from fp_reference.shared_reference import decoded_buffer

    cc, program, online, reporting = report_registration(count=4, report_count=4)
    cc = replace(cc, limits=limits(384 << 20, 10**15))
    cfg = cuda_contract(cc.initializer_pattern) if cuda else None
    storage = STORAGE if case == 'shared' else None
    host = HostResourceContract(HOST, {r: HOST for r in ('deployment', 'compiler')}) if cuda else None
    rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
        cuda=cfg, shared_storage=storage, host=host)
    control = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting)
    owned = (rt._contract, rt._online, rt._token_report_contract, tuple(rt._programs.values()),
             None if cfg is None else rt._cuda.contract)
    before = pack(owned)
    assert not wrappers(owned) & wrappers((cc, program, online, reporting, cfg))
    cc.__dict__['normalizer_cap'] = F(1)
    program.__dict__['definition'] = None
    online.data.streams[0].__dict__['observation_ids'] = ('foreign',)
    reporting.__dict__['stream_id'] = 'foreign'
    if cfg is not None:
        cfg.__dict__['state_atol'] = F(1 << 30)
        cfg.storage.__dict__['arena_bytes'] = 1
    rt.contract.__dict__.clear()
    rt.online_contract.__dict__.clear()
    assert pack(owned) == before

    for index, target in enumerate((0, 1, 1, 0)):
        forecasts = [root.predict_next(f'train/{index}', encode_context(())) for root in (rt, control)]
        assert all(f.status == 'PREDICTED_REFERENCE' for f in forecasts)
        left, right = (f.predictions[0][1] for f in forecasts)
        assert tuple(left) == tuple(right)
        left.origin.__dict__['output'] = left.origin.W[::-1].tobytes()
        public = rt.snapshot()
        private = (owned, rt._candidates, rt._pending, tuple(rt._observations),
                   () if not cuda else tuple(rt._cuda.phases.values()))
        assert not wrappers(public) & wrappers(private)
        public.pending.record.sources.__dict__['past'] = (1, 1, 1)
        if cuda:
            public.cuda.contract.__dict__['state_atol'] = F(1 << 30)
            public.cuda.phases[-1].__dict__['status'] = 'FORGED_PUBLIC_PHASE'
        for root in (rt, control):
            result = root.observe(target)
            assert result.status == 'OBSERVED_REFERENCE', result.reason
        a, b = (root.snapshot() for root in (rt, control))
        assert a.candidates[0].learner == b.candidates[0].learner
        assert a.observations == b.observations
        a.observations[-1].__dict__['target'] = 1-target
        a.candidates[0].learner.origin.__dict__['output'] = b'changed public learner'

    frozen = rt._candidates[rt._deployed_id].learner
    assert (frozen.cursor, frozen.optimizer_steps, frozen.unit_count) == (4, 2, 0)
    if cuda:
        frozen_current, frozen_staged = dict(rt._cuda.current), dict(rt._cuda.staged)
        frozen_words = rt._cuda._values[frozen_current[rt._deployed_id]].raw()
    for root in (rt, control):
        assert root.begin_report().status == 'REPORTING'
    for index, target in enumerate((1, 0, 0, 1)):
        for root in (rt, control):
            assert root.predict_report(f'report/{index}').status == 'PREDICTED_REPORT'
        public = rt.snapshot()
        public.token_report.learner.origin.__dict__['output'] = b'changed public frozen learner'
        public.token_report.pending.record.sources.__dict__['past'] = (1, 1, 1)
        if cuda:
            public.cuda.phases[-1].__dict__['status'] = 'FORGED_PUBLIC_REPORT'
        a, b = (root.observe_report(target) for root in (rt, control))
        assert a.status == b.status == ('COMPLETE_REPORT' if index == 3 else 'SCORED_REPORT')
        assert rt._token_report.native_total == control._token_report.native_total
        assert rt._token_report.records == control._token_report.records
        assert (rt._token_report.events[-1].physical_loss is not None) == cuda
        assert rt._candidates[rt._deployed_id].learner is frozen

    a, b = (root.report_result() for root in (rt, control))
    assert a.native_mean == b.native_mean and (a.physical_mean is not None) == cuda
    a.native_mean.__dict__['lower'] = F(0)
    assert rt.report_result().native_mean == control.report_result().native_mean

    snapshot = validate_residency(rt)
    assert snapshot.halted is None and snapshot.cursor == 4
    assert len(snapshot.token_report.events) == len(snapshot.token_report.records) == 4
    phase_bytes = frames = words = 0
    if cuda:
        assert (rt._cuda.current, rt._cuda.staged) == (frozen_current, frozen_staged)
        assert rt._cuda._values[frozen_current[rt._deployed_id]].raw() == frozen_words
        assert len(snapshot.cuda.phases) == 19
        buffers = dict(snapshot.buffers)
        for phase in snapshot.cuda.phases:
            assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
            raw = (b''.join(decoded_buffer(snapshot, phase.object_id, byte_cap=STORAGE.expanded_cap,
                reference_cap=STORAGE.reference_cap)) if storage else buffers[phase.object_id])
            body = pack(phase)  # Uncached complete actual phase, not a retained-image lookup.
            size = int.from_bytes(raw[:8], 'big')
            assert len(raw) == 1 << 20 and size == len(body)
            assert raw[8:8+size] == body and not any(raw[8+size:])
            phase_bytes += len(body)
            frames += len(raw)
            words += phase.forward_operations
        rt._cuda.check()
        arena = rt._cuda.arena
        assert arena._counter == arena._allocation_counter() == (1, ARENA, 1)

    # A failed export after the completed report preserves all actual outcomes
    # and makes further non-diagnostic access terminal, including on CUDA.
    with patch.object(host_failure, 'detached', side_effect=MemoryError('public export control')):
        try:
            rt.report_result()
        except MemoryError:
            pass
        else:
            raise AssertionError('copy allocation failure was hidden')
    final = validate_residency(rt)
    assert final.halted is host_failure.HOST_ALLOCATION_FAILURE
    assert final.token_report == snapshot.token_report and final.candidates == snapshot.candidates
    try:
        rt.report_result()
    except ContractError:
        pass
    else:
        raise AssertionError('failed public export regained authority')
    result = dict(training_events=4, optimizer_commits=2, report_events=4,
        exact_native_trajectory_equal_to_unattacked_control=True,
        supplied_registrations_and_public_wrappers_isolated=True,
        frozen_private_native_learner_preserved=True,
        frozen_private_physical_learner_preserved=True if cuda else None,
        terminal_export_failure_preserves_completed_prefix=True,
        checked_phases=19 if cuda else 0, checked_primitive_words=words,
        complete_phase_bytes=phase_bytes, complete_frame_bytes=frames,
        uncached_complete_frames_and_padding_checked=cuda,
        paid_reference_peak=final.resources['peak']['reference_payload_bytes'])
    if cuda:
        result['arena'] = dict(native_allocation_counter=arena._counter,
            current_allocation_counter=arena._allocation_counter(), consumed_bytes=arena._cursor,
            **arena._last_usage)
    return result, rt


def publish(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)


def worker(case, output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST, {r: HOST for r in ('deployment', 'compiler')}))
    started = time.perf_counter()
    result = dict(status='RUNNING', case=case, before=measured(host))
    publish(output, result)
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = exercise(case, cuda=True)
        result.update(status='PASS_ACTUAL_PUBLIC_VALUE_BOUNDARY', outcome=outcome,
            device=asdict(rt._cuda._device.check()))
    except Exception as error:
        result.update(status='FAILED', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    publish(output, result)
    return 0 if result['status'] == 'PASS_ACTUAL_PUBLIC_VALUE_BOUNDARY' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('original journal exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs before launch')
    cpu = json.loads((ROOT/'evidence/minimal/FP_PUBLIC_VALUE_REGRESSION_CPU.json').read_text(encoding='utf-8'))
    assert cpu['status'] == 'PASS_PUBLIC_VALUE_REGRESSION_CPU' and cpu['audit_count'] == 16
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=HOST,
        deadline_ms=DEADLINE, arena_bytes=ARENA, allocator_reserved_cap=ARENA,
        whole_board_VRAM_upper=24 << 30, protocol='experiments/next_token/PUBLIC_VALUE_CUDA_A1.md',
        scope=__doc__.strip(), results=[])
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for case in CASES:
            journal['active_case'] = case
            publish(JOURNAL, journal)
            with tempfile.TemporaryDirectory(prefix='fp-public-value-cuda-') as directory:
                output = Path(directory)/'worker.json'
                started = time.perf_counter()
                job = run_in_job(__file__, ('--worker', case, '--output', output),
                    commit_limit=HOST, timeout_ms=DEADLINE)
                row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
                journal['results'].append(row)
                if output.exists():
                    data = output.read_bytes()
                    if len(data) > 65536:
                        raise RuntimeError('unexpected oversized worker receipt')
                    row['result'] = json.loads(data)
                result = row.get('result', {})
                accepted = job.exit_code == 0 and not job.timed_out and result.get('status') == 'PASS_ACTUAL_PUBLIC_VALUE_BOUNDARY'
                row['accepted_execution'] = accepted
                if accepted:
                    assert job.attached_before_resume and job.peak_job_commit <= HOST
                    for moment in ('before', 'after'):
                        measurement = result[moment]
                        assert (measurement['process_id'], measurement['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                        assert measurement['job_commit_peak'] <= job.peak_job_commit
                        assert measurement['lifetime_process_commit_peak'] <= job.peak_process_commit
                    outcome = result['outcome']
                    assert (outcome['training_events'], outcome['optimizer_commits'], outcome['report_events'], outcome['checked_phases']) == (4, 2, 4, 19)
                    assert outcome['complete_frame_bytes'] == 19 << 20
                    assert outcome['arena']['native_allocation_counter'] == outcome['arena']['current_allocation_counter'] == [1, ARENA, 1]
                print(case+': '+result.get('status', 'NO_COMPLETE_RESULT'), flush=True)
                publish(JOURNAL, journal)
                if not accepted:
                    journal['status'] = 'UNRESOLVED_PUBLIC_VALUE_CUDA_A1'
                    break
        else:
            journal['status'] = 'COMPLETE_PUBLIC_VALUE_CUDA_A1'
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        journal.pop('active_case', None)
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--cpu', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.cpu:
        result = {case: exercise(case, cuda=False)[0] for case in CASES}
        assert 'torch' not in sys.modules
        result = dict(status='PASS_PUBLIC_VALUE_DEVICE_HARNESS_CPU', cases=result,
            actual_cuda_execution=False, scope='native controls for the new actual-device harness')
        publish(ROOT/'evidence/minimal/FP_PUBLIC_VALUE_DEVICE_HARNESS_CPU.json', result)
        print(json.dumps(result, indent=2))
    elif args.worker:
        if args.output is None:
            parser.error('worker output is required')
        raise SystemExit(worker(args.worker, args.output))
    else:
        launch()
