"""Exact shared-byte and actual native token-owner preservation controls.

No CUDA, corpus, architecture search, persistence, installation or model score.
"""
from dataclasses import replace
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from unittest.mock import patch
import argparse
import json
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference import byte_archive as byte
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.machine import PlannedObject
from fp_reference.profile import ProfileSpec
from fp_reference.resources import ResourceExceeded
from fp_reference.shared_reference import SharedReferenceContract, SharedPlannedObject, decoded_buffer, ROOT_KIND
from audit_owned_token_learner import fixture, registration, live
from audit_reference_construction import validate_residency, limits


STORAGE = SharedReferenceContract(1 << 20, 1 << 20, 1 << 20, 1 << 20, 4 << 20)


def rejects(fn, expected=ContractError):
    try:
        fn()
    except expected:
        return
    raise AssertionError('invalid archive operation accepted')


def raw_pages():
    encoder, reader = byte.Encoder(), byte.Reader()
    spaces = bytearray(1 << 16), bytearray(1 << 16), bytearray(1 << 16)
    originals, pages = [], []
    streams = ((bytes(range(256)), b'\x00'*8192, b'\x00\x00\x00\x80'),
               (b'prefix', bytes(range(256)), b'\x00'*8192, b'suffix'),
               (b'prefix', b'suffix', bytes(range(256))), (),
               (pack(('\U00010000', '\ud800\udc00', b'\x00\xff', F(7, 13), [True, None], {2: 'b', 1: 'a'})),))
    # Force every equal-length piece into the same checksum bucket. Distinct
    # bytes must still stay distinct, including across accepted pages.
    with patch.object(byte.zlib, 'crc32', return_value=0):
        streams += tuple((word, word[::-1], b'ab', b'ba') for word in (b'aa', b'ab', b'ba', b'bb'))
        for stream in streams:
            build = encoder.begin(*spaces, byte_cap=1 << 20, reference_cap=10000)
            rejects(lambda: encoder.begin(*spaces, byte_cap=1 << 20, reference_cap=10000))
            for part in stream:
                build.push(part)
            header = build.finish()
            output = bytearray(build.extent)
            build.write(output)
            rejects(lambda: build.write(output))
            raw = bytes(output)
            reader.add(raw)
            encoder.add(raw)
            pages.append(raw)
            originals.append(b''.join(stream))
            assert b''.join(reader.decoded(header.ordinal, byte_cap=1 << 20, reference_cap=10000)) == originals[-1]
    # Rebuild from retained bytes alone, after discarding producer indices and
    # overwriting every old mutable workspace/output buffer.
    for space in spaces:
        space[:] = b'\xff'*len(space)
    output[:] = b'\xff'*len(output)
    fresh = byte.Reader()
    for raw in pages:
        fresh.add(raw)
    for i, wanted in enumerate(originals):
        assert b''.join(fresh.decoded(i, byte_cap=1 << 20, reference_cap=10000)) == wanted
    rejects(lambda: list(fresh.decoded(0, byte_cap=1, reference_cap=10000)), ResourceExceeded)
    rejects(lambda: list(fresh.decoded(0, byte_cap=1 << 20, reference_cap=1)), ResourceExceeded)
    rejects(lambda: byte.Reader().add(pages[1]))
    rejects(lambda: byte.Reader().add(pages[0][:-1]))
    # Valid zlib/checksum, deliberately undefined future reference. Adding
    # more pages must not retroactively make the forged old root admissible.
    head = byte._page(pages[0])
    forged_program = zlib.compress(byte.U64.pack(head.pieces))
    forged = byte.HEADER.pack(byte.MAGIC, 0, 0, head.pieces, 1, 1,
                              head.literal_bytes, len(forged_program))
    forged += pages[0][byte.HEADER.size:byte.HEADER.size+head.literal_bytes]+forged_program
    corrupt = byte.Reader()
    corrupt.add(forged)
    for raw in pages[1:]:
        corrupt.add(raw)
    rejects(lambda: list(corrupt.decoded(0, byte_cap=1 << 20, reference_cap=10000)))
    # Paid collision comparison exhaustion is a resource refusal, not equality.
    e = byte.Encoder()
    b = e.begin(*spaces, byte_cap=1024, reference_cap=100, comparison_cap=1)
    with patch.object(byte.zlib, 'crc32', return_value=0):
        b.push(b'ab')
        rejects(lambda: b.push(b'ba'), ResourceExceeded)
    return dict(pages=len(pages), expanded_bytes=sum(map(len, originals)),
                retained_bytes=sum(map(len, pages)), checksum_collisions_preserve_bytes=True,
                independent_reader_and_old_snapshots=True, future_references_refused=True)


def trajectories():
    histories = events = profiles = roots = expanded = stored = 0
    for unit, word in product((1, 2, 4), ((0, 1, 0, 1, 1, 0, 1, 0), (1, 1, 0, 0, 0, 1, 0, 1))):
        d, initial = fixture(unit, 'mixed')
        profile = ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2)
        cfg, program, online = registration(d, initial, count=8, profiles=(profile,))
        cfg = replace(cfg, limits=limits(128 << 20, 10**14))
        expected, old_snapshots = {}, []
        original = ReferenceCompilerRuntime._allocate
        def record(rt, owner, objects):
            for obj in objects:
                if type(obj) in (PlannedObject, SharedPlannedObject) and obj.spec.kind != 'reserved_target':
                    expected[obj.spec.object_id] = pack(obj.value)
            return original(rt, owner, objects)
        legacy = ReferenceCompilerRuntime(cfg, program, online=online)
        with patch.object(ReferenceCompilerRuntime, '_allocate', record):
            shared = ReferenceCompilerRuntime(cfg, program, online=online, shared_storage=STORAGE)
            for t, target in enumerate(word):
                for runtime in (legacy, shared):
                    assert runtime.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
                    assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
                if t == 3:
                    old_snapshots.append(shared.snapshot())
                    for runtime in (legacy, shared):
                        assert runtime.construct_candidate(program, profile_id='reverse-repeat').status == 'BUILT_REFERENCE'
                a, b = validate_residency(legacy), validate_residency(shared)
                assert tuple(c.learner for c in a.candidates) == tuple(c.learner for c in b.candidates)
                assert tuple(r.sources for r in a.observations) == tuple(r.sources for r in b.observations)
            old_snapshots.append(shared.snapshot())
        events += len(shared.snapshot().event_traces)
        for snapshot in old_snapshots:
            buffers = dict(snapshot.buffers)
            for identity, entry in snapshot.resources['objects'].items():
                if entry['kind'].startswith(ROOT_KIND):
                    wanted = expected[identity]
                    decoded = b''.join(decoded_buffer(snapshot, identity,
                        byte_cap=STORAGE.expanded_cap, reference_cap=STORAGE.reference_cap))
                    assert decoded == wanted
                    roots += 1
                    expanded += len(wanted)
                if entry['kind'] in ('immutable_shared_reference_page', 'shared_reference_workspace'):
                    roles = {snapshot.resources['owners'][owner] for owner in entry['references']}
                    assert roles == {'compiler', 'deployment'}
            assert all(buffers[k] == dict(shared.snapshot().buffers)[k]
                       for k in snapshot.reference_archive.pages)
        profiles += len(shared.snapshot().profile_events)
        stored += sum(len(dict(shared.snapshot().buffers)[p]) for p in shared.snapshot().reference_archive.pages)
        histories += 1
    return dict(histories=histories, candidate_observations=events, profile_events=profiles,
                complete_roots_compared=roots, decoded_bytes_compared=expanded,
                final_page_bytes=stored, both_dependency_roles_charged=True)


def failures():
    d, initial = fixture(2, 'mixed')
    cfg, program, online = registration(d, initial)
    cfg = replace(cfg, limits=limits(128 << 20, 10**14))
    failures = 0
    for mode in ('changed-output', 'copy-quota', 'page-quota', 'page-write', 'dependency-quota', 'work-quota'):
        rt = ReferenceCompilerRuntime(cfg, program, online=online, shared_storage=STORAGE)
        assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        before, prefix = live(rt.snapshot()), rt._reference_archive.snapshot()
        if mode == 'changed-output':
            original = byte.Builder.push
            def changed(self, part):
                return original(self, bytes((part[0] ^ 1,))+part[1:])
            hook = patch.object(byte.Builder, 'push', changed)
        elif mode in ('copy-quota', 'page-quota'):
            original = rt._ledger.allocate
            def denied(owner, objects, **kw):
                kind = 'shared_reference_copy_workspace' if mode == 'copy-quota' else 'immutable_shared_reference_page'
                if any(obj.kind == kind for obj in objects):
                    raise ResourceExceeded('registered retained-page refusal control')
                return original(owner, objects, **kw)
            hook = patch.object(rt._ledger, 'allocate', denied)
        elif mode == 'dependency-quota':
            original = rt._ledger.acquire
            def denied(owner, identity, **kw):
                if identity.endswith(':copy'):
                    raise ResourceExceeded('registered deployment dependency refusal control')
                return original(owner, identity, **kw)
            hook = patch.object(rt._ledger, 'acquire', denied)
        elif mode == 'work-quota':
            original = rt._ledger.charge_work
            def denied(role, debit, **kw):
                if kw.get('note', '').endswith(':shared-reference'):
                    raise ResourceExceeded('registered archive work refusal control')
                return original(role, debit, **kw)
            hook = patch.object(rt._ledger, 'charge_work', denied)
        else:
            hook = patch.object(byte.Builder, 'write', side_effect=RuntimeError('page writer fault'))
        with hook:
            if mode in ('changed-output', 'page-write'):
                rejects(lambda: rt.observe(1), (ContractError, RuntimeError))
            else:
                assert rt.observe(1).status == 'UNRESOLVED'
        snap = validate_residency(rt)
        assert snap.halted and snap.cursor == 0 and live(snap) == before
        assert snap.observations[-1].target == 1 and snap.observations[-1].sources.position == 0
        assert rt._reference_archive.snapshot().pages == prefix.pages
        assert snap.event_traces[-1].after_observe.targets == (1,)
        failures += 1
    return dict(post_target_failures=failures, targets_and_old_learners_retained=True)


def funding_boundary():
    import fp_reference.runtime as implementation
    import fp_reference.shared_reference as shared
    d, initial = fixture(2, 'mixed')
    cfg, program, online = registration(d, initial)
    rt = ReferenceCompilerRuntime(cfg, program, online=online, shared_storage=STORAGE)
    # Even inspecting the shape of this deliberately unsupported body is
    # forbidden before payment. This is a private allocation-boundary attack,
    # not a public way of submitting arbitrary state to Runtime.
    with patch.object(implementation, 'packed_size', side_effect=AssertionError('unpaid old size traversal')), \
         patch.object(shared, 'bounded_packed_size', side_effect=AssertionError('unpaid archive traversal')), \
         patch.object(rt._ledger, 'charge_work', side_effect=ResourceExceeded('no paid work')):
        plan = rt._machine.realize('funding-control', 'reference-record', object(), rt._chi)
        rejects(lambda: rt._allocate(rt._data_owner, (plan,)), ResourceExceeded)
    return dict(body_unread_before_work_refusal=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_EXACT_SHARED_NATIVE_TOKEN_RETENTION',
        scope='byte preservation and actual native event/profile ownership; no CUDA retention or install release',
        bytes=raw_pages(), runtime=trajectories(), failures=failures(), planning=funding_boundary())
    assert 'torch' not in sys.modules
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_SHARED_TOKEN_RETENTION_CPU.json').write_text(body, encoding='utf-8')
    print(body)
