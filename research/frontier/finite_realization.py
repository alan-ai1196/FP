"""Recover hidden finite-state updates from exact short-word probabilities, without a supplied state basis."""

import argparse
import json
from collections import deque
from functools import cache
from itertools import count, permutations, product

import mpmath as mp
from sympy import Matrix, Rational, eye, kronecker_product, ones, zeros


def machine(actions, weights):
    k, d = len(weights), len(actions)
    operators = [zeros(k) for _ in range(d)]
    for s, row in enumerate(weights):
        for a, counts in enumerate(row):
            operators[a][s, actions[a][s]] = Rational(counts, sum(row))
    transition = sum(operators, zeros(k))
    if ones(1, k) * transition == ones(1, k):
        initial = ones(1, k) / k
    else:
        (vector,) = (transition.T - eye(k)).nullspace()
        initial = vector.T / sum(vector)
    assert min(initial) > 0 and initial * transition == initial

    @cache
    def prefix(w):
        return initial if not w else prefix(w[:-1]) * operators[w[-1]]

    queried = set()

    def probability(w):
        assert len(w) <= 2 * k - 1
        queried.add(w)
        return sum(prefix(w))

    return operators, initial, probability, queried


def linear_model(rank, d, probability):
    words = [w for length in range(rank) for w in product(range(d), repeat=length)]
    us = []
    h = zeros(0, len(words))
    for u in words:
        extended = h.col_join(Matrix([[probability(u + v) for v in words]]))
        if extended.rank() > len(us):
            us.append(u)
            h = extended
            if len(us) == rank:
                break
    _, cols = h.rref()
    assert len(cols) == rank
    vs = [words[i] for i in cols]
    inverse = h[:, cols].inv()
    ops = [
        inverse * Matrix([[probability(u + (a,) + v) for v in vs] for u in us])
        for a in range(d)
    ]
    terminal = inverse * Matrix([probability(u) for u in us])
    initial = Matrix([[probability(v) for v in vs]])
    return ops, terminal, initial


def basis(m):
    rref, pivots = m.rref()
    return rref[: len(pivots), :].as_immutable()


def image_spaces(ops):
    root = eye(ops[0].rows).as_immutable()
    seen, queue = {root: ()}, deque([root])
    while queue:
        u = queue.popleft()
        for a, op in enumerate(ops):
            v = basis(u * op)
            if v not in seen:
                seen[v] = seen[u] + (a,)
                queue.append(v)
    return seen


def positive_spectrum(m):
    # Identity-action words in the rational fixtures have positive rational eigenvalues.
    _, factors = m.charpoly().as_poly().factor_list()
    return all(f.degree() == 1 and -f.nth(0) / f.nth(1) > 0 for f, _ in factors)


def product_operator(ops, w):
    out = eye(ops[0].rows)
    for i in w:
        out = out * ops[i]
    return out


def split_rows(spaces, transform):
    result = []
    for v in spaces:
        restricted = v.T.gauss_jordan_solve((v * transform).T)[0].T
        for _, _, vectors in restricted.T.eigenvects():
            result.append(Matrix.vstack(*(x.T for x in vectors)) * v)
    return result


def loop_generators(start, ops):
    """Transport maps between minimum subspaces back to one observable basis."""
    r = start.rows
    paths, queue = {start: eye(r)}, deque([start])
    loops = []
    while queue:
        u = queue.popleft()
        for op in ops:
            image = u * op
            v = basis(image)
            assert v.rows == r
            edge = v.T.gauss_jordan_solve(image.T)[0].T
            transport = paths[u] * edge
            if v not in paths:
                paths[v] = transport
                queue.append(v)
            loop = transport * paths[v].inv()
            if loop not in loops:
                loops.append(loop)
    return loops


def trace_algebra(generators):
    """Independent rational audit of the matrix-algebra method at ranks two and three."""
    r = generators[0].rows
    assert r in (2, 3)
    generators = [(g, kronecker_product(g, g.inv().T)) for g in generators]
    echelon, algebra = {}, []

    def include(g, action, length):
        vector = list(action)
        for j, x in enumerate(vector):
            if not x:
                continue
            if j not in echelon:
                echelon[j] = [v / x for v in vector[j:]]
                algebra.append((g, action, length))
                return
            for pos, coeff in enumerate(echelon[j], j):
                vector[pos] -= x * coeff

    include(eye(r), eye(r * r), 0)
    for g, action, length in algebra:
        for gen, adjoint in generators:
            include(g * gen, action * adjoint, length + 1)
    # The eigenvalue phases give the number of permutation fixed points. In
    # ranks two and three cycle parity and existence of a positive trace suffice.
    signs = [g.det() > 0 for g, _, _ in algebra]

    def character(i, j):
        if r == 2:
            return 2 if signs[i] == signs[j] else 0
        if signs[i] != signs[j]:
            return 1
        return 3 if (algebra[i][0] * algebra[j][0]).trace() else 0

    tr = Matrix(
        [[character(i, j) for j in range(len(algebra))] for i in range(len(algebra))]
    )
    constraints = []
    for coeff in tr.nullspace():
        matrix = sum(
            (c * entry[1] for c, entry in zip(coeff, algebra, strict=True) if c),
            zeros(r * r),
        )
        constraints.append(matrix)
    matrix = Matrix.vstack(*constraints) if constraints else zeros(0, r * r)
    diagonal = [v.reshape(r, r) for v in matrix.nullspace()]
    assert len(diagonal) == r
    lines = [eye(r)]
    for operator in diagonal:
        lines = split_rows(lines, operator)
    assert len(lines) == r
    return lines, {
        "conjugation_algebra_dimension": len(algebra),
        "largest_basis_word_length": max(t for _, _, t in algebra),
    }


def identify(rank, d, probability, check_algebra=True):
    ops, terminal, initial = linear_model(rank, d, probability)
    seen = image_spaces(ops)
    subspace = min(seen, key=lambda u: (u.rows, len(seen[u]), seen[u]))
    r = subspace.rows
    eigenspaces = [eye(r)]
    longest_return = products_checked = 0
    split_lengths = []
    if r > 1:
        for length in count(1):
            for w in product(range(d), repeat=length):
                path = product_operator(ops, w)
                products_checked += 1
                if basis(subspace * path) != subspace:
                    continue
                transform = subspace.T.gauss_jordan_solve((subspace * path).T)[0].T
                if positive_spectrum(transform):
                    longest_return = length
                    previous_size = len(eigenspaces)
                    eigenspaces = split_rows(eigenspaces, transform)
                    if len(eigenspaces) > previous_size:
                        split_lengths.append(length)
                    if len(eigenspaces) == r:
                        break
            if len(eigenspaces) == r:
                break
    assert len(eigenspaces) == r
    axes = []

    def register(row):
        norm = (row * terminal)[0]
        assert norm
        row = (row / norm).as_immutable()
        if row not in axes:
            axes.append(row)
        return axes.index(row)

    for line in eigenspaces:
        register(line * subspace)
    trace_audit = None
    if check_algebra and r in (2, 3):
        separate, trace_audit = trace_algebra(loop_generators(subspace, ops))
        spectral = [line * subspace for line in separate]
        assert {(row / (row * terminal)[0]).as_immutable() for row in spectral} == set(
            axes
        )
    recovered = []
    for row in axes:  # New normalized rows join the forward closure during iteration.
        edges = []
        for op in ops:
            next_row = row * op
            edges.append((register(next_row), (next_row * terminal)[0]))
        recovered.append(edges)
    transition = zeros(len(axes))
    for s, outcomes in enumerate(recovered):
        for dest, p in outcomes:
            transition[s, dest] += p
    (vector,) = (transition.T - eye(len(axes))).nullspace()
    mu = vector.T / sum(vector)
    assert min(mu) > 0 and sum(mu) == 1
    assert mu * Matrix.vstack(*axes) == initial
    return (
        recovered,
        mu,
        {
            "image_subspaces": len(seen),
            "minimum_rank": r,
            "minimum_subspaces": sum(v.rows == r for v in seen),
            "longest_return_examined_with_positive_spectrum": longest_return,
            "separating_return_lengths": split_lengths,
            "word_products_examined": products_checked,
            "trace_algebra_audit": trace_audit,
        },
    )


def check(name, actions, rows, rank=None, check_algebra=True):
    k, d = len(rows), len(actions)
    rank = k if rank is None else rank
    ops, initial, probability, queried = machine(actions, rows)
    got, mu, stats = identify(rank, d, probability, check_algebra)
    assert len(got) == k and max(map(len, queried)) <= 2 * rank - 1
    for labels in permutations(range(k)):
        if all(
            got[i][a]
            == (labels.index(actions[a][labels[i]]), sum(ops[a].row(labels[i])))
            for i in range(k)
            for a in range(d)
        ) and all(mu[i] == initial[labels[i]] for i in range(k)):
            break
    else:
        raise AssertionError("the inferred machine differs from the generating one")
    return dict(
        stats,
        source=name,
        states=k,
        supplied_hankel_rank=rank,
        alphabet=d,
        distinct_raw_moments=len(queried),
        longest_observed_word=max(map(len, queried)),
    )


def main():
    # A two-phase independently emitted permutation source crossed with a
    # three-name reset source of linear rank two. Its minimum images have size two.
    paired = [(b, j) for b in range(2) for j in range(3)]
    product_actions = tuple(
        tuple(3 * (1 - s) + j for s, i in paired) for b, j in paired
    )
    left, right = ((3, 1), (1, 3)), ((1, 2, 5), (3, 2, 3), (5, 2, 1))
    product_rows = tuple(
        tuple(left[s][b] * right[i][j] for b, j in paired) for s, i in paired
    )
    return [
        check(
            "three_reset_names",
            ((0, 0, 0), (1, 1, 1), (2, 2, 2)),
            ((6, 3, 1), (1, 6, 3), (2, 2, 6)),
        ),
        check(
            "noncommuting_permutations",
            ((1, 2, 0), (1, 0, 2)),
            ((1, 2), (2, 3), (3, 1)),
        ),
        check(
            "common_four_cycle",
            ((1, 2, 3, 0),) * 4,
            tuple(tuple(7 if i == a else 1 for a in range(4)) for i in range(4)),
        ),
        check(
            "two_minimum_images",
            ((1, 0, 3, 2), (2, 3, 0, 1), (0, 0, 2, 2)),
            ((4, 2, 2), (2, 4, 2), (3, 3, 2), (1, 5, 2)),
        ),
        check("dependent_reset_rows", ((0, 0, 0), (1, 1, 1), (2, 2, 2)), right, rank=2),
        check(
            "period_six",
            ((1, 2, 3, 4, 5, 0), (0,) * 6, (0,) * 6),
            tuple((8, 4 + v, 4 - v) for v in (2, 1, -1, -2, -1, 1)),
            rank=3,
        ),
        check("dependent_nonmerging_pairs", product_actions, product_rows, rank=4),
    ]


def adjacent_periods():
    """Stationary per-token KLs for the existing constant-advance probability clock."""
    with mp.workdps(85):
        tick = amplitude = mp.mpf("0.5")
        stop = 310
        weights = [(1 - tick) ** 2 * tick**j for j in range(stop)]

        def kl(p, q):
            return p * mp.log(p / q) + (1 - p) * mp.log((1 - p) / (1 - q))

        def marks(k):
            return [
                (1 + amplitude * mp.cospi(mp.mpf(2 * j) / k)) / 2 for j in range(stop)
            ]

        out = []
        for k in (16, 64, 256, 1024, 4096):
            p, successor = marks(k), marks(k + 1)
            characteristic = (1 - tick) / (1 - tick * mp.expjpi(mp.mpf(2) / k))
            mean = (1 + amplitude * characteristic.real) / 2
            adj = sum(
                w * kl(x, y) for w, x, y in zip(weights, p, successor, strict=True)
            )
            iid = sum(w * kl(x, mean) for w, x in zip(weights, p, strict=True))
            out.append(
                {
                    "period": k,
                    "times_k6_adjacent_KL": float(k**6 * adj),
                    "times_k4_best_iid_KL": float(k**4 * iid),
                }
            )
        assert abs(out[-1]["times_k6_adjacent_KL"] / float(100 * mp.pi**4) - 1) < 0.001
        assert abs(out[-1]["times_k4_best_iid_KL"] / float(22 * mp.pi**4) - 1) < 0.001
        bound = (1 - tick) * tick**stop * mp.log((1 + amplitude) / (1 - amplitude))
        return {"rates": out, "unscaled_truncation_upper": float(bound)}


def binary_three_catalog():
    by_rank, by_minimum = {}, {}
    rows = ((1, 4), (2, 3), (4, 1))
    maps = list(product(range(3), repeat=3))
    witnesses = [w for n in range(3) for w in product(range(2), repeat=n)]
    for ops in product(maps, repeat=2):

        def reachable(s, transitions=ops):
            seen = [s]
            for i in seen:
                for t in transitions:
                    if t[i] not in seen:
                        seen.append(t[i])
            return len(seen) == 3

        if not all(reachable(s) for s in range(3)):
            continue
        _, _, probability, _ = machine(ops, rows)
        rank = Matrix(
            [[probability(u + v) for v in witnesses] for u in witnesses]
        ).rank()
        verified = check("binary_catalog", ops, rows, rank, check_algebra=False)
        r = verified["minimum_rank"]
        by_rank[rank] = by_rank.get(rank, 0) + 1
        by_minimum[r] = by_minimum.get(r, 0) + 1
    return {
        "complete_three_state_binary_catalog": sum(by_rank.values()),
        "by_hankel_rank": by_rank,
        "by_minimum_image_size": by_minimum,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", action="store_true")
    options = parser.parse_args()
    result = (
        binary_three_catalog()
        if options.catalog
        else {"reconstructions": main(), "period_resolution": adjacent_periods()}
    )
    print(json.dumps(result, indent=2))
