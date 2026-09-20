"""One fixed, source-bound Windows job for the scaled frontier AMP audit."""
from dataclasses import asdict
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts'), str(Path(__file__).resolve().parent)]
from windows_job_audit_support import run_in_job
import radix9_frontier as model

OUTPUT = ROOT/'evidence/minimal/FP_RADIX9_FRONTIER_CUDA.json'
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty')
REFERENCE = 'evidence/minimal/FP_RADIX9_FRONTIER_EXACT.json'
CAP = 4 << 30
DEADLINE = 240000


def git(*args):
    return subprocess.run(('git', *args), cwd=ROOT, capture_output=True,
                          encoding='utf-8', check=True).stdout.strip()


def main():
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES, REFERENCE), 'commit every execution dependency first'
    clean()
    assert not OUTPUT.exists(), 'retain every previous attempt; this protocol is not silently restarted'
    reference = json.loads(git('show', source+':'+REFERENCE))
    registration = {'source': source, 'scope': 'passive arithmetic experiment, not ReferenceCompilerRuntime or a model stream',
                    'process_commit_cap': CAP, 'deadline_ms': DEADLINE,
                    'cases': [{'name': name, 'n': n, 'query': query, 'count_rows': len(rows)}
                              for name, n, support, query, rows in model.cases()],
                    'exhaustive_triangle': {'profiles': 125, 'ordered_queries': 9},
                    'mantissas': 'FP32 storage, explicit FP16 input casts/products, FP32 alignment/sums/divisions',
                    'exponents': 'guarded host integers; actual GPU normalization predicates determine carries',
                    'alignment_cutoff': model.CUTOFF, 'exponent_cap': model.EXPONENT_CAP,
                    'comparison': 'all floating words against exact RNE machine; outputs against independent integer decoder',
                    'claimed_timing_comparison': False}
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': registration, 'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-radix9-frontier-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    output = directory/'result.json'
    row = {'worker_status': 'FAILED', 'execution_source': source}
    try:
        job = run_in_job(model.__file__, ('--cuda-worker', '--output', str(output)),
                         commit_limit=CAP, timeout_ms=DEADLINE)
        row['completed_job'] = asdict(job)
        if output.exists():
            raw = output.read_bytes()
            row['raw_result_bytes'] = len(raw)
            assert len(raw) < 65536
            row['result'] = json.loads(raw)
        clean()
        if (job.exit_code == 0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes):
            result = row['result']
            assert result['process_id'] == job.process_id and result['status'] == 'PASS_ACTUAL_AMP_ARITHMETIC_ONLY'
            assert len(result['cases']) == len(reference['AMP_exact_machine'])
            for actual, expected in zip(result['cases'], reference['AMP_exact_machine']):
                for key, value in expected.items():
                    if key != 'checked_device_words':
                        assert actual[key] == value, (actual['case'], key)
                assert actual['checked_device_words'] > 0
            for key, value in reference['exhaustive_triangle'].items():
                if key != 'checked_device_words':
                    assert result['exhaustive_triangle'][key] == value, key
            assert result['exhaustive_triangle']['checked_device_words'] > 0
            row['worker_status'] = 'EXECUTED_AND_INDEPENDENTLY_MATCHED'
    except Exception:
        # A collection/reader failure must not erase the already launched attempt.
        row['collection_traceback'] = traceback.format_exc()
    report['workers'].append(row)
    report['status'] = ('COMPLETE_EXECUTION' if row['worker_status'] == 'EXECUTED_AND_INDEPENDENTLY_MATCHED'
                        else 'COMPLETE_WITH_FAILURE' if 'completed_job' in row else 'FAILED_LAUNCH_OR_COLLECTION')
    publish()
    if output.exists():
        assert output.resolve().parent == directory
        output.unlink()
    directory.rmdir()
    completed = row.get('completed_job', {})
    print(json.dumps({'status': report['status'], 'process_id': completed.get('process_id'),
                      'peak_job_commit': completed.get('peak_job_commit')}, indent=2))
    if report['status'] != 'COMPLETE_EXECUTION':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
