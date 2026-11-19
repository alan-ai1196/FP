"""Exact finite-context fitting and a recurrent realization of its continuation forecasts."""
from dataclasses import dataclass
from fractions import Fraction as F
from math import gcd, lcm

from learner import FitWork, normalize, solve, subtract


def grid_fit(counts, total):
    """Minimize multiclass empirical Brier loss on the strictly positive mass grid."""
    k = len(counts)
    if total < k or k < 2 or any(n < 0 for n in counts):
        raise ValueError("invalid positive grid or counts")
    n = sum(counts)
    if not n:
        counts, n = [1] * k, k
    masses = [1] * k
    for _ in range(total - k):
        j = min(range(k), key=lambda y: (2 * masses[y] + 1) * n - 2 * total * counts[y])
        masses[j] += 1
    return tuple(masses)


def exact_form(values):
    denom = lcm(*(x.denominator for x in values))
    weights = [int(x * denom) for x in values]
    divisor = gcd(denom, *weights)
    return denom // divisor, tuple((i, w // divisor) for i, w in enumerate(weights) if w)


def apply_form(form, state):
    denom, weights = form
    value = sum(w * state[i] for i, w in weights)
    quotient, residual = divmod(value, denom)
    if residual:
        raise ArithmeticError("state outside the exact fitted closure")
    return quotient


@dataclass(frozen=True)
class StreamModel:
    transitions: tuple
    heads: tuple

    def step(self, state, symbol):
        return tuple(apply_form(f, state) for f in self.transitions[symbol])

    def read(self, state):
        return tuple(apply_form(f, state) for f in self.heads)


def realize(table, alphabet_size):
    """Close learned head columns under the observed raw-context shift."""
    contexts = len(table)
    cols = []
    pivots = {}
    work = FitWork()

    def insert(column):
        residual = list(map(F, column))
        for i in sorted(pivots):
            if residual[i]:
                residual = subtract(residual, residual[i], pivots[i], work)
        j = next((i for i, v in enumerate(residual) if v), None)
        if j is not None:
            pivots[j] = normalize(residual, residual[j], work)
            cols.append(column)

    def shifted(col, a):
        return tuple(col[(i * alphabet_size + a) % contexts] for i in range(contexts))

    heads = list(zip(*table, strict=True))
    for head in heads:
        insert(head)
    for col in cols:  # Each independent child joins this same finite queue.
        for a in range(alphabet_size):
            insert(shifted(col, a))
    if not cols:
        raise ValueError("zero output table")
    shift_cols = [shifted(col, a) for a in range(alphabet_size) for col in cols]
    anchor = sorted(pivots)
    left = [[col[i] for col in cols] for i in anchor]
    right = [[col[i] for col in shift_cols + heads] for i in anchor]
    solved = solve(left, right, work)
    forms = [exact_form(col) for col in zip(*solved, strict=True)]
    r = len(cols)
    model = StreamModel(tuple(tuple(forms[a*r:(a+1)*r]) for a in range(alphabet_size)),
                        tuple(forms[alphabet_size*r:]))
    state_rows = list(zip(*cols, strict=True))
    return model, state_rows, work


def all_suffix_lines(signs, alphabet_size):
    def orient(col):
        return tuple(col[0] * v for v in col)
    lines = [orient(signs)]
    seen = set(lines)
    for line in lines:
        for a in range(alphabet_size):
            col = orient([line[(i * alphabet_size + a) % len(signs)] for i in range(len(signs))])
            if col not in seen:
                seen.add(col)
                lines.append(col)
    return lines


def stationarity(probs):
    """Independent exact occupation law for a strictly positive finite-context source."""
    n, k = len(probs), len(probs[0])
    eq = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for j, row in enumerate(probs):
        for a, p in enumerate(row):
            eq[(j * k + a) % n][j] -= p
    eq[-1] = [F(1)] * n
    solved = solve(eq, [[F(int(i == n-1))] for i in range(n)], FitWork())
    pi = [w[0] for w in solved]
    assert all(w > 0 for w in pi) and sum(pi) == 1
    for i in range(n):
        assert pi[i] == sum(pi[j] * p for j, row in enumerate(probs) for a, p in enumerate(row)
                            if (j*k+a) % n == i)
    return pi
