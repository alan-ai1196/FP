"""Sufficient update coordinates for a finite bank of positive likelihoods."""

import struct

import numpy as np


def centered(v):
    return v[1:] - v[0]


def probabilities(logweights):
    w = np.exp(logweights - np.max(logweights))
    return w / w.sum()


def pack_basis(rows):
    rank, width = rows.shape
    return struct.pack("<BB", rank, width) + rows.astype("<f8", copy=False).tobytes()


def unpack_basis(payload):
    rank, width = struct.unpack_from("<BB", payload)
    if len(payload) != 2 + 8 * rank * width:
        raise ValueError("inconsistent update basis dimensions")
    return np.frombuffer(payload, dtype="<f8", offset=2).reshape(rank, width)


class LearnedBasis:
    def __init__(self, width):
        self.rows = np.empty((0, width))

    def observe(self, likelihood):
        x = centered(likelihood)
        residual = x.copy()
        for _ in range(2):
            residual -= (self.rows @ residual) @ self.rows
        norm = np.linalg.norm(residual)
        if norm > 1e-9 * max(1, np.linalg.norm(x)):
            self.rows = np.vstack((self.rows, residual / norm))


class RatioState:
    def __init__(self, bank_size):
        self.ratio = np.zeros(bank_size - 1)

    def weights(self):
        return probabilities(np.r_[0.0, self.ratio])

    def observe(self, likelihood):
        self.ratio += centered(likelihood)
        return 0.0


class ProjectedState:
    def __init__(self, rows):
        self.rows = rows
        self.coefficients = np.zeros(len(rows))

    def weights(self):
        return probabilities(np.r_[0.0, self.coefficients @ self.rows])

    def observe(self, likelihood):
        x = centered(likelihood)
        change = self.rows @ x
        self.coefficients += change
        return float(np.linalg.norm(x - change @ self.rows))


class AssignmentState:
    def __init__(self, k):
        self.gauge = np.zeros((k - 1, k - 1))

    def observe(self, arm, log_likelihood):
        delta = log_likelihood[:-1] - log_likelihood[-1]
        if arm < len(self.gauge):
            self.gauge[arm] += delta
        else:
            self.gauge -= delta

    def enumerated_weights(self, assignments):
        w = np.pad(self.gauge, ((0, 1), (0, 1)))
        return probabilities(w[np.arange(len(w)), assignments].sum(axis=1))


def subset_marginals(log_factors):
    """Two subset passes compute the permanent and every assignment marginal in log space."""
    k = len(log_factors)
    assert log_factors.shape == (k, k)
    full = (1 << k) - 1
    forward = np.full(full + 1, -np.inf)
    backward = forward.copy()
    forward[0] = backward[full] = 0
    for mask in range(1, full + 1):
        i = mask.bit_count() - 1
        forward[mask] = np.logaddexp.reduce(
            [
                forward[mask ^ (1 << j)] + log_factors[i, j]
                for j in range(k)
                if mask & (1 << j)
            ]
        )
    edge = np.zeros((k, k))
    for mask in range(full - 1, -1, -1):
        i = mask.bit_count()
        terms = []
        for j in range(k):
            if not mask & (1 << j):
                term = log_factors[i, j] + backward[mask | (1 << j)]
                terms.append(term)
                edge[i, j] += np.exp(forward[mask] + term - forward[full])
        backward[mask] = np.logaddexp.reduce(terms)
    return forward[full], edge


class PivotCode:
    """Acquire well-conditioned observable coordinates from a discovered row space."""

    def __init__(self, rows):
        from scipy.linalg import qr

        rank, width = rows.shape
        _, _, ordered = qr(rows, pivoting=True, mode="economic")
        self.keep = np.sort(ordered[:rank])
        self.rest = np.setdiff1d(np.arange(width), self.keep)
        self.decoder = np.linalg.solve(rows[:, self.keep], rows[:, self.rest])
        self.condition = float(np.linalg.cond(rows[:, self.keep]))
        mask = sum(1 << int(j) for j in self.keep)
        self.packet = (
            struct.pack("<BB", rank, width)
            + mask.to_bytes((width + 7) // 8, "little")
            + self.decoder.astype("<f8", copy=False).tobytes()
        )

    def state(self):
        rank, width = struct.unpack_from("<BB", self.packet)
        end = 2 + (width + 7) // 8
        mask = int.from_bytes(self.packet[2:end], "little")
        keep = np.array([j for j in range(width) if (mask >> j) & 1])
        rest = np.array([j for j in range(width) if not (mask >> j) & 1])
        decoder = np.frombuffer(self.packet, dtype="<f8", offset=end).reshape(
            rank, width - rank
        )
        return PivotState(keep, rest, decoder)


class PivotState:
    def __init__(self, keep, rest, decoder):
        self.keep, self.rest, self.decoder = keep, rest, decoder
        self.values = np.zeros(len(keep))

    def weights(self):
        odds = np.zeros(1 + len(self.keep) + len(self.rest))
        odds[1 + self.keep] = self.values
        odds[1 + self.rest] = self.values @ self.decoder
        return probabilities(odds)

    def observe(self, log_likelihood):
        self.values += log_likelihood[1 + self.keep] - log_likelihood[0]


class ArmPartitions:
    """Refine likelihood equality classes within each publicly observed action name."""

    def __init__(self, k, hypotheses):
        self.labels = np.zeros((k, hypotheses), dtype=np.intp)

    def observe(self, arm, log_likelihood):
        _, first, index = np.unique(
            np.column_stack((self.labels[arm], log_likelihood)),
            axis=0,
            return_index=True,
            return_inverse=True,
        )
        self.labels[arm] = np.argsort(np.argsort(first))[index]

    def packet(self):
        k, n = self.labels.shape
        if k != 4 or n != 24:
            raise ValueError(
                "the packed incidence layout is for the four-ticket workload"
            )
        sets = [
            [set(np.flatnonzero(row == i).tolist()) for i in range(row.max() + 1)]
            for row in self.labels
        ]
        if any(len(group) != k for group in sets):
            return None
        incidence = self.labels.T.copy()
        for g, group in enumerate(sets[1:], start=1):
            names = []
            for block in group:
                missing = [
                    j for j, source in enumerate(sets[0]) if block.isdisjoint(source)
                ]
                if len(missing) != 1:
                    return None
                names.append(missing[0])
            incidence[:, g] = np.asarray(names)[self.labels[g]]
        if len(set(map(tuple, incidence))) != n or np.any(
            np.sort(incidence, axis=1) != np.arange(k)
        ):
            return None
        flat = incidence.astype(np.uint8).ravel()
        data = flat[::4] | (flat[1::4] << 2) | (flat[2::4] << 4) | (flat[3::4] << 6)
        return struct.pack("<BB", k, n) + data.tobytes()


class DiscoveredAssignment:
    def __init__(self, packet):
        k, n = struct.unpack_from("<BB", packet)
        assert k == 4 and n == len(packet) - 2
        packed = np.frombuffer(packet, dtype=np.uint8, offset=2)
        self.incidence = np.column_stack([(packed >> (2 * j)) & 3 for j in range(k)])
        self.state = AssignmentState(k)
        self.representatives = np.stack(
            [
                np.flatnonzero(self.incidence[:, arm] == v)[0]
                for arm in range(k)
                for v in range(k)
            ]
        ).reshape(k, k)

    def weights(self):
        return self.state.enumerated_weights(self.incidence)

    def observe(self, arm, log_likelihood):
        values = log_likelihood[self.representatives[arm]]
        assert np.array_equal(values[self.incidence[:, arm]], log_likelihood)
        self.state.observe(arm, values)
