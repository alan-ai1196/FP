"""One bounded actual arithmetic gate for carry-free coefficient histograms."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import math
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler'),
               str(ROOT/'experiments/joint_uncertainty')]
import audit_count_histogram_cuda as common
import packed_count_histogram as packed
import audit_packed_count_histogram as cpu
from fp_reference import indexed_amp as amp
from fp_reference.indexed_execution import IndexedState
from windows_job_audit_support import run_in_job

STATUS = 'PASS_ACTUAL_PACKED_HISTOGRAM_ARITHMETIC'
FORWARD = 'packed-count-coefficient-normalized-histogram-rne16-rne32-v1'
DEPENDENCIES = common.DEPENDENCIES+('theory/proofs/PACKED_COUNT_HISTOGRAM.md',
    'evidence/minimal/FP_PACKED_COUNT_HISTOGRAM.json')


def fixtures():
    yield 'prior-offdiagonal', cpu.state(3, (0, 0, 0)), (0, 1)
    yield 'prior-diagonal', cpu.state(3, (0, 0, 0)), (2, 2)
    for magnitude in (46, 47, 48):
        for sign in (1, -1):
            yield f'subnormal-{sign*magnitude}', cpu.state(2, (sign*magnitude,)), (0, 1)
    yield 'range-396', cpu.state(2, (396,)), (0, 1)
    for n, kind in ((32, 'band'), (64, 'band'), (128, 'path'), (256, 'empty')):
        before, query = cpu.fixture(n, kind)
        yield f'n{n}-{kind}', before, query
    before, _ = cpu.fixture(256, 'empty')
    yield 'n256-empty-diagonal', before, (255, 255)
    before, query = cpu.fixture(256, 'one')
    yield 'n256-positive80', before, query
    yield 'n256-negative80', replace(before, counts=tuple(-d for d in before.counts)), query


class Decoder(cpu.NativeAdapter):
    histogram = staticmethod(packed.prepare)
    rounded_observation = staticmethod(common.decoder.rounded_observation)

    @staticmethod
    def _rounded_schedule(before, plan, arithmetic):
        assert plan.before == before
        return packed.schedule(plan, arithmetic)


def oracle(before, query):
    n = before.n
    if n <= 16:
        return cpu.prior.oracle(before, query)
    if n in (32, 64):
        assert (before, query) == cpu.fixture(n, 'band')
        terms = cpu.band_oracle(before, query, 2)
    elif n == 128:
        assert (before, query) == cpu.fixture(n, 'path')
        terms = tuple(tuple((k, math.comb(n-1, k)) for k in range(n)
                            if (n-1-k)%2 == y) for y in (0, 1))
    else:
        assert n == 256
        if not any(before.counts):
            terms = ((((0, 1 << (n-1)),), ()) if query[0] == query[1]
                     else (((0, 1 << (n-2)),),)*2)
        else:
            assert query == (0, 1) and abs(before.counts[0]) == 80 and not any(before.counts[1:])
            terms = tuple(((80*int(y == int(before.counts[0] < 0)), 1 << (n-2)),) for y in (0, 1))
    return terms, tuple(sum(h*9**k for k, h in part) for part in terms)


def preflight():
    assert 'torch' not in sys.modules
    result = json.loads((ROOT/'evidence/minimal/FP_PACKED_COUNT_HISTOGRAM.json').read_text())
    assert result['status'] == 'PASS_PASSIVE_PACKED_COUNT_HISTOGRAM'
    rows = []
    check = cpu.Audit()
    for name, before, query in fixtures():
        plan = packed.prepare(before, query)
        assert plan.output_cells <= common.CELLS
        coefficients, parts = oracle(before, query)
        assert plan.terms == coefficients and packed.exact_parts(plan) == parts
        check.check(plan)
        rows.append({'case': name, 'n': before.n, 'query': query, 'H': plan.span,
            'terms': plan.term_count, 'prediction_outputs': plan.output_cells,
            'integer_envelope': plan.integer_envelope, 'elimination': dict(plan.shape)})
    assert len(rows) == 16
    return {'cases': rows, 'host_job_cap': common.CAP, 'deadline_ms': common.DEADLINE,
        'arena_bytes': common.ARENA, 'allocator_cap': 2*common.ARENA,
        'phase_output_cap': common.CELLS, 'execution_identity': common.CudaPrefixContract.execution_identity,
        'forward_id': FORWARD, 'integer_bits': 32768, 'state_atol': '1/100', 'probability_atol': '1/1000',
        'CPU_fixture_predictions': check.predictions, 'CPU_fixture_observations': check.observations,
        'scope': 'actual arithmetic with independent coefficients; no Runtime, model score or class certificate',
        'failure_policy': 'retain every terminal outcome; no cap changes or silent retry'}


def worker(path):
    with patch.object(common, 'fixtures', fixtures), patch.object(common, 'decoder', Decoder), \
            patch.object(common, 'oracle', oracle):
        success = common.worker(path)
    result = json.loads(path.read_text(encoding='utf-8'))
    result['forward_id'] = FORWARD
    if success:
        result['status'] = STATUS
    path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return success


def read_result(result):
    assert result['status'] == STATUS and result['forward_id'] == FORWARD
    assert len(result['cases']) == 16
    checked = 0
    for (name, before, query), row in zip(fixtures(), result['cases']):
        assert row['case'] == name
        plan = packed.prepare(before, query)
        expected, _ = packed.rounded_prediction(plan)
        assert row['prediction_outputs'] == plan.output_cells
        assert row['checked_prediction_operations']+7 == plan.output_cells
        assert row['half_operations'] == 3*plan.term_count
        assert row['prediction_words'] == list(expected.words)
        assert all(type(word) is int for word in row['prediction_words'])
        reference = packed.reference(plan)
        relation = amp.check_prediction(reference, expected, cpu.TOLERANCE,
            normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
        assert row['probability_error'] == str(relation.probability_error)
        assert len(row['observations']) == 2
        checked += 7
        for target, observation in enumerate(row['observations']):
            assert type(observation['target']) is int and observation['target'] == target
            rounded, _ = Decoder.rounded_observation(before, expected, target)
            assert observation['gradient_words'] == list(rounded.gradient_words)
            assert all(type(word) is int for word in observation['gradient_words'])
            mass = reference.masses[target]
            truth = IndexedState(rounded.encoded, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
            relation = amp.check_state(truth, rounded, cpu.TOLERANCE, bit_limit=32768)
            assert observation['gradient_error'] == str(relation.state_error)
            checked += 3
    assert checked == 208
    return {'status': 'PASS_RETAINED_PACKED_ENDPOINTS', 'fixtures': 16,
            'prediction_and_gradient_words': checked, 'new_CUDA_executions': 0}


def read(path):
    report = json.loads(path.read_text(encoding='utf-8'))
    assert report['status'] == STATUS and len(report['workers']) == 1
    assert report['registration'] == json.loads(json.dumps(preflight()))
    row = report['workers'][0]
    job = row['completed_job']
    assert row['worker_status'] == STATUS and job['exit_code'] == 0
    assert job['attached_before_resume'] and not job['timed_out'] and not job['limit_terminated_processes']
    assert job['peak_job_commit'] <= common.CAP and job['process_id'] == row['result']['process_id']
    return read_result(row['result'])


def execute(attempt):
    output = ROOT/f'evidence/minimal/FP_PACKED_HISTOGRAM_CUDA_A{attempt}.json'
    assert attempt > 0 and not output.exists()
    source = common.git('rev-parse', 'HEAD')
    def clean():
        assert common.git('rev-parse', 'HEAD') == source
        assert not common.git('status', '--porcelain', '--', *DEPENDENCIES)
    clean()
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'execution_source': source,
              'registration': preflight(), 'workers': []}
    def publish():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(output)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-packed-histogram-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    path = directory/'result.json'
    row, failed = {'worker_status': 'FAILED'}, True
    try:
        job = run_in_job(str(Path(__file__).resolve()), ('--worker', '--output', path),
            commit_limit=common.CAP, timeout_ms=common.DEADLINE)
        row['completed_job'] = asdict(job)
        if path.exists():
            assert path.stat().st_size < 131072
            row['result'] = json.loads(path.read_text(encoding='utf-8'))
        report['workers'].append(row)
        publish()
        clean()
        if job.timed_out or job.limit_terminated_processes:
            row['worker_status'] = 'RESOURCE_TERMINATED'
        elif job.exit_code == 0:
            assert job.attached_before_resume and job.peak_job_commit <= common.CAP
            assert row['result']['process_id'] == job.process_id
            row['reader'] = read_result(row['result'])
            row['worker_status'], failed = STATUS, False
    except Exception:
        if not report['workers']:
            report['workers'].append(row)
        row['collection_traceback'] = traceback.format_exc()
    report['status'] = 'STOPPED_WITH_RETAINED_FAILURE' if failed else STATUS
    publish()
    if path.exists():
        assert path.resolve().parent == directory
        path.unlink()
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
    parser.add_argument('--read', type=Path)
    args = parser.parse_args()
    if args.read is not None:
        print(json.dumps(read(args.read), indent=2))
    elif args.worker:
        assert args.output is not None
        raise SystemExit(0 if worker(args.output) else 1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        execute(args.attempt)
    else:
        parser.error('select --preflight, --attempt, --read or --worker')
