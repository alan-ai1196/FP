"""Exact/float64 research audit, not a Compiler completion or install API.

Default: standard-library exact audit. --optimize additionally runs independent
float64 multistart searches (NumPy/SciPy); these are observations, not proofs.
--write saves only the compact audit result in the canonical evidence directory.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import product
import json
from math import log, prod
from pathlib import Path

CELLS = ((0, 0), (0, 1), (1, 0), (1, 1))
DIAGONAL, OFF_DIAGONAL = (0, 3), (1, 2)
PAIRS = tuple(product(DIAGONAL, OFF_DIAGONAL))


def sum_probabilities(weights):
    """Four unary sources, two positive heads, fixed base (1,1)."""
    result = []
    for i, j in CELLS:
        masses = [1 + weights[2*i+y] + weights[4+2*j+y] for y in (0, 1)]
        result.append(F(masses[1], sum(masses)))
    return tuple(result)


def likelihood(probabilities, counts):
    # Counts are (class-0, class-1); zero-count endpoints use 0**0 == 1.
    return prod((1-p)**n0 * p**n1 for p, (n0, n1) in zip(probabilities, counts))


def closed_intersection(p):
    return max(min(p[i] for i in DIAGONAL), min(p[i] for i in OFF_DIAGONAL)) <= min(
        max(p[i] for i in DIAGONAL), max(p[i] for i in OFF_DIAGONAL))


def exact_sum_envelope(counts):
    """Solve only the continuous prediction-family closure of Theorem 2.

    The returned likelihood is a supremum; no reachability is inferred.
    """
    assert len(counts) == 4 and all(a >= 0 and b >= 0 and a+b > 0 for a, b in counts)
    targets = tuple(F(b, a+b) for a, b in counts)
    if closed_intersection(targets):
        return likelihood(targets, counts), (targets,), ()
    candidates = []
    for d, o in PAIRS:
        pooled = F(counts[d][1]+counts[o][1], sum(counts[d])+sum(counts[o]))
        p = list(targets)
        p[d] = p[o] = pooled
        assert closed_intersection(p)
        candidates.append((likelihood(p, counts), tuple(p), (d, o)))
    best = max(value for value, _, _ in candidates)
    return best, tuple(p for value, p, _ in candidates if value == best), tuple(
        pair for value, _, pair in candidates if value == best)


def finite_sum_representation(p):
    """Independent constructive converse of Theorem 1; exact rational weights."""
    if any(not 0 < v < 1 for v in p):
        return None
    dl, dh = sorted(p[i] for i in DIAGONAL)
    ol, oh = sorted(p[i] for i in OFF_DIAGONAL)

    def in_ri(v, lo, hi):
        return v == lo if lo == hi else lo < v < hi

    if dl == dh:
        common = dl
    elif ol == oh:
        common = ol
    elif max(dl, ol) < min(dh, oh):
        common = (max(dl, ol)+min(dh, oh))/2
    else:
        return None
    if not in_ri(common, dl, dh) or not in_ri(common, ol, oh):
        return None
    lam = F(1, 2) if p[0] == p[3] else (common-p[3])/(p[0]-p[3])
    mu = F(1, 2) if p[1] == p[2] else (common-p[2])/(p[1]-p[2])
    totals = (lam, mu, 1-mu, 1-lam)
    masses = [(t*(1-v), t*v) for t, v in zip(totals, p)]
    scale = 2/min(v for row in masses for v in row)
    weights = [F(0)]*8
    for y in (0, 1):
        a = [row[y]*scale-1 for row in masses]
        k = min(range(4), key=a.__getitem__)
        ir, jc = CELLS[k]
        for i in (0, 1):
            weights[2*i+y] = a[2*i+jc]
        for j in (0, 1):
            weights[4+2*j+y] = a[2*ir+j]-a[k]
    assert min(weights) >= 0
    assert sum_probabilities(weights) == tuple(p)
    return tuple(weights)


def ce(p, counts):
    n = sum(a+b for a, b in counts)
    return -sum((a*log(float(1-v)) if a else 0) + (b*log(float(v)) if b else 0)
                for v, (a, b) in zip(p, counts))/n


def exact_audit():
    datasets = {
        'deterministic_xor': ((1, 0), (0, 1), (0, 1), (1, 0)),
        'noise_one_quarter': ((3, 1), (1, 3), (1, 3), (3, 1)),
        'unequal_counts_and_noise': ((7, 1), (1, 5), (2, 9), (8, 3)),
        'overlapping_target_intervals': ((4, 1), (3, 2), (2, 3), (1, 4)),
    }
    envelopes = {name: exact_sum_envelope(c) for name, c in datasets.items()}
    grid_count, max_roundoff = 0, 0.0
    for weights in product(range(3), repeat=8):
        p = sum_probabilities(weights)
        q = tuple(1-v if i in DIAGONAL else v for i, v in enumerate(p))
        assert any(q[d]+q[o] <= 1 for d, o in PAIRS)
        assert prod(q) <= F(1, 4)
        for name, counts in datasets.items():
            assert likelihood(p, counts) <= envelopes[name][0]
        for i, j in CELLS:
            k = 2*i+j
            m0 = float(1+weights[2*i]+weights[4+2*j])
            m1 = float(1+weights[2*i+1]+weights[4+2*j+1])
            max_roundoff = max(max_roundoff, abs(m1/(m0+m1)-float(p[k])))
        grid_count += 1
    representable, boundary, separated = 0, 0, 0
    for p in product((F(1, 5), F(2, 5), F(3, 5), F(4, 5)), repeat=4):
        weights = finite_sum_representation(p)
        if weights is not None:
            representable += 1
            assert closed_intersection(p)
        elif closed_intersection(p):
            boundary += 1
        else:
            separated += 1
    # Endpoint-only touching is not finite attainment with positive masses.
    limiting = (F(1, 2), F(1, 2), F(3, 4), F(1, 4))
    assert closed_intersection(limiting) and finite_sum_representation(limiting) is None
    assert envelopes['deterministic_xor'][0] == F(1, 4)
    assert len(envelopes['deterministic_xor'][2]) == 4
    for name, (_, optimizers, _) in envelopes.items():
        for p in optimizers:
            assert likelihood(p, datasets[name]) == envelopes[name][0]

    # A native finite SUM graph strictly improves on unigram without PRODUCT.
    finite_sum = sum_probabilities((0, 2, 2, 0, 4, 4, 0, 0))
    finite_likelihood = likelihood(finite_sum, datasets['deterministic_xor'])
    assert F(1, 16) < finite_likelihood < F(1, 4)
    limiting_losses = []
    for a in (10, 100, 1000):
        p = sum_probabilities((0, a, a, 0, a*a, a*a, 0, 0))
        limiting_losses.append(ce(p, datasets['deterministic_xor']))
    assert all(a > b > log(2)/2 for a, b in zip(limiting_losses, limiting_losses[1:]))

    # Exact one-PRODUCT witness across rational odds, not just one lucky float.
    odds = (F(1), F(3, 2), F(2), F(3), F(9))
    for r in odds:
        p = []
        for x, z in CELLS:
            m0, m1 = r+2*r*(r*r-1)*x*z, 1+(r*r-1)*(x+z)
            q = (m0 if x == z else m1)/(m0+m1)
            assert q == r/(r+1)
            p.append(m1/(m0+m1))
        if r == 3:
            witness = tuple(p)
    assert likelihood(witness, datasets['deterministic_xor']) == F(81, 256) > F(1, 4)
    assert all(witness[i] == F(c[1], sum(c)) for i, c in enumerate(datasets['noise_one_quarter']))
    return {
        'status': 'PASS',
        'scope': 'static two-bit unary sources; arbitrary positive SUM DAG; base (1,1); one final normalization',
        'proof': 'theory/proofs/NORMALIZED_SUM_XOR.md',
        'exact_sum_weight_assignments': grid_count,
        'exact_likelihood_checks': grid_count*len(datasets),
        'rational_table_grid': {
            'total': representable+boundary+separated,
            'finite_representations_constructed': representable,
            'closure_only': boundary,
            'separated': separated,
        },
        'max_float64_probability_roundoff_on_integer_grid': max_roundoff,
        'deterministic_xor': {
            'unigram_ce': log(2),
            'sum_ce_infimum': log(2)/2,
            'sum_likelihood_supremum': '1/4',
            'finite_sum_beats_unigram_likelihood': str(finite_likelihood),
            'finite_sum_ce': ce(finite_sum, datasets['deterministic_xor']),
            'sum_approach_ce_A_10_100_1000_K_A_squared': limiting_losses,
            'one_product_integer_witness_likelihood': '81/256',
            'one_product_ce': log(F(4, 3)),
            'strict_forcing_gap_to_finite_witness': log(2)/2-log(F(4, 3)),
        },
        'one_product_rational_odds_checked': [str(r) for r in odds],
        'exact_weighted_envelopes': {
            name: {'likelihood_supremum': str(value),
                   'optimal_pool_pairs': pairs,
                   'infimum_ce_float64_display': -log(value)/sum(a+b for a, b in datasets[name])}
            for name, (value, _, pairs) in envelopes.items()
        },
        'not_claimed': ['finite attainment of every envelope', 'registered value reachability',
                        'resource/install feasibility', 'persistence', 'AMP bridge', 'Compiler freeze'],
    }


def float64_search():
    import numpy as np
    from scipy.optimize import minimize

    rng = np.random.default_rng(20260906)
    rows = []
    for d, eta in ((2, 0.0), (2, 0.01), (2, 0.1), (2, 0.25), (2, 0.4),
                   (3, 0.1), (4, 0.1), (5, 0.1)):
        bits = np.array(list(product((0, 1), repeat=d)))
        x = np.eye(2)[bits].reshape(len(bits), 2*d)
        labels = bits.sum(1) % 2
        targets = (1-2*eta)*np.eye(2)[labels]+eta

        def objective(z):
            weights = np.exp(z.reshape(2*d, 2))
            masses = 1.0+x@weights
            totals = masses.sum(1, keepdims=True)
            loss = (np.log(totals[:, 0])-(targets*np.log(masses)).sum(1)).mean()
            gradient = (x.T@(1/totals-targets/masses))*weights/len(bits)
            return loss, gradient.ravel()

        results = [minimize(objective, rng.normal(8, 5, 4*d), jac=True,
                            method='L-BFGS-B', bounds=[(-35, 35)]*(4*d),
                            options={'ftol': 1e-13, 'gtol': 1e-10, 'maxiter': 1500})
                   for _ in range(16)]
        best = min(results, key=lambda r: r.fun)
        h = 0 if eta == 0 else -eta*log(eta)-(1-eta)*log(1-eta)
        conjectured = log(2)-(log(2)-h)/(2**(d-1))
        rows.append({'bits': d, 'noise': eta, 'restarts': 16,
                     'best_ce': float(best.fun), 'successful_terminations': sum(bool(r.success) for r in results),
                     'comparison_value': conjectured,
                     'comparison_status': 'PROVED infimum; multi-input proof in UNARY_SUM_PARITY_ENVELOPE.md'})
    return {'arithmetic': 'float64', 'algorithm': 'bounded log-weight L-BFGS-B; fixed positive base retained',
            'seed': 20260906, 'results': rows,
            'scope': 'local numerical search, never a completeness or global-optimality certificate'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimize', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = exact_audit()
    if args.optimize:
        result['numerical_search'] = float64_search()
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_NORMALIZED_SUM_XOR_AUDIT.json').write_text(text, encoding='utf-8')
    print(text, end='')
