"""One two-unit full-vocabulary native resource diagnosis; no text score."""
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
JOURNAL = ROOT/'evidence/minimal/FP_OWNED_TRANSITION_COST_A1.json'
ARTIFACTS = Path(r'F:\experiment\FP_owned_transition_cost_a1')
HOST, DEADLINE, EVENTS, BLOCK = 16 << 30, 1800000, 1024, 64


def independent_residency(rt):
    """Fold complete actual buffers/leases, without accepting index totals."""
    from run_native_text_a1 import complete_residency
    ledger = rt._ledger
    current = {key: 0 for key in ledger.limits.global_residency}
    roles = {role: dict(current) for role in ledger.limits.role_residency}
    assert len(ledger._objects) == len(rt._buffers)
    for key, buf in rt._buffers.items():
        spec, refs = ledger._objects[key], ledger._refs[key]
        extent = {'reference_payload_bytes': len(buf), 'physical_objects': 1}
        assert spec.residency == extent and refs and all(type(n) is int and n > 0 for n in refs.values())
        assert all(owner in ledger._owners and owner not in ledger._closed_owners for owner in refs)
        present = {ledger._owners[owner] for owner in refs}
        for dimension, amount in extent.items():
            current[dimension] += amount
            for role in present:
                roles[role][dimension] += amount
    result = complete_residency(rt)
    assert result['current'] == current and result['role_current'] == roles
    result['every_role_recomputed_from_complete_leaves_and_actual_buffers'] = True
    return result


def worker(output):
    from run_native_text_a1 import registration, TRAIN, progress, publish
    from run_text_baseline_anchor_a1 import tape
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from audit_token_reference_host import measured
    from probe_native_stream_cost import python_oracle, capture_allocations, verify_bytes
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    started, rt = time.perf_counter(), None
    result = dict(status='RUNNING', before=measured(host), blocks=[], completed_targets=0,
        original_training_declaration=TRAIN, actual_amp_execution=False, model_score=None)
    save = lambda: publish(output, result)
    save()
    try:
        oracle = python_oracle()
        training, identity = tape('train', TRAIN)
        anchor = json.loads((ROOT/'evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json').read_text(encoding='utf-8'))
        assert anchor['status'] == 'COMPLETE_TEXT_BASELINE_ANCHOR_A1'
        assert identity['prefix_sha256'] == anchor['results'][0]['result']['train_source']['prefix_sha256']
        result['training_source'] = identity
        with capture_allocations() as records:
            cc, program, online, storage, reporting = registration()
            assert len(online.data.active.observation_ids) == TRAIN == 1048576
            assert online.learner.update_unit == 512
            result['program_id'] = program.program_id
            initial = time.perf_counter()
            rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
                reporting=reporting, host=host_contract)
            result['initialization_seconds'] = time.perf_counter()-initial
            result['initialized'] = progress(rt, label='initialized', started=started)
            save()
            for index, target in enumerate(training[:EVENTS]):
                if index % BLOCK == 0:
                    result['blocks'].append(dict(first_target=index, completed=0,
                        predict_seconds=0.0, observe_seconds=0.0))
                block = result['blocks'][-1]
                for label, action, expected in (
                    ('predict', lambda: rt.predict_next(f'train/{index}', encode_context(())), 'PREDICTED_REFERENCE'),
                    ('observe', lambda: rt.observe(int(target)), 'OBSERVED_REFERENCE')):
                    tick = time.perf_counter()
                    answer = action()
                    block[label+'_seconds'] += time.perf_counter()-tick
                    assert answer.status == expected, answer.reason
                block['completed'] += 1
                result['completed_targets'] = index+1
                if (index+1) % 16 == 0:
                    result['latest'] = progress(rt, label='ordinary', started=started)
                    save()
            result['ordinary_seconds'] = sum(b['predict_seconds']+b['observe_seconds'] for b in result['blocks'])
            state = rt._candidates[rt._deployed_id].learner
            assert (rt._cursor, state.cursor, state.unit_count, state.optimizer_steps) == (EVENTS, EVENTS, 0, 2)
            assert len(rt._observations) == len(rt._event_traces) == EVENTS
            assert [i+1 for i, event in enumerate(rt._event_traces) if event.after_commit is not None] == [512, 1024]
            assert tuple(r.target for r in rt._observations) == tuple(map(int, training[:EVENTS]))
            for i, record in enumerate(rt._observations):
                assert record.cursor == i and record.sources.past == tuple(
                    50257 if lag > i else int(training[i-lag]) for lag in range(1, 513))
            assert rt._token_report is None and rt._cuda is None and 'torch' not in sys.modules
            assert not any('_compiled_stream_' in name for name in sys.modules)
            result.update(latest=progress(rt, label='byte-audit', started=started),
                residency=independent_residency(rt), all_original_sources_targets_and_traces_retained=True)
            save()
            tick = time.perf_counter()
            result['independent_bytes'] = verify_bytes(rt, records, oracle)
            result['independent_audit_seconds'] = time.perf_counter()-tick
            result['status'] = 'PASS_OWNED_TRANSITION_COST_A1'
    except Exception as error:
        result.update(status='UNRESOLVED_OWNED_TRANSITION_COST_A1', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-4000:])
        if rt is not None:
            result['latest'] = progress(rt, label='failed-prefix', started=started)
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    save()
    return 0 if result['status'] == 'PASS_OWNED_TRANSITION_COST_A1' else 2


def launch():
    from windows_job_audit_support import run_in_job
    from run_native_text_a1 import publish
    if JOURNAL.exists() or ARTIFACTS.exists():
        raise RuntimeError('original resource diagnosis/artifacts exist; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all diagnosis inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    ARTIFACTS.mkdir(parents=True)
    output = ARTIFACTS/'worker.json'
    journal = dict(status='RUNNING', source_commit=source, host_cap=HOST, deadline_ms=DEADLINE,
        observed_events=EVENTS, expected_optimizer_commits=2, original_training_declaration=1048576,
        protocol='experiments/next_token/OWNED_TRANSITION_COST_A1.md', external_heartbeat=str(output))
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    started = time.perf_counter()
    try:
        run = run_in_job(__file__, ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
        journal.update(job=asdict(run), launcher_seconds=time.perf_counter()-started)
        if output.exists():
            payload = output.read_bytes()
            if len(payload) > 131072:
                raise RuntimeError('unexpected resource-diagnosis receipt size')
            journal['result'] = json.loads(payload)
        result = journal.get('result', {})
        accepted = (run.exit_code == 0 and not run.timed_out and result.get('status') == 'PASS_OWNED_TRANSITION_COST_A1')
        if accepted:
            assert run.attached_before_resume and run.peak_job_commit <= HOST
            for point in ('before', 'after'):
                sample = result[point]
                assert (sample['process_id'], sample['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                assert sample['job_commit_peak'] <= run.peak_job_commit
                assert sample['lifetime_process_commit_peak'] <= run.peak_process_commit
            assert result['completed_targets'] == EVENTS and result['model_score'] is None
            assert (result['latest']['optimizer_steps'], result['latest']['pending_targets']) == (2, 0)
            assert [b['first_target'] for b in result['blocks']] == list(range(0, EVENTS, BLOCK))
            assert all(b['completed'] == BLOCK for b in result['blocks'])
            assert result['residency']['every_role_recomputed_from_complete_leaves_and_actual_buffers']
            assert result['independent_bytes']['images'] > 0 and result['independent_bytes']['records'] > 0
            assert not result['actual_amp_execution'] and result['original_training_declaration'] == 1048576
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()
        journal.update(status='COMPLETE_OWNED_TRANSITION_COST_A1' if accepted else 'UNRESOLVED_OWNED_TRANSITION_COST_A1',
            accepted_execution=accepted, source_unchanged_during_checks=True)
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


def control():
    from audit_token_reporting import report_registration, train
    from audit_shared_token_retention import STORAGE
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.resources import ObjectSpec
    from fp_reference.shared_reference import SharedPlannedObject, ROOT_BYTES
    from probe_native_stream_cost import python_oracle, capture_allocations, verify_bytes
    oracle = python_oracle()
    with capture_allocations() as records:
        cc, program, online, reporting = report_registration(count=4)
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            shared_storage=replace(STORAGE, canonical_image_bytes=64 << 10, token_invariant_bytes=1 << 20))
        train(rt, (0, 1, 1, 0))
        assert rt._candidates[rt._deployed_id].learner.optimizer_steps == 2
        # Toy model values fall below the unchanged 8-KiB image threshold.
        # Add one explicitly paid synthetic retention control to exercise the
        # image oracle, without enlarging the toy learner or issuing authority.
        image_source = bytes(range(256))*41
        rt._allocate(rt._data_owner, (SharedPlannedObject(ObjectSpec('cost-harness:image',
            'image_oracle_control', {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, rt._chi),
            image_source),))
        independent_residency(rt)
        checked = verify_bytes(rt, records, oracle)
        assert checked['images'] > 0
        # A separate audit corruption, after all actual events, establishes
        # that the role scan does not merely repeat the cached answer.
        actual = rt._ledger._leases._version
        total = actual.lookup.total
        bad = total[:2]+(total[2]+1,)+total[3:]
        rt._ledger._leases._version = replace(actual, lookup=replace(actual.lookup, total=bad))
        try:
            independent_residency(rt)
        except AssertionError:
            pass
        else:
            raise AssertionError('independent residency scan trusted a false role total')
        finally:
            rt._ledger._leases._version = actual
    assert 'torch' not in sys.modules
    print(json.dumps(dict(status='PASS_OWNED_TRANSITION_COST_HARNESS_CPU', targets=4, optimizer_commits=2,
        synthetic_image_source_bytes=len(image_source), independent_bytes=checked,
        false_role_augmentation_refused=True), indent=2))


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
