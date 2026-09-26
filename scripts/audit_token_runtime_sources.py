"""Actual Runtime token-source ownership and complete literal learner paths.

This small literal integration is the control for the forthcoming indexed
backend, not a full-vocabulary performance or new AMP/release claim.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference import ConstructionContract, OnlineContract, ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.ingress import encode_context
from fp_reference.learner import LearnerSpec
from fp_reference.profile import ProfileSpec
from audit_reference_construction import limits, rejects, validate_residency
from audit_native_tokens import fixture, complete, same
import native_tokens as tokens


def registration(d, initial, count=4, *, profile=None):
    rules, program = tokens.materialize(d)
    reads = tuple(SourceRead(f'lag{lag}/token{token}',
        'target_missing' if token == d.sources.padding else 'target_atom',
        0 if token == d.sources.padding else token, lag)
        for lag in range(1, d.sources.context+1) for token in range(d.sources.vocabulary+1))
    streams = (StreamSpec('training', 'train', tuple(f'train/{i}' for i in range(count))),
               StreamSpec('heldout', 'validation', ('validation/0',)))
    data = DataContract(streams, 'training', (), reads)
    counts = program.counts()
    cfg = ConstructionContract(rules, limits(byte_cap=64 << 20, work_cap=10**9),
        {'construct': 'compiler', 'range_audit': 'compiler'},
        {'nodes': counts['nodes'], 'SUMs': counts['SUMs'], 'PRODUCTs': counts['PRODUCTs'],
         'edges': counts['edges'], 'slots': program.slot_count}, complete(initial), F(1000), F(1000), 32768)
    online = OnlineContract(data, LearnerSpec(d.output.update_unit, d.output.learning_rate, d.output.grid_bits),
        profiles=() if profile is None else (profile,))
    return cfg, program, online


def run_word(d, root, word, *, profile=None):
    cfg, graph, online = registration(d, root, len(word), profile=profile)
    rt = ReferenceCompilerRuntime(cfg, graph, online=online)
    exact = root
    checks = 0
    for t, target in enumerate(word):
        expected = exact.predict()
        predicted = rt.predict_next(f'train/{t}', encode_context(()))
        assert predicted.status == 'PREDICTED_REFERENCE'
        snapshot = validate_residency(rt)
        actual_sources = dict(snapshot.pending.record.sources)
        for lag in range(1, d.sources.context+1):
            for token in range(d.sources.vocabulary+1):
                assert actual_sources[f'lag{lag}/token{token}'] == expected.window.atom(lag, token)
                checks += 1
        assert predicted.predictions[0][1] == tuple(expected.output.mass(y)/expected.output.normalizer for y in range(d.output.labels))
        observed = rt.observe(target)
        assert observed.status == 'OBSERVED_REFERENCE'
        exact = exact.observe(expected, target)
        if exact.output.unit_count == d.output.update_unit:
            exact = exact.commit()
        snapshot = validate_residency(rt)
        candidate = next(s for s in snapshot.candidates if s.candidate_id == snapshot.deployed_id)
        same(exact, candidate.learner)
        assert snapshot.observations[-1].target == target
        assert snapshot.observations[-1].sources == tuple(actual_sources.items())
    return rt, exact, checks


def histories():
    events = commits = atoms = words = parameters = 0
    for unit, kind in product((1, 2), ('mixed', 'zero-embedding', 'zero-core')):
        d, root = fixture(unit, kind)
        for word in product(range(2), repeat=4):
            rt, exact, checked = run_word(d, root, word)
            snapshot = validate_residency(rt)
            assert snapshot.cursor == 4 and snapshot.halted is None
            words += 1
            events += 4
            atoms += checked
            commits += 4//unit
            parameters += 4*d.slot_count
    return dict(complete_words=words, runtime_observations=events, optimizer_commits=commits,
        owned_causal_atom_checks=atoms, complete_parameter_and_gradient_coordinate_pairs=parameters)


def profiles():
    d, root = fixture(2, 'mixed')
    spec = ProfileSpec('retained-contexts', ('train/0', 'train/2'), 2)
    events = continuations = 0
    for word in product(range(2), repeat=4):
        cfg, graph, online = registration(d, root, 6, profile=spec)
        rt = ReferenceCompilerRuntime(cfg, graph, online=online)
        for i, target in enumerate(word):
            assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
        born = rt.construct_candidate(graph, profile_id=spec.profile_id)
        assert born.status == 'BUILT_REFERENCE', born
        snapshot = validate_residency(rt)
        replay = root
        for event, position in zip(snapshot.profile_events, (0, 2, 0, 2)):
            assert event.observation_id == f'train/{position}'
            same(replay, event.before)
            window = d.sources.window(word, position)
            expected = replay.predict(window)
            offset = len(cfg.semantics.sources)
            assert event.prediction.values[offset:offset+len(expected.values)] == expected.values
            replay = replay.observe(expected, word[position], window=window)
            same(replay, event.after_observe)
            if replay.output.unit_count == d.output.update_unit:
                replay = replay.commit()
                same(replay, event.after_commit)
            else:
                assert event.after_commit is None
            events += 1
        candidate = next(c for c in snapshot.candidates if c.candidate_id == born.candidate_id)
        assert candidate.learner.cursor == snapshot.cursor == 4
        assert replay.source_position == 3
        same(replay, candidate.learner)
        # Ordinary source acquisition resumes from the real global prefix,
        # independently of the replayed candidate's last source position.
        for i, target in enumerate((1, 0), 4):
            tape = word+(1, 0)
            window = d.sources.window(tape, i)
            expected = replay.predict(window)
            prediction = rt.predict_next(f'train/{i}', encode_context(()))
            assert dict(prediction.predictions)[born.candidate_id] == tuple(expected.output.mass(y)/expected.output.normalizer for y in range(d.output.labels))
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            replay = replay.observe(expected, target, window=window)
            if replay.output.unit_count == d.output.update_unit:
                replay = replay.commit()
            candidate = next(c for c in validate_residency(rt).candidates if c.candidate_id == born.candidate_id)
            same(replay, candidate.learner)
            continuations += 1
        uses = rt.snapshot().data_uses
        assert sum(use.purpose == 'profile' for use in uses) == 4
    return dict(profiles=16, original_context_profile_events=events, ordinary_candidate_continuations=continuations,
        complete_profile_and_ordinary_state_match=True, owned_profile_data_uses=True)


def boundaries():
    d, root = fixture(2, 'mixed')
    cfg, graph, online = registration(d, root)
    rejects(lambda: SourceRead('bad', 'target_missing', 0, 0))
    rejects(lambda: SourceRead('bad', 'target_missing', 1, 1))
    rejects(lambda: replace(online.data, active_stream='heldout'))
    rejects(lambda: ProfileSpec('leak', ('validation/0',), 2).validate(online.data, online.learner))
    bad = replace(online.data, source_reads=tuple(replace(r, kind='target_atom', index=d.sources.padding)
        if r.kind == 'target_missing' else r for r in online.data.source_reads))
    rejects(lambda: bad.validate(cfg.semantics))
    wrong_delay = replace(cfg.semantics, sources=tuple(replace(s, availability_delay=0) for s in cfg.semantics.sources))
    rejects(lambda: online.data.validate(wrong_delay))
    for field, value in (('index', 1), ('kind', 'caller_callback')):
        original = next(r for r in online.data.source_reads if r.kind == 'target_missing')
        forged = replace(original)
        object.__setattr__(forged, field, value)
        data = replace(online.data, source_reads=tuple(forged if r is original else r for r in online.data.source_reads))
        run = replace(online, data=data)
        rejects(lambda: ReferenceCompilerRuntime(cfg, graph, online=run))
    # Caller ingress has no token-atom coordinate. The Runtime derives all
    # history from its retained targets; adding a fake source input fails.
    rt = ReferenceCompilerRuntime(cfg, graph, online=online)
    rejects(lambda: rt.predict_next('train/0', encode_context((1,))))
    snapshot = validate_residency(rt)
    assert snapshot.halted is not None and snapshot.cursor == 0
    return dict(schema_delay_role_and_ingress_refusals=9, caller_cannot_supply_history_atoms=True,
        first_PAD_is_not_token_zero=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_LITERAL_TOKEN_SOURCES', scope='actual ReferenceCompilerRuntime source/profile semantics on the literal audit class; no indexed/AMP/release claim')
    for key, fn in (('histories', histories), ('profiles', profiles), ('boundaries', boundaries)):
        result[key] = fn()
        print('PASS '+key, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_RUNTIME_SOURCES.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
