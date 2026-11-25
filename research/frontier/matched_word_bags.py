"""Recover ordinary word predictions when only matched bag histograms are disclosed."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
from text_aggregate import (
    FIT_END,
    FIT_SHA,
    FIT_START,
    HISTORY,
    TAU,
    K,
    flat_score,
    install,
    stochastic,
    tables,
    tokens,
    vocabulary,
)
from threadpoolctl import threadpool_limits

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "matched_word_bags_fits.json"
SIZES = (1, 4, 16, 64, 256, 1024, 4096, 16384)
SEEDS = (173, 419, 773)
REPORTS = (
    (
        "train_source",
        11065536,
        "6a5ba10e3d734d15ee7afc161d0e9bba5671bc07fa71c4f9ea09e36dc0976302",
    ),
    (
        "reporting_source",
        327680,
        "48c8f46c59996036aac2fdd76d06e5439ddc32898b25b3b11c43c8b8809fc4b2",
    ),
)


def histograms(values, size):
    ids = np.repeat(np.arange(len(values) // size), size)
    return (
        np.bincount(ids * K + values, minlength=len(values) // size * K)
        .reshape(-1, K)
        .astype(np.uint16)
    )


def cross_counts(left, right):
    result = np.zeros((K, K))
    for start in range(0, len(left), 8192):
        left_chunk = left[start : start + 8192].astype(float)
        right_chunk = (
            left_chunk if left is right else right[start : start + 8192].astype(float)
        )
        result += left_chunk.T @ right_chunk
    return result


def fitted(dd, dy, xcount, ycount, b):
    n = xcount.sum()
    groups = n // b
    pi, nu = xcount / n, ycount / n
    u = (ycount + 0.5) / (n + K / 2)
    centered_xx = dd - groups * b**2 * np.outer(pi, pi)
    centered_xy = dy - groups * b**2 * np.outer(pi, nu)
    joint = np.outer(pi, nu) + (n - 1) / (int(n) * int(n - b)) * centered_xy
    moment = stochastic(np.maximum(joint, 0), u)
    moment = stochastic((groups * pi)[:, None] * moment + TAU * u, u)
    delta = np.linalg.solve(centered_xx / b + TAU * np.eye(K), centered_xy / b)
    regression = stochastic(np.maximum(nu + delta - pi @ delta, 0), u)
    eigen = np.linalg.eigvalsh(centered_xx / n)
    return (install(moment), install(regression)), {
        "design_rank": int(np.count_nonzero(eigen > 1e-10)),
        "largest_design_eigenvalue": float(eigen[-1]),
        "smallest_positive_design_eigenvalue": float(
            min(x for x in eigen if x > 1e-10)
        ),
        "negative_moment_mass": float(-joint[joint < 0].sum()),
    }


def fit_all(directory):
    words = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, _ = vocabulary(words[:HISTORY])
    coded = classes[words[FIT_START - 1 : FIT_END]]
    d, y = coded[:-1], coded[1:]
    n = len(d)
    xcount = np.bincount(d, minlength=K)
    ycount = np.bincount(y, minlength=K)
    pair = tables(d, y)
    u = (ycount + 0.5) / (n + K / 2)
    packets = []
    identifiers = {}

    def register(packet):
        if packet not in identifiers:
            identifiers[packet] = len(packets)
            packets.append(packet)
        return identifiers[packet]

    def record(name, seed, size, xx, xy):
        heads, diag = fitted(xx, xy, xcount, ycount, size)
        return {
            "construction": name,
            "seed": seed,
            "covariance": register(heads[0]),
            "regression": register(heads[1]),
            **diag,
        }

    marginal = register(install(np.tile(u, (K, 1))))
    direct = register(install(stochastic(pair + TAU * u, u)))
    conditions = []
    perm = {seed: np.random.default_rng([seed, 6311]).permutation(n) for seed in SEEDS}
    for b in SIZES:
        g = n // b
        rows = []

        if b == 1:
            rows.append(record("contiguous", None, b, np.diag(xcount), pair))
        else:
            cx, cy = histograms(d, b), histograms(y, b)
            rows.append(
                record(
                    "contiguous", None, b, cross_counts(cx, cx), cross_counts(cx, cy)
                )
            )
        for seed in SEEDS:
            idx = perm[seed]
            shuffle = np.random.default_rng([seed, b, 6312]).permutation(g)
            if b == 1:
                rows.append(record("matched", seed, b, np.diag(xcount), pair))
                rows.append(
                    record(
                        "shuffled",
                        seed,
                        b,
                        np.diag(xcount),
                        tables(d[idx], y[idx][shuffle]),
                    )
                )
            else:
                cx, cy = histograms(d[idx], b), histograms(y[idx], b)
                xx = cross_counts(cx, cx)
                rows.append(record("matched", seed, b, xx, cross_counts(cx, cy)))
                rows.append(
                    record("shuffled", seed, b, xx, cross_counts(cx, cy[shuffle]))
                )
        capacity = comb(b + K - 1, K - 1)
        conditions.append(
            {
                "size": b,
                "groups": g,
                "raw_collector_labels": 2 * n,
                "raw_class_bits": 2 * n * (K - 1).bit_length(),
                "enumerative_histogram_bits": 2 * g * (capacity - 1).bit_length(),
                "conditions": rows,
            }
        )
    return {
        "registration": "fff0f7a",
        "fit_prefix": FIT_SHA,
        "class_names": names.tolist(),
        "marginal_packet": marginal,
        "direct_packet": direct,
        "conditions": conditions,
        "packets": packets,
    }


def score_all(directory):
    receipt = json.loads(FROZEN.read_text())
    train = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, lexical = vocabulary(train[:HISTORY])
    assert names.tolist() == receipt["class_names"]
    within = lexical / np.bincount(classes, weights=lexical, minlength=K)[classes]
    out = []
    for role, start, digest in REPORTS:
        words = tokens(role, start + 65536, digest, directory)[start - 1 :]
        d, y = classes[words[:-1]], classes[words[1:]]
        lexical_log = np.log(within[words[1:]])
        scores = [
            flat_score(p, d, y, lexical_log, classes, within)
            for p in receipt["packets"]
        ]
        out.append(
            {
                "file": role,
                "start": start,
                "prefix_sha256": digest,
                "word_targets": len(y),
                "packet_scores": scores,
            }
        )
    return {"reports": out}


def partitions(items, b):
    if not items:
        yield ()
        return
    for tail in combinations(items[1:], b - 1):
        group = (items[0], *tail)
        rest = tuple(x for x in items if x not in group)
        for more in partitions(rest, b):
            yield (group, *more)


def variance(sequence):
    return (
        sum(x * x for x in sequence) / len(sequence)
        - (sum(sequence) / len(sequence)) ** 2
    )


def exact_check():
    sign_cases = 0
    for c in (F(0), F(1, 4), F(-1, 2), F(3, 4)):
        joint = {(0, 0): F(1)}
        for b in range(1, 9):
            new = {}
            for (x, y), value in joint.items():
                for dx in (0, 1):
                    for dy in (0, 1):
                        key = (x + dx, y + dy)
                        new[key] = (
                            new.get(key, 0)
                            + value * (1 + c * (2 * dx - 1) * (2 * dy - 1)) / 4
                        )
            joint = new
            chi = (
                sum(
                    p * p / F(comb(b, x) * comb(b, y), 4**b)
                    for (x, y), p in joint.items()
                )
                - 1
            )
            assert chi == sum(c ** (2 * j) for j in range(1, b + 1))
            moments = [
                sum(
                    p * F((2 * x - b) * (2 * y - b), b) ** k
                    for (x, y), p in joint.items()
                )
                for k in (1, 2)
            ]
            assert moments[0] == c and moments[1] - c * c == 1 + (1 - F(2, b)) * c * c
            sign_cases += 1
    instances = partition_count = 0
    for n, sizes in ((4, (1, 2)), (6, (1, 2, 3)), (8, (1, 2, 4))):
        for ordering in (
            list(range(n)),
            [int(i % 3 == 0) for i in range(n)],
            [i % 2 for i in range(n)],
        ):
            x = [F(i % 2) - F(1, 2) for i in range(n)]
            y = [F(v) - F(sum(ordering), n) for v in ordering]
            c = sum(a * b for a, b in zip(x, y)) / n
            h = {
                (i, j): x[i] * y[j] + x[j] * y[i] for i, j in combinations(range(n), 2)
            }
            degrees = [sum(v for edge, v in h.items() if i in edge) for i in range(n)]
            total = sum(degrees) / (2 * (n - 1))
            a = [(deg - total) / (n - 2) for deg in degrees]
            resid = sum((v - a[i] - a[j]) ** 2 for (i, j), v in h.items())
            for b in sizes:
                estimates = []
                for groups in partitions(tuple(range(n)), b):
                    cross = sum(
                        sum(x[i] for i in group) * sum(y[i] for i in group)
                        for group in groups
                    )
                    estimates.append(F(n - 1, n * (n - b)) * cross)
                assert sum(estimates) / len(estimates) == c
                assert (
                    variance(estimates)
                    == F((n - 1) * (b - 1), n * n * (n - b) * (n - 3)) * resid
                )
                partition_count += len(estimates)
                instances += 1
    return {
        "exact_sign_bag_laws": sign_cases,
        "fixed_tape_mean_variance_cases": instances,
        "partition_evaluations": partition_count,
    }


def serialize(result):
    if "packets" in result:
        header = {k: v for k, v in result.items() if k not in ("conditions", "packets")}
        return (
            json.dumps(header)[:-1]
            + ',\n"conditions": [\n'
            + ",\n".join(json.dumps(x) for x in result["conditions"])
            + '],\n"packets": [\n'
            + ",\n".join(json.dumps(x) for x in result["packets"])
            + "]}\n"
        )
    if "reports" in result:
        items = []
        for report in result["reports"]:
            head = {k: v for k, v in report.items() if k != "packet_scores"}
            items.append(
                json.dumps(head)[:-1]
                + ',\n"packet_scores": [\n'
                + ",\n".join(json.dumps(v) for v in report["packet_scores"])
                + "]}"
            )
        return '{"reports": [\n' + ",\n".join(items) + "]}\n"
    return json.dumps(result, indent=2) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["fit", "score", "check"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        if args.operation == "fit":
            result = fit_all(args.data_dir)
        elif args.operation == "score":
            result = score_all(args.data_dir)
        else:
            result = exact_check()
    encoded = serialize(result)
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
