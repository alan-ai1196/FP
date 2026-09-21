"""Owned CUDA policy and finite run closure inside actual fenced processes.

Only ordinary context/target transport drives selection, fresh evidence and
installation. These are correctness/resource runs, not model-science wins.
"""
import argparse
from dataclasses import replace
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import tempfile
import traceback
from types import FunctionType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CudaCompilerPolicy, CudaCompilationStep
from fp_reference.core import ContractError
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.cuda_storage import CudaStorageUnresolved
from fp_reference.host_failure import CUDA_RESOURCE_FAILURE, HOST_ALLOCATION_FAILURE
from fp_reference.host_resources import HostResourceContract
from fp_reference.ingress import encode_context
from fp_reference.machine import pack
from fp_reference.machine import ReferenceMachineModel
from fp_reference.native_search import GrammarLimits
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH
from fp_reference.policy import POLICY_EXTERNAL_PORTS
from fp_reference.program import Binding, DelayedStateSpec
from fp_reference.resources import ResourceExceeded
import fp_reference.runtime as execution
from audit_cpu_installation import configuration, SMALL
from audit_cuda_runtime import cuda_contract, audit_snapshot, no_device_handles
from audit_float64_runtime import replay
from audit_paired_cpu_persistence import config
from audit_reference_construction import limits, rejects, validate_residency, zero_program
from audit_reference_persistence import event
from windows_job_audit_support import run_in_job

HOST_CAP = 4 << 30
STEP = CudaCompilationStep(2, 'native', 10000, 'ref', 'cuda')


def parameters(*, count=40, learned=False, recurrent=False, continued=False, cpu=True, horizon=30,
               byte_cap=500_000_000):
    cfg = config(cap=10, peak=10, pattern=(F(2),)) if learned else config(cap=4, peak=1)
    cfg = replace(cfg, limits=limits(byte_cap, 60_000_000_000))
    if recurrent:
        cfg = replace(cfg, semantics=replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(1)),)))
    cfg, online = configuration(cfg=cfg, count=count, continued=continued,
        bounds=GrammarLimits(3, 2, 0, 1, 1) if learned else SMALL)
    rules = tuple(replace(r, rule_id=r.rule_id.replace('finite', 'cuda'), score_path=CUDA_PATH, max_epochs=horizon)
        if r.score_path == FLOAT64_PATH else replace(r, max_epochs=horizon) for r in online.persistence.rules)
    online = replace(online, persistence=replace(online.persistence, rules=rules), cpu_install=None,
                     float64=online.float64 if cpu else None)
    base = replace(zero_program(2), bindings=(Binding('h', 0),)) if recurrent else zero_program(2)
    return cfg, base, online


def make(*, steps=(STEP,), **kwargs):
    cfg, base, online = parameters(**kwargs)
    return ReferenceCompilerRuntime(cfg, base, online=online,
        host=HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}),
        cuda=cuda_contract(install=CudaInstallContract()), policy=CudaCompilerPolicy(steps))


def forbidden(rt, *, sealed=False):
    before = rt.snapshot()
    observation = f'observation-{before.cursor}'
    inputs = {'begin_context': (observation,), 'receive_context': ('absent-ingress', 0, b''),
        'finish_context': ('absent-ingress',), 'predict_next': (observation, encode_context((F(1), F(0)))),
        'observe': (0,)}
    ports = [name for name, method in vars(ReferenceCompilerRuntime).items()
        if type(method) is FunctionType and not name.startswith('_') and name != 'snapshot'
        and (sealed or name not in POLICY_EXTERNAL_PORTS)]
    for name in ports:
        rejects(lambda: getattr(rt, name)(*inputs.get(name, ())))
    assert replace(rt.snapshot(), host_resources=None) == replace(before, host_resources=None)
    return len(ports)


def owned(rt):
    state = validate_residency(rt)
    no_device_handles(state)
    buffers = dict(state.buffers)
    assert buffers[state.run.manifest_object_id] == pack(state.run.manifest)
    assert buffers[state.compiler_policy.state.object_id] == pack(state.compiler_policy.state)
    assert not state.compiler_policy.executing
    for receipt in state.install_receipts:
        assert buffers[receipt.object_id] == pack(receipt)
    closure = state.run.closure
    if closure is not None:
        assert buffers[closure.object_id] == pack(closure)
        assert closure.cursor == state.cursor == len(rt.online_contract.data.active.observation_ids)
        assert closure.deployed_id == state.deployed_id and closure.alpha_spent == state.alpha_spent
        assert closure.cuda_device == state.cuda.device
        raw_states = {p.object_id: p.raw_state for p in state.cuda.phases}
        assert tuple((cid, pid) for cid, pid, _, _ in closure.cuda_transport.current) == state.cuda.current
        assert closure.cuda_transport.current == tuple(
            (cid, pid, raw_states[pid], leases)
            for cid, pid, raw, leases in closure.cuda_transport.current)
        assert closure.checked_cuda_phases+closure.unresolved_cuda_phases == len(state.cuda.phases)
        assert dict(closure.native_graphs) == {key: tuple(program.counts().items()) for key, program in state.programs}
        assert tuple(d.proof for d in closure.decisions if d.proof is not None) == state.reference_proofs
        cuda_predictions = [p for p in state.cuda.phases if p.status == 'CHECKED_CUDA_PREFIX_PHASE' and p.raw_prediction is not None]
        diagnostic = next(d for d in closure.diagnostics if d.path == 'cuda-half-single')
        assert diagnostic.predictions == len(cuda_predictions)
    return state


def success(case):
    learned, recurrent, cpu = case == 'learned', case == 'recurrent', case != 'no-cpu'
    continued = case == 'success'
    steps = (STEP, CudaCompilationStep(24, 'next', 10000, 'ref-next', 'cuda-next')) if continued else (STEP,)
    tape = (0,)*22+(1,)*16+(0, 1)*11 if continued else (0,)*40 if learned else (0,)*22+(0, 1)*9
    rt = make(steps=steps, count=len(tape), learned=learned, recurrent=recurrent, continued=continued, cpu=cpu)
    denied = forbidden(rt)
    expected = [22, 38] if continued else [18] if learned else [22]
    previous, publications = rt._deployed_id, []
    def trace(frame, kind, arg):
        nonlocal previous
        if frame.f_code is not ReferenceCompilerRuntime._install_owned.__code__:
            return None
        if rt._deployed_id != previous:
            stage = next(s for s in rt._policy_state.stages if s.candidate_id == rt._deployed_id)
            assert stage.status == 'INSTALLED_CUDA' and stage.install_attempt == rt._install_receipts[-1].attempt.attempt_id
            assert rt._policy_state.object_id in rt._buffers
            publications.append(rt._cursor)
            previous = rt._deployed_id
        return trace
    for cursor, target in enumerate(tape, 1):
        # Trace each expected publication, not the entire native class's
        # arithmetic. The receipt/cursor equality below catches any install
        # outside these windows. Instrumentation supplies no Runtime input.
        if cursor in expected:
            sys.settrace(trace)
        try:
            event(rt, target)
        finally:
            sys.settrace(None)
    state = owned(rt)
    assert publications == [r.attempt.cursor for r in state.install_receipts] == expected, (
        publications, [r.attempt.cursor for r in state.install_receipts],
        [(s.status, s.reason) for s in state.compiler_policy.state.stages], state.halted,
        [(a.status, a.reason) for a in state.install_attempts])
    assert state.halted is None and state.run.status == 'SEALED_CUDA_STREAM'
    assert all(s.status == 'INSTALLED_CUDA' for s in state.compiler_policy.state.stages)
    assert state.alpha_spent == (F(3, 4) if continued else F(1, 2))
    if learned:
        actual = next(c for c in state.candidates if c.candidate_id == state.deployed_id)
        assert actual.theta != tuple(F(2) for _ in actual.theta)
    denied += forbidden(rt, sealed=True)
    return {'native_classes': [len(s.rows) for s in state.searches], 'install_cursors': publications,
        'policy_and_learner_publish_together': True, 'cursor': state.cursor, 'sealed_control_denials': denied,
        'alpha_spent': str(state.alpha_spent), 'independent_CUDA_phases': audit_snapshot(rt)['phases'],
        'independent_CPU_phases': replay(rt)[0] if cpu else 0, 'host': host_record(state)}


def host_record(state):
    resource = state.host_resources
    return {key: getattr(resource, key) for key in ('process_id', 'creation_100ns', 'lifetime_process_commit_peak')}


def registration():
    cfg, base, online = parameters()
    host = HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP})
    cuda = cuda_contract(install=CudaInstallContract())
    def root(policy, *, device=cuda, process=host, run=online):
        return ReferenceCompilerRuntime(cfg, base, online=run, cuda=device, host=process, policy=policy)
    rejects(lambda: root(CompilerPolicy(())))
    rejects(lambda: root(CudaCompilerPolicy(()), device=None))
    rejects(lambda: root(CudaCompilerPolicy(()), process=None))
    rejects(lambda: root(CudaCompilerPolicy((STEP,)), device=replace(cuda, install=None)))
    rejects(lambda: root(lambda *args: 'supplied policy state'))
    invalid = (replace(STEP, after_cursor=1), replace(STEP, after_cursor=42),
        replace(STEP, search_name='undeclared'), replace(STEP, reference_rule='cuda'),
        replace(STEP, cuda_rule='ref'))
    for step in invalid:
        rejects(lambda: root(CudaCompilerPolicy((step,))))
    import torch
    assert torch.cuda.memory_allocated() == torch.cuda.memory_reserved() == 0
    assert torch.cuda.memory_stats().get('allocation.all.allocated', 0) == 0
    rt = root(CudaCompilerPolicy(()))
    return {'registration_rejections_before_native_tensor_allocation': 10,
        'compiler_control_denials': forbidden(rt), 'host': host_record(owned(rt))}


def horizon_budget():
    rt = make(steps=(STEP, CudaCompilationStep(24, 'next', 10000, 'ref-next', 'cuda-next')),
        count=40, continued=True)
    for target in (0,)*22+(1,)*16+(0, 1):
        event(rt, target)
    state = owned(rt)
    assert state.run.status == 'SEALED_CUDA_STREAM'
    assert [r.attempt.cursor for r in state.install_receipts] == [22]
    stage = state.compiler_policy.state.stages[1]
    assert stage.status == 'UNRESOLVED' and stage.ended_cursor == 24
    assert stage.reference_identity is stage.cuda_identity is None
    assert 'registered future horizon does not fit' in stage.reason
    assert state.alpha_spent == F(1, 2)
    return {'30_epoch_second_admission_exceeds_remaining_16_events': True,
        'no_unadmitted_identity_or_alpha_debit': True, 'first_install_and_second_selection_retained': True,
        'terminal_denials': forbidden(rt, sealed=True), 'host': host_record(state)}


def branch(index):
    tape = tuple((index >> bit) & 1 for bit in range(4))
    rt = make(count=4, horizon=2)
    for target in tape:
        event(rt, target)
    state = owned(rt)
    assert state.run.status == 'SEALED_CUDA_STREAM' and state.halted is None
    assert len(state.searches) == 1 and len(state.searches[0].rows) == 35
    assert len(state.reference_proofs) == 1 and not state.install_receipts
    status = state.compiler_policy.state.stages[0].status
    assert status == ('UNRESOLVED' if tape[0] == tape[1] else 'BASELINE_SELECTED')
    assert state.alpha_spent == (F(1, 2) if tape[0] == tape[1] else 0)
    return {'labels': tape, 'stage_status': status, 'alpha_spent': str(state.alpha_spent),
        'independent_CUDA_phases': audit_snapshot(rt)['phases'], 'terminal_denials': forbidden(rt, sealed=True),
        'host': host_record(state)}


def late_frame_failure():
    rt = make(steps=(), count=3)
    event(rt, 0)
    event(rt, 1)
    original = execution.verify_transport
    seen = []
    def corrupt(witness, prefix, candidates):
        assert rt._run_closure is None and f'{rt._runtime_id}:run-closure' in rt._buffers
        value = prefix._values[prefix.current[rt._deployed_id]]
        value.gradient_sum.unsqueeze_(0)
        seen.append(value.gradient_sum)
        return original(witness, prefix, candidates)
    with patch.object(execution, 'verify_transport', corrupt):
        rejects(lambda: event(rt, 0), ContractError)
    assert len(seen) == 1
    seen[0].squeeze_(0)
    state = owned(rt)
    assert state.cursor == 3 and state.run.closure is None and state.run.status == 'HALTED_UNRESOLVED'
    assert f'{state.runtime_id}:run-closure' in dict(state.buffers)
    return {'prepared_owned_report_bytes_are_not_a_published_run': True,
        'post-preparation_device_corruption_keeps_completed_event_but_revokes_authority': True,
        'terminal_denials': forbidden(rt, sealed=True), 'host': host_record(state)}


def short(case, *, byte_cap=500_000_000):
    if case == 'partial':
        steps, tape = (), (0, 1, 0)
    elif case == 'search-budget':
        steps, tape = (replace(STEP, search_transitions=1),), (0, 0, 0, 1)
    else:
        assert case == 'unfinished'
        steps, tape = (STEP, STEP), (0, 0, 0)
    rt = make(steps=steps, count=len(tape), byte_cap=byte_cap, horizon=1 if case == 'unfinished' else 30)
    for target in tape:
        event(rt, target)
    state = owned(rt)
    assert state.run.status == 'SEALED_CUDA_STREAM' and not state.install_receipts
    if case == 'partial':
        assert state.run.closure.partial_optimizer_events == 1
        assert all(c.learner.unit_count == 1 for c in state.candidates)
    else:
        assert all(status == 'UNRESOLVED' for _, status, _ in state.run.closure.stage_outcomes)
    if case == 'search-budget':
        assert not state.reference_proofs and state.searches[0].status == 'CANCELLED'
    if case == 'unfinished':
        assert [s.status for s in state.compiler_policy.state.stages] == ['EVIDENCE', 'WAITING']
        assert state.alpha_spent == F(1, 2)
    return {'case': case, 'cursor': state.cursor, 'partial_optimizer_events': state.run.closure.partial_optimizer_events,
        'stage_outcomes': [s for _, s, _ in state.run.closure.stage_outcomes], 'terminal_denials': forbidden(rt, sealed=True),
        'independent_CUDA_phases': audit_snapshot(rt)['phases'], 'host': host_record(state)}


def failure(case):
    classes = {'report-resource': ResourceExceeded, 'report-memory': MemoryError,
               'report-device': CudaStorageUnresolved, 'report-unexpected': RuntimeError}
    rt = make(count=22, horizon=20)
    for _ in range(21):
        event(rt, 0)
    fault = classes[case]('injected CUDA run reporting failure')
    with patch.object(execution, 'cuda_diagnostics', side_effect=fault):
        if case == 'report-resource':
            event(rt, 0)
        else:
            try:
                event(rt, 0)
            except classes[case] as exc:
                assert exc is fault
            else:
                raise AssertionError('original run failure was lost')
    state = owned(rt)
    assert state.cursor == len(state.observations) == 22 and state.run.closure is None
    assert state.run.status == 'HALTED_UNRESOLVED'
    assert [r.attempt.cursor for r in state.install_receipts] == [22]
    assert state.compiler_policy.state.stages[0].status == 'INSTALLED_CUDA' and state.alpha_spent == F(1, 2)
    if case == 'report-memory':
        assert state.halted is HOST_ALLOCATION_FAILURE
    if case == 'report-device':
        assert state.halted is CUDA_RESOURCE_FAILURE
    return {'case': case, 'completed_target_install_and_alpha_survive_failed_report': True,
        'original_unexpected_exception_preserved': case == 'report-unexpected', 'host': host_record(state)}


def policy_failure(case):
    installation = case == 'install-policy-failure'
    count = 22 if installation else 4
    rt = make(count=count, horizon=20 if installation else 2)
    for _ in range(21 if installation else 1):
        event(rt, 0)
    original = ReferenceMachineModel.realize
    wanted = 'INSTALLED_CUDA' if installation else 'EVIDENCE'
    def fail(object_id, kind, value, provenance):
        if kind == 'owned_compiler_policy' and value.stages[0].status == wanted:
            raise ResourceExceeded('injected policy-state residency failure')
        return original(object_id, kind, value, provenance)
    with patch.object(ReferenceMachineModel, 'realize', staticmethod(fail)):
        event(rt, 0)
    state = owned(rt)
    assert not state.install_receipts and state.alpha_spent == F(1, 2)
    assert state.cursor == (22 if installation else 2)
    if installation:
        assert state.run.status == 'SEALED_CUDA_STREAM'
        assert state.compiler_policy.state.stages[0].status == 'UNRESOLVED'
        assert state.install_attempts[-1].status == 'UNRESOLVED'
        assert all(i.status not in ('ACTIVE', 'REFERENCE_CROSSED', 'CUDA_CROSSED') for i in state.persistence_identities)
    else:
        assert state.run.status == 'HALTED_UNRESOLVED' and state.run.closure is None
        assert len(state.persistence_identities) == 2
    return {'case': case, 'ordinary_event_and_spent_alpha_retained_without_install_or_retry': True,
        'terminal_denials': forbidden(rt, sealed=True), 'host': host_record(state)}


CASES = ('success', 'learned', 'recurrent', 'no-cpu', 'registration', 'partial', 'search-budget', 'unfinished', 'horizon-budget',
         'report-resource', 'report-memory', 'report-device', 'report-unexpected', 'admit-policy-failure', 'install-policy-failure',
         'late-frame', *('branch-'+str(i) for i in range(16)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--worker-output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker_output:
        assert args.case and not args.write
        try:
            if args.case == 'registration':
                result = registration()
            elif args.case == 'horizon-budget':
                result = horizon_budget()
            elif args.case.endswith('policy-failure'):
                result = policy_failure(args.case)
            elif args.case == 'late-frame':
                result = late_frame_failure()
            elif args.case.startswith('branch-'):
                result = branch(int(args.case.split('-')[1]))
            else:
                result = success(args.case) if args.case in CASES[:4] else failure(args.case) if args.case.startswith('report-') else short(args.case)
        except Exception:
            Path(args.worker_output).write_text(json.dumps({'failure': traceback.format_exc()[-4096:]}), encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result), encoding='utf-8')
        return
    report = {'status': 'PASS', 'scope': 'owned finite CUDA policy/run under registered host, tensor and framebuffer resource coordinates; no model-science or complete release claim'}
    workers = []
    branches = []
    for case in (args.case,) if args.case else CASES:
        with tempfile.TemporaryDirectory(prefix='fp-cuda-run-', dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent == ROOT
            output = Path(temporary)/'result.json'
            job = run_in_job(__file__, ('--case', case, '--worker-output', output), commit_limit=HOST_CAP, timeout_ms=900000)
            assert job.exit_code == 0 and not job.timed_out, (case, job, output.read_text() if output.exists() else '')
            raw = output.read_bytes()
            assert len(raw) <= 8192
            result = json.loads(raw)
            host = result['host']
            assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
            assert host['lifetime_process_commit_peak'] <= job.peak_process_commit <= HOST_CAP
            assert job.attached_before_resume and job.peak_job_commit <= HOST_CAP
            workers.append(job)
            if case.startswith('branch-'):
                branches.append(result)
            else:
                report[case] = dict(result, completed_job={key: getattr(job, key) for key in
                    ('peak_process_commit', 'peak_job_commit', 'user_100ns', 'kernel_100ns')})
        print(case+' PASS', flush=True)
    report['host_enforcement'] = {'workers': len(workers), 'commit_cap': HOST_CAP,
        'all_successful_exits_and_PID_lifetime_matches': True, 'all_fenced_before_execution': True,
        'maximum_process_commit': max(j.peak_process_commit for j in workers),
        'maximum_job_commit': max(j.peak_job_commit for j in workers)}
    if branches:
        report['finite_branches'] = {'complete_binary_four_event_streams': len(branches),
            'native_members_per_run': 35,
            'independent_CUDA_phases': sum(row['independent_CUDA_phases'] for row in branches),
            'baseline_selected': sum(row['stage_status'] == 'BASELINE_SELECTED' for row in branches),
            'evidence_unresolved': sum(row['stage_status'] == 'UNRESOLVED' for row in branches),
            'sealed_port_denials': sum(row['terminal_denials'] for row in branches)}
    if args.write:
        assert args.case is None
        (ROOT/'evidence/minimal/FP_CUDA_POLICY_RUN_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
