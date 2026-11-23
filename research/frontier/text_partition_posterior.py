"""Prospective frozen and prequential Bayesian partition predictions on the raw text tape."""

import argparse
import hashlib
import json
import struct
from pathlib import Path
from time import perf_counter

import numpy as np
from controlled_sensing import UNIT, quantize
from nested_class import event_prob
from partition_posterior import Online, exact_example, posterior, subset_marginals
from response_classes import BLOCKS, SIZES, SUBSETS
from text import git_json, tape
from text_addresses import CAL, RENT
from text_nested_class import SELECTION_END, frozen
from text_response_classes import END as START
from text_response_classes import SHA as PREVIOUS_SHA
from text_response_classes import Model, panels, ranks
from threadpoolctl import threadpool_limits
from word_classes import vector

REGISTRATION = "8793590"
END = START + 2 * CAL
SHA = "ff12f6daaa6314f30b3a182d1ab3cac4426f01a0765c2170003b2fc6624ccf2f"
ALPHA = 512


def report_starts():
    return range(START, END, CAL)


def load_data(directory):
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    source = next(
        e["result"]["train_source"] for e in ledger["results"] if e["case"] == "ngram"
    )
    data = tape(dict(source, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == PREVIOUS_SHA
    )
    return data


def fold_rows(table):
    labels = []
    rows = []
    by_row = {}
    for row in table:
        key = row.tobytes()
        if key not in by_row:
            by_row[key] = len(rows)
            rows.append(row)
        labels.append(by_row[key])
    return np.array(labels), np.stack(rows)


def model_from_rates(early, current, rates):
    labels, table = fold_rows(quantize(rates))
    return Model(early, current, labels, table)


def count_packet(kind, early, current, n, h, prior):
    shared = np.array_equal(early, current)
    header = struct.pack(
        "<BBH", {"current": 1, "independent": 8, "mixture": 4}[kind], int(shared), ALPHA
    )
    header += early.tobytes() + (b"" if shared else current.tobytes())
    stored = (
        (n.sum(axis=0, dtype=np.uint32), h.sum(axis=0, dtype=np.uint32))
        if kind == "current"
        else (n, h)
    )
    packet = (
        header
        + prior.astype("<f8").tobytes()
        + b"".join(x.astype("<u4").tobytes() for x in stored)
    )
    return packet, len(header)


def resume(packet):
    tag, shared, alpha = struct.unpack_from("<BBH", packet)
    kind = {1: "current", 4: "mixture", 8: "independent"}[tag]
    early = np.frombuffer(packet, dtype="<u2", count=8, offset=4)
    current = (
        early if shared else np.frombuffer(packet, dtype="<u2", count=8, offset=20)
    )
    offset = 20 if shared else 36
    prior = np.frombuffer(packet, dtype="<f8", count=8, offset=offset)
    counts = np.frombuffer(packet, dtype="<u4", offset=offset + 64).reshape(
        2, 1 if tag == 1 else 8, 8
    )
    return early, current, Online(kind, counts[0], counts[1], prior, alpha)


def study(data, previous):
    exact_example()
    early = np.array(previous["early_ids"], dtype="<u2")
    current = np.array(previous["current_ids"], dtype="<u2")
    fit_n = np.asarray(previous["training_counts"], dtype="<u4")
    fit_h = np.asarray(previous["training_hits"], dtype="<u4")
    rows, outputs, odds, _, _, _ = frozen(data[:SELECTION_END])
    ids = np.frombuffer(data, dtype=np.uint16)
    obs = rows.common.observe(ids, START, END)
    belongs = vector(outputs).astype(bool)
    raw_mass = rows.apply(belongs)
    raw = raw_mass[obs.query]
    prior = event_prob(raw_mass[current], odds / 1024)
    assert np.allclose(prior, previous["base_class_mass_by_column"], rtol=0, atol=1e-15)
    base = event_prob(raw, odds / 1024)
    y = belongs[obs.target]
    glob = (
        -np.log(obs.readout(rows.tables[0]))
        - y * np.log(odds / 1024)
        + np.log1p((odds / 1024 - 1) * raw)
    )
    u, v = ranks(early, obs.history), ranks(current, obs.query)
    eligible, missing = panels(u, v)
    indices = np.flatnonzero(eligible)
    iu, iv, iy = u[indices], v[indices], y[indices]
    ns, hs, weights, util = posterior(fit_n, fit_h, prior, ALPHA)
    marg = subset_marginals(util)
    enum = np.bincount(BLOCKS.ravel(), weights=np.repeat(weights, 4), minlength=256)
    np.testing.assert_allclose(marg[1:], enum[1:], rtol=0, atol=3e-11)
    mixture = (SUBSETS.T * marg) @ ((hs + ALPHA * prior) / (ns + float(ALPHA)))
    rates = {
        "mixture": mixture,
        "current": np.tile(
            (fit_h.sum(axis=0) + ALPHA * prior) / (fit_n.sum(axis=0) + ALPHA), (8, 1)
        ),
        "independent": (fit_h + ALPHA * prior) / (fit_n + float(ALPHA)),
    }
    assert int(fit_n.sum()) + len(iu) < 2**32 and np.all(fit_h <= fit_n)
    nbase = previous["global_bytes"]
    named = {}
    all_metrics = {}
    resources = {}
    replay_counts = {}
    code_scores = {}
    times = {}

    def record(name, q, charged):
        if q is None:
            losses = glob.copy()
        else:
            a = q.astype(float) / UNIT
            pred = base[indices]
            gains = np.where(iy, np.log(a / pred), np.log((1 - a) / (1 - pred)))
            losses = glob.copy()
            losses[indices] -= gains

        def part(sl):
            e, m = eligible[sl], missing[sl]
            x = losses[sl]
            return {
                "nll": float(x.mean()),
                "priced": float(x.mean() + 8 * RENT * charged / CAL),
                "eligible_nll": float(x[e].mean()),
                "withheld_nll": float(x[m].mean()),
                "eligible": int(e.sum()),
                "withheld": int(m.sum()),
            }

        all_metrics[name] = {
            "blocks": [part(slice(0, CAL)), part(slice(CAL, None))],
            "all": part(slice(None)),
            "first4096_mean": float(
                np.mean([losses[i : i + 4096].mean() for i in (0, CAL)])
            ),
        }

    record("global", None, nbase)
    for kind, rate in rates.items():
        installed = model_from_rates(early, current, rate)
        packet = installed.packet()
        selected = installed.means[installed.labels[iu], iv]
        assert np.array_equal(selected, quantize(rate)[iu, iv])
        if kind != "mixture":
            name = "current" if kind == "current" else "independent"
            assert (
                packet.hex() == previous["installations"][f"{name}/512"]["packet_hex"]
            )
        named[kind] = {
            "exact_q16_row_profiles": len(installed.means),
            "labels": installed.labels.tolist(),
            "packet_hex": packet.hex(),
            "charged_frozen_bytes": nbase + len(packet) + 1,
        }
        record(kind + "/frozen", selected, nbase + len(packet) + 1)
        state, header_bytes = count_packet(kind, early, current, fit_n, fit_h, prior)
        for mode in ("permitted", "all"):
            started = perf_counter()
            restored_early, restored_current, stream = resume(state)
            assert np.array_equal(restored_early, early) and np.array_equal(
                restored_current, current
            )
            forecasts = np.empty(len(iu), dtype=np.float64)
            counts = fit_n.copy()
            hits = fit_h.copy()
            updates = missing_updates = 0
            for i in range(len(iu)):
                a, b = int(iu[i]), int(iv[i])
                p, likelihood = stream.predict(a, b)
                forecasts[i] = p
                if mode == "all" or not missing[indices[i]]:
                    observed = bool(iy[i])
                    stream.observe(a, b, observed, likelihood)
                    counts[a, b] += 1
                    hits[a, b] += int(observed)
                    updates += 1
                    missing_updates += int(missing[indices[i]])
            elapsed = perf_counter() - started
            # Reconstruct the posterior from uint32 raw sufficient counts, independently of event order.
            if kind == "mixture":
                t0 = perf_counter()
                for _ in range(9):
                    n2, h2, w2, _ = posterior(counts, hits, prior, ALPHA)
                times["single full posterior rebuild from counts/" + mode] = round(
                    (perf_counter() - t0) / 9, 7
                )
                np.testing.assert_array_equal(n2, stream.n)
                np.testing.assert_array_equal(h2, stream.h)
                np.testing.assert_allclose(w2, stream.weights, rtol=0, atol=2e-10)
                assert np.all(stream.weights > 0)
                minimum = float(stream.weights.min())
            elif kind == "current":
                np.testing.assert_array_equal(stream.n[0], counts.sum(axis=0))
                np.testing.assert_array_equal(stream.h[0], hits.sum(axis=0))
                minimum = None
            else:
                np.testing.assert_array_equal(stream.n, counts)
                np.testing.assert_array_equal(stream.h, hits)
                minimum = None
            key = kind + "/" + mode
            allocated = stream.allocated()
            charged = nbase + len(state) + 1
            active_bytes = nbase + 1 + header_bytes + sum(allocated.values())
            resources[key] = {
                **allocated,
                "charged_active_arrays_dictionary_global_carry": active_bytes,
                "serialized_counts_model_bytes": len(state),
                "charged_with_global_and_carry": charged,
                "sha256_initial_count_packet": hashlib.sha256(state).hexdigest(),
            }
            replay_counts[key] = {
                "updates": updates,
                "withheld_updates": missing_updates,
                "final_counts_sum": int(counts.sum()),
                "min_partition_weight": minimum,
            }
            allowed = (
                np.ones(len(iu), dtype=bool) if mode == "all" else ~missing[indices]
            )
            true_terms = np.where(iy, -np.log(forecasts), -np.log1p(-forecasts))
            released = quantize(forecasts)
            rq = released.astype(float) / UNIT
            code_scores[key] = {
                "unrounded_nll_on_updates": float(true_terms[allowed].sum()),
                "q16_nll_on_updates": float(
                    np.where(iy, -np.log(rq), -np.log1p(-rq))[allowed].sum()
                ),
            }
            if kind == "mixture":
                one = SIZES == 1
                code_scores[key]["posterior_log_ratio_for_one_class"] = float(
                    np.log(w2[one][0] / weights[one][0])
                )
            record(key, released, charged)
            all_metrics[key]["all"]["priced_active_arrays"] = (
                all_metrics[key]["all"]["nll"] + 8 * RENT * active_bytes / CAL
            )
            times[key] = round(elapsed, 4)
    for mode in ("permitted", "all"):
        mix = code_scores["mixture/" + mode]
        excess = (
            mix["unrounded_nll_on_updates"]
            - code_scores["current/" + mode]["unrounded_nll_on_updates"]
        )
        assert abs(excess - mix["posterior_log_ratio_for_one_class"]) < 1e-8
    shares = np.bincount(SIZES, weights=weights, minlength=5)[1:].tolist()

    def normalized_result(o):
        if isinstance(o, float):
            return round(o, 11)
        if isinstance(o, list):
            return [normalized_result(x) for x in o]
        if isinstance(o, dict):
            return {k: normalized_result(v) for k, v in o.items()}
        return o

    return normalized_result(
        {
            "registration": REGISTRATION,
            "early_ids": early.tolist(),
            "current_ids": current.tolist(),
            "prefix": SHA,
            "starts": list(report_starts()),
            "alpha": ALPHA,
            "prior_fit_eligible_targets": int(fit_n.sum()),
            "posterior_mass_by_size": shares,
            "frozen_installations": named,
            "online_resources": resources,
            "replay": replay_counts,
            "coding_identity": code_scores,
            "scores": all_metrics,
        }
    ), times


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    previous = json.loads(
        Path(__file__).with_name("text_response_classes_result.json").read_text()
    )
    with threadpool_limits(limits=1):
        result, times = study(load_data(args.data_dir), previous)
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    elif not args.check:
        print(json.dumps(result, indent=2))
    if args.write or args.check:
        print("seconds for online forecasts and updates", times)
