"""Exact dyadic slack lifts and a robust nine-PRODUCT interval above minimum cap."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import random

from decoder_exact_limit_audit import predictions
from product_support_closure_audit import evaluate as evaluate_slots, groups
from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_product, add_sum, cube, sources


def build_subset_basis(d, k):
    nodes = sources(d)
    factors = []
    for i in range(d):
        tail = 2*i+1
        for _ in range(k):
            tail = add_sum(nodes, ((tail, F(1, 2)),))
        factors.append(add_sum(nodes, ((2*i, 1), (tail, 1))))
    current = factors[0]
    for factor in factors[1:]:
        current = add_product(nodes, current, factor)
    outputs = [current]
    for subset in range(1, 2**d):
        bit = subset & -subset
        coordinate = d-bit.bit_length()
        current = add_product(nodes, outputs[subset ^ bit], 2*coordinate+1)
        for _ in range(k):
            current = add_sum(nodes, ((current, 2),))
        outputs.append(current)
    assert sum(node[0] == 'product' for node in nodes) == 2**d+d-2
    assert sum(node[0] == 'sum' for node in nodes) == d*(k+1)+k*(2**d-1)
    return nodes, outputs


def positive_readout(d, epsilon, scale):
    if not 0 < epsilon < 1 or scale <= 1:
        raise ValueError('positive epsilon below one and strictly positive slack required')
    coefficients = []
    for subset in range(2**d):
        row = []
        for label in range(2**d):
            value = (scale-1)*(1-epsilon)**subset.bit_count()
            if label & subset == label:
                value += scale*(-epsilon)**(subset ^ label).bit_count()
            if value < 0:
                raise ValueError('negative coefficient: this proposed basis is too coarse for its slack')
            row.append(value)
        coefficients.append(tuple(row))
    return tuple(coefficients)


def dyadic_scale(nodes, source, coefficient):
    coefficient = F(coefficient)
    denominator = coefficient.denominator
    if coefficient < 0 or denominator & (denominator-1):
        raise ValueError('finite nonnegative dyadic coefficient required by this local-alphabet constructor')
    if not coefficient:
        return add_sum(nodes, ())
    tail = source
    for _ in range(denominator.bit_length()-1):
        tail = add_sum(nodes, ((tail, F(1, 2)),))
    current = tail
    for bit in bin(coefficient.numerator)[3:]:
        terms = ((current, 2), (tail, 1)) if bit == '1' else ((current, 2),)
        current = add_sum(nodes, terms)
    return current


def build_exact_slack(d, m):
    assert type(d) is int and d >= 2 and type(m) is int and m >= 0
    sigma = F(1, 2**m)
    scale = 1+sigma
    k = m+(4*d-1).bit_length()
    epsilon = F(1, 2**k)
    assert sigma*(1-epsilon)**d >= scale*epsilon
    nodes, basis = build_subset_basis(d, k)
    coefficients = positive_readout(d, epsilon, scale)
    heads = []
    for label in range(2**d):
        terms = []
        for subset, feature in enumerate(basis):
            weight = coefficients[subset][label]
            if weight:
                terms.append((dyadic_scale(nodes, feature, weight), 1))
        heads.append(add_sum(nodes, terms))
    count = 2**d
    assert sum(node[0] == 'product' for node in nodes) == count+d-2
    sum_upper = d*(k+1)+k*(count-1)+count**2*(2*(m+d*k)+1)+count
    assert sum(node[0] == 'sum' for node in nodes) <= sum_upper
    assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} <= {F(1, 2), F(1), F(2)}
    return nodes, heads, basis, coefficients, scale, k


def scalar_one_product_audit():
    rng = random.Random(2026091104)
    slots = groups(3, 1)
    count = sum(map(len, slots))
    checks = 0
    for _ in range(120):
        coefficients = [F(rng.randrange(5), rng.choice((2, 3, 7))) for _ in range(count)]
        original = evaluate_slots(3, 1, coefficients)
        for index, context in enumerate(cube(3)):
            active = [2*i+bit for i, bit in enumerate(context)]
            pruned = coefficients.copy()
            for combination in slots:
                for i, bit in enumerate(context):
                    pruned[combination[2*i+1-bit]] = 0
            values = evaluate_slots(3, 1, pruned)
            assert values[index] == original[index]
            assert all(0 <= a <= b for a, b in zip(values, original))
            u = [pruned[slots[0][i]] for i in active]
            v = [pruned[slots[1][i]] for i in active]
            weight = pruned[slots[2][-1]]
            linear = [pruned[slots[2][source]]+weight*u[i]*v[i] for i, source in enumerate(active)]
            quadratic = [weight*(u[i]*v[j]+u[j]*v[i]) for i in range(3) for j in range(i+1, 3)]
            assert values[index] == sum(linear)+sum(quadratic)
            neighbor_sum = sum(values[index ^ (1 << i)] for i in range(3))
            assert neighbor_sum == 2*sum(linear)+sum(quadratic) >= values[index]
            maximum_off = max(value for i, value in enumerate(values) if i != index)
            if values[index] > 0:
                assert maximum_off/(maximum_off+values[index]) >= F(1, 4)
            checks += 1
    cone_witness = tuple(F(x*y+x*z+y*z, 4) for x, y, z in cube(3))
    target = (F(0),)*7+(F(1),)
    assert max(abs(a-b) for a, b in zip(cone_witness, target)) == F(1, 4)
    return checks


def near_cap_probability_bound(slack):
    if slack < 0:
        raise ValueError('this bound is parameterized above the minimum cap nine')
    return max(F(0), (9-26*slack)/(45*(9+slack)))


def audit():
    scalar_checks = scalar_one_product_audit()
    assert near_cap_probability_bound(F(0)) == F(1, 45)
    assert near_cap_probability_bound(F(9, 26)) == 0
    assert near_cap_probability_bound(F(0))**2/4 == F(1, 8100)
    cases = ((2, 1), (2, 3), (2, 8), (3, 1), (3, 3), (3, 8), (3, 40), (4, 1), (4, 3))
    records, entries, resource_checks = [], 0, 0
    for d, m in cases:
        nodes, heads, basis, coefficients, scale, k = build_exact_slack(d, m)
        values = evaluate_tables(nodes, binary_tables(d))
        count = 2**d
        epsilon = F(1, 2**k)
        assert max(max(values[feature]) for feature in basis) <= 1
        peak = max(max(table) for table in values)
        assert peak <= 2*scale-1
        for context in range(count):
            for subset, feature in enumerate(basis):
                expected = epsilon**(context ^ subset).bit_count() if subset & context == subset else F(0)
                assert values[feature][context] == expected
            excess = tuple(values[head][context] for head in heads)
            assert excess == tuple((scale-1)+scale*(label == context) for label in range(count))
            q, normalizer = predictions(excess)
            assert normalizer == (count+1)*scale
            assert q == tuple(F(1+(label == context), count+1) for label in range(count))
            entries += count
        sums = sum(node[0] == 'sum' for node in nodes)
        if d == 3:
            # Every wrong excess equals sigma; compare exponents instead of
            # materializing a huge denominator for the conservative value floor.
            assert m <= sums*2**9
            resource_checks += 1
        records.append({'d': d, 'm': m, 'k': k, 'PRODUCTs': count+d-2,
                        'weighted_SUMs': sums, 'exact_normalizer': str((count+1)*scale),
                        'maximum_feature': str(peak), 'all_predictions_exact': True})

    rng = random.Random(2026091105)
    cap_checks = 0
    for slack in (F(0), F(1, 100), F(1, 20), F(1, 5), F(9, 26)):
        cap = 9+slack
        for trial in range(70):
            tables, predictions_table = [], []
            for context in range(8):
                if trial % 2:
                    epsilon = F(1, 2**rng.choice((2, 5, 20)))
                    total = (1+slack)*rng.choice((F(1), 1-epsilon))
                    excess = [total*epsilon/7]*8
                    excess[context] = total*(1-epsilon)
                else:
                    weights = [rng.randrange(6) for _ in range(8)]
                    weights[context] += 1
                    total = (1+slack)*rng.choice((F(0), F(1, 4), F(1, 2), F(1)))
                    excess = [total*w/sum(weights) for w in weights]
                q, normalizer = predictions(excess)
                assert 8 <= normalizer <= cap and max(q) <= F(1, 2)
                tables.append(tuple(excess))
                predictions_table.append(q)
            error = max(abs(predictions_table[x][i]-F(1+(x == i), 9)) for x in range(8) for i in range(8))
            head = rng.randrange(8)
            lower = 1-5*slack/9-2*cap*error
            upper = 1+slack
            wrong = slack/9+cap*error
            assert 2*wrong <= upper-lower
            for fraction in (F(0), F(1, 2), F(1)):
                comparison = []
                for x in range(8):
                    value = tables[x][head]
                    surplus = value-sum(v for i, v in enumerate(tables[x]) if i != head)
                    floor = max(F(0), surplus)
                    comparison.append((1-fraction)*floor+fraction*value)
                    assert 0 <= comparison[-1] <= upper
                    if x == head:
                        assert surplus >= lower
                    else:
                        assert comparison[-1] <= wrong
                if lower > 0:
                    scaled_error = max(abs(2*v/(upper+lower)-(x == head)) for x, v in enumerate(comparison))
                    assert scaled_error <= (upper-lower)/(upper+lower)
                cap_checks += 1

    failures = 0
    for epsilon, scale in ((F(1, 4), F(101, 100)), (F(1, 8), F(1))):
        try:
            positive_readout(3, epsilon, scale)
        except ValueError:
            failures += 1
        else:
            raise AssertionError('invalid direct positive lift accepted')
    for coefficient in (F(-1, 2), F(1, 3)):
        try:
            dyadic_scale(sources(1), 0, coefficient)
        except ValueError:
            failures += 1
        else:
            raise AssertionError('coefficient outside the dyadic constructor accepted')

    return {'status': 'PASS',
            'scope': 'static exact identity-noise decoder above minimum cap; complete at-most-eight lower bound near cap nine',
            'three_bit_scalar_one_PRODUCT_singleton_margin': '1/4; not claimed sharp for the one-PRODUCT class',
            'scalar_source_pruning_and_neighbor_checks': scalar_checks,
            'exact_dyadic_graph_cases': len(cases), 'individual_exact_excess_entries': entries,
            'selected_exact_graphs': records,
            'rational_cap_surplus_and_rescaling_checks': cap_checks,
            'invalid_positive_or_dyadic_lifts_rejected': failures,
            'near_cap_probability_margin_for_PRODUCTs_at_most_eight': '(9-26h)/(45*(9+h)), 0<=h<9/26',
            'cap_nine_probability_margin': '1/45', 'cap_nine_CE_margin': '1/8100',
            'exact_PRODUCT_minimum_on_open_cap_interval_9_to_243_over_26': 9,
            'all_dimension_exact_upper_above_minimum_cap': '2^d+d-2 for d>=2',
            'finite_alphabet_resource_checks': resource_checks,
            'joint_SUM_probability_accuracy_cost': 'Theta(log(1/(h+delta))) for fixed PRODUCT budget 9, 10 or 11',
            'joint_SUM_CE_accuracy_cost': 'Theta(log(1/(h+sqrt(rho)))) for fixed PRODUCT budget 9, 10 or 11',
            'not_claimed': ['243/26 is the sharp eight-PRODUCT range threshold',
                            'the quarter scalar margin is sharp for one PRODUCT',
                            'exact scalar singleton mass with fewer PRODUCTs',
                            'fixed arithmetic or registered value/install/persistence/AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_NORMALIZER_SLACK_DECODER_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
