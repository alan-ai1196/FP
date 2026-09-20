"""Exact finite-power composition for the rounded positive evidence curve.

No retained model tapes, Runtime authority, simulated installation or GPU.
The comparison coefficient is an analysis variable, not a selectable rule.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(Path(__file__).resolve().parent)]
from fp_reference.persistence import ArcsinePersistenceRule, PersistenceRule, next_wealth
from fp_reference.persistence_mixture import initial_coefficients, next_mixture
from fp_reference.numerics import log_enclosure
from fp_reference.learner import initial_state, observe_event, commit_event
from fp_reference.semantics import evaluate
from audit_simplex_learner import fixture
from log_enclosure_audit import verify_log_ratio
from simplex_gradient import context, relation_graph
import predictable_mixture_state as scalar
import likelihood_persistence_power as certified

B, C, RHO, ALPHA = F(13, 8), F(1, 3), F(1, 98), F(1, 4)
R = 1-C*RHO/(1-C*B)
BITS = 32768
OUTPUT = ROOT/'evidence/minimal/FP_MIXTURE_PERSISTENCE_POWER.json'
SCORE_CHECKS = []


def regret(t):
    return F(4**t, comb(2*t, t))


def declaration(horizon, bits):
    # No scalar test reaches this high threshold in the short audit words.
    return ArcsinePersistenceRule('passive-power', 1, horizon, F(1, 1024), B, 12, bits)


def fixed_declaration(horizon, bits):
    return PersistenceRule('passive-fixed-control', 1, horizon, F(1, 1024), C*B, B, 12, bits)


def constants(c=C):
    low, high = certified.log(F(1, 5)), certified.log(F(9, 5))
    v, u = certified.log(1+c*low), certified.log(1+c*high)
    a = (u-v)/(high-low)
    r = 1-c*RHO/(1-c*B)
    assert 0 < c*B < 1 and 0 < r < 1 and a.lo > 0
    assert low.lo > -B and high.hi < B
    return u, v, a, r


def scalar_audit():
    updates = 0
    for bits in (3, 21):
        rule = declaration(5, bits)
        fixed_rule = fixed_declaration(5, bits)
        for word in product((F(-1), F(0), F(1, 2)), repeat=5):
            numbers, wealth = initial_coefficients(rule, bit_limit=BITS), F(1)
            fixed = F(1)
            monomial, physical, ideal = (F(1),), F(1), F(1)
            for t, g in enumerate(word, 1):
                ell = g + (RHO if t % 2 else -RHO)
                assert -B <= ell <= B and ell >= g-RHO
                physical *= 1+C*ell
                ideal *= 1+C*g
                numbers, wealth = next_mixture(numbers, wealth, ell, t-1, rule, bit_limit=BITS)
                fixed = next_wealth(fixed, ell, fixed_rule, bit_limit=BITS)
                monomial = scalar.polynomial_step(monomial, ell/B)
                exact = scalar.independent_readout(monomial)
                epsilon = F(2**t-1, 1 << bits)
                assert 0 <= exact-wealth <= epsilon
                assert regret(t)*exact >= physical >= R**t*ideal
                assert wealth >= R**t*ideal/regret(t)-epsilon
                assert 0 <= physical-fixed <= epsilon and fixed >= R**t*ideal-epsilon
                updates += 1
    return {'complete_five_score_words_per_grid': 243, 'coefficient_bits': [3, 21],
            'production_kernel_compositions': updates,
            'fine_grid_fixed_control_compositions': updates,
            'independent_signed_monomial_readouts': updates}


def native_audit(u, v, slope):
    cfg, graph, online, _ = fixture(3)
    _, _, worlds = relation_graph(3)
    rule = declaration(6, 22)
    fixed_rule = fixed_declaration(6, 22)
    units = scored = world_checks = 0
    priors = ((F(1, 4),)*4, tuple(F(k, 10) for k in range(1, 5)))
    assert len(worlds) == 4
    for prior, word in product(priors, product((0, 1), repeat=6)):
        state = initial_state(graph, cfg.semantics, (F(1),)+prior, 0,
                              spec=online.learner, bit_limit=BITS)
        curves = [(initial_coefficients(rule, bit_limit=BITS), F(1)) for _ in range(2)]
        fixed_curves = [F(1), F(1)]
        ideal, log_ideal = certified.Interval.point(1), certified.Interval.point(0)
        past, product_ratios = [], F(1)
        for cursor, label in enumerate(word):
            query = ((past[0][2], past[1][2]) if cursor == 3 else
                     ((0, 1), (1, 2), (0, 2), None, (2, 2), (0, 2))[cursor])
            pred = evaluate(graph, cfg.semantics, state.theta, context(3, *query), bit_limit=BITS)
            probability = pred.probabilities[label]
            gain = certified.log(2*probability)
            ideal *= 1+C*gain
            log_ideal += certified.log(1+C*gain)
            product_ratios *= 2*probability
            past.append((*query, label))
            expert_ratios = tuple(F(9, 5)**(len(past)-sum((h[i]^h[j]) != y for i, j, y in past))
                                 * F(1, 5)**sum((h[i]^h[j]) != y for i, j, y in past) for h in worlds)
            assert product_ratios == sum(w*expert for w, expert in zip(prior, expert_ratios))
            for h, weight, expert in zip(worlds, prior, expert_ratios):
                errors = sum((h[i]^h[j]) != y for i, j, y in past)
                lower = (len(past)-errors)*u+errors*v+slope*certified.log(weight)
                assert product_ratios >= weight*expert and log_ideal.lo >= lower.hi
                world_checks += 1
            # A fixed, pre-target rational probability perturbation tests the
            # tube premise. These numbers are not executed device forecasts.
            delta = F(1 if cursor % 2 else -1, 1000)
            perturbed = (pred.probabilities[0]+delta, pred.probabilities[1]-delta)
            for path, probs in enumerate((pred.probabilities, perturbed)):
                raw = log_enclosure(2*probs[label], terms=12, bit_limit=BITS)
                checked = verify_log_ratio(2*probs[label], F(1), raw.lower, raw.upper)
                SCORE_CHECKS.append((checked.terms, checked.maximum_operand_bits))
                assert -B <= raw.lower <= B and raw.lower >= gain.hi-RHO
                numbers, wealth = curves[path]
                numbers, wealth = next_mixture(numbers, wealth, raw.lower, cursor, rule, bit_limit=BITS)
                epsilon = F(2**(cursor+1)-1, 1 << rule.coefficient_grid_bits)
                assert wealth >= R**(cursor+1)*ideal.hi/regret(cursor+1)-epsilon
                fixed_curves[path] = next_wealth(fixed_curves[path], raw.lower, fixed_rule, bit_limit=BITS)
                assert fixed_curves[path] >= R**(cursor+1)*ideal.hi-epsilon
                curves[path] = numbers, wealth
                scored += 1
            state = commit_event(observe_event(graph, state, online.learner, pred, label, bit_limit=BITS),
                                 online.learner, bit_limit=BITS)
            assert state.cursor == state.optimizer_steps == cursor+1
            assert state.unit_count == 0 and not any(state.gradient_sum)
            units += 1
    return {'all_six_label_words_per_initial_state': 64, 'initial_world_weights': [list(map(str, p)) for p in priors],
            'native_continuous_units': units,
            'exact_world_compositions': world_checks, 'production_score_and_curve_checks': scored,
            'fine_grid_fixed_control_checks': scored,
            'second_path': 'rational pre-target probability tube; no AMP execution'}


def power_bounds(u, v, slope):
    rows, comparisons = [], 0
    epsilon = F(1, 1 << 32)
    drift = F(9, 10)*u+F(1, 10)*v+certified.log(R)
    assert drift.lo > 0
    for horizon in (64, 128):
        thresholds = (certified.log((1/ALPHA+epsilon)*regret(horizon))-horizon*certified.log(R),
                      certified.log(1/ALPHA+epsilon)-horizon*certified.log(R))
        cdf, cumulative = [], F(0)
        for k in range(horizon+1):
            cumulative += F(comb(horizon, k)*9**(horizon-k), 10**horizon)
            cdf.append(cumulative)
        assert cumulative == 1
        for worlds in (2, 128):
            row = {'horizon': horizon, 'fractional_bits': horizon+32, 'uniform_initial_worlds': worlds}
            for label, threshold in zip(('mixture', 'fine_grid_fixed_control'), thresholds):
                offset = horizon*u+slope*certified.log(F(1, worlds))-threshold
                accepted = -1
                for errors in range(horizon+1):
                    margin = offset-errors*(u-v)
                    comparisons += 1
                    if margin.lo >= 0:
                        accepted = errors
                    else:
                        assert margin.hi < 0, 'cutoff unresolved at audit precision'
                        break
                lower = cdf[accepted] if accepted >= 0 else F(0)
                downward = F(lower.numerator*10**6//lower.denominator, 10**6)
                row[label] = {'certified_noise_cutoff': accepted,
                             'power_lower_rounded_down_to_millionth': str(downward)}
            assert row['mixture']['certified_noise_cutoff'] <= row['fine_grid_fixed_control']['certified_noise_cutoff']
            rows.append(row)
    other_u, other_v, _, other_r = constants(F(6, 13))
    other_drift = F(9, 10)*other_u+F(1, 10)*other_v+certified.log(other_r)
    assert other_drift.lo > 0
    return {'analysis_comparator': str(C), 'normalized_comparator_fraction': str(C*B),
            'common_score_error': str(RHO), 'factor_distortion': str(R),
            'alpha_per_path': str(ALPHA), 'uniform_rounding_error_upper': str(epsilon),
            'distorted_mean_log_growth': certified.short(drift),
            'tighter_fixed_comparator_distorted_growth': certified.short(other_drift),
            'exact_cutoff_comparisons': comparisons, 'uniform_prior_examples': rows,
            'alternative': 'each fixed relation world with fresh Bernoulli(1/10) noise; queries precede the current noise',
            'uniform_prior_scope': 'each row holds for every supported fixed world, hence any mixture over those worlds',
            'scope': 'paired crossing or operational/premise failure; no physical completion probability'}


def audit():
    u, v, slope, r = constants()
    assert r == R == F(535, 539)
    result = {'status': 'EXACT_MIXTURE_POWER_AUDIT_PASS',
              'retained_model_tapes_used': False, 'model_or_GPU_workers': 0,
              'scalar': scalar_audit(), 'native': native_audit(u, v, slope),
              'finite_power': power_bounds(u, v, slope)}
    checks = certified.LOG_CHECKS+SCORE_CHECKS
    result['independent_exact_logs'] = {'comparison_intervals': len(certified.LOG_CHECKS),
        'production_score_intervals': len(SCORE_CHECKS), 'maximum_verifier_terms': max(t for t, _ in checks),
        'maximum_verifier_operand_bits': max(b for _, b in checks), 'outward_fractional_bits': 96}
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
