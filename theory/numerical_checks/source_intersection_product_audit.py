"""Exact source-intersection witnesses, face minima, and shared identity lower bounds."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from product_support_closure_audit import verify_accept, verified_parity_proof
from shared_disjoint_product_audit import flatten_outputs
from two_product_support_border_audit import add_product, add_sum, cube, faces, sources


def contrast_constant(positive_sources, products):
    assert type(positive_sources) is int and positive_sources >= 1
    assert type(products) is int and products >= 0
    bound = 1
    for j in range(1, products+1):
        bound = (positive_sources+j-1)**2*bound**2
    result = (positive_sources+products)*bound
    formula = positive_sources+products
    for j in range(1, products+1):
        formula *= (positive_sources+j-1)**(2**(products-j+1))
    assert formula == result
    return result


def evaluate_tables(nodes, source_values):
    """Original graph evaluation; source tables may be arbitrary fixed rationals."""
    width = len(next(iter(source_values.values())))
    values = []
    for index, node in enumerate(nodes):
        if node[0] == 'source':
            table = tuple(map(F, source_values[index]))
            assert len(table) == width and min(table) >= 0
        elif node[0] == 'product':
            assert all(0 <= parent < index for parent in node[1:])
            table = tuple(a*b for a, b in zip(values[node[1]], values[node[2]]))
        else:
            assert node[0] == 'sum'
            assert all(0 <= parent < index and weight >= 0 for parent, weight in node[1])
            table = tuple(sum((weight*values[parent][x] for parent, weight in node[1]), F(0))
                          for x in range(width))
        values.append(table)
    return values


def retained_monomial(nodes, output, values, x):
    """One choice per flattened parent, preserving every PRODUCT's shared definition."""
    assert values[output][x] > 0
    products = [i for i, node in enumerate(nodes) if node[0] == 'product']
    requests = [parent for i in products for parent in nodes[i][1:]]+[output]
    order, combinations = flatten_outputs(nodes, requests)
    assert order == products
    retained = {i: (F(1), Counter({i: 1})) for i, node in enumerate(nodes) if node[0] == 'source'}

    def choose(terms):
        if not terms:
            return F(0), Counter()
        feature = max(terms, key=lambda i: terms[i]*values[i][x])
        coefficient, exponents = retained[feature]
        return terms[feature]*coefficient, exponents.copy()

    for j, index in enumerate(products):
        left, right = choose(combinations[2*j]), choose(combinations[2*j+1])
        retained[index] = (left[0]*right[0], left[1]+right[1])
    coefficient, exponents = choose(combinations[-1])
    assert coefficient > 0 and all(values[i][x] > 0 for i in exponents)
    assert len(exponents) <= len(products)+1 and sum(exponents.values()) <= 2**len(products)
    monomial = []
    for y in range(len(values[output])):
        value = coefficient
        for source, exponent in exponents.items():
            value *= values[source][y]**exponent
        monomial.append(value)
    assert all(0 <= a <= b for a, b in zip(monomial, values[output]))
    positive = [i for i, node in enumerate(nodes) if node[0] == 'source' and values[i][x] > 0]
    bound = contrast_constant(len(positive), len(products))
    assert monomial[x]*bound >= values[output][x]
    mu = min([F(1), *(v/values[i][x] for i in positive for v in values[i] if v > 0)])
    region = frozenset(y for y in range(len(values[output])) if all(values[i][y] > 0 for i in exponents))
    assert x in region
    assert all(values[output][y]*bound >= mu**(2**len(products))*values[output][x] for y in region)
    return {'coefficient': coefficient, 'exponents': exponents,
            'region': region, 'source_ratio_floor': mu, 'contrast_constant': bound}


def binary_tables(d):
    return {2*i+bit: tuple(F(x[i] == bit) for x in cube(d)) for i in range(d) for bit in (0, 1)}


def short_face_condition(d, products, support):
    eligible = [face for pattern, face in faces(d)
                if sum(value != -1 for value in pattern) <= products+1 and face <= support]
    return all(any(x in face for face in eligible) for x in support)


def random_graph(rng, nodes, products):
    for _ in range(products):
        left = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 7), F(1), F(5))))
                               for _ in range(rng.randrange(1, 6))))
        right = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 3), F(2))))
                                for _ in range(rng.randrange(1, 6))))
        add_product(nodes, left, left if rng.randrange(3) == 0 else right)
    output = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), F(1), F(3))))
                             for _ in range(rng.randrange(1, 7))))
    return output


def decoder_graph(d):
    nodes = sources(d)

    def indicators(indices):
        if len(indices) == 1:
            return [2*indices[0], 2*indices[0]+1]
        middle = len(indices)//2
        left, right = indicators(indices[:middle]), indicators(indices[middle:])
        return [add_product(nodes, a, b) for a in left for b in right]

    outputs = indicators(tuple(range(d)))
    return nodes, outputs


def upper_count(d):
    return 0 if d == 1 else 2**d+upper_count(d//2)+upper_count(d-d//2)


def check_identity_scale(excess, truth):
    count = len(excess)
    cap = F(count+1)
    assert count >= 3 and min(excess) >= 0 and sum(excess) <= 1
    normalizer = count+sum(excess)
    predictions = [(1+value)/normalizer for value in excess]
    targets = [F(1+(i == truth), count+1) for i in range(count)]
    error = max(abs(q-p) for q, p in zip(predictions, targets))
    assert max(predictions) <= 2/cap <= F(1, 2)
    surplus = excess[truth]-sum(value for i, value in enumerate(excess) if i != truth)
    assert surplus == (2*predictions[truth]-1)*normalizer+count-2
    assert surplus >= 1-2*cap*error
    assert 0 <= excess[truth] <= 1
    assert all(value <= cap*error for i, value in enumerate(excess) if i != truth)
    assert 1-max(F(0), surplus) <= 2*cap*error


def audit():
    rng = random.Random(2026091102)
    generic_graphs, binary_graphs = 240, 200
    retained_checks, nonunit_ratio_checks = 0, 0
    for _ in range(generic_graphs):
        count, width = rng.randrange(1, 8), rng.randrange(2, 17)
        nodes = [('source', i) for i in range(count)]
        source_values = {i: tuple(rng.choice((F(0), F(0), F(1, 9), F(1), F(7, 3))) for _ in range(width))
                         for i in range(count)}
        output = random_graph(rng, nodes, rng.randrange(6))
        values = evaluate_tables(nodes, source_values)
        for x, value in enumerate(values[output]):
            if value:
                result = retained_monomial(nodes, output, values, x)
                nonunit_ratio_checks += result['source_ratio_floor'] < 1
                retained_checks += 1
    for _ in range(binary_graphs):
        d = rng.randrange(1, 6)
        nodes = sources(d)
        products = rng.randrange(5)
        output = random_graph(rng, nodes, products)
        values = evaluate_tables(nodes, binary_tables(d))
        eligible_faces = {face for pattern, face in faces(d)
                          if sum(value != -1 for value in pattern) <= products+1}
        for x, value in enumerate(values[output]):
            if value:
                result = retained_monomial(nodes, output, values, x)
                assert result['source_ratio_floor'] == 1 and result['region'] in eligible_faces
                retained_checks += 1

    # A consistent selection is essential; not every expanded monomial is short.
    nodes = sources(4)
    output = add_sum(nodes, ((2*i+1, 1) for i in range(4)))
    for _ in range(2):
        output = add_product(nodes, output, output)
    values = evaluate_tables(nodes, binary_tables(4))
    result = retained_monomial(nodes, output, values, 15)
    assert len(result['exponents']) == 1 and sum(result['exponents'].values()) == 4
    polynomial = {(0, 0, 0, 0): 1}
    for _ in range(4):
        next_polynomial = Counter()
        for exponent, coefficient in polynomial.items():
            for i in range(4):
                next_exponent = list(exponent)
                next_exponent[i] += 1
                next_polynomial[tuple(next_exponent)] += coefficient
        polynomial = next_polynomial
    assert polynomial[(1, 1, 1, 1)] == 24

    # At P=0 this necessary support test is also the complete SUM support rule.
    sum_catalogues = {}
    for d in (2, 3):
        source_supports = [frozenset(i for i, x in enumerate(cube(d)) if x[j] == bit)
                           for j in range(d) for bit in (0, 1)]
        actual = {frozenset().union(*(support for support, bit in zip(source_supports, bits) if bit))
                  for bits in product((0, 1), repeat=2*d)}
        allowed = {frozenset(i for i in range(2**d) if mask >> i & 1)
                   for mask in range(1 << (2**d))
                   if short_face_condition(d, 0, frozenset(i for i in range(2**d) if mask >> i & 1))}
        assert actual == allowed
        sum_catalogues[str(d)] = len(allowed)
    assert sum_catalogues == {'2': 10, '3': 28}

    root = Path(__file__).resolve().parents[2]
    border_record = json.loads((root/'evidence/minimal/FP_PRODUCT_SUPPORT_CLOSURE_AUDIT.json').read_text())
    assert verify_accept(4, 2, 8896, tuple(border_record['border_certificate_exponents']))
    assert short_face_condition(4, 2, frozenset(i for i in range(16) if 8896 >> i & 1))
    assert short_face_condition(3, 2, frozenset(i for i in range(8) if 150 >> i & 1))
    verified_parity_proof()  # Yet this support is outside the full two-PRODUCT closure.

    face_cases = 0
    for d in range(2, 8):
        contexts = cube(d)
        for codimension in range(1, d+1):
            nodes = sources(d)
            output = 0
            for i in range(1, codimension):
                output = add_product(nodes, output, 2*i+(i % 2))
            output = add_sum(nodes, ((output, F(3, 2)),))
            target = tuple(F(3, 2)*all(x[i] == i % 2 for i in range(codimension)) for x in contexts)
            values = evaluate_tables(nodes, binary_tables(d))
            assert values[output] == target
            assert sum(node[0] == 'product' for node in nodes) == codimension-1
            if codimension >= 2:
                assert not short_face_condition(d, codimension-2,
                                                frozenset(i for i, value in enumerate(target) if value))
            face_cases += 1

    square_records = []
    for d in range(2, 9):
        nodes = sources(d)
        output = add_sum(nodes, ((2*i+1, 1) for i in range(d)))
        products = d-2
        for _ in range(products):
            output = add_product(nodes, output, output)
        degree = 2**products
        denominator = d**degree+(d-1)**degree
        output = add_sum(nodes, ((output, F(1, denominator)),))
        values = evaluate_tables(nodes, binary_tables(d))
        error = F((d-1)**degree, denominator)
        target = tuple(F(all(x)) for x in cube(d))
        assert max(abs(g-f) for g, f in zip(values[output], target)) == error
        assert error >= F(1, contrast_constant(d, products)+1)
        if d in (2, 3, 4, 6, 8):
            square_records.append({'d': d, 'PRODUCTs': products, 'degree': degree, 'exact_sup_error': str(error)})

    decoder_records = []
    for d in range(2, 7):
        nodes, outputs = decoder_graph(d)
        values = evaluate_tables(nodes, binary_tables(d))
        count = 2**d
        assert sum(node[0] == 'product' for node in nodes) == upper_count(d)
        assert all(values[output] == tuple(F(i == j) for i in range(count)) for j, output in enumerate(outputs))
        assert all(sum(values[output][x] for output in outputs)+count == count+1 for x in range(count))
        scalar_margin = F(1, contrast_constant(d, d-2)+1)
        decoder_records.append({'d': d, 'labels': count,
                                'exact_and_approximation_PRODUCT_lower_bound': count+d-2,
                                'exact_PRODUCT_upper_witness': upper_count(d),
                                'scalar_margin': str(scalar_margin),
                                'probability_margin_below_lower_count': str(scalar_margin/(2*(count+1))),
                                'CE_margin_below_lower_count': str(scalar_margin**2/(2*count*(count+1)**2))})
    assert decoder_records[1]['scalar_margin'] == '1/37'
    assert decoder_records[1]['probability_margin_below_lower_count'] == '1/666'
    assert decoder_records[1]['CE_margin_below_lower_count'] == '1/1774224'

    scale_cases = 0
    for count in (4, 8, 16):
        for _ in range(150):
            weights = [rng.randrange(6) for _ in range(count)]
            if not sum(weights):
                weights[0] = 1
            budget = rng.choice((F(0), F(1, 5), F(1, 2), F(9, 10), F(1)))
            excess = [budget*w/sum(weights) for w in weights]
            check_identity_scale(excess, rng.randrange(count))
            scale_cases += 1
        for truth in range(count):
            for exponent in (1, 5, 20, 100):
                epsilon = F(1, 2**exponent)
                for slack in (F(0), F(1, 2), F(1)):
                    excess = [epsilon*(1-slack)/(count-1)]*count
                    excess[truth] = 1-epsilon
                    check_identity_scale(excess, truth)
                    scale_cases += 1

    return {'status': 'PASS',
            'scope': 'full fixed-source static positive DAGs; scalar mass and minimum-cap identity conditionals',
            'generic_rational_source_DAGs': generic_graphs,
            'binary_unary_source_DAGs': binary_graphs,
            'full_domain_retained_monomial_checks': retained_checks,
            'checks_with_source_ratio_floor_below_one': nonunit_ratio_checks,
            'zero_PRODUCT_exhaustive_support_counts': sum_catalogues,
            'two_PRODUCT_support_border_passes_necessary_condition': True,
            'two_PRODUCT_parity_passes_necessary_condition_but_exact_proof_rejects_closure': True,
            'two_PRODUCT_four_source_monomial_counterexample_coefficient': 24,
            'exact_face_constructions': face_cases,
            'repeated_square_full_cube_cases': 7, 'selected_square_approximants': square_records,
            'identity_decoder_counts_and_margins': decoder_records,
            'arbitrary_multiclass_normalizer_and_surplus_checks': scale_cases,
            'not_claimed': ['short source intersections suffice for mass closure',
                            'every expanded monomial has at most P+1 distinct sources',
                            'dimension-independent positive approximation margin',
                            'sharp shared decoder counts for d>2',
                            'registered value/install/persistence or reference-AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_SOURCE_INTERSECTION_PRODUCT_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
