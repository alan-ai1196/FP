"""Guarded positive-mass box bounds, without persistence authority.

Runtime must supply its own complete aligned domain enclosures before the
next context. These arithmetic functions attest to neither coverage nor
lineage, and never change a registered bet or mean-null.
"""
from fractions import Fraction as F

from .core import ContractError, natural
from .numerics import compare_exact, compare_exact_work
from .semantics import _guard, _operation


def mass_box_work(rows, labels):
    """Conservative primitive charge; integer/host limits remain separate."""
    natural(rows, 'complete mass-box row count', positive=True)
    natural(labels, 'complete mass-box label count', positive=True)
    return 128+rows*(64+labels*(128+8*compare_exact_work()))


def probability_box(masses, *, bit_limit):
    if type(masses) is not tuple or not masses:
        raise ContractError('nonempty ordered mass intervals required')
    add = lambda a, b: _operation(a, b, multiply=False, bit_limit=bit_limit)
    mul = lambda a, b: _operation(a, b, multiply=True, bit_limit=bit_limit)
    lower_sum, upper_sum = F(0), F(0)
    for interval in masses:
        if (type(interval) is not tuple or len(interval) != 2
                or any(type(v) is not F for v in interval)):
            raise ContractError('exact lower/upper mass pairs required')
        lower, upper = interval
        _guard(lower, upper, bit_limit=bit_limit)
        if lower <= 0 or compare_exact(lower, upper, bit_limit=bit_limit) > 0:
            raise ContractError('positive ordered mass intervals required')
        lower_sum, upper_sum = add(lower_sum, lower), add(upper_sum, upper)
    probabilities = []
    for lower, upper in masses:
        lower_denominator = add(lower, add(upper_sum, -upper))
        upper_denominator = add(upper, add(lower_sum, -lower))
        probabilities.append((mul(lower, F(lower_denominator.denominator, lower_denominator.numerator)),
                              mul(upper, F(upper_denominator.denominator, upper_denominator.numerator))))
    return tuple(probabilities)


def paired_mass_ratio_bound(base_rows, candidate_rows, *, bit_limit):
    if (type(base_rows) is not tuple or type(candidate_rows) is not tuple
            or not base_rows or len(base_rows) != len(candidate_rows)
            or any(type(row) is not tuple for row in base_rows+candidate_rows)):
        raise ContractError('complete aligned nonempty mass-box domains required')
    maximum = F(1)
    labels = len(base_rows[0])
    for base, candidate in zip(base_rows, candidate_rows):
        if len(base) != labels or len(candidate) != labels:
            raise ContractError('paired mass boxes changed the registered label interface')
        base_probabilities = probability_box(base, bit_limit=bit_limit)
        candidate_probabilities = probability_box(candidate, bit_limit=bit_limit)
        for (base_lower, base_upper), (candidate_lower, candidate_upper) in zip(
                base_probabilities, candidate_probabilities):
            for numerator, denominator in ((candidate_upper, base_lower), (base_upper, candidate_lower)):
                ratio = _operation(numerator, F(denominator.denominator, denominator.numerator),
                                   multiply=True, bit_limit=bit_limit)
                if compare_exact(ratio, maximum, bit_limit=bit_limit) > 0:
                    maximum = ratio
    return maximum
