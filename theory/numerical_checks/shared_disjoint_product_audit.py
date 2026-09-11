"""Exact static comparison for disjoint heads and the four-PRODUCT parity boundary."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import random

from product_support_closure_audit import mass_margin, verified_parity_proof
from two_product_support_border_audit import (
    add_product, add_sum, cube, evaluate, sources,
)


def flatten_outputs(nodes, outputs):
    """Only SUM paths are flattened; every PRODUCT remains a separate feature."""
    flattened, products = [], []
    for index, node in enumerate(nodes):
        if node[0] == 'source':
            terms = {index: F(1)}
        elif node[0] == 'product':
            assert all(0 <= parent < index for parent in node[1:])
            products.append(index)
            terms = {index: F(1)}
        else:
            assert node[0] == 'sum'
            terms = {}
            for parent, weight in node[1]:
                assert 0 <= parent < index and weight >= 0
                for feature, coefficient in flattened[parent].items():
                    terms[feature] = terms.get(feature, F(0))+weight*coefficient
            terms = {feature: coefficient for feature, coefficient in terms.items() if coefficient}
        flattened.append(terms)
    return products, [flattened[index].copy() for index in outputs]


def distance(left, right):
    return max(abs(a-b) for a, b in zip(left, right))


def static_comparator(nodes, outputs, contexts, targets):
    """Construct a mathematical comparison graph, without Runtime authority."""
    count = len(outputs)
    if not count or len(targets) != count or not contexts:
        raise ValueError('nonempty matching outputs, targets and contexts required')
    if any(len(target) != len(contexts) or any(value < 0 for value in target) for target in targets):
        raise ValueError('nonnegative target tables on the complete domain required')
    if any(sum(target[x] > 0 for target in targets) > 1 for x in range(len(contexts))):
        raise ValueError('target positive supports must be pairwise disjoint')
    products, terms = flatten_outputs(nodes, outputs)
    if len(products) < count-1:
        raise ValueError('this comparison requires P >= k-1')
    tables = [evaluate(nodes, output, contexts)[0] for output in outputs]
    errors = [distance(table, target) for table, target in zip(tables, targets)]
    feature_tables = {feature: evaluate(nodes, feature, contexts)[0]
                      for feature in set().union(*(set(head) for head in terms))}

    def linear_table(head):
        return tuple(sum((coefficient*feature_tables[feature][x]
                          for feature, coefficient in head.items()), F(0))
                     for x in range(len(contexts)))

    assert [linear_table(head) for head in terms] == tables
    remaining = list(range(count))
    current = list(tables)
    discarded = []
    cut = len(nodes)
    for feature in reversed(products[len(products)-count+1:]):
        chosen = max(remaining, key=lambda i: terms[i].get(feature, F(0)))
        remaining.remove(chosen)
        discarded.append(chosen)
        for i in remaining:
            coefficient = terms[i].pop(feature, F(0))
            removed = tuple(coefficient*v for v in feature_tables.get(feature, (F(0),)*len(contexts)))
            for x, target in enumerate(targets[i]):
                if target > 0:
                    assert targets[chosen][x] == 0
                    assert 0 <= removed[x] <= current[chosen][x] <= tables[chosen][x] <= errors[chosen]
            updated = linear_table(terms[i])
            assert all(v == old-loss and 0 <= v <= original
                       for v, old, loss, original in zip(updated, current[i], removed, tables[i]))
            current[i] = updated
        cut = feature
    assert len(remaining) == 1
    survivor = remaining[0]
    prefix = nodes[:cut]
    output = add_sum(prefix, sorted(terms[survivor].items()))
    actual = evaluate(prefix, output, contexts)[0]
    assert actual == current[survivor]
    assert sum(node[0] == 'product' for node in prefix) == len(products)-count+1
    error = distance(actual, targets[survivor])
    assert error <= sum(errors)
    return {'survivor': survivor, 'discarded': discarded,
            'original_errors': errors, 'comparison_error': error,
            'comparison_PRODUCT_count': len(products)-count+1}


def parity_graph(cap=F(4)):
    assert cap > 2
    nodes = sources(3)
    e = add_product(nodes, add_sum(nodes, ((0, 1), (3, 1))),
                    add_sum(nodes, ((1, 1), (2, 1))))
    o = add_product(nodes, add_sum(nodes, ((0, 1), (2, 1))),
                    add_sum(nodes, ((1, 1), (3, 1))))
    even = add_product(nodes, add_sum(nodes, ((e, 1), (5, 1))),
                       add_sum(nodes, ((o, 1), (4, 1))))
    odd = add_product(nodes, add_sum(nodes, ((e, 1), (4, 1))),
                      add_sum(nodes, ((o, 1), (5, 1))))
    outputs = [add_sum(nodes, ((head, cap-2),)) for head in (even, odd)]
    return nodes, outputs


def audit():
    proof, record = verified_parity_proof()
    delta, counts, power = mass_margin(3, 2, 150, proof)
    assert delta == F(1, 18432) and counts == {'total': 156, 'pure': 48, 'bad': 108} and power == 2
    probability_gap = 2*delta/(4*5)
    loss_gap = probability_gap**2/4
    assert probability_gap == F(1, 184320) and loss_gap == F(1, 135895449600)

    rng = random.Random(2026091101)
    random_cases = 360
    empty_support_cases = 0
    for case in range(random_cases):
        d = rng.randrange(1, 5)
        contexts = cube(d)
        count = rng.randrange(1, 6)
        nodes = sources(d)
        for _ in range(count-1+rng.randrange(3)):
            left = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 3), 1, 3)))
                                   for _ in range(rng.randrange(1, 5))))
            right = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), 1, 2)))
                                    for _ in range(rng.randrange(1, 5))))
            add_product(nodes, left, left if rng.randrange(3) == 0 else right)
        outputs = [add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((0, F(1, 2), 1, 4)))
                                   for _ in range(rng.randrange(1, 6)))) for _ in range(count)]
        targets = [[F(0)]*len(contexts) for _ in range(count)]
        for x in range(len(contexts)):
            owner = rng.randrange(count+1)
            if owner < count:
                targets[owner][x] = rng.choice((F(1, 2), F(1), F(5, 2)))
        empty_support_cases += any(not any(target) for target in targets)
        static_comparator(nodes, outputs, contexts, targets)

    # Repeated squaring with unbounded features and compensating tiny readouts.
    large_cases = 0
    for exponent in (1, 16, 128, 1024):
        nodes = sources(1)
        feature = add_sum(nodes, ((0, 2**exponent),))
        for _ in range(3):
            feature = add_product(nodes, feature, feature)
        epsilon = F(1, 2**exponent)
        coefficient = F(1, 2**(8*exponent))
        first = add_sum(nodes, ((feature, coefficient),))
        second = add_sum(nodes, ((1, 1), (feature, epsilon*coefficient)))
        result = static_comparator(nodes, [first, second], cube(1), [(1, 0), (0, 1)])
        assert result['discarded'] == [0] and result['original_errors'] == [0, epsilon]
        assert result['comparison_error'] == 0
        assert evaluate(nodes, feature, cube(1))[1] == 2**(8*exponent)
        large_cases += 1

    # The two-head sum-of-errors constant is attained by this comparison.
    nodes = sources(1)
    constant = add_sum(nodes, ((0, 1), (1, 1)))
    feature = add_product(nodes, constant, constant)
    output = add_sum(nodes, ((feature, F(1, 2)),))
    result = static_comparator(nodes, [output, output], cube(1), [(1, 0), (0, 1)])
    assert result['original_errors'] == [F(1, 2), F(1, 2)]
    assert result['comparison_error'] == 1

    # Wrong choice of discarded head violates the total-original-error bound.
    nodes = sources(1)
    feature = add_product(nodes, 0, 0)
    epsilon = F(1, 1024)
    second = add_sum(nodes, ((1, 1), (feature, epsilon)))
    result = static_comparator(nodes, [feature, second], cube(1), [(1, 0), (0, 1)])
    assert result['discarded'] == [0] and sum(result['original_errors']) == epsilon
    wrong_comparison_error = distance((0, 0), (1, 0))
    assert wrong_comparison_error > sum(result['original_errors'])

    # Identical parity heads share the scalar three-PRODUCT exact witness.
    nodes, outputs = parity_graph()
    products, terms = flatten_outputs(nodes, outputs)
    even_product = products[2]
    duplicated_graph = nodes[:products[3]]
    duplicated = add_sum(duplicated_graph, ((even_product, 1),))
    even_target = tuple(F(sum(x) % 2 == 0) for x in cube(3))
    assert evaluate(duplicated_graph, duplicated, cube(3))[0] == even_target
    assert sum(node[0] == 'product' for node in duplicated_graph) == 3
    try:
        static_comparator(duplicated_graph, [duplicated, duplicated], cube(3), [even_target, even_target])
    except ValueError as error:
        assert 'disjoint' in str(error)
    else:
        raise AssertionError('overlapping targets accepted')

    # r>=1 is essential: disjoint unary outputs need no PRODUCTs.
    nodes = sources(3)
    assert [evaluate(nodes, head, cube(3))[0] for head in (0, 1)] == [
        tuple(F(x[0] == bit) for x in cube(3)) for bit in (0, 1)]
    assert not any(node[0] == 'product' for node in nodes)

    caps = (F(5, 2), F(3), F(4), F(5), F(8), F(17, 3))
    scale_cases, witness_cases = 0, 0
    for cap in caps:
        a = cap-2
        nodes, outputs = parity_graph(cap)
        heads = [evaluate(nodes, output, cube(3))[0] for output in outputs]
        assert sum(node[0] == 'product' for node in nodes) == 4
        for x, values in zip(cube(3), zip(*heads)):
            assert values == tuple(a*F(sum(x) % 2 == i) for i in (0, 1))
            assert sum(values)+2 == cap
            assert tuple((1+v)/cap for v in values) == tuple(
                1-1/cap if sum(x) % 2 == i else 1/cap for i in (0, 1))
        witness_cases += 1
        predictions = [1/cap+F(i, 16)*(1-2/cap) for i in range(17)]
        predictions.extend(1/cap+(1-2/cap)/2**k for k in (20, 100))
        predictions.extend(1-1/cap-(1-2/cap)/2**k for k in (20, 100))
        for q in predictions:
            lower = max(1/q, 1/(1-q))
            for normalizer in (lower, (lower+cap)/2, cap):
                excess = (normalizer*(1-q)-1, normalizer*q-1)
                assert min(excess) >= 0 and sum(excess)+2 <= cap
                for truth in (0, 1):
                    target_q = 1-1/cap if truth else 1/cap
                    error = abs(q-target_q)
                    assert 0 <= excess[truth] <= a
                    assert excess[truth] >= a-cap**2*error/(1+cap*error)
                    assert excess[1-truth] <= cap*error
                    for discarded in (0, 1):
                        survivor = 1-discarded
                        for ratio in (F(0), F(1, 3), F(1)):
                            largest_h = min(excess[discarded], excess[survivor]/ratio) if ratio else excess[discarded]
                            for fraction in (F(0), F(1, 2), F(1)):
                                h = fraction*largest_h
                                comparison = excess[survivor]-ratio*h
                                target = a if survivor == truth else F(0)
                                assert comparison >= 0
                                assert abs(comparison-target) <= cap*(cap+1)*error
                                scale_cases += 1

    return {'status': 'PASS',
            'scope': 'static positive scalar DAGs, disjoint excess outputs; no Runtime completion authority',
            'scalar_parity_proof_reverified_without_LP': True,
            'scalar_parity_proof_unique_nodes': len(record['packed_proof']['nodes']),
            'scalar_two_PRODUCT_parity_margin': str(delta),
            'random_shared_nested_DAG_comparisons': random_cases,
            'random_cases_including_empty_target_supports': empty_support_cases,
            'unbounded_hidden_feature_and_tiny_readout_cases': large_cases,
            'largest_hidden_feature': '2^8192',
            'two_head_error_sum_bound_saturation': True,
            'wrong_head_choice_counterexample': {'original_total_error': str(epsilon), 'wrong_comparison_error': 1},
            'overlapping_parity_heads_exact_PRODUCT_count': 3,
            'overlapping_target_premise_rejected': True,
            'zero_PRODUCT_disjoint_unary_witness_checked': True,
            'exact_four_PRODUCT_parity_witnesses': witness_cases,
            'arbitrary_normalizer_and_shared_contribution_comparisons': scale_cases,
            'parity_noise_one_quarter_cap_four': {
                'exact_and_approximation_PRODUCT_minimum': 4,
                'at_most_three_PRODUCT_probability_margin': str(probability_gap),
                'at_most_three_PRODUCT_CE_gap_nats': str(loss_gap)},
            'not_claimed': ['sharp loss constants', 'same lower bound at larger caps',
                            'recurrent physical PRODUCT counts',
                            'registered value/install/persistence or reference-AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_SHARED_DISJOINT_PRODUCT_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
