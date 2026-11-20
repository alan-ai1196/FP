"""Priced successor rows on the pinned original prefix, with integer-mass log bounds."""
from array import array
from collections import Counter, defaultdict
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import prod
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

ANCHOR = "a674dda8985be1dd316b102da4fa00a42c837819"
FIT = 786432
VOCAB = 50257
TAU = 64
SCALE = 10**18
CTX = Context(prec=60)


@lru_cache(maxsize=100000)
def log_bounds(n):
    if n == 1:
        return 0, 0
    if n <= 0:
        raise ValueError("positive integer mass required")
    logged = CTX.ln(Decimal(n))
    # Decimal ln is correctly rounded to nearest. Adjacent representables enclose the real log.
    low = CTX.multiply(CTX.next_minus(logged), Decimal(SCALE))
    high = CTX.multiply(CTX.next_plus(logged), Decimal(SCALE))
    return (int(low.to_integral_value(rounding=ROUND_FLOOR)),
            int(high.to_integral_value(rounding=ROUND_CEILING)))


def ratio_log(a, b):
    la, ha = log_bounds(a)
    lb, hb = log_bounds(b)
    return la - hb, ha - lb


def outward(bounds, n):
    lo, hi = bounds
    denominator = SCALE*n
    units = (lo*10**9 // denominator, -((-hi*10**9) // denominator))
    return [f"{u//10**9}.{u%10**9:09}" for u in units]  # losses here are nonnegative


class Rows:
    def __init__(self, tokens, vocab, tau):
        self.vocab, self.tau = vocab, tau
        self.base = Counter(tokens)
        self.den = len(tokens) + vocab
        self.pairs = Counter(zip(tokens[:-1], tokens[1:]))
        self.outgoing, self.degrees = Counter(), Counter()
        for (x, _), n in self.pairs.items():
            self.outgoing[x] += n
            self.degrees[x] += 1

    def mass(self, x, y, use):
        base = self.base[y] + 1
        if not use:
            return base, self.den
        return (self.pairs[x, y]*self.den + self.tau*base,
                self.den*(self.outgoing[x]+self.tau))

    def improvement(self, x, y):
        base = self.base[y] + 1
        return self.pairs[x, y]*self.den + self.tau*base, (self.outgoing[x]+self.tau)*base

    def bits(self, x):
        return 64 + 48*self.degrees[x]


def gate(rows, observed):
    # Aggregate only after all gate observations. Frozen row likelihoods commute under multiplication.
    by_x = defaultdict(list)
    for (x, y), n in observed.items():
        if rows.outgoing[x]:
            by_x[x].append((y, n))
    chosen = set()
    fallbacks = 0
    for x, entries in by_x.items():
        lo = hi = 0
        for y, n in entries:
            l, h = ratio_log(*rows.improvement(x, y))
            lo += n*l
            hi += n*h
        price_lo, price_hi = (v*rows.bits(x) for v in log_bounds(2))
        if 256*lo > price_hi:
            chosen.add(x)
        elif 256*hi >= price_lo:
            fallbacks += 1
            odds = prod(F(*rows.improvement(x, y))**n for y, n in entries)
            if odds**256 > 2**rows.bits(x):
                chosen.add(x)
    return chosen, fallbacks


def audit_gate():
    checked = 0
    for fit in product(range(2), repeat=4):
        rows = Rows(fit, 2, 2)
        for val in product(range(2), repeat=3):
            hist = Counter(zip((fit[-1], *val[:-1]), val))
            chosen, _ = gate(rows, hist)
            def wealth(subset):
                advantage = prod(F(*rows.improvement(x, y))**n for (x, y), n in hist.items() if x in subset)
                return advantage**256 / 2**sum(rows.bits(x) for x in subset)
            # Include overspending on unobserved rows in this exhaustive independent control.
            choices = [set(), {0}, {1}, {0, 1}]
            assert wealth(chosen) == max(wealth(s) for s in choices)
            checked += 1
    bad = Rows((0, 0, 1, 1), 2, 2)
    assert F(*bad.improvement(1, 1)) > 1 and F(*bad.improvement(1, 0)) < 1
    return checked


def git_json(path):
    root = Path(__file__).resolve().parents[2]
    return json.loads(subprocess.check_output(["git", "-C", str(root), "show", f"{ANCHOR}:{path}"]))


def tape(source, directory):
    path = (directory / Path(source["path"].replace("\\", "/")).name) if directory else Path(source["path"])
    with path.open("rb") as f:
        before = os.fstat(f.fileno())
        raw = f.read(source["bytes_read"])
        after = os.fstat(f.fileno())
    if (before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns
            or before.st_size != source["file_bytes"] or len(raw) != source["bytes_read"]
            or hashlib.sha256(raw).hexdigest() != source["prefix_sha256"]):
        raise ValueError("corpus identity mismatch")
    values = array("H")
    if values.itemsize != 2:
        raise ValueError("reader requires 16-bit unsigned short")
    values.frombytes(raw)
    if sys.byteorder != "little":
        values.byteswap()
    if max(values) >= VOCAB:
        raise ValueError("symbol outside registered vocabulary")
    return values


def load_prefixes(directory):
    j = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    assert j["vocabulary"] == VOCAB and j["status"] == "COMPLETE_TEXT_BASELINE_ANCHOR_A1"
    first = next(entry for entry in j["results"] if entry["case"] == "ngram")
    assert first["accepted_execution"]
    ref = first["result"]
    train = tape(ref["train_source"], directory)
    val = tape(ref["reporting_source"], directory)
    assert (len(train), len(val)) == (1048576, 16384)
    return train, val, ref


def original(directory):
    historical = git_json("research/reconstruction/text_capacity_result.json")["ordinary_text"]
    train, val, ref = load_prefixes(directory)
    rows = Rows(train[:FIT], VOCAB, TAU)
    observations = Counter(zip(train[FIT-1:-1], train[FIT:]))
    chosen, fallbacks = gate(rows, observations)
    scored = Counter(zip(val[4095:-1], val[4096:]))
    positions = sum(scored.values())
    assert positions == historical["scored_positions"] == 12288
    results = {}
    for name, selected in [("base", set()), ("priced", chosen), ("all", set(rows.outgoing))]:
        lo = hi = 0
        for (x, y), n in scored.items():
            num, den = rows.mass(x, y, x in selected)
            l, h = ratio_log(den, num)
            lo += n*l
            hi += n*h
        bounds = outward((lo, hi), positions)
        lower, upper = map(F, bounds)
        results[name] = dict(rows=len(selected), distinct_entries=sum(rows.degrees[x] for x in selected),
                             row_payload_bits=sum(rows.bits(x) for x in selected), nll=bounds,
                             below_fixed_simplex=upper < F(historical["fixed_class_infimum_nats"][0]),
                             above_mkn=lower > F(str(historical["recorded_nats"]["mkn5"])),
                             above_transformer=lower > F(str(historical["recorded_nats"]["transformer"])))
    return dict(registration="477c05a", train_prefix_sha256=ref["train_source"]["prefix_sha256"],
                val_prefix_sha256=ref["reporting_source"]["prefix_sha256"], vocab=VOCAB,
                fit_tokens=FIT, fitted_pairs=FIT-1, gate_tokens=sum(observations.values()),
                gate_distinct_pairs=len(observations), exact_price_tie_fallbacks=fallbacks,
                base_payload_bits=32*VOCAB, score_positions=positions, arms=results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    out = {"exhaustive_small_gates": audit_gate()}
    if args.text:
        out["original_text"] = original(args.data_dir)
    if args.check:
        expected = json.loads(Path(__file__).with_name("text_result.json").read_text())
        assert out == {key: expected[key] for key in out}
    print(json.dumps(out, indent=2))
