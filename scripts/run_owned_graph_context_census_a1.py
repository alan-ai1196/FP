"""One passive exact census for the original full ordinary-text host lower.

Read only the registered training prefix. No learner, Runtime execution,
validation view, GPU, predictive score or throughput comparison is involved.
"""
from collections import Counter
from dataclasses import asdict
from itertools import product
from pathlib import Path
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
TRAIN, CONTEXT, UNIT, VOCAB, MASTERS, NODES, REPORT = 1 << 20, 512, 512, 50257, 603092, 8, 16384
HOST, DEADLINE, ORIGINAL_HOST = 4 << 30, 180000, 96 << 30
JOURNAL = ROOT/'evidence/minimal/FP_OWNED_GRAPH_CONTEXT_CENSUS_A1.json'
CPU = ROOT/'evidence/minimal/FP_OWNED_GRAPH_CONTEXT_CENSUS_CPU.json'
PROTOCOL = 'experiments/next_token/OWNED_GRAPH_CONTEXT_CENSUS_A1.md'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def publish(path, value):
    pending = path.with_name(path.name+'.tmp')
    pending.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    pending.replace(path)


def census(tokens, context, vocabulary):
    """Full byte equality determines distinctness; hashes are only set indices."""
    import numpy as np
    assert type(context) is int and context > 0 and 0 < vocabulary < 65536
    assert tokens.ndim == 1 and tokens.dtype == np.dtype('<u2')
    assert len(tokens) > 0 and np.all(tokens < vocabulary)
    assert len(tokens)*context < 1 << 63
    padded = np.concatenate((np.full(context, vocabulary, dtype='<u2'), tokens))
    raw, distinct = memoryview(padded).cast('B'), set()
    difference = np.zeros(len(padded)+1, dtype=np.int64)
    count = 0
    for position in range(len(tokens)):
        # Runtime uses reverse lag order. Reversal preserves equality and
        # every token multiplicity, so chronological byte strings suffice.
        key = raw[2*position:2*(position+context)].tobytes()
        distinct.add(key)
        if len(distinct) != count:
            count += 1
            difference[position] += 1
            difference[position+context] -= 1
    weights = np.cumsum(difference[:-1], dtype=np.int64)
    counts = np.zeros(vocabulary+1, dtype=np.int64)
    np.add.at(counts, padded, weights)
    assert np.all(weights >= 0) and int(counts.sum()) == count*context
    return count, counts


def non_small_lower(counts, cached_ids=257):
    # Distinct labels have distinct scalar-node IDs. Even an adversarial
    # allocation can put at most cached_ids labels into those small IDs.
    largest = sum(sorted(map(int, counts), reverse=True)[:cached_ids])
    total = sum(map(int, counts))
    return total-largest, largest


def cpu_controls():
    import numpy as np
    from audit_owned_graph_host_bound import abi
    layout, cases = abi(), 0
    # Compare exact full context tuples and a direct Counter oracle, not a
    # second byte-set/difference-array implementation.
    for size in range(1, 7):
        for word in product(range(3), repeat=size):
            for context in (1, 2, 3, 8):
                d, counts = census(np.array(word, dtype='<u2'), context, 3)
                contexts = {tuple(3 if lag > t else word[t-lag]
                    for lag in range(1, context+1)) for t in range(size)}
                oracle = Counter(label for past in contexts for label in past)
                assert d == len(contexts)
                assert list(map(int, counts)) == [oracle[label] for label in range(4)]
                # All adversarial choices of two cache-resident label IDs.
                from itertools import combinations
                bound, largest = non_small_lower(counts, 2)
                assert bound == min(sum(n for label, n in oracle.items() if label not in cached)
                    for cached in combinations(range(4), 2))
                assert bound+largest == d*context
                cases += 1
    assert abi() == layout and 'torch' not in sys.modules
    return dict(status='PASS_OWNED_GRAPH_CONTEXT_CENSUS_CPU', abi=layout,
        exhaustive_cases=cases, independent_tuple_and_counter_oracle=True,
        adversarial_small_id_assignment_oracle=True, corpus_accessed=False)


def worker(output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    from audit_owned_graph_host_bound import abi, lower
    from run_text_baseline_anchor_a1 import tape
    host = _WindowsProcessHost(HostResourceContract(HOST, {r: HOST for r in ('compiler', 'deployment')}))
    started = time.perf_counter()
    result = dict(status='RUNNING', before=measured(host))
    publish(output, result)
    try:
        layout = abi()
        tokens, identity = tape('train', TRAIN)
        anchor = json.loads((ROOT/'evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json').read_text(encoding='utf-8'))
        assert anchor['status'] == 'COMPLETE_TEXT_BASELINE_ANCHOR_A1'
        assert identity == anchor['results'][0]['result']['train_source']
        d, counts = census(tokens, CONTEXT, VOCAB)
        non_small, largest = non_small_lower(counts)
        terms = lower(TRAIN, UNIT, CONTEXT, MASTERS, NODES, REPORT, d, non_small)
        assert abi() == layout and 'torch' not in sys.modules
        selected = sum(terms.values())
        result.update(status='PASS_EXACT_CONTEXT_CENSUS', abi=layout, training_source=identity,
            distinct_contexts=d, distinct_context_token_occurrences=d*CONTEXT,
            largest_257_label_multiplicities_sum=largest,
            non_small_context_reference_lower=non_small,
            selected_disjoint_host_lower_terms=terms, selected_disjoint_host_lower_bytes=selected,
            original_host_cap=ORIGINAL_HOST,
            unchanged_graph_host_excluded=selected > ORIGINAL_HOST,
            host_decision='EXCLUDED' if selected > ORIGINAL_HOST else 'UNRESOLVED',
            qualification_node_cap_assumed_relaxed=True,
            validation_accessed=False, runtime_or_learner_constructed=False,
            model_result=False)
    except Exception as error:
        result.update(status='UNRESOLVED', reason=type(error).__name__+': '+str(error),
            traceback=traceback.format_exc()[-5000:])
    result.update(after=measured(host), worker_wall_seconds=time.perf_counter()-started)
    publish(output, result)
    return 0 if result['status'] == 'PASS_EXACT_CONTEXT_CENSUS' else 2


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('original census journal exists; never replay')
    if git('status', '--porcelain'):
        raise RuntimeError('commit census inputs and CPU controls before launch')
    source = git('rev-parse', 'HEAD')
    assert json.loads(CPU.read_text(encoding='utf-8'))['status'] == 'PASS_OWNED_GRAPH_CONTEXT_CENSUS_CPU'
    host_cpu = json.loads((ROOT/'evidence/minimal/FP_OWNED_GRAPH_HOST_BOUND_CPU.json').read_text(encoding='utf-8'))
    assert host_cpu['status'] == 'PASS_OWNED_GRAPH_HOST_BOUND_CPU' and host_cpu['all_lower_terms_checked']
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, protocol=PROTOCOL,
        scope=__doc__.strip(), host_cap=HOST, deadline_ms=DEADLINE,
        original_training_horizon=TRAIN, context=CONTEXT, original_host_cap=ORIGINAL_HOST)
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    try:
        with tempfile.TemporaryDirectory(prefix='fp-graph-context-census-') as directory:
            output = Path(directory)/'worker.json'
            started = time.perf_counter()
            job = run_in_job(__file__, ('--worker', '--output', output), commit_limit=HOST, timeout_ms=DEADLINE)
            journal.update(job=asdict(job), launch_wall_seconds=time.perf_counter()-started)
            if output.exists():
                raw = output.read_bytes()
                if len(raw) > 32768:
                    raise RuntimeError('unexpected oversized census receipt')
                journal['result'] = json.loads(raw)
            result = journal.get('result', {})
            accepted = job.exit_code == 0 and not job.timed_out and result.get('status') == 'PASS_EXACT_CONTEXT_CENSUS'
            if accepted:
                assert job.attached_before_resume and job.peak_job_commit <= HOST
                for moment in ('before', 'after'):
                    sample = result[moment]
                    assert (sample['process_id'], sample['creation_100ns']) == (job.process_id, job.process_creation_100ns)
                    assert sample['job_commit_peak'] <= job.peak_job_commit
                    assert sample['lifetime_process_commit_peak'] <= job.peak_process_commit
                assert sum(result['selected_disjoint_host_lower_terms'].values()) == result['selected_disjoint_host_lower_bytes']
            journal.update(status='COMPLETE_OWNED_GRAPH_CONTEXT_CENSUS_A1' if accepted else 'UNRESOLVED_OWNED_GRAPH_CONTEXT_CENSUS_A1',
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
        result = cpu_controls()
        target = args.output or CPU
        with target.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
        print(result['status'], flush=True)
    elif args.worker:
        if args.output is None:
            parser.error('worker output is required')
        raise SystemExit(worker(args.output))
    else:
        launch()
