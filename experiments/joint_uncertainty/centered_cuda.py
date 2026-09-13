"""One new owned centered-world control; retain, never repeat the first pair."""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import tempfile
import traceback

import centered_contraction as model
import constraint_cuda as comparison
from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy
from fp_reference.cuda_prefix import output_cells
from fp_reference.host_resources import HostResourceContract
from audit_cuda_runtime import audit_snapshot, SINGLE
from audit_cuda_policy_run import owned
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

ROOT = comparison.ROOT
OUTPUT = ROOT / 'evidence/minimal/FP_CENTERED_CONTRACTION_CUDA_AUDIT.json'
DEPENDENCIES = comparison.DEPENDENCIES + ('experiments/joint_uncertainty/centered_contraction.py',
    'experiments/joint_uncertainty/centered_cuda.py', comparison.OUTPUT.relative_to(ROOT).as_posix())


def fixture():
    cfg, _, online = model.contraction.fixture('enumerated', horizon=len(comparison.TAPE))
    rules, graph = model.centered(2, 3)
    assert rules == cfg.semantics
    return cfg, graph, online


def preflight():
    registration = comparison.preflight()
    rules, graph = model.centered(2, 3)
    cells = {phase: output_cells(phase, graph, rules, model.contraction.LearnerSpec(1, F(0)))
             for phase in ('initialize', 'predict', 'observe', 'commit')}
    assert max(cells.values()) <= registration['phase_output_cells']
    state = model.contraction.control.model_initial(graph, rules, (F(1), F(8)))
    history = []
    maximum_probability_error = F(0)
    for i, j, y in comparison.TAPE:
        row = model.contraction.point(2, 3, history, (i, j))
        inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
        prediction = model.contraction.control.model_predict(graph, rules, state, inputs)
        expected = model.contraction.masses(2, history[-3:], (i, j))
        assert prediction['masses'] == expected
        maximum_probability_error = max(maximum_probability_error,
            *(abs(p - v/sum(expected)) for p, v in zip(prediction['probabilities'], expected)))
        state = model.contraction.control.model_commit(model.contraction.control.model_observe(graph, state, prediction, y),
                                                       model.contraction.LearnerSpec(1, F(0)))
        history.append((i, j, y))
    registration['cases'] = ['centered']
    registration['bounds'] = [{'kind': 'centered', 'graph': graph.counts(), 'output_cells': cells,
        'rounded_interpreter_maximum_mass_error': '0', 'rounded_interpreter_maximum_probability_error': str(maximum_probability_error)}]
    return registration


def worker():
    cfg, graph, online = fixture()
    cap = comparison.HOST_CAP
    rt = ReferenceCompilerRuntime(cfg, graph, online=online, policy=CudaCompilerPolicy(()),
        cuda=comparison.device_contract(), host=HostResourceContract(cap, {'deployment': cap, 'compiler': cap}))
    forecasts = []
    history = []
    for at, (i, j, y) in enumerate(comparison.TAPE):
        event = deliver_context(rt, f'contract-{at}', model.contraction.control.context(2, i, j))
        if event.status != 'PREDICTED_REFERENCE':
            assert event.status == 'UNRESOLVED'
            break
        snap = rt.snapshot()
        assert snap.pending.record.target is None
        expected = model.contraction.masses(2, history[-3:], (i, j))
        probability = tuple(m/sum(expected) for m in expected)
        assert dict(event.predictions)[snap.deployed_id] == probability
        phase = next(p for p in reversed(snap.cuda.phases) if p.raw_prediction is not None
                     and p.observation_id == f'contract-{at}' and p.candidate_id == snap.deployed_id)
        actual = tuple(SINGLE.decode(word) for word in phase.raw_prediction[3])
        assert actual == phase.reference_prediction.masses == expected
        forecasts.append({'reference_p0': str(probability[0]), 'reference_masses': list(map(str, expected)),
                          'actual_masses': list(map(str, actual))})
        observed = rt.observe(y)
        if observed.status != 'OBSERVED_REFERENCE':
            assert observed.status == 'UNRESOLVED'
            break
        history.append((i, j, y))
    final = owned(rt)
    complete = final.run.status == 'SEALED_CUDA_STREAM' and final.halted is None
    assert complete or final.run.status == 'HALTED_UNRESOLVED'
    assert not final.install_receipts and not final.reference_proofs
    cuda_audit = audit_snapshot(rt) if complete else None
    float_phases = replay(rt)[0] if complete else None
    if complete:
        assert len(final.observations) == len(comparison.TAPE) == len(forecasts)
        assert cuda_audit['phases'] == float_phases == 28
        assert final.candidates[0].theta == cfg.initializer_pattern and not final.candidates[0].delayed
    final = owned(rt)
    maximum = lambda traces: {key: str(max((getattr(t.relation, key) for t in traces if t.relation is not None), default=F(0)))
        for key in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error')}
    host = final.host_resources
    return {'kind': 'centered', 'run_status': final.run.status, 'halted': final.halted,
        'forecasts': forecasts, 'retained_observations': len(final.observations), 'CUDA_audit': cuda_audit,
        'independent_binary64_phases': float_phases, 'CUDA_relation_maxima': maximum(final.cuda.phases),
        'binary64_relation_maxima': maximum(final.float64_traces),
        'packed_peak': final.resources['peak']['reference_payload_bytes'],
        'consumed_arena_extent': final.cuda.storage['consumed_arena_extent'],
        'host': {key: getattr(host, key) for key in ('process_id', 'creation_100ns', 'lifetime_process_commit_peak',
            'job_commit_peak', 'process_user_100ns', 'process_kernel_100ns', 'job_user_100ns', 'job_kernel_100ns')},
        'device': {'identity': asdict(final.cuda.device.identity), 'execution_identity': final.cuda.contract.execution_identity,
            'physical_vram_upper': final.cuda.device.physical_vram_upper, 'scope': final.cuda.device.scope},
        'class_or_install_certificate': False}


def run(write):
    source = model.contraction.control.git('rev-parse', 'HEAD')
    def source_clean():
        assert model.contraction.control.git('rev-parse', 'HEAD') == source
        assert not model.contraction.control.git('status', '--porcelain', '--', *DEPENDENCIES)
    source_clean()
    previous = json.loads(comparison.OUTPUT.read_text(encoding='utf-8'))
    assert previous['status'] == 'COMPLETE_EXECUTION' and len(previous['workers']) == 2
    registration = preflight()
    for key, value in previous['registration'].items():
        if key not in ('cases', 'bounds'):
            assert json.loads(json.dumps(registration[key])) == value, key
    assert not write or not OUTPUT.exists(), 'retain the original centered attempt'
    report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source, 'registration': registration,
        'prior_comparison': {'journal': comparison.OUTPUT.relative_to(ROOT).as_posix(),
            'source': previous['registration_source'], 'attempts_retained_without_rerun': 2}, 'workers': []}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    with tempfile.TemporaryDirectory(prefix='fp-centered-cuda-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT.resolve()
        output = Path(temporary) / 'result.json'
        job = run_in_job(__file__, ('--worker', '--output', str(output)), commit_limit=comparison.HOST_CAP, timeout_ms=comparison.TIMEOUT)
        row = {'case_index': 0, 'kind': 'centered', 'worker_status': 'FAILED', 'completed_job': asdict(job), 'execution_source': source}
        if output.exists():
            with output.open('rb') as stream:
                payload = stream.read(65537)
            assert len(payload) <= 65536
            row['result'] = json.loads(payload)
        if job.exit_code == 0 and not job.timed_out:
            assert row['result']['host']['process_id'] == job.process_id
            assert row['result']['host']['creation_100ns'] == job.process_creation_100ns
            row['worker_status'] = 'EXECUTED'
        report['workers'].append(row)
        source_clean()
        report['status'] = 'COMPLETE_EXECUTION'
        publish()
    return {'status': report['status'], 'worker_status': row['worker_status'], 'run_status': row.get('result', {}).get('run_status')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert bool(args.output) == args.worker
    if args.worker:
        assert not (args.preflight or args.write)
        try:
            result = worker()
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback': traceback.format_exc()}), encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
    else:
        print(json.dumps(preflight() if args.preflight else run(args.write), indent=2))
