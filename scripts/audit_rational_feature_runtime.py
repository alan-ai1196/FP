"""Owned rational-feature Reference Runtime, independent native controls and refusals."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
import audit_joint_runtime as old
from audit_reference_construction import rejects, validate_residency
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference import joint_relation as joint, joint_partition_decoder as decoder, joint_amp as amp
from fp_reference.joint_execution import JointState, JointTheta, RATIONAL_MODEL_ID, RATIONAL_ARITHMETIC_ID
from fp_reference.cuda_prefix import JointCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.core import ContractError, stable_hash
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.learner import observe_event
from shared_noise_factor_closure import counter_states
from unknown_noise_decoding import Joint, DEFAULT, OTHER
from unknown_noise_model import JointControl
from rational_feature_scale import Bank, gradient_basis, reference, native_graph
from audit_rational_feature_scale import integer_parts

OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_REFERENCE_RUNTIME.json'
NONINTEGER = ((F(2, 5), F(3, 7)), (F(1, 3), F(2, 3)))


def indexing_and_parts():
    descriptions = []
    for n, family, C in tuple((n, family, C) for n in (2, 3, 4) for family, C in ((DEFAULT, F(10)), (OTHER, F(8))))+((2, NONINTEGER, F(5, 2)),):
        schema = joint.JointRelation(n, *family, feature_scale=C)
        rules, graph, spec, theta, _ = native_graph(Bank(n, *family, C))
        schema.compare_literal(graph, rules, theta, spec, node_cap=1000, term_cap=10000, slot_cap=100)
        assert schema.counts() == graph.counts()
        descriptions.append(dict(n=n, native_scale=str(C), likelihood_scale=schema.scale, graph=graph.counts()))
    cuts = queries = reads = 0
    for n, family, C in ((2, DEFAULT, F(10)), (3, DEFAULT, F(10)), (2, OTHER, F(8)),
                         (3, OTHER, F(8)), (2, NONINTEGER, F(5, 2))):
        schema = joint.JointRelation(n, *family, feature_scale=C)
        model, control = Bank(n, *family, C), Joint(n, *family)
        budget = replace(old.BUDGET, step_cap=3)
        size = decoder.workspace_bytes(schema, budget)
        backing = bytearray([165])*(size+26)
        with memoryview(backing)[13:-13] as scratch:
            for T, states in counter_states(n*(n-1)//2+1, 3):
                for values in sorted(states):
                    before = joint.JointCountState(schema, values[:-1], values[-1], T, T)
                    weights = control.counts(T, values[:-1], values[-1])
                    for query in product(range(n), repeat=2):
                        plan = decoder.prepare_bound(schema, before, schema.rules(), schema.source_row(query[0]*n+query[1]), budget, scratch)
                        expected = integer_parts(control, weights, query)
                        assert plan.rate_parts == expected and plan.normalization == sum(weights)
                        assert decoder.reference(plan) == reference(model, expected)
                        roots = plan.excesses+(plan.normalization,)+tuple(v for row in expected for v in row)
                        for at, value in enumerate(roots):
                            start = (budget.live_cells+2+at)*plan.cell_bytes
                            assert int.from_bytes(scratch[start:start+plan.cell_bytes], 'little') == value
                            reads += 1
                        assert plan.maximum_integer_bits <= plan.integer_envelope
                        queries += 1
                    cuts += 1
        assert backing[:13] == backing[-13:] == bytearray([165])*13
    return dict(literal_descriptions=descriptions, reachable_cuts=cuts, complete_ordered_queries=queries,
                paid_packed_root_reads=reads, external_canaries_preserved=True)


def owned_small():
    rows = []
    for n, family, C in ((2, DEFAULT, F(10)), (3, DEFAULT, F(10)),
                         (2, OTHER, F(8)), (2, NONINTEGER, F(5, 2))):
        cfg, schema, online = old.fixture(n, 2, family=family, feature_scale=C)
        histories = triples = 0
        for word in product(tuple(product(range(n), range(n), (0, 1))), repeat=2):
            runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
            initial = validate_residency(runtime)
            models = {initial.deployed_id: old.literal(schema)}
            old.check_state(initial.candidates[0].learner, models[initial.deployed_id][3])
            for event in word:
                triples += old.step(runtime, schema, event, models)
            histories += 1
        rows.append(dict(n=n, rates=list(map(str, schema.rates)), native_scale=str(C),
                         all_two_event_histories=histories, complete_owned_native_triples=triples))
    return rows


def input_and_plan_attacks():
    cfg, schema, online = old.fixture(3, 3, feature_scale=F(10))
    before = joint.JointCountState(schema, (0, 0, 0), 2, 2, 2)
    rules, sources = schema.rules(), schema.source_row(1)
    with memoryview(bytearray(decoder.workspace_bytes(schema, old.BUDGET))) as scratch:
        plan = decoder.prepare_bound(schema, before, rules, sources, old.BUDGET, scratch)
        assert plan.rate_parts == ((648, 648), (450, 450))
        changed_parts = ((653, 643), (442, 458))
        model = Bank(3, schema.rates, schema.prior, F(10))
        assert reference(model, changed_parts) == decoder.reference(plan)
        assert gradient_basis(model, changed_parts, 0)[0] == F(-1, 2196)
        assert gradient_basis(model, plan.rate_parts, 0)[0] == 0
        attacks = (
            replace(plan, rate_parts=changed_parts),
            replace(plan, rate_parts=plan.rate_parts[:-1]),
            replace(plan, rate_parts=tuple((True, row[1]) for row in plan.rate_parts)),
            replace(plan, normalization=plan.normalization*2, excesses=tuple(2*v for v in plan.excesses),
                    rate_parts=tuple(tuple(2*v for v in row) for row in plan.rate_parts)),
            replace(plan, before=replace(before, model=replace(schema, feature_scale=F(20)))),
            replace(plan, workspace_bytes=plan.workspace_bytes-1),
            replace(plan, bit_limit=plan.bit_limit-1))
        for changed in attacks:
            rejects(lambda: decoder.check_bound_plan(changed, schema, before, rules, sources, old.BUDGET, scratch))
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    for alternate in (replace(schema, feature_scale=None), replace(schema, feature_scale=F(20)),
                      replace(schema, rates=schema.rates[::-1])):
        assert alternate.program_id != schema.program_id
        assert runtime.construct_candidate(alternate).status == 'REJECTED_ADMISSIBILITY'
    legacy = replace(schema, feature_scale=None)
    assert legacy.program_id == stable_hash(('indexed-native-description-v1',
        (joint.SCHEMA, schema.n, schema.rates, schema.prior)))
    for bad_scale in (10, True, F(9)):
        rejects(lambda: replace(schema, feature_scale=bad_scale))
    assert old.predict(runtime, schema, (0, 0)).status == 'PREDICTED_REFERENCE'
    assert runtime.observe(0).status == 'OBSERVED_REFERENCE'
    observed = runtime.snapshot().event_traces[0].after_observe
    assert schema.gamma(1) == 0 and observed.gradient(1) == F(1, 20)
    rejects(lambda: JointState(observed.encoded, observed.gradient_forms[:1]+observed.gradient_forms[2:]))

    initial = joint.initialize(schema)
    legacy_contract = JointCudaPrefixContract(CudaStorageContract(512, 2 << 20,
        {r: (512, 2 << 20) for r in ('deployment', 'compiler')}), F(1, 100), F(1, 1000),
        schema=legacy, partitions=old.BUDGET)
    # A new registered schedule cannot reassign the original physical IDs.
    object.__setattr__(legacy_contract, 'schema', schema)
    rejected = [lambda: amp.JointAmpState(initial),
        lambda: amp.JointAmpPrediction(initial, (0, 1), (1065353216,)*7),
        lambda: amp.ResidentState(initial),
        lambda: amp.ResidentPrediction(initial, (0, 1), object()),
        lambda: amp.JointAmpRange(JointTheta(schema, initial.counts, 0, 0), cfg.source_domain),
        legacy_contract.__post_init__]
    for action in rejected:
        rejects(action)
    assert 'torch' not in sys.modules
    return dict(altered_complete_plans_refused=len(attacks), equal_readout_different_fixed_gradient='-1/2196',
        wrong_feature_mode_scale_or_rate_order_refused=3, malformed_or_inadmissible_scale_refused=3,
        actual_zero_fixed_coefficient_gradient='1/20', omitted_gradient_coordinate_refused=True,
        legacy_descriptor_identity_preserved=True, legacy_AMP_entrypoints_refused=len(rejected), torch_imported=False)


def large_and_large_denominator():
    n, C = 64, F(8)
    budget = replace(old.BUDGET, join_cells=64, live_cells=1024, arithmetic=32768, step_cap=32)
    cfg, schema, online = old.fixture(n, 8, family=OTHER, feature_scale=C, budget=budget)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    control = JointControl(n, *OTHER)
    word = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 1), (3, 4, 1), (2, 4, 0), (4, 2, 1))
    with patch.object(joint.JointRelation, 'materialize_program', side_effect=AssertionError('world expansion')), \
            patch.object(joint.JointRelation, 'materialize_learner', side_effect=AssertionError('slot expansion')):
        for u, v, y in word:
            answer = control.predict(u, v)
            result = old.predict(runtime, schema, (u, v))
            assert result.status == 'PREDICTED_REFERENCE' and result.predictions[0][1] == answer.joint
            assert runtime.observe(y).status == 'OBSERVED_REFERENCE'
            trace = runtime.snapshot().event_traces[-1]
            assert trace.prediction.rate_parts == answer.rate_parts
            assert trace.after_observe.gradient_forms == gradient_basis(Bank(n, *OTHER, C), answer.rate_parts, y)
            control.observe(y)
            counts, diagonal, T = control.coordinates()
            state = runtime.snapshot().candidates[0].learner.encoded
            assert (state.counts, state.diagonal, state.steps, state.cursor) == (counts, diagonal, T, T)
    final = validate_residency(runtime)
    assert final.run.status == 'SEALED_REFERENCE_STREAM' and not final.run.closure.decisions
    assert final.run.manifest.machine_id == RATIONAL_MODEL_ID
    assert final.run.manifest.reference_arithmetic == RATIONAL_ARITHMETIC_ID
    rejects(lambda: final.candidates[0].learner.materialize(scalar_cap=100000, budget=budget), ArithmeticUnresolved)

    q = (1 << 200)+1
    family = ((F(1, 4), F(q+1, 4*q)), (F(1, 2),)*2)
    cfg, wide, online = old.fixture(2, 8, family=family, feature_scale=F(4), budget=replace(old.BUDGET, step_cap=8))
    root = ReferenceCompilerRuntime(cfg, wide, online=online)
    models = {root.snapshot().deployed_id: old.literal(wide)}
    for event in ((0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1))*2:
        old.step(root, wide, event, models, replace(old.BUDGET, step_cap=8))
    assert wide.scale.bit_length() == 203 and wide.native_scale == 4
    return dict(n=n, native_hypotheses=str(schema.K), ordinary_events=8, complete_gradient_coordinates=12,
        independent_unsigned_control_matches=True, status=final.run.status, constructor_decisions=0,
        integer_workspace_bytes=decoder.workspace_bytes(schema, budget), packed_peak_bytes=final.resources['peak']['reference_payload_bytes'],
        large_denominator_bits=203, large_denominator_native_scale=4, large_denominator_owned_native_triples=8)


def gradient_precision_obstruction():
    # The new fixed gradient has an irreducible product denominator even
    # while heads and exact posterior coordinates fit the same bit allowance.
    q = (1 << 200)+1
    family = ((F(1, 4), F(q+1, 4*q)), (F(1, 2),)*2)
    budget = replace(old.BUDGET, step_cap=100)
    cfg, schema, online = old.fixture(2, 90, family=family, feature_scale=F(4), budget=budget,
                                    byte_cap=512 << 20, work_cap=10**15)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    for k in range(90):
        before = runtime.snapshot()
        assert old.predict(runtime, schema, (0, 0)).status == 'PREDICTED_REFERENCE'
        pending = runtime.snapshot().pending.predictions[0][1]
        result = runtime.observe(0)
        if result.status == 'OBSERVED_REFERENCE':
            continue
        assert result.status == 'UNRESOLVED' and 'integer work limit' in result.reason, result
        after = validate_residency(runtime)
        a = 3*q
        denominator = 4*(a**k+(a-1)**k)*(a**(k+1)+(a-1)**(k+1))
        U, V = (a**k, (a-1)**k)
        mass = F(a*U+(a-1)*V, q*(U+V))
        gradient = F(U, 4*(U+V))-F(U, U+V)/mass
        assert gradient.denominator == denominator and denominator.bit_length() > cfg.reference_integer_bits
        assert k == 81 and after.cursor == k and after.candidates == before.candidates
        assert after.pending.record.target == 0 and after.observations[-1].target == 0
        assert len(after.event_traces) == len(before.event_traces)
        rules, graph, spec, initial = old.literal(schema)
        weights = tuple(F(w, 2*(U+V)) for w in (U, U, V, V))
        native_state = replace(initial, theta=initial.theta[:4]+weights, cursor=k, optimizer_steps=k)
        native_cache = evaluate(graph, rules, native_state.theta, schema.source_row(0), (), bit_limit=131072)
        old.check_prediction(pending, native_cache)
        rejects(lambda: observe_event(graph, native_state, spec, native_cache, 0, bit_limit=32768), ArithmeticUnresolved)
        high = observe_event(graph, native_state, spec, native_cache, 0, bit_limit=131072)
        assert high.gradient_sum[0] == gradient
        prediction_bits = max(max(v.numerator.bit_length(), v.denominator.bit_length())
            for v in pending.activation_basis()+pending.masses+pending.probabilities+(pending.normalizer,))
        assert prediction_bits < cfg.reference_integer_bits
        return dict(committed_events=k, failed_observation_index=k, final_prediction_passed=True,
            status=result.status, exact_fixed_gradient_denominator_bits=denominator.bit_length(),
            maximum_native_prediction_integer_bits=prediction_bits,
            reference_integer_limit=cfg.reference_integer_bits, full_native_same_limit_refuses=True,
            independent_native_131072_bit_gradient_matches=True, actual_target_retained=True,
            no_successor_published=True, native_normalizer='4', likelihood_scale_bits=schema.scale.bit_length(),
            scope='exact materialized native-gradient bit limit; no impossibility claim for every symbolic representation')
    raise AssertionError('expected full-gradient precision obstruction did not occur')


def main():
    result = {'status': 'PASS_OWNED_RATIONAL_FEATURE_REFERENCE_RUNTIME',
        'scope': 'complete native G/Gamma/reference phases, paid parts and actual same-path freshness; no AMP/install or CERTIFIED_COMPLETE'}
    jobs = dict(indexing_parts=indexing_and_parts, small=owned_small, attacks=input_and_plan_attacks,
        large=large_and_large_denominator, precision_obstruction=gradient_precision_obstruction,
        profile=lambda: old.profile(feature_scale=F(8), family=OTHER),
        funding=lambda: old.funding(feature_scale=F(10)),
        workspace=lambda: old.workspace_lifetime(feature_scale=F(10)),
        bindings_atomic=lambda: old.bindings_and_atomic_failure(feature_scale=F(10)),
        fresh=lambda: old.fresh_reference(feature_scale=F(10)))
    for name, function in jobs.items():
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
