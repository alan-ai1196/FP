"""Complete actual CUDA learners beside owned Reference Runtime events.

The device helpers have no Runtime authority yet. This audit checks their
full continuous state against a separate exact rounded interpreter and
compares them to the Runtime's own exact trajectories. It does not install
GPU state, borrow reference wealth or claim complete device ownership.
"""
from dataclasses import dataclass, replace
from contextlib import nullcontext
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference import cuda_learner as gpu
from fp_reference.core import ContractError
from fp_reference.learner import LearnerSpec
from fp_reference.profile import ProfileSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, Source, State, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved
from audit_cuda_primitives import HALF, SINGLE
from audit_reference_construction import contract, domain, limits, rejects, zero_program
from audit_reference_events import online, shared_graph
from ingress_audit_support import deliver_context


def q(value, layout=SINGLE):
    return layout.decode(layout.rounded(value))


@dataclass(frozen=True)
class ModelState:
    theta: tuple
    delayed: tuple
    gradient: tuple
    unit: int
    cursor: int
    steps: int


def model_initial(graph, rules, theta, cursor=0):
    return ModelState(tuple(map(q, theta)), tuple((s.state_id, (F(0),)*s.delay) for s in rules.states),
                      (F(0),)*graph.slot_count, 0, cursor, 0)


def model_predict(graph, rules, state, inputs):
    """Independent exact rounded evaluation with its own incoming-edge tape."""
    sources = {key: q(q(value), HALF) for key, value in inputs.items()}
    theta = tuple(q(value, HALF) for value in state.theta)
    histories = dict(state.delayed)
    values, incoming = [], []
    for node in graph.nodes:
        if isinstance(node, Source):
            value, edges = sources[node.source_id], ()
        elif isinstance(node, State):
            value, edges = histories[node.state_id][0], ()
        elif isinstance(node, Product):
            value = q(values[node.left]*values[node.right], HALF)
            edges = ((node.left, values[node.right], None), (node.right, values[node.left], None))
        else:
            value, edges = F(0), []
            for term in node.terms:
                weighted = q(theta[term.slot]*values[term.parent], HALF)
                value = q(value+weighted)
                edges.append((term.parent, theta[term.slot], (term.slot, values[term.parent])))
            value = q(value, HALF)
        values.append(value)
        incoming.append(tuple(edges))
    excesses = tuple(values[h] for h in graph.heads)
    masses = tuple(q(q(base)+value) for base, value in zip(rules.base, excesses))
    normalizer = F(0)
    for value in masses:
        normalizer = q(normalizer+value)
    probabilities = tuple(q(value/normalizer) for value in masses)
    bodies = {binding.state_id: values[binding.body] for binding in graph.bindings}
    delayed = tuple((s.state_id, histories[s.state_id][1:]+(bodies[s.state_id],)) for s in rules.states)
    return {'values': tuple(values), 'theta_half': theta, 'excesses': excesses, 'masses': masses,
            'normalizer': normalizer, 'probabilities': probabilities, 'delayed': delayed,
            'incoming': tuple(incoming)}


def model_observe(graph, state, prediction, target):
    inverse_t, inverse_y = q(1/prediction['normalizer']), q(1/prediction['masses'][target])
    seed_target = q(inverse_t-inverse_y)
    adjoint, slots = [F(0)]*len(graph.nodes), [F(0)]*graph.slot_count
    for label, head in enumerate(graph.heads):
        adjoint[head] = q(adjoint[head]+(seed_target if label == target else inverse_t))
    for index in reversed(range(len(graph.nodes))):
        seed = adjoint[index]
        for parent, weight, parameter in prediction['incoming'][index]:
            if parameter is not None:
                slot, value = parameter
                slots[slot] = q(slots[slot]+q(seed*value))
            adjoint[parent] = q(adjoint[parent]+q(seed*weight))
    accumulated = tuple(q(a+b) for a, b in zip(state.gradient, slots))
    return replace(state, delayed=prediction['delayed'], gradient=accumulated,
                   unit=state.unit+1, cursor=state.cursor+1)


def model_commit(state, spec):
    assert state.unit == spec.update_unit and state.cursor % spec.update_unit == 0
    scale = q(q(spec.learning_rate)/q(F(spec.update_unit)))
    if spec.optimizer_id == 'mean-ce-normalized-simplex-gradient-v1':
        total = moment = F(0)
        for index in spec.simplex_slots:
            total = q(total+state.theta[index])
            moment = q(moment+q(state.theta[index]*state.gradient[index]))
        mean = q(moment/total)
        theta = list(state.theta)
        normalization = F(0)
        for index in spec.simplex_slots:
            multiplier = q(F(1)-q(scale*q(state.gradient[index]-mean)))
            theta[index] = q(state.theta[index]*multiplier)
            assert theta[index] >= 0
            normalization = q(normalization+theta[index])
        for index in spec.simplex_slots:
            theta[index] = max(F(0),q(theta[index]/normalization))
        return replace(state, theta=tuple(theta), gradient=(F(0),)*len(theta), unit=0, steps=state.steps+1)
    theta = []
    for value, gradient in zip(state.theta, state.gradient):
        updated = max(F(0), q(value-q(scale*gradient)))
        if spec.commit_grid_bits is not None:
            scale_grid = 1 << spec.commit_grid_bits
            scaled = updated*scale_grid
            updated = F(scaled.numerator//scaled.denominator, scale_grid)
        theta.append(updated)
    return replace(state, theta=tuple(theta), gradient=(F(0),)*len(theta), unit=0, steps=state.steps+1)


def same_values(actual, expected, layout=SINGLE):
    assert gpu.raw_tensor(actual) == tuple(layout.encode_exact(value) for value in expected)


def same_state(actual, expected):
    same_values(actual.theta, expected.theta)
    same_values(actual.gradient_sum, expected.gradient)
    assert (actual.unit_count, actual.cursor, actual.optimizer_steps) == (expected.unit, expected.cursor, expected.steps)
    assert tuple(key for key, _ in actual.delayed) == tuple(key for key, _ in expected.delayed)
    for (_, values), (_, wanted) in zip(actual.delayed, expected.delayed):
        same_values(values, wanted, HALF)


def same_prediction(actual, expected):
    for label in ('values', 'theta_half', 'excesses', 'masses', 'probabilities'):
        same_values(getattr(actual, label), expected[label], HALF if label in ('values', 'theta_half', 'excesses') else SINGLE)
    same_values(actual.normalizer, (expected['normalizer'],))
    assert tuple(key for key, _ in actual.delayed) == tuple(key for key, _ in expected['delayed'])
    for (_, values), (_, wanted) in zip(actual.delayed, expected['delayed']):
        same_values(values, wanted, HALF)


class Audit:
    def __init__(self, arena=None):
        self.arena = arena
        self.phases = 0
        self.half_results = 0
        self.half_multiply_results = 0
        self.single_results = 0
        self.reference_coordinates = 0
        self.reference_recast_differences = 0
        self.maximum_state_error = F(0)

    def execute(self, function, *args):
        with (nullcontext(None) if self.arena is None else self.arena.phase('learner-audit:'+function.__name__)) as workspace:
            arithmetic = gpu.CudaArithmetic(32768, workspace=workspace)
            value = function(*args, arithmetic)
            trace = arithmetic.raw_trace()
        self.phases += 1
        self.half_results += sum(len(words) for _, width, words in trace if width == 16)
        self.half_multiply_results += sum(len(words) for op, width, words in trace if width == 16 and op == 'mul')
        self.single_results += sum(len(words) for _, width, words in trace if width == 32)
        return value

    def compare_reference(self, actual, reference):
        assert (actual.unit_count, actual.cursor, actual.optimizer_steps) == (
            reference.unit_count, reference.cursor, reference.optimizer_steps)
        pairs = [(actual.theta, reference.theta, SINGLE), (actual.gradient_sum, reference.gradient_sum, SINGLE)]
        assert tuple(key for key, _ in actual.delayed) == tuple(key for key, _ in reference.delayed)
        pairs.extend((a, b, HALF) for (_, a), (_, b) in zip(actual.delayed, reference.delayed))
        for tensor, values, layout in pairs:
            for word, exact in zip(gpu.raw_tensor(tensor), values):
                self.reference_coordinates += 1
                self.reference_recast_differences += word != layout.rounded(exact)
                self.maximum_state_error = max(self.maximum_state_error, abs(layout.decode(word)-exact))

    def result(self):
        return {'actual_CUDA_phases': self.phases, 'half_arithmetic_or_ingress_results': self.half_results,
                'actual_half_multiply_results': self.half_multiply_results,
                'single_arithmetic_or_ingress_results': self.single_results,
                'reference_state_coordinates_compared': self.reference_coordinates,
                'coordinates_differing_from_recast_exact_reference': self.reference_recast_differences,
                'largest_observed_state_absolute_error_float64_summary': (
                    float(self.maximum_state_error) if self.reference_coordinates else None)}


def exhaustive_audit(*, arena=None):
    audit, events = Audit(arena), 0
    cfg = replace(contract(pattern=(F(1, 3), F(1, 4), F(0))), reference_integer_bits=32768,
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    rules, graph = cfg.semantics, shared_graph()
    for sequence in product(product((0, 1), repeat=2), repeat=3):
        run = online(cfg, 3, unit=2, rate=F(1, 8), grid=16)
        runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
        assert runtime.construct_candidate(graph).status == 'BUILT_REFERENCE'
        graphs = dict(runtime.snapshot().programs)
        actual, expected = {}, {}
        for state in runtime.snapshot().candidates:
            native = graphs[state.program_id]
            actual[state.candidate_id] = audit.execute(gpu.initialize, native, rules, state.theta, 0)
            expected[state.candidate_id] = model_initial(native, rules, state.theta)
            same_state(actual[state.candidate_id], expected[state.candidate_id])
        for cursor, (context, target) in enumerate(sequence):
            row = domain(1)[context]
            sources = dict(zip((s.source_id for s in rules.sources), row))
            assert deliver_context(runtime, f'observation-{cursor}', row).status == 'PREDICTED_REFERENCE'
            for state in runtime.snapshot().candidates:
                key, native = state.candidate_id, graphs[state.program_id]
                previous, previous_raw = actual[key], gpu.raw_state(actual[key])
                prediction = audit.execute(gpu.evaluate, native, rules, previous, sources)
                model_prediction = model_predict(native, rules, expected[key], sources)
                same_prediction(prediction, model_prediction)
                actual[key] = audit.execute(gpu.observe_event, native, rules, previous, run.learner, prediction, target)
                expected[key] = model_observe(native, expected[key], model_prediction, target)
                same_state(actual[key], expected[key])
                assert gpu.raw_state(previous) == previous_raw
                assert actual[key].theta is previous.theta
                if (cursor+1) % 2 == 0:
                    before_commit, before_raw = actual[key], gpu.raw_state(actual[key])
                    actual[key] = audit.execute(gpu.commit_event, actual[key], run.learner)
                    expected[key] = model_commit(expected[key], run.learner)
                    same_state(actual[key], expected[key])
                    assert gpu.raw_state(before_commit) == before_raw
            assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
            for state in runtime.snapshot().candidates:
                audit.compare_reference(actual[state.candidate_id], state.learner)
                assert actual[state.candidate_id].unit_count == (cursor+1) % 2
            events += 1
        # A partial final unit stays partial; no synthetic optimizer flush.
        assert all(state.unit_count == 1 for state in actual.values())
        assert runtime.install(runtime.snapshot().deployed_id, bridge=True).status == 'UNRESOLVED'
    assert audit.reference_recast_differences > 0 and audit.half_results > 0
    return {'all_binary_context_target_three_event_streams': 64, 'ordinary_events': events,
            'reference_and_CUDA_baseline_candidate_paths': 4,
            'all_parameters_accumulators_queues_and_clocks_compared': True,
            'predecessor_device_tensors_unchanged': True, 'partial_final_units_preserved': True,
            **audit.result()}


def profile_recurrence_audit(*, arena=None):
    audit = Audit(arena)
    profile = ProfileSpec('old-data', ('observation-0', 'observation-1'), 3)
    cfg = replace(contract(pattern=(F(1, 8), F(1, 3), F(1, 4))), reference_integer_bits=32768,
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    rules = replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(10)),))
    cfg = replace(cfg, semantics=rules)
    graph = Program((State('h'), Source('x0_0'), Source('x0_1'),
                     Sum('mass', (Term(0, 0), Term(1, 1))), Product('mass', 3, 3),
                     Sum('mass', (Term(4, 2),))), 3, (3, 5), (Binding('h', 3),))
    baseline = Program((Sum('mass', ()),), 0, (0, 0), (Binding('h', 0),))
    run = replace(online(cfg, 6, unit=2, rate=F(1, 64), grid=16), profiles=(profile,))
    runtime = ReferenceCompilerRuntime(cfg, baseline, online=run)
    initial_gpu = audit.execute(gpu.initialize, baseline, rules, (), 0)
    initial_model = model_initial(baseline, rules, ())
    same_state(initial_gpu, initial_model)
    for cursor, target in enumerate((0, 1)):
        row = domain(1)[cursor]
        inputs = dict(zip((s.source_id for s in rules.sources), row))
        assert deliver_context(runtime, f'observation-{cursor}', row).status == 'PREDICTED_REFERENCE'
        predicted = audit.execute(gpu.evaluate, baseline, rules, initial_gpu, inputs)
        expected = model_predict(baseline, rules, initial_model, inputs)
        same_prediction(predicted, expected)
        initial_gpu = audit.execute(gpu.observe_event, baseline, rules, initial_gpu, run.learner, predicted, target)
        initial_model = model_observe(baseline, initial_model, expected, target)
        same_state(initial_gpu, initial_model)
        if cursor == 1:
            initial_gpu = audit.execute(gpu.commit_event, initial_gpu, run.learner)
            initial_model = model_commit(initial_model, run.learner)
        same_state(initial_gpu, initial_model)
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
    built = runtime.construct_candidate(graph, profile_id=profile.profile_id)
    assert built.status == 'BUILT_REFERENCE', built
    theta = cfg.initializer_pattern
    actual = audit.execute(gpu.initialize, graph, rules, theta, 0)
    model = model_initial(graph, rules, theta)
    same_state(actual, model)
    retained = {obs.observation_id: obs for obs in runtime.snapshot().observations}
    # Read only the Runtime's retained revealed contexts/targets, in the
    # registered profile order, keeping the complete recurrent local history.
    for observation_id in profile.observation_ids*profile.passes:
        observation = retained[observation_id]
        inputs = dict(observation.sources)
        predicted = audit.execute(gpu.evaluate, graph, rules, actual, inputs)
        expected = model_predict(graph, rules, model, inputs)
        same_prediction(predicted, expected)
        previous, previous_raw = actual, gpu.raw_state(actual)
        actual = audit.execute(gpu.observe_event, graph, rules, actual, run.learner, predicted, observation.target)
        model = model_observe(graph, model, expected, observation.target)
        assert gpu.raw_state(previous) == previous_raw
        same_state(actual, model)
        if model.cursor % 2 == 0:
            actual = audit.execute(gpu.commit_event, actual, run.learner)
            model = model_commit(model, run.learner)
            same_state(actual, model)
    previous = actual
    actual = gpu.attach_clock(actual, 2, run.learner)
    model = replace(model, cursor=2)
    assert actual.theta is previous.theta and actual.delayed is previous.delayed and actual.gradient_sum is previous.gradient_sum
    same_state(actual, model)
    candidate = next(state for state in runtime.snapshot().candidates if state.candidate_id == built.candidate_id)
    audit.compare_reference(actual, candidate.learner)
    for cursor, target in enumerate((1, 0, 0, 1), 2):
        row = domain(1)[cursor % 2]
        inputs = dict(zip((s.source_id for s in rules.sources), row))
        assert deliver_context(runtime, f'observation-{cursor}', row).status == 'PREDICTED_REFERENCE'
        for native, is_candidate in ((baseline, False), (graph, True)):
            before = actual if is_candidate else initial_gpu
            expected_before = model if is_candidate else initial_model
            predicted = audit.execute(gpu.evaluate, native, rules, before, inputs)
            expected = model_predict(native, rules, expected_before, inputs)
            same_prediction(predicted, expected)
            after = audit.execute(gpu.observe_event, native, rules, before, run.learner, predicted, target)
            expected_after = model_observe(native, expected_before, expected, target)
            same_state(after, expected_after)
            if (cursor+1) % 2 == 0:
                after = audit.execute(gpu.commit_event, after, run.learner)
                expected_after = model_commit(expected_after, run.learner)
                same_state(after, expected_after)
            if is_candidate:
                actual, model = after, expected_after
            else:
                initial_gpu, initial_model = after, expected_after
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
        for state in runtime.snapshot().candidates:
            audit.compare_reference(actual if state.candidate_id == built.candidate_id else initial_gpu, state.learner)
    assert actual.optimizer_steps == 5 and len(actual.delayed[0][1]) == 2
    assert audit.reference_recast_differences > 0
    return {'original_revealed_profile_records': 2, 'actual_profile_replayed_events': 6,
            'ordinary_events': 6, 'candidate_final_optimizer_steps': 5,
            'profile_attachment_preserves_all_device_buffers': True,
            'both_delayed_queue_positions_compared_every_event': True, **audit.result()}


def topology_audit(*, arena=None):
    """Different native graphs, three labels, arbitrary legal source values."""
    rng, audit = random.Random(2026091371), Audit(arena)
    cfg = contract(k=3, pattern=(F(1, 8), F(1, 3), F(1, 4), F(0)))
    spec = LearnerSpec(3, F(1, 16))
    # One value lies just above a half midpoint, but RNE32 ingress first
    # rounds it back to the midpoint. Direct rational-to-half is different.
    double_round = F(1, 2)+F(1, 1 << 12)+F(1, 1 << 26)
    assert q(q(double_round), HALF) != q(double_round, HALF)
    source_values = (F(0), F(1), F(1, 3), F(1, 7), double_round)
    for _ in range(24):
        nodes = [Source('x0_0'), Source('x0_1'), Sum('mass', ())]
        for _ in range(9):
            if rng.randrange(3) == 0:
                parent = rng.randrange(len(nodes))
                nodes.append(Product('mass', parent, parent if rng.randrange(2) else rng.randrange(len(nodes))))
            else:
                edges = tuple(Term(rng.randrange(len(nodes)), rng.randrange(3)) for _ in range(rng.randrange(5)))
                nodes.append(Sum('mass', edges))
        # Repeated nontrivial heads and an explicitly unused fourth slot.
        head = rng.randrange(3, len(nodes))
        graph = Program(tuple(nodes), 4, (head, head, len(nodes)-1))
        actual = audit.execute(gpu.initialize, graph, cfg.semantics, cfg.initializer_pattern, 0)
        model = model_initial(graph, cfg.semantics, cfg.initializer_pattern)
        same_state(actual, model)
        for cursor in range(4):
            inputs = {s.source_id: rng.choice(source_values) for s in cfg.semantics.sources}
            inputs['x0_0'] = double_round if cursor == 0 else inputs['x0_0']
            target = rng.randrange(3)
            prediction = audit.execute(gpu.evaluate, graph, cfg.semantics, actual, inputs)
            expected = model_predict(graph, cfg.semantics, model, inputs)
            same_prediction(prediction, expected)
            previous, previous_raw = actual, gpu.raw_state(actual)
            actual = audit.execute(gpu.observe_event, graph, cfg.semantics, actual, spec, prediction, target)
            model = model_observe(graph, model, expected, target)
            same_state(actual, model)
            assert gpu.raw_state(previous) == previous_raw
            if (cursor+1) % 3 == 0:
                actual = audit.execute(gpu.commit_event, actual, spec)
                model = model_commit(model, spec)
                same_state(actual, model)
            assert gpu.raw_tensor(actual.gradient_sum)[-1] == 0
        assert actual.unit_count == 1 and actual.optimizer_steps == 1
    return {'seeded_native_graphs': 24, 'events_per_graph': 4, 'labels': 3,
            'repeated_edges_heads_squares_and_unused_slots': True,
            'host_single_then_device_half_source_rounding_checked': True,
            'all_full_states_and_native_predictions_match_exact_rounded_model': True, **audit.result()}


def failure_and_grid_audit():
    import torch
    cfg, spec = contract(), LearnerSpec(2, F(1, 8), 16)
    graph = shared_graph()
    state = gpu.initialize(graph, cfg.semantics, cfg.initializer_pattern, 0, gpu.CudaArithmetic(4096))
    rejects(lambda: gpu.commit_event(state, spec, gpu.CudaArithmetic(4096)))
    rejects(lambda: gpu.attach_clock(state, 1, spec))
    rejects(lambda: gpu.evaluate(graph, cfg.semantics, state, {}, gpu.CudaArithmetic(4096)))
    rejects(lambda: gpu.CudaArithmetic(4096).div(torch.ones(1, device='cuda'), 3.0))
    rejects(lambda: gpu.CudaArithmetic(4096).mul(torch.ones(1, device='cuda'), 3.0))
    rejects(lambda: gpu.CudaArithmetic(4096).add(torch.ones(1, device='cuda'), torch.ones(1, device='cuda', dtype=torch.float16)))
    rejects(lambda: gpu.initialize(object(), cfg.semantics, cfg.initializer_pattern, 0, gpu.CudaArithmetic(4096)))
    rejects(lambda: gpu.initialize(graph, cfg.semantics, (F(1 << 128),)*3, 0, gpu.CudaArithmetic(4096)), ArithmeticUnresolved)
    overflow = gpu.initialize(graph, cfg.semantics, (F(65536),)*3, 0, gpu.CudaArithmetic(4096))
    before = gpu.raw_state(overflow)
    phase = gpu.CudaArithmetic(4096)
    rejects(lambda: gpu.evaluate(graph, cfg.semantics, overflow, dict(zip(('x0_0', 'x0_1'), domain(1)[0])), phase), ArithmeticUnresolved)
    assert gpu.raw_state(overflow) == before
    assert any(word & 0x7c00 == 0x7c00 for _, width, words in phase.raw_trace() if width == 16 for word in words)

    # All input states are finite. A positive overflowing step becomes -inf
    # and then a finite projected zero. The retained tape must still refuse.
    maximum = SINGLE.tensor([0x7f7fffff], torch)
    pending = gpu.CudaLearnerState(torch.zeros(1, device='cuda'), (), maximum, 1, 1, 0)
    before = gpu.raw_state(pending)
    phase = gpu.CudaArithmetic(4096)
    rejects(lambda: gpu.commit_event(pending, LearnerSpec(1, F(2)), phase), ArithmeticUnresolved)
    assert gpu.raw_state(pending) == before
    trace = phase.raw_trace()
    assert any(op == 'positive-part' and words == (0,) for op, _, words in trace)
    assert any(op == 'mul' and words == (0x7f800000,) for op, _, words in trace)

    # A mutable tensor handle is not an immutable proof. Helpers revalidate
    # complete state; Runtime must retain private ownership before integration.
    corrupt = gpu.initialize(graph, cfg.semantics, cfg.initializer_pattern, 0, gpu.CudaArithmetic(4096))
    corrupt.theta[0] = float('nan')
    rejects(lambda: gpu.evaluate(graph, cfg.semantics, corrupt,
            dict(zip(('x0_0', 'x0_1'), domain(1)[0])), gpu.CudaArithmetic(4096)), ArithmeticUnresolved)

    rng = random.Random(2026091370)
    words = [0, 1, 2, 0x007fffff, 0x00800000, 0x7f7fffff,
             *[rng.randrange(0x7f800000) for _ in range(128)]]
    values = SINGLE.tensor(words, torch)
    compared = 0
    for bits in (0, 1, 8, 16, 23, 24, 126, 149, 150, 4095):
        phase = gpu.CudaArithmetic(4096)
        actual = phase.floor_grid(values, bits)
        phase.check()
        expected = []
        for word in words:
            value = SINGLE.decode(word)*(1 << bits)
            exact = F(value.numerator//value.denominator, 1 << bits)
            expected.append(SINGLE.encode_exact(exact))
        assert gpu.raw_tensor(actual) == tuple(expected)
        compared += len(words)
    negative_zero = SINGLE.tensor([0x80000000], torch)
    phase = gpu.CudaArithmetic(4096)
    assert gpu.raw_tensor(phase.positive_part(negative_zero)) == (0,)
    assert gpu.raw_tensor(phase.floor_grid(negative_zero, 149)) == (0,)
    assert gpu.raw_tensor(phase.ingress((F(-1, 1 << 150),))) == (0x80000000,)
    phase.check()
    return {'incomplete_clock_source_and_scalar_divisor_rejected': True,
            'actual_half_forward_overflow_retains_unchanged_predecessor': True,
            'finite_projection_cannot_hide_actual_optimizer_intermediate_overflow': True,
            'mutable_device_parameter_corruption_revalidated': True,
            'independent_exact_dyadic_grid_coordinate_checks': compared,
            'projection_and_floor_canonicalize_negative_zero': True,
            'host_RNE32_ingress_preserves_negative_underflow_zero': True}


def simplex_boundary_audit():
    from fp_reference.learner import SIMPLEX_GRADIENT
    from fp_reference.cuda_prefix import output_cells
    cases = (((F(0),F(1)),(F(10),F(0)),(0,1)),
             ((F(1,3),)*3,(F(1),F(2),F(3)),(0,1,2)),
             ((F(2),F(1,4),F(3),F(3,4)),(F(7),F(-1),F(-2),F(1)),(1,3)))
    checked = 0
    for theta,gradient,slots in cases:
        arith = gpu.CudaArithmetic(32768)
        actual = gpu.CudaLearnerState(arith.ingress(theta),(),arith.ingress(gradient),1,1,0)
        expected = ModelState(tuple(map(q,theta)),(),tuple(map(q,gradient)),1,1,0)
        spec = LearnerSpec(1,F(1,4),optimizer_id=SIMPLEX_GRADIENT,simplex_slots=slots)
        arith = gpu.CudaArithmetic(32768)
        before = arith.output_cells
        result = gpu.commit_event(actual,spec,arith)
        same_state(result,model_commit(expected,spec))
        graph = Program((Sum('mass',()),),len(theta),(0,0))
        assert arith.output_cells-before==output_cells('commit',graph,contract().semantics,spec)
        if not theta[slots[0]]:
            assert gpu.raw_tensor(result.theta)[slots[0]]==0
        checked += 1
    # A nonzero negative successor is refused before zero canonicalization.
    arith = gpu.CudaArithmetic(32768)
    state = gpu.CudaLearnerState(arith.ingress((F(9,10),F(1,10))),(),
        arith.ingress((F(0),F(5))),1,1,0)
    spec = LearnerSpec(1,F(1),optimizer_id=SIMPLEX_GRADIENT,simplex_slots=(0,1))
    arith = gpu.CudaArithmetic(32768)
    rejects(lambda:gpu.commit_event(state,spec,arith),ArithmeticUnresolved)
    return {'rounded_complete_successors':checked,'prepaid_output_extents_match':True,
            'zero_times_negative_factor_canonicalized_after_validation':True,'negative_nonzero_update_refused':True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', choices=('all', 'exhaustive', 'profile', 'topology', 'failures', 'simplex'), default='all')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write and args.section != 'all':
        parser.error('only the complete audit may replace canonical evidence')
    import torch
    result = {'status': 'PASS', 'scope': 'actual continuous CUDA learner mechanics beside owned Reference Runtime events; no device authority',
              'backend_id': gpu.BACKEND_ID, 'device': torch.cuda.get_device_name(0),
              'torch': torch.__version__, 'torch_CUDA_runtime': torch.version.cuda}
    for name, audit in (('exhaustive', exhaustive_audit), ('profile', profile_recurrence_audit),
                        ('topology', topology_audit), ('failures', failure_and_grid_audit), ('simplex', simplex_boundary_audit)):
        if args.section in ('all', name):
            result[name] = audit()
            print(name+' PASS', flush=True)
    result['not_closed'] = ['registered Runtime AMP contract and per-event bridge authority',
        'complete device/host workspace ownership and failure-atomic publication',
        'same-path AMP persistence, build/copy/install and model-science release',
        'all-input or future numerical error guarantees']
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_LEARNER_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
