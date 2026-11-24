"""Replay a learned sensor choice in the exact Foundation R4 evaluator."""

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from controlled_sensing import COSTS, SEEDS, UNIT
from positive_comparison import SOURCE


def field(buf, i, width):
    return (int.from_bytes(buf, "little") >> (width * i)) & ((1 << width) - 1)


def check(info):
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

    packet = bytes.fromhex(info["action_hex"])
    narrow = packet[0] == 1
    assert packet[:4] == bytes((1 if narrow else 2, 2, 3, 1))
    first = [field(packet[4:5], u, 1) if narrow else u for u in range(8)]
    width = 2 if narrow else 8
    second = packet[5:7] if narrow else packet[4:12]
    policy = packet[7:] if narrow else packet[12:]
    probs = bytes.fromhex(info["q16_hex"])

    names = [
        *(f"u{i}" for i in range(8)),
        *(f"v{i}" for i in range(8)),
        "j0",
        "j1",
        "j2",
    ]
    states = [*(f"p{i}" for i in range(width)), "s0", "s1"]
    specs = tuple(DelayedStateSpec(s, "bit", 1, 1) for s in states)
    nodes = [*(Source(a) for a in names), *(State(s) for s in states)]
    slots = [1]

    def insert(node):
        nodes.append(node)
        return len(nodes) - 1

    def add(parents):
        return insert(Sum("bit", tuple(Term(p, 0) for p in parents)))

    first_bodies = [add(u for u in range(8) if first[u] == i) for i in range(width)]
    pairs = [
        insert(Product("bit", len(names) + i, 8 + v))
        for i in range(width)
        for v in range(8)
    ]
    second_bodies = [
        add(p for k, p in enumerate(pairs) if field(second, k, 1) == s)
        for s in range(2)
    ]
    queries = [
        insert(Product("bit", len(names) + width + s, 16 + j))
        for s in range(2)
        for j in range(3)
    ]
    actions = [
        add(q for k, q in enumerate(queries) if field(policy, k, 2) == a)
        for a in range(3)
    ]
    heads = []
    for agree in (False, True):
        terms = []
        for k, q in enumerate(queries):
            n = field(probs, k, 16)
            excess = (n if agree else UNIT - n) - 1
            if excess not in slots:
                slots.append(excess)
            terms.append(Term(q, slots.index(excess)))
        heads.append(insert(Sum("bit", tuple(terms))))
    rules = SemanticRules(
        tuple(SourceSpec(a, "bit", 0, 1) for a in names),
        ("bit",),
        (("bit", "bit", "bit"),),
        "bit",
        (1, 1),
        specs,
    )
    bindings = tuple(
        Binding(s, b) for s, b in zip(states, first_bodies + second_bodies, strict=True)
    )
    prog = Program(tuple(nodes), len(slots), tuple(heads), bindings)

    def step(name, history):
        return evaluate(prog, rules, slots, {a: int(a == name) for a in names}, history)

    for u in range(8):
        pre = step(names[u], reset_delayed(rules))
        assert [h[0] for _, h in pre.delayed] == [
            int(i == first[u]) for i in range(width)
        ] + [0, 0]
        for v in range(8):
            post = step(names[8 + v], pre.delayed)
            s = field(second, 8 * first[u] + v, 1)
            assert [h[0] for _, h in post.delayed] == [0] * width + [1 - s, s]
            for j in range(3):
                last = step(names[16 + j], post.delayed)
                k = 3 * s + j
                assert [last.values[p] for p in actions] == [
                    int(a == field(policy, k, 2)) for a in range(3)
                ]
                assert last.probabilities[1] == Fraction(field(probs, k, 16), UNIT)
    return len(nodes), len(specs), len(slots)


def response_class_check():
    import controlled_sensing as cs
    import response_classes as rc

    programs = contexts = 0
    for family in rc.LAWS:
        seed = rc.SEEDS[0]
        truth = rc.environment(seed, family)
        count, hits = rc.observations(cs.episodes(seed, truth), cs.BUDGETS[-1])
        pred, _ = rc.fit(count, hits)
        for cost in cs.COSTS:
            arms = cs.control_tables(pred.mean(axis=4), cost)
            for arm in ("one_then_one", "three_then_one"):
                m = arms[arm]
                _, selected, _ = rc.installation(pred, m)
                for z in range(2):
                    info = {
                        "action_hex": m.packet.hex(),
                        "q16_hex": selected[:, :, z].tobytes().hex(),
                    }
                    check(info)
                    programs += 1
                    contexts += 192
    print(
        "scalar R4 response branches",
        programs,
        "context and observed-bit checks",
        contexts,
    )


def run(response_classes=False, posterior=False, calibration=False, grouped=False):
    folder = "src/reference_compiler"
    here = Path(__file__).resolve().parent
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, folder]
    )
    models = json.loads((here / "controlled_sensing_result.json").read_text())[
        "largest_budget_installations"
    ]
    with TemporaryDirectory(prefix="fp-sensor-reference-") as tmp:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / folder))
        if grouped:
            from grouped_r4 import run_prefix

            print(run_prefix())
            return
        if calibration:
            from coin_calibration import r4_fitted_counter

            receipt = json.loads((here / "coin_calibration_timing.json").read_text())
            print(r4_fitted_counter(receipt))
            return
        if posterior:
            from partition_posterior import r4_example

            r4_example()
            return
        if response_classes:
            response_class_check()
            return
        for arm in ("one_then_one", "three_then_one"):
            sizes = [
                check(models[f"{seed}/{name}/{c}/{arm}"])
                for seed in SEEDS
                for name in ("tabular", "rank_one")
                for c in COSTS
            ]
            print(
                arm,
                "installations",
                len(sizes),
                "complete context checks",
                192 * len(sizes),
                "nodes, delayed cells, slots",
                sorted(set(sizes)),
            )


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the comparison requires assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--response-classes", action="store_true")
    group.add_argument("--partition-posterior", action="store_true")
    group.add_argument("--coin-calibration", action="store_true")
    group.add_argument("--grouped-reset", action="store_true")
    args = parser.parse_args()
    run(
        args.response_classes,
        args.partition_posterior,
        args.coin_calibration,
        args.grouped_reset,
    )
