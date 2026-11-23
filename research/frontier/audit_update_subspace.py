"""Independent rank, parity, permanent and precision checks for the adaptive state."""

import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import permutations, product
from math import factorial, prod
from pathlib import Path

import numpy as np
from sympy import Matrix
from threadpoolctl import threadpool_limits
from update_subspace import LearnedBasis, subset_marginals


def sign(p):
    return (-1) ** sum(x > y for i, x in enumerate(p) for y in p[i + 1 :])


def structural():
    ranks = []
    trajectories = 0
    for k in range(2, 6):
        ps = list(permutations(range(k)))
        X = Matrix(
            [
                [
                    int(p[i] == j) - int(ps[0][i] == j)
                    for i in range(k)
                    for j in range(k)
                ]
                for p in ps
            ]
        )
        assert X.rank() == (k - 1) ** 2
        ranks.append(X.rank())
        weights = [[F(1)] * k for _ in range(k)]
        prior = [F(i + 1, len(ps) * (len(ps) + 1) // 2) for i in range(len(ps))]
        direct = prior.copy()
        for t in range(12):
            arm = t % k
            inc = [F(1 + (t + 2 * j) % 7, 9) for j in range(k)]
            weights[arm] = [a * b for a, b in zip(weights[arm], inc, strict=True)]
            direct = [v * inc[p[arm]] for p, v in zip(ps, direct, strict=True)]
            gauge = [
                [
                    w * weights[-1][-1] / (row[-1] * weights[-1][j])
                    for j, w in enumerate(row)
                ]
                for row in weights
            ]
            via = [
                v * prod(gauge[i][j] for i, j in enumerate(p))
                for p, v in zip(ps, prior, strict=True)
            ]
            assert all(
                u * sum(via) == v * sum(direct)
                for u, v in zip(direct, via, strict=True)
            )
            trajectories += 1
    return ranks, trajectories


def hit_path(p, bits, floor, spread):
    q = [floor + spread * (p[i] == i) for i in range(len(bits))]
    return prod(x if b else 1 - x for x, b in zip(q, bits, strict=True))


def parity():
    cases = 0
    for k in range(3, 7):
        a = F(1, 4 * k)
        spread = 1 - k * a
        ps = list(permutations(range(k)))
        even = [p for p in ps if sign(p) == 1]
        odd = [p for p in ps if sign(p) == -1]
        for t in range(k - 1):
            assert Counter(p[:t] for p in even) == Counter(p[:t] for p in odd)
        total = 0
        for bits in product((0, 1), repeat=k - 1):
            gap = (
                sum(hit_path(p, bits, a, spread) for p in even)
                - sum(hit_path(p, bits, a, spread) for p in odd)
            ) / len(even)
            assert abs(gap) == 2 * spread ** (k - 1) / factorial(k)
            total += abs(gap) / 2
            cases += 1
        assert total == (2 * spread) ** (k - 1) / factorial(k)
    return cases


def permanent_reduction():
    count = 0
    for k in (2, 3):
        ps = list(permutations(range(k)))
        n = factorial(k) + 1
        for bits in product((0, 1), repeat=k * k):
            b = np.array(bits).reshape(k, k).tolist()
            lifted = [[n + v for v in row] for row in b]
            success = F(1)
            posterior = [F(1, len(ps))] * len(ps)
            for i, row in enumerate(lifted):
                den = sum(row)
                p = [F(v, den) for v in row]
                assert min(p) > F(1, 4 * k)
                marginal = [
                    sum(w for w, h in zip(posterior, ps, strict=True) if h[i] == j)
                    for j in range(k)
                ]
                h = sum(x * y for x, y in zip(p, marginal, strict=True))
                success *= den * h
                posterior = [
                    w * p[s[i]] / h for s, w in zip(ps, posterior, strict=True)
                ]
            integer = factorial(k) * success
            assert integer.denominator == 1
            assert integer.numerator % n == sum(
                prod(b[i][j] for i, j in enumerate(s)) for s in ps
            )
            count += 1
    return count


def numeric():
    rng = np.random.default_rng(18)
    worst = 0.0
    for k in range(2, 9):
        p = np.array(list(permutations(range(k))), dtype=np.uint8)
        for scale in (1, 40):
            w = rng.normal(size=(k, k)) * scale
            z, means = subset_marginals(w)
            scores = w[np.arange(k), p].sum(axis=1)
            ref = scores.max() + np.log(np.exp(scores - scores.max()).sum())
            weights = np.exp(scores - ref)
            expected = np.stack(
                [np.bincount(col, weights=weights, minlength=k) for col in p.T]
            )
            worst = max(worst, abs(z - ref), float(np.max(np.abs(means - expected))))
    assert worst < 1e-11

    def full_mean(odds):
        p = F(odds, 1 + odds)
        return np.asarray([[p, 1 - p], [1 - p, p]], dtype=np.float64)

    assert np.array_equal(full_mean(3**700), full_mean(3**1400))
    assert np.max(np.abs(full_mean(1) - full_mean(3**700))) == 0.5
    # Check a collision with all sixteen marginal entries normal even after rounding.
    perms = list(permutations(range(4)))

    def means(eps, perturb):
        mat = [[F(1) if i == j else eps for j in range(4)] for i in range(4)]
        if perturb:
            mat[0][1] *= 2
            mat[1][0] /= 2
        w = [prod(mat[i][v] for i, v in enumerate(h)) for h in perms]
        z = sum(w)
        return [
            [
                sum(x for x, h in zip(w, perms, strict=True) if h[i] == j) / z
                for j in range(4)
            ]
            for i in range(4)
        ]

    eps = F(1, 2**80)
    left, right = (
        np.asarray(means(eps, flag), dtype=np.float64) for flag in (False, True)
    )
    assert np.min(left) == float(eps**2) and np.array_equal(left, right)
    clean, changed = means(F(1), False), means(F(1), True)
    assert (changed[0][1] - clean[0][1]) / 2 == F(7, 104)
    return worst


def unlabeled(data):
    from text_shared_state import REPORT_START, train_study
    from text_ticket_actions import generate_groups
    from text_update_subspace import BANK, DISCOVER_END, START, offers, prepare, replay

    snaps, streams, _ = prepare(data)
    study = train_study(data[:REPORT_START])
    ids = np.frombuffer(data, dtype=np.uint16)
    groups = generate_groups(study, ids[START:DISCOVER_END].reshape(-1, 3))
    # Supply only the same number of hypothetical-hit vectors, independent of purchases, prices
    # and purchased outcomes. Group membership was public in the registered task.
    source = []
    for g, (e, priors, _) in enumerate(groups):
        source.append((priors["reuse"], offers(e, 0, g).names))
    for n in (8, 64, 512):
        basis = LearnedBasis(len(BANK) - 1)
        paid, counts = snaps[n]
        for i in range(max(counts)):
            for g, (priors, names) in enumerate(source):
                if i < counts[g]:
                    basis.observe(np.log(priors[i, BANK[:, names[i]]]))
        distance = np.linalg.norm(paid.T @ paid - basis.rows.T @ basis.rows, 2)
        print(
            "unlabeled",
            n,
            "rank",
            len(basis.rows),
            "projector distance",
            f"{distance:.5g}",
        )
        if n != 512:
            continue
        snaps[999] = basis.rows, counts
        mismatches = 0
        error = 0.0
        for _, _, _, word, off in streams:
            p, b, _ = replay("posterior", word, off, snaps)
            q, c, _ = replay("learned_999", word, off, snaps)
            error = max(error, float(np.max(np.abs(p - q))))
            mismatches += np.count_nonzero(b != c)
        print(
            "unlabeled transfer decision differences",
            mismatches,
            "maximum forecast difference",
            f"{error:.5g}",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    print("exact assignment ranks and positive-prior gauge updates", structural())
    print("sharp parity transcript checks", parity())
    print(
        "Boolean permanents reconstructed through clipped success queries",
        permanent_reduction(),
    )
    print("largest log-normalizer or marginal discrepancy", numeric())
    if args.text:
        from text_update_subspace import load_data

        with threadpool_limits(limits=1):
            unlabeled(load_data(args.data_dir))
