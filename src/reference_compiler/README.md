# Foundation-R4 Reference Compiler — scoped CPU and RTX 3090 AMP release

The [owned histogram extension](../../theory/proofs/OWNED_HISTOGRAM_DECODER.md)
executes the same complete native count learner with prepaid integer
enumeration. Its CPU/native gate passes; its actual Runtime CUDA gate is
registered and still open. This extension has no complete-release claim.

**Status: Reference/CPU and RTX 3090 AMP baseline FROZEN, 2026-09-13;
prospective v2 strategy separately audited. Experiments are UNHELD within
their tested scopes.** Source
`5e55eb4` passes all 21 CPU and 10 CUDA audits of that release from one
fresh clone, including 38 submodule imports, independent endpoint models,
trained/recurrent installation, device resources and the n=32 hierarchy.
See [target scope](../../theory/proofs/CUDA_RELEASE_SCOPE.md) and
[integrated evidence](../../evidence/minimal/FP_CUDA_RELEASE_AUDIT.json).
The separate earlier CPU prerequisite remains recorded at `ebe2c4c`.

The current [prospective extension](../../theory/proofs/OWNED_PROSPECTIVE_SELECTION.md)
can install a freshly tested native candidate without claiming that its
unresolved full constructor class is optimized. Historical selection IDs
are optional additional checked assertions; actual paired start/current
trajectories and the complete physical transition remain mandatory. The
proposer compares registered initialized values rather than requiring an
exact unrestricted fitted coefficient. Run `scripts/audit_prospective_selection.py`
from the repository root. This is a scoped extension, not a replacement
claim that the whole historical release was rerun.

[RN-2](../../experiments/prospective_relation/RESULTS.md) executes this strategy
in twenty sealed FP streams and eight new AMP posterior workers. All sixteen
IID cases install while the full training classes remain unresolved; the
disconnected uncertainty control remains. Its 17,064 CUDA/binary64 phase
replays and model scores belong to source `5bcbb49`.

The late 2026-09-05 research workspace contained a larger `fp_reference` package than the eight files that survived as direct final attachments. The missing scratch modules are not evidence that the implementation never existed: execution provenance records a 22-module package and an intermediate 24/24 unit + 47/47 gate pass before later complete-Runtime hardening.

This directory contains the current scoped Reference/CPU and target AMP
implementation; Git retains the directly persisted late-WIP source.
Registered RTX 3090 resource and model experiments are running within this scope.
See root `IMPLEMENTATION_STATUS.md` for the
current release and `RECOVERY_MANIFEST.md` for historical provenance.

Extend the implementation against `FP_THEORY.md`; do not weaken its contract
or import superseded R4.2 semantics. The reference modules are restored and
integrated; actual target execution retains its own complete endpoint evidence.

`fp_reference.cuda_learner` now provides actual continuous mixed-precision
learner mechanics with an independent exact rounded audit. The helpers have
no signer; the owned Runtime installation below supplies the separate transition. See
[CUDA learner scope](../../theory/proofs/CONTINUOUS_CUDA_LEARNERS.md).
Importing the component does not import Torch or initialize CUDA.

`fp_reference.cuda_storage` now supplies a prepaid typed tensor arena for
those same learners. Its actual 16 MiB allocation executes all 1,306 phases
without a further native allocator event; initialization/extent/history
guards and explicit allocator configuration have adversarial coverage.
See [storage scope](../../theory/proofs/BOUNDED_CUDA_TENSOR_STORAGE.md).
Host evidence, Runtime state and driver/context resources are not supplied
by this component alone.

`ReferenceCompilerRuntime(..., cuda=CudaPrefixContract(...))` now owns those
continuous CUDA trajectories and the tensor arena. Read
[owned CUDA prefix](../../theory/proofs/OWNED_CUDA_PREFIX.md) and run
`scripts/audit_cuda_runtime.py`. The immutable manifest, prepaid raw phase
frames, exact relations and joint reference/device publication have actual
endpoint coverage. CPU install and its complete run policy refuse this target
root. [Current CUDA range and fresh persistence](../../theory/proofs/OWNED_CUDA_PERSISTENCE.md)
also execute through this Runtime. Register a `PersistenceRule` with
`score_path=CUDA_PATH` and use `admit_cuda_persistence`,
`cuda_persistence_result`, `cancel_cuda_persistence` and
`paired_cuda_persistence_result`. The root owns full-domain bounds and
checks actual forecasts against the exact mixed rounding schedule; no
caller-supplied range or device state is accepted. Run
`scripts/audit_cuda_persistence.py`.

Register `CudaPrefixContract(install=CudaInstallContract(...))` from
`fp_reference.cuda_installation` to enable `install_cuda(candidate_id,
proposal_proof_id=..., reference_identity=..., cuda_identity=...)`. Runtime
checks owned historical selection, both fresh crossings, actual initialized
device extents and full states before one combined root/lease publication.
The CUDA learner objects retain identity; old searches and evidence stop
with history and alpha preserved. Read
[owned CUDA installation](../../theory/proofs/OWNED_CUDA_INSTALLATION.md) and
run `scripts/audit_cuda_installation.py`. The complete target release above
combines this component with its owned policy/run and resource bindings.
Read [device-resource observation scope](../../theory/proofs/CUDA_RESOURCE_OBSERVABILITY.md)
before promoting native arena counters to a complete device claim. The
actual foreign-allocation audit also distinguishes Torch's CUDA build tag
from the Windows runtime version returned by the native API.

`CudaPrefixContract.device` now requires an immutable `CudaDeviceContract`
from `fp_reference.cuda_device`. Its default binds actual runtime/API 13040,
display driver 616.92 and a 24 GiB physical framebuffer cap for each role
and globally. Runtime reads the actual ordinal/PCI/UUID/capacity and refuses
a mismatch before tensor allocation. `snapshot().cuda.device` reports the
whole-board residency upper separately from native arena and host commitment.
Read [the scoped resource proof](../../theory/proofs/WHOLE_BOARD_CUDA_RESOURCES.md)
and run `scripts/audit_cuda_device.py`; the actual 4 GiB host-job audit also
executes the CUDA install and continuation. This does not issue a complete target release.

The [owned CUDA policy/run](../../theory/proofs/OWNED_CUDA_POLICY_RUN.md) now
uses the same Runtime strategy with explicit target identities:

```python
from fp_reference import CudaCompilerPolicy, CudaCompilationStep
policy = CudaCompilerPolicy((CudaCompilationStep(2, 'native', 10000, 'ref', 'cuda'),))
runtime = ReferenceCompilerRuntime(contract, initial_program, online=online,
    host=host, cuda=cuda, policy=policy)
```

The immutable `cuda` declaration must enable resident installation; `host`
must bind a worker fenced before execution. The registered future comparison
must fit the stream horizon. Empty target steps give the ordinary CUDA
baseline. At the horizon Runtime verifies the full device frame and publishes
`SEALED_CUDA_STREAM`, retaining partial units and unresolved stages. The
report is `snapshot().run` together with the entire snapshot; it supplies no
future authority or current CUDA-class optimum. Run
`scripts/audit_cuda_policy_run.py`.

The [existing hierarchical fixture](../../theory/proofs/OWNED_CUDA_HIERARCHY.md)
now executes under this target policy: n=32 installs at 330 and seals at 622,
with 1,963 independently replayed CUDA and binary64 phases. Its actual
SUM-only training tie and disconnected/misleading-relation controls pass;
neither empirical optimality nor fresh installation identifies an unseen
table or forces the selected structure. Run `scripts/audit_cuda_hierarchy.py`.
The full fresh-clone integration passes at `5e55eb4`; run
`scripts/audit_cuda_release.py --write` to reproduce it on committed source.

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

The construction-only/manual interface remains an explicit partial mode;
the owned online policy binds the aggregate reference manifest described
below. The registered machine counts retained packed reference payload
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
and run `scripts/audit_context_ingress.py`. Packed ingress alone does not
cover host metadata or temporary workspace; v6 adds the host binding below.

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
non-ASCII encodings change. Mutable buffers are private bytearrays, with public
snapshot byte copies and the same object-preserving CPU install contract.
Completed CUDA evidence frames now become immutable after their final write;
snapshots share their complete bytes. The copy coexistence and publication
are paid and audited in [the frame-preservation proof](../../theory/proofs/IMMUTABLE_CUDA_EVIDENCE_FRAMES.md).
Read [`OWNED_ENCODING.md`](../../theory/proofs/OWNED_ENCODING.md) and run
`scripts/audit_owned_encoding.py` for the actual historical alias failure,
code-point/size checks and old/new workspace measurements. They do not close
full host allocation or authorize a complete Runtime release.

The failure rule introduced in machine v5 also closes every public
continuation/authority port after host MemoryError. It uses a precreated
marker in existing state slots, bypassing allocating cleanup/logging; spent
work, alpha and the failed prefix remain. Snapshot reads are diagnostic and
may themselves fail. This corrects an actual injected-fault execution in
which old cleanup freed a candidate's learner buffers yet left it in the
next prediction. Read [`HOST_ALLOCATION_FAILURE.md`](../../theory/proofs/HOST_ALLOCATION_FAILURE.md)
and run `scripts/audit_host_allocation_failure.py`. Its real Windows job
refusal test measures child commitment, not total host memory or complete
ERC-1 registration. Ordinary checked payload/work refusal keeps its semantics.

The host binding introduced in machine v6 accepts an optional immutable
host policy in the actual Runtime constructor, for example:

```python
from fp_reference import HostResourceContract, ReferenceCompilerRuntime

host = HostResourceContract(128 << 20, {
    'deployment': 96 << 20, 'compiler': 64 << 20,
})
runtime = ReferenceCompilerRuntime(contract, initial_program, online=online, host=host)
```

This requires the executing 64-bit Windows CPython process to be in the
matching fixed 64 MiB job before execution. Runtime creates its own native
binding; supplied samples/handles cannot do so. Both roles share and pay the
whole private process arena, once globally. Whole-process peak/CPU history
survives late registration, failure and CPU installation. Native premise
failure closes authority; diagnostics cannot rewrite its first host marker.
`snapshot().host_resources` observes live counters, not complete physical
state. Omitting `host` is explicitly partial and changes chi.

Read [`BOUND_HOST_RUNTIME.md`](../../theory/proofs/BOUND_HOST_RUNTIME.md)
and run `scripts/audit_bound_host_runtime.py`. Its actual bounded CPU chain
and late-fence counterexample establish the declared commitment scope.
The subsequent owned policy/run protocol below closes its declared CPU
registration and publication scope. Shared platform/device resources,
additional resource limits and actual target AMP are outside this host result.

Machine v7 introduced the owned registered Compiler strategy, retained in
current v9. For an online registration containing the named native
class and two CPU evidence rules:

```python
from fp_reference import CompilationStep, CompilerPolicy

policy = CompilerPolicy((CompilationStep(
    after_cursor=2, search_name='native', search_transitions=10000,
    reference_rule='ref', float64_rule='finite',
),))
runtime = ReferenceCompilerRuntime(
    contract, initial_program, online=online, host=host, policy=policy,
)
```

Only context/target transport and passive snapshots remain external ports
in this mode. The Runtime's post-commit strategy runs the full registered
native class, admits separate fresh evidence, and attempts CPU installation
at the common optimizer boundary. The completed policy record and learner
publish together. `snapshot().compiler_policy` exposes the owned progress;
ordinary observation success is separate from the Compiler's result/halt
state. Search or evidence uncertainty stays UNRESOLVED without alpha refunds.
`CompilerPolicy(())` is the closed ordinary baseline. Omitting `policy`
retains the explicitly manual reference mode, with a different chi.

Read [`OWNED_COMPILER_POLICY.md`](../../theory/proofs/OWNED_COMPILER_POLICY.md)
and run `scripts/audit_owned_compiler_policy.py`. Two successive native-class
installs and all short-stream outcomes traverse the actual endpoint, including
the registered host path. No arbitrary adaptive-strategy optimum, multi-root
family error bound, target AMP or full Runtime release is inferred.

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

Machine v8 now owns an aggregate reference run manifest and terminal report.
The actual initial Program and all fixed contracts/arithmetic are bound and
stored with paid bytes/work. At the registered ordinary horizon, Runtime
seals its continuation ports and reports historical decision classes,
unresolved stages and finite-prefix range/precision diagnostics. The complete
report is `snapshot().run` together with the existing full snapshot, including
resource and host records. A report failure cannot undo an already published
event/install or become a successful run. See
[`OWNED_REFERENCE_RUN.md`](../../theory/proofs/OWNED_REFERENCE_RUN.md) and run
`python -B scripts/audit_reference_run.py`.

Machine v9 adds a checked all-categorical empirical upper and a native
relation proposal from ordinary labels. An owned feasible endpoint attaining
the upper closes the full grammar's empirical optimum through a distinct
`BoundedReferenceProof`, without asserting executed enumeration. Same-theta
ordinary successors retain their actual whole-domain range object; changed
theta recomputes/replaces it, preserving all learner/history coordinates.
The n=32 bounded CPU audit installs at 330 and seals at 622, with 1,963
independent binary64 phase checks. Read
[`SATURATED_REFERENCE_CLASS_BOUND.md`](../../theory/proofs/SATURATED_REFERENCE_CLASS_BOUND.md)
and run `python -B scripts/audit_reference_acceleration.py`.

The [47-gate mapping](../../docs/REFERENCE_RELEASE_GATE_MAP.md) distinguishes
current reference evidence, scoped theorems, absent bypass authority and
target AMP obligations. Gate 17 has current owned evidence; the full
reference integration passed at `ebe2c4c`. Actual target AMP is next.
The unsafe old learner
and query callbacks have been replaced. Historical proof/bridge signers are
quarantined in Git and replayed by `audit_recovered_authorities.py`; current
`proof.py` exposes only typed comparison data and fixed maximum checking,
with issuance owned by Runtime. `bridge.py` remains reserved. Their
importability is not a gate pass. Current owned CPU persistence results and
installation receipts have only their stated scope; the generic target
install port stays UNRESOLVED and no CERTIFIED_COMPLETE is issued.
