"""Exact audits of the scoped binary parity precision laws; no Runtime authority."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / 'evidence/minimal/FP_PARITY_COMPOSITION.json'
PAIRS = ((1, 64), (1, 8), (1, 2), (1, 1), (2, 1), (8, 1), (64, 1))


def conv(a, b):
    return a[0]*b[0]+a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def distortion(a, b):
    ratio = F(a[0]*b[1], a[1]*b[0])
    return max(ratio, 1/ratio)


def probability(a):
    return F(a[0], sum(a))


def xor_probability(q, r):
    return q*r+(1-q)*(1-r)


def tilt(q, odds_ratio):
    return odds_ratio*q/(1+(odds_ratio-1)*q)


def clamp(q):
    return min(F(1), max(F(0), q))


def total_variation_join(e, f):
    if max(e, f) <= F(1, 2):
        return e+f-2*e*f
    return min(F(1), e+f)


def t_upper(ratio):
    # sqrt(ratio) >= 2*ratio/(ratio+1), so this is an outward rational bound.
    return (ratio-1)/(ratio+1+4*ratio/(ratio+1))


@dataclass(frozen=True)
class State:
    reference: F
    virtual: F
    actual: F
    odds_bound: F
    tail_bound: F
    paths: tuple


def check_state(state):
    p, t, s = state.reference, state.virtual, state.actual
    assert 0 < p < 1 and 0 < t < 1 and 0 <= s <= 1
    assert 1 <= distortion((p, 1-p), (t, 1-t)) <= state.odds_bound
    assert abs(s-t) <= state.tail_bound <= 1
    assert state.odds_bound == max(state.paths)
    bound = t_upper(state.odds_bound)
    assert abs(s-p) <= bound+state.tail_bound
    assert abs(1/(1+8*t)-1/(1+8*p)) <= F(8, 9)*bound
    assert abs(8/(1+8*s)-8/(1+8*p)) <= F(64, 9)*bound+64*state.tail_bound
    return state


def leaf(pair, ratio, shift):
    p = probability(pair)
    t = tilt(p, ratio)
    bound = max(ratio, 1/ratio)
    return check_state(State(p, t, clamp(t+shift), bound, abs(shift), (bound,)))


def join(left, right, ratio, shift):
    p = xor_probability(left.reference, right.reference)
    t = tilt(xor_probability(left.virtual, right.virtual), ratio)
    s = clamp(tilt(xor_probability(left.actual, right.actual), ratio)+shift)
    rho = max(ratio, 1/ratio)
    c = total_variation_join(left.tail_bound, right.tail_bound)
    e = min(F(1), abs(shift)+tilt(c, rho))
    paths = tuple(rho*path for path in left.paths+right.paths)
    return check_state(State(p, t, s, rho*max(left.odds_bound, right.odds_bound), e, paths))


def audit():
    counts = {}
    count = 0
    for a, b, c, d in product(PAIRS, repeat=4):
        assert distortion(conv(a, b), conv(c, d)) <= max(distortion(a, c), distortion(b, d))
        count += 1
    counts['two_block_projective_comparisons'] = count
    count = 0
    for a, b, c, d, e, f in product(PAIRS, repeat=6):
        assert distortion(conv(conv(a, b), c), conv(conv(d, e), f)) <= max(
            distortion(a, d), distortion(b, e), distortion(c, f))
        count += 1
    counts['three_block_projective_comparisons'] = count

    count = 0
    extremizers = []
    for s in (F(101, 100), F(9, 8), F(2), F(10)):
        t = (s-1)/(s+1)
        for a in PAIRS+((1, s), (1, 9*s)):
            b = a[0]*s*s, a[1]
            x, y = probability(a), probability(b)
            assert abs(x-y) <= t
            assert abs(1/(1+8*x)-1/(1+8*y)) <= F(8, 9)*t
            count += 1
        assert probability((s, 1))-probability((1, s)) == t
        x, y = probability((1, 9*s)), probability((s, 9))
        assert abs(1/(1+8*x)-1/(1+8*y)) == F(8, 9)*t
        extremizers.append({'sqrt_odds_distortion': str(s), 'sharp_TV': str(t),
                            'sharp_match_gradient': str(F(64, 9)*t)})
    counts['native_readout_comparisons'] = count
    counts['attaining_readout_pairs'] = 8

    grid = tuple((a, 8-a) for a in range(9))
    count = 0
    for a, b, c, d in product(grid, repeat=4):
        e, f = abs(probability(a)-probability(c)), abs(probability(b)-probability(d))
        if max(e, f) > F(1, 2):
            continue
        assert abs(probability(conv(a, b))-probability(conv(c, d))) <= e+f-2*e*f
        count += 1
    counts['two_block_TV_comparisons'] = count

    count = 0
    for a, b, ratio in product(grid, grid, (F(1, 8), F(1, 2), F(1), F(2), F(8))):
        p, q = probability(a), probability(b)
        rho = max(ratio, 1/ratio)
        assert abs(tilt(p, ratio)-tilt(q, ratio)) <= tilt(abs(p-q), rho)
        # The upper endpoint is attained by a boundary interval in the favored direction.
        if ratio >= 1:
            assert tilt(abs(p-q), ratio)-tilt(F(0), ratio) == tilt(abs(p-q), rho)
        count += 1
    counts['common_reweighting_comparisons'] = count

    rng = Random(20260923)
    ratios = (F(1, 2), F(63, 64), F(1), F(64, 63), F(2))
    shifts = (F(0), F(1, 256), F(-1, 256), F(1, 32), F(-1, 32), F(1, 4), F(-1, 4))
    count = nodes = 0

    def combine(left, right):
        nonlocal nodes
        nodes += 1
        return join(left, right, rng.choice(ratios), rng.choice(shifts))

    def balanced(states):
        if len(states) == 1:
            return states[0]
        middle = len(states)//2
        return combine(balanced(states[:middle]), balanced(states[middle:]))

    for length in range(2, 17):
        for _ in range(128):
            states = tuple(leaf(rng.choice(PAIRS), rng.choice(ratios), rng.choice(shifts))
                           for _ in range(length))
            balanced(states)
            serial = states[0]
            for state in states[1:]:
                serial = combine(serial, state)
            count += 2
    counts['mixed_error_trees'] = count
    counts['mixed_error_internal_nodes'] = nodes

    previous = F(1)
    for exponent in (1, 2, 4, 8, 16, 32, 64):
        near_identity = (2**exponent, 1)
        actual = conv(conv((2, 1), near_identity), near_identity)
        exact = conv(conv((1, 1), near_identity), near_identity)
        distance = distortion(actual, exact)
        assert previous < distance < 2
        previous = distance
    assert 2-previous < F(1, 2**60)
    counts['projective_sharpness_sequence'] = 7

    for depth in (1, 4, 8):
        base = leaf((1, 1), F(9, 8), F(0))
        identity = leaf((2**80, 1), F(1), F(0))
        for _ in range(depth):
            base = join(base, identity, F(9, 8), F(0))
        assert base.odds_bound == F(9, 8)**(depth+1)
        error_factor = distortion((base.reference, 1-base.reference), (base.virtual, 1-base.virtual))
        assert 0 < base.odds_bound-error_factor < F(1, 2**65)
    counts['rounded_path_sharpness_witnesses'] = 3

    rare = F(1, 2**150)
    pair = (1-rare, rare)
    output_error = 1-probability(conv(pair, pair))
    assert output_error == 2*rare*(1-rare) > rare
    point_product = lambda a, b: (a[0]*b[0], a[1]*b[1])
    assert distortion(point_product((1, 1), (1, 1)), point_product((2, 1), (2, 1))) == 4
    # Reweighting an inherited absolute error is not TV-nonexpansive.
    inherited = F(1, 256)
    assert tilt(inherited, F(2)) > inherited

    return {'status': 'PASS_EXACT_PARITY_COMPOSITION', 'arithmetic': 'fractions.Fraction',
        'scope': 'conditional response and numerical-error laws; no physical kernel or Runtime release',
        'checks': counts, 'sharp_readout_extremizers': extremizers,
        'counterexamples': {
            'shared_latent_product': {'local_odds_distortion': '2', 'output_odds_distortion': '4'},
            'underflow_maximum_error': {'local_absolute_error': str(rare),
                'output_to_local_error_ratio': str(output_error/rare)},
            'omitted_reweighting': {'inherited_TV': str(inherited), 'output_TV': str(tilt(inherited, F(2)))}}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        ARTIFACT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    else:
        assert json.loads(ARTIFACT.read_text(encoding='utf-8')) == report
    print(json.dumps(report, indent=2))
