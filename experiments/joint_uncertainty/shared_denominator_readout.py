"""Positive common-denominator elimination, with complete native learner checks.

This passive compiler optimizes the graph before construction. It does not
quotient an executing Program, add a native division, or issue AMP authority.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math

from positive_rational_readout import (
    BITS, ROOT, RationalCircuit, lower, spanning_tree_circuit, tree_oracle,
    checked_prediction, selected_degree, degree_recurrence,
    forward_fixed_gradient, ArithmeticUnresolved, evaluate, ce_gradient,
    SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState, initial_state,
    observe_event, commit_event, attach_boundary,
)
from fp_reference import float64_learner as f64
from fp_reference.binary_arithmetic import Float64Arithmetic


def upward_error(value):
    """A short exact upper enclosure; full error fractions add no audit value."""
    assert value >= 0
    scaled = value*(1 << 96)
    return str(F((scaled.numerator+scaled.denominator-1)//scaled.denominator, 1 << 96))


def common_denominator_tree_circuit(n):
    """Every surviving edge is N_ij/Q; the common Q need not be evaluated."""
    assert type(n) is int and n >= 2
    root = n-1
    edges = tuple((i, j) for i in range(root) for j in range(n) if i != j)
    circuit = RationalCircuit(len(edges))
    numerators = dict(zip(edges, circuit.inputs))
    remaining = list(range(n))
    pivots = []
    for v in range(n-1):
        others = [u for u in remaining if u != v]
        incident = [numerators[v, u] for u in others]
        total = incident[0]
        for numerator in incident[1:]:
            total = circuit.op('add', total, numerator)
        pivots.append(total)
        for i, j in product(others, repeat=2):
            if i == j or i == root:
                continue
            direct = circuit.op('mul', numerators[i, j], total)
            via = circuit.op('mul', numerators[i, v], numerators[v, j])
            numerators[i, j] = circuit.op('add', direct, via)
        remaining.remove(v)

    # Product_t(S_t/Q_t), Q_t=Product_(u<t) S_u. Cancel only formal,
    # positive factors, before native compilation: R=S_last/D.
    prefix = denominator = circuit.one
    for pivot in pivots[:-2]:
        prefix = circuit.op('mul', prefix, pivot)
        denominator = circuit.op('mul', denominator, prefix)
    head = circuit.op('div', pivots[-1], denominator)
    return circuit, head, edges


def setup(n):
    circuit, head, edges = common_denominator_tree_circuit(n)
    rules, graph = lower(circuit, head)
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                      simplex_slots=tuple(range(1, len(edges)+1)))
    return circuit, head, edges, rules, graph, spec


def small_tree_audit():
    checked = 0
    for n in range(2, 7):
        _, _, edges, rules, graph, _ = setup(n)
        original, original_head, original_edges = spanning_tree_circuit(n)
        assert edges == original_edges
        d = len(edges)
        priors = [(F(0),)*d, (F(1, d),)*d,
                  tuple(F(i+1, d*(d+1)//2) for i in range(d)),
                  (F(1),)+(F(0),)*(d-1), (F(0),)*(d-1)+(F(1),)]
        for theta in priors:
            checked_prediction(original, original_head, rules, graph, theta,
                               oracle=tree_oracle(n, theta))
            checked += 1
    return {'n_values': list(range(2, 7)), 'independent_enumerated_tree_cases': checked,
            'complete_native_gradient_checks': 2*checked}


def learner_audit():
    checked = profiles = 0
    for n in (2, 3, 4):
        _, _, edges, rules, graph, spec = setup(n)
        d = len(edges)
        theta = tuple(F(i+1, d*(d+1)//2) for i in range(d))
        initial = initial_state(graph, rules, (F(1),)+theta, 0, spec=spec, bit_limit=BITS)

        def step(state, target):
            nonlocal checked
            value, slopes = tree_oracle(n, state.theta[1:])
            prediction = evaluate(graph, rules, state.theta, {'one': F(1)}, (), bit_limit=BITS)
            assert prediction.probabilities == (value/(1+value), 1/(1+value))
            selected = tuple(-g/(value*(1+value)) if target == 0 else g/(1+value) for g in slopes)
            full = (forward_fixed_gradient(graph, rules, state.theta, {'one': F(1)}, target),)+selected
            observed = observe_event(graph, state, spec, prediction, target, bit_limit=BITS)
            assert observed == ReferenceLearnerState(state.theta, (), full, 1,
                                                     state.cursor+1, state.optimizer_steps)
            mean = sum(w*g for w, g in zip(state.theta[1:], selected))
            updated = tuple(w*(1-g+mean) for w, g in zip(state.theta[1:], selected))
            assert max(selected)-min(selected) < 1 and min(updated) > 0 and sum(updated) == 1
            committed = commit_event(observed, spec, bit_limit=BITS)
            assert committed == ReferenceLearnerState((F(1),)+updated, (), (F(0),)*(d+1),
                                                      0, state.cursor+1, state.optimizer_steps+1)
            checked += 1
            return committed

        frontier = [initial]
        for _ in range(3):
            frontier = [step(state, y) for state in frontier for y in (0, 1)]
        state = step(step(initial, 0), 0)
        attached = attach_boundary(state, 12, spec)
        assert attached == replace(state, cursor=12)
        step(attached, 1)
        profiles += 1
    return {'native_observe_commit_pairs': checked, 'complete_state_checks': 2*checked,
            'all_binary_history_depth': 3, 'two_pass_profile_attachments': profiles}


def checked_binary64(rules, graph, spec, theta, exact_prediction):
    """Actual registered CPU primitives, each checked against exact rounding.

    Relative value and absolute learner errors are diagnostics with fixed
    audit thresholds, not an issued complete Runtime bridge.
    """
    arithmetic = Float64Arithmetic(BITS)
    phase = 'initialize'
    try:
        state = f64.initialize(graph, rules, (F(1),)+theta, 0, arithmetic)
        phase = 'forward'
        prediction = f64.evaluate(graph, rules, state, {'one': F(1)}, arithmetic)
        assert exact_prediction is not None
        actual_values = prediction.values+prediction.masses+(prediction.normalizer,)
        exact_values = exact_prediction.values+exact_prediction.masses+(exact_prediction.normalizer,)
        value_error = max(abs(a.exact-b)/max(F(1), abs(b)) for a, b in zip(actual_values, exact_values))
        probability_error = max(abs(a.exact-b) for a, b in zip(prediction.probabilities, exact_prediction.probabilities))
        gradient_error = state_error = F(0)
        reference = initial_state(graph, rules, (F(1),)+theta, 0, spec=spec, bit_limit=BITS)
        for target in (0, 1):
            phase = f'observe_{target}'
            actual_observed = f64.observe_event(graph, state, spec, prediction, target, arithmetic)
            exact_observed = observe_event(graph, reference, spec, exact_prediction, target, bit_limit=BITS)
            gradient_error = max(gradient_error, *(abs(a.exact-b) for a, b in zip(actual_observed.gradient_sum, exact_observed.gradient_sum)))
            phase = f'commit_{target}'
            actual_committed = f64.commit_event(actual_observed, spec, arithmetic)
            exact_committed = commit_event(exact_observed, spec, bit_limit=BITS)
            state_error = max(state_error, *(abs(a.exact-b) for a, b in zip(actual_committed.theta, exact_committed.theta)))
            assert actual_committed.delayed == () and actual_committed.unit_count == 0
            assert actual_committed.cursor == actual_committed.optimizer_steps == 1
            assert all(g.exact == 0 for g in actual_committed.gradient_sum)
        assert value_error < F(1, 10**9) and probability_error < F(1, 10**12)
        assert gradient_error < F(1, 10**9) and state_error < F(1, 10**9)
        return {'status': 'PASS_TWO_COMPLETE_UNITS', 'checked_scalar_operations': arithmetic.operations,
                'maximum_relative_native_value_error_upper': upward_error(value_error),
                'maximum_absolute_probability_error_upper': upward_error(probability_error),
                'maximum_absolute_full_gradient_error_upper': upward_error(gradient_error),
                'maximum_absolute_committed_parameter_error_upper': upward_error(state_error)}
    except ArithmeticUnresolved as exc:
        return {'status': 'UNRESOLVED', 'phase': phase, 'reason': str(exc),
                'checked_scalar_operations': arithmetic.operations}


def resource_audit():
    previous = json.loads((ROOT/'evidence/minimal/FP_POSITIVE_RATIONAL_READOUT.json').read_text())
    previous = {r['n']: r for r in previous['resource_pressure']['rows']}
    rows = []
    for n in (*range(2, 14), 16):
        circuit, head, edges, rules, graph, spec = setup(n)
        d = len(edges)
        degree = 2**(n-2)
        assert selected_degree(graph) == degree
        row = {'n': n, 'rational_nodes': len(circuit.nodes), 'native': graph.counts(),
               'maximum_selected_degree': degree, 'denominator_degree': degree-n+1,
               'old_emitter_degree': degree_recurrence(n)}
        if n in previous:
            row['retained_old_exact_status'] = previous[n].get('exact', 'NOT_RUN')
            row['retained_old_binary64_status'] = previous[n].get('binary64', {}).get('status', 'NOT_RUN')
        if n > 13:
            row['evaluation'] = 'NOT_RUN; syntax and degree only'
            rows.append(row)
            continue
        theta = (F(1, d),)*d
        w = F(d+1, d)
        value = n**(n-2)*w**(n-1)
        slopes = tuple(F(2 if j == n-1 else 1, n)*n**(n-2)*w**(n-2) for i, j in edges)
        row['exact_probability_oracle'] = str(value/(1+value))
        prediction = None
        try:
            original, original_head, _ = spanning_tree_circuit(n)
            prediction = checked_prediction(original, original_head, rules, graph, theta,
                                             oracle=(value, slopes))
            coefficient = math.prod(k**(2**(k-3)) for k in range(3, n+1))
            assert prediction.masses[0] == coefficient*w**degree
            assert prediction.masses[1] == coefficient*w**degree/value
            retained = prediction.values+prediction.masses+(prediction.normalizer,)+prediction.probabilities
            row.update(exact='PASS', maximum_forward_operand_bits=max(max(x.numerator.bit_length(),
                       x.denominator.bit_length()) for x in retained))
        except ArithmeticUnresolved as exc:
            row.update(exact='UNRESOLVED', reason=str(exc))
        row['checked_binary64'] = checked_binary64(rules, graph, spec, theta, prediction)
        rows.append(row)
    return {'reference_integer_bits': BITS, 'rows': rows,
            'reference_operand_representation': 'explicit reduced rational scalars',
            'forward_operand_scope': 'retained values, masses, normalizer and probabilities; excludes arithmetic temporaries',
            'reported_error_upper_grid_bits': 96,
            'relative_value_and_absolute_gradient_state_tolerance': '1/1000000000',
            'absolute_probability_tolerance': '1/1000000000000',
            'old_rows_are_retained_evidence_not_rerun': True,
            'Runtime_or_AMP_authority': False}


def state_and_denominator_witnesses():
    _, _, edges, rules, graph, _ = setup(4)
    theta = (F(1),)+(F(1, len(edges)),)*len(edges)
    prediction = evaluate(graph, rules, theta, {'one': F(1)}, (), bit_limit=BITS)
    wrong = prediction.masses[0]/(prediction.masses[0]+1)
    assert wrong != prediction.probabilities[0]
    original, head, _ = spanning_tree_circuit(4)
    old_rules, old_graph = lower(original, head)
    old_prediction = evaluate(old_graph, old_rules, theta, {'one': F(1)}, (), bit_limit=BITS)
    old_gradient = ce_gradient(old_graph, theta, old_prediction, 1, bit_limit=BITS)
    new_gradient = ce_gradient(graph, theta, prediction, 1, bit_limit=BITS)
    assert old_prediction.probabilities == prediction.probabilities
    assert old_gradient[1:] == new_gradient[1:] and old_gradient[0] != new_gradient[0]
    return {'n': 4, 'correct_probability0': str(prediction.probabilities[0]),
            'erased_denominator_probability0': str(wrong),
            'old_fixed_feature_gradient': str(old_gradient[0]),
            'new_fixed_feature_gradient': str(new_gradient[0]),
            'selected_gradients_identical_but_complete_observed_states_different': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS_WITH_DECLARED_NUMERICAL_REFUSALS',
              'scope': 'passive positive compiler and complete CPU learner audits; no Runtime or AMP authority',
              'tree_oracle': small_tree_audit(), 'complete_learner': learner_audit(),
              'resource_pressure': resource_audit(), 'nonerasable_information': state_and_denominator_witnesses()}
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
