"""One full owned unit with the integrated writer and unchanged A1 limits."""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from windows_job_audit_support import run_in_job
from run_shared_cuda_retention_audit import CONTRACTS

CASE = 'full-unit512'
CONTRACT = dict(CONTRACTS[CASE])
JOURNAL = ROOT/'evidence/minimal/FP_SHARED_CUDA_RETENTION_A2.json'


def accept(row):
    job, result = row['job'], row.get('result', {})
    if (job['exit_code'] != 0 or job['timed_out']
            or result.get('status') != 'PASS_ACTUAL_SHARED_TOKEN_RETENTION'):
        return False
    assert result['case'] == CASE
    assert job['attached_before_resume'] is True
    for name in ('before', 'after'):
        measured = result[name]
        assert (measured['process_id'], measured['creation_100ns']) == (
            job['process_id'], job['process_creation_100ns'])
        assert measured['lifetime_process_commit_peak'] <= job['peak_process_commit'] <= CONTRACT['host_cap']
        assert measured['job_commit_peak'] <= job['peak_job_commit'] <= CONTRACT['host_cap']
    outcome = result['outcome']
    assert (outcome['ordinary_targets'], outcome['candidate_observations'],
            outcome['profile_events'], outcome['checked_cuda_phases']) == (512, 512, 0, 1026)
    assert (outcome['vocabulary'], outcome['context'], outcome['master_coordinates']) == (50257, 512, 603092)
    assert (outcome['committed_units'], outcome['pending_count']) == (1, 0)
    assert outcome['all_original_unit_records_retained'] is True
    assert outcome['state_atol'] == CONTRACT['state_atol']
    assert outcome['probability_atol'] == CONTRACT['probability_atol']
    assert outcome['paid_reference_peak'] <= CONTRACT['reference_payload_cap']
    arena = outcome['arena']
    size = CONTRACT['arena_bytes']
    assert arena['native_allocation_counter'] == arena['current_allocation_counter'] == [1, size, 1]
    assert arena['consumed_bytes'] <= size
    assert all(arena[key] == size for key in (
        'actual_tensor_arena_bytes', 'actual_allocator_reserved_bytes',
        'lifetime_tensor_peak_bytes', 'lifetime_allocator_reserved_peak_bytes'))
    return True


def main():
    if sys.flags.optimize:
        raise RuntimeError('this audited execution requires Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run required')
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute',
        '--git-common-dir'], cwd=ROOT, text=True).strip())
    if ROOT.resolve() != common.parent.resolve():
        raise RuntimeError('launch this single attempt only from the canonical worktree')
    if JOURNAL.exists():
        raise RuntimeError('existing A2 journal: inspect its actual process/result; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit every execution input before launch')
    prior_path = ROOT/'evidence/minimal/FP_SHARED_CUDA_RETENTION_A1.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    full = next(row for row in prior['results'] if row['case'] == CASE)
    if (prior['status'] != 'FAILED' or prior['contracts'][CASE] != CONTRACT
            or full['accepted_execution'] or not full['job']['timed_out']):
        raise RuntimeError('this attempt requires the original terminal timeout and unchanged caps')
    reporting = json.loads((ROOT/'evidence/minimal/FP_TOKEN_REPORTING_A1.json').read_text(encoding='utf-8'))
    if reporting['status'] != 'COMPLETE_ACTUAL_FROZEN_TOKEN_REPORTING_AUDIT':
        raise RuntimeError('the fixed reporting boundary must be terminal and successful first')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=(CASE,), contracts={CASE: CONTRACT},
        whole_board_VRAM_upper=24 << 30, results=[],
        prior_journal=prior_path.name, prior_source_commit=prior['source_commit'],
        scope='one full owned token unit after byte-preserving writer integration; unchanged A1 model/caps/tolerances; no language score or isolated-speedup claim')

    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')

    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-shared-frame-a2-') as temporary:
            output, progress = Path(temporary)/'result.json', Path(temporary)/'progress.json'
            journal.update(active_case=CASE, active_progress_path=str(progress))
            publish()
            started = time.perf_counter()
            job = run_in_job(ROOT/'scripts/audit_shared_cuda_retention.py',
                ('--worker', CASE, '--output', output, '--progress', progress),
                commit_limit=CONTRACT['host_cap'], timeout_ms=CONTRACT['deadline_ms'])
            row = dict(case=CASE, job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            for name, path in (('result', output), ('last_progress', progress)):
                if path.exists():
                    with path.open('rb') as stream:
                        body = stream.read(65537)
                    try:
                        if len(body) > 65536:
                            raise ValueError('bounded result extent exceeded')
                        row[name] = json.loads(body)
                    except (ValueError, UnicodeError) as error:
                        row[name+'_read_error'] = f'{type(error).__name__}: {error}'
            try:
                passed = accept(row)
            except Exception as error:
                passed = False
                row['acceptance_error'] = f'{type(error).__name__}: {error}'
            row['accepted_execution'] = passed
            journal['results'].append(row)
            journal['status'] = 'COMPLETE_ACTUAL_SHARED_TOKEN_RETENTION_A2' if passed else 'FAILED'
    except Exception as error:
        journal['status'] = 'LAUNCHER_FAILED'
        journal['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        journal.pop('active_case', None)
        journal.pop('active_progress_path', None)
        publish()
    print(CASE+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
    print('Journal: '+str(JOURNAL), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
