"""Construct priced, directed error-state readouts from ordinary words and sampled counts."""

import argparse
import json
import struct
from pathlib import Path
from time import perf_counter

import numpy as np
from direction_learning import history
from sample_acquisition import BUDGETS, RATE, SEEDS
from sparse_directions import FIT, Native
from sparse_transfer import source_identity
from text_addresses import RENT
from threadpoolctl import threadpool_limits

REGISTRATION = "8bc761f"
SHIFTS = (5, 7, 9)
GAINS = tuple(sign * g for g in (0.5, 1, 2, 4, 8, 16, 32, 64) for sign in (-1, 1))
TAIL = 65535
CAPS = (32, 96)
FITS = len(SEEDS) * len(BUDGETS)
RULE = struct.Struct("<HHBh")
HEADER = struct.Struct("<BBB")


def mixture(variance, scale, risk):
    return np.sqrt(
        (variance + scale) * (2 * np.log(1 / risk) + np.log1p(variance / scale))
    )


def encode(edges, names):
    if not edges:
        return b""
    uses_tail = any(TAIL in (src, dst) for src, dst, _, _ in edges)
    domain = sorted(map(int, names)) if uses_tail else []
    word = HEADER.pack(1, len(edges), len(domain))
    for edge in sorted(edges, key=lambda e: e[1]):
        word += RULE.pack(*edge)
    return word + np.asarray(domain, dtype="<u2").tobytes()


def decode(word):
    if not word:
        return [], []
    version, count, size = HEADER.unpack_from(word)
    if (
        version != 1
        or not 1 <= count <= 3
        or len(word) != HEADER.size + count * RULE.size + 2 * size
    ):
        raise ValueError("invalid directed readout header or length")
    edges = [RULE.unpack_from(word, HEADER.size + k * RULE.size) for k in range(count)]
    domain = np.frombuffer(
        word, dtype="<u2", offset=HEADER.size + count * RULE.size
    ).tolist()
    if (
        len({e[1] for e in edges}) != count
        or domain != sorted(set(domain))
        or any(e[2] not in SHIFTS or e[3] / 256 not in GAINS for e in edges)
        or (any(TAIL in e[:2] for e in edges) != bool(domain))
    ):
        raise ValueError("invalid directed rule or complementary domain")
    return edges, domain


def program_indices(word, ids):
    edges, domain = decode(word)
    if domain and domain != sorted(map(int, ids)):
        raise ValueError("complement differs from evaluator's partition")
    ix = {int(raw): i for i, raw in enumerate(ids)}
    ix[TAIL] = len(ids)
    return [(ix[src], ix[dst], shift, code / 256) for src, dst, shift, code in edges]


def search_utility(frequency, y, budget, lib):
    n, d = frequency.shape
    outcomes = np.eye(d)[y]
    risk = 0.025 / (FITS * d * d * len(SHIFTS) * len(GAINS))
    bounds = np.empty((len(SHIFTS), len(GAINS), d, d))
    for h, shift in enumerate(SHIFTS):
        rate = 2.0**-shift
        state = lib.histories(frequency, y, True, rate)
        realized = state.T @ outcomes
        for k, gain in enumerate(GAINS):
            increment = np.expm1(gain * state)
            estimate = gain * realized - increment.T @ frequency
            variance = np.einsum("ti,ti->i", increment, increment) / (4 * budget)
            scale = gain**2 * n * rate / (64 * budget)
            bounds[h, k] = estimate - mixture(variance, scale, risk)[:, None]
    return bounds


def select(bounds, ids):
    names = [*map(int, ids), TAIL]
    d = len(names)
    winners = {cap: (0.0, b"", 0.0) for cap in CAPS}
    for size in (d - 1, d):
        scores = bounds[:, :, :size, :size].reshape(-1, size)
        flat = scores.argmax(axis=0)
        value = scores[flat, np.arange(size)]
        order = np.argsort(-value, kind="stable")
        edges = []
        total = 0.0
        for j in order[:3]:
            h, k, i = np.unravel_index(flat[j], (len(SHIFTS), len(GAINS), size))
            edges.append((names[i], names[j], SHIFTS[h], round(256 * GAINS[k])))
            total += float(value[j])
            word = encode(edges, ids)
            net = total - 8 * RENT * len(word)
            for cap, (best, previous, _) in winners.items():
                if len(word) <= cap and (-net, len(word), word) < (
                    -best,
                    len(previous),
                    previous,
                ):
                    winners[cap] = (net, word, total)
    return {
        str(cap): {
            "packet": word.hex(),
            "certified_nats": total,
            "after_installation_price": net,
        }
        for cap, (net, word, total) in winners.items()
    }


def ideal_interval(frequency, y, budget):
    """Simultaneous exact-read diagonal score intervals from the same sampled tape."""
    n, d = frequency.shape
    residual = -frequency.copy()
    residual[np.arange(n), y] += 1
    past = history(residual, RATE)
    future = history(residual[::-1], RATE)[::-1]
    score = (past * residual).sum(axis=0)
    lag = np.arange(n)
    square_weights = RATE / (2 - RATE) * -np.expm1(2 * lag * np.log1p(-RATE))
    reverse_radius = np.sqrt(
        square_weights * np.log(4 * d * n * FITS / 0.0125) / (2 * budget)
    )[::-1, None]
    weight_cap = -np.expm1(lag * np.log1p(-RATE))
    weight_cap = weight_cap + weight_cap[::-1]
    upper = np.minimum(np.abs(past + future) + reverse_radius, weight_cap[:, None])
    proxy = np.einsum("ti,ti->i", upper, upper) / (4 * budget)
    radius = mixture(proxy, n * RATE / (64 * budget), 0.0125 / (d * FITS))
    energy_up = np.minimum(np.abs(past) + reverse_radius[::-1], 1)
    energy_up = np.einsum("ti,ti->i", energy_up, energy_up)
    excess = np.maximum(np.abs(score) - radius, 0)
    g = np.sign(score) * np.minimum(64, 4 * excess / np.maximum(energy_up, 1e-30))
    code = np.rint(g * 256).astype(int)
    g = code / 256
    lower = g * score - abs(g) * radius - g**2 * energy_up / 8
    i = int(np.argmax(lower))
    result = {
        "index": i if lower[i] > 0 else None,
        "slope_Q8": int(code[i]) if lower[i] > 0 else 0,
        "certified_nats": float(max(0, lower[i])),
        "estimated_score": float(score[i]),
        "radius": float(radius[i]),
    }
    return result, score, radius


def acquire(counts, y, ids, budget, lib):
    if counts.shape != (len(y), len(ids) + 1) or np.any(counts.sum(axis=1) != budget):
        raise ValueError("receipt count or partition mismatch")
    frequency = counts.astype(float) / budget
    programs = select(search_utility(frequency, y, budget, lib), ids)
    ideal, score, radius = ideal_interval(frequency, y, budget)
    return programs, ideal, score, radius


def exact_score_variance(q, y, budget):
    r = -q.copy()
    r[np.arange(len(y)), y] += 1
    s = history(r, RATE)
    h = s + history(r[::-1], RATE)[::-1]
    v = q * (1 - q) / budget
    # Sum k_{jt}^2 v_j forward: weight RATE^2 and pole (1-RATE)^2.
    from scipy.signal import lfilter

    past_variance = lfilter([0, RATE**2], [1, -((1 - RATE) ** 2)], v, axis=0)
    return (s * r).sum(axis=0), (v * (h**2 + past_variance)).sum(axis=0)


def reference_delta(edges, states, q, y):
    z = np.zeros_like(q)
    for src, dst, shift, gain in edges:
        z[:, dst] = states[shift][:, src] * gain
    from scipy.special import logsumexp

    log_z = logsumexp(np.log(q) + z, axis=1)
    return log_z - z[np.arange(len(y)), y], z


def fit(directory):
    with np.load(
        directory / "transformer_class_5907fd5.npz", allow_pickle=False
    ) as train:
        signature = source_identity(train)["arrays_sha256"]
        q, y, ids = train["mass"][:FIT], train["target"][:FIT], train["ids"]
    rows, timing = [], []
    with Native() as lib:
        for b in BUDGETS:
            truth, variance = exact_score_variance(q, y, b)
            for seed in SEEDS:
                counts = (
                    np.random.default_rng([seed, b]).multinomial(b, q).astype(np.uint16)
                )
                start = perf_counter()
                packets, ideal, score, radius = acquire(counts, y, ids, b, lib)
                timing.append(round(perf_counter() - start, 4))
                # The following evaluator alone receives the base probabilities.
                states = {
                    h: lib.histories(counts.astype(float) / b, y, True, 2.0**-h)
                    for h in SHIFTS
                }
                for record in packets.values():
                    edges = program_indices(bytes.fromhex(record["packet"]), ids)
                    delta, _ = reference_delta(edges, states, q, y)
                    record["checked_training_gain"] = float(-delta.sum())
                j = ideal["index"]
                ideal["true_score"] = float(truth[j]) if j is not None else None
                ideal["true_score_variance"] = (
                    float(variance[j]) if j is not None else None
                )
                ideal["maximum_error_over_radius"] = float(
                    np.max(abs(truth - score) / radius)
                )
                if j is not None:
                    exact_state = lib.histories(q, y, False)
                    z = exact_state[:, j] * (ideal["slope_Q8"] / 256)
                    ideal["checked_training_gain"] = float(
                        ((y == j) * z - np.log1p(q[:, j] * np.expm1(z))).sum()
                    )
                else:
                    ideal["checked_training_gain"] = 0.0
                rows.append(
                    {
                        "budget": b,
                        "seed": seed,
                        "programs": packets,
                        "ideal_diagonal": ideal,
                    }
                )
    return {
        "registration": REGISTRATION,
        "fit_array_hash": signature,
        "ids": ids.tolist(),
        "fit_targets": len(y),
        "candidate_rules": len(SHIFTS) * len(GAINS) * q.shape[1] ** 2,
        "fits": rows,
    }, timing


if __name__ == "__main__":
    from coin_memory import compare

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache-dir", type=Path, required=True)
    dest = p.add_mutually_exclusive_group(required=True)
    dest.add_argument("--write", type=Path)
    dest.add_argument("--check", type=Path)
    a = p.parse_args()
    with threadpool_limits(limits=1):
        result, times = fit(a.cache_dir)
    if a.check:
        assert compare(result, json.loads(a.check.read_text(encoding="utf8")))
    else:
        a.write.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print("Acquisition seconds per fit, without simulation or evaluation:", times)
