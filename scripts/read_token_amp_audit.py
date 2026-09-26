"""Read the terminal token AMP journal and conservatively bound diagnostics.

No GPU, numerical trajectory replay, model scoring or bridge issuance.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]


def upward(value):
    if type(value) is not float or value < 0 or not math.isfinite(value):
        raise ValueError('finite nonnegative rounded diagnostic required')
    result = math.nextafter(value, math.inf) if value else 0.0
    if not math.isfinite(result):
        raise ValueError('diagnostic bound exhausted')
    return result


def main():
    source = ROOT/'evidence/minimal/FP_TOKEN_AMP_CUDA_A1.json'
    raw = json.loads(source.read_text(encoding='utf-8'))
    assert raw['source_commit'] == '17c92045cc9cee30b0ae6079f1714c09b2bf8b9f'
    assert raw['status'] == 'COMPLETE_PHYSICAL_SCHEDULE_AUDIT'
    assert tuple(row['case'] for row in raw['results']) == ('small-exact', 'train-context512')
    for row in raw['results']:
        job, result = row['job'], row['result']
        assert row['accepted_execution'] and job['exit_code'] == 0 and not job['timed_out']
        assert job['attached_before_resume'] and job['commit_limit'] == raw['host_cap'] == 4 << 30
        assert job['peak_job_commit'] <= raw['host_cap'] and job['limit_terminated_processes'] == 0
        for key in ('before', 'after'):
            observed = result[key]
            assert (observed['process_id'], observed['creation_100ns']) == (job['process_id'], job['process_creation_100ns'])
            assert observed['lifetime_process_commit_peak'] <= job['peak_process_commit']
            assert observed['job_commit_peak'] <= job['peak_job_commit']
        assert result['max_reserved'] <= result['allocator_cap'] == 512 << 20
    small, full = (row['result'] for row in raw['results'])
    assert (small['exact_primitive_calls'], small['exact_primitive_words'], small['half_words']) == (2006, 10020, 976)
    witness = small['underflow_counterexample']
    assert F(witness['first_probability_error']) == 0
    assert F(witness['next_native_probability'])-F(witness['next_physical_probability']) == F(1, 524286)
    assert full['complete_CPU_device_endpoint_and_basis_word_equality']
    assert full['maximum_master_grid_distance'] == dict(E=0, C=1, W=1)
    # The original diagnostic used nearest binary64 subtraction. Its final
    # maximum can be one ulp below the true endpoint distance. Preserve the
    # journal, and promote each nonzero reported maximum by one successor.
    tiny = F(1, 2**100)
    rounded = abs(float(tiny)-(-1.0))
    assert F(rounded) < 1+tiny <= F(upward(rounded))
    assert upward(0.0) == 0.0
    maximum_finite = struct.unpack('>d', bytes.fromhex('7fefffffffffffff'))[0]
    try:
        upward(maximum_finite)
    except ValueError:
        pass
    else:
        raise AssertionError('nonfinite outward diagnostic accepted')
    result = dict(status='PASS_TERMINAL_JOURNAL_READER', original_source=raw['source_commit'],
        original_journal_unchanged=True, trajectories_reexecuted=False,
        diagnostic_correction='one upward binary64 successor per nonzero original rounded maximum',
        exact_diagnostic_counterexample_checked=True,
        small_complete_basis_maxima={key: upward(max(row['full_basis_absolute_error_upper'][key] for row in small['native_comparisons']))
            for key in small['native_comparisons'][0]['full_basis_absolute_error_upper']},
        real_unit_complete_basis_upper={key: upward(value) for key, value in full['full_basis_absolute_error_upper'].items()},
        real_unit_master_grid_distance=full['maximum_master_grid_distance'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
