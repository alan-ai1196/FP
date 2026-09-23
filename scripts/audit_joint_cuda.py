"""Preregistered fresh-job gate for the owned joint-noise AMP realization."""
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
from fp_reference import joint_amp as amp, joint_partition_decoder as decoder, joint_cuda_prefix as executor
from fp_reference import cuda_learner as gpu, phase_deflate
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.encoding import pack
from fp_reference.joint_relation import JointRelation, initialize, observe, commit, attach
from fp_reference.joint_execution import JointState
from fp_reference.learner import observe_event, commit_event
from fp_reference.profile import ProfileSpec, attach_boundary
from fp_reference.persistence import PersistenceContract, PersistenceRule, REFERENCE_PATH, CUDA_PATH
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_joint_runtime import fixture, literal, predict
from audit_joint_amp import BUDGET, configuration as cuda_contract, independent_state, operations, TOLERANCE
from audit_reference_construction import validate_residency, rejects
from audit_cuda_runtime import phase_payload, no_device_handles
from unknown_noise_decoding import DEFAULT, OTHER
import mixture_partition_bridge as prototype
import audit_phase_writer_binding as runner

CAP = 4 << 30
STATUS = 'PASS_ACTUAL_OWNED_JOINT_AMP'
CASES = ('profiles', 'fresh-install', 'large-closure', 'old-A1-cut', 'reversal', 'scale-refusal',
    'unfunded', 'second-commit', 'prediction-word', 'gradient-word', 'operation-word',
    'old-output', 'target-swap', 'plan-roots', 'workspace', 'profile-refusal', 'legacy-shared-owner')


def configuration(n, length, *, family=DEFAULT, profiles=(), persistence=None, law=False,
                  install=False, policy=False, budget=BUDGET, output_cap=64):
    cfg, schema, online = fixture(n, length, family=family, profiles=profiles,
        persistence=persistence, law=law, budget=budget, byte_cap=1 << 30, work_cap=10**14)
    cfg = replace(cfg, normalizer_cap=F(2*(schema.scale-1)))
    cuda = cuda_contract(schema, budget, phase_output_cells=output_cap,
        phase_evidence_bytes=65536 if n <= 5 else 524288,
        evidence_encoding=phase_deflate.ENCODING_ID, install=CudaInstallContract() if install else None)
    return ReferenceCompilerRuntime(cfg, schema, online=online, cuda=cuda,
        host=HostResourceContract(CAP, {r: CAP for r in ('deployment', 'compiler')}),
        policy=CudaCompilerPolicy(()) if policy else None), schema


def step(runtime, model, event):
    i, j, target = event
    answer = predict(runtime, model, (i, j))
    assert answer.status == 'PREDICTED_REFERENCE', answer
    result = runtime.observe(target)
    assert result.status == 'OBSERVED_REFERENCE', result


def frames(runtime, prior=None):
    snapshot = validate_residency(runtime)
    no_device_handles(snapshot)
    buffers = dict(snapshot.buffers)
    if prior is not None:
        assert tuple(pack(p) for p in prior.cuda.phases) == tuple(pack(p) for p in snapshot.cuda.phases[:len(prior.cuda.phases)])
    for record in snapshot.cuda.phases:
        frame = buffers[record.object_id]
        used = int.from_bytes(frame[:8], 'big')
        assert phase_payload(snapshot, frame) == pack(record) and not any(frame[8+used:])
        if record.status == 'CHECKED_CUDA_PREFIX_PHASE':
            assert type(runtime._buffers[record.object_id]) is bytes
    return snapshot


def check_phases(runtime):
    snapshot = frames(runtime)
    model = snapshot.cuda.contract.schema
    assert snapshot.cuda.contract.forward_id == amp.FORWARD_ID
    records = {p.object_id: p for p in snapshot.cuda.phases}
    observations = {r.observation_id: r for r in snapshot.observations}
    if snapshot.pending is not None:
        observations[snapshot.pending.record.observation_id] = snapshot.pending.record
    native_states, native_predictions, plans = {}, {}, {}
    bundle = literal(model) if model.n <= 3 else None
    words = half = outputs = predictions = native_phases = 0
    maximum_frame = 0
    maxima = {}
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record
        kind = record.phase.split(':')[-1]
        predecessor = records.get(record.input_phase)
        assert record.raw_state.encoded == record.reference.encoded
        expected_native = None
        if kind == 'initialize':
            expected = initialize(model, record.ordinary_cursor)
            if bundle:
                expected_native = literal(model, record.ordinary_cursor)[3]
        elif kind == 'predict':
            expected = predecessor.raw_state.encoded
            query, _ = model.source_query(model.rules(), dict(observations[record.observation_id].sources))
            assert record.raw_prediction.before == expected and record.raw_prediction.query == query
            oracle = prototype.prepare(independent_state(expected), query)
            plans[record.object_id] = oracle
            columns, _, trace = prototype.rounded(oracle)
            assert (record.execution_plan.excesses, record.execution_plan.normalization) == (oracle.excess_parts, oracle.normalization)
            assert record.execution_plan.before == expected and record.execution_plan.query == query
            assert record.execution_plan.bit_limit == min(32768, snapshot.cuda.contract.partitions.integer_bits)
            assert record.raw_prediction.words == tuple(v.word for v in columns)
            actual_ops = tuple(('host-RNE32-ingress' if tag == 'constant' else 'cast-float'+str(width) if tag == 'cast' else tag,
                width, (word,)) for tag, width, word in trace[0])
            assert record.raw_operations == actual_ops and record.output_cells == oracle.output_cells
            assert record.forward_operations == len(actual_ops)
            exact = prototype.reference(oracle)
            actual_ref = record.reference_prediction
            assert exact == actual_ref.excesses+actual_ref.masses+(actual_ref.normalizer,)+actual_ref.probabilities
            predictions += 1
            if bundle:
                rules, graph, spec, _ = bundle
                expected_native = native_states[record.input_phase]
                cache = evaluate(graph, rules, expected_native.theta, dict(observations[record.observation_id].sources), (), bit_limit=32768)
                native_predictions[record.object_id] = cache
                assert actual_ref.materialize(scalar_cap=10000) == cache
                physical = record.raw_prediction.decoded().materialize(scalar_cap=10000)
                assert max(abs(a-b) for a, b in zip(cache.values, physical.values)) <= TOLERANCE.state_atol
        elif kind == 'observe':
            prediction = records[record.prediction_phase]
            actual_target = observations[record.observation_id].target
            assert prediction.input_phase == record.input_phase and prediction.observation_id == record.observation_id
            expected = observe(predecessor.raw_state.encoded, prediction.raw_prediction.query, actual_target)
            columns = tuple(amp._Scalar(v, 32) for v in prediction.raw_prediction.words)
            arithmetic = amp._Arithmetic(32768)
            gradient, _ = prototype.observation_schedule(plans[prediction.object_id], columns, actual_target, arithmetic)
            assert record.raw_state.gradient_words == tuple(v.word for v in gradient)
            assert record.raw_operations == operations(arithmetic) and record.output_cells == 6+8*len(model.rates)
            if bundle:
                expected_native = observe_event(bundle[1], native_states[record.input_phase], bundle[2],
                    native_predictions[record.prediction_phase], actual_target, bit_limit=32768)
        elif kind == 'commit':
            expected = commit(predecessor.raw_state.encoded)
            if bundle:
                expected_native = commit_event(native_states[record.input_phase], bundle[2], bit_limit=32768)
        elif kind == 'attach':
            expected = attach(predecessor.raw_state.encoded, record.ordinary_cursor)
            # Derive the clock namespace from the phase predecessor, not
            # from the reference or physical endpoint being checked.
            if predecessor.phase.endswith(':initialize') and record.phase.startswith('profile:'):
                expected = attach(predecessor.raw_state.encoded, 0)
            if bundle:
                expected_native = attach_boundary(native_states[record.input_phase], expected.cursor, bundle[2])
        else:
            raise AssertionError(kind)
        assert expected == record.raw_state.encoded
        if kind in ('initialize', 'commit', 'attach'):
            assert not record.raw_operations and not record.raw_state.gradient_words and record.output_cells == 0
        if expected_native is not None:
            assert record.reference.materialize(scalar_cap=10000, budget=BUDGET) == expected_native
            physical = JointState(record.raw_state.encoded, tuple(amp.single(v) for v in record.raw_state.gradient_words)).materialize(
                scalar_cap=10000, budget=BUDGET)
            assert physical.theta == expected_native.theta
            assert max(abs(a-b) for a, b in zip(physical.gradient_sum, expected_native.gradient_sum)) <= TOLERANCE.state_atol
            native_states[record.object_id] = expected_native
            native_phases += 1
        for key, value in vars(record.relation).items():
            maxima[key] = max(maxima.get(key, F(0)), value)
        outputs += record.output_cells
        for _, width, values in record.raw_operations:
            words += len(values)
            half += len(values) if width == 16 else 0
        maximum_frame = max(maximum_frame, int.from_bytes(dict(snapshot.buffers)[record.object_id][:8], 'big'))
    key = next(k for k in runtime._buffers if k.endswith(':joint-partition-storage'))
    assert len(runtime._buffers[key]) == decoder.workspace_bytes(model, snapshot.cuda.contract.partitions)
    return {'checked_phases': len(snapshot.cuda.phases), 'independent_partition_RNE_predictions': predictions,
        'full_literal_native_phases': native_phases, 'actual_operation_words': words, 'actual_half_words': half,
        'output_words_including_copies': outputs, 'cursor': snapshot.cursor, 'table_bytes': len(runtime._buffers[key]),
        'packed_peak_bytes': snapshot.resources['peak']['reference_payload_bytes'],
        'consumed_arena_bytes': snapshot.cuda.storage['consumed_arena_extent'], 'largest_encoded_frame_bytes': maximum_frame,
        'maximum_relation_errors': {k: str(v) for k, v in maxima.items()}}


def preserved(runtime, before):
    after = frames(runtime, before)
    assert after.candidates == before.candidates and after.cursor == before.cursor
    assert after.cuda.current == before.cuda.current
    return after


def integration(case):
    word = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 1), (2, 2, 0), (1, 0, 1), (0, 1, 0))
    if case == 'profiles':
        spec = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
        runtime, model = configuration(3, 8, profiles=(spec,), budget=replace(BUDGET, integer_bits=4096))
        for k, event in enumerate(word):
            step(runtime, model, event)
            if k == 1:
                assert runtime.construct_candidate(model, profile_id='twice').status == 'BUILT_REFERENCE'
        assert sorted(c.learner.optimizer_steps for c in runtime.snapshot().candidates) == [8, 10]
        return {**check_phases(runtime), 'profile_events': 4, 'optimizer_steps': [8, 10]}
    if case == 'large-closure':
        with patch.object(JointRelation, 'materialize_program', side_effect=AssertionError('world expansion')), \
                patch.object(JointRelation, 'materialize_learner', side_effect=AssertionError('slot expansion')):
            runtime, model = configuration(64, 8, policy=True)
            for event in word:
                step(runtime, model, event)
        final = runtime.snapshot()
        assert final.run.status == 'SEALED_CUDA_STREAM' and not final.run.closure.decisions
        return {**check_phases(runtime), 'worlds': str(model.K), 'closure': final.run.status, 'constructor_decisions': 0}
    if case == 'old-A1-cut':
        spec = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
        runtime, model = configuration(2, 48, profiles=(spec,))
        cut = None
        for k in range(48):
            step(runtime, model, (0, 1, 0))
            if k == 1:
                assert runtime.construct_candidate(model, profile_id='twice').status == 'BUILT_REFERENCE'
            if k == 26:
                cut = tuple((c.learner.cursor, c.learner.optimizer_steps, c.learner.encoded.counts) for c in runtime.snapshot().candidates)
        assert (27, 29, (29,)) in cut
        return {**check_phases(runtime), 'historical_cut_reached_by_new_source': cut,
                'scope': 'new joint-excess realization at original tolerances; terminal dense A1/A2 unchanged'}
    if case == 'reversal':
        runtime, model = configuration(2, 105, family=((F(1, 10),), (F(1),)))
        for _ in range(52):
            step(runtime, model, (0, 1, 0))
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        phase = runtime.snapshot().cuda.phases[-1]
        assert phase.raw_prediction.decoded().excesses[1] == 0
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
                installed = runtime.install_cuda(candidate.candidate_id, reference_identity=r.identity_id, cuda_identity=c.identity_id)
                assert installed.status == 'INSTALLED_CUDA', installed
                after = frames(runtime, before)
                assert after.deployed_id == candidate.candidate_id
                assert tuple(v.learner for v in before.candidates) == tuple(v.learner for v in after.candidates)
                assert before.cuda.current == after.cuda.current and before.cuda.phases == after.cuda.phases
                assert after.alpha_spent == F(1, 2) and all(i.status == 'UNRESOLVED' for i in after.persistence_identities)
                installed_at = before.cursor
        assert installed_at is not None and runtime.snapshot().cursor > installed_at
        return {**check_phases(runtime), 'fresh_start_cursor': 16, 'paired_install_cursor': installed_at,
            'post_install_continuation_to': 36, 'alpha_spent': '1/2', 'constructor_certificate': None}
    raise ValueError(case)


def fault(case):
    family = ((F(1, 3),), (F(1),)) if case == 'old-output' else DEFAULT
    runtime, model = configuration(3, 3, family=family, output_cap=2 if case == 'unfunded' else 64)
    if case == 'unfunded':
        before = frames(runtime)
        with patch.object(amp, '_prediction_schedule', side_effect=AssertionError('unfunded device kernel entered')) as forbidden:
            result = predict(runtime, model, (0, 1))
        after = preserved(runtime, before)
        phase = after.cuda.phases[-1]
        assert result.status == 'UNRESOLVED' and not forbidden.called and phase.arena_phase is None
        assert not phase.raw_operations and phase.output_cells == 0 and after.pending.record.target is None
        return {'status': result.status, 'executor_entries': 0, 'retained_context_and_failed_phase': True}
    if case == 'second-commit':
        assert runtime.construct_candidate(model).status == 'BUILT_REFERENCE'
        before = frames(runtime)
        assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
        original, calls = executor.commit, []
        def failed(state):
            calls.append(True)
            if len(calls) == 2:
                raise ArithmeticUnresolved('injected second joint physical commit refusal')
            return original(state)
        with patch.object(executor, 'commit', failed):
            result = runtime.observe(0)
        after = preserved(runtime, before)
        assert result.status == 'UNRESOLVED' and len(calls) == 2
        assert after.pending.record.target == 0 and len(after.event_traces) == 2
        assert all(t.after_observe.encoded.pending == (0, 1, 0) for t in after.event_traces)
        assert after.cuda.phases[-1].raw_state.encoded.pending == (0, 1, 0)
        return {'status': result.status, 'observed_lineages_retained': 2, 'published_advances': 0, 'retained_target': 0}
    query = (0, 0) if case == 'old-output' else (1, 2)
    assert predict(runtime, model, query).status == 'PREDICTED_REFERENCE'
    old_output = runtime._cuda._values[runtime._cuda.predicted[runtime.snapshot().deployed_id]]
    assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
    if case in ('gradient-word', 'target-swap'):
        assert predict(runtime, model, query).status == 'PREDICTED_REFERENCE'
    before = frames(runtime)
    changes = []
    if case in ('prediction-word', 'gradient-word', 'operation-word'):
        method = 'add' if case == 'operation-word' else 'stack'
        original = getattr(gpu.CudaArithmetic, method)
        def changed(arithmetic, *args, **kwargs):
            value = original(arithmetic, *args, **kwargs)
            if not changes:
                import torch
                assert value.dtype == torch.float32
                value.view(torch.int32).reshape(-1)[0].bitwise_xor_(1)
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
            raw, resident = original(plan, state, arithmetic)
            changes.append(True)
            if case == 'old-output':
                assert old_output.raw().words == raw.words
                return raw, amp.ResidentPrediction(raw.before, raw.query, old_output.readout)
            assert case == 'plan-roots'
            object.__setattr__(plan, 'excesses', tuple(2*v for v in plan.excesses))
            object.__setattr__(plan, 'normalization', 2*plan.normalization)
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
    return {'case': case, 'status': 'EXECUTION_FAILED', 'published_advances': 0,
        'old_frames_and_native_physical_predecessors_preserved': True, 'actual_target': actual_target,
        'reason': after.cuda.phases[-1].reason}


def workspace():
    runtime, model = configuration(3, 3)
    key = next(k for k in runtime._buffers if k.endswith(':joint-partition-storage'))
    pinned, original, visits = runtime._buffers[key], decoder.prepare, []
    def monitored(state, query, budget, borrowed, **kwargs):
        assert borrowed is not pinned and borrowed.obj is pinned.obj
        events = runtime.snapshot().resources['events']
        if len(visits) % 3:
            charged = [e for e in events if ':cuda:ordinary:predict:' in str(e[-1]) and 'work' in dict(e[4])]
            assert charged and dict(charged[-1][4])['work'] >= amp.forward_work(model, BUDGET, 64)
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
            raise ArithmeticUnresolved('injected fault after owned physical integer construction')
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
    if case in ('profiles', 'fresh-install', 'large-closure', 'old-A1-cut', 'reversal'):
        return integration(case)
    if case == 'workspace':
        return workspace()
    if case == 'scale-refusal':
        runtime, model = configuration(2, 3, family=OTHER)
        for _ in range(2):
            step(runtime, model, (0, 1, 1))
        checked, before = check_phases(runtime), frames(runtime)
        result = predict(runtime, model, (0, 1))
        after = preserved(runtime, before)
        phase = after.cuda.phases[-1]
        assert result.status == phase.status == 'UNRESOLVED' and phase.output_cells == 29
        assert 'native coordinate' in phase.reason and after.pending.record.target is None
        error = max(abs(a-b) for a, b in zip(phase.reference_prediction.masses, phase.raw_prediction.decoded().masses))
        assert error == F(65863667, 4117889024) > TOLERANCE.state_atol
        return {**checked, 'expected_refusal': result.status, 'actual_native_error': str(error), 'third_target_received': False}
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
    if case == 'legacy-shared-owner':
        import audit_owned_integer_partition_cuda as legacy
        runtime, model = legacy.configuration(3, 4)
        for event in ((0, 1, 0), (1, 2, 1), (0, 2, 0), (1, 1, 1)):
            step(runtime, model, event)
        return {'new_shared_owner_regression': legacy.check_phases(runtime), 'scope': 'fresh four-event job after shared owner changes; no old attempt rerun'}
    return fault(case)


def preflight():
    assert 'torch' not in sys.modules
    audit = json.loads((ROOT/'evidence/minimal/FP_JOINT_AMP_CPU.json').read_text(encoding='utf-8'))
    assert audit['complete_audit'] and audit['status'] == 'PASS_JOINT_AMP_CPU'
    return {'status': 'REGISTERED_BEFORE_JOINT_CUDA_EXECUTION', 'cases': CASES,
        'job_cap': CAP, 'deadline_ms': 900000, 'fresh_owner_per_job': True,
        'budget': asdict(BUDGET), 'profile_integer_bits': 4096, 'arena_bytes': 32 << 20, 'allocator_cap': 64 << 20,
        'output_cells': 64, 'frame_bytes_n2_n3': 65536, 'frame_bytes_n64': 524288,
        'state_atol': '1/100', 'probability_atol': '1/1000', 'native_normalizer_cap': '2*(S-1)',
        'native_activation_cap': 'S-2', 'forward_id': amp.FORWARD_ID, 'evidence_encoding': phase_deflate.ENCODING_ID,
        'expected_scale_refusal': 'S120 third prediction after two label1 events; no tolerance relaxation',
        'failure_policy': 'stop at first unexpected failure; retain every outcome; no retry or changed cap within attempt',
        'scope': 'paid host integer inference and actual GPU half/single phases, profiles, paired fresh install and adversarial lifetime; no model superiority, GPU integer inference or constructor completeness'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        report = {'status': 'FAILED_AUDIT', 'process_id': os.getpid(), 'case': args.worker}
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
        runner.matrix(args.attempt, script=__file__, cases=CASES, journal_prefix='FP_JOINT_AMP_CUDA',
            registration_fn=preflight, production_anchor='HEAD', result_status=STATUS, final_status=STATUS, worker_status='PASS')
    else:
        parser.error('select --preflight, --attempt or --worker')
