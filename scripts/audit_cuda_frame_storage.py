"""Exact completed-frame preservation and bounded host/CUDA regressions.

The synthetic host fixture is a storage experiment, not a model execution.
The historical Runtime snapshot/constructor source is checked unchanged;
the legacy fixture retains the actual former mutable frame representation.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import fp_reference.runtime as execution
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.resources import ObjectSpec, ResourceExceeded, ResourceLedger
from audit_reference_construction import contract, limits, rejects, validate_residency, zero_program

BASELINE = 'b0c409c'
OUTPUT = ROOT/'evidence/minimal/FP_CUDA_FRAME_STORAGE_AUDIT.json'
HOST_FRAMES, HOST_EXTENT, HOST_SNAPSHOTS = 128, 1 << 20, 2
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty')
CASES = ('legacy', 'immutable', 'simplex-profile', 'likelihood-profile', 'frame-cap',
         'combined-failure', 'seal-publish-expected', 'seal-publish-unexpected',
         'seal-copy-memory', 'seal-executor-priority')


def git(*args):
    return subprocess.check_output(('git', *args), cwd=ROOT, encoding='utf-8').strip()


def source_check():
    path = 'src/reference_compiler/fp_reference/runtime.py'
    old = ast.parse(git('show', BASELINE+':'+path))
    new = ast.parse((ROOT/path).read_text(encoding='utf-8'))

    def method(tree, name):
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ReferenceCompilerRuntime')
        return ast.dump(next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name))

    for name in ('snapshot', '__init__'):
        assert method(old, name) == method(new, name), name
    return {'baseline': git('rev-parse', BASELINE),
            'actual_snapshot_and_constructor_AST_unchanged': True,
            'legacy_representation': 'one bytearray per completed frame; exact prior snapshot method'}


def fixture(*, byte_cap=512 << 20, work_cap=10**12):
    cfg = replace(contract(), limits=limits(byte_cap=byte_cap, work_cap=work_cap))
    return execution.ReferenceCompilerRuntime(cfg, zero_program(2))


def add_frame(root, ordinal, extent):
    label = f'storage-fixture:cuda:{ordinal}'
    root._ledger.allocate(root._data_owner, (ObjectSpec(label, 'owned_cuda_phase_frame',
        {'reference_payload_bytes': extent, 'physical_objects': 1}, root._chi),))
    root._buffers[label] = bytearray(extent)
    # All byte values, including nonzero padding: preservation must not rely
    # on zero-filled unused tails or on interpreting just the encoded prefix.
    block = bytes((i+ordinal) % 256 for i in range(4096))
    for offset in range(0, extent, len(block)):
        root._buffers[label][offset:min(offset+len(block), extent)] = block[:min(len(block), extent-offset)]
    payload = pack((label, 'COMPLETE_SYNTHETIC_FRAME', ordinal))
    assert len(payload)+8 <= extent
    root._buffers[label][:8] = len(payload).to_bytes(8, 'big')
    root._buffers[label][8:8+len(payload)] = payload
    return label


def seal(root, label):
    root._seal_cuda_frame(label, origin='construction', candidate=root._deployed_id)


def exact_audit():
    root = fixture()
    frames, compared, seen = [], 0, set()
    for ordinal in range(32):
        label = add_frame(root, ordinal, 512+ordinal)
        before = dict(root.snapshot().buffers)[label]
        seen.update(before)
        prior = root._ledger.snapshot()
        seal(root, label)
        after = validate_residency(root)
        assert type(root._buffers[label]) is bytes and root._buffers[label] == before
        assert after.resources['current'] == prior['current']
        assert after.resources['peak']['reference_payload_bytes'] >= prior['current']['reference_payload_bytes']+len(before)
        assert label+':immutable-copy' in root._ledger._retired
        assert root._router._ledger is root._event_router._ledger is root._ledger
        frames.append(label)
        compared += len(before)
    earlier = root.snapshot()
    old_buffers = dict(earlier.buffers)
    fresh = add_frame(root, 32, 1024)
    fresh_bytes = dict(root.snapshot().buffers)[fresh]
    seal(root, fresh)
    later = root.snapshot()
    current_buffers = dict(later.buffers)
    for label in frames:
        assert current_buffers[label] is old_buffers[label] is root._buffers[label]
    assert fresh not in old_buffers and fresh in current_buffers
    assert current_buffers[fresh] == fresh_bytes
    assert seen == set(range(256))
    rejects(lambda: root._buffers[frames[0]].__setitem__(8, 0), AttributeError)
    rejects(lambda: seal(root, frames[0]))
    nonframe = next(key for key, value in root._ledger._objects.items() if value.kind != 'owned_cuda_phase_frame')
    rejects(lambda: seal(root, nonframe))

    base = fixture()
    initial_bytes = base._ledger.snapshot()['current']['reference_payload_bytes']
    initial_work = base._ledger.snapshot()['spent']['compiler']['work']
    refused = []
    for kind, limited in (
            ('copy-residency', fixture(byte_cap=initial_bytes+1024)),
            ('copy-work', fixture(work_cap=initial_work))):
        label = add_frame(limited, 0, 1024)
        before = limited.snapshot()
        with patch.object(execution, 'bytes', side_effect=AssertionError('unpaid frame copy'), create=True):
            rejects(lambda: seal(limited, label), ResourceExceeded)
        after = validate_residency(limited)
        assert after.resources['current'] == before.resources['current']
        assert dict(after.buffers) == dict(before.buffers)
        assert type(limited._buffers[label]) is bytearray
        refused.append(kind)

    failures = []
    for point in ('prepare-release', 'prepare-router'):
        for error_type in (ResourceExceeded, RuntimeError):
            broken = fixture()
            label = add_frame(broken, 0, 1024)
            original_root = broken.__dict__
            initial = broken._ledger.snapshot()['current']['reference_payload_bytes']
            target, method = ((ResourceLedger, 'prepare_transfer') if point == 'prepare-release'
                              else (execution, 'CostRouter'))
            with patch.object(target, method, side_effect=error_type('retained prepublication fault')):
                rejects(lambda: seal(broken, label), error_type)
            snapshot = validate_residency(broken)
            assert broken.__dict__ is original_root
            assert type(broken._buffers[label]) is bytearray
            assert type(broken._buffers[label+':immutable-copy']) is bytes
            assert broken._buffers[label] == broken._buffers[label+':immutable-copy']
            assert snapshot.resources['current']['reference_payload_bytes'] == initial+1024
            assert snapshot.resources['objects'][label+':immutable-copy']['references'] == {broken._data_owner: 1}
            failures.append(point+':'+error_type.__name__)
    return {'status': 'EXACT_FRAME_PRESERVATION_PASS', 'frames': len(frames)+1,
            'full_frame_bytes_compared': compared+1024, 'all_256_byte_values_exercised': True,
            'prior_snapshot_unchanged_after_next_frame': True, 'new_snapshot_reuses_every_old_immutable_frame': True,
            'unchanged_snapshot_source': source_check(), 'pre_copy_refusals': refused,
            'both_actual_buffers_remain_owned_after_faults': failures,
            'no_model_execution_or_certificate': True}


def host_worker(mode):
    root = fixture()
    labels = []
    for ordinal in range(HOST_FRAMES):
        label = add_frame(root, ordinal, HOST_EXTENT)
        if mode == 'immutable':
            seal(root, label)
        labels.append(label)
    snapshots = [root.snapshot() for _ in range(HOST_SNAPSHOTS)]
    snapshot_buffers = [dict(s.buffers) for s in snapshots]
    byte_checks, identities = 0, set()
    for label in labels:
        identities.add(id(root._buffers[label]))
        for buffers in snapshot_buffers:
            assert buffers[label] == root._buffers[label]
            identities.add(id(buffers[label]))
            byte_checks += HOST_EXTENT
    expected = HOST_FRAMES*(1 if mode == 'immutable' else HOST_SNAPSHOTS+1)
    assert len(identities) == expected
    return {'status': 'SYNTHETIC_COMPLETE_SNAPSHOT_STORAGE_PASS', 'process_id': os.getpid(),
            'representation': mode, 'frames': HOST_FRAMES, 'bytes_per_frame': HOST_EXTENT,
            'simultaneous_complete_snapshots': HOST_SNAPSHOTS, 'full_frame_bytes_compared': byte_checks,
            'distinct_live_frame_payloads': len(identities),
            'distinct_live_frame_payload_bytes': len(identities)*HOST_EXTENT,
            'packed_peak': dict(root._ledger.snapshot()['peak']),
            'no_CUDA_or_model_outcome': True}


def cuda_worker(case):
    if case.startswith('seal-'):
        return cuda_failure(case)
    original = execution.ReferenceCompilerRuntime._seal_cuda_frame
    prepare = ResourceLedger.prepare_transfer
    counts = {'frames': 0, 'full_frame_bytes_compared': 0, 'maximum_copy_bytes': 0}

    def checked(root, label, **kwargs):
        def compare(ledger, moves, releases=(), close_owners=()):
            copy_id = label+':immutable-copy'
            assert releases == ((root._data_owner, copy_id, 1),)
            assert ledger is root._ledger
            assert type(root._buffers[label]) is bytearray
            assert type(root._buffers[copy_id]) is bytes
            assert root._buffers[label] == root._buffers[copy_id]
            assert len(root._buffers[label]) == root._cuda.contract.phase_evidence_bytes
            assert ledger._refs[label] == ledger._refs[copy_id] == {root._data_owner: 1}
            counts['full_frame_bytes_compared'] += len(root._buffers[label])
            counts['maximum_copy_bytes'] = max(counts['maximum_copy_bytes'], len(root._buffers[label]))
            return prepare(ledger, moves, releases, close_owners)

        with patch.object(ResourceLedger, 'prepare_transfer', compare):
            original(root, label, **kwargs)
        assert type(root._buffers[label]) is bytes
        assert label+':immutable-copy' not in root._buffers
        counts['frames'] += 1

    with patch.object(execution.ReferenceCompilerRuntime, '_seal_cuda_frame', checked):
        if case == 'likelihood-profile':
            from likelihood_lowering import owned
            result = owned('profile-install')
        elif case == 'simplex-profile':
            from audit_simplex_learner import owned
            result = owned(n=2, profiles=True, cuda=True, bounded=True)
        else:
            from audit_cuda_runtime import execute_case
            result = execute_case(case)
    assert counts['frames'] > 0
    return {'status': 'ACTUAL_CUDA_FRAME_PRESERVATION_PASS', 'process_id': os.getpid(),
            'case': case, 'retained_frame_checks': counts, 'complete_existing_audit': result}


def cuda_failure(case):
    from fp_reference import cuda_learner as gpu
    from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
    from audit_cuda_runtime import configuration, cuda_contract, domain
    from audit_reference_events import online
    from ingress_audit_support import deliver_context
    cfg = configuration()
    root = execution.ReferenceCompilerRuntime(cfg, zero_program(2),
        online=online(cfg, 3, unit=2, rate=F(1, 8), grid=16), cuda=cuda_contract())
    assert deliver_context(root, 'observation-0', domain(1)[1]).status == 'PREDICTED_REFERENCE'
    before = root.snapshot()
    original = execution.ReferenceCompilerRuntime._seal_cuda_frame
    original_observe = gpu.observe_event
    executor_error = RuntimeError('original executor failure survives failed immutable retention')
    reached = []

    def broken(owner, label, **kwargs):
        reached.append(label)
        if case == 'seal-copy-memory':
            with patch.object(execution, 'bytes', side_effect=MemoryError('injected copy allocation failure'), create=True):
                original(owner, label, **kwargs)
        else:
            error_type = RuntimeError if case == 'seal-publish-unexpected' else ResourceExceeded
            with patch.object(ResourceLedger, 'prepare_transfer', side_effect=error_type('injected frame publication refusal')):
                original(owner, label, **kwargs)

    def observe(*args, **kwargs):
        if case == 'seal-executor-priority':
            raise executor_error
        return original_observe(*args, **kwargs)

    caught = None
    with patch.object(execution.ReferenceCompilerRuntime, '_seal_cuda_frame', broken), patch.object(gpu, 'observe_event', observe):
        try:
            result = root.observe(1)
        except (RuntimeError, MemoryError) as exc:
            caught = exc
        else:
            assert case == 'seal-publish-expected' and result.status == 'UNRESOLVED'
    assert len(reached) == 1
    snapshot = root.snapshot() if case == 'seal-copy-memory' else validate_residency(root)
    label, = reached
    assert snapshot.halted and snapshot.cursor == 0 and snapshot.pending.record.target == 1
    assert len(snapshot.observations) == 1 and snapshot.observations[0].target == 1
    assert snapshot.candidates == before.candidates
    assert snapshot.cuda.current == before.cuda.current and snapshot.cuda.staged == before.cuda.staged
    assert not snapshot.install_receipts and snapshot.run.status != 'SEALED_CUDA_STREAM'
    assert type(root._buffers[label]) is bytearray
    assert label+':immutable-copy' in snapshot.resources['objects']
    if case == 'seal-copy-memory':
        assert type(caught) is MemoryError and root._halted is HOST_ALLOCATION_FAILURE
        assert label+':immutable-copy' not in root._buffers
        rejects(lambda: root.begin_context('observation-1'))
    else:
        assert type(root._buffers[label+':immutable-copy']) is bytes
        assert root._buffers[label] == root._buffers[label+':immutable-copy']
        assert snapshot.cuda.phases[-1].status == ('UNRESOLVED' if case == 'seal-publish-expected' else 'EXECUTION_FAILED')
        if case == 'seal-executor-priority':
            assert caught is executor_error
        elif case == 'seal-publish-unexpected':
            assert type(caught) is RuntimeError
    return {'status': 'ACTUAL_CUDA_FINALIZATION_FAILURE_PASS', 'case': case, 'process_id': os.getpid(),
            'received_target_and_actual_device_prefix_retained': True, 'failed_phase_never_accepted': True,
            'both_copies_retained_and_owned': case != 'seal-copy-memory',
            'terminal_partial_allocation_prefix': case == 'seal-copy-memory',
            'original_executor_error_preserved': case == 'seal-executor-priority'}


def bounded(case):
    from windows_job_audit_support import run_in_job
    source = git('rev-parse', 'HEAD')
    assert not git('status', '--porcelain', '--', *DEPENDENCIES), 'commit execution dependencies first'
    source_evidence = source_check()
    cap, timeout = ((512 << 20, 60000) if case in ('legacy', 'immutable') else (4 << 30, 180000))
    temporary = Path(tempfile.mkdtemp(prefix='fp-frame-storage-', dir=ROOT))
    assert temporary.resolve().parent == ROOT.resolve()
    output = temporary/'result.json'
    row = {'case': case, 'execution_source': source, 'status': 'FAILED', 'baseline_check': source_evidence}
    try:
        job = run_in_job(__file__, ('--worker', case, '--output', str(output)), commit_limit=cap, timeout_ms=timeout)
        row['completed_job'] = asdict(job)
        if output.exists() and output.stat().st_size <= 262144:
            row['result'] = json.loads(output.read_text(encoding='utf-8'))
        assert job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
        assert job.attached_before_resume and job.peak_job_commit <= cap
        assert row['result']['process_id'] == job.process_id
        assert git('rev-parse', 'HEAD') == source and not git('status', '--porcelain', '--', *DEPENDENCIES)
        row['status'] = 'PASS'
    except Exception as exc:
        row['failure'] = {'type': type(exc).__name__, 'reason': str(exc)}
    finally:
        output.unlink(missing_ok=True)
        temporary.rmdir()
    return row


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--bounded', nargs='+', choices=CASES)
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert bool(args.worker) == bool(args.output)
    failed = False
    if args.worker:
        assert not (args.write or args.bounded)
        try:
            result = host_worker(args.worker) if args.worker in ('legacy', 'immutable') else cuda_worker(args.worker)
        except Exception as exc:
            failed = True
            result = {'status': 'FAILED', 'process_id': os.getpid(),
                      'failure': {'type': type(exc).__name__, 'reason': str(exc),
                                  'traceback': traceback.format_exc(limit=10)[-5000:]}}
    else:
        result = exact_audit()
        prior = json.loads(OUTPUT.read_text(encoding='utf-8')) if args.write and OUTPUT.exists() else {}
        previous = prior.get('bounded_attempts', [])
        if 'bounded_attempt_notes' in prior:
            result['bounded_attempt_notes'] = prior['bounded_attempt_notes']
        for case in args.bounded or ():
            row = bounded(case)
            previous.append(row)
            failed |= row['status'] != 'PASS'
        if previous:
            result['bounded_attempts'] = previous
    text = json.dumps(result, indent=2)+'\n'
    if args.worker:
        args.output.write_text(text, encoding='utf-8')
    elif args.write:
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
    if failed:
        raise SystemExit(1)
