"""One original/projection native text pair at a 256-target prefix.

Full million-target declaration and all checks remain; no AMP or model score.
"""
from contextlib import nullcontext
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
JOURNAL = ROOT/'evidence/minimal/FP_LEDGER_PROJECTION_COST_A1.json'
ARTIFACTS = Path(r'F:\experiment\FP_ledger_projection_a1')
HOST, DEADLINE, EVENTS, BLOCK = 16 << 30, 900000, 256, 64
MODES = ('original', 'projection')


def worker(mode, output):
    from run_native_text_a1 import registration, TRAIN, progress, complete_residency, publish
    from run_text_baseline_anchor_a1 import tape
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from audit_token_reference_host import measured
    from probe_native_stream_cost import python_oracle, capture_allocations, verify_bytes
    from ledger_projection_audit_support import original_observe, BASELINE
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    started = time.perf_counter()
    result = dict(status='RUNNING', mode=mode, before=measured(host), blocks=[],
        original_observe_source=BASELINE, completed_targets=0)
    save = lambda: publish(output, result)
    save()
    try:
        oracle = python_oracle()
        baseline_source = (ARTIFACTS/'original_observe.py').read_bytes()
        declared = json.loads(JOURNAL.read_text(encoding='utf-8'))['baseline_method']
        assert len(baseline_source) == declared['bytes']
        assert hashlib.sha256(baseline_source).hexdigest() == declared['sha256']
        result['baseline_method'] = declared
        context = (patch.object(ReferenceCompilerRuntime, 'observe',
            original_observe(baseline_source.decode('utf-8'))) if mode == 'original' else nullcontext())
        training, identity = tape('train', TRAIN)
        old = json.loads((ROOT/'evidence/minimal/FP_NATIVE_TEXT_A1.json').read_text(encoding='utf-8'))
        assert old['status'] == 'UNRESOLVED_NATIVE_TEXT_A1'
        assert identity['prefix_sha256'] == old['result']['training_source']['prefix_sha256']
        result['training_source'] = identity
        with context, capture_allocations() as records:
            cc, program, online, storage, reporting = registration()
            assert len(online.data.active.observation_ids) == TRAIN == 1048576
            result['program_id'] = program.program_id
            init = time.perf_counter()
            rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
                reporting=reporting, host=host_contract)
            result['initialization_seconds'] = time.perf_counter()-init
            save()
            for index, target in enumerate(training[:EVENTS]):
                if index % BLOCK == 0:
                    result['blocks'].append(dict(first_target=index, completed=0,
                        predict_seconds=0.0, observe_seconds=0.0))
                block = result['blocks'][-1]
                for label, action, expected in (
                    ('predict', lambda: rt.predict_next(f'train/{index}', encode_context(())), 'PREDICTED_REFERENCE'),
                    ('observe', lambda: rt.observe(int(target)), 'OBSERVED_REFERENCE')):
                    start = time.perf_counter()
                    outcome = action()
                    block[label+'_seconds'] += time.perf_counter()-start
                    assert outcome.status == expected, outcome.reason
                block['completed'] += 1
                result['completed_targets'] = index+1
                if (index+1) % 16 == 0:
                    result['latest'] = progress(rt, label='ordinary', started=started)
                    save()
            result['ordinary_seconds'] = sum(b['predict_seconds']+b['observe_seconds'] for b in result['blocks'])
            state = rt._candidates[rt._deployed_id].learner
            assert (rt._cursor, state.cursor, state.unit_count, state.optimizer_steps) == (EVENTS, EVENTS, EVENTS, 0)
            assert len(rt._observations) == len(rt._event_traces) == EVENTS
            assert tuple(r.target for r in rt._observations) == tuple(map(int, training[:EVENTS]))
            for index, record in enumerate(rt._observations):
                expected = tuple(50257 if lag > index else int(training[index-lag]) for lag in range(1, 513))
                assert record.cursor == index and record.sources.past == expected
            assert rt._token_report is None and rt._cuda is None and 'torch' not in sys.modules
            assert not any('_compiled_stream_' in name for name in sys.modules)
            result.update(latest=progress(rt, label='terminal', started=started),
                residency=complete_residency(rt), original_training_declaration=TRAIN,
                all_original_sources_targets_and_traces_retained=True,
                actual_amp_execution=False, model_score=None)
            save()
            audit_start = time.perf_counter()
            result['independent_bytes'] = verify_bytes(rt, records, oracle)
            result['independent_audit_seconds'] = time.perf_counter()-audit_start
            result['status'] = 'PASS_LEDGER_PROJECTION_COST_A1'
    except Exception as error:
        result.update(status='UNRESOLVED_LEDGER_PROJECTION_COST_A1', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-4000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    save()
    return 0 if result['status'] == 'PASS_LEDGER_PROJECTION_COST_A1' else 2


def launch():
    from windows_job_audit_support import run_in_job
    from run_native_text_a1 import publish
    from ledger_projection_audit_support import BASELINE, original_observe_source
    if JOURNAL.exists() or ARTIFACTS.exists():
        raise RuntimeError('original projection cost control/artifacts exist; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all control inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    ARTIFACTS.mkdir(parents=True)
    baseline_source = original_observe_source().encode('utf-8')
    (ARTIFACTS/'original_observe.py').write_bytes(baseline_source)
    baseline_method = dict(source_commit=BASELINE, bytes=len(baseline_source),
        sha256=hashlib.sha256(baseline_source).hexdigest())
    journal = dict(status='RUNNING', source_commit=source, original_observe_source=BASELINE,
        baseline_method=baseline_method,
        host_cap=HOST, deadline_ms=DEADLINE, observed_events=EVENTS,
        original_training_declaration=1048576, order=MODES, results=[],
        protocol='experiments/next_token/LEDGER_PROJECTION_COST_A1.md')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for mode in MODES:
            output = ARTIFACTS/(mode+'.json')
            started = time.perf_counter()
            run = run_in_job(__file__, ('--worker', '--mode', mode, '--output', output),
                commit_limit=HOST, timeout_ms=DEADLINE)
            item = dict(mode=mode, job=asdict(run), launcher_seconds=time.perf_counter()-started,
                external_heartbeat=str(output))
            if output.exists():
                payload = output.read_bytes()
                if len(payload) > 131072:
                    raise RuntimeError('unexpected projection-cost receipt size')
                item['result'] = json.loads(payload)
            result = item.get('result', {})
            accepted = (run.exit_code == 0 and not run.timed_out
                and result.get('status') == 'PASS_LEDGER_PROJECTION_COST_A1')
            if accepted:
                assert run.attached_before_resume and run.peak_job_commit <= HOST
                for moment in ('before', 'after'):
                    sample = result[moment]
                    assert (sample['process_id'], sample['creation_100ns']) == (
                        run.process_id, run.process_creation_100ns)
                    assert sample['job_commit_peak'] <= run.peak_job_commit
                    assert sample['lifetime_process_commit_peak'] <= run.peak_process_commit
                assert result['completed_targets'] == EVENTS and result['model_score'] is None
                assert [b['first_target'] for b in result['blocks']] == list(range(0, EVENTS, BLOCK))
                assert all(b['completed'] == BLOCK for b in result['blocks'])
                assert not result['actual_amp_execution'] and result['original_training_declaration'] == 1048576
                assert result['independent_bytes']['records'] > 0 and result['independent_bytes']['images'] > 0
                assert result['baseline_method'] == baseline_method
            item['accepted_execution'] = accepted
            journal['results'].append(item)
            publish(JOURNAL, journal)
            print(mode, result.get('status', 'MISSING'), flush=True)
        accepted = all(r['accepted_execution'] for r in journal['results'])
        journal.update(status='COMPLETE_LEDGER_PROJECTION_COST_A1' if accepted else 'UNRESOLVED_LEDGER_PROJECTION_COST_A1',
            accepted_execution=accepted)
        if accepted:
            original, projection = [r['result'] for r in journal['results']]
            assert original['program_id'] == projection['program_id']
            assert original['residency'] == projection['residency']
            assert original['independent_bytes'] == projection['independent_bytes']
            for name in ('completed_training_targets', 'revealed_training_targets', 'optimizer_steps',
                         'pending_targets', 'event_traces', 'live_objects', 'retired_objects',
                         'resource_events', 'paid_payload_peak', 'object_peak', 'spent', 'halted'):
                assert original['latest'][name] == projection['latest'][name]
            journal['paid_counters_and_complete_byte_totals_equal'] = True
            journal['observed_original_over_projection_ordinary_seconds'] = (
                original['ordinary_seconds']/projection['ordinary_seconds'])
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
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.ingress import encode_context
    from audit_token_reporting import setup
    from ledger_projection_audit_support import original_observe, original_observe_source
    from probe_native_stream_cost import python_oracle, capture_allocations, verify_bytes
    oracle = python_oracle()
    source = original_observe_source()
    with patch('subprocess.check_output', side_effect=AssertionError('bounded worker spawned a subprocess')):
        original = original_observe(source)
    for mode in MODES:
        context = (patch.object(ReferenceCompilerRuntime, 'observe', original)
            if mode == 'original' else nullcontext())
        with context, capture_allocations() as records:
            rt, _ = setup(shared=True)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
            assert verify_bytes(rt, records, oracle)['records'] > 0
    assert 'torch' not in sys.modules
    print('PASS_LEDGER_PROJECTION_COST_HARNESS_CPU')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    mode.add_argument('--control', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--mode', choices=MODES)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.control:
        control()
    elif args.worker:
        if args.output is None or args.mode is None:
            parser.error('worker output and mode required')
        raise SystemExit(worker(args.mode, args.output))
    else:
        launch()
