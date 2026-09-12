"""Exact SUM-accuracy bounds, cap-preserving constructions, and arithmetic counterexamples."""
from fractions import Fraction as F
from math import ceil, comb, factorial, lcm
from pathlib import Path
import argparse
import json
import random

from conditional_coefficient_paths_audit import (bounded_mass_data, decoder_path, materialize,
                                               native_masses, normalize, rescale_hidden, round_and_expand)
from conditional_product_universality_audit import row_reduce
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_product, add_sum, sources


ALPHABET = (F(1, 2), F(1), F(2))
SCOPE = ('fixed finite sources, scalar SUM/binary PRODUCT DAGs, base one per label, '
         'finite normalizer cap, local weights {1/2,1,2}; supplied-graph bounds '
         'and constructions, not generic exactness/closure classification')


def counts(nodes):
    return sum(n[0] == 'sum' for n in nodes), sum(n[0] == 'product' for n in nodes)


def coefficient_degrees(nodes):
    """Degree in independent local SUM coefficient slots, retaining repeated ancestors."""
    degrees = []
    for node in nodes:
        if node[0] == 'source':
            degree = 0
        elif node[0] == 'product':
            degree = degrees[node[1]]+degrees[node[2]]
        else:
            degree = 1+max((degrees[p] for p, a in node[1] if a), default=-1)
        degrees.append(degree)
    return degrees


def lattice_check(nodes, heads, source_values, target, cap):
    assert {a for n in nodes if n[0] == 'sum' for _, a in n[1]} <= set(ALPHABET)
    sums, products = counts(nodes)
    source_denominator = lcm(*(v.denominator for row in source_values.values() for v in row))
    target_denominator = lcm(*(v.denominator for row in target for v in row))
    denominator = source_denominator**(2**products)*2**(sums*2**products)
    values = evaluate_tables(nodes, source_values)
    assert all((v*denominator).denominator == 1 for row in values for v in row)
    masses = native_masses(nodes, heads, source_values)
    assert max(map(sum, masses)) <= cap
    q = normalize(masses)
    for row in masses:
        t = sum(row)*denominator
        assert t.denominator == 1 and 0 < t <= cap*denominator
        assert all((v*denominator).denominator == 1 for v in row)
    error = max(abs(a-b) for row, goal in zip(q, target) for a, b in zip(row, goal))
    if not error:
        return 'EXACT'
    assert error >= 1/(target_denominator*cap*denominator)
    return 'SEPARATED'


def random_native(rng, d, products, labels):
    nodes = sources(d)
    def linear():
        return add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice(ALPHABET))
                               for _ in range(rng.randrange(1, 6))))
    for _ in range(products):
        left, right = linear(), linear()
        add_product(nodes, left, left if rng.randrange(3) == 0 else right)
    return nodes, [linear() for _ in range(labels)]


def arithmetic_and_perturbation_audit(rng):
    lattice_cases, separated, perturbations = 0, 0, 0
    for index in range(120):
        d, labels = 1+index % 3, 2+index % 4
        nodes, heads = random_native(rng, d, index % 6, labels)
        source_values = binary_tables(d) if index % 2 else {
            i: tuple(F(rng.randrange(5), rng.choice((2, 3, 5, 7))) for _ in range(2**d)) for i in range(2*d)}
        raw = [[rng.randrange(1, 10) for _ in range(labels)] for _ in range(2**d)]
        target = tuple(tuple(F(v, sum(row)) for v in row) for row in raw)
        masses = native_masses(nodes, heads, source_values)
        cap = max(map(sum, masses))
        result = lattice_check(nodes, heads, source_values, target, cap)
        separated += result == 'SEPARATED'
        lattice_cases += 1

        degrees = coefficient_degrees(nodes)
        sums, products = counts(nodes)
        degree = max(1, *(degrees[h] for h in heads))
        assert max(degrees) <= sums*2**products
        eta = F(1, 4*degree*(1+index % 7))
        perturbed = [('sum', tuple((p, a*(1-eta*F(rng.randrange(5), 4))) for p, a in n[1]))
                     if n[0] == 'sum' else n for n in nodes]
        changed = native_masses(perturbed, heads, source_values)
        contraction = (1-eta)**degree
        assert all(contraction*a <= b <= a for row, new in zip(masses, changed) for a, b in zip(row, new))
        q, rounded = normalize(masses), normalize(changed)
        error = max(abs(a-b) for row, new in zip(q, rounded) for a, b in zip(row, new))
        assert error <= degree*eta/(1-degree*eta) <= 2*degree*eta
        assert max(map(sum, changed)) <= cap
        perturbations += 1

    # Exactness is an explicit alternative, not a positive margin for every candidate.
    direct = [('source', 0, 0), ('source', 0, 1)]
    table = {0: (F(1),), 1: (F(0),)}
    assert lattice_check(direct, [0, 1], table, ((F(2, 3), F(1, 3)),), F(3)) == 'EXACT'
    squares, false_meshes = [], 0
    for products in range(8):
        nodes = list(direct)
        h = add_sum(nodes, ((0, F(1, 2)),))
        for _ in range(products):
            h = add_product(nodes, h, h)
        value = evaluate_tables(nodes, table)[h][0]
        assert counts(nodes) == (1, products)
        assert value.denominator == 2**(2**products)
        if products:
            assert (value*2).denominator != 1  # naive 2^S mesh ignores PRODUCT reuse
            false_meshes += 1
        assert lattice_check(nodes, [h, 1], table, ((F(1, 2), F(1, 2)),), F(3)) == 'SEPARATED'
        squares.append({'PRODUCTs': products, 'SUMs': 1, 'exact_denominator_power_of_two': 2**products})
    return {'arbitrary_native_lattice_checks': lattice_cases, 'nonexact_rational_comparisons': separated,
            'relative_coefficient_perturbation_checks': perturbations, 'exact_alternative_checked': True,
            'shared_square_meshes': squares, 'false_meshes_ignoring_reuse_rejected': false_meshes}


def quadratic_add(u, v):
    return u[0]+v[0], u[1]+v[1]


def quadratic_scale(a, u):
    return a*u[0], a*u[1]


def quadratic_multiply(u, v):
    return u[0]*v[0]+2*u[1]*v[1], u[0]*v[1]+u[1]*v[0]


def quadratic_sign(u):
    """Exact sign of a+b*sqrt(2), using rational comparisons only."""
    a, b = u
    if not b:
        return (a > 0)-(a < 0)
    if not a or (a > 0) == (b > 0):
        return (b > 0)-(b < 0)
    difference = a*a-2*b*b
    assert difference != 0
    return ((a > 0)-(a < 0))*((difference > 0)-(difference < 0))


def quadratic_native_values(nodes, source_values):
    values, width = [], len(next(iter(source_values.values())))
    for i, node in enumerate(nodes):
        if node[0] == 'source':
            row = source_values[i]
        elif node[0] == 'product':
            row = [quadratic_multiply(u, v) for u, v in zip(values[node[1]], values[node[2]])]
        else:
            row = []
            for x in range(width):
                value = (F(0), F(0))
                for parent, weight in node[1]:
                    value = quadratic_add(value, quadratic_scale(weight, values[parent][x]))
                row.append(value)
        assert all(quadratic_sign(v) >= 0 for v in row)
        values.append(row)
    return values


def algebraic_norm_audit(rng):
    pool = [(F(a), F(b)) for a, b in ((0, 0), (1, 0), (0, 1), (2, -1), (-1, 1))]
    for value in pool:
        assert quadratic_sign(value) == 0 or quadratic_sign(quadratic_add(value, (F(-1, 4), F(0)))) > 0
        assert quadratic_sign(quadratic_add((F(4), F(0)), quadratic_scale(-1, (value[0], -value[1])))) > 0
        assert quadratic_sign(quadratic_add((F(4), F(0)), (value[0], -value[1]))) > 0
    cases, norm_checks = 0, 0
    for index in range(32):
        d, products = 1+index % 2, index % 4
        nodes, heads = random_native(rng, d, products, 2)
        source_values = {i: tuple(rng.choice(pool) for _ in range(2**d)) for i in range(2*d)}
        values = quadratic_native_values(nodes, source_values)
        masses = [[quadratic_add((F(1), F(0)), values[h][x]) for h in heads] for x in range(2**d)]
        totals = [quadratic_add(*row) for row in masses]
        cap = max(ceil(abs(a)+2*abs(b)) for a, b in totals)
        assert all(quadratic_sign(quadratic_add((F(cap), F(0)), quadratic_scale(-1, total))) >= 0 for total in totals)
        sums = counts(nodes)[0]
        degree, power = 2**products, sums*2**products
        monomials = comb(2*d+degree, degree)
        # All sources are integral in Z[sqrt(2)], with positive values >=1/4;
        # every conjugate source has absolute value <4. Target entries use A=4.
        conjugate_bound = 12*(1+monomials*cap*16**degree)
        for x, row in enumerate(masses):
            for label, mass in enumerate(row):
                target = (F(1, 2), F(1 if (x+label) % 2 else -1, 4))
                residual = quadratic_add(mass, quadratic_scale(-1, quadratic_multiply(target, totals[x])))
                if quadratic_sign(residual) == 0:
                    continue
                zeta = quadratic_scale(4*2**power, residual)
                assert zeta[0].denominator == zeta[1].denominator == 1
                norm = zeta[0]**2-2*zeta[1]**2
                assert norm.denominator == 1 and abs(norm) >= 1
                assert quadratic_multiply(zeta, (zeta[0], -zeta[1])) == (norm, F(0))
                conjugate = (zeta[0], -zeta[1])
                conjugate_abs = quadratic_scale(quadratic_sign(conjugate), conjugate)
                assert quadratic_sign(quadratic_add((F(conjugate_bound*2**power), F(0)),
                                                    quadratic_scale(-1, conjugate_abs))) >= 0
                # Cross-multiply the claimed probability gap, retaining the actual normalizer.
                residual_abs = quadratic_scale(quadratic_sign(residual), residual)
                multiplier = 4*cap*conjugate_bound*2**(2*power)
                assert quadratic_sign(quadratic_add(quadratic_scale(multiplier, residual_abs),
                                                    quadratic_scale(-1, totals[x]))) >= 0
                norm_checks += 1
        cases += 1
    # A legitimate algebraic exact target has zero residual: it receives no positive gap.
    exact_sources = {0: ((F(3), F(2)),), 1: ((F(3), F(-2)),)}
    exact_nodes = [('source', 0, 0), ('source', 0, 1)]
    values = quadratic_native_values(exact_nodes, exact_sources)
    masses = [quadratic_add((F(1), F(0)), row[0]) for row in values]
    total = quadratic_add(*masses)
    assert total == (F(8), F(0))
    for mass, sign in zip(masses, (1, -1)):
        assert mass == quadratic_multiply((F(1, 2), F(sign, 4)), total)
    assert norm_checks > 0
    return {'field': 'Q(sqrt(2))', 'field_degree': 2, 'native_graphs': cases,
            'exact_integer_norm_and_probability_gap_checks': norm_checks,
            'irrational_sources_and_targets_retained_exactly': True,
            'negative_conjugates_retained': True, 'exact_algebraic_alternative_checked': True,
            'general_nonzero_gap_form': 'C_star*2^(-e*S*2^P)'}


def decoder_quantization_audit():
    records, common_structure = [], None
    for accuracy_power in (1, 4, 8, 16, 32):
        delta = F(1, 2**accuracy_power)
        epsilon = F(1, 2**(accuracy_power+2))
        nodes, heads = decoder_path(3)
        source_values = binary_tables(3)
        limit, tail = bounded_mass_data(nodes, heads, source_values, F(9))
        assert tail == 7
        target = normalize(limit)
        ideal = materialize(nodes, epsilon)
        beta = 1/(1+tail*epsilon)
        assert beta.denominator & (beta.denominator-1)  # final contraction is genuinely non-dyadic
        corrected = [add_sum(ideal, ((h, beta),)) for h in heads]
        normalized, outputs, normalized_sources = rescale_hidden(ideal, corrected, source_values, F(1))
        ideal_q = normalize(native_masses(normalized, outputs, normalized_sources))
        assert max(abs(a-b) for row, goal in zip(ideal_q, target) for a, b in zip(row, goal)) <= delta/2
        degrees = coefficient_degrees(normalized)
        degree = max(degrees[h] for h in outputs)
        weights = [a for node in normalized if node[0] == 'sum' for _, a in node[1] if a]
        assert epsilon <= min(weights) <= max(weights) <= 1/epsilon
        eta = delta/(4*degree)
        extra = (4*degree-1).bit_length()
        precision = 2*accuracy_power+2+extra
        assert F(1, 2**precision) <= eta*min(weights)
        rounded, expanded, mapping = round_and_expand(normalized, precision)
        for original, new in zip(normalized, rounded):
            if original[0] == 'sum':
                assert len(original[1]) == len(new[1])
                assert all(p == q and (1-eta)*a <= b <= a for (p, a), (q, b) in zip(original[1], new[1]))
        expanded_sources = {mapping[p]: row for p, row in normalized_sources.items()}
        expanded_heads = [mapping[h] for h in outputs]
        actual_values = evaluate_tables(expanded, expanded_sources)
        masses = native_masses(expanded, expanded_heads, expanded_sources)
        q = normalize(masses)
        error = max(abs(a-b) for row, goal in zip(q, target) for a, b in zip(row, goal))
        assert error <= delta and error > 0
        assert max(map(sum, masses)) <= 9 and max(v for row in actual_values for v in row) <= 1
        assert {a for node in expanded if node[0] == 'sum' for _, a in node[1]} <= set(ALPHABET)
        sums, products = counts(expanded)
        assert products == 9
        initial_sums = counts(normalized)[0]
        assert sums <= initial_sums+len(weights)*(2*precision+accuracy_power+2)
        slope = 5*len(weights)
        intercept = initial_sums+len(weights)*(6+2*extra)
        assert sums <= slope*accuracy_power+intercept
        structure = (initial_sums, len(weights), degree, slope, intercept)
        if common_structure is not None:
            assert common_structure == structure
        common_structure = structure
        records.append({'probability_tolerance': '2^(-%d)' % accuracy_power, 'epsilon_power': accuracy_power+2,
                        'rounding_precision': precision, 'SUMs': sums, 'PRODUCTs': products,
                        'actual_probability_error': str(error), 'normalizer_at_most_9': True,
                        'all_activations_at_most_1': True})
    return {'finite_native_graphs': records, 'original_SUMs': common_structure[0],
            'coefficient_slots': common_structure[1], 'maximum_coefficient_degree': common_structure[2],
            'proved_linear_SUM_upper_for_delta_2_to_minus_m': '%d*m+%d' % common_structure[3:],
            'earlier_exact_exclusion': 'P<=11 at cap nine; DECODER_EXACT_AND_LIMIT_COMPLEXITY.md',
            'generic_rational_probability_lower_if_not_exact': '1/(81*2^(S*2^P))',
            'stronger_specialized_upper_baseline': 'S=13*k+6, error<=2^(-k)/3; generic quantizer is not cost-optimized'}


def sparse_dyadic(n):
    return sum((F(1, 2**factorial(m)) for m in range(1, n+1)), F(0))


def scalar_graph(coefficient):
    nodes = [('source', 0, 0)]
    head = dyadic_scale(nodes, 0, coefficient)
    zero = add_sum(nodes, ())
    return nodes, [head, zero]


def real_exact_local_nonattainment_audit():
    target, cap = ((F(5, 8), F(3, 8)),), F(8, 3)
    source_values = {0: (F(1),)}
    real = [('source', 0, 0)]
    real_heads = [add_sum(real, ((0, F(2, 3)),)), add_sum(real, ())]
    assert normalize(native_masses(real, real_heads, source_values)) == target
    assert max(map(sum, native_masses(real, real_heads, source_values))) == cap
    assert cap*min(target[0]) == 1
    assert (cap*max(target[0])-1).denominator == 3  # every finite local graph is dyadic
    records = []
    for precision in (1, 2, 4, 8, 16, 32):
        denominator = 2**precision
        below = F((F(2, 3)*denominator)//1, denominator)
        nodes, heads = scalar_graph(below)
        masses = native_masses(nodes, heads, source_values)
        q = normalize(masses)
        assert max(map(sum, masses)) < cap
        assert lattice_check(nodes, heads, source_values, target, cap) == 'SEPARATED'
        error = target[0][0]-q[0][0]
        assert error == (2-3*below)/(8*(2+below)) > 0
        sums, products = counts(nodes)
        assert products == 0 and sums <= 2*precision+1

        total = F(ceil(cap*denominator), denominator)
        assert cap < total < cap+F(1, denominator)
        exact_nodes = [('source', 0, 0)]
        exact_heads = [dyadic_scale(exact_nodes, 0, p*total-1) for p in target[0]]
        exact_masses = native_masses(exact_nodes, exact_heads, source_values)
        assert normalize(exact_masses) == target and max(map(sum, exact_masses)) == total
        assert counts(exact_nodes)[1] == 0
        assert max(v for row in evaluate_tables(exact_nodes, source_values) for v in row) <= 1
        records.append({'precision': precision, 'same_cap_approximate_SUMs': sums,
                        'same_cap_probability_error': str(error), 'slack_exact_cap': str(total),
                        'slack_exact_SUMs': counts(exact_nodes)[0]})
    return {'target': ['5/8', '3/8'], 'minimum_cap': str(cap), 'PRODUCTs': 0,
            'real_coefficient_exact_excess': '2/3', 'any_finite_local_PRODUCT_budget_still_not_exact_at_minimum_cap': True,
            'finite_native_records': records}


def product_precision_audit():
    records = []
    for steps in range(1, 9):
        nodes = [('source', 0, 0)]
        g = add_sum(nodes, ((0, F(1, 2)),))
        t = add_sum(nodes, ((g, F(1, 2)),))
        for i in range(steps):
            factor = add_sum(nodes, ((0, F(1, 2)), (t, F(1, 2))))
            g = add_product(nodes, g, factor)
            g = add_sum(nodes, ((g, F(2)),))
            if i+1 < steps:
                t = add_product(nodes, t, t)
        zero = add_sum(nodes, ())
        source_values = {0: (F(1),)}
        values = evaluate_tables(nodes, source_values)
        tail = F(1, 2**(2**(steps+1)))
        assert values[g][0] == F(2, 3)*(1-tail)
        denominator_power = 2**(steps+1)-1
        assert values[g][0].denominator == 2**denominator_power
        masses = native_masses(nodes, [g, zero], source_values)
        assert max(map(sum, masses)) < F(8, 3)
        error = F(5, 8)-normalize(masses)[0][0]
        assert error == 3*tail/(32-8*tail) > 0
        assert counts(nodes) == (2*steps+3, 2*steps-1)
        assert max(v for row in values for v in row) <= 1
        assert {a for node in nodes if node[0] == 'sum' for _, a in node[1]} <= set(ALPHABET)
        records.append({'steps': steps, 'SUMs': counts(nodes)[0], 'PRODUCTs': counts(nodes)[1],
                        'tail_exponent_in_base_two': 2**(steps+1), 'excess_denominator_power_of_two': denominator_power,
                        'same_cap_and_activation_bound': True})
    return {'target': ['5/8', '3/8'], 'cap': '8/3', 'activation_cap': 1,
            'exact_error_formula': '3*tau/(32-8*tau), tau=2^(-2^(n+1))',
            'SUMs': '2*n+3', 'PRODUCTs': '2*n-1', 'accuracy_cost_order': 'O(log log(1/delta_n))',
            'native_graphs': records, 'sharp_joint_cost_not_claimed': True}


def irrational_boundaries_audit():
    records = []
    for n in range(2, 7):
        partial = sparse_dyadic(n)
        tail_upper = F(1, 2**(factorial(n+1)-1))
        assert 0 < partial < partial+tail_upper < 1
        nodes, heads = scalar_graph(partial)
        actual = normalize(native_masses(nodes, heads, {0: (F(1),)}))[0]
        upper = (1+partial+tail_upper)/(2+partial+tail_upper)
        lower = (1+partial)/(2+partial)
        assert actual[0] == lower and 0 < upper-lower < tail_upper/4
        sums_target, products = counts(nodes)
        assert products == 0 and sums_target <= 2*factorial(n)+1
        assert max(v for row in evaluate_tables(nodes, {0: (F(1),)}) for v in row) <= 1

        nodes, heads = scalar_graph(1+partial)
        source_interval = (1/(1+partial+tail_upper), 1/(1+partial))
        endpoint_predictions = []
        for endpoint in source_interval:
            source_values = {0: (endpoint,)}
            masses = native_masses(nodes, heads, source_values)
            assert max(map(sum, masses)) <= 3
            assert max(v for row in evaluate_tables(nodes, source_values) for v in row) <= 1
            endpoint_predictions.append(normalize(masses)[0][0])
        assert endpoint_predictions[1] == F(2, 3)
        assert 0 < F(2, 3)-endpoint_predictions[0] < tail_upper/6
        sums_source, products = counts(nodes)
        assert products == 0 and sums_source <= 2*factorial(n)+2
        records.append({'series_terms': n, 'rational_source_irrational_target_SUMs': sums_target,
                        'irrational_source_rational_target_SUMs': sums_source,
                        'next_tail_exponent': factorial(n+1),
                        'SUM_over_log_accuracy_upper_for_first_example': str(F(sums_target, factorial(n+1)+1)),
                        'SUM_over_log_accuracy_upper_for_second_example': str(F(sums_source, factorial(n+1))),
                        'exact_rational_interval_and_native_endpoint_checks': True})
    return {'records': records, 'infinite_series_and_nonexactness': 'proved; not inferred from finite endpoints',
            'first_error_upper': '2^(-1-(n+1)!)', 'second_error_upper': '2^(1-(n+1)!)/6',
            'common_PRODUCT_count': 0, 'normalizer_cap': 3, 'activation_cap': 1}


def unbounded_arity_audit():
    # Complete P=0 exact equations for source values 1 and 2 are inconsistent.
    _, pivots = row_reduce([[F(1), F(-2), F(1)], [F(2), F(-4), F(1)]])
    assert 2 in pivots
    records = []
    for n in (1, 2, 4, 16, 64):
        nodes = [('source', 0, 0)]
        heads = [add_sum(nodes, ((0, F(1)),)*(2*n)), add_sum(nodes, ((0, F(1)),)*n)]
        source_values = {0: (F(1), F(2))}
        masses = native_masses(nodes, heads, source_values)
        q = normalize(masses)
        error = max(abs(row[0]-F(2, 3)) for row in q)
        assert counts(nodes) == (2, 0) and error == F(1, 3*(2+3*n))
        assert max(map(sum, masses)) == 2+6*n
        assert sum(len(node[1]) for node in nodes if node[0] == 'sum') == 3*n
        records.append({'n': n, 'SUMs': 2, 'SUM_edges': 3*n, 'normalizer': 2+6*n, 'error': str(error)})
    return {'strictly_positive_rational_target': 'constant (2/3,1/3)', 'rational_source': [1, 2],
            'complete_SUM_exact_equations_inconsistent': True, 'uncapped_constant_node_count_witnesses': records}


def audit():
    rng = random.Random(2026091201)
    return {'status': 'PASS', 'scope': SCOPE,
            'fixed_algebraic_data_SUM_trichotomy': ['positive closure gap', 'eventually minimum exact SUM count',
                                              'Theta(log(1/delta)) for nonexact closure points'],
            'universal_pointwise_upper': 'O(log(1/delta)), same finite cap and PRODUCT count',
            'arithmetic_and_relative_rounding': arithmetic_and_perturbation_audit(rng),
            'algebraic_number_field_extension': algebraic_norm_audit(rng),
            'general_quantization_of_decoder_path': decoder_quantization_audit(),
            'real_exact_versus_local_nonattainment': real_exact_local_nonattainment_audit(),
            'PRODUCT_precision_tradeoff': product_precision_audit(),
            'transcendental_data_counterexamples': irrational_boundaries_audit(),
            'necessary_finite_cap_with_unpriced_arity': unbounded_arity_audit(),
            'not_claimed': ['a uniform bound over unknown targets or leading amplitudes',
                            'generic classification into the three asymptotic branches',
                            'rational and arbitrary-real exact classes coincide',
                            'sharp constants or complete SUM-edge/encoding/physical costs',
                            'registered acquisition, value, persistence, install or AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_SUM_ACCURACY_COMPLEXITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
