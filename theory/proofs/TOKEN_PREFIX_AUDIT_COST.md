# Repeated prefix cost of the current ordinary-token verifier

Status: **EXACT SCHEDULE LAW; COMPLETE CPU RUNTIME COUNT CONTROL PASS**.
This concerns the successful ordinary path with `composed_native=False`
and `archive_workspaces=False`,
not an information lower bound on FP, a new numerical bridge or a wall-time
theorem. Foundation/ERC and the rational/relation closure remain unchanged.
The physical raw-call count below refers to the original separate-copy path
(`grouped_reads=False`). The subsequent [grouped fresh-read lowering](GROUPED_FRESH_TOKEN_READS.md)
preserves logical leaf inspections and native reevaluations while changing
the number and size of actual transport calls.
The subsequent [owned native gradient composition](COMPOSED_TOKEN_NATIVE_BOUNDS.md)
changes native event evaluations to 2B while retaining the physical captures.
The later [owned workspace lowering](TOKEN_WORKSPACE_LIVENESS.md) decodes sealed
historical fields, freshly captures live operands and adds an observation
validation capture. These original physical-call laws do not apply to it.

The [owned-image comparison](OWNED_CANONICAL_IMAGES.md#actual-device-result-and-closure)
reduces the four first ordinary CUDA calls from 18.70098 to 9.84782 seconds
while preserving all fresh reads. It cannot remove repetitions that precede
serialization. The following count law identifies those repetitions without
launching another long trajectory or interpreting a short profile as a
whole-unit cost decomposition.

## Decision class and exact counts

Fix one supplied token G/Gamma/U, one incumbent, update-unit size B >= 1, and
a successful sequence of B ordinary predict/observe pairs followed by its
required native and physical commit. There are no profile, reporting,
installation, run-closure, extra external predicate or failed/retried calls
inside this count. Each unit starts at a committed origin. Resource failures
can truncate it and are outside the successful-count assertion.

A **native event evaluation** here is one retained event row evaluated inside
`token_batch.Kernel._bound`. It includes that row's forward/reverse contribution
in the batched enclosure calculation; it does not mean a separately issued
Python call per row. Exact scalar forecasts, new physical primitive execution
and interval reductions add other work. A **leaf capture** is one physical-side
`LeafWords.capture`, excluding the independent CPU producer's captures.

For event k in 1,...,B, the pending predecessor contains k-1 leaves:

| Ordinary operation | Native rows reevaluated | Physical leaf captures |
| --- | ---: | ---: |
| Prediction k | 2(k-1) | 3(k-1) |
| Observation k, before any commit | k | 4k-2 |
| Required commit, once at B | B | 2B |

**Derivation.** `token_cuda_prefix.execute` checks the prediction predecessor
through `check_state`, then `check_prediction` constructs the same native
prefix again. Empty prefixes use the committed origin. Observation checks
the new k-record state, and `TokenReferenceMachine.commit` independently
reconstructs the B-record native bound. The physical commit's final native
state is a committed origin and adds no `_bound` call.

Prediction freshly captures its old resident before execution, after execution
to exclude mutation, and again for complete retained state. Observation
captures its predecessor twice and its successor twice. Commit captures its
B-leaf predecessor twice; its successor has no pending leaves. Forecast word
captures do not themselves contain leaves. Every call still runs under the
ordinary source, state, ownership, numerical and retention checks.

Summing gives the exact per-unit laws:

    native bound calls      = 3B - 1
    native event evaluations = B(3B + 1)/2
    physical leaf captures   = B(7B + 1)/2.

Equivalently, original event j contributes to 3(B-j)+2 native reevaluations
and 7(B-j)+4 physical leaf captures. An unfinished m-event prefix with no
commit has m(3m-1)/2 native event evaluations and m(7m-3)/2 leaf captures.
This explains why two-event measurements omit most of the unit's repetitions.

The argument applies to both shared-retention modes and optional image reuse:
those change representation after the fresh numerical captures. The owned
arena reuse implementation also preserves these calls. It is not inferred
from the image cache's hit rate or a compression ratio.

## Fresh-read count and byte law

Each leaf capture reads seven named numeric arrays: values, normalizer,
target mass, embedding gradients, core gradients, common readout gradients
and target corrections. Thus leaf captures alone issue

    raw calls = 7B(7B + 1)/2.

Let M be the number of stored native input/core activations, C the number of
core slots, K the number of readout features, D the embedding width and r_j
the number of distinct source tokens, including padding, in event j's window.
The current half/single recipe gives exactly

    S_j = 2M + 8 + 4C + 8K + 4D r_j bytes per leaf capture,
    repeated leaf bytes = sum_j [7(B-j)+4] S_j.

This excludes host incidence metadata, masters, prepared operands, forests,
current basis, forecasts, all other primitive reads and complete evidence
serialization. It is a lower component of total read traffic, not its total.
Zero-sized arrays still have raw calls; the CUDA copy skips empty extents.
All seven arrays are nonempty in the existing full-V fixture.

`CudaArrays.raw` uses `CudaWorkspace.raw_bytes`, which currently copies each
named extent separately with `non_blocking=False`. The laws count read calls
and payload bytes, not a minimum duration for any call. The phase field
`forward_operations` / journal `checked_device_words` counts checked primitive
outputs; it is not a counter of all repeated device reads.

For the existing full-V fixture, B=512, M=2056, C=4, K=8 and D=4. Therefore:

- 1,535 native bound calls evaluate 393,472 event rows: 768.5 per target.
- 917,760 leaf captures issue 6,424,320 raw calls: 12,547.5 per target.
- Since r_j >= 1, each leaf has at least 4,216 bytes, for at least
  3,869,276,160 repeated leaf-read bytes per unit.

These are deductions from the schedule and shapes, not new GPU measurements
or measurements of A2's complete transfer traffic. For N targets comprising
whole units of fixed size B, these components scale as Theta(NB), not
Theta(N^2). Quadratic growth is within B; retained global history and ledger
costs can add separate growth across units.

## CPU control and consequence

`scripts/audit_token_prefix_cost.py` runs the complete ordinary Runtime with
the existing CPU device/array substitution and existing mixed SUM/PRODUCT
fixture. It completes two units at each B in {1,2,4,8}: 30 observations,
72 checked phases and eight commits. Instrumentation counts actual native
prefix lengths, physical-side leaf captures and raw calls/bytes, without
altering checks or supplying forecasts. Every individual predict/observe
call matches the table, including resets and commits. Every captured leaf
matches the exact byte formula. The pure full-V model factory supplies only
the stated shapes; no corpus file or Torch/CUDA backend is opened. Evidence
is `FP_TOKEN_PREFIX_COST_CPU.json`.

The image qualification is closed. Optimizing only constant metadata checks
or image placement cannot remove these structural repetitions. This supplies
an implementation reason to investigate composing native enclosures over
immutable retained events and grouping fresh physical reads at unchanged
observation boundaries. Neither lowering is implemented; its preservation
and ownership argument still has to be established at this entry's source.
The subsequent grouped-read proof/implementation above now addresses that
transport question; native enclosure composition remains unimplemented.

The distinction matters for correctness. A stored host leaf is not evidence
that its still-live device array is unchanged: the existing changed-leaf
control refuses a real physical-side array mutation while the earlier sealed
record stays intact. Reusing native solver results would require binding all
inputs, complete owned cache state and numerical allowances. Grouping reads
would require preserving every named extent/generation and its observation
boundary, with paid workspace and no intervening legal writes. Dropping live
arrays, weakening tolerances, shrinking B to change U, or omitting complete
records does not follow from the count law.
