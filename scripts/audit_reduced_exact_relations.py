"""Exact arithmetic audit motivated by the terminal rational-feature CUDA A2.

The bounded exhaustive class and independently computed wide witness are
passive CPU evidence. No CUDA, installation or completeness token is issued.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from math import gcd
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import numerics as arithmetic, semantics
from fp_reference import rational_feature_amp as amp, joint_amp as legacy, joint_partition_decoder as decoder
from fp_reference.core import ContractError
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.float64_bridge import _Check, _ReducedCheck
from fp_reference.joint_relation import JointRelation, initialize, commit
from fp_reference.joint_execution import JointState, JointLearner, JointReferenceMachine
from fp_reference.semantics import ArithmeticUnresolved
from audit_joint_amp import BUDGET, TOLERANCE, configuration
from audit_rational_feature_amp import WIDE, Q, prediction
from audit_reference_construction import rejects
from unknown_noise_decoding import DEFAULT

OUTPUT = ROOT/'evidence/minimal/FP_REDUCED_EXACT_RELATIONS.json'


def width(value):
    return max(abs(value.numerator).bit_length(), value.denominator.bit_length())


def exhaustive():
    values = sorted({F(n, d) for n in range(-8, 9) for d in range(1, 9)})
    totals = {'compare': [0, 0], 'add': [0, 0]}
    for left, right in product(values, repeat=2):
        truth = {'compare': (left > right)-(left < right), 'add': left+right}
        for cap in (1, 3, 5, 8, 12, 32):
            for name, function in (('compare', arithmetic.compare_reduced_exact),
                                   ('add', arithmetic.add_reduced_exact)):
                try:
                    actual = function(left, right, bit_limit=cap)
                except ArithmeticUnresolved:
                    totals[name][1] += 1
                else:
                    assert actual == truth[name]
                    assert width(left) <= cap and width(right) <= cap
                    if name == 'add':
                        assert width(actual) <= cap
                    totals[name][0] += 1
        # This entire finite class fits the generous final cap.
        assert arithmetic.compare_reduced_exact(left, right, bit_limit=32) == truth['compare']
        assert arithmetic.add_reduced_exact(left, right, bit_limit=32) == truth['add']
    return dict(unique_signed_fractions=len(values), ordered_pairs=len(values)**2,
        bit_limits=[1, 3, 5, 8, 12, 32], outcomes={k: dict(exact=v[0], unresolved=v[1]) for k, v in totals.items()})


def guarded_primitives():
    huge = F((1 << 150)+1, 1 << 150)
    # The old function promises affordable unreduced comparison afterward.
    # The new function proves order only. Preserve that distinction.
    rejects(lambda: arithmetic.compare_exact(huge, huge, bit_limit=200), ArithmeticUnresolved)
    assert arithmetic.compare_reduced_exact(huge, huge, bit_limit=200) == 0
    rejects(lambda: arithmetic.compare_exact(-huge, huge, bit_limit=200), ArithmeticUnresolved)
    assert arithmetic.compare_reduced_exact(-huge, huge, bit_limit=200) == -1
    rejects(lambda: semantics._operation(huge, -huge, multiply=False, bit_limit=200), ArithmeticUnresolved)
    assert arithmetic.add_reduced_exact(huge, -huge, bit_limit=200) == 0
    # Coprime products still exceed the cap; there is no unlimited fallback.
    a, b = F(128, 129), F(129, 130)
    for function in (arithmetic.compare_reduced_exact, arithmetic.add_reduced_exact):
        rejects(lambda: function(a, b, bit_limit=9), ArithmeticUnresolved)
        rejects(lambda: function(huge, F(0), bit_limit=100), ArithmeticUnresolved)
        for value in (0, 1.0, True):
            rejects(lambda: function(value, F(1), bit_limit=200), ContractError)
            rejects(lambda: function(F(1), value, bit_limit=200), ContractError)
        for cap in (0, -1, True, 3.0):
            rejects(lambda: function(F(0), F(1), bit_limit=cap), ContractError)
    # Even an easily known zero sum can refuse a conservative numerator
    # preflight. No universal optimality or all-fitting-results claim.
    rejects(lambda: arithmetic.add_reduced_exact(F(128), F(-128), bit_limit=8), ArithmeticUnresolved)

    original_operation, original_guard, original_gcd = arithmetic._operation, arithmetic._guard, arithmetic.gcd
    rows = []
    for addition in (False, True):
        observed = []
        for left, right in ((F(0), F(0)), (F(-2, 3), F(4, 9)), (huge, huge), (huge, -huge), (a, b)):
            counts = dict(operation=0, guard=0, gcd=0)

            def operation(*args, **kwargs):
                counts['operation'] += 1
                return original_operation(*args, **kwargs)

            def guard(*args, **kwargs):
                counts['guard'] += 1
                return original_guard(*args, **kwargs)

            def counted_gcd(*args):
                counts['gcd'] += 1
                assert all(abs(v).bit_length() <= 512 for v in args)
                return original_gcd(*args)

            function = arithmetic.add_reduced_exact if addition else arithmetic.compare_reduced_exact
            with patch.object(arithmetic, '_operation', operation), patch.object(arithmetic, '_guard', guard), \
                    patch.object(semantics, '_guard', guard), patch.object(arithmetic, 'gcd', counted_gcd):
                function(left, right, bit_limit=512)
            assert counts == dict(operation=4 if addition else 2, guard=10 if addition else 5, gcd=2)
            assert sum(counts.values()) <= arithmetic.reduced_exact_work(addition=addition)
            observed.append(counts)
        rows.append(dict(addition=addition, cases=len(observed), instrumented_calls=observed[0],
            tariff=arithmetic.reduced_exact_work(addition=addition)))
    return dict(old_raw_product_promise_preserved=True, no_unbounded_fallback=True,
        conservative_zero_sum_can_remain_unresolved=True, primitive_call_checks=rows,
        scope='guarded operation/guard/GCD call counts; proof also prices quotients and scalar work; not bigint bit-time')


class PricedCheck(_ReducedCheck):
    """Passive accounting of relation arithmetic, with independent tariffs."""
    total = 0

    def exact(self, *args, **kwargs):
        type(self).total += 4
        return super().exact(*args, **kwargs)

    def compare(self, *args, **kwargs):
        type(self).total += 64
        return super().compare(*args, **kwargs)

    def add(self, *args, **kwargs):
        type(self).total += 96
        return super().add(*args, **kwargs)

    def mul(self, *args, **kwargs):
        type(self).total += 24
        return super().mul(*args, **kwargs)


def wide_continuation():
    model = JointRelation(2, *WIDE, feature_scale=F(4))
    budget = replace(BUDGET, step_cap=100)
    machine, spec = JointReferenceMachine(model, budget), JointLearner(model)
    reference = JointState(initialize(model))
    physical = amp.JointAmpState(reference.encoded)
    maximum_price = 0
    maximum_error = F(0)
    witness = None
    with memoryview(bytearray(decoder.workspace_bytes(model, budget))) as scratch:
        for T in range(82):
            _, raw, cache, _, _ = prediction(physical.encoded, (0, 0), scratch, budget)
            PricedCheck.total = 0
            with patch.object(amp, '_Check', PricedCheck):
                amp.check_prediction(cache, raw, TOLERANCE, normalizer_cap=F(6), activation_cap=F(2), bit_limit=32768)
            maximum_price = max(maximum_price, PricedCheck.total)
            if T == 81:
                # A compare-only repair remains insufficient: raw mass addition
                # multiplies two wide denominators even though the sum is 4.
                class CompareOnly(_Check):
                    compare = _ReducedCheck.compare

                with patch.object(amp, '_Check', CompareOnly):
                    rejects(lambda: amp.check_prediction(cache, raw, TOLERANCE,
                        normalizer_cap=F(6), activation_cap=F(2), bit_limit=32768), ArithmeticUnresolved)
                rejects(lambda: _Check(TOLERANCE, 32768).add(*cache.masses), ArithmeticUnresolved)
                assert _ReducedCheck(TOLERANCE, 32768).add(*cache.masses) == 4
                rejects(lambda: machine.observe(model, reference, spec, cache, 0, bit_limit=32768), ArithmeticUnresolved)
                a, b = 3*Q, 3*Q-1
                expected_denominator = 4*(a**T+b**T)*(a**(T+1)+b**(T+1))
                gradient = F(a**T, 4*(a**T+b**T))-F(Q*a**T, a**(T+1)+b**(T+1))
                assert gradient.denominator == expected_denominator and gradient.denominator.bit_length() == 32863
                assert reference.encoded == physical.encoded and reference.cursor == 81
                return dict(predictions=82, observed_and_committed=81, original_limit=32768,
                    old_observation_comparison=witness, compare_only_prediction_failure_at_T=81,
                    reduced_mass_sum='4', native_gradient_refusal_at_T=81,
                    exact_gradient_denominator_bits=gradient.denominator.bit_length(),
                    maximum_native_prediction_bits=width(max(cache.activation_basis()+cache.masses+cache.probabilities,
                        key=width)), maximum_observed_gradient_error_upper_2_neg_48=upper(maximum_error),
                    maximum_priced_relation_arithmetic=maximum_price, paid_relation_tariff=amp.relation_work(model),
                    scope='actual ordered CPU count continuation, exact unsigned/literal sums and passive fixed RNE; no CUDA or live Runtime failure-lifetime claim')
            observed = machine.observe(model, reference, spec, cache, 0, bit_limit=32768)
            actual, _ = amp._observation_schedule(physical, raw, 0, amp._Arithmetic(32768))
            if T == 41:
                with patch.object(amp, '_Check', _Check):
                    rejects(lambda: amp.check_state(observed, actual, TOLERANCE, bit_limit=32768), ArithmeticUnresolved)
                previous = F(0)
                for k, (x, word) in enumerate(zip(observed.gradient_forms[:4], actual.gradient_words[:4])):
                    error = abs(x-amp.single(word))
                    try:
                        arithmetic.compare_exact(error, previous, bit_limit=32768)
                    except ArithmeticUnresolved:
                        g = gcd(error.denominator, previous.denominator)
                        h = gcd(error.numerator, previous.numerator) or 1
                        raw_bits = max((error.numerator*previous.denominator).bit_length(),
                                       (previous.numerator*error.denominator).bit_length())
                        reduced_bits = max(((error.numerator//h)*(previous.denominator//g)).bit_length(),
                            ((previous.numerator//h)*(error.denominator//g)).bit_length())
                        witness = dict(T=T, coordinate=k, native_gradient_denominator_bits=x.denominator.bit_length(),
                            error_denominator_bits=error.denominator.bit_length(),
                            previous_error_denominator_bits=previous.denominator.bit_length(),
                            shared_denominator_bits=g.bit_length(), raw_cross_product_bits=raw_bits,
                            reduced_cross_product_bits=reduced_bits, error_upper_2_neg_48=upper(error))
                        assert (k, raw_bits, reduced_bits) == (2, 33492, 16732)
                        break
                    previous = max(previous, error)
                assert witness is not None
            PricedCheck.total = 0
            with patch.object(amp, '_Check', PricedCheck):
                relation = amp.check_state(observed, actual, TOLERANCE, bit_limit=32768)
            maximum_price = max(maximum_price, PricedCheck.total)
            assert maximum_price < amp.relation_work(model)
            maximum_error = max(maximum_error, relation.state_error)
            reference = machine.commit(observed, spec, bit_limit=32768)
            physical = amp.JointAmpState(commit(actual.encoded))
            amp.check_state(reference, physical, TOLERANCE, bit_limit=32768)
    raise AssertionError('missing materialized-gradient boundary')


def upper(value):
    grid = 1 << 48
    return str(F((value.numerator*grid+value.denominator-1)//value.denominator, grid))


def owner_tariff():
    for C in (None, F(10)):
        model = JointRelation(3, *DEFAULT, feature_scale=C)
        # Read only the closed tariff dispatch; constructing a real prefix
        # would require CUDA admission and is outside this CPU audit.
        prefix = object.__new__(_CudaPrefix)
        prefix.contract = configuration(model)
        dimension = model.n*(model.n-1)//2+2*model.n+8*len(model.rates)+32
        assert prefix.relation_work(model, model.rules()) == (512 if C is None else 2048)*dimension
        assert prefix.contract.work_model.startswith(legacy.WORK_MODEL if C is None else amp.WORK_MODEL)
    return dict(new_rational_feature_coefficient=2048, unchanged_unit_feature_coefficient=512,
        complete_description_dispatch=True, work_model=amp.WORK_MODEL,
        arithmetic_model='guarded integer, GCD, quotient and scalar primitive tariff; independent bit cap and physical host cap')


def main():
    result = dict(status='PASS_REDUCED_EXACT_RELATIONS', exhaustive=exhaustive(),
        guards_and_primitives=guarded_primitives(), continuation=wide_continuation(), owner_tariff=owner_tariff())
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
