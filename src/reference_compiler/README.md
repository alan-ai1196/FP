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
fixed update units, revealed-data roles/use and finite-alphabet queries.

This uses the explicit `ConstructionContract` slice, not the complete ERC-1
run manifest. The registered machine counts retained packed reference payload
bytes and conservative reference operation charges; it does not claim total
CPython heap, bit-time, GPU memory or CUDA work accounting. Numeric integer
work limits and inconclusive range bounds produce UNRESOLVED. Intermediate
build failures release partial buffers without refunding spent work or peak.

Run `python -B scripts/audit_reference_construction.py` and
`python -B scripts/audit_reference_events.py` from repository root. They
exercise the actual Runtime and independent exact/ownership/clock oracles.
The existing XVII.5 value recurrence now also runs through the endpoint.
Read [`REFERENCE_RUNTIME_CONTINUATION.md`](../../docs/REFERENCE_RUNTIME_CONTINUATION.md)
for the supported deterministic raw-revealed-data interface, stop-gradient
delayed learner, retained event phases, terminal failures and exact limits.

Next integrate registered profile replay, complete grammar search and typed
proofs, then persistence/bridge/atomic installation. The unsafe old learner
and query callbacks have been replaced. Historical proof/bridge signers are
quarantined in Git and replayed by `audit_recovered_authorities.py`; current
`proof.py`/`bridge.py` expose no authority. Their importability is not a gate
pass. The package issues no complete Compiler, persistence or install token.
