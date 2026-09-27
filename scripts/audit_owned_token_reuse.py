"""Actual token owner/array logic on a reused CPU tensor backing buffer.

Only physical device binding/counters are substituted. No CUDA context,
corpus, device certificate or measured training-throughput claim.
"""
from contextlib import contextmanager
from dataclasses import replace
from itertools import product
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import json
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime, runtime
from fp_reference.core import ContractError, freeze_data
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.cuda_storage import CudaArena, CudaStorageContract
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.profile import ProfileSpec
from fp_reference.resources import ResourceExceeded
from fp_reference.shared_reference import decoded_buffer
from fp_reference.token_arrays import CudaArrays
from fp_reference import token_reuse
from fp_reference.token_reuse import TokenReuseArena
from audit_reference_construction import limits
from audit_shared_token_retention import STORAGE
from audit_token_reporting import report_registration, train
from audit_token_cuda_owner import cuda_contract


def reject(call, kind=ContractError):
    try:
        call()
    except kind:
        return
    raise AssertionError('invalid reuse continuation was admitted')


def cpu_arena(contract, reuse):
    arena = object.__new__(TokenReuseArena if reuse else CudaArena)
    arena.contract, arena.device = contract, torch.device('cpu')
    arena._storage = torch.empty(contract.arena_bytes, dtype=torch.uint8)
    arena._pointer = arena._storage.untyped_storage().data_ptr()
    arena._failure, arena._active, arena._cursor = None, None, 0
    arena._regions, arena._starts, arena._phases = [], [], []
    arena._require_stream = lambda: None
    def check():
        if arena._failure is not None:
            raise ResourceExceeded(arena._failure)
    arena.check = check
    if reuse:
        arena._init_reuse()
    def snapshot():
        rows = tuple((r.sequence, r.phase, r.owner, r.operation, r.offset, r.byte_size,
                      r.reserved_size, r.shape, r.dtype, r.initialized) for r in arena._regions)
        return freeze_data(dict(scope='CPU tensor storage substitution; no device authority',
            regions=rows, phases=tuple(arena._phases), consumed_arena_extent=arena._cursor,
            **(arena.reuse_snapshot() if reuse else {})))
    arena.snapshot = snapshot
    return arena


@contextmanager
def cpu_device():
    def prefix(contract):
        value = object.__new__(_CudaPrefix)
        value.contract, value.arena = contract, cpu_arena(contract.storage, contract.reuse_regions)
        value._device = SimpleNamespace(check=lambda: None, snapshot=lambda: None)
        value.current, value.staged, value.predicted, value.phases, value._values = {}, {}, {}, {}, {}
        value._native_bounds = {}
        return value
    with patch.object(runtime, '_CudaPrefix', prefix), patch.object(runtime.secrets, 'token_hex', return_value='cpu-reuse-control'):
        yield


def setup(*, reuse, shared=False, unit=2, count=4, report_count=2, profile=False, arena_bytes=1 << 20):
    cc, program, online, reporting = report_registration(unit, count, report_count)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    if profile:
        online = replace(online, profiles=(ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2),))
    cfg = replace(cuda_contract(cc.initializer_pattern), reuse_regions=reuse,
        storage=CudaStorageContract(arena_bytes, 32 << 20,
            {role: (arena_bytes, 32 << 20) for role in ('deployment', 'compiler')}))
    rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting, cuda=cfg,
        shared_storage=STORAGE if shared else None)
    return rt, program


def frames(snapshot, shared):
    checked = 0
    for phase in snapshot.cuda.phases:
        raw = (b''.join(decoded_buffer(snapshot, phase.object_id, byte_cap=STORAGE.expanded_cap,
            reference_cap=STORAGE.reference_cap)) if shared else dict(snapshot.buffers)[phase.object_id])
        count = int.from_bytes(raw[:8], 'big')
        assert raw[8:8+count] == pack(phase) and not any(raw[8+count:])
        checked += count
    return checked


def trajectory(targets, *, reuse, shared, unit=2, profile=False, arena_bytes=1 << 20):
    with cpu_device():
        rt, program = setup(reuse=reuse, shared=shared, unit=unit, count=len(targets),
                            profile=profile, arena_bytes=arena_bytes)
        history = []
        for i, target in enumerate(targets):
            if profile and i == 4:
                result = rt.construct_candidate(program, profile_id='reverse-repeat')
                assert result.status == 'BUILT_REFERENCE', result.reason
            result = rt.predict_next(f'train/{i}', encode_context(()))
            assert result.status == 'PREDICTED_REFERENCE', result.reason
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE', result.reason
            snapshot = rt.snapshot()
            history.append((snapshot, tuple(pack(row) for row in snapshot.cuda.phases)))
        assert rt.begin_report().status == 'REPORTING'
        for i, target in enumerate((0, 1)):
            result = rt.predict_report(f'report/{i}')
            assert result.status == 'PREDICTED_REPORT', result.reason
            # Exercise the repaired public boundary through the reused lowering.
            prediction = rt._cuda.phases[rt.snapshot().token_report.pending.cuda_prediction]
            reject(lambda: prediction.relation.__setitem__('stored_sum_lower', (0,)), AttributeError)
            result = rt.observe_report(target)
            assert result.status in ('SCORED_REPORT', 'COMPLETE_REPORT'), (result.status, result.reason)
        final = rt.snapshot()
        checked_bytes = frames(final, shared)
        for old, expected in history:
            assert tuple(pack(row) for row in old.cuda.phases) == expected
            assert tuple(pack(row) for row in final.cuda.phases[:len(expected)]) == expected
        arena = rt._cuda.arena
        if reuse:
            assert len(arena._header_history) == len(arena._phases)
            assert tuple(i for i, _, _ in arena._header_history) == tuple(range(len(arena._phases)))
            assert arena._allocated_bytes > arena._peak_live_bytes
            assert sum(len(row[1]) for row in arena._retirements) > 0
            assert not arena._pins
            assert len(rt._cuda._values) < len(rt._cuda.phases)
            # A historical success cannot be reaccepted even if some tensors
            # it once named are still shared by a current resident.
            reject(lambda: rt._cuda.accept(final.cuda.phases[0]))
        return dict(phase_bytes=tuple(pack(row) for row in final.cuda.phases),
            report=(final.token_report.native_total, final.token_report.physical_total),
            retained_bytes=checked_bytes, phases=len(final.cuda.phases),
            peak=arena._peak_live_bytes if reuse else arena._cursor,
            cumulative=arena._allocated_bytes if reuse else arena._cursor,
            retired=sum(len(row[1]) for row in arena._retirements) if reuse else 0,
            profile_events=len(final.profile_events))


def histories():
    count = phases = retained = retired = profiles = 0
    peak = cumulative = 0
    cases = [(word, 2, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0, 1, 0, 0, 1), 4, False), ((0, 1, 1, 0, 0, 1), 2, True)]
    for shared in (False, True):
        for targets, unit, profile in cases:
            normal = trajectory(targets, reuse=False, shared=shared, unit=unit, profile=profile)
            reused = trajectory(targets, reuse=True, shared=shared, unit=unit, profile=profile)
            assert normal['phase_bytes'] == reused['phase_bytes']
            assert normal['report'] == reused['report']
            count += 1
            phases += reused['phases']
            retained += reused['retained_bytes']
            retired += reused['retired']
            peak = max(peak, reused['peak'])
            cumulative = max(cumulative, reused['cumulative'])
            profiles += reused['profile_events']
    return dict(paired_histories=count, identical_complete_phases=phases,
        identical_retained_body_bytes=retained, actual_retired_generations=retired,
        largest_reuse_peak_bytes=peak, largest_cumulative_buddy_bytes=cumulative,
        profile_events=profiles, exact_physical_and_native_reports=True)


def actual_overwrite():
    cfg = CudaStorageContract(512, 2 << 20, {r: (512, 2 << 20) for r in ('deployment', 'compiler')})
    arena = cpu_arena(cfg, True)
    with arena.phase('first') as ws:
        old = ws.empty((4,), torch.float32, 'old')
        old.fill_(1)
        ws.written(old)
        alias = arena.derive(old, old.reshape(2, 2))
    first = SimpleNamespace(arena_phase=0, object_id='first', status='CHECKED_CUDA_PREFIX_PHASE')
    # No owner seal: even empty roots retain every allocation and the header.
    arena.collect(())
    assert arena._generations.require(old) in arena._pins
    reject(lambda: arena.accept(first))
    arena.seal(first)
    arena.accept(first)
    arena.collect(())
    assert arena._header_history == [(0, 0, 8)] and not arena._headers
    with arena.phase('second') as newer:
        value = newer.empty((4,), torch.float32, 'new')
        assert value.data_ptr() == old.data_ptr()
        value.fill_(7)
        newer.written(value)
        assert tuple(old.tolist()) == (7, 7, 7, 7)
        reject(lambda: arena.require_initialized(old))
        reject(lambda: newer.raw_bytes((alias,), bytearray(32)))
        reject(lambda: newer.written(old))
        reject(lambda: arena.derive(value, old))
        # Address-correct but unissued views have no authority either.
        reject(lambda: arena.require_initialized(value.view(4)))
        reject(lambda: arena.derive(value, value.view(torch.float16)))
        array = CudaArrays(newer, bytearray(32), element_cap=16, cell_cap=16)
        reject(lambda: array.add(value, old))
    reject(lambda: arena.accept(first))
    return dict(old_words_actually_overwritten=True, refused_operations=9,
                unsealed_region_and_header_pinned=True)


def bounded_training():
    targets = (0, 1, 1, 0)*4
    ordinary = trajectory(targets, reuse=False, shared=True)
    reused = trajectory(targets, reuse=True, shared=True, arena_bytes=8192)
    assert ordinary['phase_bytes'] == reused['phase_bytes']
    assert ordinary['report'] == reused['report']
    assert ordinary['cumulative'] > 8192 >= reused['peak']
    return dict(ordinary_events=len(targets), committed_units=len(targets)//2, report_events=2,
        complete_phases=reused['phases'], backing_bytes=8192,
        append_only_consumed_bytes=ordinary['cumulative'], reused_peak_bytes=reused['peak'],
        reused_cumulative_buddy_bytes=reused['cumulative'], identical_phase_and_score_values=True)


def partition(arena, allocations):
    spans = [(offset, offset+size) for offset, size in allocations]
    spans += [(offset, offset+(1 << order)) for order, entries in arena._free.items() for offset in entries]
    spans.sort()
    assert spans[0][0] == 0 and spans[-1][1] == arena.contract.arena_bytes
    assert all(left[1] == right[0] for left, right in zip(spans, spans[1:]))
    assert sum(size for _, size in allocations) == arena._live_bytes


def small_allocator():
    cfg = CudaStorageContract(512, 2 << 20, {r: (512, 2 << 20) for r in ('deployment', 'compiler')})
    actions = (8, 24, 80, 256, 'oldest')
    histories = steps = refusals = 0
    for word in product(actions, repeat=5):
        arena, active = cpu_arena(cfg, True), []
        for action in word:
            if action == 'oldest':
                if active:
                    arena._release(*active.pop(0))
            else:
                before = (tuple(active), {k: set(v) for k, v in arena._free.items()}, arena._live_bytes)
                try:
                    active.append(arena._reserve(action))
                except ResourceExceeded:
                    assert before == (tuple(active), arena._free, arena._live_bytes)
                    refusals += 1
            partition(arena, active)
            steps += 1
        histories += 1
    return dict(histories=histories, partition_checks=steps, unchanged_allocation_refusals=refusals)


def failures():
    checked = []
    for mode in ('unpaid-collection', 'unsealed-frame', 'partial-allocation', 'retirement-memory'):
        with cpu_device():
            rt, _ = setup(reuse=True)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            before = rt.snapshot()
            arena = rt._cuda.arena
            old_learner = before.candidates[0].learner
            if mode == 'unpaid-collection':
                original = rt._ledger.charge_work
                def denied(role, debit, **kwargs):
                    if ':cuda:ordinary:observe:' in kwargs.get('note', ''):
                        raise ResourceExceeded('no prepaid collection work')
                    return original(role, debit, **kwargs)
                hook = patch.object(rt._ledger, 'charge_work', denied)
                point = arena.reuse_snapshot()
            elif mode == 'unsealed-frame':
                hook = patch.object(rt, '_seal_cuda_frame', side_effect=ResourceExceeded('frame retention refused'))
            elif mode == 'partial-allocation':
                original, calls = arena._reserve, [0]
                def denied(size):
                    calls[0] += 1
                    if calls[0] == 5:
                        raise ResourceExceeded('new phase allocation refused')
                    return original(size)
                hook = patch.object(arena, '_reserve', denied)
            else:
                hook = patch.object(arena, '_release', side_effect=MemoryError('retirement metadata failure'))
            with hook:
                if mode == 'retirement-memory':
                    reject(lambda: rt.observe(1), MemoryError)
                else:
                    result = rt.observe(1)
                    assert result.status == 'UNRESOLVED', (mode, result)
            after = rt.snapshot()
            assert after.candidates[0].learner == old_learner
            assert after.observations[-1].target == 1
            if mode == 'unpaid-collection':
                assert arena.reuse_snapshot() == point
            elif mode in ('unsealed-frame', 'partial-allocation'):
                phase = after.cuda.phases[-1].arena_phase
                pinned = {g for g in arena._generations._live if arena._regions[arena._generation_regions[g]].phase == phase}
                assert pinned and phase not in arena._sealed and pinned <= set(arena._pins)
                token_reuse.collect(rt._cuda)  # diagnostic continuation of the pin rule only
                assert pinned <= arena._generations._live and phase in arena._headers
            else:
                assert after.halted and arena._failure is not None
                reject(arena.check, ResourceExceeded)
            checked.append(mode)
    return dict(post_target_boundaries=checked, old_learners_and_targets_retained=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_TOKEN_REUSE_CPU', scope=__doc__.strip())
    for name, test in (('overwrite', actual_overwrite), ('allocator', small_allocator),
                       ('failures', failures), ('histories', histories), ('bounded_training', bounded_training)):
        result[name] = test()
        print(name+': PASS', flush=True)
    assert not torch.cuda.is_initialized()
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_TOKEN_REUSE_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
