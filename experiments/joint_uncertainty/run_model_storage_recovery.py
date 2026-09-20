"""One fixed new execution of the first retained n16/c2 memory failure.

No historical result is overwritten and no completed baseline is rerun.
The existing model worker and independent reader keep their full checks.
"""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import tempfile
import traceback

import run_joint as experiment

ROOT = experiment.ROOT
CASE, RATE = (16, 'iid-c2', 16), '1'
OLD_SOURCE = '38b27b300c22aa89ed2c458c4fbf1038a4a6b910'
OLD_JOURNAL = 'evidence/minimal/FP_JOINT_UNCERTAINTY_EXPERIMENT.json'
OUTPUT = ROOT/'evidence/minimal/FP_MODEL_STORAGE_RECOVERY_EXPERIMENT.json'
DEPENDENCIES = experiment.DEPENDENCIES+(
    'experiments/joint_uncertainty/analyze_joint.py',
    'experiments/joint_uncertainty/MODEL_STORAGE_RECOVERY_PROTOCOL.md',
    'experiments/joint_uncertainty/run_model_storage_recovery.py', OLD_JOURNAL)


def prior():
    record = json.loads((ROOT/OLD_JOURNAL).read_text(encoding='utf-8'))
    assert record['registration_source'] == OLD_SOURCE
    failed = [r for r in record['workers'] if r['kind'] == 'FP' and r['case'][0] == 16]
    assert len(failed) == 8 and all(r['worker_status'] == 'FAILED' for r in failed)
    selected = failed[0]
    assert (tuple(selected['case']), selected['rate']) == (CASE, RATE)
    assert 'MemoryError' in selected['traceback'] and 'cuda_storage.py' in selected['traceback']
    posterior, = [r for r in record['workers'] if r['kind'] == 'posterior' and tuple(r['case']) == CASE]
    assert posterior['worker_status'] == 'EXECUTED' and posterior['execution_source'] == OLD_SOURCE
    return {'canonical_path': OLD_JOURNAL,
        'artifact_commit': experiment.git('log', '-1', '--format=%H', '--', OLD_JOURNAL),
        'execution_source': OLD_SOURCE, 'all_original_n16_failures_retained': len(failed),
        'selected_failure': selected,
        'reused_strong_control': {key: posterior[key] for key in (
            'kind', 'case', 'rate', 'execution_source', 'completed_job',
            'adaptive_exact_unseen', 'adaptive_AMP_unseen',
            'adaptive_exact_full_domain', 'adaptive_AMP_full_domain')}}


def preflight():
    cfg, run, policy = experiment.configuration(CASE, RATE)
    cuda = experiment.device_contract()
    unchanged = ('experiments/joint_uncertainty/run_joint.py', 'experiments/joint_uncertainty/joint_model.py')
    assert not experiment.git('diff', OLD_SOURCE, '--', *unchanged)
    assert (experiment.HOST_CAP, experiment.PACKED_CAP, experiment.FRAME,
            experiment.ARENA, experiment.CELLS, experiment.TIMEOUT) == (
                16 << 30, 8 << 30, 2 << 20, 256 << 20, 65536, 7200000)
    assert run.persistence.rules[0].bound == 6
    training = 10*len(experiment.support(CASE))
    assert training == 140
    return {'case': list(CASE), 'rate': RATE, 'new_workers': 1,
        'training_events': training, 'evaluation_events': CASE[0]**2,
        'host_cap': experiment.HOST_CAP, 'packed_cap': experiment.PACKED_CAP,
        'work_cap_per_role': experiment.WORK, 'native_arena_bytes': experiment.ARENA,
        'allocator_cap': 2*experiment.ARENA, 'phase_frame_bytes': experiment.FRAME,
        'phase_output_cells': experiment.CELLS, 'timeout_ms': experiment.TIMEOUT,
        'solver': experiment.SOLVER, 'reference_integer_bits': cfg.reference_integer_bits,
        'data_and_model_worker': 'unchanged existing RN-5 fp_worker, configuration and data',
        'worker_and_data_files_unchanged_from': OLD_SOURCE,
        'independent_reader': 'existing analyze_joint.check_fp from this same source',
        'control': prior(), 'scope': 'one current-source execution recovery; no population or isolated-change claim'}


def clean(source):
    assert experiment.git('rev-parse', 'HEAD') == source
    assert not experiment.git('status', '--porcelain', '--', *DEPENDENCIES)


def save(value):
    OUTPUT.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def execute(source):
    directory = Path(tempfile.mkdtemp(prefix='fp-storage-recovery-', dir=ROOT))
    assert directory.resolve().parent == ROOT.resolve()
    output = directory/'worker.json'
    row = {'kind': 'FP', 'case': list(CASE), 'rate': RATE, 'execution_source': source,
           'worker_status': 'FAILED'}
    try:
        job = experiment.rn1.run_in_job(ROOT/'experiments/joint_uncertainty/run_joint.py',
            ('--worker', 'FP', '--case', *map(str, CASE), '--rate', RATE, '--worker-output', str(output)),
            commit_limit=experiment.HOST_CAP, timeout_ms=experiment.TIMEOUT)
        row['completed_job'] = asdict(job)
        if output.exists():
            with output.open('rb') as stream:
                raw = stream.read(65537)
            assert len(raw) <= 65536, 'bounded worker report exceeds fixed minimal extent'
            row.update(json.loads(raw))
        # The worker has no authority to replace the parent's source or job
        # observation, even if a future report accidentally includes them.
        row.update(execution_source=source, completed_job=asdict(job))
        assert (row['kind'], tuple(row['case']), row['rate']) == ('FP', CASE, RATE)
        if row['worker_status'] == 'EXECUTED':
            assert job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
            assert job.attached_before_resume and max(job.peak_process_commit, job.peak_job_commit) <= experiment.HOST_CAP
            host = row['host']
            assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
            assert host['lifetime_process_commit_peak'] <= job.peak_process_commit
        else:
            row['reason'] = 'failed/missing bounded worker; no model outcome inferred'
    except Exception:
        row['worker_status'] = 'FAILED'
        row['validation_error'] = traceback.format_exc(limit=8)[-5000:]
    finally:
        output.unlink(missing_ok=True)
        directory.rmdir()
    row.update(kind='FP', case=list(CASE), rate=RATE, execution_source=source)
    return row


def read_result(row):
    if row['worker_status'] != 'EXECUTED':
        return {'status': 'FAILED_WORKER_UNSCORED', 'model_score_checks': 0}
    from analyze_joint import check_fp
    hidden, edges, train, evaluation = experiment.data(CASE)
    count, details = check_fp(row, hidden, edges, train, evaluation)
    return {'status': 'SAME_SOURCE_INDEPENDENT_READER_PASS', 'model_score_checks': count,
            'details': details, 'execution_source': row['execution_source']}


def run():
    assert not OUTPUT.exists(), 'retain the existing journal; this protocol has no automatic retry'
    source = experiment.git('rev-parse', 'HEAD')
    clean(source)
    report = {'experiment': 'one-case-n16-model-storage-recovery', 'status': 'RUNNING',
              'registration_source': source, 'registration': preflight(), 'workers': []}
    save(report)
    row = execute(source)
    report['workers'].append(row)
    # Publish even a failed physical attempt before invoking any reader.
    report['status'] = 'WORKER_FINISHED_READER_PENDING'
    save(report)
    try:
        clean(source)
        report['analysis'] = read_result(row)
        report['status'] = 'COMPLETED' if row['worker_status'] == 'EXECUTED' else 'COMPLETED_FAILED_WORKER'
    except Exception:
        report['status'] = 'COMPLETED_READER_FAILURE_UNSCORED'
        report['reader_failure'] = traceback.format_exc(limit=8)[-5000:]
    save(report)
    return {'status': report['status'], 'completed_workers': len(report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--preflight', action='store_true')
    operation.add_argument('--run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(preflight() if args.preflight else run(), indent=2))
