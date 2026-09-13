"""Recompute the three retained model controls without executing another GPU job."""
from fractions import Fraction as F
from itertools import product
import json
import subprocess

import constraint_cuda as first
import centered_cuda as second
from audit_cuda_primitives import SINGLE


def analyze():
    reports = (json.loads(first.OUTPUT.read_text(encoding='utf-8')),
               json.loads(second.OUTPUT.read_text(encoding='utf-8')))
    assert reports[1]['prior_comparison']['source'] == reports[0]['registration_source']
    assert reports[1]['prior_comparison']['attempts_retained_without_rerun'] == 2
    common = {k: v for k, v in reports[0]['registration'].items() if k not in ('cases', 'bounds')}
    assert {k: v for k, v in reports[1]['registration'].items() if k not in ('cases', 'bounds')} == common
    output = []
    forecasts = phases = 0
    for report, dependencies in zip(reports, (first.DEPENDENCIES, second.DEPENDENCIES)):
        assert report['status'] == 'COMPLETE_EXECUTION'
        # Actual execution dependencies, not decorative or repeated hashes.
        subprocess.run(['git', 'diff', '--exit-code', report['registration_source'], '--', *dependencies],
                       cwd=first.ROOT, check=True, stdout=subprocess.DEVNULL)
        assert len(report['workers']) == len(report['registration']['cases'])
        for index, row in enumerate(report['workers']):
            assert row['case_index'] == index and row['kind'] == report['registration']['cases'][index]
            assert row['execution_source'] == report['registration_source'] and row['worker_status'] == 'EXECUTED'
            job = row['completed_job']
            result = row['result']
            assert job['exit_code'] == 0 and not job['timed_out'] and job['attached_before_resume']
            assert job['commit_limit'] == common['host_cap'] and job['peak_job_commit'] <= job['commit_limit']
            assert job['process_id'] == result['host']['process_id']
            assert job['process_creation_100ns'] == result['host']['creation_100ns']
            assert result['run_status'] == 'SEALED_CUDA_STREAM' and result['halted'] is None
            assert not result['class_or_install_certificate']
            assert result['retained_observations'] == len(result['forecasts']) == len(common['tape']) == 9
            assert result['independent_binary64_phases'] == result['CUDA_audit']['phases'] == 28
            assert result['packed_peak'] <= common['packed_cap']
            assert result['CUDA_audit']['actual_arena_bytes'] == common['arena_bytes']
            assert result['consumed_arena_extent'] <= common['arena_bytes']
            assert result['CUDA_audit']['largest_phase_frame_used'] <= common['phase_evidence_bytes']
            assert result['CUDA_audit']['maximum_output_cells'] <= common['phase_output_cells']
            maximum_probability = maximum_division = maximum_mass = maximum_total = F(0)
            history = []
            for (i, j, target), prediction in zip(common['tape'], result['forecasts'], strict=True):
                # Independent four-world latent sum; no native emitter or
                # reported reference probability enters this calculation.
                exact = [F(0), F(0)]
                for z in product((0, 1), repeat=2):
                    w = 1
                    for a, b, y in history[-3:]:
                        w *= 9 if (z[a] ^ z[b]) == y else 1
                    for y in (0, 1):
                        exact[y] += F(w * (9 if (z[i] ^ z[j]) == y else 1), 4)
                if row['kind'] == 'enumerated':
                    exact = [2 * value for value in exact]
                assert tuple(map(F, prediction['reference_masses'])) == tuple(exact)
                assert F(prediction['reference_p0']) == exact[0]/sum(exact)
                actual = tuple(map(F, prediction['actual_masses']))
                raw = tuple(SINGLE.decode(SINGLE.rounded(value/sum(actual))) for value in actual)
                maximum_mass = max(maximum_mass, *(abs(a-b) for a, b in zip(actual, exact)))
                maximum_total = max(maximum_total, abs(sum(actual)-sum(exact)))
                maximum_probability = max(maximum_probability, *(abs(a-b/sum(exact)) for a, b in zip(raw, exact)))
                maximum_division = max(maximum_division, *(abs(a-b/sum(actual)) for a, b in zip(raw, actual)))
                if row['kind'] != 'enumerated':
                    assert actual == tuple(exact)
                history.append((i, j, target))
                forecasts += 1
            maxima = result['CUDA_relation_maxima']
            assert maximum_mass <= F(maxima['native_error']) <= F(common['state_native_normalizer_tolerance'])
            assert maximum_total == F(maxima['normalizer_error'])
            assert maximum_probability == F(maxima['probability_error']) <= F(common['probability_tolerance'])
            assert maximum_division == F(maxima['division_error'])
            phases += 28
            output.append({'kind': row['kind'], 'source': row['execution_source'],
                'packed_peak': result['packed_peak'], 'completed_job_peak': job['peak_job_commit'],
                'native_error': maxima['native_error'], 'normalizer_error': maxima['normalizer_error'],
                'raw_probability_error': str(maximum_probability)})
    assert [r['kind'] for r in output] == ['contracted', 'enumerated', 'centered']
    return {'source_bound_sealed_jobs': len(output), 'independent_retained_forecast_checks': forecasts,
            'independently_audited_CUDA_phases': phases, 'independently_audited_binary64_phases': phases,
            'comparisons': output, 'scope': 'same finite model/interface/resource registration; no new GPU job or class/install authority'}


if __name__ == '__main__':
    print(json.dumps(analyze(), indent=2))
