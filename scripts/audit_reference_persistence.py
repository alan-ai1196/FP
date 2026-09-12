"""Actual Runtime fresh reference evidence, with independent numerical checks.

These are finite execution audits under explicitly registered external stream
assumptions. They do not infer a stochastic law from test tapes, prove paired
AMP persistence, authorize installation or introduce a static model family.
"""
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'theory/numerical_checks')]

from ingress_audit_support import deliver_context
from fp_reference import ReferenceCompilerRuntime
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.info import Moment, QuerySpec
from fp_reference.ingress import IngressContract
from fp_reference.machine import pack
from fp_reference.persistence import PersistenceContract, PersistenceRule
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Source, Sum, Term
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import forward_oracle, online


SOURCE_PAIR = Program((Source('x0_0'), Source('x0_1')), 0, (0, 1))


def rule(*, epoch=1, horizon=10, alpha=F(1, 4), bound=F(3, 4)):
    return PersistenceRule('future', epoch, horizon, alpha, F(3, 4), bound, 12, 16)


def fixture(*, cfg=None, count=24, registration=None, law=True, graph=SOURCE_PAIR,
            profiles=(), queries=(), ingress=None):
    cfg = contract(cap=3, peak=1) if cfg is None else cfg
    registration = PersistenceContract(F(3, 4), (rule(),)) if registration is None else registration
    run = online(cfg, count, unit=2, rate=F(1, 4), grid=16, queries=queries)
    run = replace(run, profiles=profiles, persistence=registration)
    if ingress is not None:
        run = replace(run, data=replace(run.data, ingress=ingress))
    if law:
        run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('audit external branch-invariant producer assumption')))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    result = rt.construct_candidate(graph)
    assert result.status == 'BUILT_REFERENCE', result
    return rt, result.candidate_id


def identity(rt, identity_id):
    return next(value for value in rt.snapshot().persistence_identities if value.identity_id == identity_id)


def admit(rt, candidate):
    result = rt.admit_reference_persistence(candidate, 'future')
    assert result.identity_id is not None and identity(rt, result.identity_id).status == 'ACTIVE', result
    return result.identity_id


def event(rt, target, context=None):
    cursor = rt.snapshot().cursor
    context = domain(1)[0] if context is None else context
    predicted = deliver_context(rt, f'observation-{cursor}', context)
    assert predicted.status == 'PREDICTED_REFERENCE', predicted
    observed = rt.observe(target)
    assert observed.status == 'OBSERVED_REFERENCE', observed
    return predicted, observed


def owned(rt):
    snapshot = validate_residency(rt)
    buffers = dict(snapshot.buffers)
    for value in snapshot.persistence_identities:
        assert value.object_id and buffers[value.object_id] == pack(value)
        assert value.owner in snapshot.resources['objects'][value.object_id]['references']
    for allocation in snapshot.alpha_allocations:
        assert buffers[allocation.allocation_id] == pack(allocation)
    assert snapshot.alpha_spent == sum((value.alpha for value in snapshot.alpha_allocations), F(0))
    for value in snapshot.persistence_events:
        assert buffers[f'{value.identity_id}:event:{value.cursor}'] == pack(value)
    return snapshot


def decimal(value):
    return Decimal(value.numerator)/Decimal(value.denominator)


def check_gain(value):
    with localcontext() as context:
        context.prec = 100
        truth = (decimal(value.candidate_probability)/decimal(value.base_probability)).ln()
        assert decimal(value.gain.lower) <= truth <= decimal(value.gain.upper)


def wealth_oracle(wealth, gain_sum, count, registration):
    raw = wealth*(1+registration.bet*gain_sum/(count*registration.bound))
    scale = 1 << registration.wealth_grid_bits
    return F(raw.numerator*scale//raw.denominator, scale)


def scoring_and_clocks_audit():
    registration = PersistenceContract(F(3, 4), (rule(epoch=3, horizon=4, bound=F(3)),))
    graph = Program((Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0),)),
                     Sum('mass', (Term(1, 1),))), 2, (2, 3))
    rt, candidate = fixture(cfg=contract(cap=10, peak=10, pattern=(F(1),)),
                            registration=registration, graph=graph)
    iid = admit(rt, candidate)
    wealth, gain_sum, count, checked, changed_after_commit = F(1), F(0), 0, 0, 0
    for target in (0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1):
        before = rt.snapshot()
        prior = {s.candidate_id: s for s in before.candidates}
        sources = dict(zip(('x0_0', 'x0_1'), domain(1)[0]))
        expected = forward_oracle(graph, rt.contract.semantics, prior[candidate].theta, sources)[0]
        prediction, observed = event(rt, target)
        value = rt.snapshot().persistence_events[-1]
        assert value.candidate_probability == expected[target]
        assert value.candidate_probability == dict(prediction.predictions)[candidate][target]
        assert value.base_probability == F(1, 2)
        check_gain(value)
        count += 1
        gain_sum += value.gain.lower
        assert value.epoch_finished == (count == 3)
        assert observed.committed == ((before.cursor+1) % 2 == 0)
        if count == 3:
            wealth = wealth_oracle(wealth, gain_sum, count, registration.rules[0])
            gain_sum, count = F(0), 0
        assert value.wealth_after == identity(rt, iid).wealth == wealth
        if observed.committed:
            after = next(s for s in rt.snapshot().candidates if s.candidate_id == candidate)
            updated = forward_oracle(graph, rt.contract.semantics, after.theta, sources)[0]
            changed_after_commit += int(updated[target] != value.candidate_probability)
        checked += 1
    snapshot = owned(rt)
    assert identity(rt, iid).epochs_completed == 4 and snapshot.cursor == 12
    assert next(s for s in snapshot.candidates if s.candidate_id == candidate).learner.optimizer_steps == 6
    assert changed_after_commit > 0
    assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    return {'sealed_probability_and_Decimal_log_checks': checked,
            'registered_epoch_events': 3, 'optimizer_update_unit': 2,
            'completed_epochs': 4, 'optimizer_commits': 6,
            'committed_successor_probabilities_differ_from_scored_predictions': changed_after_commit,
            'independent_exact_dyadic_wealth_checks': checked}


def crossing_audit():
    rt, candidate = fixture()
    iid = admit(rt, candidate)
    previous = F(1)
    for _ in range(10):
        event(rt, 0)
        value = rt.snapshot().persistence_events[-1]
        check_gain(value)
        expected = wealth_oracle(previous, value.gain.lower, 1, identity(rt, iid).rule)
        assert value.wealth_before == previous and value.wealth_after == expected
        previous = expected
        if rt.reference_persistence_result(iid).status == 'REFERENCE_CROSSED':
            break
    crossed = identity(rt, iid)
    assert crossed.status == 'REFERENCE_CROSSED' and crossed.crossing_cursor == crossed.cursor
    assert crossed.wealth >= 4 and crossed.epochs_completed < 10
    assert crossed.epochs_completed == crossed.cursor  # H=1 independently of update unit 2
    historical_count = len(rt.snapshot().persistence_events)
    for target in (1, 1, 0, 1):
        event(rt, target)
        live = identity(rt, iid)
        assert live.cursor == rt.snapshot().cursor and live.wealth == crossed.wealth
        assert live.crossing_cursor == crossed.crossing_cursor
        assert rt.reference_persistence_result(iid).status == 'REFERENCE_CROSSED'
    snapshot = owned(rt)
    assert len(snapshot.persistence_events) == historical_count
    assert snapshot.alpha_spent == F(1, 4)
    before_install = rt.snapshot()
    assert rt.install(candidate, rt.reference_persistence_result(iid)).status == 'UNRESOLVED'
    assert rt.snapshot() == before_install
    rt.retire_candidate(candidate)
    assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    assert identity(rt, iid).wealth == crossed.wealth and rt.snapshot().alpha_spent == F(1, 4)
    owned(rt)

    rt, candidate = fixture(graph=zero_program(2))
    iid = admit(rt, candidate)
    for target in (0, 1)*5:
        event(rt, target)
    stopped = identity(rt, iid)
    assert stopped.status == 'UNRESOLVED' and stopped.epochs_completed == 10 and stopped.wealth == 1
    assert all(v.gain.lower == v.gain.upper == 0 for v in rt.snapshot().persistence_events)
    assert stopped.crossing_cursor is None and rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    event(rt, 0)
    assert identity(rt, iid) == stopped  # terminal horizon does not silently restart

    registration = PersistenceContract(F(3, 4), (rule(alpha=F(1, 2)),))
    odd, candidate = fixture(registration=registration)
    iid = admit(odd, candidate)
    for _ in range(3):
        event(odd, 0)
    odd_crossing = identity(odd, iid)
    assert odd.reference_persistence_result(iid).status == 'REFERENCE_CROSSED'
    assert odd_crossing.crossing_cursor == 3 and odd_crossing.current_candidate.unit_count == 1
    assert odd_crossing.current_candidate.optimizer_steps == 1
    rejects(lambda: odd.admit_reference_persistence(candidate, 'future'))
    owned(odd)
    return {'positive_crossing_cursor': crossed.crossing_cursor,
            'positive_crossing_wealth_lower': str(crossed.wealth),
            'H1_epochs_are_distinct_from_optimizer_commits': True,
            'crossing_at_cursor_3_with_optimizer_unit_count_1_is_legal': True,
            'continued_lineages_track_after_statistic_stops': True,
            'retirement_invalidates_current_crossing_without_refund': True,
            'equal_forecasts_end_without_crossing_or_rejection': True,
            'reference_crossing_cannot_authorize_install': True}


def null_tree_audit():
    # For independent fair labels, the two exact likelihood ratios are 4/3
    # and 2/3, whose product 8/9 < 1 proves nonpositive conditional mean log
    # gain. This is a declared finite producer audit, not inferred randomness.
    horizon = 5
    registration = PersistenceContract(F(3, 4), (rule(horizon=horizon, alpha=F(1, 2)),))
    prefixes, crossings, events = {(): F(1)}, 0, 0
    for labels in product((0, 1), repeat=horizon):
        rt, candidate = fixture(count=6, registration=registration)
        iid = admit(rt, candidate)
        for i, target in enumerate(labels):
            event(rt, target)
            prefix = labels[:i+1]
            wealth = identity(rt, iid).wealth
            assert prefixes.setdefault(prefix, wealth) == wealth
            events += 1
        crossings += int(identity(rt, iid).crossing_cursor is not None)
        for value in rt.snapshot().persistence_events:
            check_gain(value)
        owned(rt)
    checks = 0
    for prefix, wealth in prefixes.items():
        if len(prefix) < horizon:
            assert (prefixes[prefix+(0,)]+prefixes[prefix+(1,)])/2 <= wealth
            checks += 1
    crossing_probability = F(crossings, 2**horizon)
    assert 0 < crossing_probability <= F(1, 2)
    return {'complete_fair_label_paths': 2**horizon, 'actual_ordinary_events': events,
            'exact_conditional_lower_wealth_inequalities': checks,
            'first_crossing_probability': str(crossing_probability), 'allocated_alpha': '1/2',
            'null_justification': 'fixed ratio product (4/3)*(2/3)=8/9<1 under fair independent labels'}


def freshness_and_alpha_audit():
    rt, candidate = fixture()
    first, second = admit(rt, candidate), admit(rt, candidate)
    before = rt.snapshot()
    rejects(lambda: setattr(before.alpha_allocations[0], 'alpha', F(0)), FrozenInstanceError)
    prediction = deliver_context(rt, 'observation-0', domain(1)[0])
    assert prediction.status == 'PREDICTED_REFERENCE'
    assert rt.snapshot().pending.persistence_ids == (first, second)
    rejects(lambda: rt.admit_reference_persistence(candidate, 'future'))
    rejects(lambda: rt.cancel_reference_persistence(first))
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    event(rt, 0)
    assert identity(rt, first).wealth == identity(rt, second).wealth > 1
    assert [(v.observation_id, v.identity_id) for v in rt.snapshot().persistence_events] == [
        ('observation-0', first), ('observation-0', second), ('observation-1', first), ('observation-1', second)]
    rt.cancel_reference_persistence(first)
    assert rt.snapshot().alpha_spent == F(1, 2)
    newborn = rt.construct_candidate(SOURCE_PAIR).candidate_id
    third = admit(rt, newborn)
    fresh = identity(rt, third)
    assert fresh.start_cursor == 2 and fresh.wealth == 1 and fresh.epochs_completed == 0
    assert fresh.initial_candidate.optimizer_steps == 0
    assert identity(rt, second).current_candidate.optimizer_steps == 1
    blocked = rt.admit_reference_persistence(newborn, 'future')
    assert blocked.status == 'UNRESOLVED' and blocked.identity_id is None and rt.snapshot().alpha_spent == F(3, 4)
    rt.retire_candidate(candidate)
    assert identity(rt, second).status == 'UNRESOLVED' and rt.snapshot().alpha_spent == F(3, 4)
    event(rt, 0)
    assert rt.snapshot().persistence_events[-1].identity_id == third
    assert not any(v.identity_id == third and v.cursor < 2 for v in rt.snapshot().persistence_events)
    rejects(lambda: deliver_context(rt, 'observation-0', domain(1)[0]))
    owned(rt)

    rt, candidate = fixture(law=False)
    result = rt.admit_reference_persistence(candidate, 'future')
    assert result.status == 'UNRESOLVED' and result.identity_id is None
    assert rt.snapshot().alpha_spent == 0 and not rt.snapshot().alpha_allocations

    profile = ProfileSpec('old-data', ('observation-0', 'observation-1'), 2)
    query = QuerySpec('old-label', (Moment((), 1),), (F(0),), (F(1),), 4, 24)
    rt, _ = fixture(profiles=(profile,), queries=(query,))
    event(rt, 0)
    event(rt, 1)
    assert rt.query('old-label', profile.observation_ids).status == 'ANSWERED'
    candidate = rt.construct_candidate(SOURCE_PAIR, profile_id=profile.profile_id).candidate_id
    iid = admit(rt, candidate)
    assert not rt.snapshot().persistence_events and identity(rt, iid).start_cursor == 2
    assert {'proposal', 'profile'} <= {v.purpose for v in rt.snapshot().data_uses}
    rejects(lambda: rt.admit_reference_persistence(candidate, 'future', observation_ids=profile.observation_ids), TypeError)
    event(rt, 0)
    uses = tuple(v for v in rt.snapshot().data_uses if v.purpose == 'persistence')
    assert len(uses) == 1 and uses[0].observation_ids == ('observation-2',)
    assert {v.observation_id for v in rt.snapshot().persistence_events} == {'observation-2'}
    owned(rt)
    return {'shared_fresh_event_is_scored_for_every_preadmitted_identity': True,
            'target_time_admission_cancellation_and_old_ID_backfill_rejected': True,
            'cancel_retire_and_newborn_have_no_alpha_or_wealth_refund': True,
            'global_allocated_alpha': '3/4',
            'explicit_external_stochastic_assumption_required': True,
            'profile_and_proposal_old_observations_are_not_fresh_persistence': True}


def failure_audit():
    # A real integer cap admits the whole-class bound log(2), but cannot
    # complete the losing score log(2/3). It must terminate this identity.
    rt, candidate = fixture(cfg=replace(contract(cap=3, peak=1), reference_integer_bits=128))
    iid = admit(rt, candidate)
    event(rt, 1)
    failed = identity(rt, iid)
    assert failed.status == 'UNRESOLVED' and 'ArithmeticUnresolved' in failed.reason
    assert failed.wealth == 1 and failed.epochs_completed == 0
    event(rt, 1)
    assert identity(rt, iid) == failed and rt.snapshot().cursor == 2
    assert rt.snapshot().alpha_spent == F(1, 4)
    assert not rt.snapshot().persistence_events
    assert [v.observation_ids for v in rt.snapshot().data_uses if v.purpose == 'persistence'] == [('observation-0',)]
    owned(rt)

    rt, candidate = fixture(cfg=replace(contract(cap=3, peak=1), reference_integer_bits=96))
    admission = rt.admit_reference_persistence(candidate, 'future')
    assert admission.status == 'UNRESOLVED' and admission.identity_id is not None
    assert rt.snapshot().alpha_spent == F(1, 4)
    assert identity(rt, admission.identity_id).status == 'UNRESOLVED'
    owned(rt)

    # Calibrate only actual prior work, then use an immutable cap large enough
    # for ordinary successors but smaller than the next evidence computation.
    # The registered binary source domain needs at most ten context bytes.
    # A sixteen-byte window keeps the next paid ordinary event below this
    # deliberately small evidence-failure budget; no data arrives for free.
    window = IngressContract(16, 16)
    rt, candidate = fixture(ingress=window)
    admit(rt, candidate)
    deliver_context(rt, 'observation-0', domain(1)[0])
    work_cap = rt.snapshot().resources['spent']['compiler']['work']+200
    cfg = replace(contract(cap=3, peak=1), limits=limits(work_cap=work_cap))
    limited, candidate = fixture(cfg=cfg, ingress=window)
    iid = admit(limited, candidate)
    event(limited, 0)
    failed = identity(limited, iid)
    assert failed.status == 'UNRESOLVED' and 'ResourceExceeded' in failed.reason
    event(limited, 1)
    assert identity(limited, iid) == failed and limited.snapshot().cursor == 2
    assert limited.snapshot().alpha_spent == F(1, 4)
    assert not limited.snapshot().persistence_events
    owned(limited)

    # Actual materialization can fail after the alpha allocation. Diagnostic
    # state has no authority and no fictitious packed residency is claimed.
    rt, candidate = fixture()
    byte_cap = rt.snapshot().resources['current']['reference_payload_bytes']+1
    cfg = replace(contract(cap=3, peak=1), limits=limits(byte_cap=byte_cap))
    limited, candidate = fixture(cfg=cfg)
    result = limited.admit_reference_persistence(candidate, 'future')
    assert result.status == 'UNRESOLVED' and result.identity_id is not None
    snapshot = validate_residency(limited)
    assert snapshot.alpha_spent == F(1, 4) and len(snapshot.alpha_allocations) == 1
    assert identity(limited, result.identity_id).status == 'UNRESOLVED'
    assert snapshot.resources['peak']['reference_payload_bytes'] <= byte_cap

    # Unexpected scoring failure cannot discard a losing target and resume
    # from prior wealth. The ordinary trajectory halts and retains the target.
    rt, candidate = fixture()
    iid = admit(rt, candidate)
    event(rt, 0)
    before = rt.snapshot()
    deliver_context(rt, 'observation-1', domain(1)[0])
    with patch.object(execution, 'log_enclosure', side_effect=RuntimeError('injected evidence backend failure')):
        rejects(lambda: rt.observe(1), RuntimeError)
    snapshot = owned(rt)
    assert snapshot.halted and snapshot.observations[-1].target == 1
    assert snapshot.cursor == before.cursor and snapshot.candidates == before.candidates
    assert identity(rt, iid).status == 'UNRESOLVED' and rt.snapshot().alpha_spent == F(1, 4)
    rejects(lambda: deliver_context(rt, 'observation-1', domain(1)[0]))
    assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'

    # A crossing before an optimizer boundary must not survive a later failed
    # commit of the required continuously tracked ordinary trajectories.
    registration = PersistenceContract(F(3, 4), (rule(alpha=F(1, 2)),))
    rt, candidate = fixture(registration=registration)
    iid = admit(rt, candidate)
    for _ in range(3):
        event(rt, 0)
    crossed = identity(rt, iid)
    assert rt.reference_persistence_result(iid).status == 'REFERENCE_CROSSED'
    deliver_context(rt, 'observation-3', domain(1)[0])
    with patch.object(execution, 'commit_event', side_effect=RuntimeError('injected ordinary commit backend failure')):
        rejects(lambda: rt.observe(1), RuntimeError)
    snapshot = owned(rt)
    assert snapshot.halted and snapshot.cursor == 3 and snapshot.observations[-1].target == 1
    assert identity(rt, iid).crossing_cursor == 3 and identity(rt, iid).wealth == crossed.wealth
    assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    assert snapshot.alpha_spent == F(1, 2)

    # A computed first-crossing event is not sufficient: its owned successor
    # evidence state must also materialize before a current crossing exists.
    rt, candidate = fixture()
    iid = admit(rt, candidate)
    for _ in range(5):
        event(rt, 0)
    before = identity(rt, iid)
    allocate = rt._allocate
    injections = []

    def crossing_workspace_failure(owner, objects):
        if any(obj.spec.kind == 'reference_persistence_state' and b'REFERENCE_CROSSED' in obj.payload for obj in objects):
            injections.append(owner)
            raise ResourceExceeded('injected first-crossing workspace allocation failure')
        return allocate(owner, objects)

    with patch.object(rt, '_allocate', side_effect=crossing_workspace_failure):
        event(rt, 0)
    snapshot = owned(rt)
    assert len(injections) == 1 and snapshot.cursor == 6 and not snapshot.halted
    assert snapshot.persistence_events[-1].wealth_after >= 4
    failed = identity(rt, iid)
    assert failed.status == 'UNRESOLVED' and failed.wealth == before.wealth and failed.crossing_cursor is None
    assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    event(rt, 1)
    assert identity(rt, iid) == failed and rt.snapshot().alpha_spent == F(1, 4)
    owned(rt)

    # Two evidence successors may already contain the first crossing when
    # ordinary publication fails. Neither may escape the failed shared prefix.
    rt, candidate = fixture()
    identities = (admit(rt, candidate), admit(rt, candidate))
    for _ in range(5):
        event(rt, 0)
    before = rt.snapshot()
    deliver_context(rt, 'observation-5', domain(1)[0])
    with patch.object(rt._ledger, 'release_many', side_effect=RuntimeError('injected ordinary publication failure')):
        rejects(lambda: rt.observe(0), RuntimeError)
    snapshot = owned(rt)
    assert snapshot.halted and snapshot.cursor == 5 and snapshot.candidates == before.candidates
    assert snapshot.observations[-1].target == 0 and snapshot.alpha_spent == F(1, 2)
    for iid in identities:
        assert identity(rt, iid).crossing_cursor == 6  # executed but never published successor
        assert rt.reference_persistence_result(iid).status == 'UNRESOLVED'
    rejects(lambda: deliver_context(rt, 'observation-5', domain(1)[0]))
    return {'real_integer_cap_stops_identity_without_skipping_outcome': True,
            'real_work_cap_stops_identity_while_ordinary_continuation_remains_legal': True,
            'failed_numeric_and_physical_admission_keep_spent_alpha': True,
            'unexpected_score_failure_keeps_target_and_halts_ordinary_prefix': True,
            'ordinary_commit_failure_after_crossing_invalidates_current_evidence': True,
            'first_crossing_workspace_failure_cannot_activate_or_resume_evidence': True,
            'ordinary_publication_failure_revokes_all_staged_crossings': True,
            'failed_identity_cannot_resume_or_inherit_prior_wealth': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', choices=('all', 'scores', 'crossing', 'null', 'freshness', 'failures'), default='all')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checks = {'scores': scoring_and_clocks_audit, 'crossing': crossing_audit, 'null': null_tree_audit,
              'freshness': freshness_and_alpha_audit, 'failures': failure_audit}
    result = {'status': 'PASS', 'scope': 'actual owned Runtime reference evidence under an explicit external conditional stochastic-law assumption',
              'null_id': rule().null_id}
    for key, audit in checks.items():
        if args.section in ('all', key):
            result[key] = audit()
    result['not_closed'] = ['external producer stochastic-law verification', 'paired reference and actual AMP persistence',
                            'full ERC-1 physical resources', 'atomic installation and complete Runtime release']
    if args.write:
        if args.section != 'all':
            parser.error('only the complete audit may replace canonical evidence')
        (ROOT/'evidence/minimal/FP_REFERENCE_PERSISTENCE_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
