"""Captured prediction values at complete storage, feature and failure boundaries.

Exact CPU controls only. Existing optional formats are checked for lossless
compatibility; this is not a new format, cost experiment or CUDA release.
"""
from contextlib import nullcontext
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from fp_reference import ReferenceCompilerRuntime, encoding, phase_encoding
from fp_reference.core import ContractError
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded
from fp_reference.token_values import CapturedTokenValues as Captured
from captured_values_audit_support import SOURCE, literal_predictions
from audit_owned_token_learner import fixture, registration, compare, live
from audit_reference_construction import validate_residency
from audit_shared_token_retention import STORAGE


def outcome(call):
    try:
        return 'VALUE', call()
    except (ContractError, ResourceExceeded) as error:
        return type(error).__name__, str(error)


def phase_formats():
    vectors = decisions = encoded = expanded = 0
    raw = struct.pack('<4I', 0, 1, 7, (1 << 32)-1)
    for length, tail in product((0, 1, 7, 8, 16, 512), ((), (F(-3, 7),))):
        value = Captured(raw, 2, tuple(i % 2 for i in range(length)), 16, tail)
        literal = tuple(value)
        extent = phase_encoding.extent(literal, encoded_cap=1 << 20)
        outputs = []
        for subject in (literal, value):
            output = bytearray(extent.encoded_bytes)
            assert phase_encoding.write(subject, output) == extent
            outputs.append(bytes(output))
        assert outputs[0] == outputs[1]
        complete = b''.join(phase_encoding.decoded_fragments(outputs[1]))
        assert complete == encoding.pack(literal)
        assert phase_encoding.check(outputs[1], value) == extent.expanded_bytes
        for cap, full in product((1, max(1, extent.encoded_bytes-1), extent.encoded_bytes),
                                 (1, max(1, extent.expanded_bytes-1), extent.expanded_bytes)):
            assert outcome(lambda: phase_encoding.extent(value, encoded_cap=cap, expanded_cap=full)) == outcome(
                lambda: phase_encoding.extent(literal, encoded_cap=cap, expanded_cap=full))
            decisions += 1
        vectors += 1
        encoded += len(outputs[1])
        expanded += len(complete)
    return dict(vectors=vectors, paired_cap_decisions=decisions, encoded_bytes=encoded,
        independent_complete_decoded_bytes=expanded, existing_format_bytes_unchanged=True)


def archive_boundaries():
    import audit_canonical_images as images
    import audit_compositional_reference as expressions
    value = Captured(struct.pack('<4I', 0, 1, 7, 65535), 2, (0, 1)*256, 16, (F(3, 7),))
    literal = tuple(value)
    raw = encoding.pack(literal)
    rt = images.root()
    snap, identity, actual = images.retain(rt, value, 'captured')
    assert actual == raw
    cache = rt._reference_archive.images
    entry = cache.find(value)
    assert entry is not None and entry.source is value
    assert cache._metrics(value, {}) == cache._metrics(literal, {})
    public = next(e for e in snap.reference_archive.canonical_images if e.buffer == entry.buffer)
    assert type(public.source) is tuple and public.source == literal
    public.__dict__.update(source=(F(99),), size=1, buffer='forged')
    assert cache.find(value) is entry and entry.source is value
    images.retain(rt, value, 'after-public-write')
    checked = 0
    for byte_cap, depth, bits in product((1, len(raw)-1, len(raw), len(raw)+1), (1, 2), (1, 16, 32)):
        options = dict(byte_limit=byte_cap, depth_limit=depth, integer_bits=bits)
        assert outcome(lambda: encoding.bounded_packed_size(value, images=cache, **options)) == outcome(
            lambda: encoding.bounded_packed_size(literal, **options))
        checked += 1
    expr = expressions.root()
    previous = set(expr._reference_archive.bindings)
    key = expressions.retain(expr, value, 'captured')
    bindings = expr._reference_archive.bindings
    assert bindings[id(value)][0] is value
    introduced = [bindings[key][0] for key in bindings.keys()-previous]
    assert introduced == [value]
    assert not any(type(v) is F for v in introduced)
    snapshot = validate_residency(expr)
    assert expressions.decode(snapshot, key) == raw
    exported = [v for v, _ in snapshot.reference_archive.expression_bindings if v == literal]
    assert len(exported) == 1 and type(exported[0]) is tuple
    before = len(bindings)
    again = expressions.retain(expr, value, 'second-captured')
    assert len(expr._reference_archive.bindings) == before
    assert expressions.decode(validate_residency(expr), again) == raw
    # The initial image binding still compares every byte with the source.
    failed = images.root()
    original = encoding.write_packed
    def wrong(subject, output):
        original(subject, output)
        output[-1] ^= 1
    with patch.object(encoding, 'write_packed', wrong):
        assert outcome(lambda: images.retain(failed, value, 'wrong-image'))[0] == 'ContractError'
    failed_snapshot = validate_residency(failed)
    assert failed_snapshot.halted and failed._reference_archive.images.find(value) is None
    assert any(row['kind'] == 'immutable_canonical_image' for row in failed_snapshot.resources['objects'].values())
    # Even a forged physical tuple cannot bind mutable descendants as pure.
    forged = tuple.__new__(Captured, (bytearray(4), 1, (0,), 16, ()))
    refusals = []
    for name, module in (('canonical-image', images), ('expression', expressions)):
        target = module.root()
        assert outcome(lambda: module.retain(target, forged, 'forged'))[0] == 'ContractError'
        assert target.snapshot().halted
        refusals.append(name)
    return dict(complete_bytes_per_archive= len(raw), canonical_guard_pairs=checked,
        public_image_and_binding_sources_are_detached_tuples=True,
        wrong_image_refused_with_paid_prefix_retained=True, malformed_capture_refusals=refusals,
        expression_new_bindings=1, expression_retained_decoded_fraction_bindings=0,
        repeated_capture_uses_original_complete_binding=True)


def allocation_failures():
    cases = []
    for mode in ('pre-target-capture', 'pre-target-tail', 'post-target-capture', 'post-target-tail',
                 'diagnostic-decode'):
        d, initial = fixture(2, 'mixed')
        cc, program, online = registration(d, initial)
        rt = ReferenceCompilerRuntime(cc, program, online=online)
        if mode.startswith('post-target') or mode == 'diagnostic-decode':
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        if mode == 'diagnostic-decode':
            assert rt.observe(1).status == 'OBSERVED_REFERENCE'
        before = rt.snapshot()
        method = '__iter__' if mode == 'diagnostic-decode' else 'with_tail' if mode.endswith('tail') else '__new__'
        with patch.object(Captured, method, side_effect=MemoryError('fixed capture allocation refusal')) as fault:
            try:
                if mode.startswith('pre-target'):
                    rt.predict_next('train/0', encode_context(()))
                elif mode.startswith('post-target'):
                    rt.observe(1)
                else:
                    rt.snapshot()
            except MemoryError:
                pass
            else:
                raise AssertionError('host allocation failure did not escape')
            assert fault.call_count == 1
        after = validate_residency(rt)
        assert after.halted == HOST_ALLOCATION_FAILURE and after.event_phase == 'halted'
        assert after.candidates == before.candidates and after.cursor == before.cursor
        assert after.resources['spent']['compiler']['work'] >= before.resources['spent']['compiler']['work']
        if mode.startswith('post-target'):
            assert after.observations[-1].target == 1 and after.cursor == 0
        elif mode.startswith('pre-target'):
            assert not any(record.target is not None for record in after.observations)
        else:
            assert after.observations == before.observations and after.event_traces == before.event_traces
        assert outcome(lambda: rt.predict_next('train/1', encode_context(())))[0] == 'ContractError'
        assert rt.snapshot() == after
        cases.append(mode)
    return dict(terminal_host_failure_sites=cases, actual_prefix_and_spent_work_retained=True,
        failed_operations_never_publish_a_successor_or_refund=True)


def input_features():
    histories = events = gradients = 0
    for layout, unit, shared, kind, word in product(((0, 1, 0, 6, 8, 11, 0), (0, 1, 2, 3, 4, 5, 0)),
            (1, 2, 4), (False, True), ('mixed', 'zero-embedding'), ((0, 0, 0, 0), (0, 1, 1, 0))):
        answers = []
        for old in (True, False):
            with (literal_predictions() if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='captured-input-features'):
                d, exact = fixture(unit, kind)
                d = replace(d, features=layout)
                exact = replace(exact, definition=d)
                cc, program, online = registration(d, exact)
                rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE if shared else None)
                outputs = []
                for index, target in enumerate(word):
                    expected = exact.predict()
                    outputs.append(rt.predict_next(f'train/{index}', encode_context(())))
                    assert outputs[-1].status == 'PREDICTED_REFERENCE'
                    if not old:
                        prediction = rt._pending.predictions[0][1]
                        assert type(prediction.values) is Captured
                        assert tuple(prediction.values) == expected.values
                        features = prediction.probabilities.features
                        assert features[0] is features[-1]
                        selected = {layout[i]: value for i, value in enumerate(features) if layout[i] < d.input_nodes}
                        assert len({id(value) for value in selected.values()}) == len(selected)
                    outputs.append(rt.observe(target))
                    assert outputs[-1].status == 'OBSERVED_REFERENCE'
                    exact = exact.observe(expected, target)
                    snapshot = validate_residency(rt)
                    gradients += compare(snapshot.event_traces[-1].after_observe, exact)
                    if (index+1) % unit == 0:
                        exact = exact.commit()
                    compare(live(snapshot), exact)
                answers.append(encoding.pack((tuple(outputs), snapshot)))
        assert answers[0] == answers[1]
        histories += 1
        events += len(word)
    return dict(paired_complete_histories=histories, targets_per_arm=events,
        exact_pending_gradient_coordinates_both_arms=gradients,
        distinct_input_coordinates_not_merged=True, repeated_feature_identity_preserved=True,
        complete_results_snapshots_and_grid_masters_equal=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    result = dict(status='PASS_CAPTURED_VALUE_BOUNDARIES_CPU', literal_source=SOURCE)
    for name, function in (('phase_formats', phase_formats), ('archives', archive_boundaries),
                           ('allocation_failures', allocation_failures), ('input_features', input_features)):
        result[name] = function()
        print('PASS '+name, flush=True)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
