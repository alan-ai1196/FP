"""Test what one learned scalar memory can change on the registered full-vocabulary stream."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path
import argparse
import json

from text import FIT, SCALE, TAU, VOCAB, Rows, git_json, load_prefixes, log_bounds, outward, ratio_log

GRID = 4096
CAL = 131072
OPTIONS = sorted(product(range(-2, 3), repeat=2), key=lambda pair: (sum(map(abs, pair)), pair))


def quantize(num, den):
    return max(1, min(GRID-1, (2*GRID*num+den)//(2*den)))


def transition(base, slope, old):
    memory = old if slope >= 0 else GRID-old
    return ((4-abs(slope))*base + abs(slope)*memory + 2)//4


def charged(slopes, recurrent):
    active = sum(s != 0 for s in slopes)
    return 3*active + (12 if active and recurrent else 0)


def masses(events, slopes, recurrent, initial, skip=0):
    histogram = [0]*GRID
    state = initial
    for i, (base, group, outcome) in enumerate(events):
        state = transition(base, slopes[group], state if recurrent else initial)
        if i >= skip:
            histogram[state if outcome else GRID-state] += 1
    return {k: n for k,n in enumerate(histogram) if n}


def group_loss(hist):
    lo = hi = 0
    for k,n in hist.items():
        l, h = ratio_log(GRID, k)
        lo += n*l
        hi += n*h
    return lo, hi


def quality(hist):
    return prod(k**n for k,n in hist.items())


def select(events, recurrent, initial):
    best = None
    best_hist = best_bounds = None
    nonzero = []
    exact = 0
    for slopes in OPTIONS:
        hist = masses(events, slopes, recurrent, initial)
        bits = charged(slopes, recurrent)
        raw_bounds = group_loss(hist)
        if slopes == (0,0):
            zero = raw_bounds
        else:
            nonzero.append(raw_bounds)
        bounds = tuple(a+bits*b for a,b in zip(raw_bounds, log_bounds(2), strict=True))
        take = best is None or bounds[1] < best_bounds[0]
        if best is not None and not take and bounds[0] <= best_bounds[1]:
            exact += 1
            take = (quality(hist) << charged(best, recurrent)) > (quality(best_hist) << bits)
        if take:
            best, best_hist, best_bounds = slopes, hist, bounds
    low = min(l for l,_ in nonzero) - zero[1]
    high = min(h for _,h in nonzero) - zero[0]
    denominator = len(events)*SCALE
    raw_excess = [low*10**9//denominator, -((-high*10**9)//denominator)]
    return best, exact, raw_excess


def frequency_mask(rows):
    order = sorted(rows.base, key=lambda x: (-rows.base[x], x))
    member = bytearray(rows.vocab)
    cumulative = 0
    for x in order:
        member[x] = 1
        cumulative += rows.base[x]
        if 2*cumulative >= rows.den-rows.vocab:
            break
    return member


def fitted_masses(rows, calibrate, previous, member=None):
    member = frequency_mask(rows) if member is None else member
    base_group = sum(rows.base[y]+1 for y,flag in enumerate(member) if flag)
    positive = Counter()
    for (x,y), count in rows.pairs.items():
        if member[y]:
            positive[x] += count
    totals = Counter()
    hits = Counter()
    for y in calibrate:
        totals[previous] += 1
        hits[previous] += member[y]
        previous = y
    group_num = []
    fitted = []
    for x in range(rows.vocab):
        num = positive[x]*rows.den + rows.tau*base_group
        den = (rows.outgoing[x]+rows.tau)*rows.den
        group_num.append(num)
        fitted.append(quantize(hits[x]*den + TAU*num, (totals[x]+TAU)*den))
    return member, group_num, fitted, quantize(base_group, rows.den)


def entropy_bound(hist):
    # infimum over a fixed group mass per last token, including boundary values.
    lo = hi = 0
    for bins in hist.values():
        for n in bins:
            if n:
                l, h = ratio_log(sum(bins), n)
                lo += n*l
                hi += n*h
    return lo, hi


def small_checks():
    n = 0
    init = GRID//2-53
    for targets in product((0,1), repeat=3):
        events = [(321+973*i, i%2, y) for i,y in enumerate(targets)]
        for recurrent in (False, True):
            best, _, _ = select(events, recurrent, init)
            scores = {}
            for slopes in OPTIONS:
                p = F(init, GRID)
                likelihood = F(1)
                for b,g,y in events:
                    s = F(slopes[g], 4)
                    z = p if recurrent else F(init, GRID)
                    h = z if s >= 0 else 1-z
                    raw = (1-abs(s))*F(b,GRID) + abs(s)*h
                    p = F(quantize(raw.numerator, raw.denominator),GRID)
                    likelihood *= p if y else 1-p
                scores[slopes] = likelihood / 2**charged(slopes,recurrent)
            assert best == max(OPTIONS, key=scores.get)
            n += len(OPTIONS)
    rows = Rows([0,0,1,2,1,0], 4, TAU)
    mask, gnum, _, _ = fitted_masses(rows, [1,0], 0)
    for x in range(4):
        probs = [F(*rows.mass(x,y,True)) for y in range(4)]
        target = sum(p for y,p in enumerate(probs) if mask[y])
        assert target == F(gnum[x], rows.den*(rows.outgoing[x]+rows.tau))
        for z in (F(1,GRID), F(1,3), F(GRID-1,GRID)):
            normalized = [p*(z/target if mask[y] else (1-z)/(1-target)) for y,p in enumerate(probs)]
            assert sum(normalized)==1 and all(p>0 for p in normalized)
    return n


def original(directory):
    train, val, source = load_prefixes(directory)
    rows = Rows(train[:FIT], VOCAB, TAU)
    boundary = FIT+CAL
    member, group_numerator, base, initial = fitted_masses(rows, train[FIT:boundary], train[FIT-1])
    def encode(xs, ys):
        return [(base[x], member[x], member[y]) for x,y in zip(xs,ys,strict=True)]
    gate = encode(train[boundary-1:-1], train[boundary:])
    report = encode(val[:-1], val[1:])
    skip = 4095
    count = len(report)-skip
    assert len(gate) == CAL and count == 12288
    recur, recur_ties, recurrent_excess = select(gate, True, initial)
    overwrite, static_ties, overwrite_excess = select(gate, False, initial)
    within_lo = within_hi = raw_lo = raw_hi = 0
    empirical = {}
    for (x,y), n in Counter(zip(val[4095:-1], val[4096:], strict=True)).items():
        num, den = rows.mass(x,y,True)
        mass = group_numerator[x] if member[y] else den-group_numerator[x]
        l, h = ratio_log(mass,num)
        within_lo += n*l
        within_hi += n*h
        l, h = ratio_log(den,num)
        raw_lo += n*l
        raw_hi += n*h
        empirical.setdefault(x,[0,0])[member[y]] += n
    scores = {"original_full_bank": outward((raw_lo,raw_hi),count),
              "correct_group_revealed": outward((within_lo,within_hi),count)}
    l,h = entropy_bound(empirical)
    scores["hindsight_overwrite"] = outward((within_lo+l,within_hi+h), count)
    for name,slopes,rec in (("calibrated_row",(0,0),False),("selected_overwrite",overwrite,False),
                             ("selected_recurrent",recur,True)):
        l,h = group_loss(masses(report,slopes,rec,initial,skip))
        scores[name] = outward((within_lo+l,within_hi+h),count)
    first = {}
    varied = set()
    state = initial
    for i,(b,g,_) in enumerate(report):
        state = transition(b,recur[g],state)
        if i >= skip:
            x = val[i]
            if first.setdefault(x,state) != state:
                varied.add(x)
    ref = git_json("research/reconstruction/text_capacity_result.json")["ordinary_text"]["recorded_nats"]
    comparisons = {key: F(scores["correct_group_revealed"][0]) > F(str(ref[key]))
                   for key in ("mkn5","transformer")}
    success = (bool(varied) and all(F(scores["selected_recurrent"][1]) < F(scores[k][0])
                                   for k in ("original_full_bank","selected_overwrite")))
    return dict(registration="2a89cc5", fit_tokens=FIT, calibration_targets=CAL, gate_targets=len(gate),
                train_prefix_sha256=source["train_source"]["prefix_sha256"],
                val_prefix_sha256=source["reporting_source"]["prefix_sha256"], scored_targets=count,
                group_types=sum(member), global_mass_grid_index=initial, denominator=GRID,
                fit_pair_entries=len(rows.pairs), candidate_sweeps=2*len(OPTIONS),
                gate_transition_evaluations=len(gate)*2*len(OPTIONS), recurrent_quarter_slopes=list(recur),
                overwrite_quarter_slopes=list(overwrite), recurrent_fee_bits=charged(recur,True),
                overwrite_fee_bits=charged(overwrite,False), exact_gate_comparisons=recur_ties+static_ties,
                minimum_nonzero_unpriced_gate_excess_nanonats=dict(recurrent=recurrent_excess,overwrite=overwrite_excess),
                distinct_last_tokens=len(first), last_tokens_with_different_states=len(varied),
                nll_nats=scores, historical_below_oracle_floor=comparisons, registered_success=success)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = {"independent_policy_checks": small_checks()}
    if args.text:
        result["original_text"] = original(args.data_dir)
    if args.check:
        expected = json.loads(Path(__file__).with_name("text_memory_result.json").read_text())
        assert result == {k: expected[k] for k in result}
    print(json.dumps(result, indent=2))
