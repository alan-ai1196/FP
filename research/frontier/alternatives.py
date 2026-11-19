"""Independent squared-loss factor learner and rank-one passive acquisition checks."""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb
import json
from pathlib import Path
import argparse

from learner import FitWork, solve
from audit import boundary, run_word


def word_mask(word, alphabet):
    mask = 1  # intercept is the initial sign, also unknown
    for letter in word:
        mask ^= 1 << (alphabet.index(letter) + 1)
    return mask


class ParityEquations:
    def __init__(self):
        self.rows = {}

    def reduce(self, mask):
        bit = 0
        for pivot in sorted(self.rows, reverse=True):
            if (mask >> pivot) & 1:
                row, rhs = self.rows[pivot]
                mask ^= row
                bit ^= rhs
        return mask, bit

    def add(self, mask, bit):
        residual, known = self.reduce(mask)
        if residual:
            self.rows[residual.bit_length() - 1] = residual, known ^ bit
        elif known != bit:
            raise ValueError("inconsistent empirical sign equations")


def fit_rank_one(events, alphabet, min_visits):
    counts = {}
    for word, label in events:
        mask = word_mask(word, alphabet)
        counts.setdefault(mask, [0, 0])[label] += 1
    equations = ParityEquations()
    margin = 0
    visits = 0
    for mask, (zeros, ones) in counts.items():
        if zeros + ones >= min_visits and zeros != ones:
            equations.add(mask, int(zeros > ones))
            visits += zeros + ones
            margin += abs(ones - zeros)
    return equations, F(margin, visits) if visits else F(0)


def linear_design():
    alphabet = "pqrv"
    truth = 0b11010
    def episode(word):
        clean = 1 - ((word_mask(word, alphabet) & truth).bit_count() & 1)
        return [(word, y) for y in (clean, clean, 1 - clean, clean)]
    even = [a + b for a in alphabet for b in alphabet]
    even_tape = [event for w in even for event in episode(w)]
    before, rho = fit_rank_one(even_tape, alphabet, 4)
    after, rho_after = fit_rank_one(even_tape + episode("r"), alphabet, 4)
    assert (len(before.rows), len(after.rows)) == (4, 5) and rho == rho_after == F(1, 2)
    tests = 0
    for n in range(6):
        for raw in product(alphabet, repeat=n):
            mask = word_mask("".join(raw), alphabet)
            res, sign = before.reduce(mask)
            assert bool(res) == bool(n % 2)
            if not res:
                assert sign == ((mask & truth).bit_count() & 1)
            assert after.reduce(mask) == (0, (mask & truth).bit_count() & 1)
            tests += 1
    # Different linear systems and query masks checked against every consistent parameter.
    checks = 0
    for records in combinations(range(1, 8), 3):
        for target in range(8):
            eq = ParityEquations()
            for row in records:
                eq.add(row, (row & target).bit_count() % 2)
            compatible = [h for h in range(8) if all(not ((row & (target ^ h)).bit_count() % 2)
                                                       for row in records)]
            for mask in range(8):
                residual, bit = eq.reduce(mask)
                count = sum((mask & h).bit_count() % 2 for h in compatible)
                if residual:
                    assert 2 * count == len(compatible)
                else:
                    assert count == bit * len(compatible)
                checks += 1
    return dict(before_dimension=len(before.rows), after_dimension=len(after.rows),
                even_examples=len(even_tape), added_examples=4, query_words=tests,
                posterior_checks=checks, calibration=str(rho))


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left, right):
    cols = transpose(right)
    return [[sum(x * y for x, y in zip(row, col, strict=True)) for col in cols] for row in left]


def ridge_update(target, fixed, decay, work):
    gram = multiply(transpose(fixed), fixed)
    for j in range(len(gram)):
        gram[j][j] += decay
    return transpose(solve(gram, transpose(multiply(target, fixed)), work))


def pair_fit(tape, decay, sweeps, blank=False):
    counts = [[[0, 0] for _ in range(2)] for _ in range(2)]
    for i, j, label in tape:
        counts[i][j][label] += 1
    assert len({sum(c) for row in counts for c in row}) == 1
    target = [[F(o - z, o + z) for z, o in row] for row in counts]
    u = [[F(int(i == j and not blank)) for j in range(2)] for i in range(2)]
    work = FitWork()
    trace = []
    for _ in range(sweeps):
        v = ridge_update(transpose(target), u, decay, work)
        u = ridge_update(target, v, decay, work)
        fitted = multiply(u, transpose(v))
        trace.append(fitted)
    return trace, work


def factor():
    tape = [(i, j, (i ^ j) ^ flip) for i, j in product(range(2), repeat=2)
            for flip in (0, 0, 0, 1)]
    trace, work = pair_fit(tape, F(1, 2), 3)
    zero, _ = pair_fit(tape, F(1, 2), 1, blank=True)
    costs = []
    for fitted in trace:
        a, b = fitted[0]
        c, d = fitted[1]
        assert a * d == b * c and a == d == -b == -c
        costs.append(sum((F(1 + fitted[i][j], 2) - y) ** 2 for i, j, y in tape) / len(tape))
    assert all(v < F(1, 4) for v in costs) and zero[0] == [[0, 0], [0, 0]]
    # The first sweep can overshoot the regularized limit; raw risk need not decrease to it.
    return dict(examples=len(tape), trainable_entries=8, dense_sweeps=3,
                first_sweep_positive_score=str(trace[0][0][1]), first_sweep_brier=str(costs[0]),
                last_score_within_1e_6_of_regularized_limit=abs(trace[-1][0][1] - F(1, 4)) < F(1, 10**6),
                last_score_integer_bits=max(trace[-1][0][1].numerator.bit_length(),
                                            trace[-1][0][1].denominator.bit_length()),
                zero_seed_stationary=True, saturated_table_brier="3/16",
                solve_divisions=work.divisions, solve_multiply_subtracts=work.multiply_subtracts)


def geometric_risk():
    prefixes = ("", "q", "qq", "m", "mq", "mqq")
    probes = ("", "q", "qq", "vqq")
    start = (1, 1, -1)
    columns = [tuple(run_word(start, boundary, p + s)[0] for p in prefixes) for s in probes]
    all_bits = [(1, *rest) for rest in product((-1, 1), repeat=5)]
    def distance(a, b):
        wrong = sum(x != y for x, y in zip(a, b, strict=True))
        return min(wrong, len(a) - wrong)
    distances = [[distance(c, bit) for bit in all_bits] for c in columns]
    minimum = min(sum(min(row[j] for j in js) for row in distances)
                  for js in combinations(range(len(all_bits)), 3))
    def routed(state, letter):
        if letter == "v":
            x, y, _ = state
            return x, y, -x
        return boundary(state, letter)
    errors = sum(run_word(start, routed, p + s)[0] != run_word(start, boundary, p + s)[0]
                 for p in prefixes for s in probes)
    assert minimum == errors == 2
    e = F(errors, 24)
    rho = F(1, 2)
    beta = rho * (1 - 2 * e)
    loss = (1 - rho ** 2) / 4 + rho ** 2 * e * (1 - e)
    assert loss == F(119, 576)
    return dict(free_three_bit_encodings=comb(32, 3), minimum_errors=minimum, cases=24,
                optimal_router_amplitude=str(beta), optimal_router_brier=str(loss),
                transform_brier="3/16", excess=str(loss - F(3, 16)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = dict(partial_coverage=linear_design(), ridge_factors=factor(), sharp_risk=geometric_risk())
    if args.check:
        assert result == json.loads(Path(__file__).with_name("alternatives_result.json").read_text())
    print(json.dumps(result, indent=2))
