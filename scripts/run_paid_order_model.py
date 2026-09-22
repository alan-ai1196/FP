"""One preregistered paid-order continuation of the exposed n16 model tape."""
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
from fp_reference import phase_deflate, query_order, indexed_amp
from windows_job_audit_support import run_in_job
import run_indexed_model as model
import run_phase_encoding as frames

CASE = (16, 'iid-c2', 16)
MODE = 'global'
GATE_SOURCE = 'ad68440d76d272c14a4b36f9dcab5613e28858f0'
DEPENDENCIES = model.DEPENDENCIES+('theory/proofs/PAID_QUERY_ORDER.md',
    'experiments/joint_uncertainty/PAID_ORDER_MODEL_PROTOCOL.md')


def configuration(case, mode):
    cfg, schema, online, cuda, policy, host = original_setup(case, mode)
    return (replace(cfg, indexed_order_search=True), schema, online,
        replace(cuda, order_search=True, evidence_encoding=phase_deflate.ENCODING_ID), policy, host)


original_setup = model.setup


def preflight():
    assert 'torch' not in sys.modules
    assert not model.git('diff', GATE_SOURCE, '--', 'src/reference_compiler')
    a1, a2, a5 = (json.loads((ROOT/f'evidence/minimal/FP_PAID_ORDER_CUDA_A{i}.json').read_text())
                   for i in (1, 2, 5))
    assert all(row['worker_status'] == 'PASS' for row in a1['workers'][:18])
    assert a2['workers'][0]['worker_status'] == 'PASS'
    assert a5['status'] == 'PASS_ACTUAL_PAID_QUERY_ORDER' and len(a5['workers']) == 5
    assert all(row['worker_status'] == 'PASS' for row in a5['workers'])
    baselines, source = model.controls()
    baseline = next(row for row in baselines if tuple(row['case']) == CASE)
    prior = json.loads((ROOT/'evidence/minimal/FP_PHASE_DEFLATE_CUDA_A1.json').read_text())
    control = next(row for row in prior['workers'] if row['case'] == 'model-global-deflate')
    assert control['worker_status'] == 'UNRESOLVED_MODEL' and control['result']['result']['cursor'] == 194
    old = original_setup(CASE, MODE)
    new = configuration(CASE, MODE)
    assert {k for k in vars(old[0]) if getattr(old[0], k) != getattr(new[0], k)} == {'indexed_order_search'}
    # The matched old path already used the byte-only compressed realization.
    old_cuda = replace(old[3], evidence_encoding=phase_deflate.ENCODING_ID)
    assert {k for k in vars(old_cuda) if getattr(old_cuda, k) != getattr(new[3], k)} == {
        'order_search', 'forward_id', 'work_model'}
    assert old[1:3] == new[1:3] and old[4:] == new[4:]
    assert new[3].forward_id == indexed_amp.ORDERED_FORWARD_ID
    _, _, train, evaluation = model.data(CASE)
    assert len(train) == 140 and len(evaluation) == 256
    return {'status': 'REGISTERED_PAID_ORDER_N16_MODEL', 'case': CASE, 'mode': MODE,
        'training_events': len(train), 'evaluation_events': len(evaluation),
        'host_job_cap': model.CAP, 'deadline_ms': model.DEADLINE, 'packed_bytes': model.PACKED,
        'work_per_role': model.WORK, 'arena_bytes': model.ARENA, 'phase_frame_bytes': model.FRAME,
        'phase_output_cells': model.CELLS, 'reference_integer_bits': 32768,
        'state_atol': '1/100', 'probability_atol': '1/1000', 'normalizer_cap': 18, 'activation_cap': 8,
        'new_paid_scratch_bytes': query_order.workspace_bytes(16, (0, 0)),
        'search_work_model': query_order.WORK_MODEL,
        'declared_forward_id': new[3].forward_id, 'evidence_encoding': phase_deflate.ENCODING_ID,
        'prior_fixed_compressed_source': prior['execution_source'], 'prior_fixed_compressed_cursor': 194,
        'baseline_anchor': model.BASELINE_ANCHOR, 'baseline_execution_source': source,
        'retained_strong_exact_posterior_CE': baseline['adaptive_exact_unseen']['expected_CE_binary64'],
        'changes': ['paid reference and physical order search', '393216-byte lifetime-owned DP table',
                    'registered order-dependent AMP schedule and work identity'],
        'unchanged': ['data, targets and evaluation order', 'complete native learner and initial state',
                      'all numerical and resource limits', 'empty Compiler policy', 'strong retained posterior controls'],
        'scope': 'one exposed retrospective tape, same original envelope; no full indexed release or model-superiority claim',
        'failure_policy': 'retain every terminal outcome; no score for an incomplete prefix; no silent retry or cap relaxation'}


def worker():
    roots = []
    constructor = model.ReferenceCompilerRuntime
    def capture(*args, **kwargs):
        rt = constructor(*args, **kwargs)
        roots.append(rt)
        return rt
    with patch.object(model, 'setup', configuration), patch.object(model, 'ReferenceCompilerRuntime', capture):
        result = model.worker(CASE, MODE)
    assert len(roots) == 1
    rt = roots[0]
    snapshot = rt.snapshot()
    assert snapshot.cuda.contract.order_search and rt._contract.indexed_order_search
    assert result['declared_forward_id'] == indexed_amp.ORDERED_FORWARD_ID
    search_events = [e for e in snapshot.resources['events'] if 'query-order-search' in e[-1]]
    key, buffer = next((k, b) for k, b in snapshot.buffers if 'query-order-storage' in k)
    assert len(buffer) == snapshot.resources['objects'][key]['residency']['reference_payload_bytes'] == 393216
    return {'status': 'EXECUTED_AND_AUDITED', 'process_id': os.getpid(), 'case': CASE, 'mode': MODE,
        'result': result, 'frame_audit': frames.frames(rt),
        'paid_search': {'calls': len(search_events), 'work': sum(dict(e[4])['work'] for e in search_events),
                        'charged_and_actual_table_bytes': len(buffer), 'certificate_class': None}}


def execute(attempt):
    output = ROOT/f'evidence/minimal/FP_PAID_ORDER_MODEL_A{attempt}.json'
    assert attempt > 0 and not output.exists(), 'retain every actual attempt separately'
    source = model.git('rev-parse', 'HEAD')
    def clean():
        assert model.git('rev-parse', 'HEAD') == source
        assert not model.git('status', '--porcelain', '--', *DEPENDENCIES)
    clean()
    registration = preflight()
    baselines, _ = model.controls()
    baseline = next(row for row in baselines if tuple(row['case']) == CASE)
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'execution_source': source,
              'registration': registration, 'workers': []}
    def publish():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(output)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-paid-order-model-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    path = directory/'result.json'
    row = {'case': CASE, 'mode': MODE, 'worker_status': 'FAILED'}
    failed = False
    try:
        job = run_in_job(str(Path(__file__).resolve()), ('--worker', '--output', path),
            commit_limit=model.CAP, timeout_ms=model.DEADLINE)
        row['completed_job'] = asdict(job)
        if path.exists():
            raw = path.read_bytes()
            assert len(raw) <= 262144
            row['result'] = json.loads(raw)
        report['workers'].append(row)
        publish()
        clean()
        if job.timed_out or job.limit_terminated_processes:
            row['worker_status'] = 'RESOURCE_TERMINATED'
        elif job.exit_code == 0:
            actual = row['result']
            assert job.attached_before_resume and job.peak_job_commit <= model.CAP
            assert actual['status'] == 'EXECUTED_AND_AUDITED' and actual['process_id'] == job.process_id
            assert actual['case'] == list(CASE) and actual['mode'] == MODE
            row['reader'] = model.read_result(actual['result'], CASE, MODE, baseline)
            row['worker_status'] = actual['result']['status']
        else:
            failed = True
    except Exception:
        if not report['workers']:
            report['workers'].append(row)
        row['collection_traceback'] = traceback.format_exc()
        failed = True
    report['status'] = 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' if failed else 'COMPLETE_WITH_RETAINED_OUTCOME'
    publish()
    print(row['worker_status'], flush=True)
    if path.exists():
        assert path.resolve().parent == directory
        path.unlink()
    directory.rmdir()
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
        result = {'status': 'FAILED_AUDIT', 'process_id': os.getpid(), 'case': CASE, 'mode': MODE}
        try:
            result = worker()
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
        parser.error('select --preflight, --attempt or --worker')
