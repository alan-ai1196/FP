"""Exact audit of pre-context persistence, without Runtime authority.

The native forecast counterexample attacks a proposed context-dependent bet.
It does not mutate an owned rule or replay a new model/install experiment.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.numerics import log_enclosure
from fp_reference.learner import LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.persistence import PersistenceRule, next_wealth
from fp_reference.program import Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import evaluate

BITS = 32768


def common_bet(scores, factors):
    """Exact finite domination criterion; both score signs are required."""
    assert min(scores) < 0 < max(scores) and min(factors) >= 0
    if any(e > 1 for g, e in zip(scores, factors) if g == 0):
        return None
    lower = max([F(0)]+[(e-1)/g for g, e in zip(scores, factors) if g > 0])
    upper = min((e-1)/g for g, e in zip(scores, factors) if g < 0)
    return (lower, upper) if lower <= upper else None


def null_vertices(scores):
    """Independently enumerate vertices of {p >= 0, sum p = 1, p.g <= 0}."""
    rows = []
    for i, score in enumerate(scores):
        if score <= 0:
            rows.append(tuple(F(j == i) for j in range(len(scores))))
    for i, j in combinations(range(len(scores)), 2):
        if scores[i]*scores[j] < 0:
            row = [F(0)]*len(scores)
            row[i] = -scores[j]/(scores[i]-scores[j])
            row[j] = scores[i]/(scores[i]-scores[j])
            assert sum(row) == 1 and sum(a*b for a, b in zip(row, scores)) == 0
            rows.append(tuple(row))
    return rows


def finite_audit():
    checks = valid = vertex_checks = 0
    for n in (2, 3, 4):
        # Sorting loses no case: factors still range independently over all
        # coordinates, and the proposition is invariant under relabeling.
        for scores in combinations_with_replacement(map(F, (-2, -1, 0, 1, 2)), n):
            if not min(scores) < 0 < max(scores):
                continue
            vertices = null_vertices(scores)
            for factors in product(tuple(F(i, 2) for i in range(5)), repeat=n):
                maximum = max(sum(p*e for p, e in zip(row, factors)) for row in vertices)
                certificate = common_bet(scores, factors)
                assert (maximum <= 1) == (certificate is not None)
                if certificate is not None:
                    lam = certificate[0]
                    assert all(0 <= e <= 1+lam*g for g, e in zip(scores, factors))
                    valid += 1
                checks += 1
                vertex_checks += len(vertices)
    local_checks = 0
    for first, second in product(product((F(-2), F(-1)), (F(1), F(2))), repeat=2):
        scores = first+second
        for left, right in product((F(0), F(1, 8), F(1, 4), F(3, 8)), repeat=2):
            factors = tuple(1+lam*g for pair, lam in ((first, left), (second, right)) for g in pair)
            assert (common_bet(scores, factors) is not None) == (left == right)
            local_checks += 1
    return {'factor_tables': checks, 'valid_tables': valid,
            'independent_null_vertex_expectations': vertex_checks,
            'two_context_bet_tables': local_checks,
            'score_alphabet': [-2, -1, 0, 1, 2], 'factor_grid': ['0', '1/2', '1', '3/2', '2'],
            'outcomes': [2, 3, 4], 'sorted_scores_cover_permutations': True}


def enclosure(value):
    result = log_enclosure(value, terms=12, bit_limit=BITS)
    with localcontext() as ctx:
        ctx.prec = 160
        dec = lambda q: Decimal(q.numerator)/Decimal(q.denominator)
        exact_check = dec(value).ln()
        assert dec(result.lower) <= exact_check <= dec(result.upper)
    return result.lower, result.upper


def short_interval(lower, upper, bits=40):
    """Small outward dyadic evidence; full exact arithmetic stays in the audit."""
    scale = 1 << bits
    lo = F((lower.numerator*scale)//lower.denominator, scale)
    hi = F(-((-upper.numerator*scale)//upper.denominator), scale)
    assert lo <= lower <= upper <= hi
    return [str(lo), str(hi)]


def native_counterexample():
    rules = SemanticRules(tuple(SourceSpec(x, 'mass', 0, F(1)) for x in ('A', 'B')),
                          ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    candidate = Program((Source('A'), Source('B'),
        Sum('mass', (Term(0, 0),)*8+(Term(1, 0),)*5),
        Sum('mass', (Term(1, 0),)*3)), 1, (2, 3))
    baseline = Program((Source('A'), Sum('mass', ())), 0, (1, 1))
    probabilities = []
    for point in ((F(1), F(0)), (F(0), F(1))):
        source = dict(zip(('A', 'B'), point))
        p = evaluate(candidate, rules, (F(1),), source, bit_limit=BITS).probabilities
        q = evaluate(baseline, rules, (), source, bit_limit=BITS).probabilities
        probabilities.append(p)
        assert q == (F(1, 2), F(1, 2))
    assert probabilities == [(F(9, 10), F(1, 10)), (F(3, 5), F(2, 5))]
    # A registered zero rate realizes the fixed predictors through actual
    # continuous native units; no state is reset after seeing a label.
    spec = LearnerSpec(1, F(0))
    units = 0
    for word in product(range(4), repeat=3):
        for graph, theta in ((candidate, (F(1),)), (baseline, ())):
            state = initial_state(graph, rules, theta, 0, spec=spec, bit_limit=BITS)
            for cursor, event in enumerate(word):
                context, label = divmod(event, 2)
                source = {'A': F(context == 0), 'B': F(context == 1)}
                prediction = evaluate(graph, rules, state.theta, source, bit_limit=BITS)
                expected = probabilities[context] if graph is candidate else (F(1, 2),)*2
                assert prediction.probabilities == expected
                observed = observe_event(graph, state, spec, prediction, label, bit_limit=BITS)
                state = commit_event(observed, spec, bit_limit=BITS)
                assert state.theta == theta and not any(state.gradient_sum)
                assert state.cursor == cursor+1 and state.optimizer_steps == cursor+1
                units += 1
    joint = (F(1, 100), F(11, 100), F(87, 100), F(1, 100))
    bounds = (F(2), F(2), F(1, 4), F(1, 4))
    gains = [enclosure(2*p) for pair in probabilities for p in pair]
    assert all(-bound < lo <= hi < bound for (lo, hi), bound in zip(gains, bounds))
    mean_lo = sum(p*g[0] for p, g in zip(joint, gains))
    mean_hi = sum(p*g[1] for p, g in zip(joint, gains))
    assert mean_hi < 0
    factors = [(1+F(3, 4)/b*lo, 1+F(3, 4)/b*hi) for (lo, hi), b in zip(gains, bounds)]
    factor_lo = sum(p*g[0] for p, g in zip(joint, factors))
    factor_hi = sum(p*g[1] for p, g in zip(joint, factors))
    assert factor_lo > 1
    logs = [(enclosure(lo)[0], enclosure(hi)[1]) for lo, hi in factors]
    log_lo = sum(p*g[0] for p, g in zip(joint, logs))
    log_hi = sum(p*g[1] for p, g in zip(joint, logs))
    assert F(1, 4) < log_lo and all(-2 < lo <= hi < 2 for lo, hi in logs)
    rounded = []
    for (lo, _), bound in zip(gains, bounds):
        rule = PersistenceRule('passive-local-bound', 1, 256, F(1, 4), F(3, 4), bound, 12, 16)
        rounded.append(next_wealth(F(1), lo, rule, bit_limit=BITS))
    rounded_mean = sum(p*e for p, e in zip(joint, rounded))
    assert rounded_mean > 1
    # A common pre-context coefficient remains valid for this same null.
    fixed_mean_lo, fixed_mean_hi = (1+mean_lo/8, 1+mean_hi/8)
    assert fixed_mean_hi < 1
    # Chebyshev for independent, unrounded log factors: at n=256, mean >64,
    # variance <=1024, log(4)<2, so P(W_256>=4)>1-1024/62^2=705/961.
    crossing_lower = 1-F(4*256, (256//4-2)**2)
    assert crossing_lower == F(705, 961) and crossing_lower > F(1, 4)
    return {'native_candidate_probabilities': [[str(x) for x in pair] for pair in probabilities],
            'native_forecast_checks': 4,
            'native_rate_zero_continuous_unit_checks': units,
            'outcome_order': ['A:0', 'A:1', 'B:0', 'B:1'],
            'full_support_IID_joint_law': [str(x) for x in joint],
            'local_bounds': ['2', '1/4'], 'bet_fraction': '3/4',
            'context_coefficients': ['3/8', '3'],
            'mean_true_gain': short_interval(mean_lo, mean_hi),
            'mean_unrounded_factor': short_interval(factor_lo, factor_hi),
            'mean_unrounded_log_factor': short_interval(log_lo, log_hi),
            'first_step_actual_grid16_factors': [str(x) for x in rounded],
            'first_step_actual_grid16_mean': str(rounded_mean),
            'common_coefficient_1_over_8_mean': short_interval(fixed_mean_lo, fixed_mean_hi),
            'unrounded_by_256_crossing_probability_lower': str(crossing_lower),
            'unrounded_eventual_crossing_probability': '1',
            'grid16_eventual_crossing_claimed': False,
            'no_Runtime_authority_or_actual_installation': True}


def global_likelihood_bound():
    # A pre-context envelope for successful owned likelihood predictions;
    # this does not edit the bound=6 registration of the running matrix.
    low, high = enclosure(F(99, 500)), enclosure(F(901, 500))
    bound = F(13, 8)
    assert -bound < low[0] and high[1] < bound
    return {'exact_candidate_probability_range': ['1/10', '9/10'],
            'AMP_mass_probability_error': '1/1000', 'actual_baseline_probability': '1/2',
            'implied_successful_AMP_probability_range': ['99/1000', '901/1000'],
            'global_bound': str(bound), 'common_coefficient_at_bet_3_over_4': '6/13',
            'lower_endpoint_log_enclosure': short_interval(*low),
            'upper_endpoint_log_enclosure': short_interval(*high),
            'original_bound_6_experiment_unchanged': True,
            'power_or_installation_improvement_claimed': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = {'status': 'EXACT_AUDIT_PASS', 'scope': 'finite pre-context mean-null, passive native forecasts',
              'domination': finite_audit(), 'counterexample': native_counterexample(),
              'global_likelihood_bound': global_likelihood_bound()}
    if args.write:
        (ROOT/'evidence/minimal/FP_PERSISTENCE_FILTRATION_AUDIT.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
