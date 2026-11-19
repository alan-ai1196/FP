"""Evaluate a data-inferred categorical transition table in the pinned R4 arithmetic."""
from fractions import Fraction
from pathlib import Path
import subprocess
import sys

SOURCE = "a674dda8985be1dd316b102da4fa00a42c837819"


def compare(root, alphabet, table, signs, model):
    root = Path(root).resolve()
    version = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if version != SOURCE:
        raise ValueError("the comparison requires the pinned reconstruction checkout")
    subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", "src/reference_compiler"],
                   check=True)
    sys.path.insert(0, str(root / "src/reference_compiler"))
    from fp_reference.program import (Binding, DelayedStateSpec, Product, Program, SemanticRules,
                                      Source, SourceSpec, State, Sum, Term)
    from fp_reference.semantics import evaluate, reset_delayed

    names = ("reset", *alphabet)
    specs = tuple(SourceSpec(a, "n", 0, 1) for a in names)
    states = tuple(DelayedStateSpec(f"s{i}", "n", 1, 1) for i in range(len(table)))
    nodes = [Source(a) for a in names]
    old = []
    incoming = [[] for _ in states]
    incoming[0].append(0)
    for row in states:
        old.append(len(nodes))
        nodes.append(State(row.state_id))
    for i, row in enumerate(table):
        for a, dest in enumerate(row):
            incoming[dest].append(len(nodes))
            nodes.append(Product("n", old[i], a + 1))
    bodies = []
    for terms in incoming:
        bodies.append(len(nodes))
        nodes.append(Sum("n", tuple(Term(t, 0) for t in terms)))
    heads = []
    for sign in (-1, 1):
        heads.append(len(nodes))
        nodes.append(Sum("n", tuple(Term(body, 1) for body, s in zip(bodies, signs) if s == sign)))
    rules = SemanticRules(specs, ("n",), (("n", "n", "n"),), "n", (1, 1), states)
    prog = Program(tuple(nodes), 2, tuple(heads),
                   tuple(Binding(row.state_id, b) for row, b in zip(states, bodies)))
    if model.amplitude >= 1:
        raise ValueError("finite positive-base comparison requires positive label noise")
    theta = (1, 2 * model.amplitude / (1 - model.amplitude))

    def event(letter, delayed):
        return evaluate(prog, rules, theta, {a: int(a == letter) for a in names}, delayed, bit_limit=128)

    start = event("reset", reset_delayed(rules))
    pairs = [(0, start.delayed, model.initial)]
    seen = set(pairs)
    assert start.probabilities[1] == model.forecast("")
    for i, delayed, state in pairs:
        assert tuple(v[0] for _, v in delayed) == tuple(int(i == j) for j in range(len(table)))
        for ai, a in enumerate(alphabet):
            observed = event(a, delayed)
            after = model.step(state, a)
            assert observed.probabilities[1] == (1 + model.amplitude * after[0]) / 2
            nxt = table[i][ai], observed.delayed, after
            if nxt not in seen:
                seen.add(nxt)
                pairs.append(nxt)
    assert len(pairs) == len(table)
    return dict(letters=len(alphabet), complete_joint_states=len(pairs),
                exact_evaluations=1 + len(table) * len(alphabet), nodes=len(nodes),
                sources=len(specs), delayed_cells=len(states), products=len(table) * len(alphabet),
                sums=len(table) + 2, sum_terms=sum(len(n.terms) for n in nodes if isinstance(n, Sum)),
                parameter_slots=len(theta), learned_excess_mass=str(Fraction(theta[1])))
