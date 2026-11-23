"""Exact small two-set NTP problems, physical normalization and a joint-search obstruction."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations, product
from math import prod
from pathlib import Path

import numpy as np
from measure_word_classes import restore
from text import SCALE, ratio_log
from text_addresses import SELECT_END, fit
from text_word_classes import load_data
from word_classes import HEADER, UNIT, ProbabilityRows


def mass(p, mask):
    return sum(v for i, v in enumerate(p) if mask >> i & 1)


def tilt(p, b, r):
    row = [v * (r if (b >> j) & 1 else 1) for j, v in enumerate(p)]
    return tuple(x / sum(row) for x in row)


def check_submodular():
    k = 4
    rows = [(F(1, 2), F(1, 4), F(1, 8), F(1, 8)), (F(1, 8), F(3, 8), F(1, 4), F(1, 4))]
    datasets = [
        [(rows[i % 2], (i * i + j * i + 1) % k) for i in range(1, 7)] for j in range(k)
    ]
    inequalities = 0
    for data, rho in product(datasets, (F(1, 2), F(3, 4), F(3, 2), F(2))):
        gain = []
        for b in range(1 << k):
            g = F(1)
            for p, y in data:
                q = tilt(p, b, rho)
                assert sum(q) == 1
                g *= q[y] / p[y]
            gain.append(g)
        for l, r in product(range(1 << k), repeat=2):
            assert gain[l] * gain[r] <= gain[l | r] * gain[l & r]
            inequalities += 1
    # On a single fixed base, ratio-sorted prefixes include an exact optimum for every tilt.
    for p, rho in product(rows, (F(1, 2), F(2))):
        for counts in product(range(1, 4), repeat=k):

            def gain(mask, p=p, rho=rho, counts=counts):
                ratio = tilt(p, mask, rho)
                return prod(
                    (q / v) ** n for v, q, n in zip(p, ratio, counts, strict=True)
                )

            order = sorted(range(k), key=lambda j: counts[j] / p[j], reverse=rho > 1)
            prefixes = [sum(1 << j for j in order[:i]) for i in range(k + 1)]
            assert max(map(gain, prefixes)) == max(gain(m) for m in range(1 << k))
    return inequalities


def cut_witness():
    v = 4
    edges = list(combinations(range(v), 2))
    graphs = 0
    for mask in range(1, 1 << len(edges)):
        graph = [e for i, e in enumerate(edges) if (mask >> i) & 1]
        smooth = F(1, 1000 * len(graph))
        cuts = []
        gains = []
        for b in range(1 << v):
            size = b.bit_count()
            score = F(1)
            cut = 0
            for i, j in graph:
                x, y = (b >> i) & 1, (b >> j) & 1
                cut += x != y
                s = (1 - smooth) * F(x + y, 2) + smooth * F(size, v)
                den = (1 + 2 * s) ** 4
                # Each of the two earlier history types can buy its own gate.
                score *= max(F(1), 3 ** (3 * x + y) / den) * max(
                    F(1), 3 ** (x + 3 * y) / den
                )
            cuts.append(cut)
            gains.append(score)
        assert all(
            c == max(cuts) for c, g in zip(cuts, gains, strict=True) if g == max(gains)
        )
        graphs += 1
    return graphs


def neutral_trap():
    # The ten rich output labels have eight occurrences each, the other ten have two.
    _, hi = ratio_log(4, 1)
    assert F(8 * hi, 100 * SCALE) < F(3, 23)
    score = F(4) ** 80 / F(5, 2) ** 100
    assert score > 1
    # Exact two-label counterexample to submodularity after profiling the input gate.
    base = (F(1, 2), F(1, 2))
    gains = [
        prod(max(F(1), tilt(base, mask, F(2))[y] / base[y]) for y in range(2))
        for mask in range(4)
    ]
    assert gains == [1, F(4, 3), F(4, 3), 1]
    assert gains[1] * gains[2] > gains[0] * gains[3]
    return score.numerator.bit_length()


def full_text(data):
    root = Path(__file__).resolve().parent
    receipt = json.loads((root / "text_word_classes_result.json").read_text())
    rows = ProbabilityRows(fit(data[:SELECT_END]))
    c = rows.common
    total = 0
    qset = np.argsort(c.outgoing, kind="stable")[[0, len(c.outgoing) // 2, -1]].tolist()
    for q in qset:
        den = int((c.outgoing[q] + 64) * rows.back_den)
        nums = [
            int(c.rows.pairs[q, y]) * rows.back_den + 64 * int(rows.back_num[y])
            for y in range(len(c.counts))
        ]
        assert sum(nums) == den
        for info in receipt["installations"].values():
            m = restore(info)
            if not len(m.outputs):
                continue
            packet = m.install(rows)
            kind, flags, na, nb, scalar, stored = HEADER.unpack_from(
                packet, len(rows.base)
            )
            assert flags == int(m.types is None) + 2 * int(m.current)
            off = len(rows.base) + HEADER.size + 2 * na
            ids = {}
            stride = 2 if kind == 1 else 4
            for i in range(nb):
                j = int.from_bytes(
                    packet[off + stride * i : off + stride * i + 2], "little"
                )
                units = (
                    scalar
                    if stride == 2
                    else int.from_bytes(
                        packet[off + stride * i + 2 : off + stride * i + 4], "little"
                    )
                )
                ids[j] = units
            assert (
                len(packet) == off + nb * stride
                and sum((u - UNIT) * int(rows.back_num[j]) for j, u in ids.items())
                == stored
            )
            norm = sum(n * ids.get(j, UNIT) for j, n in enumerate(nums))
            delta = sum(int(c.rows.pairs[q, j]) * (u - UNIT) for j, u in ids.items())
            assert norm == UNIT * den + rows.back_den * delta + 64 * stored
            assert abs(norm / (UNIT * den) - (1 + rows.apply(m.weights())[q])) < 2e-14
            total += 1
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    print("rational submodularity inequalities", check_submodular())
    print("positive four-vertex graph reductions", cut_witness())
    neutral_trap()
    if args.text:
        from threadpoolctl import threadpool_limits

        with threadpool_limits(limits=1):
            print(
                "exact full-alphabet active normalizations",
                full_text(load_data(args.data_dir)),
            )
