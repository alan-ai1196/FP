"""Exact rational enclosures for the scoped fresh log-loss power theorem."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json

from value_reachability_audit import floor_dyadic, loss_upper, step

B, GAP, RHO = F(9, 8), F(1, 1568), F(1, 1 << 32)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def scale(a, c):
    ends = (a[0]*c, a[1]*c)
    return min(ends), max(ends)


def square(a):
    return (F(0) if a[0] <= 0 <= a[1] else min(a[0]**2, a[1]**2),
            max(a[0]**2, a[1]**2))


def reciprocal(a):
    assert a[0] > 0
    return 1/a[1], 1/a[0]


def log_interval(ratio, terms=16):
    assert F(1, 3) <= ratio <= 3
    z = (ratio-1)/(ratio+1)
    center = 2*sum((z**(2*k+1)/F(2*k+1) for k in range(terms)), F(0))
    remainder = 2*abs(z)**(2*terms+1)/((2*terms+1)*(1-z*z))
    return center-remainder, center+remainder


def expectation(values, p):
    return add(scale(values[0], 1-p), scale(values[1], p))


def kl(p, q):
    return expectation((log_interval((1-p)/(1-q)), log_interval(p/q)), p)


def audit():
    polynomial = F(1, 2)-B/6+B**2/24-B**3/120
    exponential_lower = 1+B+B**2/2+B**3/6+B**4/24
    assert polynomial == F(7237, 20480) > F(1, 3)
    assert exponential_lower == F(100331, 32768) > 3
    assert -F(1, 6)+B/12 < 0  # Upper bound on polynomial derivative.
    maximum_width = 4*F(1, 2)**33/(33*(1-F(1, 4)))
    assert maximum_width < RHO < GAP/12
    assert RHO/24+(2*B*RHO+RHO**2)/288 <= RHO/16

    grid = tuple(F(k, 8) for k in range(2, 7))
    moment_cases = 0
    for p, q in product(grid, repeat=2):
        logs = (log_interval((1-p)/(1-q)), log_interval(p/q))
        moment = expectation(tuple(square(v) for v in logs), p)
        risk = kl(p, q)
        assert moment[1] <= 3*risk[0]
        moment_cases += 1

    paired_cases = 0
    for p, candidate, comparator in product(grid, repeat=3):
        logs = (log_interval((1-candidate)/(1-comparator)),
                log_interval(candidate/comparator))
        epsilon, comparator_risk = kl(p, candidate), kl(p, comparator)
        mean = add(comparator_risk, scale(epsilon, -1))
        second = expectation(tuple(square(v) for v in logs), p)
        assert second[1] <= 6*add(comparator_risk, epsilon)[0]
        inverse_factors = tuple(reciprocal(add((F(1), F(1)), scale(v, F(1, 24))))
                                for v in logs)
        inverse_mean = expectation(inverse_factors, p)
        bound = add((F(1), F(1)), scale(add(mean, scale(epsilon, -2)), -F(1, 48)))
        assert inverse_mean[1] <= bound[0]
        for lo, hi in logs:
            assert -B <= lo <= hi <= B and hi-lo <= maximum_width
        # These rational lower scores give a lower expectation under every law.
        lower_mean = (1-p)*logs[0][0]+p*logs[1][0]
        direct_mean = expectation(logs, p)
        assert direct_mean[0] == lower_mean
        assert direct_mean[1]-lower_mean <= RHO
        paired_cases += 1

    theta = F(0)
    for _ in range(32):
        theta = floor_dyadic(step(theta), 32)
    bias = loss_upper(theta)
    analytic_bias = F(1, 54)*F(11, 12)**62
    assert bias < GAP/6 and analytic_bias < GAP/6
    assert F(1, 1)/24*(GAP-GAP/6)-6*(GAP+GAP/6)/288 == GAP/96
    assert GAP/96-RHO/16 >= GAP/192

    alpha = beta = F(1, 20)
    exact_budget, lower_score_budget = 9*96*1568, 9*192*1568
    assert exact_budget*GAP/96 == lower_score_budget*GAP/192 == 9
    tail_upper = 1/(alpha*2**9)
    assert tail_upper == F(5, 128) < beta

    target = (F(1, 2), F(1, 2), F(3, 4), F(1, 4))
    constant_mass_choices = ((1, 1), (1, 1), (1, 3), (3, 1))
    for p, mass in zip(target, constant_mass_choices):
        assert min(mass) >= 1 and sum(mass) <= 4 and F(mass[1], sum(mass)) == p
    for mass in set(constant_mass_choices):
        q = F(mass[1], sum(mass))
        fixed_function_risk_lower = sum((kl(p, q)[0] for p in target), F(0))/4
        assert fixed_function_risk_lower >= GAP

    return {
        'status': 'PASS',
        'scope': 'bounded binary forecasts, declared fresh conditional law, fixed continuous evidence identity',
        'single_forecast_moment_grid_cases': moment_cases,
        'paired_forecast_moment_and_reciprocal_grid_cases': paired_cases,
        'log_enclosure': {'method': 'rational atanh series with symmetric rigorous tail',
                          'terms': 16, 'ratio_domain': ['1/3', '3'],
                          'maximum_width': str(maximum_width), 'declared_rho': str(RHO)},
        'candidate': {'registered_profile_steps': 32, 'fraction_bits': 32,
                      'coefficient': str(theta), 'excess_ce_upper': str(bias),
                      'excess_ce_upper_display': float(bias),
                      'required_bias_upper': str(GAP/6),
                      'separate_unrounded_analytic_bias_upper': str(analytic_bias)},
        'all_class_comparator_excess_ce_lower': str(GAP),
        'alpha': str(alpha), 'beta': str(beta),
        'theoretical_sufficient_fresh_budget_exact_scores': exact_budget,
        'theoretical_sufficient_fresh_budget_lower_scores': lower_score_budget,
        'no_crossing_probability_upper_at_these_budgets': str(tail_upper),
        'fresh_events_executed': 0,
        'context_after_selection_requirement': 'entire comparator function chosen before fresh context',
        'context_aware_constant_selection_counterexample_exact': True,
        'not_claimed': ['grid enumeration proves the universal moment theorem',
                        'unknown population determined by 16 profile labels',
                        'context-aware controller is an authorized zero-PRODUCT complete compiler',
                        'fresh iid context premise holds for general teacher-forced LM',
                        'bounded-memory wealth implementation or complete runtime/AMP certification'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_LOG_LOSS_PERSISTENCE_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
