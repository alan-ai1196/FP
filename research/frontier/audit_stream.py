"""Causal single-stream checks with an exact independently fitted context-tree baseline."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import json
from math import comb
from pathlib import Path
from random import Random

from stream import all_suffix_lines, grid_fit, realize, stationarity


def kt(z, o):
    return F(comb(2*z, z) * comb(2*o, o), 4**(z+o) * comb(z+o, z))


def ctw(counts, depth):
    levels = [None] * (depth + 1)
    levels[depth] = [(z, o, kt(z, o), F(1)) for z, o in counts]
    for k in reversed(range(depth)):
        level = []
        for c in range(2**k):
            left, right = levels[k+1][c], levels[k+1][c+2**k]
            z, o = left[0] + right[0], left[1] + right[1]
            local = kt(z, o)
            joint = local + left[2] * right[2]
            level.append((z, o, joint / 2, local / joint))
        levels[k] = level
    forecasts = []
    for c in range(2**depth):
        p = F(0)
        for k in reversed(range(depth+1)):
            z, o, _, stop = levels[k][c % (2**k)]
            p = stop * F(2*o+1, 2*(z+o+1)) + (1-stop) * p
        forecasts.append((1-p, p))
    return levels[0][0][2], forecasts


def draw(rng, masses):
    u = rng.randrange(sum(masses))
    for y, m in enumerate(masses):
        if u < m:
            return y
        u -= m
    raise ArithmeticError("invalid mass")


def complete_grid(k):
    checks = 0
    for n in range(k, k + 5):
        options = [c for c in product(range(1, n), repeat=k) if sum(c) == n]
        for counts in product(range(4), repeat=k):
            totals = sum(counts)
            def objective(c):
                return sum(totals * x*x - 2*n*cnt*x for x, cnt in zip(c, counts, strict=True))
            assert objective(grid_fit(counts, n)) == min(map(objective, options))
            checks += 1
    return checks


def scan():
    rows = []
    for length in (1, 2, 3):
        found = []
        for code in range(2**(2**length)):
            col = tuple(1 if (code >> i) & 1 else -1 for i in range(2**length))
            model, rows_by_context, _ = realize([(x,) for x in col], 2)
            for i, st in enumerate(rows_by_context):
                assert model.read(st) == (col[i],)
                for a in (0, 1):
                    assert model.step(st, a) == rows_by_context[(2*i+a) % len(col)]
            if len(all_suffix_lines(col, 2)) > len(rows_by_context[0]):
                found.append(code)
        rows.append(dict(depth=length, tables=2**(2**length), strict=len(found),
                         first=next(iter(found), None)))
    assert [v["strict"] for v in rows] == [0, 0, 16] and rows[-1]["first"] == 18
    return rows


def affine_grids():
    # Coefficients and offsets are represented in half units.
    checked = 0
    maxima = {}
    for m in range(2, 9):
        bound = m*m - m*m//4
        pairs = list(product(range(m), repeat=2))
        peak = 0
        for a, b in product((-4, -2, -1, 1, 2, 4), repeat=2):
            for offset in range(-2*m, 2*m+1):
                values = [offset+a*x+b*y for x, y in pairs]
                valid = sum(not v % 2 and 0 <= v <= 2*(m-1) for v in values)
                assert valid <= bound
                peak = max(peak, valid)
                checked += 1
        assert peak == bound
        midpoint = sum((x+y) % 2 == 0 for x, y in pairs)
        assert midpoint == ((m+1)//2)**2 + (m//2)**2
        assert all(abs(F((x+y+1)//2, m-1) - F(x+y, 2*(m-1))) <= F(1, 2*(m-1)) for x, y in pairs)
        maxima[str(m)] = peak
    return dict(mixed_affine_forms=checked, maximum_accepted_pairs=maxima)


def dec(v):
    return Decimal(v.numerator) / Decimal(v.denominator)


def scores(forecasts, truth, stationary, test):
    with localcontext() as ctx:
        ctx.prec = 60
        losses = []
        for weights in ([tuple(w * p for p in row) for w, row in zip(stationary, truth)],
                        [tuple(F(x, sum(map(sum, test))) for x in row) for row in test]):
            loss = sum(-dec(w)*dec(q).ln() for row, forecast in zip(weights, forecasts)
                       for w, q in zip(row, forecast))
            losses.append(format(loss, ".12f"))
        return dict(stationary_nll=losses[0], held_out_nll=losses[1])


def stream_trial(hidden_masses, length, visits, seed, sign_law):
    k = len(hidden_masses[0])
    contexts = k**length
    rng = Random(seed)
    raw = 0
    counts = [[0]*k for _ in range(contexts)]
    full_counts = [[0]*k for _ in range(contexts)]
    tokens = 0
    # Fair forecasts for every token up to the predetermined coverage checkpoint.
    while min(map(sum, counts)) < visits:
        prediction = (F(1, k),) * k
        y = draw(rng, hidden_masses[raw])
        assert prediction[y] == F(1, k)
        full_counts[raw][y] += 1
        if sum(counts[raw]) < visits:
            counts[raw][y] += 1
        raw = (raw*k+y) % contexts
        tokens += 1
        if tokens > 100000:
            raise RuntimeError("coverage checkpoint exceeded audit allowance")
    if sign_law:
        table = [(1 if o > z else -1,) for z, o in counts]
        assert all(z != o for z, o in counts)
        amp = F(sum(abs(o-z) for z, o in counts), visits*contexts)
        def decode(values):
            p = (1 + amp * values[0]) / 2
            return 1-p, p
    else:
        grid = 12
        table = [grid_fit(c, grid) for c in counts]
        def decode(values):
            return tuple(F(x, grid) for x in values)
    model, states, work = realize(table, k)
    for i, state in enumerate(states):
        assert model.read(state) == table[i]
        for a in range(k):
            assert model.step(state, a) == states[(i*k+a) % contexts]
    predictions = [decode(model.read(s)) for s in states]
    fitted = {(c, a): F(2*row[a]+1, 2*sum(row)+k) for c, row in enumerate(full_counts) for a in range(k)}
    table_kt = [tuple(fitted[c, a] for a in range(k)) for c in range(contexts)]
    state = states[raw]
    test = [[0]*k for _ in range(contexts)]
    for _ in range(4096):
        p = decode(model.read(state))
        assert p == predictions[raw] and sum(p) == 1
        y = draw(rng, hidden_masses[raw])
        test[raw][y] += 1
        state = model.step(state, y)
        raw = (raw*k+y) % contexts
    truth = [tuple(F(x, sum(row)) for x in row) for row in hidden_masses]
    pi = stationarity(truth)
    reports = {name: scores(rows, truth, pi, test) for name, rows in
               [("learned", predictions), ("indexed_same_fit", list(map(decode, table))),
                ("full_prefix_KT", table_kt), ("true_law", truth)]}
    result = dict(seed=seed, tokens=tokens, retained=visits*contexts, contexts=contexts,
                  state_dimension=len(states[0]), distinct_rows=len(set(states)),
                  transition_taps=[[len(form[1]) for form in row] for row in model.transitions],
                  fit_divisions=work.divisions, fit_multiply_subtracts=work.multiply_subtracts,
                  held_out_tokens=sum(map(sum, test)), scores=reports)
    if sign_law:
        result["signed_copy_width"] = len(all_suffix_lines([c[0] for c in table], k))
        result["amplitude"] = str(amp)
        assert table == [(1 if o > z else -1,) for z, o in hidden_masses]
        assert result["state_dimension"] == 4 and result["signed_copy_width"] == 5
        base, forecasts = ctw(full_counts, length)
        for c, row in enumerate(forecasts):
            for y in (0, 1):
                extra = [list(r) for r in full_counts]
                extra[c][y] += 1
                nxt, _ = ctw(extra, length)
                assert nxt / base == row[y]
        reports["full_prefix_frozen_CTW"] = scores(forecasts, truth, pi, test)
        reports["same_retained_frozen_CTW"] = scores(ctw(counts, length)[1], truth, pi, test)
        with localcontext() as ctx:
            ctx.prec = 60
            joint, _ = ctw([[x+y for x, y in zip(t, h)] for t, h in zip(full_counts, test)], length)
            result["continuing_CTW_held_out_nll"] = format(-dec(joint / base).ln() / sum(map(sum,test)), ".12f")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    binary = [[1, 3] if i in (1, 4) else [3, 1] for i in range(8)]
    ternary = [[2+i+j, 2+(i*j)%3, 8-i-j-(i*j)%3] for i, j in product(range(3), repeat=2)]
    out = dict(smallest_binary=scan(), finite_grid_rigidity=affine_grids(),
               nearest_grid_checks=complete_grid(2)+complete_grid(3),
               binary=stream_trial(binary, 3, 63, 2719, True),
               ternary=stream_trial(ternary, 2, 97, 3503, False))
    if args.check:
        assert out == json.loads(Path(__file__).with_name("stream_result.json").read_text())
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
