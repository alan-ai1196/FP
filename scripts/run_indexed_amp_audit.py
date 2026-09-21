"""Source-bound, bounded owned indexed CUDA attempts; retain every attempt."""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from windows_job_audit_support import run_in_job

CASES = ('profiles', 'large', 'install', 'closure', 'unfunded', 'target-swap', 'second-commit', 'endpoint-binding')
CAP = 4 << 30
DEADLINE = 900000


def git(*arguments):
    return subprocess.run(('git', *arguments), cwd=ROOT, capture_output=True, check=True, encoding='utf-8').stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', type=int, required=True)
    parser.add_argument('--cases', nargs='+', choices=CASES, default=CASES)
    args = parser.parse_args()
    assert args.attempt > 0 and len(set(args.cases)) == len(args.cases)
    output = ROOT/f'evidence/minimal/FP_OWNED_INDEXED_AMP_CUDA_A{args.attempt}.json'
    assert not output.exists(), 'an executed or pending attempt is never overwritten or silently restarted'
    source = git('rev-parse', 'HEAD')
    dependencies = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty', 'evidence/minimal/FP_INDEXED_AMP_SCHEDULE.json')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *dependencies), 'commit all execution inputs first'
    clean()
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': {
        'source': source, 'cases': list(args.cases), 'process_commit_cap': CAP, 'deadline_ms_per_worker': DEADLINE,
        'scope': 'actual owned indexed ReferenceCompilerRuntime/AMP phases, resource and installation boundaries; no model advantage or class-optimality claim',
        'state_atol': '1/100', 'probability_atol': '1/1000', 'normalizer_cap': 18, 'activation_cap': 8,
        'reference_model': 'exact indexed counts and positive partitions',
        'physical_model': 'independent counts, half products, single readout/gradient in owned CUDA arena',
        'old_job_policy': 'all earlier terminal model/component jobs stay terminal'}, 'workers': []}
    def publish():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(output)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-owned-indexed-amp-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    for case in args.cases:
        raw_path = directory/(case+'.json')
        row = {'case': case, 'worker_status': 'FAILED', 'execution_source': source}
        print('START '+case, flush=True)
        try:
            job = run_in_job(str(ROOT/'scripts/audit_indexed_amp.py'), ('--worker', case, '--output', str(raw_path)),
                commit_limit=CAP, timeout_ms=DEADLINE)
            row['completed_job'] = asdict(job)
            if raw_path.exists():
                raw = raw_path.read_bytes()
                row['raw_result_bytes'] = len(raw)
                assert len(raw) <= 65536, 'bounded complete result required'
                row['result'] = json.loads(raw)
            clean()
            if (job.exit_code == 0 and not job.timed_out and job.attached_before_resume
                    and not job.limit_terminated_processes and row['result']['process_id'] == job.process_id
                    and row['result']['status'] in ('PASS_OWNED_INDEXED_CUDA', 'COUNTEREXAMPLE_REPRODUCED')):
                row['worker_status'] = ('COUNTEREXAMPLE_REPRODUCED' if row['result']['status'] == 'COUNTEREXAMPLE_REPRODUCED'
                                        else 'EXECUTED_AND_CHECKED')
        except Exception:
            row['collection_traceback'] = traceback.format_exc()
        report['workers'].append(row)
        publish()
        print(row['worker_status']+' '+case, flush=True)
        if raw_path.exists():
            assert raw_path.resolve().parent == directory
            raw_path.unlink()
    statuses = {r['worker_status'] for r in report['workers']}
    report['status'] = ('COMPLETE_WITH_FAILURE' if 'FAILED' in statuses else
        'COMPLETE_WITH_COUNTEREXAMPLE' if 'COUNTEREXAMPLE_REPRODUCED' in statuses else 'COMPLETE_EXECUTION')
    publish()
    assert directory.parent == ROOT.resolve()
    directory.rmdir()
    print(json.dumps({'status': report['status'], 'cases': list(args.cases)}))
    if report['status'] == 'COMPLETE_WITH_FAILURE':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
