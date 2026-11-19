"""Bound the value of an undiscovered continuation register using only fitted moments."""
from fractions import Fraction as F

from learner import FitWork, integer_column, solve
from materialization import layout_cut, lower_layout


def discover(left, right, counts, rent=0, next_charge=0):
    """Return a feasible executable layout, certified cost interval and search accounting."""
    r = len(left)
    if not r or len(right) != r or any(len(row) != r for row in left):
        raise ValueError("square independent rows required")
    if not counts or any(len(row) != r*len(counts) for row in right) or next_charge < 0:
        raise ValueError("invalid shifted moments or acquisition charge")
    signs = left[0]
    b = [[x*s for x, s in zip(row, signs, strict=True)] for row in left]
    shifted = [[[row[a*r+j]*signs[j] for j in range(r)] for row in right] for a in range(len(counts))]
    fit = FitWork()
    inv = solve(b, [[F(i == j) for j in range(r)] for i in range(r)], fit)
    ids, forms, coefficients = {}, [], []
    multiplies = 0

    def identify(raw):
        nonlocal multiplies
        if any(v not in (-1, 1) for v in raw):
            raise ValueError("fitted moments violate the signed closure")
        orientation = int(raw[0])
        signature = tuple(int(v)*orientation for v in raw)
        if signature not in ids:
            ids[signature] = len(ids)
            weights = [sum(x*y for x, y in zip(row, signature, strict=True)) for row in inv]
            multiplies += r*r
            coefficients.append(weights)
            forms.append(integer_column(weights))
        return ids[signature], orientation

    for column in zip(*b, strict=True):
        identify(column)
    assert len(ids) == r
    demands = [dict() for _ in counts]
    expanded = set()
    todo = list(range(r))
    intervals = []
    arc_visits = 0
    while True:
        for j in todo:
            for a, block in enumerate(shifted):
                raw = [sum(v*w for v, w in zip(row, coefficients[j], strict=True)) for row in block]
                multiplies += r*r
                demands[a][j] = identify(raw)
            expanded.add(j)
        boundary = set(range(len(ids))) - expanded
        triples = [(a, j, i) for a, row in enumerate(demands) for j, (i, _) in row.items()]
        upper_set, high, upper_work = layout_cut(r, forms, triples, counts, rent, boundary)
        optimistic, low, lower_work = layout_cut(r, forms, triples, counts, rent)
        arc_visits += upper_work["arcs"] + lower_work["arcs"]
        if intervals:
            assert intervals[-1][0] <= low <= high <= intervals[-1][1]
        intervals.append((low, high))
        if high-low <= next_charge:
            plans = lower_layout(r, forms, demands, upper_set)
            return dict(intervals=intervals, expanded=len(expanded), discovered=len(ids),
                        registers=len(upper_set), exact=low == high, rational_dot_terms=multiplies,
                        inverse_divisions=fit.divisions, inverse_multiply_subtracts=fit.multiply_subtracts,
                        cut_arcs_constructed=arc_visits), plans
        candidates = optimistic & boundary
        assert candidates
        todo = [min(candidates)]
