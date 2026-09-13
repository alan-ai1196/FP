"""Actual owned binary64 learner prefixes, checked against an independent CPU path.

The oracle uses Python float operations directly, not Float64Arithmetic or
rounded exact learner endpoints. These CPU execution audits grant no target
AMP, population-improvement or installation authority.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import math
import struct
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from ingress_audit_support import deliver_context
from fp_reference import ReferenceCompilerRuntime
from fp_reference.binary_arithmetic import Float64Value
from fp_reference.core import ContractError
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.float64_bridge import Float64Contract, check_state
from fp_reference.machine import pack
from fp_reference.persistence import PersistenceContract, PersistenceRule
from fp_reference.profile import ProfileSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, Source, State, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.float64_learner as finite
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import online, shared_graph


def bits(value):
    return int.from_bytes(struct.pack('>d', value), 'big')


@dataclass(frozen=True)
class CPUState:
    theta: tuple
    delayed: tuple
    gradient: tuple
    unit: int
    cursor: int
    steps: int


def cpu_initial(graph, rules, pattern, cursor):
    return CPUState(tuple(float(pattern[i % len(pattern)]) for i in range(graph.slot_count)),
                    tuple((s.state_id, (0.0,)*s.delay) for s in rules.states),
                    (0.0,)*graph.slot_count, 0, cursor, 0)


def cpu_predict(graph, rules, state, sources):
    """Independent direct scalar program interpreter with explicit edge tape."""
    available = {key: float(value) for key, value in sources.items()}
    history = dict(state.delayed)
    values, incoming = [], []
    for node in graph.nodes:
        if isinstance(node, Source):
            value, edges = available[node.source_id], ()
        elif isinstance(node, State):
            value, edges = history[node.state_id][0], ()
        elif isinstance(node, Product):
            value = values[node.left]*values[node.right]
            edges = ((node.left, values[node.right], None), (node.right, values[node.left], None))
        else:
            value, edge_list = 0.0, []
            for edge in node.terms:
                weighted = state.theta[edge.slot]*values[edge.parent]
                value = value+weighted
                edge_list.append((edge.parent, state.theta[edge.slot], (edge.slot, values[edge.parent])))
            edges = tuple(edge_list)
        values.append(value)
        incoming.append(edges)
    excesses = tuple(values[h] for h in graph.heads)
    masses = tuple(float(b)+v for b, v in zip(rules.base, excesses))
    total = 0.0
    for value in masses:
        total = total+value
    prediction = tuple(value/total for value in masses)
    body = {b.state_id: values[b.body] for b in graph.bindings}
    delayed = tuple((s.state_id, history[s.state_id][1:]+(body[s.state_id],)) for s in rules.states)
    return {'values': tuple(values), 'excesses': excesses, 'masses': masses,
            'normalizer': total, 'probabilities': prediction, 'delayed': delayed,
            'incoming': tuple(incoming)}


def cpu_observe(graph, state, prediction, target):
    inverse_total = 1.0/prediction['normalizer']
    inverse_target = 1.0/prediction['masses'][target]
    target_seed = inverse_total+(-inverse_target)
    adjoint = [0.0]*len(graph.nodes)
    slots = [0.0]*graph.slot_count
    for label, head in enumerate(graph.heads):
        adjoint[head] = adjoint[head]+(target_seed if label == target else inverse_total)
    for index in reversed(range(len(graph.nodes))):
        seed = adjoint[index]
        for parent, weight, parameter in prediction['incoming'][index]:
            if parameter is not None:
                slot, value = parameter
                slots[slot] = slots[slot]+seed*value
            adjoint[parent] = adjoint[parent]+seed*weight
    accumulated = tuple(a+b for a, b in zip(state.gradient, slots))
    return replace(state, delayed=prediction['delayed'], gradient=accumulated,
                   unit=state.unit+1, cursor=state.cursor+1)


def cpu_commit(state, spec):
    assert state.unit == spec.update_unit and state.cursor % spec.update_unit == 0
    scale = float(spec.learning_rate)/float(spec.update_unit)
    values = []
    for value, gradient in zip(state.theta, state.gradient):
        delta = scale*gradient
        updated = max(0.0, value+(-delta))
        if spec.commit_grid_bits is not None:
            updated = math.ldexp(math.floor(math.ldexp(updated, spec.commit_grid_bits)), -spec.commit_grid_bits)
        values.append(updated)
    return replace(state, theta=tuple(values), gradient=(0.0,)*len(values), unit=0, steps=state.steps+1)


def same_values(actual, expected):
    assert tuple(value.bits for value in actual) == tuple(bits(value) for value in expected)


def same_state(actual, expected):
    assert actual is not None
    same_values(actual.theta, expected.theta)
    same_values(actual.gradient_sum, expected.gradient)
    assert (actual.unit_count, actual.cursor, actual.optimizer_steps) == (expected.unit, expected.cursor, expected.steps)
    assert tuple(key for key, _ in actual.delayed) == tuple(key for key, _ in expected.delayed)
    for (_, a), (_, b) in zip(actual.delayed, expected.delayed):
        same_values(a, b)


def same_prediction(actual, expected):
    for key in ('values', 'excesses', 'masses', 'probabilities'):
        same_values(getattr(actual, key), expected[key])
    assert actual.normalizer.bits == bits(expected['normalizer'])
    for (_, a), (_, b) in zip(actual.delayed, expected['delayed']):
        same_values(a, b)


def fixture(*, cfg=None, count=4, graph=None, state_atol=F(1, 1 << 24),
            probability_atol=F(1, 1 << 24), unit=2, rate=F(1, 8), grid=None,
            profiles=(), persistence=None):
    cfg = replace(contract(pattern=(F(1, 3), F(1, 4), F(0))), reference_integer_bits=32768,
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000)) if cfg is None else cfg
    run = replace(online(cfg, count, unit=unit, rate=rate, grid=grid),
                  float64=Float64Contract(state_atol, probability_atol), profiles=profiles,
                  persistence=persistence)
    if persistence is not None:
        run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external branch-invariant audit law assumption')))
    rt = ReferenceCompilerRuntime(cfg, zero_program(len(cfg.semantics.base)), online=run)
    candidate = rt.construct_candidate(shared_graph() if graph is None else graph)
    assert candidate.status == 'BUILT_REFERENCE', candidate
    return rt, candidate.candidate_id


def ingest(rt, sequence):
    for row, target in sequence:
        cursor = rt.snapshot().cursor
        prediction = deliver_context(rt, f'observation-{cursor}', row)
        assert prediction.status == 'PREDICTED_REFERENCE', prediction
        observed = rt.observe(target)
        assert observed.status == 'OBSERVED_REFERENCE', observed


def owned(rt):
    snapshot = validate_residency(rt)
    buffers = dict(snapshot.buffers)
    for state in snapshot.candidates:
        assert buffers[state.object_ids[1]] == pack((state.learner, state.float64))
    for index, trace in enumerate(snapshot.float64_traces):
        object_id = f'{trace.candidate_id}:float64:{trace.phase}:{index}'
        assert buffers[object_id] == pack(trace)
        assert trace.program_id in dict(snapshot.retained_programs)
    return snapshot


def replay(rt):
    snapshot = owned(rt)
    programs = dict(snapshot.programs)
    observations = {value.observation_id: value for value in snapshot.observations}
    states, predictions, ordinary_starts = {}, {}, {}
    compared = recast_differences = profile_recast_differences = 0
    for trace in snapshot.float64_traces:
        assert trace.status == 'CHECKED_FLOAT64_PHASE' and trace.relation is not None
        graph = programs[trace.program_id]
        origin, phase = trace.phase.split(':')
        key = trace.candidate_id
        if phase == 'initialize':
            states[key] = cpu_initial(graph, rt.contract.semantics, rt.contract.initializer_pattern, trace.ordinary_cursor)
        elif phase == 'attach':
            states[key] = replace(states[key], cursor=trace.reference.cursor)
        elif phase == 'predict':
            record = observations[trace.observation_id]
            prediction = cpu_predict(graph, rt.contract.semantics, states[key], dict(record.sources))
            predictions[key] = prediction
            same_prediction(trace.float64_prediction, prediction)
            if origin == 'ordinary':
                ordinary_starts[key, trace.observation_id] = (states[key], trace.reference)
        elif phase == 'observe':
            states[key] = cpu_observe(graph, states[key], predictions[key], observations[trace.observation_id].target)
        elif phase == 'commit':
            states[key] = cpu_commit(states[key], rt.online_contract.learner)
        else:
            raise AssertionError(trace.phase)
        same_state(trace.float64, states[key])
        for field in ('theta', 'gradient_sum'):
            different = sum(value.bits != bits(float(ref)) for value, ref in zip(getattr(trace.float64, field), getattr(trace.reference, field)))
            recast_differences += different
            if origin == 'profile':
                profile_recast_differences += different
        assert trace.max_local_round_error >= 0
        compared += 1
    unpublished = (snapshot.halted is not None and snapshot.halted[0] == 'observe'
                   and snapshot.pending is not None and snapshot.pending.stage == 'observation-failed')
    if unpublished:
        # Every executed successor above is still replayed. A failed joint
        # observation publishes none of them: the complete root retains the
        # exact pre-target learners as well as the paid unpublished phases.
        record = snapshot.pending.record
        assert record.cursor == snapshot.cursor and observations[record.observation_id] == record
        for candidate in snapshot.candidates:
            expected, reference = ordinary_starts[candidate.candidate_id, record.observation_id]
            assert candidate.learner == reference
            same_state(candidate.float64, expected)
    else:
        for candidate in snapshot.candidates:
            same_state(candidate.float64, states[candidate.candidate_id])
    return compared, recast_differences, profile_recast_differences


def exhaustive_audit():
    phases = divergences = events = commits = 0
    for sequence in product(tuple(product((0, 1), repeat=2)), repeat=3):
        rt, _ = fixture(count=3)
        ingest(rt, tuple((domain(1)[context], target) for context, target in sequence))
        count, different, _ = replay(rt)
        phases += count
        divergences += different
        events += len(sequence)*2
        commits += sum(t.phase == 'ordinary:commit' for t in rt.snapshot().float64_traces)
    assert divergences > 0
    grid_phases = 0
    for sequence in product(tuple(product((0, 1), repeat=2)), repeat=2):
        rt, _ = fixture(count=2, grid=24)
        ingest(rt, tuple((domain(1)[context], target) for context, target in sequence))
        grid_phases += replay(rt)[0]
    return {'complete_three_event_context_target_streams': 64,
            'paired_lineage_events': events, 'optimizer_commits': commits,
            'independent_bitwise_phase_checks': phases,
            'actual_finite_coordinates_differing_from_recast_exact_endpoints': divergences,
            'registered_floor_grid_two_event_streams': 16,
            'registered_floor_grid_bitwise_phase_checks': grid_phases}


def profile_and_recurrence_audit():
    profile = ProfileSpec('old-data', ('observation-0', 'observation-1'), 3)
    rt, _ = fixture(count=4, profiles=(profile,))
    ingest(rt, ((domain(1)[0], 0), (domain(1)[1], 1)))
    result = rt.construct_candidate(shared_graph(), profile_id=profile.profile_id)
    assert result.status == 'BUILT_REFERENCE', result
    count, differences, profile_differences = replay(rt)
    assert profile_differences > 0 and rt.snapshot().cursor == 2
    target = next(c for c in rt.snapshot().candidates if c.candidate_id == result.candidate_id)
    assert target.learner.cursor == target.float64.cursor == 2
    assert target.learner.optimizer_steps == target.float64.optimizer_steps == 3
    assert len([t for t in rt.snapshot().float64_traces if t.candidate_id == target.candidate_id and t.phase == 'profile:predict']) == 6

    cfg = replace(contract(pattern=(F(1, 8), F(1, 3), F(1, 4))), reference_integer_bits=32768,
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    cfg = replace(cfg, semantics=replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(10)),)))
    graph = Program((State('h'), Source('x0_0'), Source('x0_1'),
                     Sum('mass', (Term(0, 0), Term(1, 1))), Product('mass', 3, 3),
                     Sum('mass', (Term(4, 2),))), 3, (3, 5), (Binding('h', 3),))
    # The deployed zero graph still has to bind every declared delayed state.
    initial = Program((Sum('mass', ()),), 0, (0, 0), (Binding('h', 0),))
    run = replace(online(cfg, 4, unit=2, rate=F(1, 64), grid=None),
                  float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)))
    recurrence = ReferenceCompilerRuntime(cfg, initial, online=run)
    built = recurrence.construct_candidate(graph)
    assert built.status == 'BUILT_REFERENCE', built
    ingest(recurrence, tuple((domain(1)[i % 2], target) for i, target in enumerate((0, 1, 1, 0))))
    recurrent_phases, _, _ = replay(recurrence)
    state = next(c for c in recurrence.snapshot().candidates if c.candidate_id == built.candidate_id)
    tolerance = recurrence.online_contract.float64
    one = Float64Value(bits(1.0))
    bad_gradient = replace(state.float64, gradient_sum=(one,)+state.float64.gradient_sum[1:])
    rejects(lambda: check_state(state.learner, bad_gradient, tolerance, bit_limit=32768), ArithmeticUnresolved)
    history = state.float64.delayed[0][1]
    bad_tail = replace(state.float64, delayed=(('h', (history[0], one)),))
    rejects(lambda: check_state(state.learner, bad_tail, tolerance, bit_limit=32768), ArithmeticUnresolved)
    # A zero sign is kept in state identity, even when an error relation is zero.
    empty = next(c for c in recurrence.snapshot().candidates if c.candidate_id == recurrence.snapshot().deployed_id)
    signed = replace(empty.float64, delayed=(('h', (Float64Value(1 << 63), Float64Value(0))),))
    assert check_state(empty.learner, signed, Float64Contract(F(0), F(0)), bit_limit=32768).state_error == 0
    assert signed != empty.float64 and pack(signed) != pack(empty.float64)
    return {'profile_replayed_events': 6, 'original_profile_observations': 2, 'ordinary_cursor_after_profile': 2,
            'profile_and_initial_prefix_phase_checks': count,
            'profile_coordinates_not_equal_to_exact_endpoint_recasts': profile_differences,
            'recurrent_phase_checks': recurrent_phases,
            'full_accumulator_and_hidden_delayed_tail_checked': True,
            'numeric_zero_relation_does_not_erase_raw_sign_bit': True}


def normalization_audit():
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    cfg = replace(contract(cap=F(8, 3), peak=1, pattern=(F(2, 3),)),
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000), reference_integer_bits=32768)
    rt, candidate = fixture(cfg=cfg, graph=graph, count=2)
    ingest(rt, ((domain(1)[0], 0),))
    trace = next(t for t in rt.snapshot().float64_traces if t.candidate_id == candidate and t.phase == 'ordinary:predict')
    raw = tuple(value.exact for value in trace.float64_prediction.probabilities)
    mass = tuple(value.exact for value in trace.float64_prediction.masses)
    mathematical = tuple(value/sum(mass) for value in mass)
    assert raw == trace.reference_prediction.probabilities == (F(5, 8), F(3, 8))
    assert mathematical != raw and trace.relation.division_error > 0
    replay(rt)
    strict, candidate = fixture(cfg=cfg, graph=graph, count=2, probability_atol=F(0))
    before = strict.snapshot()
    result = deliver_context(strict, 'observation-0', domain(1)[0])
    assert result.status == 'UNRESOLVED' and strict.snapshot().halted
    assert strict.snapshot().candidates == before.candidates and strict.snapshot().cursor == 0
    failed = strict.snapshot().float64_traces[-1]
    assert failed.status == 'UNRESOLVED' and failed.float64_prediction is not None
    assert tuple(v.exact for v in failed.float64_prediction.probabilities) == failed.reference_prediction.probabilities
    return {'displayed_prediction_exactly_equals_reference': True,
            'stored_mass_normalization_gap': str(trace.relation.division_error),
            'zero_probability_tolerance_rejects_displayed_equality': True}


def failure_audit():
    # Exact dyadic initial state passes; rounded reciprocal derivatives fail
    # zero state tolerance only after the target is irrevocably revealed.
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    cfg = replace(contract(cap=3, peak=1, pattern=(F(1),)),
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000), reference_integer_bits=32768)
    rt, _ = fixture(cfg=cfg, graph=graph, state_atol=F(0))
    before = rt.snapshot()
    assert deliver_context(rt, 'observation-0', domain(1)[0]).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'UNRESOLVED'
    assert rt.snapshot().halted and rt.snapshot().observations[0].target == 0
    assert rt.snapshot().candidates == before.candidates
    assert rt.snapshot().float64_traces[-1].phase == 'ordinary:observe'
    rejects(lambda: deliver_context(rt, 'observation-0', domain(1)[0]))

    # A genuine binary64 oracle integer cap is reached while casting an unused
    # declared source; the exact zero program itself predicts without it.
    tiny_cfg = replace(contract(source_domain=False), reference_integer_bits=1200,
                       limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    run = replace(online(tiny_cfg, 2, unit=2), float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)))
    tiny = ReferenceCompilerRuntime(tiny_cfg, zero_program(2), online=run)
    result = deliver_context(tiny, 'observation-0', (F(1, 1 << 600), F(0)))
    assert result.status == 'UNRESOLVED' and tiny.snapshot().halted
    assert tiny.snapshot().float64_traces[-1].phase == 'ordinary:predict'
    assert 'integer' in tiny.snapshot().float64_traces[-1].reason

    # Calibrate the registered count, then actually exhaust it on the finite
    # candidate observation after both predictions have completed.
    probe, candidate = fixture()
    deliver_context(probe, 'observation-0', domain(1)[0])
    work = probe.snapshot().resources['spent']['compiler']['work']+probe._machine.observation_work(shared_graph())+4
    small_cfg = replace(probe.contract, limits=limits(byte_cap=80_000_000, work_cap=work))
    small, _ = fixture(cfg=small_cfg)
    before = small.snapshot()
    assert deliver_context(small, 'observation-0', domain(1)[0]).status == 'PREDICTED_REFERENCE'
    assert small.observe(0).status == 'UNRESOLVED'
    assert small.snapshot().halted and small.snapshot().candidates == before.candidates
    assert small.snapshot().observations[0].target == 0

    # The cap changes the manifest's own size. Each calibration is a new
    # immutable root; stop only when that same cap misses the actual first
    # finite-observe evidence allocation by one byte.
    cap = 80_000_000
    for _ in range(16):
        probe, _ = fixture()
        constrained_cfg = replace(probe.contract, limits=limits(byte_cap=cap, work_cap=100_000_000))
        constrained, _ = fixture(cfg=constrained_cfg)
        before = constrained.snapshot()
        assert deliver_context(constrained, 'observation-0', domain(1)[0]).status == 'PREDICTED_REFERENCE'
        allocations = []
        original_allocate = constrained._allocate
        def measure(owner, objects):
            if any(value.spec.kind == 'executed_float64_phase' for value in objects):
                allocations.append(constrained.snapshot().resources['current']['reference_payload_bytes']+sum(value.spec.residency['reference_payload_bytes'] for value in objects))
            return original_allocate(owner, objects)
        with patch.object(constrained, '_allocate', measure):
            result = constrained.observe(0)
        assert allocations
        boundary = allocations[0]-1
        if cap == boundary:
            break
        cap = boundary
    else:
        raise AssertionError('immutable observe-evidence boundary did not stabilize')
    assert result.status == 'UNRESOLVED'
    assert constrained.snapshot().halted and constrained.snapshot().candidates == before.candidates
    assert constrained.snapshot().observations[0].target == 0
    assert constrained.snapshot().float64_traces[-1].status == 'UNRESOLVED'
    assert constrained.snapshot().float64_traces[-1].phase == 'ordinary:observe'
    assert constrained.snapshot().float64_traces[-1].candidate_id == before.deployed_id
    assert 'phase evidence retention failed' in constrained.snapshot().float64_traces[-1].reason
    validate_residency(constrained)

    # An unexpected finite backend exception is retained, then propagated;
    # the exact successor is never published without its numerical peer.
    broken, _ = fixture()
    before = broken.snapshot()
    deliver_context(broken, 'observation-0', domain(1)[0])
    with patch.object(finite, 'observe_event', side_effect=RuntimeError('injected finite backend failure')):
        rejects(lambda: broken.observe(0), RuntimeError)
    assert broken.snapshot().halted and broken.snapshot().candidates == before.candidates
    assert broken.snapshot().observations[0].target == 0
    assert broken.snapshot().float64_traces[-1].status == 'EXECUTION_FAILED'
    validate_residency(broken)

    # An internal registered-backend ContractError is an implementation failure,
    # not a proof that this valid native program was inadmissible.
    broken, _ = fixture()
    with patch.object(finite, 'initialize', side_effect=ContractError('registered executor invariant violation')):
        rejects(lambda: broken.construct_candidate(zero_program(2)), RuntimeError)
    assert broken.snapshot().attempts[-1][1] == 'EXECUTION_FAILED'
    assert broken.snapshot().float64_traces[-1].status == 'EXECUTION_FAILED'
    validate_residency(broken)

    # Numerically acceptable endpoint data cannot stand in for the registered
    # operation schedule. Even the zero deployed learner must execute its phase.
    skipped, _ = fixture(state_atol=F(1), probability_atol=F(1))
    deliver_context(skipped, 'observation-0', domain(1)[0])
    def skip_observe(program, state, spec, prediction, target, arith):
        return replace(state, cursor=state.cursor+1, unit_count=state.unit_count+1,
                       delayed=prediction.delayed)
    with patch.object(finite, 'observe_event', side_effect=skip_observe):
        rejects(lambda: skipped.observe(0), RuntimeError)
    assert skipped.snapshot().float64_traces[-1].status == 'EXECUTION_FAILED'
    assert skipped.snapshot().float64_traces[-1].scalar_operations == 0
    assert skipped.snapshot().halted

    # A successfully computed phase still needs an owned evidence allocation.
    # Fail that allocation during a valid newborn construction with a real cap.
    generous = replace(contract(), reference_integer_bits=32768,
                       limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    run = replace(online(generous, 2, unit=2), float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)))
    def constructor_boundary(*, before_phase=False):
        byte_cap = 80_000_000
        for _ in range(16):
            cfg = replace(generous, limits=limits(byte_cap=byte_cap, work_cap=100_000_000))
            runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
            boundaries = []
            allocate = runtime._allocate
            def measure_constructor(owner, objects):
                if any(value.spec.kind == 'executed_float64_phase' for value in objects):
                    current = runtime.snapshot().resources['current']['reference_payload_bytes']
                    boundaries.append(current if before_phase else current+sum(value.spec.residency['reference_payload_bytes'] for value in objects)-1)
                return allocate(owner, objects)
            with patch.object(runtime, '_allocate', measure_constructor):
                result = runtime.construct_candidate(zero_program(2))
            assert boundaries
            if byte_cap == boundaries[0]:
                return cfg, runtime, result, byte_cap
            byte_cap = boundaries[0]
        raise AssertionError('immutable construction-evidence boundary did not stabilize')
    tight_cfg, retained, failed, constructor_cap = constructor_boundary()
    assert failed.status == 'UNRESOLVED'
    snapshot = validate_residency(retained)
    assert snapshot.float64_traces[-1].status == 'UNRESOLVED'
    assert 'phase evidence retention failed' in snapshot.float64_traces[-1].reason
    for index, trace in enumerate(snapshot.float64_traces):
        if trace.status == 'CHECKED_FLOAT64_PHASE':
            assert dict(snapshot.buffers)[f'{trace.candidate_id}:float64:{trace.phase}:{index}'] == pack(trace)

    # A second, expected allocation failure cannot hide an earlier unexpected
    # backend failure or relabel that execution bug as mere budget exhaustion.
    combined_cfg, _, _, pre_phase_cap = constructor_boundary(before_phase=True)
    combined = ReferenceCompilerRuntime(combined_cfg, zero_program(2), online=run)
    before = combined.snapshot()
    original_failure = 'injected finite initializer failure before evidence retention'
    with patch.object(finite, 'initialize', side_effect=RuntimeError(original_failure)):
        rejects(lambda: combined.construct_candidate(zero_program(2)), RuntimeError)
    snapshot = validate_residency(combined)
    assert snapshot.candidates == before.candidates and snapshot.event_phase == 'idle'
    assert snapshot.attempts[-1][1] == 'EXECUTION_FAILED'
    assert snapshot.float64_traces[-1].status == 'EXECUTION_FAILED'
    assert original_failure in snapshot.float64_traces[-1].reason
    assert 'ResourceExceeded' in snapshot.float64_traces[-1].reason
    assert 'phase evidence retention failed' in snapshot.float64_traces[-1].reason
    assert snapshot.resources['peak']['reference_payload_bytes'] <= pre_phase_cap
    return {'actual_state_tolerance_failure_retains_revealed_target': True,
            'actual_binary64_integer_work_limit_stops_prediction': True,
            'real_work_and_coexistence_caps_halt_paired_prefix': True,
            'unexpected_finite_backend_failure_cannot_publish_exact_only_successor': True,
            'internal_backend_contract_failure_not_mislabeled_admissibility': True,
            'valid_looking_endpoint_without_registered_operations_rejected': True,
            'combined_backend_and_evidence_allocation_failure_preserves_both_causes': True,
            'failed_evidence_allocation_cannot_leave_unowned_checked_phase': True,
            'same_manifest_observe_evidence_cap': cap,
            'same_manifest_constructor_evidence_cap': constructor_cap,
            'same_manifest_before_constructor_evidence_cap': pre_phase_cap}


def crossing_audit():
    registration = PersistenceContract(F(1, 2),
        (PersistenceRule('future', 1, 10, F(1, 4), F(3, 4), F(3, 4), 12, 16),))
    graph = Program((Source('x0_0'), Source('x0_1')), 0, (0, 1))
    cfg = replace(contract(cap=3, peak=1), reference_integer_bits=32768,
                  limits=limits(byte_cap=80_000_000, work_cap=100_000_000))
    rt, candidate = fixture(cfg=cfg, graph=graph, count=14, persistence=registration)
    admitted = rt.admit_reference_persistence(candidate, 'future')
    assert admitted.identity_id is not None
    for _ in range(6):
        ingest(rt, ((domain(1)[0], 0),))
    result = rt.reference_persistence_result(admitted.identity_id)
    assert result.status == 'REFERENCE_CROSSED'
    cursor = rt.snapshot().cursor
    assert deliver_context(rt, f'observation-{cursor}', domain(1)[0]).status == 'PREDICTED_REFERENCE'
    with patch.object(finite, 'observe_event', side_effect=ArithmeticUnresolved('finite continuation loses its numerical relation')):
        assert rt.observe(0).status == 'UNRESOLVED'
    stopped = rt.reference_persistence_result(admitted.identity_id)
    assert stopped.status == 'UNRESOLVED' and stopped.alpha_spent == F(1, 4)
    assert stopped.crossing_cursor == result.crossing_cursor
    assert rt.install(candidate, bridge=True, persistence=True).status == 'UNRESOLVED'
    return {'finite_trajectory_failure_revokes_current_reference_crossing': True,
            'historical_crossing_and_spent_alpha_retained': True,
            'checked_cpu_prefix_has_no_AMP_or_install_authority': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', choices=('all', 'exhaustive', 'profiles', 'normalization', 'failures', 'crossing'), default='all')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checks = {'exhaustive': exhaustive_audit, 'profiles': profile_and_recurrence_audit,
              'normalization': normalization_audit, 'failures': failure_audit, 'crossing': crossing_audit}
    result = {'status': 'PASS', 'scope': 'owned actual CPU binary64 and exact reference learner prefixes; no target AMP authorization'}
    for key, check in checks.items():
        if args.section in ('all', key):
            result[key] = check()
    result['not_closed'] = ['target AMP or CUDA realization', 'paired reference/AMP persistence and atomic installation',
                            'full ERC-1 physical accounting and complete Runtime release']
    if args.write:
        if args.section != 'all':
            parser.error('only the complete audit may replace canonical evidence')
        (ROOT/'evidence/minimal/FP_FLOAT64_RUNTIME_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
