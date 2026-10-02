# Public values must not alias live Runtime authority

Status (2026-09-29): **THREE HISTORICAL COUNTEREXAMPLES; REPAIR PASSES FOCUSED, SIXTEEN-SCRIPT CPU AND TWO ACTUAL CUDA AUDITS; SCOPED QUALIFICATION CLOSED**.
Foundation and ERC-1 are unchanged. The historical caller-boundary ownership claim
is falsified; prior successful trajectories are not retroactively fabricated or
erased. Do not borrow the old release as evidence against these new attacks.

## Counterexamples at e13348e

`audit_public_value_boundary.py --historical-only` loads the actual Runtime and
public-port guard from canonical Git `e13348e`, with the existing small token
and finite-search registrations. It changes only supplied/returned wrapper
metadata, through ordinary Python dictionaries. No private Runtime field,
parameter setter, monkeypatched numerical producer or new issuer is used by
the attacks. Loading historical code is audit instrumentation, not a weakened
imitation of the verifier. No corpus or CUDA execution occurs.

1. After revealing target zero, changing a returned snapshot's observation
   target to one changes the next accepted causal context to one. The original
   paid target wire and pending learner target still say zero. The Runtime
   returns `PREDICTED_REFERENCE` without halting.
2. The lazy token probabilities returned by `predict_next` expose their
   committed origin wrapper. Replacing its readout bytes with a row permutation
   preserves column totals and maxima. The next `observe` accepts the altered
   live predecessor at cursor one, without an optimizer commit or halt. Existing
   prediction-cache recomputation therefore does not close this alias.
3. A genuine exhausted reference class has maximum likelihood 1/4. Changing
   the exported `ReferenceClassProof.best_likelihood` to the valid Fraction one
   also changes the retained issuance. `verify_reference_class_proof` accepts
   it at the same revision and decision class although the search still reports
   1/4. Type validation and comparison with the retained object are insufficient
   when the caller can mutate that retained object through the returned value.

The third witness falsifies a concrete reference empirical-optimum proposition
in the existing ordered native class and baseline scope. It is not a new
`CERTIFIED_COMPLETE` class, a population result or an installation experiment.
Evidence is `evidence/minimal/FP_PUBLIC_VALUE_BOUNDARY_COUNTEREXAMPLES.json`.

## Common cause and repair obligation

Frozen dataclasses prohibit ordinary field assignment but still have writable
metadata. Freezing the outer return object, or copying one image-binding wrapper,
does not detach all reachable learner, source, contract and proof wrappers.
Likewise a supplied registration cannot become private merely by retaining it.

For the closed registered Python value model, let mutable nodes include record
wrappers and containers. An inward or outward value transfer must have no such
node shared with the opposite side. Immutable exact scalars and recursively
immutable tuples may share identity. Fixed trusted classes/code and scalar
internals remain outside the component substitution model, as in the existing
canonical-image audit; this is not an arbitrary Python security sandbox.

A graph copy with one memo can preserve complete values and alias relationships
within the recipient graph while separating every mutable node across the
boundary. Structural induction establishes equality of each supported copied
value. The memo preserves repeated references; no constructor or caller copying
hook needs to run. Actual metadata entries, including unexpected ones, must be
copied or explicitly refused, not silently discarded. Unsupported objects and
cycles cannot acquire authority through a partial copy.

The repair must cover constructor declarations, supplied candidate programs,
all public return values and contract getters. In particular it must preserve
independent retained proof issuance and the live reporting freeze. A failed
export after publication must retain that actual prefix and become terminal;
it cannot undo a revealed target or regain continuation authority. Read-only
diagnostics remain passive. Copy work and heap usage are real implementation
costs, not a new semantic architecture action or a free performance claim.

## Qualification and running experiment

The repair was qualified in the linked canonical Git worktree
`F:\FP_passive_boundary`, branch `compiler/passive-boundary`. It changes the
value ownership boundary, not learning or search semantics. Its focused controls
block the three witnesses and preserve constructor/getter/candidate-program
isolation, immutable-source identity, internal sharing, complete extra metadata,
slotted records and four terminal copy failures. Sixteen binary training histories
and 112 training/reporting events stay exactly equal to untouched controls under
repeated public mutations, with both packed and shared storage. The actual private
learner remains identical during frozen reporting; public wrapper identity is
deliberately detached. `FP_PUBLIC_VALUE_BOUNDARY_CPU.json` retains these checks.

`public_values.detached` copies complete dictionary and inherited slot metadata
without constructors or caller copying hooks. The existing public-port guard
detaches every result and every read-only property. Constructor declarations are
copied together; later candidate programs are copied after their existing type,
header and construction-work admission. Invalid foreign proposals retain their
recorded rejection behavior. Copy allocation failure follows the existing
terminal host protocol, including when observation has already published.

Existing construction, events, profiles, search proofs, paired CPU persistence,
installation, ingress, host failures, native-token learning/reporting and shared
retention audits pass during qualification. CPU tensor reuse also preserves
602 complete phase bodies and the bounded eight-unit/report trajectory. Three
audit fixture assumptions were repaired: reporting now checks private frozen
identity separately from detached diagnostic equality; the CPU phase stub
declares its token kind; historical constructor replay uses the historical
declaration's own fields. These changes do not weaken numerical/ownership checks.

The committed-source bundle `audit_public_value_regression.py` passes all sixteen
complete relevant audit scripts at `86423cd`, with assertions enabled and no
source changes during execution. Its separate receipt is
`evidence/minimal/FP_PUBLIC_VALUE_REGRESSION_CPU.json`. This is a scoped
caller-boundary regression, not reissuance of the old complete CPU/CUDA release
or an actual device/performance claim. Actual-device qualification of the new
public copy boundary is supplied separately below.

The [fixed actual CUDA A1 control](../../experiments/next_token/PUBLIC_VALUE_CUDA_A1.md)
now completes both original packed/shared training/reporting workers at
`9d7250d`, each under its four-GiB/180-second host job. Each preserves nineteen
actual phases, 6,340 primitive words and all 19,922,944 retained frame bytes
under public metadata mutations. Exact native histories/reports match untouched
controls; private frozen identity, physical lineage and words remain unchanged.
The final export MemoryError preserves the completed prefix and closes authority.
The actual single 32-MiB arena/reservation remains unchanged, and source is fixed
throughout. `FP_PUBLIC_VALUE_CUDA_A1.json` is terminal; never replay it.

The scoped repair is merged into main at `5be0bd8` after OS identity inspection
established the original text worker's absence on October 2. Production modules
match the qualified source exactly and the focused audit passes on main. Close
this qualification.
The token device controls do not reissue the whole old release, enumerate all
registrations or supply a model score/performance comparison. No further alias,
storage or static-feature variant is due without a new concrete counterexample.

The original native text A1 worker used unchanged committed `e13348e` inputs
and did not mutate exported wrappers. It is now absent with a missing final
receipt; its surviving heartbeat establishes no completed model score or timeout.
Its original journal is reconciled to terminal UNRESOLVED. This audit neither
restarted nor patched that worker. Keep its interrupted attempt separate from
this adversarial caller-boundary qualification.
