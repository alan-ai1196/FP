"""Registered owned comparison of two native window-posterior representations.

Both initial models have base one, Gamma=(1,8), the identical causal source
interface and full domain, and the same physical/resource/numerical contract.
This is a correctness/control tape, not a model-quality or discovery study.
"""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import tempfile
import traceback

import constraint_contraction as model
from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy
from fp_reference.cuda_prefix import output_cells
from fp_reference.host_resources import HostResourceContract
from audit_cuda_runtime import cuda_contract, audit_snapshot, SINGLE
from audit_cuda_policy_run import owned
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

ROOT = model.control.ROOT
OUTPUT = ROOT / 'evidence/minimal/FP_CONSTRAINT_CONTRACTION_CUDA_AUDIT.json'
DEPENDENCIES = model.control.DEPENDENCIES + ('experiments/joint_uncertainty/constraint_contraction.py',
                                           'experiments/joint_uncertainty/constraint_cuda.py')
CASES = ('contracted', 'enumerated')
TAPE = ((0, 0, 0),) * 4 + ((0, 1, 0), (0, 1, 0), (0, 1, 1), (0, 1, 1), (0, 1, 0))
HOST_CAP = 16 << 30
TIMEOUT = 900000


def device_contract():
    return cuda_contract(state_atol=F(2), probability_atol=F(1, 10000),
                         phase_output_cells=16384, phase_evidence_bytes=2 << 20)


def preflight():
    cuda = device_contract()
    bounds = []
    for kind in CASES:
        rules, graph = {'contracted': model.contracted, 'enumerated': model.enumerated}[kind](2, 3)
        cells = {phase: output_cells(phase, graph, rules, model.LearnerSpec(1, F(0)))
                 for phase in ('initialize', 'predict', 'observe', 'commit')}
        assert max(cells.values()) <= cuda.phase_output_cells
        # Nine future labels are fixed as a synthetic correctness diagnostic;
        # they remain unavailable to Runtime until the actual observe action.
        history = []
        state = model.control.model_initial(graph, rules, (F(1), F(8)))
        maximum_mass_error = maximum_probability_error = F(0)
        for i, j, y in TAPE:
            row = model.point(2, 3, history, (i, j))
            inputs = dict(zip((s.source_id for s in rules.sources), row, strict=True))
            prediction = model.control.model_predict(graph, rules, state, inputs)
            expected = model.masses(2, history[-3:], (i, j))
            if kind == 'enumerated':
                expected = tuple(2 * m for m in expected)
            maximum_mass_error = max(maximum_mass_error, *(abs(a-b) for a, b in zip(prediction['masses'], expected)))
            maximum_probability_error = max(maximum_probability_error,
                *(abs(a-b/sum(expected)) for a, b in zip(prediction['probabilities'], expected)))
            state = model.control.model_commit(model.control.model_observe(graph, state, prediction, y), model.LearnerSpec(1, F(0)))
            assert state.theta == (F(1), F(8))
            history.append((i, j, y))
        assert maximum_mass_error <= cuda.state_atol and maximum_probability_error <= cuda.probability_atol
        bounds.append({'kind': kind, 'graph': graph.counts(), 'output_cells': cells,
                       'rounded_interpreter_maximum_mass_error': str(maximum_mass_error),
                       'rounded_interpreter_maximum_probability_error': str(maximum_probability_error)})
    return {'cases': CASES, 'tape': TAPE, 'n': 2, 'window': 3, 'source_domain_rows': 2340,
            'sources': 22, 'native_delayed_states': 0, 'initializer': ['1', '8'],
            'base': ['1', '1'], 'learning_rate': '0', 'update_unit': 1, 'grid': None,
            'host_cap': HOST_CAP, 'timeout_ms': TIMEOUT, 'packed_cap': 2 << 30, 'work_per_role': 10**12,
            'activation_and_normalizer_cap': '14580',
            'arena_bytes': cuda.storage.arena_bytes, 'allocator_reserved_cap': cuda.storage.allocator_reserved_cap,
            'phase_output_cells': cuda.phase_output_cells, 'phase_evidence_bytes': cuda.phase_evidence_bytes,
            'state_native_normalizer_tolerance': str(cuda.state_atol), 'probability_tolerance': str(cuda.probability_atol),
            'bounds': bounds, 'scope': 'initial registered finite model; no proposal, fresh installation or class certificate'}


def worker(index):
    kind = CASES[index]
    cfg, graph, online = model.fixture(kind, horizon=len(TAPE))
    rt = ReferenceCompilerRuntime(cfg, graph, online=online, policy=CudaCompilerPolicy(()),
         cuda=device_contract(), host=HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    forecasts = []
    history = []
    for at, (i, j, y) in enumerate(TAPE):
        event = deliver_context(rt, f'contract-{at}', model.control.context(2, i, j))
        if event.status != 'PREDICTED_REFERENCE':
            assert event.status == 'UNRESOLVED'
            break
        snap = rt.snapshot()
        assert snap.pending.record.target is None
        expected = model.masses(2, history[-3:], (i, j))
        if kind == 'enumerated':
            expected = tuple(2 * m for m in expected)
        probability = tuple(m / sum(expected) for m in expected)
        assert dict(event.predictions)[snap.deployed_id] == probability
        phase = next(p for p in reversed(snap.cuda.phases) if p.raw_prediction is not None
                     and p.observation_id == f'contract-{at}' and p.candidate_id == snap.deployed_id)
        assert phase.reference_prediction.masses == expected
        actual = tuple(SINGLE.decode(word) for word in phase.raw_prediction[3])
        if kind == 'contracted':
            assert actual == expected
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
        assert len(final.observations) == len(TAPE) == len(forecasts)
        assert cuda_audit['phases'] == float_phases == 1 + 3 * len(TAPE)
        assert final.candidates[0].theta == cfg.initializer_pattern
        assert not final.candidates[0].delayed
    final = owned(rt)
    maximum = lambda traces: {key: str(max((getattr(t.relation, key) for t in traces if t.relation is not None), default=F(0)))
        for key in ('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error')}
    host = final.host_resources
    return {'kind': kind, 'run_status': final.run.status, 'halted': final.halted,
            'forecasts': forecasts, 'retained_observations': len(final.observations),
            'CUDA_audit': cuda_audit, 'independent_binary64_phases': float_phases,
            'CUDA_relation_maxima': maximum(final.cuda.phases), 'binary64_relation_maxima': maximum(final.float64_traces),
            'packed_peak': final.resources['peak']['reference_payload_bytes'],
            'consumed_arena_extent': final.cuda.storage['consumed_arena_extent'],
            'host': {key: getattr(host, key) for key in ('process_id', 'creation_100ns', 'lifetime_process_commit_peak',
                      'job_commit_peak', 'process_user_100ns', 'process_kernel_100ns', 'job_user_100ns', 'job_kernel_100ns')},
            'device': {'identity': asdict(final.cuda.device.identity), 'execution_identity': final.cuda.contract.execution_identity,
                       'physical_vram_upper': final.cuda.device.physical_vram_upper, 'scope': final.cuda.device.scope},
            'class_or_install_certificate': False}


def run(write, resume):
    source = model.control.git('rev-parse', 'HEAD')
    def source_clean():
        assert model.control.git('rev-parse', 'HEAD') == source
        assert not model.control.git('status', '--porcelain', '--', *DEPENDENCIES)
    source_clean()
    registration = json.loads(json.dumps(preflight()))
    if resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == source
        assert report['registration'] == registration
        assert [r['case_index'] for r in report['workers']] == list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(), 'preserve the original registered attempts'
        report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source, 'registration': registration, 'workers': []}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']), len(CASES)):
        source_clean()
        with tempfile.TemporaryDirectory(prefix='fp-constraint-cuda-', dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent == ROOT.resolve()
            output = Path(temporary) / 'result.json'
            job = run_in_job(__file__, ('--worker', str(index), '--output', str(output)), commit_limit=HOST_CAP, timeout_ms=TIMEOUT)
            row = {'case_index': index, 'kind': CASES[index], 'completed_job': asdict(job),
                   'worker_status': 'FAILED', 'execution_source': source}
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                assert len(payload) <= 65536
                row['result'] = json.loads(payload)
            if job.exit_code == 0 and not job.timed_out:
                assert 'run_status' in row.get('result', {})
                assert row['result']['host']['process_id'] == job.process_id
                assert row['result']['host']['creation_100ns'] == job.process_creation_100ns
                row['worker_status'] = 'EXECUTED'
            report['workers'].append(row)
            source_clean()
            publish()
            print(json.dumps({'case_index': index, 'kind': CASES[index], 'status': row['worker_status']}), flush=True)
    report['status'] = 'COMPLETE_EXECUTION'
    publish()
    return {'status': report['status'], 'workers': len(report['workers']),
            'executed': sum(r['worker_status'] == 'EXECUTED' for r in report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--worker', type=int, choices=range(len(CASES)))
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    assert not args.resume or args.write
    assert bool(args.output) == (args.worker is not None)
    if args.worker is not None:
        assert not (args.preflight or args.write or args.resume)
        try:
            result = worker(args.worker)
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback': traceback.format_exc()}), encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    else:
        print(json.dumps(run(args.write, args.resume), indent=2))
