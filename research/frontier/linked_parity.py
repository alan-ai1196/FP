"""Learn and price a shared update from raw binary sequences with fresh task orientations."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import atanh, comb, log, log1p, prod
from pathlib import Path

import numpy as np
from scipy.special import betaln
from transfer_dictionary import walsh

REGISTRATION = "9e7d752"
M = 8
SIZES = (128, 1024, 8192)
LENGTHS = (1, 2, 4, 16)
REPEATS = 32
PRICE = 0.002


def character(mask, word):
    return 1 - 2 * ((mask & word).bit_count() % 2)


def second_mask(mask):
    return 1 ^ mask ^ (mask << 1)


def residuals(raw, mask, memory):
    word = 0
    for x in raw[:memory]:
        word = 2 * word + int(x < 0)
    out = []
    for x in raw[memory:]:
        out.append(x * character(mask, word))
        word = ((word << 1) + int(x < 0)) % (1 << memory)
    return out


def exact_check():
    a = F(1, 2)
    histories_checked = pairs_checked = partitions_checked = 0
    for memory in range(2, 5):
        masks = range(1 << (memory - 1), 1 << memory)
        assert len({second_mask(s) for s in masks}) == len(masks)
        for length in range(1, 5):
            words = list(product((-1, 1), repeat=memory + length))
            residual = {s: [residuals(w, s, memory) for w in words] for s in masks}
            for s in masks:
                density = [
                    (prod(1 + a * z for z in row) + prod(1 - a * z for z in row)) / 2
                    for row in residual[s]
                ]
                assert sum(density) == len(words)
                second_moment = ((1 + a * a) ** length + (1 - a * a) ** length) / 2
                assert sum(p * p for p in density) == len(words) * second_moment
                if length == 1:
                    assert set(density) == {1}
                if length == 2:
                    decoded = set()
                    for raw, p in zip(words, density, strict=True):
                        diffs = tuple(
                            raw[i] * raw[i + 1] for i in range(memory, -1, -1)
                        )
                        z = diffs[0] * diffs[-1]
                        bits = sum((x < 0) << i for i, x in enumerate(diffs[1:-1]))
                        assert p == 1 + a * a * z * character(s, bits)
                        decoded.add((bits, z, diffs[-1], raw[0]))
                        restored = [raw[0]]
                        for dx in (diffs[-1], *reversed(diffs[1:-1]), z * diffs[-1]):
                            restored.append(dx * restored[-1])
                        assert tuple(restored) == raw
                        past = sum(
                            (x < 0) << i for i, x in enumerate(reversed(raw[:-1]))
                        )
                        assert p == 1 + a * a * raw[-1] * character(
                            second_mask(s), past
                        )
                    assert len(decoded) == len(words)
                for alt in masks:
                    pair_score = sum(
                        mass * (sum(row) ** 2 - length) / 2
                        for mass, row in zip(density, residual[alt], strict=True)
                    ) / len(words)
                    if alt == s:
                        assert pair_score == comb(length, 2) * a**2
                    else:
                        assert 0 <= pair_score <= comb(length, 2) * a**4
                    pairs_checked += 1
                histories_checked += len(words)
        for b in range(memory):
            for code in range(1 << b):
                cell = [s for s in masks if s % (1 << b) == code]
                forecasts = [
                    sum(F(character(second_mask(s), x), len(cell)) for s in cell)
                    for x in range(1 << (memory + 1))
                ]
                assert set(forecasts) <= {-1, 0, 1}
                assert sum(z * z for z in forecasts) == F(len(forecasts), len(cell))
                partitions_checked += 1
    return {
        "exact_source_word_densities": histories_checked,
        "exact_pair_statistic_expectations": pairs_checked,
        "exact_affine_packet_cells": partitions_checked,
    }


class Rules:
    def __init__(self, memory):
        self.memory = memory
        self.width = 1 << (memory + 1)
        self.count = 1 << (memory - 1)
        masks = np.arange(self.count, 2 * self.count)
        histories = np.arange(self.width)
        values = np.array([character(x, x) for x in histories], dtype=np.int8)
        self.character = values[histories[:, None] & histories[None, :]]
        self.actions = self.character[: 1 << memory, masks]
        self.second = self.character[second_mask(masks)]
        self.packet = np.empty((self.count, memory, self.width), dtype=np.int8)
        active = np.ones(self.width, dtype=bool)
        for b in reversed(range(memory)):
            self.packet[:, b] = self.second * active
            if b:
                direction = 3 << (b - 1)
                active &= self.character[direction] == 1

    def give_tapes(self, rng, chosen, a, length):
        """Only this generator sees the shared mask and individual task signs."""
        number = SIZES[-1] // length
        raw = np.empty((number, self.memory + length), dtype=np.int8)
        raw[:, : self.memory] = 1 - 2 * rng.integers(
            2, size=(number, self.memory), dtype=np.int8
        )
        phase = 1 - 2 * rng.integers(2, size=number, dtype=np.int8)
        words = (raw[:, : self.memory] < 0) @ (1 << np.arange(self.memory - 1, -1, -1))
        for t in range(length):
            # All tested strengths admit this exact eight-point Bernoulli sampler.
            flips = rng.integers(8, size=number) >= int(4 * (1 + a))
            out = self.actions[words, chosen] * phase * (1 - 2 * flips.astype(np.int8))
            raw[:, self.memory + t] = out
            words = ((2 * words) + (out < 0)) % (1 << self.memory)
        return raw

    def records(self, raw):
        words = (raw[:, : self.memory] < 0) @ (1 << np.arange(self.memory - 1, -1, -1))
        outcomes = raw[:, self.memory :]
        context = np.empty(outcomes.shape, dtype=np.int16)
        pair = np.empty((len(raw), outcomes.shape[1] - 1), dtype=np.int16)
        for t in range(outcomes.shape[1]):
            context[:, t] = words
            extended = 2 * words + (outcomes[:, t] < 0)
            if t < outcomes.shape[1] - 1:
                pair[:, t] = extended
            words = extended % (1 << self.memory)
        return context, outcomes, pair

    def likelihoods(self, context, outcomes, a):
        length = outcomes.shape[1]
        if length == 1:
            return None
        integer = np.zeros((len(context), self.count), dtype=np.int8)
        for t in range(length):
            integer += self.actions[context[:, t]] * outcomes[:, t, None]
        z = np.arange(-length, length + 1) * atanh(a)
        relative_log_mass = 0.5 * length * log1p(-a * a) + np.logaddexp(z, -z) - log(2)
        return relative_log_mass[integer.astype(np.int16) + length]

    def pair_counts(self, pair, outcomes):
        idx = pair.ravel()
        signs = outcomes[:, 1:].ravel()
        counts = np.bincount(idx, minlength=self.width)
        positive = np.bincount(idx[signs > 0], minlength=self.width)
        return counts, 2 * positive - counts

    def unrestricted(self, counts, signed):
        correlations = walsh(signed)
        mask = int(np.abs(correlations).argmax())
        n = int(counts.sum())
        plus = (n + int(correlations[mask])) // 2
        score = betaln(plus + 0.5, n - plus + 0.5) - betaln(0.5, 0.5) + n * log(2)
        selected = score > log(self.width)
        prediction = (
            self.character[mask] * (float(correlations[mask]) / (n + 1))
            if selected
            else np.zeros(self.width)
        )
        return prediction, signed / (counts + 1), mask if selected else -1

    def trained(self, scores, fraction):
        total = np.zeros(self.count) if scores is None else scores[fraction].sum(axis=0)
        chosen = int(total.argmax())
        return chosen, bool(total[chosen] > log(self.count))

    def installation(self, guess, counts, signed, strength):
        n = counts.sum()
        if not n:
            return -1, -1
        packets = self.packet[guess]
        gain = (
            atanh(strength) * (packets @ signed)
            + 0.5 * log1p(-(strength**2)) * (np.abs(packets) @ counts)
        ) / n
        priced = np.append(0.0, gain - PRICE * np.arange(self.memory))
        greedy = int(priced[1] > priced[0])
        for index in range(2, len(priced)):
            if priced[index] <= priced[greedy]:
                break
            greedy = index
        return int(priced.argmax()) - 1, greedy - 1


def gain(truth, forecast):
    return float(np.mean(0.5 * np.log1p(-(forecast**2)) + truth * np.arctanh(forecast)))


def one_run(rules, rng, a, signal, length):
    actual = int(rng.integers(rules.count))
    raw = rules.give_tapes(rng, actual, a if signal else 0, length)
    context, outcomes, pair = rules.records(raw)
    scores = rules.likelihoods(context, outcomes, a)
    strength = a * a
    truth = rules.second[actual] * (strength if signal else 0.0)
    result = []
    for n in SIZES:
        tasks = n // length
        first = slice(0, tasks)
        counts, signed = rules.pair_counts(pair[first], outcomes[first])
        guess, installed = rules.trained(scores, first)
        raw_walsh, direct, raw_mask = rules.unrestricted(counts, signed)
        projections = [gain(truth, strength * item) for item in rules.packet[guess]]
        train = np.flatnonzero(np.arange(tasks) % 4 != 3)
        validation = slice(3, tasks, 4)
        split_guess, _ = rules.trained(scores, train)
        val_counts, val_signed = rules.pair_counts(
            pair[validation], outcomes[validation]
        )
        joint, greedy = rules.installation(
            split_guess, val_counts, val_signed, strength
        )
        row = {
            "mask_installed": int(installed),
            "correct_installed_mask": int(signal and installed and guess == actual),
            "mask_gain": projections[-1] if installed else 0.0,
            "walsh_installed": int(raw_mask >= 0),
            "correct_walsh_direction": int(
                signal
                and raw_mask == second_mask(actual + rules.count)
                and raw_walsh[0] > 0
            ),
            "walsh_gain": gain(truth, raw_walsh),
            "conditional_table_gain": gain(truth, direct),
            "packet_gains_if_installed": [projections[b] for b in (0, 2, 4, 7)],
        }
        for name, bits in (("joint", joint), ("greedy", greedy)):
            value = (
                0.0
                if bits < 0
                else gain(truth, strength * rules.packet[split_guess, bits])
            )
            row[name + "_bits"] = bits
            row[name + "_gain"] = value
            row[name + "_priced_gain"] = value - PRICE * max(bits, 0)
        result.append(row)
    return result


def check_vector_evaluator():
    memory = 3
    rules = Rules(memory)
    a = F(1, 2)
    comparisons = 0
    for length in (2, 3, 4):
        raw = np.array(list(product((-1, 1), repeat=memory + length)), dtype=np.int8)
        context, outcomes, pairs = rules.records(raw)
        scores = rules.likelihoods(context, outcomes, float(a))
        for s in range(rules.count, 2 * rules.count):
            masses = []
            for word in raw.tolist():
                z = residuals(word, s, memory)
                masses.append(
                    (prod(1 + a * r for r in z) + prod(1 - a * r for r in z)) / 2
                )
            assert (
                np.max(
                    np.abs(
                        np.exp(scores[:, s - rules.count])
                        - np.array(masses, dtype=float)
                    )
                )
                < 2e-14
            )
            comparisons += len(raw)
        subset = np.arange(0, len(raw), 5)
        counts, signed = rules.pair_counts(pairs[subset], outcomes[subset])
        raw_x = pairs[subset].ravel()
        y = outcomes[subset, 1:].ravel()
        assert np.array_equal(
            walsh(signed), rules.character[:, raw_x] @ y.astype(np.int64)
        )
        for guess in range(rules.count):
            full = [0.0]
            for b, packet in enumerate(rules.packet[guess]):
                raw_mean = float(a * a) * packet[raw_x]
                full.append(float(np.log1p(raw_mean * y).mean()) - PRICE * b)
            assert (
                rules.installation(guess, counts, signed, float(a * a))[0]
                == int(np.argmax(full)) - 1
            )
    return comparisons


def summarize(runs, n, length):
    result = {
        "responses": n,
        "raw_tokens": n + M * (n // length),
        "adjacent_pairs": (n // length) * (length - 1),
    }
    for key in runs[0]:
        values = [row[key] for row in runs]
        if key.endswith("_bits"):
            result[key + "_histogram_fair_then_zero_through_seven"] = np.bincount(
                np.array(values) + 1, minlength=M + 1
            ).tolist()
        elif key == "packet_gains_if_installed":
            result[key] = np.mean(values, axis=0).tolist()
        elif key.endswith("gain"):
            result[key] = float(np.mean(values))
        else:
            result[key] = int(sum(values))
    return result


def audit():
    exact = exact_check()
    exact["vector_likelihoods_against_independent_rational_evaluation"] = (
        check_vector_evaluator()
    )
    rules = Rules(M)
    records = []
    for a in (0.5, 0.75):
        for signal in (True, False):
            for length in LENGTHS:
                seed = 2026112600 + int(1000 * a) + 100 * int(signal) + length
                rng = np.random.default_rng(seed)
                runs = [one_run(rules, rng, a, signal, length) for _ in range(REPEATS)]
                records.append(
                    {
                        "fitted_strength": a,
                        "source_has_signal": signal,
                        "responses_per_task": length,
                        "prefixes": [
                            summarize([r[i] for r in runs], n, length)
                            for i, n in enumerate(SIZES)
                        ],
                    }
                )
    return {
        "registration": REGISTRATION,
        "memory": M,
        "repetitions": REPEATS,
        "nats_per_installed_bit": PRICE,
        "exact_audit": exact,
        "results": records,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    blob = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(blob.encode())
    else:
        print(blob, end="")
