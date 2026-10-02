"""Actual AMP qualification with historical source delivered by the launcher.

Two packed/shared training/reporting controls. No corpus, new model, cost
comparison, full-V budget, installation or whole-release claim.
"""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import hashlib
from unittest.mock import patch
import os
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from run_public_value_cuda_a1 import exercise, publish, HOST, DEADLINE, ARENA

from captured_values_audit_support import SOURCE

SOURCE_PATH = 'src/reference_compiler/fp_reference/token_execution.py'
CASES = ('packed', 'shared')
JOURNAL = ROOT/'evidence/minimal/FP_CAPTURED_VALUES_CUDA_A2.json'
HARNESS = ROOT/'evidence/minimal/FP_CAPTURED_VALUES_DEVICE_HARNESS_A2_CPU.json'


def extract_literal_source():
    return subprocess.check_output(['git', 'show', SOURCE+':'+SOURCE_PATH], cwd=ROOT)


def load_literal_source(path, expected):
    raw = path.read_bytes()
    if len(raw) > 65536 or hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError('historical source artifact lost its exact byte identity')
    return raw.decode('utf-8')


def control(case, *, cuda, literal_source):
    from captured_values_audit_support import literal_predictions
    from fp_reference import encoding
    from fp_reference.data_usage import source_mapping
    from fp_reference.token_values import CapturedTokenValues

    # Reuse the fixed fixture, never its historical launcher or journal.
    result, rt = exercise(case, cuda=cuda)
    program = rt._programs[rt._candidates[rt._deployed_id].program_id]
    records = {record.observation_id: record for record in rt._observations}
    predictions = [(trace.prediction, records[trace.observation_id]) for trace in rt._event_traces]
    predictions += [(event.prediction, event.record) for event in rt._token_report.events]
    assert len(predictions) == 8
    coordinates = canonical_bytes = containers = 0
    # A passive exact comparator after execution; it issues no forecast,
    # resource admission, bridge, persistence or installation authority.
    with literal_predictions(literal_source):
        for prediction, record in predictions:
            values = prediction.values
            assert type(values) is CapturedTokenValues
            embedding, width, past, grid, tail = values.validate()
            assert embedding is prediction.before.origin.embedding and past is prediction.window.past
            literal = rt._machine.predict(program, rt._contract.semantics, prediction.before,
                source_mapping(record.sources), bit_limit=rt._contract.reference_integer_bits)
            assert type(literal.values) is tuple and tuple(values) == literal.values
            assert prediction == literal
            original = encoding.pack(literal)
            assert encoding.pack(prediction) == original
            coordinates += len(values)
            canonical_bytes += len(original)
            containers += sys.getsizeof(values)+sys.getsizeof(tail)
    result['captured_values'] = dict(original_training_and_report_forecasts=8,
        historical_literal_value_coordinates=coordinates,
        complete_literal_prediction_bytes_compared=canonical_bytes,
        selected_capture_tail_container_bytes=containers,
        original_immutable_embedding_and_context_references_preserved=True,
        actual_node_tail_and_complete_logical_values_equal=True)
    return result, rt


def worker(case, output, literal_path, literal_digest):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(HOST, {r: HOST for r in ('deployment', 'compiler')}))
    started = time.perf_counter()
    result = dict(status='RUNNING', case=case, before=measured(host))
    publish(output, result)
    try:
        literal_source = load_literal_source(literal_path, literal_digest)
        import torch
        torch.set_num_threads(1)
        checked, rt = control(case, cuda=True, literal_source=literal_source)
        gpu = torch.cuda.get_device_name(0)
        assert gpu == 'NVIDIA GeForce RTX 3090' and torch.cuda.get_device_capability(0) == (8, 6)
        result.update(status='PASS_ACTUAL_CAPTURED_VALUES', outcome=checked,
            device=asdict(rt._cuda._device.check()), gpu_name=gpu,
            torch_version=str(torch.__version__), torch_cuda_version=torch.version.cuda)
    except Exception as error:
        result.update(status='FAILED', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    publish(output, result)
    return 0 if result['status'] == 'PASS_ACTUAL_CAPTURED_VALUES' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('original journal exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit all execution inputs before launch')
    cpu = json.loads((ROOT/'evidence/minimal/FP_CAPTURED_VALUES_REGRESSION_CPU.json').read_text(encoding='utf-8'))
    assert cpu['status'] == 'PASS_CAPTURED_VALUES_REGRESSION_CPU' and cpu['audit_count'] == 25
    subprocess.run(['git', 'diff', '--exit-code', cpu['source_commit'], '--', 'src/reference_compiler'],
        cwd=ROOT, check=True, capture_output=True)
    assert json.loads(HARNESS.read_text(encoding='utf-8'))['status'] == 'PASS_CAPTURED_VALUES_DEVICE_HARNESS_A2_CPU'
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    literal_bytes = extract_literal_source()
    literal_digest = hashlib.sha256(literal_bytes).hexdigest()
    journal = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=HOST,
        deadline_ms=DEADLINE, arena_bytes=ARENA, allocator_reserved_cap=ARENA,
        whole_board_VRAM_upper=24 << 30, protocol='experiments/next_token/CAPTURED_VALUES_CUDA_A2.md',
        scope=__doc__.strip(), results=[], historical_source_artifact=dict(
            commit=SOURCE, path=SOURCE_PATH, bytes=len(literal_bytes), sha256=literal_digest))
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for case in CASES:
            journal['active_case'] = case
            publish(JOURNAL, journal)
            with tempfile.TemporaryDirectory(prefix='fp-captured-values-cuda-') as directory:
                output = Path(directory)/'worker.json'
                literal_path = Path(directory)/'historical-token-execution.py'
                literal_path.write_bytes(literal_bytes)
                started = time.perf_counter()
                job = run_in_job(__file__, ('--worker', case, '--output', output,
                    '--literal-source', literal_path, '--source-sha256', literal_digest),
                    commit_limit=HOST, timeout_ms=DEADLINE)
                row = dict(case=case, job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
                journal['results'].append(row)
                if output.exists():
                    data = output.read_bytes()
                    if len(data) > 65536:
                        raise RuntimeError('unexpected oversized worker receipt')
                    row['result'] = json.loads(data)
                result = row.get('result', {})
                accepted = job.exit_code == 0 and not job.timed_out and result.get('status') == 'PASS_ACTUAL_CAPTURED_VALUES'
                row['accepted_execution'] = accepted
                if accepted:
                    assert job.attached_before_resume and job.peak_job_commit <= HOST
                    for moment in ('before', 'after'):
                        measurement = result[moment]
                        assert (measurement['process_id'], measurement['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                        assert measurement['job_commit_peak'] <= job.peak_job_commit
                        assert measurement['lifetime_process_commit_peak'] <= job.peak_process_commit
                    outcome = result['outcome']
                    assert (outcome['training_events'], outcome['optimizer_commits'], outcome['report_events'], outcome['checked_phases']) == (4, 2, 4, 19)
                    assert outcome['complete_frame_bytes'] == 19 << 20
                    assert outcome['arena']['native_allocation_counter'] == outcome['arena']['current_allocation_counter'] == [1, ARENA, 1]
                    assert outcome['captured_values']['historical_literal_value_coordinates'] == 96
                print(case+': '+result.get('status', 'NO_COMPLETE_RESULT'), flush=True)
                publish(JOURNAL, journal)
                if not accepted:
                    journal['status'] = 'UNRESOLVED_CAPTURED_VALUES_CUDA_A2'
                    break
        else:
            journal['status'] = 'COMPLETE_CAPTURED_VALUES_CUDA_A2'
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()
        journal['source_unchanged_during_checks'] = True
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        journal.pop('active_case', None)
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--cpu', action='store_true')
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', choices=CASES)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--literal-source', type=Path)
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    if args.cpu:
        if HARNESS.exists():
            parser.error('harness receipt already exists')
        literal_bytes = extract_literal_source()
        literal_digest = hashlib.sha256(literal_bytes).hexdigest()
        with tempfile.TemporaryDirectory(prefix='fp-captured-source-a2-') as directory:
            literal_path = Path(directory)/'historical-token-execution.py'
            literal_path.write_bytes(literal_bytes)
            literal_source = load_literal_source(literal_path, literal_digest)
            literal_path.write_bytes(literal_bytes+b'\n')
            try:
                load_literal_source(literal_path, literal_digest)
            except RuntimeError:
                pass
            else:
                raise AssertionError('changed historical bytes accepted')
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('worker attempted child process')):
            result = {case: control(case, cuda=False, literal_source=literal_source)[0] for case in CASES}
        assert 'torch' not in sys.modules
        receipt = dict(status='PASS_CAPTURED_VALUES_DEVICE_HARNESS_A2_CPU', cases=result,
            actual_cuda_execution=False, no_child_process_required=True,
            changed_source_artifact_refused=True, scope='native control for the fixed one-process device harness')
        with HARNESS.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, indent=2)+'\n')
        print(receipt['status'], flush=True)
    elif args.worker:
        if args.output is None or args.literal_source is None or args.source_sha256 is None:
            parser.error('worker output and bound historical source artifact are required')
        raise SystemExit(worker(args.worker, args.output, args.literal_source, args.source_sha256))
    else:
        launch()

