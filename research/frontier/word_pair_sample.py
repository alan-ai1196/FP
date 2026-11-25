"""Compare transmitted random word pairs with matched bag histograms at equal bits."""

import argparse
import json
from pathlib import Path

import numpy as np
from matched_word_bags import FROZEN, SEEDS, evaluate, serialize
from text_aggregate import (
    FIT_END,
    FIT_SHA,
    FIT_START,
    HISTORY,
    TAU,
    K,
    install,
    stochastic,
    tables,
    tokens,
    vocabulary,
)
from threadpoolctl import threadpool_limits

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "word_pair_sample_fits.json"
RANGES = (
    (
        "train_source",
        11131072,
        "3ed199c3d63a2f8f1aacfdc23be37b77721cd5365ea775334de795af70153792",
    ),
    (
        "reporting_source",
        393216,
        "c3b19e3dd03e92b2bfb2435af4023fdadbb27c919d1005fbd30c4514c5c1771c",
    ),
)


def transmit(labels):
    width = (K - 1).bit_length()
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint8)
    encoded = np.packbits(
        ((labels.astype(np.uint8)[:, None] >> shifts) & 1).ravel(), bitorder="big"
    )
    bits = np.unpackbits(encoded, count=len(labels) * width, bitorder="big")
    decoded = bits.reshape(-1, width) @ (1 << shifts)
    assert np.array_equal(decoded, labels)
    return decoded.astype(np.int64), encoded.nbytes


def fit_samples(directory):
    bags = json.loads(FROZEN.read_text())
    train = tokens("train_source", FIT_END, FIT_SHA, directory)
    names, classes, _ = vocabulary(train[:HISTORY])
    assert names.tolist() == bags["class_names"]
    coded = classes[train[FIT_START - 1 : FIT_END]]
    d, y = coded[:-1], coded[1:]
    n = len(d)
    packets = []
    ids = {}
    conditions = []
    for seed in SEEDS:
        order = np.random.default_rng([seed, 7311]).permutation(n)
        counts = {}
        for c in bags["conditions"]:
            item = {
                "seed": seed,
                "size": c["size"],
                "histogram_bits": c["enumerative_histogram_bits"],
            }
            for key, number in (
                ("same_groups", c["groups"]),
                ("same_bits", min(n, c["enumerative_histogram_bits"] // 10)),
            ):
                if number not in counts:
                    positions = order[:number]
                    ctx, first = transmit(d[positions])
                    target, second = transmit(y[positions])
                    observed = tables(ctx, target)
                    u = (observed.sum(axis=0) + 0.5) / (number + K / 2)
                    packet = install(stochastic(observed + TAU * u, u))
                    if packet not in ids:
                        ids[packet] = len(packets)
                        packets.append(packet)
                    counts[number] = {
                        "paired_positions": number,
                        "payload_bits": 10 * number,
                        "wire_bytes": first + second,
                        "packet": ids[packet],
                    }
                item[key] = counts[number]
            assert (
                8 * item["same_bits"]["wire_bytes"] <= c["enumerative_histogram_bits"]
            )
            conditions.append(item)
    return {
        "registration": "2852526",
        "fit_prefix": FIT_SHA,
        "class_names": names.tolist(),
        "conditions": conditions,
        "packets": packets,
    }


def score_samples(directory):
    bags = json.loads(FROZEN.read_text())
    samples = json.loads(SAMPLES.read_text())
    ids = {bags["direct_packet"], bags["marginal_packet"]}
    for size in bags["conditions"]:
        for row in size["conditions"]:
            if row["construction"] == "matched":
                ids.update((row["covariance"], row["regression"]))
    bag_ids = sorted(ids)
    packets = [bags["packets"][i] for i in bag_ids] + samples["packets"]
    result = evaluate(directory, bags["class_names"], packets, RANGES)
    return {"bag_packet_ids": bag_ids, "first_sample_index": len(bag_ids), **result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["fit", "score"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        if args.operation == "fit":
            body = serialize(fit_samples(args.data_dir))
        else:
            result = score_samples(args.data_dir)
            body = (
                json.dumps({k: v for k, v in result.items() if k != "reports"})[:-1]
                + ",\n"
                + serialize({"reports": result["reports"]})[1:]
            )
    if args.output:
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
