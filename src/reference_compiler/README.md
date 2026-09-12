# Foundation-R4 Reference Compiler — recovery/WIP

**Status: NOT FROZEN.**

The late 2026-09-05 research workspace contained a larger `fp_reference` package than the eight files that survived as direct final attachments. The missing scratch modules are not evidence that the implementation never existed: execution provenance records a 22-module package and an intermediate 24/24 unit + 47/47 gate pass before later complete-Runtime hardening.

This directory contains the current reconstruction; Git retains the directly persisted late-WIP source. Current modules import, but complete Runtime/proof/bridge integration remains open. See root `IMPLEMENTATION_STATUS.md` and `RECOVERY_MANIFEST.md` before editing.

Do not “fix” imports by weakening the contract or copying old R4.2 semantics into the new Runtime. Recover/implement the missing modules against `FP_THEORY.md`, then run the complete endpoint gates.

## Current executable recovery (2026-09-12)

`fp_reference.ReferenceCompilerRuntime` now owns native **construction and
exact ordinary continuation**: typed skeleton admission, complete parameter slots, fixed registered
initialization, delayed-state reset, conservative/full-finite-domain range
checking, actual packed reference buffers, owners/refcounts and immutable
resource-role charges. Its snapshots retain current constructed states,
program/buffer registries, resource history and failed attempts. An immutable
`OnlineContract` adds causal source reads, exact projected mean-CE SGD,
fixed update units, revealed-data roles/use, finite-alphabet queries and
preregistered newborn profiles. `construct_candidate(..., profile_id=...)`
executes paid replay of the retained original IDs and keeps complete value,
optimizer and delayed state at its ordinary boundary attachment.
`start_reference_search`/`advance_reference_search` enumerate all ordered
native syntax in five explicit finite caps. Every program runs that same
registered constructor; a checked explicit cursor cannot skip a region.
Runtime issues only a current typed maximum proof for fixed-state empirical
CE over this constructor class plus the actual deployed baseline.

This uses the explicit `ConstructionContract` slice, not the complete ERC-1
run manifest. The registered machine counts retained packed reference payload
bytes and conservative reference operation charges; it does not claim total
CPython heap, bit-time, GPU memory or CUDA work accounting. Numeric integer
work limits and inconclusive range bounds produce UNRESOLVED. Intermediate
build failures release partial buffers without refunding spent work or peak.

Run `python -B scripts/audit_reference_construction.py` and
`python -B scripts/audit_reference_events.py` and
`python -B scripts/audit_reference_profiles.py` and
`python -B scripts/audit_reference_search.py` from repository root. They
exercise the actual Runtime and independent exact/ownership/clock oracles.
The existing XVII.5 value recurrence now also runs through the endpoint.
Read [`REFERENCE_RUNTIME_CONTINUATION.md`](../../docs/REFERENCE_RUNTIME_CONTINUATION.md)
for the supported deterministic raw-revealed-data interface, stop-gradient
delayed learner, retained event phases, terminal failures and exact limits.

Read [`ORDERED_NATIVE_REFERENCE_CLASS.md`](../../theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md)
for the finite grammar proof and exact decision scope. Fixed-state exact
likelihood ranking does not optimize every future trajectory or parameter
value. Any unresolved member or final verification budget blocks its proof;
external mutations invalidate earlier authority.

Next integrate complete ERC-1 registration, fresh persistence/error state,
full physical accounting and reference/AMP/atomic installation. The unsafe old learner
and query callbacks have been replaced. Historical proof/bridge signers are
quarantined in Git and replayed by `audit_recovered_authorities.py`; current
`proof.py` exposes only typed comparison data and fixed maximum checking,
with issuance owned by Runtime. `bridge.py` remains reserved. Their
importability is not a gate pass. The package issues no complete Compiler,
persistence or install token.
