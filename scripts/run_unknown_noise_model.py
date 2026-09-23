"""Four preregistered complete joint-noise model jobs and a passive reader."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/joint_uncertainty')]
import unknown_noise_model as model
import audit_joint_cuda as gate
import read_joint_amp_gate as gate_reader
from audit_unknown_noise_model import BUDGET
from audit_joint_runtime import fixture
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job, JobRun
from fp_reference import ReferenceCompilerRuntime, HostResourceContract, CudaCompilerPolicy, phase_deflate
from fp_reference.cuda_prefix import JointCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference import joint_amp as amp, joint_partition_decoder as decoder
from fp_reference.binary_arithmetic import round_binary
from fp_reference.cuda_range import SINGLE, HALF

CAP, DEADLINE, PACKED, WORK = 16 << 30, 7200000, 8 << 30, 10**15
ARENA, FRAME, CELLS = 256 << 20, 4 << 20, 65536
CPU = 'evidence/minimal/FP_UNKNOWN_NOISE_MODEL_CPU.json'
GATE = 'evidence/minimal/FP_JOINT_AMP_CUDA_A1.json'
EXECUTION_SOURCE = '333cba1180607c8a538cb12a7115705e692c41fa'
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty',
    'experiments/adaptive_uncertainty', 'experiments/relation_noise', 'theory/numerical_checks',
    'theory/proofs/BAND_MODEL_RESOURCE_BOUND.md', 'evidence/minimal/FP_BAND_MODEL_CONTROL.json', CPU, GATE)


def git(*arguments):
    return subprocess.check_output(('git',)+arguments, cwd=ROOT, text=True).strip()


def configuration(case):
    _, train, evaluation = model.data(case)
    cfg, schema, online = fixture(case[0], len(train)+len(evaluation), budget=BUDGET, byte_cap=PACKED, work_cap=WORK)
    cfg = replace(cfg, normalizer_cap=F(38))
    storage = CudaStorageContract(ARENA, 2*ARENA, {r: (ARENA, 2*ARENA) for r in ('deployment', 'compiler')})
    cuda = JointCudaPrefixContract(storage, F(1, 100), F(1, 1000), schema=schema, partitions=BUDGET,
        phase_output_cells=CELLS, phase_evidence_bytes=FRAME, evidence_encoding=phase_deflate.ENCODING_ID)
    host = HostResourceContract(CAP, {r: CAP for r in ('deployment', 'compiler')})
    return cfg, schema, online, cuda, host


def preflight():
    assert 'torch' not in sys.modules
    cpu = json.loads((ROOT/CPU).read_text())
    assert cpu['status'] == 'PASS_UNKNOWN_NOISE_MODEL_CPU'
    gate_result = gate_reader.read(json.loads((ROOT/GATE).read_text()))
    assert gate_result['completed_jobs'] == 17
    assert not git('diff', gate_reader.SOURCE, '--', 'src/reference_compiler')
    for case in model.CASES:
        cfg, schema, online, cuda, host = configuration(case)
        assert schema.rates == model.RATES and schema.prior == model.PRIOR
        assert cuda.forward_id == amp.FORWARD_ID and len(online.data.active.observation_ids) == 376
        assert decoder.workspace_bytes(schema, BUDGET) == 264453
    return {'status': 'REGISTERED_UNKNOWN_NOISE_N64_MODEL', 'cases': model.CASES,
        'production_gate_source': gate_reader.SOURCE, 'production_gate_jobs': 17,
        'rates': list(map(str, model.RATES)), 'prior': list(map(str, model.PRIOR)),
        'budget': asdict(BUDGET), 'all_labels_bounds': cpu['all_labels_bounds'], 'workspace_bytes': 264453,
        'job_cap': CAP, 'deadline_ms': DEADLINE, 'packed_bytes': PACKED, 'work_per_role': WORK,
        'arena_bytes': ARENA, 'allocator_cap': 2*ARENA, 'phase_frame_bytes': FRAME, 'phase_output_cells': CELLS,
        'reference_integer_bits': 32768, 'state_atol': '1/100', 'probability_atol': '1/1000',
        'activation_cap': 18, 'normalizer_cap': 38, 'forward_id': amp.FORWARD_ID,
        'evidence_encoding': phase_deflate.ENCODING_ID, 'forest_events': 63, 'repeat_events': 63,
        'evaluation_events': 250, 'initial_training_unseen_evaluation_events': 124,
        'score_grid_bits': model.GRID, 'control': 'independent full unsigned-history finite-rate/world posterior; true-rate oracle receives the additional true rate',
        'scope': 'four declared tapes, two shared hidden/noise/order seeds across true-rate strata; no population, model selection, GPU integer inference or constructor optimum claim',
        'failure_policy': 'retain every outcome; no incomplete-prefix scores, retries or cap changes; continue honest resource refusal, stop unexpected execution/audit failure'}


def check_coordinates(state, control):
    d, s, t = control.coordinates()
    assert state.counts == d and state.diagonal == s and state.steps == state.cursor == t and state.pending is None
    assert state.model.rates == model.RATES and state.model.prior == model.PRIOR


def worker(case):
    cfg, schema, online, cuda, host = configuration(case)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online, cuda=cuda, host=host, policy=CudaCompilerPolicy(()))
    import torch
    device_name = torch.cuda.get_device_name(cuda.storage.device)
    hidden, train, evaluation = model.data(case)
    control = model.JointControl(case[0])
    raw = []
    checkpoints = {}
    maximum_gap = F(0)
    for k, (i, j, target) in enumerate(train+evaluation):
        expected = control.predict(i, j)
        if k <= 63:
            assert expected.rate_posterior == model.PRIOR
        if k < 63:
            assert expected.joint == (F(1, 2),)*2
        if k in (0, 63, 126):
            checkpoints[str(k)] = [model.enclosure(v) for v in expected.rate_posterior]
        result = deliver_context(runtime, online.data.active.observation_ids[k],
            tuple(schema.source_row(i*schema.n+j).values()))
        if result.status != 'PREDICTED_REFERENCE':
            assert result.status == 'UNRESOLVED'
            return unresolved(runtime, case, result.reason, device_name)
        assert len(result.predictions) == 1 and result.predictions[0][1] == expected.joint
        snapshot = runtime.snapshot()
        phase = snapshot.cuda.phases[-1]
        assert phase.phase == 'ordinary:predict' and phase.reference_prediction.probabilities == expected.joint
        assert phase.execution_plan.normalization == sum(sum(p) for p in expected.rate_parts)
        words = phase.raw_prediction.words[2:4]+phase.raw_prediction.words[5:7]
        masses = tuple(amp.single(w) for w in words[:2])
        proper = tuple(v/sum(masses) for v in masses)
        maximum_gap = max(maximum_gap, *(abs(a-b) for a, b in zip(proper, expected.joint)))
        if k >= len(train):
            raw.append(words)
        result = runtime.observe(target)
        if result.status != 'OBSERVED_REFERENCE':
            assert result.status == 'UNRESOLVED'
            return unresolved(runtime, case, result.reason, device_name)
        control.observe(target)
        state = runtime.snapshot().candidates[0].learner.encoded
        check_coordinates(state, control)
        if (k+1) % 63 == 0:
            print(f'PROGRESS {case} {k+1}/376', flush=True)
    snapshot = runtime.snapshot()
    assert snapshot.run.status == 'SEALED_CUDA_STREAM' and not snapshot.run.closure.decisions
    assert snapshot.cursor == 376 and len(snapshot.candidates) == 1 and not snapshot.persistence_identities
    checkpoints['376'] = [model.enclosure(v) for v in control.forecast((0, 0)).rate_posterior]
    statistics = control.statistics()
    # Release complete extra snapshots before the final independently retained
    # phase audit. Their immutable frame payload is already shared, not erased.
    del snapshot, phase
    audit = gate.check_phases(runtime)
    assert (audit['checked_phases'], audit['independent_partition_RNE_predictions'],
            audit['output_words_including_copies'], audit['actual_operation_words'], audit['actual_half_words']) == (1129, 376, 19176, 14664, 752)
    assert audit['table_bytes'] == 264453 and audit['full_literal_native_phases'] == 0
    return {'status': 'COMPLETE_MODEL', 'case': case, 'device': device_name, 'cursor': 376,
        'all_ordinary_native_forecasts_equal_independent_joint': 376,
        'complete_unsigned_count_successor_checks': 376, 'closure': 'SEALED_CUDA_STREAM', 'constructor_decisions': 0,
        'audit': audit, 'independent_control': statistics, 'rate_checkpoint_grid_bits': model.GRID,
        'rate_posterior_checkpoint_intervals': checkpoints,
        'maximum_proper_probability_error': str(maximum_gap), 'evaluation_four_word_readouts': raw}


def unresolved(runtime, case, reason, device):
    snapshot = gate.frames(runtime)
    return {'status': 'UNRESOLVED_RUNTIME', 'case': case, 'device': device, 'cursor': snapshot.cursor,
        'reason': reason, 'retained_phases': len(snapshot.cuda.phases), 'scores': None,
        'packed_peak_bytes': snapshot.resources['peak']['reference_payload_bytes']}


def decode_readout(row):
    assert len(row) == 4 and all(type(w) is int for w in row)
    masses = tuple(amp.single(w) for w in row[:2])
    division = tuple(amp.single(w) for w in row[2:])
    assert min(masses) >= 1 and max(masses) <= 19 and sum(masses) <= 38
    normalizer = round_binary(sum(masses), SINGLE, bit_limit=32768).value
    assert division == tuple(round_binary(v/normalizer, SINGLE, bit_limit=32768).value for v in masses)
    return masses, tuple(v/sum(masses) for v in masses), division


def expected_readout(forecast):
    """Independent unsigned-history integer parts -> four exact RNE words.

    This passive reader uses neither the production partition constructor
    nor its scalar schedule. It does not establish device execution by itself.
    """
    parts = forecast.rate_parts
    scale = 20
    roots = tuple(sum((int(scale*(1-rate))-1)*p[y]+(int(scale*rate)-1)*p[1-y]
                      for rate, p in zip(model.RATES, parts)) for y in (0, 1))
    assert min(roots) > 0 and sum(roots) == (scale-2)*sum(sum(p) for p in parts)
    single = lambda v: round_binary(F(v), SINGLE, bit_limit=32768).value
    half = lambda v: round_binary(F(v), HALF, bit_limit=32768).value
    common = max(v.bit_length() for v in roots)
    scaled = []
    for value in roots:
        bits = value.bit_length()
        power = F(0) if bits-common < -149 else F(1, 1 << (common-bits))
        scaled.append(single(single(half(single(F(value, 1 << bits))))*single(power)))
    denominator = single(sum(scaled))
    masses = tuple(single(1+single((scale-2)*single(v/denominator))) for v in scaled)
    normalizer = single(sum(masses))
    probabilities = tuple(single(v/normalizer) for v in masses)
    return tuple(int.from_bytes(struct.pack('<f', float(v)), 'little') for v in masses+probabilities)


def read_result(result, case):
    assert tuple(result['case']) == case
    if result['status'] == 'UNRESOLVED_RUNTIME':
        assert result['scores'] is None and result['reason']
        return {'status': 'RETAINED_UNRESOLVED_RUNTIME', 'cursor': result['cursor'], 'scores': None}
    assert result['status'] == 'COMPLETE_MODEL' and result['cursor'] == 376
    assert result['closure'] == 'SEALED_CUDA_STREAM' and type(result['constructor_decisions']) is int and result['constructor_decisions'] == 0
    assert result['all_ordinary_native_forecasts_equal_independent_joint'] == result['complete_unsigned_count_successor_checks'] == 376
    hidden, evaluation, joint, known, checkpoints, stats, forecasts = model.replay(case)
    assert result['rate_checkpoint_grid_bits'] == model.GRID
    assert result['rate_posterior_checkpoint_intervals'] == checkpoints and result['independent_control'] == stats
    words = result['evaluation_four_word_readouts']
    assert len(words) == 250
    actual, maximum_gap, maximum_division = {}, F(0), F(0)
    for (i, j, _), row in zip(evaluation, words):
        masses, proper, division = decode_readout(row)
        assert tuple(row) == expected_readout(forecasts[i, j]), 'retained mass/readout words differ from the registered complete RNE schedule'
        # Validate the actual scalar readout exactly, including probability
        # words. The worker separately read every intermediate operation.
        maximum_gap = max(maximum_gap, *(abs(a-b) for a, b in zip(proper, joint[i, j])))
        maximum_division = max(maximum_division, *(abs(a-b) for a, b in zip(proper, division)))
        assert all(abs(20*a-b) <= F(1, 100) for a, b in zip(joint[i, j], masses))
        actual[i, j] = proper
    assert maximum_gap <= F(result['maximum_proper_probability_error']) <= F(1, 1000)
    assert maximum_division <= F(1, 1000)
    audit = result['audit']
    assert (audit['checked_phases'], audit['independent_partition_RNE_predictions'], audit['output_words_including_copies'],
            audit['actual_operation_words'], audit['actual_half_words'], audit['table_bytes']) == (1129, 376, 19176, 14664, 752, 264453)
    assert audit['packed_peak_bytes'] <= PACKED and audit['consumed_arena_bytes'] <= ARENA
    assert audit['largest_encoded_frame_bytes'] < FRAME
    assert set(audit['maximum_relation_errors']) == gate_reader.ERRORS
    for key, value in audit['maximum_relation_errors'].items():
        assert 0 <= F(value) <= (F(1, 1000) if key in ('probability_error', 'division_error') else F(1, 100))
    scores = {}
    groups = (('all_evaluation', tuple((i, j) for i, j, _ in evaluation)),
              ('initial_training_unseen', tuple((i, j) for i, j, _ in evaluation if abs(i-j) == 2)))
    for group, pairs in groups:
        scores[group] = {name: model.score(predictions, hidden, F(case[1]), pairs)
                        for name, predictions in (('owned_joint_AMP', actual), ('exact_joint_unknown_rate', joint), ('oracle_true_rate', known))}
    return {'status': 'PASS_COMPLETE_UNKNOWN_NOISE_MODEL_READER', 'case': case, 'scores': scores,
        'maximum_eval_probability_error': str(maximum_gap), 'maximum_eval_division_error': str(maximum_division),
        'rate_posterior_checkpoint_intervals': checkpoints, 'rate_grid_bits': model.GRID}


def read_completed_job(job, actual, case):
    assert type(job) is JobRun and job.exit_code == 0 and not job.timed_out and not job.limit_terminated_processes
    assert job.attached_before_resume and job.peak_job_commit <= job.commit_limit == CAP
    assert actual['status'] == 'EXECUTED_AND_AUDITED' and actual['process_id'] == job.process_id
    return read_result(actual['result'], case)


def cpu_readers():
    """Exercise raw-word and actual JobRun interfaces before model execution."""
    from itertools import product
    from audit_joint_amp import prediction
    from fp_reference.joint_relation import JointRelation, initialize, observe, commit
    schema = JointRelation(2, model.RATES, model.PRIOR)
    reads = negative = 0
    with memoryview(bytearray(decoder.workspace_bytes(schema, BUDGET))) as scratch:
        for length in range(5):
            for labels in product((0, 1), repeat=length):
                state = initialize(schema, 0)
                control = model.JointControl(2)
                for target in labels:
                    state = commit(observe(state, (0, 1), target))
                    control.predict(0, 1)
                    control.observe(target)
                for pair in ((0, 1), (1, 1)):
                    _, raw, _, _, _ = prediction(state, pair, scratch, BUDGET)
                    words = raw.words[2:4]+raw.words[5:7]
                    decode_readout(words)
                    assert expected_readout(control.forecast(pair)) == words
                    reads += 1
                    for k in (2, 3):
                        altered = list(words)
                        altered[k] ^= 1
                        try:
                            decode_readout(altered)
                        except AssertionError:
                            negative += 1
                        else:
                            raise AssertionError('changed divided word admitted')
    sample = JobRun(0, False, CAP, 1, 1, 0, 0, 1, 0, True, 5, 9)
    actual = {'status': 'EXECUTED_AND_AUDITED', 'process_id': 5,
        'result': {'status': 'UNRESOLVED_RUNTIME', 'case': model.CASES[0],
            'scores': None, 'reason': 'synthetic refusal', 'cursor': 0}}
    assert read_completed_job(sample, actual, model.CASES[0])['scores'] is None
    try:
        read_completed_job(replace(sample, commit_limit=2*CAP), actual, model.CASES[0])
    except AssertionError:
        pass
    else:
        raise AssertionError('changed job cap admitted')
    assert 'torch' not in sys.modules
    return {'status': 'PASS_CPU_MODEL_READERS', 'RNE_readouts': reads, 'changed_probability_words_refused': negative,
        'synthetic_JobRun_interface_and_changed_cap': 'PASS', 'model_scores_computed': 0, 'device_jobs': 0}


def read_report(report):
    assert 'torch' not in sys.modules
    assert report['execution_source'] == EXECUTION_SOURCE
    assert report['status'] in ('COMPLETE_WITH_RETAINED_OUTCOMES', 'STOPPED_EXECUTION_OR_AUDIT_FAILURE')
    assert report['registration'] == json.loads(json.dumps(preflight()))
    declared = [list(case) for case in model.CASES]
    assert [r['case'] for r in report['workers']] == declared[:len(report['workers'])]
    if report['status'] == 'COMPLETE_WITH_RETAINED_OUTCOMES':
        assert len(report['workers']) == len(declared)
    rows = []
    for row in report['workers']:
        case = tuple(row['case'])
        job = JobRun(**row['completed_job'])
        if row['worker_status'] == 'RESOURCE_TERMINATED':
            assert job.timed_out or job.limit_terminated_processes
            rows.append({'case': case, 'status': 'RESOURCE_TERMINATED', 'scores': None})
        elif row['worker_status'] == 'FAILED':
            assert report['status'] == 'STOPPED_EXECUTION_OR_AUDIT_FAILURE'
            rows.append({'case': case, 'status': 'FAILED', 'scores': None})
        else:
            assert row['worker_status'] == row['result']['result']['status']
            checked = read_completed_job(job, row['result'], case)
            assert row['reader'] == json.loads(json.dumps(checked))
            rows.append(checked)
    complete = sum(r['status'] == 'PASS_COMPLETE_UNKNOWN_NOISE_MODEL_READER' for r in rows)
    return {'status': 'PASS_RETAINED_UNKNOWN_NOISE_OUTCOMES', 'execution_source': report['execution_source'],
        'original_status': report['status'], 'unexecuted_cases': declared[len(rows):], 'workers': rows,
        'independent_integer_to_RNE_retained_word_checks': 1000*complete,
        'replay_scope': 'post-execution passive strengthening; original worker and journal unchanged; no device rerun'}


def reader_adversaries(report):
    from copy import deepcopy
    read_report(report)
    actual = report['workers'][0]['result']['result']
    case = tuple(actual['case'])
    altered = deepcopy(actual)
    row = altered['evaluation_four_word_readouts'][0]
    original = list(row)
    row[0] ^= 1
    masses = tuple(amp.single(v) for v in row[:2])
    normalizer = round_binary(sum(masses), SINGLE, bit_limit=32768).value
    row[2:] = [int.from_bytes(struct.pack('<f', float(round_binary(v/normalizer, SINGLE, bit_limit=32768).value)), 'little') for v in masses]
    decode_readout(row)  # The weaker four-word normalization check still passes.
    try:
        read_result(altered, case)
    except AssertionError as exc:
        assert 'complete RNE schedule' in str(exc)
    else:
        raise AssertionError('changed but tolerance-compatible mass row admitted')
    source = deepcopy(report)
    source['execution_source'] = '0'*40
    try:
        read_report(source)
    except AssertionError:
        pass
    else:
        raise AssertionError('foreign source admitted as the declared experiment')
    return {'status': 'PASS_STRICT_RETAINED_READOUT_ADVERSARIES', 'case': case,
        'original_four_words': original, 'altered_four_words': row,
        'self_consistent_altered_divisions_still_pass': True,
        'complete_independent_RNE_replay_refuses': True, 'foreign_execution_source_refused': True,
        'scope': 'artifact-reader boundary; actual source-bound Runtime conformance was already strict; original journal unchanged'}


def execute(attempt):
    assert attempt == 1, 'only the original four-job matrix is registered'
    path = ROOT/'evidence/minimal/FP_UNKNOWN_NOISE_MODEL_A1.json'
    assert not path.exists(), 'never overwrite or retry a terminal attempt'
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES)
    clean()
    report = {'status': 'REGISTERED_NOT_COMPLETED', 'execution_source': source, 'registration': preflight(), 'workers': []}
    def publish():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(path)
    publish()
    directory = Path(tempfile.mkdtemp(prefix='fp-unknown-model-', dir=ROOT)).resolve()
    assert directory.parent == ROOT.resolve()
    stop = False
    for index, case in enumerate(model.CASES):
        output = directory/f'{index}.json'
        row = {'case': case, 'worker_status': 'FAILED'}
        print('START '+str(case), flush=True)
        try:
            clean()
            job = run_in_job(str(Path(__file__).resolve()), ('--worker', index, '--output', output), commit_limit=CAP, timeout_ms=DEADLINE)
            row['completed_job'] = asdict(job)
            if output.exists():
                raw = output.read_bytes()
                assert len(raw) <= 262144
                row['result'] = json.loads(raw)
            report['workers'].append(row)
            publish()
            clean()
            if job.timed_out or job.limit_terminated_processes:
                row['worker_status'] = 'RESOURCE_TERMINATED'
            elif job.exit_code == 0:
                row['reader'] = read_completed_job(job, row['result'], case)
                row['worker_status'] = row['result']['result']['status']
            else:
                stop = True
        except Exception:
            if not any(item is row for item in report['workers']):
                report['workers'].append(row)
            row['collection_traceback'] = traceback.format_exc()
            stop = True
        publish()
        print(row['worker_status']+' '+str(case), flush=True)
        if output.exists():
            assert output.resolve().parent == directory
            output.unlink()
        if stop:
            break
    report['status'] = 'STOPPED_EXECUTION_OR_AUDIT_FAILURE' if stop else 'COMPLETE_WITH_RETAINED_OUTCOMES'
    publish()
    directory.rmdir()
    if stop:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--cpu-readers', action='store_true')
    parser.add_argument('--reader-adversaries', action='store_true')
    parser.add_argument('--attempt', type=int)
    parser.add_argument('--worker', type=int, choices=range(len(model.CASES)))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--read', type=Path)
    args = parser.parse_args()
    if args.worker is not None:
        assert args.output is not None
        result = {'status': 'FAILED_AUDIT', 'process_id': os.getpid(), 'case': model.CASES[args.worker]}
        try:
            result.update(result=worker(model.CASES[args.worker]), status='EXECUTED_AND_AUDITED')
        except Exception:
            result['traceback'] = traceback.format_exc()
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        if result['status'] == 'FAILED_AUDIT':
            raise SystemExit(1)
    elif args.preflight:
        print(json.dumps(preflight(), indent=2))
    elif args.cpu_readers:
        print(json.dumps(cpu_readers(), indent=2))
    elif args.read:
        report = json.loads(args.read.read_text())
        print(json.dumps(reader_adversaries(report) if args.reader_adversaries else read_report(report), indent=2))
    elif args.attempt is not None:
        execute(args.attempt)
    else:
        parser.error('select --preflight, --attempt, --worker or --read')
