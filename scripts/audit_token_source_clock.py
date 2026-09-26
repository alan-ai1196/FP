"""Audit independent file-source and learner clocks, retained profiles and frozen scoring."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from causal_tokens import TokenSources, TokenWindow
from fp_reference.learner import LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.semantics import evaluate
from audit_native_tokens import fixture, complete
from audit_enclosed_tokens import compare_pending
import native_readout as readout
import native_tokens as tokens
import enclosed_tokens as bounded

OUTPUT = ROOT/'evidence/minimal/FP_TOKEN_SOURCE_CLOCK.json'


def refuses(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('expected refusal')


def sources(window):
    return {f'lag{lag}/token{token}': F(window.atom(lag, token))
            for lag in range(1, window.schema.context+1) for token in range(window.schema.vocabulary+1)}


def context_erasure():
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1),)*2, 1, 4, F(1, 3), 2))
    root = tokens.initialize(d, (0,), (), (0,), embedding_overrides=((1, 0, 16),))
    first = (TokenWindow(d.sources, 1, (0,)), TokenWindow(d.sources, 1, (1,)))
    last = TokenWindow(d.sources, 2, (0,))
    units, endpoints = [], []
    for window in first:
        state = bounded.begin(root)
        state = state.observe(state.predict(window), 0, window=window)
        state = state.observe(state.predict(last), 0, window=last)
        decoded = state.exact_decoder()
        endpoint = state.commit()
        assert complete(endpoint) == complete(decoded.commit())
        units.append(state)
        endpoints.append(endpoint)
    a, b = units
    assert a.origin is b.origin and a.targets == b.targets == (0, 0)
    assert a.past == b.past == (0,) and a.source_position == b.source_position == 3
    assert a.cursor == b.cursor == 2
    assert a.exact_decoder().gradient(d.embedding_slots) != b.exact_decoder().gradient(d.embedding_slots)
    assert endpoints[0].output.parameter(0, 0) == 0
    assert endpoints[1].output.parameter(0, 0) == F(1, 16)
    # The old target-only replay agrees with only the all-zero-source branch.
    wrong = root
    for target in b.targets:
        wrong = wrong.observe(wrong.predict(), target)
    assert complete(wrong.commit()) != complete(endpoints[1])
    return dict(same_origin_targets_final_context_and_both_clocks=True,
        target_only_replay_changes_native_commit=True,
        correct_target_masters=[str(s.output.parameter(0, 0)) for s in endpoints],
        complete_source_records_retained=[len(s.windows) for s in units])


def cache_binding():
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2),)*2, 1, 4, F(1, 3), 2))
    root = tokens.initialize(d, (16,), (), (16,), output_overrides=((0, 0, 32),))
    a, b = (TokenWindow(d.sources, 1, (token,)) for token in range(2))
    ca, cb = root.predict(a), root.predict(b)
    assert ca.values == cb.values and ca.output.normalizer == cb.output.normalizer
    ga = root.observe(ca, 0, window=a)
    gb = root.observe(cb, 0, window=b)
    assert ga.gradient(0) == gb.gradient(1) == F(-1, 20)
    assert ga.gradient(1) == gb.gradient(0) == 0
    refuses(lambda: root.observe(replace(ca, window=b), 0, window=a))
    refuses(lambda: root.observe(ca, 0))  # Explicit source was not the default reader.
    bounded_root = bounded.begin(root)
    bounded_cache = bounded_root.predict(a)
    refuses(lambda: bounded_root.observe(replace(bounded_cache, window=b), 0, window=a))
    refuses(lambda: bounded_root.observe(bounded_cache, 0))
    refuses(lambda: root.predict(TokenWindow(TokenSources(3, 1), 1, (0,))))
    return dict(equal_forward_values_have_different_embedding_gradient_coordinates=True,
        nonzero_coordinate_gradient='-1/20', altered_source_binding_refusals=5)


def retained_profiles():
    d, root = fixture(2, 'mixed')
    rules, graph = tokens.materialize(d)
    learner = LearnerSpec(d.output.update_unit, d.output.learning_rate, d.output.grid_bits)
    profiles = observations = commits = 0
    for tape in product(range(2), repeat=4):
        for selection in combinations(range(4), 2):
            state, enclosure = root, bounded.begin(root)
            native = initial_state(graph, rules, complete(root), 0, spec=learner, bit_limit=32768)
            for index in selection*2:
                window, target = d.sources.window(tape, index), tape[index]
                cache, interval_cache = state.predict(window), enclosure.predict(window)
                reference = evaluate(graph, rules, native.theta, sources(window), (), bit_limit=32768)
                assert tuple(cache.output.mass(y) for y in range(2)) == reference.masses
                state = state.observe(cache, target, window=window)
                enclosure = enclosure.observe(interval_cache, target, window=window)
                native = observe_event(graph, native, learner, reference, target, bit_limit=32768)
                assert complete(state) == native.theta
                assert tuple(state.gradient(i) for i in range(d.slot_count)) == native.gradient_sum
                assert state.source_position == index+1 and state.past == window.append(target).past
                assert state.cursor == native.cursor == enclosure.cursor
                compare_pending(enclosure, state)
                decoded = enclosure.exact_decoder()
                assert complete(decoded) == complete(state) and decoded.source_position == state.source_position
                assert tuple(decoded.gradient(i) for i in range(d.slot_count)) == native.gradient_sum
                observations += 1
                if state.output.unit_count == d.output.update_unit:
                    state, native = state.commit(), commit_event(native, learner, bit_limit=32768)
                    endpoint = enclosure.commit()
                    assert complete(endpoint) == complete(state) == native.theta
                    assert endpoint.source_position == state.source_position and endpoint.past == state.past
                    enclosure = bounded.begin(endpoint)
                    commits += 1
            assert state.cursor == 4 and state.source_position == selection[-1]+1
            profiles += 1
    return dict(retained_source_schedules=profiles, literal_native_observations=observations,
        literal_and_enclosed_exact_commits=commits, source_and_learner_clocks_checked_separately=True,
        no_profile_admission_or_data_role_authority=True)


def frozen_reporting():
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1),)*2, 1, 4, F(1, 16), 2))
    state = tokens.initialize(d, (16,), (), (0,),
        embedding_overrides=((1, 0, 32), (2, 0, 0)), output_overrides=((0, 0, 16),))
    for target in (0, 1, 0, 1):
        state = state.observe(state.predict(), target)
        if state.output.unit_count == 2:
            state = state.commit()
    before = state
    parameter_values = complete(state)
    rules, graph = tokens.materialize(d)
    interval_state = bounded.begin(state)
    training_probability = state.predict().output.probability(0)
    empty_window = d.sources.window((), 0)
    validation_probability = state.predict(empty_window).output.probability(0)
    assert validation_probability == F(1, 2) and training_probability != validation_probability
    count = 0
    for tape in product(range(2), repeat=4):
        window = empty_window
        for index, target in enumerate(tape):
            assert window == d.sources.window(tape, index)
            cache = state.predict(window)
            enclosure = interval_state.predict(window)
            ref = evaluate(graph, rules, parameter_values, sources(window), (), bit_limit=32768)
            assert tuple(cache.output.probability(y) for y in range(2)) == ref.probabilities
            assert all(enclosure.mass(y).contains(ref.masses[y]) for y in range(2))
            assert enclosure.normalizer.contains(ref.normalizer)
            # Reporting advances only the external source reader.
            window = window.append(target)
            assert state is before and complete(state) == parameter_values
            assert state.cursor == 4 and state.source_position == 4 and state.output.unit_count == 0
            assert all(state.gradient(i) == 0 for i in range(d.slot_count))
            count += 1
    return dict(synthetic_reporting_files=16, frozen_native_and_enclosed_predictions=count,
        trained_learner_cursor=4, reporting_source_positions=[0, 1, 2, 3],
        first_new_file_probability=str(validation_probability), leaked_training_context_probability=str(training_probability),
        complete_learner_unchanged=True, no_actual_validation_file_or_model_score=True)


def failed_explicit_observation():
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2**1024), F(1)), 1, 0, F(1, 2**1024), 1))
    root = tokens.initialize(d, (1,), (), (1,), output_overrides=((0, 0, 0),))
    state = bounded.begin(root)
    window = TokenWindow(d.sources, 7, (1,))
    cache = state.predict(window)
    try:
        state.observe(cache, 0, window=window)
    except bounded.EnclosureUnresolved as error:
        retained = error.retained_unit
        assert retained.targets == (0,) and retained.windows == (window,) and retained.past == (0,)
        decoded = retained.exact_decoder()
        assert decoded.cursor == 1 and decoded.source_position == 8
        actual = root.observe(root.predict(window), 0, window=window)
        assert tuple(decoded.gradient(i) for i in range(d.slot_count)) == tuple(actual.gradient(i) for i in range(d.slot_count))
    else:
        raise AssertionError('expected observation enclosure refusal')
    return dict(failed_new_target_retains_exact_supplied_source=True, learner_cursor=1, source_position=8)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_EXACT_TOKEN_SOURCE_CLOCK', scope='independent supplied source points and native optimizer clock; passive refinement, not owned ingestion, reporting or profile authority')
    for name, function in dict(context_erasure=context_erasure, source_binding=cache_binding,
        retained_profiles=retained_profiles, frozen_reporting=frozen_reporting, failed_observation=failed_explicit_observation).items():
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
