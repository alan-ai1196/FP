"""Exact three-bit decoder minimum twelve versus all-dimension limit minimum N+d-2."""
from collections import Counter
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import argparse
import json
import sys

from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_product, add_sum, cube, sources


def union_closure(generators):
    result = {0}
    for generator in generators:
        result |= {a | generator for a in result}
    return frozenset(result)


def intersections(state):
    return {a & b for a in state for b in state}


def three_bit_exact_search():
    """Complete exact-support auxiliary class only; not a limit-support search."""
    contexts = cube(3)
    basis = tuple(sum(1 << j for j, x in enumerate(contexts) if x[i] == bit)
                  for i in range(3) for bit in (0, 1))
    point_maps = []
    for permutation in permutations(range(3)):
        for flip in contexts:
            point_maps.append(tuple(contexts.index(tuple(x[permutation[i]] ^ flip[i] for i in range(3)))
                                    for x in contexts))
    assert len(set(point_maps)) == 48
    assert all(set(mapping) == set(range(8)) for mapping in point_maps)
    assert all(tuple(a[b[i]] for i in range(8)) in point_maps for a in point_maps for b in point_maps)
    mask_maps = [tuple(sum(1 << mapping[i] for i in range(8) if mask >> i & 1) for mask in range(256))
                 for mapping in point_maps]
    assert all({mapping[mask] for mask in basis} == set(basis) for mapping in mask_maps)
    assert all({mapping[1 << i] for i in range(8)} == {1 << i for i in range(8)} for mapping in mask_maps)

    def canonical(state):
        return min(tuple(sorted(mapping[mask] for mask in state)) for mapping in mask_maps)

    initial = union_closure(basis)
    assert len(initial) == 28
    levels = [{canonical(initial)}]
    records = []
    for depth in range(4):
        histogram, transitions, next_level = Counter(), 0, set()
        for state in levels[depth]:
            products = intersections(state)
            available = sum((1 << i) in products for i in range(8))
            histogram[available] += 1
            assert available < 8
            if depth < 3:
                for support in products-set(state):
                    if support.bit_count() >= 2:
                        extended = set(state) | {mask | support for mask in state}
                        next_level.add(canonical(extended))
                        transitions += 1
        records.append({'auxiliary_PRODUCTs': depth, 'state_orbits': len(levels[depth]),
                        'available_singleton_histogram': dict(sorted(histogram.items())),
                        'maximum_available_singletons': max(histogram),
                        'extensions_enumerated': transitions})
        if depth < 3:
            levels.append(next_level)
    assert [row['state_orbits'] for row in records] == [1, 8, 266, 10835]
    assert [row['maximum_available_singletons'] for row in records] == [0, 2, 4, 6]
    assert [row['extensions_enumerated'] for row in records] == [130, 1094, 38013, 0]

    # Independent raw ordered auxiliary sequences, rebuilding each full SUM closure.
    raw_sequences = [()]
    raw_counts = []
    for depth in (1, 2):
        next_sequences, raw_states, raw_orbits = [], set(), set()
        for sequence in raw_sequences:
            state = union_closure((*basis, *sequence))
            for support in intersections(state)-state:
                if support.bit_count() < 2:
                    continue
                extended_sequence = (*sequence, support)
                rebuilt = union_closure((*basis, *extended_sequence))
                assert rebuilt == state | {mask | support for mask in state}
                next_sequences.append(extended_sequence)
                raw_states.add(rebuilt)
                raw_orbits.add(canonical(rebuilt))
        assert raw_orbits == levels[depth]
        raw_counts.append({'auxiliary_PRODUCTs': depth, 'ordered_sequences': len(next_sequences),
                           'states_without_symmetry': len(raw_states), 'matching_state_orbits': len(raw_orbits)})
        raw_sequences = next_sequences

    # The output property is externally fixed: all eight one-point masks.
    four_auxiliaries = (3, 12, 48, 192)
    state = union_closure((*basis, *four_auxiliaries))
    assert all((1 << i) in intersections(state) for i in range(8))
    return {'decision_class': 'three-bit complete exact singleton-support DAGs with free SUMs; terminalization theorem',
            'cube_automorphisms_checked': 48, 'levels': records,
            'raw_prefix_cross_checks': raw_counts,
            'four_auxiliary_upper_supports': four_auxiliaries,
            'exact_SUPPORT_and_mass_PRODUCT_minimum': 12,
            'not_a_closure_certificate': True}


def build_limit(d, k):
    assert type(d) is int and d >= 2 and type(k) is int and k >= 1
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
    for _ in range(d):
        tail, terms = current, []
        for _ in range(k):
            tail = add_sum(nodes, ((tail, F(1, 2)),))
            terms.append((tail, 1))
        current = add_sum(nodes, terms)
    outputs = [current]
    for subset in range(1, 2**d):
        bit = subset & -subset
        coordinate = d-bit.bit_length()
        current = add_product(nodes, outputs[subset ^ bit], 2*coordinate+1)
        for _ in range(k):
            current = add_sum(nodes, ((current, 2),))
        outputs.append(current)
    assert sum(node[0] == 'product' for node in nodes) == 2**d+d-2
    assert sum(node[0] == 'sum' for node in nodes) == 2*d*(k+1)+k*(2**d-1)
    assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} == {F(1, 2), F(1), F(2)}
    return nodes, outputs


def build_exact_three_bit():
    nodes = sources(3)
    pairs = [add_product(nodes, x, 2+y) for x, y in product((0, 1), repeat=2)]
    outputs = [add_product(nodes, pair, 4+z) for pair in pairs for z in (0, 1)]
    assert sum(node[0] == 'product' for node in nodes) == 12
    return nodes, outputs


def evaluate_at(nodes, context, cast=F):
    values, peak = [], cast(0)
    for index, node in enumerate(nodes):
        if node[0] == 'source':
            value = cast(int(context[node[1]] == node[2]))
        elif node[0] == 'product':
            value = values[node[1]]*values[node[2]]
        else:
            value = cast(0)
            for parent, weight in node[1]:
                assert parent < index and weight >= 0
                value = value+(cast(weight.numerator)/cast(weight.denominator))*values[parent]
        values.append(value)
        peak = max(peak, value)
    return values, peak


def predictions(excess, cast=F):
    masses = [cast(1)+value for value in excess]
    normalizer = cast(0)
    for mass in masses:
        normalizer = normalizer+mass
    return tuple(mass/normalizer for mass in masses), normalizer


def audit():
    search = three_bit_exact_search()
    nodes, outputs = build_exact_three_bit()
    values = evaluate_tables(nodes, binary_tables(3))
    assert all(values[output] == tuple(F(i == j) for i in range(8)) for j, output in enumerate(outputs))
    assert max(max(table) for table in values) == 1
    for x in range(8):
        prediction, normalizer = predictions([values[output][x] for output in outputs])
        assert normalizer == 9 and prediction == tuple(F(1+(x == i), 9) for i in range(8))

    graph_cases, context_cases, head_cases = 0, 0, 0
    selected = []
    for d in range(2, 7):
        count, cap = 2**d, 2**d+1
        for k in (1, 3, 8):
            epsilon = F(1, 2**k)
            contraction = (1-epsilon)**d
            nodes, outputs = build_limit(d, k)
            values = evaluate_tables(nodes, binary_tables(d))
            assert max(max(table) for table in values) == 1
            mass_error, probability_error, chi_square_maximum = F(0), F(0), F(0)
            for context in range(count):
                excess = tuple(values[output][context] for output in outputs)
                formula = tuple(contraction*epsilon**(context.bit_count()-subset.bit_count())
                                if subset & context == subset else F(0) for subset in range(count))
                assert excess == formula
                total = sum(excess)
                assert total == contraction*(1+epsilon)**context.bit_count()
                assert total <= (1-epsilon**2)**d <= 1
                target_excess = tuple(F(subset == context) for subset in range(count))
                mass_error = max(mass_error, *(abs(a-b) for a, b in zip(excess, target_excess)))
                prediction, normalizer = predictions(excess)
                target = tuple(F(1+(subset == context), cap) for subset in range(count))
                assert normalizer == count+total <= cap
                deficit = target[context]-prediction[context]
                assert deficit >= 0 and all(prediction[i] >= target[i] for i in range(count) if i != context)
                assert sum(prediction[i]-target[i] for i in range(count) if i != context) == deficit
                assert max(abs(a-b) for a, b in zip(prediction, target)) == deficit
                assert deficit <= (1-contraction)/cap <= d*epsilon/cap
                chi_square = sum((a-b)**2/b for a, b in zip(target, prediction))
                assert chi_square <= 2*d*d*epsilon*epsilon/cap
                probability_error = max(probability_error, deficit)
                chi_square_maximum = max(chi_square_maximum, chi_square)
                context_cases += 1
                head_cases += count
            assert mass_error == 1-contraction <= d*epsilon
            exact_probability_error = F(2, cap)-(1+contraction)/(count+(1-epsilon**2)**d)
            assert probability_error == exact_probability_error
            graph_cases += 1
            if k == 3:
                selected.append({'d': d, 'k': k, 'PRODUCTs': count+d-2,
                                 'weighted_SUMs': 2*d*(k+1)+k*(count-1),
                                 'exact_mass_sup_error': str(mass_error),
                                 'exact_probability_sup_error': str(probability_error)})

    # Binary64 is a separate execution path, never the exact support authority.
    assert sys.float_info.mant_dig == 53 and sys.float_info.max_exp == 1024
    floating = []
    for k in (54, 400):
        nodes, outputs = build_limit(3, k)
        epsilon = F(1, 2**k)
        contraction = (1-epsilon)**3
        all_equal = True
        for index, context in enumerate(cube(3)):
            exact, exact_peak = evaluate_at(nodes, context)
            rounded, rounded_peak = evaluate_at(nodes, context, float)
            assert exact_peak == 1 and rounded_peak <= 1
            actual = tuple(exact[output] for output in outputs)
            formula = tuple(contraction*epsilon**(index.bit_count()-subset.bit_count())
                            if subset & index == subset else F(0) for subset in range(8))
            assert actual == formula
            q_exact, t_exact = predictions(actual)
            q_float, _ = predictions([rounded[output] for output in outputs], float)
            target_exact = tuple(F(1+(subset == index), 9) for subset in range(8))
            target_float = tuple((1.0+(subset == index))/9.0 for subset in range(8))
            assert t_exact <= 9 and q_exact != target_exact
            all_equal &= q_float == target_float
        # The last evaluated context is 111, whose correct readout is label 7.
        assert exact[outputs[7]] == contraction > F(999, 1000)
        if k == 54:
            assert all_equal and exact[outputs[0]] > 0 and rounded[outputs[0]] > 0
        else:
            assert not all_equal and all(rounded[output] == 0 for output in outputs)
            assert q_float == (0.125,)*8
        floating.append({'d': 3, 'k': k, 'PRODUCTs': 9,
                         'weighted_SUMs': 6*(k+1)+7*k,
                         'binary64_full_prediction_table_equals_target': all_equal,
                         'exact_tail_at_111_is_positive': True,
                         'binary64_all_excess_heads_underflow_to_zero_at_111': k == 400,
                         'exact_correct_excess_at_111_exceeds_999_over_1000': True})

    # Small exact checks of the resource-law constants; no huge bound artifacts.
    assert F(2, 9)-F(1, 8) == F(7, 72)
    resource_checks = 0
    for budget in (9, 10, 11):
        for k in (1, 3):
            epsilon = F(1, 2**k)
            contraction = (1-epsilon)**3
            sums = 13*k+6
            tau = F(1, 2**(sums*2**budget))
            error = F(2, 9)-(1+contraction)/(8+(1-epsilon**2)**3)
            assert min(F(7, 72), tau/9) <= error <= epsilon/3
            assert 2*3**2*epsilon**2/9 == 2*epsilon**2
            resource_checks += 1

    return {'status': 'PASS',
            'scope': 'complete static unary-source scalar DAGs; exact and approximation decision classes distinguished',
            'three_bit_exact_support_enumeration': search,
            'all_dimension_approximation_PRODUCT_minimum': '2^d+d-2 for d>=2',
            'same_approximation_minimum_for_identity_conditionals_at_cap': '2^d+1',
            'local_SUM_coefficient_alphabet': ['1/2', '1', '2'],
            'maximum_intermediate_feature': 1,
            'weighted_SUM_count_formula': '2d(k+1)+k(2^d-1)',
            'exact_finite_graph_grid_cases': graph_cases,
            'full_context_cases': context_cases, 'individual_excess_entries_checked': head_cases,
            'selected_graphs': selected,
            'CE_excess_upper_bound': '2*d^2*2^(-2k)/(2^d+1)',
            'binary64_counterexamples': floating,
            'three_bit_resource_law_constant_checks': resource_checks,
            'three_bit_SUM_accuracy_cost_at_PRODUCT_budgets_9_to_11':
                'Theta(log(1/delta)) for probability error; Theta(log(1/rho)) for excess CE; exact arithmetic',
            'not_claimed': ['exact minimum 2^d+d-2',
                            'higher-dimensional exact minima beyond d=3',
                            'arbitrary accuracy at fixed SUM or fixed arithmetic resources',
                            'safe removal of an asymptotically singleton parent',
                            'registered value/install/persistence or reference-AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_DECODER_EXACT_LIMIT_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
