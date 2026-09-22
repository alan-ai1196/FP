"""Owned order-search funding, literal continuations and width recovery."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime, query_order, query_projection
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.indexed_execution import IndexedReferenceMachine
from fp_reference.indexed_relation import DecodeAllowance
from fp_reference.semantics import ArithmeticUnresolved
from audit_indexed_source_binding import predict
from audit_reference_construction import validate_residency
import audit_indexed_runtime as reference


def enabled_fixture(*args, **kwargs):
    cfg, schema, online = original_fixture(*args, **kwargs)
    return replace(cfg, indexed_order_search=True), schema, online


original_fixture = reference.fixture


def funding():
    cfg, schema, online = enabled_fixture(3, 2)
    seed = ReferenceCompilerRuntime(cfg, schema, online=online)
    assert predict(seed, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    assert seed.observe(0).status == 'OBSERVED_REFERENCE'
    spent = seed.snapshot().resources['spent']['deployment']['work']
    planning = IndexedReferenceMachine(3, DecodeAllowance()).evaluation_work(schema, cfg.semantics)
    fee = query_order.search_work(2, 1, (0, 1))
    narrow = replace(cfg, limits=replace(cfg.limits, role_cumulative={
        'deployment': {'work': spent+planning+fee-1}, 'compiler': {'work': 10**14}}))
    denied = ReferenceCompilerRuntime(narrow, schema, online=online)
    assert predict(denied, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    assert denied.observe(0).status == 'OBSERVED_REFERENCE'
    before = validate_residency(denied)
    with patch.object(query_order, 'search', side_effect=AssertionError('unfunded DP entered')) as blocked:
        result = predict(denied, schema, (0, 1))
    after = validate_residency(denied)
    assert result.status == 'UNRESOLVED' and not blocked.called
    assert after.candidates == before.candidates and after.cursor == before.cursor == 1
    assert after.pending.record.target is None and not after.pending.predictions
    assert after.resources['spent']['deployment']['work'] == spent+planning
    old_storage = {k: b for k, b in before.buffers if 'query-order-storage' in k}
    assert old_storage == {k: b for k, b in after.buffers if 'query-order-storage' in k}

    original = query_order.search
    observed = []
    def paid(n, support, query, join, live, workspace, **kwargs):
        current = seed.snapshot()
        events = [e for e in current.resources['events'] if 'query-order-search' in e[-1]]
        assert events and dict(events[-1][4])['work'] == query_order.search_work(n, len(support), query)
        key = next(k for k, _ in current.buffers if 'query-order-storage' in k)
        owned = seed._buffers[key]
        assert type(workspace) is memoryview and workspace is not owned
        assert workspace.obj is owned.obj and len(workspace) == len(owned)
        observed.append((n, len(workspace), dict(events[-1][4])['work']))
        return original(n, support, query, join, live, workspace, **kwargs)
    with patch.object(query_order, 'search', paid):
        assert predict(seed, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
    assert observed == [(2, 48, fee)]
    return {'unfunded_solver_entries': 0, 'received_context_retained': True,
        'unrevealed_target_and_old_native_state_preserved': True,
        'paid_before_actual_DP_calls': observed, 'entire_extent_retained_on_refusal': True}


def proposals():
    original = query_order.search
    rows = []
    for case in ('missing-vertex', 'bool-vertex', 'costs-are-not-authority', 'retained-result'):
        cfg, schema, online = enabled_fixture(3, 3)
        rt = ReferenceCompilerRuntime(cfg, schema, online=online)
        models = {rt.snapshot().deployed_id: reference.literal(3)}
        reference.step(rt, schema, (0, 1, 0), models)
        before = validate_residency(rt)
        saved = pack(before.event_traces)
        retained = []
        def altered(*args, **kwargs):
            result = original(*args, **kwargs)
            assert result is not None
            if case == 'missing-vertex':
                return replace(result, order=())
            if case == 'bool-vertex':
                return replace(result, order=(False,))
            if case == 'costs-are-not-authority':
                return replace(result, output_cells=0, tape_nodes=0)
            if retained:
                object.__setattr__(retained[0], 'order', ())
            retained.append(result)
            return result
        with patch.object(query_order, 'search', altered):
            if case in ('missing-vertex', 'bool-vertex'):
                try:
                    predict(rt, schema, (0, 1))
                except ContractError:
                    pass
                else:
                    raise AssertionError('malformed order entered exact tables')
                after = validate_residency(rt)
                assert after.halted and after.candidates == before.candidates
                assert not after.pending.predictions and after.pending.record.target is None
            else:
                reference.step(rt, schema, (0, 1, 0), models)
                first = validate_residency(rt)
                first_saved = pack(first.event_traces)
                reference.step(rt, schema, (0, 1, 1), models)
                assert pack(first.event_traces) == first_saved
                if case == 'retained-result':
                    assert len(retained) == 2 and retained[0].order == ()
        assert pack(before.event_traces) == saved
        rows.append({'case': case, 'old_native_history_unchanged': True,
            'outcome': 'REFUSED' if case in ('missing-vertex', 'bool-vertex') else 'COMPLETE_LITERAL_UPDATES'})
    return rows


def frontier():
    n = 16
    history = tuple(event for leaf in range(2, n) for event in ((0, leaf, 0), (1, leaf, 0)))
    outcomes = []
    final = None
    for enabled in (False, True):
        cfg, schema, online = original_fixture(n, len(history)+1)
        rt = ReferenceCompilerRuntime(replace(cfg, indexed_order_search=enabled), schema, online=online)
        failure = None
        for i, j, y in history:
            result = predict(rt, schema, (i, j))
            if result.status == 'UNRESOLVED':
                failure = result.reason
                break
            assert result.status == 'PREDICTED_REFERENCE'
            assert rt.observe(y).status == 'OBSERVED_REFERENCE'
        if failure is None:
            result = predict(rt, schema, (2, 3))
            if result.status == 'UNRESOLVED':
                failure = result.reason
        snapshot = validate_residency(rt)
        assert snapshot.pending.record.target is None
        outcomes.append({'order_search': enabled, 'completed_events': snapshot.cursor,
            'status': result.status, 'reason': failure,
            'packed_bytes': snapshot.resources['current']['reference_payload_bytes'],
            'search_work_paid': sum(dict(e[4]).get('work', 0) for e in snapshot.resources['events']
                                    if 'query-order-search' in e[-1])})
        if enabled:
            assert failure is None and snapshot.cursor == len(history)
            final = snapshot
        else:
            assert failure and snapshot.cursor <= len(history)
    prediction = final.pending.predictions[0][1]
    counts = prediction.before.counts
    edges = tuple(combinations(range(n), 2))
    assert counts == tuple(int((u in (0, 1)) and v >= 2) for u, v in edges)
    try:
        query_projection.prepare(prediction.before, (2, 3), DecodeAllowance())
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('the fixed natural-order obstruction disappeared')
    total = same = 0
    active = tuple(e for e, d in zip(edges, counts) if d)
    for world in range(1 << (n-1)):
        def bit(v):
            return (world >> (v-1)) & 1 if v else 0
        weight = 9**sum(bit(u) == bit(v) for u, v in active)
        total += weight
        if bit(2) == bit(3):
            same += weight
    expected = (1+8*F(same, total))/10
    assert prediction.probabilities[0] == expected
    return {'family': 'K(2,14), fixed anchor0 and unchanged native learner',
        'matched_owned_runs': outcomes, 'complete_count_coordinates': len(counts),
        'independent_exact_world_terms': 1 << (n-1), 'forecast': str(expected),
        'final_query': (2, 3), 'next_target_revealed': False}


def cpu():
    with patch.object(reference, 'fixture', enabled_fixture):
        complete = {name: fn() for name, fn in (
            ('small', reference.small_audit), ('profile', reference.profile_audit),
            ('large', reference.large_audit), ('closure', reference.closure_audit),
            ('adversaries', reference.adversaries), ('persistence', reference.persistence_audit))}
    return {'status': 'PASS_PAID_QUERY_ORDER_CPU',
        'scope': 'owned reference search, complete native checks and structural recovery; actual AMP gate separate',
        'complete_indexed_reference_regression': complete, 'funding': funding(),
        'proposal_boundary': proposals(), 'width_recovery': frontier()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = cpu()
    if args.write or args.output:
        output = args.output or ROOT/'evidence/minimal/FP_PAID_QUERY_ORDER_CPU.json'
        assert not output.exists(), 'retain each source-bound outcome separately'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
