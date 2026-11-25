"""Discover a hidden affine terminal rule under two matched noisy-read budgets."""

import argparse
import json
from math import log
from pathlib import Path

import numpy as np

SEEDS = (173, 419, 773)
RHO = 0.5
REPEATS = 97


class Source:
    def __init__(self, seed, d, size):
        rng = np.random.default_rng([seed, d, 2711])
        self.d = d
        self.support = sorted(map(int, rng.choice(d - 1, size - 1, replace=False)))
        self.offset = int(rng.integers(2))

    def sample(self, rng, n, input_reads, target_reads):
        x = rng.integers(2, size=(n, self.d - 1), dtype=np.uint8)
        y = np.bitwise_xor.reduce(x[:, self.support], axis=1) ^ self.offset
        x_counts = rng.binomial(input_reads, 0.25 + 0.5 * x).astype(np.uint8)
        y_counts = rng.binomial(target_reads, 0.25 + 0.5 * y).astype(np.uint8)
        return x_counts, y_counts

    def truth(self):
        return sum(1 << i for i in self.support), self.offset


def packed_rows(hard):
    # pad every input vector to its own byte boundary
    return [
        int.from_bytes(row.tobytes(), "little")
        for row in np.packbits(hard, axis=1, bitorder="little")
    ]


def eliminate(x, y, b):
    d = x.shape[1] + 1
    basis = [None] * d
    rank = xors = 0
    for i, (raw, target) in enumerate(
        zip(packed_rows(2 * x.astype(int) > b), 2 * y.astype(int) > b, strict=True)
    ):
        row = raw | (1 << (d - 1))
        rhs = int(target)
        while row:
            j = row.bit_length() - 1
            if basis[j] is None:
                basis[j] = row, rhs
                rank += 1
                break
            other, value = basis[j]
            row ^= other
            rhs ^= value
            xors += 1
        if not row and rhs:
            return None, {
                "status": "inconsistent",
                "rank": rank,
                "inspected": i + 1,
                "row_xors": xors,
            }
    stats = {"rank": rank, "inspected": len(y), "row_xors": xors}
    if rank != d:
        return None, {"status": "rank deficient", **stats}
    solution = 0
    for j, (row, rhs) in enumerate(basis):
        bit = rhs ^ ((solution & row).bit_count() % 2)
        solution |= bit << j
    return (solution % (1 << (d - 1)), solution >> (d - 1)), {
        "status": "installed",
        **stats,
    }


def walsh(values):
    values = values.copy()
    step = 1
    while step < len(values):
        blocks = values.reshape(-1, 2 * step)
        left = blocks[:, :step].copy()
        right = blocks[:, step:].copy()
        blocks[:, :step] = left + right
        blocks[:, step:] = left - right
        step *= 2
    return values


def likelihoods(x, y, b):
    # Relative to fair independent latent coordinates read under the same schedule.
    width = x.shape[1]
    masks = np.arange(1 << width)
    sizes = np.array([int(i).bit_count() for i in masks])
    parity = sizes % 2
    x_hard = np.asarray(packed_rows(2 * x.astype(int) > b))
    y_hard = 2 * y.astype(int) > b
    if b == 1:
        count = np.bincount(x_hard, weights=1 - 2 * y_hard, minlength=len(masks))
        correlation = walsh(count)
        a = RHO ** (sizes + 1)
        base = 0.5 * len(y) * np.log1p(-a * a)
        advantage = correlation * np.arctanh(a)
        return np.stack([base + advantage, base - advantage])

    # Keep tiny probabilities of contradicting an apparently perfect vote.
    count = np.column_stack([x, y]).astype(int)
    odds = np.exp(-abs(b - 2 * count) * np.log(3.0))
    log_bias = np.log1p(-odds) - np.log1p(odds)
    scores = np.empty((2, len(masks)))
    for chunk in np.array_split(masks, max(1, len(masks) // 128)):
        select = ((chunk[None, :] >> np.arange(width)[:, None]) & 1).astype(float)
        magnitude = log_bias[:, :-1] @ select + log_bias[:, -1:]
        aligned = np.log1p(np.exp(magnitude))
        opposed = np.log(-np.expm1(magnitude))
        flip = parity[x_hard[:, None] & chunk] ^ y_hard[:, None]
        scores[0, chunk] = np.where(flip, opposed, aligned).sum(axis=0)
        scores[1, chunk] = np.where(flip, aligned, opposed).sum(axis=0)
    return scores


def likelihood(x, y, b):
    scores = likelihoods(x, y, b)
    sign, mask = map(int, np.unravel_index(scores.argmax(), scores.shape))
    peak = float(scores[sign, mask])
    installed = peak > log(scores.size)
    return (
        (mask, sign) if installed else None,
        {
            "status": "installed" if installed else "rent",
            "peak_log_gain": round(peak, 9),
        },
    )


def probability(model, x, b):
    if model is None:
        return np.full(len(x), 0.5)
    mask, offset = model
    ids = [i for i in range(x.shape[1]) if mask & (1 << i)]
    bias = np.tanh(0.5 * np.log(3.0) * (b - 2 * x[:, ids].astype(int)))
    # Conditional probability of target bit ONE, before its only noisy report.
    return 0.5 * (1 - RHO * (-1) ** offset * bias.prod(axis=1))


def test_sets(source, seed):
    cases = {}
    for b in (1, 17):
        x, y = source.sample(
            np.random.default_rng([seed, source.d, b, 8102]), 2048, b, 1
        )
        cases[b] = x, y, probability(source.truth(), x, b)
    return cases


def score(cases, model):
    result = {}
    for b, (x, y, p) in cases.items():
        q = probability(model, x, b)
        # Stable near p=q=1/2 even for a 32-coordinate one-pass parity.
        delta = p - q
        kl = p * np.log1p(delta / q) + (1 - p) * np.log1p(-delta / (1 - q))
        nll = -np.mean(np.log(np.where(y, q, 1 - q)))
        result[str(b)] = [float(f"{kl.mean():.12g}"), float(f"{nll:.12g}")]
    return result


def model_record(model):
    return None if model is None else [hex(model[0]), model[1]]


def parse_model(record):
    return None if record is None else (int(record[0], 16), record[1])


def run():
    panels = []
    for d, size, resets in [(12, 6, (8, 24, 128, 1024)), (64, 32, (96,))]:
        for seed in SEEDS:
            source = Source(seed, d, size)
            truth = source.truth()
            cases = test_sets(source, seed)
            oracle, fair = score(cases, truth), score(cases, None)
            fits = []
            for t in resets:
                for b in (1, REPEATS):
                    n = t * REPEATS // b
                    rng = np.random.default_rng([seed, d, t, b, 6021])
                    x, y = source.sample(rng, n, b, b)
                    models = {"elimination": eliminate(x, y, b)}
                    if d == 12:
                        models["likelihood"] = likelihood(x, y, b)
                    tested = {}
                    for name, (model, meta) in models.items():
                        record = model_record(model)
                        current = score(cases, parse_model(record))
                        report = (
                            "oracle"
                            if current == oracle
                            else "fair"
                            if current == fair
                            else current
                        )
                        tested[name] = {
                            **meta,
                            "model": record,
                            "correct": model == truth,
                            "terminal_scores": report,
                        }
                    fits.append(
                        {
                            "budget_index": t,
                            "reads_per_coordinate": b,
                            "reset_rows": n,
                            "total_reads": d * n * b,
                            "advances": (d - 1) * n,
                            "fits": tested,
                        }
                    )
            panels.append(
                {
                    "d": d,
                    "support_size_including_target": size,
                    "seed": seed,
                    "hidden_mask_and_offset": model_record(truth),
                    "oracle": oracle,
                    "fair": fair,
                    "acquisition": fits,
                }
            )
    return {
        "registration": "e79bc90",
        "terminal_scores": ["conditional_KL_nats", "realized_NLL_nats"],
        "panels": panels,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(run(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
