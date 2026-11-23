"""One-stage decision loss from a deterministic compression, with primal and dual witnesses."""

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations, product

import numpy as np
from scipy.optimize import linprog


@dataclass
class Context:
    vertices: tuple
    # Axis zero is the hidden target. Total mass includes the context's prior.
    mass: np.ndarray


def reports(ctxs, compression):
    """Columns are simulated joint laws over context, unchanged target, and reconstructed IDs."""
    mappings = [np.asarray(x, dtype=int) for x in compression]
    decoders = []
    for phi in mappings:
        size = len(np.unique(phi))
        if size == 0 or set(phi) != set(range(size)):
            raise ValueError("compressed labels must be consecutive and start at zero")
        decoders.append(
            [
                np.asarray(f, dtype=int)[phi]
                for f in product(range(len(phi)), repeat=size)
            ]
        )
    p = np.concatenate([c.mass.ravel() for c in ctxs])
    if np.any(p < 0) or not np.isclose(p.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError("context masses must be nonnegative and sum to one")
    local = []
    for c in ctxs:
        if any(v < 0 or v >= len(mappings) for v in c.vertices):
            raise ValueError("unknown local component")
        if len(set(c.vertices)) != len(c.vertices) or c.mass.shape[1:] != tuple(
            len(mappings[v]) for v in c.vertices
        ):
            raise ValueError(
                "each context needs distinct vertices and one raw axis per vertex"
            )
        # Decode the local law once for each tuple of decoders participating in this context.
        index = np.indices(c.mass.shape).reshape(c.mass.ndim, -1)
        law = {}
        for choice in product(*(range(len(decoders[v])) for v in c.vertices)):
            target = [index[0]]
            for i, (v, k) in enumerate(zip(c.vertices, choice, strict=True), 1):
                target.append(decoders[v][k][index[i]])
            destination = np.ravel_multi_index(target, c.mass.shape)
            law[choice] = np.bincount(
                destination, weights=c.mass.ravel(), minlength=c.mass.size
            )
        local.append(law)
    columns = []
    for choice in product(*(range(len(d)) for d in decoders)):
        columns.append(
            np.concatenate(
                [
                    tab[tuple(choice[v] for v in c.vertices)]
                    for c, tab in zip(ctxs, local, strict=True)
                ]
            )
        )
    return p, np.stack(columns, axis=1)


def solve(p, columns):
    """Minimize half L1 over shared decoder mixtures and independently solve its bounded-loss dual."""
    n, d = columns.shape
    # Each point has the same total mass, so its positive errors sum to half L1.
    primal = linprog(
        np.r_[np.zeros(d), np.ones(n)],
        A_ub=np.c_[columns, -np.eye(n)],
        b_ub=p,
        A_eq=np.r_[np.ones(d), np.zeros(n)][None, :],
        b_eq=[1],
        bounds=(0, None),
    )
    # A deterministic decoder is also the coarse policy that reports a raw ID.
    dual = linprog(
        np.r_[p, -1.0],
        A_ub=np.c_[-columns.T, np.ones(d)],
        b_ub=np.zeros(d),
        bounds=[(0, 1)] * n + [(None, None)],
    )
    assert primal.success and dual.success, (primal.message, dual.message)
    mixture = primal.x[:d]
    loss = dual.x[:n]
    distance = np.abs(columns @ mixture - p).sum() / 2
    witness = float(np.min(columns.T @ loss) - p @ loss)
    assert abs(distance - witness) < 1e-9 and abs(distance - primal.fun) < 1e-9
    return distance, mixture, loss


def verify(ctxs, compression, truth):
    p, columns = reports(ctxs, compression)
    d, _, loss = solve(p, columns)
    assert abs(d - float(truth)) < 1e-9
    # At this dual witness, reporting the uncompressed IDs attains the raw minimum.
    _, raw = reports(ctxs, [range(len(phi)) for phi in compression])
    assert abs(np.min(raw.T @ loss) - p @ loss) < 1e-9


def parity_example(epsilon):
    ctxs = []
    for i, j in product(range(2), repeat=2):
        mass = np.empty((1, 2, 2))
        for a, b in product(range(2), repeat=2):
            prob = (1 - epsilon) * int((a ^ b) == i * j) / 2 + epsilon / 4
            mass[0, a, b] = float(prob / 4)
        ctxs.append(Context((i, 2 + j), mass))
    return ctxs


def stability_examples():
    for n in (8, 64, 512):
        w = F(1, 2) + F(1, n)
        p, q = 1 - F(1, n), F(1, 4)
        delta = F(1, n * n)
        table = [[w * (1 - p), w * p], [(1 - w) * (1 - q), (1 - w) * q]]
        initial = (1 - w) * (p - q)
        verify([Context((0,), np.array(table, dtype=float))], [(0, 0)], initial)
        table[0][0] -= delta
        table[1][0] += delta
        increase = delta * p / (w - delta)
        verify(
            [Context((0,), np.array(table, dtype=float))], [(0, 0)], initial + increase
        )


def cut_certificate():
    edges = list(combinations(range(4), 2))
    audited = 0
    for mask in range(1, 1 << len(edges)):
        graph = [e for i, e in enumerate(edges) if mask >> i & 1]
        m = len(graph)
        # A distinct right-side vertex per edge enforces two signed bipartite comparisons.
        desired = [(i, 4 + k, 0) for k, (i, _) in enumerate(graph)] + [
            (j, 4 + k, 1) for k, (_, j) in enumerate(graph)
        ]
        best = min(
            sum(x[i] == x[j] for i, j in graph) for x in product(range(2), repeat=4)
        )
        mis, x = min(
            (sum((x[i] ^ x[j]) != t for i, j, t in desired), x)
            for x in product(range(2), repeat=4 + m)
        )
        assert mis == best
        # Primal certificate mixes x and its binary complement. The mismatch payoff is dual feasible.
        total = F(0)
        for i, j, t in desired:
            for a, b in product(range(2), repeat=2):
                p = F(int((a ^ b) == t), 2)
                q = F(
                    int((a, b) == (x[i], x[j])) + int((a, b) == (1 - x[i], 1 - x[j])), 2
                )
                total += abs(p - q)
        assert total / (4 * m) == F(best, 2 * m)
        audited += 1
    return audited


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    for noise in (F(0), F(1, 8), F(1, 4), F(3, 8), F(1, 2), F(3, 4), F(1)):
        value = max(F(0), F(1, 4) - noise / 2)
        verify(parity_example(noise), [(0, 0)] * 4, value)
    compression = [(0, 0, 1, 1)]
    for target, d in ((lambda r: r // 2, F(0)), (lambda r: r % 2, F(1, 2))):
        mass = np.zeros((2, 4))
        for r in range(4):
            mass[target(r), r] = 0.25
        verify([Context((0,), mass)], compression, d)
    print(
        "primal, dual and all deterministic reporting policies agree on seven noise levels and two target-compression problems"
    )
    stability_examples()
    print("six binary hidden-target stability examples verified")
    print("exact bipartite signed cut certificates", cut_certificate())
