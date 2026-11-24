"""Extract the preregistered full-word losses and class masses from the archived Transformer."""

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

import numpy as np
import torch
from address_anchors import load_archived_transformer, score_fivegram
from text import FIT, VOCAB, git_json, tape
from text_persistence import END as START
from text_persistence import SHA as PREVIOUS_SHA

REGISTRATION = "5907fd5"
FIT_SIZE, BLOCK = 32768, 16384
END = START + FIT_SIZE + 3 * BLOCK
SHA = "465c041d897528e706cca4ba39aa3126496cebb07a3aa7886ec5019899d2083a"
CHECKPOINT = "0becbbd8515ac04fb225939cf1e81b594632b4aefd268d0e16f3faa8d16fae9b"


def extract(path, data_dir=None, models_root=None):
    ledger = {
        e["case"]: e["result"]
        for e in git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")["results"]
    }
    src = ledger["ngram"]["train_source"]
    raw = tape(dict(src, bytes_read=2 * END, prefix_sha256=SHA), data_dir)
    tokens = np.frombuffer(raw, dtype=np.uint16)
    assert (
        hashlib.sha256(tokens[:START].astype("<u2").tobytes()).hexdigest()
        == PREVIOUS_SHA
    )
    freq = np.bincount(tokens[:FIT], minlength=VOCAB)
    ids = np.lexsort((np.arange(VOCAB), -freq))[:32].astype(np.uint16)
    parent = json.loads(
        Path(__file__).with_name("text_word_classes_result.json").read_text()
    )
    old = np.asarray(parent["installations"]["global"]["output_ids"], dtype=np.uint16)
    mapping = np.full(VOCAB, len(ids), np.uint8)
    mapping[ids] = np.arange(len(ids))
    target = mapping[tokens[START:END]]
    old_hits = np.isin(tokens[START:END], old).astype(np.uint8)
    mass = np.empty((END - START, len(ids) + 1))
    old_mass = np.empty(len(target))
    nll = np.empty(len(target))
    dense_indices = np.array(
        [0, 31, FIT_SIZE, FIT_SIZE + BLOCK, FIT_SIZE + 2 * BLOCK, len(target) - 1]
    )
    dense = np.empty((len(dense_indices), VOCAB))
    selection = ledger["report"]["selected"]
    assert selection["sha256"] == CHECKPOINT
    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        model, spec, weights = load_archived_transformer(
            selection, ledger[selection["case"]], models_root, directory
        )
        from baselines.transformer import normalized_nll, reporting_inputs

        cols = torch.as_tensor(ids.astype(np.int64), device="cuda")
        oldcols = torch.as_tensor(old.astype(np.int64), device="cuda")
        torch.cuda.reset_peak_memory_stats()
        start = perf_counter()
        high = 0.0
        with (
            torch.inference_mode(),
            torch.autocast(device_type="cuda", dtype=torch.float16),
        ):
            for first in range(START, END, 32):
                for pos, inputs in reporting_inputs(
                    tokens, range(first, first + 32), spec, device="cuda"
                ):
                    ix = np.asarray(list(pos)) - START
                    assert np.array_equal(ix + START, np.arange(first, first + 32))
                    logits = model(inputs, last_only=True)
                    y = torch.as_tensor(
                        tokens[ix + START].astype(np.int64), device="cuda"
                    )
                    z = torch.logsumexp(logits.double(), dim=1)
                    named = torch.exp(logits[:, cols].double() - z[:, None])
                    tail = 1 - named.sum(dim=1, keepdim=True)
                    subset = torch.exp(logits[:, oldcols].double() - z[:, None]).sum(
                        dim=1, keepdim=True
                    )
                    rawloss = z - logits.gather(1, y[:, None]).squeeze(1).double()
                    block = (
                        torch.cat((named, tail, subset, rawloss[:, None]), dim=1)
                        .cpu()
                        .numpy()
                    )
                    mass[ix], old_mass[ix], nll[ix] = (
                        block[:, :33],
                        block[:, 33],
                        block[:, 34],
                    )
                    verify = np.flatnonzero(
                        (dense_indices >= ix[0]) & (dense_indices <= ix[-1])
                    )
                    if len(verify):
                        take = torch.as_tensor(
                            dense_indices[verify] - ix[0], device="cuda"
                        )
                        dense[verify] = (
                            torch.softmax(logits[take].double(), dim=1).cpu().numpy()
                        )
                    if first in (START, START + FIT_SIZE, END - 32):
                        direct = torch.softmax(logits.double(), dim=1)
                        high = max(
                            high,
                            float(torch.abs(direct[:, cols] - named).max()),
                            float(
                                torch.abs(
                                    direct[:, oldcols].sum(1) - subset[:, 0]
                                ).max()
                            ),
                            float(torch.abs(normalized_nll(logits, y) - rawloss).max()),
                        )
        elapsed = perf_counter() - start
        peak = torch.cuda.max_memory_allocated()
        anchors = score_fivegram(
            tokens,
            ledger["ngram"],
            models_root,
            None,
            directory,
            (START + FIT_SIZE + BLOCK, START + FIT_SIZE + 2 * BLOCK),
        )
    assert high < 2e-12 and np.all((mass > 0) & (mass < 1))
    np.testing.assert_allclose(mass.sum(axis=1), 1, rtol=0, atol=4e-15)
    arrays = {
        "mass": mass,
        "target": target,
        "old_mass": old_mass,
        "old_hits": old_hits,
        "nll": nll,
        "ids": ids,
        "old_ids": old,
    }
    signature = hashlib.sha256()
    for name, data in arrays.items():
        signature.update(name.encode())
        signature.update(data.tobytes())
    meta = {
        "registration": REGISTRATION,
        "prefix_sha256": SHA,
        "checkpoint_sha256": CHECKPOINT,
        "checkpoint_file_bytes": weights.stat().st_size,
        "parameters": sum(p.numel() for p in model.parameters()),
        "vocabulary": VOCAB,
        "rolling_context": spec.context,
        "targets": len(target),
        "first_target": START,
        "bytes_arrays": sum(a.nbytes for a in arrays.values()),
        "arrays_sha256": signature.hexdigest(),
        "normalization_error": high,
        "extraction_seconds": elapsed,
        "gpu_peak_allocated_bytes": peak,
        "gpu": torch.cuda.get_device_name(),
        "mkn5": anchors,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        **arrays,
        dense=dense,
        dense_indices=dense_indices,
        dense_targets=tokens[START + dense_indices],
        metadata=np.array(json.dumps(meta)),
    )
    return meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--models-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(args.cache, args.data_dir, args.models_root), indent=2))
