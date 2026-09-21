"""Complete owned Runtime/CUDA prefix audit; target install remains held.

Fresh child processes give each real native allocator its declared history.
The expected learners come from the independent exact rounded interpreter;
only immutable Runtime snapshots supply observed values and provenance.
"""
from dataclasses import fields, is_dataclass, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from collections.abc import Mapping
import argparse
import json
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference import cuda_learner as gpu
from fp_reference.cuda_prefix import CudaPrefixContract, CudaRunManifest, widen, output_cells
from fp_reference.cuda_prefix import LEGACY_PHASE_ENCODING_ID, BINARY_PHASE_ENCODING_ID
from fp_reference.phase_encoding import decoded_fragments
from fp_reference.cuda_range import forward_operations
from fp_reference.cuda_storage import CudaStorageContract, CudaStorageUnresolved
from fp_reference.float64_bridge import Float64Contract
from fp_reference.machine import pack
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.profile import ProfileSpec
from fp_reference.native_search import GrammarLimits
from fp_reference.search import ReferenceSearchSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, Source, State, Sum, Term
from audit_cuda_learner import model_initial, model_predict, model_observe, model_commit, HALF, SINGLE
from audit_reference_construction import contract, domain, limits, rejects, validate_residency, zero_program
from audit_reference_events import online, shared_graph
from audit_reference_search import brute_grammar
from ingress_audit_support import deliver_context


def cuda_contract(**changes):
    size = 16 << 20
    return replace(CudaPrefixContract(CudaStorageContract(size, 2*size,
        {role: (size, 2*size) for role in ('deployment', 'compiler')}), F(1, 100), F(1, 100)), **changes)


def phase_payload(snapshot,frame):
    """Independent audit view of a complete frame's declared typed record."""
    size = int.from_bytes(frame[:8],'big')
    assert 0<size<=len(frame)-8
    kind = getattr(snapshot.cuda.contract,'evidence_encoding',LEGACY_PHASE_ENCODING_ID)
    if kind == LEGACY_PHASE_ENCODING_ID:
        return frame[8:8+size]
    assert kind == BINARY_PHASE_ENCODING_ID
    return b''.join(decoded_fragments(memoryview(frame)[8:8+size]))


def configuration():
    return replace(contract(pattern=(F(1, 3), F(1, 4), F(0))), reference_integer_bits=32768,
                   limits=limits(byte_cap=80_000_000, work_cap=100_000_000))


def raw_model(state):
    return (tuple(SINGLE.encode_exact(v) for v in state.theta),
            tuple((key, tuple(HALF.encode_exact(v) for v in row)) for key, row in state.delayed),
            tuple(SINGLE.encode_exact(v) for v in state.gradient), state.unit, state.cursor, state.steps)


def raw_model_prediction(prediction):
    result = []
    for key in ('values', 'theta_half', 'excesses', 'masses', 'normalizer', 'probabilities'):
        layout = HALF if key in ('values', 'theta_half', 'excesses') else SINGLE
        values = (prediction[key],) if key == 'normalizer' else prediction[key]
        result.append(tuple(layout.encode_exact(v) for v in values))
    result.append(tuple((key, tuple(HALF.encode_exact(v) for v in row)) for key, row in prediction['delayed']))
    return tuple(result)


def no_device_handles(value):
    if is_dataclass(value):
        for field in fields(value):
            no_device_handles(getattr(value, field.name))
    elif isinstance(value, Mapping):
        for key, item in value.items():
            no_device_handles(key)
            no_device_handles(item)
    elif isinstance(value, (tuple, list)):
        for item in value:
            no_device_handles(item)
    else:
        assert type(value).__module__ != 'torch', type(value)


def audit_snapshot(runtime):
    snapshot = validate_residency(runtime)
    no_device_handles(snapshot)
    assert type(snapshot.run.manifest) is CudaRunManifest
    assert snapshot.run.manifest.cuda == snapshot.cuda.contract
    graphs, observations = dict(snapshot.programs), {r.observation_id: r for r in snapshot.observations}
    buffers = dict(snapshot.buffers)
    expected, count = {}, 0
    for record in snapshot.cuda.phases:
        assert record.status == 'CHECKED_CUDA_PREFIX_PHASE', record
        graph, kind = graphs[record.program_id], record.phase.split(':')[1]
        before = None if record.input_phase is None else expected[record.input_phase]
        if kind == 'initialize':
            result = model_initial(graph, runtime.contract.semantics, record.reference.theta, record.reference.cursor)
        elif kind == 'attach':
            result = replace(before, cursor=record.reference.cursor)
        elif kind == 'predict':
            row = observations.get(record.observation_id)
            if row is None:
                row = snapshot.pending.record
            result = model_predict(graph, runtime.contract.semantics, before, dict(row.sources))
            assert record.raw_prediction == raw_model_prediction(result)
            assert record.raw_state == raw_model(before)
        elif kind == 'observe':
            result = model_observe(graph, before, expected[record.prediction_phase], observations[record.observation_id].target)
        else:
            assert kind == 'commit'
            result = model_commit(before, runtime.online_contract.learner)
        if kind != 'predict':
            assert record.raw_state == raw_model(result)
        assert record.forward_operations == (forward_operations(graph, runtime.contract.semantics) if kind == 'predict' else 0)
        expected[record.object_id] = result
        frame = buffers[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        assert size > 0 and phase_payload(snapshot,frame) == pack(record)
        assert len(frame) == snapshot.cuda.contract.phase_evidence_bytes
        assert not any(frame[8+size:])
        assert record.relation is not None
        assert record.output_cells <= snapshot.cuda.contract.phase_output_cells
        assert record.output_cells == output_cells(kind, graph, runtime.contract.semantics, runtime.online_contract.learner)
        assert record.arena_phase is not None
        count += 1
    current = dict(snapshot.cuda.current)
    assert set(current) == {state.candidate_id for state in snapshot.candidates}
    for state in snapshot.candidates:
        actual = expected[current[state.candidate_id]]
        assert (actual.unit, actual.cursor, actual.steps) == (state.learner.unit_count, state.learner.cursor, state.learner.optimizer_steps)
    storage = snapshot.cuda.storage
    arena_bytes = snapshot.cuda.contract.storage.arena_bytes
    assert storage['actual_tensor_arena_bytes'] == arena_bytes
    assert storage['native_allocation_counter_current'] == storage['native_allocation_counter_at_binding'] == (1, arena_bytes, 1)
    return {'phases': count, 'actual_arena_bytes': storage['actual_tensor_arena_bytes'],
            'largest_phase_frame_used': max(int.from_bytes(buffers[r.object_id][:8], 'big')+8 for r in snapshot.cuda.phases),
            'maximum_output_cells': max(r.output_cells for r in snapshot.cuda.phases)}


def stream_case(index, *, arena_bytes=16 << 20):
    sequence = tuple(product(tuple(product((0, 1), repeat=2)), repeat=3))[index]
    cfg = configuration()
    storage = CudaStorageContract(arena_bytes, 2*arena_bytes,
        {role: (arena_bytes, 2*arena_bytes) for role in ('deployment', 'compiler')})
    runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=online(cfg, 3, unit=2, rate=F(1, 8), grid=16), cuda=cuda_contract(storage=storage))
    candidate = runtime.construct_candidate(shared_graph())
    assert candidate.status == 'BUILT_REFERENCE'
    previous = runtime.snapshot()
    for cursor, (context, target) in enumerate(sequence):
        assert deliver_context(runtime, f'observation-{cursor}', domain(1)[context]).status == 'PREDICTED_REFERENCE'
        pending = runtime.snapshot()
        assert pending.cuda.current == previous.cuda.current
        assert pending.pending.record.target is None
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
        previous = runtime.snapshot()
    result = audit_snapshot(runtime)
    assert previous.cursor == 3 and all(s.learner.unit_count == 1 for s in previous.candidates)
    assert runtime.install(candidate.candidate_id, bridge=True).status == 'UNRESOLVED'
    assert runtime.install_cpu(candidate.candidate_id, proposal_proof_id='x', reference_identity='x', float64_identity='x').status == 'UNRESOLVED'
    runtime.retire_candidate(candidate.candidate_id)
    retired = runtime.snapshot()
    assert candidate.candidate_id not in dict(retired.cuda.current)
    assert retired.cuda.phases == previous.cuda.phases
    assert dict(retired.cuda.storage)['consumed_arena_extent'] == dict(previous.cuda.storage)['consumed_arena_extent']
    return result


def profile_case():
    cfg = replace(configuration(), initializer_pattern=(F(1, 8), F(1, 3), F(1, 4)))
    cfg = replace(cfg, semantics=replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(10)),)))
    graph = Program((State('h'), Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0), Term(1, 1))),
                     Product('mass', 3, 3), Sum('mass', (Term(4, 2),))), 3, (3, 5), (Binding('h', 3),))
    base = Program((Sum('mass', ()),), 0, (0, 0), (Binding('h', 0),))
    profile = ProfileSpec('old-data', ('observation-0', 'observation-1'), 3)
    run = replace(online(cfg, 6, unit=2, rate=F(1, 64), grid=16), profiles=(profile,),
                  float64=Float64Contract(F(1, 10**10), F(1, 10**10)))
    runtime = ReferenceCompilerRuntime(cfg, base, online=run, cuda=cuda_contract())
    for cursor, target in enumerate((0, 1, 1, 0, 0, 1)):
        if cursor == 2:
            built = runtime.construct_candidate(graph, profile_id=profile.profile_id)
            assert built.status == 'BUILT_REFERENCE', built
        assert deliver_context(runtime, f'observation-{cursor}', domain(1)[cursor % 2]).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(target).status == 'OBSERVED_REFERENCE'
    result = audit_snapshot(runtime)
    snapshot = runtime.snapshot()
    assert all(r.status == 'CHECKED_FLOAT64_PHASE' for r in snapshot.float64_traces)
    assert len(snapshot.float64_traces) == result['phases']
    candidate = next(s for s in snapshot.candidates if s.candidate_id == built.candidate_id)
    assert candidate.learner.optimizer_steps == 5 and len(candidate.delayed[0][1]) == 2
    result['CPU_binary64_phases'] = len(snapshot.float64_traces)
    result['ordinary_events'] = len(snapshot.observations)
    result['replayed_events'] = len(snapshot.profile_events)
    return result


def search_case(exhaustion=False):
    cfg = configuration()
    if exhaustion:
        cfg = replace(cfg, limits=limits(byte_cap=1_000_000, work_cap=100_000_000))
    bounds = GrammarLimits(2, 1, 0, 1, 0)
    search = ReferenceSearchSpec('native', bounds, ('observation-0', 'observation-1'))
    run = replace(online(cfg, 2, unit=2, rate=F(1, 8), grid=16), searches=(search,))
    runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=run, cuda=cuda_contract())
    for cursor in (0, 1):
        assert deliver_context(runtime, f'observation-{cursor}', domain(1)[cursor]).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(cursor).status == 'OBSERVED_REFERENCE'
    opened = runtime.start_reference_search('native')
    result = runtime.advance_reference_search(opened.search_id, transitions=10000)
    snapshot = runtime.snapshot()
    if exhaustion:
        assert result.status == 'UNRESOLVED', result
        assert not snapshot.reference_proofs
        assert any(row.status == 'UNRESOLVED' for row in snapshot.searches[0].rows)
        return {'actual_CUDA_evidence_budget_failure_leaves_native_search_unresolved': True,
                'no_reference_class_proof_issued': True, 'global_packed_cap': 1_000_000}
    assert result.status == 'REFERENCE_CLASS_EXHAUSTED', result
    independent = brute_grammar(cfg.semantics, bounds)
    assert len(independent) == 35
    assert {row.program for row in snapshot.searches[0].rows} == set(independent)
    assert all(row.status == 'COMPARED_REFERENCE' for row in snapshot.searches[0].rows)
    summary = audit_snapshot(runtime)
    summary['independent_complete_native_members'] = len(independent)
    summary['decision_class'] = 'fixed-state reference empirical CE over the registered initializer endpoints plus actual baseline'
    assert runtime.install(result.best_candidate_id, bridge=True).status == 'UNRESOLVED'
    return summary


def failure_case(case):
    cfg = configuration()
    cuda = cuda_contract(phase_output_cells=46) if case == 'output-cap' else (
        cuda_contract(phase_evidence_bytes=4800) if case == 'frame-cap' else cuda_contract())
    if case == 'zero-tolerance':
        cuda = cuda_contract(state_atol=F(0), probability_atol=F(0))
    if case == 'normalization':
        cfg = replace(cfg, semantics=replace(cfg.semantics, base=(F(1), F(1, 1 << 24))))
        cuda = cuda_contract(probability_atol=F(0))
    runtime = ReferenceCompilerRuntime(cfg, zero_program(2), online=online(cfg, 3, unit=2, rate=F(1, 8), grid=16), cuda=cuda)
    if case == 'malformed-backend':
        before = runtime.snapshot()
        with patch.object(gpu, 'initialize', return_value=object()):
            try:
                runtime.construct_candidate(shared_graph())
            except RuntimeError as error:
                assert isinstance(error.__cause__, ContractError)
            else:
                raise AssertionError('a malformed backend result became an admissibility rejection')
        snapshot = runtime.snapshot()
        assert snapshot.attempts[-1][1] == 'EXECUTION_FAILED'
        assert snapshot.candidates == before.candidates and snapshot.cuda.current == before.cuda.current
        return {'malformed_backend_and_failed_raw_capture_cannot_become_admissibility_rejection': True}
    if case == 'normalization':
        before = runtime.snapshot()
        assert deliver_context(runtime, 'observation-0', domain(1)[1]).status == 'UNRESOLVED'
        snapshot = runtime.snapshot()
        record = snapshot.cuda.phases[-1]
        assert record.status == 'UNRESOLVED' and record.raw_prediction[4] == (0x3f800000,)
        assert record.raw_prediction[3] == (0x3f800000, SINGLE.encode_exact(F(1, 1 << 24)))
        assert snapshot.cuda.current == before.cuda.current and not snapshot.observations
        assert snapshot.pending.record.target is None
        return {'actual_single_readout_refused_by_preregistered_zero_probability_tolerance': True,
                'rounded_normalizer_raw': 0x3f800000, 'target_not_revealed': True}
    built = runtime.construct_candidate(shared_graph())
    if case == 'zero-tolerance':
        assert built.status == 'UNRESOLVED' and built.candidate_id is None
        snapshot = runtime.snapshot()
        assert len(snapshot.candidates) == len(snapshot.cuda.current) == 1
        assert snapshot.cuda.phases[-1].status == 'UNRESOLVED'
        assert snapshot.cuda.phases[-1].raw_state[0][0] == SINGLE.rounded(F(1, 3))
        assert deliver_context(runtime, 'observation-0', domain(1)[1]).status == 'PREDICTED_REFERENCE'
        assert runtime.observe(1).status == 'OBSERVED_REFERENCE'
        return {'inexact_newborn_refused_without_reference_endpoint_fallback': True,
                'failed_device_state_retained_while_baseline_continues': True}
    assert built.status == 'BUILT_REFERENCE'
    if case == 'allocation-escape':
        before = runtime.snapshot()
        import torch
        foreign = torch.empty(1, device='cuda')
        del foreign
        rejects(lambda: runtime.begin_context('observation-0'), CudaStorageUnresolved)
        snapshot = runtime.snapshot()
        assert snapshot.halted and snapshot.cursor == 0 and not snapshot.observations
        assert snapshot.cuda.current == before.cuda.current
        assert snapshot.cuda.storage['status'] == 'UNRESOLVED'
        rejects(lambda: runtime.construct_candidate(shared_graph()))
        return {'entry_rejects_freed_foreign_allocation_without_advancing_ingress': True}
    if case == 'frame-cap':
        before = runtime.snapshot()
        assert deliver_context(runtime, 'observation-0', domain(1)[1]).status == 'UNRESOLVED'
        snapshot = runtime.snapshot()
        record = snapshot.cuda.phases[-1]
        assert record.status == 'UNRESOLVED' and 'evidence retention failed' in record.reason
        assert snapshot.cuda.current == before.cuda.current and not snapshot.observations
        assert snapshot.pending.record.target is None
        frame = dict(snapshot.buffers)[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        assert phase_payload(snapshot,frame) == pack((record.object_id, 'ADMITTED_CUDA_PHASE'))
        assert len(frame) == 4800 and snapshot.halted
        return {'actual_evidence_frame_cap_cannot_leave_an_unowned_checked_phase': True,
                'admitted_frame_and_actual_device_outputs_retained': True}
    assert deliver_context(runtime, 'observation-0', domain(1)[1]).status == 'PREDICTED_REFERENCE'
    before = runtime.snapshot()
    if case == 'prepaid-frame':
        original = runtime._ledger.allocate
        def denied(owner, objects):
            if any(o.kind == 'owned_cuda_phase_frame' for o in objects):
                raise ResourceExceeded('injected phase-frame admission refusal')
            return original(owner, objects)
        with patch.object(runtime._ledger, 'allocate', denied):
            result = runtime.observe(1)
        assert result.status == 'UNRESOLVED'
        assert runtime.snapshot().cuda.storage['consumed_arena_extent'] == before.cuda.storage['consumed_arena_extent']
    elif case in ('unexpected-backend', 'combined-failure'):
        original = gpu.observe_event
        injected = RuntimeError('actual executor fault injection' if case == 'unexpected-backend' else
                                'retained original executor failure '+('x'*cuda.phase_evidence_bytes))
        def fail(program, *args):
            if program.slot_count:
                raise injected
            return original(program, *args)
        with patch.object(gpu, 'observe_event', fail):
            try:
                runtime.observe(1)
            except RuntimeError as error:
                assert error is injected
            else:
                raise AssertionError('unexpected backend failure was downgraded')
        if case == 'combined-failure':
            record = runtime.snapshot().cuda.phases[-1]
            assert record.status == 'EXECUTION_FAILED' and 'evidence retention failed' in record.reason
    elif case == 'unexecuted-endpoint':
        def skipped(program, rules, state, spec, prediction, target, arithmetic):
            assert not program.slot_count
            return replace(state, delayed=prediction.delayed, unit_count=state.unit_count+1, cursor=state.cursor+1)
        with patch.object(gpu, 'observe_event', skipped):
            try:
                runtime.observe(1)
            except RuntimeError as error:
                assert 'registered output schedule' in str(error.__cause__)
            else:
                raise AssertionError('numerically correct but unexecuted device phase was accepted')
    else:
        assert case == 'output-cap'
        assert runtime.observe(1).status == 'UNRESOLVED'
    snapshot = runtime.snapshot()
    assert snapshot.halted and snapshot.cursor == 0 and snapshot.pending.record.target == 1
    assert snapshot.candidates == before.candidates and snapshot.cuda.current == before.cuda.current
    assert len(snapshot.observations) == 1 and snapshot.observations[0].target == 1
    if case != 'prepaid-frame':
        assert snapshot.cuda.phases[-1].status in ('UNRESOLVED', 'EXECUTION_FAILED')
        base = snapshot.deployed_id
        if case != 'unexecuted-endpoint':
            assert dict(snapshot.cuda.staged)[base] != dict(snapshot.cuda.current)[base]
        assert snapshot.cuda.storage['consumed_arena_extent'] > before.cuda.storage['consumed_arena_extent']
    rejects(lambda: runtime.observe(1))
    rejects(lambda: runtime.begin_context('observation-1'))
    return {'all_published_reference_and_CUDA_states_unchanged': True, 'revealed_target_and_executed_prefix_retained': True,
            'completed_CUDA_phases': len(snapshot.cuda.phases), 'case': case}


def execute_case(case, *, arena_bytes=16 << 20):
    if case.startswith('stream-'):
        index = int(case[7:])
        assert 0 <= index < 64
        return stream_case(index, arena_bytes=arena_bytes)
    if case == 'profile':
        return profile_case()
    if case in ('search', 'search-exhaustion'):
        return search_case(case == 'search-exhaustion')
    return failure_case(case)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--arena-mib', type=int)
    args = parser.parse_args()
    if args.case:
        if args.write:
            parser.error('a subcase cannot replace canonical evidence')
        if args.arena_mib is not None and (not args.case.startswith('stream-') or args.arena_mib <= 0):
            parser.error('an alternate arena belongs to one positive-size stream control')
        print(json.dumps(execute_case(args.case, arena_bytes=(16 if args.arena_mib is None else args.arena_mib) << 20)))
        return
    if args.arena_mib is not None:
        parser.error('an alternate arena requires an explicit stream subcase')
    widened = 0
    for word in range(65536):
        if word & 0x7c00 != 0x7c00:
            value = widen(word, 16)
            assert value.exact == HALF.decode(word) and value.negative == bool(word >> 15)
            widened += 1
    single_boundaries = (0, 1, 0x007fffff, 0x00800000, 0x3f800000, 0x7f7fffff,
                        0x80000000, 0x80000001, 0x807fffff, 0x80800000, 0xbf800000, 0xff7fffff)
    for word in single_boundaries:
        value = widen(word, 32)
        assert value.exact == SINGLE.decode(word) and value.negative == bool(word >> 31)
    results = []
    for index in range(64):
        process = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--case', 'stream-'+str(index)],
                                 capture_output=True, text=True, timeout=60)
        if process.returncode:
            raise RuntimeError(process.stdout+process.stderr)
        results.append(json.loads(process.stdout))
        if (index+1) % 8 == 0:
            print(str(index+1)+' complete Runtime streams PASS', flush=True)
    report = {'status': 'PASS', 'scope': 'owned actual CUDA prefix and per-phase relations; no target persistence/install/release',
              'complete_binary_three_event_streams': 64, 'ordinary_events': 192,
              'independently_replayed_stream_CUDA_phases': sum(r['phases'] for r in results),
              'actual_arena_bytes_per_registered_root': 16 << 20,
              'largest_stream_phase_frame_used': max(r['largest_phase_frame_used'] for r in results),
              'maximum_stream_output_cells': max(r['maximum_output_cells'] for r in results),
              'all_finite_half_exact_widenings_including_zero_sign': widened,
              'signed_single_boundary_widenings': len(single_boundaries),
              'all_checked_phase_frames_match_owned_raw_records': True,
              'public_snapshots_contain_no_device_handles': True}
    for case in ('profile', 'search', 'search-exhaustion', 'output-cap', 'prepaid-frame', 'frame-cap', 'unexpected-backend',
                 'combined-failure', 'malformed-backend', 'unexecuted-endpoint', 'allocation-escape', 'zero-tolerance', 'normalization'):
        process = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--case', case], capture_output=True, text=True, timeout=60)
        if process.returncode:
            raise RuntimeError(process.stdout+process.stderr)
        report[case] = json.loads(process.stdout)
        print(case+' PASS', flush=True)
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_RUNTIME_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
