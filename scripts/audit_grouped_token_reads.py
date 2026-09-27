"""Exact layout and complete CPU-tensor Runtime checks for fresh read grouping.

No CUDA context, corpus, speed claim or new semantic/numerical action.
"""
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

import torch
import audit_owned_token_reuse as control
from fp_reference import readback_groups as groups
from fp_reference.core import ContractError
from fp_reference.cuda_storage import CudaStorageContract, CudaWorkspace, CudaStorageUnresolved
from fp_reference.resources import ResourceExceeded
from fp_reference.ingress import encode_context


def layout_control():
    cases = refusals = 0
    rows = tuple(product(range(4), repeat=2))
    for length in range(4):
        for layout in product(rows, repeat=length):
            for capacity in (1, 2, 3):
                if any(size > capacity for _, size in layout):
                    control.reject(lambda: groups.plan(layout, capacity), CudaStorageUnresolved)
                    refusals += 1
                    continue
                result = groups.plan(layout, capacity)
                named = [i for _, _, members in result for i in members]
                assert sorted(named) == [i for i, (_, size) in enumerate(layout) if size]
                for first, end, members in result:
                    assert 0 < end-first <= capacity
                    assert all(first <= layout[i][0] and layout[i][0]+layout[i][1] <= end for i in members)
                transport = sum(end-first for first, end, _ in result)
                extent = max((offset+size for offset, size in layout), default=0)
                assert transport <= extent+sum(size for _, size in layout)
                ordered = sorted((offset, offset+size, i) for i, (offset, size) in enumerate(layout) if size)
                # Independent finite DP over every possible ordered cut.
                dp = [0]+[len(ordered)+1]*len(ordered)
                for stop in range(1, len(ordered)+1):
                    for start in range(stop):
                        if max(high for _, high, _ in ordered[start:stop])-ordered[start][0] <= capacity:
                            dp[stop] = min(dp[stop], 1+dp[start])
                assert len(result) == dp[-1]
                cases += 1
    for layout, capacity in (([], 4), (((True, 1),), 4), (((0, -1),), 4), (((0,),), 4), ((), 0)):
        control.reject(lambda: groups.plan(layout, capacity))
    return dict(valid_layouts=cases, capacity_refusals=refusals, malformed_refusals=5,
                coverage_capacity_transport_bound_and_ordered_optimality=True)


def transport_control():
    cfg = CudaStorageContract(4096, 2 << 20, {r: (4096, 2 << 20) for r in ('compiler', 'deployment')})
    comparisons = 0
    for reuse in (False, True):
        arena = control.cpu_arena(cfg, reuse)
        with arena.phase('raw-control') as ws:
            a = ws.empty((4,), torch.float16, 'a')
            hole = ws.empty((17,), torch.float32, 'opaque-uninitialized-gap')
            b = ws.empty((4,), torch.float32, 'b')
            c = ws.empty((2,), torch.int64, 'c')
            empty = ws.empty((0,), torch.float16, 'empty')
            arena._storage.copy_(torch.arange(4096, dtype=torch.int64).to(torch.uint8))
            for value in (a, b, c, empty):
                ws.written(value)
            alias = a[1:3]
            if reuse:
                arena.derive(a, alias)
            values = (b, alias, a, c, empty, a)
            for capacity in (16, 32, 128, 512):
                buffer = bytearray(capacity)
                expected = ws.raw_bytes(values, buffer)
                assert ws.grouped_raw_bytes(values, buffer) == expected
                assert not any(buffer)
                # Opaque uninitialized gap words may not enter any named result.
                hole.fill_(123.25)
                assert ws.grouped_raw_bytes(values, buffer) == expected and not any(buffer)
                comparisons += 1
            control.reject(lambda: ws.grouped_raw_bytes((hole,), bytearray(128)))
            control.reject(lambda: ws.grouped_raw_bytes((b.clone(),), bytearray(128)))
            control.reject(lambda: ws.grouped_raw_bytes((c,), bytearray(8)), CudaStorageUnresolved)
            before = ws.grouped_raw_bytes(values, bytearray(128))
            b.fill_(-0.0)
            after = ws.grouped_raw_bytes(values, bytearray(128))
            assert before[0] != after[0]  # No cross-call host memoization.
            for failure in (RuntimeError, MemoryError):
                buffer = bytearray(128)
                original = torch.Tensor.copy_
                def partial(value, source, *args, **kwargs):
                    original(value, source, *args, **kwargs)
                    raise failure('transfer completed then refused')
                with patch.object(torch.Tensor, 'copy_', partial):
                    control.reject(lambda: ws.grouped_raw_bytes(values, buffer), failure)
                assert not any(buffer)
        # Failed-phase diagnostics may freshly read after workspace closure.
        assert ws.grouped_raw_bytes(values, bytearray(128)) == after
    with patch.object(CudaWorkspace, 'raw_bytes', CudaWorkspace.grouped_raw_bytes):
        stale = control.actual_overwrite()
    return dict(byte_comparisons=comparisons, stale_generation_control=stale,
        foreign_uninitialized_oversized_views_refuse=True, opaque_gaps_and_failed_transfers_cleared=True,
        repeated_calls_read_changed_words=True, closed_workspace_diagnostics_preserved=True)


def trajectories():
    count = phases = encoded = 0
    metrics = []
    cases = [(word, 2, False) for word in product((0, 1), repeat=4)]
    cases += [((0, 1, 1, 0)*2, 4, False), ((0, 1, 1, 0, 0, 1), 2, True)]
    original_cfg = control.cuda_contract
    scalar, grouped = CudaWorkspace.raw_bytes, CudaWorkspace.grouped_raw_bytes
    for reuse in (False, True):
        for targets, unit, profile in cases:
            results = []
            for enabled in (False, True):
                measured = dict(ordinary_copies=0, grouped_copies=0, transport_bytes=0, requested_bytes=0)
                def registration(*args, **kwargs):
                    return replace(original_cfg(*args, **kwargs), grouped_reads=enabled)
                def raw(ws, values, buffer):
                    result = scalar(ws, values, buffer)
                    measured['ordinary_copies'] += sum(bool(x) for x in result)
                    measured['transport_bytes'] += sum(map(len, result))
                    measured['requested_bytes'] += sum(map(len, result))
                    return result
                def raw_group(ws, values, buffer):
                    result = grouped(ws, values, buffer)
                    layout = tuple((v.storage_offset()*v.element_size(), v.numel()*v.element_size()) for v in values)
                    plan = groups.plan(layout, len(buffer))
                    measured['grouped_copies'] += len(plan)
                    measured['transport_bytes'] += sum(end-first for first, end, _ in plan)
                    measured['requested_bytes'] += sum(map(len, result))
                    return result
                with patch.object(control, 'cuda_contract', registration), \
                        patch.object(CudaWorkspace, 'raw_bytes', raw), \
                        patch.object(CudaWorkspace, 'grouped_raw_bytes', raw_group):
                    result = control.trajectory(targets, reuse=reuse, shared=True, unit=unit, profile=profile)
                results.append((result, measured))
            before, after = results
            assert before[0]['phase_bytes'] == after[0]['phase_bytes']
            assert before[0]['report'] == after[0]['report']
            assert before[0]['peak'] == after[0]['peak'] and before[0]['cumulative'] == after[0]['cumulative']
            assert before[1]['grouped_copies'] == 0 < after[1]['grouped_copies']
            assert sum(after[1][key] for key in ('ordinary_copies', 'grouped_copies')) < before[1]['ordinary_copies']
            assert before[1]['requested_bytes'] == after[1]['requested_bytes']
            count += 1
            phases += after[0]['phases']
            encoded += after[0]['retained_bytes']
            metrics.append((before[1], after[1]))
    totals = [{key: sum(pair[i][key] for pair in metrics) for key in metrics[0][0]} for i in (0, 1)]
    return dict(paired_histories=count, identical_complete_phases=phases, identical_phase_body_bytes=encoded,
        identical_native_and_physical_reports=True, unchanged_physical_allocation_extents=True,
        ungrouped_transport=totals[0], grouped_transport=totals[1])


def failures():
    # Actual post-target owner behavior: no unpaid readback, no successor on
    # transport refusal, and a complete failed/unsealed physical phase stays.
    original_cfg = control.cuda_contract
    outcomes = []
    for mode in ('unpaid', 'transport', 'memory', 'changed-leaf'):
        def registration(*args, **kwargs):
            return replace(original_cfg(*args, **kwargs), grouped_reads=True)
        with control.cpu_device(), patch.object(control, 'cuda_contract', registration):
            rt, _ = control.setup(reuse=True, shared=True, unit=4, count=4)
            for i in range(2):
                assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                assert rt.observe(i).status == 'OBSERVED_REFERENCE'
            before = rt.snapshot()
            learner = before.candidates[0].learner
            if mode == 'changed-leaf':
                resident = rt._cuda._values[rt._cuda.current[before.deployed_id]]
                resident.state.leaves[0].values[0, 0] += 1
                control.reject(lambda: rt.predict_next('train/2', encode_context(())), RuntimeError)
                assert rt.snapshot().candidates[0].learner == learner
            else:
                assert rt.predict_next('train/2', encode_context(())).status == 'PREDICTED_REFERENCE'
                old_phase_count = len(rt._cuda.phases)
                if mode == 'unpaid':
                    original = rt._ledger.charge_work
                    def deny(role, debit, **kwargs):
                        if ':cuda:ordinary:observe:' in kwargs.get('note', ''):
                            raise ResourceExceeded('unpaid grouped readback')
                        return original(role, debit, **kwargs)
                    hook = patch.object(rt._ledger, 'charge_work', deny)
                else:
                    error = ResourceExceeded if mode == 'transport' else MemoryError
                    original_group, calls = CudaWorkspace.grouped_raw_bytes, [0]
                    def fail_new_state(ws, values, buffer):
                        payloads = original_group(ws, values, buffer)
                        calls[0] += 1
                        if calls[0] == 2:
                            # First: predecessor. Second: newly executed state.
                            raise error('new-state readback refused after copying')
                        return payloads
                    hook = patch.object(CudaWorkspace, 'grouped_raw_bytes', fail_new_state)
                with hook:
                    if mode == 'memory':
                        control.reject(lambda: rt.observe(1), MemoryError)
                    else:
                        result = rt.observe(1)
                        assert result.status == 'UNRESOLVED', result
                current = rt.snapshot()
                assert current.cursor == 2 and current.candidates[0].learner == learner
                assert current.observations[-1].target == 1 and len(current.observations) == 3
                if mode == 'unpaid':
                    assert len(rt._cuda.phases) == old_phase_count
                else:
                    assert calls[0] >= 2 and rt._cuda.arena._pins
                    if mode == 'transport':
                        assert len(rt._cuda.phases) == old_phase_count+1
                        failed = tuple(rt._cuda.phases.values())[-1]
                        assert failed.status == 'UNRESOLVED' and failed.raw_state.unit_count == 3
                        assert failed.arena_phase not in rt._cuda.arena._sealed
            outcomes.append(mode)
    return outcomes


def tariff_control():
    from audit_token_reference_host import text_model_fixture
    d, _ = text_model_fixture()
    n, context, arena = d.output.update_unit, d.sources.context, 1 << 30
    view_bound = 11+7*n+(n*(context+1)+2)*n.bit_length()
    tariff = groups.resident_work(d, arena)
    assert tariff == 16*arena+256*view_bound*(view_bound+1).bit_length()
    original = control.cuda_contract
    paired = []
    for enabled in (False, True):
        with patch.object(control, 'cuda_contract', lambda *a, **kw: replace(original(*a, **kw), grouped_reads=enabled)):
            paired.append(control.trajectory((0, 1, 1, 0), reuse=True, shared=True))
    assert paired[0]['phase_bytes'] == paired[1]['phase_bytes'] and paired[0]['report'] == paired[1]['report']
    with control.cpu_device(), patch.object(control, 'cuda_contract',
            lambda *a, **kw: replace(original(*a, **kw), grouped_reads=True)):
        rt, _ = control.setup(reuse=True, shared=True, unit=4, count=4)
        assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        value = rt._cuda._values[rt._cuda.current[rt.snapshot().deployed_id]]
        with patch.object(CudaWorkspace, 'grouped_raw_bytes', side_effect=AssertionError('unfunded transport')):
            with patch.object(value.arithmetic, 'capture_view_cap', 6):
                control.reject(value.raw, ResourceExceeded)
            cap = value.arithmetic.capture_view_cap
            excess = replace(value, state=replace(value.state, corrections=value.state.corrections*(cap+1)))
            control.reject(excess.raw, ResourceExceeded)
    return dict(full_V_view_bound=view_bound, full_V_extra_work_per_phase=tariff,
        final_tariff_rechecked_complete_phases=paired[0]['phases'], final_tariff_record_and_report_equality=True,
        oversized_view_table_and_metadata_refused_before_transport=True)


def audit():
    result = dict(layout=layout_control(), transport=transport_control(), runtime=trajectories(),
                  failures=failures(), tariff=tariff_control())
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_GROUPED_FRESH_TOKEN_READS_CPU', scope=__doc__.strip(), **result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_GROUPED_TOKEN_READS_CPU.json').write_text(body, encoding='utf-8')
    print(body)
