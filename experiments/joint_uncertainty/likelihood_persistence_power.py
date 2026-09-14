"""Exact audit of likelihood learning, physical wealth and finite fresh power.

This is a passive theorem audit, not a model worker, new evidence identity,
counterfactual installation or source of values for ReferenceCompilerRuntime.
Only retained training profiles enter the four conditional-law calculations.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import comb, factorial
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
                str(Path(__file__).resolve().parent)]
from fp_reference.learner import initial_state, observe_event, commit_event
from fp_reference.numerics import log_enclosure
from fp_reference.persistence import PersistenceRule, next_wealth
from fp_reference.semantics import evaluate
from log_enclosure_audit import verify_log_ratio
from audit_simplex_learner import fixture
from simplex_gradient import context, relation_graph
from joint_model import data, AdaptivePosterior, counts_from_training

CASES = ((8, 'iid-c2', 16), (8, 'iid-c2', 17),
         (8, 'iid-c4', 18), (8, 'iid-c4', 19))
BITS, OUTWARD_BITS = 32768, 96
COEFFICIENT, RHO, DELTA = F(1, 8), F(1, 98), F(1, 1 << 16)
DISTORTION, KAPPA, ALPHA, HORIZON = F(587, 588), F(1, 4), F(1, 4), 64
LOG_CHECKS = []


def floor_at(value, bits):
    scale = 1 << bits
    return F(value.numerator*scale//value.denominator, scale)


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __post_init__(self):
        assert type(self.lo) is F and type(self.hi) is F and self.lo <= self.hi

    @classmethod
    def point(cls, value):
        return cls(F(value), F(value))

    @classmethod
    def outward(cls, lo, hi):
        assert lo <= hi
        return cls(floor_at(lo, OUTWARD_BITS), -floor_at(-hi, OUTWARD_BITS))

    def __add__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        return self.outward(self.lo+other.lo, self.hi+other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self+(-other if isinstance(other, Interval) else -F(other))

    def __rsub__(self, other):
        return -self+other

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        values = tuple(a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi))
        return self.outward(min(values), max(values))

    __rmul__ = __mul__

    def reciprocal(self):
        assert self.lo > 0 or self.hi < 0
        return self.outward(1/self.hi, 1/self.lo)

    def __truediv__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        return self*other.reciprocal()


@lru_cache(maxsize=4096)
def exact_log(value):
    assert type(value) is F and value > 0
    result = log_enclosure(value, terms=24, bit_limit=BITS)
    checked = verify_log_ratio(value, F(1), result.lower, result.upper)
    LOG_CHECKS.append((checked.terms, checked.maximum_operand_bits))
    return Interval.outward(result.lower, result.upper)


def log(value):
    if not isinstance(value, Interval):
        return exact_log(F(value))
    assert value.lo > 0
    return Interval.outward(exact_log(value.lo).lo, exact_log(value.hi).hi)


def short(value, bits=40):
    value = value if isinstance(value, Interval) else Interval.point(value)
    return [str(floor_at(value.lo, bits)), str(-floor_at(-value.hi, bits))]


def rule():
    return PersistenceRule('passive-power-audit', 1, HORIZON, ALPHA,
                           F(3, 4), F(6), 12, 16)


def constants():
    low_gain, high_gain = log(F(1, 5)), log(F(9, 5))
    low_factor, high_factor = 1+COEFFICIENT*low_gain, 1+COEFFICIENT*high_gain
    negative, positive = log(low_factor), log(high_factor)
    slope = (positive-negative)/(high_gain-low_gain)
    intercept = positive-slope*high_gain
    assert low_factor.lo > F(3, 4) and negative.hi < 0 < positive.lo
    assert (F(9, 10)*positive+F(1, 10)*negative).lo > 0
    return low_gain, high_gain, positive, negative, slope, intercept


def scalar_audit(values):
    low, high, positive, negative, slope, intercept = values
    # Exact finite witnesses for the constants used in the analytic proof.
    assert sum(F(2)**j/factorial(j) for j in range(5)) > 5
    assert sum(F(9, 8)**j/factorial(j) for j in range(5)) > F(9, 5)
    assert F(1, 2)-F(9, 8)/6+F(9, 8)**2/24-F(9, 8)**3/120 > F(1, 3)
    tail = 2*F(1, 3)**25/(25*(1-F(1, 9)))
    assert 4*tail < F(1, 1 << 32)
    assert F(1, 99)+F(1, 1 << 32) < RHO
    assert DISTORTION == 1-RHO/6
    chord_checks = inverse_checks = 0
    for numerator in range(10, 91):
        p = F(numerator, 100)
        gains = (log(2*p), log(2*(1-p)))
        for probability, gain in zip((p, 1-p), gains):
            if probability not in (F(1, 10), F(9, 10)):
                slack = log(1+COEFFICIENT*gain)-(slope*gain+intercept)
                assert slack.lo > 0
                chord_checks += 1
        if p == F(1, 2):
            assert gains == (Interval.point(0),)*2
        else:
            mu = p*gains[0]+(1-p)*gains[1]
            inverse = p*(1+COEFFICIENT*gains[0]).reciprocal()+(1-p)*(1+COEFFICIENT*gains[1]).reciprocal()
            assert inverse.hi <= (1-mu/16).lo
        inverse_checks += 1
    return {'chord_interior_checks': chord_checks, 'reciprocal_contraction_checks': inverse_checks,
            'twelve_term_uniform_log_width_upper': str(4*tail),
            'common_score_error': str(RHO), 'multiplicative_distortion': str(DISTORTION),
            'chord_slope': short(slope), 'positive_log_factor': short(positive),
            'negative_log_factor': short(negative)}


def native_audit():
    cfg, graph, online, _ = fixture(3)
    _, _, worlds = relation_graph(3)
    units = mixture_checks = floor_checks = 0
    for word in product((0, 1), repeat=6):
        state = initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                              spec=online.learner, bit_limit=BITS)
        product_ratios, past = F(1), []
        ideal, error_sum, wealth = Interval.point(1), Interval.point(0), F(1)
        for cursor, label in enumerate(word):
            # Predictable queries, including loops and a branch on an earlier
            # label. No choice depends on the current label.
            query = ((past[0][2], past[1][2]) if cursor == 3 else
                     ((0, 1), (1, 2), (0, 2), None, (2, 2), (0, 2))[cursor])
            prediction = evaluate(graph, cfg.semantics, state.theta, context(3, *query), bit_limit=BITS)
            probability = prediction.probabilities[label]
            product_ratios *= 2*probability
            past.append((*query, label))
            expert_ratios = tuple(F(1) for _ in worlds)
            for i, j, target in past:
                expert_ratios = tuple(old*(F(9, 5) if h[i]^h[j] == target else F(1, 5))
                                      for old, h in zip(expert_ratios, worlds))
            assert product_ratios == sum(expert_ratios)/len(worlds)
            assert all(product_ratios >= term/len(worlds) for term in expert_ratios)
            mixture_checks += len(worlds)
            gain = log(2*probability)
            distorted_factor = DISTORTION*(1+COEFFICIENT*gain)
            ideal = ideal*distorted_factor
            error_sum = error_sum*distorted_factor+1
            # A fixed pre-target perturbation tests both error signs. It is a
            # passive rational tube witness, not an executed AMP forecast.
            perturbed = (prediction.probabilities[0]-F(1, 1000),
                         prediction.probabilities[1]+F(1, 1000))
            score = log_enclosure(2*perturbed[label], terms=12, bit_limit=BITS)
            verify_log_ratio(2*perturbed[label], F(1), score.lower, score.upper)
            assert score.lower >= gain.hi-RHO
            wealth = next_wealth(wealth, score.lower, rule(), bit_limit=BITS)
            assert wealth >= (ideal-DELTA*error_sum).hi
            assert wealth < 1/ALPHA
            floor_checks += 1
            state = commit_event(observe_event(graph, state, online.learner, prediction,
                                              label, bit_limit=BITS), online.learner, bit_limit=BITS)
            assert state.cursor == cursor+1 and state.optimizer_steps == cursor+1
            assert state.unit_count == 0 and not any(state.gradient_sum)
            units += 1
    return {'all_six_label_words': 64, 'native_continuous_unit_checks': units,
            'exact_mixture_domination_checks': mixture_checks,
            'actual_wealth_helper_floor_composition_checks': floor_checks,
            'perturbation_scope': 'fixed rational pre-target tube witness; no GPU phase'}


def absorption_audit(values):
    cfg, graph, online, _ = fixture(2)
    state = initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                          spec=online.learner, bit_limit=BITS)
    wealth, before_zero = F(1), None
    for cursor in range(HORIZON):
        prediction = evaluate(graph, cfg.semantics, state.theta, context(2, 0, 0), bit_limit=BITS)
        assert prediction.probabilities == (F(9, 10), F(1, 10))
        score = log_enclosure(F(1, 5), terms=12, bit_limit=BITS)
        previous = wealth
        wealth = next_wealth(wealth, score.lower, rule(), bit_limit=BITS)
        state = commit_event(observe_event(graph, state, online.learner, prediction, 1,
                                          bit_limit=BITS), online.learner, bit_limit=BITS)
        assert state.theta == cfg.initializer_pattern and state.optimizer_steps == cursor+1
        if wealth == 0:
            before_zero, count = previous, cursor+1
            break
    assert wealth == 0 and before_zero > 0
    positive_score = log_enclosure(F(9, 5), terms=12, bit_limit=BITS)
    assert next_wealth(wealth, positive_score.lower, rule(), bit_limit=BITS) == 0
    _, _, positive, negative, _, _ = values
    drift = F(9, 10)*positive+F(1, 10)*negative
    assert drift.lo > 0
    return {'native_self_query_units_until_absorption': count,
            'positive_wealth_immediately_before_zero': str(before_zero),
            'absorbing_zero_even_on_next_favorable_score': True,
            'correct_law_probability_of_this_prefix': str(F(1, 10)**count),
            'unrounded_positive_mean_log_increment': short(drift),
            'scope': 'positive-probability failure of eventual power; no failure of null validity'}


def fixed_world_scope_audit():
    cfg, graph, online, _ = fixture(2)
    state = initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                          spec=online.learner, bit_limit=BITS)
    prediction = evaluate(graph, cfg.semantics, state.theta, context(2, 0, 1), bit_limit=BITS)
    state = commit_event(observe_event(graph, state, online.learner, prediction, 1,
                                      bit_limit=BITS), online.learner, bit_limit=BITS)
    after = evaluate(graph, cfg.semantics, state.theta, context(2, 0, 1), bit_limit=BITS)
    assert after.probabilities == (F(9, 50), F(41, 50))
    inverses = tuple((1+COEFFICIENT*log(2*p)).reciprocal() for p in after.probabilities)
    fixed_world_mean = F(9, 10)*inverses[0]+F(1, 10)*inverses[1]
    mixture_mean = sum(p*factor for p, factor in zip(after.probabilities, inverses))
    assert fixed_world_mean.lo > 1 and mixture_mean.hi < 1
    return {'native_unit_after_one_label': 1, 'next_candidate_probabilities': ['9/50', '41/50'],
            'fixed_equal_world_inverse_factor_mean': short(fixed_world_mean),
            'posterior_mixture_inverse_factor_mean': short(mixture_mean),
            'scope': 'reciprocal supermartingale cannot be asserted conditional on every fixed hidden world'}


def profile_bounds(values):
    _, _, positive, negative, slope, _ = values
    threshold = log(1/(ALPHA*(1-KAPPA)))-HORIZON*log(DISTORTION)
    drawdown = DELTA*HORIZON/(KAPPA*DISTORTION**HORIZON)
    cdf, cumulative = [], F(0)
    for errors in range(HORIZON+1):
        cumulative += F(comb(HORIZON, errors)*9**(HORIZON-errors), 10**HORIZON)
        cdf.append(cumulative)
    assert cumulative == 1 and drawdown < F(4356, 1000000)
    rows, cutoff_checks = [], 0
    for case in CASES:
        # The future tape returned by data() is not used in this calculation.
        train = data(case)[2]
        posterior = AdaptivePosterior(case[0], counts_from_training(case[0], train), case[1])
        total = sum(posterior.weights)
        weights = tuple(F(2*posterior.weights[mask], total) for mask in range(0, 1 << case[0], 2))
        assert len(weights) == 128 and sum(weights) == 1 and min(weights) > 0
        cutoffs = {}
        for weight in set(weights):
            offset = HORIZON*positive+slope*log(weight)-threshold
            accepted = -1
            for errors in range(HORIZON+1):
                margin = offset-errors*(positive-negative)
                cutoff_checks += 1
                if margin.lo >= 0:
                    accepted = errors
                else:
                    assert margin.hi < 0, 'noise cutoff unresolved at the audit precision'
                    break
            cutoffs[weight] = accepted
        ideal_lower = sum(weight*(cdf[cutoffs[weight]] if cutoffs[weight] >= 0 else 0) for weight in weights)
        lower = max(F(0), ideal_lower-drawdown)
        decimal_lower = F(lower.numerator*10**6//lower.denominator, 10**6)
        assert decimal_lower <= lower <= 1
        rows.append({'case': case, 'training_events': len(train), 'worlds': len(weights),
                     'distinct_initial_weights_checked': len(cutoffs),
                     'power_lower_outward_interval': short(lower),
                     'power_lower_rounded_down_to_millionth': str(decimal_lower),
                     'scope': 'posterior-mixture alternative; paired crossing or operational failure by64; no evaluation targets or empirical outcome'})
    return {'horizon': HORIZON, 'alpha': str(ALPHA), 'wealth_grid_bits': 16,
            'kappa': str(KAPPA), 'drawdown_allowance': short(drawdown),
            'ideal_terminal_log_threshold': short(threshold),
            'exact_noise_cutoff_comparisons': cutoff_checks, 'profiles': rows}


def audit():
    values = constants()
    result = {'status': 'EXACT_AUDIT_PASS',
              'scope': 'conditional finite fresh-power theorem; no Runtime/GPU execution or new model outcome',
              'scalar': scalar_audit(values), 'native': native_audit(),
              'absorption': absorption_audit(values), 'fixed_world_scope': fixed_world_scope_audit(),
              'finite_power': profile_bounds(values)}
    result['independent_exact_log_checks'] = {'distinct_24_term_intervals': len(LOG_CHECKS),
        'maximum_verifier_terms': max(row[0] for row in LOG_CHECKS),
        'maximum_verifier_operand_bits': max(row[1] for row in LOG_CHECKS),
        'outward_interval_fractional_bits': OUTWARD_BITS}
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_LIKELIHOOD_PERSISTENCE_POWER.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
