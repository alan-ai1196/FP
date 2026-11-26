"""Exact observable polynomial identities for homogeneous stochastic updates."""

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from itertools import permutations, product
from math import factorial, prod
from pathlib import Path

import numpy as np
from pair_memory import modular_rank

REGISTRATION = "9700cc6"


def commutator(p, q):
    terms = Counter()
    for u, a in p.items():
        for v, b in q.items():
            terms[u + v] += a * b
            terms[v + u] -= a * b
    return {w: v for w, v in terms.items() if v}


def identities():
    bracket = {"MC": 1, "CM": -1}
    square = {u + v: a * b for u, a in bracket.items() for v, b in bracket.items()}
    return [commutator(square, {letter: 1}) for letter in "MC"]


def matrix_word(word, m, c):
    value = np.eye(len(m), dtype=m.dtype)
    for letter in word:
        value = value @ (c if letter == "C" else m)
    return value


def word_ranks(polynomials):
    rng = np.random.default_rng(91507)
    pairs = rng.integers(-5, 6, size=(24, 2, 2, 2))
    ranks = []
    for length in range(6):
        words = ["".join(w) for w in product("MC", repeat=length)]
        entries = np.array(
            [[matrix_word(w, m, c).flatten() for w in words] for m, c in pairs]
        )
        cells = entries.transpose(0, 2, 1).reshape(-1, len(words))
        ranks.append(int(modular_rank(cells)))
        if length == 5:
            for p in polynomials:
                assert np.all(cells @ np.array([p.get(w, 0) for w in words]) == 0)
    assert ranks == [1, 2, 4, 8, 16, 30]
    return ranks


def character(word, signs):
    return prod(s for letter, s in zip(word, signs, strict=True) if letter == "C")


def contrast(p, signs):
    return signs[0] * sum(a * character(w, signs[1:]) for w, a in p.items())


def positive_example(polynomials, *, stationary):
    if stationary:
        minus, plus = (2, 1, 1, 0), (3, 0, 1, 3)
        center = np.array([F(v, 7) for v in (2, 2, 1, 2)])
        reset = center.copy()
        head = np.array([F(v, 4) for v in (-3, 3, 3, 3)])
        clean_gap = F(11, 28)
    else:
        minus, plus = (1, 2, 3, 0), (3, 1, 0, 2)
        center = np.array([F(1, 4)] * 4)
        reset = center / 8
        reset[0] += F(7, 8)
        head = np.array([F(v, 4) for v in (-3, 3, -3, 3)])
        clean_gap = F(7, 8) / 2
    eps = F(1, 8)
    eye = np.eye(4, dtype=int)
    tm, tp = [(1 - eps) * eye[list(dests)] + eps * center for dests in (minus, plus)]
    m, c = (tp + tm) / 2, (tp - tm) / 2
    if stationary:
        assert np.array_equal(reset @ m, reset)
    inputs = list(product((-1, 1), repeat=6))
    raw_law = {}
    for signs in inputs:
        state = reset.copy()
        for sign in signs:
            state = state @ (tp if sign == 1 else tm)
        mean = state @ head
        for y in (-1, 1):
            raw_law[signs, y] = (1 + y * mean) / 128
    assert min(raw_law.values()) > 0 and sum(raw_law.values()) == 1
    # Direct observation margin versus conditioned matrix multiplication for all masks.
    for letters in product("MC", repeat=6):
        observable = sum(
            y * prob * character(letters, signs) for (signs, y), prob in raw_law.items()
        )
        assert observable == reset @ matrix_word(letters, m, c) @ head
    gaps = []
    for p in polynomials:
        raw = sum(prob * y * contrast(p, signs) for (signs, y), prob in raw_law.items())
        direct = sum(
            a * (reset @ c @ matrix_word(w, m, c) @ head) for w, a in p.items()
        )
        assert direct == raw
        gaps.append(raw)
    expected = clean_gap * (1 - eps) ** 6 * F(3, 4)
    assert gaps[0] == expected
    return {
        "minus": minus,
        "plus": plus,
        "reset": list(map(str, reset)),
        "refresh_distribution": list(map(str, center)),
        "refresh_probability": str(eps),
        "terminal_means": list(map(str, head)),
        "minimum_transition": str(min(tm.min(), tp.min())),
        "minimum_raw_record_probability": str(min(raw_law.values())),
        "matches_64_raw_fourier_coefficients": True,
        "observable_gaps": list(map(str, gaps)),
        "three_state_excess_nll_floor": str(sum(d * d for d in gaps) / 12),
    }


def vandermonde_terms(d):
    for order in permutations(range(d + 1)):
        sign = (-1) ** sum(i > j for k, i in enumerate(order) for j in order[k + 1 :])
        yield sign, "C".join("M" * exponent for exponent in order)


def alternating_score(d, signs):
    """Accumulate signed exponent permutations with the same used exponents."""
    last = (1 << (d + 1)) - 1
    values = [0] * (last + 1)
    positions = [0] * (last + 1)
    for mask in range(1, last + 1):
        low = mask & -mask
        positions[mask] = positions[mask ^ low] + low.bit_length()
    values[0] = 1
    for used in range(last):
        for j in range(d + 1):
            if used & (1 << j):
                continue
            after = used | (1 << j)
            sign = (-1) ** ((used >> (j + 1)).bit_count())
            if after != last:
                sign *= signs[positions[after] - 1]
            values[after] += sign * values[used]
    return values[last]


def alternating_audit(d):
    terms = list(vandermonde_terms(d))
    rng = np.random.default_rng(600 + d)
    length = d * (d + 3) // 2
    assert len({w for _, w in terms}) == factorial(d + 1)
    for _ in range(6):
        signs = list(map(int, rng.choice((-1, 1), size=length)))
        assert alternating_score(d, signs) == sum(
            a * character(w, signs) for a, w in terms
        )
    m, c = rng.integers(-2, 3, (2, d, d)).astype(object)
    assert not np.any(sum(a * matrix_word(w, m, c) for a, w in terms))
    diagonal = np.diag(np.arange(d + 1)).astype(object)
    shift = np.diag(np.ones(d, dtype=int), 1).astype(object)
    large = sum(a * matrix_word(w, diagonal, shift) for a, w in terms)
    det = prod(factorial(i) for i in range(1, d + 1))
    assert large[0, d] == det and np.count_nonzero(large) == 1
    return {
        "restricted_dimension": d,
        "suffix_reads": length,
        "terms": len(terms),
        "subset_transitions": (d + 1) * 2**d,
        "adjacent_nonzero_entry": det,
    }


def audit():
    polynomials = identities()
    inputs = list(product((-1, 1), repeat=6))
    scores = np.array([[contrast(p, s) for s in inputs] for p in polynomials])
    assert np.array_equal(scores @ scores.T, 384 * np.eye(2, dtype=int))
    for s, first, second in zip(inputs, *scores):
        a, z1, z2, z3, z4, z5 = s
        assert first == 4 * a * (int(z2 == z5 == -z3) - int(z1 == z4 == -z3))
        assert abs(second) == abs(first)
    ranks = word_ranks(polynomials)
    return {
        "registration": REGISTRATION,
        "integer_matrix_pairs": 24,
        "rank_modulus": 1009,
        "ranks_by_suffix_length": ranks,
        "full_six_sign_span_dimension": 1 + sum(ranks),
        "commutator_coefficients": polynomials,
        "contrast_frequencies": dict(sorted(Counter(map(int, scores[0])).items())),
        "positive_stationary": positive_example(polynomials, stationary=True),
        "positive_permutations_with_refresh": positive_example(
            polynomials, stationary=False
        ),
        "alternating_checks": [alternating_audit(d) for d in range(1, 6)],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
