"""Exact indexed AMP schedule audit and source-bound owned CUDA workers."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference import indexed_amp as amp
from fp_reference.indexed_count import CountState
from fp_reference.indexed_execution import IndexedState, IndexedEvaluation
from fp_reference.indexed_relation import IndexedRelation
from fp_reference.cuda_prefix import IndexedCudaPrefixContract, ProjectedIndexedCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.float64_bridge import Float64Contract
from fp_reference.host_resources import HostResourceContract
from fp_reference.learner import observe_event
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.core import ContractError
from fp_reference.persistence import PersistenceContract, PersistenceRule, REFERENCE_PATH, CUDA_PATH
from fp_reference.policy import CudaCompilerPolicy
from fp_reference.profile import ProfileSpec
from audit_indexed_runtime import fixture, literal, check_state as check_native_state
from audit_reference_construction import rejects, validate_residency
from audit_cuda_runtime import no_device_handles
from ingress_audit_support import deliver_context
import indexed_phase_bridge as component
import count_learner_encoding as native_counts

CAP = 4 << 30


def binding_audit():
    """Exact adversaries against conformance and proper probability bounds."""
    def operations(arithmetic):
        return tuple(('host-RNE32-ingress' if tag == 'constant' else
            'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
            for tag, width, word in arithmetic.trace)
    endpoint_words = operation_words = gradient_words = 0
    division_errors = []
    cases = ((2, (0,), (0, 1)), (2, (0,), (0, 0)),
             (5, (0, 0, 0, 0, 1, 0, 0, 0, 0, -1), (2, 4)))
    for n, d, query in cases:
        schema = IndexedRelation(n)
        c = CountState(n, d, None, sum(map(abs, d)), sum(map(abs, d)))
        before = amp.IndexedAmpState(c)
        plan = amp.prepare_prediction(schema, before, schema.rules(),
            schema.source_row(query[0]*n+query[1]), output_cap=262144)
        arithmetic = amp._Arithmetic(32768)
        raw, _ = amp.execute_prediction(plan, before, arithmetic)
        tape = operations(arithmetic)
        amp.check_prediction_execution(plan, before, raw, tape, bit_limit=32768)
        for k in range(7):
            words = tuple(word ^ (int(j == k)) for j, word in enumerate(raw.words))
            rejects(lambda: amp.check_prediction_execution(plan, before, replace(raw, words=words), tape,
                bit_limit=32768))
            endpoint_words += 1
        for k, (tag, width, (word,)) in enumerate(tape):
            changed = tape[:k]+((tag, width, (word ^ 1,)),)+tape[k+1:]
            rejects(lambda: amp.check_prediction_execution(plan, before, raw, changed, bit_limit=32768))
            operation_words += 1
        for changed in (tape[:-1], tape+tape[-1:], (('mul', tape[0][1], tape[0][2]),)+tape[1:]):
            rejects(lambda: amp.check_prediction_execution(plan, before, raw, changed, bit_limit=32768))
        rules, graph, _, _ = literal(n)
        native = native_counts.decode(c)
        exact = evaluate(graph, rules, native.theta, schema.source_row(query[0]*n+query[1]), (), bit_limit=32768)
        ref = IndexedEvaluation(c, query, exact.excesses, exact.masses, exact.normalizer, exact.probabilities, ())
        relation = amp.check_prediction(ref, raw, Float64Contract(F(1, 100), F(1, 1000)),
            normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
        decoded = raw.decoded()
        proper = tuple(m/sum(decoded.masses) for m in decoded.masses)
        division = max(abs(p-q) for p,q in zip(proper, decoded.probabilities))
        assert relation.division_error == division
        assert relation.probability_error == max(abs(p-q) for p,row in zip(ref.probabilities,
            zip(proper, decoded.probabilities)) for q in row)
        assert relation.normalizer_error == max(abs(ref.normalizer-decoded.normalizer),
            abs(ref.normalizer-sum(decoded.masses)), abs(decoded.normalizer-sum(decoded.masses)))
        division_errors.append(str(division))
        if n == 2 and query == (0, 1):
            changed = replace(raw, words=raw.words[:2]+(raw.words[2]+1,)+raw.words[3:])
            rejects(lambda: amp.check_prediction(ref, changed, Float64Contract(F(1, 100), F(0)),
                normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768), ArithmeticUnresolved)
        for target in (0, 1):
            arithmetic = amp._Arithmetic(32768)
            observed, _ = amp.execute_observation(before, raw, target, arithmetic)
            tape = operations(arithmetic)
            amp.check_observation_execution(before, raw, target, observed, tape, bit_limit=32768)
            for k in range(3):
                words = tuple(word ^ int(j == k) for j, word in enumerate(observed.gradient_words))
                rejects(lambda: amp.check_observation_execution(before, raw, target,
                    replace(observed, gradient_words=words), tape, bit_limit=32768))
                gradient_words += 1
    assert division_errors[1] == '1/41943040'
    return {'status': 'PASS', 'prediction_word_substitutions_refused': endpoint_words,
        'operation_word_substitutions_refused': operation_words,
        'gradient_word_substitutions_refused_including_inactive_diagonal_forms': gradient_words,
        'changed_trace_length_or_operation_refused': 9, 'division_errors': division_errors,
        'proper_probability_error_with_unchanged_rounded_probability': 'REFUSED_AT_ZERO_TOLERANCE'}


def cpu_audit():
    predictions = observations = half_outputs = 0
    maximum = F(0)
    groups = []
    for n in (3, 5):
        schema = IndexedRelation(n)
        rules, graph, spec, _ = literal(n)
        rows = tuple(product((-1, 0, 1), repeat=3 if n == 3 else 2))
        queries = tuple(product(range(n), repeat=2)) if n == 3 else ((0, 1), (2, 4), (4, 4))
        for row in rows:
            d = row if n == 3 else (0, 0, 0, 0, row[0], 0, 0, 0, 0, row[1])
            clock = sum(map(abs, d))
            c = CountState(n, d, None, clock, clock)
            state = amp.IndexedAmpState(c)
            native_state = native_counts.decode(c)
            for query in queries:
                sources = schema.source_row(query[0]*n+query[1])
                plan = amp.prepare_prediction(schema, state, rules, sources, output_cap=262144)
                arithmetic = amp._Arithmetic(32768)
                raw, _ = amp.execute_prediction(plan, state, arithmetic)
                assert len(arithmetic.trace)+7 == plan.output_cells
                half_outputs += sum(width == 16 for _, width, _ in arithmetic.trace)
                expected, _, execution, _ = component.execute_predictions((component.CompactState(c),), query)
                assert raw.words == expected[0].words
                exact = evaluate(graph, rules, native_state.theta, sources, (), bit_limit=32768)
                reference = IndexedEvaluation(c, query, exact.excesses, exact.masses, exact.normalizer, exact.probabilities, ())
                tolerance = Float64Contract(F(1, 100), F(1, 1000))
                relation = amp.check_prediction(reference, raw, tolerance, normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
                physical = raw.decoded().materialize(scalar_cap=10000)
                actual_error = max(abs(a-b) for a, b in zip(exact.values+exact.masses, physical.values+physical.masses))
                assert actual_error == relation.native_error
                for target in (0, 1):
                    arithmetic = amp._Arithmetic(32768)
                    observed, _ = amp.execute_observation(state, raw, target, arithmetic)
                    assert len(arithmetic.trace)+3 == 13
                    old = component.execute_observations((component.CompactState(c),), expected, (target,), execution)[0]
                    assert observed.encoded == old.encoded and observed.gradient_words == old.gradient_words
                    full = observe_event(graph, native_state, spec, exact, target, bit_limit=32768)
                    mass = exact.masses[target]
                    ref = IndexedState(observed.encoded, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
                    relation = amp.check_state(ref, observed, tolerance, bit_limit=32768)
                    decoded = old.materialize(scalar_cap=10000)
                    error = max(abs(a-b) for a, b in zip(full.gradient_sum, decoded.gradient_sum))
                    assert error == relation.state_error and full.theta == decoded.theta
                    maximum = max(maximum, error)
                    observations += 1
                predictions += 1
        groups.append({'n': n, 'profiles': len(rows), 'ordered_queries': len(queries)})
    assert half_outputs > 0
    c = CountState(2, (0,), None, 0, 0)
    schema = IndexedRelation(2)
    raw, _ = amp.execute_prediction(amp.prepare_prediction(schema, amp.IndexedAmpState(c), schema.rules(),
        schema.source_row(1), output_cap=1000), amp.IndexedAmpState(c), amp._Arithmetic(32768))
    observed, _ = amp.execute_observation(amp.IndexedAmpState(c), raw, 0, amp._Arithmetic(32768))
    ref = IndexedState(observed.encoded, (F(0), F(-4, 5), F(4, 5)))
    forged = replace(observed, encoded=replace(observed.encoded, pending=(0, 1, 1)))
    rejects(lambda: amp.check_state(ref, forged, Float64Contract(F(1, 100), F(1, 1000)), bit_limit=32768))
    rejects(lambda: amp.range_bound(schema, schema.rules(), amp.IndexedAmpState(c), amp.CategoricalPairDomain(2),
        normalizer_cap=F(10), activation_cap=F(8)), ArithmeticUnresolved)
    return {'status': 'PASS', 'scope': 'exact RNE schedule and complete native coordinates; no actual GPU or owned provenance claim',
        'groups': groups, 'predictions': predictions, 'observations': observations,
        'half_precision_scalar_outputs': half_outputs, 'maximum_gradient_error': str(maximum),
        'independently_bound_target_forgery': 'REFUSED', 'insufficient_whole_domain_range_cap': 'UNRESOLVED',
        'independent_endpoint_and_normalization_checks': binding_audit()}


def configuration(n, length, *, profiles=(), persistence=None, law=False, install=False, policy=False, projected=False, **cuda_changes):
    cfg, schema, online = fixture(n, length, profiles=profiles, persistence=persistence, law=law,
                                  byte_cap=1 << 30, work_cap=10**14)
    cfg = replace(cfg, normalizer_cap=F(18))
    arena = 32 << 20
    contract = ProjectedIndexedCudaPrefixContract if projected else IndexedCudaPrefixContract
    cuda = contract(CudaStorageContract(arena, 2*arena,
        {role: (arena, 2*arena) for role in ('deployment', 'compiler')}), F(1, 100), F(1, 1000),
        n=n, phase_output_cells=65536, phase_evidence_bytes=(4 << 20) if n > 32 else 262144,
        install=CudaInstallContract() if install else None)
    cuda = replace(cuda, **cuda_changes)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online,
        host=HostResourceContract(CAP, {role: CAP for role in ('deployment', 'compiler')}),
        cuda=cuda, policy=CudaCompilerPolicy(()) if policy else None)
    return rt, schema


def step(rt, schema, event):
    i, j, target = event
    cursor = rt.snapshot().cursor
    key = rt.snapshot().online.data.active.observation_ids[cursor]
    result = deliver_context(rt, key, tuple(schema.source_row(i*schema.n+j).values()))
    assert result.status == 'PREDICTED_REFERENCE', result
    result = rt.observe(target)
    assert result.status == 'OBSERVED_REFERENCE', result


def check_phases(rt, *, projected=False):
    snapshot = validate_residency(rt)
    no_device_handles(snapshot)
    words = half = phases = 0
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record
        kind = record.phase.split(':')[-1]
        assert type(record.raw_state) is amp.IndexedAmpState
        if kind == 'predict':
            raw = record.raw_prediction
            state = amp.IndexedAmpState(raw.before)
            if projected:
                from fp_reference import projected_amp
                schema = IndexedRelation(raw.before.n)
                plan = projected_amp.prepare_prediction(schema,state,schema.rules(),
                    schema.source_row(raw.query[0]*schema.n+raw.query[1]),output_cap=65536)
                expected,_ = amp._prediction_schedule(plan,state,amp._Arithmetic(32768))
                assert raw.words == expected.words
            else:
                expected, _, execution, _ = component.execute_predictions((component.CompactState(raw.before),), raw.query)
                assert raw.words == expected[0].words
            assert record.forward_operations > 0
            assert record.output_cells == record.execution_plan.output_cells
        elif kind == 'observe':
            actual = record.raw_state
            old = component.CompactState(actual.encoded, actual.gradient_words)
            if actual.encoded.n <= 5:
                native = native_counts.decode(actual.encoded)
                materialized = old.materialize(scalar_cap=10000)
                assert native.theta == materialized.theta
                assert max(abs(a-b) for a,b in zip(native.gradient_sum, materialized.gradient_sum)) == record.relation.state_error
        else:
            assert record.raw_state.encoded == record.reference.encoded and not record.raw_state.gradient_words
        for _, width, values in record.raw_operations:
            words += len(values)
            half += len(values) if width == 16 else 0
        phases += 1
    return {'checked_phases': phases, 'actual_floating_words': words, 'actual_half_words': half,
        'cursor': snapshot.cursor, 'packed_current_bytes': snapshot.resources['current']['reference_payload_bytes'],
        'consumed_arena_bytes': snapshot.cuda.storage['consumed_arena_extent']}


def worker(case):
    if case.startswith('projected-'):
        from audit_projected_amp import worker as projected_worker
        return projected_worker(case[len('projected-'):])
    if case in ('plan-binding','executor-plan-binding'):
        from audit_indexed_amp_plan_binding import evaluate_plan
        rt,schema = configuration(3,2)
        step(rt,schema,(1,2,0))
        before = rt.snapshot()
        candidate = before.deployed_id
        prior = rt._cuda.phases[dict(before.cuda.current)[candidate]].raw_state
        assert prior.encoded.counts == (0,0,1) and prior.encoded.cursor == 1
        original = amp.prepare_prediction
        honest_plan = original(schema,prior,schema.rules(),schema.source_row(1),output_cap=65536)
        honest,expected_operations = evaluate_plan(honest_plan,prior)
        physical = amp.execute_prediction
        def substituted(*args,**kwargs):
            plan = original(*args,**kwargs)
            assert plan.support == ((1,2),) and plan.positions == (2,)
            return replace(plan,positions=(0,))
        def changed_after_execution(plan,*args,**kwargs):
            result = physical(plan,*args,**kwargs)
            object.__setattr__(plan,'output_cells',plan.output_cells-1)
            return result
        def forbidden(*args,**kwargs):
            raise AssertionError('a plan with the wrong factor address executed')
        key = before.online.data.active.observation_ids[before.cursor]
        if case == 'plan-binding':
            with patch.object(amp,'prepare_prediction',substituted),patch.object(amp,'execute_prediction',forbidden):
                rejects(lambda: deliver_context(rt,key,tuple(schema.source_row(1).values())),RuntimeError)
        else:
            with patch.object(amp,'execute_prediction',changed_after_execution):
                rejects(lambda: deliver_context(rt,key,tuple(schema.source_row(1).values())),RuntimeError)
        after = validate_residency(rt)
        no_device_handles(after)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED' and 'plan differs' in phase.reason
        if case == 'plan-binding':
            assert phase.execution_plan.positions == (0,) and phase.execution_plan.support == ((1,2),)
            assert not phase.raw_operations and phase.output_cells == 0 and phase.raw_prediction is None
        else:
            assert phase.raw_prediction.words == honest.words and phase.raw_operations == expected_operations
            assert phase.execution_plan.output_cells == honest_plan.output_cells-1
            assert phase.output_cells == honest_plan.output_cells
        assert after.cursor == 1 and after.candidates == before.candidates and after.pending.record.target is None
        assert not after.pending.predictions and after.cuda.current == before.cuda.current
        return {'certificate_claim':'REFUSED','scope':'complete registered plan binding before execution and after helper return',
            'attack':case,'runtime_status':'REFUSED_BEFORE_TARGET','phase_status':phase.status,
            'actual_prefix':[[1,2,0]],'current_query':[0,1],
            'actual_output_cells':phase.output_cells,'retained_plan_output_cells':phase.execution_plan.output_cells,
            'target_revealed':False,'published_predictions':0,'learner_advances':0}
    if case == 'projection-boundary':
        rt,schema = configuration(15,14)
        for leaf in range(2,15):
            step(rt,schema,(1,leaf,0))
        checked = check_phases(rt)
        before = rt.snapshot()
        key = before.online.data.active.observation_ids[before.cursor]
        def forbidden(*args,**kwargs):
            raise AssertionError('unfunded global AMP table execution began')
        with patch.object(amp,'execute_prediction',forbidden):
            result = deliver_context(rt,key,tuple(schema.source_row(2*15+3).values()))
        assert result.status == 'UNRESOLVED' and 'join-cell allowance' in result.reason,result
        after = validate_residency(rt)
        no_device_handles(after)
        phase = after.cuda.phases[-1]
        assert phase.status == 'UNRESOLVED' and phase.reference_prediction.probabilities[0] == F(189,250)
        assert dict(phase.reference_prediction.table_work)['projected_active_edges'] == 2
        assert phase.output_cells == 0 and not phase.raw_operations and phase.raw_prediction is None
        assert after.cursor == 13 and after.candidates == before.candidates and after.cuda.current == before.cuda.current
        assert after.pending.record.target is None and not after.pending.predictions
        assert phase.reference_prediction.before == before.candidates[0].learner.encoded
        return {**checked,'actual_star_observations':13,'reference_forecast':'189/250',
            'reference_projected_active_edges':2,'retained_nonzero_counts':13,
            'unchanged_global_AMP_status':result.status,'unfunded_AMP_output_cells':0,
            'target_revealed':False,'published_predictions_or_learner_advances':0}
    if case == 'endpoint-binding':
        rt, schema = configuration(2, 1)
        before = rt.snapshot()
        original = amp.execute_prediction
        executed = {}
        def substituted(plan, state, arithmetic):
            raw, resident = original(plan, state, arithmetic)
            assert raw.words[5] == 1056964608  # exact single 1/2
            executed['words'] = raw.words
            # Same owned extent and all original arithmetic; only its final
            # copied probability changes after the helper's local copy check.
            resident.readout[5].fill_(float(amp.single(raw.words[5]+1)))
            return resident.raw(), resident
        with patch.object(amp, 'execute_prediction', substituted):
            rejects(lambda: deliver_context(rt, before.online.data.active.observation_ids[0],
                                            tuple(schema.source_row(1).values())), RuntimeError)
        after = validate_residency(rt)
        no_device_handles(after)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED' and 'final endpoint' in phase.reason, phase
        assert phase.raw_prediction.words[5] == executed['words'][5]+1
        assert phase.raw_operations[-2] == ('div', 32, (executed['words'][5],))
        relation = amp.check_prediction(phase.reference_prediction, phase.raw_prediction,
            Float64Contract(F(1, 100), F(1, 1000)), normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
        assert relation.probability_error == relation.division_error == F(1, 16777216)
        assert after.cursor == 0 and after.candidates == before.candidates and after.cuda.current == before.cuda.current
        return {'certificate_claim': 'REFUSED', 'scope': 'fixed AMP transition conformance; passive numerical tolerance still passes',
                'runtime_status': 'REFUSED_BEFORE_TARGET', 'phase_status': phase.status,
                'arithmetic_probability_word': executed['words'][5],
                'accepted_final_probability_word': phase.raw_prediction.words[5],
                'probability_error': str(relation.probability_error),
                'reported_division_error': str(relation.division_error),
                'actual_stored_mass_division_error': '1/16777216',
                'output_cells': phase.output_cells, 'target_revealed': False}
    if case in ('gradient-binding', 'predecessor-binding'):
        rt, schema = configuration(2, 1)
        before = rt.snapshot()
        assert deliver_context(rt, before.online.data.active.observation_ids[0],
                               tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
        original = amp.execute_observation
        executed = {}
        def substituted(state, prediction, target, arithmetic, **kwargs):
            raw, resident = original(state, prediction, target, arithmetic, **kwargs)
            executed['gradient_words'] = raw.gradient_words
            if case == 'gradient-binding':
                resident.gradient[1].fill_(float(amp.single(raw.gradient_words[1] ^ 1)))
            else:
                kwargs['resident_prediction'].readout[5].fill_(float(amp.single(prediction.words[5]+1)))
            return resident.raw(), resident
        with patch.object(amp, 'execute_observation', substituted):
            rejects(lambda: rt.observe(0), RuntimeError)
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED', phase
        reason = 'final endpoint' if case == 'gradient-binding' else 'pre-target prediction'
        assert reason in phase.reason, phase
        assert after.pending.record.target == after.observations[-1].target == 0
        assert after.cursor == 0 and after.candidates == before.candidates and after.cuda.current == before.cuda.current
        assert phase.raw_state.encoded.pending == (0, 1, 0)
        return {'certificate_claim': 'REFUSED', 'case': case, 'phase_status': phase.status,
                'reason': phase.reason, 'retained_actual_target': 0, 'published_advances': 0,
                'arithmetic_gradient_words': list(executed['gradient_words']),
                'retained_gradient_words': list(phase.raw_state.gradient_words)}
    if case == 'trace-binding':
        rt, schema = configuration(2, 1)
        before = rt.snapshot()
        original = amp.execute_prediction
        def substituted(plan, state, arithmetic):
            raw, resident = original(plan, state, arithmetic)
            arithmetic.device._records[2][1].fill_(8)  # nine's extent, after its uses
            return raw, resident
        with patch.object(amp, 'execute_prediction', substituted):
            rejects(lambda: deliver_context(rt, before.online.data.active.observation_ids[0],
                                            tuple(schema.source_row(1).values())), RuntimeError)
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED' and 'retained operations' in phase.reason, phase
        assert phase.raw_prediction.words[5] == 1056964608
        assert amp.single(phase.raw_operations[2][2][0]) == 8
        assert after.candidates == before.candidates and after.cuda.current == before.cuda.current
        return {'certificate_claim': 'REFUSED', 'phase_status': phase.status, 'endpoint_unchanged': True,
                'expected_constant': 9, 'retained_changed_constant': 8, 'target_revealed': False}
    if case == 'old-output':
        rt, schema = configuration(2, 2)
        original = amp.execute_prediction
        captured = {}
        def substituted(plan, state, arithmetic):
            raw, resident = original(plan, state, arithmetic)
            if not captured:
                captured['old'] = resident
                return raw, resident
            stale = amp.ResidentPrediction(raw.before, raw.query, captured['old'].readout)
            assert stale.raw() == raw  # equal words do not prove fresh extent ownership
            return raw, stale
        with patch.object(amp, 'execute_prediction', substituted):
            step(rt, schema, (0, 0, 0))
            before = rt.snapshot()
            rejects(lambda: deliver_context(rt, before.online.data.active.observation_ids[1],
                                            tuple(schema.source_row(0).values())), RuntimeError)
        after = validate_residency(rt)
        phase = after.cuda.phases[-1]
        assert phase.status == 'EXECUTION_FAILED' and 'raw phase readout' in phase.reason, phase
        assert after.cursor == 1 and after.candidates == before.candidates and after.cuda.current == before.cuda.current
        return {'certificate_claim': 'REFUSED', 'phase_status': phase.status, 'equal_final_words': True,
                'older_owned_extent_not_a_current_phase_output': True, 'second_target_revealed': False}
    if case == 'profiles':
        rt, schema = configuration(5, 8, profiles=(ProfileSpec('twice', ('indexed-event:0', 'indexed-event:1'), 2),))
        for k, event in enumerate(((1, 2, 0), (3, 4, 0), (2, 4, 0), (0, 0, 0),
                                   (1, 3, 1), (2, 4, 1), (0, 1, 0), (4, 4, 1))):
            step(rt, schema, event)
            if k == 1:
                assert rt.construct_candidate(schema, profile_id='twice').status == 'BUILT_REFERENCE'
        result = check_phases(rt)
        assert result['actual_half_words'] > 0
        assert sorted(c.learner.optimizer_steps for c in rt.snapshot().candidates) == [8, 10]
        return {**result, 'profile_events': len(rt.snapshot().profile_events), 'optimizer_steps': [8, 10]}
    if case == 'large':
        def forbidden(*a, **kw):
            raise AssertionError('owned indexed AMP tried to build a world table')
        with patch.object(component.native, 'relation_graph', forbidden), \
                patch.object(IndexedRelation, 'materialize_program', forbidden), \
                patch.object(IndexedRelation, 'materialize_learner', forbidden):
            rt, schema = configuration(256, 4, profiles=(ProfileSpec('twice', ('indexed-event:0', 'indexed-event:1'), 2),))
            for k, event in enumerate(((0, 1, 0), (0, 0, 0), (1, 2, 0), (0, 2, 1))):
                step(rt, schema, event)
                if k == 1:
                    assert rt.construct_candidate(schema, profile_id='twice').status == 'BUILT_REFERENCE'
        return {**check_phases(rt), 'n': 256, 'world_builders': 'DISABLED', 'profile_events': 4}
    if case == 'install':
        persistence = PersistenceContract(F(1, 2), tuple(PersistenceRule(name, 1, 20, F(1, 4), F(3, 4), F(3), 12, 16,
            score_path=path) for name,path in (('ref',REFERENCE_PATH),('cuda',CUDA_PATH))))
        rt, schema = configuration(2, 36, persistence=persistence, law=True, install=True)
        for _ in range(16):
            step(rt, schema, (0, 1, 1))
        candidate = rt.construct_candidate(schema)
        assert candidate.status == 'BUILT_REFERENCE'
        r = rt.admit_reference_persistence(candidate.candidate_id, 'ref')
        c = rt.admit_cuda_persistence(candidate.candidate_id, 'cuda')
        assert r.identity_id and c.identity_id, (r, c)
        assert all(i.status == 'ACTIVE' for i in rt.snapshot().persistence_identities), rt.snapshot().persistence_identities
        for _ in range(8):
            step(rt, schema, (0, 1, 0))
            if rt.paired_cuda_persistence_result(r.identity_id, c.identity_id).status == 'PAIRED_CUDA_CROSSED':
                break
        paired = rt.paired_cuda_persistence_result(r.identity_id, c.identity_id)
        assert paired.status == 'PAIRED_CUDA_CROSSED', paired
        before = rt.snapshot()
        installed = rt.install_cuda(candidate.candidate_id, reference_identity=r.identity_id, cuda_identity=c.identity_id)
        assert installed.status == 'INSTALLED_CUDA', installed
        after = rt.snapshot()
        assert after.deployed_id == candidate.candidate_id
        assert tuple(c.learner for c in before.candidates) == tuple(c.learner for c in after.candidates)
        assert before.cuda.current == after.cuda.current and before.cuda.phases == after.cuda.phases
        assert after.alpha_spent == F(1, 2) and all(i.status == 'UNRESOLVED' for i in after.persistence_identities)
        step(rt, schema, (0, 1, 0))
        return {**check_phases(rt), 'paired_crossing_cursor': before.cursor, 'installation': installed.status,
                'alpha_after_installation': str(after.alpha_spent), 'historical_selection_proof': None,
                'post_install_continuation': True}
    if case == 'closure':
        rt, schema = configuration(3, 3, policy=True)
        for event in ((0, 1, 0), (1, 2, 0), (0, 2, 1)):
            step(rt, schema, event)
        assert rt.snapshot().run.status == 'SEALED_CUDA_STREAM'
        assert not rt.snapshot().run.closure.decisions
        return {**check_phases(rt), 'closure': rt.snapshot().run.status, 'class_decisions': 0}
    if case == 'unfunded':
        rt, schema = configuration(3, 1, phase_output_cells=2)
        before = rt.snapshot()
        def forbidden(*args, **kwargs):
            raise AssertionError('unfunded indexed GPU executor entered')
        with patch.object(amp._Arithmetic, '__init__', forbidden):
            result = deliver_context(rt, before.online.data.active.observation_ids[0], tuple(schema.source_row(1).values()))
        assert result.status == 'UNRESOLVED', result
        after = validate_residency(rt)
        failed = after.cuda.phases[-1]
        assert failed.status == 'UNRESOLVED' and failed.arena_phase is None and failed.output_cells == 0
        assert after.cursor == 0 and after.candidates == before.candidates
        assert after.pending.record.sources and after.pending.record.target is None
        assert len(after.buffers) > len(before.buffers)
        return {'status': result.status, 'retained_received_context': True, 'executor_entries': 0,
                'failed_phase_retained': True, 'published_advances': 0}
    if case == 'target-swap':
        rt, schema = configuration(2, 1)
        before = rt.snapshot()
        assert deliver_context(rt, before.online.data.active.observation_ids[0], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
        original = amp.execute_observation
        def swapped(state, prediction, target, arithmetic, **kwargs):
            return original(state, prediction, 1-target, arithmetic, **kwargs)
        with patch.object(amp, 'execute_observation', swapped):
            rejects(lambda: rt.observe(0), RuntimeError)
        after = validate_residency(rt)
        failed = after.cuda.phases[-1]
        assert failed.status == 'EXECUTION_FAILED' and failed.raw_state.encoded.pending == (0, 1, 1)
        assert after.pending.record.target == after.observations[-1].target == 0
        assert after.cursor == 0 and after.candidates == before.candidates and after.cuda.current == before.cuda.current
        return {'false_pending_target': 1, 'retained_actual_target': 0, 'failed_phase': failed.status,
                'published_advances': 0, 'owned_target_binding': 'REFUSED'}
    if case == 'second-commit':
        from fp_reference import indexed_cuda_prefix
        rt, schema = configuration(3, 1)
        assert rt.construct_candidate(schema).status == 'BUILT_REFERENCE'
        before = rt.snapshot()
        assert deliver_context(rt, before.online.data.active.observation_ids[0], tuple(schema.source_row(1).values())).status == 'PREDICTED_REFERENCE'
        calls = 0
        original = indexed_cuda_prefix.commit
        def failed_second(state):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise ArithmeticUnresolved('injected second indexed CUDA commit refusal')
            return original(state)
        with patch.object(indexed_cuda_prefix, 'commit', failed_second):
            result = rt.observe(0)
        assert result.status == 'UNRESOLVED' and calls == 2
        after = validate_residency(rt)
        assert after.candidates == before.candidates and after.cuda.current == before.cuda.current and after.cursor == 0
        assert after.pending.record.target == after.observations[-1].target == 0
        assert all(t.after_observe.encoded.pending == (0, 1, 0) for t in after.event_traces)
        assert after.cuda.phases[-1].status == 'UNRESOLVED' and after.cuda.phases[-1].raw_state.encoded.pending == (0, 1, 0)
        return {'commit_calls': calls, 'status': result.status, 'retained_actual_target': 0,
                'observed_lineages_retained': len(after.event_traces), 'published_advances': 0}
    raise ValueError(case)


def main():
    from audit_projected_amp import PROJECTED_CASES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', choices=('profiles', 'large', 'install', 'closure', 'unfunded', 'target-swap',
        'second-commit', 'endpoint-binding', 'gradient-binding', 'trace-binding', 'predecessor-binding', 'old-output', 'projection-boundary', 'plan-binding', 'executor-plan-binding')
        +tuple('projected-'+case for case in PROJECTED_CASES))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        report = {'status': 'FAILED', 'process_id': os.getpid(), 'case': args.worker}
        try:
            report['result'] = worker(args.worker)
            report['status'] = ('COUNTEREXAMPLE_REPRODUCED' if report['result'].get('certificate_claim') == 'FALSIFIED'
                                else 'PASS_OWNED_INDEXED_CUDA')
        except Exception:
            report['traceback'] = traceback.format_exc()
        if args.output is None:
            parser.error('--worker requires a bounded result --output')
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'status': report['status'], 'case': args.worker}))
        if report['status'] not in ('PASS_OWNED_INDEXED_CUDA', 'COUNTEREXAMPLE_REPRODUCED'):
            raise SystemExit(1)
    else:
        report = cpu_audit()
        if args.write:
            (ROOT/'evidence/minimal/FP_INDEXED_AMP_SCHEDULE.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
