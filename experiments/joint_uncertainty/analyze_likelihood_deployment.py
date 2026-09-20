"""Independent scalar/result reader for the registered B=13/8 n8 matrix.

Minimal records distinguish numerical threshold, owned crossing and install.
Full owned phase/lineage/range checks remain the execution's separate evidence.
"""
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from statistics import mean
import argparse
import json
import sys

import run_likelihood_deployment as experiment
import analyze_likelihood_model as common
from fp_reference.numerics import log_enclosure, log_enclosure_work, compare_exact_work
from fp_reference.persistence import REFERENCE_PATH, CUDA_PATH
from fp_reference.persistence_bounds import mass_box_work
from log_enclosure_audit import verify_log_ratio

ROOT, BOUND = experiment.ROOT, experiment.BOUND
SELF = Path(__file__).relative_to(ROOT).as_posix()
DEPENDENCIES = tuple(dict.fromkeys(experiment.DEPENDENCIES+common.DEPENDENCIES+
    ('experiments/joint_uncertainty/analyze_likelihood_model.py',)))


@lru_cache(maxsize=4096)
def gain(probability):
    interval = log_enclosure(2*probability, terms=12, bit_limit=32768)
    verify_log_ratio(probability, F(1, 2), interval.lower, interval.upper)
    # The registered posterior and 0.001 relation leave strict margin inside B.
    assert -BOUND <= interval.lower <= interval.upper <= BOUND
    return interval.lower


def check_fresh(result, exact, amp, evaluation, cutoff, *, domain_rows=64):
    fresh = result['fresh']
    assert fresh is not None
    paths = fresh['paths']
    assert len(paths) == fresh['identities'] <= 2
    assert len({p['score_path'] for p in paths}) == len(paths)
    assert F(result['alpha_spent']) == F(len(paths), 4)
    installed = result['install_cursor']
    assert fresh['install_transport_checked'] == (installed is not None)
    assert not paths or result['cutoff']['candidate_selected']
    details, numerical, owned = [], [], []
    count = 0
    fee = mass_box_work(domain_rows, 2)+log_enclosure_work(12)+compare_exact_work()
    for path in paths:
        name = path['score_path']
        assert name in (REFERENCE_PATH, CUDA_PATH)
        forecasts = exact if name == REFERENCE_PATH else amp
        assert forecasts is not None
        assert F(path['bound']) == BOUND and F(path['bet']) == F(3, 4) and F(path['alpha']) == F(1, 4)
        assert path['start_cursor'] == cutoff and path['epoch_events'] == 0
        assert path['status'] in ('ACTIVE', 'REFERENCE_CROSSED', 'CUDA_CROSSED', 'UNRESOLVED')
        records = path['score_records']
        assert len(records) <= len(evaluation)
        assert [row[0] for row in records] == list(range(cutoff, cutoff+len(records)))
        wealths, crossed = [F(1)], None
        for offset, (cursor, recorded) in enumerate(records):
            assert crossed is None, 'scoring continued after a numerical threshold'
            i, j, label = evaluation[offset]
            raw = wealths[-1]*(1+F(6, 13)*gain(forecasts[i, j][label]))
            wealths.append(F(raw.numerator*65536//raw.denominator, 65536))
            assert F(recorded) == wealths[-1]
            if wealths[-1] >= 4:
                crossed = cursor+1
        assert path['numerical_crossing_cursor'] == crossed
        if crossed is not None:
            numerical.append(crossed)
        completed = path['epochs_completed']
        assert type(completed) is int and max(0, len(records)-1) <= completed <= len(records)
        assert F(path['wealth']) == wealths[completed]
        assert cutoff+completed <= path['cursor'] <= cutoff+len(evaluation)
        crossing = path['crossing_cursor']
        if crossing is not None:
            assert crossing == crossed and completed == len(records)
            assert F(path['crossing_wealth']) == wealths[-1] >= 4
            owned.append(crossing)
        else:
            assert path['crossing_wealth'] is None
            if crossed is not None:
                assert path['status'] == 'UNRESOLVED' and installed is None
        if path['status'] in ('REFERENCE_CROSSED', 'CUDA_CROSSED'):
            assert path['status'] == ('REFERENCE_CROSSED' if name == REFERENCE_PATH else 'CUDA_CROSSED')
            assert crossing is not None
        if path['status'] == 'ACTIVE':
            assert crossed is None and completed == len(records) and path['cursor'] == cutoff+completed
        assert path['ratio_bound_kind'] in ('native-class-cap', 'current-native-mass-box')
        if records:
            assert path['ratio_bound_kind'] == 'current-native-mass-box' and path['ratio_bound'] is not None
        if path['ratio_bound'] is not None:
            ratio = F(path['ratio_bound'])
            assert ratio >= 1 and log_enclosure(ratio, terms=12, bit_limit=32768).upper <= BOUND
        charges = path['refinement_charge_cursors']
        assert charges == list(range(cutoff, cutoff+len(charges)))
        assert len(records) <= len(charges) <= len(records)+1
        assert path['refinement_charged_work'] == fee*len(charges)
        count += len(records)
        details.append({'score_path': name, 'recorded_score_count': len(records),
            'numerical_crossing_cursor': crossed, 'owned_crossing_cursor': crossing,
            'terminal_status': path['status'], 'refinement_work_attempts': len(charges),
            'unretained_numerical_threshold': crossed is not None and crossing is None})
    assert fresh['events'] == count and fresh['numerical_crossings'] == sorted(numerical)
    assert fresh['crossings'] == sorted(owned)
    if installed is not None:
        assert len(owned) == 2 and installed == max(owned), 'installation lacks its paired owned crossing'
    return {'paths': details, 'paired_owned_crossing_without_install': len(owned) == 2 and installed is None,
            'scope': 'recorded scalar prefixes only; worker source supplies whole-domain range and owned transport evidence'}, len(paths)


def verify(journal, *, partial=False, source_check=True):
    report = json.loads(Path(journal).read_text(encoding='utf-8'))
    source = report['registration_source']
    assert source == experiment.model.git('rev-parse', source)
    if source_check:
        assert not experiment.model.git('diff', source, '--', *DEPENDENCIES), 'analysis dependencies differ from execution'
        assert not experiment.model.git('ls-files', '--others', '--exclude-standard', '--', *DEPENDENCIES)
        assert experiment.model.git('ls-files', '--', SELF) and not experiment.model.git('status', '--porcelain', '--', SELF)
    assert report['registration'] == json.loads(json.dumps(experiment.preflight()))
    rows = report['workers']
    assert 0 <= len(rows) <= len(experiment.CASES)
    assert [(r['case_index'], tuple(r['case'])) for r in rows] == list(enumerate(experiment.CASES[:len(rows)]))
    status = report['status']
    assert status in ('PARTIAL_EXECUTION', 'COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES', 'STOPPED_AUDITOR_FAILURE')
    assert partial or status != 'PARTIAL_EXECUTION'
    if status in ('COMPLETE_EXECUTION', 'COMPLETE_WITH_FAILURES'):
        assert len(rows) == len(experiment.CASES)
        assert (status == 'COMPLETE_EXECUTION') == all(r['worker_status'] == 'EXECUTED' for r in rows)
    if status == 'STOPPED_AUDITOR_FAILURE':
        assert rows and rows[-1]['worker_status'] == 'FAILED'
    controls, _ = experiment.retained_controls()
    baselines, _ = experiment.model.retained_baselines()
    old_details, old_scores, old_decisions, posterior_checks = [], 0, 0, 0
    for row, case, baseline in zip(controls['workers'], experiment.CASES, baselines):
        assert common.check_job(row, controls['registration_source'], baseline['device'])
        detail, scores, decisions = common.check_result(row['result'], case, baseline)
        old_details.append(detail)
        old_scores += scores
        old_decisions += decisions
        posterior_checks += common.check_baseline(baseline, *experiment.model.data(case))
    details, score_checks, path_checks, phases = [], 0, 0, 0
    for index, row in enumerate(rows):
        if not common.check_job(row, source, baselines[index]['device']):
            detail = {'status': 'FAILED', 'reason': common.failure_reason(row), 'no_imputed_score_or_phase_count': True}
        else:
            detail, scores, decisions = common.check_result(row['result'], tuple(row['case']), baselines[index],
                                                            fresh_checker=check_fresh)
            score_checks += scores
            path_checks += decisions
            if row['result']['phase_audit_status'] == 'ALL_EXECUTED_PHASES_CHECKED':
                phases += row['result']['independent_binary64_phases']
            if detail['status'] == 'SEALED_CUDA_STREAM':
                previous = controls['workers'][index]['result']
                candidate_words = lambda values: [r for r in values if r['candidate'] == 'posterior']
                detail['retained_B6_comparison'] = {
                    'previous_install_cursor': previous['install_cursor'],
                    'candidate_readout_words_identical': candidate_words(row['result']['CUDA_readouts']) == candidate_words(previous['CUDA_readouts']),
                    'previous_expected_CE_binary64': old_details[index]['expected_CE_binary64']}
        details.append({'case': row['case'], **detail})
    sealed = [r for r in details if r['status'] == 'SEALED_CUDA_STREAM']
    groups = []
    for law in ('iid-c2', 'iid-c4'):
        selected = [r for r in sealed if r['case'][1] == law]
        groups.append({'law': law, 'scored_workers': len(selected),
            'installed_workers': sum(r['install_cursor'] is not None for r in selected),
            'expected_CE_binary64': {key: mean(r['expected_CE_binary64'][key] for r in selected if key in r['expected_CE_binary64'])
                if any(key in r['expected_CE_binary64'] for r in selected) else None
                for key in ('candidate_stream_unseen', 'deployed_stream_unseen', 'adaptive_exact_unseen')}})
    assert 'torch' not in sys.modules
    return {'journal_status': status, 'execution_source': source,
        'analysis_source': experiment.model.git('rev-parse', 'HEAD') if source_check else None,
        'scope': 'retained retrospective outcomes; no new GPU execution or Runtime authority',
        'attempted_workers': len(rows), 'sealed_workers': len(sealed),
        'failed_workers': sum(r['status'] == 'FAILED' for r in details),
        'halted_unresolved_workers': sum(r['status'] == 'HALTED_UNRESOLVED' for r in details),
        'independent_model_score_checks': score_checks, 'independent_fresh_path_checks': path_checks,
        'worker_verified_CUDA_and_binary64_phases_each': phases,
        'retained_B6_score_checks': old_scores, 'retained_B6_decisions': old_decisions,
        'retained_posterior_score_checks': posterior_checks, 'new_control_workers': 0,
        'maximum_completed_job_bytes': max((r['completed_job']['peak_job_commit'] for r in rows), default=None),
        'groups': groups, 'workers': details}


def self_test():
    scenarios = experiment.fresh_scenarios()

    def check(example):
        return check_fresh(example['result'], example['exact'], None, example['evaluation'], 0,
                           domain_rows=example['domain_rows'])

    for example in scenarios:
        check(example)
    mutations = (
        lambda p: p.update(bound='6'),
        lambda p: p.update(ratio_bound_kind='native-class-cap'),
        lambda p: p.update(wealth='0'),
        lambda p: p['score_records'].pop(0),
        lambda p: p.update(refinement_charged_work=p['refinement_charged_work']+1),
        lambda p: p.update(numerical_crossing_cursor=None),
        lambda p: p.update(crossing_cursor=1),
        lambda p: p.update(start_cursor=1),
    )
    for mutate in mutations:
        forged = deepcopy(scenarios[0])
        mutate(forged['result']['fresh']['paths'][0])
        try:
            check(forged)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError('forged fresh record accepted')
    forged = deepcopy(scenarios[1])
    forged['result']['install_cursor'] = forged['result']['fresh']['numerical_crossings'][0]
    forged['result']['fresh']['install_transport_checked'] = True
    try:
        check(forged)
    except AssertionError:
        pass
    else:
        raise AssertionError('unretained numerical crossing promoted to installation')
    return {'status': 'PASS', 'actual_reference_scenarios': 2,
            'forged_rule_scope_wealth_cursor_work_and_install_refusals': 9,
            'numeric_crossing_without_owned_crossing_preserved': True,
            'scope': 'reader development cases; no synthetic successful model worker'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--journal', type=Path, default=experiment.OUTPUT)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else verify(args.journal, partial=args.partial), indent=2))
