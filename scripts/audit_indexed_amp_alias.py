"""Supplied and retained AMP metadata aliases across owned continuations."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import indexed_amp as amp, phase_deflate
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation
from fp_reference.indexed_execution import IndexedState, IndexedReferenceMachine
from fp_reference.indexed_relation import DecodeAllowance
from fp_reference.float64_bridge import Float64Contract
from fp_reference.encoding import pack
from audit_indexed_source_binding import predict, native
from audit_reference_construction import validate_residency, rejects
from audit_cuda_runtime import phase_payload
import audit_indexed_amp as indexed
import audit_phase_writer_binding as runner

CASES = ('physical-input-counts', 'later-planner-result')


def operations(arithmetic):
    return tuple(('host-RNE32-ingress' if tag == 'constant' else
        'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
        for tag, width, word in arithmetic.trace)


def cpu():
    schema = IndexedRelation(3)
    rules, sources = schema.rules(), schema.source_row(5)
    physical = amp.IndexedAmpState(CountState(3, (0, 0, 1), None, 1, 1))
    reference = IndexedState(CountState(3, (0, 0, 1), None, 1, 1))
    machine = IndexedReferenceMachine(3, DecodeAllowance())
    expected = machine.execute_prediction(machine.prepare_prediction(schema, rules, reference, sources, bit_limit=32768))
    plan = amp.prepare_prediction(schema, physical, rules, sources, output_cap=65536)
    amp.check_prediction_plan(plan, schema, physical, rules, sources, output_cap=65536)
    saved = pack(physical)
    object.__setattr__(physical.encoded, 'counts', (0, 0, -1))
    arithmetic = amp._Arithmetic(32768)
    wrong, _ = amp.execute_prediction(plan, physical, arithmetic)
    amp.check_prediction_plan(plan, schema, physical, rules, sources, output_cap=65536)
    amp.check_prediction_execution(plan, physical, wrong, operations(arithmetic), bit_limit=32768)
    rejects(lambda: amp.check_prediction(expected, wrong, Float64Contract(F(1, 100), F(1, 1000)),
        normalizer_cap=F(10), activation_cap=F(8), bit_limit=32768))
    assert pack(physical) != saved and reference.encoded.counts == (0, 0, 1)

    first = amp.IndexedAmpState(CountState(3, (0, 0, 0), None, 0, 0))
    old = amp.prepare_prediction(schema, first, rules, sources, output_cap=65536)
    original = pack(old)
    amp.check_prediction_plan(old, schema, first, rules, sources, output_cap=65536)
    old_cells = old.output_cells
    later = amp.IndexedAmpState(CountState(3, (0, 0, 1), None, 1, 1))
    object.__setattr__(old, 'output_cells', old_cells-1)
    current = amp.prepare_prediction(schema, later, rules, schema.source_row(1), output_cap=65536)
    amp.check_prediction_plan(current, schema, later, rules, schema.source_row(1), output_cap=65536)
    rejects(lambda: amp.check_prediction_plan(old, schema, first, rules, sources, output_cap=65536))
    assert pack(old) != original
    return {'status': 'AMP_METADATA_ALIAS_COUNTEREXAMPLES',
        'scope': 'passive exact CPU components; not an owned CUDA execution',
        'physical_input': {'native_reference_count': 1, 'mutated_physical_count': -1,
            'required_reference_probability': str(expected.probabilities[0]),
            'actual_RNE_probability': str(amp.single(wrong.words[5])),
            'conditional_plan_and_RNE_checks_pass': True, 'native_bridge_refuses': True,
            'predecessor_already_corrupted': True},
        'later_result': {'earlier_plan_accepted_before_mutation': True,
            'old_output_cells': old_cells, 'changed_old_output_cells': old.output_cells,
            'current_plan_check_passes': True, 'earlier_plan_now_fails_its_original_check': True}}


def probe(case):
    rt, schema = indexed.configuration(3, 2, evidence_encoding=phase_deflate.ENCODING_ID)
    retained = []
    original_prepare = amp.prepare_prediction
    def planner(*args, **kwargs):
        if retained:
            old = retained[0]
            object.__setattr__(old, 'output_cells', old.output_cells-1)
        result = original_prepare(*args, **kwargs)
        retained.append(result)
        return result
    context = patch.object(amp, 'prepare_prediction', planner) if case == 'later-planner-result' else patch.object(amp, 'prepare_prediction', original_prepare)
    with context:
        assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        before = validate_residency(rt)
        native_before = pack(before.candidates[0].learner)
        prior_metadata = tuple(pack(p) for p in before.cuda.phases)
        prior_buffers = dict(before.buffers)
        old_prediction = next(p for p in before.cuda.phases if p.phase.endswith(':predict'))
        old_cells = old_prediction.execution_plan.output_cells
        original_execute = amp.execute_prediction
        calls = []
        def executor(plan, state, arithmetic):
            assert state.encoded.counts == (0, 0, 1)
            object.__setattr__(state.encoded, 'counts', (0, 0, -1))
            calls.append(True)
            return original_execute(plan, state, arithmetic)
        query = (1, 2) if case == 'physical-input-counts' else (0, 1)
        error = None
        with patch.object(amp, 'execute_prediction', executor if case == 'physical-input-counts' else original_execute):
            try:
                event = predict(rt, schema, query)
            except Exception as exc:
                event, error = None, type(exc).__name__+': '+str(exc)
        after = validate_residency(rt)
        assert pack(before.candidates[0].learner) == native_before
        assert pack(after.candidates[0].learner) == native_before
        assert after.cursor == 1 and after.pending.record.target is None
        mismatches = []
        for index, old in enumerate(before.cuda.phases):
            assert phase_payload(after, prior_buffers[old.object_id]) == prior_metadata[index]
            if pack(old) != prior_metadata[index]:
                mismatches.append(old.phase)
        assert len(mismatches) == 1
        phase = after.cuda.phases[-1]
        current_id = dict(after.cuda.current)[after.deployed_id]
        physical = next(p.raw_state for p in after.cuda.phases if p.object_id == current_id)
        row = {'case': case, 'status': 'ACTUAL_AMP_METADATA_ALIAS_COUNTEREXAMPLE',
            'reference_native_predecessor_unchanged': True,
            'earlier_snapshot_AMP_metadata_changed': True,
            'old_sealed_bytes_unchanged': True, 'old_sealed_metadata_mismatches': mismatches,
            'current_phase_status': phase.status, 'error': error,
            'ordinary_cursor': after.cursor, 'target': None}
        if case == 'physical-input-counts':
            assert calls == [True] and error and event is None and after.halted
            assert not after.pending.predictions and phase.status == 'EXECUTION_FAILED'
            assert physical.encoded.counts == (0, 0, -1)
            row['current_physical_predecessor_counts'] = physical.encoded.counts
            row['reference_counts'] = after.candidates[0].learner.encoded.counts
            row['published_new_prediction'] = False
        else:
            assert not error and event.status == 'PREDICTED_REFERENCE' and not after.halted
            assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
            assert old_prediction.status == 'CHECKED_CUDA_PREFIX_PHASE'
            assert old_prediction.output_cells == old_cells
            assert old_prediction.execution_plan.output_cells == old_cells-1
            assert physical.encoded.counts == (0, 0, 1)
            assert after.pending.predictions[0][1].probabilities == (F(1, 2), F(1, 2))
            row.update(published_new_prediction=True, old_phase_output_cells=old_cells,
                old_plan_output_cells=old_cells-1, old_phase_still_marked_checked=True)
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
            final = validate_residency(rt)
            _, legal = native(schema, ((1, 2, 0), (0, 1, 0)), (0, 1))
            assert final.candidates[0].learner.materialize(scalar_cap=1000) == legal
            assert final.cuda.phases[-1].raw_state.encoded.counts == (1, 0, 1)
            row['complete_native_and_AMP_update_still_correct'] = True
            row['cursor_after_actual_target'] = 2
        return row


def preflight():
    assert 'torch' not in sys.modules
    return {'status': 'REGISTERED_BEFORE_ACTUAL_AMP_METADATA_ALIAS_PROBES',
        'cases': CASES, 'production_anchor': '7fe0471', 'job_cap': indexed.CAP, 'deadline_ms': 900000,
        'physical_input_hypothesis': 'bridge refuses but physical predecessor and old snapshot/phase metadata already changed',
        'later_result_hypothesis': 'a later planner mutates its own retained output; new execution passes while old checked phase no longer matches its sealed bytes',
        'fault_scope': 'supplied count argument or retained returned plan only; no owner globals, stack, tensor writes or codec changes'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        report = {'status': 'FAILED_AUDIT', 'case': args.worker, 'process_id': os.getpid()}
        try:
            report.update(status='ACTUAL_AMP_METADATA_ALIAS_COUNTEREXAMPLE', result=probe(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.cpu:
        report = cpu()
        assert 'torch' not in sys.modules
        output = args.output or ROOT/'evidence/minimal/FP_INDEXED_AMP_ALIAS_CPU.json'
        assert not output.exists(), 'retain the original passive evidence'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt, script=__file__, cases=CASES,
            journal_prefix='FP_INDEXED_AMP_ALIAS_CUDA', registration_fn=preflight,
            production_anchor='7fe0471', result_status='ACTUAL_AMP_METADATA_ALIAS_COUNTEREXAMPLE',
            final_status='FALSIFIED_AMP_METADATA_CONTINUATION_BINDING')
    else:
        parser.error('select --cpu, --preflight, --attempt or --worker')
