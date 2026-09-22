"""Exact alternative-order AMP plans and complete native-coordinate audits."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import indexed_amp as amp, projected_amp, query_order
from fp_reference.indexed_execution import IndexedEvaluation, IndexedState
from fp_reference.float64_bridge import Float64Contract
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.learner import observe_event
from audit_indexed_amp_plan_binding import evaluate_plan
from audit_reference_construction import rejects
import audit_projected_amp as exact
import audit_indexed_amp as legacy


def choose(n, support, query, join, live):
    # Passive numerical audit only. Owned payment is tested separately.
    result = query_order.search(n, support, query, join, live,
                                bytearray(query_order.workspace_bytes(n, query)))
    if result is None:
        raise ArithmeticUnresolved('empty structural order class')
    return result.order


def numeric(planner):
    cases = [(3, counts, query) for counts in product((-1, 0, 1), repeat=3)
             for query in product(range(3), repeat=2)]
    for a, b in product((-2, 0, 2), repeat=2):
        cases.extend((5, (a, -1, b, 0, a, 0, 0, 0, 0, b), query)
                     for query in ((0, 4), (1, 4), (4, 1), (2, 2)))
    cases.append((4, (-2, -2, -2, -2, -2, -1), (0, 3)))
    fixtures = {n: exact.native_fixture(n) for n in (3, 4, 5)}
    predictions = observations = half = reordered = 0
    maximum = {key: F(0) for key in ('native', 'probability', 'division', 'gradient')}
    unresolved = []
    tolerance = Float64Contract(F(1, 100), F(1, 1000))
    for n, counts, query in cases:
        args = exact.arguments(n, counts, query)
        schema, before, rules, sources = args
        plan = planner._prepare_prediction(*args, output_cap=262144, order_search=choose)
        planner.check_prediction_plan(plan, *args, output_cap=262144, allow_orders=True)
        natural = planner.prepare_prediction(*args, output_cap=262144)
        reordered += plan.orders != natural.orders
        raw, operations = evaluate_plan(plan, before)
        assert len(operations)+7 == plan.output_cells
        amp.check_prediction_execution(plan, before, raw, operations, bit_limit=32768)
        half += sum(len(words) for _, width, words in operations if width == 16)
        _, graph, spec, _ = fixtures[n]
        native = exact.native_counts.decode(before.encoded)
        expected = evaluate(graph, rules, native.theta, sources, (), bit_limit=32768)
        reference = IndexedEvaluation(before.encoded, query, expected.excesses, expected.masses,
                                     expected.normalizer, expected.probabilities, ())
        diagnostics = amp.check_prediction(reference, raw, Float64Contract(F(1), F(1)),
            normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
        full = raw.decoded().materialize(scalar_cap=10000)
        assert diagnostics.native_error == max(abs(x-y) for x, y in zip(
            expected.values+expected.masses, full.values+full.masses))
        for key, value in (('native', diagnostics.native_error), ('probability', diagnostics.probability_error),
                           ('division', diagnostics.division_error)):
            maximum[key] = max(maximum[key], value)
        try:
            amp.check_prediction(reference, raw, tolerance, normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768)
        except ArithmeticUnresolved as exc:
            unresolved.append({'n': n, 'counts': counts, 'query': query, 'phase': 'prediction', 'reason': str(exc)})
        predictions += 1
        for target in (0, 1):
            arithmetic = amp._Arithmetic(32768)
            observed, _ = amp._observation_schedule(before, raw, target, arithmetic)
            complete = observe_event(graph, native, spec, expected, target, bit_limit=32768)
            mass = expected.masses[target]
            reference_state = IndexedState(observed.encoded, (1/mass-F(1, 5), F(4, 5)-8/mass, F(4, 5)))
            relation = amp.check_state(reference_state, observed, Float64Contract(F(1), F(1)), bit_limit=32768)
            decoded = legacy.component.CompactState(observed.encoded, observed.gradient_words).materialize(scalar_cap=10000)
            assert complete.theta == decoded.theta
            assert relation.state_error == max(abs(x-y) for x, y in zip(complete.gradient_sum, decoded.gradient_sum))
            maximum['gradient'] = max(maximum['gradient'], relation.state_error)
            try:
                amp.check_state(reference_state, observed, tolerance, bit_limit=32768)
            except ArithmeticUnresolved as exc:
                unresolved.append({'n': n, 'counts': counts, 'query': query, 'phase': 'observe',
                                   'target': target, 'reason': str(exc)})
            observations += 1
    return {'predictions': predictions, 'observations': observations, 'selected_order_differs_from_natural': reordered,
        'half_outputs': half, 'maximum_complete_coordinate_errors': {k: str(v) for k, v in maximum.items()},
        'fixed_tolerance_unresolved': unresolved}


def binding(planner):
    args = exact.arguments(4, (-2, -2, -2, -2, -2, -1), (0, 3))
    plan = planner._prepare_prediction(*args, output_cap=65536, order_search=choose)
    fields = 0
    for changes in ({'orders': ()}, {'orders': ((0, 0, 2),)}, {'orders': ((False, 1, 2),)},
                    {'orders': [plan.orders[0]]}, {'positions': plan.positions[::-1]},
                    {'nodes': plan.nodes[:-1]}, {'output_cells': 0},
                    {'orders': ((1, 0, 2),)}):
        # A changed valid order with the old tape also must refuse.
        bad = replace(plan, **changes)
        rejects(lambda: planner.check_prediction_plan(bad, *args, output_cap=65536, allow_orders=True))
        fields += 1
    alternative = planner._prepare_prediction(*args, output_cap=65536, orders=((1, 0, 2),))
    planner.check_prediction_plan(alternative, *args, output_cap=65536, allow_orders=True)
    rejects(lambda: planner.check_prediction_plan(alternative, *args, output_cap=65536))
    return {'order_or_tape_substitutions_refused': fields,
        'complete_alternative_order_accepted_in_expanded_class': True,
        'same_alternative_refused_in_fixed_natural_class': True}


def cpu():
    def prepare(*args, **kwargs):
        return projected_amp._prepare_prediction(*args, **kwargs, order_search=choose)
    with patch.object(projected_amp, 'prepare_prediction', prepare):
        exhaustive = exact.exhaustive()
    return {'status': 'PASS_PAID_ORDER_PASSIVE_AMP',
        'scope': 'exact structural plans, RNE and complete native-coordinate relations; no device or owned resource authority',
        'projected_complete_small_tapes': exhaustive,
        'global': numeric(amp), 'projected': numeric(projected_amp),
        'global_order_class_binding': binding(amp), 'projected_order_class_binding': binding(projected_amp)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = cpu()
    if args.write:
        (ROOT/'evidence/minimal/FP_PAID_ORDER_AMP_CPU.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
