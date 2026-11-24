"""Independent exact small laws for the horizon, hidden orbit and repeat-read bounds."""

import json
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import prod

import sympy as sp
from reversible_reports import plant


def partitions(n, lower=1):
    if not n:
        yield ()
    for k in range(lower, n + 1):
        for tail in partitions(n - k, k):
            yield (k, *tail)


def orbit(cycles, signs):
    n = len(signs)
    move = []
    for m in cycles:
        start = len(move)
        move.extend([start + (i + 1) % m for i in range(m)])
    phase = signs
    c = []
    while True:
        c.append(F(sum(x * y for x, y in zip(signs, phase, strict=True)), n))
        phase = tuple(phase[move[i]] for i in range(n))
        if phase == signs:
            return tuple(c)


def horizon(cap=7):
    sources = []
    counts = []
    for n in range(1, cap + 1):
        for cycles in partitions(n):
            for signs in product((-1, 1), repeat=n):
                sources.append(orbit(cycles, signs))
        # Equal first n moments at ANY two sizes <=n must give identical complete cycles.
        seen = {}
        for c in sources:
            prefix = tuple(c[i % len(c)] for i in range(n))
            assert seen.setdefault(prefix, c) == c
        counts.append(len(seen))
        if n >= 3:
            f = (-1,) + (1,) * (n - 1)
            x, y = orbit((n,), f), orbit((n - 1, 1), f)
            assert x[: n - 1] == y[: n - 1] and x[n - 1] != y[0]
    bad_max = orbit(
        (5, 7, *((1,) * 12)), (-1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, *([1] * 12))
    )
    assert max(t.denominator for t in bad_max[:11]) == 3 and bad_max[14] == F(5, 6)
    return {
        "capacity": cap,
        "sources": len(sources),
        "distinct_correlations_by_cap": counts,
        "denominators_24_state_example": [t.denominator for t in bad_max[:15]],
    }


def group_orbit():
    actions, f, _ = plant()
    first = tuple(2 * f.astype(int) - 1)
    words = {first: ()}
    work = [first]
    for row in work:
        for i, perm in enumerate(actions):
            nxt = tuple(row[h] for h in perm)
            if nxt not in words:
                work.append(nxt)
                words[nxt] = (i, *words[row])
    rank = sp.Matrix(work).rank()
    assert len(work) == 56 and rank == 8
    return {
        "distinct_endpoint_states": len(work),
        "linear_dimension": rank,
        "largest_shortest_word": max(map(len, words.values())),
    }


def noisy_parities(k, rho):
    vectors = list(product((-1, 1), repeat=k))
    result = {}
    for theta in (-1, 1):
        hidden = [v for v in vectors if prod(v) == theta]
        row = []
        for observed in vectors:
            p = sum(
                prod((1 + rho * x * y) / 2 for x, y in zip(v, observed, strict=True))
                for v in hidden
            ) / len(hidden)
            assert p == (1 + theta * rho**k * prod(observed)) / 2**k
            row.append(p)
        assert all(
            row[i] + row[i + 1] == F(1, 2 ** (k - 1)) for i in range(0, len(row), 2)
        )
        result[theta] = row
    return sum(abs(a - b) for a, b in zip(result[1], result[-1], strict=True)) / 2


def best_repeats(k, rho, horizon):
    odds = (1 + rho) / (1 - rho)
    bias = [(odds**i - 1) / (odds**i + 1) for i in range(horizon + 1)]

    @lru_cache(None)
    def value(counts, remaining):
        if not remaining:
            return (1 + prod(bias[i] for i in counts)) / 2
        candidates = []
        for i in set(counts):
            rest = list(counts)
            rest.remove(i)
            align = (1 + rho * bias[i]) / 2
            candidates.append(
                align * value(tuple(sorted([*rest, i + 1])), remaining - 1)
                + (1 - align) * value(tuple(sorted([*rest, abs(i - 1)])), remaining - 1)
            )
        return max(candidates)

    return value((0,) * k, horizon)


def run():
    rho = F(3, 4)
    tv = [noisy_parities(k, rho) for k in range(2, 7)]
    assert tv == [rho**k for k in range(2, 7)]
    adaptive = {
        str(k): {str(h): str(best_repeats(k, rho, h)) for h in (k - 1, k, 2 * k, 3 * k)}
        for k in (2, 3, 4)
    }
    assert all(
        F(rows[str(int(k) - 1)]) == F(1, 2) and F(rows[k]) == (1 + rho ** int(k)) / 2
        for k, rows in adaptive.items()
    )
    return {
        "horizon": horizon(),
        "opaque_actions": group_orbit(),
        "noise_amplitude": str(rho),
        "one_pass_parity_total_variations_k_2_to_6": list(map(str, tv)),
        "optimal_accuracy_with_repeats": adaptive,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
