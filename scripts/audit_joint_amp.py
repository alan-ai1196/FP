"""Exact joint AMP schedule/relation gate before any actual CUDA execution."""
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
from fp_reference import ReferenceCompilerRuntime, joint_amp as amp, joint_partition_decoder as decoder
from fp_reference import runtime as owner
from fp_reference.cuda_prefix import JointCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.float64_bridge import Float64Contract
from fp_reference.indexed_execution import CategoricalPairDomain
from fp_reference.joint_execution import (JointState, JointLearner, JointReferenceMachine,
    _execute_owned_prediction)
from fp_reference.joint_relation import JointRelation, JointCountState, initialize, observe, commit, attach
from fp_reference.learner import observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import evaluate, ArithmeticUnresolved
from audit_joint_runtime import fixture, literal
from audit_joint_partition_storage import rejects
from shared_noise_factor_closure import counter_states
from unknown_noise_decoding import DEFAULT, OTHER
import mixture_partition_bridge as prototype

OUTPUT = ROOT/'evidence/minimal/FP_JOINT_AMP_CPU.json'
BUDGET = decoder.JointPartitionAllowance(join_cells=64, live_cells=1024, arithmetic=32768, step_cap=2048)
TOLERANCE = Float64Contract(F(1, 100), F(1, 1000))


def operations(arithmetic):
    return tuple(('host-RNE32-ingress' if tag == 'constant' else 'cast-float'+str(width) if tag == 'cast' else tag,
                  width, (word,)) for tag, width, word in arithmetic.trace)


def independent_state(before):
    return prototype.State(prototype.Model(before.n, before.model.rates, before.model.prior),
                           before.counts, before.diagonal, before.cursor, before.steps)


def configuration(schema, budget=BUDGET, **kwargs):
    size = 32 << 20
    storage = CudaStorageContract(size, 64 << 20, {r: (size, 64 << 20) for r in ('deployment', 'compiler')})
    return JointCudaPrefixContract(storage, TOLERANCE.state_atol, TOLERANCE.probability_atol,
                                  schema=schema, partitions=budget, **kwargs)


def prediction(before, query, scratch, budget=BUDGET):
    model = before.model
    raw = amp.JointAmpState(before)
    plan = amp._prepare_prediction(model, raw, model.rules(), model.source_row(query[0]*model.n+query[1]),
        output_cap=64, budget=budget, workspace=scratch, bit_limit=32768)
    arithmetic = amp._Arithmetic(plan.bit_limit)
    actual, resident = amp._prediction_schedule(plan, raw, arithmetic)
    assert resident is None and len(arithmetic.trace)+7 == plan.output_cells
    assert amp.check_prediction_execution(plan, raw, actual, operations(arithmetic), bit_limit=plan.bit_limit) == len(arithmetic.trace)
    oracle = prototype.prepare(independent_state(before), query)
    columns, _, traces = prototype.rounded(oracle)
    assert (plan.excesses, plan.normalization) == (oracle.excess_parts, oracle.normalization)
    assert actual.words == tuple(v.word for v in columns) and tuple(arithmetic.trace) == traces[0]
    return plan, actual, oracle, columns, arithmetic


def enumeration():
    rows = []
    for n, family in ((2, DEFAULT), (3, DEFAULT), (2, OTHER), (3, OTHER), (2, ((F(1, 3),), (F(1),)))):
        model = JointRelation(n, *family)
        budget = replace(BUDGET, step_cap=3)
        machine = JointReferenceMachine(model, budget)
        spec = JointLearner(model)
        states = forecasts = observations = words = halves = native_refusals = 0
        maxima = {}
        with memoryview(bytearray(decoder.workspace_bytes(model, budget))) as scratch:
            for total, level in counter_states(n*(n-1)//2+1, 3):
                for counts in sorted(level):
                    before = JointCountState(model, counts[:-1], counts[-1], total, total)
                    states += 1
                    for query in product(range(n), repeat=2):
                        plan, raw, oracle, columns, arithmetic = prediction(before, query, scratch, budget)
                        ref = _execute_owned_prediction(plan, model)
                        forecasts += 1
                        words += plan.output_cells
                        halves += sum(width == 16 for _, width, _ in arithmetic.trace)
                        prediction_errors = None
                        for y in (0, 1):
                            arith = amp._Arithmetic(32768)
                            actual, resident = amp._observation_schedule(amp.JointAmpState(before), raw, y, arith)
                            expected_arith = amp._Arithmetic(32768)
                            expected, _ = prototype.observation_schedule(oracle, columns, y, expected_arith)
                            assert resident is None and actual.encoded == observe(before, query, y)
                            assert actual.gradient_words == tuple(v.word for v in expected)
                            assert tuple(arith.trace) == tuple(expected_arith.trace)
                            assert len(arith.trace)+len(actual.gradient_words) == 6+8*len(model.rates)
                            amp.check_observation_execution(amp.JointAmpState(before), raw, y, actual,
                                                             operations(arith), bit_limit=32768)
                            observed = machine.observe(model, JointState(before), spec, ref, y, bit_limit=32768)
                            errors = prototype.errors(oracle, columns, expected, y)
                            bounds = prototype.precision_bound(model.scale)
                            for key, value in errors.items():
                                assert value <= bounds[key]
                                maxima[key] = max(maxima.get(key, F(0)), value)
                            check = lambda: amp.check_state(observed, actual, TOLERANCE, bit_limit=32768)
                            if errors['gradient'] > TOLERANCE.state_atol and query[0] != query[1]:
                                rejects(check, ArithmeticUnresolved)
                            else:
                                check()
                            amp.check_state(machine.commit(observed, spec, bit_limit=32768),
                                amp.JointAmpState(commit(actual.encoded)), TOLERANCE, bit_limit=32768)
                            prediction_errors = errors
                            observations += 1
                            words += len(arith.trace)+len(actual.gradient_words)
                        check = lambda: amp.check_prediction(ref, raw, TOLERANCE,
                            normalizer_cap=F(2*(model.scale-1)), activation_cap=F(model.scale-2), bit_limit=32768)
                        if any(prediction_errors[k] > limit for k, limit in (
                                ('native', TOLERANCE.state_atol), ('normalizer', TOLERANCE.state_atol),
                                ('probability', TOLERANCE.probability_atol), ('proper_mass_division', TOLERANCE.probability_atol))):
                            rejects(check, ArithmeticUnresolved)
                            native_refusals += 1
                        else:
                            check()
                        bound = amp.range_bound(model, model.rules(), amp.JointAmpState(before),
                            CategoricalPairDomain(n),
                            normalizer_cap=F(2*(model.scale-1)), activation_cap=F(model.scale-2))
                        decoded = raw.decoded()
                        assert all(lo <= v <= hi for lo, v, hi in zip(bound.base_lower, decoded.masses, bound.masses_upper))
                        assert sum(decoded.masses) <= bound.stored_mass_sum_upper
        rows.append({'n': n, 'rates': tuple(map(str, model.rates)), 'reachable_cuts': states,
            'predictions': forecasts, 'both_target_observations': observations, 'words_including_copies': words,
            'half_words': halves, 'original_tolerance_prediction_refusals': native_refusals,
            'maximum_errors': {k: str(v) for k, v in maxima.items()}})
    return rows


def native_continuation():
    model = JointRelation(3, *DEFAULT)
    machine, spec = JointReferenceMachine(model, BUDGET), JointLearner(model)
    rules, graph, native_spec, native = literal(model)
    reference, physical = JointState(initialize(model)), amp.JointAmpState(initialize(model))
    block = ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 2, 0), (2, 2, 1), (2, 2, 0), (1, 0, 1), (0, 1, 0))
    word = block*10
    max_error = F(0)
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        for k, (i, j, y) in enumerate(word):
            plan, raw, _, _, _ = prediction(physical.encoded, (i, j), scratch)
            ref = _execute_owned_prediction(plan, model)
            native_prediction = evaluate(graph, rules, native.theta, model.source_row(i*3+j), (), bit_limit=32768)
            assert ref.materialize(scalar_cap=10000) == native_prediction
            floating = raw.decoded().materialize(scalar_cap=10000)
            errors = tuple(abs(a-b) for a, b in zip(native_prediction.values, floating.values))
            assert max(errors) <= TOLERANCE.state_atol
            max_error = max(max_error, *errors)
            native_observed = observe_event(graph, native, native_spec, native_prediction, y, bit_limit=32768)
            observed = machine.observe(model, reference, spec, ref, y, bit_limit=32768)
            assert observed.materialize(scalar_cap=10000, budget=BUDGET) == native_observed
            arithmetic = amp._Arithmetic(32768)
            actual, _ = amp._observation_schedule(physical, raw, y, arithmetic)
            decoded = JointState(actual.encoded, tuple(amp.single(v) for v in actual.gradient_words)).materialize(
                scalar_cap=10000, budget=BUDGET)
            assert decoded.theta == native_observed.theta
            assert max(abs(a-b) for a, b in zip(decoded.gradient_sum, native_observed.gradient_sum)) <= TOLERANCE.state_atol
            native = commit_event(native_observed, native_spec, bit_limit=32768)
            reference = machine.commit(observed, spec, bit_limit=32768)
            physical = amp.JointAmpState(commit(actual.encoded))
            assert reference.materialize(scalar_cap=10000, budget=BUDGET) == native
            amp.check_state(reference, physical, TOLERANCE, bit_limit=32768)
            if k == 3:
                native = attach_boundary(native, 2, native_spec)
                reference = machine.attach(reference, 2, spec)
                physical = amp.JointAmpState(attach(physical.encoded, 2))
    return {'complete_literal_native_triples': len(word), 'profile_attachment_step': 4,
        'profile_attachment_cursor': 2, 'final_cursor': reference.cursor, 'final_steps': reference.optimizer_steps,
        'all_slots_and_caches_checked': True, 'maximum_native_activation_error': str(max_error)}


def witnesses():
    rows = []
    for model, before, query, name in (
        (JointRelation(2, *OTHER), (2, 0, 2, -2), (0, 1), 'S120-two-event-native-refusal'),
        (JointRelation(2, *DEFAULT), (29, 0, 27, 29), (0, 1), 'old-A1-cut-new-schedule')):
        steps, diagonal, cursor, count = before
        encoded = JointCountState(model, (count,), diagonal, cursor, steps)
        with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
            plan, raw, oracle, columns, _ = prediction(encoded, query, scratch)
            ref = _execute_owned_prediction(plan, model)
            checker = lambda: amp.check_prediction(ref, raw, TOLERANCE,
                normalizer_cap=F(2*(model.scale-1)), activation_cap=F(model.scale-2), bit_limit=32768)
            gradient, _ = prototype.observation_schedule(oracle, columns, 1, amp._Arithmetic(32768))
            errors = prototype.errors(oracle, columns, gradient, 1)
            if model.scale == 120:
                assert errors['native'] == F(65863667, 4117889024)
                rejects(checker, ArithmeticUnresolved)
            else:
                checker()
            rows.append({'case': name, 'native_error': str(errors['native']), 'normalizer_error': str(errors['normalizer']),
                         'probability_error': str(errors['probability']), 'status': 'UNRESOLVED' if model.scale == 120 else 'PASS'})
    model = JointRelation(2, (F(1, 10), F(1, 5)), (F(1, 2), F(1, 2)))
    encoded = JointCountState(model, (1000,), 0, 1000, 1000)
    restored = JointCountState(model, (0,), 0, 2000, 2000)
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        _, raw, _, _, _ = prediction(encoded, (0, 1), scratch)
        _, recovered, _, _, _ = prediction(restored, (0, 1), scratch)
    assert raw.decoded().excesses[1] == 0 and recovered.decoded().probabilities == (F(1, 2),)*2
    initial = replace(restored, steps=0)
    rejects(lambda: amp.check_state(JointState(restored), amp.JointAmpState(initial), TOLERANCE, bit_limit=32768))
    return {'scale_and_historical_cut': rows, 'temporary_zero_excess_restores_half_forecast': True,
        'd_zero_does_not_erase_T_or_rate_posterior': True,
        'reversal_scope': 'two reachable exact/RNE snapshots, not 2000 device events'}


def adversaries():
    model = JointRelation(3, *DEFAULT)
    state = commit(observe(initialize(model), (1, 2), 0))
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        plan, raw, _, _, arithmetic = prediction(state, (0, 1), scratch)
        kwargs = dict(output_cap=64, budget=BUDGET, workspace=scratch, bit_limit=32768)
        checker = lambda p: amp.check_prediction_plan(p, model, amp.JointAmpState(state), model.rules(), model.source_row(1), **kwargs)
        changes = {'query': (1, 2), 'order': plan.order[::-1], 'normalization': plan.normalization+1,
            'excesses': tuple(2*v for v in plan.excesses), 'integer_envelope': plan.integer_envelope+1,
            'maximum_integer_bits': plan.maximum_integer_bits+1, 'multiplications': plan.multiplications+1,
            'additions': plan.additions+1, 'compacted_cells': plan.compacted_cells+1,
            'cell_bytes': plan.cell_bytes+1, 'workspace_bytes': plan.workspace_bytes+1, 'bit_limit': plan.bit_limit-1,
            'before': replace(state, steps=state.steps+2)}
        for key, value in changes.items():
            rejects(lambda: checker(replace(plan, **{key: value})))
        rejects(lambda: checker(replace(plan, excesses=tuple(2*v for v in plan.excesses), normalization=2*plan.normalization)))
        trace = operations(arithmetic)
        for k in range(7):
            altered = replace(raw, words=raw.words[:k]+(raw.words[k]^1,)+raw.words[k+1:])
            rejects(lambda: amp.check_prediction_execution(plan, amp.JointAmpState(state), altered, trace, bit_limit=32768))
        for k, row in enumerate(trace):
            altered = trace[:k]+((row[0], row[1], (row[2][0]^1,)),)+trace[k+1:]
            rejects(lambda: amp.check_prediction_execution(plan, amp.JointAmpState(state), raw, altered, bit_limit=32768))
        for altered in (trace[:-1], trace+(trace[0],)):
            rejects(lambda: amp.check_prediction_execution(plan, amp.JointAmpState(state), raw, altered, bit_limit=32768))
        obs_arithmetic = amp._Arithmetic(32768)
        observed, _ = amp._observation_schedule(amp.JointAmpState(state), raw, 0, obs_arithmetic)
        obs_trace = operations(obs_arithmetic)
        for k in range(len(observed.gradient_words)):
            altered = replace(observed, gradient_words=observed.gradient_words[:k]+(observed.gradient_words[k]^1,)+observed.gradient_words[k+1:])
            rejects(lambda: amp.check_observation_execution(amp.JointAmpState(state), raw, 0, altered, obs_trace, bit_limit=32768))
        rejects(lambda: amp.check_observation_execution(amp.JointAmpState(state), raw, 1, observed, obs_trace, bit_limit=32768))
        rejects(lambda: amp._observation_schedule(amp.JointAmpState(state), raw, True, amp._Arithmetic(32768)))
        rejects(lambda: amp._prepare_prediction(model, amp.JointAmpState(state), model.rules(), model.source_row(1),
            **{**kwargs, 'output_cap': plan.output_cells-1}), ArithmeticUnresolved)
        extra = replace(raw)
        object.__setattr__(extra, 'unregistered', True)
        rejects(lambda: amp.check_prediction_execution(plan, amp.JointAmpState(state), extra, trace, bit_limit=32768))
    cfg, _, online = fixture(3, 3, budget=BUDGET)
    cuda = configuration(model)
    checks = (replace(cuda, schema=replace(model, rates=model.rates[::-1])),
              replace(cuda, partitions=replace(BUDGET, step_cap=BUDGET.step_cap-1)))
    with patch.object(owner, '_CudaPrefix', side_effect=AssertionError('foreign joint registration reached CUDA')) as forbidden:
        for other in checks:
            rejects(lambda: ReferenceCompilerRuntime(cfg, model, online=online, cuda=other))
        assert not forbidden.called
    zero_model = JointRelation(2, (F(1, 3),), (F(1),))
    with memoryview(bytearray(decoder.workspace_bytes(zero_model, BUDGET))) as scratch:
        p, z, _, _, a = prediction(initialize(zero_model), (0, 0), scratch)
        t = operations(a)
        at = next(k for k, row in enumerate(t) if row[2] == (0,))
        bad = t[:at]+((t[at][0], t[at][1], (False,)),)+t[at+1:]
        rejects(lambda: amp.check_prediction_execution(p, amp.JointAmpState(p.before), z, bad, bit_limit=32768))
    narrower = replace(BUDGET, integer_bits=4096)
    with memoryview(bytearray(decoder.workspace_bytes(model, narrower))) as scratch:
        p, result, _, _, _ = prediction(state, (0, 1), scratch, narrower)
        assert p.bit_limit == 4096 and result.words == raw.words
    return {'plan_field_refusals': len(changes), 'common_root_scaling_refused': True,
        'prediction_word_refusals': 7, 'gradient_word_refusals': 5, 'operation_word_refusals': len(trace),
        'trace_length_refusals': 2, 'extra_field_and_boolean_word_refusals': 2,
        'actual_target_binding_refusals': 2, 'output_extent_refusals': 1, 'foreign_cuda_registration_refusals': len(checks),
        'narrower_integer_allowance_preserves_the_same_RNE_words': 4096}


SECTIONS = {'enumeration': enumeration, 'native': native_continuation, 'witnesses': witnesses, 'adversaries': adversaries}


def run(section=None):
    result = {'status': 'PASS_JOINT_AMP_CPU', 'complete_audit': section is None,
        'scope': 'Exact native/RNE schedule and relation audit. No actual device, owned AMP phase, installation or constructor certificate.'}
    for key, fn in SECTIONS.items():
        if section in (None, key):
            result[key] = fn()
            print('PASS '+key, flush=True)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=tuple(SECTIONS))
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert args.section is None or not args.write
    result = run(args.section)
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8', newline='\n')
    print(text, end='')
