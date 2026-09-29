"""Passive exact/float64 audit of the existing token learner's floor-grid U.

No new corpus, Runtime/device replay, timing, text score or changed optimizer.
The small loss witness uses exact likelihood products, not numerical logs.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import token_native as tokens, token_readout as readout
from fp_reference.token_causal import TokenSources
from fp_reference.learner import LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.semantics import evaluate

OUTPUT = ROOT/'evidence/minimal/FP_TOKEN_GRID_DYNAMICS.json'


def parameters(state):
    return tuple(state.parameter(i) for i in range(state.definition.slot_count))


def gradients(state):
    return tuple(state.gradient(i) for i in range(state.definition.slot_count))


def source(window):
    return {f'lag{lag}/token{token}': F(int(value == token))
            for lag, value in enumerate(window.past, 1)
            for token in range(window.schema.vocabulary+1)}


def simple(bits, eta, unit, embedding, w0, w1):
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1),)*2, 1, bits, eta, unit))
    return tokens.initialize(d, (embedding,), (), (w0,),
        output_overrides=((1, 0, w1),))


def reached(root, word):
    """Compare every actual native observation with its literal positive DAG."""
    d = root.definition
    assert len(word) == d.output.update_unit
    rules, graph = tokens.materialize(d)
    spec = LearnerSpec(d.output.update_unit, d.output.learning_rate, d.output.grid_bits)
    scalar = initial_state(graph, rules, parameters(root), 0, spec=spec, bit_limit=32768)
    state, records, likelihood = root, [], F(1)
    for target in word:
        prediction = state.predict()
        literal = evaluate(graph, rules, scalar.theta, source(prediction.window), (), bit_limit=32768)
        assert tuple(prediction.output.probability(y) for y in range(2)) == literal.probabilities
        records.append((prediction.window, target))
        likelihood *= literal.probabilities[target]
        state = state.observe(prediction, target)
        scalar = observe_event(graph, scalar, spec, literal, target, bit_limit=32768)
        assert gradients(state) == scalar.gradient_sum
        assert parameters(state) == scalar.theta
        assert (state.cursor, state.output.unit_count) == (scalar.cursor, scalar.unit_count)
    endpoint, scalar = state.commit(), commit_event(scalar, spec, bit_limit=32768)
    assert parameters(endpoint) == scalar.theta and gradients(endpoint) == scalar.gradient_sum
    assert endpoint.source_window() == records[-1][0].append(word[-1])
    assert endpoint.output.optimizer_steps == scalar.optimizer_steps == 1
    return state, endpoint, tuple(records), likelihood


def grid_cells():
    counts, histories, observations = Counter(), 0, 0
    for bits, eta, unit, embedding, head in product(
            (0, 1), (F(0), F(1, 16), F(1), F(2), F(8)), (1, 2), (0, 1, 3),
            ((0, 0), (0, 1), (1, 0), (1, 4))):
        root = simple(bits, eta, unit, embedding, *head)
        q = root.definition.output.grid
        for word in product((0, 1), repeat=unit):
            pending, endpoint, _, _ = reached(root, word)
            for theta, g, following in zip(parameters(root), gradients(pending), parameters(endpoint)):
                m, n = theta*q, following*q
                assert m.denominator == n.denominator == 1
                a = eta*q*g/unit
                ceiling = -(-a.numerator//a.denominator)
                assert n == max(0, m-ceiling)
                assert (n > m) == (a <= -1)
                assert (n < m) == (m > 0 and a > 0)
                assert (n == m) == ((-1 < a <= 0) if m > 0 else (a > -1))
                continuous = max(F(0), theta-eta*g/unit)
                assert -F(1, q) < following-continuous <= 0
                counts['parameter_decisions'] += 1
                counts['positive_subquantum'] += int(0 < a < 1)
                counts['negative_subquantum'] += int(-1 < a < 0)
                counts['boundary_minus_one'] += int(a == -1)
                counts['boundary_zero'] += int(a == 0)
                counts['boundary_plus_one'] += int(a == 1)
                counts['strict_projection_to_zero'] += int(m-a < 0)
            histories += 1
            observations += unit
    assert all(counts[key] > 0 for key in counts), counts
    return dict(histories=histories, observations=observations,
        complete_literal_gradient_and_endpoint_equality=True, **dict(counts))


def likelihood_at(state, records):
    result = F(1)
    for window, target in records:
        result *= state.predict(window).output.probability(target)
    return result


def collapse_witness():
    word = (1, 0, 0, 1, 1, 1)
    rows, future_units = [], 0
    for eta in (F(0), F(1, 16), F(1, 1 << 32)):
        root = simple(0, eta, 6, 1, 1, 4)
        pending, endpoint, records, before = reached(root, word)
        after = likelihood_at(endpoint, records)
        assert gradients(pending) == (F(9, 70), F(3, 70), F(-3, 35), F(-1, 7), F(2, 35))
        assert before == F(2500, 117649)
        if eta == 0:
            assert parameters(endpoint) == parameters(root) and after == before
        else:
            assert parameters(endpoint) == (F(0), F(0), F(1), F(1), F(3))
            assert after == F(1, 48) < before
            # Every possible next complete unit; the accompanying proof extends
            # the invariant to all future units and every eta in (0,1).
            for continuation in product((0, 1), repeat=6):
                state = endpoint
                for target in continuation:
                    prediction = state.predict()
                    assert tuple(prediction.output.probability(y) for y in range(2)) == (F(1, 2),)*2
                    state = state.observe(prediction, target)
                state = state.commit()
                assert parameters(state) == parameters(endpoint)
                assert gradients(state) == (F(0),)*5
                assert state.cursor == 12 and state.output.optimizer_steps == 2
                assert state.past == (continuation[-1],)
                future_units += 1
            # An explicitly counterfactual, unrounded step on the same frozen
            # unit decreases loss. It is not substituted for the registered U.
            rules, graph = tokens.materialize(root.definition)
            theta = tuple(max(F(0), v-eta*g/6) for v, g in zip(parameters(root), gradients(pending)))
            continuous = F(1)
            for window, target in records:
                continuous *= evaluate(graph, rules, theta, source(window), (), bit_limit=32768).probabilities[target]
            assert continuous > before
        rows.append(dict(learning_rate=str(eta), before_likelihood=str(before),
            after_likelihood=str(after), endpoint=[str(v) for v in parameters(endpoint)],
            unrounded_same_unit_strictly_improves=(eta > 0)))
    return dict(word=list(word), grid_bits=0, initial=[1, 1, 1, 1, 4],
        accumulated_gradient=['9/70', '3/70', '-3/35', '-1/7', '2/35'],
        cases=rows, all_next_unit_continuations_checked=future_units,
        theorem_learning_rate_interval='0 < eta < 1',
        before_over_after_likelihood='120000/117649',
        future_zero_context_absorption_is_conditional_theorem=True)


def absent_labels():
    # The feature is zero in two units: the clock counts active units, not
    # all units. A later observed target revives the retained zero coordinate.
    spec = readout.Spec((F(1),)*3, 1, 0, F(1, 1 << 32), 1)
    state = readout.initialize(spec, (3,))
    trajectory, active = [], 0
    for feature in (F(0), F(1), F(0), F(1), F(1), F(1)):
        old = state.parameter(2, 0)
        state, _ = state.observe(state.predict((feature,)), 0)
        expected = state.common[0]
        assert state.gradient(2, 0) == expected
        state = state.commit()
        active += int(feature > 0)
        assert state.parameter(2, 0) == max(F(0), old-int(feature > 0))
        trajectory.append(int(state.parameter(2, 0)))
    assert trajectory == [3, 2, 2, 1, 0, 0] and active == 4
    # A distinct registered rate demonstrates why zero does not erase future
    # trainability. This is a separate trajectory from its own initialization.
    state = readout.initialize(readout.Spec((F(1),)*3, 1, 0, F(1), 1), (1,))
    state, _ = state.observe(state.predict((F(1),)), 0)
    state = state.commit()
    assert state.parameter(2, 0) == 0
    state, _ = state.observe(state.predict((F(4),)), 2)
    state = state.commit()
    assert state.parameter(2, 0) > 0
    return dict(absent_master_trajectory=trajectory, feature_sequence=[0, 1, 0, 1, 1, 1],
        separate_observed_label_revival_master=str(state.parameter(2, 0)),
        zero_parameters_retained=True)


def full_vocabulary():
    import numpy as np
    from fp_reference import token_batch as batch
    from audit_token_reference_host import text_fixture
    d, origin, windows, targets, identity = text_fixture()
    bounds = batch.Kernel(d, element_cap=1 << 24).bound(origin, windows, targets)
    endpoint = bounds.commit()
    assert (endpoint.cursor, endpoint.optimizer_steps) == (512, 1)
    scale = batch.ArrayInterval.rational(d.output.grid*d.output.learning_rate/d.output.update_unit)
    embedding, core, common = scale*bounds.embedding, scale*bounds.core, scale*bounds.common
    assert np.all(embedding.lower > -1) and np.all(embedding.upper < 1)
    positive, negative = embedding.lower > 0, embedding.upper < 0
    assert np.all(positive | negative)
    assert np.array_equal(endpoint.E[bounds.embedding_ids], origin.E[bounds.embedding_ids]-positive.astype(np.uint32))
    decrement_low, decrement_high = np.ceil(common.lower), np.ceil(common.upper)
    assert np.array_equal(decrement_low, decrement_high)
    absent = np.ones(d.output.labels, dtype=bool)
    absent[bounds.correction_ids] = False
    expected = np.maximum(0, origin.W[absent].astype(np.int64)-decrement_low.astype(np.int64))
    assert np.array_equal(endpoint.W[absent], expected)
    rows = {}
    for name in ('E', 'C', 'W'):
        old, new = getattr(origin, name), getattr(endpoint, name)
        delta = new.astype(np.int64)-old.astype(np.int64)
        rows[name] = dict(coordinates=int(old.size), unchanged=int(np.sum(delta == 0)),
            increased=int(np.sum(delta > 0)), decreased=int(np.sum(delta < 0)),
            newly_zero=int(np.sum((old > 0) & (new == 0))),
            min_integer_change=int(delta.min()), max_integer_change=int(delta.max()))
    assert rows['E']['decreased'] == 465 and rows['E']['increased'] == 0
    assert rows['C']['newly_zero'] == 2 and rows['W']['increased'] == 1992
    return dict(status='RESOLVED_OUTWARD_FLOAT64_NATIVE_GRID_CELLS', source=identity,
        vocabulary=d.output.labels, grid_bits=d.output.grid_bits, learning_rate=str(d.output.learning_rate),
        update_unit=d.output.update_unit, scaled_gradient_factor=str(d.output.grid*d.output.learning_rate/d.output.update_unit),
        complete_native_master_coordinates=d.slot_count, changes=rows,
        active_embedding_rows=len(bounds.embedding_ids),
        active_embedding_positive_gradients=int(np.sum(positive)),
        active_embedding_negative_gradients=int(np.sum(negative)),
        scaled_embedding_enclosure=[float(embedding.lower.min()), float(embedding.upper.max())],
        core_before=origin.C.tolist(), core_after=endpoint.C.tolist(),
        scaled_core_lower=core.lower.tolist(), scaled_core_upper=core.upper.tolist(),
        observed_target_rows=len(bounds.correction_ids), absent_target_rows=int(np.sum(absent)),
        scaled_common_lower=common.lower.tolist(), scaled_common_upper=common.upper.tolist(),
        absent_label_integer_decrement=decrement_low.astype(int).tolist(),
        independent_full_v_rational_decoder=False, actual_amp_result=False,
        runtime_replay=False, corpus_loss_scored=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = dict(status='PASS', exact_grid_cells=grid_cells(),
        exact_causal_collapse=collapse_witness(), exact_absent_labels=absent_labels(),
        existing_full_v_unit=full_vocabulary(),
        scope='passive optimizer diagnosis; no changed Gamma/U, device replay, timing or text score')
    assert 'torch' not in sys.modules
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
