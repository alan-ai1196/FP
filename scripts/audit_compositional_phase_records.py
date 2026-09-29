"""Passive expression audit of five actual full-vocabulary CPU Runtime records.

The existing complete owner still executes every original check and retention.
The research model consumes its finished records afterwards. No CUDA context,
new corpus data, substituted Runtime retention or timing/host-budget claim.
"""
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/next_token'), str(ROOT/'theory/numerical_checks')]
from fp_reference import ReferenceCompilerRuntime, encoding
from fp_reference.ingress import encode_context
from fp_reference.shared_reference import decoded_buffer
from audit_owned_token_reuse import cpu_device
from audit_shared_cuda_retention import full_registration
from audit_reference_construction import validate_residency
import compositional_retention_model as model


def audit():
    cc, program, online, cfg, storage, origin, windows, targets, corpus = full_registration()
    cfg = replace(cfg, reuse_regions=True)
    storage = replace(storage, canonical_image_bytes=64 << 20, token_invariant_bytes=4 << 20)
    with cpu_device():
        rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg, shared_storage=storage)
        for i, target in enumerate(targets[:2]):
            result = rt.predict_next(f'train/{i}', encode_context(()))
            assert result.status == 'PREDICTED_REFERENCE', result.reason
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE', result.reason
        snapshot = validate_residency(rt)
    phases = snapshot.cuda.phases
    assert len(phases) == 5
    owner, rows = model.Owner(), []
    for phase in phases:
        expected = encoding.pack(phase)
        # Compare with the actual complete frame, including its paid padding.
        raw = b''.join(decoded_buffer(snapshot, phase.object_id,
            byte_cap=storage.expanded_cap, reference_cap=storage.reference_cap))
        count = int.from_bytes(raw[:8], 'big')
        assert len(raw) == cfg.phase_evidence_bytes and count == len(expected)
        assert raw[8:8+count] == expected and not any(raw[8+count:])
        with patch.object(model.Reader, 'expand', side_effect=AssertionError('binding expanded old data')):
            root = owner.retain(phase)
        assert b''.join(owner.reader.expand(root)) == expected
        assert id(phase) not in owner.bindings
        rows.append(dict(phase=phase.phase, **owner.statistics[-1]))
    rebuilt = model.Reader(owner.limits)
    for page in owner.snapshot()[0]:
        rebuilt.add(page)
    for phase, root in zip(phases, owner.roots):
        assert b''.join(rebuilt.expand(root)) == encoding.pack(phase)
    literals = [len(payload) for tag, payload, _ in owner.reader.index.nodes if tag == 0]
    pairs = len(owner.reader.index.nodes)-len(literals)
    stored = sum(map(len, owner.reader.pages))
    assert stored == model.HEADER.size*len(rows)+sum(5+n for n in literals)+17*pairs
    return dict(status='PASS_COMPOSITIONAL_FULL_V_RECORDS', scope=__doc__.strip(),
        vocabulary=program.definition.output.labels, masters=program.slot_count,
        original_targets=2, original_runtime_phases=len(phases), corpus=corpus,
        all_existing_frames_and_padding_checked=True, all_model_roots_fully_recovered=True,
        independent_page_only_rebuild=True, no_expansion_during_model_binding=True,
        original_frame_bytes=sum(cfg.phase_evidence_bytes for _ in phases),
        complete_canonical_bytes=sum(r['expanded'] for r in rows),
        retained_model_page_bytes=stored, literal_nodes=len(literals), pair_nodes=pairs,
        source_binding_count=len(owner.bindings), phases=rows)


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('complete record audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_COMPOSITIONAL_FULL_V_RECORDS.json').write_text(body, encoding='utf-8')
    print(body)
