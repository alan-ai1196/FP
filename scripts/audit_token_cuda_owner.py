"""Closed CPU controls for token CUDA owner transitions; fresh worker below.

CPU mode grants no device or Runtime bridge authority. It checks the exact
phase graph, full retained data and the native predicates used by that owner.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from audit_native_tokens import fixture
from audit_owned_token_learner import registration
from audit_token_amp_schedule import ExactPrimitives
from fp_reference.cuda_prefix import TokenCudaPrefixContract
from fp_reference.cuda_storage import CudaStorageContract
from fp_reference.token_cuda_prefix import transition, fresh_origin, check_state, check_prediction
from fp_reference.token_cuda_state import Resident, StateWords
from fp_reference.token_array_events import Kernel
from fp_reference import token_amp as amp
from fp_reference.token_array_check import CheckedPrimitives
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_execution import TokenReferenceMachine
from fp_reference.token_sources import TokenValues, TokenContext
from fp_reference.core import ContractError
from fp_reference.encoding import packed_size

HOST_CAP, ARENA, CELLS, FRAME, DEADLINE = 4 << 30, 32 << 20, 4096, 1 << 20, 180000


def cuda_contract(pattern, *, state_atol=F(1, 4)):
    return TokenCudaPrefixContract(CudaStorageContract(ARENA, ARENA,
        {r: (ARENA, ARENA) for r in ('deployment', 'compiler')}), state_atol, F(1, 10000),
        phase_output_cells=CELLS, phase_evidence_bytes=FRAME, initializer=pattern, exact_cell_cap=4096)


def cpu():
    oracle = ExactPrimitives()
    counts = dict(histories=0, events=0, commits=0, profiles=0, checked_phases=0, arrays=0)
    maximum_phase_cells = {}
    label_words = 0
    largest = F(0)
    for unit, kind, word in product((1, 2, 4), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, exact = fixture(unit, kind)
        cc, p, o = registration(d, exact)
        cfg, m = cuda_contract(cc.initializer_pattern), TokenReferenceMachine(cc.initializer_pattern)
        native = m.initial_state(p, cc.semantics, m.initializer(p.slot_count, cc.initializer_pattern),
                                 0, spec=o.learner, bit_limit=32768)
        def phase(kind, before=None, prediction=None, window=None, target=None, birth=None):
            checker = CheckedPrimitives(cfg.exact_cell_cap)
            def audit(*args):
                checker(*args)
                oracle(*args)
            a = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=CELLS, audit=audit)
            result = transition(kind, p, cfg, before, prediction, window, target, native.cursor, birth, a)
            a.check()
            counts['checked_phases'] += 1
            counts['arrays'] += len(a.records)
            maximum_phase_cells[kind] = max(maximum_phase_cells.get(kind, 0), a.cells)
            return result
        physical = phase('initialize', birth=fresh_origin(p, cfg, 0, o.learner, cc.semantics, 32768))
        for target in word:
            context = TokenValues(TokenContext(cfg.initializer.sources, native.source.position, native.source.past))
            npred = m.predict(p, cc.semantics, native, context, bit_limit=32768)
            pred = phase('predict', physical, window=npred.window)
            # Bind the separately paid label method to the same complete
            # positive recipe as target observation, including unseen labels.
            audit = CheckedPrimitives(cfg.exact_cell_cap)
            labels = CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=CELLS, audit=audit)
            old_kernel = amp.Kernel(d, amp.Arithmetic(), element_cap=cfg.initializer.element_cap)
            old_pred = old_kernel.predict(physical.origin, npred.window)
            _, expected_mass, expected_division = old_kernel.mass_block(old_pred, 0, d.output.labels)
            for y in range(d.output.labels):
                mass, division = Kernel(d, element_cap=cfg.initializer.element_cap).readout_label(physical.prepared, pred.forecast, y, labels)
                assert mass.tobytes() == expected_mass[y, 0].tobytes() and division.tobytes() == expected_division[y, 0].tobytes()
                label_words += 2
            labels.check()
            check_state(native, physical.raw(), cfg)
            report = check_prediction(native, npred, physical.raw(), pred.raw(), cfg, F(100), F(100))
            assert packed_size((native, npred, physical.raw(), pred.raw(), report)) < FRAME
            old, old_raw = physical, physical.raw()
            native = m.observe(p, native, o.learner, npred, target, rules=cc.semantics, bit_limit=32768, sources=context)
            physical = phase('observe', physical, pred, npred.window, target)
            relation = check_state(native, physical.raw(), cfg)
            largest = max(largest, F(relation['state_error_upper']))
            assert old.raw() == old_raw
            # Complete immutable round-trip, including every future-used cache.
            assert physical.raw().cpu().raw(CPUArrays(element_cap=cfg.initializer.element_cap, cell_cap=CELLS)) == physical.raw()
            counts['events'] += 1
            if native.unit_count == unit:
                native = m.commit(native, o.learner, bit_limit=32768)
                physical = phase('commit', physical)
                relation = check_state(native, physical.raw(), cfg)
                largest = max(largest, F(relation['state_error_upper']))
                counts['commits'] += 1
        counts['histories'] += 1
    return dict(status='PASS_CPU_TOKEN_OWNER_TRANSITIONS', counts=counts,
        maximum_state_error_upper=str(largest), exact_primitive_words=oracle.words, exact_half_words=oracle.half_words,
        maximum_phase_cells=maximum_phase_cells,
        independently_compared_paid_label_words=label_words,
        scope='CPU transition/predicate control; no actual device, Runtime CUDA execution or issued bridge')


def actual_runtime(case):
    from fp_reference import ReferenceCompilerRuntime
    from fp_reference.profile import ProfileSpec
    from fp_reference.ingress import encode_context
    from fp_reference.host_resources import HostResourceContract
    from fp_reference.token_arrays import CudaArrays
    from fp_reference.token_streaming import Forest, Block
    from audit_reference_construction import limits, validate_residency
    if case == 'train-prefix8':
        from audit_token_reference_host import text_fixture
        from fp_reference import ConstructionContract, OnlineContract
        from fp_reference.data_usage import DataContract, StreamSpec
        from fp_reference.token_execution import TokenProgram, TokenInitializer, TokenLearner
        from fp_reference.token_sources import TokenAtomFamily, TokenSourceReads
        from fp_reference.program import SemanticRules
        d, root, windows, targets, identity = text_fixture()
        family = TokenAtomFamily(d.sources.vocabulary, d.sources.context)
        pattern = TokenInitializer(family, d.width, d.output, tuple(map(int, root.E.flat)),
            tuple(map(int, root.C)), tuple(map(int, root.W.flat)), 1 << 24)
        program = TokenProgram(d)
        rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
        cc = ConstructionContract(rules, limits(2 << 30, 10**15),
            {'construct': 'compiler', 'range_audit': 'compiler'}, program.counts(), pattern, F(100), F(100), 32768)
        data = DataContract((StreamSpec('train', 'train', tuple(f'train/{i}' for i in range(512))),),
                            'train', (), TokenSourceReads(family))
        online = OnlineContract(data, TokenLearner(d.output))
        cfg = TokenCudaPrefixContract(CudaStorageContract(128 << 20, 128 << 20,
            {r: (128 << 20, 128 << 20) for r in ('deployment', 'compiler')}), F(16), F(1, 10**6),
            phase_output_cells=1 << 22, phase_evidence_bytes=64 << 20, initializer=pattern, exact_cell_cap=4096)
        rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg,
            host=HostResourceContract(8 << 30, {'deployment': 8 << 30, 'compiler': 8 << 30}))
        for i, target in enumerate(targets[:8]):
            pred = rt.predict_next(f'train/{i}', encode_context(()))
            assert pred.status == 'PREDICTED_REFERENCE', pred.reason
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE', result.reason
        snapshot = validate_residency(rt)
        current = rt._cuda_learner_record(snapshot.candidates[0])
        assert snapshot.cursor == current.raw_state.cursor == current.raw_state.unit_count == 8
        assert tuple(x.window for x in current.raw_state.leaves) == windows[:8]
        assert tuple(x.target for x in current.raw_state.leaves) == targets[:8]
        rt._cuda.check_state(snapshot.candidates[0].learner, current.raw_state, bit_limit=32768)
        rows = tuple(rt._cuda.phases.values())
        assert len(rows) == 17 and all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows)
        outcome = dict(ordinary_targets=8, pending_unit_count=8, committed_units=0,
            vocabulary=d.output.labels, context=d.sources.context, retained_master_coordinates=d.slot_count,
            checked_cuda_phases=len(rows), checked_device_words=sum(p.forward_operations for p in rows),
            corpus=identity, state_atol='16', probability_atol='1/1000000',
            scope='actual owned partial unit; no commit, loss or full-corpus affordability claim')
        rt._cuda.check()
        arena = rt._cuda.arena
        outcome.update(arena=dict(native_allocation_counter=arena._counter, current_allocation_counter=arena._allocation_counter(),
            consumed_bytes=arena._cursor, phases=len(arena._phases), regions=len(arena._regions), **arena._last_usage),
            runtime_halted=rt._halted is not None)
        return outcome, rt
    d, exact = fixture(4 if case == 'cache-forgery' else 2, 'mixed')
    profile = ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2)
    cc, program, online = registration(d, exact, 8, profiles=(profile,) if case == 'events-profile' else ())
    cc = replace(cc, limits=limits(384 << 20, 10**15))
    cfg = cuda_contract(cc.initializer_pattern)
    if case == 'observation-quota':
        cfg = replace(cfg, phase_output_cells=512)
    rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg,
        host=HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    def event(i, target):
        pred = rt.predict_next(f'train/{i}', encode_context(()))
        assert pred.status == 'PREDICTED_REFERENCE', pred.reason
        result = rt.observe(target)
        assert result.status == 'OBSERVED_REFERENCE', result.reason
        snapshot = validate_residency(rt)
        for candidate in snapshot.candidates:
            phase = rt._cuda_learner_record(candidate)
            rt._cuda.check_state(candidate.learner, phase.raw_state, bit_limit=32768)
        return snapshot
    if case == 'events-profile':
        for i, target in enumerate((0, 1, 1, 0)):
            event(i, target)
        candidate = rt.construct_candidate(program, profile_id=profile.profile_id)
        assert candidate.status == 'BUILT_REFERENCE', candidate.reason
        for i, target in enumerate((1, 0, 0, 1), 4):
            event(i, target)
        snapshot = validate_residency(rt)
        assert len(snapshot.profile_events) == 4 and len(snapshot.candidates) == 2
        rows = tuple(rt._cuda.phases.values())
        assert all(p.status == 'CHECKED_CUDA_PREFIX_PHASE' for p in rows)
        assert all(p.input_phase is None for p in rows if p.phase.endswith(':initialize'))
        sources = {r.observation_id: r.sources for r in snapshot.observations}
        for p in rows:
            if p.phase == 'profile:predict':
                window = p.raw_prediction.window
                assert (window.position, window.past) == (sources[p.observation_id].position, sources[p.observation_id].past)
        # Newborn physical states are exactly fresh Gamma, even after the
        # deployed learner has trained. Initialization has no trained input.
        births = [p.raw_state.origin for p in rows if p.phase.endswith(':initialize')]
        assert len(births) == 2
        assert (births[0].embedding, births[0].core, births[0].output) == (births[1].embedding, births[1].core, births[1].output)
        outcome = dict(ordinary_targets=8, candidate_event_observations=len(snapshot.event_traces),
            profile_events=len(snapshot.profile_events), checked_cuda_phases=len(rows),
            checked_device_words=sum(p.forward_operations for p in rows),
            original_profile_contexts_preserved=True, independently_derived_fresh_gamma=True)
    elif case == 'cache-forgery':
        for i, target in enumerate((0, 1, 1)):
            event(i, target)
        owner = rt._deployed_id
        identity = rt._cuda.current[owner]
        resident = rt._cuda._values[identity]
        assert resident.state.core.count == 3
        with rt._cuda.arena.phase('adversarial:equivalent-current-root') as workspace:
            a = CudaArrays(workspace, rt._buffers[f'{rt._runtime_id}:cuda-raw-readout'],
                           element_cap=cfg.initializer.element_cap, cell_cap=CELLS)
            zero = a.zeros(tuple(resident.basis.core.shape))
            compressed = Forest(3, (Block(2, resident.basis.core), Block(1, zero)))
            forged = replace(resident, state=replace(resident.state, core=compressed))
            a.check()
        assert forged.raw() != rt._cuda.phases[identity].raw_state
        # Same ordinary coordinates still pass the old numeric predicate.
        rt._cuda.check_state(rt._candidates[owner].learner, forged.raw(), bit_limit=32768)
        rt._cuda._values[identity] = forged
        try:
            rt.predict_next('train/3', encode_context(()))
        except RuntimeError:
            pass
        else:
            raise AssertionError('forged future-used carry cache accepted')
        assert rt._cuda.current[owner] == identity and rt._cursor == 3 and rt._halted is not None
        failure = tuple(rt._cuda.phases.values())[-1]
        assert failure.status == 'EXECUTION_FAILED' and 'continuation cache changed' in failure.reason
        outcome = dict(basis_only_relation_still_passes=True, complete_owner_refuses_forged_cache=True,
                       no_prediction_published=True, retained_ordinary_targets=3)
    else:
        assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        previous = dict(rt._cuda.current)
        if case == 'source-forgery':
            owner = rt._deployed_id
            identity = rt._cuda.predicted[owner]
            prediction = rt._cuda._values[identity]
            wrong = prediction.forecast.window.append(0)
            rt._cuda._values[identity] = replace(prediction, forecast=replace(prediction.forecast, window=wrong))
            try:
                rt.observe(1)
            except RuntimeError:
                pass
            else:
                raise AssertionError('source-forged physical forecast accepted')
        else:
            result = rt.observe(1)
            assert result.status == 'UNRESOLVED' and 'output-cell allowance' in result.reason, result
        assert rt._cursor == 0 and rt._cuda.current == previous and rt._halted is not None
        assert len(rt._observations) == 1 and rt._observations[0].target == 1
        assert rt._pending is not None and rt._pending.stage == 'observation-failed'
        failure = tuple(rt._cuda.phases.values())[-1]
        assert failure.reference.targets == (1,) and failure.reference.windows[-1].position == 0
        outcome = dict(actual_target_retained=True, original_source_retained=True,
            no_native_or_amp_successor_published=True, terminal_phase_status=failure.status, terminal_reason=failure.reason)
    rt._cuda.check()
    arena = rt._cuda.arena
    outcome.update(arena=dict(native_allocation_counter=arena._counter, current_allocation_counter=arena._allocation_counter(),
        consumed_bytes=arena._cursor, phases=len(arena._phases), regions=len(arena._regions), **arena._last_usage),
        runtime_halted=rt._halted is not None)
    return outcome, rt


def worker(case, output):
    from dataclasses import asdict
    import time
    import traceback
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    cap = 8 << 30 if case == 'train-prefix8' else HOST_CAP
    host = _WindowsProcessHost(HostResourceContract(cap, {'deployment': cap, 'compiler': cap}))
    before, start = measured(host), time.perf_counter()
    report, code = dict(status='RUNNING', case=case, before=before), 0
    Path(output).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = actual_runtime(case)
        report.update(status='PASS_ACTUAL_TOKEN_RUNTIME_OWNER', outcome=outcome,
                      device=asdict(rt._cuda._device.check()))
    except Exception as error:
        code = 2
        report.update(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000],
                      traceback=traceback.format_exc()[-5000:])
    report.update(after=measured(host), worker_wall_seconds=time.perf_counter()-start)
    Path(output).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', choices=('events-profile', 'cache-forgery', 'source-forgery', 'observation-quota', 'train-prefix8'))
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.worker:
        if not args.output:
            parser.error('worker requires output and an externally preattached host job')
        raise SystemExit(worker(args.worker, args.output))
    result = cpu()
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_TOKEN_CUDA_OWNER_CPU.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
