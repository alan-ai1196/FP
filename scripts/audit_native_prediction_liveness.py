"""Exact live-object witness for the unchanged native text representation.

No corpus, timing experiment, trained score, CUDA or Runtime mutation. The
million-target lower bound is source/ABI-derived, not a measured memory slope.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import gc
import json
import struct
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
SOURCE = 'c67a0aad7468d5e59635e02fb1501fee93c2f68e'


def selected_storage(value_tuples, inputs):
    """Count each selected live object once; exclude all integer referents."""
    fraction_ids, tuple_ids, values = set(), set(), set()
    fraction_bytes = tuple_bytes = occurrences = 0
    for value_tuple in value_tuples:
        assert type(value_tuple) is tuple and len(value_tuple) >= inputs
        if id(value_tuple) not in tuple_ids:
            tuple_ids.add(id(value_tuple))
            tuple_bytes += sys.getsizeof(value_tuple)
        for value in value_tuple[:inputs]:
            assert type(value) is F
            occurrences += 1
            values.add((value.numerator, value.denominator))
            if id(value) not in fraction_ids:
                fraction_ids.add(id(value))
                fraction_bytes += sys.getsizeof(value)
    return dict(input_occurrences=occurrences, distinct_input_objects=len(fraction_ids),
        distinct_input_values=len(values), distinct_value_tuples=len(tuple_ids),
        fraction_shallow_bytes=fraction_bytes, tuple_shallow_bytes=tuple_bytes,
        selected_shallow_bytes=fraction_bytes+tuple_bytes)


def abi_and_alias_controls():
    assert sys.implementation.name == 'cpython' and sys.version_info[:3] == (3, 12, 9)
    assert struct.calcsize('P') == 8 and sysconfig.get_config_var('Py_DEBUG') in (0, None)
    fresh = tuple(F(n, d) for n, d in ((0, 1), (1, 2), (17, 65536), (1 << 2048, 3))
                  for _ in range(32))
    assert len({id(x) for x in fresh}) == 128
    assert all(gc.is_tracked(x) and sys.getsizeof(x) == 48 for x in fresh)
    assert F.__basicsize__ == 32 and F.__itemsize__ == 0
    assert tuple.__basicsize__ == 24 and tuple.__itemsize__ == 8
    assert all(sys.getsizeof(tuple(range(n))) == 40+8*n for n in (1, 6, 12, 2048, 2056))
    # Deliberate sharing falsifies counting occurrences as fresh allocations.
    # The witness counts both the repeated scalar and repeated tuple once.
    single = F(1, 2)
    aliased = (single,)*32
    shared = selected_storage((aliased, aliased), 32)
    assert shared['input_occurrences'] == 64 and shared['distinct_input_objects'] == 1
    assert shared['distinct_value_tuples'] == 1
    assert shared['selected_shallow_bytes'] == 48+sys.getsizeof(aliased)
    separate = tuple(F(1, 2) for _ in range(32))
    counted = selected_storage((separate,), 32)
    assert counted['distinct_input_values'] == 1 and counted['distinct_input_objects'] == 32
    return dict(python=sys.version, pointer_bytes=8, fraction_basicsize=32,
        fraction_gc_header_bytes=16, fraction_allocation_lower_bytes=48,
        tuple_base_with_gc_bytes=40, tuple_item_bytes=8,
        fresh_scalar_controls=128, equal_value_fresh_objects=32,
        aliased_object_control=shared, shared_integers_never_counted=True)


def history(rt, definition, word):
    from fp_reference.ingress import encode_context
    inputs = definition.sources.context*definition.width
    expected_ids, expected_tuples = [], []
    for i, target in enumerate(word):
        forecast = rt.predict_next(f'train/{i}', encode_context(()))
        assert forecast.status == 'PREDICTED_REFERENCE', forecast.reason
        # Keep addresses only: this observer must not itself keep a discarded
        # historical prediction alive across the following Runtime operation.
        prediction = rt._pending.predictions[0][1]
        expected_ids.append(tuple(id(x) for x in prediction.values[:inputs]))
        expected_tuples.append(id(prediction.values))
        del prediction, forecast
        observed = rt.observe(target)
        assert observed.status == 'OBSERVED_REFERENCE', observed.reason
    gc.collect()
    traces = rt._event_traces
    assert rt._cursor == len(word) and len(traces) == len(word)
    assert [tuple(id(x) for x in t.prediction.values[:inputs]) for t in traces] == expected_ids
    assert [id(t.prediction.values) for t in traces] == expected_tuples
    assert len({x for row in expected_ids for x in row}) == len(word)*inputs
    assert len(set(expected_tuples)) == len(word)
    for trace in traces:
        prediction = trace.prediction
        assert prediction.before is trace.before
        assert len(prediction.values) == inputs+len(definition.nodes)
        # Check actual input values against the retained causal origin/window.
        expected = tuple(F(int(q), definition.output.grid)
            for token in prediction.window.past for q in trace.before.origin.E[token])
        assert prediction.values[:inputs] == expected
    result = selected_storage((t.prediction.values for t in traces), inputs)
    per_trace = 48*inputs+40+8*(inputs+len(definition.nodes))
    assert result['selected_shallow_bytes'] == len(word)*per_trace
    assert result['distinct_input_objects'] == len(word)*inputs
    commits = sum(t.after_commit is not None for t in traces)
    assert commits == len(word)//definition.output.update_unit
    return dict(targets=len(word), commits=commits, inputs_per_prediction=inputs,
        values_per_prediction=inputs+len(definition.nodes),
        pre_target_identities_preserved_through_observe_commit_and_gc=True, **result)


def small_complete_histories():
    from fp_reference import ReferenceCompilerRuntime
    from audit_owned_token_learner import fixture, registration
    from audit_shared_token_retention import STORAGE
    groups = []
    for unit, kind, shared in product((1, 2, 4), ('mixed', 'zero-embedding'), (False, True)):
        aggregate = dict(update_unit=unit, initializer=kind, shared_storage=shared,
            histories=0, targets=0, commits=0, distinct_input_objects=0,
            selected_shallow_bytes=0, minimum_distinct_input_values=1 << 60)
        for word in product((0, 1), repeat=4):
            definition, initial = fixture(unit, kind)
            cfg, program, online = registration(definition, initial)
            rt = ReferenceCompilerRuntime(cfg, program, online=online,
                shared_storage=STORAGE if shared else None)
            result = history(rt, definition, word)
            aggregate['histories'] += 1
            for key in ('targets', 'commits', 'distinct_input_objects', 'selected_shallow_bytes'):
                aggregate[key] += result[key]
            aggregate['minimum_distinct_input_values'] = min(
                aggregate['minimum_distinct_input_values'], result['distinct_input_values'])
        if kind == 'zero-embedding':
            assert aggregate['minimum_distinct_input_values'] == 1
        groups.append(aggregate)
    return groups


def full_registration_control():
    from fp_reference import ReferenceCompilerRuntime
    from run_native_text_a1 import registration, TRAIN, HOST
    cc, program, online, storage, reporting = registration()
    d = program.definition
    assert len(online.data.active.observation_ids) == TRAIN == 1 << 20
    assert (d.sources.context, d.width, len(d.nodes), d.output.update_unit) == (512, 4, 8, 512)
    rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage,
        reporting=reporting)
    # Synthetic legal labels only. No original experiment is replayed, no
    # corpus/report is opened, and no host timing/peak measurement is claimed.
    sample = history(rt, d, (0, 1))
    assert rt._token_report is None and rt._cuda is None
    per_trace = 48*d.input_nodes+40+8*(d.input_nodes+len(d.nodes))
    lower = TRAIN*per_trace
    assert per_trace == 114792 and lower == 120368136192
    assert HOST == 103079215104 and lower > HOST
    first_excluded = HOST//per_trace+1
    assert first_excluded == 897966
    assert (first_excluded-1)*per_trace <= HOST < first_excluded*per_trace
    return dict(synthetic_labels=[0, 1], complete_runtime_sample=sample,
        program_id=program.program_id, training_declaration=TRAIN,
        reference_host_cap_bytes=HOST, selected_lower_bytes_per_trace=per_trace,
        selected_full_horizon_lower_bytes=lower,
        selected_full_horizon_lower_gib=str(F(lower, 1 << 30)),
        first_count_excluded_by_selected_objects_alone=first_excluded,
        predicts_actual_failure_cursor=False, actual_full_horizon_execution=False)


def audit():
    # Bind the source argument to entire relevant production files, not just
    # samples of successful trajectories. This is a historical scoped law if
    # a later representation changes its allocation/retention hypotheses.
    paths = ('src/reference_compiler/fp_reference/runtime.py',
        'src/reference_compiler/fp_reference/token_execution.py',
        'src/reference_compiler/fp_reference/token_batch.py', 'scripts/run_native_text_a1.py')
    subprocess.run(['git', 'diff', '--exit-code', SOURCE, '--', *paths], cwd=ROOT,
        check=True, capture_output=True)
    abi = abi_and_alias_controls()
    groups = small_complete_histories()
    full = full_registration_control()
    assert 'torch' not in sys.modules
    return dict(status='PASS_NATIVE_PREDICTION_LIVENESS_CPU', production_source=SOURCE,
        audited_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        bound_source_files=list(paths), abi=abi, groups=groups,
        totals={key: sum(group[key] for group in groups) for key in
            ('histories', 'targets', 'commits', 'distinct_input_objects', 'selected_shallow_bytes')},
        full_registration=full, scope='source/ABI liveness lower bound and finite complete CPU controls; no timing, corpus, model score or CUDA')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    result = audit()
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
        print(result['status'], result['totals'], flush=True)
    else:
        print(json.dumps(result, indent=2))
