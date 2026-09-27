"""Two fixed token reuse jobs, only after shared-retention A2 terminates."""
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
from audit_token_reuse_cuda import CASES, HOST, ARENA, RESERVED, DEADLINE

JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_REUSE_CUDA_A1.json'


def accept(row):
    job, result = row['job'], row.get('result', {})
    if job['exit_code'] or job['timed_out'] or result.get('status') != 'PASS_ACTUAL_OWNED_TOKEN_REUSE':
        return False
    assert result['case'] == row['case'] and job['attached_before_resume']
    for name in ('before', 'after'):
        measured = result[name]
        assert (measured['process_id'], measured['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
        assert measured['lifetime_process_commit_peak'] <= job['peak_process_commit'] <= HOST
        assert measured['job_commit_peak'] <= job['peak_job_commit'] <= HOST
    outcome, arena = result['outcome'], result['outcome']['arena']
    assert outcome['owned_reference_peak'] <= 256 << 20
    assert outcome['historical_view_refused'] and outcome['addresses_reused'] and outcome['frozen_current_preserved']
    assert arena['native_allocation_counter'] == arena['current_allocation_counter'] == [1, ARENA, 1]
    assert arena['actual_tensor_arena_bytes'] == arena['lifetime_tensor_peak_bytes'] == ARENA
    assert arena['actual_allocator_reserved_bytes'] == arena['lifetime_allocator_reserved_peak_bytes'] == RESERVED
    assert arena['peak_live_reserved_bytes'] <= ARENA < arena['cumulative_reserved_bytes']
    assert arena['retired_generations'] > 0
    expected = (16, 8, 2, 45, 45) if row['case'] == CASES[0] else (2, 1, 0, 8, 7)
    assert tuple(outcome[k] for k in ('training_events', 'complete_training_units', 'report_events',
        'retained_phases', 'checked_phases')) == expected
    assert outcome['retained_header_records'] == expected[3]
    assert outcome['checked_array_words'] == (19164 if row['case'] == CASES[0] else 3351)
    if row['case'] == CASES[0]:
        assert outcome['public_snapshot_writes_refused'] == 2 and outcome['saved_view_extent_reused']
    else:
        assert outcome['failed_phase_pins'] > 0 and outcome['unsealed_header_retained']
        assert outcome['no_successor_published'] and outcome['revealed_failed_target'] == 1
    return True


def main():
    if sys.flags.optimize:
        raise RuntimeError('qualification requires Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run required')
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip())
    if ROOT.resolve() != common.parent.resolve():
        raise RuntimeError('launch only from the canonical worktree after integration')
    if JOURNAL.exists():
        raise RuntimeError('existing reuse journal: inspect the result; never replay')
    prior = json.loads((ROOT/'evidence/minimal/FP_SHARED_CUDA_RETENTION_A2.json').read_text(encoding='utf-8'))
    if (prior['status'] not in ('FAILED', 'COMPLETE_ACTUAL_SHARED_TOKEN_RETENTION_A2')
            or len(prior['results']) != 1 or 'active_case' in prior
            or type(prior['results'][0].get('job', {}).get('exit_code')) is not int):
        raise RuntimeError('preserve the original A2 until its actual job is terminal')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs and the original A2 result before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=HOST,
        deadline_ms=DEADLINE, arena_bytes=ARENA, allocator_reserved_cap=RESERVED,
        phase_evidence_bytes=1 << 20, phase_output_cells=4096, exact_rounding_cells=4096,
        reference_payload_cap=256 << 20, work_per_role=10**15, state_atol='1/4', probability_atol='1/10000',
        whole_board_VRAM_upper=24 << 30, prior_a2_source=prior['source_commit'],
        scope='finite owned token reuse, actual stale-generation and unsealed-retention controls; no corpus/full-V fit/model score',
        results=[])
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for case in CASES:
            journal['active_case'] = case
            publish()
            with tempfile.TemporaryDirectory(prefix='fp-token-reuse-') as temporary:
                output = Path(temporary)/'result.json'
                start = time.perf_counter()
                job = run_in_job(ROOT/'scripts/audit_token_reuse_cuda.py',
                    ('--worker', case, '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
                row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-start)
                if output.exists():
                    with output.open('rb') as stream:
                        payload = stream.read(65537)
                    try:
                        if len(payload) > 65536:
                            raise ValueError('bounded result extent exceeded')
                        row['result'] = json.loads(payload)
                    except (ValueError, UnicodeError) as error:
                        row['result_read_error'] = f'{type(error).__name__}: {error}'
                try:
                    passed = accept(row)
                except Exception as error:
                    passed = False
                    row['acceptance_error'] = f'{type(error).__name__}: {error}'
                row['accepted_execution'] = passed
                journal['results'].append(row)
                publish()
                print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
                if not passed:
                    journal['status'] = 'FAILED'
                    break
        else:
            journal['status'] = 'COMPLETE_ACTUAL_OWNED_TOKEN_REUSE_A1'
    except Exception as error:
        journal.update(status='LAUNCHER_FAILED', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        journal.pop('active_case', None)
        publish()
    return 0 if journal['status'] == 'COMPLETE_ACTUAL_OWNED_TOKEN_REUSE_A1' else 1


if __name__ == '__main__':
    raise SystemExit(main())
