"""Derive and execute a priced register layout for a learned signed continuation law."""
from collections import deque
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations

from learner import FitWork, integer_column, normalize, solve, subtract


def independent(vectors):
    pivots = {}
    selected = []
    work = FitWork()
    for i, vec in enumerate(vectors):
        row = list(map(F, vec))
        for j in sorted(pivots):
            if row[j]:
                row = subtract(row, row[j], pivots[j], work)
        j = next((j for j, value in enumerate(row) if value), None)
        if j is not None:
            pivots[j] = normalize(row, row[j], work)
            selected.append(i)
    return selected


@dataclass
class Bank:
    rank: int
    forms: tuple
    demand: tuple
    columns: tuple
    head_sign: int

    @classmethod
    def fit(cls, graph, output, basis=None):
        def orient(col):
            return tuple(col[0] * x for x in col)
        columns = [orient(col) for col in basis] if basis is not None else [orient(output)]
        ids = {col: i for i, col in enumerate(columns)}
        d = len(graph[0])
        mapping = [[] for _ in range(d)]
        for col in columns:
            for a in range(d):
                shifted = tuple(col[graph[i][a]] for i in range(len(graph)))
                key = orient(shifted)
                if key not in ids:
                    ids[key] = len(columns)
                    columns.append(key)
                mapping[a].append((ids[key], shifted[0]))
        b = independent(columns)
        if basis is not None:
            assert b == list(range(len(basis)))
        order = b + [i for i in range(len(columns)) if i not in b]
        names = {orig: j for j, orig in enumerate(order)}
        assert names[ids[orient(output)]] == 0
        ordered = tuple(columns[i] for i in order)
        rank = len(b)
        coordinates = list(zip(*ordered[:rank], strict=True))
        anchors = independent(coordinates)
        sol = solve([list(coordinates[i]) for i in anchors],
                    [[col[i] for col in ordered] for i in anchors], FitWork())
        forms = tuple(integer_column(col) for col in zip(*sol, strict=True))
        demand = tuple(tuple((names[row[i][0]], row[i][1]) for i in order) for row in mapping)
        return cls(rank, forms, demand, ordered, output[0])

    def cost(self, selected, counts, rent):
        total = sum(counts)
        charge = len(selected) * (3*total + rent)
        for n, row in zip(counts, self.demand, strict=True):
            missing = {row[j][0] for j in selected} - selected
            charge += n * sum(2*len(self.forms[i])+1 for i in missing)
        return charge

    def choose(self, counts, rent=0):
        if len(counts) != len(self.demand):
            raise ValueError("one count per symbol required")
        queries = ((a, j, i) for a, row in enumerate(self.demand) for j, (i, _) in enumerate(row))
        selected, flow, work = layout_cut(self.rank, self.forms, queries, counts, rent)
        assert flow == self.cost(selected, counts, rent)
        return selected, flow, work

    def lower(self, selected):
        return lower_layout(self.rank, self.forms, self.demand, selected)


def lower_layout(rank, forms, demands, selected):
    ids = sorted(selected)
    assert ids[:rank] == list(range(rank))
    plans = []
    for row in demands:
        slots = {v: i for i, v in enumerate(ids)}
        missing = sorted({row[j][0] for j in ids} - selected)
        for i in missing:
            slots[i] = len(slots)
        plans.append((tuple(forms[i] for i in missing),
                      tuple((slots[row[j][0]], row[j][1]) for j in ids)))
    return tuple(plans)


def execute(state, plan):
    synth, writes = plan
    scratch = list(state)
    work = 0
    for form in synth:
        val = sum(w if state[j] > 0 else -w for j, w in form)
        assert val != 0
        scratch.append(1 if val > 0 else -1)
        work += 2*len(form) + 1
    new = tuple(scratch[j] if sign > 0 else -scratch[j] for j, sign in writes)
    return new, work + 3*len(writes)


def choose_basis(bank, graph, counts, rent=0):
    """Finite comparison over observable bases with the output held resident."""
    tried = 0
    winner = None
    output = tuple(bank.head_sign * v for v in bank.columns[0])
    for extra in combinations(range(1, len(bank.columns)), bank.rank-1):
        ids = (0, *extra)
        basis = [bank.columns[j] for j in ids]
        if len(independent(basis)) != bank.rank:
            continue
        tried += 1
        alternate = Bank.fit(graph, output, basis)
        selected, score, _ = alternate.choose(counts, rent)
        key = (score, len(selected), ids)
        if winner is None or key < winner[0]:
            winner = key, alternate, selected
    key, alternate, selected = winner
    return alternate, selected, key[0], tried


def layout_cut(rank, forms, dependencies, counts, rent, forbidden=()):
    if any(type(n) is not int or n < 0 for n in (*counts, rent)):
        raise ValueError("nonnegative integer resource counts required")
    c = len(forms)
    source, sink = c, c + 1
    fees = [(i, sink, 3*sum(counts)+rent) for i in range(c)]
    force = [(source, i) for i in range(rank)] + [(j, sink) for j in forbidden]
    needs = {}
    for a, j, i in dependencies:
        key = a, i
        if key not in needs:
            needs[key] = c + 2 + len(needs)
            fees.append((needs[key], i, counts[a]*(2*len(forms[i])+1)))
        force.append((j, needs[key]))
    bound = 1 + sum(w for _, _, w in fees)
    nodes = c + 2 + len(needs)
    flow, kept, augmentations = cut(nodes, fees + [(i,j,bound) for i,j in force], source, sink)
    selected = kept.intersection(range(c))
    assert set(range(rank)) <= selected and not selected.intersection(forbidden)
    return selected, flow, dict(vertices=nodes, arcs=len(fees)+len(force), augmentations=augmentations)


def cut(n, arcs, source, sink):
    residual = [{} for _ in range(n)]
    for i, j, capacity in arcs:
        residual[i][j] = residual[i].get(j, 0) + capacity
        residual[j].setdefault(i, 0)
    value = augmentations = 0
    while True:
        previous = {source: source}
        queue = deque([source])
        while queue and sink not in previous:
            i = queue.popleft()
            for j, weight in residual[i].items():
                if weight and j not in previous:
                    previous[j] = i
                    queue.append(j)
        if sink not in previous:
            return value, set(previous), augmentations
        path = []
        j = sink
        while j != source:
            i = previous[j]
            path.append((i, j))
            j = i
        amount = min(residual[i][j] for i, j in path)
        for i, j in path:
            residual[i][j] -= amount
            residual[j][i] += amount
        value += amount
        augmentations += 1
