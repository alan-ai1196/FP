# A finite basis for every native reference coordinate

Status: **PROVED, CONDITIONAL COMPONENT BRIDGE; EXACT/BINARY64 AND
ACTUAL RTX3090 AUDITS PASS**.

The [indexed literal representation](INDEXED_RELATION_REFERENCE.md) extends
to a complete numerical phase relation without checking K=2^(n-1) entries.
Parameters stay encoded by exact counts. An actual ordered query determines
the source, PRODUCT and indicator cache coordinates. Seven actual readout
words and three pending-gradient words then cover every remaining native
reference coordinate. Each check has an explicit finite decision class.

This closes a numerical representation obligation before Runtime integration.
It does not supply owned admission, source acquisition, a complete Compiler
Omega quotient, fresh evidence or installation authority. The actual target
must come from an independent observation record; a numerical state cannot
certify its own reported label. A counterexample below exposed precisely
that circularity in the draft checker.

## 1. Fixed semantic model and physical representation

Use exactly the indexed theorem's literal G, uniform Gamma, feature slot0=1,
selected slots1..K, unit rate, one-event units, no grid and categorical pair
domain. No new semantic action or native constructor is added. Keep the
complete count coordinates C=(n,d,alpha,c,s), including profile multiplicity,
pending query/label, cursor and optimizer-step clock. The data/provenance and
resource state surrounding this component are not removed.

In the proposed physical representation, parameters are **encoded**, not a
K-entry floating master vector. Their semantic decoder is exactly

`theta_0=1`, `theta_(k+1)=W(k)/Z`,

with the positive count weights W and normalizer Z from the indexed proof.
Thus equal complete count coordinates imply equality of every parameter,
without materializing those numbers. A later explicit parameter read still
needs its paid exact or numerical decoder and can exhaust its allowance.
The experiment never uploads an exact reference successor as GPU weights.

A committed physical state consists of C with empty alpha and a zero native
gradient. After observation it retains C with its actual pending event and
three binary32 words `(g_fixed,g_match,g_other)`. For native slot k+1 the
gradient reader uses g_match iff the original world's parity matches that
pending event's target; otherwise it uses g_other. Slot0 uses g_fixed. The
native world order and all slot ties remain those of the literal code.

A prediction retains its complete predecessor C, actual ordered query and
seven binary32 words: two excesses, two masses, normalizer and two
probabilities. All other native cache values have the exact indexed 0/1
decoder. This includes inactive nodes and all source/PRODUCT coordinates;
query(i,j) and(j,i) are not identified merely because their forecasts agree.
There are no delayed coordinates in this family.

These are concrete representation choices, not a minimum-storage theorem.
The three raw gradient outputs and every produced numerical operation remain
checked even where an exact algebraic dependence might allow another encoding.

## 2. Complete-coordinate bridge theorem

Assume the exact reference and physical encodings have the same complete C,
the same fixed G/Gamma/U/source declarations, and the actual ordered query q.
After prediction, let an **independently supplied actual target** y be fixed.
The observed physical alpha must equal(q,y), its cursor must advance by one,
and its d and step clock must stay equal to the reference predecessor's.

By the count theorem, the exact reference pending gradient has the forms

`G_fixed=1/M_y-1/5`, `G_match=4/5-8/M_y`, `G_other=4/5`,

where M_y is the exact native mass. For a nonloop query both world classes
occur, even if one has extremely small posterior mass. For a diagonal only
the matching class occurs when y=0, and only the other class when y=1. The
fixed-feature derivative always remains an actual native coordinate.

It follows that the maximum native gradient error is exactly the maximum
over these occurring scalar classes. Every parameter error is zero under
the encoded-parameter decoder. Unit count, clocks, pending tag and empty
delayed state agree by the discrete checks. Every non-head cache error is
zero, so native activation/mass error is the maximum over the two excesses
and two masses; normalizer and probability errors are their explicit scalar
errors. This proves a complete native reference-coordinate relation from a
finite basis, with no K-entry scan. It covers the reference learner and
`Evaluation` fields, not arbitrary physical or Compiler coordinates.

The class predicates and their input bindings are part of the theorem.
Checking the three gradient numbers while allowing a label or slot-map
substitution is not a complete-state check.

## 3. Tight scalar intervals certify the whole basis

The existing [checked binary64 enclosure](RADIX9_ACCURACY_ENCLOSURE.md)
supplies p0 in[l,u], with1/10<=l<=u<=9/10. Its input is the actual complete
count state and query, not a displayed prediction alone. It uses the fixed
positive tape budget B and an actual primitive-checked binary64 result;
constructing a passive interval object does not establish that execution.

The exact native intervals follow without large likelihood integers:

| Coordinates | Exact target interval |
|---|---|
|excess0|[10l-1,10u-1]|
|excess1|[9-10u,9-10l]|
|mass0|[10l,10u]|
|mass1|[10(1-u),10(1-l)]|
|normalizer|[10,10]|
|probability0/1|[l,u] / [1-u,1-l]|

If the target mass is in[a,b], a>=1, the gradient intervals are

`G_fixed in [1/b-1/5, 1/a-1/5]`,

`G_match in [4/5-8/a, 4/5-8/b]`, `G_other=4/5`.

These follow from monotonicity, with no Lipschitz overestimate. For an actual
finite word v and target interval[L,U], its absolute error lies between

`max(L-v,v-U,0)` and `max(abs(v-L),abs(v-U))`.

Taking maxima over the occurring basis classes gives lower and upper bounds
on the full-coordinate errors. The prototype declares state/native/normalizer
tolerance1/100 and probability tolerance1/1000. It reports within all complete
reference tolerances only when every relevant upper bound passes; a lower
bound exceeding its tolerance proves outside; all other cases are UNRESOLVED.
The interval carries its complete predecessor and query binding. No uniform
history-tolerance assertion or constructor-completeness certificate follows.

**A forecast-only relation is insufficient.** At n2 after four equality
labels, perturb the positive readout's p0 downward by1/2000, form its native
excesses/masses, and evaluate the pending rare-label gradient with actual
RNE32 scalar rules. The resulting forecast error is below0.001 and the
activation/mass error below0.01, but the matching-world gradient error is

`54706105/1377828864 > 0.0397`.

The complete checker rejects it. This is an adversarial nearby readout,
not an observed failure of the main kernel or a deliberately weakened model
baseline. It shows why a valid scalar probability certificate cannot simply
be promoted to a complete-state certificate.

## 4. Independently bind the actual target

At the uniform prior, a nonloop query has both masses5. Labels0 and1 therefore
produce identical triples of stored gradient forms: fixed0, matching about
-4/5, other about4/5. Their **slot assignments** differ because the parity
match predicate uses the label.

Take an actual label0 observation and change only the physical pending label
to1. All three gradient words, the preceding forecast, counts and clocks
remain the same. A checker that computes its expected event from the
physical pending tag accepts the forgery: it checks a self-consistent label1
event instead of the event that occurred. Committing produces the opposite
count update, and the next same-pair forecast changes from41/50 to9/50.
The corresponding learned-slot gradient values are swapped, differing by
about1.6, despite the unchanged three-word array.

The draft checker made this circular assumption. The final API requires an
independent `target` argument and checks the full expected observation
transition before numerical intervals. The adversarial audit reproduces the
circular acceptance by intentionally passing the self-reported target, then
proves that the actual target0 is refused. Runtime must obtain this argument
from its owned post-prediction observation record. Passing the physical tag
again would recreate the same invalid proof. Nothing about numeric accuracy
or a content hash supplies that missing information authority.

## 5. Declared mixed-precision phase and exact commit rewrite

The implementation preflights a complete, explicit natural elimination order
and positive table geometry, then runs the existing exact-power radix9
lowering. Proved powers alias mantissas and add guarded host exponents;
remaining products execute actual half arithmetic; mantissas, SUMs,
alignments and divisions use binary32. Counts and carries remain exact
bounded host integers, with actual device normalization predicates checked.

For native readout, align the two resulting partition mantissas to their
common maximum exponent. The existing cutoff16 alignment has its explicit
zero coefficient beyond the cutoff. Divide each aligned positive mass by
their binary32 sum to obtain two numerical marginals. Compute both excesses
as8 times their own marginal, both masses as1 plus excess, their actual sum
and both actual divisions. No subtraction/clipping manufactures the smaller
marginal. Native excesses stay in[0,8] and masses stay positive. These seven
outputs are the complete readout words checked above.

After the separately supplied target, select its actual stored mass and
compute the three gradient forms using explicit binary32 operations and
rounded constants. The gradient belongs to that preceding prediction and
predecessor. A stale prediction execution cannot supply another state's
mass. This schedule has its own operations; it is not claimed to reproduce
the older literal AMP schedule's operation words.

Commit uses the proved exact unit-simplex identity

`w'_k = w_k*(1-G_k+G_fixed) = w_k*(1+8*I_k)/M_y`.

Consequently a signed count increment implements the same exact semantic U.
The physical parameter decoder remains exactly the new posterior, rather
than accumulating rounded gradient errors in a floating master vector. The
pending gradient is still present and must satisfy its phase relation; a
failed bridge cannot be ignored merely because the count rewrite exists.
Commit clears the gradient/tag and increments the step clock. Profile
attachment changes only the ordinary cursor at an empty-accumulator boundary.
Other rates, units or priors cannot inherit this rewrite.

All counters have a fixed envelope2^62-1, with an additional exponent/tape
preflight. A failed commit leaves the immutable observed predecessor, label
and gradient available. The synthetic clock-boundary audit predicts and
observes from an endpoint at the step cap, then refuses the next commit
without deleting that observation. It does not replay2^62 events.

## 6. Costs, audits and the integration boundary

The implementation retains all D=n(n-1)/2 counts, the complete schema and
query/pending/clocks. It has no initial K-entry Program, prior, master or
gradient array. Exact parameter decoding and full explicit output retain
their separate allowances and can return UNRESOLVED. Pointwise comparison
of the finite numeric basis does not authorize a free full-state read.

Table preflight uses the indexed decoder's declared join/live/operation
metrics. In addition, the prototype caps batch size512 and retained logical
tape cells262144, and charges the table operation allowance across the batch.
The exact tape-size formula is input factor cells plus positive table
operations plus6; all checks precede numerical execution. The existing
scalar forecast calculation is still executed in the reused decoder even
though the complete readout uses its partitions; its work is counted.
Metadata, C validation, powers, bit arithmetic, audit/evidence and all
physical process costs remain additional. No optimality or whole-memory
advantage is claimed.

The exact audit uses the independent literal native learner, including its
ambient reverse derivative and explicit normalized commit. At n3 it covers
all125 signed triangle profiles, all9 ordered queries and both labels; at
n5 it covers81 signed branching profiles, five queries and both labels.
There are1530 distinct pre-target predictions and3060 complete observed/
committed pairs. Preparing the controls executes666 exact native units.
The same prediction is reused across the two possible label branches.

Across the small, sequential and large paths, the CPU audit checks170562 rounded scalar
results and736038 actual binary64 primitives. The largest small native
gradient error is2859/3449815040; the larger n256 prefix still passes its
declared full-state tolerance through the per-phase interval check. The
eleven malformed phase/word cases, retained pending clock overflow and
three pre-numerical resource failures remain explicit in the report.

A nine-event profile/continuation and a100-event late-birth reversal add109
sequential component events with full native comparisons. The former ends
at cursor23/step9 after attachment to20; the latter returns exactly to the
uniform prior at cursor107/step100.

With the literal builder disabled, n256 executes four component events and
a profile attachment, ending at cursor21/step4. Its original parameter map
is the four weights(81,81,1,81)/(61K), repeated over the free coordinates.
Selected parameter/gradient values agree with independent closed formulas,
and both full-state/cache output requests refuse their exponential extents.
Two256-cycle inputs at heights16/10^12 additionally check both pending labels
using checked binary64 and an independent positive cycle-tail enclosure.
The latter are synthetic reachable phase inputs, not executed trillion-event
histories. No cycle-size resource or precision contract is extended.

The minimal [CPU report](../../evidence/minimal/FP_INDEXED_PHASE_BRIDGE.json)
is produced by `experiments/joint_uncertainty/indexed_phase_bridge.py`.
The one registered actual GPU diagnostic now reproduces all words and
complete basis decisions under its4-GiB/600-second enforced Windows job.
Its source was committed before launch; the completed process binding is
retained below. No old GPU diagnostic or model stream was restarted.

The production Runtime still expects literal Program/prior/slot tuples,
complete native arrays and its registered phase/evidence formats. This new
component is not inserted through those APIs as an apparent old backend.
Owned indexed admission and representation identity, actual information
acquisition, charged complete phases, fresh persistence and reachable
installation remain required. The finite coordinate theorem supplies a way
to check those new phases without an exponential native-array scan; it does
not grant the missing ownership or continuity itself.

## 7. Actual RTX3090 phase audit (2026-09-21)

Source `b0b1f3b95f38528bf4d60ea9046cb6a4224739ee` executes exactly once through
`run_indexed_phase_bridge.py`. The
[17,168-byte GPU report](../../evidence/minimal/FP_INDEXED_PHASE_BRIDGE_CUDA.json)
is **COMPLETE_EXECUTION**. Torch2.12.0+cu132, CUDA13.2 and the actual RTX3090
execute293,008 checked device words. Every non-device-count field of the
component reports equals the committed CPU audit, including the numerical
error bounds, native comparisons, retained failures and both adversaries.
The adversarial controls themselves use the declared CPU exact audit; they
are not reported as failures of the main GPU kernel.

| Executed component group | Checked device words | Rounded scalar results | Checked binary64 primitives |
|---|---:|---:|---:|
| n3, 125 profiles, 9 queries, both labels |144000|88875|298125|
| n5, 81 profiles, 5 queries, both labels |92664|50139|307881|
| Nine-event profile/continuation |1052|626|2193|
| 100-event late-birth reversal |9800|6200|14982|
| Four-event n256 prefix |28764|17964|33417|
| Two n256 correlated inputs, both labels |16728|6758|79440|
| Total |293008|170562|736038|

The actual paths contain1,645 distinct pre-target predictions and3,177
observed component states. Of those observations,3,169 also have an
independent full literal native observation/commit comparison; the eight
large states instead use the proved finite basis and independent formulas
or cycle enclosures. The largest retained n256 prefix gradient-error upper
bound is below0.003259, with probability-error upper bound below0.000242276.
All tested live component phases satisfy the registered tolerances. This
is a finite execution result, not a uniform guarantee for all histories.

The worker PID2712, creation134344290691241388, exits0. It is attached to
the enforcing job before resume; no timeout or limit termination occurs.
Peak process/job commit are2,088,697,856/2,089,934,848 bytes, below4 GiB.
Torch peak allocated/reserved bytes are675,840/2,097,152. The raw worker
report is12,513 bytes; the final evidence additionally retains registration
and the completed job. These are observed resource values for this audit,
not an optimized Runtime cost or a comparative resource advantage.

This diagnostic is terminal. The subsequent
[owned indexed reference](OWNED_INDEXED_REFERENCE.md) now admits the exact
indexed G/Gamma/U through `ReferenceCompilerRuntime` and preserves actual
source/target provenance, complete reference phases, profiles, resource
roles, failures and fresh reference persistence. It passes exhaustive small
native comparisons and an actual n256 reference prefix. This component's
physical state and operation words still need their own owned Runtime
path, complete phase evidence, fresh paired persistence and reachable
installation. The original CUDA evidence remains bound to its original
source. These results do not reopen the frozen static resource program or
authorize another cycle-size study.
