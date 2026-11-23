"""Learn a partition of earlier word IDs from full-vocabulary conditional target likelihood."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from controlled_sensing import UNIT, packed, quantize
from nested_class import event_prob
from response_classes import BLOCKS, LABELS, LOG_COUNTS, SIZES, SUBSETS
from scipy.special import betaln, xlogy
from text import VOCAB, git_json, tape
from text_addresses import CAL, RENT
from text_nested_class import END as START
from text_nested_class import SELECTION_END as OLD_SELECTION
from text_nested_class import SHA as OLD_SHA
from text_nested_class import frozen, restore
from threadpoolctl import threadpool_limits
from word_classes import Gate, vector

REGISTRATION = "3b17ced"
FIT_END = START + 2 * CAL
REPORT_START = FIT_END + CAL
END = REPORT_START + 2 * CAL
SHA = "2a1fa217f39637032606f5163cf841710d34054b5a604a5017e795c0ff044d1e"
ALPHAS = (8, 64, 512)


def report_starts():
    return range(REPORT_START, END, CAL)


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == OLD_SHA
    )
    return data


def top_names(ids):
    count = np.bincount(ids, minlength=VOCAB)
    return np.lexsort((np.arange(VOCAB), -count))[:8].astype("<u2")


def ranks(names, values):
    # The sentinel is never a row or column in the fitted table.
    lookup = np.full(VOCAB, 8, dtype=np.uint8)
    lookup[names] = np.arange(8)
    return lookup[values]


def panels(u, v):
    eligible = (u < 8) & (v < 8)
    # The modulus is a power of two, hence uint8 subtraction gives the same residue.
    withheld = eligible & np.isin((v - u) % 8, (0, 3))
    return eligible, withheld


@dataclass
class Model:
    early: np.ndarray
    current: np.ndarray
    labels: np.ndarray
    means: np.ndarray

    def packet(self):
        k = len(self.means)
        shared = np.array_equal(self.early, self.current)
        names = self.early.tobytes() + (b"" if shared else self.current.tobytes())
        groups = b"" if k in (1, 8) else packed(self.labels, (k - 1).bit_length())
        return bytes((1, k, int(shared))) + names + groups + self.means.tobytes()

    def selected(self, u, v):
        rates = np.zeros(len(u), dtype=np.uint16)
        eligible = (u < 8) & (v < 8)
        rates[eligible] = self.means[self.labels[u[eligible]], v[eligible]]
        return rates


def fits(early, current, n, h, prior):
    ns, hs = SUBSETS @ n, SUBSETS @ h
    result = {}
    empirical = np.divide(hs, ns, out=np.full(hs.shape, 0.5), where=ns != 0)
    ll = (xlogy(hs, empirical) + xlogy(ns - hs, 1 - empirical)).sum(axis=1)
    evidence = {
        "occupied_training_pairs": int(np.count_nonzero(n)),
        "saturated_empirical_gain": float(ll[1 << np.arange(8)].sum() - ll[-1]),
        "best_two_class_empirical_gain": float(
            ll[BLOCKS[SIZES == 2]].sum(axis=1).max() - ll[-1]
        ),
        "split_comparisons": {},
    }
    for alpha in ALPHAS:
        a, b = alpha * prior, alpha * (1 - prior)
        score = (betaln(hs + a, ns - hs + b) - betaln(a, b)).sum(axis=1)
        vals = score[BLOCKS].sum(axis=1) - LOG_COUNTS
        evidence["split_comparisons"][str(alpha)] = {
            "best_two_integrated_gain": float(
                score[BLOCKS[SIZES == 2]].sum(axis=1).max() - score[-1]
            ),
            "best_nontrivial_net_gain": float(vals[SIZES > 1].max() - score[-1]),
        }
        idx = int(np.flatnonzero(vals >= max(vals) - 1e-9)[0])
        for name, labels in (
            ("current", np.zeros(8, dtype=int)),
            ("learned", LABELS[idx]),
            ("independent", np.arange(8)),
        ):
            ids = np.arange(int(max(labels)) + 1)
            masks = (labels == ids[:, None]) @ (1 << np.arange(8))
            means = quantize((hs[masks] + a) / (ns[masks] + alpha))
            result[f"{name}/{alpha}"] = Model(early, current, labels, means)
    return result, evidence


def normalized(rows, outputs, odds, models):
    # Independent exact group sums from the raw successor counts and the persisted base masses.
    reference = next(iter(models.values()))
    membership = vector(outputs).astype(bool)
    cases = 0
    base_class = rows.apply(membership)
    for j, v in enumerate(reference.current):
        observed = rows.count.getrow(v).toarray()[0].astype(np.int64)
        back = int(rows.back_num[membership].sum())
        inside = int(observed[membership].sum()) * rows.back_den + 64 * back
        outside = int(observed[~membership].sum()) * rows.back_den + 64 * int(
            rows.back_num[~membership].sum()
        )
        assert inside + outside == (int(rows.common.outgoing[v]) + 64) * rows.back_den
        q = Fraction(int(inside) * odds, int(inside) * odds + int(outside) * 1024)
        assert abs(float(q) - event_prob(base_class[v], odds / 1024)) < 1e-15
        for m in models.values():
            for t in m.means[:, j]:
                rate = Fraction(int(t), UNIT)
                assert (q * (rate / q) + (1 - q) * ((1 - rate) / (1 - q))) == 1
                cases += 1
    return cases


def experiment(data):
    rows, outputs, odds, _, _, raw = frozen(data[:OLD_SELECTION])
    prior_work = json.loads(
        Path(__file__).with_name("text_nested_class_result.json").read_text()
    )
    global_gate = Gate(None, outputs, np.array([odds], dtype=np.uint16))
    global_bytes = len(global_gate.install(rows))
    joint = restore(prior_work["installations"]["joint"])
    assert (
        hashlib.sha256(joint.pack(rows, outputs)).hexdigest()
        == prior_work["installations"]["joint"]["sha256"]
    )
    ids = np.frombuffer(data, dtype=np.uint16)
    early = top_names(ids[START - 2 : FIT_END - 2])
    current = top_names(ids[START - 1 : FIT_END - 1])
    inside = vector(outputs).astype(bool)
    mass = rows.apply(inside)
    prior = event_prob(mass, odds / 1024)
    u = ranks(early, ids[START - 2 : FIT_END - 2])
    v = ranks(current, ids[START - 1 : FIT_END - 1])
    active, hold = panels(u, v)
    chosen = active & ~hold
    keys = 8 * u[chosen] + v[chosen]
    count = np.bincount(keys, minlength=64).reshape(8, 8)
    hit = np.bincount(
        keys, weights=inside[ids[START:FIT_END]][chosen], minlength=64
    ).reshape(8, 8)
    models, evidence = fits(early, current, count, hit, prior[current])
    checks = normalized(rows, outputs, odds, models)
    sizes = {
        "global": global_bytes,
        "joint": joint.size(rows, outputs),
        "raw_cap": raw["raw_cap"][1].bits // 8,
    }
    sizes.update({k: global_bytes + len(m.packet()) + 1 for k, m in models.items()})

    def score(start):
        obs = rows.common.observe(ids, start, start + CAL)
        base = -np.log(obs.readout(rows.tables[0]))
        b = inside[obs.target]
        mu = mass[obs.query]
        p = prior[obs.query]
        scalar = odds / 1024
        glob = base - (b * np.log(scalar) - np.log1p((scalar - 1) * mu))
        u, v = ranks(early, obs.history), ranks(current, obs.query)
        eligible, withheld = panels(u, v)
        summary = {}

        def record(name, loss):
            summary[name] = {
                "nll": float(loss.mean()),
                "priced": float(loss.mean() + 8 * RENT * sizes[name] / CAL),
                "eligible_nll": float(loss[eligible].mean()),
                "withheld_nll": float(loss[withheld].mean()),
                "first4096_nll": float(loss[:4096].mean()),
            }

        record("global", glob)
        record("joint", base - joint.gain(obs, mu, b))
        tri, readout, _ = raw["raw_cap"]
        record("raw_cap", readout.losses(tri, obs))
        for name, m in models.items():
            table = m.selected(u, v)
            actual = table[eligible].astype(float) / UNIT
            pg = p[eligible]
            gain = np.where(
                b[eligible], np.log(actual / pg), np.log((1 - actual) / (1 - pg))
            )
            loss = glob.copy()
            loss[eligible] -= gain
            record(name, loss)
        return {
            "first_target": start,
            "eligible": int(eligible.sum()),
            "withheld": int(withheld.sum()),
            "models": summary,
        }

    selection = score(FIT_END)

    def best(names):
        return min(
            names,
            key=lambda name: (selection["models"][name]["priced"], sizes[name], name),
        )

    best_each = {
        f: best([f"{f}/{alpha}" for alpha in ALPHAS])
        for f in ("current", "learned", "independent")
    }
    winner = best(["global", *best_each.values()])
    blocks = [score(start) for start in report_starts()]
    chosen_names = ["global", "joint", "raw_cap", *best_each.values()]
    mean = {}
    for name in chosen_names:
        mean[name] = {}
        for field in selection["models"][name]:
            weights = [
                b["eligible"]
                if field == "eligible_nll"
                else b["withheld"]
                if field == "withheld_nll"
                else CAL
                for b in blocks
            ]
            mean[name][field] = round(
                float(
                    np.average(
                        [b["models"][name][field] for b in blocks], weights=weights
                    )
                ),
                10,
            )

    def rounded(block):
        return {
            **block,
            "models": {
                k: {f: round(val, 10) for f, val in vals.items()}
                for k, vals in block["models"].items()
            },
        }

    return {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "starts": [START, FIT_END, REPORT_START, *list(report_starts())[1:], END],
        "training_eligible": int(active.sum()),
        "training_withheld_excluded": int(hold.sum()),
        "training_evidence": evidence,
        "training_counts": count.tolist(),
        "training_hits": hit.astype(int).tolist(),
        "early_ids": early.tolist(),
        "current_ids": current.tolist(),
        "base_class_mass_by_column": prior[current].tolist(),
        "exact_normalizations": checks,
        "global_bytes": global_bytes,
        "charged_bytes": sizes,
        "alpha_selection": best_each,
        "overall_selection": winner,
        "installations": {
            k: {"labels": m.labels.tolist(), "packet_hex": m.packet().hex()}
            for k, m in models.items()
        },
        "selection": rounded(selection),
        "blocks": [rounded(b) for b in blocks],
        "mean": mean,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    with threadpool_limits(limits=1):
        result = experiment(load_data(args.data_dir))
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    elif not args.check:
        print(json.dumps(result, indent=2))
