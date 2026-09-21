"""One fixed source-bound actual mixed-precision power-lowering diagnostic."""
from dataclasses import asdict
import json
import tempfile
import traceback
from pathlib import Path

from run_radix9_frontier import ROOT, DEPENDENCIES, CAP, DEADLINE, git, run_in_job
import radix9_power_lowering as model

REFERENCE = 'evidence/minimal/FP_RADIX9_POWER_LOWERING.json'
RETAINED = ('evidence/minimal/FP_RADIX9_ACCURACY_ENCLOSURE.json',
            'evidence/minimal/FP_RADIX9_ACCURACY_CUDA.json')
OUTPUT = ROOT/'evidence/minimal/FP_RADIX9_POWER_LOWERING_CUDA.json'


def main():
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES, REFERENCE, *RETAINED), 'commit all execution inputs first'
    clean()
    assert not OUTPUT.exists(), 'retain every attempt; no silent restart'
    expected = json.loads(git('show', source+':'+REFERENCE))
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': {
        'source': source, 'process_commit_cap': CAP, 'deadline_ms': DEADLINE,
        'scope': 'static power lowering of a passive count decoder, not a Runtime or model stream',
        'small_groups': [{'n': 3, 'profiles': 125, 'queries': 9}, {'n': 5, 'profiles': 81, 'queries': 5}],
        'stress_cases': [{'name': name, 'n': n, 'query': query, 'count_magnitudes': hs}
                         for name, n, query, hs in model.stress_cases()],
        'arithmetic': 'proved power products alias mantissas and add host exponents; remaining products FP16; sums FP32',
        'success_criterion': 'all actual words and reference decisions match; all five stress forecasts within1/1000',
        'uniform_scope': 'the H/S error bound and fixed tape, not all cycles or all decoders',
        'old_execution_policy': 'read retained terminal controls; do not rerun them',
        'claimed_timing_or_memory_advantage': False}, 'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-radix9-power-', dir=ROOT)).resolve()
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
            assert actual['process_id'] == job.process_id and actual['status'] == 'PASS_ACTUAL_MIXED_POWER_LOWERING'
            for key in ('small_audit', 'stress_cases'):
                for got, want in zip(actual[key], expected[key], strict=True):
                    assert {k:v for k,v in got.items() if k != 'checked_device_words'} == {k:v for k,v in want.items() if k != 'checked_device_words'}
                    assert got['checked_device_words'] > 0
            assert all(f['decision']['status'] == 'WITHIN_TOLERANCE' for c in actual['stress_cases'] for f in c['forecasts'])
            row['worker_status'] = 'EXECUTED_AND_INDEPENDENTLY_MATCHED'
    except Exception:
        row['collection_traceback'] = traceback.format_exc()
    report['workers'].append(row)
    report['status'] = ('COMPLETE_EXECUTION' if row['worker_status'] == 'EXECUTED_AND_INDEPENDENTLY_MATCHED'
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
