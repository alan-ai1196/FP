# Numerical continuation needs live operands and complete history in different roles

Status: **NUMERICAL CONTINUATION THEOREM; CPU AND FINITE CUDA PASS; QUALIFICATION CLOSED**.
This is ordinary-token research under frozen Foundation/ERC. It introduces
no new semantic architecture action, G/Gamma/U, source interface or precision
rule. The owner implementation below now has complete CPU controls. No CUDA
authority, performance claim or `CERTIFIED_COMPLETE` follows from the proof
or CPU substitution alone.

The [owned base-fact qualification](OWNED_TOKEN_BASE_FACTS.md#actual-result-and-closure)
is closed: its original 16-target device comparison reduced ordinary time
from 83.07 to 60.58 seconds. Another static invariant does not address the
remaining representation question. Must every historical event array stay
on the device merely because every original value must remain available?

## Exact continuation class

Fix the existing `token_array_events.Kernel`, its explicit half/single
operations and integer grid, one registered definition, a committed origin,
and a finite legal sequence of actual source windows and revealed targets.
This includes original windows supplied by an out-of-order or repeated
profile. Nothing in the argument permits a target to enter before disclosure
or a profile to invent a source window.

The numerical continuation class consists of its `predict`, `readout_label`,
`observe`, `append`, `basis` and `commit` operations, plus `prepare` on the
next committed origin. Gamma/initial upload is unchanged. All existing
shape, type, finite-value, grid and arithmetic guards remain. Assume each
compared numerical operation completes under its supplied allowance and
satisfies its registered RNE primitive decision. A different actual device
word must still be refused by the unchanged primitive checker. The
theorem does not assert that a representation change fits the same whole
Runtime memory/work budget.

Separate three kinds of information in a pending unit:

1. Current numerical operands: the actual masters and prepared operands,
   every block of every carry forest, and an outstanding forecast when one
   exists. Any region aliased by these operands remains live.
2. Causal metadata: the original windows/targets and their order, unit count,
   clocks, definition, origin identities and sparse row keys/counts.
3. Historical numerical values: each completed event's activations,
   normalizer, target mass, four gradient components and incidence arrays,
   plus the previously materialized current basis. All their exact words
   remain available in immutable images; this is not deletion or retention
   of only the current gradient sum.

"Historical" describes the role of a field, not permission to free its
storage. The same array can occur in both the first and third groups.
Resource identities, allocation geometry, alias/generation metadata and
failed/unsealed work are additional complete owner state, not numerical
values which this partition may discard.

## Continuation theorem

Replace access through every old leaf's numerical/incidence field and through
the previous basis by an inaccessible marker. Retain the causal metadata,
complete immutable historical images and all actual current operands,
including aliases through carry roots. Then every successful operation in
the stated class emits the same ordered primitive outputs, bit for bit,
including signed zeros, and the same next committed masters and clocks.

Proof by inspection and induction on the executed continuation:

- Prediction uses the original embedding masters, prepared core weights,
  readout column totals/base total and its actual source window.
- Label evaluation uses the supplied forecast, original output masters and
  prepared base. It does not use old leaf arrays or a prior basis.
- Observation differentiates the new forecast. `append` adds its new
  derivative to the existing carry forests; it only concatenates the old
  leaf metadata. It never reads an old leaf's array or incidence field.
- `basis` reads the carry forests and row keys. It constructs its result
  anew; the previously materialized basis is not an input.
- Commit likewise constructs a basis from the forests, projects the original
  masters and takes cursor/source metadata from the complete ordered records.
  Preparing the resulting origin therefore receives the same integer words.

Each primitive has the same ordered operands and operation; induction gives
the same outputs and guard outcomes. A newly produced event is then archived
without removing any array still reachable as a current operand. The same
argument applies at the next step and after unit reset. No associativity
change, native-gradient approximation or recalculation of a historical
floating result is used.

The original complete `StateWords` numerical diagnostic can be reconstructed:
read the actual live operands and decode all historical fields from their
exact typed word images. This supplies every former leaf/basis coordinate,
including values that future numerical operations do not read. It does not
pretend that a retired device address is still an initialized live array.
Original allocation/alias history and actual retirement state must also be
retained by a real owner. Current resource snapshots will correctly differ
from those of an owner that retains all device allocations indefinitely.

The scope is deliberate. An inaccessible marker cannot bypass `Resident.raw`,
tensor enumeration, predecessor equality or retention. The theorem identifies
the numerical read boundary; the owned lowering below separately implements
complete diagnostic decoding, live-root enumeration and sealed publication.

## Counterexample: archive a leaf, then free all its arrays

The first core/common gradient of a unit is itself a size-one carry block.
More generally, an odd append leaves the newest core/common arrays as current
size-one blocks. Archiving the leaf's bytes does not make these aliases dead.

In the production `Forest` schedule, append the float32 vector `[1]`. Its
carry block aliases that vector. Save its immutable bytes, then overwrite the
old array with zero as if the region had been freed and reused. Appending
`[2]` now yields `[2]`, whereas the untouched continuation yields `[3]`.
The archive still correctly contains `[1]`. Complete historical storage alone
therefore does not preserve continuation; the live alias cut is essential.

Retirement must be over allocation generations reachable from all current
operands, including derived views and every current/staged/predicted root.
It cannot be a list of leaf field names or a test of whether a numerical
value has already been copied. No failed or unsealed extent may be retired.

## What remains live: an exact coordinate law, not a memory lower

At pending count t, let C be the core slot count, K the readout feature count
and D the embedding width. Let e_a be the number of these events whose
complete window contains token a, counting an event once for that token;
let c_y be the number whose revealed target is y. Missing rows are absent.
The number of float32 coordinate occurrences in all carry blocks is exactly

    W_t = (C+K) popcount(t)
          + D sum_a popcount(e_a)
          + K sum_y popcount(c_y).

Each append contributes one block of size one to each relevant forest and
merges adjacent equal sizes. Its block sizes are the one-bits of its event
count, proving the formula. The nominal block payload is 4 W_t bytes. The
number of block arrays is

    A_t = 2 popcount(t) + sum_a popcount(e_a) + sum_y popcount(c_y).

Together with the three master and four prepared arrays, these give a
sufficient numerical operand enumeration; an outstanding forecast adds its
two arrays. The old leaf and previous basis field occurrences are excluded,
but any storage they share with those roots is still included by generation.
These are coordinate/array-occurrence laws, not actual reserved-memory laws:
padding, alias unions, zero-sized arrays, metadata, archives, workspaces,
failure pins and host allocations require their own complete accounting.
They are not minimality theorems for arbitrary programs or FP realizations.

Retiring historical workspaces cannot promise linear total verification.
With growing row support, W_t can grow with t. Even in a word-read oracle
model, a verifier that conclusively accepts exact equality to a sealed live
image under arbitrary one-word corruption must inspect every independently
mutable word: if one is unread, changing just it leaves the verifier's
observations unchanged and would receive the same false acceptance. Refusal
or `UNRESOLVED` remains possible without all reads. This lower applies only
to that exact-integrity decision class and observation interface; it is not
a universal FP, wall-time, PCIe-transfer or device-kernel lower. Grouping reads
does not violate it, and a different trusted observation contract would need
its own proof. No still-live word may be replaced by a previous host image
under the current contract.

## Ownership premises for an actual lowering

The constructive representation claim is conditional on all of the following.
The owner implementation and finite controls below address these premises;
they do not prove arbitrary Python code or grant a new completeness class.

- The image comes from this owner's freshly checked successful physical phase,
  retains all original word/shape/dtype/incidence/source data and provenance,
  and is admitted and sealed before any view is retired. A caller-supplied
  image or a mutable public dataclass is not an authority source.
- Images, indexes, dependencies, role leases and the live operand declaration
  occur in complete state. New storage/work is prepaid. Future diagnostic
  expansion or transfer is charged and may honestly be unresolved.
- The actual live generation graph is complete. Retirement invalidates old
  views before reuse, preserves all geometry/alias/retirement history and
  keeps current/staged/predicted roots and all failed/unsealed pins.
- The actual numerical executor, independently checked primitive outputs,
  native/AMP predicates, source/target boundary and fresh pre/post checks on
  every remaining live operand stay in force. An archive cannot attest to a
  live tensor. A failed archive/copy/retention/retirement operation cannot
  publish a successful learner or regain continuation authority.

Under those premises, induction combines the numerical continuation theorem
with an exact decoder for historical queries and the actual resource history.
No value usable by a legal future continuation is assumed away. This is a
physical representation question within R4's existing realization/ownership
semantics, not evidence that R4 needs a new semantic architecture action.
It gives no same-budget acceptance equivalence or installation authorization.

## Finite adversarial control

`scripts/audit_token_workspace_liveness.py` runs the existing production
numerical transitions on CPU arrays, with an independent exact primitive
oracle and the existing checker. After each observation the second arm
replaces all old leaf array/incidence fields and the old basis with objects
which refuse reads/conversion. Complete images contain only builtin tuples,
ints, strings and bytes; fresh diagnostic wrappers are reconstructed from
them. Current carry aliases stay live. Every subsequent emitted array is
compared bit for bit with the untouched arm, as are commits, forecasts,
per-label values, declared primitive extents and reconstructed states.

Cases exhaust all four-target binary histories at unit sizes 1, 2 and 4 over
the existing mixed, zero-embedding and zero-core models, which include tied
slots, shared PRODUCTs, a square and a repeated feature. Longer unit-eight
cases and original-record reverse/repeat profiles add carry/source controls.
The minimal result is `FP_TOKEN_WORKSPACE_LIVENESS_CPU.json`. The explicit
live-alias overwrite counterexample is retained alongside the passing tests.

The final control passes 152 paired histories, including two profiles,
640 observations and 348 commits. Its 1,780 paired numerical phases compare
209,048 output arrays/742,504 words and reconstruct all 640 pending states.
The exact oracle checks 367,502 floating primitive-word occurrences across
both arms. All 640 coordinate laws agree with event counts derived separately
from the original windows/targets. There are 832 current core/common alias
witnesses and zero accesses through the blocked historical fields. These are
finite numerical/value controls, not complete owned Runtime trajectories.

No corpus or CUDA context is opened. This passive control does not allocate/
reuse a device region, execute a complete Runtime retirement or test its
failure boundary. Those are the separate implementation obligations below.
The static-invariant and rational/relation branches remain closed.

## Complete owned representation

`TokenCudaPrefixContract.archive_workspaces` is exact-boolean and default off.
It requires the existing generation-reuse arena and shared complete retention
in both roles. Backend, primitive schedule, G/Gamma/U, numerical allowances,
source/persistence rules and installation authority do not change. This is
a physical storage lowering within the existing realization contract.

After a successful observation, `token_workspace_archive.prepare` proposes
private historical views for the seven numeric fields of every leaf and the
four numeric fields of the materialized basis. Each image contains its exact
shape/dtype/bytes, source capture-phase identity/index/field path, and original
allocation generation/region/view extent. A weak binding identifies the actual
owner without a reference cycle. Incidence arrays and causal metadata remain
original and freshly checked. Current masters, prepared operands, forecasts
and **every actual carry block** retain their real tensor objects.

The proposal is checked independently against the newly checked full raw state
and the original device geometry. An equal-valued replacement for a live root
is refused. Prior image bodies are saved before the producer runs and cannot
be rewritten by it. A further full decoded capture checks all current operands
and historical fields before publication. This adds one live-state capture
per successful observation; it is not the old raw-call schedule unchanged.

Images enter the complete owned phase frame, including source/geometry and
owner-binding facts in its execution plan. Actual frame encoding/admission
must fit the existing frame allowance. Runtime retains that frame, seals the
arena phase and accepts it before the proposal can become a continuation root.
No retirement happens inside the image producer. Snapshots expose only builtin
immutable image values, including the owner-binding relation, for every retained
private resident/proposal. They never expose a private image wrapper or a tensor.

The successful observation consumes its outstanding forecast: its entry is
removed from `predicted` only after acceptance. The complete forecast phase
remains retained. The next collector therefore follows every current, staged
and outstanding-forecast root and its aliases, while every failed
or unsealed generation remains pinned. It invalidates historical generations
before physical reuse and retains allocation/alias/retirement history. A leaf
field can become an image while its former allocation remains live through a
carry root. Fresh current-root checks continue to detect any changed word.

Complete historical diagnostics decode image words rather than dereferencing
a retired address. Every later numerical pre/post check still freshly reads
the actual live arrays. Work is prepaid by the existing complete phase tariff
plus `16 * phase_evidence_bytes + 1024 * (7 * update_unit + 4)` for image walks,
binding and additional capture. This is a declared primitive tariff, not a
Python heap or bit-time theorem. Exact image payloads fit the actual admitted
phase frames; shared pages/dependencies retain both-role leases. The enforced
whole-process host limit also covers Python objects and temporary encodings.
Exhaustion refuses rather than deleting images, skipping checks or raising caps.

Preparation/retention failure leaves the old learner and current authority
intact, retains the revealed target and all unsealed work, and closes further
execution. Typed invalid proposals retain a failed phase and their complete
proposal image. A partial retirement metadata failure is terminal even after
some historical generations have been invalidated. No such failure can regain
successful continuation authority.

## Complete CPU owner qualification

`scripts/audit_owned_token_workspaces.py` substitutes only physical device
binding, using actual Torch CPU tensors, the real generation arena and the
complete Runtime/bridge/retention/reporting paths. All 21 paired histories pass:
363 numerical phase bodies/15,064,144 bytes agree after excluding only the new
archive plan field, as do 136,391 checked primitive words, all learners/reports
and cumulative buddy allocations. Cases include all four-target binary words,
unit sizes 1/2/4/8, multiple commits, reverse/repeated original-record profiles
and one pair combining grouped reads, composed native bounds and owned facts.

Actual generation retirement and stale-view refusal pass. Old sealed records
remain unchanged; public snapshot replacement has no image authority. Zeroing
an actual live common carry still refuses the next phase. Unpaid work, forged
image words/geometry/owner, substituted live roots, preparation MemoryError,
retention refusal/MemoryError and partial-retirement MemoryError all preserve
the old learner and close continuation. Missing reuse/shared retention and a
non-boolean option refuse at registration. The old reuse regression and default
prefix-cost audit also pass.

The minimal `FP_OWNED_TOKEN_WORKSPACES_CPU.json` retains the counts. Peak live
buddy bytes in the unit-four and unit-eight examples fall 5,712 to 5,128 and
6,576 to 5,352. Aggregate raw calls fall 123,326 to 118,015 and raw bytes
2,328,076 to 2,228,500, while complete frame bytes rise 15,064,144 to 16,512,140.
These raw counters exclude initialization and grouped transfers. They are no
total-I/O, timing, fixed-budget dominance or actual-device claim.

## Fixed first CUDA comparison

`scripts/run_archived_workspaces_cuda_a1.py` is registered before its first
launch. It uses only the already declared first 1,024 training bytes and first
16 targets. Two fresh workers run in order `resident`, then `archived`, each
inside a preattached 240-second/16-GiB Windows job. Both keep the original
V=50,257, L=512, D=4, K=8, unit=512 resource fixture with 603,092 masters,
1-GiB device arena/reservation, 2-GiB reference payload, 64-MiB phase frame,
2^22 output-cell bound, 4,096 exact-cell bound, state tolerance 16 and
probability/division tolerance 10^-6. Both enable generation reuse, 64 MiB of
owned canonical images and 4 MiB of qualified token-base facts. Grouped reads
and composed native bounds stay off. Only workspace archival differs.

Both arms use the same lightweight phase hook to keep the first actual event
value view and its issued generation, with no inner arithmetic profiler. Both
must preserve 33 checked phases, all original contexts/targets, 16 pending
records, no optimizer commit and identical checked primitive/cumulative
allocation counts. Initialization is timed separately from ordinary calls.

After timing, the resident arm must still accept that view. The archived arm
must have retired its generation and refuse the old view; read-only test
instrumentation then observes that its actual bytes have been overwritten.
Those bytes never reenter a learner. The complete original event image must
remain unchanged. The archived arm then zeros an **actual live common carry**;
the next prediction must retain a failed phase with changed live words, the
original historical image, prior sealed record, old learner and cursor 16,
without a successful successor.

The exclusive `FP_ARCHIVED_WORKSPACES_CUDA_A1.json` records the clean committed
source, original worker identities, caps and device evidence. Commit before
launch. Never replay a terminal or partial journal, raise a failed cap or
replace a failed worker. Judge the one ordered pair's total ordinary-call time
and live-storage measurements at its original outcome. No full-unit benefit,
general speedup, affordable training or language score follows. Close this
finite qualification afterward; further work must target ordinary learning
cost on evidence, with Foundation/ERC and the relation/rational branch closed.

## Actual result and closure

Both original workers at `791368565b1d8c54498a119611c5df3c517987ef` pass on the
declared RTX 3090 under every registered cap. Each retains 33 successful phases,
4,541,709 checked primitive words, all original 16 contexts/targets, 16 pending
records and no optimizer commit. Cumulative buddy allocation is 36,772,296 bytes
in both arms. Native/current allocation counters remain `(1,1073741824,1)`;
actual/lifetime tensor and allocator reservation remain 1 GiB. The largest
used arena extent is 24,379,392 bytes and peak live buddy storage is 24,214,064
bytes in both arms. No measured peak-storage reduction occurs in this prefix.

| Original measurement | Resident history | Archived history |
| --- | ---: | ---: |
| Initialization seconds | 9.9378218 | 9.8883847 |
| All 32 ordinary calls, seconds | 61.6477362 | 61.8832904 |
| First eight targets, ordinary seconds | 29.5324685 | 29.4672818 |
| Last eight targets, ordinary seconds | 32.1152677 | 32.4160086 |
| Peak whole-job committed bytes | 3,328,253,952 | 3,449,225,216 |
| Peak paid reference bytes | 272,951,974 | 273,083,091 |

Ordinary time increases by 0.38210% in this single ordered pair. This is no
statistical slowdown claim; it supplies **no evidence of a speed benefit**.
Whole-job/reference peaks in the archived arm also include its extra fault,
so their differences are not isolated archival overhead measurements. The
post-worker live byte counts, 7,212,336 and 6,554,720, likewise follow different
numbers of collection attempts. They are not a paired terminal live-set claim.

The first event-value generation is 232 in both workers. It stays valid and
unchanged in the resident arm. In the archived arm it is retired, its old view
is refused, and direct test instrumentation confirms actual address overwrite.
The complete original event words still decode unchanged. Actual in-place
zeroing of a **live common carry** then causes the next prediction to refuse
with the existing changed-predecessor error. The 34th phase retains changed
carry words and the original historical leaf image; the earlier sealed record,
learner and cursor 16 remain, with no successor or new arena allocation.

The exclusive `FP_ARCHIVED_WORKSPACES_CUDA_A1.json` is terminal. Its original
process/device identities and per-call times remain auditable. This closes
the finite owner/device representation qualification; the option stays default
off. Complete historical values can survive actual retirement and overwrite
while live corruption remains detectable. That correctness result does not
establish affordable text learning. Later-prefix/full-unit benefit remains
unmeasured, and no long replay or storage-variant sweep follows from this pair.

The accumulated short comparisons distinguish algebraic/count progress from
measured affordability: native composition, grouped reads and workspace
archival all have preservation evidence, but none demonstrates a substantial
early-prefix time reduction. Qualified base-fact reuse did reduce that cost,
yet about 62 seconds for 16 targets remains. The next priority is the remaining
complete validation/retention cost and an evidence-based ordinary-text budget,
not another static/relation/storage special case. Strong trained baselines
remain required; this resource fixture supplies no language-quality result.
Foundation/ERC stay frozen.
