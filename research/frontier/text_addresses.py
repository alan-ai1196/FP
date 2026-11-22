"""Fit a token address from the observed log-loss difference of two full-vocabulary readouts."""

import argparse
import hashlib
import json
import struct
import sys
from array import array
from dataclasses import dataclass, replace
from itertools import product
from math import fsum, log
from pathlib import Path

import numpy as np
from packed_trigram import Trigram, knapsack, lookup, pair_ids
from text import FIT, TAU, VOCAB, Rows, git_json, tape
from text_memory import CAL, frequency_mask
from text_statistic import REPORT_HASH as ADDRESS_HASH

READOUT_END = FIT + 2 * CAL
ADDRESS_END = READOUT_END + 4 * CAL
SELECT_END = ADDRESS_END + CAL
REPORT_END = SELECT_END + CAL
SELECT_HASH = "786fa17c12238c81d60a7ad450122b689eb774b6a03928aced91173913ceee90"
REPORT_HASH = "582ad8f02059dab29ec766794dd72cf8f686255dea64904cb42acbff5fed7fbc"
TOTAL_MASS = 1 << 24
RENT = log(2) / 256
HEADER = struct.Struct("<HBBHHIIII")
assert HEADER.size == 24


@dataclass
class Observations:
    history: np.ndarray
    query: np.ndarray
    target: np.ndarray
    category: np.ndarray
    refinement: np.ndarray
    seen: np.ndarray
    outgoing: np.ndarray
    base: np.ndarray

    def readout(self, masses):
        backoff = masses[self.category] / TOTAL_MASS * self.refinement
        return (self.seen + TAU * backoff) / (self.outgoing + TAU)


class Common:
    def __init__(self, data, vocab, named):
        self.vocab = vocab
        self.rows = Rows(data, vocab, TAU)
        self.counts = np.array(
            [self.rows.base[i] for i in range(vocab)], dtype=np.int64
        )
        self.outgoing = np.array(
            [self.rows.outgoing[i] for i in range(vocab)], dtype=np.int64
        )
        self.unigram = self.counts + 1
        ranking = np.lexsort((np.arange(vocab), -self.counts))
        self.top = np.sort(ranking[:named])
        self.category = np.full(vocab, named, dtype=np.int32)
        self.category[self.top] = np.arange(named)
        self.tail = int(self.unigram[self.category == named].sum())
        self.prior = np.append(self.unigram[self.top], self.tail) / self.rows.den
        self.seed = np.frombuffer(frequency_mask(self.rows), dtype=np.uint8)
        last = ranking[int(self.seed.sum()) - 1]
        self.boundary = int(self.counts[last]), int(last)
        assert np.array_equal(self.seed, self.default(2))
        keys = np.fromiter(
            (int(a) << 16 | int(b) for a, b in self.rows.pairs), dtype=np.uint64
        )
        order = np.argsort(keys)
        self.keys = keys[order]
        self.values = np.fromiter(self.rows.pairs.values(), dtype=np.uint32)[order]

    def default(self, mode):
        if mode == 2:
            cutoff, last = self.boundary
            return (
                (self.counts > cutoff)
                | ((self.counts == cutoff) & (np.arange(self.vocab) <= last))
            ).astype(np.uint8)
        return np.full(self.vocab, mode, dtype=np.uint8)

    def observe(self, tokens, start, stop):
        before = tokens[start - 2 : stop - 2]
        q = tokens[start - 1 : stop - 1]
        y = tokens[start:stop]
        seen = lookup(self.keys, self.values, pair_ids(q, y))
        c = self.category[y]
        refinement = np.where(c == len(self.top), self.unigram[y] / self.tail, 1.0)
        outgoing = self.outgoing[q]
        base = (seen + TAU * self.unigram[y] / self.rows.den) / (outgoing + TAU)
        return Observations(before, q, y, c, refinement, seen, outgoing, base)


def quantized(masses):
    qty = masses * (TOTAL_MASS - len(masses))
    whole = np.floor(qty).astype(np.int32)
    order = np.lexsort((np.arange(len(whole)), -(qty - whole)))
    whole += 1
    whole[order[: TOTAL_MASS - int(whole.sum())]] += 1
    assert whole.min() >= 1 and whole.sum() == TOTAL_MASS
    return whole


def em_readouts(obs, states, count, prior):
    categories = len(prior)
    parameters = np.tile(prior, (count, 1))
    indices = states.astype(np.int32) * categories + obs.category

    def loss():
        mass = parameters[states, obs.category] * obs.refinement
        term = -np.log((obs.seen + TAU * mass) / (obs.outgoing + TAU)).sum()
        return float(term - 2048 * (prior * np.log(parameters)).sum())

    initial = previous = loss()
    for _ in range(16):
        part = TAU * parameters[states, obs.category] * obs.refinement
        credit = part / (obs.seen + part)
        totals = np.bincount(
            indices, weights=credit, minlength=count * categories
        ).reshape(count, categories)
        totals += 2048 * prior
        parameters = totals / totals.sum(axis=1, keepdims=True)
        current = loss()
        assert current <= previous + 1e-7
        previous = current
    return np.stack([quantized(row) for row in parameters]), [
        round(initial, 6),
        round(previous, 6),
    ]


def serialize(common, masses, route=None):
    ids = b""
    mode = fallback = number = 0
    if route is not None and np.all(route == route[0]):
        masses = masses[[int(route[0])]]
        route = None
    if route is not None:
        options = []
        for default in (0, 1, 2):
            exceptions = np.flatnonzero(route != common.default(default))
            options.append(
                (1, default, len(exceptions), exceptions.astype("<u2").tobytes())
            )
        options.append((2, 0, 0, np.packbits(route, bitorder="little").tobytes()))
        mode, fallback, number, ids = min(options, key=lambda a: len(a[3]))
    weights = len(masses)
    assert weights == (2 if mode else 1)
    cutoff, last = common.boundary
    result = bytearray(
        HEADER.pack(
            len(common.top),
            mode,
            fallback,
            number,
            last,
            cutoff,
            common.tail,
            int(masses[0, -1]),
            int(masses[-1, -1]),
        )
    )
    for j, tok in enumerate(common.top):
        result.extend(int(tok).to_bytes(2, "little"))
        for row in masses:
            result.extend(int(row[j]).to_bytes(3, "little"))
    result.extend(ids)
    return bytes(result)


def deserialize(payload, counts):
    count, mode, fallback, number, last, cutoff, tail, left, right = HEADER.unpack_from(
        payload
    )
    columns = 2 if mode else 1
    pos = HEADER.size
    top, masses = [], np.empty((columns, count + 1), dtype=np.int32)
    masses[0, -1], masses[-1, -1] = left, right
    for j in range(count):
        top.append(int.from_bytes(payload[pos : pos + 2], "little"))
        pos += 2
        for row in masses:
            row[j] = int.from_bytes(payload[pos : pos + 3], "little")
            pos += 3
    assert np.all(masses.sum(axis=1) == TOTAL_MASS)
    if mode == 2:
        routing = np.unpackbits(
            np.frombuffer(payload[pos:], dtype=np.uint8), bitorder="little"
        )[: len(counts)]
    elif mode == 1:
        routing = np.full(len(counts), fallback, dtype=np.uint8)
        if fallback == 2:
            routing = (
                (counts > cutoff)
                | ((counts == cutoff) & (np.arange(len(counts)) <= last))
            ).astype(np.uint8)
        changes = np.frombuffer(payload[pos:], dtype="<u2")
        assert len(changes) == number
        routing[changes] ^= 1
    else:
        assert pos == len(payload)
        routing = np.zeros(len(counts), dtype=np.uint8)
    return top, masses, routing, tail, mode


def measure(loss, bits, n):
    return {
        "extra_bits": int(bits),
        "nll": round(float(loss) / n, 10),
        "priced_nll": round((float(loss) + RENT * int(bits)) / n, 10),
    }


@dataclass
class Address:
    route: np.ndarray
    payload: bytes
    parameters: tuple

    @property
    def bits(self):
        return 8 * (len(self.payload) + int(self.payload[2] != 0))

    def loss(self, obs, log_zero, gain):
        return float(-log_zero.sum() - gain[self.route[obs.history].astype(bool)].sum())


def learn_routes(common, masses, obs, weighted):
    actual_gain = np.log(obs.readout(masses[1]) / obs.readout(masses[0]))
    contrast = (
        actual_gain
        if weighted
        else np.log(masses[1, obs.category] / masses[0, obs.category])
    )
    evidence = np.bincount(obs.history, weights=contrast, minlength=common.vocab)
    magnitude = np.sqrt(
        np.bincount(obs.history, weights=contrast**2, minlength=common.vocab)
    )
    routes = {}
    for beta, storage, default in product((0, 1, 2), ("sparse", "dense"), (0, 1, 2)):
        initial = common.default(default)
        advantage = np.where(initial, -evidence, evidence)
        price = 16 * RENT * len(obs.target) / CAL if storage == "sparse" else 0
        route = initial ^ (advantage > price + beta * magnitude)
        key = route.tobytes()
        if key not in routes:
            routes[key] = Address(
                route, serialize(common, masses, route), (beta, storage, default)
            )
    return list(routes.values())


def routed_scores(obs, masses):
    one, two = (obs.readout(row) for row in masses)
    return np.log(one), np.log(two / one)


def choose_routes(candidates, obs, log_zero, gain):
    models = [(a.loss(obs, log_zero, gain), a) for a in candidates]
    return min(models, key=lambda item: item[0] + RENT * item[1].bits)


@dataclass
class CalibratedTrigram:
    masses: np.ndarray
    tau: int
    active: np.ndarray
    payload: bytes
    bits: int

    def observations(self, obs):
        return replace(obs, base=obs.readout(self.masses[0]))

    def losses(self, trigram, obs):
        calibrated = self.observations(obs)
        row, found, gain = trigram.combined(calibrated, self.tau)
        retained = np.zeros(len(trigram.pairs), dtype=bool)
        retained[self.active] = True
        return -np.log(calibrated.base) - np.where(found & retained[row], gain, 0)


def fit_calibrated_trigram(common, tables, trigram, purchase, validation, cap):
    best = None
    for name, mass in tables:
        base = serialize(common, mass)
        fit_obs = replace(purchase, base=purchase.readout(mass[0]))
        val_obs = replace(validation, base=validation.readout(mass[0]))
        for tau in (4, 16, 64):
            rows, _ = trigram.purchase(
                fit_obs, tau, cap - len(base), RENT * len(purchase.target) / CAL
            )
            bits = 8 * len(base) + trigram.bits(rows)
            loss = trigram.score(val_obs, tau, rows)
            value = loss + RENT * bits
            if best is None or value < best[0]:
                best = value, loss, name, mass, base, tau, rows, bits
    _, loss, name, mass, base, tau, rows, bits = best
    payload = base + trigram.pack(tau, rows)
    assert 8 * (len(payload) + 2 * bool(len(rows))) == bits <= 8 * cap
    model = CalibratedTrigram(mass, tau, rows, payload, bits)
    details = {
        "base": name,
        "tau": tau,
        "rows": len(rows),
        "successors": int(trigram.degree[rows].sum()),
        "bytes_including_live_state": bits // 8,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "selection": measure(loss, bits, CAL),
    }
    return model, details


def fit(prefix):
    assert len(prefix) == SELECT_END
    common = Common(prefix[:FIT], VOCAB, 512)
    tokens = np.frombuffer(prefix, dtype=np.uint16)
    read = common.observe(tokens, FIT, READOUT_END)
    pair, pair_trace = em_readouts(read, common.seed[read.history], 2, common.prior)
    pooled, pool_trace = em_readouts(
        read, np.zeros(len(read.target), dtype=np.uint8), 1, common.prior
    )
    purchase = common.observe(tokens, READOUT_END, ADDRESS_END)
    validation = common.observe(tokens, ADDRESS_END, SELECT_END)
    log_zero, gain = routed_scores(validation, pair)
    routes = {}
    selection = {}
    candidates = {}
    for name, weighted in (("conditional", True), ("marginal", False)):
        choices = learn_routes(common, pair, purchase, weighted)
        loss, a = choose_routes(choices, validation, log_zero, gain)
        candidates[name] = len(choices)
        routes[name] = a
        selection[name] = measure(loss, a.bits, CAL)
    seed = Address(common.seed, serialize(common, pair, common.seed), ())
    routes["seed"] = seed
    selection["seed"] = measure(seed.loss(validation, log_zero, gain), seed.bits, CAL)
    constants = []
    tables = (
        ("pooled", pooled),
        ("row_zero", pair[:1]),
        ("row_one", pair[1:]),
    )
    for name, masses in tables:
        bits = 8 * len(serialize(common, masses))
        loss = float(-np.log(validation.readout(masses[0])).sum())
        constants.append((loss + RENT * bits, loss, bits, name, masses))
    _, loss, bits, which, constant = min(constants, key=lambda x: x[0])
    selection["constant"] = measure(loss, bits, CAL)
    selection["bigram"] = measure(-np.log(validation.base).sum(), 0, CAL)
    trigram = Trigram(tokens[:READOUT_END])
    cap = routes["conditional"].bits // 8
    raw, full, details = [], [], {}
    for tau in (4, 16, 64):
        chosen, stats = trigram.purchase(
            purchase, tau, cap, RENT * len(purchase.target) / CAL
        )
        loss = trigram.score(validation, tau, chosen)
        bits = trigram.bits(chosen)
        raw.append((loss + RENT * bits, loss, bits, tau, chosen))
        full.append((trigram.score(validation, tau), tau))
        details[str(tau)] = stats
    _, loss, bits, tau, active = min(raw, key=lambda x: x[0])
    full_loss, full_tau = min(full)
    full_bits = 8 * (11 + 12 * len(trigram.pairs) + 6 * len(trigram.keys))
    selection["matched_trigram"] = measure(loss, bits, CAL)
    selection["unpruned_trigram"] = measure(full_loss, full_bits, CAL)
    information = {
        "em_penalized_nll_before_after": {"pair": pair_trace, "pooled": pool_trace},
        "distinct_candidate_maps": candidates,
        "chosen_constant": which,
        "raw_purchase": details,
        "raw_tau": tau,
        "full_tau": full_tau,
        "training_bigram_pairs": len(common.keys),
        "training_trigram_pairs": len(trigram.pairs),
        "training_trigram_triples": len(trigram.keys),
        "conditional_cap_bytes": cap,
        "selection": selection,
    }
    hybrid, hybrid_info = fit_calibrated_trigram(
        common, tables, trigram, purchase, validation, cap
    )
    return (
        common,
        pair,
        constant,
        routes,
        trigram,
        active,
        information,
        hybrid,
        hybrid_info,
    )


def replay(payload, common, data, lo, hi):
    """Score raw tokens from serialized readouts while advancing one history byte."""
    top, masses, route, tail, mode = deserialize(payload, common.counts)
    category = {int(x): j for j, x in enumerate(top)}
    initial = route[data[lo - 2]]
    state, last = int(initial), int(data[lo - 1])
    log_terms = []
    for i in range(lo, hi):
        y = int(data[i])
        c = category.get(y, len(top))
        numerator = int(masses[state, c])
        denominator = TOTAL_MASS
        if c == len(top):
            numerator *= int(common.unigram[y])
            denominator *= tail
        count = common.rows.pairs[last, y]
        num = count * denominator + TAU * numerator
        den = (common.rows.outgoing[last] + TAU) * denominator
        log_terms.append(log(den / num))
        state, last = int(route[last]) if mode else 0, y
    return fsum(log_terms)


def score(prefix, trained):
    common, pair, constant, routes, trigram, active, info, hybrid, hybrid_info = trained
    obs = common.observe(np.frombuffer(prefix, dtype=np.uint16), SELECT_END, REPORT_END)
    log_zero, gain = routed_scores(obs, pair)
    report, descriptions = {}, {}
    for name, a in routes.items():
        loss = a.loss(obs, log_zero, gain)
        assert (
            abs(replay(a.payload, common, prefix, SELECT_END, REPORT_END) - loss) < 1e-7
        )
        report[name] = measure(loss, a.bits, CAL)
        descriptions[name] = {
            "fit_parameters": list(a.parameters),
            "selected_types": int(a.route.sum()),
            "changed_seed_types": int(np.count_nonzero(a.route != common.seed)),
            "changed_reporting_targets": int(
                np.count_nonzero(a.route[obs.history] != common.seed[obs.history])
            ),
            "encoding": ("constant", "sparse", "dense")[a.payload[2]],
            "payload_bytes": len(a.payload),
            "sha256": hashlib.sha256(a.payload).hexdigest(),
        }
    payload = serialize(common, constant)
    loss = float(-np.log(obs.readout(constant[0])).sum())
    assert abs(replay(payload, common, prefix, SELECT_END, REPORT_END) - loss) < 1e-7
    report["constant"] = measure(loss, 8 * len(payload), CAL)
    report["bigram"] = measure(-np.log(obs.base).sum(), 0, CAL)
    tau = info["raw_tau"]
    raw_payload = trigram.pack(tau, active)
    raw_bits = trigram.bits(active)
    raw_loss = trigram.score(obs, tau, active)
    assert raw_bits <= routes["conditional"].bits
    report["matched_trigram"] = measure(raw_loss, raw_bits, CAL)
    report["unpruned_trigram"] = measure(
        trigram.score(obs, info["full_tau"]),
        info["selection"]["unpruned_trigram"]["extra_bits"],
        CAL,
    )
    target = report["conditional"]["priced_nll"]
    beats = {
        name: target < arm["priced_nll"]
        for name, arm in report.items()
        if name != "conditional"
    }
    hybrid_loss = float(hybrid.losses(trigram, obs).sum())
    assert (
        abs(
            hybrid_loss
            - trigram.score(hybrid.observations(obs), hybrid.tau, hybrid.active)
        )
        < 1e-7
    )
    return {
        "registration": "afc26fc",
        "vocabulary": VOCAB,
        "named_outputs": 512,
        "data_block_ends": [FIT, READOUT_END, ADDRESS_END, SELECT_END, REPORT_END],
        "prefix_sha256": {
            "address": ADDRESS_HASH,
            "selection": SELECT_HASH,
            "reporting": REPORT_HASH,
        },
        "acquisition": info,
        "routes": descriptions,
        "reporting": report,
        "matched_trigram": {
            "entries": int(trigram.degree[active].sum()),
            "rows": len(active),
            "packed_bytes": len(raw_payload),
            "sha256": hashlib.sha256(raw_payload).hexdigest(),
        },
        "conditional_priced_wins": beats,
        "posthoc_calibrated_trigram": dict(
            hybrid_info, reporting=measure(hybrid_loss, hybrid.bits, CAL)
        ),
        "registered_formation": descriptions["conditional"]["changed_seed_types"] > 0
        and all(beats[n] for n in ("constant", "seed", "bigram")),
    }


def controls():
    c = Common(array("H", [0, 0, 1, 3, 2, 1, 1, 0, 2, 4, 2, 5]), 7, 3)
    mass = np.stack([quantized(c.prior), quantized(c.prior[::-1])])
    routes = 0
    for flags in product((0, 1), repeat=7):
        bits = np.array(flags, dtype=np.uint8)
        payload = serialize(c, mass, bits)
        top, p, route, tail, _ = deserialize(payload, c.counts)
        assert np.array_equal(p[route], mass[bits])
        for q in range(c.vocab):
            for s in range(len(p)):
                probs = []
                for y in range(c.vocab):
                    j = top.index(y) if y in top else len(top)
                    fraction = 1 if j < len(top) else c.unigram[y] / tail
                    probs.append(
                        (c.rows.pairs[q, y] + TAU * p[s, j] / TOTAL_MASS * fraction)
                        / (c.rows.outgoing[q] + TAU)
                    )
                assert abs(fsum(probs) - 1) < 1e-12
        routes += 1
    checks = 0
    for value in product((1, 3, 8), repeat=4):
        w, v = np.array([1, 2, 3, 4]), np.array(value)
        for cap in range(11):
            _, score = knapsack(w[w <= cap], v[w <= cap], cap)
            assert score == max(
                sum(v[j] for j in range(4) if mask >> j & 1)
                for mask in range(16)
                if sum(w[j] for j in range(4) if mask >> j & 1) <= cap
            )
            checks += 1
    return {"packed_boolean_maps": routes, "small_knapsacks": checks}


def load_data(directory):
    anchor = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(e for e in anchor["results"] if e["case"] == "ngram")["result"][
        "train_source"
    ]
    data = tape(
        dict(src, bytes_read=REPORT_END * 2, prefix_sha256=REPORT_HASH), directory
    )
    for n, digest in (
        (READOUT_END, src["prefix_sha256"]),
        (ADDRESS_END, ADDRESS_HASH),
        (SELECT_END, SELECT_HASH),
    ):
        part = data[:n]
        if sys.byteorder != "little":
            part.byteswap()
        assert hashlib.sha256(part.tobytes()).hexdigest() == digest
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = {"controls": controls()}
    if not args.audit:
        sequence = load_data(args.data_dir)
        result["text"] = score(sequence, fit(sequence[:SELECT_END]))
    if args.check:
        assert json.loads(args.check.read_text(encoding="utf8")) == result
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    elif not args.check:
        print(output, end="")
