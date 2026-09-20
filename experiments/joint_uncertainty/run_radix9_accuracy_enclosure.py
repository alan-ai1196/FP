"""Source-bound actual AMP tolerance stress; every attempted outcome is kept."""
from dataclasses import asdict
import json
import tempfile
import traceback
from pathlib import Path

from run_radix9_frontier import ROOT, DEPENDENCIES, CAP, DEADLINE, git, run_in_job
import radix9_accuracy_enclosure as model

REFERENCE = 'evidence/minimal/FP_RADIX9_ACCURACY_ENCLOSURE.json'
OUTPUT = ROOT/'evidence/minimal/FP_RADIX9_ACCURACY_CUDA.json'


def main():
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES, REFERENCE), 'commit every execution dependency first'
    clean()
    assert not OUTPUT.exists(), 'retain the previous attempt; no silent restart'
    expected = json.loads(git('show', source+':'+REFERENCE))['stress_cases']
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': {
        'source': source, 'process_commit_cap': CAP, 'deadline_ms': DEADLINE,
        'scope': 'four synthetic count-state forecasts; no trillion-event replay, Runtime bridge or model score',
        'cases': [{'name': name, 'n': n, 'query': query, 'count_magnitudes': hs}
                  for name, n, query, hs in model.stress_cases()],
        'arithmetic': 'actual FP16 products, FP32 alignment/sums; host integer exponents; checked binary64 enclosure',
        'tolerance': str(model.TOLERANCE), 'expected_decisions': ['WITHIN_TOLERANCE']*2+['OUTSIDE_TOLERANCE']*2,
        'success_criterion': 'all words and both accepted/rejected accuracy outcomes reproduce the committed CPU oracle',
        'claimed_timing_comparison': False}, 'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-radix9-accuracy-', dir=ROOT)).resolve()
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
        if job.exit_code == 0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes:
            actual = row['result']
            assert actual['process_id'] == job.process_id
            assert actual['status'] == 'PASS_ACTUAL_AMP_TOLERANCE_DIAGNOSTIC'
            for got, want in zip(actual['stress_cases'], expected, strict=True):
                assert {k:v for k,v in got.items() if k != 'checked_device_words'} == {k:v for k,v in want.items() if k != 'checked_device_words'}
                assert got['checked_device_words'] > 0
            decisions = [f['decision']['status'] for c in actual['stress_cases'] for f in c['forecasts']]
            assert decisions == report['registration']['expected_decisions']
            row['worker_status'] = 'EXECUTED_AND_MATCHED_EXPECTED_DECISIONS'
    except Exception:
        row['collection_traceback'] = traceback.format_exc()
    report['workers'].append(row)
    report['status'] = ('COMPLETE_EXECUTION' if row['worker_status'] == 'EXECUTED_AND_MATCHED_EXPECTED_DECISIONS'
                        else 'COMPLETE_WITH_FAILURE' if 'completed_job' in row else 'FAILED_LAUNCH_OR_COLLECTION')
    publish()
    if output.exists():
        assert output.resolve().parent == directory
        output.unlink()
    directory.rmdir()
    print(json.dumps({'status': report['status'], 'job': row.get('completed_job')}, indent=2))
    if report['status'] != 'COMPLETE_EXECUTION':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
