"""Single preregistered fresh-arena device attempt. Never replays a journal."""
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

JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_CUDA_OWNER_A1.json'
CASES = ('events-profile', 'cache-forgery', 'source-forgery', 'observation-quota', 'train-prefix8')
CAP, DEADLINE, ARENA = 4 << 30, 180000, 32 << 20


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run required')
    if JOURNAL.exists():
        raise RuntimeError('existing attempt: inspect its outcome; no automatic retry')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=CAP, deadline_ms=DEADLINE,
        arena_bytes=ARENA, allocator_reserved_cap=ARENA, whole_board_VRAM_upper=24 << 30,
        scope='actual Runtime token event/profile phases and refusal controls; no persistence/install or model score', results=[])
    journal['train_prefix_contract'] = dict(host_cap=8 << 30, deadline_ms=900000, arena_bytes=128 << 20,
        allocator_reserved_cap=128 << 20, phase_output_cells=1 << 22, phase_evidence_bytes=64 << 20,
        state_atol='16', probability_atol='1/1000000', observed_events=8, update_unit=512)
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    for case in CASES:
        journal['active_case'] = case
        publish()
        with tempfile.TemporaryDirectory(prefix='fp-token-owner-') as temporary:
            output = Path(temporary)/'result.json'
            start = time.perf_counter()
            cap, deadline = (8 << 30, 900000) if case == 'train-prefix8' else (CAP, DEADLINE)
            run = run_in_job(ROOT/'scripts/audit_token_cuda_owner.py', ('--worker', case, '--output', output),
                             commit_limit=cap, timeout_ms=deadline)
            row = dict(case=case, job=asdict(run), launch_wall_seconds=time.perf_counter()-start)
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                if len(payload) <= 65536:
                    row['result'] = json.loads(payload)
            success = (run.exit_code == 0 and not run.timed_out
                       and row.get('result', {}).get('status') == 'PASS_ACTUAL_TOKEN_RUNTIME_OWNER')
            if success:
                for name in ('before', 'after'):
                    observed = row['result'][name]
                    assert (observed['process_id'], observed['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak'] <= run.peak_process_commit <= cap
                    assert observed['job_commit_peak'] <= run.peak_job_commit <= cap
            row['accepted_execution'] = success
            journal['results'].append(row)
            publish()
            print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not success:
                journal['status'] = 'FAILED'
                break
    else:
        journal['status'] = 'COMPLETE_ACTUAL_TOKEN_RUNTIME_OWNER_AUDIT'
    journal.pop('active_case', None)
    publish()
    print('Journal: '+str(JOURNAL), flush=True)


if __name__ == '__main__':
    main()
