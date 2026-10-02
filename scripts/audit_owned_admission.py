"""Exact admission and complete-continuation controls; no corpus/device timing."""
from contextlib import nullcontext
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, runtime, resources
from fp_reference.core import ContractError
from fp_reference.data_usage import read_sources, DataUsageLedger
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceLedger, ResourceLimits, ObjectSpec, ResourceExceeded, CostRouter
from audit_owned_token_learner import fixture, registration
from audit_reference_construction import limits, validate_residency
from audit_shared_token_retention import STORAGE
from owned_admission_audit_support import BASELINE, historical_method, historical_prediction_ports


def admission():
    original_allocate = historical_method(resources, ResourceLedger, 'allocate')
    original_prepare = historical_method(resources, ResourceLedger, 'prepare_allocation')
    shapes = ({'bytes': 6, 'objects': 3}, {'bytes': 3, 'objects': 2}, {'bytes': 6, 'objects': 3})
    proposals = [(), (object(),), (ObjectSpec('bad-shape', 'toy', {'bytes': 1}, 'audit'),)]
    atoms = [ObjectSpec(label, 'toy', {'bytes': size, 'objects': 1}, 'audit')
        for label, size in (('new', 0), ('new', 1), ('new', 2), ('huge', 8),
                            ('left', 1), ('retired', 1))]
    proposals += [(x,) for x in atoms]+list(product(atoms[:3]+[atoms[4]], repeat=2))
    states = decisions = accepted = refused = 0
    for profile, leases in product(range(3), product(((), ('A',), ('B',), ('A', 'B')), repeat=2)):
        caps = shapes[profile]
        role_caps = dict(compiler={'bytes': 1, 'objects': 1} if profile == 2 else caps, deployment=caps)
        ledger = ResourceLedger(ResourceLimits(caps, role_caps,
            {role: {'work': 1000} for role in role_caps}))
        ledger.register_owner('A', 'compiler')
        ledger.register_owner('B', 'deployment')
        ledger.register_owner('closed', 'compiler')
        ledger.close_owner('closed')
        # Actual legal construction, retirement and multi-role sharing; no
        # manually forged current totals or resource-state oracle inputs.
        with patch.object(ResourceLedger, 'allocate', original_allocate):
            ledger.allocate('A', (ObjectSpec('retired', 'toy', {'bytes': 0, 'objects': 1}, 'audit'),))
            ledger.release('A', 'retired')
            try:
                for label, size, owners in zip(('left', 'right'), (1, 2), leases):
                    if owners:
                        ledger.allocate(owners[0], (ObjectSpec(label, 'toy', {'bytes': size, 'objects': 1}, 'audit'),))
                        for other in owners[1:]:
                            ledger.acquire(other, label, count=2)
            except ResourceExceeded:
                continue
        states += 1
        before = pack(ledger.snapshot())
        for owner, request in product(('A', 'B', 'closed', 'unknown'), proposals):
            try:
                with patch.object(ResourceLedger, 'allocate', original_allocate):
                    wanted = original_prepare(ledger, owner, request)
                expected = None
            except ContractError as error:
                expected = (type(error).__name__, str(error))
            try:
                # Preflight must not derive an otherwise unused ledger clone.
                with patch.object(ResourceLedger, '_detached', side_effect=AssertionError('preflight cloned history')):
                    answer = ledger.check_allocation(owner, request)
                assert answer is None
                actual = None
            except ContractError as error:
                actual = (type(error).__name__, str(error))
            assert expected == actual, (profile, leases, owner, expected, actual)
            assert pack(ledger.snapshot()) == before
            if expected is None:
                realized = ledger._detached()
                realized.allocate(owner, request)
                assert pack(realized.snapshot()) == pack(wanted.snapshot())
                accepted += 1
            else:
                refused += 1
            decisions += 1
        # The exact complete-frame guard still precedes even owner checking.
        ledger.unregistered_future_job = object()
        for fn in (lambda: original_prepare(ledger, 'unknown', ()),
                   lambda: ledger.check_allocation('unknown', ())):
            try:
                fn()
            except ContractError as error:
                assert str(error) == 'physical preparation needs the complete registered ledger state'
            else:
                raise AssertionError('preflight ignored an unknown ledger coordinate')
    return dict(reachable_lease_states=states, exact_admission_decisions=decisions,
        accepted=accepted, refused=refused, identical_first_error_type_and_message=True,
        all_predecessor_snapshots_unchanged=True, every_accepted_allocation_matches_original=True,
        unknown_complete_frame_coordinates_refused=True, no_history_clone_in_preflight=True)


def histories():
    checked = events = 0
    cases = [(word, shared, unit) for shared, unit, word in product(
        (False, True), (1, 2, 4), product((0, 1), repeat=4))]
    cases += [((0, 1, 1, 0)*16, shared, 512) for shared in (False, True)]
    for word, shared, unit in cases:
        answers = []
        for old in (True, False):
            with (historical_prediction_ports() if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='owned-prefix-control'):
                d, initial = fixture(unit, 'mixed')
                cc, p, online = registration(d, initial, count=len(word))
                cc = replace(cc, limits=limits(128 << 20, 10**15))
                rt = ReferenceCompilerRuntime(cc, p, online=online, shared_storage=STORAGE if shared else None)
                outputs = []
                for index, target in enumerate(word):
                    outputs.append(rt.predict_next(f'train/{index}', encode_context(())))
                    assert outputs[-1].status == 'PREDICTED_REFERENCE'
                    context = rt._pending.record.sources
                    assert context.past == tuple(2 if lag > index else word[index-lag] for lag in (1, 2, 3))
                    # Retain the original family *identity*, not just equal data.
                    assert context.family is rt._online.data.source_reads.family
                    outputs.append(rt.observe(target))
                    assert outputs[-1].status == 'OBSERVED_REFERENCE'
                    # Current and arbitrarily old public wrappers cannot forge
                    # the invariant used by the next internal source read.
                    if index == 0 or index == len(word)-2:
                        exposed = rt.snapshot()
                        exposed.observations[0].__dict__.update(cursor=999, target=None)
                        exposed.observations[0].sources.__dict__['past'] = (0, 0, 0)
                snapshot = validate_residency(rt)
                assert (snapshot.cursor, len(snapshot.observations)) == (len(word), len(word))
                assert tuple(r.target for r in snapshot.observations) == word
                answers.append(pack((tuple(outputs), snapshot)))
        assert answers[0] == answers[1]
        events += len(word)
        checked += 1
    return dict(paired_complete_histories=checked, target_events_per_arm=events,
        complete_results_and_serialized_snapshots_equal=True,
        old_public_record_mutations_cannot_forge_the_prefix=True,
        original_source_family_identity_preserved=True)


def no_copy():
    class History(list):
        def __iter__(self):
            raise AssertionError('ordinary indexed source read iterated full history')
        def __getitem__(self, key):
            assert type(key) is int
            visited.append(key)
            return super().__getitem__(key)
    from audit_native_history_work import Visits
    from contextlib import ExitStack
    visited = []
    d, initial = fixture(512, 'mixed')
    cc, p, online = registration(d, initial, count=64)
    cc = replace(cc, limits=limits(128 << 20, 10**15))
    rt = ReferenceCompilerRuntime(cc, p, online=online, shared_storage=STORAGE)
    original = rt._observations
    observed = Visits()
    with ExitStack() as stack:
        observed.install(stack)
        for index in range(64):
            # Instrument only the read boundary; it never supplies a different
            # record, validates in place of Runtime, or remains as owned state.
            rt._observations = History(original)
            try:
                assert rt.predict_next(f'train/{index}', encode_context(())).status == 'PREDICTED_REFERENCE'
            finally:
                rt._observations = original
            assert rt.observe(index % 2).status == 'OBSERVED_REFERENCE'
    assert visited == [index-lag for index in range(64) for lag in range(1, min(index, 3)+1)]
    assert observed.counts['source_history_copied_slots'] == observed.counts['source_history_checked_rows'] == 0
    assert observed.counts['_detached_calls'] == observed.counts['snapshot_event_rows'] == 0
    assert len(rt._observations) == 64 and len(rt._ledger._events) == 3256
    return dict(targets=64, actual_past_target_reads=len(visited), expected=sum(min(i, 3) for i in range(64)),
        ordinary_full_history_copies=0, ordinary_full_prefix_checks=0,
        ingress_ledger_history_clones=0, internal_ledger_diagnostic_event_rows=0,
        retained_resource_events=len(rt._ledger._events), retained_observations=64,
        residency_object_visits_still_required=observed.counts['residency_object_rows'])


def continuations():
    import audit_owned_token_learner as native
    import audit_indexed_token_sources as indexed
    import audit_context_ingress as ingress
    return dict(profiles=native.profiles(), source_queries=indexed.queries_and_attacks(),
        source_funding=indexed.admission_before_decoding(), target_failures=native.retained_failures(),
        ingress_admission=ingress.admission_audit(), ingress_failures=ingress.failure_audit())


def prefix_failures():
    from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
    from audit_reference_construction import rejects
    class UnreadHistory(list):
        def __iter__(self):
            raise AssertionError('unfunded source history was copied')
        def __getitem__(self, key):
            raise AssertionError('unfunded source history was read')
    charge = CostRouter.charge_work
    def deny(router, purpose, debit, note=''):
        if note.endswith(':indexed-source-read'):
            raise ResourceExceeded('injected source funding refusal')
        return charge(router, purpose, debit, note)
    paired = 0
    for mode in ('unfunded', 'missing-prefix', 'post-reveal-memory', 'post-reveal-contract'):
        answers = []
        for old in (True, False):
            with (historical_prediction_ports() if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='owned-prefix-failure'):
                d, initial = fixture(2, 'mixed')
                cc, p, online = registration(d, initial, count=6)
                rt = ReferenceCompilerRuntime(cc, p, online=online)
                for index, target in enumerate((0, 1, 1, 0)):
                    assert rt.predict_next(f'train/{index}', encode_context(())).status == 'PREDICTED_REFERENCE'
                    assert rt.observe(target).status == 'OBSERVED_REFERENCE'
                original = rt._observations
                if mode == 'unfunded':
                    rt._observations = UnreadHistory(original)
                    try:
                        with patch.object(CostRouter, 'charge_work', deny), \
                                patch.object(runtime, 'TokenContext', side_effect=AssertionError('unfunded context built')) as context:
                            assert rt.predict_next('train/4', encode_context(())).status == 'UNRESOLVED'
                            assert not context.called
                    finally:
                        rt._observations = original
                elif mode == 'missing-prefix':
                    # A selected private-corruption control, not a legal
                    # transition or an arbitrary-corruption equivalence claim.
                    original.pop()
                    rejects(lambda: rt.predict_next('train/4', encode_context(())))
                    assert rt._halted is not None
                else:
                    assert rt.predict_next('train/4', encode_context(())).status == 'PREDICTED_REFERENCE'
                    error = MemoryError if mode == 'post-reveal-memory' else ContractError
                    # The earliest fallible call after append is outside
                    # observe's inner handler. Even this prefix cannot resume.
                    with patch.object(DataUsageLedger, 'record', side_effect=error('post-reveal prefix control')):
                        rejects(lambda: rt.observe(1), error)
                    assert len(original) == 5 and original[-1].target == 1
                    assert rt._cursor == 4 and rt._event_phase != 'idle'
                    if error is MemoryError:
                        assert rt._halted is HOST_ALLOCATION_FAILURE
                rejects(lambda: rt.predict_next('train/4', encode_context(())))
                rejects(lambda: rt.begin_context('train/4'))
                rejects(lambda: rt.observe(1))
                answers.append(pack(validate_residency(rt)))
        assert answers[0] == answers[1], mode
        paired += 1
    # The generic helper is still a boundary for caller-supplied histories and
    # must continue validating the entire prefix, including old rows outside L.
    records = tuple(original[:4])
    for bad in (records[:-1], (replace(records[0], cursor=99),)+records[1:],
                (replace(records[0], target=None),)+records[1:]):
        rejects(lambda: read_sources(online.data, 4, (), bad))
    return dict(paired_failures=paired, complete_failed_snapshots_equal=True,
        unfunded_history_reads_and_context_allocations=0,
        post_reveal_failures_cannot_resume=True,
        generic_helper_malformed_prefix_refusals=3)


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
            with (historical_prediction_ports() if old else nullcontext()), \
                    patch.object(owned, 'numerical_phase', pack):
                answers.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert answers[0] == answers[1]
        phases += len(answers[0]['phases'])
        words += answers[0]['primitive_words']
        body_bytes += sum(map(len, answers[0]['phases']))
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        checked_primitive_words=words, complete_phase_bytes=body_bytes,
        frames_learners_reports_reads_allocations_retirements_equal=True,
        actual_cuda_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_ADMISSION_CPU', baseline_source=BASELINE, scope=__doc__.strip())
    for name, fn in (('admission', admission), ('histories', histories),
                     ('no_copy', no_copy), ('continuations', continuations),
                     ('prefix_failures', prefix_failures), ('cpu_phases', cpu_phases)):
        result[name] = fn()
        print('PASS '+name, flush=True)
    import torch
    assert not torch.cuda.is_initialized()
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_ADMISSION_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    # This historical claim compares the original full-scanning ledger ports;
    # later immutable-map accounting has its own complete transition audit.
    from owned_transition_audit_support import historical_ledger
    with historical_ledger('a694441'):
        main()
