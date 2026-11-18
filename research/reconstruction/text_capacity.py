"""Certify the whole frozen lag-copy simplex on the registered text suffix.

With no options, run exact synthetic controls. --text reads only the two
registered data prefixes. EM proposes a witness, integer bounds decide.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import ceil, floor, prod
from pathlib import Path
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.numerics import log_enclosure

GRID = 2**24
SCALE = 10**12


@lru_cache(maxsize=16384)
def scaled_log(numerator, denominator):
    """Outward bounds in integer trillionths of a nat."""
    interval = log_enclosure(F(numerator, denominator), terms=10, bit_limit=32768)
    return floor(SCALE*interval.lower), ceil(SCALE*interval.upper)


def lag_matches(tokens, first, width):
    if not width <= first < len(tokens):
        raise ValueError("all lag cells must precede every scored target")
    windows = np.lib.stride_tricks.sliding_window_view(tokens[first-width:], width+1)
    rows, cols = np.nonzero(windows[:, -2::-1] == windows[:, -1:])
    return rows, cols


def propose(base, denominator, rows, cols, width):
    n = len(base)
    weights = np.full(width+1, 0.5/width, dtype=np.float64)
    weights[0] = 0.5
    base = base.astype(np.float64)/denominator
    for _ in range(128):
        probabilities = weights[0]*base + np.bincount(rows, weights[1:][cols], minlength=n)
        if np.any(probabilities <= 0) or not np.all(np.isfinite(probabilities)):
            raise ValueError("invalid EM probability")
        inverse = 1/probabilities
        weights[0] *= np.dot(base, inverse)/n
        weights[1:] *= np.bincount(cols, inverse[rows], minlength=width)/n
        weights /= weights.sum()
    lag_units = [floor(float(w)*GRID) for w in weights[1:]]
    return [GRID-sum(lag_units), *lag_units]


def certify(base, denominator, rows, cols, units):
    n, grid = len(base), sum(units)
    if not (n and denominator > 0 and units[0] > 0 and min(units) >= 0):
        raise ValueError("positive base, normalized witness and nonempty score required")
    # Entries are 1-based lag addresses. No dense vocabulary probabilities
    # are needed because every source distribution is normalized by definition.
    matches = [[] for _ in range(n)]
    for row, col in zip(rows, cols, strict=True):
        matches[int(row)].append(int(col)+1)
    totals = [0]*len(units)
    loss_low = loss_high = absent_low = absent_high = absent = 0
    base_low = base_high = 0
    product_denominator = grid*denominator
    for raw_base, addresses in zip(base, matches, strict=True):
        b = int(raw_base)
        if not 0 < b <= denominator:
            raise ValueError("target base probability outside (0,1]")
        p = b*units[0] + denominator*sum(units[j] for j in addresses)
        lo, hi = scaled_log(product_denominator, p)
        loss_low += lo
        loss_high += hi
        totals[0] += (SCALE*grid*b + p-1)//p
        increment = (SCALE*product_denominator + p-1)//p
        for j in addresses:
            totals[j] += increment
        lo, hi = scaled_log(denominator, b)
        base_low += lo
        base_high += hi
        if not addresses:
            absent += 1
            absent_low += lo
            absent_high += hi
    scale = n*SCALE
    score_upper = F(max(totals), scale)
    assert score_upper >= 1
    _, penalty = scaled_log(score_upper.numerator, score_upper.denominator)
    return dict(lower=F(loss_low, scale)-F(penalty, SCALE), upper=F(loss_high, scale),
                score_upper=score_upper, absent=absent, matches=len(rows),
                support_low=F(absent_low, scale), support_high=F(absent_high, scale),
                base_low=F(base_low, scale), base_high=F(base_high, scale))


def controls():
    tapes = 0
    for tape in product(range(2), repeat=7):
        for width, first in ((2, 2), (3, 4)):
            rows, cols = lag_matches(np.array(tape), first, width)
            literal = [(t-first, j-1) for t in range(first, len(tape))
                       for j in range(1, width+1) if tape[t-j] == tape[t]]
            assert literal == list(zip(rows.tolist(), cols.tolist(), strict=True))
            tapes += 1
    # Four literal rows. All simplex predictors induce (p,p,p,1-p);
    # direct maximization of p^3(1-p) gives p=3/4 and optimum 27/256.
    base = np.ones(4, dtype=np.int64)
    rows = np.arange(4)
    cols = np.array([0, 0, 0, 1])
    witness = [2, 5, 1]
    exact = certify(base, 2, rows, cols, witness)
    optimum_log = log_enclosure(F(256, 27), terms=14, bit_limit=32768)
    assert exact["lower"] <= optimum_log.lower/4 <= optimum_log.upper/4 <= exact["upper"]
    assert exact["upper"]-exact["lower"] < F(1, 10**8)
    # Independently test the product inequality, including zero-likelihood
    # faces, for each pair of a strictly positive-base witness and a candidate.
    grid = [(a, b, 8-a-b) for a in range(9) for b in range(9-a)]
    matrix = [(F(1, 2), 1, 0)]*3 + [(F(1, 2), 0, 1)]
    def target_probs(vector):
        return [sum(a*w for a, w in zip(row, vector))/8 for row in matrix]
    pairs = 0
    for u in grid:
        if not u[0]:
            continue
        probabilities = target_probs(u)
        exact_ratio = max(sum(row[j]/p for row, p in zip(matrix, probabilities))/4 for j in range(3))
        bounded = certify(base, 2, rows, cols, u)
        assert exact_ratio <= bounded["score_upper"] <= exact_ratio + F(1, SCALE)
        for w in grid:
            assert prod(target_probs(w)) <= prod(probabilities)*exact_ratio**4
            pairs += 1
    em = propose(base, 2, rows, cols, 2)
    certified_em = certify(base, 2, rows, cols, em)
    assert certified_em["lower"] <= optimum_log.lower/4 <= optimum_log.upper/4 <= certified_em["upper"]
    assert certified_em["upper"]-certified_em["lower"] < F(1, 10**5)
    return dict(causal_tape_checks=tapes, exact_simplex_pairs=pairs, analytic_optimum_likelihood="27/256")


def outward(value, upper=False):
    integer = (ceil if upper else floor)(value*10**9)
    sign = "-" if integer < 0 else ""
    whole, remainder = divmod(abs(integer), 10**9)
    return f"{sign}{whole}.{remainder:09d}"


def text_result():
    sys.path.insert(0, str(ROOT/'scripts'))
    import run_text_baseline_anchor_a1 as original
    anchor = json.loads(original.JOURNAL.read_text(encoding="utf-8"))
    cases = {case["case"]: case for case in anchor["results"]}
    assert anchor["status"] == "COMPLETE_TEXT_BASELINE_ANCHOR_A1"
    assert cases["ngram"]["accepted_execution"] and cases["report"]["accepted_execution"]
    mkn, transformer = cases["ngram"]["result"], cases["report"]["result"]
    assert mkn["unigram"]["alpha"] == 1 and anchor["vocabulary"] == original.VOCAB == 50257
    assert (original.TRAIN, original.TUNE, original.REPORT) == (1048576, 4096, 16384)
    train, train_source = original.tape("train", original.TRAIN)
    tokens, report_source = original.tape("val", original.REPORT)
    for actual, expected in ((train_source, mkn["train_source"]),
                             (report_source, mkn["reporting_source"]),
                             (report_source, transformer["reporting_source"])):
        assert (actual["bytes_read"], actual["prefix_sha256"]) == (expected["bytes_read"], expected["prefix_sha256"])
    counts = np.bincount(train, minlength=original.VOCAB) + 1
    denominator = int(counts.sum())
    base = counts[tokens[original.TUNE:]]
    rows, cols = lag_matches(tokens, original.TUNE, 512)
    units = propose(base, denominator, rows, cols, 512)
    result = certify(base, denominator, rows, cols, units)
    refs = dict(transformer=F(str(transformer["score"]["report_mean_nll_nats"])),
                mkn5=F(str(mkn["report_mean_nll_nats"])),
                unigram=F(str(mkn["unigram"]["report_mean_nll_nats"])))
    assert result["base_low"] <= refs["unigram"] <= result["base_high"]
    comparisons = {}
    for name, loss in refs.items():
        comparisons[name] = ("whole class above recorded NLL" if result["lower"] > loss else
                             "a hindsight witness below recorded NLL" if result["upper"] < loss else
                             "unresolved by bracket")
    return dict(protocol="7355afc", training_tokens=len(train), scored_interval=[original.TUNE, original.REPORT],
                vocabulary=original.VOCAB, lag_cells=512, verified_original_prefix_identities=True,
                scored_positions=len(base), target_lag_matches=result["matches"],
                positions_without_copy=result["absent"], witness_grid=GRID, em_sweeps=128,
                max_column_score_upper=outward(result["score_upper"], True),
                fixed_class_infimum_nats=[outward(result["lower"]), outward(result["upper"], True)],
                contextual_support_lower_nats=outward(result["support_low"]),
                base_nats=[outward(result["base_low"]), outward(result["base_high"], True)],
                recorded_nats={name: float(loss) for name, loss in refs.items()}, comparisons=comparisons,
                scope="Hindsight class certificate on the previously exposed development suffix")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("this audit requires assertions")
    if args.output and args.output.exists():
        parser.error("output exists")
    result = {"synthetic_controls": controls()}
    if args.text:
        result["ordinary_text"] = text_result()
    encoded = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded+"\n")
    print(encoded)
