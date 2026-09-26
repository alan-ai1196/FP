"""One bounded, preregistered full-vocabulary token prediction comparison."""
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

JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_READOUT_CUDA_A1.json'
CAP, DEADLINE = 4 << 30, 900000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run is required')
    if JOURNAL.exists():
        raise RuntimeError('existing attempt; inspect its terminal result instead of replaying it')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, host_cap=CAP, deadline_ms=DEADLINE,
        whole_board_VRAM_upper=24 << 30, allocator_cap=512 << 20,
        scope='complete finite prediction relation; no owned event/state bridge or model claim')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='fp-token-readout-') as temporary:
        output = Path(temporary)/'result.json'
        start = time.perf_counter()
        run = run_in_job(ROOT/'scripts/audit_token_readout_cuda.py', ('--output', output),
            commit_limit=CAP, timeout_ms=DEADLINE)
        journal.update(job=asdict(run), launch_wall_seconds=time.perf_counter()-start)
        if output.exists():
            with output.open('rb') as stream:
                payload = stream.read(65537)
            if len(payload) <= 65536:
                journal['result'] = json.loads(payload)
        result = journal.get('result', {})
        success = (run.exit_code == 0 and not run.timed_out
                   and result.get('status') == 'PASS_ACTUAL_COMPLETE_TOKEN_PREDICTION_RELATION')
        if success:
            for name in ('before', 'after'):
                observed = result[name]
                assert (observed['process_id'], observed['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                assert observed['lifetime_process_commit_peak'] <= run.peak_process_commit <= CAP
                assert observed['job_commit_peak'] <= run.peak_job_commit <= CAP
        journal['accepted_execution'] = success
        journal['status'] = 'COMPLETE_PREDICTION_RELATION_AUDIT' if success else 'FAILED'
    JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(journal, indent=2))


if __name__ == '__main__':
    main()
