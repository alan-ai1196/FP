"""Complete owned expression-retention controls; actual CPU tensors, no CUDA.

No corpus, device release, wall-time comparison or model-quality claim.
"""
from contextlib import nullcontext
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime, byte_terms as terms, encoding
from fp_reference.compositional_reference import _CompositionalReference
from fp_reference.shared_reference import (SharedPlannedObject, ROOT_BYTES, decoded_buffer,
                                          SharedReferenceContract, _SharedReference)
from fp_reference.resources import ObjectSpec, ResourceLedger, ResourceExceeded
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from audit_owned_token_learner import fixture, registration
from audit_reference_construction import limits, validate_residency
from audit_shared_token_retention import STORAGE


def contract(original=STORAGE, **kwargs):
    return replace(original, encoding=terms.ENCODING_ID,
        expression_nodes=1 << 20, expression_bindings=1 << 20, **kwargs)


def root():
    d, origin = fixture(2, 'mixed')
    cc, program, online = registration(d, origin)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    return ReferenceCompilerRuntime(cc, program, online=online, shared_storage=contract())


def retain(rt, value, label):
    identity = 'owned-expression-control:'+str(label)
    planned = SharedPlannedObject(ObjectSpec(identity, 'complete_expression_control',
        {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, rt._chi), value)
    rt._allocate(rt._data_owner, (planned,))
    return identity


def decode(snapshot, identity):
    cfg = snapshot.reference_archive.contract
    return b''.join(decoded_buffer(snapshot, identity, byte_cap=cfg.expanded_cap,
        reference_cap=cfg.reference_cap))


def reject(call, kinds=(ContractError, ResourceExceeded, RuntimeError, MemoryError)):
    try:
        call()
    except kinds:
        return
    raise AssertionError('invalid complete retention accepted')


@dataclass(frozen=True)
class Record:
    value: object


def components():
    rt = root()
    values = (None, True, False, -(1 << 129), F(-2, 3), b'', bytes(range(256))*33,
        '', '\ud800\U0001f600\ud83d\ude00\x00\x7f', 'z'*10000,
        (), [], {}, {2: b'v', 'x': [F(3, 7)]}, tuple(range(80)))
    old, count = [], 0
    for i, value in enumerate(values):
        # Native binding must not secretly expand previous expressions.
        with patch.object(terms.Reader, 'expand', side_effect=AssertionError('native binding expanded')):
            identity = retain(rt, value, i)
        snapshot = validate_residency(rt)
        raw = decode(snapshot, identity)
        assert raw == encoding.pack(value)
        old.append((snapshot, identity, raw))
        count += len(raw)
    mutable = Record([1])
    first = retain(rt, mutable, 'mutable-before')
    before = validate_residency(rt)
    mutable.value.append(2)
    mutable.__dict__['value'] = (2, 3)
    second = retain(rt, mutable, 'mutable-after')
    assert decode(before, first) != decode(validate_residency(rt), second)
    assert id(mutable) not in rt._reference_archive.bindings
    # Diagnostic contract and bindings must not write the owner's authority.
    public = rt.snapshot().reference_archive
    original = rt._reference_archive.contract
    public.contract.__dict__.update(encoding='forged', expression_bindings=0, comparison_cap=1)
    public.__dict__['expression_bindings'] = ((None, 1 << 63),)
    assert rt._reference_archive.contract == original and rt._reference_archive.contract is not public.contract
    identity = retain(rt, values[-1], 'after-snapshot')
    assert decode(validate_residency(rt), identity) == encoding.pack(values[-1])
    for snap, identity, raw in old:
        assert decode(snap, identity) == raw
    snapshot = validate_residency(rt)
    for identity in snapshot.reference_archive.pages+snapshot.reference_archive.workspaces:
        owners = snapshot.resources['objects'][identity]['references']
        assert {snapshot.resources['owners'][owner] for owner in owners} == {'compiler', 'deployment'}
    assert all(type(binding) is tuple for binding in snapshot.reference_archive.expression_bindings)
    expected_limits = replace(rt._reference_archive.reader.index.limits)
    rt._reference_archive.encoder.index.limits.__dict__.update(nodes=1 << 63, expanded=1 << 63)
    assert rt._reference_archive.reader.index.limits == expected_limits
    assert rt._reference_archive.reader.index.limits is not rt._reference_archive.encoder.index.limits
    return dict(typed_values=len(values), canonical_bytes=count, preserved_old_snapshots=len(old),
        mutable_fields_rewalked=True, public_binding_and_contract_substitution_isolated=True,
        pages_and_workspaces_owned_by_both_roles=True, native_binding_does_not_expand=True,
        producer_and_reader_limit_wrappers_isolated=True)


def grammar():
    limits = terms.Limits(page_bytes=1 << 16)
    producer = terms.Producer(limits)
    reader = terms.Reader(limits)
    roots, pages = [], []
    # Every binary word through length 5, including equal content constructed
    # from independent objects and forced checksum collisions.
    with patch.object(terms.zlib, 'crc32', return_value=0):
        bindings = {}
        for i, word in enumerate([()] + [w for n in range(1, 6) for w in product((0, 1), repeat=n)]):
            producer.begin(bytearray(limits.page_bytes))
            def handle(raw):
                return terms.U64.unpack(producer.send(raw))[0]
            emit = terms.Walk(lambda raw: handle(b'L'+raw),
                lambda a, b: handle(b'C'+terms.U64.pack(a)+terms.U64.pack(b)), bindings)
            proposed, _ = emit.value(word)
            producer.finish(terms.U64.pack(proposed))
            output = bytearray(producer.extent)
            producer.write(output)
            raw = bytes(output)
            actual = reader.add(raw)
            check = terms.Walk(reader.literal, reader.pair, bindings)
            expected, _ = check.value(word)
            assert expected == actual
            assert b''.join(reader.decoded(i, byte_cap=limits.expanded, reference_cap=limits.references)) == encoding.pack(word)
            bindings.update(check.proposals)
            roots.append(actual)
            pages.append(raw)
            producer.accept()
    # Every bit of the first nonempty tuple's page must preserve its exact
    # expected expression or refuse; variants are not all assumed invalid.
    accepted = refused = 0
    original = pages[1]
    for offset, bit in product(range(len(original)), range(8)):
        mutated = original[:offset]+bytes((original[offset] ^ (1 << bit),))+original[offset+1:]
        test = terms.Reader(limits)
        test.add(pages[0])
        try:
            actual = test.add(mutated)
            wanted, _ = terms.Walk(test.literal, test.pair, {}).value((0,))
            if actual != wanted:
                raise ContractError('changed expression root')
            assert b''.join(test.expand(actual)) == encoding.pack((0,))
            accepted += 1
        except (ContractError, ResourceExceeded):
            refused += 1
    # Unique-node bounds alone do not bound full recovery references.
    index = terms.Index(terms.Limits(references=4))
    a = index.add_literal(b'a')
    b = index.add_pair(a, a)
    c = index.add_pair(b, b)
    reject(lambda: index.add_pair(c, c), ResourceExceeded)
    limited = terms.Reader(limits)
    limited.add(pages[0])
    reject(lambda: list(limited.decoded(0, byte_cap=1, reference_cap=1)), ResourceExceeded)
    assert not list(terms.Reader(limits).roots)
    for changes in (dict(encoding='unknown'), dict(expression_nodes=0), dict(expression_bindings=0),
                    dict(reference_cap=1 << 64), dict(encoding=STORAGE.encoding)):
        reject(lambda: replace(contract(), **changes), ContractError)
    return dict(binary_words=len(pages), forced_collisions_exact=True,
        bit_variants_refused=refused, bit_variants_preserving_exact_expression=accepted,
        unfolded_reference_limit_independent_of_unique_nodes=True,
        invalid_registration_and_recovery_limits_refuse=True)


def extent_counterexample():
    # Reproduce the old materialization boundary, not an invented decoder.
    # The new term format's valid unused node makes unchanged recovery explicit.
    from fp_reference import shared_reference as shared
    source_commit = 'a4089cb'
    source = subprocess.check_output(['git', 'show', source_commit+':src/reference_compiler/fp_reference/shared_reference.py'],
        cwd=ROOT, text=True)
    declared = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == '_SharedReference')
    names = ('_materialize', '_scratch_releases')
    module = ast.Module(body=[n for n in declared.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
    namespace = dict(vars(shared))
    exec(compile(ast.fix_missing_locations(module), '<canonical unprotected copy boundary>', 'exec'), namespace)
    outcomes = []
    for legacy in (True, False):
        rt = root()
        owner, changed = rt._reference_archive, []
        original = owner.encoder.write
        def enlarged(output):
            original(output)
            header = list(terms.HEADER.unpack_from(output))
            header[3] += 1
            output.extend(b'L'+terms.U32.pack(7)+b'\xffresize')
            terms.HEADER.pack_into(output, 0, *header)
            changed.append(True)
        from contextlib import ExitStack
        with ExitStack() as stack:
            if legacy:
                for name in names:
                    stack.enter_context(patch.object(_SharedReference, name, namespace[name]))
            stack.enter_context(patch.object(owner.encoder, 'write', enlarged))
            if legacy:
                identity = retain(rt, (137, b'original'), 'resize-witness')
            else:
                reject(lambda: retain(rt, (137, b'original'), 'resize-witness'), BufferError)
        snap = rt.snapshot()
        if legacy:
            assert changed and snap.halted is None
            assert decode(snap, identity) == encoding.pack((137, b'original'))
            page = owner.pages[-1]
            paid = snap.resources['objects'][page]['residency']['reference_payload_bytes']
            actual = len(dict(snap.buffers)[page])
            assert actual == paid+12
            outcomes.append(dict(legacy_retention_accepted=True, decoded_record_equal=True,
                charged_page_bytes=paid, actual_page_bytes=actual))
        else:
            assert not changed and snap.halted
            validate_residency(rt)
            assert snap.reference_archive.fixed_copy_workspaces
    return dict(original_copy_source=source_commit, witness=outcomes[0],
        repaired_copy_refuses_resize_before_extent_changes=True)


def histories():
    import audit_owned_token_workspaces as owned
    cases = [(word, 2, False, False, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0), 1, False, False, False),
              ((0, 1, 1, 0)*2, 8, False, False, False),
              ((0, 1, 1, 0, 0, 1), 2, True, False, False),
              ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = total = words = calls = raw_bytes = 0
    for word, unit, profile, combined, archived in cases:
        rows = []
        for enabled in (False, True):
            context = patch.object(owned, 'STORAGE', contract(owned.STORAGE)) if enabled else nullcontext()
            with context, patch.object(owned, 'numerical_phase', encoding.pack):
                rows.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert rows[0] == rows[1], (word, unit, profile, combined)
        phases += len(rows[0]['phases'])
        total += sum(map(len, rows[0]['phases']))
        words += rows[0]['primitive_words']
        calls += rows[0]['raw_calls']
        raw_bytes += rows[0]['raw_bytes']
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        complete_phase_bytes=total, checked_primitive_words=words,
        identical_raw_calls=calls, identical_raw_bytes=raw_bytes,
        full_frames_learners_reports_profiles_and_arena_history_equal=True)


def frames_and_failures():
    from audit_shared_cuda_retention import add_frame
    # Original owned frames with deliberately nonzero tails, no GPU authority.
    rt, total = root(), 0
    for i, size in enumerate((4096, 8192, 32768)):
        label, value = add_frame(rt, i, size)
        original = bytes(rt._buffers[label])
        assert any(original[8+len(encoding.pack(value)):])
        rt._reference_archive.seal_cuda_frame(rt, label, value, role='deployment')
        assert decode(validate_residency(rt), label) == original
        total += size
    import audit_owned_token_workspaces as owned
    faults = ('literal', 'handle', 'page-copy', 'expected', 'accept', 'relocation', 'work',
              'binding-cap', 'reference-cap', 'output-resize', 'workspace-resize')
    outcomes = []
    for stage in ('native', 'frame'):
        for fault in faults:
            with owned.cpu_device(), patch.object(owned, 'STORAGE', contract(owned.STORAGE)):
                rt, _ = owned.setup(False, unit=4, count=4)
                assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
                before = rt.snapshot()
                archive = rt._reference_archive
                original_seal = archive.seal_cuda_frame
                if fault in ('literal', 'handle'):
                    original_send = archive.encoder.send
                    def send(message):
                        if fault == 'handle':
                            return 0
                        if message[:1] == b'L':
                            message = b'L'+bytes((message[1] ^ 1,))+message[2:]
                        return original_send(message)
                    hook = lambda: patch.object(archive.encoder, 'send', send)
                elif fault == 'page-copy':
                    write = archive.encoder.write
                    def corrupt(output):
                        write(output)
                        output[0] ^= 1
                    hook = lambda: patch.object(archive.encoder, 'write', corrupt)
                elif fault == 'output-resize':
                    hook = lambda: patch.object(archive.encoder, 'write', lambda output: output.extend(b'!'))
                elif fault == 'workspace-resize':
                    hook = lambda: patch.object(archive.encoder, 'send',
                        lambda message: archive.encoder.pending.extend(b'!'))
                elif fault == 'expected':
                    hook = lambda: patch.object(archive.reader, 'literal', side_effect=MemoryError('expected traversal'))
                elif fault == 'accept':
                    hook = lambda: patch.object(archive.encoder, 'accept', side_effect=MemoryError('publication'))
                elif fault == 'relocation':
                    hook = lambda: patch.object(rt._ledger, 'prepare_transfer', side_effect=MemoryError('relocation'))
                elif fault == 'work':
                    hook = lambda: patch.object(archive, '_charge', side_effect=ResourceExceeded('unpaid term work'))
                elif fault == 'binding-cap':
                    hook = lambda: patch.object(archive, 'contract', replace(archive.contract, expression_bindings=len(archive.bindings)))
                else:
                    cap = replace(archive.reader.index.limits, references=1)
                    hook = lambda: patch.object(archive.reader.index, 'limits', cap)
                # Native allocations have no frame relocation; exercise the
                # corresponding owned copy admission instead in that cell.
                if fault == 'relocation' and stage == 'native':
                    hook = lambda: patch.object(archive, '_materialize', side_effect=MemoryError('owned copy admission'))
                def seal(*args, **kwargs):
                    with hook():
                        return original_seal(*args, **kwargs)
                context = hook() if stage == 'native' else patch.object(archive, 'seal_cuda_frame', seal)
                with context:
                    try:
                        rt.observe(1)
                    except (ContractError, ResourceExceeded, RuntimeError, MemoryError, BufferError):
                        pass
                after = validate_residency(rt)
                assert after.halted and after.cursor == 0, (stage, fault)
                assert after.observations[-1].target == 1
                assert after.candidates[0].learner == before.candidates[0].learner
                assert after.cuda.current == before.cuda.current and after.cuda.predicted == before.cuda.predicted
                if stage == 'frame':
                    assert rt._cuda.arena._pins
                    failures = [v for v in after.resources['objects'].values() if v['kind'] == 'owned_cuda_phase_frame']
                    assert failures, fault
                reject(lambda: rt.predict_next('train/1', encode_context(())))
                outcomes.append(stage+':'+fault)
    return dict(nonzero_padding_frames=3, full_frame_bytes=total, post_target_faults=outcomes,
        actual_target_old_learner_and_failed_frame_pins_preserved=True)


def fresh_and_funding():
    from fp_reference import compositional_reference as implementation
    rt = root()
    with patch.object(implementation, 'bounded_packed_size', side_effect=AssertionError('unpaid source traversal')), \
            patch.object(rt._ledger, 'charge_work', side_effect=ResourceExceeded('unfunded')):
        reject(lambda: retain(rt, object(), 'unpaid'), ResourceExceeded)
    import audit_owned_token_workspaces as owned
    with owned.cpu_device(), patch.object(owned, 'STORAGE', contract(owned.STORAGE)):
        rt, _ = owned.setup(False, unit=4, count=4)
        owned.event(rt, 0, 0)
        before = rt.snapshot()
        resident = rt._cuda._values[rt._cuda.current[before.deployed_id]]
        live = resident.state.common.blocks[0].value
        assert bool(live.ne(0).any())
        live.zero_()
        reject(lambda: rt.predict_next('train/1', encode_context(())))
        after = validate_residency(rt)
        assert after.cursor == 1 and after.candidates[0].learner == before.candidates[0].learner
        assert after.cuda.phases[-1].status == 'EXECUTION_FAILED'
        assert 'changed after its owned phase' in after.cuda.phases[-1].reason
    return dict(body_unread_before_payment=True, changed_actual_live_tensor_refused=True,
        original_learner_and_cursor_preserved=True)


def audit():
    result = dict(components=components(), grammar=grammar(), extent_counterexample=extent_counterexample())
    print('PASS exact grammar, snapshots, mutable values and owned native retention', flush=True)
    result['histories'] = histories()
    print('PASS complete paired CPU Runtime histories', flush=True)
    result['failures'] = frames_and_failures()
    result['fresh_and_funding'] = fresh_and_funding()
    import torch
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_COMPOSITIONAL_REFERENCE_CPU', scope=__doc__.strip(), **result)


def full_v():
    from audit_shared_cuda_retention import full_registration
    from audit_owned_token_reuse import cpu_device
    cc, program, online, cfg, storage, origin, windows, targets, corpus = full_registration()
    cfg = replace(cfg, reuse_regions=True)
    storage = replace(storage, canonical_image_bytes=64 << 20, token_invariant_bytes=4 << 20)
    rows, bodies = [], []
    for enabled in (False, True):
        with cpu_device():
            rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg,
                shared_storage=contract(storage) if enabled else storage)
            for i, target in enumerate(targets[:2]):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            snapshot = validate_residency(rt)
        current = tuple(encoding.pack(p) for p in snapshot.cuda.phases)
        assert len(current) == 5
        for phase, expected in zip(snapshot.cuda.phases, current):
            raw = decode(snapshot, phase.object_id)
            count = int.from_bytes(raw[:8], 'big')
            assert len(raw) == cfg.phase_evidence_bytes and count == len(expected)
            assert raw[8:8+count] == expected and not any(raw[8+count:])
        bodies.append((current, snapshot.candidates[0].learner, rt._cuda.arena.snapshot()))
        archive = snapshot.reference_archive
        buffers = dict(snapshot.buffers)
        rows.append(dict(encoding=archive.contract.encoding, checked_phases=len(current),
            complete_phase_bytes=sum(map(len, current)),
            checked_primitive_words=sum(p.forward_operations for p in snapshot.cuda.phases),
            retained_pages=len(archive.pages), retained_page_bytes=sum(len(buffers[p]) for p in archive.pages),
            reference_peak=snapshot.resources['peak']['reference_payload_bytes'],
            source_bindings=len(archive.expression_bindings),
            term_nodes=len(rt._reference_archive.reader.index.nodes) if enabled else None))
        print('PASS full-V CPU complete frames: '+('expressions' if enabled else 'existing archive'), flush=True)
    assert bodies[0] == bodies[1]
    import torch
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_COMPOSITIONAL_REFERENCE_FULL_V_CPU', vocabulary=50257,
        masters=program.slot_count, original_targets=2, corpus=corpus, paths=rows,
        complete_bodies_learners_and_arena_histories_equal=True,
        all_original_frames_and_padding_checked=True,
        scope='complete CPU Runtime ownership qualification; no device or timing claim')


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('compositional owner audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--full-v', action='store_true')
    args = parser.parse_args()
    result = full_v() if args.full_v else audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        name = 'FP_COMPOSITIONAL_REFERENCE_FULL_V_CPU.json' if args.full_v else 'FP_COMPOSITIONAL_REFERENCE_CPU.json'
        (ROOT/'evidence/minimal'/name).write_text(body, encoding='utf-8')
    print(body)
