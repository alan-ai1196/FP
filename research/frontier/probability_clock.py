"""Finite-state likelihood, population optima and approximation costs for a probability clock."""

import argparse
import json
from fractions import Fraction as F
from itertools import product
from math import ceil, floor, prod
from pathlib import Path

import numpy as np
from text import log_bounds, outward, ratio_log

RHO, AMP, COS = F(2, 3), F(1, 2), F(3, 5)
SIN = F(4, 5)
BUDGETS = (1, 2, 4, 8, 16, 32)
TRUNC = 104


def cosines(n, c):
    last, value = c, F(1)
    out = []
    for _ in range(n):
        out.append(value)
        last, value = value, 2 * c * value - last
    return out


def rates(n, amplitude, c):
    return [(1 + amplitude * v) / 2 for v in cosines(n, c)]


def sample(n, seed):
    rng = np.random.Generator(np.random.PCG64(seed))
    ages = rng.geometric(1 - float(RHO), size=n) - 1
    probabilities = np.array([float(p) for p in rates(int(ages.max()) + 1, AMP, COS)])
    tape = np.zeros(int(ages.sum()) + n, dtype=np.uint8)
    tape[np.cumsum(ages + 1) - 1] = np.where(rng.random(n) < probabilities[ages], 1, 2)
    return tape


def count(tape):
    marks = np.flatnonzero(tape)
    assert marks[-1] == len(tape) - 1
    ages = np.diff(marks, prepend=-1) - 1
    return np.bincount(ages).tolist(), np.bincount(
        ages[tape[marks] == 1], minlength=ages.max() + 1
    ).tolist()


def bucket(k, m, l):
    return k if k < m else m + (k - m) % l


def pool(counts, m, l):
    out = [0] * (m + l)
    for k, n in enumerate(counts):
        out[bucket(k, m, l)] += n
    return out


def fit_bins(total, hits):
    return [F(2 * h + 1, 2 * n + 2) for n, h in zip(total, hits, strict=True)]


def fit_layout(total, hits, k):
    best = None
    for cycle in range(1, k + 1):
        m = k - cycle
        n, h = pool(total, m, cycle), pool(hits, m, cycle)
        coefficients = {}
        for each, yes in zip(n, h, strict=True):
            for value, sign in ((each, 1), (yes, -1), (each - yes, -1)):
                if value > 1:
                    coefficients[value] = coefficients.get(value, 0) + sign * value
        lo = hi = 0
        for v, c in coefficients.items():
            a, b = log_bounds(v)
            lo += c * (a if c > 0 else b)
            hi += c * (b if c > 0 else a)
        take = best is None or hi < best[0]
        if best is not None and not take and lo <= best[1]:
            diff = coefficients.copy()
            for v, c in best[2].items():
                diff[v] = diff.get(v, 0) - c
            take = prod(v**c for v, c in diff.items() if c > 0) < prod(
                v ** (-c) for v, c in diff.items() if c < 0
            )
        if take:
            best = (lo, hi, coefficients)
            selected = cycle
    return selected


def ce(p, q):
    bounds = []
    for weight, rate in ((p, q), (1 - p, 1 - q)):
        bounds.append((weight, ratio_log(rate.denominator, rate.numerator)))
    return tuple(sum(w * bound[i] for w, bound in bounds) for i in (0, 1))


def average(terms):
    return tuple(sum(w * cost[i] for w, cost in terms) for i in (0, 1))


def print_bounds(cost, n=1):
    return outward((floor(cost[0]), ceil(cost[1])), n)


def observed(total, hits, advance, forecast):
    n = sum(total)
    ticks = sum(k * v for k, v in enumerate(total))
    terms = [(ticks + n, ce(F(ticks, ticks + n), advance))]
    for k, (v, h) in enumerate(zip(total, hits, strict=True)):
        if v:
            terms.append((v, ce(F(h, v), forecast[k])))
    return print_bounds(average(terms), ticks + n)


def multiply(a, b):
    x, y = a
    u, v = b
    return x * u - y * v, x * v + y * u


def power(k):
    out = (F(1), F(0))
    for _ in range(k):
        out = multiply(out, (COS, SIN))
    return out


def population_layout(k, l):
    m = k - l
    table = []
    for j in range(k):
        if j < m:
            weight = (1 - RHO) * RHO**j
            real = power(j)[0]
        else:
            scale = RHO**l
            weight = (1 - RHO) * RHO**j / (1 - scale)
            a, b = power(l)
            u, v = 1 - scale * a, scale * b
            real = (1 - scale) * multiply(power(j), (u, v))[0] / (u * u + v * v)
        table.append((weight, (1 + AMP * real) / 2))
    assert sum(w for w, _ in table) == 1
    return table


def population(table, advance, forecast):
    return average(
        [
            (1, ce(RHO, advance)),
            *[
                ((1 - RHO) * w, ce(p, q))
                for (w, p), q in zip(table, forecast, strict=True)
            ],
        ]
    )


def clock_population(advance, amplitude, c):
    actual = rates(TRUNC, AMP, COS)
    fitted = rates(TRUNC, amplitude, c)
    lo, hi = average(
        [
            (1, ce(RHO, advance)),
            *[
                ((1 - RHO) ** 2 * RHO**k, ce(p, q))
                for k, (p, q) in enumerate(zip(actual, fitted, strict=True))
            ],
        ]
    )
    min_q = (1 - abs(amplitude)) / 2
    upper = ratio_log(min_q.denominator, min_q.numerator)[1]
    return lo, hi + (1 - RHO) * RHO**TRUNC * upper


def stream_counts(tape, k, l):
    n = [0] * k
    h = [0] * k
    state = 0
    for token in tape:
        if token == 0:
            state = state + 1 if state + 1 < k else k - l
        else:
            n[state] += 1
            h[state] += int(token == 1)
            state = 0
    return n, h


def law(word, initial_mean):
    # Conditional tick probability is constant. Before the first mark use the
    # supplied initial complex phase mean; any mark resets the phase to one.
    phase = initial_mean
    probability = F(1)
    for token in word:
        if token == 0:
            probability *= RHO
            phase = multiply(phase, (COS, SIN))
        else:
            probability *= (
                (1 - RHO) * (1 + (AMP if token == 1 else -AMP) * phase[0]) / 2
            )
            phase = (F(1), F(0))
    return probability


def capped_probability(word, cap):
    k = len(cap)
    weights = [w for w, _ in cap]
    for token in word:
        new = [F(0)] * k
        for i, (_, p) in enumerate(cap):
            if token == 0:
                new[min(i + 1, k - 1)] += weights[i] * RHO
            else:
                new[0] += weights[i] * (1 - RHO) * (p if token == 1 else 1 - p)
        weights = new
    return sum(weights)


def clock_audit():
    minor = [
        [law((0,) * i + s, (F(1), F(0))) for s in ((), (1,), (0, 1))] for i in range(3)
    ]
    a, b, c = minor[0]
    d, e, f = minor[1]
    g, h, j = minor[2]
    determinant = a * (e * j - f * h) - b * (d * j - f * g) + c * (d * h - e * g)
    # Every two-state candidate has zero minor. Each word event differs by at
    # most four-word TV, and the six three-factor products are 3-Lipschitz.
    tv = abs(determinant) / 18
    loss_floor = 2 * (1 - RHO) * tv * tv
    u, v = 1 - RHO * COS, RHO * SIN
    start = ((1 - RHO) * u / (u * u + v * v), (1 - RHO) * v / (u * u + v * v))
    audited = 0
    for k in range(1, 6):
        cap = population_layout(k, 1)

        for length in range(k + 1):
            for word in product(range(3), repeat=length):
                assert capped_probability(word, cap) == law(word, start)
                audited += 1
        separator = (1,) + (0,) * (k - 1) + (1,)
        assert capped_probability(separator, cap) != law(separator, start)
    return {
        "cap_stationary_word_equalities": audited,
        "postreset_rank_three_minor": str(determinant),
        "two_state_TV_lower": str(tv),
        "two_state_rate_lower_nats": str(loss_floor),
    }


def experiment():
    train = sample(65536, 2026112305)
    total, hits = count(train)
    ticks = len(train) - sum(total)
    advance = F(2 * ticks + 1, 2 * len(train) + 2)
    pairs = fit_bins(total[:2], hits[:2])
    amp = max(-1 + F(1, 65536), min(1 - F(1, 65536), 2 * pairs[0] - 1))
    c = max(F(-1), min(F(1), (2 * pairs[1] - 1) / amp)) if amp else F(0)
    choices = {k: fit_layout(total, hits, k) for k in BUDGETS}
    test = sample(65536, 2026112306)
    nt, ht = count(test)
    rows = {}
    for k, l in choices.items():
        layouts = {}
        best = None
        ideal = {}
        for cycle in range(1, k + 1):
            table = population_layout(k, cycle)
            val = population(table, RHO, [p for _, p in table])
            ideal[cycle] = val
            if best is None or val[1] < ideal[best][0]:
                best = cycle
            elif val[0] <= ideal[best][1]:
                raise ArithmeticError(
                    "population optima are too close for this precision"
                )
        for name, cycle in (("selected", l), ("saturated", 1)):
            bins = pool(total, k - cycle, cycle)
            positives = pool(hits, k - cycle, cycle)
            params = fit_bins(bins, positives)
            current = [params[bucket(age, k - cycle, cycle)] for age in range(len(nt))]
            evaluated = stream_counts(test, k, cycle)
            assert evaluated == (pool(nt, k - cycle, cycle), pool(ht, k - cycle, cycle))
            layouts[name] = {
                "cycle": cycle,
                "heldout_nll": observed(nt, ht, advance, current),
                "population_nll": print_bounds(
                    population(population_layout(k, cycle), advance, params)
                ),
            }
        layouts["best_possible_cycle"] = best
        layouts["optimum_population_nll"] = print_bounds(ideal[best])
        layouts["saturated_optimum_nll"] = print_bounds(ideal[1])
        rows[str(k)] = layouts
    other = {}
    for name, p, a, angle in (("fitted", advance, amp, c), ("oracle", RHO, AMP, COS)):
        other[name] = {
            "heldout_nll": observed(nt, ht, p, rates(len(nt), a, angle)),
            "population_nll": print_bounds(clock_population(p, a, angle)),
        }
    return {
        "registration": "e98ce50",
        "runs_per_split": 65536,
        "train_tokens": len(train),
        "test_tokens": len(test),
        "max_train_age": len(total) - 1,
        "max_test_age": len(nt) - 1,
        "train_age_zero_one_counts": total[:2],
        "fitted_parameters": [str(x) for x in (advance, amp, c)],
        "layouts_scored": sum(BUDGETS),
        "finite_machines": rows,
        "rotation": other,
        "exact_controls": clock_audit(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment()
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf-8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
