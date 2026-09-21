"""Owned indexed reference admission, causal phases and retained evidence.

Native oracles use the independent literal builder and reverse derivative.
No helper state, interval, phase record or GPU diagnostic is admitted as an
owned Runtime endpoint. Physical/installation integration remains separate.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import simplex_gradient as native
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, StreamSpec, SourceRead, StochasticStreamLaw
from fp_reference.indexed_relation import IndexedRelation, bound_view
from fp_reference.indexed_execution import (IndexedInitializer, IndexedLearner, CategoricalPairDomain,
    IndexedReferenceMachine, IndexedState, IndexedEvaluation)
from fp_reference.learner import SIMPLEX_GRADIENT, LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.profile import ProfileSpec, attach_boundary
from fp_reference.persistence import PersistenceContract, PersistenceRule
from fp_reference.program import Program, Sum
from fp_reference.runtime import ConstructionContract, OnlineContract
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference import indexed_execution as indexed
from audit_reference_construction import limits, rejects, validate_residency
from ingress_audit_support import deliver_context


def fixture(n, length, *, profiles=(), persistence=None, law=False, byte_cap=128 << 20, work_cap=10**14):
    schema = IndexedRelation(n)
    rules = schema.rules()
    ids = tuple(f'indexed-event:{k}' for k in range(length))
    cfg = ConstructionContract(rules, limits(byte_cap, work_cap),
        {'construct': 'compiler', 'range_audit': 'compiler'},
        {k: schema.counts()[k] for k in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots')},
        IndexedInitializer(n), F(10), F(8), 32768, CategoricalPairDomain(n))
    data = DataContract((StreamSpec('online', 'online', ids),), 'online', (F(1),)*(2*n),
        tuple(SourceRead(source.source_id, 'input', k, 0) for k, source in enumerate(rules.sources)))
    if law:
        data = replace(data, stream_law=StochasticStreamLaw('audit external stochastic producer assumption; finite tape proves no law'))
    online = OnlineContract(data, IndexedLearner(n), profiles=profiles, persistence=persistence)
    return cfg, schema, online


def literal(n, cursor=0):
    rules, graph, worlds = native.relation_graph(n)
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=tuple(range(1, len(worlds)+1)))
    state = initial_state(graph, rules, (F(1),)+(F(1, len(worlds)),)*len(worlds), cursor, spec=spec, bit_limit=32768)
    return rules, graph, spec, state


def check_state(actual, expected):
    assert type(actual) is IndexedState
    assert actual.materialize(scalar_cap=10000) == expected


def check_prediction(actual, expected):
    assert type(actual) is IndexedEvaluation
    assert actual.materialize(scalar_cap=10000) == expected


def step(rt, schema, event, models):
    cursor = rt.snapshot().cursor
    observation_id = rt.snapshot().online.data.active.observation_ids[cursor]
    i, j, y = event
    result = deliver_context(rt, observation_id, tuple(schema.source_row(i*schema.n+j).values()))
    assert result.status == 'PREDICTED_REFERENCE', result
    pending = validate_residency(rt).pending
    assert pending.record.target is None and pending.record.observation_id == observation_id
    predictions = {}
    for candidate, prediction in pending.predictions:
        rules, graph, spec, state = models[candidate]
        before = evaluate(graph, rules, state.theta, native.context(schema.n, i, j), (), bit_limit=32768)
        check_prediction(prediction, before)
        predictions[candidate] = before
    outcome = rt.observe(y)
    assert outcome.status == 'OBSERVED_REFERENCE', outcome
    snapshot = validate_residency(rt)
    traces = {t.candidate_id: t for t in snapshot.event_traces if t.observation_id == observation_id}
    for candidate in snapshot.candidates:
        rules, graph, spec, state = models[candidate.candidate_id]
        observed = observe_event(graph, state, spec, predictions[candidate.candidate_id], y, bit_limit=32768)
        committed = commit_event(observed, spec, bit_limit=32768)
        trace = traces[candidate.candidate_id]
        check_state(trace.before, state)
        check_state(trace.after_observe, observed)
        check_state(trace.after_commit, committed)
        check_state(candidate.learner, committed)
        assert trace.after_observe.encoded.pending == event
        models[candidate.candidate_id] = rules, graph, spec, committed
    return len(traces)


def small_audit():
    histories = phases = 0
    groups = []
    for n in (2, 3):
        events = tuple(product(range(n), range(n), (0, 1)))
        cfg, schema, online = fixture(n, 2)
        count = 0
        for history in product(events, repeat=2):
            rt = ReferenceCompilerRuntime(cfg, schema, online=online)
            initial = validate_residency(rt).candidates[0]
            oracle = literal(n)
            check_state(initial.learner, oracle[3])
            models = {initial.candidate_id: oracle}
            for event in history:
                phases += step(rt, schema, event, models)
            histories += 1
            count += 1
        groups.append({'n': n, 'complete_length_two_histories': count})
    return {'groups': groups, 'owned_histories': histories, 'complete_prediction_observation_commit_comparisons': phases}


def profile_audit():
    cfg, schema, online = fixture(3, 7, profiles=(ProfileSpec('twice', ('indexed-event:0', 'indexed-event:1'), 2),))
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    models = {rt.snapshot().deployed_id: literal(3)}
    tape = ((0, 1, 0), (1, 2, 1), (2, 0, 0), (0, 0, 1), (1, 2, 0), (1, 0, 1), (2, 2, 0))
    phases = 0
    for cursor, event in enumerate(tape):
        phases += step(rt, schema, event, models)
        if cursor == 1:
            result = rt.construct_candidate(schema, profile_id='twice')
            assert result.status == 'BUILT_REFERENCE', result
            rules, graph, spec, state = literal(3)
            for trace in rt.snapshot().profile_events:
                i, j, y = tape[trace.position % 2]
                expected = evaluate(graph, rules, state.theta, native.context(3, i, j), (), bit_limit=32768)
                check_state(trace.before, state)
                check_prediction(trace.prediction, expected)
                observed = observe_event(graph, state, spec, expected, y, bit_limit=32768)
                check_state(trace.after_observe, observed)
                state = commit_event(observed, spec, bit_limit=32768)
                check_state(trace.after_commit, state)
            state = attach_boundary(state, 2, spec)
            models[result.candidate_id] = rules, graph, spec, state
            candidate = next(s for s in rt.snapshot().candidates if s.candidate_id == result.candidate_id)
            check_state(candidate.learner, state)
    snapshot = validate_residency(rt)
    assert sorted(c.learner.optimizer_steps for c in snapshot.candidates) == [7, 9]
    # Construction accepts no learned endpoint or externally supplied lease.
    before = rt.snapshot()
    rejects(lambda: rt.construct_candidate(schema, theta=()), TypeError)
    rejects(lambda: rt.construct_candidate(schema, objects=()), TypeError)
    assert rt.snapshot() == before
    return {'ordinary_component_phases': phases, 'profile_events': len(snapshot.profile_events),
            'ordinary_cursor': snapshot.cursor, 'optimizer_steps': [7, 9],
            'forbidden_value_or_resource_injection_refusals': 2}


def large_audit():
    n = 256
    cfg, schema, online = fixture(n, 4,
        profiles=(ProfileSpec('twice', ('indexed-event:0', 'indexed-event:1'), 2),))
    def forbidden(*args, **kwargs):
        raise AssertionError('indexed Runtime tried to materialize literal world tables')
    with patch.object(native, 'relation_graph', forbidden), patch.object(IndexedRelation, 'materialize_program', forbidden), \
            patch.object(IndexedRelation, 'materialize_learner', forbidden):
        rt = ReferenceCompilerRuntime(cfg, schema, online=online)
        forecasts = []
        for k, (i, j, y) in enumerate(((0, 1, 0), (0, 0, 0), (1, 2, 0), (0, 2, 1))):
            result = deliver_context(rt, online.data.active.observation_ids[k], tuple(schema.source_row(i*n+j).values()))
            assert result.status == 'PREDICTED_REFERENCE', result
            forecasts.append(dict(result.predictions)[rt.snapshot().deployed_id][0])
            assert rt.observe(y).status == 'OBSERVED_REFERENCE'
            if k == 1:
                result = rt.construct_candidate(schema, profile_id='twice')
                assert result.status == 'BUILT_REFERENCE', result
        snapshot = validate_residency(rt)
    assert forecasts == [F(1, 2), F(9, 10), F(1, 2), F(189, 250)]
    deployed = next(c for c in snapshot.candidates if c.candidate_id == snapshot.deployed_id)
    view = bound_view(schema, deployed.learner.encoded, (0, 1))
    for slot in (1, 2, schema.K//2, schema.K//2+1, schema.K):
        a, b = schema.world_bit(slot-1, 1), schema.world_bit(slot-1, 2)
        assert view.theta(slot) == F(1 if (a, b) == (1, 0) else 81, 61*schema.K)
    rejects(lambda: deployed.learner.materialize(scalar_cap=100000), ArithmeticUnresolved)
    rejects(lambda: snapshot.event_traces[-1].prediction.materialize(scalar_cap=100000), ArithmeticUnresolved)
    assert sorted(c.learner.optimizer_steps for c in snapshot.candidates) == [4, 6]
    return {'n': n, 'logical_worlds_power_of_two': n-1, 'actual_ingress_events': snapshot.cursor,
            'ordinary_component_phases': len(snapshot.event_traces), 'profile_events': len(snapshot.profile_events),
            'deployed_forecasts': [str(v) for v in forecasts], 'optimizer_steps': [4, 6],
            'explicit_full_output_refusals': 2, 'logical_graph_counts': schema.counts(),
            'packed_current_bytes': snapshot.resources['current']['reference_payload_bytes'],
            'scope': 'actual owned reference phases and packed leases; no total-process or comparative resource bound'}


def closure_audit():
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    models = {rt.snapshot().deployed_id: literal(3)}
    for event in ((0, 1, 0), (1, 2, 0), (0, 2, 1)):
        step(rt, schema, event, models)
    snapshot = validate_residency(rt)
    assert snapshot.run.status == 'SEALED_REFERENCE_STREAM'
    assert not snapshot.run.closure.decisions
    assert snapshot.run.manifest.machine_id == IndexedReferenceMachine.model_id
    assert snapshot.run.manifest.reference_arithmetic == 'indexed-literal-count-positive-query-block-reference-v1'
    rejects(lambda: rt.construct_candidate(schema))
    return {'status': snapshot.run.status, 'events': snapshot.cursor,
            'scope': 'owned empty Compiler strategy and finite ordinary stream; no class-optimality or install claim'}


def adversaries():
    cfg, schema, online = fixture(3, 3)
    wrong = IndexedRelation(2)
    for function in (
        lambda: replace(cfg, source_domain=CategoricalPairDomain(2)),
        lambda: replace(cfg, initializer_pattern=IndexedInitializer(2)),
        lambda: replace(cfg, source_domain=None),
        lambda: ReferenceCompilerRuntime(cfg, schema, online=replace(online, learner=IndexedLearner(2))),
        lambda: ReferenceCompilerRuntime(cfg, schema),
        lambda: ReferenceCompilerRuntime(cfg, wrong, online=online)):
        rejects(function)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    assert rt.construct_candidate(object()).status == 'REJECTED_ADMISSIBILITY'
    # A real native description unsupported by this physical encoder is
    # unresolved, not a theorem that its native semantics are inadmissible.
    literal_graph = schema.materialize_program(node_cap=1000, term_cap=10000, slot_cap=100)
    assert rt.construct_candidate(literal_graph).status == 'UNRESOLVED'
    before = rt.snapshot()
    fake = IndexedState(before.candidates[0].learner.encoded)
    assert rt.construct_candidate(fake).status == 'REJECTED_ADMISSIBILITY'
    assert rt.snapshot().candidates == before.candidates
    rejects(lambda: rt.observe(0))
    assert deliver_context(rt, online.data.active.observation_ids[0], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
    locked = rt.snapshot()
    rejects(lambda: rt.construct_candidate(schema))
    assert rt.snapshot() == locked
    rejects(lambda: rt.observe(2))
    assert rt.snapshot() == locked
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    assert rt.snapshot().event_traces[-1].after_observe.encoded.pending == (0, 1, 0)

    invalid = ReferenceCompilerRuntime(cfg, schema, online=online)
    before = invalid.snapshot()
    rejects(lambda: deliver_context(invalid, online.data.active.observation_ids[0], (F(0),)*6))
    after = validate_residency(invalid)
    assert after.cursor == 0 and after.candidates == before.candidates and after.halted is not None
    assert after.ingress and len(after.buffers) > len(before.buffers)
    rejects(lambda: invalid.observe(0))

    def forbidden(*args, **kwargs):
        raise AssertionError('an unfunded numerical phase executed')
    # The actual deployment work cap is too small to enter prediction. The
    # independent Compiler allowance still funds and retains received data.
    narrow = replace(cfg, limits=replace(cfg.limits, role_cumulative={
        'deployment': {'work': 1}, 'compiler': {'work': 10**14}}))
    denied = ReferenceCompilerRuntime(narrow, schema, online=online)
    with patch.object(IndexedReferenceMachine, 'prepare_prediction', forbidden), \
            patch.object(IndexedReferenceMachine, 'execute_prediction', forbidden):
        result = deliver_context(denied, online.data.active.observation_ids[0], tuple(schema.source_row(1).values()))
    assert result.status == 'UNRESOLVED', result
    stopped = validate_residency(denied)
    assert stopped.pending.record.target is None and stopped.pending.record.sources
    assert stopped.resources['spent']['deployment']['work'] == 0 and stopped.halted is not None

    # Planning and numeric execution have separate owned debits. Funding
    # only the complete planning ceiling must never enter the table kernel.
    planning = IndexedReferenceMachine(3, indexed.DecodeAllowance()).evaluation_work(schema, cfg.semantics)
    planning_only = replace(cfg, limits=replace(cfg.limits, role_cumulative={
        'deployment': {'work': planning}, 'compiler': {'work': 10**14}}))
    denied_execution = ReferenceCompilerRuntime(planning_only, schema, online=online)
    with patch.object(IndexedReferenceMachine, 'execute_prediction', forbidden):
        result = deliver_context(denied_execution, online.data.active.observation_ids[0], tuple(schema.source_row(1).values()))
    assert result.status == 'UNRESOLVED', result
    stopped = validate_residency(denied_execution)
    assert stopped.pending.record.target is None and stopped.pending.record.sources
    assert stopped.resources['spent']['deployment']['work'] == planning and stopped.halted is not None

    # A conservative exact-integer allowance is solver uncertainty. Both
    # already completed observations and the newly received context survive.
    bounded = ReferenceCompilerRuntime(replace(cfg, reference_integer_bits=15), schema, online=online)
    models = {bounded.snapshot().deployed_id: literal(3)}
    step(bounded, schema, (0, 1, 0), models)
    step(bounded, schema, (0, 1, 0), models)
    before = bounded.snapshot()
    with patch.object(indexed.partition, 'decode', forbidden):
        result = deliver_context(bounded, online.data.active.observation_ids[2], tuple(schema.source_row(1).values()))
    assert result.status == 'UNRESOLVED', result
    after = validate_residency(bounded)
    assert after.cursor == 2 and after.observations == before.observations and after.candidates == before.candidates
    assert after.pending.record.observation_id == online.data.active.observation_ids[2]

    # The fixed natural order can become expensive even on a tree. Build a
    # star through actual observations while its center is kept in each
    # query; a subsequent leaf query would eliminate that center first.
    # The new block response must recover that query without dropping any
    # count; the old global preflight remains an independent refusal witness.
    tree_cfg, tree_schema, tree_online = fixture(15, 14)
    tree = ReferenceCompilerRuntime(tree_cfg, tree_schema, online=tree_online)
    for k, leaf in enumerate(range(2, 15)):
        result = deliver_context(tree, tree_online.data.active.observation_ids[k],
            tuple(tree_schema.source_row(15+leaf).values()))
        assert result.status == 'PREDICTED_REFERENCE' and result.predictions[0][1] == (F(1, 2), F(1, 2))
        assert tree.observe(0).status == 'OBSERVED_REFERENCE'
    before = tree.snapshot()
    # The old global schedule still refuses; the owned block projection
    # now computes the required two-edge response, retaining all13 counts.
    rejects(lambda: indexed.partition_plan(before.candidates[0].learner.encoded,
        (2,3),tuple(range(14)),indexed.DecodeAllowance()),ArithmeticUnresolved)
    result = deliver_context(tree, tree_online.data.active.observation_ids[13],
        tuple(tree_schema.source_row(2*15+3).values()))
    assert result.status == 'PREDICTED_REFERENCE' and result.predictions[0][1][0] == F(189,250), result
    after = validate_residency(tree)
    assert after.cursor == 13 and after.observations == before.observations and after.candidates == before.candidates
    assert after.pending.record.sources and after.pending.record.target is None
    prediction = after.pending.predictions[0][1]
    assert prediction.before == before.candidates[0].learner.encoded
    assert dict(prediction.table_work)['projected_active_edges'] == 2

    # The first candidate completes its local commit; the second fails.
    # Neither published learner advances, and both the target and all
    # completed/observed local phases remain in the same owned root.
    failed = ReferenceCompilerRuntime(cfg, schema, online=online)
    assert failed.construct_candidate(schema).status == 'BUILT_REFERENCE'
    initial = failed.snapshot()
    assert deliver_context(failed, online.data.active.observation_ids[0], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
    original = IndexedReferenceMachine.commit
    calls = 0
    def fail_second(machine, *args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ArithmeticUnresolved('injected second-lineage commit uncertainty')
        return original(machine, *args, **kwargs)
    with patch.object(IndexedReferenceMachine, 'commit', fail_second):
        result = failed.observe(0)
    assert result.status == 'UNRESOLVED' and calls == 2
    after = validate_residency(failed)
    assert after.cursor == 0 and after.candidates == initial.candidates
    assert after.observations[-1].target == after.pending.record.target == 0
    assert len(after.event_traces) == 2
    assert after.event_traces[0].after_commit is not None and after.event_traces[1].after_commit is None
    assert all(t.after_observe.encoded.pending == (0, 1, 0) for t in after.event_traces)
    rules, graph, spec, state = literal(3)
    prediction = evaluate(graph, rules, state.theta, native.context(3, 0, 1), (), bit_limit=32768)
    observed = observe_event(graph, state, spec, prediction, 0, bit_limit=32768)
    for trace in after.event_traces:
        check_state(trace.after_observe, observed)
    assert failed.install(after.candidates[1].candidate_id, certified=True, bridge=True).status == 'UNRESOLVED'
    return {'registration_binding_refusals': 6, 'unimplemented_native_translation_unresolved': 1,
            'invalid_structure_or_supplied_state_refusals': 2, 'locked_or_invalid_target_refusals': 4,
            'bad_domain_retained_ingress': True, 'unfunded_deployment_prediction_refused_before_executor': True,
            'planning_funded_but_table_execution_refused_before_executor': True,
            'integer_allowance_refused_before_partition': True,
            'actual_star_history_events_before_projection_recovery': 13,
            'old_global_width_refusal_verified_before_tables': True,
            'owned_star_query_recovered_with_complete_history': True,
            'second_lineage_failure_retains_target_and_both_observed_states': True,
            'published_learners_advanced_on_failure': 0, 'helper_install_authority': False}


def persistence_audit():
    registration = PersistenceContract(F(1, 2), (PersistenceRule('fresh', 1, 20, F(1, 4), F(3, 4), F(3), 12, 16),))
    cfg, schema, online = fixture(2, 36, persistence=registration, law=True)
    rules, graph, spec, _ = literal(2)
    native_cfg = replace(cfg, initializer_pattern=(F(1), F(1, 2), F(1, 2)),
        source_domain=tuple(tuple(schema.source_row(k).values()) for k in range(4)))
    native_online = replace(online, learner=spec)
    executions = (ReferenceCompilerRuntime(cfg, schema, online=online),
                  ReferenceCompilerRuntime(native_cfg, graph, online=native_online))
    candidates = []
    for rt, program in zip(executions, (schema, graph)):
        for cursor in range(16):
            assert deliver_context(rt, online.data.active.observation_ids[cursor], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(1).status == 'OBSERVED_REFERENCE'
        born = rt.construct_candidate(program)
        assert born.status == 'BUILT_REFERENCE'
        candidates.append(born.candidate_id)
        admission = rt.admit_reference_persistence(born.candidate_id, 'fresh')
        assert admission.status == 'UNRESOLVED' and admission.identity_id, admission
        assert rt.snapshot().persistence_identities[0].status == 'ACTIVE'
        assert rt.snapshot().persistence_identities[0].start_cursor == 16
        assert not rt.snapshot().persistence_events
    # A foreign root's valid candidate name is still not local ownership.
    before = executions[0].snapshot()
    rejects(lambda: executions[0].admit_reference_persistence(candidates[1], 'fresh'))
    assert executions[0].snapshot() == before
    comparisons = 0
    for cursor in range(16, 36):
        for rt in executions:
            assert deliver_context(rt, online.data.active.observation_ids[cursor], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        compact, expanded = (validate_residency(rt) for rt in executions)
        a, b = compact.persistence_identities[0], expanded.persistence_identities[0]
        for key in ('start_cursor', 'cursor', 'epoch_events', 'epochs_completed', 'gain_lower_sum', 'gain_upper_sum',
                    'wealth', 'ratio_bound', 'crossing_cursor', 'crossing_wealth', 'status', 'ratio_bound_kind'):
            assert getattr(a, key) == getattr(b, key), key
        for key in ('initial_base', 'initial_candidate', 'current_base', 'current_candidate'):
            check_state(getattr(a, key), getattr(b, key))
        assert len(compact.persistence_events) == len(expanded.persistence_events)
        for x, y in zip(compact.persistence_events, expanded.persistence_events):
            for key in ('observation_id', 'cursor', 'base_probability', 'candidate_probability', 'gain',
                        'epoch_finished', 'wealth_before', 'wealth_after', 'score_path'):
                assert getattr(x, key) == getattr(y, key), key
        assert all(e.cursor >= 16 for e in compact.persistence_events)
        comparisons += 1
    rt = executions[0]
    current = rt.snapshot().persistence_identities[0]
    assert current.status == 'REFERENCE_CROSSED' and current.crossing_cursor > 16
    assert rt.install(candidates[0], certified=True, bridge=True).status == 'UNRESOLVED'
    rt.retire_candidate(candidates[0])
    final = validate_residency(rt)
    assert final.alpha_spent == F(1, 4) and len(final.alpha_allocations) == 1
    assert final.persistence_identities[0].status == 'UNRESOLVED'
    assert 'lineage retired' in final.persistence_identities[0].reason
    assert final.persistence_events
    return {'fresh_start_cursor': 16, 'ordinary_events': 36, 'paired_native_root_comparisons': comparisons,
            'crossing_cursor': current.crossing_cursor, 'crossing_wealth': str(current.crossing_wealth),
            'fresh_score_events': len(final.persistence_events), 'alpha_after_retirement': str(final.alpha_spent),
            'foreign_root_admission_refusals': 1, 'unpaired_installation': 'UNRESOLVED',
            'scope': 'exact same-path reference statistic under a declared external law; finite tape proves no stochastic law'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--section', choices=('small', 'profile', 'large', 'closure', 'adversaries', 'persistence'))
    args = parser.parse_args()
    if args.write and args.section is not None:
        parser.error('canonical evidence requires the complete audit, without --section')
    functions = {'small': small_audit, 'profile': profile_audit, 'large': large_audit, 'closure': closure_audit,
                 'adversaries': adversaries, 'persistence': persistence_audit}
    report = {'status': 'PASS', 'complete_audit': args.section is None,
              'scope': 'owned indexed exact reference execution; no new complete AMP or installation release'}
    for name, function in functions.items():
        if args.section in (None, name):
            report[name] = function()
    if args.write:
        assert args.section is None
        (ROOT/'evidence/minimal/FP_INDEXED_RUNTIME.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
