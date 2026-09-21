"""Static exact-radix-power lowering of the positive count decoder.

Only a syntactically proved power receives an exact exponent shift. The
remaining products still execute half arithmetic in the AMP diagnostic.
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
import radix9_frontier as original
import radix9_accuracy_enclosure as enclosure
from fp_reference.semantics import ArithmeticUnresolved


def analyze(tape, heads):
    powers, budgets, products = [], [], []
    for tag, *args in tape.nodes:
        if tag in ('zero', 'one', 'nine', 'factor'):
            powers.append(tag != 'zero')
            budgets.append((0, 0))
            continue
        left, right = args
        a, b = budgets[left], budgets[right]
        if tag == 'mul':
            shift = powers[left] or powers[right]
            products.append((powers[left], powers[right]))
            powers.append(powers[left] and powers[right])
            budgets.append((a[0]+b[0]+int(not shift), a[1]+b[1]))
        else:
            assert tag == 'add'
            powers.append(False)
            budgets.append((max(a[0], b[0]), max(a[1], b[1])+1))
        if powers[-1]:
            assert budgets[-1] == (0, 0)
    return tuple(products), tuple(powers), tuple(budgets), tuple(max(budgets[h][k] for h in heads) for k in (0, 1))


def uniform_error_bound(budget):
    """Absolute forecast bound from mixed-rounding counts and positive odds."""
    h, s = budget
    assert type(h) is int and type(s) is int and min(h, s) >= 0
    eta = F(3*h, 1 << 11)+F(2*h+19*s, 1 << 24)
    if eta >= 1:
        raise ArithmeticUnresolved('mixed-rounding envelope exhausted')
    sum_epsilon = F(1, 1 << 19)
    final = 2*sum_epsilon/(1-sum_epsilon)
    return eta/(2-eta)+final


class Decoder(original.Decoder):
    def run(self, tape, heads, rows):
        self.plan, self.power_tags, self.budgets, self.mass_budget = analyze(tape, heads)
        self.product_index = self.exact_shifts = self.nonpower_products = 0
        result = super().run(tape, heads, rows)
        assert self.product_index == len(self.plan)
        for state, power in zip(result[1], self.power_tags):
            if power:
                assert all(m == 1 for m in state.mantissa.values)
        return result

    def mul(self, left, right):
        left_power, right_power = self.plan[self.product_index]
        self.product_index += 1
        if not (left_power or right_power):
            self.nonpower_products += 1
            return super().mul(left, right)
        power, other = (left, right) if left_power else (right, left)
        assert all(m == 1 for m in power.mantissa.values)
        exponent = tuple(a+b for a, b in zip(left.exponent, right.exponent))
        # Keep the original conservative product guard and the input envelope.
        if max(exponent)+2 > original.EXPONENT_CAP:
            raise ArithmeticUnresolved('exact power product exceeds its declared exponent field')
        exponent = tuple(0 if m == 0 else e for m, e in zip(other.mantissa.values, exponent))
        self.max_exponent = max(self.max_exponent, *exponent)
        self.exact_shifts += 1
        result = original.Wide(other.mantissa, exponent)
        # The immutable mantissa Batch, including its actual CUDA tensor, is
        # shared. No CPU answer is cast/uploaded as a replacement product.
        assert result.mantissa is other.mantissa
        return result


def local_bound_audit():
    half, single = F(1, 1 << 11), F(1, 1 << 24)
    eps = F(1, 1 << 19)
    assert (1+single)**19 < 1+eps and (1-single)**19 > 1-eps
    assert F(1, 9**15) < single
    checked = 0
    for h, s in product(range(4), repeat=2):
        eta = 3*h*half+(2*h+19*s)*single
        assert (1-half)**(3*h)*(1-single)**(2*h+19*s) >= 1-eta
        assert (1+half)**(3*h)*(1+single)**(2*h+19*s) <= 1/(1-eta)
        checked += 1
    assert uniform_error_bound((1, 256)) < enclosure.TOLERANCE
    assert uniform_error_bound((1, 512)) > enclosure.TOLERANCE
    try:
        uniform_error_bound((1000, 0))
    except ArithmeticUnresolved:
        pass
    else:
        raise AssertionError('exhausted mixed-rounding bound accepted')
    # Both sums happen to round to mantissa1 at these counts. Neither is a
    # proved exact power, so their product retains a general half operation.
    tape = original.Tape()
    left = tape.op('add', 1, tape.factor(0, 0))
    right = tape.op('add', 1, tape.factor(1, 0))
    value = tape.op('mul', left, right)
    decoder = Decoder(1, 'amp')
    _, states = decoder.run(tape, (value, value), ((16, 32),))
    assert states[left].mantissa.values == states[right].mantissa.values == (F(1),)
    assert not decoder.power_tags[left] and not decoder.power_tags[right]
    assert decoder.nonpower_products == 1 and decoder.mass_budget == (1, 2)
    return {'local_inequality_cases': checked, 'rounded_one_is_not_a_power_proof': True,
            'exhausted_error_budget_refusals': 1,
            'uniform_bound_H1_S256': str(uniform_error_bound((1, 256))),
            'uniform_bound_H1_S512': str(uniform_error_bound((1, 512)))}


def small_audit(torch=None):
    groups = ((3, ((0, 1), (0, 2), (1, 2)), tuple(product(range(-2, 3), repeat=3)), tuple(product(range(3), repeat=2))),
              (5, ((0, 1), (1, 2), (1, 3), (1, 4)), tuple(product(range(-1, 2), repeat=4)),
               ((0, 1), (1, 4), (2, 3), (0, 0), (4, 4))))
    result = []
    half, single = F(1, 1 << 11), F(1, 1 << 24)
    for n, support, rows, queries in groups:
        forecasts = nodes = power_nodes = words = scalar = shifts = products = 0
        maximum, witness = F(-1), None
        for query in queries:
            tape, heads = original.compile_tape(n, support, query)
            decoder = Decoder(len(rows), 'amp', torch)
            probabilities, states = decoder.run(tape, heads, rows)
            factors = {}
            for budget in set(decoder.budgets):
                h, s = budget
                factors[budget] = ((1-half)**(3*h)*(1-single)**(2*h+19*s),
                                   (1+half)**(3*h)*(1+single)**(2*h+19*s))
            for row_index, (signed, observed) in enumerate(zip(rows, probabilities.values)):
                exact = []
                for node_index, (tag, *args) in enumerate(tape.nodes):
                    if tag in ('zero', 'one', 'nine'):
                        value = {'zero': 0, 'one': 1, 'nine': 9}[tag]
                    elif tag == 'factor':
                        edge, parity = args
                        value = 9**(max(signed[edge], 0) if parity == 0 else max(-signed[edge], 0))
                    else:
                        a, b = (exact[j] for j in args)
                        value = a*b if tag == 'mul' else a+b
                    exact.append(value)
                    state = states[node_index]
                    e, m = state.exponent[row_index], state.mantissa.values[row_index]
                    decoded = m*9**e
                    lo, hi = factors[decoder.budgets[node_index]]
                    assert lo*value <= decoded <= hi*value
                    if decoder.power_tags[node_index]:
                        assert m == 1 and value == 9**e
                        power_nodes += 1
                    if not value:
                        assert m == 0 and e == 0
                    nodes += 1
                truth = original.probability_oracle(n, support, query, signed)
                assert F(exact[heads[0]], exact[heads[0]]+exact[heads[1]]) == truth
                error = abs(observed-truth)
                assert error <= uniform_error_bound(decoder.mass_budget)
                assert error <= enclosure.TOLERANCE
                if error > maximum:
                    maximum = error
                    witness = {'counts': signed, 'query': query, 'computed': str(observed), 'exact': str(truth)}
                forecasts += 1
            words += decoder.arith.device_words
            scalar += decoder.arith.scalar_results
            shifts += decoder.exact_shifts
            products += decoder.nonpower_products
        result.append({'n': n, 'profiles': len(rows), 'queries': len(queries), 'forecasts': forecasts,
                       'exact_node_enclosures': nodes, 'exact_power_node_checks': power_nodes,
                       'static_shift_nodes_over_queries': shifts, 'general_product_nodes_over_queries': products,
                       'scalar_rounding_results': scalar, 'checked_device_words': words,
                       'maximum_absolute_error': str(maximum), 'maximum_absolute_error_float': float(maximum),
                       'witness': witness})
    return result


def stress_cases():
    return enclosure.stress_cases()+(('cycle512_recovery', 512, (0, 128), (8,)),)


def stress_audit(torch=None):
    old = json.loads((ROOT/'evidence/minimal/FP_RADIX9_ACCURACY_ENCLOSURE.json').read_text())
    gpu = json.loads((ROOT/'evidence/minimal/FP_RADIX9_ACCURACY_CUDA.json').read_text())
    assert gpu['status'] == 'COMPLETE_EXECUTION'
    old_rows = {r['case']: r for r in old['stress_cases']}
    result = []
    for name, n, query, magnitudes in stress_cases():
        support, _ = enclosure.cycle_input(n, magnitudes[0])
        rows = tuple(enclosure.cycle_input(n, h)[1] for h in magnitudes)
        tape, heads = original.compile_tape(n, support, query)
        decoder = Decoder(len(rows), 'amp', torch)
        probabilities, _ = decoder.run(tape, heads, rows)
        bound = uniform_error_bound(decoder.mass_budget)
        actual64 = 0
        if name in old_rows:
            prior = old_rows[name]
            physical = next(row for row in gpu['workers'][0]['result']['stress_cases'] if row['case'] == name)
            assert physical['forecasts'] == prior['forecasts']
            assert (prior['n'], prior['query']) == (n, list(query))
            references = tuple(F(f['binary64_probability']) for f in prior['forecasts'])
            old_probabilities = tuple(F(f['AMP_probability']) for f in prior['forecasts'])
            baseline_source = gpu['registration']['source']
            old_scalar = prior['AMP_scalar_rounding_results']
        else:
            reference = original.Decoder(len(rows), 'binary64')
            references, _ = reference.run(tape, heads, rows)
            references = references.values
            actual64 = reference.arith.float64.operations
            prior = next(row for row in old['original_search'] if (row['n'], row['query'], row['h']) == (n, list(query), magnitudes[0]))
            old_probabilities = (F(prior['AMP_probability']),)
            baseline_source = 'retained CPU AMP-machine search; no old device execution for this512-cycle'
            old_scalar = None
        forecasts = []
        for h, signed, observed, value64, baseline in zip(magnitudes, rows, probabilities.values, references, old_probabilities):
            bounds = enclosure.enclosure(value64, max(tape.budgets[j] for j in heads))
            decision = enclosure.classify(observed, bounds)
            assert decision['status'] == 'WITHIN_TOLERANCE'
            if h < 10**12:
                truth = original.probability_oracle(n, support, query, signed)
                assert bounds[0] <= truth <= bounds[1]
                assert abs(observed-truth) <= bound
            forecasts.append({'count_magnitude': h, 'AMP_probability': str(observed),
                              'baseline_probability': str(baseline), 'reference_interval': list(map(str, bounds)),
                              'decision': decision, 'baseline_decision': enclosure.classify(baseline, bounds)})
        result.append({'case': name, 'n': n, 'query': list(query), 'mass_budget_H_S': decoder.mass_budget,
                       'uniform_absolute_error_bound': str(bound), 'uniform_absolute_error_bound_float': float(bound),
                       'uniform_1e_3_class_decided': bound <= enclosure.TOLERANCE,
                       'static_exact_shift_nodes': decoder.exact_shifts,
                       'general_product_nodes': decoder.nonpower_products,
                       'positive_tape_nodes': len(tape.nodes), 'scalar_rounding_results': decoder.arith.scalar_results,
                       'checked_device_words': decoder.arith.device_words,
                       'baseline_scalar_rounding_results': old_scalar, 'baseline_source': baseline_source,
                       'new_binary64_primitive_checks': actual64,
                       'largest_exponent': decoder.max_exponent, 'forecasts': forecasts})
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
            report = {'status': 'PASS_ACTUAL_MIXED_POWER_LOWERING', 'process_id': os.getpid(),
                      'torch': torch.__version__, 'CUDA': torch.version.cuda,
                      'device': torch.cuda.get_device_name(0),
                      'small_audit': small_audit(torch), 'stress_cases': stress_audit(torch)}
            torch.cuda.synchronize()
            report.update(peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),
                          peak_torch_reserved_bytes=torch.cuda.max_memory_reserved())
        else:
            report = {'status': 'PASS_STATIC_POWER_LOWERING_AUDIT',
                      'scope': 'passive decoder arithmetic, not a native Program/Runtime bridge',
                      'local_bounds': local_bound_audit(), 'small_audit': small_audit(), 'stress_cases': stress_audit()}
    except Exception:
        args.output.write_text(json.dumps({'status': 'FAILED', 'process_id': os.getpid(),
                                          'traceback': traceback.format_exc()}, indent=2)+'\n')
        raise
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'small_forecasts': sum(r['forecasts'] for r in report['small_audit']),
                      'stress_decisions': [f['decision']['status'] for r in report['stress_cases'] for f in r['forecasts']]}, indent=2))


if __name__ == '__main__':
    main()
