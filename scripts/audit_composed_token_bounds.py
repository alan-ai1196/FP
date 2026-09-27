"""Exact and complete CPU Runtime controls for owned native gradient composition.

No corpus, CUDA authority, wall-time improvement or class certificate. The
old batch commit, physical event graph, fresh reads and complete records stay.
"""
from dataclasses import replace
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from audit_owned_token_learner import fixture, registration
from audit_token_cuda_owner import cuda_contract
from audit_token_snapshot_bounds import cpu_device, phase_frame
from audit_token_reporting import report_registration
from audit_shared_cuda_retention import STORAGE
from audit_reference_construction import validate_residency, limits
from fp_reference import ReferenceCompilerRuntime, runtime, token_cuda_prefix as execution
from fp_reference import token_batch as ref, token_gradient_forest as forest
from fp_reference.token_execution import TokenState
from fp_reference.token_cuda_state import LeafWords
from fp_reference.profile import ProfileSpec
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded
from fp_reference.token_enclosures import EnclosureUnresolved

CAP = 1 << 20


def rejects(action, errors=(ValueError, TypeError, AttributeError, ContractError)):
    try:
        action()
    except errors:
        return
    raise AssertionError('invalid native composition operation admitted')


def primitives():
    points = (F(-2**53), F(-1, 3), F(-1, 2**1075), F(0), F(1, 2**1074), F(1), F(2**53))
    cases = merges = 0
    for values in product(points, repeat=3):
        blocks, rows = (), []
        for count, value in enumerate(values, 1):
            row = ref.ArrayInterval.rational(value).reshape((1,))
            rows.append(row)
            old_blocks = len(blocks)
            blocks = forest.append(blocks, row, element_cap=CAP)
            merges += old_blocks+1-len(blocks)
            result = forest.root(blocks, count, (1,), element_cap=CAP)
            control = ref.reduce_rows(ref.join(tuple(r.reshape((1, 1)) for r in rows)))
            assert forest.encode(result) == forest.encode(control)
            assert result.scalar(0).contains(sum(values[:count], F(0)))
            assert len(blocks) == count.bit_count()
            raw = blocks[-1][1]
            a = forest.decode(raw, element_cap=CAP)
            rejects(lambda: a.lower.setflags(write=True))
            cases += 1
    rejects(lambda: forest.decode(((2,), bytes(8), bytes(16)), element_cap=CAP))
    rejects(lambda: forest.decode(((True,), bytes(8), bytes(8)), element_cap=CAP))
    rejects(lambda: forest.decode(((2,), bytes(16), bytes(16)), element_cap=1))
    rejects(lambda: forest.root(((2, forest.encode(ref.ArrayInterval.zero((1,)))),), 3, (1,), element_cap=CAP))
    return dict(exact_prefix_sums=cases, carry_merges=merges,
                balanced_root_words_match=True, byte_backed_views_cannot_be_made_writable=True)


def exact_histories():
    events = coordinates = basis_coordinates = commits = histories = different = 0
    witness = None
    # All binary four-event words and the existing tied/square/zero fixtures.
    for unit, kind, word in product((1, 2, 4, 8), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, exact = fixture(unit, kind)
        origin = ref.Origin.from_native(exact, element_cap=CAP)
        kernel, cache, windows, targets = ref.Kernel(d, element_cap=CAP), forest.empty(), (), ()
        for target in word:
            window = exact.source_window()
            windows, targets = windows+(window,), targets+(target,)
            leaf = kernel.prefix(origin, (window,), (target,))
            old_cache, old_image = cache, pack(cache)
            cache = forest.extend(cache, leaf, element_cap=CAP)
            embedding_counts = Counter(a for w in windows for a in set(w.past))
            target_counts = Counter(targets)
            payload = sum(len(raw) for blocks in (cache[1], cache[2],
                *(f for _, (_, f) in cache[3]), *(f for _, (_, f) in cache[4]))
                for _, interval in blocks for raw in interval[1:])
            expected_payload = 16*((d.slots+d.output.features)*len(targets).bit_count()+
                d.width*sum(n.bit_count() for n in embedding_counts.values())+
                d.output.features*sum(n.bit_count() for n in target_counts.values()))
            assert payload == expected_payload
            assert pack(old_cache) == old_image
            # Modifying disposable producer arrays cannot modify a cache leaf.
            image = pack(cache)
            leaf.core.lower.fill(999)
            assert pack(cache) == image
            exact = exact.observe(exact.predict(window), target, window=window)
            unit_recipe = ref.Unit(origin, windows, targets)
            current = forest.view(cache, unit_recipe, element_cap=CAP)
            baseline = kernel.prefix(origin, windows, targets)
            for slot in range(d.slot_count):
                value, batch_value = current.gradient(slot), baseline.gradient(slot)
                assert value.contains(exact.gradient(slot)) and batch_value.contains(exact.gradient(slot))
                if (value.lower, value.upper) != (batch_value.lower, batch_value.upper):
                    different += 1
                    if witness is None:
                        witness = dict(unit=unit, initializer=kind, targets=list(targets), slot=slot,
                            exact=str(exact.gradient(slot)), composed=[value.lower.hex(), value.upper.hex()],
                            batch=[batch_value.lower.hex(), batch_value.upper.hex()])
                coordinates += 1
            for k, value in enumerate(exact.output.common):
                assert current.common.scalar(k).contains(value)
                basis_coordinates += 1
            corrections = dict(exact.output.corrections)
            for i, label in enumerate(current.correction_ids):
                for k, value in enumerate(corrections[int(label)]):
                    assert current.corrections.scalar((i, k)).contains(value)
                    basis_coordinates += 1
            assert not hasattr(current, 'mass') and not hasattr(current, 'commit')
            if len(targets) < unit:
                prediction = kernel.predict(current)
                wanted = exact.predict()
                assert prediction.normalizer.scalar(0).contains(wanted.output.normalizer)
                for i, value in enumerate(wanted.values):
                    assert prediction.values.scalar((i, 0)).contains(value)
            else:
                rejects(lambda: kernel.predict(current))
                # The actual native U still uses the independent full batch.
                origin, exact = baseline.commit(), exact.commit()
                assert all(origin.parameter(i) == exact.parameter(i) for i in range(d.slot_count))
                cache, windows, targets = forest.empty(), (), ()
                commits += 1
            events += 1
        histories += 1
    assert witness is not None
    # Original windows can be repeated or out of source order in paid profiles.
    profiles = 0
    for word in product((0, 1), repeat=4):
        d, exact = fixture(4, 'mixed')
        origin, cache = ref.Origin.from_native(exact, element_cap=CAP), forest.empty()
        kernel = ref.Kernel(d, element_cap=CAP)
        windows, targets = (), ()
        for index in (3, 0, 3, 1):
            window, target = d.sources.window(word, index), word[index]
            windows, targets = windows+(window,), targets+(target,)
            cache = forest.extend(cache, kernel.prefix(origin, (window,), (target,)), element_cap=CAP)
            exact = exact.observe(exact.predict(window), target, window=window)
            view = forest.view(cache, ref.Unit(origin, windows, targets), element_cap=CAP)
            assert all(view.gradient(i).contains(exact.gradient(i)) for i in range(d.slot_count))
            coordinates += d.slot_count
        profiles += 1
    return dict(histories=histories, events=events, exact_gradient_coordinates=coordinates,
        exact_readout_basis_coordinates=basis_coordinates, unchanged_exact_commits=commits,
        repeated_out_of_order_profiles=profiles, differing_batch_gradient_intervals=different,
        endpoint_non_equivalence_witness=witness, complete_input_recipe_retained=True)


def tensor_lowerings():
    # Real typed CPU tensor arenas exercise both storage modes and grouping.
    # They do not bind CUDA or grant actual-device authority.
    import torch
    import audit_owned_token_reuse as storage
    original = storage.cuda_contract
    rows = []
    for reuse in (False, True):
        outcomes = []
        for enabled in (False, True):
            def cfg(*args, **kwargs):
                return replace(original(*args, **kwargs), composed_native=enabled, grouped_reads=True)
            with patch.object(storage, 'cuda_contract', cfg):
                outcomes.append(storage.trajectory((0, 1, 1, 0)*2, reuse=reuse, shared=True, unit=4))
        for key in ('report', 'peak', 'cumulative', 'retired', 'phases'):
            assert outcomes[0][key] == outcomes[1][key], key
        rows.append(dict(reuse=reuse, checked_phases=outcomes[1]['phases'],
            peak_bytes=outcomes[1]['peak'], cumulative_bytes=outcomes[1]['cumulative'],
            retired_generations=outcomes[1]['retired']))
    assert not torch.cuda.is_initialized()
    return dict(paired_histories=2, rows=rows, grouped_reads_enabled_in_both_arms=True,
                identical_physical_extent_retirements_and_reports=True, cuda_context_created=False)


def owner_run(word, unit, enabled, *, profile=False, shared=True):
    cc, program, online, reporting = report_registration(unit, len(word), 2)
    cc = replace(cc, limits=limits(256 << 20, 10**14))
    if profile:
        online = replace(online, profiles=(ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2),))
    sizes, captures = [], [0]
    original_bound, original_capture = ref.Kernel._bound, LeafWords.capture.__func__
    def bound(kernel, retained):
        sizes.append(len(retained.targets))
        return original_bound(kernel, retained)
    def capture(cls, leaf, backend):
        captures[0] += 1
        return original_capture(cls, leaf, backend)
    with cpu_device(), patch.object(runtime.secrets, 'token_hex', return_value='native-forest-control'), \
            patch.object(ref.Kernel, '_bound', bound), patch.object(LeafWords, 'capture', classmethod(capture)):
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            cuda=replace(cuda_contract(cc.initializer_pattern), composed_native=enabled),
            shared_storage=STORAGE if shared else None)
        frozen = []
        for i, target in enumerate(word):
            if profile and i == 4:
                result = rt.construct_candidate(program, profile_id='reverse-repeat')
                assert result.status == 'BUILT_REFERENCE', result.reason
            result = rt.predict_next(f'train/{i}', encode_context(()))
            assert result.status == 'PREDICTED_REFERENCE', result.reason
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE', result.reason
            frozen.append((rt.snapshot(), tuple(pack(p) for p in rt.snapshot().cuda.phases)))
        assert rt.begin_report().status == 'REPORTING'
        for i, target in enumerate((0, 1)):
            result = rt.predict_report(f'report/{i}')
            assert result.status == 'PREDICTED_REPORT', result.reason
            result = rt.observe_report(target)
            assert result.status in ('SCORED_REPORT', 'COMPLETE_REPORT'), result.reason
        snapshot = validate_residency(rt)
        for old, packed in frozen:
            assert tuple(pack(p) for p in old.cuda.phases) == packed
        assert all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in snapshot.cuda.phases)
        phases = []
        entries = dict(snapshot.cuda.native_bounds)
        for phase in snapshot.cuda.phases:
            plan = dict(phase.execution_plan)
            if enabled:
                version, cache = plan.pop('native_gradient_cache')
                assert version == forest.VERSION
                assert entries[phase.object_id] == (forest.binding(phase.reference), cache)
                assert cache[0] == phase.reference.unit_count
                # Canonical frame retains the entire new cache and reference.
                frame = phase_frame(snapshot, phase.object_id, shared)
                assert int.from_bytes(frame[:8], 'big') == len(pack(phase))
                assert frame[8:8+len(pack(phase))] == pack(phase)
            phases.append(pack(replace(phase, relation=None, execution_plan=plan)))
        report = snapshot.token_report
        native_report, physical_report = report.native_total, report.physical_total
    return dict(phases=phases, learners=tuple(c.learner for c in snapshot.candidates),
        report=(native_report, physical_report), event_rows=sum(sizes), bound_calls=len(sizes),
        leaf_captures=captures[0], checked_words=sum(p.forward_operations for p in snapshot.cuda.phases))


def owned_histories():
    rows, phases, pairs = [], 0, 0
    cases = [(word, 2, False, True) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0)*4, 8, False, True), ((0, 1, 1, 0)*2, 4, False, True),
              ((0, 1, 1, 0), 1, False, False), ((0, 1, 1, 0, 0, 1), 2, True, True)]
    for word, unit, profile, shared in cases:
        before, after = (owner_run(word, unit, enabled, profile=profile, shared=shared) for enabled in (False, True))
        for key in ('phases', 'learners', 'report', 'leaf_captures', 'checked_words'):
            assert before[key] == after[key], key
        if not profile:
            assert after['event_rows'] == 2*len(word)
            assert after['bound_calls'] == len(word)+len(word)//unit
            assert before['event_rows'] == len(word)*(3*unit+1)//2
        rows.append(dict(unit=unit, events=len(word), profile=profile, shared=shared,
            baseline_event_rows=before['event_rows'], composed_event_rows=after['event_rows'],
            baseline_bound_calls=before['bound_calls'], composed_bound_calls=after['bound_calls']))
        phases += len(after['phases'])
        pairs += 1
    return dict(paired_histories=pairs, identical_physical_and_native_phase_bodies=phases,
        interval_diagnostics_and_new_cache_excluded_from_byte_comparison=True,
        identical_fresh_leaf_capture_and_primitive_word_counts=True,
        identical_complete_learners_and_reports=True,
        rows=[dict(key, paired_histories=count) for key, count in Counter(tuple(row.items()) for row in rows).items()])


def failures():
    outcomes = []
    for mode in ('unpaid', 'arithmetic', 'memory', 'retention', 'changed-leaf', 'public-cache', 'changed-origin', 'changed-record'):
        cc, p, online, _ = report_registration(4, 4, 1)
        cc = replace(cc, limits=limits(256 << 20, 10**14))
        with cpu_device():
            rt = ReferenceCompilerRuntime(cc, p, online=online,
                cuda=replace(cuda_contract(cc.initializer_pattern), composed_native=True), shared_storage=STORAGE)
            for i in range(2):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(i).status == 'OBSERVED_REFERENCE'
            before = rt.snapshot()
            learner, identity = before.candidates[0].learner, dict(before.cuda.current)[before.deployed_id]
            original_bytes = tuple(pack(p) for p in before.cuda.phases)
            if mode == 'changed-leaf':
                rt._cuda._values[identity].state.leaves[0].values[0, 0] += 1
                rejects(lambda: rt.predict_next('train/2', encode_context(())), RuntimeError)
            elif mode == 'public-cache':
                public = next(p for p in before.cuda.phases if p.object_id == identity)
                rejects(lambda: public.execution_plan.__setitem__('native_gradient_cache', (forest.VERSION, forest.empty())))
                exposed = dict(before.cuda.native_bounds)[identity]
                rejects(lambda: exposed.__setitem__(1, forest.empty()))
                # Ordinary dataclass __dict__ writes to a diagnostic phase do
                # not replace the private value used by the next bound query.
                public.__dict__['execution_plan'] = {'native_gradient_cache': (forest.VERSION, forest.empty())}
                assert rt.predict_next('train/2', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt._cuda._native_bounds[identity] == exposed
                outcomes.append(mode)
                continue
            elif mode in ('changed-origin', 'changed-record'):
                # Direct helper calls are adversarial diagnostics only; there
                # is no public Runtime ingress for these forged references.
                if mode == 'changed-origin':
                    raw = bytearray(learner.origin.core)
                    raw[0] ^= 1
                    altered = replace(learner, origin=replace(learner.origin, core=bytes(raw)))
                else:
                    altered = replace(learner, targets=(1, 0))
                rejects(lambda: forest.prepare(rt._cuda, 'unissued', identity, 'predict', altered))
                assert 'unissued' not in rt._cuda._native_bounds
                outcomes.append(mode)
                continue
            else:
                assert rt.predict_next('train/2', encode_context(())).status == 'PREDICTED_REFERENCE'
                entry_count = len(rt._cuda._native_bounds)
                if mode == 'unpaid':
                    original = rt._ledger.charge_work
                    def deny(role, debit, **kwargs):
                        if ':cuda:ordinary:observe:' in kwargs.get('note', ''):
                            raise ResourceExceeded('unpaid native composition')
                        return original(role, debit, **kwargs)
                    hook = patch.object(rt._ledger, 'charge_work', deny)
                elif mode in ('arithmetic', 'memory'):
                    original_extend = forest.extend
                    def stop(*args, **kwargs):
                        result = original_extend(*args, **kwargs)
                        raise (MemoryError if mode == 'memory' else EnclosureUnresolved)('after new gradient computation')
                    hook = patch.object(forest, 'extend', stop)
                else:
                    hook = patch.object(rt._reference_archive, 'prepare_frame', side_effect=ResourceExceeded('native cache retention'))
                with hook:
                    if mode == 'memory':
                        rejects(lambda: rt.observe(1), MemoryError)
                    else:
                        result = rt.observe(1)
                        assert result.status == 'UNRESOLVED', result
                now = rt.snapshot()
                assert now.observations[-1].target == 1 and len(now.observations) == 3
                if mode == 'unpaid':
                    assert len(rt._cuda._native_bounds) == entry_count
                if mode == 'retention':
                    assert len(rt._cuda._native_bounds) == entry_count+1
                    failed = now.cuda.phases[-1]
                    assert failed.status == 'UNRESOLVED'
                    assert rt._cuda._native_bounds[failed.object_id][1][0] == 3
                    assert failed.object_id not in dict(now.cuda.current).values()
            now = rt.snapshot()
            assert now.cursor == 2 and now.candidates[0].learner == learner
            assert tuple(pack(p) for p in before.cuda.phases) == original_bytes
            outcomes.append(mode)
    return outcomes


def audit():
    p, exact = primitives(), exact_histories()
    print('PASS exact primitive and native-history controls', flush=True)
    owned = owned_histories()
    print('PASS paired complete Runtime histories', flush=True)
    refused = failures()
    assert 'torch' not in sys.modules
    storage = tensor_lowerings()
    return dict(status='PASS_COMPOSED_TOKEN_NATIVE_BOUNDS_CPU', primitive=p, exact=exact, owned=owned,
        failure_and_binding_controls=refused, tensor_storage=storage,
        full_unit512_derived=dict(old_native_event_rows=393472,
            composed_native_event_rows=1024, unchanged_physical_leaf_captures=917760), scope=__doc__.strip())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('native composition audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_COMPOSED_TOKEN_BOUNDS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
