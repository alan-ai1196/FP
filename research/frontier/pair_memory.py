"""Exact compression after observing an unknown balanced dictionary once."""

import argparse
import json
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
from math import gcd, prod
from pathlib import Path

import numpy as np
from pair_dictionary import KAPPA, representatives

REGISTRATION = "59b8251"


def modular_rank(a, prime=1009):
    a = a.copy() % prime
    pivot = 0
    for col in range(a.shape[1]):
        rows = np.flatnonzero(a[pivot:, col])
        if not len(rows):
            continue
        i = pivot + rows[0]
        a[[i, pivot]] = a[[pivot, i]]
        a[pivot] = a[pivot] * pow(int(a[pivot, col]), -1, prime) % prime
        a[pivot + 1 :] = (a[pivot + 1 :] - a[pivot + 1 :, col, None] * a[pivot]) % prime
        pivot += 1
    return pivot


def geometry(d):
    labels = representatives(d)
    k = len(labels)
    edges = list(combinations(range(d), 2))
    e = len(edges)
    products = np.array([labels[:, i] * labels[:, j] for i, j in edges]).T
    incidence = np.zeros((d, e), dtype=np.int64)
    for j, (x, y) in enumerate(edges):
        incidence[[x, y], j] = 1
    u = (d - 1) * products + 1
    cov = u.T @ u
    cd = k * (d - 1) ** 2
    pd = 2 * (d - 1) * (d - 2)
    projection = (
        pd * np.eye(e, dtype=np.int64) - 2 * (d - 1) * (incidence.T @ incidence) + 4
    )
    eigen = F(d * (d - 2), (d - 1) * (d - 3))
    assert np.all(incidence @ u.T == 0)
    assert np.array_equal(
        cov * pd * eigen.denominator, projection * cd * eigen.numerator
    )
    assert np.array_equal((cov @ cov) * eigen.denominator, cd * cov * eigen.numerator)
    rank = modular_rank(cov)
    assert rank == d * (d - 3) // 2
    # Every column is a raw training type. Column zero collects all loops.
    w = np.column_stack((np.full(k, 3 * d, np.int64), 2 * (2 + products)))
    assert np.all(w.sum(axis=1) == 2 * d * d)
    mean = u.T @ w
    assert np.all(mean[:, 0] == 0)
    multiplier = F(d - 1, 2 * d - 3)
    assert np.array_equal(
        mean[:, 1:] * (cd * multiplier.denominator),
        cov * ((d - 1) * w[:, 1:].sum(axis=0) * multiplier.numerator),
    )
    return w, {
        "unordered_edges": e,
        "rank": rank,
        "nonzero_eigenvalue": str(eigen),
        "posterior_columns_checked": e + 1,
    }


def information(joint):
    row = joint.sum(axis=1)
    law = joint / row[:, None]
    marginal = joint.sum(axis=0) / joint.sum()
    p = row / row.sum()
    return float(np.sum(p[:, None] * law * np.log(law / marginal))), float(
        np.sum(p[:, None] * (law - marginal) ** 2)
    )


def reduced_joint(w, n):
    if n == 1:
        train = w
    else:
        groups = {}
        for i, j in combinations_with_replacement(range(w.shape[1]), 2):
            mass = w[:, i] * w[:, j]
            key = tuple(mass // np.gcd.reduce(mass))
            if i != j:
                mass = 2 * mass
            if key in groups:
                groups[key] += mass
            else:
                groups[key] = mass.copy()
        train = np.column_stack(list(groups.values()))
    joint = train.T @ w
    return joint // np.gcd.reduce(joint.ravel())


def compressed(joint, mask):
    selected = np.array([bool(mask & (1 << j)) for j in range(len(joint))])
    first = joint[selected].sum(axis=0)
    return np.stack((first, joint.sum(axis=0) - first))


def regular_information(d, degree, terms=24):
    # Rational enclosure for the log gain of a regular graph membership bit.
    # h(z)=(1+z)ln(1+z)-z. Bound the tail by a geometric series.
    q = F(degree, d - 1)
    kappa = F(1, 2)
    x = 1 - (1 + kappa) / d
    p = x * q
    eigen = F(d * (d - 2), (d - 1) * (d - 3))
    shift = 2 * kappa**2 * eigen * (d - 1) / (x * d**3)

    def h(z):
        assert abs(z) < 1
        center = sum((-z) ** m / (m * (m - 1)) for m in range(2, terms + 1))
        error = abs(z) ** (terms + 1) / (terms * (terms + 1) * (1 - abs(z)))
        return center, error

    value, error = F(0), F(0)
    for weight, delta in ((q, shift * (1 - q)), (1 - q, -shift * q)):
        for prior, offset in ((p, delta), (1 - p, -delta)):
            mid, radius = h(offset / prior)
            value += x * weight * prior * mid
            error += x * weight * prior * radius
    return value - error, value + error


def matching_control():
    result = []
    for d in range(4, 25, 2):
        match = regular_information(d, 1)
        cycle = regular_information(d, 2)
        assert match[0] > cycle[1] if d < 20 else cycle[0] > match[1]
        result.append(
            {
                "vocabulary": d,
                "matching_gain": float(sum(match) / 2),
                "cycle_gain": float(sum(cycle) / 2),
                "maximum_rational_enclosure_width": float(
                    max(match[1] - match[0], cycle[1] - cycle[0])
                ),
            }
        )
    return result


def twenty_certificate():
    # A lower curvature bound prices every nonregular degree sequence. Only
    # one real-degree curve per possible number of edges then needs checking.
    d = 20
    edges = d * (d - 1) // 2
    s0 = 1 - F(1, 2 * (d - 1))
    w = 2 * s0 / d**2
    t = F(d * (d - 2), (d - 1) * (d - 3)) / (4 * s0**2)
    g = w * t
    assert t < F(3, 10) and w < F(1, 200) and 1 - w * edges >= F(3, 40)
    # Uniform ratios of the displaced Bernoulli probabilities to their means.
    low_p = 1 - F(3, 10) * F(2, d - 2)
    high_p = 1 + F(3, 10) * (1 + F(2, (d - 1) * (d - 2)))
    assert 3 * g / (1 - w * edges) < F(6, 100)
    curvature_floor = 1 / (high_p * F(106, 100)) - 1 / (2 * low_p * F(94, 100))
    assert curvature_floor > F(1, 6)
    candidates = []
    for k in range(1, edges + 1):
        degree = F(2 * k, d)
        lo, hi = regular_information(d, degree)
        frac = degree - (degree.numerator // degree.denominator)
        penalty = d * frac * (1 - frac) / (3 * k * (d - 2))
        candidates.append((k, degree, 2 * lo / g**2, 2 * hi / g**2 - penalty))
    winner = next(c for c in candidates if c[1] == 2)
    noninteger = max(c[3] for c in candidates if c[1].denominator != 1)
    other = max(c[3] for c in candidates if c[1].denominator == 1 and c[1] != 2)
    assert winner[2] > max(noninteger, other)
    return {
        "edge_counts": len(candidates),
        "certified_degree": int(winner[1]),
        "winning_normalized_gain_lower": float(winner[2]),
        "other_integer_degree_upper": float(other),
        "noninteger_degree_upper": float(noninteger),
        "relative_curvature_difference_lower": float(curvature_floor),
    }


def best_bit(joint):
    n = len(joint)
    # Fix the last history in message zero. Candidate comparisons use exact
    # integers. Graph symmetries often give the same sorted cell counts.
    total = joint.sum(axis=0)
    distinct = {}
    for mask in range(1, 1 << (n - 1)):
        chosen = [j for j in range(n - 1) if mask & (1 << j)]
        first = joint[chosen].sum(axis=0)
        sizes = tuple(sorted((int(first.sum()), int(total.sum() - first.sum()))))
        counts = tuple(sorted(map(int, np.r_[first, total - first])))
        signature = (sizes, counts)
        if signature in distinct:
            distinct[signature][1] += 1
        else:
            distinct[signature] = [mask, 1]
    # A common constant in the mutual information cancels across partitions.
    # Log of this factor is the remaining mutual information times total mass.
    best_num, best_den, example, ties = 0, 1, 0, 0
    powers = {}
    for (sizes, counts), (mask, repeats) in distinct.items():
        for v in (*sizes, *counts):
            if v not in powers:
                powers[v] = v**v
        numerator = prod(powers[v] for v in counts)
        denominator = prod(powers[v] for v in sizes)
        common = gcd(numerator, denominator)
        numerator //= common
        denominator //= common
        difference = numerator * best_den - best_num * denominator
        if difference > 0:
            best_num, best_den, example, ties = numerator, denominator, mask, repeats
        elif difference == 0:
            ties += repeats
    assert sum(x[1] for x in distinct.values()) == (1 << (n - 1)) - 1
    return example, ties, len(distinct)


def evaluate(d):
    w, result = geometry(d)
    if d > 6:
        return result
    horizons = []
    for n in (1, 2):
        joint = reduced_joint(w, n)
        full, full_norm = information(joint)
        info = {
            "training_pairs": n,
            "training_types": len(joint),
            "full_incremental_gain": full,
        }
        if n == 1:
            value, norm = information(compressed(joint, 2))
            info["one_specified_edge_gain"] = value
            info["one_specified_edge_variance_fraction"] = norm / full_norm
        if len(joint) <= 16:
            choice, ties, profiles = best_bit(joint)
            value, norm = information(compressed(joint, choice))
            assert norm / full_norm <= 1 / result["rank"] + 2e-14
            info["best_one_bit"] = {
                "incremental_gain": value,
                "variance_fraction": norm / full_norm,
                "history_mask": choice,
                "optimal_encoders": ties,
                "encoders": (1 << (len(joint) - 1)) - 1,
                "distinct_count_profiles": profiles,
            }
        else:
            # A feasible one-bit encoder selects all histories for which the
            # likelihood of the next occurrence of one prescribed edge rises.
            q = joint[:, 1] / joint.sum(axis=1)
            first = q > joint[:, 1].sum() / joint.sum()
            selected = np.stack((joint[first].sum(axis=0), joint[~first].sum(axis=0)))
            value, norm = information(selected)
            assert norm / full_norm <= 1 / result["rank"] + 2e-14
            info["specified_edge_increase_bit"] = {
                "incremental_gain": value,
                "variance_fraction": norm / full_norm,
            }
        horizons.append(info)
    result["horizons"] = horizons
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "registration": REGISTRATION,
        "contrast": KAPPA,
        "dimensions": {d: evaluate(d) for d in (4, 6, 8, 12)},
        "supplemental_regular_graph_comparison": matching_control(),
        "supplemental_global_twenty_name_certificate": twenty_certificate(),
    }
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
