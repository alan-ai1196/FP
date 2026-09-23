"""Six registered n64 learning jobs with exact and existing AMP controls."""
from contextlib import ExitStack
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import CudaCompilerPolicy, ReferenceCompilerRuntime, phase_deflate
from fp_reference import indexed_amp as amp, projected_amp, packed_histogram_amp as packed_amp
from fp_reference import packed_histogram_decoder as packed
from fp_reference.cuda_prefix import IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.indexed_count import CountState
from audit_indexed_runtime import fixture
from windows_job_audit_support import run_in_job
import band_model as band
import run_indexed_model as model
import run_phase_encoding as frames
from audit_owned_packed_histogram_cuda import CASES as GATE_CASES

MODES = ('global', 'projected', 'carry-free')
BUDGET = packed.PackedHistogramAllowance(live_cells=1024, arithmetic=16384)
GATE_SOURCE = 'd600dba80a60c05909feca4106bc285aef311472'
CONTROL = 'evidence/minimal/FP_BAND_MODEL_CONTROL.json'
DEPENDENCIES = model.DEPENDENCIES+(CONTROL,
    'experiments/joint_uncertainty/BAND_MODEL_PROTOCOL.md', 'theory/proofs/BAND_MODEL_RESOURCE_BOUND.md')


def controls():
    result = json.loads((ROOT/CONTROL).read_text(encoding='utf-8'))
    assert result['status'] == 'PASS_BAND_MODEL_EXACT_CONTROL_AND_GEOMETRY'
    assert tuple(tuple(row['case']) for row in result['controls']) == band.CASES
    return result['controls']


def configuration(case, mode):
    assert case in band.CASES and mode in MODES
    hidden, edges, train, evaluation = band.data(case)
    cfg, schema, online = fixture(case[0], len(train)+len(evaluation), byte_cap=model.PACKED, work_cap=model.WORK)
    cfg = replace(cfg, normalizer_cap=F(18), indexed_histogram=BUDGET if mode == 'carry-free' else None)
    storage = CudaStorageContract(model.ARENA, 2*model.ARENA,
        {role: (model.ARENA, 2*model.ARENA) for role in ('deployment', 'compiler')})
    kind = ProjectedIndexedCudaPrefixContract if mode == 'projected' else IndexedCudaPrefixContract
    cuda = kind(storage, F(1, 100), F(1, 1000), n=case[0],
        phase_output_cells=model.CELLS, phase_evidence_bytes=model.FRAME,
        evidence_encoding=phase_deflate.ENCODING_ID, histogram=cfg.indexed_histogram)
    host = HostResourceContract(model.CAP, {role: model.CAP for role in ('deployment', 'compiler')})
    return cfg, schema, online, cuda, CudaCompilerPolicy(()), host


def adapters(stack, mode=None):
    stack.enter_context(patch.object(model, 'data', band.data))
    stack.enter_context(patch.object(model, 'scoring_groups', band.scoring_groups))
    stack.enter_context(patch.object(model, 'AdaptivePosterior', band.JointPosterior))
    if mode is not None:
        stack.enter_context(patch.object(model, 'setup', lambda case, _: configuration(case, mode)))


def preflight():
    assert 'torch' not in sys.modules
    assert not model.git('diff', GATE_SOURCE, '--', 'src/reference_compiler/fp_reference')
    gate = json.loads((ROOT/'evidence/minimal/FP_OWNED_PACKED_HISTOGRAM_CUDA_A1.json').read_text())
    assert gate['execution_source'] == GATE_SOURCE and gate['status'] == 'PASS_ACTUAL_OWNED_PACKED_HISTOGRAM'
    assert tuple(row['case'] for row in gate['workers']) == GATE_CASES
    for row in gate['workers']:
        job = row['completed_job']
        assert row['worker_status'] == 'PASS' and job['exit_code'] == 0
        assert job['attached_before_resume'] and not job['timed_out'] and not job['limit_terminated_processes']
        assert job['peak_job_commit'] <= job['commit_limit'] == 4 << 30
        assert row['result']['process_id'] == job['process_id']
    rows = []
    for case, control in zip(band.CASES, controls()):
        assert json.loads(json.dumps(band.control(case))) == control
        configs = [configuration(case, mode) for mode in MODES]
        a, b, c = configs
        assert a[:3] == b[:3] and a[4:] == b[4:]
        assert {k for k in vars(a[3]) if getattr(a[3], k) != getattr(b[3], k)} == {'backend_id', 'forward_id'}
        assert {k for k in vars(a[0]) if getattr(a[0], k) != getattr(c[0], k)} == {'indexed_histogram'}
        assert a[1:3] == c[1:3] and a[4:] == c[4:]
        assert {k for k in vars(a[3]) if getattr(a[3], k) != getattr(c[3], k)} == {
            'histogram', 'backend_id', 'forward_id', 'work_model'}
        rows.append({'case': case, 'training': 126, 'evaluation': 250, 'total': 376,
            'training_unseen_evaluation_queries': 124, 'complete_count_coordinates': 2016,
            'joint_posterior_expected_unseen_CE': control['scores']['adaptive_exact_unseen']['expected_CE_binary64'],
            'pair_ablation_expected_unseen_CE': control['scores']['independent_pair_unseen']['expected_CE_binary64']})
    # Validate the global output upper law on the full support, independent
    # of either tape's labels. This is metadata only, not a numerical run.
    schema = configs[0][1]
    counts = tuple(int(j-i <= 2) for i, j in combinations(range(64), 2))
    before = amp.IndexedAmpState(CountState(64, counts, None, 125, 125))
    maximum = checked = 0
    for i, j in combinations(range(64), 2):
        if j-i <= 2:
            plan = amp._prepare_prediction(schema, before, schema.rules(), schema.source_row(i*64+j), output_cap=model.CELLS)
            maximum = max(maximum, plan.output_cells)
            checked += 1
    assert maximum <= 280*64-150 < model.CELLS
    return {'status': 'REGISTERED_N64_BAND_MODEL', 'cases': rows, 'modes_in_execution_order': MODES,
        'all_labels_geometry_bound': band.bounds(64), 'all_forecasts_packed_bit_bound': 24064,
        'all_forecasts_histogram_output_bound': 6785, 'all_global_forecasts_output_bound': 17770,
        'global_full_support_metadata_queries': checked, 'global_full_support_maximum_outputs': maximum,
        'host_job_cap': model.CAP, 'deadline_ms': model.DEADLINE, 'packed_bytes': model.PACKED,
        'work_per_role': model.WORK, 'arena_bytes': model.ARENA, 'allocator_cap': 2*model.ARENA,
        'phase_frame_bytes': model.FRAME, 'phase_output_cells': model.CELLS, 'reference_integer_bits': 32768,
        'state_atol': '1/100', 'probability_atol': '1/1000', 'normalizer_cap': 18, 'activation_cap': 8,
        'histogram_allowance': asdict(BUDGET), 'histogram_workspace_bytes': packed.workspace_bytes(BUDGET, n=64),
        'evidence_encoding': phase_deflate.ENCODING_ID, 'component_source': GATE_SOURCE,
        'forward_ids': {mode: configuration(band.CASES[0], mode)[3].forward_id for mode in MODES},
        'controls': 'independent exact joint posterior, existing global and projected AMP; independent-pair posterior is only a correlation ablation',
        'scope': 'two fixed bounded-width causal tapes, full native count learner and ordinary updates; no all-pair distribution, population inference, architecture search or complete release',
        'failure_policy': 'retain every outcome; no incomplete-prefix score or relaxed caps; continue declared matrix on honest resource/numerical refusal, stop on execution/audit failure'}


def worker(case, mode):
    roots = []
    def capture(*args, **kwargs):
        rt = ReferenceCompilerRuntime(*args, **kwargs)
        roots.append(rt)
        return rt
    with ExitStack() as stack:
        adapters(stack, mode)
        stack.enter_context(patch.object(model, 'ReferenceCompilerRuntime', capture))
        result = model.worker(case, 'projected' if mode == 'projected' else 'global')
    assert len(roots) == 1
    rt = roots[0]
    snapshot = rt.snapshot()
    assert result['declared_forward_id'] == configuration(case, mode)[3].forward_id
    assert result['oracle_assignment_visits'] == 0
    workspace = 0
    if mode == 'carry-free':
        key, buffer = next((k, b) for k, b in snapshot.buffers if k.endswith(':histogram-storage'))
        workspace = packed.workspace_bytes(BUDGET, n=case[0])
        assert len(buffer) == workspace == snapshot.resources['objects'][key]['residency']['reference_payload_bytes']
    return {'status': 'EXECUTED_AND_AUDITED', 'case': case, 'mode': mode, 'process_id': os.getpid(),
        'result': result, 'frame_audit': frames.frames(rt), 'paid_histogram_bytes': workspace}


def read_worker(actual, case, mode):
    assert actual['case'] == list(case) and actual['mode'] == mode
    result = actual['result']
    assert result['declared_forward_id'] == configuration(case, mode)[3].forward_id
    assert actual['paid_histogram_bytes'] == (packed.workspace_bytes(BUDGET, n=64) if mode == 'carry-free' else 0)
    control = next(row for row in controls() if row['case'] == list(case))
    with ExitStack() as stack:
        adapters(stack)
        return model.read_result(result, case, 'projected' if mode == 'projected' else 'global', control['scores'])


def read(path):
    report = json.loads(path.read_text(encoding='utf-8'))
    assert report['status'] == 'COMPLETE_WITH_RETAINED_OUTCOMES'
    expected = tuple((case, mode) for case in band.CASES for mode in MODES)
    assert tuple((tuple(row['case']), row['mode']) for row in report['workers']) == expected
    results = []
    for row, (case, mode) in zip(report['workers'], expected):
        job = row['completed_job']
        if row['worker_status'] == 'RESOURCE_TERMINATED':
            assert job['timed_out'] or job['limit_terminated_processes']
            results.append({'case': case, 'mode': mode, 'status': 'RESOURCE_TERMINATED', 'scores': 0})
            continue
        actual = row['result']
        assert job['exit_code'] == 0 and not job['timed_out'] and not job['limit_terminated_processes']
        assert job['attached_before_resume'] and job['peak_job_commit'] <= model.CAP
        assert actual['process_id'] == job['process_id'] and actual['status'] == 'EXECUTED_AND_AUDITED'
        results.append({'case': case, 'mode': mode, **read_worker(actual, case, mode)})
    return {'status': 'PASS_RETAINED_BAND_MODEL_READERS', 'workers': results}


def execute(attempt):
    path = ROOT/f'evidence/minimal/FP_BAND_MODEL_A{attempt}.json'
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
    directory = Path(tempfile.mkdtemp(prefix='fp-band-model-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    stop = False
    for index, case in enumerate(band.CASES):
        for mode in MODES:
            output = directory/f'{index}-{mode}.json'
            row = {'case': case, 'mode': mode, 'worker_status': 'FAILED'}
            print('START '+str(case)+' '+mode, flush=True)
            try:
                clean()
                job = run_in_job(str(Path(__file__).resolve()), ('--worker', index, '--mode', mode, '--output', output),
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
                    assert job.attached_before_resume and job.peak_job_commit <= model.CAP
                    row['reader'] = read_worker(actual, case, mode)
                    row['worker_status'] = actual['result']['status']
                else:
                    stop = True
            except Exception:
                if not any(item is row for item in report['workers']):
                    report['workers'].append(row)
                row['collection_traceback'] = traceback.format_exc()
                stop = True
            publish()
            print(row['worker_status']+' '+str(case)+' '+mode, flush=True)
            if output.exists():
                assert output.resolve().parent == directory
                output.unlink()
            if stop:
                break
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
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--read', type=Path)
    args = parser.parse_args()
    if args.read:
        print(json.dumps(read(args.read), indent=2))
    elif args.worker is not None:
        assert args.mode and args.output
        result = {'status': 'FAILED_AUDIT', 'process_id': os.getpid(), 'case': band.CASES[args.worker], 'mode': args.mode}
        try:
            result = worker(band.CASES[args.worker], args.mode)
        except Exception:
            result['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        if result['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        execute(args.attempt)
    else:
        parser.error('select --preflight, --attempt, --read or --worker')
