"""Exact conditional universality, cap-independent rank bounds, and a cap-108 decoder."""
from fractions import Fraction as F
from itertools import product
from math import lcm
from pathlib import Path
import argparse
import json
import random

from decoder_exact_limit_audit import build_exact_three_bit, predictions
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_support_border_audit import add_product, add_sum, sources


def monomial_bank(d):
    nodes = sources(d)
    features = [add_sum(nodes, ((0, 1), (1, 1)))]
    for subset in range(1, 2**d):
        bit = subset & -subset
        literal = 2*(d-bit.bit_length())+1
        if subset == bit:
            features.append(literal)
        else:
            features.append(add_product(nodes, features[subset ^ bit], literal))
    assert sum(node[0] == 'product' for node in nodes) == 2**d-d-1
    return nodes, features


def mobius(values):
    result = list(values)
    for bit in (1 << i for i in range((len(values)-1).bit_length())):
        for subset in range(len(values)):
            if subset & bit:
                result[subset] -= result[subset ^ bit]
    return tuple(result)


def native_from_masses(d, masses, integer_alphabet=False):
    """An exact constructor for this fixed feature cone, not the full FP class."""
    count = 2**d
    if len(masses) != count or not masses[0] or any(len(row) != len(masses[0]) for row in masses):
        raise ValueError('complete rectangular mass table required')
    nodes, features = monomial_bank(d)
    heads = []
    for label in range(len(masses[0])):
        coefficients = mobius([F(row[label])-1 for row in masses])
        if any(coefficients[subset] < 0 for subset in range(count) if subset.bit_count() >= 2):
            raise ValueError('outside the fixed monomial feature cone: negative higher coefficient')
        linear = [coefficients[1 << i] for i in range(d)]
        minimum = coefficients[0]+sum(min(F(0), value) for value in linear)
        if minimum < 0:
            raise ValueError('outside the fixed monomial feature cone: negative affine remainder')
        terms = [(features[0], minimum)]
        for i, value in enumerate(linear):
            coordinate = d-i-1
            terms.append((2*coordinate+(value >= 0), abs(value)))
        terms.extend((features[subset], coefficients[subset]) for subset in range(count) if subset.bit_count() >= 2)
        terms = [(feature, weight) for feature, weight in terms if weight]
        if integer_alphabet:
            if any(weight.denominator != 1 for _, weight in terms):
                raise ValueError('this integer-alphabet path requires integer readout coefficients')
            terms = [(dyadic_scale(nodes, feature, weight), F(1)) for feature, weight in terms]
        heads.append(add_sum(nodes, terms))
    assert sum(node[0] == 'product' for node in nodes) == count-d-1
    return nodes, heads, features


def positive_conditional_lift(d, target, integer_alphabet=False):
    target = tuple(tuple(map(F, row)) for row in target)
    if len(target) != 2**d or not target[0] or any(len(row) != len(target[0]) for row in target):
        raise ValueError('complete target table required')
    if any(min(row) <= 0 or sum(row) != 1 for row in target):
        raise ValueError('strictly positive normalized probabilities required')
    columns = list(zip(*target))
    ratio = max(max(column)/min(column) for column in columns)
    scale = max(1/value for value in target[0])
    growth = d*(1+ratio)
    if integer_alphabet:
        scale = F(lcm(*(value.denominator for row in target for value in row)))
        growth = F((growth.numerator+growth.denominator-1)//growth.denominator)
    masses = tuple(tuple(scale*growth**context.bit_count()*p for p in row) for context, row in enumerate(target))
    nodes, heads, features = native_from_masses(d, masses, integer_alphabet)
    return nodes, heads, features, masses, scale, growth


def row_reduce(matrix):
    result = [list(map(F, row)) for row in matrix]
    row, pivots = 0, []
    for column in range(len(result[0])):
        pivot = next((i for i in range(row, len(result)) if result[i][column]), None)
        if pivot is None:
            continue
        result[row], result[pivot] = result[pivot], result[row]
        value = result[row][column]
        result[row] = [entry/value for entry in result[row]]
        for i in range(len(result)):
            if i != row and result[i][column]:
                factor = result[i][column]
                result[i] = [a-factor*b for a, b in zip(result[i], result[row])]
        pivots.append(column)
        row += 1
        if row == len(result):
            break
    return result, pivots


def rank(matrix):
    return len(row_reduce(matrix)[1])


def left_null(matrix):
    reduced, pivots = row_reduce(list(zip(*matrix)))
    count = len(matrix)
    free = next(i for i in range(count) if i not in pivots)
    vector = [F(0)]*count
    vector[free] = 1
    for row, pivot in enumerate(pivots):
        vector[pivot] = -reduced[row][free]
    total = sum(abs(value) for value in vector)
    vector = tuple(value/total for value in vector)
    assert all(sum(vector[i]*matrix[i][j] for i in range(count)) == 0 for j in range(len(matrix[0])))
    return vector


def verify_fixed_bank_dual(weights):
    # Coordinates: (u0,u1,u2,u3,constant), with rows e0,ea,e2,e3.
    rows = ((1, 0, 0, 0, -1), (-4, 3, 0, 0, -1), (1, -3, 1, 0, 0), (-1, 3, -4, 1, 0))
    return len(weights) == 4 and min(weights) >= 0 and tuple(
        sum(weight*row[i] for weight, row in zip(weights, rows)) for i in range(5)) == (0, 0, 0, 1, -12)


def audit():
    rng = random.Random(2026091106)
    universal_cases, integer_cases, entries = 0, 0, 0
    selected = []
    for d in range(1, 5):
        count = 2**d
        for labels in (2, count, count+1):
            weights = [[rng.randrange(1, 10) for _ in range(labels)] for _ in range(count)]
            target = [tuple(F(value, sum(row)) for value in row) for row in weights]
            for integer_alphabet in ((False, True) if d <= 3 else (False,)):
                nodes, heads, features, masses, scale, growth = positive_conditional_lift(d, target, integer_alphabet)
                values = evaluate_tables(nodes, binary_tables(d))
                assert all(set(values[feature]) <= {F(0), F(1)} for feature in features)
                for context in range(count):
                    excess = [values[head][context] for head in heads]
                    assert tuple(1+value for value in excess) == masses[context]
                    q, normalizer = predictions(excess)
                    assert q == target[context] and normalizer == scale*growth**context.bit_count()
                    entries += labels
                if integer_alphabet:
                    assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} <= {F(1), F(2)}
                    integer_cases += 1
                universal_cases += 1
                if labels == count:
                    selected.append({'d': d, 'labels': labels, 'PRODUCTs': count-d-1,
                                     'integer_local_alphabet': integer_alphabet,
                                     'maximum_normalizer': str(scale*growth**d)})

    rank_cases, null_cases = 60, 0
    for _ in range(rank_cases):
        d = rng.randrange(2, 5)
        count = 2**d
        nodes = sources(d)
        products = rng.randrange(5)
        first_head = random_graph(rng, nodes, products)
        heads = [first_head]+[add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((F(1, 2), F(1), F(2))))
                                             for _ in range(5))) for _ in range(count-1)]
        values = evaluate_tables(nodes, binary_tables(d))
        masses = [[1+values[head][context] for head in heads] for context in range(count)]
        q = [[value/sum(row) for value in row] for row in masses]
        actual_rank = rank(masses)
        assert actual_rank == rank(q) <= d+1+products
        if actual_rank < count:
            w = left_null(q)
            assert sum(w) == 0 and sum(abs(v) for v in w) == 1
            target = [[F(1+(i == j), count+1) for j in range(count)] for i in range(count)]
            assert all(sum(w[i]*(target[i][j]-q[i][j]) for i in range(count)) == w[j]/(count+1)
                       for j in range(count))
            error = max(abs(target[i][j]-q[i][j]) for i in range(count) for j in range(count))
            assert error >= F(1, count*(count+1))
            null_cases += 1

    rank_equality_cases = 0
    for d in range(1, 6):
        count = 2**d
        signs = [1]*(count//2)+[-1]*(count//2)
        target = [[F(1+(i == j), count+1) for j in range(count)] for i in range(count)]
        q = [[target[i][j]-F(signs[i]*signs[j], count*(count+1)) for j in range(count)] for i in range(count)]
        assert all(min(row) > 0 and sum(row) == 1 for row in q)
        assert rank(q) == count-1
        assert max(abs(q[i][j]-target[i][j]) for i in range(count) for j in range(count)) == F(1, count*(count+1))
        rank_equality_cases += 1

    assert verify_fixed_bank_dual((9, 3, 4, 1))
    assert not verify_fixed_bank_dual((9, 2, 4, 1))
    assert not verify_fixed_bank_dual((9, 3, 4, -1))
    assert not verify_fixed_bank_dual((9, 3, 4))
    witness_records = []
    for multiplier, integer_alphabet in ((F(1), False), (F(3), True)):
        u = (F(1), F(5, 3), F(4), F(12))
        masses = [[multiplier*u[context.bit_count()]*(1+(context == label)) for label in range(8)] for context in range(8)]
        nodes, heads, features = native_from_masses(3, masses, integer_alphabet)
        values = evaluate_tables(nodes, binary_tables(3))
        normalizers = []
        for context in range(8):
            excess = [values[head][context] for head in heads]
            assert [1+v for v in excess] == masses[context]
            q, normalizer = predictions(excess)
            assert q == tuple(F(1+(i == context), 9) for i in range(8))
            normalizers.append(normalizer)
        assert max(normalizers) == 108*multiplier
        if integer_alphabet:
            assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} <= {F(1), F(2)}
        witness_records.append({'PRODUCTs': 4, 'maximum_normalizer': str(max(normalizers)),
                                'integer_local_alphabet': integer_alphabet,
                                'normalizers_by_context': list(map(str, normalizers)),
                                'maximum_excess_feature': str(max(max(table) for table in values))})

    # Check the fixed-bank certificate on feasible non-minimal scales as well.
    for _ in range(40):
        e0, ea, e2, e3 = [F(rng.randrange(10), rng.choice((2, 3, 5))) for _ in range(4)]
        u0 = 1+e0
        u1 = (4*u0+1+ea)/3
        u2 = 3*u1-u0+e2
        u3 = 4*u2-3*u1+u0+e3
        assert u3-12 == e3+4*e2+3*ea+9*e0 >= 0
        u = (u0, u1, u2, u3)
        masses = [[u[context.bit_count()]*(1+(context == label)) for label in range(8)] for context in range(8)]
        nodes, heads, _ = native_from_masses(3, masses)
        values = evaluate_tables(nodes, binary_tables(3))
        assert all(1+values[head][context] == masses[context][label]
                   for context in range(8) for label, head in enumerate(heads))

    invalid = 0
    for target in (((0, 1), (F(1, 2), F(1, 2))), ((F(1, 2), F(1, 3)), (F(1, 2), F(1, 2)))):
        try:
            positive_conditional_lift(1, target)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError('target outside positive normalized class accepted')
    # Rejection by the fixed four-monomial cone is not complete FP rejection.
    try:
        native_from_masses(3, [[F(1+(i == j)) for j in range(8)] for i in range(8)])
    except ValueError as error:
        assert 'fixed monomial feature cone' in str(error)
    else:
        raise AssertionError('cap-nine identity incorrectly accepted by four-monomial bank')
    nodes, heads = build_exact_three_bit()
    values = evaluate_tables(nodes, binary_tables(3))
    assert all(values[head][i] == (i == j) for j, head in enumerate(heads) for i in range(8))

    return {'status': 'PASS',
            'scope': 'full static unary-source conditional rank lower bound; fixed-bank exact constructions; no Runtime authority',
            'worst_case_exact_and_approximation_PRODUCT_count_unbounded_cap': '2^d-d-1 for d>=1; universality over finite output alphabets',
            'positive_target_graph_cases': universal_cases, 'integer_local_alphabet_cases': integer_cases,
            'individual_exact_mass_entries': entries, 'selected_universal_lifts': selected,
            'original_DAG_and_prediction_rank_checks': rank_cases, 'exact_left_null_witnesses': null_cases,
            'rank_relaxation_equality_cases': rank_equality_cases,
            'three_bit_probability_gap_for_PRODUCTs_at_most_three_at_any_cap': '1/72',
            'three_bit_CE_gap_for_PRODUCTs_at_most_three_at_any_cap': '1/20736',
            'exact_four_PRODUCT_identity_witnesses': witness_records,
            'fixed_four_monomial_bank_optimal_cap': '108',
            'fixed_bank_dual_multipliers_e0_ea_e2_e3': [9, 3, 4, 1],
            'fixed_bank_feasible_scale_checks': 40, 'forged_duals_rejected': 3,
            'invalid_probability_tables_rejected': invalid,
            'fixed_bank_rejection_with_full_FP_twelve_PRODUCT_witness': True,
            'not_claimed': ['108 is the minimum cap for the full variable-parent four-PRODUCT class',
                            'the rank relaxation witness is native PRODUCT optimal',
                            'universality at a fixed range or full physical budget',
                            'recurrent state dimension lower bounds',
                            'unknown target acquisition, registered value/install/persistence or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_CONDITIONAL_PRODUCT_UNIVERSALITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
