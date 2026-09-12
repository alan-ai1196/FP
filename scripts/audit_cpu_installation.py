"""Actual owned CPU install transactions and an independent lease oracle."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'theory/numerical_checks')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract
from fp_reference.installation import CpuInstallContract
from fp_reference.machine import pack
from fp_reference.native_search import GrammarLimits
from fp_reference.resources import ObjectSpec, ResourceLedger, ResourceLimits, ResourceExceeded
from fp_reference.search import ReferenceSearchSpec
from fp_reference.semantics import ArithmeticUnresolved
from audit_paired_cpu_persistence import config, registration, pair
from audit_reference_construction import domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import online, shared_graph
from audit_reference_persistence import event, identity
from audit_float64_runtime import replay


SMALL = GrammarLimits(2, 1, 0, 0, 0)


def fixture(*, cfg=None, install=None, bounds=SMALL, count=40, discovery=True, continued=False, host=None):
    cfg = config(cap=4, peak=1) if cfg is None else cfg
    run = replace(online(cfg, count, unit=2, rate=F(1, 8), grid=16),
        float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)),
        cpu_install=CpuInstallContract() if install is None else install,
        persistence=registration(bound=F(3), horizon=30),
        searches=(ReferenceSearchSpec('native', bounds, ('observation-0', 'observation-1')),))
    run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external branch-invariant audit producer')))
    if continued:
        # Both later proposal observations and the new alpha rules are fixed
        # before the first Runtime event, not selected after seeing a result.
        run = replace(run, searches=run.searches+(
            ReferenceSearchSpec('next', bounds, ('observation-22', 'observation-23')),),
            persistence=replace(run.persistence, rules=run.persistence.rules+tuple(
                replace(rule, rule_id=rule.rule_id+'-next', alpha=F(1, 8)) for rule in run.persistence.rules)))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run, host=host)
    if not discovery:
        return rt
    event(rt, 0)
    event(rt, 0)
    search = rt.start_reference_search('native')
    search = rt.advance_reference_search(search.search_id, transitions=10000)
    assert search.status == 'REFERENCE_CLASS_EXHAUSTED', search
    ids = pair(rt, search.best_candidate_id)
    for _ in range(30):
        event(rt, 0)
        if rt.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED' and rt.snapshot().cursor % 2 == 0:
            break
    assert rt.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED'
    return rt, search, ids


def install(rt, search, ids, **kwargs):
    args = dict(proposal_proof_id=search.proof_id, reference_identity=ids[0], float64_identity=ids[1])
    args.update(kwargs)
    return rt.install_cpu(search.best_candidate_id, **args)


def ownership(rt):
    state = validate_residency(rt)
    buffers = dict(state.buffers)
    for receipt in state.install_receipts:
        assert buffers[receipt.object_id] == pack(receipt)
        assert receipt.attempt.status == 'INSTALLED_CPU'
    for current in state.candidates:
        role = 'deployment' if current.candidate_id == state.deployed_id else 'compiler'
        assert state.resources['owners'][current.physical_owner] == role
        assert current.physical_owner not in state.resources['closed_owners']
        assert buffers[current.object_ids[1]] == pack((current.learner, current.float64))
    return state


def ledger_audit():
    cases = successes = 0
    owners = ('a', 'b')
    for counts in product(range(3), repeat=4):
        refs = {'x': dict(zip(owners, counts[:2])), 'y': dict(zip(owners, counts[2:]))}
        refs = {obj: {owner: count for owner, count in entries.items() if count} for obj, entries in refs.items()}
        if not all(refs.values()):
            continue
        for cap_a, cap_b in product(range(1, 4), repeat=2):
            caps = {'a': cap_a, 'b': cap_b}
            if any(sum((1 if obj == 'x' else 2) for obj in refs if owner in refs[obj]) > caps[owner] for owner in owners):
                continue
            declared = ResourceLimits({'bytes': 3}, {o: {'bytes': caps[o]} for o in owners}, {o: {'work': 100} for o in owners})
            ledger = ResourceLedger(declared)
            for owner in owners:
                ledger.register_owner(owner, owner)
            for obj, values in refs.items():
                first = next(iter(values))
                ledger.allocate(first, (ObjectSpec(obj, 'payload', {'bytes': 1 if obj == 'x' else 2}, 'fixed-audit'),))
                for owner, count in values.items():
                    additional = count-int(owner == first)
                    if additional:
                        ledger.acquire(owner, obj, count=additional)
            operations = [((a, b, obj, n),) for a, b in (('a', 'b'), ('b', 'a')) for obj in refs for n in (1, 2)]
            operations += [(('a', 'b', 'x', n), ('b', 'a', 'y', n)) for n in (1, 2)]
            operations += [(('a', 'b', 'x', 1), ('a', 'b', 'x', 1)),
                           (('a', 'b', 'x', 1), ('b', 'a', 'x', 2))]
            for moves in operations:
                previous = ledger.snapshot()
                debits = {}
                for a, b, obj, n in moves:
                    debits[(a, obj)] = debits.get((a, obj), 0)+n
                valid = all(refs[obj].get(owner, 0) >= n for (owner, obj), n in debits.items())
                expected = {obj: dict(value) for obj, value in refs.items()}
                if valid:
                    for (owner, obj), n in debits.items():
                        expected[obj][owner] -= n
                    for a, b, obj, n in moves:
                        expected[obj][b] = expected[obj].get(b, 0)+n
                    expected = {obj: {o: n for o, n in value.items() if n} for obj, value in expected.items()}
                    valid = all(sum((1 if obj == 'x' else 2) for obj in expected if owner in expected[obj]) <= caps[owner] for owner in owners)
                if not valid:
                    rejects(lambda: ledger.prepare_transfer(moves))
                else:
                    result = ledger.prepare_transfer(moves).snapshot()
                    assert {obj: dict(value['references']) for obj, value in result['objects'].items()} == expected
                    assert result['current']['bytes'] == 3 and result['spent'] == previous['spent']
                    successes += 1
                assert ledger.snapshot() == previous
                cases += 1
    # Simultaneous role exchange fits; an acquire-first implementation does not.
    caps = ResourceLimits({'bytes': 2}, {'dep': {'bytes': 1}, 'compiler': {'bytes': 1}},
        {'dep': {'work': 10}, 'compiler': {'work': 10}})
    ledger = ResourceLedger(caps)
    for owner, role in (('old', 'dep'), ('candidate', 'compiler'), ('new-dep', 'dep'), ('new-shadow', 'compiler')):
        ledger.register_owner(owner, role)
    ledger.allocate('old', (ObjectSpec('x', 'payload', {'bytes': 1}, 'fixed'),))
    ledger.allocate('candidate', (ObjectSpec('y', 'payload', {'bytes': 1}, 'fixed'),))
    rejects(lambda: ledger.acquire('new-dep', 'y'), ResourceExceeded)
    after = ledger.prepare_transfer((('old', 'new-shadow', 'x', 1), ('candidate', 'new-dep', 'y', 1)),
        close_owners=('old', 'candidate'))
    assert after.snapshot()['current']['bytes'] == after.snapshot()['peak']['bytes'] == 2
    rejects(lambda: after.acquire('old', 'x'))
    rejects(lambda: ledger.prepare_transfer((('old', 'candidate', 'x', 1),), (('old', 'x', 1),)))
    rejects(lambda: ledger.prepare_transfer((), close_owners=('old',)))
    ledger._unaccounted_state = []
    rejects(lambda: ledger.prepare_transfer(()))
    return {'independent_complete_lease_cases': cases, 'feasible_atomic_transfers': successes,
            'original_ledger_unchanged_on_every_prepare': True,
            'acquire_first_false_rejection_and_atomic_role_exchange_checked': True,
            'lease_laundering_overrelease_closed_owner_and_unknown_state_rejected': True}


def success_audit(*, learned=False):
    bounds = GrammarLimits(3, 2, 0, 1, 1) if learned else SMALL
    cfg = config(cap=10, peak=10, pattern=(F(2),)) if learned else config(cap=4, peak=1)
    cfg = replace(cfg, limits=limits(500_000_000, 2_000_000_000))
    rt, search, ids = fixture(cfg=cfg, bounds=bounds)
    # Add a paused owned frontier after crossing. Installation must close it
    # while preserving every paid row, cursor and code lease.
    pending_search = rt.start_reference_search('native')
    before = ownership(rt)
    buffers = dict(rt._buffers)
    base = next(s for s in before.candidates if s.candidate_id == before.deployed_id)
    target = next(s for s in before.candidates if s.candidate_id == search.best_candidate_id)
    if learned:
        assert target.theta and target.theta != target.learner.gradient_sum
        assert target.theta != tuple(cfg.initializer_pattern[i % len(cfg.initializer_pattern)] for i in range(len(target.theta)))
    rejects(lambda: rt.reference_class_proof(search.proof_id, decision_class_id=search.decision_class_id))
    observed_roots = []
    def observe_publication(frame, event_kind, arg):
        if frame.f_code is ReferenceCompilerRuntime.install_cpu.__code__ and event_kind in ('line', 'return'):
            # Observational instrumentation only; ordinary API calls remain
            # serialized. No callback supplies any state to the transaction.
            current = rt._deployed_id
            if not observed_roots or observed_roots[-1] != current:
                observed_roots.append(current)
            if current == target.candidate_id:
                assert rt._event_phase == 'idle'
                assert rt._candidates[target.candidate_id].physical_owner != target.physical_owner
                assert all(v.status not in ('ACTIVE', 'REFERENCE_CROSSED', 'FLOAT64_CROSSED') for v in rt._persistence_identities.values())
                assert all(v.status == 'CLOSED_BY_INSTALL' for v in rt._searches.values())
        return observe_publication
    sys.settrace(observe_publication)
    try:
        result = install(rt, search, ids)
    finally:
        sys.settrace(None)
    assert result.status == 'INSTALLED_CPU', result
    after = ownership(rt)
    assert observed_roots == [base.candidate_id, target.candidate_id]
    assert after.cursor == before.cursor and after.observations == before.observations
    assert after.data_uses == before.data_uses and after.queries == before.queries
    assert after.float64_traces == before.float64_traces and after.event_traces == before.event_traces
    assert after.alpha_allocations == before.alpha_allocations and after.alpha_spent == before.alpha_spent
    assert after.programs == before.programs and after.retained_programs == before.retained_programs
    for prior in before.candidates:
        current = next(s for s in after.candidates if s.candidate_id == prior.candidate_id)
        assert replace(current, physical_owner=prior.physical_owner) == prior
        assert all(rt._buffers[obj] is buffers[obj] for obj in prior.object_ids)
    receipt = after.install_receipts[-1]
    assert receipt.candidates_before == before.candidates and receipt.candidates_after == after.candidates
    assert rt.paired_persistence_result(*ids).status == 'UNRESOLVED'
    rejects(lambda: rt.reference_class_proof(search.proof_id, decision_class_id=search.decision_class_id))
    paused = next(s for s in before.searches if s.search_id == pending_search.search_id)
    stopped = next(s for s in after.searches if s.search_id == pending_search.search_id)
    assert paused.cursor == stopped.cursor and paused.rows == stopped.rows and stopped.status == 'CLOSED_BY_INSTALL'
    snapshot = rt.snapshot()
    assert rt.advance_reference_search(pending_search.search_id, transitions=100).status == 'UNRESOLVED'
    assert rt.snapshot() == snapshot
    spent = rt.snapshot().resources['spent']
    event(rt, 1)
    event(rt, 0)
    now = ownership(rt)
    assert now.cursor == after.cursor+2
    assert all(now.resources['spent'][r]['work'] > spent[r]['work'] for r in ('deployment', 'compiler'))
    checked, _, _ = replay(rt)
    rt.retire_candidate(base.candidate_id)
    assert all(s.candidate_id != base.candidate_id for s in ownership(rt).candidates)
    return {'complete_native_class_programs': search.programs_compared, 'install_cursor': after.cursor,
            'all_complete_learners_and_actual_buffer_objects_preserved': True,
            'one_complete_root_publication': observed_roots == [base.candidate_id, target.candidate_id],
            'old_evidence_and_paused_frontier_closed_without_refund': True,
            'post_install_events_roles_and_shadow_retirement_checked': True,
            'independent_continuous_binary64_phase_checks': checked, 'nonzero_trained_target': learned}


def failures_audit():
    rt, search, ids = fixture()
    before = ownership(rt)
    rt._unregistered_job_state = {'pending': True}
    blocked = install(rt, search, ids)
    assert blocked.status == 'UNRESOLVED' and 'unregistered Runtime state' in blocked.reason
    assert rt._unregistered_job_state == {'pending': True} and rt.snapshot() == before
    del rt._unregistered_job_state
    # Caller-written identifiers/results cannot replace actual search/evidence.
    bad = install(rt, search, ids, proposal_proof_id='external-fake-proof')
    assert bad.status == 'UNRESOLVED' and rt.snapshot().deployed_id == before.deployed_id
    rejects(lambda: install(rt, search, (ids[1], ids[0])))
    assert rt.snapshot().deployed_id == before.deployed_id
    target = next(s for s in rt.snapshot().candidates if s.candidate_id == search.best_candidate_id)
    copied = rt.construct_candidate(dict(rt.snapshot().programs)[target.program_id]).candidate_id
    counterfeit = rt.install_cpu(copied, proposal_proof_id=search.proof_id,
        reference_identity=ids[0], float64_identity=ids[1])
    assert counterfeit.status == 'UNRESOLVED'
    # A partial optimizer accumulator remains real even after both crossings.
    event(rt, 0)
    partial = rt.snapshot()
    result = install(rt, search, ids)
    assert result.status == 'UNRESOLVED' and rt.snapshot() == partial
    event(rt, 0)
    before = ownership(rt)
    # Abort at the last prepared physical operation: old learners, evidence
    # and frontier remain; the complete attempt/resource history must change.
    with patch.object(ResourceLedger, 'prepare_transfer', side_effect=RuntimeError('injected before complete root publication')):
        rejects(lambda: install(rt, search, ids), RuntimeError)
    failed = ownership(rt)
    assert failed.deployed_id == before.deployed_id and failed.candidates == before.candidates
    assert failed.persistence_identities == before.persistence_identities and failed.searches == before.searches
    assert failed.cursor == before.cursor and failed.observations == before.observations
    assert failed.revision == before.revision+1 and failed.next_install == before.next_install+1
    assert failed.alpha_spent == before.alpha_spent and failed.alpha_allocations == before.alpha_allocations
    assert not failed.install_receipts and failed.install_attempts[-1].status == 'EXECUTION_FAILED'
    assert failed.resources['current'] == before.resources['current']
    assert failed.resources['spent']['deployment']['work'] > before.resources['spent']['deployment']['work']
    assert failed.resources['peak']['reference_payload_bytes'] > before.resources['peak']['reference_payload_bytes']
    assert rt.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED'
    # An aborted attempt creates no transport/rebase and cannot erase spent
    # work, but its still-continuous old learners permit a later paid retry.
    retry = install(rt, search, ids)
    assert retry.status == 'INSTALLED_CPU'
    assert len(ownership(rt).install_receipts) == 1
    return {'fake_proposal_wrong_path_and_partial_unit_rejected': True,
            'unregistered_future_job_coordinate_cannot_inherit_atomic_frame_proof': True,
            'equal_graph_newborn_cannot_inherit_selected_lineage_evidence': True,
            'late_prepare_abort_preserves_old_learners_evidence_and_frontier': True,
            'aborted_work_and_peak_retained_without_alpha_refund': True,
            'paid_retry_preserves_old_trajectory_until_actual_commit': True}


def capacity_audit():
    rt, search, ids = fixture()
    before = ownership(rt)
    observed_sizes = []
    allocate = ReferenceCompilerRuntime._allocate
    def measure(runtime, owner, objects):
        if runtime is rt and any(obj.spec.kind == 'prepared_cpu_install_receipt' for obj in objects):
            observed_sizes.append(rt._ledger.snapshot()['current']['reference_payload_bytes']+sum(obj.spec.residency['reference_payload_bytes'] for obj in objects))
        return allocate(runtime, owner, objects)
    with patch.object(ReferenceCompilerRuntime, '_allocate', measure):
        assert install(rt, search, ids).status == 'INSTALLED_CPU'
    assert len(observed_sizes) == 1 and observed_sizes[0] > before.resources['peak']['reference_payload_bytes']
    byte_cap = observed_sizes[0]-1
    cfg = replace(config(cap=4, peak=1), limits=limits(byte_cap, 100_000_000))
    limited, search, ids = fixture(cfg=cfg)
    old = ownership(limited)
    failure = install(limited, search, ids)
    after = ownership(limited)
    assert failure.status == 'UNRESOLVED' and 'coexistence' in failure.reason
    assert after.deployed_id == old.deployed_id and after.candidates == old.candidates
    assert after.persistence_identities == old.persistence_identities and not after.install_receipts
    assert after.resources['current'] == old.resources['current']
    assert after.resources['peak']['reference_payload_bytes'] <= byte_cap
    assert after.resources['spent']['deployment']['work'] > old.resources['spent']['deployment']['work']
    assert limited.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED'
    # Control admission is paid, then reject before the much larger prepared
    # install work when its registered role lacks capacity.
    charge = 4096+16*sum(len(buf) for _, buf in before.buffers)+1024*(
        len(before.resources['objects'])+len(before.candidates)+len(before.persistence_identities)+len(before.searches))
    work_cap = before.resources['spent']['deployment']['work']+charge-1
    cfg = config(cap=4, peak=1)
    cfg = replace(cfg, limits=replace(cfg.limits, role_cumulative={'deployment': {'work': work_cap}, 'compiler': {'work': 100_000_000}}))
    limited, search, ids = fixture(cfg=cfg)
    old = ownership(limited)
    failure = install(limited, search, ids)
    after = ownership(limited)
    assert failure.status == 'UNRESOLVED' and 'cumulative work' in failure.reason
    assert after.candidates == old.candidates
    assert after.resources['spent']['deployment']['work'] == old.resources['spent']['deployment']['work']+limited._machine.control_admission_work
    assert after.resources['spent']['compiler'] == old.resources['spent']['compiler']
    assert not after.install_receipts and after.alpha_spent == old.alpha_spent
    return {'actual_prepublication_peak_limit_rejects_existing_feasible_target': True,
            'actual_install_work_role_limit_rejects_without_free_execution': True,
            'failed_preparation_keeps_learners_evidence_and_paid_peak_history': True,
            'calibrated_peak_cap': byte_cap}


def continuation_audit():
    rt, first, first_ids = fixture(count=80, continued=True)
    assert rt.snapshot().cursor == 22
    assert install(rt, first, first_ids).status == 'INSTALLED_CPU'
    first_receipt = ownership(rt).install_receipts[0]
    event(rt, 1)
    event(rt, 1)
    next_search = rt.start_reference_search('next')
    next_search = rt.advance_reference_search(next_search.search_id, transitions=10000)
    assert next_search.status == 'REFERENCE_CLASS_EXHAUSTED', next_search
    proposal = rt.reference_class_proof(next_search.proof_id, decision_class_id=next_search.decision_class_id)
    assert proposal.base_lineage_id == first.best_candidate_id
    assert next_search.best_candidate_id != first.best_candidate_id
    ref = rt.admit_reference_persistence(next_search.best_candidate_id, 'ref-next')
    finite = rt.admit_float64_persistence(next_search.best_candidate_id, 'finite-next')
    next_ids = ref.identity_id, finite.identity_id
    assert all(next_ids) and set(next_ids).isdisjoint(first_ids)
    assert all(identity(rt, key).wealth == 1 and identity(rt, key).start_cursor == 24 for key in next_ids)
    for _ in range(30):
        event(rt, 1)
        if rt.paired_persistence_result(*next_ids).status == 'PAIRED_CPU_CROSSED' and rt.snapshot().cursor % 2 == 0:
            break
    assert install(rt, next_search, next_ids).status == 'INSTALLED_CPU'
    current = ownership(rt)
    assert len(current.install_receipts) == 2 and current.install_receipts[0] == first_receipt
    assert current.install_receipts[-1].attempt.old_deployed_id == first.best_candidate_id
    assert current.alpha_spent == F(3, 4) and len(current.alpha_allocations) == 4
    assert rt.paired_persistence_result(*first_ids).status == rt.paired_persistence_result(*next_ids).status == 'UNRESOLVED'
    assert all(session.status == 'CLOSED_BY_INSTALL' for session in current.searches)
    # A third comparison has a live shadow and sufficient fresh horizon, but
    # no alpha. Installing twice cannot make lifetime risk available again.
    exhausted = rt.admit_reference_persistence(first.best_candidate_id, 'ref-next')
    assert exhausted.status == 'UNRESOLVED' and exhausted.identity_id is None and 'global alpha' in exhausted.reason
    assert rt.snapshot().alpha_allocations == current.alpha_allocations
    event(rt, 0)
    event(rt, 1)
    checked, _, _ = replay(rt)
    ownership(rt)
    return {'consecutive_owned_installations': 2,
            'complete_native_classes': [first.programs_compared, next_search.programs_compared],
            'install_cursors': [receipt.attempt.cursor for receipt in current.install_receipts],
            'second_proposal_uses_actual_new_base_and_fresh_identities': True,
            'both_generations_keep_receipts_and_close_old_authority': True,
            'global_alpha_remains_spent_across_both_installations': str(current.alpha_spent),
            'third_admission_refused_without_refund': True,
            'independent_continuous_binary64_phase_checks': checked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('ledger', 'success', 'learned', 'failures', 'capacity', 'continuation'))
    args = parser.parse_args()
    parts = {'ledger': ledger_audit, 'success': success_audit,
             'learned': lambda: success_audit(learned=True), 'failures': failures_audit, 'capacity': capacity_audit,
             'continuation': continuation_audit}
    if args.section:
        print(json.dumps(parts[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'serialized CPU root/lease installation from owned exact proposal and two-path evidence',
        **{key: fn() for key, fn in parts.items()},
        'not_closed': ['concurrent/crash-safe publication', 'full host/device resource accounting', 'target AMP', 'complete ERC-1/Runtime freeze']}
    if args.write:
        (ROOT/'evidence/minimal/FP_CPU_INSTALLATION_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
