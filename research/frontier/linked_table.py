"""Infer arbitrary binary history values from linked tokens, including unseen transitions."""

import argparse
import json
from collections import deque
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import atanh, comb, prod
from pathlib import Path

import numpy as np
from linked_parity import gain
from scipy.linalg import eigh
from threadpoolctl import threadpool_limits

REGISTRATION = "6b2b606"
SIZES = (256, 2048, 16384)
REPEATS = 32


class Words:
    def __init__(self, memory):
        self.memory = memory
        self.v = 1 << memory
        edge = np.arange(2 * self.v)
        self.left = edge // 2
        self.right = edge % self.v
        self.loop = self.left == self.right
        middle = self.left % (self.v // 2)
        self.distinct = (middle != 0) & (middle != self.v // 2 - 1)
        self.held = self.distinct & (self.left < self.v // 2) & (edge % 2 == 0)
        self.powers = 1 << np.arange(memory - 1, -1, -1)
        if memory % 2:
            hidden = set(zip(self.left[self.held], self.right[self.held], strict=True))
            assert not any(
                (v, u) in hidden for u, v in zip(self.left, self.right, strict=True)
            )

    def tasks(self, rng, table, a):
        n = SIZES[-1]
        raw = np.empty((n, self.memory + 2), dtype=np.int8)
        raw[:, : self.memory] = 1 - 2 * rng.integers(
            2, size=(n, self.memory), dtype=np.int8
        )
        phase = 1 - 2 * rng.integers(2, size=n, dtype=np.int8)
        w = (raw[:, : self.memory] < 0) @ self.powers
        for t in range(2):
            flip = rng.integers(8, size=n) >= int(4 * (1 + a))
            bit = phase * table[w] * (1 - 2 * flip.astype(np.int8))
            raw[:, self.memory + t] = bit
            w = (2 * w + (bit < 0)) % self.v
        return raw

    def observations(self, raw):
        word = (raw[:, : self.memory] < 0) @ self.powers
        return 2 * word + (raw[:, -2] < 0), raw[:, -2] * raw[:, -1]

    def relations(self, signed):
        matrix = np.zeros((self.v, self.v), dtype=np.int64)
        matrix[self.left, self.right] = signed
        matrix = matrix + matrix.T
        np.fill_diagonal(matrix, 0)
        return matrix

    def square(self, signed, reliability):
        """Use direct and alternate path evidence on each four-vertex square."""
        field = signed * atanh(reliability)
        query = np.flatnonzero(self.distinct)

        def combine(a, b):
            return (np.logaddexp(a + b, -a - b) - np.logaddexp(a - b, b - a)) / 2

        alternate = combine(field[query ^ 1], field[query ^ self.v])
        field[query] += combine(alternate, field[query ^ self.v ^ 1])
        relation = np.tanh(field)
        relation[self.loop] = 1
        return reliability * relation

    def forest(self, matrix, reliability):
        """Use a maximum-weight forest, discarding the signs of all other relations."""
        parent = list(range(self.v))
        neighbors = [[] for _ in parent]

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        rows, cols = np.nonzero(np.triu(matrix, 1))
        ordered = sorted(
            zip(rows.tolist(), cols.tolist(), strict=True),
            key=lambda ij: -abs(matrix[ij]),
        )
        used = 0
        for i, j in ordered:
            u, v = root(i), root(j)
            if u == v:
                continue
            parent[u] = v
            value = np.tanh(atanh(reliability) * matrix[i, j])
            neighbors[i].append((j, value))
            neighbors[j].append((i, value))
            used += 1
        correlation = np.zeros((self.v, self.v))
        for i in range(self.v):
            queue = deque([(i, -1, 1.0)])
            while queue:
                at, previous, value = queue.popleft()
                correlation[i, at] = value
                for nxt, weight in neighbors[at]:
                    if nxt != previous:
                        queue.append((nxt, at, value * weight))
        # A sign estimate for each independent tree is useful as a third spectral start.
        signs = np.ones(self.v, dtype=np.int64)
        for i in range(self.v):
            signs[i] = 1 if correlation[i, root(i)] >= 0 else -1
        return reliability * correlation[self.left, self.right], signs, used

    def spectral(self, matrix, forest):
        """Round a leading eigenvector, then improve ordinary profiled sign agreement."""
        _, vectors = eigh(matrix, subset_by_index=(self.v - 1, self.v - 1))
        eigen = np.where(vectors[:, 0] < 0, -1, 1)
        tolerance = 1e-12 * np.max(np.abs(matrix)) if matrix.dtype.kind == "f" else 0
        best_value = -np.inf
        checks = 0
        for initial in (eigen, np.ones(self.v, dtype=np.int64), forest):
            labels = initial.copy()
            fields = matrix @ labels
            while True:
                changed = False
                for i in range(self.v):
                    checks += 1
                    if labels[i] * fields[i] < -tolerance:
                        labels[i] *= -1
                        fields += (2 * labels[i]) * matrix[:, i]
                        changed = True
                if not changed:
                    break
            value = (labels @ fields).item()
            if value > best_value:
                best, best_value = labels.copy(), value
        return best, checks


def rational_checks():
    memory = 3
    graph = Words(memory)
    reliability = F(1, 4)
    a = F(1, 2)
    density_checks = posterior_checks = 0
    hidden = int(np.flatnonzero(graph.held)[0])
    neighbors = (hidden ^ 1, hidden ^ graph.v, hidden ^ graph.v ^ 1)
    tables = [(1, *remaining) for remaining in product((-1, 1), repeat=graph.v - 1)]
    for table in tables:
        for e, (u, v) in enumerate(zip(graph.left, graph.right, strict=True)):
            x = 1 - 2 * (e % 2)
            for y in (-1, 1):
                density = sum(
                    (1 + a * h * x * table[u]) * (1 + a * h * y * table[v]) / 2
                    for h in (-1, 1)
                )
                assert density == 1 + reliability * x * y * table[u] * table[v]
                density_checks += 1
    for length in range(5):
        selected = (*neighbors, hidden)[:length]
        for observations in product((-1, 1), repeat=length):
            weights = [
                prod(
                    1 + reliability * z * table[graph.left[e]] * table[graph.right[e]]
                    for e, z in zip(selected, observations, strict=True)
                )
                for table in tables
            ]
            average = sum(
                w * table[graph.left[hidden]] * table[graph.right[hidden]]
                for w, table in zip(weights, tables, strict=True)
            ) / sum(weights)
            signed = np.zeros(2 * graph.v, dtype=np.int64)
            signed[list(selected)] = observations
            model = graph.square(signed, float(reliability))[hidden]
            assert abs(float(reliability * average) - model) < 1e-14
            if length < 3:
                assert average == 0
            if length == 3:
                assert abs(average) == reliability**3
            if length <= 3:
                predicted, _, _ = graph.forest(
                    graph.relations(signed), float(reliability)
                )
                assert abs(predicted[hidden] - model) < 1e-14
            posterior_checks += 1
    return {
        "raw_densities": density_checks,
        "complete_table_posterior_checks": posterior_checks,
    }


def coded_memory():
    # Column i of a Hamming parity check is the nonzero binary integer i.
    for m in (2, 3, 4):
        n = (1 << m) - 1
        cells = {}
        for x in range(1 << n):
            syndrome = 0
            for i in range(1, n + 1):
                if x & (1 << (i - 1)):
                    syndrome ^= i
            word = x ^ (1 << (syndrome - 1)) if syndrome else x
            cells[word] = cells.get(word, 0) + 1
        assert len(cells) == 2 ** (n - m) and set(cells.values()) == {n + 1}

    def entropy_gain(a):
        return ((1 + a) * (1 + a).ln() + (1 - a) * (1 - a).ln()) / 2

    out = []
    with localcontext() as ctx:
        ctx.prec = 65
        for m in (5, 7, 16, 24, 32):
            v = 2**m
            for lmbda in (Decimal(1) / 4, Decimal(9) / 16):
                oracle = entropy_gain(lmbda)
                root = entropy_gain(lmbda * (1 - Decimal(2) / v))
                other = entropy_gain(lmbda * (1 - Decimal(4) / v))
                gap = (2 * (oracle - root) + (2 * v - 4) * (oracle - other)) / (2 * v)
                linear = m * oracle / (2 * v)
                out.append(
                    {
                        "M": m,
                        "retained_bits": v - 1 - m,
                        "reliability": str(lmbda),
                        "hamming_exact_average_excess": float(gap),
                        "all_linear_packets_proved_excess_floor": float(linear),
                        "hamming_beats_every_linear_packet_certified": bool(
                            gap < linear
                        ),
                    }
                )
    return out


def score_prefix(graph, endpoint, observed, table, a, signal, hide, n):
    keep = ~graph.held[endpoint] if hide else np.ones(len(endpoint), dtype=bool)
    edge = endpoint[keep]
    counts = np.bincount(edge, minlength=2 * graph.v)
    positive = np.bincount(edge[observed[keep] > 0], minlength=2 * graph.v)
    signed = 2 * positive - counts
    reliability = a * a
    matrix = graph.relations(signed)
    forest, starting, kept = graph.forest(matrix, reliability)
    labels, checks = graph.spectral(matrix, starting)
    truth = (reliability if signal else 0.0) * table[graph.left] * table[graph.right]
    means = {
        "direct_KT": signed / (counts + 1),
        "direct_known_strength": reliability * np.tanh(atanh(reliability) * signed),
        "square": graph.square(signed, reliability),
        "forest": forest,
        "spectral_refined": reliability * labels[graph.left] * labels[graph.right],
    }
    collision = (signed @ signed - counts.sum()) / 2
    available_fraction = 1 - (graph.held.mean() if hide else 0)
    expected_signal = comb(n, 2) * reliability**2 * available_fraction / (2 * graph.v)
    declares_signal = collision > expected_signal / 2
    means["forest_if_detected"] = forest if declares_signal else np.zeros_like(forest)
    recovered = np.abs(labels @ table) == graph.v
    return {
        "available_pairs": int(counts.sum()),
        "visible_distinct_arcs": int((counts > 0).sum()),
        "forest_edges": kept,
        "spectral_coordinate_checks": checks,
        "spectral_correct_entries_up_to_flip": int((graph.v + abs(labels @ table)) // 2)
        if signal
        else None,
        "exact_spectral_table": int(recovered and signal),
        "collision_declares_signal": int(declares_signal),
        "full": {name: gain(truth, mu) for name, mu in means.items()},
        "designated": {
            name: gain(truth[graph.held], mu[graph.held]) for name, mu in means.items()
        },
    }


def summary(rows):
    data = {}
    for name in rows[0]:
        values = [r[name] for r in rows]
        if isinstance(values[0], dict):
            data[name + "_mean_gain"] = {
                k: float(np.mean([v[k] for v in values])) for k in values[0]
            }
        elif name in ("exact_spectral_table", "collision_declares_signal"):
            data[name + "_runs"] = sum(values)
        elif values[0] is not None:
            data["mean_" + name] = float(np.mean(values))
    return data


def audit():
    exact = rational_checks()
    packets = coded_memory()
    records = []
    with threadpool_limits(limits=1):
        for memory in (5, 7):
            graph = Words(memory)
            for a in (0.5, 0.75):
                for signal in (True, False):
                    seed = 2026112600 + memory * 1000 + int(100 * a) + int(signal)
                    rng = np.random.default_rng(seed)
                    repeat = {(hide, n): [] for hide in (False, True) for n in SIZES}
                    for _ in range(REPEATS):
                        table = 1 - 2 * rng.integers(2, size=graph.v, dtype=np.int64)
                        raw = graph.tasks(rng, table, a if signal else 0.0)
                        edge, z = graph.observations(raw)
                        for (hide, n), bucket in repeat.items():
                            bucket.append(
                                score_prefix(
                                    graph, edge[:n], z[:n], table, a, signal, hide, n
                                )
                            )
                    for hide in (False, True):
                        records.append(
                            {
                                "memory": memory,
                                "response_strength": a,
                                "source_has_structure": signal,
                                "hide_designated_outcomes": hide,
                                "designated_directed_edges": int(graph.held.sum()),
                                "training": [
                                    {
                                        "subjects": n,
                                        "underlying_raw_tokens": n * (memory + 2),
                                        **summary(repeat[hide, n]),
                                    }
                                    for n in SIZES
                                ],
                            }
                        )
    return {
        "registration": REGISTRATION,
        "repetitions": REPEATS,
        "rational_checks": exact,
        "memory_codes": packets,
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
