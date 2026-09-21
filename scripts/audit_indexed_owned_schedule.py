"""Singleton plan elimination and owned reference/AMP schedule audits."""
from contextlib import ExitStack
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import ast
import json
import os
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import indexed_amp as amp, projected_amp, phase_deflate, cuda_learner as gpu
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation
from fp_reference.indexed_execution import IndexedReferenceMachine
from fp_reference.encoding import pack
from audit_indexed_source_binding import predict, native
from audit_reference_construction import validate_residency
from audit_cuda_runtime import phase_payload
import audit_indexed_runtime as reference
import audit_indexed_amp as indexed
import audit_phase_writer_binding as runner

PORTS = ((IndexedReferenceMachine, 'prepare_prediction'), (IndexedReferenceMachine, 'execute_prediction'),
         (amp, 'prepare_prediction'), (projected_amp, 'prepare_prediction'),
         (amp, 'execute_prediction'), (amp, 'execute_observation'))
FAULTS = ('retired-producers', 'projected-retired-producers', 'fault-prediction-word',
          'fault-gradient-word', 'fault-operation-word', 'projected-fault-prediction-word')
INTEGRATION = ('profiles', 'projected-profiles', 'large', 'projected-large', 'install',
               'projected-install', 'projected-closure', 'projected-unfunded', 'projected-second-commit')
CASES = FAULTS+tuple('integration-'+name for name in INTEGRATION)


def kernel_audit():
    relative = 'src/reference_compiler/fp_reference/indexed_amp.py'
    old = subprocess.run(('git', 'show', '7fe0471:'+relative), cwd=ROOT,
                         capture_output=True, encoding='utf-8', check=True).stdout
    current = (ROOT/relative).read_text(encoding='utf-8')
    names = ('_Arithmetic', '_prediction_schedule', '_observation_schedule', '_check_execution',
             'check_prediction_execution', 'check_observation_execution', 'check_state', 'check_prediction')
    def bodies(text):
        return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(text).body
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names}
    assert bodies(old) == bodies(current) and len(bodies(current)) == len(names)
    owner = ast.parse((ROOT/'src/reference_compiler/fp_reference/indexed_cuda_prefix.py').read_text())
    called = {node.func.attr for node in ast.walk(owner)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not {'prepare_prediction', 'execute_prediction', 'execute_observation'} & called
    return {'source_anchor': '7fe0471', 'unchanged_arithmetic_and_checker_bodies': list(names),
        'retired_AMP_producer_calls_in_owner_AST': 0}


def finite_elimination():
    checked = accepted = recovered = 0
    for actual, proposal, helper_cost, cap in product(range(4), range(5), range(5), range(13)):
        # Four exact input values; four possible plans plus a raising helper.
        unique = (3*actual+1) % 4
        build, execute = 1+actual, 2
        old_ok = proposal == unique and helper_cost+build+execute <= cap
        new_ok = build+execute <= cap
        checked += 1
        if old_ok:
            accepted += 1
            assert new_ok and (actual, proposal) == (actual, unique)
        if new_ok and not old_ok:
            recovered += 1
        assert build+execute <= helper_cost+build+execute
    return {'finite_input_proposal_cost_cap_cases': checked, 'old_successes_preserved': accepted,
        'additional_legal_successes': recovered,
        'scope': 'exact finite model of singleton proposal elimination; no wall-time or complete Compiler claim'}


def noninjective_plan():
    schema = IndexedRelation(3)
    outputs, plans = [], []
    for sign in (1, -1):
        before = amp.IndexedAmpState(CountState(3, (0, 0, sign), None, 1, 1))
        plan = amp._prepare_prediction(schema, before, schema.rules(), schema.source_row(5), output_cap=65536)
        raw, _ = amp._prediction_schedule(plan, before, amp._Arithmetic(32768))
        plans.append(plan)
        outputs.append(str(amp.single(raw.words[5])))
    assert plans[0] == plans[1] and outputs[0] != outputs[1]
    return {'same_complete_plan': True, 'distinct_native_counts': (1, -1), 'different_RNE_probabilities': outputs,
        'consequence': 'removing a redundant producer does not permit replacing the native input by its plan'}


def cpu():
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError('a retired producer reached an owned reference execution')
    with ExitStack() as stack:
        for obj, name in PORTS:
            stack.enter_context(patch.object(obj, name, forbidden))
        small = reference.small_audit()
        profile = reference.profile_audit()
        closure = reference.closure_audit()
    assert not calls and 'torch' not in sys.modules
    return {'status': 'PASS_INDEXED_OWNED_SCHEDULE_CPU', 'kernel': kernel_audit(),
        'elimination_model': finite_elimination(), 'input_not_quotiented': noninjective_plan(),
        'actual_reference': {'small': small, 'profile': profile, 'closure': closure, 'retired_producer_calls': 0}}


def frames(rt, before, saved):
    after = validate_residency(rt)
    assert tuple(pack(p) for p in before.cuda.phases) == saved
    assert tuple(pack(p) for p in after.cuda.phases[:len(saved)]) == saved
    buffers = dict(after.buffers)
    for phase in after.cuda.phases:
        assert phase_payload(after, buffers[phase.object_id]) == pack(phase)
    return after


def probe(name):
    projected = name.startswith('projected-')
    case = name[len('projected-'):] if projected else name
    rt, schema = indexed.configuration(3, 3, projected=projected, evidence_encoding=phase_deflate.ENCODING_ID)
    calls = []
    def retired(*args, **kwargs):
        calls.append(True)
        raise AssertionError('retired producer received owned data or numerical workspace')
    with ExitStack() as stack:
        if case == 'retired-producers':
            for obj, method in PORTS:
                stack.enter_context(patch.object(obj, method, retired))
        assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        before = validate_residency(rt)
        native_before = pack(before.candidates[0].learner)
        if case == 'fault-gradient-word':
            assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
            before = validate_residency(rt)
        saved = tuple(pack(p) for p in before.cuda.phases)
        if case.startswith('fault-'):
            method = 'add' if case == 'fault-operation-word' else 'stack'
            original = getattr(gpu.CudaArithmetic, method)
            def changed(arithmetic, *args, **kwargs):
                tensor = original(arithmetic, *args, **kwargs)
                if not calls:
                    import torch
                    assert tensor.dtype == torch.float32
                    tensor.view(torch.int32).reshape(-1)[0].bitwise_xor_(1)
                    calls.append(True)
                return tensor
            stack.enter_context(patch.object(gpu.CudaArithmetic, method, changed))
        error = None
        try:
            event = rt.observe(0) if case == 'fault-gradient-word' else predict(rt, schema, (1, 2))
        except Exception as exc:
            event, error = None, type(exc).__name__+': '+str(exc)
        after = frames(rt, before, saved)
        assert pack(before.candidates[0].learner) == pack(after.candidates[0].learner) == native_before
        assert after.cursor == 1 and after.cuda.current == before.cuda.current
        assert after.pending.record.target == (0 if case == 'fault-gradient-word' else None)
        current = dict(after.cuda.current)[after.deployed_id]
        assert next(p.raw_state for p in after.cuda.phases if p.object_id == current).encoded.counts == (0, 0, 1)
        row = {'case': name, 'native_and_physical_predecessors_unchanged': True,
            'earlier_snapshot_and_sealed_metadata_unchanged': True, 'error': error,
            'actual_target_retained': after.pending.record.target, 'checked_full_records': len(after.cuda.phases)}
        if case.startswith('fault-'):
            assert error and event is None and after.halted and calls == [True]
            assert after.cuda.phases[-1].status == 'EXECUTION_FAILED'
            assert case == 'fault-gradient-word' or not after.pending.predictions
            row.update(changed_one_bit_in_one_fresh_output=True, published_advances=0)
        else:
            assert not error and event.status == 'PREDICTED_REFERENCE' and not calls
            expected, _ = native(schema, ((1, 2, 0),), (1, 2))
            assert after.pending.predictions[0][1].probabilities == expected.probabilities
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
            final = frames(rt, before, saved)
            _, legal = native(schema, ((1, 2, 0), (1, 2, 0)), (1, 2))
            assert final.candidates[0].learner.materialize(scalar_cap=1000) == legal
            assert final.cuda.phases[-1].raw_state.encoded == final.candidates[0].learner.encoded
            row.update(retired_producer_calls=0, complete_native_and_AMP_update_matches_literal=True,
                checked_full_records=len(final.cuda.phases))
        return row


def device_worker(case):
    if case in FAULTS:
        return probe(case)
    assert case.startswith('integration-') and case[len('integration-'):] in INTEGRATION
    original = indexed.configuration
    def configured(*args, **kwargs):
        return original(*args, **{**kwargs, 'evidence_encoding': phase_deflate.ENCODING_ID})
    with patch.object(indexed, 'configuration', configured):
        return indexed.worker(case[len('integration-'):])


def preflight():
    assert 'torch' not in sys.modules
    return {'status': 'REGISTERED_SINGLETON_PLAN_ELIMINATION', 'cases': CASES,
        'job_cap': indexed.CAP, 'deadline_ms': 900000,
        'source': 'all execution inputs committed at launch HEAD',
        'trusted_kernel': 'the pre-existing fixed private builders and numerical/RNE implementations',
        'retired_ports': [obj.__name__+'.'+name for obj, name in PORTS],
        'fault_scope': 'one bit in one fresh device output; no old tensor, native metadata or owner mutation',
        'scope': 'fixed indexed schedules, native continuations and declared physical fault checks; no arbitrary Python sandbox or class-optimality claim'}


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
            report.update(status='PASS_ACTUAL_OWNED_INDEXED_SCHEDULE', result=device_worker(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.cpu:
        report = cpu()
        output = args.output or ROOT/'evidence/minimal/FP_INDEXED_OWNED_SCHEDULE_CPU.json'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt, script=__file__, cases=CASES,
            journal_prefix='FP_INDEXED_OWNED_SCHEDULE_CUDA', registration_fn=preflight,
            production_anchor='HEAD', result_status='PASS_ACTUAL_OWNED_INDEXED_SCHEDULE',
            final_status='PASS_ACTUAL_OWNED_INDEXED_SCHEDULE', worker_status='PASS')
    else:
        parser.error('select --cpu, --preflight, --attempt or --worker')
