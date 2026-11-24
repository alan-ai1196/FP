"""Acquire a deterministic observable quotient by paid noisy reads and inverse actions."""

import json
from collections import Counter
from pathlib import Path

import numpy as np

SEEDS = (173, 419, 773)
LENGTHS = (16, 128, 1024)
ACTIONS = range(3)
CAP = 10
VOTES = 225


def plant():
    hidden = np.arange(8)
    transposition = hidden.copy()
    transposition[[0, 1]] = [1, 0]
    original = np.stack((transposition, -hidden % 8, (1 - hidden) % 8))
    rng = np.random.default_rng(25112026)
    rename = rng.permutation(8)
    order = rng.permutation(3)
    actions = rename[original[order][:, np.argsort(rename)]]
    old = np.isin(np.argsort(rename), [0, 1, 3])
    new = np.isin(np.argsort(rename), [0, 2, 5, 7])
    return actions, old, new


class Panel:
    """The fitter can reset, execute raw letters and count independently noisy reads."""

    def __init__(self, rng):
        self._actions, self._old, self._new = plant()
        self._rng = rng
        self.cost = Counter()

    def reset(self, size):
        self._state = self._rng.integers(len(self._old), size=size)
        self.cost["resets"] += size

    def move(self, a):
        self._state = self._actions[a, self._state]
        self.cost["advances"] += len(self._state)

    def read(self, count, terminal=False):
        positive = (self._new if terminal else self._old)[self._state]
        self.cost["reports"] += count * len(positive)
        return self._rng.binomial(count, np.where(positive, 0.875, 0.125))


def probe(panel, word):
    for a in word:
        panel.move(a)
    signs = panel.read(VOTES) > VOTES // 2
    for a in reversed(word):
        panel.move(a)
    return signs


def partition(panel):
    words = [()]
    trace = []
    for _ in range(CAP):
        panel.reset(100)
        successors = {(a,) + w for a in ACTIONS for w in words}
        tests = sorted(set(words) | successors, key=lambda w: (len(w), w))
        observed = {w: probe(panel, w) for w in tests}
        before = np.column_stack([observed[w] for w in words])
        signatures, index = np.unique(before, axis=0, return_inverse=True)
        groups = [index == i for i in range(len(signatures))]
        split = next(
            (
                w
                for w in tests
                if any(np.any(observed[w][g] != observed[w][g][0]) for g in groups)
            ),
            None,
        )
        trace.append(
            {
                "classes": len(groups),
                "tests": len(tests),
                "added": None if split is None else list(split),
            }
        )
        if split is not None:
            words.append(split)
            continue
        ids = {tuple(row): i for i, row in enumerate(signatures)}
        after = [np.column_stack([observed[(a,) + w] for w in words]) for a in ACTIONS]
        try:
            edges = np.array([[ids[tuple(mat[g][0])] for g in groups] for mat in after])
        except KeyError as err:
            raise ValueError("a successor signature has no sampled source") from err
        if any(not np.array_equal(row[row], np.arange(len(groups))) for row in edges):
            raise ValueError("sampled edges are inconsistent with inverse spelling")
        return words, signatures, edges, trace, (before, after)
    raise ValueError("refinement exceeded the state ceiling")


def conventional_partition(before, after):
    # Independently reduce the observed transition relation by ordinary Moore refinement.
    edges = {
        tuple(s): tuple(tuple(mat[i]) for mat in after) for i, s in enumerate(before)
    }
    states = list(edges)
    groups = {s: int(s[0]) for s in states}
    while True:
        keys = {s: (groups[s], *(groups[d] for d in edges[s])) for s in states}
        lookup = {k: i for i, k in enumerate(dict.fromkeys(keys.values()))}
        new = {s: lookup[k] for s, k in keys.items()}
        if len(lookup) == len(set(groups.values())):
            break
        groups = new
    # This enrolled experiment produces a minimal table at closure.
    assert len(set(new.values())) == len(states)
    order = sorted(states, key=new.get)
    return order, np.array([[new[edges[s][a]] for s in order] for a in ACTIONS])


def calibrate(panel, words, signatures, size=1024):
    panel.reset(size)
    obs = [probe(panel, w) for w in words]
    ids = {tuple(row): i for i, row in enumerate(signatures)}
    cls = np.array([ids[tuple(row)] for row in zip(*obs, strict=True)])
    f = panel.read(1)
    g = panel.read(1, terminal=True)
    correct = int(np.count_nonzero(f == signatures[cls, 0]))
    agree = int(np.clip(correct, (1 + 0.5) * size / 2, (1 + 0.875) * size / 2))
    counts = np.bincount(cls, minlength=len(ids))
    new_hits = np.bincount(cls, weights=g, minlength=len(ids)).astype(int)
    return agree, size, counts, new_hits, [float(f.mean()), float(g.mean())]


def transitive(edges):
    seen = {0}
    while True:
        expanded = {int(edges[a, i]) for i in seen for a in range(len(edges))} | seen
        if expanded == seen:
            return len(seen) == edges.shape[1]
        seen = expanded


def encode(edges, positive, correct, total, counts, hits):
    a, q = edges.shape
    width = max(1, (q - 1).bit_length())
    transitions = sum(int(dest) << (i * width) for i, dest in enumerate(edges.flat))
    labels = sum(int(flag) << i for i, flag in enumerate(positive))
    fields = np.array([correct, total, *hits, *counts], dtype="<u2")
    return (
        bytes([q, a])
        + transitions.to_bytes((a * q * width + 7) // 8, "little")
        + labels.to_bytes((q + 7) // 8, "little")
        + fields.tobytes()
    )


def decode(packet):
    q, a = packet[:2]
    width = max(1, (q - 1).bit_length())
    end = 2 + (a * q * width + 7) // 8
    bits = int.from_bytes(packet[2:end], "little")
    edges = np.array(
        [(bits >> (i * width)) % (1 << width) for i in range(a * q)]
    ).reshape(a, q)
    label_end = end + (q + 7) // 8
    labels = int.from_bytes(packet[end:label_end], "little")
    f = np.array([(labels >> i) % 2 for i in range(q)], dtype=bool)
    correct, total, *extra = map(int, np.frombuffer(packet[label_end:], dtype="<u2"))
    hits, counts = np.array_split(extra, 2)
    assert len(counts) == q and counts.sum() == total and np.all(hits <= counts)
    pf = np.where(f, correct / total, 1 - correct / total)
    pg = (hits + 1) / (counts + 2)
    prior = np.full(q, 1 / q) if transitive(edges) else (counts + 1) / (total + q)
    return edges, pf, pg, prior


def verify_graph(words, signatures, edges):
    true, f, _ = plant()
    probes = []
    for w in words:
        states = np.arange(len(f))
        for a in w:
            states = true[a, states]
        probes.append(f[states])
    ids = {tuple(row): i for i, row in enumerate(signatures)}
    to_model = np.array([ids[tuple(row)] for row in zip(*probes, strict=True)])
    assert len(set(to_model)) == len(f)
    assert np.array_equal(to_model[true], edges[:, to_model])


def test_draw(seed, length, episodes=128):
    rng = np.random.default_rng([seed, length, 832])
    edges, f, g = plant()
    state = rng.integers(len(f), size=episodes)
    actions = rng.integers(len(edges), size=(length, episodes))
    raw = []
    for t in range(length + 1):
        raw.append(rng.random(episodes) < np.where(f[state], 0.875, 0.125))
        if t < length:
            state = edges[actions[t], state]
    terminal = rng.random(episodes) < np.where(g[state], 0.875, 0.125)
    return actions, np.array(raw), terminal


def forward(model, actions, raw, first_only=False):
    edges, f, g, prior = model
    inverse = np.argsort(edges, axis=1)
    weights = np.tile(prior, (raw.shape[1], 1))
    predictions = []
    for t, z in enumerate(raw):
        predictions.append(weights @ f)
        if not first_only or t == 0:
            weights *= np.where(z[:, None], f, 1 - f)
            weights /= weights.sum(axis=1, keepdims=True)
        if t < len(actions):
            weights = np.take_along_axis(weights, inverse[actions[t]], axis=1)
    return np.array(predictions), weights @ g


def likelihood_filter(model, actions, raw):
    # Keep independent log likelihoods of all starting classes and track their locations.
    edges, f, g, prior = model
    starts = np.tile(np.arange(len(f)), (raw.shape[1], 1))
    score = np.tile(np.log(prior), (raw.shape[1], 1))

    def weights():
        mass = np.exp(score - score.max(axis=1, keepdims=True))
        return mass / mass.sum(axis=1, keepdims=True)

    predictions = []
    for t, z in enumerate(raw):
        local = f[starts]
        predictions.append(np.sum(weights() * local, axis=1))
        score += np.log(np.where(z[:, None], local, 1 - local))
        if t < len(actions):
            starts = edges[actions[t, :, None], starts]
    return np.array(predictions), np.sum(weights() * g[starts], axis=1)


def losses(p, q, outcome):
    kl = p * np.log(p / q) + (1 - p) * np.log((1 - p) / (1 - q))
    return {
        "excess_nats": float(kl.mean()),
        "realized_nll": float(-np.mean(np.log(np.where(outcome, q, 1 - q)))),
    }


def evaluate(seed, model, reference, marginal, length):
    actions, raw, terminal = test_draw(seed, length)
    edges, f, g = plant()
    oracle = forward(
        (edges, 0.125 + 0.75 * f, 0.125 + 0.75 * g, np.full(len(f), 1 / len(f))),
        actions,
        raw,
    )
    forecasts = {
        "oracle": oracle,
        "quotient": forward(model, actions, raw),
        "conventional": likelihood_filter(reference, actions, raw),
        "first_report": forward(model, actions, raw, first_only=True),
        "marginal": (
            np.full(raw.shape, marginal[0]),
            np.full(terminal.shape, marginal[1]),
        ),
    }
    diff = max(
        float(np.abs(x - y).max())
        for x, y in zip(forecasts["quotient"], forecasts["conventional"], strict=True)
    )
    assert diff < 1e-10
    return {
        "length": length,
        "conventional_max_difference": diff,
        "scores": {
            name: {
                "ordinary": losses(oracle[0], q[0], raw),
                "terminal": losses(oracle[1], q[1], terminal),
            }
            for name, q in forecasts.items()
        },
    }


def run():
    fits = []
    for seed in SEEDS:
        panel = Panel(np.random.default_rng([seed, 1529]))
        words, signatures, edges, rounds, samples = partition(panel)
        build_cost = dict(panel.cost)
        order, ref_edges = conventional_partition(*samples)
        order_index = {tuple(row): i for i, row in enumerate(signatures)}
        ref_ids = [order_index[s] for s in order]
        panel.cost.clear()
        correct, total, counts, hits, marginal = calibrate(panel, words, signatures)
        packet = encode(edges, signatures[:, 0], correct, total, counts, hits)
        model = decode(packet)
        reference = ref_edges, *(x[ref_ids] for x in model[1:])
        verify_graph(words, signatures, edges)
        fits.append(
            {
                "seed": seed,
                "words": words,
                "rounds": rounds,
                "classes": len(signatures),
                "build_cost": build_cost,
                "calibration_cost": dict(panel.cost),
                "packet_hex": packet.hex(),
                "bytes": len(packet),
                "f_correct": correct,
                "calibration_by_class": counts.tolist(),
                "new_positive": hits.tolist(),
                "marginals": marginal,
                "lengths": [
                    evaluate(seed, model, reference, marginal, h) for h in LENGTHS
                ],
            }
        )
    return {"registration": "3d4b9a2", "fresh_episodes_per_length": 128, "fits": fits}


if __name__ == "__main__":
    Path(__file__).with_name("reversible_reports_result.json").write_text(
        json.dumps(run(), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
