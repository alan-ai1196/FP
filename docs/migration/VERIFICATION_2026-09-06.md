# FP GitHub Baseline Verification — 2026-09-06

Repository: `alan-ai1196/FP`  
Visibility: **private**  
Default branch: `main`  
Clone URL: `https://github.com/alan-ai1196/FP.git`

This verification was performed against GitHub itself after canonicalization and the curated R4.2 historical import. It does not rely on the local scratch tree being implicitly correct.

## 1. Canonical research-state files

The following Git blobs were re-read/verified on `main`:

| file | verified Git blob SHA |
|---|---|
| `README.md` | `b0c19c18140a22b871d05b269f4d72b4602498d6` |
| `FP_THEORY.md` | `fe8603a384f3040f470f797c198b1c4ceaa78fed` |
| `HANDOFF.md` | `0f3b4225d09136b665e79755a3025739c6210d5a` |
| `CLAIMS_AND_STATUS.md` | `0e143c80e60f7faf72247b46760128b4758be6b2` |
| `RESEARCH_HISTORY.md` | `4b7adf036247cffe1328f7f41ea9077635c16029` |
| `OPEN_PROBLEMS.md` | `204fb3ada6ef693ddf2b3dd92819d0a98cd5285f` |
| `IMPLEMENTATION_STATUS.md` | `aaa620d0dc14e8c3c75a087ef8cd060675c5cc50` |

`FP_THEORY.md` was re-read through its final lines and still ends with the intended Foundation-R4 rule: implementation/solver failures do not justify a new semantic mechanism unless they distinguish the declared theory object from the faithful executable object. `HANDOFF.md` was re-read through its final session protocol and explicitly makes the repository, not model identity/chat history, the research state.

## 2. Theory/evidence provenance

The repository contains the compact historical v155 gate catalog plus minimal numerical/model-check evidence for the Foundation-R4 rewrite and v156–v164 attack chain. These are supporting evidence only; `FP_THEORY.md` is the unique normative theory source.

The Git tree is non-truncated and contains the expected `evidence/minimal/` audit JSONs, including Foundation-R4 freeze/congruence/Reference-Compiler model checks and v156/v157/v158/v159/v161/v162/v163/v164 audits.

## 3. Current Reference Compiler boundary

`src/reference_compiler/` is intentionally marked **WIP / NOT FROZEN**. The repository retains readable late-WIP recovery modules:

- `bridge.py`
- `info.py`
- `learner.py`
- `proof.py`

and `RECOVERY_MANIFEST.md`, which records the larger 2026-09-05 module set, later complete-Runtime hardening, and exact SHA-256 values for large late-WIP scratch files where available.

The repository does **not** pretend the final strict Runtime was import-complete or re-frozen. The historical intermediate 24/24 unit and 47/47 gate pass remains intermediate evidence only. GPU/model science remains HOLD until Reference Compiler closure and the target AMP bridge are re-established from the canonical repository.

## 4. R4.2 historical implementation evidence

The sealed historical R4.2/V23 package was recovered and audited, but the old ZIP and embedded Git history were not imported. `experiments/legacy_r4_2_v23/SOURCE_MANIFEST.md` records:

- package SHA-256 `2c3e5091f90a0e5e3bf659dabb04afb0c7cf7b293ea7e7319892a1f8a273ccd4`;
- historical release commit `2f5977d41c78edfebe892af2fe8d789ba9fb8f26`;
- historical release tree `58136ac42efcc50ed27af9e003aaede1ac417458`;
- exact SHA-256 for every recovered source/text file.

The canonical repository retains only the readable historical subset needed to audit the R4.2 implementation shape/failure (`program.py`, `gpu_runtime.py`, `readout.py`, config/data/validation, release metadata and the real-GPU postmortem). Larger superseded files are identified by exact hashes rather than copied into a second maintained codebase.

## 5. Bulk/cache/path audit

The recursive GitHub tree was searched after historical import. No tracked paths matched:

- `*.zip` / archived experiment bundles;
- `__pycache__`;
- `.env`;
- `*.log`;
- nested `.git/` history.

The repository contains no model weights, checkpoints or datasets; `.gitignore` blocks the common weight/checkpoint/cache/environment/build patterns. Repository size at verification was approximately 69 KB.

## 6. Secret audit

GitHub code search returned zero matches for common credential signatures:

- `AKIA`
- `ghp_`
- `github_pat_`
- `hf_`
- `sk-`

No secret/token/environment file was intentionally imported. Environment-dependent historical code uses environment-variable names or data-root paths only; it does not contain credentials.

## 7. Git-history policy

No historical package `.git` directory was imported. R3/R4 history is represented only by selected provenance metadata/docs and the new canonical repository commits.

Temporary connector test refs created during migration do not contain divergent commits; they were moved onto the same canonical commit chain as `main`. The connector available during migration exposes ref update but not ref deletion, so these names may remain as aliases, but there is only one reachable research history. `main` is the sole canonical branch and future work should use it directly unless a deliberate research branch is created for substantive work.

## 8. Clone/takeover readiness

A new researcher/model can now clone the repository and recover the research state without old chat history by reading, in order:

1. `FP_THEORY.md`
2. `HANDOFF.md`
3. `IMPLEMENTATION_STATUS.md`
4. `CLAIMS_AND_STATUS.md`
5. `OPEN_PROBLEMS.md`
6. recent Git commits

The next authorized research task is Reference Compiler implementation closure. New GPU/model science is not authorized by this migration.

**Result: canonical GitHub migration baseline VERIFIED.**
