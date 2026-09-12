"""Owned profile replay, complete newborn attachment and exact value-path audit."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'theory/numerical_checks')]

from fp_reference import OnlineContract, ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.learner import LearnerSpec
from fp_reference.profile import ProfileSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, SemanticRules, Source, SourceSpec, State, Sum, Term
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import forward_oracle, online, shared_graph
from value_reachability_audit import GAP, floor_dyadic, loss_upper, step


def ingest(rt, stream):
    for cursor, (row, target) in enumerate(stream):
        assert rt.predict_next(f'observation-{cursor}', row).status == 'PREDICTED_REFERENCE'
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'


def value_fixture():
    cfg = replace(contract(2, 2, cap=4, peak=2, pattern=(F(0),)), limits=limits(byte_cap=60_000_000))
    graph = Program(tuple(Source(s.source_id) for s in cfg.semantics.sources)+(
        Product('mass', 1, 3), Product('mass', 1, 2),
        Sum('mass', (Term(4, 0),)), Sum('mass', (Term(5, 1),))), 2, (6, 7))
    stream = tuple((row, y) for row, count in zip(domain(2), (2, 2, 3, 1))
                   for y in (0,)*(4-count)+(1,)*count)
    base_run = online(cfg, 32, unit=16, rate=F(16), grid=32)
    profile = ProfileSpec('fixed-profile', tuple(f'observation-{i}' for i in range(16)), 32)
    run = replace(base_run, profiles=(profile,))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    # Requested value construction is unavailable, never replaced by a free
    # pre-fitted state or a successful initializer-only candidate.
    premature = rt.construct_candidate(graph, profile_id=profile.profile_id)
    assert premature.status == 'UNRESOLVED' and premature.candidate_id is None
    assert rt.snapshot().profiles[-1].events_completed == 0
    ingest(rt, stream)
    before = rt.snapshot()
    result = rt.construct_candidate(graph, profile_id=profile.profile_id)
    assert result.status == 'BUILT_REFERENCE'
    after = validate_residency(rt)
    candidate = next(s for s in after.candidates if s.candidate_id == result.candidate_id)
    deployed = next(s for s in after.candidates if s.candidate_id == after.deployed_id)
    assert deployed == before.candidates[0] and after.cursor == before.cursor == 16
    assert after.observations == before.observations and after.event_traces == before.event_traces
    assert after.resources['spent']['deployment'] == before.resources['spent']['deployment']
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert candidate.profile_id == profile.profile_id
    record = after.profiles[-1]
    assert record.status == 'PROFILED_REFERENCE' and record.events_completed == record.total_events == 512
    assert record.initial.cursor == record.attached.cursor == 16 and record.local.cursor == 512
    assert replace(record.local, cursor=16) == record.attached == candidate.learner
    events = tuple(e for e in after.profile_events if e.candidate_id == candidate.candidate_id)
    value, first, commits = F(0), None, 0
    for position, event in enumerate(events):
        assert event.position == event.before.cursor == position and event.ordinary_cursor == 16
        assert event.observation_id == profile.observation_ids[position % 16]
        if event.after_commit is not None:
            commits += 1
            value = floor_dyadic(step(value), 32)
            assert event.after_commit.theta == (value, value)
            if first is None and loss_upper(value) < GAP:
                first = commits
    assert commits == 32 and first == 13 and candidate.theta == (value, value)
    uses = tuple(u for u in after.data_uses if u.purpose == 'profile' and u.consumer == candidate.candidate_id)
    count = Counter(obs for use in uses for obs in use.observation_ids)
    assert len(uses) == 512 and count == Counter({obs: 32 for obs in profile.observation_ids})
    assert all(u.cursor == 16 for u in uses)
    # The other existing XVII.5 fixture has a dormant factor face. Profile
    # must not silently initialize it from an expressive encoded witness.
    dormant = Program(tuple(Source(s.source_id) for s in cfg.semantics.sources)+(
        Sum('mass', (Term(0, 0), Term(3, 1))), Sum('mass', (Term(1, 2), Term(2, 3))),
        Product('mass', 4, 5), Sum('mass', (Term(6, 4),)),
        Sum('mass', (Term(1, 5), Term(2, 6)))), 7, (7, 8))
    dormant_result = rt.construct_candidate(dormant, profile_id=profile.profile_id)
    assert dormant_result.status == 'BUILT_REFERENCE'
    dormant_state = next(s for s in rt.snapshot().candidates if s.candidate_id == dormant_result.candidate_id)
    assert dormant_state.theta[:5] == (F(0),)*5
    dormant_events = tuple(e for e in rt.snapshot().profile_events if e.candidate_id == dormant_result.candidate_id)
    assert len(dormant_events) == 512 and all(e.after_observe.gradient_sum[:5] == (F(0),)*5 for e in dormant_events)
    rt.retire_candidate(dormant_result.candidate_id)
    # Marginal target counts are exactly balanced: the unchanged uniform
    # deployed predictor is the empirical optimal unigram for this fixture.
    assert sum(y for _, y in stream) == len(stream)//2
    future = rt.predict_next('observation-16', domain(2)[2])
    assert dict(future.predictions)[candidate.candidate_id][1] > F(1, 2)
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    assert rt.snapshot().cursor == 17
    bound_candidate = next(s for s in rt.snapshot().candidates if s.candidate_id == candidate.candidate_id)
    assert bound_candidate.learner.optimizer_steps == 32 and bound_candidate.learner.unit_count == 1
    return {'unique_profile_labels': 16, 'actual_profile_predictions_and_observations': 512,
            'registered_profile_updates': 32, 'ordinary_cursor_before_and_after_profile': 16,
            'every_commit_matches_existing_exact_recurrence': True, 'existing_CE_upper_first_crossing': first,
            'baseline': 'empirical optimal unigram on balanced retained labels',
            'fresh_persistence_observations_created_by_profile': 0,
            'existing_dormant_face_preserved_for_512_profile_events': True,
            'next_ordinary_event_continues_complete_profiled_state': True}


def exhaustive_replay():
    cfg = contract(pattern=(F(0), F(1, 3), F(0)), cap=100, peak=100)
    graph = shared_graph()
    profile = ProfileSpec('two-passes', ('observation-1', 'observation-0'), 2)
    checks = 0
    for entries in product(product((0, 1), repeat=2), repeat=2):
        run = replace(online(cfg, 4, unit=2, rate=F(1, 4)), profiles=(profile,))
        rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
        stream = tuple((domain(1)[x], y) for x, y in entries)
        ingest(rt, stream)
        result = rt.construct_candidate(graph, profile_id='two-passes')
        assert result.status == 'BUILT_REFERENCE'
        built = next(s for s in rt.snapshot().candidates if s.candidate_id == result.candidate_id)
        theta, accumulated, updates = cfg.initializer_pattern, (F(0),)*3, 0
        for position, index in enumerate((1, 0, 1, 0)):
            row, target = stream[index]
            sources = dict(zip((s.source_id for s in cfg.semantics.sources), row))
            probabilities, gradients = forward_oracle(graph, cfg.semantics, theta, sources)
            event = rt.snapshot().profile_events[position]
            assert event.prediction.probabilities == probabilities
            accumulated = tuple(a+b for a, b in zip(accumulated, gradients[target]))
            if position % 2:
                theta = tuple(floor_dyadic(max(F(0), v-F(1, 8)*g), 24) for v, g in zip(theta, accumulated))
                accumulated, updates = (F(0),)*3, updates+1
            checks += 1
        assert built.theta == theta and built.learner.gradient_sum == accumulated
        assert built.learner.optimizer_steps == updates == 2 and built.learner.cursor == 2
        validate_residency(rt)
    return {'all_two_event_binary_context_target_streams': 16, 'independent_profile_prediction_and_gradient_checks': checks}


def recurrent_attachment():
    rules = SemanticRules((SourceSpec('x', 'mass', 0, 1), SourceSpec('previous-y0', 'mass', 1, 1)),
                          ('mass',), (('mass', 'mass', 'mass'),), 'mass', (1, 1),
                          (DelayedStateSpec('h', 'mass', 2, 1),))
    cfg = replace(contract(source_domain=False, pattern=(F(0),)), semantics=rules)
    graph = Program((Source('x'), Source('previous-y0'), State('h')), 0, (2, 1), (Binding('h', 0),))
    data = DataContract((StreamSpec('online', 'online', tuple(f'observation-{i}' for i in range(6))),),
                        'online', (F(1),), (SourceRead('x', 'input', 0, 0), SourceRead('previous-y0', 'target_atom', 0, 1)))
    # Nonchronological record order tests logged source provenance rather than
    # recomputing a fictional source prefix from profile-local event indices.
    profile = ProfileSpec('recurrent', ('observation-3', 'observation-0', 'observation-2', 'observation-1'), 2)
    run = OnlineContract(data, LearnerSpec(2, 0), profiles=(profile,))
    rt = ReferenceCompilerRuntime(cfg, graph, online=run)
    ingest(rt, (((0,), 0), ((1,), 1), ((0,), 1), ((1,), 0)))
    before = rt.snapshot()
    result = rt.construct_candidate(graph, profile_id='recurrent')
    assert result.status == 'BUILT_REFERENCE'
    after = validate_residency(rt)
    candidate = next(s for s in after.candidates if s.candidate_id == result.candidate_id)
    events = after.profile_events
    by_id = {obs.observation_id: obs for obs in before.observations}
    history = (F(0), F(0))
    for event in events:
        source = dict(by_id[event.observation_id].sources)
        assert event.prediction.values[1] == source['previous-y0']
        assert event.prediction.values[2] == history[0]
        history = history[1:]+(source['x'],)
        assert event.after_observe.delayed == (('h', history),)
    assert candidate.delayed == (('h', history),) == (('h', (F(0), F(1))),)
    assert after.profiles[-1].local.cursor == 8 and candidate.learner.cursor == after.cursor == 4
    assert candidate.learner.optimizer_steps == 4
    forecast = rt.predict_next('observation-4', (1,))
    assert forecast.status == 'PREDICTED_REFERENCE'
    pending = dict(rt.snapshot().pending.predictions)[candidate.candidate_id]
    assert pending.values[2] == history[0]
    rt.observe(1)
    after_one = next(s for s in rt.snapshot().candidates if s.candidate_id == candidate.candidate_id)
    assert after_one.delayed == (('h', (F(1), F(1))),)
    return {'recurrent_profile_events': 8, 'logged_original_source_contexts_preserved': True,
            'delayed_and_optimizer_state_survive_boundary_attachment': True}


def invalid_and_failed_profiles():
    cfg = contract(pattern=(F(0),), cap=100, peak=100)
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    base_run = online(cfg, 4, unit=2)
    profile = ProfileSpec('fit', ('observation-0', 'observation-1'), 2)
    run = replace(base_run, profiles=(profile,))
    rejects(lambda: replace(base_run, profiles=(ProfileSpec('bad', ('test-label',), 2),)))
    rejects(lambda: replace(base_run, profiles=(ProfileSpec('bad', ('unknown',), 2),)))
    rejects(lambda: replace(base_run, profiles=(ProfileSpec('bad', ('observation-0',), 1),)))
    rejects(lambda: ProfileSpec('bad', ('observation-0', 'observation-0'), 1))
    rejects(lambda: ProfileSpec('bad', ('observation-0',), True))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    ingest(rt, (((1, 0), 0), ((1, 0), 0)))
    rejects(lambda: rt.construct_candidate(graph, profile_id='fit', theta=(100,)), TypeError)
    assert rt.construct_candidate(graph, profile_id=profile).status == 'REJECTED_ADMISSIBILITY'
    assert rt.construct_candidate(graph, profile_id='unregistered').status == 'REJECTED_ADMISSIBILITY'
    before = rt.snapshot()
    original, calls = execution.observe_event, []

    def fail_after_read(*args, **kwargs):
        calls.append(1)
        # Public events cannot interleave with a value-construction prefix.
        rejects(lambda: rt.predict_next('observation-2', (1, 0)))
        rejects(lambda: rt.construct_candidate(graph))
        if len(calls) == 3:
            raise RuntimeError('injected profile backend failure')
        return original(*args, **kwargs)

    with patch.object(execution, 'observe_event', side_effect=fail_after_read):
        rejects(lambda: rt.construct_candidate(graph, profile_id='fit'), RuntimeError)
    after = validate_residency(rt)
    failed = after.profiles[-1]
    assert after.candidates == before.candidates and after.cursor == before.cursor
    assert after.observations == before.observations and after.event_traces == before.event_traces
    assert failed.status == 'EXECUTION_FAILED' and failed.events_completed == 2
    assert failed.candidate_id+':owner' in after.resources['closed_owners']
    uses = tuple(u for u in after.data_uses if u.purpose == 'profile' and u.consumer == failed.candidate_id)
    assert len(uses) == 3 and uses[-1].observation_ids == ('observation-0',)
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert failed.program_id in dict(after.programs)
    assert dict(after.retained_programs)[failed.program_id] in dict(after.buffers)
    # Since no new ordinary target was revealed by profile, failure need not
    # halt the deployed trajectory or manufacture a fresh-data retry.
    assert after.event_phase == 'idle'
    assert rt.predict_next('observation-2', (1, 0)).status == 'PREDICTED_REFERENCE'
    rt.observe(1)

    # A legal registered gradient path leaves the cap at its first commit.
    tight = replace(cfg, normalizer_cap=F(2), activation_cap=F(1))
    rt = ReferenceCompilerRuntime(tight, zero_program(2), online=run)
    ingest(rt, (((1, 0), 0), ((1, 0), 0)))
    before = rt.snapshot()
    result = rt.construct_candidate(graph, profile_id='fit')
    assert result.status == 'UNRESOLVED' and result.candidate_id is None
    failed = rt.snapshot().profiles[-1]
    assert failed.local.theta == (F(1, 2),) and failed.stage == 'range'
    assert rt.snapshot().candidates == before.candidates and rt.snapshot().cursor == 2
    validate_residency(rt)

    # Actual cumulative work exhaustion inside replay retains the paid prefix.
    calibration = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    ingest(calibration, (((1, 0), 0), ((1, 0), 0)))
    before_work = calibration.snapshot().resources['spent']['compiler']['work']
    work_caps = dict(cfg.limits.role_cumulative)
    work_caps['compiler'] = {'work': before_work+125}
    capped = replace(cfg, limits=replace(cfg.limits, role_cumulative=work_caps))
    limited = ReferenceCompilerRuntime(capped, zero_program(2), online=run)
    ingest(limited, (((1, 0), 0), ((1, 0), 0)))
    incumbent = limited.snapshot().candidates
    assert limited.construct_candidate(graph, profile_id='fit').status == 'UNRESOLVED'
    last = validate_residency(limited)
    assert last.candidates == incumbent and last.cursor == 2
    assert last.profiles[-1].status == 'UNRESOLVED' and 0 < last.profiles[-1].events_completed < 4
    assert any(use.purpose == 'profile' for use in last.data_uses)
    assert before_work < last.resources['spent']['compiler']['work'] <= before_work+125

    # A physical cap that admits construction cannot disguise the extra live
    # replay tape/state as free profiling. Derive it from the actual initializer.
    calibration.construct_candidate(graph)
    cap = calibration.snapshot().resources['peak']['reference_payload_bytes']
    tight_memory = replace(cfg, limits=limits(byte_cap=cap))
    memory = ReferenceCompilerRuntime(tight_memory, zero_program(2), online=run)
    ingest(memory, (((1, 0), 0), ((1, 0), 0)))
    incumbent = memory.snapshot().candidates
    assert memory.construct_candidate(graph, profile_id='fit').status == 'UNRESOLVED'
    last = validate_residency(memory)
    assert last.candidates == incumbent and last.cursor == 2
    assert last.resources['peak']['reference_payload_bytes'] <= cap
    assert last.profiles[-1].status == 'UNRESOLVED'
    return {'invalid_roles_horizons_and_value_injection_rejected': True,
            'failure_releases_newborn_objects_without_refunding_reads_or_work': True,
            'failed_profile_code_and_actual_read_identities_retained': True,
            'ordinary_continuation_and_profile_are_separate_clocks': True,
            'profile_work_and_physical_coexistence_caps_enforced': True,
            'unverified_profile_successor_is_unresolved': True}


def audit():
    return {'status': 'PASS', 'scope': 'public Runtime newborn construction with preregistered paid profile replay',
            'existing_value_path': value_fixture(), 'exhaustive_replay': exhaustive_replay(),
            'recurrent_attachment': recurrent_attachment(), 'adversaries': invalid_and_failed_profiles(),
            'not_closed': ['complete grammar search and typed proof authority',
                           'complete ERC-1 manifest and total host/device resource accounting',
                           'fresh stochastic persistence and error ledger',
                           'certified float64 and actual AMP execution', 'atomic installation and full Runtime release']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_PROFILE_RUNTIME_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
