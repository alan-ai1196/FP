"""Complete unrestricted-node dyadic cap decisions and exact total-accuracy constructions."""
from fractions import Fraction as F
from functools import reduce
from itertools import product
from math import ceil, gcd, lcm
from pathlib import Path
import argparse
import copy
import json
import random

from conditional_coefficient_paths_audit import native_masses, normalize
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_product, add_sum, sources


ALPHABET = {F(1, 2), F(1), F(2)}


def dyadic(value):
    return value.denominator & (value.denominator-1) == 0


def validate(d, target, cap):
    if type(d) is not int or d < 1 or type(cap) not in (int, F):
        raise ValueError('positive binary dimension and exact rational cap required')
    if len(target) != 2**d or not target or len(target[0]) < 2:
        raise ValueError('complete binary domain and at least two labels required')
    k = len(target[0])
    if any(len(row) != k or any(type(v) not in (int, F) for v in row) for row in target):
        raise ValueError('complete exact rational probability rows required')
    target = tuple(tuple(map(F, row)) for row in target)
    if any(min(row) <= 0 or sum(row) != 1 for row in target):
        raise ValueError('strictly positive probability rows required')
    return target, F(cap)


def scope(d, k):
    return {'sources': 'complete binary unary indicators', 'd': d, 'labels': k,
            'base': 1, 'SUM_weights': ['1/2', '1', '2'], 'PRODUCTs': 'unrestricted finite',
            'SUMs': 'unrestricted finite', 'other_resource_or_Runtime_authority': False}


def primitive_row(row):
    denominator = lcm(*(v.denominator for v in row))
    integers = [int(v*denominator) for v in row]
    common = reduce(gcd, integers)
    return tuple(v//common for v in integers)


def dyadic_in_interval(lower, upper):
    if lower > upper or (lower == upper and not dyadic(lower)):
        raise ValueError('no dyadic scale in this interval')
    if dyadic(lower):
        return lower
    precision = 0
    while F(1, 2**precision) > upper-lower:
        precision += 1
    scale = F(ceil(lower*2**precision), 2**precision)
    assert lower <= scale <= upper and dyadic(scale)
    return scale


def classify(d, target, cap):
    """Exact decision only for unrestricted finite P,S; coefficients/data are explicit."""
    target, cap = validate(d, target, cap)
    k = len(target[0])
    integer_rows = [primitive_row(row) for row in target]
    row_caps = [F(sum(row), min(row)) for row in integer_rows]
    minimum = max(row_caps)
    critical = tuple(x for x, r in enumerate(row_caps) if r == cap)
    result = {'scope': scope(d, k), 'minimum_cap': minimum, 'critical_rows': critical}
    if cap < k:
        return dict(result, status='EMPTY_CLASS')
    if cap < minimum:
        x, j = min(product(range(len(target)), range(k)), key=lambda pair: target[pair[0]][pair[1]])
        return dict(result, status='OUTSIDE_CLOSURE', witness=(x, j), gap=1/cap-target[x][j])
    for x in critical:
        smallest = min(integer_rows[x])
        if smallest & (smallest-1):
            j = next(j for j, a in enumerate(integer_rows[x]) if not dyadic(F(a, smallest)))
            return dict(result, status='LIMIT_ONLY', witness=(x, j, F(integer_rows[x][j], smallest)))
    masses = []
    for row in integer_rows:
        scale = dyadic_in_interval(F(1, min(row)), cap/sum(row))
        masses.append(tuple(scale*a for a in row))
    return dict(result, status='EXACT_LOCAL', mass_rows=tuple(masses))


def verify_decision(d, target, cap, certificate, requested_scope=None):
    """Independent probability/base/forced-mass checks, without the primitive-integer test."""
    try:
        target, cap = validate(d, target, cap)
        expected = scope(d, len(target[0]))
        if certificate['scope'] != expected or (requested_scope is not None and requested_scope != expected):
            return False
        row_caps = [1/min(row) for row in target]
        if certificate['minimum_cap'] != max(row_caps) or certificate['critical_rows'] != tuple(
                x for x, r in enumerate(row_caps) if r == cap):
            return False
        status = certificate['status']
        if status == 'EMPTY_CLASS':
            return cap < len(target[0])
        if cap < len(target[0]):
            return False
        if status == 'OUTSIDE_CLOSURE':
            x, j = certificate['witness']
            if type(x) is not int or type(j) is not int or not 0 <= x < len(target) or not 0 <= j < len(target[0]):
                return False
            return certificate['gap'] == 1/cap-target[x][j] > 0
        if any(v < 1/cap for row in target for v in row):
            return False
        if status == 'LIMIT_ONLY':
            x, j, forced = certificate['witness']
            if type(x) is not int or type(j) is not int or not 0 <= x < len(target) or not 0 <= j < len(target[0]):
                return False
            return row_caps[x] == cap and forced == cap*target[x][j] and not dyadic(forced)
        if status == 'EXACT_LOCAL':
            masses = certificate['mass_rows']
            return (len(masses) == len(target) and all(len(row) == len(target[0]) for row in masses)
                    and all(type(v) in (int, F) and F(v) >= 1 and dyadic(F(v)) for row in masses for v in row)
                    and max(map(sum, masses)) <= cap and normalize(masses) == target)
        return False
    except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):
        return False


def singleton_bank(d):
    nodes = sources(d)
    level = [0, 1]
    for coordinate in range(1, d):
        level = [add_product(nodes, parent, 2*coordinate+bit) for parent in level for bit in (0, 1)]
    assert sum(n[0] == 'product' for n in nodes) == 2**(d+1)-4
    return nodes, level


def combine(nodes, terms):
    if len(terms) == 1 and terms[0][1] == 1:
        return terms[0][0]
    return add_sum(nodes, terms)


def exact_graph(d, mass_rows):
    if type(d) is not int or d < 1 or len(mass_rows) != 2**d or len(mass_rows[0]) < 2:
        raise ValueError('complete binary mass table required')
    if any(len(row) != len(mass_rows[0]) or any(type(v) not in (int, F) or v < 1 or not dyadic(F(v))
                                             for v in row) for row in mass_rows):
        raise ValueError('every mass must be dyadic and at least the fixed base one')
    nodes, indicators = singleton_bank(d)
    heads = []
    for column in zip(*mass_rows):
        terms = [(indicator, value-1) if value-1 in ALPHABET else (dyadic_scale(nodes, indicator, value-1), F(1))
                 for indicator, value in zip(indicators, column) if value > 1]
        heads.append(combine(nodes, terms))
    return nodes, heads


def approximate_graph(d, target, steps):
    if type(steps) is not int or steps < 1:
        raise ValueError('a positive integer geometric depth is required')
    target, _ = validate(d, target, 0)  # validate the table; this constructor makes no cap decision
    nodes, indicators = singleton_bank(d)
    masses = tuple(tuple(v/min(row) for v in row) for row in target)
    constants, one = {}, None
    heads = []
    for column in zip(*masses):
        terms = []
        for indicator, mass in zip(indicators, column):
            coefficient = mass-1
            if not coefficient:
                continue
            if dyadic(coefficient):
                terms.append((indicator, coefficient) if coefficient in ALPHABET
                             else (dyadic_scale(nodes, indicator, coefficient), F(1)))
                continue
            if coefficient not in constants:
                if one is None:
                    one = add_sum(nodes, ((0, F(1)), (1, F(1))))
                a, b = coefficient.numerator, coefficient.denominator
                denominator = 2**((b-1).bit_length())
                seed, tail = F(a, denominator), 1-F(b, denominator)
                assert 0 < tail < F(1, 2)
                g = dyadic_scale(nodes, one, seed)
                t = dyadic_scale(nodes, one, tail)
                for i in range(steps):
                    factor = add_sum(nodes, ((one, F(1, 2)), (t, F(1, 2))))
                    g = add_product(nodes, g, factor)
                    g = add_sum(nodes, ((g, F(2)),))
                    if i+1 < steps:
                        t = add_product(nodes, t, t)
                constants[coefficient] = (g, coefficient*(1-tail**(2**steps)))
            # A computed scalar is a graph value, so applying it costs a PRODUCT.
            terms.append((add_product(nodes, constants[coefficient][0], indicator), F(1)))
        heads.append(combine(nodes, terms))
    return nodes, heads, constants, masses


def check_native(d, nodes, heads, target, cap, exact=False):
    assert sum(n[0] == 'source' for n in nodes) == 2*d
    assert {a for n in nodes if n[0] == 'sum' for _, a in n[1]} <= ALPHABET
    values = evaluate_tables(nodes, binary_tables(d))
    masses = native_masses(nodes, heads, binary_tables(d))
    q = normalize(masses)
    assert max(map(sum, masses)) <= cap
    assert max(v for row in values for v in row) <= max(F(1), cap-len(heads))
    error = max(abs(a-b) for row, goal in zip(q, target) for a, b in zip(row, goal))
    if exact:
        assert error == 0
    return error, values, masses


def row_types(k, bound):
    return [tuple(F(v, sum(row)) for v in row) for row in product(range(1, bound+1), repeat=k)
            if reduce(gcd, row) == 1]


def audit():
    rng = random.Random(2026091202)
    statuses = {s: 0 for s in ('EMPTY_CLASS', 'OUTSIDE_CLOSURE', 'EXACT_LOCAL', 'LIMIT_ONLY')}
    target_cases, exact_graphs, limit_examples = 0, 0, []
    models = []
    for k, bound in ((2, 5), (3, 3)):
        for rows in product(row_types(k, bound), repeat=2):
            minimum = max(1/min(row) for row in rows)
            models.extend((1, rows, cap) for cap in (minimum-F(1, 4), minimum, minimum+F(1, 4)))
    for index in range(36):
        d, k = 2+index % 2, 2+index % 4
        raw = [[rng.randrange(1, 12) for _ in range(k)] for _ in range(2**d)]
        target = tuple(tuple(F(v, sum(row)) for v in row) for row in raw)
        minimum = max(1/min(row) for row in target)
        models.extend((d, target, cap) for cap in (minimum-F(1, 8), minimum, minimum+F(1, 8)))
    # A dyadic cap and one good critical row do not settle the other critical row.
    mixed = ((F(1, 4), F(3, 8), F(3, 8)), (F(1, 4), F(1, 3), F(5, 12)))
    models.append((1, mixed, F(4)))
    for d, target, cap in models:
        result = classify(d, target, cap)
        assert verify_decision(d, target, cap, result)
        k = len(target[0])
        # Independent direct forced-mass criterion; no gcd/minimum-integer shortcut.
        if cap < k:
            direct = 'EMPTY_CLASS'
        elif min(v for row in target for v in row) < 1/cap:
            direct = 'OUTSIDE_CLOSURE'
        elif any(not dyadic(cap*v) for row in target if min(row) == 1/cap for v in row):
            direct = 'LIMIT_ONLY'
        else:
            direct = 'EXACT_LOCAL'
        assert result['status'] == direct
        statuses[direct] += 1
        target_cases += 1
        if direct == 'EXACT_LOCAL':
            nodes, heads = exact_graph(d, result['mass_rows'])
            check_native(d, nodes, heads, target, cap, exact=True)
            exact_graphs += 1
        elif direct == 'LIMIT_ONLY' and (len(limit_examples) < 16 or d >= 2 or target == mixed):
            limit_examples.append((d, target, cap))

    # The complete unrestricted-node result does not answer P=9 for this target.
    identity = tuple(tuple(F(1+int(i == j), 9) for j in range(8)) for i in range(8))
    identity_result = classify(3, identity, F(9))
    assert identity_result['status'] == 'EXACT_LOCAL'
    nodes, heads = exact_graph(3, identity_result['mass_rows'])
    check_native(3, nodes, heads, identity, F(9), exact=True)
    assert sum(n[0] == 'product' for n in nodes) == 12 and sum(n[0] == 'sum' for n in nodes) == 0
    narrowed = dict(scope(3, 8), PRODUCTs=9)
    assert not verify_decision(3, identity, F(9), identity_result, requested_scope=narrowed)

    constructed, constant_checks, mixed_records = 0, 0, []
    for d, target, cap in limit_examples:
        first_cost = None
        for steps in (1, 2, 3, 5):
            nodes, heads, constants, ideal = approximate_graph(d, target, steps)
            error, values, masses = check_native(d, nodes, heads, target, cap)
            assert error > 0
            assert all(a <= b for row, old in zip(masses, ideal) for a, b in zip(row, old))
            for feature, value in constants.values():
                assert set(values[feature]) == {value}
                constant_checks += 1
            h = F(1, 2**(2**steps))
            assert error <= (cap-len(heads))*h/len(heads)
            sums, products = sum(n[0] == 'sum' for n in nodes), sum(n[0] == 'product' for n in nodes)
            cost = sums+products
            if first_cost is None:
                first_cost = cost
            assert cost == first_cost+4*len(constants)*(steps-1)
            assert sums*2**products <= 2**(cost-1)
            if target == mixed:
                mixed_records.append({'geometric_depth': steps, 'SUMs': sums, 'PRODUCTs': products,
                                      'total_nodes': cost, 'probability_error': str(error),
                                      'distinct_nondyadic_constants': len(constants)})
            constructed += 1

    certificate = classify(1, mixed, F(4))
    assert certificate['status'] == 'LIMIT_ONLY' and certificate['critical_rows'] == (0, 1)
    bad = copy.deepcopy(certificate)
    bad['critical_rows'] = (0,)
    assert not verify_decision(1, mixed, F(4), bad)
    bad = copy.deepcopy(certificate)
    x, j, value = bad['witness']
    bad['witness'] = (x, j, F(1))
    assert not verify_decision(1, mixed, F(4), bad)
    bad = copy.deepcopy(certificate)
    bad['witness'] = (x-len(mixed), j, value)
    assert not verify_decision(1, mixed, F(4), bad)
    bad = copy.deepcopy(certificate)
    bad['status'] = 'EXACT_LOCAL'
    bad['mass_rows'] = ((F(1), F(3, 2), F(3, 2)),)*2
    assert not verify_decision(1, mixed, F(4), bad)
    bad = copy.deepcopy(identity_result)
    bad['scope'] = narrowed
    assert not verify_decision(3, identity, F(9), bad)

    separate = ((F(3, 4), F(1, 4)), (F(3, 5), F(2, 5)))
    separate_result = classify(1, separate, F(4))
    assert verify_decision(1, separate, F(4), separate_result) and separate_result['status'] == 'EXACT_LOCAL'
    nodes, heads = exact_graph(1, separate_result['mass_rows'])
    _, _, masses = check_native(1, nodes, heads, separate, F(4), exact=True)
    assert tuple(map(sum, masses)) == (F(4), F(5, 2))
    assert any(not dyadic(4*v) for v in separate[1])
    assert sum(n[0] == 'product' for n in nodes) == 0 and sum(n[0] == 'sum' for n in nodes) == 2

    invalid = 0
    for d, target, cap in ((1, mixed[:1], F(4)), (1, ((F(0), F(1)),)*2, F(4)),
                           (1, ((F(1, 2), F(1, 4)),)*2, F(4)), (True, mixed, F(4)),
                           (1, mixed, float('nan')), (1, mixed, float('inf'))):
        try:
            classify(d, target, cap)
        except ValueError:
            invalid += 1
    assert invalid == 6
    invalid_masses = 0
    for bad in (((F(1, 2), F(1)),)*2, ((F(4, 3), F(1)),)*2):
        try:
            exact_graph(1, bad)
        except ValueError:
            invalid_masses += 1
    assert invalid_masses == 2
    return {'status': 'PASS', 'scope': scope('any fixed d>=1', 'any fixed k>=2'),
            'known_rational_table_cap_classifications': target_cases, 'classified_status_counts': statuses,
            'exact_full_native_graphs': exact_graphs, 'geometric_limit_graphs': constructed,
            'computed_constant_value_checks': constant_checks,
            'exact_branch_condition': 'R>=R0 and every critical forced mass R*Q is dyadic',
            'total_accuracy_order_on_limit_only_branch': 'Theta(log log(1/delta))',
            'actual_total_node_growth_for_each_constructed_family': 'C_n=C_1+4*m*(n-1), m distinct nondyadic constants',
            'mixed_critical_row_counterexample': {'cap': '4', 'forced_bad_mass_row': ['1', '4/3', '5/3'],
                                                 'finite_graphs': mixed_records},
            'identity_scope_counterexample': {'unrestricted_status': 'EXACT_LOCAL', 'exact_PRODUCTs': 12,
                                              'exact_SUMs': 0, 'P_9_scope_rejected': True},
            'retained_noncritical_normalizers': ['4', '5/2'],
            'forged_or_narrowed_certificates_rejected': 6, 'invalid_claim_inputs_rejected': invalid,
            'negative_excess_or_nondyadic_exact_construction_rejected': invalid_masses,
            'not_claimed': ['fixed-PRODUCT classification', 'minimum finite exact graph size in general',
                            'sharp SUM/PRODUCT Pareto constants', 'uniform small dependence on target dimension or encoding',
                            'registered target acquisition, value, ownership/install, persistence or AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_DYADIC_CAP_TOTAL_COMPLEXITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
