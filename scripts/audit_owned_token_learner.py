"""Exhaustive actual-Runtime control for complete compact native token states.

No model score, corpus, Torch, device job or installation certificate.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference import ConstructionContract, OnlineContract, ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, StreamSpec, source_mapping
from fp_reference.encoding import pack, packed_size, bounded_packed_size, fragments, write_packed
from fp_reference.info import Moment, QuerySpec, evaluate_query
from fp_reference.ingress import encode_context
from fp_reference.learner import LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.profile import ProfileSpec
from fp_reference.program import SemanticRules, Sum, Term
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import evaluate
from fp_reference.token_sources import TokenAtomFamily, TokenSourceReads, TokenContext
from fp_reference.token_execution import (TokenProgram, TokenInitializer, TokenLearner,
    TokenReferenceMachine, TokenProbabilities)
from fp_reference.token_batch import Kernel
from fp_reference.token_enclosures import EnclosureUnresolved
from audit_native_tokens import fixture, complete, same
from audit_reference_construction import limits, rejects, validate_residency
import native_tokens as tokens


def registration(d, initial, count=4, *, profiles=(), queries=()):
    family = TokenAtomFamily(d.sources.vocabulary, d.sources.context)
    program = TokenProgram(d)
    q = tuple(int(initial.parameter(i)*d.output.grid) for i in range(d.slot_count))
    e, c = d.embedding_slots, d.slots
    pattern = TokenInitializer(family, d.width, d.output, q[:e], q[e:e+c] or (0,), q[e+c:], 1 << 20)
    rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
    cfg = ConstructionContract(rules, limits(128 << 20, 10**10),
        {'construct': 'compiler', 'range_audit': 'compiler'}, program.counts(), pattern, F(100), F(100), 32768)
    data = DataContract((StreamSpec('train', 'train', tuple(f'train/{i}' for i in range(count))),),
                        'train', (), TokenSourceReads(family))
    return cfg, program, OnlineContract(data, TokenLearner(d.output), profiles=profiles, queries=queries)


def live(snapshot, candidate=None):
    return next(s.learner for s in snapshot.candidates if s.candidate_id == (candidate or snapshot.deployed_id))


def owned(runtime):
    snapshot = validate_residency(runtime)
    buffers = dict(snapshot.buffers)
    for candidate in snapshot.candidates:
        assert buffers[candidate.object_ids[1]] == pack(candidate.learner)
    if snapshot.event_traces:
        trace = snapshot.event_traces[-1]
        prefix = f'{trace.candidate_id}:event:{trace.before.cursor}'
        assert buffers[prefix+':observed'] == pack(replace(trace, after_commit=None))
        if trace.after_commit is not None:
            assert buffers[prefix+':committed'] == pack(trace)
    return snapshot


def compare(actual, exact):
    literal = actual.materialize(scalar_cap=2*exact.definition.slot_count+3)
    same(exact, literal)
    assert actual.source == exact.source_window()
    for raw in (actual.origin.E, actual.origin.C, actual.origin.W):
        assert not raw.flags.writeable
    return exact.definition.slot_count


def histories():
    words = events = commits = forecasts = gradients = 0
    for unit, kind, word in product((1, 2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, exact = fixture(unit, kind)
        cfg, program, online = registration(d, exact)
        rt = ReferenceCompilerRuntime(cfg, program, online=online)
        rules, literal = tokens.materialize(d)
        assert program.counts() == {k: literal.counts()[k] for k in program.counts()}
        spec = LearnerSpec(unit, d.output.learning_rate, d.output.grid_bits)
        scalar = initial_state(literal, rules, complete(exact), 0, spec=spec, bit_limit=32768)
        compare(live(owned(rt)), exact)
        for t, target in enumerate(word):
            expected = exact.predict()
            result = rt.predict_next(f'train/{t}', encode_context(()))
            assert result.status == 'PREDICTED_REFERENCE'
            snapshot = owned(rt)
            prediction = snapshot.pending.predictions[0][1]
            assert type(result.predictions[0][1]) is TokenProbabilities
            source = source_mapping(snapshot.pending.record.sources)
            scalar_prediction = evaluate(literal, rules, scalar.theta, source, scalar.delayed, bit_limit=32768)
            assert tuple(result.predictions[0][1]) == scalar_prediction.probabilities
            assert prediction.normalizer == scalar_prediction.normalizer
            assert prediction.window == expected.window
            forecasts += d.output.labels
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE'
            exact = exact.observe(expected, target)
            scalar = observe_event(literal, scalar, spec, scalar_prediction, target, bit_limit=32768)
            snapshot = owned(rt)
            after = snapshot.event_traces[-1].after_observe
            gradients += compare(after, exact)
            assert after.materialize(scalar_cap=1000) == scalar
            if (t+1) % unit == 0:
                exact = exact.commit()
                scalar = commit_event(scalar, spec, bit_limit=32768)
                commits += 1
            actual = live(snapshot)
            compare(actual, exact)
            assert actual.materialize(scalar_cap=1000) == scalar
            assert snapshot.observations[-1].target == target and snapshot.data_uses[-1].purpose == 'ordinary'
            events += 1
        words += 1
    return dict(histories=words, owned_observations=events, exact_scalar_probabilities=forecasts,
        complete_pending_gradient_coordinates=gradients, exact_grid_commits=commits,
        complete_literal_native_equality=True, owned_state_event_payloads_and_leases_match=True)


def profiles():
    events = continuations = profiles = 0
    for word in product((0, 1), repeat=4):
        d, root = fixture(2, 'mixed')
        profile = ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2)
        cfg, program, online = registration(d, root, 6, profiles=(profile,))
        rt = ReferenceCompilerRuntime(cfg, program, online=online)
        for t, target in enumerate(word):
            assert rt.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
        result = rt.construct_candidate(program, profile_id=profile.profile_id)
        assert result.status == 'BUILT_REFERENCE'
        owned = validate_residency(rt)
        exact = root
        for event in owned.profile_events:
            window = event.prediction.window
            record = next(r for r in owned.observations if r.observation_id == event.observation_id)
            assert (window.position, window.past) == (record.sources.position, record.sources.past)
            before = exact.predict(window)
            assert tuple(event.prediction.probabilities) == tuple(before.output.mass(y)/before.output.normalizer for y in range(d.output.labels))
            exact = exact.observe(before, record.target, window=window)
            compare(event.after_observe, exact)
            if exact.output.unit_count == 2:
                exact = exact.commit()
            compare(event.after_commit or event.after_observe, exact)
            events += 1
        exact = replace(exact, output=replace(exact.output, cursor=4))
        compare(live(owned, result.candidate_id), exact)
        assert exact.source_position == 1 and exact.cursor == 4
        for t, target in enumerate((1, 0), 4):
            assert rt.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
            current = rt.snapshot().pending.record.sources
            window = tokens.TokenWindow(d.sources, current.position, current.past)
            pred = exact.predict(window)
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            exact = exact.observe(pred, target, window=window)
            if exact.output.unit_count == 2:
                exact = exact.commit()
            compare(live(validate_residency(rt), result.candidate_id), exact)
            continuations += 1
        profiles += 1
    return dict(newborn_profiles=profiles, original_source_profile_events=events, ordinary_candidate_continuations=continuations)


def boundary_attacks():
    d, root = fixture(2, 'mixed')
    query = QuerySpec('retained-moment', (Moment(('lag1/token2',)), Moment(('lag1/token0',), 1)),
                      (F(0), F(0)), (F(1), F(1)), 8, 4)
    cfg, program, online = registration(d, root, queries=(query,))
    rt = ReferenceCompilerRuntime(cfg, program, online=online)
    assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
    snap = rt.snapshot()
    before, prediction = live(snap), snap.pending.predictions[0][1]
    machine = TokenReferenceMachine(cfg.initializer_pattern)
    sources = source_mapping(snap.pending.record.sources)
    def observe(pred, source=sources):
        return machine.observe(program, before, online.learner, pred, 0,
            rules=cfg.semantics, sources=source, bit_limit=32768)
    mutations = (replace(prediction, normalizer=prediction.normalizer+1),
                 replace(prediction, values=(prediction.values[0]+1,)+prediction.values[1:]),
                 replace(prediction, head_upper=prediction.head_upper+1),
                 replace(prediction, probabilities=replace(prediction.probabilities, normalizer=prediction.normalizer+1)),
                 replace(prediction, before=replace(before)))
    for mutation in mutations:
        rejects(lambda: observe(mutation))
    foreign = source_mapping(TokenContext(cfg.semantics.sources, 1, (0, 2, 2)))
    rejects(lambda: observe(prediction, foreign))
    rejects(lambda: machine.commit(before, online.learner, bit_limit=32768))
    rejects(lambda: before.materialize(scalar_cap=1))
    hidden = replace(cfg.initializer_pattern)
    object.__setattr__(hidden, 'trained_state', before)
    rejects(lambda: replace(cfg, initializer_pattern=hidden))
    rejects(lambda: replace(online, learner=LearnerSpec(2, F(1, 16), 5)).validate(cfg))
    rejects(lambda: ReferenceCompilerRuntime(cfg, program))
    rejects(lambda: replace(program, definition=replace(d, output=replace(d.output, base=(F(1), F(1))))).validate(cfg.semantics))
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    for t, target in enumerate((1, 1, 0), 1):
        assert rt.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
    snap = validate_residency(rt)
    result = rt.query(query.query_id, tuple(r.observation_id for r in snap.observations))
    assert result == evaluate_query(query, snap.observations, bit_limit=32768)
    assert rt.snapshot().data_uses[-1].purpose == 'proposal'
    # The registration is a native class, not one hard-coded core graph.
    alternate = TokenProgram(replace(d, nodes=d.nodes+(Sum('f', (Term(0, 0),)),)))
    rejects(lambda: machine.predict(alternate, cfg.semantics, before, sources, bit_limit=32768))
    cfg2 = replace(cfg, graph_limits={k: max(v, alternate.counts()[k]) for k, v in cfg.graph_limits.items()})
    alternative = ReferenceCompilerRuntime(cfg2, program, online=online)
    assert alternative.construct_candidate(alternate).status == 'BUILT_REFERENCE'
    # Packed bytes retain every byte, avoid a whole-hex temporary and reject
    # an undersized paid buffer or a too-small traversal budget.
    payload = bytes(range(256))*5+b'\x00\xff'
    encoded = pack(payload)
    assert json.loads(encoded) == ['bytes_hex', payload.hex()]
    assert len(encoded) == packed_size(payload) == bounded_packed_size(payload, byte_limit=10000)
    assert max(map(len, fragments(payload, packed=True))) <= 512
    short = bytearray(len(encoded)-1)
    rejects(lambda: write_packed(payload, short))
    assert len(short) == len(encoded)-1
    rejects(lambda: bounded_packed_size(payload, byte_limit=2*len(payload)), ResourceExceeded)
    assert json.loads(''.join(fragments(payload))) == ['bytes', payload.hex()]
    return dict(cache_source_clock_registration_and_decoder_refusals=13, owned_query_coordinates=2,
                distinct_native_core_construction=True, streamed_binary_payload_bytes=len(payload))


def retained_failures():
    d, root = fixture(2, 'mixed')
    cfg, program, online = registration(d, root)
    rt = ReferenceCompilerRuntime(cfg, program, online=online)
    for t, target in enumerate((0, 1)):
        assert rt.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
        if t == 0:
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
    before = live(rt.snapshot())
    with patch.object(Kernel, 'bound', side_effect=EnclosureUnresolved('audit forced ambiguous exact grid cell')):
        outcome = rt.observe(1)
    assert outcome.status == 'UNRESOLVED'
    snap = validate_residency(rt)
    assert snap.halted is not None and snap.cursor == 1 and len(snap.observations) == 2
    assert snap.pending.record.target == 1 and snap.data_uses[-1].purpose == 'ordinary'
    assert live(snap) == before
    pending = snap.event_traces[-1].after_observe
    assert pending.targets == (0, 1) and len(pending.windows) == 2
    exact = root
    for window, target in zip(pending.windows, pending.targets):
        exact = exact.observe(exact.predict(window), target, window=window)
    compare(pending, exact)
    rejects(lambda: rt.observe(1))
    # Choose a cap above the complete precommit prefix, but below the already
    # registered commit debit. No solver may run before that debit succeeds.
    # Subtract the previously paid (but numerically refused) commit allowance.
    spent_before_commit = snap.resources['spent']['deployment']['work']-TokenReferenceMachine(cfg.initializer_pattern).commit_work(program)
    caps = {role: dict(value) for role, value in cfg.limits.role_cumulative.items()}
    caps['deployment']['work'] = spent_before_commit
    cfg = replace(cfg, limits=replace(cfg.limits, role_cumulative=caps))
    denied = ReferenceCompilerRuntime(cfg, program, online=online)
    assert denied.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
    assert denied.observe(0).status == 'OBSERVED_REFERENCE'
    assert denied.predict_next('train/1', encode_context(())).status == 'PREDICTED_REFERENCE'
    with patch.object(Kernel, 'bound', side_effect=AssertionError('unfunded solver executed')):
        result = denied.observe(1)
    assert result.status == 'UNRESOLVED'
    snap = validate_residency(denied)
    assert snap.observations[-1].target == 1 and snap.event_traces[-1].after_observe.targets == (0, 1)
    assert snap.event_traces[-1].after_commit is None and snap.cursor == 1
    return dict(numerical_refusal_retains_complete_target_and_unit=True,
                commit_debit_precedes_solver=True, denied_commit_retains_complete_target_and_unit=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_COMPLETE_TOKEN_REFERENCE')
    for key, check in (('histories', histories), ('profiles', profiles), ('boundary_attacks', boundary_attacks), ('retained_failures', retained_failures)):
        result[key] = check()
        print('PASS '+key, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_OWNED_TOKEN_LEARNER.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
