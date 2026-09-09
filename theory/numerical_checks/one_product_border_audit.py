"""Exact two-PRODUCT necessity, one-PRODUCT approximation and float64 false exactness."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json


VERTICES = tuple(product((0, 1), repeat=3))
SELECTOR = tuple(int(z == 0) if x == 0 else int(w == 0) for x, z, w in VERTICES)


def build(k):
    assert type(k) is int and k >= 1
    nodes = [('source', axis, bit) for axis in range(3) for bit in (0, 1)]
    def linear(terms):
        index = len(nodes)
        nodes.append(('sum', tuple(terms)))
        return index
    tails = []
    for source in (4, 2):  # w_0 and z_0, respectively.
        current = source
        for _ in range(k):
            current = linear(((current, F(1, 2)),))
        tails.append(current)
    left = linear(((0, F(1)), (tails[0], F(1))))
    right = linear(((1, F(1)), (tails[1], F(1))))
    current = len(nodes)
    nodes.append(('product', left, right))
    for _ in range(k):
        current = linear(((current, F(2)),))
    terms = []
    for _ in range(k):
        current = linear(((current, F(1, 2)),))
        terms.append((current, F(1)))
    output = linear(terms)
    assert sum(node[0] == 'sum' for node in nodes) == 4*k+3
    assert sum(node[0] == 'product' for node in nodes) == 1
    assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} == {F(1, 2), F(1), F(2)}
    return tuple(nodes), output


def evaluate(nodes, output, cast):
    table = []
    peak = cast(0)
    for context in VERTICES:
        values = []
        for node in nodes:
            if node[0] == 'source':
                value = cast(int(context[node[1]] == node[2]))
            elif node[0] == 'product':
                value = values[node[1]]*values[node[2]]
            else:
                value = cast(0)
                # Declared left-to-right scalar accumulation, no reassociation.
                for parent, weight in node[1]:
                    coefficient = cast(weight.numerator)/cast(weight.denominator)
                    value = value+coefficient*values[parent]
            values.append(value)
            peak = max(peak, value)
        table.append(values[output])
    return tuple(table), peak


def likelihood(probabilities):
    result = F(1)
    for selector, q in zip(SELECTOR, probabilities):
        count1 = 4 if selector else 3
        result *= q**count1*(1-q)**(6-count1)
    return result


def audit():
    import numpy as np
    from sympy import Matrix
    target = tuple(F(1+v, 2+v) for v in SELECTOR)
    zero_set = frozenset(i for i, v in enumerate(SELECTOR) if not v)
    faces = {frozenset(): 'empty'}
    for pattern in product((-1, 0, 1), repeat=3):
        face = frozenset(i for i, x in enumerate(VERTICES)
                         if all(a == -1 or a == b for a, b in zip(pattern, x)))
        if face <= zero_set:
            faces[face] = pattern
    covers = [(a, b) for i, a in enumerate(faces) for b in tuple(faces)[i:] if a | b == zero_set]
    assert len(covers) == 1
    assert {faces[mask] for mask in covers[0]} == {(0, 1, -1), (1, -1, 1)}
    for axis, bit in product(range(3), (0, 1)):
        assert any(x[axis] == bit and f == 0 for x, f in zip(VERTICES, SELECTOR))
        assert any(x[axis] == bit and f == 1 for x, f in zip(VERTICES, SELECTOR))
    positive_points = [x for x, f in zip(VERTICES, SELECTOR) if f]
    assert Matrix([[1, *x] for x in positive_points]).det() != 0
    # Exact support is feasible with one PRODUCT, yet its values overcount.
    support_only = tuple((x+(1-z))*((1-x)+(1-w)) for x, z, w in VERTICES)
    assert tuple(int(v > 0) for v in support_only) == SELECTOR and support_only != SELECTOR
    assert max(support_only) == 2

    # A complete affine-threshold obstruction for every SUM model.
    positive_pair = ((0, 0, 1), (1, 1, 0))
    negative_pair = ((0, 1, 0), (1, 0, 1))
    assert tuple(sum(x[i] for x in positive_pair) for i in range(3)) == tuple(sum(x[i] for x in negative_pair) for i in range(3))
    constant = F(7, 12)
    assert max(abs(q-constant) for q in target) == F(1, 12)
    assert F(7, 5)/(1+F(7, 5)) == constant and 1+F(7, 5) <= 3
    sum_ce_gap = F(2, 8)*F(1, 12)**2
    assert sum_ce_gap == F(1, 576)

    bayes_likelihood = likelihood(target)
    records = []
    rounded_exact_cases = []
    for k in (*range(1, 9), 16, 32, 54, 100):
        nodes, output = build(k)
        exact, exact_peak = evaluate(nodes, output, F)
        epsilon = F(1, 2**k)
        formula = tuple((1-epsilon)*(f+epsilon*int(z == 0 and w == 0))
                        for (x, z, w), f in zip(VERTICES, SELECTOR))
        assert exact == formula and exact_peak <= 2
        assert max(exact) < 1 and tuple(int(v > 0) for v in exact) == SELECTOR
        prediction = tuple((1+v)/(2+v) for v in exact)
        error = max(abs(p-q) for p, q in zip(target, prediction))
        assert error == epsilon/(3*(3-epsilon)) <= epsilon/6
        assert likelihood(prediction) < bayes_likelihood
        chi_squared_upper = sum((p-q)**2/(q*(1-q)) for p, q in zip(target, prediction))/8
        assert chi_squared_upper <= epsilon*epsilon/16
        rounded, rounded_peak = evaluate(nodes, output, np.float64)
        assert rounded_peak <= 2 and max(rounded) <= 1
        appears_exact = rounded == tuple(np.float64(v) for v in SELECTOR)
        if appears_exact:
            assert exact != tuple(F(v) for v in SELECTOR)
            rounded_exact_cases.append(k)
        if k in (1, 3, 8, 54, 100):
            records.append({'k': k, 'SUM_nodes': 4*k+3, 'PRODUCT_nodes': 1,
                            'exact_probability_sup_error': str(error),
                            'proved_CE_excess_upper': str(epsilon*epsilon/16),
                            'strict_Bayes_likelihood_deficit_exact': True,
                            'float64_excess_table_appears_exact': appears_exact})
    assert 54 in rounded_exact_cases and 100 in rounded_exact_cases
    assert F(1, 2**6)/16 < sum_ce_gap  # k=3 beats every SUM by a proved margin.
    return {'status': 'PASS', 'scope': 'three binary unary sources, scalar SUM/PRODUCT, fixed base (1,1), final cap three',
            'target_selector_table': SELECTOR,
            'target_probabilities': [str(q) for q in target],
            'unique_parent_zero_face_cover': [list(faces[mask]) for mask in covers[0]],
            'positive_target_contexts_affinely_span': True,
            'support_only_one_PRODUCT_witness_overcounts': True,
            'proved_exact_conditional_PRODUCT_minimum': 2,
            'one_PRODUCT_Bayes_loss_infimum_attained': False,
            'full_SUM_supnorm_distance': '1/12',
            'full_SUM_CE_gap_lower': str(sum_ce_gap),
            'local_coefficient_alphabet': ['1/2', '1', '2'],
            'source_and_feature_activation_cap': 2,
            'final_normalizer_cap': 3,
            'native_DAG_cases_checked': 12,
            'selected_finite_witnesses': records,
            'float64_false_exact_mass_cases': rounded_exact_cases,
            'not_claimed': ['positive loss gap between one and two PRODUCTs',
                            'bounded complete construction resources',
                            'rounded equality proves real-arithmetic exactness',
                            'fixed-atom cone closure counterexample',
                            'registered value/install or AMP certification']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_ONE_PRODUCT_BORDER_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
