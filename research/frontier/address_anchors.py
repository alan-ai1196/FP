"""Score the archived five-gram and Transformer on the registered precision-study subpanels."""

import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from mixture_addresses import SUBPANEL, replication_data, starts
from text import ANCHOR, VOCAB, git_json


def selected_model(selection, models_root):
    path = Path(selection["artifact"])
    if models_root is not None:
        path = models_root / path.parent.name / path.name
    with path.open("rb") as stream:
        assert hashlib.file_digest(stream, "sha256").hexdigest() == selection["sha256"]
    return path


def score_fivegram(tokens, record, models_root, scorer, directory, panels=None):
    selected = record["selected"]
    model = selected_model(selected, models_root)
    if scorer is None:
        scorer = model.parents[2] / "report-build/Release/fp_kenlm_report.exe"
    source = directory / "subpanel.bin"

    def total(count):
        reply = subprocess.check_output(
            [str(scorer), str(model), str(source), str(VOCAB), str(count), "256"],
            text=True,
        )
        result = json.loads(reply)
        assert (
            result["status"],
            result["order"],
            result["vocabulary"],
            result["tokens"],
        ) == ("COMPLETE_FROZEN_KENLM_REPORT", 5, VOCAB, count)
        return count * result["mean_nll_nats"]

    losses = []
    for start in starts() if panels is None else panels:
        tokens[start - 4 : start + SUBPANEL].astype("<u2").tofile(source)
        losses.append((total(4 + SUBPANEL) - total(4)) / SUBPANEL)
    return {
        "file_bytes": model.stat().st_size,
        "sha256": selected["sha256"],
        "distinct_training_positions": record["train_source"]["bytes_read"] // 2,
        "block_nll": [round(loss, 9) for loss in losses],
        "mean_nll": round(math.fsum(losses) / len(losses), 9),
    }


def score_transformer(tokens, selected, training, models_root, directory, panels=None):
    import torch

    # Load the exact two model modules used to train the checkpoint from their retained revision.
    root = Path(__file__).resolve().parents[2]
    for name in ("transformer.py", "nanogpt/model.py"):
        target = directory / "baselines" / name
        target.parent.mkdir(exist_ok=True, parents=True)
        target.write_bytes(
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(root),
                    "show",
                    f"{ANCHOR}:experiments/next_token/baselines/{name}",
                ]
            )
        )
    sys.path.insert(0, str(directory))
    from baselines.transformer import (
        Spec,
        Transformer,
        normalized_nll,
        reporting_inputs,
    )

    spec = Spec(**training["model"])
    weights = selected_model(selected, models_root)
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model = Transformer(spec, seed=training["seed"]).cuda().eval()
    model.load_state_dict(torch.load(weights, map_location="cuda", weights_only=True))
    model.requires_grad_(False)
    losses = []
    with (
        torch.inference_mode(),
        torch.autocast(device_type="cuda", dtype=torch.float16),
    ):
        for start in starts() if panels is None else panels:
            terms = []
            for first in range(start, start + SUBPANEL, 32):
                for positions, inputs in reporting_inputs(
                    tokens, range(first, first + 32), spec, device="cuda"
                ):
                    logits = model(inputs, last_only=True)
                    targets = torch.as_tensor(
                        tokens[list(positions)].astype(np.int64), device="cuda"
                    )
                    terms.extend(normalized_nll(logits, targets).cpu().tolist())
            assert len(terms) == SUBPANEL
            losses.append(math.fsum(terms) / SUBPANEL)
    return {
        "file_bytes": weights.stat().st_size,
        "sha256": selected["sha256"],
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "loaded_parameter_bytes": sum(
            p.numel() * p.element_size() for p in model.parameters()
        ),
        "distinct_training_positions": training["train_source"]["bytes_read"] // 2,
        "training_target_exposures": training["training_target_exposures"],
        "block_nll": [round(loss, 9) for loss in losses],
        "mean_nll": round(math.fsum(losses) / len(losses), 9),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--models-root", type=Path)
    parser.add_argument("--kenlm-reporter", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    panels_group = parser.add_mutually_exclusive_group()
    panels_group.add_argument(
        "--shared",
        action="store_true",
        help="score the later frozen history-transfer panels",
    )
    panels_group.add_argument(
        "--word-classes",
        action="store_true",
        help="score the raw word-class reporting panels",
    )
    panels_group.add_argument(
        "--nested",
        action="store_true",
        help="score the nested word-class calibration panels",
    )
    panels_group.add_argument(
        "--response-classes",
        action="store_true",
        help="score the chronological missing word-pair panels",
    )
    panels_group.add_argument(
        "--partition-posterior",
        action="store_true",
        help="score the continuing posterior-prediction panels",
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    ledger = git_json("evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json")
    records = {entry["case"]: entry["result"] for entry in ledger["results"]}
    if args.partition_posterior:
        from text_partition_posterior import REGISTRATION, load_data, report_starts

        data, panels, registration = (
            load_data(args.data_dir),
            report_starts(),
            REGISTRATION,
        )
    elif args.response_classes:
        from text_response_classes import REGISTRATION, load_data, report_starts

        data, panels, registration = (
            load_data(args.data_dir),
            report_starts(),
            REGISTRATION,
        )
    elif args.nested:
        from text_nested_class import REGISTRATION, load_data, report_starts

        data, panels, registration = (
            load_data(args.data_dir),
            report_starts(),
            REGISTRATION,
        )
    elif args.word_classes:
        from text_word_classes import REGISTRATION, load_data, report_starts

        data, panels, registration = (
            load_data(args.data_dir),
            report_starts(),
            REGISTRATION,
        )
    elif args.shared:
        from text_shared_state import REGISTRATION, load_data, report_starts

        data, panels, registration = (
            load_data(args.data_dir),
            report_starts(),
            REGISTRATION,
        )
    else:
        data, panels, registration = (
            replication_data(args.data_dir),
            starts(),
            "ed60c61",
        )
    tokens = np.frombuffer(data, dtype=np.uint16)
    selection = records["report"]["selected"]
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        result = {
            "registration": registration,
            "targets_per_block": SUBPANEL,
            "first_targets": list(panels),
            "mkn5": score_fivegram(
                tokens,
                records["ngram"],
                args.models_root,
                args.kenlm_reporter,
                directory,
                panels,
            ),
            "transformer": score_transformer(
                tokens,
                selection,
                records[selection["case"]],
                args.models_root,
                directory,
                panels,
            ),
        }
    if args.check:
        old = json.loads(args.check.read_text(encoding="utf8"))
        for arm in ("mkn5", "transformer"):
            for field in ("block_nll", "mean_nll"):
                np.testing.assert_allclose(
                    old[arm][field], result[arm][field], rtol=0, atol=2e-5
                )
                old[arm][field] = result[arm][field]
        assert old == result
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf8")
    elif not args.check:
        print(output, end="")
