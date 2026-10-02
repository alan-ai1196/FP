"""Exact full-schedule expansion law for the native ordinary byte archive.

Counts complete stream bytes, not resident memory or elapsed time. Read-only
observers run around the real producer, decoder and expected traversal.
No corpus, numerical substitution, new codec or experiment replay.
"""
from collections import Counter
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, byte_archive, encoding, shared_reference
from fp_reference.ingress import encode_context
from fp_reference.token_batch import Origin
from fp_reference.token_execution import TokenState
from fp_reference.token_values import CapturedTokenValues
from audit_token_reporting import report_registration
from audit_shared_token_retention import STORAGE
from run_native_text_a1 import complete_residency


def schedule(targets, unit):
    assert type(targets) is int and targets >= 0 and type(unit) is int and unit > 0
    commits, remainder = divmod(targets, unit)
    return dict(origins=8*targets+5*commits,
        pending_windows=commits*(3*unit*unit+unit-2)+3*remainder*remainder-remainder,
        commits=commits)


def selected(value, definition):
    """Count occurrences in the serialized tree, deliberately not a heap set.

    Stop at an Origin after accounting for its disjoint array/base fields.
    Its definition/source have no TokenState, so this omits no pending window.
    All other fields retain the canonical traversal, including repeated aliases.
    """
    count = Counter()
    def visit(item):
        if type(item) is Origin:
            raw = (item.embedding, item.core, item.output)
            assert all(type(part) is bytes for part in raw)
            assert sum(map(len, raw)) == 4*definition.slot_count
            assert item.definition == definition
            count['origins'] += 1
            count['master_hex_bytes'] += 2*sum(map(len, raw))
            count['origin_base_bytes'] += encoding.packed_size(item.definition.output.base)
            return
        if type(item) is TokenState:
            count['pending_windows'] += len(item.windows)
            for window in item.windows:
                assert window.schema == definition.sources and len(window.past) == definition.sources.context
                assert all(type(token) is int and 0 <= token <= definition.sources.vocabulary for token in window.past)
                # Every integer costs at least 19 bytes, with tuple delimiters
                # and separators making at least 20 bytes per lag sufficient.
                assert encoding.packed_size(window.past) >= 20*len(window.past)
                count['pending_window_byte_lower'] += 20*len(window.past)
        if type(item) in (tuple, list, CapturedTokenValues):
            for child in item:
                visit(child)
        elif isinstance(item, Mapping):
            for key, child in item.items():
                visit(key)
                visit(child)
        elif is_dataclass(item) and not isinstance(item, type):
            for field in fields(item):
                visit(getattr(item, field.name))
    visit(value)
    count['selected_byte_lower'] = sum(count[k] for k in
        ('master_hex_bytes', 'origin_base_bytes', 'pending_window_byte_lower'))
    return count


@contextmanager
def observed(definition):
    allocate = shared_reference._SharedReference.allocate
    push, decoded, compare = byte_archive.Builder.push, byte_archive.Reader.decoded, shared_reference._compare_stream
    traffic, census, kinds = Counter(), Counter(), Counter()
    def producer(builder, part):
        result = push(builder, part)
        traffic['producer_bytes'] += len(part)
        return result
    def reader(owner, *args, **kwargs):
        for part in decoded(owner, *args, **kwargs):
            traffic['decoder_bytes'] += len(part)
            traffic['decoder_pieces'] += 1
            yield part
    def checker(actual, expected, size):
        def counted():
            for part in expected:
                traffic['expected_bytes'] += len(part)
                yield part
        return compare(actual, counted(), size)
    def retain(owner, runtime, role, planned):
        before = traffic.copy()
        result = allocate(owner, runtime, role, planned)
        raw = runtime._buffers[owner.pages[-1]]
        header = byte_archive._page(raw)
        # Extent here is checked against three independent actual streams;
        # the producer's declared header is not accepted as a byte-count oracle.
        assert all(traffic[k]-before[k] == header.expanded_bytes for k in
            ('producer_bytes', 'decoder_bytes', 'expected_bytes'))
        assert traffic['decoder_pieces']-before['decoder_pieces'] == header.references
        actual = selected(planned.value, definition)
        assert actual['selected_byte_lower'] <= header.expanded_bytes
        assert header.expanded_bytes <= header.references*byte_archive.PIECE_LIMIT
        census.update(actual)
        census['pages'] += 1
        census['retained_page_bytes'] += len(raw)
        kinds[planned.spec.kind] += 1
        return result
    with patch.object(byte_archive.Builder, 'push', producer), \
            patch.object(byte_archive.Reader, 'decoded', reader), \
            patch.object(shared_reference, '_compare_stream', checker), \
            patch.object(shared_reference._SharedReference, 'allocate', retain):
        yield traffic, census, kinds


def verify_counts(targets, definition, counts):
    expected = schedule(targets, definition.output.update_unit)
    assert {key: counts[key] for key in ('origins', 'pending_windows')} == {
        key: expected[key] for key in ('origins', 'pending_windows')}
    assert counts['master_hex_bytes'] == expected['origins']*8*definition.slot_count
    assert counts['origin_base_bytes'] == expected['origins']*encoding.packed_size(definition.output.base)
    assert counts['pending_window_byte_lower'] == expected['pending_windows']*20*definition.sources.context
    return expected


def finite_histories():
    runs = targets = commits = expanded = pages = pieces = 0
    complete_pairs = 0
    for unit, length in product((1, 2, 4), range(5)):
        for word in product((0, 1), repeat=length):
            with patch('fp_reference.runtime.secrets.token_hex', return_value='native-retention-volume'):
                cc, program, online, _ = report_registration(unit=unit, count=4)
                rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE)
                with observed(program.definition) as (traffic, counts, kinds):
                    for i, target in enumerate(word):
                        assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
                        verify_counts(i+1, program.definition, counts)
                expected = verify_counts(length, program.definition, counts)
                assert rt._cursor == len(rt._event_traces) == length
                assert rt._candidates[rt._deployed_id].learner.optimizer_steps == expected['commits']
                assert kinds['after_optimizer_phase'] == expected['commits']
                # Compare complete state against an unobserved control for
                # every length/unit, one representative binary word per pair.
                if word == (0,)*length:
                    plain = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE)
                    for i, target in enumerate(word):
                        assert plain.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                        assert plain.observe(target).status == 'OBSERVED_REFERENCE'
                    assert encoding.pack(plain.snapshot()) == encoding.pack(rt.snapshot())
                    complete_pairs += 1
                runs += 1
                targets += length
                commits += expected['commits']
                expanded += traffic['producer_bytes']
                pages += counts['pages']
                pieces += traffic['decoder_pieces']
    return dict(complete_histories=runs, targets=targets, commits=commits,
        complete_observed_unobserved_state_pairs=complete_pairs, pages=pages,
        bytes_in_each_of_three_complete_streams=expanded, decoded_piece_occurrences=pieces,
        exact_formula_at_every_completed_prefix=True, identical_aliases_count_as_repeated_occurrences=True)


def full_vocabulary():
    from run_native_text_a1 import registration
    cc, program, online, storage, reporting = registration()
    rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage, reporting=reporting)
    with observed(program.definition) as (traffic, counts, kinds):
        for i, target in enumerate((0, 1)):
            assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            verify_counts(i+1, program.definition, counts)
    residency = complete_residency(rt)
    assert rt._reference_archive.images is not None and rt._reference_archive.images.used > 0
    assert len(online.data.active.observation_ids) == 1048576
    d = program.definition
    full = schedule(1048576, d.output.update_unit)
    components = dict(master_hex_bytes=full['origins']*8*d.slot_count,
        origin_base_bytes=full['origins']*encoding.packed_size(d.output.base),
        pending_window_byte_lower=full['pending_windows']*20*d.sources.context)
    volume = sum(components.values())
    assert volume == 68844511893504
    return dict(synthetic_targets=2, original_training_declaration=1048576,
        actual_three_stream_counts=dict(traffic), actual_selected_census=dict(counts),
        actual_record_kinds=dict(kinds), complete_residency=residency,
        canonical_images_active=True, full_schedule=dict(**full, **components,
            selected_byte_lower_in_each_stream=volume, three_stream_byte_lower=3*volume,
            minimum_decoder_piece_occurrences=(volume+byte_archive.PIECE_LIMIT-1)//byte_archive.PIECE_LIMIT,
            distinct_origin_master_payload_upper=(full['commits']+1)*4*d.slot_count,
            required_per_stream_bytes_per_second_for_7200_seconds=str(Fraction(volume, 7200))),
        full_volume_is_source_derived_not_prefix_extrapolated=True,
        no_full_host_or_time_impossibility_claim=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    result = dict(status='PASS_NATIVE_RETENTION_VOLUME', scope=__doc__.strip())
    for name, action in (('finite_histories', finite_histories), ('full_vocabulary', full_vocabulary)):
        result[name] = action()
        print('PASS '+name, flush=True)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
