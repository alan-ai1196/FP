# Foundation-R4 Reference Compiler — recovery/WIP

**Status: NOT FROZEN.**

The late 2026-09-05 research workspace contained a larger `fp_reference` package than the eight files that survived as direct final attachments. The missing scratch modules are not evidence that the implementation never existed: execution provenance records a 22-module package and an intermediate 24/24 unit + 47/47 gate pass before later complete-Runtime hardening.

This directory preserves the directly persisted late-WIP source exactly enough to continue the recovery. It is not currently guaranteed import-complete by itself. See root `IMPLEMENTATION_STATUS.md` and `RECOVERY_MANIFEST.md` before editing.

Do not “fix” imports by weakening the contract or copying old R4.2 semantics into the new Runtime. Recover/implement the missing modules against `FP_THEORY.md`, then run the complete endpoint gates.

## Current executable recovery (2026-09-12)

`fp_reference.ReferenceCompilerRuntime` now owns the native **construction**
segment: typed skeleton admission, complete parameter slots, fixed registered
initialization, delayed-state reset, conservative/full-finite-domain range
checking, actual packed reference buffers, owners/refcounts and immutable
resource-role charges. Its snapshots retain current constructed states,
program/buffer registries, resource history and failed attempts.

This uses the explicit `ConstructionContract` slice, not the complete ERC-1
run manifest. The registered machine counts retained packed reference payload
bytes and conservative reference operation charges; it does not claim total
CPython heap, bit-time, GPU memory or CUDA work accounting. Numeric integer
work limits and inconclusive range bounds produce UNRESOLVED. Intermediate
build failures release partial buffers without refunding spent work or peak.

Run `python -B scripts/audit_reference_construction.py` from repository root.
It exercises the actual Runtime endpoint and independent exact/ownership
oracles. It is not an install, AMP, learning or 47-gate completion test.
The package currently issues no complete Compiler or install authorization.
Positive delayed-body evaluation is checked, but source availability,
score-time target visibility and the ordinary learner clock still require
the pending Runtime event/information integration.

Next integrate registered information/data-use and learner/value continuation,
then complete grammar search, proof/persistence/bridge/atomic installation.
The preserved `info.py`, `proof.py`, `bridge.py` and learner callbacks are
still WIP and are not consumed as authorities by this new endpoint. In
particular, `info.py` still depends on the missing data-use integration.
