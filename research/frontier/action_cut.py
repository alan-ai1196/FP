"""Exact finite audits for two-state update learning, autonomous calibration and tape elimination."""

import json
from collections import defaultdict
from fractions import Fraction as F
from functools import cache
from itertools import combinations, product


def step(action, state):
    return action if action < 2 else state ^ (action - 2)


def ones_and_totals(edges, actions):
    ones, size = [0, 0], [0, 0]
    for u, v in edges:
        for start in (0, 1):
            s = step(actions[v], step(actions[u], start))
            size[s] += 1
            ones[s] += 1 - start
    return tuple(ones), tuple(size)


@cache
def bernoulli_record(ones, count):
    if count == 0:
        return F(1)
    return F(ones**ones * (count - ones) ** (count - ones), count**count)


def likelihood(ones, size):
    return bernoulli_record(ones[0], size[0]) * bernoulli_record(ones[1], size[1])


@cache
def anchored_likelihood(b, ones, size):
    return likelihood(
        (b // 4 + ones[0], 3 * b // 4 + ones[1]), (b + size[0], b + size[1])
    )


def maximum_cut(d, edges):
    return max(
        sum(side[u] != side[v] for u, v in edges) for side in product((0, 1), repeat=d)
    )


def verify_graph(d, edges, cubic):
    m = len(edges)
    b = 64 * m if cubic else 128 * m * m
    optimal = 2 * maximum_cut(d, edges)
    seen = set()
    for v in product(range(4), repeat=d):
        ones, size = ones_and_totals(edges, v)
        score = ones[1] + size[0] - ones[0]
        assert score <= optimal
        if cubic:
            assert abs(size[1] - m) <= min(m, 12 * (optimal - score))
        seen.add((ones, size))
    best = max(anchored_likelihood(b, *p) for p in seen)
    winners = {
        o[1] + n[0] - o[0] for o, n in seen if anchored_likelihood(b, o, n) == best
    }
    assert winners == {optimal}
    return len(seen)


PERIOD = (1,) * 3 + (0,) * 3
PERIOD = PERIOD * 2 + ((1,) * 5 + (0,) * 5) * 2


def scan(data, actions, initial=0):
    """data are the tokens scored AFTER the initial, already observed context."""
    state = initial
    ones, size = [0, 0], [0, 0]
    for token in data:
        if token < 2:
            size[state] += 1
            ones[state] += token
        state = step(actions[token], state)
    return state, tuple(ones), tuple(size)


def calibration():
    bound = F(3, 8) ** 12 * F(5, 8) ** 20
    distinct_constants = F(1, 4) ** 8 * F(3, 4) ** 24
    count = 0
    for a in product(range(4), repeat=2):
        for initial in (0, 1):
            boundary = scan(PERIOD, a, initial)[0]
            end, o, n = scan(PERIOD, a, boundary)
            assert boundary == end
            p = likelihood(o, n)
            if set(a) == {0, 1}:
                assert p == distinct_constants and n == (16, 16)
            else:
                assert p <= bound
            count += 1
    # Human-readable sufficient inequality at the smallest simple cubic graph.
    # p_bad^(2B-32) < p_good^(2B) * (1/4)^(2m), compared exactly.
    for m in (6, 9, 12):
        b = 64 * m
        assert bound ** ((2 * b - 32) // 32) < distinct_constants ** (2 * b // 32) * F(
            1, 4
        ) ** (2 * m)
    return count


def full_tape_k4():
    edges = tuple(combinations(range(2, 6), 2))
    b = 64 * len(edges)
    graph = tuple(k for u, v in edges for k in (u, v, 1, u, v, 0))
    best, winners = F(0), []
    for prefix in product(range(4), repeat=2):
        # First 0 is observed. Every period ends at the same boundary after warmup.
        start = step(prefix[0], 0)
        boundary, a, n = scan(PERIOD, prefix, start)
        boundary2, a2, n2 = scan(PERIOD, prefix, boundary)
        assert boundary == boundary2
        repeats = b // 16 - 1
        for names in product(range(4), repeat=4):
            acts = prefix + names
            _, pos, ct = scan(graph, acts, boundary)
            ones = tuple(a[s] + repeats * a2[s] + pos[s] for s in (0, 1))
            size = tuple(n[s] + repeats * n2[s] + ct[s] for s in (0, 1))
            p = likelihood(ones, size)
            if p >= best:
                if p > best:
                    winners = []
                best = p
                winners.append((prefix, names))
    # Cubic odd degree forces all winning vertex actions to be permutations.
    assert all(set(a) == {0, 1} and set(v) <= {2, 3} for a, v in winners)
    assert all(sum(v[u - 2] != v[w - 2] for u, w in edges) == 4 for _, v in winners)
    return {"all_programs": 4**6, "maximizers": len(winners), "maximum_cut": 4}


def tape_dp(x, y, p, sum_product):
    first = {v: x.index(v) for v in set(x)}
    last = {v: len(x) - 1 - x[::-1].index(v) for v in set(x)}
    live = ()
    scores = {(0, ()): F(1)}
    width = 0
    for i, (v, target) in enumerate(zip(x, y, strict=True)):
        after = tuple(sorted(w for w in set(live) | {v} if last[w] > i))
        width = max(width, len(after))
        new = defaultdict(F)
        for (s, encoded), mass in scores.items():
            choices = dict(zip(live, encoded, strict=True))
            for a in range(4) if first[v] == i else (choices[v],):
                choices[v] = a
                dest = step(a, s)
                key = (dest, tuple(choices[w] for w in after))
                chance = p[dest] if target else 1 - p[dest]
                value = mass * chance
                if sum_product:
                    new[key] += value / (4 if first[v] == i else 1)
                else:
                    new[key] = max(new[key], value)
        scores, live = new, after
    return (sum(scores.values()) if sum_product else max(scores.values())), width


def verify_dp():
    p, cases = (F(1, 5), F(2, 3)), 0
    for x in ((0, 1, 2, 0, 1, 2), (0, 0, 1, 1, 2, 2), (0, 1, 1, 2, 1, 0)):
        for y in product((0, 1), repeat=len(x)):
            all_probs = []
            for a in product(range(4), repeat=3):
                s, chance = 0, F(1)
                for token, target in zip(x, y, strict=True):
                    s = step(a[token], s)
                    chance *= p[s] if target else 1 - p[s]
                all_probs.append(chance)
            assert tape_dp(x, y, p, True)[0] == sum(all_probs) / 64
            assert tape_dp(x, y, p, False)[0] == max(all_probs)
            cases += 2
    return cases


def main():
    graphs = 0
    pairs = list(combinations(range(4), 2))
    for mask in range(1, 1 << len(pairs)):
        verify_graph(4, [e for k, e in enumerate(pairs) if (mask >> k) & 1], False)
        graphs += 1
    k33 = tuple(product(range(3), range(3, 6)))
    prism = ((0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5))
    for d, edges in ((4, pairs), (6, k33), (6, prism)):
        verify_graph(d, edges, True)
    return {
        "loopless_labeled_four_vertex_nonempty_graphs": graphs,
        "cubic_graphs": 3,
        "calibration_pairs_and_starts": calibration(),
        "autonomous_k4": full_tape_k4(),
        "exact_tape_dp_comparisons": verify_dp(),
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
