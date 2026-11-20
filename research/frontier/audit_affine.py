"""Check the scalar law, its confidence sets and the registered noisy comparison."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json

from affine import bounded, feasible_endpoints, fit_symbol, learn, propagate, step
from audit_action import advance, dot, enclosure, predict, sample_counts, sampled_model

FAMILIAR = ["q"*i for i in range(4)]
PROBES = [(0,0), (1,0), (2,1), (3,2)]
WORDS = FAMILIAR + ["q"*i+"v"+"q"*j for i,j in PROBES]
HIDDEN = {"q": [[F(1,2), F(1,2)], [F(0), F(1)]],
          "v": [[F(3,4), F(1,4)], [F(1,2), F(1,2)]]}


def oracle(word):
    return predict(word, [F(1), F(0)], HIDDEN, [F(1,4), F(3,4)])


def controls():
    checks = 0
    grid = [F(i, 4) for i in range(5)]
    for x, z in product(grid, repeat=2):
        for y, t in product(grid, repeat=2):
            pairs = [(x, y, 1), (z, t, 3)]
            p = fit_symbol(pairs)
            # KKT signs on the two coordinates certify the exact square minimum.
            for j in range(2):
                grad = sum(n*(step(p, a)-b)*(a if j else 1-a) for a,b,n in pairs)
                assert (p[j] == 0 and grad >= 0) or (p[j] == 1 and grad <= 0) or grad == 0
            checks += 1
    boxes = [((F(1,4), F(1,2)), (F(1,2), F(3,4))), ((F(1,2), F(1)), (F(1,4), F(1,2)))]
    verts = feasible_endpoints(boxes)
    def feasible(v):
        for interval, (l, u) in boxes:
            values = [step(v, x) for x in interval]
            if max(values) < l or min(values) > u:
                return False
        return True
    assert all(feasible(v) for v in verts)
    for model in product(grid, repeat=2):
        if feasible(model):
            for x in grid:
                l, u = propagate(verts, (x, x))
                assert l <= step(model, x) <= u
    bad = {"": (4,2), "q": (4,2), "v": (4,1), "qv": (4,3)}
    assert learn(bad, dict.fromkeys(bad, F(0)), "qv")[-1] is None
    # On this proper subinterval the unique scalar map overshoots the full cube.
    reversal = (F(7,4), F(3,4))
    assert [step(reversal, v) for v in (F(3,4), F(1))] == [F(1), F(3,4)]
    assert step(reversal, F(0)) > 1

    exact = {w: (512, int(512*oracle(w))) for w in WORDS}
    initial, maps, first, vertices = learn(exact, dict.fromkeys(WORDS, F(0)), "qv")
    expected = {"q": (F(3,8), F(7,8)), "v": (F(5,16), F(9,16))}
    assert initial == F(1,4) and first == (initial, initial) and maps == expected
    assert all(set(vertices[a]) == {model} for a, model in expected.items())
    return dict(box_optimality_checks=checks, exact_endpoints={a: list(map(str, t)) for a,t in maps.items()})


def trial(seed, n, truth):
    counts = sample_counts(oracle, WORDS, n, seed)
    radius = {512: F(5,64), 8192: F(5,256)}[n]
    initial, maps, first, regions = learn({w: (n,h) for w,h in counts.items()},
                                          dict.fromkeys(WORDS, radius), "qv")
    old_start, old_maps, head, rank = sampled_model(FAMILIAR, PROBES, counts, n)
    assert rank == 4
    constant = F(sum(counts.values()), n*len(counts))
    errors = [F(0), F(0), F(0)]
    width = tested = violations = 0
    stochastic = {a: [[1-lo, lo], [1-hi, hi]] for a, (lo, hi) in maps.items()}
    layers = [("", initial, first, old_start, (1-initial, initial))]
    for length in range(9):
        following = []
        for w, current, band, old, categorical in layers:
            assert current == categorical[1] and sum(categorical) == 1
            if w not in counts:
                true_mean = truth[w]
                forecasts = (current, bounded(dot(old, head)), constant)
                for j, value in enumerate(forecasts):
                    errors[j] += (value-true_mean)**2
                width = max(width, band[1]-band[0])
                violations += int(not band[0] <= true_mean <= band[1])
                tested += 1
            if length < 8:
                for a in "qv":
                    next_band = propagate(regions[a], band) if regions is not None else (F(0), F(1))
                    following.append((w+a, step(maps[a], current), next_band, advance(old, old_maps[a]),
                                      advance(categorical, stochastic[a])))
        layers = following
    assert tested == 503
    means = [v / tested for v in errors]
    summary = dict(seed=seed, n=n, mean_excess_brier=[enclosure(v) for v in means],
                   maximum_interval_width=enclosure(width), violated_intervals=violations,
                   width_below_one_quarter=width < F(1,4), compatible=regions is not None)
    return means, summary


def experiment():
    checks = controls()
    truth = {"".join(w): oracle("".join(w)) for t in range(9) for w in product("qv", repeat=t)}
    _, old = trial(27031, 512, truth)
    trials = [trial(seed, 512, truth) for seed in range(32)]
    _, larger = trial(0, 8192, truth)
    means = [[v for v in e] for e, _ in trials]
    report = dict(seeds=[0,31], trials=len(trials),
                  mean_excess_brier=[enclosure(sum(col)/len(col)) for col in zip(*means, strict=True)],
                  bounded_beats_unconstrained=sum(a < b for a,b,_ in means),
                  bounded_beats_constant=sum(a < c for a,_,c in means),
                  unconstrained_beats_constant=sum(b < c for _,b,c in means),
                  trials_width_below_one_quarter=sum(r["width_below_one_quarter"] for _,r in trials),
                  trials_with_interval_miss=sum(r["violated_intervals"] > 0 for _,r in trials),
                  incompatible_trials=sum(not r["compatible"] for _,r in trials))
    return dict(controls=checks, scale=10**9, score_order=["bounded", "unconstrained_clipped", "fitted_constant"],
                words=WORDS, adjacent_prefix_probes=sum(bool(w) and w[:-1] in WORDS for w in WORDS),
                word_prefix_lookups=sum(bool(w) for w in WORDS),
                seed_27031=old, prospective=report, larger_sample=larger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment()
    if args.check:
        assert result == json.loads(Path(__file__).with_name("affine_result.json").read_text())
    print(json.dumps(result, indent=2))
