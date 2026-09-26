"""Single registered actual-device attempt; no replay of existing journals."""
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

JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_AMP_CUDA_A1.json'
CASES = ('small-exact', 'train-context512')
CAP, DEADLINE = 4 << 30, 900000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run is required')
    if JOURNAL.exists():
        raise RuntimeError('existing attempt; inspect its actual state instead of replaying it')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=list(CASES), host_cap=CAP, deadline_ms=DEADLINE,
        whole_board_VRAM_upper=24 << 30, allocator_cap=512 << 20,
        scope='actual finite numerical schedule audit; no Runtime, issued bridge, install or model claim', results=[])
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    for case in CASES:
        journal['active_case'] = case
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='fp-token-amp-') as temporary:
            output = Path(temporary)/'result.json'
            start = time.perf_counter()
            run = run_in_job(ROOT/'scripts/audit_token_amp_schedule.py', ('--worker', case, '--output', output),
                commit_limit=CAP, timeout_ms=DEADLINE)
            row = dict(case=case, job=asdict(run), launch_wall_seconds=time.perf_counter()-start)
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                if len(payload) <= 65536:
                    row['result'] = json.loads(payload)
            success = run.exit_code == 0 and not run.timed_out and 'result' in row
            if success:
                for name in ('before', 'after'):
                    observed = row['result'][name]
                    assert (observed['process_id'], observed['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak'] <= run.peak_process_commit <= CAP
                    assert observed['job_commit_peak'] <= run.peak_job_commit <= CAP
            row['accepted_execution'] = success
            journal['results'].append(row)
            JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
            print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not success:
                journal['status'] = 'FAILED'
                break
    else:
        journal['status'] = 'COMPLETE_PHYSICAL_SCHEDULE_AUDIT'
    journal.pop('active_case', None)
    JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(journal, indent=2))


if __name__ == '__main__':
    main()
