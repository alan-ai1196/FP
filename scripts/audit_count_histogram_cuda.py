"""Preregistered hardware check of the proved histogram arithmetic schedule.

One fresh bounded arena/job, exact RNE of every actual word and endpoint,
independent native coordinates. This is a numerical component fixture, not
an owned Runtime continuation, paid constructor, model score or release.
"""
from dataclasses import asdict
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import count_histogram as decoder
from audit_count_histogram import oracle, state, TOLERANCE
from joint_model import data
from fp_reference import cuda_learner as gpu, indexed_amp as amp
from fp_reference.cuda_prefix import CudaPrefixContract
from fp_reference.cuda_storage import CudaArena, CudaStorageContract
from fp_reference.indexed_count import CountState, observe
from fp_reference.indexed_execution import IndexedState
from windows_job_audit_support import run_in_job

CAP, DEADLINE, ARENA, CELLS = 4 << 30, 600000, 16 << 20, 65536
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty',
    'experiments/adaptive_uncertainty', 'theory/proofs/COUNT_HISTOGRAM_DECODER.md')


def fixtures():
    yield 'prior-offdiagonal', state(3, (0, 0, 0)), (0, 1)
    yield 'prior-diagonal', state(3, (0, 0, 0)), (2, 2)
    for magnitude in (46, 47, 48):
        for sign in (1, -1):
            yield f'subnormal-{sign*magnitude}', state(2, (sign*magnitude,)), (0, 1)
    yield 'range-396', state(2, (396,)), (0, 1)
    yield 'dense-positive', state(16, (1,)*120), (0, 1)
    yield 'dense-negative', state(16, (-1,)*120), (1, 2)
    for case, cursor in (((16, 'iid-c2', 16), 194), ((16, 'iid-c2', 17), 332),
                         ((16, 'iid-c4', 18), 276), ((16, 'iid-c4', 18), 372),
                         ((16, 'iid-c4', 19), 368)):
        _, _, train, evaluation = data(case)
        tape = train+evaluation
        indices = {edge: k for k, edge in enumerate(combinations(range(16), 2))}
        counts = [0]*120
        for i, j, target in tape[:cursor]:
            if i != j:
                counts[indices[tuple(sorted((i, j)))]] += 1-2*target
        yield f'{case[1]}-{case[2]}-{cursor}', CountState(16, tuple(counts), None, cursor, cursor), tape[cursor][:2]


def preflight():
    assert 'torch' not in sys.modules
    rows = []
    for name, before, query in fixtures():
        hist = decoder.histogram(before, query)
        assert hist.output_cells <= CELLS
        rows.append({'case': name, 'n': before.n, 'query': query, 'H': hist.span,
                     'terms': hist.term_count, 'prediction_outputs': hist.output_cells})
    assert len(rows) == 16
    return {'cases': rows, 'host_job_cap': CAP, 'deadline_ms': DEADLINE,
        'arena_bytes': ARENA, 'allocator_cap': 2*ARENA, 'phase_output_cap': CELLS,
        'execution_identity': CudaPrefixContract.execution_identity,
        'state_atol': '1/100', 'probability_atol': '1/1000',
        'scope': 'actual numerical component only; no Runtime, class certificate, model score or speed comparison',
        'failure_policy': 'one attempt; retain failed or terminated outcome without cap changes or silent retry'}


def worker(output):
    report = {'status': 'RUNNING', 'process_id': os.getpid(), 'cases': []}
    def publish():
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    publish()
    try:
        arena = CudaArena(CudaStorageContract(ARENA, 2*ARENA,
            {role: (ARENA, 2*ARENA) for role in ('deployment', 'compiler')}))
        readout = bytearray(8*CELLS)
        for name, before, query in fixtures():
            physical_hist = decoder.histogram(before, query)
            with arena.phase(name+':predict') as workspace:
                actual = gpu.CudaArithmetic(32768, workspace=workspace,
                    output_cell_limit=CELLS, readout_buffer=readout)
                arithmetic = amp._Arithmetic(32768, actual)
                raw, resident = decoder._rounded_schedule(before, physical_hist, arithmetic)
                actual.check()
                assert actual.output_cells == physical_hist.output_cells
                endpoint = amp.IndexedAmpPrediction(before, query,
                    workspace.raw_words((resident.readout,), readout)[0])
                assert raw == endpoint == resident.raw()
                # Reconstruct after execution from retained inputs; no reference
                # partition/forecast supplies a physical numerical result.
                expected_arithmetic = amp._Arithmetic(32768)
                expected, _ = decoder._rounded_schedule(before, decoder.histogram(before, query), expected_arithmetic)
                checked = amp._check_execution(expected, endpoint, expected_arithmetic, actual.raw_trace())
                assert checked+7 == actual.output_cells
            reference, hist = decoder.reference(before, query)
            bins, parts = oracle(before, query)
            assert hist.terms == bins and reference.excesses == tuple(F(8*z, sum(parts)) for z in parts)
            relation = amp.check_prediction(reference, endpoint, TOLERANCE,
                normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
            row = {'case': name, 'prediction_outputs': physical_hist.output_cells,
                'prediction_words': endpoint.words, 'checked_prediction_operations': checked,
                'half_operations': sum(width == 16 for _, width, _ in arithmetic.trace),
                'probability_error': str(relation.probability_error), 'observations': []}
            for target in (0, 1):
                with arena.phase(name+':observe-'+str(target)) as workspace:
                    actual = gpu.CudaArithmetic(32768, workspace=workspace,
                        output_cell_limit=CELLS, readout_buffer=readout)
                    scalar = amp._Arithmetic(32768, actual)
                    raw, observed = amp._observation_schedule(amp.IndexedAmpState(before), endpoint,
                        target, scalar, resident_prediction=resident)
                    actual.check()
                    fresh = amp.IndexedAmpState(observe(before, *query, target),
                        workspace.raw_words((observed.gradient,), readout)[0])
                    assert raw == fresh == observed.raw() and actual.output_cells == 13
                    amp.check_observation_execution(amp.IndexedAmpState(before), endpoint, target,
                        fresh, actual.raw_trace(), bit_limit=32768)
                    mass = reference.masses[target]
                    native = IndexedState(fresh.encoded, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
                    error = amp.check_state(native, fresh, TOLERANCE, bit_limit=32768)
                    row['observations'].append({'target': target, 'gradient_words': fresh.gradient_words,
                                                'gradient_error': str(error.state_error)})
                assert resident.raw() == endpoint
            report['cases'].append(row)
            publish()
        snapshot = arena.snapshot()
        assert tuple(snapshot[key] for key in ('torch', 'torch_git_version', 'CUDA_runtime',
            'device_name', 'capability')) == CudaPrefixContract.execution_identity
        assert len(snapshot['phases']) == 48 and not any(readout)
        report['physical'] = {key: snapshot[key] for key in ('device_name', 'capability', 'torch',
            'torch_git_version', 'CUDA_runtime', 'actual_tensor_arena_bytes',
            'actual_allocator_reserved_bytes', 'native_allocation_counter_current')}
        report['status'] = 'PASS_ACTUAL_HISTOGRAM_ARITHMETIC'
    except Exception:
        report['status'] = 'FAILED_COMPONENT_AUDIT'
        report['traceback'] = traceback.format_exc()
    publish()
    return report['status'] == 'PASS_ACTUAL_HISTOGRAM_ARITHMETIC'


def git(*args):
    return subprocess.run(('git', *args), cwd=ROOT, capture_output=True,
                          encoding='utf-8', check=True).stdout.strip()


def execute(attempt):
    path = ROOT/f'evidence/minimal/FP_COUNT_HISTOGRAM_CUDA_A{attempt}.json'
    assert attempt > 0 and not path.exists()
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES)
    clean()
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'execution_source': source,
              'registration': preflight(), 'workers': []}
    def publish():
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temp.replace(path)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-count-histogram-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    output = directory/'result.json'
    row = {'worker_status': 'FAILED'}
    failed = True
    try:
        job = run_in_job(str(Path(__file__).resolve()), ('--worker', '--output', output),
                         commit_limit=CAP, timeout_ms=DEADLINE)
        row['completed_job'] = asdict(job)
        if output.exists():
            assert output.stat().st_size < 131072
            row['result'] = json.loads(output.read_text(encoding='utf-8'))
        report['workers'].append(row)
        publish()
        clean()
        if job.timed_out or job.limit_terminated_processes:
            row['worker_status'] = 'RESOURCE_TERMINATED'
        elif job.exit_code == 0:
            actual = row['result']
            assert job.attached_before_resume and job.peak_job_commit <= CAP
            assert actual['process_id'] == job.process_id and actual['status'] == 'PASS_ACTUAL_HISTOGRAM_ARITHMETIC'
            assert [x['case'] for x in actual['cases']] == [x['case'] for x in report['registration']['cases']]
            for declared, done in zip(report['registration']['cases'], actual['cases']):
                assert done['prediction_outputs'] == declared['prediction_outputs']
                assert done['checked_prediction_operations']+7 == done['prediction_outputs']
                assert done['half_operations'] == 3*declared['terms']
                assert [v['target'] for v in done['observations']] == [0, 1]
            row['worker_status'] = actual['status']
            failed = False
    except Exception:
        if not report['workers']:
            report['workers'].append(row)
        row['collection_traceback'] = traceback.format_exc()
    report['status'] = 'STOPPED_WITH_RETAINED_FAILURE' if failed else 'PASS_ACTUAL_HISTOGRAM_ARITHMETIC'
    publish()
    if output.exists():
        assert output.resolve().parent == directory
        output.unlink()
    directory.rmdir()
    print(report['status'], flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        raise SystemExit(0 if worker(args.output) else 1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        execute(args.attempt)
    else:
        parser.error('select --preflight, --attempt or --worker')
