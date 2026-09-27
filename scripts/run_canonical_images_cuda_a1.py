"""Fixed two-target CUDA comparison of uncached/owned-image retention.

No full unit, model score or replay of an earlier worker. Both modes use the
same existing full-V model and all original numerical/storage limits. This
new finite comparison follows the completed paired CPU preservation/profile.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
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
CASES = ('uncached', 'owned-images')
HOST, DEADLINE, ARENA, PAYLOAD = 16 << 30, 180000, 1 << 30, 2 << 30
JOURNAL = ROOT/'evidence/minimal/FP_CANONICAL_IMAGES_CUDA_A1.json'


def worker(case, output):
    from audit_shared_cuda_retention import full_registration
    from audit_token_reference_host import measured
    from audit_reference_construction import validate_residency
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from fp_reference.shared_reference import ROOT_KIND
    from fp_reference.byte_archive import _page, U64
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
        cc, program, online, cfg, storage, _, windows, targets, corpus = full_registration()
        assert (program.definition.output.labels, program.definition.sources.context,
                program.slot_count, program.definition.output.update_unit) == (50257, 512, 603092, 512)
        assert not cfg.reuse_regions  # Isolate this new retention change.
        assert (cfg.storage.arena_bytes, cfg.storage.allocator_reserved_cap) == (ARENA, ARENA)
        assert (cfg.state_atol, cfg.probability_atol) == (F(16), F(1, 10**6))
        assert (cfg.phase_evidence_bytes, cfg.phase_output_cells, cfg.exact_cell_cap) == (64 << 20, 1 << 22, 4096)
        storage = replace(storage, canonical_image_bytes=0 if case == 'uncached' else 64 << 20)
        result['corpus'] = corpus
        rt = timed('initialize', lambda: ReferenceCompilerRuntime(cc, program, online=online,
            cuda=cfg, shared_storage=storage, host=host_contract))
        for i, target in enumerate(targets[:2]):
            outcome = timed(f'predict/{i}', lambda: rt.predict_next(f'train/{i}', encode_context(())))
            assert outcome.status == 'PREDICTED_REFERENCE', outcome.reason
            outcome = timed(f'observe/{i}', lambda: rt.observe(target))
            assert outcome.status == 'OBSERVED_REFERENCE', outcome.reason
        snapshot = validate_residency(rt)
        rows = tuple(rt._cuda.phases.values())
        current = rt._cuda_learner_record(snapshot.candidates[0])
        learner = snapshot.candidates[0].learner
        assert len(rows) == 5 and all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows)
        assert snapshot.cursor == current.raw_state.cursor == 2
        assert learner.unit_count == current.raw_state.unit_count == 2
        assert learner.origin.optimizer_steps == current.raw_state.origin.optimizer_steps == 0
        assert learner.windows == windows[:2] and learner.targets == targets[:2]
        assert tuple(x.window for x in current.raw_state.leaves) == windows[:2]
        assert tuple(x.target for x in current.raw_state.leaves) == targets[:2]
        rt._cuda.check_state(learner, current.raw_state, bit_limit=32768)
        for p in rows:
            assert snapshot.resources['objects'][p.object_id]['kind'] == ROOT_KIND+'owned_cuda_phase_frame'
            ordinal = U64.unpack_from(rt._buffers[p.object_id], 8)[0]
            page = _page(rt._buffers[snapshot.reference_archive.pages[ordinal]])
            assert page.expanded_bytes == cfg.phase_evidence_bytes
        rt._cuda.check()
        arena, images = rt._cuda.arena, rt._reference_archive.images
        if images is not None:
            assert images.find(program.definition.output.base) is not None
        result.update(status='PASS_ACTUAL_CANONICAL_IMAGES_PREFIX',
            outcome=dict(observations=2, checked_phases=5, checked_device_words=sum(p.forward_operations for p in rows),
                cursor=2, pending_count=2, committed_units=0, all_original_records_retained=True,
                vocabulary=50257, context=512, master_coordinates=603092,
                paid_reference_peak=snapshot.resources['peak']['reference_payload_bytes'],
                image_count=0 if images is None else len(images.entries),
                image_bytes=0 if images is None else images.used,
                archive_pages=len(snapshot.reference_archive.pages),
                actual_page_bytes=sum(len(rt._buffers[k]) for k in snapshot.reference_archive.pages),
                arena=dict(native_allocation_counter=arena._counter,
                    current_allocation_counter=arena._allocation_counter(),
                    consumed_bytes=arena._cursor, **arena._last_usage)),
            device=asdict(rt._cuda._device.check()))
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result['after'] = measured(host)
    save()
    return 0 if result['status'] == 'PASS_ACTUAL_CANONICAL_IMAGES_PREFIX' else 2


def accept(row):
    job, result = row['job'], row.get('result', {})
    if job['exit_code'] or job['timed_out'] or result.get('status') != 'PASS_ACTUAL_CANONICAL_IMAGES_PREFIX':
        return False
    assert result['case'] == row['case'] and job['attached_before_resume'] and job['peak_job_commit'] <= HOST
    for label in ('before', 'after'):
        value = result[label]
        assert (value['process_id'], value['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
        assert value['job_commit_peak'] <= job['peak_job_commit']
        assert value['lifetime_process_commit_peak'] <= job['peak_process_commit']
    o, arena = result['outcome'], result['outcome']['arena']
    assert (o['observations'], o['checked_phases'], o['cursor'], o['pending_count'], o['committed_units']) == (2, 5, 2, 2, 0)
    assert o['checked_device_words'] > 0 and o['all_original_records_retained']
    assert (o['vocabulary'], o['context'], o['master_coordinates']) == (50257, 512, 603092)
    assert o['paid_reference_peak'] <= PAYLOAD
    assert (o['image_count'] > 0) == (row['case'] == 'owned-images')
    assert 0 <= o['image_bytes'] <= 64 << 20
    assert arena['native_allocation_counter'] == arena['current_allocation_counter'] == [1, ARENA, 1]
    assert arena['consumed_bytes'] <= ARENA
    assert all(arena[key] == ARENA for key in ('actual_tensor_arena_bytes', 'actual_allocator_reserved_bytes',
        'lifetime_tensor_peak_bytes', 'lifetime_allocator_reserved_peak_bytes'))
    return True


def launch():
    from windows_job_audit_support import run_in_job
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip())
    if ROOT.resolve() != common.parent.resolve():
        raise RuntimeError('launch only from the canonical worktree')
    if JOURNAL.exists():
        raise RuntimeError('existing fixed CUDA comparison: inspect it; never replay')
    for name, status in (
        ('FP_SHARED_CUDA_RETENTION_A2.json', 'COMPLETE_ACTUAL_SHARED_TOKEN_RETENTION_A2'),
        ('FP_TOKEN_REUSE_CUDA_A1.json', 'COMPLETE_ACTUAL_OWNED_TOKEN_REUSE_A1'),
        ('FP_CANONICAL_IMAGE_COST_CPU.json', 'COMPLETE_PAIRED_CPU_CANONICAL_IMAGE_COST')):
        prior = json.loads((ROOT/'evidence/minimal'/name).read_text(encoding='utf-8'))
        if prior['status'] != status or 'active_case' in prior:
            raise RuntimeError('required original execution is not terminal and successful: '+name)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit the inputs and previous results before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=HOST, deadline_ms=DEADLINE,
        arena_bytes=ARENA, reference_payload_cap=PAYLOAD, canonical_image_cap=64 << 20,
        observed_events=2, update_unit=512, phase_evidence_bytes=64 << 20, phase_output_cells=1 << 22,
        state_atol='16', probability_atol='1/1000000', exact_cell_cap=4096,
        whole_board_VRAM_upper=24 << 30, results=[], scope=__doc__.strip())
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for case in CASES:
            journal['active_case'] = case
            publish()
            with tempfile.TemporaryDirectory(prefix='fp-canonical-images-cuda-') as temporary:
                output = Path(temporary)/'result.json'
                start = time.perf_counter()
                job = run_in_job(Path(__file__), ('--worker', case, '--output', output),
                    commit_limit=HOST, timeout_ms=DEADLINE)
                row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-start)
                if output.exists():
                    with output.open('rb') as stream:
                        data = stream.read(65537)
                    try:
                        if len(data) > 65536:
                            raise ValueError('bounded result extent exceeded')
                        row['result'] = json.loads(data)
                    except (ValueError, UnicodeError) as error:
                        row['result_read_error'] = type(error).__name__+': '+str(error)
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
            assert len({r['result']['outcome']['checked_device_words'] for r in journal['results']}) == 1
            journal['status'] = 'COMPLETE_ACTUAL_CANONICAL_IMAGES_A1'
    except Exception as error:
        journal.update(status='LAUNCHER_FAILED', error=type(error).__name__+': '+str(error))
        raise
    finally:
        journal.pop('active_case', None)
        publish()
    return 0 if journal['status'] == 'COMPLETE_ACTUAL_CANONICAL_IMAGES_A1' else 1


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('this fixed comparison requires assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', choices=CASES)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker and not args.output:
        parser.error('worker requires its externally attached job and result path')
    raise SystemExit(worker(args.worker, args.output) if args.worker else launch())
