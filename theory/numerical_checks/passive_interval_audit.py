"""Finite-information structural audit; no persistence or install authority.

The probability theorem assumes the stated iid law. Seeded streams below are
algorithm fixtures, not empirical proofs of confidence coverage.
"""
from fractions import Fraction as F
from itertools import product
from math import isqrt
from pathlib import Path
import argparse
import json
import random

from normalized_sum_xor_audit import closed_intersection, finite_sum_representation

D, O = (0, 3), (1, 2)
ALPHA, K = F(1, 20), 4


def interval_certificate(intervals, weights=(F(1, 4),)*4):
    assert len(intervals) == 4 and len(weights) == 4 and min(weights) > 0 and sum(weights) == 1
    assert all(0 <= lo <= hi <= 1 for lo, hi in intervals)
    if max(intervals[d][1] for d in D) < min(intervals[o][0] for o in O):
        pairs = ((d, o) for d in D for o in O)
    elif max(intervals[o][1] for o in O) < min(intervals[d][0] for d in D):
        pairs = ((o, d) for d in D for o in O)
    else:
        return None
    return min(2*weights[a]*weights[b]/(weights[a]+weights[b])
               * (intervals[b][0]-intervals[a][1])**2 for a, b in pairs)


def radius(n):
    assert n >= 1
    threshold = 2*K*n*(n+1)/ALPHA
    integer_threshold = (threshold.numerator+threshold.denominator-1)//threshold.denominator
    k = (integer_threshold-1).bit_length()
    denominator = 1 << max(8, n.bit_length()+2)
    squared_ceiling = (k*denominator*denominator+2*n-1)//(2*n)
    numerator = isqrt(squared_ceiling)
    if numerator*numerator < squared_ceiling:
        numerator += 1
    r = F(numerator, denominator)
    assert 2*n*r*r >= k
    assert F(2, 1 << k) <= ALPHA/(K*n*(n+1))
    return r


def intervals_from_counts(counts):
    result = []
    for n, successes in counts:
        assert 0 <= successes <= n
        if n == 0:
            result.append((F(0), F(1)))
        else:
            mean, r = F(successes, n), radius(n)
            result.append((max(F(0), mean-r), min(F(1), mean+r)))
    return tuple(result)


def stream_fixture(quarter_probabilities, seed, limit=12000):
    rng = random.Random(seed)
    counts = [[0, 0] for _ in range(4)]
    for cursor in range(1, limit+1):
        context = rng.randrange(4)
        target = int(rng.randrange(4) < quarter_probabilities[context])
        counts[context][0] += 1
        counts[context][1] += target
        # The certificate sees only revealed counts; no simulator probabilities.
        intervals = intervals_from_counts(counts)
        margin = interval_certificate(intervals)
        if margin is not None:
            return {'status': 'SUM_EXCLUDED_BY_CONFIDENCE_BOX', 'cursor': cursor,
                    'counts_n_successes': counts,
                    'intervals': [[str(v) for v in bounds] for bounds in intervals],
                    'rational_excess_over_bayes_lower_bound': str(margin)}
    return {'status': 'UNRESOLVED', 'cursor': limit, 'counts_n_successes': counts}


def audit():
    # Independent enumeration: every box vertex is a concrete probability table.
    # Adjacent vertices cannot switch between the two strict-order components
    # without a closure vertex, since an unchanged diagonal/off-diagonal pair
    # would otherwise have to obey both opposite strict inequalities.
    grid = (F(0), F(1, 2), F(1))
    choices = tuple((a, b) for a in grid for b in grid if a <= b)
    excluded, unresolved = 0, 0
    for box in product(choices, repeat=4):
        answer = interval_certificate(box)
        admits_closure = any(closed_intersection(vertex) for vertex in product(*box))
        assert (answer is None) == admits_closure
        if answer is None:
            unresolved += 1
        else:
            assert answer > 0
            excluded += 1
    p_sum = (F(3, 4),)*4
    p_product = (F(5, 8), F(7, 8), F(7, 8), F(5, 8))
    encode = lambda p: tuple(int(v >= F(1, 2)) for v in p)
    assert encode(p_sum) == encode(p_product) == (1, 1, 1, 1)
    assert finite_sum_representation(p_sum) is not None and not closed_intersection(p_product)
    assert interval_certificate(((F(1, 2), F(1)),)*4) is None
    assert interval_certificate(tuple((v, v) for v in p_product)) == F(1, 64)
    # Every length-8 label transcript on a repeated context schedule occurs
    # with positive probability under both structural hypotheses.
    for labels in product((0, 1), repeat=8):
        for p in (p_sum, p_product):
            likelihood = F(1)
            for index, y in enumerate(labels):
                likelihood *= p[index % 4] if y else 1-p[index % 4]
            assert likelihood > 0
    for n in range(1, 4097):
        radius(n)
    allocated = sum(ALPHA/(K*n*(n+1)) for n in range(1, 4097))
    assert K*allocated == ALPHA*F(4096, 4097) < ALPHA
    for n in (10**6, 10**9, 10**12):
        radius(n)

    positive = stream_fixture((1, 3, 3, 1), 20260906)
    control = stream_fixture((3, 3, 3, 3), 20260907)
    assert positive['status'] == 'SUM_EXCLUDED_BY_CONFIDENCE_BOX'
    assert control['status'] == 'UNRESOLVED'
    d, r = F(1, 28), F(1, 224)
    robust_gap = (d-r)**2/2-F(16, 3)*r*r
    assert robust_gap == F(115, 301056) > 0
    return {
        'status': 'PASS', 'scope': 'binary 2x2 static source class, known interval information or declared iid passive law',
        'arithmetic': 'exact rational interval/likelihood/radius decisions',
        'closed_interval_boxes_checked': excluded+unresolved,
        'boxes_with_uniform_positive_sum_exclusion': excluded,
        'boxes_admitting_sum_closure_hypothesis': unresolved,
        'one_bit_mean_transcript_collision': {'transcript': '1111', 'sum_target': [str(v) for v in p_sum],
                                             'non_sum_target': [str(v) for v in p_product],
                                             'non_sum_excess_ce_lower_bound': '1/64'},
        'common_support_length_eight_label_transcripts': 256,
        'dyadic_anytime_radii_checked': 4099,
        'preregistered_global_alpha': str(ALPHA),
        'error_allocation': 'alpha/(4 n(n+1)) per context and sample count; never refunded',
        'passive_noisy_xor_fixture': positive,
        'passive_constant_control': control,
        'range_four_robust_two_product_comparison': {'target_radius': str(r), 'fixed_witness_gap': str(robust_gap)},
        'not_claimed': ['probability coverage proved by simulation', 'validity on a deterministic fixed corpus',
                        'no-crossing as rejection', 'fresh candidate persistence',
                        'registered value/install reachability', 'Compiler/AMP closure'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_PASSIVE_INTERVAL_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
