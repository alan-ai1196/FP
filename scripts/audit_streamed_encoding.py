"""Exact old/new canonical-byte checks and an optional native CPU profile.

No CUDA, text score, new representation authority or discarded coordinates.
The historical writer is loaded from Git, not kept as another implementation.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import cProfile
import json
import pstats
import subprocess
import sys
import time
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded

PREVIOUS = 'e3faaf5fdc7c617837fccfc27136561b82fa80d7'


@dataclass(frozen=True)
class Record:
    label: str
    value: object


class Choice(Enum):
    VALUE = ('a', F(2, 3))


def previous():
    path = 'src/reference_compiler/fp_reference/encoding.py'
    body = subprocess.check_output(['git', 'show', PREVIOUS+':'+path], cwd=ROOT, encoding='utf-8')
    module = types.ModuleType('fp_reference._previous_encoding')
    module.__package__ = 'fp_reference'
    exec(compile(body, 'git:'+PREVIOUS+':'+path, 'exec'), module.__dict__)
    return module


def emitted(writer, value, packed, spaced):
    return ''.join(writer.fragments(value, packed=packed, spaced=spaced)).encode('utf-8', 'surrogatepass')


def refused(call, kinds=(ContractError, ResourceExceeded)):
    try:
        call()
    except kinds:
        return
    raise AssertionError('an invalid or unfunded serialization succeeded')


def audit():
    old = previous()
    atoms = (None, False, True, -17, 0, 17, F(-2, 3), F(1, 7), '', '\\"\n',
             '\x7f\ud800', '\U0001f600', '\ud83d\ude00', b'', bytes(range(256)))
    values = list(atoms)
    values.extend(tuple(row) for row in product(atoms[:8], repeat=3))
    values.extend((list(atoms), Record('typed', atoms),
        {'\ud83d\ude00': 1, '\U0001f600': 2, F(-1, 3): Record('x', (1, 2)), (3, 'x'): False},
        b'\0\xff'*513, 'a'*255+'\ud800\U0001f600'+'"\\\n'*257,
        -(1 << 4095), F(1, 1 << 4095)))
    for depth in (1, 4, 16, 32):
        item = atoms
        for _ in range(depth):
            item = Record('nested', (item,))
        values.append(item)
    comparisons = expanded = 0
    for value, packed, spaced in product(values, (False, True), (False, True)):
        wanted = emitted(old, value, packed, spaced)
        actual = emitted(encoding, value, packed, spaced)
        assert actual == wanted
        comparisons += 1
        expanded += len(actual)
        if packed and not spaced:
            assert encoding.packed_size(value) == len(actual)
            out = bytearray(len(actual))
            encoding.write_packed(value, out)
            assert bytes(out) == actual
    for value in (0.0, -0.0, 1.25, Choice.VALUE):
        for spaced in (False, True):
            assert emitted(old, value, False, spaced) == emitted(encoding, value, False, spaced)
            comparisons += 1
        refused(lambda: encoding.pack(value))
    for code in range(65536):
        value = chr(code)
        raw = encoding.pack(value)
        assert raw == old.pack(value)
        assert json.loads(raw.decode('utf-8', 'surrogatepass')) == ['str', value]
    for high, low in product(range(0xd800, 0xdc00), (0xdc00, 0xde00, 0xdfff)):
        units = chr(high)+chr(low)
        scalar = chr(0x10000+((high-0xd800) << 10)+(low-0xdc00))
        assert encoding.pack(units) != encoding.pack(scalar)
    for value in (float('nan'), float('inf'), object(), Record):
        refused(lambda: emitted(encoding, value, False, False))
    cyclic_list, cyclic_mapping = [], {}
    cyclic_list.append(cyclic_list)
    cyclic_mapping['self'] = cyclic_mapping
    cyclic_record = Record('self', None)
    object.__setattr__(cyclic_record, 'value', cyclic_record)
    for value, packed in product((cyclic_list, cyclic_mapping, cyclic_record), (False, True)):
        refused(lambda: emitted(encoding, value, packed, False))
    shared = Record('shared', (1, 2))
    assert encoding.pack((shared, shared)) == old.pack((shared, shared))
    deep = 0
    for _ in range(65):
        deep = (deep,)
    refused(lambda: encoding.bounded_packed_size(deep, byte_limit=100000))
    refused(lambda: encoding.bounded_packed_size(1 << 32768, byte_limit=100000))
    refused(lambda: encoding.bounded_packed_size(tuple(range(100)), byte_limit=64))
    # Fragment counts are deterministic work diagnostics, not timings or a
    # complete interpreter-memory model. Same repeated rational payload, with
    # increasing nesting, reveals recursive fragment propagation overhead.
    shape = tuple(F(1, 50257) for _ in range(4096))
    for _ in range(8):
        shape = Record('layer', (shape,))
    before = tuple(old.fragments(shape, packed=True))
    after = tuple(encoding.fragments(shape, packed=True))
    assert ''.join(before) == ''.join(after)
    return dict(status='PASS_EXACT_STREAMED_CANONICAL_ENCODING', previous_source=PREVIOUS,
        typed_mode_comparisons=comparisons, compared_bytes=expanded,
        BMP_codepoints=65536, surrogate_pair_classes=3072,
        cyclic_container_refusals=6, repeated_acyclic_objects_preserved=True,
        whole_records_and_identity_bytes_unchanged=True, previous_traversal_refusals_preserved=True,
        repeated_rational_fragments=dict(previous=len(before), current=len(after)),
        scope='canonical byte equality and bounded traversal; no CUDA or model result')


def identities():
    from audit_owned_encoding import source_case
    from fp_reference import runtime
    from fp_reference.ingress import encode_context
    from fp_reference.program import Program
    rt, (first, second) = source_case(runtime)
    initial = rt.snapshot()
    assert first.program_id != second.program_id
    built = rt.construct_candidate(second)
    assert built.status == 'BUILT_REFERENCE'
    prediction = rt.predict_next('observation-0', encode_context((1, 0)))
    values = dict(prediction.predictions)
    assert values[initial.deployed_id][0] == F(2, 3)
    assert values[built.candidate_id][0] == F(1, 2)
    with patch.object(Program, 'program_id', property(lambda self: 'forced-collision-address')):
        rt, (first, second) = source_case(runtime)
        before = rt.snapshot()
        refused_candidate = rt.construct_candidate(second)
        after = rt.snapshot()
        assert refused_candidate.status == 'UNRESOLVED' and refused_candidate.candidate_id is None
        assert 'collision' in refused_candidate.reason
        assert after.candidates == before.candidates and after.programs == before.programs
        assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
        prediction = rt.predict_next('observation-0', encode_context((1, 0)))
        assert dict(prediction.predictions)[before.deployed_id][0] == F(2, 3)
    return dict(distinct_source_predictions_preserved=True, forced_collision_refuses_without_code_replacement=True)


def profile_native():
    from audit_shared_cuda_retention import full_registration
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.ingress import encode_context
    cc, program, online, _, storage, _, _, targets, _ = full_registration()
    profiler = cProfile.Profile()
    started = time.perf_counter()
    profiler.enable()
    rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage)
    forecast = rt.predict_next('train/0', encode_context(()))
    assert forecast.status == 'PREDICTED_REFERENCE', forecast.reason
    result = rt.observe(targets[0])
    assert result.status == 'OBSERVED_REFERENCE', result.reason
    profiler.disable()
    assert 'torch' not in sys.modules
    stats = pstats.Stats(profiler)
    return dict(case='initialization-and-one-full-vocabulary-native-event',
        profiled_seconds=time.perf_counter()-started, calls=stats.total_calls,
        primitive_calls=stats.prim_calls,
        scope='cProfile CPU diagnostic, not uninstrumented latency or GPU throughput')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--profile-native', action='store_true')
    args = parser.parse_args()
    result = audit()
    result['runtime_identity'] = identities()
    if args.profile_native:
        result['native_profile'] = profile_native()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_STREAMED_ENCODING_CPU.json').write_text(body, encoding='utf-8')
    print(body)


if __name__ == '__main__':
    main()
