"""Finite audits of an unbounded, shared-state predictive mixture and branch pruning."""

import argparse
import ctypes as c
import json
import os
from contextlib import contextmanager
from fractions import Fraction as F
from itertools import product
from math import comb, factorial, fsum, log, log1p, prod
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from action_cut import step
from causal_state import compile_libraries

HERE = Path(__file__).resolve().parent


@contextmanager
def native():
    with TemporaryDirectory() as directory:
        (path,) = compile_libraries(
            Path(directory), ("address",), HERE / "state_birth.c"
        )
        lib = c.CDLL(str(path))
        lib.birth_tree.argtypes = [
            c.c_int,
            np.ctypeslib.ndpointer(np.uint8, ndim=1, flags="C_CONTIGUOUS"),
            c.c_double,
            c.c_int,
            np.ctypeslib.ndpointer(np.float64, ndim=2, flags="C_CONTIGUOUS"),
            np.ctypeslib.ndpointer(np.uint64, ndim=1, flags="C_CONTIGUOUS"),
        ]
        lib.birth_tree.restype = c.c_int
        try:
            yield lib
        finally:
            if os.name == "nt":
                import _ctypes

                _ctypes.FreeLibrary(lib._handle)


def full(lib, x, beta, neutral=False):
    raw = np.ascontiguousarray(x, dtype=np.uint8)
    assert raw.ndim == 1 and len(raw) > 0 and max(raw) <= 1
    n = len(x)
    joint = np.zeros((n, n))
    sizes = np.zeros(n, dtype=np.uint64)
    if not lib.birth_tree(n, raw, float(beta), int(neutral), joint, sizes):
        raise ArithmeticError("unavailable workspace or too many branches to count")
    return joint, sizes


def partitions(n):
    if n == 1:
        yield (0,)
    else:
        for x in partitions(n - 1):
            for j in range(max(x) + 2):
                yield (*x, j)


def partition_weight(x, path, beta, alphabet=2):
    destinations = {}
    r = max(path) + 1
    heads = [[0] * alphabet for _ in range(r)]
    incoming = [1] + [0] * (r - 1)
    for t, (s, a) in enumerate(zip(path, x, strict=True)):
        heads[s][a] += 1
        if t + 1 < len(x):
            nxt = path[t + 1]
            if (s, a) in destinations and destinations[s, a] != nxt:
                return None
            if (s, a) not in destinations:
                destinations[s, a] = nxt
                incoming[nxt] += 1
    prior = beta ** (r - 1) * prod(factorial(h - 1) for h in incoming)
    prior /= prod(beta + i for i in range(1, len(destinations) + 1))
    evidence = prod(
        F(
            factorial(alphabet - 1) * prod(map(factorial, row)),
            factorial(sum(row) + alphabet - 1),
        )
        for row in heads
    )
    ml = prod(F(prod(v**v for v in row), sum(row) ** sum(row)) for row in heads)
    assert evidence >= ml / prod(
        comb(sum(row) + alphabet - 1, alphabet - 1) for row in heads
    )
    return prior, prior * evidence


def distinct_probabilities(n, alphabet, beta):
    # Coefficients of the exponential generating function for weighted partitions.
    inverse_rising = [F(1)]
    coeff = [F(1)]
    mass = [F(1)]
    for i in range(1, n + 1):
        inverse_rising.append(inverse_rising[-1] / (alphabet + i - 1))
        coeff.append(
            beta / i * sum(coeff[i - j] * inverse_rising[j] for j in range(1, i + 1))
        )
        mass.append(mass[-1] * i * coeff[i] / ((beta + i - 1) * coeff[i - 1]))
    return mass


def check_distinct():
    alphabet = 6
    beta = F(3, 4)
    mass = distinct_probabilities(alphabet, alphabet, beta)
    checked = 0
    for n in range(alphabet + 1):
        x = tuple(range(n))
        unseen = mass[n + 1] / mass[n] if n < alphabet else F(0)
        seen = (1 - (alphabet - n) * unseen) / n if n else 0
        for a in range(alphabet):
            y = x + (a,)
            truth = sum(
                w[1]
                for path in partitions(len(y))
                if (w := partition_weight(y, path, beta, alphabet)) is not None
            )
            assert truth == mass[n] * (seen if a < n else unseen)
            checked += 1
    return checked


def check(lib):
    tapes = paths = 0
    for beta in (F(1), F(1, 4)):
        for n in range(1, 7):
            total = F(0)
            for x in product((0, 1), repeat=n):
                joint, sizes = full(lib, x, beta)
                truth = [F(0)] * n
                prior = F(0)
                count = 0
                for path in partitions(n):
                    w = partition_weight(x, path, beta)
                    if w is not None:
                        prior += w[0]
                        truth[max(path)] += w[1]
                        count += 1
                assert prior == 1 and int(sizes[-1]) == count
                np.testing.assert_allclose(
                    joint[-1], np.array(truth, dtype=float), rtol=5e-15, atol=1e-18
                )
                if n <= 4:
                    beam_mass, _, _ = beam(x, float(beta), width=32)
                    np.testing.assert_allclose(beam_mass, joint.sum(axis=1), rtol=5e-15)
                total += sum(truth)
                tapes += 1
                paths += count
            assert total == 1
    thresholds = {}
    for beta in (F(1), F(1, 4)):
        n = next(
            j
            for j in range(2, 25)
            if beta * (2 * j + 1) * comb(2 * j, j) > 2 * (j + 1) ** 2
        )
        x = (0, 1) * n
        a = partition_weight(x, (0,) * len(x), beta)
        b = partition_weight(x, x, beta)
        odds = beta * (2 * n + 1) * comb(2 * n, n) / (2 * (n + 1) ** 2)
        assert b[1] / a[1] == odds
        thresholds[str(beta)] = {
            "first_complete_cycles": n,
            "split_to_merged_odds": str(odds),
        }
    return {
        "exact_tapes": tapes,
        "valid_paths_and_comparator_checks": paths,
        "alternating_thresholds": thresholds,
        "all_distinct_next_token_exact_checks": check_distinct(),
    }


def replace_at(xs, i, value):
    return xs[:i] + (value,) + xs[i + 1 :]


def beam(x, beta, width):
    # List order breaks equal-mass ties, using old destinations in their canonical order.
    live = [(1.0, 0, (-1, -1), (0, 0), (1,))]
    evidence = retained = 1.0
    forecasts = []
    # A discarded prefix at depth u has a binary envelope w*(u+1)/(n+1).
    suspended_numerator = 0.0
    certificates = []
    peak_candidates = 1
    for t, letter in enumerate(x):
        candidates = []
        pred = 0.0
        for weight, s, table, counts, inc in live:
            idx = 2 * s + letter
            score = weight * (counts[idx] + 1) / (sum(counts[2 * s : 2 * s + 2]) + 2)
            pred += score
            if t + 1 == len(x):
                continue
            updated = replace_at(counts, idx, counts[idx] + 1)
            if table[idx] != -1:
                candidates.append((score, table[idx], table, updated, inc))
                continue
            denom = sum(inc) + beta
            for j, v in enumerate(inc):
                candidates.append(
                    (
                        score * v / denom,
                        j,
                        replace_at(table, idx, j),
                        updated,
                        replace_at(inc, j, v + 1),
                    )
                )
            j = len(inc)
            candidates.append(
                (
                    score * beta / denom,
                    j,
                    replace_at(table, idx, j) + (-1, -1),
                    updated + (0, 0),
                    inc + (1,),
                )
            )
        upper_tail = suspended_numerator / (t + 1)
        certificates.append(
            (retained, upper_tail, log1p(t * upper_tail / (retained + upper_tail)))
        )
        evidence *= pred
        forecasts.append(evidence)
        if candidates:
            peak_candidates = max(peak_candidates, len(candidates))
            candidates.sort(key=lambda branch: -branch[0])
            kept = candidates[:width]
            scale = fsum(z[0] for z in kept)
            dropped = fsum(z[0] for z in candidates[width:])
            suspended_numerator += retained * dropped * (t + 2)
            retained *= scale
            live = [
                (w / scale, s, table, counts, inc) for w, s, table, counts, inc in kept
            ]
    return forecasts, certificates, peak_candidates


def conventional(x, suffix):
    members = range(4) if suffix else product(range(4), repeat=2)
    results = []
    for choice in members:
        nstates = 2**choice if suffix else 2
        s = 0
        ct = [[0, 0] for _ in range(nstates)]
        likelihood = F(1)
        prefix = []
        for a in x:
            likelihood *= F(ct[s][a] + 1, sum(ct[s]) + 2)
            prefix.append(likelihood)
            ct[s][a] += 1
            s = (2 * s + a) % nstates if suffix else step(choice[a], s)
        results.append(prefix)
    return [float(sum(group) / len(results)) for group in zip(*results, strict=True)]


def scores(masses):
    return {
        "fit_nll": -log(masses[11]) / 12,
        "continuation_nll": -log(masses[15] / masses[11]) / 4,
    }


def experiment(lib):
    rng = np.random.Generator(np.random.PCG64(261126))
    tapes = {
        "period_four": (0, 0, 1, 1) * 4,
        "period_three": ((0, 1, 1) * 6)[:16],
        "fair_iid": tuple(map(int, rng.integers(2, size=16))),
    }
    data = {}
    for name, x in tapes.items():
        entry = {
            "tape": "".join(map(str, x)),
            "suffix_mix": scores(conventional(x, True)),
            "two_state_mix": scores(conventional(x, False)),
            "address_priors": [],
        }
        for beta in (1.0, 0.25):
            joint, sizes = full(lib, x, beta)
            neutral, check_sizes = full(lib, x, beta, True)
            assert np.array_equal(sizes, check_sizes)
            masses = joint.sum(axis=1)
            post = joint / masses[:, None]
            prior = neutral / (0.5 ** np.arange(1, len(x) + 1))[:, None]
            np.testing.assert_allclose(prior.sum(axis=1), 1, atol=2e-14, rtol=0)
            approx, certs, peak_candidates = beam(x, beta, 32)
            prefix_mass = np.r_[1.0, masses[:-1]]
            actual_log_ratios = np.log(
                (masses / prefix_mass) / (approx / np.r_[1.0, approx[:-1]])
            )
            retained, upper_tail, bounds = np.transpose(certs)
            assert np.all(retained <= prefix_mass * (1 + 3e-14))
            assert np.all(prefix_mass <= (retained + upper_tail) * (1 + 3e-14))
            assert np.all(actual_log_ratios <= bounds + 5e-14)
            entry["address_priors"].append(
                {
                    "beta": beta,
                    "complete_mixture": scores(masses),
                    "beam32": scores(approx),
                    "beam32_peak_candidates_before_pruning": peak_candidates,
                    "beam32_continuation_excess_and_certificate_nats": [
                        float(actual_log_ratios[12:].sum()),
                        float(bounds[12:].sum()),
                    ],
                    "beam32_largest_single_token_excess_and_bound_nats": [
                        float(max(actual_log_ratios)),
                        float(max(bounds)),
                    ],
                    "prefix_branches_at_12_and_16": sizes[[11, 15]].tolist(),
                    "total_prefix_branch_visits": int(sizes.sum()),
                    "posterior_mean_visited_states": (
                        post[[11, 15]] @ np.arange(1, 17)
                    ).tolist(),
                    "prior_mean_on_clamped_inputs": (
                        prior[[11, 15]] @ np.arange(1, 17)
                    ).tolist(),
                    "posterior_over_states_at_16": post[-1].tolist(),
                }
            )
        data[name] = entry
    return {"registration": "f9a6c19", "tapes": data}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "sample"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with native() as library:
        report = check(library) if args.command == "check" else experiment(library)
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(encoded.encode())
    else:
        print(encoded, end="")
