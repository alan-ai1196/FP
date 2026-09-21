"""One source-bound actual CUDA diagnostic of complete indexed phase maps."""
from dataclasses import asdict
from pathlib import Path
import json
import tempfile
import traceback

from run_radix9_frontier import ROOT, DEPENDENCIES, CAP, git, run_in_job
import indexed_phase_bridge as model

DEADLINE = 600000
REFERENCE = 'evidence/minimal/FP_INDEXED_PHASE_BRIDGE.json'
OUTPUT = ROOT/'evidence/minimal/FP_INDEXED_PHASE_BRIDGE_CUDA.json'


def strip_device_counts(value):
    if type(value) is dict:
        return {k: strip_device_counts(v) for k, v in value.items() if k != 'checked_device_words'}
    if type(value) is list:
        return [strip_device_counts(v) for v in value]
    return value


def main():
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES, REFERENCE), 'commit all execution inputs first'
    clean()
    assert not OUTPUT.exists(), 'retain every attempt; do not silently restart this diagnostic'
    expected = json.loads(git('show', source+':'+REFERENCE))
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'registration': {
        'source': source, 'process_commit_cap': CAP, 'deadline_ms': DEADLINE,
        'scope': 'complete indexed native-reference coordinate/phase component, not an owned Runtime or model stream',
        'device': 'NVIDIA GeForce RTX 3090', 'torch': '2.12.0+cu132', 'CUDA': '13.2',
        'state_native_normalizer_atol': '1/100', 'probability_atol': '1/1000',
        'small_groups': [{'n': 3, 'profiles': 125, 'queries': 9, 'targets': 2},
                         {'n': 5, 'profiles': 81, 'queries': 5, 'targets': 2}],
        'sequential_component_traces': ['nine-event profile/continuation', '100-event late-birth reversal',
                                        'four-event n256 prefix with cursor attachment'],
        'correlated_phase_inputs': {'n': 256, 'query': [0, 96], 'heights': [16, 10**12], 'targets': [0, 1]},
        'synthetic_history_scope': 'large count/clock values are reachable phase inputs, not replayed historical events',
        'boundary_controls': 'CPU exact; self-reported target and nearby-readout adversaries are not main GPU kernel failures',
        'success_criterion': 'every actual word and complete-coordinate decision matches the independent CPU audit; all live component phases pass',
        'old_execution_policy': 'no terminal model or GPU diagnostic is rerun',
        'claimed_timing_or_memory_advantage': False}, 'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-indexed-phase-', dir=ROOT)).resolve()
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
            assert actual['process_id'] == job.process_id and actual['status'] == 'PASS_ACTUAL_COMPACT_PHASES'
            for key in ('small_audit', 'trajectories', 'large_prefix', 'correlated_states', 'gradient_counterexample', 'boundaries', 'scope'):
                assert strip_device_counts(actual[key]) == strip_device_counts(expected[key]), key
            groups = actual['small_audit']+actual['trajectories']+[actual['large_prefix'], actual['correlated_states']]
            assert all(group['checked_device_words'] > 0 for group in groups)
            assert actual['gradient_counterexample']['complete_relation']['status'] == 'OUTSIDE_COMPLETE_REFERENCE_TOLERANCES'
            assert actual['boundaries']['self_reported_target_counterexample']['independent_actual_target_check'] == 'REFUSED'
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
