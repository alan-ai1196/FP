"""Exact loss-discrepancy inequalities and noise-dependent finite-range loss rates."""
from fractions import Fraction as F
from itertools import product
from math import comb, isqrt
from pathlib import Path
import argparse
import json
import random

from normalizer_chord_audit import log_bounds
from unary_sum_parity_audit import cube, interval_sum


def logs(value):
    return log_bounds(F(value), bits=72, terms=32)


def entropy(p):
    return interval_sum((-v, logs(v)) for v in (p, 1-p) if v)


def envelope(d, eta):
    return interval_sum(((1-F(2, 2**d), logs(2)), (F(2, 2**d), entropy(eta))))


def subtract(a, b):
    return a[0]-b[1], a[1]-b[0]


def beta(d, cap):
    cap = F(cap)
    assert d >= 2 and cap >= 2
    result = F(1)
    for j in range(1, d):
        result *= j*(cap-2)/(d-1+j*(cap-2))
    return result


def finite_noise_lower(d, eta, cap):
    effective_noise = (1-(1-2*eta)*beta(d, cap))/2
    return interval_sum(((1-F(2, 2**d), logs(2)), (F(2, 2**d), entropy(effective_noise))))


def rational_sqrt_bounds(v, bits=64):
    v = F(v)
    scale = 2**bits
    root = isqrt(v.numerator*scale*scale//v.denominator)
    lo, hi = F(root, scale), F(root+1, scale)
    assert lo*lo <= v <= hi*hi
    return lo, hi


def deterministic_gap_lower(d, cap):
    factor = (d-1)*sum((F(1, j) for j in range(1, d)), F(0))
    lo, hi = rational_sqrt_bounds(1+cap/factor)
    return F(2, 2**d)*logs(1+1/hi)[0], F(2, 2**d)*logs(1+1/lo)[1]


def mass_loss(d, eta, masses):
    _, chi = cube(d)
    terms = []
    for sign, (a, b) in zip(chi, masses):
        correct = (a if sign == 1 else b)/(a+b)
        terms.append((-F(1-eta, 2**d), logs(correct)))
        if eta:
            terms.append((-F(eta, 2**d), logs(1-correct)))
    return interval_sum(terms)


def audit():
    rng = random.Random(20260909)
    likelihood_cases = contraction_cases = 0
    for d in range(2, 7):
        xs, chi = cube(d)
        for _ in range(60):
            weights = tuple(tuple(tuple(F(rng.randrange(8), 3) for _ in range(2))
                                  for _ in range(d)) for _ in range(2))
            mass = tuple(tuple(1+sum(weights[y][i][bit] for i, bit in enumerate(x))
                               for y in range(2)) for x in xs)
            q = tuple(b/(a+b) for a, b in mass)
            discrepancy = abs(sum(sign*v for sign, v in zip(chi, q)))
            assert discrepancy <= max(q)-min(q)
            cap = max(a+b for a, b in mass)
            contraction = beta(d, cap)
            ratios = tuple(b/a for a, b in mass)
            log_contrast = interval_sum((sign, logs(r)) for sign, r in zip(chi, ratios))
            if min(ratios) != max(ratios):
                assert max(abs(v) for v in log_contrast) < contraction*logs(max(ratios)/min(ratios))[0]
            for t in (F(0), F(1, 3), F(1)):
                velocities = tuple((b-a)/((1-t)*a+t*b) for a, b in mass)
                assert abs(sum(sign*v for sign, v in zip(chi, velocities))) <= contraction*(max(velocities)-min(velocities))
                contraction_cases += 1
            correct_product = wrong_product = F(1)
            for sign, probability in zip(chi, q):
                correct = 1-probability if sign == 1 else probability
                correct_product *= correct
                wrong_product *= 1-correct
            for eta in (F(0), F(1, 10), F(1, 4), F(2, 5)):
                a, b = eta.numerator, eta.denominator
                lhs = correct_product**(b-a)*wrong_product**a
                r = (1+discrepancy)/2
                rhs = F(2)**(-(2**d-2)*b)*r**(2*(b-a))*(1-r)**(2*a)
                assert lhs <= rhs
                actual = mass_loss(d, eta, mass)
                contracted_lower = finite_noise_lower(d, eta, cap)
                assert actual[0] >= contracted_lower[1]
                likelihood_cases += 1

    # The binomial cancellation driving the sharp witness leading terms.
    for m in range(1, 33):
        harmonic = sum((F(1, j) for j in range(1, m+1)), F(0))
        assert sum((F((-1)**(s-1)*comb(m, s), s) for s in range(1, m+1)), F(0)) == harmonic
    assert beta(3, 2) == 0
    assert finite_noise_lower(3, F(1, 4), F(2)) == logs(2)

    deterministic_rows = []
    noisy_rows = []
    for d in (2, 3, 5, 8):
        xs, _ = cube(d)
        m, ncontexts = d-1, 2**d
        factor = m*sum((F(1, j) for j in range(1, d)), F(0))
        for n in (10, 100, 1000, 10000):
            k, u = F(n), factor*n*n/(2*m)
            cap = 2+k+2*m*u
            mass = tuple(tuple(1+k*int(y == x[0])+u*sum(x[1:]) for y in range(2)) for x in xs)
            assert min(min(row) for row in mass) >= 1 and max(sum(row) for row in mass) == cap
            gap = subtract(mass_loss(d, F(0), mass), envelope(d, F(0)))
            lower = deterministic_gap_lower(d, cap)
            assert 0 < lower[0] <= lower[1] <= gap[0]
            scaled = tuple(v*n for v in gap)
            if n == 10000:
                assert max(abs(v-F(4, ncontexts)) for v in scaled) < F(1, 10000)
            deterministic_rows.append({'bits': d, 'n': n, 'exact_cap': str(cap),
                                       'n_times_witness_gap_display': [float(v) for v in scaled],
                                       'proved_witness_limit': str(F(4, ncontexts)),
                                       'n_times_lower_bound_display': [float(v*n) for v in lower],
                                       'proved_lower_limit': str(F(2, ncontexts))})
        for eta in (F(1, 10), F(1, 4), F(2, 5)):
            lam, signal = 1/eta, 1-2*eta
            lower_constant = interval_sum(((signal*factor/ncontexts, logs((1-eta)/eta)),))
            witness_constant = 2*signal*signal*lam*factor/ncontexts
            for multiplier in (100, 10000, 1000000):
                cap = lam*multiplier
                u = (cap-lam)/(2*m)
                mass = tuple(tuple(lam*((1-eta, eta) if x[0] == 0 else (eta, 1-eta))[y]
                                   +u*sum(x[1:]) for y in range(2)) for x in xs)
                assert min(min(row) for row in mass) >= 1 and max(sum(row) for row in mass) == cap
                for x, row in zip(xs, mass):
                    if not sum(x[1:]):
                        assert row[1]/sum(row) == (eta if x[0] == 0 else 1-eta)
                gap = subtract(mass_loss(d, eta, mass), envelope(d, eta))
                lower = subtract(finite_noise_lower(d, eta, cap), envelope(d, eta))
                assert 0 < lower[0] <= lower[1] <= gap[0]
                assert gap[1] <= signal*lam*m/(cap-lam)
                scaled = tuple(cap*v for v in gap)
                scaled_lower = tuple(cap*v for v in lower)
                if multiplier == 1000000:
                    assert max(abs(v-witness_constant) for v in scaled) < F(1, 10000)
                    assert max(abs(a-b) for a in scaled_lower for b in lower_constant) < F(1, 10000)
                    noisy_rows.append({'bits': d, 'noise': str(eta), 'exact_cap': str(cap),
                                       'R_times_witness_gap_display': [float(v) for v in scaled],
                                       'proved_witness_limit': str(witness_constant),
                                       'R_times_lower_bound_display': [float(v) for v in scaled_lower],
                                       'proved_lower_limit_display': [float(v) for v in lower_constant]})
    return {'status': 'PASS', 'scope': 'complete static unary-SUM class; uniform noisy parity; base one; final range cap',
            'exact_loss_discrepancy_likelihood_checks': likelihood_cases,
            'exact_interpolation_contraction_checks': contraction_cases,
            'outward_log_contraction_mass_pairs': contraction_cases//3,
            'exact_binomial_harmonic_identities': 32,
            'selected_deterministic_witnesses': [row for row in deterministic_rows if row['n'] in (10, 10000)],
            'selected_positive_noise_witnesses': [row for row in noisy_rows if row['noise'] == '1/4' or row['bits'] == 3],
            'all_native_witnesses_checked': 52,
            'proved_rate_exponents': {'eta_zero': 'Delta_R = Theta(R^-1/2)',
                                     'fixed_eta_between_zero_and_half': 'Delta_R = Theta(R^-1)'},
            'not_claimed': ['sharp leading CE constants', 'uniform noise/range crossover',
                            'discrepancy optimizer minimizes CE', 'physical or registered value/install evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_SUM_PARITY_LOSS_RATE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
