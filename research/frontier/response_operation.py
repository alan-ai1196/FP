"""Identify an unknown binary truth table from noisy responses on opaque tasks."""

import argparse
import json
from math import exp, log, sqrt
from pathlib import Path

import numpy as np
from parity_acquisition import SIZE, M, verify_result

BITS = 1 << np.arange(M, dtype=np.uint8)
WORDS = np.arange(SIZE, dtype=np.uint8)
PARITY = np.array([i.bit_count() % 2 for i in range(SIZE)], dtype=np.uint8)
PILOTS = np.append(BITS, np.uint8(3))
ETA = 1 / 8


def rng(seed):
    return np.random.Generator(np.random.PCG64(seed))


def flips(generator, shape):
    return generator.integers(0, 8, shape, dtype=np.uint8) == 0


def responses(hidden_inputs, task_masks, teacher_gate):
    selected = hidden_inputs[:, None] & task_masks[None, :]
    return PARITY[selected] if teacher_gate == 6 else (selected != 0).astype(np.uint8)


def fold_probabilities(bits, gate):
    # Each active anchor is used once. Its posterior is independent of all
    # previously folded anchors under the specified fresh-input prior.
    bits = np.asarray(bits, dtype=np.float64)
    g00, g01, g10, g11 = [(gate >> j) & 1 for j in range(4)]
    values = np.empty((len(bits), SIZE), dtype=np.float64)
    values[:, 0] = 0
    for mask in range(1, SIZE):
        high = mask.bit_length() - 1
        previous = mask ^ (1 << high)
        q = bits[:, high]
        if not previous:
            values[:, mask] = q
        else:
            p = values[:, previous]
            values[:, mask] = (
                g00
                + (g10 - g00) * p
                + (g01 - g00) * q
                + (g11 - g10 - g01 + g00) * p * q
            )
    return values


def encode(signatures, anchors, gate):
    word = sum(int(v) << (7 * i) for i, v in enumerate(signatures))
    word |= gate << (7 * SIZE)
    for i, task in enumerate(anchors):
        word |= int(task) << (7 * SIZE + 4 + 7 * i)
    return word.to_bytes((7 * SIZE + 4 + 7 * M + 7) // 8, "little")


def decode(payload):
    word = int.from_bytes(payload, "little")
    signatures = np.array(
        [(word >> (7 * i)) & 127 for i in range(SIZE)], dtype=np.uint8
    )
    gate = (word >> (7 * SIZE)) & 15
    anchors = np.array(
        [(word >> (7 * SIZE + 4 + 7 * i)) & 127 for i in range(M)], dtype=np.uint8
    )
    return signatures, anchors, gate


def learn_names(signature_tokens):
    signs = signature_tokens.sum(axis=2) > signature_tokens.shape[2] // 2
    signatures = (signs @ BITS).astype(np.uint8)
    anchors = []
    for target in BITS:
        matches = np.flatnonzero(signatures == target)
        if len(matches) != 1:
            return None
        anchors.append(matches[0])
    if np.count_nonzero(signatures == 0) != 1:
        return None
    return signatures, np.asarray(anchors, dtype=np.uint8)


def fit_operations(signatures, anchor_tokens, response_tokens):
    anchor_bits = anchor_tokens.mean(axis=2) > 0.5
    hits = response_tokens.sum(axis=2, dtype=np.int64)
    n = response_tokens.shape[2]
    per_condition = []
    for gate in range(16):
        predictions = fold_probabilities(anchor_bits, gate)[:, signatures] == 1
        per_condition.append(np.where(predictions, hits, n - hits).sum(axis=1))
    per_condition = np.asarray(per_condition)
    return anchor_bits, hits, per_condition


def maximizing(scores):
    return np.flatnonzero(scores == scores.max()).tolist()


def weights(log_scores):
    relative = np.exp(log_scores - np.max(log_scores, axis=-1, keepdims=True))
    return relative / relative.sum(axis=-1, keepdims=True)


def input_mixture(counts, centers, row_probabilities):
    # For each candidate hidden input, score the 21 exposed observations. Binomial
    # coefficients and the common flip factor cancel from the posterior weights.
    center = np.asarray(centers, dtype=np.float64)
    matches = counts @ center.T + (3 - counts) @ (1 - center).T
    return weights(matches * log(7)) @ row_probabilities


def test_scores(probabilities, labels, novel):
    losses = -np.log(np.where(labels, probabilities, 1 - probabilities))
    return {
        "all_nll": float(losses.mean()),
        "novel_input_nll": float(losses[novel].mean()),
    }


def closure_gates(signatures):
    # A truth table preserves the observed rows if applying it coordinatewise to
    # any two rows returns another row. Integer bit sets give an independent test.
    ncols = signatures.shape[1]
    universe = (1 << ncols) - 1
    rows = {sum(int(bit) << i for i, bit in enumerate(row)) for row in signatures}
    closed = []
    for g in range(16):

        def combine(x, y, gate=g):
            parts = (~x & ~y, ~x & y, x & ~y, x & y)
            out = 0
            for j, part in enumerate(parts):
                if gate & (1 << j):
                    out |= part
            return out & universe

        if all(combine(x, y) in rows for x in rows for y in rows):
            closed.append(g)
    return closed


def run_world(teacher, teacher_gate):
    table = responses(PILOTS, teacher, teacher_gate)
    dictionary_tokens = table[:M].T[:, :, None] ^ flips(rng(23112502), (SIZE, M, 65))
    dictionary = learn_names(dictionary_tokens)
    if dictionary is None:
        return {
            "fit_failure": "The empirical pilot signatures do not identify the required anchor names."
        }
    signatures, anchors = dictionary
    anchor_tokens = table[:, anchors, None] ^ flips(rng(23112503), (M + 1, M, 65))
    observed = table[:, :, None] ^ flips(rng(23112504), (M + 1, SIZE, 17))
    anchor_bits, hits, per_condition = fit_operations(
        signatures, anchor_tokens, observed
    )
    scores = per_condition.sum(axis=1)
    winner = maximizing(scores)[0]
    packed = encode(signatures, anchors, winner)
    signatures, anchors, winner = decode(packed)
    tasks = np.flatnonzero((signatures != 0) & ~np.isin(np.arange(SIZE), anchors))
    if len(tasks) != SIZE - M - 1:
        return {
            "fit_failure": "The deployed task dictionary has an ambiguous empty or singleton signature."
        }
    episodes = 2048
    tape = rng(23112505)
    hidden = tape.integers(0, SIZE, episodes, dtype=np.uint8)
    exposed = responses(hidden, teacher[anchors], teacher_gate)[:, :, None] ^ flips(
        tape, (episodes, M, 3)
    )
    labels = responses(hidden, teacher[tasks], teacher_gate) ^ flips(
        tape, (episodes, len(tasks))
    )
    counts = exposed.sum(axis=2, dtype=np.int64)
    posterior = 1 / (1 + np.exp(-(2 * counts - 3) * log(7)))
    novel = ~np.isin(hidden, PILOTS)
    references = {"learned": winner, "fixed_xor": 6, "fixed_or": 14}
    results = {}
    mixture = np.zeros((episodes, len(tasks)))
    gate_weights = weights(scores * log(7))
    for gate in range(16):
        prob = (
            ETA
            + (1 - 2 * ETA) * fold_probabilities(posterior, gate)[:, signatures[tasks]]
        )
        mixture += gate_weights[gate] * prob
        for name, index in references.items():
            if gate == index:
                results[name] = test_scores(prob, labels, novel)
    results["bayesian_gate_mixture"] = test_scores(mixture, labels, novel)
    prototypes = input_mixture(counts, anchor_bits, (hits[:, tasks] + 0.5) / 18)
    results["prototype_lookup"] = test_scores(prototypes, labels, novel)
    oracle_probs = input_mixture(
        counts,
        responses(WORDS, teacher[anchors], teacher_gate),
        ETA + (1 - 2 * ETA) * responses(WORDS, teacher[tasks], teacher_gate),
    )
    results["same_observations_oracle"] = test_scores(oracle_probs, labels, novel)

    # Diagnostics below access the generator's true rows only after scoring.
    true_anchors = [int(np.flatnonzero(teacher == bit)[0]) for bit in BITS]
    correct_bits = table[:, true_anchors]
    distances = [
        int(
            np.count_nonzero(
                fold_probabilities(correct_bits, gate)[:, teacher] != table
            )
        )
        for gate in range(16)
    ]
    fit_error_bound = (SIZE * M + (M + 1) * M) * exp(-2 * 65 * (0.5 - ETA) ** 2)
    affinity = 2 * sqrt(ETA * (1 - ETA))
    fit_error_bound += sum(
        affinity ** (17 * d) for g, d in enumerate(distances) if g != teacher_gate
    )
    return {
        "winner": winner,
        "pilot_only_erm": maximizing(per_condition[:, :M].sum(axis=1)),
        "full_erm": maximizing(scores),
        "training_matches": scores.tolist(),
        "unique_fitted_signatures": len(set(signatures.tolist())),
        "correct_task_signatures": int(np.count_nonzero(signatures == teacher)),
        "stored_model_bytes": len(packed),
        "stored_model_bits": 7 * SIZE + 4 + 7 * M,
        "novel_input_episodes": int(novel.sum()),
        "novel_input_targets": int(novel.sum()) * len(tasks),
        "oracle_label_distances_by_gate": distances,
        "pilot_closure": closure_gates(table[:M].T),
        "full_closure": closure_gates(table.T),
        "failure_probability_bound_on_this_design": fit_error_bound,
        "scores": results,
    }


def experiment():
    teacher = rng(23112501).permutation(SIZE).astype(np.uint8)
    return {
        "signature_targets": SIZE * M * 65,
        "operation_anchor_targets": (M + 1) * M * 65,
        "operation_fit_targets": (M + 1) * SIZE * 17,
        "test_episodes": 2048,
        "adaptation_targets_per_episode": 3 * M,
        "scored_targets": 2048 * (SIZE - M - 1),
        "xor_world": run_world(teacher, 6),
        "or_world": run_world(teacher, 14),
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", type=Path)
    args = cli.parse_args()
    result = experiment()
    if args.check:
        verify_result(result, json.loads(args.check.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
