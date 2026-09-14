"""Owned Compiler strategy: real end-to-end CPU execution and finite adversaries."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import FunctionType
import argparse
import inspect
import json
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CompilationStep
from fp_reference.core import ContractError
from fp_reference.host_failure import HOST_RESOURCE_FAILURE
from fp_reference.host_resources import HostResourceContract, HostExecutionUnresolved, _WindowsProcessHost
from fp_reference.machine import pack
from fp_reference.ingress import encode_context
from fp_reference.native_search import GrammarLimits
from fp_reference.policy import POLICY_EXTERNAL_PORTS
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.runtime as execution
from audit_cpu_installation import configuration, SMALL
from audit_paired_cpu_persistence import config
from audit_reference_construction import limits, rejects, validate_residency, zero_program
from audit_reference_persistence import event, check_gain, wealth_oracle
from audit_float64_runtime import replay
from windows_job_audit_support import run_in_job


STEP = CompilationStep(2, 'native', 10000, 'ref', 'finite')


def make(*, steps=(STEP,), cfg=None, count=40, continued=False, host=None, bounds=SMALL, transform=None):
    cfg, online = configuration(cfg=cfg, count=count, continued=continued, bounds=bounds)
    if transform is not None:
        online = transform(online)  # fixture construction only, before Runtime
    return ReferenceCompilerRuntime(cfg, zero_program(2), online=online, host=host, policy=CompilerPolicy(steps))


def owned(rt):
    snapshot = validate_residency(rt)
    policy = snapshot.compiler_policy
    assert not policy.executing
    assert dict(snapshot.buffers)[policy.state.object_id] == pack(policy.state)
    for receipt in snapshot.install_receipts:
        assert dict(snapshot.buffers)[receipt.object_id] == pack(receipt)
    return snapshot


def forbidden(rt):
    before = rt.snapshot()
    ports = tuple(name for name, value in vars(ReferenceCompilerRuntime).items()
                  if type(value) is FunctionType and not name.startswith('_') and name not in POLICY_EXTERNAL_PORTS)
    for name in ports:
        rejects(lambda: getattr(rt, name)())
    after = rt.snapshot()
    # Kernel observations themselves can change; all owned recorded state is
    # otherwise unchanged, including resource work and proposal revision.
    assert replace(after, host_resources=None) == replace(before, host_resources=None)
    return len(ports)


def success(*, host=None, learned=False):
    cfg = config(cap=10, peak=10, pattern=(F(2),)) if learned else None
    if learned:
        cfg = replace(cfg, limits=limits(500_000_000, 2_000_000_000))
    steps = (STEP,) if learned else (STEP, CompilationStep(24, 'next', 10000, 'ref-next', 'finite-next'))
    rt = make(steps=steps, cfg=cfg, count=80, continued=not learned, host=host,
              bounds=GrammarLimits(3, 2, 0, 1, 1) if learned else SMALL)
    denied, publications = forbidden(rt), []
    prior_deployed = rt.snapshot().deployed_id

    def observe_publication(frame, event_kind, arg):
        nonlocal prior_deployed
        if frame.f_code.co_name != 'install_cpu':
            return None
        if frame.f_code.co_name == 'install_cpu' and event_kind in ('line', 'return'):
            current = rt._deployed_id
            if current != prior_deployed:
                completed = [stage for stage in rt._policy_state.stages
                             if stage.status == 'INSTALLED_CPU' and stage.candidate_id == current]
                assert completed and completed[-1].install_attempt == rt._install_receipts[-1].attempt.attempt_id
                assert rt._policy_state.object_id in rt._buffers
                publications.append(rt._cursor)
                prior_deployed = current
        return observe_publication

    tape = (0,)*20 if learned else (0,)*22+(1,)*16+(0, 1)
    # Trace only reads the owning object. It supplies no transition values.
    sys.settrace(observe_publication)
    try:
        for cursor, target in enumerate(tape):
            event(rt, target)
            if cursor in (1, 21, 37):
                denied += forbidden(rt)
    finally:
        sys.settrace(None)
    snapshot = owned(rt)
    assert snapshot.halted is None
    expected = (18,) if learned else (22, 38)
    assert tuple(publications) == tuple(r.attempt.cursor for r in snapshot.install_receipts) == expected
    assert all(stage.status == 'INSTALLED_CPU' for stage in snapshot.compiler_policy.state.stages)
    assert snapshot.alpha_spent == (F(1, 2) if learned else F(3, 4))
    classes = [len(session.rows) for session in snapshot.searches]
    assert classes == ([774] if learned else [35, 35])
    if learned:
        target = next(s for s in snapshot.candidates if s.candidate_id == snapshot.deployed_id)
        assert target.theta and target.theta != tuple(cfg.initializer_pattern[i % len(cfg.initializer_pattern)] for i in range(len(target.theta)))
    checked, _, _ = replay(rt)
    result = {'native_class_sizes': classes, 'installed_at_cursors': publications,
              'policy_and_learner_publish_in_same_root': True, 'external_control_ports_denied': denied,
              'only_context_and_target_input_drives_compilation': True,
              'global_alpha_spent': str(snapshot.alpha_spent), 'independent_binary64_phase_checks': checked,
              'continued_after_install': snapshot.cursor > publications[-1], 'nonzero_trained_install': learned}
    if host is not None:
        measured = rt.snapshot().host_resources
        result['host'] = {name: getattr(measured, name) for name in ('process_id', 'creation_100ns',
            'lifetime_process_commit_peak', 'job_commit_peak', 'process_user_100ns', 'process_kernel_100ns')}
    return result


def registration():
    cfg, online = configuration()
    rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), policy=CompilerPolicy((STEP,))))
    rejects(lambda: CompilationStep(2, 'native', True, 'ref', 'finite'))
    rejects(lambda: CompilerPolicy((STEP, replace(STEP, after_cursor=1))))
    for step in (replace(STEP, search_name='undeclared'), replace(STEP, after_cursor=1),
                 replace(STEP, reference_rule='finite'), replace(STEP, after_cursor=100)):
        rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), online=online, policy=CompilerPolicy((step,))))
    rt = make()
    for value in (True, {}, lambda: None, rt.snapshot().compiler_policy, rt.snapshot().compiler_policy.state):
        rejects(lambda: ReferenceCompilerRuntime(cfg, zero_program(2), online=online, policy=value))
    external = ReferenceCompilerRuntime(cfg, zero_program(2), online=online)
    assert external.chi != rt.chi and external.snapshot().compiler_policy is None
    baseline = make(steps=())
    for target in (0, 1, 0, 1):
        prediction, _ = event(baseline, target)
        assert all(values == (F(1, 2), F(1, 2)) for values in dict(prediction.predictions).values())
    state = owned(baseline)
    assert state.compiler_policy.state.stages == () and not state.searches and state.alpha_spent == 0
    forbidden(baseline)
    return {'invalid_boundary_class_rule_budget_and_supplied_execution_rejected': 12,
            'manual_control_mode_explicitly_has_different_claim_identity': True,
            'empty_strategy_is_a_closed_ordinary_baseline': True}


def exhaustive():
    def short(online):
        rules = tuple(replace(rule, max_epochs=4, alpha=F(5, 12), bound=F(9, 8), bet=F(99, 100)) for rule in online.persistence.rules)
        return replace(online, persistence=replace(online.persistence, alpha_total=F(9, 10), rules=rules))
    counts = {'BASELINE_SELECTED': 0, 'UNRESOLVED': 0, 'INSTALLED_CPU': 0}
    gains = checks = 0
    for targets in product(range(2), repeat=6):
        rt = make(count=6, transform=short)
        for target in targets:
            event(rt, target)
        snapshot = owned(rt)
        assert snapshot.halted is None
        stage = snapshot.compiler_policy.state.stages[0]
        # Independent three-prediction oracle for this existing 35-program
        # class: (1/3,2/3), (1/2,1/2), (2/3,1/3), with incumbent on ties.
        if targets[0] != targets[1]:
            expected, alpha = 'BASELINE_SELECTED', F(0)
        else:
            expected = 'INSTALLED_CPU' if len(set(targets)) == 1 else 'UNRESOLVED'
            alpha = F(5, 6)
        assert stage.status == expected and snapshot.alpha_spent == alpha
        counts[stage.status] += 1
        by_id = {item.identity_id: item for item in snapshot.persistence_identities}
        wealth = {key: F(1) for key in by_id}
        for item in snapshot.persistence_events:
            check_gain(item)  # independent exact log enclosure
            rule = by_id[item.identity_id].rule
            assert item.epoch_finished
            wealth[item.identity_id] = wealth_oracle(wealth[item.identity_id], item.gain.lower, 1, rule)
            assert item.wealth_after == wealth[item.identity_id]
            gains += 1
        for key, value in wealth.items():
            assert by_id[key].wealth == value
        checks += 1
    assert counts == {'BASELINE_SELECTED': 32, 'UNRESOLVED': 30, 'INSTALLED_CPU': 2}
    return {'all_six_label_streams': checks, 'outcomes': counts, 'independent_log_and_exact_wealth_checks': gains}


def failures():
    cfg, online = configuration()
    manual = ReferenceCompilerRuntime(cfg, zero_program(2), online=online)
    with patch.object(ReferenceCompilerRuntime, '_range', side_effect=HostExecutionUnresolved('injected native-premise loss inside construction')):
        rejects(lambda: manual.construct_candidate(zero_program(2)), HostExecutionUnresolved)
    assert manual.snapshot().halted == HOST_RESOURCE_FAILURE
    # Host premise loss is not a bad graph/argument: a ContractError catch
    # must not convert it into INADMISSIBLE_REFERENCE and continue execution.
    rejects(lambda: manual.construct_candidate(zero_program(2)))

    rt = make()
    event(rt, 0)
    assert rt.predict_next('observation-1', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
    with patch.object(execution, 'commit_event', side_effect=ArithmeticUnresolved('injected ordinary commit uncertainty')):
        result = rt.observe(0)
    ordinary = owned(rt)
    assert result.status == 'UNRESOLVED' and ordinary.cursor == 1 and len(ordinary.observations) == 2
    assert ordinary.compiler_policy.state.stages[0].status == 'WAITING'
    assert not ordinary.searches and ordinary.alpha_spent == 0

    rt = make(steps=(replace(STEP, search_transitions=1),))
    for _ in range(4):
        event(rt, 0)
    short = owned(rt)
    assert short.compiler_policy.state.stages[0].status == 'UNRESOLVED'
    assert short.searches[0].status == 'CANCELLED' and not short.reference_proofs and short.alpha_spent == 0
    assert len(short.searches) == 1
    forbidden(rt)

    rt = make(steps=(STEP, replace(STEP, after_cursor=4)),
              transform=lambda online: replace(online, persistence=replace(online.persistence, alpha_total=F(1, 4))))
    for _ in range(6):
        event(rt, 0)
    exhausted = owned(rt)
    assert [s.status for s in exhausted.compiler_policy.state.stages] == ['UNRESOLVED', 'UNRESOLVED']
    assert exhausted.alpha_spent == F(1, 4) and len(exhausted.alpha_allocations) == 1
    assert not exhausted.install_receipts

    rt = make()
    event(rt, 0)
    save = ReferenceCompilerRuntime._save_policy
    def failed_metadata(self, stages):
        if stages[0].status == 'ADMITTING_FLOAT64':
            raise ResourceExceeded('injected policy storage refusal after reference admission')
        return save(self, stages)
    with patch.object(ReferenceCompilerRuntime, '_save_policy', failed_metadata):
        event(rt, 0)
    failed = owned(rt)
    assert failed.halted[0] == 'compiler-policy' and failed.cursor == 2
    assert len(failed.observations) == 2 and failed.alpha_spent == F(1, 4)
    assert failed.compiler_policy.state.stages[0].status == 'ADMITTING_REFERENCE'
    rejects(lambda: event(rt, 0))

    rt = make()
    for _ in range(21):
        event(rt, 0)
    previous = rt.snapshot()
    allocate = ReferenceCompilerRuntime._allocate
    def failed_install_policy(self, owner, objects):
        if owner.endswith(':workspace') and any(obj.spec.kind == 'owned_compiler_policy' for obj in objects):
            raise ResourceExceeded('injected policy publication buffer refusal')
        return allocate(self, owner, objects)
    with patch.object(ReferenceCompilerRuntime, '_allocate', failed_install_policy):
        event(rt, 0)
    aborted = owned(rt)
    assert aborted.halted is None and aborted.deployed_id == previous.deployed_id and not aborted.install_receipts
    assert aborted.compiler_policy.state.stages[0].status == 'UNRESOLVED'
    assert aborted.compiler_policy.state.stages[0].install_attempt == aborted.install_attempts[-1].attempt_id
    assert aborted.alpha_spent == F(1, 2)
    event(rt, 0)
    return {'native_premise_loss_cannot_be_misclassified_as_graph_inadmissibility': True,
            'failed_ordinary_commit_retains_target_without_advancing_policy': True,
            'search_allowance_exhaustion_not_completeness': True,
            'two_policy_stages_cannot_reuse_one_alpha_allocation': True,
            'failed_policy_retention_keeps_observation_and_spent_alpha_without_retry': True,
            'policy_buffer_failure_aborts_complete_install_before_publication': True}


def native_failure(host):
    rt = make(host=host)
    for _ in range(21):
        event(rt, 0)
    deployed = rt.snapshot().deployed_id
    observe = _WindowsProcessHost.observe
    hits = []
    def lost_premise(self):
        caller = inspect.currentframe().f_back
        # Lose a real backend premise at the nested public relation read
        # inside install, after admission/work but before root publication.
        if (caller.f_code.co_name == 'guarded'
                and caller.f_back.f_code is ReferenceCompilerRuntime._install_owned.__code__):
            hits.append(True)
            raise HostExecutionUnresolved('injected loss of nested native observation')
        return observe(self)
    with patch.object(_WindowsProcessHost, 'observe', lost_premise):
        rejects(lambda: event(rt, 0), HostExecutionUnresolved)
    snapshot = owned(rt)
    assert len(hits) == 1 and snapshot.halted == HOST_RESOURCE_FAILURE
    assert snapshot.deployed_id == deployed and not snapshot.install_receipts and snapshot.alpha_spent == F(1, 2)
    assert snapshot.event_phase == 'halted' and snapshot.cursor == 22
    assert snapshot.install_attempts[-1].status == 'PREPARING'
    rejects(lambda: event(rt, 0))
    return {'nested_native_premise_loss_preserves_terminal_marker_without_allocating_cleanup': True,
            'last_ordinary_event_retained': snapshot.cursor, 'alpha_spent': str(snapshot.alpha_spent)}


def bounded():
    cap = 64 << 20
    with tempfile.TemporaryDirectory(prefix='fp-owned-policy-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        path = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--worker', '--output', path), commit_limit=cap)
        assert job.exit_code == 0 and not job.timed_out, job
        with path.open('rb') as source:
            content = source.read(8193)
        assert len(content) <= 8192
        result = json.loads(content)
        measured = result['success']['host']
        assert (measured['process_id'], measured['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert measured['lifetime_process_commit_peak'] <= job.peak_process_commit <= cap
        assert measured['job_commit_peak'] <= job.peak_job_commit <= cap
        return {'worker': result, 'job': asdict(job)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=('registration', 'success', 'learned', 'exhaustive', 'failures', 'bounded'))
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker:
        host = HostResourceContract(128 << 20, {'deployment': 96 << 20, 'compiler': 64 << 20})
        result = {'success': success(host=host), 'native_failure': native_failure(host)}
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
        return
    sections = {'registration': registration, 'success': success, 'learned': lambda: success(learned=True), 'exhaustive': exhaustive,
                'failures': failures, 'bounded': bounded}
    result = {'status': 'PASS', 'scope': 'registered owned sequential native-class Compiler strategy on actual CPU Runtime'}
    result.update({key: run() for key, run in sections.items() if args.section is None or key == args.section})
    result['not_closed'] = ['arbitrary adaptive policy/value classes or target AMP',
                            'complete ERC-1 run/publication and release-gate mapping', 'multi-run error-family authority']
    if args.write:
        assert args.section is None
        (ROOT/'evidence/minimal/FP_OWNED_COMPILER_POLICY_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
