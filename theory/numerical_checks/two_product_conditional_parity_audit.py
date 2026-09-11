"""Exact larger-range parity witnesses; full-class lower and fixed-bank dual checks."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import random

from decoder_exact_limit_audit import predictions
from normalizer_slack_decoder_audit import dyadic_scale
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_support_border_audit import add_product, add_sum, cube, sources


def build_parity(odds=F(3), local_integer=False):
    r = F(odds)
    if r <= 1:
        raise ValueError('odds must exceed one')
    nodes = sources(3)
    left = add_sum(nodes, ((1, 1), (3, 1)))
    right = add_sum(nodes, ((0, 1), (2, 1)))
    a = add_product(nodes, left, right)
    b = add_product(nodes, a, 5)
    readouts = (((4, r-1), (b, (r-1)*(r+1)**2)), ((5, r-1), (a, r*r-1)))
    heads = []
    for terms in readouts:
        if local_integer:
            if any(weight.denominator != 1 for _, weight in terms):
                raise ValueError('integer path requires integer coefficients')
            terms = [(dyadic_scale(nodes, parent, weight), F(1)) for parent, weight in terms]
        heads.append(add_sum(nodes, terms))
    return nodes, heads, (a, b)


def verify_dual(odds, weights):
    r = F(odds)
    if r <= 1 or len(weights) != 4 or min(weights) < 0:
        return False
    rows = ((1, 0, 0, 0, -1), (0, 1, 0, 0, -1), (-r, 0, 1, 0, 0), (1, -r, -r, 1, 0))
    return tuple(sum(F(w)*row[i] for w, row in zip(weights, rows)) for i in range(5)) == (0, 0, 0, 1, -(r*r+r-1))


def audit():
    records, entries = [], 0
    odds_values = (F(1025, 1024), F(6, 5), F(3, 2), F(2), F(3), F(7), F(33))
    for r in odds_values:
        nodes, heads, features = build_parity(r)
        values = evaluate_tables(nodes, binary_tables(3))
        totals = []
        for i, (x, y, z) in enumerate(cube(3)):
            a = x ^ y
            assert values[features[0]][i] == a and values[features[1]][i] == a*z
            q, total = predictions([values[head][i] for head in heads])
            assert q == tuple((r if label == a ^ z else 1)/(r+1) for label in range(2))
            totals.append(total)
            entries += 2
        assert sum(node[0] == 'product' for node in nodes) == 2
        assert max(totals) == (r+1)*(r*r+r-1)
        assert verify_dual(r, (r*r-1, r, r, 1))
        records.append({'odds': str(r), 'noise': str(1/(r+1)), 'PRODUCTs': 2,
                        'maximum_normalizer': str(max(totals))})

    nodes, heads, _ = build_parity(F(3), local_integer=True)
    values = evaluate_tables(nodes, binary_tables(3))
    assert sum(node[0] == 'product' for node in nodes) == 2
    assert {weight for node in nodes if node[0] == 'sum' for _, weight in node[1]} <= {F(1), F(2)}
    for i, context in enumerate(cube(3)):
        q, total = predictions([values[head][i] for head in heads])
        assert q[1] == F(3 if sum(context) % 2 else 1, 4) and total <= 44

    rng = random.Random(2026091110)
    order_cases = 160
    for _ in range(order_cases):
        nodes = sources(3)
        first = random_graph(rng, nodes, rng.randrange(2))
        second = add_sum(nodes, ((rng.randrange(len(nodes)), rng.choice((F(1, 2), F(1), F(3)))) for _ in range(6)))
        values = evaluate_tables(nodes, binary_tables(3))
        masses = [(1+values[first][i], 1+values[second][i]) for i in range(8)]
        signs = [(-1)**sum(context) for context in cube(3)]
        assert all(sum(signs[i]*masses[i][label] for i in range(8)) == 0 for label in range(2))
        q = [row[1]/sum(row) for row in masses]
        even = [i for i in range(8) if signs[i] == 1]
        odd = [i for i in range(8) if signs[i] == -1]
        even_mass, odd_mass = (sum(sum(masses[i]) for i in group) for group in (even, odd))
        assert even_mass == odd_mass
        assert sum(masses[i][1] for i in even)/even_mass == sum(masses[i][1] for i in odd)/odd_mass
        assert max(q[i] for i in even) >= min(q[i] for i in odd)
        for r in odds_values[:5]:
            eta = 1/(r+1)
            assert max(abs(q[i]-(eta if signs[i] == 1 else 1-eta)) for i in range(8)) >= F(1, 2)-eta

    dual_scale_cases = 100
    for _ in range(dual_scale_cases):
        r = rng.choice(odds_values)
        e0, e1, ea, eb = (F(rng.randrange(9), rng.choice((2, 3, 7))) for _ in range(4))
        u0, u1 = 1+e0, 1+e1
        ua = r*u0+ea
        ub = r*ua+r*u1-u0+eb
        assert ub-(r*r+r-1) == eb+r*ea+(r*r-1)*e0+r*e1 >= 0
    for r in odds_values:
        assert not verify_dual(r, (r*r-1, r, r, 2))
        assert not verify_dual(r, (r*r-1, r, -r, 1))
        assert not verify_dual(r, (r*r-1, r, r))
    invalid = 0
    for odds in (F(0), F(1), F(-3)):
        try:
            build_parity(odds)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError('invalid odds accepted')

    return {'status': 'PASS',
            'scope': 'static full-class at-most-one-PRODUCT lower; exact two-PRODUCT upper; fixed-bank range dual only',
            'witnesses': records, 'exact_probability_entries': entries,
            'noise_one_quarter_integer_alphabet': [1, 2], 'integer_graph_PRODUCTs': 2,
            'integer_graph_maximum_normalizer': '44', 'arbitrary_one_PRODUCT_order_cases': order_cases,
            'one_PRODUCT_probability_gap': '1/2-eta', 'one_PRODUCT_CE_gap': '(log(2)-H(eta))/4',
            'fixed_bank_optimal_cap': '(r+1)*(r^2+r-1)', 'exact_dual_scale_cases': dual_scale_cases,
            'forged_duals_rejected': 3*len(odds_values), 'invalid_odds_rejected': invalid,
            'not_claimed': ['sharp range for arbitrary two-PRODUCT parents', 'three-PRODUCT intermediate phases',
                            'registered acquisition/value/install/persistence or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_TWO_PRODUCT_CONDITIONAL_PARITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
