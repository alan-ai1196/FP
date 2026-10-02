"""Complete-state and refusal checks for ordinary live-ledger projection.

No corpus, performance result, actual CUDA or new certificate authority.
"""
from contextlib import nullcontext
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceLedger, ResourceExceeded
from audit_native_history_work import trajectory
from audit_shared_token_retention import STORAGE, failures as storage_failures
from audit_token_reporting import report_registration
from ledger_projection_audit_support import BASELINE, original_observe


def paired_histories(original):
    checked, samples = 0, []
    cases = [(word, shared, 2) for shared, word in product((False, True), product((0, 1), repeat=4))]
    cases += [((0, 1, 1, 0)*16, shared, 512) for shared in (False, True)]
    for word, shared, unit in cases:
        results, counts = [], []
        for old in (True, False):
            with (patch.object(ReferenceCompilerRuntime, 'observe', original) if old else nullcontext()):
                value, count = trajectory(word, shared, observed=True, unit=unit,
                    expected_snapshots=old)
            results.append(value)
            counts.append(count)
        assert results[0] == results[1]
        # The exact same complete live-lease traversal still runs. All other
        # measured whole-history terms remain and must not be advertised away.
        for key, value in counts[0]['counts'].items():
            if not key.startswith('snapshot'):
                assert counts[1]['counts'][key] == value, key
        if len(word) == 64:
            samples.append(dict(storage='shared' if shared else 'packed', targets=64,
                removed_snapshot_event_rows=counts[0]['counts']['snapshot_event_rows'],
                retained_residency_object_rows=counts[1]['counts']['residency_object_rows'],
                retained_ledger_clone_slots=counts[1]['counts']['detached_event_slots'],
                all_other_counted_traversals_equal=True))
        checked += 1
    return dict(paired_complete_histories=checked, complete_serialized_snapshots_equal=True,
        exact_work_comparison=samples)


def barrier_failures(original):
    results = []
    for shared, mode in product((False, True), ('empty-lease', 'zero-lease', 'unknown-owner',
                                               'closed-owner', 'resource', 'memory')):
        answers = []
        for old in (True, False):
            with (patch.object(ReferenceCompilerRuntime, 'observe', original) if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='projection-failure-control'):
                cc, p, online, report = report_registration()
                rt = ReferenceCompilerRuntime(cc, p, online=online, reporting=report,
                    shared_storage=STORAGE if shared else None)
                assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
                prior = rt._candidates[rt._deployed_id].learner
                release = ResourceLedger.release_many
                repairs, fired = [], []
                def inject(ledger, releases):
                    result = release(ledger, releases)
                    if sys._getframe(1).f_code.co_name != 'observe':
                        return result
                    assert not fired
                    fired.append(True)
                    if mode in ('resource', 'memory'):
                        return result
                    key = next(iter(ledger._objects))
                    saved = ledger._refs[key]
                    repairs.append((key, saved))
                    if mode == 'empty-lease':
                        ledger._refs[key] = {}
                    elif mode == 'zero-lease':
                        ledger._refs[key] = {next(iter(saved)): 0}
                    elif mode == 'unknown-owner':
                        ledger._refs[key] = {'unregistered-owner': 1}
                    else:
                        lease_owner = next(iter(saved))
                        assert lease_owner not in ledger._closed_owners
                        ledger._closed_owners.add(lease_owner)
                        repairs.append(('closed', lease_owner))
                    return result
                residency = ResourceLedger._residency
                def barrier(ledger, *args):
                    if fired and mode in ('resource', 'memory'):
                        error = ResourceExceeded if mode == 'resource' else MemoryError
                        raise error('post-release live-lease control')
                    return residency(ledger, *args)
                with patch.object(ResourceLedger, 'release_many', inject), \
                        patch.object(ResourceLedger, '_residency', barrier):
                    try:
                        outcome = rt.observe(1)
                        assert mode == 'resource' and outcome.status == 'UNRESOLVED'
                    except (ContractError, MemoryError) as error:
                        assert mode != 'resource'
                        assert isinstance(error, MemoryError) == (mode == 'memory')
                assert fired and rt._cursor == 0 and rt._halted
                assert rt._observations[-1].target == 1
                assert rt._candidates[rt._deployed_id].learner is prior
                if mode == 'memory':
                    assert rt._halted is HOST_ALLOCATION_FAILURE
                # Remove the synthetic invalid lease only to inspect the full
                # already terminal diagnostic; never resume either trajectory.
                for key, value in reversed(repairs):
                    if key == 'closed':
                        rt._ledger._closed_owners.remove(value)
                    else:
                        rt._ledger._refs[key] = value
                answers.append(pack(rt.snapshot()))
                try:
                    rt.predict_next('train/0', encode_context(()))
                except ContractError:
                    pass
                else:
                    raise AssertionError('failed observation retained continuation authority')
        assert answers[0] == answers[1], (shared, mode)
        results.append(('shared' if shared else 'packed')+'/'+mode)
    return dict(paired_terminal_controls=results, complete_failed_snapshots_equal=True,
        target_and_prior_learner_retained=True, continuation_denied=True)


def cpu_phases(original):
    import audit_owned_token_workspaces as owned
    cases = [((0, 1, 1, 0), unit, False, False, False) for unit in (1, 2, 4)]
    cases += [((0, 1, 1, 0)*2, 8, False, False, False),
        ((0, 1, 1, 0, 0, 1), 2, True, False, False),
        ((0, 1, 1, 0)*2, 4, False, True, True)]
    phases = words = body_bytes = 0
    for word, unit, profile, combined, archived in cases:
        answers = []
        for old in (True, False):
            with (patch.object(ReferenceCompilerRuntime, 'observe', original) if old else nullcontext()), \
                    patch.object(owned, 'numerical_phase', pack):
                answers.append(owned.trajectory(word, archived, unit=unit, profile=profile, combined=combined))
        assert answers[0] == answers[1]
        phases += len(answers[0]['phases'])
        words += answers[0]['primitive_words']
        body_bytes += sum(map(len, answers[0]['phases']))
    return dict(paired_histories=len(cases), complete_phase_bodies=phases,
        checked_primitive_words=words, complete_phase_bytes=body_bytes,
        frames_learners_reports_reads_allocations_retirements_equal=True,
        actual_cuda_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    original = original_observe()
    result = dict(status='PASS_LEDGER_PROJECTION_CPU', baseline_source=BASELINE, scope=__doc__.strip())
    for name, action in (('histories', lambda: paired_histories(original)),
        ('barrier_failures', lambda: barrier_failures(original)),
        ('storage_failures', storage_failures), ('cpu_phases', lambda: cpu_phases(original))):
        result[name] = action()
        print('PASS '+name, flush=True)
    import torch
    assert not torch.cuda.is_initialized()
    if args.write:
        (ROOT/'evidence/minimal/FP_LEDGER_PROJECTION_CPU.json').write_text(
            json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    # Isolate this prior projection from later ingress/source refinements.
    from owned_admission_audit_support import historical_prediction_ports
    with historical_prediction_ports(BASELINE):
        main()
