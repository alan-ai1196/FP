"""One fixed actual frozen-reporting attempt, after the live retention unit."""
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

JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_REPORTING_A1.json'
CASES = ('frozen-report', 'forecast-forgery')
CAP, DEADLINE, ARENA = 4 << 30, 180000, 32 << 20


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run required')
    if JOURNAL.exists():
        raise RuntimeError('existing attempt: inspect its terminal result; no replay')
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip())
    retention = common.parent/'evidence/minimal/FP_SHARED_CUDA_RETENTION_A1.json'
    if retention.exists() and json.loads(retention.read_text(encoding='utf-8'))['status'] == 'RUNNING':
        raise RuntimeError('the original shared-retention A1 is still active; preserve its fixed execution first')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit the full execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=CAP, deadline_ms=DEADLINE,
        arena_bytes=ARENA, allocator_reserved_cap=ARENA, whole_board_VRAM_upper=24 << 30,
        scope='owned frozen native/AMP token reporting and altered-forecast refusal; finite toy control, no corpus or language score',
        results=[])
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    for case in CASES:
        journal['active_case'] = case
        publish()
        with tempfile.TemporaryDirectory(prefix='fp-token-reporting-') as temporary:
            output = Path(temporary)/'result.json'
            start = time.perf_counter()
            run = run_in_job(ROOT/'scripts/audit_token_reporting.py', ('--worker', case, '--output', output),
                             commit_limit=CAP, timeout_ms=DEADLINE)
            row = dict(case=case, job=asdict(run), launch_wall_seconds=time.perf_counter()-start)
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                if len(payload) <= 65536:
                    row['result'] = json.loads(payload)
            success = (run.exit_code == 0 and not run.timed_out
                       and row.get('result', {}).get('status') == 'PASS_ACTUAL_FROZEN_TOKEN_REPORTING')
            if success:
                for name in ('before', 'after'):
                    measured = row['result'][name]
                    assert (measured['process_id'], measured['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                    assert measured['lifetime_process_commit_peak'] <= run.peak_process_commit <= CAP
                    assert measured['job_commit_peak'] <= run.peak_job_commit <= CAP
            row['accepted_execution'] = success
            journal['results'].append(row)
            publish()
            print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not success:
                journal['status'] = 'FAILED'
                break
    else:
        journal['status'] = 'COMPLETE_ACTUAL_FROZEN_TOKEN_REPORTING_AUDIT'
    journal.pop('active_case', None)
    publish()
    print('Journal: '+str(JOURNAL), flush=True)


if __name__ == '__main__':
    main()
