"""Full-vocabulary interpolated trigram with byte-budgeted purchase of entire rows."""

import struct

import numpy as np


def locations(keys, query):
    """Find indices in a sorted nonempty key array, with a separate membership mask."""
    index = np.minimum(np.searchsorted(keys, query), len(keys) - 1)
    return index, keys[index] == query


def lookup(keys, values, query):
    index, found = locations(keys, query)
    return np.where(found, values[index], 0)


def pair_ids(first, second):
    return (first.astype(np.uint64) << 16) | second


def knapsack(weights, values, capacity):
    """Integer at-most-capacity DP. Prefer the earlier rows on an exact tie."""
    best = np.zeros(capacity + 1, dtype=np.int64)
    moves = []
    for weight, value in zip(weights.tolist(), values.tolist(), strict=True):
        alternative = best[:-weight] + value
        take = alternative > best[weight:]
        moves.append(np.packbits(take, bitorder="little"))
        np.maximum(best[weight:], alternative, out=best[weight:])
    remaining = capacity
    chosen = []
    for j in reversed(range(len(moves))):
        weight = int(weights[j])
        i = remaining - weight
        if i >= 0 and int(moves[j][i // 8]) & (1 << (i % 8)):
            chosen.append(j)
            remaining -= weight
    chosen.reverse()
    assert sum(int(values[j]) for j in chosen) == best[-1]
    return np.array(chosen, dtype=np.int64), int(best[-1])


class Trigram:
    def __init__(self, tokens):
        keys = pair_ids(pair_ids(tokens[:-2], tokens[1:-1]), tokens[2:])
        self.keys, self.counts = np.unique(keys, return_counts=True)
        self.counts = self.counts.astype(np.uint32)
        self.pairs, self.offset = np.unique(self.keys >> 16, return_index=True)
        self.degree = np.diff(self.offset, append=len(self.keys))
        self.total = np.add.reduceat(self.counts, self.offset, dtype=np.uint32)

    def combined(self, obs, tau):
        contexts = pair_ids(obs.history, obs.query)
        index, found = locations(self.pairs, contexts)
        counts = lookup(self.keys, self.counts, pair_ids(contexts, obs.target))
        total = np.where(found, self.total[index], 0)
        ratio = (counts / obs.base + tau) / (total + tau)
        return index, found, np.log(ratio)

    def purchase(self, obs, tau, cap_bytes, rent):
        index, found, gain = self.combined(obs, tau)
        benefit = np.bincount(
            index[found], weights=gain[found], minlength=len(self.pairs)
        )
        size = 12 + 6 * self.degree
        units = np.rint(1e7 * (benefit - rent * 8 * size)).astype(np.int64)
        candidates = np.flatnonzero((units > 0) & (size <= cap_bytes - 11))
        capacity = max(0, (cap_bytes - 11) // 6)
        selected, net = knapsack(size[candidates] // 6, units[candidates], capacity)
        if net * 1e-7 <= rent * 8 * 11:
            selected = selected[:0]
        installed = candidates[selected]
        return installed, {
            "eligible_rows": len(candidates),
            "dp_capacity_units": capacity,
            "dp_cells_visited": int(sum((capacity + 1) - size[candidates] // 6)),
            "active_rows": len(installed),
            "active_entries": int(self.degree[installed].sum()),
        }

    def bits(self, active):
        return (
            8 * (11 + 12 * len(active) + 6 * int(self.degree[active].sum()))
            if len(active)
            else 0
        )

    def score(self, obs, tau, active=None):
        index, found, gain = self.combined(obs, tau)
        if active is None:
            total_gain = gain.sum()
        else:
            mask = np.zeros(len(self.pairs), dtype=bool)
            mask[active] = True
            total_gain = gain[found & mask[index]].sum()
        return float(-np.log(obs.base).sum() - total_gain)

    def pack(self, tau, active):
        if not len(active):
            return b""
        header = struct.pack("<IIB", len(active), int(self.degree[active].sum()), tau)
        index = bytearray()
        entries = bytearray()
        for j in active:
            uq = int(self.pairs[j])
            index.extend(
                struct.pack(
                    "<HHII", uq >> 16, uq & 65535, len(entries) // 6, int(self.total[j])
                )
            )
            start = int(self.offset[j])
            for i in range(start, start + int(self.degree[j])):
                entries.extend(
                    struct.pack("<HI", int(self.keys[i]) & 65535, int(self.counts[i]))
                )
        packed = header + index + entries
        assert 8 * (len(packed) + 2) == self.bits(active)
        return packed
