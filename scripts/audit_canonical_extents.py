"""Exact grammar/guard and complete Runtime controls for direct extents.

The old calculator comes from committed canonical source. No corpus, CUDA,
timing estimate, serialization change or new certificate class is used.
"""
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import MappingProxyType, ModuleType
from unittest.mock import patch
import argparse
import cProfile
import json
import pstats
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded

PREVIOUS = '075eba1da7493582665b8801a61430ac02876be6'


@dataclass(frozen=True)
class Record:
    label: str
    value: object


@dataclass(frozen=True)
class Empty:
    pass


def previous(source=None):
    path = 'src/reference_compiler/fp_reference/encoding.py'
    if source is None:
        source = subprocess.check_output(['git', 'show', PREVIOUS+':'+path], cwd=ROOT, encoding='utf-8')
    module = ModuleType('fp_reference._extent_predecessor')
    module.__package__ = 'fp_reference'
    exec(compile(source, 'git:'+PREVIOUS+':'+path, 'exec'), module.__dict__)
    return module


def outcome(call):
    try:
        return ('VALUE', call())
    except (ContractError, ResourceExceeded) as error:
        return type(error).__name__, str(error)


def grammar(old):
    atoms = (None, True, False, -17, 0, 17, 1 << 129, F(-1, 7), F(1, 1 << 129),
             '', 'ascii "\\', '\x00\x7f\ud800\U0001f600', b'', bytes(range(256)))
    values = list(atoms)
    values += [row for row in product(atoms, repeat=2)]
    values += [list(row) for row in product(atoms[:8], repeat=2)]
    values += [Record('label', row) for row in product(atoms[:8], repeat=2)]
    values += [dict(zip(('a', 'b'), row)) for row in product(atoms[:8], repeat=2)]
    values += [MappingProxyType({'a': (1, F(2, 3)), 'b': [None, True]}),
               {F(-1, 3): Record('typed', atoms), '\ud83d\ude00': 1, '\U0001f600': 2},
               b'\0\xff'*(1 << 17), 'plain "\\'*1024,
               ''.join(chr(i) for i in range(65536)), -(1 << 32767), (), [], {}, Empty()]
    checks = compared = 0
    for value in values:
        raw = old.pack(value)
        assert encoding.packed_size(value) == old.packed_size(value) == len(raw)
        assert encoding.pack(value) == raw
        compared += len(raw)
        checks += 1
    # Every ASCII byte, every printable pair, and all BMP code points also
    # exercise scalar string sizing directly against the original rule.
    strings = [chr(i) for i in range(65536)]
    strings += [''.join(row) for row in product(map(chr, range(32, 127)), repeat=2)]
    strings += ['a'*255+'\ud800\U0001f600'+'"\\\n'*257, '\ud83d\ude00', '\U0001f600']
    for value in strings:
        assert encoding._string_size(value) == old._string_size(value)
    return dict(values=checks, packed_bytes_compared=compared, string_cases=len(strings)), atoms


def guards(old, atoms):
    checks = 0
    values = (*atoms, (), [], {}, Empty(), Record('x', (1, F(1, 3))),
              MappingProxyType({'x': [0, '\x00\x7f']}), tuple(range(65)))
    for value in values:
        size = old.packed_size(value)
        for cap, depth, bits in product((1, 2, 8, max(1, size-1), size, size+1),
                                         (1, 2, 4, 64), (1, 4, 128, 129, 32768)):
            args = dict(byte_limit=cap, depth_limit=depth, integer_bits=bits)
            assert outcome(lambda: encoding.bounded_packed_size(value, **args)) == outcome(
                lambda: old.bounded_packed_size(value, **args))
            checks += 1
    cycle = []
    cycle.append(cycle)
    malformed = ((0, object()), float('nan'), Record, cycle, [0, (1 << 32768)])
    for value, cap in product(malformed, (8, 100000)):
        args = dict(byte_limit=cap)
        assert outcome(lambda: encoding.bounded_packed_size(value, **args)) == outcome(
            lambda: old.bounded_packed_size(value, **args))
        checks += 1
    # Eagerly stopping on encoded extent would change this original refusal:
    # encoding just the first integer already exceeds 8, yet the guard must
    # visit the unsupported next value before its final extent decision.
    witness = outcome(lambda: encoding.bounded_packed_size((0, object()), byte_limit=8))
    assert witness == ('ContractError', 'unsupported packed reference payload')
    return dict(decisions=checks, eager_extent_refusal_counterexample=witness)


def observations(old):
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
        row = (1, F(2, 3))  # Stable answers isolate reads from allocation IDs.
        def __iter__(self):
            log.append(('keys',))
            return iter(('x', 'y'))
        def __getitem__(self, key):
            log.append(('item', key))
            return 0 if key == 'x' else self.row
        def __len__(self):
            log.append(('length',))
            return 2
    class Misses:
        def find(self, value):
            log.append(('image', id(value)))
    values = (Observed(Ordered(), [0, 1]), Ordered(), [Observed(1, 2), Observed(3, 4)])
    for value, bounded, images in product(values, (False, True), (None, Misses())):
        result = []
        for writer in (old, encoding):
            log.clear()
            size = (writer.bounded_packed_size(value, byte_limit=100000, images=images)
                    if bounded else writer.packed_size(value, images=images))
            result.append((size, tuple(log)))
        assert result[0] == result[1], (type(value).__name__, bounded, images is not None, result)
    return dict(ordered_field_mapping_and_image_walks=12)


@contextmanager
def previous_calculator(old):
    current = encoding.packed_size
    def replace_aliases(source, target):
        for name, module in tuple(sys.modules.items()):
            if name.startswith('fp_reference.') and module is not None:
                for attribute, value in tuple(vars(module).items()):
                    if value is source:
                        setattr(module, attribute, target)
    replace_aliases(current, old.packed_size)
    try:
        yield
    finally:
        # Include modules first imported during this control, so no old
        # calculator can leak into the following current Runtime arm.
        replace_aliases(old.packed_size, current)


def runtime_controls(old):
    from contextlib import nullcontext
    import audit_owned_token_workspaces as owned
    cases = [((0, 1, 1, 0), unit, False, False, False) for unit in (1, 2, 4)]
    cases += [((0, 1, 1, 0)*2, 8, False, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False, False),
              ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = retained = words = raw_calls = raw_bytes = 0
    for word, unit, profile, combined, archived in cases:
        rows = []
        for legacy in (True, False):
            with (previous_calculator(old) if legacy else nullcontext()), \
                    patch.object(owned, 'numerical_phase', encoding.pack):
                rows.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert rows[0] == rows[1]
        phases += len(rows[0]['phases'])
        retained += sum(map(len, rows[0]['phases']))
        words += rows[0]['primitive_words']
        raw_calls += rows[0]['raw_calls']
        raw_bytes += rows[0]['raw_bytes']
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        complete_phase_bytes=retained, checked_primitive_words=words,
        identical_raw_calls=raw_calls, identical_raw_bytes=raw_bytes,
        full_frames_learners_reports_allocations_and_retirements_equal=True)


def call_counts(old):
    value = Record('ordinary', tuple(F(i, 7) for i in range(512)))
    results = []
    for writer in (old, encoding):
        profiler = cProfile.Profile()
        size = profiler.runcall(writer.packed_size, value)
        stats = pstats.Stats(profiler)
        calls = sum(v[1] for k, v in stats.stats.items() if k[2] == 'packed_size')
        results.append(dict(size=size, visited_occurrences=calls, total_calls=stats.total_calls))
    assert results[0]['size'] == results[1]['size']
    assert results[0]['visited_occurrences'] == results[1]['visited_occurrences']
    assert results[1]['total_calls'] < results[0]['total_calls']
    return dict(previous=results[0], direct=results[1], scope='deterministic toy call counts; no timing claim')


def audit():
    old = previous()
    component, atoms = grammar(old)
    result = dict(grammar=component, guards=guards(old, atoms), observations=observations(old),
                  calls=call_counts(old))
    print('PASS exact grammar, guarded decisions and observation order', flush=True)
    result['runtime'] = runtime_controls(old)
    from audit_canonical_images import component as images, failures
    result['owned_images'], result['image_failures'] = images(), failures()
    import torch
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_DIRECT_CANONICAL_EXTENTS_CPU', previous_source=PREVIOUS,
                scope=__doc__.strip(), **result)


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('exact extent audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_DIRECT_CANONICAL_EXTENTS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
