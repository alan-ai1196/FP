"""Learn an interpreter of unseen task descriptions from ordinary labeled parity episodes."""

import argparse
import json
from dataclasses import dataclass
from itertools import combinations
from math import exp
from pathlib import Path

import numpy as np
from parity_acquisition import SIZE, M, signed_correlations, verify_result

BITS = tuple(1 << i for i in range(M))
PAIRS = tuple(a | b for a, b in combinations(BITS, 2))
PARITY = np.array([word.bit_count() % 2 for word in range(SIZE)], dtype=np.uint8)
INPUTS = np.arange(SIZE, dtype=np.uint8)
NAMES = ("linear", "interactions", "lookup")


@dataclass(frozen=True)
class Interpreter:
    columns: tuple
    terms: tuple

    def mask(self, task):
        result = 0
        for bit, column in zip(BITS, self.columns):
            if task & bit:
                result ^= column
        for pair_index, coefficient in self.terms:
            pair = PAIRS[pair_index]
            if task & pair == pair:
                result ^= coefficient
        return result

    def to_bytes(self):
        # Low bits contain the seven singleton columns and the interaction count.
        word = sum(column << (7 * i) for i, column in enumerate(self.columns))
        word |= len(self.terms) << 49
        for i, (pair_index, coefficient) in enumerate(self.terms):
            word |= (pair_index | (coefficient << 5)) << (54 + 12 * i)
        return word.to_bytes((54 + 12 * len(self.terms) + 7) // 8, "little")

    @classmethod
    def from_bytes(cls, payload):
        word = int.from_bytes(payload, "little")
        columns = tuple((word >> (7 * i)) & 127 for i in range(M))
        nterms = (word >> 49) & 31
        if nterms > len(PAIRS) or len(payload) != (54 + 12 * nterms + 7) // 8:
            raise ValueError("Invalid interpreter length")
        terms = []
        for i in range(nterms):
            entry = (word >> (54 + 12 * i)) & 4095
            pair_index = entry & 31
            if pair_index >= len(PAIRS):
                raise ValueError("Invalid interaction address")
            terms.append((pair_index, entry >> 5))
        return cls(columns, tuple(terms))


def split_ids():
    training = tuple(sorted((*BITS, *PAIRS)))
    validation = tuple(
        sorted(
            (1 << (a - 1)) | (1 << (b - 1)) | (1 << (c - 1))
            for a, b, c in combinations(range(1, 8), 3)
            if a ^ b ^ c == 0
        )
    )
    assert all(sum(t & p == p for t in validation) == 1 for p in PAIRS)
    heldout = tuple(sorted(set(range(1, SIZE)).difference(training, validation)))
    assert (len(training), len(validation), len(heldout)) == (28, 7, 92)
    return training, validation, heldout


def worlds():
    rng = np.random.Generator(np.random.PCG64(23112401))
    while True:
        columns = tuple(map(int, rng.integers(0, SIZE, size=M, dtype=np.uint8)))
        base = Interpreter(columns, ())
        linear = [base.mask(t) for t in range(SIZE)]
        if len(set(linear)) == SIZE:
            break
    i, j, k = map(
        int,
        np.random.Generator(np.random.PCG64(23112402)).choice(M, size=3, replace=False),
    )
    pair = (1 << i) | (1 << j)
    shear = [linear[t ^ ((1 << k) if t & pair == pair else 0)] for t in range(SIZE)]
    perm = np.random.Generator(np.random.PCG64(23112403)).permutation(SIZE)
    return {
        "linear": np.asarray(linear, dtype=np.uint8),
        "shear": np.asarray(shear, dtype=np.uint8),
        "opaque": perm.astype(np.uint8),
    }


def data(ids, teacher, n, seed):
    rng = np.random.Generator(np.random.PCG64(seed))
    words = rng.integers(0, SIZE, (len(ids), n), dtype=np.uint8)
    flips = rng.integers(0, 8, words.shape, dtype=np.uint8) == 0
    return words, PARITY[words & teacher[list(ids), None]] ^ flips


def meanings(ids, xs, ys):
    scores = (ys.shape[1] + signed_correlations(xs, ys)) // 2
    rows = {task: row for task, row in zip(ids, scores)}
    return rows, {task: int(np.argmax(row)) for task, row in rows.items()}


def fit(ids, xs, ys):
    rows, inferred = meanings(ids, xs, ys)
    linear = Interpreter(tuple(inferred[bit] for bit in BITS), ())
    terms = []
    for index, pair in enumerate(PAIRS):
        proposed = inferred[pair]
        original = linear.mask(pair)
        extra_matches = int(rows[pair][proposed] - rows[pair][original])
        if 7**extra_matches > 2**12:
            terms.append((index, original ^ proposed))
    richer = Interpreter(linear.columns, tuple(terms))
    return (linear, richer), inferred


def complement_probabilities(inferred):
    remaining = np.array(
        sorted(set(range(SIZE)) - set(inferred.values())), dtype=np.uint8
    )
    clean_ones = PARITY[remaining[:, None] & INPUTS].sum(axis=0)
    return 1 / 8 + (3 / 4) * clean_ones / len(remaining)


def forecast(model, ids, words):
    masks = np.array([model.mask(task) for task in ids], dtype=np.uint8)
    return 1 / 8 + (3 / 4) * PARITY[words & masks[:, None]]


def log_loss(probabilities, labels):
    return float(-np.log(np.where(labels, probabilities, 1 - probabilities)).mean())


def compare_compositions(predicted, actual):
    if len(set(predicted)) < SIZE:
        return None
    predicted_inverse = {mask: i for i, mask in enumerate(predicted)}
    actual_inverse = {int(mask): i for i, mask in enumerate(actual)}
    return sum(
        predicted_inverse[predicted[t] ^ predicted[u]]
        == actual_inverse[int(actual[t] ^ actual[u])]
        for t in range(SIZE)
        for u in range(SIZE)
    )


def compact_composition(model):
    # Compile the one-interaction case from the fitted columns and coefficient.
    # A zero direction encodes ordinary XOR. The 12-bit instruction fits in two bytes.
    linear = Interpreter(model.columns, ())
    inverse = {linear.mask(t): t for t in range(SIZE)}
    if len(inverse) != SIZE or len(model.terms) > 1:
        return None
    index, coefficient = model.terms[0] if model.terms else (0, 0)
    direction = inverse[coefficient]
    if direction & PAIRS[index]:
        return None
    return (index | (direction << 5)).to_bytes(2, "little")


def check_compact_composition(instruction, masks):
    if instruction is None:
        return None
    word = int.from_bytes(instruction, "little")
    pair, direction = PAIRS[word & 31], word >> 5
    first = pair & -pair
    second = pair ^ first
    cases = 0
    for left in range(SIZE):
        for right in range(SIZE):
            cross = (bool(left & first) and bool(right & second)) ^ (
                bool(left & second) and bool(right & first)
            )
            output = left ^ right ^ (direction if cross else 0)
            assert masks[output] == masks[left] ^ masks[right]
            cases += 1
    return {
        "packed_bytes": len(instruction),
        "update_direction": direction,
        "controls_mask": pair if direction else 0,
        "verified_pairs": cases,
    }


def trial(teacher):
    train, valid, test = split_ids()
    train_x, train_y = data(train, teacher, 256, 23112405)
    valid_x, valid_y = data(valid, teacher, 128, 23112406)
    fitted, learned_training = fit(train, train_x, train_y)
    # Deploy the packed representation and validate on entirely new task IDs.
    models = [Interpreter.from_bytes(model.to_bytes()) for model in fitted]
    initial_posterior = complement_probabilities(learned_training)
    valid_probs = [forecast(model, valid, valid_x) for model in models] + [
        initial_posterior[valid_x]
    ]
    valid_losses = [log_loss(p, valid_y) for p in valid_probs]
    winner = min(range(len(NAMES)), key=valid_losses.__getitem__)
    _, learned_valid = meanings(valid, valid_x, valid_y)
    known = learned_training | learned_valid
    posterior = complement_probabilities(known)
    test_x, test_y = data(test, teacher, 128, 23112407)
    full_words = np.broadcast_to(INPUTS, (len(test), SIZE))
    full_oracle = 1 / 8 + (3 / 4) * PARITY[teacher[list(test), None] & full_words]
    records = {}
    for i, name in enumerate(NAMES):
        if i < len(models):
            model = models[i]
            predicted = [model.mask(t) for t in range(SIZE)]
            output = forecast(model, test, test_x)
            all_inputs = forecast(model, test, full_words)
            packed = model.to_bytes()
            info = {
                "columns": model.columns,
                "terms": [(PAIRS[index], value) for index, value in model.terms],
                "model_bits": 54 + 12 * len(model.terms),
                "model_bytes": len(packed),
                "law_pairs_correct": compare_compositions(predicted, teacher),
                "posthoc_compact_law": check_compact_composition(
                    compact_composition(model), predicted
                ),
            }
        else:
            output = posterior[test_x]
            all_inputs = np.broadcast_to(posterior, full_words.shape)
            # The retained bit set suffices for an unknown key. This run caches all
            # 128 probabilities as float64 for scoring and charges this separately.
            info = {
                "residual_mask_bits": SIZE,
                "cached_probability_bytes": posterior.nbytes,
            }
        per_id = (-np.log(np.where(test_y, output, 1 - output)).mean(axis=1)).tolist()
        info.update(
            validation_nll=valid_losses[i],
            test_nll=log_loss(output, test_y),
            test_nll_by_id=per_id,
            exact_unseen_rules=int(np.all(all_inputs == full_oracle, axis=1).sum()),
        )
        records[name] = info
    target_probs = 1 / 8 + (3 / 4) * PARITY[teacher[list(test), None] & test_x]
    # These measurements use the generator only after fitting and validation.
    return {
        "selected": NAMES[winner],
        "oracle_test_nll": log_loss(target_probs, test_y),
        "correctly_identified_training_ids": sum(
            learned_training[t] == int(teacher[t]) for t in train
        ),
        "correctly_identified_validation_ids": sum(
            learned_valid[t] == int(teacher[t]) for t in valid
        ),
        "models": records,
    }


def experiment():
    train, valid, test = split_ids()
    n = 256
    failure = len(train) * exp(-2 * n * (7 / 8 - 0.72) ** 2) + len(train) * (
        SIZE - 1
    ) * exp(-2 * n * (0.69 - 0.5) ** 2)
    return {
        "training_ids": train,
        "validation_ids": valid,
        "test_ids": test,
        "flip_rate": "1/8",
        "training_targets": len(train) * n,
        "validation_targets": len(valid) * 128,
        "test_targets": len(test) * 128,
        "fit_histogram_bytes": len(train) * SIZE * 8,
        "fit_walsh_operations": len(train) * SIZE * M,
        "validation_meaning_walsh_operations": len(valid) * SIZE * M,
        "interaction_candidates": len(PAIRS),
        "good_training_event_failure_upper_bound": failure,
        "worlds": {name: trial(teacher) for name, teacher in worlds().items()},
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", type=Path)
    args = cli.parse_args()
    result = json.loads(json.dumps(experiment()))
    if args.check:
        verify_result(result, json.loads(args.check.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
