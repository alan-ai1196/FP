"""Executed four-learner CPU persistence and adversarial whole-domain checks.

External laws are declared audit fixtures, never inferred from their tapes.
No target AMP, installation or complete resource authority is claimed.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from ingress_audit_support import deliver_context
from fp_reference.binary_arithmetic import Float64Arithmetic, Float64Value
from fp_reference.float64_range import enclose_float64, enclosure_operations
from fp_reference.persistence import PersistenceContract, PersistenceRule, REFERENCE_PATH, FLOAT64_PATH
from fp_reference.profile import ProfileSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, Source, State, Sum, Term
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import shared_graph
from audit_reference_persistence import identity, event, owned, check_gain, wealth_oracle
from audit_float64_runtime import CPUState, bits, cpu_initial, cpu_predict, fixture, replay


SOURCE_PAIR = Program((Source('x0_0'), Source('x0_1')), 0, (0, 1))


def registration(*, bound=F(3, 4), horizon=10, epoch=1, alpha=F(1, 4)):
    return PersistenceContract(F(3, 4), tuple(
        PersistenceRule(label, epoch, horizon, alpha, F(3, 4), bound, 12, 16, path)
        for label, path in (('ref', REFERENCE_PATH), ('finite', FLOAT64_PATH))))


def config(**kwargs):
    return replace(contract(**kwargs), reference_integer_bits=32768,
                   limits=limits(byte_cap=80_000_000, work_cap=100_000_000))


def pair(rt, candidate):
    r = rt.admit_reference_persistence(candidate, 'ref')
    f = rt.admit_float64_persistence(candidate, 'finite')
    assert r.identity_id and f.identity_id, (r, f)
    assert identity(rt, r.identity_id).status == identity(rt, f.identity_id).status == 'ACTIVE', (r, f)
    return r.identity_id, f.identity_id


def float_exact(value):
    return F.from_float(value)


def range_audit():
    cfg = config(cap=10000, peak=10000, source_domain=False)
    graph = shared_graph()
    grid = (F(0), F(1, 8), F(1, 3), F(2, 3), F(1))
    cases, scopes = 0, 0
    for pattern in product((F(0), F(1, 3), F(1), F(2)), repeat=2):
        state = cpu_initial(graph, cfg.semantics, pattern, 0)
        theta = tuple(Float64Value(bits(v)) for v in state.theta)
        arithmetic = Float64Arithmetic(32768)
        bound = enclose_float64(graph, cfg.semantics, theta, normalizer_cap=cfg.normalizer_cap,
                                activation_cap=cfg.activation_cap, arith=arithmetic)
        assert bound.scalar_operations == arithmetic.operations == enclosure_operations(graph, cfg.semantics)
        for row in product(grid, repeat=2):
            prediction = cpu_predict(graph, cfg.semantics, state, dict(zip(('x0_0', 'x0_1'), row)))
            values, masses, total, probabilities = (prediction[k] for k in ('values', 'masses', 'normalizer', 'probabilities'))
            assert all(float_exact(v) <= b.exact for v, b in zip(values, bound.values_upper))
            assert all(lo.exact <= float_exact(v) <= hi.exact for lo, v, hi in zip(bound.base_lower, masses, bound.masses_upper))
            assert sum(map(float_exact, masses), F(0)) <= bound.stored_mass_sum_upper
            assert float_exact(total) <= bound.rounded_normalizer_upper.exact
            assert all(0 < lo.exact <= float_exact(p) <= 1 for lo, p in zip(bound.raw_probability_lower, probabilities))
            cases += 1
        scopes += 1

    # Whole delayed boxes, not only the currently visible queue head.
    rules = replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(1)),))
    recurrent = Program((Source('x0_0'), State('h'), Sum('mass', (Term(0, 0), Term(1, 0))),
                         Product('mass', 2, 2), Sum('mass', ())), 1, (3, 4), (Binding('h', 2),))
    theta = (Float64Value(bits(0.25)),)
    bound = enclose_float64(recurrent, rules, theta, normalizer_cap=F(10), activation_cap=F(10), arith=Float64Arithmetic(32768))
    recurrent_cases = 0
    for source, head, tail in product(grid, repeat=3):
        state = CPUState((0.25,), (('h', (float(head), float(tail))),), (0.0,), 0, 0, 0)
        pred = cpu_predict(recurrent, rules, state, {'x0_0': source, 'x0_1': F(1)-source})
        assert all(float_exact(v) <= b.exact for v, b in zip(pred['values'], bound.values_upper))
        assert all(float_exact(v) <= 1 for _, queue in pred['delayed'] for v in queue)
        recurrent_cases += 1

    # Reference source cap is below its upward-rounded finite source value.
    # Checking a currently harmless context cannot establish the whole domain.
    unsafe = config(cap=10, peak=F(1, 10), source_domain=False)
    unsafe = replace(unsafe, semantics=replace(unsafe.semantics, sources=tuple(replace(s, upper=F(1, 10)) for s in unsafe.semantics.sources)))
    rejects(lambda: enclose_float64(SOURCE_PAIR, unsafe.semantics, (), normalizer_cap=F(10),
        activation_cap=F(1, 10), arith=Float64Arithmetic(32768)), ArithmeticUnresolved)
    # Strict positive real bases can disappear, even though all maxima fit.
    tiny = replace(cfg.semantics, base=(F(1, 1 << 1075), F(1)))
    rejects(lambda: enclose_float64(zero_program(2), tiny, (), normalizer_cap=F(2),
        activation_cap=F(2), arith=Float64Arithmetic(32768)), ArithmeticUnresolved)
    # Positive masses do not alone prevent a rounded final division of zero.
    wide = replace(cfg.semantics, base=(F(1, 1 << 1074), F(1 << 1023)))
    rejects(lambda: enclose_float64(zero_program(2), wide, (), normalizer_cap=F(1 << 1024),
        activation_cap=F(2), arith=Float64Arithmetic(32768)), ArithmeticUnresolved)
    return {'independent_box_declarations': scopes, 'independent_direct_float_context_checks': cases,
            'full_delayed_box_cases': recurrent_cases,
            'upward_source_rounding_base_underflow_and_final_division_underflow_rejected': True}


def scored_trajectories_audit():
    rt, candidate = fixture(cfg=config(pattern=(F(1, 3), F(1, 4), F(0))), count=12,
        persistence=registration(bound=F(6), epoch=3, horizon=4), rate=F(1, 8), grid=24)
    rid, fid = pair(rt, candidate)
    wealth = {rid: F(1), fid: F(1)}
    sums, counts = {rid: F(0), fid: F(0)}, {rid: 0, fid: 0}
    different_paths, different_output, new_bounds, checks = 0, 0, 0, 0
    previous_theta = identity(rt, fid).candidate_float64_range[0].theta
    for context, target in ((0, 0), (1, 1), (0, 1), (1, 0))*3:
        cursor = rt.snapshot().cursor
        assert deliver_context(rt, f'observation-{cursor}', domain(1)[context]).status == 'PREDICTED_REFERENCE'
        pending = rt.snapshot().pending
        exact = dict(pending.predictions)
        finite = dict(pending.float64_predictions)
        assert pending.persistence_ids == (rid, fid)
        rejects(lambda: rt.admit_float64_persistence(candidate, 'finite'))
        rejects(lambda: rt.cancel_float64_persistence(fid))
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
        rows = rt.snapshot().persistence_events[-2:]
        for row in rows:
            path = identity(rt, row.identity_id).rule.score_path
            source = exact if path == REFERENCE_PATH else finite
            for cid, actual in ((row.base_lineage_id, row.base_probability), (row.candidate_lineage_id, row.candidate_probability)):
                pred = source[cid]
                expected = pred.probabilities[target] if path == REFERENCE_PATH else pred.masses[target].exact/sum((v.exact for v in pred.masses), F(0))
                assert actual == expected, (cursor, row.cursor, path, cid, actual, expected,
                    [(v.rule.score_path, v.status, v.reason) for v in rt.snapshot().persistence_identities])
                if path == FLOAT64_PATH:
                    different_output += int(actual != pred.probabilities[target].exact)
            check_gain(row)
            iid = row.identity_id
            counts[iid] += 1
            sums[iid] += row.gain.lower
            if counts[iid] == 3:
                wealth[iid] = wealth_oracle(wealth[iid], sums[iid], counts[iid], identity(rt, iid).rule)
                sums[iid], counts[iid] = F(0), 0
            assert row.wealth_after == identity(rt, iid).wealth == wealth[iid]
            checks += 1
        different_paths += int(rows[0].candidate_probability != rows[1].candidate_probability)
        current = identity(rt, fid)
        new_bounds += int(current.candidate_float64_range[0].theta != previous_theta)
        assert all(b.theta == current.current_candidate_float64.theta for b in current.candidate_float64_range)
        previous_theta = current.candidate_float64_range[0].theta
    assert different_paths and different_output and new_bounds == 6
    snapshot = owned(rt)
    assert snapshot.alpha_spent == F(1, 2)
    assert tuple(a.path for a in snapshot.alpha_allocations) == (REFERENCE_PATH, FLOAT64_PATH)
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    bitwise_checks, _, _ = replay(rt)
    return {'same_event_independent_score_and_wealth_checks': checks,
            'events_with_different_reference_and_finite_probabilities': different_paths,
            'stored_mass_probabilities_differing_from_rounded_output': different_output,
            'post_optimizer_range_recertifications': new_bounds, 'independent_four_trajectory_phase_checks': bitwise_checks}


def nontransfer_audit():
    delta = F(1, 1 << 54)
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    rt, candidate = fixture(cfg=config(cap=2+delta, peak=1, pattern=(delta,)), graph=graph,
        count=10, rate=F(0), persistence=registration(bound=delta, horizon=8))
    rid, fid = pair(rt, candidate)
    for _ in range(8):
        event(rt, 0)
    r, f = identity(rt, rid), identity(rt, fid)
    assert r.crossing_cursor == 5 and r.wealth >= 4
    assert rt.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert f.wealth == 1 and f.crossing_cursor is None
    assert all(v.gain.lower == v.gain.upper == 0 for v in rt.snapshot().persistence_events if v.identity_id == fid)
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    rejects(lambda: rt.reference_persistence_result(fid))
    rejects(lambda: rt.float64_persistence_result(rid))
    rejects(lambda: rt.paired_persistence_result(fid, rid))
    before = rt.snapshot()
    assert rt.install(candidate, rt.paired_persistence_result(rid, fid)).status == 'UNRESOLVED'
    assert rt.snapshot() == before
    owned(rt)
    return {'delta': str(delta), 'normalizer_cap': str(2+delta), 'reference_crossing_cursor': 5,
            'reference_wealth_lower': str(r.wealth), 'finite_mass_gain': '0', 'finite_wealth': '1',
            'reference_crossing_cannot_transfer_to_physical_path': True}


def null_and_crossing_audit():
    horizon = 5
    declared = registration(horizon=horizon, alpha=F(1, 3))
    trees = ({(): F(1)}, {(): F(1)})
    crossings, events = [0, 0], 0
    for labels in product((0, 1), repeat=horizon):
        rt, candidate = fixture(cfg=config(cap=3, peak=1), graph=SOURCE_PAIR, count=6, persistence=declared)
        ids = pair(rt, candidate)
        for t, target in enumerate(labels):
            event(rt, target)
            for index, iid in enumerate(ids):
                value = identity(rt, iid)
                assert trees[index].setdefault(labels[:t+1], value.wealth) == value.wealth
            events += 1
        for index, iid in enumerate(ids):
            crossings[index] += int(identity(rt, iid).crossing_cursor is not None)
        owned(rt)
    checks = 0
    for tree in trees:
        for prefix, wealth in tree.items():
            if len(prefix) < horizon:
                assert (tree[prefix+(0,)]+tree[prefix+(1,)])/2 <= wealth
                checks += 1
    probabilities = tuple(F(n, 2**horizon) for n in crossings)
    assert all(0 < p <= F(1, 3) for p in probabilities)
    # Separate registered allocations; shared events need no independence.
    rt, candidate = fixture(cfg=config(cap=3, peak=1), graph=SOURCE_PAIR, count=14, persistence=registration())
    ids = pair(rt, candidate)
    for _ in range(6):
        event(rt, 0)
    assert rt.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED'
    history = tuple(identity(rt, iid).wealth for iid in ids)
    event(rt, 1)
    assert rt.paired_persistence_result(*ids).status == 'PAIRED_CPU_CROSSED'
    assert tuple(identity(rt, iid).wealth for iid in ids) == history
    deliver_context(rt, 'observation-7', domain(1)[0])
    with patch.object(execution.finite, 'commit_event', side_effect=RuntimeError('finite commit broke the continuous four-path prefix')):
        rejects(lambda: rt.observe(1), RuntimeError)
    assert rt.snapshot().halted and rt.snapshot().observations[-1].target == 1
    assert rt.paired_persistence_result(*ids).status == 'UNRESOLVED'
    assert tuple(identity(rt, iid).wealth for iid in ids) == history
    assert rt.snapshot().alpha_spent == F(1, 2)
    return {'complete_fair_label_paths': 2**horizon, 'ordinary_events': events,
            'two_path_conditional_wealth_inequalities': checks,
            'path_crossing_probabilities': list(map(str, probabilities)), 'each_path_alpha': '1/3',
            'null_justification': 'both fixed stored-mass ratio products are (4/3)*(2/3)=8/9<1 under fair independent labels',
            'two_actual_crossings_and_post_crossing_finite_failure_checked': True}


def failures_audit():
    # Independent arithmetic can exhaust only the reference scoring budget.
    # A surviving finite statistic is not permission to fill the missing path.
    rt, candidate = fixture(cfg=config(pattern=(F(1, 3), F(1, 4), F(0))), count=12,
        persistence=registration(bound=F(6), epoch=3, horizon=4), rate=F(1, 8))
    rid, fid = pair(rt, candidate)
    for context, target in (((0, 0), (1, 1), (0, 1), (1, 0))*2)[:7]:
        event(rt, target, domain(1)[context])
    assert identity(rt, rid).status == 'UNRESOLVED' and 'integer work limit' in identity(rt, rid).reason
    assert identity(rt, fid).status == 'ACTIVE' and not rt.snapshot().halted
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    assert rt.snapshot().alpha_spent == F(1, 2)

    # The finite first-crossing successor must itself be owned. A retained
    # score that exceeds the threshold cannot replace a failed state write.
    rt, candidate = fixture(cfg=config(cap=3, peak=1), graph=SOURCE_PAIR, count=12, persistence=registration())
    rid, fid = pair(rt, candidate)
    for _ in range(5):
        event(rt, 0)
    before = identity(rt, fid)
    allocate = rt._allocate
    failed_writes = []
    def fail_crossing(owner, objects):
        if any(obj.spec.kind == 'binary64_persistence_state' and obj.value.status == 'FLOAT64_CROSSED' for obj in objects):
            failed_writes.append(owner)
            raise ResourceExceeded('injected finite crossing state allocation failure')
        return allocate(owner, objects)
    with patch.object(rt, '_allocate', side_effect=fail_crossing):
        event(rt, 0)
    failed = identity(rt, fid)
    assert len(failed_writes) == 1 and failed.status == 'UNRESOLVED' and failed.wealth == before.wealth
    assert failed.crossing_cursor is None and rt.snapshot().persistence_events[-1].wealth_after >= 4
    assert rt.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    event(rt, 1)
    assert identity(rt, fid) == failed
    owned(rt)

    # The independently rounded optimizer reaches theta=float(1/10), slightly
    # above the exact endpoint. The next whole-domain stored-mass sum exceeds
    # R=21/10; a current context with inactive source would still look harmless.
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    rt, candidate = fixture(cfg=config(cap=F(21, 10), peak=1, pattern=(F(0),)), graph=graph,
        count=12, rate=F(1, 5), persistence=registration(bound=F(1), horizon=10))
    rid, fid = pair(rt, candidate)
    event(rt, 0)
    event(rt, 0)
    failed = identity(rt, fid)
    assert failed.status == 'UNRESOLVED' and 'whole-domain stored-mass sum' in failed.reason
    assert identity(rt, rid).status == 'ACTIVE' and rt.snapshot().cursor == 2
    assert next(s for s in rt.snapshot().candidates if s.candidate_id == candidate).theta == (F(1, 10),)
    event(rt, 0, domain(1)[1])
    assert identity(rt, fid) == failed and rt.snapshot().cursor == 3
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    # Exact safe at all source values; finite safe at x=0 but unsafe at x=1/10.
    cfg = config(cap=10, peak=F(1, 10), source_domain=False)
    cfg = replace(cfg, semantics=replace(cfg.semantics,
        sources=tuple(replace(s, upper=F(1, 10)) for s in cfg.semantics.sources)))
    rt, candidate = fixture(cfg=cfg, graph=SOURCE_PAIR, count=12, persistence=registration(bound=F(3)))
    rid = rt.admit_reference_persistence(candidate, 'ref').identity_id
    failed = rt.admit_float64_persistence(candidate, 'finite')
    assert failed.status == 'UNRESOLVED' and failed.identity_id
    assert 'whole-domain activation' in failed.reason
    assert rt.snapshot().alpha_spent == F(1, 2)
    event(rt, 0, (F(0), F(0)))
    assert rt.snapshot().cursor == 1 and identity(rt, failed.identity_id).cursor == 0
    assert rt.paired_persistence_result(rid, failed.identity_id).status == 'UNRESOLVED'
    # Paid actual admission work and evidence allocation limits.
    generous, candidate = fixture(cfg=config(cap=3, peak=1), graph=SOURCE_PAIR, count=12, persistence=registration())
    initial = generous.snapshot()
    cap = initial.resources['spent']['compiler']['work']+100
    limited_cfg = replace(config(cap=3, peak=1), limits=limits(80_000_000, cap))
    limited, candidate = fixture(cfg=limited_cfg, graph=SOURCE_PAIR, count=12, persistence=registration())
    failed = limited.admit_float64_persistence(candidate, 'finite')
    assert failed.identity_id and failed.status == 'UNRESOLVED'
    assert identity(limited, failed.identity_id).status == 'UNRESOLVED'
    assert limited.snapshot().alpha_spent == F(1, 4)
    byte_cap = initial.resources['current']['reference_payload_bytes']+1
    limited_cfg = replace(config(cap=3, peak=1), limits=limits(byte_cap, 100_000_000))
    limited, candidate = fixture(cfg=limited_cfg, graph=SOURCE_PAIR, count=12, persistence=registration())
    failed = limited.admit_float64_persistence(candidate, 'finite')
    assert failed.identity_id and failed.status == 'UNRESOLVED'
    assert limited.snapshot().alpha_spent == F(1, 4)
    assert validate_residency(limited).resources['peak']['reference_payload_bytes'] <= byte_cap
    # State-matched result API excludes different admission boundaries.
    rt, candidate = fixture(cfg=config(cap=3, peak=1), graph=SOURCE_PAIR, count=14, persistence=registration(horizon=6))
    rid = rt.admit_reference_persistence(candidate, 'ref').identity_id
    event(rt, 0)
    event(rt, 0)
    fid = rt.admit_float64_persistence(candidate, 'finite').identity_id
    rejects(lambda: rt.paired_persistence_result(rid, fid))
    rt.cancel_float64_persistence(fid)
    assert rt.snapshot().alpha_spent == F(1, 2)
    assert rt.float64_persistence_result(fid).status == 'UNRESOLVED'
    return {'observed_safe_context_cannot_substitute_for_whole_domain': True,
            'rounded_optimizer_invalidates_future_domain_before_next_context': True,
            'reference_integer_exhaustion_cannot_borrow_finite_evidence': True,
            'unowned_finite_first_crossing_cannot_authorize_pair': True,
            'actual_work_and_byte_cap_admission_failures_keep_alpha': True,
            'different_start_boundaries_and_wrong_score_paths_cannot_pair': True,
            'cancelled_physical_identity_cannot_recycle_alpha': True}


def profile_freshness_audit():
    profile = ProfileSpec('past-only', ('observation-0', 'observation-1'), 2)
    rt, candidate = fixture(cfg=config(pattern=(F(1, 3), F(1, 4), F(0))), count=14,
        persistence=registration(bound=F(6), horizon=6, alpha=F(1, 8)), profiles=(profile,), grid=24)
    old = pair(rt, candidate)
    event(rt, 0)
    event(rt, 1)
    old_wealth = tuple(identity(rt, iid).wealth for iid in old)
    built = rt.construct_candidate(shared_graph(), profile_id='past-only')
    assert built.status == 'BUILT_REFERENCE', built
    fresh = pair(rt, built.candidate_id)
    for iid in fresh:
        value = identity(rt, iid)
        assert value.start_cursor == 2 and value.wealth == 1 and value.epochs_completed == 0
        assert value.initial_candidate.optimizer_steps == value.initial_candidate_float64.optimizer_steps == 2
    assert tuple(identity(rt, iid).wealth for iid in old) == old_wealth
    assert len(rt.snapshot().profile_events) == 4 and rt.snapshot().cursor == 2
    rejects(lambda: rt.paired_persistence_result(old[0], fresh[1]))
    event(rt, 0)
    assert {(v.identity_id, v.observation_id) for v in rt.snapshot().persistence_events if v.identity_id in fresh} == {
        (fresh[0], 'observation-2'), (fresh[1], 'observation-2')}
    rt.retire_candidate(candidate)
    assert rt.paired_persistence_result(*old).status == 'UNRESOLVED'
    assert all(identity(rt, iid).status == 'ACTIVE' for iid in fresh)
    assert rt.snapshot().alpha_spent == F(1, 2)
    rejects(lambda: deliver_context(rt, 'observation-0', domain(1)[0]))
    owned(rt)
    return {'profile_events': 4, 'original_profile_observations': 2,
            'new_identity_start_cursor': 2, 'first_fresh_observation': 'observation-2',
            'complete_profile_states_retained_without_wealth_or_alpha_transfer': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('range', 'scores', 'nontransfer', 'null', 'failures', 'freshness'))
    args = parser.parse_args()
    parts = {'range': range_audit, 'scores': scored_trajectories_audit, 'nontransfer': nontransfer_audit,
             'null': null_and_crossing_audit, 'failures': failures_audit, 'freshness': profile_freshness_audit}
    if args.section:
        print(json.dumps(parts[args.section](), indent=2))
        return
    result = {'status': 'PASS', 'scope': 'owned exact-reference and actual CPU binary64 stored-mass persistence',
              **{name: fn() for name, fn in parts.items()},
              'not_closed': ['external producer law verification', 'target AMP', 'full ERC-1 resources', 'atomic install and complete Runtime release']}
    if args.write:
        (ROOT/'evidence/minimal/FP_PAIRED_CPU_PERSISTENCE_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
