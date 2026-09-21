"""Indexed literal code and complete exact reference coordinates.

This passive representation has no Runtime, source-acquisition, ownership,
phase-evidence, initialization or installation authority. It indexes the
existing finite relation Program; it does not introduce a native constructor.
"""
from dataclasses import dataclass, field, replace
from fractions import Fraction as F
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
import count_learner_encoding as counts
import positive_frontier_decoder as frontier
import simplex_gradient as native
from fp_reference.core import ContractError, natural
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
                                  initial_state, observe_event, commit_event)
from fp_reference.profile import attach_boundary
from fp_reference.program import (Product, Program, SemanticRules, Source, SourceSpec,
                                  DelayedStateSpec, Sum, Term, rational)
from fp_reference.semantics import ArithmeticUnresolved, Evaluation, evaluate

from fp_reference.indexed_relation import (SCHEMA, MAX_N, index, allowance, NodeHeader, IndexedRelation,
    DecodeAllowance, partition_plan, partition_shape_plan, ReferenceView, bound_view)

def code_audit():
    rows = []
    limits = dict(node_cap=100_000, term_cap=2_000_000, slot_cap=65536)
    for n in range(2, 9):
        schema = IndexedRelation(n)
        rules, graph, worlds = native.relation_graph(n)
        gamma = (F(1),)+(F(1, len(worlds)),)*len(worlds)
        learner = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                              simplex_slots=tuple(range(1, len(worlds)+1)))
        schema.compare_literal(graph, rules, gamma, learner, **limits)
        assert schema.graph_counts() == graph.counts()
        assert all(tuple(schema.world_bit(k, v) for v in range(n)) == z for k, z in enumerate(worlds))
        terms = 0
        for k, node in enumerate(graph.nodes):
            h = schema.header(k)
            if type(node) is Sum:
                assert h == NodeHeader('SUM', arity=len(node.terms))
                for rank, term in enumerate(node.terms):
                    assert schema.term(k, rank) == term
                    terms += 1
            elif type(node) is Source:
                assert h == NodeHeader('SOURCE', source_id=node.source_id)
            else:
                assert h == NodeHeader('PRODUCT', parents=(node.left, node.right))
        for rank in range(n*n):
            assert schema.source_query(rules, schema.source_row(rank))[0] == divmod(rank, n)
        rows.append({'n': n, 'nodes': len(graph.nodes), 'ordered_SUM_terms': terms, 'slots': graph.slot_count})
    return rows


def phase_audit():
    totals = dict(boundary_states=0, native_caches=0, observed_states=0, committed_states=0)
    rows = []
    for n, depth in ((2, 3), (3, 2)):
        schema = IndexedRelation(n)
        rules, graph, _ = native.relation_graph(n)
        learner = schema.materialize_learner(slot_cap=64)
        gamma = tuple(schema.gamma(k) for k in range(schema.slot_count))
        initial = initial_state(graph, rules, gamma, 0, spec=learner, bit_limit=32768)
        alphabet = tuple(product(range(n), range(n), (0, 1)))
        level = [(initial, counts.initialize(n))]
        boundaries = transitions = 0
        for cut in range(depth+1):
            following = []
            for reference, encoded in level:
                assert bound_view(schema, encoded, (0, 0)).materialize_state(scalar_cap=100) == reference
                boundaries += 1
                totals['boundary_states'] += 1
                caches = {}
                for query in product(range(n), repeat=2):
                    actual = evaluate(graph, rules, reference.theta, native.context(n, *query), (), bit_limit=32768)
                    assert bound_view(schema, encoded, query).materialize_cache(scalar_cap=1000) == actual
                    caches[query] = actual
                    totals['native_caches'] += 1
                if cut == depth:
                    continue
                for i, j, y in alphabet:
                    observed = observe_event(graph, reference, learner, caches[i, j], y, bit_limit=32768)
                    pending = counts.observe(encoded, i, j, y)
                    # Deliberately bind another query: gradient belongs to the pending event.
                    assert bound_view(schema, pending, (j, 0)).materialize_state(scalar_cap=100) == observed
                    committed = commit_event(observed, learner, bit_limit=32768)
                    successor = counts.commit(pending)
                    assert bound_view(schema, successor, (i, j)).materialize_state(scalar_cap=100) == committed
                    following.append((committed, successor))
                    totals['observed_states'] += 1
                    totals['committed_states'] += 1
                    transitions += 1
            level = following
        rows.append({'n': n, 'depth': depth, 'boundary_histories': boundaries, 'transitions': transitions})
    return {'cases': rows, 'checks': totals}


def profile_audit():
    schema = IndexedRelation(3)
    rules, graph, _ = native.relation_graph(3)
    learner = schema.materialize_learner(slot_cap=64)
    checked = 0
    for passes in (1, 2, 3):
        reference, state = counts.native_initial(3), counts.initialize(3)
        for event in ((0, 1, 0), (1, 2, 1), (0, 2, 0))*passes:
            prediction = evaluate(graph, rules, reference.theta, native.context(3, *event[:2]), (), bit_limit=32768)
            reference = observe_event(graph, reference, learner, prediction, event[2], bit_limit=32768)
            state = counts.observe(state, *event)
            assert bound_view(schema, state, (2, 1)).materialize_state(scalar_cap=100) == reference
            reference = commit_event(reference, learner, bit_limit=32768)
            state = counts.commit(state)
            assert bound_view(schema, state, (2, 1)).materialize_state(scalar_cap=100) == reference
            checked += 2
        reference = attach_boundary(reference, 20, learner)
        state = counts.attach(state, 20)
        assert bound_view(schema, state, (1, 2)).materialize_state(scalar_cap=100) == reference
        checked += 1
    return {'profiles': 3, 'complete_state_comparisons': checked}


def schedule_audit():
    """All n4 active graphs, all free-variable orders and all ordered queries."""
    n = 4
    edges = tuple(combinations(range(n), 2))
    queries = tuple(product(range(n), repeat=2))
    checked = 0
    peak = dict(largest_join_cells=0, peak_live_integer_cells=0, positive_arithmetic=0)
    for mask in range(1 << len(edges)):
        signed = tuple((1 if e % 2 else -1) if mask >> e & 1 else 0 for e in range(len(edges)))
        state = counts.CountState(n, signed, None, mask.bit_count(), mask.bit_count())
        exact = frontier.enumeration(n, signed, queries)
        for order in permutations(range(n-1)):
            for query, expected in zip(queries, exact):
                plan = partition_plan(state, query, order, DecodeAllowance())
                parts, actual = frontier.decode(n, signed, query, order=order)
                assert parts == expected
                assert all(actual[key] == value for key, value in plan.items())
                for key in ('largest_join_cells', 'peak_live_integer_cells'):
                    peak[key] = max(peak[key], plan[key])
                peak['positive_arithmetic'] = max(peak['positive_arithmetic'],
                    plan['positive_multiplications']+plan['positive_additions'])
                checked += 1
    return {'active_graphs': 64, 'orders_per_graph': 6, 'ordered_queries_per_order': 16,
            'complete_plan_and_partition_comparisons': checked, 'maximum_logical_work': peak}


def refusal(function, exception=ContractError):
    try:
        function()
    except exception:
        return 1
    raise AssertionError('unsupported binding or unfunded read was accepted')


def boundary_audit():
    schema = IndexedRelation(3)
    rules, graph, _ = native.relation_graph(3)
    gamma = tuple(schema.gamma(k) for k in range(schema.slot_count))
    learner = schema.materialize_learner(slot_cap=64)
    limits = dict(node_cap=1000, term_cap=1000, slot_cap=64)
    swapped = list(graph.nodes)
    last = swapped[graph.heads[0]]
    swapped[graph.heads[0]] = Sum('mass', last.terms[::-1])
    retied = list(graph.nodes)
    retied[graph.heads[0]] = Sum('mass', (replace(last.terms[0], slot=2),)+last.terms[1:])
    mismatches = [
        (replace(graph, heads=graph.heads[::-1]), rules, gamma, learner),
        (replace(graph, nodes=tuple(swapped)), rules, gamma, learner),
        (replace(graph, nodes=tuple(retied)), rules, gamma, learner),
        (graph, replace(rules, base=(F(2), F(1))), gamma, learner),
        (graph, replace(rules, sources=rules.sources[::-1]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], source_id='renamed'),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], availability_delay=1),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, sources=(replace(rules.sources[0], upper=F(2)),)+rules.sources[1:]), gamma, learner),
        (graph, replace(rules, states=(DelayedStateSpec('extra', 'mass', 1, F(1)),)), gamma, learner),
        (graph, rules, (F(1), F(1, 2), F(1, 6), F(1, 6), F(1, 6)), learner),
        (graph, rules, gamma, replace(learner, learning_rate=F(1, 2))),
        (graph, rules, gamma, replace(learner, update_unit=2)),
        (graph, rules, gamma, replace(learner, simplex_slots=(1, 2, 3))),
        (graph, rules, tuple(float(v) for v in gamma), learner),
    ]
    binding = sum(refusal(lambda args=args: schema.compare_literal(*args, **limits)) for args in mismatches)
    soft = native.context(3, 0, 1)
    soft['x0:0'], soft['x0:1'] = F(1, 2), F(1, 2)
    state = counts.initialize(3)
    view = bound_view(schema, state, (0, 1))
    source = schema.source_row(1)
    invalid_sources = [soft, {**source, 'extra': F(0)}, {k: v for k, v in source.items() if k != 'x1:2'},
                       {**source, 'x0:0': 1.0}, {**source, 'x0:1': F(1)}]
    sources = sum(refusal(lambda values=values: ReferenceView.bind(schema, state, rules, values))
                  for values in invalid_sources)
    stale = sum(refusal(lambda other=other: view.require_binding(schema, other, rules, source)) for other in (
        replace(state, cursor=1), replace(state, steps=1), counts.observe(state, 0, 0, 0)))
    stale += refusal(lambda: view.require_binding(schema, state, rules, schema.source_row(3)))
    assert view.state == state and not view._partitions
    original = frontier.decode
    def forbidden(*args, **kwargs):
        raise AssertionError('a rejected preflight entered the numerical table decoder')
    frontier.decode = forbidden
    try:
        n = 16
        dense = counts.CountState(n, (1,)*(n*(n-1)//2), None, n*(n-1)//2, n*(n-1)//2)
        large = IndexedRelation(n)
        guarded = bound_view(large, dense, (0, 1), budget=DecodeAllowance(join_cells=1024))
        guards = refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
        assert not guarded._partitions
        small = IndexedRelation(2)
        tall = counts.CountState(2, (10**12,), None, 10**12, 10**12)
        guarded = bound_view(small, tall, (0, 1))
        guards += refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
        assert not guarded._partitions
        for budget in (DecodeAllowance(live_cells=1), DecodeAllowance(arithmetic=1), DecodeAllowance(integer_bits=5)):
            guarded = bound_view(schema, counts.commit(counts.observe(state, 0, 1, 0)), (0, 1), budget=budget)
            guards += refusal(lambda: guarded.theta(1), ArithmeticUnresolved)
            assert not guarded._partitions
    finally:
        frontier.decode = original
    cached = bound_view(schema, state, (0, 1))
    cached.partition((0, 1))
    indices = sum(refusal(function) for function in (
        lambda: bound_view(schema, state, (0, 3)),
        lambda: schema.world_bit(True, 0), lambda: schema.world_bit(schema.K, 0),
        lambda: schema.header(schema.graph_counts()['nodes']),
        lambda: schema.term(0, 0), lambda: schema.term(schema.first_indicator+1, 0),
        lambda: schema.term(schema.heads[0], 8*schema.K),
        lambda: schema.selected_slot(schema.K), lambda: view.theta(schema.slot_count),
        lambda: cached.partition((False, 1)),
        lambda: ReferenceView.bind(schema, state, rules, source, order=(0, 0)),
        lambda: IndexedRelation(MAX_N+1)))
    return {'literal_binding_refusals': binding, 'complete_source_refusals': sources,
            'stale_clock_pending_or_orientation_refusals': stale, 'preallocation_partition_refusals': guards,
            'invalid_index_order_or_prototype_refusals': indices}


def large_index_audit():
    n = 256
    schema = IndexedRelation(n)
    K = schema.K
    initial = counts.CountState(n, (0,)*(n*(n-1)//2), None, 0, 0)
    state = counts.commit(counts.observe(initial, 0, 1, 0))
    view = bound_view(schema, state, (0, 1))
    parts, stats = view.partition((0, 1))
    assert parts == (9*(K//2), K//2)
    slots = (1, 2, K//2, K//2+1, K)
    for slot in slots:
        expected = F(9 if schema.world_bit(slot-1, 1) == 0 else 1, 5*K)
        assert view.theta(slot) == expected
    assert view.value(schema.heads[0]) == F(36, 5)
    assert view.value(schema.heads[1]) == F(4, 5)
    assert view.probability(0) == F(41, 50) and view.probability(1) == F(9, 50)
    assert view.mass(0) == F(41, 5) and view.normalizer == 10 and view.delayed == ()
    # A diagonal has a nonzero full gradient even though committed d is unchanged.
    diagonal = counts.observe(state, 0, 0, 0)
    pending = bound_view(schema, diagonal, (1, 0))
    assert all(pending.gradient(slot) == F(-4, 45) for slot in (0,)+slots)
    assert (pending.unit_count, pending.cursor, pending.optimizer_steps) == (1, 2, 1)
    after = counts.commit(diagonal)
    assert after.counts == state.counts and after.steps == 2 and after.cursor == 2
    relative = counts.commit(counts.observe(after, 1, 2, 0))
    attached = counts.attach(relative, 20)
    final = bound_view(schema, attached, (1, 2))
    assert final.value(schema.heads[0]) == F(36, 5)
    assert (final.unit_count, final.cursor, final.optimizer_steps) == (0, 20, 3)
    for slot in slots:
        world = slot-1
        a, b = schema.world_bit(world, 1), schema.world_bit(world, 2)
        assert final.theta(slot) == F((9 if a == 0 else 1)*(9 if a == b else 1), 25*K)
    # Native orientation is retained in all source and pair cache coordinates.
    reverse = bound_view(schema, state, (1, 0))
    assert view.value(0) == 1 and reverse.value(0) == 0
    assert view.value(2*n+1) == 1 and reverse.value(2*n+1) == 0
    checks = 0
    for world in (0, 1, K//2, K-1):
        z = tuple(schema.world_bit(world, v) for v in range(n))
        for y in (0, 1):
            node = schema.first_indicator+2*world+y
            header = schema.header(node)
            expected = tuple((i, j) for i in range(n) for j in range(n) if z[i] ^ z[j] == y)
            assert header.arity == len(expected)
            for rank in sorted({0, header.arity//2, header.arity-1}) if header.arity else ():
                i, j = expected[rank]
                assert schema.term(node, rank) == Term(2*n+i*n+j, 0)
                checks += 1
        for y in (0, 1):
            for repetition in (0, 7):
                assert schema.term(schema.heads[y], 8*world+repetition) == Term(schema.first_indicator+2*world+y, world+1)
                checks += 1
    unopened = bound_view(schema, initial, (0, 1))
    refusals = sum(refusal(function, ArithmeticUnresolved) for function in (
        lambda: schema.materialize_program(node_cap=100_000, term_cap=2_000_000, slot_cap=65536),
        lambda: schema.materialize_node(schema.heads[0], term_cap=2_000_000),
        lambda: schema.materialize_learner(slot_cap=65536),
        lambda: unopened.materialize_state(scalar_cap=100_000),
        lambda: unopened.materialize_cache(scalar_cap=100_000)))
    assert unopened.state == initial and not unopened._partitions
    return {'n': n, 'logical_worlds_power_of_two': n-1, 'signed_count_coordinates': len(state.counts),
            'logical_nodes': '2^256 + 66050', 'logical_SUM_terms': '65552 * 2^255',
            'native_index_witnesses': checks, 'sampled_parameter_slots_per_state': len(slots),
            'actual_count_reference_commits': 3, 'profile_attachment_cursor': attached.cursor,
            'anchor_probability': str(view.probability(0)),
            'anchor_partition_integer_bits': max(v.bit_length() for v in (*parts, sum(parts))),
            'anchor_partition_work': stats, 'explicit_full_read_refusals': refusals,
            'scope': 'exact symbolic/reference execution; no large native Program or K-entry state is materialized'}


def audit():
    code = code_audit()
    phases = phase_audit()
    profiles = profile_audit()
    schedules = schedule_audit()
    boundaries = boundary_audit()
    # Keep the independent native builder unavailable during the large example.
    original = native.relation_graph
    def forbidden(_):
        raise AssertionError('large indexed execution tried to materialize a native world graph')
    native.relation_graph = forbidden
    try:
        large = large_index_audit()
    finally:
        native.relation_graph = original
    assert 'torch' not in sys.modules
    return {'schema': SCHEMA, 'exact_literal_code': code, 'native_phase_audit': phases,
            'profile_audit': profiles, 'schedule_audit': schedules,
            'boundary_audit': boundaries, 'large_index_audit': large,
            'scope': 'exact indexed G/Gamma/U and reference coordinates; no Runtime admission, AMP bridge, physical resource or completeness certificate'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit()
    encoded = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded, encoding='utf-8')
    print(encoded)
