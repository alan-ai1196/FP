"""Exact complete native token trajectories and sparse-source counterexamples."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token')]
from fp_reference.program import Sum, Term, Product
from fp_reference.learner import LearnerSpec, initial_state, observe_event, commit_event
from fp_reference.semantics import evaluate
from causal_tokens import TokenSources
import native_readout as readout
import native_tokens as tokens

OUTPUT = ROOT/'evidence/minimal/FP_NATIVE_TOKENS.json'


def refuses(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('expected refusal')


def complete(state):
    return tuple(state.parameter(i) for i in range(state.definition.slot_count))


def same(state, native):
    assert complete(state) == native.theta
    assert tuple(state.gradient(i) for i in range(state.definition.slot_count)) == native.gradient_sum
    assert (state.cursor, state.output.unit_count, state.output.optimizer_steps) == (native.cursor, native.unit_count, native.optimizer_steps)


def fixture(unit, kind):
    sources = TokenSources(2, 3)
    output = readout.Spec((F(1, 2), F(3, 4)), 7, 5, F(1, 16), unit)
    # A tied core slot, two distinct PRODUCTs, a shared square, repeated final
    # feature and unused parameter. No hand simplification in the literal G.
    nodes = (Sum('f', (Term(0, 0), Term(2, 1), Term(4, 0))),
             Sum('f', (Term(1, 2), Term(3, 3), Term(5, 4))),
             Product('f', 6, 7), Product('f', 6, 6),
             Sum('f', (Term(8, 5), Term(9, 6), Term(0, 5))), Product('f', 8, 9))
    definition = tokens.Definition(sources, 2, nodes, 8, (6, 7, 8, 9, 10, 11, 8), output)
    embedding = (1, 3) if kind != 'zero-embedding' else (0, 0)
    core = (4, 3, 5, 2, 6, 3, 4, 7) if kind != 'zero-core' else (0,)*8
    overrides = ((0, 0, 0), (1, 1, 5), (2, 1, 2)) if kind != 'zero-embedding' else ()
    state = tokens.initialize(definition, embedding, core, (0, 1, 2, 3, 2, 4, 1),
        embedding_overrides=overrides, output_overrides=((0, 0, 3), (1, 6, 0)))
    return definition, state


def histories():
    results = []
    for unit, kind in product((1, 2), ('mixed', 'zero-embedding', 'zero-core')):
        definition, root = fixture(unit, kind)
        rules, graph = tokens.materialize(definition)
        spec = LearnerSpec(unit, definition.output.learning_rate, definition.output.grid_bits)
        cardinalities = definition.cardinalities()
        assert cardinalities['sources'] == len(rules.sources)
        assert cardinalities['parameter_slots'] == graph.slot_count
        assert cardinalities['sum_nodes'] == sum(type(n) is Sum for n in graph.nodes)
        assert cardinalities['product_nodes'] == sum(type(n) is Product for n in graph.nodes)
        assert cardinalities['incoming_edges'] == sum(len(n.terms) if type(n) is Sum else 2 if type(n) is Product else 0 for n in graph.nodes)
        observations = commits = words = 0
        original = complete(root)
        for word in product(range(2), repeat=6):
            state = root
            native = initial_state(graph, rules, original, 0, spec=spec, bit_limit=32768)
            for target in word:
                prediction = state.predict()
                expected_past = tuple(word[state.cursor-lag] if lag <= state.cursor else 2 for lag in range(1, 4))
                assert prediction.window.past == expected_past
                source_values = {f'lag{lag}/token{token}': F(int(expected_past[lag-1] == token))
                                 for lag in range(1, 4) for token in range(3)}
                ref = evaluate(graph, rules, native.theta, source_values, (), bit_limit=32768)
                offset = len(rules.sources)
                assert prediction.values == ref.values[offset:offset+len(prediction.values)]
                assert prediction.output.normalizer == ref.normalizer
                assert tuple(prediction.output.mass(y) for y in range(2)) == ref.masses
                assert tuple(prediction.output.probability(y) for y in range(2)) == ref.probabilities
                state = state.observe(prediction, target)
                native = observe_event(graph, native, spec, ref, target, bit_limit=32768)
                same(state, native)
                assert state.past == tuple(word[state.cursor-lag] if lag <= state.cursor else 2 for lag in range(1, 4))
                observations += 1
                # A zero-valued/dormant slot is retained; the unused slot's
                # gradient is exactly zero for a different, structural reason.
                assert state.gradient(definition.embedding_slots+7) == 0
                if state.output.unit_count == unit:
                    state, native = state.commit(), commit_event(native, spec, bit_limit=32768)
                    same(state, native)
                    commits += 1
            assert root.cursor == 0 and complete(root) == original
            words += 1
        results.append(dict(update_unit=unit, initializer=kind, complete_token_words=words,
            native_observations=observations, native_commits=commits, native_cardinalities=cardinalities))
        print(f'PASS histories unit={unit} initializer={kind}', flush=True)
    return results


def repeated_and_pending():
    d = tokens.Definition(TokenSources(2, 3), 1, (), 0, (0, 1, 2),
        readout.Spec((F(1),)*2, 3, 2, F(0), 1))
    state = tokens.initialize(d, (4,), (), (1, 2, 3),
        output_overrides=((1, 0, 2), (1, 1, 1), (1, 2, 4)))
    for _ in range(3):
        state = state.observe(state.predict(), 0).commit()
    cache = state.predict()
    _, adjoints = state.output.observe(cache.output, 1)
    pending = state.observe(cache, 1)
    assert pending.gradient(0) == sum(adjoints) == F(-4, 231)
    assert pending.gradient(0) != adjoints[-1] == F(-1, 33)
    assert pending.gradient(1) == pending.gradient(2) == 0

    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1),)*2, 1, 4, F(1, 8), 3))
    state = tokens.initialize(d, (8,), (), (4,), output_overrides=((1, 0, 8),))
    first = state.observe(state.predict(), 0)
    padding_gradient = first.gradient(2)
    assert padding_gradient != 0
    second = first.observe(first.predict(), 1)
    third = second.observe(second.predict(), 0)
    assert third.past == (0,) and third.gradient(2) == padding_gradient
    expected = state.parameter(2)-d.output.learning_rate*padding_gradient/d.output.update_unit
    expected = max(F(0), F((expected*d.output.grid).numerator//(expected*d.output.grid).denominator, d.output.grid))
    after = third.commit()
    assert after.parameter(2) == expected and after.parameter(2) != state.parameter(2)
    return dict(repeated_token_native_gradient=str(pending.gradient(0)), incorrect_last_occurrence_only=str(adjoints[-1]),
        earlier_padding_gradient_survives_later_inactive_events=str(padding_gradient),
        committed_padding_master=str(after.parameter(2)), initial_padding_master=str(state.parameter(2)))


def initialization_witnesses():
    d = tokens.Definition(TokenSources(2, 2), 1, (Product('f', 0, 1),), 0, (2,),
        readout.Spec((F(1, 2),)*2, 1, 4, F(1, 8), 1))
    root = tokens.initialize(d, (0,), (), (8,), output_overrides=((0, 0, 4),))
    for word in product(range(2), repeat=5):
        state = root
        for target in word:
            prediction = state.predict()
            assert tuple(prediction.output.probability(y) for y in range(2)) == (F(1, 2),)*2
            state = state.observe(prediction, target)
            assert all(state.gradient(i) == 0 for i in range(d.slot_count))
            state = state.commit()
            assert complete(state) == complete(root)
    d = tokens.Definition(TokenSources(2, 1), 1, (), 0, (0,),
        readout.Spec((F(1, 2),)*2, 1, 8, F(1, 8), 1))
    state = tokens.initialize(d, (128,), (), (64,))
    first = state.observe(state.predict(), 0)
    assert all(first.gradient(i) == 0 for i in range(d.embedding_slots))
    state = first.commit()
    second = state.observe(state.predict(), 1)
    assert second.gradient(0) != 0
    # Zero direct-SUM input is not necessarily dormant: its derivative is 1.
    zero = tokens.initialize(d, (0,), (), (64,), output_overrides=((0, 0, 128),))
    revived = zero.observe(zero.predict(), 0).commit()
    assert revived.parameter(2) > 0
    return dict(all_zero_product_embedding_invariant_words=32, invariant_events=160,
        symmetric_readout_first_core_gradient_zero=True, subsequent_core_gradient=str(second.gradient(0)),
        zero_direct_SUM_input_can_learn=True)


def binding():
    d, state = fixture(2, 'mixed')
    cache = state.predict()
    pending = state.observe(cache, 0)
    refuses(lambda: pending.observe(cache, 1))
    refuses(lambda: state.observe(replace(cache, values=cache.values[:-1]+(F(9),)), 0))
    refuses(lambda: pending.observe(replace(pending.predict(), window=cache.window), 0))
    refuses(lambda: state.observe(replace(cache, output=replace(cache.output, features=(F(0),)*7)), 0))
    refuses(lambda: state.observe(replace(cache, output=replace(cache.output, normalizer=F(99))), 0))
    refuses(lambda: state.observe(cache, True))
    refuses(lambda: state.commit())
    refuses(lambda: state.parameter(d.slot_count))
    refuses(lambda: state.gradient(-1))
    refuses(lambda: replace(d, nodes=(Product('f', d.input_nodes, 0),)))
    refuses(lambda: tokens.initialize(d, (1, 2), (1,)*d.slots, (1,)*7, embedding_overrides=((0, 0, 1), (0, 0, 2))))
    return dict(stale_context_and_core_cache_readout_clock_index_and_initializer_refusals=11)


def vocabulary_context():
    V, L, D = 50257, 512, 4
    offset = L*D
    nodes = (Sum('f', (Term(0, 0), Term(D, 1), Term(offset-D, 0))),
             Product('f', offset, 1), Product('f', offset, offset))
    definition = tokens.Definition(TokenSources(V, L), D, nodes, 3,
        (0, offset, offset+1, offset+2), readout.Spec((F(1, V),)*V, 4, 8, F(1, 64), 2))
    state = tokens.initialize(definition, (4, 6, 0, 2), (8, 4, 3), (1, 2, 1, 0),
        embedding_overrides=((17, 0, 12), (50256, 1, 3)), output_overrides=((17, 0, 4),))
    original = state
    word = (17, 50256, 50256, 31, 0, 50256, 17, 31)
    snapshots = []
    for target in word:
        cache = state.predict()
        expected = tuple(word[state.cursor-lag] if lag <= state.cursor else V for lag in range(1, L+1))
        assert cache.window.past == expected
        assert all(cache.values[lag*D+k] == state.parameter(token*D+k)
                   for lag, token in enumerate(expected) for k in range(D))
        state = state.observe(cache, target)
        if state.output.unit_count == 2:
            state = state.commit()
            snapshots.append(dict(cursor=state.cursor, embedding_exceptions=readout.field(state.embedding.overrides, 'nodes'),
                readout_exceptions=sum(readout.field(c.labels, 'nodes') for c in state.output.columns)))
    assert original.cursor == 0 and original.past == (V,)*L
    assert state.past[:len(word)] == tuple(reversed(word))
    assert state.past[len(word):] == (V,)*(L-len(word))
    return dict(vocabulary=V, context=L, width=D, events=len(word), complete_context_and_embedding_cache_checks=L*D*len(word),
        native_cardinalities=definition.cardinalities(), snapshots=snapshots,
        EOT_retained_without_reset=True, literal_large_graph_expanded=False,
        scope='indexed composition execution on synthetic token IDs; small-class full native equivalence is separate; no text quality, owned resource or timing claim')


def main():
    result = dict(status='PASS_EXACT_NATIVE_TOKENS', scope='complete passive fixed native token learner; no Runtime, AMP, model-quality or constructor certificate')
    for name, function in dict(native_histories=histories, sparse_gradient_witnesses=repeated_and_pending,
                               initialization=initialization_witnesses, binding=binding, full_vocabulary_context=vocabulary_context).items():
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
