"""Owned finite run registration, completion and failure, through Runtime."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import FunctionType
import argparse
import json
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference.core import ContractError
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE, HOST_RESOURCE_FAILURE
from fp_reference.host_resources import HostResourceContract, HostExecutionUnresolved
from fp_reference.ingress import encode_context
from fp_reference.machine import pack
from fp_reference.program import Program, Source
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.runtime as execution
from audit_cpu_installation import configuration
from audit_float64_runtime import replay
from audit_owned_compiler_policy import make, STEP
from audit_reference_construction import rejects, validate_residency, zero_program
from audit_reference_persistence import event
from windows_job_audit_support import run_in_job


def owned(rt):
    state = validate_residency(rt)
    run, buffers = state.run, dict(state.buffers)
    assert buffers[run.manifest_object_id] == pack(run.manifest)
    assert run.manifest.construction == rt.contract
    assert run.manifest.online == rt.online_contract
    if run.closure is not None:
        assert buffers[run.closure.object_id] == pack(run.closure)
        assert run.closure.cursor == state.cursor == len(rt.online_contract.data.active.observation_ids)
        assert run.closure.deployed_id == state.deployed_id
        assert run.closure.alpha_spent == state.alpha_spent
        assert dict(run.closure.native_graphs) == {key: tuple(program.counts().items()) for key, program in state.programs}
        assert tuple(d.proof for d in run.closure.decisions if d.proof is not None) == state.reference_proofs
    return state


def closed_ports(rt):
    before = rt.snapshot()
    ports = tuple(name for name, fn in vars(ReferenceCompilerRuntime).items()
                  if type(fn) is FunctionType and not name.startswith('_') and name != 'snapshot')
    for name in ports:
        rejects(lambda: getattr(rt, name)())
    assert replace(rt.snapshot(), host_resources=None) == replace(before, host_resources=None)
    return len(ports)


def registration():
    cfg, online = configuration()
    initial = zero_program(2)
    def root(c=cfg, p=initial, o=online, policy=CompilerPolicy(())):
        return ReferenceCompilerRuntime(c, p, online=o, policy=policy)
    rt = root()
    snapshot = owned(rt)
    assert snapshot.run.status == 'OPEN_OWNED_STREAM'
    assert snapshot.run.manifest.initial_program == initial
    variants = [
        root(p=Program((Source('x0_0'),), 0, (0, 0))),
        root(c=replace(cfg, normalizer_cap=F(5))),
        root(c=replace(cfg, graph_limits=dict(cfg.graph_limits, edges=10001))),
        root(c=replace(cfg, initializer_pattern=(F(1),))),
        root(o=replace(online, learner=replace(online.learner, learning_rate=F(0)))),
        root(o=replace(online, float64=replace(online.float64, state_atol=F(1, 1024)))),
        root(policy=CompilerPolicy((STEP,))), root(policy=None),
    ]
    assert len({rt.chi, *(other.chi for other in variants)}) == len(variants)+1
    assert variants[-1].snapshot().run.status == 'MANUAL_PARTIAL'
    assert 'UNRESOLVED' in snapshot.run.host_scope
    rejects(lambda: ReferenceCompilerRuntime(cfg, initial, online=online, manifest=snapshot.run.manifest), TypeError)
    rejects(lambda: ReferenceCompilerRuntime(cfg, initial, online=online, run=snapshot.run), TypeError)
    return {'registered_coordinate_variants_have_distinct_identity': len(variants),
            'initial_baseline_and_fixed_numerical_policy_in_owned_manifest': True,
            'caller_manifest_and_run_record_not_authority_inputs': True}


def finite_streams():
    count = denied = 0
    for length in (2, 3, 4):
        for labels in product(range(2), repeat=length):
            rt = make(count=length, steps=())
            for target in labels[:-1]:
                event(rt, target)
            assert owned(rt).run.status == 'OPEN_OWNED_STREAM'
            assert rt.predict_next(f'observation-{length-1}', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
            pending = owned(rt)
            assert pending.run.status == 'OPEN_OWNED_STREAM' and pending.pending.record.target is None
            assert rt.observe(labels[-1]).status == 'OBSERVED_REFERENCE'
            final = owned(rt)
            assert final.run.status == 'SEALED_REFERENCE_STREAM' and final.halted is None
            assert final.run.closure.partial_optimizer_events == length % 2
            assert all(c.learner.unit_count == length % 2 for c in final.candidates)
            for diagnostics in final.run.closure.diagnostics:
                assert diagnostics.predictions == length
                assert diagnostics.minimum_nonzero_activation is None
                assert diagnostics.maximum_activation == 0
                assert diagnostics.minimum_mass == 1 and diagnostics.maximum_normalizer == 2
            denied += closed_ports(rt)
            count += 1
    # A partial final optimizer unit does not give the strategy another
    # boundary. Its EVIDENCE state survives even though evidence exhausted
    # its declared horizon at the last event.
    def horizon(n):
        return lambda online: replace(online, persistence=replace(online.persistence,
            rules=tuple(replace(rule, max_epochs=n) for rule in online.persistence.rules)))
    rt = make(count=5, transform=horizon(3))
    for _ in range(5):
        event(rt, 0)
    final = owned(rt)
    assert final.run.status == 'SEALED_REFERENCE_STREAM'
    assert final.compiler_policy.state.stages[0].status == 'EVIDENCE'
    assert final.run.closure.stage_outcomes[0][1] == 'UNRESOLVED'
    assert final.alpha_spent == F(1, 2) and not final.install_receipts
    assert all(identity.status == 'UNRESOLVED' for identity in final.persistence_identities)
    denied += closed_ports(rt)
    # A newly eligible stage at the final boundary cannot borrow a future
    # event, and a later stage cannot run opportunistically in its place.
    rt = make(count=2, steps=(STEP, STEP))
    event(rt, 0)
    event(rt, 0)
    final = owned(rt)
    assert [stage.status for stage in final.compiler_policy.state.stages] == ['UNRESOLVED', 'WAITING']
    assert all(outcome[1] == 'UNRESOLVED' for outcome in final.run.closure.stage_outcomes)
    return {'all_binary_streams_at_lengths_2_3_4': count, 'terminal_port_denials_without_history_growth': denied,
            'partial_optimizer_unit_retained_without_flush': True,
            'end_of_stream_not_evidence_crossing_or_rejection': True,
            'waiting_and_active_stages_report_unresolved_without_history_erasure': True}


def installed(*, host=None, closure_failure=None):
    rt = make(count=22, host=host, transform=lambda online: replace(online,
        persistence=replace(online.persistence, rules=tuple(replace(rule, max_epochs=20) for rule in online.persistence.rules))))
    for _ in range(21):
        event(rt, 0)
    assert rt.predict_next('observation-21', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
    allocate = ReferenceCompilerRuntime._allocate
    def admission(self, owner, objects):
        if any(obj.spec.object_id.endswith(':run-closure') for obj in objects) and closure_failure is not None:
            raise closure_failure('injected closure retention refusal')
        return allocate(self, owner, objects)
    with patch.object(ReferenceCompilerRuntime, '_allocate', admission):
        if closure_failure is MemoryError:
            rejects(lambda: rt.observe(0), MemoryError)
        else:
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    final = owned(rt)
    assert final.cursor == len(final.observations) == 22
    assert final.install_receipts[-1].attempt.target_id == final.deployed_id
    assert final.compiler_policy.state.stages[0].status == 'INSTALLED_CPU'
    assert final.alpha_spent == F(1, 2)
    if closure_failure is not None:
        assert final.run.status == 'HALTED_UNRESOLVED' and final.run.closure is None
        if closure_failure is MemoryError:
            assert final.halted == HOST_ALLOCATION_FAILURE
        rejects(lambda: rt.predict_next('observation-21', encode_context((1, 0))))
        return {'already_published_install_event_and_alpha_survive_failed_run_closure': True,
                'event_success_cannot_authorize_complete_run_success': True}
    assert final.run.status == 'SEALED_REFERENCE_STREAM'
    assert final.run.closure.stage_outcomes[0][1] == 'INSTALLED_CPU'
    assert len(final.run.closure.decisions) == 1 and final.run.closure.decisions[0].proof.program_count == 35
    checks, _, _ = replay(rt)
    denied = closed_ports(rt)
    result = {'cursor': final.cursor, 'native_class_size': 35, 'independent_binary64_phase_checks': checks,
              'sealed_port_denials': denied, 'alpha_spent': str(final.alpha_spent),
              'closure_included_in_actual_owned_payload_bytes': True}
    if host is not None:
        observed = rt.snapshot().host_resources
        result['host'] = {key: getattr(observed, key) for key in ('process_id', 'creation_100ns',
            'lifetime_process_commit_peak', 'job_commit_peak', 'process_user_100ns', 'process_kernel_100ns')}
    return result


def failures():
    rows = {failure.__name__: installed(closure_failure=failure) for failure in (ResourceExceeded, MemoryError)}
    for failure in (ArithmeticUnresolved, HostExecutionUnresolved):
        rt = make(count=2, steps=())
        event(rt, 0)
        assert rt.predict_next('observation-1', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
        with patch.object(execution, 'prediction_diagnostics', side_effect=failure('injected reporting uncertainty')):
            if failure is HostExecutionUnresolved:
                rejects(lambda: rt.observe(0), failure)
            else:
                assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        final = owned(rt)
        assert final.cursor == len(final.observations) == 2 and final.run.closure is None
        assert final.run.status == 'HALTED_UNRESOLVED'
        if failure is HostExecutionUnresolved:
            assert final.halted == HOST_RESOURCE_FAILURE
        rows[failure.__name__] = {'completed_target_prefix_not_rolled_back_or_sealed': True}
    rt = make(count=2, steps=())
    event(rt, 0)
    assert rt.predict_next('observation-1', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
    # Same future-feature frame adversary as CPU installation, never a
    # production extension or an allowed caller state-injection port.
    rt._unregistered_future_job = ('pending',)
    rejects(lambda: rt.observe(0))
    final = owned(rt)
    assert final.cursor == 2 and final.run.status == 'HALTED_UNRESOLVED' and final.run.closure is None
    rows['unknown_frame'] = {'unregistered_future_job_cannot_inherit_run_completion': True}
    return rows


def bounded():
    cap = 64 << 20
    with tempfile.TemporaryDirectory(prefix='fp-run-audit-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--worker', '--output', output), commit_limit=cap, timeout_ms=60000)
        assert job.exit_code == 0 and not job.timed_out, job
        with output.open('rb') as source:
            payload = source.read(8193)
        assert len(payload) <= 8192
        result = json.loads(payload)
        host = result['host']
        assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert host['lifetime_process_commit_peak'] <= job.peak_process_commit <= cap
        assert host['job_commit_peak'] <= job.peak_job_commit <= cap
        assert host['process_user_100ns'] <= job.user_100ns and host['process_kernel_100ns'] <= job.kernel_100ns
        return dict(result, completed_job=asdict(job))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--section', choices=('registration', 'finite_streams', 'installed', 'failures', 'bounded'))
    args = parser.parse_args()
    if args.worker:
        cap = 64 << 20
        result = installed(host=HostResourceContract(cap, {'deployment': cap, 'compiler': cap}))
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
        return
    cases = {name: globals()[name]() for name in ('registration', 'finite_streams', 'installed', 'failures', 'bounded')
             if args.section in (None, name)}
    result = {'status': 'PASS', 'scope': 'owned single-root finite reference run, actual CPU protocol and terminal report',
              'cases': cases, 'not_claimed': ['CERTIFIED_COMPLETE or universal Compiler optimality',
                  'target AMP or full Runtime release', 'cross-root family error control',
                  'host process exit from a Runtime snapshot alone']}
    if args.write:
        assert args.section is None
        (ROOT/'evidence/minimal/FP_REFERENCE_RUN_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
