"""Exact native node/edge/precision costs at rational nondyadic cap boundaries."""
from fractions import Fraction as F
from itertools import product
from math import ceil, lcm
from pathlib import Path
import argparse
import json
import random

from conditional_coefficient_paths_audit import normalize
from dyadic_cap_total_complexity_audit import ALPHABET, classify, primitive_row, singleton_bank, validate
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables
from two_product_support_border_audit import add_product, add_sum


def ideal_excess(d, target, cap):
    target, cap = validate(d, target, cap)
    if classify(d, target, cap)['status'] != 'LIMIT_ONLY':
        raise ValueError('this audit construction requires the declared nonattained cap class')
    excess = tuple(tuple(v/min(row)-1 for v in row) for row in target)
    return target, cap, excess


def dyadic_encoding(value):
    value = F(value)
    if value < 0 or value.denominator & (value.denominator-1):
        raise ValueError('a nonnegative exact dyadic value is required')
    if not value:
        return {'significand_bits': 0, 'exponent': 0, 'encoding_bits': 1}
    a, exponent = value.numerator, 1-value.denominator.bit_length()
    while a % 2 == 0:
        a //= 2
        exponent += 1
    bits = a.bit_length()
    assert F(a)*F(2)**exponent == value and a % 2 == 1
    return {'significand_bits': bits, 'exponent': exponent,
            'encoding_bits': 2+bits+max(1, abs(exponent).bit_length())}


def edge_count(nodes):
    return sum(2 if n[0] == 'product' else len(n[1]) if n[0] == 'sum' else 0 for n in nodes)


def binary_sum(nodes, terms):
    if not terms:
        return add_sum(nodes, ())
    current = terms[0]
    for parent in terms[1:]:
        current = add_sum(nodes, ((current, 1), (parent, 1)))
    return current


def grid_graph(d, target, cap, halvings, squares, exact=False):
    """Expand every repeated SUM edge; multiplicity is never an integer weight."""
    if type(halvings) is not int or halvings < 1 or type(squares) is not int or squares < 0:
        raise ValueError('positive halving depth and nonnegative squaring count required')
    target, cap = validate(d, target, cap)
    minimum = max(1/min(row) for row in target)
    target, _, excess = ideal_excess(d, target, minimum if exact else cap)
    denominator = 2**(halvings*2**squares)
    if exact:
        integer_rows = [primitive_row(row) for row in target]
        numerators = tuple(tuple(a*ceil(F(denominator, min(row)))-denominator for a in row)
                           for row in integer_rows)
    else:
        numerators = tuple(tuple(int(c*denominator) for c in row) for row in excess)
    expected = tuple(tuple(1+F(a, denominator) for a in row) for row in numerators)
    if max(map(sum, expected)) > cap:
        raise ValueError('this grid precision does not meet the declared cap')
    nodes, indicators = singleton_bank(d)
    seed = add_sum(nodes, ((0, 1), (1, 1)))
    for _ in range(halvings):
        seed = add_sum(nodes, ((seed, F(1, 2)),))
    for _ in range(squares):
        seed = add_product(nodes, seed, seed)
    scaled = [add_product(nodes, seed, indicator) for indicator in indicators]
    heads = []
    for column in zip(*numerators):
        heads.append(add_sum(nodes, ((parent, 1) for parent, a in zip(scaled, column)
                                     for _ in range(a))))
    assert sum(n[0] == 'sum' for n in nodes) == halvings+len(heads)+1
    assert sum(n[0] == 'product' for n in nodes) == squares+3*2**d-4
    return nodes, heads, {'grid_denominator': denominator, 'ideal_excess': excess, 'expected_masses': expected}


def shared_reciprocal_graph(d, target, cap, steps, exact=False):
    if type(steps) is not int or steps < 1:
        raise ValueError('positive integer reciprocal depth required')
    target, cap = validate(d, target, cap)
    minimum = max(1/min(row) for row in target)
    target, _, excess = ideal_excess(d, target, minimum if exact else cap)
    common = lcm(*(c.denominator for row in excess for c in row))
    denominator = 2**((common-1).bit_length())
    tail = 1-F(common, denominator)
    assert 0 < tail < F(1, 2)
    tau = tail**(2**steps)
    if exact and minimum*(1+(common-1)*tau) > cap:
        raise ValueError('positive tail repair exceeds the declared cap at this precision')
    nodes, indicators = singleton_bank(d)
    one = add_sum(nodes, ((0, 1), (1, 1)))
    g = dyadic_scale(nodes, one, F(1, denominator))
    t = dyadic_scale(nodes, one, tail)
    stages = []
    for i in range(steps):
        h = add_product(nodes, g, t)
        g = add_sum(nodes, ((g, 1), (h, 1)))
        stages.append((g, h, t))
        if i+1 < steps or exact:
            t = add_product(nodes, t, t)
    scaled = [add_product(nodes, g, indicator) for indicator in indicators]
    tails = [add_product(nodes, t, indicator) for indicator in indicators] if exact else []
    heads = []
    for column in zip(*excess):
        terms = [dyadic_scale(nodes, parent, c*common) for parent, c in zip(scaled, column) if c]
        if exact:
            terms.extend(dyadic_scale(nodes, parent, common+c*common-1) for parent, c in zip(tails, column))
        heads.append(binary_sum(nodes, terms))
    assert max(len(n[1]) for n in nodes if n[0] == 'sum') <= 2
    return nodes, heads, {'common_denominator': common, 'tail': tail, 'stages': stages,
                          'ideal_excess': excess, 'tau': tau, 'reciprocal': g,
                          'retained_final_tail': t if exact else None}


def check_native(d, nodes, heads, target, cap, exact=False):
    assert sum(n[0] == 'source' for n in nodes) == 2*d
    assert {w for n in nodes if n[0] == 'sum' for _, w in n[1]} <= ALPHABET
    values = evaluate_tables(nodes, binary_tables(d))
    masses = tuple(tuple(1+values[h][x] for h in heads) for x in range(2**d))
    totals = tuple(map(sum, masses))
    probabilities = normalize(masses)
    error = max(abs(p-q) for row, goal in zip(probabilities, target) for p, q in zip(row, goal))
    assert (error == 0 if exact else error > 0) and max(totals) <= cap
    assert max(v for row in values for v in row) <= max(F(1), cap-len(heads))
    direct = [dyadic_encoding(v) for row in values for v in row]
    direct.extend(dyadic_encoding(v) for row in masses for v in row)
    direct.extend(dyadic_encoding(v) for v in totals)
    volume = sum(v['encoding_bits'] for v in direct)
    probability_bits = sum(v.numerator.bit_length()+v.denominator.bit_length()+2
                           for row in probabilities for v in row)
    sums = sum(n[0] == 'sum' for n in nodes)
    products = sum(n[0] == 'product' for n in nodes)
    return {'values': values, 'masses': masses, 'totals': totals, 'probabilities': probabilities,
            'error': error, 'SUMs': sums, 'PRODUCTs': products, 'nodes': sums+products,
            'edges': edge_count(nodes), 'direct_bit_volume': volume,
            'including_rational_predictions_bits': volume+probability_bits,
            'maximum_significand_bits': max(v['significand_bits'] for v in direct)}


def precision_check(target_row, cap, masses, slack=F(0)):
    q = tuple(v/sum(masses) for v in masses)
    error = max(abs(a-b) for a, b in zip(q, target_row))
    assert 0 <= slack <= 1 and min(masses) >= 1 and sum(masses) <= cap+slack and min(target_row) == 1/cap
    witnesses = 0
    excess_checks = 0
    for j, prob in enumerate(target_row):
        forced = cap*prob
        if forced.denominator & (forced.denominator-1) == 0:
            continue
        b = dyadic_encoding(masses[j])['significand_bits']
        constant = cap*(1+forced)+int(slack > 0)
        tolerance = error+slack
        assert masses[j].denominator <= 2**(b-1)
        assert abs(masses[j]-forced) <= constant*tolerance
        assert tolerance >= F(1, 2**(b-1))/(forced.denominator*constant)
        witnesses += 1
        ideal = forced-1
        if tolerance <= ideal/(2*constant):
            actual = masses[j]-1
            bits = dyadic_encoding(actual)['significand_bits']
            assert actual >= ideal/2
            assert tolerance >= ideal/(2*forced.denominator*constant*2**bits)
            excess_checks += 1
    assert witnesses > 0
    return witnesses, excess_checks


def small_floats(bits, lower, upper):
    # Wide independent exponent range: filtering by value, not a fixed-point grid.
    return sorted({F(a)*F(2)**e for a in range(1, 2**bits, 2) for e in range(-12, 7)
                   if lower <= F(a)*F(2)**e <= upper})


def ceil_log2(value):
    value = F(value)
    if value <= 0:
        raise ValueError('positive exact logarithm argument required')
    result = value.numerator.bit_length()-value.denominator.bit_length()
    if F(2)**result < value:
        result += 1
    assert F(2)**(result-1) < value <= F(2)**result
    return result


def grid_resource_plan(d, target, minimum, slack, tolerance, sum_budget, product_budget):
    target, _, _ = ideal_excess(d, target, minimum)
    if type(slack) not in (int, F) or type(tolerance) not in (int, F):
        raise ValueError('exact range slack and tolerance required')
    if not 0 <= slack <= 1 or tolerance < 0 or slack+tolerance <= 0:
        raise ValueError('nonnegative tolerances with positive joint allowance required')
    if type(sum_budget) is not int or type(product_budget) is not int:
        raise ValueError('integer resource budgets required')
    row_sum = max(sum(primitive_row(row)) for row in target)
    level = ceil_log2(F(2*max(1, row_sum))/(slack+tolerance))
    sum_overhead, product_overhead = len(target[0])+1, 3*2**d-4
    sums, products = sum_budget-sum_overhead, product_budget-product_overhead
    if level < 1 or sums < 1 or products < 0 or sums*2**products < level:
        raise ValueError('outside this sufficient envelope; no full-class rejection follows')
    squares = min(products, ceil_log2(level))
    halvings = ceil(F(level, 2**squares))
    exponent = halvings*2**squares
    bits = 2*level+ceil_log2(minimum+1)+1
    assert halvings <= sums and level <= exponent <= 2*level
    return {'halvings': halvings, 'squares': squares, 'level': level,
            'exact': slack >= tolerance, 'significand_bits': bits, 'grid_exponent': exponent}


def audit():
    scalar = ((F(5, 8), F(3, 8)),)*2
    mixed = ((F(1, 4), F(3, 8), F(3, 8)), (F(1, 4), F(1, 3), F(5, 12)))
    cases = [(1, scalar, F(8, 3)), (1, mixed, F(4))]
    rng = random.Random(2026091203)
    while len(cases) < 20:
        d, k = rng.choice((1, 2, 3)), rng.choice((2, 3, 4))
        raw = [[rng.randrange(1, 10) for _ in range(k)] for _ in range(2**d)]
        target = tuple(tuple(F(v, sum(row)) for v in row) for row in raw)
        cap = max(1/min(row) for row in target)
        if classify(d, target, cap)['status'] == 'LIMIT_ONLY':
            cases.append((d, target, cap))

    grid_records = []
    grid_count = 0
    grids = [(1, p) for p in range(5)]+[(s, p) for s in (2, 3) for p in range(3)]
    for case, (d, target, cap) in enumerate(cases[:2]):
        for halvings, squares in grids:
            nodes, heads, metadata = grid_graph(d, target, cap, halvings, squares)
            report = check_native(d, nodes, heads, target, cap)
            denominator = metadata['grid_denominator']
            ideal = metadata['ideal_excess']
            expected = tuple(tuple(1+F(int(c*denominator), denominator) for c in row) for row in ideal)
            assert report['masses'] == expected
            assert all((v*denominator).denominator == 1 for row in report['values'] for v in row)
            common = lcm(*(v.denominator for row in target for v in row))
            assert F(1, denominator)/(common*cap) <= report['error'] <= F(1, denominator)
            readout_edges = sum(len(nodes[h][1]) for h in heads)
            mass_sum = sum(c for row in ideal for c in row)
            assert denominator*mass_sum-2**d*len(heads) < readout_edges <= denominator*mass_sum
            if case == 0 and halvings == 1:
                grid_records.append({key: report[key] for key in
                                     ('SUMs', 'PRODUCTs', 'nodes', 'edges', 'maximum_significand_bits')}
                                    | {'squares': squares, 'grid_denominator_bits': denominator.bit_length(),
                                       'error': str(report['error'])})
            grid_count += 1

    reciprocal_records = []
    reciprocal_count, stage_checks, mass_precision_checks, excess_precision_checks = 0, 0, 0, 0
    for case, (d, target, cap) in enumerate(cases):
        base_counts = None
        for steps in (1, 2, 3, 5, 8):
            nodes, heads, metadata = shared_reciprocal_graph(d, target, cap, steps)
            report = check_native(d, nodes, heads, target, cap)
            common, tau = metadata['common_denominator'], metadata['tau']
            tail = metadata['tail']
            values, ideal = report['values'], metadata['ideal_excess']
            for i, (g, h, t) in enumerate(metadata['stages']):
                assert set(values[t]) == {tail**(2**i)}
                assert set(values[g]) == {F(1, common)*(1-tail**(2**(i+1)))}
                stage_checks += 1
            assert set(values[metadata['reciprocal']]) == {F(1, common)*(1-tau)}
            assert report['masses'] == tuple(tuple(1+(1-tau)*c for c in row) for row in ideal)
            exact_errors = []
            for row, goal, total in zip(ideal, target, report['totals']):
                original_total = len(heads)+sum(row)
                assert total == original_total-tau*(original_total-len(heads))
                exact_errors.extend(tau*abs(1-len(heads)*q)/total for q in goal)
            assert report['error'] == max(exact_errors)
            if base_counts is None:
                base_counts = report['SUMs'], report['PRODUCTs'], report['edges']
            assert report['SUMs'] == base_counts[0]+steps-1
            assert report['PRODUCTs'] == base_counts[1]+2*(steps-1)
            assert report['edges'] == base_counts[2]+6*(steps-1)
            # A loose, explicit full-materialization upper independent of requested depth.
            fixed_nodes = len(nodes)-3*steps+1
            seed_bits = (2**((common-1).bit_length())).bit_length()
            maximum_integer = max(int(c*common) for row in ideal for c in row)
            target_bits = max(1, maximum_integer.bit_length())
            volume_upper = 100*2**d*(fixed_nodes+len(heads)+1)*(seed_bits+target_bits+1)*2**steps
            assert report['including_rational_predictions_bits'] <= volume_upper
            for goal, masses in zip(target, report['masses']):
                if min(goal) == 1/cap and any((cap*v).denominator & ((cap*v).denominator-1) for v in goal):
                    a, b = precision_check(goal, cap, masses)
                    mass_precision_checks += a
                    excess_precision_checks += b
            if case == 0:
                reciprocal_records.append({key: report[key] for key in
                                           ('SUMs', 'PRODUCTs', 'nodes', 'edges', 'direct_bit_volume',
                                            'including_rational_predictions_bits', 'maximum_significand_bits')}
                                          | {'steps': steps, 'error_denominator_bits': report['error'].denominator.bit_length()})
            reciprocal_count += 1

    repaired_graphs, repaired_mass_checks, repaired_excess_checks, rejected_slack = 0, 0, 0, 0
    repair_records = []
    for case, (d, target, minimum) in enumerate(cases):
        excess = tuple(tuple(v/min(row)-1 for v in row) for row in target)
        common = lcm(*(v.denominator for row in excess for v in row))
        h_seed = 2**((common-1).bit_length())
        tail = 1-F(common, h_seed)
        base_counts = None
        for steps in (1, 2, 3, 5, 8):
            tau = tail**(2**steps)
            slack = minimum*(common-1)*tau
            if slack > 1:
                continue
            nodes, heads, metadata = shared_reciprocal_graph(d, target, minimum+slack, steps, exact=True)
            report = check_native(d, nodes, heads, target, minimum+slack, exact=True)
            assert set(report['values'][metadata['retained_final_tail']]) == {tau}
            assert report['masses'] == tuple(tuple((1+(common-1)*tau)*(1+c) for c in row) for row in excess)
            assert max(report['totals']) == minimum+slack
            if base_counts is None:
                base_counts = steps, report['SUMs'], report['PRODUCTs'], report['edges']
            first, sums, products, edges = base_counts
            assert report['SUMs'] == sums+steps-first
            assert report['PRODUCTs'] == products+2*(steps-first)
            assert report['edges'] == edges+6*(steps-first)
            for goal, masses in zip(target, report['masses']):
                if min(goal) == 1/minimum and any((minimum*v).denominator & ((minimum*v).denominator-1) for v in goal):
                    a, b = precision_check(goal, minimum, masses, slack)
                    repaired_mass_checks += a
                    repaired_excess_checks += b
            try:
                shared_reciprocal_graph(d, target, minimum+slack/2, steps, exact=True)
            except ValueError:
                rejected_slack += 1
            if case == 0:
                repair_records.append({key: report[key] for key in
                                       ('SUMs', 'PRODUCTs', 'nodes', 'edges', 'direct_bit_volume', 'maximum_significand_bits')}
                                      | {'steps': steps, 'exact_prediction': True,
                                         'slack': str(slack) if steps <= 3 else 'rational; denominator bits recorded',
                                         'slack_denominator_bits': slack.denominator.bit_length()})
            repaired_graphs += 1
    assert rejected_slack == repaired_graphs and repaired_excess_checks > 0

    exact_grid_graphs, rejected_grid = 0, 0
    for d, target, minimum in cases[:2]:
        integer_rows = [primitive_row(row) for row in target]
        for squares in (1, 2, 3, 4):
            denominator = 2**(2**squares)
            actual_cap = max(F(sum(row)*ceil(F(denominator, min(row))), denominator) for row in integer_rows)
            nodes, heads, metadata = grid_graph(d, target, actual_cap, 1, squares, exact=True)
            report = check_native(d, nodes, heads, target, actual_cap, exact=True)
            assert report['masses'] == metadata['expected_masses']
            assert minimum < actual_cap <= minimum+F(max(map(sum, integer_rows)), denominator)
            try:
                grid_graph(d, target, (minimum+actual_cap)/2, 1, squares, exact=True)
            except ValueError:
                rejected_grid += 1
            exact_grid_graphs += 1
    assert exact_grid_graphs == rejected_grid

    envelope_graphs, envelope_exact, rejected_envelopes = 0, 0, 0
    for d, target, minimum in cases[:2]:
        for level, fraction, product_allowance in product((1, 3, 5), (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)), range(3)):
            epsilon = F(1, 2**level)
            slack, tolerance = fraction*epsilon, (1-fraction)*epsilon
            row_sum = max(sum(primitive_row(row)) for row in target)
            grid_level = ceil_log2(2*row_sum/epsilon)
            product_budget = 3*2**d-4+product_allowance
            sum_budget = len(target[0])+1+ceil(F(grid_level, 2**product_allowance))
            plan = grid_resource_plan(d, target, minimum, slack, tolerance, sum_budget, product_budget)
            nodes, heads, _ = grid_graph(d, target, minimum+slack if plan['exact'] else minimum,
                                         plan['halvings'], plan['squares'], exact=plan['exact'])
            report = check_native(d, nodes, heads, target, minimum+slack, exact=plan['exact'])
            assert report['error'] <= tolerance
            assert report['SUMs'] <= sum_budget and report['PRODUCTs'] <= product_budget
            assert report['maximum_significand_bits'] <= plan['significand_bits']
            positive = [v for row in report['values'] for v in row if v]
            assert min(positive) >= F(1, 2**plan['grid_exponent'])
            try:
                grid_resource_plan(d, target, minimum, slack, tolerance, sum_budget-1, product_budget)
            except ValueError:
                rejected_envelopes += 1
            envelope_graphs += 1
            envelope_exact += int(plan['exact'])
    assert rejected_envelopes == envelope_graphs

    floating_rows, floating_mass_checks, floating_excess_checks = 0, 0, 0
    for goal, cap, maximum in ((scalar[0], F(8, 3), 6), (mixed[1], F(4), 5)):
        for bits in range(1, maximum+1):
            values = small_floats(bits, F(1), cap-len(goal)+1)
            for masses in product(values, repeat=len(goal)):
                if sum(masses) > cap:
                    continue
                a, b = precision_check(goal, cap, masses)
                floating_rows += 1
                floating_mass_checks += a
                floating_excess_checks += b
    assert floating_excess_checks > 0

    # All displayed probabilities can be exact while mathematical normalization is not.
    excess64 = float(F(2, 3))
    masses64 = (1.0+excess64, 1.0)
    total64 = sum(masses64)
    displayed = tuple(v/total64 for v in masses64)
    stored = tuple(map(F, masses64))
    semantic = tuple(v/sum(stored) for v in stored)
    error64 = max(abs(a-b) for a, b in zip(semantic, scalar[0]))
    assert displayed == tuple(map(float, scalar[0])) and error64 > 0
    assert sum(stored) <= F(8, 3)
    precision_check(scalar[0], F(8, 3), stored)
    rounded = {'stored_mass_hex': [v.hex() for v in masses64],
               'rounded_probabilities': [str(v) for v in displayed],
               'exact_probability_error_from_stored_masses': str(error64),
               'exact_cap_respected': True, 'mass_significand_bits': dyadic_encoding(stored[0])['significand_bits']}

    invalid = 0
    for value in (F(-1), F(1, 3)):
        try:
            dyadic_encoding(value)
        except ValueError:
            invalid += 1
    for d, target, cap in ((1, scalar, F(3)), (1, scalar, F(5, 2))):
        try:
            shared_reciprocal_graph(d, target, cap, 1)
        except ValueError:
            invalid += 1
    assert invalid == 4
    return {'status': 'PASS', 'scope': 'complete binary unary sources; rational targets in LIMIT_ONLY at R0; cap R0+h; local weights {1/2,1,2}',
            'full_domain_target_cases': len(cases), 'expanded_repeated_edge_graphs': grid_count,
            'binary_arity_shared_reciprocal_graphs': reciprocal_count, 'exact_shared_stage_checks': stage_checks,
            'exact_positive_tail_repair_graphs': repaired_graphs, 'exact_expanded_grid_slack_graphs': exact_grid_graphs,
            'insufficient_slack_constructions_rejected': rejected_slack+rejected_grid,
            'joint_slack_mass_precision_inequalities': repaired_mass_checks,
            'joint_slack_excess_precision_inequalities': repaired_excess_checks,
            'separate_PRODUCT_SUM_range_precision_envelope_graphs': envelope_graphs,
            'envelope_exact_predictions': envelope_exact, 'insufficient_sufficient_envelope_requests_rejected': rejected_envelopes,
            'graph_mass_precision_inequalities': mass_precision_checks, 'graph_excess_precision_inequalities': excess_precision_checks,
            'small_floating_mass_rows': floating_rows, 'small_float_mass_precision_inequalities': floating_mass_checks,
            'small_float_excess_precision_inequalities': floating_excess_checks,
            'node_only_optimum': 'log2(log2(1/delta))+O_target(1)',
            'expanded_parent_family_edge_cost': 'Theta_target(1/actual_error)',
            'joint_achievable_orders': {'nodes': 'Theta(log log(1/delta))', 'edges': 'Theta(log log(1/delta))',
                                        'full_direct_numerical_bit_volume': 'Theta(log(1/delta))'},
            'one_shared_reciprocal_growing_counts': {'SUMs': 'n', 'PRODUCTs': '2*n-1', 'other_work': 'fixed target-dependent overhead'},
            'expanded_edge_example': grid_records, 'bounded_arity_example': reciprocal_records,
            'joint_slack_and_accuracy_law': {'node_only_optimum': 'log2(log2(1/(h+delta)))+O_target(1)',
                                            'joint_node_edge_order': 'Theta(log log(1/(h+delta)))',
                                            'direct_numerical_bit_volume_order': 'Theta(log(1/(h+delta)))'},
            'exact_positive_tail_repair_example': repair_records,
            'binary64_displayed_equality_counterexample': rounded, 'invalid_or_different_branch_requests_rejected': invalid,
            'not_claimed': ['optimal bounded-arity leading constant', 'exact low-P Pareto phases',
                            'liveness-optimal memory or optimal bit-time', 'arbitrary symbolic or multi-component number encoding',
                            'fixed-precision AMP bridge, registered value access or physical Runtime authority']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_NODE_EDGE_PRECISION_ACCURACY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
