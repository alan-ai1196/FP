"""Exact native conditional paths, cap correction, and local-alphabet density witnesses."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from conditional_product_universality_audit import mobius
from frozen_feature_universality_audit import decide_universality, shifted_bank
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_support_border_audit import add_product, add_sum, sources


SCOPE = ('finite known nonnegative sources, scalar positive SUM/binary PRODUCT DAGs, '
         'base one per label, one final normalization; rational path verification, '
         'not generic phase/amplitude search or Runtime authority')


def exact(value):
    if type(value) not in (int, F):
        raise ValueError('this audit requires explicit exact rational inputs')
    return F(value)


def path_sum(nodes, terms):
    nodes.append(('sum', tuple(terms)))  # parent, positive amplitude, integer exponent
    return len(nodes)-1


def validate_path(nodes, heads, source_values):
    if not source_values or not heads or not next(iter(source_values.values())):
        raise ValueError('nonempty complete source domain and output heads required')
    width = len(next(iter(source_values.values())))
    if any(type(h) is not int or not 0 <= h < len(nodes) for h in heads):
        raise ValueError('invalid head')
    for i, node in enumerate(nodes):
        if node[0] == 'source':
            if i not in source_values or len(source_values[i]) != width or any(exact(v) < 0 for v in source_values[i]):
                raise ValueError('complete finite nonnegative source table required')
        elif node[0] == 'product':
            if len(node) != 3 or any(type(p) is not int or not 0 <= p < i for p in node[1:]):
                raise ValueError('invalid binary PRODUCT')
        elif node[0] == 'sum':
            for p, a, w in node[1]:
                if type(p) is not int or not 0 <= p < i or exact(a) < 0 or type(w) is not int:
                    raise ValueError('nonnegative rational amplitude and integer exponent required')
        else:
            raise ValueError('unsupported node')


def materialize(nodes, epsilon):
    epsilon = exact(epsilon)
    if epsilon <= 0:
        raise ValueError('a finite positive path parameter is required')
    return [('sum', tuple((p, F(a)*epsilon**w) for p, a, w in node[1]))
            if node[0] == 'sum' else node for node in nodes]


def leading_sum(terms):
    terms = [term for term in terms if term is not None]
    if not terms:
        return None
    order = min(w for w, a in terms)
    return order, sum((a for w, a in terms if w == order), F(0))


def leading_tables(nodes, source_values):
    """Only leading orders/amplitudes, without a polynomial expansion."""
    width, values = len(next(iter(source_values.values()))), []
    for i, node in enumerate(nodes):
        if node[0] == 'source':
            row = [(0, F(v)) if v else None for v in source_values[i]]
        elif node[0] == 'product':
            row = [(u[0]+v[0], u[1]*v[1]) if u is not None and v is not None else None
                   for u, v in zip(values[node[1]], values[node[2]])]
        else:
            row = [leading_sum((values[p][x][0]+w, values[p][x][1]*a)
                               for p, a, w in node[1] if a and values[p][x] is not None)
                   for x in range(width)]
        values.append(row)
    return values


def mass_polynomials(nodes, heads, source_values):
    """Independently expand every node into a full univariate Laurent polynomial."""
    width, values = len(next(iter(source_values.values()))), []
    for i, node in enumerate(nodes):
        row = []
        for x in range(width):
            polynomial = {}
            if node[0] == 'source':
                if source_values[i][x]:
                    polynomial[0] = F(source_values[i][x])
            elif node[0] == 'product':
                for u, a in values[node[1]][x].items():
                    for v, b in values[node[2]][x].items():
                        polynomial[u+v] = polynomial.get(u+v, F(0))+a*b
            else:
                for p, a, w in node[1]:
                    if a:
                        for v, b in values[p][x].items():
                            polynomial[v+w] = polynomial.get(v+w, F(0))+a*b
            row.append(polynomial)
        values.append(row)
    masses = [[dict(values[h][x]) for h in heads] for x in range(width)]
    for row in masses:
        for polynomial in row:
            polynomial[0] = polynomial.get(0, F(0))+1
    return masses


def leading_prediction(nodes, heads, source_values):
    validate_path(nodes, heads, source_values)
    values = leading_tables(nodes, source_values)
    orders, leading, probabilities = [], [], []
    for x in range(len(next(iter(source_values.values())))):
        mass = [leading_sum(((0, F(1)), values[h][x])) for h in heads]
        order = min(w for w, a in mass)
        row = tuple(a if w == order else F(0) for w, a in mass)
        orders.append(order)
        leading.append(row)
        probabilities.append(tuple(a/sum(row) for a in row))
    return tuple(orders), tuple(leading), tuple(probabilities)


def verify_prediction(nodes, heads, source_values, target):
    _, _, actual = leading_prediction(nodes, heads, source_values)
    return actual == tuple(tuple(exact(v) for v in row) for row in target)


def native_masses(nodes, heads, source_values):
    values = evaluate_tables(nodes, source_values)
    return tuple(tuple(1+values[h][x] for h in heads)
                 for x in range(len(next(iter(source_values.values())))))


def normalize(masses):
    return tuple(tuple(v/sum(row) for v in row) for row in masses)


def check_path(nodes, heads, source_values, epsilons):
    orders, leading, target = leading_prediction(nodes, heads, source_values)
    polynomials = mass_polynomials(nodes, heads, source_values)
    tails = []
    for x, row in enumerate(polynomials):
        assert min(w for poly in row for w in poly) == orders[x] <= 0
        assert tuple(poly.get(orders[x], F(0)) for poly in row) == leading[x]
        tails.append(sum(a for poly in row for w, a in poly.items() if w > orders[x]))
    for epsilon in epsilons:
        assert 0 < epsilon <= 1
        masses = native_masses(materialize(nodes, epsilon), heads, source_values)
        expansion = tuple(tuple(sum(a*epsilon**w for w, a in poly.items()) for poly in row)
                          for row in polynomials)
        assert masses == expansion
        for x, row in enumerate(normalize(masses)):
            assert max(abs(a-b) for a, b in zip(row, target[x])) <= epsilon*tails[x]/sum(leading[x])
    return orders, target


def bounded_mass_data(nodes, heads, source_values, cap):
    validate_path(nodes, heads, source_values)
    cap = exact(cap)
    polynomials = mass_polynomials(nodes, heads, source_values)
    if cap < len(heads) or any(w < 0 for row in polynomials for poly in row for w in poly):
        raise ValueError('no bounded mass lift within the requested cap')
    limit = tuple(tuple(poly[0] for poly in row) for row in polynomials)
    if max(map(sum, limit)) > cap:
        raise ValueError('the limiting normalizer itself exceeds the cap')
    tail = max(sum(a for poly in row for w, a in poly.items() if w > 0) for row in polynomials)
    return limit, tail


def check_cap_contraction(nodes, heads, source_values, cap, epsilons):
    limit, tail = bounded_mass_data(nodes, heads, source_values, cap)
    target, labels = normalize(limit), len(heads)
    records = []
    for epsilon in epsilons:
        actual = materialize(nodes, epsilon)
        # The boundary cap equals the base total only for the uniform target.
        beta = (cap-labels)/(cap-labels+tail*epsilon) if cap > labels else F(0)
        corrected = [add_sum(actual, ((head, beta),)) for head in heads]
        assert sum(n[0] == 'product' for n in actual) == sum(n[0] == 'product' for n in nodes)
        masses = native_masses(actual, corrected, source_values)
        q = normalize(masses)
        assert max(map(sum, masses)) <= cap
        assert all(abs(a-b) <= tail*epsilon for row, goal in zip(masses, limit) for a, b in zip(row, goal))
        assert all(abs(sum(row)-sum(goal)) <= tail*epsilon for row, goal in zip(masses, limit))
        error = max(abs(a-b) for row, goal in zip(q, target) for a, b in zip(row, goal))
        assert error <= 2*tail*epsilon/labels
        assert min(v for row in q for v in row) >= 1/cap
        # KL(target || q) <= chi-square(target || q), checked without logarithm rounding.
        chi_square = sum(sum((a-b)**2/b for a, b in zip(goal, row))
                         for goal, row in zip(target, q))/len(q)
        assert chi_square <= 4*cap*tail**2*epsilon**2/labels
        records.append({'epsilon': str(epsilon), 'beta': str(beta), 'maximum_normalizer': str(max(map(sum, masses))),
                        'probability_error': str(error), 'CE_upper_chi_square': str(chi_square)})
    return tail, records


def random_path(rng, d, products, labels):
    nodes = sources(d)
    def linear():
        terms = tuple((rng.randrange(len(nodes)), F(rng.randrange(5), rng.choice((1, 2, 3, 7))),
                       rng.randrange(-3, 4)) for _ in range(rng.randrange(1, 5)))
        return path_sum(nodes, terms)
    for _ in range(products):
        left, right = linear(), linear()
        add_product(nodes, left, left if rng.randrange(3) == 0 else right)
    return nodes, [linear() for _ in range(labels)]


def decoder_path(d):
    nodes = sources(d)
    factors = [path_sum(nodes, ((2*i, F(1), 0), (2*i+1, F(1), 1))) for i in range(d)]
    current = factors[0]
    for factor in factors[1:]:
        current = add_product(nodes, current, factor)
    heads = [current]
    for subset in range(1, 2**d):
        bit = subset & -subset
        coordinate = d-bit.bit_length()
        multiplied = add_product(nodes, heads[subset ^ bit], 2*coordinate+1)
        heads.append(path_sum(nodes, ((multiplied, F(1), -1),)))
    return nodes, heads


def round_and_expand(nodes, precision):
    rounded, expanded, mapping = [], [], []
    denominator = 2**precision
    for node in nodes:
        if node[0] == 'sum':
            terms = tuple((p, F((F(a)*denominator)//1, denominator)) for p, a in node[1])
            rounded.append(('sum', terms))
            scaled = [dyadic_scale(expanded, mapping[p], a) for p, a in terms]
            mapping.append(add_sum(expanded, ((p, F(1)) for p in scaled)))
        elif node[0] == 'product':
            rounded.append(node)
            mapping.append(add_product(expanded, mapping[node[1]], mapping[node[2]]))
        else:
            rounded.append(node)
            expanded.append(node)
            mapping.append(len(expanded)-1)
    return rounded, expanded, mapping


def rescale_hidden(nodes, heads, source_values, bound):
    """Preserve every final excess, using only source/SUM scaling and the same PRODUCTs."""
    bound = exact(bound)
    values = evaluate_tables(nodes, source_values)
    if bound <= 0 or any(v > bound for row in source_values.values() for v in row) or any(
            v > bound for h in heads for v in values[h]):
        raise ValueError('the sources and final excesses must already fit the activation cap')
    unit = min(F(1), bound)
    normalized, normalized_sources, mapping, scales = [], {}, [], []
    for i, node in enumerate(nodes):
        if node[0] == 'product':
            scale = scales[node[1]]*scales[node[2]]
            mapped = add_product(normalized, mapping[node[1]], mapping[node[2]])
        else:
            scale = max(F(1), max(values[i])/unit)
            if node[0] == 'source':
                source = len(normalized)
                normalized.append(node)
                normalized_sources[source] = source_values[i]
                mapped = add_sum(normalized, ((source, 1/scale),))
            else:
                mapped = add_sum(normalized, ((mapping[p], a*scales[p]/scale) for p, a in node[1]))
        mapping.append(mapped)
        scales.append(scale)
    outputs = [add_sum(normalized, ((mapping[h], scales[h]),)) for h in heads]
    result = evaluate_tables(normalized, normalized_sources)
    assert [result[h] for h in outputs] == [values[h] for h in heads]
    assert all(result[j] == tuple(v/scales[i] for v in values[i]) for i, j in enumerate(mapping))
    assert max(v for row in result for v in row) <= bound
    assert sum(n[0] == 'product' for n in normalized) == sum(n[0] == 'product' for n in nodes)
    return normalized, outputs, normalized_sources


def rounding_audit(rng):
    cases, total_nodes, nontrivial, rescaled, original_exceeds_cap = 0, 0, 0, 0, 0
    for index in range(36):
        d, products, labels = 1+index % 3, index % 5, 2+index % 4
        nodes = sources(d)
        heads = [random_graph(rng, nodes, products)]
        heads += [add_sum(nodes, ((rng.randrange(len(nodes)), F(rng.randrange(1, 9), 7))
                                 for _ in range(3))) for _ in range(labels-1)]
        source_values = binary_tables(d)
        original = evaluate_tables(nodes, source_values)
        normalizers = tuple(sum(1+original[h][x] for h in heads) for x in range(2**d))
        bound = max(F(1), *(max(original[h]) for h in heads))
        original_exceeds_cap += max(v for row in original for v in row) > bound
        rescale_hidden(nodes, heads, source_values, bound)
        rescaled += 1
        previous = None
        for precision in (1, 4, 10, 18):
            rounded, expanded, mapping = round_and_expand(nodes, precision)
            rounded_values = evaluate_tables(rounded, source_values)
            expanded_values = evaluate_tables(expanded, {mapping[p]: row for p, row in source_values.items()})
            assert [expanded_values[p] for p in mapping] == rounded_values
            assert all(a <= b for row, old in zip(rounded_values, original) for a, b in zip(row, old))
            if previous is not None:
                assert all(a <= b for row, new in zip(previous, rounded_values) for a, b in zip(row, new))
            assert max(v for row in expanded_values for v in row) <= max(v for row in original for v in row)
            assert all(sum(1+rounded_values[h][x] for h in heads) <= normalizers[x] for x in range(2**d))
            assert sum(n[0] == 'product' for n in expanded) == products
            assert {a for n in expanded if n[0] == 'sum' for _, a in n[1]} <= {F(1, 2), F(1), F(2)}
            nontrivial += rounded_values != original
            previous = rounded_values
            cases += 1
            total_nodes += len(expanded)
    assert nontrivial > 0
    # Large shared hidden feature, followed by small readouts; restore the heads only at the end.
    nodes = sources(1)
    large = add_sum(nodes, ((0, F(1024)), (1, F(1024))))
    squared = add_product(nodes, large, large)
    first = add_sum(nodes, ((squared, F(1, 2**22)),))
    descendant = add_product(nodes, first, large)
    second = add_sum(nodes, ((descendant, F(1, 1024)),))
    original_peak = max(v for row in evaluate_tables(nodes, binary_tables(1)) for v in row)
    scaled_nodes, _, scaled_sources = rescale_hidden(nodes, [first, second], binary_tables(1), F(1))
    scaled_peak = max(v for row in evaluate_tables(scaled_nodes, scaled_sources) for v in row)
    assert original_peak == 1048576 and scaled_peak == 1
    # The same theorem also works below one when the declared sources fit.
    small_sources = {0: (F(1, 8), F(1, 4)), 1: (F(1, 4), F(1, 8))}
    rescale_hidden(nodes, [first, second], small_sources, F(1, 2))
    rescaled += 2
    return {'rounded_and_expanded_graphs': cases, 'expanded_nodes_checked': total_nodes,
            'graphs_with_actual_rounding_change': nontrivial,
            'same_PRODUCT_count_normalizer_cap_and_common_activation_cap': True,
            'exact_hidden_activation_rescalings': rescaled,
            'random_original_graphs_exceeding_the_new_cap': original_exceeds_cap,
            'explicit_hidden_peak_before': str(original_peak), 'explicit_hidden_peak_after': str(scaled_peak),
            'shared_final_head_with_PRODUCT_descendant_preserved': True}


def variable_bank_audit(rng):
    records, limit = [], F(1)
    for labels in (2, 3, 5):
        for _ in range(10):
            raw = [[rng.randrange(1, 20) for _ in range(labels)] for _ in range(4)]
            target = tuple(tuple(F(v, sum(row)) for v in row) for row in raw)
            gamma = max(max(column)/min(column) for column in zip(*target))
            c, growth = 2*max(1/v for v in target[0]), 4*(1+gamma)
            masses = tuple(tuple(c*growth**i.bit_count()*v for v in row) for i, row in enumerate(target))
            coefficients = [mobius([row[j]-1 for row in masses]) for j in range(labels)]
            for b0, by, bx, bxy in coefficients:
                assert min(b0, by, bx, bxy) > 0
                limit = min(limit, b0/(2*bxy), by/(2*bxy), bx/(2*bxy))
            records.append((target, masses, coefficients))
    t = F(1)
    while t > limit:
        t /= 2
    for target, masses, coefficients in records:
        nodes, feature, table = shifted_bank(t)
        one = add_sum(nodes, ((0, 1), (1, 1)))
        heads = []
        for b0, by, bx, bxy in coefficients:
            adjusted = (b0-t*t*bxy, by-t*bxy, bx-t*bxy, bxy)
            assert min(adjusted) > 0
            heads.append(add_sum(nodes, zip((one, 3, 1, feature), adjusted)))
        actual = native_masses(nodes, heads, binary_tables(2))
        assert actual == masses and normalize(actual) == target
        assert sum(n[0] == 'product' for n in nodes) == 1
        assert decide_universality(table, len(heads), 1000)['status'] == 'NOT_UNIVERSAL'
    return {'finite_targets_realized_exactly': len(records), 'label_counts': [2, 3, 5],
            'one_common_positive_shift': str(t), 'PRODUCTs': 1,
            'every_frozen_bank_still_nonuniversal': True}


def audit():
    rng = random.Random(2026091113)
    epsilons = (F(1), F(1, 2), F(1, 8), F(1, 256))
    exhaustive_cases, random_cases, bounded_cases, divergent_rows, zero_limits = 0, 0, 0, 0, 0
    # Complete small exponent box, not completeness over every possible phase.
    for powers in product(range(-2, 3), repeat=4):
        nodes = sources(1)
        heads = [path_sum(nodes, ((0, F(2), powers[2*j]), (1, F(3), powers[2*j+1]))) for j in range(2)]
        check_path(nodes, heads, binary_tables(1), epsilons)
        exhaustive_cases += 1
    for index in range(64):
        d = 1+index % 3
        nodes, heads = random_path(rng, d, index % 5, 2+index % 4)
        source_values = binary_tables(d) if index % 2 else {
            i: tuple(F(rng.randrange(4), rng.choice((1, 2, 5))) for _ in range(2**d)) for i in range(2*d)}
        orders, target = check_path(nodes, heads, source_values, epsilons)
        divergent_rows += sum(w < 0 for w in orders)
        zero_limits += sum(v == 0 for row in target for v in row)
        random_cases += 1
        # Shift only final heads; arbitrary hidden orders/sharing remain intact.
        values = leading_tables(nodes, source_values)
        bounded_heads = []
        for h in heads:
            visible = [term[0] for term in values[h] if term is not None]
            shift = max(0, -min(visible)) if visible else 0
            bounded_heads.append(path_sum(nodes, ((h, F(1), shift),)))
        polys = mass_polynomials(nodes, bounded_heads, source_values)
        cap = max(sum(poly[0] for poly in row) for row in polys)+F(index % 2, 3)
        check_cap_contraction(nodes, bounded_heads, source_values, cap, epsilons)
        bounded_cases += 1
    assert divergent_rows and zero_limits

    # Unequal row orders and tied contributions must retain their exact amplitudes.
    nodes = sources(1)
    h0 = path_sum(nodes, ((0, F(2), -2), (0, F(1), -2), (1, F(1), 0)))
    h1 = path_sum(nodes, ((0, F(3), -2), (1, F(4), -1)))
    heads, source_values = [h0, h1], binary_tables(1)
    tied_orders, target = check_path(nodes, heads, source_values, epsilons)
    assert tied_orders == (-2, -1) and target == ((F(1, 2), F(1, 2)), (F(0), F(1)))
    assert verify_prediction(nodes, heads, source_values, target)
    forged = [((F(2, 5), F(3, 5)), (F(0), F(1))),  # dropped tied contribution
              ((F(1, 3), F(2, 3)), (F(0), F(1))),  # same support, wrong amplitudes
              ((F(1, 2), F(1, 2)), (F(1, 2), F(1, 2)))]  # wrong support
    assert all(not verify_prediction(nodes, heads, source_values, q) for q in forged)

    invalid = 0
    for amplitude, exponent in ((F(-1), 0), (float('nan'), 0), (1, float('inf')), (1, F(1, 2))):
        bad = sources(1)
        h = path_sum(bad, ((0, amplitude, exponent),))
        try:
            leading_prediction(bad, [h], source_values)
        except ValueError:
            invalid += 1
    for epsilon in (F(0), F(-1), float('nan'), float('inf')):
        try:
            materialize(nodes, epsilon)
        except ValueError:
            invalid += 1
    assert invalid == 8
    for cap in (F(1), F(100)):
        try:
            bounded_mass_data(nodes, heads, source_values, cap)
        except ValueError:
            invalid += 1
    assert invalid == 10

    decoder, decoder_heads = decoder_path(3)
    decoder_sources = binary_tables(3)
    assert sum(n[0] == 'product' for n in decoder) == 9
    orders, decoder_target = check_path(decoder, decoder_heads, decoder_sources, epsilons)
    assert set(orders) == {0}
    assert decoder_target == tuple(tuple(F(1+int(i == j), 9) for j in range(8)) for i in range(8))
    for epsilon in epsilons:
        raw = native_masses(materialize(decoder, epsilon), decoder_heads, decoder_sources)
        assert tuple(map(sum, raw)) == tuple(8+(1+epsilon)**i.bit_count() for i in range(8))
        assert max(map(sum, raw)) > 9  # reject a claimed already-feasible pure path
    tail, corrected = check_cap_contraction(decoder, decoder_heads, decoder_sources, F(9), epsilons)
    assert tail == 7
    try:
        bounded_mass_data(decoder, decoder_heads, decoder_sources, F(17, 2))
    except ValueError:
        invalid += 1
    assert invalid == 11

    # D=0 and R=k are separate exact cases, not a division by zero in the contraction.
    constant = sources(1)
    h = path_sum(constant, ((0, F(1), 0), (1, F(1), 0)))
    no_tail, _ = check_cap_contraction(constant, [h, h], binary_tables(1), F(4), epsilons)
    assert no_tail == 0
    vanishing = sources(1)
    h = path_sum(vanishing, ((0, F(1), 1), (1, F(1), 1)))
    check_cap_contraction(vanishing, [h, h], binary_tables(1), F(2), epsilons)

    return {'status': 'PASS', 'scope': SCOPE,
            'exhaustive_small_integer_exponent_box_cases': exhaustive_cases,
            'random_shared_nested_squared_DAG_paths': random_cases,
            'random_bounded_mass_cap_contractions': bounded_cases,
            'diverging_normalizer_rows_checked': divergent_rows, 'zero_limiting_probabilities_checked': zero_limits,
            'independent_checks': ['leading-order/amplitude DAG', 'complete Laurent expansion', 'actual rational native DAG'],
            'tied_leading_context_orders': list(tied_orders), 'zero_tail_and_uniform_cap_boundary_cases': 2,
            'forged_support_or_value_claims_rejected': len(forged), 'invalid_or_false_cap_inputs_rejected': invalid,
            'decoder': {'d': 3, 'labels': 8, 'PRODUCTs': 9, 'cap': 9, 'tail_constant_D': str(tail),
                        'pure_path_exceeds_cap_at_every_nonempty_context': True,
                        'same_cap_corrected_native_witnesses': corrected,
                        'pure_monomial_path_impossibility_at_P_le_11_uses': 'proved exact minimum 12 in DECODER_EXACT_AND_LIMIT_COMPLEXITY.md'},
            'local_alphabet_rounding': rounding_audit(rng), 'variable_support_invariant_bank': variable_bank_audit(rng),
            'not_claimed': ['complete generic phase or amplitude search', 'rational amplitudes for every real lift',
                            'fixed SUM/bit budget closure equality', 'activation bounds for the original unscaled execution',
                            'registered information/value/physical/persistence/AMP authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_CONDITIONAL_COEFFICIENT_PATHS_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
