# FP — Factor Programs

This repository is the canonical persistence layer for the FP research project.

FP studies whether a **typed causal positive program** built from a small native algebra can allocate useful distinctions and physical graph structure under ordinary task loss and hard physical constraints, without an externally supplied architecture-action menu.

## Start here

1. [`FP_THEORY.md`](FP_THEORY.md) — **the only normative theory source**.
2. [`HANDOFF.md`](HANDOFF.md) — current research state and next-model takeover guide.
3. [`CLAIMS_AND_STATUS.md`](CLAIMS_AND_STATUS.md) — proved / numerical / empirical / conjectural / falsified claims.
4. [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) — exact Compiler/runtime state and known migration recovery boundary.
5. [`RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md) — why the theory changed from R5 to the current foundation.
6. [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) — only currently unresolved research questions.

## Current status

- **Theory:** Foundation R4 frozen and consolidated into `FP_THEORY.md`.
- **Reference Compiler:** WIP; **not frozen**. A strict complete-runtime rewrite was in progress when persistence moved to GitHub.
- **GPU/model science:** **HOLD**. No new RTX3090 science is authorized until the complete Reference Compiler runtime passes the required reference gates and the actual AMP path passes its bridge gates.
- **Historical R4.2 implementation:** preserved under `experiments/legacy_r4_2_v23/` because its failure produced the v24 theoretical counterexample. It is not a current implementation.

## Repository discipline

GitHub is the source of truth. Chat memory and local workspaces are scratch context only. Any result with long-term research value must end in a coherent repository commit.

Do not commit model weights, datasets, checkpoints, caches, large raw logs, virtual environments, provider credentials, or regenerated experiment bundles. Preserve the smallest evidence needed to audit a claim plus its generation code/metadata.

## Numerical discipline

- theorem/algorithm/numerical audits: exact arithmetic or float64 reference path;
- physical/GPU execution: registered AMP/mixed-precision path after the reference↔AMP bridge is certified;
- decision-critical near ties: exact encoded arithmetic or sound enclosures, never an arbitrary floating tolerance.

## Scope separation

FP is independent of the separate memory/provenance research project. Do not import that project's problem statements, benchmarks, mechanisms, or claims into FP merely because both use the word “provenance.”
