"""Fixed-source CPU qualification of captured native prediction values.

Complete relevant Runtime, ownership, storage, reporting, persistence and
installation audits. No original experiment is replayed, and this does not
reissue the historical whole release or supply CUDA/performance authority.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import subprocess
import sys
import tempfile

from audit_public_value_regression import AUDITS as PUBLIC_AUDITS, git

ROOT = Path(__file__).resolve().parents[1]
AUDITS = PUBLIC_AUDITS+('canonical_images', 'compositional_reference', 'phase_encoding',
    'token_base_facts', 'reference_run', 'owned_token_workspaces', 'captured_token_values',
    'captured_value_boundaries', 'native_prediction_liveness')
EVIDENCE = ROOT/'evidence/minimal/FP_CAPTURED_VALUES_REGRESSION_CPU.json'


def run(name):
    with tempfile.TemporaryDirectory(prefix='fp-captured-audit-') as temporary:
        command = [sys.executable, '-B', str(ROOT/'scripts'/('audit_'+name+'.py'))]
        if name == 'phase_encoding':
            # This older script normally selects a historical receipt itself.
            # Keep the new reproduction separate from that original artifact.
            command += ['--output', str(Path(temporary)/'phase.json')]
        completed = subprocess.run(command, cwd=ROOT, text=True, encoding='utf-8',
            capture_output=True, timeout=1200)
        if completed.returncode:
            raise RuntimeError(name+': '+completed.stdout[-1000:]+completed.stderr[-4000:])
        lines = completed.stdout.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith('{'))
        result = json.loads('\n'.join(lines[start:]))
        if not result.get('status', '').startswith('PASS'):
            raise RuntimeError(name+': missing terminal PASS')
        row = dict(status=result['status'], scope=result.get('scope'), complete_script=True)
        if name == 'host_allocation_failure':
            # This is a new actual OS refusal control, not a reused old receipt.
            row['actual_windows_refusal'] = result['os']
        return row


def main():
    if not __debug__ or sys.flags.optimize:
        raise RuntimeError('the correctness checks require assertions')
    if EVIDENCE.exists():
        raise RuntimeError('qualification receipt exists; do not overwrite it')
    source = git('rev-parse', 'HEAD')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('commit all qualification inputs first')
    results, failures = {}, {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(run, name): name for name in AUDITS}
        for job in as_completed(pending):
            name = pending[job]
            try:
                results[name] = job.result()
                print('PASS '+name, flush=True)
            except Exception as error:
                failures[name] = type(error).__name__+': '+str(error)
                print('FAILED '+name, flush=True)
    if git('rev-parse', 'HEAD') != source or git('status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('source changed during qualification')
    result = dict(status='FAILED_CAPTURED_VALUES_REGRESSION_CPU' if failures else 'PASS_CAPTURED_VALUES_REGRESSION_CPU',
        source_commit=source, scope=__doc__.strip(), audit_count=len(results),
        audits={name: results[name] for name in AUDITS if name in results}, failures=failures,
        actual_cuda_execution=False, source_unchanged_during_checks=True)
    with EVIDENCE.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(result['status'], flush=True)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
