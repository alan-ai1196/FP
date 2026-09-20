"""Fixed-rule conditional predictions and a reciprocal-power counterexample.

Reads all four retained tapes after registration. No model execution, rule
selection, Runtime authority or imputation of an unavailable outcome occurs.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

import likelihood_deployment_envelope as envelope
import run_likelihood_deployment as experiment
from fp_reference.persistence import next_wealth

ROOT, SOURCE = experiment.ROOT, '8ccacc0'
COEFFICIENT = F(6, 13)
OUTPUT = ROOT/'evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_PREDICTION.json'
INPUTS = envelope.INPUTS+(
    'src/reference_compiler', 'scripts',
    'experiments/joint_uncertainty/likelihood_deployment_envelope.py',
    'experiments/joint_uncertainty/likelihood_persistence_power.py',
    'experiments/joint_uncertainty/run_likelihood_deployment.py',
    'experiments/joint_uncertainty/LIKELIHOOD_DEPLOYMENT_PROTOCOL.md',
    experiment.CONTROL_PATH, experiment.CONTROL_ANALYSIS,
)


def registered_rule():
    return replace(envelope.rule(), bound=F(13, 8))


def crossings(exact, evaluation, cutoff):
    wealth = [F(1)]*3
    first, at_crossing = [None]*3, [None]*3
    minimum, minimum_cursor = F(1), cutoff
    reference_checks = 0
    for offset, (i, j, label) in enumerate(evaluation):
        p = exact[i, j][label]
        low, high = envelope.gain_tube(p)
        gains = (envelope.gain_interval(p).lower, low, high)
        for path, gain in enumerate(gains):
            if first[path] is not None:
                continue
            assert 1+COEFFICIENT*gain > 0
            after = envelope.floor_at(wealth[path]*(1+COEFFICIENT*gain), 16)
            if path == 0:
                assert next_wealth(wealth[path], gain, registered_rule(), bit_limit=32768) == after
                reference_checks += 1
                if after < minimum:
                    minimum, minimum_cursor = after, cutoff+offset+1
            wealth[path] = after
            if after >= 4:
                first[path], at_crossing[path] = cutoff+offset+1, str(after)
    ref, latest, earliest = first
    assert all(cursor is not None for cursor in first)
    assert earliest <= ref <= latest
    return {'reference_cursor': ref, 'AMP_earliest_cursor': earliest,
        'AMP_latest_cursor': latest,
        'paired_cursor_interval': [max(ref, earliest), max(ref, latest)],
        'reference_wealth_at_crossing': at_crossing[0],
        'lower_tube_wealth_at_crossing': at_crossing[1],
        'upper_tube_wealth_at_crossing': at_crossing[2],
        'minimum_reference_wealth_before_stopping': str(minimum),
        'minimum_reference_wealth_cursor': minimum_cursor,
        'actual_wealth_helper_prefix_checks': reference_checks}


def reciprocal_witness():
    cfg, graph, online, _ = envelope.fixture(2)
    state = envelope.initial_state(graph, cfg.semantics, cfg.initializer_pattern,
        0, spec=online.learner, bit_limit=32768)
    prediction = envelope.evaluate(graph, cfg.semantics, state.theta,
        envelope.context(2, 0, 0), bit_limit=32768)
    assert prediction.probabilities == (F(9, 10), F(1, 10))
    p = prediction.probabilities[0]
    a, b = envelope.log(2*p), envelope.log(2*(1-p))
    mean_gain = p*a+(1-p)*b
    critical = mean_gain/(-a*b)
    assert F(1, 8) < critical.lo <= critical.hi < COEFFICIENT
    rows = []
    for coefficient, rule in ((F(1, 8), envelope.rule()), (COEFFICIENT, registered_rule())):
        positive, negative = 1+coefficient*a, 1+coefficient*b
        inverse = p*positive.reciprocal()+(1-p)*negative.reciprocal()
        growth = p*envelope.log(positive)+(1-p)*envelope.log(negative)
        rounded = tuple(next_wealth(F(1), envelope.gain_interval(q).lower, rule,
                                   bit_limit=32768) for q in (p, 1-p))
        rounded_inverse = p/rounded[0]+(1-p)/rounded[1]
        assert rounded_inverse >= inverse.lo
        rows.append({'coefficient': str(coefficient), 'ideal_expected_reciprocal': envelope.short(inverse),
            'ideal_expected_log_growth': envelope.short(growth),
            'production_one_step_wealth': tuple(map(str, rounded)),
            'production_expected_reciprocal': str(rounded_inverse)})
    assert F(rows[0]['ideal_expected_reciprocal'][1]) < 1
    assert F(rows[1]['ideal_expected_reciprocal'][0]) > F(109, 100)
    assert F(rows[1]['ideal_expected_log_growth'][0]) > F(rows[0]['ideal_expected_log_growth'][1]) > 0
    return {'native_query': [0, 0], 'native_probabilities': ['9/10', '1/10'],
        'critical_coefficient_for_ideal_reciprocal_contraction': envelope.short(critical),
        'rules': rows,
        'scope': 'correct-posterior alternative; does not falsify mean-null validity'}


def audit():
    source = experiment.model.git('rev-parse', SOURCE)
    assert not experiment.model.git('diff', source, '--', *INPUTS)
    assert not experiment.model.git('status', '--porcelain', '--', *INPUTS)
    registration = experiment.preflight()
    assert F(registration['persistence']['coefficient']) == COEFFICIENT
    controls, provenance = experiment.retained_controls()
    witness = reciprocal_witness()
    rows = []
    forecasts = 0
    for case, control in zip(experiment.CASES, controls['workers']):
        hidden, edges, train, evaluation = experiment.model.data(case)
        counts = experiment.model.counts_from_training(case[0], train)
        exact, _, _ = envelope.reader.posterior_predictions(case[0], counts, case[1], evaluation)
        assert len(exact) == len(evaluation) == 64
        forecasts += len(exact)
        fresh = crossings(exact, evaluation, len(train))
        scores = envelope.score_envelopes(case, exact, hidden, edges, evaluation, len(train),
                                         fresh['paired_cursor_interval'])
        prior = control['result']
        for subset, record in scores.items():
            value = F(prior['scores']['adaptive_exact_'+subset]['expected_CE_binary64'])
            lo, hi = map(F, record['reference_candidate_expected_CE'])
            assert lo-F(1, 1 << 42) <= value <= hi+F(1, 1 << 42)
            old_score = F(prior['scores']['deployed_stream_'+subset]['expected_CE_binary64'])
            new = envelope.Interval(*map(F, record['deployed_expected_CE_if_installed']))
            old = envelope.Interval(old_score-F(1, 1 << 42), old_score+F(1, 1 << 42))
            record['conditional_deployed_CE_change_from_B6'] = envelope.short(new-old)
        rows.append({'case': case, 'training_events': len(train), 'evaluation_events': len(evaluation),
            'retained_B6_install_cursor': prior['install_cursor'], 'fresh': fresh,
            'remaining_forecasts_if_installed': [len(train)+64-fresh['paired_cursor_interval'][1],
                                                 len(train)+64-fresh['paired_cursor_interval'][0]],
            'conditional_scores': scores})
    assert rows[0]['fresh']['paired_cursor_interval'][0] > rows[0]['retained_B6_install_cursor']
    assert F(rows[0]['conditional_scores']['unseen']['conditional_deployed_CE_change_from_B6'][0]) > F(16, 1000)
    assert all(row['fresh']['paired_cursor_interval'][1] < row['retained_B6_install_cursor'] for row in rows[1:])
    checked = envelope.LOG_AUDITS+envelope.LOG_CHECKS
    assert 'torch' not in sys.modules
    return {'status': 'CONDITIONAL_FIXED_RULE_PREDICTION_AND_COUNTEREXAMPLE_PASS',
        'registration_source': source, 'retained_control': provenance,
        'evaluation_tapes_used': True, 'new_model_or_baseline_workers': 0,
        'scope': 'fixed registered rule; passive conditional prediction, no actual new crossing, score or installation',
        'premises': 'paired identities admitted at cutoff; exact posterior; proper-mass error<=0.001; all necessary proof refresh/physical/retention/install gates succeed',
        'coefficient': str(COEFFICIENT), 'probability_tolerance': str(envelope.ETA),
        'uniform_production_log_width_upper': str(envelope.WIDTH),
        'reciprocal_power_counterexample': witness, 'cases': rows,
        'exact_pre_target_forecasts': forecasts,
        'actual_wealth_helper_prefix_checks': sum(row['fresh']['actual_wealth_helper_prefix_checks'] for row in rows),
        'independent_exact_log_enclosures': len(checked),
        'maximum_independent_log_terms': max(n for n, _ in checked),
        'maximum_independent_log_operand_bits': max(n for _, n in checked)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8')
    print(text, end='')
