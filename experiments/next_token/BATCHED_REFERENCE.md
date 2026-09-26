# Batched complete native token units

Status: **CONDITIONAL NUMERICAL REFINEMENT; EXACT AUDIT PASS, 2026-09-26**.
The [implementation](batched_tokens.py) evaluates already retained update
units of the [native learner](NATIVE_TOKEN_LEARNER.md). It changes no graph,
initializer, gradient or optimizer. It supplies no Runtime, data-role,
online freshness, AMP, total-host-resource or model-quality certificate.

## What batching preserves

Fix a complete committed origin and the N actual source/target records in
one registered update unit. Native parameters are fixed throughout that
unit. Each event's forward values and gradients can therefore be computed
independently, then its gradient contributions added. Exact addition is
associative; grouping by DAG depth, parameter slot, target or input token
preserves every incidence, including tied slots, shared PRODUCT parents,
squares, repeated features and repeated tokens. Empty SUMs and unused slots
remain present. No within-unit intermediate parameter update is skipped.

This proves a refinement of the complete pending gradient and committed
endpoint for that fixed G/Gamma/U. It does not equate arbitrary Compiler
control traces: a constructor could acquire information or act between
events. Batch input already contains revealed records. In particular,
source positions need not equal learner time, and every actual source
window is retained as required by the [source-clock proof](SOURCE_AND_LEARNER_CLOCKS.md).

The kernel uses outward binary64 interval arithmetic under the same
nearest-rounding/gradual-underflow assumptions as the
[scalar solver](EXACT_COMMITS_WITH_ENCLOSURES.md). Array broadcasting applies
those scalar rules elementwise. Reductions use explicit balanced addition
trees; grouped reductions sort integer keys stably and pair equal-key
rows, retaining unpaired rows. They do not assume a vendor BLAS or floating
`sum` reduction order. Induction over these trees and the forward/reverse
DAG encloses the complete native gradient basis.

Committed masters use immutable byte buffers of uint32 grid integers, with
grid exponent p <= 32 and vocabulary V <= 2^20. These are realization
limits, not semantic restrictions on FP. Converting a master to binary64
and scaling by 2^-p is exact. Each readout column's integer sum is strictly
below 2^52, so uint64 accumulation and its binary64 conversion are also
exact. All remaining arithmetic uses enclosures; nonfinite values refuse.

For every touched embedding row, every core slot and every readout cell,
the kernel encloses q - 2^p eta G/N. Only equal endpoint values of
max(0,floor(.)) authorize the next integer. Target readout rows include
their signed correction before projection, using the old master. Untouched
embedding rows have structurally zero gradients. All decisions must resolve
before a new immutable origin is returned. Induction gives exact committed
native states without cumulative floating endpoint error. A refusal retains
the complete unit and its optional exact decoder; it does not select a
midpoint or silently call an oracle.

## Resource and authority boundary

The kernel preflights a declared per-array element limit, including input
masters, feature batches with repeated indices, edge metadata, and the
largest forward/reverse incidence arrays. Pairwise min/max avoids an
implicit stack of four complete product arrays. Many such arrays can coexist:
**this limit is not a total memory or work bound**. Python source records,
metadata, immutable old versions, exact materialization and failure scratch
also cost resources. A whole-process job is the next empirical check.

The packed buffers cannot be made writable through their NumPy views.
Intermediate intervals remain passive mutable data; callers can fabricate
dataclasses. No caller-supplied bound is Runtime authority. Actual source
acquisition, role restrictions, ownership, failed-unit retention and the
physical AMP relation remain integration obligations. The full readout is
scanned once per commit, not expanded for every event; worst-case master
storage remains proportional to (V+1)D + J + VK.

## Minimal evidence

[The audit](../../scripts/audit_batched_tokens.py) and its
[3421-byte record](../../evidence/minimal/FP_BATCHED_TOKENS.json) cover:

- 350 exact broadcast checks, 432 nonpoint checks and 1,440 signed balanced
  or segmented reduction checks across all 120 permutations of five rows.
- All 384 small token words: 2,304 native event comparisons, 48,384 complete
  unit-gradient coordinate checks and 1,728 exact commits, with no oracle
  continuation. These reuse the independently literal-checked native cases.
- 96 retained-source schedules and 192 exact commits. Changing all targets
  leaves forward values and normalizers bit-identical. Eight schema/quota
  refusals cover dense inputs, repeated feature indices and edge metadata.
- Honest unresolved exact-zero boundaries, retained source/target units,
  immutable masters, empty SUMs, shared zero PRODUCTs and unused slots.
- A full 50,257-label, 512-event synthetic unit: 5,632 core values and the
  full pending gradient basis are enclosed; all 301,548 resulting parameters
  match the separate rational control. Its largest common denominator has
  12,303 bits. Packed master payload is 1,206,192 bytes, not total memory.

No text loss, throughput comparison or physical budget result is inferred
from these checks. Proceed to measured execution and the text study instead
of extending the static example catalog.
