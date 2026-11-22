"""Check the algebra on exact finite laws, and audit all trained maps and full text rows."""

import argparse
import itertools
import struct
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from shared_readout import MULTIPLIERS, address
from text import VOCAB
from text_addresses import TOTAL_MASS
from text_shared_state import REPORT_START, SOURCE, load_data, train_study
from threadpoolctl import threadpool_limits


def normalize(weights):
    s = sum(weights)
    return tuple(w / s for w in weights)


def group_update(p, ids, odds, raw=(), tau=1):
    mass = sum(p[j] for j in ids)
    cond = normalize([p[j] * r for j, r in zip(ids, odds, strict=True)])
    if raw:
        cond = normalize([r + tau * c for r, c in zip(raw, cond, strict=True)])
    updated = list(p)
    for j, c in zip(ids, cond, strict=True):
        updated[j] = mass * c
    return tuple(updated)


def singleton(p, j, rho):
    weights = list(p)
    weights[j] *= rho
    return normalize(weights)


def check_small():
    groups = ((1, 2), (3, 4, 5))
    n = 0
    for raw in itertools.product((1, 3), repeat=6):
        p = normalize(list(map(F, raw)))
        for rho in map(F, MULTIPLIERS):
            src = singleton(p, 0, rho)
            one = group_update(p, groups[0], (3, 1))
            both = group_update(one, groups[1], (2, 4, 1), (1, 2, 0), 8)
            s1 = group_update(src, groups[0], (3, 1))
            joint = group_update(s1, groups[1], (2, 4, 1), (1, 2, 0), 8)
            backwards = group_update(p, groups[1], (2, 4, 1), (1, 2, 0), 8)
            assert group_update(backwards, groups[0], (3, 1)) == both
            assert singleton(both, 0, rho) == joint
            assert sum(joint) == 1
            for ids in groups:
                assert sum(both[j] for j in ids) == sum(p[j] for j in ids)
            for j in range(len(p)):
                assert joint[j] * p[j] == src[j] * both[j]
            n += 1
    return n


def unpack_map(wire, counts):
    mode, default, n = struct.unpack_from("<BBH", wire)
    values = np.full(VOCAB, default, dtype=np.uint8)
    if mode == 0:
        assert len(wire) == 4
    elif mode == 3:
        cutoffs = list(struct.iter_unpack("<IH", wire[4:]))
        assert len(cutoffs) == n == 8
        for i, f in enumerate(map(int, counts)):
            values[i] = sum((-f, i) > (-limit, last) for limit, last in cutoffs)
    else:
        sparse = mode == 1
        assert sparse or mode == 2
        ids = (
            struct.unpack_from("<" + str(n) + "H", wire, 4) if sparse else range(VOCAB)
        )
        start = 4 + (2 * n if sparse else 0)
        assert len(wire) == start + (len(ids) + 1) // 2
        for i, u in enumerate(ids):
            values[u] = (wire[start + i // 2] // (16 if i % 2 else 1)) % 16
    return values


def check_text(data):
    with threadpool_limits(limits=1):
        study = train_study(data[:REPORT_START])
    base = study.base
    c = base.common
    addresses = {
        a.payload: a
        for models in study.models.values()
        for model in models.values()
        for a in model.maps
        if a is not None
    }
    dense = address(np.arange(VOCAB, dtype=np.uint32) % 9)
    for a in (dense, study.source, study.constant):
        addresses[a.payload] = a
    for wire, a in addresses.items():
        assert np.array_equal(unpack_map(wire, c.counts), a.codes)

    # Preserve the source learner's entire input while rewriting every negative target.
    original = np.array([7, 10, SOURCE, 11, 2, 13, 0, 1, 8], dtype=np.uint16)
    changed = original.copy()
    changed.reshape(-1, 3)[1:, 2] = [5, 9]
    for l, r in zip(
        base.source_panel(original, 0, 9), base.source_panel(changed, 0, 9), strict=True
    ):
        assert np.array_equal(l, r)

    perm = np.array([8, 3, 1, 5, 0, 7, 2, 6, 4])
    all_ids = np.arange(VOCAB)
    study_maps = study.models[262144]
    for head in study_maps["reuse"].heads:
        permuted = np.empty_like(head.odds)
        permuted[perm] = head.odds
        assert np.array_equal(
            head.odds[study.source.codes[all_ids]],
            permuted[perm[study.source.codes[all_ids]]],
        )

    # Enumerate the integer bigram row for every output, including the pooled tail.
    def row(q):
        den = TOTAL_MASS * int(c.tail) * int(c.rows.outgoing[q] + 64)
        nums = []
        for y in range(VOCAB):
            category = int(c.category[y])
            weight = int(c.unigram[y]) if category == len(c.top) else int(c.tail)
            nums.append(
                int(c.rows.pairs[q, y]) * TOTAL_MASS * int(c.tail)
                + 64 * int(base.mass[category]) * weight
            )
        assert sum(nums) == den
        return nums, den

    rows = study_maps["raw"].raw
    raw_examples = [
        (int(k >> 16) & 65535, int(k) & 65535) for k in rows.keys[[0, -1]].tolist()
    ]
    examples = raw_examples + [
        (0, int(np.argmin(c.outgoing))),
        (SOURCE, int(np.argmax(c.outgoing))),
    ]
    cases = 0
    for u, q in examples:
        nums, den = row(q)
        ids = [int(i) for g in base.groups for i in g]
        other = den - nums[SOURCE] - sum(nums[j] for j in ids)
        coarsened = tuple(
            F(v, den) for v in [nums[SOURCE], *(nums[j] for j in ids), other]
        )
        rho = F(MULTIPLIERS[study.source.codes[u]])
        for model in study_maps.values():
            p = coarsened
            s = singleton(p, 0, rho)
            for g, (head, a) in enumerate(zip(model.heads, model.maps, strict=True)):
                z = int(a.codes[u]) if a is not None else 0
                # This rational is the exact binary64 readout weight, also for rank one.
                odds = tuple(map(F, head.odds[z]))
                members = tuple(range(1 + 4 * g, 5 + 4 * g))
                raw = ()
                tau = 1
                if model.raw is not None:
                    key = (g << 32) | (u << 16) | q
                    i = np.searchsorted(model.raw.keys, key)
                    if i < len(model.raw.keys) and model.raw.keys[i] == key:
                        raw = tuple(map(int, model.raw.counts[i]))
                        tau = model.raw.tau
                p = group_update(p, members, odds, raw, tau)
                s = group_update(s, members, odds, raw, tau)
            assert sum(s) == 1 and singleton(p, 0, rho) == s
            src = singleton(coarsened, 0, rho)
            assert all(s[j] * w == p[j] * src[j] for j, w in enumerate(coarsened))
            cases += 1
    return len(addresses), cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    print("exact finite laws and transformation triples", check_small())
    if args.text:
        maps, cases = check_text(load_data(args.data_dir))
        print("decoded maps over the full raw vocabulary", maps)
        print(
            "joint normalization and ratio checks on enumerated full-alphabet rows",
            cases,
        )
