"""Sparse acquisition of a new action from ordinary binary word outcomes."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random
import argparse
import json

from learner import FitWork, moment_blocks, solve
from materialization import independent


def dot(row, col):
    return sum(x*y for x, y in zip(row, col, strict=True))


def advance(state, matrix):
    return [dot(state, col) for col in zip(*matrix, strict=True)]


def predict(word, start, actions, head):
    state = start
    for a in word:
        state = advance(state, actions[a])
    return dot(state, head)


def design(pre, post, start, anchor, head):
    row, col = start, head
    for _ in range(pre):
        row = advance(row, anchor)
    for _ in range(post):
        col = [dot(r, col) for r in anchor]
    return [x*y for x in row for y in col]


def update(entries, dimension):
    rows = [d for d, _, _ in entries]
    active = independent(zip(*rows, strict=True))
    m = len(active)
    gram = [[sum(n*d[i]*d[j] for d,n,_ in entries) for j in active] for i in active]
    right = [[sum(h*d[i] for d,_,h in entries)] for i in active]
    rhs = [a+[int(i==j) for j in range(m)] for i,a in enumerate(right)]
    work = FitWork()
    solved = solve(gram, rhs, work)
    values = [F(0)]*dimension
    for j, fit in zip(active, solved, strict=True):
        values[j] = fit[0]

    def query(d):
        if len(independent([*rows, d])) != m:
            return None
        da = [d[j] for j in active]
        variance_proxy = dot(da, [dot(v[1:], da) for v in solved])
        return dot(d, values), variance_proxy
    return values, query, len(active), work


def fit_anchors(familiar, counts, n):
    means = {w: F(counts[w], n) for w in familiar}
    work = FitWork()
    suffixes, left, shifted = moment_blocks(means, ["", "q"], "q", 2, work)
    anchor = solve(left, shifted, work)
    return [means[s] for s in suffixes], anchor, [int(s == "") for s in suffixes], work


def enclosure(value, scale=10**9):
    scaled = value * scale
    return [scaled.numerator // scaled.denominator, -(-scaled.numerator // scaled.denominator)]


def sampled_check(oracle, familiar, probes, n):
    seed = 27031
    random = Random(seed)
    words = familiar + ["q"*i + "v" + "q"*j for i, j in probes]
    counts = {}
    for word in words:
        probability = oracle(word)
        counts[word] = sum(random.randrange(probability.denominator) < probability.numerator for _ in range(n))
    start, anchor, head, _ = fit_anchors(familiar, counts, n)
    entries = [(design(i, j, start, anchor, head), n, counts[w])
               for (i, j), w in zip(probes, words[len(familiar):], strict=True)]
    fitted, _, rank, _ = update(entries, 4)
    transitions = {"q": anchor, "v": [fitted[:2], fitted[2:]]}
    constant = F(sum(counts.values()), n*len(words))
    clipped_count = tested = 0
    squared = constant_squared = F(0)
    for length in range(9):
        for symbols in product("qv", repeat=length):
            word = "".join(symbols)
            if word in counts:
                continue
            raw = predict(word, start, transitions, head)
            forecast = min(F(1), max(F(0), raw))
            target = oracle(word)
            squared += (forecast - target)**2
            constant_squared += (constant - target)**2
            clipped_count += (raw != forecast)
            tested += 1
    assert rank == 4 and tested == 503
    return dict(seed=seed, successes=list(counts.values()), design_rank=rank,
                unseen_words=tested, raw_outside_unit_interval=clipped_count, scale=10**9,
                clipped_mean_excess_brier=enclosure(squared/tested),
                fitted_constant_mean_excess_brier=enclosure(constant_squared/tested))


def paired_actions():
    identity = [[1, 0], [0, 1]]
    swap = [[0, 1], [1, 0]]
    start, head = [1, 0], [F(1,4), F(3,4)]
    first = {"q": swap, "b": identity, "c": identity}
    second = {"q": swap, "b": swap, "c": swap}
    tests = 0
    for length in range(7):
        for pieces in product(("q", "bc"), repeat=length):
            word = "".join(pieces)
            assert predict(word, start, first, head) == predict(word, start, second, head)
            tests += 1
    single = [predict("b", start, a, head) for a in (first, second)]
    assert single == [F(1,4), F(3,4)]
    survival = F(63,64)
    assert (1-survival)/2 == F(1,128) and (1-survival**64)/2 > F(1,4)
    return dict(paired_word_checks=tests, isolated_b_forecasts=list(map(str, single)),
                one_step_drift="1/128", drift_after_64_scaled=enclosure((1-survival**64)/2), scale=10**9)


def experiment():
    # Test-only generator. The fitter receives words and individual binary outcomes.
    planted = {"q": [[F(1,2), F(1,2)], [F(0), F(1)]],
               "v": [[F(3,4), F(1,4)], [F(1,2), F(1,2)]]}
    oracle = lambda w: predict(w, [F(1), F(0)], planted, [F(1,4), F(3,4)])
    n = 512
    def labels(word):
        positives = n*oracle(word)
        assert positives.denominator == 1
        for i in range(n):
            yield ((i+1)*positives.numerator//n - i*positives.numerator//n)

    familiar = ["q"*i for i in range(4)]
    counts = {w: sum(labels(w)) for w in familiar}
    start, anchor, head, anchor_work = fit_anchors(familiar, counts, n)
    probes = [(0,0), (1,0), (2,1), (3,2)]
    entries = []
    for pre, post in probes:
        w = "q"*pre + "v" + "q"*post
        entries.append((design(pre, post, start, anchor, head), n, sum(labels(w))))
    _, partial, rank, _ = update(entries[:2], 4)
    novel = design(4, 0, start, anchor, head)
    pred, proxy = partial(novel)
    assert rank == 2 and pred == oracle("qqqqv")
    assert partial(design(0, 1, start, anchor, head)) is None
    full, fitted, full_rank, fit_work = update(entries, 4)
    assert full_rank == 4
    new = [full[:2], full[2:]]
    actions = {"q": anchor, "v": new}
    checked = 0
    for t in range(9):
        for symbols in product("qv", repeat=t):
            w = "".join(symbols)
            assert predict(w, start, actions, head) == oracle(w)
            checked += 1
    # The observable-coordinate map intertwines both operations on every length.
    observation = [[oracle(""), oracle("q")], [F(3,4), F(3,4)]]
    for a, op in planted.items():
        for idx, row in enumerate(op):
            assert advance(row, observation) == advance(observation[idx], actions[a])
    compatible = [(x,y) for x,y in product((-1,1),repeat=2) if x+y==2]
    assert compatible == [(1,1)]
    return dict(labels_per_word=n, familiar_words=4, familiar_labels=4*n, rare_words=4,
                rare_labels=4*n, training_symbol_reads=n*(sum(map(len,familiar))+sum(i+j+1 for i,j in probes)),
                partial_rank=rank, partial_novel_forecast=str(pred), partial_variance_proxy=str(proxy),
                full_rank=full_rank, learned_action=[[str(v) for v in row] for row in new],
                full_novel_variance_proxy=str(fitted(novel)[1]), exact_word_checks=checked,
                anchor_divisions=anchor_work.divisions, anchor_multiply_subtracts=anchor_work.multiply_subtracts,
                fit_divisions=fit_work.divisions, fit_multiply_subtracts=fit_work.multiply_subtracts,
                sampled=sampled_check(oracle, familiar, probes, n), counterexamples=paired_actions())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment()
    if args.check:
        assert result == json.loads(Path(__file__).with_name("action_result.json").read_text())
    print(json.dumps(result, indent=2))
