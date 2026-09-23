"""Owned direct integer table storage, native continuations and adversarial gate."""
from contextlib import ExitStack
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy
from fp_reference import integer_partition_decoder as hist, integer_partition_amp as physical, indexed_amp as amp
from fp_reference.encoding import pack
from fp_reference.indexed_relation import IndexedRelation, bound_view
from fp_reference.semantics import ArithmeticUnresolved
from audit_indexed_source_binding import predict
from audit_reference_construction import rejects, validate_residency
import audit_indexed_runtime as reference
import audit_owned_histogram as gray
import integer_partition as prototype
import audit_packed_histogram_cuda as fixtures
from audit_count_histogram import oracle, state as count_state

BUDGET = hist.DirectPartitionAllowance(live_cells=1024, arithmetic=16384)
ORIGINAL_FIXTURE = reference.fixture


def fixture(*args, **kwargs):
    cfg, schema, online = ORIGINAL_FIXTURE(*args, **kwargs)
    return replace(cfg, indexed_histogram=BUDGET), schema, online


def enumeration():
    budget = replace(BUDGET, join_cells=32, live_cells=128, arithmetic=4096, span_cap=6)
    states = queries = words = half = maximum_compacted = 0
    sizes = {}
    for n in (2, 3, 4):
        with memoryview(bytearray(hist.workspace_bytes(budget, n=n))) as scratch:
            sizes[n] = len(scratch)
            for values in product((-1, 0, 1), repeat=n*(n-1)//2):
                before = count_state(n, values)
                states += 1
                for query in product(range(n), repeat=2):
                    plan = hist.prepare(before, query, budget, scratch, bit_limit=32768)
                    _, parts = oracle(before, query)
                    old = prototype.prepare(before, query)
                    assert plan.parts == parts == old.parts
                    assert plan.shape == old.shape and plan.maximum_integer_bits == old.maximum_integer_bits
                    assert plan.compacted_cells <= (n-1)*budget.live_cells
                    maximum_compacted = max(maximum_compacted, plan.compacted_cells)
                    width, _ = hist._layout(n, budget)
                    for y in (0, 1):
                        start = (budget.live_cells+y)*width
                        assert int.from_bytes(scratch[start:start+width], 'little') == parts[y]
                    arithmetic = amp._Arithmetic(32768)
                    raw, _ = physical._prediction_schedule(plan, amp.IndexedAmpState(before), arithmetic)
                    expected, trace = prototype.rounded_prediction(old)
                    assert raw == expected and tuple(arithmetic.trace) == trace
                    assert plan.output_cells == len(trace)+7
                    words += plan.output_cells
                    half += sum(width == 16 for _, width, _ in trace)
                    queries += 1
    assert states == 759 and queries == 11919
    return {'states': states, 'ordered_queries': queries, 'prediction_output_words': words,
        'half_words': half, 'maximum_compacted_cells': maximum_compacted, 'workspace_bytes_by_n': sizes,
        'independent_assignment_oracle_and_prototype_words_equal': True,
        'paid_partition_root_fields_checked': True}


def larger():
    rows = []
    for name, before, query in fixtures.fixtures():
        plan = hist.passive_plan(before, query, BUDGET)
        _, parts = fixtures.oracle(before, query)
        assert plan.parts == parts
        arithmetic = amp._Arithmetic(32768)
        actual, _ = physical._prediction_schedule(plan, amp.IndexedAmpState(before), arithmetic)
        expected, trace = prototype.rounded_prediction(prototype.prepare(before, query))
        assert actual == expected and tuple(arithmetic.trace) == trace
        rows.append({'case': name, 'n': before.n, 'positive_partitions': sum(bool(v) for v in plan.parts),
            'workspace_bytes': hist.workspace_bytes(BUDGET, n=before.n),
            'integer_envelope': plan.integer_envelope, 'compacted_cells': plan.compacted_cells,
            'prediction_outputs': plan.output_cells})
    return rows


def native_continuations():
    # Reuse the independent literal Program/Gamma/U and derivative comparisons.
    with patch.object(gray, 'BUDGET', BUDGET), patch.object(gray, 'fixture', fixture):
        result = gray.native_continuations()
    with patch.object(reference, 'fixture', fixture):
        result['owned_n256_profiles'] = reference.large_audit()
    return result


def closure():
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    models = {rt.snapshot().deployed_id: reference.literal(3)}
    for event in ((0, 1, 0), (1, 2, 0), (0, 2, 1)):
        reference.step(rt, schema, event, models)
    snapshot = validate_residency(rt)
    assert snapshot.run.status == 'SEALED_REFERENCE_STREAM' and not snapshot.run.closure.decisions
    assert snapshot.run.manifest.machine_id == hist.MODEL_ID
    assert snapshot.run.manifest.reference_arithmetic == 'indexed-literal-count-direct-partition-reference-v1'
    rejects(lambda: rt.construct_candidate(schema))
    return {'status': snapshot.run.status, 'events': snapshot.cursor, 'constructor_decisions': 0,
            'machine_id': snapshot.run.manifest.machine_id}


def funding_and_limits():
    cfg, schema, online = fixture(3, 3)
    planning = hist.construction_work(3, BUDGET)
    rows = []
    for name, cap in (('before-table-construction', planning-1), ('before-exact-partitions', planning)):
        denied = replace(cfg, limits=replace(cfg.limits, role_cumulative={
            'deployment': {'work': cap}, 'compiler': {'work': 10**14}}))
        rt = ReferenceCompilerRuntime(denied, schema, online=online)
        before = validate_residency(rt)
        with patch.object(hist, 'prepare' if cap < planning else 'reference',
                          side_effect=AssertionError('unfunded kernel entered')) as forbidden:
            outcome = predict(rt, schema, (0, 1))
        after = validate_residency(rt)
        assert outcome.status == 'UNRESOLVED' and not forbidden.called
        assert after.candidates == before.candidates and after.cursor == 0
        assert after.pending.record.target is None and not after.pending.predictions
        assert after.resources['spent']['deployment']['work'] == (0 if cap < planning else planning)
        rows.append({'case': name, 'status': outcome.status, 'unfunded_entries': 0})
    for name, budget, bits in (('span', replace(BUDGET, span_cap=1), 32768), ('integer', BUDGET, 1075)):
        rt = ReferenceCompilerRuntime(replace(cfg, indexed_histogram=budget, reference_integer_bits=bits), schema, online=online)
        for _ in range(2):
            assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
            assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        before = validate_residency(rt)
        assert predict(rt, schema, (0, 1)).status == 'UNRESOLVED'
        after = validate_residency(rt)
        key = next(k for k, _ in before.buffers if k.endswith(':histogram-storage'))
        assert dict(after.buffers)[key] == dict(before.buffers)[key]
        assert after.candidates == before.candidates and after.observations == before.observations
        assert after.cursor == 2 and after.pending.record.target is None
        rows.append({'case': name, 'status': 'UNRESOLVED', 'prior_full_events': 2,
                     'scratch_untouched_on_preflight_refusal': True})
    state = count_state(4, (1,)*6)
    plan = hist.passive_plan(state, (0, 1), BUDGET)
    shape = dict(plan.shape)
    caps = (('join_cells', shape['largest_join_cells']-1),
            ('live_cells', shape['peak_live_integer_cells']-1),
            ('arithmetic', shape['positive_multiplications']+shape['positive_additions']-1))
    for field, limit in caps:
        budget = replace(BUDGET, **{field: limit})
        with memoryview(bytearray([165])*hist.workspace_bytes(budget, n=4)) as scratch:
            before_bytes = bytes(scratch)
            rejects(lambda: hist.prepare(state, (0, 1), budget, scratch, bit_limit=32768), ArithmeticUnresolved)
            assert bytes(scratch) == before_bytes
    dense = count_state(16, (1,)*120)
    rejects(lambda: hist.passive_plan(dense, (0, 1), BUDGET), ArithmeticUnresolved)
    rejects(lambda: replace(cfg, indexed_order_search=True))
    size = hist.workspace_bytes(BUDGET, n=4)
    for scratch in (memoryview(bytearray(size-1)), memoryview(bytes(size)), memoryview(bytearray(size*2))[::2]):
        rejects(lambda: hist.prepare(state, (0, 1), BUDGET, scratch, bit_limit=32768))
        scratch.release()
    return {'runtime_refusals': rows, 'unchanged_preflight_table_refusals': [name for name, _ in caps],
            'dense_n16_width_refusal': 'UNRESOLVED', 'mixed_order_registration_refused': True,
            'wrong_workspace_refusals': 3}


def workspace_continuation():
    cfg, schema, online = fixture(3, 3)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online)
    key = next(k for k in rt._buffers if k.endswith(':histogram-storage'))
    owned = rt._buffers[key]
    original = hist.prepare
    visits, blocked, handles = [], [], []
    def no_resize(backing):
        try:
            backing.extend(b'x')
        except BufferError:
            blocked.append(True)
        else:
            raise AssertionError('wide table buffer grew behind its paid extent')
    def monitored(before, query, budget, borrowed, **kwargs):
        entries = [e for e in rt.snapshot().resources['events'] if str(e[-1]).endswith(':predict')]
        assert entries and dict(entries[-1][4])['work'] == hist.construction_work(schema.n, budget)
        assert borrowed is not owned and borrowed.obj is owned.obj
        if handles:
            no_resize(handles[-1])
        value = original(before, query, budget, borrowed, **kwargs)
        backing = borrowed.obj
        handles.append(backing)
        borrowed.release()
        no_resize(backing)
        visits.append(value.compacted_cells)
        return value
    with patch.object(hist, 'prepare', monitored):
        assert predict(rt, schema, (0, 1)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(0).status == 'OBSERVED_REFERENCE'
        prior = validate_residency(rt)
        saved = pack(prior.event_traces)
        assert predict(rt, schema, (1, 2)).status == 'PREDICTED_REFERENCE'
        assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    no_resize(handles[0])
    after = validate_residency(rt)
    assert pack(prior.event_traces) == saved and len(owned) == hist.workspace_bytes(BUDGET, n=3)
    assert after.candidates[0].learner.encoded.counts == (1, 0, -1)
    return {'paid_before_construction_compaction_counts': visits, 'blocked_resizes': len(blocked),
            'billed_and_actual_bytes': len(owned), 'old_history_unchanged': True}


def adversarial_plan():
    schema = IndexedRelation(3)
    before = amp.IndexedAmpState(count_state(3, (1, -1, 0)))
    sources = schema.source_row(1)
    with memoryview(bytearray(hist.workspace_bytes(BUDGET, n=3))) as scratch:
        kwargs = dict(output_cap=65536, budget=BUDGET, workspace=scratch, bit_limit=32768)
        plan = physical._prepare_prediction(schema, before, schema.rules(), sources, **kwargs)
        changes = [replace(plan, query=(1, 0)), replace(plan, span=plan.span+1),
            replace(plan, integer_envelope=plan.integer_envelope+1), replace(plan, maximum_integer_bits=0),
            replace(plan, compacted_cells=plan.compacted_cells+1), replace(plan, bit_limit=32767),
            replace(plan, parts=plan.parts[::-1]), replace(plan, parts=tuple(2*v for v in plan.parts)),
            replace(plan, parts=(plan.parts[0]+1, plan.parts[1])), replace(plan, query=(False, 1)),
            replace(plan, shape=((plan.shape[0][0], float(plan.shape[0][1])),)+plan.shape[1:]),
            replace(plan, before=replace(plan.before, cursor=plan.before.cursor+1))]
        for changed in changes:
            rejects(lambda: physical.check_prediction_plan(changed, schema, before, schema.rules(), sources, **kwargs))
        arithmetic = amp._Arithmetic(32768)
        raw, _ = physical._prediction_schedule(plan, before, arithmetic)
        tape = gray.operations(arithmetic)
        physical.check_prediction_execution(plan, before, raw, tape, bit_limit=32768)
        for k in range(7):
            changed = replace(raw, words=tuple(word ^ int(k == j) for j, word in enumerate(raw.words)))
            rejects(lambda: physical.check_prediction_execution(plan, before, changed, tape, bit_limit=32768))
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



def owned_bit_crossing_and_reversal():
    from fp_reference import packed_histogram_decoder as packed
    # A1 at 1 GiB refused observation 181. Retain it; this is a separately
    # declared 2-GiB continuation, with the same production code and work cap.
    retained = json.loads((ROOT/'evidence/minimal/FP_DIRECT_PARTITION_N256_REFERENCE_A1.json').read_text())
    assert retained['outcome'] == 'UNRESOLVED' and retained['at_cursor_before_target'] == 180
    assert retained['packed_cap'] == 1 << 30 and retained['pending_target'] == 1
    assert retained['reason'] == 'global coexistence exceeds reference_payload_bytes'
    cap = 2 << 30
    cfg, schema, online = fixture(256, 257, byte_cap=cap, work_cap=10**15)
    rt = ReferenceCompilerRuntime(cfg, schema, online=online, policy=CompilerPolicy(()))
    current = 0
    crossed = restored = False
    def forbidden(*args, **kwargs):
        raise AssertionError('direct partition continuation tried to expand worlds')
    with patch.object(reference.native, 'relation_graph', forbidden), \
            patch.object(IndexedRelation, 'materialize_program', forbidden), \
            patch.object(IndexedRelation, 'materialize_learner', forbidden):
        for cursor, target in enumerate((0,)*128+(1,)*128+(0,)):
            result = predict(rt, schema, (0, 1))
            assert result.status == 'PREDICTED_REFERENCE', result
            power = 9**abs(current)
            posterior0 = F(power if current >= 0 else 1, 1+power)
            expected = (1+8*posterior0)/10
            assert result.predictions[0][1] == (expected, 1-expected)
            before = rt.snapshot()
            state = before.candidates[0].learner.encoded
            assert state.counts == (current,)+(0,)*32639 and state.cursor == state.steps == cursor
            assert before.pending.record.target is None
            if cursor == 128:
                rejects(lambda: packed.passive_plan(state, (0, 1)), ArithmeticUnresolved)
                assert state.counts[0] == 128
                crossed = True
            if cursor == 256:
                assert result.predictions[0][1] == (F(1, 2), F(1, 2))
                restored = True
            outcome = rt.observe(target)
            if outcome.status != 'OBSERVED_REFERENCE':
                failed = validate_residency(rt)
                diagnostic = {'status': 'RETAINED_N256_REFERENCE_REFUSAL',
                    'scope': 'separately declared 2-GiB packed/10^15 work CPU continuation',
                    'at_cursor_before_target': cursor, 'received_target': target,
                    'outcome': outcome.status, 'reason': outcome.reason,
                    'published_cursor': failed.cursor,
                    'published_count': failed.candidates[0].learner.encoded.counts[0],
                    'pending_target': failed.pending.record.target if failed.pending else None,
                    'packed_cap': cap,
                    'packed_current': failed.resources['current']['reference_payload_bytes'],
                    'packed_peak': failed.resources['peak']['reference_payload_bytes'],
                    'spent_work': {role: dict(values) for role, values in failed.resources['spent'].items()},
                    'old_packed_cut_crossed': crossed, 'zero_forecast_restored': restored}
                output = ROOT/'evidence/minimal/FP_DIRECT_PARTITION_N256_REFERENCE_A2.json'
                serialized = json.dumps(diagnostic, indent=2)+'\n'
                with output.open('x', encoding='utf-8') as stream:
                    stream.write(serialized)
                raise AssertionError(json.dumps(diagnostic))
            current += 1-2*target
    after = validate_residency(rt)
    assert crossed and restored and after.cursor == 257
    assert after.candidates[0].learner.encoded.counts == (1,)+(0,)*32639
    assert after.run.status == 'SEALED_REFERENCE_STREAM' and not after.run.closure.decisions
    assert (1 << 30) < after.resources['peak']['reference_payload_bytes'] <= cap
    return {'n': 256, 'ordinary_events': after.cursor, 'full_count_coordinates': 32640,
        'packed_cap_bytes': cap, 'work_cap_per_role': 10**15,
        'prior_1_gib_refusal_retained': 'FP_DIRECT_PARTITION_N256_REFERENCE_A1.json',
        'old_packed_bit_cut_crossed': 128, 'zero_count_and_half_forecast_restored_at': 256,
        'paid_table_bytes': hist.workspace_bytes(BUDGET, n=256),
        'packed_peak_bytes': after.resources['peak']['reference_payload_bytes'],
        'status': after.run.status, 'constructor_decisions': 0}

SECTIONS = {'enumeration': enumeration, 'larger': larger, 'native': native_continuations,
            'closure': closure, 'funding': funding_and_limits, 'workspace': workspace_continuation,
            'adversarial': adversarial_plan, 'bit-reversal': owned_bit_crossing_and_reversal}


def run(section=None):
    report = {'status': 'PASS_OWNED_INTEGER_PARTITION_CPU', 'complete_audit': section is None,
        'scope': 'paid exact host base9 tables and native/RNE continuation; half/single readout; no actual CUDA or completeness claim'}
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
        output = ROOT/'evidence/minimal/FP_OWNED_INTEGER_PARTITION_CPU.json'
        assert not output.exists(), 'retain source-bound outcomes'
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
