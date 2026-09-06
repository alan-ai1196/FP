# FP Implementation Status

## Status at GitHub migration (2026-09-06)

**Reference Compiler: WIP — NOT FROZEN.**  
**Historical implementations: recovered and auditable.**  
**GPU/model science: HOLD.**

This distinction is important. A complete implementation existed for older theory versions; the stricter Foundation-R4 Reference Compiler rewrite was still under adversarial integration when persistence moved from chat/local scratch to GitHub.

## 1. Recovered complete historical implementation

`experiments/legacy_r4_2_v23/` is restored from the sealed historical package `FP_NATIVE_FROM_PRIOR_R4_2_V23_3090_ONECLICK_WINDOWS_MSVC.zip`.

Historical release metadata:

- release commit recorded by the package: `2f5977d41c78edfebe892af2fe8d789ba9fb8f26`;
- release tree: `58136ac42efcc50ed27af9e003aaede1ac417458`;
- package SHA-256: `2c3e5091f90a0e5e3bf659dabb04afb0c7cf7b293ea7e7319892a1f8a273ccd4`;
- archive file count: 33;
- fresh build-host gates: 25/25 PASS;
- target CUDA gates were deferred in that package.

It contains the complete `fpnp` package (`compiler_v23.py`, `async_compile.py`, `program.py`, `transaction.py`, `gpu_runtime.py`, `readout.py`, `selftest.py`, etc.) and its source/postmortem docs.

**This code is intentionally classified as `SUPERSEDED`.** The real R4.2 trace became the v24 counterexample: it stayed near the unigram prior and materialized no PRODUCT nodes despite high evidence throughput. Preserve it for audit and code reuse, not as current Compiler semantics.

A still earlier R3 final package was also recovered during migration. It contained its own coherent embedded Git history with commits from imported baseline through theory-faithful telemetry. Its code is not duplicated here because R4.2 is the later complete historical implementation; its commit provenance is recorded in `docs/migration/ASSET_AUDIT_2026-09-06.md`.

## 2. Foundation-R4 Reference Compiler rewrite

On 2026-09-05 the research workspace contained a stricter `fp_reference` module set:

```text
__init__.py
anti_unigram.py
bridge.py
build.py
candidate_factory.py
compiler.py
core.py
data_store.py
data_usage.py
equivalence.py
info.py
learner.py
lineage.py
machine.py
native_search.py
persistence.py
program.py
proof.py
resources.py
runtime.py
search.py
semantics.py
```

An intermediate state ran 24/24 unit tests and a 47/47 executable v155 gate registry. Randomized model checks were also used for search/resource/numerical/native-DAG/anti-unigram behavior.

Then adversarial code review found additional complete-Runtime issues and the API was hardened further, including:

- full resource ownership/refcount in snapshots rather than aggregate totals only;
- no caller-supplied arbitrary branch upper as a completeness proof;
- explicit legal PRODUCT rules and registered delayed state;
- registered value-operation provenance;
- authority-issued build/persistence/bridge/equivalence proof tokens instead of booleans;
- candidate construction chain from zero-valued native program skeleton through registered profiler to deterministic machine realization;
- query range/precision quantization rather than metadata-only bit counts;
- complete Runtime ownership of filtration/data-use/error/e-process/query/search state;
- prediction-visible state separated from target-derived microbatch accumulators;
- four continuous trajectories: deployed-ref, deployed-AMP, candidate-ref, candidate-AMP;
- explicit finite decision class scope for `CERTIFIED_COMPLETE`;
- immutable assignment of work/resource roles;
- fresh observation-use ledger;
- build/install work and build-before-free peak accounting.

The **final endpoint integration after these changes had not been re-run through the full closure battery** before migration. Therefore the earlier green numbers are historical intermediate evidence, not a freeze certificate for the final intended Runtime.

## 3. What is preserved in `src/reference_compiler/`

The migration preserves the directly persisted late-WIP modules that are small enough to remain useful as readable recovery source (`bridge.py`, `info.py`, `learner.py`, `proof.py`) plus a recovery manifest describing the larger scratch module set, sizes, important later-session design changes, and known source hashes where available.

Large late-WIP `build.py`, `compiler.py`, `persistence.py`, and `runtime.py` were intentionally **not** committed as ad-hoc encoded fragments: they were not an import-complete or frozen release, and preserving a fragment encoding would make a transport workaround part of the canonical project design. Their SHA-256 values remain recorded for provenance in the recovery/migration notes. Reconstruct the complete package against `FP_THEORY.md`, using the preserved modules and the complete R4.2 implementation only as implementation references, then re-run all gates.

The repository therefore treats the current Reference Compiler source as a **recovery/WIP branch point**, not a release. Do not report its package as complete until imports/tests are restored and the complete endpoint suite passes.

## 4. Required closure tests

Before an `implementation: freeze reference compiler` commit can be made, require at minimum:

1. clean package import from a fresh clone;
2. no hidden caller path to `CERTIFIED`, persistence authorization, resource-only bypass or install;
3. explicit finite decision-class scope for every completeness result;
4. exact/native candidate construction coverage on small exhaustive grammars;
5. ownership/refcount/peak/cumulative resource model checks;
6. data-role and fresh-data-use checks;
7. global-filtration predictability checks;
8. four-path event-order/cursor continuity checks;
9. authority-issued and state-bound build/proof/bridge/persistence/equivalence tokens;
10. NaN/Inf and sound-enclosure adversarial checks;
11. query output range/finite-precision enforcement;
12. anti-unigram discovery without latent-group oracle;
13. all 47 historical v155 gate obligations mapped to executable runtime/model-check/scoped-theorem evidence;
14. randomized exact-vs-exhaustive model checks after the endpoint path itself is exercised;
15. target AMP bridge only after reference closure.

If the complete Runtime cannot represent a legal `FP_THEORY.md` candidate class without adding a new semantic primitive, stop and reopen theory. If it merely runs out of search/information/certificate budget, return `UNRESOLVED`.
