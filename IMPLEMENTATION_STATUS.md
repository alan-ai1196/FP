# FP Implementation Status

## Status at GitHub migration (2026-09-06)

**Reference Compiler: WIP — NOT FROZEN.**  
**Historical implementations: recovered and auditable.**  
**GPU/model science: HOLD.**

**2026-09-12 update: Experiment Resource Contract ERC-1 is FROZEN as a
specification; executable enforcement is OPEN.** The unified scoped
PRODUCT/SUM/range/precision law is now XVII.31. Read
[`EXPERIMENT_RESOURCE_CONTRACT.md`](EXPERIMENT_RESOURCE_CONTRACT.md).
The next work is the complete Runtime, then the actual AMP bridge and RTX
3090 experiments. Static special-case expansion is parked; the mathematical
resource audit does not restore imports, close authority paths or certify
any device execution.

This distinction is important. A complete implementation existed for older theory versions; the stricter Foundation-R4 Reference Compiler rewrite was still under adversarial integration when persistence moved from chat/local scratch to GitHub.

## 1. Recovered historical implementation provenance

The sealed historical package `FP_NATIVE_FROM_PRIOR_R4_2_V23_3090_ONECLICK_WINDOWS_MSVC.zip` was recovered and audited during migration. The canonical repository keeps a curated readable subset under `experiments/legacy_r4_2_v23/` plus `SOURCE_MANIFEST.md`, which records the exact package identity and SHA-256 of every recovered source/text file. The old ZIP, embedded `.git`, caches, datasets, checkpoints and raw logs are intentionally not imported.

Historical release metadata:

- release commit recorded by the package: `2f5977d41c78edfebe892af2fe8d789ba9fb8f26`;
- release tree: `58136ac42efcc50ed27af9e003aaede1ac417458`;
- package SHA-256: `2c3e5091f90a0e5e3bf659dabb04afb0c7cf7b293ea7e7319892a1f8a273ccd4`;
- archive file count: 33;
- fresh build-host gates: 25/25 PASS;
- target CUDA gates were deferred in that package.

The recovered package itself contained the complete `fpnp` implementation (`compiler_v23.py`, `async_compile.py`, `program.py`, `transaction.py`, `gpu_runtime.py`, `readout.py`, `selftest.py`, etc.). The canonical repository retains only the historical source needed to audit the implementation shape and R4.2 failure; omitted superseded files remain cryptographically identified by `SOURCE_MANIFEST.md` rather than duplicated as a second maintained implementation.

**This historical implementation is intentionally classified as `SUPERSEDED`.** The real R4.2 trace became the v24 counterexample: it stayed near the unigram prior and materialized no PRODUCT nodes despite high evidence throughput. Preserve it for audit and code-reference purposes, not as current Compiler semantics.

A still earlier R3 final package was also recovered during migration. It contained its own coherent embedded Git history with commits from imported baseline through theory-faithful telemetry. Its old `.git` is not imported; its provenance is recorded in `docs/migration/ASSET_AUDIT_2026-09-06.md`.

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

Large late-WIP `build.py`, `compiler.py`, `persistence.py`, and `runtime.py` were intentionally **not** committed as ad-hoc encoded fragments: they were not an import-complete or frozen release, and preserving a fragment encoding would make a transport workaround part of the canonical project design. Their SHA-256 values remain recorded for provenance in the recovery/migration notes. Reconstruct the complete package against `FP_THEORY.md`, using the preserved modules and the historical R4.2 implementation only as an implementation reference, then re-run all gates.

The repository therefore treats the current Reference Compiler source as a **recovery/WIP branch point**, not a release. Do not report its package as complete until imports/tests are restored and the complete endpoint suite passes.

### Executable construction recovery (2026-09-12)

The reconstructed `program`, `semantics`, `resources`, `machine` and `runtime`
modules now provide the actual `ReferenceCompilerRuntime` construction
endpoint. It admits generic typed source/SUM/PRODUCT/delayed bodies, retains
shared/unused parameter coordinates and repeated edges, executes a fixed
registered initializer from zero slot state, and binds constructed states
to actual owned packed buffers. Full finite source-domain checks or a
conservative source/state box give positive/range evidence. A loose bound
or exact integer-work limit produces UNRESOLVED, not a negative certificate.

`scripts/audit_reference_construction.py` checks nine existing resource
fixtures through that endpoint, 80 shared native graphs with 320 independent
exact full-context comparisons, and 1,500 ownership/refcount/role/peak/work
model-check steps. A build that fits alone but cannot coexist with its
incumbent stays unresolved; partial backend failures release actual buffers
without refunding work or peak. This is current executable evidence, unlike
the historical 24/24 and 47/47 counts.

**Scope limits remain material.** The `ConstructionContract` is only the
enforced construction slice of ERC-1. The machine's packed-payload bytes and
conservative reference operation charges do not close total host/device
memory or bit-time accounting. Query/data-use, ordinary learner/profile
continuation, complete grammar search, typed proof authority, fresh paired
persistence, actual AMP and atomic install still need integration. The
preserved helper authorities are not trusted by the current endpoint;
installation remains UNRESOLVED. No full gate or implementation freeze is
claimed by this audit.

## 4. Required closure tests

### Current recovery audit (2026-09-06)

The reconstructed `core.py` restores strict claim/certificate data objects and
typed complete-state identity. `scripts/audit_recovered_authorities.py` executes
the actual recovered authority source and reproduces four false authorizations;
see `theory/proofs/EXECUTION_AUTHORITY_BOUNDARY.md`. These helper imports and
counterexamples do not restore the complete Runtime or validate the old gate
counts. Implementation remains NOT FROZEN; science remains HOLD.

The 2026-09-09 selector counterexample adds a precise theorem-audit obligation
(`theory/proofs/ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md`). Exact exclusion at
bounded PRODUCT count and final range does not establish a positive loss gap;
complete SUM construction resources also matter. Its explicit CPU float64
path rounds a one-PRODUCT table to an exact target that real arithmetic cannot
realize with one PRODUCT. An implementation must keep numerical equality,
exact algebraic class, approximation closure and complete-resource authority
separate. The standalone audit does not exercise or close the missing Runtime.

The 2026-09-11 shared-decoder audit strengthens this obligation
(`theory/proofs/DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`). Its nine-PRODUCT
family uses only {1/2,1,2} SUM coefficients and keeps all features <=1, yet
binary64 can both round away genuine leakage (k=54) and underflow the shared
root before later amplification (k=400). In the latter case every excess
head at context 111 becomes zero although the exact correct excess exceeds
0.999. Maximum-activation bounds alone therefore cannot authorize a bridge.
These are standalone CPU theorem audits; complete Runtime/AMP closure
remains unverified.

The 2026-09-12 conditional-path theorem adds a search-scope counterexample
(`theory/proofs/CONDITIONAL_COEFFICIENT_PATHS.md`). Pure monomial coefficient
paths are complete at unrestricted normalizer range, but requiring each
such path to remain at a fixed cap misses valid conditional limits. A final
positive excess contraction restores the same cap with no added PRODUCT.
The standalone audit verifies supplied rational paths and resource-preserving
graph constructions; generic phase/amplitude solving is not implemented.
Its hidden-node rescaling and finite-alphabet closure results explicitly
allow growing SUM/scaling work and do not authorize a registered Runtime
state rewrite or a numerical bridge.

Before an `implementation: freeze reference compiler` commit can be made, require at minimum:

The complete endpoint must also enforce the frozen ERC-1 manifest and its
separate P/S/edge/range/precision/ownership counters. A low-node high-arity
witness and a high-precision reciprocal witness must pay their respective
physical costs. This is part of the existing complete resource contract,
not a replacement for any of the following gates.

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
