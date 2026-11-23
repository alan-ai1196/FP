"""Evaluate a data-inferred categorical transition table in the pinned R4 arithmetic."""
from fractions import Fraction
from pathlib import Path
import subprocess
import sys

SOURCE = "a674dda8985be1dd316b102da4fa00a42c837819"


def categorical_evaluator(root, alphabet, table, readouts, theta):
    root = Path(root).resolve()
    version = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if version != SOURCE:
        raise ValueError("the comparison requires the pinned reconstruction checkout")
    subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", "src/reference_compiler"],
                   check=True)
    sys.path.insert(0, str(root / "src/reference_compiler"))
    return categorical_program(alphabet, table, readouts, theta)


def categorical_program(alphabet, table, readouts, theta):
    """Construct the program after the caller loads the pinned R4 evaluator."""
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
    for terms in readouts:
        heads.append(len(nodes))
        nodes.append(Sum("n", tuple(Term(bodies[state], slot) for state,slot in terms)))
    rules = SemanticRules(specs, ("n",), (("n", "n", "n"),), "n", (1,)*len(heads), states)
    prog = Program(tuple(nodes), len(theta), tuple(heads),
                   tuple(Binding(row.state_id, b) for row, b in zip(states, bodies)))

    def event(letter, delayed):
        return evaluate(prog, rules, theta, {a: int(a == letter) for a in names}, delayed, bit_limit=128)

    start = event("reset", reset_delayed(rules))
    size = dict(letters=len(alphabet),nodes=len(nodes),sources=len(specs),delayed_cells=len(states),
                products=len(table)*len(alphabet), sums=len(table)+len(heads),
                sum_terms=sum(len(n.terms) for n in nodes if isinstance(n,Sum)),parameter_slots=len(theta))
    return event,start,size


def compare(root, alphabet, table, signs, model):
    if model.amplitude >= 1:
        raise ValueError("finite positive-base comparison requires positive label noise")
    theta = (1, 2 * model.amplitude / (1 - model.amplitude))
    readouts = [[(i,1) for i,s in enumerate(signs) if s==sign] for sign in (-1,1)]
    event,start,size = categorical_evaluator(root,alphabet,table,readouts,theta)
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
    return dict(**size,complete_joint_states=len(pairs),exact_evaluations=1+len(table)*len(alphabet),
                learned_excess_mass=str(Fraction(theta[1])))


def compare_emissions(root, alphabet, actions, emissions):
    table = tuple(zip(*actions,strict=True))
    scale = 2/min(p for row in emissions for p in row)
    theta = (1, *(scale*p-1 for row in emissions for p in row))
    readouts = [[(i,1+i*len(alphabet)+a) for i in range(len(table))] for a in range(len(alphabet))]
    event,initial,size = categorical_evaluator(root,alphabet,table,readouts,theta)
    reached = {0:initial}
    queue = [0]
    assert tuple(initial.probabilities)==tuple(emissions[0])
    for i in queue:
        for a,letter in enumerate(alphabet):
            after = event(letter,reached[i].delayed)
            destination = table[i][a]
            assert tuple(after.probabilities)==tuple(emissions[destination])
            assert tuple(row[0] for _,row in after.delayed)==tuple(int(j==destination) for j in range(len(table)))
            if destination not in reached:
                reached[destination]=after
                queue.append(destination)
    assert len(reached)==len(table)
    return dict(**size,complete_joint_states=len(reached),exact_evaluations=1+len(table)*len(alphabet))
