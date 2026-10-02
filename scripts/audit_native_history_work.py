"""Count actual whole-history visits without timing, corpus or device claims.

Wrappers observe existing calls and delegate unchanged. Complete snapshot
equality against uninstrumented roots checks that the observer is passive.
"""
from collections import Counter
from contextlib import ExitStack
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, runtime as owner
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from fp_reference.resources import ResourceLedger
from audit_owned_token_learner import fixture, registration
from audit_shared_token_retention import STORAGE
from audit_reference_construction import limits


class Visits:
    def __init__(self):
        self.counts = Counter()
        self.callers = Counter()
        self.sources = []

    def install(self, stack):
        for name in ('snapshot', '_detached', '_residency'):
            original = getattr(ResourceLedger, name)
            def observe(ledger, *args, _name=name, _original=original, **kwargs):
                self.counts[_name+'_calls'] += 1
                caller = sys._getframe(1).f_code.co_name
                self.callers[_name+' <- '+caller] += 1
                if _name == 'snapshot':
                    self.counts['snapshot_event_rows'] += len(ledger._events)
                    self.counts['snapshot_object_rows'] += len(ledger._objects)
                    self.counts['snapshot_retired_ids'] += len(ledger._retired)
                elif _name == '_detached':
                    self.counts['detached_event_slots'] += len(ledger._events)
                    self.counts['detached_object_slots'] += len(ledger._objects)
                    self.counts['detached_ref_maps'] += len(ledger._refs)
                    self.counts['detached_retired_ids'] += len(ledger._retired)
                else:
                    self.counts['residency_object_rows'] += len(args[0])
                return _original(ledger, *args, **kwargs)
            stack.enter_context(patch.object(ResourceLedger, name, observe))
        original_read = owner.read_sources
        def observe_read(contract, cursor, inputs, history):
            assert type(history) is tuple and len(history) == cursor
            self.sources.append(cursor)
            # These are two separate loops in canonical source: tuple(list),
            # then the full contiguous/revealed-prefix check on success.
            self.counts['source_history_copied_slots'] += len(history)
            answer = original_read(contract, cursor, inputs, history)
            self.counts['source_history_checked_rows'] += len(history)
            return answer
        stack.enter_context(patch.object(owner, 'read_sources', observe_read))


def trajectory(word, shared, *, observed, unit, checkpoints=(), expected_snapshots=True):
    with patch('fp_reference.runtime.secrets.token_hex', return_value='history-work-control'):
        definition, initial = fixture(unit, 'mixed')
        cc, program, online = registration(definition, initial, count=len(word))
        cc = replace(cc, limits=limits(128 << 20, 10**15))
        rt = ReferenceCompilerRuntime(cc, program, online=online,
            shared_storage=STORAGE if shared else None)
        initial_events = len(rt._ledger._events)
        initial_objects = len(rt._ledger._objects)
        visits, samples = Visits(), []
        with ExitStack() as stack:
            if observed:
                visits.install(stack)
            for index, target in enumerate(word):
                predicted = rt.predict_next(f'train/{index}', encode_context(()))
                assert predicted.status == 'PREDICTED_REFERENCE', (index, predicted.reason)
                advanced = rt.observe(target)
                assert advanced.status == 'OBSERVED_REFERENCE', (index, advanced.reason)
                if observed and index+1 in checkpoints:
                    samples.append(dict(targets=index+1, counts=dict(visits.counts),
                        resource_events=len(rt._ledger._events), live_objects=len(rt._ledger._objects)))
        count = len(word)
        if observed:
            assert visits.sources == list(range(count))
            assert visits.counts['source_history_copied_slots'] == count*(count-1)//2
            assert visits.counts['source_history_checked_rows'] == count*(count-1)//2
            assert visits.callers['_detached <- prepare_allocation'] == count
            assert visits.callers['snapshot <- observe'] == (count if expected_snapshots else 0)
            # A successful prediction appends at least one information event
            # before its mandatory clone; history events are never truncated.
            assert visits.counts['detached_event_slots'] >= count*(initial_events+1)+count*(count-1)//2
            if expected_snapshots:
                assert visits.counts['snapshot_event_rows'] >= count*(initial_events+1)+count*(count-1)//2
            else:
                assert visits.counts['snapshot_event_rows'] == 0
        snapshot = rt.snapshot()  # outside the observer; no diagnostic counts
        assert (snapshot.cursor, len(snapshot.observations), len(snapshot.event_traces)) == (count, count, count)
        assert tuple(r.target for r in snapshot.observations) == word
        assert snapshot.halted is None
        return pack(snapshot), dict(storage='shared' if shared else 'packed', targets=count,
            unit=unit, initial_events=initial_events, initial_objects=initial_objects,
            counts=dict(visits.counts), callers=dict(visits.callers), checkpoints=samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checked = 0
    for shared, word in product((False, True), product((0, 1), repeat=4)):
        original, _ = trajectory(word, shared, observed=False, unit=2)
        observed, _ = trajectory(word, shared, observed=True, unit=2)
        assert original == observed
        checked += 1
    growth = []
    for shared in (False, True):
        word = (0, 1, 1, 0)*16
        original, _ = trajectory(word, shared, observed=False, unit=512)
        observed, counts = trajectory(word, shared, observed=True, unit=512, checkpoints=(8, 16, 32, 64))
        assert original == observed
        growth.append(counts)
        checked += 1
    horizon = 1 << 20
    result = dict(status='PASS_NATIVE_HISTORY_WORK_CPU', scope=__doc__.strip(),
        paired_complete_histories=checked, entire_serialized_snapshots_equal=True,
        growth=growth, full_horizon_source_law=dict(targets=horizon,
            copied_history_slots=horizon*(horizon-1)//2,
            checked_history_rows=horizon*(horizon-1)//2,
            extra_context_work_not_included=True, source_derivation_not_full_horizon_execution=True),
        no_timing_throughput_or_full_budget_claim=True, no_actual_cuda_or_corpus=True)
    result['control_allowances'] = dict(reference_payload_bytes=128 << 20, work_per_role=10**15)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_NATIVE_HISTORY_WORK_CPU.json').write_text(
            json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions are required')
    # This audit's recorded law concerns the original observe diagnostic.
    # Reproduce that exact method, including its existing public/host guard.
    from ledger_projection_audit_support import original_observe
    from owned_admission_audit_support import historical_prediction_ports
    with historical_prediction_ports('364934d'), \
            patch.object(ReferenceCompilerRuntime, 'observe', original_observe()):
        main()
