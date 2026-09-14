"""Independent analysis of retained n8 likelihood model attempts.

No target worker is run. Failed jobs receive no imputed model score. Stored
mass probabilities, raw divisions, reference forecasts and actual deployment
are kept distinct. Reconstructed scalar evidence grants no Runtime authority.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
from statistics import mean
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/adaptive_uncertainty'))
import run_likelihood_model as model
from analyze_adaptive import (check_score, check_baseline, posterior_predictions,
                              DEPENDENCIES as BASELINE_DEPENDENCIES)
from fp_reference.numerics import log_enclosure
from log_enclosure_audit import verify_log_ratio

SOURCE = '86083a0'
SELF = Path(__file__).relative_to(ROOT).as_posix()
DEPENDENCIES = tuple(dict.fromkeys(model.DEPENDENCIES+BASELINE_DEPENDENCIES+
                                   ('experiments/adaptive_uncertainty/analyze_adaptive.py',)))


def decode_single(word):
    """Independent exact IEEE binary32 decoding, without a device or cast."""
    assert type(word) is int and 0 <= word < 1 << 32
    exponent, mantissa = (word >> 23) & 255, word & ((1 << 23)-1)
    assert exponent != 255, 'nonfinite retained word'
    value = F(mantissa, 1 << 149) if exponent == 0 else F((1 << 23)+mantissa)
    if exponent:
        power = exponent-150
        value = value*(1 << power) if power >= 0 else value/F(1 << -power)
    return -value if word >> 31 else value


def readouts(records, evaluation, cutoff, candidate):
    masses, raw = {}, {}
    for row in records:
        role, cursor = row['candidate'], row['cursor']
        assert role in ('baseline', 'posterior') and (candidate or role == 'baseline')
        assert type(cursor) is int and cutoff <= cursor < cutoff+len(evaluation)
        assert tuple(row['pair']) == evaluation[cursor-cutoff][:2], 'readout has a stale context/cursor'
        key = role, cursor
        assert key not in masses, 'duplicate retained readout'
        assert len(row['mass_words']) == len(row['division_words']) == 2
        m = tuple(decode_single(word) for word in row['mass_words'])
        r = tuple(decode_single(word) for word in row['division_words'])
        assert min(m) > 0 and all(0 < v < 1 for v in r)
        assert max(m) <= 16
        if role == 'baseline':
            assert m == (F(1), F(1)) and r == (F(1, 2), F(1, 2))
        masses[key], raw[key] = tuple(v/sum(m) for v in m), r
    expected = {(role, cutoff+i) for i in range(len(evaluation))
                for role in (('baseline', 'posterior') if candidate else ('baseline',))}
    assert set(masses) == set(raw) == expected, 'incomplete retained forecast set'
    return masses, raw


@lru_cache(maxsize=4096)
def lower_gain(probability):
    interval = log_enclosure(2*probability, terms=12, bit_limit=32768)
    verify_log_ratio(probability, F(1, 2), interval.lower, interval.upper)
    assert -6 <= interval.lower <= interval.upper <= 6
    return interval.lower


def crossing(probabilities, evaluation, cutoff):
    wealth, maximum, signs = F(1), F(1), Counter()
    crossed = None
    for offset, (i, j, label) in enumerate(evaluation):
        gain = lower_gain(probabilities[i, j][label])
        signs['positive' if gain > 0 else 'negative' if gain < 0 else 'zero'] += 1
        unrounded = wealth*(1+gain/8)
        wealth = F(unrounded.numerator*65536//unrounded.denominator, 65536)
        maximum = max(maximum, wealth)
        if wealth >= 4:
            crossed = cutoff+offset+1
            break
    return {'crossing_cursor': crossed, 'events': offset+1,
            'terminal_or_crossing_wealth': str(wealth), 'maximum_wealth': str(maximum),
            'gain_signs': dict(signs)}


def check_fresh(result, exact, amp, evaluation, cutoff):
    fresh = result['fresh']
    assert fresh is not None
    assert type(fresh['identities']) is int and 0 <= fresh['identities'] <= 2
    assert F(result['alpha_spent']) == F(fresh['identities'], 4)
    installed = result['install_cursor']
    assert fresh['install_transport_checked'] == (installed is not None)
    if fresh['identities'] == 0:
        assert not fresh['events'] and not fresh['crossings'] and installed is None
        return {'scope': 'no admitted identities; no reconstructed install'}, 0
    assert result['cutoff']['candidate_selected'] and exact is not None and amp is not None
    if fresh['identities'] == 1:
        # The compact worker summary omits individual path labels. It cannot
        # identify which of the two paths was admitted in this unusual case.
        assert installed is None and len(fresh['crossings']) <= 1
        return {'scope': 'UNRESOLVED_FROM_MINIMAL_RECORD: one identity without its path label'}, 0
    reference, device = crossing(exact, evaluation, cutoff), crossing(amp, evaluation, cutoff)
    actual_crossings = sorted(r['crossing_cursor'] for r in (reference, device) if r['crossing_cursor'] is not None)
    assert fresh['crossings'] == actual_crossings
    assert fresh['events'] == reference['events']+device['events']
    if installed is not None:
        assert len(actual_crossings) == 2 and installed == max(actual_crossings), 'install precedes paired fresh crossing'
    return {'reference': reference, 'CUDA_stored_mass': device,
            'paired_crossing_without_install': len(actual_crossings) == 2 and installed is None,
            'scope': 'independent scalar/cursor replay; worker source checked the full owned transport'}, 1


def check_job(row, source, device):
    assert row['execution_source'] == source
    job = row['completed_job']
    assert job['commit_limit'] == model.CAP and job['attached_before_resume']
    assert row['worker_status'] in ('FAILED', 'EXECUTED')
    if row['worker_status'] == 'FAILED':
        return False
    assert 'report_audit_failure' not in row
    assert job['exit_code'] == 0 and not job['timed_out'] and not job['limit_terminated_processes']
    assert max(job['peak_process_commit'], job['peak_job_commit']) <= model.CAP
    result = row['result']
    assert result['device'] == device
    host = result['host']
    assert result['process_id'] == job['process_id'] == host['process_id']
    assert host['creation_100ns'] == job['process_creation_100ns']
    assert host['lifetime_process_commit_peak'] <= job['peak_process_commit']
    assert host['job_commit_peak'] <= job['peak_job_commit']
    for clock in ('user', 'kernel'):
        assert max(host[f'process_{clock}_100ns'], host[f'job_{clock}_100ns']) <= job[f'{clock}_100ns']
    return True


def check_result(result, case, baseline):
    hidden, edges, train, evaluation = model.data(case)
    cutoff, count = len(train), len(evaluation)
    assert result['case'] == list(case) and result['training_events'] == cutoff and result['evaluation_events'] == count == 64
    assert result['counts'] == [list(row) for row in model.counts_from_training(case[0], train)]
    assert result['class_certificate'] is False, 'the one-proposal class remains UNRESOLVED'
    assert result['packed_peak'] <= model.PACKED
    checked = result['phase_audit_status'] == 'ALL_EXECUTED_PHASES_CHECKED'
    if checked:
        phases = result['independent_CUDA']
        assert phases['checked_phases'] == result['independent_binary64_phases'] > 0
        assert phases['refused_phases'] == 0 and phases['actual_arena_bytes'] == model.ARENA
        assert phases['maximum_output_cells'] <= model.CELLS and phases['largest_phase_frame_used'] <= model.FRAME
    else:
        assert result['phase_audit_status'] == 'NUMERICAL_REFUSAL; NO_COMPLETE_REPLAY_CLAIM'
        assert result['independent_CUDA'] is None and result['independent_binary64_phases'] is None
    if result['run_status'] != 'SEALED_CUDA_STREAM':
        assert result['run_status'] == 'HALTED_UNRESOLVED' and result['halted'] is not None
        assert not result['scores'] and not result['CUDA_readouts']
        return {'status': 'HALTED_UNRESOLVED', 'halted': result['halted'], 'no_imputed_tail': True}, 0, 0
    assert checked and result['halted'] is None and result['cursor'] == cutoff+count
    cut = result['cutoff']
    assert cut['search_status'] == 'UNRESOLVED'
    candidate = result['candidate_native'] is not None
    assert cut['candidate_created'] is candidate and cut['compared_members'] == int(candidate)
    assert not cut['candidate_selected'] or candidate
    if candidate:
        _, graph, _, _, _, _ = model.setup(case)
        assert result['candidate_native'] == graph.counts()
        assert cut['proposal_status'] == 'PROPOSED_NATIVE'
    assert result['reference_posterior_forecast_checks'] == (count if candidate else 0)
    mass, raw = readouts(result['CUDA_readouts'], evaluation, cutoff, candidate)
    exact, _, _ = posterior_predictions(case[0], model.counts_from_training(case[0], train), case[1], evaluation)
    amp = {pair[:2]: mass['posterior', cutoff+i] for i, pair in enumerate(evaluation)} if candidate else None
    decision, decision_checks = check_fresh(result, exact if candidate else None, amp, evaluation, cutoff)
    installed = result['install_cursor']
    predictions = {'adaptive_exact': exact}
    divisions = {'adaptive_exact': None}
    for label in ('candidate_stream', 'deployed_stream'):
        if label == 'candidate_stream' and not candidate:
            continue
        predictions[label], divisions[label] = {}, {}
        for offset, event in enumerate(evaluation):
            cursor, pair = cutoff+offset, event[:2]
            role = 'posterior' if label == 'candidate_stream' or installed is not None and cursor >= installed else 'baseline'
            predictions[label][pair], divisions[label][pair] = mass[role, cursor], raw[role, cursor]
    expected_scores = {label+'_'+subset for label in predictions for subset in ('unseen', 'full_domain')}
    assert set(result['scores']) == expected_scores
    score_checks = 0
    for label in predictions:
        for subset, pairs in (('unseen', model.unseen_pairs(case[0], edges)),
                              ('full_domain', tuple(product(range(case[0]), repeat=2)))):
            record = result['scores'][label+'_'+subset]
            check_score(record, predictions[label], divisions[label], hidden, pairs)
            if label == 'adaptive_exact':
                assert record == baseline[label+'_'+subset]
            score_checks += 1
    for label, tolerance in (('binary64_maxima', F(1, 10**9)), ('CUDA_maxima', F(1, 100))):
        for key, value in result[label].items():
            bound = F(1, 1000) if label == 'CUDA_maxima' and key in ('probability_error', 'division_error') else tolerance
            assert 0 <= F(value) <= bound
    if candidate:
        error = max(abs(a-b) for pair in exact for a, b in zip(amp[pair], exact[pair]))
        assert F(result['maximum_candidate_mass_posterior_error']) == error <= F(1, 1000)
        combined_error = max(abs(a-b) for offset, event in enumerate(evaluation)
                             for values in (mass['posterior', cutoff+offset], raw['posterior', cutoff+offset])
                             for a, b in zip(values, exact[event[:2]]))
        assert combined_error <= F(result['CUDA_maxima']['probability_error'])
    else:
        assert result['maximum_candidate_mass_posterior_error'] is None
    division_error = max(abs(p-q) for key in mass for p, q in zip(mass[key], raw[key]))
    assert division_error <= F(result['CUDA_maxima']['division_error'])
    return {'status': 'SEALED_CUDA_STREAM', 'candidate': candidate, 'install_cursor': installed,
            'fresh': decision, 'class': 'UNRESOLVED: one owned v7 proposal, no complete-class proof',
            'expected_CE_binary64': {key: value['expected_CE_binary64'] for key, value in result['scores'].items()},
            'maximum_candidate_mass_posterior_error': result['maximum_candidate_mass_posterior_error']}, score_checks, decision_checks


def failure_reason(row):
    text = row.get('report_audit_failure') or row.get('result', {}).get('traceback')
    if text:
        return text.strip().splitlines()[-1]
    return 'timeout; stage unreported' if row['completed_job']['timed_out'] else 'failed without a reported stage'


def verify(journal, *, partial=False, source_check=True):
    report = json.loads(Path(journal).read_text(encoding='utf-8'))
    source = model.git('rev-parse', SOURCE)
    if source_check:
        assert not model.git('diff', source, '--', *DEPENDENCIES), 'analysis dependencies differ from the execution source'
        assert not model.git('ls-files', '--others', '--exclude-standard', '--', *DEPENDENCIES)
        assert model.git('ls-files', '--', SELF) and not model.git('status', '--porcelain', '--', SELF), 'commit the analyzer first'
    assert report['registration_source'] == source and report['protocol_origin'] == model.PROTOCOL_ORIGIN
    registration = json.loads(json.dumps(model.preflight()))
    assert report['registration'] == registration
    assert report['prior_auditor_failure'] == model.prior_auditor_failure(registration)
    rows = report['workers']
    assert 0 <= len(rows) <= len(model.CASES)
    assert [(row['case_index'], tuple(row['case'])) for row in rows] == list(enumerate(model.CASES[:len(rows)]))
    allowed = ('PARTIAL_EXECUTION', 'COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES', 'STOPPED_AUDITOR_FAILURE')
    assert report['status'] in allowed
    if not partial:
        assert report['status'] != 'PARTIAL_EXECUTION', 'matrix is still running; use --partial to inspect the retained prefix'
    if report['status'] in ('COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES'):
        assert len(rows) == len(model.CASES)
        assert (report['status'] == 'COMPLETE_EXECUTION') == all(row['worker_status'] == 'EXECUTED' for row in rows)
    elif report['status'] == 'STOPPED_AUDITOR_FAILURE':
        assert rows and rows[-1]['worker_status'] == 'FAILED'
    baselines, _ = model.retained_baselines()
    device = baselines[0]['device']
    baseline_checks = 0
    for case, baseline in zip(model.CASES, baselines):
        baseline_checks += check_baseline(baseline, *model.data(case))
    details, score_checks, decision_checks, checked_phases = [], 0, 0, 0
    for row, baseline in zip(rows, baselines):
        if not check_job(row, source, device):
            detail = {'status': 'FAILED', 'reason': failure_reason(row), 'no_imputed_score_or_phase_count': True}
        else:
            detail, scores, decisions = check_result(row['result'], tuple(row['case']), baseline)
            score_checks += scores
            decision_checks += decisions
            if row['result']['phase_audit_status'] == 'ALL_EXECUTED_PHASES_CHECKED':
                checked_phases += row['result']['independent_binary64_phases']
        details.append({'case': row['case'], **detail})
    sealed = [row for row in details if row['status'] == 'SEALED_CUDA_STREAM']
    groups = []
    for law in ('iid-c2', 'iid-c4'):
        cases = [row for row in sealed if row['case'][1] == law]
        groups.append({'law': law, 'scored_workers': len(cases),
                       'installed_workers': sum(row['install_cursor'] is not None for row in cases),
                       'expected_CE_binary64': {key: mean(row['expected_CE_binary64'][key] for row in cases if key in row['expected_CE_binary64'])
                           if any(key in row['expected_CE_binary64'] for row in cases) else None
                           for key in ('candidate_stream_unseen', 'deployed_stream_unseen', 'adaptive_exact_unseen')}})
    assert 'torch' not in sys.modules
    return {'journal_status': report['status'], 'execution_source': source,
            'analysis_source': model.git('rev-parse', 'HEAD') if source_check else None,
            'scope': 'retained retrospective outcomes; no new GPU execution, IID draw or Runtime authority',
            'attempted_workers': len(rows), 'sealed_workers': len(sealed),
            'failed_workers': sum(row['status'] == 'FAILED' for row in details),
            'halted_unresolved_workers': sum(row['status'] == 'HALTED_UNRESOLVED' for row in details),
            'independent_model_score_checks': score_checks, 'independent_fresh_decisions': decision_checks,
            'worker_verified_CUDA_and_binary64_phases_each': checked_phases,
            'reused_control_score_checks': baseline_checks, 'new_baseline_workers': 0,
            'original_failed_attempt_preserved': report['prior_auditor_failure'],
            'maximum_completed_job_bytes': max((r['completed_job']['peak_job_commit'] for r in rows), default=None),
            'groups': groups, 'workers': details}


def self_test():
    def rejects(call):
        try:
            call()
        except AssertionError:
            return
        raise AssertionError('forged record was accepted')
    assert decode_single(0x3f800000) == 1 and decode_single(1) == F(1, 1 << 149)
    for value in (0x7f800000, 0x7fc00000, -1, True):
        rejects(lambda value=value: decode_single(value))
    evaluation = ((0, 0, 0),)
    row = {'candidate': 'baseline', 'cursor': 2, 'pair': [0, 0],
           'mass_words': [0x3f800000]*2, 'division_words': [0x3f000000]*2}
    readouts([row], evaluation, 2, False)
    rejects(lambda: readouts([row, row], evaluation, 2, False))
    rejects(lambda: readouts([], evaluation, 2, False))
    stale = deepcopy(row); stale['cursor'] = 1
    rejects(lambda: readouts([stale], evaluation, 2, False))
    wrong = deepcopy(row); wrong['mass_words'][0] = 0
    rejects(lambda: readouts([wrong], evaluation, 2, False))
    future = ((0, 0, 0),)*64
    probabilities = {(0, 0): (F(9, 10), F(1, 10))}
    crossed = crossing(probabilities, future, 2)
    cursor = crossed['crossing_cursor']
    fixture_result = {'fresh': {'identities': 2, 'events': 2*crossed['events'],
                              'crossings': [cursor, cursor], 'install_transport_checked': True},
                      'alpha_spent': '1/2', 'install_cursor': cursor, 'cutoff': {'candidate_selected': True}}
    check_fresh(fixture_result, probabilities, probabilities, future, 2)
    early = deepcopy(fixture_result); early['install_cursor'] -= 1
    rejects(lambda: check_fresh(early, probabilities, probabilities, future, 2))
    reused = deepcopy(fixture_result); reused['fresh']['events'] += 1
    rejects(lambda: check_fresh(reused, probabilities, probabilities, future, 2))
    no_install = deepcopy(fixture_result); no_install['install_cursor'] = None
    no_install['fresh']['install_transport_checked'] = False
    detail, _ = check_fresh(no_install, probabilities, probabilities, future, 2)
    assert detail['paired_crossing_without_install']
    prior = json.loads((ROOT/model.PRIOR_FAILURE_PATH).read_text(encoding='utf-8'))
    failed = prior['workers'][0]
    assert check_job(failed, model.PROTOCOL_ORIGIN, None) is False
    forged = deepcopy(failed); forged['worker_status'] = 'EXECUTED'
    rejects(lambda: check_job(forged, model.PROTOCOL_ORIGIN, None))
    case = model.CASES[0]
    _, _, train, evaluation = model.data(case)
    fake_class = {'case': list(case), 'training_events': len(train), 'evaluation_events': len(evaluation),
                  'counts': [list(row) for row in model.counts_from_training(case[0], train)], 'class_certificate': True}
    rejects(lambda: check_result(fake_class, case, None))
    prefix = verify(model.OUTPUT, partial=True, source_check=False)
    return {'status': 'PASS', 'negative_word_readout_freshness_job_class_checks': 12,
            'paired_crossing_without_install_retained': True,
            'original_failed_job_not_promoted': True, 'current_prefix': prefix,
            'scope': 'analyzer development checks; no fabricated successful model worker'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--journal', type=Path, default=model.OUTPUT)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    assert not args.self_test or not args.partial and args.journal == model.OUTPUT
    print(json.dumps(self_test() if args.self_test else verify(args.journal, partial=args.partial), indent=2))
