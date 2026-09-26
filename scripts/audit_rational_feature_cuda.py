"""Preregistered fresh-job gate for the complete rational-feature AMP path."""
from copy import deepcopy
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, HostResourceContract, CudaCompilerPolicy
from fp_reference import rational_feature_amp as amp, joint_partition_decoder as decoder, joint_cuda_prefix as executor
from fp_reference import cuda_learner as gpu, phase_deflate
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.joint_relation import JointRelation
from fp_reference.joint_execution import JointState
from fp_reference.learner import observe_event, commit_event
from fp_reference.profile import ProfileSpec, attach_boundary
from fp_reference.persistence import PersistenceContract, PersistenceRule, REFERENCE_PATH, CUDA_PATH
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_joint_runtime import fixture, literal, predict
from audit_joint_amp import BUDGET, configuration as cuda_contract, operations, TOLERANCE
from audit_joint_cuda import frames, preserved, step
from audit_reference_construction import rejects
from unknown_noise_decoding import DEFAULT, OTHER
from unknown_noise_model import JointControl
from rational_feature_scale import Bank, reference as exact_readout, rounded, gradient_basis
from audit_rational_feature_amp import WIDE, Q
import audit_phase_writer_binding as runner

ANCHOR = '95ba561'
CAP, DEADLINE = 4 << 30, 900000
STATUS = 'PASS_ACTUAL_OWNED_RATIONAL_FEATURE_AMP'
ORIGINAL_CASES = ('profiles', 'fresh-install', 'large-closure', 'range-scale', 'wide-denominator',
    'precision-refusal', 'reversal', 'unfunded', 'second-commit', 'prediction-word',
    'coefficient-word', 'gradient-word', 'operation-word', 'old-output', 'target-swap',
    'plan-roots', 'rate-parts', 'stored-parts', 'workspace', 'profile-refusal', 'legacy-unit')
CASES = ORIGINAL_CASES[19:]
WORD = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 1), (2, 2, 0), (1, 0, 1), (0, 1, 0))


def configuration(n, length, *, family=DEFAULT, C=10, profiles=(), persistence=None,
                  law=False, install=False, policy=False, budget=BUDGET, output_cap=128):
    cfg, model, online = fixture(n, length, family=family, feature_scale=F(C), profiles=profiles,
        persistence=persistence, law=law, budget=budget, byte_cap=1 << 30, work_cap=10**15)
    cfg = replace(cfg, normalizer_cap=F(2*(C-1)))
    cuda = cuda_contract(model, budget, phase_output_cells=output_cap,
        phase_evidence_bytes=65536 if n <= 3 else 524288,
        evidence_encoding=phase_deflate.ENCODING_ID, install=CudaInstallContract() if install else None)
    return ReferenceCompilerRuntime(cfg, model, online=online, cuda=cuda,
        host=HostResourceContract(CAP, {r: CAP for r in ('deployment', 'compiler')}),
        policy=CudaCompilerPolicy(()) if policy else None), model


def upper(value):
    """Small exact dyadic upper enclosure, not a dump of wide error fractions."""
    grid = 1 << 48
    numerator = (value.numerator*grid+value.denominator-1)//value.denominator
    return str(F(numerator, grid))


def coefficient_trace(model):
    arithmetic = amp._Arithmetic(32768)
    columns = tuple(arithmetic.op('constant', constant=c)
                    for j in range(len(model.rates)) for c in model.coefficients(j))
    return tuple(v.word for v in columns), tuple(arithmetic.trace)


def check_phases(runtime, *, literal_bits=131072):
    """Reconstruct every lineage from unsigned actual events, never endpoints."""
    snapshot = frames(runtime)
    model, budget = snapshot.cuda.contract.schema, snapshot.cuda.contract.partitions
    assert snapshot.cuda.contract.forward_id == amp.FORWARD_ID
    records = {p.object_id: p for p in snapshot.cuda.phases}
    observations = {r.observation_id: r for r in snapshot.observations}
    if snapshot.pending is not None:
        observations[snapshot.pending.record.observation_id] = snapshot.pending.record
    controls, native_states, native_predictions, parts_by_prediction = {}, {}, {}, {}
    bundle = literal(model) if model.n <= 3 else None
    bank = Bank(model.n, model.rates, model.prior, model.native_scale)
    coefficient_words, coefficients = coefficient_trace(model)
    words = halves = outputs = predictions = native_phases = maximum_frame = 0
    materialization_step_cap = budget.step_cap
    maxima = {}
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record.status
        kind = record.phase.split(':')[-1]
        previous = records.get(record.input_phase)
        expected_native = None
        if kind == 'initialize':
            control, cursor, pending = JointControl(model.n, model.rates, model.prior), record.ordinary_cursor, None
            if bundle:
                expected_native = literal(model, cursor)[3]
        else:
            old_control, cursor, pending = controls[record.input_phase]
            control = deepcopy(old_control)
            if kind == 'predict':
                assert pending is None
                query, _ = model.source_query(model.rules(), dict(observations[record.observation_id].sources))
                answer = control.forecast(query)
                parts, Z = answer.rate_parts, sum(map(sum, answer.rate_parts))
                parts_by_prediction[record.object_id] = parts
                N = tuple(sum(model.coefficient_integers(j)[0]*row[y]+model.coefficient_integers(j)[1]*row[1-y]
                              for j, row in enumerate(parts)) for y in (0, 1))
                plan, actual = record.execution_plan, record.raw_prediction
                assert actual.before == previous.raw_state.encoded and actual.query == query
                assert actual.rate_parts == plan.rate_parts == parts and actual.normalization == plan.normalization == Z
                assert plan.excesses == N and plan.before == actual.before and plan.query == query
                assert plan.bit_limit == min(32768, budget.integer_bits)
                columns, _, trace = rounded(bank, parts, 0)
                assert actual.words == tuple(v.word for v in columns)+coefficient_words
                expected_ops = tuple(('host-RNE32-ingress' if tag == 'constant' else
                    'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
                    for tag, width, word in trace[0]+coefficients)
                assert record.raw_operations == expected_ops
                assert record.output_cells == 21+4*sum(bool(v) for v in N)+4*len(model.rates)
                assert record.forward_operations == len(expected_ops)
                ref = record.reference_prediction
                assert exact_readout(bank, parts) == ref.excesses+ref.masses+(ref.normalizer,)+ref.probabilities
                assert ref.probabilities == answer.joint and ref.rate_parts == parts and ref.normalization == Z
                predictions += 1
                if bundle:
                    expected_native = native_states[record.input_phase]
                    cache = evaluate(bundle[1], bundle[0], expected_native.theta,
                        dict(observations[record.observation_id].sources), (), bit_limit=literal_bits)
                    native_predictions[record.object_id] = cache
                    assert ref.materialize(scalar_cap=10000) == cache
                    physical = actual.decoded().materialize(scalar_cap=10000)
                    assert max(abs(a-b) for a, b in zip(cache.values, physical.values)) <= TOLERANCE.state_atol
            elif kind == 'observe':
                prediction = records[record.prediction_phase]
                assert prediction.input_phase == record.input_phase and prediction.observation_id == record.observation_id
                actual_target = observations[record.observation_id].target
                assert pending is None and type(actual_target) is int and actual_target in (0, 1)
                pending = prediction.raw_prediction.query+(actual_target,)
                cursor += 1
                parts = parts_by_prediction[prediction.object_id]
                _, gradient, traces = rounded(bank, parts, actual_target)
                assert record.raw_state.gradient_words == tuple(v.word for v in gradient)
                expected_ops = tuple(('host-RNE32-ingress' if tag == 'constant' else
                    'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
                    for tag, width, word in traces[1])
                assert record.raw_operations == expected_ops
                zeros = sum(not sum(row) for row in parts)+sum(not v for row in parts for v in row)
                assert record.output_cells == 6+29*len(parts)-3*zeros
                assert record.reference.gradient_forms == gradient_basis(bank, parts, actual_target)
                if bundle:
                    expected_native = observe_event(bundle[1], native_states[record.input_phase], bundle[2],
                        native_predictions[prediction.object_id], actual_target, bit_limit=literal_bits)
            elif kind == 'commit':
                assert pending is not None
                control.pending = pending[:2]
                control.observe(pending[2])
                pending = None
                if bundle:
                    expected_native = commit_event(native_states[record.input_phase], bundle[2], bit_limit=literal_bits)
            elif kind == 'attach':
                assert pending is None
                cursor = 0 if previous.phase.endswith(':initialize') and record.phase.startswith('profile:') else record.ordinary_cursor
                if bundle:
                    expected_native = attach_boundary(native_states[record.input_phase], cursor, bundle[2])
            else:
                raise AssertionError(kind)
        d, s, T = control.coordinates()
        encoded = record.raw_state.encoded
        assert encoded == record.reference.encoded and encoded.model == model
        assert (encoded.counts, encoded.diagonal, encoded.steps, encoded.cursor, encoded.pending) == (d, s, T, cursor, pending)
        controls[record.object_id] = control, cursor, pending
        if kind in ('initialize', 'commit', 'attach'):
            assert not record.raw_operations and not record.raw_state.gradient_words and record.output_cells == 0
        if expected_native is not None:
            # A legal final commit can produce T=step_cap+1. The independent
            # literal reader needs its own declared allowance for that state;
            # this cannot authorize another live Runtime prediction.
            materialization_step_cap = max(materialization_step_cap, encoded.steps)
            literal_budget = replace(budget, step_cap=max(budget.step_cap, encoded.steps))
            assert record.reference.materialize(scalar_cap=10000, budget=literal_budget, bit_limit=literal_bits) == expected_native
            physical = JointState(encoded, tuple(amp.single(v) for v in record.raw_state.gradient_words)).materialize(
                scalar_cap=10000, budget=literal_budget, bit_limit=literal_bits)
            assert physical.theta == expected_native.theta
            assert max(abs(a-b) for a, b in zip(physical.gradient_sum, expected_native.gradient_sum)) <= TOLERANCE.state_atol
            native_states[record.object_id] = expected_native
            native_phases += 1
        for key, value in vars(record.relation).items():
            maxima[key] = max(maxima.get(key, F(0)), value)
        outputs += record.output_cells
        for _, width, values in record.raw_operations:
            words += len(values)
            halves += len(values) if width == 16 else 0
        maximum_frame = max(maximum_frame, int.from_bytes(dict(snapshot.buffers)[record.object_id][:8], 'big'))
    key = next(k for k in runtime._buffers if k.endswith(':joint-partition-storage'))
    assert len(runtime._buffers[key]) == decoder.workspace_bytes(model, budget)
    return dict(checked_phases=len(snapshot.cuda.phases), independent_unsigned_RNE_predictions=predictions,
        full_literal_native_phases=native_phases, actual_operation_words=words, actual_half_words=halves,
        output_words_including_copies=outputs, cursor=snapshot.cursor, table_bytes=len(runtime._buffers[key]),
        packed_peak_bytes=snapshot.resources['peak']['reference_payload_bytes'],
        consumed_arena_bytes=snapshot.cuda.storage['consumed_arena_extent'], largest_encoded_frame_bytes=maximum_frame,
        maximum_relation_error_upper_bounds={k: upper(v) for k, v in maxima.items()}, error_upper_grid_bits=48,
        runtime_prediction_step_cap=budget.step_cap, literal_materialization_step_cap=materialization_step_cap)


def integration(case):
    if case == 'profiles':
        spec = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
        runtime, model = configuration(3, 8, profiles=(spec,), budget=replace(BUDGET, integer_bits=4096))
        for k, event in enumerate(WORD):
            step(runtime, model, event)
            if k == 1:
                assert runtime.construct_candidate(model, profile_id='twice').status == 'BUILT_REFERENCE'
        assert sorted(c.learner.optimizer_steps for c in runtime.snapshot().candidates) == [8, 10]
        return {**check_phases(runtime), 'profile_events': 4, 'optimizer_steps': [8, 10]}
    if case == 'large-closure':
        with patch.object(JointRelation, 'materialize_program', side_effect=AssertionError('world expansion')), \
                patch.object(JointRelation, 'materialize_learner', side_effect=AssertionError('slot expansion')):
            runtime, model = configuration(64, 8, family=OTHER, C=8, policy=True)
            for event in WORD[:5]+((3, 4, 1), (2, 4, 0), (4, 2, 1)):
                step(runtime, model, event)
        final = runtime.snapshot()
        assert final.run.status == 'SEALED_CUDA_STREAM' and not final.run.closure.decisions
        return {**check_phases(runtime), 'native_hypotheses': str(model.K), 'closure': final.run.status, 'constructor_decisions': 0}
    if case == 'range-scale':
        runtime, model = configuration(2, 3, family=OTHER, C=8)
        for _ in range(2):
            step(runtime, model, (0, 1, 1))
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        phase = runtime.snapshot().cuda.phases[-1]
        error = max(abs(a-b) for a, b in zip(phase.reference_prediction.masses, phase.raw_prediction.decoded().masses))
        assert error == F(8950209, 16471556096)
        assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
        return {**check_phases(runtime), 'native_scale': 8, 'likelihood_scale': 120,
                'native_error_at_two_event_cut': str(error), 'original_tolerances_pass': True}
    if case == 'wide-denominator':
        runtime, model = configuration(2, 8, family=WIDE, C=4, budget=replace(BUDGET, step_cap=8))
        for event in ((0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1))*2:
            step(runtime, model, event)
        return {**check_phases(runtime), 'likelihood_scale_bits': model.scale.bit_length(),
                'native_scale': 4, 'exact_nonzero_coefficient_rounds_to_zero': amp.single(coefficient_trace(model)[0][-1]) == 0}
    if case == 'precision-refusal':
        runtime, model = configuration(2, 82, family=WIDE, C=4, budget=replace(BUDGET, step_cap=100))
        for _ in range(81):
            step(runtime, model, (0, 0, 0))
        before = frames(runtime)
        assert predict(runtime, model, (0, 0)).status == 'PREDICTED_REFERENCE'
        predicted = frames(runtime)
        assert predicted.cuda.phases[-1].status == 'CHECKED_CUDA_PREFIX_PHASE'
        result = runtime.observe(0)
        after = preserved(runtime, before)
        assert result.status == 'UNRESOLVED' and 'integer work limit' in result.reason
        assert after.cuda.phases == predicted.cuda.phases and after.pending.record.target == 0
        assert len(after.event_traces) == len(before.event_traces) and after.cursor == 81
        a = 3*Q
        denominator = 4*(a**81+(a-1)**81)*(a**82+(a-1)**82)
        assert denominator.bit_length() == 32863
        return {**check_phases(runtime), 'expected_refusal': result.status, 'actual_target_retained': 0,
            'failed_observation_index': 81, 'exact_fixed_gradient_denominator_bits': 32863,
            'last_actual_prediction_passed': True, 'physical_observation_entered': False, 'published_advances': 0}
    if case == 'reversal':
        runtime, model = configuration(2, 105, family=((F(1, 10),), (F(1),)), C=10)
        for _ in range(52):
            step(runtime, model, (0, 1, 0))
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert runtime.snapshot().cuda.phases[-1].raw_prediction.decoded().excesses[1] == 0
        assert runtime.observe(1).status == 'OBSERVED_REFERENCE'
        for _ in range(51):
            step(runtime, model, (0, 1, 1))
        state = runtime.snapshot().candidates[0].learner.encoded
        assert state.counts == (0,) and state.steps == 104
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert runtime.snapshot().cuda.phases[-1].raw_prediction.decoded().probabilities == (F(1, 2),)*2
        return {**check_phases(runtime), 'temporary_zero_excess': True, 'restored_zero_count_steps': 104,
                'restored_actual_half_forecast': True, 'final_target_unrevealed': True}
    if case == 'fresh-install':
        persistence = PersistenceContract(F(1, 2), tuple(PersistenceRule(name, 1, 20, F(1, 4), F(3, 4), F(3), 12, 16,
            score_path=path) for name, path in (('ref', REFERENCE_PATH), ('cuda', CUDA_PATH))))
        runtime, model = configuration(2, 36, persistence=persistence, law=True, install=True)
        for _ in range(16):
            step(runtime, model, (0, 1, 1))
        candidate = runtime.construct_candidate(model)
        assert candidate.status == 'BUILT_REFERENCE'
        r = runtime.admit_reference_persistence(candidate.candidate_id, 'ref')
        c = runtime.admit_cuda_persistence(candidate.candidate_id, 'cuda')
        assert r.identity_id and c.identity_id
        assert all(i.start_cursor == 16 and i.status == 'ACTIVE' for i in runtime.snapshot().persistence_identities)
        installed_at = None
        for _ in range(20):
            step(runtime, model, (0, 1, 0))
            if installed_at is None and runtime.paired_cuda_persistence_result(r.identity_id, c.identity_id).status == 'PAIRED_CUDA_CROSSED':
                before = frames(runtime)
                physical = tuple(runtime._cuda._values[v] for _, v in before.cuda.current)
                pointer, stream = runtime._cuda.arena._pointer, runtime._cuda.arena._stream
                installed = runtime.install_cuda(candidate.candidate_id, reference_identity=r.identity_id, cuda_identity=c.identity_id)
                assert installed.status == 'INSTALLED_CUDA', installed
                after = frames(runtime, before)
                assert after.deployed_id == candidate.candidate_id
                assert tuple(v.learner for v in before.candidates) == tuple(v.learner for v in after.candidates)
                assert before.cuda.current == after.cuda.current and before.cuda.phases == after.cuda.phases
                assert all(old is runtime._cuda._values[v] for old, (_, v) in zip(physical, after.cuda.current))
                assert (pointer, stream) == (runtime._cuda.arena._pointer, runtime._cuda.arena._stream)
                assert after.alpha_spent == F(1, 2) and all(i.status == 'UNRESOLVED' for i in after.persistence_identities)
                installed_at = before.cursor
        assert installed_at == 20 and runtime.snapshot().cursor == 36
        return {**check_phases(runtime), 'fresh_start_cursor': 16, 'paired_install_cursor': installed_at,
            'post_install_continuation_to': 36, 'alpha_spent': '1/2', 'same_resident_objects_arena_and_stream': True,
            'constructor_certificate': None}
    raise ValueError(case)


def fault(case):
    family, C = (((F(1, 3),), (F(1),)), 3) if case == 'old-output' else (DEFAULT, 10)
    runtime, model = configuration(3, 4, family=family, C=C, output_cap=2 if case == 'unfunded' else 128)
    if case == 'unfunded':
        before = frames(runtime)
        with patch.object(amp, '_prediction_schedule', side_effect=AssertionError('unfunded device entry')) as forbidden:
            result = predict(runtime, model, (0, 1))
        after = preserved(runtime, before)
        phase = after.cuda.phases[-1]
        assert result.status == 'UNRESOLVED' and not forbidden.called and phase.arena_phase is None
        assert not phase.raw_operations and phase.output_cells == 0 and after.pending.record.target is None
        return dict(status=result.status, executor_entries=0, retained_context_and_failed_phase=True)
    if case == 'second-commit':
        assert runtime.construct_candidate(model).status == 'BUILT_REFERENCE'
        before = frames(runtime)
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        original, calls = executor.commit, []
        def failed(state):
            calls.append(True)
            if len(calls) == 2:
                raise ArithmeticUnresolved('injected second rational-feature physical commit refusal')
            return original(state)
        with patch.object(executor, 'commit', failed):
            result = runtime.observe(0)
        after = preserved(runtime, before)
        assert result.status == 'UNRESOLVED' and len(calls) == 2
        assert after.pending.record.target == 0 and len(after.event_traces) == 2
        assert all(t.after_observe.encoded.pending == (0, 1, 0) for t in after.event_traces)
        assert after.cuda.phases[-1].raw_state.encoded.pending == (0, 1, 0)
        return dict(status=result.status, observed_lineages_retained=2, published_advances=0, retained_target=0)
    query = (0, 0) if case == 'old-output' else (0, 1) if case in ('rate-parts', 'stored-parts') else (1, 2)
    if case in ('rate-parts', 'stored-parts'):
        step(runtime, model, (0, 0, 0))
        step(runtime, model, (0, 0, 0))
    else:
        assert predict(runtime, model, query).status == 'PREDICTED_REFERENCE'
        old_output = runtime._cuda._values[runtime._cuda.predicted[runtime.snapshot().deployed_id]]
        assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
    if case in ('gradient-word', 'target-swap', 'stored-parts'):
        assert predict(runtime, model, query).status == 'PREDICTED_REFERENCE'
    before = frames(runtime)
    changed_parts = ((653, 643), (442, 458))
    if case == 'stored-parts':
        resident = runtime._cuda._values[runtime._cuda.predicted[before.deployed_id]]
        assert resident.rate_parts == ((648, 648), (450, 450))
        object.__setattr__(resident, 'rate_parts', changed_parts)
        rejects(lambda: runtime.observe(0), RuntimeError)
        after = preserved(runtime, before)
        assert after.cuda.phases[-1].status == 'EXECUTION_FAILED' and after.pending.record.target == 0
        return dict(status='EXECUTION_FAILED', actual_target=0, changed_owned_prediction_parts_refused=True,
                    published_advances=0, reason=after.cuda.phases[-1].reason)
    changes = []
    if case in ('prediction-word', 'coefficient-word', 'gradient-word', 'operation-word'):
        method = 'add' if case == 'operation-word' else 'stack'
        original = getattr(gpu.CudaArithmetic, method)
        def changed(arithmetic, *args, **kwargs):
            value = original(arithmetic, *args, **kwargs)
            if not changes:
                import torch
                assert value.dtype == torch.float32
                index = 7 if case == 'coefficient-word' else 0
                value.view(torch.int32).reshape(-1)[index].bitwise_xor_(1)
                changes.append(True)
            return value
        context = patch.object(gpu.CudaArithmetic, method, changed)
    elif case == 'target-swap':
        original = amp._observation_schedule
        def changed(state, prediction, target, arithmetic, **kwargs):
            changes.append(True)
            return original(state, prediction, 1-target, arithmetic, **kwargs)
        context = patch.object(amp, '_observation_schedule', changed)
    else:
        original = amp._prediction_schedule
        def changed(plan, state, arithmetic):
            changes.append(True)
            if case == 'rate-parts':
                assert plan.rate_parts == ((648, 648), (450, 450))
                object.__setattr__(plan, 'rate_parts', changed_parts)
                return original(plan, state, arithmetic)
            raw, resident = original(plan, state, arithmetic)
            if case == 'old-output':
                assert old_output.raw().words == raw.words
                return raw, amp.ResidentPrediction(raw.before, raw.query, old_output.readout, raw.rate_parts, raw.normalization)
            assert case == 'plan-roots'
            object.__setattr__(plan, 'excesses', tuple(2*v for v in plan.excesses))
            object.__setattr__(plan, 'normalization', 2*plan.normalization)
            object.__setattr__(plan, 'rate_parts', tuple(tuple(2*v for v in row) for row in plan.rate_parts))
            return raw, resident
        context = patch.object(amp, '_prediction_schedule', changed)
    with context:
        rejects(lambda: runtime.observe(0) if case in ('gradient-word', 'target-swap') else predict(runtime, model, query), RuntimeError)
    after = preserved(runtime, before)
    assert changes == [True] and after.cuda.phases[-1].status == 'EXECUTION_FAILED'
    actual_target = 0 if case in ('gradient-word', 'target-swap') else None
    assert after.pending.record.target == actual_target
    if case == 'target-swap':
        assert after.cuda.phases[-1].raw_state.encoded.pending[-1] == 1
    return dict(case=case, status='EXECUTION_FAILED', published_advances=0,
        old_frames_and_predecessors_preserved=True, actual_target=actual_target, reason=after.cuda.phases[-1].reason)


def workspace():
    runtime, model = configuration(3, 3)
    key = next(k for k in runtime._buffers if k.endswith(':joint-partition-storage'))
    pinned, original, visits = runtime._buffers[key], decoder.prepare, []
    def monitored(state, query, budget, borrowed, **kwargs):
        assert borrowed is not pinned and borrowed.obj is pinned.obj
        events = runtime.snapshot().resources['events']
        if len(visits) % 3:
            charged = [e for e in events if ':cuda:ordinary:predict:' in str(e[-1]) and 'work' in dict(e[4])]
            assert charged and dict(charged[-1][4])['work'] >= amp.forward_work(model, BUDGET, 128)
        else:
            charged = [e for e in events if str(e[-1]).endswith(':predict')]
            assert charged and dict(charged[-1][4])['work'] == decoder.construction_work(model, BUDGET)
        result = original(state, query, budget, borrowed, **kwargs)
        borrowed.release()
        rejects(lambda: pinned.obj.extend(b'x'), BufferError)
        visits.append(result.compacted_cells)
        return result
    with patch.object(decoder, 'prepare', monitored):
        step(runtime, model, (0, 1, 0))
        step(runtime, model, (1, 2, 1))
    checked, before = check_phases(runtime), frames(runtime)
    calls = []
    def fail_physical(*args, **kwargs):
        value = original(*args, **kwargs)
        calls.append(True)
        if len(calls) == 2:
            raise ArithmeticUnresolved('injected uncertainty after owned rational-feature physical integer construction')
        return value
    with patch.object(decoder, 'prepare', fail_physical):
        result = predict(runtime, model, (0, 2))
    after = preserved(runtime, before)
    assert result.status == 'UNRESOLVED' and len(visits) == 6 and len(calls) == 2
    assert runtime._buffers[key] is pinned and key in after.resources['objects']
    assert after.pending.record.target is None
    rejects(lambda: pinned.obj.extend(b'x'), BufferError)
    return {**checked, 'prepaid_reference_physical_reconstruction_visits': len(visits),
        'postwrite_failure': result.status, 'failed_table_remains_owned_and_pinned': True}


def worker(case):
    if case in ORIGINAL_CASES[:7]:
        return integration(case)
    if case == 'workspace':
        return workspace()
    if case == 'profile-refusal':
        spec = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
        runtime, model = configuration(3, 3, profiles=(spec,), budget=replace(BUDGET, step_cap=1))
        for target in (0, 1):
            step(runtime, model, (0, 1, target))
        before = frames(runtime)
        result = runtime.construct_candidate(model, profile_id='twice')
        after = preserved(runtime, before)
        assert result.status == 'UNRESOLVED' and after.profiles[0].events_completed == 2
        assert after.profiles[0].local.encoded.steps == 2 and after.profiles[0].attached is None
        return {**check_phases(runtime), 'failed_profile_steps_retained': 2, 'published_newborns': 0}
    if case == 'legacy-unit':
        import audit_joint_cuda as legacy
        runtime, model = legacy.configuration(3, 4)
        for event in ((0, 1, 0), (1, 2, 1), (0, 2, 0), (1, 1, 1)):
            step(runtime, model, event)
        return dict(new_shared_owner_regression=legacy.check_phases(runtime),
            scope='fresh four-event unit-feature job after shared owner changes; not a historical attempt rerun')
    return fault(case)


def preflight():
    assert 'torch' not in sys.modules
    cpu = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_AMP_CPU.json').read_text())
    assert cpu['status'] == 'PASS_RATIONAL_FEATURE_AMP_CPU'
    assert sum(row['predictions'] for row in cpu['enumeration']) == 2964
    assert sum(row['both_target_observations'] for row in cpu['enumeration']) == 5928
    assert sum(row['words_including_copies'] for row in cpu['enumeration']) == 550524
    repaired = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_RUN_DIAGNOSTICS.json').read_text())
    assert repaired['status'] == 'PASS_RATIONAL_FEATURE_RUN_DIAGNOSTICS'
    prior = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A1.json').read_text())
    assert prior['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE'
    assert prior['execution_source'] == 'e16c97619a34773a03d4c5aea05d519ea2ac8af3'
    assert prior['registration']['cases'] == list(ORIGINAL_CASES)
    assert [(r['case'], r['worker_status']) for r in prior['workers']] == [
        ('profiles', 'PASS'), ('fresh-install', 'PASS'), ('large-closure', 'FAILED')]
    assert "AttributeError: 'DecodedPrediction' object has no attribute 'values'" in prior['workers'][-1]['result']['traceback']
    second = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A2.json').read_text())
    assert second['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE'
    assert second['execution_source'] == 'f298eab090e10089da2d2f8bee6b9f9bfe266797'
    assert second['registration']['cases'] == list(ORIGINAL_CASES[2:])
    assert [(r['case'], r['worker_status']) for r in second['workers']] == [
        ('large-closure', 'PASS'), ('range-scale', 'PASS'), ('wide-denominator', 'PASS'), ('precision-refusal', 'FAILED')]
    failure = second['workers'][-1]['result']['traceback']
    assert "observation_id='joint-event:41'" in failure and 'reference operation may exceed its integer work limit' in failure
    reduced = json.loads((ROOT/'evidence/minimal/FP_REDUCED_EXACT_RELATIONS.json').read_text())
    assert reduced['status'] == 'PASS_REDUCED_EXACT_RELATIONS'
    assert reduced['continuation']['predictions'] == 82 and reduced['continuation']['observed_and_committed'] == 81
    assert reduced['continuation']['exact_gradient_denominator_bits'] == 32863
    assert reduced['owner_tariff']['work_model'] == amp.WORK_MODEL
    third = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A3.json').read_text())
    assert third['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE'
    assert third['execution_source'] == '862e91c112a71619f32f2b7aac1704d2fb415ddf'
    assert third['registration']['cases'] == list(ORIGINAL_CASES[5:])
    assert [(r['case'], r['worker_status']) for r in third['workers']] == [
        *((case, 'PASS') for case in ORIGINAL_CASES[5:19]), ('profile-refusal', 'FAILED')]
    failure = third['workers'][-1]['result']['traceback']
    assert 'record.reference.materialize' in failure and 'joint committed-step allowance exhausted' in failure
    reader = json.loads((ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_READER_BUDGET.json').read_text())
    assert reader['status'] == 'PASS_RATIONAL_FEATURE_READER_BUDGET'
    assert reader['full_native_state_and_failed_profile_comparisons'] == 8
    assert reader['runtime_prediction_step_cap'] == 1 and reader['independently_funded_materialization_step_cap'] == 2
    assert runner.indexed.CAP == CAP
    git = runner.registration.model.git
    assert not git('diff', ANCHOR, '--', 'src/reference_compiler')
    changed = [f'src/reference_compiler/fp_reference/{name}.py' for name in
               ('cuda_prefix', 'float64_bridge', 'joint_amp', 'numerics', 'rational_feature_amp')]
    assert git('diff', '--name-only', 'dcdd3e9', ANCHOR, '--', 'src/reference_compiler').splitlines() == changed
    assert not git('diff', '862e91c', '--', 'src/reference_compiler')
    return dict(status='REGISTERED_RATIONAL_FEATURE_CUDA_CONTINUATION_A4', production_anchor=ANCHOR,
        prior_attempts=['FP_RATIONAL_FEATURE_AMP_CUDA_A1.json', 'FP_RATIONAL_FEATURE_AMP_CUDA_A2.json',
                       'FP_RATIONAL_FEATURE_AMP_CUDA_A3.json'],
        prior_passing_cases=list(ORIGINAL_CASES[:19]), changed_production_files=[],
        solver_production_files_from_A2=changed, production_unchanged_since='862e91c',
        work_model=amp.WORK_MODEL, relation_tariff='2048*(d+2*n+8*J+32)',
        changed_scope='passive literal reader funds max(runtime step_cap, materialized committed T); runtime unchanged from A3',
        literal_materialization_step_cap='max(runtime step_cap, materialized committed T)',
        cases=CASES, job_cap=CAP, deadline_ms=DEADLINE, fresh_owner_per_job=True,
        budget=asdict(BUDGET), profile_integer_bits=4096, wide_step_cap=8, precision_step_cap=100,
        arena_bytes=32 << 20, allocator_cap=64 << 20, output_cells=128,
        frame_bytes_n2_n3=65536, frame_bytes_n64=524288, state_atol='1/100', probability_atol='1/1000',
        activation_cap='C-2', normalizer_cap='2*(C-1)', forward_id=amp.FORWARD_ID,
        evidence_encoding=phase_deflate.ENCODING_ID, literal_audit_bits=131072, reference_bits=32768,
        report_error_upper_grid_bits=48, expected_reference_refusal='label0 after 81 diagonal-zero commits at q=2^200+1; last physical prediction passes',
        failure_policy='stop at first unexpected failure; retain every outcome; no retry or changed cap within attempt',
        scope='actual complete native AMP/cache/gradient conformance and owned continuation/fresh install; no model superiority, GPU integer inference or constructor completeness')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        report = dict(status='FAILED_AUDIT', process_id=os.getpid(), case=args.worker)
        try:
            report.update(status=STATUS, result=worker(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        if args.attempt != 4:
            parser.error('only continuation A4 is registered here; A1/A2/A3 remain terminal')
        runner.matrix(args.attempt, script=__file__, cases=CASES, journal_prefix='FP_RATIONAL_FEATURE_AMP_CUDA',
            registration_fn=preflight, production_anchor=ANCHOR, result_status=STATUS, final_status=STATUS, worker_status='PASS')
    else:
        parser.error('select --preflight, --attempt or --worker')
