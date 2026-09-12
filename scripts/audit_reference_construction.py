"""Audit the actual Runtime construction endpoint and owned reference resources.

This is not a complete Runtime gate report. No learning, persistence, AMP or
install closure is inferred from the construction segment checked here.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
sys.path.insert(0, str(ROOT/'theory/numerical_checks'))

from fp_reference.core import ContractError
from fp_reference.machine import pack
from fp_reference.program import Binding, DelayedStateSpec, Product, Program, SemanticRules, Source, SourceSpec, State, Sum, Term
from fp_reference.resources import CostRouter, ObjectSpec, ResourceExceeded, ResourceLedger, ResourceLimits
from fp_reference import ConstructionContract, ReferenceCompilerRuntime
from fp_reference.semantics import evaluate, reset_delayed
from dyadic_cap_total_complexity_audit import exact_graph
from node_edge_precision_accuracy_audit import shared_reciprocal_graph
from source_intersection_product_audit import binary_tables, evaluate_tables, random_graph
from two_product_support_border_audit import sources


def rejects(fn, error=ContractError):
    try:
        fn()
    except error:
        return
    raise AssertionError('an invalid action was accepted')


def semantic_rules(d, k):
    return SemanticRules(tuple(SourceSpec(f'x{i}_{bit}', 'mass', 0, F(1)) for i in range(d) for bit in (0, 1)),
                         ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1),)*k)


def domain(d):
    return tuple(tuple(F(x[i] == bit) for i in range(d) for bit in (0, 1)) for x in product((0, 1), repeat=d))


def limits(byte_cap=10_000_000, work_cap=10_000_000):
    caps = {'reference_payload_bytes': byte_cap, 'physical_objects': 100_000}
    return ResourceLimits(caps, {'deployment': caps, 'compiler': caps},
                          {'deployment': {'work': work_cap}, 'compiler': {'work': work_cap}})


def contract(d=1, k=2, *, cap=100, peak=100, pattern=(F(1, 2), F(1), F(2)), source_domain=True):
    return ConstructionContract(semantic_rules(d, k), limits(), {'construct': 'compiler', 'range_audit': 'compiler'},
                                {'nodes': 1000, 'SUMs': 1000, 'PRODUCTs': 1000, 'edges': 10000, 'slots': 100},
                                pattern, F(cap), F(peak), 4096, domain(d) if source_domain else None)


def zero_program(k):
    return Program((Sum('mass', ()),), 0, (0,)*k)


def translate(nodes, heads, pattern):
    slots = {F(value): i for i, value in enumerate(pattern)}
    result = []
    for node in nodes:
        if node[0] == 'source':
            result.append(Source(f'x{node[1]}_{node[2]}'))
        elif node[0] == 'product':
            result.append(Product('mass', node[1], node[2]))
        else:
            result.append(Sum('mass', tuple(Term(parent, slots[F(weight)]) for parent, weight in node[1])))
    return Program(tuple(result), len(pattern), tuple(heads))


def validate_residency(runtime):
    snapshot = runtime.snapshot()
    objects, buffers = snapshot.resources['objects'], dict(snapshot.buffers)
    assert set(objects) == set(buffers)
    assert snapshot.resources['current']['reference_payload_bytes'] == sum(map(len, buffers.values()))
    assert snapshot.resources['current']['physical_objects'] == len(buffers)
    for candidate in snapshot.candidates:
        assert candidate.object_ids and all(candidate.physical_owner in objects[key]['references'] for key in candidate.object_ids)
        assert candidate.program_id in dict(snapshot.programs)
    return snapshot


def native_endpoint_audit():
    identity = tuple(tuple(F(1+int(i == j)) for j in range(8)) for i in range(8))
    old_nodes, heads = exact_graph(3, identity)
    cfg = contract(3, 8, cap=9, peak=1)
    runtime = ReferenceCompilerRuntime(cfg, zero_program(8))
    graph = translate(old_nodes, heads, cfg.initializer_pattern)
    result = runtime.construct_candidate(graph)
    assert result.status == 'BUILT_REFERENCE'
    state = next(s for s in runtime.snapshot().candidates if s.candidate_id == result.candidate_id)
    assert graph.counts()['PRODUCTs'] == 12 and graph.counts()['SUMs'] == 0
    assert state.theta == cfg.initializer_pattern  # unused coordinates are retained and charged
    assert all(bound.normalizer.lower == bound.normalizer.upper == 9 for bound in state.range_evidence)
    snapshot = validate_residency(runtime)
    assert runtime.install(result.candidate_id, certified=True, bridge=True).status == 'UNRESOLVED'
    assert runtime.snapshot() == snapshot
    rejects(lambda: runtime.construct_candidate(graph, theta=()), TypeError)
    rejects(lambda: runtime.construct_candidate(graph, objects=()), TypeError)
    rejects(lambda: snapshot.resources['owners'].__setitem__('fake', 'deployment'), AttributeError)
    assert runtime.construct_candidate(object()).status == 'REJECTED_ADMISSIBILITY'
    tight = replace(cfg, graph_limits=dict(cfg.graph_limits, PRODUCTs=11))
    narrow = ReferenceCompilerRuntime(tight, zero_program(8))
    assert narrow.construct_candidate(graph).status == 'REJECTED_ADMISSIBILITY'

    # Reuse existing precision/range fixtures rather than inventing a new static
    # family. Both approximating and exact-slack graphs traverse the Runtime.
    target = ((F(5, 8), F(3, 8)),)*2
    fixture_count = 1
    for depth in (1, 2, 3, 5):
        for exact in (False, True):
            cap = F(8, 3)+(F(16, 3)*F(1, 4)**(2**depth) if exact else 0)
            cfg = contract(1, 2, cap=cap, peak=max(F(1), cap-2))
            nodes, heads, _ = shared_reciprocal_graph(1, target, cap, depth, exact=exact)
            graph = translate(nodes, heads, cfg.initializer_pattern)
            rt = ReferenceCompilerRuntime(cfg, zero_program(2))
            result = rt.construct_candidate(graph)
            assert result.status == 'BUILT_REFERENCE'
            built = next(s for s in rt.snapshot().candidates if s.candidate_id == result.candidate_id)
            old = evaluate_tables(nodes, binary_tables(1))
            for index, row in enumerate(domain(1)):
                actual = evaluate(graph, cfg.semantics, built.theta, dict(zip((s.source_id for s in cfg.semantics.sources), row)))
                expected = tuple(old[h][index]+1 for h in heads)
                assert actual.masses == expected and actual.normalizer <= cap
                if exact:
                    assert actual.probabilities == target[index]
            validate_residency(rt)
            fixture_count += 1

    rng = random.Random(2026091204)
    pattern = (F(0), F(1, 7), F(1), F(5), F(1, 3), F(2), F(1, 2), F(3))
    cfg = contract(2, 2, cap=10**100, peak=10**100, pattern=pattern)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2))
    point_checks = 0
    for _ in range(80):
        nodes = sources(2)
        first = random_graph(rng, nodes, rng.randrange(5))
        second = random_graph(rng, nodes, rng.randrange(3))
        graph = translate(nodes, (first, second), pattern)
        result = rt.construct_candidate(graph)
        assert result.status == 'BUILT_REFERENCE'
        built = next(s for s in rt.snapshot().candidates if s.candidate_id == result.candidate_id)
        oracle = evaluate_tables(nodes, binary_tables(2))
        for index, row in enumerate(domain(2)):
            actual = evaluate(graph, cfg.semantics, built.theta, dict(zip((s.source_id for s in cfg.semantics.sources), row)))
            assert actual.values == tuple(values[index] for values in oracle)
            assert actual.masses == (1+oracle[first][index], 1+oracle[second][index])
            point_checks += 1
        before = validate_residency(rt)
        rt.retire_candidate(result.candidate_id)
        after = validate_residency(rt)
        assert after.resources['spent']['compiler']['work'] == before.resources['spent']['compiler']['work']+rt._machine.control_admission_work
        assert after.resources['spent']['deployment'] == before.resources['spent']['deployment']
        assert after.resources['peak'] == before.resources['peak']
        assert len(after.candidates) == 1 and len(after.programs) == 1
    return fixture_count, point_checks


def boundary_audit():
    assert pack({1: 'value'}) != pack({'1': 'value'})
    assert pack((1,)) != pack([1]) and pack(F(1)) != pack(1)
    cfg = contract(cap=3, peak=1, pattern=(F(1),), source_domain=False)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2))
    graph = Program((Source('x0_0'), Source('x0_1'), Sum('mass', (Term(0, 0), Term(1, 0))), Sum('mass', ())), 1, (2, 3))
    result = rt.construct_candidate(graph)
    assert result.status == 'UNRESOLVED_RANGE'
    assert result.candidate_id in {c.candidate_id for c in rt.snapshot().candidates}
    proven = ReferenceCompilerRuntime(replace(cfg, source_domain=domain(1)), zero_program(2))
    assert proven.construct_candidate(graph).status == 'BUILT_REFERENCE'

    # A final model fits in isolation but its build cannot coexist with the
    # incumbent at this cap. Work and actual peaks survive the failed attempt.
    cfg = contract(pattern=(F(1),))
    loose = ReferenceCompilerRuntime(cfg, zero_program(2))
    initial_peak = loose.snapshot().resources['peak']['reference_payload_bytes']
    tight = ReferenceCompilerRuntime(replace(cfg, limits=limits(byte_cap=initial_peak)), zero_program(2))
    before = tight.snapshot()
    failure = tight.construct_candidate(zero_program(2))
    after = validate_residency(tight)
    assert failure.status == 'UNRESOLVED' and failure.candidate_id is None
    assert after.resources['current'] == before.resources['current']
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert after.cursor == before.cursor and after.deployed_id == before.deployed_id

    # A backend failure after allocation cannot leave an unowned physical build
    # or turn itself into an admissibility theorem.
    failing = ReferenceCompilerRuntime(contract(pattern=(F(1),)), zero_program(2))
    before = failing.snapshot()
    original = failing._machine.realize

    def fail_after_initial_buffers(object_id, kind, value, provenance):
        if kind == 'initialized_reference_state':
            raise RuntimeError('injected backend failure')
        return original(object_id, kind, value, provenance)

    with patch.object(failing._machine, 'realize', side_effect=fail_after_initial_buffers):
        rejects(lambda: failing.construct_candidate(zero_program(2)), RuntimeError)
    after = validate_residency(failing)
    assert after.resources['current'] == before.resources['current'] and len(after.candidates) == 1
    assert after.resources['spent']['compiler']['work'] > before.resources['spent']['compiler']['work']
    assert after.attempts[-1][1] == 'EXECUTION_FAILED'

    # Numerator/denominator work uncertainty is distinct from range infeasibility.
    cfg = replace(contract(cap=3, peak=1, pattern=(F(1, 2),)), reference_integer_bits=64)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2))
    nodes = [Source('x0_0'), Sum('mass', (Term(0, 0),))]
    for _ in range(10):
        nodes.append(Product('mass', len(nodes)-1, len(nodes)-1))
    nodes.append(Sum('mass', ()))
    result = rt.construct_candidate(Program(tuple(nodes), 1, (len(nodes)-2, len(nodes)-1)))
    assert result.status == 'UNRESOLVED' and 'integer work' in result.reason
    validate_residency(rt)

    invalid = [Program((Source('undeclared'),), 0, (0, 0)),
               Program((Source('x0_0'), Product('mass', 1, 0)), 0, (1, 1)),
               Program((Source('x0_0'), Sum('mass', (Term(0, F(1)),))), 2, (1, 1)),
               Program((Source('x0_0'), Sum('mass', (Term(0, -1),))), 1, (1, 1)),
               Program((Source('x0_0'), Product('unregistered', 0, 0)), 0, (1, 1))]
    for graph in invalid:
        assert rt.construct_candidate(graph).status == 'REJECTED_ADMISSIBILITY'
    rejects(lambda: replace(cfg, initializer_pattern=(float('nan'),)))
    rejects(lambda: replace(cfg, source_domain=()))
    rejects(lambda: replace(cfg, graph_limits=dict(cfg.graph_limits, slots=True)))

    rules = SemanticRules((SourceSpec('x', 'mass', 0, F(1)),), ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)),
                          (DelayedStateSpec('memory', 'mass', 2, F(1)),))
    recurrent = Program((Source('x'), State('memory'), Sum('mass', ())), 0, (1, 2), (Binding('memory', 0),))
    state = reset_delayed(rules)
    read = []
    for observation in (1, 0, 0, 1):
        result = evaluate(recurrent, rules, (), {'x': F(observation)}, state)
        read.append(result.excesses[0])
        state = result.delayed
    assert read == [0, 0, 1, 0]
    rejects(lambda: replace(recurrent, bindings=()).validate(rules))
    rejects(lambda: DelayedStateSpec('bad', 'mass', 0, 1))
    # Tiny exact values are not silently rounded to zero through the recovered
    # core's old require_finite/float path.
    tiny = F(1, 2**2000)
    ordinary = semantic_rules(1, 2)
    direct = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    actual = evaluate(direct, ordinary, (tiny,), {'x0_0': F(1), 'x0_1': F(0)})
    assert actual.excesses[0] == tiny > 0
    return {'inconclusive_source_box_retained': True, 'coexistence_failure_keeps_cost_and_incumbent': True,
            'backend_failure_releases_partial_build_without_refund': True,
            'integer_work_exhaustion_is_unresolved': True, 'invalid_native_programs_rejected': len(invalid),
            'positive_delay_trace': read, 'exact_tiny_value_preserved': True}


def ownership_model_check():
    caps = {'bytes': 40, 'objects': 8}
    role_caps = {'bytes': 25, 'objects': 8}
    ledger = ResourceLedger(ResourceLimits(caps, {'deployment': role_caps, 'compiler': role_caps},
                                          {'deployment': {'work': 80}, 'compiler': {'work': 80}}))
    owner_roles = {'a': 'deployment', 'b': 'compiler', 'c': 'compiler'}
    for owner, role in owner_roles.items():
        ledger.register_owner(owner, role)
    model, retired = {}, set()
    spent = {role: 0 for role in ('deployment', 'compiler')}
    peak = {'bytes': 0, 'objects': 0}
    role_peak = {role: dict(peak) for role in spent}
    rng = random.Random(2026091205)
    accepted, rejected = 0, 0

    def counts(objects):
        total = {'bytes': sum(size for size, refs in objects.values()), 'objects': len(objects)}
        roles = {role: {'bytes': 0, 'objects': 0} for role in spent}
        for size, refs in objects.values():
            for role in {owner_roles[owner] for owner in refs}:
                roles[role]['bytes'] += size
                roles[role]['objects'] += 1
        return total, roles

    def feasible(objects):
        total, roles = counts(objects)
        return all(total[key] <= value for key, value in caps.items()) and all(
            values[key] <= cap for values in roles.values() for key, cap in role_caps.items())

    for step in range(1500):
        before = ledger.snapshot()
        new = {key: (size, dict(refs)) for key, (size, refs) in model.items()}
        operation = rng.choice(('allocate', 'acquire', 'release', 'work'))
        owner = rng.choice(tuple(owner_roles))
        object_id = rng.choice(tuple(model)) if model and operation in ('acquire', 'release') else f'object:{step}'
        if operation == 'allocate':
            size = rng.randrange(1, 17)
            new[object_id] = (size, {owner: 1})
            ok = feasible(new)
            action = lambda: ledger.allocate(owner, (ObjectSpec(object_id, 'test_buffer', {'bytes': size, 'objects': 1}, f'known:{step}'),))
        elif operation == 'acquire':
            ok = object_id in model
            if ok:
                new[object_id][1][owner] = new[object_id][1].get(owner, 0)+1
                ok = feasible(new)
            action = lambda: ledger.acquire(owner, object_id)
        elif operation == 'release':
            ok = object_id in model and owner in model[object_id][1]
            if ok:
                refs = new[object_id][1]
                refs[owner] -= 1
                if not refs[owner]:
                    del refs[owner]
                if not refs:
                    del new[object_id]
            action = lambda: ledger.release(owner, object_id)
        else:
            role, cost = owner_roles[owner], rng.randrange(1, 9)
            ok = spent[role]+cost <= 80
            action = lambda: ledger.charge_work(role, {'work': cost})
        if ok:
            action()
            if operation == 'work':
                spent[role] += cost
            else:
                retired.update(set(model)-set(new))
                model = new
            accepted += 1
        else:
            rejects(action)
            assert ledger.snapshot() == before
            rejected += 1
        total, roles = counts(model)
        for key, used in total.items():
            peak[key] = max(peak[key], used)
        for role, values in roles.items():
            for key, used in values.items():
                role_peak[role][key] = max(role_peak[role][key], used)
        snapshot = ledger.snapshot()
        assert snapshot['current'] == total and snapshot['role_current'] == roles
        assert snapshot['peak'] == peak and snapshot['role_peak'] == role_peak
        assert snapshot['spent'] == {role: {'work': value} for role, value in spent.items()}
        assert set(snapshot['objects']) == set(model) and set(snapshot['retired_object_ids']) == retired
        for key, (size, refs) in model.items():
            assert snapshot['objects'][key]['references'] == refs
    before = ledger.snapshot()
    rejects(lambda: ledger.charge_work('compiler', {'work': -1}))
    rejects(lambda: ledger.register_owner('a', 'compiler'))
    assert ledger.snapshot() == before
    ledger.close_owner('b')
    rejects(lambda: ledger.allocate('b', (ObjectSpec('later', 'buffer', {'bytes': 1, 'objects': 1}, 'known'),)))
    router = CostRouter(ledger, {'query': 'compiler'})
    rejects(lambda: router.ledger_for('query').charge_work('deployment', {'work': 0}), TypeError)
    rejects(lambda: router.charge_work('unregistered', {'work': 0}))
    return {'steps': 1500, 'accepted': accepted, 'rejected': rejected,
            'shared_roles_refcounts_peaks_and_no_refund': True, 'closed_owner_and_role_reroute_rejected': True}


def audit():
    fixtures, point_checks = native_endpoint_audit()
    return {'status': 'PASS', 'scope': 'actual ReferenceCompilerRuntime native construction/recovery endpoint; packed reference payload machine only',
            'existing_resource_fixture_graphs': fixtures, 'random_shared_native_graphs': 80,
            'independent_exact_full_context_comparisons': point_checks, 'boundary_checks': boundary_audit(),
            'ownership_model_check': ownership_model_check(),
            'not_closed': ['complete immutable run manifest', 'legal information/data-use interface',
                           'grammar-complete search and reachable learner/profile continuation',
                           'fresh persistence and error ledger', 'full host/device memory and physical work model',
                           'actual AMP event bridge', 'atomic install and complete 47-gate Runtime release']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    output = json.dumps(audit(), indent=2, default=str)+'\n'
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_CONSTRUCTION_RUNTIME_AUDIT.json').write_text(output, encoding='utf-8')
    print(output, end='')
