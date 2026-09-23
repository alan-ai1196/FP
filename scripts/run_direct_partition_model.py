"""Two declared n64 direct-partition jobs against retained strong controls."""
from contextlib import ExitStack
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import run_band_model as baseline
import audit_owned_integer_partition_cuda as gate
from fp_reference import ReferenceCompilerRuntime, integer_partition_decoder as direct

model, band, BUDGET = baseline.model, baseline.band, gate.BUDGET
MODE = 'direct-partition'
GATE = 'evidence/minimal/FP_OWNED_INTEGER_PARTITION_CUDA_A1.json'
CPU = 'evidence/minimal/FP_OWNED_INTEGER_PARTITION_CPU.json'
CONTROLS = 'evidence/minimal/FP_BAND_MODEL_A1.json'
PROTOCOL = 'experiments/joint_uncertainty/DIRECT_PARTITION_MODEL_PROTOCOL.md'
DEPENDENCIES = baseline.DEPENDENCIES+(CPU, GATE, CONTROLS, PROTOCOL)


def configuration(case):
    cfg, schema, online, cuda, policy, host = baseline.configuration(case, 'global')
    return (replace(cfg, indexed_histogram=BUDGET), schema, online,
            replace(cuda, histogram=BUDGET), policy, host)


def preflight():
    assert 'torch' not in sys.modules
    cpu = json.loads((ROOT/CPU).read_text(encoding='utf-8'))
    assert cpu['status'] == 'PASS_OWNED_INTEGER_PARTITION_CPU' and cpu['complete_audit']
    component = json.loads((ROOT/GATE).read_text(encoding='utf-8'))
    assert component['status'] == gate.STATUS
    assert tuple(row['case'] for row in component['workers']) == gate.CASES
    assert not model.git('diff', component['execution_source'], '--', 'src/reference_compiler')
    for row in component['workers']:
        job = row['completed_job']
        assert row['worker_status'] == 'PASS' and job['exit_code'] == 0
        assert job['attached_before_resume'] and not job['timed_out'] and not job['limit_terminated_processes']
        assert job['peak_job_commit'] <= job['commit_limit'] == 4 << 30
        assert row['result']['process_id'] == job['process_id'] and row['result']['status'] == gate.STATUS
    retained = json.loads((ROOT/CONTROLS).read_text(encoding='utf-8'))
    reader = baseline.read(ROOT/CONTROLS)
    assert len(reader['workers']) == 6 and all(
        row['status'] == 'PASS_COMPLETE_MODEL_READER' for row in reader['workers'])
    for case, control in zip(band.CASES, baseline.controls()):
        assert json.loads(json.dumps(band.control(case))) == control
        prior, current = baseline.configuration(case, 'global'), configuration(case)
        assert prior[1:3] == current[1:3] and prior[4:] == current[4:]
        assert {k for k in vars(prior[0]) if getattr(prior[0], k) != getattr(current[0], k)} == {'indexed_histogram'}
        assert {k for k in vars(prior[3]) if getattr(prior[3], k) != getattr(current[3], k)} == {
            'histogram', 'backend_id', 'forward_id', 'work_model'}
        assert current[3].forward_id == gate.physical.FORWARD_ID
    return {'status': 'REGISTERED_DIRECT_PARTITION_N64_MODEL', 'cases': band.CASES, 'mode': MODE,
        'component_source': component['execution_source'], 'retained_control_source': retained['execution_source'],
        'retained_control_modes': baseline.MODES, 'retained_control_jobs': 6,
        'component_jobs': len(gate.CASES), 'budget': asdict(BUDGET),
        'all_labels_geometry': band.bounds(64), 'all_forecasts_integer_envelope': 1564,
        'all_forecasts_readout_bit_guard': 7536, 'all_prediction_output_cells': 29,
        'workspace_bytes': direct.workspace_bytes(BUDGET, n=64),
        'host_job_cap': model.CAP, 'deadline_ms': model.DEADLINE, 'packed_bytes': model.PACKED,
        'work_per_role': model.WORK, 'arena_bytes': model.ARENA, 'allocator_cap': 2*model.ARENA,
        'phase_frame_bytes': model.FRAME, 'phase_output_cells': model.CELLS, 'reference_integer_bits': 32768,
        'state_atol': '1/100', 'probability_atol': '1/1000', 'activation_cap': 8, 'normalizer_cap': 18,
        'forward_id': configuration(band.CASES[0])[3].forward_id,
        'evidence_encoding': configuration(band.CASES[0])[3].evidence_encoding,
        'controls': 'same exact joint posterior and retained complete global/projected/carry-free jobs; pair posterior is only an ablation',
        'scope': 'two exposed tapes; paid host integer inference plus half/single readout; no GPU sum-product, blind model selection, throughput, population or complete indexed release claim',
        'failure_policy': 'retain every attempt; no incomplete-prefix scores or cap changes; continue on honest resource/numerical refusal, stop on unexpected execution/audit failure'}


def worker(case):
    roots = []
    def capture(*args, **kwargs):
        rt = ReferenceCompilerRuntime(*args, **kwargs)
        roots.append(rt)
        return rt
    with ExitStack() as stack:
        baseline.adapters(stack)
        stack.enter_context(patch.object(model, 'setup', lambda selected, _: configuration(selected)))
        stack.enter_context(patch.object(model, 'ReferenceCompilerRuntime', capture))
        result = model.worker(case, 'global')
    assert len(roots) == 1
    rt = roots[0]
    snapshot = rt.snapshot()
    key, buffer = next((k, b) for k, b in snapshot.buffers if k.endswith(':histogram-storage'))
    size = direct.workspace_bytes(BUDGET, n=case[0])
    assert len(buffer) == size == snapshot.resources['objects'][key]['residency']['reference_payload_bytes']
    assert result['oracle_assignment_visits'] == 0
    assert result['declared_forward_id'] == configuration(case)[3].forward_id
    assert result['audit']['maximum_histogram_terms'] == 0
    assert result['audit']['maximum_positive_integer_partitions'] <= 2
    assert result['audit']['maximum_phase_output_cells'] <= 29
    if result['status'] == 'COMPLETE_MODEL':
        assert result['audit']['maximum_positive_integer_partitions'] == 2
        assert result['audit']['maximum_phase_output_cells'] == 29
    return {'status': 'EXECUTED_AND_AUDITED', 'case': case, 'mode': MODE, 'process_id': os.getpid(),
        'result': result, 'frame_audit': baseline.frames.frames(rt), 'paid_partition_bytes': size}


def read_worker(actual, case):
    assert actual['case'] == list(case) and actual['mode'] == MODE
    assert actual['paid_partition_bytes'] == direct.workspace_bytes(BUDGET, n=64)
    result = actual['result']
    assert result['declared_forward_id'] == configuration(case)[3].forward_id
    control = next(row for row in baseline.controls() if row['case'] == list(case))
    with ExitStack() as stack:
        baseline.adapters(stack)
        return model.read_result(result, case, 'global', control['scores'])


def read(path):
    report = json.loads(path.read_text(encoding='utf-8'))
    assert report['status'] == 'COMPLETE_WITH_RETAINED_OUTCOMES'
    assert tuple(tuple(row['case']) for row in report['workers']) == band.CASES
    results = []
    for row, case in zip(report['workers'], band.CASES):
        job = row['completed_job']
        if row['worker_status'] == 'RESOURCE_TERMINATED':
            assert job['timed_out'] or job['limit_terminated_processes']
            results.append({'case': case, 'status': 'RESOURCE_TERMINATED', 'scores': 0})
            continue
        actual = row['result']
        assert job['exit_code'] == 0 and not job['timed_out'] and not job['limit_terminated_processes']
        assert job['attached_before_resume'] and job['peak_job_commit'] <= job['commit_limit'] == model.CAP
        assert actual['process_id'] == job['process_id'] and actual['status'] == 'EXECUTED_AND_AUDITED'
        results.append({'case': case, **read_worker(actual, case)})
    return {'status': 'PASS_RETAINED_DIRECT_PARTITION_MODEL_READERS', 'workers': results}


def execute(attempt):
    path = ROOT/f'evidence/minimal/FP_DIRECT_PARTITION_MODEL_A{attempt}.json'
    assert attempt > 0 and not path.exists(), 'retain every attempt'
    source = model.git('rev-parse', 'HEAD')
    def clean():
        assert model.git('rev-parse', 'HEAD') == source
        assert not model.git('status', '--porcelain', '--', *DEPENDENCIES)
    clean()
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'execution_source': source,
              'registration': preflight(), 'workers': []}
    def publish():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(path)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-direct-model-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    stop = False
    for index, case in enumerate(band.CASES):
        output = directory/f'{index}.json'
        row = {'case': case, 'mode': MODE, 'worker_status': 'FAILED'}
        print('START '+str(case)+' '+MODE, flush=True)
        try:
            clean()
            job = baseline.run_in_job(str(Path(__file__).resolve()), ('--worker', index, '--output', output),
                commit_limit=model.CAP, timeout_ms=model.DEADLINE)
            row['completed_job'] = asdict(job)
            if output.exists():
                raw = output.read_bytes()
                assert len(raw) <= 262144
                row['result'] = json.loads(raw)
            report['workers'].append(row)
            publish()
            clean()
            if job.timed_out or job.limit_terminated_processes:
                row['worker_status'] = 'RESOURCE_TERMINATED'
            elif job.exit_code == 0:
                actual = row['result']
                assert actual['status'] == 'EXECUTED_AND_AUDITED' and actual['process_id'] == job.process_id
                assert job['attached_before_resume'] and job['peak_job_commit'] <= model.CAP
                row['reader'] = read_worker(actual, case)
                row['worker_status'] = actual['result']['status']
            else:
                stop = True
        except Exception:
            if not any(item is row for item in report['workers']):
                report['workers'].append(row)
            row['collection_traceback'] = traceback.format_exc()
            stop = True
        publish()
        print(row['worker_status']+' '+str(case), flush=True)
        if output.exists():
            assert output.resolve().parent == directory
            output.unlink()
        if stop:
            break
    report['status'] = 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' if stop else 'COMPLETE_WITH_RETAINED_OUTCOMES'
    publish()
    directory.rmdir()
    if stop:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', type=int, choices=range(len(band.CASES)))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--read', type=Path)
    args = parser.parse_args()
    if args.read:
        print(json.dumps(read(args.read), indent=2))
    elif args.worker is not None:
        assert args.output
        report = {'status': 'FAILED_AUDIT', 'process_id': os.getpid(), 'case': band.CASES[args.worker], 'mode': MODE}
        try:
            report = worker(band.CASES[args.worker])
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        execute(args.attempt)
    else:
        parser.error('select --preflight, --attempt, --read or --worker')
