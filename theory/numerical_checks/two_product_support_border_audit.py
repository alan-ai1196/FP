"""Shared-DAG zero faces and a two-PRODUCT limit with exact support minimum three."""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import random


def cube(d):
    return tuple(product((0, 1), repeat=d))


VERTICES = cube(4)
TARGET = tuple((1-x)*y*z+x*(1-z)*w for x, y, z, w in VERTICES)


def sources(d):
    return [('source', i, bit) for i in range(d) for bit in (0, 1)]


def add_sum(nodes, terms):
    index = len(nodes)
    nodes.append(('sum', tuple((p, F(w)) for p, w in terms)))
    return index


def add_product(nodes, left, right):
    index = len(nodes)
    nodes.append(('product', left, right))
    return index


def evaluate(nodes, output, contexts, cast=F):
    table, peak = [], cast(0)
    for x in contexts:
        values = []
        for index, node in enumerate(nodes):
            if node[0] == 'source':
                value = cast(int(x[node[1]] == node[2]))
            elif node[0] == 'product':
                assert 0 <= node[1] < index and 0 <= node[2] < index
                value = values[node[1]]*values[node[2]]
            else:
                value = cast(0)
                for parent, weight in node[1]:
                    assert 0 <= parent < index and weight >= 0
                    # Registered audit order: scalar left-to-right SUM.
                    value = value+(cast(weight.numerator)/cast(weight.denominator))*values[parent]
            values.append(value)
            peak = max(peak, value)
        table.append(values[output])
    return tuple(table), peak


def faces(d):
    contexts = cube(d)
    return [(pattern, frozenset(i for i, x in enumerate(contexts)
                               if all(a == -1 or a == b for a, b in zip(pattern, x))))
            for pattern in product((-1, 0, 1), repeat=d)]


def zero_cover(nodes, output, d):
    """One global parent choice per PRODUCT, including repeated shared nodes."""
    contexts = cube(d)
    universe = frozenset(range(len(contexts)))
    products = [i for i, node in enumerate(nodes) if node[0] == 'product']
    result = set()
    for bits in product((1, 2), repeat=len(products)):
        choice = dict(zip(products, bits))
        sets = []
        for i, node in enumerate(nodes):
            if node[0] == 'source':
                value = frozenset(k for k, x in enumerate(contexts) if x[node[1]] != node[2])
            elif node[0] == 'sum':
                value = universe
                for parent, weight in node[1]:
                    if weight:
                        value = value & sets[parent]
            else:
                value = sets[node[choice[i]]]
            sets.append(value)
        result.add(sets[output])
    return result


def verify_packing(table, witnesses):
    """Each pair's coordinate hull must contain an externally positive point."""
    d = (len(table)-1).bit_length()
    contexts = cube(d)
    if len(table) != 2**d or len(set(witnesses)) != len(witnesses):
        return False
    if not all(x in contexts and table[contexts.index(x)] == 0 for x in witnesses):
        return False
    for a, b in combinations(witnesses, 2):
        if not any(value > 0 and all(ai != bi or xi == ai for ai, bi, xi in zip(a, b, x))
                   for x, value in zip(contexts, table)):
            return False
    return True


def verify_three_required(table, witnesses):
    """Support-only two-PRODUCT exclusion via the normal-form proof."""
    if len(table) != 16 or any(type(v) not in (int, F) or v < 0 for v in table):
        return False
    support = frozenset(i for i, value in enumerate(table) if value > 0)
    # Any compatible pair of unary literals is a face fixing <=2 coordinates.
    if not support or any(face <= support for pattern, face in faces(4)
                          if sum(v != -1 for v in pattern) <= 2):
        return False
    return len(witnesses) >= 4 and verify_packing(table, witnesses)


def build_limit(k):
    assert type(k) is int and k >= 1
    nodes = sources(4)
    tails = []
    for source, steps in ((3, 3*k), (4, 2*k), (7, k)):
        current = source
        for _ in range(steps):
            current = add_sum(nodes, ((current, F(1, 2)),))
        tails.append(current)
    left = add_sum(nodes, ((1, 1), (tails[0], 1)))
    middle = add_sum(nodes, ((0, 1), (tails[1], 1)))
    right = add_sum(nodes, ((5, 1), (tails[2], 1)))
    current = add_product(nodes, left, middle)
    current = add_product(nodes, current, right)
    for _ in range(3*k):
        current = add_sum(nodes, ((current, 2),))
    geometric = []
    for _ in range(k):
        current = add_sum(nodes, ((current, F(1, 2)),))
        geometric.append((current, 1))
    output = add_sum(nodes, geometric)
    assert sum(node[0] == 'sum' for node in nodes) == 10*k+4
    assert sum(node[0] == 'product' for node in nodes) == 2
    assert {w for node in nodes if node[0] == 'sum' for _, w in node[1]} == {F(1, 2), F(1), F(2)}
    return nodes, output


def build_exact():
    nodes = sources(4)
    a = add_product(nodes, 0, 3)
    b = add_product(nodes, 1, 7)
    left = add_sum(nodes, ((a, 1), (4, 1)))
    right = add_sum(nodes, ((b, 1), (5, 1)))
    output = add_product(nodes, left, right)
    return nodes, output


def positive_value_bound(nodes, output, contexts):
    weights = [w for node in nodes if node[0] == 'sum' for _, w in node[1] if w]
    mu = min([F(1), *weights])
    count_s = sum(node[0] == 'sum' for node in nodes)
    count_p = sum(node[0] == 'product' for node in nodes)
    exponent = count_s*2**count_p
    tau = mu**exponent
    table, _ = evaluate(nodes, output, contexts)
    assert all(value == 0 or value >= tau for value in table)
    return tau


def audit():
    import numpy as np
    zeros = frozenset(i for i, v in enumerate(TARGET) if not v)
    support = frozenset(range(16))-zeros
    all_faces = faces(4)
    assert len(all_faces) == 81
    assert sorted(len(face) for _, face in all_faces if face <= support) == [1, 1, 1, 1, 2, 2]
    witnesses = ((0, 0, 1, 0), (0, 1, 0, 1), (1, 1, 0, 0), (1, 1, 1, 1))
    assert verify_three_required(TARGET, witnesses)
    zero_faces = [face for _, face in all_faces if face <= zeros]
    assert not any(set().union(*chosen) == zeros for chosen in combinations(zero_faces, 3))
    assert any(set().union(*chosen) == zeros for chosen in combinations(zero_faces, 4))
    nodes, output = build_exact()
    assert evaluate(nodes, output, VERTICES)[0] == TARGET
    assert sum(node[0] == 'product' for node in nodes) == 3

    # The generic exact face bound is sharp for independent XOR sums.
    for m in range(1, 6):
        contexts = cube(2*m)
        nodes = sources(2*m)
        products = []
        for i in range(m):
            left = add_sum(nodes, ((4*i+1, 1), (4*i+3, 1)))
            right = add_sum(nodes, ((4*i, 1), (4*i+2, 1)))
            products.append(add_product(nodes, left, right))
        output = add_sum(nodes, ((p, 1) for p in products))
        table, _ = evaluate(nodes, output, contexts)
        assert table == tuple(F(sum(x[2*i] != x[2*i+1] for i in range(m))) for x in contexts)
        zero_indices = frozenset(i for i, value in enumerate(table) if not value)
        cover = zero_cover(nodes, output, 2*m)
        assert len(zero_indices) == 2**m and len(cover) == 2**m
        assert all(len(face) == 1 for face in cover) and set().union(*cover) == zero_indices

    records, rounded_equal = [], []
    target_prob = tuple(F(1+v, 2+v) for v in TARGET)
    for k in (*range(1, 9), 16, 32, 54, 100):
        epsilon = F(1, 2**k)
        nodes, output = build_limit(k)
        table, peak = evaluate(nodes, output, VERTICES)
        formula = []
        for x, y, z, w in VERTICES:
            f = (1-x)*y*z+x*(1-z)*w
            raw = (x+epsilon**3*y)*((1-x)+epsilon**2*(1-z))*(z+epsilon*w)/epsilon**3
            assert raw == f+epsilon*(1-x)*y*w+epsilon**3*y*(1-z)*w
            formula.append((1-epsilon)*raw)
        assert table == tuple(formula) and peak <= 2 and max(table) <= 1
        assert max(abs(v-f) for v, f in zip(table, TARGET)) == epsilon
        assert frozenset(i for i, v in enumerate(table) if v > 0) == support | {5}
        q = tuple((1+v)/(2+v) for v in table)
        for prediction, target, f in zip(q, target_prob, TARGET):
            assert F(1, 2) <= prediction <= F(2, 3)
            assert abs(prediction-target) <= epsilon/(6 if f else 4)
        chi_square = sum((p-v)**2/(v*(1-v)) for p, v in zip(target_prob, q))/16
        assert 0 < chi_square <= 25*epsilon**2/512
        cover = zero_cover(nodes, output, 4)
        assert len(cover) <= 4 and set().union(*cover) == frozenset(i for i, v in enumerate(table) if not v)
        rounded, _ = evaluate(nodes, output, VERTICES, np.float64)
        prediction = tuple((np.float64(1)+v)/(np.float64(2)+v) for v in rounded)
        equal = prediction == tuple(np.float64(1+v)/np.float64(2+v) for v in TARGET)
        if equal:
            assert rounded[5] > 0 and table[5] > 0 and q != target_prob
            rounded_equal.append(k)
        if k in (1, 3, 8, 54, 100):
            records.append({'k': k, 'SUM_nodes': 10*k+4, 'PRODUCT_nodes': 2,
                            'mass_sup_error': f'2^-{k}',
                            'float64_normalized_table_equals_target': equal,
                            'float64_excess_leakage_is_positive': bool(rounded[5] > 0)})
    assert 54 in rounded_equal and 100 in rounded_equal

    rng = random.Random(20260911)
    random_graphs = 300
    admissible_faces = {face for _, face in faces(4)} | {frozenset()}
    for _ in range(random_graphs):
        nodes = sources(4)
        for j in range(rng.randrange(1, 5)):
            left = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), 1, 2)))
                                   for _ in range(rng.randrange(1, 5))))
            right = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), 1, 2)))
                                    for _ in range(rng.randrange(1, 5))))
            add_product(nodes, left, left if rng.randrange(3) == 0 else right)
        output = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), 1, 2)))
                                 for _ in range(4)))
        table, _ = evaluate(nodes, output, VERTICES)
        cover = zero_cover(nodes, output, 4)
        assert cover <= admissible_faces
        assert set().union(*cover) == frozenset(i for i, value in enumerate(table) if not value)
        assert len(cover) <= 2**sum(node[0] == 'product' for node in nodes)
        positive_value_bound(nodes, output, VERTICES)

    # Repeated squaring proves that sharing can require the 2^P exponent.
    for count in range(1, 7):
        nodes = sources(1)
        output = add_sum(nodes, ((1, F(1, 2)),))
        for _ in range(count):
            output = add_product(nodes, output, output)
        tau = positive_value_bound(nodes, output, cube(1))
        assert evaluate(nodes, output, cube(1))[0] == (F(0), tau)
        assert tau == F(1, 2)**(2**count)

    forgeries = []
    forgeries.append(verify_three_required(TARGET, witnesses[:3]))
    forgeries.append(verify_three_required(TARGET, (*witnesses[:3], witnesses[0])))
    changed = list(TARGET)
    changed[VERTICES.index(witnesses[0])] = 1
    forgeries.append(verify_three_required(changed, witnesses))
    # A genuine one-PRODUCT support must not pass the pure-face premise.
    easy = tuple((x+y)*((1-x)+(1-y)) for x, y, z, w in VERTICES)
    forgeries.append(verify_three_required(easy, witnesses))
    assert not any(forgeries)

    return {'status': 'PASS',
            'scope': 'full scalar unary-source SUM/PRODUCT DAGs on the binary cube; exact real arithmetic',
            'target_mass': TARGET, 'exact_support_and_mass_PRODUCT_minimum': 3,
            'limiting_family_PRODUCT_count': 2,
            'zero_face_cover_minimum': 4,
            'coordinate_faces_checked': 81, 'packing_witnesses': witnesses,
            'packing_pairs_checked': 6, 'sharp_disjoint_XOR_cases': 5,
            'actual_finite_alphabet_graph_cases': 12, 'selected_families': records,
            'exact_leakage_at_0101_formula': '(1-2^-k)(2^-k+2^(-3k))',
            'CE_excess_upper_bound_formula': '25*2^(-2k)/512',
            'local_coefficient_alphabet': ['1/2', '1', '2'],
            'activation_cap': 2, 'binary_normalizer_cap': 3,
            'random_shared_DAG_face_and_positive_value_checks': random_graphs,
            'repeated_squaring_bound_saturation_cases': 6,
            'forged_support_certificates_rejected': len(forgeries),
            'not_claimed': ['mass limits preserve the attainable exact support patterns at fixed PRODUCT count',
                            'exact minimum three for the unrestricted conditional target',
                            'general m-XOR approximation lower bound without full resource assumptions',
                            'free erasure of positive leakage', 'registered value/install/persistence or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_TWO_PRODUCT_SUPPORT_BORDER_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
