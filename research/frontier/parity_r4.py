"""Run the learned synopsis and all query routes with Foundation R4's exact arithmetic."""

import json
import subprocess
import sys
from fractions import Fraction
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from parity_acquisition import (
    SIZE,
    canonical_basis,
    choose,
    episodes,
    fit_options,
    package,
    subspaces,
)
from positive_comparison import SOURCE


def compare():
    from fp_reference.program import (
        Binding,
        DelayedStateSpec,
        Product,
        Program,
        SemanticRules,
        Source,
        SourceSpec,
        Sum,
        Term,
    )
    from fp_reference.semantics import evaluate, reset_delayed

    def circuit(ninputs, masks, encoder):
        names = ["unit", *(f"x{i}_{v}" for i in range(ninputs) for v in (0, 1))]
        nodes = [Source(name) for name in names]

        def insert(node):
            nodes.append(node)
            return len(nodes) - 1

        zero = insert(Sum("bit", ()))
        outputs = []
        for mask in masks:
            pairs = [(1 + 2 * i, 2 + 2 * i) for i in range(ninputs) if mask & (1 << i)]
            if not pairs:
                outputs.append((0, zero))
                continue
            even, odd = pairs[0]
            for other_even, other_odd in pairs[1:]:
                terms = []
                for left, right in (
                    (even, other_even),
                    (odd, other_odd),
                    (even, other_odd),
                    (odd, other_even),
                ):
                    terms.append(Term(insert(Product("bit", left, right)), 0))
                even = insert(Sum("bit", tuple(terms[:2])))
                odd = insert(Sum("bit", tuple(terms[2:])))
            outputs.append((even, odd))
        states = ()
        bindings = ()
        if encoder:
            states = tuple(
                DelayedStateSpec(f"stored{i}", "bit", 1, 1) for i in range(len(outputs))
            )
            bindings = tuple(
                Binding(spec.state_id, pair[1]) for spec, pair in zip(states, outputs)
            )
            heads = (zero, zero)
            theta = (1,)
        else:
            heads = tuple(insert(Sum("bit", (Term(root, 1),))) for root in outputs[0])
            theta = (1, 6)
        interface = tuple(SourceSpec(name, "bit", 0, 1) for name in names)
        rules = SemanticRules(
            interface, ("bit",), (("bit", "bit", "bit"),), "bit", (1, 1), states
        )
        program = Program(tuple(nodes), len(theta), heads, bindings)

        def run(bits):
            source = {"unit": 1}
            for i, value in enumerate(bits):
                source[f"x{i}_0"] = 1 - value
                source[f"x{i}_1"] = value
            return evaluate(program, rules, theta, source, reset_delayed(rules))

        return run, program.counts()

    # Fit against the registration's labeled examples and serialize the actual routes.
    teacher = (
        np.random.Generator(np.random.PCG64(23112601))
        .permutation(SIZE)
        .astype(np.uint8)
    )
    train_x, train_y = episodes(23112602, 256, teacher)
    optimum, nlayouts, _, _ = choose(subspaces(4), fit_options(train_x, train_y), 256)
    _, space, routes = optimum
    basis = canonical_basis(space)
    packed = package(basis, routes, False)
    header_len = (7 * len(basis) + 7) // 8
    header = int.from_bytes(packed[:header_len], "little")
    basis = [(header >> (7 * i)) & 127 for i in range(len(basis))]
    query_entries = int.from_bytes(packed[header_len:], "little")
    encode, encode_counts = circuit(7, basis, True)
    decoders = [circuit(n, [(1 << n) - 1], False) for n in range(6)]
    # R4 is evaluated once for every distinct exposed argument vector, then composed
    # exhaustively. This memoization is for checking exact semantics, not deployment timing.
    native_prob = {}
    for n, (run, _) in enumerate(decoders):
        for values in range(1 << n):
            bits = tuple((values >> i) & 1 for i in range(n))
            native_prob[bits] = run(bits).probabilities
    reads = raw_reads = cases = 0
    for word in range(SIZE):
        native = encode(tuple((word >> i) & 1 for i in range(7)))
        state = tuple(int(history[0]) for _, history in native.delayed)
        assert all(
            bit == ((word & mask).bit_count() & 1) for bit, mask in zip(state, basis)
        )
        for task in range(SIZE):
            entry = (query_entries >> (9 * task)) & 511
            assert not entry & 256
            selection = entry & 15
            address = (entry >> 4) & 7
            flip = (entry >> 7) & 1
            inputs = tuple(bit for i, bit in enumerate(state) if selection & (1 << i))
            reads += len(inputs)
            if address:
                inputs += ((word >> (address - 1)) & 1,)
                raw_reads += 1
            expected = (word & int(teacher[task])).bit_count() % 2
            assert native_prob[inputs][expected ^ flip] == Fraction(7, 8)
            cases += 1
    return {
        "revision": SOURCE,
        "layouts_fit": nlayouts,
        "model_bytes": len(packed),
        "stored_basis": basis,
        "r4_encoder": encode_counts,
        "r4_decoder_by_arity": [counts for _, counts in decoders],
        "r4_encoder_evaluations": SIZE,
        "r4_query_argument_evaluations": len(native_prob),
        "composite_word_task_checks": cases,
        "synopsis_query_taps": reads,
        "raw_query_taps": raw_reads,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    folder = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(root), "archive", "--format=zip", SOURCE, folder]
    )
    with TemporaryDirectory(prefix="fp-parity-reference-") as staged:
        with ZipFile(BytesIO(archive)) as pinned:
            pinned.extractall(staged)
        sys.path.insert(0, str(Path(staged) / folder))
        print(json.dumps(compare(), indent=2))
