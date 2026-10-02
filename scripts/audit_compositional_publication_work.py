"""Exact publication-copy law of the existing default-off expression owner.

No changed codec, corpus, timing or device run. Ordinary native Runtime only;
the old actual AMP comparison remains terminal and is not replayed.
"""
from collections import Counter
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, byte_terms, encoding
from fp_reference.compositional_reference import _CompositionalReference
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded
from audit_token_reporting import report_registration
from audit_shared_token_retention import STORAGE


def setup():
    cc, program, online, _ = report_registration(unit=2, count=8)
    storage = replace(STORAGE, encoding=byte_terms.ENCODING_ID,
        expression_nodes=1 << 18, expression_bindings=1 << 18)
    return ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage)


def binding_cardinality():
    cases = []
    for size in (1, 2, 8, 17, 64):
        values = tuple(f'train/{i}' for i in range(size))
        for cap in (size, size+1):
            limits = byte_terms.Limits(page_bytes=1 << 16)
            producer = byte_terms.Producer(limits)
            builder = producer.begin(bytearray(limits.page_bytes))
            def handle(message):
                return byte_terms.U64.unpack(builder.send(message))[0]
            walk = byte_terms.Walk(lambda raw: handle(b'L'+raw),
                lambda a, b: handle(b'C'+byte_terms.U64.pack(a)+byte_terms.U64.pack(b)), {}, cap)
            try:
                root, pure = walk.value(values)
            except ResourceExceeded:
                assert cap == size
                assert len(walk.proposals) == size
            else:
                assert cap == size+1 and pure and len(walk.proposals) == size+1
                assert {id(value) for value in values} <= walk.proposals.keys()
                builder.finish(byte_terms.U64.pack(root))
                page = bytearray(builder.extent)
                builder.write(page)
                reader = byte_terms.Reader(limits)
                reader.add(bytes(page))
                assert b''.join(reader.decoded(0, byte_cap=1 << 20, reference_cap=1 << 20)) == encoding.pack(values)
            cases.append(dict(distinct_strings=size, binding_cap=cap, accepted=cap == size+1))
    from run_native_text_a1 import TRAIN, REPORT
    assert (TRAIN, REPORT) == (1048576, 16384)
    return dict(exact_tuple_threshold_controls=cases,
        full_manifest_distinct_training_and_reporting_id_strings=TRAIN+REPORT,
        previous_actual_expression_binding_cap=1 << 20,
        unavoidable_leaf_bindings_exceed_that_cap_by=TRAIN+REPORT-(1 << 20),
        counterfactual_unchanged_cap_cannot_initialize_full_text_manifest=True,
        no_actual_full_constructor_or_old_experiment_replayed=True)


def audit():
    verify, accept = _CompositionalReference._verify, _CompositionalReference._accept
    counts = Counter()
    lengths = []
    def observed_verify(owner, *args, **kwargs):
        entries = len(owner.bindings)
        result = verify(owner, *args, **kwargs)
        assert owner._pending_bindings is not owner.bindings
        assert all(owner._pending_bindings[key] is value for key, value in owner.bindings.items())
        counts['binding_entries_copied'] += entries
        counts['binding_publications'] += 1
        return result
    def observed_accept(owner, *args, **kwargs):
        before = owner.pages
        length = len(before)
        result = accept(owner, *args, **kwargs)
        assert type(owner.pages) is list and owner.pages is not before
        assert len(owner.pages) == length+1
        assert all(owner.pages[i] is value for i, value in enumerate(before))
        lengths.append(length)
        counts['page_slots_copied'] += length
        return result
    word = (0, 1, 1, 0)*2
    with patch('fp_reference.runtime.secrets.token_hex', return_value='compositional-publication-work'):
        with patch.object(_CompositionalReference, '_verify', observed_verify), \
                patch.object(_CompositionalReference, '_accept', observed_accept):
            rt = setup()
            initial = len(rt._reference_archive.pages)
            for i, target in enumerate(word):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(target).status == 'OBSERVED_REFERENCE'
                # Every revealed observation has a different immutable string
                # value in the strong source-binding table. Equality of many
                # other source values cannot collapse these distinct labels.
                sources = {source for source, _ in rt._reference_archive.bindings.values() if type(source) is str}
                assert all(f'train/{j}' in sources for j in range(i+1))
        snapshot = rt.snapshot()
        plain = setup()
        for i, target in enumerate(word):
            assert plain.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert plain.observe(target).status == 'OBSERVED_REFERENCE'
        assert encoding.pack(snapshot) == encoding.pack(plain.snapshot())
    pages = len(rt._reference_archive.pages)
    assert lengths == list(range(pages))
    assert counts['page_slots_copied'] == pages*(pages-1)//2
    assert counts['binding_publications'] == pages
    assert pages-initial >= 5*len(word)+len(word)//2
    targets, unit = 1048576, 512
    # At least five ordinary pages and one additional commit page. Changed
    # range pages, initialization and reporting only increase this lower.
    minimum_pages = 5*targets+targets//unit
    copies = minimum_pages*(minimum_pages-1)//2
    return dict(status='PASS_COMPOSITIONAL_PUBLICATION_WORK', scope=__doc__.strip(),
        actual=dict(targets=len(word), commits=len(word)//2, initial_pages=initial,
            total_pages=pages, **dict(counts), complete_observed_unobserved_snapshot_equal=True,
            every_old_page_and_binding_identity_preserved_in_the_copy=True,
            every_revealed_observation_id_retained_as_a_source_binding=True),
        original_full_native_schedule=dict(targets=targets, unit=unit,
            minimum_ordinary_pages=minimum_pages, minimum_old_page_slots_copied=copies,
            selected_reference_slot_bytes_on_64_bit_host=8*copies,
            minimum_binding_entries_copied=targets*(targets-1)//2),
        manifest_binding_lower=binding_cardinality(),
        source_count_not_elapsed_time_or_resident_memory=True,
        existing_expression_realization_remains_default_off=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    result = audit()
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))
    print(result['status'], flush=True)
