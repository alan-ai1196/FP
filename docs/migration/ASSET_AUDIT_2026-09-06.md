# FP GitHub migration asset audit — 2026-09-06

## Purpose

This audit records how the pre-GitHub FP research state was classified during the initial migration to `alan-ai1196/FP`. The goal was not to dump the old workspace but to preserve enough canonical state, proofs, evidence and implementation provenance that a new model can continue without chat history.

## Sources inspected

### Current theory/research workspace

The migration workspace contained, among other files:

- Foundation R4 frozen theory (`FP_THEORY_FOUNDATION_R4_FROZEN_2026-09-04.md`);
- Reference Compiler R1 contract;
- v156–v164 adversarial theory/proof drafts;
- Foundation R4 freeze/congruence/Compiler model-check/gate-crosswalk JSONs;
- v156–v164 compact numerical-audit JSONs;
- a late Reference Compiler WIP directory.

### Persistent FP Library

The `/FP` Library contained the historical canonicals and reports plus multiple complete implementation/result ZIPs. Key recovered implementation packages were:

- `FP_NATIVE_FROM_PRIOR_R4_2_V23_3090_ONECLICK_WINDOWS_MSVC.zip` — latest complete R4.2 historical package;
- `FP_NATIVE_FROM_PRIOR_R3_V18_3090_ONECLICK_WINDOWS_MSVC_FINAL.zip` — complete R3 implementation with embedded Git history;
- `FP_R3_1_CODEX_REFERENCE_PACK.zip` — compact R3 contract/reference pack;
- older R1/R2/R3/R4/R4.1 packages and result bundles.

### Current-conversation/generated file surface

The current project file surface confirmed the full Foundation-R4 theory rewrite sequence, v156–v164 audits, R4 freeze artifacts, Reference Compiler contract and eight directly persisted late-WIP implementation modules.

## Historical implementation provenance recovered

### R4.2 / v23

The sealed package recorded:

- commit: `2f5977d41c78edfebe892af2fe8d789ba9fb8f26`;
- tree: `58136ac42efcc50ed27af9e003aaede1ac417458`;
- SHA-256: `2c3e5091f90a0e5e3bf659dabb04afb0c7cf7b293ea7e7319892a1f8a273ccd4`;
- 33 archive files;
- 25/25 fresh-buildhost gates passed; target CUDA checks were deferred.

Its source is retained in `experiments/legacy_r4_2_v23/` because the later real trace falsified the v23 closure claim.

### R3 embedded Git history

The R3 final package contained a real nested Git repository. The recovered coherent commit sequence was:

```text
860b164 r3.1 theory faithful production telemetry
3eacf8e r3.1 snapshot boundary and resume rng preservation
dd86d0c r3.1 results archive identity verification
3d4e1df r3.1 release sealing
2e0cf48 r3.1 docs and source packaging
620c650 r3.1 canonical lifecycle theory
7615225 r3.1 compiler outcome and lifecycle audits
97e5742 r3.1 scheduler wall accounting and compiler throughput
471ba03 r3.1 imported release baseline
```

The old `.git` directory itself was **not** imported. Its provenance is summarized here; R4.2 provides the later complete historical source snapshot.

## Canonicalization decisions

### Canonical

- root `FP_THEORY.md`: newly consolidated sole normative theory source;
- root handoff/status/history/open-problem documents;
- current implementation status and recovery manifest.

### Supporting proof/evidence

- v156 recurrent/capacity attack notes because they contain important proof details;
- compact Foundation-R4/v156–v164 JSON audits required to audit key numerical/model-check statements.

### Historical implementation evidence

- R4.2 source-only implementation and its relevant postmortem/release docs.

### Superseded but not copied wholesale

- historical v1–v155 canonicals and v156–v164 repeated drafts: their research logic is compressed into `RESEARCH_HISTORY.md` and current claims into `FP_THEORY.md`/`CLAIMS_AND_STATUS.md`;
- older R1/R2/R3/R4/R4.1 packages: redundant after R4.2 + provenance summary;
- duplicate ZIP variants.

### Excluded

- `.venv`, caches, `__pycache__`, pip/HuggingFace caches;
- model weights/checkpoints/datasets;
- raw/large run outputs and duplicated bundles;
- build outputs;
- temporary logs;
- nested historical `.git` directories;
- anything unrelated to FP.

## Reference Compiler persistence repair

A key migration finding was that the 2026-09-05 strict Reference Compiler workspace had contained a 22-module package, while only eight late-WIP modules survived as direct final attachments. Historical execution provenance proves that the additional modules were developed and that an intermediate state passed 24/24 unit tests + 47/47 gates. Later complete-Runtime hardening had not been re-frozen.

Therefore the repository **does not** claim that the eight directly persisted files are the complete final package, and **does not** claim the old green test counts for the final intended Runtime. `src/reference_compiler/RECOVERY_MANIFEST.md` records the exact recovered module inventory and design changes so the next model can restore the package without relying on chat history.

## Secret and bulk-artifact policy

Before import, the staging tree was scanned for common key/token/password patterns and suspicious credential filenames. Large/cache/binary patterns are ignored by `.gitignore`; the baseline intentionally contains no `.env`, credentials, model weights, datasets, checkpoint or ZIP bundle.

See the migration verification commit/result for the final GitHub readback status.
