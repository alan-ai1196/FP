"""Exact profile-gradient and outward-enclosure audit; float64 is observational."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json

CELLS = tuple(product((0, 1), repeat=2))
GAP = F(1, 1568)


def direct_products(parameters, x, z):
    a, b = parameters
    return (1+a*x*z, 1+b*x*(1-z)), ((F(x*z), F(0)), (F(0), F(x*(1-z))))


def factored_product(parameters, x, z):
    a, b, c, d, e, u, v = parameters
    left, right = a*(1-x)+b*z, c*x+d*(1-z)
    h = left*right
    return (1+e*h, 1+u*x+v*(1-z)), (
        (e*right*(1-x), e*right*z, e*left*x, e*left*(1-z), h, F(0), F(0)),
        (F(0), F(0), F(0), F(0), F(0), F(x), F(1-z)))


def profile_gradient(realization, parameters, successes=(2, 2, 3, 1)):
    gradient = [F(0)]*len(parameters)
    for (x, z), n1 in zip(CELLS, successes):
        mass, derivatives = realization(parameters, x, z)
        n0 = 4-n1
        for k in range(len(parameters)):
            gradient[k] += (4*(derivatives[0][k]+derivatives[1][k])/sum(mass)
                            -n0*derivatives[0][k]/mass[0]-n1*derivatives[1][k]/mass[1])/16
    return tuple(gradient)


def step(value):
    return value+(2-value)/((value+1)*(value+2))


def floor_dyadic(value, bits):
    scale = 1 << bits
    return F(value.numerator*scale//value.denominator, scale)


def ceil_dyadic(value, bits):
    return -floor_dyadic(-value, bits)


def loss_upper(lower_parameter):
    q = (1+lower_parameter)/(2+lower_parameter)
    return F(8, 3)*(F(3, 4)-q)**2


def audit():
    gradient_cases = 0
    for a, b in product((F(0), F(1), F(7, 6), F(2)), repeat=2):
        actual = profile_gradient(direct_products, (a, b))
        expected = tuple((v-2)/(16*(v+1)*(v+2)) for v in (a, b))
        assert actual == expected
        gradient_cases += 1
    zero_cases = 0
    for successes in product(range(5), repeat=4):
        for u, v in ((F(0), F(0)), (F(1, 3), F(5, 3)), (F(3), F(2))):
            parameters = (F(0),)*5+(u, v)
            gradient = profile_gradient(factored_product, parameters, successes)
            assert gradient[:5] == (F(0),)*5
            assert tuple(max(F(0), p-16*g) for p, g in zip(parameters, gradient))[:5] == (F(0),)*5
            zero_cases += 1
    # This same parameterization really does contain the useful static witness.
    expressive = (F(1), F(1), F(3), F(5, 3), F(1), F(1, 3), F(5, 3))
    target = (F(1, 2), F(1, 2), F(3, 4), F(1, 4))
    for (x, z), p in zip(CELLS, target):
        mass, _ = factored_product(expressive, x, z)
        assert mass[1]/sum(mass) == p

    exact, exact_iterates = F(0), []
    for t in range(1, 9):
        gradient = profile_gradient(direct_products, (exact, exact))
        updated = max(F(0), exact-16*gradient[0])
        assert updated == step(exact) and gradient[0] == gradient[1]
        exact = updated
        assert 0 < exact < 2
        exact_iterates.append(exact)

    bits = 64
    lo = hi = F(1)
    reference = 1.0
    maximum_reference_difference = F(0)
    first_certificate = None
    for t in range(1, 33):
        if t > 1:
            lo, hi = floor_dyadic(step(lo), bits), min(F(2), ceil_dyadic(step(hi), bits))
            reference += (2-reference)/((reference+1)*(reference+2))
        assert 1 <= lo <= hi <= 2
        if t <= len(exact_iterates):
            assert lo <= exact_iterates[t-1] <= hi
        maximum_reference_difference = max(maximum_reference_difference,
                                           abs(F(reference)-lo), abs(F(reference)-hi))
        upper = loss_upper(lo)
        if upper < GAP and first_certificate is None:
            first_certificate = {'step': t, 'theta_lower': str(lo), 'theta_upper': str(hi),
                                 'excess_ce_upper': str(upper), 'strict_gap_to_entire_one_product_class': str(GAP-upper),
                                 'excess_ce_upper_float64_display': float(upper)}
    assert first_certificate['step'] == 13
    # Separate, preregistered finite-encoded learner; not an enclosure midpoint.
    encoded, encoded_certificate = F(0), None
    maximum_encoded_bits = 0
    for t in range(1, 33):
        previous = encoded
        encoded = floor_dyadic(step(encoded), 32)
        assert previous <= encoded < 2 and (encoded*(1 << 32)).denominator == 1
        maximum_encoded_bits = max(maximum_encoded_bits, int(encoded*(1 << 32)).bit_length())
        if t <= len(exact_iterates):
            assert 0 <= exact_iterates[t-1]-encoded <= F(t-1, 1 << 32)
        upper = loss_upper(encoded)
        if upper < GAP and encoded_certificate is None:
            encoded_certificate = {'step': t, 'coefficient': str(encoded),
                                   'excess_ce_upper': str(upper),
                                   'strict_gap_to_entire_one_product_class': str(GAP-upper)}
    assert encoded_certificate['step'] == 13 and maximum_encoded_bits <= 33
    analytic = F(1, 54)*F(11, 12)**40
    assert analytic < GAP
    assert maximum_reference_difference < F(1, 10**12)
    return {
        'status': 'PASS', 'scope': 'registered zero-init projected full-batch CE gradient, step size 16; fixed 16-label profile',
        'profile_class_one_counts': [2, 2, 3, 1], 'labels_per_context': 4,
        'independent_two_slot_gradient_identities_checked': gradient_cases,
        'dormant_face_gradient_cases': zero_cases,
        'first_eight_iterations_checked_with_unrounded_rationals': True,
        'eighth_iterate_numerator_bits': exact_iterates[-1].numerator.bit_length(),
        'outward_enclosure_bits': bits,
        'separately_registered_dyadic_learner': {'fraction_bits': 32, 'commit_rounding': 'downwards',
                                              'maximum_coefficient_integer_bits': maximum_encoded_bits,
                                              'first_certificate': encoded_certificate},
        'first_step_certified_by_this_KL_bound': first_certificate,
        'profile_observation_evaluations_for_certificate': 13*16,
        'unique_profile_labels': 16, 'backward_update_passes': 13,
        'independent_analytic_21_step_excess_ce_upper': str(analytic),
        'normalizer_cap_along_entire_exact_trajectory': 4,
        'max_float64_difference_from_exact_trajectory_enclosure': float(maximum_reference_difference),
        'not_claimed': ['13 is the minimal possible useful step count', 'all one-product graphs are unreachable',
                        'expressivity witness installed at initialization', 'profile labels are fresh persistence',
                        'unknown population identified by profile counts', 'complete Runtime or AMP bridge'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_VALUE_REACHABILITY_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
