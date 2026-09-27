"""Fixed device qualification for owned token reuse; no corpus/model score."""
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.encoding import pack
from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceExceeded
from audit_reference_construction import limits, validate_residency
from audit_shared_token_retention import STORAGE
from audit_token_reporting import report_registration
from audit_token_cuda_owner import cuda_contract
from audit_token_reference_host import measured

CASES = ('reuse-training', 'unsealed-retention')
HOST, ARENA, RESERVED, DEADLINE = 4 << 30, 8192, 2 << 20, 180000


def registration(case):
    if case not in CASES:
        raise ValueError('unknown fixed token reuse case')
    cc, program, online, reporting = report_registration(count=16 if case == CASES[0] else 4, report_count=2)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    cfg = replace(cuda_contract(cc.initializer_pattern), reuse_regions=True,
        storage=CudaStorageContract(ARENA, RESERVED, {r: (ARENA, RESERVED) for r in ('deployment', 'compiler')}))
    return cc, program, online, reporting, cfg


def execute(rt, case):
    targets = (0, 1, 1, 0)*4 if case == CASES[0] else (0, 1)
    old_view = old_generation = None
    for index, target in enumerate(targets):
        result = rt.predict_next(f'train/{index}', encode_context(()))
        assert result.status == 'PREDICTED_REFERENCE', result.reason
        if index == 0:
            forecast = rt._cuda._values[rt._cuda.predicted[rt._deployed_id]]
            old_view = forecast.forecast.values
            old_generation = rt._cuda.arena._generations.require(old_view)
        result = rt.observe(target)
        assert result.status == 'OBSERVED_REFERENCE', result.reason
    before = validate_residency(rt)
    current = rt._cuda.current[rt._deployed_id]
    frozen = rt._cuda.phases[current].raw_state
    if case == CASES[0]:
        assert before.candidates[0].learner.origin.optimizer_steps == 8
        assert rt.begin_report().status == 'REPORTING'
        for index, target in enumerate((0, 1)):
            result = rt.predict_report(f'report/{index}')
            assert result.status == 'PREDICTED_REPORT', result.reason
            snapshot = rt.snapshot()
            row = next(p for p in snapshot.cuda.phases if p.object_id == snapshot.token_report.pending.cuda_prediction)
            original = pack(row)
            try:
                row.relation['stored_sum_lower'] = (0,)
            except TypeError:
                pass
            else:
                raise AssertionError('public normalization relation remained writable')
            assert pack(row) == original
            result = rt.observe_report(target)
            assert result.status == ('SCORED_REPORT' if index == 0 else 'COMPLETE_REPORT'), result.reason
        report = rt.report_result()
        assert report.status == 'COMPLETE_REPORT' and report.physical_mean.lower > 0
        extra = dict(complete_training_units=8, report_events=2, public_snapshot_writes_refused=2,
            native_mean_nats=(str(report.native_mean.lower), str(report.native_mean.upper)),
            physical_mean_nats=(str(report.physical_mean.lower), str(report.physical_mean.upper)))
    else:
        assert rt.predict_next('train/2', encode_context(())).status == 'PREDICTED_REFERENCE'
        with patch.object(rt._reference_archive, 'seal_cuda_frame', side_effect=ResourceExceeded('fixed unsealed-frame control')):
            result = rt.observe(1)
        assert result.status == 'UNRESOLVED'
        failed = rt.snapshot()
        assert failed.halted and failed.observations[-1].target == 1 and failed.cursor == 2
        row = failed.cuda.phases[-1]
        arena = rt._cuda.arena
        assert row.status == 'UNRESOLVED' and row.arena_phase not in arena._sealed
        pins = {g for g in arena._generations._live if arena._regions[arena._generation_regions[g]].phase == row.arena_phase}
        assert pins and pins <= set(arena._pins) and row.arena_phase in arena._headers
        for generation in pins:
            arena.require_initialized(arena._pins[generation])
        extra = dict(complete_training_units=1, report_events=0, revealed_failed_target=1,
            failed_phase_pins=len(pins), unsealed_header_retained=True, no_successor_published=True)
    after = validate_residency(rt)
    assert after.candidates == before.candidates and rt._cuda.current[rt._deployed_id] == current
    assert rt._cuda._values[current].raw() == frozen
    arena = rt._cuda.arena
    assert old_generation not in arena._generations._live
    try:
        arena.require_initialized(old_view)
    except ContractError:
        pass
    else:
        raise AssertionError('a retired actual device view regained numeric authority')
    old_region = arena._regions[arena._generation_regions[old_generation]]
    old_extent_reused = any(r.phase > old_region.phase and r.offset <= old_region.offset
        and r.offset+r.byte_size >= old_region.offset+old_region.byte_size for r in arena._regions)
    if case == CASES[0]:
        assert old_extent_reused
    # The failed prefix need not have overwritten this particular saved view.
    # It must still have actually reused storage elsewhere, and reject it.
    starts = set()
    duplicate_offset = False
    for row in arena._regions:
        duplicate_offset |= row.offset in starts
        starts.add(row.offset)
    assert duplicate_offset
    assert len(arena._header_history) == len(arena._phases)
    rt._cuda.check()
    rows = tuple(rt._cuda.phases.values())
    return dict(training_events=len(targets), retained_phases=len(rows),
        checked_phases=sum(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows),
        checked_array_words=sum(p.forward_operations for p in rows),
        historical_view_refused=True, addresses_reused=True,
        saved_view_extent_reused=old_extent_reused, frozen_current_preserved=True,
        retained_header_records=len(arena._header_history),
        owned_reference_peak=after.resources['peak']['reference_payload_bytes'], **extra)


def worker(case, output):
    contract = HostResourceContract(HOST, {r: HOST for r in ('deployment', 'compiler')})
    host = _WindowsProcessHost(contract)
    start = time.perf_counter()
    result, code = dict(status='RUNNING', case=case, before=measured(host)), 0
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    try:
        import torch
        torch.set_num_threads(1)
        cc, program, online, reporting, cfg = registration(case)
        rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
            cuda=cfg, shared_storage=STORAGE, host=contract)
        outcome = execute(rt, case)
        arena = rt._cuda.arena
        outcome['arena'] = dict(native_allocation_counter=arena._counter,
            current_allocation_counter=arena._allocation_counter(), **arena._last_usage,
            live_reserved_bytes=arena._live_bytes, peak_live_reserved_bytes=arena._peak_live_bytes,
            cumulative_reserved_bytes=arena._allocated_bytes,
            retired_generations=sum(len(row[1]) for row in arena._retirements))
        result.update(status='PASS_ACTUAL_OWNED_TOKEN_REUSE', outcome=outcome,
            device=asdict(rt._cuda._device.check()))
    except Exception as error:
        code = 2
        result.update(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000],
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-start)
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


def cpu_control():
    """Check the exact proposed worker branches without a device/job claim."""
    from audit_owned_token_reuse import cpu_device
    import torch
    results = {}
    for case in CASES:
        with cpu_device():
            cc, program, online, reporting, cfg = registration(case)
            rt = ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting,
                cuda=cfg, shared_storage=STORAGE)
            results[case] = execute(rt, case)
    assert not torch.cuda.is_initialized()
    return dict(status='PASS_TOKEN_REUSE_WORKER_BRANCHES_CPU',
        scope='same worker branches with CPU tensor/device substitution; no actual CUDA/job authority', cases=results)


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('qualification requires Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--worker', choices=CASES)
    mode.add_argument('--cpu-control', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.cpu_control:
        print(json.dumps(cpu_control(), indent=2))
        raise SystemExit(0)
    if not args.output:
        parser.error('actual worker requires its externally preattached host job and output path')
    raise SystemExit(worker(args.worker, args.output))
