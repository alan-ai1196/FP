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
`admit_reference_persistence` registers a future continuous candidate/base
comparison before context ingress. Runtime scores sealed paired forecasts,
owns guarded lower log/wealth arithmetic and spends global alpha once per
identity. Its `REFERENCE_CROSSED` result is conditional reference evidence;
failure, retirement and reconstruction cannot recycle its authority.

An optional immutable `OnlineContract.float64=Float64Contract(...)` now
executes a separate CPU binary64 learner from initialization through all
profile/ordinary phases. `binary_arithmetic.py` checks actual scalar outputs
against exact rounding; `float64_learner.py` fixes the ordered algorithm;
`float64_bridge.py` checks the complete paired state and all three readout
representations. Raw floating bits and phase evidence have actual packed
residency. No current method accepts a caller's numeric endpoint or bridge
token. Read [`OWNED_FLOAT64_PREFIX.md`](../../theory/proofs/OWNED_FLOAT64_PREFIX.md)
for its finite executed-prefix scope and remaining full-domain/device limits.

This uses the explicit `ConstructionContract` slice, not the complete ERC-1
run manifest. The registered machine counts retained packed reference payload
bytes and conservative reference operation charges; it does not claim total
CPython heap, bit-time, GPU memory or CUDA work accounting. Numeric integer
work limits and inconclusive range bounds produce UNRESOLVED. Intermediate
build failures release partial buffers without refunding spent work or peak.

Run `python -B scripts/audit_reference_construction.py` and
`python -B scripts/audit_reference_events.py` and
`python -B scripts/audit_reference_profiles.py` and
`python -B scripts/audit_reference_search.py` and
`python -B scripts/audit_reference_persistence.py` from repository root. They
exercise the actual Runtime and independent exact/ownership/clock oracles.
The numerical route additionally uses `scripts/audit_binary_arithmetic.py`
and `scripts/audit_float64_runtime.py`, with no GPU execution.
The existing XVII.5 value recurrence now also runs through the endpoint.
Read [`REFERENCE_RUNTIME_CONTINUATION.md`](../../docs/REFERENCE_RUNTIME_CONTINUATION.md)
for the supported deterministic raw-revealed-data interface, stop-gradient
delayed learner, retained event phases, terminal failures and exact limits.

Read [`ORDERED_NATIVE_REFERENCE_CLASS.md`](../../theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md)
for the finite grammar proof and exact decision scope. Fixed-state exact
likelihood ranking does not optimize every future trajectory or parameter
value. Any unresolved member or final verification budget blocks its proof;
external mutations invalidate earlier authority.

Read [`OWNED_REFERENCE_PERSISTENCE.md`](../../theory/proofs/OWNED_REFERENCE_PERSISTENCE.md)
for the conditional null, native ratio bound, bounded lower wealth,
nonrefundable alpha and explicit external stochastic-process assumption.
The pure numerical/kernel audits do not own observation or lineage facts.

Next integrate complete ERC-1 registration, paired AMP persistence/error state,
full physical accounting and reference/AMP/atomic installation. The unsafe old learner
and query callbacks have been replaced. Historical proof/bridge signers are
quarantined in Git and replayed by `audit_recovered_authorities.py`; current
`proof.py` exposes only typed comparison data and fixed maximum checking,
with issuance owned by Runtime. `bridge.py` remains reserved. Their
importability is not a gate pass. The package issues no complete Compiler,
persistence or install token.
