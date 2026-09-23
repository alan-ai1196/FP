"""Preregistered actual Runtime gate for the fixed histogram realization."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations
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
from fp_reference import histogram_decoder as hist, histogram_amp as physical, indexed_amp as amp
from fp_reference import phase_deflate, query_projection
from fp_reference.encoding import pack
from fp_reference.indexed_relation import DecodeAllowance
from fp_reference.semantics import ArithmeticUnresolved
from audit_reference_construction import validate_residency, rejects
from audit_indexed_source_binding import predict
from audit_cuda_runtime import phase_payload, no_device_handles
from audit_owned_histogram import BUDGET, fixture, operations
from audit_count_histogram import oracle
import count_histogram as prototype
import audit_indexed_amp as indexed
import audit_indexed_owned_schedule as owned
import audit_phase_writer_binding as runner

ORIGINAL_CONFIGURATION = indexed.configuration
INTEGRATION = ('profiles', 'install', 'closure', 'unfunded', 'second-commit')
FAULTS = ('retired-producers', 'fault-prediction-word', 'fault-gradient-word', 'fault-operation-word')
CASES = INTEGRATION+FAULTS+('old-output', 'target-swap', 'plan-term', 'workspace', 'underflow-reversal', 'dense',
                           'legacy-large', 'legacy-projected-large')


def configuration(*args, **kwargs):
    with patch.object(indexed, 'fixture', fixture):
        return ORIGINAL_CONFIGURATION(*args, **{**kwargs, 'histogram': BUDGET,
            'evidence_encoding': phase_deflate.ENCODING_ID})


def check_phases(rt, **unused):
    snapshot = validate_residency(rt)
    no_device_handles(snapshot)
    assert snapshot.cuda.contract.histogram == BUDGET
    assert snapshot.cuda.contract.forward_id == physical.FORWARD_ID
    buffers = dict(snapshot.buffers)
    words = outputs = half = predictions = 0
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record
        frame = buffers[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        assert type(rt._buffers[record.object_id]) is bytes
        assert phase_payload(snapshot, frame) == pack(record) and not any(frame[8+size:])
        kind = record.phase.split(':')[-1]
        assert record.raw_state.encoded == record.reference.encoded
        if kind == 'predict':
            raw = record.raw_prediction
            expected, histogram, trace = prototype.rounded_prediction(raw.before, raw.query)
            assert record.execution_plan.before == record.reference.encoded == raw.before
            assert record.execution_plan.terms == histogram.terms
            assert raw == expected and record.output_cells == histogram.output_cells
            expected_operations = tuple(('host-RNE32-ingress' if tag == 'constant' else
                'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
                for tag, width, word in trace)
            assert record.raw_operations == expected_operations
            reference, _ = prototype.reference(raw.before, raw.query)
            assert record.reference_prediction.probabilities == reference.probabilities
            assert record.forward_operations == len(trace)
            predictions += 1
        elif kind == 'observe':
            previous = next(p for p in snapshot.cuda.phases if p.object_id == record.input_phase)
            prediction = next(p for p in snapshot.cuda.phases if p.object_id == record.prediction_phase)
            amp.check_observation_execution(previous.raw_state, prediction.raw_prediction,
                record.raw_state.encoded.pending[2], record.raw_state, record.raw_operations, bit_limit=32768)
        else:
            assert not record.raw_state.gradient_words and record.output_cells == 0
        outputs += record.output_cells
        for _, width, values in record.raw_operations:
            words += len(values)
            half += len(values) if width == 16 else 0
    scratch_id = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    assert len(rt._buffers[scratch_id]) == hist.workspace_bytes(BUDGET)
    return {'checked_phases': len(snapshot.cuda.phases), 'actual_floating_words': words,
        'output_words_including_copies': outputs, 'actual_half_words': half,
        'independent_histogram_prediction_readers': predictions, 'cursor': snapshot.cursor,
        'histogram_billed_and_actual_bytes': len(rt._buffers[scratch_id]),
        'packed_current_bytes': snapshot.resources['current']['reference_payload_bytes'],
        'consumed_arena_bytes': snapshot.cuda.storage['consumed_arena_extent']}


def preserved(rt, before):
    after = owned.frames(rt, before, tuple(pack(p) for p in before.cuda.phases))
    assert after.candidates == before.candidates and after.cursor == before.cursor
    assert after.cuda.current == before.cuda.current and after.halted
    assert after.cuda.phases[-1].status == 'EXECUTION_FAILED'
    return after


def fault(case):
    rt, schema = configuration(3, 2)
    if case == 'old-output':
        first = predict(rt, schema, (0, 0))
        assert first.status == 'PREDICTED_REFERENCE'
        old = rt._cuda._values[rt._cuda.predicted[rt.snapshot().deployed_id]]
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        before = validate_residency(rt)
        original = physical._prediction_schedule
        def changed(plan, state, arithmetic):
            raw, resident = original(plan, state, arithmetic)
            assert old.raw().words == raw.words
            return raw, amp.ResidentPrediction(raw.before, raw.query, old.readout)
        with patch.object(physical, '_prediction_schedule', changed):
            rejects(lambda: predict(rt, schema, (1, 1)), RuntimeError)
        after = preserved(rt, before)
        assert 'raw phase readout' in after.cuda.phases[-1].reason
    elif case == 'target-swap':
        assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        before = validate_residency(rt)
        original = amp._observation_schedule
        def changed(state, prediction, target, arithmetic, **kwargs):
            return original(state, prediction, 1-target, arithmetic, **kwargs)
        with patch.object(amp, '_observation_schedule', changed):
            rejects(lambda: rt.observe(0), RuntimeError)
        after = preserved(rt, before)
        assert after.pending.record.target == after.observations[-1].target == 0
        assert after.cuda.phases[-1].raw_state.encoded.pending == (0, 1, 1)
    elif case == 'plan-term':
        indexed.step(rt, schema, (0, 1, 0))
        before = validate_residency(rt)
        original = physical._prediction_schedule
        def changed(plan, state, arithmetic):
            result = original(plan, state, arithmetic)
            part = plan.terms[0]
            k, h = part[0]
            object.__setattr__(plan, 'terms', (((k, h+1),)+part[1:], plan.terms[1]))
            return result
        with patch.object(physical, '_prediction_schedule', changed):
            rejects(lambda: predict(rt, schema, (0, 1)), RuntimeError)
        after = preserved(rt, before)
        assert 'histogram plan differs' in after.cuda.phases[-1].reason
    else:
        raise ValueError(case)
    assert after.pending.record.target == (0 if case == 'target-swap' else None)
    return {'case': case, 'status': 'EXECUTION_FAILED', 'published_advances': 0,
        'reason': after.cuda.phases[-1].reason, 'checked_full_records': len(after.cuda.phases),
        'actual_target_retained': after.pending.record.target,
        'native_predecessors_and_old_sealed_records_preserved': True}


def workspace():
    rt, schema = configuration(3, 3)
    key = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    permanent = rt._buffers[key]
    original = hist.prepare
    handles, calls, blocked = [], [], []
    def resize(backing):
        try:
            backing.extend(b'x')
        except BufferError:
            blocked.append(True)
        else:
            raise AssertionError('actual histogram scratch grew behind the paid extent')
    def monitored(before, query, budget, borrowed, **kwargs):
        assert borrowed is not permanent and borrowed.obj is permanent.obj
        if handles:
            resize(handles[-1])
        events = rt.snapshot().resources['events']
        if len(calls) % 3:
            charged = [e for e in events if ':cuda:ordinary:predict:' in str(e[-1])
                       and 'work' in dict(e[4])]
            assert charged and dict(charged[-1][4])['work'] >= physical.forward_work(
                schema.n, budget, rt._cuda.contract.phase_output_cells)
        else:
            charged = [e for e in events if str(e[-1]).endswith(':predict')]
            assert charged and dict(charged[-1][4])['work'] == hist.enumeration_work(schema.n, budget)
        result = original(before, query, budget, borrowed, **kwargs)
        backing = borrowed.obj
        handles.append(backing)
        borrowed.release()
        resize(backing)
        calls.append(result.world_visits)
        return result
    with patch.object(hist, 'prepare', monitored):
        indexed.step(rt, schema, (0, 1, 0))
        before = validate_residency(rt)
        saved = tuple(pack(p) for p in before.cuda.phases)
        indexed.step(rt, schema, (1, 2, 1))
    resize(handles[0])
    after = owned.frames(rt, before, saved)
    assert calls == [4]*6 and len(blocked) == 12
    assert after.candidates[0].learner.encoded.counts == (1, 0, -1)
    return {**check_phases(rt), 'prepaid_reference_physical_and_reconstruction_calls': len(calls),
            'blocked_resizes': len(blocked), 'old_history_unchanged': True}


def dense():
    rt, schema = configuration(16, 121)
    for i, j in combinations(range(16), 2):
        indexed.step(rt, schema, (i, j, 0))
    before = validate_residency(rt)
    counts = before.candidates[0].learner.encoded
    assert counts.counts == (1,)*120 and counts.cursor == counts.steps == 120
    rejects(lambda: query_projection.prepare(counts, (0, 1), DecodeAllowance()), ArithmeticUnresolved)
    assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    prediction = rt.snapshot().cuda.phases[-1]
    assert prediction.execution_plan.term_count == 17 and prediction.output_cells == 170
    _, parts = oracle(counts, (0, 1))
    expected = (1+8*F(parts[0], sum(parts)))/10
    assert prediction.reference_prediction.probabilities[0] == expected
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    assert rt.snapshot().candidates[0].learner.encoded.counts == (0,)+(1,)*119
    return {**check_phases(rt), 'complete_count_coordinates': 120,
        'dense_native_history_events': 120, 'independent_final_assignment_terms': 32768,
        'old_join_class': 'UNRESOLVED', 'final_prediction_outputs': 170,
        'exact_reference_forecast': str(expected), 'continued_opposite_label': True}


def reversal():
    rt, schema = configuration(2, 105)
    for _ in range(52):
        indexed.step(rt, schema, (0, 1, 0))
    assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    at_zero = rt.snapshot().cuda.phases[-1]
    assert at_zero.raw_prediction.decoded().excesses[1] == 0
    assert at_zero.reference_prediction.excesses[1] > 0
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    for _ in range(51):
        indexed.step(rt, schema, (0, 1, 1))
    assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    final = rt.snapshot()
    assert final.cursor == 104 and final.candidates[0].learner.encoded.counts == (0,)
    assert final.cuda.phases[-1].raw_prediction.decoded().probabilities == (F(1, 2),)*2
    assert final.pending.record.target is None
    return {**check_phases(rt), 'transient_zero_at_cursor': 52,
        'native_zeroed_coordinate_remains_positive': True,
        'contrary_events': 52, 'returned_forecast': ['1/2', '1/2'],
        'complete_counts_preserved_and_recovered': True}


def worker(case):
    if case.startswith('legacy-'):
        def legacy(*args, **kwargs):
            return ORIGINAL_CONFIGURATION(*args, **{**kwargs, 'evidence_encoding': phase_deflate.ENCODING_ID})
        with patch.object(indexed, 'configuration', legacy):
            return indexed.worker(case[len('legacy-'):])
    with patch.object(indexed, 'configuration', configuration), patch.object(indexed, 'check_phases', check_phases):
        if case in INTEGRATION:
            return indexed.worker(case)
        if case in FAULTS:
            return owned.probe(case)
        if case in ('old-output', 'target-swap', 'plan-term'):
            return fault(case)
        if case == 'workspace':
            return workspace()
        if case == 'dense':
            return dense()
        if case == 'underflow-reversal':
            return reversal()
    raise ValueError(case)


def preflight():
    assert 'torch' not in sys.modules
    return {'status': 'REGISTERED_OWNED_HISTOGRAM_GATE', 'cases': CASES,
        'job_cap': indexed.CAP, 'deadline_ms': 900000, 'fresh_owner_per_job': True,
        'histogram_bytes': hist.workspace_bytes(BUDGET), 'world_cap': BUDGET.world_cap,
        'span_cap': BUDGET.span_cap, 'reference_machine': hist.MODEL_ID,
        'forward_id': physical.FORWARD_ID, 'arena_bytes': 32 << 20,
        'phase_output_cap': 65536, 'phase_frame_bytes': 262144,
        'legacy_n256_frame_bytes': 4 << 20, 'evidence_encoding': phase_deflate.ENCODING_ID,
        'state_atol': '1/100', 'probability_atol': '1/1000',
        'fault_scope': 'fresh device words, stale output, supplied plan coefficient, supplied scratch operations and target binding; no arbitrary Python process sandbox',
        'failure_policy': 'stop at first failure; retain every outcome; no silent retry or cap changes',
        'scope': 'complete owned component continuations and dense width recovery; no model score or new complete indexed release'}


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
            report.update(status='PASS_ACTUAL_OWNED_HISTOGRAM', result=worker(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt, script=__file__, cases=CASES,
            journal_prefix='FP_OWNED_HISTOGRAM_CUDA', registration_fn=preflight,
            production_anchor='HEAD', result_status='PASS_ACTUAL_OWNED_HISTOGRAM',
            final_status='PASS_ACTUAL_OWNED_HISTOGRAM', worker_status='PASS')
    else:
        parser.error('select --preflight, --attempt or --worker')
