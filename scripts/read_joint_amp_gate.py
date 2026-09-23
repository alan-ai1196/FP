"""Read the terminal joint AMP journal without importing Torch or rerunning jobs.

This checks retained reports against their committed declaration. Complete
phase/native/RNE reads ran inside the source-bound workers; the small journal
does not contain those full frames and is not an independent execution proof.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '2432a25064ec8f757f8760f24d1e4f27558dccc8'
STATUS = 'PASS_ACTUAL_OWNED_JOINT_AMP'
CAP = 4 << 30
CASES = ('profiles', 'fresh-install', 'large-closure', 'old-A1-cut', 'reversal', 'scale-refusal',
    'unfunded', 'second-commit', 'prediction-word', 'gradient-word', 'operation-word',
    'old-output', 'target-swap', 'plan-roots', 'workspace', 'profile-refusal', 'legacy-shared-owner')
DEFAULT = ROOT/'evidence/minimal/FP_JOINT_AMP_CUDA_A1.json'
COUNTS = ('checked_phases', 'independent_partition_RNE_predictions', 'full_literal_native_phases',
    'actual_operation_words', 'actual_half_words', 'output_words_including_copies')
CHECKED_BLOCKS = frozenset(('profiles', 'fresh-install', 'large-closure', 'old-A1-cut',
    'reversal', 'scale-refusal', 'workspace', 'profile-refusal'))
ERRORS = frozenset(('state_error', 'native_error', 'normalizer_error', 'probability_error', 'division_error'))


def same(left, right):
    # JSON types matter: true does not substitute for an integer or vice versa.
    assert json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def read(report):
    assert 'torch' not in sys.modules
    assert report['status'] == STATUS and report['execution_source'] == SOURCE
    registration = report['registration']
    for key, value in {
            'status': 'REGISTERED_BEFORE_JOINT_CUDA_EXECUTION', 'cases': list(CASES),
            'job_cap': CAP, 'deadline_ms': 900000, 'fresh_owner_per_job': True,
            'budget': dict(join_cells=64, live_cells=1024, arithmetic=32768, step_cap=2048, integer_bits=32768),
            'profile_integer_bits': 4096, 'arena_bytes': 32 << 20, 'allocator_cap': 64 << 20,
            'output_cells': 64, 'frame_bytes_n2_n3': 65536, 'frame_bytes_n64': 524288,
            'state_atol': '1/100', 'probability_atol': '1/1000',
            'native_normalizer_cap': '2*(S-1)', 'native_activation_cap': 'S-2',
            'forward_id': 'joint-noise-integer-excess-half-mantissas-single-readout-v1',
            'evidence_encoding': 'typed-reference-json-v4-zlib-1.3.1-1.3.1-l6-w15-m8-s0-v1'}.items():
        same(registration[key], value)
    assert [w['case'] for w in report['workers']] == list(CASES)
    results, processes, totals, maxima = {}, set(), dict.fromkeys(COUNTS, 0), {}
    peak = 0
    for row in report['workers']:
        job, output, case = row['completed_job'], row['result'], row['case']
        assert row['worker_status'] == 'PASS' and output['status'] == STATUS and output['case'] == case
        for key, value in dict(exit_code=0, timed_out=False, commit_limit=CAP,
                limit_terminated_processes=0, attached_before_resume=True).items():
            same(job[key], value)
        for key in ('process_id', 'process_creation_100ns', 'peak_process_commit', 'peak_job_commit', 'total_processes'):
            assert type(job[key]) is int and job[key] > 0
        same(output['process_id'], job['process_id'])
        assert job['peak_process_commit'] <= job['peak_job_commit'] <= CAP
        identity = (job['process_id'], job['process_creation_100ns'])
        assert identity not in processes
        processes.add(identity)
        peak = max(peak, job['peak_job_commit'])
        value = results[case] = output['result']
        assert ('checked_phases' in value) == (case in CHECKED_BLOCKS)
        if case not in CHECKED_BLOCKS:
            continue
        for key in COUNTS:
            assert type(value[key]) is int and value[key] >= 0
            totals[key] += value[key]
        assert value['checked_phases'] > 0 and value['independent_partition_RNE_predictions'] > 0
        assert value['full_literal_native_phases'] == (0 if case == 'large-closure' else value['checked_phases'])
        assert 0 < value['table_bytes'] <= value['packed_peak_bytes'] <= 1 << 30
        assert 0 < value['consumed_arena_bytes'] <= 32 << 20
        frame_cap = 524288 if case == 'large-closure' else 65536
        assert 0 < value['largest_encoded_frame_bytes'] <= frame_cap-8
        assert set(value['maximum_relation_errors']) == ERRORS
        for key, error in value['maximum_relation_errors'].items():
            limit = F(1, 1000) if key in ('probability_error', 'division_error') else F(1, 100)
            assert 0 <= F(error) <= limit
            maxima[key] = max(maxima.get(key, F(0)), F(error))
    p = results['profiles']
    same((p['cursor'], p['profile_events'], p['optimizer_steps']), (8, 4, [8, 10]))
    p = results['fresh-install']
    same((p['fresh_start_cursor'], p['paired_install_cursor'], p['post_install_continuation_to'],
          p['alpha_spent'], p['constructor_certificate']), (16, 20, 36, '1/2', None))
    p = results['large-closure']
    same((p['worlds'], p['closure'], p['constructor_decisions']), (str(1 << 64), 'SEALED_CUDA_STREAM', 0))
    p = results['old-A1-cut']
    same(p['historical_cut_reached_by_new_source'], [[27, 27, [27]], [27, 29, [29]]])
    assert p['cursor'] == 48
    p = results['reversal']
    same((p['temporary_zero_excess'], p['restored_zero_count_steps'], p['restored_actual_half_forecast'],
          p['final_target_unrevealed']), (True, 104, True, True))
    p = results['scale-refusal']
    same((p['expected_refusal'], p['actual_native_error'], p['third_target_received']),
         ('UNRESOLVED', '65863667/4117889024', False))
    p = results['unfunded']
    same((p['status'], p['executor_entries'], p['retained_context_and_failed_phase']), ('UNRESOLVED', 0, True))
    p = results['second-commit']
    same((p['status'], p['observed_lineages_retained'], p['published_advances'], p['retained_target']),
         ('UNRESOLVED', 2, 0, 0))
    for case in ('prediction-word', 'gradient-word', 'operation-word', 'old-output', 'target-swap', 'plan-roots'):
        p = results[case]
        same((p['case'], p['status'], p['published_advances'], p['old_frames_and_native_physical_predecessors_preserved'],
              p['actual_target']), (case, 'EXECUTION_FAILED', 0, True, 0 if case in ('gradient-word', 'target-swap') else None))
        assert p['reason'].startswith('ContractError:')
    p = results['workspace']
    same((p['prepaid_reference_physical_reconstruction_visits'], p['postwrite_failure'],
          p['failed_table_remains_owned_and_pinned']), (6, 'UNRESOLVED', True))
    p = results['profile-refusal']
    same((p['failed_profile_steps_retained'], p['published_newborns']), (2, 0))
    p = results['legacy-shared-owner']['new_shared_owner_regression']
    same((p['checked_phases'], p['independent_partition_and_RNE_prediction_readers'], p['cursor']), (13, 4, 4))
    return {'status': 'PASS_RETAINED_JOINT_AMP_GATE', 'execution_source': SOURCE, 'completed_jobs': len(processes),
        'joint_checked_blocks': totals, 'maximum_checked_relation_errors': {k: str(v) for k, v in maxima.items()},
        'observed_peak_host_commit_bytes': peak, 'legacy_checked_phases': p['checked_phases'],
        'scope': 'source-bound terminal reports; totals exclude preparatory phases of fault-only reports and all refused phases; no GPU rerun, model result or constructor certificate'}


def negatives(report):
    # Report-validation attacks are separate from the actual owner faults.
    changes = [
        lambda r: r.update(execution_source='0'*40),
        lambda r: r.update(status='REGISTERED_NOT_COMPLETED'),
        lambda r: r['registration'].update(state_atol='1/50'),
        lambda r: r['workers'].pop(),
        lambda r: r['workers'].__setitem__(1, deepcopy(r['workers'][0])),
        lambda r: r['workers'][0]['completed_job'].update(timed_out=True),
        lambda r: r['workers'][0]['completed_job'].update(commit_limit=2*CAP),
        lambda r: r['workers'][0]['completed_job'].update(attached_before_resume=False),
        lambda r: r['workers'][0]['result'].update(process_id=0),
        lambda r: r['workers'][0]['completed_job'].update(exit_code=False),
        lambda r: r['workers'][0]['result']['result']['maximum_relation_errors'].update(normalizer_error='1/50'),
        lambda r: r['workers'][1]['result']['result'].update(post_install_continuation_to=20),
        lambda r: r['workers'][4]['result']['result'].update(restored_zero_count_steps=0),
        lambda r: r['workers'][5]['result']['result'].update(expected_refusal=STATUS),
        lambda r: r['workers'][8]['result']['result'].update(published_advances=1),
        lambda r: r['workers'][14]['result']['result'].update(failed_table_remains_owned_and_pinned=False),
        lambda r: r['workers'][0]['result']['result'].pop('checked_phases'),
        lambda r: r['workers'][0]['result']['result']['maximum_relation_errors'].pop('native_error'),
    ]
    for change in changes:
        altered = deepcopy(report)
        change(altered)
        try:
            read(altered)
        except (AssertionError, KeyError, ValueError):
            continue
        raise AssertionError('altered report received a retained-gate PASS')
    return len(changes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path, default=DEFAULT)
    parser.add_argument('--negative-checks', action='store_true')
    args = parser.parse_args()
    report = json.loads(args.path.read_text(encoding='utf-8'))
    result = read(report)
    if args.negative_checks:
        result['retained_report_refusals'] = negatives(report)
    print(json.dumps(result, indent=2))
