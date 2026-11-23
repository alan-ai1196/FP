"""Learn update directions from bought likelihoods and transfer them to new text decisions."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from text import git_json, tape
from text_shared_state import REPORT_START, train_study
from text_ticket_actions import END as START
from text_ticket_actions import SHA as OLD_SHA
from text_ticket_actions import generate_groups, random_stream
from threadpoolctl import threadpool_limits
from ticket_policy import PERMS, A, B, K, PermutationLearner, menu
from update_subspace import (
    ArmPartitions,
    AssignmentState,
    LearnedBasis,
    ProjectedState,
    RatioState,
    pack_basis,
    unpack_basis,
)

DISCOVER_END = START + 3 * 65536
BLOCK = 32768
END = DISCOVER_END + 3 * 4 * BLOCK
SHA = "56fbe061c9c4de29f4cc3da2bd57b012ca3d5e5cf947195c911b3d988a293168"
REGISTRATION = "46fdab6"
N = 512
PRIORS = ("pooled", "global", "rank_one", "separate")
BANK = PERMS[np.random.Generator(np.random.PCG64(117)).permutation(len(PERMS))]
NAMES = (
    "posterior",
    "ratios",
    "semantic",
    "learned_8",
    "learned_64",
    "learned_512",
    "first_four",
)


def load_data(directory):
    records = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    src = next(
        e["result"]["train_source"] for e in records["results"] if e["case"] == "ngram"
    )
    data = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), directory)
    assert (
        hashlib.sha256(np.asarray(data[:START], dtype="<u2").tobytes()).hexdigest()
        == OLD_SHA
    )
    return data


@dataclass
class Offers:
    names: np.ndarray
    prices: np.ndarray
    purchase: object


def offers(env, panel, group):
    mapping = random_stream(10, panel, group).permutation(K)
    names, prices = menu(random_stream(11, panel, group), N, 0.25)
    return Offers(names, prices, env.purchase_channel(mapping))


def loglik(p, hit):
    return np.log(p) if hit else np.log1p(-p)


def discover(groups, controls=None):
    partitions = ArmPartitions(K, len(BANK)) if controls is not None else None
    bank = LearnedBasis(len(BANK) - 1)
    discoveries, counts, snapshots = [], [0, 0], {}
    learners = [PermutationLearner() for _ in groups]
    choices = [offers(e, 0, g) for g, (e, _, _) in enumerate(groups)]
    for i in range(N):
        for g, (_, priors, _) in enumerate(groups):
            word = priors["reuse"][i]
            a = choices[g]
            j = int(a.names[i])
            learner = learners[g]
            if np.clip(learner.price_threshold(word, None, j), A, B) >= a.prices[i]:
                hit = a.purchase(i, j)
                learner.buy_feedback(word, None, j, hit)
                size = len(bank.rows)
                # Only the realized likelihood vector in anonymous bank order enters basis learning.
                likelihood = loglik(word[BANK[:, j]], hit)
                bank.observe(likelihood)
                if partitions is not None:
                    partitions.observe(j, likelihood)
                counts[g] += 1
                if size != len(bank.rows):
                    discoveries.append([i + 1, g])
        if i + 1 in (8, 64, 512):
            snapshots[i + 1] = (bank.rows.copy(), counts.copy())
            if partitions is not None:
                controls[i + 1] = (
                    [len(np.unique(row)) for row in partitions.labels],
                    partitions.packet(),
                )
    return snapshots, discoveries


def prepare(data, controls=None):
    study = train_study(data[:REPORT_START])
    tokens = np.frombuffer(data, dtype=np.uint16)
    discovery = generate_groups(study, tokens[START:DISCOVER_END].reshape(-1, 3))
    snapshots, milestones = discover(discovery, controls)
    snapshots = {n: (unpack_basis(pack_basis(b)), c) for n, (b, c) in snapshots.items()}
    streams = []
    opportunities = []
    for block in range(4):
        first = DISCOVER_END + block * 3 * BLOCK
        groups = generate_groups(
            study, tokens[first : first + 3 * BLOCK].reshape(-1, 3)
        )
        opportunities.append([len(e.context.history) for e, _, _ in groups])
        for g, (env, priors, _) in enumerate(groups):
            choice = offers(env, block + 1, g)
            for name in PRIORS:
                streams.append((name, block, g, priors[name][:N], choice))
    info = {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "first_transfer_triple": DISCOVER_END,
        "discovery_group_opportunities": [
            len(e.context.history) for e, _, _ in discovery
        ],
        "transfer_group_opportunities": opportunities,
        "basis_additions_opportunity_and_group": milestones,
        "basis": {
            str(n): {
                "rank": len(b),
                "purchases_by_group": counts,
                "shared_payload_bytes": len(pack_basis(b)),
                "packet_sha256": hashlib.sha256(pack_basis(b)).hexdigest(),
                "maximum_orthogonality_error": float(
                    np.max(np.abs(b @ b.T - np.eye(len(b))))
                )
                if len(b)
                else 0.0,
            }
            for n, (b, counts) in snapshots.items()
        },
    }
    return snapshots, streams, info


def matrices(words, seq):
    if seq.shape != (len(BANK), 4):
        raise ValueError("four-word hypothesis bank required")
    return words[:, seq]


def replay(name, word, off, snapshots):
    p = np.empty((N, K))
    feedback = np.full(N, -1, dtype=np.int8)
    residual = 0.0
    if name == "posterior":
        state = PermutationLearner()
        bank = matrices(word, PERMS)
    elif name == "semantic":
        state = AssignmentState(K)
        bank = matrices(word, PERMS)
    else:
        if name == "ratios":
            state = RatioState(len(BANK))
        else:
            basis = (
                snapshots[512][0][:4]
                if name == "first_four"
                else snapshots[int(name.split("_")[-1])][0]
            )
            state = ProjectedState(basis)
        bank = matrices(word, BANK)
    for i in range(N):
        j = int(off.names[i])
        w = state.enumerated_weights(PERMS) if name == "semantic" else state.weights()
        p[i] = w @ bank[i]
        if np.clip(p[i, j], A, B) < off.prices[i]:
            continue
        hit = off.purchase(i, j)
        feedback[i] = hit
        if name == "posterior":
            state.buy_feedback(word[i], None, j, hit)
        elif name == "semantic":
            state.observe(j, loglik(word[i], hit))
        else:
            residual = max(residual, state.observe(loglik(bank[i, :, j], hit)))
    return p, feedback, residual


def summarize(rows):
    forecasts = buys = feedback = 0
    discrepancy = before = residual = 0.0
    payoff = 0.0
    first = None
    for prior, block, g, off, p, bit, r, reference, truth in rows:
        delta = np.max(np.abs(p - reference), axis=1)
        changed = (bit >= 0) != (truth >= 0)
        dif = np.flatnonzero(changed)
        if len(dif):
            witness = [block, g, prior, int(dif[0]) + 1]
            if first is None:
                first = witness
        until = int(dif[0]) + 1 if len(dif) else N
        before = max(before, float(delta[:until].max()))
        discrepancy = max(discrepancy, float(delta.max()))
        residual = max(residual, r)
        forecasts += len(p)
        buys += int((bit >= 0).sum())
        feedback += int((bit != truth).sum())
        payoff += np.where(bit >= 0, bit - off.prices, 0).sum()
    return {
        "opportunities": forecasts,
        "purchases": buys,
        "buy_and_feedback_differences": feedback,
        "first_stream_with_different_decision": first,
        "max_probability_error": float(f"{discrepancy:.7g}"),
        "max_error_through_first_different_decision": float(f"{before:.7g}"),
        "maximum_discarded_increment_norm": float(f"{residual:.7g}"),
        "mean_realized_reward": round(float(payoff / forecasts), 10),
    }


def experiment(data):
    snapshots, streams, report = prepare(data)
    storage = report["persistent_bytes_at_simultaneous_group_beliefs"] = {}
    basis = snapshots[512][0]
    for n in (1, 8, 16, 64):
        storage[str(n)] = {
            "posterior": 8 * len(PERMS) * n,
            "ratios": 8 * (len(PERMS) - 1) * n,
            "semantic": 8 * (K - 1) ** 2 * n,
            "learned": 2 + basis.nbytes + 8 * len(basis) * n,
        }
    all_rows = {name: [] for name in NAMES}
    for prior, block, g, word, off in streams:
        ref, bits, _ = replay("posterior", word, off, snapshots)
        for name in NAMES:
            p, bit, r = (
                (ref, bits, 0.0)
                if name == "posterior"
                else replay(name, word, off, snapshots)
            )
            all_rows[name].append((prior, block, g, off, p, bit, r, ref, bits))
    report["aggregate"] = {name: summarize(rows) for name, rows in all_rows.items()}
    report["by_word_prior"] = {
        prior: {
            name: summarize([r for r in rows if r[0] == prior])
            for name, rows in all_rows.items()
        }
        for prior in PRIORS
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    with threadpool_limits(limits=1):
        receipt = experiment(load_data(args.data_dir))
    if args.check:
        assert receipt == json.loads(args.check.read_text(encoding="utf8"))
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")
    elif not args.check:
        print(json.dumps(receipt, indent=2))
