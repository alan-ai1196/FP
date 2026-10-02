"""Host-allocation terminal authority, historical replay and real OS refusal.

Fault injection changes an allocation site in trusted code, never Runtime's
owned state. The Windows child additionally executes a real memory refusal
inside unmodified begin_context under an independently enforced commit cap.
"""
from dataclasses import asdict, fields, replace
from pathlib import Path
from types import FunctionType
import argparse
import ast
import json
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

import fp_reference.runtime as execution
from fp_reference.core import ContractError
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
from fp_reference.ingress import IngressContract, encode_context
from fp_reference.resources import ResourceLedger
from audit_control_admission import historical_modules
from audit_reference_construction import contract, limits, rejects, validate_residency, zero_program
from audit_reference_events import online
from audit_cpu_installation import fixture as install_fixture, install
from audit_reference_search import runtime_fixture as search_fixture
from windows_job_audit_support import run_in_job


HISTORICAL = 'dfa1583'


def fixture(module=execution, *, prime=True):
    cfg = contract()
    cfg = module.ConstructionContract(**{f.name: getattr(cfg, f.name) for f in fields(module.ConstructionContract) if f.init})
    run = online(cfg, 4, unit=1)
    run = module.OnlineContract(**{f.name: getattr(run, f.name) for f in fields(module.OnlineContract) if f.init})
    rt = module.ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    if prime:
        assert rt.predict_next('observation-0', encode_context((1, 0))).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    return rt


def history_audit():
    old = historical_modules(HISTORICAL, ('fp_reference.machine', 'fp_reference.runtime'))['fp_reference.runtime']
    rt = fixture(old)
    before = rt.snapshot()
    with patch.object(old, 'ConstructionResult', side_effect=MemoryError('injected result allocation')):
        rejects(lambda: rt.construct_candidate(zero_program(2)), MemoryError)
    failed = rt.snapshot()
    orphan = next(s for s in failed.candidates if s.candidate_id != before.deployed_id)
    assert orphan.physical_owner in failed.resources['closed_owners']
    assert not any(key in failed.resources['objects'] for key in orphan.object_ids)
    assert failed.event_phase == 'idle'
    prediction = rt.predict_next('observation-1', encode_context((1, 0)))
    assert prediction.status == 'PREDICTED_REFERENCE'
    assert orphan.candidate_id in dict(prediction.predictions)
    rt = fixture()
    with patch.object(execution, 'ConstructionResult', side_effect=MemoryError('injected result allocation')):
        rejects(lambda: rt.construct_candidate(zero_program(2)), MemoryError)
    retained = validate_residency(rt)
    assert retained.halted == HOST_ALLOCATION_FAILURE and retained.event_phase == 'halted'
    rejects(lambda: rt.predict_next('observation-1', encode_context((1, 0))))
    assert rt.snapshot() == retained
    return {'source_commit': HISTORICAL, 'failure_site': 'construction result allocation after publication',
            'historical_candidate_lost_all_owned_learner_buffers': True,
            'historical_next_public_prediction_used_that_candidate': True,
            'current_prefix_retained_without_cleanup_or_continuation': True}


def ports_audit():
    rt = fixture()
    with patch.object(execution, 'ConstructionResult', side_effect=MemoryError):
        rejects(lambda: rt.construct_candidate(zero_program(2)), MemoryError)
    failed = rt.snapshot()
    ports = tuple(name for name, value in vars(execution.ReferenceCompilerRuntime).items()
                  if not name.startswith('_') and type(value) is FunctionType and name != 'snapshot')
    for name in ports:
        # Guard precedes argument decoding and every action/result authority.
        for _ in range(16):
            rejects(lambda: getattr(rt, name)())
        assert rt.snapshot() == failed
    tree = ast.parse((ROOT/'src/reference_compiler/fp_reference/runtime.py').read_text(encoding='utf-8'))
    broad = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for index, handler in enumerate(node.handlers):
                if isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                    assert index > 0
                    prior = node.handlers[index-1]
                    assert isinstance(prior.type, ast.Name) and prior.type.id == 'MemoryError'
                    assert len(prior.body) == 1 and isinstance(prior.body[0], ast.Raise) and prior.body[0].exc is None
                    broad += 1
    return {'guarded_continuation_or_authority_ports': len(ports), 'repeated_terminal_refusals': len(ports)*16,
            'internal_allocation_failures_bypass_broad_handlers': broad,
            'refusals_do_not_grow_or_rewrite_owned_state': True}


def prefix_audit():
    cases = 0
    # The result-allocation boundary is after publication in these operations.
    for result_name, action in (
        ('IngressResult', lambda rt: rt.begin_context('observation-1')),
        ('PredictionResult', lambda rt: rt.predict_next('observation-1', encode_context((1, 0)))),
        ('ObservationResult', lambda rt: rt.observe(0)),
        ('RuntimeSnapshot', lambda rt: rt.snapshot()),
    ):
        rt = fixture()
        if result_name == 'ObservationResult':
            rt.predict_next('observation-1', encode_context((1, 0)))
        before = rt.snapshot()
        with patch.object(execution, result_name, side_effect=MemoryError):
            rejects(lambda: action(rt), MemoryError)
        after = rt.snapshot()
        assert after.halted == HOST_ALLOCATION_FAILURE and after.event_phase == 'halted'
        assert after.alpha_spent == before.alpha_spent and after.cursor >= before.cursor
        assert after.observations[:len(before.observations)] == before.observations
        assert after.resources['spent']['compiler']['work'] >= before.resources['spent']['compiler']['work']
        cases += 1
    # Resource publication can precede a failing history record allocation.
    rt = fixture()
    before = rt.snapshot()
    with patch.object(ResourceLedger, '_event', side_effect=MemoryError):
        rejects(lambda: rt.construct_candidate(zero_program(2)), MemoryError)
    after = rt.snapshot()
    assert after.halted == HOST_ALLOCATION_FAILURE
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    # A read-only snapshot failure cannot leave a current proof port active.
    rt, _ = search_fixture()
    result = rt.start_reference_search('native')
    result = rt.advance_reference_search(result.search_id, transitions=10000)
    assert result.proof_id is not None
    with patch.object(execution, 'RuntimeSnapshot', side_effect=MemoryError):
        rejects(rt.snapshot, MemoryError)
    rejects(lambda: rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id))
    assert rt.snapshot().reference_proofs  # retained historical evidence
    # Actual dual persistence survives as history, without current authority;
    # installation failure cannot refund alpha or rebase the deployed learner.
    rt, selected, ids = install_fixture()
    before = rt.snapshot()
    with patch.object(execution, 'CpuInstallResult', side_effect=MemoryError):
        rejects(lambda: install(rt, selected, ids), MemoryError)
    after = rt.snapshot()
    assert after.halted == HOST_ALLOCATION_FAILURE
    assert after.deployed_id == before.deployed_id and after.alpha_spent == before.alpha_spent > 0
    assert after.candidates == before.candidates and after.persistence_identities == before.persistence_identities
    role = rt.online_contract.cpu_install.work_role
    assert after.resources['spent'][role]['work'] > before.resources['spent'][role]['work']
    rejects(lambda: rt.paired_persistence_result(*ids))
    rejects(lambda: install(rt, selected, ids))
    return {'event_and_snapshot_result_failures': cases, 'paid_ledger_history_allocation_failure': True,
            'historical_class_proof_retained_but_current_authority_closed': True,
            'failed_cpu_install_retains_deployment_learners_persistence_alpha_and_work': True,
            'construction_writer_and_ledger_event_sweep': allocation_site_audit()}


def allocation_site_audit():
    counts = {}
    unfinished_reservation_cases = unreleased_buffer_cases = 0
    for label, module, attribute in (('packed_writers', execution, 'write_packed'),
                                      ('ledger_events', ResourceLedger, '_event')):
        original = getattr(module, attribute)
        seen = 0
        def count(*args, **kwargs):
            nonlocal seen
            seen += 1
            return original(*args, **kwargs)
        rt = fixture()
        with patch.object(module, attribute, count):
            assert rt.construct_candidate(zero_program(2)).status == 'BUILT_REFERENCE'
        counts[label] = seen
        for position in range(1, seen+1):
            reached = 0
            def fail(*args, **kwargs):
                nonlocal reached
                reached += 1
                if reached == position:
                    if label == 'packed_writers':
                        args[1][0] = 91  # actual admitted partial buffer write
                    raise MemoryError('injected allocation site')
                return original(*args, **kwargs)
            rt = fixture()
            before = rt.snapshot()
            with patch.object(module, attribute, fail):
                rejects(lambda: rt.construct_candidate(zero_program(2)), MemoryError)
            after = rt.snapshot()
            assert reached == position and after.halted == HOST_ALLOCATION_FAILURE
            assert after.candidates == before.candidates and after.observations == before.observations
            assert after.alpha_spent == before.alpha_spent
            for key, payload in before.buffers:
                assert dict(after.buffers)[key] == payload
            for role, costs in before.resources['spent'].items():
                assert after.resources['spent'][role]['work'] >= costs['work']
            # Interrupted admission may lack a finished buffer; interrupted
            # release may leave a buffer after the ledger lease was removed.
            # Neither terminal prefix is a valid continuation snapshot.
            buffers, objects = dict(after.buffers), after.resources['objects']
            unfinished_reservation_cases += bool(set(objects)-set(buffers))
            unreleased_buffer_cases += bool(set(buffers)-set(objects))
            for key in set(buffers) & set(objects):
                assert objects[key]['residency']['reference_payload_bytes'] == len(buffers[key])
            rejects(lambda: rt.predict_next('observation-1', encode_context((1, 0))))
            assert rt.snapshot() == after
    assert unfinished_reservation_cases and unreleased_buffer_cases
    return dict(counts, terminal_unfinished_reservation_cases=unfinished_reservation_cases,
                terminal_unreleased_buffer_cases=unreleased_buffer_cases)


def worker(output):
    # Work/payload caps permit the declared 128 MiB context window. The fixed
    # external 64 MiB OS job denies its actual allocation; no monkeypatch or
    # synthetic ResourceExceeded supplies this MemoryError.
    cfg = replace(contract(), limits=limits(byte_cap=1 << 30, work_cap=1 << 34))
    run = online(cfg, 2, unit=1)
    run = replace(run, data=replace(run.data, ingress=IngressContract(capacity=1 << 27, chunk_bytes=64)))
    rt = execution.ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    before = rt.snapshot()
    error = None
    try:
        rt.begin_context('observation-0')
    except MemoryError:
        error = 'MemoryError'
    after = rt.snapshot()
    assert error == 'MemoryError' and after.halted == HOST_ALLOCATION_FAILURE
    assert after.cursor == 0 and after.pending is None and not after.observations
    assert after.candidates == before.candidates
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    rejects(lambda: rt.begin_context('observation-0'))
    result = {'status': 'PASS', 'actual_exception': error, 'requested_context_window': 1 << 27,
              'packed_cap_permitted_window': True, 'terminal_before_first_input_byte': True,
              'paid_work_after_failure': after.resources['spent']['compiler']['work'],
              'packed_peak_after_failure': after.resources['peak']['reference_payload_bytes']}
    Path(output).write_text(json.dumps(result), encoding='utf-8')


def os_audit():
    with tempfile.TemporaryDirectory(prefix='fp-host-audit-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        run = run_in_job(__file__, ('--worker', output), commit_limit=1 << 26)
        assert not run.timed_out and run.exit_code == 0, run
        result = json.loads(output.read_text(encoding='utf-8'))
        assert result['status'] == 'PASS'
        assert 0 < run.peak_process_commit <= run.commit_limit
        assert 0 < run.peak_job_commit <= run.commit_limit
        # SDK TotalProcesses includes failed job associations. Even an empty
        # Python worker here records two associations. Do not infer their
        # individual origin or count only our explicitly launched worker.
        assert run.total_processes >= 1 and run.user_100ns+run.kernel_100ns > 0
        assert 0 <= run.limit_terminated_processes < run.total_processes
        return {'child': result, 'windows_job': asdict(run),
                'scope': 'child job committed memory and measured CPU time; not total host memory, role attribution or full ERC-1 enforcement'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('history', 'ports', 'prefixes', 'os'))
    parser.add_argument('--worker')
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    sections = {'history': history_audit, 'ports': ports_audit, 'prefixes': prefix_audit, 'os': os_audit}
    if args.section:
        print(json.dumps(sections[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'terminal public Runtime authority on host allocation exhaustion',
              **{name: fn() for name, fn in sections.items()},
              'not_closed': ['full host resource enforcement/role accounting', 'complete ERC-1 and Runtime release', 'actual AMP and GPU science']}
    if args.write:
        (ROOT/'evidence/minimal/FP_HOST_ALLOCATION_FAILURE_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
