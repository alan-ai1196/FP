"""One preregistered owned storage attempt; existing journals are terminal."""
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

JOURNAL = ROOT/'evidence/minimal/FP_SHARED_CUDA_RETENTION_A1.json'
CASES = ('profile-and-retention-fault', 'full-unit512')
CONTRACTS = {
    'profile-and-retention-fault': dict(host_cap=4 << 30, deadline_ms=180000, arena_bytes=32 << 20,
        phase_evidence_bytes=1 << 20, state_atol='1/4', probability_atol='1/10000'),
    'full-unit512': dict(host_cap=16 << 30, deadline_ms=14400000, arena_bytes=1 << 30,
        phase_evidence_bytes=64 << 20, state_atol='16', probability_atol='1/1000000',
        reference_payload_cap=2 << 30, phase_output_cells=1 << 22, observed_events=512, update_unit=512)
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run required')
    if JOURNAL.exists():
        raise RuntimeError('existing attempt must be inspected, never replayed')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit every execution input before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, contracts=CONTRACTS,
        whole_board_VRAM_upper=24 << 30, results=[],
        scope='actual lossless full-frame retention, post-target refusal, and complete full-vocabulary owned unit; no language score or installation')
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    for case in CASES:
        cfg = CONTRACTS[case]
        journal['active_case'] = case
        with tempfile.TemporaryDirectory(prefix='fp-shared-frame-') as temporary:
            output, progress = Path(temporary)/'result.json', Path(temporary)/'progress.json'
            journal['active_progress_path'] = str(progress)
            publish()
            started = time.perf_counter()
            job = run_in_job(ROOT/'scripts/audit_shared_cuda_retention.py',
                ('--worker', case, '--output', output, '--progress', progress),
                commit_limit=cfg['host_cap'], timeout_ms=cfg['deadline_ms'])
            row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            for name, path in (('result', output), ('last_progress', progress)):
                if path.exists():
                    with path.open('rb') as stream:
                        body = stream.read(65537)
                    if len(body) <= 65536:
                        row[name] = json.loads(body)
            passed = (job.exit_code == 0 and not job.timed_out
                and row.get('result', {}).get('status') == 'PASS_ACTUAL_SHARED_TOKEN_RETENTION')
            if passed:
                for name in ('before', 'after'):
                    observed = row['result'][name]
                    assert (observed['process_id'], observed['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak'] <= job.peak_process_commit <= cfg['host_cap']
                    assert observed['job_commit_peak'] <= job.peak_job_commit <= cfg['host_cap']
                arena = row['result']['outcome']['arena']
                assert arena['native_allocation_counter'] == arena['current_allocation_counter'] == [1, cfg['arena_bytes'], 1]
                assert arena['consumed_bytes'] <= cfg['arena_bytes']
                assert all(arena[key] == cfg['arena_bytes'] for key in (
                    'actual_tensor_arena_bytes', 'actual_allocator_reserved_bytes',
                    'lifetime_tensor_peak_bytes', 'lifetime_allocator_reserved_peak_bytes'))
            row['accepted_execution'] = passed
            journal['results'].append(row)
            publish()
            print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not passed:
                journal['status'] = 'FAILED'
                break
    else:
        journal['status'] = 'COMPLETE_ACTUAL_SHARED_TOKEN_RETENTION_AUDIT'
    journal.pop('active_case', None)
    journal.pop('active_progress_path', None)
    publish()
    print('Journal: '+str(JOURNAL), flush=True)


if __name__ == '__main__':
    main()
