"""Exact event/prefix controls for the packed reference and physical recipe."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys
import numpy as np
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import batched_tokens as ref
import state_relation
import readout_envelope
from readout_relation import PredictionContract
from enclosed_tokens import EnclosureUnresolved
from audit_native_tokens import fixture
from audit_token_amp_schedule import ExactPrimitives
from audit_token_readout_relation import refuses

CAP = 1 << 20


def paired_origin(d, native, oracle=None):
    origin = ref.Origin.from_native(native, element_cap=CAP)
    a = amp.Arithmetic(audit=oracle)
    return origin, amp.State.initialize(origin, a), ref.Kernel(d, element_cap=CAP), amp.Kernel(d, a, element_cap=CAP)


def same_native(left, right):
    assert left.definition == right.definition
    for slot in range(left.definition.slot_count):
        assert left.parameter(slot) == right.parameter(slot)
        assert left.gradient(slot) == right.gradient(slot)
    assert (left.cursor, left.output.unit_count, left.output.optimizer_steps, left.source_window()) == (
        right.cursor, right.output.unit_count, right.output.optimizer_steps, right.source_window())


def audit_events():
    oracle = ExactPrimitives()
    events = gradients = commits = early_refusals = forecasts = 0
    master_distance = dict(E=0, C=0, W=0)
    state_contract = state_relation.Contract(F(1, 4), CAP, 1000)
    prediction_contract = PredictionContract(F(1000), F(1000), F(1), F(1, 10), F(1, 10000), 1, CAP, 1000)
    maximum_state_error = F(0)
    state_relations = 0
    for unit, kind, word in product((2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, native = fixture(unit, kind)
        reference, physical, control, kernel = paired_origin(d, native, oracle)
        state_relation.check(reference, physical, kernel.a, state_contract)
        state_relations += 1
        for t, target in enumerate(word):
            prediction, floating = control.predict(reference), kernel.predict(physical)
            exact = native.predict()
            assert prediction.predecessor is reference and floating.predecessor is physical
            assert prediction.window == floating.window == exact.window
            assert all(prediction.values.scalar((i, 0)).contains(v) for i, v in enumerate(exact.values))
            assert prediction.normalizer.scalar(0).contains(exact.output.normalizer)
            assert all(prediction.mass(y).contains(exact.output.mass(y)) for y in range(d.output.labels))
            # A physical all-label forecast can be decoded before the target
            # exists in any pending record or gradient calculation.
            _, masses, probabilities = kernel.mass_block(floating, 0, d.output.labels)
            assert masses.shape == probabilities.shape == (d.output.labels, 1)
            forecast_relation = readout_envelope.bound(prediction, floating, kernel, prediction_contract)
            assert forecast_relation['target_cache_checks'] == forecast_relation['target_decoder_words'] == 0
            stored_total = sum((F(float(m)) for m in masses[:, 0]), F(0))
            for y in range(d.output.labels):
                native_probability = exact.output.mass(y)/exact.output.normalizer
                raw, proper = F(float(probabilities[y, 0])), F(float(masses[y, 0]))/stored_total
                assert max(abs(raw-native_probability), abs(proper-native_probability)) <= F(forecast_relation['probability_error_upper'])
            forecasts += d.output.labels
            reference = control.observe(reference, prediction, target)
            physical = kernel.observe(physical, floating, target)
            native = native.observe(exact, target)
            assert reference.cursor == physical.cursor == native.cursor
            assert reference.unit_count == physical.unit_count == native.output.unit_count
            assert reference.source == physical.source == native.source_window()
            assert reference.unit.windows == physical.windows and reference.unit.targets == physical.targets
            same_native(reference.unit.exact_decoder(), native)
            for slot in range(d.slot_count):
                assert reference.gradient(slot).contains(native.gradient(slot))
                gradients += 1
            relation = state_relation.check(reference, physical, kernel.a, state_contract)
            maximum_state_error = max(maximum_state_error, F(relation['state_error_upper']))
            state_relations += 1
            n = reference.unit_count
            # Independent columns are prefix-stable; no future target is
            # needed to produce the pre-observation feature/normalizer words.
            assert physical.values[:, n-1].tobytes() == floating.values[:, 0].tobytes()
            assert physical.normalizer[n-1:n].tobytes() == floating.normalizer.tobytes()
            assert masses[target, 0].tobytes() == physical.target_mass[n-1].tobytes()
            events += 1
            if n < unit:
                refuses(reference.commit)
                refuses(lambda: physical.commit(kernel.a))
                early_refusals += 2
            else:
                refuses(lambda: control.predict(reference))
                refuses(lambda: kernel.predict(physical))
                reference, physical, native = reference.commit(), physical.commit(kernel.a), native.commit()
                assert reference == ref.Origin.from_native(native, element_cap=CAP)
                actual = physical.read(kernel.a)
                relation = state_relation.check(reference, physical, kernel.a, state_contract)
                maximum_state_error = max(maximum_state_error, F(relation['state_error_upper']))
                state_relations += 1
                for key in master_distance:
                    master_distance[key] = max(master_distance[key], int(np.max(np.abs(
                        getattr(actual, key).astype(np.int64)-getattr(reference, key).astype(np.int64)), initial=0)))
                commits += 1
    return dict(histories=96, observations=events, pre_target_label_forecasts=forecasts,
        complete_reference_gradient_coordinates=gradients, independent_commits=commits,
        early_commit_refusals=early_refusals, full_unit_prediction_refusals=2*commits,
        exact_physical_primitive_calls=oracle.calls, exact_physical_primitive_words=oracle.words,
        half_words=oracle.half_words, maximum_master_grid_distance=master_distance,
        complete_state_relations=state_relations, state_tolerance='1/4', maximum_state_error_upper=str(maximum_state_error),
        pre_target_words_equal_post_observation_columns=True)


def bindings_and_profiles():
    d, native = fixture(4, 'mixed')
    reference, physical, control, kernel = paired_origin(d, native)
    prediction, floating = control.predict(reference), kernel.predict(physical)
    refuses(lambda: control.observe(reference, replace(prediction, predecessor=replace(reference)), 0))
    refuses(lambda: kernel.observe(physical, replace(floating, predecessor=replace(physical)), 0))
    fake = floating.normalizer.copy()
    fake[0] = np.nextafter(fake[0], np.float32(np.inf))
    refuses(lambda: kernel.observe(physical, replace(floating, normalizer=fake), 0))
    refuses(lambda: kernel.observe(physical, replace(floating, normalizer=floating.normalizer.reshape(1, 1)), 0))
    refuses(lambda: kernel.observe(physical, replace(floating, normalizer=floating.normalizer.view(np.int32)), 0))
    refuses(lambda: control.observe(reference, replace(prediction, normalizer=prediction.normalizer.reshape((1, 1))), 0))
    for actor, state, cache in ((control, reference, prediction), (kernel, physical, floating)):
        with patch.object(actor, '_forward', side_effect=EnclosureUnresolved('charged arithmetic allowance exhausted')):
            try:
                actor.observe(state, cache, 1)
            except EnclosureUnresolved as error:
                retained = error.retained_unit
                if type(retained) is ref.Unit:
                    assert retained.origin is state and retained.windows == (cache.window,) and retained.targets == (1,)
                else:
                    assert retained[0] is state and retained[1:] == ((cache.window,), (1,))
            else:
                raise AssertionError('post-target arithmetic refusal must retain the actual target')
    old_windows = (native.source_window(),)
    refuses(lambda: control.bound(reference, old_windows, (0,)))
    refuses(lambda: kernel.unit(physical, old_windows, (0,)))
    for actor, origin in ((control, reference), (kernel, physical)):
        refuses(lambda: actor.prefix(origin, (), ()))
        refuses(lambda: actor.prefix(origin, old_windows*5, (0,)*5))
    # Repeated, out-of-order original contexts are legal retained profiles.
    # The target's original source position is independent of learner time.
    word, positions = (0, 1, 1, 0), (2, 0, 2, 1)
    for t, position in enumerate(positions):
        window = d.sources.window(word, position)
        target = word[position]
        prediction, floating = control.predict(reference, window), kernel.predict(physical, window)
        exact = native.predict(window)
        if window != native.source_window():
            refuses(lambda: control.observe(reference, prediction, target))
            refuses(lambda: kernel.observe(physical, floating, target))
        reference = control.observe(reference, prediction, target, window=window)
        physical = kernel.observe(physical, floating, target, window=window)
        native = native.observe(exact, target, window=window)
        same_native(reference.unit.exact_decoder(), native)
        assert reference.source == physical.source == native.source_window()
        assert reference.cursor == physical.cursor == t+1
        for slot in range(d.slot_count):
            assert reference.gradient(slot).contains(native.gradient(slot))
    assert reference.source.position == physical.source.position == 2
    assert reference.cursor == physical.cursor == 4
    relation_contract = state_relation.Contract(F(1, 4), CAP, 1000)
    state_relation.check(reference, physical, kernel.a, relation_contract)
    wrong = physical.common.copy()
    wrong[0] += 1
    refuses(lambda: state_relation.check(reference, replace(physical, common=wrong), kernel.a, relation_contract))
    wrong = physical.corrections.copy()
    wrong[0, 0] += 1
    refuses(lambda: state_relation.check(reference, replace(physical, corrections=wrong), kernel.a, relation_contract))
    refuses(lambda: state_relation.check(reference, replace(physical, correction_ids=physical.correction_ids[::-1]), kernel.a, relation_contract))
    refuses(lambda: state_relation.check(reference, physical, kernel.a, replace(relation_contract, state_atol=F(0))))
    wrong_master = physical.origin.W.copy()
    wrong_master[-1, -1] += 32
    wrong_state = replace(physical.origin, W=wrong_master)
    refuses(lambda: state_relation.check(reference, replace(physical, origin=wrong_state), kernel.a, relation_contract))
    dormant = physical.core.copy()
    dormant[-1] = 1
    refuses(lambda: state_relation.check(reference, replace(physical, core=dormant), kernel.a, relation_contract))
    wrong_embedding = physical.embedding.copy()
    wrong_embedding[-1, 0] += 1
    refuses(lambda: state_relation.check(reference, replace(physical, embedding=wrong_embedding), kernel.a, relation_contract))
    return dict(retained_profile_events=4, final_source_position=2, final_learner_cursor=4,
        original_contexts_preserved=True, explicit_predecessor_cache_and_arity_refusals=12,
        complete_state_relation_mutation_refusals=7, post_target_refusals_preserve_actual_record=2,
        implicit_wrong_profile_source_refuses=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_CAUSAL_PACKED_TOKEN_EVENT_PREFIXES',
        scope='exact passive event/prefix controls; no Runtime, owned gradient-error or new CUDA bridge')
    for name, function in (('events', audit_events), ('bindings_and_profiles', bindings_and_profiles)):
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_EVENT_PREFIXES.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
