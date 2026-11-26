"""Causal literal-block prediction after a cut in a Bayesian automaton mixture."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import comb, factorial, log, prod
from pathlib import Path

import numpy as np
from state_birth import partition_weight, partitions


class BlockPredictor:
    """A dense count trie updated only when a complete raw block arrives."""

    def __init__(self, alphabet, length, limit=None):
        self.alphabet = alphabet
        self.length = length
        self.limit = limit
        self.sizes = [alphabet**i for i in range(length + 1)]
        self.counts = [0] * sum(self.sizes)
        self.depth = self.node = 0
        self.updates = self.clears = 0
        self.peak = 0

    def forecast(self):
        remain = self.length - self.depth - 1
        parent = self.counts[self.node] + self.sizes[remain + 1]
        first = self.alphabet * self.node + 1
        return tuple(
            F(self.counts[first + a] + self.sizes[remain], parent)
            for a in range(self.alphabet)
        )

    def observe(self, a):
        self.node = self.alphabet * self.node + 1 + a
        self.depth += 1
        if self.depth < self.length:
            return
        while self.node:
            self.counts[self.node] += 1
            self.node = (self.node - 1) // self.alphabet
        self.counts[0] += 1
        self.depth = 0
        self.updates += self.length + 1
        self.peak = max(self.peak, self.counts[0])
        if self.counts[0] == self.limit:
            self.counts = [0] * len(self.counts)
            self.clears += 1


def block_probability(x, d, b, limit=None):
    """Independent integrated histogram formula with a final partial observation."""
    if limit and len(x) > limit * b:
        return prod(
            block_probability(x[i : i + limit * b], d, b)
            for i in range(0, len(x), limit * b)
        )
    n, r = divmod(len(x), b)
    types = d**b
    counts = {}
    for j in range(n):
        word = tuple(x[j * b : (j + 1) * b])
        counts[word] = counts.get(word, 0) + 1
    mass = F(
        factorial(types - 1) * prod(map(factorial, counts.values())),
        factorial(n + types - 1),
    )
    if r:
        prefix = tuple(x[n * b :])
        count = sum(v for w, v in counts.items() if w[:r] == prefix)
        mass *= F(count + d ** (b - r), n + types)
    return mass


def structure_factor(n, d, b, c, states, limit=None):
    """Two valid partial-block bounds, with an independent charge for each reset."""
    types = d**b

    def charge(m):
        return c**m * comb(m + types - 1, types - 1)

    blocks, tail = divmod(n, b)
    past = 1
    if limit:
        epochs, blocks = divmod(blocks, limit)
        past = charge(limit) ** epochs
    if not tail:
        return past * charge(blocks)
    types_cost = comb(blocks + types - 1, types - 1)
    partial_cost = F(blocks + types, blocks + d ** (b - tail))
    return past * min(charge(blocks + 1), states**blocks * types_cost * partial_cost)


def model_mass(x, rows, table, state):
    mass = F(1)
    for a in x:
        mass *= rows[state][a]
        state = table[state][a]
    return mass


def cut_weight(beta):
    x = (0, 1, 0)
    masses = {
        path: w[1]
        for path in partitions(len(x))
        if (w := partition_weight(x, path, beta)) is not None
    }
    return 1 - masses[(0, 0, 0)] / sum(masses.values())


def rounded_weight(z, levels):
    index = min(levels, 1 + (levels * z.numerator) // z.denominator)
    return F(index, levels + 1)


def guarded_finite(x, b, limit, eta, bits):
    """Both experts reset at each count epoch. Evidence products only score the test."""
    predictor = BlockPredictor(2, b, limit)
    kept_counts = [2, 1]
    levels = 2**bits
    gate = rounded_weight(eta, levels)
    kept = fallback = quantized = F(1)
    for a in x:
        kept_score = F(kept_counts[a] + 1, sum(kept_counts) + 2)
        fallback_score = predictor.forecast()[a]
        forecast = (1 - gate) * kept_score + gate * fallback_score
        gate = rounded_weight(gate * fallback_score / forecast, levels)
        quantized *= forecast
        kept *= kept_score
        fallback *= fallback_score
        kept_counts[a] += 1
        previous_clears = predictor.clears
        predictor.observe(a)
        if predictor.clears != previous_clears:
            kept_counts = [2, 1]
    ideal = (1 - eta) * kept + eta * fallback
    bound = F(levels + 1, levels) ** len(x)
    assert ideal <= quantized * bound
    return {
        "gate_bits": bits,
        "finite_mixture_nats": -log(quantized),
        "same_experts_exact_gate_nats": -log(ideal),
        "excess_nats": log(ideal / quantized),
        "allowance_nats": log(bound),
    }


def check():
    # A positive, nonsynchronizing two-state model with asymmetric outputs.
    rows = ((F(1, 3), F(2, 3)), (F(3, 5), F(2, 5)))
    table = ((0, 1), (1, 0))
    comparisons = strings = 0
    for b in (1, 2, 3):
        c = sum(
            max(model_mass(w, rows, table, s) for s in (0, 1))
            for w in product((0, 1), repeat=b)
        )
        for limit in (None, 2):
            for n in range(1, 8):
                total = F(0)
                factor = structure_factor(n, 2, b, c, 2, limit)
                assert structure_factor(n, 2, b, 1, 1, limit) == 1 / block_probability(
                    (0,) * n, 2, b, limit
                )
                for x in product((0, 1), repeat=n):
                    predictor = BlockPredictor(2, b, limit)
                    mass = F(1)
                    for a in x:
                        law = predictor.forecast()
                        assert sum(law) == 1
                        mass *= law[a]
                        predictor.observe(a)
                    assert mass == block_probability(x, 2, b, limit)
                    free_starts = prod(
                        max(model_mass(x[j : j + b], rows, table, s) for s in (0, 1))
                        for j in range(0, n, b)
                    )
                    assert free_starts <= mass * factor
                    total += mass
                    strings += 1
                    for s in (0, 1):
                        assert model_mass(x, rows, table, s) <= mass * factor
                        comparisons += 1
                assert total == 1
    histograms = 0
    for d, b, n in ((2, 1, 4), (2, 2, 3), (3, 1, 4), (3, 2, 2)):
        block_types = d**b
        signatures = set()
        words = list(product(range(d), repeat=b))
        for x in product(range(d), repeat=n * b):
            if any(
                x[i : i + b] > x[i + b : i + 2 * b] for i in range(0, len(x) - b, b)
            ):
                continue
            base = block_probability(x, d, b)
            signatures.add(tuple(block_probability(x + w, d, b) / base for w in words))
        expected = comb(n + block_types - 1, block_types - 1)
        assert len(signatures) == expected
        assert 1 / block_probability((0,) * (n * b), d, b) == expected
        histograms += expected
    gate_checks = 0
    for bits in (0, 1, 3):
        h = 2**bits
        for i in range(8 * h + 1):
            z = F(i, 8 * h)
            rounded = rounded_weight(z, h)
            assert rounded >= F(h, h + 1) * z and 1 - rounded >= F(h, h + 1) * (1 - z)
        for x in product((0, 1), repeat=8):
            guarded_finite(x, 2, 2, F(3, 7), bits)
            gate_checks += 1
    return {
        "normalized_string_checks": strings,
        "comparator_checks": comparisons,
        "distinct_boundary_laws": histograms,
        "adaptive_two_expert_gate_checks": gate_checks,
        "discarded_cut_weights": [str(cut_weight(b)) for b in (F(1, 4), F(1, 128))],
    }


def known_alternating_rows(x):
    # Both inputs toggle the state. The head learns the raw symbols in each phase.
    counts = [[2, 0], [0, 1]]
    phase = 1
    prob = F(1)
    for a in x:
        prob *= F(counts[phase][a] + 1, sum(counts[phase]) + 2)
        counts[phase][a] += 1
        phase = 1 - phase
    return prob


def score(x, b, limit, eta, oracle, c):
    predictor = BlockPredictor(2, b, limit)
    kept_counts = [2, 1]
    kept = fallback = mixture = F(1)
    max_gate_bits = 0
    for a in x:
        kept_row = tuple(F(v + 1, sum(kept_counts) + 2) for v in kept_counts)
        block_row = predictor.forecast()
        weight = eta * fallback / ((1 - eta) * kept + eta * fallback)
        max_gate_bits = max(
            max_gate_bits,
            weight.numerator.bit_length() + weight.denominator.bit_length(),
        )
        law = tuple(
            (1 - weight) * u + weight * v
            for u, v in zip(kept_row, block_row, strict=True)
        )
        assert sum(law) == 1
        mixture *= law[a]
        kept *= kept_row[a]
        fallback *= block_row[a]
        kept_counts[a] += 1
        predictor.observe(a)
    assert fallback == block_probability(x, 2, b, limit)
    assert mixture == (1 - eta) * kept + eta * fallback
    bound = structure_factor(len(x), 2, b, c, c, limit)
    assert oracle <= fallback * bound and mixture >= eta * fallback
    cells = len(predictor.counts)
    return {
        "kept_nats": -log(kept),
        "fallback_nats": -log(fallback),
        "mixture_nats": -log(mixture),
        "guard_posterior": float(eta * fallback / mixture),
        "pointwise_excess_to_oracle_nats": log(oracle / mixture),
        "pointwise_upper_nats": log(bound / eta),
        "dense_counter_bits_at_limit_or_this_horizon": cells
        * predictor.peak.bit_length(),
        "counter_cells": cells,
        "largest_counter": predictor.peak,
        "raw_forecasts_and_cursor_advances": len(x),
        "histogram_increments": predictor.updates,
        "counter_clear_writes": predictor.clears * cells,
        "max_exact_gate_fraction_bits_before_forecast": max_gate_bits,
    }


def experiment():
    tapes = {
        "alternating": (1, 0) * 128,
        "fair_iid": tuple(
            map(int, np.random.Generator(np.random.PCG64(261127)).integers(2, size=256))
        ),
    }
    records = {}
    for name, x in tapes.items():
        oracle = F(1) if name == "alternating" else F(1, 2 ** len(x))
        entry = {
            "tape": "".join(map(str, x)),
            "oracle_nats": -log(oracle),
            "two_phase_row_learner_nats": -log(known_alternating_rows(x)),
            "comparisons": [],
        }
        for b in (1, 2, 4):
            for limit in (None, 16):
                for beta in (F(1, 4), F(1, 128)):
                    eta = cut_weight(beta)
                    result = score(
                        x, b, limit, eta, oracle, 2 if name == "alternating" else 1
                    )
                    entry["comparisons"].append(
                        {
                            "block_length": b,
                            "reset_blocks": limit,
                            "beta": str(beta),
                            "discarded_mass": str(eta),
                            **result,
                        }
                    )
        entry["supplemental_fully_capped"] = [
            {"beta": str(beta), **guarded_finite(x, 2, 16, cut_weight(beta), bits)}
            for beta in (F(1, 4), F(1, 128))
            for bits in (0, 2, 4, 8)
        ]
        records[name] = entry
    return {"registration": "45217a9", "tapes": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check() if args.command == "check" else experiment()
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(encoded.encode())
    else:
        print(encoded, end="")
