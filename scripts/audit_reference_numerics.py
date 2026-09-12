"""Independent rational-tail and Decimal audits of the reference log kernel.

Exact identities audit the enclosure formula. High-precision Decimal is a
separate numerical diagnostic, not the mathematical source of certification.
No stochastic persistence, abstract-real/AMP bridge or installation is tested.
"""
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))

from fp_reference.core import ContractError
from fp_reference.numerics import (LogInterval, compare_exact, compare_exact_work,
                                  floor_nonnegative_dyadic, log_enclosure, log_enclosure_work)
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.numerics as numerical
import fp_reference.semantics as semantic_arithmetic


def rejects(operation, exception=ContractError):
    try:
        operation()
    except exception:
        return
    raise AssertionError(f'expected {exception.__name__}')


def exact_oracle(value, terms):
    """Explicit powers/sums and repeated reduction, independent of kernel guards."""
    reduced, exponent = value, 0
    while reduced >= 2:
        reduced /= 2
        exponent += 1
    while reduced < 1:
        reduced *= 2
        exponent -= 1

    def series(x):
        z = (x-1)/(x+1)
        partial = sum((2*z**(2*j+1)/(2*j+1) for j in range(terms)), F(0))
        remainder = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
        # A longer exact partial sum lies inside the claimed tail bound.
        longer = sum((2*z**(2*j+1)/(2*j+1) for j in range(terms+5)), F(0))
        assert partial <= longer <= partial+remainder
        return partial, partial+remainder

    lo, hi = series(reduced)
    a, b = series(F(2))
    return lo+min(exponent*a, exponent*b), hi+max(exponent*a, exponent*b)


def decimal_check(value, enclosure):
    # Near-one inputs need enough digits to retain their original displacement.
    precision = max(100, max(value.numerator.bit_length(), value.denominator.bit_length())*31//100+70)
    with localcontext() as context:
        context.prec = precision
        argument = Decimal(value.numerator)/Decimal(value.denominator)
        truth = argument.ln()
        lo = Decimal(enclosure.lower.numerator)/Decimal(enclosure.lower.denominator)
        hi = Decimal(enclosure.upper.numerator)/Decimal(enclosure.upper.denominator)
        # Explicit numerical-diagnostic slack covers Decimal conversion/rounding;
        # it is never returned by the production enclosure or used as evidence.
        slack = Decimal(10)**(-precision+20)*max(Decimal(1), abs(truth))
        assert lo-slack <= truth <= hi+slack


def log_audit():
    ordinary = sorted({F(n, d) for n in range(1, 18) for d in range(1, 18)})
    extreme = [F(1, 1 << 1200), F(1 << 1200), F(1, 10**500), F(10**500),
               F((1 << 1200)+1, 1 << 1200), F((1 << 1200)-1, 1 << 1200),
               F(3, 1 << 1200), F(3 << 1200), F((1 << 513)+7, (1 << 389)+3)]
    cases = decimal_checks = 0
    for value in ordinary+extreme:
        previous = None
        for terms in (1, 4, 12):
            interval = log_enclosure(value, terms=terms, bit_limit=150000)
            assert (interval.lower, interval.upper) == exact_oracle(value, terms)
            if previous is not None:
                assert previous.lower <= interval.lower <= interval.upper <= previous.upper
            previous = interval
            decimal_check(value, interval)
            decimal_checks += 1
            cases += 1
        inverse = log_enclosure(1/value, terms=12, bit_limit=150000)
        assert previous.lower+inverse.lower <= 0 <= previous.upper+inverse.upper

    two = log_enclosure(F(2), terms=12, bit_limit=150000)
    for exponent in (-1200, -91, -1, 0, 1, 67, 1200):
        actual = log_enclosure(F(2)**exponent, terms=12, bit_limit=150000)
        assert (actual.lower, actual.upper) == (min(exponent*two.lower, exponent*two.upper),
                                               max(exponent*two.lower, exponent*two.upper))
    product_checks = 0
    for a in (F(1, 97), F(2, 3), F(1), F(7, 3), F(97)):
        for b in (F(1, 101), F(3, 7), F(1), F(11, 2), F(101)):
            first = log_enclosure(a, terms=8, bit_limit=150000)
            second = log_enclosure(b, terms=8, bit_limit=150000)
            combined = log_enclosure(a*b, terms=8, bit_limit=150000)
            assert max(combined.lower, first.lower+second.lower) <= min(combined.upper, first.upper+second.upper)
            product_checks += 1
    return {'exact_formula_and_nested_tail_cases': cases,
            'independent_decimal_diagnostics': decimal_checks,
            'reciprocal_identity_cases': len(ordinary)+len(extreme),
            'exact_power_of_two_identity_cases': 7,
            'log_product_interval_identity_cases': product_checks,
            'extreme_argument_exponent': 1200,
            'near_one_sub_binary64_displacements_retained': True}


def floor_audit():
    values = sorted({F(n, d) for n in range(26) for d in range(1, 18)})
    cases = 0
    for bits in (0, 1, 3, 8, 32):
        previous = F(0)
        for value in values:
            actual = floor_nonnegative_dyadic(value, bits=bits, bit_limit=512)
            expected = F(value.numerator*(1 << bits)//value.denominator, 1 << bits)
            assert actual == expected and 0 <= actual <= value < actual+F(1, 1 << bits)
            assert previous <= actual
            previous = actual
            cases += 1
    assert floor_nonnegative_dyadic(F(1, 1 << 1200), bits=32, bit_limit=2048) == 0
    assert floor_nonnegative_dyadic(F(1, 1 << 1200), bits=1200, bit_limit=4096) == F(1, 1 << 1200)
    return {'exact_grid_and_monotonicity_cases': cases,
            'tiny_positive_value_may_conservatively_round_to_zero': True}


def comparison_audit():
    values = sorted({F(n, d) for n in range(-9, 10) for d in range(1, 10)})
    cases = 0
    for left in values:
        for right in values:
            expected = (left > right)-(left < right)
            assert compare_exact(left, right, bit_limit=64) == expected
            cases += 1
    huge = [F(-1, 1 << 1200), F(0), F(1, 1 << 1200),
            F((1 << 1200)-1, (1 << 1200)+1),
            F((1 << 1200)+1, (1 << 1200)-1)]
    for left in huge:
        for right in huge:
            assert compare_exact(left, right, bit_limit=4096) == (left > right)-(left < right)
    for bad in (0, 1.0, True, float('inf'), float('nan')):
        rejects(lambda bad=bad: compare_exact(bad, F(1), bit_limit=64))
        rejects(lambda bad=bad: compare_exact(F(1), bad, bit_limit=64))
    for bad in (0, -1, True, 64.0):
        rejects(lambda bad=bad: compare_exact(F(1), F(2), bit_limit=bad))
    rejects(lambda: compare_exact(F(1, 1 << 1200), F(0), bit_limit=512), ArithmeticUnresolved)
    expensive = F((1 << 150)+1, 1 << 150)
    # Each input fits. The raw cross products do not; equality and mixed signs
    # intentionally do not bypass the registered fixed arithmetic operation.
    rejects(lambda: compare_exact(expensive, expensive, bit_limit=200), ArithmeticUnresolved)
    rejects(lambda: compare_exact(-expensive, expensive, bit_limit=200), ArithmeticUnresolved)

    original_operation, original_guard = numerical._operation, numerical._guard
    charged_cases = 0
    for left, right in ((F(-1), F(1)), (F(0), F(0)), (F(2, 3), F(7, 11)),
                        (huge[-1], huge[-2]), (huge[0], huge[2])):
        counts = [0]

        def operation(*args, **kwargs):
            counts[0] += 1
            return original_operation(*args, **kwargs)

        def guard(*args, **kwargs):
            counts[0] += 1
            return original_guard(*args, **kwargs)

        with patch.object(numerical, '_operation', operation), patch.object(numerical, '_guard', guard), patch.object(semantic_arithmetic, '_guard', guard):
            compare_exact(left, right, bit_limit=4096)
        assert counts[0] <= compare_exact_work()
        charged_cases += 1
    return {'exact_signed_order_cases': cases, 'huge_denominator_cases': len(huge)**2,
            'input_and_raw_cross_product_exhaustion_unresolved': True,
            'no_sign_or_equality_budget_bypass': True,
            'primitive_charge_upper_checks': charged_cases}


def adversarial_audit():
    for value in (0, 1, 1.0, float('nan'), float('inf'), True, F(0), F(-1)):
        rejects(lambda value=value: log_enclosure(value, terms=4, bit_limit=512))
    for terms in (0, -1, True, 1.0):
        rejects(lambda terms=terms: log_enclosure(F(2), terms=terms, bit_limit=512))
        rejects(lambda terms=terms: log_enclosure_work(terms))
    for bits in (0, -1, True, 512.0):
        rejects(lambda bits=bits: log_enclosure(F(2), terms=4, bit_limit=bits))
    rejects(lambda: LogInterval(F(1), F(-1)))
    rejects(lambda: LogInterval(-1, 1))
    interval = LogInterval(F(-1), F(1))
    rejects(lambda: setattr(interval, 'lower', F(-2)), FrozenInstanceError)
    rejects(lambda: log_enclosure(F(1, 1 << 1200), terms=4, bit_limit=512), ArithmeticUnresolved)
    rejects(lambda: log_enclosure(F(3, 2), terms=32, bit_limit=24), ArithmeticUnresolved)
    rejects(lambda: log_enclosure(F(2), terms=1 << 128, bit_limit=64), ArithmeticUnresolved)
    rejects(lambda: floor_nonnegative_dyadic(F(-1), bits=4, bit_limit=512))
    rejects(lambda: floor_nonnegative_dyadic(F(1), bits=True, bit_limit=512))
    rejects(lambda: floor_nonnegative_dyadic(F(1), bits=1000, bit_limit=64), ArithmeticUnresolved)
    rejects(lambda: floor_nonnegative_dyadic(F(1 << 40), bits=32, bit_limit=64), ArithmeticUnresolved)

    charged_cases = 0
    original_operation, original_guard = numerical._operation, numerical._guard
    for value in (F(1), F(3, 2), F(2), F(1, 7), F(1, 1 << 1200)):
        for terms in (1, 4, 12):
            counts = [0]

            def operation(*args, **kwargs):
                counts[0] += 1
                return original_operation(*args, **kwargs)

            def guard(*args, **kwargs):
                counts[0] += 1
                return original_guard(*args, **kwargs)

            with patch.object(numerical, '_operation', operation), patch.object(numerical, '_guard', guard), patch.object(semantic_arithmetic, '_guard', guard):
                log_enclosure(value, terms=terms, bit_limit=150000)
            assert counts[0] <= log_enclosure_work(terms)
            charged_cases += 1
    return {'strict_fraction_signed_interval_and_registration_checks': True,
            'input_series_scale_and_floor_integer_exhaustion_unresolved': True,
            'primitive_charge_upper_checks': charged_cases,
            'no_unbounded_fallback_or_float_log': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = {'status': 'PASS', 'scope': 'guarded exact rational logarithm enclosure, signed ordering and monotone nonnegative dyadic floor',
              'logarithm': log_audit(), 'floor': floor_audit(), 'comparison': comparison_audit(), 'adversaries': adversarial_audit(),
              'not_closed': ['statistical stream-law and fresh persistence authority',
                             'full physical/bit-time accounting', 'abstract-real float64 or actual AMP bridge', 'atomic installation']}
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_NUMERICS_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
