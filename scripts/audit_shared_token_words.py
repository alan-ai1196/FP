"""Exact CPU control for sharing fresh immutable token state byte images.

Uses the complete phase executor with only its array backend substituted.
No corpus, CUDA allocation, Runtime certificate or model score is involved.
"""
from contextlib import contextmanager
from dataclasses import fields, is_dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from audit_native_tokens import fixture
from audit_owned_token_learner import registration
from audit_token_cuda_owner import cuda_contract
from fp_reference import token_cuda_prefix as execution
from fp_reference.core import ContractError
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.encoding import pack
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_cuda_state import ArrayWords, share_state_bytes
from fp_reference.token_execution import TokenReferenceMachine
from fp_reference.token_sources import TokenContext, TokenValues


def payloads(value, path=()):
    if type(value) is bytes:
        yield path, value
    elif type(value) is tuple:
        for i, child in enumerate(value):
            yield from payloads(child, path+(i,))
    elif is_dataclass(value):
        for field in fields(value):
            yield from payloads(getattr(value, field.name), path+(field.name,))


def set_path(value, path, data):
    if not path:
        return data
    key, *rest = path
    if type(value) is tuple:
        return tuple(set_path(child, rest, data) if i == key else child for i, child in enumerate(value))
    return replace(value, **{key: set_path(getattr(value, key), rest, data)})


def unique_bytes(rows):
    unique = {id(data): data for row in rows for _, data in payloads(row.raw_state)}
    return sum(map(len, unique.values()))


def run(word, unit, sharing, fault=None):
    reads, backends = [], []
    original_raw = CPUArrays.raw

    def measured_raw(self, value):
        raw = original_raw(self, value)
        if any(self is backend for backend in backends):
            reads.append((tuple(raw.shape), str(raw.dtype), raw.tobytes()))
        return raw

    class Arena:
        @contextmanager
        def phase(self, identity):
            yield SimpleNamespace(index=0)

        def require_initialized(self, value):
            pass  # CPU phase-logic control, not a physical residency check.

    def arrays(workspace, readout_buffer, **kwargs):
        value = CPUArrays(**kwargs)
        backends.append(value)
        return value

    d, initial = fixture(unit, 'mixed')
    cc, program, online = registration(d, initial)
    cfg, machine = cuda_contract(cc.initializer_pattern), TokenReferenceMachine(cc.initializer_pattern)
    native = machine.initial_state(program, cc.semantics, machine.initializer(program.slot_count, cc.initializer_pattern),
                                   0, spec=online.learner, bit_limit=32768)
    owner = SimpleNamespace(contract=cfg, arena=Arena(), current={}, staged={}, predicted={}, phases={}, _values={})

    def phase(kind, context=None, forecast=None, target=None):
        with patch.object(CPUArrays, 'raw', measured_raw), patch.object(execution, 'CudaArrays', arrays), patch.object(execution, 'share_state_bytes',
                share_state_bytes if sharing else lambda fresh, retained: fresh):
            row, error = execution.execute(owner, f'cpu:{len(owner.phases)}', kind, program, 'incumbent', native,
                rules=cc.semantics, spec=online.learner, bit_limit=32768, ordinary_cursor=native.cursor,
                origin='construction' if kind == 'initialize' else 'ordinary',
                observation_id=f'train/{native.cursor if kind == "predict" else native.cursor-1}',
                sources=context, reference_prediction=forecast, target=target,
                normalizer_cap=F(100), activation_cap=F(100), source_domain=None, readout_buffer=None)
        if error is None:
            _CudaPrefix.accept(owner, row)
        return row, error

    row, error = phase('initialize')
    assert error is None, row.reason
    owner.current['incumbent'] = row.object_id
    for target in word:
        context = TokenValues(TokenContext(cfg.initializer.sources, native.source.position, native.source.past))
        forecast = machine.predict(program, cc.semantics, native, context, bit_limit=32768)
        row, error = phase('predict', context, forecast)
        assert error is None, row.reason
        native = machine.observe(program, native, online.learner, forecast, target,
                                 rules=cc.semantics, bit_limit=32768, sources=context)
        row, error = phase('observe', context, forecast, target)
        assert error is None, row.reason
        if native.unit_count == unit:
            native = machine.commit(native, online.learner, bit_limit=32768)
            row, error = phase('commit')
            assert error is None, row.reason
        owner.current['incumbent'] = row.object_id

    if fault is not None:
        before = owner.phases[owner.current['incumbent']]
        old_bytes = pack(before)
        value = owner._values[before.object_id]
        if fault == 'master':
            value.origin.E.flat[0] += 1
        elif fault == 'leaf':
            value.state.leaves[0].values.flat[0] += np.float32(1)
        else:
            raise AssertionError(fault)
        context = TokenValues(TokenContext(cfg.initializer.sources, native.source.position, native.source.past))
        forecast = machine.predict(program, cc.semantics, native, context, bit_limit=32768)
        failed, error = phase('predict', context, forecast)
        assert type(error) is ContractError and 'changed after its owned phase' in failed.reason
        assert failed.status == 'EXECUTION_FAILED' and failed.raw_state != before.raw_state
        assert pack(before) == old_bytes
        assert owner.current['incumbent'] == before.object_id
    return tuple(owner.phases.values()), reads


def cpu():
    histories = phases = canonical_bytes = read_calls = read_bytes = 0
    old_payload = shared_payload = 0
    for unit, word in product((1, 2, 4), product((0, 1), repeat=4)):
        old, old_reads = run(word, unit, False)
        shared, shared_reads = run(word, unit, True)
        assert old_reads == shared_reads
        for a, b in zip(old, shared, strict=True):
            left, right = pack(a), pack(b)
            assert left == right
            canonical_bytes += len(left)
        histories += 1
        phases += len(old)
        read_calls += len(old_reads)
        read_bytes += sum(len(data) for _, _, data in old_reads)
        old_payload += unique_bytes(old)
        shared_payload += unique_bytes(shared)
        assert unique_bytes(shared) < unique_bytes(old)
    # Actual changed CPU arrays are freshly recaptured and refused, including
    # the complete changed state in the failure record. Sharing cannot mask it.
    failures = []
    for fault in ('master', 'leaf'):
        old, a = run((0, 1), 4, False, fault)
        shared, b = run((0, 1), 4, True, fault)
        assert a == b and pack(old) == pack(shared)
        failures.append(fault)

    raw = next(row.raw_state for row in reversed(shared) if row.raw_state.unit_count == 2)
    original = pack(raw)
    changed_fields = 0
    for path, data in payloads(raw):
        if not data:
            continue
        fresh = set_path(raw, path, bytes([data[0] ^ 1])+data[1:])
        result = share_state_bytes(fresh, raw)
        assert pack(result) == pack(fresh) and pack(result) != original
        changed_fields += 1
    assert pack(raw) == original
    # Sharing an equal string does not replace fresh shape/dtype or metadata.
    bit_fields = 0
    for dtype in ('float16', 'float32', 'int64'):
        for shape in ((2,), (1, 2)):
            data = np.asarray([0, -0.0], dtype=dtype).tobytes()
            fresh_array = ArrayWords(shape, dtype, data)
            fresh = replace(raw, prepared=(fresh_array,)+raw.prepared[1:])
            hint = replace(raw, prepared=(ArrayWords((len(data),), 'untrusted', bytes(bytearray(data))),)+raw.prepared[1:])
            result = share_state_bytes(fresh, hint)
            assert pack(result) == pack(fresh)
            assert result.prepared[0].data is hint.prepared[0].data
            mutable = replace(hint, prepared=(replace(hint.prepared[0], data=bytearray(data)),)+hint.prepared[1:])
            assert share_state_bytes(fresh, mutable).prepared[0].data is fresh_array.data
            bit_fields += 1
    zero = ArrayWords((1,), 'float32', np.asarray([0.0], dtype=np.float32).tobytes())
    negative = replace(zero, data=np.asarray([-0.0], dtype=np.float32).tobytes())
    fresh = replace(raw, prepared=(negative,)+raw.prepared[1:])
    hint = replace(raw, prepared=(zero,)+raw.prepared[1:])
    assert share_state_bytes(fresh, hint).prepared[0].data is negative.data
    assert 'torch' not in sys.modules
    return dict(status='PASS_FRESH_TOKEN_IMAGE_SHARING_CPU', histories=histories,
        compared_complete_phases=phases, identical_canonical_bytes=canonical_bytes,
        identical_fresh_read_calls=read_calls, identical_fresh_read_bytes=read_bytes,
        aggregate_unique_state_payload_bytes_without_sharing=old_payload,
        aggregate_unique_state_payload_bytes_with_sharing=shared_payload,
        changed_payload_fields_preserved=changed_fields, metadata_and_mutable_hint_cases=bit_fields,
        signed_zero_distinguished=True, actual_array_mutation_refusals=failures,
        scope='exact CPU phase-logic/storage control; no CUDA/whole-host/runtime-certificate/throughput/model claim')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = cpu()
    if args.write:
        (ROOT/'evidence/minimal/FP_SHARED_TOKEN_WORDS_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
