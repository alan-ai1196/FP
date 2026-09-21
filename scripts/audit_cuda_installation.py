"""Actual owned CUDA installation, identity transport and failed boundaries.

Each case uses a fresh allocator process. The native class, pre-context
evidence and entire pre/post-install learners are obtained through Runtime.
CPU lease algebra has its separate exhaustive audit; this checks device
identity, quiescence and the complete combined publication on real CUDA.
"""
from dataclasses import replace
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime
from fp_reference import cuda_learner as gpu
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.cuda_storage import CudaStorageUnresolved
from fp_reference.machine import pack
from fp_reference.native_search import GrammarLimits
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH, LIVE_STATUSES
from fp_reference.program import Binding, DelayedStateSpec
from audit_cpu_installation import configuration, SMALL
from audit_cuda_runtime import cuda_contract, audit_snapshot
from audit_paired_cpu_persistence import config
from audit_reference_construction import limits, rejects, zero_program
from audit_reference_persistence import event, identity, owned
from audit_float64_runtime import replay


def fixture(*, learned=False, recurrent=False, continued=False, cpu=True, host=None, byte_cap=500_000_000, work_cap=12_000_000_000):
    cfg = config(cap=10, peak=10, pattern=(F(2),)) if learned else config(cap=4, peak=1)
    if recurrent:
        cfg = replace(cfg, semantics=replace(cfg.semantics, states=(DelayedStateSpec('h', 'mass', 2, F(1)),)))
    cfg = replace(cfg, limits=limits(byte_cap, work_cap))
    bounds = GrammarLimits(3, 2, 0, 1, 1) if learned else SMALL
    cfg, run = configuration(cfg=cfg, bounds=bounds, continued=continued, count=60 if continued else 40)
    rules = tuple(replace(r, rule_id=r.rule_id.replace('finite', 'cuda'), score_path=CUDA_PATH)
                  if r.score_path == FLOAT64_PATH else r for r in run.persistence.rules)
    run = replace(run, persistence=replace(run.persistence, rules=rules), cpu_install=None,
                  float64=run.float64 if cpu else None)
    base = replace(zero_program(2), bindings=(Binding('h', 0),)) if recurrent else zero_program(2)
    rt = ReferenceCompilerRuntime(cfg, base, online=run, host=host, cuda=cuda_contract(install=CudaInstallContract()))
    event(rt, 0)
    event(rt, 0)
    search, ids = select(rt, 'native', 'ref', 'cuda')
    cross(rt, ids, 0)
    return rt, search, ids


def select(rt, search_name, ref_rule, cuda_rule):
    search = rt.start_reference_search(search_name)
    search = rt.advance_reference_search(search.search_id, transitions=10000)
    if search.status != 'REFERENCE_CLASS_EXHAUSTED':
        session = next(s for s in rt.snapshot().searches if s.search_id == search.search_id)
        histogram = Counter((row.status, row.reason) for row in session.rows if row.status != 'COMPARED_REFERENCE')
        largest = histogram.most_common(8)
        raise AssertionError(json.dumps({'search_result': repr(search), 'total_rows': len(session.rows),
            'unresolved_reasons': [{'status': status, 'reason': reason, 'rows': count}
                                   for (status, reason), count in largest],
            'other_unresolved_rows': sum(histogram.values())-sum(count for _, count in largest)}))
    r = rt.admit_reference_persistence(search.best_candidate_id, ref_rule)
    c = rt.admit_cuda_persistence(search.best_candidate_id, cuda_rule)
    ids = r.identity_id, c.identity_id
    assert all(ids) and all(identity(rt, key).status == 'ACTIVE' for key in ids), (r, c)
    return search, ids


def cross(rt, ids, target):
    for _ in range(30):
        event(rt, target)
        if rt.paired_cuda_persistence_result(*ids).status == 'PAIRED_CUDA_CROSSED' and rt.snapshot().cursor % 2 == 0:
            return
    raise AssertionError('fixture did not reach its two independent owned crossings')


def install(rt, selected, ids, **changes):
    arguments = dict(proposal_proof_id=selected.proof_id, reference_identity=ids[0], cuda_identity=ids[1])
    arguments.update(changes)
    return rt.install_cuda(selected.best_candidate_id, **arguments)


def ownership(rt):
    snapshot = owned(rt)
    buffers = dict(snapshot.buffers)
    for receipt in snapshot.install_receipts:
        assert receipt.attempt.status == 'INSTALLED_CUDA'
        assert buffers[receipt.object_id] == pack(receipt)
    for candidate in snapshot.candidates:
        role = 'deployment' if candidate.candidate_id == snapshot.deployed_id else 'compiler'
        assert snapshot.resources['owners'][candidate.physical_owner] == role
    return snapshot


def success_case(*, learned=False, recurrent=False, cpu=True):
    rt, selected, ids = fixture(learned=learned, recurrent=recurrent, cpu=cpu)
    rt.start_reference_search('native')
    before, prefix = ownership(rt), rt._cuda
    target = next(c for c in before.candidates if c.candidate_id == selected.best_candidate_id)
    if learned:
        assert target.theta and target.theta != (F(2),)*len(target.theta)
    actual_objects = dict(prefix._values)
    storage = prefix.arena._storage
    published = []
    def trace(frame, kind, arg):
        if frame.f_code is ReferenceCompilerRuntime._install_owned.__code__ and kind in ('line', 'return'):
            if not published or published[-1] != rt._deployed_id:
                published.append(rt._deployed_id)
            if rt._deployed_id == target.candidate_id:
                assert rt._event_phase == 'idle'
                assert all(s.status not in LIVE_STATUSES for s in rt._persistence_identities.values())
                assert all(s.status == 'CLOSED_BY_INSTALL' for s in rt._searches.values())
                assert rt._cuda is prefix and rt._cuda.arena._storage is storage
        return trace
    sys.settrace(trace)
    try:
        result = install(rt, selected, ids)
    finally:
        sys.settrace(None)
    assert result.status == 'INSTALLED_CUDA', result
    after = ownership(rt)
    assert published == [before.deployed_id, target.candidate_id]
    assert after.cursor == before.cursor and after.observations == before.observations
    assert after.data_uses == before.data_uses and after.alpha_allocations == before.alpha_allocations
    assert after.cuda == before.cuda and after.float64_traces == before.float64_traces
    assert all(rt._cuda._values[key] is value for key, value in actual_objects.items())
    assert rt._cuda.arena._storage is storage
    for prior in before.candidates:
        current = next(c for c in after.candidates if c.candidate_id == prior.candidate_id)
        assert replace(current, physical_owner=prior.physical_owner) == prior
    receipt = after.install_receipts[-1]
    assert receipt.cuda_transport.current
    assert tuple((row[0], row[1]) for row in receipt.cuda_transport.current) == before.cuda.current
    assert receipt.cuda_transport.allocation_counter == (1, 16 << 20, 1)
    assert rt.paired_cuda_persistence_result(*ids).status == 'UNRESOLVED'
    rejects(lambda: rt.reference_class_proof(selected.proof_id, decision_class_id=selected.decision_class_id))
    peak_before = before.resources['peak']['reference_payload_bytes']
    peak_install = after.resources['peak']['reference_payload_bytes']
    work_before = before.resources['spent']['deployment']['work']
    work_after = after.resources['spent']['deployment']['work']
    # Execution really continues with the new deployment and the old shadow.
    event(rt, 1)
    event(rt, 0)
    result = audit_snapshot(rt)
    cpu_phases = replay(rt)[0] if cpu else 0
    result.update(native_class_size=selected.programs_compared, install_cursor=after.cursor,
        trained_nonzero_state=learned, recurrent=recurrent, independent_CPU_phases=cpu_phases,
        one_complete_root_publication=True, identical_device_objects_and_extents=True,
        peak_before_install=peak_before, peak_during_install=peak_install,
        deployment_work_before=work_before, deployment_work_after=work_after)
    return result


def failure_case(kind, *, byte_cap=500_000_000, work_cap=4_000_000_000):
    rt, selected, ids = fixture(byte_cap=byte_cap, work_cap=work_cap)
    before = ownership(rt)
    if kind == 'capacity':
        result = install(rt, selected, ids)
        assert result.status == 'UNRESOLVED' and result.attempt_id, result
    elif kind == 'late':
        fault = RuntimeError('injected combined-root preparation failure')
        with patch.object(rt._ledger, 'prepare_transfer', side_effect=fault):
            try:
                install(rt, selected, ids)
            except RuntimeError as exc:
                assert exc is fault
            else:
                raise AssertionError('late failed installation was published')
    elif kind == 'unknown':
        rt._cuda.future_job = []
        result = install(rt, selected, ids)
        assert result.status == 'UNRESOLVED' and 'unregistered device state coordinate' in result.reason
        del rt._cuda.future_job
    elif kind == 'pending':
        import torch
        torch.cuda._sleep(200_000_000)
        assert not torch.cuda.default_stream().query()
        result = install(rt, selected, ids)
        assert result.status == 'UNRESOLVED' and 'quiescent' in result.reason, result
        torch.cuda.synchronize()
    else:
        assert kind in ('corrupt', 'extent')
        original = rt._machine.realize
        raw, changed = gpu.raw_tensor, []
        def read(value):
            if kind == 'extent' and changed and value is changed[0]:
                raise AssertionError('installation read outside its initialized extent before rejecting the view')
            return raw(value)
        def change(object_id, label, value, chi):
            if label == 'prepared_cuda_install_receipt':
                # Same byte storage and raw values, but an invalid complete
                # gradient shape. A failed bridge must revoke old crossings.
                phase = rt._cuda.current[selected.best_candidate_id]
                gradient = rt._cuda._values[phase].gradient_sum
                if kind == 'corrupt':
                    gradient.unsqueeze_(0)
                else:
                    assert gradient.numel() == 0
                    gradient.as_strided_((2,), (1,))
                changed.append(gradient)
            return original(object_id, label, value, chi)
        with patch.object(rt._machine, 'realize', change), patch.object(gpu, 'raw_tensor', read):
            rejects(lambda: install(rt, selected, ids))
        after = rt.snapshot()
        assert after.halted and after.deployed_id == before.deployed_id
        assert all(v.status == 'UNRESOLVED' for v in after.persistence_identities)
        rejects(lambda: rt.cuda_persistence_result(ids[1]), CudaStorageUnresolved)
        assert after.alpha_spent == before.alpha_spent
        return {'observed_device_metadata_corruption_is_terminal_without_a_live_old_crossing': True,
                'out_of_extent_view_refused_before_numeric_read': kind == 'extent'}
    after = ownership(rt)
    assert after.candidates == before.candidates and after.cuda == before.cuda
    assert after.persistence_identities == before.persistence_identities
    assert after.searches == before.searches and after.alpha_spent == before.alpha_spent
    assert not after.install_receipts and after.next_install == before.next_install+1
    assert after.resources['spent']['deployment']['work'] > before.resources['spent']['deployment']['work']
    if kind in ('late', 'unknown'):
        assert install(rt, selected, ids).status == 'INSTALLED_CUDA'
        assert rt.snapshot().next_install == before.next_install+2
    return {'failed_preparation_preserves_old_learners_evidence_and_frontier': True,
            'actual_work_peak_and_attempt_IDs_not_refunded': True, 'case': kind}


def guards_case():
    rt, selected, ids = fixture()
    assert install(rt, selected, ids, proposal_proof_id='not-owned').status == 'UNRESOLVED'
    rejects(lambda: install(rt, selected, ids, cuda_identity=ids[0]))
    assert rt.install_cpu(selected.best_candidate_id, proposal_proof_id=selected.proof_id,
                         reference_identity=ids[0], float64_identity=ids[1]).status == 'UNRESOLVED'
    assert rt.install(selected.best_candidate_id, certificate=True).status == 'UNRESOLVED'
    event(rt, 0)
    before = rt.snapshot()
    assert install(rt, selected, ids).status == 'UNRESOLVED'
    assert rt.snapshot() == before
    event(rt, 0)
    graph = dict(rt.snapshot().programs)[next(c.program_id for c in rt.snapshot().candidates if c.candidate_id == selected.best_candidate_id)]
    newborn = rt.construct_candidate(graph)
    assert newborn.status == 'BUILT_REFERENCE'
    assert rt.install_cuda(newborn.candidate_id, proposal_proof_id=selected.proof_id,
                           reference_identity=ids[0], cuda_identity=ids[1]).status == 'UNRESOLVED'
    assert install(rt, selected, ids).status == 'INSTALLED_CUDA'
    return {'wrong_path_fake_proof_partial_unit_and_same_graph_newborn_refused': True,
            'CPU_and_generic_tokens_cannot_install_the_CUDA_root': True}


def continuation_case():
    rt, first, ids = fixture(continued=True)
    assert install(rt, first, ids).status == 'INSTALLED_CUDA'
    event(rt, 1)
    event(rt, 1)
    second, later = select(rt, 'next', 'ref-next', 'cuda-next')
    assert set(ids).isdisjoint(later)
    assert all(identity(rt, key).wealth == 1 and identity(rt, key).start_cursor == 24 for key in later)
    cross(rt, later, 1)
    assert install(rt, second, later).status == 'INSTALLED_CUDA'
    snapshot = ownership(rt)
    assert len(snapshot.install_receipts) == 2 and snapshot.alpha_spent == F(3, 4)
    assert snapshot.install_receipts[-1].attempt.old_deployed_id == first.best_candidate_id
    assert rt.paired_cuda_persistence_result(*ids).status == rt.paired_cuda_persistence_result(*later).status == 'UNRESOLVED'
    exhausted = rt.admit_cuda_persistence(first.best_candidate_id, 'cuda-next')
    assert exhausted.status == 'UNRESOLVED' and exhausted.identity_id is None
    event(rt, 0)
    event(rt, 1)
    return {'install_cursors': [r.attempt.cursor for r in snapshot.install_receipts],
            'native_classes': [first.programs_compared, second.programs_compared],
            'second_comparison_uses_actual_new_base_and_fresh_alpha': True,
            'no_alpha_refund_after_two_installs': True, 'independent_CUDA_phases': audit_snapshot(rt)['phases']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case')
    parser.add_argument('--byte-cap', type=int, default=500_000_000)
    parser.add_argument('--work-cap', type=int, default=4_000_000_000)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.case:
        if args.write:
            parser.error('a subcase cannot replace canonical evidence')
        if args.case in ('small', 'learned', 'recurrent', 'no-cpu'):
            result = success_case(learned=args.case == 'learned', recurrent=args.case == 'recurrent', cpu=args.case != 'no-cpu')
        elif args.case == 'guards':
            result = guards_case()
        elif args.case == 'continuation':
            result = continuation_case()
        else:
            result = failure_case(args.case, byte_cap=args.byte_cap, work_cap=args.work_cap)
        print(json.dumps(result))
        return
    report = {'status': 'PASS', 'scope': 'owned serialized same-device CUDA installation; tensor/packed-host model, not full device release'}
    def execute(case, *extra):
        process = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--case', case, *map(str, extra)],
                                 capture_output=True, text=True, timeout=900)
        if process.returncode:
            raise RuntimeError(process.stdout+process.stderr)
        print(case+' PASS', flush=True)
        return json.loads(process.stdout)
    for case in ('small', 'learned', 'recurrent', 'no-cpu', 'guards', 'late', 'unknown', 'pending', 'corrupt', 'extent', 'continuation'):
        report[case] = execute(case)
    baseline = report['small']
    cap = (baseline['peak_before_install']+baseline['peak_during_install'])//2
    assert baseline['peak_before_install'] < cap < baseline['peak_during_install']
    report['byte-cap'] = execute('capacity', '--byte-cap', cap)
    report['byte-cap']['registered_cap'] = cap
    cap = (baseline['deployment_work_before']+baseline['deployment_work_after'])//2
    report['work-cap'] = execute('capacity', '--work-cap', cap)
    report['work-cap']['registered_cap'] = cap
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_INSTALLATION_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
