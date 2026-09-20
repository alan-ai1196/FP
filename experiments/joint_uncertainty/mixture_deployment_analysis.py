"""Two fixed precision-matched procedures on exposed n8 tapes, conditionally.

No coefficient search, model worker, imputed failed result or Runtime token.
The declarations come from the preceding committed worldwise power proof.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import likelihood_deployment_envelope as envelope
import run_likelihood_deployment as fixed_experiment
import predictable_mixture_state as oracle
from fp_reference.persistence import ArcsinePersistenceRule, PersistenceRule, next_wealth
from fp_reference.persistence_mixture import initial_coefficients, next_mixture, step_work

B, C, GRID, HORIZON, BITS = F(13, 8), F(1, 3), 96, 64, 32768
OUTPUT = ROOT/'evidence/minimal/FP_MIXTURE_DEPLOYMENT_ANALYSIS.json'
SELF_OUTPUT = ROOT/'evidence/minimal/FP_MIXTURE_DEPLOYMENT_READER_AUDIT.json'
PROTOCOL = 'experiments/joint_uncertainty/MIXTURE_DEPLOYMENT_ANALYSIS.md'
DEPENDENCIES = ('src/reference_compiler', 'scripts', 'experiments/joint_uncertainty',
                'experiments/adaptive_uncertainty', 'experiments/relation_noise')
DATA_INPUTS = ('experiments/joint_uncertainty/joint_model.py',
               'experiments/adaptive_uncertainty/analyze_adaptive.py',
               'experiments/adaptive_uncertainty/adaptive_model.py',
               'experiments/relation_noise/model.py')


def declarations(*, horizon=HORIZON, grid=GRID, alpha=F(1, 4)):
    return {'mixture': ArcsinePersistenceRule('mixture', 1, horizon, alpha, B, 12, grid),
            'fixed_control': PersistenceRule('fixed-control', 1, horizon, alpha, C*B, B, 12, grid)}


def start(rule):
    return (initial_coefficients(rule, bit_limit=BITS) if type(rule) is ArcsinePersistenceRule else None, F(1))


def advance(state, score, epoch, rule):
    numbers, wealth = state
    if type(rule) is ArcsinePersistenceRule:
        following, after = next_mixture(numbers, wealth, score, epoch, rule, bit_limit=BITS)
        assert following == oracle.rounded_step(numbers, score/B)
        independent = oracle.independent_readout(oracle.expanded(tuple(F(n, 1 << rule.coefficient_grid_bits) for n in following)))
        assert after == independent
        return following, after
    after = next_wealth(wealth, score, rule, bit_limit=BITS)
    assert after == envelope.floor_at(wealth*(1+C*score), rule.wealth_grid_bits)
    return None, after


def enclosure_audit():
    checks = 0
    # The large threshold keeps every short test path live. Actual lower
    # scores need not be log values for this algebraic order property.
    for rule in declarations(horizon=4, grid=7, alpha=F(1, 1024)).values():
        for word in product((F(-1), F(0), F(1, 2)), repeat=4):
            for perturbations in product((F(-1, 100), F(1, 100)), repeat=4):
                low = actual = high = start(rule)
                for t, (g, perturbation) in enumerate(zip(word, perturbations)):
                    low = advance(low, g-F(1, 100), t, rule)
                    actual = advance(actual, g+perturbation, t, rule)
                    high = advance(high, g+F(1, 100), t, rule)
                    assert low[1] <= actual[1] <= high[1]
                    if low[0] is not None:
                        assert all(a <= b <= c for a, b, c in zip(low[0], actual[0], high[0]))
                    checks += 1
    return {'complete_score_and_perturbation_words_per_method': 3**4*2**4,
            'paired_method_prefix_enclosures': checks,
            'independent_readout_and_floor_checks': 3*checks}


def payload(state):
    numbers, wealth = state
    return {'coefficient_cells': 0 if numbers is None else len(numbers),
            'coefficient_unsigned_payload_bits': 0 if numbers is None else sum(n.bit_length() for n in numbers),
            'scalar_wealth_numerator_denominator_bits': wealth.numerator.bit_length()+wealth.denominator.bit_length()}


def crossings(exact, evaluation, cutoff, rule):
    states = [start(rule) for _ in range(3)]
    first, epochs = [None]*3, [0]*3
    minimum = F(1)
    for offset, (i, j, label) in enumerate(evaluation):
        p = exact[i, j][label]
        lo, hi = envelope.gain_tube(p)
        gains = envelope.gain_interval(p).lower, lo, hi
        assert all(-B <= value <= B for value in gains)
        for path, gain in enumerate(gains):
            if first[path] is not None:
                continue
            states[path] = advance(states[path], gain, offset, rule)
            epochs[path] += 1
            if path == 0:
                minimum = min(minimum, states[path][1])
            if states[path][1]*rule.alpha >= 1:
                first[path] = cutoff+offset+1
    ref, latest, earliest = first
    if earliest is None:
        assert ref is None and latest is None
    if latest is not None:
        assert ref is not None and earliest <= ref <= latest
    if ref is None or earliest is None:
        possible = (None,)
        pair_earliest = pair_latest = None
    else:
        pair_earliest = max(ref, earliest)
        pair_latest = None if latest is None else max(ref, latest)
        possible = tuple(range(pair_earliest, (pair_latest if pair_latest is not None else cutoff+HORIZON)+1))
        if pair_latest is None:
            possible += (None,)
    detail = {'reference_cursor': ref, 'AMP_earliest_possible_cursor': earliest,
        'AMP_guaranteed_by_cursor': latest, 'paired_first_possible_cursor': pair_earliest,
        'paired_guaranteed_by_cursor': pair_latest,
        'no_paired_crossing_within_horizon_forced': ref is None or earliest is None,
        'continued_uniform_deployment_in_envelope': None in possible,
        'reference_minimum_wealth': str(minimum),
        'reference_terminal_or_crossing_wealth': str(states[0][1]),
        'arithmetic_prefix_checks': sum(epochs), 'reference_completed_epochs': epochs[0],
        'reference_statistic_payload': payload(states[0]),
        'reference_curve_update_work': sum(step_work(t) for t in range(epochs[0])) if type(rule) is ArcsinePersistenceRule else 0}
    return detail, possible


def risks(case, exact, hidden, edges, evaluation, cutoff, possible):
    order = {tuple(row[:2]): cutoff+i for i, row in enumerate(evaluation)}
    assert len(order) == len(evaluation) == 64
    tube, reference = {}, {}
    for pair, probabilities in exact.items():
        true_zero = F(1, 10) if hidden[pair[0]]^hidden[pair[1]] else F(9, 10)
        tube[pair] = envelope.risk_tube(probabilities[0], true_zero)
        reference[pair] = envelope.risk(probabilities[0], true_zero)
    uniform = envelope.log(F(2))
    result = {}
    for subset, pairs in (('unseen', envelope.reader.model.unseen_pairs(case[0], edges)),
                           ('full_domain', tuple(product(range(case[0]), repeat=2)))):
        deployed = []
        for installed in possible:
            deployed.append(envelope.mean_interval(uniform if installed is None or order[pair] < installed
                                                    else tube[pair] for pair in pairs))
        result[subset] = {'contexts': len(pairs),
            'reference_candidate_CE': envelope.short(envelope.mean_interval(reference[p] for p in pairs)),
            'AMP_candidate_CE': envelope.short(envelope.mean_interval(tube[p] for p in pairs)),
            'conditional_deployed_CE': envelope.short(envelope.Interval(min(v.lo for v in deployed), max(v.hi for v in deployed)))}
    return result


def censoring_audit():
    words = ((0, 0, 0),)*HORIZON
    for rule in declarations().values():
        detail, possible = crossings({(0, 0): (F(1, 2), F(1, 2))}, words, 0, rule)
        assert detail['reference_cursor'] is None and detail['AMP_earliest_possible_cursor'] is None
        assert detail['no_paired_crossing_within_horizon_forced'] and possible == (None,)
    fixed = declarations()['fixed_control']
    p = F(5337, 10000)
    absent, possible = crossings({(0, 0): (p, 1-p)}, words, 0, fixed)
    assert absent['reference_cursor'] is None and absent['AMP_earliest_possible_cursor'] is not None
    assert possible == (None,) and absent['no_paired_crossing_within_horizon_forced']
    p = F(5347, 10000)
    uncertain, possible = crossings({(0, 0): (p, 1-p)}, words, 0, fixed)
    assert uncertain['reference_cursor'] < HORIZON and uncertain['AMP_guaranteed_by_cursor'] is None
    assert None in possible and not uncertain['no_paired_crossing_within_horizon_forced']
    evaluation = tuple((i, j, 0) for i, j in product(range(8), repeat=2))
    exact = {(i, j): (p, 1-p) for i, j, _ in evaluation}
    values = risks((8, 'synthetic-report-audit', 0), exact, (0,)*8, (), evaluation, 0, possible)
    uniform = envelope.log(F(2))
    for score in values.values():
        lo, hi = map(F, score['conditional_deployed_CE'])
        assert lo < uniform.lo <= uniform.hi <= hi
    return {'status': 'PASS', 'all_paths_censored_procedures': 2,
        'AMP_upper_crossing_cannot_replace_missing_reference': True,
        'missing_AMP_lower_crossing_keeps_uniform_deployment_in_risk': True,
        'ambiguous_reference_cursor': uncertain['reference_cursor'],
        'scope': 'synthetic report branches; no native model or physical execution'}


def audit():
    model = fixed_experiment.model
    source = model.git('rev-parse', 'HEAD')
    assert not model.git('status', '--porcelain', '--', *DEPENDENCIES), 'commit analysis dependencies before reading tapes'
    assert not model.git('diff', '8ccacc0', '--', *DATA_INPUTS)
    controls, provenance = fixed_experiment.retained_controls()
    baselines, baseline_provenance = model.retained_baselines()
    prediction_path = 'evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_PREDICTION.json'
    fixed_prediction = json.loads((ROOT/prediction_path).read_text(encoding='utf-8'))
    assert fixed_prediction == json.loads(model.git('show', '5c39a26:'+prediction_path))
    small = enclosure_audit()
    rows, score_checks = [], 0
    for case, control, baseline, prediction in zip(model.CASES, controls['workers'], baselines, fixed_prediction['cases']):
        assert tuple(control['case']) == tuple(baseline['case']) == tuple(prediction['case']) == case
        hidden, edges, train, evaluation = model.data(case)
        counts = model.counts_from_training(case[0], train)
        exact, _, _ = envelope.reader.posterior_predictions(case[0], counts, case[1], evaluation)
        assert len(exact) == len(evaluation) == HORIZON
        methods = {}
        for name, rule in declarations().items():
            fresh, possible = crossings(exact, evaluation, len(train), rule)
            scores = risks(case, exact, hidden, edges, evaluation, len(train), possible)
            for subset, result in scores.items():
                lo, hi = map(F, result['reference_candidate_CE'])
                for prior in (control['result']['scores'], baseline):
                    value = F(prior['adaptive_exact_'+subset]['expected_CE_binary64'])
                    assert lo-F(1, 1 << 42) <= value <= hi+F(1, 1 << 42)
                    score_checks += 1
            methods[name] = {'fresh': fresh, 'scores': scores}
        differences = {}
        for subset in ('unseen', 'full_domain'):
            mix = envelope.Interval(*map(F, methods['mixture']['scores'][subset]['conditional_deployed_CE']))
            fixed = envelope.Interval(*map(F, methods['fixed_control']['scores'][subset]['conditional_deployed_CE']))
            differences[subset] = envelope.short(mix-fixed)
        rows.append({'case': case, 'training_events': len(train), 'evaluation_events': HORIZON,
            'retained_B6_actual_install': control['result']['install_cursor'],
            'registered_B13_8_conditional_paired_cursors': prediction['fresh']['paired_cursor_interval'],
            'procedures': methods, 'mixture_minus_fixed_conditional_CE': differences})
    assert model.git('rev-parse', 'HEAD') == source and not model.git('status', '--porcelain', '--', *DEPENDENCIES)
    checked = envelope.LOG_AUDITS+envelope.LOG_CHECKS
    assert 'torch' not in sys.modules
    return {'status': 'CONDITIONAL_PRECISION_MATCHED_ANALYSIS_PASS', 'analysis_source': source,
        'protocol': PROTOCOL, 'evaluation_tapes_used': True, 'new_model_or_baseline_workers': 0,
        'scope': 'two fixed retrospective procedures; conditional scalar crossings and risk, no owned execution or imputed failed result',
        'premises': 'unchanged exact posterior; pre-cut admission; proper-mass error<=0.001; complete range, work, physical, retention, bridge and install gates succeed',
        'declaration': {'bound': str(B), 'horizon': HORIZON, 'epoch_events': 1, 'alpha_per_path': '1/4',
            'log_terms': 12, 'mixture_coefficient_bits': GRID, 'fixed_wealth_bits': GRID, 'fixed_coefficient': str(C)},
        'retained_owned_controls': provenance, 'retained_posterior_controls': baseline_provenance,
        'enclosure_audit': small, 'reference_forecasts': 256, 'rechecked_retained_reference_candidate_scores': score_checks,
        'independent_exact_log_checks': len(checked), 'maximum_independent_log_terms': max(t for t, _ in checked),
        'maximum_independent_log_operand_bits': max(b for _, b in checked), 'cases': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    result = censoring_audit() if args.self_test else audit()
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        (SELF_OUTPUT if args.self_test else OUTPUT).write_text(text, encoding='utf-8')
    print(text, end='')
