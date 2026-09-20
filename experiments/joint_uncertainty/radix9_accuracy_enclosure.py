"""Count-decoder tolerance evidence from a checked binary64 enclosure.

This passive numerical decision grants no native-state or Runtime authority.
The CUDA mode executes only the new fixed stress states, not old model jobs.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import radix9_frontier as r
from fp_reference.semantics import ArithmeticUnresolved

EPSILON = F(1, 1 << 46)
TOLERANCE = F(1, 1000)


def enclosure(probability64, mass_budget):
    """Conditional on the proved tape bound and this actual binary64 result."""
    assert type(probability64) is F and 0 < probability64 < 1
    assert type(mass_budget) is int and 0 <= mass_budget <= r.EXPONENT_CAP
    q = mass_budget+1
    t = q*2*EPSILON/(1-EPSILON)
    if t >= 1:
        raise ArithmeticUnresolved('binary64 geometric enclosure is not informative at this tape budget')
    lower = max(F(1, 10), probability64*(1-t))
    upper = min(F(9, 10), probability64/(1-t))
    if lower > upper:
        raise ArithmeticUnresolved('binary64 output contradicts its known-noise enclosure')
    return lower, upper


def classify(observed, bounds, tolerance=TOLERANCE):
    assert type(observed) is F and 0 < observed < 1
    assert type(tolerance) is F and tolerance >= 0
    lo, hi = bounds
    assert F(0) < lo <= hi < F(1)
    minimum = max(lo-observed, observed-hi, F(0))
    maximum = max(abs(observed-lo), abs(observed-hi))
    status = ('WITHIN_TOLERANCE' if maximum <= tolerance else
              'OUTSIDE_TOLERANCE' if minimum > tolerance else 'UNRESOLVED')
    return {'status': status, 'minimum_absolute_error': str(minimum),
            'maximum_absolute_error': str(maximum),
            'minimum_absolute_error_float': float(minimum),
            'maximum_absolute_error_float': float(maximum)}


def stress_cases():
    return (('triangle_huge_counts', 3, (0, 1), (10**12,)),
            ('cycle64_huge_counts', 64, (0, 16), (10**12,)),
            ('cycle256_accuracy_failure', 256, (0, 96), (16, 10**12)))


def cycle_input(n, h):
    support = tuple(sorted({tuple(sorted((i, (i+1) % n))) for i in range(n)}))
    negative = (1, 2) if n == 3 else (0, n-1)
    return support, tuple(-h if edge == negative else h for edge in support)


def limiting_interval(n, query, h):
    """Independent frustrated-cycle counting bound, using no large power."""
    assert query[0] == 0 and 0 < query[1] < n and h >= 1
    # h0 <= h: n/9^h <= n/9^h0. Only the fixed small integer9^16 is needed.
    h0 = min(h, 16)
    y = F(n, 9**h0)
    if y >= 1:
        raise ArithmeticUnresolved('cycle tail bound requires n/9^h0 < 1')
    deviation = F(4, 5)*y*y/(1-y)
    limit = F(9, 10)-F(4*query[1], 5*n)
    return limit-deviation, limit+deviation


def geometric_audit():
    delta = 2*EPSILON/(1-EPSILON)
    checked = 0
    for budget in (0, 1, 7, 8, 9, 23, 191, 383, 767, 1535):
        t = (budget+1)*delta
        assert (1+delta)**(budget+1) <= 1/(1-t)
        checked += 1
    ambiguous = classify(F(1, 2), (F(499, 1000), F(502, 1000)))
    assert ambiguous['status'] == 'UNRESOLVED'
    assert classify(F(1, 2), (F(499, 1000), F(501, 1000)))['status'] == 'WITHIN_TOLERANCE'
    assert classify(F(1, 2), (F(503, 1000), F(504, 1000)))['status'] == 'OUTSIDE_TOLERANCE'
    try:
        enclosure(F(1, 2), (1 << 45)-1)
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('uninformative geometric denominator was accepted')
    return {'exact_geometric_checks': checked, 'decision_boundaries': 3,
            'uninformative_budget_refusals': 1}


def retained_device_audit():
    """A new numerical reader of terminal evidence; no old CUDA execution."""
    cpu = json.loads((ROOT/'evidence/minimal/FP_RADIX9_FRONTIER_EXACT.json').read_text())
    gpu = json.loads((ROOT/'evidence/minimal/FP_RADIX9_FRONTIER_CUDA.json').read_text())
    assert gpu['status'] == 'COMPLETE_EXECUTION'
    actual = gpu['workers'][0]['result']['cases']
    forecasts, width, error = 0, F(0), F(0)
    for reference, physical, machine in zip(cpu['binary64'], actual, cpu['AMP_exact_machine'], strict=True):
        assert reference['case'] == physical['case'] == machine['case']
        assert reference['mass_roundoff_budget'] == physical['mass_roundoff_budget']
        assert physical['probabilities'] == machine['probabilities']
        assert physical['checked_device_words'] > 0
        for p64, observed in zip(reference['probabilities'], physical['probabilities'], strict=True):
            bounds = enclosure(F(p64), reference['mass_roundoff_budget'])
            decision = classify(F(observed), bounds)
            assert decision['status'] == 'WITHIN_TOLERANCE'
            forecasts += 1
            width = max(width, bounds[1]-bounds[0])
            error = max(error, F(decision['maximum_absolute_error']))
    return {'source': gpu['registration']['source'], 'forecast_checks': forecasts,
            'new_device_executions': 0, 'maximum_reference_interval_width_float': float(width),
            'maximum_certified_absolute_error': str(error),
            'maximum_certified_absolute_error_float': float(error)}


def small_audit():
    support = ((0, 1), (0, 2), (1, 2))
    rows = tuple(product(range(-2, 3), repeat=3))
    forecasts = actual64 = 0
    width, error = F(0), F(0)
    for query in product(range(3), repeat=2):
        tape, heads = r.compile_tape(3, support, query)
        budget = max(tape.budgets[h] for h in heads)
        reference = r.Decoder(len(rows), 'binary64')
        p64, _ = reference.run(tape, heads, rows)
        amp = r.Decoder(len(rows), 'amp')
        physical, _ = amp.run(tape, heads, rows)
        actual64 += reference.arith.float64.operations
        for signed, value64, observed in zip(rows, p64.values, physical.values):
            bounds = enclosure(value64, budget)
            truth = r.probability_oracle(3, support, query, signed)
            assert bounds[0] <= truth <= bounds[1]
            decision = classify(observed, bounds)
            assert decision['status'] == 'WITHIN_TOLERANCE' and abs(observed-truth) <= TOLERANCE
            forecasts += 1
            width = max(width, bounds[1]-bounds[0])
            error = max(error, F(decision['maximum_absolute_error']))
    return {'profiles': len(rows), 'ordered_queries': 9, 'forecasts': forecasts,
            'actual_binary64_primitives': actual64,
            'maximum_reference_interval_width_float': float(width),
            'maximum_certified_absolute_error_float': float(error)}


def search_audit():
    # Original deterministic exploratory search, preceding the GPU protocol.
    inputs = tuple((n, n//4, 16) for n in (16, 32, 64, 128, 256))
    inputs += ((256, 16, 16), (256, 32, 16), (256, 96, 16), (256, 128, 16), (512, 128, 8))
    result = []
    for n, q, h in inputs:
        support, signed = cycle_input(n, h)
        tape, heads = r.compile_tape(n, support, (0, q))
        decoder = r.Decoder(1, 'amp')
        value, _ = decoder.run(tape, heads, (signed,))
        truth = r.probability_oracle(n, support, (0, q), signed)
        result.append({'n': n, 'query': [0, q], 'h': h,
                       'AMP_probability': str(value.values[0]),
                       'exact_absolute_error_float': float(abs(value.values[0]-truth)),
                       'within_1e_3': abs(value.values[0]-truth) <= TOLERANCE})
    assert sum(not row['within_1e_3'] for row in result) == 2
    return result


def stress_audit(torch=None):
    result = []
    for name, n, query, magnitudes in stress_cases():
        support, _ = cycle_input(n, magnitudes[0])
        rows = tuple(cycle_input(n, h)[1] for h in magnitudes)
        tape, heads = r.compile_tape(n, support, query)
        budget = max(tape.budgets[h] for h in heads)
        reference = r.Decoder(len(rows), 'binary64')
        values64, _ = reference.run(tape, heads, rows)
        device = r.Decoder(len(rows), 'amp', torch)
        values, _ = device.run(tape, heads, rows)
        forecasts = []
        for h, signed, value64, observed in zip(magnitudes, rows, values64.values, values.values):
            bounds = enclosure(value64, budget)
            analytic = limiting_interval(n, query, h)
            # The independent combinatorial tube is far narrower here.
            assert bounds[0] <= analytic[0] <= analytic[1] <= bounds[1]
            try:
                truth = r.probability_oracle(n, support, query, signed)
            except ArithmeticUnresolved as exc:
                assert h == 10**12 and 'integer' in str(exc)
                oracle = 'UNRESOLVED_INTEGER_HEIGHT'
            else:
                assert h == 16 and bounds[0] <= truth <= bounds[1]
                assert analytic[0] <= truth <= analytic[1]
                oracle = 'CHECKED_EXACT_INTEGER_DECODER'
            decision = classify(observed, bounds)
            assert decision['status'] == ('OUTSIDE_TOLERANCE' if n == 256 else 'WITHIN_TOLERANCE')
            forecasts.append({'count_magnitude': h, 'binary64_probability': str(value64),
                              'AMP_probability': str(observed),
                              'exact_probability_enclosure': list(map(str, bounds)),
                              'independent_cycle_interval_contained': True,
                              'integer_oracle': oracle, 'decision': decision})
        result.append({'case': name, 'n': n, 'query': list(query), 'negative_edge': [1, 2] if n == 3 else [0, n-1],
                       'positive_tape_nodes': len(tape.nodes), 'mass_budget': budget,
                       'actual_binary64_primitives': reference.arith.float64.operations,
                       'AMP_scalar_rounding_results': device.arith.scalar_results,
                       'checked_device_words': device.arith.device_words,
                       'largest_exponent': device.max_exponent,
                       'maximum_exponent_bits': device.max_exponent.bit_length(),
                       'forecasts': forecasts})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cuda-worker', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.cuda_worker:
            import torch
            assert torch.cuda.is_available()
            torch.cuda.set_device(0)
            torch.cuda.reset_peak_memory_stats()
            report = {'status': 'PASS_ACTUAL_AMP_TOLERANCE_DIAGNOSTIC', 'process_id': os.getpid(),
                      'torch': torch.__version__, 'CUDA': torch.version.cuda,
                      'device': torch.cuda.get_device_name(0), 'stress_cases': stress_audit(torch)}
            torch.cuda.synchronize()
            report.update(peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),
                          peak_torch_reserved_bytes=torch.cuda.max_memory_reserved())
        else:
            report = {'status': 'PASS_CONDITIONAL_DECODER_ENCLOSURES',
                      'scope': 'scalar numerical decisions; no Runtime or complete native-state authority',
                      'tolerance': str(TOLERANCE), 'bound_audit': geometric_audit(),
                      'retained_device_reader': retained_device_audit(),
                      'small_exact_audit': small_audit(), 'original_search': search_audit(),
                      'stress_cases': stress_audit()}
    except Exception:
        args.output.write_text(json.dumps({'status': 'FAILED', 'process_id': os.getpid(),
                                          'traceback': traceback.format_exc()}, indent=2)+'\n')
        raise
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'stress_decisions':
                     [f['decision']['status'] for c in report['stress_cases'] for f in c['forecasts']]}, indent=2))


if __name__ == '__main__':
    main()
