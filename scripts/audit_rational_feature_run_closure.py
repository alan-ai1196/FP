"""CPU regression for complete native cache dispatch in finite run reports.

Actual A1 failed at this reader. These passive checks grant no device or
run-sealing authority and do not replace a fresh actual closure job.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import rational_feature_amp as amp, joint_amp as legacy, joint_partition_decoder as decoder
from fp_reference.joint_relation import JointRelation, initialize
from fp_reference.joint_execution import _execute_owned_prediction
from fp_reference.run_state import prediction_diagnostics
from fp_reference.cuda_run import cuda_diagnostics
from audit_joint_amp import BUDGET
from audit_rational_feature_amp import WIDE
from unknown_noise_decoding import DEFAULT, OTHER

OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_RUN_DIAGNOSTICS.json'


def encoded(n, family, C, query):
    model = JointRelation(n, *family, feature_scale=None if C is None else F(C))
    budget = replace(BUDGET, step_cap=8)
    plan = decoder.passive_plan(initialize(model), query, budget)
    physical = legacy if C is None else amp
    raw, _ = physical._prediction_schedule(plan, physical.JointAmpState(plan.before), physical._Arithmetic(32768))
    return raw, _execute_owned_prediction(plan, model)


def report(raw):
    # This is a passive dispatch fixture, not an initialized private owner.
    records = {
        'checked': SimpleNamespace(status='CHECKED_CUDA_PREFIX_PHASE', raw_prediction=raw),
        'no_prediction': SimpleNamespace(status='CHECKED_CUDA_PREFIX_PHASE', raw_prediction=None),
        'failed': SimpleNamespace(status='EXECUTION_FAILED', raw_prediction=object())}
    return cuda_diagnostics(SimpleNamespace(indexed=True, phases=records), 32768)


def main():
    count = 0
    for n, family, C in ((2, DEFAULT, 10), (3, OTHER, 8), (2, WIDE, 4), (3, DEFAULT, None)):
        for query in ((0, 0), (0, 1), (1, 0)):
            raw, _ = encoded(n, family, C, query)
            materialized = raw.decoded().materialize(scalar_cap=10000)
            expected = prediction_diagnostics((materialized,), 'indexed-cuda-half-single', 32768)
            assert report(raw) == expected
            count += 1
    wide, exact = encoded(2, WIDE, 4, (0, 1))
    physical, reference = report(wide), prediction_diagnostics((exact,), 'exact-reference', 32768)
    assert physical.minimum_nonzero_activation == 1
    assert reference.minimum_nonzero_activation == F(1, (1 << 200)+1)
    small, _ = encoded(3, OTHER, 8, (0, 1))
    large, _ = encoded(64, OTHER, 8, (0, 1))
    with (patch.object(amp.DecodedPrediction, 'materialize', side_effect=AssertionError('world expansion')),
          patch.object(JointRelation, 'materialize_program', side_effect=AssertionError('graph expansion'))):
        assert report(large) == report(small)
    assert 'torch' not in sys.modules
    return dict(status='PASS_RATIONAL_FEATURE_RUN_DIAGNOSTICS',
        complete_basis_vs_materialized_reports=count, n64_world_expansion_prohibited=True,
        actual_rounded_coefficient_zero_distinguished_from_exact_nonzero=True,
        physical_minimum_positive_activation='1', reference_minimum_positive_activation='1/(2^200+1)',
        unscored_failed_and_empty_prediction_records_skipped=True, legacy_unit_mode_compared=True,
        scope='passive run-report dispatch only; A1 failure unchanged; actual repaired CUDA closure remains unverified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
