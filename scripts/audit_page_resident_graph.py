"""Exact page-resident graph control against the existing eager realization.

No corpus, actual device, throughput comparison or whole-host fit assertion.
"""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler'),
               str(ROOT/'theory/numerical_checks')]
from fp_reference import value_graph as eager, encoding
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.shared_reference import _compare_stream
import page_resident_graph_model as compact
import audit_owned_value_graph_runtime as fixture


def emit_page(producer, value):
    producer.begin(bytearray(producer.limits.page_bytes))
    walk = eager._OwnedWalk(lambda raw: eager.U64.unpack(producer.send(raw))[0], {}, producer.limits)
    root, _ = walk.value(value)
    producer.finish(eager.U64.pack(root))
    output = bytearray(producer.extent)
    producer.write(output)
    page = bytes(output)
    if type(producer) is compact.Producer:
        producer.accept(page)
    else:
        producer.accept()
    return page, root


def same(left, right):
    assert list(left.index.raw) == list(right.index.raw)
    assert left.nodes == right.nodes and left.metrics == right.metrics
    assert left.references == right.references and left.roots == right.roots
    assert left.pages == right.pages


def corresponding_resources(old, new, extra):
    counts = Counter()
    a, b = old.resources, new.resources
    assert a.keys() == b.keys()
    for key in a.keys()-{'events', 'spent'}:
        assert a[key] == b[key], key
    assert len(a['events']) == len(b['events'])
    for first, second in zip(a['events'], b['events']):
        if first[1] == 'work' and first[5].endswith(':owned-value-graph'):
            assert len(first[4]) == 1 and first[4][0][0] == 'work'
            expected = first[:4]+((('work', first[4][0][1]+extra),),)+first[5:]
            assert expected == second
            counts[first[2]] += 1
        else:
            assert first == second
    for role in a['spent']:
        assert dict(b['spent'][role]) == {**a['spent'][role],
            'work': a['spent'][role]['work']+counts[role]*extra}
    # Compare every other snapshot field after checking every resource-field
    # difference explicitly, including failed/unused and non-graph events.
    assert replace(old, resources=new.resources) == new
    assert encoding.pack(replace(old, resources=new.resources)) == encoding.pack(new)
    return sum(counts.values())*extra


def grammar():
    from audit_owned_value_graph import samples
    limits = eager.Limits(page_bytes=1<<18, comparisons=1<<26, references=1<<26)
    first, second = eager.Producer(limits), compact.Producer(limits)
    old, new, cases = eager.Reader(limits), compact.Reader(limits), 0
    values = list(samples()) + [tuple(range(n)) for n in (1, 2, 8, 65, 513)]
    with patch.object(eager.zlib, 'crc32', return_value=0):
        for value in values:
            a, expected = emit_page(first, value)
            b, actual = emit_page(second, value)
            assert (a, expected) == (b, actual)
            assert old.add(a) == new.add(b) == actual
            assert b''.join(new.expanded(actual, byte_cap=limits.expanded,
                visit_cap=limits.references)) == encoding.pack(value)
            same(old, new)
            cases += 1
    # An accepted old page must remain intact after workspace reuse.
    assert all(type(page) is bytes for page in second.index.pages)
    for identity in range(len(second.index.raw)):
        assert second.index.view(identity).readonly
        assert second.index.view(identity).obj is second.index.pages[second.index.rows[identity][0]]
    return dict(values=cases, nodes=len(new.nodes), pages=len(new.pages),
        complete_wire_identity=True, forced_crc_collisions_checked_by_full_equality=True,
        separate_indices_use_only_actual_immutable_pages=True)


def histories():
    totals, max_payload = Counter(), 0
    for unit, size in product((1, 2, 4), range(5)):
        for word in product((0, 1), repeat=size):
            with patch('fp_reference.runtime.secrets.token_hex', return_value='page-resident-runtime'):
                old = fixture.setup(unit, 4, memo=32)
                with patch('fp_reference.value_graph_reference._ValueGraphReference', compact.Owner):
                    new = fixture.setup(unit, 4, memo=32)
                for i, target in enumerate(word):
                    fixture.event(old, i, target)
                    fixture.event(new, i, target)
            a, b = old.snapshot(), new.snapshot()
            totals['extra_metadata_work'] += corresponding_resources(a, b,
                compact.metadata_work(new._reference_archive.contract))
            old_archive, new_archive = old._reference_archive, new._reference_archive
            same(old_archive.reader, new_archive.reader)
            assert old_archive.encoder.index.raw == new_archive.encoder.index.raw
            for index, identity in enumerate(new_archive.pages):
                page = new._buffers[identity]
                assert new_archive.reader.pages[index] is page
                assert new_archive.encoder.index.pages[index] is page
            # Cold recovery is independent of both live compact indices.
            recovered = eager.Reader(new_archive.limits)
            for identity in new_archive.pages:
                recovered.add(new._buffers[identity])
            same(recovered, new_archive.reader)
            payload = compact.resident_payload(new_archive)
            max_payload = max(max_payload, sum(payload[k] for k in (
                'immutable_page_bytes', 'locator_capacity_bytes', 'metric_capacity_bytes', 'hash_capacity_bytes')))
            totals['histories'] += 1
            totals['targets'] += len(word)
            totals['commits'] += len(word)//unit
            totals['nodes'] += len(new_archive.reader.nodes)
            totals['pages'] += len(new_archive.pages)
    return dict(totals, all_complete_values_and_wire_pages_equal=True,
        every_resource_event_and_role_total_checked_with_exact_extra_debit=True,
        every_other_complete_snapshot_field_equal=True,
        all_actual_pages_shared_without_raw_or_parsed_node_copies=True,
        independent_cold_eager_recovery=True, largest_selected_resident_payload=max_payload)


def storage_law():
    limits = eager.Limits(nodes=16384, page_bytes=1<<20)
    producer, reader = compact.Producer(limits), compact.Reader(limits)
    counters = []
    first = 0
    for stop in (1, 8, 9, 4096, 4097, 8193):
        producer.begin(bytearray(limits.page_bytes))
        for value in range(first, stop):
            root = producer.send(b'i'+format(value, 'x').encode())
        producer.finish(root)
        output = bytearray(producer.extent)
        producer.write(output)
        page = bytes(output)
        reader.add(page)
        producer.accept(page)
        n = len(reader.nodes)
        blocks = (n+compact.BLOCK-1)//compact.BLOCK
        capacity = max(16, 1 << (2*n-1).bit_length())
        measured = producer.index.rows.capacity_bytes+reader.index.rows.capacity_bytes
        measured += reader.checked.capacity_bytes+len(producer.index.table)+len(reader.index.table)
        assert measured == 104*compact.BLOCK*blocks+16*capacity
        assert all(index.peak_table_bytes <= 12*capacity for index in (producer.index, reader.index))
        assert producer.index.rows is not reader.index.rows
        assert producer.index.table is not reader.index.table
        assert all(a is b for a, b in zip(producer.index.pages, reader.index.pages))
        counters.append(dict(nodes=n, blocks=blocks, hash_slots_per_index=capacity,
            exact_compact_table_capacity=measured))
        first = stop
    # A row failure after publication into the private parser cannot grant a
    # complete root, lose old pages, or permit an additional parser append.
    next_page, _ = emit_page(compact.Producer(limits), 9000)
    next_page = bytearray(next_page)
    eager.HEADER.pack_into(next_page, 0, eager.MAGIC, len(reader.pages), len(reader.nodes), 1, len(reader.nodes))
    old_root, old_pages = reader.roots[-1], tuple(reader.pages)
    append = reader.checked.append
    def fail(*values):
        append(*values)
        raise MemoryError('after private metric row')
    with patch.object(reader.checked, 'append', fail):
        fixture.refuse(lambda: reader.add(bytes(next_page)), MemoryError)
    assert tuple(reader.pages) == old_pages and reader.roots[-1] == old_root
    fixture.refuse(lambda: reader.add(bytes(next_page)), ContractError)
    assert b''.join(reader.expanded(old_root, byte_cap=limits.expanded,
        visit_cap=limits.references)) == encoding.pack(8192)
    return dict(capacity_boundaries=counters, exact_capacity_law=True,
        separate_indices_and_shared_immutable_pages=True, partial_metric_row_failure_preserves_old_roots=True)


def failures():
    limits = eager.Limits(page_bytes=1<<16, comparisons=1<<20, references=1<<20)
    producer = compact.Producer(limits)
    first, root = emit_page(producer, (0,))
    second, _ = emit_page(producer, (1, 0))
    refused = accepted = 0
    for position, bit in product(range(len(second)), range(8)):
        page = bytearray(second)
        page[position] ^= 1<<bit
        reader = compact.Reader(limits)
        reader.add(first)
        try:
            current = reader.add(bytes(page))
            expected, _ = eager._OwnedWalk(reader.find, {}, limits).value((1, 0))
            if current != expected:
                raise ContractError('changed root')
        except (ContractError, ResourceExceeded):
            refused += 1
        else:
            assert b''.join(reader.expanded(current, byte_cap=limits.expanded,
                visit_cap=limits.references)) == encoding.pack((1, 0))
            accepted += 1
        assert b''.join(reader.expanded(root, byte_cap=limits.expanded,
            visit_cap=limits.references)) == encoding.pack((0,))
    # A producer cannot publish a mutable workspace as historical authority.
    candidate = compact.Producer(limits)
    candidate.begin(bytearray(limits.page_bytes))
    candidate.finish(candidate.send(b'i1'))
    output = bytearray(candidate.extent)
    candidate.write(output)
    fixture.refuse(lambda: candidate.accept(output))
    changed = bytearray(output)
    changed[-1] ^= 1
    fixture.refuse(lambda: candidate.accept(bytes(changed)))
    candidate.accept(bytes(output))
    # Necessity: byte expansion on repeated child lookups is independent of
    # the old node/unfolded-reference tests. Unused definitions are enough.
    limits = replace(limits, references=2048)
    producer = eager.Producer(limits)
    producer.begin(bytearray(limits.page_bytes))
    emit = lambda raw: eager.U64.unpack(producer.send(raw))[0]
    leaf = emit(b'b'+b'a'*1024)
    emit(eager.vector(b'u', (leaf,)*8))
    producer.finish(eager.U64.pack(leaf))
    output = bytearray(producer.extent)
    producer.write(output)
    page = bytes(output)
    old = eager.Reader(limits)
    old.add(page)
    class UnprojectedNodes(compact.Nodes):
        def __getitem__(self, key):
            return tuple(super().__getitem__(key))
    class Unprojected(compact.Reader):
        def __init__(self, limits):
            super().__init__(limits)
            self.nodes = UnprojectedNodes(self)
    class Unmetered(Unprojected):
        def _lookup_debit(self, count):
            self.lookup_work += count
    unmetered = Unmetered(limits)
    unmetered.add(page)
    assert unmetered.lookup_work == 8*1026 > limits.references
    metered = Unprojected(limits)
    fixture.refuse(lambda: metered.add(page), ResourceExceeded)
    assert metered.lookup_work <= limits.references and not metered.roots
    projected = compact.Reader(limits)
    projected.add(page)
    assert projected.lookup_work == 8
    # Projection does not remove the need to fund value reconstruction.
    producer = eager.Producer(limits)
    producer.begin(bytearray(limits.page_bytes))
    emit = lambda raw: eager.U64.unpack(producer.send(raw))[0]
    zero, one = emit(b'i0'), emit(b'i1')
    data = emit(b'b'+b'\0'*8192)
    past, tail = emit(eager.vector(b'u', (zero,))), emit(b'u')
    emit(eager.vector(b'c', (data, one, past, one, tail)))
    producer.finish(eager.U64.pack(zero))
    output = bytearray(producer.extent)
    producer.write(output)
    page = bytes(output)
    eager.Reader(limits).add(page)
    packed = compact.Reader(limits)
    fixture.refuse(lambda: packed.add(page), ResourceExceeded)
    assert packed.lookup_work <= limits.references and not packed.roots
    # A global save/set/restore around a generator's lifetime is insufficient:
    # the second suspended recovery can lend its cap to the first one.
    class AmbientRecovery(compact.Reader):
        def expanded(self, root, *, byte_cap, visit_cap):
            before = self.lookup_work, self.lookup_cap
            self.lookup_work, self.lookup_cap = 0, byte_cap+visit_cap
            try:
                yield from eager.Reader.expanded(self, root, byte_cap=byte_cap, visit_cap=visit_cap)
            finally:
                self.lookup_work, self.lookup_cap = before
    recovery_limits = replace(limits, references=1<<20)
    borrowed = AmbientRecovery(recovery_limits)
    borrowed.add(page)
    capture = len(borrowed.nodes)-1
    small = dict(byte_cap=borrowed.metrics[capture].size, visit_cap=borrowed.references[capture])
    assert small['byte_cap']+small['visit_cap'] < 8192
    first = borrowed.expanded(capture, **small)
    prefix = next(first)
    second = borrowed.expanded(zero, byte_cap=20000, visit_cap=20000)
    next(second)
    assert prefix+b''.join(first) == encoding.pack((F(0),))
    second.close()
    isolated = compact.Reader(recovery_limits)
    isolated.add(page)
    original_meter = isolated.lookup_work, isolated.lookup_cap
    first = isolated.expanded(capture, **small)
    next(first)
    second = isolated.expanded(zero, byte_cap=20000, visit_cap=20000)
    prefix = next(second)
    assert isolated._recovery.get() is None
    fixture.refuse(lambda: b''.join(first), ResourceExceeded)
    assert prefix+b''.join(second) == encoding.pack(0)
    assert (isolated.lookup_work, isolated.lookup_cap) == original_meter
    assert isolated._recovery.get() is None
    return dict(bit_variants_refused=refused, bit_variants_exact=accepted,
        previous_page_recovery_after_every_failure=True,
        mutable_or_changed_acceptance_refused=True,
        repeated_lookup_necessity=dict(old_unfolded_references=max(old.references),
            unmetered_reconstructed_bytes=unmetered.lookup_work,
            reconstruction_allowance=limits.references, unprojected_refuses_before_overspend=True,
            actual_projected_tag_bytes=projected.lookup_work,
            actual_large_value_refuses_before_overspend=True),
        interleaved_recovery=dict(ambient_meter_borrows_another_calls_cap=True,
            original_small_call_allowance=small['byte_cap']+small['visit_cap'],
            required_operand_bytes=8192, actual_continuation_meter_refuses=True,
            independent_recovery_completes=True, parser_meter_unchanged=True))


def full_native():
    from run_native_text_a1 import registration, complete_residency
    from fp_reference import ReferenceCompilerRuntime
    cc, program, online, storage, reporting = registration()
    with patch('fp_reference.value_graph_reference._ValueGraphReference', compact.Owner), fixture.observed() as checks:
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            shared_storage=fixture.contract(storage, memo=8192))
        initial = compact.resident_payload(rt._reference_archive)
        for i, target in enumerate((0, 1)):
            fixture.event(rt, i, target)
    owner = rt._reference_archive
    return dict(original_train=1048576, original_report=16384, vocabulary=50257,
        masters=603092, synthetic_targets=2, initial_compact_storage=initial,
        final_compact_storage=compact.resident_payload(owner),
        actual_native_canonical_checks=dict(checks), residency=complete_residency(rt),
        no_full_host_timing_or_model_result=True)


def tensor():
    with patch('fp_reference.value_graph_reference._ValueGraphReference', compact.Owner):
        return dict(complete_cpu_tensor=fixture.tensor_histories(),
            failures=fixture.failure_prefixes(), funding_and_freshness=fixture.funding_and_freshness())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--full-native', action='store_true')
    mode.add_argument('--tensor', action='store_true')
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions required')
    result = dict(status='PASS_PAGE_RESIDENT_GRAPH_CPU', scope=__doc__.strip())
    actions = [('full_native', full_native)] if args.full_native else [('tensor', tensor)] if args.tensor else [
        ('grammar', grammar), ('histories', histories), ('storage_law', storage_law), ('failures', failures)]
    for name, action in actions:
        result[name] = action()
        print('PASS '+name, flush=True)
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
