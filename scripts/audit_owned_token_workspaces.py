"""Complete Runtime controls for sealed historical token workspaces.

Actual Torch CPU tensor backing, generation reuse and the full owner/bridge/
retention/reporting logic. Only device binding is substituted. No CUDA,
corpus, timing claim or model-quality result.
"""
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from audit_owned_token_reuse import cpu_device, frames
from audit_token_reporting import report_registration
from audit_token_cuda_owner import cuda_contract
from audit_shared_token_retention import STORAGE
from audit_reference_construction import limits, validate_residency
from fp_reference import ReferenceCompilerRuntime, token_workspace_archive as archive
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded, ResourceLedger
from fp_reference.shared_reference import _SharedReference
from fp_reference.ingress import encode_context
from fp_reference.encoding import pack
from fp_reference.profile import ProfileSpec


def reject(call, errors=(ContractError, RuntimeError)):
    try:
        call()
    except errors:
        return
    raise AssertionError('invalid workspace continuation admitted')


def setup(enabled, *, unit=2, count=4, profile=False, combined=False):
    cc, program, online, reporting = report_registration(unit, count, 2)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    if profile:
        online = replace(online, profiles=(ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2),))
    cfg = replace(cuda_contract(cc.initializer_pattern), reuse_regions=True, archive_workspaces=enabled,
                  grouped_reads=combined, composed_native=combined)
    storage = replace(STORAGE, canonical_image_bytes=64 << 10 if combined else 0,
                      token_invariant_bytes=1 << 20 if combined else 0)
    return ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
        cuda=cfg, shared_storage=storage), program


def event(rt, i, target):
    result = rt.predict_next(f'train/{i}', encode_context(()))
    assert result.status == 'PREDICTED_REFERENCE', result.reason
    result = rt.observe(target)
    assert result.status == 'OBSERVED_REFERENCE', result.reason


def numerical_phase(phase):
    plan = dict(phase.execution_plan)
    plan.pop('archived_workspaces', None)
    return pack(replace(phase, execution_plan=plan))


def trajectory(word, enabled, *, unit=2, profile=False, combined=False):
    from fp_reference.token_arrays import CudaArrays
    with cpu_device():
        rt, program = setup(enabled, unit=unit, count=len(word), profile=profile, combined=combined)
        saved, raw_calls, raw_bytes = [], [0], [0]
        original_raw = CudaArrays.raw
        def raw(self, value):
            raw_calls[0] += 1
            raw_bytes[0] += value.numel()*value.element_size()
            return original_raw(self, value)
        with patch.object(CudaArrays, 'raw', raw):
            for i, target in enumerate(word):
                if profile and i == 4:
                    assert rt.construct_candidate(program, profile_id='reverse-repeat').status == 'BUILT_REFERENCE'
                event(rt, i, target)
                if enabled:
                    assert not rt._cuda.predicted  # Only unconsumed forecasts are roots.
                snapshot = validate_residency(rt)
                assert snapshot.cuda.archived_workspaces == (() if not enabled else
                    tuple((key, archive.images(value, owner=rt._cuda)) for key, value in rt._cuda._values.items()))
                saved.append((snapshot, tuple(pack(p) for p in snapshot.cuda.phases)))
            assert rt.begin_report().status == 'REPORTING'
            for i, target in enumerate((0, 1)):
                assert rt.predict_report(f'report/{i}').status == 'PREDICTED_REPORT'
                assert rt.observe_report(target).status in ('SCORED_REPORT', 'COMPLETE_REPORT')
        snapshot = validate_residency(rt)
        retained = frames(snapshot, True)
        for old, bodies in saved:
            assert tuple(pack(p) for p in old.cuda.phases) == bodies
        arena = rt._cuda.arena
        assert not arena._pins
        return dict(phases=tuple(numerical_phase(p) for p in snapshot.cuda.phases),
            learners=tuple(c.learner for c in snapshot.candidates),
            reports=(snapshot.token_report.native_total, snapshot.token_report.physical_total),
            primitive_words=sum(p.forward_operations for p in snapshot.cuda.phases),
            raw_calls=raw_calls[0], raw_bytes=raw_bytes[0], frame_bytes=retained,
            peak=arena._peak_live_bytes, cumulative=arena._allocated_bytes,
            retired=sum(len(row[1]) for row in arena._retirements))


def histories():
    pairs = phases = words = bytes_compared = 0
    counts = [dict(raw_calls=0, raw_bytes=0, frame_bytes=0, retired=0) for _ in range(2)]
    peak_examples = []
    cases = [(word, 2, False, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0)*2, 4, False, False), ((0, 1, 1, 0), 1, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False), ((0, 1, 1, 0)*2, 8, False, False),
              ((0, 1, 1, 0)*2, 4, False, True)]
    for word, unit, profile, combined in cases:
        left, right = (trajectory(word, enabled, unit=unit, profile=profile, combined=combined) for enabled in (False, True))
        for key in ('phases', 'learners', 'reports', 'primitive_words', 'cumulative'):
            assert left[key] == right[key], key
        for i, row in enumerate((left, right)):
            for key in counts[i]:
                counts[i][key] += row[key]
        if unit in (4, 8):
            peak_examples.append(dict(unit=unit, combined=combined, original=left['peak'], archived=right['peak']))
        pairs += 1
        phases += len(right['phases'])
        words += right['primitive_words']
        bytes_compared += sum(map(len, right['phases']))
    return dict(pairs=pairs, matching_numerical_phase_bodies=phases, matching_phase_bytes=bytes_compared,
        matching_primitive_words=words, identical_learners_reports_and_cumulative_allocations=True,
        original_counts=counts[0], archived_counts=counts[1], live_peak_examples=peak_examples,
        count_scope='Raw counters exclude initialization and grouped transfers; no timing or total transport claim.')


def stale_and_live():
    with cpu_device():
        rt, _ = setup(True, unit=4, count=4)
        observed, original = [], archive.prepare
        def capture(*args):
            resident = args[3]
            observed.append(resident.state.leaves[-1].values)
            return original(*args)
        with patch.object(archive, 'prepare', capture):
            event(rt, 0, 0)
        old = observed[0]
        generation = rt._cuda.arena._generations.require(old)
        snapshot = rt.snapshot()
        body = tuple(pack(p) for p in snapshot.cuda.phases)
        original_image = snapshot.cuda.archived_workspaces
        reject(lambda: original_image.__setitem__(0, ()), AttributeError)
        snapshot.cuda.__dict__['archived_workspaces'] = ('forged',)
        assert rt.snapshot().cuda.archived_workspaces == original_image
        # Collection occurs before the next actual prediction. The consumed
        # forecast is absent, so its historical values can really retire.
        assert rt.predict_next('train/1', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert generation not in rt._cuda.arena._generations._live
        reject(lambda: rt._cuda.arena.require_initialized(old))
        assert tuple(pack(p) for p in snapshot.cuda.phases) == body
        assert rt.observe(1).status == 'OBSERVED_REFERENCE'
        for i, y in ((2, 1), (3, 0)):
            event(rt, i, y)
        assert tuple(pack(p) for p in rt.snapshot().cuda.phases[:len(body)]) == body
    with cpu_device():
        rt, _ = setup(True, unit=4, count=4)
        event(rt, 0, 0)
        before = rt.snapshot()
        resident = rt._cuda._values[rt._cuda.current[before.deployed_id]]
        live = resident.state.common.blocks[0].value
        assert bool(live.ne(0).any())
        live.zero_()
        reject(lambda: rt.predict_next('train/1', encode_context(())))
        after = rt.snapshot()
        assert after.cursor == 1 and after.candidates[0].learner == before.candidates[0].learner
        failure = after.cuda.phases[-1]
        assert failure.status == 'EXECUTION_FAILED' and 'changed after its owned phase' in failure.reason
        assert failure.raw_state.common.blocks[0][1].data != before.cuda.phases[-1].raw_state.common.blocks[0][1].data
    with cpu_device():
        rt, _ = setup(True, unit=4, count=4)
        event(rt, 0, 0)
        before = rt.snapshot()
        live_before = set(rt._cuda.arena._generations._live)
        with patch.object(rt._cuda.arena, '_release', side_effect=MemoryError('during actual generation retirement')):
            reject(lambda: rt.predict_next('train/1', encode_context(())), MemoryError)
        after = rt.snapshot()
        assert after.halted is not None and after.cursor == 1
        assert after.candidates[0].learner == before.candidates[0].learner
        assert rt._cuda.arena._failure is not None
        assert set(rt._cuda.arena._generations._live) < live_before
        reject(lambda: rt.predict_next('train/1', encode_context(())))
    return dict(actual_historical_generation_retired=True, stale_view_refuses=True,
        public_image_replacement_has_no_authority=True, old_sealed_records_unchanged=True,
        actual_changed_live_carry_refuses=True, partial_retirement_memory_failure_is_terminal=True,
        old_learner_preserved=True)


def failures():
    cases = ('unpaid', 'image', 'geometry', 'owner', 'live-root', 'prepare-memory', 'retention', 'retention-memory')
    for case in cases:
        with cpu_device():
            rt, _ = setup(True, unit=4, count=4)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            before = rt.snapshot()
            sealed = set(rt._cuda.arena._sealed)
            original = archive.prepare
            if case == 'unpaid':
                charge = ResourceLedger.charge_work
                def deny(self, role, cost, **kwargs):
                    if ':cuda:ordinary:observe:' in kwargs.get('note', ''):
                        raise ResourceExceeded('unpaid archive phase')
                    return charge(self, role, cost, **kwargs)
                hook = patch.object(ResourceLedger, 'charge_work', deny)
            elif case in ('retention', 'retention-memory'):
                def fail(*args, **kwargs):
                    raise (MemoryError if case.endswith('memory') else ResourceExceeded)('after workspace proposal')
                hook = patch.object(_SharedReference, 'seal_cuda_frame', fail)
            else:
                def forged(*args):
                    value = original(*args)
                    if case == 'prepare-memory':
                        raise MemoryError('after private workspace proposal')
                    if case == 'live-root':
                        return replace(value, state=replace(value.state, core=replace(value.state.core)))
                    field = value.state.leaves[0].values
                    version, source, geometry, words = field._value
                    if case == 'image':
                        shape, dtype, data = words
                        words = (shape, dtype, bytes([data[0] ^ 1])+data[1:])
                    elif case == 'geometry':
                        geometry = (geometry[0]+1, *geometry[1:])
                    elif case == 'owner':
                        import weakref
                        field._owner = weakref.ref(rt)
                    field._value = (version, source, geometry, words)
                    return value
                hook = patch.object(archive, 'prepare', forged)
            with hook:
                try:
                    result = rt.observe(0)
                    assert result.status == 'UNRESOLVED'
                except (RuntimeError, MemoryError):
                    pass
            after = rt.snapshot()
            assert after.cursor == 0 and after.observations[-1].target == 0 and after.halted is not None
            assert after.candidates[0].learner == before.candidates[0].learner
            assert set(rt._cuda.arena._sealed) == sealed
            assert after.cuda.current == before.cuda.current and after.cuda.predicted == before.cuda.predicted
            if case == 'unpaid':
                assert len(after.cuda.phases) == len(before.cuda.phases)
            else:
                assert rt._cuda.arena._pins
            if case in ('image', 'geometry', 'owner', 'live-root'):
                failed = after.cuda.phases[-1]
                assert failed.status == 'EXECUTION_FAILED'
                assert failed.execution_plan['failed_workspace_archive_proposal']
                reject(lambda: rt._cuda.accept(failed))
    return list(cases)


def registration_controls():
    cc, program, online, _ = report_registration()
    cfg = cuda_contract(cc.initializer_pattern)
    reject(lambda: replace(cfg, archive_workspaces=True))
    reject(lambda: replace(cfg, reuse_regions=True, archive_workspaces=1))
    cfg = replace(cfg, reuse_regions=True, archive_workspaces=True)
    with cpu_device():
        reject(lambda: ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg))
    return dict(generation_reuse_required=True, exact_boolean_required=True,
                shared_retention_in_both_roles_required=True)


def audit():
    result = histories()
    print('PASS complete paired Runtime histories', flush=True)
    boundaries, failed, registration = stale_and_live(), failures(), registration_controls()
    import torch
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_OWNED_TOKEN_WORKSPACE_ARCHIVES_CPU', histories=result,
                boundaries=boundaries, failures=failed, registration=registration, scope=__doc__.strip())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('owned workspace audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_TOKEN_WORKSPACES_CPU.json').write_text(body, encoding='utf-8')
    print(body)
