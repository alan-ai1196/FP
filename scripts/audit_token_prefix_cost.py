"""Count unavoidable repetitions in the current successful token phase schedule.

Complete Runtime logic with CPU array/device substitution, two update units
per existing synthetic fixture. No timing, corpus, CUDA or new model result.
The claims concern this implementation schedule, not lower bounds on FP.
"""
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]

from audit_owned_token_learner import fixture, registration
from audit_token_cuda_owner import cuda_contract
from audit_token_snapshot_bounds import cpu_device
from audit_shared_cuda_retention import STORAGE
from audit_reference_construction import validate_residency, limits
from fp_reference import ReferenceCompilerRuntime, token_cuda_prefix as execution
from fp_reference.ingress import encode_context
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_batch import Kernel
from fp_reference.token_cuda_state import LeafWords


LEAF_ARRAYS = ('values', 'normalizer', 'target_mass', 'embedding', 'core', 'common', 'corrections')


def run(unit):
    definition, initial = fixture(unit, 'mixed')
    cc, program, online = registration(definition, initial, count=2*unit)
    cc = replace(cc, limits=limits(256 << 20, 10**14))
    backends, rows = [], []
    current = None
    original_bound, original_capture, original_raw = Kernel._bound, LeafWords.capture.__func__, CPUArrays.raw

    def arrays(workspace, readout_buffer, **kwargs):
        backend = CPUArrays(**kwargs)
        backends.append(backend)
        return backend

    def physical(backend):
        return any(backend is candidate for candidate in backends)

    def bound(kernel, retained):
        if current is not None:
            current['native_prefix_sizes'].append(len(retained.targets))
        return original_bound(kernel, retained)

    def raw(backend, value):
        result = original_raw(backend, value)
        if current is not None and physical(backend):
            current['all_raw_calls'] += 1
            current['all_raw_bytes'] += result.nbytes
        return result

    def capture(cls, leaf, backend):
        result = original_capture(cls, leaf, backend)
        if current is not None and physical(backend):
            extent = sum(len(getattr(result, key).data) for key in LEAF_ARRAYS)
            d = leaf.origin.definition
            assert extent == (2*(d.input_nodes+len(d.nodes))+8+4*d.slots+
                              8*d.output.features+4*d.width*len(set(result.window.past)))
            current['leaf_captures'] += 1
            current['leaf_bytes'] += extent
        return result

    def operation(kind, index, action):
        nonlocal current
        current = dict(kind=kind, index=index, native_prefix_sizes=[], leaf_captures=0,
                       leaf_bytes=0, all_raw_calls=0, all_raw_bytes=0)
        result = action()
        rows.append(current)
        current = None
        return result

    with cpu_device(), patch.object(execution, 'CudaArrays', arrays), \
            patch.object(Kernel, '_bound', bound), patch.object(CPUArrays, 'raw', raw), \
            patch.object(LeafWords, 'capture', classmethod(capture)):
        rt = operation('initialize', 0, lambda: ReferenceCompilerRuntime(cc, program, online=online,
            cuda=cuda_contract(cc.initializer_pattern), shared_storage=STORAGE))
        for index in range(2*unit):
            result = operation('predict', index, lambda: rt.predict_next(f'train/{index}', encode_context(())))
            assert result.status == 'PREDICTED_REFERENCE', result.reason
            result = operation('observe', index, lambda: rt.observe((0, 1, 1, 0)[index % 4]))
            assert result.status == 'OBSERVED_REFERENCE', result.reason
        snapshot = validate_residency(rt)

    assert len(snapshot.cuda.phases) == 4*unit+3
    assert all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in snapshot.cuda.phases)
    learner = snapshot.candidates[0].learner
    assert (snapshot.cursor, learner.unit_count, learner.origin.optimizer_steps) == (2*unit, 0, 2)
    first, *ordinary = rows
    assert first['native_prefix_sizes'] == [] and first['leaf_captures'] == 0
    for row in ordinary:
        k = row['index'] % unit
        if row['kind'] == 'predict':
            expected_prefixes, expected_captures = ([k, k] if k else []), 3*k
        else:
            expected_prefixes, expected_captures = [k+1], 4*k+2
            if k+1 == unit:
                expected_prefixes += [unit]  # Independent native optimizer commit.
                expected_captures += 2*unit  # Physical pre/post commit predecessor.
        assert row['native_prefix_sizes'] == expected_prefixes, row
        assert row['leaf_captures'] == expected_captures, row
        assert row['all_raw_calls'] >= 7*row['leaf_captures']
        assert row['all_raw_bytes'] >= row['leaf_bytes']

    totals = {key: sum(row[key] for row in rows) for key in
              ('leaf_captures', 'leaf_bytes', 'all_raw_calls', 'all_raw_bytes')}
    totals['native_bound_calls'] = sum(len(row['native_prefix_sizes']) for row in rows)
    totals['native_event_evaluations'] = sum(sum(row['native_prefix_sizes']) for row in rows)
    assert totals['native_bound_calls'] == 2*(3*unit-1)
    assert totals['native_event_evaluations'] == unit*(3*unit+1)
    assert totals['leaf_captures'] == unit*(7*unit+1)
    return dict(unit=unit, completed_units=2, observations=2*unit, checked_phases=len(snapshot.cuda.phases),
        every_ordinary_step_matches_law=True, **totals)


def audit():
    from audit_token_reference_host import text_model_fixture
    rows = [run(unit) for unit in (1, 2, 4, 8)]
    d, _ = text_model_fixture()  # Pure existing model factory; opens no corpus.
    assert 'torch' not in sys.modules
    B = d.output.update_unit
    assert (B, d.input_nodes+len(d.nodes), d.slots, d.output.features, d.width) == (512, 2056, 4, 8, 4)
    minimum_leaf_bytes = 2*(d.input_nodes+len(d.nodes))+8+4*d.slots+8*d.output.features+4*d.width
    return dict(status='PASS_CURRENT_TOKEN_PREFIX_COST_LAW_CPU', rows=rows,
        full_unit512_derived_counts=dict(native_bound_calls=3*B-1,
            native_event_evaluations=B*(3*B+1)//2, leaf_captures=B*(7*B+1)//2,
            leaf_raw_calls=7*B*(7*B+1)//2, minimum_leaf_bytes=minimum_leaf_bytes,
            minimum_repeated_leaf_read_bytes=minimum_leaf_bytes*B*(7*B+1)//2),
        scope=__doc__.strip())


if __name__ == '__main__':
    if sys.flags.optimize:
        raise RuntimeError('cost-law audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_PREFIX_COST_CPU.json').write_text(body, encoding='utf-8')
    print(body)
