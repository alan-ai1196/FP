"""Fixed original/copied byte-comparison qualification on the actual device.

Two full-V/unit512 workers differ only in two exact archive comparisons.
Time the original first 16 targets with images/base facts and generation reuse.
Then check an uncached complete phase and refuse a corrupted frame after the
seventeenth original target. No profiler, full unit or language score.
"""
from contextlib import nullcontext
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
CASES, EVENTS = ('original-comparisons', 'copied-comparisons'), 16
HOST, DEADLINE, ARENA = 16 << 30, 240000, 1 << 30
JOURNAL = ROOT/'evidence/minimal/FP_BYTE_COMPARISONS_CUDA_A1.json'


def worker(case, output, previous_path):
    from audit_byte_comparisons import previous, previous_comparisons
    from audit_shared_cuda_retention import full_registration
    from audit_reference_construction import validate_residency
    from audit_token_reference_host import measured
    from fp_reference import ReferenceCompilerRuntime, encoding, byte_archive, shared_reference
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from fp_reference.shared_reference import ROOT_KIND, decoded_buffer
    from fp_reference import token_base_facts as facts
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    result = dict(status='RUNNING', case=case, before=measured(host), stages={})
    def save():
        Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    def timed(label, action):
        start = time.perf_counter()
        value = action()
        result['stages'][label] = time.perf_counter()-start
        save()
        return value
    save()
    try:
        import torch
        torch.set_num_threads(1)
        old = previous(json.loads(Path(previous_path).read_text(encoding='utf-8')))
        with (previous_comparisons(old) if case == 'original-comparisons' else nullcontext()):
            assert (byte_archive.Builder._compare is old[0]) == (case == 'original-comparisons')
            assert (shared_reference._compare_stream is old[1]) == (case == 'original-comparisons')
            cc, program, online, cfg, storage, _, windows, targets, corpus = full_registration()
            assert (program.definition.output.labels, program.definition.sources.context,
                    program.slot_count, program.definition.output.update_unit) == (50257, 512, 603092, 512)
            cfg = replace(cfg, reuse_regions=True)
            assert not cfg.grouped_reads and not cfg.composed_native and not cfg.archive_workspaces
            assert (cfg.storage.arena_bytes, cfg.storage.allocator_reserved_cap) == (ARENA, ARENA)
            assert (cfg.state_atol, cfg.probability_atol) == (F(16), F(1, 10**6))
            assert (cfg.phase_evidence_bytes, cfg.phase_output_cells, cfg.exact_cell_cap) == (64 << 20, 1 << 22, 4096)
            storage = replace(storage, canonical_image_bytes=64 << 20, token_invariant_bytes=4 << 20)
            result['corpus'] = corpus
            rt = timed('initialize', lambda: ReferenceCompilerRuntime(cc, program, online=online,
                cuda=cfg, shared_storage=storage, host=host_contract))
            for i, target in enumerate(targets[:EVENTS]):
                outcome = timed(f'predict/{i}', lambda: rt.predict_next(f'train/{i}', encode_context(())))
                assert outcome.status == 'PREDICTED_REFERENCE', outcome.reason
                outcome = timed(f'observe/{i}', lambda: rt.observe(target))
                assert outcome.status == 'OBSERVED_REFERENCE', outcome.reason
                assert facts._ACTIVE.get() is None
            snapshot = validate_residency(rt)
            rows = tuple(rt._cuda.phases.values())
            learner = snapshot.candidates[0].learner
            assert len(rows) == 33 and all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows)
            assert snapshot.cursor == learner.unit_count == EVENTS and learner.origin.optimizer_steps == 0
            assert learner.windows == windows[:EVENTS] and learner.targets == targets[:EVENTS]
            assert tuple(x.window for x in rows[-1].raw_state.leaves) == windows[:EVENTS]
            assert tuple(x.target for x in rows[-1].raw_state.leaves) == targets[:EVENTS]
            rt._cuda.check_state(learner, rows[-1].raw_state, bit_limit=32768)
            fact = rt._reference_archive.base_facts
            assert fact.source is program.definition.output.base and fact.total == 1 and fact.required_bits == 33
            assert fact.size == 1407321 and snapshot.reference_archive.token_base_facts == fact.snapshot()
            assert rt._buffers[fact.buffer] == encoding.pack((facts.FACT_ID, fact.source, fact.total, fact.required_bits))
            assert rt._data_owner in rt._ledger._refs[fact.buffer]
            assert rt._reference_archive.deployment_owner in rt._ledger._refs[fact.buffer]
            for phase in rows:
                assert snapshot.resources['objects'][phase.object_id]['kind'] == ROOT_KIND+'owned_cuda_phase_frame'
                ordinal = byte_archive.U64.unpack_from(rt._buffers[phase.object_id], 8)[0]
                assert byte_archive._page(rt._buffers[snapshot.reference_archive.pages[ordinal]]).expanded_bytes == cfg.phase_evidence_bytes
            result['positive'] = dict(observations=16, checked_phases=33,
                checked_primitive_words=sum(p.forward_operations for p in rows), cursor=16,
                pending_count=16, committed_units=0, all_original_records_retained=True,
                paid_base_fact_bytes=fact.size, both_fact_roles_checked=True,
                paid_reference_peak=snapshot.resources['peak']['reference_payload_bytes'],
                archive_pages=len(snapshot.reference_archive.pages),
                actual_page_bytes=sum(len(rt._buffers[k]) for k in snapshot.reference_archive.pages))
            # Uncached expected bytes remain independent of both archive indices
            # and the owned-image acceleration used during ordinary execution.
            phase = snapshot.cuda.phases[-1]
            raw = b''.join(decoded_buffer(snapshot, phase.object_id,
                byte_cap=storage.expanded_cap, reference_cap=storage.reference_cap))
            size = int.from_bytes(raw[:8], 'big')
            expected = encoding.pack(phase)
            assert len(raw) == cfg.phase_evidence_bytes
            assert raw[8:8+size] == expected and not any(raw[8+size:])
            result['independent_frame'] = dict(uncached_actual_phase_equal=True,
                actual_phase_bytes=len(expected), complete_frame_bytes=len(raw), all_padding_checked=True)
            del raw, expected

            assert rt.predict_next('train/16', encode_context(())).status == 'PREDICTED_REFERENCE'
            before = rt.snapshot()
            seal, push = shared_reference._SharedReference.seal_cuda_frame, byte_archive.Builder.push
            changed = []
            def corrupt(builder, part):
                if not changed:
                    part = bytes((part[0] ^ 1,))+part[1:]
                    changed.append(1)
                return push(builder, part)
            def corrupt_frame(*args, **kwargs):
                with patch.object(byte_archive.Builder, 'push', corrupt):
                    return seal(*args, **kwargs)
            with patch.object(shared_reference._SharedReference, 'seal_cuda_frame', corrupt_frame):
                try:
                    rt.observe(targets[EVENTS])
                except RuntimeError as error:
                    refusal = type(error).__name__+': '+str(error)
                else:
                    raise AssertionError('corrupt post-target frame was accepted')
            after = validate_residency(rt)
            failed = after.cuda.phases[-1]
            assert changed and after.halted and after.cursor == EVENTS
            assert after.candidates[0].learner == learner
            assert after.observations[-1].target == targets[EVENTS]
            assert after.observations[-1].sources.position == EVENTS
            assert after.cuda.current == before.cuda.current and after.cuda.predicted == before.cuda.predicted
            assert len(after.cuda.phases) == 35 and failed.status == 'EXECUTION_FAILED'
            assert 'shared reference differs from the complete owned record' in failed.reason
            assert rt._cuda.arena._pins
            assert after.resources['objects'][failed.object_id]['kind'] == 'owned_cuda_phase_frame'
            assert type(rt._buffers[failed.object_id]) is bytearray and len(rt._buffers[failed.object_id]) == 64 << 20
            try:
                rt.predict_next('train/17', encode_context(()))
            except Exception:
                pass
            else:
                raise AssertionError('failed archive resumed')
            result['corruption_control'] = dict(original_target_index=16, original_target_retained=True,
                changed_producer_refused=True, independent_reader_mismatch=True,
                old_learner_and_cursor_preserved=True, terminal=True,
                retained_failed_frame_bytes=len(rt._buffers[failed.object_id]),
                unsealed_pins=len(rt._cuda.arena._pins), refusal=refusal)
            rt._cuda.check()
            arena, images = rt._cuda.arena, rt._reference_archive.images
            result.update(status='PASS_ACTUAL_BYTE_COMPARISONS',
                outcome=dict(total_phase_records=35, paid_reference_peak=after.resources['peak']['reference_payload_bytes'],
                    image_count=len(images.entries), image_bytes=images.used,
                    cumulative_arena_bytes=arena._allocated_bytes, peak_live_arena_bytes=arena._peak_live_bytes,
                    arena=dict(native_allocation_counter=arena._counter, current_allocation_counter=arena._allocation_counter(),
                        consumed_bytes=arena._cursor, **arena._last_usage)), device=asdict(rt._cuda._device.check()))
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error), traceback=traceback.format_exc()[-5000:])
    result['after'] = measured(host)
    save()
    return 0 if result['status'] == 'PASS_ACTUAL_BYTE_COMPARISONS' else 2


def accept(row):
    job, r = row['job'], row.get('result', {})
    if job['exit_code'] or job['timed_out'] or r.get('status') != 'PASS_ACTUAL_BYTE_COMPARISONS':
        return False
    assert r['case'] == row['case'] and job['attached_before_resume'] and job['peak_job_commit'] <= HOST
    for mark in ('before', 'after'):
        v = r[mark]
        assert (v['process_id'], v['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
        assert v['job_commit_peak'] <= job['peak_job_commit'] and v['lifetime_process_commit_peak'] <= job['peak_process_commit']
    p, o, c, f = r['positive'], r['outcome'], r['corruption_control'], r['independent_frame']
    assert (p['observations'], p['checked_phases'], p['checked_primitive_words'], p['cursor'],
            p['pending_count'], p['committed_units']) == (16, 33, 4541709, 16, 16, 0)
    assert p['all_original_records_retained'] and p['both_fact_roles_checked'] and p['paid_base_fact_bytes'] == 1407321
    assert f['uncached_actual_phase_equal'] and f['all_padding_checked'] and f['complete_frame_bytes'] == 64 << 20
    assert all(c[k] for k in ('original_target_retained', 'changed_producer_refused',
        'independent_reader_mismatch', 'old_learner_and_cursor_preserved', 'terminal'))
    assert c['original_target_index'] == 16 and c['retained_failed_frame_bytes'] == 64 << 20 and c['unsealed_pins'] > 0
    assert o['total_phase_records'] == 35 and o['paid_reference_peak'] <= 2 << 30
    assert 0 < o['image_bytes'] <= 64 << 20
    a = o['arena']
    assert a['native_allocation_counter'] == a['current_allocation_counter'] == [1, ARENA, 1]
    assert a['consumed_bytes'] <= ARENA
    assert all(a[k] == ARENA for k in ('actual_tensor_arena_bytes', 'actual_allocator_reserved_bytes',
        'lifetime_tensor_peak_bytes', 'lifetime_allocator_reserved_peak_bytes'))
    return True


def launch():
    from windows_job_audit_support import run_in_job
    from audit_byte_comparisons import PREVIOUS, previous_sources
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip())
    if ROOT.resolve() != common.parent.resolve() or JOURNAL.exists():
        raise RuntimeError('canonical worktree and absent journal required; never replay')
    for name, status in (('FP_BYTE_COMPARISONS_CPU.json', 'PASS_BOUNDED_BYTE_COMPARISONS_CPU'),
                         ('FP_CANONICAL_EXTENTS_CUDA_A1.json', 'COMPLETE_ACTUAL_CANONICAL_EXTENTS_A1')):
        if json.loads((ROOT/'evidence/minimal'/name).read_text(encoding='utf-8'))['status'] != status:
            raise RuntimeError('required original result is not terminal and successful: '+name)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit implementation, CPU evidence and registration before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    prior_source = previous_sources()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, previous_comparison_source=PREVIOUS,
        cases=CASES, host_cap=HOST, deadline_ms=DEADLINE, arena_bytes=ARENA, reference_payload_cap=2 << 30,
        canonical_image_cap=64 << 20, token_fact_cap=4 << 20, ordinary_targets=16, fault_target_index=16,
        update_unit=512, phase_evidence_bytes=64 << 20, phase_output_cells=1 << 22, exact_cell_cap=4096,
        state_atol='16', probability_atol='1/1000000', reuse_regions=True,
        grouped_reads=False, composed_native=False, archive_workspaces=False,
        scope=__doc__.strip(), results=[])
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-byte-comparisons-cuda-') as temporary:
            prior = Path(temporary)/'prior_comparisons.json'
            prior.write_text(json.dumps(prior_source), encoding='utf-8')
            for case in CASES:
                journal['active_case'] = case
                publish()
                output = Path(temporary)/(case+'.json')
                start = time.perf_counter()
                job = run_in_job(Path(__file__), ('--worker', case, '--output', output, '--previous-path', prior),
                    commit_limit=HOST, timeout_ms=DEADLINE)
                row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-start)
                if output.exists():
                    with output.open('rb') as stream:
                        data = stream.read(65537)
                    if len(data) > 65536:
                        raise ValueError('bounded result extent exceeded')
                    row['result'] = json.loads(data)
                try:
                    passed = accept(row)
                except Exception as error:
                    passed = False
                    row['acceptance_error'] = type(error).__name__+': '+str(error)
                row['accepted_execution'] = passed
                journal['results'].append(row)
                publish()
                print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
                if not passed:
                    journal['status'] = 'FAILED'
                    break
            else:
                assert len({r['result']['outcome']['cumulative_arena_bytes'] for r in journal['results']}) == 1
                journal['status'] = 'COMPLETE_ACTUAL_BYTE_COMPARISONS_A1'
    except Exception as error:
        journal.update(status='LAUNCHER_FAILED', error=type(error).__name__+': '+str(error))
        raise
    finally:
        journal.pop('active_case', None)
        publish()
    return 0 if journal['status'] == 'COMPLETE_ACTUAL_BYTE_COMPARISONS_A1' else 1


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('byte comparison qualification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', choices=CASES)
    parser.add_argument('--output')
    parser.add_argument('--previous-path')
    args = parser.parse_args()
    if args.worker and (not args.output or not args.previous_path):
        parser.error('worker requires its attached job, output and original code path')
    raise SystemExit(worker(args.worker, args.output, args.previous_path) if args.worker else launch())
