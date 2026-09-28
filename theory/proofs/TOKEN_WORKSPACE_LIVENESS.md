# Numerical continuation needs live operands and complete history in different roles

Status: **NUMERICAL CONTINUATION THEOREM; PASSIVE CPU CONTROL; OWNER LOWERING OPEN**.
This is ordinary-token research under frozen Foundation/ERC. It introduces
no new semantic architecture action, G/Gamma/U, source interface or precision
rule. No Runtime retirement implementation, CUDA authority, performance
claim or `CERTIFIED_COMPLETE` follows from this proof alone.

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

The scope is deliberate. The current Runtime's `Resident.raw`, `tensors`,
predecessor equality checks, phase retention and collector still expect the
old representation. Passing a marker-bearing object to them would refuse.
The theorem is not a drop-in bypass of any of those checks. It identifies the
numerical read boundary an owned representation may implement and then audit.

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
The current implementation has not discharged them for archived workspaces.

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

No corpus or CUDA context is opened. This control does not allocate/reuse a
device region, execute a complete Runtime retirement or test its failure
boundary. The next implementation must bind and seal the representation in
the real owner before any new actual-device qualification is justified.
The static-invariant and rational/relation branches remain closed.
