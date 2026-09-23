"""Exact audit of joint native indexing and contiguous positive elimination.

Caller-owned component only. The existing Runtime must still reject this
unregistered indexed representation; no actual CUDA phase is executed.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import joint_relation as joint, joint_partition_decoder as decoder
from fp_reference.core import ContractError
from fp_reference.learner import ReferenceLearnerState, initial_state, observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import ArithmeticUnresolved, Evaluation, evaluate
from fp_reference.encoding import pack
from unknown_noise_decoding import DEFAULT, OTHER, Joint
from shared_noise_factor_closure import counter_states, forest_decode
import audit_mixture_partition_bridge as old
import mixture_partition_bridge as prototype
import audit_packed_count_histogram as histogram

OUTPUT = ROOT/'evidence/minimal/FP_JOINT_PARTITION_STORAGE.json'
BUDGET = decoder.JointPartitionAllowance(join_cells=32, live_cells=128, arithmetic=4096, step_cap=128)


def rejects(function, error=(ContractError, ArithmeticUnresolved)):
    try:
        function()
    except error:
        return
    raise AssertionError('invalid component input was accepted')


def literal(model):
    return old.small_native(prototype.Model(model.n, model.rates, model.prior))


def indexing():
    rows = []
    for rates, prior in (DEFAULT, OTHER):
        for n in (2, 3, 4):
            model = joint.JointRelation(n, rates, prior)
            bank, rules, graph, spec, worlds = literal(model)
            model.compare_literal(graph, rules, (F(1),)+bank.prior, spec,
                                  node_cap=1000, term_cap=100000, slot_cap=100)
            assert model.counts() == graph.counts()
            assert tuple(model.hypothesis(k) for k in range(model.K)) == tuple(
                (j, sum(z[v] << (n-1-v) for v in range(1, n))) for j, z in worlds)
            for node, actual in enumerate(graph.nodes):
                header = model.header(node)
                if header.kind == 'SUM':
                    assert header.arity == len(actual.terms)
                    for at in {0, header.arity//2, header.arity-1}:
                        if 0 <= at < header.arity:
                            assert model.term(node, at) == actual.terms[at]
            rows.append({'n': n, 'rates': tuple(map(str, rates)), 'complete_literal_counts': graph.counts()})
    model = joint.JointRelation(3, *DEFAULT)
    bank, rules, graph, spec, _ = literal(model)
    gamma = (F(1),)+bank.prior
    compare = lambda g=graph, r=rules, t=gamma, u=spec: model.compare_literal(
        g, r, t, u, node_cap=1000, term_cap=100000, slot_cap=100)
    rejects(lambda: compare(g=replace(graph, heads=graph.heads[::-1])))
    rejects(lambda: compare(r=replace(rules, base=(F(2), F(1)))))
    rejects(lambda: compare(t=(gamma[0], gamma[1]/2, gamma[2]+gamma[1]/2)+gamma[3:]))
    rejects(lambda: compare(u=replace(spec, learning_rate=F(1, 2))))
    source = replace(rules.sources[0])
    object.__setattr__(source, 'availability_delay', False)
    rejects(lambda: compare(r=replace(rules, sources=(source,)+rules.sources[1:])))
    for kind, value in (('g', graph), ('r', rules), ('u', spec)):
        extra = replace(value)
        object.__setattr__(extra, 'unregistered', True)
        rejects(lambda: compare(**{kind: extra}))
    for key in ('node_cap', 'term_cap', 'slot_cap'):
        limits = dict(node_cap=1000, term_cap=100000, slot_cap=100)
        limits[key] = 1
        rejects(lambda: model.materialize_program(**limits), ArithmeticUnresolved)
    return {'complete_graph_initializer_learner_matches': rows, 'literal_binding_refusals': 8,
            'pre_materialization_resource_refusals': 3}


def enumeration():
    rows = []
    for rates, prior in (DEFAULT, OTHER):
        states = queries = roots_checked = max_compacted = max_bits = 0
        extents = {}
        for n in (2, 3, 4):
            model = joint.JointRelation(n, rates, prior)
            oracle = Joint(n, rates, prior)
            budget = replace(BUDGET, step_cap=3)
            size = decoder.workspace_bytes(model, budget)
            extents[n] = size
            backing = bytearray([165])*(size+26)
            with memoryview(backing)[13:-13] as extent:
                for total, level in counter_states(n*(n-1)//2+1, 3):
                    for counts in sorted(level):
                        before = joint.JointCountState(model, counts[:-1], counts[-1], total, total)
                        weights = oracle.counts(total, counts[:-1], counts[-1])
                        normalization = sum(weights)
                        for query in product(range(n), repeat=2):
                            plan = decoder.prepare(before, query, budget, extent)
                            expected = tuple(sum(w*int(model.scale*(1-eta if z[query[0]]^z[query[1]] == y else eta)-1)
                                for w, (eta, z) in zip(weights, oracle.hypotheses)) for y in (0, 1))
                            assert (plan.excesses, plan.normalization) == (expected, normalization)
                            assert decoder.reference(plan)[5:] == tuple(oracle.forecast(weights, (*query, y)) for y in (0, 1))
                            for y, value in enumerate(expected+(normalization,)):
                                start = (budget.live_cells+2+y)*plan.cell_bytes
                                assert int.from_bytes(extent[start:start+plan.cell_bytes], 'little') == value
                                roots_checked += 1
                            assert before == joint.JointCountState(model, counts[:-1], counts[-1], total, total)
                            assert plan.multiplications+plan.additions <= budget.arithmetic
                            assert plan.compacted_cells <= len(rates)*(n-1)*budget.live_cells
                            assert plan.maximum_integer_bits <= plan.integer_envelope
                            max_compacted = max(max_compacted, plan.compacted_cells)
                            max_bits = max(max_bits, plan.maximum_integer_bits)
                            queries += 1
                        states += 1
            assert backing[:13] == backing[-13:] == bytearray([165])*13
        rows.append({'rates': tuple(map(str, rates)), 'reachable_cuts': states, 'ordered_queries': queries,
                     'packed_joint_root_checks': roots_checked, 'exact_extent_bytes_by_n': extents,
                     'maximum_compacted_cells': max_compacted, 'maximum_integer_bits': max_bits,
                     'external_canary_bytes_unchanged': True})
    return rows


def order_audit():
    model = joint.JointRelation(4, *OTHER)
    before = joint.JointCountState(model, (1, -2, 0, 1, -1, 2), -1, 10, 10)
    budget = replace(BUDGET, step_cap=10)
    count = 0
    with memoryview(bytearray(decoder.workspace_bytes(model, budget))) as scratch:
        for query in product(range(4), repeat=2):
            expected = prototype.prepare(prototype.State(prototype.Model(4, *OTHER), before.counts,
                before.diagonal, before.cursor, before.steps), query)
            for order in permutations(range(3)):
                actual = decoder.prepare(before, query, budget, scratch, order=order)
                assert actual.excesses == expected.excess_parts and actual.normalization == expected.normalization
                count += 1
    return {'complete_order_query_cases': count, 'independent_tape_values_agree': True}


def zero_parts():
    rows = []
    for rate in (F(1, 3), F(1, 10)):
        model = joint.JointRelation(2, (rate,), (F(1),))
        before = joint.JointCountState(model, (396,), 0, 396, 396)
        budget = replace(BUDGET, step_cap=396)
        independent = Joint(2, model.rates, model.prior)
        weights = independent.counts(before.steps, before.counts, before.diagonal)
        for query in ((0, 0), (0, 1)):
            plan = decoder.passive_plan(before, query, budget)
            assert (plan.excesses[1] == 0) == (query[0] == query[1])
            assert decoder.reference(plan)[5] == independent.forecast(weights, (*query, 0))
            assert plan.output_cells == (25 if query[0] == query[1] else 29)
            rows.append({'rate': str(rate), 'native_scale': model.scale, 'query': query,
                         'steps': before.steps, 'second_excess_is_zero': plan.excesses[1] == 0,
                         'maximum_integer_bits': plan.maximum_integer_bits})
    return rows


def native_step(bundle, encoded, state, query, target, budget, scratch):
    bank, rules, graph, spec, worlds = bundle
    model = encoded.model
    sources = model.source_row(query[0]*model.n+query[1])
    plan = decoder.prepare_bound(model, encoded, rules, sources, budget, scratch)
    independent = Joint(model.n, model.rates, model.prior)
    weights = independent.counts(encoded.steps, encoded.counts, encoded.diagonal)
    assert state.theta == (F(1),)+tuple(F(w, plan.normalization) for w in weights)
    assert (state.cursor, state.optimizer_steps, state.unit_count) == (encoded.cursor, encoded.steps, 0)
    prediction = evaluate(graph, rules, state.theta, sources, (), bit_limit=32768)
    values = decoder.reference(plan)
    inputs = tuple(sources[s.source_id] for s in rules.sources)
    pairs = tuple(F((u, v) == query) for u, v in product(range(model.n), repeat=2))
    coefficients = bank.table[query[0]*model.n+query[1]]
    features = tuple(model.scale*coefficients[y][k]-1 for k in range(model.K) for y in (0, 1))
    assert prediction == Evaluation(inputs+pairs+features+values[:2], values[:2], values[2:4], values[4], values[5:], ())
    observed = observe_event(graph, state, spec, prediction, target, bit_limit=32768)
    gradients = (1/values[2+target]-F(2, model.scale),)+tuple(F(model.scale-2, model.scale)
        -(model.scale*p-1)/values[2+target] for p in coefficients[target])
    assert observed == ReferenceLearnerState(state.theta, (), gradients, 1, state.cursor+1, state.optimizer_steps)
    pending = joint.observe(encoded, query, target)
    assert pending.pending == (*query, target) and pending.counts == encoded.counts and pending.steps == encoded.steps
    successor = joint.commit(pending)
    committed = commit_event(observed, spec, bit_limit=32768)
    expected = bank.step(state.theta[1:], (query[0]*model.n+query[1], target))
    following = independent.counts(successor.steps, successor.counts, successor.diagonal)
    assert tuple(F(w, sum(following)) for w in following) == expected
    assert committed == ReferenceLearnerState((F(1),)+expected, (), (F(0),)*graph.slot_count, 0,
                                             successor.cursor, successor.steps)
    return successor, committed


def native_audit():
    rows = []
    for n, family in ((2, DEFAULT), (3, DEFAULT), (2, OTHER)):
        model = joint.JointRelation(n, *family)
        bundle = literal(model)
        bank, rules, graph, spec, _ = bundle
        initial = initial_state(graph, rules, (F(1),)+bank.prior, 7, spec=spec, bit_limit=32768)
        current = [(joint.initialize(model, 7), initial)]
        triples = 0
        with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
            for _ in range(2):
                following = []
                for encoded, state in current:
                    for u, v, y in product(range(n), range(n), (0, 1)):
                        following.append(native_step(bundle, encoded, state, (u, v), y, BUDGET, scratch))
                        triples += 1
                current = following
        rows.append({'n': n, 'rates': tuple(map(str, model.rates)), 'birth_cursor': 7, 'complete_native_triples': triples})
    model = joint.JointRelation(3, *DEFAULT)
    bundle = literal(model)
    bank, rules, graph, spec, _ = bundle
    encoded = joint.initialize(model)
    state = initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=32768)
    word = ((0, 1, 0), (1, 2, 0))*2+((0, 2, 1),)*36+((0, 2, 0),)*36+((2, 2, 1),)*4
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        for at, (u, v, y) in enumerate(word):
            if at == 4:
                encoded, state = joint.attach(encoded, 2), attach_boundary(state, 2, spec)
            encoded, state = native_step(bundle, encoded, state, (u, v), y, BUDGET, scratch)
    assert (encoded.cursor, encoded.steps, encoded.counts, encoded.diagonal) == (78, 80, (2, 0, 2), -4)
    rows.append({'n': 3, 'complete_native_triples': len(word), 'profile_attachment': {'steps': 4, 'cursor': 2},
                 'final_cursor': encoded.cursor, 'final_steps': encoded.steps, 'diagonal': encoded.diagonal,
                 'counts': encoded.counts, 'changing_support_and_reversal': True})
    return rows


def larger():
    rows = []
    for n in (32, 64):
        known, query = histogram.fixture(n, 'band')
        oracle = histogram.band_oracle(known, query, 2)
        height = sum(map(abs, known.counts))
        for family in (DEFAULT, OTHER):
            model = joint.JointRelation(n, *family)
            before = joint.JointCountState(model, known.counts, -3, height+7, height+7)
            budget = replace(BUDGET, live_cells=8*n, arithmetic=32768, step_cap=before.steps)
            with patch.object(joint.JointRelation, 'materialize_program', side_effect=AssertionError('world expansion')):
                actual = decoder.passive_plan(before, query, budget)
            excesses, normalization = [0, 0], 0
            for eta, prior in zip(model.rates, model.prior):
                a, b = int(model.scale*eta), int(model.scale*(1-eta))
                constant = int(prior*model.prior_scale)*b**2*a**5
                z0, z1 = (constant*sum(coefficient*a**(height-energy)*b**energy for energy, coefficient in part)
                          for part in oracle)
                normalization += z0+z1
                excesses[0] += (b-1)*z0+(a-1)*z1
                excesses[1] += (a-1)*z0+(b-1)*z1
            assert (actual.excesses, actual.normalization) == (tuple(excesses), normalization)
            rows.append({'n': n, 'rates': tuple(map(str, model.rates)), 'worlds': str(model.K),
                         'steps': before.steps, 'workspace_bytes': actual.workspace_bytes,
                         'cell_bytes': actual.cell_bytes, 'table_geometry': dict(actual.shape),
                         'total_multiplications': actual.multiplications, 'total_additions': actual.additions,
                         'maximum_integer_bits': actual.maximum_integer_bits, 'compacted_cells': actual.compacted_cells})
    model = joint.JointRelation(256, *OTHER)
    counts = tuple(1 if j == i+1 else 0 for i in range(256) for j in range(i+1, 256))
    state = joint.JointCountState(model, counts, -1, 258, 258)
    budget = replace(BUDGET, live_cells=2048, arithmetic=65536, step_cap=258)
    plan = decoder.passive_plan(state, (0, 255), budget)
    forest = forest_decode(256, 258, counts, -1, (0, 255), model.rates, model.prior)
    assert decoder.reference(plan)[5] == forest['forecast_zero']
    rows.append({'n': 256, 'rates': tuple(map(str, model.rates)), 'worlds': str(model.K),
                 'steps': state.steps, 'workspace_bytes': plan.workspace_bytes, 'maximum_integer_bits': plan.maximum_integer_bits,
                 'total_multiplications': plan.multiplications, 'total_additions': plan.additions,
                 'oracle': 'independent positive forest path recurrence'})
    return rows


def boundaries():
    model = joint.JointRelation(3, *DEFAULT)
    before = joint.JointCountState(model, (1, -1, 0), 0, 4, 4)
    rules, sources = model.rules(), model.source_row(1)
    with memoryview(bytearray(decoder.workspace_bytes(model, BUDGET))) as scratch:
        plan = decoder.prepare_bound(model, before, rules, sources, BUDGET, scratch)
        changes = [replace(plan, query=(1, 0)), replace(plan, order=plan.order[::-1]),
            replace(plan, excesses=tuple(2*v for v in plan.excesses), normalization=2*plan.normalization),
            replace(plan, normalization=plan.normalization+1), replace(plan, maximum_integer_bits=0),
            replace(plan, multiplications=plan.multiplications-1), replace(plan, additions=plan.additions-1),
            replace(plan, compacted_cells=plan.compacted_cells+1), replace(plan, cell_bytes=plan.cell_bytes+1),
            replace(plan, workspace_bytes=plan.workspace_bytes-1), replace(plan, bit_limit=plan.bit_limit-1),
            replace(plan, before=replace(before, cursor=5)), replace(plan, before=replace(before, steps=6)),
            replace(plan, before=replace(before, diagonal=2)), replace(plan, query=(False, 1)),
            replace(plan, shape=((plan.shape[0][0], F(plan.shape[0][1])),)+plan.shape[1:])]
        extra = replace(plan)
        object.__setattr__(extra, 'authority', True)
        changes.append(extra)
        for changed in changes:
            rejects(lambda: decoder.check_bound_plan(changed, model, before, rules, sources, BUDGET, scratch))
        substitutes = [lambda: decoder.check_bound_plan(plan, model, before, rules, model.source_row(3), BUDGET, scratch),
            lambda: decoder.prepare_bound(replace(model, rates=model.rates[::-1]), before, rules, sources, BUDGET, scratch),
            lambda: decoder.prepare_bound(replace(model, prior=(F(1, 3), F(2, 3))), before, rules, sources, BUDGET, scratch),
            lambda: decoder.prepare_bound(model, before, replace(rules, base=(F(2), F(1))), sources, BUDGET, scratch),
            lambda: decoder.prepare_bound(model, before, rules, {}, BUDGET, scratch),
            lambda: decoder.prepare(joint.observe(before, (0, 1), 0), (0, 1), BUDGET, scratch),
            lambda: joint.attach(joint.observe(before, (0, 1), 0), 2)]
        for case in substitutes:
            rejects(case)
    shape = dict(plan.shape)
    caps = [('join_cells', shape['largest_join_cells']-1), ('live_cells', shape['peak_live_integer_cells']-1),
            ('arithmetic', plan.multiplications+plan.additions-1), ('step_cap', 3),
            ('integer_bits', plan.integer_envelope+1023)]
    for key, value in caps:
        budget = replace(BUDGET, **{key: value})
        backing = bytearray([165])*decoder.workspace_bytes(model, budget)
        with memoryview(backing) as scratch:
            original = bytes(scratch)
            rejects(lambda: decoder.prepare(before, (0, 1), budget, scratch), ArithmeticUnresolved)
            assert bytes(scratch) == original
    # Height zero is not an empty joint history. The total clock is needed
    # for both the posterior and admission before the first workspace write.
    canceled = joint.JointCountState(model, (0, 0, 0), 0, 4, 4)
    budget = replace(BUDGET, step_cap=3)
    with memoryview(bytearray([165])*decoder.workspace_bytes(model, budget)) as scratch:
        old_bytes = bytes(scratch)
        rejects(lambda: decoder.prepare(canceled, (0, 1), budget, scratch), ArithmeticUnresolved)
        assert bytes(scratch) == old_bytes
    size = decoder.workspace_bytes(model, BUDGET)
    for scratch in (memoryview(bytearray(size-1)), memoryview(bytes(size)), memoryview(bytearray(2*size))[::2]):
        rejects(lambda: decoder.prepare(before, (0, 1), BUDGET, scratch))
        scratch.release()
    dense_model = joint.JointRelation(16, *DEFAULT)
    dense = joint.JointCountState(dense_model, (1,)*120, 0, 120, 120)
    rejects(lambda: decoder.passive_plan(dense, (0, 1)), ArithmeticUnresolved)
    # A fail after admitted execution may change scratch. The caller retains
    # its own pinned view; there is no automatic release/refund or state commit.
    backing = bytearray([165])*size
    saved = pack(before)
    original_preflight = decoder._preflight
    def fault(*args):
        result = original_preflight(*args)
        return (1,)+result[1:]
    with memoryview(backing) as owner:
        with patch.object(decoder, '_preflight', fault):
            with memoryview(owner) as borrowed:
                rejects(lambda: decoder.prepare(before, (0, 1), BUDGET, borrowed), ArithmeticUnresolved)
        rejects(lambda: backing.extend(b'x'), BufferError)
        assert backing != bytearray([165])*size and pack(before) == saved
    return {'bound_plan_refusals': len(changes), 'complete_input_refusals': len(substitutes),
            'prewrite_resource_refusals': [key for key, _ in caps],
            'canceled_height_zero_step_refusal': True, 'workspace_shape_refusals': 3,
            'dense_n16_status': 'UNRESOLVED', 'postwrite_fault_keeps_input_and_caller_pin': True}


def admission_boundary():
    from fp_reference import ReferenceCompilerRuntime
    from audit_reference_construction import contract, zero_program, validate_residency
    runtime = ReferenceCompilerRuntime(contract(), zero_program(2))
    before = validate_residency(runtime)
    result = runtime.construct_candidate(joint.JointRelation(2, *DEFAULT))
    after = validate_residency(runtime)
    assert result.status == 'REJECTED_ADMISSIBILITY'
    assert before.candidates == after.candidates and before.programs == after.programs
    return {'runtime_status': result.status, 'registered_production_paths_changed': False,
            'no_indexed_joint_admission_or_constructor_certificate': True}


SECTIONS = {'indexing': indexing, 'enumeration': enumeration, 'orders': order_audit, 'zero_parts': zero_parts,
            'native': native_audit, 'larger': larger, 'boundaries': boundaries, 'admission': admission_boundary}


def run(section=None):
    report = {'status': 'PASS_JOINT_PARTITION_STORAGE_COMPONENT', 'complete_audit': section is None,
              'scope': 'Exact literal indexing, count transitions and caller-owned integer extent. No Runtime registration, device execution or completeness certificate.'}
    for key, function in SECTIONS.items():
        if section in (None, key):
            report[key] = function()
            print('PASS '+key, flush=True)
    assert 'torch' not in sys.modules
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=tuple(SECTIONS))
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert args.section is None or not args.write
    result = run(args.section)
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        OUTPUT.write_text(text, encoding='utf-8', newline='\n')
    print(text, end='')
