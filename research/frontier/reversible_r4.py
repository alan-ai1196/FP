"""Replay the fitted quotient with actual positive R4 arithmetic on a finite horizon."""

import json
import subprocess
import sys
from fractions import Fraction as F
from io import BytesIO
from math import ceil, lcm
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from positive_comparison import SOURCE
from reversible_reports import decode, test_draw


def check(fit, horizon=16):
    from fp_reference.program import (
        Binding,
        DelayedStateSpec,
        Product,
        Program,
        SemanticRules,
        Source,
        SourceSpec,
        State,
        Sum,
        Term,
    )
    from fp_reference.semantics import evaluate, reset_delayed

    packet = bytes.fromhex(fit["packet_hex"])
    edges, pf, _, prior = decode(packet)
    q = len(prior)
    assert np.all(prior == 1 / q)
    f = list(map(F, map(float, pf)))
    fields = list(map(int, np.frombuffer(packet[-(2 + 2 * q) * 2 :], dtype="<u2")))
    g = [
        F(1 + h, 2 + n) for h, n in zip(fields[2 : 2 + q], fields[2 + q :], strict=True)
    ]
    denom = lcm(*(p.denominator for p in f))
    emissions = [[int(p * denom) for p in side] for side in ([1 - x for x in f], f)]
    cap = max(max(row) for row in emissions) ** (horizon + 1) - 1
    names = ["reset", "no", "yes", *(str(i) for i in range(len(edges))), "terminal"]
    sources = tuple(SourceSpec(name, "n", 0, 1) for name in names)
    cells = tuple(DelayedStateSpec(str(i), "n", 1, cap) for i in range(q))
    nodes = [Source(name) for name in names] + [State(s.state_id) for s in cells]
    slots = [F(1)]

    def insert(node):
        nodes.append(node)
        return len(nodes) - 1

    def linear(terms):
        terms_with_slots = []
        for parent, weight in terms:
            if weight == 0:
                continue
            if weight not in slots:
                slots.append(weight)
            terms_with_slots.append(Term(parent, slots.index(weight)))
        return insert(Sum("n", tuple(terms_with_slots)))

    def gate(i, j):
        return insert(Product("n", i, j))

    bodies = []
    inverse = np.argsort(edges, axis=1)
    for i in range(q):
        old = len(names) + i
        terms = []
        for j, row in enumerate(emissions):
            factor = row[i]
            terms.extend([(gate(old, j + 1), factor), (j + 1, factor - 1)])
        for a in range(len(edges)):
            terms.append((gate(len(names) + int(inverse[a, i]), 3 + a), 1))
        terms.append((gate(old, len(names) - 1), 1))
        bodies.append(linear(terms))
    ordinary = linear((j, 1) for j in range(len(names) - 1))
    heads = []
    for bit in (0, 1):
        terms = []
        for selector, probabilities in [(ordinary, f), (len(names) - 1, g)]:
            p = probabilities if bit else [1 - v for v in probabilities]
            # The same scale on both output heads preserves their normalized ratio.
            scale = max(1, ceil(1 / min(sum(probabilities), q - sum(probabilities))))
            subtotal = linear(
                (body, scale * prob) for body, prob in zip(bodies, p, strict=True)
            )
            terms.extend(
                [(gate(selector, subtotal), 1), (selector, scale * sum(p) - 1)]
            )
        heads.append(linear(terms))
    program = Program(
        tuple(nodes),
        len(slots),
        tuple(heads),
        tuple(Binding(c.state_id, b) for c, b in zip(cells, bodies, strict=True)),
    )
    rules = SemanticRules(sources, ("n",), (("n", "n", "n"),), "n", (1, 1), cells)
    raw_actions, raw, _ = test_draw(fit["seed"], horizon)
    checked = max_bits = 0
    for episode in (0, 1):
        weights = [1] * q
        delayed = reset_delayed(rules)

        def step(name, readout, weights):
            nonlocal delayed, checked, max_bits
            inp = {n: int(name == n) for n in names}
            result = evaluate(program, rules, slots, inp, delayed, bit_limit=8192)
            assert result.probabilities[1] == sum(
                w * p for w, p in zip(weights, readout, strict=True)
            ) / sum(weights)
            delayed = result.delayed
            assert [s[0] for _, s in delayed] == [w - 1 for w in weights]
            max_bits = max(max_bits, *(w.bit_length() for w in weights))
            checked += 1

        step("reset", f, weights)
        for t in range(horizon + 1):
            b = int(raw[t, episode])
            weights = [w * m for w, m in zip(weights, emissions[b], strict=True)]
            step(names[1 + b], f, weights)
            if t < horizon:
                a = int(raw_actions[t, episode])
                weights = [weights[j] for j in inverse[a]]
                step(str(a), f, weights)
        step("terminal", g, weights)
    return {
        "seed": fit["seed"],
        "matched_events": checked,
        "largest_observed_weight_bits": max_bits,
        "declared_cell_cap_bits": cap.bit_length(),
        **program.counts(),
    }


def run():
    here = Path(__file__).resolve().parent
    folder = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, folder]
    )
    fits = json.loads((here / "reversible_reports_result.json").read_text())["fits"]
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / folder))
        return {"reference": SOURCE, "fits": [check(f) for f in fits]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
