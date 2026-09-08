"""Exact full-class finite-range parity reduction, polynomial certificate and native witnesses."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random

from normalizer_chord_audit import log_bounds
from unary_sum_parity_audit import cube, interval_sum


def capacity_value(d, cap, c, t):
    assert all(type(v) in (int, F) for v in (cap, c, t))
    cap, c, t = map(F, (cap, c, t))
    assert d >= 2 and cap >= c >= 2 and 0 <= t <= (cap-c)/d
    u = (cap-c-t)/(d-1)
    first, second = (c-1)/c, 1/(c+t)
    for j in range(1, d):
        first *= j*u/(c+j*u)
        second *= j*u/(c+t+j*u)
    return first-second


def native_masses(d, cap, c, t):
    assert all(type(v) in (int, F) for v in (cap, c, t))
    cap, c, t = map(F, (cap, c, t))
    u = (cap-c-t)/(d-1)
    xs, _ = cube(d)
    return tuple((1+(c-2+t)*x[0]+u*sum(x[1:]), 1+(c-2)*(1-x[0])) for x in xs)


def symbolic_range_four_certificate():
    # Exact rational polynomial reconstruction, not numerical SOS fitting.
    import sympy as s
    c, t, a, b, g = s.symbols('c t a b g')
    u = (4-c-t)/2
    value = (c-1)/c*u/(c+u)*2*u/(c+2*u)-1/(c+t)*u/(c+t+u)*2*u/(c+t+2*u)
    denominator = 40*c*(c+t)*(t-4)*(-c+t-4)*(c+t+4)
    numerator = s.cancel(denominator*(s.Rational(1, 40)-value))
    assert s.Poly(numerator, c, t).total_degree() == 5
    total = a+b+g
    polynomial = s.Poly(s.cancel(numerator.subs({c: 2+2*a/total, t: 2*b/(3*total)})*total**5), a, b, g)
    asserted = (4096*a**5+14336*a**4*(b+g)
                +a**3*(15360*b*b+26112*b*g+9472*g*g)
                +a*a*(s.Rational(51712, 9)*b**3+s.Rational(34304, 3)*b*b*g+5632*b*g*g+512*g**3)
                +a*(s.Rational(35840, 81)*b**4+s.Rational(1408, 27)*b**3*g-1216*b*b*g*g
                    -s.Rational(704, 3)*b*g**3+576*g**4)
                +s.Rational(3904, 9)*b**3*g*g+s.Rational(13024, 9)*b*b*g**3
                +s.Rational(4768, 3)*b*g**4+576*g**5)
    assert polynomial == s.Poly(asserted, a, b, g)
    squares = 608*b*b*g*(a-g)**2+s.Rational(352, 3)*b*g*g*(a-g)**2
    remainder = s.Poly(polynomial.as_expr()-squares, a, b, g)
    assert all(v >= 0 for v in remainder.coeffs())
    assert polynomial.as_expr().subs({a: 0, g: 0}) == 0
    return {'rational_identity': 'PASS', 'degree': 5, 'original_nonzero_monomials': len(polynomial.terms()),
            'positive_square_multipliers': ['608 b^2 g', '(352/3) b g^2'],
            'remaining_coefficients_nonnegative': True,
            'remaining_nonzero_monomials': len(remainder.terms()),
            'global_maximum': '1/40', 'attained_c_t_u': ['2', '2/3', '2/3']}


def audit():
    rng = random.Random(20260908)
    random_cases = 0
    for d in range(2, 8):
        xs, chi = cube(d)
        for _ in range(160):
            weights = tuple(tuple(tuple(F(rng.randrange(8), 3) for _ in range(2))
                                  for _ in range(d)) for _ in range(2))
            mass = tuple(tuple(1+sum(weights[y][i][bit] for i, bit in enumerate(x))
                               for y in range(2)) for x in xs)
            totals = tuple(a+b for a, b in mass)
            c, cap = min(totals), max(totals)
            slopes = tuple(abs(sum(weights[y][i][1]-weights[y][i][0] for y in range(2))) for i in range(d))
            assert c+sum(slopes) == cap
            discrepancy = abs(sum(sign*b/(a+b) for sign, (a, b) in zip(chi, mass)))
            # Original denominator's exact best numerator, after orientation.
            oriented = tuple(c+sum(t*bit for t, bit in zip(slopes, x)) for x in xs)
            integral = sum(sign/den for sign, den in zip(chi, oriented))
            moments = tuple(-sum(sign*x[i]/den for sign, x, den in zip(chi, xs, oriented)) for i in range(d))
            fixed_upper = (c-1)*integral+(c-2)*max(moments)
            chosen = min(range(d), key=lambda i: slopes[i])
            assert moments[chosen] == max(moments)
            attained = sum(sign*(c-1-(c-2)*x[chosen])/den for sign, x, den in zip(chi, xs, oriented))
            assert attained == fixed_upper >= discrepancy
            reduced = capacity_value(d, cap, c, min(slopes))
            assert reduced >= fixed_upper
            witness = native_masses(d, cap, c, min(slopes))
            assert all(min(row) >= 1 for row in witness)
            assert max(sum(row) for row in witness) == cap
            assert sum(sign*b/(a+b) for sign, (a, b) in zip(chi, witness)) == reduced
            harmonic_factor = (d-1)*sum((F(1, j) for j in range(1, d)), F(0))
            assert cap*(1-reduced)**2 >= 4*harmonic_factor*reduced
            random_cases += 1

    grid_cases = 0
    for d in range(2, 8):
        harmonic_factor = (d-1)*sum((F(1, j) for j in range(1, d)), F(0))
        for cap in (F(2), F(4), F(10), F(100)):
            for i, j in product(range(9), repeat=2):
                c = 2+(cap-2)*F(i, 8)
                t = (cap-c)*F(j, 8*d)
                value = capacity_value(d, cap, c, t)
                assert 0 <= value < 1
                assert cap*(1-value)**2 >= 4*harmonic_factor*value
                if d == 3 and cap == 4:
                    assert value <= F(1, 40)
                grid_cases += 1

    certificate = symbolic_range_four_certificate()
    asymptotic_rows = []
    for d in (2, 3, 5, 8):
        factor = (d-1)*sum((F(1, j) for j in range(1, d)), F(0))
        for n in (10, 100, 1000, 10000):
            cap, c, t = factor*n**4, F(n*n), F(n**3)
            value = capacity_value(d, cap, c, t)
            assert cap*(1-value)**2 >= 4*factor*value
            scaled = n*n*(1-value)
            if n == 10000:
                assert abs(scaled-2) < F(1, 1000)
            asymptotic_rows.append({'bits': d, 'n': n, 'exact_A': str(factor),
                                    'n_squared_times_deficit_display': float(scaled),
                                    'proved_limit': 2})

    # Four real native products, with compound SUM parents and one final readout.
    xs, chi = cube(3)
    for (x, z, w), sign in zip(xs, chi):
        even2 = ((1-x)+z)*(x+(1-z))
        odd2 = ((1-x)+(1-z))*(x+z)
        even3 = (even2+w)*(odd2+(1-w))
        odd3 = (even2+(1-w))*(odd2+w)
        assert even3 == int(sign == 1) and odd3 == int(sign == -1)
        mass = (1+2*even3, 1+2*odd3)
        assert sum(mass) == 4 and F(mass[int(sign == -1)], 4) == F(3, 4)
    ce_lower = interval_sum(((-F(3, 4), log_bounds(F(161, 320))),
                             (-F(1, 4), log_bounds(F(159, 320)))))
    bayes = interval_sum(((-F(3, 4), log_bounds(F(3, 4))),
                          (-F(1, 4), log_bounds(F(1, 4)))))
    gap = ce_lower[0]-bayes[1], ce_lower[1]-bayes[0]
    assert gap[0] > F(127, 1000)
    return {'status': 'PASS', 'scope': 'complete static binary unary-SUM class; base one; final-normalizer cap',
            'random_exact_fixed_denominator_optimization_and_symmetrization_cases': random_cases,
            'exact_reduced_domain_grid_cases': grid_cases,
            'range_four_three_input_global_certificate': certificate,
            'universal_range_law': 'R*(1-D)^2 >= 4*(d-1)*H_(d-1)*D',
            'sharp_fixed_dimension_asymptotic': 'sqrt(R)*(1-D_d(R)) -> 2*sqrt((d-1)*H_(d-1))',
            'rational_asymptotic_witness_sequence': asymptotic_rows,
            'range_four_noise_one_quarter_three_input_comparison': {
                'all_SUM_CE_lower_display': [float(v) for v in ce_lower],
                'four_PRODUCT_Bayes_CE_display': [float(v) for v in bayes],
                'certified_all_SUM_gap_display': [float(v) for v in gap],
                'proved_gap_exceeds': '127/1000'},
            'not_claimed': ['discrepancy maximizer minimizes CE', 'global certificate from numerical termination',
                            'sharp four-PRODUCT count', 'uniform joint dimension/range asymptotic',
                            'registered value/build/install or AMP evidence']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_SUM_PARITY_RANGE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
