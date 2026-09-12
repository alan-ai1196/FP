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

`float64_range.py` now supplies current whole-domain rounded forward and
delayed-invariant bounds for CPU persistence. Declare a separate
`PersistenceRule(..., score_path='binary64-stored-mass')`; Runtime admits it
through `admit_float64_persistence` with a separate global alpha debit.
`paired_persistence_result(reference_id, float64_id)` requires both owned
current crossings on matching four-learner starts and schedules. It never
copies reference wealth or uses rounded division output as a normalized
probability. Read [`PAIRED_CPU_PERSISTENCE.md`](../../theory/proofs/PAIRED_CPU_PERSISTENCE.md)
and run `scripts/audit_paired_cpu_persistence.py` for this CPU protocol scope.

`OnlineContract.cpu_install=CpuInstallContract(...)` additionally registers
the fixed CPU installation policy. `install_cpu` checks owned historical
selection and current paired evidence separately, prepares actual metadata
and leases, then publishes one complete serialized CPython root. All raw
learner buffers retain identity; the old deployment becomes a shadow.
Searches close with history retained and old persistence loses authority
without alpha refunds. Failure keeps old learner/evidence records while
retaining real attempt/work/peak history; retries use new physical IDs.
Read [`OWNED_CPU_INSTALLATION.md`](../../theory/proofs/OWNED_CPU_INSTALLATION.md)
and run `scripts/audit_cpu_installation.py`. This operation is distinct
from a current class optimum, target AMP and concurrent/crash-safe install.

This uses the explicit `ConstructionContract` slice, not the complete ERC-1
run manifest. The registered machine counts retained packed reference payload
bytes and conservative reference operation charges; it does not claim total
CPython heap, bit-time, GPU memory or CUDA work accounting. Numeric integer
work limits and inconclusive range bounds produce UNRESOLVED. Intermediate
build failures release partial buffers without refunding spent work or peak.

The control rule introduced in machine v2 additionally requires a positive
control admission debit before any public Compiler state change. An
unfunded request cannot mint IDs or invalidate a current proof revision;
an admitted failure still retains its full recorded costs/history. Read
[`OWNED_CONTROL_ADMISSION.md`](../../theory/proofs/OWNED_CONTROL_ADMISSION.md)
and run `scripts/audit_control_admission.py`. It also replays the historical
raw-ingress failure from `5055f3e`.

The ingress rule introduced in machine v3 requires bounded exact byte
ingress. `DataContract.ingress=IngressContract(capacity=4096, chunk_bytes=64)`
registers a window before execution. `begin_context(observation_id)` prepays
work, body, fixed terminal status and identity, and seals learner/persistence
IDs before offering bytes. Call `receive_context(ingress_id, offset, chunk)`
with only the offered extent, then `finish_context(ingress_id)`. The latter
guards integer lengths before materialization and executes ordinary prediction.
`predict_next(observation_id, encoded)` accepts only one bounded byte chunk
through the same protocol. `ingress.encode_context` is a producer utility;
raw rational tuples are no longer an alternate Runtime input port.

Failed prefixes retain their actual bytes and fixed status in paid storage.
The grammar covers all nonnegative rationals; a window or integer limit can
leave execution UNRESOLVED. Read
[`OWNED_CONTEXT_INGRESS.md`](../../theory/proofs/OWNED_CONTEXT_INGRESS.md)
and run `scripts/audit_context_ingress.py`. Complete host metadata, temporary
copies/arithmetic scratch and general diagnostic accounting remain open.

The encoding introduced in machine v4 additionally preserves every
Python source-name code point in its typed UTF-8/surrogatepass encoding.
The old ASCII-escaped JSON could give different legal source programs the
same ID and let candidate construction change the deployed program without
installation. An owned address now also requires complete Program equality;
collisions return UNRESOLVED before code can be replaced.

`machine.realize` now creates a `PlannedObject` with exact extent and value,
not a buffer or lease. Runtime checks the complete allocation batch before
writing directly to the owned buffer. Identity hashes stream the same typed
coordinates without a duplicate tagged tree. ASCII bytes stay compatible;
non-ASCII encodings change. All buffers are private bytearrays, with public
snapshot byte copies and the same object-preserving CPU install contract.
Read [`OWNED_ENCODING.md`](../../theory/proofs/OWNED_ENCODING.md) and run
`scripts/audit_owned_encoding.py` for the actual historical alias failure,
code-point/size checks and old/new workspace measurements. They do not close
full host allocation or authorize a complete Runtime release.

Current machine `packed-reference-payload-v5` also closes every public
continuation/authority port after host MemoryError. It uses a precreated
marker in existing state slots, bypassing allocating cleanup/logging; spent
work, alpha and the failed prefix remain. Snapshot reads are diagnostic and
may themselves fail. This corrects an actual injected-fault execution in
which old cleanup freed a candidate's learner buffers yet left it in the
next prediction. Read [`HOST_ALLOCATION_FAILURE.md`](../../theory/proofs/HOST_ALLOCATION_FAILURE.md)
and run `scripts/audit_host_allocation_failure.py`. Its real Windows job
refusal test measures child commitment, not total host memory or complete
ERC-1 registration. Ordinary checked payload/work refusal keeps its semantics.

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
for the supported exact revealed-data interface, stop-gradient
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

Next integrate complete ERC-1 registration/accounting and the explicit
release-gate mapping, then actual paired AMP execution and installation.
The unsafe old learner
and query callbacks have been replaced. Historical proof/bridge signers are
quarantined in Git and replayed by `audit_recovered_authorities.py`; current
`proof.py` exposes only typed comparison data and fixed maximum checking,
with issuance owned by Runtime. `bridge.py` remains reserved. Their
importability is not a gate pass. Current owned CPU persistence results and
installation receipts have only their stated scope; the generic target
install port stays UNRESOLVED and no CERTIFIED_COMPLETE is issued.
