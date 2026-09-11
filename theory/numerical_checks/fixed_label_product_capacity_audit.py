"""Exact fixed-alphabet PRODUCT capacity constructions and complete-class parameter audit."""
from fractions import Fraction as F
from math import comb, lcm
from pathlib import Path
import argparse
import json
import random

from conditional_product_universality_audit import mobius, native_from_masses, rank
from decoder_exact_limit_audit import predictions
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_conditional_parity_audit import build_parity
from two_product_support_border_audit import add_product, add_sum, cube, sources


def parameter_count(d, k, p):
    return p*p+(2*d+k+1)*p+k*(d+1)


def capacity_bounds(d, k):
    if d < 1 or k < 2:
        raise ValueError('d>=1 and k>=2 required')
    n = 2**d
    choices = [(n-d-1, None)]+[((k+1)*2**a+2**(d-a)-d-k-2, a) for a in range(1, d)]
    upper, split = min(choices, key=lambda pair: pair[0])
    lower, high = 0, n
    while lower < high:
        middle = (lower+high)//2
        if parameter_count(d, k, middle) >= n*(k-1):
            high = middle
        else:
            lower = middle+1
    dimension_lower = lower
    lower = max(dimension_lower, min(n, k)-d-1, (d-1).bit_length(), 0)
    # FROZEN_FEATURE_UNIVERSALITY.md strengthens the former parameter lower bound.
    frozen = n-d-1
    assert 0 <= lower <= upper <= frozen
    return {'d': d, 'labels': k, 'dimension_lower': dimension_lower,
            'all_class_lower': lower, 'constructive_upper': upper, 'block_width': split,
            'frozen_numerical_bank_exact_minimum': frozen}


def block_features(nodes, d, coordinates, one):
    width = len(coordinates)
    result = [one]
    for subset in range(1, 2**width):
        bit = subset & -subset
        literal = 2*coordinates[width-bit.bit_length()]+1
        result.append(literal if subset == bit else add_product(nodes, result[subset ^ bit], literal))
    return result


def positive_masses(d, target, integer_alphabet):
    target = tuple(tuple(map(F, row)) for row in target)
    if len(target) != 2**d or not target[0] or any(len(row) != len(target[0]) for row in target):
        raise ValueError('complete rectangular target required')
    if any(min(row) <= 0 or sum(row) != 1 for row in target):
        raise ValueError('strictly positive normalized target required')
    ratio = max(max(column)/min(column) for column in zip(*target))
    c, growth = max(1/v for v in target[0]), d*(1+ratio)
    if integer_alphabet:
        c = F(lcm(*(value.denominator for row in target for value in row)))
        growth = F((growth.numerator+growth.denominator-1)//growth.denominator)
    masses = tuple(tuple(c*growth**context.bit_count()*value for value in row)
                   for context, row in enumerate(target))
    return target, masses, c, growth


def build_universal(d, target, integer_alphabet=False):
    target, masses, c, growth = positive_masses(d, target, integer_alphabet)
    k = len(target[0])
    bounds = capacity_bounds(d, k)
    a = bounds['block_width']
    if a is None:
        nodes, heads, _ = native_from_masses(d, masses, integer_alphabet)
        return nodes, heads, masses, c, growth, bounds
    b = d-a
    nodes = sources(d)
    one = add_sum(nodes, ((0, 1), (1, 1)))
    left = block_features(nodes, d, list(range(a)), one)
    right = block_features(nodes, d, list(range(a, d)), one)

    def weighted_sum(terms):
        terms = [(parent, value) for parent, value in terms if value]
        if integer_alphabet:
            assert all(value.denominator == 1 for _, value in terms)
            terms = [(dyadic_scale(nodes, parent, value), F(1)) for parent, value in terms]
        return add_sum(nodes, terms)

    heads = []
    for label in range(k):
        coefficients = mobius([row[label]-1 for row in masses])
        assert min(coefficients) >= 0
        terms = [(one, coefficients[0])]
        terms.extend((left[u], coefficients[u << b]) for u in range(1, 2**a))
        terms.extend((right[v], coefficients[v]) for v in range(1, 2**b))
        for u in range(1, 2**a):
            inner = weighted_sum((right[v], coefficients[(u << b) | v]) for v in range(1, 2**b))
            cross = add_product(nodes, left[u], inner)
            terms.append((cross, F(1)))
        heads.append(weighted_sum(terms))
    assert sum(node[0] == 'product' for node in nodes) == bounds['constructive_upper']
    return nodes, heads, masses, c, growth, bounds


def flatten_normal_form(d, nodes, heads):
    """Signed affine chart of the full positive graph; used only for a lower bound."""
    p = sum(node[0] == 'product' for node in nodes)
    width = d+1+p
    representations, parents = [], []
    for node in nodes:
        vector = [F(0)]*width
        if node[0] == 'source':
            _, coordinate, bit = node
            vector[0] = 1-bit
            vector[coordinate+1] = 2*bit-1
        elif node[0] == 'sum':
            for parent, weight in node[1]:
                vector = [a+weight*b for a, b in zip(vector, representations[parent])]
        else:
            j = len(parents)
            parents.append(tuple(tuple(representations[parent][:d+1+j]) for parent in node[1:]))
            vector[d+1+j] = F(1)
        representations.append(tuple(vector))
    readouts = [representations[head] for head in heads]
    assert sum(len(side) for pair in parents for side in pair)+sum(map(len, readouts)) == parameter_count(d, len(heads), p)
    return parents, readouts


def evaluate_normal_form(d, parents, readouts):
    masses = []
    for context in cube(d):
        values = [F(1), *map(F, context)]
        for left, right in parents:
            values.append(sum(a*b for a, b in zip(left, values))*sum(a*b for a, b in zip(right, values)))
        masses.append(tuple(1+sum(a*b for a, b in zip(readout, values)) for readout in readouts))
    return tuple(masses)


def dependence_count(d, k, p):
    """A finite integer dimension witness, not an explicitly reconstructed polynomial."""
    m, dimension = parameter_count(d, k, p), 2**d*(k-1)
    if m >= dimension:
        raise ValueError('parameter count does not exclude this class')
    degree = 2**d*(2**(p+1)-1)
    t = 1
    while comb(dimension+t, dimension) <= comb(m+degree*t, m):
        t *= 2
    return {'d': d, 'labels': k, 'PRODUCTs': p, 'parameter_count': m,
            'probability_dimension': dimension, 'cleared_coordinate_degree_bound': degree,
            'polynomial_degree_witness': t,
            'strict_monomial_count_inequality_verified': True}


def determinant(matrix):
    rows = [list(map(F, row)) for row in matrix]
    result = F(1)
    for j in range(len(rows)):
        pivot = next((i for i in range(j, len(rows)) if rows[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            result = -result
        value = rows[j][j]
        result *= value
        for i in range(j+1, len(rows)):
            factor = rows[i][j]/value
            rows[i] = [a-factor*b for a, b in zip(rows[i], rows[j])]
    return result


def frozen_bank_obstruction():
    # Full unary span and three x-centered monomials: W has dimension eight.
    contexts = cube(4)
    bank = [[F(v) for v in (1, x, y, z, w, x*y, x*z, x*w)] for x, y, z, w in contexts]
    frozen_nodes = sources(4)
    frozen_features = [add_product(frozen_nodes, 1, other) for other in (3, 5, 7)]
    frozen_values = evaluate_tables(frozen_nodes, binary_tables(4))
    assert bank == [[F(1)]+[frozen_values[v][i] for v in (1, 3, 5, 7, *frozen_features)] for i in range(16)]
    assert sum(node[0] == 'product' for node in frozen_nodes) == 3
    target = [F(3 if (y ^ z ^ w) else 1, 4) for x, y, z, w in contexts]
    matrix = [row+[-q*v for v in row] for row, q in zip(bank, target)]
    value = determinant(matrix)
    assert rank(bank) == 8 and value != 0 and rank(matrix) == 16
    # If q=n/t with n,t in this W, [W,-diag(q)W] has a nonzero null vector.
    # A real full-class two-PRODUCT graph realizes the same target, ignoring x.
    original, heads, _ = build_parity(F(3))
    nodes = sources(4)
    mapping = {i: i+2 for i in range(6)}
    for old, node in enumerate(original[6:], 6):
        if node[0] == 'sum':
            mapping[old] = add_sum(nodes, ((mapping[parent], weight) for parent, weight in node[1]))
        else:
            mapping[old] = add_product(nodes, mapping[node[1]], mapping[node[2]])
    mapped_heads = [mapping[head] for head in heads]
    values = evaluate_tables(nodes, binary_tables(4))
    for i in range(16):
        q, total = predictions([values[head][i] for head in mapped_heads])
        assert q[1] == target[i] and total <= 44
    assert sum(node[0] == 'product' for node in nodes) == 2
    return {'fixed_bank_rank': 8, 'fixed_bank_PRODUCTs': 3,
            'exact_target_obstruction_determinant': str(value),
            'full_native_witness_PRODUCTs': 2, 'full_native_witness_cap': '44'}


def audit():
    rng = random.Random(2026091111)
    cases = [(d, 2) for d in range(1, 10)]+[(4, 3), (6, 3), (7, 5), (8, 5), (6, 9), (5, 32)]
    records, entries, integer_cases = [], 0, 0
    for d, k in cases:
        rows = [[rng.randrange(1, 10) for _ in range(k)] for _ in range(2**d)]
        target = [tuple(F(value, sum(row)) for value in row) for row in rows]
        for integer_alphabet in ((False, True) if d <= 4 else (False,)):
            nodes, heads, masses, c, growth, bounds = build_universal(d, target, integer_alphabet)
            values = evaluate_tables(nodes, binary_tables(d))
            for i, row in enumerate(target):
                excess = [values[head][i] for head in heads]
                assert tuple(1+v for v in excess) == masses[i]
                q, total = predictions(excess)
                assert q == row and total == c*growth**i.bit_count()
                entries += k
            if integer_alphabet:
                assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} <= {F(1), F(2)}
                integer_cases += 1
            p = sum(node[0] == 'product' for node in nodes)
            assert p == bounds['constructive_upper']
            records.append({**bounds, 'actual_PRODUCTs': p, 'integer_local_alphabet': integer_alphabet,
                            'maximum_normalizer': str(c*growth**d)})

    normal_form_cases, signed_charts = 100, 0
    for _ in range(normal_form_cases):
        d, k, p = rng.randrange(1, 6), rng.randrange(2, 6), rng.randrange(6)
        nodes = sources(d)
        heads = [random_graph(rng, nodes, p)]
        for _ in range(k-1):
            heads.append(add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((F(1, 2), F(1), F(2)))) for _ in range(6))))
        parents, readouts = flatten_normal_form(d, nodes, heads)
        values = evaluate_tables(nodes, binary_tables(d))
        expected = tuple(tuple(1+values[head][i] for head in heads) for i in range(2**d))
        assert evaluate_normal_form(d, parents, readouts) == expected
        signed_charts += any(value < 0 for pair in parents for side in pair for value in side) or any(value < 0 for row in readouts for value in row)

    count_checks = 0
    for d in range(1, 31):
        for k in (2, 3, 5, 2**max(1, d//2), 2**d, 2**d+1):
            result = capacity_bounds(d, k)
            if k >= 2**d:
                assert result['all_class_lower'] == result['constructive_upper'] == 2**d-d-1
            assert result['frozen_numerical_bank_exact_minimum'] == 2**d-d-1
            if d >= 6 and k <= 2**d:
                # An explicit conservative uniform lower/upper order check.
                assert 64*result['all_class_lower']**2 >= 2**d*k
                assert result['constructive_upper']**2 <= 16*2**d*k
            count_checks += 1
    for d, adaptive, frozen in ((3, 3, 4), (8, 44, 247), (20, 3560, 1048555)):
        result = capacity_bounds(d, 2)
        assert result['constructive_upper'] == adaptive and result['frozen_numerical_bank_exact_minimum'] == frozen
        assert result['all_class_lower'] <= adaptive < frozen
    invalid = 0
    for d, k in ((0, 2), (2, 1), (-1, 3)):
        try:
            capacity_bounds(d, k)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError('invalid class accepted')

    return {'status': 'PASS',
            'scope': 'full static fixed-label universality bounds; exact finite graphs; no Runtime or topology-emergence authority',
            'exact_and_approximation_worst_case_order': 'Theta(min(2^d,sqrt(2^d*k))) for k>=2',
            'frozen_numerical_bank_exact_minimum': '2^d-d-1 for every k>=2',
            'universal_graph_cases': len(records), 'integer_local_alphabet_cases': integer_cases,
            'exact_probability_entries': entries, 'graph_records': records,
            'original_shared_DAG_normal_form_cases': normal_form_cases, 'signed_affine_charts_retained': signed_charts,
            'finite_capacity_count_checks': count_checks,
            'algebraic_dependence_count_witnesses': [dependence_count(4, 2, 0), dependence_count(5, 2, 1)],
            'frozen_bank_scope_counterexample': frozen_bank_obstruction(), 'invalid_classes_rejected': invalid,
            'not_claimed': ['sharp universal counts for every small d,k', 'identical exact and approximation counts for every fixed alphabet',
                            'sublinear total coefficient, SUM-edge or target-information cost', 'necessary graph-topology change',
                            'finite normalizer, registered value/install/persistence or AMP guarantees']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_FIXED_LABEL_PRODUCT_CAPACITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
