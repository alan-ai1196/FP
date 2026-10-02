"""Owned typed-value retention: exact native and CPU-tensor Runtime controls.

No corpus, timing experiment, actual CUDA claim or trained score. Every
retained native value and actual original frame keeps its complete oracle.
"""
from collections import Counter, OrderedDict
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler'),
               str(ROOT/'theory/numerical_checks')]
from fp_reference import ReferenceCompilerRuntime, encoding, value_graph as graph
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded, ObjectSpec
from fp_reference.shared_reference import SharedPlannedObject, ROOT_BYTES, decoded_buffer, _compare_stream
from fp_reference.value_graph_reference import _ValueGraphReference
from audit_shared_token_retention import STORAGE
from audit_token_reporting import report_registration
from audit_reference_construction import validate_residency, limits
from run_native_text_a1 import complete_residency


def contract(original=STORAGE, *, memo=128):
    return replace(original, encoding=graph.ENCODING_ID,
        expression_nodes=1 << 22, expression_bindings=memo)


def setup(unit=2, count=4, memo=128):
    cc, program, online, reporting = report_registration(unit, count, 2)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    return ReferenceCompilerRuntime(cc, program, online=online,
        shared_storage=contract(memo=memo), reporting=reporting)


def event(rt, i, target):
    predicted = rt.predict_next(f'train/{i}', encode_context(()))
    assert predicted.status == 'PREDICTED_REFERENCE'
    # Exercise the actual public isolation boundary, not a claimed flag.
    predicted.predictions[0][1].origin.__dict__['cursor'] = -99
    assert rt.observe(target).status == 'OBSERVED_REFERENCE'


def decode(snapshot, identity):
    cfg = snapshot.reference_archive.contract
    return b''.join(decoded_buffer(snapshot, identity, byte_cap=cfg.expanded_cap,
        reference_cap=cfg.reference_cap))


def refuse(call, types=(ContractError, ResourceExceeded, MemoryError, RuntimeError, BufferError)):
    try:
        call()
    except types:
        return
    raise AssertionError('invalid owned retention accepted')


def retain(rt, value, label):
    identity = 'value-graph-control:'+str(label)
    rt._allocate(rt._data_owner, (SharedPlannedObject(ObjectSpec(identity, 'value_graph_control',
        {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, rt._chi), value),))
    return identity


@contextmanager
def observed(*, clear=False):
    allocate, accept = _ValueGraphReference.allocate, _ValueGraphReference._accept
    counts = Counter()
    def publication(owner, *args):
        pages, bindings = owner.pages, owner.bindings
        old = set(bindings)
        result = accept(owner, *args)
        assert owner.pages is pages and owner.bindings is bindings
        assert len(bindings) <= owner.contract.expression_bindings
        counts['facts_evicted'] += len(old-set(bindings))
        return result
    def checked(owner, rt, role, planned):
        if clear:
            owner.bindings.clear()
        result = allocate(owner, rt, role, planned)
        root = owner.reader.roots[-1]
        size = owner.reader.metrics[root].size
        _compare_stream(owner.reader.expanded(root, byte_cap=owner.contract.expanded_cap,
            visit_cap=owner.contract.reference_cap),
            (s.encode('utf-8', 'surrogatepass') for s in encoding.fragments(planned.value, packed=True)), size)
        assert size == encoding.bounded_packed_size(planned.value,
            byte_limit=owner.contract.expanded_cap, integer_bits=rt._contract.reference_integer_bits)
        counts['native_records'] += 1
        counts['canonical_bytes'] += size
        counts['memo_peak'] = max(counts['memo_peak'], len(owner.bindings))
        return result
    with patch.object(_ValueGraphReference, 'allocate', checked), patch.object(_ValueGraphReference, '_accept', publication):
        yield counts


def components():
    from audit_owned_value_graph import samples
    rt, decoded, saved = setup(memo=4), 0, []
    for i, value in enumerate(samples()):
        with patch.object(graph.Reader, 'expanded', side_effect=AssertionError('native retention expanded old data')):
            identity = retain(rt, value, i)
        snapshot = validate_residency(rt)
        raw = decode(snapshot, identity)
        assert raw == encoding.pack(value)
        decoded += len(raw)
        if i in (0, 17, 98):
            saved.append((snapshot, identity, raw))
        assert len(rt._reference_archive.bindings) <= 4
    @dataclass(frozen=True)
    class Mutable:
        value: object
    value = Mutable([1])
    first = retain(rt, value, 'mutable-before')
    old = rt.snapshot()
    value.__dict__['value'] = (2, 3)
    second = retain(rt, value, 'mutable-after')
    assert decode(old, first) != decode(rt.snapshot(), second)
    assert id(value) not in rt._reference_archive.bindings
    public = rt.snapshot().reference_archive
    original = replace(rt._reference_archive.contract)
    public.contract.__dict__.update(encoding='forged', expression_bindings=0)
    for source, _ in public.expression_bindings:
        if hasattr(source, '__dict__'):
            source.__dict__.clear()
    assert rt._reference_archive.contract == original
    event(rt, 0, 0)
    for snapshot, identity, raw in saved:
        assert decode(snapshot, identity) == raw
    current = validate_residency(rt)
    for identity in current.reference_archive.pages+current.reference_archive.workspaces:
        owners = current.resources['objects'][identity]['references']
        assert {current.resources['owners'][key] for key in owners} == {'compiler', 'deployment'}
    return dict(typed_values=len(samples()), canonical_bytes=decoded, memo_cap=4,
        complete_old_snapshots=len(saved), public_sources_and_contract_isolated=True,
        mutable_wrappers_rechecked=True, pages_workspaces_and_live_buffers_paid=True,
        no_complete_expansion_during_native_binding=True)


def grammar():
    def page(producer, value, bindings):
        producer.begin(bytearray(producer.limits.page_bytes))
        walk = graph._OwnedWalk(lambda raw: graph.U64.unpack(producer.send(raw))[0], bindings, producer.limits)
        root, _ = walk.value(value)
        producer.finish(graph.U64.pack(root))
        output = bytearray(producer.extent)
        producer.write(output)
        producer.accept()
        return bytes(output)
    limits = graph.Limits(page_bytes=1 << 16, comparisons=1 << 26, bindings=4)
    producer, reader, pages = graph.Producer(limits), graph.Reader(limits), []
    words = [()] + [word for n in range(1, 6) for word in product((0, 1), repeat=n)]
    with patch.object(graph.zlib, 'crc32', return_value=0):
        for word in words:
            raw = page(producer, word, {})
            root = reader.add(raw)
            expected, _ = graph._OwnedWalk(reader.find, {}, limits).value(word)
            assert expected == root
            assert b''.join(reader.decoded(len(pages), byte_cap=limits.expanded,
                reference_cap=limits.references)) == encoding.pack(word)
            pages.append(raw)
    refused = accepted = 0
    for offset, bit in product(range(len(pages[1])), range(8)):
        raw = bytearray(pages[1])
        raw[offset] ^= 1 << bit
        reader = graph.Reader(limits)
        reader.add(pages[0])
        try:
            root = reader.add(bytes(raw))
            expected, _ = graph._OwnedWalk(reader.find, {}, limits).value((0,))
            if root != expected:
                raise ContractError('wrong root')
        except (ContractError, ResourceExceeded):
            refused += 1
        else:
            assert b''.join(reader.expanded(root, byte_cap=1000, visit_cap=1000)) == encoding.pack((0,))
            accepted += 1
    # Empty raw strings still require an unfolded-reference guard.
    limits = replace(limits, references=7)
    producer, reader = graph.Producer(limits), graph.Reader(limits)
    producer.begin(bytearray(limits.page_bytes))
    emit = lambda raw: graph.U64.unpack(producer.send(raw))[0]
    node = emit(b'b')
    for _ in range(3):
        node = emit(graph.vector(b'x', (node, node)))
    producer.finish(graph.U64.pack(node))
    output = bytearray(producer.extent)
    producer.write(output)
    refuse(lambda: reader.add(bytes(output)), ResourceExceeded)
    for changes in (dict(expression_nodes=0), dict(expression_bindings=0),
                    dict(reference_cap=1 << 64), dict(encoding='unknown')):
        refuse(lambda: replace(contract(), **changes), ContractError)
    # Valid unused captures expose why per-node reference bounds alone do
    # not fund aggregate semantic parsing. This is a necessity control, not
    # a claim that an earlier committed Runtime accepted this page.
    limits = graph.Limits(page_bytes=1 << 16, references=128)
    producer = graph.Producer(limits)
    producer.begin(bytearray(limits.page_bytes))
    emit = lambda raw: graph.U64.unpack(producer.send(raw))[0]
    zero, data, width, grid = (emit(raw) for raw in (b'i0', b'b'+b'\0'*32, b'i8', b'i4'))
    past = emit(graph.vector(b'u', (zero,)*4))
    for i in range(5):
        tail = emit(graph.vector(b'u', (emit(b'q'+format(i, 'x').encode()+b'/1'),)))
        emit(graph.vector(b'c', (data, width, past, grid, tail)))
    producer.finish(graph.U64.pack(zero))
    output = bytearray(producer.extent)
    producer.write(output)
    class Unmetered(graph.Reader):
        def _semantic_debit(self, count):
            self.semantic_work += count
    unmetered = Unmetered(limits)
    unmetered.add(bytes(output))
    assert max(unmetered.references) <= limits.references
    assert unmetered.references[zero] == 1 and unmetered.semantic_work == 215
    metered = graph.Reader(limits)
    refuse(lambda: metered.add(bytes(output)), ResourceExceeded)
    assert metered.semantic_work <= limits.references and not metered.roots
    return dict(binary_words=len(words), forced_crc_collisions_checked_by_full_equality=True,
        bit_variants_refused=refused, bit_variants_with_exact_value=accepted,
        zero_byte_raw_graph_still_bounded_by_unfolded_references=True,
        unused_capture_necessity_control=dict(root_references=1, maximum_node_references=max(unmetered.references),
            page_semantic_work_without_meter=unmetered.semantic_work, reference_allowance=128,
            actual_parser_refuses_before_exceeding_aggregate_allowance=True),
        malformed_registrations_refused=True)


def native_histories():
    total, pairs = Counter(), 0
    for unit, length in product((1, 2, 4), range(5)):
        for word in product((0, 1), repeat=length):
            with patch('fp_reference.runtime.secrets.token_hex', return_value='owned-value-graph-runtime'):
                with observed() as counts:
                    rt = setup(unit, 4, memo=32)
                    for i, target in enumerate(word):
                        event(rt, i, target)
                cc, program, online, reporting = report_registration(unit, 4, 2)
                plain = ReferenceCompilerRuntime(cc, program, online=online,
                    reporting=reporting, shared_storage=STORAGE)
                for i, target in enumerate(word):
                    event(plain, i, target)
                a, b = validate_residency(rt), validate_residency(plain)
                for name in ('observations', 'event_traces', 'pending', 'cursor', 'data_uses'):
                    assert encoding.pack(getattr(a, name)) == encoding.pack(getattr(b, name)), name
                assert a.candidates[0].learner == b.candidates[0].learner
                total.update({key: counts[key] for key in ('native_records', 'canonical_bytes', 'facts_evicted')})
                total['histories'] += 1
                total['targets'] += length
                total['commits'] += length//unit
                if word == (0,)*length:
                    with observed(clear=True):
                        cold = setup(unit, 4, memo=32)
                        for i, target in enumerate(word):
                            event(cold, i, target)
                    warm_pages = tuple(rt._buffers[key] for key in rt._reference_archive.pages)
                    cold_pages = tuple(cold._buffers[key] for key in cold._reference_archive.pages)
                    assert warm_pages == cold_pages
                    assert cold._candidates[cold._deployed_id].learner == a.candidates[0].learner
                    pairs += 1
    return dict(**total, memo_cap=32, memo_eviction_page_identity_pairs=pairs,
        all_sources_traces_targets_and_learners_equal_to_existing_archive=True,
        every_new_native_record_fully_recovered=True)


def tensor_histories():
    import audit_owned_token_workspaces as owned
    cases = [(word, 2, False, False, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0), 1, False, False, False),
              ((0, 1, 1, 0)*2, 8, False, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False, False),
              ((0, 1, 1, 0)*2, 4, False, True, True)]
    totals = Counter()
    for word, unit, profile, combined, archived in cases:
        rows = []
        for graph_enabled in (False, True):
            context = patch.object(owned, 'STORAGE', contract(owned.STORAGE, memo=32)) if graph_enabled else nullcontext()
            with context, patch.object(owned, 'numerical_phase', encoding.pack):
                rows.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert rows[0] == rows[1], (word, unit, profile, combined)
        totals['phases'] += len(rows[0]['phases'])
        totals['body_bytes'] += sum(map(len, rows[0]['phases']))
        for key in ('primitive_words', 'raw_calls', 'raw_bytes'):
            totals[key] += rows[0][key]
        totals['independently_recovered_body_bytes'] += rows[0]['frame_bytes']
        # The reused helper calls its body count frame_bytes. Keep the actual
        # registered complete frame extent as a separate, correctly named sum.
        from audit_token_cuda_owner import FRAME
        totals['registered_complete_frame_bytes'] += len(rows[0]['phases'])*FRAME
    return dict(pairs=len(cases), **totals,
        complete_frames_reports_profiles_native_learners_and_arena_histories_equal=True)


def failure_prefixes():
    from audit_shared_cuda_retention import add_frame
    rt, frame_bytes = setup(), 0
    for i, size in enumerate((4096, 8192, 32768)):
        label, value = add_frame(rt, i, size)
        raw = bytes(rt._buffers[label])
        assert any(raw[8+len(encoding.pack(value)):])
        rt._reference_archive.seal_cuda_frame(rt, label, value, role='deployment')
        assert decode(validate_residency(rt), label) == raw
        frame_bytes += size
    import audit_owned_token_workspaces as owned
    failures = []
    names = ('message', 'handle', 'page-copy', 'output-resize', 'workspace-resize',
             'expected', 'accept', 'relocation', 'work', 'references', 'partial-memo')
    for stage, name in product(('native', 'frame'), names):
        with owned.cpu_device(), patch.object(owned, 'STORAGE', contract(owned.STORAGE, memo=32)):
            rt, _ = owned.setup(False, unit=4, count=4)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            before, owner = rt.snapshot(), rt._reference_archive
            send, write, seal = owner.encoder.send, owner.encoder.write, owner.seal_cuda_frame
            if name == 'message':
                hook = lambda: patch.object(owner.encoder, 'send',
                    lambda raw: send(raw+b'!' if raw[:1] == b's' else raw))
            elif name == 'handle':
                hook = lambda: patch.object(owner.encoder, 'send', return_value=0)
            elif name == 'page-copy':
                def corrupt(output):
                    write(output)
                    output[0] ^= 1
                hook = lambda: patch.object(owner.encoder, 'write', corrupt)
            elif name == 'output-resize':
                hook = lambda: patch.object(owner.encoder, 'write', lambda output: output.extend(b'!'))
            elif name == 'workspace-resize':
                hook = lambda: patch.object(owner.encoder, 'send', lambda raw: owner.encoder.pending.extend(b'!'))
            elif name == 'expected':
                hook = lambda: patch.object(owner.reader, 'find', side_effect=MemoryError('expected binding'))
            elif name == 'accept':
                hook = lambda: patch.object(owner.encoder, 'accept', side_effect=MemoryError('accept'))
            elif name == 'relocation':
                hook = (lambda: patch.object(rt._ledger, 'prepare_transfer', side_effect=MemoryError('relocation'))) \
                    if stage == 'frame' else (lambda: patch.object(owner, '_materialize', side_effect=MemoryError('copy')))
            elif name == 'work':
                hook = lambda: patch.object(owner, '_charge', side_effect=ResourceExceeded('unpaid'))
            elif name == 'references':
                hook = lambda: patch.object(owner.reader, 'limits', replace(owner.reader.limits, references=1))
            else:
                class FailingMemo(OrderedDict):
                    def __setitem__(self, key, value):
                        super().__setitem__(key, value)
                        if self.fail:
                            raise MemoryError('after a checked memo insertion')
                memo = FailingMemo()
                memo.fail = False
                memo.update(owner.bindings)
                memo.fail = True
                hook = lambda: patch.object(owner, 'bindings', memo)
            def failed_seal(*args, **kwargs):
                with hook():
                    return seal(*args, **kwargs)
            context = hook() if stage == 'native' else patch.object(owner, 'seal_cuda_frame', failed_seal)
            with context:
                try:
                    rt.observe(1)
                except (ContractError, ResourceExceeded, RuntimeError, MemoryError, BufferError):
                    pass
            after = validate_residency(rt)
            assert after.halted and after.cursor == 0, (stage, name)
            assert after.observations[-1].target == 1
            assert after.candidates[0].learner == before.candidates[0].learner
            assert after.cuda.current == before.cuda.current and after.cuda.predicted == before.cuda.predicted
            if stage == 'frame':
                assert rt._cuda.arena._pins
                assert any(row['kind'] == 'owned_cuda_phase_frame' for row in after.resources['objects'].values())
            refuse(lambda: rt.predict_next('train/1', encode_context(())))
            failures.append(stage+':'+name)
    return dict(nonzero_padding_frames=3, frame_bytes=frame_bytes,
        post_target_failures=failures, paid_actual_prefix_target_old_learner_and_frame_pins_preserved=True)


def funding_and_freshness():
    import fp_reference.value_graph_reference as implementation
    rt = setup()
    with patch.object(implementation, 'bounded_packed_size', side_effect=AssertionError('unpaid source walk')), \
            patch.object(rt._ledger, 'charge_work', side_effect=ResourceExceeded('unfunded')):
        refuse(lambda: retain(rt, object(), 'unpaid'), ResourceExceeded)
    import audit_owned_token_workspaces as owned
    with owned.cpu_device(), patch.object(owned, 'STORAGE', contract(owned.STORAGE)):
        rt, _ = owned.setup(False, unit=4, count=4)
        owned.event(rt, 0, 0)
        before = rt.snapshot()
        resident = rt._cuda._values[rt._cuda.current[before.deployed_id]]
        resident.state.common.blocks[0].value.zero_()
        refuse(lambda: rt.predict_next('train/1', encode_context(())))
        after = validate_residency(rt)
        assert after.cursor == 1 and after.candidates[0].learner == before.candidates[0].learner
        assert after.cuda.phases[-1].status == 'EXECUTION_FAILED'
        assert 'changed after its owned phase' in after.cuda.phases[-1].reason
    return dict(unpaid_body_not_read=True, actual_changed_tensor_refuses=True,
        previous_learner_and_cursor_preserved=True)


def full_native():
    from run_native_text_a1 import registration
    cc, program, online, storage, reporting = registration()
    with observed() as counts:
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            shared_storage=contract(storage, memo=8192))
        initial = len(rt._reference_archive.reader.nodes), sum(len(rt._buffers[p]) for p in rt._reference_archive.pages)
        for i, target in enumerate((0, 1)):
            event(rt, i, target)
    archive = rt._reference_archive
    complete = complete_residency(rt)
    final = len(archive.reader.nodes), sum(len(rt._buffers[p]) for p in archive.pages)
    return dict(original_train=1048576, original_report=16384, vocabulary=50257, masters=603092,
        synthetic_targets=2, memo_cap=8192, memo_entries=len(archive.bindings),
        initial_nodes=initial[0], initial_page_bytes=initial[1],
        additional_nodes=final[0]-initial[0], additional_page_bytes=final[1]-initial[1],
        actual_native_canonical_checks=dict(counts), residency=complete,
        canonical_images_created=len(archive.images.entries),
        owned_base_fact_retained=archive.base_facts is not None,
        no_full_host_timing_or_model_result=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--full-native', action='store_true')
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions required')
    result = dict(status='PASS_OWNED_VALUE_GRAPH_RUNTIME_CPU', scope=__doc__.strip())
    actions = [('full_native', full_native)] if args.full_native else [
        ('components', components), ('grammar', grammar), ('native_histories', native_histories),
        ('tensor_histories', tensor_histories), ('failure_prefixes', failure_prefixes),
        ('funding_and_freshness', funding_and_freshness)]
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
