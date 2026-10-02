"""One complete owned value-graph AMP control; no corpus or performance comparison."""
from dataclasses import asdict, replace
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
from run_public_value_cuda_a1 import exercise, publish, HOST, DEADLINE, ARENA
from audit_public_value_regression import git

JOURNAL = ROOT/'evidence/minimal/FP_OWNED_VALUE_GRAPH_CUDA_A1.json'
HARNESS = ROOT/'evidence/minimal/FP_OWNED_VALUE_GRAPH_DEVICE_HARNESS_CPU.json'
NODES, MEMO, BASE = 1 << 22, 32, 1 << 20


def control(*, cuda):
    import audit_token_reporting as fixture
    from audit_owned_value_graph_runtime import observed
    from fp_reference import value_graph as graph
    from fp_reference.value_graph_reference import _ValueGraphReference
    cfg = replace(fixture.STORAGE, encoding=graph.ENCODING_ID,
        expression_nodes=NODES, expression_bindings=MEMO, token_invariant_bytes=BASE)
    with patch.object(fixture, 'STORAGE', cfg), observed() as counts:
        result, rt = exercise('shared', cuda=cuda)
    owner = rt._reference_archive
    assert type(owner) is _ValueGraphReference and owner.contract.encoding == graph.ENCODING_ID
    assert owner.encoder.index.raw == owner.reader.index.raw
    assert all(raw == rt._buffers[identity] for raw, identity in zip(owner.reader.pages, owner.pages))
    assert len(owner.reader.pages) == len(owner.pages) == owner.encoder.ordinal
    assert counts['native_records'] > 0 and counts['facts_evicted'] > 0
    assert counts['memo_peak'] <= MEMO and len(owner.bindings) <= MEMO
    assert all(len(owner.reader.index.raw[root]) > 0 for _, root in owner.bindings.values())
    assert owner.base_facts is not None
    result['owned_value_graph'] = dict(encoding=graph.ENCODING_ID, node_cap=NODES,
        source_memo_cap=MEMO, source_memo_entries=len(owner.bindings),
        retained_nodes=len(owner.reader.nodes), retained_pages=len(owner.pages),
        retained_page_bytes=sum(len(rt._buffers[key]) for key in owner.pages),
        actual_native_canonical_checks=dict(counts),
        separate_indices_agree_on_every_definition=True,
        all_reader_pages_equal_to_actual_paid_buffers=True)
    return result, rt


def worker(output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')}))
    started = time.perf_counter()
    result = dict(status='RUNNING', before=measured(host))
    publish(output, result)
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = control(cuda=True)
        result.update(status='PASS_ACTUAL_OWNED_VALUE_GRAPH', outcome=outcome,
            device=asdict(rt._cuda._device.check()))
    except Exception as error:
        result.update(status='UNRESOLVED', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    publish(output, result)
    return 0 if result['status'] == 'PASS_ACTUAL_OWNED_VALUE_GRAPH' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('original journal exists; never replay')
    if git('status', '--porcelain'):
        raise RuntimeError('commit all execution inputs before launch')
    source = git('rev-parse', 'HEAD')
    for name in ('FP_OWNED_VALUE_GRAPH_RUNTIME_CPU.json', 'FP_OWNED_VALUE_GRAPH_RUNTIME_FULL_V_CPU.json'):
        assert json.loads((ROOT/'evidence/minimal'/name).read_text(encoding='utf-8'))['status'] == 'PASS_OWNED_VALUE_GRAPH_RUNTIME_CPU'
    regression = json.loads((ROOT/'evidence/minimal/FP_OWNED_VALUE_GRAPH_REGRESSION_CPU.json').read_text(encoding='utf-8'))
    assert regression['status'] == 'PASS_OWNED_VALUE_GRAPH_REGRESSION_CPU'
    assert regression['audit_count'] == 21 and not regression['failures']
    assert not git('diff', regression['source_commit'], source, '--', 'src/reference_compiler',
        'scripts/audit_owned_value_graph_runtime.py', 'scripts/audit_owned_value_graph_regression.py')
    harness = json.loads(HARNESS.read_text(encoding='utf-8'))
    assert harness['status'] == 'PASS_OWNED_VALUE_GRAPH_DEVICE_HARNESS_CPU'
    assert not git('diff', harness['source_commit'], source, '--', 'src/reference_compiler', 'scripts')
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, host_cap=HOST, deadline_ms=DEADLINE,
        arena_bytes=ARENA, allocator_reserved_cap=ARENA, whole_board_VRAM_upper=24 << 30,
        node_cap=NODES, source_memo_cap=MEMO, token_base_fact_cap=BASE,
        protocol='experiments/next_token/OWNED_VALUE_GRAPH_CUDA_A1.md', scope=__doc__.strip())
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-owned-value-graph-') as directory:
            output = Path(directory)/'worker.json'
            started = time.perf_counter()
            job = run_in_job(__file__, ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
            journal.update(job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            if output.exists():
                raw = output.read_bytes()
                if len(raw) > 65536:
                    raise RuntimeError('unexpected oversized worker receipt')
                journal['result'] = json.loads(raw)
            result = journal.get('result', {})
            accepted = job.exit_code == 0 and not job.timed_out and result.get('status') == 'PASS_ACTUAL_OWNED_VALUE_GRAPH'
            if accepted:
                assert job.attached_before_resume and job.peak_job_commit <= HOST
                for moment in ('before', 'after'):
                    sample = result[moment]
                    assert (sample['process_id'], sample['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                    assert sample['job_commit_peak'] <= job.peak_job_commit
                    assert sample['lifetime_process_commit_peak'] <= job.peak_process_commit
                outcome = result['outcome']
                assert (outcome['training_events'], outcome['optimizer_commits'], outcome['report_events'],
                        outcome['checked_phases']) == (4, 2, 4, 19)
                assert outcome['complete_frame_bytes'] == 19 << 20
                assert outcome['arena']['native_allocation_counter'] == outcome['arena']['current_allocation_counter'] == [1, ARENA, 1]
                assert outcome['owned_value_graph']['actual_native_canonical_checks']['facts_evicted'] > 0
            journal.update(status='COMPLETE_OWNED_VALUE_GRAPH_CUDA_A1' if accepted else 'UNRESOLVED_OWNED_VALUE_GRAPH_CUDA_A1',
                accepted_execution=accepted)
        assert git('rev-parse', 'HEAD') == source and not git('status', '--porcelain', '--untracked-files=no')
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--cpu', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.cpu:
        if HARNESS.exists():
            parser.error('original harness receipt exists')
        if git('status', '--porcelain', '--untracked-files=no'):
            parser.error('commit harness inputs first')
        source = git('rev-parse', 'HEAD')
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('worker attempted subprocess')):
            result, _ = control(cuda=False)
        assert 'torch' not in sys.modules
        assert git('rev-parse', 'HEAD') == source and not git('status', '--porcelain', '--untracked-files=no')
        receipt = dict(status='PASS_OWNED_VALUE_GRAPH_DEVICE_HARNESS_CPU', source_commit=source, outcome=result,
            subprocess_creation_forbidden_across_control=True, actual_cuda_execution=False)
        with HARNESS.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, indent=2)+'\n')
        print(receipt['status'], flush=True)
    elif args.worker:
        if args.output is None:
            parser.error('worker output is required')
        raise SystemExit(worker(args.output))
    else:
        launch()
