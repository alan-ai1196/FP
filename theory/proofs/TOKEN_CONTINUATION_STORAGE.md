# Continuation roots for token device storage

**Status:** sufficient-root/ownership argument, optional owned implementation
and complete CPU Runtime/array controls. Actual device reuse is not yet
qualified. The running shared-retention A2 remains fixed at307251e and never
uses this preparation. The earlier passive trace and generation component
are now connected by the implemented lowering in the final section.

The default ordinary-text executor retains every device temporary. Its
append-only allocation sum is an implementation cost, not a lower bound on
the device storage needed by the registered learner. For reuse,
distinguish the complete historical evidence from physical arrays
that a future owned phase can still read.
The execution premise remains the existing serialized private owner with
hidden raw tensor handles, not arbitrary external Python/device mutation.

The immutable-history premise needs the subsequent
[token snapshot repair](../../experiments/next_token/FROZEN_TOKEN_REPORTING.md#7-public-snapshot-counterexample-and-value-boundary-repair).
At a7d2232, public relation/plan mappings were writable despite the frozen
outer record. A normalization write actually falsified reporting. The repair
detaches/freezes those mappings and preserves their canonical bytes. This
corrects that implementation premise; it adds no physical roots and grants
no device-reuse authority.

## The boundary and the roots

Consider the existing closed `TokenCudaPrefixContract`, which excludes
likelihood encodings and installation. Use a boundary at entry to the next
owned token phase, with no active CUDA workspace. Every earlier completed
phase has already gone through Runtime's evidence-retention and acceptance
path, or failed without gaining publication authority. All immutable phase
records, source/target records, resource history and snapshot data stay.
The declaration is not permission to collect at workspace closure: complete
fresh capture and evidence retention occur after that closure.

Let I be the union of phase IDs in `current`, `staged` and `predicted`, for
all candidates. For each value in `_values[I]`, keep its named tensors from
`tensors()`. Also follow `PredictionResident.predecessor` and
`ReadoutResident.prediction` transitively, keeping the named tensors of each
visited resident. Retain the entire registered allocation containing each
view, including its padding, rather than just the view's visible slice.
Also pin every allocation of an attempted phase whose complete evidence
has not been successfully sealed. A failed capture or writer must not let
unrecorded physical information disappear just because no learner map
references it. A reclamation implementation needs the actual owner's seal
boundary; a backend's self-reported CHECKED status is not that boundary.

This is a conservative root set, not a claim of minimal liveness. In
particular, stale mapped predictions or retired candidates may over-retain.

During a phase, keep those boundary allocations and **every new allocation**
until complete checking, fresh capture, retention and acceptance have ended.
Do not publish a successor or free an input merely because its numeric
transition finished. In an ordinary update, the old published learner and
the staged successor coexist through commit and joint publication.

## Why these roots suffice for the existing token continuation interface

The argument is induction on the next supported phase and then on the
length of a legal Runtime continuation:

1. `token_cuda_prefix.execute` obtains every physical predecessor from
   `current` or `staged`, and every observation/readout forecast from
   `predicted`. Initialization has no physical predecessor. The selected
   values therefore lie in the retained resident closure.
2. `Resident.raw` and `tensors` name the same master, prepared, leaf, carry
   forest and basis arrays. A prediction/readout names its own arrays and
   retains its predecessor identity. The conservative closure includes all
   those predecessor arrays too. Complete pre-transition and post-transition
   readbacks remain possible; a gradient total alone is not this root set.
3. The closed `transition`/`Kernel` operations read those input residents or
   newly allocated results. They construct successors from those same
   objects and new arrays. Primitive validation and raw operation capture
   may read every new result, so none of these temporaries is released
   before the phase's evidence is sealed. A complete successor's named
   arrays are therefore a subset of inputs plus this phase's allocations.
4. The existing acceptance/publication paths update the maps only to actual
   newly retained phases, retain an existing map, or remove a published
   candidate. Profile attachment and replay use `staged`; a newborn derives
   fresh Gamma. No token Runtime operation resolves an arbitrary historical
   phase into a physical learner. Candidate IDs are monotonically fresh.
5. Historical inspection uses immutable phase records and arena metadata.
   `CudaPrefixSnapshot` exports no `Resident`, tensor, `_values` map or
   writable workspace. Current-state relation/range inspection also uses
   phase words. The extra physical `_values` readers in likelihood and
   installation are unreachable under this token registration. They are
   excluded premises, not silently covered extensions.

Thus a device allocation outside this closure, the unsealed-attempt pins
and the in-flight outputs is
not read by the next legal token phase. Its omission cannot change the next
phase's array inputs, provided the storage implementation admits only the
retained generation of each view. The same argument then applies at the
next boundary. Full historical values remain available from retained words;
this is not permission to replace a fresh read of a live array with a host
image. It also supplies no liveness result for future installation,
arbitrary historical replay APIs, new callbacks or other physical backends.

## Why the present arena cannot simply use a free list

The present `CudaArena._region_for` checks backing storage, offset, extent,
dtype and initialization. Its proof relies on addresses never being reused.
Allocate initialized view A, retire its address, then allocate same-shaped
view B at that address with different words. If both have the same backing
and dtype, A now passes those spatial checks as B. A saved A handle would
read B's data. Exact host evidence alone does not fix this aliasing error.

A future reusable lowering must therefore bind every issued view to a
unique allocation generation and reject retired generations before numeric
input, readback, write or derived-view admission. A derived view may borrow
only its live parent's generation; address equality cannot reauthorize an
old view. Historical phase acceptance must not resurrect a collected
physical resident. These are physical ownership obligations, not a new FP
architecture action or changed SUM/PRODUCT/optimizer semantics.

It must also retain full generation/retirement/resource history, charge
collection and coexistence, preserve failed frames and old roots on failed
admission, and keep actual/lifetime device allocation counters binding.
The root argument establishes neither such an implementation nor an
allocator fit, fragmentation, whole-host, throughput or model-quality bound.

## Measurement scope

`scripts/audit_token_storage_liveness.py` instruments the existing CPU array
schedule. Every kernel input and every named resident capture must belong
to the previous boundary roots or the current phase's new allocations.
The shadow live set releases only at the stated boundary; CPU values are
not overwritten and no CUDA allocation is made. All phase outputs coexist
through finite checks and capture. Byte totals include the existing
eight-byte array alignment and one phase header at a time.

The full probe uses the existing V=50,257, L=512, D=4, K=8, 603,092-master
resource model for two complete update units and frozen readout. Targets
are an explicit affine permutation of token IDs, not corpus data. The
declared live/coexistence totals count an ideal compact set of allocations;
they do not establish a realizable layout or an all-history supremum.
The probe checks a sufficient access set, including transitive predecessor
arrays, rather than claiming that its read sequence equals every owner
readback call. It repeats no numerical bridge or device certificate.

The initial prototype unnecessarily reconstructed full `StateWords` on
each capture. It was stopped without a result and replaced by direct fresh
reads of all named arrays; repeated model-definition validation is irrelevant
to this allocation-access question. The fixed A2 worker was not interrupted.

The completed full trace checks42,985,243 array inputs across2,055 phases,
allocating3,112,430 regions. Its exact padded-byte totals are:

| Quantity | Bytes |
|---|---:|
| Append-only cumulative allocation | 834,873,456 |
| Largest retained continuation root set | 16,515,368 |
| Largest roots plus complete new phase coexistence | 33,718,200 |
| Terminal frozen-report root set | 5,029,936 |

Peak retained region count is9,247; both byte peaks occur during commit
staging. The small two-unit control checks6,652 inputs across23 phases.
Evidence is FP_TOKEN_STORAGE_LIVENESS_CPU.json. These successful traces have
no failed/unsealed pins. A real allocator still needs fragmentation and
failure handling, and its full backing allocation remains charged.

## Generation control and the implementation decision

`scripts/audit_array_generations.py` invokes the actual spatial predicate
on CPU half, single and int64 tensor views. In each counterfactual reused
extent, the old view passes and reads the new words. This is **not a defect
in the present append-only arena**, whose no-reuse premise excludes it.
It falsifies adding address reuse while leaving its guard unchanged.

The passive `array_generations.ArrayGenerations` component binds exact
weak object identity to monotonically fresh allocation generations. Derived
views retain their live parent's generation. A known old view cannot be
reissued or rebound, even to an equal address; retired views refuse. Dead
Python views may be pruned, but their allocation is not implicitly retired.
An attempted issue spends its generation before fallible metadata growth,
so a failed admission cannot recycle that name. Storage geometry, owner,
initialization, resource and seal checks remain separate required premises;
this component alone grants no physical read/write or reclamation authority.

The CPU control passes27 actual-tensor refusals,3,125 five-action histories
and15,625 actions against a separate identity/live-set oracle, plus two
metadata-failure boundaries. No CUDA context is initialized. Aggregate
evidence is FP_ARRAY_GENERATIONS_CPU.json.

The trace motivated the single owned implementation below: cumulative
temporary allocation is much larger than this sufficient continuation set.
Do not extend this into more passive storage or relation examples. No change
to Foundation, the frozen experiment semantics, G/Gamma/U, numerical
tolerances or current A2 registration follows from these results.

## Implemented owned lowering and its exact scope

`TokenCudaPrefixContract(reuse_regions=True)` now selects
`token_reuse.TokenReuseArena` and a distinct registered work model. The default
continues to append. The optional lowering requires a power-of-two backing
extent and excludes installation and likelihood representations through the
existing token contract. There is still one actual backing allocation, fully
charged to both roles with all existing allocator/device lifetime checks.
No allocator counter or cache is reset.

At the next Runtime phase entry, the owner prepays collection and new-view
metadata work, allocates its ordinary evidence frame, and computes the roots
above. The collector frees only generations outside that root closure whose
successful producing phase has been sealed by the owner. Runtime supplies
that seal **after actual complete frame retention succeeds**, not when the
workspace closes or the executor returns CHECKED. Failed/unsealed attempts
remain pinned, including their headers and initialized or uninitialized
allocations. This conservatively also pins successfully captured failure
records. All new outputs survive until the next eligible phase entry.

Every admitted output receives an exact-object generation binding. Supported
reshapes derive that same live generation after checking backing, dtype and
extent containment. Numeric inputs, writes and fresh raw readbacks require
both generation and the original geometry/initialization conditions. Retire
invalidates the generation before returning its block to the pool. Dead weak
views may disappear; a retained stale view can never be issued or rebound to
a new generation. Acceptance requires a sealed, previously unaccepted phase,
so an old phase cannot resurrect a collected physical resident.

The full historical phase records, all region metadata, generation names,
allocation totals, headers and retirement records remain available. Only
sealed physical lookup entries unreachable from the three owner maps are
removed; source/target records, native states and retained physical words are
unchanged. Fresh reads of every live predecessor and every new output still
execute. The snapshot value-boundary correction above is part of this proof.

The pool splits a power-of-two free block and coalesces free buddies on
release. For array byte size n, define the old padded request and the new
reserved block by

    a(n) = max(8, 8 ceil(n/8)),
    b(n) = 2^ceil(log2(max(8,n))).

Then `a(n) <= b(n) < 2 a(n)`. If L is the current set of retained allocation
generations and H its retained phase headers, the exact occupied-block law is

    occupied = 8 |H| + sum_{i in L} b(n_i).

Thus buddy rounding costs less than twice the corresponding eight-byte-padded
occupied sum when any block/header is live; both sums are zero otherwise.
L includes current roots, every unsealed pin and every in-flight
output; it does not count historical words as live device arrays. This is an
**occupied-block law conditional on admission**, not a guarantee that an arena
of twice the ideal live-byte peak can fit every allocation. Fragmentation
can leave no sufficiently large free block. That condition returns UNRESOLVED;
the actual whole backing extent remains charged irrespective of occupancy.
The full-vocabulary passive trace above is not a measured buddy layout.

The induction is now operational: the retained roots can supply every legal
next read; generation checks exclude recycled aliases; new outputs are
disjoint until their complete checks/retention; the only next publication is
the existing owned transition. No new semantic architecture action is added.
Whole-host metadata/word history, work, elapsed time and fit remain separate
constraints. Collection failure cannot publish a learner; a partial metadata
failure closes the arena, and MemoryError uses Runtime's existing terminal
host-failure boundary.

`scripts/audit_owned_token_reuse.py --write` substitutes only device binding
and counters with one actual CPU tensor backing buffer. It runs the actual
Torch array operations, workspace/view guards, complete token Runtime,
native/physical checks, frame retention and scoring. It provides:

- 36 paired append-only/reusing histories, including all binary four-event
  words, deeper carries, multi-candidate profiles and plain/shared frames.
  All602 phase encodings/24,380,806 body bytes and native/physical report
  accumulators agree. Eight profile events are included. Historical snapshots
  remain unchanged after actual memory reuse;62,386 generations are retired.
- One finite capacity witness:16 training events/eight units and two frozen
  reports complete45 phases using an8,192-byte backing buffer, with5,096 peak
  occupied bytes. All phase/score values match the append-only run, which
  consumes104,904 bytes. Cumulative buddy requests total120,304 bytes.
- Actual address reuse overwrites an old view's words; nine stale/unissued
  view or authority operations refuse. Unsealed allocations and headers stay.
- All3,125 five-action allocation/free histories,15,625 independent complete
  partition checks and1,266 allocation refusals with unchanged pool state.
- Four post-target boundaries: unpaid collection, unsealed frame, partial
  allocation and retirement MemoryError. Targets and old learners remain;
  unsealed pins survive diagnostic collection and memory failure is terminal.

Evidence is `evidence/minimal/FP_OWNED_TOKEN_REUSE_CPU.json`. The existing
reporting, public-snapshot and544-phase shared-word regressions pass. No CUDA
context is initialized by this audit. These are finite CPU implementation
checks and one constructive toy capacity witness, not a device result,
full-vocabulary fit, sustained corpus feasibility or `CERTIFIED_COMPLETE`.
Keep A2 fixed; actual reuse qualification follows its terminal outcome. The
destination remains affordable ordinary-text learning with strong baselines.

## Actual bounded device qualification

Both original workers registered in
[OWNED_TOKEN_REUSE.md](../../experiments/next_token/OWNED_TOKEN_REUSE.md#actual-device-result-and-closure)
pass at6941373 after A2's separate original execution terminated. The
successful worker completes16 targets/eight commits and two frozen reports,
with45 checked phases and19,164 checked array words. Actual address reuse
overwrites the saved forecast extent and the old handle refuses; both public
normalization writes also refuse. Occupancy peaks at5,096 bytes within one
8,192-byte allocation, despite120,304 cumulative buddy-reserved bytes and
5,341 retired generations. The original CPU capacity witness now has this
scoped physical execution, not a general allocator-fit guarantee.

The second worker retains eight phase records/seven checked records and3,351
checked words, including the final executed but unsealed failure. It keeps
all185 failed generations plus their header, the actually revealed third
target1, cursor2 and the preceding learner. No successor publishes. Both
workers retain all header history, use2-MiB allocator reservation and preserve
actual/lifetime counters(1,8192,1). Their host peaks fit the unchanged4-GiB
caps and neither reaches its180-second deadline.

The journal `FP_TOKEN_REUSE_CUDA_A1.json` is terminal. No full-V fit, corpus
score, training throughput or whole-Compiler completeness follows. Do not
extend this into more reuse controls: the remaining ordinary-text obstacle
is affordable complete execution, including retained host and reference work.
