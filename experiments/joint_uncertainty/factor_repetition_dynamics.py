"""Passive native audit of factor certainty and rational height under repetition.

All events are distinct legal noisy observations. This audits the existing
simplex U; it issues no Runtime, resource, AMP or installation certificate.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
import factor_simplex_posterior as native
from factor_query_matroid import factor_query_graph, inputs
from fp_reference import float64_learner as f64
from fp_reference.binary_arithmetic import Float64Arithmetic
from fp_reference.semantics import ArithmeticUnresolved

BITS = 32768
ORACLE_BITS = 131072
WORLDS = native.worlds_for((2, 2))
TABLES = tuple(tuple(z[0] if q == 0 else z[1] if q == 1 else z[0] ^ z[1]
                     for z in WORLDS) for q in range(3))


class NativeRefusal(Exception):
    def __init__(self, phase, reason):
        super().__init__(reason)
        self.phase = phase


def guarded(phase, function):
    try:
        return function()
    except ArithmeticUnresolved as exc:
        raise NativeRefusal(phase, str(exc)) from exc


def setup(sizes=(2, 2), rate=None, factors=None):
    rules, graph = factor_query_graph(sizes, TABLES)
    spec = native.spec_for(graph, len(sizes), rate)
    factors = factors or tuple((F(1, k),)*k for k in sizes)
    state = native.initial_state(graph, rules, native.factors_to_theta(factors),
                                 0, spec=spec, bit_limit=BITS)
    return rules, graph, spec, state, factors


def checked_step(rules, graph, spec, state, factors, query, label):
    """Independent tensor/forward-dual checks of both complete native boundaries."""
    m, sizes = len(factors), tuple(map(len, factors))
    worlds = native.worlds_for(sizes)
    source = inputs(3, query)
    table = tuple(tuple(8*int(bit == y) for y in (0, 1)) for bit in TABLES[query])
    assert state.theta == native.factors_to_theta(factors)
    prediction = guarded('evaluate', lambda: native.evaluate(
        graph, rules, state.theta, source, (), bit_limit=BITS))
    assert prediction.normalizer == 10 and all(0 <= v <= 8 for v in prediction.values)
    weights = native.joint_weights(factors, worlds)
    masses = tuple(1+sum(w*c[y] for w, c in zip(weights, table)) for y in (0, 1))
    assert prediction.masses == masses
    assert prediction.probabilities == tuple(v/10 for v in masses)
    gradient = guarded('gradient', lambda: native.ce_gradient(
        graph, state.theta, prediction, label, bit_limit=BITS))
    selected = []
    for j, k in enumerate(sizes):
        for b in range(k):
            conditional = sum((c[label]*math.prod(factors[i][z[i]] for i in range(m) if i != j)
                               for z, c in zip(worlds, table) if z[j] == b), F(0))
            selected.append(m*(F(4, 5)-conditional/masses[label]))
    fixed = native.forward_fixed_gradient(graph, rules, state.theta, source, label)
    assert gradient == (fixed,)+tuple(selected)
    observed = guarded('observe', lambda: native.observe_event(
        graph, state, spec, prediction, label, bit_limit=BITS))
    assert observed == native.ReferenceLearnerState(state.theta, (), gradient, 1,
                                                   state.cursor+1, state.optimizer_steps)
    committed = guarded('commit', lambda: native.commit_event(observed, spec, bit_limit=BITS))
    exact_joint = native.posterior(weights, table, label, rules.base)
    marginals = native.marginals(exact_joint, worlds, sizes)
    alpha = m*spec.learning_rate
    updated = tuple(tuple((1-alpha)*a+alpha*b for a, b in zip(q, post))
                    for q, post in zip(factors, marginals))
    assert committed == native.ReferenceLearnerState(native.factors_to_theta(updated), (),
        (F(0),)*graph.slot_count, 0, state.cursor+1, state.optimizer_steps+1)
    return committed, updated, prediction, observed


def full_bayes(k):
    scale = 9**k
    return tuple(F(w, 82*scale+18) for w in (81*scale, 9, 9, scale))


def anchor_forecast(weights):
    return sum(w*F(9 if z[0] == 0 else 1, 10) for w, z in zip(weights, WORLDS))


def integer_height_audit():
    """Independent integer recurrence, never serialize large numerators."""
    a, b = 4, 5
    rows = []
    for k in range(16):
        assert 0 < a < b and math.gcd(a, b) == 1
        assert max(a.bit_length(), b.bit_length()) <= ORACLE_BITS
        assert F(b+a, 4*b).denominator == F(b-a, 4*b).denominator == 4*b
        oracle = full_bayes(k)
        assert oracle[0]/oracle[3] == 81
        true_bias = sum(w*(1 if z[0] == 0 else -1) for w, z in zip(oracle, WORLDS))
        assert true_bias == F(40*9**k, 41*9**k+9)
        if k:
            assert 5*a > 4*b
        assert F(a, b) == true_bias if k <= 1 else F(a, b) > true_bias
        row = {'repetitions': k, 'bias_numerator_bits': a.bit_length(),
               'bias_denominator_bits': b.bit_length(),
               'selected_parameter_denominator_bits': (4*b).bit_length(),
               'full_bayes_maximum_parameter_bits': max(max(w.numerator.bit_length(),
                    w.denominator.bit_length()) for w in oracle)}
        if k <= 3:
            row['bias'] = str(F(a, b))
            row['product_00_to_11_odds'] = str(F((b+a)**2, (b-a)**2))
        if k >= 2:
            assert a % 2 == 0 and a % 3 == 0 and a % 5 != 0
            assert b % 2 == 1 and b % 3 != 0 and b % 5 != 0
        if k < 15:
            aa, bb = 9*a*b, 5*b*b+4*a*a
            assert max(aa.bit_length(), bb.bit_length()) <= ORACLE_BITS
            divisor = math.gcd(aa, bb)
            row['next_reduction_gcd'] = divisor
            if k >= 2:
                assert divisor == 1 and 5*b*b < bb < 9*b*b
            a, b = aa//divisor, bb//divisor
        rows.append(row)
    return {'integer_oracle_bit_cap': ORACLE_BITS, 'rows': rows,
            'scope': 'explicit reduced scalar height; no encoded-description lower bound'}


def native_height_audit():
    rules, graph, spec, state, factors = setup()
    # Kept in memory only, for independent binary64 comparison of the passed prefix.
    trace, rows = [], []
    last_bias = F(4, 5)
    for query in [0, 1]+[2]*16:
        old_state = state
        try:
            state, factors, prediction, observed = checked_step(
                rules, graph, spec, state, factors, query, 0)
        except NativeRefusal as exc:
            assert state == old_state
            refusal = {'status': 'UNRESOLVED', 'attempted_cursor': state.cursor+1,
                       'attempted_repetition': state.cursor-1, 'phase': exc.phase,
                       'reason': str(exc), 'last_complete_cursor': state.cursor}
            break
        trace.append((prediction, observed, state))
        if state.cursor >= 2:
            bias = factors[0][0]-factors[0][1]
            assert factors[0] == factors[1]
            if state.cursor > 2:
                assert bias == 9*last_bias/(5+4*last_bias**2)
            last_bias = bias
            rows.append({'repetitions': state.cursor-2,
                         'bias_denominator_bits': bias.denominator.bit_length(),
                         'largest_parameter_denominator_bits': max(v.denominator.bit_length() for v in state.theta)})
    else:
        raise AssertionError('expected the fixed native arithmetic guard to refuse')
    assert state.cursor == 13 and refusal['attempted_repetition'] == 12
    return {'native': graph.counts(), 'reference_integer_bits': BITS,
            'native_units': len(trace), 'complete_state_checks': 2*len(trace),
            'bounded_internal_values': [0, 8], 'normalizer': 10,
            'rows': rows, 'refusal': refusal}, trace


def full_joint_control():
    rules, graph, spec, state, factors = setup((4,))
    rows = []
    for query in [0, 1]+[2]*128:
        state, factors, _, _ = checked_step(rules, graph, spec, state, factors, query, 0)
        if state.cursor >= 2:
            k = state.cursor-2
            assert factors[0] == full_bayes(k)
            prediction = native.evaluate(graph, rules, state.theta, inputs(3, 0), (), bit_limit=BITS)
            assert prediction.probabilities[0] == anchor_forecast(full_bayes(k))
            if k in (0, 1, 2, 11, 12, 15, 32, 64, 128):
                rows.append({'repetitions': k, 'maximum_parameter_bits': max(max(v.numerator.bit_length(),
                    v.denominator.bit_length()) for v in state.theta)})
    return {'status': 'PASS', 'native': graph.counts(), 'native_units': state.cursor,
            'complete_state_checks': 2*state.cursor, 'reference_integer_bits': BITS,
            'retained_00_to_11_odds': '81', 'rows': rows}


def signed_damping_audit():
    """Asymmetric priors, both likelihood signs and actual fixed native rates."""
    values = (F(-4, 5), F(-1, 10), F(0), F(1, 10), F(4, 5))
    rates = (F(0), F(1, 8), F(1, 4), F(1, 2))
    units = 0
    for u, v in product(values, repeat=2):
        factors = tuple((F(1, 2)+a/2, F(1, 2)-a/2) for a in (u, v))
        for rate in rates:
            rules, graph, spec, initial, _ = setup(rate=rate, factors=factors)
            for label in (0, 1):
                _, updated, _, _ = checked_step(rules, graph, spec, initial, factors, 2, label)
                rho = F(4 if label == 0 else -4, 5)
                alpha = 2*rate
                expected = ((1-alpha)*u+alpha*(u+rho*v)/(1+rho*u*v),
                            (1-alpha)*v+alpha*(v+rho*u)/(1+rho*u*v))
                actual = tuple(q[0]-q[1] for q in updated)
                assert actual == expected
                if not label and rate:
                    s, d = u+v, u-v
                    ss, dd = actual[0]+actual[1], actual[0]-actual[1]
                    assert ss == s*(1+alpha*rho*(1-u*v)/(1+rho*u*v))
                    assert dd == d*(1-alpha*rho*(1+u*v)/(1+rho*u*v))
                    assert (not s and not ss) or abs(ss) > abs(s)
                    assert (not d and not dd) or abs(dd) < abs(d)
                units += 1
    return {'signed_prior_pairs': 25, 'fixed_rates': list(map(str, rates)),
            'label_branches': 2, 'native_units': units, 'complete_state_checks': 2*units}


def upward_error(value, bits=96):
    scale = 1 << bits
    return str(F((value.numerator*scale+value.denominator-1)//value.denominator, scale))


def checked_binary64(trace):
    rules, graph, spec, initial, _ = setup()
    arithmetic = Float64Arithmetic(BITS)
    state = f64.initialize(graph, rules, initial.theta, 0, arithmetic)
    value_error = probability_error = gradient_error = state_error = F(0)
    for index, query in enumerate([0, 1]+[2]*64):
        prediction = f64.evaluate(graph, rules, state, inputs(3, query), arithmetic)
        observed = f64.observe_event(graph, state, spec, prediction, 0, arithmetic)
        state = f64.commit_event(observed, spec, arithmetic)
        assert state.cursor == state.optimizer_steps == index+1
        assert observed.cursor == index+1 and observed.optimizer_steps == index
        assert observed.delayed == state.delayed == () and observed.unit_count == 1
        assert state.unit_count == 0 and all(g.exact == 0 for g in state.gradient_sum)
        if index < len(trace):
            p, o, s = trace[index]
            value_error = max(value_error, *(abs(a.exact-b) for a, b in zip(
                prediction.values+prediction.masses+(prediction.normalizer,), p.values+p.masses+(p.normalizer,))))
            probability_error = max(probability_error, *(abs(a.exact-b) for a, b in zip(prediction.probabilities, p.probabilities)))
            gradient_error = max(gradient_error, *(abs(a.exact-b) for a, b in zip(observed.gradient_sum, o.gradient_sum)))
            state_error = max(state_error, *(abs(a.exact-b) for a, b in zip(state.theta, s.theta)))
    forecast = f64.evaluate(graph, rules, state, inputs(3, 0), arithmetic)
    probability = forecast.probabilities[0].exact
    true_probability = anchor_forecast(full_bayes(64))
    assert abs(probability-F(9, 10)) < F(1, 10**12)
    assert probability-true_probability > F(9, 1000)
    assert max(value_error, probability_error, gradient_error, state_error) < F(1, 10**12)
    assert all(v.exact > 0 for v in state.theta)
    return {'status': 'PASS_CHECKED_PRIMITIVES', 'native_units': state.cursor,
            'complete_state_boundaries': 2*state.cursor,
            'checked_scalar_operations': arithmetic.operations,
            'complete_reference_compared_units': len(trace),
            'maximum_absolute_native_value_error_upper': upward_error(value_error),
            'maximum_absolute_probability_error_upper': upward_error(probability_error),
            'maximum_absolute_full_gradient_error_upper': upward_error(gradient_error),
            'maximum_absolute_committed_parameter_error_upper': upward_error(state_error),
            'error_upper_grid_bits': 96,
            'terminal_anchor_probability0': str(probability),
            'terminal_anchor_probability0_float': float(probability),
            'full_bayes_anchor_probability0_float': float(true_probability),
            'terminal_gap_above': '9/1000', 'every_terminal_parameter_still_positive': True,
            'scope': 'exact rounding checks throughout; native-reference comparison only on passed prefix; no Runtime or AMP bridge'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    heights = integer_height_audit()
    reference, trace = native_height_audit()
    result = {'status': 'PASS_WITH_DECLARED_NATIVE_REFERENCE_REFUSAL',
              'scope': 'passive learner dynamics; distinct legal observations; no production changes or execution authority',
              'history': {'anchor': [[0, 1, 0], [0, 2, 0]], 'repeated_event': [1, 2, 0],
                          'Gamma': 'uniform four-world prior', 'noise': '1/10'},
              'explicit_rational_height': heights, 'native_factor': reference,
              'full_joint_control': full_joint_control(), 'signed_damping': signed_damping_audit(),
              'checked_binary64': checked_binary64(trace),
              'limiting_anchor_forecasts': {'native_factor': '9/10', 'full_bayes': '73/82', 'gap': '2/205'},
              'erased_information': 'relative odds of worlds 00 and 11; every repeated event gives them identical likelihood'}
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
