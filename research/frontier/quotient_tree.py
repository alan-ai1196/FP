"""An exact marginal LP on a tree decomposition of the co-occurring decoder entries."""

from itertools import pairwise, product

import numpy as np
from quotient_value import Context, reports, solve
from scipy import sparse
from scipy.optimize import linprog


def sparse_rows(entries, shape):
    row, col, data = zip(*entries, strict=True)
    return sparse.coo_matrix((data, (row, col)), shape=shape).tocsr()


def tree_distance(contexts, compression, bags, parents):
    """The parent of each later bag must precede it and connected bags must cover each entry."""
    if len(bags) != len(parents) or not parents or parents[0] != -1:
        raise ValueError("one rooted tree of bags is required")
    alphabets = list(map(len, compression))
    variables = set()
    for i, (bag, parent) in enumerate(zip(bags, parents, strict=True)):
        if len(set(bag)) != len(bag) or (i and not 0 <= parent < i):
            raise ValueError("invalid bag or parent")
        for v, s in bag:
            if v < 0 or v >= len(alphabets) or s not in compression[v]:
                raise ValueError("unknown decoder entry")
        if i and not (set(bag) & variables) <= set(bags[parent]):
            raise ValueError(
                "bags containing a decoder entry must form a connected subtree"
            )
        variables.update(bag)
    settings = [list(product(*(range(alphabets[v]) for v, _ in bag))) for bag in bags]
    offsets = np.cumsum([0] + [len(s) for s in settings]).tolist()
    n = offsets[-1]
    eq = [(0, j, 1) for j in range(offsets[1])]
    rhs = [1.0]
    for i, parent in enumerate(parents[1:], 1):
        separator = sorted(set(bags[i]) & set(bags[parent]))
        dims = tuple(alphabets[v] for v, _ in separator)
        start = len(rhs)
        rhs.extend([0.0] * int(np.prod(dims, dtype=int)))
        for b, sign in ((i, 1), (parent, -1)):
            positions = [bags[b].index(x) for x in separator]
            for k, assignment in enumerate(settings[b]):
                index = (
                    np.ravel_multi_index(tuple(assignment[j] for j in positions), dims)
                    if dims
                    else 0
                )
                eq.append((start + index, offsets[b] + k, sign))
    pairs = []
    first = 0
    for c in contexts:
        shape = c.mass.shape
        if len(set(c.vertices)) != len(c.vertices) or shape[1:] != tuple(
            alphabets[v] for v in c.vertices
        ):
            raise ValueError("joint observation shape does not match its components")
        encoded = {}
        for index in zip(*np.nonzero(c.mass), strict=True):
            y, *raw = index
            entry = tuple(
                (v, compression[v][r]) for v, r in zip(c.vertices, raw, strict=True)
            )
            encoded.setdefault(entry, np.zeros(shape[0]))[y] += c.mass[index]
        for entry, mass in encoded.items():
            b = next((i for i, bag in enumerate(bags) if set(entry) <= set(bag)), None)
            if b is None:
                raise ValueError("no bag covers an observed set of decoder entries")
            positions = [bags[b].index(x) for x in entry]
            for k, assignment in enumerate(settings[b]):
                raw = tuple(assignment[j] for j in positions)
                for y in np.flatnonzero(mass):
                    row = first + np.ravel_multi_index((y, *raw), shape)
                    pairs.append((row, offsets[b] + k, mass[y]))
        first += c.mass.size
    p = np.concatenate([c.mass.ravel() for c in contexts])
    if np.any(p < 0) or not np.isclose(p.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError("context masses must be nonnegative and sum to one")
    A = sparse_rows(pairs, (len(p), n))
    eq = sparse_rows(eq, (len(rhs), n))
    constraints = sparse.hstack([A, -sparse.eye(len(p))], format="csr")
    normal = sparse.hstack([eq, sparse.csr_matrix((len(rhs), len(p)))], format="csr")
    result = linprog(
        np.r_[np.zeros(n), np.ones(len(p))],
        A_ub=constraints,
        b_ub=p,
        A_eq=normal,
        b_eq=rhs,
        bounds=(0, None),
    )
    assert result.success, result.message
    d = float(np.abs(A @ result.x[:n] - p).sum() / 2)
    assert abs(result.fun - d) < 1e-9
    nbytes = sum(
        x.nbytes for m in (constraints, normal) for x in (m.data, m.indices, m.indptr)
    )
    return d, {
        "bag_entries": n,
        "deviations": len(p),
        "equalities": len(rhs),
        "nonzeros": constraints.nnz + normal.nnz,
        "csr_constraint_bytes": nbytes,
    }


def path_instance(h):
    phi = [tuple(i // 2 for i in range(2 * h))] * 2
    order = [(v, s) for s in range(h) for v in (0, 1)]
    bags = list(pairwise(order))
    mass = np.zeros((2, 2 * h, 2 * h))
    for bag in bags:
        (a, i), (b, j) = sorted(bag)
        assert a == 0 and b == 1
        for bit in range(2):
            mass[bit, 2 * i + bit, 2 * j + (bit ^ (i % 2) ^ (j % 2))] = 0.5 / len(bags)
    return [Context((0, 1), mass)], phi, bags, list(range(-1, len(bags) - 1))


def compare_overlapping_bags():
    # Two shared vertices, one with a varying code, and a disconnected singleton.
    phi = [(0, 0), (0, 1), (0, 0), (0, 0), (0, 0)]
    scopes = [(0, 1, 2), (1, 2, 3), (4,)]
    rng = np.random.default_rng(73)
    ctxs = []
    for scope in scopes:
        counts = rng.integers(1, 12, size=(2,) * (1 + len(scope)))
        ctxs.append(Context(scope, counts / (counts.sum() * len(scopes))))
    bags = [
        ((0, 0), (1, 0), (1, 1), (2, 0)),
        ((1, 0), (1, 1), (2, 0), (3, 0)),
        ((4, 0),),
    ]
    d, _ = tree_distance(ctxs, phi, bags, [-1, 0, 1])
    p, columns = reports(ctxs, phi)
    assert abs(solve(p, columns)[0] - d) < 1e-9


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("the audit requires assertions")
    compare_overlapping_bags()
    for h in (2, 4, 8, 12):
        ctxs, phi, bags, parents = path_instance(h)
        d, work = tree_distance(ctxs, phi, bags, parents)
        assert abs(d - 0.5) < 1e-9
        if h == 2:
            p, points = reports(ctxs, phi)
            assert abs(solve(p, points)[0] - d) < 1e-9
        print(
            "codes per component",
            h,
            "D",
            round(d, 12),
            "global columns",
            (2 * h) ** (2 * h),
            work,
        )
