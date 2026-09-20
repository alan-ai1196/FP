"""Exact word/ownership audit of prepaid bulk CUDA observation.

The bounded helper fixture has no Runtime authority. Complete Runtime and
installation regressions exercise the actual prepaid execution integration.
"""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import random
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import cuda_learner as gpu
from fp_reference.core import ContractError
from fp_reference.cuda_storage import CudaArena, CudaStorageContract, CudaStorageUnresolved
from fp_reference.semantics import ArithmeticUnresolved
from audit_reference_construction import rejects

OUTPUT = ROOT/'evidence/minimal/FP_CUDA_READOUT_AUDIT.json'
CAP, TIMEOUT, ARENA = 4 << 30, 120000, 16 << 20


def worker():
    import torch
    arena = CudaArena(CudaStorageContract(ARENA, 2*ARENA,
                       {r: (ARENA, 2*ARENA) for r in ('deployment', 'compiler')}))
    halves = tuple(range(1 << 16))
    rng = random.Random(20260914)
    singles = (0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000,
               0x3f800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
               0x7fc00001, 0x7f800001, 0xffcabcde)+tuple(rng.randrange(1 << 32) for _ in range(512))

    def put(workspace, words, width):
        dtype = torch.float16 if width == 16 else torch.float32
        value = workspace.empty((len(words),), dtype, 'exact-raw-word-fixture')
        payload = bytearray().join(w.to_bytes(width//8, 'little') for w in words)
        if words:
            host = torch.frombuffer(payload, dtype=torch.int16 if width == 16 else torch.int32)
            value.view(host.dtype).copy_(host)
        workspace.written(value)
        return value

    with arena.phase('all-half-and-adversarial-single-words') as workspace:
        a = put(workspace, halves, 16)
        scalar = put(workspace, (0x8000,), 16)
        padding_start = scalar.storage_offset()*2+2
        arena._storage[padding_start:padding_start+6].fill_(255)
        b = put(workspace, singles, 32)
        empty = put(workspace, (), 16)
        views = (b, scalar, a, a[3:11], b[7:12], empty, scalar)
        expected = tuple(gpu.raw_tensor(value) for value in views)
        buffer = bytearray(8*(len(halves)+len(singles)+2))
        before = arena._allocation_counter()
        assert workspace.raw_words(views, buffer) == expected
        assert not any(buffer)
        assert expected == (singles, (0x8000,), halves, halves[3:11], singles[7:12], (), (0x8000,))
        buffer[:] = b'\xff'*len(buffer)
        assert workspace.raw_words(views, buffer) == expected
        assert arena._allocation_counter() == before
        rejects(lambda: workspace.raw_words(views, bytearray(1)), CudaStorageUnresolved)
        rejects(lambda: workspace.raw_words(views, bytes(buffer)))
        rejects(lambda: workspace.raw_words(list(views), buffer))
        rejects(lambda: workspace.raw_words((b.view(torch.int32),), buffer))
        rejects(lambda: workspace.raw_words((torch.empty(1),), buffer))
        padding_view = arena._storage[padding_start:padding_start+2].view(torch.float16)
        rejects(lambda: workspace.raw_words((padding_view,), buffer))
        assert workspace.raw_words((empty,), bytearray()) == ((),)
    assert workspace.raw_words(views, buffer) == expected
    old_workspace = workspace

    with arena.phase('new-phase-not-old-observer') as workspace:
        fresh = put(workspace, (0x3f800000,), 32)
        uninitialized = workspace.empty((1,), torch.float32, 'uninitialized-refusal')
        rejects(lambda: workspace.raw_words((uninitialized,), buffer))
        rejects(lambda: workspace.raw_words((scalar,), buffer))
        rejects(lambda: old_workspace.raw_words((fresh,), buffer))
    guards = 9

    try:
        with arena.phase('fresh-reread-detects-mutation') as workspace:
            arithmetic = gpu.CudaArithmetic(32768, workspace=workspace, output_cell_limit=64,
                                             readout_buffer=bytearray(512))
            value = arithmetic.constant(F(1))
            arithmetic.check()
            first = arithmetic.raw_trace()
            value.fill_(float('inf'))
            arithmetic.check()
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('bulk observer reused a stale successful word check')
    failed = arithmetic.raw_trace()
    assert first[-1][2] == (0x3f800000,) and failed[-1][2] == (0x7f800000,)
    assert arena.snapshot()['phases'][-1][-1] == 'FAILED'

    # Same actual resident scalar views, ABBA order, with fresh readback and
    # equality on every trial. Timings describe only this shared-machine
    # fixture, not model or GPU throughput.
    with arena.phase('scalar-versus-bulk-readback') as workspace:
        values = tuple(put(workspace, ((0x3c00 if i%2 else 0x3f800000),),
                           16 if i%2 else 32) for i in range(8192))
        buffer = bytearray(8*len(values))
        expected = tuple(((0x3c00 if i%2 else 0x3f800000),) for i in range(len(values)))
        measurements = []
        before = arena._allocation_counter()
        for mode in ('scalar', 'bulk', 'bulk', 'scalar'):
            start = time.perf_counter()
            actual = tuple(gpu.raw_tensor(v) for v in values) if mode == 'scalar' else workspace.raw_words(values, buffer)
            elapsed = time.perf_counter()-start
            assert actual == expected
            assert not any(buffer)
            measurements.append({'mode': mode, 'host_elapsed_seconds': elapsed,
                                 'synchronous_device_to_host_copies': len(values) if mode == 'scalar' else 1})
        assert arena._allocation_counter() == before
    snapshot = arena.snapshot()
    return {'status': 'BOUNDED_RAW_READOUT_FIXTURE_PASS', 'process_id': os.getpid(),
        'all_binary16_words_checked': len(halves), 'binary32_words_checked': len(singles),
        'ordered_duplicate_subview_and_empty_rows_checked': len(views),
        'readout_guard_rejections': guards, 'opaque_padding_poison_preserved_logical_words': True,
        'buffer_poison_cannot_replace_fresh_device_observation': True,
        'failed_phase_infinity_reread_and_old_record_detachment': True,
        'benchmark_scalar_views': len(values), 'readback_trials': measurements,
        'actual_arena_bytes': snapshot['actual_tensor_arena_bytes'],
        'native_allocation_counter': snapshot['native_allocation_counter_current'],
        'new_device_allocation_during_readout': False,
        'scope': 'exact helper word and guard audit; timings are this fixture only; no model outcome or complete Runtime certificate'}


def owned_worker():
    import torch
    import audit_cuda_runtime as reference
    from audit_reference_construction import validate_residency
    cfg = reference.configuration()
    runtime = reference.ReferenceCompilerRuntime(cfg, reference.zero_program(2),
        online=reference.online(cfg, 3, unit=2, rate=F(1, 8), grid=16), cuda=reference.cuda_contract())
    candidate = runtime.construct_candidate(reference.shared_graph())
    assert candidate.status == 'BUILT_REFERENCE'
    key = runtime.snapshot().runtime_id+':cuda-raw-readout'
    boundaries = 0

    def owned_zero():
        nonlocal boundaries
        snapshot = validate_residency(runtime)
        buffer = dict(snapshot.buffers)[key]
        assert len(buffer) == 8*snapshot.cuda.contract.phase_output_cells
        assert not any(buffer)
        obj = snapshot.resources['objects'][key]
        assert obj['kind'] == 'cuda_raw_readout_workspace'
        assert obj['residency'] == {'reference_payload_bytes': len(buffer), 'physical_objects': 1}
        boundaries += 1
        return snapshot

    owned_zero()
    assert reference.deliver_context(runtime, 'observation-0', reference.domain(1)[0]).status == 'PREDICTED_REFERENCE'
    owned_zero()
    assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
    owned_zero()
    checked = reference.audit_snapshot(runtime)
    original = torch.Tensor.copy_
    armed, retained_error = True, None

    def copy_failure(destination, source, *args, **kwargs):
        nonlocal armed
        result = original(destination, source, *args, **kwargs)
        if armed and not destination.is_cuda and source.is_cuda and destination.dtype == torch.uint8:
            armed = False
            raise RuntimeError('injected failure after actual host readback')
        return result

    torch.Tensor.copy_ = copy_failure
    try:
        try:
            reference.deliver_context(runtime, 'observation-1', reference.domain(1)[1])
        except RuntimeError as error:
            retained_error = error
        else:
            raise AssertionError('unexpected copy failure was promoted to a prediction')
    finally:
        torch.Tensor.copy_ = original
    assert retained_error is not None and not armed
    snapshot = owned_zero()
    assert snapshot.halted is not None and snapshot.cursor == 1
    trace, alias = retained_error.__traceback__, None
    while trace is not None:
        if trace.tb_frame.f_code.co_name == 'copy_failure':
            alias = trace.tb_frame.f_locals['destination']
        trace = trace.tb_next
    assert alias is not None and not alias.is_cuda
    owned_view = torch.frombuffer(runtime._buffers[key], dtype=torch.uint8)
    assert alias.data_ptr() == owned_view.data_ptr() and not any(alias.tolist())
    assert snapshot.cuda.phases[-1].status == 'EXECUTION_FAILED'
    return {'status': 'OWNED_READOUT_LIFETIME_AND_FAILURE_AUDIT_PASS', 'process_id': os.getpid(),
        'zero_owned_workspace_public_boundaries': boundaries,
        'owned_workspace_bytes': len(runtime._buffers[key]),
        'checked_CUDA_phases_before_injected_failure': checked['phases'],
        'failed_copy_retains_its_actual_exception': True,
        'traceback_alias_still_has_a_paid_live_owner': True,
        'opaque_transport_bytes_cleared_before_failed_public_cut': True,
        'failed_phase_not_promoted_or_previous_cursor_advanced': True}


def simplex_worker():
    from collections import Counter
    from audit_simplex_learner import owned
    original = gpu.CudaArithmetic._raw_words
    calls = Counter()

    def counted(arithmetic):
        assert arithmetic._readout_buffer is not None
        calls[arithmetic] += 1
        return original(arithmetic)

    gpu.CudaArithmetic._raw_words = counted
    try:
        result = owned(n=2, cuda=True, bounded=True)
    finally:
        gpu.CudaArithmetic._raw_words = original
    histogram = Counter(calls.values())
    assert max(histogram) == 6 and histogram[6] == 6
    assert sum(histogram.values()) == result['CUDA']['phases']
    return {'status': 'UNENCODED_SIMPLEX_RAW_CAPTURE_BOUND_PASS', 'process_id': os.getpid(),
        'raw_capture_count_phase_histogram': dict(sorted(histogram.items())),
        'maximum_complete_captures_per_phase': 6,
        'complete_owned_simplex_audit': result}


def bounded():
    from windows_job_audit_support import run_in_job
    jobs = []
    for case in ('words', 'owned', 'simplex'):
        with tempfile.TemporaryDirectory(prefix='cuda-readout-', dir=ROOT/'runs') as directory:
            path = Path(directory)
            assert path.resolve().parent == (ROOT/'runs').resolve()
            output = path/'result.json'
            job = run_in_job(__file__, ('--worker', str(output), '--case', case), commit_limit=CAP, timeout_ms=TIMEOUT)
            result = json.loads(output.read_text(encoding='utf-8')) if output.exists() else None
        assert job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
        assert job.attached_before_resume and job.peak_job_commit <= CAP
        assert result is not None and result['process_id'] == job.process_id
        jobs.append({'case': case, 'completed_job': asdict(job), 'result': result})
    return {'status': 'DEVELOPMENT_CUDA_READOUT_AUDIT_PASS', 'workers': jobs}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--case', choices=('words', 'owned', 'simplex'), default='words')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert not (args.worker and args.write)
    workers = {'words': worker, 'owned': owned_worker, 'simplex': simplex_worker}
    result = workers[args.case]() if args.worker else bounded()
    rendered = json.dumps(result, indent=2)+'\n'
    if args.worker:
        args.worker.write_text(rendered, encoding='utf-8')
    else:
        if args.write:
            OUTPUT.write_text(rendered, encoding='utf-8')
        print(rendered, end='')
