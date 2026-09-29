"""Check the trial's suffix reduction on a complete owned native trajectory."""
from fractions import Fraction as F
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.ingress import encode_context
from audit_token_reporting import report_registration
from audit_shared_token_retention import STORAGE
from run_native_text_a1 import suffix_interval, complete_residency, model_state


def main():
    training, values, boundary = (1, 0, 0, 1), (0, 1, 1, 0, 1, 0, 0, 1), 3
    cc, program, online, reporting = report_registration(count=len(training), report_count=len(values), terms=16)
    runtime = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=STORAGE, reporting=reporting)
    for index, target in enumerate(training):
        assert runtime.predict_next(f'train/{index}', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
    frozen = model_state(runtime)
    assert runtime.begin_report().status == 'REPORTING'
    totals = []
    for index, target in enumerate(values):
        assert runtime.predict_report(f'report/{index}').status == 'PREDICTED_REPORT'
        expected_past = tuple(program.definition.sources.padding if lag > index else values[index-lag]
                              for lag in range(1, program.definition.sources.context+1))
        assert runtime._token_report.pending.record.sources.past == expected_past
        assert runtime.observe_report(target).status == ('COMPLETE_REPORT' if index+1 == len(values) else 'SCORED_REPORT')
        assert model_state(runtime) is frozen
        totals.append(runtime._token_report.native_total)
    complete = runtime.report_result()
    assert complete.status == 'COMPLETE_REPORT' and complete.physical_mean is None
    scale = 1 << reporting.accumulator_bits
    assert complete.native_mean.lower == F(totals[-1][0], len(values)*scale)
    assert complete.native_mean.upper == F(totals[-1][1], len(values)*scale)
    checks = 0
    for split in (1, boundary, 7):
        lower, upper = suffix_interval(totals[-1], totals[split-1], len(values)-split, reporting.accumulator_bits)
        events = runtime._token_report.events[split:]
        exact_lower = sum((event.native_loss.lower for event in events), F(0))/len(events)
        exact_upper = sum((event.native_loss.upper for event in events), F(0))/len(events)
        assert lower <= exact_lower <= exact_upper <= upper
        assert exact_lower-lower < F(1, scale) and upper-exact_upper < F(1, scale)
        checks += 1
    resources = complete_residency(runtime)
    snapshot = runtime.snapshot()
    assert resources['current'] == snapshot.resources['current']
    assert resources['role_current'] == snapshot.resources['role_current']
    assert resources['peak'] == snapshot.resources['peak']
    assert 'torch' not in sys.modules
    result = dict(status='PASS_OWNED_NATIVE_TEXT_REPORT_CONTROL', training_targets=len(training),
        reporting_targets=len(values), suffix_boundaries_checked=checks,
        exact_directed_suffix_sum_enclosed=True, endpoint_rounding_error_below='2^-40',
        original_report_contexts_and_frozen_identity_preserved=True,
        every_current_buffer_and_lease_checked=True, full_snapshot_resource_totals_match=True,
        actual_corpus_opened=False, cuda_execution=False)
    (ROOT/'evidence/minimal/FP_NATIVE_TEXT_REPORT_CONTROL.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
