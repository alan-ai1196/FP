"""Actual paid structural order search, continuation and refusal gate."""
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import query_order, indexed_amp as amp, phase_deflate, cuda_learner as gpu
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from audit_indexed_source_binding import predict, native
from audit_reference_construction import validate_residency
import audit_indexed_amp as indexed
import audit_indexed_owned_schedule as owned
import audit_phase_writer_binding as runner

INTEGRATION = ('profiles', 'projected-profiles', 'large', 'projected-large', 'install',
               'projected-install', 'projected-closure', 'projected-unfunded', 'projected-second-commit')
EXTRA = ('width-recovery', 'projected-width-recovery', 'search-class-refusal', 'search-funding-refusal',
         'scratch-frame', 'projected-scratch-frame', 'missing-order', 'bool-order')
CASES = owned.FAULTS+tuple('integration-'+case for case in INTEGRATION)+EXTRA
A2_CASES = ('search-funding-control', 'search-funding-refusal', 'scratch-frame',
            'projected-scratch-frame', 'missing-order', 'bool-order')
A3_CASES = A2_CASES[1:]
CONTROL_SOURCE = '7f965952a17fd331ea5a8bb262bbdc1ca07084ae'


def preserved(rt, before):
    after = owned.frames(rt, before, tuple(pack(p) for p in before.cuda.phases))
    assert after.cursor == before.cursor and after.candidates == before.candidates
    assert after.cuda.current == before.cuda.current and after.pending.record.target is None
    assert after.pending.record.sources and not after.pending.predictions
    assert after.halted
    phase = after.cuda.phases[-1]
    assert phase.arena_phase is None and phase.output_cells == 0
    return after, phase


def refusal(case):
    n = 17 if case == 'search-class-refusal' else 3
    rt, schema = indexed.configuration(n, 1)
    before = validate_residency(rt)
    original = query_order.search
    entries = []
    def proposed(*args, **kwargs):
        entries.append(True)
        if case == 'search-class-refusal':
            raise AssertionError('out-of-class solver entered')
        result = original(*args, **kwargs)
        return replace(result, order=() if case == 'missing-order' else (False, 1))
    def forbidden(*args, **kwargs):
        raise AssertionError('refused order entered numerical allocation')
    error = None
    with patch.object(query_order, 'search', proposed), patch.object(gpu.CudaArithmetic, '__init__', forbidden):
        try:
            outcome = predict(rt, schema, (0, 1))
        except RuntimeError as exc:
            assert isinstance(exc.__cause__, ContractError)
            outcome, error = None, type(exc).__name__+': '+str(exc)
    after, phase = preserved(rt, before)
    if case == 'search-class-refusal':
        assert outcome.status == phase.status == 'UNRESOLVED' and not entries and error is None
        assert 'free-vertex class' in phase.reason
    else:
        assert outcome is None and error and phase.status == 'EXECUTION_FAILED' and entries == [True]
    return {'case': case, 'phase_status': phase.status, 'reason': phase.reason,
        'solver_entries': len(entries), 'numerical_entries': 0, 'published_advances': 0,
        'full_retained_count_coordinates': len(after.candidates[0].learner.encoded.counts),
        'target_revealed': False, 'checked_full_records': len(after.cuda.phases),
        'native_and_physical_predecessors_unchanged': True}


def funding_control():
    seed, schema = indexed.configuration(3, 1)
    original = query_order.search
    charged = []
    def paid(n, support, query, join, live, workspace, **kwargs):
        snapshot = seed.snapshot()
        fee = query_order.search_work(n, len(support), query)
        events = [e for e in snapshot.resources['events'] if 'query-order-search' in e[-1]]
        assert events and dict(events[-1][4])['work'] == fee
        charged.append((snapshot.resources['spent']['deployment']['work'], fee))
        return original(n, support, query, join, live, workspace, **kwargs)
    with patch.object(query_order, 'search', paid):
        assert predict(seed, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    successful = indexed.check_phases(seed)
    assert len(charged) == 1
    return {'case': 'search-funding-control', 'funded_control': successful,
        'prior_deployment_debit': charged[0][0], 'search_fee': charged[0][1],
        'denied_work_cap': charged[0][0]-1, 'query': [0, 1], 'n': 3,
        'scope': 'one fresh CUDA owner; no target revealed'}


def funding():
    # The control lives in a distinct fresh job. Its registered one-unit
    # deficit selects a resource allowance, never a native numerical value.
    journal = json.loads((ROOT/'evidence/minimal/FP_PAID_ORDER_CUDA_A2.json').read_text())
    # Parent preflight binds unchanged production to this terminal control.
    # Do not spawn git inside the two-process Windows execution job.
    assert journal['execution_source'] == CONTROL_SOURCE
    assert journal['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' and len(journal['workers']) == 2
    row = journal['workers'][0]
    assert row['case'] == 'search-funding-control' and row['worker_status'] == 'PASS'
    job = row['completed_job']
    assert job['exit_code'] == 0 and not job['timed_out'] and not job['limit_terminated_processes']
    assert job['attached_before_resume'] and job['peak_job_commit'] <= indexed.CAP
    assert row['result']['process_id'] == job['process_id']
    control = row['result']['result']
    cap, fee = control['denied_work_cap'], control['search_fee']
    assert control['query'] == [0, 1] and control['n'] == 3
    assert cap == control['prior_deployment_debit']-1 and fee == query_order.search_work(3, 0, (0, 1))
    fixture = indexed.fixture
    def narrow(*args, **kwargs):
        cfg, relation, online = fixture(*args, **kwargs)
        return replace(cfg, limits=replace(cfg.limits, role_cumulative={
            'deployment': {'work': cap}, 'compiler': {'work': 10**14}})), relation, online
    with patch.object(indexed, 'fixture', narrow):
        denied, relation = indexed.configuration(3, 1)
    before = validate_residency(denied)
    def forbidden(*args, **kwargs):
        raise AssertionError('unfunded structural or numerical kernel entered')
    with patch.object(query_order, 'search', forbidden) as search, \
            patch.object(gpu.CudaArithmetic, '__init__', forbidden) as numerical:
        result = predict(denied, relation, (0, 1))
    after, phase = preserved(denied, before)
    assert result.status == phase.status == 'UNRESOLVED' and not search.called and not numerical.called
    assert after.resources['spent']['deployment']['work'] == cap+1-fee
    old = {k: b for k, b in before.buffers if 'query-order-storage' in k}
    assert old == {k: b for k, b in after.buffers if 'query-order-storage' in k}
    return {'case': 'search-funding-refusal', 'funded_control_process_id': job['process_id'],
        'prior_deployment_debit': cap+1, 'search_fee': fee, 'denied_work_cap': cap,
        'unfunded_solver_entries': 0, 'unfunded_numerical_entries': 0,
        'phase_status': phase.status, 'reason': phase.reason,
        'old_state_and_scratch_unchanged': True, 'target_revealed': False,
        'checked_full_records': len(after.cuda.phases)}


def scratch(projected):
    rt, schema = indexed.configuration(3, 3, projected=projected)
    indexed.step(rt, schema, (0, 1, 0))
    before = validate_residency(rt)
    old = dict(before.buffers)
    original = query_order.search
    retained, blocked = [], []
    def attempt(backing, label):
        try:
            backing.extend(b'x')
        except BufferError:
            blocked.append(label)
        else:
            raise AssertionError('unpaid scratch resize succeeded')
    def borrowed(n, support, query, join, live, workspace, **kwargs):
        assert type(workspace) is memoryview
        backing = workspace.obj
        attempt(retained[0] if retained else backing, 'DURING_CALL')
        result = original(n, support, query, join, live, workspace, **kwargs)
        retained.append(backing)
        workspace[-1] = len(retained)
        workspace.release()
        attempt(backing, 'AFTER_VIEW_RELEASE')
        return result
    history = ((0, 1, 0),)
    with patch.object(query_order, 'search', borrowed):
        for k in range(2):
            assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            expected, _ = native(schema, history, (0, 1))
            assert rt.snapshot().pending.predictions[0][1].materialize(scalar_cap=1000) == expected
            attempt(retained[0], 'BETWEEN_CALLS')
            if k == 0:
                assert rt.observe(0).status == 'OBSERVED_REFERENCE'
                history += ((0, 1, 0),)
    after = owned.frames(rt, before, tuple(pack(p) for p in before.cuda.phases))
    assert dict(before.buffers) == old and all(type(b) is bytes for _, b in after.buffers)
    key, data = next((k, b) for k, b in after.buffers if 'query-order-storage' in k)
    assert len(data) == after.resources['objects'][key]['residency']['reference_payload_bytes'] == 48
    assert data != old[key] and len(retained) == 4 and len(blocked) == 10
    assert after.cursor == 2 and after.pending.record.target is None
    return {**indexed.check_phases(rt, projected=projected), 'blocked_resize_attempts': len(blocked),
        'solver_calls': len(retained), 'charged_and_actual_scratch_bytes': 48,
        'old_snapshots_and_native_history_unchanged': True,
        'helper_release_and_between_call_handles_cannot_resize': True}


def width(projected):
    rt, schema = indexed.configuration(16, 29, projected=projected)
    for leaf in range(2, 16):
        indexed.step(rt, schema, (0, leaf, 0))
        indexed.step(rt, schema, (1, leaf, 0))
    assert predict(rt, schema, (2, 3)).status == 'PREDICTED_REFERENCE'
    snapshot = validate_residency(rt)
    prediction = snapshot.pending.predictions[0][1]
    edges = tuple(combinations(range(16), 2))
    assert prediction.before.counts == tuple(int(u in (0, 1) and v >= 2) for u, v in edges)
    total = same = 0
    for world in range(1 << 15):
        def bit(v):
            return (world >> (v-1)) & 1 if v else 0
        weight = 9**sum(bit(u) == bit(v) for u, v in edges if u in (0, 1) and v >= 2)
        total += weight
        if bit(2) == bit(3):
            same += weight
    exact = (1+8*F(same, total))/10
    assert prediction.probabilities[0] == exact and snapshot.cursor == 28
    assert snapshot.pending.record.target is None
    last = snapshot.cuda.phases[-1]
    return {**indexed.check_phases(rt, projected=projected), 'family': 'K(2,14), anchor0',
        'complete_count_coordinates': len(prediction.before.counts), 'exact_world_terms': 32768,
        'exact_forecast': str(exact), 'actual_forecast_word': last.raw_prediction.words[5],
        'final_output_cells': last.output_cells, 'final_orders': last.execution_plan.orders,
        'probability_error': str(last.relation.probability_error),
        'all_search_work_paid': sum(dict(e[4]).get('work', 0) for e in snapshot.resources['events']
                                    if 'query-order-search' in e[-1]),
        'target_revealed': False}


def worker(case):
    original = indexed.configuration
    def configured(*args, **kwargs):
        # The global n256 control deliberately retains its registered natural
        # schedule; the exact searched global class stops at n16.
        return original(*args, **{**kwargs, 'order_search': case != 'integration-large',
            'evidence_encoding': phase_deflate.ENCODING_ID})
    with patch.object(indexed, 'configuration', configured):
        if case in owned.FAULTS:
            return owned.probe(case)
        if case.startswith('integration-'):
            return indexed.worker(case[len('integration-'):])
        if case in ('search-class-refusal', 'missing-order', 'bool-order'):
            return refusal(case)
        if case == 'search-funding-refusal':
            return funding()
        if case == 'search-funding-control':
            return funding_control()
        if case.endswith('scratch-frame'):
            return scratch(case.startswith('projected-'))
        if case.endswith('width-recovery'):
            return width(case.startswith('projected-'))
        raise AssertionError(case)


def preflight():
    assert 'torch' not in sys.modules
    old = json.loads((ROOT/'evidence/minimal/FP_PAID_ORDER_CUDA_A1.json').read_text())
    assert old['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' and len(old['workers']) == 19
    assert tuple(r['case'] for r in old['workers']) == CASES[:19]
    assert all(r['worker_status'] == 'PASS' for r in old['workers'][:18])
    failed = old['workers'][-1]
    assert failed['worker_status'] == 'FAILED'
    assert 'initial CUDA extent model requires the actual default allocator settings' in failed['result']['traceback']
    assert not runner.registration.model.git('diff', old['execution_source'], '--', 'src/reference_compiler')
    for row in old['workers']:
        job = row['completed_job']
        assert job['attached_before_resume'] and not job['timed_out'] and not job['limit_terminated_processes']
        assert job['peak_job_commit'] <= indexed.CAP
    a2 = json.loads((ROOT/'evidence/minimal/FP_PAID_ORDER_CUDA_A2.json').read_text())
    assert a2['execution_source'] == CONTROL_SOURCE and a2['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE'
    assert len(a2['workers']) == 2 and a2['workers'][0]['worker_status'] == 'PASS'
    assert a2['workers'][1]['worker_status'] == 'FAILED'
    assert 'WinError 1816' in a2['workers'][1]['result']['traceback']
    assert not runner.registration.model.git('diff', CONTROL_SOURCE, '--', 'src/reference_compiler')
    return {'status': 'REGISTERED_PAID_QUERY_ORDER_CUDA_A3_CONTINUATION', 'cases': A3_CASES,
        'previous_source': old['execution_source'], 'retained_A1_passes': 18,
        'retained_A1_failure': 'two-owner funding fixture refused default allocator state; no production failure inferred',
        'retained_A2_control': CONTROL_SOURCE,
        'retained_A2_failure': 'refusal fixture tried to spawn git inside the two-process Windows job before CUDA initialization',
        'funding_protocol': 'separate fresh control/refusal jobs; refusal work cap equals prior-debit control minus one',
        'job_cap': indexed.CAP, 'deadline_ms': 900000, 'source': 'all execution inputs committed at launch HEAD',
        'search_class': 'lex(C,N) at most15 free vertices per searched block; no numerical-existence certificate',
        'scratch': '12*2^r actual bytes; owner export outlives separate writable helper views',
        'work_model': query_order.WORK_MODEL,
        'numerics': 'unchanged RNE kernels and 1/100 state, 1/1000 probability tolerances',
        'fixed_control': 'only integration-large uses fixed global n256; projected n256 searches local blocks',
        'scope': 'paid reference/AMP component gate, full native continuations and scoped refusals; no full indexed release or model comparison'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', type=int, choices=(3,))
    parser.add_argument('--worker', choices=A3_CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        assert args.output is not None
        report = {'status': 'FAILED_AUDIT', 'case': args.worker, 'process_id': os.getpid()}
        try:
            report.update(status='PASS_ACTUAL_PAID_QUERY_ORDER', result=worker(args.worker))
        except Exception:
            report['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if report['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.attempt is not None:
        runner.matrix(args.attempt, script=__file__, cases=A3_CASES, journal_prefix='FP_PAID_ORDER_CUDA',
            registration_fn=preflight, production_anchor='HEAD', result_status='PASS_ACTUAL_PAID_QUERY_ORDER',
            final_status='PASS_ACTUAL_PAID_QUERY_ORDER', worker_status='PASS')
    else:
        parser.error('select --preflight, --attempt or --worker')
