"""Exact complete-ledger/Runtime transition controls; no corpus/device timing."""
from contextlib import nullcontext, ExitStack
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, owned_maps
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceLedger, ResourceLimits, ObjectSpec
from audit_owned_token_learner import fixture, registration
from audit_reference_construction import limits, validate_residency
from audit_shared_token_retention import STORAGE
from owned_transition_audit_support import BASELINE, ledger_class, original_transitions


def equivalent(left, right):
    a, b = left.snapshot(), right.snapshot()
    assert a == b and pack(a) == pack(b)
    # Mapping insertion order is a public observation, even when a canonical
    # serializer sorts keys. It must not disappear into equal byte encodings.
    for field in ('owners', 'objects'):
        assert tuple(a[field]) == tuple(b[field])
    for key in a['objects']:
        assert tuple(a['objects'][key]['references']) == tuple(b['objects'][key]['references'])
    # Independently recompute every current total from complete leaves using
    # the original scanner, never the candidate's augmented answer.
    total, roles = OLD._residency(right, dict(right._objects), {key: dict(v) for key, v in right._refs.items()})
    assert total == b['current'] and roles == b['role_current']


OLD = ledger_class()


def ledger_decisions():
    profiles = ((8, 5, 6), (5, 5, 5), (8, 8, 8))
    leases = ((), (('A', 1),), (('B', 1),), (('C', 1),), (('A', 1), ('B', 2)),
        (('A', 2), ('C', 1)), (('B', 1), ('C', 2)), (('A', 1), ('B', 1), ('C', 1)))
    object_spec = lambda key, n: ObjectSpec(key, 'audit', {'bytes': n, 'objects': 1}, 'owned-transition')
    cases = []
    for owner in ('A', 'B', 'C', 'closed', 'unknown'):
        for specs in ((), (object_spec('new', 0),), (object_spec('new', 4),),
                      (object_spec('x', 1),), (object_spec('retired', 1),),
                      (object_spec('new', 1), object_spec('new', 2)),
                      (object_spec('new', 1), object_spec('other', 2))):
            cases.append(('allocate', (owner, specs), {}))
        for obj, count in product(('x', 'y', 'missing'), (1, 2)):
            cases += [('acquire', (owner, obj), {'count': count}), ('release', (owner, obj), {'count': count})]
    for source, dest, obj, count in product(('A', 'B', 'C'), ('A', 'B', 'C'), ('x', 'y'), (1, 2)):
        cases.append(('prepare_transfer', (((source, dest, obj, count),),), {}))
    for releases in ((), (('A', 'x', 1),), (('A', 'x', 1), ('A', 'x', 1)),
                     (('A', 'x', 1), ('C', 'y', 2)), (('A', 'x', 0),)):
        cases.append(('release_many', (releases,), {}))
    for owner in ('A', 'B', 'C', 'closed', 'unknown'):
        cases.extend((('release_owner', (owner,), {}), ('close_owner', (owner,), {})))
        cases.append(('prepare_transfer', ((), (), (owner,)), {}))
    for role, amount in product(('compiler', 'deployment', 'unknown'), (0, 5, 101)):
        cases.append(('charge_work', (role, {'work': amount}), {}))
    states = decisions = accepted = refused = 0
    for profile, owned in product(profiles, product(leases, repeat=2)):
        cap, compiler, deployment = profile
        cfg = ResourceLimits({'bytes': cap, 'objects': 4},
            {'compiler': {'bytes': compiler, 'objects': 4}, 'deployment': {'bytes': deployment, 'objects': 4}},
            {role: {'work': 100} for role in ('compiler', 'deployment')})
        pair = [OLD(cfg), ResourceLedger(cfg)]
        errors = []
        for ledger in pair:
            try:
                for owner, role in (('A', 'compiler'), ('B', 'compiler'), ('C', 'deployment'), ('closed', 'compiler')):
                    ledger.register_owner(owner, role)
                ledger.close_owner('closed')
                ledger.allocate('A', (object_spec('retired', 0),))
                ledger.release('A', 'retired')
                for obj, size, refs in zip(('x', 'y'), (2, 3), owned):
                    if refs:
                        ledger.allocate(refs[0][0], (object_spec(obj, size),))
                        for index, (owner, count) in enumerate(refs):
                            extra = count-int(index == 0)
                            if extra:
                                ledger.acquire(owner, obj, count=extra)
                errors.append(None)
            except ContractError as error:
                errors.append((type(error).__name__, str(error)))
        assert errors[0] == errors[1]
        if errors[0] is not None:
            continue
        equivalent(*pair)
        states += 1
        for name, args, kwargs in cases:
            trials = [ledger._detached() for ledger in pair]
            answers, before = [], [pack(ledger.snapshot()) for ledger in pair]
            for ledger in trials:
                try:
                    result = getattr(ledger, name)(*args, **kwargs)
                    answers.append((None, result))
                except ContractError as error:
                    answers.append(((type(error).__name__, str(error)), None))
            assert answers[0][0] == answers[1][0], (owned, name, args, answers)
            equivalent(*trials)
            equivalent(*pair)
            assert before == [pack(ledger.snapshot()) for ledger in pair]
            if answers[0][0] is None:
                if answers[0][1] is not None:
                    equivalent(answers[0][1], answers[1][1])
                    # Prepare forks retain all old history and cannot mutate
                    # the predecessor through future appends or leaf updates.
                    for result in (answers[0][1], answers[1][1]):
                        result.charge_work('compiler', {'work': 1})
                    equivalent(answers[0][1], answers[1][1])
                    assert before == [pack(ledger.snapshot()) for ledger in pair]
                accepted += 1
            else:
                refused += 1
            decisions += 1
    return dict(reachable_lease_states=states, exact_transition_decisions=decisions,
        accepted=accepted, refused=refused, complete_snapshots_order_peaks_events_and_errors_equal=True,
        every_current_total_independently_scanned=True, prepared_forks_leave_predecessors_unchanged=True)


def histories():
    cases = [(word, shared, unit) for shared, unit, word in product(
        (False, True), (1, 2, 4), product((0, 1), repeat=4))]
    cases += [((0, 1, 1, 0)*16, shared, 512) for shared in (False, True)]
    targets = 0
    for word, shared, unit in cases:
        answers = []
        for old in (True, False):
            with (original_transitions() if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='owned-transition-control'):
                d, initial = fixture(unit, 'mixed')
                cc, p, online = registration(d, initial, count=len(word))
                cc = replace(cc, limits=limits(128 << 20, 10**15))
                rt = ReferenceCompilerRuntime(cc, p, online=online, shared_storage=STORAGE if shared else None)
                results = []
                for i, y in enumerate(word):
                    predicted = rt.predict_next(f'train/{i}', encode_context(()))
                    assert predicted.status == 'PREDICTED_REFERENCE'
                    observed = rt.observe(y)
                    assert observed.status == 'OBSERVED_REFERENCE'
                    results.extend((predicted, observed))
                snapshot = validate_residency(rt)
                answers.append((pack((tuple(results), snapshot)),
                    tuple(snapshot.resources['objects']), tuple(k for k, _ in snapshot.buffers)))
        assert answers[0] == answers[1]
        targets += len(word)
    return dict(paired_complete_histories=len(cases), targets_per_arm=targets,
        complete_results_states_bytes_and_insertion_order_equal=True)


def no_global_scan():
    d, initial = fixture(512, 'mixed')
    cc, p, online = registration(d, initial, count=64)
    cc = replace(cc, limits=limits(128 << 20, 10**15))
    rt = ReferenceCompilerRuntime(cc, p, online=online, shared_storage=STORAGE)
    nodes, original = [], owned_maps._make
    def count(*args):
        result = original(*args)
        nodes.append(None)
        return result
    with ExitStack() as stack:
        for method in ('__iter__', 'items', 'values'):
            stack.enter_context(patch.object(owned_maps.OwnedMap, method,
                side_effect=AssertionError('ordinary transition traversed a complete growing map')))
        stack.enter_context(patch.object(owned_maps.OwnedLog, '__iter__',
            side_effect=AssertionError('ordinary transition traversed complete event history')))
        stack.enter_context(patch.object(owned_maps, '_make', count))
        for i in range(64):
            assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(i % 2).status == 'OBSERVED_REFERENCE'
    snapshot = validate_residency(rt)
    total, roles = OLD._residency(rt._ledger, dict(rt._ledger._objects), dict(rt._ledger._refs))
    assert total == snapshot.resources['current'] and roles == snapshot.resources['role_current']
    assert len(snapshot.observations) == 64 and len(snapshot.resources['events']) == 3256
    return dict(targets=64, global_map_or_event_iterations=0, constructed_index_nodes=len(nodes),
        retained_objects=len(snapshot.resources['objects']), retained_events=len(snapshot.resources['events']),
        all_physical_buffers_and_exact_leaf_sums_checked=True)


def atomic_failures():
    cfg = ResourceLimits({'bytes': 32, 'objects': 16},
        {role: {'bytes': 32, 'objects': 16} for role in ('compiler', 'deployment')},
        {role: {'work': 1000} for role in ('compiler', 'deployment')})
    ledger = ResourceLedger(cfg)
    for owner, role in (('A', 'compiler'), ('B', 'compiler'), ('C', 'deployment')):
        ledger.register_owner(owner, role)
    make_spec = lambda key, size: ObjectSpec(key, 'audit', {'bytes': size, 'objects': 1}, 'fault-control')
    ledger.allocate('A', (make_spec('x', 4), make_spec('y', 3)))
    ledger.acquire('C', 'x')
    actions = (
        lambda x: x.allocate('A', (make_spec('new', 2), make_spec('other', 1))),
        lambda x: x.acquire('B', 'x', count=2),
        lambda x: x.release('A', 'y'),
        lambda x: x.release_many((('A', 'x', 1), ('C', 'x', 1), ('A', 'y', 1))),
        lambda x: x.prepare_transfer((('A', 'B', 'y', 1), ('C', 'A', 'x', 1))),
        lambda x: x._shrink_object(make_spec('x', 1)))
    original, checked = owned_maps._make, 0
    before = pack(ledger.snapshot())
    for action in actions:
        nodes = []
        def counted(*args):
            nodes.append(None)
            return original(*args)
        with patch.object(owned_maps, '_make', counted):
            action(ledger._detached())
        for fail_at in range(len(nodes)):
            trial, calls = ledger._detached(), []
            def failure(*args):
                if len(calls) == fail_at:
                    raise MemoryError('owned transition node preparation')
                calls.append(None)
                return original(*args)
            with patch.object(owned_maps, '_make', failure):
                try:
                    action(trial)
                except MemoryError:
                    pass
                else:
                    raise AssertionError('failed owned transition node was published')
            assert pack(trial.snapshot()) == before and pack(ledger.snapshot()) == before
            equivalent(ledger, trial)
            checked += 1
    # At common event-append failures the old and new Runtime retain the same
    # target, prior learner, work and diagnostic prefix.
    snapshots = []
    for old in (True, False):
        with (original_transitions() if old else nullcontext()), \
                patch('fp_reference.runtime.secrets.token_hex', return_value='owned-transition-failure'):
            d, initial = fixture(2, 'mixed')
            cc, p, online = registration(d, initial)
            rt = ReferenceCompilerRuntime(cc, p, online=online)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            prior = rt._candidates[rt._deployed_id].learner
            with patch.object(type(rt._ledger), '_event', side_effect=MemoryError('common event-append control')):
                try:
                    rt.observe(1)
                except MemoryError:
                    pass
                else:
                    raise AssertionError('host failure did not escape')
            assert rt._cursor == 0 and rt._observations[-1].target == 1 and rt._halted
            assert rt._candidates[rt._deployed_id].learner is prior
            snapshots.append(pack(validate_residency(rt)))
            try:
                rt.predict_next('train/0', encode_context(()))
            except ContractError:
                pass
            else:
                raise AssertionError('failed target regained continuation authority')
    assert snapshots[0] == snapshots[1]
    # Fail the new node constructor at a real pre-input and post-target port.
    # Node preparation cannot publish a partial weighted index.
    for port in ('begin', 'observe'):
        d, initial = fixture(2, 'mixed')
        cc, p, online = registration(d, initial)
        rt = ReferenceCompilerRuntime(cc, p, online=online)
        if port == 'observe':
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        with patch.object(owned_maps, '_make', side_effect=MemoryError('actual owned map allocation failed')):
            try:
                rt.begin_context('train/0') if port == 'begin' else rt.observe(1)
            except MemoryError:
                pass
            else:
                raise AssertionError('actual allocation failure did not escape')
        snapshot = validate_residency(rt)
        assert snapshot.halted is not None and snapshot.cursor == 0
        assert len(snapshot.observations) == int(port == 'observe')
        if port == 'observe':
            assert snapshot.observations[-1].target == 1
    return dict(ledger_node_allocation_failures=checked, unchanged_complete_predecessors=True,
        paired_common_event_failure_equal=True, real_runtime_node_failures=2,
        actual_revealed_target_and_terminal_authority_preserved=True)


def cpu_phases():
    import audit_owned_token_workspaces as owned
    cases = [((0, 1, 1, 0), unit, False, False, False) for unit in (1, 2, 4)]
    cases += [((0, 1, 1, 0)*2, 8, False, False, False),
        ((0, 1, 1, 0, 0, 1), 2, True, False, False),
        ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = words = body_bytes = 0
    for word, unit, profile, combined, archived in cases:
        answers = []
        for old in (True, False):
            with (original_transitions() if old else nullcontext()), patch.object(owned, 'numerical_phase', pack):
                answers.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert answers[0] == answers[1]
        phases += len(answers[0]['phases'])
        words += answers[0]['primitive_words']
        body_bytes += sum(map(len, answers[0]['phases']))
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        checked_primitive_words=words, complete_phase_bytes=body_bytes,
        frames_learners_reports_reads_allocations_retirements_equal=True,
        actual_cuda_execution=False)


def commits_and_frames_without_scans():
    def forbid(stack):
        for method in ('__iter__', 'items', 'values'):
            stack.enter_context(patch.object(owned_maps.OwnedMap, method,
                side_effect=AssertionError('commit/frame transition scanned a whole owned map')))
        stack.enter_context(patch.object(owned_maps.OwnedLog, '__iter__',
            side_effect=AssertionError('commit/frame transition scanned old resource events')))
    for shared in (False, True):
        d, initial = fixture(2, 'mixed')
        cc, p, online = registration(d, initial, count=8)
        rt = ReferenceCompilerRuntime(cc, p, online=online, shared_storage=STORAGE if shared else None)
        with ExitStack() as stack:
            forbid(stack)
            for i, y in enumerate((0, 1, 1, 0)*2):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(y).status == 'OBSERVED_REFERENCE'
        snapshot = validate_residency(rt)
        assert snapshot.cursor == 8 and sum(t.after_commit is not None for t in snapshot.event_traces) == 4
    import audit_owned_token_workspaces as owned
    from audit_owned_token_reuse import cpu_device, frames
    with cpu_device():
        rt, _ = owned.setup(True, unit=2, count=4, combined=True)
        with ExitStack() as stack:
            forbid(stack)
            for i, y in enumerate((0, 1, 1, 0)):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(y).status == 'OBSERVED_REFERENCE'
        snapshot = validate_residency(rt)
        retained = frames(snapshot, True)
        assert snapshot.cursor == 4
    return dict(native_targets=16, native_optimizer_commits=8, native_representations=2,
        cpu_tensor_targets=4, cpu_tensor_phases=len(snapshot.cuda.phases),
        full_cpu_tensor_frame_bytes_checked=retained,
        global_map_or_event_iterations=0, actual_cuda_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_TRANSITIONS_CPU', baseline_source=BASELINE, scope=__doc__.strip())
    for name, fn in (('ledger_decisions', ledger_decisions), ('histories', histories),
                     ('no_global_scan', no_global_scan), ('atomic_failures', atomic_failures),
                     ('cpu_phases', cpu_phases), ('commits_and_frames_without_scans', commits_and_frames_without_scans)):
        result[name] = fn()
        print('PASS '+name, flush=True)
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_TRANSITIONS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    main()
