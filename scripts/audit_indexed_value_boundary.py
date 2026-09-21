"""Value-only indexed reference planning, with exact and actual owned probes."""
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime, indexed_values as values, phase_deflate
from fp_reference.indexed_count import CountState
from fp_reference.indexed_execution import IndexedState, IndexedReferenceMachine
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance
from fp_reference.encoding import pack
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from audit_indexed_source_binding import predict, native
from audit_indexed_runtime import fixture
from audit_reference_construction import validate_residency, rejects
from audit_cuda_runtime import phase_payload
import audit_indexed_amp as indexed
import audit_phase_writer_binding as runner

FAULTS = ('planner-sources', 'planner-counts', 'planner-raises',
         'planner-poison-restore', 'retained-result', 'retired-executor')
INTEGRATION = ('integration-profiles', 'integration-projected-profiles',
               'integration-projected-large', 'integration-projected-install')
CASES = FAULTS+INTEGRATION


def immutable(value):
    return (value is None or type(value) in (str, int, bool)
            or type(value) is tuple and all(immutable(child) for child in value))


def setup(length, cuda):
    if cuda:
        return indexed.configuration(3, length, evidence_encoding=phase_deflate.ENCODING_ID)
    cfg, schema, online = fixture(3, length)
    return ReferenceCompilerRuntime(cfg, schema, online=online), schema


def probe(case, *, cuda=False):
    rt, schema = setup(3, cuda)
    assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    prior = validate_residency(rt)
    native_before = pack(prior.candidates[0].learner)
    phases_before = tuple(pack(p) for p in prior.cuda.phases) if cuda else ()
    query = (0, 1) if case == 'planner-sources' else (1, 2)
    expected, _ = native(schema, ((1, 2, 0),), query)
    honest = IndexedReferenceMachine.prepare_prediction
    calls, retained, port_calls = [], [], []
    real_port = values.reference

    def port(*args, **kwargs):
        assert immutable(args) and all(immutable(v) for v in kwargs.values())
        result = real_port(*args, **kwargs)
        assert immutable(result)
        port_calls.append(True)
        return result

    def altered(machine, program, rules, state, sources, *, bit_limit):
        calls.append(True)
        if case == 'retained-result' and retained:
            old_machine, old_state, old_plan = retained[0]
            object.__setattr__(old_state.encoded, 'counts', (0, 0, -1))
            object.__setattr__(old_plan, 'query', (0, 0))
            object.__setattr__(old_plan.projection, 'blocks', ())
            object.__setattr__(old_machine.budget, 'integer_bits', 1)
        if case == 'planner-sources':
            sources.clear()
            sources.update(program.source_row(5))
        elif case in ('planner-counts', 'planner-raises', 'planner-poison-restore'):
            original = state.encoded.counts
            object.__setattr__(state.encoded, 'counts', (0, 0, -1))
            if case == 'planner-raises':
                raise RuntimeError('registered supplied-input failure after mutation')
        plan = honest(machine, program, rules, state, sources, bit_limit=bit_limit)
        if case == 'planner-poison-restore':
            # This plan has the same geometry under either sign. Restoring
            # its metadata cannot poison the later private exact execution.
            object.__setattr__(state.encoded, 'counts', original)
        if case == 'retained-result':
            retained.append((machine, state, plan))
        return plan

    def retired(*args, **kwargs):
        calls.append(True)
        raise AssertionError('retired numerical delegation must not be reached')

    refused = case in ('planner-sources', 'planner-counts', 'planner-raises')
    method = 'execute_prediction' if case == 'retired-executor' else 'prepare_prediction'
    error = None
    with patch.object(values, 'reference', port), patch.object(IndexedReferenceMachine, method,
            retired if case == 'retired-executor' else altered):
        try:
            result = predict(rt, schema, query)
        except Exception as exc:
            result, error = None, type(exc).__name__+': '+str(exc)
        after = validate_residency(rt)
        assert pack(prior.candidates[0].learner) == native_before
        assert pack(after.candidates[0].learner) == native_before
        assert after.cursor == 1 and after.pending.record.target is None
        assert schema.source_query(schema.rules(), dict(after.pending.record.sources))[0] == query
        assert rt._machine.budget.integer_bits == 32768
        row = {'case': case, 'refused': refused, 'error': error,
            'old_snapshot_unchanged': True, 'native_predecessor_unchanged': True,
            'actual_context_retained': True, 'target_before_decision': None}
        if refused:
            assert error and result is None and after.halted and not after.pending.predictions
            assert len(calls) == 1
            assert not port_calls if case == 'planner-raises' else len(port_calls) == 1
        else:
            assert not error and result.status == 'PREDICTED_REFERENCE'
            assert after.pending.predictions[0][1].probabilities == expected.probabilities
            saved_prediction = pack(after.pending.predictions[0][1])
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
            learned = validate_residency(rt)
            history = ((1, 2, 0), query+(0,))
            _, legal = native(schema, history, query)
            assert learned.candidates[0].learner.materialize(scalar_cap=1000) == legal
            row['complete_native_update_matches_literal'] = True
            if case == 'retained-result':
                assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
                last = validate_residency(rt)
                exact, _ = native(schema, history, (0, 1))
                assert last.pending.predictions[0][1].probabilities == exact.probabilities
                assert pack(after.pending.predictions[0][1]) == saved_prediction
                assert pack(prior.candidates[0].learner) == native_before
                row['prior_accepted_output_unchanged_after_later_helper'] = True
            if case == 'retired-executor':
                assert not calls
                row['retired_executor_calls'] = 0
        row['private_planning_work_paid'] = (after.resources['spent']['deployment']['work']
            - prior.resources['spent']['deployment']['work'])
    final = validate_residency(rt)
    if cuda:
        assert tuple(pack(p) for p in final.cuda.phases[:len(phases_before)]) == phases_before
        buffers = dict(final.buffers)
        for phase in final.cuda.phases:
            assert phase_payload(final, buffers[phase.object_id]) == pack(phase)
        assert all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in final.cuda.phases)
        if refused:
            assert len(final.cuda.phases) == len(prior.cuda.phases)
        row['checked_full_phase_records'] = len(final.cuda.phases)
        row['older_sealed_metadata_unchanged'] = True
    return row


def restored_input_witness():
    schema = IndexedRelation(3)
    machine = IndexedReferenceMachine(3, DecodeAllowance())
    owned = IndexedState(CountState(3, (0, 0, 1), None, 1, 1))
    plan = machine.prepare_prediction(schema, schema.rules(), owned, schema.source_row(5), bit_limit=32768)
    packet = values.freeze(plan, cells=values.reference_cells(3), bits=32768)
    local = values.thaw(packet, cells=values.reference_cells(3), bits=32768)
    object.__setattr__(local.before, 'counts', (0, 0, -1))
    wrong = machine.execute_prediction(local)
    object.__setattr__(local.before, 'counts', (0, 0, 1))
    correct = machine.execute_prediction(plan)
    assert wrong.before == owned.encoded and wrong.query == plan.query
    assert wrong.probabilities != correct.probabilities
    assert values.same(values.freeze(local, cells=values.reference_cells(3), bits=32768), packet)
    return {'scope': 'passive counterexample to copy-plus-after-equality; not the repaired Runtime',
        'metadata_restored': True, 'required_probability': str(correct.probabilities[0]),
        'wrong_probability': str(wrong.probabilities[0]),
        'consequence': 'the owned path removes the replaceable numerical executor'}


def heap_model():
    rows = []
    for input_alias, output_alias in product((False, True), repeat=2):
        trials = accepted = input_failures = history_failures = semantic_failures = 0
        for actual, rewrite, returned, late, target in product(range(4), range(4), range(4), range(4), range(2)):
            owner = {'input': actual}
            supplied = owner if input_alias else dict(owner)
            supplied['input'] = rewrite
            proposal = {'input': returned}
            trials += 1
            input_failures += owner['input'] != actual
            if proposal['input'] != owner['input']:
                continue
            accepted += 1
            # Fixed kernel, two-bit full input and an actual binary target.
            forecast = (owner['input'] >> 1) ^ (owner['input'] & 1)
            expected = (actual >> 1) ^ (actual & 1)
            successor = (owner['input'], target)
            semantic_failures += forecast != expected or successor != (actual, target)
            record = proposal if output_alias else dict(proposal)
            saved = record['input']
            proposal['input'] = late
            history_failures += record['input'] != saved
        if not input_alias and not output_alias:
            assert input_failures == history_failures == semantic_failures == 0
        else:
            assert input_failures or history_failures
        rows.append({'shared_input': input_alias, 'shared_output': output_alias, 'trials': trials,
            'accepted': accepted, 'input_failures': input_failures,
            'history_failures': history_failures, 'semantic_failures': semantic_failures})
    return rows


def value_audit():
    count = 0
    for n in range(2, 5):
        for signs in product((-1, 0, 1), repeat=n*(n-1)//2):
            steps = sum(map(abs, signs))
            state = CountState(n, signs, None, steps, steps)
            packet = values.freeze(state, cells=values.reference_cells(n), bits=32768)
            assert immutable(packet)
            restored = values.thaw(packet, cells=values.reference_cells(n), bits=32768)
            assert restored == state and restored is not state
            object.__setattr__(restored, 'cursor', steps+1)
            assert state.cursor == steps
            count += 1
    malformed = ([], {}, object(), ('record', 'Foreign', ()), ('fraction', 1, 0),
                 ('fraction', 2, 4), ('tuple', []), ('record', 'CountState', (3,)))
    for item in malformed:
        rejects(lambda: values.thaw(item, cells=100, bits=24), (ContractError, ResourceExceeded, TypeError))
    deep = None
    for _ in range(18):
        deep = ('tuple', (deep,))
    rejects(lambda: values.thaw(deep, cells=100, bits=24), ResourceExceeded)
    rejects(lambda: values.thaw(('tuple', tuple(range(101))), cells=100, bits=24), ResourceExceeded)
    rejects(lambda: values.freeze(1 << 63, cells=100, bits=24), ResourceExceeded)
    assert not values.same(False, 0) and not values.same(True, 1)
    # Rationals are unnecessary for metadata proposals. Excluding them avoids
    # any reliance on copying their mutable Python internals.
    rejects(lambda: values.freeze(F(3, 7), cells=10, bits=24), ContractError)
    return {'ternary_states': count, 'malformed_or_unfunded_values_refused': len(malformed)+4,
        'native_records_detached': True, 'rational_objects_cannot_cross': True,
        'exact_primitive_types_checked': True}


def funding():
    cfg, schema, online = fixture(3, 1)
    cfg = replace(cfg, limits=replace(cfg.limits, role_cumulative={
        'deployment': {'work': 10000}, 'compiler': {'work': 10**14}}))
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    with patch.object(values, 'reference', side_effect=AssertionError('unfunded helper entered')) as helper:
        result = predict(rt, schema, (0, 1))
    assert result.status == 'UNRESOLVED' and not helper.called
    state = validate_residency(rt)
    assert state.cursor == 0 and state.pending.record.target is None and not state.pending.predictions
    return {'unfunded_helper_calls': 0, 'received_context_retained': True, 'status': result.status}


def larger_declared_limit():
    cfg, schema, online = fixture(3, 1)
    rt = ReferenceCompilerRuntime(replace(cfg, reference_integer_bits=65536), schema, online=online)
    assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    assert rt.snapshot().pending.predictions[0][1].probabilities == (F(1, 2), F(1, 2))
    return {'nominal_reference_bits': 65536, 'decoder_bits': 32768, 'forecast': '1/2'}


def preflight():
    assert 'torch' not in sys.modules
    return {'status': 'REGISTERED_INDEXED_VALUE_BOUNDARY', 'cases': CASES,
        'job_cap': indexed.CAP, 'deadline_ms': 900000,
        'source': 'all execution dependencies committed at launch HEAD',
        'hypotheses': 'input faults refuse before AMP; harmless/restored proposals execute the actual input; retained aliases cannot change old records',
        'scope': 'reference prediction delegation only; no complete Runtime or other-helper release'}


def device_worker(case):
    if case in FAULTS:
        return probe(case, cuda=True)
    assert case in INTEGRATION
    original = indexed.configuration
    def configured(*args, **kwargs):
        return original(*args, **{**kwargs, 'evidence_encoding': phase_deflate.ENCODING_ID})
    with patch.object(indexed, 'configuration', configured):
        return indexed.worker(case[len('integration-'):])


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
            report.update(status='PASS_ACTUAL_INDEXED_VALUE_BOUNDARY', result=device_worker(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.cpu:
        report = {'status': 'PASS_INDEXED_VALUE_BOUNDARY_CPU', 'scope': preflight()['scope'],
            'copy_restore_counterexample': restored_input_witness(), 'heap_model': heap_model(),
            'closed_values': value_audit(), 'funding': funding(), 'larger_nominal_limit': larger_declared_limit(),
            'runtime': [probe(case) for case in FAULTS]}
        assert 'torch' not in sys.modules
        output = args.output or ROOT/'evidence/minimal/FP_INDEXED_VALUE_BOUNDARY_CPU.json'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt, script=__file__, cases=CASES,
            journal_prefix='FP_INDEXED_VALUE_BOUNDARY_CUDA', registration_fn=preflight,
            production_anchor='HEAD', result_status='PASS_ACTUAL_INDEXED_VALUE_BOUNDARY',
            final_status='PASS_ACTUAL_INDEXED_VALUE_BOUNDARY', worker_status='PASS')
    else:
        parser.error('select --cpu, --preflight, --attempt or --worker')
