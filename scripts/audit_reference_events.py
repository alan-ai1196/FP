"""Exact adversarial audit of the public Runtime's owned causal continuation.

Independent forward differentials audit reverse CE derivatives. Exhaustive
short streams audit actual endpoint clocks/values, not a helper imitation.
The fixed value-reachability fixture is reused; no new static case is claimed.
"""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys
from unittest.mock import patch
import importlib
import pkgutil

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'theory/numerical_checks')]

from ingress_audit_support import deliver_context
from fp_reference import OnlineContract, ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.info import Moment, QuerySpec, quantize
from fp_reference.learner import LearnerSpec, ce_gradient
from fp_reference.machine import pack
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, SemanticRules, Source, SourceSpec, State, Sum, Term
from fp_reference.resources import ObjectSpec, ResourceExceeded, ResourceLedger
from fp_reference.semantics import evaluate
import fp_reference.runtime as execution
import fp_reference
from audit_reference_construction import contract, domain, limits, rejects, semantic_rules, validate_residency, zero_program
from value_reachability_audit import GAP, floor_dyadic, loss_upper, step


def online(cfg, count, *, unit=2, rate=F(1), grid=24, queries=()):
    ids = tuple(f'observation-{i}' for i in range(count))
    streams = (StreamSpec('ordinary', 'online', ids), StreamSpec('holdout', 'test', ('test-label',)))
    reads = tuple(SourceRead(s.source_id, 'input', i, 0) for i, s in enumerate(cfg.semantics.sources))
    data = DataContract(streams, 'ordinary', tuple(s.upper for s in cfg.semantics.sources), reads)
    return OnlineContract(data, LearnerSpec(unit, rate, grid), queries)


def forward_oracle(graph, rules, theta, inputs, delayed=()):
    """Independent forward-mode differentiation on every slot, including zero."""
    zero = (F(0),)*graph.slot_count
    value, deriv = [], []
    old = dict(delayed)
    for node in graph.nodes:
        if type(node) is Source:
            v, dv = inputs[node.source_id], zero
        elif type(node) is State:
            v, dv = old[node.state_id][0], zero
        elif type(node) is Sum:
            v, dv = F(0), [F(0)]*graph.slot_count
            for edge in node.terms:
                v += theta[edge.slot]*value[edge.parent]
                for slot in range(graph.slot_count):
                    dv[slot] += theta[edge.slot]*deriv[edge.parent][slot]
                dv[edge.slot] += value[edge.parent]
            dv = tuple(dv)
        else:
            v = value[node.left]*value[node.right]
            dv = tuple(value[node.left]*b+value[node.right]*a
                       for a, b in zip(deriv[node.left], deriv[node.right]))
        value.append(v)
        deriv.append(dv)
    masses = tuple(b+value[h] for b, h in zip(rules.base, graph.heads))
    total = sum(masses)
    total_deriv = tuple(sum(deriv[h][slot] for h in graph.heads) for slot in range(graph.slot_count))
    gradients = tuple(tuple(total_deriv[slot]/total-deriv[head][slot]/masses[y]
                            for slot in range(graph.slot_count)) for y, head in enumerate(graph.heads))
    return tuple(m/total for m in masses), gradients


def random_gradient_audit():
    rng = random.Random(2026091206)
    rules = semantic_rules(2, 3)
    theta = (F(0), F(1, 3), F(2), F(1, 7))
    checks = 0
    for _ in range(80):
        nodes = [Source(s.source_id) for s in rules.sources]+[Sum('mass', ())]
        for _ in range(12):
            if rng.randrange(3) == 0:
                left = rng.randrange(len(nodes))
                right = left if rng.randrange(2) else rng.randrange(len(nodes))
                nodes.append(Product('mass', left, right))
            else:
                terms = tuple(Term(rng.randrange(len(nodes)), rng.randrange(3)) for _ in range(rng.randrange(5)))
                nodes.append(Sum('mass', terms))
        # Repeated heads too. Slot 3 is deliberately declared but unused.
        heads = tuple(rng.randrange(len(nodes)) for _ in range(3))
        graph = Program(tuple(nodes), 4, heads)
        for row in domain(2):
            inputs = dict(zip((s.source_id for s in rules.sources), row))
            probability, gradients = forward_oracle(graph, rules, theta, inputs)
            result = evaluate(graph, rules, theta, inputs, bit_limit=16384)
            assert result.probabilities == probability
            for target in range(3):
                assert ce_gradient(graph, theta, result, target, bit_limit=16384) == gradients[target]
                assert gradients[target][-1] == 0
                checks += 1
    return {'native_graphs': 80, 'independent_exact_gradient_vectors': checks,
            'zero_shared_repeated_and_unused_coordinates': True}


def shared_graph():
    return Program((Source('x0_0'), Source('x0_1'),
                    Sum('mass', (Term(0, 0), Term(1, 1), Term(0, 0))),
                    Product('mass', 2, 2),
                    Sum('mass', (Term(3, 1), Term(2, 0))),
                    Sum('mass', ())), 3, (4, 5))


def exhaustive_endpoint_audit():
    cfg = contract(pattern=(F(0), F(1, 3), F(0)), cap=100, peak=100)
    graph, events, commits = shared_graph(), 0, 0
    for sequence in product(product((0, 1), repeat=2), repeat=3):
        run = online(cfg, 3, unit=2, rate=F(1, 4))
        rt = ReferenceCompilerRuntime(cfg, graph, online=run)
        candidate = rt.construct_candidate(graph)
        assert candidate.status == 'BUILT_REFERENCE'
        expected = {s.candidate_id: (s.theta, (F(0),)*3, 0) for s in rt.snapshot().candidates}
        for cursor, (context, target) in enumerate(sequence):
            row = domain(1)[context]
            inputs = dict(zip((s.source_id for s in cfg.semantics.sources), row))
            forecast = deliver_context(rt, f'observation-{cursor}', row)
            assert forecast.status == 'PREDICTED_REFERENCE'
            for key, probabilities in forecast.predictions:
                theta, accumulated, steps = expected[key]
                p, gradients = forward_oracle(graph, cfg.semantics, theta, inputs)
                assert p == probabilities
                accumulated = tuple(a+b for a, b in zip(accumulated, gradients[target]))
                if (cursor+1) % 2 == 0:
                    theta = tuple(floor_dyadic(max(F(0), v-run.learner.learning_rate*g/2), 24)
                                  for v, g in zip(theta, accumulated))
                    accumulated, steps = (F(0),)*3, steps+1
                    commits += 1
                expected[key] = theta, accumulated, steps
            result = rt.observe(target)
            assert result.status == 'OBSERVED_REFERENCE'
            state = validate_residency(rt)
            assert state.cursor == cursor+1 and state.event_phase == 'idle'
            for branch in state.candidates:
                theta, accumulated, steps = expected[branch.candidate_id]
                assert branch.learner.theta == theta and branch.learner.gradient_sum == accumulated
                assert branch.learner.cursor == cursor+1 and branch.learner.unit_count == (cursor+1) % 2
                assert branch.learner.optimizer_steps == steps
            events += 1
        assert len(rt.snapshot().event_traces) == 6
    return {'complete_stream_class': 'all 4^3 context/target sequences; one shared native graph, two continuous reference lineages',
            'streams': 64, 'paired_events': events, 'individual_optimizer_commits': commits}


def clock_and_data_audit():
    query = QuerySpec('target-mean', (Moment((), 0), Moment(('x0_0',), 0)), (0, 0), (1, 1), 2, 8)
    cfg = contract(pattern=(F(0),), cap=100, peak=100)
    run = online(cfg, 6, unit=2, rate=F(1), grid=None, queries=(query,))
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    rt = ReferenceCompilerRuntime(cfg, graph, online=run)
    rejects(lambda: rt.observe(0))
    rejects(lambda: deliver_context(rt, 'test-label', (1, 0)))
    rejects(lambda: deliver_context(rt, 'observation-1', (1, 0)))
    rejects(lambda: rt.query('target-mean', ('observation-0',)))
    rejects(lambda: rt.query('missing', ('observation-0',)))
    rejects(lambda: rt.query('target-mean', ('observation-0',), fn=lambda: (F(1),)), TypeError)
    rejects(lambda: rt.predict_next('observation-0', b'', target=0), TypeError)
    p0 = deliver_context(rt, 'observation-0', (1, 0))
    before = rt.snapshot()
    rejects(lambda: deliver_context(rt, 'observation-0', (1, 0)))
    rejects(lambda: rt.construct_candidate(graph))
    rejects(lambda: rt.query('target-mean', ('observation-0',)))
    rejects(lambda: rt.observe(True))
    rejects(lambda: rt.observe(0, commit=True), TypeError)
    assert rt.snapshot() == before
    assert not rt.observe(0).committed
    state = rt.snapshot().candidates[0].learner
    assert state.theta == (F(0),) and state.gradient_sum == (F(-1, 2),)
    rejects(lambda: rt.construct_candidate(graph))  # no shortened newborn unit
    p1 = deliver_context(rt, 'observation-1', (1, 0))
    assert p1.predictions == p0.predictions  # target-derived accumulator is invisible
    assert rt.observe(0).committed
    assert rt.snapshot().candidates[0].theta == (F(1, 2),)
    assert rt.snapshot().event_traces[-1].after_observe.theta == (F(0),)
    assert rt.snapshot().event_traces[-1].after_commit.theta == (F(1, 2),)
    answer = rt.query('target-mean', ('observation-0', 'observation-1'))
    assert answer.status == 'ANSWERED' and answer.indices == (3, 3) and answer.values == (1, 1)
    assert rt.snapshot().data_uses[-1].purpose == 'proposal'
    rejects(lambda: rt.query('target-mean', ('test-label',)))
    rejects(lambda: rt.query('target-mean', ('observation-0', 'observation-0')))
    rejects(lambda: deliver_context(rt, 'observation-0', (1, 0)))
    new_graph = replace(graph, nodes=graph.nodes+(Sum('mass', ()),))
    new = rt.construct_candidate(new_graph)
    assert new.status == 'BUILT_REFERENCE'
    candidate = next(s for s in rt.snapshot().candidates if s.candidate_id == new.candidate_id)
    assert candidate.birth_cursor == candidate.learner.cursor == 2 and candidate.theta == (0,)
    assert candidate.learner.gradient_sum == (0,) and candidate.learner.optimizer_steps == 0
    forecast = dict(deliver_context(rt, 'observation-2', (1, 0)).predictions)
    assert forecast[rt.snapshot().deployed_id] == (F(3, 5), F(2, 5))
    assert forecast[new.candidate_id] == (F(1, 2), F(1, 2))
    rt.observe(1)
    retained_traces = rt.snapshot().event_traces
    rt.retire_candidate(new.candidate_id)
    assert rt.snapshot().event_traces == retained_traces
    assert new_graph.program_id in dict(rt.snapshot().programs)
    retained_code = dict(rt.snapshot().retained_programs)[new_graph.program_id]
    assert retained_code in dict(rt.snapshot().buffers)
    assert candidate.physical_owner not in rt.snapshot().resources['objects'][retained_code]['references']
    validate_residency(rt)
    rejects(lambda: setattr(run.learner, 'update_unit', 1), FrozenInstanceError)
    rejects(lambda: replace(run.data, active_stream='holdout'))
    rejects(lambda: replace(run.data, streams=run.data.streams+(StreamSpec('renamed', 'train', ('observation-0',)),)))
    rejects(lambda: replace(run.data, access_id='query-only'))
    rejects(lambda: replace(run.data, stream_law='iid-because-unread'))
    before = rt.snapshot()
    assert rt.install(new.candidate_id, fresh=True, certified=True).status == 'UNRESOLVED'
    assert rt.snapshot() == before
    return {'target_accumulator_invisible_until_full_unit': True, 'no_caller_commit_or_query_callback': True,
            'immutable_roles_no_reused_or_future_ids': True, 'newborn_reset_at_common_boundary': True,
            'retired_lineage_trace_and_query_use_retained': True, 'no_stochastic_or_install_authorization': True}


def causal_history_audit():
    rules = SemanticRules((SourceSpec('current', 'mass', 0, 1), SourceSpec('past-input', 'mass', 2, 1),
                           SourceSpec('previous-y0', 'mass', 1, 1)), ('mass',), (('mass', 'mass', 'mass'),),
                          'mass', (1, 1), (DelayedStateSpec('h', 'mass', 2, 1),))
    cfg = replace(contract(source_domain=False, pattern=(F(0),)), semantics=rules)
    graph = Program((Source('current'), Source('past-input'), Source('previous-y0'), State('h')),
                    0, (3, 2), (Binding('h', 0),))
    streams = (StreamSpec('online', 'online', tuple(f'causal-{i}' for i in range(5))),)
    data = DataContract(streams, 'online', (F(1),), (SourceRead('current', 'input', 0, 0),
                         SourceRead('past-input', 'input', 0, 2), SourceRead('previous-y0', 'target_atom', 0, 1)))
    run = OnlineContract(data, LearnerSpec(1, 0))
    rt = ReferenceCompilerRuntime(cfg, graph, online=run)
    targets = (0, 1, 1, 0, 0)
    inputs = (1, 0, 1, 0, 0)
    rows = []
    for cursor in range(5):
        assert deliver_context(rt, f'causal-{cursor}', (inputs[cursor],)).status == 'PREDICTED_REFERENCE'
        pending = rt.snapshot().pending
        row = dict(pending.record.sources)
        assert row['past-input'] == (inputs[cursor-2] if cursor >= 2 else 0)
        assert row['previous-y0'] == (int(targets[cursor-1] == 0) if cursor else 0)
        prediction = pending.predictions[0][1]
        assert prediction.values[3] == (inputs[cursor-2] if cursor >= 2 else 0)
        rows.append(tuple(int(v) for _, v in pending.record.sources))
        assert rt.observe(targets[cursor]).status == 'OBSERVED_REFERENCE'
    validate_residency(rt)
    rejects(lambda: SourceRead('previous-y0', 'target_atom', 0, 0))
    bad = replace(data, source_reads=data.source_reads[:-1]+(SourceRead('previous-y0', 'target_atom', 0, 2),))
    rejects(lambda: ReferenceCompilerRuntime(cfg, graph, online=OnlineContract(bad, run.learner)))
    return {'exact_causal_source_rows': rows, 'positive_delayed_body_trace_checked': True,
            'current_target_and_mismatched_source_delay_rejected': True}


def query_precision_audit():
    count = 0
    for bits in range(1, 7):
        levels = (1 << bits)-1
        seen = set()
        # Every level and both boundaries of every quantization cell.
        for numerator in range(2*levels+1):
            value = F(numerator, 2*levels)
            index, decoded = quantize(value, F(0), F(1), bits, bit_limit=4096)
            distances = tuple(abs(value-F(j, levels)) for j in range(levels+1))
            nearest = [j for j, distance in enumerate(distances) if distance == min(distances)]
            expected = nearest[0] if len(nearest) == 1 else next(j for j in nearest if j % 2 == 0)
            assert index == expected and decoded == F(index, levels)
            seen.add(decoded)
            count += 1
        assert len(seen) == 1 << bits
    tiny = F(1, 1 << 1200)
    index, decoded = quantize(tiny, 0, 2*tiny, 3, bit_limit=8192)
    assert index == 4 and decoded == 8*tiny/7 and decoded > 0
    rejects(lambda: quantize(F(3, 2), 0, 1, 2, bit_limit=4096))
    rejects(lambda: quantize(float('nan'), 0, 1, 2, bit_limit=4096))
    cfg = contract(pattern=(F(0),))
    narrow = QuerySpec('narrow', (Moment((), 0),), (0,), (F(1, 4),), 3, 2)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=online(cfg, 2, queries=(narrow,)))
    deliver_context(rt, 'observation-0', (1, 0))
    rt.observe(0)
    before = rt.snapshot().resources['spent']['compiler']['work']
    result = rt.query('narrow', ('observation-0',))
    assert result.status == 'UNRESOLVED' and not result.values
    assert rt.snapshot().data_uses[-1].purpose == 'proposal'
    assert rt.snapshot().resources['spent']['compiler']['work'] > before
    with patch.object(execution, 'evaluate_query', side_effect=RuntimeError('query backend failed')):
        rejects(lambda: rt.query('narrow', ('observation-0',)), RuntimeError)
    assert rt.snapshot().queries[-1].result.status == 'EXECUTION_FAILED'
    assert rt.snapshot().data_uses[-1].purpose == 'proposal'
    validate_residency(rt)
    return {'exact_level_and_tie_cases': count, 'sub_binary64_rational_range_preserved': True,
            'failed_query_keeps_data_use_and_work': True}


def failure_audit():
    cfg = contract(pattern=(F(0),), cap=100, peak=100)
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    run = online(cfg, 4, unit=1)
    rt = ReferenceCompilerRuntime(cfg, graph, online=run)
    assert rt.construct_candidate(graph).status == 'BUILT_REFERENCE'
    deliver_context(rt, 'observation-0', (1, 0))
    before = rt.snapshot()
    original, calls = execution.observe_event, []

    def fail_second(*args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError('candidate backend failed after deployed successor was built')
        return original(*args, **kwargs)

    with patch.object(execution, 'observe_event', side_effect=fail_second):
        rejects(lambda: rt.observe(0), RuntimeError)
    after = validate_residency(rt)
    assert len(calls) == 2 and after.candidates == before.candidates and after.cursor == before.cursor
    assert after.event_phase == 'halted' and after.pending.record.target == 0
    assert after.observations[-1].target == 0 and after.data_uses[-1].purpose == 'ordinary'
    assert dict(after.buffers)[after.pending.target_object_id] == pack(rt._target_slot(0))
    assert dict(before.buffers)[before.pending.target_object_id] == pack(rt._target_slot(None))
    assert after.resources['spent']['deployment']['work'] > before.resources['spent']['deployment']['work']
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert after.resources['peak']['reference_payload_bytes'] >= before.resources['peak']['reference_payload_bytes']
    rejects(lambda: rt.observe(1))
    rejects(lambda: deliver_context(rt, 'observation-1', (1, 0)))
    rejects(lambda: rt.construct_candidate(graph))
    rejects(lambda: rt.retire_candidate(after.candidates[1].candidate_id))
    assert rt.install(after.candidates[1].candidate_id, bridge=True).status == 'UNRESOLVED'

    # Actual ordinary optimizer leaves the declared range. It is not silently
    # clipped to the range, rolled back and retried, or classified globally bad.
    tight = replace(cfg, normalizer_cap=F(2), activation_cap=F(1))
    ranged = ReferenceCompilerRuntime(tight, graph, online=run)
    deliver_context(ranged, 'observation-0', (1, 0))
    assert ranged.observe(0).status == 'UNRESOLVED'
    stopped = validate_residency(ranged)
    assert stopped.event_phase == 'halted' and stopped.pending.record.target == 0
    assert stopped.candidates[0].theta == (0,)
    assert stopped.event_traces[-1].after_commit.theta == (F(1, 2),)

    # The target ingress has already been allocated and paid. Exhausting work
    # immediately after reveal cannot make that target disappear from Omega.
    full = ReferenceCompilerRuntime(cfg, graph, online=run)
    deliver_context(full, 'observation-0', (1, 0))
    spent = full.snapshot().resources['spent']['deployment']['work']
    lcaps = dict(cfg.limits.role_cumulative)
    lcaps['deployment'] = {'work': spent}
    capped = replace(cfg, limits=replace(cfg.limits, role_cumulative=lcaps))
    exhausted = ReferenceCompilerRuntime(capped, graph, online=run)
    assert deliver_context(exhausted, 'observation-0', (1, 0)).status == 'PREDICTED_REFERENCE'
    assert exhausted.observe(1).status == 'UNRESOLVED'
    assert exhausted.snapshot().pending.record.target == 1 and exhausted.snapshot().cursor == 0
    validate_residency(exhausted)

    # Real coexistence cap: construction and prediction fit, but the ordinary
    # successor cannot be built while the old state and event evidence remain.
    full = ReferenceCompilerRuntime(cfg, graph, online=run)
    deliver_context(full, 'observation-0', (1, 0))
    cap = full.snapshot().resources['peak']['reference_payload_bytes']
    constrained = replace(cfg, limits=limits(byte_cap=cap))
    memory = ReferenceCompilerRuntime(constrained, graph, online=run)
    assert deliver_context(memory, 'observation-0', (1, 0)).status == 'PREDICTED_REFERENCE'
    published = memory.snapshot().candidates
    assert memory.observe(0).status == 'UNRESOLVED'
    final = validate_residency(memory)
    assert final.candidates == published and final.pending.record.target == 0
    assert final.resources['peak']['reference_payload_bytes'] <= cap

    # A failed multi-owner release must be all-or-nothing before publication.
    ledger = ResourceLedger(limits())
    ledger.register_owner('a', 'compiler')
    ledger.register_owner('b', 'deployment')
    obj = ObjectSpec('shared', 'test', {'reference_payload_bytes': 1, 'physical_objects': 1}, 'fixture')
    ledger.allocate('a', (obj,))
    ledger.acquire('b', 'shared')
    before_ledger = ledger.snapshot()
    rejects(lambda: ledger.release_many((('a', 'shared', 1), ('b', 'shared', 2))))
    assert ledger.snapshot() == before_ledger
    ledger.release_many((('a', 'shared', 1), ('b', 'shared', 1)))
    assert ledger.snapshot()['current']['physical_objects'] == 0
    assert ledger.snapshot()['peak'] == before_ledger['peak']
    return {'candidate_backend_failure_keeps_both_published_states': True,
            'target_reveal_and_executed_costs_cannot_roll_back': True,
            'infeasible_optimizer_successor_halts_unresolved': True,
            'target_survives_post_reveal_work_exhaustion': True,
            'ordinary_successor_coexistence_exhaustion_preserves_target_and_incumbent': True,
            'atomic_multi_owner_release_checked': True}


def existing_reachability_fixture():
    cfg = contract(2, 2, cap=4, peak=2, pattern=(F(0),))
    cfg = replace(cfg, limits=limits(byte_cap=60_000_000, work_cap=10_000_000))
    graph = Program(tuple(Source(s.source_id) for s in cfg.semantics.sources)+(
        Product('mass', 1, 3), Product('mass', 1, 2),
        Sum('mass', (Term(4, 0),)), Sum('mass', (Term(5, 1),))), 2, (6, 7))
    # Repeated values at distinct declared deterministic stream positions.
    # This is 512 scored online events, not 16 fresh labels secretly recycled.
    stream = tuple((row, y) for row, ones in zip(domain(2), (2, 2, 3, 1)) for y in (0,)*(4-ones)+(1,)*ones)*32
    run = online(cfg, len(stream), unit=16, rate=F(16), grid=32)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    candidate = rt.construct_candidate(graph).candidate_id
    value, first = F(0), None
    for cursor, (row, target) in enumerate(stream):
        assert deliver_context(rt, f'observation-{cursor}', row).status == 'PREDICTED_REFERENCE'
        result = rt.observe(target)
        assert result.status == 'OBSERVED_REFERENCE', result
        if result.committed:
            value = floor_dyadic(step(value), 32)
            current = next(s for s in rt.snapshot().candidates if s.candidate_id == candidate)
            assert current.theta == (value, value)
            assert rt.snapshot().candidates[0].learner.optimizer_steps == (cursor+1)//16
            if loss_upper(value) < GAP and first is None:
                first = (cursor+1)//16
    assert first == 13
    final = validate_residency(rt)
    assert len(final.observations) == len({r.observation_id for r in final.observations}) == 512
    assert len(final.event_traces) == 1024 and len(final.data_uses) == 512
    return {'existing_theorem_fixture': 'XVII.5 direct PRODUCT, zero initializer, mean CE step 16, floor-to-2^-32 commits',
            'deterministic_online_events': 512, 'reference_lineages': 2, 'registered_update_units': 32,
            'independent_scalar_recurrence_matches_every_commit': True,
            'existing_scoped_CE_bound_first_crossing_unit': first,
            'last_shared_parameter': str(value),
            'scope_limit': 'not a stochastic persistence result, profile replay, unknown-population acquisition or AMP/install certificate'}


def audit():
    modules = tuple(info.name for info in pkgutil.iter_modules(fp_reference.__path__))
    for module in modules:
        importlib.import_module(f'fp_reference.{module}')
    assert not hasattr(importlib.import_module('fp_reference.proof'), 'ProofAuthority')
    assert not hasattr(importlib.import_module('fp_reference.bridge'), 'BridgeAuthority')
    return {'status': 'PASS', 'scope': 'actual public Runtime construction + exact ordinary online continuation and revealed-data queries',
            'all_current_modules_import': True, 'unsafe_historical_signers_exposed_by_current_package': False,
            'gradient_audit': random_gradient_audit(), 'exhaustive_endpoint': exhaustive_endpoint_audit(),
            'clock_data_boundaries': clock_and_data_audit(), 'causality': causal_history_audit(),
            'query_precision': query_precision_audit(), 'failure_prefixes': failure_audit(),
            'existing_value_path': existing_reachability_fixture(),
            'not_closed': ['complete ERC-1 run manifest and full host/device physical accounting',
                           'query-only hidden-information contracts and registered profile replay',
                           'complete grammar search and typed proof authority',
                           'stochastic filtration, fresh paired persistence and error allocation',
                           'certified float64 and actual AMP event bridge', 'atomic install and complete 47-gate release']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_EVENT_RUNTIME_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
