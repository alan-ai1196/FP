"""One fixed complete native FP text learner; no CUDA or shortened-horizon score.

The original one-million-token trajectory must finish, followed by the owned
frozen report. A cap/solver failure is UNRESOLVED with no replacement text score.
"""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler'),
               str(ROOT/'experiments/next_token')]
TRAIN, REPORT, SPLIT = 1 << 20, 16384, 4096
HOST, PAYLOAD, OBJECTS, WORK = 96 << 30, 64 << 30, 1 << 26, 1 << 63
DEADLINE = 7200000
ARTIFACTS = Path(r'F:\experiment\FP_next_token_native_a1')
JOURNAL = ROOT/'evidence/minimal/FP_NATIVE_TEXT_A1.json'


def publish(path, value):
    # A deadline may kill the worker while publishing. Retain the preceding
    # complete heartbeat rather than leaving a truncated JSON diagnosis.
    pending = path.with_name(path.name+'.tmp')
    pending.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    pending.replace(path)


def registration():
    from fp_reference import ConstructionContract, OnlineContract
    from fp_reference.data_usage import DataContract, StreamSpec
    from fp_reference.resources import ResourceLimits
    from fp_reference.token_execution import TokenProgram, TokenInitializer, TokenLearner
    from fp_reference.token_sources import TokenAtomFamily, TokenSourceReads
    from fp_reference.token_reporting import TokenReportingContract
    from fp_reference.program import SemanticRules
    from fp_reference.shared_reference import SharedReferenceContract
    from audit_token_reference_host import text_model_fixture
    d, origin = text_model_fixture()  # model factory; opens no corpus
    assert (d.output.labels, d.sources.context, d.width, d.output.features,
            d.output.grid_bits, d.output.learning_rate, d.output.update_unit,
            d.slot_count) == (50257, 512, 4, 8, 16, F(1, 1024), 512, 603092)
    family = TokenAtomFamily(d.sources.vocabulary, d.sources.context)
    pattern = TokenInitializer(family, d.width, d.output, tuple(map(int, origin.E.flat)),
        tuple(map(int, origin.C)), tuple(map(int, origin.W.flat)), 1 << 24)
    program = TokenProgram(d)
    rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
    caps = {'reference_payload_bytes': PAYLOAD, 'physical_objects': OBJECTS}
    limits = ResourceLimits(caps, {role: caps for role in ('compiler', 'deployment')},
        {role: {'work': WORK} for role in ('compiler', 'deployment')})
    cc = ConstructionContract(rules, limits, {'construct': 'compiler', 'range_audit': 'compiler'},
        program.counts(), pattern, normalizer_cap=F(1 << 96), activation_cap=F(1 << 80),
        reference_integer_bits=32768)
    data = DataContract((
        StreamSpec('train', 'train', tuple(f'train/{i}' for i in range(TRAIN))),
        StreamSpec('report', 'validation', tuple(f'report/{i}' for i in range(REPORT)))),
        'train', (), TokenSourceReads(family))
    online = OnlineContract(data, TokenLearner(d.output))
    storage = SharedReferenceContract(64 << 20, 16 << 20, 128 << 20, 8 << 20, 1 << 30,
        canonical_image_bytes=8 << 30, token_invariant_bytes=4 << 20)
    reporting = TokenReportingContract('report', 16, 40)
    return cc, program, online, storage, reporting


def suffix_interval(final, prefix, count, bits):
    """Subtract exact *matching integer accumulators*, not unknown intervals."""
    if type(count) is not int or count <= 0 or len(final) != 2 or len(prefix) != 2:
        raise ValueError('two cumulative endpoints and a nonempty suffix required')
    totals = tuple(a-b for a, b in zip(final, prefix))
    if not 0 <= totals[0] <= totals[1]:
        raise ValueError('inconsistent directed suffix accumulators')
    return tuple(F(value, (1 << bits)*count) for value in totals)


def model_state(runtime):
    return runtime._candidates[runtime._deployed_id].learner


def progress(runtime, *, label, started):
    """Passive counters only; no source/gradient setter or resource authority."""
    state, ledger = model_state(runtime), runtime._ledger
    return dict(label=label, elapsed_seconds=time.perf_counter()-started,
        completed_training_targets=runtime._cursor, revealed_training_targets=len(runtime._observations),
        optimizer_steps=state.optimizer_steps, pending_targets=state.unit_count,
        event_traces=len(runtime._event_traces), live_objects=len(ledger._objects),
        retired_objects=len(ledger._retired), resource_events=len(ledger._events),
        paid_payload_peak=ledger._peak['reference_payload_bytes'],
        object_peak=ledger._peak['physical_objects'],
        spent={role: dict(values) for role, values in ledger._spent.items()},
        halted=runtime._halted)


def complete_residency(runtime):
    """Inspect every current buffer/lease without allocating a giant snapshot."""
    ledger = runtime._ledger
    assert len(ledger._objects) == len(runtime._buffers)
    assert all(key in runtime._buffers for key in ledger._objects)
    total, roles = ledger._residency(ledger._objects, ledger._refs)
    assert total['reference_payload_bytes'] == sum(map(len, runtime._buffers.values()))
    assert total['physical_objects'] == len(runtime._buffers)
    for candidate in runtime._candidates.values():
        assert all(candidate.physical_owner in ledger._refs[key] for key in candidate.object_ids)
    return dict(current=total, role_current=roles, peak=dict(ledger._peak),
        role_peak={role: dict(value) for role, value in ledger._role_peak.items()},
        every_current_buffer_and_lease_inspected=True)


def worker():
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.ingress import encode_context
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    from run_text_baseline_anchor_a1 import tape, digest
    host_contract = HostResourceContract(HOST, {role: HOST for role in ('compiler', 'deployment')})
    host = _WindowsProcessHost(host_contract)
    result = dict(status='RUNNING', before=measured(host), checkpoints=[],
        reporting_opened=False, model_score=None, actual_amp_execution=False)
    output = ARTIFACTS/'worker.json'
    save = lambda: publish(output, result)
    started = time.perf_counter()
    runtime = None
    save()
    try:
        training, identity = tape('train', TRAIN)
        anchor = json.loads((ROOT/'evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json').read_text(encoding='utf-8'))
        assert anchor['status'] == 'COMPLETE_TEXT_BASELINE_ANCHOR_A1'
        assert identity['prefix_sha256'] == anchor['results'][0]['result']['train_source']['prefix_sha256']
        result['training_source'] = identity
        save()
        cc, program, online, storage, reporting = registration()
        result['model'] = dict(program_id=program.program_id, native_counts=program.counts(),
            vocabulary=50257, context=512, width=4, features=8, parameters=603092,
            grid_bits=16, learning_rate='1/1024', update_unit=512,
            initializer='unchanged deterministic text_model_fixture at the registered source',
            activation_cap=str(cc.activation_cap), normalizer_cap=str(cc.normalizer_cap))
        save()
        runtime = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
            reporting=reporting, host=host_contract)
        result['checkpoints'].append(progress(runtime, label='initialized', started=started))
        save()
        for index, target in enumerate(training):
            predicted = runtime.predict_next(f'train/{index}', encode_context(()))
            if predicted.status != 'PREDICTED_REFERENCE':
                raise RuntimeError(predicted.status+': '+predicted.reason)
            observed = runtime.observe(int(target))
            if observed.status != 'OBSERVED_REFERENCE':
                result.update(status='UNRESOLVED_NATIVE_TEXT_A1', reason=observed.reason)
                break
            if index+1 in (1, 16, 128) or (index+1) % 256 == 0:
                # Preserve only logarithmic milestones; keep a separate latest
                # heartbeat for bounded-run diagnosis without huge event logs.
                mark = progress(runtime, label=f'train/{index+1}', started=started)
                result['latest'] = mark
                if (index+1) & index == 0:
                    result['checkpoints'].append(mark)
                save()
        else:
            frozen = model_state(runtime)
            assert frozen.cursor == TRAIN and frozen.unit_count == 0 and frozen.optimizer_steps == TRAIN//512
            assert len(runtime._observations) == len(runtime._event_traces) == TRAIN
            assert all(record.target == int(training[i]) and record.cursor == i
                       for i, record in enumerate(runtime._observations))
            assert runtime.begin_report().status == 'REPORTING'
            values, identity = tape('val', REPORT)
            assert identity['prefix_sha256'] == anchor['results'][0]['result']['reporting_source']['prefix_sha256']
            result.update(reporting_source=identity, reporting_opened=True,
                completed_training=progress(runtime, label='trained', started=started))
            save()
            prefix = None
            for index, target in enumerate(values):
                forecast = runtime.predict_report(f'report/{index}')
                if forecast.status != 'PREDICTED_REPORT':
                    raise RuntimeError(forecast.status+': '+forecast.reason)
                scored = runtime.observe_report(int(target))
                if scored.status != ('COMPLETE_REPORT' if index+1 == REPORT else 'SCORED_REPORT'):
                    result.update(status='UNRESOLVED_NATIVE_TEXT_A1', reason=scored.reason)
                    break
                assert model_state(runtime) is frozen
                if index+1 == SPLIT:
                    prefix = tuple(runtime._token_report.native_total)
                if (index+1) % 256 == 0:
                    result['completed_reporting_targets'] = index+1
                    save()
            else:
                complete = runtime.report_result()
                assert complete.status == 'COMPLETE_REPORT' and complete.physical_mean is None
                assert prefix is not None and len(runtime._token_report.events) == REPORT
                bounds = suffix_interval(runtime._token_report.native_total, prefix, REPORT-SPLIT,
                    reporting.accumulator_bits)
                # Frozen masters are an external audit artifact, not a complete
                # Runtime checkpoint or authority to resume/install this run.
                model = ARTIFACTS/'native_masters.bin'
                model.write_bytes(frozen.origin.embedding+frozen.origin.core+frozen.origin.output)
                result.update(status='COMPLETE_NATIVE_TEXT_A1',
                    model_score=dict(report_start=SPLIT, report_stop=REPORT, tokens=REPORT-SPLIT,
                        native_mean_lower=str(bounds[0]), native_mean_upper=str(bounds[1]),
                        approximate_mean_lower=float(bounds[0]), approximate_mean_upper=float(bounds[1]),
                        full_prefix_native_mean=[str(complete.native_mean.lower), str(complete.native_mean.upper)],
                        frozen_native_identity_unchanged=True, physical_mean=None),
                    model_artifact=dict(path=str(model), bytes=model.stat().st_size, sha256=digest(model),
                        encoding='concatenated native uint32 E,C,W arrays; not a resumable Runtime'),
                    resources=complete_residency(runtime))
        if runtime is not None:
            result['latest'] = progress(runtime, label='worker-terminal', started=started)
            if result['status'] != 'COMPLETE_NATIVE_TEXT_A1':
                result['failure_context'] = dict(event_phase=runtime._event_phase,
                    last_revealed_target=(runtime._observations[-1].target if runtime._observations else None),
                    last_observation_id=(runtime._observations[-1].observation_id if runtime._observations else None))
        assert 'torch' not in sys.modules
    except Exception as error:
        result.update(status='UNRESOLVED_NATIVE_TEXT_A1', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-4000:], model_score=None)
        if runtime is not None:
            result['latest'] = progress(runtime, label='exception', started=started)
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    save()
    return 0 if result['status'] == 'COMPLETE_NATIVE_TEXT_A1' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists() or ARTIFACTS.exists():
        raise RuntimeError('original journal or artifact directory exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit the model/protocol/runner before the original launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    ARTIFACTS.mkdir()
    journal = dict(status='RUNNING', source_commit=source,
        protocol='experiments/next_token/NATIVE_TEXT_A1.md',
        host_job_cap=HOST, deadline_ms=DEADLINE, training_horizon=TRAIN, report_horizon=REPORT,
        suffix_start=SPLIT, artifact_directory=str(ARTIFACTS),
        scope='complete native Runtime training/reporting; no AMP result or shortened-horizon score')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        started = time.perf_counter()
        run = run_in_job(__file__, ('--worker',), commit_limit=HOST, timeout_ms=DEADLINE)
        journal.update(job=asdict(run), launch_wall_seconds=time.perf_counter()-started)
        output = ARTIFACTS/'worker.json'
        if output.exists():
            journal['result'] = json.loads(output.read_text(encoding='utf-8'))
        result = journal.get('result', {})
        accepted = run.exit_code == 0 and not run.timed_out and result.get('status') == 'COMPLETE_NATIVE_TEXT_A1'
        journal['accepted_execution'] = accepted
        assert run.attached_before_resume and run.peak_job_commit <= HOST
        for moment in ('before', 'after'):
            if moment in result:
                observation = result[moment]
                assert (observation['process_id'], observation['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                assert observation['job_commit_peak'] <= run.peak_job_commit
                assert observation['lifetime_process_commit_peak'] <= run.peak_process_commit
        if accepted:
            assert result['completed_training']['completed_training_targets'] == TRAIN
            assert result['completed_reporting_targets'] == REPORT and result['model_score']['tokens'] == REPORT-SPLIT
            assert result['model_score']['physical_mean'] is None and not result['actual_amp_execution']
        journal['status'] = 'COMPLETE_NATIVE_TEXT_A1' if accepted else 'UNRESOLVED_NATIVE_TEXT_A1'
        if run.timed_out:
            journal['termination'] = 'OS timeout; worker heartbeat is only the last reported completed prefix'
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', reason=type(error).__name__+': '+str(error))
        raise
    finally:
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        raise SystemExit(worker())
    launch()
