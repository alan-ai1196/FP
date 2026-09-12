"""Actual bounded CUDA tensor storage, including complete learner execution.

The native allocation counter detects transient escaped allocations even
after their tensors are freed. This is a tensor-allocator audit, not a claim
about driver/context allocations or complete Runtime/AMP installation.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import cuda_learner as gpu
from fp_reference.cuda_storage import CudaArena, CudaStorageContract, CudaStorageUnresolved, initial_reservation_bytes
from fp_reference.core import ContractError
from fp_reference.learner import LearnerSpec
from fp_reference.semantics import ArithmeticUnresolved
from audit_cuda_primitives import SINGLE
from audit_cuda_learner import exhaustive_audit, profile_recurrence_audit, topology_audit
from audit_reference_construction import rejects


ARENA_BYTES = 16*1024*1024


def registration_audit(torch):
    for size in (True, 0, -512, 513, 1 << 63):
        rejects(lambda size=size: CudaStorageContract(size, 2*ARENA_BYTES,
                {r: (ARENA_BYTES, 2*ARENA_BYTES) for r in ('deployment', 'compiler')}))
    cfg = CudaStorageContract(ARENA_BYTES, 2*ARENA_BYTES,
                {'deployment': (ARENA_BYTES, 2*ARENA_BYTES), 'compiler': (ARENA_BYTES//2, 2*ARENA_BYTES)})
    before = torch.cuda.memory_allocated()
    rejects(lambda: CudaArena(cfg), CudaStorageUnresolved)
    assert torch.cuda.memory_allocated() == before == 0
    # A 2 MiB request needs a fresh default 20 MiB segment. Refuse its
    # insufficient reservation cap before creating any actual device tensor.
    cfg = CudaStorageContract(2 << 20, 4 << 20,
                             {r: (2 << 20, 4 << 20) for r in ('deployment', 'compiler')})
    before_events = torch.cuda.memory_stats().get('allocation.all.allocated', 0)
    rejects(lambda: CudaArena(cfg), CudaStorageUnresolved)
    assert torch.cuda.memory_allocated() == torch.cuda.memory_reserved() == 0
    assert torch.cuda.memory_stats().get('allocation.all.allocated', 0) == before_events == 0
    return {'malformed_caps_rejected': True, 'shared_arena_role_refusal_precedes_device_allocation': True,
            'insufficient_real_allocator_segment_cap_refused_before_allocation': True,
            'allocation_counter_after_all_registration_refusals': before_events}


def bootstrap_probe(case):
    """Run in a separate new process, never reset an existing allocator."""
    import torch
    if case in ('hidden-setting-witness', 'hidden-setting-binding'):
        before = torch.cuda.memory._snapshot()['allocator_settings']
        torch._C._accelerator_setAllocatorSettings('large_segment_size_mb:40')
        torch._C._accelerator_setAllocatorSettings('')
        assert torch.cuda.memory._snapshot()['allocator_settings'] == before
        assert torch.cuda.memory_stats().get('allocation.all.allocated', 0) == 0
        if case == 'hidden-setting-witness':
            value = torch.empty(2 << 20, dtype=torch.uint8, device='cuda')
            assert value.numel() == torch.cuda.memory_allocated() == 2 << 20
            assert torch.cuda.memory_reserved() == 40 << 20
            return {'same_reported_settings_as_initial_default': True,
                    'before_allocation_counter': 0, 'request_bytes': 2 << 20,
                    'actual_allocator_reserved_bytes': torch.cuda.memory_reserved()}
    size = {'small': 512, 'medium': 2 << 20, 'large': 10 << 20,
            'hidden-setting-binding': 2 << 20}[case]
    reserve = initial_reservation_bytes(size)
    arena = CudaArena(CudaStorageContract(size, reserve,
                     {r: (size, reserve) for r in ('deployment', 'compiler')}))
    observed = arena.snapshot()
    assert observed['actual_tensor_arena_bytes'] == size
    assert observed['actual_allocator_reserved_bytes'] == reserve
    return {'request_bytes': size, 'pre_admitted_segment_bytes': reserve,
            'actual_allocator_reserved_bytes': observed['actual_allocator_reserved_bytes'],
            'explicit_allocator_configuration': observed['allocator_configuration'],
            'native_counter': list(observed['native_allocation_counter_current'])}


def extent_audit(arena, torch):
    samples = [(torch.float16, 0), (torch.float16, 1), (torch.float32, 3),
               (torch.bool, 5), (torch.int32, 2), (torch.float32, 0)]
    requests = 0
    predicted_cursor = arena.snapshot()['consumed_arena_extent']
    # Every length-three request sequence over this finite typed alphabet.
    # The independent model derives offsets and padding without reading the
    # allocator's region descriptors, then checks actual tensor storage.
    for sequence in product(samples, repeat=3):
        with arena.phase('extent-model') as workspace:
            predicted_cursor += 8
            for dtype, count in sequence:
                value = workspace.empty((count,), dtype, 'model-output')
                width = {torch.float16: 2, torch.float32: 4, torch.int32: 4, torch.bool: 1}[dtype]
                assert value.storage_offset()*width == predicted_cursor
                assert value.untyped_storage().data_ptr() == arena._storage.untyped_storage().data_ptr()
                assert value.numel()*value.element_size() == count*width
                assert tuple(value.shape) == (count,)
                predicted_cursor += max(8, ((count*width+7)//8)*8)
                value.fill_(1)
                workspace.written(value)
                workspace.require_initialized(value)
                requests += 1
        assert arena._cursor == predicted_cursor

    with arena.phase('extent-guards') as workspace:
        arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
        raw = workspace.empty((3,), torch.float32, 'uninitialized')
        rejects(lambda: arithmetic.mul(raw, raw))
        raw.fill_(1)
        workspace.written(raw)
        rejects(lambda: workspace.written(raw))
        workspace.require_initialized(raw[1:2])
        offset = raw.storage_offset()*4
        crossing = arena._storage.narrow(0, offset, 16).view(torch.float32)
        rejects(lambda: arithmetic.mul(crossing, crossing))
        rejects(lambda: arithmetic.mul(raw.view(torch.float16), raw.view(torch.float16)))
        negative_view = torch.ops.aten._neg_view.default(raw)
        rejects(lambda: arithmetic.mul(negative_view, negative_view))
        uninitialized = workspace.empty((1,), torch.float16, 'unread-unused')
        old_cursor, old_regions = arena._cursor, len(arena._regions)
        rejects(lambda: workspace.empty((ARENA_BYTES,), torch.float32, 'too-large'), CudaStorageUnresolved)
        assert arena._cursor == old_cursor and len(arena._regions) == old_regions
    with arena.phase('stale-guards') as later:
        rejects(lambda: later.written(raw))
        rejects(lambda: later.written(uninitialized))
        rejects(lambda: later.require_initialized(uninitialized))
        later.require_initialized(raw)
    rejects(lambda: workspace.empty((1,), torch.float32, 'closed-workspace'))
    snapshot = arena.snapshot()
    assert snapshot['role_tensor_arena_bytes'] == {r: ARENA_BYTES for r in ('deployment', 'compiler')}
    return {'complete_typed_allocation_request_sequences': 216, 'actual_extent_requests': requests,
            'real_offsets_and_storage_identity_match_independent_model': True,
            'uninitialized_cross_extent_reinterpreted_and_lazy_negative_reads_rejected': True,
            'old_or_already_initialized_extent_cannot_be_redeclared_written': True,
            'failed_large_extent_does_not_allocate_or_advance_cursor': True,
            'whole_actual_backing_arena_charged_to_each_role_once_globally': True}


def grid_and_failure_audit(arena, torch):
    rng = random.Random(2026091372)
    words = [0, 1, 2, 0x007fffff, 0x00800000, 0x7f7fffff,
             *[rng.randrange(0x7f800000) for _ in range(128)]]
    with arena.phase('grid-input') as workspace:
        arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
        values = arithmetic.ingress(tuple(SINGLE.decode(word) for word in words))
        arithmetic.check()
    before = gpu.raw_tensor(values)
    compared = 0
    for bits in (0, 1, 8, 16, 23, 24, 126, 149, 150, 4095):
        with arena.phase('grid-execution') as workspace:
            arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
            actual = arithmetic.floor_grid(values, bits)
            arithmetic.check()
            expected = []
            for word in words:
                scaled = SINGLE.decode(word)*(1 << bits)
                expected.append(SINGLE.encode_exact(F(scaled.numerator//scaled.denominator, 1 << bits)))
            assert gpu.raw_tensor(actual) == tuple(expected)
            compared += len(words)
        assert gpu.raw_tensor(values) == before

    with arena.phase('overflow-input') as workspace:
        arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
        zero = arithmetic.ingress((F(0),))
        maximum = arithmetic.ingress((SINGLE.decode(0x7f7fffff),))
        arithmetic.check()
    pending = gpu.CudaLearnerState(zero, (), maximum, 1, 1, 0)
    before = gpu.raw_state(pending)
    try:
        with arena.phase('masked-overflow') as workspace:
            arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
            gpu.commit_event(pending, LearnerSpec(1, F(2)), arithmetic)
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('a finite projected endpoint hid an actual arena optimizer overflow')
    trace = arithmetic.raw_trace()
    assert any(op == 'mul' and result == (0x7f800000,) for op, _, result in trace)
    assert any(op == 'positive-part' and result == (0,) for op, _, result in trace)
    assert gpu.raw_state(pending) == before and arena.snapshot()['phases'][-1][-1] == 'FAILED'
    return {'exact_grid_coordinates_inside_owned_arena': compared,
            'complete_predecessor_preserved_after_actual_masked_overflow': True,
            'failed_phase_extents_and_infinite_intermediate_retained': True}


def escaped_allocation_audit(arena, torch):
    before = arena.snapshot()
    original = 'original unexpected CUDA executor failure'
    try:
        with arena.phase('escaped-allocation-and-backend-failure') as workspace:
            arithmetic = gpu.CudaArithmetic(4096, workspace=workspace)
            retained = arithmetic.ingress((F(1),))
            foreign = torch.empty(1, dtype=torch.float32, device='cuda')
            del foreign
            assert torch.cuda.memory_allocated() == ARENA_BYTES
            raise RuntimeError(original)
    except RuntimeError as error:
        assert str(error) == original
        assert isinstance(error.__cause__, CudaStorageUnresolved)
        assert any('allocation escaped' in note for note in error.__notes__)
    else:
        raise AssertionError('escaped allocation or earlier backend failure was accepted')
    after = arena.snapshot()
    assert after['status'] == 'UNRESOLVED' and after['phases'][-1][-1] == 'FAILED'
    assert after['actual_tensor_arena_bytes'] == before['actual_tensor_arena_bytes'] == ARENA_BYTES
    assert after['native_allocation_counter_current'] != before['native_allocation_counter_current']
    assert gpu.raw_tensor(retained) == (0x3f800000,)
    cursor, phases = after['consumed_arena_extent'], len(after['phases'])
    rejects(lambda: arena.phase('cannot-resume'), CudaStorageUnresolved)
    assert arena.snapshot()['consumed_arena_extent'] == cursor and len(arena.snapshot()['phases']) == phases
    return {'freed_foreign_tensor_restores_current_bytes_but_does_not_erase_allocation_history': True,
            'native_counter_before': list(before['native_allocation_counter_current']),
            'native_counter_after_freed_foreign_allocation': list(after['native_allocation_counter_current']),
            'actual_current_bytes_after_foreign_tensor_free': after['actual_tensor_arena_bytes'],
            'original_unexpected_failure_not_downgraded_by_storage_refusal': True,
            'actual_completed_write_retained_with_failed_phase': True,
            'storage_failure_is_terminal_without_counter_reset_or_identity_reuse': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--bootstrap', choices=('small', 'medium', 'large',
                        'hidden-setting-witness', 'hidden-setting-binding'))
    args = parser.parse_args()
    if args.bootstrap:
        if args.write:
            parser.error('a bootstrap subcase cannot replace canonical evidence')
        print(json.dumps(bootstrap_probe(args.bootstrap)))
        return
    import torch
    result = {'status': 'PASS', 'scope': 'actual bounded CUDA tensor arena and complete learner mechanics; no Runtime or total-device authority',
              'registration': registration_audit(torch)}
    result['actual_initial_reservation_classes'] = {}
    for case in ('small', 'medium', 'large', 'hidden-setting-witness', 'hidden-setting-binding'):
        child = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--bootstrap', case],
                               capture_output=True, text=True, check=True, timeout=60)
        result['actual_initial_reservation_classes'][case] = json.loads(child.stdout)
    cfg = CudaStorageContract(ARENA_BYTES, 2*ARENA_BYTES,
                             {role: (ARENA_BYTES, 2*ARENA_BYTES) for role in ('deployment', 'compiler')})
    arena = CudaArena(cfg)
    for name, audit in (('exhaustive_learners', exhaustive_audit), ('recurrent_profile', profile_recurrence_audit),
                        ('varied_native_graphs', topology_audit)):
        result[name] = audit(arena=arena)
        print(name+' PASS', flush=True)
    learner_snapshot = arena.snapshot()
    result['learner_storage'] = {key: learner_snapshot[key] for key in (
        'allocation_id', 'device_name', 'capability', 'torch', 'torch_git_version', 'CUDA_runtime',
        'actual_tensor_arena_bytes', 'actual_allocator_reserved_bytes', 'lifetime_tensor_peak_bytes',
        'lifetime_allocator_reserved_peak_bytes', 'native_allocation_counter_at_binding',
        'native_allocation_counter_current', 'consumed_arena_extent')}
    result['learner_storage']['actual_initialized_view_extents'] = len(learner_snapshot['regions'])
    assert all(row[-1] for row in learner_snapshot['regions'])
    assert len(learner_snapshot['phases']) == 1306
    result['extents'] = extent_audit(arena, torch)
    result['grid_and_failure'] = grid_and_failure_audit(arena, torch)
    result['escaped_allocation'] = escaped_allocation_audit(arena, torch)
    result['not_closed'] = ['Runtime device registration, paid host evidence and joint event publication',
        'driver/context/non-PyTorch allocations or total-device accounting',
        'target range, same-path AMP persistence, build/copy/install and science release',
        'liveness-optimal storage or a GPU performance claim']
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_STORAGE_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
