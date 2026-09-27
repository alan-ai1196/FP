# Compose native gradient enclosures inside an owned update unit

Status: **CONDITIONAL ENCLOSURE AND SCHEDULE THEOREMS; CPU AND FINITE CUDA PASS**.
The optional `TokenCudaPrefixContract(composed_native=True)` changes the native
interval solver. It changes no Foundation/ERC definition, G, Gamma, U, token
source, AMP arithmetic, physical read boundary, persistence or install rule.
It issues no `CERTIFIED_COMPLETE` or new installation authority. Ordinary
next-token learning remains the objective; no relation-task branch is reopened.

## Exact object and decision class

Fix one committed packed origin theta and a registered update unit of B events.
For every revealed original source window x_j and target y_j, let g_j be the
exact gradient of that event at theta. Parameters remain theta until the whole
unit commits. The pending native gradient is therefore

    G_t = sum_{j=1}^t g_j,                 1 <= t <= B.

This holds for tied SUM slots, repeated incidences/features, shared PRODUCTs,
squares and zero factors: differentiation and finite addition are linear in
the event index. It does not assume positive gradients. Reordering the source
windows in a *registered profile* changes their sequence but not this argument;
the original windows, targets and profile multiplicities must all remain.

For the untied readout, retain the existing basis: common row sum c, and the
target-indexed corrections d_y. The exact output gradient is c-d_y, with an
absent correction equal to exact zero. Embedding coordinates are grouped by
the actual token in each original window, retaining every repeated lag
incidence in the one-event derivative. Absent token rows contribute zero.

The new solver's decision class is **one supplied, actually retained pending
prefix and its actual physical state** under the existing fixed absolute
state tolerance and readout envelope. Success bounds all master and pending
gradient coordinates. A `GradientBounds` value is a *projection used by that
predicate*, not a historical-activation cache, a reached-state certificate or
a grid-commit decision. It retains the complete `Unit` exact replay recipe.
Caller construction of a projection or forest tuple is not evidence of its
soundness. Runtime accepts no caller-supplied forest, binding or projection.

## Enclosure induction

Run the existing outward binary64 `token_batch.Kernel` on each new single
event under theta. Its seven ordinary basis components give an enclosure of
that event's exact gradient. The same finite/denominator/element guards apply.
No result from the physical learner supplies this native derivative.

For core/common vectors and each present embedding/correction row, append
the enclosure to a forest of consecutive perfect binary trees. Only adjacent
trees of the same size carry. Each stored block is an exact builtin tuple
containing its size, shape and two immutable byte arrays of binary64 endpoints.

Assume each input interval contains its exact vector. An outward addition
contains the exact sum, including signed contributions and cancellation.
Induction on carries proves each block encloses precisely its represented
event contributions. The descending block sizes are the binary expansion of
that row's event count. A right fold of their values is the ragged spine of the
explicit balanced reducer and encloses the whole row sum. Missing rows have
exactly zero contribution; no nonzero incidence is pruned. Subtracting an
enclosed target correction from the enclosed common row contains the actual
signed output gradient. This proves containment of every coordinate of G_t.

Finite outward operations are a premise, not an assumed precision guarantee.
Overflow, a denominator interval crossing zero, exhausted elements or state
tolerance produce `UNRESOLVED`. No tolerance, grid or physical arithmetic is
relaxed. The existing full-batch native commit is still executed once at B;
only its independently unique exact grid cells can publish new native masters.
The forest resets after this commit, and Gamma starts an independent empty
forest for every newborn. Profile attachment may change only the committed
ordinary cursor, as before.

**Not endpoint equivalence.** The old batch kernel sums across events before
some tied-slot reductions and groups embedding incidences in lag-major order.
The new solver first completes each event's derivative. Those binary64
associations can differ. Both can contain the exact gradient yet return
different endpoints and different acceptance decisions at a fixed tolerance.
No old pass/refuse equivalence or interval-width dominance is claimed. The
finite audit records a concrete ordinary-token witness to endpoint difference.

Old per-event native forward arrays are disposable solver workspaces, just as
in the original batch solver. Their absence from the new continuation cache
does not erase an observation: theta and every original (x_j,y_j) remain, and
the exact native decoder can still reconstruct historical quantities. Future
fixed-origin gradients require that recipe and the additive basis, not an old
forward workspace. All *physical* leaves and their fresh read checks remain.

## Owned binding and failure boundary

Admission prepays the existing phase tariff plus `token_gradient_forest.work`.
Before a cache is used, the private owner derives a fresh exact value image of
the definition, masters, clocks, committed source, original windows and targets.
The image contains only exact builtin tuples, ints, strings and bytes;
Fractions are integer pairs. It contains no live dataclass, NumPy array, public
mapping or digest. Equal immutable subtrees may be shared only after this
fresh value comparison. This avoids repeated retained copies of the model.

Prediction/readout must match the previous image exactly. Observation must
extend its windows and targets by exactly the one owned revealed record,
under the same origin. Commit must follow the complete B-record unit and
advance the registered clocks. A current/staged phase ID comes only from the
existing Runtime seal/accept/publication path. The private `_native_bounds`
table retains each proposal and its immutable image. Public phase wrappers
and caller diagnostic arrays are not lookup sources.

Each phase's existing complete reference plus its new complete forest is
serialized in its prepaid phase frame. The image is a deterministic exact
projection of that reference and is also retained in `CudaPrefixSnapshot`.
All private table entries, including failed proposals, are exposed as
immutable snapshot values. Thus no hidden solver coordinate is omitted from
complete state. Host array temporaries, immutable images, table metadata,
canonical bytes and failed exception workspaces remain within the actual
whole-process/job host contract; the reference payload ledger still accounts
for the actual admitted frames/archive/pages. No free external cache exists.

Only sealing and accepting a successful phase can put its ID in a live root.
An unpaid phase does not compute a new derivative. An arithmetic, allocation
or retention failure cannot advance the learner or reuse its unaccepted
proposal. Already revealed targets and any admitted frames/proposals remain.
The ordinary predecessor, pre-target forecast, all new primitives and full
physical continuation caches are still freshly checked at their original
boundaries. Stored host gradient bounds never stand in for live device bytes.

This is a private serialized-owner argument under the existing closed-value
execution model. Arbitrary private Python reflection, concurrent owner calls,
external writes inside a protected operation and foreign cache injection are
not additional legal information interfaces.

## Exact work and storage laws

Use the successful ordinary decision class of
[TOKEN_PREFIX_AUDIT_COST.md](TOKEN_PREFIX_AUDIT_COST.md): one supplied incumbent,
B predict/observe pairs and the required commit, no profiles, reporting,
failures, extra diagnostics or closure work. Count an event row only when
evaluated inside `token_batch.Kernel._bound`.

| Component per complete unit | Original solver | Composed solver |
| --- | ---: | ---: |
| Native bound calls | 3B-1 | B+1 |
| Native forward/reverse event rows | B(3B+1)/2 | 2B |
| Physical leaf captures | B(7B+1)/2 | B(7B+1)/2 |

Proof: each new observation computes one single-event bound. Prediction
materializes the already owned gradient projection once and uses it for both
existing predicates; it computes no old gradient again. At B, the unchanged
native commit evaluates B rows independently. Before any commit, m successful
observations use exactly m native rows. Physical captures are unchanged by
inspection of the execution path and by complete CPU Runtime counters.

At B=512 this replaces 393,472 native event rows by **1,024**, with 513 bound
calls instead of 1,535. The unchanged 917,760 physical leaf captures, native
exact forecasts, model validation, readout envelopes and complete retention
are separate costs. This is not a 384.25-fold time prediction.

There is also an exact numeric-cache law. Write p(n)=popcount(n), C for core
slots, K for readout features and D for embedding width. At prefix t, let e_a
count events whose window contains token a at least once, and c_y count target
occurrences of label y. The live forest's **binary64 endpoint bytes** are

    16 [(C+K)p(t) + D sum_a p(e_a) + K sum_y p(c_y)].

This excludes shapes, keys, the complete binding recipe and historical phase
records; it is not a total-host bound. The expression follows because every
vector coordinate has exactly two eight-byte endpoints per carry block. No
per-event forward image is hidden in it. Across B appends, carry additions in
scalar coordinates are exactly

    (C+K)[B-p(B)] + D sum_a [e_a-p(e_a)] + K sum_y [c_y-p(c_y)].

Root extraction adds work at every predicate. Materializing all sparse rows,
comparing all original records and serializing complete phase history can
still accumulate quadratic work within B. This theorem removes repeated
native event differentiation; it does **not** establish linear whole-Runtime
time, linear historical evidence size or affordable language-model training.
The explicit extra tariff bounds image construction, sparse planning, carry
updates and up to two complete projections per phase; it is a conservative
primitive-operation allowance, not a Python-heap, bit-time or wall-time law.

## Evidence and next decision

`scripts/audit_composed_token_bounds.py` supplies exact Fraction checks,
binary64 boundary sums, source/profile binding attacks and paired complete
Runtime trajectories with CPU array/device substitution. Its evidence is
`FP_COMPOSED_TOKEN_BOUNDS_CPU.json`; CPU execution supplies no actual CUDA
authority. Default-off registration leaves the original solver available.

The exact controls cover 1,029 boundary prefix sums, 192 native histories,
23,296 gradient-coordinate comparisons, 12,516 readout-basis comparisons,
336 unchanged exact commits and 16 repeated/out-of-order profiles. They find
839 batch/composed gradient endpoint differences with exact containment in
both; the first witness is retained. The endpoint-byte formula is checked
at every ordinary exact prefix. Twenty paired complete Runtime histories
preserve 357 native/physical phase bodies after excluding the intentionally
different interval diagnostics and new cache field. Fresh leaf capture and
primitive-word counts, complete learners, reports and old snapshots agree.
Unpaid work, arithmetic/memory/retention failures, changed physical leaves,
public cache writes and forged origins/records exercise the refusal boundary.
Two additional paired CPU tensor histories run grouping with append-only and
reusing arenas. Both preserve23 checked phases, physical allocation extents,
retirements and report totals per arm without creating a CUDA context. The
original default solver's full owner and schedule-count controls also pass.

### Fixed first actual-device comparison

`scripts/run_composed_bounds_cuda_a1.py --run` is a new exclusive registration,
not a replay of any earlier journal. It requires committed clean inputs and
the completed CPU gate. Two sequential fresh workers (`batch`, `composed`)
use the original full-V=50,257, context512, width4, K8, 603,092-master model and
unit512. Both keep the original first1,024 training bytes, observe only the
first16 targets, and open no validation/test data. Each keeps a240-second,
16-GiB host job, 1-GiB append-only CUDA arena/reservation, 2-GiB reference
payload, 64-MiB frame/images, 2^22 phase cells, state tolerance16 and the same
10^-6 probability/division tolerances. Grouped reads and physical reuse are
off in both. Device identity and lifetime counters remain binding.

Each positive trace must retain33 checked phases, every original record and
16 pending targets without a commit. An identical lightweight counter around
`Kernel._bound` must observe46 calls/376 rows in the batch arm and16/16 in the
composed arm. The existing independent batch predicate is checked outside
timing in both. After timing, the composed worker zeros an actual live leaf:
the next prediction must refuse while retaining old learner/evidence and a
complete failed phase. Compare the32 ordinary calls; initialization and the
extra fault are reported separately. This is one ordered pair with counters,
not a statistical speedup, complete-unit measurement or model result.

The exclusive journal is `FP_COMPOSED_BOUNDS_CUDA_A1.json`. Commit before
launch; do not reset counters, replay a terminal result or increase caps after
seeing failure. Its outcome determines whether this solver removes a measured
cost or only a counted component. No full-unit rerun is authorized by its
row-count theorem alone.

### Actual-device result and closure

The original pair at `c093979061ccfa78e8a615b296c2b0c0e3079168` completes.
`FP_COMPOSED_BOUNDS_CUDA_A1.json` is terminal with status
`COMPLETE_ACTUAL_COMPOSED_BOUNDS_A1`. Never replay it. Both workers exit0
without timeout or a resource kill, under every original cap and device
identity. Each positive trace retains33 checked phases/4,541,709 primitive
words,16 original targets/windows, cursor16, no commit and all16 pending
records. Their29,850,216 consumed arena bytes and lifetime allocation counters
`(1,1073741824,1)` agree. Neither allocator history nor peaks are reset.

| Measured component | Batch | Composed |
| --- | ---: | ---: |
| Ordinary native bound calls / event rows | 46 / 376 | 16 / 16 |
| Initialization seconds | 10.22115 | 10.37450 |
| First eight ordinary pairs, seconds | 40.23279 | 39.90785 |
| Last eight ordinary pairs, seconds | 43.36216 | 42.71037 |
| All32 ordinary calls, seconds | 83.59495 | 82.61821 |
| Whole-job peak commitment, bytes | 3,332,599,808 | 3,456,643,072 |
| Paid reference peak, bytes | 271,544,532 | 271,748,870 |

The ordinary-time ratio is1.0118222, an observed **1.16841% reduction** in
one ordered pair with identical counters. This is no statistical/general
speedup and provides little evidence of a practical early-prefix benefit.
Late-unit timing is unmeasured. The exact native-row reduction is confirmed,
but it is not a sufficient explanation of total runtime. Images remain336
entries/67,102,758 bytes in both arms.

After timing, the composed worker zeros the actual first live leaf. The next
prediction refuses with the changed-predecessor error, retains a34th complete
failed phase and the changed words, and leaves the old sealed bytes, native
learner and cursor intact. No new tensor allocation or successor appears.
Its whole-job time/commitment and final archive metrics include this extra
fault, so their difference is not an isolated cache-overhead measurement.

**This qualification is closed; the option remains default off.** The
algebraic composition question is settled for this fixed-origin unit and
the owned finite implementation is exercised. No further native-reduction
variant or full-unit replay follows from this small timing difference.
Repeated model validation/exact invariant work, complete retention and
fresh live-data checks remain relevant ordinary-text costs; this experiment
does not isolate their contributions. The earlier first-event CPU profile
is evidence about those costs, not a whole-unit decomposition. Progress on
them must preserve complete state and source/resource/bridge ownership.
Affordable ordinary next-token learning and strong trained baselines remain
the scientific objective; Foundation/ERC and the relation closure stay fixed.
