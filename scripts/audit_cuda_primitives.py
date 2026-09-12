"""Actual CUDA arithmetic diagnostics before owned AMP learner integration.

The Fraction oracle checks raw device outputs, including signed zero. This
script issues no Runtime bridge, resource, persistence or install authority.
No CUDA absence, nonfinite result or unexpected arithmetic mismatch is silently
accepted as a finite successful execution. The intentionally exercised overflow
boundary is reported separately. All arrays are regenerated and discarded.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))

from fp_reference.binary_arithmetic import BinaryFormat, round_binary
from fp_reference.semantics import ArithmeticUnresolved


@dataclass(frozen=True)
class Layout:
    width: int
    fraction_bits: int
    exponent_bits: int
    bias: int
    torch_name: str
    struct_code: str

    @property
    def sign(self):
        return 1 << (self.width-1)

    @property
    def infinity(self):
        return ((1 << self.exponent_bits)-1) << self.fraction_bits

    @property
    def fmt(self):
        return BinaryFormat(self.fraction_bits+1, 1-self.bias, self.bias)

    def decode(self, word):
        assert type(word) is int and 0 <= word < 1 << self.width
        exponent = (word >> self.fraction_bits) & ((1 << self.exponent_bits)-1)
        assert exponent != (1 << self.exponent_bits)-1
        mantissa = word & ((1 << self.fraction_bits)-1)
        if exponent:
            mantissa += 1 << self.fraction_bits
        shift = (exponent if exponent else 1)-self.bias-self.fraction_bits
        value = F(mantissa << shift) if shift >= 0 else F(mantissa, 1 << -shift)
        return -value if word & self.sign else value

    def encode_exact(self, value, *, negative_zero=False):
        # A finite already-rounded binary16/32 dyadic is exactly binary64.
        # This conversion encodes the oracle result; it does not round the
        # original rational through binary64 before the reference decision.
        number = -0.0 if not value and negative_zero else float(value)
        word = int.from_bytes(struct.pack('>'+self.struct_code, number), 'big')
        assert self.decode(word) == value
        assert bool(word & self.sign) == bool(value < 0 or not value and negative_zero)
        return word

    def rounded(self, value, *, negative_zero=False):
        result = round_binary(value, self.fmt, bit_limit=4096, negative_zero=negative_zero)
        return self.encode_exact(result.value, negative_zero=result.negative_zero)

    def tensor(self, words, torch):
        integers = [word if word < self.sign else word-(1 << self.width) for word in words]
        return torch.tensor(integers, dtype=getattr(torch, 'int'+str(self.width))).view(
            getattr(torch, self.torch_name)).to('cuda')

    def words(self, tensor, torch):
        assert tensor.is_cuda and tensor.dtype == getattr(torch, self.torch_name)
        return [word & ((1 << self.width)-1) for word in
                tensor.view(getattr(torch, 'int'+str(self.width))).cpu().tolist()]


HALF = Layout(16, 10, 5, 15, 'float16', 'e')
SINGLE = Layout(32, 23, 8, 127, 'float32', 'f')
SEED = 2026091369


def encoding_audit(torch):
    finite = [word for word in range(1 << 16) if word & 0x7c00 != 0x7c00]
    values = HALF.tensor(finite, torch)
    assert HALF.words(values, torch) == finite
    assert HALF.words(values.to(torch.float32).to(torch.float16), torch) == finite
    # Every adjacent positive finite half pair has an exactly representable
    # float32 midpoint. Check it and its two float32 neighbours, with both
    # signs. This is exhaustive over these conversion cells, not all f32.
    inputs, expected = [], []
    for lower in range(HALF.infinity-1):
        midpoint = (HALF.decode(lower)+HALF.decode(lower+1))/2
        center = SINGLE.encode_exact(midpoint)
        nearest = lower+(lower & 1)
        for sign in (0, 1):
            inputs.extend((center-1 | sign*SINGLE.sign,
                           center | sign*SINGLE.sign, center+1 | sign*SINGLE.sign))
            expected.extend((lower | sign*HALF.sign,
                             nearest | sign*HALF.sign, lower+1 | sign*HALF.sign))
    finite_boundary_cases = len(inputs)
    midpoint = SINGLE.encode_exact(F(65520))
    for sign in (0, 1):
        inputs.extend(word | sign*SINGLE.sign for word in (midpoint-1, midpoint, midpoint+1))
        expected.extend(word | sign*HALF.sign for word in (0x7bff, 0x7c00, 0x7c00))
    actual = HALF.words(SINGLE.tensor(inputs, torch).to(torch.float16), torch)
    assert actual == expected
    return {'all_finite_half_raw_roundtrips': len(finite),
            'all_finite_half_to_single_to_half_roundtrips': len(finite),
            'signed_finite_half_midpoint_and_adjacent_single_casts': finite_boundary_cases,
            'signed_half_overflow_boundary_casts': 6,
            'actual_nonfinite_overflow_casts_not_certifiable': 4,
            'zero_signs_checked': True}


def cases(layout, rng):
    positive = [0, 1, 2, (1 << layout.fraction_bits)-1, 1 << layout.fraction_bits,
                (1 << layout.fraction_bits)+1,
                *[layout.rounded(value) for value in (F(1, 2), F(1), F(3, 2), F(3), F(7))],
                layout.infinity-1]
    boundary = positive+[word | layout.sign for word in positive]
    pairs = list(product(boundary, repeat=2))
    def raw():
        # Half the random values concentrate on ordinary working scales;
        # the other half cover the whole finite exponent range.
        if rng.randrange(2):
            exponent = layout.bias+rng.randrange(-8, 9)
            return (rng.randrange(2)*layout.sign | exponent << layout.fraction_bits
                    | rng.randrange(1 << layout.fraction_bits))
        return rng.randrange(layout.infinity) | rng.randrange(2)*layout.sign
    pairs.extend((raw(), raw()) for _ in range(1024))
    triples = [(raw(), raw(), raw()) for _ in range(1024)]
    triples.extend((a, b, c) for a, b, c in product((0, layout.sign), repeat=3))
    return pairs, triples


def expected_binary(layout, name, a, b):
    left, right = layout.decode(a), layout.decode(b)
    if name == 'add':
        exact = left+right
        negative = not exact and not left and not right and bool(a & b & layout.sign)
    else:
        if name == 'div' and not right:
            raise ZeroDivisionError
        exact = left*right if name == 'mul' else left/right
        negative = not exact and bool((a ^ b) & layout.sign)
    return layout.rounded(exact, negative_zero=bool(negative))


def arithmetic_audit(torch):
    rng = random.Random(SEED)
    result = {}
    for layout in (HALF, SINGLE):
        pairs, triples = cases(layout, rng)
        left, right = (layout.tensor([row[i] for row in pairs], torch) for i in range(2))
        counts = {}
        for name in ('add', 'mul', 'div'):
            actual = layout.words(getattr(torch, name)(left, right), torch)
            checked = overflow = zero_denominators = 0
            for (a, b), word in zip(pairs, actual):
                try:
                    expected = expected_binary(layout, name, a, b)
                except ZeroDivisionError:
                    assert word & layout.infinity == layout.infinity
                    zero_denominators += 1
                except ArithmeticUnresolved:
                    # With these finite bounded inputs, the only oracle
                    # refusal is arithmetic overflow, checked by raw infinity.
                    assert word & ~layout.sign == layout.infinity
                    overflow += 1
                else:
                    assert word == expected, (layout.torch_name, name, hex(a), hex(b), hex(word), hex(expected))
                    checked += 1
            counts[name] = {'exact_RNE_raw_comparisons': checked,
                            'actual_overflows_unresolved': overflow,
                            'zero_denominator_nonfinite_unresolved': zero_denominators}
        a, b, c = (layout.tensor([row[i] for row in triples], torch) for i in range(3))
        actual = layout.words(torch.addcmul(c, a, b, value=1), torch)
        checked = overflow = direct_half_differences = 0
        for (wa, wb, wc), word in zip(triples, actual):
            va, vb, vc = (layout.decode(w) for w in (wa, wb, wc))
            exact = va*vb+vc
            negative = bool(not exact and not va*vb and not vc
                            and (wa ^ wb) & layout.sign and wc & layout.sign)
            try:
                wide = SINGLE.rounded(exact, negative_zero=negative)
                expected = layout.rounded(SINGLE.decode(wide),
                                          negative_zero=bool(wide & SINGLE.sign and not SINGLE.decode(wide)))
            except ArithmeticUnresolved:
                assert word & ~layout.sign == layout.infinity
                overflow += 1
            else:
                assert word == expected, ('addcmul', layout.torch_name, hex(word), hex(expected))
                checked += 1
                if layout is HALF:
                    direct_half_differences += word != HALF.rounded(exact, negative_zero=negative)
        counts['addcmul_value_1'] = {'single_FMA_then_storage_RNE_raw_comparisons': checked,
                                    'actual_overflows_unresolved': overflow,
                                    'differs_from_direct_half_FMA_in_sample': direct_half_differences}
        result[layout.torch_name] = counts
    return result


def counterexample_audit(torch):
    def half(value):
        return HALF.tensor([HALF.rounded(value)], torch)
    def single(value):
        return SINGLE.tensor([SINGLE.rounded(value)], torch)
    a = b = half(F(1025, 1024))
    c = half(F(1, 2048))
    separate = HALF.words((a*b)+c, torch)[0]
    combined = HALF.words(torch.addcmul(c, a, b, value=1), torch)[0]
    assert HALF.decode(separate) == F(1026, 1024)
    assert HALF.decode(combined) == F(1027, 1024)

    # ab lies at a half midpoint; c reaches only a float32 half-ULP.
    # RNE32 removes c before the final half tie is resolved downward.
    va, vb, vc = F(1027, 1024), F(3, 2), F(1, 1 << 24)
    actual = HALF.words(torch.addcmul(half(vc), half(va), half(vb), value=1), torch)[0]
    ideal = HALF.rounded(va*vb+vc)
    wide = SINGLE.rounded(va*vb+vc)
    assert actual == HALF.rounded(SINGLE.decode(wide)) == 0x3e04
    assert ideal == 0x3e05

    # Same positive numerator/denominator, different operand residence.
    numerator, denominator = single(F(7)), single(F(12))
    device_division = SINGLE.words(numerator/denominator, torch)[0]
    scalar_division = SINGLE.words(numerator/12.0, torch)[0]
    assert device_division == SINGLE.rounded(F(7, 12))
    reciprocal = SINGLE.decode(SINGLE.rounded(F(1, 12)))
    assert scalar_division == SINGLE.rounded(F(7)*reciprocal) != device_division

    mass = SINGLE.tensor([SINGLE.rounded(F(1)), SINGLE.rounded(F(1, 1 << 24))], torch)
    total = single(F(0))
    for index in range(2):
        total = total+mass[index:index+1]
    total_word = SINGLE.words(total, torch)[0]
    outputs = SINGLE.words(mass/total, torch)
    stored_total = F(1)+F(1, 1 << 24)
    assert SINGLE.decode(total_word) == 1 and sum(map(SINGLE.decode, outputs)) == stored_total > 1
    assert F(1)/stored_total != SINGLE.decode(outputs[0])
    return {
        'positive_separate_half_multiply_add': {'inputs': ['1025/1024', '1025/1024', '1/2048'],
             'separate_output_bits': hex(separate), 'addcmul_output_bits': hex(combined)},
        'positive_half_addcmul_double_rounding': {'inputs': list(map(str, (va, vb, vc))),
             'actual_bits': hex(actual), 'ideal_single_round_half_FMA_bits': hex(ideal),
             'actual_equals_single_FMA_then_half': True},
        'positive_division_operand_residence': {'numerator': 7, 'denominator': 12,
             'device_tensor_divisor_bits': hex(device_division), 'CPU_scalar_divisor_bits': hex(scalar_division),
             'scalar_matches_rounded_reciprocal_then_multiply': True},
        'stored_mass_normalization': {'masses': ['1', '1/16777216'],
             'exact_stored_mass_total': str(stored_total), 'rounded_device_normalizer': '1',
             'raw_division_outputs_sum_exactly': str(sum(map(SINGLE.decode, outputs))),
             'stored_mass_distribution_differs_from_raw_division_outputs': True}}


def dispatch_audit(torch):
    a = torch.ones((4, 4), device='cuda', dtype=torch.float32)
    with torch.autocast('cuda', dtype=torch.float16):
        outputs = {'elementwise_SUM': a+a, 'elementwise_PRODUCT': a*a,
                   'reduction_SUM': a.sum(), 'matrix_multiply': a@a}
    observed = {key: str(value.dtype) for key, value in outputs.items()}
    assert observed == {'elementwise_SUM': 'torch.float32', 'elementwise_PRODUCT': 'torch.float32',
                        'reduction_SUM': 'torch.float32', 'matrix_multiply': 'torch.float16'}
    subnormal = {}
    for layout in (HALF, SINGLE):
        minimum = layout.tensor([1], torch)
        one = layout.tensor([layout.rounded(F(1))], torch)
        assert layout.words(minimum*one, torch) == [1]
        assert layout.words(minimum+minimum, torch) == [2]
        subnormal[layout.torch_name] = {'min_subnormal_times_device_one_bits': 1,
                                       'min_subnormal_plus_itself_bits': 2}
    return {'autocast_float32_input_observed_outputs': observed,
            'actual_explicit_half_arithmetic_executed_elsewhere_in_audit': True,
            'tested_min_subnormal_operations': subnormal}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('actual CUDA execution required; CPU or simulated arithmetic cannot pass this audit')
    torch.cuda.set_device(0)
    torch.cuda.synchronize()
    props = torch.cuda.get_device_properties(0)
    driver = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                            capture_output=True, text=True, check=True).stdout.strip().splitlines()
    result = {'status': 'PASS', 'scope': 'actual eager CUDA primitive encodings and lowering counterexamples; no Runtime authority',
              'seed': SEED, 'executed_utc': datetime.now(timezone.utc).isoformat(),
              'device': {'name': props.name, 'capability': list(torch.cuda.get_device_capability(0)),
                         'total_memory_bytes': props.total_memory, 'driver_versions': driver,
                         'torch': torch.__version__, 'torch_git_version': torch.version.git_version,
                         'torch_CUDA_runtime': torch.version.cuda, 'Python': sys.version}}
    for name, audit in (('encodings', encoding_audit), ('arithmetic', arithmetic_audit),
                        ('counterexamples', counterexample_audit), ('dispatch', dispatch_audit)):
        result[name] = audit(torch)
        print(name+' PASS', flush=True)
    torch.cuda.synchronize()
    result['not_closed'] = ['untested kernels, tensor shapes, compiler fusion or parallel reduction orders',
        'all-format/all-input arithmetic correctness', 'GPU input FTZ/DAZ or IEEE flags in general',
        'complete continuous AMP learners, same-path persistence and Runtime install',
        'ERC-1 physical device ownership or model-science release']
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_PRIMITIVE_AUDIT.json').write_text(
            json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
