"""Fixed-source CPU regression of the repaired public value boundary.

This executes complete existing audit scripts plus the new attacks. It is not
a replacement for the historical release driver, an actual CUDA run, a resource
benchmark or an assertion that every FP registration has been enumerated.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDITS = (
    'cpu_installation', 'reference_search', 'owned_token_reuse', 'owned_token_learner',
    'token_cuda_owner', 'reference_events', 'reference_profiles', 'paired_cpu_persistence',
    'shared_token_retention', 'reference_construction', 'token_reporting',
    'context_ingress', 'host_allocation_failure', 'shared_cuda_retention',
    'public_value_boundary', 'native_text_reporting')
EVIDENCE = ROOT/'evidence/minimal/FP_PUBLIC_VALUE_REGRESSION_CPU.json'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def run(name):
    completed = subprocess.run([sys.executable, '-B', str(ROOT/'scripts'/('audit_'+name+'.py'))],
        cwd=ROOT, text=True, encoding='utf-8', capture_output=True, timeout=1200)
    if completed.returncode:
        raise RuntimeError(name+': '+completed.stdout[-1000:]+completed.stderr[-4000:])
    # Some established audits emit a few progress lines before their final JSON.
    lines = completed.stdout.splitlines()
    start = next(i for i, line in enumerate(lines) if line == '{')
    result = json.loads('\n'.join(lines[start:]))
    if not result.get('status', '').startswith('PASS'):
        raise RuntimeError(name+': missing terminal PASS')
    return dict(status=result['status'], scope=result.get('scope'), complete_script=True)


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
    result = dict(status='FAILED_PUBLIC_VALUE_REGRESSION_CPU' if failures else 'PASS_PUBLIC_VALUE_REGRESSION_CPU',
        source_commit=source, scope=__doc__.strip(), audit_count=len(results),
        audits={name: results[name] for name in AUDITS if name in results}, failures=failures,
        actual_cuda_execution=False, source_unchanged_during_checks=True)
    EVIDENCE.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(result['status'], flush=True)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
