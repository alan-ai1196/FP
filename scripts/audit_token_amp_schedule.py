"""Exact primitive controls and complete native comparisons for token AMP.

Default CPU mode imports no Torch. Physical workers require an independently
bound host/device job and are launched only by run_token_amp_audit.py.
"""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import math
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import batched_tokens as reference
from enclosed_tokens import EnclosureUnresolved
from fp_reference.binary_arithmetic import BinaryFormat, round_binary
from audit_native_tokens import fixture

HOST_CAP, BOARD_CAP, ALLOCATOR_CAP = 4 << 30, 24 << 30, 512 << 20
ELEMENT_CAP = 1 << 24
EXECUTION_ID = ('2.12.0+cu132', '7661cd9c6b841b62b7f411aa52ec51f05457263b',
                '13.2', 'NVIDIA GeForce RTX 3090', (8, 6))


class ExactPrimitives:
    def __init__(self):
        self.calls = self.words = self.half_words = 0

    def __call__(self, tag, output, *inputs):
        fmt = BinaryFormat(11, -14, 15) if output.dtype == np.float16 else amp.SINGLE
        word = np.uint16 if output.dtype == np.float16 else np.uint32
        arrays = np.broadcast_arrays(*inputs)
        expected = []
        for index in np.ndindex(output.shape):
            x = [F(int(a[index])) if a.dtype.kind in 'iu' else F(float(a[index])) for a in arrays]
            signs = [bool(np.signbit(a[index])) for a in arrays]
            negative_zero = False
            if tag == 'cast':
                value, negative_zero = x[0], not x[0] and signs[0]
            elif tag == 'ceil':
                value = F(math.ceil(x[0]))
                negative_zero = not value and signs[0]
            elif tag in ('add', 'sub'):
                value = x[0]+x[1] if tag == 'add' else x[0]-x[1]
                negative_zero = not x[0] and not x[1] and signs[0] and (signs[1] if tag == 'add' else not signs[1])
            else:
                value = x[0]*x[1] if tag == 'mul' else x[0]/x[1]
                negative_zero = not value and signs[0] != signs[1]
            rounded = round_binary(value, fmt, bit_limit=4096, negative_zero=bool(negative_zero))
            expected.append(-0.0 if rounded.negative_zero else float(rounded.value))
        want = np.asarray(expected, dtype=output.dtype).reshape(output.shape)
        if not np.array_equal(output.view(word), want.view(word)):
            mismatch = np.flatnonzero(output.view(word).ravel() != want.view(word).ravel())
            i = int(mismatch[0])
            raise AssertionError(f'{tag} RNE mismatch at {i}: {output.ravel()[i]} != {want.ravel()[i]}')
        self.calls += 1
        self.words += output.size
        self.half_words += output.size if output.dtype == np.float16 else 0


def grid_witness(arithmetic):
    checked = refused = 0
    for q in (0, 1, 65536, 1 << 31, reference.WORD_MAX):
        for step in (F(-3, 2), F(-1, 1 << 24), F(0), F(1, 1 << 24), F(1, 4), F(1), F(3, 2)):
            exact = max(0, math.floor(F(q)-step))
            try:
                value = arithmetic.project(arithmetic.array(q, 'int64'), arithmetic.constant(step), arithmetic.constant(1))
            except EnclosureUnresolved:
                assert exact > reference.WORD_MAX
                refused += 1
            else:
                assert int(arithmetic.raw(value)) == exact
                checked += 1
    # This discrepancy is a deterministic arithmetic witness, not a training
    # outcome. The small positive step survives the integer-grid update.
    q, step = 65536, F(1, 4096)
    naive = np.floor(np.float32(q)-np.float32(float(step)))
    assert int(naive) == q and max(0, q-math.ceil(step)) == q-1
    return dict(exact_projected_cells=checked, word_envelope_refusals=refused,
        naive_float32_master=int(naive), native_integer_master=q-1)


def underflow_witness(a):
    import native_tokens as tokens
    import native_readout as readout
    from causal_tokens import TokenSources
    from fp_reference.program import Product
    d = tokens.Definition(TokenSources(2, 1), 1, (Product('f', 0, 0),), 0, (1,),
        readout.Spec((F(1), F(1)), 1, 16, F(1, 16), 1))
    root = tokens.initialize(d, (1,), (), (65536,), embedding_overrides=((1, 0, 65536),))
    origin = reference.Origin.from_native(root, element_cap=100)
    state = amp.State.initialize(origin, a)
    kernel = amp.Kernel(d, a, element_cap=100)
    prediction = root.predict()
    assert prediction.values[-1] == F(1, 1 << 32)
    assert prediction.output.mass(1)/prediction.output.normalizer == F(1, 2)
    pending = kernel.unit(state, (root.source_window(),), (1,))
    assert a.raw(pending.values)[-1, 0] == 0
    assert float(a.raw(pending.target_mass)[0]/a.raw(pending.normalizer)[0]) == 0.5
    exact = root.observe(prediction, 1).commit()
    following = pending.commit(a)
    actual = following.read(a)
    exact_origin = reference.Origin.from_native(exact, element_cap=100)
    assert exact_origin.W[:, 0].tolist() == [65535, 65536]
    assert actual.W[:, 0].tolist() == [65536, 65536]
    # This next source is the ordinary successor of the actual target1,
    # whose retained embedding is one. No foreign context is substituted.
    next_native = exact.predict()
    next_physical = kernel.unit(following, (exact.source_window(),), (1,))
    native_probability = next_native.output.mass(1)/next_native.output.normalizer
    actual_probability = F(float(a.raw(next_physical.target_mass)[0]))/F(float(a.raw(next_physical.normalizer)[0]))
    assert native_probability == F(131072, 262143) and actual_probability == F(1, 2)
    return dict(native_first_feature='1/4294967296', stored_half_feature=0,
        first_probability_error='0', native_next_masters=[65535, 65536], physical_next_masters=[65536, 65536],
        next_native_probability=str(native_probability), next_physical_probability=str(actual_probability),
        next_probability_gap=str(native_probability-actual_probability), actual_ordinary_successor=True)


def distances(pending, bounds, a):
    """Full basis discrepancy upper bounds, not a bridge or tolerance waiver."""
    def upper(actual, enclosed):
        actual = a.raw(actual).astype(np.float64)
        if not actual.size:
            return 0.0
        return float(np.max(np.maximum(abs(actual-enclosed.lower), abs(actual-enclosed.upper))))
    assert np.array_equal(pending.embedding_ids, bounds.embedding_ids)
    assert np.array_equal(pending.correction_ids, bounds.correction_ids)
    return {key: upper(getattr(pending, key), getattr(bounds, key)) for key in
        ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections')}


def endpoint_errors(actual, exact):
    return {key: int(np.max(np.abs(getattr(actual, key).astype(np.int64)-getattr(exact, key).astype(np.int64)), initial=0))
            for key in ('E', 'C', 'W')}


def small(*, cuda=False):
    audit = ExactPrimitives()
    a = amp.Arithmetic(cuda=cuda, audit=audit)
    grid = grid_witness(a)
    underflow = underflow_witness(a)
    rows = []
    for unit in (1, 2):
        for kind in ('mixed', 'zero-embedding', 'zero-core'):
            d, root = fixture(unit, kind)
            origin = reference.Origin.from_native(root, element_cap=ELEMENT_CAP)
            state = amp.State.initialize(origin, a)
            kernel, control = amp.Kernel(d, a, element_cap=ELEMENT_CAP), reference.Kernel(d, element_cap=ELEMENT_CAP)
            exact = origin
            word = (0, 1, 1, 0, 0, 1)
            maxima, masters = {}, dict(E=0, C=0, W=0)
            for offset in range(0, len(word), unit):
                windows = tuple(d.sources.window(word, t) for t in range(offset, offset+unit))
                targets = word[offset:offset+unit]
                old_bytes = state.read(a)
                pending = kernel.unit(state, windows, targets)
                native = control.bound(exact, windows, targets)
                for key, value in distances(pending, native, a).items():
                    maxima[key] = max(value, maxima.get(key, 0))
                following, exact = pending.commit(a), native.commit()
                assert state.read(a) == old_bytes
                actual = following.read(a)
                assert (actual.cursor, actual.optimizer_steps, actual.source) == (exact.cursor, exact.optimizer_steps, exact.source)
                for key, value in endpoint_errors(actual, exact).items():
                    masters[key] = max(value, masters[key])
                state = following
            rows.append(dict(unit=unit, initializer=kind, commits=len(word)//unit,
                full_basis_absolute_error_upper=maxima, maximum_master_grid_distance=masters,
                previous_state_unchanged=True, complete_source_and_clock_match=True))
    return dict(status='PASS_EXACT_PHYSICAL_SCHEDULE' if cuda else 'PASS_CPU_SCHEDULE', schedule=amp.SCHEDULE,
        grid=grid, underflow_counterexample=underflow, exact_primitive_calls=audit.calls, exact_primitive_words=audit.words,
        half_words=audit.half_words, native_comparisons=rows,
        scope='exact primitive schedule checks and complete finite native discrepancy report; no Runtime or issued bridge')


def actual_text():
    from audit_token_reference_host import text_fixture
    d, origin, windows, targets, identity = text_fixture()
    a = amp.Arithmetic(cuda=True)
    state = amp.State.initialize(origin, a)
    kernel = amp.Kernel(d, a, element_cap=ELEMENT_CAP)
    control = reference.Kernel(d, element_cap=ELEMENT_CAP)
    import torch
    torch.cuda.synchronize()
    started = time.perf_counter()
    pending = kernel.unit(state, windows, targets)
    following = pending.commit(a)
    torch.cuda.synchronize()
    elapsed = time.perf_counter()-started
    bounds = control.bound(origin, windows, targets)
    exact = bounds.commit()
    actual = following.read(a)
    assert (actual.cursor, actual.optimizer_steps, actual.source) == (exact.cursor, exact.optimizer_steps, exact.source)
    assert state.read(a) == origin
    # Independent CPU execution retains its own actual integer masters;
    # equality covers every stored value, gradient-basis and successor word.
    cpu = amp.Arithmetic()
    cpu_state = amp.State.initialize(origin, cpu)
    cpu_pending = amp.Kernel(d, cpu, element_cap=ELEMENT_CAP).unit(cpu_state, windows, targets)
    for key in ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections'):
        x, y = a.raw(getattr(pending, key)), cpu.raw(getattr(cpu_pending, key))
        assert x.dtype == y.dtype and x.shape == y.shape
        assert x.tobytes() == y.tobytes(), 'CPU/device word mismatch in '+key
    assert cpu_pending.commit(cpu).read(cpu) == actual
    return dict(status='PASS_ACTUAL_TEXT_SCHEDULE', vocabulary=d.output.labels, context=d.sources.context,
        unit=d.output.update_unit, parameters=d.slot_count, physical_operations=a.operations,
        physical_unit_and_commit_seconds=elapsed, full_basis_absolute_error_upper=distances(pending, bounds, a),
        maximum_master_grid_distance=endpoint_errors(actual, exact),
        complete_CPU_device_endpoint_and_basis_word_equality=True, previous_state_unchanged=True,
        source=identity, loss_scored=False, reference_endpoint_used_for_device_update=False,
        scope='one complete supplied-fixture unit and finite discrepancy report; no owned bridge, online or language-quality claim')


def worker(case, output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.cuda_device import CudaDeviceContract, _CudaDevice
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    before = measured(host)
    result, code = {}, 0
    try:
        import torch
        identity = (str(torch.__version__), torch.version.git_version, torch.version.cuda,
            torch.cuda.get_device_name(0), tuple(torch.cuda.get_device_capability(0)))
        if identity != EXECUTION_ID:
            raise RuntimeError('actual Torch/CUDA/device build differs from registered target')
        device = _CudaDevice(CudaDeviceContract(BOARD_CAP, {'deployment': BOARD_CAP, 'compiler': BOARD_CAP}), 0)
        torch.set_num_threads(1)
        torch.cuda.set_per_process_memory_fraction(ALLOCATOR_CAP/torch.cuda.get_device_properties(0).total_memory, 0)
        torch.cuda.reset_peak_memory_stats(0)
        result = small(cuda=True) if case == 'small-exact' else actual_text()
        result.update(before=before, after=measured(host), device=asdict(device.check()), build=list(identity),
            allocator_cap=ALLOCATOR_CAP, max_allocated=torch.cuda.max_memory_allocated(0),
            max_reserved=torch.cuda.max_memory_reserved(0))
        assert result['max_reserved'] <= ALLOCATOR_CAP
    except Exception as error:
        result = dict(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000], before=before)
        code = 2
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('small-exact', 'train-context512'))
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker:
        if not args.output:
            parser.error('physical worker needs output and a preattached host job')
        raise SystemExit(worker(args.worker, args.output))
    result = small()
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_AMP_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
