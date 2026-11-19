"""Certify partial-orbit layout search against a separately constructed complete oracle."""
from itertools import product
from pathlib import Path
import argparse
import json

from audit import boundary, reference_graph, run_word
from discovery import discover
from learner import FitWork, moment_blocks, words
from materialization import Bank, execute


def measurements(alphabet, initial, step, output, short):
    probes = {p + a + s for p in short for s in short for a in ("", *alphabet)}
    counts = {}
    for w in sorted(probes, key=lambda w: (len(w), w)):
        label = int(output(run_word(initial, step, w)) > 0)
        for outcome in [label, 1-label, label, label]:
            counts.setdefault(w, [0, 0])[outcome] += 1
    signs = {w: 1 if o > z else -1 for w, (z, o) in counts.items()}
    work = FitWork()
    s, left, right = moment_blocks(signs, short, alphabet, len(short), work)
    return (s, left, right), dict(raw_words=len(probes), ordinary_labels=4*len(probes),
                                  input_symbols=4*sum(map(len, probes)), basis_divisions=work.divisions,
                                  basis_multiply_subtracts=work.multiply_subtracts)


def study(alphabet, initial, step, output, short, workloads):
    (suffixes, left, right), training = measurements(alphabet, initial, step, output, short)
    # Independent oracle has the hidden graph; the search receives only empirical moments.
    graph, values = reference_graph(alphabet, initial, step, output)
    columns = []
    for s in suffixes:
        dest = list(range(len(values)))
        for a in s:
            ai = alphabet.index(a)
            dest = [graph[j][ai] for j in dest]
        columns.append(tuple(values[j] for j in dest))
    bank = Bank.fit(graph, values, columns)
    trials = []
    for counts, stop_price in workloads:
        result, plans = discover(left, right, counts, next_charge=stop_price)
        _, optimal, _ = bank.choose(counts)
        assert all(lo <= optimal <= hi for lo, hi in result["intervals"])
        start = (0, (1,)*result["registers"])
        pairs = [start]
        seen = {start}
        per_letter = [None]*len(alphabet)
        for i, state in pairs:
            assert left[0][0]*state[0] == values[i]
            for a, dest in enumerate(graph[i]):
                after, spent = execute(state, plans[a])
                if per_letter[a] is None:
                    per_letter[a] = spent
                assert per_letter[a] == spent
                pair = dest, after
                if pair not in seen:
                    seen.add(pair)
                    pairs.append(pair)
        assert result["intervals"][-1][1] == sum(a*b for a, b in zip(counts, per_letter))
        trials.append(result)
    return len(bank.forms), training, trials


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    cases = [(n, 0) for n in product(range(3), repeat=3)]
    cases += [((2,1,4), 100)]
    c, _, trials = study("qmv", (1,1,-1), boundary, lambda s: s[0], list(words("qmv", 2)), cases)
    assert c == 4 and any(len(t["intervals"]) > 1 for t in trials)
    assert all(t["exact"] for t in trials[:-1])
    assert not trials[-1]["exact"] and trials[-1]["intervals"][-1][1]-trials[-1]["intervals"][-1][0] <= 100
    hidden = [(0,2,0), (0,0,2), (0,0,3), (3,1,0)]
    c2, _, complementary = study("012", 0, lambda s,a: hidden[s][int(a)], lambda s: 1 if s == 0 else -1,
                                 list(words("012", 3)), [((2,3,9), 0)])
    r = 8
    def transition(s, a):
        if a == "q":
            return (s+1) % r
        if a == "m":
            return 1-s if s < 2 else s
        return 1 if s == 0 else s
    size, training, large = study("qmv", 0, transition, lambda s: 1 if s == 0 else -1,
                                  ["q"*i for i in range(r)], [((46,53,1), 0)])
    assert size == 2**(r-1) and large[0]["expanded"] == r and large[0]["discovered"] == r+2
    result = dict(small_workloads=len(cases), early_exit=trials[-1], complementary_full_orbit=c2,
                  complementary_intervals=complementary[0]["intervals"], monoid_rank=r,
                  monoid_full_orbit=size, monoid_acquisition=training, monoid_search=large[0])
    rendered = json.dumps(result, indent=2)
    if args.check:
        assert json.loads(rendered) == json.loads(Path(__file__).with_name("discovery_result.json").read_text())
    print(rendered)


if __name__ == "__main__":
    main()
