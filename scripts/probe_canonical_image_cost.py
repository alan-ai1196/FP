"""Paired first-event CPU profiles with/without owned canonical images.

Same full-V model, original training prefix and numerical checks. Each mode
has a fresh bounded Windows job. These are instrumented CPU-substituted costs,
not CUDA throughput or a full-unit result. Existing journals are not replayed.
"""
from dataclasses import asdict, replace
from pathlib import Path
from contextlib import nullcontext
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
CASES = ('uncached', 'owned-images')
JOURNAL = ROOT/'evidence/minimal/FP_CANONICAL_IMAGE_COST_CPU.json'


def worker(case, output):
    from audit_shared_cuda_retention import full_registration
    from audit_canonical_images import without_images
    from audit_token_snapshot_bounds import cpu_device
    from probe_token_phase_cost import measure
    from audit_token_reference_host import measured
    from fp_reference import ReferenceCompilerRuntime, runtime
    from fp_reference.ingress import encode_context
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    host = _WindowsProcessHost(HostResourceContract(8 << 30, {r: 8 << 30 for r in ('deployment', 'compiler')}))
    result = dict(status='RUNNING', case=case, before=measured(host), stages={})
    def save():
        Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        cc, program, online, cfg, storage, _, _, targets, corpus = full_registration()
        storage = replace(storage, canonical_image_bytes=64 << 20)
        result['corpus'] = corpus
        with cpu_device(), (without_images() if case == 'uncached' else nullcontext()), \
                patch.object(runtime.secrets, 'token_hex', return_value='canonical-images-profile'):
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
            images = rt._reference_archive.images
            result.update(status='COMPLETE_CPU_CANONICAL_IMAGE_COST', cursor=rt.snapshot().cursor,
                retained_phases=len(rt._cuda.phases), image_count=0 if images is None else len(images.entries),
                image_bytes=0 if images is None else images.used)
        assert 'torch' not in sys.modules
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error),
                      traceback=traceback.format_exc()[-5000:])
    result['after'] = measured(host)
    save()
    return 0 if result['status'] == 'COMPLETE_CPU_CANONICAL_IMAGE_COST' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('existing paired diagnostic: inspect it; do not replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit the implementation and diagnostic before measurement')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    result = dict(status='RUNNING', source_commit=source, cases=CASES, host_cap=8 << 30,
        deadline_ms=180000, canonical_image_cap=64 << 20, scope=__doc__.strip(), results=[])
    def publish():
        JOURNAL.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    try:
        for case in CASES:
            result['active_case'] = case
            publish()
            with tempfile.TemporaryDirectory(prefix='fp-canonical-image-cost-') as temporary:
                output = Path(temporary)/'result.json'
                job = run_in_job(Path(__file__), ('--worker', case, '--output', output),
                    commit_limit=8 << 30, timeout_ms=180000)
                row = dict(case=case, job=asdict(job))
                if output.exists():
                    row['result'] = json.loads(output.read_text(encoding='utf-8'))
                result['results'].append(row)
                completed = (job.exit_code == 0 and not job.timed_out and
                    row.get('result', {}).get('status') == 'COMPLETE_CPU_CANONICAL_IMAGE_COST')
                if completed:
                    observed = row['result']
                    assert job.attached_before_resume and job.peak_job_commit <= 8 << 30
                    assert (observed['cursor'], observed['retained_phases']) == (1, 3)
                    assert (observed['image_count'] > 0) == (case == 'owned-images')
                    assert 0 <= observed['image_bytes'] <= 64 << 20
                    for mark in ('before', 'after'):
                        value = observed[mark]
                        assert (value['process_id'], value['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                        assert value['job_commit_peak'] <= job.peak_job_commit
                print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
                if not completed:
                    result['status'] = 'FAILED'
                    break
        else:
            result['status'] = 'COMPLETE_PAIRED_CPU_CANONICAL_IMAGE_COST'
    except Exception as error:
        result.update(status='LAUNCHER_FAILED', error=type(error).__name__+': '+str(error))
        raise
    finally:
        result.pop('active_case', None)
        publish()
    return 0 if result['status'] == 'COMPLETE_PAIRED_CPU_CANONICAL_IMAGE_COST' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--worker', choices=CASES)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker and not args.output:
        parser.error('worker requires an output path')
    raise SystemExit(worker(args.worker, args.output) if args.worker else launch())
