"""CPU reporting-boundary and Windows child-job controls; no real text/GPU."""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import math
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]


def job_worker(limit, output):
    from run_text_baseline_anchor_a1 import process_identity
    result = dict(process=process_identity(), active_limit=limit)
    try:
        child = subprocess.run([sys.executable, '-B', '-c', 'raise SystemExit(0)'],
            creationflags=subprocess.CREATE_NO_WINDOW, timeout=15)
    except OSError:
        assert limit == 1
        result['child'] = 'REFUSED'
    else:
        assert limit == 2 and child.returncode == 0
        result['child'] = 'COMPLETED'
    Path(output).write_text(json.dumps(result), encoding='utf-8')


def audit():
    import numpy as np
    import torch
    from baselines.transformer import Spec, Transformer, report, reporting_inputs, normalized_nll
    from run_text_baseline_anchor_a1 import transformer_report, learning_rate, STEPS, RATES
    from windows_job_audit_support import run_in_job
    torch.set_num_threads(1)
    model = Transformer(Spec(11, 4, 2, 2, 8, 0.1, False), seed=173).double()
    values = np.asarray([i*i % 11 for i in range(21)], dtype='<u2')
    before = {name: tensor.clone() for name, tensor in model.state_dict().items()}
    whole = report(model, values, batch_size=3)
    maximum_error = 0.
    for boundary in (1, 4, 13, 21):
        result = transformer_report(model, values, boundary=boundary)
        prefix = report(model, values[:boundary], batch_size=2)
        assert result['tuning_tokens'] == boundary and result['report_tokens'] == len(values)-boundary
        assert abs(prefix['mean_nll_nats']-result['tuning_mean_nll_nats']) < 1e-14
        if boundary < len(values):
            # Independent direct suffix traversal, still using the full tape.
            losses = []
            with torch.no_grad():
                for positions, inputs in reporting_inputs(values, range(boundary, len(values)), model.spec):
                    logits = model(inputs, last_only=True)
                    targets = torch.tensor([int(values[i]) for i in positions])
                    losses.extend(normalized_nll(logits, targets).tolist())
            error = abs(math.fsum(losses)/len(losses)-result['report_mean_nll_nats'])
            maximum_error = max(maximum_error, error)
            assert error < 1e-14
            combined = (boundary*result['tuning_mean_nll_nats']+(len(values)-boundary)*result['report_mean_nll_nats'])/len(values)
            assert abs(combined-whole['mean_nll_nats']) < 1e-14
    assert all(torch.equal(value, model.state_dict()[name]) for name, value in before.items())
    reset = report(model, values[13:], batch_size=4)['mean_nll_nats']
    preserved = transformer_report(model, values, boundary=13)['report_mean_nll_nats']
    assert abs(reset-preserved) > 1e-8
    for maximum in RATES:
        rates = [learning_rate(step, maximum) for step in range(STEPS)]
        assert rates[0] == maximum/256 and rates[255] == maximum and rates[256] == maximum
        assert abs(rates[-1]-0.1*maximum) < 1e-18
        assert all(a <= b for a, b in zip(rates[:255], rates[1:256]))
        assert all(a >= b for a, b in zip(rates[256:-1], rates[257:]))
    jobs = []
    with tempfile.TemporaryDirectory(prefix='fp-baseline-job-control-') as temporary:
        for limit in (1, 2):
            output = Path(temporary)/f'{limit}.json'
            job = run_in_job(__file__, ('--job-worker', limit, '--output', output),
                commit_limit=256 << 20, timeout_ms=30000, process_limit=limit)
            assert job.exit_code == 0 and not job.timed_out and job.attached_before_resume
            result = json.loads(output.read_text(encoding='utf-8'))
            assert (result['process']['process_id'], result['process']['creation_100ns']) == (job.process_id, job.process_creation_100ns)
            assert job.peak_job_commit <= 256 << 20
            jobs.append(dict(job=asdict(job), result=result))
    assert not torch.cuda.is_initialized()
    result = dict(status='PASS_TEXT_BASELINE_ANCHOR_CONTROL', reporting_boundaries=[1, 4, 13, 21],
        original_context_suffix_checked=True, maximum_float64_suffix_error=maximum_error,
        context_reset_changes_loss=abs(reset-preserved), frozen_parameters_unchanged=True,
        complete_registered_learning_rate_schedules_checked=True, jobs=jobs,
        corpus_opened=False, cuda_initialized=False)
    (ROOT/'evidence/minimal/FP_TEXT_BASELINE_ANCHOR_CONTROL.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job-worker', type=int, choices=(1, 2))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.job_worker:
        job_worker(args.job_worker, args.output)
    else:
        audit()
