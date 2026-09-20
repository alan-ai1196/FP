"""Owned mixture persistence: exact arithmetic, actual CPU paths and failures.

No scalar helper supplies a Runtime certificate. CUDA execution is a separate
optional bounded worker; a running registered experiment is never modified.
"""
from collections import Counter
from dataclasses import FrozenInstanceError, asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
                str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import persistence_mixture as kernel
from fp_reference.persistence import (ArcsinePersistenceRule, PersistenceContract,
                                      REFERENCE_PATH, FLOAT64_PATH)
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.core import ContractError
from fp_reference.program import Program, Source, Sum, Term
from audit_reference_construction import contract, limits, rejects, validate_residency
from audit_reference_persistence import fixture, event, identity, owned, check_gain
import fp_reference.runtime as execution
import predictable_mixture_state as oracle

OUTPUT = ROOT/'evidence/minimal/FP_MIXTURE_PERSISTENCE_AUDIT.json'


def rule(*, epoch=1, horizon=16, bits=32, bound=F(3, 4), terms=12, path=REFERENCE_PATH, label='future'):
    return ArcsinePersistenceRule(label, epoch, horizon, F(1, 4), bound, terms, bits, path)


def register(value):
    return PersistenceContract(F(3, 4), (value,))


def oracle_wealth(numbers, bits):
    polynomial = oracle.expanded(tuple(F(n, 1 << bits) for n in numbers))
    return oracle.independent_readout(polynomial)


def check_snapshot(snapshot):
    checked = 0
    for current in snapshot.persistence_identities:
        r = current.rule
        assert type(r) is ArcsinePersistenceRule
        values = tuple(e for e in snapshot.persistence_events if e.identity_id == current.identity_id)
        numbers, wealth, accumulated, count = (1 << r.coefficient_grid_bits,), F(1), F(0), 0
        committed = [(numbers, wealth)]
        crossed = None
        for item in values:
            assert crossed is None
            assert item.wealth_before == wealth and item.cursor >= current.start_cursor
            check_gain(item)
            accumulated += item.gain.lower
            count += 1
            assert item.epoch_finished == (count == r.epoch_events)
            if item.epoch_finished:
                numbers = oracle.rounded_step(numbers, accumulated/(count*r.bound))
                wealth = oracle_wealth(numbers, r.coefficient_grid_bits)
                committed.append((numbers, wealth))
                accumulated, count = F(0), 0
            assert item.wealth_after == wealth
            if wealth*r.alpha >= 1:
                crossed = item.cursor+1
            checked += 1
        if current.mixture_coefficients is None:
            assert not values and current.status == 'UNRESOLVED'
        else:
            assert (current.mixture_coefficients, current.wealth) == committed[current.epochs_completed]
        if current.crossing_cursor is not None:
            assert current.crossing_cursor == crossed
            assert current.crossing_wealth == current.wealth >= 4
        elif crossed is not None:
            assert current.status == 'UNRESOLVED'
    return checked


def kernel_audit():
    r = rule(horizon=5, bits=18, bound=F(1))
    calls = Counter()
    originals = {name: getattr(kernel._Integers, name) for name in ('guard', 'add', 'mul', 'divide', 'dyadic')}
    wrappers = {}
    for name, original in originals.items():
        def count(self, *args, _name=name, _original=original, **kwargs):
            calls[_name] += 1
            return _original(self, *args, **kwargs)
        wrappers[name] = count
    checked, maximum_calls = 0, 0
    with patch.multiple(kernel._Integers, **wrappers):
        for word in product((F(-1, 3), F(0), F(1, 2)), repeat=5):
            n, wealth = kernel.initial_coefficients(r, bit_limit=4096), F(1)
            for t, score in enumerate(word):
                before = sum(calls.values())
                expected = oracle.rounded_step(n, score)
                n, wealth = kernel.next_mixture(n, wealth, score, t, r, bit_limit=4096)
                used = sum(calls.values())-before
                assert n == expected and wealth == oracle_wealth(n, r.coefficient_grid_bits)
                assert used+128 < kernel.step_work(t)
                maximum_calls = max(maximum_calls, used)
                checked += 1
    seed = kernel.initial_coefficients(r, bit_limit=4096)
    bad = (
        lambda: kernel.next_mixture(list(seed), F(1), F(0), 0, r, bit_limit=4096),
        lambda: kernel.next_mixture((seed[0]-1,), F(1), F(0), 0, r, bit_limit=4096),
        lambda: kernel.next_mixture(seed, F(2), F(0), 0, r, bit_limit=4096),
        lambda: kernel.next_mixture(seed, F(1), F(2), 0, r, bit_limit=4096),
        lambda: kernel.next_mixture(seed, F(1), F(0), 5, r, bit_limit=4096),
        lambda: kernel.next_mixture(seed, F(1), 0.0, 0, r, bit_limit=4096),
        lambda: kernel.initial_coefficients(r, bit_limit=18),
        lambda: kernel.next_mixture(seed, F(1), F(1, 2), 0, r, bit_limit=19),
        lambda: register(replace(r, coefficient_grid_bits=True)),
    )
    for f in bad:
        rejects(f)
    return {'complete_words': 3**5, 'guarded_updates': checked,
            'maximum_instrumented_integer_kernel_calls_per_update': maximum_calls,
            'forged_state_rule_score_and_budget_refusals': len(bad),
            'work_scope': 'instrumented guarded calls plus fixed rational allowance; no machine-time claim'}


def reference_audit():
    rt, candidate = fixture(registration=register(rule()))
    admitted = rt.admit_reference_persistence(candidate, 'future')
    assert identity(rt, admitted.identity_id).status == 'ACTIVE'
    rejects(lambda: rt.admit_reference_persistence(candidate, rule()))
    rejects(lambda: setattr(rule(), 'coefficient_grid_bits', 4), FrozenInstanceError)
    for _ in range(12):
        event(rt, 0)
    snap = owned(rt)
    assert check_snapshot(snap) == 7
    p = identity(rt, admitted.identity_id)
    assert p.crossing_cursor == 7 and p.cursor == 12 and p.epochs_completed == 7
    assert rt.reference_persistence_result(admitted.identity_id).status == 'REFERENCE_CROSSED'
    assert rt.install(candidate, certified=True, bridge=True).status == 'UNRESOLVED'

    # Evidence epochs and optimizer commits are distinct clocks, with changing
    # predictions. The curve advances only after all three epoch events.
    graph = Program((Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0),)),
                     Sum('mass', (Term(1, 1),))), 2, (2, 3))
    rt, candidate = fixture(cfg=contract(cap=10, peak=10, pattern=(F(1),)),
        graph=graph, registration=register(rule(epoch=3, horizon=4, bound=F(3))))
    admitted = rt.admit_reference_persistence(candidate, 'future')
    for label in (0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1):
        event(rt, label)
    snap = owned(rt)
    assert check_snapshot(snap) == 12
    p = identity(rt, admitted.identity_id)
    assert p.epochs_completed == 4 and p.cursor == 12 and p.status == 'UNRESOLVED'
    candidate_state = next(c for c in snap.candidates if c.candidate_id == candidate)
    assert candidate_state.learner.optimizer_steps == 6
    return {'owned_first_crossing_cursor': 7, 'tracked_through_cursor': 12,
            'constant_forecast_scores': 7, 'changing_learner_epoch_scores': 12,
            'three_event_epochs': 4, 'optimizer_commits': 6,
            'scalar_crossing_does_not_authorize_install': True}


def fair_null_audit():
    history = {}
    score_checks = 0
    for word in product((0, 1), repeat=5):
        rt, candidate = fixture(count=6, registration=register(rule(horizon=5, bits=21)))
        admitted = rt.admit_reference_persistence(candidate, 'future')
        history[()] = F(1)
        for t, label in enumerate(word):
            event(rt, label)
            history[word[:t+1]] = identity(rt, admitted.identity_id).wealth
        score_checks += check_snapshot(owned(rt))
        assert rt.reference_persistence_result(admitted.identity_id).status == 'UNRESOLVED'
    comparisons = 0
    for past, wealth in history.items():
        if len(past) < 5:
            assert (history[past+(0,)]+history[past+(1,)])/2 <= wealth
            comparisons += 1
    return {'actual_fair_label_words': 32, 'owned_score_checks': score_checks,
            'conditional_wealth_inequalities': comparisons}


def failure_audit():
    r = rule()
    # The computed event and the old owned curve both survive a failed crossing
    # publication. Neither helper output nor event alone can confer authority.
    rt, candidate = fixture(registration=register(r))
    admitted = rt.admit_reference_persistence(candidate, 'future')
    for _ in range(6):
        event(rt, 0)
    before = identity(rt, admitted.identity_id)
    original = rt._allocate
    seen = []

    def refuse_crossing(owner, objects):
        if any(o.spec.kind == 'reference_persistence_state' and o.value.status == 'REFERENCE_CROSSED' for o in objects):
            seen.append(True)
            raise ResourceExceeded('injected mixture crossing retention failure')
        return original(owner, objects)

    with patch.object(rt, '_allocate', side_effect=refuse_crossing):
        event(rt, 0)
    snap = owned(rt)
    assert seen == [True] and check_snapshot(snap) == 7
    after = identity(rt, admitted.identity_id)
    assert after.mixture_coefficients == before.mixture_coefficients and after.wealth == before.wealth
    assert after.status == 'UNRESOLVED' and after.crossing_cursor is None
    assert snap.persistence_events[-1].wealth_after >= 4 and not snap.halted
    event(rt, 1)
    assert identity(rt, admitted.identity_id) == after and rt.snapshot().alpha_spent == F(1, 4)

    # The new fee is charged before entering the arithmetic, at an immutable
    # cap measured from an otherwise identical actual root.
    entered = []
    cfg = contract(cap=3, peak=1)
    rt, candidate = fixture(cfg=cfg, registration=register(r))
    rt.admit_reference_persistence(candidate, 'future')
    real_step = kernel.next_mixture

    def capture(*args, **kwargs):
        entered.append(rt._ledger.snapshot()['spent']['compiler']['work'])
        return real_step(*args, **kwargs)

    with patch.object(kernel, 'next_mixture', side_effect=capture):
        event(rt, 0)
    assert len(entered) == 1
    cap = entered[0]-kernel.step_work(0)
    limited = replace(cfg, limits=limits(work_cap=cap))
    rt, candidate = fixture(cfg=limited, registration=register(r))
    admitted = rt.admit_reference_persistence(candidate, 'future')
    assert identity(rt, admitted.identity_id).status == 'ACTIVE'
    with patch.object(kernel, 'next_mixture', side_effect=AssertionError('unpaid mixture arithmetic')):
        event(rt, 0)
    snap = owned(rt)
    assert snap.alpha_spent == F(1, 4) and not snap.persistence_events
    assert identity(rt, admitted.identity_id).status == 'UNRESOLVED'

    # Admission also spends alpha before its prepaid seed can fail. A failed
    # identity has no curve and cannot be revived by the next observation.
    initialization = []
    rt, candidate = fixture(cfg=cfg, registration=register(r))
    real_initial = kernel.initial_coefficients

    def capture_initial(*args, **kwargs):
        initialization.append(rt._ledger.snapshot()['spent']['compiler']['work'])
        return real_initial(*args, **kwargs)

    with patch.object(kernel, 'initial_coefficients', side_effect=capture_initial):
        rt.admit_reference_persistence(candidate, 'future')
    assert len(initialization) == 1
    initial_cap = initialization[0]-kernel.initial_work()
    rt, candidate = fixture(cfg=replace(cfg, limits=limits(work_cap=initial_cap)), registration=register(r))
    with patch.object(kernel, 'initial_coefficients', side_effect=AssertionError('unpaid mixture seed')):
        admitted = rt.admit_reference_persistence(candidate, 'future')
    snap = owned(rt)
    p = identity(rt, admitted.identity_id)
    assert p.status == 'UNRESOLVED' and p.mixture_coefficients is None
    assert snap.alpha_spent == F(1, 4) and not snap.persistence_events

    # A real operand limit, without a patched arithmetic failure. Admission
    # fits; the first score's product cannot be proved to fit in 128 bits.
    bit_cfg = replace(cfg, reference_integer_bits=128)
    rt, candidate = fixture(cfg=bit_cfg, registration=register(rule(bits=124, terms=1)))
    admitted = rt.admit_reference_persistence(candidate, 'future')
    before = identity(rt, admitted.identity_id)
    assert before.status == 'ACTIVE'
    event(rt, 0)
    snap = owned(rt)
    after = identity(rt, admitted.identity_id)
    assert after.status == 'UNRESOLVED' and 'mixture product' in after.reason
    assert after.mixture_coefficients == before.mixture_coefficients and after.wealth == before.wealth
    assert not snap.persistence_events and snap.alpha_spent == F(1, 4)
    assert not snap.halted and snap.observations[-1].target == 0

    # A numerical failure keeps the previous curve; an unexpected backend
    # failure additionally halts the ordinary root and retains the target.
    for error in (ArithmeticUnresolved('injected curve bit exhaustion'), RuntimeError('injected curve backend failure')):
        rt, candidate = fixture(registration=register(r))
        admitted = rt.admit_reference_persistence(candidate, 'future')
        event(rt, 0)
        before = identity(rt, admitted.identity_id)
        with patch.object(kernel, 'next_mixture', side_effect=error):
            if isinstance(error, ArithmeticUnresolved):
                event(rt, 1)
            else:
                from ingress_audit_support import deliver_context
                from audit_reference_construction import domain
                deliver_context(rt, 'observation-1', domain(1)[0])
                rejects(lambda: rt.observe(1), RuntimeError)
        snap = owned(rt)
        after = identity(rt, admitted.identity_id)
        assert after.status == 'UNRESOLVED' and after.mixture_coefficients == before.mixture_coefficients
        assert after.wealth == before.wealth and snap.observations[-1].target == 1
        assert bool(snap.halted) == (not isinstance(error, ArithmeticUnresolved))
        assert rt.reference_persistence_result(admitted.identity_id).status == 'UNRESOLVED'
    return {'crossing_retention_failure_keeps_old_owned_curve': True,
            'retained_numerical_threshold_has_no_crossing_authority': True,
            'immutable_work_cap_refuses_before_arithmetic': cap,
            'immutable_admission_cap_refuses_before_seed': initial_cap,
            'actual_integer_limit_refuses_with_old_curve': {'bit_limit': 128, 'coefficient_grid_bits': 124},
            'arithmetic_and_unexpected_failures_cannot_resume': True}


def paired_audit():
    import audit_paired_cpu_persistence as paired
    from ingress_audit_support import deliver_context
    from audit_reference_construction import domain

    def registration(bound=F(3, 4), horizon=10):
        return PersistenceContract(F(3, 4), tuple(rule(label=label, path=path, bound=bound, horizon=horizon)
            for label, path in (('ref', REFERENCE_PATH), ('finite', FLOAT64_PATH))))

    # The reference has real positive gains that actual binary64 mass storage
    # loses. An owned adaptive reference crossing still cannot fill that path.
    delta = F(1, 1 << 54)
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    rt, candidate = paired.fixture(cfg=paired.config(cap=2+delta, peak=1, pattern=(delta,)),
        graph=graph, count=10, rate=F(0), persistence=registration(delta, 8))
    rid, fid = paired.pair(rt, candidate)
    for _ in range(8):
        event(rt, 0)
    snap = owned(rt)
    score_checks = check_snapshot(snap)
    ref, finite = identity(rt, rid), identity(rt, fid)
    assert ref.crossing_cursor == 6 and rt.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert finite.wealth == 1 and finite.crossing_cursor is None
    assert all(e.gain.lower == e.gain.upper == 0 for e in snap.persistence_events if e.identity_id == fid)
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    before = rt.snapshot()
    assert rt.install(candidate, rt.paired_persistence_result(rid, fid)).status == 'UNRESOLVED'
    assert rt.snapshot() == before

    # Refuse just the finite crossing save; the reference crossing survives,
    # but the numerical finite threshold has no retained pair authority.
    rt, candidate = paired.fixture(cfg=paired.config(cap=3, peak=1), graph=paired.SOURCE_PAIR,
        count=12, persistence=registration())
    rid, fid = paired.pair(rt, candidate)
    for _ in range(6):
        event(rt, 0)
    before = identity(rt, fid)
    allocate = rt._allocate
    failed_writes = []

    def fail_crossing(owner, objects):
        if any(o.spec.kind == 'binary64_persistence_state' and o.value.status == 'FLOAT64_CROSSED' for o in objects):
            failed_writes.append(owner)
            raise ResourceExceeded('injected owned mixture finite crossing save failure')
        return allocate(owner, objects)

    with patch.object(rt, '_allocate', side_effect=fail_crossing):
        event(rt, 0)
    snap = owned(rt)
    score_checks += check_snapshot(snap)
    after = identity(rt, fid)
    assert len(failed_writes) == 1 and rt.reference_persistence_result(rid).status == 'REFERENCE_CROSSED'
    assert after.mixture_coefficients == before.mixture_coefficients and after.wealth == before.wealth
    assert after.status == 'UNRESOLVED' and after.crossing_cursor is None
    assert rt.paired_persistence_result(rid, fid).status == 'UNRESOLVED'
    assert snap.alpha_spent == F(1, 2) and not snap.halted

    # Both complete evidence successors cross, then ordinary publication
    # fails. Both curves remain auditable history but neither is current.
    rt, candidate = paired.fixture(cfg=paired.config(cap=3, peak=1), graph=paired.SOURCE_PAIR,
        count=12, persistence=registration())
    ids = paired.pair(rt, candidate)
    for _ in range(6):
        event(rt, 0)
    before = rt.snapshot()
    deliver_context(rt, 'observation-6', domain(1)[0])
    with patch.object(rt._ledger, 'release_many', side_effect=RuntimeError('injected mixture ordinary publication failure')):
        rejects(lambda: rt.observe(0), RuntimeError)
    snap = owned(rt)
    score_checks += check_snapshot(snap)
    assert snap.halted and snap.cursor == 6 and snap.candidates == before.candidates
    assert snap.observations[-1].target == 0 and snap.alpha_spent == F(1, 2)
    assert all(identity(rt, iid).crossing_cursor == 7 for iid in ids)
    assert rt.paired_persistence_result(*ids).status == 'UNRESOLVED'
    return {'independent_curve_score_checks': score_checks,
            'reference_only_crossing_cursor': 6, 'finite_stored_mass_gain_and_wealth': ['0', '1'],
            'unretained_finite_crossing_cannot_pair': True,
            'shared_publication_failure_revokes_both_executed_crossings': True}


def audit():
    result = {'status': 'OWNED_MIXTURE_REFERENCE_AND_PAIRED_AUDIT_PASS', 'kernel': kernel_audit(),
              'owned_reference': reference_audit(), 'fair_null': fair_null_audit(), 'failures': failure_audit(),
              'paired_failures': paired_audit(),
              'scope': 'owned reference and paired binary64 failures; bounded profile/install evidence is separate'}
    assert 'torch' not in sys.modules
    return result


def profile_worker(path):
    """Existing full native profile/install fixture with a fixed new rule."""
    import audit_simplex_learner as native
    import audit_paired_cpu_persistence as paired
    import audit_reference_persistence as reference
    notes, replayed = {}, {}
    original_validate = native.validate_residency

    def declaration(**kwargs):
        horizon = kwargs['horizon']
        return PersistenceContract(F(3, 4), tuple(rule(label=label, path=score_path,
            bound=F(13, 8), horizon=horizon, bits=horizon+32)
            for label, score_path in (('ref', REFERENCE_PATH), ('finite', FLOAT64_PATH))))

    def independent_wealth(previous, gain, count, declaration):
        key = declaration.rule_id
        numbers, wealth = replayed.get(key, ((1 << declaration.coefficient_grid_bits,), F(1)))
        assert wealth == previous
        numbers = oracle.rounded_step(numbers, gain/(count*declaration.bound))
        wealth = oracle_wealth(numbers, declaration.coefficient_grid_bits)
        replayed[key] = numbers, wealth
        return wealth

    def validate(root):
        snapshot = original_validate(root)
        checks = check_snapshot(snapshot)
        details = []
        for p in snapshot.persistence_identities:
            prefix = p.identity_id+':mixture-epoch:'
            charges = tuple(e for e in snapshot.resources['events'] if e[1] == 'work' and e[5].startswith(prefix))
            assert [int(e[5][len(prefix):]) for e in charges] == list(range(p.epochs_completed))
            assert sum(dict(e[4])['work'] for e in charges) == sum(kernel.step_work(t) for t in range(p.epochs_completed))
            details.append({'score_path': p.rule.score_path, 'bound': str(p.rule.bound),
                'coefficient_grid_bits': p.rule.coefficient_grid_bits, 'epochs': p.epochs_completed,
                'coefficient_cells': len(p.mixture_coefficients), 'wealth': str(p.wealth),
                'crossing_cursor': p.crossing_cursor, 'paid_step_work': sum(dict(e[4])['work'] for e in charges)})
        notes.update(independent_curve_score_checks=checks, paths=details)
        return snapshot

    with patch.object(paired, 'registration', declaration), patch.object(reference, 'wealth_oracle', independent_wealth), patch.object(native, 'validate_residency', validate):
        result = native.owned(n=2, profiles=True, cuda=path == 'cuda', bounded=True)
    result['mixture'] = notes
    result['process_id'] = os.getpid()
    return result


def bounded_profile(path):
    from windows_job_audit_support import run_in_job
    import audit_simplex_learner as native
    dependencies = ('src/reference_compiler', 'scripts',
        'experiments/joint_uncertainty/predictable_mixture_state.py',
        'experiments/joint_uncertainty/simplex_gradient.py',
        'experiments/joint_uncertainty/joint_model.py',
        'experiments/adaptive_uncertainty')

    def git(*args):
        return subprocess.check_output(('git', *args), cwd=ROOT, encoding='utf-8').strip()

    source = git('rev-parse', 'HEAD')
    assert not git('status', '--porcelain', '--', *dependencies), 'commit the development execution dependencies first'
    directory = Path(tempfile.mkdtemp(prefix='fp-mixture-audit-', dir=ROOT))
    assert directory.resolve().parent == ROOT.resolve()
    output = directory/'profile.json'
    cap = native.HOST_CAPS[path]
    record = {'path': path, 'execution_source': source, 'status': 'FAILED'}
    try:
        job = run_in_job(__file__, ('--worker', path, '--output', str(output)), commit_limit=cap, timeout_ms=180000)
        record['completed_job'] = asdict(job)
        if output.exists() and output.stat().st_size <= 262144:
            record['result'] = json.loads(output.read_text(encoding='utf-8'))
        assert job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
        assert job.attached_before_resume and job.peak_job_commit <= cap
        result = record['result']
        assert result['process_id'] == job.process_id == result['host']['process_id']
        assert result['host']['creation_100ns'] == job.process_creation_100ns
        assert git('rev-parse', 'HEAD') == source and not git('status', '--porcelain', '--', *dependencies)
        record['status'] = 'PASS'
    except Exception as exc:
        # Preserve a failed bounded attempt as evidence rather than losing its
        # source, exit status and physical peak to an assertion in the parent.
        record['failure'] = {'type': type(exc).__name__, 'reason': str(exc)}
    finally:
        output.unlink(missing_ok=True)
        directory.rmdir()
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--profile-cpu', action='store_true')
    parser.add_argument('--profile-cuda', action='store_true')
    parser.add_argument('--worker', choices=('cpu', 'cuda'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert bool(args.worker) == bool(args.output)
    failed = False
    if args.worker:
        assert not (args.write or args.profile_cpu or args.profile_cuda)
        try:
            result = profile_worker(args.worker)
        except Exception as exc:
            failed = True
            result = {'status': 'FAILED', 'process_id': os.getpid(),
                      'failure': {'type': type(exc).__name__, 'reason': str(exc),
                                  'traceback': traceback.format_exc(limit=8)[-4000:]}}
    else:
        result = audit()
        previous = json.loads(OUTPUT.read_text(encoding='utf-8')).get('bounded_profiles', []) if args.write and OUTPUT.exists() else []
        paths = tuple(path for path, enabled in (('cpu', args.profile_cpu), ('cuda', args.profile_cuda)) if enabled)
        if paths:
            current = [bounded_profile(path) for path in paths]
            previous.extend(current)
            failed = any(item['status'] != 'PASS' for item in current)
            result['status'] = 'OWNED_MIXTURE_PROFILE_AUDIT_FAILED' if failed else 'OWNED_MIXTURE_PROFILE_AUDIT_PASS'
            result['profile_request'] = list(paths)
        if previous:
            result['bounded_profiles'] = previous
            result['scope'] += '; bounded profile attempts retained with their own source, path and status'
    text = json.dumps(result, indent=2)+'\n'
    if args.worker:
        args.output.write_text(text, encoding='utf-8')
    elif args.write:
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
    if failed:
        raise SystemExit(1)
