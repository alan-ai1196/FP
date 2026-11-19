"""Check physical layouts against literal execution, all subsets and trained sources."""
from itertools import combinations, product
from pathlib import Path
import argparse
import json

from audit import boundary, observations, reference_graph
from learner import FitWork, Learner
from materialization import Bank, choose_basis, execute


def from_observations(alphabet, start, step, output, keep_fitted_basis):
    learner = Learner(alphabet, 4)
    for w, y in observations(alphabet, 4, start, step, output):
        learner.observe(w, y)
    machine = learner.fit(FitWork())
    states = [machine.initial]
    ids = {states[0]: 0}
    graph = []
    for s in states:
        row = []
        for a in alphabet:
            after = machine.step(s, a)
            if after not in ids:
                ids[after] = len(states)
                states.append(after)
            row.append(ids[after])
        graph.append(tuple(row))
    signs = [s[0] for s in states]
    basis = list(zip(*states, strict=True)) if keep_fitted_basis else None
    return Bank.fit(graph, signs, basis), graph


def all_sets(bank):
    optional = range(bank.rank, len(bank.forms))
    for size in range(len(optional) + 1):
        for subset in combinations(optional, size):
            yield set(range(bank.rank)) | set(subset)


def check(bank, graph, counts, rent=0):
    optimal, charge, witness = bank.choose(counts, rent)
    trials = []
    for subset in all_sets(bank):
        plan = bank.lower(subset)
        work = None
        for i, row in enumerate(graph):
            current = tuple(bank.columns[j][i] for j in sorted(subset))
            letter_work = []
            for a, dest in enumerate(row):
                update, paid = execute(current, plan[a])
                assert update == tuple(bank.columns[j][dest] for j in sorted(subset))
                letter_work.append(paid)
            if work is None:
                work = letter_work
            assert work == letter_work
        cost = sum(n*p for n, p in zip(counts, work, strict=True)) + rent * len(subset)
        assert cost == bank.cost(subset, counts, rent)
        trials.append((cost, subset))
    assert charge == min(c for c, _ in trials)
    assert optimal == set.intersection(*(s for c, s in trials if c == charge))
    return dict(registers=len(optimal), cost=charge, work=witness)


def finite_graphs():
    volume = 0
    for mapping in product(range(2), repeat=4):
        for signs in product((-1, 1), repeat=2):
            graph, output = reference_graph("01", 0, lambda s, a: mapping[2*s+int(a)],
                                            lambda s: signs[s])
            bank = Bank.fit(graph, output)
            for counts in [(0, 0), (1, 4), (5, 1)]:
                for rent in (0, 2):
                    check(bank, graph, counts, rent)
                    volume += 1
    return volume


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    bank, graph = from_observations("qmv", (1,1,-1), boundary, lambda s: s[0], True)
    workloads = [(3,2,2), (2,2,3), (2,1,4)]
    results = [check(bank, graph, c) for c in workloads]
    assert [t["registers"] for t in results] == [3,3,4]
    assert check(bank, graph, workloads[-1], rent=8)["registers"] == 3
    adaptive = []
    for counts in [(2,1,4), (48,4,48), (48,48,4)]:
        alternate, chosen, price, tried = choose_basis(bank, graph, counts)
        horizon = sum(counts)
        analytic = min(12*horizon, 9*horizon + 7*min(counts[0], counts[2]))
        assert price == analytic == check(alternate, graph, counts)["cost"]
        adaptive.append(dict(counts=counts, cost=price, registers=len(chosen), feasible_bases=tried))
    assert [x["registers"] for x in adaptive] == [3,4,3]
    # Selected after searching finite automata; both target graphs belong only to the generator.
    hidden = [(0,2,0), (0,0,2), (0,0,3), (3,1,0)]
    both, graph = from_observations("012", 0, lambda s,a: hidden[s][int(a)],
                                    lambda s: 1 if s == 0 else -1, False)
    options = [both.cost(s, (2,3,9), 0) for s in all_sets(both)]
    assert options == [284,291,308,252]
    assert check(both, graph, (2,3,9))["cost"] == 252
    hidden = [(2,3,3), (2,3,2), (1,1,3), (2,2,2)]
    shared, graph = from_observations("012", 0, lambda s,a: hidden[s][int(a)],
                                      lambda s: 1 if s == 1 else -1, False)
    base = set(range(shared.rank))
    uses = [[row[j][0] for j in base if row[j][0] not in base] for row in shared.demand]
    assert any(len(row) > len(set(row)) for row in uses)
    for row, plan in zip(uses, shared.lower(base), strict=True):
        assert len(plan[0]) == len(set(row))
    check(shared, graph, (2,3,9))
    result = dict(boundary_workloads=workloads, boundary_results=results,
                  alternative_bases=adaptive, complementary_layout_costs=options, missing_requests_per_letter=uses,
                  small_graph_price_checks=finite_graphs())
    rendered = json.dumps(result, indent=2)
    if args.check:
        assert json.loads(rendered) == json.loads(Path(__file__).with_name("materialization_result.json").read_text())
    print(rendered)


if __name__ == "__main__":
    main()
