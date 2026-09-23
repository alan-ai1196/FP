"""Owned histogram construction, exact continuation and adversarial audit.

CPU only. Actual CUDA, fresh physical installation and model streams require
their own source-bound jobs. No constructor-class completeness is asserted.
"""
from contextlib import ExitStack
from dataclasses import replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference import histogram_decoder as hist, histogram_amp as physical, indexed_amp as amp
from fp_reference import indexed_execution, runtime as owner, query_projection
from fp_reference.core import ContractError
from fp_reference.encoding import pack
from fp_reference.indexed_count import CountState
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance, bound_view
from fp_reference.semantics import ArithmeticUnresolved
from audit_indexed_source_binding import predict
from audit_reference_construction import rejects, validate_residency
from audit_indexed_owned_schedule import PORTS
import audit_indexed_runtime as reference
import count_histogram as prototype
from audit_count_histogram import oracle, state as count_state

BUDGET = hist.HistogramAllowance()
ORIGINAL_FIXTURE = reference.fixture


def fixture(*args, **kwargs):
    cfg, schema, online = ORIGINAL_FIXTURE(*args, **kwargs)
    return replace(cfg, indexed_histogram=BUDGET), schema, online


def operations(arithmetic):
    return tuple(('host-RNE32-ingress' if tag == 'constant' else
        'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
        for tag, width, word in arithmetic.trace)


def enumeration():
    states = queries = words = half = 0
    with memoryview(bytearray(hist.workspace_bytes(BUDGET))) as scratch:
        for n in (2, 3, 4):
            for values in product((-1, 0, 1), repeat=n*(n-1)//2):
                before = count_state(n, values)
                states += 1
                for query in product(range(n), repeat=2):
                    plan = hist.prepare(before, query, BUDGET, scratch, bit_limit=32768)
                    bins, parts = oracle(before, query)
                    assert plan.terms == bins and hist.exact_parts(plan) == parts
                    assert plan.incident_visits == (n-1)*((1 << (n-1))-1)
                    assert plan.term_count <= min(1 << (n-1), 2*(plan.span+1))
                    arithmetic = amp._Arithmetic(32768)
                    raw, _ = physical._prediction_schedule(plan, amp.IndexedAmpState(before), arithmetic)
                    expected, old, trace = prototype.rounded_prediction(before, query)
                    assert raw == expected and tuple(arithmetic.trace) == trace
                    assert plan.output_cells == old.output_cells == len(trace)+7
                    words += plan.output_cells
                    half += sum(width == 16 for _, width, _ in trace)
                    queries += 1
    assert states == 759 and queries == 11919
    return {'states': states, 'ordered_queries': queries, 'prediction_output_words': words,
        'half_words': half, 'independent_assignment_oracle_and_old_schedule_equal': True,
        'actual_histogram_bytes': hist.workspace_bytes(BUDGET)}


def point_state(actual, expected):
    assert actual.materialize(scalar_cap=10000, budget=BUDGET) == expected
    schema = IndexedRelation(actual.encoded.n)
    view = bound_view(schema, actual.encoded, (0, 1), budget=BUDGET)
    assert view.materialize_state(scalar_cap=10000) == expected


def native_continuations():
    entries = []
    def forbidden(*args, **kwargs):
        entries.append(True)
        raise AssertionError('retired plan producer entered the owned histogram path')
    with ExitStack() as stack:
        stack.enter_context(patch.object(reference, 'fixture', fixture))
        stack.enter_context(patch.object(reference, 'check_state', point_state))
        for obj, name in PORTS:
            stack.enter_context(patch.object(obj, name, forbidden))
        small = reference.small_audit()
        profile = reference.profile_audit()
        fresh = reference.persistence_audit()
    assert not entries
    return {'small': small, 'profiles': profile, 'fresh_reference': fresh,
        'retired_producer_calls': 0, 'complete_pending_and_committed_histogram_point_reads': True}


def closure():
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    models = {rt.snapshot().deployed_id: reference.literal(3)}
    for event in ((0, 1, 0), (1, 2, 0), (0, 2, 1)):
        reference.step(rt, schema, event, models)
    snapshot = validate_residency(rt)
    assert snapshot.run.status == 'SEALED_REFERENCE_STREAM' and not snapshot.run.closure.decisions
    assert snapshot.run.manifest.machine_id == hist.MODEL_ID
    assert snapshot.run.manifest.reference_arithmetic == 'indexed-literal-count-positive-exponent-histogram-reference-v1'
    rejects(lambda: rt.construct_candidate(schema))
    return {'status': snapshot.run.status, 'events': snapshot.cursor, 'constructor_decisions': 0,
            'machine_id': snapshot.run.manifest.machine_id}


def funding_and_limits():
    rows = []
    cfg, schema, online = fixture(3, 3)
    planning = hist.enumeration_work(3, BUDGET)
    for name, cap in (('before-enumeration', planning-1), ('before-exact-partitions', planning)):
        denied_cfg = replace(cfg, limits=replace(cfg.limits, role_cumulative={
            'deployment': {'work': cap}, 'compiler': {'work': 10**14}}))
        rt = ReferenceCompilerRuntime(denied_cfg, schema, online=online)
        before = validate_residency(rt)
        with patch.object(hist, 'prepare' if cap < planning else 'reference',
                          side_effect=AssertionError('unfunded kernel entered')) as forbidden:
            outcome = predict(rt, schema, (0, 1))
        after = validate_residency(rt)
        assert outcome.status == 'UNRESOLVED' and not forbidden.called
        assert after.candidates == before.candidates and after.cursor == 0
        assert after.pending.record.target is None and after.pending.record.sources and not after.pending.predictions
        assert after.resources['spent']['deployment']['work'] == (0 if cap < planning else planning)
        rows.append({'case': name, 'status': outcome.status, 'unfunded_entries': 0})
    for name, budget, bits in (('span', replace(BUDGET, span_cap=1), 32768),
                               ('integer', BUDGET, 1075)):
        bounded = replace(cfg, indexed_histogram=budget, reference_integer_bits=bits)
        rt = ReferenceCompilerRuntime(bounded, schema, online=online)
        for _ in range(2):
            assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        before = validate_residency(rt)
        outcome = predict(rt, schema, (0, 1))
        after = validate_residency(rt)
        assert outcome.status == 'UNRESOLVED' and after.cursor == 2
        assert after.candidates == before.candidates and after.observations == before.observations
        old = dict(before.buffers)
        key = next(k for k in old if k.endswith(':histogram-storage'))
        assert dict(after.buffers)[key] == old[key]
        assert after.pending.record.target is None and after.pending.record.sources
        rows.append({'case': name, 'status': outcome.status, 'prior_full_events': 2,
                     'scratch_untouched_on_preflight_refusal': True})
    rejects(lambda: fixture(17, 1), ArithmeticUnresolved)
    rejects(lambda: replace(cfg, indexed_order_search=True))
    before = count_state(3, (1, 0, 0))
    bad = (memoryview(bytearray(hist.workspace_bytes(BUDGET)-1)),
           memoryview(bytes(hist.workspace_bytes(BUDGET))),
           memoryview(bytearray(hist.workspace_bytes(BUDGET))).cast('I'))
    for scratch in bad:
        rejects(lambda: hist.prepare(before, (0, 1), BUDGET, scratch, bit_limit=32768))
        scratch.release()
    return {'runtime_refusals': rows, 'out_of_class_registration': 'UNRESOLVED',
            'mixed_order_registration_refused': True, 'wrong_workspace_refusals': len(bad)}


def workspace_continuation():
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    key = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    owned = rt._buffers[key]
    original = hist.prepare
    visits, blocked, handles = [], [], []
    def no_resize(backing, label):
        try:
            backing.extend(b'x')
        except BufferError:
            blocked.append(label)
        else:
            raise AssertionError('histogram scratch grew behind its paid extent')
    def monitored(before, query, budget, borrowed, **kwargs):
        current = rt.snapshot()
        entries = [e for e in current.resources['events'] if str(e[-1]).endswith(':predict')]
        assert entries and dict(entries[-1][4])['work'] == hist.enumeration_work(schema.n, budget)
        assert borrowed is not owned and borrowed.obj is owned.obj
        if handles:
            no_resize(handles[-1], 'later-call')
        value = original(before, query, budget, borrowed, **kwargs)
        backing = borrowed.obj
        handles.append(backing)
        borrowed.release()
        no_resize(backing, 'after-borrow-release')
        visits.append(value.world_visits)
        return value
    with patch.object(hist, 'prepare', monitored):
        assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        prior = validate_residency(rt)
        saved = pack(prior.event_traces)
        assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    no_resize(handles[0], 'after-all-calls')
    after = validate_residency(rt)
    assert pack(prior.event_traces) == saved and len(owned) == hist.workspace_bytes(BUDGET)
    assert after.candidates[0].learner.encoded.counts == (1, 0, -1)
    return {'paid_before_enumeration': visits, 'blocked_resizes': blocked,
            'billed_and_actual_bytes': len(owned), 'old_history_unchanged': True}


def adversarial_plan():
    schema = IndexedRelation(3)
    before = amp.IndexedAmpState(count_state(3, (1, -1, 0)))
    sources = schema.source_row(1)
    with memoryview(bytearray(hist.workspace_bytes(BUDGET))) as scratch:
        kwargs = dict(output_cap=65536, budget=BUDGET, workspace=scratch, bit_limit=32768)
        plan = physical._prepare_prediction(schema, before, schema.rules(), sources, **kwargs)
        changes = [replace(plan, query=(1, 0)), replace(plan, span=plan.span+1),
            replace(plan, world_visits=plan.world_visits+1), replace(plan, incident_visits=0),
            replace(plan, bit_limit=32767), replace(plan, terms=plan.terms[::-1]),
            replace(plan, before=replace(plan.before, cursor=plan.before.cursor+1)),
            replace(plan, query=(False, 1))]
        for changed in changes:
            rejects(lambda: physical.check_prediction_plan(changed, schema, before, schema.rules(), sources, **kwargs))
        arithmetic = amp._Arithmetic(32768)
        raw, _ = physical._prediction_schedule(plan, before, arithmetic)
        tape = operations(arithmetic)
        physical.check_prediction_execution(plan, before, raw, tape, bit_limit=32768)
        for k in range(7):
            words = tuple(word ^ int(k == j) for j, word in enumerate(raw.words))
            rejects(lambda: physical.check_prediction_execution(plan, before, replace(raw, words=words), tape, bit_limit=32768))
        for k, (tag, width, (word,)) in enumerate(tape):
            changed = tape[:k]+((tag, width, (word ^ 1,)),)+tape[k+1:]
            rejects(lambda: physical.check_prediction_execution(plan, before, raw, changed, bit_limit=32768))
        for changed in (tape[:-1], tape+tape[-1:]):
            rejects(lambda: physical.check_prediction_execution(plan, before, raw, changed, bit_limit=32768))
        rejects(lambda: physical._prepare_prediction(schema, before, schema.rules(), sources,
            **{**kwargs, 'output_cap': plan.output_cells-1}), ArithmeticUnresolved)
    return {'full_plan_coordinate_refusals': len(changes), 'endpoint_bit_refusals': 7,
            'operation_bit_refusals': len(tape), 'trace_extent_refusals': 2,
            'one_short_output_cap': 'UNRESOLVED'}


def dense_continuation():
    cfg, schema, online = fixture(16, 121)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    for i, j in combinations(range(16), 2):
        assert predict(rt, schema, (i, j)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    before = validate_residency(rt)
    actual = before.candidates[0].learner.encoded
    assert actual.counts == (1,)*120 and actual.cursor == actual.steps == 120
    rejects(lambda: query_projection.prepare(actual, (0, 1), DecodeAllowance()), ArithmeticUnresolved)
    result = predict(rt, schema, (0, 1))
    assert result.status == 'PREDICTED_REFERENCE'
    _, parts = oracle(actual, (0, 1))
    expected = (1+8*F(parts[0], sum(parts)))/10
    assert result.predictions[0][1][0] == expected
    view = bound_view(schema, actual, (0, 1), budget=BUDGET)
    assert view.probability(0) == expected
    assert sum(view.theta(slot) for slot in range(1, schema.K+1)) == 1
    prediction = rt.snapshot().pending.predictions[0][1]
    assert dict(prediction.table_work)['histogram_terms'] == 17
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    after = validate_residency(rt)
    assert after.candidates[0].learner.encoded.counts == (0,)+(1,)*119
    assert after.cursor == 121
    return {'events': 121, 'complete_counts': 120, 'independent_world_terms': 32768,
            'old_join_class': 'UNRESOLVED', 'owned_final_histogram_terms': 17,
            'exact_forecast': str(expected), 'all_theta_slots_sum': '1',
            'continued_native_update': True}


SECTIONS = {'enumeration': enumeration, 'native': native_continuations, 'closure': closure,
            'funding': funding_and_limits, 'workspace': workspace_continuation,
            'adversarial': adversarial_plan, 'dense': dense_continuation,
            'legacy-n256': reference.large_audit}


def run(section=None):
    report = {'status': 'PASS_OWNED_HISTOGRAM_CPU', 'complete_audit': section is None,
        'scope': 'paid reference and passive full-coordinate AMP; actual owned CUDA gate still open'}
    for name, function in SECTIONS.items():
        if section in (None, name):
            report[name] = function()
            print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=tuple(SECTIONS))
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert args.section is None or not args.write
    report = run(args.section)
    if args.write:
        output = ROOT/'evidence/minimal/FP_OWNED_HISTOGRAM_CPU.json'
        assert not output.exists(), 'retain source-bound outcomes'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
