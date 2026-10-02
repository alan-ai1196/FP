"""Exact traces and owned CPU controls for source-compiled canonical streams.

No corpus, GPU, performance estimate or production backend authority.
The compiled components consume the same authored canonical algorithms.
"""
from collections.abc import Mapping
from contextlib import nullcontext
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import encoding, shared_reference
from native_stream_audit_support import load, compiled_controls


@dataclass(frozen=True)
class Record:
    name: str
    value: object


class Choice(Enum):
    VALUE = ('a', F(2, 3))


def consume(iterator):
    values = []
    try:
        values.extend(iterator)
        return values, None
    except Exception as error:
        return values, (type(error).__name__, str(error))


def grammar(compiled):
    atoms = (None, False, True, -17, 0, 17, F(-2, 3), F(1, 7), '', '\\"\n',
             '\x7f\ud800', '\U0001f600', '\ud83d\ude00', b'', bytes(range(256)))
    values = list(atoms)+list(product(atoms[:8], repeat=3))
    values += [list(atoms), Record('typed', atoms),
        {'\ud83d\ude00': 1, '\U0001f600': 2, F(-1, 3): Record('x', (1, 2)), (3, 'x'): False},
        b'\0\xff'*513, 'a'*255+'\ud800\U0001f600'+'"\\\n'*257,
        -(1 << 32767), F(1, 1 << 32767), Choice.VALUE, 0.0, -0.0, 1.25,
        float('nan'), float('inf'), object(), Record]
    cyclic_list, cyclic_map = [], {}
    cyclic_list.append(cyclic_list)
    cyclic_map['self'] = cyclic_map
    record = Record('self', None)
    object.__setattr__(record, 'value', record)
    values += [cyclic_list, cyclic_map, record]
    shared = Record('shared', (1, 2))
    values.append((shared, shared))
    checks = fragments = compared = 0
    for value, packed, spaced in product(values, (False, True), (False, True)):
        a = consume(encoding.fragments(value, packed=packed, spaced=spaced))
        b = consume(compiled.fragments(value, packed=packed, spaced=spaced))
        assert a == b, (type(value), packed, spaced, a[1], b[1])
        checks += 1
        fragments += len(a[0])
        compared += sum(len(s.encode('utf-8', 'surrogatepass')) for s in a[0])
    for code in range(65536):
        value = chr(code)
        assert tuple(encoding.fragments(value, packed=True)) == tuple(compiled.fragments(value, packed=True))
    for high, low in product(range(0xd800, 0xdc00), (0xdc00, 0xde00, 0xdfff)):
        units = chr(high)+chr(low)
        scalar = chr(0x10000+((high-0xd800) << 10)+(low-0xdc00))
        for value in (units, scalar):
            assert tuple(encoding.fragments(value, packed=True)) == tuple(compiled.fragments(value, packed=True))
    return dict(typed_mode_cases=checks, exact_fragments=fragments, complete_bytes=compared,
        BMP_codepoints=65536, surrogate_pair_classes=3072,
        cyclic_foreign_nonfinite_and_packed_float_enum_refusals_equal=True)


def observations(compiled):
    log = []
    @dataclass
    class Observed:
        a: object
        b: object
        def __getattribute__(self, name):
            if name in ('a', 'b'):
                log.append(('field', name))
            return object.__getattribute__(self, name)
    class Ordered(Mapping):
        def __iter__(self):
            log.append(('keys',))
            return iter(('y', 'x'))
        def __getitem__(self, key):
            log.append(('item', key))
            return 0 if key == 'x' else (1, F(2, 3))
        def __len__(self):
            log.append(('length',))
            return 2
    class Images:
        def find(self, value):
            log.append(('image', type(value).__name__))
            return 'hit' if value == b'image' else None
        def fragments(self, entry):
            assert entry == 'hit'
            log.append(('image-read',))
            yield from encoding.fragments(b'image', packed=True)
    count = 0
    for packed, spaced, use_images, mutate in product((False, True), repeat=4):
        answers = []
        for writer in (encoding, compiled):
            log.clear()
            value = Observed(Ordered(), [b'image', 'a'*257+'\ud800', 3])
            trace = []
            for fragment in writer.fragments(value, packed=packed, spaced=spaced,
                                              images=Images() if use_images else None):
                trace.append((fragment, tuple(log)))
                if mutate and len(trace) == 15:
                    value.b.append(4)
            answers.append(trace)
        assert answers[0] == answers[1], (packed, spaced, use_images, mutate)
        count += 1
    return dict(yield_by_yield_field_mapping_image_and_mutation_traces=count)


def partitions(raw):
    if not raw:
        return [(), (b'',)]
    result = []
    for mask in range(1 << (len(raw)-1)):
        start, parts = 0, []
        for index in range(1, len(raw)):
            if mask & (1 << (index-1)):
                parts.append(raw[start:index]); start = index
        parts.append(raw[start:])
        result.append(tuple(parts))
    return result


def consumers(compiled):
    values = [Record('nested', tuple(F(i, 7) for i in range(512))),
        {'a': b'\0\xff'*8193, 'b': 'x'*255+'\ud800\U0001f600'}, (), None]
    piece_count = byte_count = 0
    for value, extent in product(values, (256, 257, 8192)):
        a = tuple(shared_reference._packed_parts(value, bytearray(extent)))
        b = tuple(compiled._packed_parts(value, bytearray(extent)))
        assert a == b and b''.join(a) == encoding.pack(value)
        piece_count += len(a); byte_count += sum(map(len, a))
    decisions = 0
    def result(fn, actual, expected, size):
        log = []
        def emit(parts, label):
            for p in parts:
                log.append((label, p))
                yield p
            log.append((label, 'exhausted'))
        try:
            value = fn(emit(actual, 'actual'), emit(expected, 'expected'), size)
            answer = ('OK', value)
        except Exception as error:
            answer = (type(error).__name__, str(error))
        return answer, log
    for length in range(5):
        for word in product((0, 255), repeat=length):
            raw = bytes(word)
            for actual, expected in product(partitions(raw), repeat=2):
                for altered, size in ((expected, len(raw)), ((b'',)+expected+(b'',), len(raw)),
                    (expected+(b'x',), len(raw)), (expected, len(raw)+1),
                    ((b'x',)+expected, len(raw))):
                    a = result(shared_reference._compare_stream, actual, altered, size)
                    b = result(compiled._compare_stream, actual, altered, size)
                    assert a == b
                    decisions += 1
    return dict(producer_pieces=piece_count, producer_bytes=byte_count,
        partition_corruption_and_iterator_read_decisions=decisions,
        producer_piece_boundaries_and_independent_reader_refusals_equal=True)


def runtime(encoder, consumers):
    from fp_reference.ingress import encode_context
    from audit_token_reporting import report_registration
    from audit_shared_token_retention import STORAGE
    from audit_reference_construction import validate_residency
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.shared_reference import decoded_buffer
    checked = records = bytes_checked = 0
    for word in product((0, 1), repeat=4):
        rows = []
        # Fix the existing root nonce solely to compare *all* retained bytes,
        # including IDs; these independent toy roots never exchange authority.
        for native in (False, True):
            with (compiled_controls(encoder, consumers) if native else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='native-stream-control'):
                cc, program, online, reporting = report_registration(count=4, report_count=3)
                rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting, shared_storage=STORAGE)
                for index, target in enumerate(word):
                    assert rt.predict_next(f'train/{index}', encode_context(())).status == 'PREDICTED_REFERENCE'
                    assert rt.observe(target).status == 'OBSERVED_REFERENCE'
                assert rt.begin_report().status == 'REPORTING'
                for index, target in enumerate((1, 0, 1)):
                    assert rt.predict_report(f'report/{index}').status == 'PREDICTED_REPORT'
                    assert rt.observe_report(target).status == ('COMPLETE_REPORT' if index == 2 else 'SCORED_REPORT')
                snapshot = validate_residency(rt)
                for label, raw in snapshot.buffers:
                    if snapshot.resources['objects'][label]['kind'].startswith('shared_reference_root:'):
                        decoded = b''.join(decoded_buffer(snapshot, label,
                            byte_cap=STORAGE.expanded_cap, reference_cap=STORAGE.reference_cap))
                        records += 1; bytes_checked += len(decoded)
                rows.append(encoding.pack(snapshot))
        assert rows[0] == rows[1]
        checked += 1
    return dict(paired_histories=checked, decoded_records=records, decoded_bytes=bytes_checked,
        complete_snapshots_learners_reports_pages_ledger_and_identity_bytes_equal=True)


def cpu_phases(encoder, consumers):
    import audit_owned_token_workspaces as owned
    cases = [((0, 1, 1, 0), unit, False, False, False) for unit in (1, 2, 4)]
    cases += [((0, 1, 1, 0)*2, 8, False, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False, False),
              ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = checked_bytes = words = 0
    for word, unit, profile, combined, archived in cases:
        answers = []
        for native in (False, True):
            with (compiled_controls(encoder, consumers) if native else nullcontext()), \
                    patch.object(owned, 'numerical_phase', encoding.pack):
                answers.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert answers[0] == answers[1]
        phases += len(answers[0]['phases'])
        checked_bytes += sum(map(len, answers[0]['phases']))
        words += answers[0]['primitive_words']
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        complete_phase_bytes=checked_bytes, checked_primitive_words=words,
        full_frames_learners_reports_raw_reads_allocations_retirements_equal=True,
        actual_cuda_execution=False)


def failures(encoder, consumers):
    from audit_shared_token_retention import failures as storage_failures
    from audit_canonical_images import failures as image_failures
    with compiled_controls(encoder, consumers):
        result = dict(storage=storage_failures(), images=image_failures())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    encoder, consumer, manifest = load()
    result = dict(status='PASS_NATIVE_STREAM_COMPONENTS_CPU', scope=__doc__.strip(), build=manifest)
    for name, action in (('grammar', lambda: grammar(encoder)), ('observations', lambda: observations(encoder)),
        ('consumers', lambda: consumers(consumer)), ('runtime', lambda: runtime(encoder, consumer)),
        ('cpu_phases', lambda: cpu_phases(encoder, consumer)), ('failures', lambda: failures(encoder, consumer))):
        result[name] = action()
        print('PASS '+name, flush=True)
    import torch
    assert not torch.cuda.is_initialized()
    if args.write:
        (ROOT/'evidence/minimal/FP_NATIVE_STREAM_COMPONENTS_CPU.json').write_text(
            json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    main()
