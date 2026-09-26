# Ordinary-token mixed precision and the grid boundary

Status: **CPU AND BOTH ORIGINAL GPU JOBS COMPLETE AT17c9204, 2026-09-26**.
The [actual results and reporting correction](AMP_RESULTS.md) preserve the
preregistration below and the original terminal journal. Do not rerun it.
Source: [amp_tokens.py](amp_tokens.py). The
[audit](../../scripts/audit_token_amp_schedule.py) checks this schedule's
actual primitives and reports its complete discrepancy from native learning.
It issues no Runtime, bridge, data-role, lineage or installation authority.

## The physical schedule

Keep every grid master as an exact integer in an int64 tensor, with the
same uint32 value envelope as the packed reference. Initialize from the
declared birth only; actual device successors use their own retained
masters, source records and gradients. No reference gradient or endpoint
enters their computation.

Convert integer masters to single, scale by2^-p, then cast core operands
and embedding outputs to half. Core SUM edge products and PRODUCT nodes
round to half; explicit balanced SUM accumulation is single, followed by
half node storage. The readout uses single coefficients/features, a rounded
exact integer column total, and single balanced operations. Base constants
and their exact sum have separate registered RNE32 ingress. Backward uses
stored half core values/coefficient operands widened to single and explicit
single operations, including the usual straight-through cast derivative.
Grouped reductions preserve every incidence and parameter tie. There is
no autograd, fused contraction, hidden loss scaling or BLAS reduction.

Each actual floating primitive is checked for finiteness before later
projection can conceal it. This synchronous audit executor is not a GPU
throughput implementation. General resource ownership and immutable phase
evidence must still be integrated into ReferenceCompilerRuntime.

For signed scaled gradient a and integer master q, prove

    max(0, floor(q-a)) = max(0, q-ceil(a)).

The inequality defining ceil(a) is equivalent to the one defining
floor(q-a). Thus the device can compute the rounded scaled gradient first,
take its integer ceiling, subtract in integers and clamp. Guard the shift
before conversion and reject a successor outside the word envelope. This
preserves the exact projected update **of the computed floating gradient**;
it does not prove that gradient equals the native one.

For q65536 and a2^-12, nearest single subtraction rounds q-a back to q;
floor then gives65536 instead of65535. The integer identity avoids this
extra master-magnitude error, including at q2^32-1. It cannot repair a
gradient already lost in the forward/backward schedule.

## A current perfect prediction can conceal a future learning error

There is a two-label ordinary causal token witness. Let p16, eta1/16 and
unit1; each base is1. One input channel has default embedding2^-16,
including PAD, while token1's embedding is1. Its sole core feature is the
square of the lag-one embedding. Both output weights initially equal1.

At the file start the native feature is2^-32. Half storage rounds that
PRODUCT to zero. Both paths nevertheless predict exactly(1/2,1/2).
Observe target1. Native non-target gradient is1/[2(2^32+1)] > 0, while
the physical one is0. Native masters become(65535,65536); the physical
masters stay(65536,65536). Both embedding gradients are exactly zero at
this first symmetric prediction, so the token1 embedding stays1.

The next ordinary source is therefore token1 and the feature is1 on both
paths. Native target1 probability is131072/262143; physical probability
is1/2. Their gap is1/524286. This is a legal immediate continuation using
the actually observed target, not a forged source context. Exact current
probability agreement gave no permission to discard the small feature's
gradient. This refutes a zero-error whole-learner bridge for this schedule,
not Foundation or the existence of an approximate finite-prefix relation.

Even avoiding underflow cannot generally infer an exact grid endpoint from
a nonzero gradient tolerance: projection is discontinuous at integer scaled
gradients. The reference may resolve exact cells; an AMP trajectory must
retain its own endpoint and have its actual complete relation checked.
Do not silently snap it to the reference or widen a failed tolerance after
seeing its outcome. A future complete bridge needs its declared state/error
class and owned failure behavior, not just the current target probability.

## Actual-device preregistration

Run exactly two fresh jobs with [run_token_amp_audit.py](../../scripts/run_token_amp_audit.py)
after committing all inputs. Each has a preattached4-GiB Windows private
commit fence and900-second deadline, one active process, a512-MiB Torch
allocator cap and a conservative24-GiB whole-physical-board VRAM upper.
The latter is not measured per-process VRAM or exclusive availability.
Imports, controls, transfers and checks all count in the job. Parent and
shared platform costs remain outside this scope.

Bind the existing actual target: Torch2.12.0+cu132, build
7661cd9c6b841b62b7f411aa52ec51f05457263b, CUDA13.2, RTX3090 capability8.6;
the existing native CUDA/NVML contract binds runtime/driver API13040 and
driver616.92 to the same physical board. No CPU fallback is permitted.

1. **small-exact** runs the integer-grid witness, the half-underflow/future
   witness and six complete native fixture trajectories: unit1/2 times
   mixed/zero-input/zero-core initialization, word(0,1,1,0,0,1). Check every
   actual half/single primitive word with the exact binary rounding oracle,
   including signed zeros and every complete optimizer/source endpoint.
   Report native discrepancies instead of assuming exact endpoint equality.
2. **train-context512** runs the single fixed complete unit from the
   [CPU feasibility protocol](REFERENCE_HOST_PROTOCOL.md): first512 training
   tokens, full vocabulary/context512, four supplied SUMs/four PRODUCTs.
   Compare all stored feature, normalizer, target-mass and complete gradient
   basis words and every endpoint against independent CPU execution of the
   same physical schedule. Separately report complete master differences
   and sound absolute gradient-basis/value discrepancy upper bounds against
   the native enclosure reference. This large case does not claim an exact
   per-primitive RNE audit; the small case supplies that audit at its own scope.

Numerical native discrepancies are expected measurements, not waived bridge
failures: **no tolerance-qualified bridge is attempted or issued here**.
The exact counterexample is registered before device execution. No language
loss, validation/test data, topology selection or model ranking is included.
The GPU is not initialized from a trained reference state. Every old device
origin must remain unchanged after constructing its successor.

The original journal is `FP_TOKEN_AMP_CUDA_A1.json`; any existing journal
blocks replay. Stop on an unexpected arithmetic/word comparison, device,
worker, host or timeout failure. Retain the failed attempt; do not adjust
the cap or numerical schedule within it. Store only compact aggregate
evidence, not arrays or weights. After this gate, attack the observed bridge
obstacle and integrate the actual Runtime path rather than adding static
variants or returning to relation tasks.

PyTorch documents [ceil](https://docs.pytorch.org/docs/2.14/generated/torch.ceil.html)
and cautions that [floating reductions and platforms need not agree](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html).
Those current documentation pages are API context, not a substitute for the
pinned build and exact word audit of this execution.
