"""Stage-separated CPU cost diagnostic for one existing full-V token event.

Runs the complete Runtime/phase/retention logic with the device, arena and
array substitutions from the snapshot CPU control. This is not a physical
CUDA certificate, a full-unit run or a model-quality experiment.
"""
from pathlib import Path
from dataclasses import asdict
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
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]


def measure(operation):
    profiler = cProfile.Profile()
    start = time.perf_counter()
    result = profiler.runcall(operation)
    elapsed = time.perf_counter()-start
    stats = pstats.Stats(profiler)
    def row(key, value):
        filename, line, function = key
        try:
            filename = str(Path(filename).relative_to(ROOT)).replace('\\', '/')
        except ValueError:
            filename = Path(filename).name
        primitive, calls, own, cumulative, _ = value
        return dict(function=filename+':'+str(line)+':'+function, calls=calls,
                    primitive_calls=primitive, self_seconds=own, cumulative_seconds=cumulative)
    ordered = sorted(stats.stats.items(), key=lambda entry: entry[1][3], reverse=True)
    return result, dict(wall_seconds=elapsed, calls=stats.total_calls, primitive_calls=stats.prim_calls,
                        cumulative_top=[row(k, v) for k, v in ordered[:18]],
                        self_top=[row(k, v) for k, v in sorted(stats.stats.items(), key=lambda e: e[1][2], reverse=True)[:12]])


def worker(output):
    from audit_shared_cuda_retention import full_registration
    from audit_token_snapshot_bounds import cpu_device
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.ingress import encode_context
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    host = _WindowsProcessHost(HostResourceContract(8 << 30, {r: 8 << 30 for r in ('deployment', 'compiler')}))
    result = dict(status='RUNNING', scope=__doc__.strip(), before=measured(host), stages={})
    def save():
        Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        cc, program, online, cfg, storage, _, _, targets, corpus = full_registration()
        result['corpus'] = corpus
        with cpu_device():
            # Separate initialization from steady event work; the earlier
            # combined profile could not identify which stage dominated.
            start = time.perf_counter()
            rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg, shared_storage=storage)
            result['initialization_unprofiled_seconds'] = time.perf_counter()-start
            save()
            outcome, trace = measure(lambda: rt.predict_next('train/0', encode_context(())))
            assert outcome.status == 'PREDICTED_REFERENCE', outcome.reason
            result['stages']['predict'] = trace
            save()
            outcome, trace = measure(lambda: rt.observe(targets[0]))
            assert outcome.status == 'OBSERVED_REFERENCE', outcome.reason
            result['stages']['observe'] = trace
            result.update(status='COMPLETE_CPU_COST_DIAGNOSTIC', retained_phases=len(rt._cuda.phases),
                          cursor=rt.snapshot().cursor)
        assert 'torch' not in sys.modules
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error), traceback=traceback.format_exc()[-4000:])
    result['after'] = measured(host)
    save()
    return 0 if result['status'] == 'COMPLETE_CPU_COST_DIAGNOSTIC' else 2


def launch():
    from windows_job_audit_support import run_in_job
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    destination = ROOT/'evidence/minimal/FP_TOKEN_PHASE_COST_CPU.json'
    if destination.exists():
        raise RuntimeError('existing diagnostic: inspect it before any further measurement')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    with tempfile.TemporaryDirectory(prefix='fp-token-phase-cost-') as temporary:
        output = Path(temporary)/'result.json'
        job = run_in_job(Path(__file__), ('--worker', str(output)), commit_limit=8 << 30, timeout_ms=180000)
        result = dict(implementation_source=source, job=asdict(job))
        if output.exists():
            result['result'] = json.loads(output.read_text(encoding='utf-8'))
        destination.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(job=asdict(job), status=result.get('result', {}).get('status'), artifact=str(destination)), indent=2))
    return job.exit_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--worker')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raise SystemExit(worker(args.worker) if args.worker else launch())
