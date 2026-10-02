"""Exact passive typed-graph audit on complete native Runtime records.

The Runtime keeps its existing byte archive and every ordinary check. This
observer grants no storage, resource, certificate, CUDA or continuation port.
No corpus, timing experiment, shortened text score or old journal replay.
"""
from collections import Counter
from contextlib import contextmanager
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
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler'),
               str(ROOT/'theory/numerical_checks')]
import owned_value_graph_model as model
from fp_reference import ReferenceCompilerRuntime, encoding, shared_reference
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded
from fp_reference.token_causal import TokenSources, TokenWindow
from fp_reference.token_values import CapturedTokenValues
from audit_shared_token_retention import STORAGE
from audit_token_reporting import report_registration
from run_native_text_a1 import complete_residency


def recover(owner, root, value):
    metric = owner.reader.metrics[root]
    shared_reference._compare_stream(owner.reader.expanded(root,
        byte_cap=owner.limits.expanded, visit_cap=1 << 30),
        (s.encode('utf-8', 'surrogatepass') for s in encoding.fragments(value, packed=True)), metric.size)
    assert metric.size == encoding.bounded_packed_size(value,
        byte_limit=owner.limits.expanded, integer_bits=owner.limits.integer_bits)
    assert metric.size == encoding.bounded_packed_size(value,
        byte_limit=owner.limits.expanded, integer_bits=owner.limits.integer_bits, images=owner)


def samples():
    atoms = (None, False, True, 0, -1, 256, F(0), F(-7, 16), F(3, 7), '',
        '\"\\\n\x7f', '😀', '\ud83d\ude00', '\ud800', b'', b'\x00\xff')
    values = list(atoms)+[(), []]
    values += [pair for pair in product(atoms[:9], repeat=2)]
    values += [[None, (1, 2), F(1, 3)], {'z': 1, 'a': (2, 3)},
        TokenWindow(TokenSources(2, 3), 2, (0, 1, 2))]
    for width, past, grid in product((1, 2), ((), (0,), (1, 0, 1)), (1, 4, 1 << 32)):
        raw = struct.pack('<4I', 0, 1, (1 << 32)-1, 12)
        values.append(CapturedTokenValues(raw, width, past, grid, (F(1, 3), F(0))))
    return values


def exact_values():
    owner = model.Owner(owned_records=True)
    roots_id, bindings_id = id(owner.roots), id(owner.bindings)
    tested_guards = 0
    for value in samples():
        with patch.object(model.Reader, 'expanded', side_effect=AssertionError('binding unfolded a value')), \
                patch.object(CapturedTokenValues, '__iter__', side_effect=AssertionError('binding expanded captured inputs')):
            root = owner.retain(value)
        recover(owner, root, value)
        assert id(owner.roots) == roots_id and id(owner.bindings) == bindings_id
        m = owner.reader.metrics[root]
        for byte_limit, depth, bits in product(
                set((1, m.size, max(m.size, m.traversal), max(m.size, m.traversal)+1)),
                set((1, max(1, m.depth-1), max(1, m.depth))),
                set((1, max(1, m.integer_bits-1), max(1, m.integer_bits)))):
            admitted = max(m.size, m.traversal) <= byte_limit and m.depth <= depth and m.integer_bits <= bits
            try:
                encoding.bounded_packed_size(value, byte_limit=byte_limit, depth_limit=depth, integer_bits=bits)
            except ResourceExceeded:
                assert not admitted
            else:
                assert admitted
            tested_guards += 1
    rebuilt = model.Reader(owner.limits)
    for page in owner.reader.pages:
        rebuilt.add(page)
    assert rebuilt.nodes == owner.reader.nodes and rebuilt.metrics == owner.reader.metrics
    for root, value in zip(owner.roots, samples()):
        raw = b''.join(rebuilt.expanded(root, byte_cap=1 << 20, visit_cap=1 << 20))
        assert raw == encoding.pack(value)
    return dict(values=len(owner.roots), exact_guard_boundary_checks=tested_guards,
        independent_page_only_rebuild=True, no_old_publication_container_replaced=True,
        no_captured_input_iteration_or_complete_expansion_during_binding=True,
        graph_nodes=len(owner.reader.nodes), binding_entries=len(owner.bindings),
        expanded_bytes=sum(owner.reader.metrics[root].size for root in owner.roots),
        page_bytes=sum(map(len, owner.reader.pages)), expected_walk=dict(owner.counts))


def stability_boundary():
    record = TokenSources(2, 3)
    owner = model.Owner()  # No claim that a caller's frozen record is private.
    before = owner.retain(record)
    record.__dict__['context'] = 4
    after = owner.retain(record)
    assert before != after and id(record) not in owner.bindings
    recover(owner, after, record)
    mutable = [TokenSources(2, 3)]
    outer = (mutable,)
    owner.retain(outer)
    mutable[0].__dict__['context'] = 7
    root = owner.retain(outer)
    recover(owner, root, outer)
    assert id(outer) not in owner.bindings
    # Necessary-premise witness: the boolean cannot establish ownership.
    borrowed = model.Owner(owned_records=True)
    foreign = TokenSources(2, 3)
    root = borrowed.retain(foreign)
    foreign.__dict__['context'] = 9
    assert borrowed.retain(foreign) == root
    assert b''.join(borrowed.reader.expanded(root, byte_cap=1 << 20, visit_cap=100)) != encoding.pack(foreign)
    return dict(default_rechecks_foreign_records_and_mutable_descendants=True,
        caller_claiming_ownership_can_produce_stale_binding=True,
        ownership_premise_is_necessary_not_established_by_a_flag=True)


def binding_eviction():
    # Source facts accelerate traversal. Page bytes, not those facts, retain
    # the complete value. Forgetting facts changes work, never expected roots.
    values = samples()
    values = values+list(reversed(values))+values
    warm, cold = model.Owner(owned_records=True), model.Owner(owned_records=True)
    warm_peak = cold_peak = 0
    for value in values:
        cold.bindings.clear()
        assert warm.retain(value) == cold.retain(value)
        assert warm.reader.pages[-1] == cold.reader.pages[-1]
        warm_peak, cold_peak = max(warm_peak, len(warm.bindings)), max(cold_peak, len(cold.bindings))
    assert warm.reader.nodes == cold.reader.nodes
    assert warm.reader.metrics == cold.reader.metrics
    assert warm.counts['source_visits'] < cold.counts['source_visits']
    return dict(retentions=len(values), every_page_and_root_equal=True,
        entire_derived_graph_equal=True, clear_before_every_cold_retention=True,
        warm_binding_peak=warm_peak, cold_binding_peak=cold_peak,
        warm_source_visits=warm.counts['source_visits'], cold_source_visits=cold.counts['source_visits'],
        no_runtime_eviction_policy_or_optimal_cache_claim=True)


def adversaries():
    refused = []
    value = ('alpha', 1, (F(1, 3), b'bytes'))
    good = model.Owner()
    good.retain(value)
    page = good.reader.pages[0]
    # Single-bit variants are either refused or must still describe the exact
    # independently expected structural value. Valid irrelevant data need not
    # be rejected merely because a page is byte-different.
    accepted = rejected = 0
    for offset in range(len(page)):
        for bit in range(8):
            raw = bytearray(page)
            raw[offset] ^= 1 << bit
            reader = model.Reader(good.limits)
            try:
                root = reader.add(bytes(raw))
                expected, _ = model.Walk(reader.find, {}, good.limits, False).value(value)
                if root != expected:
                    raise ContractError('wrong root')
            except (ContractError, ResourceExceeded):
                rejected += 1
            else:
                assert b''.join(reader.expanded(root, byte_cap=1 << 20, visit_cap=1000)) == encoding.pack(value)
                accepted += 1
    cases = []
    for label, transform in (
        ('changed_scalar', lambda raw: b'swrong' if raw == b'salpha' else raw),
        ('forward_reference', lambda raw: model.vector(b'u', (1 << 32,)) if raw[:1] == b'u' else raw)):
        owner = model.Owner()
        send = owner.producer.send
        with patch.object(owner.producer, 'send', side_effect=lambda raw: send(transform(raw))):
            try:
                owner.retain(value)
            except (ContractError, ResourceExceeded):
                assert owner.failed and not owner.roots and not owner.bindings
                cases.append(label)
            else:
                raise AssertionError(label)
    for label, changes, sample in (
        ('node_cap', {'nodes': 1}, value), ('binding_cap', {'bindings': 1}, (b'a', b'b')),
        ('expanded_cap', {'expanded': 40}, (0, 1)),
        ('integer_cap', {'integer_bits': 1}, 17), ('depth_cap', {'depth': 1}, ((1,),)),
        ('page_cap', {'page_bytes': model.HEADER.size}, 1)):
        owner = model.Owner(replace(model.Limits(), **changes))
        try:
            owner.retain(sample)
        except ResourceExceeded:
            assert owner.failed
            cases.append(label)
        else:
            raise AssertionError(label)
    for stage in ('producer_accept', 'root_append', 'partial_binding_update'):
        owner = model.Owner()
        old = owner.retain((0,))
        old_bindings = dict(owner.bindings)
        if stage == 'producer_accept':
            owner.producer.accept = lambda: (_ for _ in ()).throw(MemoryError('accept'))
        elif stage == 'root_append':
            class FailingList(list):
                def append(self, value): raise MemoryError('append')
            owner.roots = FailingList(owner.roots)
        else:
            class FailingDict(dict):
                def update(self, values):
                    key = next(iter(values))
                    self[key] = values[key]
                    raise MemoryError('partial update')
            owner.bindings = FailingDict(owner.bindings)
        try:
            owner.retain((b'next',))
        except MemoryError:
            assert owner.failed and all(owner.bindings[k] is v for k, v in old_bindings.items())
            assert owner.roots[0] == old
            assert len(owner.roots) == (2 if stage == 'partial_binding_update' else 1)
            assert b''.join(owner.reader.expanded(old, byte_cap=100, visit_cap=100)) == encoding.pack((0,))
            for source, root in owner.bindings.values():
                recover(owner, root, source)
            try:
                owner.retain(0)
            except ContractError:
                pass
            else:
                raise AssertionError('terminal model continued')
            refused.append(stage)
        else:
            raise AssertionError(stage)
    # A forged immutable tuple subclass still owes complete operand checks.
    for parts in ((b'\0'*4, 1, (0,), 3, ()), (b'\0'*4, 1, [0], 4, ())):
        forged = tuple.__new__(CapturedTokenValues, parts)
        try:
            model.Owner().retain(forged)
        except ContractError:
            cases.append('forged_capture')
        else:
            raise AssertionError('forged capture')
    capture = CapturedTokenValues(b'\0'*8, 1, (0,), 4, (F(1, 3),))
    for label, wrong in (('reader_capture_grid', {b'i4': b'i3'}),
                         ('reader_capture_tail', {b'q1/3': b'i1'}),
                         ('reader_capture_source_index', {b'i0': b'i2'})):
        owner = model.Owner()
        send = owner.producer.send
        with patch.object(owner.producer, 'send', side_effect=lambda raw: send(wrong.get(raw, raw))):
            try:
                owner.retain(capture)
            except ContractError:
                assert owner.failed and not owner.roots
                cases.append(label)
            else:
                raise AssertionError(label)
    # Identical expanded tuples with distinct native capture/tuple structure
    # belong to different fixed expression classes, just as in byte terms.
    owner = model.Owner()
    compact, literal = owner.retain(capture), owner.retain(tuple(capture))
    assert compact != literal
    assert b''.join(owner.reader.expanded(compact, byte_cap=1000, visit_cap=100)) == \
           b''.join(owner.reader.expanded(literal, byte_cap=1000, visit_cap=100))
    finish = owner.producer.finish
    with patch.object(owner.producer, 'finish', side_effect=lambda root: finish(literal)):
        try:
            owner.retain(capture)
        except ContractError:
            assert owner.failed and len(owner.roots) == 2
            cases.append('equal_bytes_wrong_structural_root')
        else:
            raise AssertionError('broadened structural class')
    return dict(single_bit_pages=accepted+rejected, bit_pages_accepted_with_exact_value=accepted,
        bit_pages_refused=rejected, producer_and_cap_refusals=cases,
        terminal_publication_failures=refused, all_old_roots_and_bindings_preserved=True)


@contextmanager
def observed():
    original = shared_reference._SharedReference.allocate
    owner, totals, types = model.Owner(owned_records=True), Counter(), Counter()
    def retain(archive, runtime, role, planned):
        result = original(archive, runtime, role, planned)
        prior_roots, prior_bindings = owner.roots, owner.bindings
        with patch.object(model.Reader, 'expanded', side_effect=AssertionError('binding expanded a record')), \
                patch.object(CapturedTokenValues, '__iter__', side_effect=AssertionError('binding expanded captured inputs')):
            root = owner.retain(planned.value)
        assert owner.roots is prior_roots and owner.bindings is prior_bindings
        recover(owner, root, planned.value)
        totals['records'] += 1
        totals['canonical_bytes'] += owner.reader.metrics[root].size
        types[planned.spec.kind] += 1
        return result
    with patch.object(shared_reference._SharedReference, 'allocate', retain):
        yield owner, totals, types


def graph_counts(owner):
    types = Counter(tag.decode() for tag, _ in owner.reader.nodes)
    payload = sum(map(len, owner.reader.pages))
    raw_bytes = sum(len(raw) for raw in owner.reader.index)
    assert payload == model.HEADER.size*len(owner.reader.pages)+8*len(owner.reader.nodes)+raw_bytes
    edges = sum(len(value) for tag, value in owner.reader.nodes if tag in (b'u', b'l', b'm', b'd', b'c'))
    atoms = sum(len(raw)-1 for raw in owner.reader.index if raw[:1] not in (b'u', b'l', b'm', b'd', b'c'))
    assert payload == 40*len(owner.reader.pages)+9*len(owner.reader.nodes)+atoms+8*edges
    return dict(nodes=len(owner.reader.nodes), bindings=len(owner.bindings), pages=len(owner.roots),
        page_bytes=payload, distinct_node_payload_bytes=raw_bytes,
        distinct_child_edges=edges, distinct_atom_payload_bytes=atoms,
        node_tags=dict(types), expected_walk=dict(owner.counts), parser=dict(owner.reader.counts),
        raw_master_and_other_byte_leaf_payload=sum(len(value) for tag, value in owner.reader.nodes if tag == b'b'))


def native_histories():
    totals, pairs = Counter(), 0
    for unit, length in product((1, 2, 4), range(5)):
        for word in product((0, 1), repeat=length):
            with patch('fp_reference.runtime.secrets.token_hex', return_value='owned-value-graph'):
                cc, program, online, _ = report_registration(unit=unit, count=4)
                with observed() as (owner, actual, kinds):
                    rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE)
                    for i, target in enumerate(word):
                        predicted = rt.predict_next(f'train/{i}', encode_context(()))
                        assert predicted.status == 'PREDICTED_REFERENCE'
                        # A public Origin is a detached wrapper, so changing it
                        # cannot invalidate a binding to an actual private one.
                        predicted.predictions[0][1].origin.__dict__['cursor'] = -99
                        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
                counts = graph_counts(owner)
                assert counts['expected_walk']['root_appends'] == actual['records']
                assert counts['expected_walk']['binding_inserts'] == counts['bindings']
                for source, root in owner.bindings.values():
                    recover(owner, root, source)
                if word == (0,)*length:
                    plain = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE)
                    for i, target in enumerate(word):
                        assert plain.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                        assert plain.observe(target).status == 'OBSERVED_REFERENCE'
                    assert encoding.pack(rt.snapshot()) == encoding.pack(plain.snapshot())
                    pairs += 1
                totals.update(actual)
                totals['histories'] += 1
                totals['targets'] += length
                totals['commits'] += length//unit
                totals['graph_page_bytes'] += counts['page_bytes']
                totals['graph_nodes'] += counts['nodes']
                totals['source_child_edges'] += owner.counts['source_child_edges']
    return dict(**totals, complete_observed_unobserved_snapshot_pairs=pairs,
        every_record_and_persistent_source_recovered=True, public_origin_mutations_isolated=True,
        default_runtime_archive_unchanged=True)


def full_vocabulary():
    from run_native_text_a1 import registration
    cc, program, online, storage, reporting = registration()
    with observed() as (owner, totals, kinds):
        rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage, reporting=reporting)
        initialized = graph_counts(owner)
        for i, target in enumerate((0, 1)):
            assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
    final = graph_counts(owner)
    assert len(online.data.active.observation_ids) == 1048576
    assert len(online.data.streams[1].observation_ids) == 16384
    assert final['bindings'] < 1 << 20
    assert len(owner.reader.nodes) < owner.limits.nodes
    # Rebuild all derived structures from retained page bytes, independently
    # of producer, source objects, source bindings and prior reader indices.
    rebuilt = model.Reader(owner.limits)
    for page in owner.reader.pages:
        rebuilt.add(page)
    assert rebuilt.nodes == owner.reader.nodes and rebuilt.metrics == owner.reader.metrics
    return dict(original_training_declaration=1048576, original_reporting_declaration=16384,
        vocabulary=50257, masters=603092, synthetic_targets=2,
        initialized_graph=initialized, final_graph=final, record_kinds=dict(kinds),
        **totals, complete_residency=complete_residency(rt), independent_page_only_rebuild=True,
        binding_cap=owner.limits.bindings, node_cap=owner.limits.nodes,
        full_manifest_and_original_values_admitted_in_passive_model=True,
        no_runtime_archive_replacement_or_resource_authority=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--small-only', action='store_true')
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions required')
    result = dict(status='PASS_OWNED_VALUE_GRAPH_MODEL', scope=__doc__.strip())
    actions = [('exact_values', exact_values), ('stability_boundary', stability_boundary),
               ('binding_eviction', binding_eviction),
               ('adversaries', adversaries), ('native_histories', native_histories)]
    if not args.small_only:
        actions.append(('full_vocabulary', full_vocabulary))
    for name, action in actions:
        result[name] = action()
        print('PASS '+name, flush=True)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
