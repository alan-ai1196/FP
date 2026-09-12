# Bounded actual CUDA tensor storage

**Status, 2026-09-13:** scoped storage invariant and actual RTX 3090 audit.
This implements one physical component of ERC-1. It grants no Runtime,
persistence or installation authority and does not change Foundation or the
frozen PRODUCT/SUM/range/precision law.

Sources: [`cuda_storage.py`](../../src/reference_compiler/fp_reference/cuda_storage.py)
and [`cuda_learner.py`](../../src/reference_compiler/fp_reference/cuda_learner.py).
Run `python -B scripts/audit_cuda_storage.py --write`; the retained artifact is
[`FP_CUDA_STORAGE_AUDIT.json`](../../evidence/minimal/FP_CUDA_STORAGE_AUDIT.json).

## Physical invariant and scope

One actual CUDA byte tensor backs all learner states and phase temporaries.
The fixed arena and allocator reservation are charged fully to deployment
and compiler, once globally. Each phase consumes an eight-byte header;
each output reserves at least eight bytes, rounded up to eight-byte alignment.
Offsets advance monotonically, including zero-length outputs and failed
phases. Previously initialized extents remain resident and readable. There
is no address reuse or erasure argument hidden inside a free list.

For arena size B and admitted requests with byte sizes b_i, the constructive
extent bound is `8 * phases + sum(max(8, 8 * ceil(b_i/8))) <= B`.
Induction on requests proves disjoint, aligned, in-buffer output extents.
Before an operand is read, the executor checks actual storage identity,
contiguity, dtype, extent containment and initialization; lazy negative or
conjugate views cannot stand for the recorded raw extent. A new write can
initialize only its complete new extent in its current phase. This is a
trusted mechanical implementation, not protection against arbitrary Python
code mutating raw tensor handles. Runtime must own and hide those handles.

All learner output/cast/copy/integer-mask operations use explicit arena
views and `out=` or `copy_`. The complete continuous numerical schedule in
[`CONTINUOUS_CUDA_LEARNERS.md`](CONTINUOUS_CUDA_LEARNERS.md) is unchanged.
The three native lifetime allocation counters must stay at their binding
values after each operation check and phase closure. No allocator cache is
emptied and no current, accumulated or peak counter is reset by this path.
The execution premise is a serialized default stream, no external allocator
or tensor mutations, and a native allocator with the registered settings.
Initial zero counters reject a visible prior allocation history; they do
not prove that arbitrary earlier caller code never reset that history.

This bounds the actual PyTorch tensor allocator, including its reservation,
not GPU driver/context/non-PyTorch allocations or whole-device residency.
Host tensor metadata, readbacks, traces and control work must also be paid
by the complete Runtime integration. The entire B-byte tensor remains the
physical charge even when only a small prefix contains written outputs.

## Request size is not allocator reservation

For a fresh native allocator in the audited PyTorch 2.12 implementation,
512-byte-multiple request B and explicitly bound 20 MiB large segments, the
first segment size is:

| Request | Allocator reservation |
|---|---|
| B <= 1 MiB | 2 MiB |
| 1 MiB < B < 10 MiB | 20 MiB |
| B >= 10 MiB | `2 MiB * ceil(B / (2 MiB))` |

This is a versioned implementation law from
[`get_allocation_size`](https://github.com/pytorch/pytorch/blob/v2.12.0/c10/cuda/CUDACachingAllocator.cpp),
not a universal CUDA property. The arena checks the predicted segment against
every registered role/global cap **before** allocating its backing tensor,
then checks the actual segment and allocation counters. Unsupported builds,
settings, histories or devices remain unresolved. Independent fresh processes
execute requests of 512 bytes, 2 MiB and 10 MiB and match all three branches.
A 2 MiB request with a 4 MiB reservation cap is refused with zero allocations.

An initial draft trusted the reported empty configuration string. That is
false even before the first tensor allocation: set `large_segment_size_mb:40`,
then set the configuration to the empty string. The complete reported
allocator-settings dictionary equals the initial default snapshot, but an
actual 2 MiB request reserves **40 MiB**, not 20 MiB. The versioned
[`AllocatorConfig.cpp`](https://github.com/pytorch/pytorch/blob/v2.12.0/c10/core/AllocatorConfig.cpp)
explains why: parsing resets some fields, while the large-segment value
persists unless supplied. The last configuration string omits that state.

The corrected constructor executes the explicit registered configuration
`large_segment_size_mb:20` before its first allocation and retains the
resulting settings. A separate fresh-process audit first creates the hidden
40 MiB state, then verifies that this binding actually restores a 20 MiB
reservation. Merely printing an apparently default configuration would not
establish the admission premise.

## A current-byte snapshot loses transient work

After legal arena execution, allocate and free one external binary32 tensor.
Current tensor bytes return to 16,777,216, exactly the previous value. But
the native lifetime counters `(allocations, allocated bytes, segments)` change
from `(1, 16777216, 1)` to `(2, 16777728, 2)`. The extra request occupies the
allocator's 512-byte quantum and obtains another segment in this execution.
The arena refuses the escaped allocation despite equality of current bytes.

Failure is terminal for the arena and retains prior writes, extents and the
failed phase. An unexpected executor exception occurring before this storage
refusal is preserved as the primary error; it cannot become an ordinary
resource-uncertainty outcome because closure also failed. A separate actual
overflow test retains an infinite optimizer intermediate even when later
projection returns finite zero, with the predecessor state unchanged.

## Executed evidence

All **1,306 complete learner phases** from the independent exact rounded
audit run inside one **16 MiB** tensor arena. Both current and lifetime peak
tensor/reserved bytes are 16,777,216, and the three allocation counters remain
`(1, 16777216, 1)`. The 32,996 initialized views consume 304,064 bytes of
that prepaid buffer. This is not a 304 KiB GPU-memory or performance claim.

An independent offset model checks all 216 length-three request sequences
over six typed shapes, giving 648 actual extents. Additional checks cover
uninitialized, cross-extent, reinterpreted and lazy-negative reads, stale
writes, closed workspaces, admission failure without cursor advance, 1,340
exact grid coordinates, masked overflow and a freed escaped allocation.
The actual device/build identity is retained with the small count/witness
artifact. The audit stores no weights, datasets or full tensor tapes.

The subsequent [Runtime-owned AMP prefix](OWNED_CUDA_PREFIX.md) now executes
immutable physical registration, prepaid evidence, continuous private device
learners, per-event relations and joint reference/device publication. Target
range, fresh same-path persistence, build/copy/install and total-device
accounting still need their own closure. Model science remains HOLD.
