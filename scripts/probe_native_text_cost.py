"""One bounded native Runtime cost diagnosis, without AMP or a model score.

Retain the original million-target declaration and model, observe only sixteen
targets as a diagnostic, and profile prediction/observation at indices 0 and 15.
All ordinary native checks, ownership and retention run unchanged.
"""
from dataclasses import asdict
from pathlib import Path
import argparse
import cProfile
import json
import os
import pstats
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
JOURNAL = ROOT/'evidence/minimal/FP_NATIVE_TEXT_COST_A1.json'
HOST, DEADLINE, EVENTS, SAMPLES = 16 << 30, 180000, 16, (0, 15)


def measure(action):
    profiler = cProfile.Profile()
    started = time.perf_counter()
    value = profiler.runcall(action)
    wall = time.perf_counter()-started
    stats = pstats.Stats(profiler)
    def filename(name):
        try:
            return Path(name).relative_to(ROOT).as_posix()
        except ValueError:
            return Path(name).name
    def row(item):
        (file, line, name), (primitive, calls, own, cumulative, callers) = item
        return dict(function=f'{filename(file)}:{line}:{name}', calls=calls,
            primitive_calls=primitive, self_seconds=own, cumulative_seconds=cumulative)
    modules = {}
    for (file, _, _), (_, _, own, _, _) in stats.stats.items():
        key = filename(file)
        modules[key] = modules.get(key, 0.0)+own
    assert abs(sum(modules.values())-stats.total_tt) < 1e-6
    return value, dict(wall_seconds=wall, total_calls=stats.total_calls,
        total_self_seconds=stats.total_tt,
        cumulative_top=[row(x) for x in sorted(stats.stats.items(), key=lambda x: x[1][3], reverse=True)[:20]],
        self_top=[row(x) for x in sorted(stats.stats.items(), key=lambda x: x[1][2], reverse=True)[:16]],
        module_self_seconds=sorted(modules.items(), key=lambda x: x[1], reverse=True)[:16],
        cumulative_rows_overlap_do_not_sum=True)


def worker(output):
    from run_native_text_a1 import registration, TRAIN, progress, complete_residency, publish
    from run_text_baseline_anchor_a1 import tape
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from audit_token_reference_host import measured
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    started = time.perf_counter()
    result = dict(status='RUNNING', before=measured(host), profiled={}, unprofiled_seconds=[])
    save = lambda: publish(output, result)
    save()
    try:
        training, identity = tape('train', TRAIN)
        old = json.loads((ROOT/'evidence/minimal/FP_NATIVE_TEXT_A1.json').read_text(encoding='utf-8'))
        assert old['status'] == 'UNRESOLVED_NATIVE_TEXT_A1'
        assert identity['prefix_sha256'] == old['result']['training_source']['prefix_sha256']
        result['training_source'] = identity
        cc, program, online, storage, reporting = registration()
        assert len(online.data.active.observation_ids) == TRAIN == 1048576
        result['program_id'] = program.program_id
        init = time.perf_counter()
        rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
            reporting=reporting, host=host_contract)
        result['initialization_seconds'] = time.perf_counter()-init
        save()
        for index, target in enumerate(training[:EVENTS]):
            for label, action, expected in (
                ('predict', lambda: rt.predict_next(f'train/{index}', encode_context(())), 'PREDICTED_REFERENCE'),
                ('observe', lambda: rt.observe(int(target)), 'OBSERVED_REFERENCE')):
                if index in SAMPLES:
                    outcome, report = measure(action)
                    result['profiled'][f'{label}/{index}'] = report
                else:
                    start = time.perf_counter()
                    outcome = action()
                    result['unprofiled_seconds'].append(time.perf_counter()-start)
                assert outcome.status == expected, outcome.reason
                save()
        state = rt._candidates[rt._deployed_id].learner
        assert (rt._cursor, state.cursor, state.unit_count, state.optimizer_steps) == (16, 16, 16, 0)
        assert len(rt._observations) == len(rt._event_traces) == 16
        assert tuple(r.target for r in rt._observations) == tuple(map(int, training[:16]))
        for index, record in enumerate(rt._observations):
            expected = tuple(50257 if lag > index else int(training[index-lag]) for lag in range(1, 513))
            assert record.cursor == index and record.sources.past == expected
        assert rt._token_report is None and rt._cuda is None and 'torch' not in sys.modules
        result.update(status='PASS_NATIVE_TEXT_COST_A1', latest=progress(rt, label='terminal', started=started),
            residency=complete_residency(rt), all_original_sources_targets_and_traces_retained=True,
            original_training_declaration=TRAIN, actual_amp_execution=False, model_score=None)
    except Exception as error:
        result.update(status='UNRESOLVED_NATIVE_TEXT_COST_A1', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-4000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    save()
    return 0 if result['status'] == 'PASS_NATIVE_TEXT_COST_A1' else 2


def launch():
    from windows_job_audit_support import run_in_job
    from run_native_text_a1 import publish
    if JOURNAL.exists():
        raise RuntimeError('original diagnostic exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all diagnostic inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, host_cap=HOST, deadline_ms=DEADLINE,
        observed_events=EVENTS, profiled_events=SAMPLES, original_training_declaration=1048576,
        scope=__doc__.strip(), protocol='experiments/next_token/NATIVE_TEXT_COST_A1.md')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-native-text-cost-') as directory:
            output = Path(directory)/'worker.json'
            run = run_in_job(__file__, ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
            journal['job'] = asdict(run)
            if output.exists():
                payload = output.read_bytes()
                if len(payload) > 131072:
                    raise RuntimeError('unexpected diagnostic receipt size')
                journal['result'] = json.loads(payload)
        result = journal.get('result', {})
        accepted = run.exit_code == 0 and not run.timed_out and result.get('status') == 'PASS_NATIVE_TEXT_COST_A1'
        if accepted:
            assert run.attached_before_resume and run.peak_job_commit <= HOST
            for moment in ('before', 'after'):
                measured = result[moment]
                assert (measured['process_id'], measured['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                assert measured['job_commit_peak'] <= run.peak_job_commit
                assert measured['lifetime_process_commit_peak'] <= run.peak_process_commit
            assert set(result['profiled']) == {f'{op}/{i}' for i in SAMPLES for op in ('predict', 'observe')}
            assert len(result['unprofiled_seconds']) == 28 and result['model_score'] is None
            assert not result['actual_amp_execution'] and result['original_training_declaration'] == 1048576
        journal.update(status='COMPLETE_NATIVE_TEXT_COST_A1' if accepted else 'UNRESOLVED_NATIVE_TEXT_COST_A1',
            accepted_execution=accepted)
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


def control():
    from audit_token_reporting import setup
    from fp_reference.ingress import encode_context
    rt, _ = setup()
    prediction, a = measure(lambda: rt.predict_next('train/0', encode_context(())))
    observed, b = measure(lambda: rt.observe(0))
    assert prediction.status == 'PREDICTED_REFERENCE' and observed.status == 'OBSERVED_REFERENCE'
    assert rt.snapshot().cursor == 1 and all(r['total_calls'] > 0 for r in (a, b))
    assert 'torch' not in sys.modules
    print('PASS_NATIVE_TEXT_COST_HARNESS_CPU')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    mode.add_argument('--control', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.control:
        control()
    elif args.worker:
        if args.output is None:
            parser.error('worker output required')
        raise SystemExit(worker(args.output))
    else:
        launch()
