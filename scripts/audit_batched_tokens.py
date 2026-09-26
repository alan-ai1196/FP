"""Independent exact controls for batched retained-record token enclosures."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product, permutations, combinations
from pathlib import Path
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference.program import Sum, Product, Term
from causal_tokens import TokenSources, TokenWindow
from audit_native_tokens import fixture, complete
from audit_enclosed_tokens import long_unit_fixture
from enclosed_tokens import Interval, EnclosureUnresolved
import native_tokens as tokens
import native_readout as readout
import batched_tokens as batch

OUTPUT = ROOT/'evidence/minimal/FP_BATCHED_TOKENS.json'


def refuses(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('expected refusal')


def array(points):
    enclosed = [Interval.exact(p) for p in points]
    return batch.ArrayInterval(np.asarray([v.lower for v in enclosed]), np.asarray([v.upper for v in enclosed]))


def primitive_audit():
    values = (F(-2), F(-1, 3), F(-1, 2**1075), F(0), F(1, 2**1075), F(1, 2**1074), F(1, 2), F(1), F(7, 3), F(2**52+1))
    a, b = array(values).reshape((-1, 1)), array(values).reshape((1, -1))
    results = (a+b, a-b, a*b)
    checks = 0
    for i, x in enumerate(values):
        for j, y in enumerate(values):
            for result, exact in zip(results, (x+y, x-y, x*y)):
                assert result.scalar((i, j)).contains(exact)
                checks += 1
    denominators = (F(-3), F(-1, 3), F(1, 7), F(1), F(3))
    result = a/array(denominators).reshape((1, -1))
    for i, x in enumerate(values):
        for j, y in enumerate(denominators):
            assert result.scalar((i, j)).contains(x/y)
            checks += 1
    boxes = ((F(-3, 7), F(-1, 3)), (F(-2), F(3)), (F(0), F(5, 8)), (F(1, 7), F(9, 7)))
    x = batch.ArrayInterval(np.asarray([Interval.exact(a).lower for a, b in boxes]),
                            np.asarray([Interval.exact(b).upper for a, b in boxes]))
    a, b = x.reshape((-1, 1)), x.reshape((1, -1))
    results = (a+b, a-b, a*b)
    wide = 0
    for i, (low, high) in enumerate(boxes):
        for j, (left, right) in enumerate(boxes):
            for u, v in product((low, (low+high)/2, high), (left, (left+right)/2, right)):
                for result, exact in zip(results, (u+v, u-v, u*v)):
                    assert result.scalar((i, j)).contains(exact)
                    wide += 1
    refuses(lambda: batch.ArrayInterval.point(np.asarray([1e308]))*batch.ArrayInterval.point(np.asarray([2.0])))
    refuses(lambda: batch.ArrayInterval.point(np.asarray([0.0])).reciprocal())
    refuses(lambda: batch.words((2**80,)))
    refuses(lambda: batch.words((-1,)))
    refuses(lambda: batch.words((True,)))
    return dict(exact_broadcast_operation_checks=checks, nonpoint_checks=wide, arithmetic_word_and_type_refusals=5)


def reductions():
    checks = 0
    keys = (2, 0, 2, 1, 0)
    values = tuple((F(i-2, 3), F((-1)**i, i+1), F(i % 2)) for i in range(5))
    for order in permutations(range(5)):
        ordered = tuple(values[i] for i in order)
        intervals = array(tuple(x for row in ordered for x in row)).reshape((5, 3))
        total = batch.reduce_rows(intervals)
        ids, grouped = batch.segment_rows(np.asarray([keys[i] for i in order]), intervals)
        assert tuple(ids) == (0, 1, 2)
        for k in range(3):
            assert total.scalar(k).contains(sum((row[k] for row in values), F(0)))
            for j, key in enumerate(ids):
                assert grouped.scalar((j, k)).contains(sum((values[i][k] for i in range(5) if keys[i] == key), F(0)))
            checks += 4
    empty = batch.reduce_rows(batch.ArrayInterval.zero((0, 3)))
    assert np.all(empty.lower == 0) and np.all(empty.upper == 0)
    return dict(permutations=120, signed_balanced_and_segment_checks=checks, empty_sum_exact=True)


def same_endpoint(packed, exact):
    assert tuple(packed.parameter(i) for i in range(exact.definition.slot_count)) == complete(exact)
    assert packed.cursor == exact.cursor and packed.optimizer_steps == exact.output.optimizer_steps
    assert packed.source == exact.source_window()


def histories():
    rows = []
    for unit, kind in product((1, 2), ('mixed', 'zero-embedding', 'zero-core')):
        d, root = fixture(unit, kind)
        packed_root = batch.Origin.from_native(root, element_cap=100000)
        kernel = batch.Kernel(d, element_cap=100000)
        completed = commits = events = gradients = unresolved = 0
        for word in product(range(2), repeat=6):
            packed, exact = packed_root, root
            for offset in range(0, len(word), unit):
                windows = tuple(d.sources.window(word, t) for t in range(offset, offset+unit))
                targets = word[offset:offset+unit]
                bounds = kernel.bound(packed, windows, targets)
                for event, (window, target) in enumerate(zip(windows, targets)):
                    cache = exact.predict(window)
                    assert all(bounds.values.scalar((i, event)).contains(value) for i, value in enumerate(cache.values))
                    assert bounds.normalizer.scalar(event).contains(cache.output.normalizer)
                    assert bounds.target_mass.scalar(event).contains(cache.output.mass(target))
                    assert all(bounds.mass(event, y).contains(cache.output.mass(y)) for y in range(d.output.labels))
                    exact = exact.observe(cache, target, window=window)
                    events += 1
                assert all(bounds.gradient(i).contains(exact.gradient(i)) for i in range(d.slot_count))
                gradients += d.slot_count
                try:
                    following = bounds.commit()
                except EnclosureUnresolved as error:
                    assert error.retained_unit is bounds.unit
                    decoded = error.retained_unit.exact_decoder()
                    assert tuple(decoded.gradient(i) for i in range(d.slot_count)) == tuple(exact.gradient(i) for i in range(d.slot_count))
                    unresolved += 1
                    break
                exact = exact.commit()
                same_endpoint(following, exact)
                packed = following
                commits += 1
            else:
                completed += 1
        rows.append(dict(update_unit=unit, initializer=kind, requested_words=64, complete_words=completed,
            native_event_comparisons=events, complete_gradient_coordinate_checks=gradients,
            exact_native_commits=commits, terminal_unresolved_words=unresolved, oracle_resumptions=0))
        print(f'PASS batched histories unit={unit} initializer={kind}', flush=True)
    return rows


def profiles_and_binding():
    d, root = fixture(2, 'mixed')
    packed_root = batch.Origin.from_native(root, element_cap=100000)
    kernel = batch.Kernel(d, element_cap=100000)
    count = commits = 0
    for tape in product(range(2), repeat=4):
        for pair in combinations(range(4), 2):
            packed, exact = packed_root, root
            for _ in range(2):
                windows = tuple(d.sources.window(tape, i) for i in pair)
                targets = tuple(tape[i] for i in pair)
                bounds = kernel.bound(packed, windows, targets)
                altered = kernel.bound(packed, windows, tuple(1-y for y in targets))
                # Forward source/normalization is independent of all targets
                # in the retained unit, not just the selected current label.
                assert np.array_equal(bounds.values.lower, altered.values.lower)
                assert np.array_equal(bounds.values.upper, altered.values.upper)
                assert np.array_equal(bounds.normalizer.lower, altered.normalizer.lower)
                assert np.array_equal(bounds.normalizer.upper, altered.normalizer.upper)
                for window, target in zip(windows, targets):
                    exact = exact.observe(exact.predict(window), target, window=window)
                assert all(bounds.gradient(i).contains(exact.gradient(i)) for i in range(d.slot_count))
                packed, exact = bounds.commit(), exact.commit()
                same_endpoint(packed, exact)
                commits += 1
            count += 1
    try:
        packed_root.E.flags.writeable = True
    except ValueError:
        pass
    else:
        raise AssertionError('immutable packed master became writable')
    refuses(lambda: batch.Origin.from_native(root, element_cap=1))
    refuses(lambda: batch.Kernel(d, element_cap=1))
    refuses(lambda: kernel.bound(packed_root, (root.source_window(),), (0,)))
    refuses(lambda: kernel.bound(packed_root, (root.source_window(),)*2, (0, True)))
    foreign = TokenWindow(TokenSources(3, 3), 0, (3,)*3)
    refuses(lambda: kernel.bound(packed_root, (foreign,)*2, (0, 1)))
    wide = tokens.Definition(TokenSources(2, 1), 8, (), 0, (0,),
        readout.Spec((F(1),)*2, 1, 4, F(1, 3), 1))
    refuses(lambda: batch.Kernel(wide, element_cap=12))  # Full input masters:24.
    repeated = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,)*7,
        readout.Spec((F(1),)*2, 7, 4, F(1, 3), 5))
    refuses(lambda: batch.Kernel(repeated, element_cap=20))  # Feature batch:35.
    metadata = tokens.Definition(TokenSources(2, 1), 1, (Sum('f', (Term(0, 0),)*4),), 1, (1,),
        readout.Spec((F(1),)*2, 1, 4, F(1, 3), 1))
    refuses(lambda: batch.Kernel(metadata, element_cap=8))  # Edge index table:12.
    return dict(retained_schedules=count, exact_commits=commits, target_noninterference_units=commits,
        immutable_master_views=True, dimension_element_source_and_target_refusals=8)


def refusals_and_empty_core():
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2),)*2, 1, 8, F(1, 8), 1))
    root = tokens.initialize(d, (128,), (), (64,))
    packed = batch.Origin.from_native(root, element_cap=1000)
    window = TokenWindow(d.sources, 7, (1,))
    bounds = batch.Kernel(d, element_cap=1000).bound(packed, (window,), (0,))
    try:
        bounds.commit()
    except EnclosureUnresolved as error:
        assert error.retained_unit is bounds.unit
        decoded = error.retained_unit.exact_decoder()
        assert decoded.gradient(1) == 0 and decoded.cursor == 1 and decoded.source_position == 8
    else:
        raise AssertionError('expected unresolved symmetric exact grid boundary')
    for target in range(2):
        z = tokens.Definition(TokenSources(2, 1), 1, (Sum('f', ()), Product('f', 1, 1)), 1, (1, 2),
            readout.Spec((F(1),)*2, 2, 4, F(1, 3), 1))
        initial = tokens.initialize(z, (2,), (3,), (1, 2))
        origin = batch.Origin.from_native(initial, element_cap=1000)
        result = batch.Kernel(z, element_cap=1000).bound(origin, (initial.source_window(),), (target,))
        exact = initial.observe(initial.predict(), target).commit()
        same_endpoint(result.commit(), exact)
    return dict(ambiguous_boundary_retains_complete_source_target_unit=True,
        empty_SUM_PRODUCT_and_unused_slot_exact_cases=2)


def full_vocabulary():
    d, root, targets = long_unit_fixture()
    windows = tuple(d.sources.window(targets, i) for i in range(len(targets)))
    origin = batch.Origin.from_native(root, element_cap=1 << 22)
    bounds = batch.Kernel(d, element_cap=1 << 22).bound(origin, windows, targets)
    exact = root
    for event, (window, target) in enumerate(zip(windows, targets)):
        cache = exact.predict(window)
        assert all(bounds.values.scalar((i, event)).contains(value) for i, value in enumerate(cache.values))
        assert bounds.normalizer.scalar(event).contains(cache.output.normalizer)
        assert bounds.target_mass.scalar(event).contains(cache.output.mass(target))
        exact = exact.observe(cache, target, window=window)
    a, b = dict(exact.embedding_gradient), bounds.embedding_ids
    assert tuple(sorted({k//d.width for k in a})) == tuple(b)
    for i, token in enumerate(b):
        for k in range(d.width):
            assert bounds.embedding.scalar((i, k)).contains(a[int(token)*d.width+k])
    assert all(bounds.core.scalar(i).contains(g) for i, g in enumerate(exact.core_gradient))
    assert all(bounds.common.scalar(i).contains(g) for i, g in enumerate(exact.output.common))
    corrections = dict(exact.output.corrections)
    assert tuple(corrections) == tuple(bounds.correction_ids)
    for i, token in enumerate(bounds.correction_ids):
        for k, g in enumerate(corrections[int(token)]):
            assert bounds.corrections.scalar((i, k)).contains(g)
    endpoint, native = bounds.commit(), exact.commit()
    same_endpoint(endpoint, native)
    assert origin.embedding == batch.Origin.from_native(root, element_cap=1 << 22).embedding
    return dict(vocabulary=d.output.labels, update_unit=d.output.update_unit, context=d.sources.context,
        core_value_checks=len(targets)*(d.input_nodes+len(d.nodes)),
        complete_pending_gradient_basis_checked=True, complete_endpoint_parameter_checks=d.slot_count,
        maximum_exact_common_denominator_bits=max(v.denominator.bit_length() for v in exact.output.common),
        packed_master_payload_bytes=len(endpoint.embedding)+len(endpoint.core)+len(endpoint.output),
        original_master_payload_unchanged=True,
        scope='synthetic retained-record numerical audit; no actual text loss, online freshness, timing, total memory, Runtime or AMP claim')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_BATCHED_NATIVE_TOKEN_ENCLOSURES', numpy_version=np.__version__,
        scope='batched complete retained units, explicit interval reductions and immutable packed exact masters; passive only')
    for name, function in dict(primitives=primitive_audit, reductions=reductions, native_histories=histories,
        retained_profiles=profiles_and_binding, unresolved_and_empty=refusals_and_empty_core, full_vocabulary=full_vocabulary).items():
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
