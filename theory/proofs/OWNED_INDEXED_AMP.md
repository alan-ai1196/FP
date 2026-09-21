# Owned indexed AMP execution and resident transport

Status: **SCOPED REFINEMENT ARGUMENT AND EXACT CPU SCHEDULE AUDIT;
SOURCE-BOUND ACTUAL CUDA AUDIT PENDING**.

This extends [owned indexed reference execution](OWNED_INDEXED_REFERENCE.md)
inside the same `ReferenceCompilerRuntime`. It implements a new declared
physical schedule for the same literal G, uniform Gamma, unit simplex U
and complete categorical domain. It does not introduce a native architecture
action, change Foundation R4/ERC-1, or claim class completeness or a resource
advantage. The older array-based CUDA machine keeps its own declaration.

## 1. Complete physical representation

`IndexedCudaPrefixContract(n=...)` selects the fixed
`owned-indexed-radix9-half-products-single-readout-v1` backend. Both reference
and CUDA registrations must describe the same indexed family and n. The
physical learner independently retains all signed counts, pending ordered
query/target, cursor and optimizer clock. At an observed boundary it also
retains three actual single-precision gradient words in the owned CUDA
arena. The physical prediction retains the complete predecessor, ordered
query and seven actual single-precision readout words. The original native
cache has its exact source/pair/parity point decoding, including orientation.

Counts encode the full parameter vector exactly; they are not copied from
a trained reference endpoint. Physical initialization derives zero counts
from the registered Gamma. Observation uses Runtime's actual target.
Commit independently performs the proved count rewrite of the native
unit simplex update, preserving the observed predecessor and clearing only
the successor's completed accumulator. Attachment changes only the ordinary
cursor, as in the reference path. It is not an approximate SGD update
followed by a reset to a reference posterior. Explicit native output still
requires K coordinates and its guarded output allowance.

The public API accepts neither physical endpoints nor numerical certificates.
The existing private CUDA owner retains the complete maps, arena, phases,
predictions and device binding. Its field set is unchanged. New resident
learner/cache types have fixed complete field sets. No tensor handle enters
a public snapshot; actual words, count metadata and owned leases do.

## 2. Fixed arithmetic and full-coordinate check

The positive table geometry has the same natural-order preflight as the
component proof. A static tape preserves every factor and required positive
SUM/PRODUCT. Syntax-proved radix powers shift a guarded integer exponent
and alias an immutable mantissa. Other products cast both mantissas to half,
multiply in half and widen the result to single. SUMs align using the fixed
16-entry reciprocal-power table, add in single and normalize twice in single.
The host uses freshly read actual device words for normalization decisions;
it never uploads a reference forecast or posterior.

For scalar batches the choices and power-table reads are aliases of existing
owned tensors. This differs from the earlier diagnostic's allocated `where`
and gather schedule. It preserves those selected numerical values, while
having its own explicit operation/output/metadata costs. No equality of
physical resource histories or old CUDA operation tapes is asserted.

All arithmetic uses `CudaArithmetic` with its current paid `CudaWorkspace`.
Every new result is freshly read through the owned host readout buffer and
compared with exact RNE on the actual operand words. Signed zero follows the
specified operation. Output stack copies are checked against every source
word. The complete raw operation tape and the positive execution plan are
retained in an indexed CUDA phase frame. The reference comparison cannot
feed any numerical answer into the physical successor.

The existing exact reference prediction supplies all seven target values;
no second binary64 target computation is needed in this owned scope. Count
equality proves zero parameter error and equality of both clocks and the
pending event. Comparing the three active gradient forms covers every
native accumulator coordinate; a diagonal checks exactly the forms that
occur but retains all three actual words. Source/pair/parity cache values
are exact, so the seven-value check covers every other native cache and
readout coordinate. Actual activation/normalizer caps and separate state
and probability tolerances are checked as well.

**Conditional phase refinement.** Under the fixed declarations and resource
guards, every accepted physical phase is the independently executed stated
AMP transition and lies within the registered complete native-coordinate
tolerances of the owned exact reference phase. Initialization and the
count/clock maps commute exactly. Prediction and observation use the
finite coordinate basis above. Induction over ordinary and profile phases
proves the continuous relation. A target swap cannot be repaired by reporting
a matching pending tag: the reference observed state and explicit target
come independently from the actual owned observation record.

This statement does not extend the owned reference decoder past its current
integer-height or table allowances. A numerical or resource refusal leaves
that continuation unresolved. The large-count binary64 component theorem
does not silently replace this Runtime's registered reference machine.

## 3. Predictable range and resource accounting

For every admitted categorical prediction, aligned parts are nonnegative
single values, and at least one has positive mantissa at the largest
exponent. RNE of their sum is at least either input, because the inputs are
representable and rounding is monotone. Therefore each rounded marginal
lies in [0,1], its product by eight lies in [0,8], and adding the exactly
representable base one gives a stored mass in [1,9]. The rounded normalizer
is at most 18. This supplies one full-domain mass box without enumerating
n^2 queries or K worlds. It binds the complete current count parameters
and categorical domain. It applies to the registered guarded schedule;
unfunded/invalid predictions stop before their target can be scored.

The bound is deliberately conservative: normalizer cap 10 is insufficient
for this particular box, even though the exact native normalizer is 10.
The present protocol registers cap 18 and activation cap 8. Failure of the
box is `UNRESOLVED`, not a claim that actual numerical outputs exceed 10.
No new static precision special case is needed.

Metadata planning, exact word checks, counted output cells and fixed evidence
frames are prepaid by the existing Runtime role routing. With P non-power
products and S additions on the positive tape, prediction executes exactly
`38 + 6P + 4S` output cells, including its seven-value stack. Observation
executes 13 cells including its three-value stack. Initialization, count
commit and clock attachment allocate no new floating cells. Their host
count/metadata and phase frames still have costs. A prediction's complete
plan is checked before entering the numerical arena.

All floating outputs use arena extents; aliases never create unregistered
device allocations. Every completed or failed output remains within the
same arena and phase history. Complete packed count/plan/evidence records
and readout buffers have actual Runtime leases. Whole process/job commitment
and device/tensor observations remain separate measured resources; the work
tariff and packed bytes do not stand for total RAM or elapsed bit complexity.

## 4. Fresh evidence and installation

Both persistence paths use their own actual pre-target forecasts, current
lineages and alpha debits. CUDA scores normalize the two stored positive
masses exactly, following the existing proper stored-mass scoring contract;
they do not reuse reference gains or treat independently rounded probability
words as an exactly normalized distribution. The full-domain mass box
supports the predictable gain bound. The external stochastic-law declaration
remains an assumption, not a conclusion from a finite test tape.

The existing [prospective installation argument](OWNED_PROSPECTIVE_SELECTION.md)
already makes historical class selection an optional additional assertion.
Registration no longer requires a nonempty search declaration for CUDA
installation. An actual owned candidate, both fresh current crossings,
paired starting states and all transport checks remain mandatory. This
removes an extra implementation gate; it adds no proposal mechanism or
training-maximum claim. Native-class search for the indexed family remains
unimplemented and has no borrowed `CERTIFIED_COMPLETE`.

The existing same-device identity transport checks the exact current count
records and any resident gradient extents, then preserves every learner,
CUDA phase, arena byte, prefix map and device coordinate. Fallible
preparation precedes the joint root/lease publication. The old base remains
as a shadow; previous evidence is invalidated without alpha refund or
rebasing. Empty-strategy finite CUDA closure uses the same complete frame
and does not establish class optimality. These integration paths require
the pending actual audit below before being reported as executed results.

## 5. Evidence and registered actual tests

[The CPU schedule audit](../../evidence/minimal/FP_INDEXED_AMP_SCHEDULE.json)
passes 270 predictions and 540 observations, from 27 n3 profiles on all
nine ordered queries and nine n5 profiles on three queries. Its scalar
RNE simulation contains 279 half outputs. Seven prediction and three
gradient words match the prior independently implemented component, and
full native caches/gradients are checked. Maximum gradient error is exactly
49/188743680. The independently bound target forgery is refused, and the
insufficient whole-domain range cap returns `UNRESOLVED`.

`scripts/run_indexed_amp_audit.py --attempt 1` registers seven fresh owned
Runtime workers: n5 ordinary/profile execution with real half products;
n256 construction/profile/continuation with world builders disabled;
fresh paired persistence, installation and continued learning; finite empty
CUDA strategy closure; unfunded numerical entry; a substituted target; and
failure on the second candidate's CUDA commit. Each worker is attached
before resume to a 4-GiB job with a 900-second deadline. Source and complete
inputs must be committed first. Every attempt has its own retained report;
failed attempts are never overwritten or silently restarted.

**No new actual GPU outcome is claimed at this source.** All earlier model
and standalone component jobs remain terminal. This is not a new complete
CPU/CUDA release or a model-science improvement.
