"""Independent finite-format rounding and actual CPU binary64 scalar audit.

The generic oracle explicitly lists representable points and compares exact
distances; it does not use production exponent extraction, quantization or
rounding helpers. CPU checks retain raw encodings, especially signed zero.
No GPU, AMP bridge, whole-learner or installation authority is inferred.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math
import random
import struct
import sys
from unittest.mock import PropertyMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))

from fp_reference.binary_arithmetic import (BINARY64, BinaryExecutionMismatch, BinaryFormat,
                                           Float64Arithmetic, Float64Value, RoundedBinary, round_binary)
from fp_reference.core import ContractError
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.binary_arithmetic as execution


def rejects(function, error=ContractError):
    try:
        function()
    except error:
        return
    raise AssertionError('an invalid or unresolved numerical action was accepted')


def pow2(exponent):
    return F(2**exponent) if exponent >= 0 else F(1, 2**-exponent)


def points(fmt):
    quantum = pow2(fmt.emin-fmt.precision+1)
    result = {F(n)*quantum for n in range(2**(fmt.precision-1))}
    for exponent in range(fmt.emin, fmt.emax+1):
        result.update(F(n)*pow2(exponent-fmt.precision+1)
                      for n in range(2**(fmt.precision-1), 2**fmt.precision))
    return tuple(sorted(result))


def nearest_oracle(value, fmt, *, negative_zero=False):
    """Enumerated nearest point, with tie parity on the adjacent common grid.

    The virtual next power of two represents overflow after rounding. Ties
    use the spacing of the tied neighbors; this also covers precision=1,
    where one global normalized-significand parity label is insufficient.
    """
    magnitude = abs(value)
    finite = points(fmt)
    virtual = pow2(fmt.emax+1)
    choices = finite+(virtual,)
    distance = min(abs(point-magnitude) for point in choices)
    nearest = tuple(point for point in choices if abs(point-magnitude) == distance)
    if len(nearest) == 2:
        spacing = nearest[1]-nearest[0]
        chosen = next(point for point in nearest if (point/spacing).denominator == 1 and (point/spacing).numerator % 2 == 0)
    else:
        assert len(nearest) == 1
        chosen = nearest[0]
    if chosen == virtual:
        return None
    if fmt.subnormal_mode == 'flush-output' and chosen < pow2(fmt.emin):
        chosen = F(0)
    return RoundedBinary(-chosen if value < 0 else chosen, bool(not chosen and (value < 0 or not value and negative_zero)))


def exhaustive_rounding_audit():
    cases, ties, formats, overflows = 0, 0, 0, 0
    for precision, (emin, emax), mode in product(range(1, 5), ((-2, 2), (0, 0)), ('gradual', 'flush-output')):
        fmt = BinaryFormat(precision, emin, emax, mode)
        values = points(fmt)+(pow2(emax+1),)
        samples = {F(n, d) for n in range(49) for d in range(1, 10)}
        samples.update(values)
        for left, right in zip(values, values[1:]):
            midpoint = (left+right)/2
            delta = (right-left)/8
            samples.update((midpoint-delta, midpoint, midpoint+delta))
            ties += 1
        for magnitude, sign in product(sorted(samples), (1, -1)):
            value = sign*magnitude
            expected = nearest_oracle(value, fmt)
            if expected is None:
                rejects(lambda: round_binary(value, fmt, bit_limit=4096), ArithmeticUnresolved)
                overflows += 1
            else:
                assert round_binary(value, fmt, bit_limit=4096) == expected, (value, fmt, expected)
            cases += 1
        formats += 1
    return {'complete_small_format_declarations': formats,
            'signed_exact_nearest_point_comparisons': cases,
            'adjacent_midpoints_and_neighborhoods_per_sign': ties,
            'overflow_cases_checked': overflows,
            'precision_one_common_grid_ties_checked': True,
            'oracle_uses_enumerated_points_and_exact_distances': True}


def counterexample_audit():
    coarse, fine = BinaryFormat(2, -4, 4), BinaryFormat(3, -4, 4)
    value = F(21, 16)
    assert round_binary(value, coarse, bit_limit=4096).value == F(3, 2)
    intermediate = round_binary(value, fine, bit_limit=4096).value
    assert intermediate == F(5, 4) and round_binary(intermediate, coarse, bit_limit=4096).value == 1
    hardware_casts = []
    for precision, emin, emax, code in ((11, -14, 15, 'e'), (24, -126, 127, 'f')):
        value = F(1)+pow2(-precision)+pow2(-54)
        expected = F(1)+pow2(1-precision)
        assert round_binary(value, BinaryFormat(precision, emin, emax), bit_limit=4096).value == expected
        converted = struct.unpack('>'+code, struct.pack('>'+code, float(value)))[0]
        assert converted == 1.0 and F.from_float(float(value)) == F(1)+pow2(-precision)
        hardware_casts.append({'target_precision': precision, 'direct_result': str(expected), 'via_binary64_result': '1'})

    fmt = BinaryFormat(3, 0, 2, 'flush-output')
    assert round_binary(F(7, 8), fmt, bit_limit=4096).value == 1
    assert round_binary(F(7, 8)-F(1, 64), fmt, bit_limit=4096).value == 0
    assert round_binary(F(3, 4), fmt, bit_limit=4096).value == 0
    # Output flushing is neither pre-round flushing nor nearest rounding in
    # a format from which subnormal points were deleted.
    assert abs(F(3, 4)-1) < abs(F(3, 4)-0)
    a, b, c = F(5, 4), F(5, 4), F(1, 8)
    fused = round_binary(a*b+c, fine, bit_limit=4096).value
    separate = round_binary(round_binary(a*b, fine, bit_limit=4096).value+c, fine, bit_limit=4096).value
    assert fused == F(7, 4) and separate == F(3, 2)
    sequential = round_binary(round_binary(F(1)+F(1, 8), fine, bit_limit=4096).value+F(1, 8), fine, bit_limit=4096).value
    assert sequential == 1 and round_binary(F(1)+F(1, 8)+F(1, 8), fine, bit_limit=4096).value == F(5, 4)
    tiny = pow2(-1200)
    assert float(tiny) == 0.0 and round_binary(tiny, BinaryFormat(3, -1200, 0), bit_limit=4096).value == tiny
    return {'toy_p3_to_p2_double_rounding': {'input': '21/16', 'direct': '3/2', 'via_p3': '1'},
            'actual_half_and_single_cast_double_rounding': hardware_casts,
            'FTZ_rounding_before_output_flush_and_input_policy_are_distinct': True,
            'positive_fused_vs_separate_result': ['7/4', '3/2'],
            'positive_single_round_vs_ordered_SUM_result': ['5/4', '1'],
            'premature_binary64_underflow_of_exact_2_to_minus1200_reproduced': True}


def from_float(value):
    return Float64Value(int.from_bytes(struct.pack('>d', value), 'big'))


def decode_oracle(bits):
    value = struct.unpack('>d', bits.to_bytes(8, 'big'))[0]
    return F.from_float(value), math.copysign(1.0, value) < 0


def check_nearest_binary64(value, exact):
    """Independent nearest-neighbor distance check at the observed encoding.

    This uses adjacent physical encodings, not production quantization. A
    finite extremum's outward neighbor is the virtual overflow power of two.
    """
    observed = value.as_float()
    point = F.from_float(observed)
    distance = abs(point-exact)
    for direction in (-math.inf, math.inf):
        adjacent = math.nextafter(observed, direction)
        neighbor = F.from_float(adjacent) if math.isfinite(adjacent) else (-1 if direction < 0 else 1)*pow2(1024)
        other = abs(neighbor-exact)
        assert distance <= other, (value, exact, neighbor)
        if distance == other:
            assert value.bits % 2 == 0


def signed_zero_and_limits_audit():
    arith = Float64Arithmetic(16384)
    zero, negative_zero = Float64Value(0), Float64Value(1 << 63)
    one, negative_one = arith.cast(F(1)), arith.cast(F(-1))
    assert zero.exact == negative_zero.exact == 0 and zero.bits != negative_zero.bits
    checked = 0
    for left, right in product((zero, negative_zero), repeat=2):
        result = arith.add(left, right)
        assert result.exact == 0 and result.negative == (left.negative and right.negative)
        result = arith.mul(left, right)
        assert result.exact == 0 and result.negative == (left.negative != right.negative)
        checked += 2
    for left, right in product((zero, negative_zero), (one, negative_one)):
        for operation in (arith.mul, arith.div):
            result = operation(left, right)
            assert result.exact == 0 and result.negative == (left.negative != right.negative)
            checked += 1
    assert arith.add(one, negative_one).bits == 0
    assert arith.add(negative_one, one).bits == 0
    assert arith.neg(zero) == negative_zero and arith.neg(negative_zero) == zero
    assert arith.positive_part(negative_zero) == zero and arith.positive_part(negative_one) == zero
    assert arith.floor_grid(negative_zero, 16) == zero
    assert round_binary(F(0), BINARY64, bit_limit=4096, negative_zero=True).negative_zero

    delta = pow2(-1074)
    for sign in (1, -1):
        for magnitude, expected in ((delta/2-delta/8, F(0)), (delta/2, F(0)), (delta/2+delta/8, delta),
                                    (3*delta/2, 2*delta), (5*delta/2, 2*delta)):
            result = arith.cast(sign*magnitude)
            assert result.exact == sign*expected
            assert result.negative == (sign < 0)
            checked += 1
        underflow = arith.mul(arith.cast(sign*delta), arith.cast(F(1, 2)))
        assert underflow.exact == 0 and underflow.negative == (sign < 0)
        checked += 1
    minimum_normal = pow2(-1022)
    midpoint = minimum_normal-delta/2
    assert arith.cast(midpoint).exact == minimum_normal
    assert arith.cast(midpoint-delta/8).exact == minimum_normal-delta
    maximum = F.from_float(sys.float_info.max)
    threshold = pow2(1024)-pow2(970)
    assert arith.cast(threshold-F(1)).exact == maximum
    assert arith.cast(-threshold+F(1)).exact == -maximum
    for value in (threshold, threshold+F(1), -threshold, -threshold-F(1)):
        rejects(lambda value=value: arith.cast(value), ArithmeticUnresolved)
    rejects(lambda: arith.mul(arith.cast(maximum), arith.cast(F(2))), ArithmeticUnresolved)
    rejects(lambda: arith.add(arith.cast(maximum), arith.cast(pow2(970))), ArithmeticUnresolved)
    for denominator in (zero, negative_zero):
        rejects(lambda denominator=denominator: arith.div(one, denominator), ArithmeticUnresolved)
    return {'signed_zero_and_underflow_checks': checked,
            'normal_subnormal_boundary_carry_checked': True,
            'exact_overflow_midpoint_and_neighbors_checked': True,
            'overflow_and_zero_division_never_return_finite_saturation': True}


def actual_binary64_audit():
    rng = random.Random(31944)
    arith = Float64Arithmetic(16384)
    encodings = [0, 1 << 63, 1, (1 << 63)+1, (1 << 52)-1, 1 << 52,
                 0x7fefffffffffffff, 0xffefffffffffffff,
                 *[rng.randrange(1 << 64) for _ in range(128)]]
    encodings = [word for word in encodings if (word >> 52) & 2047 != 2047]
    values = []
    for word in encodings:
        value = Float64Value(word)
        exact, negative = decode_oracle(word)
        assert value.exact == exact and value.negative == negative
        assert from_float(value.as_float()).bits == word
        values.append(value)
    expected_error, successful, overflow = F(0), 0, 0
    expected_operations = arith.operations
    pairs = [(rng.choice(values), rng.choice(values)) for _ in range(180)]
    pairs.extend((from_float(a), from_float(b)) for a, b in ((1.0, 2**-53), (1.0, 3*2**-53),
                                                          (1.0, -1.0), (-0.0, 0.0), (-0.0, -0.0),
                                                          (2**-1022, -2**-1022+2**-1074)))
    threshold = pow2(1024)-pow2(970)
    for left, right in pairs:
        for name in ('add', 'mul', 'div'):
            if name == 'div' and not right.exact:
                continue
            expected_operations += 1
            if name == 'add':
                exact = left.exact+right.exact
                actual = left.as_float()+right.as_float()
            elif name == 'mul':
                exact = left.exact*right.exact
                actual = left.as_float()*right.as_float()
            else:
                exact = left.exact/right.exact
                actual = left.as_float()/right.as_float()
            if abs(exact) >= threshold:
                rejects(lambda name=name, left=left, right=right: getattr(arith, name)(left, right), ArithmeticUnresolved)
                overflow += 1
                continue
            result = getattr(arith, name)(left, right)
            assert result.bits == from_float(actual).bits
            check_nearest_binary64(result, exact)
            expected_error = max(expected_error, abs(result.exact-exact))
            assert arith.max_round_error == expected_error
            successful += 1
    assert arith.operations == expected_operations
    floor_checks = 0
    for value in values:
        if value.exact < 0:
            continue
        for bits in (0, 1, 8, 16, 52, 53, 1022, 1074, 1200):
            scaled = value.exact*2**bits
            expected = F(scaled.numerator//scaled.denominator, 2**bits)
            result = arith.floor_grid(value, bits)
            assert result.exact == expected and not result.negative
            floor_checks += 1
    one = arith.cast(F(1))
    half_ulp = arith.cast(pow2(-53))
    ordered = arith.add(arith.add(one, half_ulp), half_ulp)
    regrouped = arith.add(one, arith.add(half_ulp, half_ulp))
    assert ordered.exact == 1 and regrouped.exact == 1+pow2(-52)
    return {'raw_finite_encoding_roundtrips': len(values), 'successful_actual_scalar_comparisons': successful,
            'independent_binary64_adjacent_distance_and_tie_checks': successful,
            'actual_overflow_cases_unresolved': overflow, 'exact_floor_grid_checks': floor_checks,
            'operation_counts_and_maximum_local_round_error_match_independent_accounting': True,
            'positive_CPU_ordered_SUM_reassociation_changes_result': True}


def failure_audit():
    for precision in (True, 0, F(3), 3.0):
        rejects(lambda precision=precision: BinaryFormat(precision, -2, 2))
    for emin, emax in ((True, 2), (-2, False), (3, 2), (F(-2), 2), (-2, 2.0)):
        rejects(lambda emin=emin, emax=emax: BinaryFormat(3, emin, emax))
    rejects(lambda: BinaryFormat(3, -2, 2, 'ftz'))
    for value in (1, 1.0, True):
        rejects(lambda value=value: round_binary(value, BINARY64, bit_limit=4096))
    rejects(lambda: round_binary(F(1), BINARY64, bit_limit=4096, negative_zero=True))
    rejects(lambda: round_binary(F(0), BINARY64, bit_limit=4096, negative_zero=1))
    rejects(lambda: RoundedBinary(F(1), True))
    rejects(lambda: RoundedBinary(0, False))
    for bits in (True, -1, 1 << 64, F(0), 0.0):
        rejects(lambda bits=bits: Float64Value(bits))
    for bits in (0x7ff0000000000000, 0xfff0000000000000, 0x7ff0000000000001, 0x7ff8000000000000):
        rejects(lambda bits=bits: Float64Value(bits), ArithmeticUnresolved)
    for value, fmt, bit_limit in ((pow2(-128), BinaryFormat(3, -2, 2), 128),
                                  (F(1), BinaryFormat(1_000_000, -2, 2), 128),
                                  (F(1), BinaryFormat(3, -1_000_000, 2), 128),
                                  (F(1), BINARY64, 128)):
        rejects(lambda value=value, fmt=fmt, bit_limit=bit_limit: round_binary(value, fmt, bit_limit=bit_limit), ArithmeticUnresolved)
    rejects(lambda: Float64Arithmetic(128), ArithmeticUnresolved)
    limited = Float64Arithmetic(4096)
    rejects(lambda: limited.cast(pow2(-4096)), ArithmeticUnresolved)
    assert limited.operations == 1 and limited.max_round_error == 0
    # Even if a helper's active budget changes, its operation must check the
    # encoding requirement before constructing an exact subnormal denominator.
    limited.bit_limit = 128
    with patch.object(Float64Value, 'exact', new_callable=PropertyMock,
                      side_effect=AssertionError('raw value decoded before its integer budget check')):
        rejects(lambda: limited.add(Float64Value(1), Float64Value(1)), ArithmeticUnresolved)
    assert limited.operations == 2
    arith = Float64Arithmetic(4096)
    one = arith.cast(F(1))
    rejects(lambda: arith.floor_grid(one, 4096), ArithmeticUnresolved)
    rejects(lambda: arith.floor_grid(arith.cast(F(-1)), 4), ArithmeticUnresolved)
    rejects(lambda: arith.cast(1))
    rejects(lambda: arith.add(one, 1.0))
    before = arith.operations
    # Fault injection changes the actual scalar operand decode, without
    # changing its retained bits or exact oracle. Both value and zero-sign
    # mismatches must be detected instead of accepting a self-reported result.
    with patch.object(Float64Value, 'as_float', return_value=0.0):
        rejects(lambda: arith.add(one, one), BinaryExecutionMismatch)
    assert arith.operations == before+1
    negative_zero = Float64Value(1 << 63)
    with patch.object(Float64Value, 'as_float', return_value=0.0):
        rejects(lambda: arith.add(negative_zero, negative_zero), BinaryExecutionMismatch)
    assert type(arith.scalar_work) is int and arith.scalar_work > 0
    return {'malformed_formats_numeric_types_and_raw_encodings_rejected': True,
            'input_and_shift_bit_exhaustion_unresolved_before_large_allocation': True,
            'binary64_integer_budget_checked_before_raw_subnormal_decode': True,
            'failed_scalar_attempts_keep_operation_counts': True,
            'actual_value_and_negative_zero_backend_mismatches_detected': True,
            'registered_reference_scalar_work': arith.scalar_work,
            'work_scope': 'registered fixed primitive charge, not elapsed bit-time or CPU heap accounting'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', choices=('all', 'rounding', 'counterexamples', 'limits', 'actual', 'failures'), default='all')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checks = {'rounding': exhaustive_rounding_audit, 'counterexamples': counterexample_audit,
              'limits': signed_zero_and_limits_audit, 'actual': actual_binary64_audit, 'failures': failure_audit}
    result = {'status': 'PASS', 'scope': 'exact registered scalar binary rounding and actual checked CPU binary64 operations'}
    for key, audit in checks.items():
        if args.section in ('all', key):
            result[key] = audit()
    result['not_closed'] = ['IEEE exception flag semantics', 'input DAZ or GPU FTZ behavior', 'FMA or parallel reduction kernels',
                            'continuous whole-learner bridge', 'actual AMP and installation authority']
    if args.write:
        if args.section != 'all':
            parser.error('only the full audit may replace canonical evidence')
        (ROOT/'evidence/minimal/FP_BINARY_ARITHMETIC_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
