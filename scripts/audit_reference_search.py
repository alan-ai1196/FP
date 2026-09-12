"""Independent finite grammar and actual Runtime reference-class proof audit.

No new static architecture family, population optimum or AMP authority is
inferred. The brute-force grammar does not use planner counts/ranks/cursors;
endpoint values use the existing independent forward differential oracle.
"""
from dataclasses import FrozenInstanceError, asdict, replace
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import argparse
import json
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'theory/numerical_checks')]

from ingress_audit_support import deliver_context
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.info import Moment, QuerySpec
from fp_reference.machine import pack
from fp_reference.native_search import GrammarAction, GrammarCursor, GrammarLimits
from fp_reference.profile import ProfileSpec
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, SemanticRules, Source, SourceSpec, State, Sum, Term
from fp_reference.proof import verify_maximum
from fp_reference.search import ReferenceSearchSpec, compare_likelihoods
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.native_search as grammar
import fp_reference.runtime as execution
from audit_reference_construction import contract, domain, limits, rejects, semantic_rules, validate_residency, zero_program
from audit_reference_events import forward_oracle, online
from audit_reference_profiles import ingest
from value_reachability_audit import floor_dyadic


def brute_grammar(rules, bounds):
    """Explicit finite Cartesian products; no production count/rank helpers."""
    result = []

    def visit(nodes, types, sums, products, edges, slots):
        roots = tuple(i for i, t in enumerate(types) if t == rules.readout_type)
        bodies = tuple(tuple(i for i, t in enumerate(types) if t == s.type_id) for s in rules.states)
        for body in product(*bodies):
            for order in permutations(range(len(rules.states))):
                bindings = tuple(Binding(rules.states[i].state_id, body[i]) for i in order)
                for heads in product(roots, repeat=len(rules.base)):
                    result.append(Program(nodes, slots, heads, bindings))
        if len(nodes) == bounds.nodes:
            return
        for source in rules.sources:
            visit(nodes+(Source(source.source_id),), types+(source.type_id,), sums, products, edges, slots)
        for state in rules.states:
            visit(nodes+(State(state.state_id),), types+(state.type_id,), sums, products, edges, slots)
        if sums < bounds.SUMs:
            for type_id in rules.sum_types:
                choices = tuple(Term(i, slot) for i, t in enumerate(types) if t == type_id for slot in range(slots))
                for arity in range(bounds.edges-edges+1):
                    for terms in product(choices, repeat=arity):
                        visit(nodes+(Sum(type_id, terms),), types+(type_id,), sums+1, products, edges+arity, slots)
        if products < bounds.PRODUCTs and edges+2 <= bounds.edges:
            for left_type, right_type, result_type in rules.product_rules:
                for i, left in enumerate(types):
                    for j, right in enumerate(types):
                        if left == left_type and right == right_type:
                            visit(nodes+(Product(result_type, i, j),), types+(result_type,), sums, products+1, edges+2, slots)

    for slots in range(bounds.slots+1):
        visit((), (), 0, 0, 0, slots)
    assert len(set(result)) == len(result)
    return tuple(result)


def checked_grammar(rules, bounds):
    cursor, result = GrammarCursor(), []
    while not cursor.done:
        action = grammar.plan(cursor, rules, bounds)
        successor, emitted = grammar.apply_checked(cursor, action, rules, bounds)
        assert successor.transitions == cursor.transitions+1
        assert successor.emitted == cursor.emitted+int(emitted is not None)
        if emitted is not None:
            emitted.validate(rules)
            result.append(emitted)
        cursor = successor
    assert grammar.apply_checked(cursor, GrammarAction('done'), rules, bounds) == (cursor, None)
    return tuple(result), cursor


def grammar_audit():
    scalar = semantic_rules(1, 2)
    typed = SemanticRules((SourceSpec('m', 'mass', 0, F(1)), SourceSpec('f', 'flag', 0, F(1))),
                          ('mass', 'flag'), (('mass', 'flag', 'mass'), ('flag', 'mass', 'flag'),
                                            ('mass', 'mass', 'flag')), 'mass', (F(1), F(1)))
    states = tuple(DelayedStateSpec(f's{i}', 'mass', i+1, F(1)) for i in range(3))
    missing_body = replace(scalar, states=(DelayedStateSpec('other', 'absent', 1, F(1)),))
    declarations = (
        ('empty', scalar, GrammarLimits(0, 0, 0, 0, 2)),
        ('scalar-compounds', scalar, GrammarLimits(3, 1, 1, 2, 0)),
        ('shared-PRODUCT-descendants', scalar, GrammarLimits(4, 1, 2, 4, 0)),
        ('repeated-edges-and-slots', scalar, GrammarLimits(2, 1, 1, 2, 2)),
        ('multiple-SUMs', scalar, GrammarLimits(3, 2, 0, 1, 1)),
        ('typed-products', typed, GrammarLimits(3, 1, 1, 2, 0)),
        ('binding-permutations', replace(scalar, states=states), GrammarLimits(1, 1, 0, 0, 1)),
        ('delayed-bodies', replace(scalar, states=states[:2]), GrammarLimits(2, 1, 0, 1, 0)),
        ('absent-body-type', missing_body, GrammarLimits(2, 1, 1, 2, 1)),
    )
    checked = []
    for name, rules, bounds in declarations:
        expected = brute_grammar(rules, bounds)
        actual, cursor = checked_grammar(rules, bounds)
        assert len(actual) == len(set(actual)) and set(actual) == set(expected), name
        assert cursor.emitted == len(actual)
        checked.append({'class': name, 'programs': len(actual), 'transitions': cursor.transitions})
    arithmetic = 0
    for base, exponent, cap in product(range(6), range(13), range(1, 21)):
        assert grammar._power(base, exponent, cap) == min(cap, base**exponent)
        assert grammar._geometric(base, exponent, cap) == min(cap, sum(base**i for i in range(exponent)))
        arithmetic += 2
    # Astronomical unvisited classes saturate without materializing exponents.
    assert grammar._power(2, 10**100, 7) == grammar._geometric(2, 10**100, 7) == 7
    assert grammar._geometric(0, 10**100, 7) == 1
    assert grammar._geometric(1, 10**100, 7) == 7
    assert grammar.output_count(GrammarCursor(nodes=(Source('x0_0'), Source('x0_1'))), missing_body, 1) == 0

    bounds, cursor = GrammarLimits(2, 1, 1, 2, 1), GrammarCursor()
    rejects(lambda: grammar.apply_checked(cursor, GrammarAction('close'), scalar, bounds))
    rejects(lambda: grammar.apply_checked(cursor, GrammarAction('done'), scalar, bounds))
    rejects(lambda: grammar.apply_checked(cursor, GrammarAction('descend', node=Source('x0_1')), scalar, bounds))
    cursor, _ = grammar.apply_checked(cursor, grammar.plan(cursor, scalar, bounds), scalar, bounds)
    rejects(lambda: grammar.apply_checked(cursor, GrammarAction('close'), scalar, bounds))
    rejects(lambda: grammar.apply_checked(cursor, GrammarAction('descend', node=Source('x0_0')), scalar, bounds))
    correct = grammar.plan(cursor, scalar, bounds)
    rejects(lambda: grammar.apply_checked(cursor, replace(correct, program=replace(correct.program, slot_count=1)), scalar, bounds))
    while grammar.output_count(cursor, scalar, 2) < 2 or cursor.frames[-1].next_output:
        cursor, _ = grammar.apply_checked(cursor, grammar.plan(cursor, scalar, bounds), scalar, bounds)
    skipped = GrammarAction('emit', program=grammar.output_at(cursor, scalar, 1))
    rejects(lambda: grammar.apply_checked(cursor, skipped, scalar, bounds))
    correct = grammar.plan(cursor, scalar, bounds)
    next_cursor, _ = grammar.apply_checked(cursor, correct, scalar, bounds)
    rejects(lambda: grammar.apply_checked(next_cursor, correct, scalar, bounds))
    return {'independent_complete_classes': checked, 'saturated_arithmetic_checks': arithmetic,
            'early_close_skip_repeat_wrong_slots_and_wrong_children_rejected': True,
            'no_function_gradient_support_or_binding_order_quotient': True}


SMALL = GrammarLimits(1, 1, 0, 0, 0)


def runtime_fixture(*, bounds=SMALL, cfg=None, profile=False, count=6, stream=None, initial=None,
                    objective_ids=('observation-0', 'observation-1')):
    cfg = contract(pattern=(F(1, 2),)) if cfg is None else cfg
    stream = tuple(zip(domain(1), (0, 1))) if stream is None else stream
    query = QuerySpec('retained-label', (Moment((), 1),), (F(0),), (F(1),), 2, count)
    run = online(cfg, count, unit=2, rate=F(1, 4), grid=8, queries=(query,))
    profile_spec = ProfileSpec('registered-profile', ('observation-0', 'observation-1'), 2)
    spec = ReferenceSearchSpec('native', bounds, objective_ids,
                               profile_spec.profile_id if profile else None)
    run = replace(run, profiles=(profile_spec,) if profile else (), searches=(spec,))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2) if initial is None else initial, online=run)
    ingest(rt, stream)
    return rt, spec


def finish(rt, result, chunks=(1, 37, 113)):
    calls = 0
    while next(s for s in rt.snapshot().searches if s.search_id == result.search_id).status == 'RUNNING':
        result = rt.advance_reference_search(result.search_id, transitions=chunks[calls % len(chunks)])
        calls += 1
        assert calls < 10000
    return result


def profile_theta_oracle(program, cfg, run, records, spec):
    theta = tuple(cfg.initializer_pattern[i % len(cfg.initializer_pattern)] for i in range(program.slot_count))
    if spec.profile_id is None:
        return theta, 0
    profile = next(p for p in run.profiles if p.profile_id == spec.profile_id)
    by_id = {r.observation_id: r for r in records}
    gradient, commits = (F(0),)*program.slot_count, 0
    for position, obs in enumerate(profile.observation_ids*profile.passes):
        record = by_id[obs]
        _, derivatives = forward_oracle(program, cfg.semantics, theta, dict(record.sources))
        gradient = tuple(a+b for a, b in zip(gradient, derivatives[record.target]))
        if (position+1) % run.learner.update_unit == 0:
            theta = tuple(floor_dyadic(max(F(0), v-run.learner.learning_rate*g/run.learner.update_unit),
                                       run.learner.commit_grid_bits) for v, g in zip(theta, gradient))
            gradient, commits = (F(0),)*program.slot_count, commits+1
    return theta, commits


def oracle_likelihood(program, cfg, learner, records):
    result = F(1)
    for record in records:
        probabilities, _ = forward_oracle(program, cfg.semantics, learner.theta, dict(record.sources), learner.delayed)
        result *= probabilities[record.target]
    return result


def assert_owned_search(rt, result):
    snapshot = validate_residency(rt)
    session = next(s for s in snapshot.searches if s.search_id == result.search_id)
    assert dict(snapshot.buffers)[session.object_id] == pack(session)
    assert session.owner in snapshot.resources['objects'][session.object_id]['references']
    assert session.expected_revision == snapshot.revision
    return snapshot, session


def runtime_audit():
    bounds = GrammarLimits(2, 1, 1, 2, 1)
    rt, spec = runtime_fixture(bounds=bounds, profile=True)
    before = rt.snapshot()
    result = rt.start_reference_search('native')
    assert result.status == 'UNRESOLVED' and result.programs_compared == 0 and result.proof_id is None
    snapshot, session = assert_owned_search(rt, result)
    assert session.cursor == GrammarCursor() and snapshot.cursor == before.cursor
    result = finish(rt, result)
    assert result.status == 'REFERENCE_CLASS_EXHAUSTED', result
    snapshot, session = assert_owned_search(rt, result)
    expected = set(brute_grammar(rt.contract.semantics, bounds))
    assert {row.program for row in session.rows} == expected and len(session.rows) == len(expected)
    records = tuple(r for r in snapshot.observations if r.observation_id in spec.observation_ids)
    scores, events, changed = [], 0, 0
    for ordinal, row in enumerate(session.rows):
        assert row.ordinal == ordinal and row.status == 'COMPARED_REFERENCE'
        theta, commits = profile_theta_oracle(row.program, rt.contract, rt.online_contract, records, spec)
        assert row.learner.theta == theta and row.learner.optimizer_steps == commits
        assert row.learner.cursor == before.cursor and row.learner.unit_count == 0
        assert row.likelihood == oracle_likelihood(row.program, rt.contract, row.learner, records)
        scores.append(row.likelihood)
        events += commits*rt.online_contract.learner.update_unit
        initial_theta = tuple(rt.contract.initializer_pattern[i % len(rt.contract.initializer_pattern)] for i in range(row.program.slot_count))
        changed += int(theta != initial_theta)
    assert changed > 0
    base = next(c for c in snapshot.candidates if c.candidate_id == session.base_lineage_id)
    assert base == before.candidates[0] and snapshot.cursor == before.cursor
    assert result.best_likelihood == max((session.base_likelihood, *scores))
    proof = rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id)
    assert proof.program_count == len(expected) and proof.best_likelihood == result.best_likelihood
    assert proof.kind == 'ordered-native-reference-class-and-baseline-optimum-v1'
    assert rt.verify_reference_class_proof(proof, decision_class_id=result.decision_class_id) == proof
    identical = replace(proof)
    assert identical is not proof and rt.verify_reference_class_proof(identical, decision_class_id=result.decision_class_id) == proof
    # Encoded proposition coordinates retain their declared types. Equality
    # between Python numeric types cannot stand in for identical proof data.
    for key in ('issued_revision', 'ordinary_cursor', 'program_count'):
        for wrong in (True, float(getattr(proof, key)), F(getattr(proof, key))):
            rejects(lambda key=key, wrong=wrong: replace(proof, **{key: wrong}))
    for wrong in (True, 1, float(proof.best_likelihood)):
        rejects(lambda wrong=wrong: replace(proof, best_likelihood=wrong))
    for key in ('proof_id', 'chi', 'runtime_id', 'search_id', 'decision_class_id',
                'base_lineage_id', 'winner_lineage_id'):
        rejects(lambda key=key: replace(proof, **{key: 1}))

    class EqualFraction(F):
        def __eq__(self, other):
            return True

    # Previously this represented likelihood 1, yet the public verifier
    # accepted it as equal to an issued 1/4 likelihood. No Runtime mutation or
    # patched solver is needed to expose the missing type validation.
    assert F(1, 4) == EqualFraction(1)
    rejects(lambda: replace(proof, best_likelihood=EqualFraction(1)))
    rejects(lambda: rt.verify_reference_class_proof(replace(proof, best_likelihood=F(1)), decision_class_id=result.decision_class_id))
    rejects(lambda: rt.verify_reference_class_proof(replace(proof, issued_revision=proof.issued_revision+1), decision_class_id=result.decision_class_id))
    rejects(lambda: rt.verify_reference_class_proof(proof, decision_class_id='another-class'))
    rejects(lambda: setattr(proof, 'kind', 'CERTIFIED_COMPLETE'), FrozenInstanceError)
    other, _ = runtime_fixture(bounds=bounds, profile=True)
    rejects(lambda: other.verify_reference_class_proof(proof, decision_class_id=result.decision_class_id))
    rejects(lambda: rt.advance_reference_search(result.search_id, transitions=1, cursor=replace(session.cursor, done=True)), TypeError)
    prior_install = rt.snapshot()
    assert rt.install(result.best_candidate_id, proof).status == 'UNRESOLVED' and rt.snapshot() == prior_install
    assert rt.query('retained-label', spec.observation_ids).status == 'ANSWERED'
    rejects(lambda: rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id))
    stale = rt.advance_reference_search(result.search_id, transitions=1)
    assert stale.status == 'UNRESOLVED' and stale.proof_id is None
    return {'complete_profile_constructor_programs': len(expected), 'actual_profile_events': events,
            'constructor_endpoints_changed_by_profile': changed,
            'independent_endpoint_and_likelihood_checks': len(expected),
            'all_rows_and_explicit_cursor_have_owned_packed_residency': True,
            'winner_likelihood': str(result.best_likelihood),
            'proof_field_types_and_identical_copies_checked_without_numeric_coercion': True,
            'typed_class_bound_proof_tamper_cross_runtime_staleness_and_install_checks': True}


def compound_audit():
    # This is one exhaustive Runtime audit, not a claim about unrestricted SUM
    # coefficients. The entire P=0 portion is an exact strong same-class baseline.
    bounds = GrammarLimits(3, 1, 1, 2, 0)
    rules = SemanticRules((SourceSpec('x', 'mass', 0, F(1)), SourceSpec('z', 'mass', 0, F(1))),
                          ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    cube = tuple(tuple(map(F, row)) for row in product((0, 1), repeat=2))
    cfg = replace(contract(cap=4, peak=1), semantics=rules, source_domain=cube)
    stream = tuple((row, int(row[0] != row[1])) for row in cube)
    rt, spec = runtime_fixture(bounds=bounds, cfg=cfg, count=6, stream=stream,
                               objective_ids=tuple(f'observation-{i}' for i in range(4)))
    result = finish(rt, rt.start_reference_search('native'), chunks=(211,))
    assert result.status == 'REFERENCE_CLASS_EXHAUSTED', result
    snapshot, session = assert_owned_search(rt, result)
    expected = set(brute_grammar(rules, bounds))
    assert {row.program for row in session.rows} == expected and len(expected) == len(session.rows)
    scores = {row.program: oracle_likelihood(row.program, cfg, row.learner, snapshot.observations) for row in session.rows}
    assert all(row.likelihood == scores[row.program] for row in session.rows)
    sum_only = max(value for graph, value in scores.items() if graph.counts()['PRODUCTs'] == 0)
    short_prefix = max(value for graph, value in scores.items() if len(graph.nodes) < 3)
    witness = Program((Source('x'), Source('z'), Product('mass', 0, 1)), 0, (2, 0))
    assert sum_only == short_prefix == session.base_likelihood == F(1, 16)
    assert scores[witness] == F(1, 12) and result.best_likelihood == max(scores.values()) > sum_only
    assert len(snapshot.candidates) == 2  # baseline plus actual reachable winner
    return {'declared_bounds': asdict(bounds), 'complete_native_programs': len(expected),
            'full_same_class_P0_and_all_shorter_prefix_likelihood': str(sum_only),
            'empirical_optimal_unigram_likelihood': '1/16',
            'constructed_compound_likelihood': str(scores[witness]),
            'best_complete_class_likelihood': str(result.best_likelihood),
            'nonimproving_prefixes_were_not_pruned': True,
            'scope': 'four logged XOR contexts; all ordered native syntax in these explicit bounds; fixed initializer; no unrestricted-value exclusion'}


def recurrent_audit():
    states = (DelayedStateSpec('a', 'mass', 1, F(1)), DelayedStateSpec('b', 'mass', 2, F(1)))
    cfg = contract()
    cfg = replace(cfg, semantics=replace(cfg.semantics, states=states))
    initial = replace(zero_program(2), bindings=(Binding('a', 0), Binding('b', 0)))
    rt, spec = runtime_fixture(cfg=cfg, initial=initial, profile=True)
    result = finish(rt, rt.start_reference_search('native'))
    assert result.status == 'REFERENCE_CLASS_EXHAUSTED', result
    snapshot, session = assert_owned_search(rt, result)
    expected = set(brute_grammar(cfg.semantics, SMALL))
    assert set(r.program for r in session.rows) == expected
    for row in session.rows:
        queues = {s.state_id: (F(0),)*s.delay for s in states}
        for observation in snapshot.observations*2:
            node = row.program.nodes[0]
            value = dict(observation.sources)[node.source_id] if type(node) is Source else (queues[node.state_id][0] if type(node) is State else F(0))
            queues = {key: old[1:]+(value,) for key, old in queues.items()}
        assert row.learner.delayed == tuple(sorted(queues.items()))
        assert row.likelihood == oracle_likelihood(row.program, cfg, row.learner, snapshot.observations)
    return {'complete_delayed_binding_programs': len(expected),
            'independent_replayed_buffers_and_frozen_state_objective_checks': len(session.rows)}


def adversarial_audit():
    rt, spec = runtime_fixture()
    result = rt.start_reference_search('native')
    with patch.object(grammar, 'plan', return_value=GrammarAction('close')):
        rejects(lambda: rt.advance_reference_search(result.search_id, transitions=1))
    assert rt.snapshot().searches[-1].status == 'EXECUTION_FAILED' and not rt.snapshot().reference_proofs
    assert len(rt.snapshot().candidates) == 1

    rt, _ = runtime_fixture()
    result = rt.start_reference_search('native')
    compare = rt._compare_native_program

    def substituted(session, program):
        updated, error = compare(session, program)
        fake = replace(updated.rows[-1], program=Program((Source('x0_1'),), 0, (0, 0)))
        return replace(updated, rows=updated.rows[:-1]+(fake,)), error

    with patch.object(rt, '_compare_native_program', side_effect=substituted):
        rejects(lambda: rt.advance_reference_search(result.search_id, transitions=2))
    assert not rt.snapshot().reference_proofs

    # A selector bug is independently refuted at proof time. Source-only
    # members on this onehot task beat the deployed empirical uniform baseline.
    rt, _ = runtime_fixture(bounds=GrammarLimits(2, 0, 0, 0, 0))
    result = rt.start_reference_search('native')
    with patch.object(execution, 'compare_likelihoods', return_value=0):
        rejects(lambda: finish(rt, result))
    assert not rt.snapshot().reference_proofs and rt.snapshot().searches[-1].status == 'EXECUTION_FAILED'
    # Even a score above every alternative must equal the selected endpoint.
    rt, _ = runtime_fixture()
    result = rt.start_reference_search('native')
    compare = rt._compare_native_program

    def inflated(session, program):
        updated, error = compare(session, program)
        return replace(updated, best_likelihood=F(1)), error

    with patch.object(rt, '_compare_native_program', side_effect=inflated):
        rejects(lambda: finish(rt, result))
    assert not rt.snapshot().reference_proofs

    # An unexpected scoring failure keeps the consumed ordinal and data-use
    # record, releases the speculative lineage, and cannot activate a proof.
    rt, _ = runtime_fixture()
    result = rt.start_reference_search('native')
    before = rt.snapshot()
    with patch.object(execution, 'likelihood', side_effect=RuntimeError('injected reference backend failure')):
        rejects(lambda: rt.advance_reference_search(result.search_id, transitions=2), RuntimeError)
    failed = validate_residency(rt)
    assert failed.searches[-1].cursor.emitted == 1 and failed.searches[-1].rows[0].status == 'EXECUTION_FAILED'
    assert len(failed.candidates) == 1 and len(failed.data_uses) > len(before.data_uses)
    assert failed.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert not failed.reference_proofs

    # Tight range verification blocks only the final proof, never drops syntax
    # or infers that descendants are useless from a failed parent comparison.
    cfg = contract(cap=3)
    rt, _ = runtime_fixture(cfg=cfg)
    result = finish(rt, rt.start_reference_search('native'))
    session = rt.snapshot().searches[-1]
    assert result.status == 'UNRESOLVED' and session.cursor.done and session.unresolved == 2
    assert len(session.rows) == 3 and result.programs_compared == 1 and result.unresolved_programs == 2
    assert not rt.snapshot().reference_proofs

    rt, spec = runtime_fixture(profile=True, stream=())
    result = rt.start_reference_search('native')
    assert result.status == 'UNRESOLVED' and result.programs_compared == 0
    assert 'profile observations' in result.reason and len(rt.snapshot().candidates) == 1
    rt, _ = runtime_fixture(stream=())
    assert rt.start_reference_search('native').status == 'UNRESOLVED'
    rejects(lambda: rt.start_reference_search('unregistered'))
    rejects(lambda: ReferenceSearchSpec('bad', SMALL, ('observation-0', 'observation-0')))
    bad_spec = ReferenceSearchSpec('bad', SMALL, ('test-label',))
    rejects(lambda: ReferenceCompilerRuntime(rt.contract, zero_program(2), online=replace(rt.online_contract, searches=(bad_spec,))))
    bad_spec = ReferenceSearchSpec('bad', GrammarLimits(1001, 0, 0, 0, 0), ('observation-0',))
    rejects(lambda: ReferenceCompilerRuntime(rt.contract, zero_program(2), online=replace(rt.online_contract, searches=(bad_spec,))))

    # Real operation budget: all syntax/rows finish, final maximum verification
    # cannot fit. Evidence and cumulative work survive, with no issued token.
    rt, _ = runtime_fixture()
    full = finish(rt, rt.start_reference_search('native'), chunks=(1000,))
    snapshot = rt.snapshot()
    full_work = snapshot.resources['spent']['compiler']['work']
    cap = full_work-(full.programs_compared+1)-1
    limited_cfg = replace(contract(pattern=(F(1, 2),)), limits=limits(work_cap=cap))
    limited, _ = runtime_fixture(cfg=limited_cfg)
    partial = finish(limited, limited.start_reference_search('native'), chunks=(1000,))
    limited_snapshot = validate_residency(limited)
    assert partial.status == 'UNRESOLVED' and limited_snapshot.searches[-1].cursor.done
    assert partial.programs_compared == full.programs_compared and not limited_snapshot.reference_proofs
    assert limited_snapshot.resources['spent']['compiler']['work'] <= cap
    peak = snapshot.resources['peak']['reference_payload_bytes']
    current = snapshot.resources['current']['reference_payload_bytes']
    assert peak > current
    memory_cap = (peak+current)//2
    limited_cfg = replace(contract(pattern=(F(1, 2),)), limits=limits(byte_cap=memory_cap))
    limited, _ = runtime_fixture(cfg=limited_cfg)
    partial = finish(limited, limited.start_reference_search('native'), chunks=(1000,))
    assert partial.status == 'UNRESOLVED' and not limited.snapshot().reference_proofs
    assert validate_residency(limited).resources['peak']['reference_payload_bytes'] <= memory_cap

    tiny = F(1, 2)+F(1, 2**1200)
    assert float(tiny) == float(F(1, 2)) and compare_likelihoods(tiny, F(1, 2), bit_limit=4096) == 1
    rejects(lambda: verify_maximum(F(1, 2), (tiny,), bit_limit=4096))
    rejects(lambda: compare_likelihoods(tiny, F(1, 2), bit_limit=256), ArithmeticUnresolved)
    cfg = replace(contract(), reference_integer_bits=16)
    stream = tuple((domain(1)[i % 2], i % 2) for i in range(24))
    rt, spec = runtime_fixture(cfg=cfg, count=24, stream=stream,
                               objective_ids=tuple(f'observation-{i}' for i in range(24)))
    assert rt.start_reference_search('native').status == 'UNRESOLVED' and not rt.snapshot().reference_proofs

    # All external mutations invalidate the active complete context. Search
    # chunking itself preserves its own checked prefix.
    for action in ('query', 'construct', 'predict', 'another-search'):
        rt, spec = runtime_fixture()
        result = rt.start_reference_search('native')
        result = rt.advance_reference_search(result.search_id, transitions=1)
        if action == 'query':
            rt.query('retained-label', spec.observation_ids)
        elif action == 'construct':
            rt.construct_candidate(zero_program(2))
        elif action == 'predict':
            deliver_context(rt, 'observation-2', domain(1)[0])
            rejects(lambda: rt.advance_reference_search(result.search_id, transitions=1))
            rt.observe(0)
        else:
            rt.start_reference_search('native')
        assert rt.advance_reference_search(result.search_id, transitions=1).status == 'UNRESOLVED'
        session = next(s for s in rt.snapshot().searches if s.search_id == result.search_id)
        assert session.status == 'STALE_CONTEXT' and not rt.snapshot().reference_proofs
    rt, _ = runtime_fixture()
    result = rt.start_reference_search('native')
    rt.advance_reference_search(result.search_id, transitions=2)
    old_rows = rt.snapshot().searches[-1].rows
    rt.cancel_reference_search(result.search_id)
    _, session = assert_owned_search(rt, result)
    assert session.status == 'CANCELLED' and session.rows == old_rows
    assert rt.advance_reference_search(result.search_id, transitions=1).status == 'UNRESOLVED'

    # An empty constructor class still has its deployed baseline comparison;
    # a trained baseline can also beat every member while lying outside grammar.
    rt, _ = runtime_fixture(bounds=GrammarLimits(0, 0, 0, 0, 0))
    empty = finish(rt, rt.start_reference_search('native'))
    assert empty.status == 'REFERENCE_CLASS_EXHAUSTED' and empty.programs_compared == 0
    assert empty.best_candidate_id == rt.snapshot().deployed_id and empty.best_likelihood == F(1, 4)
    scaled = Program((Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0),)),
                      Sum('mass', (Term(1, 0),))), 1, (2, 3))
    rt, _ = runtime_fixture(cfg=contract(pattern=(F(4),)), initial=scaled)
    before = rt.snapshot()
    assert before.candidates[0].theta != (F(4),) and not SMALL.admits(scaled)
    base_wins = finish(rt, rt.start_reference_search('native'))
    assert base_wins.status == 'REFERENCE_CLASS_EXHAUSTED' and base_wins.best_candidate_id == before.deployed_id
    assert base_wins.best_likelihood > F(1, 4) and rt.snapshot().candidates == before.candidates
    return {'fake_prefix_closure_substituted_row_wrong_selector_and_unbound_winner_score_rejected': True,
            'backend_failure_preserves_visited_ordinal_reads_work_and_owned_evidence': True,
            'range_information_numeric_work_and_coexistence_failures_unresolved': True,
            'all_compared_rows_still_need_final_proof_verification_budget': True,
            'sub_binary64_likelihood_difference_retained': True,
            'external_mutations_invalidate_active_and_historical_authority': True,
            'cancelled_history_remains_physically_owned': True,
            'empty_class_and_trained_deployed_winner_outside_grammar_have_explicit_scope': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', choices=('all', 'grammar', 'runtime', 'compound', 'recurrent', 'adversaries'), default='all')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checks = {'grammar': grammar_audit, 'runtime': runtime_audit, 'compound': compound_audit,
              'recurrent': recurrent_audit, 'adversaries': adversarial_audit}
    result = {'status': 'PASS', 'scope': 'owned complete ordered native constructor class plus actual deployed baseline; fixed-state exact empirical CE'}
    for key, audit in checks.items():
        if args.section in ('all', key):
            result[key] = audit()
    result['not_closed'] = ['all future continuations or arbitrary parameter values',
                            'population and fresh stochastic persistence claims',
                            'full ERC-1 host/device resources and information interfaces',
                            'actual AMP bridge, atomic installation and complete Runtime release']
    if args.write:
        if args.section != 'all':
            parser.error('only the complete audit can replace canonical evidence')
        (ROOT/'evidence/minimal/FP_REFERENCE_SEARCH_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
