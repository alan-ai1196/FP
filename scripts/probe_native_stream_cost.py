"""One source-bound native CPU pair; complete streams, no AMP/model score."""
from contextlib import contextmanager, nullcontext
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import shared_reference, byte_archive
from native_stream_audit_support import load, compiled_controls

JOURNAL = ROOT/'evidence/minimal/FP_NATIVE_STREAM_COST_A1.json'
HOST, DEADLINE, EVENTS = 16 << 30, 180000, 16
MODES = ('python', 'compiled')
PYTHON_COMPARE = shared_reference._compare_stream


def python_oracle():
    # Separate globals and a name outside the component substitution namespace.
    spec = importlib.util.spec_from_file_location('fp_canonical_stream_oracle',
        ROOT/'src/reference_compiler/fp_reference/encoding.py')
    module = importlib.util.module_from_spec(spec)
    module.__package__ = 'fp_reference'
    spec.loader.exec_module(module)
    assert module.fragments.__module__ == 'fp_canonical_stream_oracle'
    return module


@contextmanager
def capture_allocations():
    original, records = shared_reference._SharedReference.allocate, []
    def observe(archive, runtime, owner, planned):
        result = original(archive, runtime, owner, planned)
        records.append((planned.spec.object_id, len(archive.pages)-1, planned.value))
        return result
    with patch.object(shared_reference._SharedReference, 'allocate', observe):
        yield records


def verify_bytes(runtime, records, oracle):
    """All images uncached, then every complete record through a fresh reader."""
    archive, image_count, image_bytes = runtime._reference_archive, 0, 0
    cfg, buffers = archive.contract, runtime._buffers
    if archive.images is not None:
        for entry in archive.images.entries:
            assert archive.images.find(entry.source) is entry
            raw = buffers[entry.buffer]
            assert type(raw) is bytes and len(raw) == entry.size
            PYTHON_COMPARE((memoryview(raw)[i:i+8192] for i in range(0, len(raw), 8192)),
                (s.encode('utf-8', 'surrogatepass') for s in oracle.fragments(entry.source, packed=True)),
                entry.size)
            image_count += 1
            image_bytes += entry.size
    assert len(records) == len(archive.pages)
    reader, record_bytes, live_roots = byte_archive.Reader(), 0, 0
    for expected_ordinal, ((label, ordinal, value), page) in enumerate(zip(records, archive.pages)):
        assert ordinal == expected_ordinal
        header = reader.add(buffers[page])
        assert header.ordinal == ordinal
        if label in buffers:
            raw = buffers[label]
            assert raw == shared_reference.ROOT_MAGIC+byte_archive.U64.pack(ordinal)
            live_roots += 1
        PYTHON_COMPARE(reader.decoded(ordinal, byte_cap=cfg.expanded_cap,
            reference_cap=cfg.reference_cap),
            (s.encode('utf-8', 'surrogatepass') for s in oracle.fragments(value,
                packed=True, images=archive.images)), header.expanded_bytes)
        record_bytes += header.expanded_bytes
    return dict(images=image_count, uncached_image_bytes=image_bytes,
        records=len(records), complete_record_bytes=record_bytes, live_roots=live_roots,
        independent_uncompiled_encoder_and_comparator=True, fresh_reader=True)


def worker(mode, output):
    from run_native_text_a1 import registration, TRAIN, progress, complete_residency, publish
    from run_text_baseline_anchor_a1 import tape
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.ingress import encode_context
    from audit_token_reference_host import measured
    host_contract = HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    started = time.perf_counter()
    result = dict(status='RUNNING', mode=mode, before=measured(host), operations=[])
    save = lambda: publish(output, result)
    save()
    try:
        oracle = python_oracle()
        context = nullcontext()
        if mode == 'compiled':
            encoder, consumers, manifest = load()
            result['native_build'] = manifest
            context = compiled_controls(encoder, consumers)
        training, identity = tape('train', TRAIN)
        old = json.loads((ROOT/'evidence/minimal/FP_NATIVE_TEXT_A1.json').read_text(encoding='utf-8'))
        assert old['status'] == 'UNRESOLVED_NATIVE_TEXT_A1'
        assert identity['prefix_sha256'] == old['result']['training_source']['prefix_sha256']
        result['training_source'] = identity
        with context, capture_allocations() as records:
            cc, program, online, storage, reporting = registration()
            assert len(online.data.active.observation_ids) == TRAIN == 1048576
            result['program_id'] = program.program_id
            init = time.perf_counter()
            rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
                reporting=reporting, host=host_contract)
            result['initialization_seconds'] = time.perf_counter()-init
            save()
            for index, target in enumerate(training[:EVENTS]):
                for label, action, expected in (
                    ('predict', lambda: rt.predict_next(f'train/{index}', encode_context(())), 'PREDICTED_REFERENCE'),
                    ('observe', lambda: rt.observe(int(target)), 'OBSERVED_REFERENCE')):
                    start = time.perf_counter()
                    outcome = action()
                    elapsed = time.perf_counter()-start
                    result['operations'].append(dict(operation=label, index=index, seconds=elapsed))
                    assert outcome.status == expected, outcome.reason
                save()
            result['ordinary_seconds'] = sum(r['seconds'] for r in result['operations'])
            state = rt._candidates[rt._deployed_id].learner
            assert (rt._cursor, state.cursor, state.unit_count, state.optimizer_steps) == (16, 16, 16, 0)
            assert len(rt._observations) == len(rt._event_traces) == 16
            assert tuple(r.target for r in rt._observations) == tuple(map(int, training[:16]))
            for index, record in enumerate(rt._observations):
                expected = tuple(50257 if lag > index else int(training[index-lag]) for lag in range(1, 513))
                assert record.cursor == index and record.sources.past == expected
            assert rt._token_report is None and rt._cuda is None and 'torch' not in sys.modules
            result.update(latest=progress(rt, label='terminal', started=started),
                residency=complete_residency(rt), original_training_declaration=TRAIN,
                all_original_sources_targets_and_traces_retained=True,
                actual_amp_execution=False, model_score=None)
            save()
            audit_start = time.perf_counter()
            result['independent_bytes'] = verify_bytes(rt, records, oracle)
            result['independent_audit_seconds'] = time.perf_counter()-audit_start
            result['status'] = 'PASS_NATIVE_STREAM_COST_A1'
    except Exception as error:
        result.update(status='UNRESOLVED_NATIVE_STREAM_COST_A1', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-4000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    save()
    return 0 if result['status'] == 'PASS_NATIVE_STREAM_COST_A1' else 2


def launch():
    from windows_job_audit_support import run_in_job
    from run_native_text_a1 import publish
    if JOURNAL.exists():
        raise RuntimeError('original stream cost control exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all control inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # Check build provenance before opening the exclusive execution journal.
    _, _, manifest = load()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, native_build=manifest,
        host_cap=HOST, deadline_ms=DEADLINE, observed_events=EVENTS,
        original_training_declaration=1048576, order=MODES, results=[],
        protocol='experiments/next_token/NATIVE_STREAM_COST_A1.md')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-native-stream-cost-') as directory:
            for mode in MODES:
                output = Path(directory)/(mode+'.json')
                run = run_in_job(__file__, ('--worker', '--mode', mode, '--output', output),
                    commit_limit=HOST, timeout_ms=DEADLINE)
                item = dict(mode=mode, job=asdict(run))
                if output.exists():
                    payload = output.read_bytes()
                    if len(payload) > 131072:
                        raise RuntimeError('unexpected stream-cost receipt size')
                    item['result'] = json.loads(payload)
                result = item.get('result', {})
                accepted = (run.exit_code == 0 and not run.timed_out
                    and result.get('status') == 'PASS_NATIVE_STREAM_COST_A1')
                if accepted:
                    assert run.attached_before_resume and run.peak_job_commit <= HOST
                    for moment in ('before', 'after'):
                        sample = result[moment]
                        assert (sample['process_id'], sample['creation_100ns']) == (
                            run.process_id, run.process_creation_100ns)
                        assert sample['job_commit_peak'] <= run.peak_job_commit
                        assert sample['lifetime_process_commit_peak'] <= run.peak_process_commit
                    assert len(result['operations']) == 32 and result['model_score'] is None
                    assert not result['actual_amp_execution'] and result['original_training_declaration'] == 1048576
                    assert result['independent_bytes']['records'] > 0
                    assert result['independent_bytes']['images'] > 0
                    if mode == 'compiled':
                        assert result['native_build'] == manifest
                item['accepted_execution'] = accepted
                journal['results'].append(item)
                publish(JOURNAL, journal)
                print(mode, result.get('status', 'MISSING'), flush=True)
        accepted = all(r['accepted_execution'] for r in journal['results'])
        journal.update(status='COMPLETE_NATIVE_STREAM_COST_A1' if accepted else 'UNRESOLVED_NATIVE_STREAM_COST_A1',
            accepted_execution=accepted)
        if accepted:
            original, compiled = [r['result'] for r in journal['results']]
            assert original['program_id'] == compiled['program_id']
            journal['observed_python_over_compiled_ordinary_seconds'] = (
                original['ordinary_seconds']/compiled['ordinary_seconds'])
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


def control():
    from audit_token_reporting import report_registration
    from audit_shared_token_retention import STORAGE
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.core import ContractError
    from fp_reference.ingress import encode_context
    oracle = python_oracle()
    encoder, consumers, _ = load()
    for mode in MODES:
        context = compiled_controls(encoder, consumers) if mode == 'compiled' else nullcontext()
        with context, capture_allocations() as records:
            cc, p, online, report = report_registration()
            rt = ReferenceCompilerRuntime(cc, p, online=online, reporting=report,
                shared_storage=replace(STORAGE, canonical_image_bytes=4 << 20))
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
            archive = rt._reference_archive
            archive.prepare_frame(rt, 'oracle-control', tuple(range(2048)), role='compiler')
            checked = verify_bytes(rt, records, oracle)
            assert checked['images'] > 0 and checked['records'] > 0
            for label in (archive.images.entries[0].buffer, archive.pages[0]):
                old = rt._buffers[label]
                rt._buffers[label] = bytes((old[0] ^ 1,))+old[1:]
                try:
                    verify_bytes(rt, records, oracle)
                except ContractError:
                    pass
                else:
                    raise AssertionError('independent oracle missed corrupt image/page')
                finally:
                    rt._buffers[label] = old
    assert 'torch' not in sys.modules
    print('PASS_NATIVE_STREAM_COST_HARNESS_CPU')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', action='store_true')
    mode.add_argument('--control', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--mode', choices=MODES)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.control:
        control()
    elif args.worker:
        if args.output is None or args.mode is None:
            parser.error('worker output and mode required')
        raise SystemExit(worker(args.mode, args.output))
    else:
        launch()
