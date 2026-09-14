"""History-uniform bound for the existing radix9 RNE32 commit decoder.

This is an exact arithmetic-machine audit, not a new CUDA execution, full
native-gradient bound, Runtime certificate or unlimited-resource guarantee.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from audit_cuda_primitives import SINGLE

U = F(1, 1 << 24)
HALF_SUBNORMAL = F(1, 1 << 150)
ROUNDINGS = 0


def rounded(value):
    global ROUNDINGS
    word = SINGLE.rounded(value)
    # An independent binary64-to-binary32 calculation agrees on every
    # arithmetic input in this finite audit. No general double-rounding
    # equivalence is assumed by the proof or exact oracle.
    reference = struct.unpack('<I', struct.pack('<f', float(value)))[0]
    assert reference == word
    ROUNDINGS += 1
    return SINGLE.decode(word)


def power_table():
    powers = [rounded(F(1, 9))]
    for _ in range(1, 64):
        powers.append(rounded(powers[-1]**2))
    assert powers[6:] == [F(0)]*58
    return tuple(powers)


def weight(exponent, powers):
    assert type(exponent) is int and 0 <= exponent < 1 << 64
    value = F(1)
    for bit in range(exponent.bit_length()):
        if exponent & (1 << bit):
            value = rounded(value*powers[bit])
    return value


def theta_bound(k, error):
    assert 1 <= k <= 1 << 24
    gamma = (k-1)*U/(1-(k-1)*U)
    return (k-1)*error+gamma+U+HALF_SUBNORMAL


def normalize_audit(exponents, values, exact, bound):
    k = len(exponents)
    assert min(exponents) == 0
    a = tuple(exact[d] for d in exponents)
    b = tuple(values[d] for d in exponents)
    A, B = sum(a), sum(b)
    S = F(0)
    for value in b:
        S = rounded(S+value)
    assert 1 <= S <= k
    gamma = (k-1)*U/(1-(k-1)*U)
    assert abs(S-B) <= gamma*S
    error = F(0)
    for x, y in zip(a, b):
        normalized = rounded(y/S)
        assert abs(normalized-y/S) <= U+HALF_SUBNORMAL
        current = abs(normalized-x/A)
        assert current <= bound
        error = max(error, current)
    return error


def audit():
    powers = power_table()
    values = tuple(weight(d, powers) for d in range(65))
    exact = tuple(F(1, 9**d) for d in range(65))
    errors = tuple(abs(a-b) for a, b in zip(exact[:64], values[:64]))
    error = max(*errors, exact[64])
    assert error == U/72 == F(1, 1207959552)
    assert [d for d, x in enumerate(errors) if x == error] == [1]
    assert values[47] == F(1, 1 << 149) and values[48:] == (F(0),)*17
    tails = 0
    for bit in range(6, 64):
        for low in range(64):
            assert weight((1 << bit)+low, powers) == 0
            tails += 1
    assert weight((1 << 64)-2, powers) == 0
    tails += 1
    ordered, maximum = 0, F(0)
    for exponents in product(range(65), repeat=3):
        if min(exponents) != 0:
            continue
        maximum = max(maximum, normalize_audit(exponents, values, exact, theta_bound(3, error)))
        ordered += 1
    assert ordered == 65**3-64**3
    widths = {}
    for k in (2, 8, 128):
        bound = theta_bound(k, error)
        maximum_k, checks, witness = F(0), 0, None
        for d in range(65):
            for position in sorted({0, k//2, k-1}):
                exponents = [d]*k
                exponents[position] = 0
                observed = normalize_audit(exponents, values, exact, bound)
                if observed > maximum_k:
                    maximum_k = observed
                    witness = {'repeated_exponent': d, 'unit_weight_position': position}
                checks += 1
        widths[str(k)] = {'declared_uniform_bound': str(bound),
                         'bound_binary64': float(bound), 'normalization_vectors': checks,
                         'observed_maximum_error': str(maximum_k),
                         'observed_maximum_binary64': float(maximum_k), 'observed_witness': witness}
    assert theta_bound(128, error) < F(1, 100000)
    assert 'torch' not in sys.modules
    return {'status': 'EXACT_RNE32_AUDIT_PASS',
            'scope': 'radix9 selected-weight commit decoder; no new GPU or full Runtime certificate',
            'inverse_radix_word': SINGLE.encode_exact(powers[0]),
            'first_power_words': [SINGLE.encode_exact(x) for x in powers[:7]],
            'first_zero_power_index': 6,
            'low_exponent_words': [SINGLE.encode_exact(x) for x in values[:64]],
            'low_exponents_audited': 64, 'first_zero_decoded_weight_exponent': 48,
            'high_bit_tail_patterns': tails,
            'uniform_unnormalized_absolute_error': str(error),
            'error_attaining_low_exponents': [1],
            'tail_exact_upper': str(exact[64]),
            'all_ordered_three_weight_vectors_with_zero': ordered,
            'three_weight_observed_maximum': str(maximum),
            'width_audits': widths, 'binary64_cross_checked_RNE32_operations': ROUNDINGS,
            'persistent_counts_erased': False,
            'unlimited_resources_or_full_native_gradient_bound_claimed': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_LIKELIHOOD_DECODE_ERROR.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
