"""Complete CUDA frame storage controls; CPU mode has no device authority."""
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys
import time
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.resources import ObjectSpec, ResourceExceeded, ResourceLedger
from fp_reference.shared_reference import SharedReferenceContract, decoded_buffer, ROOT_KIND
from fp_reference import shared_reference as shared
from fp_reference import byte_archive as archive
from audit_owned_token_learner import fixture, registration
from audit_reference_construction import validate_residency, limits
from audit_shared_token_retention import rejects


STORAGE = SharedReferenceContract(2 << 20, 2 << 20, 2 << 20, 1 << 20, 8 << 20)


def full_registration():
    from audit_token_reference_host import text_fixture
    from fp_reference import ConstructionContract, OnlineContract
    from fp_reference.data_usage import DataContract, StreamSpec
    from fp_reference.token_execution import TokenProgram, TokenInitializer, TokenLearner
    from fp_reference.token_sources import TokenAtomFamily, TokenSourceReads
    from fp_reference.program import SemanticRules
    from fp_reference.cuda_prefix import TokenCudaPrefixContract
    from fp_reference.cuda_storage import CudaStorageContract
    d, origin, windows, targets, corpus = text_fixture()
    family = TokenAtomFamily(d.sources.vocabulary, d.sources.context)
    pattern = TokenInitializer(family, d.width, d.output, tuple(map(int, origin.E.flat)),
        tuple(map(int, origin.C)), tuple(map(int, origin.W.flat)), 1 << 24)
    program = TokenProgram(d)
    rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
    cc = ConstructionContract(rules, limits(2 << 30, 10**15),
        {'construct': 'compiler', 'range_audit': 'compiler'}, program.counts(), pattern, F(100), F(100), 32768)
    data = DataContract((StreamSpec('train', 'train', tuple(f'train/{i}' for i in range(512))),),
                        'train', (), TokenSourceReads(family))
    online = OnlineContract(data, TokenLearner(d.output))
    cfg = TokenCudaPrefixContract(CudaStorageContract(1 << 30, 1 << 30,
        {r: (1 << 30, 1 << 30) for r in ('deployment', 'compiler')}), F(16), F(1, 10**6),
        phase_output_cells=1 << 22, phase_evidence_bytes=64 << 20, initializer=pattern, exact_cell_cap=4096)
    storage = SharedReferenceContract(64 << 20, 16 << 20, 128 << 20, 8 << 20, 1 << 30)
    return cc, program, online, cfg, storage, origin, windows, targets, corpus


def preflight():
    """Count late full-unit records before committing the physical job caps.

    CPU schedule only; no new primitive/device validation or owned trajectory.
    The same already registered1024 training bytes supply the resource fixture.
    """
    from fp_reference.token_cuda_prefix import transition, fresh_origin, check_state, check_prediction
    from fp_reference.token_execution import TokenReferenceMachine, TokenState
    from fp_reference.token_sources import TokenValues, TokenContext
    from fp_reference.token_arrays import CPUArrays
    from fp_reference.token_cuda_state import ArrayWords
    from fp_reference.cuda_prefix import IndexedCudaPhase
    from fp_reference.token_array_events import Kernel
    from fp_reference.encoding import packed_size
    cc, program, online, cfg, storage, origin, windows, targets, corpus = full_registration()
    machine = TokenReferenceMachine(cc.initializer_pattern)
    def arithmetic():
        return CPUArrays(element_cap=1 << 24, cell_cap=cfg.phase_output_cells)
    a = arithmetic()
    physical = transition('initialize', program, cfg, None, None, None, None, 0,
        fresh_origin(program, cfg, 0, online.learner, cc.semantics, 32768), a)
    results = {}
    def measure(kind, reference, native_prediction, state, prediction, a, relation, window, target):
        # Deliberately longer fixed identities; this is a record-size control,
        # not a manufactured execution receipt or a Runtime-issued phase.
        record = IndexedCudaPhase('phase-'+'x'*192, 'candidate-'+'c'*96, program.program_id,
            'ordinary:'+kind, 511, 'train/511', 'input-'+'a'*192,
            'prediction-'+'p'*192 if kind == 'observe' else None, reference, native_prediction,
            state.raw(), None if prediction is None else prediction.raw(),
            tuple((tag, ArrayWords.capture(value, a)) for tag, value in a.records), relation,
            a.cells, 1026, 'CHECKED_CUDA_PREFIX_PHASE', '', a.cells,
            execution_plan=dict(window=window, target=target, schedule=Kernel.schedule_id,
                readout_recipe=Kernel.readout_id, primitive_words=1 << 30, exact_rounding_cells=4096))
        results[kind] = dict(canonical_record_bytes=packed_size(record), output_cells=a.cells,
                             pending_count=reference.unit_count)
    for i, (window, target) in enumerate(zip(windows, targets)):
        p = arithmetic()
        prediction = transition('predict', program, cfg, physical, None, window, None, i, None, p)
        if i == 511:
            native = TokenState(origin, windows[:i], targets[:i])
            source = TokenValues(TokenContext(cfg.initializer.sources, window.position, window.past))
            npred = machine.predict(program, cc.semantics, native, source, bit_limit=32768)
            relation = check_prediction(native, npred, physical.raw(), prediction.raw(), cfg, F(100), F(100))
            measure('predict', native, npred, physical, prediction, p, relation, window, None)
        a = arithmetic()
        physical = transition('observe', program, cfg, physical, prediction, window, target, i+1, None, a)
    native = TokenState(origin, windows, targets)
    measure('observe', native, None, physical, None, a,
            check_state(native, physical.raw(), cfg), windows[-1], targets[-1])
    native = machine.commit(native, online.learner, bit_limit=32768)
    a = arithmetic()
    physical = transition('commit', program, cfg, physical, None, None, None, 512, None, a)
    measure('commit', native, None, physical, None, a,
            check_state(native, physical.raw(), cfg), None, None)
    assert all(row['canonical_record_bytes']+8 < cfg.phase_evidence_bytes for row in results.values())
    assert 'torch' not in sys.modules
    return dict(status='PASS_FULL_UNIT_RECORD_SIZE_PREFLIGHT', phases=results,
        full_vocabulary=program.definition.output.labels, context=program.definition.sources.context,
        masters=program.slot_count, corpus=corpus,
        registered_frame_bytes=cfg.phase_evidence_bytes,
        scope='late-record CPU size/resource calibration; no actual owner/device execution or model score')


def native_root():
    d, initial = fixture(2, 'mixed')
    cfg, program, online = registration(d, initial)
    cfg = replace(cfg, limits=limits(128 << 20, 10**14))
    return ReferenceCompilerRuntime(cfg, program, online=online, shared_storage=STORAGE)


def add_frame(rt, ordinal, size):
    label = f'shared-frame-control:{ordinal}'
    value = dict(label=label, words=bytes(range(256))*4, integer=ordinal,
                 status='COMPLETE_SYNTHETIC_FRAME')
    body = pack(value)
    assert 8+len(body) < size
    rt._ledger.allocate(rt._data_owner, (ObjectSpec(label, 'owned_cuda_phase_frame',
        {'reference_payload_bytes': size, 'physical_objects': 1}, rt._chi),))
    rt._buffers[label] = bytearray(size)
    block = bytes(range(256))
    for offset in range(0, size, len(block)):
        rt._buffers[label][offset:min(offset+len(block), size)] = block[:min(len(block), size-offset)]
    rt._buffers[label][:8] = len(body).to_bytes(8, 'big')
    rt._buffers[label][8:8+len(body)] = body
    return label, value


def seal(rt, label, value):
    rt._reference_archive.seal_cuda_frame(rt, label, value, role='compiler')


def cpu():
    rt, saved, compared, coexist = native_root(), [], 0, []
    prepare = ResourceLedger.prepare_transfer
    for i in range(17):
        label, value = add_frame(rt, i, (1 << 16)+i)
        original = bytes(rt._buffers[label])
        old_snapshot = rt.snapshot()
        def check(ledger, moves, releases=(), close_owners=()):
            if any(identity == label+':shared-root-copy' for _, identity, _ in releases):
                page_id = rt._reference_archive.pages[-1]
                scratch = page_id+':copy'
                assert rt._buffers[scratch] == rt._buffers[page_id]
                assert type(rt._buffers[label]) is bytearray and bytes(rt._buffers[label]) == original
                assert type(rt._buffers[page_id]) is bytes and type(rt._buffers[scratch]) is bytearray
                validate_residency(rt)
                coexist.append((len(original), len(rt._buffers[page_id])))
            return prepare(ledger, moves, releases, close_owners)
        with patch.object(ResourceLedger, 'prepare_transfer', check):
            seal(rt, label, value)
        snapshot = validate_residency(rt)
        assert rt._router._ledger is rt._event_router._ledger is rt._ledger
        assert snapshot.resources['objects'][label]['kind'] == ROOT_KIND+'owned_cuda_phase_frame'
        assert type(rt._buffers[label]) is bytes and len(rt._buffers[label]) == 16
        decoded = b''.join(decoded_buffer(snapshot, label, byte_cap=STORAGE.expanded_cap,
                                         reference_cap=STORAGE.reference_cap))
        assert decoded == original and set(decoded) == set(range(256))
        assert dict(old_snapshot.buffers)[label] == original
        saved.append((snapshot, label, original))
        compared += len(original)
    # Every original snapshot is self-contained after later dictionary appends.
    for snapshot, label, original in saved:
        assert b''.join(decoded_buffer(snapshot, label, byte_cap=STORAGE.expanded_cap,
                                      reference_cap=STORAGE.reference_cap)) == original
    failures = []
    for mode in ('work', 'copy', 'root', 'wrong-bytes', 'prepare-expected',
                 'prepare-unexpected', 'router-expected', 'router-unexpected'):
        broken = native_root()
        label, value = add_frame(broken, 0, 1 << 16)
        raw, old_root = bytes(broken._buffers[label]), broken.__dict__
        if mode == 'work':
            hook = patch.object(broken._ledger, 'charge_work', side_effect=ResourceExceeded('paid work refused'))
        elif mode in ('copy', 'root'):
            allocate = broken._ledger.allocate
            def refuse(owner, objects, **kw):
                kind = 'shared_reference_copy_workspace' if mode == 'copy' else 'shared_cuda_frame_root_copy'
                if any(obj.kind == kind for obj in objects):
                    raise ResourceExceeded('prepublication residency refused')
                return allocate(owner, objects, **kw)
            hook = patch.object(broken._ledger, 'allocate', refuse)
        elif mode == 'wrong-bytes':
            push = archive.Builder.push
            def wrong(builder, part):
                return push(builder, bytes((part[0] ^ 1,))+part[1:])
            hook = patch.object(archive.Builder, 'push', wrong)
        else:
            error = ResourceExceeded if mode.endswith('expected') and not mode.endswith('unexpected') else RuntimeError
            owner, method = ((ResourceLedger, 'prepare_transfer') if mode.startswith('prepare') else (shared, 'CostRouter'))
            hook = patch.object(owner, method, side_effect=error('prepublication failure'))
        with hook:
            rejects(lambda: seal(broken, label, value), (ContractError, RuntimeError))
        state = validate_residency(broken)
        assert broken.__dict__ is old_root
        assert type(broken._buffers[label]) is bytearray and bytes(broken._buffers[label]) == raw
        if mode.startswith(('prepare', 'router')):
            page_id = broken._reference_archive.pages[-1]
            assert broken._buffers[page_id] == broken._buffers[page_id+':copy']
            assert label+':shared-root-copy' in dict(state.buffers)
        failures.append(mode)
    assert 'torch' not in sys.modules
    return dict(status='PASS_EXACT_SHARED_CUDA_FRAME_RETENTION', complete_frames=len(saved),
        full_frame_bytes_compared=compared, all_256_byte_values_and_nonzero_padding=True,
        original_and_both_page_copies_paid_before_publication=len(coexist),
        old_snapshots_decode_after_later_appends=True, failure_boundaries=failures,
        scope='exact actual Runtime storage hook; synthetic frames, no CUDA execution or model claim')


def actual(case, progress):
    from fp_reference.host_resources import HostResourceContract
    from fp_reference.ingress import encode_context
    from fp_reference.profile import ProfileSpec
    from audit_token_cuda_owner import cuda_contract
    from audit_token_reference_host import measured
    started = time.perf_counter()
    if case == 'full-unit512':
        cc, program, online, cfg, storage, _, windows, targets, corpus = full_registration()
        host_cap = 16 << 30
    else:
        d, initial = fixture(2, 'mixed')
        profile = ProfileSpec('reverse-repeat', ('train/3', 'train/0'), 2)
        cc, program, online = registration(d, initial, count=12, profiles=(profile,))
        cc = replace(cc, limits=limits(384 << 20, 10**15))
        cfg, storage, host_cap = cuda_contract(cc.initializer_pattern), STORAGE, 4 << 30
        targets, corpus = (0, 1, 1, 0, 1, 0, 0, 1), None
    rt = ReferenceCompilerRuntime(cc, program, online=online, cuda=cfg, shared_storage=storage,
        host=HostResourceContract(host_cap, {r: host_cap for r in ('deployment', 'compiler')}))
    def publish(stage):
        progress.write_text(json.dumps(dict(stage=stage, cursor=rt._cursor,
            observations=len(rt._observations), cuda_phases=len(rt._cuda.phases),
            archive_pages=len(rt._reference_archive.pages), elapsed_seconds=time.perf_counter()-started,
            host=measured(rt._host))), encoding='utf-8')
    publish('initialized')
    for i, target in enumerate(targets):
        pred = rt.predict_next(f'train/{i}', encode_context(()))
        if pred.status != 'PREDICTED_REFERENCE':
            publish('prediction-unresolved')
            raise RuntimeError(pred.reason)
        observed = rt.observe(target)
        if observed.status != 'OBSERVED_REFERENCE':
            publish('observation-unresolved')
            raise RuntimeError(observed.reason)
        if case == 'profile-and-retention-fault' and i == 3:
            child = rt.construct_candidate(program, profile_id='reverse-repeat')
            assert child.status == 'BUILT_REFERENCE', child.reason
        if (i+1) % 16 == 0 or i == len(targets)-1:
            publish('ordinary-prefix')
    snapshot = validate_residency(rt)
    rows = tuple(rt._cuda.phases.values())
    assert all(row.status == 'CHECKED_CUDA_PREFIX_PHASE' for row in rows)
    for row in rows:
        assert snapshot.resources['objects'][row.object_id]['kind'] == ROOT_KIND+'owned_cuda_phase_frame'
        root = rt._buffers[row.object_id]
        ordinal = archive.U64.unpack_from(root, 8)[0]
        header = archive._page(rt._buffers[snapshot.reference_archive.pages[ordinal]])
        assert header.expanded_bytes == cfg.phase_evidence_bytes
    for candidate in snapshot.candidates:
        phase = rt._cuda_learner_record(candidate)
        rt._cuda.check_state(candidate.learner, phase.raw_state, bit_limit=32768)
    outcome = dict(ordinary_targets=len(targets), candidate_observations=len(snapshot.event_traces),
        profile_events=len(snapshot.profile_events), checked_cuda_phases=len(rows),
        checked_device_words=sum(p.forward_operations for p in rows),
        complete_frame_bytes_decoded=len(rows)*cfg.phase_evidence_bytes,
        archive_pages=len(snapshot.reference_archive.pages),
        actual_page_bytes=sum(len(rt._buffers[key]) for key in snapshot.reference_archive.pages),
        paid_reference_peak=snapshot.resources['peak']['reference_payload_bytes'],
        vocabulary=program.definition.output.labels, context=program.definition.sources.context,
        master_coordinates=program.slot_count, corpus=corpus)
    if case == 'full-unit512':
        learner = snapshot.candidates[0].learner
        current = rt._cuda_learner_record(snapshot.candidates[0])
        assert snapshot.cursor == current.raw_state.cursor == 512
        assert learner.unit_count == current.raw_state.unit_count == 0
        assert learner.origin.optimizer_steps == current.raw_state.origin.optimizer_steps == 1
        assert len(rows) == 1026
        # The complete observed native unit and every original source remain.
        last_observation = next(p for p in reversed(rows) if p.phase == 'ordinary:observe')
        assert last_observation.reference.windows == windows and last_observation.reference.targets == targets
        assert tuple(x.window for x in last_observation.raw_state.leaves) == windows
        assert tuple(x.target for x in last_observation.raw_state.leaves) == targets
        outcome.update(committed_units=1, pending_count=0, all_original_unit_records_retained=True,
                       state_atol='16', probability_atol='1/1000000')
    else:
        assert len(rows) == 44 and len(snapshot.profile_events) == 4
        forecasts = rt.predict_next('train/8', encode_context(()))
        assert forecasts.status == 'PREDICTED_REFERENCE', forecasts.reason
        before = tuple(c.learner for c in rt._candidates.values())
        current = dict(rt._cuda.current)
        original = archive.Builder.push
        def changed(builder, part):
            return original(builder, bytes((part[0] ^ 1,))+part[1:])
        with patch.object(archive.Builder, 'push', changed):
            rejects(lambda: rt.observe(1), RuntimeError)
        failed = validate_residency(rt)
        assert failed.halted and failed.cursor == 8 and len(failed.observations) == 9
        assert failed.observations[-1].target == 1 and failed.observations[-1].sources.position == 8
        assert tuple(c.learner for c in rt._candidates.values()) == before and rt._cuda.current == current
        bad = tuple(rt._cuda.phases.values())[-1]
        assert bad.phase == 'ordinary:observe' and bad.status == 'EXECUTION_FAILED'
        assert bad.reference.targets[-1] == 1
        assert type(rt._buffers[bad.object_id]) is bytearray
        assert len(rt._buffers[bad.object_id]) == cfg.phase_evidence_bytes
        outcome.update(changed_page_rejected_after_actual_target=True,
            failed_full_frame_retained=True, no_native_or_amp_successor_published=True)
    rt._cuda.check()
    arena = rt._cuda.arena
    outcome.update(arena=dict(native_allocation_counter=arena._counter,
        current_allocation_counter=arena._allocation_counter(), consumed_bytes=arena._cursor,
        phases=len(arena._phases), regions=len(arena._regions), **arena._last_usage))
    publish('complete')
    return outcome, rt


def worker(case, output, progress):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from audit_token_reference_host import measured
    cap = 16 << 30 if case == 'full-unit512' else 4 << 30
    host = _WindowsProcessHost(HostResourceContract(cap, {r: cap for r in ('deployment', 'compiler')}))
    before = measured(host)
    try:
        import torch
        torch.set_num_threads(1)
        outcome, rt = actual(case, progress)
        result = dict(status='PASS_ACTUAL_SHARED_TOKEN_RETENTION', case=case, before=before,
            after=measured(host), outcome=outcome, device=asdict(rt._cuda._device.check()))
    except Exception as error:
        import traceback
        result = dict(status='FAILED_ACTUAL_SHARED_TOKEN_RETENTION', case=case, before=before,
            after=measured(host), error=f'{type(error).__name__}: {error}', traceback=traceback.format_exc()[-12000:])
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    if result['status'] != 'PASS_ACTUAL_SHARED_TOKEN_RETENTION':
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--worker', choices=('profile-and-retention-fault', 'full-unit512'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--progress', type=Path)
    args = parser.parse_args()
    if args.worker:
        if args.output is None or args.progress is None:
            parser.error('worker requires its result and bounded progress paths')
        worker(args.worker, args.output, args.progress)
        return
    result = preflight() if args.preflight else cpu()
    body = json.dumps(result, indent=2)+'\n'
    if args.write:
        name = 'FP_SHARED_CUDA_RETENTION_PREFLIGHT.json' if args.preflight else 'FP_SHARED_CUDA_RETENTION_CPU.json'
        (ROOT/'evidence/minimal'/name).write_text(body, encoding='utf-8')
    print(body)


if __name__ == '__main__':
    main()
