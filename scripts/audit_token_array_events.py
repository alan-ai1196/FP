"""CPU/exact controls and shape preflight for the explicit token array kernel.

No CUDA import in the default audit or preflight. The fresh actual-device
worker is run only by run_token_array_audit.py after source registration.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference import token_amp as amp, token_batch as ref, token_streaming as stream
from fp_reference.token_arrays import CPUArrays, CudaArrays
from fp_reference.token_array_events import Kernel
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
from audit_native_tokens import fixture
from audit_token_amp_schedule import ExactPrimitives, EXECUTION_ID

ELEMENT_CAP, CELL_CAP = 1 << 24, 1 << 26
HOST_CAP, BOARD_CAP, ARENA, READOUT = 4 << 30, 24 << 30, 1 << 30, 4 << 20
DEADLINE = 900000


def refuses(operation, kind=ContractError):
    try:
        operation()
    except kind:
        return
    raise AssertionError('expected exact array execution refusal')


def same(raw, expected):
    assert (raw.dtype, raw.shape, raw.tobytes()) == (expected.dtype, expected.shape, expected.tobytes())
    return raw.size


def compare_state(actual, expected, a):
    assert type(actual) is type(expected)
    assert (actual.cursor, actual.source) == (expected.cursor, expected.source)
    count = 0
    if type(actual) is amp.State:
        assert actual.definition == expected.definition and actual.optimizer_steps == expected.optimizer_steps
        for key in ('E', 'C', 'W'):
            count += same(a.raw(getattr(actual, key)), getattr(expected, key))
        return count
    assert type(actual) is stream.Pending
    assert (actual.windows, actual.targets) == (expected.windows, expected.targets)
    count += compare_state(actual.origin, expected.origin, a)
    for left, right in zip(actual.leaves, expected.leaves):
        assert left.origin is actual.origin and (left.windows, left.targets) == (right.windows, right.targets)
        for key in ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections'):
            count += same(a.raw(getattr(left, key)), getattr(right, key))
        for key in ('embedding_ids', 'correction_ids'):
            count += same(getattr(left, key), getattr(right, key))
    def forest(left, right):
        assert type(left) is type(right) is stream.Forest and left.count == right.count
        assert tuple(b.count for b in left.blocks) == tuple(b.count for b in right.blocks)
        return sum(same(a.raw(x.value), y.value) for x, y in zip(left.blocks, right.blocks))
    count += forest(actual.core, expected.core)+forest(actual.common, expected.common)
    for key in ('embedding', 'corrections'):
        left, right = getattr(actual, key), getattr(expected, key)
        assert tuple(k for k, _ in left) == tuple(k for k, _ in right)
        count += sum(forest(x, y) for (_, x), (_, y) in zip(left, right))
    return count


def cpu_controls():
    oracle = ExactPrimitives()
    counts = dict(histories=0, events=0, commits=0, complete_state_words=0, output_arrays=0, output_cells=0)
    for unit, kind, word in product((1, 2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, native = fixture(unit, kind)
        origin = ref.Origin.from_native(native, element_cap=ELEMENT_CAP)
        k = Kernel(d, element_cap=ELEMENT_CAP)
        a = CPUArrays(element_cap=ELEMENT_CAP, cell_cap=CELL_CAP, audit=oracle)
        current = k.upload(origin, a)
        prepared, pending = k.prepare(current, a), None
        control_a = amp.Arithmetic()
        control_k = stream.Kernel(d, control_a, element_cap=ELEMENT_CAP)
        expected = amp.State.initialize(origin, control_a)
        for target in word:
            window = current.source if pending is None else pending.source
            old, old_expected = pending, expected
            pred = k.predict(prepared, window, a)
            leaf = k.observe(prepared, pred, window, target, a)
            pending = k.append(pending, leaf, a)
            expected = control_k.observe(expected, control_k.predict(expected), target)
            counts['complete_state_words'] += compare_state(pending, expected, a)
            if old is not None:
                compare_state(old, old_expected, a)
            counts['events'] += 1
            if pending.unit_count == unit:
                current, expected = k.commit(pending, a), control_k.commit(expected)
                counts['complete_state_words'] += compare_state(current, expected, a)
                prepared, pending = k.prepare(current, a), None
                counts['commits'] += 1
            else:
                refuses(lambda: k.commit(pending, a))
        a.check()
        counts['histories'] += 1
        counts['output_arrays'] += len(a.records)
        counts['output_cells'] += a.cells
    counts.update(exact_primitive_calls=oracle.calls, exact_primitive_words=oracle.words, half_words=oracle.half_words)
    return counts


def attacks():
    d, native = fixture(4, 'mixed')
    origin = ref.Origin.from_native(native, element_cap=ELEMENT_CAP)
    k = Kernel(d, element_cap=ELEMENT_CAP)
    a = CPUArrays(element_cap=ELEMENT_CAP, cell_cap=CELL_CAP)
    current = k.upload(origin, a)
    prepared = k.prepare(current, a)
    pred = k.predict(prepared, current.source, a)
    refuses(lambda: k.observe(replace(prepared), pred, current.source, 0, a))
    refuses(lambda: k.observe(prepared, pred, current.source.append(0), 0, a))
    refuses(lambda: k.observe(prepared, pred, current.source, d.output.labels, a))
    refuses(lambda: k.observe(prepared, replace(pred, normalizer=pred.normalizer.reshape((1,))), current.source, 0, a))
    rows = a.ingress(np.asarray([[1.0], [2.0]], dtype=np.float32), 'float32')
    count = a.cells
    refuses(lambda: a.replace_rows(rows, (0, 0), rows))
    assert a.cells == count
    refuses(lambda: a.take(rows, (2,)))
    assert a.cells == count
    tiny = CPUArrays(element_cap=2, cell_cap=1)
    refuses(lambda: tiny.zeros((2,)), ResourceExceeded)
    assert tiny.cells == 0 and not tiny.records
    refuses(lambda: tiny.zeros((3,)), ArithmeticUnresolved)
    assert tiny.cells == 0 and not tiny.records
    q = a.ingress(np.asarray([65536], dtype=np.int64), 'int64')
    g = a.rational((F(1, 4096),))
    same(a.raw(a.project(q, g, a.constant(1))), np.asarray([65535], dtype=np.int64))
    refuses(lambda: a.project(a.ingress(np.asarray([ref.WORD_MAX], dtype=np.int64), 'int64'),
                             a.rational((F(-1),)), a.constant(1)), ArithmeticUnresolved)
    a.check()
    return dict(refusals=9, duplicate_write_and_budget_refuse_before_allocation=True,
                exact_integer_projection_survives_float32_absorption=True)


class Phases:
    """Diagnostic runner: paired CPU schedule never supplies device results."""
    def __init__(self, arena=None, *, exact=False):
        self.arena, self.buffer = arena, bytearray(READOUT) if arena is not None else None
        self.oracle = ExactPrimitives() if exact else None
        self.counts = dict(phases=0, arrays=0, cells=0, extent_bytes=0, maximum_phase_cells=0,
                           maximum_array_bytes=0, checked_device_words=0)

    def phase(self, name, expected_call, actual_call=None):
        a = CPUArrays(element_cap=ELEMENT_CAP, cell_cap=CELL_CAP, audit=self.oracle)
        expected = expected_call(a)
        a.check()
        c = self.counts
        c['phases'] += 1
        c['arrays'] += len(a.records)
        c['cells'] += a.cells
        c['extent_bytes'] += 8+sum(max(8, (value.nbytes+7)//8*8) for _, value in a.records)
        c['maximum_phase_cells'] = max(c['maximum_phase_cells'], a.cells)
        c['maximum_array_bytes'] = max(c['maximum_array_bytes'], *(v.nbytes for _, v in a.records))
        if self.arena is None:
            self.last = a
            return expected, expected, a
        with self.arena.phase(name) as workspace:
            b = CudaArrays(workspace, self.buffer, element_cap=ELEMENT_CAP, cell_cap=CELL_CAP)
            actual = actual_call(b)
            assert (len(a.records), a.cells, a.bytes) == (len(b.records), b.cells, b.bytes)
            for (left_tag, left), (right_tag, right) in zip(a.records, b.records):
                assert left_tag == right_tag
                c['checked_device_words'] += same(b.raw(right), left)
            b.check()
            assert not any(self.buffer)
        self.last = b
        return expected, actual, b


def trajectory(origin, windows, targets, phases, *, independent=True):
    d = origin.definition
    k = Kernel(d, element_cap=ELEMENT_CAP)
    cpu, gpu, a = phases.phase('token:init', lambda a: k.upload(origin, a), lambda a: k.upload(origin, a))
    cp, gp, a = phases.phase('token:prepare', lambda a: k.prepare(cpu, a), lambda a: k.prepare(gpu, a))
    pending_cpu = pending_gpu = None
    control_a = amp.Arithmetic()
    control_k = stream.Kernel(d, control_a, element_cap=ELEMENT_CAP)
    control = amp.State.initialize(origin, control_a)
    events = commits = checked = 0
    for window, target in zip(windows, targets):
        pred_cpu, pred_gpu, a = phases.phase('token:predict', lambda a: k.predict(cp, window, a), lambda a: k.predict(gp, window, a))
        def observe(prepared, pred, previous, a):
            leaf = k.observe(prepared, pred, window, target, a)
            return k.append(previous, leaf, a)
        pending_cpu, pending_gpu, a = phases.phase('token:observe',
            lambda a: observe(cp, pred_cpu, pending_cpu, a), lambda a: observe(gp, pred_gpu, pending_gpu, a))
        if independent:
            control = control_k.observe(control, control_k.predict(control, window), target, window=window)
        events += 1
        if pending_cpu.unit_count == d.output.update_unit:
            if independent:
                checked += compare_state(pending_gpu, control, a)
            cpu, gpu, a = phases.phase('token:commit', lambda a: k.commit(pending_cpu, a), lambda a: k.commit(pending_gpu, a))
            if independent:
                control = control_k.commit(control)
                checked += compare_state(gpu, control, a)
            # Read the retained old state after commit; its masters/forests must
            # still agree with the independently executed explicit CPU path.
            checked += compare_state(pending_gpu, pending_cpu, a)
            pending_cpu = pending_gpu = None
            commits += 1
            if events < len(targets):
                cp, gp, a = phases.phase('token:prepare', lambda a: k.prepare(cpu, a), lambda a: k.prepare(gpu, a))
    assert pending_cpu is None and events == len(targets)
    return dict(events=events, commits=commits, complete_state_words=checked,
        endpoint_parameters=d.slot_count, final_cursor=gpu.cursor, optimizer_steps=gpu.optimizer_steps)


def small_cases(phases):
    reports = []
    for unit, kind, word in ((2, 'mixed', (0, 1, 1, 0)*2), (4, 'mixed', (1, 0, 0, 1)*2),
                             (4, 'zero-embedding', (0, 1, 0, 1)), (4, 'zero-core', (1, 0, 1, 0))):
        d, native = fixture(unit, kind)
        origin = ref.Origin.from_native(native, element_cap=ELEMENT_CAP)
        windows = tuple(d.sources.window(word, i) for i in range(len(word)))
        reports.append(trajectory(origin, windows, word, phases))
    d, native = fixture(4, 'mixed')
    origin = ref.Origin.from_native(native, element_cap=ELEMENT_CAP)
    word, ids = (0, 1, 0, 1), (3, 1, 3, 0)
    reports.append(trajectory(origin, tuple(d.sources.window(word, i) for i in ids), tuple(word[i] for i in ids), phases))
    return reports


def text_case(phases):
    from audit_token_reference_host import text_fixture
    d, origin, windows, targets, identity = text_fixture()
    result = trajectory(origin, windows, targets, phases)
    result.update(vocabulary=d.output.labels, context=d.sources.context, corpus=identity)
    return result


def preflight():
    rows = []
    for case in ('small', 'train-context512'):
        phases = Phases()
        result = small_cases(phases) if case == 'small' else text_case(phases)
        assert phases.counts['extent_bytes'] <= ARENA
        assert phases.counts['maximum_array_bytes'] <= READOUT
        rows.append(dict(case=case, counts=phases.counts, trajectory=result))
    return dict(status='CPU_ARRAY_PREFLIGHT', arena_bytes=ARENA, host_job_cap=HOST_CAP,
        phase_cell_cap=CELL_CAP, array_cap=ELEMENT_CAP, readout_bytes=READOUT, deadline_ms=DEADLINE,
        cases=rows, scope='CPU shapes/numerics only; no measured device or process bound')


def device_refusals(phases):
    """Actual arena boundaries, without making an unowned CUDA allocation."""
    old_a, arena = phases.last, phases.arena
    old = old_a.records[-1][1]
    old_bytes = old_a.raw(old).tobytes()
    refuses(lambda: old_a.zeros((1,)))  # Closed phase has no output authority.
    with arena.phase('token:storage-refusals') as workspace:
        a = CudaArrays(workspace, phases.buffer, element_cap=ELEMENT_CAP, cell_cap=CELL_CAP)
        refuses(lambda: a.copy(np.zeros((1,), dtype=np.float32)))
        refuses(lambda: workspace.written(old))
        uninitialized = workspace.empty((1,), a.xp.int64, 'test-uninitialized')
        refuses(lambda: a.raw(uninitialized))
        refuses(lambda: a.copy(uninitialized))
        refuses(lambda: workspace.raw_bytes((old,), bytearray(1)), ResourceExceeded)
        rows = a.zeros((2, 1))
        count, cursor = a.cells, arena._cursor
        refuses(lambda: a.replace_rows(rows, (0, 0), rows))
        assert (a.cells, arena._cursor) == (count, cursor)
        tiny = CudaArrays(workspace, phases.buffer, element_cap=ELEMENT_CAP, cell_cap=1)
        refuses(lambda: tiny.zeros((2,)), ResourceExceeded)
        assert not tiny.records and tiny.cells == 0 and arena._cursor == cursor
        empty = a.ingress(np.asarray([], dtype=np.int64), 'int64')
        assert a.raw(empty).shape == (0,)
        assert a.raw(old).tobytes() == old_bytes and not any(phases.buffer)
        a.check()
    return dict(refusals=8, old_initialized_words_unchanged=True, empty_integer_view_checked=True,
                borrowed_readout_cleared=True)


def worker(case, output):
    from dataclasses import asdict
    import os
    import time
    import traceback
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.cuda_device import CudaDeviceContract, _CudaDevice
    from fp_reference.cuda_storage import CudaArena, CudaStorageContract
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    before = measured(host)
    result = dict(status='RUNNING', case=case, before=before)
    output = Path(output)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    arena, phases, code = None, None, 0
    start = time.perf_counter()
    try:
        import torch
        identity = (str(torch.__version__), torch.version.git_version, torch.version.cuda,
                    torch.cuda.get_device_name(0), tuple(torch.cuda.get_device_capability(0)))
        if identity != EXECUTION_ID:
            raise RuntimeError('actual Torch/CUDA/device build differs from registered target')
        device = _CudaDevice(CudaDeviceContract(BOARD_CAP, {'deployment': BOARD_CAP, 'compiler': BOARD_CAP}), 0)
        torch.set_num_threads(1)
        # No peak/counter/cache reset or process allocator-fraction mutation.
        arena = CudaArena(CudaStorageContract(ARENA, ARENA,
            {role: (ARENA, ARENA) for role in ('deployment', 'compiler')}))
        phases = Phases(arena, exact=case == 'small')
        result['trajectory'] = small_cases(phases) if case == 'small' else text_case(phases)
        trajectory_cursor = arena._cursor
        assert trajectory_cursor == phases.counts['extent_bytes']
        result['storage_controls'] = device_refusals(phases)
        observed = device.check()
        result.update(status='PASS_ACTUAL_ARENA_TOKEN_SCHEDULE', device=asdict(observed), build=list(identity))
        if phases.oracle is not None:
            result['exact_primitive_words'] = phases.oracle.words
            result['exact_half_words'] = phases.oracle.half_words
    except Exception as error:
        result.update(status='FAILED', error_type=type(error).__name__, reason=str(error)[:1600],
                      traceback=traceback.format_exc()[-5000:])
        code = 2
    finally:
        result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-start)
        if phases is not None:
            result['arrays'] = phases.counts
        if arena is not None:
            # Minimal numeric accounting; do not serialize hundreds of thousands
            # of tensor/phase descriptors or read the entire backing allocation.
            result['arena'] = dict(status='ACTIVE' if arena._failure is None else 'UNRESOLVED',
                failure=arena._failure, consumed_extent=arena._cursor, regions=len(arena._regions),
                phases=len(arena._phases), initialized_regions=sum(r.initialized for r in arena._regions),
                native_allocation_counter_at_binding=arena._counter, **arena._last_usage)
        output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', choices=('small', 'train-context512'))
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker:
        if not args.output:
            parser.error('physical worker requires output and an externally preattached host job')
        raise SystemExit(worker(args.worker, args.output))
    if args.preflight:
        result, suffix = preflight(), 'PREFLIGHT'
    else:
        result, suffix = dict(status='PASS_CPU_ARRAY_EVENTS', controls=cpu_controls(), attacks=attacks()), 'CPU'
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/f'evidence/minimal/FP_TOKEN_ARRAY_{suffix}.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
