"""Exact graph and checkerboard checks for earlier-token calibration."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations, product
from math import prod
from pathlib import Path

import numpy as np
from nested_class import BASE
from shared_readout import MULTIPLIERS, NEUTRAL
from text_nested_class import (
    END,
    REPORT_START,
    SELECTION_END,
    frozen,
    load_data,
    restore,
)
from word_classes import UNIT, Gate


def support(edges, odds):
    """Propagate products along a forest, returning all other edges and their consistency."""
    neighbors = {}
    for i, (u, q) in enumerate(edges):
        for src, dst in ((("u", u), ("q", q)), (("q", q), ("u", u))):
            neighbors.setdefault(src, []).append((dst, i))
    factor = {}
    tree = set()
    components = 0
    for vertex in neighbors:
        if vertex in factor:
            continue
        factor[vertex] = F(1)
        stack = [vertex]
        components += 1
        while stack:
            src = stack.pop()
            for dst, i in neighbors[src]:
                if dst not in factor:
                    tree.add(i)
                    factor[dst] = odds[i] / factor[src]
                    stack.append(dst)
    chords = set(range(len(edges))) - tree
    consistent = all(
        factor["u", edges[i][0]] * factor["q", edges[i][1]] == odds[i] for i in chords
    )
    return components, chords, consistent


def rank(matrix):
    a = [list(row) for row in matrix]
    n = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(n, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[n], a[pivot] = a[pivot], a[n]
        for i in range(n + 1, len(a)):
            scale = a[i][col] / a[n][col]
            a[i] = [y - scale * x for x, y in zip(a[n], a[i], strict=True)]
        n += 1
    return n


def contracted_graphs():
    universe = list(product(range(3), repeat=2))
    graphs = chord_tests = 0
    for mask in range(1, 1 << 9):
        edges = [e for i, e in enumerate(universe) if (mask >> i) & 1]
        if any(len(set(v)) < 3 for v in zip(*edges, strict=True)):
            continue
        odds = [F((u + 2) * (q + 1), 6) for u, q in edges]
        components, chords, ok = support(edges, odds)
        assert ok and len(chords) == len(edges) - 6 + components
        for i in chords:
            changed = odds.copy()
            changed[i] *= 2
            assert not support(edges, changed)[2]
            chord_tests += 1
        w = [[F(0)] * 3 for _ in range(3)]
        for u, q in edges:
            m = F(q + 1, q + 3)
            w[u][q] = (1 + 3 * u + q) * m * (1 - m)
        cols = list(map(sum, zip(*w, strict=True)))
        l = [
            [
                int(u == v) * sum(w[u])
                - sum(w[u][q] * w[v][q] / cols[q] for q in range(3))
                for v in range(3)
            ]
            for u in range(3)
        ]
        assert rank(l) == 3 - components and all(sum(row) == 0 for row in l)
        for h in ((1, 2, 5), (3, -1, 0), (0, 1, 0), (1, 1, 1)):
            mean = [sum(w[u][q] * h[u] for u in range(3)) / cols[q] for q in range(3)]
            energy = sum(w[u][q] * (h[u] - mean[q]) ** 2 for u, q in edges)
            assert (
                energy == sum(h[u] * h[v] * l[u][v] for u, v in universe)
                and energy >= 0
            )
        graphs += 1
    return graphs, chord_tests


def checkerboards():
    # Balanced two-by-two log loss is minimized by zero offsets for every additive model.
    p = F(3, 4)
    for a, b, c, d in product((F(1, 2), F(1), F(2)), repeat=4):
        likelihood = F(1)
        for i, j in product(range(2), repeat=2):
            odds = (a, b)[i] * (c, d)[j]
            m = odds / (1 + odds)
            hits = 3 if i == j else 1
            likelihood *= m**hits * (1 - m) ** (4 - hits)
        assert likelihood <= F(1, 2) ** 16
    for n in range(1, 8):
        edges = list(product(range(2 * n), repeat=2))
        lam = p / (1 - p)
        truth = [lam if (u < n) == (q < n) else 1 / lam for u, q in edges]
        cells = [
            [(u, q), (u + n, q), (u, q + n), (u + n, q + n)]
            for u, q in product(range(n), repeat=2)
        ]
        assert sorted(cell for cycle in cells for cell in cycle) == edges
        for cycle in cells:
            assert not support(cycle, [truth[edges.index(e)] for e in cycle])[2]
        kept = [i for i, (u, q) in enumerate(edges) if u < n or q < n]
        assert (
            len(kept) == 3 * n * n
            and support([edges[i] for i in kept], [truth[i] for i in kept])[2]
        )
        if n == 2:
            for k in range(n * n):
                for exceptions in combinations(range(len(edges)), k):
                    allowed = [i for i in range(len(edges)) if i not in exceptions]
                    assert not support(
                        [edges[i] for i in allowed], [truth[i] for i in allowed]
                    )[2]


def checkerboard_loss():
    # Sixteen equiprobable raw pairs, four empirical outcomes per pair.
    # Each cell's likelihood relative to truth is rational. The optimal free
    # exceptions replace the k smallest likelihood ratios with one.
    levels = (F(1, 3), F(1), F(3))
    ratios = {}
    for a, b, same in product(levels, levels, (False, True)):
        m = a * b / (1 + a * b)
        hits = 3 if same else 1
        r = F(hits, 4)
        ratios[a, b, same] = (m / r) ** hits * ((1 - m) / (1 - r)) ** (4 - hits)
    thresholds = [F(27, 16) ** ((4 - k) * (8 + k)) for k in range(4)]
    for factors in product(levels, repeat=8):
        gains = sorted(
            ratios[factors[u], factors[4 + q], (u < 2) == (q < 2)]
            for u, q in product(range(4), repeat=2)
        )
        likelihood = prod(gains)
        for k, threshold in enumerate(thresholds):
            assert likelihood**2 * threshold <= 1
            likelihood /= gains[k]
    return len(levels) ** 8 * len(thresholds)


def replication():
    """Compare every small quantized additive fit with independently priced cell fits."""
    types_u = (0, 1, 1)
    types_q = (0, 0, 1)
    levels = (F(1, 2), F(1), F(2))
    for tariff in (F(1), F(3, 2), F(5), F(100)):

        def best(rows, cols, coarse, tariff=tariff):
            best_score = F(0)
            for row_par in product(levels, repeat=len(rows)):
                for col_par in product(levels, repeat=len(cols)):
                    score = F(1)
                    for u, i in enumerate(rows):
                        for q, j in enumerate(cols):
                            a = row_par[u] * col_par[q]
                            m = a / (1 + a)
                            k = 3 if i == j else 1
                            # Integer observed counts and nonuniform tariffs test both summands.
                            repeats = 1 + i + 2 * j
                            raw = (m**k * (1 - m) ** (4 - k)) ** repeats
                            truth = F(k, 4)
                            patched = (
                                truth**k * (1 - truth) ** (4 - k)
                            ) ** repeats / tariff ** (1 + i * j)
                            copies = (
                                types_u.count(i) * types_q.count(j) if coarse else 1
                            )
                            score *= max(raw, patched) ** copies
                    best_score = max(best_score, score)
            return best_score

        assert best(range(2), range(2), True) == best(types_u, types_q, False)
    # At n=2 the nonproduct counterexample has d=log(27/16)/4 and bad-cell KL=log(7).
    # exp(x) >= 1+x and log(x) >= (x-1)/x for x >= 1.
    assert F(27 - 16, 4 * 27) > F(1, 16)
    assert (1 + F(4) + F(4) ** 2 / 2) > 7
    assert F(21) ** 3 * F(7, 27) == 7**4


def text_normalization(data):
    receipt = json.loads(
        Path(__file__).with_name("text_nested_class_result.json").read_text()
    )
    rows, outputs, reference, _, _, _ = frozen(data[:SELECTION_END])
    members = set(map(int, outputs))
    c = rows.common
    qset = np.argsort(c.outgoing, kind="stable")[[0, len(c.outgoing) // 2, -1]]
    checks = 0
    for q in qset:
        counts = rows.count.getrow(q).toarray().ravel().astype(int)
        nums = [
            int(counts[j]) * rows.back_den + 64 * int(v)
            for j, v in enumerate(rows.back_num)
        ]
        total = (int(c.outgoing[q]) + 64) * rows.back_den
        inside = sum(nums[j] for j in members)
        outside = sum(x for j, x in enumerate(nums) if j not in members)
        assert inside + outside == total
        for info in receipt["installations"].values():
            m = restore(info)
            n, scalar, back, nt, live, res = BASE.unpack_from(
                m.pack(rows, outputs), len(rows.base)
            )
            assert (n, nt, live, res) == (len(members), len(m.tables), m.live(), 0)
            sparse_mass = int(counts[outputs].sum()) * rows.back_den + 64 * back
            assert sparse_mass == inside
            choices = [
                {F(float(MULTIPLIERS[i])) for i in set(t.codes) | {NEUTRAL}}
                for t in m.tables
            ]
            for mult in {F(scalar, UNIT) * prod(v) for v in product(*choices)}:
                a, b = mult.numerator, mult.denominator
                assert a * inside + b * outside == b * total + (a - b) * sparse_mass
                checks += 1
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = c.observe(ids, REPORT_START, END)
    inside = np.isin(np.arange(c.vocab), outputs)
    previous = Gate(None, outputs, np.array([reference], dtype=np.uint16))
    new = restore(receipt["installations"]["previous"])
    np.testing.assert_allclose(
        previous.gain(rows, obs),
        new.gain(obs, rows.apply(inside)[obs.query], inside[obs.target]),
        rtol=0,
        atol=1e-12,
    )
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    print("covering 3x3 supports and perturbed chords", contracted_graphs())
    checkerboards()
    print("rational checkerboard loss bounds", checkerboard_loss())
    replication()
    print("heterogeneous replicated odds and four tariff schedules agree exactly")
    print(
        "checkerboard constructions through 14x14 and all 697 deletion sets below threshold on 4x4"
    )
    if args.text:
        from threadpoolctl import threadpool_limits

        with threadpool_limits(limits=1):
            print(
                "exact full-vocabulary query and odds checks",
                text_normalization(load_data(args.data_dir)),
            )
