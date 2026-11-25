"""Recover a binary lookup from separate descriptor and noisy outcome tapes."""

import argparse
import json
from itertools import combinations, product
from math import comb
from pathlib import Path

import numpy as np
from outcome_sketch import decompose, gain

NAMES = 32
BUDGETS = (32, 64, 128, 256)


def packed(binary):
    return np.packbits(binary, bitorder="little").tobytes()


def incidence(names, buckets, t, d):
    rows = np.zeros((d, t), dtype=np.uint8)
    np.bitwise_xor.at(rows, (names, buckets), 1)
    return [int.from_bytes(packed(row), "little") for row in rows]


def sender(outcomes, buckets, t):
    rows = np.zeros(t, dtype=np.uint8)
    np.bitwise_xor.at(rows, buckets, outcomes)
    return packed(rows)


def certify(columns, t, h):
    """Index every radius-h error by its residue and its effect on the decoded rule."""
    rank, quotient, pivot_work = decompose(columns, t)
    corrections = {0: 0}
    tested = 1
    if rank != len(columns):
        return None, rank, pivot_work, tested
    units = []
    for j in range(t):
        residue, correction, work = quotient(1 << j)
        pivot_work += work
        tested += 1
        if residue in corrections:
            return None, rank, pivot_work, tested
        corrections[residue] = correction
        units.append((residue, correction))
    if h == 2:
        for (left, x), (right, y) in combinations(units, 2):
            tested += 1
            residue = left ^ right
            if residue in corrections:
                return None, rank, pivot_work, tested
            corrections[residue] = x ^ y
    elif h != 1:
        raise ValueError("This implementation tests one or two errors.")

    def decode(message):
        target, rule, work = quotient(int.from_bytes(message, "little"))
        result = rule ^ corrections[target] if target in corrections else None
        return result, work

    return decode, rank, pivot_work, tested


def bounded_product(left, right, h):
    return np.convolve(left, right)[: h + 1]


def sample_posterior(names, reports, n, d, h):
    """Sum the likelihood over errors outside the sampled positions and all lookup bits."""
    visits = np.bincount(names, minlength=d)
    ones = np.bincount(names, weights=reports, minlength=d).astype(int)
    # The factor for a name has one monomial per possible clean bit.
    factors = []
    for a, b in zip(ones, visits - ones, strict=True):
        factor = np.zeros(h + 1)
        if a <= h:
            factor[a] += 0.5
        if b <= h:
            factor[b] += 0.5
        factors.append(factor)
    one = np.array([1.0, *([0.0] * h)])
    prefix = [one]
    for factor in factors:
        prefix.append(bounded_product(prefix[-1], factor, h))
    outside = np.array([comb(n - len(names), h - i) for i in range(h + 1)])
    total = prefix[-1] @ outside
    if not total:
        raise ValueError("The observations contradict the declared raw noise budget.")
    suffix = one
    answer = np.zeros(d)
    for j in reversed(range(d)):
        others = bounded_product(prefix[j], suffix, h)
        mismatch_if_positive = visits[j] - ones[j]
        if mismatch_if_positive <= h:
            size = h - mismatch_if_positive + 1
            answer[j] = 0.5 * (others[:size] @ outside[mismatch_if_positive:]) / total
        suffix = bounded_product(suffix, factors[j], h)
    return np.clip(answer, 0, 1)


def source(seed, n, h):
    rng = np.random.default_rng([seed, n, h, 8311])
    base = np.tile(np.arange(NAMES), 2 * h + 1)
    names = rng.permutation(np.r_[base, rng.integers(8, size=n - len(base))])
    truth = np.random.default_rng([seed, n, h, 8312]).integers(2, size=NAMES)
    outcomes = truth[names].astype(np.uint8)
    flips = np.random.default_rng([seed, n, h, 8313]).choice(n, size=h, replace=False)
    outcomes[flips] ^= 1
    order = np.random.default_rng([seed, n, h, 8315]).permutation(n)
    return names, truth, outcomes, order


def run():
    rows = []
    for seed, n, h in product(range(32, 64), (1024, 65536), (1, 2)):
        names, truth, outcomes, order = source(seed, n, h)
        for t in BUDGETS:
            rng = np.random.default_rng([seed, n, h, t, 8314])
            buckets = rng.integers(t, size=n, dtype=np.uint16)
            message = sender(outcomes, buckets, t)
            assert 8 * len(message) == t
            columns = incidence(names, buckets, t, NAMES)
            decode, rank, pivot_work, attempts = certify(columns, t, h)
            pred = np.full(NAMES, 0.5)
            rule = None
            if decode:
                rule, extra = decode(message)
                pivot_work += extra
                assert rule is not None
                pred = np.array([(rule >> j) & 1 for j in range(NAMES)])
                assert np.array_equal(pred, truth)
            positions = order[:t]
            sampled = sample_posterior(
                names[positions], outcomes[positions], n, NAMES, h
            )
            seen = np.unique(names[positions])
            clean = np.full(NAMES, 0.5)
            clean[seen] = truth[seen]
            rows.append(
                {
                    "seed": seed,
                    "N": n,
                    "h": h,
                    "bits": t,
                    "public_bucket_bits": n * (t.bit_length() - 1),
                    "reads_per_collector": n,
                    "rank": rank,
                    "radius_syndromes_tested": attempts,
                    "pivot_xors": pivot_work,
                    "installed_le32": None
                    if rule is None
                    else int(rule).to_bytes(4, "little").hex(),
                    "gain": gain(truth, pred),
                    "sample_gain": gain(truth, sampled),
                    "clean_sample_gain": gain(truth, clean),
                    "visited_names": len(seen),
                }
            )
    return rows


def audit():
    # An independent enumerator tests the entire lookup code and all admissible raw flips.
    accepted = rejected = decoded = 0
    for h in (1, 2):
        names = np.repeat(np.arange(2), 2 * h + 1)
        n = len(names)
        for seed in range(18):
            t = n + 2
            buckets = (
                np.arange(n)
                if seed == 0
                else np.random.default_rng(seed).integers(t, size=n)
            )
            columns = incidence(names, buckets, t, 2)
            decode, _, _, _ = certify(columns, t, h)
            distance = min(
                columns[0].bit_count(),
                columns[1].bit_count(),
                (columns[0] ^ columns[1]).bit_count(),
            )
            assert (decode is not None) == (distance > 2 * h)
            if decode is None:
                rejected += 1
                continue
            accepted += 1
            for bits in product((0, 1), repeat=2):
                truth = np.array(bits, dtype=np.uint8)
                for errors in range(h + 1):
                    for locations in combinations(range(n), errors):
                        reports = truth[names].copy()
                        reports[list(locations)] ^= 1
                        rule, _ = decode(sender(reports, buckets, t))
                        assert rule == bits[0] + 2 * bits[1]
                        decoded += 1

    names = np.array([0, 2, 0, 3, 2])
    d, n = 4, 8
    checked = 0
    for h in (1, 2):
        numerators = {}
        counts = {}
        for bits in product((0, 1), repeat=d):
            truth = np.array(bits)
            for locations in combinations(range(n), h):
                flipped = np.isin(np.arange(len(names)), locations).astype(int)
                obs = tuple(truth[names] ^ flipped)
                counts[obs] = counts.get(obs, 0) + 1
                numerators[obs] = numerators.get(obs, np.zeros(d)) + truth
        for obs, count in counts.items():
            expected = numerators[obs] / count
            np.testing.assert_allclose(sample_posterior(names, obs, n, d, h), expected)
            checked += 1

    # Integer walk multiplicities give exact checks of the radial and two-step comparisons.
    ball_tests = 0
    for t in range(2, 8):
        ways = [1, *([0] * ((1 << t) - 1))]
        histories = []
        for step in range(18):
            radial = [ways[(1 << k) - 1] for k in range(t + 1)]
            assert all(v == radial[i.bit_count()] for i, v in enumerate(ways))
            assert all(a >= b for a, b in zip(radial, radial[2:]))
            ball = [
                sum(v for i, v in enumerate(ways) if i.bit_count() <= r)
                for r in range(t + 1)
            ]
            if step >= 2:
                assert all(
                    b <= t * t * a for a, b in zip(histories[-2], ball, strict=True)
                )
                ball_tests += len(ball)
            histories.append(ball)
            ways = [sum(ways[i ^ (1 << j)] for j in range(t)) for i in range(1 << t)]
    return {
        "certified_toy_designs": accepted,
        "rejected_toy_designs": rejected,
        "all_rules_raw_error_patterns_decoded": decoded,
        "exact_sample_posteriors": checked,
        "exact_cube_ball_comparisons": ball_tests,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        data = json.dumps(audit(), indent=2) + "\n"
    else:
        rows = run()
        data = (
            '{"registration":"5ec91ee","rows":[\n'
            + ",\n".join(json.dumps(row, allow_nan=False) for row in rows)
            + "]}\n"
        )
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
