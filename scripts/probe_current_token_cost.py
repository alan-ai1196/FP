"""One bounded CPU diagnostic of the qualified ordinary-token path.

Profile prediction/observation at events 0 and 15 in one complete 16-event
history. Actual Torch CPU tensors replace only the device binding; the owner,
generation arena, numerical checks and retention remain. Both owned base
facts and canonical images are enabled. No CUDA context, model score,
full-unit extrapolation or unprofiled-throughput claim is admitted.
"""
from dataclasses import asdict, replace
from pathlib import Path
from types import CodeType
import argparse
import cProfile
import json
import os
import pstats
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
JOURNAL = ROOT/'evidence/minimal/FP_CURRENT_TOKEN_COST_CPU_A1.json'
HOST, DEADLINE, EVENTS = 8 << 30, 240000, 16
SAMPLES = (0, 15)


def measure(operation):
    from fp_reference.runtime import ReferenceCompilerRuntime
    from fp_reference.shared_reference import _SharedReference
    from fp_reference.token_cuda_prefix import execute
    def key(code):
        return code.co_filename, code.co_firstlineno, code.co_name
    write = next(c for c in ReferenceCompilerRuntime._cuda_execute.__code__.co_consts
                 if type(c) is CodeType and c.co_name == 'write')
    selected = dict(reference_retention=key(_SharedReference.allocate.__code__),
        phase_preparation=key(_SharedReference.prepare_frame.__code__),
        phase_write=key(write), phase_retention=key(_SharedReference.seal_cuda_frame.__code__),
        numerical_execution=key(execute.__code__))
    profiler = cProfile.Profile()
    start = time.perf_counter()
    outcome = profiler.runcall(operation)
    elapsed = time.perf_counter()-start
    stats = pstats.Stats(profiler)
    # Check the recorded caller graph as well as the source-based partition.
    # If any selected subtree can contain another, their sum is inadmissible.
    roots = set(selected.values())
    for root in roots:
        assert root in stats.stats, root
        stack, seen = list(stats.stats[root][4]), {root}
        while stack:
            caller = stack.pop()
            if caller in seen:
                continue
            assert caller not in roots, 'profile subtrees overlap'
            seen.add(caller)
            if caller in stats.stats:
                stack.extend(stats.stats[caller][4])
    def row(item):
        (filename, line, function), (primitive, calls, own, cumulative, _) = item
        try:
            filename = Path(filename).relative_to(ROOT).as_posix()
        except ValueError:
            filename = Path(filename).name
        return dict(function=f'{filename}:{line}:{function}', calls=calls,
            primitive_calls=primitive, self_seconds=own, cumulative_seconds=cumulative)
    partition = {name: row((code, stats.stats[code])) for name, code in selected.items()}
    subtotal = sum(v['cumulative_seconds'] for v in partition.values())
    assert subtotal <= elapsed+0.01
    return outcome, dict(wall_seconds=elapsed, calls=stats.total_calls,
        primitive_calls=stats.prim_calls, disjoint_subtrees=partition,
        selected_seconds=subtotal, unassigned_wall_seconds=max(0, elapsed-subtotal),
        cumulative_top=[row(item) for item in sorted(stats.stats.items(), key=lambda x: x[1][3], reverse=True)[:24]],
        self_top=[row(item) for item in sorted(stats.stats.items(), key=lambda x: x[1][2], reverse=True)[:12]])


def worker(output):
    from audit_shared_cuda_retention import full_registration
    from audit_owned_token_reuse import cpu_device
    from audit_reference_construction import validate_residency
    from audit_token_reference_host import measured
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from fp_reference import token_base_facts as facts
    import torch
    torch.set_num_threads(1)
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    result = dict(status='RUNNING', before=measured(host), profiled={}, unprofiled={})
    def save():
        Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        cc, program, online, cfg, storage, _, windows, targets, corpus = full_registration()
        assert (program.definition.output.labels, program.definition.sources.context,
                program.slot_count, program.definition.output.update_unit) == (50257, 512, 603092, 512)
        cfg = replace(cfg, reuse_regions=True)
        assert not cfg.grouped_reads and not cfg.composed_native and not cfg.archive_workspaces
        storage = replace(storage, canonical_image_bytes=64 << 20, token_invariant_bytes=4 << 20)
        result['corpus'] = corpus
        with cpu_device():
            start = time.perf_counter()
            rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg,
                shared_storage=storage, host=host_contract)
            result['initialize_seconds'] = time.perf_counter()-start
            save()
            for i, target in enumerate(targets[:EVENTS]):
                for kind, operation, status in (
                        ('predict', lambda: rt.predict_next(f'train/{i}', encode_context(())), 'PREDICTED_REFERENCE'),
                        ('observe', lambda: rt.observe(target), 'OBSERVED_REFERENCE')):
                    label = f'{kind}/{i}'
                    if i in SAMPLES:
                        outcome, trace = measure(operation)
                        result['profiled'][label] = trace
                    else:
                        start = time.perf_counter()
                        outcome = operation()
                        result['unprofiled'][label] = time.perf_counter()-start
                    assert outcome.status == status, outcome.reason
                    assert facts._ACTIVE.get() is None
                    save()
            snapshot = validate_residency(rt)
            rows = tuple(rt._cuda.phases.values())
            learner = snapshot.candidates[0].learner
            assert len(rows) == 2*EVENTS+1 and all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows)
            assert snapshot.cursor == learner.unit_count == EVENTS and learner.origin.optimizer_steps == 0
            assert learner.windows == windows[:EVENTS] and learner.targets == targets[:EVENTS]
            assert rt._reference_archive.base_facts.source is program.definition.output.base
            assert rt._reference_archive.base_facts.required_bits == 33
            rt._cuda.check_state(learner, rows[-1].raw_state, bit_limit=32768)
            assert not torch.cuda.is_initialized()
            result.update(status='PASS_CURRENT_TOKEN_COST_CPU', cursor=snapshot.cursor,
                pending_count=learner.unit_count, committed_units=learner.origin.optimizer_steps,
                checked_phases=len(rows), checked_primitive_words=sum(p.forward_operations for p in rows),
                paid_reference_peak=snapshot.resources['peak']['reference_payload_bytes'],
                owned_base_fact_bytes=rt._reference_archive.base_facts.size,
                image_bytes=rt._reference_archive.images.used, no_cuda_context=True,
                all_original_records_retained=True)
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result['after'] = measured(host)
    save()
    return 0 if result['status'] == 'PASS_CURRENT_TOKEN_COST_CPU' else 2


def accept(row):
    job, result = row['job'], row.get('result', {})
    if job['exit_code'] or job['timed_out'] or result.get('status') != 'PASS_CURRENT_TOKEN_COST_CPU':
        return False
    assert job['attached_before_resume'] and job['peak_job_commit'] <= HOST
    for mark in ('before', 'after'):
        value = result[mark]
        assert (value['process_id'], value['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
        assert value['job_commit_peak'] <= job['peak_job_commit']
        assert value['lifetime_process_commit_peak'] <= job['peak_process_commit']
    assert (result['cursor'], result['pending_count'], result['committed_units'], result['checked_phases']) == (16, 16, 0, 33)
    assert result['checked_primitive_words'] == 4541709
    assert result['no_cuda_context'] and result['all_original_records_retained']
    assert result['paid_reference_peak'] <= 2 << 30 and result['owned_base_fact_bytes'] == 1407321
    assert 0 < result['image_bytes'] <= 64 << 20
    assert set(result['profiled']) == {f'{op}/{i}' for i in SAMPLES for op in ('predict', 'observe')}
    assert len(result['unprofiled']) == 28
    assert all(len(v['disjoint_subtrees']) == 5 for v in result['profiled'].values())
    return True


def launch():
    from windows_job_audit_support import run_in_job
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=ROOT, text=True).strip())
    if ROOT.resolve() != common.parent.resolve() or JOURNAL.exists():
        raise RuntimeError('canonical worktree and absent journal required; never replay')
    prior = json.loads((ROOT/'evidence/minimal/FP_ARCHIVED_WORKSPACES_CUDA_A1.json').read_text(encoding='utf-8'))
    if prior['status'] != 'COMPLETE_ACTUAL_ARCHIVED_WORKSPACES_A1' or 'active_case' in prior:
        raise RuntimeError('inspect the original terminal workspace comparison first')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit the diagnostic and registration before measurement')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, host_cap=HOST, deadline_ms=DEADLINE,
        observed_events=EVENTS, profiled_events=SAMPLES, arena_bytes=1 << 30,
        reference_payload_cap=2 << 30, canonical_image_cap=64 << 20, token_fact_cap=4 << 20,
        scope=__doc__.strip())
    def publish():
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-current-token-cost-') as temporary:
            output = Path(temporary)/'result.json'
            job = run_in_job(Path(__file__), ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
            journal['job'] = asdict(job)
            if output.exists():
                with output.open('rb') as stream:
                    data = stream.read(131073)
                if len(data) > 131072:
                    raise ValueError('bounded diagnostic result extent exceeded')
                journal['result'] = json.loads(data)
            passed = accept(journal)
            journal['status'] = 'COMPLETE_CURRENT_TOKEN_COST_CPU_A1' if passed else 'FAILED'
    except Exception as error:
        journal.update(status='LAUNCHER_FAILED', error=type(error).__name__+': '+str(error))
        raise
    finally:
        publish()
    print(journal['status'], flush=True)
    return 0 if journal['status'] == 'COMPLETE_CURRENT_TOKEN_COST_CPU_A1' else 1


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('cost diagnostic requires assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker and not args.output:
        parser.error('worker requires its attached job and result path')
    raise SystemExit(worker(args.output) if args.worker else launch())
