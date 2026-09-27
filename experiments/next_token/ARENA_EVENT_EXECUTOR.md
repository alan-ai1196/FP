# Token events and floating continuation state in the fixed CUDA arena

This is the array lowering of the incremental token learner, not a new FP
architecture or a return to static relation tasks. The numerical event
schedule and binary-carry forests from
[the streaming derivation](STREAMING_AMP_GRADIENTS.md) now have an executor
whose device results occupy explicit extents of the existing CUDA arena.
The next boundary is binding this executor and its complete state relation
inside ReferenceCompilerRuntime. A component upload is not an authorized
Gamma, and no bridge, persistence lineage or install authority is issued.

## 1. Closed numerical schedule and resource meaning

`fp_reference/token_array_events.py` executes one stored-half forward pass,
one single-precision reverse pass and the v2 binary-carry append. The new
lowering is named `token-half-single-one-event-explicit-arena-arrays-v1`;
it implements the already separate v2 physical learner, not the original
lag-major batched learner. `token_amp.py` and `token_streaming.py` are now
canonical package implementations; their old experiment paths are aliases.

The only CUDA array backend is `CudaArrays` in `token_arrays.py`. Every
output requests a fresh declared extent, is fully written and is marked
initialized once. Contiguous reshapes retain the same initialized extent.
Integer row indices are explicit admitted arrays. Indexed reads use an
explicit output, and row replacement copies the predecessor before writing
distinct destinations; duplicate destinations refuse before allocation.
Old masters, event leaves and every historical carry block remain readable.

An output-cell allowance and per-array element allowance precede each
allocation. They are separate from arena bytes and the whole-process host
limit. CPU metadata, constants, readback copies and Python objects are not
charged as GPU tensors; the externally bound Windows job still covers the
complete worker. The CPU interpreter is a diagnostic, with no resource or
Runtime authority. There is no fallback to it on device failure.

Readout masters are uint32-valued int64 arrays. For V <= 2^20, all complete
column sums are below 2^52, so explicit pairwise int64 additions are exact.
An arbitrary CUDA library reduction with `out=` is not assumed to avoid
private scratch storage. Integer masters, shifts, gather/scatter and column
totals now have their own admitted extents. Grid commits use exact integer
`max(0, q - ceil(RNE32(scale*g)))`; float32 subtraction from q is never used.

Named initialized views can be copied into a bounded borrowed CPU bytearray.
No gaps are decoded, old phases remain readable, the borrowed prefix is
cleared after each read, and the returned immutable bytes confer no storage
or continuation authority. The arena still requires fresh native allocator
history, one backing allocation, unchanged lifetime allocation counters,
the serialized default stream and no address reuse or allocator reset.

The kernel is a numerical component. Its prepared caches and forecasts must
be kept private and bound by the enclosing owner; typed caller-made caches
are not authenticated just because their shapes match. The actual Runtime
registration still refuses token CUDA execution. Its integration must bind
the actual source/target and predecessor, register the complete leaf/carry
invariant, compare native state/readout coordinates and retain failed work.
The functional all-label decoder is determined by the stored complete W,
base and feature values; this audit does not execute or certify a complete
rounded probability vector, nor borrow an old static readout certificate.

## 2. CPU evidence before a device attempt

`scripts/audit_token_array_events.py --write` passes 144 histories across
unit lengths 1, 2 and 4 and three initializers. All 576 observations and 336
commits match the independent passive v2 implementation, including complete
leaf/carry states, source clocks and old states after later writes. It checks
83,322 complete-state words, 165,444 exact primitive words (15,936 half) and
nine refusal/integer-update controls. These include wrong preparation/source,
bad target/normalizer shape, overlapping row writes, preallocation quota
refusal and uint32 exhaustion. This is finite numerical verification.

The CPU preflight uses the existing full V=50,257, context=512, width=4,
eight-feature, update-unit=512 resource fixture and the same 1,024 bytes of
training prefix. It does not select a language model or read validation/test.
The new event/carry schedule completes one update independently of reference
endpoints and consumes 402,094,088 padded bytes, 408,471 arrays and 1,027
phases. The largest array is 3,216,448 bytes and largest phase is 1,743,251
output cells. Small controls use 166,424 bytes in 79 phases. Preflight is a
shape/numerical calculation, not a measured host/device bound or speed claim.

The array/launch count is a real limitation. An append-only arena cannot
train an unbounded corpus by retaining every temporary forever. Any later
storage reclamation must prove which information all relevant legal future
operations can still read. No allocator recycling or discard is introduced
under the name of this lowering, and no efficiency claim follows merely
from avoiding repeated event derivatives.

## 3. Fixed actual-device preregistration

The sole new launcher is `scripts/run_token_array_audit.py --run`; it requires
a clean source commit and exclusively creates
`evidence/minimal/FP_TOKEN_ARRAY_CUDA_A1.json`. All older token/relation jobs
remain terminal and are not rerun. This audit has two fresh workers:

1. `small`: the five CPU-preflight trajectories, including zero faces,
   multiple unit commits and reversed/repeated original profile contexts;
   28 events and nine commits. Check every actual array word against the
   explicit CPU schedule, exact primitives on that schedule, and complete
   states against the independent passive v2 learner.
2. `train-context512`: exactly the full 512-event preflight above, one commit
   over all 603,092 masters. Check every actual array output word against
   the CPU schedule, complete retained leaves/forests against independent
   v2, and old pending state after commit. No native endpoint supplies an
   AMP successor and no loss, validation, held-out or model score is computed.

Each child starts suspended, enters its non-breakaway one-process Windows
job before resume, and has a 4-GiB host commit limit and 900-second deadline.
Each binds a fresh 1-GiB tensor arena and 1-GiB allocator-reservation cap to
both roles; the entire 24-GiB RTX3090 board remains charged to both roles.
The per-phase cell cap is 2^26, per-array element cap 2^24 and borrowed
readout buffer 4 MiB. Limits are fixed before device outcomes. The exact
Torch2.12.0+cu132 build, CUDA13.2 runtime, SM8.6 RTX3090 and current registered
CUDA/NVML device contract must match. No peaks/counters/cache are reset and
no allocator fraction is changed. An allocation outside the single backing
buffer is a failure of this lowering, even if final residency looks small.

Both workers include real refusal checks for closed workspaces, foreign CPU
inputs, old writes, uninitialized reads, undersized readback, duplicate row
writes and cell exhaustion. Empty integer views and clearing of borrowed
readback are checked. Minimal evidence retains counters, counts, bounds,
identity, terminal outcome and timings; no tensors, corpus or giant trace.
Any failed/terminated attempt is retained, stops the suite and is not silently
retried with changed caps. Wall time includes CPU replay/readback and is not
a training throughput benchmark.

The stopping point for this component is this one finite device audit and
its actual failure diagnosis if needed. Then integrate the Runtime owner;
do not expand a catalog of static variants. Ordinary next-token learning
and fresh strong language-model baselines remain the objective.
