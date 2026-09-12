# Owned actual CUDA learner prefixes

**Status, 2026-09-13:** implemented in `ReferenceCompilerRuntime`, with an
independent exact rounded model and actual RTX 3090 execution. This is a
checked finite prefix, not the complete target AMP release. Foundation,
XVII.31 and ERC-1 are unchanged; model science remains HOLD.

Source: [`runtime.py`](../../src/reference_compiler/fp_reference/runtime.py),
[`cuda_prefix.py`](../../src/reference_compiler/fp_reference/cuda_prefix.py),
[`cuda_learner.py`](../../src/reference_compiler/fp_reference/cuda_learner.py).
Run `python -B scripts/audit_cuda_runtime.py --write`. Retain only the small
[`FP_CUDA_RUNTIME_AUDIT.json`](../../evidence/minimal/FP_CUDA_RUNTIME_AUDIT.json).

## Registration, state and exact claim

The constructor accepts an immutable `CudaPrefixContract` through its `cuda`
keyword. It binds the explicit numerical backend, expected actual Torch
version/build, CUDA runtime, device name/SM, storage contract, tolerances,
per-phase output allowance and evidence-frame capacity. The owned manifest
includes this declaration before initial construction. The actual execution
identity is checked before the backing tensor is allocated. Callers cannot
provide a running device state, prediction, callback, relation or certificate.

The existing native initialization, profile, prediction, observation and
commit paths all pass a common private numerical hook. The optional CPU
binary64 learner and the CUDA learner execute independently. CUDA reads the
registered initializer only at birth and thereafter retains its own master
parameters, half delayed queues, gradient accumulator and clocks. Profile
attachment changes the clock at a whole-unit boundary while preserving every
numeric buffer. It does not recast a trained reference or CPU endpoint.

Each retained `CHECKED_CUDA_PREFIX_PHASE` asserts only the following:

1. This root executed the registered phase from its own predecessor and,
   for observation, its own sealed pre-target device prediction.
2. Complete raw predecessor bits did not change. The actual output has the
   registered shape, finite intermediates and exact output-allocation count.
3. The observed exact/reference relation satisfies the manifest tolerances
   and the checked current-context caps. The record is physically retained
   in its already paid frame under the root's information owner.

The state relation compares master parameters, every delayed queue entry,
gradient accumulators and exact equality of unit/cursor/optimizer clocks.
Prediction checks compare native values, excesses, masses, delayed successors,
rounded normalizer, the exact sum of stored masses, exact normalized
stored-mass probabilities and raw rounded division outputs separately. Native
and normalizer errors use `state_atol`; probability and division errors use
`probability_atol`. All reference comparisons use guarded exact arithmetic.

The existing rational comparison implementation is reused through an exact
binary16/32-to-binary64 **encoding injection**. Integer bit manipulation
preserves every finite value and both zero signs. This creates passive values
for comparison, not a CPU-executed trajectory or persistence identity. Original
half/single words remain in the CUDA record. All 63,488 finite half encodings
and twelve signed single boundary encodings independently verify the decoder.

This is not an all-input floating-kernel theorem or a guarantee of a future
relation. Every next phase must check again. Unsupported execution, exhausted
resources or failed numerical bounds remain unresolved. A checked phase
alone gives no whole-domain target range or installation authorization.

## Physical output schedule and prepaid evidence

Let `m=max(1, slots)`, V be the node count, K the label count, E the number
of SUM edges, P the PRODUCT count, S the SUM count, D the total delay length
and A the number of external sources. For this fixed lowering, the exact
number of output coordinates, counting an empty output as one, is:

| Phase | Output coordinates |
|---|---|
| initialize | `2m + 2 + D` |
| predict | `m + 2 max(1,A) + 1 + P + 3E + S + V + 6K + D` |
| observe | `6 + K + V + 3m + 4(E+P)` |
| commit without/with a grid | `4 + 7m` / `4 + 14m` |
| whole-unit clock attachment | 0 |

These identities follow by adding the actual output, cast, copy, projection
mask and grid-work extents in the registered executor. They are not lower
bounds over other legal physical implementations. Each allocation consumes
the prepaid output allowance before execution; the completed phase must also
match the derived exact count. Returning a numerically correct baseline clock
successor without performing its registered operations is rejected.

Runtime prepays the fixed conservative work debit
`128 * output_allowance + 2 * relation_work + evidence_capacity` before a phase.
This is the existing machine's abstract work model, including the declared
output/readback/relation/encoding work, not elapsed GPU time, total host heap
or a physical FLOP lower certificate. Actual tensor storage is separately
bound by the [prepaid arena](BOUNDED_CUDA_TENSOR_STORAGE.md). No old device
extent is freed or recycled after candidate retirement or failed work.

The evidence frame's full capacity is allocated in the CPU resource ledger
before any CUDA phase starts. Its first eight bytes give the used typed
encoding length; the remaining bytes still count toward residency. Successful
records retain full raw state/prediction/operation data and predecessor IDs.
The audit independently compares each frame's actual bytes with its record.
The default frame capacity is 128 KiB; observed used lengths in these small
cases are below 6.1 KiB. This conservative realization does not claim optimal
evidence storage. Host process enforcement and total-device resources retain
their separate scopes.

If a record does not fit, it cannot remain CHECKED. The retained frame still
describes admission, the diagnostic is unresolved, all actual device extents
remain present and no successor is published. A prior unexpected executor
error remains primary when evidence retention also fails. An escaped host
allocation failure reaches the existing terminal host boundary.

## Joint publication and authority boundary

The private CUDA owner retains phase outputs separately from its published
candidate-to-state map. Ordinary predictions do not advance that map. After
target revelation, observe/commit results remain staged until **all** exact,
optional CPU and CUDA learner phases, evidence writes, reference feasibility
checks and coexistence allocations succeed. Runtime then publishes the
prepared reference and CUDA maps in the same serialized event transition.

If the second learner fails after the first completed its CUDA phase, both
published learners remain at the predecessor cursor. Completed staged device
work, the failed phase, the revealed target and spent resources remain.
No exact-only or baseline-only successor is returned as a successful event.
Native allocation history is also checked at public continuation boundaries;
a freed external CUDA temporary cannot disappear through current-byte equality.

The complete root frame includes the private CUDA owner. Public snapshots
contain immutable raw records and ownership/extent descriptions, never tensor
handles. Retiring a candidate removes its live binding but preserves its
phase records and physical arena. Internal helpers have no signer.

The existing `install_cpu` explicitly refuses a CUDA-bearing root, and the
CPU owned-policy/run-closure protocol cannot register that root. The generic
target install port still returns UNRESOLVED. Reference search remains a
reference decision class; its optimum or CPU wealth cannot become AMP evidence.

## Executed audit and open target work

All 64 binary three-event context/target streams execute the public Runtime
endpoint with a deployed baseline and native shared candidate. Their 1,024
CUDA phases match an independent exact rounded interpreter using only owned
snapshots. Partial final optimizer units remain partial. A recurrent profile
case checks another 44 CUDA phases and 44 independent CPU phases, including
both clock attachments, both positions of the delay queue, six replayed and
six ordinary events, and five candidate optimizer steps.

A 35-member complete native constructor class also executes its CUDA births,
retirement and reference comparison, contributing 41 phases. Its exact
decision class is fixed-state reference empirical CE over the registered
initializer endpoints plus actual baseline. An actual one-million-byte
packed cap prevents some device-evidence admissions: native search remains
UNRESOLVED and issues no class proof. Exhausted construction is not exclusion.

Further controls cover a real 46-coordinate phase cap, refusal of a phase
frame before any GPU work, an actually insufficient 4,800-byte evidence frame,
unexpected executor failure, a correct-looking unexecuted endpoint, a freed
escaped allocation, zero-tolerance birth rejection without endpoint fallback
and actual rounded-normalizer/readout rejection before target revelation.
Combined executor/evidence failure preserves the original exception. A
malformed backend result whose raw extraction also fails remains an execution
failure, not an admissibility rejection of already validated native input.
Injected failures are identified as injections, not naturally occurring OOMs.

The active remaining work is whole-domain target range for current CUDA
states, separate fresh same-path AMP persistence, actual build/copy/install
relations and full device resource closure. This prefix implementation issues
neither `CERTIFIED_COMPLETE` nor a model-science release. Do not restart the
static PRODUCT/SUM/range/precision study or reconstruct the existing learners.
