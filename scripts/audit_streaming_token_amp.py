"""Exact CPU controls for incremental complete token gradients and carry state."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import streaming_amp as stream
import batched_tokens as ref
import state_relation
from enclosed_tokens import EnclosureUnresolved
from audit_native_tokens import fixture
from audit_token_amp_schedule import ExactPrimitives
from audit_token_readout_relation import refuses

CAP = 1 << 20


def balanced(values):
    values = np.asarray(values, dtype=np.float32)
    while len(values) > 1:
        pairs = len(values)//2
        following = np.asarray(values[:2*pairs:2]+values[1:2*pairs:2], dtype=np.float32)
        values = np.concatenate((following, values[-1:])) if len(values) % 2 else following
    return values[0]


def carry_fixture():
    # Fixed dyadic scalars, including a minimum subnormal and values whose
    # addition is absorption-sensitive. Geometry also exercises N=256/257.
    atoms = (F(-2), F(-1), F(0), F(1), F(2), F(1 << 24), F(-(1 << 24)), F(1, 1 << 24), F(1, 1 << 149))
    return tuple(tuple(atoms[(37*t+11*k+t*k) % len(atoms)] for k in range(8)) for t in range(257))


def forests():
    oracle = ExactPrimitives()
    a = amp.Arithmetic(audit=oracle)
    forest, leaves = stream.Forest(), []
    carries = reads = maxima = 0
    for row in carry_fixture():
        leaf = a.array([float(x) for x in row], 'float32')
        leaves.append(leaf)
        before = a.operations
        forest = forest.append(leaf, a)
        carries += a.operations-before
        before = a.operations
        actual = forest.root(a)
        reads += a.operations-before
        assert actual.tobytes() == balanced(leaves).tobytes()
        maxima = max(maxima, len(forest.blocks))
    n = len(leaves)
    assert carries == n-n.bit_count()
    assert reads == sum(t.bit_count()-1 for t in range(1, n+1))
    assert maxima == max(t.bit_count() for t in range(1, n+1))
    # Equal native sum AND equal current floating sum still do not identify
    # complete continuation state. Retain the two dyadic carry coordinates.
    def make(values):
        value = stream.Forest()
        for x in values:
            value = value.append(a.array((x,), 'float32'), a)
        return value
    left, right = (-2, -1, 1), (-2, -2, 2)
    f, g = make(left), make(right)
    assert sum(left) == sum(right) == -2
    assert f.root(a).tobytes() == g.root(a).tobytes()
    delta = 2.0**-23
    first, second = f.append(a.array((delta,), 'float32'), a), g.append(a.array((delta,), 'float32'), a)
    assert F(float(first.root(a)[0])) == F(-2)+F(1, 1 << 23)
    assert F(float(second.root(a)[0])) == F(-2)
    return dict(prefixes=n, vector_width=8, carry_additions=carries, root_additions=reads,
        maximum_live_blocks=maxima, recompute_all_prefix_additions=n*(n-1)//2,
        current_root_compression_falsified=dict(histories=(left, right), exact_and_current_sum='-2',
            next_leaf='1/8388608', next_roots=('-16777215/8388608', '-2')),
        exact_primitive_calls=oracle.calls, exact_primitive_words=oracle.words)


def controls():
    oracle = ExactPrimitives()
    histories = events = commits = words = forecasts = changed = 0
    largest = committed_error = F(0)
    contract = state_relation.Contract(F(1, 4), CAP, 1000)
    for unit, kind, word in product((2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, native = fixture(unit, kind)
        exact_origin = ref.Origin.from_native(native, element_cap=CAP)
        reference = ref.Kernel(d, element_cap=CAP)
        a = amp.Arithmetic(audit=oracle)
        current = amp.State.initialize(exact_origin, a)
        kernel = stream.Kernel(d, a, element_cap=CAP)
        for target in word:
            prediction = kernel.predict(current)
            expected = native.predict()
            old = current
            current = kernel.observe(current, prediction, target)
            view = current.diagnostic_view(a)
            native = native.observe(expected, target)
            bounds = reference.prefix(exact_origin, current.windows, current.targets)
            cache = stream.audit_cache(current, a, element_cap=CAP)
            words += cache['physical_leaf_and_carry_words']
            report = state_relation.check(bounds, view, a, contract)
            largest = max(largest, F(report['state_error_upper']))
            assert (current.cursor, current.unit_count, current.source) == (native.cursor, native.output.unit_count, native.source_window())
            # Every prefix has the same pre-target forward words as the old
            # pointwise schedule, but its cross-event gradient association is new.
            legacy = kernel.event_kernel.prefix(current.origin, current.windows, current.targets)
            for key in ('values', 'normalizer', 'target_mass'):
                assert a.raw(getattr(view, key)).tobytes() == a.raw(getattr(legacy, key)).tobytes()
            changed += int(any(a.raw(getattr(view, k)).tobytes() != a.raw(getattr(legacy, k)).tobytes()
                               for k in ('embedding', 'core', 'common', 'corrections')))
            assert a.raw(prediction.event.values).tobytes() == a.raw(current.leaves[-1].values).tobytes()
            _, masses, probabilities = kernel.event_kernel.mass_block(prediction.event, 0, d.output.labels)
            for y in range(d.output.labels):
                exact_probability = expected.output.mass(y)/expected.output.normalizer
                assert abs(F(float(probabilities[y, 0]))-exact_probability) <= F(1, 10000)
            forecasts += d.output.labels
            events += 1
            if current.unit_count == unit:
                refuses(lambda: kernel.predict(current))
                current = kernel.commit(current)
                native = native.commit()
                exact_origin = ref.Origin.from_native(native, element_cap=CAP)
                committed = state_relation.check(exact_origin, current, a, contract)
                committed_error = max(committed_error, F(committed['parameter_error_upper']))
                commits += 1
            else:
                refuses(lambda: kernel.commit(current))
            if type(old) is stream.Pending:
                # A newer append cannot overwrite a historical forest/leaf.
                stream.audit_cache(old, a, element_cap=CAP)
        assert kernel.event_evaluations == len(word)
        histories += 1
    assert changed > 0
    return dict(histories=histories, events=events, commits=commits, pre_target_label_checks=forecasts,
        physical_leaf_and_carry_words_checked=words, prefixes_differing_from_legacy_gradient_association=changed,
        maximum_pending_state_error_upper=str(largest), maximum_committed_parameter_error_upper=str(committed_error),
        fixed_small_fixture_tolerance='1/4',
        exact_primitive_calls=oracle.calls, exact_primitive_words=oracle.words, half_words=oracle.half_words,
        one_new_event_derivative_per_observation=True, complete_future_caches_replayed=True)


def profiles_and_attacks():
    checked = 0
    contract = state_relation.Contract(F(1, 4), CAP, 1000)
    for word in product((0, 1), repeat=4):
        d, native = fixture(4, 'mixed')
        origin = ref.Origin.from_native(native, element_cap=CAP)
        a = amp.Arithmetic()
        current = amp.State.initialize(origin, a)
        kernel = stream.Kernel(d, a, element_cap=CAP)
        reference = ref.Kernel(d, element_cap=CAP)
        for index in (3, 0, 3, 0):
            window, target = d.sources.window(word, index), word[index]
            pred = kernel.predict(current, window)
            current = kernel.observe(current, pred, target, window=window)
            native = native.observe(native.predict(window), target, window=window)
            assert current.cursor == native.cursor and current.source == native.source_window()
            state_relation.check(reference.prefix(origin, current.windows, current.targets), current.diagnostic_view(a), a, contract)
            stream.audit_cache(current, a, element_cap=CAP)
            checked += 1
        assert current.cursor == 4 and current.source.position == 1
        physical = kernel.commit(current)
        state_relation.check(ref.Origin.from_native(native.commit(), element_cap=CAP), physical, a, contract)
    d, root = fixture(4, 'mixed')
    origin = ref.Origin.from_native(root, element_cap=CAP)
    a = amp.Arithmetic()
    kernel = stream.Kernel(d, a, element_cap=CAP)
    pending = amp.State.initialize(origin, a)
    for y in (0, 1, 0):
        pending = kernel.observe(pending, kernel.predict(pending), y)
    basis = pending.basis(a)
    # Preserve EVERY current ordinary gradient coordinate while changing an
    # unobserved carry cache. The old coordinate predicate alone cannot bind it.
    forged = replace(pending, core=stream.Forest(3, (stream.Block(2, basis.core.copy()), stream.Block(1, np.zeros_like(basis.core)))))
    assert forged.core.root(a).tobytes() == pending.core.root(a).tobytes()
    bounds = ref.Kernel(d, element_cap=CAP).prefix(origin, pending.windows, pending.targets)
    state_relation.check(bounds, forged.diagnostic_view(a), a, contract)
    refuses(lambda: stream.audit_cache(forged, a, element_cap=CAP))
    prediction = kernel.predict(pending)
    refuses(lambda: kernel.observe(replace(pending), prediction, 1))
    with patch.object(stream.Forest, 'append', side_effect=EnclosureUnresolved('forced carry failure')):
        try:
            kernel.observe(pending, prediction, 1)
        except EnclosureUnresolved as error:
            old, cached, window, target, leaf = error.retained_unit
            assert old is pending and cached is prediction and window == prediction.window and target == 1
            assert leaf.targets == (1,) and leaf.windows == (window,)
        else:
            raise AssertionError('failed carry was accepted')
    return dict(profile_events=checked, original_source_clocks_preserved=True,
        basis_only_cache_binding_falsified=True, complete_cache_replay_rejects_forgery=True,
        cache_predecessor_identity_refusal=True, post_target_failure_retains_predecessor_target_and_actual_leaf=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_STREAMING_TOKEN_AMP_CPU_CONTROL', schedule=stream.SCHEDULE)
    for key, test in (('forests', forests), ('events', controls), ('profiles_and_attacks', profiles_and_attacks)):
        result[key] = test()
        print('PASS '+key, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_STREAMING_TOKEN_AMP_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
