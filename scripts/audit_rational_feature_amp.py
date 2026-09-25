"""Exact complete-coordinate and adversarial gate for rational-feature AMP."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import rational_feature_amp as amp, joint_amp as legacy, joint_partition_decoder as decoder
from fp_reference.joint_relation import JointRelation, JointCountState, initialize, observe, commit, attach
from fp_reference.joint_execution import JointState, JointLearner, JointReferenceMachine, _execute_owned_prediction
from fp_reference.indexed_execution import CategoricalPairDomain
from fp_reference.cuda_prefix import _CudaPrefix
from fp_reference.core import ContractError
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.learner import observe_event, commit_event
from fp_reference.profile import attach_boundary
from audit_joint_amp import BUDGET, TOLERANCE, operations, configuration
from audit_joint_runtime import literal
from audit_reference_construction import rejects
from shared_noise_factor_closure import counter_states
from unknown_noise_decoding import Joint, DEFAULT, OTHER
from audit_rational_feature_scale import integer_parts
from rational_feature_scale import Bank, rounded, errors, precision_bound

OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_FEATURE_AMP_CPU.json'
Q = (1 << 200)+1
WIDE = ((F(1, 4), F(Q+1, 4*Q)), (F(1, 2),)*2)
ONE = ((F(1, 3),), (F(1),))


def prediction(before, query, scratch, budget=BUDGET):
    model = before.model
    state = amp.JointAmpState(before)
    plan = amp._prepare_prediction(model, state, model.rules(), model.source_row(query[0]*model.n+query[1]),
        output_cap=128, budget=budget, workspace=scratch, bit_limit=32768)
    arith = amp._Arithmetic(plan.bit_limit)
    raw, resident = amp._prediction_schedule(plan, state, arith)
    assert resident is None and len(arith.trace)+len(raw.words) == amp.prediction_output_cells(plan)
    amp.check_prediction_plan(plan, model, state, model.rules(), model.source_row(query[0]*model.n+query[1]),
        output_cap=128, budget=budget, workspace=scratch, bit_limit=32768)
    assert amp.check_prediction_execution(plan, state, raw, operations(arith), bit_limit=plan.bit_limit) == len(arith.trace)
    oracle = Joint(model.n, model.rates, model.prior)
    weights = oracle.counts(before.steps, before.counts, before.diagonal)
    parts = integer_parts(oracle, weights, query)
    assert plan.rate_parts == raw.rate_parts == parts and plan.normalization == raw.normalization == sum(weights)
    columns, _, traces = rounded(Bank(model.n, model.rates, model.prior, model.native_scale), parts, 0)
    coefficients = amp._Arithmetic(32768)
    coefficient_words = tuple(coefficients.op('constant', constant=c).word
                             for j in range(len(model.rates)) for c in model.coefficients(j))
    assert raw.words == tuple(v.word for v in columns)+coefficient_words
    assert tuple(arith.trace) == traces[0]+tuple(coefficients.trace)
    reference = _execute_owned_prediction(plan, model)
    amp.check_prediction(reference, raw, TOLERANCE, normalizer_cap=2*(model.native_scale-1),
                         activation_cap=model.native_scale-2, bit_limit=32768)
    return plan, raw, reference, columns, arith


def enumeration():
    rows = []
    cases = ((2, DEFAULT, 10), (3, DEFAULT, 10), (2, OTHER, 8), (3, OTHER, 8), (2, ONE, 3), (2, WIDE, 4))
    for n, family, C in cases:
        model = JointRelation(n, *family, feature_scale=F(C))
        machine, spec = JointReferenceMachine(model, BUDGET), JointLearner(model)
        bank, bounds = Bank(n, *family, F(C)), precision_bound(C)
        budget = replace(BUDGET, step_cap=3)
        cuts = forecasts = observations = words = halves = 0
        maxima = {}
        with memoryview(bytearray(decoder.workspace_bytes(model, budget))) as scratch:
            for T, states in counter_states(n*(n-1)//2+1, 3):
                for counts in sorted(states):
                    before = JointCountState(model, counts[:-1], counts[-1], T, T)
                    cuts += 1
                    for query in product(range(n), repeat=2):
                        plan, raw, ref, columns, arith = prediction(before, query, scratch, budget)
                        forecasts += 1
                        words += amp.prediction_output_cells(plan)
                        halves += sum(width == 16 for _, width, _ in arith.trace)
                        decoded = raw.decoded()
                        coefficient_error = max(abs(a-b) for a, b in zip(
                            (F(c) for j in range(len(model.rates)) for c in model.coefficients(j)), decoded.coefficients))
                        assert coefficient_error <= bounds['coefficient_cache']
                        maxima['coefficient_cache'] = max(maxima.get('coefficient_cache', F(0)), coefficient_error)
                        bound = amp.range_bound(model, model.rules(), amp.JointAmpState(before), CategoricalPairDomain(n),
                            normalizer_cap=F(2*(C-1)), activation_cap=F(C-2))
                        assert all(lo <= v <= hi for lo, v, hi in zip(bound.base_lower, decoded.masses, bound.masses_upper))
                        assert sum(decoded.masses) <= bound.stored_mass_sum_upper
                        for y in (0, 1):
                            arithmetic = amp._Arithmetic(32768)
                            actual, resident = amp._observation_schedule(amp.JointAmpState(before), raw, y, arithmetic)
                            expected_columns, expected, traces = rounded(bank, raw.rate_parts, y)
                            assert resident is None and actual.encoded == observe(before, query, y)
                            assert actual.gradient_words == tuple(v.word for v in expected)
                            assert tuple(arithmetic.trace) == traces[1]
                            assert len(arithmetic.trace)+len(actual.gradient_words) == amp.observation_output_cells(raw)
                            amp.check_observation_execution(amp.JointAmpState(before), raw, y, actual,
                                                            operations(arithmetic), bit_limit=32768)
                            observed = machine.observe(model, JointState(before), spec, ref, y, bit_limit=32768)
                            amp.check_state(observed, actual, TOLERANCE, bit_limit=32768)
                            amp.check_state(machine.commit(observed, spec, bit_limit=32768),
                                amp.JointAmpState(commit(actual.encoded)), TOLERANCE, bit_limit=32768)
                            for key, value in errors(bank, raw.rate_parts, expected_columns, expected, y).items():
                                assert value <= bounds[key]
                                maxima[key] = max(maxima.get(key, F(0)), value)
                            observations += 1
                            words += amp.observation_output_cells(raw)
        rows.append(dict(n=n, rates=list(map(str, model.rates)), native_scale=C,
            likelihood_scale_bits=model.scale.bit_length(), reachable_cuts=cuts, predictions=forecasts,
            both_target_observations=observations, words_including_copies=words, half_words=halves,
            maximum_errors={k: str(v) for k, v in maxima.items()}))
    return rows


def native_continuation():
    rows = []
    for n, family, C, repeats in ((3, DEFAULT, 10, 10), (3, OTHER, 8, 10), (2, WIDE, 4, 1), (2, ONE, 3, 10)):
        model = JointRelation(n, *family, feature_scale=F(C))
        machine, spec = JointReferenceMachine(model, BUDGET), JointLearner(model)
        rules, graph, native_spec, native = literal(model)
        reference, physical = JointState(initialize(model)), amp.JointAmpState(initialize(model))
        block = ((0, 1, 0), (1, n-1, 0), (0, n-1, 1), (0, n-1, 0),
                 (n-1, n-1, 1), (n-1, n-1, 0), (1, 0, 1), (0, 1, 0))
        maximum = F(0)
        with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
            for k, (i, j, y) in enumerate(block*repeats):
                plan, raw, ref, _, _ = prediction(physical.encoded, (i, j), scratch)
                cache = evaluate(graph, rules, native.theta, model.source_row(i*n+j), (), bit_limit=32768)
                assert ref.materialize(scalar_cap=10000) == cache
                decoded = raw.decoded().materialize(scalar_cap=10000)
                maximum = max(maximum, *(abs(a-b) for a, b in zip(decoded.values, cache.values)))
                assert maximum <= TOLERANCE.state_atol
                native_observed = observe_event(graph, native, native_spec, cache, y, bit_limit=32768)
                observed = machine.observe(model, reference, spec, ref, y, bit_limit=32768)
                assert observed.materialize(scalar_cap=10000, budget=BUDGET) == native_observed
                arithmetic = amp._Arithmetic(32768)
                actual, _ = amp._observation_schedule(physical, raw, y, arithmetic)
                decoded_state = JointState(actual.encoded, tuple(amp.single(w) for w in actual.gradient_words)).materialize(
                    scalar_cap=10000, budget=BUDGET)
                assert decoded_state.theta == native_observed.theta
                assert max(abs(a-b) for a, b in zip(decoded_state.gradient_sum, native_observed.gradient_sum)) <= TOLERANCE.state_atol
                native = commit_event(native_observed, native_spec, bit_limit=32768)
                reference = machine.commit(observed, spec, bit_limit=32768)
                physical = amp.JointAmpState(commit(actual.encoded))
                assert reference.materialize(scalar_cap=10000, budget=BUDGET) == native
                if k == 3:
                    native = attach_boundary(native, 2, native_spec)
                    reference = machine.attach(reference, 2, spec)
                    physical = amp.JointAmpState(attach(physical.encoded, 2))
        rows.append(dict(native_scale=C, complete_literal_native_triples=8*repeats,
            all_coefficients_fixed_and_selected_gradients_checked=True,
            final_cursor=reference.cursor, optimizer_steps=reference.optimizer_steps,
            maximum_complete_cache_error=str(maximum)))
    return rows


def adversaries():
    model = JointRelation(3, *DEFAULT, feature_scale=F(10))
    before = JointCountState(model, (0, 0, 0), 2, 2, 2)
    state = amp.JointAmpState(before)
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        plan, raw, ref, _, arithmetic = prediction(before, (0, 1), scratch)
        trace = operations(arithmetic)
        kwargs = dict(output_cap=128, budget=BUDGET, workspace=scratch, bit_limit=32768)
        changed_parts = ((653, 643), (442, 458))
        altered = replace(plan, rate_parts=changed_parts)
        rejects(lambda: amp.check_prediction_plan(altered, model, state, model.rules(), model.source_row(1), **kwargs))
        altered_prediction = replace(raw, rate_parts=changed_parts)
        assert altered_prediction.words == raw.words
        rejects(lambda: amp.check_prediction_execution(plan, state, altered_prediction, trace, bit_limit=32768))
        rejects(lambda: amp.check_prediction(ref, altered_prediction, TOLERANCE,
            normalizer_cap=F(18), activation_cap=F(8), bit_limit=32768))
        for k in range(len(raw.words)):
            changed = replace(raw, words=raw.words[:k]+(raw.words[k]^1,)+raw.words[k+1:])
            rejects(lambda: amp.check_prediction_execution(plan, state, changed, trace, bit_limit=32768))
        for k, row in enumerate(trace):
            changed = trace[:k]+((row[0], row[1], (row[2][0]^1,)),)+trace[k+1:]
            rejects(lambda: amp.check_prediction_execution(plan, state, raw, changed, bit_limit=32768))
        for bad in (trace[:-1], trace+(trace[0],), ((trace[0][0], True, trace[0][2]),)+trace[1:]):
            rejects(lambda: amp.check_prediction_execution(plan, state, raw, bad, bit_limit=32768))
        arith = amp._Arithmetic(32768)
        observed, _ = amp._observation_schedule(state, raw, 0, arith)
        obs_trace = operations(arith)
        for k in range(len(observed.gradient_words)):
            changed = replace(observed, gradient_words=observed.gradient_words[:k]+(observed.gradient_words[k]^1,)+observed.gradient_words[k+1:])
            rejects(lambda: amp.check_observation_execution(state, raw, 0, changed, obs_trace, bit_limit=32768))
        for k, row in enumerate(obs_trace):
            changed = obs_trace[:k]+((row[0], row[1], (row[2][0]^1,)),)+obs_trace[k+1:]
            rejects(lambda: amp.check_observation_execution(state, raw, 0, observed, changed, bit_limit=32768))
        rejects(lambda: amp.check_observation_execution(state, altered_prediction, 0, observed, obs_trace, bit_limit=32768))
        rejects(lambda: amp.check_observation_execution(state, raw, 1, observed, obs_trace, bit_limit=32768))
        rejects(lambda: amp._observation_schedule(state, raw, True, amp._Arithmetic(32768)))
        rejects(lambda: replace(raw, words=raw.words[:7]))
        rejects(lambda: replace(raw, rate_parts=raw.rate_parts[:-1]))
        rejects(lambda: replace(raw, rate_parts=((True, 648), (450, 450))))
        rejects(lambda: replace(observed, gradient_words=observed.gradient_words[1:]))
        rejects(lambda: amp._prepare_prediction(model, state, model.rules(), model.source_row(1),
            **(kwargs | {'output_cap': amp.prediction_output_cells(plan)-1})), ArithmeticUnresolved)
        rejects(lambda: amp._prepare_prediction(model, state, model.rules(), model.source_row(1),
            **(kwargs | {'budget': replace(BUDGET, step_cap=1)})), ArithmeticUnresolved)
        rejects(lambda: amp._prepare_prediction(model, state, model.rules(), model.source_row(1),
            **(kwargs | {'bit_limit': 1060})), ArithmeticUnresolved)
    return dict(equal_head_changed_parts_refusals=4, changed_readout_or_coefficient_words=len(raw.words),
        changed_gradient_words=len(observed.gradient_words), changed_prediction_operations=len(trace),
        changed_gradient_operations=len(obs_trace), omitted_extra_or_mistyped_traces=3,
        wrong_or_boolean_target_refusals=2, missing_or_mistyped_complete_coordinates=4,
        output_step_and_precision_refusals=3)


def registration_and_witnesses():
    model = JointRelation(2, *OTHER, feature_scale=F(8))
    contract = configuration(model)
    assert (contract.backend_id, contract.forward_id, contract.work_model) == (amp.BACKEND_ID, amp.FORWARD_ID, amp.WORK_MODEL)
    assert legacy.implementation(model) is amp and legacy.implementation(replace(model, feature_scale=None)) is legacy
    # Exercise the actual private owner's closed routing without initializing a
    # device: this is a routing/type audit, not an owned execution certificate.
    prefix = object.__new__(_CudaPrefix)
    prefix.contract = contract
    raw_state = amp.JointAmpState(initialize(model))
    prefix.check_queue(model.rules(), raw_state, bit_limit=32768)
    assert prefix.theta_binding(raw_state) == raw_state.theta
    assert prefix.joint_implementation is amp
    prefix.check_state(JointState(raw_state.encoded), raw_state, bit_limit=32768)
    assert prefix.forward_work(model, model.rules()) == amp.forward_work(model, BUDGET, contract.phase_output_cells)
    for old in (lambda: legacy.JointAmpState(raw_state.encoded),
                lambda: legacy.ResidentState(raw_state.encoded)):
        rejects(old)
    for invalid in (replace(model, feature_scale=F(17, 2)), replace(model, feature_scale=F((1 << 24)+1))):
        rejects(lambda: configuration(invalid), ArithmeticUnresolved)
        rejects(lambda: amp.JointAmpState(initialize(invalid)), ArithmeticUnresolved)
    wrong = configuration(replace(model, feature_scale=None))
    object.__setattr__(wrong, 'schema', model)
    rejects(wrong.__post_init__)
    initial = amp.JointAmpState(initialize(JointRelation(2, *DEFAULT, feature_scale=F(10))))
    with memoryview(bytearray(decoder.workspace_bytes(initial.encoded.model, BUDGET))) as scratch:
        _, raw, _, _, _ = prediction(initial.encoded, (0, 0), scratch)
        observed, _ = amp._observation_schedule(initial, raw, 0, amp._Arithmetic(32768))
        assert initial.encoded.model.gamma(1) == 0 and amp.single(observed.gradient_words[1]) > 0
    cut = JointCountState(model, (-2,), 0, 2, 2)
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        _, raw, ref, _, _ = prediction(cut, (0, 1), scratch)
        native_error = max(abs(a-b) for a, b in zip(ref.excesses+ref.masses, raw.decoded().excesses+raw.decoded().masses))
        assert native_error == F(8950209, 16471556096) < TOLERANCE.state_atol
    assert 'torch' not in sys.modules
    return dict(distinct_complete_registration=True, old_graph_or_backend_identity_refusals=3,
        unsupported_noninteger_or_large_scale_refusals=4, actual_owner_routing_checked_without_device=True,
        zero_fixed_coefficient_retains_nonzero_gradient=True, S120_C8_native_error=str(native_error),
        original_tolerances_pass=True, torch_imported=False,
        scope='exact scalar/type audit; no actual CUDA or paired installation evidence')


def scalar_boundaries():
    # These synthetic nonnegative arrays test the proved scalar equations;
    # they do not claim to be the canonical partition at the chosen count cut.
    count = words = zeros = 0
    for family, C in ((DEFAULT, 10), (OTHER, 8), (WIDE, 4)):
        model = JointRelation(2, *family, feature_scale=F(C))
        bank = Bank(2, *family, F(C))
        state = amp.JointAmpState(initialize(model))
        plan = decoder.passive_plan(state.encoded, (0, 1), BUDGET)
        J = len(model.rates)
        for exponent in (0, 1, 24, 126, 149, 150, 151, 256, 2000):
            big = 1 << exponent
            arrays = (
                ((big, 0),)+((0, 0),)*(J-1),
                ((0, big),)+((0, 0),)*(J-1),
                tuple((big if j == 0 else 1, 1) for j in range(J)),
                tuple((1, big if j == J-1 else 1) for j in range(J)))
            for parts in arrays:
                Z = sum(map(sum, parts))
                N = tuple(sum(model.coefficient_integers(j)[0]*row[y]+model.coefficient_integers(j)[1]*row[1-y]
                              for j, row in enumerate(parts)) for y in (0, 1))
                synthetic = replace(plan, excesses=N, normalization=Z, rate_parts=parts)
                arith = amp._Arithmetic(32768)
                raw, _ = amp._prediction_schedule(synthetic, state, arith)
                assert len(arith.trace)+len(raw.words) == amp.prediction_output_cells(synthetic)
                words += amp.prediction_output_cells(synthetic)
                for y in (0, 1):
                    arith = amp._Arithmetic(32768)
                    actual, _ = amp._observation_schedule(state, raw, y, arith)
                    columns, expected, traces = rounded(bank, parts, y)
                    assert raw.words[:7] == tuple(v.word for v in columns)
                    assert actual.gradient_words == tuple(v.word for v in expected)
                    assert tuple(arith.trace) == traces[1]
                    assert len(arith.trace)+len(actual.gradient_words) == amp.observation_output_cells(raw)
                    for key, value in errors(bank, parts, columns, expected, y).items():
                        assert value <= precision_bound(C)[key]
                    words += amp.observation_output_cells(raw)
                zeros += sum(v == 0 for row in parts for v in row)
                count += 1
        if family is DEFAULT:
            with memoryview(bytearray(decoder.workspace_bytes(model, replace(BUDGET, integer_bits=4096)))) as scratch:
                narrow = amp._prepare_prediction(model, state, model.rules(), model.source_row(1), output_cap=128,
                    budget=replace(BUDGET, integer_bits=4096), workspace=scratch, bit_limit=32768)
            a, b = amp._Arithmetic(32768), amp._Arithmetic(4096)
            full, _ = amp._prediction_schedule(plan, state, a)
            low, _ = amp._prediction_schedule(narrow, state, b)
            assert full == low and a.trace == b.trace
    return dict(synthetic_arrays=count, words_including_copies=words, zero_parity_parts=zeros,
        largest_binary_exponent=2000, narrower_4096_bit_allowance_preserves_words=True,
        scope='scalar array boundaries, including zero rows; no assertion of reachable canonical count cuts')


def main():
    result = {'status': 'PASS_RATIONAL_FEATURE_AMP_CPU',
              'scope': 'complete actual-input plans, fixed RNE schedule, native coordinates and closed routing; no device execution'}
    for name, function in dict(enumeration=enumeration, native=native_continuation,
                               adversaries=adversaries, registration=registration_and_witnesses,
                               boundaries=scalar_boundaries).items():
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
