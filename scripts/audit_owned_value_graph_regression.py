"""Fixed-source CPU regression for complete owned typed-value graph retention."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import sys

from audit_public_value_regression import AUDITS as PUBLIC_AUDITS, git
from audit_captured_values_regression import run

ROOT = Path(__file__).resolve().parents[1]
AUDITS = PUBLIC_AUDITS+('token_base_facts', 'reference_run', 'captured_value_boundaries',
    'compositional_reference', 'owned_value_graph_runtime')
EVIDENCE = ROOT/'evidence/minimal/FP_OWNED_VALUE_GRAPH_REGRESSION_CPU.json'


def main():
    if not __debug__ or sys.flags.optimize:
        raise RuntimeError('assertions are required')
    if EVIDENCE.exists():
        raise RuntimeError('original qualification receipt exists; never overwrite')
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
    result = dict(status='FAILED_OWNED_VALUE_GRAPH_REGRESSION_CPU' if failures else 'PASS_OWNED_VALUE_GRAPH_REGRESSION_CPU',
        source_commit=source, scope=__doc__.strip(), audit_count=len(results),
        audits={name: results[name] for name in AUDITS if name in results}, failures=failures,
        actual_cuda_execution=False, source_unchanged_during_checks=True)
    with EVIDENCE.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(result['status'], flush=True)
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
