"""Infer the algebra of two uninterpreted input letters from ordinary answers."""

import argparse
import json
from collections import Counter, deque
from itertools import product
from math import log
from pathlib import Path

import numpy as np
from rare_flat import risk

ETA = 1 / 8
V = 5
REPETITIONS = (1, 3, 9, 33)


def words_upto(length):
    return [w for n in range(length + 1) for w in product(range(2), repeat=n)]


WORDS = words_upto(7)
INDEX = {w: i for i, w in enumerate(WORDS)}


def visible_walk(trans, mask, word):
    state = 0
    for letter in word:
        state = trans[state][letter]
    return (mask >> state) & 1


def canonical(raw, q):
    highest = 0
    for j in range(q):
        if j > highest:
            return False
        for dest in raw[2 * j : 2 * j + 2]:
            if dest > highest + 1:
                return False
            highest = max(dest, highest)
    return highest == q - 1


def minimal(trans, mask):
    colors = [(mask >> j) & 1 for j in range(len(trans))]
    while len(set(colors)) != len(trans):
        signatures = [
            (c, colors[a], colors[b]) for c, (a, b) in zip(colors, trans, strict=True)
        ]
        ids = {v: j for j, v in enumerate(dict.fromkeys(signatures))}
        if len(ids) == len(set(colors)):
            return False
        colors = [ids[v] for v in signatures]
    return True


def laws(trans):
    commuting = all(trans[a][1] == trans[b][0] for a, b in trans)
    involutive = all(
        trans[a][0] == j and trans[b][1] == j for j, (a, b) in enumerate(trans)
    )
    return bool(commuting), bool(involutive)


def equivalent(trans, mask, other, target):
    seen = {(0, 0)}
    queue = deque(seen)
    while queue:
        a, b = queue.popleft()
        if (mask >> a) & 1 != (target >> b) & 1:
            return False
        for pair in zip(trans[a], other[b], strict=True):
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    return True


def packet(trans, readout):
    q = len(trans)
    width = (q - 1).bit_length()
    value, offset = q - 1, 2
    for row in trans:
        for dest in row:
            value |= dest << offset
            offset += width
    value |= readout << offset
    return value.to_bytes((offset + q + 7) // 8, "little")


def unpack(data):
    value = int.from_bytes(data, "little")
    q = 1 + (value & 3)
    value >>= 2
    width = (q - 1).bit_length()
    mask = (1 << width) - 1
    rows = []
    for _ in range(q):
        rows.append((value & mask, (value >> width) & mask))
        value >>= 2 * width
    return tuple(rows), value


def heldout():
    rng = np.random.default_rng([8513])
    return [
        tuple(map(int, rng.integers(2, size=length)))
        for length in (24, 25)
        for _ in range(128)
    ]


def catalogue():
    held = heldout()
    transitions, selected, masks, prior, sizes = [], [], [], [], []
    train_blocks, held_blocks = [], []
    for q in range(1, 5):
        base, machine_ids, outputs = [], [], []
        for raw in product(range(q), repeat=2 * q):
            if not canonical(raw, q):
                continue
            table = tuple((raw[2 * j], raw[2 * j + 1]) for j in range(q))
            base.append(table)
            for mask in range(1 << q):
                if minimal(table, mask):
                    machine_ids.append(len(base) - 1)
                    outputs.append(mask)
        array = np.array(base, dtype=np.uint8)
        sid = np.arange(len(base))
        reached = np.zeros((len(base), len(WORDS)), dtype=np.uint8)
        for i, w in enumerate(WORDS[1:], start=1):
            reached[:, i] = array[sid, reached[:, INDEX[w[:-1]]], w[-1]]
        terminal = np.zeros((len(base), len(held)), dtype=np.uint8)
        for i, w in enumerate(held):
            state = np.zeros(len(base), dtype=np.uint8)
            for letter in w:
                state = array[sid, state, letter]
            terminal[:, i] = state
        mask_vec = np.array(outputs, dtype=np.uint8)[:, None]
        mid = np.array(machine_ids)
        train_blocks.append((mask_vec >> reached[mid]) & 1)
        held_blocks.append((mask_vec >> terminal[mid]) & 1)
        selected.extend((len(transitions) + mid).tolist())
        transitions.extend(base)
        masks.extend(outputs)
        prior.extend([-log(4 * len(outputs))] * len(outputs))
        sizes.extend([q] * len(outputs))
    return (
        transitions,
        np.array(selected),
        np.array(masks),
        np.array(sizes),
        np.array(prior),
        np.vstack(train_blocks),
        np.vstack(held_blocks),
    )


def source(seed, kind):
    rng = np.random.default_rng([seed, kind, 8511])
    if kind == 0:
        a, b = map(int, rng.choice([1, 2, 3], size=2, replace=False))
        trans = tuple((j ^ a, j ^ b) for j in range(4))
    else:
        forward = tuple((j + 1) % 4 for j in range(4))
        other = tuple((j - 1) % 4 for j in range(4)) if kind == 1 else (1, 0, 2, 3)
        pair = (other, forward) if rng.integers(2) else (forward, other)
        trans = tuple(zip(*pair, strict=True))
    return trans, 1 << int(rng.integers(4))


def fit_data():
    held = heldout()
    cases, observations, targets = [], [], []
    for seed, kind in product(range(96, 112), range(3)):
        trans, mask = source(seed, kind)
        short = np.array([visible_walk(trans, mask, w) for w in WORDS], dtype=np.uint8)
        long = np.array([visible_walk(trans, mask, w) for w in held], dtype=np.uint8)
        rng = np.random.default_rng([seed, kind, 8512])
        signed = np.zeros(len(WORDS), dtype=np.int32)
        for repeat in range(1, 34):
            for idx in rng.permutation(len(WORDS)):
                # Ordered raw word, query, then a single noisy binary answer.
                answer = int(short[idx]) ^ int(rng.random() < ETA)
                raw = (*WORDS[idx], 2, 3 + answer)
                address = INDEX[raw[:-2]]
                signed[address] += 2 * (raw[-1] - 3) - 1
            if repeat in REPETITIONS:
                cases.append((seed, kind, repeat, trans, mask))
                observations.append(signed.copy())
                targets.append(long)
    return cases, np.array(observations), np.array(targets)


def posterior(logs, held):
    top = np.argmax(logs, axis=0)
    offsets = np.max(logs, axis=0)
    weights = np.exp(logs - offsets)
    mass = weights.sum(axis=0)
    weights /= mass
    return top, np.log(mass) + offsets, weights.T @ held


def parity_matrix(words):
    names = [(w.count(0) % 2) + 2 * (w.count(1) % 2) for w in words]
    return np.array([[(s >> j) & 1 for j in names] for s in range(16)])


def run():
    trans, ids, masks, sizes, prior, short, held = catalogue()
    cases, signed, truth = fit_data()
    rows = []
    # The matrix product forms signed integer counts. Their largest possible
    # absolute value is 8,415; binary32 represents every summand and sum exactly.
    scores = short.astype(np.float32) @ signed.T.astype(np.float32)
    scale = log((1 - ETA) / ETA)
    top, z, pred = posterior(prior[:, None] + scale * scores.astype(float), held)
    plog = scale * (parity_matrix(WORDS) @ signed.T) - log(16)
    _, pz, ppred = posterior(plog, parity_matrix(heldout()))
    for j, (seed, kind, repeat, actual, truth_mask) in enumerate(cases):
        best = int(top[j])
        table = trans[ids[best]]
        mask = int(masks[best])
        data = packet(table, mask)
        assert unpack(data) == (table, mask)
        commutes, involutive = laws(table)
        gp = float(np.exp(-np.logaddexp(0.0, pz[j] - z[j])))
        forecasts = {
            "general": pred[j],
            "toggle": ppred[j],
            "mix": gp * pred[j] + (1 - gp) * ppred[j],
            "installed": held[best],
        }
        target = ETA + (1 - 2 * ETA) * truth[j]
        floor = risk(target.mean(), target, V)
        gains = {
            k: floor - risk(ETA + (1 - 2 * ETA) * v, target, V)
            for k, v in forecasts.items()
        }
        rows.append(
            {
                "seed": seed,
                "kind": ("xor", "cycle", "order")[kind],
                "repetitions": repeat,
                "training_words": repeat * len(WORDS),
                "training_raw_tokens": repeat * 2048,
                "installed_states": int(sizes[best]),
                "transitions": table,
                "readout": mask,
                "packet_hex": data.hex(),
                "exact_all_words": equivalent(table, mask, actual, truth_mask),
                "commutes": commutes,
                "involutive": involutive,
                "general_family_mass": gp,
                "query_gain": gains,
                "full_token_gain": {k: v / 26.5 for k, v in gains.items()},
                "oracle_query_gain": floor - risk(target, target, V),
            }
        )
    return rows


def from_signs(signs, q):
    suffix = words_upto(max(0, q - 2))

    def sig(w):
        return tuple(signs[INDEX[w + v]] for v in suffix)

    queue = deque([()])
    indices = {sig(()): 0}
    trans = []
    mask = 0
    while queue:
        w = queue.popleft()
        j = len(trans)
        mask |= int(signs[INDEX[w]]) << j
        children = []
        for a in range(2):
            u = (*w, a)
            signature = sig(u)
            if signature not in indices:
                indices[signature] = len(indices)
                queue.append(u)
            children.append(indices[signature])
        trans.append(tuple(children))
    return tuple(trans), mask


def audit():
    trans, ids, _, sizes, _, short, _ = catalogue()
    raw_laws = np.array([laws(t) for t in trans], dtype=bool)[ids]
    worst = {}
    simultaneous = {}
    for q in range(1, 5):
        selection = sizes == q
        observed = short[selection]
        results = raw_laws[selection]
        canonical_w = [(), (0,), (1,), (0, 1)]
        canonical_hits = observed[:, [INDEX[w] for w in canonical_w]]
        passed = np.ones(len(observed), dtype=bool)
        for length in range(q + 2):
            for w in product(range(2), repeat=length):
                key = (w.count(0) % 2) + 2 * (w.count(1) % 2)
                passed &= observed[:, INDEX[w]] == canonical_hits[:, key]
            if np.array_equal(passed, np.all(results, axis=1)):
                simultaneous[q] = length
                break
        assert q in simultaneous
        for index, eqs in enumerate((((0, 1), (1, 0)), ((0, 0), ()), ((1, 1), ()))):
            comparisons = []
            for u in words_upto(q - 1):
                for v in words_upto(max(0, q - 2)):
                    a, b = (u + e + v for e in eqs)
                    comparisons.append((len(a), INDEX[a], INDEX[b]))
            failed = np.zeros(len(observed), dtype=bool)
            first = np.zeros(len(observed), dtype=np.uint8)
            for length, a, b in sorted(comparisons):
                mismatch = observed[:, a] != observed[:, b]
                first[mismatch & ~failed] = length
                failed |= mismatch
            if index == 0:
                assert np.array_equal(~failed, results[:, 0])
            elif index == 1:
                first_letter = failed
            else:
                assert np.array_equal(~(first_letter | failed), results[:, 1])
            worst[f"{q}/" + ("AB", "AA", "BB")[index]] = int(max(first))
    for seed, kind in product(range(96, 112), range(3)):
        t, g = source(seed, kind)
        recovered = from_signs([visible_walk(t, g, w) for w in WORDS], 4)
        assert equivalent(*recovered, t, g)
    # No two canonical minimal rooted machines here induce the same short-word law.
    packed = np.packbits(short, axis=1)
    assert len(np.unique(packed, axis=0)) == len(packed)
    # Enumerate all two-state transition tables allowing redundant states and names.
    unrestricted = set()
    for raw in product(range(2), repeat=4):
        table = ((raw[0], raw[1]), (raw[2], raw[3]))
        for mask in range(4):
            unrestricted.add(bytes(visible_walk(table, mask, w) for w in WORDS))
    assert unrestricted == {p.tobytes() for p in short[sizes <= 2]}
    checks = 0
    for length in range(1, 7):
        for hidden in product(range(2), repeat=length):
            transitions = []
            outputs = 0
            base = length + 1
            for j in range(length + 1):
                parity = hidden[:j].count(0) % 2
                outputs |= int(parity ^ (j == length)) << j
                transitions.append(
                    tuple(
                        j + 1
                        if j < length and hidden[j] == a
                        else base + (parity ^ (a == 0))
                        for a in range(2)
                    )
                )
            transitions.extend(((base + 1, base), (base, base + 1)))
            outputs |= 1 << (base + 1)
            assert minimal(transitions, outputs)
            assert not laws(transitions)[1]
            for w in words_upto(length + 2):
                assert visible_walk(transitions, outputs, w) == (w.count(0) % 2) ^ (
                    w == hidden
                )
                checks += 1
    return {
        "minimal_rooted_machines_by_size": dict(
            sorted(Counter(map(int, sizes)).items())
        ),
        "reachable_transition_tables": len(trans),
        "model_word_count": short.size,
        "law_classes": dict(Counter(str(tuple(map(bool, x))) for x in raw_laws)),
        "largest_shortest_witness_length": worst,
        "first_complete_canonical_disagreement_depth_by_exact_size": simultaneous,
        "two_state_languages_after_removing_redundancy": len(unrestricted),
        "isolated_defect_word_checks": checks,
        "recovered_from_outcomes_alone": 48,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        data = json.dumps(audit(), indent=2) + "\n"
    else:
        data = (
            '{"registration":"720cb90","rows":[\n'
            + ",\n".join(json.dumps(v, allow_nan=False) for v in run())
            + "]}\n"
        )
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
