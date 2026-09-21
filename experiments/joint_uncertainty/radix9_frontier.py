"""Passive scaled positive inference: host integer exponents, finite mantissas.

The CUDA diagnostic uses actual half products and single additions/divisions.
Every floating word is checked independently. This is not a Runtime bridge.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).resolve().parent)]
import positive_frontier_decoder as exact
from audit_cuda_primitives import HALF, SINGLE
from fp_reference.binary_arithmetic import BinaryFormat, Float64Arithmetic, round_binary
from fp_reference.semantics import ArithmeticUnresolved

BITS = 32768
CUTOFF = 16
EXPONENT_CAP = (1 << 62)-1


from fp_reference.positive_tape import Tape, compile_tape


@dataclass(frozen=True)
class Batch:
    values: tuple[F, ...]
    tensor: object = None


class Arithmetic:
    def __init__(self, size, mode, torch=None):
        assert mode in ('binary64', 'amp') and (torch is None or mode == 'amp')
        self.size, self.mode, self.torch = size, mode, torch
        self.float64 = Float64Arithmetic(BITS) if mode == 'binary64' else None
        self.scalar_results = self.device_words = self.predicates = 0

    def operation(self, tag, a=None, b=None, *, half=False, constant=None):
        values = []
        for i in range(self.size):
            if tag == 'constant':
                value = F(constant)
            elif tag == 'cast':
                value = a.values[i]
            elif tag == 'mul':
                value = a.values[i]*b.values[i]
            elif tag == 'add':
                value = a.values[i]+b.values[i]
            else:
                assert tag == 'div'
                value = a.values[i]/b.values[i]
            if self.mode == 'binary64':
                assert not half
                if tag in ('constant', 'cast'):
                    result = self.float64.cast(value)
                else:
                    x, y = self.float64.cast(a.values[i]), self.float64.cast(b.values[i])
                    result = getattr(self.float64, tag)(x, y)
                assert result.exact == round_binary(value, BinaryFormat(53, -1022, 1023), bit_limit=BITS).value
                values.append(result.exact)
            else:
                layout = HALF if half else SINGLE
                values.append(layout.decode(layout.rounded(value)))
        self.scalar_results += self.size
        tensor = None
        if self.torch is not None:
            torch, layout = self.torch, HALF if half else SINGLE
            if tag == 'constant':
                tensor = torch.full((self.size,), float(constant), dtype=getattr(torch, layout.torch_name), device='cuda')
            elif tag == 'cast':
                tensor = a.tensor.to(getattr(torch, layout.torch_name))
            else:
                tensor = {'mul': torch.mul, 'add': torch.add, 'div': torch.div}[tag](a.tensor, b.tensor)
            expected = [layout.encode_exact(v) for v in values]
            actual = layout.words(tensor, torch)
            assert actual == expected, (tag, self.scalar_results, expected, actual)
            self.device_words += self.size
        return Batch(tuple(values), tensor)

    def choose(self, mask, a, b, *, actual_mask=None):
        values = tuple(x if flag else y for flag, x, y in zip(mask, a.values, b.values))
        tensor = None
        if self.torch is not None:
            torch = self.torch
            actual_mask = torch.tensor(mask, dtype=torch.bool, device='cuda') if actual_mask is None else actual_mask
            actual = tuple(actual_mask.cpu().tolist())
            assert actual == tuple(mask)
            tensor = torch.where(actual_mask, a.tensor, b.tensor)
            assert SINGLE.words(tensor, torch) == [SINGLE.encode_exact(v) for v in values]
            self.device_words += self.size
        self.predicates += self.size
        return Batch(values, tensor)

    def gather(self, powers, indices):
        assert all(0 <= i < CUTOFF for i in indices)
        values = tuple(powers[j].values[i] for i, j in enumerate(indices))
        tensor = None
        if self.torch is not None:
            torch = self.torch
            table = torch.stack([p.tensor for p in powers])
            index = torch.tensor(indices, dtype=torch.int64, device='cuda').unsqueeze(0)
            tensor = table.gather(0, index).squeeze(0)
            assert SINGLE.words(tensor, torch) == [SINGLE.encode_exact(v) for v in values]
            self.device_words += self.size
        return Batch(values, tensor)


@dataclass(frozen=True)
class Wide:
    mantissa: Batch
    exponent: tuple[int, ...]


class Decoder:
    def __init__(self, size, mode, torch=None):
        self.arith = Arithmetic(size, mode, torch)
        self.zero = self.arith.operation('constant', constant=0)
        self.one = self.arith.operation('constant', constant=1)
        self.nine = self.arith.operation('constant', constant=9)
        self.powers = [self.one]
        for _ in range(1, CUTOFF):
            self.powers.append(self.arith.operation('div', self.powers[-1], self.nine))
        self.max_exponent = self.truncated_alignments = 0

    def normalize(self, mantissa, exponent):
        exponent = tuple(exponent)
        for _ in range(2):
            mask = tuple(v >= 9 for v in mantissa.values)
            actual_mask = None if self.arith.torch is None else mantissa.tensor >= 9
            physical_mask = mask if actual_mask is None else tuple(actual_mask.cpu().tolist())
            assert physical_mask == mask
            divided = self.arith.operation('div', mantissa, self.nine)
            mantissa = self.arith.choose(mask, divided, mantissa, actual_mask=actual_mask)
            # The predicate is checked against the actual device before host
            # integer metadata uses it. Exponents never come from a posterior cast.
            exponent = tuple(e+int(flag) for e, flag in zip(exponent, physical_mask))
        exponent = tuple(0 if v == 0 else e for v, e in zip(mantissa.values, exponent))
        assert all(v == 0 or 1 <= v < 9 for v in mantissa.values)
        assert all(0 <= e <= EXPONENT_CAP for e in exponent)
        self.max_exponent = max(self.max_exponent, *exponent)
        return Wide(mantissa, exponent)

    def mul(self, left, right):
        exponent = tuple(a+b for a, b in zip(left.exponent, right.exponent))
        if max(exponent)+2 > EXPONENT_CAP:
            raise ArithmeticUnresolved('wide product exceeds its declared exponent field')
        arith = self.arith
        if arith.mode == 'amp':
            a = arith.operation('cast', left.mantissa, half=True)
            b = arith.operation('cast', right.mantissa, half=True)
            value = arith.operation('mul', a, b, half=True)
            value = arith.operation('cast', value)
        else:
            value = arith.operation('mul', left.mantissa, right.mantissa)
        return self.normalize(value, exponent)

    def add(self, left, right):
        arith = self.arith
        choose_left = tuple(a >= b for a, b in zip(left.exponent, right.exponent))
        high = arith.choose(choose_left, left.mantissa, right.mantissa)
        low = arith.choose(choose_left, right.mantissa, left.mantissa)
        difference = tuple(abs(a-b) for a, b in zip(left.exponent, right.exponent))
        exponent = tuple(max(a, b) for a, b in zip(left.exponent, right.exponent))
        if max(exponent)+2 > EXPONENT_CAP:
            raise ArithmeticUnresolved('wide sum exceeds its declared exponent field')
        coefficient = arith.gather(self.powers, tuple(min(d, CUTOFF-1) for d in difference))
        dropped = tuple(d >= CUTOFF for d in difference)
        self.truncated_alignments += sum(dropped)
        coefficient = arith.choose(dropped, self.zero, coefficient)
        aligned = arith.operation('mul', low, coefficient)
        return self.normalize(arith.operation('add', high, aligned), exponent)

    def run(self, tape, heads, rows):
        if any(sum(map(abs, row))+len(tape.nodes)+4 > EXPONENT_CAP for row in rows):
            raise ArithmeticUnresolved('input exponent envelope exceeds its declared field')
        zero_exponents = (0,)*len(rows)
        states = []
        for tag, *args in tape.nodes:
            if tag in ('zero', 'one', 'nine'):
                state = Wide(self.zero if tag == 'zero' else self.one,
                             (1,)*len(rows) if tag == 'nine' else zero_exponents)
            elif tag == 'factor':
                edge, parity = args
                exponent = tuple(max(d[edge], 0) if parity == 0 else max(-d[edge], 0) for d in rows)
                state = Wide(self.one, exponent)
            else:
                state = getattr(self, tag)(states[args[0]], states[args[1]])
            states.append(state)
        a, b = (states[h] for h in heads)
        total = self.add(a, b)
        difference = tuple(t-e for t, e in zip(total.exponent, a.exponent))
        assert all(0 <= d <= 2 for d in difference)
        value = self.arith.operation('div', a.mantissa, total.mantissa)
        probability = self.arith.operation('mul', value, self.arith.gather(self.powers, difference))
        assert all(F(0) < p < F(1) for p in probability.values)
        return probability, states


def cases():
    rows = []
    hs = (0, 1, 7, 8, 16, 47, 48, 64, 339, 340, 384)
    rows.append(('frustrated_triangle', 3, ((0, 1), (0, 2), (1, 2)), (0, 1),
                 tuple((h, h, -h) for h in hs)))
    for query in ((1, 2), (1, 1)):
        rows.append((f'triangle_query_{query[0]}_{query[1]}', 3, ((0, 1), (0, 2), (1, 2)), query,
                     tuple((h, h, -h) for h in (0, 1, 48, 384))))
    for n in (8, 64):
        support = tuple(sorted({tuple(sorted((i, (i+1) % n))) for i in range(n)}))
        patterns = tuple(tuple(-h if e == (0, n-1) else h for e in support) for h in (0, 1, 8, 64))
        rows.append((f'frustrated_cycle_{n}', n, support, (0, n//4), patterns))
    return tuple(rows)


def probability_oracle(n, support, query, signed):
    complete = tuple(dict(zip(support, signed)).get(e, 0) for e in exact.edges(n))
    parts, _ = exact.decode(n, complete, query)
    return exact.forecast(parts)


def naive_audit():
    rows = []
    for name, fmt in (('binary16', BinaryFormat(11, -14, 15)), ('binary32', BinaryFormat(24, -126, 127)),
                      ('binary64', BinaryFormat(53, -1022, 1023))):
        first = next(h for h in range(1, 400) if round_binary(F(1, 9**h), fmt, bit_limit=BITS).value == 0)
        # Best possible scalar rounding of the locally normalized entry already
        # fails; power-algorithm error is not needed for this counterexample.
        q = probability_oracle(3, ((0, 1), (0, 2), (1, 2)), (0, 1), (first, first, -first))
        rounded_partition = sum((int(z1 == 0)*int(z2 == 0)*int(z1 != z2) for z1 in (0, 1) for z2 in (0, 1)))
        assert rounded_partition == 0 and abs(q-F(19, 30)) < F(1, 10**10)
        rows.append({'format': name, 'first_zero_count': first, 'rounded_partition': rounded_partition,
                     'true_probability0_float': float(q), 'exact_probability_distance_from_19_over_30_below': '1/10000000000'})
    return rows


def audit(mode, torch=None):
    result = []
    for name, n, support, query, inputs in cases():
        tape, heads = compile_tape(n, support, query)
        decoder = Decoder(len(inputs), mode, torch)
        probability, states = decoder.run(tape, heads, inputs)
        truth = tuple(probability_oracle(n, support, query, row) for row in inputs)
        errors = tuple(abs(a-b) for a, b in zip(probability.values, truth))
        assert all(s.mantissa.values[i] > 0 for s, node in zip(states, tape.nodes) if node[0] == 'factor'
                   for i in range(len(inputs)))
        epsilon = F(1, 512) if mode == 'amp' else F(1, 1 << 46)
        budget = max(tape.budgets[h] for h in heads)+1
        ratio = ((1+epsilon)/(1-epsilon))**budget
        assert all(p/ratio <= a <= p*ratio for a, p in zip(probability.values, truth))
        result.append({'case': name, 'n': n, 'query': query,
                       'support': 'triangle' if n == 3 else 'cycle',
                       'count_magnitudes': [abs(row[0]) for row in inputs],
                       'negative_edges': [edge for edge, d in zip(support, inputs[-1]) if d < 0],
                       'positive_tape_nodes': len(tape.nodes), 'mass_roundoff_budget': budget-1,
                       'scalar_rounding_results': decoder.arith.scalar_results,
                       'actual_binary64_primitive_checks': 0 if decoder.arith.float64 is None else decoder.arith.float64.operations,
                       'checked_device_words': decoder.arith.device_words,
                       'checked_selection_entries': decoder.arith.predicates,
                       'largest_retained_exponent': decoder.max_exponent,
                       'alignment_truncations': decoder.truncated_alignments,
                       'probabilities': list(map(str, probability.values)),
                       'maximum_absolute_error_float': float(max(errors)),
                       'all_forecasts_within_1e_3': max(errors) <= F(1, 1000),
                       'history_uniform_local_epsilon': str(epsilon),
                       'maximum_relative_normalization_factor_float': float(ratio)})
    return result


def exhaustive_triangle(torch=None):
    support = ((0, 1), (0, 2), (1, 2))
    rows = tuple(product(range(-2, 3), repeat=3))
    maximum, witness = F(-1), None
    words = scalar = 0
    for query in product(range(3), repeat=2):
        tape, heads = compile_tape(3, support, query)
        decoder = Decoder(len(rows), 'amp', torch)
        probabilities, _ = decoder.run(tape, heads, rows)
        for signed, actual in zip(rows, probabilities.values):
            expected = probability_oracle(3, support, query, signed)
            error = abs(actual-expected)
            if error > maximum:
                maximum = error
                witness = {'counts': signed, 'query': query, 'computed_probability': str(actual),
                           'exact_probability': str(expected)}
        words += decoder.arith.device_words
        scalar += decoder.arith.scalar_results
    assert maximum < F(1, 1000)
    return {'signed_count_profiles': len(rows), 'ordered_queries': 9,
            'forecasts': 9*len(rows), 'maximum_absolute_error': str(maximum),
            'maximum_absolute_error_float': float(maximum), 'witness': witness,
            'scalar_rounding_results': scalar, 'checked_device_words': words}


def bound_audit():
    half, single, double = F(1, 1 << 11), F(1, 1 << 24), F(1, 1 << 53)
    tail = F(1, 9**15)
    rows = []
    for mode, unit, epsilon in (('amp', single, F(1, 512)), ('binary64', double, F(1, 1 << 46))):
        mul_upper = (1+half)**3*(1+single)**2 if mode == 'amp' else (1+double)**3
        mul_lower = (1-half)**3*(1-single)**2 if mode == 'amp' else (1-double)**3
        assert mul_upper < 1+epsilon and mul_lower > 1-epsilon
        assert (1+unit)**19 < 1+epsilon and (1-unit)**19 > 1-epsilon
        assert tail < epsilon and (1+unit)**4 < 1+epsilon and (1-unit)**4 > 1-epsilon
        ratio = (1+epsilon)/(1-epsilon)
        assert (1+epsilon)*(1+9*ratio**2) < 11
        assert (1-epsilon)*(1+1/(9*ratio**2)) > 1
        rows.append({'mode': mode, 'local_epsilon': str(epsilon),
                     'normalization_exponent_difference_at_most': 2})
    return {'status': 'PASS_EXACT_RATIONAL_INEQUALITIES', 'alignment_cutoff': CUTOFF,
            'relative_discarded_alignment_below': str(tail), 'modes': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cuda-worker', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.cuda_worker:
            import torch
            assert torch.cuda.is_available()
            torch.cuda.set_device(0)
            torch.cuda.reset_peak_memory_stats()
            report = {'status': 'PASS_ACTUAL_AMP_ARITHMETIC_ONLY', 'process_id': os.getpid(),
                      'torch': torch.__version__, 'CUDA': torch.version.cuda,
                      'device': torch.cuda.get_device_name(0),
                      'scope': 'host integer exponents and actual half products/single sums; no Runtime bridge or model outcome',
                      'cases': audit('amp', torch), 'exhaustive_triangle': exhaustive_triangle(torch)}
            torch.cuda.synchronize()
            report.update(peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),
                          peak_torch_reserved_bytes=torch.cuda.max_memory_reserved())
        else:
            report = {'status': 'PASS_PASSIVE_SCALED_DECODER',
                      'scope': 'count-decoder arithmetic only; no original native finite trace or Runtime authority',
                      'locally_scaled_failure': naive_audit(),
                      'binary64': audit('binary64'), 'AMP_exact_machine': audit('amp'),
                      'exhaustive_triangle': exhaustive_triangle(), 'local_bounds': bound_audit()}
    except Exception:
        if args.output:
            args.output.write_text(json.dumps({'status': 'FAILED', 'process_id': os.getpid(),
                                              'traceback': traceback.format_exc()}, indent=2)+'\n', encoding='utf-8')
        raise
    text = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
