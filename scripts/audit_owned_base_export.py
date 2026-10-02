"""Exact public-export refinement and source-work counts, without timing claims.

The comparison uses the actual Git copier at 5c83725. Both arms retain the
same already-paid base fact; no weaker ownership checker or unowned cache.
Synthetic labels only. No corpus, device execution or complete budget claim.
"""
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import argparse
import gc
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import ReferenceCompilerRuntime, host_failure, public_values
from fp_reference import token_base_facts as facts
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.ingress import encode_context
from audit_reference_construction import limits, validate_residency
from audit_token_reporting import report_registration
from audit_shared_token_retention import STORAGE
from audit_public_value_boundary import wrappers

BASELINE = '5c83725'
CAP = 1 << 20


def historical_copy():
    path = 'src/reference_compiler/fp_reference/public_values.py'
    source = subprocess.check_output(['git', 'show', BASELINE+':'+path], cwd=ROOT, encoding='utf-8')
    module = ModuleType('fp_reference._owned_base_export_baseline')
    module.__package__ = 'fp_reference'
    exec(compile(source, 'git:'+BASELINE+':'+path, 'exec'), module.__dict__)
    return module.detached


@contextmanager
def visits(base):
    """Observe calls without substituting a source, array or numerical method."""
    assert sys.getprofile() is None
    leaves, count = {id(x) for x in base}, [0]
    def profile(frame, event, arg):
        if (event == 'call' and frame.f_code.co_name == 'visit'
                and frame.f_globals.get('__name__') in (public_values.__name__,
                    'fp_reference._owned_base_export_baseline')):
            item = frame.f_locals.get('item')
            if type(item) is F and id(item) in leaves:
                count[0] += 1
    sys.setprofile(profile)
    try:
        yield count
    finally:
        sys.setprofile(None)


def setup(mode='owned', unit=2, count=4, declaration=None):
    cc, program, online, report = declaration or report_registration(unit, count, 2)
    cc = replace(cc, limits=limits(256 << 20, 10**15))
    storage = None if mode == 'packed' else replace(STORAGE,
        token_invariant_bytes=CAP if mode == 'owned' else 0)
    return ReferenceCompilerRuntime(cc, program, online=online, reporting=report,
        shared_storage=storage), program


def histories(old_copy):
    pairs = events = report_events = before = after = 0
    for mode, unit, word in product(('packed', 'shared', 'owned'), (1, 2), product((0, 1), repeat=4)):
        answers, counters = [], []
        for old in (True, False):
            with (patch.object(host_failure, 'detached', old_copy) if old else nullcontext()), \
                    patch('fp_reference.runtime.secrets.token_hex', return_value='owned-base-export'):
                rt, program = setup(mode, unit)
                base = program.definition.output.base
                outputs, count = [], 0
                for i, target in enumerate(word):
                    with visits(base) as seen:
                        prediction = rt.predict_next(f'train/{i}', encode_context(()))
                    assert prediction.status == 'PREDICTED_REFERENCE'
                    assert seen[0] == (0 if mode == 'owned' and not old else 2*len(base))
                    count += seen[0]
                    outputs.append(prediction)
                    # Mutable wrappers still separate even when the base tuple
                    # legitimately keeps its previous cross-boundary identity.
                    assert not wrappers(prediction) & wrappers(rt._pending)
                    prediction.predictions[0][1].origin.__dict__['output'] = b'caller replacement'
                    outputs.append(rt.observe(target))
                    assert outputs[-1].status == 'OBSERVED_REFERENCE'
                    assert facts._ACTIVE.get() is None
                outputs.append(rt.begin_report())
                assert outputs[-1].status == 'REPORTING'
                for i, target in enumerate((1, 0)):
                    outputs.append(rt.predict_report(f'report/{i}'))
                    assert outputs[-1].status == 'PREDICTED_REPORT'
                    outputs.append(rt.observe_report(target))
                    assert outputs[-1].status in ('SCORED_REPORT', 'COMPLETE_REPORT')
                snapshot = validate_residency(rt)
                assert snapshot.cursor == len(word) and facts._ACTIVE.get() is None
                answers.append(pack((tuple(outputs), snapshot)))
                counters.append(count)
        assert answers[0] == answers[1]
        before += counters[0]
        after += counters[1]
        pairs += 1
        events += len(word)
        report_events += 2
    return dict(paired_complete_histories=pairs, training_events_per_arm=events,
        reporting_events_per_arm=report_events, complete_serialized_results_and_states_equal=True,
        exact_old_forecast_base_leaf_visits=before, exact_new_forecast_base_leaf_visits=after,
        inactive_owners_keep_full_walk=True, public_mutation_isolated=True)


def binding(old_copy):
    declaration = report_registration(count=4, report_count=2)
    rt, program = setup(declaration=declaration)
    disabled, _ = setup('shared', declaration=declaration)
    second, other_program = setup()
    base, other = program.definition.output.base, other_program.definition.output.base
    equal = tuple(list(base))
    assert base == equal and base is not equal and base is not other
    def copied(value, owner=None, function=public_values.detached):
        with visits(base) as count:
            result = function(value) if owner is None else facts.run_for(owner, function, value)
        return result, count[0]
    assert copied(base)[1] == len(base)
    assert copied(base, rt) == (base, 0)
    assert copied(equal, rt)[1] == len(base)
    assert copied(base, second)[1] == len(base)
    assert copied(base, disabled)[1] == len(base)
    wrapper = rt.contract
    wrapper.__dict__['extra'] = {'base': base, 'foreign': equal, 'mutable': [base]}
    graph = (base, base, wrapper, wrapper)
    expected = facts.run_for(rt, old_copy, graph)
    actual = facts.run_for(rt, public_values.detached, graph)
    assert pack(actual) == pack(expected)
    assert actual[0] is actual[1] is base and actual[2] is actual[3]
    assert not wrappers(graph) & wrappers(actual)
    actual[2].extra['mutable'].clear()
    assert wrapper.extra['mutable'] == [base]
    # A nested disabled Runtime shares this exact immutable source but must
    # mask the outer owner's fact through both its method and its export.
    def outer():
        assert facts.positive_base_known(base)
        with visits(base) as count:
            exported = disabled.contract
        assert exported.initializer_pattern.output.base is base and count[0] == len(base)
        assert facts.positive_base_known(base)
        return count[0]
    assert facts.run_for(rt, outer) == len(base)
    assert facts._ACTIVE.get() is None
    cycle = [base]
    cycle.append(cycle)
    for value in ((base, object()), cycle):
        try:
            facts.run_for(rt, public_values.detached, value)
        except ContractError:
            pass
        else:
            raise AssertionError('owned base hid unsupported or cyclic metadata')
        assert facts._ACTIVE.get() is None
    return dict(exact_source_identity_only=True, equal_foreign_and_passive_values_walk=True,
        complete_extra_metadata_and_internal_aliases_preserved=True,
        all_mutable_nodes_detached=True, disabled_nested_owner_masks_export=True,
        cyclic_and_foreign_metadata_refused=True)


def failures():
    cases = []
    original_run, active = facts.run_for, facts._ACTIVE
    class FailAfterSet:
        def get(self):
            return active.get()
        def set(self, value):
            active.set(value)
            raise MemoryError('after export context binding')
        def reset(self, token):
            raise AssertionError('allocating scope cleanup')
    for port, stage in product(('contract', 'snapshot', 'predict_next', 'observe'), ('before-context', 'after-binding')):
        rt, _ = setup()
        if port == 'observe':
            assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
        captured = []
        wanted = dict(contract='ConstructionContract', snapshot='RuntimeSnapshot',
                      predict_next='PredictionResult', observe='ObservationResult')[port]
        def fail_export(owner, operation, *args, **kwargs):
            if (owner is rt and operation is public_values.detached and facts._ACTIVE.get() is None
                    and type(args[0]).__name__ == wanted):
                captured.append(pack(rt._ledger.snapshot()))
                hook = (patch.object(facts, 'copy_context', side_effect=MemoryError('before export context'))
                        if stage == 'before-context' else patch.object(facts, '_ACTIVE', FailAfterSet()))
                with hook:
                    return original_run(owner, operation, *args, **kwargs)
            return original_run(owner, operation, *args, **kwargs)
        with patch.object(facts, 'run_for', fail_export):
            try:
                if port in ('contract', 'snapshot'):
                    _ = rt.contract if port == 'contract' else rt.snapshot()
                elif port == 'predict_next':
                    rt.predict_next('train/0', encode_context(()))
                else:
                    rt.observe(1)
            except MemoryError:
                pass
            else:
                raise AssertionError('export context allocation did not fail: '+port)
        assert len(captured) == 1 and facts._ACTIVE.get() is None
        assert pack(rt._ledger.snapshot()) == captured[0]  # No rollback/refund.
        assert rt._halted is host_failure.HOST_ALLOCATION_FAILURE and rt._event_phase == 'halted'
        snapshot = rt.snapshot()
        assert snapshot.cursor == int(port == 'observe')
        if port == 'observe':
            assert snapshot.observations[-1].target == 1
        try:
            rt.predict_next('train/1', encode_context(()))
        except ContractError:
            pass
        else:
            raise AssertionError('failed export regained continuation authority')
        cases.append((port, stage))
    return dict(terminal_actual_prefix_failures=cases, resource_events_and_debits_not_refunded=True,
        revealed_target_and_completed_cursor_retained=True, parent_context_restored_without_reset=True)


def full_vocabulary(old_copy):
    from fp_reference import encoding
    from fp_reference.shared_reference import _compare_stream
    from run_native_text_a1 import registration, complete_residency
    roots, counts = [], []
    for old in (True, False):
        with (patch.object(host_failure, 'detached', old_copy) if old else nullcontext()), \
                patch('fp_reference.runtime.secrets.token_hex', return_value='owned-base-export-full-v'):
            cc, program, online, storage, report = registration()
            rt = ReferenceCompilerRuntime(cc, program, online=online, shared_storage=storage, reporting=report)
            base, count = program.definition.output.base, 0
            assert len(base) == 50257 and rt._reference_archive.base_facts.source is base
            for i, target in enumerate((0, 1)):
                with visits(base) as seen:
                    assert rt.predict_next(f'train/{i}', encode_context(())).status == 'PREDICTED_REFERENCE'
                count += seen[0]
                assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            roots.append(rt)
            counts.append(count)
    assert counts == [2*2*50257, 0], counts
    left, right = roots
    assert complete_residency(left) == complete_residency(right)
    assert tuple(left._buffers) == tuple(right._buffers)
    assert all(left._buffers[key] == right._buffers[key] for key in left._buffers)
    a, b = left.snapshot(), right.snapshot()
    size = encoding.packed_size(a)
    _compare_stream((x.encode('utf-8', 'surrogatepass') for x in encoding.fragments(b, packed=True)),
        (x.encode('utf-8', 'surrogatepass') for x in encoding.fragments(a, packed=True)), size)
    del a, b
    gc.collect()
    return dict(synthetic_targets_per_arm=2, original_training_declaration=1048576,
        exact_old_forecast_base_leaf_visits=counts[0], exact_new_forecast_base_leaf_visits=counts[1],
        full_serialized_snapshot_bytes_compared=size, every_buffer_and_role_total_equal=True,
        historical_full_training_source_count=2*1048576*50257,
        no_timing_or_full_host_budget_claim=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('assertions are required')
    old = historical_copy()
    result = dict(status='PASS_OWNED_BASE_EXPORT_CPU', literal_copier_source=BASELINE, scope=__doc__.strip())
    for name, action in (('binding', lambda: binding(old)), ('failures', failures),
            ('histories', lambda: histories(old)), ('full_vocabulary', lambda: full_vocabulary(old))):
        result[name] = action()
        print('PASS '+name, flush=True)
    if args.output is not None:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
