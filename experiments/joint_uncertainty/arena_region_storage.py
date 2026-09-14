"""Bounded host audit of complete CUDA-region metadata representation.

Both implementations retain the same fields and construct the same complete
snapshot table. The baseline is imported from the immutable pre-change source.
No GPU model, phase, throughput or n16 recovery outcome is inferred.
"""
from dataclasses import asdict, fields, FrozenInstanceError, replace
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = Path('F:/FP-likelihood-model-audit')
BASELINE_SOURCE = 'b85b39da8fa8440c243814a0ce6ee930d79f7ffe'
COUNTS = (250000, 500000)
CAP, TIMEOUT = 512 << 20, 120000
NAMES = ('sequence', 'phase', 'owner', 'operation', 'offset', 'byte_size',
         'reserved_size', 'shape', 'dtype', 'initialized')


def load_implementation(source_root):
    sys.path[:0] = [str(source_root/'src/reference_compiler'), str(ROOT/'scripts')]
    from fp_reference.cuda_storage import CudaRegion
    from fp_reference.core import freeze_data
    assert tuple(field.name for field in fields(CudaRegion)) == NAMES
    return CudaRegion, freeze_data


def primitive_row(region):
    return tuple(getattr(region, name) for name in NAMES)


def field_audit():
    region_type, freeze = load_implementation(ROOT)
    checks = 0
    for sequence, phase, owner, operation, shape, dtype in product(
            range(2), range(3), ('deployment', 'compiler'), ('ingress', 'add', 'mul'),
            ((), (0,), (1,), (2,), (1, 2)), ('torch.float16', 'torch.float32')):
        size = prod(shape)*(2 if dtype == 'torch.float16' else 4)
        before = region_type(sequence, phase, owner, operation, 16*sequence, size,
                             max(8, (size+7)//8*8), shape, dtype)
        assert not hasattr(before, '__dict__')
        expected = (sequence, phase, owner, operation, 16*sequence, size,
                    max(8, (size+7)//8*8), shape, dtype, False)
        assert primitive_row(before) == expected
        try:
            before.initialized = True
        except FrozenInstanceError:
            pass
        else:
            raise AssertionError('region field became mutable')
        current = [before]
        snapshot = freeze({'regions': tuple(primitive_row(r) for r in current)})
        current[0] = replace(before, initialized=True)
        assert primitive_row(current[0]) == expected[:-1]+(True,)
        assert not before.initialized and snapshot['regions'] == (expected,)
        assert replace(current[0], owner=owner).sequence == before.sequence
        checks += 1
    assert 'torch' not in sys.modules
    return {'complete_field_replace_and_detached_snapshot_cases': checks,
            'fields': NAMES, 'old_regions_remain_unchanged_on_mark': True,
            'no_per_instance_dictionary': True,
            'scope': 'ordinary immutable field/value operations; actual CUDA extent guards tested separately'}


def worker(source_root, count):
    assert count in COUNTS
    region_type, freeze = load_implementation(source_root)
    phases = tuple(range((count+99)//100))
    regions = [region_type(i, phases[i//100], 'compiler', 'mul-single', 8*i,
                           4, 8, (), 'torch.float32', True) for i in range(count)]
    # The same complete region table and production recursive freeze.
    # No record, field, old extent or intermediate table is discarded.
    snapshot = freeze({'regions': tuple(primitive_row(r) for r in regions)})
    assert len(snapshot['regions']) == len(regions) == count
    for i, row in enumerate(snapshot['regions']):
        assert row == (i, i//100, 'compiler', 'mul-single', 8*i,
                       4, 8, (), 'torch.float32', True)
    assert 'torch' not in sys.modules
    shallow = sys.getsizeof(regions[-1])
    # This diagnostic materializes one ordinary instance's lazy dictionary.
    # It is not a prediction of whole-process savings; the job peaks measure
    # the real allocation behavior without materializing every dictionary.
    has_dict = hasattr(regions[-1], '__dict__')
    if has_dict:
        shallow += sys.getsizeof(regions[-1].__dict__)
    return {'status': 'PASS', 'process_id': os.getpid(), 'region_count': count,
            'complete_snapshot_rows_checked': count, 'fields_per_region': len(NAMES),
            'has_instance_dictionary': has_dict,
            'shallow_region_plus_dictionary_bytes': shallow,
            'shallow_size_excludes_field_referents': True,
            'no_GPU_import_or_model_execution': True}


def git(root, *args):
    return subprocess.run(('git', *args), cwd=root, capture_output=True,
                          encoding='utf-8', check=True).stdout.strip()


def audit():
    assert git(BASELINE_ROOT, 'rev-parse', 'HEAD') == BASELINE_SOURCE
    paths = ('src/reference_compiler/fp_reference/cuda_storage.py',
             'src/reference_compiler/fp_reference/core.py')
    assert not git(BASELINE_ROOT, 'status', '--porcelain', '--', *paths)
    # This is the real pre-change storage/freezer implementation, not an
    # intentionally weakened stand-in. The parent never imports it in place
    # of the current implementation inside an already running process.
    from windows_job_audit_support import run_in_job
    records = []
    with tempfile.TemporaryDirectory(prefix='fp-region-metadata-', dir=ROOT/'runs') as directory:
        directory = Path(directory)
        assert directory.resolve().parent == (ROOT/'runs').resolve()
        for count in COUNTS:
            for mode, source_root in (('baseline', BASELINE_ROOT), ('slotted', ROOT)):
                output = directory/f'{mode}-{count}.json'
                job = run_in_job(__file__, ('--worker', '--source-root', str(source_root),
                    '--count', str(count), '--output', str(output)), commit_limit=CAP, timeout_ms=TIMEOUT)
                record = {'mode': mode, 'regions': count, 'completed_job': asdict(job)}
                if output.exists():
                    payload = output.read_bytes()
                    assert len(payload) <= 4096
                    record['result'] = json.loads(payload)
                records.append(record)
                assert job.exit_code == 0 and not job.timed_out and job.attached_before_resume
                assert not job.limit_terminated_processes and job.peak_job_commit <= CAP
                assert record['result']['process_id'] == job.process_id
                assert record['result']['has_instance_dictionary'] == (mode == 'baseline')
    comparisons = []
    for count in COUNTS:
        old, new = (next(row for row in records if row['regions'] == count and row['mode'] == mode)
                    for mode in ('baseline', 'slotted'))
        delta = old['completed_job']['peak_job_commit']-new['completed_job']['peak_job_commit']
        comparisons.append({'regions': count, 'observed_peak_job_commit_reduction_bytes': delta,
                            'both_complete_snapshot_tables_checked': True})
    return {'status': 'DEVELOPMENT_HOST_AUDIT_PASS', 'baseline_source': BASELINE_SOURCE,
            'scope': 'same complete metadata/snapshot values; measured Python host overhead only; no n16 recovery or GPU timing claim',
            'field_audit': field_audit(), 'fixed_job_commit_cap': CAP,
            'fixed_job_timeout_ms': TIMEOUT, 'workers': records, 'comparisons': comparisons}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--count', type=int)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker:
        assert args.source_root and args.count in COUNTS and args.output and not args.write
        args.output.write_text(json.dumps(worker(args.source_root, args.count)), encoding='utf-8')
    else:
        assert args.source_root is None and args.count is None and args.output is None
        load_implementation(ROOT)
        report = audit()
        if args.write:
            (ROOT/'evidence/minimal/FP_ARENA_REGION_STORAGE_AUDIT.json').write_text(
                json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
