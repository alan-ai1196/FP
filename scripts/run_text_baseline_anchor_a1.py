"""Preregistered ordinary-text baseline anchor; no FP or matched-budget claim.

One million real training tokens, full GPT-2 vocabulary, tuned upstream MKN
and a normally optimized Transformer. Original jobs are exclusive and terminal.
Only aggregates belong in Git; selected model artifacts stay outside it.
"""
from dataclasses import asdict
from contextlib import nullcontext
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'experiments/next_token'), str(ROOT/'scripts'),
               str(ROOT/'src/reference_compiler')]
DATA = Path(r'F:\experiment\FP_Scaling_Trial_1R_RTX3090_WindowsGlobal_OneClick\data')
TOOLS = Path(r'F:\experiment\FP_next_token_baselines')
ARTIFACTS = TOOLS/'text_anchor_a1'
JOURNAL = ROOT/'evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json'
VOCAB, TRAIN, TUNE, REPORT, CONTEXT = 50257, 1 << 20, 4096, 16384, 256
SEED, STEPS, BATCH = 29317, 8192, 8
CHECKPOINTS, RATES, ORDERS = (512, 1024, 2048, 4096, 8192), (3e-4, 1e-3), (3, 5)
HOST, GPU_RESERVED = 16 << 30, 22 << 30
DEADLINES = {'ngram': 1800000, 'transformer-0': 7200000,
             'transformer-1': 7200000, 'report': 900000}
GPU_UUID = 'GPU-229f6784-2b41-5313-3f21-e30f26b0bf5c'


def publish(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1 << 20), b''):
            value.update(part)
    return value.hexdigest()


def tape(role, count):
    import numpy as np
    path = DATA/('train.bin' if role == 'train' else 'val.bin')
    expected = 360000000 if role == 'train' else 4000000
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        if before.st_size != expected:
            raise ValueError('registered source extent changed')
        payload = stream.read(2*count)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or len(payload) != 2*count:
        raise ValueError('incomplete or concurrently changed source view')
    values = np.frombuffer(payload, dtype='<u2')
    if np.any(values >= VOCAB):
        raise ValueError('target outside the full declared alphabet')
    return values, dict(path=str(path), file_bytes=expected, byte_offset=0,
        bytes_read=len(payload), prefix_sha256=hashlib.sha256(payload).hexdigest(),
        role='training' if role == 'train' else 'previously_exposed_development',
        whole_file_identity_source='evidence/minimal/FP_NEXT_TOKEN_DATA_ENTRY.json')


def learning_rate(step, maximum):
    if not 0 <= step < STEPS:
        raise ValueError('training attempt outside registration')
    if step < 256:
        return maximum*(step+1)/256
    fraction = (step-256)/(STEPS-1-256)
    return maximum*(0.1+0.9*0.5*(1+math.cos(math.pi*fraction)))


def spec():
    from baselines.transformer import Spec
    return Spec(VOCAB, CONTEXT, 4, 4, 128, 0.1, False)


def device():
    import torch
    torch.set_num_threads(1)
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError('the registered single CUDA device is required')
    properties = torch.cuda.get_device_properties(0)
    if 'GPU-'+str(properties.uuid) != GPU_UUID or torch.cuda.get_device_capability(0) != (8, 6):
        raise RuntimeError('device differs from the registered RTX 3090')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.manual_seed(SEED)
    return dict(name=properties.name, uuid='GPU-'+str(properties.uuid), torch_version=torch.__version__,
        cuda_version=torch.version.cuda, capacity_bytes=properties.total_memory,
        training_precision='float32 parameters and AdamW states; float16 autocast with GradScaler',
        reporting_precision='float16 autocast logits; full-alphabet float64 logsumexp',
        tf32=False, deterministic_kernel_guarantee=False)


def gpu_usage():
    import torch
    torch.cuda.synchronize()
    result = dict(allocated=torch.cuda.memory_allocated(), reserved=torch.cuda.memory_reserved(),
        peak_allocated=torch.cuda.max_memory_allocated(), peak_reserved=torch.cuda.max_memory_reserved())
    if result['peak_reserved'] > GPU_RESERVED:
        raise RuntimeError('registered monitored GPU reservation allowance exceeded')
    return result


def transformer_report(model, values, *, boundary=TUNE):
    """One frozen pass: both sections retain original file context at TUNE."""
    import numpy as np
    import torch
    from baselines.transformer import reporting_inputs, normalized_nll
    if type(boundary) is not int or not 1 <= boundary <= len(values):
        raise ValueError('nonempty tuning prefix within the report required')
    destination = next(model.parameters()).device.type
    model.eval()
    totals, counts = [0., 0.], [0, 0]
    precision = torch.autocast(device_type='cuda', dtype=torch.float16) if destination == 'cuda' else nullcontext()
    with torch.no_grad(), precision:
        for start in range(0, len(values), 32):
            for positions, inputs in reporting_inputs(values, range(start, min(start+32, len(values))),
                                                       model.spec, device=destination):
                logits = model(inputs, last_only=True)
                targets = torch.tensor([int(values[i]) for i in positions], device=destination)
                losses = normalized_nll(logits, targets).cpu().tolist()
                for section in (0, 1):
                    selected = [loss for i, loss in zip(positions, losses) if int(i >= boundary) == section]
                    totals[section] = math.fsum((totals[section], math.fsum(selected)))
                    counts[section] += len(selected)
    assert sum(counts) == len(values) and all(np.isfinite(totals))
    return dict(tuning_tokens=counts[0], tuning_mean_nll_nats=totals[0]/counts[0],
        report_tokens=counts[1], report_mean_nll_nats=(totals[1]/counts[1] if counts[1] else None),
        context_preserved_at_tuning_report_boundary=True)


def train_transformer(case, result, save):
    import numpy as np
    import torch
    from baselines.transformer import Transformer, training_batch
    result['device'] = device()
    training, train_id = tape('train', TRAIN)
    tuning, tune_id = tape('val', TUNE)
    maximum = RATES[int(case[-1])]
    model = Transformer(spec(), seed=SEED).cuda()
    optimizer = model.optimizer(learning_rate=maximum, weight_decay=0.1, betas=(0.9, 0.95))
    scaler = torch.amp.GradScaler('cuda')
    rng = np.random.default_rng(SEED)
    directory = ARTIFACTS/case
    directory.mkdir()
    checkpoint = directory/'best.pt'
    result.update(model=asdict(model.spec), parameters=sum(p.numel() for p in model.parameters()),
        seed=SEED, maximum_learning_rate=maximum, train_source=train_id, tuning_source=tune_id,
        attempted_updates=0, skipped_updates=0, training_targets_per_attempt=BATCH*CONTEXT,
        checkpoints=[], training_windows=[], final_report_suffix_read=False)
    save()
    window_loss, best = [], None
    started = time.perf_counter()
    model.train()
    for step in range(STEPS):
        rate = learning_rate(step, maximum)
        for group in optimizer.param_groups:
            group['lr'] = rate
        starts = rng.integers(-1, len(training)-CONTEXT, size=BATCH)
        inputs, targets = training_batch(training, starts, model.spec, device='cuda')
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type='cuda', dtype=torch.float16):
            loss = model.training_loss(inputs, targets)
        value = float(loss.detach())
        if not math.isfinite(value):
            raise RuntimeError('nonfinite actual training loss')
        old_scale = scaler.get_scale()
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        result['skipped_updates'] += int(scaler.get_scale() < old_scale)
        result['attempted_updates'] = step+1
        window_loss.append(value)
        if (step+1) % 256 == 0:
            result['training_windows'].append(dict(attempt=step+1, mean_nll_nats=math.fsum(window_loss)/len(window_loss),
                learning_rate=rate, scaler_scale=scaler.get_scale()))
            window_loss.clear()
            result['elapsed_training_and_tuning_seconds'] = time.perf_counter()-started
            result['gpu'] = gpu_usage()
            save()
        if step+1 in CHECKPOINTS:
            before = time.perf_counter()
            report = transformer_report(model, tuning)
            row = dict(attempt=step+1, tuning_seconds=time.perf_counter()-before, **report)
            result['checkpoints'].append(row)
            if best is None or row['tuning_mean_nll_nats'] < best['tuning_mean_nll_nats']:
                best = row
                # Only state_dict data, never a pickled model/callable.
                torch.save({key: tensor.detach().cpu().clone() for key, tensor in model.state_dict().items()}, checkpoint)
                result['selected'] = dict(row, artifact=str(checkpoint))
            model.train()
            save()
    if result['skipped_updates'] > STEPS//100:
        raise RuntimeError('over one percent of registered updates skipped by GradScaler')
    result['elapsed_training_and_tuning_seconds'] = time.perf_counter()-started
    result['selected']['sha256'] = digest(checkpoint)
    result['successful_updates'] = STEPS-result['skipped_updates']
    result['training_target_exposures'] = STEPS*BATCH*CONTEXT
    result['selection_rule'] = 'lowest prefix tuning loss; ties keep earlier checkpoint'
    result['gpu'] = gpu_usage()
    result['status'] = 'COMPLETE_TRANSFORMER_TRAINING'


def report_transformer(result, save):
    import torch
    from baselines.transformer import Transformer
    result['device'] = device()
    selection = json.loads((ARTIFACTS/'transformer_selection.json').read_text(encoding='utf-8'))
    checkpoint = Path(selection['artifact'])
    if checkpoint.parent.parent != ARTIFACTS or digest(checkpoint) != selection['sha256']:
        raise RuntimeError('selected artifact identity mismatch')
    model = Transformer(spec(), seed=SEED).cuda()
    model.load_state_dict(torch.load(checkpoint, map_location='cuda', weights_only=True))
    model.requires_grad_(False)
    values, identity = tape('val', REPORT)
    result.update(selected=selection, reporting_source=identity)
    save()
    started = time.perf_counter()
    result['score'] = transformer_report(model, values)
    result['reporting_seconds'] = time.perf_counter()-started
    if abs(result['score']['tuning_mean_nll_nats']-selection['tuning_mean_nll_nats']) > 1e-6:
        raise RuntimeError('selected frozen artifact does not reproduce its tuning score')
    result.update(gpu=gpu_usage(), status='COMPLETE_FROZEN_TRANSFORMER_REPORT')


def external(command, result, save):
    started = time.perf_counter()
    with subprocess.Popen(list(map(str, command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          creationflags=subprocess.CREATE_NO_WINDOW) as process:
        pid = process.pid
        try:
            output, errors = process.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
        row = dict(tool=Path(command[0]).name, pid=pid, exit_code=process.returncode,
            wall_seconds=time.perf_counter()-started)
    result['tools'].append(row)
    save()
    if row['exit_code']:
        raise RuntimeError(row['tool']+': '+errors.decode('utf-8', errors='replace')[-3000:])
    return output


def train_ngram(result, save):
    import numpy as np
    from baselines.ngram import write_training_text
    inventory = json.loads((TOOLS/'installed/x64-windows-static/share/kenlm/vcpkg.spdx.json').read_text(encoding='utf-8'))
    if not inventory['name'].startswith('kenlm:x64-windows-static@20230531#1 '):
        raise RuntimeError('pinned estimator package differs')
    tool_dir = TOOLS/'installed/x64-windows-static/tools/kenlm'
    scorer = TOOLS/'report-build/Release/fp_kenlm_report.exe'
    directory = ARTIFACTS/'ngram'
    directory.mkdir()
    training, train_id = tape('train', TRAIN)
    tuning, tune_id = tape('val', TUNE)
    text_path, score_path = directory/'train.txt', directory/'report.bin'
    with text_path.open('wb') as stream:
        assert write_training_text(training, stream, vocabulary=VOCAB) == TRAIN
    tuning.tofile(score_path)
    result.update(train_source=train_id, tuning_source=tune_id, tools=[], candidates=[],
        estimator='upstream unpruned interpolated modified Kneser-Ney; no discount fallback')
    save()
    for order in ORDERS:
        arpa, binary = directory/f'order{order}.arpa', directory/f'order{order}.trie'
        external((tool_dir/'lmplz.exe', '--order', order, '--memory', '1G', '--vocab_estimate', VOCAB+3,
            '--temp_prefix', str(directory)+'/', '--text', text_path, '--arpa', arpa), result, save)
        external((tool_dir/'build_binary.exe', 'trie', arpa, binary), result, save)
        score = json.loads(external((scorer, binary, score_path, VOCAB, TUNE, CONTEXT), result, save))
        assert (score['status'], score['tokens'], score['vocabulary'], score['order']) == (
            'COMPLETE_FROZEN_KENLM_REPORT', TUNE, VOCAB, order)
        result['candidates'].append(dict(order=order, tuning=score, artifact=str(binary),
            artifact_bytes=binary.stat().st_size))
        save()
    chosen = min(result['candidates'], key=lambda row: (row['tuning']['mean_nll_nats'], row['order']))
    # Unigram is a diagnostic, independently tuned from its declared alphas.
    counts = np.bincount(training.astype(np.int64), minlength=VOCAB)
    unigram = []
    for alpha in (1/16, 1., 16.):
        logp = np.log(counts+alpha)-math.log(TRAIN+VOCAB*alpha)
        unigram.append((float(-logp[tuning].mean(dtype=np.float64)), alpha, logp))
    uni_mean, alpha, logp = min(unigram, key=lambda row: (row[0], row[1]))
    values, report_id = tape('val', REPORT)
    values.tofile(score_path)
    score = json.loads(external((scorer, chosen['artifact'], score_path, VOCAB, REPORT, CONTEXT), result, save))
    assert (score['status'], score['tokens'], score['vocabulary'], score['order']) == (
        'COMPLETE_FROZEN_KENLM_REPORT', REPORT, VOCAB, chosen['order'])
    suffix_mean = (REPORT*score['mean_nll_nats']-TUNE*chosen['tuning']['mean_nll_nats'])/(REPORT-TUNE)
    if not math.isfinite(suffix_mean) or suffix_mean < 0:
        raise RuntimeError('invalid normalized finite report score')
    result.update(selected=dict(chosen, sha256=digest(Path(chosen['artifact']))),
        reporting_source=report_id, full_prefix=score,
        report_tokens=REPORT-TUNE, report_mean_nll_nats=suffix_mean,
        context_preserved_at_tuning_report_boundary=True,
        unigram=dict(alpha=alpha, tuning_mean_nll_nats=uni_mean,
            report_mean_nll_nats=float(-logp[values[TUNE:]].mean(dtype=np.float64))),
        status='COMPLETE_NGRAM_AND_UNIGRAM_REPORT')
    # Keep the selected model, not the intermediate text/ARPA/report tapes.
    for path in (text_path, score_path, *(directory/f'order{o}.arpa' for o in ORDERS),
                 *(directory/f'order{o}.trie' for o in ORDERS if o != chosen['order'])):
        path.unlink()
    assert 'torch' not in sys.modules


def process_identity():
    # Baselines are outside FP's single-process HostResourceContract. Their
    # launcher measures the OS job containing the parent and external tool.
    import ctypes as C
    from ctypes import wintypes as W
    kernel = C.WinDLL('kernel32', use_last_error=True)
    current = kernel.GetCurrentProcess
    current.restype, current.argtypes = W.HANDLE, []
    times = kernel.GetProcessTimes
    times.restype, times.argtypes = W.BOOL, [W.HANDLE]+[C.POINTER(W.FILETIME)]*4
    in_job = kernel.IsProcessInJob
    in_job.restype, in_job.argtypes = W.BOOL, [W.HANDLE, W.HANDLE, C.POINTER(W.BOOL)]
    created, exited, used_kernel, used_user = (W.FILETIME() for _ in range(4))
    belongs = W.BOOL()
    if not times(current(), C.byref(created), C.byref(exited), C.byref(used_kernel), C.byref(used_user)):
        raise C.WinError(C.get_last_error())
    if not in_job(current(), None, C.byref(belongs)) or not belongs.value:
        raise RuntimeError('baseline process is outside its launcher job')
    return dict(process_id=os.getpid(), creation_100ns=created.dwLowDateTime+(created.dwHighDateTime << 32))


def worker(case):
    output = ARTIFACTS/(case+'.json')
    result = dict(status='RUNNING', case=case, before=process_identity())
    save = lambda: publish(output, result)
    save()
    try:
        if case == 'ngram':
            train_ngram(result, save)
        elif case == 'report':
            report_transformer(result, save)
        else:
            train_transformer(case, result, save)
    except Exception as error:
        result.update(status='FAILED', error=type(error).__name__+': '+str(error),
                      traceback=traceback.format_exc()[-4000:])
    result['after'] = process_identity()
    save()
    return 2 if result['status'] == 'FAILED' else 0


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists() or ARTIFACTS.exists():
        raise RuntimeError('original journal/artifact directory exists; never replay')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise RuntimeError('commit registration and execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    ARTIFACTS.mkdir()
    journal = dict(status='RUNNING', source_commit=source, protocol='experiments/next_token/BASELINE_ANCHOR_A1.md',
        artifact_directory=str(ARTIFACTS), train_tokens=TRAIN, tuning_tokens=TUNE,
        report_start=TUNE, report_stop=REPORT, vocabulary=VOCAB, host_job_cap=HOST,
        monitored_gpu_reserved_cap=GPU_RESERVED, cases=list(DEADLINES), results=[])
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        for case, deadline in DEADLINES.items():
            if case == 'report':
                candidates = [row['result']['selected'] | {'case': row['case']}
                              for row in journal['results'] if row['case'].startswith('transformer-')]
                selected = min(candidates, key=lambda row: (row['tuning_mean_nll_nats'], row['case']))
                publish(ARTIFACTS/'transformer_selection.json', selected)
            journal['active_case'] = case
            publish(JOURNAL, journal)
            print('Starting original '+case, flush=True)
            started = time.perf_counter()
            job = run_in_job(__file__, ('--worker', case), commit_limit=HOST, timeout_ms=deadline,
                             process_limit=2 if case == 'ngram' else 1)
            row = dict(case=case, deadline_ms=deadline, active_process_limit=2 if case == 'ngram' else 1,
                job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            path = ARTIFACTS/(case+'.json')
            if path.exists():
                row['result'] = json.loads(path.read_text(encoding='utf-8'))
            journal['results'].append(row)
            value = row.get('result', {})
            accepted = job.exit_code == 0 and not job.timed_out and value.get('status', '').startswith('COMPLETE_')
            row['accepted_execution'] = accepted
            if accepted:
                assert job.attached_before_resume and job.peak_job_commit <= HOST
                for moment in ('before', 'after'):
                    measured = value[moment]
                    assert (measured['process_id'], measured['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                if case.startswith('transformer-'):
                    assert value['attempted_updates'] == STEPS and not value['final_report_suffix_read']
                    assert value['training_target_exposures'] == STEPS*BATCH*CONTEXT
                    assert value['train_source']['prefix_sha256'] == journal['results'][0]['result']['train_source']['prefix_sha256']
                if case == 'report':
                    assert value['score']['report_tokens'] == REPORT-TUNE
                    assert value['reporting_source']['prefix_sha256'] == journal['results'][0]['result']['reporting_source']['prefix_sha256']
            print(case+': '+value.get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not accepted:
                journal['status'] = 'UNRESOLVED_BASELINE_ANCHOR'
                break
        else:
            journal['status'] = 'COMPLETE_TEXT_BASELINE_ANCHOR_A1'
    except Exception as error:
        journal.update(status='FAILED_LAUNCHER', error=type(error).__name__+': '+str(error))
        raise
    finally:
        journal.pop('active_case', None)
        publish(JOURNAL, journal)
    print(journal['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=tuple(DEADLINES))
    args = parser.parse_args()
    if args.worker:
        raise SystemExit(worker(args.worker))
    launch()
