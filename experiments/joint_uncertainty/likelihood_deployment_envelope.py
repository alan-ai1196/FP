"""Conditional persistence/deployment envelopes on the retained n8 tapes.

This is retrospective passive analysis. It reads evaluation labels but runs
no model worker and never supplies scores or installations for failed jobs.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_likelihood_model as reader
from likelihood_persistence_power import (Interval, log, short, floor_at,
    rule, LOG_CHECKS, initial_state, observe_event, commit_event, evaluate,
    fixture, context)
from fp_reference.numerics import log_enclosure
from fp_reference.persistence import next_wealth
from log_enclosure_audit import verify_log_ratio

SOURCE = '86083a0'
ETA, BITS, GRID = F(1, 1000), 32768, 16
WIDTH = 8*F(1, 3)**25/(25*(1-F(1, 9)))
OUTPUT = ROOT/'evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_ENVELOPE.json'
LOG_AUDITS = []
INPUTS = (
    'experiments/joint_uncertainty/joint_model.py',
    'experiments/joint_uncertainty/run_likelihood_model.py',
    'experiments/joint_uncertainty/LIKELIHOOD_MODEL_PROTOCOL.md',
    'experiments/adaptive_uncertainty/adaptive_model.py',
    'experiments/adaptive_uncertainty/analyze_adaptive.py',
    'experiments/relation_noise/model.py',
    'src/reference_compiler/fp_reference/numerics.py',
    'src/reference_compiler/fp_reference/persistence.py',
    'scripts/log_enclosure_audit.py',
)


@lru_cache(maxsize=4096)
def gain_interval(probability):
    assert F(99, 1000) <= probability <= F(901, 1000)
    interval = log_enclosure(2*probability, terms=12, bit_limit=BITS)
    checked = verify_log_ratio(2*probability, F(1), interval.lower, interval.upper)
    assert interval.upper-interval.lower <= WIDTH
    LOG_AUDITS.append((checked.terms, checked.maximum_operand_bits))
    return interval


def update(wealth, gain):
    assert wealth >= 0 and 1+gain/8 > 0
    return floor_at(wealth*(1+gain/8), GRID)


@lru_cache(maxsize=4096)
def gain_tube(probability):
    assert F(1, 10) <= probability <= F(9, 10)
    # A lower enclosure is not substituted for an upper bound. The width
    # covers the actual production lower log at every point inside the tube;
    # no monotonicity of the enclosure algorithm is presumed.
    lower = gain_interval(probability-ETA).lower-WIDTH
    upper = gain_interval(probability+ETA).upper
    assert 1+lower/8 > 0 and lower <= upper
    return lower, upper


def crossings(exact, evaluation, cutoff):
    wealth = [F(1)]*3
    first = [None]*3
    at_crossing = [None]*3
    for offset, (i, j, label) in enumerate(evaluation):
        p = exact[i, j][label]
        low, high = gain_tube(p)
        gains = (gain_interval(p).lower, low, high)
        for path, gain in enumerate(gains):
            wealth[path] = update(wealth[path], gain)
            if first[path] is None and wealth[path] >= 4:
                first[path] = cutoff+offset+1
                at_crossing[path] = str(wealth[path])
    ref, latest, earliest = first
    assert ref is not None and latest is not None and earliest is not None
    assert earliest <= ref <= latest
    return {'reference_cursor': ref, 'AMP_earliest_cursor': earliest,
            'AMP_latest_cursor': latest,
            'paired_cursor_interval': [max(ref, earliest), max(ref, latest)],
            'reference_wealth_at_crossing': at_crossing[0],
            'lower_tube_wealth_at_crossing': at_crossing[1],
            'upper_tube_wealth_at_crossing': at_crossing[2]}


@lru_cache(maxsize=4096)
def risk(probability_zero, target_zero):
    return -target_zero*log(probability_zero)-(1-target_zero)*log(1-probability_zero)


def risk_tube(probability_zero, target_zero):
    lo, hi = probability_zero-ETA, probability_zero+ETA
    left, right = risk(lo, target_zero), risk(hi, target_zero)
    best = risk(max(lo, min(target_zero, hi)), target_zero)
    # Binary CE is convex; its minimum is at the clipped true probability
    # and its maximum on this closed interval is at an endpoint.
    return Interval(best.lo, max(left.hi, right.hi))


def mean_interval(values):
    values = tuple(values)
    return sum(values, Interval.point(0))/len(values)


def score_envelopes(case, exact, hidden, edges, evaluation, cutoff, paired):
    uniform = log(F(2))
    cursor_by_pair = {event[:2]: cutoff+i for i, event in enumerate(evaluation)}
    exact_risk, tube = {}, {}
    for pair, probabilities in exact.items():
        target_zero = F(1, 10) if hidden[pair[0]]^hidden[pair[1]] else F(9, 10)
        exact_risk[pair] = risk(probabilities[0], target_zero)
        tube[pair] = risk_tube(probabilities[0], target_zero)
    results = {}
    for name, pairs in (('unseen', reader.model.unseen_pairs(case[0], edges)),
                        ('full_domain', tuple(product(range(case[0]), repeat=2)))):
        possible, delays = [], []
        # The registered policy installs at paired crossing if its remaining
        # gates succeed. This enumerates the enclosing cursor set, without
        # claiming every endpoint is attainable by one physical AMP path.
        for installed in range(paired[0], paired[1]+1):
            possible.append(mean_interval(uniform if cursor_by_pair[pair] < installed
                                          else tube[pair] for pair in pairs))
            delays.append(mean_interval(uniform-tube[pair] if cursor_by_pair[pair] < installed
                                        else Interval.point(0) for pair in pairs))
        results[name] = {
            'contexts': len(pairs),
            'reference_candidate_expected_CE': short(mean_interval(exact_risk[p] for p in pairs)),
            'AMP_candidate_expected_CE': short(mean_interval(tube[p] for p in pairs)),
            'deployed_expected_CE_if_installed': short(Interval(min(v.lo for v in possible), max(v.hi for v in possible))),
            'deployment_minus_same_AMP_candidate_CE': short(Interval(min(v.lo for v in delays), max(v.hi for v in delays))),
        }
    return results


def exhaustive_tube_audit():
    """All six-event label/three-forecast paths through a native learner."""
    cfg, graph, online, _ = fixture(2)
    initial = initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                            spec=online.learner, bit_limit=BITS)
    prefixes = {}

    def native_tree(state, past):
        if len(past) == 6:
            return
        query = (0, 0) if len(past) == 2 or len(past) == 3 and past[-1] else (0, 1)
        prediction = evaluate(graph, cfg.semantics, state.theta, context(2, *query), bit_limit=BITS)
        prefixes[past] = prediction.probabilities
        for label in (0, 1):
            after = commit_event(observe_event(graph, state, online.learner, prediction, label,
                                 bit_limit=BITS), online.learner, bit_limit=BITS)
            assert after.cursor == after.optimizer_steps == len(past)+1
            assert after.unit_count == 0 and not any(after.gradient_sum)
            native_tree(after, past+(label,))

    native_tree(initial, ())
    checks, leaves = 0, 0

    def physical_tree(past, wealth, lower, upper):
        nonlocal checks, leaves
        if len(past) == 6:
            leaves += 1
            return
        probabilities = prefixes[past]
        for perturbation in (-ETA, F(0), ETA):
            proper = (probabilities[0]+perturbation, probabilities[1]-perturbation)
            assert sum(proper) == 1 and min(proper) > 0
            for label in (0, 1):
                lo, hi = gain_tube(probabilities[label])
                gain = gain_interval(proper[label]).lower
                assert lo <= gain <= hi
                low_after, high_after = update(lower, lo), update(upper, hi)
                actual = next_wealth(wealth, gain, rule(), bit_limit=BITS)
                assert actual == update(wealth, gain)
                assert low_after <= actual <= high_after
                checks += 1
                physical_tree(past+(label,), actual, low_after, high_after)

    physical_tree((), F(1), F(1), F(1))
    assert leaves == 6**6 and checks == sum(6**i for i in range(1, 7))
    return {'native_prediction_prefixes': len(prefixes), 'native_unit_branches': 2*len(prefixes),
            'complete_label_and_proper_forecast_paths': leaves, 'actual_floor_enclosure_checks': checks,
            'scope': 'three rational proper-forecast perturbations per pre-target cut; no GPU execution'}


def audit():
    source = reader.model.git('rev-parse', SOURCE)
    # Only passive input/math provenance is compared. Main's physical storage
    # can evolve; that does not become an executed model result for this source.
    for name in INPUTS:
        assert (ROOT/name).is_file(), name
    assert not reader.model.git('diff', source, '--', *INPUTS)
    assert not reader.model.git('status', '--porcelain', '--', *INPUTS)
    controls, baseline_reference = reader.model.retained_baselines()
    negative_precision = 0
    for forged_probability in (F(0), F(1), F(99, 1000), F(901, 1000)):
        try:
            gain_tube(forged_probability)
        except AssertionError:
            negative_precision += 1
        else:
            raise AssertionError('unsupported reference probability accepted')
    small = exhaustive_tube_audit()
    rows = []
    for case, control in zip(reader.model.CASES, controls):
        hidden, edges, train, evaluation = reader.model.data(case)
        counts = reader.model.counts_from_training(case[0], train)
        exact, _, _ = reader.posterior_predictions(case[0], counts, case[1], evaluation)
        fresh = crossings(exact, evaluation, len(train))
        scores = score_envelopes(case, exact, hidden, edges, evaluation, len(train), fresh['paired_cursor_interval'])
        for name, record in scores.items():
            value = F(control['adaptive_exact_'+name]['expected_CE_binary64'])
            lo, hi = map(F, record['reference_candidate_expected_CE'])
            assert lo-F(1, 1 << 42) <= value <= hi+F(1, 1 << 42)
        rows.append({'case': case, 'training_events': len(train), 'evaluation_events': len(evaluation),
            'fresh': fresh,
            'remaining_forecasts_if_installed': [len(train)+64-fresh['paired_cursor_interval'][1],
                                                len(train)+64-fresh['paired_cursor_interval'][0]],
            'conditional_scores': scores})
    assert 'torch' not in sys.modules
    checked = LOG_AUDITS+LOG_CHECKS
    return {'status': 'PASSIVE_CONDITIONAL_ENVELOPE_AUDIT_PASS',
        'registration_source': source, 'baseline_reference': baseline_reference,
        'evaluation_tapes_used': True, 'new_model_or_baseline_workers': 0,
        'scope': 'retrospective conditional scalar envelopes, not observed FP scores, model completion, prospective power or installation authority',
        'premises': 'actual reference posterior; admitted paired identities at cutoff; original bound6/bet3/4/alpha1/4/grid16; proper-mass error<=0.001; successful required computations; remaining ordinary install gates for conditional deployed scores',
        'probability_tolerance': str(ETA), 'uniform_production_log_width_upper': str(WIDTH),
        'no_install_uniform_expected_CE': short(log(F(2))),
        'unsupported_reference_probability_rejections': negative_precision,
        'exhaustive_tube_audit': small, 'cases': rows,
        'independent_exact_log_enclosures': len(checked),
        'maximum_independent_log_terms': max(n for n, _ in checked),
        'maximum_independent_log_operand_bits': max(n for _, n in checked)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
