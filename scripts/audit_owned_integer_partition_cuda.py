"""Preregistered actual Runtime gate for owned direct integer partitions."""
from dataclasses import asdict
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
import audit_owned_histogram_cuda as base
import audit_owned_integer_partition as cpu
import audit_owned_packed_histogram_cuda as legacy_packed
import audit_packed_count_histogram as independent
import integer_partition as prototype
from fp_reference import integer_partition_decoder as hist, integer_partition_amp as physical, indexed_amp as amp
from fp_reference.encoding import pack
from fp_reference.indexed_relation import IndexedRelation

BUDGET, fixture = cpu.BUDGET, cpu.fixture
STATUS = 'PASS_ACTUAL_OWNED_INTEGER_PARTITION'
CASES = base.INTEGRATION+base.FAULTS+('old-output', 'target-swap', 'plan-partition',
    'workspace', 'underflow-reversal', 'large', 'band', 'legacy-large', 'legacy-projected-large', 'legacy-gray-profiles', 'legacy-packed-profiles')


def configuration(*args, **kwargs):
    with patch.object(base.indexed, 'fixture', fixture):
        return base.ORIGINAL_CONFIGURATION(*args, **{**kwargs, 'histogram': BUDGET,
            'evidence_encoding': base.phase_deflate.ENCODING_ID})


def check_phases(rt, **unused):
    snapshot = base.validate_residency(rt)
    base.no_device_handles(snapshot)
    assert snapshot.cuda.contract.histogram == BUDGET
    assert snapshot.cuda.contract.forward_id == physical.FORWARD_ID
    buffers = dict(snapshot.buffers)
    words = outputs = half = predictions = maximum_compacted = 0
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record
        frame = buffers[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        assert type(rt._buffers[record.object_id]) is bytes
        assert base.phase_payload(snapshot, frame) == pack(record) and not any(frame[8+size:])
        kind = record.phase.split(':')[-1]
        assert record.raw_state.encoded == record.reference.encoded
        if kind == 'predict':
            raw = record.raw_prediction
            expected_plan = prototype.prepare(raw.before, raw.query)
            expected, trace = prototype.rounded_prediction(expected_plan)
            if raw.before.n <= 16:
                parts = base.oracle(raw.before, raw.query)[1]
            else:
                coefficients = independent.band_oracle(raw.before, raw.query, 2)
                parts = tuple(sum(h*9**k for k, h in row) for row in coefficients)
            assert record.execution_plan.before == record.reference.encoded == raw.before
            assert record.execution_plan.parts == expected_plan.parts == parts
            assert record.execution_plan.shape == expected_plan.shape
            assert raw == expected and record.output_cells == expected_plan.output_cells
            operations = tuple(('host-RNE32-ingress' if tag == 'constant' else
                'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
                for tag, width, word in trace)
            assert record.raw_operations == operations and record.forward_operations == len(trace)
            exact = prototype.reference(expected_plan)
            assert record.reference_prediction.probabilities == exact.probabilities
            maximum_compacted = max(maximum_compacted, record.execution_plan.compacted_cells)
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
    key = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    assert len(rt._buffers[key]) == hist.workspace_bytes(BUDGET, n=snapshot.cuda.contract.n)
    return {'checked_phases': len(snapshot.cuda.phases), 'actual_floating_words': words,
        'output_words_including_copies': outputs, 'actual_half_words': half,
        'independent_partition_and_RNE_prediction_readers': predictions, 'cursor': snapshot.cursor,
        'wide_table_billed_and_actual_bytes': len(rt._buffers[key]), 'maximum_compacted_cells': maximum_compacted,
        'packed_current_bytes': snapshot.resources['current']['reference_payload_bytes'],
        'consumed_arena_bytes': snapshot.cuda.storage['consumed_arena_extent']}


def workspace():
    rt, schema = configuration(3, 3)
    key = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    permanent, original = rt._buffers[key], hist.prepare
    handles, calls, blocked = [], [], []
    def resize(backing):
        try:
            backing.extend(b'x')
        except BufferError:
            blocked.append(True)
        else:
            raise AssertionError('actual wide table scratch grew behind the paid extent')
    def monitored(before, query, budget, borrowed, **kwargs):
        assert borrowed is not permanent and borrowed.obj is permanent.obj
        if handles:
            resize(handles[-1])
        events = rt.snapshot().resources['events']
        if len(calls) % 3:
            charged = [e for e in events if ':cuda:ordinary:predict:' in str(e[-1]) and 'work' in dict(e[4])]
            assert charged and dict(charged[-1][4])['work'] >= physical.forward_work(
                schema.n, budget, rt._cuda.contract.phase_output_cells)
        else:
            charged = [e for e in events if str(e[-1]).endswith(':predict')]
            assert charged and dict(charged[-1][4])['work'] == hist.construction_work(schema.n, budget)
        result = original(before, query, budget, borrowed, **kwargs)
        backing = borrowed.obj
        handles.append(backing)
        borrowed.release()
        resize(backing)
        calls.append(result.compacted_cells)
        return result
    with patch.object(hist, 'prepare', monitored):
        base.indexed.step(rt, schema, (0, 1, 0))
        before = base.validate_residency(rt)
        saved = tuple(pack(p) for p in before.cuda.phases)
        base.indexed.step(rt, schema, (1, 2, 1))
    resize(handles[0])
    after = base.owned.frames(rt, before, saved)
    assert len(calls) == 6 and len(blocked) == 12
    assert after.candidates[0].learner.encoded.counts == (1, 0, -1)
    return {**check_phases(rt), 'prepaid_reference_physical_and_reconstruction_calls': len(calls),
        'blocked_resizes': len(blocked), 'old_history_unchanged': True}


def band():
    desired, query = independent.fixture(32, 'band')
    rt, schema = configuration(32, desired.steps+1)
    for (i, j), d in zip(combinations(range(32), 2), desired.counts):
        for _ in range(abs(d)):
            base.indexed.step(rt, schema, (i, j, int(d < 0)))
    before = rt.snapshot()
    actual = before.candidates[0].learner.encoded
    assert actual == desired
    assert base.predict(rt, schema, query).status == 'PREDICTED_REFERENCE'
    plan = rt.snapshot().cuda.phases[-1].execution_plan
    assert plan.output_cells == 29 and plan.integer_envelope == 336
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    final = rt.snapshot()
    assert final.cursor == desired.steps+1 and final.candidates[0].learner.encoded != desired
    return {**check_phases(rt), 'n': 32, 'constructed_span': desired.steps,
        'complete_count_coordinates': len(actual.counts), 'final_prediction_outputs': plan.output_cells,
        'worlds_not_enumerated': 1 << 31, 'continued_target_one_on_new_edge': True}



def partition_fault():
    rt, schema = configuration(3, 2)
    base.indexed.step(rt, schema, (0, 1, 0))
    before = base.validate_residency(rt)
    original = physical._prediction_schedule
    def changed(plan, state, arithmetic):
        result = original(plan, state, arithmetic)
        # Even a common rescaling with unchanged probability is not the
        # exact integer construction registered in this execution plan.
        object.__setattr__(plan, 'parts', tuple(2*v for v in plan.parts))
        return result
    with patch.object(physical, '_prediction_schedule', changed):
        base.rejects(lambda: base.predict(rt, schema, (0, 1)), RuntimeError)
    after = base.preserved(rt, before)
    assert 'plan differs' in after.cuda.phases[-1].reason
    assert after.pending.record.target is None
    return {'case': 'plan-partition', 'status': 'EXECUTION_FAILED', 'published_advances': 0,
        'reason': after.cuda.phases[-1].reason, 'checked_full_records': len(after.cuda.phases),
        'actual_target_retained': None, 'native_predecessors_and_old_sealed_records_preserved': True}


def worker(case):
    if case == 'legacy-packed-profiles':
        return legacy_packed.worker('profiles')
    if case == 'legacy-gray-profiles':
        return base.worker('profiles')
    if case.startswith('legacy-'):
        return base.worker(case)
    with patch.object(base.indexed, 'configuration', configuration), \
         patch.object(base.indexed, 'check_phases', check_phases), \
         patch.object(base, 'configuration', configuration), \
         patch.object(base, 'check_phases', check_phases), patch.object(base, 'physical', physical):
        if case in base.INTEGRATION or case == 'large':
            return base.indexed.worker(case)
        if case in base.FAULTS:
            return base.owned.probe(case)
        if case in ('old-output', 'target-swap'):
            return base.fault(case)
        if case == 'plan-partition':
            return partition_fault()
        if case == 'workspace':
            return workspace()
        if case == 'underflow-reversal':
            return base.reversal()
        if case == 'band':
            return band()
    raise ValueError(case)


def preflight():
    assert 'torch' not in sys.modules
    evidence = json.loads((ROOT/'evidence/minimal/FP_OWNED_INTEGER_PARTITION_CPU.json').read_text())
    assert evidence['status'] == 'PASS_OWNED_INTEGER_PARTITION_CPU' and evidence['complete_audit']
    return {'status': 'REGISTERED_OWNED_INTEGER_PARTITION_GATE', 'cases': CASES,
        'job_cap': base.indexed.CAP, 'deadline_ms': 900000, 'fresh_owner_per_job': True,
        'budget': asdict(BUDGET), 'workspace_bytes_n3_n32_n256':
            [hist.workspace_bytes(BUDGET, n=n) for n in (3, 32, 256)],
        'reference_machine': hist.MODEL_ID, 'forward_id': physical.FORWARD_ID,
        'arena_bytes': 32 << 20, 'phase_output_cap': 65536, 'phase_frame_bytes': 262144,
        'n256_frame_bytes': 4 << 20, 'evidence_encoding': base.phase_deflate.ENCODING_ID,
        'state_atol': '1/100', 'probability_atol': '1/1000',
        'fault_scope': 'fresh device words, stale output, partition mutation, paid buffer lifetime and actual target; trusted fixed checker',
        'failure_policy': 'stop at first failure; retain every outcome; no silent retry or cap changes',
        'scope': 'paid exact host integer inference and actual half/single readout; owned continuations, n32 learned band and n256 profiles; no model score, GPU sum-product or complete indexed release'}


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
        base.runner.matrix(args.attempt, script=__file__, cases=CASES,
            journal_prefix='FP_OWNED_INTEGER_PARTITION_CUDA', registration_fn=preflight,
            production_anchor='HEAD', result_status=STATUS, final_status=STATUS, worker_status='PASS')
    else:
        parser.error('select --preflight, --attempt or --worker')
