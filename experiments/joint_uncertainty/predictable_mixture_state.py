"""Exact audit of a positive representation of predictable mixture evidence.

Passive scalar research only: no Runtime endpoint, experiment registration,
model tape, supplied certificate, installation or new GPU execution.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'evidence/minimal/FP_PREDICTABLE_MIXTURE_STATE.json'


@lru_cache(maxsize=None)
def moment(k):
    return F(comb(2*k, k), 4**k)


@lru_cache(maxsize=None)
def integral_weights(t):
    """Integer numerators for integral b^k(1-b)^(t-k) against arcsine."""
    denominator = 4**t
    weight = comb(2*t, t)
    numerators = [weight]
    for k in range(t):
        numerator, divisor = weight*(2*k+1), 2*(t-k)-1
        assert numerator % divisor == 0
        weight = numerator//divisor
        numerators.append(weight)
    assert sum(comb(t, k)*w for k, w in enumerate(numerators)) == denominator
    return tuple(numerators), denominator


def rounded_step(numbers, score):
    """Numbers represent nonnegative Bernstein coefficients on one fixed grid."""
    assert numbers and all(type(v) is int and v >= 0 for v in numbers)
    assert type(score) is F and -1 <= score <= 1
    z = 1+score
    return (numbers[0],)+tuple(
        (numbers[k] if k < len(numbers) else 0)+z.numerator*numbers[k-1]//z.denominator
        for k in range(1, len(numbers)+1))


def exact_step(coefficients, score):
    z = 1+score
    return (coefficients[0],)+tuple(
        (coefficients[k] if k < len(coefficients) else 0)+z*coefficients[k-1]
        for k in range(1, len(coefficients)+1))


def polynomial_step(coefficients, score):
    """Independent signed monomial expansion of product(1+b*score)."""
    return (coefficients[0],)+tuple(
        (coefficients[k] if k < len(coefficients) else 0)+score*coefficients[k-1]
        for k in range(1, len(coefficients)+1))


def readout(numbers, bits):
    t = len(numbers)-1
    denominator, weight = 1 << (2*t), 1
    for j in range(1, t+1):
        numerator = weight*2*(2*j-1)
        assert numerator % j == 0
        weight = numerator//j
    total = first = 0
    for k, n in enumerate(numbers):
        total += n*weight
        first += n*weight*(2*k+1)
        if k < t:
            numerator, divisor = weight*(2*k+1), 2*(t-k)-1
            assert numerator % divisor == 0
            weight = numerator//divisor
    assert total > 0
    wealth = F(total, (1 << bits)*denominator)
    bet = F(first, 2*(t+1)*total)
    assert 0 < bet < 1
    return wealth, bet


def independent_readout(coefficients, extra=0):
    return sum((value*moment(j+extra) for j, value in enumerate(coefficients)), F(0))


def expanded(coefficients):
    t = len(coefficients)-1
    return tuple(sum((coefficients[k]*comb(t-k, j-k)*(-1)**(j-k)
                      for k in range(j+1)), F(0)) for j in range(t+1))


def finite_audit():
    alphabet = tuple(map(F, (-1, F(-1, 3), 0, F(1, 2), 1)))
    horizon, extra_bits = 6, 16
    grids = (3, horizon+extra_bits)
    counts = {'complete_scalar_words': 0, 'prefixes': 0,
              'rounded_state_updates': 0, 'zero_mean_null_pairs': 0,
              'nonpositive_point_nulls': 0, 'independent_readouts': 0}
    maximum_bits = 0

    def visit(past, polynomial, exact, states):
        nonlocal maximum_bits
        t = len(past)
        counts['prefixes'] += 1
        ideal = independent_readout(polynomial)
        assert expanded(exact) == polynomial
        for bits, state in zip(grids, states):
            wealth, bet = readout(state, bits)
            positive = tuple(F(n, 1 << bits) for n in state)
            own_poly = expanded(positive)
            assert wealth == independent_readout(own_poly)
            assert bet*wealth == independent_readout(own_poly, 1)
            assert 0 <= ideal-wealth <= F(2**t-1, 1 << bits)
            assert wealth >= moment(t) > 0 and state[0] == 1 << bits
            assert all(0 <= low <= high for low, high in zip(positive, exact))
            assert max(n.bit_length() for n in state) <= bits+2*t+1
            maximum_bits = max(maximum_bits, *(n.bit_length() for n in state))
            counts['independent_readouts'] += 1
            if t == horizon:
                if bits == horizon+extra_bits:
                    assert ideal-wealth < F(1, 1 << extra_bits)
                continue
            values = {score: readout(rounded_step(state, score), bits)[0] for score in alphabet}
            assert all(value <= wealth*(1+bet*score) for score, value in values.items())
            for score in alphabet:
                if score <= 0:
                    assert values[score] <= wealth
                    counts['nonpositive_point_nulls'] += 1
            for negative in (x for x in alphabet if x < 0):
                for positive_score in (x for x in alphabet if x > 0):
                    p = -negative/(positive_score-negative)
                    assert p*positive_score+(1-p)*negative == 0
                    assert p*values[positive_score]+(1-p)*values[negative] <= wealth
                    counts['zero_mean_null_pairs'] += 1
        if t == horizon:
            counts['complete_scalar_words'] += 1
            return
        for score in alphabet:
            after = tuple(rounded_step(state, score) for state in states)
            counts['rounded_state_updates'] += len(after)
            visit(past+(score,), polynomial_step(polynomial, score), exact_step(exact, score), after)

    visit((), (F(1),), (F(1),), tuple((1 << bits,) for bits in grids))
    assert counts['complete_scalar_words'] == 5**horizon
    assert counts['prefixes'] == sum(5**k for k in range(horizon+1))
    return {'horizon': horizon, 'score_alphabet': list(map(str, alphabet)),
            'coefficient_grid_bits': grids, **counts, 'maximum_coefficient_numerator_bits': maximum_bits}


def regret_audit():
    terms = sharp = 0
    for t in range(65):
        weights, denominator = integral_weights(t)
        ratio = F(4**t, comb(2*t, t))
        if t:
            assert ratio**2 <= 4*t
        for k, weight in enumerate(weights):
            b = F(k, t) if t else F(0)
            assert b**k*(1-b)**(t-k) <= ratio*F(weight, denominator)
            terms += 1
        numbers = (1 << 96,)+(0,)*t
        wealth, _ = readout(numbers, 96)
        assert ratio*wealth == 1
        sharp += 1
    return {'largest_horizon': 64, 'basis_maximum_checks': terms,
            'all_adverse_sharp_ratio_checks': sharp,
            'regret_factor_at_64': str(F(4**64, comb(128, 64)))}


def state_counterexamples():
    left, right = (F(1, 2), F(-4, 11)), (F(0), F(0))

    def polynomial(word):
        values = (F(1),)
        for value in word:
            values = polynomial_step(values, value)
        return values

    curves = tuple(polynomial(word) for word in (left, right))
    assert tuple(independent_readout(p) for p in curves) == (F(1), F(1))
    first = tuple(independent_readout(p, 1) for p in curves)
    assert first == (F(87, 176), F(1, 2))
    after = tuple(independent_readout(polynomial_step(p, F(1, 2))) for p in curves)
    assert after[1]-after[0] == F(1, 352)
    order = (F(-1, 4), F(1, 2))
    rounded = []
    for word in (order, tuple(reversed(order))):
        state = (2,)
        for value in word:
            state = rounded_step(state, value)
        rounded.append(state)
    assert rounded == [(2, 4, 1), (2, 4, 2)]
    assert tuple(readout(s, 1)[0] for s in rounded) == (F(13, 16), F(1))
    assert polynomial(order) == polynomial(tuple(reversed(order)))
    all_good = (F(1),)*3
    assert independent_readout(polynomial(all_good)) == F(63, 16) < 4
    assert F(7, 4)**3 > 4
    return {'same_wealth_and_clock': {'words': [list(map(str, left)), list(map(str, right))],
                'wealths': ['1', '1'], 'first_moments': list(map(str, first)),
                'common_continuation': '1/2', 'subsequent_wealths': list(map(str, after))},
            'rounding_destroys_permutation_equivalence': {'grid_bits': 1,
                'word': list(map(str, order)), 'forward_and_reverse_numerators': rounded,
                'forward_and_reverse_wealths': ['13/16', '1']},
            'no_first_passage_dominance': {'three_scores': ['1']*3, 'threshold': '4',
                'mixture_wealth': '63/16', 'fixed_fraction_3_over_4_wealth': str(F(7, 4)**3)}}


def horizon_audit():
    horizon, extra = 64, 32
    bits = horizon+extra
    words = ((F(1),)*horizon, (F(-1),)*horizon,
             tuple(F((-1)**t, 3) for t in range(horizon)),
             tuple(F((17*t)%19-9, 9) for t in range(horizon)))
    maxima = {'coefficient_numerator_bits': 0, 'wealth_numerator_bits': 0,
              'wealth_denominator_bits': 0, 'coefficient_payload_bits': 0}
    for word in words:
        numbers, polynomial = (1 << bits,), (F(1),)
        for t, score in enumerate(word, 1):
            numbers = rounded_step(numbers, score)
            polynomial = polynomial_step(polynomial, score)
            wealth, _ = readout(numbers, bits)
            assert 0 <= independent_readout(polynomial)-wealth <= F(2**t-1, 1 << bits) < F(1, 1 << extra)
            assert wealth.numerator.bit_length() <= bits+3*t+1
            assert wealth.denominator.bit_length() <= bits+2*t+1
            maxima['coefficient_numerator_bits'] = max(maxima['coefficient_numerator_bits'], *(n.bit_length() for n in numbers))
            maxima['wealth_numerator_bits'] = max(maxima['wealth_numerator_bits'], wealth.numerator.bit_length())
            maxima['wealth_denominator_bits'] = max(maxima['wealth_denominator_bits'], wealth.denominator.bit_length())
            maxima['coefficient_payload_bits'] = max(maxima['coefficient_payload_bits'], sum(n.bit_length() for n in numbers))
    return {'horizon': horizon, 'fractional_bits': bits, 'uniform_absolute_error_upper': str(F(1, 1 << extra)),
            'deterministic_words': len(words), 'verified_prefixes': len(words)*horizon,
            'word_definitions': ['all +1', 'all -1', 'alternating +/-1/3', '((17*t)%19-9)/9'],
            'measured_integer_encoding_maxima': maxima,
            'scope': 'integer bit lengths, not Python/process/owned resource bytes'}


def native_audit():
    sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
    from audit_simplex_learner import fixture
    from fp_reference.learner import initial_state, observe_event, commit_event
    from fp_reference.semantics import evaluate
    from fp_reference.numerics import log_enclosure
    from simplex_gradient import context
    from log_enclosure_audit import verify_log_ratio
    cfg, graph, online, _ = fixture(2)
    state = initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                          spec=online.learner, bit_limit=32768)
    prediction = evaluate(graph, cfg.semantics, state.theta, context(2, 0, 0), bit_limit=32768)
    assert prediction.probabilities == (F(9, 10), F(1, 10))
    scores = []
    for p in prediction.probabilities:
        gain = log_enclosure(2*p, terms=12, bit_limit=32768)
        verify_log_ratio(p, F(1, 2), gain.lower, gain.upper)
        assert F(-13, 8) <= gain.lower <= gain.upper <= F(13, 8)
        scores.append(gain.lower/F(13, 8))
    for labels in product((0, 1), repeat=5):
        low, exact = (1 << 21,), (F(1),)
        current = state
        for label in labels:
            prediction = evaluate(graph, cfg.semantics, current.theta, context(2, 0, 0), bit_limit=32768)
            assert prediction.probabilities == (F(9, 10), F(1, 10))
            current = commit_event(observe_event(graph, current, online.learner, prediction,
                label, bit_limit=32768), online.learner, bit_limit=32768)
            low, exact = rounded_step(low, scores[label]), polynomial_step(exact, scores[label])
        assert current.cursor == current.optimizer_steps == 5
        assert 0 <= independent_readout(exact)-readout(low, 21)[0] < F(1, 1 << 16)
    return {'exact_native_self_forecast': ['9/10', '1/10'], 'label_words': 32,
            'native_pre_target_forecasts': 160, 'complete_native_units': 160,
            'coefficient_bits': 21, 'absolute_error_upper': '1/65536',
            'scope': 'native forecast and scalar recurrence; no owned persistence or installation'}


def audit():
    result = {'status': 'EXACT_PASSIVE_MIXTURE_STATE_AUDIT_PASS',
        'scope': 'classical continuous mixture, positive state and finite precision proofs; no Runtime extension',
        'retained_model_tapes_used': False, 'new_model_or_baseline_workers': 0,
        'finite_model_check': finite_audit(), 'classical_regret': regret_audit(),
        'counterexamples': state_counterexamples(), 'horizon_and_precision': horizon_audit(),
        'native_score_check': native_audit()}
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
