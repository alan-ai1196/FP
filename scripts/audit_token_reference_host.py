"""Preregistered single-attempt CPU feasibility jobs for complete token units.

The parent never imports numerical packages. Each child starts suspended,
joins its fixed Windows job, then resumes. This is a numerical/resource
audit, not an owned Compiler run or a language-model score.
"""
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
CAP, DEADLINE, ELEMENT_CAP = 2 << 30, 180000, 1 << 24
CASES = ('rational-control', 'train-context512')
JOURNAL = ROOT/'evidence/minimal/FP_TOKEN_REFERENCE_HOST_A1.json'
TRAIN = Path('F:/experiment/FP_Scaling_Trial_1R_RTX3090_WindowsGlobal_OneClick/data/train.bin')


def timed(times, name, operation):
    start = time.perf_counter()
    try:
        return operation()
    finally:
        times[name] = time.perf_counter()-start


def measured(host):
    value = host.observe()
    return {name: getattr(value, name) for name in (
        'process_id', 'creation_100ns', 'process_commit', 'lifetime_process_commit_peak', 'job_commit_peak',
        'process_user_100ns', 'process_kernel_100ns', 'job_user_100ns', 'job_kernel_100ns', 'total_job_processes')}


def control(times):
    import batched_tokens as batch
    import enclosed_tokens as scalar
    from audit_enclosed_tokens import long_unit_fixture
    from audit_batched_tokens import same_endpoint
    d, root, targets = timed(times, 'fixture', long_unit_fixture)
    windows = timed(times, 'source_windows', lambda: tuple(d.sources.window(targets, i) for i in range(len(targets))))
    origin = timed(times, 'pack_origin', lambda: batch.Origin.from_native(root, element_cap=ELEMENT_CAP))
    kernel = timed(times, 'kernel_compile', lambda: batch.Kernel(d, element_cap=ELEMENT_CAP))
    bounds = timed(times, 'batch_bound', lambda: kernel.bound(origin, windows, targets))
    endpoint = timed(times, 'batch_commit', bounds.commit)

    def scalar_path():
        state = scalar.begin(root)
        for window, target in zip(windows, targets):
            state = state.observe(state.predict(window), target, window=window)
        return state.commit()
    scalar_endpoint = timed(times, 'scalar_enclosure_unit_and_commit', scalar_path)
    timed(times, 'compare_scalar_endpoint', lambda: same_endpoint(endpoint, scalar_endpoint))

    def exact_path():
        state = root
        for event, (window, target) in enumerate(zip(windows, targets)):
            prediction = state.predict(window)
            assert all(bounds.values.scalar((i, event)).contains(v) for i, v in enumerate(prediction.values))
            assert bounds.normalizer.scalar(event).contains(prediction.output.normalizer)
            assert bounds.target_mass.scalar(event).contains(prediction.output.mass(target))
            state = state.observe(prediction, target, window=window)
        return state
    exact = timed(times, 'rational_unit_with_forward_checks', exact_path)
    timed(times, 'compare_complete_gradient_basis', lambda: compare_basis(bounds, exact))
    exact_endpoint = timed(times, 'rational_commit', exact.commit)
    timed(times, 'compare_rational_endpoint', lambda: same_endpoint(endpoint, exact_endpoint))
    return dict(status='RESOLVED_EXACT_CONTROL', vocabulary=d.output.labels, context=d.sources.context,
        unit=d.output.update_unit, endpoint_parameters=d.slot_count,
        maximum_common_denominator_bits=max(g.denominator.bit_length() for g in exact.output.common),
        full_gradient_basis_checked=True, scalar_and_rational_endpoints_equal=True,
        master_payload_bytes=len(endpoint.embedding)+len(endpoint.core)+len(endpoint.output))


def compare_basis(bounds, exact):
    d = exact.definition
    embedding = dict(exact.embedding_gradient)
    assert tuple(sorted({i//d.width for i in embedding})) == tuple(bounds.embedding_ids)
    for row, token in enumerate(bounds.embedding_ids):
        for k in range(d.width):
            assert bounds.embedding.scalar((row, k)).contains(embedding[int(token)*d.width+k])
    assert all(bounds.core.scalar(i).contains(g) for i, g in enumerate(exact.core_gradient))
    assert all(bounds.common.scalar(i).contains(g) for i, g in enumerate(exact.output.common))
    corrections = dict(exact.output.corrections)
    assert tuple(corrections) == tuple(bounds.correction_ids)
    for row, token in enumerate(bounds.correction_ids):
        assert all(bounds.corrections.scalar((row, k)).contains(g) for k, g in enumerate(corrections[int(token)]))


def text_model_fixture():
    """The existing resource-test model, without reading any corpus bytes."""
    from fractions import Fraction as F
    import numpy as np
    import batched_tokens as batch
    import native_tokens as tokens
    import native_readout as readout
    from causal_tokens import TokenSources, TokenWindow
    from fp_reference.program import Sum, Product, Term
    V, L, D, N, K = 50257, 512, 4, 512, 8
    schema = TokenSources(V, L)
    nodes = tuple(Sum('f', tuple(Term(l*D+k, k) for l in range(L))) for k in range(D))
    nodes += tuple(Product('f', L*D+k, (k+1) % D) for k in range(D))
    definition = tokens.Definition(schema, D, nodes, D, tuple(range(L*D, L*D+K)),
        readout.Spec((F(1, V),)*V, K, 16, F(1, 1024), N))
    row, channel = np.arange(V+1, dtype=np.uint64)[:, None], np.arange(D, dtype=np.uint64)[None, :]
    E = 8192+((row+1)*(7919+2*channel)+104729*channel) % 49151
    row, feature = np.arange(V, dtype=np.uint64)[:, None], np.arange(K, dtype=np.uint64)[None, :]
    W = 1+(row*(2*feature+1)+17*feature) % 7
    origin = batch.Origin(definition, batch.words(E), batch.words((128,)*D), batch.words(W), 0, 0,
        TokenWindow(schema, 0, (V,)*L))
    return definition, origin


def text_fixture():
    import numpy as np
    definition, origin = text_model_fixture()
    schema = definition.sources
    V, N = schema.vocabulary, definition.output.update_unit
    # Read only the already registered training prefix. Exact bytes actually
    # used are identified once; do not rehash the 360 MB corpus ceremonially.
    with TRAIN.open('rb') as stream:
        before = os.fstat(stream.fileno())
        if before.st_size != 360000000:
            raise ValueError('registered training corpus length changed')
        payload = stream.read(2*N)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or len(payload) != 2*N:
        raise ValueError('incomplete or concurrently changed training prefix')
    targets = tuple(map(int, np.frombuffer(payload, dtype='<u2')))
    if not all(0 <= y < V for y in targets):
        raise ValueError('undeclared target in training prefix')
    windows = tuple(schema.window(targets, i) for i in range(N))
    identity = dict(role='historical-training', path=str(TRAIN), file_bytes=before.st_size,
        byte_offset=0, bytes_read=len(payload), prefix_sha256=hashlib.sha256(payload).hexdigest(),
        corpus_identity_source='evidence/minimal/FP_NEXT_TOKEN_DATA_ENTRY.json',
        validation_or_test_read=False)
    return definition, origin, windows, targets, identity


def text_case(times):
    import batched_tokens as batch
    from enclosed_tokens import EnclosureUnresolved
    d, origin, windows, targets, identity = timed(times, 'fixture_and_training_read', text_fixture)
    kernel = timed(times, 'kernel_compile', lambda: batch.Kernel(d, element_cap=ELEMENT_CAP))
    try:
        bounds = timed(times, 'batch_bound', lambda: kernel.bound(origin, windows, targets))
        endpoint = timed(times, 'batch_commit', bounds.commit)
    except EnclosureUnresolved as error:
        unit = error.retained_unit
        assert unit.origin is origin and unit.windows == windows and unit.targets == targets
        outcome = dict(status='UNRESOLVED', reason=str(error), complete_unit_retained=True,
            endpoint_published=False, exact_decoder_executed=False)
    else:
        assert endpoint.cursor == 512 and endpoint.optimizer_steps == 1
        assert endpoint.source == windows[-1].append(targets[-1])
        assert origin.cursor == 0 and origin.optimizer_steps == 0
        outcome = dict(status='RESOLVED_ENCLOSURE', endpoint_parameters=d.slot_count,
            touched_embedding_rows=len(bounds.embedding_ids), observed_target_rows=len(bounds.correction_ids),
            endpoint_published=True, independent_full_unit_rational_control=False,
            master_payload_bytes=len(endpoint.embedding)+len(endpoint.core)+len(endpoint.output))
    return dict(outcome, vocabulary=d.output.labels, context=d.sources.context, unit=d.output.update_unit,
        input_width=d.width, features=d.output.features, declared_native=d.cardinalities(),
        source=identity, loss_scored=False, model_or_online_freshness_claim=False)


def worker(case, output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    host = _WindowsProcessHost(HostResourceContract(CAP, {'deployment': CAP, 'compiler': CAP}))
    before, times = measured(host), {}
    try:
        result = (control if case == 'rational-control' else text_case)(times)
        assert 'torch' not in sys.modules
        import numpy as np
        result.update(timing_seconds=times, numpy_version=np.__version__, before=before, after=measured(host))
        code = 0
    except Exception as error:
        result = dict(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000],
            timing_seconds=times, before=before)
        code = 2
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


def launch():
    from windows_job_audit_support import run_in_job
    if JOURNAL.exists():
        raise RuntimeError('attempt journal already exists; do not replay a terminal or unobserved job')
    dirty = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)
    if dirty.strip():
        raise RuntimeError('commit all execution inputs before launch')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1')
    journal = dict(status='RUNNING', source_commit=source, numerical_anchor='a0610f0', cases=list(CASES),
        commit_cap=CAP, deadline_ms=DEADLINE, per_array_element_cap=ELEMENT_CAP,
        scope='fresh bounded CPU numerical/resource jobs; no Runtime/AMP/model-score certificate', results=[])
    with JOURNAL.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(journal, indent=2)+'\n')
    for case in CASES:
        journal['active_case'] = case
        JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='fp-token-host-') as temporary:
            output = Path(temporary)/'result.json'
            started = time.perf_counter()
            run = run_in_job(__file__, ('--worker', case, '--output', output), commit_limit=CAP, timeout_ms=DEADLINE)
            row = dict(case=case, job=asdict(run), launch_wall_seconds=time.perf_counter()-started)
            if output.exists():
                with output.open('rb') as stream:
                    payload = stream.read(65537)
                if len(payload) <= 65536:
                    row['result'] = json.loads(payload)
            success = run.exit_code == 0 and not run.timed_out and 'result' in row
            if success:
                for observation in ('before', 'after'):
                    measured = row['result'][observation]
                    assert (measured['process_id'], measured['creation_100ns']) == (run.process_id, run.process_creation_100ns)
                    assert measured['lifetime_process_commit_peak'] <= run.peak_process_commit <= CAP
                    assert measured['job_commit_peak'] <= run.peak_job_commit <= CAP
            row['accepted_execution'] = success
            journal['results'].append(row)
            JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
            print(case+': '+row.get('result', {}).get('status', 'NO_COMPLETE_RESULT'), flush=True)
            if not success:
                journal['status'] = 'FAILED'
                break
    else:
        journal['status'] = 'COMPLETE_RESOURCE_AUDIT'
    journal.pop('active_case', None)
    JOURNAL.write_text(json.dumps(journal, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(journal, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=CASES)
    parser.add_argument('--output')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.worker:
        if not args.output:
            parser.error('worker requires output')
        raise SystemExit(worker(args.worker, args.output))
    if not args.run:
        parser.error('explicit --run required for the one registered attempt')
    launch()
