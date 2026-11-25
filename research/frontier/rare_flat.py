"""Learn the causal toggle program that predicts an ordinary rare binary token."""

import argparse
import json
import subprocess
import sys
from collections import deque
from decimal import Decimal, localcontext
from fractions import Fraction
from io import BytesIO
from itertools import combinations, pairwise, product
from math import comb, log
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
from positive_comparison import SOURCE, categorical_program

Q16 = 65536
ETA = 1 / 8
BUDGETS = (32, 64, 128, 256, 512)


def reduce_row(x, basis):
    for pivot in sorted(basis, reverse=True):
        if x & (1 << pivot):
            x ^= basis[pivot]
    return x


def insert(x, basis):
    x = reduce_row(x, basis)
    if x:
        basis[x.bit_length() - 1] = x
    return bool(x)


def checks(basis, n):
    rows = []
    for free in range(n):
        if free in basis:
            continue
        v = 1 << free
        for pivot in sorted(basis):
            if (v & basis[pivot]).bit_count() % 2:
                v ^= 1 << pivot
        rows.append(v)
    return rows


def syndrome(rows, x):
    return sum(((w & x).bit_count() % 2) << j for j, w in enumerate(rows))


def planted(seed, n, r):
    rng = np.random.default_rng([seed, n, r, 8421])
    basis = {}
    rows = []
    while len(rows) < r:
        draw = int(rng.integers(1 << n))
        if insert(draw, basis):
            rows.append(draw)
    return rows, int(rng.integers(1 << r))


def clean_fit(seed, n, r):
    rows, offset = planted(seed, n, r)
    rng = np.random.default_rng([seed, n, r, 8422])
    basis = {}
    origin = None
    labels = positives = streak = 0
    while streak < 8:
        for raw in rng.integers(1 << n, size=256):
            x = int(raw)
            labels += 1
            if syndrome(rows, x) != offset:
                continue
            positives += 1
            if origin is None:
                origin = x
            elif insert(x ^ origin, basis):
                streak = 0
            else:
                streak += 1
            if streak == 8:
                break
    learned = checks(basis, n)
    target = syndrome(learned, origin)
    exact = all(
        (syndrome(rows, x) == offset) == (syndrome(learned, x) == target)
        for x in range(1 << n)
    )
    return {
        "seed": seed,
        "n": n,
        "r": r,
        "learned_r": len(learned),
        "labels": labels,
        "positives": positives,
        "exact": exact,
        "checks": learned,
        "target": target,
    }


def points(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def cosets(space, size):
    members = list(points(space))
    remaining = (1 << size) - 1
    while remaining:
        shift = (remaining & -remaining).bit_length() - 1
        group = sum(1 << (x ^ shift) for x in members)
        yield group
        remaining ^= group


def catalogue(n):
    size = 1 << n
    linear = {1}
    masks, sizes = [0], [0]
    while linear:
        larger = set()
        for subspace in sorted(linear):
            for coset in cosets(subspace, size):
                masks.append(coset)
                sizes.append(coset.bit_count())
                if coset != subspace:
                    larger.add(coset | subspace)
        linear = larger
    width = (size + 7) // 8
    buf = b"".join(q.to_bytes(width, "little") for q in masks)
    matrix = np.unpackbits(
        np.frombuffer(buf, dtype=np.uint8).reshape(-1, width),
        axis=1,
        count=size,
        bitorder="little",
    )
    sizes = np.array(sizes)
    support, counts = np.unique(sizes, return_counts=True)
    log_prior = np.empty(len(sizes))
    for k, count in zip(support, counts, strict=True):
        log_prior[sizes == k] = -log(len(counts) * count)
    return masks, matrix.astype(float), log_prior, support


def flat_posterior(catalog, scores):
    masks, matrix, log_prior, _ = catalog
    logs = matrix @ scores + log_prior
    top = int(np.argmax(logs))
    scale = logs[top]
    weights = np.exp(logs - scale)
    mass = weights.sum()
    return (weights @ matrix) / mass, scale + log(mass), masks[top]


def subset_posterior(scores, support):
    """Elementary symmetric polynomials give the partition function at each set size."""
    size = len(scores)
    forward = np.full((size + 1, size + 1), -np.inf)
    backward = forward.copy()
    forward[0, 0] = backward[size, 0] = 0.0
    for j in range(size):
        forward[j + 1] = forward[j]
        forward[j + 1, 1:] = np.logaddexp(forward[j, 1:], scores[j] + forward[j, :-1])
    for j in reversed(range(size)):
        backward[j] = backward[j + 1]
        backward[j, 1:] = np.logaddexp(
            backward[j + 1, 1:], scores[j] + backward[j + 1, :-1]
        )
    penalty = np.array([log(comb(size, int(k))) + log(len(support)) for k in support])
    size_logs = forward[-1, support] - penalty
    log_z = np.logaddexp.reduce(size_logs)
    size_prob = np.exp(size_logs - log_z)
    probability = np.zeros(size)
    for k, prior_mass in zip(support, size_prob, strict=True):
        if k == 0:
            continue
        for j in range(size):
            omit = np.logaddexp.reduce(forward[j, :k] + backward[j + 1, k - 1 :: -1])
            probability[j] += prior_mass * np.exp(
                min(0.0, scores[j] + omit - forward[-1, k])
            )
    order = np.argsort(-scores, kind="stable")
    sums = np.r_[0.0, np.cumsum(scores[order])]
    which = int(support[np.argmax(sums[support] - penalty)])
    best = sum(1 << int(i) for i in order[:which])
    return probability, log_z, best


def episode(rng, n, truth):
    raw = list(map(int, rng.integers(2, size=n)))
    x = sum(bit << j for j, bit in enumerate(raw))
    while rng.integers(2):
        j = int(rng.integers(n))
        raw.append(j + 2)
        x ^= 1 << j
    raw.append(n + 2)
    raw.append(((truth >> x) & 1) ^ int(rng.random() < ETA))
    return raw


def parse(raw, n):
    x = sum(bit << j for j, bit in enumerate(raw[:n]))
    for toggle in raw[n:-2]:
        x ^= 1 << (toggle - 2)
    assert raw[-2] == n + 2
    return x, raw[-1]


def query_units(p, vocab):
    # Assign the binary tilt with one unit reserved for every raw symbol.
    capacity = Q16 - vocab
    positive = 1 + np.floor(capacity * np.clip(p, 0, 1) + 0.5).astype(int)
    return 2 + capacity - positive, positive


def risk(prob, target, vocab):
    q0, q1 = query_units(prob, vocab)
    return float(-np.mean(target * np.log(q1 / Q16) + (1 - target) * np.log(q0 / Q16)))


def noisy_runs(n=6):
    catalog = catalogue(n)
    size = 1 << n
    result = []
    bit_q = np.array(release((0, 0), n)) / Q16
    toggle_q = np.array(release((n, 0), n)) / Q16
    bit_loss = -np.mean(np.log(bit_q[:2]))
    toggle_loss = -0.5 * (np.log(toggle_q[-1]) + np.mean(np.log(toggle_q[2:-1])))
    for seed, r, kind in product(range(64, 80), (2, 3), (0, 1)):
        if kind == 0:
            rows, offset = planted(seed, n, r)
            mask = sum(1 << x for x in range(size) if syndrome(rows, x) == offset)
        else:
            rng = np.random.default_rng([seed, n, r, kind, 8421])
            mask = sum(
                1 << int(x) for x in rng.choice(size, size=size >> r, replace=False)
            )
        truth = np.array([(mask >> i) & 1 for i in range(size)])
        target = ETA + (1 - 2 * ETA) * truth
        floor = risk(target.mean(), target, n + 3)
        rng = np.random.default_rng([seed, n, r, kind, 8423])
        evidence = np.zeros(size)
        tokens = 0
        for step in range(1, BUDGETS[-1] + 1):
            raw = episode(rng, n, mask)
            x, y = parse(raw, n)
            tokens += len(raw)
            evidence[x] += 2 * y - 1
            if step not in BUDGETS:
                continue
            scores = evidence * log((1 - ETA) / ETA)
            flat, fz, best = flat_posterior(catalog, scores)
            subset, sz, s_best = subset_posterior(scores, catalog[3])
            odds = float(np.exp(-np.logaddexp(0.0, sz - fz)))
            mix = odds * flat + (1 - odds) * subset
            hard = np.array([(best >> i) & 1 for i in range(size)])
            models = {"flat": flat, "subset": subset, "evidence_mix": mix, "hard": hard}
            gains = {
                k: floor - risk(ETA + (1 - 2 * ETA) * v, target, n + 3)
                for k, v in models.items()
            }
            result.append(
                {
                    "seed": seed,
                    "n": n,
                    "r": r,
                    "source": ("flat", "subset")[kind],
                    "answers": step,
                    "raw_tokens": tokens,
                    "flat_family_probability": odds,
                    "best_flat": format(best, "016x"),
                    "truth": format(mask, "016x"),
                    "correct_flat": best == mask,
                    "correct_lookup": s_best == mask,
                    "query_gain": gains,
                    "full_token_gain": {k: g / (n + 3) for k, g in gains.items()},
                    "full_token_marginal_loss": (n * bit_loss + 2 * toggle_loss + floor)
                    / (n + 3),
                    "oracle_query_gain": floor - risk(target, target, n + 3),
                }
            )
    return result


def program(mask, n):
    if mask == 0:
        return [], None
    origin, *others = points(mask)
    basis = {}
    for x in others:
        insert(x ^ origin, basis)
    rows = checks(basis, n)
    target = syndrome(rows, origin)
    assert all(
        ((mask >> x) & 1) == (syndrome(rows, x) == target) for x in range(1 << n)
    )
    return rows, target


def advance(state, symbol, n, moves, target):
    phase, z = state
    if phase < n and symbol < 2:
        return phase + 1, z ^ (moves[phase] if symbol else 0)
    if phase == n:
        if symbol == n + 2:
            return n + 1, int(z == target)
        if 2 <= symbol < n + 2:
            return n, z ^ moves[symbol - 2]
    return 0, 0


def release(state, n):
    phase, z = state
    vocab = n + 3
    if phase == n:
        probs = np.r_[0, 0, np.full(n, 1 / (2 * n)), 0.5]
        desired = (Q16 - vocab) * probs
        allocation = np.floor(desired).astype(int)
        remaining = Q16 - vocab - allocation.sum()
        order = np.argsort(-(desired - allocation), kind="stable")
        allocation[order[:remaining]] += 1
        return tuple(map(int, 1 + allocation))
    p = ETA + (1 - 2 * ETA) * z if phase == n + 1 else 0.5
    a, b = query_units(p, vocab)
    return int(a), int(b), *((1,) * (vocab - 2))


def check_memory():
    """Compare the analytic curve with every set partition of up to eight hidden values."""

    def partitions(sizes, todo):
        if not todo:
            yield tuple(sizes)
            return
        for j in range(len(sizes)):
            sizes[j] += 1
            yield from partitions(sizes, todo - 1)
            sizes[j] -= 1
        sizes.append(1)
        yield from partitions(sizes, todo - 1)
        sizes.pop()

    def entropy(p):
        return -sum(x * x.ln() for x in (p, 1 - p) if x)

    comparisons = 0
    with localcontext() as decimal_context:
        decimal_context.prec = 60
        for eta in (Decimal(0), Decimal(1) / 8, Decimal(1) / 3):
            kappa = 1 - 2 * eta
            for q in (2, 4, 8):
                cell = [Decimal(0)] + [
                    s * s * (entropy(eta + kappa / s) - entropy(eta))
                    for s in range(1, q + 1)
                ]
                optimum = {}
                for sizes in partitions([], q):
                    m = len(sizes)
                    cost = sum(cell[s] for s in sizes) / (q * q)
                    optimum[m] = min(optimum.get(m, cost), cost)
                    comparisons += 1
                for m, cost in optimum.items():
                    low, extra = divmod(q, m)
                    balanced = (
                        (m - extra) * cell[low]
                        + (extra * cell[low + 1] if extra else 0)
                    ) / (q * q)
                    assert abs(cost - balanced) < Decimal("1e-55")
        eta = Decimal(1) / 8
        r, q = 8, 256
        kappa = 1 - 2 * eta
        full_gain = entropy(eta + kappa / q) - entropy(eta)
        curve = [
            full_gain - (entropy(eta + kappa * (1 << b) / q) - entropy(eta)) / (1 << b)
            for b in range(r + 1)
        ]
        differences = [y - x for x, y in pairwise(curve)]
        assert all(y > x for x, y in pairwise(differences))
    return {
        "partition_noise_comparisons": comparisons,
        "q256_noise_one_eighth_gains": list(map(float, curve)),
    }


def exact_check():
    catalog = catalogue(3)
    masks, matrix, prior, sizes = catalog
    assert len(set(masks)) == len(masks) == 52
    for mask in masks:
        rows, target = program(mask, 3)
        moves = [syndrome(rows, 1 << j) for j in range(3)]
        for x in range(8):
            for length in range(4):
                for path in product(range(3), repeat=length):
                    state = 3, syndrome(rows, x)
                    y = x
                    for j in path:
                        state = advance(state, 2 + j, 3, moves, target)
                        y ^= 1 << j
                    assert advance(state, 5, 3, moves, target)[1] == ((mask >> y) & 1)
    scores = np.array([-4, 0, 2, 0, 5, -1, 1, -5]) * log(7)
    weighted = np.exp(matrix @ scores + prior)
    fprob, fz, _ = flat_posterior(catalog, scores)
    np.testing.assert_allclose(np.exp(fz), weighted.sum())
    np.testing.assert_allclose(fprob, weighted @ matrix / weighted.sum())
    probs = np.zeros(8)
    total = 0
    for k in sizes:
        for members in combinations(range(8), k):
            mass = np.exp(sum(scores[j] for j in members)) / (len(sizes) * comb(8, k))
            total += mass
            probs[list(members)] += mass
    pred, sz, _ = subset_posterior(scores, sizes)
    np.testing.assert_allclose(np.exp(sz), total)
    np.testing.assert_allclose(pred, probs / total)
    all_sizes = [int((matrix.sum(axis=1) == k).sum()) for k in sizes]
    return {
        "small_affine_counts_including_empty": all_sizes,
        "complete_short_toggle_checks": len(masks) * 8 * 40,
        "direct_subset_posterior_masks": sum(comb(8, k) for k in sizes),
        **check_memory(),
    }


def r4_audit():
    here = Path(__file__).resolve().parent
    data = json.loads((here / "rare_flat_result.json").read_text())
    installed = {int(v["best_flat"], 16) for v in data["noisy"]}
    transfer_checks = 0
    for candidate in installed:
        rows, target = program(candidate, 6)
        moves = [syndrome(rows, 1 << j) for j in range(6)]
        for x in range(64):
            state = 6, syndrome(rows, x)
            assert advance(state, 8, 6, moves, target)[1] == (candidate >> x) & 1
            for j in range(6):
                assert advance(state, j + 2, 6, moves, target) == (
                    6,
                    syndrome(rows, x ^ (1 << j)),
                )
                transfer_checks += 1
    fitted = next(
        v
        for v in data["noisy"]
        if v["r"] == 2 and v["source"] == "flat" and v["correct_flat"]
    )
    n = fitted["n"]
    mask = int(fitted["best_flat"], 16)
    rows, target = program(mask, n)
    moves = [syndrome(rows, 1 << j) for j in range(n)]
    vocab = tuple(map(str, range(n + 3)))
    states, indices, queue = [(0, 0)], {(0, 0): 0}, deque([(0, 0)])
    transitions, releases = [], []
    while queue:
        s = queue.popleft()
        out = []
        for a in range(n + 3):
            dest = advance(s, a, n, moves, target)
            if dest not in indices:
                indices[dest] = len(states)
                states.append(dest)
                queue.append(dest)
            out.append(indices[dest])
        transitions.append(out)
        releases.append(release(s, n))
    path = "src/reference_compiler"
    archive = subprocess.check_output(
        ["git", "-C", str(here.parents[1]), "archive", "--format=zip", SOURCE, path]
    )
    with TemporaryDirectory() as tmp:
        with ZipFile(BytesIO(archive)) as files:
            files.extractall(tmp)
        sys.path.insert(0, str(Path(tmp) / path))
        slots = [Fraction(1), *(Fraction(2 * x - 1) for p in releases for x in p)]
        heads = [
            [(i, 1 + i * len(vocab) + a) for i in range(len(states))]
            for a in range(len(vocab))
        ]
        event, start, sizes = categorical_program(vocab, transitions, heads, slots)
        actual, queue = {0: start}, deque([0])
        while queue:
            i = queue.popleft()
            assert actual[i].probabilities == tuple(
                Fraction(x, Q16) for x in releases[i]
            )
            for j, a in enumerate(vocab):
                v = event(a, actual[i].delayed)
                dest = transitions[i][j]
                assert v.probabilities == tuple(
                    Fraction(x, Q16) for x in releases[dest]
                )
                if dest not in actual:
                    actual[dest] = v
                    queue.append(dest)
                assert actual[dest].delayed == v.delayed
    assert len(actual) == len(states)
    return {
        "distinct_installed_flat_programs": len(installed),
        "inductive_atomic_transfers": transfer_checks,
        "learned_masks": rows,
        "offset": target,
        "reachable_control_and_syndrome_states": len(states),
        "complete_resets_and_edges": 1 + len(states) * len(vocab),
        "nodes": sizes["nodes"],
        "delayed_cells": sizes["delayed_cells"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--r4", action="store_true")
    args = parser.parse_args()
    if args.check or args.r4:
        data = json.dumps(exact_check() if args.check else r4_audit(), indent=2) + "\n"
    else:
        clean = [
            clean_fit(seed, 12, r) for seed in range(64, 96) for r in (2, 4, 8, 12)
        ]
        noisy = noisy_runs()
        data = '{"registration":"e80c919","clean":[\n' + ",\n".join(
            json.dumps(v) for v in clean
        )
        data += (
            '],"noisy":[\n'
            + ",\n".join(json.dumps(v, allow_nan=False) for v in noisy)
            + "]}\n"
        )
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
