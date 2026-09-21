"""Retained full native regressions after the prepaid readback tariff increase.

Uses each existing complete battery and the strict release report parser.
This is a targeted regression campaign, not a new complete target release.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_cuda_release import run_cuda_audit


def git(*arguments):
    return subprocess.check_output(('git', *arguments), cwd=ROOT, encoding='utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', type=int, required=True)
    parser.add_argument('--cases', nargs='+', choices=('cuda_installation', 'cuda_policy_run'),
                        default=('cuda_installation', 'cuda_policy_run'))
    args = parser.parse_args()
    assert args.attempt > 0 and len(set(args.cases)) == len(args.cases)
    path = ROOT/f'evidence/minimal/FP_CUDA_READBACK_REGRESSIONS_A{args.attempt}.json'
    assert not path.exists(), 'terminal or pending attempts are never overwritten'
    source = git('rev-parse', 'HEAD')
    dependencies = ('src/reference_compiler', 'scripts')
    def clean():
        # Unrelated theory/docs may advance while these unchanged batteries run.
        assert not git('diff', source, '--', *dependencies)
        assert not git('ls-files', '--others', '--exclude-standard', '--', *dependencies)
    clean()
    cells = 4096
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': {
        'source': source, 'cases': list(args.cases), 'tariff_change_source': '56dfea0',
        'prepaid_output_cells': cells, 'old_per_cell_work': 128, 'current_per_cell_work': 320,
        'additional_work_per_native_phase': (320-128)*cells,
        'additional_initial_readout_work': 8*cells,
        'installation_work_budget': {'old': 4_000_000_000, 'current': 12_000_000_000},
        'policy_work_budget': {'old': 20_000_000_000, 'current': 60_000_000_000},
        'scope': 'complete unchanged native decision classes, trajectories and failure controls with explicitly funded current work tariffs; no complete release',
        'enforcement': 'existing complete battery process/job protocols; strict full-section and counter validation; 7200-second battery deadline',
        'earlier_failure': 'FP_INDEXED_AMP_CUDA_REGRESSIONS.json'}, 'audits': {}}
    def publish():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(path)
    publish()
    for case in args.cases:
        try:
            clean()
            result = run_cuda_audit(ROOT, case)
            clean()
            report['audits'][case] = result
        except Exception as error:
            report['audits'][case] = {'status': 'FAILED', 'failure': str(error)[-8192:]}
        publish()
    report['status'] = ('COMPLETE_EXECUTION' if all(row['status'] == 'PASS' for row in report['audits'].values())
                        else 'COMPLETE_WITH_FAILURE')
    publish()
    print(report['status'])
    if report['status'] != 'COMPLETE_EXECUTION':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
