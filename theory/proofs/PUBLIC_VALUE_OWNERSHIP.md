# Public values must not alias live Runtime authority

Status (2026-09-29): **THREE ACTUAL IMPLEMENTATION COUNTEREXAMPLES; REPAIR IN QUALIFICATION**.
Foundation and ERC-1 are unchanged. The current caller-boundary ownership claim
is reopened; prior successful trajectories are not retroactively fabricated or
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

The candidate repair is being qualified in the linked canonical Git worktree
`F:\FP_passive_boundary`, branch `compiler/passive-boundary`. It changes the
value ownership boundary, not learning or search semantics. Its focused controls
currently block the three witnesses and preserve constructor/getter isolation,
immutable-source identity, internal sharing and four terminal copy failures.
Broader continuation/reporting/installation checks remain required before merge.

The original native text A1 worker remains at its committed `e13348e` inputs.
It does not mutate exported wrappers. This audit neither restarts nor patches
that worker, and cannot turn an unfinished training horizon into a model score.
The ongoing trial still has its original two-hour/96-GiB contract. Keep its
outcome separate from this adversarial caller-boundary qualification.
