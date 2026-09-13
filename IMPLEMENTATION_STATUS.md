# FP Implementation Status

## Current release (2026-09-13)

**Reference/CPU and RTX 3090 AMP baseline: FROZEN. Prospective v2 extension:
separately audited. Registered experiments: UNHELD within their tested scopes.** Source
`5e55eb4f359016d18d68239938bdfb15893238eb` passes all 21 CPU and
10 CUDA audits of that release from one fresh clone; all 38 submodules import
without Torch. Read [target scope](theory/proofs/CUDA_RELEASE_SCOPE.md) and
[integrated evidence](evidence/minimal/FP_CUDA_RELEASE_AUDIT.json). This
includes actual device/resource binding, continuous trajectories, separate
fresh evidence, resident installation, owned policy/run and n=32 target
execution. It is not a model-quality or structural-forcing result.

The current [v2 prospective extension](theory/proofs/OWNED_PROSPECTIVE_SELECTION.md)
removes historical training optimality as a required premise of fresh
installation. It retains paired owned start/current trajectories, all
resource/range/bridge checks and the same atomic physical transition.
Full-class search stays unresolved when its upper is unattained. The
relation proposer now compares only available initialized values, with
prepaid guarded exact work. CPU and actual CUDA extension matrices and the
relevant original installation/policy/reference-acceleration regressions pass.
This does not claim that the entire old 31-script release was rerun at a new
source. Its model behavior is now measured separately in RN-2 below.

The first post-release [resource experiment](experiments/erc1_rtx3090/RESULTS.md)
now completes all 54 registered configurations: 44 sealed, ten unresolved;
2,133 CUDA and 2,134 binary64 outputs independently replayed. Its natural
phase-evidence exhaustion required an experiment reporter correction,
not a Runtime change. Range/precision failures retain their own paths and
no closure. Next work is model science, not more implementation release gates.

The first [ordinary-data model experiment RN-1](experiments/relation_noise/RESULTS.md)
also completes: 36 workers, 18 sealed FP streams, ten bounded historical
selections and nine installations, with 12,564 independently checked CUDA
and binary64 phases each. Eight conditioned connected cases work; all eight
IID cases stop before candidate construction because the empirical fitted
scale is absent from the registered initializer. Strong exact/AMP posterior
controls show the observed relations remain learnable. This is a scoped
solver/strategy limitation, not a runtime correctness or Foundation failure.
The extension above separates full-class completeness from prospective
candidate evidence.

[RN-2](experiments/prospective_relation/RESULTS.md) completes at `5bcbb49`:
28 new workers, twenty sealed FP streams, nineteen actual installs and one
finite no-install outcome. All sixteen IID cases (eight known, eight new)
install with their full classes still unresolved. Four diagnostics retain
historical bounds. There are 17,064 independently replayed CUDA/binary64
phases each, 1,280 newly executed posterior forecasts, 96 independently
recomputed new scores and twenty prospective decision replays. The known
proposal/installation failure is closed in this scope; the disconnected
uncertainty counterexample remains a model-science problem.

The [component symmetry v3 proposal](theory/proofs/COMPONENT_SYMMETRY_PROPOSAL.md)
now constructs only within-component products and leaves unseen relative
flips uniform at the initialized one-hot endpoint. It preserves the complete
native decision class, guarded reachable scale selection and v2 owned paths.
`scripts/audit_component_symmetry.py` covers exact averaging, tied data,
grammar refusal, actual installation and two distinct learner continuations.
Source-bound CPU/CUDA reports and the eighteen-worker RN-3 execution are
pending; this is not another complete baseline release declaration.

The earlier Reference/CPU 21-script prerequisite passed from a
clean clone of `ebe2c4cf23f296fe517d4fe237cef45eaa98d309`, using CPython
3.12.9 on 64-bit Windows 11. All 30 package modules at that revision import.

Read [`REFERENCE_RELEASE_SCOPE.md`](theory/proofs/REFERENCE_RELEASE_SCOPE.md)
and [`FP_REFERENCE_RELEASE_AUDIT.json`](evidence/minimal/FP_REFERENCE_RELEASE_AUDIT.json).
The frozen scope is the registered native constructor decision classes plus
actual baseline, complete exact/CPU binary64 learners, owned single-root
strategy, resource/history/freshness enforcement and serialized CPU install
and finite run protocol. The 47-obligation map preserves scoped theorem,
absent-authority and held-target distinctions; it is not 47 execution passes.

The new independent endpoint model covers 36 runs/2,665 native members,
2,619 exact scores, 46 unresolved range members and three halted ordinary
commits; 23,274 binary64 phases are independently replayed. The trained
774-member install, 64 complete policy streams and actual n=32 hierarchical
chain in a 1 GiB job pass in the same integration. Three old resource-boundary
assertions required calibration against their own paid manifest; no Runtime
implementation change was needed during this release integration.

The target declaration changes documentation/evidence only. All 15 closure
obligations below are satisfied for this registered scope, including actual
AMP trajectories, resource ownership, same-path persistence and structural
installation. Foundation R4 and ERC-1 remain unchanged; static special cases
stay parked. The following component notes retain their individual scopes
and integration history, not additional release prerequisites.

Actual CUDA correctness diagnostics now execute on RTX 3090. The
[`primitive audit`](scripts/audit_cuda_primitives.py) checks all finite half
encodings, every half conversion cell's single midpoint/neighbours and
11,040 finite arithmetic results. It reproduces positive double-rounding,
contraction, divisor-residence and readout differences; see
[`ACTUAL_CUDA_PRECISION.md`](theory/proofs/ACTUAL_CUDA_PRECISION.md).
This closes a finite diagnostic, not an owned AMP learner or target gate.

The subsequent [`continuous CUDA learner`](theory/proofs/CONTINUOUS_CUDA_LEARNERS.md)
now executes explicit half forward/storage and single accumulation/readout/
backward/master updates. Its independent audit passes 1,306 phases, including
profile and recurrent state, plus 1,340 exact grid checks. Actual intermediate
overflow masked by finite projection is refused. `cuda_learner.py` is a
mechanical component; its subsequent owned Runtime integration is described
below. The target `install` port still returns UNRESOLVED.

The [bounded CUDA tensor arena](theory/proofs/BOUNDED_CUDA_TENSOR_STORAGE.md)
now contains all 1,306 phases, including every tensor temporary: one 16 MiB
allocation/reservation, 32,996 initialized extents and no further allocator
events. Admission pays actual segment size, explicitly binds a persistent
allocator setting absent from an apparently default snapshot, and detects
freed escaped allocations with lifetime counters. The audit also checks 216
complete typed extent sequences. This is scoped tensor-storage closure;
driver/context accounting, target range, persistence and installation remain
separate obligations.

The [owned CUDA prefix](theory/proofs/OWNED_CUDA_PREFIX.md) is now integrated.
Runtime registers actual execution identity and tolerances, prepays fixed
phase evidence, retains private continuous device states and checks full
exact/reference relations. Reference and CUDA successors publish together;
partial execution cannot advance either published learner. The independent
audit covers 1,024 phases across all 64 short streams, 44 recurrent/profile
phases with optional CPU binary64, and 41 phases for a 35-member native class.
Actual caps, unexecuted endpoints, malformed backend results, combined
executor/evidence failure and normalization mismatch remain explicit failures.
CPU install/run authority cannot omit a CUDA-bearing root. This is finite
prefix closure; the next range/evidence component is implemented below.

The [owned CUDA range and persistence](theory/proofs/OWNED_CUDA_PERSISTENCE.md)
now bind current device masters, full queues and the complete declared
domain to monotone rounded bounds. The v2 prefix also checks every actual
forecast against an exact mixed-arithmetic model. Runtime admits independent
fresh CUDA stored-mass evidence before context, pays its alpha and owns
current lineage/range identities through learning. The audit passes all
32 five-label null branches, 832 independent CUDA phases and 62 conditional
wealth inequalities, plus six range recomputations on a trained 12-event
path beside CPU binary64. A reference-only crossing, future half range
failure and injected one-ULP forecast mismatch remain explicit refusals.

`PAIRED_CUDA_CROSSED` is a conditional same-path evidence result. The next
[owned CUDA installation](theory/proofs/OWNED_CUDA_INSTALLATION.md) now checks
historical native selection, both current crossings and the complete actual
device state. Registered resident identity transport preserves all CUDA
objects and extents; one serialized root publication changes deployment,
transfers packed-buffer roles and ends old search/persistence authority.
Whole-arena resource roles were shared from birth and remain unchanged.

The actual endpoint audit installs complete 35-/774-/124-member classes,
including nonzero learned parameters and two-position delayed queues. Its
151/870/240 CUDA phases and optional CPU paths have independent replays.
Two successive installs at cursors 22 and 38 retain fresh identities and
spent alpha. Actual byte/work caps and pending work refuse preparation;
state-shape corruption revokes old crossings, and a view beyond its owned
extent is rejected before numeric access. The common CPU/CUDA transaction
also passes the complete CPU install, owned-policy, host-failure and run
regressions. Read `scripts/audit_cuda_installation.py` and its minimal evidence.

This component is included in the complete target integration above. It
is not an all-kernel theorem and adds no semantic architecture action.

The separate [resource observation audit](theory/proofs/CUDA_RESOURCE_OBSERVABILITY.md)
now executes a direct CUDA 32 MiB allocation/write/free invisible to the
complete native arena snapshot. It is a foreign-call counterexample to
broader history inference, not a legal Runtime action. It also records
actual Windows runtime 13.4 separately from Torch's CUDA build tag 13.2;
the earlier `CUDA_runtime` fields encode the latter. This identifies the
remaining registration/observation boundary without changing the scoped
arena or exact numerical evidence.

The next [resource component](theory/proofs/WHOLE_BOARD_CUDA_RESOURCES.md)
now binds actual runtime/API 13040 and display driver 616.92 independently
of Torch's build tag. Every CUDA root owns the native ordinal-to-PCI-to-UUID
binding and charges the board's 24 GiB physical framebuffer capacity to both
roles, once globally. This is a uniform residency upper, not observed process
usage, exclusive reservation or a cumulative-allocation bound. Caps smaller
than the envelope are refused before native tensor allocation.

The actual device audit covers the foreign 32 MiB witness, version/resource
admission and terminal authority after failed native observations, including
unexpected diagnostic/cleanup failure. One 4 GiB Windows job executes native
selection, fresh evidence, installation and continuation on the same bound
host/device, with 151 independent CUDA phase checks. The device binding is
part of the installation frame. The complete target release combines this
resource component with the execution chain; neither supplies model-quality
or performance claims.

The [owned target policy/run composition](theory/proofs/OWNED_CUDA_POLICY_RUN.md)
now executes through the same Runtime strategy as CPU, with explicitly typed
CUDA rules and identities. Only exogenous event transport remains external;
native selection, fresh admission and current paired crossings lead to the
existing resident install. The completed policy record shares its single
root publication. A mandatory host binding composes with the actual device,
framebuffer and tensor resource declarations.

At the finite horizon the full CUDA frame and current state relations are
checked, target forecast diagnostics are computed from retained words, and
the prepared report receives a final identity check before publication.
`SEALED_CUDA_STREAM` closes all continuation ports; it can contain unresolved
stages and never grants CERTIFIED_COMPLETE or a current target-class optimum.
Actual two-stage execution installs at 22/38 and seals at 60 with 456 CUDA
and CPU phase checks. Run `scripts/audit_cuda_policy_run.py` for trained,
recurrent, finite-branch, resource-horizon and failed-publication controls.
The [existing hierarchical AMP fixture](theory/proofs/OWNED_CUDA_HIERARCHY.md)
also passes: n=32, installation at 330, closure at 622, 1,963 CUDA and 1,963
binary64 phases checked independently. Its 74-node witness and empirical
upper cover the same broad reference constructor class. The smaller SUM
training tie remains bitwise equal on actual forecasts; disconnected worlds
both install with opposite unseen relations, while misleading connected
relations finish unresolved. All five actual target workers pass under their
original 4 GiB host caps. Complete target release integration now passes as
recorded above; no Foundation/ERC-1 change or new static case is involved.

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

The migration preserved directly persisted late-WIP modules (`bridge.py`, `info.py`, `learner.py`, `proof.py`) plus a recovery manifest describing the larger scratch module set. Those original bytes remain in Git. Current learner/info implementations replace the callbacks; current proof data describe only the scoped Runtime-issued reference comparison below. The bridge remains reserved. The historical false-authority audit still executes the original modules verbatim from their recovery commit.

Large late-WIP `build.py`, `compiler.py`, `persistence.py`, and `runtime.py` were intentionally **not** committed as ad-hoc encoded fragments: they were not an import-complete or frozen release, and preserving a fragment encoding would make a transport workaround part of the canonical project design. Their SHA-256 values remain recorded for provenance in the recovery/migration notes. Reconstruct the complete package against `FP_THEORY.md`, using the preserved modules and the historical R4.2 implementation only as an implementation reference, then re-run all gates.

At migration the repository therefore treated the Reference Compiler source
as a **recovery/WIP branch point**. The scoped current release and its actual
integration evidence are recorded at the top of this document.

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

**Scope of this construction audit.** The `ConstructionContract` is only
the enforced construction slice of ERC-1. Packed-payload bytes/reference
operation charges do not close total host/device memory or bit-time.
This audit alone does not establish query/data-use, learner/profile,
grammar/proof, fresh persistence, AMP or installation closure. The sections
below record subsequent executable integration, including a scoped CPU
installation. No full gate or implementation freeze follows from this audit.

### Executable causal continuation (2026-09-12)

`OnlineContract`, `data_usage.py`, the new `learner.py`/`info.py` and the
same Runtime now execute fixed causal source rules, exact mean-CE projected
SGD and finite-alphabet revealed-data queries. Runtime seals each prediction
before accepting its target, hides within-unit target accumulators from the
forward evaluator, and commits only at a full registered clock boundary.
No query callback, target-at-prediction argument, caller commit flag, supplied
learner state or role reroute is accepted. Newborn local state is initialized
at the common ordinary boundary; retained global source history is paid.

The actual event path retains pre-target, post-observation and post-commit
states. Target ingress is reserved before prediction returns. Subsequent
backend, range, work or coexistence failure keeps the target revealed, all
published input lineages, executed evidence, physical objects, work and
peaks; the incomplete prefix halts. Retiring a lineage retains an owned
shared code reference for its historical event evidence. Old unsafe
proof/bridge signers are quarantined in Git. Subsequent scoped proof
integration is recorded below; bridge importability grants no authority.

`scripts/audit_reference_events.py` checks 960 exact gradient vectors against
an independent forward differential evaluator, all 64 three-event binary
context/target streams with two reference lineages, causal delayed histories,
246 query level/tie cases and public-endpoint failure/role/clock adversaries.
The existing XVII.5 direct-PRODUCT value path executes 512 deterministic
online events and matches its separate scalar recurrence at all 32 commits;
the old scoped CE upper crosses its threshold at unit 13. This is current
Runtime evidence, not an additional static theorem or stochastic experiment.

**Remaining scope:** the registered interface currently exposes exact
revealed train/online data, so query bits do not bound information in every
public snapshot. Query-only access, report-only execution,
general recurrent backpropagation, full Compiler decision authority,
stochastic filtration/fresh persistence/error allocation,
complete host/device resource accounting, certified float64/actual AMP and
atomic install remain open. The packed-payload model omits Python metadata,
scratch and pre-allocation ingress; this prevents a full physical-resource
claim. See [`REFERENCE_RUNTIME_CONTINUATION.md`](docs/REFERENCE_RUNTIME_CONTINUATION.md).
Foundation/ERC-1 stay frozen; Runtime is NOT FROZEN and science stays HOLD.

### Registered profile construction (2026-09-12)

`ProfileSpec` and `construct_candidate(..., profile_id=...)` now execute
paid finite replay inside the newborn value constructor. Original revealed
observation IDs and logged causal source contexts are retained across
passes; reporting labels and unavailable targets cannot be substituted.
Replay uses the registered ordinary optimizer and local clock, preserves
delayed state across passes, and attaches the complete endpoint to the
current ordinary boundary. It cannot overwrite an already running lineage.
All parameter values arise from the initializer and actual optimizer steps.

`scripts/audit_reference_profiles.py` reproduces the existing XVII.5 path
from 16 retained labels with 512 paid replay events, 32 exact dyadic commits
and an unchanged ordinary cursor. The existing dormant-factor path keeps
its five zero coordinates through another 512 replay events. Independent
checks cover all 16 two-event binary context/target streams, reordered
logged causal contexts, recurrent state attachment, data-role/horizon
violations, work/coexistence exhaustion and backend failure after partial
progress. Failed profiles release the newborn's objects while retaining
paid reads, evidence and code ownership. No replayed label becomes fresh.

This closes the scoped registered value-construction path, not a complete
Compiler result. The following section records finite grammar/proof
integration; stochastic fresh persistence/error state, full physical
accounting, actual AMP and atomic installation remain open.

### Finite native reference comparison (2026-09-12)

The Runtime now owns `start_reference_search`/`advance_reference_search`
for immutable `ReferenceSearchSpec` classes. `native_search.py` enumerates
all ordered typed programs under separate node/SUM/PRODUCT/edge/slot caps,
including repeated edges, shared descendants, unused slots, readout roots
and every delayed binding order. A checked explicit cursor prevents skipped
ordinals or premature prefix closure; no score/gradient/support quotient
removes a descendant. Its full cursor/row history has packed Compiler
residency, including old/new workspace coexistence and cancelled history.

Every graph executes its registered initializer and one optional fixed
profile. The objective uses a fixed set of revealed original train/online
contexts with the same frozen endpoint state. Exact likelihood products
order equal-sized empirical CE sums without floating logarithms. All
endpoints and scores are rechecked, and a separate maximum checker binds
the claimed score to the actual live winning program and learner. Any
unresolved row or final verification budget blocks proof issuance.

`ReferenceClassProof` has one fixed kind and is accepted only through a
matching current Runtime issuance and exact class. Its decision class is
the **registered constructor endpoints plus actual deployed baseline**;
the latter can lie outside the grammar. The public result is
`REFERENCE_CLASS_EXHAUSTED`, not complete Compiler `CERTIFIED_COMPLETE`.
No caller-supplied frontier, bound, endpoint, verifier or signed boolean is
accepted. External mutations invalidate active searches and old proofs.

`scripts/audit_reference_search.py` independently checks 14,860 program/class
cases in nine grammars, plus 3,120 saturated count calculations. It executes
110 profile candidates (440 actual replay events, eight changed endpoints)
and ten recurrent/binding candidates. A complete 587-program XOR grammar
finds likelihood 1/12 after every shorter prefix and the whole same-class
P=0 portion stay at 1/16, also the empirical optimal unigram. This is a
bounded implementation audit, not an unrestricted-coefficient exclusion.
Adversaries cover false closure, substituted rows, wrong selection, inflated
scores, backend failure, class/revision tampering and actual numeric/work/
coexistence exhaustion, including failed verification after all rows finish.

Read `theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md` and its minimal audit
JSON. This closes the stated finite endpoint comparison only. Complete
ERC-1 registration, broader Compiler/persistence/error authority, total
host/device accounting, actual AMP and atomic install remain open.
Implementation is still NOT FROZEN; GPU/model science stays HOLD.

### Owned fresh reference persistence (2026-09-12)

The same Runtime now admits a registered reference candidate/base identity
before its first context and owns its complete starting/current learners,
future epoch schedule, rational gain bound, lower wealth, program leases,
event records and global alpha allocation. `StochasticStreamLaw` records
an explicit external process assumption; unread deterministic data still
grant no probability guarantee. Epoch length and the optimizer clock are
separate. Admission uses a shared update boundary; a reference crossing
at a partial optimizer unit grants no install permission.

Positive base and the normalizer cap give a full-class likelihood-ratio
bound. Fixed-term rational logarithm enclosures and downward dyadic wealth
updates preserve the conditional mean-null supermartingale inequality.
First-crossing stopping keeps wealth below `2/alpha`; floor losses can
destroy power. No floating logarithm, user-supplied gain, skipped failed
factor, retrospective epoch or inherited newborn wealth is accepted.
Several preadmitted identities may use one fresh event, each spending its
own alpha. Retirement, cancellation and failed admission never refund it.

`admit_reference_persistence` and `reference_persistence_result` report
`REFERENCE_CROSSED` only for an owned currently continuous reference pair;
finite noncrossing and numerical/resource uncertainty remain UNRESOLVED.
Unexpected failure within an ordinary event halts its prefix. Historical crossing
does not survive as live authority after a failed successor or retirement.
The proof and exact scope are in
`theory/proofs/OWNED_REFERENCE_PERSISTENCE.md`. The external probability law
and conditional null are assumptions, not facts inferred from a finite run.

`scripts/audit_reference_persistence.py` checks paired sealed scores across
six changing optimizer commits, H=3 with update unit two, and an H=1 crossing
at cursor three with a partial accumulator. It executes all 32 five-label
fair-null paths (160 actual events), checks 31 conditional wealth inequalities,
and exercises shared events, old profile/query IDs, nonrefundable alpha,
real integer/work/memory caps and failures before/after crossing. The
separate numerical and statistical kernel audits retain only their exact
counts and minimal counterexamples under `evidence/minimal/`.

This closes a reference evidence slice, not paired reference/AMP persistence.
Complete ERC-1 registration, full physical accounting, complete numerical protocol,
actual AMP event relations, atomic installation and full release gates
remain open. No new Compiler CERTIFIED_COMPLETE or install token is issued.

### Executed exact/reference-binary64 prefixes (2026-09-12)

`OnlineContract.float64` now fixes a checked CPU binary64 backend and exact
state/probability tolerances before execution. The same Runtime owns a
separate finite learner for every constructed reference lineage. Each
initializer, profile event, ordinary prediction, target-driven observation
and optimizer commit executes its actual finite arithmetic. Every scalar
output is checked against a guarded exact nearest/ties-even rounding oracle.
SUM order, separate PRODUCT/addition, division order, projection and the
optional explicit dyadic floor operation are fixed. This is no GPU emulator
claim, and no exact trained endpoint is cast to manufacture a finite trace.

Raw binary64 bits retain signed zero; the whole parameter, delayed queue,
gradient accumulator and optimizer clock state is paid and checked at every
required phase. Exact decoded stored-mass normalization, rounded normalizer
and actual division output are checked separately. Current numerical equality
is not treated as a state quotient. A fixed tolerance checks the current
pair directly; approximate closeness is never composed as an equivalence.

The argument is finite-prefix induction: successful initialization and each
actually executed/checkable next phase establish the registered relation
for that prefix. It makes no unexecuted future or all-context floating range
claim. Refusing the next phase for numeric/tolerance/resource uncertainty
leaves UNRESOLVED. Failed scalar schedules/internal invariants are execution
failures, not native-graph admissibility rejections. A phase whose evidence
allocation fails cannot remain marked as owned CHECKED evidence. Ordinary
failure also invalidates current reference persistence crossings.
An additional retention failure preserves an earlier unexpected executor
failure and both causes; resource exhaustion cannot conceal that defect.

Read `theory/proofs/OWNED_FLOAT64_PREFIX.md`. The primitive and complete
endpoint audits are `scripts/audit_binary_arithmetic.py` and
`scripts/audit_float64_runtime.py`. Their scopes do not close actual
reference/AMP relation, same-path dual persistence, full host/device resource
accounting or atomic installation. The reference protocol must close before
target-device correctness tests, followed by model science. The 47 historical
labels in `docs/history/V155_GATE_CATALOG.md` are a catalog; the old executable
registry was not preserved, so its green count cannot be reused.

### Same-path CPU persistence on four continuous learners (2026-09-12)

`PersistenceRule.score_path` fixes either exact-reference CE or mathematical
normalization of actual binary64 stored masses. Both use the same owned
event/identity engine and separate global alpha debits. Runtime now exposes
`admit_float64_persistence`, `float64_persistence_result` and
`paired_persistence_result`; none accepts an external score, endpoint or
token. Reference record types have been generalized to `PersistenceIdentity`,
`PersistenceEvent` and `PersistenceResult` with explicit path fields.

The physical identity first proves its current whole-domain bounds by
monotone ordered rounded native execution over the registered source domain
and complete delayed invariant. Actual stored-mass sums and rounded
normalizers are separate. Raw division positivity is checked too. Changed
optimizer theta triggers a renewed bound before the identity can extend;
an inconclusive bound terminates evidence without changing FP semantics.
Both initial and current reference/binary64 states are bound to each identity.

Each path uses its own bounded stopped-epoch mean-null under the complete
filtration and explicit external law. Paired CPU evidence requires two
current crossings on the same four starting learners and event schedule.
Crossed statistics freeze while their ordinary learners continue; failed
successors, retirement and missing state allocation remove live authority.
Old profile observations, alpha and wealth are not transferred to newborns.

`scripts/audit_paired_cpu_persistence.py` checks 400 direct-float contexts,
125 delayed states, 24 separately scored learning events, six new optimizer
range bounds, 62 exact conditional inequalities on 32 complete null paths,
and actual resource/identity/failure adversaries. A delta=2^-54 example
crosses reference at event five while actual finite gain is exactly zero.
Read `theory/proofs/PAIRED_CPU_PERSISTENCE.md` for the precise proposition.

This advances CPU four-path/dual persistence protocol. The separately
executed CPU installation is recorded below; complete ERC-1 enforcement,
the historical gate mapping and target AMP remain open. Runtime is NOT
FROZEN and model science remains HOLD.

### Owned installation at one complete CPU root (2026-09-12)

`OnlineContract.cpu_install` now registers a fixed serialized CPython
transition before execution. `install_cpu` accepts only owned historical
proposal and two-path persistence IDs. The proposal proof establishes class
selection at its original cursor; it remains stale as a current maximum
after fresh learning. Installation separately checks the exact selected
starting states, current continuous paired evidence, full optimizer boundary
and current exact/binary64 relation. No current-optimum or complete Compiler
certificate is inferred from their conjunction.

The target and old deployed learner keep every numeric/discrete field and
the identical underlying buffers. Paid preparation allocates metadata and
receipt while both learners coexist. A detached complete lease map transfers
their actual references to fresh deployment/compiler owners. One prepared
root publication changes ownership and deployed ID together, closes paused
searches while retaining frontier/history, and ends old persistence authority
without rebasing wealth or refunding alpha. Unknown Runtime or ledger state
coordinates cannot inherit this fixed transition proof.

A prepublication failure retains the old learners, evidence and frontier,
but changes the complete attempt/revision/resource history. Retired physical
IDs cannot be recycled: a discovered retry collision was fixed by giving
prepared metadata the unique attempt namespace. Cleanup failure halts the
prefix. These claims concern the serialized registered machine; they are
not concurrent caller or crash-recovery guarantees.

`scripts/audit_cpu_installation.py` independently checks 2,016 lease cases
(649 feasible atomic transfers) and executes complete native classes of 35
and 774 programs through selection, fresh learning, dual evidence, install
and later ordinary events. The larger class installs nonzero trained theta;
independent binary64 replay checks 151 and 870 phases respectively. Actual
immutable byte/work limits reject otherwise resident targets when install
preparation cannot fit, without releasing the old learner or refunding work.
Wrong lineage/path/proof, partial units, stale frontiers, unknown job state,
late abort and legal paid retry are also exercised.

A separate continued test compiles and installs twice in the same Runtime
(cursors 22 and 38), with the second search using the actual new baseline.
New evidence starts with unit wealth and new IDs. All four alpha allocations
remain spent across both installs; a third admission is rejected at the
global cap despite available fresh events. Binary64 replay checks another
306 phases, including ordinary continuation after the second installation.

Read `theory/proofs/OWNED_CPU_INSTALLATION.md` and its compact evidence.
The operation returns `INSTALLED_CPU`, with explicit limited scope. Generic
target `install` still returns UNRESOLVED. Complete ERC-1 registration and
host/device accounting, full release-gate mapping and actual AMP remain
open. Foundation/ERC-1 stay frozen; Runtime is NOT FROZEN and science HOLD.

### Paid Compiler control admission (2026-09-12)

Machine v2 introduced paid Compiler control admission, retained by v3. Each
admitted public Compiler control operation pays one fixed work unit through
its immutable role before changing revision, identity or retained history.
This covers construction/retirement, queries, both persistence paths,
search controls and CPU install. Insufficient admission returns UNRESOLVED
without owned mutation (void controls raise `ResourceExceeded`). Ordinary
target observation remains governed by its earlier prepaid ingress, so a
revealed target cannot be refused retroactively. All already admitted
failures retain work, peak, attempts and alpha as before.

The motivating counterexample is executed from Git `8880371`: at work cap
18, 64 unfunded legal construction requests add 64 candidate IDs, owners and
attempts plus 192 resource events, with unchanged paid counters and payload.
Thus the earlier caps imply no finite complete-state storage bound. The
new positive debit proves a bound on admitted control requests, and no
current proof revision changes merely because an unfunded request arrived.

`scripts/audit_control_admission.py` checks 64 denials at each of 11 public
paths, all 96 length-four binary construct/retire command trees under six
work caps, and a 35-program current proof surviving 16 denials. Existing
construction, ordinary/profile/search, reference/paired persistence,
binary64 and two-cycle CPU install audits pass against v2. Cost assertions
now include paid retirement and the install control admission unit.

The separate raw-input counterexample at `5055f3e` is replayed historically:
inputs `1/2^m` entered pending state before the 128-bit guard, retaining
257-/1025-/4097-bit denominators without a work/payload debit. The next
implemented correction is described below. Paid control alone still does
not imply complete host storage; see `theory/proofs/OWNED_CONTROL_ADMISSION.md`.

### Mandatory paid exact byte ingress (2026-09-12)

Machine `packed-reference-payload-v3` requires a registered exact wire
interface. `DataContract.ingress` fixes byte capacity C and maximum chunk q;
`begin_context` prepays work and allocates a C-byte window, a fixed received
count/status slot and an owned identity before offering any bytes. A
detached residency preflight precedes window creation. Failed empty
preparation preserves costs/peak/retired IDs; only a fresh paid retry is legal.

`receive_context` accepts exact bounded bytes at the offered next offset.
It writes within already owned storage without per-chunk history growth.
`finish_context` guards length and leading bits before integer creation,
then uses the existing causal prediction/learning/persistence path. The
one-chunk `predict_next` wrapper accepts encoded bytes, never raw rationals.
The grammar represents every nonnegative rational vector; insufficient byte
or integer capacity gives UNRESOLVED rather than a narrower semantic class.
Received bytes survive malformed, incomplete and over-precision failures.
Fixed terminal status remains writable at zero remaining ordinary work.

The actual learner and persistence sets seal before the first byte. Partial
context reception blocks structural/query/evidence changes and target reveal.
All integration audit producers now use this mandatory public path, including
registered profiles, exact/binary64 evidence and successive CPU installations.
The complete CPU publication frame includes the new ingress coordinates.

`scripts/audit_context_ingress.py` checks 3,072 exact integer/width cases,
85 vectors, length/bit boundaries and all 208 chunkings of one nine-byte
frame (1,328 equal-prefix snapshots). Work/residency denial, preparation
failure/retry, retained numeric/invalid/partial prefixes and 90 forbidden
mid-ingress actions are exercised. The old denominator witnesses now retain
42/139/523 paid wire bytes without oversized pending state. Existing endpoint
audits pass, including 2,016 lease cases and both CPU installation cycles.

Read `theory/proofs/OWNED_CONTEXT_INGRESS.md`. Its invariant is scoped to
serialized registered Runtime state and packed payloads. Total Python heap,
transient copies, arithmetic scratch, general exception/metadata storage,
complete ERC-1/gate enforcement and target AMP remain open. This is no
concurrent/crash-safe transport, full physical or Runtime freeze claim.

### Injective source identity and planned encoding (2026-09-12)

The v3 typed JSON encoder was not injective on supported Python strings:
one astral character and two explicit surrogate code units collapsed before
SHA-256. Both were legal, distinct causal source names. The original public
Runtime at `532d713` constructs a second program that silently replaces the
deployed program's registry entry; its next probability becomes 1/2 instead
of 2/3, with no installation or learner step. This is an exact implementation
counterexample, not a Foundation R4 failure or cryptographic hash attack.

The encoding introduced in machine v4 preserves code points with
streaming typed UTF-8/surrogatepass bytes. ASCII encodings stay compatible;
non-ASCII artifact IDs change. Reusing an owned program address additionally
requires complete validated Program equality. A forced collision gives
UNRESOLVED and cannot overwrite code or masquerade as inadmissibility.

All packed payload requests now prepare exact extents without a duplicate
tagged object tree. `PlannedObject` has a value and size, no buffer or lease;
only Runtime's checked allocation batch permits actual in-place writing.
The target slot remains prepaid. All buffers are private bytearrays and
public snapshots remain byte copies; CPU install retains the same objects.

`scripts/audit_owned_encoding.py` executes the old/new causal-name witness,
235 packed-tree and 240 identity comparisons, all 65,536 BMP code points,
3,072 surrogate/astral boundary classes and the paid allocation failure path.
Under a fixed 8 KiB payload cap and 100,000-edge grammar, old newly traced
Python allocation peaks grow to roughly 62 MB before denial; the revised
three edge-count cases stay around 0.134 MB. The packed peak stays 1,823 bytes.
Traced allocations are a diagnostic, not total heap, a portable constant,
or evidence that the 8 KiB cap covers the physical host.

Read `theory/proofs/OWNED_ENCODING.md`. Mapping-key sorting, scalar text,
interpreter/free-list state, general Runtime metadata and arithmetic scratch
still need complete accounting. ERC-1/gate registration and actual AMP remain
open; full Runtime freeze or GPU science does not follow from this result.

### Terminal host-allocation failure (2026-09-12)

Machine `packed-reference-payload-v5` retains the existing encoding/ingress
and distinguishes checked ledger refusal from actual MemoryError. Under a
fault at construction-result allocation, the original `dfa1583` cleanup
freed a candidate's learner buffers while leaving the candidate callable in
the next prediction. Current construction prepares its result earlier, and
one public boundary closes continuation/authority after any escaped host
allocation failure. Internal handlers propagate it without allocating
cleanup or failure records; existing state slots receive a precreated marker.

`scripts/audit_host_allocation_failure.py` covers 22 ports/352 repeated
refusals, all 20 internal broad handlers, the four writer/eleven ledger-event
sites on the audited construction path, ordinary-event and ledger failures,
current-proof closure and failed installation with retained four learners,
persistence, alpha and work. A real suspended-before-admission Windows child
also refuses an unmodified 128 MiB ingress allocation under a 64 MiB job cap.
This tests actual OS refusal, separately from injected precise failure sites.

Read `theory/proofs/HOST_ALLOCATION_FAILURE.md`. The marker certifies no
recovery or general snapshot availability; it prevents an uncertain prefix
from continuing or authorizing decisions. That audit job alone does not
register the production Runtime; v6 supplies the scoped binding below.

### Live process resource history (2026-09-12)

The host binding introduced in machine v6 accepts `HostResourceContract`
and owns a live binding to the executing 64-bit Windows CPython process.
The fixed process arena is shared by deployment/compiler, charged in full
to each and once globally. Its native process/job commitment cap is the
minimum of the three declared caps. This centrally covers private Python
metadata, copies, diagnostics and arithmetic workspace rather than guessing
per-record overhead. Caller handles, counters or callbacks cannot supply
the binding. The host policy is part of chi and survives CPU root publication.

Public entries check the live immutable fence and whole-process lifetime
peak/CPU history. Unestablished resource premises terminate authority with
no cleanup allocation or refunds; subsequent diagnostic failures preserve
the first host marker. No fallible post-check is added after installation.
Host observations are sampled kernel-state projections, not complete-state
equivalence certificates. The optional unbound reference mode is explicit.

`scripts/audit_bound_host_runtime.py` executes five jobs, including the
35-program search/four-learner persistence/CPU install under 64 MiB, actual
128 MiB ingress refusal, stale/fake observation rejection, and unsuccessful
exit after writing a completed-looking result. A real 80 MiB transient
allocation followed by a new stricter nested job demonstrates that new-job
peaks erase earlier process history; the lifetime check rejects that case.
Read `theory/proofs/BOUND_HOST_RUNTIME.md` and its minimal JSON evidence.

This closes the declared private-commitment dimension in the Runtime, not
complete ERC-1 run/policy/supervision/publication/error ownership, CPU-time
hard caps, shared platform/device resources, target AMP or release-gate
mapping. Foundation/ERC-1 remain frozen; Runtime is NOT FROZEN and science HOLD.

### Owned Compiler strategy (2026-09-12)

Machine `packed-reference-payload-v7` introduced immutable
`CompilerPolicy` data and owns its execution state. At registered post-commit
boundaries it runs complete native-class search, separately admits the two
fresh CPU paths, and attempts the existing checked installation. An incumbent
winner keeps deployment; exhausted search allowance or evidence ends that
stage UNRESOLVED. No supplied graph, fitted values or running policy state
can enter through the strategy declaration.

External policy-mode ports are limited to context/target transport and passive
snapshots; all 17 other current control/authority methods reject. The strategy
calls the same owned implementations internally. Packed policy state and
its work are paid; a retention failure halts without retrying an action whose
cost or alpha has already been spent. Installation prepares the completed
policy buffer and publishes it with the learner in the same root/lease
transaction. Native resource-premise loss now propagates through all internal
broad handlers, including nested public calls, without allocating cleanup.
It is an execution error distinct from `ContractError`, so a checked graph/
argument handler cannot turn missing host premises into graph inadmissibility.

`scripts/audit_owned_compiler_policy.py` exercises the two 35-program cycles,
the trained 774-program class, 64 exhaustive label streams with independent
log/wealth checks, actual refusal paths, and the two-install chain inside a
64 MiB Windows job. Read `theory/proofs/OWNED_COMPILER_POLICY.md` for the
state/filtration argument and exact scope. Global alpha is per actual Runtime
root; separate diagnostic roots are not a shared family error budget.

This closes ownership of the registered sequential strategy. Arbitrary
alternative strategies are outside this claim, not a new static research
program. The subsequent run/report and gate mapping are described below.

### Owned finite run and current release map (2026-09-12)

The run protocol introduced in machine v8 assembles and pays for one
immutable aggregate reference manifest, including initial Program, semantic,
data, value, resource, host, policy and explicit CPU arithmetic coordinates.
Changing a budget can change its own paid encoding cost; the resource-boundary
audit fixtures now calibrate real immutable roots accordingly.

After the final registered ordinary event and its owned policy phase,
Runtime prepares a paid closure and then publishes its terminal pointer.
All 22 non-diagnostic ports close. `RuntimeSnapshot.run` reports execution
status, historical class/proof scope, unresolved stages, graph counts and
retained prediction precision/range diagnostics, alongside the existing full
snapshot's learners, resources and evidence. An unresolved stage does not
make stream completion a structural rejection. Report failure does not undo
an already committed event or installed learner; it leaves the run halted
without a closure. No CERTIFIED_COMPLETE or target AMP authority is added.

Read `theory/proofs/OWNED_REFERENCE_RUN.md` and
`evidence/minimal/FP_REFERENCE_RUN_AUDIT.json`. The new endpoint audit covers
28 exhaustive binary streams, 638 unchanged terminal refusals, unfinished
stages/partial optimizer units, four failure classes, an unknown-job frame
adversary and a full 35-program
search/paired-evidence/install/closure at cursor 22. Its 141 binary64 phases
are independently replayed; the same path runs inside a real 64 MiB job
with actual process identity and successful exit checked externally.

[`REFERENCE_RELEASE_GATE_MAP.md`](docs/REFERENCE_RELEASE_GATE_MAP.md) now
maps all 47 historical obligations to specific endpoint/scoped-theorem
evidence or an explicit open/target requirement. It grants no aggregate pass.
The v9 integration below supplies owned hierarchical anti-unigram discovery
without a supplied latent partition. Final reference integration checks remain;
actual target gates 16/28–30 and the target part of atomicity follow reference
closure. Manual control, absent host binding and unsupported information
interfaces retain their explicit partial scope. Optional broader classes
are not automatically new release prerequisites. Foundation/ERC-1 stay frozen.

### Empirical-upper closure and owned hierarchy (2026-09-13)

Machine v9 adds an independently verified saturated multinomial upper for
the existing frozen-endpoint empirical objective. An actual feasible native
initializer/profile witness attaining it proves a maximum over the full
registered grammar plus baseline. `BoundedReferenceProof` and
`REFERENCE_CLASS_BOUNDED` distinguish this fact from executed enumeration;
no `CERTIFIED_COMPLETE` is added. The new mode reaches the same owned policy,
separate fresh evidence, CPU install and terminal report paths.

The n=32 endpoint receives only ordinary token bytes/labels, derives native
group SUMs and PRODUCT cells, checks all 1,024 source contexts, installs at
330 and seals at 622. Independent replay checks 1,963 binary64 phases and
the real 1 GiB job exits successfully. Exact count-table, 218-program
enumeration, all 16 four-token assignments, actual profile and forged-proof
tests accompany it. Disconnected worlds, a five-node zero-PRODUCT train tie
and consistent-but-false empirical relations bound the interpretation.

This larger execution also required retaining the same actual range buffer
when its immutable program/domain and exact theta agree. Changed theta
still triggers full recomputation and paid replacement before old release;
delays/gradients/optimizer histories are never quotiented. A recurrent case
and post-allocation failure test exercise the ownership invariant. Read
`theory/proofs/SATURATED_REFERENCE_CLASS_BOUND.md` and
`evidence/minimal/FP_REFERENCE_ACCELERATION_AUDIT.json`. Gate 17 now has
current reference evidence. Final release-revision integration remains;
Foundation/ERC-1 are unchanged, Runtime NOT FROZEN and science HOLD.

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
