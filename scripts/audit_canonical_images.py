"""Owned immutable-image controls and a paired CPU full-V prefix diagnostic.

All archive decodings are compared with uncached canonical bytes. Device
substitution carries no physical authority. No terminal GPU job is replayed.
"""
from contextlib import contextmanager
from dataclasses import dataclass, replace
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference import runtime as runtime_module
from fp_reference import encoding, byte_archive
from fp_reference.canonical_images import _CanonicalImages, MIN_IMAGE
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from fp_reference.resources import ObjectSpec, ResourceExceeded
from fp_reference.shared_reference import _SharedReference, SharedPlannedObject, ROOT_BYTES, decoded_buffer
from audit_shared_token_retention import STORAGE
from audit_owned_token_learner import fixture, registration
from audit_reference_construction import limits, validate_residency
from audit_token_snapshot_bounds import cpu_device
from audit_token_cuda_owner import cuda_contract


@dataclass(frozen=True)
class Wrapper:
    value: object


def root(cap=1 << 20, cuda=False):
    d, initial = fixture(2, 'mixed')
    cc, program, online = registration(d, initial)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    return ReferenceCompilerRuntime(cc, program, online=online,
        shared_storage=replace(STORAGE, canonical_image_bytes=cap),
        cuda=cuda_contract(cc.initializer_pattern) if cuda else None)


def retain(rt, value, index):
    identity = f'canonical-image-control:{index}'
    obj = SharedPlannedObject(ObjectSpec(identity, 'canonical_image_control',
        {'reference_payload_bytes': ROOT_BYTES, 'physical_objects': 1}, rt._chi), value)
    rt._allocate(rt._data_owner, (obj,))
    snapshot = validate_residency(rt)
    decoded = b''.join(decoded_buffer(snapshot, identity,
        byte_cap=STORAGE.expanded_cap, reference_cap=STORAGE.reference_cap))
    assert decoded == encoding.pack(value)
    return snapshot, identity, decoded


def outcome(function):
    try:
        return ('VALUE', function())
    except (ContractError, ResourceExceeded) as error:
        return ('REFUSED', type(error).__name__)


def component():
    rt = root()
    values = (bytes(range(256))*41, ('a\x00\x7f\ud800\U0001f600\ud83d\ude00"\\'*1700),
        (F(1, 3),)*512, tuple(range(-256, 256)), (1 << 32767),
        ((F(-1, 1 << 129),)*320, (b'\0\xff'*5000,)))
    archive_bytes = limit_checks = 0
    old = []
    for i, value in enumerate(values):
        snapshot, identity, raw = retain(rt, value, i)
        old.append((snapshot, identity, raw))
        archive_bytes += len(raw)
        image = rt._reference_archive.images.find(value)
        assert image is not None and image.source is value
        assert image.size == encoding.packed_size(value)
        assert ''.join(rt._reference_archive.images.fragments(image)).encode('utf-8', 'surrogatepass') == raw
        for subject in (value, [None, (value,)], Wrapper({'source': value})):
            size = encoding.packed_size(subject)
            for byte_cap in (1, image.traversal, max(1, size-1), size, size+1):
                for depth in (1, 2, 4, 64):
                    for bits in (1, 128, 129, 32767, 32768):
                        kwargs = dict(byte_limit=byte_cap, depth_limit=depth, integer_bits=bits)
                        a = outcome(lambda: encoding.bounded_packed_size(subject, **kwargs))
                        b = outcome(lambda: encoding.bounded_packed_size(subject, images=rt._reference_archive.images, **kwargs))
                        assert a == b, (i, kwargs, a, b)
                        limit_checks += 1
    producer = {'data': values[0]}
    mutable = [values[2]]
    wrapper = Wrapper((mutable, MappingProxyType(producer)))
    snap, identity, raw = retain(rt, wrapper, 'mutable-before')
    assert all(rt._reference_archive.images.find(v) is None for v in (wrapper, wrapper.value, mutable, wrapper.value[1]))
    producer['data'] = b'CHANGED'+values[0]
    mutable.append(values[3])
    _, _, changed = retain(rt, wrapper, 'mutable-after')
    assert changed != raw
    old.append((snap, identity, raw))
    for snapshot, identity, raw in old:
        assert b''.join(decoded_buffer(snapshot, identity, byte_cap=STORAGE.expanded_cap,
            reference_cap=STORAGE.reference_cap)) == raw
    cache, snapshot = rt._reference_archive.images, rt.snapshot()
    buffers = dict(snapshot.buffers)
    assert cache.used == sum(len(buffers[entry.buffer]) for entry in cache.entries) <= cache.cap
    for entry in snapshot.reference_archive.canonical_images:
        resource = snapshot.resources['objects'][entry.buffer]
        assert resource['kind'] == 'immutable_canonical_image'
        assert {snapshot.resources['owners'][o] for o in resource['references']} == {'compiler', 'deployment'}
    # Exhaustion affects only acceleration, never the complete byte output.
    limited = root(MIN_IMAGE)
    oversized = bytes(range(256))*40
    retain(limited, oversized, 'too-large')
    assert not limited._reference_archive.images.entries
    repeated = b'k'*4088  # The complete typed encoding is exactly 8,192 bytes.
    retain(limited, repeated, 'fits')
    before = tuple(limited._reference_archive.images.entries)
    assert len(before) == 1 and limited._reference_archive.images.used == MIN_IMAGE
    retain(limited, oversized, 'after-full')
    assert tuple(limited._reference_archive.images.entries) == before
    return dict(limit_checks=limit_checks, uncached_bytes_compared=archive_bytes,
        old_snapshots=len(old), image_count=len(cache.entries), image_bytes=cache.used,
        exhausted_image_budget=limited._reference_archive.images.used,
        mutable_wrappers_not_bound=True, capacity_misses_preserve_complete_bytes=True,
        both_resource_roles_own_images=True)


def failures():
    results = []
    for mode in ('wrong-image', 'wrong-page', 'unpaid-image'):
        rt = root()
        data = bytes(range(256))*40
        if mode == 'wrong-page':
            retain(rt, data, 'warm')
            original = byte_archive.Builder.push
            def bad(builder, part):
                return original(builder, bytes((part[0] ^ 1,))+part[1:])
            replacement = patch.object(byte_archive.Builder, 'push', bad)
        elif mode == 'wrong-image':
            original = encoding.write_packed
            def bad(value, buffer):
                original(value, buffer)
                buffer[-1] ^= 1
            replacement = patch.object(encoding, 'write_packed', bad)
        else:
            original = rt._ledger.charge_work
            def bad(*args, **kwargs):
                if kwargs.get('note') == 'owned-canonical-image':
                    raise ResourceExceeded('unpaid canonical image')
                return original(*args, **kwargs)
            replacement = patch.object(rt._ledger, 'charge_work', bad)
        with replacement:
            result = outcome(lambda: retain(rt, data, mode))
        assert result[0] == 'REFUSED' and rt.snapshot().halted, (mode, result)
        if mode != 'wrong-page':
            assert rt._reference_archive.images.find(data) is None
        validate_residency(rt)
        results.append(mode)
    for fault in (ResourceExceeded, MemoryError):
        with cpu_device():
            rt = root(cuda=True)
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            before = rt.snapshot()
            current = dict(rt._cuda.current)
            with patch.object(_CanonicalImages, 'prepare', side_effect=fault('fixed post-target image failure')):
                if fault is MemoryError:
                    try:
                        rt.observe(1)
                    except MemoryError:
                        pass
                    else:
                        raise AssertionError('MemoryError must escape through the terminal host guard')
                else:
                    result = rt.observe(1)
                    assert result.status == 'UNRESOLVED'
            after = rt.snapshot()
            assert after.halted
            assert after.observations[-1].target == 1 and after.cursor == 0
            assert after.candidates == before.candidates and rt._cuda.current == current
            results.append('post-target-'+fault.__name__)
    return dict(refusals=results, targets_and_prior_learners_retained=True)


@contextmanager
def without_images():
    # Strong uncached baseline: the same registration/IDs, original traversal,
    # and no per-atom cache lookup or image-admission work.
    original = _SharedReference.__init__
    def initialize(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self.images = None
    with patch.object(_SharedReference, '__init__', initialize):
        yield


def runtime_control():
    from contextlib import nullcontext
    from fp_reference.token_arrays import CPUArrays
    from audit_shared_cuda_retention import full_registration
    cc, program, online, cfg, storage, _, _, targets, corpus = full_registration()
    storage = replace(storage, canonical_image_bytes=64 << 20)
    readings, saved = [], []
    for use_cache in (False, True):
        reads = []
        original = CPUArrays.raw
        def read(a, value):
            result = original(a, value)
            reads.append((result.shape, str(result.dtype), result.tobytes()))
            return result
        # Couple only the otherwise random owner nonce, as in the prior reuse
        # CPU comparison. Each isolated Runtime still owns all of its objects.
        with cpu_device(), (nullcontext() if use_cache else without_images()), \
                patch.object(CPUArrays, 'raw', read), \
                patch.object(runtime_module.secrets, 'token_hex', return_value='canonical-images-control'):
            rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg, shared_storage=storage)
            for i, target in enumerate(targets[:2]):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            snapshot = validate_residency(rt)
            rows = tuple(encoding.pack(p) for p in snapshot.cuda.phases)
            for p, body in zip(snapshot.cuda.phases, rows):
                raw = b''.join(decoded_buffer(snapshot, p.object_id,
                    byte_cap=storage.expanded_cap, reference_cap=storage.reference_cap))
                size = int.from_bytes(raw[:8], 'big')
                assert raw[8:8+size] == body
            saved.append((snapshot.candidates, rows))
            readings.append(reads)
            if use_cache:
                cache = rt._reference_archive.images
                assert cache.find(program.definition.output.base) is not None
                images, image_bytes = len(cache.entries), cache.used
    if saved[0] != saved[1]:
        from dataclasses import fields
        candidate_changes = [[f.name for f in fields(a) if getattr(a, f.name) != getattr(b, f.name)]
                             for a, b in zip(saved[0][0], saved[1][0])]
        byte_changes = []
        for i, (a, b) in enumerate(zip(saved[0][1], saved[1][1])):
            if a != b:
                offset = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                byte_changes.append((i, len(a), len(b), offset, a[max(0,offset-40):offset+80].decode('ascii', 'replace'),
                                     b[max(0,offset-40):offset+80].decode('ascii', 'replace')))
        raise AssertionError((candidate_changes, byte_changes))
    assert readings[0] == readings[1], (len(readings[0]), len(readings[1]))
    return dict(complete_phases=len(saved[0][1]), phase_bytes=sum(map(len, saved[0][1])),
        identical_raw_reads=len(readings[0]), identical_read_bytes=sum(len(r[2]) for r in readings[0]),
        images=images, image_bytes=image_bytes, corpus=corpus,
        scope='first two events of the original full-V unit, CPU substitution; not a full unit or language score')


def audit():
    result = dict(component=component(), failures=failures(), runtime=runtime_control())
    assert 'torch' not in sys.modules
    return dict(status='PASS_OWNED_CANONICAL_IMAGES_CPU',
        scope='exact archive/value/resource checks and complete CPU-substituted Runtime; no CUDA or model result', **result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_CANONICAL_IMAGES_CPU.json').write_text(body, encoding='utf-8')
    print(body)
