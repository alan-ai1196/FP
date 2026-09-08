"""Exact parity discrepancy, log-ratio oscillation, and sharp unary-SUM loss audits."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from normalizer_chord_audit import log_bounds


def cube(d):
    vertices = tuple(product((0, 1), repeat=d))
    return vertices, tuple((-1)**sum(x) for x in vertices)


def interval_sum(terms):
    lo = hi = F(0)
    for weight, (a, b) in terms:
        lo += weight*(a if weight >= 0 else b)
        hi += weight*(b if weight >= 0 else a)
    return lo, hi


def audit():
    # These rational sums independently check the signs/identities established
    # by the integral proof, including every zero-slope degeneracy in this grid.
    denominator_cases = 0
    for d in range(2, 7):
        xs, chi = cube(d)
        for c in (F(1), F(2)):
            for slopes in product(range(3), repeat=d):
                inverse = tuple(1/(c+sum(t*b for t, b in zip(slopes, x))) for x in xs)
                integral = sum(s*v for s, v in zip(chi, inverse))
                negative_moments = tuple(-sum(s*v*x[i] for s, v, x in zip(chi, inverse, xs)) for i in range(d))
                assert integral >= 0 and min(negative_moments) >= 0
                assert c*integral == sum(t*j for t, j in zip(slopes, negative_moments))
                assert all(c*(integral+j) < 1 for j in negative_moments)
                denominator_cases += 1

    rng = random.Random(20260908)
    random_cases = 0
    algebraic_cases = 0
    for d in range(2, 9):
        xs, chi = cube(d)
        for _ in range(120):
            weights = tuple(tuple(tuple(F(rng.randrange(10), 3) for _ in range(2))
                                  for _ in range(d)) for _ in range(2))
            mass = tuple(tuple(1+sum(weights[y][i][bit] for i, bit in enumerate(x))
                               for y in range(2)) for x in xs)
            q = tuple(b/(a+b) for a, b in mass)
            assert abs(sum(s*v for s, v in zip(chi, q))) < 1

            ratios = tuple(b/a for a, b in mass)
            contrast = interval_sum((s, log_bounds(r)) for s, r in zip(chi, ratios))
            oscillation = log_bounds(max(ratios)/min(ratios))
            if max(ratios) == min(ratios):
                assert sum(chi) == 0
            else:
                assert max(abs(v) for v in contrast) < oscillation[0]

            # Audit the interpolation step using affine masses at rational t.
            for t in (F(0), F(1, 3), F(1)):
                velocity = tuple((b-a)/((1-t)*a+t*b) for a, b in mass)
                span = max(velocity)-min(velocity)
                signed = abs(sum(s*v for s, v in zip(chi, velocity)))
                assert signed < span if span else signed == 0

            # No logarithms or irrational square roots in this equivalent
            # all-noise likelihood inequality.
            u = v = total = F(1)
            for s, (a, b) in zip(chi, mass):
                u *= a if s == 1 else b
                v *= b if s == 1 else a
                total *= a+b
            factor = 2**(len(xs)-2)
            residual = total-factor*(u+v)
            assert residual >= 0 and residual*residual >= 4*factor*factor*u*v
            algebraic_cases += 1
            random_cases += 1

    witness_rows = []
    witness_cases = 0
    xs4, chi4 = cube(4)
    threshold_table = tuple(F(3, 4) if sum(x) <= 2 else F(1, 4) for x in xs4)
    assert sum(s*q for s, q in zip(chi4, threshold_table)) == F(3, 2)
    # A fixed-base native ratio approaches the sharp discrepancy constant.
    for d in range(2, 9):
        xs, chi = cube(d)
        previous = F(0)
        for k in (10, 100, 1000):
            q = tuple(F(k, k+1+k*k*sum(x)) for x in xs)
            discrepancy = sum(s*v for s, v in zip(chi, q))
            formula = F(k, k+1)
            for j in range(1, d+1):
                formula *= F(j*k*k, k+1+j*k*k)
            assert discrepancy == formula and previous < discrepancy < 1
            previous = discrepancy
    for d in range(2, 9):
        xs, chi = cube(d)
        n = len(xs)
        for eta in (F(0), F(1, 10), F(1, 4), F(2, 5)):
            entropy = interval_sum((-p, log_bounds(p)) for p in (eta, 1-eta) if p)
            envelope = interval_sum(((1-F(2, n), log_bounds(F(2))), (F(2, n), entropy)))
            for k in (10, 100, 1000):
                masses = tuple(tuple(1+k*((1-eta, eta) if x[0] == 0 else (eta, 1-eta))[y]
                                     +k*k*sum(x[1:]) for y in range(2)) for x in xs)
                terms = []
                likelihood = F(1)
                for s, (a, b) in zip(chi, masses):
                    target = (1-eta, eta) if s == 1 else (eta, 1-eta)
                    for p, mass in zip(target, (a, b)):
                        if p:
                            probability = mass/(a+b)
                            terms.append((-p/F(n), log_bounds(probability)))
                            likelihood *= probability**int(p*eta.denominator)
                loss = interval_sum(terms)
                gap = loss[0]-envelope[1], loss[1]-envelope[0]
                assert 0 < gap[0] <= gap[1] <= F(2, k)
                assert max(a+b for a, b in masses) == 2+k+2*(d-1)*k*k
                count0, count1 = eta.numerator, eta.denominator-eta.numerator
                supremum = (eta**count0*(1-eta)**count1)**2/F(2)**((n-2)*eta.denominator)
                assert likelihood < supremum
                if d in (2, 3, 8) and eta in (F(0), F(1, 4)) and k == 1000:
                    witness_rows.append({'bits': d, 'noise': str(eta), 'K': k,
                                         'proved_infimum_display': [float(v) for v in envelope],
                                         'certified_finite_excess_display': [float(v) for v in gap],
                                         'exact_peak_normalizer': 2+k+2*(d-1)*k*k})
                witness_cases += 1

    return {'status': 'PASS', 'scope': 'static positive affine binary masses; uniform parity task; no internal normalization or recurrence',
            'exact_denominator_grid_cases': denominator_cases,
            'rational_normalized_discrepancy_and_outward_log_oscillation_cases': random_cases,
            'exact_algebraic_all_noise_inequality_cases': algebraic_cases,
            'exact_native_finite_witness_cases': witness_cases,
            'linearly_separable_threshold_counterexample_discrepancy': '3/2 > 1',
            'fixed_base_discrepancy_sharpness_constructions': 21,
            'sharp_envelope': 'log(2)-2^(1-d)*(log(2)-H(eta))',
            'finite_attainment_for_d_ge_2_and_eta_lt_half': False,
            'finite_construction_excess_upper': '2/K',
            'finite_construction_peak_normalizer': '2+K+2*(d-1)*K^2',
            'selected_finite_witnesses': witness_rows,
            'proof_status': 'analytic lemmas prove the all-dimension result; finite audits check algebra and witnesses',
            'not_claimed': ['nonuniform context envelope', 'sharp finite-range envelope',
                            'registered value/acquisition/build/install evidence', 'AMP or Compiler freeze']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_UNARY_SUM_PARITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
