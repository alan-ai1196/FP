"""Audit the actual owned joint-noise Reference Runtime continuation.

Exact native controls, actual ingress/ledger/profile/freshness, and adversarial
failure boundaries. No actual CUDA or constructor-completeness authority.
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference import runtime as owner
from fp_reference.core import ContractError
from fp_reference.cuda_prefix import CudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.data_usage import DataContract, StreamSpec, SourceRead, StochasticStreamLaw
from fp_reference.encoding import pack
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_execution import CategoricalPairDomain, IndexedInitializer, IndexedLearner
from fp_reference.joint_execution import (JointInitializer, JointLearner, JointState, JointEvaluation,
    JointReferenceMachine, MODEL_ID, ARITHMETIC_ID)
from fp_reference.joint_relation import JointRelation
from fp_reference import joint_partition_decoder as decoder
from fp_reference.learner import initial_state, observe_event, commit_event
from fp_reference.persistence import PersistenceContract, PersistenceRule
from fp_reference.profile import ProfileSpec, attach_boundary
from fp_reference.resources import ResourceExceeded
from fp_reference.runtime import ConstructionContract, OnlineContract
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_reference_construction import limits, rejects, validate_residency
from ingress_audit_support import deliver_context
import audit_mixture_partition_bridge as native
import mixture_partition_bridge as prototype
from unknown_noise_decoding import DEFAULT, OTHER

OUTPUT = ROOT/'evidence/minimal/FP_JOINT_REFERENCE_RUNTIME.json'
BUDGET = decoder.JointPartitionAllowance(join_cells=32, live_cells=128, arithmetic=4096, step_cap=256)


def fixture(n, length, *, family=DEFAULT, profiles=(), persistence=None, law=False,
            budget=BUDGET, byte_cap=128 << 20, work_cap=10**14):
    schema = JointRelation(n, *family)
    rules = schema.rules()
    ids = tuple(f'joint-event:{k}' for k in range(length))
    cfg = ConstructionContract(rules, limits(byte_cap, work_cap),
        {'construct': 'compiler', 'range_audit': 'compiler'},
        {k: schema.counts()[k] for k in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots')},
        JointInitializer(schema), F(schema.scale), F(schema.scale-2), 32768,
        CategoricalPairDomain(n), indexed_histogram=budget)
    data = DataContract((StreamSpec('online', 'online', ids),), 'online', (F(1),)*(2*n),
        tuple(SourceRead(source.source_id, 'input', k, 0) for k, source in enumerate(rules.sources)))
    if law:
        data = replace(data, stream_law=StochasticStreamLaw('external stochastic producer assumption; audit tapes prove no law'))
    online = OnlineContract(data, JointLearner(schema), profiles=profiles, persistence=persistence)
    return cfg, schema, online


def literal(schema, cursor=0):
    bank, rules, graph, spec, _ = native.small_native(prototype.Model(schema.n, schema.rates, schema.prior))
    state = initial_state(graph, rules, (F(1),)+bank.prior, cursor, spec=spec, bit_limit=32768)
    return rules, graph, spec, state


def check_state(actual, expected, budget=BUDGET):
    assert type(actual) is JointState
    assert actual.materialize(scalar_cap=10000, budget=budget) == expected


def check_prediction(actual, expected):
    assert type(actual) is JointEvaluation
    assert actual.materialize(scalar_cap=10000) == expected


def predict(runtime, schema, query):
    cursor = runtime.snapshot().cursor
    return deliver_context(runtime, runtime.online_contract.data.active.observation_ids[cursor],
                           tuple(schema.source_row(query[0]*schema.n+query[1]).values()))


def step(runtime, schema, event, models, budget=BUDGET):
    u, v, target = event
    outcome = predict(runtime, schema, (u, v))
    assert outcome.status == 'PREDICTED_REFERENCE', outcome
    pending = validate_residency(runtime).pending
    assert pending.record.target is None
    expected_predictions = {}
    for candidate, prediction in pending.predictions:
        rules, graph, spec, state = models[candidate]
        expected = evaluate(graph, rules, state.theta, schema.source_row(u*schema.n+v), (), bit_limit=32768)
        check_prediction(prediction, expected)
        expected_predictions[candidate] = expected
    result = runtime.observe(target)
    assert result.status == 'OBSERVED_REFERENCE', result
    after = validate_residency(runtime)
    traces = {t.candidate_id: t for t in after.event_traces if t.observation_id == pending.record.observation_id}
    for candidate in after.candidates:
        rules, graph, spec, previous = models[candidate.candidate_id]
        observed = observe_event(graph, previous, spec, expected_predictions[candidate.candidate_id], target, bit_limit=32768)
        committed = commit_event(observed, spec, bit_limit=32768)
        trace = traces[candidate.candidate_id]
        for actual, expected in ((trace.before, previous), (trace.after_observe, observed),
                                 (trace.after_commit, committed), (candidate.learner, committed)):
            check_state(actual, expected, budget)
        assert trace.after_observe.encoded.pending == event
        models[candidate.candidate_id] = rules, graph, spec, committed
    return len(traces)


def small():
    rows = []
    for n, family in ((2, DEFAULT), (3, DEFAULT), (2, OTHER), (2, ((F(1, 3),), (F(1),)))):
        cfg, schema, online = fixture(n, 2, family=family)
        histories = triples = 0
        for word in product(tuple(product(range(n), range(n), (0, 1))), repeat=2):
            runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
            initial = validate_residency(runtime)
            models = {initial.deployed_id: literal(schema)}
            check_state(initial.candidates[0].learner, models[initial.deployed_id][3])
            for event in word:
                triples += step(runtime, schema, event, models)
            histories += 1
        rows.append({'n': n, 'rates': tuple(map(str, schema.rates)), 'all_two_event_histories': histories,
                     'owned_native_triples': triples})
    return rows


def profile():
    declared = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
    cfg, schema, online = fixture(3, 8, profiles=(declared,))
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    models = {runtime.snapshot().deployed_id: literal(schema)}
    phases = 0
    word = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 1), (2, 2, 0), (1, 0, 1), (0, 1, 0))
    for at, event in enumerate(word):
        phases += step(runtime, schema, event, models)
        if at == 1:
            result = runtime.construct_candidate(schema, profile_id='twice')
            assert result.status == 'BUILT_REFERENCE', result
            rules, graph, spec, state = literal(schema)
            snapshot = validate_residency(runtime)
            events = [e for e in snapshot.profile_events if e.candidate_id == result.candidate_id]
            assert len(events) == 4
            for record, (u, v, y) in zip(events, word[:2]*2):
                expected = evaluate(graph, rules, state.theta, schema.source_row(u*3+v), (), bit_limit=32768)
                check_state(record.before, state)
                check_prediction(record.prediction, expected)
                observed = observe_event(graph, state, spec, expected, y, bit_limit=32768)
                check_state(record.after_observe, observed)
                state = commit_event(observed, spec, bit_limit=32768)
                check_state(record.after_commit, state)
            state = attach_boundary(state, 2, spec)
            models[result.candidate_id] = rules, graph, spec, state
            born = next(s for s in snapshot.candidates if s.candidate_id == result.candidate_id)
            check_state(born.learner, state)
            assert born.learner.encoded.steps == 4 and born.learner.cursor == born.birth_cursor == 2
    final = validate_residency(runtime)
    assert sorted(s.learner.optimizer_steps for s in final.candidates) == [8, 10]
    old = runtime.snapshot()
    rejects(lambda: runtime.construct_candidate(schema, theta=()), TypeError)
    rejects(lambda: runtime.construct_candidate(schema, plan=object()), TypeError)
    assert runtime.snapshot() == old
    return {'ordinary_native_triples': phases, 'profile_native_triples': 4,
            'ordinary_cursor': final.cursor, 'optimizer_steps': [8, 10],
            'supplied_state_or_plan_refusals': 2, 'closing_cycle_canceling_edge_and_diagonal_evidence': True}


def larger_and_closure():
    n = 64
    budget = replace(BUDGET, join_cells=64, live_cells=1024, arithmetic=32768, step_cap=32)
    cfg, schema, online = fixture(n, 8, budget=budget)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    word = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 0), (3, 4, 1), (0, 4, 0), (4, 0, 1))
    expected = prototype.initialize(prototype.Model(n, *DEFAULT))
    probabilities = []
    with patch.object(JointRelation, 'materialize_program', side_effect=AssertionError('world expansion')), \
            patch.object(JointRelation, 'materialize_learner', side_effect=AssertionError('slot expansion')):
        for u, v, y in word:
            result = predict(runtime, schema, (u, v))
            plan = prototype.prepare(expected, (u, v))
            forecast = prototype.reference(plan)[5:]
            assert result.status == 'PREDICTED_REFERENCE' and result.predictions[0][1] == forecast
            probabilities.append(tuple(map(str, forecast)))
            assert runtime.observe(y).status == 'OBSERVED_REFERENCE'
            expected = prototype.commit(prototype.observe(expected, (u, v), y))
    final = validate_residency(runtime)
    actual = final.candidates[0].learner.encoded
    assert (actual.counts, actual.diagonal, actual.steps, actual.cursor) == (
        expected.counts, expected.diagonal, expected.steps, expected.cursor)
    rejects(lambda: final.candidates[0].learner.materialize(scalar_cap=100000, budget=budget), ArithmeticUnresolved)
    rejects(lambda: final.event_traces[-1].prediction.materialize(scalar_cap=100000), ArithmeticUnresolved)
    assert final.run.status == 'SEALED_REFERENCE_STREAM' and not final.run.closure.decisions
    assert final.run.manifest.machine_id == MODEL_ID and final.run.manifest.reference_arithmetic == ARITHMETIC_ID
    return {'n': n, 'native_worlds': str(schema.K), 'ordinary_events': final.cursor,
            'predictions': probabilities, 'status': final.run.status, 'constructor_decisions': 0,
            'actual_workspace_bytes': decoder.workspace_bytes(schema, budget),
            'packed_peak_bytes': final.resources['peak']['reference_payload_bytes'],
            'full_output_refusals_before_world_expansion': 2,
            'complete_counts_diagonal_and_clocks_agree': True}


def funding():
    cfg, schema, online = fixture(3, 3)
    planning = JointReferenceMachine(schema, BUDGET).evaluation_work(schema, cfg.semantics)
    rows = []
    for name, cap in (('before-integer-construction', planning-1), ('before-rational-readout', planning)):
        limited = replace(cfg, limits=replace(cfg.limits, role_cumulative={
            'deployment': {'work': cap}, 'compiler': {'work': 10**14}}))
        runtime = ReferenceCompilerRuntime(limited, schema, online=online)
        before = validate_residency(runtime)
        denied = '_prepare_joint_prediction' if cap < planning else '_execute_joint_prediction'
        with patch.object(owner, denied, side_effect=AssertionError('unfunded kernel entered')) as forbidden:
            result = predict(runtime, schema, (0, 1))
        after = validate_residency(runtime)
        assert result.status == 'UNRESOLVED' and not forbidden.called
        assert after.candidates == before.candidates and after.cursor == 0
        assert after.pending.record.target is None and not after.pending.predictions
        assert after.resources['spent']['deployment']['work'] == (0 if cap < planning else planning)
        rows.append({'case': name, 'status': result.status, 'unfunded_kernel_entries': 0})
    # A zero signed count is still two actual likelihood factors. Commit the
    # cancellation before trying another query against a one-step decoder cap.
    budget = replace(BUDGET, step_cap=1)
    runtime = ReferenceCompilerRuntime(replace(cfg, indexed_histogram=budget), schema, online=online)
    for target in (0, 1):
        assert predict(runtime, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
    before = validate_residency(runtime)
    encoded = before.candidates[0].learner.encoded
    assert encoded.counts == (0, 0, 0) and encoded.steps == 2
    key = next(k for k, _ in before.buffers if k.endswith(':joint-partition-storage'))
    result = predict(runtime, schema, (0, 1))
    after = validate_residency(runtime)
    assert result.status == 'UNRESOLVED' and after.candidates == before.candidates
    assert dict(after.buffers)[key] == dict(before.buffers)[key]
    assert after.pending.record.target is None and after.cursor == 2
    return {'kernel_debit_boundaries': rows, 'canceled_history_refusal': {'status': result.status,
            'committed_steps': 2, 'absolute_count_sum': 0, 'scratch_unchanged': True},
            'scope': 'actual packed-payload/work ledger, not total host memory or wall time'}


def workspace_lifetime():
    cfg, schema, online = fixture(3, 3)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    key = next(k for k in runtime._buffers if k.endswith(':joint-partition-storage'))
    extent = runtime._buffers[key]
    size = decoder.workspace_bytes(schema, BUDGET)
    assert len(extent) == size
    original = owner._prepare_joint_prediction
    visits = []
    def monitored(program, rules, state, sources, budget, borrowed, **kwargs):
        assert borrowed is not extent and borrowed.obj is extent.obj
        entries = [e for e in runtime.snapshot().resources['events'] if str(e[-1]).endswith(':predict')]
        assert entries and dict(entries[-1][4])['work'] == decoder.construction_work(schema, BUDGET)
        result = original(program, rules, state, sources, budget, borrowed, **kwargs)
        borrowed.release()
        rejects(lambda: extent.obj.extend(b'x'), BufferError)
        visits.append(result.compacted_cells)
        return result
    with patch.object(owner, '_prepare_joint_prediction', monitored):
        assert predict(runtime, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
    prior = validate_residency(runtime)
    prior_history = pack(prior.event_traces)
    def fail_after_build(*args, **kwargs):
        original(*args, **kwargs)
        raise ArithmeticUnresolved('injected uncertainty after joint integer construction')
    with patch.object(owner, '_prepare_joint_prediction', fail_after_build):
        result = predict(runtime, schema, (1, 2))
    after = validate_residency(runtime)
    assert result.status == 'UNRESOLVED' and after.candidates == prior.candidates and after.cursor == 1
    assert after.observations == prior.observations and pack(after.event_traces) == prior_history
    assert key in after.resources['objects'] and len(dict(after.buffers)[key]) == size
    assert after.resources['objects'][key]['references']
    assert runtime._buffers[key] is extent
    rejects(lambda: extent.obj.extend(b'x'), BufferError)
    return {'successful_borrowed_compaction_counts': visits, 'actual_retained_workspace_bytes': size,
            'after_construction_failure': result.status, 'old_history_and_learners_unchanged': True,
            'failed_scratch_still_owned_and_pinned': True}


def resource_continuation():
    cfg, schema, online = fixture(3, 10)
    size = decoder.workspace_bytes(schema, BUDGET)
    allocations = []
    def allocate(value):
        assert value != size, 'unfunded joint table allocation entered'
        allocations.append(value)
        return bytearray(value)
    # The manifest fits; the table alone exceeds the complete byte cap.
    with patch.object(owner, 'bytearray', allocate, create=True):
        rejects(lambda: ReferenceCompilerRuntime(replace(cfg, limits=limits(size-1, 10**14)), schema,
                                                online=online), ResourceExceeded)
    assert allocations

    bounded = ReferenceCompilerRuntime(replace(cfg, reference_integer_bits=1075), schema, online=online)
    for k in range(9):
        assert predict(bounded, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert bounded.observe(k % 2).status == 'OBSERVED_REFERENCE'
    before = validate_residency(bounded)
    key = next(k for k, _ in before.buffers if k.endswith(':joint-partition-storage'))
    result = predict(bounded, schema, (0, 1))
    after = validate_residency(bounded)
    assert result.status == 'UNRESOLVED' and after.cursor == 9
    assert after.candidates == before.candidates and after.observations == before.observations
    assert dict(after.buffers)[key] == dict(before.buffers)[key]
    assert after.pending.record.target is None

    # Complete support can outgrow this fixed order's table cap on a new
    # query, even though every preceding observation was decoded legally.
    budget = replace(BUDGET, join_cells=8)
    tree_cfg, tree_schema, tree_online = fixture(6, 5, budget=budget)
    tree = ReferenceCompilerRuntime(tree_cfg, tree_schema, online=tree_online)
    # Vertex zero is anchored, so use the first free vertex as the center.
    for leaf in range(2, 6):
        assert predict(tree, tree_schema, (1, leaf)).status == 'PREDICTED_REFERENCE'
        assert tree.observe(0).status == 'OBSERVED_REFERENCE'
    prior = validate_residency(tree)
    key = next(k for k, _ in prior.buffers if k.endswith(':joint-partition-storage'))
    result = predict(tree, tree_schema, (2, 3))
    stopped = validate_residency(tree)
    assert result.status == 'UNRESOLVED' and stopped.cursor == 4
    assert stopped.candidates == prior.candidates and stopped.observations == prior.observations
    assert dict(stopped.buffers)[key] == dict(prior.buffers)[key]
    assert sum(bool(v) for v in stopped.candidates[0].learner.encoded.counts) == 4

    declared = ProfileSpec('too-many-steps', ('joint-event:0', 'joint-event:1'), 2)
    profile_cfg, model, profile_online = fixture(3, 3, profiles=(declared,), budget=replace(BUDGET, step_cap=1))
    replay = ReferenceCompilerRuntime(profile_cfg, model, online=profile_online)
    for target in (0, 1):
        assert predict(replay, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert replay.observe(target).status == 'OBSERVED_REFERENCE'
    old = validate_residency(replay)
    result = replay.construct_candidate(model, profile_id=declared.profile_id)
    failed = validate_residency(replay)
    assert result.status == 'UNRESOLVED' and failed.candidates == old.candidates and failed.cursor == 2
    record = failed.profiles[0]
    assert record.status == 'UNRESOLVED' and record.events_completed == 2 and record.attached is None
    assert record.local.encoded.steps == 2 and not any(record.local.encoded.counts)
    assert len(failed.profile_events) == 2 and all(e.after_commit is not None for e in failed.profile_events)
    assert any(k.endswith(':joint-partition-storage') for k in failed.resources['objects'])
    return {'scratch_cap': size-1, 'unfunded_table_allocations': 0,
            'precision_refusal_cursor': 9, 'tree_query_width_refusal_cursor': 4,
            'prewrite_precision_and_width_refusals_preserve_state_and_scratch': True,
            'failed_profile_completed_steps': 2, 'failed_profile_absolute_count_sum': 0,
            'failed_profile_attached_or_published': False, 'scope': 'fixed algorithm allowance exhaustion, no impossibility certificate'}


def bindings_and_atomic_failure():
    cfg, schema, online = fixture(3, 3)
    wrong = JointRelation(3, schema.rates[::-1], schema.prior)
    registrations = [lambda: replace(cfg, source_domain=None),
        lambda: replace(cfg, source_domain=CategoricalPairDomain(2)),
        lambda: replace(cfg, indexed_histogram=None), lambda: replace(cfg, indexed_order_search=True),
        lambda: ReferenceCompilerRuntime(cfg, schema),
        lambda: ReferenceCompilerRuntime(cfg, schema, online=replace(online, learner=JointLearner(wrong))),
        lambda: ReferenceCompilerRuntime(cfg, schema, online=replace(online, learner=IndexedLearner(3))),
        lambda: replace(cfg, initializer_pattern=IndexedInitializer(3)),
        lambda: ReferenceCompilerRuntime(cfg, schema, online=replace(online, float64=Float64Contract(F(1, 100), F(1, 1000))))]
    for check in registrations:
        rejects(check)
    gpu = CudaPrefixContract(CudaStorageContract(512, 2 << 20,
        {role: (512, 2 << 20) for role in ('deployment', 'compiler')}), F(1, 100), F(1, 1000))
    with patch.object(owner, '_CudaPrefix', side_effect=AssertionError('unregistered device execution')) as forbidden:
        rejects(lambda: ReferenceCompilerRuntime(cfg, schema, online=online, cuda=gpu))
        assert not forbidden.called
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    assert runtime.construct_candidate(wrong).status == 'REJECTED_ADMISSIBILITY'
    graph = literal(schema)[1]
    assert runtime.construct_candidate(graph).status == 'UNRESOLVED'
    assert runtime.construct_candidate(runtime.snapshot().candidates[0].learner).status == 'REJECTED_ADMISSIBILITY'
    assert runtime.construct_candidate(schema).status == 'BUILT_REFERENCE'
    before = validate_residency(runtime)
    assert predict(runtime, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    locked = runtime.snapshot()
    rejects(lambda: runtime.construct_candidate(schema))
    rejects(lambda: runtime.observe(True))
    rejects(lambda: runtime.observe(2))
    assert runtime.snapshot() == locked
    original = JointReferenceMachine.commit
    calls = 0
    def fail_second(machine, *args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ArithmeticUnresolved('injected second joint-lineage commit uncertainty')
        return original(machine, *args, **kwargs)
    with patch.object(JointReferenceMachine, 'commit', fail_second):
        result = runtime.observe(0)
    after = validate_residency(runtime)
    assert result.status == 'UNRESOLVED' and calls == 2 and after.cursor == 0
    assert after.candidates == before.candidates and after.pending.record.target == 0
    assert after.observations[-1].target == 0 and len(after.event_traces) == 2
    assert after.event_traces[0].after_commit is not None and after.event_traces[1].after_commit is None
    assert all(t.after_observe.encoded.pending == (0, 1, 0) for t in after.event_traces)
    rules, graph, spec, initial = literal(schema)
    prediction = evaluate(graph, rules, initial.theta, schema.source_row(1), (), bit_limit=32768)
    observed = observe_event(graph, initial, spec, prediction, 0, bit_limit=32768)
    for trace in after.event_traces:
        check_state(trace.after_observe, observed)
    assert runtime.install(after.candidates[1].candidate_id, certified=True, bridge=True).status == 'UNRESOLVED'
    invalid = ReferenceCompilerRuntime(cfg, schema, online=online)
    rejects(lambda: deliver_context(invalid, online.data.active.observation_ids[0], (F(0),)*6))
    bad = validate_residency(invalid)
    assert bad.halted is not None and bad.cursor == 0 and bad.ingress
    return {'registration_refusals': len(registrations), 'wrong_model_or_supplied_state_refusals': 2,
            'unregistered_cuda_refusals_before_device_creation': 1,
            'unsupported_literal_translation': 'UNRESOLVED', 'locked_or_bad_target_refusals': 3,
            'both_observed_states_and_actual_target_retained': True, 'published_successors_on_second_failure': 0,
            'retained_invalid_categorical_ingress': True, 'supplied_install_flags': 'UNRESOLVED'}


def fresh_reference():
    registration = PersistenceContract(F(1, 2), (PersistenceRule('fresh', 1, 20, F(1, 4), F(3, 4), F(3), 12, 16),))
    cfg, schema, online = fixture(2, 36, persistence=registration, law=True)
    rules, graph, spec, initial = literal(schema)
    native_cfg = replace(cfg, initializer_pattern=initial.theta, indexed_histogram=None,
        source_domain=tuple(tuple(schema.source_row(k).values()) for k in range(4)))
    native_online = replace(online, learner=spec)
    roots = (ReferenceCompilerRuntime(cfg, schema, online=online),
             ReferenceCompilerRuntime(native_cfg, graph, online=native_online))
    candidates = []
    for runtime, program in zip(roots, (schema, graph)):
        for _ in range(16):
            assert predict(runtime, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            assert runtime.observe(1).status == 'OBSERVED_REFERENCE'
        born = runtime.construct_candidate(program)
        assert born.status == 'BUILT_REFERENCE'
        candidates.append(born.candidate_id)
        result = runtime.admit_reference_persistence(born.candidate_id, 'fresh')
        assert result.status == 'UNRESOLVED' and result.identity_id
        snapshot = validate_residency(runtime)
        assert snapshot.persistence_identities[0].start_cursor == 16 and not snapshot.persistence_events
    saved = roots[0].snapshot()
    rejects(lambda: roots[0].admit_reference_persistence(candidates[1], 'fresh'))
    assert roots[0].snapshot() == saved
    comparisons = 0
    for _ in range(20):
        for runtime in roots:
            assert predict(runtime, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
        compact, expanded = (validate_residency(runtime) for runtime in roots)
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
    current = roots[0].snapshot().persistence_identities[0]
    assert current.status == 'REFERENCE_CROSSED' and current.crossing_cursor > 16
    assert roots[0].install(candidates[0], certified=True, bridge=True).status == 'UNRESOLVED'
    roots[0].retire_candidate(candidates[0])
    final = validate_residency(roots[0])
    assert final.alpha_spent == F(1, 4) and len(final.alpha_allocations) == 1
    assert final.persistence_identities[0].status == 'UNRESOLVED' and final.persistence_events
    return {'fresh_start_cursor': 16, 'ordinary_events_per_root': 36, 'paired_native_root_comparisons': comparisons,
            'crossing_cursor': current.crossing_cursor, 'crossing_wealth': str(current.crossing_wealth),
            'fresh_score_events': len(final.persistence_events), 'alpha_after_retirement': str(final.alpha_spent),
            'foreign_root_refusals': 1, 'unpaired_install_status': 'UNRESOLVED',
            'scope': 'actual same-path reference evidence under an external stream-law assumption, no population or AMP/install claim'}


SECTIONS = {'small': small, 'profile': profile, 'large_closure': larger_and_closure, 'funding': funding,
            'workspace': workspace_lifetime, 'resource_continuation': resource_continuation,
            'bindings_atomic': bindings_and_atomic_failure, 'fresh': fresh_reference}


def run(section=None):
    result = {'status': 'PASS_OWNED_JOINT_REFERENCE_RUNTIME', 'complete_audit': section is None,
              'scope': 'Actual registered ReferenceCompilerRuntime construction/ingress/native phases/profile/freshness and packed ownership. No actual AMP, install or CERTIFIED_COMPLETE.'}
    for name, function in SECTIONS.items():
        if section in (None, name):
            result[name] = function()
            print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=tuple(SECTIONS))
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert args.section is None or not args.write
    result = run(args.section)
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8', newline='\n')
    print(text, end='')
