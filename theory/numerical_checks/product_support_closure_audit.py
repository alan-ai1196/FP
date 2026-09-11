"""Support limits of a complete static P-PRODUCT grammar, with rational certificates.

Float64 LP calls only propose exponents or Farkas combinations. Acceptance
and rejection are checked independently against the full external d,P,mask.
Work or reconstruction failures return UNRESOLVED, with no Runtime authority.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from math import gcd, lcm
from pathlib import Path
import argparse
import json
import random


class Unresolved(Exception):
    pass


def cube(d):
    return tuple(product((0, 1), repeat=d))


def groups(d, products):
    cursor, result = 0, []
    for size in [v for j in range(products) for v in (2*d+j, 2*d+j)]+[2*d+products]:
        result.append(tuple(range(cursor, cursor+size)))
        cursor += size
    return tuple(result)


@dataclass(frozen=True)
class Monomial:
    exponent: tuple
    support: int
    multiplicity: int


def expand(d, products, work_budget=200000):
    assert type(d) is int and d >= 1 and type(products) is int and products >= 0
    assert type(work_budget) is int and work_budget >= 0
    allocation = groups(d, products)
    width = 2*d*(2*products+1)+products**2
    contexts, work = cube(d), 0
    zero = (0,)*width
    features = [{zero: (sum(int(x[i] == bit)<<k for k, x in enumerate(contexts)), 1)}
                for i in range(d) for bit in (0, 1)]

    def consume():
        nonlocal work
        work += 1
        if work > work_budget:
            raise Unresolved('monomial expansion work budget')

    def affine(coefficients):
        out = {}
        for slot, feature in zip(coefficients, features):
            for exponent, value in feature.items():
                consume()
                e = list(exponent)
                e[slot] += 1
                assert tuple(e) not in out  # New slot identifies its parent.
                out[tuple(e)] = value
        return out

    for j in range(products):
        left, right = affine(allocation[2*j]), affine(allocation[2*j+1])
        out = {}
        for a, (mask_a, count_a) in left.items():
            for b, (mask_b, count_b) in right.items():
                consume()
                mask = mask_a & mask_b
                if not mask:
                    continue  # Exact source annihilator on the complete domain.
                exponent = tuple(x+y for x, y in zip(a, b))
                old_mask, old_count = out.get(exponent, (mask, 0))
                assert old_mask == mask
                out[exponent] = mask, old_count+count_a*count_b
        features.append(out)
    polynomial = affine(allocation[-1])
    return tuple(Monomial(e, mask, count) for e, (mask, count) in sorted(polynomial.items())), work


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def evaluate(d, products, coefficients):
    """Native arithmetic order; a separate path from the polynomial expansion."""
    allocation = groups(d, products)
    assert len(coefficients) == len(allocation[-1])+allocation[-1][0]
    result = []
    for x in cube(d):
        values = [F(x[i] == bit) for i in range(d) for bit in (0, 1)]
        for j in range(products):
            left = sum(coefficients[k]*v for k, v in zip(allocation[2*j], values))
            right = sum(coefficients[k]*v for k, v in zip(allocation[2*j+1], values))
            values.append(left*right)
        result.append(sum(coefficients[k]*v for k, v in zip(allocation[-1], values)))
    return tuple(result)


def leading(d, products, exponents):
    """Minimum exponent plus positive tie count, without expanding the graph."""
    allocation = groups(d, products)
    assert len(exponents) == allocation[-1][-1]+1
    assert all(type(v) is int for v in exponents)
    result = []
    for x in cube(d):
        values = [(0, 1) if x[i] == bit else (None, 0) for i in range(d) for bit in (0, 1)]

        def affine(slots):
            terms = [(exponents[k]+order, count) for k, (order, count) in zip(slots, values)
                     if order is not None]
            minimum = min(v for v, _ in terms)
            return minimum, sum(count for v, count in terms if v == minimum)

        for j in range(products):
            a, ca = affine(allocation[2*j])
            b, cb = affine(allocation[2*j+1])
            values.append((a+b, ca*cb))
        result.append(affine(allocation[-1]))
    return tuple(result)


def valid_input(d, products, support):
    return (type(d) is int and d >= 1 and type(products) is int and products >= 0
            and type(support) is int and 0 <= support < 1 << (2**d))


def verify_accept(d, products, support, exponents):
    try:
        if not valid_input(d, products, support):
            return False
        values = leading(d, products, exponents)
        return all(order == 0 if support>>i & 1 else order >= 1
                   for i, (order, _) in enumerate(values))
    except (AssertionError, ValueError, TypeError, IndexError):
        return False


def check_farkas(monomials, support, selected, certificate):
    """Sparse exact exponent balance; positive bad weight proves 0 >= a > 0."""
    try:
        positive, negative = certificate['positive'], certificate['negative']
        width = len(monomials[0].exponent)
        balance = [F(0)]*width
        strict = F(0)
        seen = set()
        for index, weight in positive:
            if (type(index) is not int or not 0 <= index < len(monomials) or index in seen
                    or type(weight) not in (int, F) or weight <= 0):
                return False
            seen.add(index)
            m = monomials[index]
            for j, v in enumerate(m.exponent):
                balance[j] += weight*v
            if m.support & ~support:
                strict += weight
        seen = set()
        for index, weight in negative:
            if (type(index) is not int or index not in selected or index in seen
                    or type(weight) not in (int, F) or weight <= 0):
                return False
            seen.add(index)
            for j, v in enumerate(monomials[index].exponent):
                balance[j] -= weight*v
        return strict > 0 and not any(balance)
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def candidates(monomials, support, context):
    return tuple(i for i, m in enumerate(monomials)
                 if m.support >> context & 1 and not m.support & ~support)


def verify_reject(d, products, support, certificate, expansion_budget=200000):
    try:
        if not valid_input(d, products, support):
            return False
        monomials, _ = expand(d, products, expansion_budget)

        def visit(tree, selected):
            covered = 0
            for i in selected:
                covered |= monomials[i].support
            kind = tree['kind']
            if kind == 'FARKAS':
                return check_farkas(monomials, support, selected, tree)
            context = tree['context']
            if (type(context) is not int or not 0 <= context < 2**d
                    or not support >> context & 1 or covered >> context & 1):
                return False
            available = candidates(monomials, support, context)
            if kind == 'NO_LEADING_MONOMIAL':
                return not available
            if kind != 'SPLIT' or tuple(i for i, _ in tree['children']) != available:
                return False
            return all(visit(child, (*selected, i)) for i, child in tree['children'])

        return visit(certificate, ())
    except (Unresolved, AssertionError, KeyError, IndexError, TypeError, ValueError):
        return False


def lp_alternative(monomials, support, selected):
    import numpy as np
    from scipy.optimize import linprog
    width = len(monomials[0].exponent)
    a = np.array([m.exponent for m in monomials]+[tuple(-v for v in monomials[i].exponent)
                                               for i in selected], dtype=np.float64)
    b = np.array([int(bool(m.support & ~support)) for m in monomials]+[0]*len(selected), float)
    result = linprog(np.zeros(width), A_ub=-a, b_ub=-b, bounds=(None, None), method='highs')
    if result.success and result.x is not None and np.all(np.isfinite(result.x)):
        for denominator in (10**3, 10**6, 10**9):
            w = tuple(F(float(v)).limit_denominator(denominator) for v in result.x)
            if (all(dot(m.exponent, w) >= int(bool(m.support & ~support)) for m in monomials)
                    and all(dot(monomials[i].exponent, w) == 0 for i in selected)):
                return 'primal', w
    dual = linprog(np.zeros(len(a)), A_eq=np.vstack((a.T, b)),
                   b_eq=np.r_[np.zeros(width), 1.0], bounds=(0, None), method='highs')
    if dual.success and dual.x is not None and np.all(np.isfinite(dual.x)):
        for denominator in (10**3, 10**6, 10**9):
            y = tuple(F(float(v)).limit_denominator(denominator) for v in dual.x)
            if min(y) < 0:
                continue
            evidence = {'kind': 'FARKAS',
                        'positive': [(i, value) for i, value in enumerate(y[:len(monomials)]) if value],
                        'negative': [(i, value) for i, value in zip(selected, y[len(monomials):]) if value]}
            if check_farkas(monomials, support, selected, evidence):
                return 'dual', evidence
    raise Unresolved('LP proposal had no exactly checked primal/Farkas alternative')


def integer_exponents(w):
    scale = lcm(*(v.denominator for v in w))
    out = tuple(int(v*scale) for v in w)
    common = 0
    for v in out:
        common = gcd(common, abs(v))
    return tuple(v//common for v in out) if common else out


def solve(d, products, support, node_budget=5000, expansion_budget=200000):
    assert valid_input(d, products, support)
    assert type(node_budget) is int and node_budget >= 0
    work = 0
    statistics = {'search_nodes': 0, 'LP_calls': 0}
    try:
        monomials, work = expand(d, products, expansion_budget)
        statistics.update({'expansion_work': work, 'visible_monomials': len(monomials)})
        choices = {x: candidates(monomials, support, x) for x in range(2**d) if support >> x & 1}

        def visit(selected):
            if statistics['search_nodes'] >= node_budget:
                raise Unresolved('support search node budget')
            statistics['search_nodes'] += 1
            covered = 0
            for i in selected:
                covered |= monomials[i].support
            remaining = [x for x in choices if not covered >> x & 1]
            if remaining:
                x = min(remaining, key=lambda x: (len(choices[x]), x))
                if not choices[x]:
                    return 'reject', {'kind': 'NO_LEADING_MONOMIAL', 'context': x}
            statistics['LP_calls'] += 1
            status, evidence = lp_alternative(monomials, support, selected)
            if status == 'dual':
                return 'reject', evidence
            exponents = integer_exponents(evidence)
            if verify_accept(d, products, support, exponents):
                return 'accept', exponents
            assert remaining
            children = []
            for index in choices[x]:
                kind, child = visit((*selected, index))
                if kind == 'accept':
                    return kind, child
                children.append((index, child))
            return 'reject', {'kind': 'SPLIT', 'context': x, 'children': children}

        kind, evidence = visit(())
        if kind == 'accept':
            assert verify_accept(d, products, support, evidence)
            return {'status': 'SUPPORT_IN_CLOSURE', 'exponents': evidence, 'statistics': statistics}
        assert verify_reject(d, products, support, evidence, expansion_budget)
        return {'status': 'SUPPORT_OUTSIDE_CLOSURE', 'proof': evidence, 'statistics': statistics}
    except Unresolved as exc:
        return {'status': 'UNRESOLVED', 'reason': str(exc), 'statistics': statistics}


def tree_statistics(tree):
    counts = Counter()
    def visit(node):
        counts[node['kind']] += 1
        if node['kind'] == 'SPLIT':
            for _, child in node['children']:
                visit(child)
    visit(tree)
    return dict(counts)


def mass_margin(d, products, support, proof, gamma=F(1), maximum=F(1)):
    """A conservative rational scalar-distance bound, for this target support."""
    assert type(gamma) in (int, F) and type(maximum) in (int, F) and 0 < gamma <= maximum
    assert verify_reject(d, products, support, proof)
    monomials, _ = expand(d, products)
    allocation = groups(d, products)
    root_slots = allocation[-1]
    assert all(sum(m.exponent[i] for i in root_slots) == 1 for m in monomials)
    maximum_power = 1
    def visit(node):
        nonlocal maximum_power
        if node['kind'] == 'SPLIT':
            for _, child in node['children']:
                visit(child)
        elif node['kind'] == 'FARKAS':
            total = sum(F(v) for _, v in node['positive'])
            bad = sum(F(v) for i, v in node['positive'] if monomials[i].support & ~support)
            assert total == sum(F(v) for _, v in node['negative']) and bad > 0
            ratio = total/bad
            maximum_power = max(maximum_power, -(-ratio.numerator//ratio.denominator))
    visit(proof)
    width = allocation[-1][-1]+1
    totals = evaluate(d, products, (F(1),)*width)
    count_bound = max(totals)
    assert count_bound.denominator == 1
    pure_bound = max((sum(m.multiplicity for m in monomials
                          if m.support>>x & 1 and not m.support & ~support)
                      for x in range(2**d) if support>>x & 1), default=0)
    bad_bound = max((sum(m.multiplicity for m in monomials
                         if m.support>>x & 1 and m.support & ~support)
                     for x in range(2**d) if support>>x & 1), default=0)
    bound = F(gamma)/(2*(bad_bound+1))
    if pure_bound:
        bound = min(bound, 2*maximum*(F(gamma)/(4*pure_bound*maximum))**maximum_power)
    return bound, {'total': int(count_bound), 'pure': pure_bound, 'bad': bad_bound}, maximum_power


def pack_proof(proof):
    """Intern identical proof nodes without storing expanded repeated subtrees."""
    pool, intern = [], {}
    def visit(node):
        if node['kind'] == 'SPLIT':
            packed = ['S', node['context'], [visit(child) for _, child in node['children']]]
        elif node['kind'] == 'NO_LEADING_MONOMIAL':
            packed = ['N', node['context']]
        else:
            weights = [F(v) for name in ('positive', 'negative') for _, v in node[name]]
            scale = lcm(*(v.denominator for v in weights))
            common = gcd(*(int(v*scale) for v in weights))
            packed = ['F', *[[[i, int(F(v)*scale)//common] for i, v in node[name]]
                             for name in ('positive', 'negative')]]
        key = json.dumps(packed, separators=(',', ':'))
        if key not in intern:
            intern[key] = len(pool)
            pool.append(packed)
        return intern[key]
    root = visit(proof)
    return {'root': root, 'nodes': pool}


def unpack_proof(d, products, support, packed):
    """Decode only full covered splits, with child ids strictly preceding parents."""
    monomials, _ = expand(d, products)
    nodes = packed['nodes']
    assert type(packed['root']) is int and 0 <= packed['root'] < len(nodes)
    decoded = []
    for index, node in enumerate(nodes):
        if node[0] == 'F':
            assert len(node) == 3
            out = {'kind': 'FARKAS', 'positive': node[1], 'negative': node[2]}
        elif node[0] == 'N':
            assert len(node) == 2
            out = {'kind': 'NO_LEADING_MONOMIAL', 'context': node[1]}
        else:
            assert len(node) == 3 and node[0] == 'S'
            available = candidates(monomials, support, node[1])
            assert len(available) == len(node[2])
            assert all(type(i) is int and 0 <= i < index for i in node[2])
            out = {'kind': 'SPLIT', 'context': node[1],
                   'children': [(m, decoded[i]) for m, i in zip(available, node[2])]}
        decoded.append(out)
    return decoded[packed['root']]


def support_mask(d, predicate):
    return sum(int(bool(predicate(x)))<<i for i, x in enumerate(cube(d)))


def verified_parity_proof():
    path = Path(__file__).resolve().parents[2]/'evidence/minimal/FP_PARITY_TWO_PRODUCT_SUPPORT_PROOF.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    # The intended claim is external to the artifact's own fields.
    assert (record['d'], record['PRODUCT_budget'], record['support_mask']) == (3, 2, 150)
    proof = unpack_proof(3, 2, 150, record['packed_proof'])
    assert verify_reject(3, 2, 150, proof)
    bound, counts, power = mass_margin(3, 2, 150, proof)
    assert bound == F(1, 18432) and counts == {'total': 156, 'pure': 48, 'bad': 108} and power == 2
    assert record['scalar_unit_mass_margin'] == str(bound) and record['K'] == counts and record['L'] == power
    return proof, record


def audit():
    from sympy import Poly, symbols
    from types import SimpleNamespace
    from unittest.mock import patch
    # Independent symbolic evaluation at each context checks the complete
    # monomial expansion, including annihilators and repeated shared paths.
    symbolic_cases = 0
    for d, p in ((1, 0), (1, 1), (2, 0), (2, 1), (2, 2), (3, 1), (3, 2)):
        ms, _ = expand(d, p)
        width = groups(d, p)[-1][-1]+1
        variables = symbols(f'w0:{width}')
        actual = evaluate(d, p, variables)
        for context, expression in enumerate(actual):
            expected = {m.exponent: m.multiplicity for m in ms if m.support>>context & 1}
            assert dict(Poly(expression, *variables).terms()) == expected
            symbolic_cases += 1

    rng = random.Random(20260911)
    arithmetic_cases = 60
    for _ in range(arithmetic_cases):
        d, p = rng.choice(((2, 1), (2, 2), (3, 2)))
        ms, _ = expand(d, p)
        width = groups(d, p)[-1][-1]+1
        w = tuple(rng.randrange(-3, 5) for _ in range(width))
        tropical = leading(d, p, w)
        coefficients = tuple(F(1, 2)**v for v in w)
        native = evaluate(d, p, coefficients)
        for x, value in enumerate(native):
            terms = [(dot(m.exponent, w), m.multiplicity) for m in ms if m.support>>x & 1]
            minimum = min(v for v, _ in terms)
            assert tropical[x] == (minimum, sum(c for v, c in terms if v == minimum))
            assert value == sum(c*F(1, 2)**v for v, c in terms)

    grid_counts = Counter()
    finite_vs_limit_disagreements = []
    for d, p in ((2, 0), (2, 1), (3, 0), (3, 1)):
        full = (1<<(2**d))-1
        unary = {full}
        for face in product((-1, 0, 1), repeat=d):
            zero = support_mask(d, lambda x: all(a == -1 or a == b for a, b in zip(face, x)))
            unary.add(full ^ zero)
        finite = unary if p == 0 else {a | (u & v) for a in unary for u in unary for v in unary}
        for mask in range(full+1):
            result = solve(d, p, mask, node_budget=1000)
            assert result['status'] != 'UNRESOLVED'
            in_closure = result['status'] == 'SUPPORT_IN_CLOSURE'
            if in_closure:
                assert verify_accept(d, p, mask, result['exponents'])
            else:
                assert verify_reject(d, p, mask, result['proof'])
            if in_closure != (mask in finite):
                finite_vs_limit_disagreements.append((d, p, mask))
            grid_counts[(d, p, result['status'])] += 1
    assert not finite_vs_limit_disagreements  # Audited small classes only, not a general closure theorem.

    # The preceding finite-support coincidence must fail for P=2: the known
    # support-border example is a required acceptance case.
    border = solve(4, 2, 8896, node_budget=100)
    assert border['status'] == 'SUPPORT_IN_CLOSURE'
    w = border['exponents']
    values = leading(4, 2, w)
    limit = tuple(c if order == 0 else 0 for order, c in values)
    assert support_mask(4, lambda x: (1-x[0])*x[1]*x[2]+x[0]*(1-x[2])*x[3]) == 8896
    total = evaluate(4, 2, (F(1),)*len(w))
    for epsilon in (F(1, 2), F(1, 8), F(1, 64)):
        actual = evaluate(4, 2, tuple(epsilon**v for v in w))
        assert all(0 <= value-f <= bound*epsilon for value, f, bound in zip(actual, limit, total))
    assert min(w) < 0  # Bounded coefficients cannot realize this support at P=2.

    # Matching support does not decide prescribed numerical mass values.
    assert verify_accept(2, 0, 15, (0, 0, 0, 0))
    nonadditive = (1, 2, 2, 1)
    assert nonadditive[0]+nonadditive[3] != nonadditive[1]+nonadditive[2]

    xor_mask = support_mask(4, lambda x: x[0] != x[1] or x[2] != x[3])
    excluded = solve(4, 1, xor_mask)
    assert excluded['status'] == 'SUPPORT_OUTSIDE_CLOSURE'
    parity_tree, parity_record = verified_parity_proof()
    parity_bound, _, _ = mass_margin(3, 2, 150, parity_tree)
    assert parity_bound/8 == F(1, 147456)
    assert parity_bound**2/256 == F(1, 86973087744)

    for x, y, z in cube(3):
        even = ((1-x)+y)*(x+(1-y))
        odd = ((1-x)+(1-y))*(x+y)
        assert even*odd == 0 and (even+(1-z))*(odd+z) == (x+y+z) % 2
    transfer_cases = 0
    for cap in map(F, (3, 4, 5, 8)):
        for index in range(13):
            q = 1/cap+F(index, 12)*(1-2/cap)
            lower = max(1/q, 1/(1-q))
            for normalizer in (lower, (lower+cap)/2, cap):
                m1, m0 = normalizer*q, normalizer*(1-q)
                assert m1 >= 1 and m0 >= 1 and m1+m0 <= cap
                for odd in (0, 1):
                    target = (1+(cap-2)*odd)/cap
                    assert abs(m1-1-(cap-2)*odd) <= cap**2*abs(q-target)
                    transfer_cases += 1

    forgeries = []
    forgeries.append(verify_accept(4, 2, 8896, tuple(abs(v) for v in w)))
    forgeries.append(verify_accept(4, 2, 8896, w[:-1]))
    forgeries.append(verify_accept(4, 2, 8896 ^ 1, w))
    forged = deepcopy(excluded['proof'])
    assert forged['kind'] == 'SPLIT'
    forged['children'].pop()
    forgeries.append(verify_reject(4, 1, xor_mask, forged))
    forged = deepcopy(excluded['proof'])
    node = forged
    while node['kind'] == 'SPLIT':
        node = node['children'][0][1]
    assert node['kind'] == 'FARKAS'
    node['positive'] = node['negative']  # Balanced, but no strict bad weight.
    forgeries.append(verify_reject(4, 1, xor_mask, forged))
    forgeries.append(verify_reject(4, 1, (1<<16)-1, excluded['proof']))
    forgeries.append(verify_reject(4, 2, xor_mask, excluded['proof']))
    assert not any(forgeries)
    assert solve(4, 2, 8896, node_budget=0)['status'] == 'UNRESOLVED'
    assert solve(4, 2, 8896, expansion_budget=0)['status'] == 'UNRESOLVED'
    for nonfinite in (float('nan'), float('inf')):
        def fake_success(objective, *args, **kwargs):
            return SimpleNamespace(success=True, x=[nonfinite]*len(objective))
        with patch('scipy.optimize.linprog', side_effect=fake_success):
            assert solve(2, 0, 15)['status'] == 'UNRESOLVED'

    return {'status': 'PASS',
            'scope': 'support of some scalar mass limit in the full static unary-source P-PRODUCT class',
            'independent_symbolic_context_expansions': symbolic_cases,
            'exact_arithmetic_and_leading_exponent_cases': arithmetic_cases,
            'small_support_grid_cases': sum(grid_counts.values()),
            'small_support_decisions': {f'd={d},P={p},{s}': n for (d, p, s), n in grid_counts.items()},
            'finite_vs_limit_support_disagreements_in_those_grids': len(finite_vs_limit_disagreements),
            'two_PRODUCT_border_support_accepted': True,
            'border_certificate_exponents': w, 'border_leading_mass': limit,
            'border_search_statistics': border['statistics'],
            'one_PRODUCT_two_XOR_rejection': tree_statistics(excluded['proof']),
            'two_PRODUCT_parity_rejection': tree_statistics(parity_tree),
            'stored_parity_proof_unique_nodes': len(parity_record['packed_proof']['nodes']),
            'parity_scalar_mass_margin': '1/18432',
            'parity_noise_one_quarter_cap_four_probability_margin': '1/147456',
            'parity_noise_one_quarter_cap_four_CE_gap': '1/86973087744',
            'exact_mass_to_conditional_transfer_cases': transfer_cases,
            'forged_certificates_rejected': len(forgeries), 'budget_UNRESOLVED_cases': 2,
            'nonfinite_LP_success_flags_return_UNRESOLVED': 2,
            'not_claimed': ['prescribed numerical mass from support membership',
                            'unlimited-work completion by every floating LP proposal',
                            'finite Boolean supports cover every mass limit',
                            'general full conditional closure, registered value/install/persistence or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--d', type=int, default=4)
    parser.add_argument('--products', type=int, default=1)
    parser.add_argument('--mask', type=int)
    parser.add_argument('--node-budget', type=int, default=5000)
    parser.add_argument('--audit', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--verify-parity-proof', action='store_true')
    args = parser.parse_args()
    if args.verify_parity_proof:
        tree, _ = verified_parity_proof()
        answer = {'status': 'VERIFIED_WITHOUT_LP', 'tree': tree_statistics(tree),
                  'scalar_mass_margin': str(mass_margin(3, 2, 150, tree)[0])}
    elif args.audit or args.write:
        answer = audit()
        if args.write:
            root = Path(__file__).resolve().parents[2]
            (root/'evidence/minimal/FP_PRODUCT_SUPPORT_CLOSURE_AUDIT.json').write_text(
                json.dumps(answer, indent=2)+'\n', encoding='utf-8')
    else:
        target = args.mask if args.mask is not None else support_mask(4, lambda x: x[0] != x[1] or x[2] != x[3])
        answer = solve(args.d, args.products, target, node_budget=args.node_budget)
    if 'proof' in answer:
        answer['proof_counts'] = tree_statistics(answer['proof'])
        del answer['proof']
    print(json.dumps(answer, indent=2, default=str))
