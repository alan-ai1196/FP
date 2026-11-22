"""Registered empirical likelihood experiment for an opaque seven-bit parity workload."""

import argparse
import json
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from math import exp, isclose, log
from pathlib import Path

import numpy as np

from parity_packing import BALL, ERRORS, M, SIZE, extend


@dataclass(frozen=True)
class Likelihood:
    correct: int
    targets: int

    def better_than(self, other):
        # Gain over a fair coin is correct*log(7) - targets*log(4).
        # Compare exactly, including layouts whose fitted predictions coincide.
        c, t = self.correct - other.correct, self.targets - other.targets
        if t == 0:
            return c > 0
        if c <= 0 <= t:
            return False
        if t < 0 <= c:
            return True
        left = 7 ** abs(c)
        right = 4 ** abs(t)
        return left > right if c > 0 else left < right


@cache
def profitable(matches, total):
    return 7**matches > 4**total


def episodes(seed, n, teacher):
    rng = np.random.Generator(np.random.PCG64(seed))
    x = rng.integers(0, SIZE, (SIZE, n), dtype=np.uint8)
    noise = rng.integers(0, 8, x.shape, dtype=np.uint8) == 0
    parity = np.array([i.bit_count() % 2 for i in range(SIZE)], dtype=np.uint8)
    return x, parity[x & teacher[:, None]] ^ noise


def fit_options(x, y):
    # The row index is an opaque task ID. No operation on its constituent bits
    # enters fitting. H[task,word] is an observed signed label count.
    count = np.zeros((SIZE, SIZE), dtype=np.int64)
    np.add.at(count, (np.arange(SIZE)[:, None], x), 1 - 2 * y.astype(np.int64))
    half = 1
    while half < SIZE:
        blocks = count.reshape(SIZE, -1, 2 * half)
        left = blocks[:, :, :half].copy()
        right = blocks[:, :, half:]
        blocks[:, :, :half] = left + right
        right[:] = left - right
        half *= 2
    n = x.shape[1]
    candidates = []
    for row in count:
        options = []
        for v, correlation in enumerate(row):
            good = (n + abs(int(correlation))) // 2
            if profitable(good, n):
                options.append((good, v, int(correlation < 0)))
        candidates.append(
            sorted(options, key=lambda option: (-option[0], option[1], option[2]))
        )
    return candidates


def span(generators):
    space = (0,)
    for w in generators:
        space = extend(space, w)
    return space


def subspaces(b):
    # Unique reduced-row-echelon basis for each subspace.
    for pivots in combinations(range(M), b):
        slots = [
            (i, j)
            for i, p in enumerate(pivots)
            for j in range(p + 1, M)
            if j not in pivots
        ]
        for assignments in product((0, 1), repeat=len(slots)):
            basis = [1 << p for p in pivots]
            for (i, j), bit in zip(slots, assignments):
                basis[i] |= bit << j
            yield span(basis)


def extensions(space):
    seen = set(space)
    for v in range(1, SIZE):
        if v not in seen:
            candidate = extend(space, v)
            seen.update(candidate)
            yield candidate


def fitted(space, options, n, unrestricted=False):
    visible = (1 << SIZE) - 1 if unrestricted else 0
    if not unrestricted:
        for w in space:
            visible |= BALL[w]
    correct = targets = tests = 0
    rules = []
    for row in options:
        rule = None
        for hits, v, flip in row:
            tests += 1
            if visible & (1 << v):
                rule = (v, flip)
                correct += hits
                targets += n
                break
        rules.append(rule)
    return Likelihood(correct, targets), rules, tests


def choose(layouts, options, n):
    optimum = None
    examined = checks = ties = 0
    for space in layouts:
        value, rules, tests = fitted(space, options, n)
        examined += 1
        checks += tests
        if optimum is None or value.better_than(optimum[0]):
            optimum = (value, space, rules)
            ties = 1
        elif value == optimum[0]:
            ties += 1
            if space < optimum[1]:
                optimum = (value, space, rules)
    return optimum, examined, checks, ties


def canonical_basis(space):
    basis = []
    generated = (0,)
    for v in space:
        if v not in generated:
            basis.append(v)
            generated = extend(generated, v)
    return basis


def compile_routes(basis):
    routes = {}
    for selection in range(1 << len(basis)):
        v = 0
        for i, w in enumerate(basis):
            if selection & (1 << i):
                v ^= w
        for error in ERRORS:
            # Prefer no raw access, then the lower address.
            choice = (error.bit_length(), selection)
            key = v ^ error
            routes[key] = min(routes.get(key, choice), choice)
    return routes


def package(basis, rules, unrestricted):
    choices = compile_routes(basis)
    table = 0
    for i, rule in enumerate(rules):
        entry = 1 << 8
        if rule is not None:
            v, flip = rule
            if unrestricted:
                entry = v | (flip << 7)
            else:
                address, selection = choices[v]
                entry = selection | (address << 4) | (flip << 7)
        table |= entry << (9 * i)
    header = sum(w << (7 * i) for i, w in enumerate(basis))
    header_bytes = (7 * len(basis) + 7) // 8
    return header.to_bytes(header_bytes, "little") + table.to_bytes(
        9 * SIZE // 8, "little"
    )


def evaluate(name, fit, x, y, teacher, layouts, tests, unrestricted=False):
    value, space, rules = fit
    basis = canonical_basis(space)
    installed = package(basis, rules, unrestricted)
    header_bytes = (7 * len(basis) + 7) // 8
    header = int.from_bytes(installed[:header_bytes], "little")
    basis = [(header >> (7 * i)) & 127 for i in range(len(basis))]
    # Encode every episode, including eventual fair responses, through a function
    # of the raw prefix alone. Task and label are inaccessible at this point.
    synopsis = np.zeros(x.shape, dtype=np.uint8)
    if basis:
        synopsis.flat[:] = [
            sum(((int(word) & w).bit_count() & 1) << i for i, w in enumerate(basis))
            for word in x.flat
        ]
    good = scored = raw_reads = synopsis_reads = correct_keys = query_xors = 0
    for task, (words, labels) in enumerate(zip(x, y)):
        byte, shift = divmod(9 * task, 8)
        byte += header_bytes
        entry = (int.from_bytes(installed[byte : byte + 2], "little") >> shift) & 511
        if entry & 256:
            continue
        flip = (entry >> 7) & 1
        # Teacher access here is solely for a post-fit clean-key diagnostic.
        correct_keys += int(rules[task] == (teacher[task], 0))
        if unrestricted:
            v = entry & 127
            # Direct baseline reads all coordinates selected by its learned mask.
            for word, target in zip(words, labels):
                pred = ((int(word) & v).bit_count() & 1) ^ flip
                good += pred == int(target)
            raw_reads += len(labels) * v.bit_count()
            query_xors += len(labels) * max(0, v.bit_count() - 1)
        else:
            address, selection = (entry >> 4) & 7, entry & 15
            for word, stored, target in zip(words, synopsis[task], labels):
                # Query-time operations use only the synopsis and one addressed bit.
                answer = (int(stored) & selection).bit_count() & 1
                if address:
                    answer ^= (int(word) >> (address - 1)) & 1
                good += (answer ^ flip) == int(target)
            raw_reads += len(labels) * int(bool(address))
            synopsis_reads += len(labels) * selection.bit_count()
            query_xors += len(labels) * max(
                0, selection.bit_count() + int(bool(address)) - 1
            )
        scored += len(labels)
    total = int(y.size)
    fair = total - scored
    nll = (good * log(8 / 7) + (scored - good) * log(8) + fair * log(2)) / total
    return dict(
        learner=name,
        layouts_scored=layouts,
        training_readout_membership_checks=tests,
        stored_basis=basis,
        derived_state_bits=len(basis),
        logical_precompute_xors=sum(w.bit_count() - 1 for w in basis),
        logical_precompute_input_taps=sum(w.bit_count() for w in basis),
        encoded_route_table_bits=SIZE * 9,
        encoded_basis_bits=7 * len(basis),
        packed_model_bytes=len(installed),
        raw_episode_storage_bits=M,
        derived_episode_storage_bits=len(basis),
        correctly_identified_keys=correct_keys,
        heldout_targets=total,
        heldout_fair_targets=fair,
        heldout_correct_confident=good,
        heldout_incorrect_confident=scored - good,
        heldout_nll=nll,
        heldout_raw_query_bit_reads=raw_reads,
        heldout_synopsis_bit_reads=synopsis_reads,
        heldout_query_xor_reductions=query_xors,
        train_confident_targets=value.targets,
        train_correct_confident=value.correct,
    )


def unseen_pairs(xtrain, ytrain, testx, testy, rules):
    # Supplemental diagnostic after the main fit. The lookup table knows the
    # flip rate and updates each (key,input) using a fair prior on its clean label.
    present = np.zeros((SIZE, SIZE), dtype=np.int64)
    signed = np.zeros_like(present)
    keys = np.arange(SIZE)[:, None]
    np.add.at(present, (keys, xtrain), 1)
    np.add.at(signed, (keys, xtrain), 2 * ytrain.astype(np.int64) - 1)
    unseen = present[keys, testx] == 0
    posterior = 1 / (1 + np.exp(-log(7) * signed[keys, testx]))
    predicted = 1 / 8 + (3 / 4) * posterior
    losses = -np.log(np.where(testy, predicted, 1 - predicted))
    total_loss = 0.0
    for task, rule in enumerate(rules):
        take = unseen[task]
        if rule is None:
            total_loss += int(take.sum()) * log(2)
        else:
            v, flip = rule
            expected = [
                ((int(x) & v).bit_count() % 2) ^ flip for x in testx[task, take]
            ]
            hits = int(np.count_nonzero(np.asarray(expected) == testy[task, take]))
            total_loss += hits * log(8 / 7) + (int(take.sum()) - hits) * log(8)
    unseen_ids, unseen_positions = np.nonzero(unseen)
    distinct_unseen = set(zip(unseen_ids, testx[unseen_ids, unseen_positions]))
    return dict(
        unique_training_pairs=int(np.count_nonzero(present)),
        unseen_heldout_draws=int(unseen.sum()),
        distinct_unseen_heldout_pairs=len(distinct_unseen),
        table_nll=float(losses.mean()),
        table_nll_unseen=log(2),
        exhaustive_nll_unseen=total_loss / int(unseen.sum()) if unseen.any() else None,
    )


def experiment():
    teacher = (
        np.random.Generator(np.random.PCG64(23112601))
        .permutation(SIZE)
        .astype(np.uint8)
    )
    xtrain, ytrain = episodes(23112602, 256, teacher)
    options = fit_options(xtrain, ytrain)
    space = (0,)
    greedy_counts = greedy_checks = 0
    for _ in range(4):
        greedy, count, checks, _ = choose(extensions(space), options, 256)
        space = greedy[1]
        greedy_counts += count
        greedy_checks += checks
    exhaustive, count, checks, optimal_layouts = choose(subspaces(4), options, 256)
    assert count == 11811
    raw, raw_count, raw_checks, _ = choose(
        (span([1 << i for i in coords]) for coords in combinations(range(M), 4)),
        options,
        256,
    )
    assert raw_count == 35
    direct_value, direct_rules, direct_tests = fitted(
        (0,), options, 256, unrestricted=True
    )
    testx, testy = episodes(23112603, 128, teacher)
    outcomes = []
    for name, fit, layouts, tests, direct in [
        ("greedy", greedy, greedy_counts, greedy_checks, False),
        ("exhaustive", exhaustive, count, checks, False),
        ("raw_coordinate_cache", raw, raw_count, raw_checks, False),
        (
            "unrestricted_raw_parity",
            (direct_value, (0,), direct_rules),
            1,
            direct_tests,
            True,
        ),
    ]:
        outcomes.append(
            evaluate(name, fit, testx, testy, teacher, layouts, tests, direct)
        )
    threshold = log(4) / log(7)
    bad = SIZE * exp(-2 * 256 * (7 / 8 - threshold) ** 2) + 2 * SIZE * (SIZE - 1) * exp(
        -2 * 256 * (threshold - 1 / 2) ** 2
    )
    return dict(
        seeds=[23112601, 23112602, 23112603],
        train_targets=int(ytrain.size),
        heldout_targets=int(testy.size),
        per_key_training_inputs=256,
        per_key_heldout_inputs=128,
        flip_rate="1/8",
        candidate_parities=SIZE,
        histogram_bytes=SIZE * SIZE * 8,
        walsh_additions_or_subtractions=SIZE * SIZE * M,
        profitable_key_mask_pairs=sum(map(len, options)),
        empirical_optimal_layouts=optimal_layouts,
        upper_probability_of_bad_correlation_event=bad,
        results=outcomes,
        posthoc_pair_retrieval=unseen_pairs(
            xtrain, ytrain, testx, testy, exhaustive[2]
        ),
    )


def verify_result(actual, expected):
    if isinstance(actual, dict):
        assert actual.keys() == expected.keys()
        for key in actual:
            verify_result(actual[key], expected[key])
    elif isinstance(actual, list):
        assert len(actual) == len(expected)
        for entry, reference in zip(actual, expected):
            verify_result(entry, reference)
    elif isinstance(actual, float):
        assert isclose(actual, expected, rel_tol=2e-14, abs_tol=1e-15)
    else:
        assert actual == expected


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(
        "--check",
        type=Path,
        help="Compare the complete recomputed result with a stored receipt",
    )
    args = cli.parse_args()
    result = experiment()
    if args.check:
        verify_result(result, json.loads(args.check.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
