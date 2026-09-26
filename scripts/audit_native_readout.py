"""Exact native readout/U audit, including full-vocabulary dense controls."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token')]
import native_readout as fast
from fp_reference.program import Program, SemanticRules, SourceSpec, Source, Sum, Term, Product
from fp_reference.learner import LearnerSpec, initial_state, ce_gradient, observe_event, commit_event
from fp_reference.semantics import evaluate

OUTPUT = ROOT/'evidence/minimal/FP_NATIVE_READOUT.json'


def refuses(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('expected refusal')


def tree(root):
    if root is None:
        return {}
    a, b = tree(root.left), tree(root.right)
    assert all(k < root.key for k in a) and all(k > root.key for k in b)
    assert abs(fast.field(root.left, 'height')-fast.field(root.right, 'height')) <= 1
    values = {**a, root.key: root.value, **b}
    assert root.height == 1+max(fast.field(root.left, 'height'), fast.field(root.right, 'height'))
    assert root.nodes == len(values) and root.weight == sum(values.values())
    assert root.total == sum(k*v for k, v in values.items())
    return values


def tree_audit():
    checks = 0
    for order in permutations(range(5)):
        root, values, retained = None, {}, []
        for key in order:
            retained.append((root, values.copy()))
            values[key] = 2*key
            root = fast.put(root, key, values[key])
            assert tree(root) == values
            checks += 1
        for deletion in (order, tuple(reversed(order)), tuple(range(5))):
            current, expected = root, values.copy()
            for key in deletion:
                current = fast.put(current, key, None)
                del expected[key]
                assert tree(current) == expected
                for threshold in range(-1, 6):
                    assert fast.above(current, threshold) == (
                        sum(v for k, v in expected.items() if k > threshold),
                        sum(k*v for k, v in expected.items() if k > threshold))
                checks += 1
        assert all(tree(old) == expected for old, expected in retained)
    return dict(insertion_permutations=120, invariant_and_update_checks=checks,
        zero_values_preserved=True, old_immutable_roots_preserved=True)


def complete(state):
    for column in state.columns:
        labels, values = tree(column.labels), tree(column.values)
        assert all(0 <= y < state.spec.labels for y in labels)
        counts = {}
        for label in range(state.spec.labels):
            raw = labels.get(label, column.default)
            counts[raw] = counts.get(raw, 0)+1
        assert values == counts
        assert column.total() == sum(column.master(y) for y in range(state.spec.labels))
    return tuple(state.parameter(y, k) for y in range(state.spec.labels) for k in range(state.spec.features))


def literal(spec, state):
    K, V = spec.features, spec.labels
    rules = SemanticRules(tuple(SourceSpec(str(i), 'f', 0, F(2)) for i in range(K)),
        ('f',), (('f', 'f', 'f'),), 'f', spec.base)
    graph = Program(tuple(Source(str(i)) for i in range(K))+tuple(
        Sum('f', tuple(Term(k, y*K+k) for k in range(K))) for y in range(V)), V*K, tuple(K+y for y in range(V)))
    learner = LearnerSpec(spec.update_unit, spec.learning_rate, spec.grid_bits)
    return rules, graph, learner, initial_state(graph, rules, complete(state), 0, spec=learner, bit_limit=32768)


def same(state, native):
    assert complete(state) == native.theta
    assert tuple(state.gradient(y, k) for y in range(state.spec.labels) for k in range(state.spec.features)) == native.gradient_sum
    assert (state.unit_count, state.cursor, state.optimizer_steps) == (native.unit_count, native.cursor, native.optimizer_steps)


def native_histories():
    rows = []
    cases = ((2, 1, 3, (1, 2), (), ((F(0), F(0)), (F(1), F(0)), (F(0), F(1)), (F(1), F(1))), 3),
             (3, 2, 2, (0, 0), ((0, 0, 3), (2, 1, 1)), ((F(1), F(1)), (F(1, 2), F(2))), 4))
    for V, unit, bits, defaults, overrides, features, length in cases:
        spec = fast.Spec(tuple(F(y+1, V) for y in range(V)), 2, bits, F(1, 3), unit)
        alphabet = tuple(product(features, range(V)))
        histories = observations = commits = 0
        for word in product(alphabet, repeat=length):
            state = fast.initialize(spec, defaults, overrides)
            rules, graph, learner, native = literal(spec, state)
            initial = state
            initial_theta = complete(state)
            for z, target in word:
                cache = state.predict(z)
                ref = evaluate(graph, rules, native.theta, {str(i): v for i, v in enumerate(z)}, (), bit_limit=32768)
                assert tuple(cache.mass(y) for y in range(V)) == ref.masses
                assert cache.normalizer == ref.normalizer
                assert tuple(cache.probability(y) for y in range(V)) == ref.probabilities
                state, _ = state.observe(cache, target)
                native = observe_event(graph, native, learner, ref, target, bit_limit=32768)
                same(state, native)
                observations += 1
                if state.unit_count == unit:
                    state, native = state.commit(), commit_event(native, learner, bit_limit=32768)
                    same(state, native)
                    commits += 1
            assert complete(initial) == initial_theta and initial.cursor == 0
            histories += 1
        rows.append(dict(labels=V, features=2, update_unit=unit, grid_bits=bits,
            complete_event_words=histories, native_observations=observations, native_commits=commits))
    return rows


def nonlinear_core():
    spec = fast.Spec((F(1, 3),)*3, 3, 3, F(1, 4), 1)
    state = fast.initialize(spec, (2, 0, 5), ((0, 1, 3), (1, 2, 1), (2, 0, 7)))
    rules = SemanticRules((SourceSpec('a', 'f', 0, F(2)), SourceSpec('b', 'f', 0, F(2))),
        ('f',), (('f', 'f', 'f'),), 'f', spec.base)
    # Shared square and a core slot repeated in a distinct SUM.
    core = (Source('a'), Source('b'), Sum('f', (Term(0, 0), Term(1, 1))),
            Product('f', 2, 2), Sum('f', (Term(0, 0), Term(1, 2))))
    graph = Program(core+tuple(Sum('f', tuple(Term(2+k, 3+3*y+k) for k in range(3))) for y in range(3)),
        12, (5, 6, 7))
    count = 0
    for core_theta in ((F(0),)*3, (F(1, 4), F(1, 2), F(3, 4)), (F(1), F(1, 8), F(0))):
        for a, b, target in product((F(0), F(1), F(2)), (F(0), F(1), F(2)), range(3)):
            u = core_theta[0]*a+core_theta[1]*b
            z = (u, u*u, core_theta[0]*a+core_theta[2]*b)
            cache = state.predict(z)
            _, adjoints = state.observe(cache, target)
            reference = evaluate(graph, rules, core_theta+complete(state), {'a': a, 'b': b}, (), bit_limit=32768)
            gradient = ce_gradient(graph, core_theta+complete(state), reference, target, bit_limit=32768)
            expected = ((adjoints[0]+2*u*adjoints[1]+adjoints[2])*a,
                        (adjoints[0]+2*u*adjoints[1])*b, adjoints[2]*b)
            assert gradient[:3] == expected
            assert tuple(cache.mass(y) for y in range(3)) == reference.masses
            count += 1
    return dict(exact_shared_PRODUCT_and_tied_core_gradient_cases=count,
        readout_slots_untied_from_core=True)


def counterexamples():
    results = []
    for master in (0, 1):
        spec = fast.Spec((F(1),)*2, 1, 0, F(1), 1)
        before = fast.initialize(spec, (master,))
        cache = before.predict((F(1),))
        pending, _ = before.observe(cache, 0)
        alpha, beta = pending.common[0], pending.corrections[0][1][0]
        wrong = max(0, master-(-(-alpha.numerator//alpha.denominator)))+beta.numerator//beta.denominator
        actual = pending.commit().parameter(0, 0)
        assert actual != wrong
        results.append(dict(initial_master=master, alpha=str(alpha), target_correction=str(beta),
            correct_target_master=str(actual), split_projection_and_correction_master=wrong))
    spec = fast.Spec((F(1),)*2, 1, 4, F(1), 2)
    before = fast.initialize(spec, (0,))
    cache = before.predict((F(1),))
    first, _ = before.observe(cache, 0)
    second, _ = before.observe(cache, 1)
    assert first.common == second.common and complete(first) == complete(second)
    assert first.gradient(0, 0) != second.gradient(0, 0)
    a, _ = first.observe(first.predict((F(0),)), 0)
    b, _ = second.observe(second.predict((F(0),)), 0)
    a, b = a.commit(), b.commit()
    assert complete(a) != complete(b)
    refuses(lambda: first.observe(cache, 0))
    refuses(lambda: before.observe(replace(cache, normalizer=cache.normalizer+1), 0))
    refuses(lambda: before.commit())
    refuses(lambda: before.observe(cache, True))
    refuses(lambda: before.predict((F(-1),)))
    return dict(noncommuting_projection_witnesses=results,
        equal_current_parameters_and_common_accumulator_have_different_future_commits=True,
        target_specific_pending_gradients_are_required=True, stale_and_changed_cache_refusals=True)


def full_vocabulary():
    V, K, events = 50257, 4, 8
    spec = fast.Spec((F(1, V),)*V, K, 8, F(1, 8), 2)
    state = fast.initialize(spec, (0, 1, 2, 4), ((17, 0, 256), (31, 2, 16)))
    # Independent dense controls store every master and every accumulated
    # gradient, apply ordinary CE and native SGD/floor to every coordinate.
    weights = [[state.parameter(y, k) for k in range(K)] for y in range(V)]
    gradients = [[F(0)]*K for _ in range(V)]
    maximum_height = 0
    snapshots = []
    for event in range(events):
        z = tuple(F((event*(k+3)+k) % 7, 3) for k in range(K))
        target = (event*7919+17) % V
        cache = state.predict(z)
        masses = [spec.base[y]+sum((w*x for w, x in zip(row, z)), F(0)) for y, row in enumerate(weights)]
        normalizer = sum(masses, F(0))
        assert cache.normalizer == normalizer
        for y in range(V):
            assert cache.mass(y) == masses[y]
            seed = 1/normalizer-(1/masses[y] if y == target else 0)
            for k in range(K):
                gradients[y][k] += seed*z[k]
        state, _ = state.observe(cache, target)
        for y in range(V):
            for k in range(K):
                assert state.gradient(y, k) == gradients[y][k]
        if state.unit_count == spec.update_unit:
            for y in range(V):
                for k in range(K):
                    value = max(F(0), weights[y][k]-spec.learning_rate*gradients[y][k]/spec.update_unit)
                    scaled = value*spec.grid
                    weights[y][k] = F(scaled.numerator//scaled.denominator, spec.grid)
                    gradients[y][k] = F(0)
            state = state.commit()
            assert complete(state) == tuple(value for row in weights for value in row)
            maximum_height = max(maximum_height, *(fast.field(c.labels, 'height') for c in state.columns),
                                 *(c.values.height for c in state.columns))
            snapshots.append(dict(cursor=state.cursor, stored_label_exceptions=sum(fast.field(c.labels, 'nodes') for c in state.columns),
                distinct_indexed_values=sum(c.values.nodes for c in state.columns)))
    return dict(labels=V, features=K, exact_dense_comparison_events=events, native_parameter_coordinates=V*K,
        complete_output_mass_checks=V*events, complete_pending_gradient_checks=V*K*events,
        complete_committed_parameter_checks=V*K*(events//spec.update_unit), maximum_index_height=maximum_height,
        final_offsets=[c.offset for c in state.columns], retained_storage_snapshots=snapshots,
        scope='full-vocabulary exact synthetic feature/control audit; no text loss, learned language structure, timing comparison or GPU execution')


def main():
    result = dict(status='PASS_EXACT_NATIVE_READOUT', scope='untied positive readout, complete pending gradients, feature adjoints and grid-projected SGD; passive refinement only')
    for name, function in dict(index=tree_audit, native=native_histories, core=nonlinear_core,
                               counterexamples=counterexamples, full_vocabulary=full_vocabulary).items():
        result[name] = function()
        print('PASS '+name, flush=True)
    assert 'torch' not in sys.modules
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = main()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
