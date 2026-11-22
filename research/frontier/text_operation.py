"""Select one of the 16 binary updates by priced full-vocabulary causal log loss."""

import argparse
import hashlib
import json
from array import array
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path

import numpy as np
from partitions import fit_sparse_trigram, price
from text import FIT, TAU, VOCAB, Rows, git_json, log_bounds, outward, ratio_log, tape
from text_memory import CAL, GRID, fitted_masses, group_loss, quantize

CAL_END = FIT + CAL
BUY_END = CAL_END + CAL
CHOOSE_END = BUY_END + CAL
REPORT_END = CHOOSE_END + CAL
PREFIX_HASH = "56bdacca110726fcc7e22527b6b1db3faaee9d0ba1d7d956ed4598fb4888d4cc"
CHOOSE_HASH = "85c0816d0b46861c606e88361461c13c4782a8da5e5aeb58989d4b895779b59e"
REGISTRATION = "00cd1ce"


def state_trace(gate, symbols, initial=0):
    """trace[i] holds the pre-update state when current symbol i arrives."""
    table = tuple((gate >> k) & 1 for k in range(4))
    trace = bytearray(len(symbols))
    state = initial
    for i, bit in enumerate(symbols):
        trace[i] = state
        state = table[2 * state + bit]
    return np.frombuffer(trace, dtype=np.uint8), state


def counts(current, states, outcome, vocab):
    index = 4 * current.astype(np.int32) + 2 * states + outcome
    return np.bincount(index, minlength=4 * vocab).reshape(vocab, 2, 2)


def pack(gate, selected, rates):
    if not selected:
        return b""
    payload = bytearray([gate])
    for x in sorted(selected):
        word = x | (rates[x, 0] << 16) | (rates[x, 1] << 28)
        payload.extend(word.to_bytes(5, "little"))
    return bytes(payload)


def unpack(payload):
    return {
        word & 65535: ((word >> 16) & 4095, word >> 28)
        for i in range(1, len(payload), 5)
        for word in [int.from_bytes(payload[i : i + 5], "little")]
    }


def fit_gate(gate, cal, buy, base):
    eligible = np.flatnonzero(
        (cal.sum(axis=2) > 0).all(axis=1) & (buy.sum(axis=2) > 0).all(axis=1)
    )
    rates, observations = {}, {}
    for tok in eligible:
        x = int(tok)
        for z in (0, 1):
            zeros, ones = map(int, cal[x, z])
            rates[x, z] = quantize(
                ones * GRID + TAU * int(base[x]), (zeros + ones + TAU) * GRID
            )
            observations[x, z] = tuple(map(int, buy[x, z]))
    selected = price(observations, base.tolist(), rates, shared_bits=5)
    return pack(gate, selected, rates), len(eligible)


def histogram(rates, outcome):
    bins = np.bincount(np.where(outcome, rates, GRID - rates), minlength=GRID)
    return {int(k): int(bins[k]) for k in np.flatnonzero(bins)}


def apply_gate(payload, base, current, states, outcome):
    table = np.tile(base[:, None], (1, 2))
    for x, values in unpack(payload).items():
        table[x] = values
    return histogram(table[current, states], outcome)


@dataclass
class Score:
    hist: dict
    bits: int

    def __post_init__(self):
        lo, hi = group_loss(self.hist)
        ll, lh = log_bounds(2)
        self.priced = (256 * lo + self.bits * ll, 256 * hi + self.bits * lh)

    def beats(self, other):
        if self.priced[1] < other.priced[0]:
            return True
        if other.priced[1] < self.priced[0]:
            return False
        # Drop all common factors. This also resolves exact conjugate-gate ties.
        d = Counter(self.hist)
        d.subtract(other.hist)
        left = prod(k**n for k, n in d.items() if n > 0)
        right = prod(k ** (-n) for k, n in d.items() if n < 0)
        left = left**256 << max(0, other.bits - self.bits)
        right = right**256 << max(0, self.bits - other.bits)
        return left > right

    def report(self, within, n):
        group = group_loss(self.hist)
        return {
            "extra_bits": self.bits,
            "nll": outward(tuple(a + b for a, b in zip(within, group)), n),
            "priced_nll": outward(
                tuple(256 * a + b for a, b in zip(within, self.priced)), 256 * n
            ),
        }


def winner(scores, skip=None):
    chosen = None
    for key, score in scores.items():
        if key != skip and (chosen is None or score.beats(scores[chosen])):
            chosen = key
    return chosen


def shared_loss(rows, num, membership, data, lo, hi):
    within = [0, 0]
    raw = [0, 0]
    for (x, y), n in Counter(
        zip(data[lo - 1 : hi - 1], data[lo:hi], strict=True)
    ).items():
        q, den = rows.mass(x, y, True)
        mass = num[x] if membership[y] else den - num[x]
        for total, numerator in ((within, mass), (raw, den)):
            l, h = ratio_log(numerator, q)
            total[0] += n * l
            total[1] += n * h
    return within, raw


def vectors(data, membership):
    tokens = np.frombuffer(data, dtype=np.uint16)
    return tokens, np.frombuffer(membership, dtype=np.uint8)[tokens]


def fit_and_choose(data):
    assert len(data) == CHOOSE_END
    rows = Rows(data[:FIT], VOCAB, TAU)
    membership, numerator, fitted, _ = fitted_masses(
        rows, data[FIT:CAL_END], data[FIT - 1]
    )
    base = np.asarray(fitted, dtype=np.int32)
    tokens, bits = vectors(data, membership)
    current = tokens[BUY_END - 1 : CHOOSE_END - 1]
    outcome = bits[BUY_END:CHOOSE_END]
    within, _ = shared_loss(rows, numerator, membership, data, BUY_END, CHOOSE_END)
    selection = {"base": Score(histogram(base[current], outcome), 0)}
    installs, eligible, boundary = {}, {}, {}

    def block(states, lo, hi):
        return counts(
            tokens[lo - 1 : hi - 1], states[lo - 1 : hi - 1], bits[lo:hi], VOCAB
        )

    for gate in range(16):
        states, boundary[gate] = state_trace(gate, bits[:-1].tobytes())
        payload, eligible[gate] = fit_gate(
            gate, block(states, FIT, CAL_END), block(states, CAL_END, BUY_END), base
        )
        installs[gate] = payload
        charged = 8 * len(payload) - 3 if payload else 0
        hist = apply_gate(payload, base, current, states[BUY_END - 1 :], outcome)
        selection[gate] = Score(hist, charged)
    chosen = winner(selection)
    raw, work = fit_sparse_trigram(
        data[:BUY_END], membership, fitted, selection[chosen].bits
    )
    arms = {k: s.report(within, CAL) for k, s in selection.items()}
    for gate, payload in installs.items():
        arms[gate].update(
            eligible_rows=eligible[gate],
            installed_rows=len(payload) // 5,
            packed_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
        )
    work.update(
        smoothed_pair_entries=len(rows.pairs),
        frequent_types=sum(membership),
        observed_token_types=len(rows.base),
        smoothed_contexts=len(rows.outgoing),
        gate_training_transitions=16 * (CHOOSE_END - 1),
        gate_fit_target_visits=16 * 2 * CAL,
        gate_selection_target_visits=16 * CAL,
    )
    return (
        rows,
        numerator,
        membership,
        base,
        installs,
        boundary,
        chosen,
        raw,
        work,
        arms,
    )


def evaluate(data, fit):
    rows, numerator, membership, base, installs, boundary, chosen, raw, work, arms = fit
    within, plain = shared_loss(
        rows, numerator, membership, data, CHOOSE_END, REPORT_END
    )
    # Keep the t-2 raw token for the trigram and the t-1 token for the first forecast.
    tokens, bits = vectors(data[CHOOSE_END - 2 :], membership)
    current, previous, outcome = tokens[1:-1], tokens[:-2], bits[2:]
    test = {"base": Score(histogram(base[current], outcome), 0)}
    for gate, payload in installs.items():
        states, _ = state_trace(
            payload[0] if payload else gate, bits[1:-1].tobytes(), boundary[gate]
        )
        test[gate] = Score(
            apply_gate(payload, base, current, states, outcome),
            arms[gate]["extra_bits"],
        )
    hindsight = winner({g: test[g] for g in installs}, skip=chosen)
    trigram = np.fromiter(
        (
            raw.get((int(x), int(p)), base[x])
            for x, p in zip(current, previous, strict=True)
        ),
        dtype=np.int32,
        count=CAL,
    )
    raw_score = Score(histogram(trigram, outcome), work["installed_bits"])
    scores = {
        name: value.report(within, CAL)
        for name, value in (
            ("selected", test[chosen]),
            ("lagged_gate_10", test[10]),
            ("calibrated_base", test["base"]),
            ("raw_trigram", raw_score),
            ("best_other_gate_hindsight", test[hindsight]),
        )
    }
    scores["smoothed_successor"] = {"nll": outward(plain, CAL)}
    common = {
        "unigram_counts_bits": 32 * VOCAB,
        "observed_successor_rows_bits": sum(rows.bits(x) for x in rows.outgoing),
        "group_membership_bits": VOCAB,
        "calibrated_rates_bits": 12 * VOCAB,
        "cached_group_numerators_uint64_bits": 64 * VOCAB,
        "shared_last_token_bits": 16,
    }
    return {
        "registration": REGISTRATION,
        "train_prefix_sha256": PREFIX_HASH,
        "vocab": VOCAB,
        "blocks": [0, FIT, CAL_END, BUY_END, CHOOSE_END, REPORT_END],
        "charged_target_count": CAL,
        "chosen_gate": chosen,
        "other_gate_hindsight": hindsight,
        "acquisition": work,
        "common_logical_bits": common,
        "selection": {str(k): v for k, v in arms.items()},
        "reporting": scores,
        "selected_beats_lagged": test[chosen].beats(test[10]),
        "selected_beats_trigram": test[chosen].beats(raw_score),
        "registered_success": test[chosen].beats(test[10])
        and test[chosen].beats(raw_score),
    }


def audit():
    rows = Rows([0, 1, 1, 0, 2, 1, 0], 4, TAU)
    member, num, fit, _ = fitted_masses(rows, [0, 1], 1)
    base = np.array(fit, dtype=np.int32)
    rates = {(x, z): 17 + 100 * x + 77 * z for x in (0, 3) for z in (0, 1)}
    cases = 0
    for gate in range(16):
        payload = pack(gate, {0, 3}, rates)
        assert payload[0] == gate and unpack(payload) == {
            x: (rates[x, 0], rates[x, 1]) for x in (0, 3)
        }
        for pattern in product(range(4), repeat=4):
            data = array("H", pattern)
            tokens, groups = vectors(data, member)
            states, _ = state_trace(gate, groups[:-1].tobytes())
            hist = Counter()
            expected = Counter()
            for t in range(1, len(data)):
                # Direct composition on the prefix, independent of the streaming trace and binary packer.
                z = 0
                for x in data[: t - 1]:
                    z = int(bool(gate & (1 << (2 * z + member[x]))))
                x, y = data[t - 1 : t + 1]
                p = rates.get((x, z), fit[x])
                hist[p if member[y] else GRID - p] += 1
                expected[x, z, member[y]] += 1
            assert apply_gate(payload, base, tokens[:-1], states, groups[1:]) == hist
            actual = counts(tokens[:-1], states, groups[1:], 4)
            assert all(
                actual[x, z, b] == expected[x, z, b]
                for x, z, b in product(range(4), range(2), range(2))
            )
            cases += 1
    for x, z in product(range(4), range(2)):
        p = rates.get((x, z), fit[x])
        distribution = []
        for y in range(4):
            q, den = rows.mass(x, y, True)
            grouped = Fraction(q, num[x] if member[y] else den - num[x])
            distribution.append(grouped * Fraction(p if member[y] else GRID - p, GRID))
        assert sum(distribution) == 1 and all(k > 0 for k in distribution)
    # Equal exact likelihood with unequal histograms and a price difference of 256 bits.
    a, b, c = Score({2: 1, 4: 1}, 256), Score({1: 1, 4: 1}, 0), Score({2: 2}, 1)
    assert not a.beats(b) and not b.beats(a) and b.beats(c)
    return {"gate_history_pairs": cases, "normalized_full_distributions": 8}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = {"controls": audit()}
    if not args.controls_only:
        anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
        src = next(r for r in anchor["results"] if r["case"] == "ngram")["result"][
            "train_source"
        ]
        data = tape(
            dict(src, bytes_read=2 * REPORT_END, prefix_sha256=PREFIX_HASH),
            args.data_dir,
        )

        def digest(n):
            chunk = data[:n]
            import sys

            if sys.byteorder != "little":
                chunk.byteswap()
            return hashlib.sha256(chunk.tobytes()).hexdigest()

        assert (
            digest(BUY_END) == src["prefix_sha256"]
            and digest(CHOOSE_END) == CHOOSE_HASH
        )
        fit = fit_and_choose(data[:CHOOSE_END])
        result["text"] = evaluate(data, fit)
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf-8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
