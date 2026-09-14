"""Adversarial exact audit for the independent log-ratio checker.

Reference posterior reconstruction exercises the retained n8 data law only;
it executes no model/GPU worker and supplies no replacement model scores.
"""
from dataclasses import asdict
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
                str(ROOT/'experiments/joint_uncertainty')]
from fp_reference.numerics import log_enclosure
from log_enclosure_audit import LogAuditUnresolved, verify_log_ratio


def legacy_check(p, q, lo, hi):
    with localcontext() as context:
        context.prec = 100
        decimal = lambda value: Decimal(value.numerator)/Decimal(value.denominator)
        truth = (decimal(p)/decimal(q)).ln()
        return decimal(lo) <= truth <= decimal(hi)


def rejects(call, kind):
    try:
        call()
    except kind:
        return
    raise AssertionError('expected exact-audit rejection or unresolved result')


def audit():
    accepted, maximum_terms, maximum_bits = 0, 0, 0
    def check(p, q, terms=12):
        nonlocal accepted, maximum_terms, maximum_bits
        interval = log_enclosure(p/q, terms=terms, bit_limit=32768)
        result = verify_log_ratio(p, q, interval.lower, interval.upper)
        accepted += 1
        maximum_terms = max(maximum_terms, result.terms)
        maximum_bits = max(maximum_bits, result.maximum_operand_bits)
        return interval, result

    rational_grid = 0
    for n in range(1, 17):
        for d in range(1, 17):
            for terms in (1, 3, 12, 24):
                check(F(n, n+d), F(d, n+d), terms)
                rational_grid += 1
    near_one = 0
    for bits in (4, 8, 16, 32, 64, 96, 128):
        for sign in (-1, 1):
            check(F(1, 2)+sign*F(1, 1 << bits), F(1, 2))
            near_one += 1
    scales = 0
    for exponent in (-512, -32, -1, 0, 1, 32, 512):
        factor = F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent)
        for residual in (F(3, 4), F(1), F(3, 2)):
            x = factor*residual
            check(x/(1+x), 1/(1+x))
            scales += 1

    # This is the exact same rational reference forecast reconstructed from
    # the first registered case, not a recovered GPU event from its dead job.
    p = F(1436234048776862726818201, 2872468070873849901111602)
    interval, reproduction = check(p, F(1, 2))
    assert not legacy_check(p, F(1, 2), interval.lower, interval.upper)
    with localcontext() as context:
        context.prec = 100
        wrong = F((Decimal(3)/2).ln())
    assert legacy_check(F(3, 4), F(1, 2), wrong, wrong)
    rejects(lambda: verify_log_ratio(F(3, 4), F(1, 2), wrong, wrong), AssertionError)
    rejects(lambda: verify_log_ratio(F(3, 4), F(1, 2), F(1), F(0)), AssertionError)
    rejects(lambda: verify_log_ratio(F(1, 2), F(1, 2), F(1, 10), F(1, 5)), AssertionError)
    narrow = log_enclosure(F(3, 2), terms=24, bit_limit=32768)
    rejects(lambda: verify_log_ratio(F(3, 4), F(1, 2), narrow.lower, narrow.upper, max_terms=8), LogAuditUnresolved)
    rejects(lambda: verify_log_ratio(F(3, 4), F(1, 2), F(0), F(1), max_bits=16), LogAuditUnresolved)

    import run_likelihood_model as model
    posterior_checks, old_failures = 0, []
    for case in model.CASES:
        _, _, train, evaluation = model.data(case)
        posterior = model.AdaptivePosterior(case[0], model.counts_from_training(case[0], train), case[1])
        for offset, (i, j, target) in enumerate(evaluation):
            predictions = posterior.predict(i, j)
            for label, probability in enumerate(predictions):
                interval, result = check(probability, F(1, 2))
                if not legacy_check(probability, F(1, 2), interval.lower, interval.upper):
                    old_failures.append({'case': case, 'cursor': len(train)+offset,
                                         'label': label, 'actual_target': label == target})
                posterior_checks += 1
            posterior.observe(target)
    assert any(row['case'] == model.CASES[0] and row['cursor'] == 65 and row['label'] == 0
               and row['actual_target'] for row in old_failures)
    assert 'torch' not in sys.modules
    return {'status': 'EXACT_AUDIT_PASS',
            'scope': 'independent scalar log-enclosure verification; no Runtime authority or new GPU/model score',
            'positive_rational_grid_checks': rational_grid, 'near_one_checks': near_one,
            'scale_checks': scales, 'same_cut_posterior_label_checks': posterior_checks,
            'accepted_valid_intervals': accepted, 'maximum_accepted_series_terms': maximum_terms,
            'maximum_accepted_operand_bits': maximum_bits,
            'correct_interval_rejected_by_old_checker': {'probability': str(p), 'baseline': '1/2',
                                                       'new_audit': asdict(reproduction)},
            'wrong_zero_width_interval_accepted_by_old_checker': {'ratio': '3/2', 'endpoint': str(wrong),
                                                                 'new_checker_rejects': True},
            'all_same_cut_legacy_false_rejections': old_failures,
            'negative_and_budget_checks': 5,
            'original_failed_job_retained_without_scores': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_EXACT_LOG_AUDIT.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
