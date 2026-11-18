"""Direct comparison with R4's exact arithmetic and post-result gate bound."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import floor
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.numerics import log_enclosure
from fp_reference.program import (Binding, DelayedStateSpec, Product, Program,
                                  SemanticRules, Source, SourceSpec, State, Sum, Term)
from fp_reference.semantics import evaluate, reset_delayed


def count_program():
    # All eight pair/label counts have identical initialization and update.
    # Current score sources contain the two inputs and yesterday's reveal.
    names = ("x", "z", "previous_x", "previous_z", "previous_y")
    specs = tuple(SourceSpec(f"{name}{i}", "n", int(name.startswith("previous")), 1)
                  for name, i in product(names, range(2)))
    nodes = [Source(s.source_id) for s in specs]
    atoms = {node.source_id: i for i, node in enumerate(nodes)}
    states, bindings, contributions = [], [], [[], []]

    def append(node):
        nodes.append(node)
        return len(nodes)-1

    for x, z in product(range(2), repeat=2):
        current = append(Product("n", atoms[f"x{x}"], atoms[f"z{z}"]))
        previous = append(Product("n", atoms[f"previous_x{x}"], atoms[f"previous_z{z}"]))
        for y in range(2):
            name = f"count{x}{z}{y}"
            states.append(DelayedStateSpec(name, "n", 1, 16))
            old = append(State(name))
            increment = append(Product("n", previous, atoms[f"previous_y{y}"]))
            count = append(Sum("n", (Term(old, 0), Term(increment, 0))))
            bindings.append(Binding(name, count))
            contributions[y].append(append(Product("n", current, count)))
    heads = tuple(append(Sum("n", tuple(Term(i, 0) for i in terms))) for terms in contributions)
    rules = SemanticRules(specs, ("n",), (("n", "n", "n"),), "n", (1, 1), tuple(states))
    return Program(tuple(nodes), 1, heads, tuple(bindings)), rules


def observe_sources(pair, previous):
    seen = dict(x=pair[0], z=pair[1])
    if previous is not None:
        seen.update(zip(("previous_x", "previous_z", "previous_y"), previous))
    return {f"{name}{i}": int(seen.get(name) == i)
            for name in ("x", "z", "previous_x", "previous_z", "previous_y") for i in range(2)}


def compare_predictors():
    program, rules = count_program()
    delayed, last = reset_delayed(rules), None
    counts = Counter()
    contexts = tuple(product((0, 1), repeat=2))

    def predict(pair):
        evaluation = evaluate(program, rules, (1,), observe_sources(pair, last), delayed, bit_limit=128)
        frequencies = [1+counts[pair, y] for y in range(2)]
        table = tuple(F(c, sum(frequencies)) for c in frequencies)
        assert evaluation.probabilities == table
        return table, evaluation.delayed

    for cycle in range(4):
        for x, z in contexts:
            _, delayed = predict((x, z))
            label = x ^ z ^ int(cycle == 3)
            counts[(x, z), label] += 1
            last = (x, z, label)
    table_likelihood = opaque_likelihood = F(1)
    for x, z in contexts:
        table, _ = predict((x, z))
        clean = x ^ z
        assert table[clean] == F(2, 3)
        sources = [F(3, 4) if symbol == clean else F(1, 4) for symbol in (x, z)]
        # Best possible noisy-copy mixture even with arbitrary contextual gates.
        correct = min(max(F(3, 4), min(sources)), max(sources))
        table_likelihood *= table[clean]**3 * (1-table[clean])
        opaque_likelihood *= correct**3 * (1-correct)
    assert table_likelihood > opaque_likelihood
    return dict(training_events=16, common_prefix_predictions=16, frozen_contexts=len(contexts),
                graph=program.counts(), trained_probability_on_clean_label="2/3",
                table_population_likelihood_power_16=str(table_likelihood),
                oracle_router_population_likelihood_power_16=str(opaque_likelihood))


def contextual():
    vertices = [(F(a, 3), F(b, 3), F(3-a-b, 3)) for a in range(4) for b in range(4-a)]
    readouts = [a for a in product((0, F(1, 2), 1), repeat=3) if any(a)]
    comparisons = 0
    for first, second in product(vertices, repeat=2):
        policies = [tuple(t*x+(1-t)*y for x, y in zip(first, second))
                    for t in (0, F(1, 3), F(2, 3), 1)]
        envelope = [max(values) for values in zip(*policies)]
        factor = sum(envelope)
        fixed = [v/factor for v in envelope]
        worst_ratio = F(0)
        for w, a in product(policies, readouts):
            contextual_score = sum(v*b for v, b in zip(w, a))
            fixed_score = sum(v*b for v, b in zip(fixed, a))
            assert contextual_score <= factor*fixed_score
            if fixed_score:
                worst_ratio = max(worst_ratio, contextual_score/fixed_score)
            comparisons += 1
        assert worst_ratio == factor <= 2
    receipt = json.loads(Path(__file__).with_name("text_capacity_result.json").read_text(), parse_float=F)
    result = receipt["ordinary_text"]
    fixed_lower = F(result["fixed_class_infimum_nats"][0])
    log_two = log_enclosure(F(2), terms=14, bit_limit=32768)
    lower = fixed_lower-log_two.upper
    assert lower > result["recorded_nats"]["transformer"]
    assert lower < result["recorded_nats"]["mkn5"]
    return dict(pointwise_comparisons=comparisons, tag_readouts_attain_domination_constant=True,
                two_vector_text_lower_billionths_of_nat=floor(10**9*lower))


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("this audit requires assertions")
    print(json.dumps(dict(r4_and_table=compare_predictors(), contextual=contextual()), indent=2))
