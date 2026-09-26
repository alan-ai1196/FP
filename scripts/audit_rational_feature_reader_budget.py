"""Separate validity of a committed prefix from a later materialization budget."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference import ReferenceCompilerRuntime
from fp_reference.profile import ProfileSpec
from fp_reference.learner import observe_event, commit_event
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_joint_runtime import fixture, literal, predict
from audit_joint_amp import BUDGET
from audit_reference_construction import rejects, validate_residency

OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_READER_BUDGET.json'


def main():
    runtime_budget = replace(BUDGET, step_cap=1)
    profile = ProfileSpec('twice', ('joint-event:0', 'joint-event:1'), 2)
    cfg, model, online = fixture(3, 3, feature_scale=F(10), budget=runtime_budget, profiles=(profile,))
    comparisons = 0
    for targets in product((0, 1), repeat=2):
        runtime = ReferenceCompilerRuntime(cfg, model, online=online)
        rules, graph, spec, expected = literal(model)
        for y in targets:
            assert predict(runtime, model, (0, 1)).status == 'PREDICTED_REFERENCE'
            cache = evaluate(graph, rules, expected.theta, model.source_row(1), (), bit_limit=131072)
            assert runtime.observe(y).status == 'OBSERVED_REFERENCE'
            expected = commit_event(observe_event(graph, expected, spec, cache, y, bit_limit=131072),
                                    spec, bit_limit=131072)
        before = validate_residency(runtime)
        state = before.candidates[0].learner
        assert state.optimizer_steps == before.cursor == 2
        rejects(lambda: state.materialize(scalar_cap=10000, budget=runtime_budget, bit_limit=131072), ArithmeticUnresolved)
        audit_budget = replace(runtime_budget, step_cap=state.optimizer_steps)
        assert state.materialize(scalar_cap=10000, budget=audit_budget, bit_limit=131072) == expected
        comparisons += 1

        result = runtime.construct_candidate(model, profile_id='twice')
        after = validate_residency(runtime)
        assert result.status == 'UNRESOLVED' and after.profiles[0].events_completed == 2
        local = after.profiles[0].local
        assert local.optimizer_steps == 2 and after.profiles[0].attached is None
        assert after.candidates == before.candidates and after.cursor == before.cursor
        rejects(lambda: local.materialize(scalar_cap=10000, budget=runtime_budget, bit_limit=131072), ArithmeticUnresolved)
        assert local.materialize(scalar_cap=10000, budget=audit_budget, bit_limit=131072) == expected
        comparisons += 1

        # The passive reader's allowance grants the live root no extra step.
        assert predict(runtime, model, (0, 1)).status == 'UNRESOLVED'
        final = validate_residency(runtime)
        assert final.cursor == 2 and final.candidates == before.candidates
        assert final.pending is None or final.pending.record.target is None
        assert cfg.indexed_histogram == runtime_budget
    assert 'torch' not in sys.modules
    return dict(status='PASS_RATIONAL_FEATURE_READER_BUDGET', two_target_histories=4,
        full_native_state_and_failed_profile_comparisons=comparisons,
        runtime_prediction_step_cap=1, independently_funded_materialization_step_cap=2,
        old_passive_read_refusals=8, failed_profile_events_retained=2, published_newborns=0,
        subsequent_runtime_prediction_unresolved=True, committed_state_preserved=True,
        literal_audit_bits=131072, scope='owned exact Reference histories and passive full native reads; no actual CUDA result')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
