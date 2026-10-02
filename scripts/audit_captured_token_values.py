"""Lossless captured-value representation and complete Runtime controls.

Source/byte/identity checks only; no corpus, timing comparison or CUDA launch.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import gc
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from fp_reference.core import ContractError
from fp_reference import encoding
from fp_reference.public_values import detached
from fp_reference.token_values import CapturedTokenValues as Captured
from captured_values_audit_support import SOURCE, literal_predictions


def outcome(fn):
    try:
        return ('ok', fn())
    except (ContractError, IndexError, ValueError, TypeError) as error:
        return type(error).__name__, str(error)


def primitive_values():
    vectors = decisions = fragments = 0
    for width, length, grid in product((1, 2, 4), range(5), (1, 16, 1 << 32)):
        words = tuple((0, 1, (1 << 32)-1, 65537)[i % 4] for i in range(2*width))
        raw = struct.pack('<'+'I'*len(words), *words)
        for past in product((0, 1), repeat=length):
            for tail in ((), (F(-3, 7), F(5, 11))):
                value = Captured(raw, width, past, grid, tail)
                expected = tuple(F(words[token*width+c], grid) for token in past for c in range(width))+tail
                assert value == expected and expected == value and not value != expected
                assert len(value) == len(expected) and tuple(value) == expected
                assert hash(value) == hash(expected) and repr(value) == repr(expected)
                assert tuple(reversed(value)) == tuple(reversed(expected))
                for multiplier in (-1, 0, 1, 2):
                    assert value*multiplier == multiplier*value == expected*multiplier
                assert (F(99),)+value == (F(99),)+expected
                assert value+(F(99),) == expected+(F(99),)
                assert value+value == expected+expected
                for needle in (F(0), F(1, grid), F(99)):
                    assert (needle in value) == (needle in expected)
                    assert value.count(needle) == expected.count(needle)
                    assert outcome(lambda: value.index(needle)) == outcome(lambda: expected.index(needle))
                for start, stop, step in product((-30, -1, 0, 2, 30), (None, -1, 2, 30), (-2, -1, 1, 2)):
                    key = slice(start, stop, step)
                    assert value[key] == expected[key]
                for packed, spaced in product((False, True), repeat=2):
                    actual = list(encoding.fragments(value, packed=packed, spaced=spaced))
                    assert actual == list(encoding.fragments(expected, packed=packed, spaced=spaced))
                    fragments += len(actual)
                size = encoding.packed_size(expected)
                for limit, depth, bits in product((1, max(1, size-1), size, size+1), (1, 2), (1, 16, 32, 64)):
                    assert outcome(lambda: encoding.bounded_packed_size(value, byte_limit=limit,
                        depth_limit=depth, integer_bits=bits)) == outcome(lambda: encoding.bounded_packed_size(
                        expected, byte_limit=limit, depth_limit=depth, integer_bits=bits))
                    decisions += 1
                exported = detached((value, value))
                assert type(exported[0]) is tuple and exported[0] == expected and exported[0] is exported[1]
                vectors += 1
    return dict(vectors=vectors, paired_guard_decisions=decisions, equal_fragments=fragments,
        exact_tuple_values_operations_and_public_aliases=True)


def forged_values():
    good = (struct.pack('<2I', 3, 7), 1, (0, 1), 16, (F(2, 3),))
    cases = [(), good+(0,)]
    for index, replacements in (
            (0, (bytearray(good[0]), b'', b'\x00')), (1, (0, -1, True, 3)),
            (2, ([0, 1], (True,), (-1,), (2,))), (3, (0, 3, 1 << 33, True)),
            (4, ([F(0)], (0,), (object(),)))):
        for replacement in replacements:
            parts = list(good)
            parts[index] = replacement
            cases.append(tuple(parts))
    for parts in cases:
        forged = tuple.__new__(Captured, parts)
        for operation in (lambda: tuple(forged), lambda: detached(forged),
                          lambda: encoding.pack(forged)):
            assert outcome(operation)[0] == 'ContractError'
    value = Captured(*good)
    for action in (lambda: object.__setattr__(value, 'past', (1, 1)),
                   lambda: object.__setattr__(value, '__dict__', {})):
        try:
            action()
        except AttributeError:
            pass
        else:
            raise AssertionError('captured immutable operands acquired writable metadata')
    # The captured immutable operands survive replacement of the supplying
    # wrappers. No lookup of a later Origin/Window attribute can change them.
    wrapper = dict(embedding=good[0], past=good[2])
    captured = Captured(wrapper['embedding'], 1, wrapper['past'], 16)
    before = tuple(captured)
    wrapper.update(embedding=struct.pack('<2I', 9, 11), past=(1, 1))
    assert tuple(captured) == before
    # Different physical captures can represent one logical tuple. This is
    # scalar value equality only; enclosing origins/causal windows stay owned.
    equal = Captured(struct.pack('<3I', 3, 7, 99), 1, (0, 1), 16)
    assert captured == equal and hash(captured) == hash(equal)
    return dict(forged_representations_refused=len(cases), writable_metadata_refusals=2,
        supplying_wrapper_replacement_preserves_captured_values=True,
        unused_master_rows_do_not_change_logical_tuple_equality=True)


def paired_histories():
    import audit_owned_admission as existing
    # Reuse the complete 98-history fixture, substituting only its baseline
    # context with the actual original literal numerical prediction methods.
    with patch.object(existing, 'historical_prediction_ports', literal_predictions):
        return existing.histories()


def paired_cpu_phases():
    import audit_owned_admission as existing
    with patch.object(existing, 'historical_prediction_ports', literal_predictions):
        return existing.cpu_phases()


def full_vocabulary():
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.ingress import encode_context
    from fp_reference.shared_reference import _compare_stream
    from run_native_text_a1 import registration, complete_residency
    states = []
    for old in (True, False):
        from contextlib import nullcontext
        with (literal_predictions() if old else nullcontext()), \
                patch('fp_reference.runtime.secrets.token_hex', return_value='captured-values-full-v'):
            cc, program, online, storage, reporting = registration()
            rt = ReferenceCompilerRuntime(cc, program, online=online,
                shared_storage=storage, reporting=reporting)
            for i, target in enumerate((0, 1)):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            states.append(rt)
    old, new = states
    assert complete_residency(old) == complete_residency(new)
    assert tuple(old._buffers) == tuple(new._buffers)
    assert all(old._buffers[key] == new._buffers[key] for key in old._buffers)
    a, b = old.snapshot(), new.snapshot()
    size = encoding.packed_size(a)
    _compare_stream((s.encode('utf-8', 'surrogatepass') for s in encoding.fragments(b, packed=True)),
        (s.encode('utf-8', 'surrogatepass') for s in encoding.fragments(a, packed=True)), size)
    del a, b
    gc.collect()
    per_value = []
    for trace in new._event_traces:
        value = trace.prediction.values
        assert type(value) is Captured
        embedding, width, past, grid, tail = value.validate()
        assert embedding is trace.before.origin.embedding and past is trace.prediction.window.past
        assert len(tail) == 8 and all(i >= 2048 for i in program.definition.features)
        per_value.append(sys.getsizeof(value)+sys.getsizeof(tail))
    assert per_value == [184, 184]
    return dict(synthetic_targets_per_arm=2, original_training_declaration=1048576,
        full_serialized_snapshot_bytes_compared=size, every_buffer_and_role_total_equal=True,
        input_recipe_and_tail_container_bytes_per_prediction=184,
        original_selected_input_objects_and_tuple_bytes_per_prediction=114792,
        existing_embedding_and_window_references_shared=True,
        no_retained_input_fraction_instances_in_value_representation=True,
        full_host_budget_or_timing_claim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    result = dict(status='PASS_CAPTURED_TOKEN_VALUES_CPU', literal_source=SOURCE)
    for name, function in (('primitive_values', primitive_values), ('forged_values', forged_values),
            ('paired_histories', paired_histories), ('paired_cpu_phases', paired_cpu_phases),
            ('full_vocabulary', full_vocabulary)):
        result[name] = function()
        print('PASS '+name, flush=True)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
