"""Run a finite prefix of a learned reset policy and harmonic report in pinned R4."""

import json
from fractions import Fraction as F
from math import ceil
from pathlib import Path

from grouped_forecast import UNIT, coefficient, eigenvalue
from positive_comparison import categorical_program


def exact_forecast(coeff, t, k):
    def factor(n, s):
        return 1 + 2 * sum(
            F(coeff[j - 1], UNIT) * eigenvalue(n, j) * coefficient(n, j, s)
            for j in range(1, min(len(coeff), n) + 1)
        )

    return F(2 * k + 1, 2 * t + 2) * factor(t + 1, k + 1) / factor(t, k)


def r4_prefix(row, depth=4, cost=0.004):
    install = row["install"]
    gains = row["panels"]["128"]["harmonic"]["gain"]
    actions = tuple(int(g > cost + 1e-14) for g in gains)
    counts = install["seen"]
    states, edges, q = [("start",)], [], []
    for state in states:
        successors = []
        if state[0] == "start":
            p = F(2 * sum(counts[4:]) + 1, 2 * (sum(counts) + 1))
            successors = [("action", x, actions[x]) for x in (0, 1)]
        elif state[0] == "action":
            _, x, a = state
            h = 4 * x + 2 * a
            p = F(2 * counts[h + 1] + 1, 2 * (sum(counts[h : h + 2]) + 1))
            successors = [("report", h + b, 0, 0) for b in (0, 1)]
        else:
            _, h, t, k = state
            p = exact_forecast(install["harmonic_q15"][h], t, k)
            if t < depth:
                successors = [("report", h, t + 1, k + y) for y in (0, 1)]
        if not successors:
            successors = [state, state]
        for nxt in successors:
            if nxt not in states:
                states.append(nxt)
        edges.append([states.index(nxt) for nxt in successors])
        q.append(p)
    # R4 adds one positive unit to each of the two score heads.
    scale = ceil(2 / min(min(q), 1 - max(q)))
    slots, heads = [1], [[], []]
    for i, p in enumerate(q):
        for head, mass in zip(heads, (1 - p, p)):
            w = scale * mass - 1
            if w not in slots:
                slots.append(w)
            head.append((i, slots.index(w)))
    event, start, size = categorical_program(("0", "1"), edges, heads, slots)
    reached, work = {0: start}, [0]
    checked = 0
    for i in work:
        current = reached[i]
        assert tuple(current.probabilities) == (1 - q[i], q[i])
        if states[i][0] == "report" and states[i][2] == depth:
            continue
        for y, j in enumerate(edges[i]):
            after = event(str(y), current.delayed)
            assert tuple(after.probabilities) == (1 - q[j], q[j])
            assert tuple(v[0] for _, v in after.delayed) == tuple(
                int(j == s) for s in range(len(states))
            )
            if j not in reached:
                reached[j] = after
                work.append(j)
            checked += 1
    assert len(reached) == len(states)
    return {"policy": actions, "checked_edges": checked, **size}


def run_prefix():
    receipts = json.loads(
        Path(__file__).with_name("learn_resets_result.json").read_text()
    )
    return {r["family"]: r4_prefix(r) for r in receipts["fits"] if "install" in r}
