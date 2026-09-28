"""Public snapshot substitution into a live canonical image binding.

Reproduce the old alias from Git, then check detached diagnostic wrappers.
The attack only mutates returned snapshot metadata, not Runtime internals or
source scalar internals. CPU physical binding supplies no CUDA authority.
"""
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import canonical_images, encoding, ReferenceCompilerRuntime
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
from fp_reference.shared_reference import SharedPlannedObject, decoded_buffer
from fp_reference.resources import ObjectSpec
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from audit_canonical_images import root, retain

PREVIOUS = '075eba1da7493582665b8801a61430ac02876be6'


def previous_snapshot():
    path = 'src/reference_compiler/fp_reference/canonical_images.py'
    source = subprocess.check_output(['git', 'show', PREVIOUS+':'+path], cwd=ROOT, encoding='utf-8')
    # Only the historical method is installed; all live objects retain their
    # current known types. No second research implementation is stored.
    module = ModuleType(canonical_images.__name__)
    module.__package__ = canonical_images.__package__
    exec(compile(source, 'git:'+PREVIOUS+':'+path, 'exec'), module.__dict__)
    return module._CanonicalImages.snapshot


def substitute(snapshot, left_source, right_source):
    entries = snapshot.reference_archive.canonical_images
    left = next(e for e in entries if e.source is left_source)
    right = next(e for e in entries if e.source is right_source)
    # Preserve the actual source identity; substitute only the public binding
    # metadata. Both source values and both paid byte buffers stay immutable.
    left.__dict__.update({key: getattr(right, key) for key in
                         ('buffer', 'size', 'traversal', 'depth', 'integer_bits')})
    return left


def component(legacy):
    with (patch.object(canonical_images._CanonicalImages, 'snapshot', previous_snapshot()) if legacy else nullcontext()):
        rt = root()
        a, b = bytes(range(256))*32, b'z'*8192
        retain(rt, a, 'a')
        retain(rt, b, 'b')
        snapshot = rt.snapshot()
        original = rt._reference_archive.images.find(a).buffer
        exposed = substitute(snapshot, a, b)
        private = rt._reference_archive.images.find(a)
        assert (exposed is private) == legacy
        assert (private.buffer == original) != legacy
        identity = 'public-snapshot-image-substitution'
        planned = SharedPlannedObject(ObjectSpec(identity, 'canonical_image_control',
            {'reference_payload_bytes': 16, 'physical_objects': 1}, rt._chi), a)
        rt._allocate(rt._data_owner, (planned,))
        after = rt.snapshot()
        raw = b''.join(decoded_buffer(after, identity, byte_cap=1 << 20, reference_cap=1 << 20))
        assert after.halted is None
        assert (raw == encoding.pack(a)) != legacy
        assert (raw == encoding.pack(b)) == legacy
        return dict(legacy=legacy, snapshot_aliases_private_binding=exposed is private,
            retention_completed=True, retained_actual_supplied_value=raw == encoding.pack(a),
            retained_substituted_value=raw == encoding.pack(b), encoded_bytes=len(raw))


def complete_prefix(legacy):
    from audit_shared_cuda_retention import full_registration
    from audit_token_snapshot_bounds import cpu_device
    from audit_reference_construction import validate_residency
    cc, program, online, cfg, storage, _, _, _, corpus = full_registration()
    storage = replace(storage, canonical_image_bytes=64 << 20, token_invariant_bytes=4 << 20)
    with cpu_device(), (patch.object(canonical_images._CanonicalImages, 'snapshot', previous_snapshot()) if legacy else nullcontext()):
        rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg, shared_storage=storage)
        snapshot = rt.snapshot()
        original = snapshot.candidates[0].learner.origin
        substitute(snapshot, original.embedding, original.output)
        # This continuation is the public pre-target port. Numerical checking
        # remains enabled and consumes the actual original masters.
        outcome = rt.predict_next('train/0', encode_context(()))
        assert outcome.status == 'PREDICTED_REFERENCE', outcome.reason
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE' and len(after.cuda.phases) == 2
        assert after.candidates[0].learner.origin.embedding == original.embedding
        raw = b''.join(decoded_buffer(after, phase.object_id,
            byte_cap=storage.expanded_cap, reference_cap=storage.reference_cap))
        size = int.from_bytes(raw[:8], 'big')
        # This fresh expected stream has NO canonical-image argument. It is
        # independent of the attacked source-to-buffer lookup.
        actual = raw[8:8+size]
        expected = encoding.pack(phase)
        assert (actual == expected) != legacy
        difference = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b), None)
        assert not any(raw[8+size:])
        return dict(legacy=legacy, public_prediction_status=outcome.status,
            checked_phases=len(after.cuda.phases), original_master_words_unchanged=True,
            retained_frame_matches_actual_phase=actual == expected,
            retained_bytes=len(actual), actual_phase_bytes=len(expected), first_differing_byte=difference,
            cursor=after.cursor, corpus=corpus)


def detached_and_failure():
    rt = root()
    value = b'a'*8192
    retain(rt, value, 'snapshot-copy')
    before = rt.snapshot()
    exposed = next(e for e in before.reference_archive.canonical_images if e.source is value)
    current = rt._reference_archive.images.find(value)
    original = dict(vars(current))
    assert exposed is not current and vars(exposed) == original
    exposed.__dict__.update(source=b'changed', buffer='missing', size=-1,
                            traversal=-1, depth=-1, integer_bits=-1)
    assert vars(current) == original
    assert vars(next(e for e in rt.snapshot().reference_archive.canonical_images if e.source is value)) == original
    # A failed diagnostic cannot return a partial binding table or turn a
    # host allocation failure into resumed Runtime authority.
    with patch.object(canonical_images, 'Image', side_effect=MemoryError('snapshot binding copy')):
        try:
            rt.snapshot()
        except MemoryError:
            pass
        else:
            raise AssertionError('snapshot allocation failure was hidden')
    after = rt.snapshot()
    assert after.halted is HOST_ALLOCATION_FAILURE
    assert after.candidates == before.candidates and after.cursor == before.cursor
    assert vars(rt._reference_archive.images.find(value)) == original
    try:
        rt.predict_next('train/0', encode_context(()))
    except ContractError:
        pass
    else:
        raise AssertionError('failed diagnostic regained continuation authority')
    return dict(all_public_binding_fields_detached=True,
        snapshot_memory_failure_terminal=True, prior_learner_and_binding_preserved=True)


def audit():
    result = dict(component=[component(legacy) for legacy in (True, False)])
    print('PASS historical substitution and detached binding controls', flush=True)
    result['public_runtime'] = [complete_prefix(legacy) for legacy in (True, False)]
    result['failure'] = detached_and_failure()
    assert 'torch' not in sys.modules
    return dict(status='PASS_CANONICAL_IMAGE_SNAPSHOT_ISOLATION_CPU', previous_source=PREVIOUS,
                scope=__doc__.strip(), **result)


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('snapshot counterexample audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_CANONICAL_IMAGE_SNAPSHOT_CPU.json').write_text(body, encoding='utf-8')
    print(body)
