# Owned rational-feature AMP refinement

Status (2026-09-26): **ALL 21 ORIGINAL CASES HAVE A SUCCESSFUL EXECUTION
ACROSS FOUR TERMINAL ATTEMPTS; THE THREE EARLIER FAILURES REMAIN RETAINED**.
A4 completes the profile reader and legacy regression without a production
change. Section 10 fixes the source-by-source scope. This is the stopping
point for the rational-feature branch, not a single-source full release or
a language-prediction result.

This implements the fixed physical schedule from
[RATIONAL_FEATURE_SCALE.md](RATIONAL_FEATURE_SCALE.md) for the native program
registered by [OWNED_RATIONAL_FEATURE_REFERENCE.md](OWNED_RATIONAL_FEATURE_REFERENCE.md).
It preserves the same G/Gamma/U as that exact Reference path. It does not
transport the old integer-copy learner into a different native program.

## 1. Closed registration and complete physical coordinates

The existing `JointCudaPrefixContract` selects its implementation from the
complete immutable native descriptor. `feature_scale=None` still selects
the original joint AMP module, with unchanged IDs and word schedule. An
explicit rational-feature descriptor selects `rational_feature_amp.py` and
requires an integer C in [3,2^24]. Noninteger C, including exact-reference
C=5/2, returns UNRESOLVED for this physical schedule. This limitation does
not change the mathematical program or the exact Reference registration.

The new fixed IDs are:

    owned-indexed-rational-features-full-rate-parts-amp-v1
    rational-features-half-excess-single-coefficients-and-full-gradient-v1
    prepaid-rational-feature-parts-and-gcd-reduced-complete-native-relation-v2

The work ID above is the current verifier tariff. A1/A2 used the original
`prepaid-rational-feature-parts-coefficients-and-complete-rne-basis-v1`.
Section 8 changes only the exact relation solver and its separate charge;
the physical backend and forward IDs, primitives and native G/Gamma/U stay fixed.

The existing optional evidence-codec surcharge still applies. Changing the
descriptor while retaining the original physical IDs is refused. Each module
has distinct closed raw and resident state classes. The original module's
state, prediction and range constructors continue to refuse rational features.
There is no callable backend supplied by the user, new constructor class,
optimizer action or Runtime/prefix/arena owner field.

The physical learner retains the entire exact count encoding, including G,
ordered rate/prior bank, C, diagonal evidence, T, ordinary cursor and pending
ordered query/target. Gamma and selected parameters decode exactly from it.
An observed unit additionally retains **all 4J binary32 gradient words**.
The first 2J words represent every fixed coordinate, including fixed zeros;
the last 2J represent selected matching/other gradient classes. On a diagonal
query only one selected class per rate has native slots, but both stored
classes still undergo exact RNE conformance.

A physical prediction retains the complete predecessor/query, all canonical
integer rate/parity parts R and Z, and a resident tensor with **7+2J words**.
The first seven are the two excesses, two masses, normalizer and probabilities.
The remaining 2J are actual RNE32 ingresses of the rational feature
coefficients. The complete non-head native cache decodes from these words
and the actual categorical query. Returning exact coefficients in that cache
would incorrectly omit a physical rounding error. Sources and PRODUCTS decode
as exact zeros and ones. Neither rare components nor fixed gradients are
removed when a physical coefficient or fraction rounds to zero.

## 2. Construct from the actual physical path and check independently

The existing private CUDA executor uses the physical path's own complete
count predecessor and actual source row. The paid integer workspace constructs
all R_jy, Z and excess integers N_y from those inputs. It receives no reference
partition, trained parameter, normalized posterior or reference gradient.
The Reference and physical paths reuse the same root-lifetime pinned extent
serially, with separate construction charges.

Prediction follows the proved half/single excess schedule. It then executes
one single ingress for each rational feature coefficient and copies all
7+2J final words into the retained resident tensor. Observation uses that
prediction's **actual resident target mass** and its retained canonical R/Z:

    fixed_(j,match) = u_j/C - v_j,target/M_target,
    fixed_(j,other) = u_j/C - v_j,other/M_target,
    selected_(j,m)  = (C-2)/C - gamma_(j,m)/M_target.

The three per-rate fractions u_j,v_j0,v_j1 are each computed by a separate
single mantissa ingress/division/common-power multiplication, with the
registered zero and subnormal rules. The shared Z mantissa and target-mass
reciprocal are actual primitive outputs. Selected gradients execute their
own negative-coefficient ingresses. No native gradient is supplied by the
Reference checker.

Every primitive and output copy is read from the owned arena and compared
with exact RNE. After the kernel, the owner reconstructs the full integer
plan from independently retained actual inputs, including R, Z, query, order,
precision and exact extent. A separate scalar replay compares every returned
word and ordered operation record, including signed zeros and closed types.
The actual raw prediction must match its retained phase again before observe.
Changing R while preserving every head therefore cannot silently change the
fixed gradient. Constant rescaling of all roots also fails canonical input
reconstruction even though normalized ratios would agree.

The native relation separately compares the complete exact model/counts/
clocks/pending state, every fixed and active selected gradient coordinate,
all feature and head activations, masses, normalizer and stored-mass sum.
It checks both rounded probabilities and proper stored-mass probabilities.
The latter feed the existing physical freshness process. Exact R and Z must
agree with the independently executed reference cache; matching current
heads alone is insufficient.

This is the existing fixed trusted-kernel and serialized public-API boundary.
It does not sandbox arbitrary trusted-code replacement or concurrent process
memory mutation. The readout/gradient helpers grant no ledger, ingress,
persistence, signer or publication capability.

## 3. Exact output tariff and uniform bounds

Let k be the number of positive excess integers (one or two). Prediction
emits exactly

    21 + 4k + 4J

scalar outputs, counting the final copy. The added 4J comprises 2J coefficient
ingresses and 2J copied coefficient words. There are at most two half outputs.

Let z be the number of zero numerators among the J row sums and 2J parity
parts. Observation emits exactly

    6 + 29J - 3z.

Each zero numerator uses one zero ingress in place of four fraction outputs.
Actual positive-prior likelihood execution has positive row sums, but the
formula also covers the separately audited scalar boundary with zero rows.
Initialization, commit and attachment have no floating outputs; their exact
state transitions, metadata and records remain paid.

For Q the decoder's step allowance, let

    b_Q = n + bit_length(P) + (Q+1)*ceil(log2 S)
          + bit_length(C.numerator) + bit_length(C.denominator).

The physical forward tariff is

    2*decoder.construction_work(model,budget)
      + 1024*(b_Q+4J+1) + 128*(n+1)*output_cap.

Existing phase, native relation, packed frame, arena, readout and codec charges
are additional. All R roots occupy the same paid integer extent established
by the Reference refinement. Retained copies of integer parts in the phase,
prediction and plan use the existing packed record path; they are not free
table storage. This is a declared scalar/index/byte tariff, not bigint time,
whole-process memory or a minimal complexity theorem. Actual GPU execution
requires its separate physical host/device admission.

The scalar error law already proved in RATIONAL_FEATURE_SCALE.md applies
unchanged to these primitive equations. It covers all fixed and selected
gradients, native masses and proper/rounded probabilities, conditional on
exact parts, primitive conformance and admitted resources. Feature-cache
error adds at most (C-2)*2^-24+2^-150. Complete native activation error is the
maximum of this bound and the head bound, not their sum. The original
state/probability tolerances remain 1/100 and 1/1000 in the declared C=10,
C=8, C=4 and C=3 CPU comparisons.

For every admitted categorical forecast, nonnegative rounded part/shared-sum
ratios lie in [0,1]. C-2 and C-1 are exactly representable integers, so monotone
RNE places feature coefficients and excesses in [0,C-2], masses in [1,C-1],
and both the actual stored-mass sum and rounded normalizer at most 2(C-1).
The existing whole-domain range object binds this box to the complete theta
and categorical domain. It is independent of the next query or target.
Range validity does not promise that every precision check resolves.

## 4. Failure, profiles and installation obligations

The shared private executor and owner preserve the existing order: debit and
allocate, construct, execute, independently check, retain, then publish all
learners together. Any failed phase retains its actual work, parts, target and
predecessor under the same rules. No partial multi-lineage successor is
published. Profiles use the same native count transition and retain T across
ordinary clock attachment. The exact-reference precision obstruction at
q=2^200+1 remains a legal UNRESOLVED result; a small physical rounding error
cannot bypass a failed declared Reference observation.

The existing installation transport dispatches by the contract's closed
native representation and validates the complete current resident class,
raw state and every initialized tensor extent. The native descriptor/Gamma
and the actual count/gradient state are preserved by the same resident
identity transport. No new owner state is introduced. These physical claims
require device evidence. **A1 in section6 supplies its declared paired
crossing/install and post-install continuation; A2–A4 in sections7–10 supply
the remaining closure, precision, binding and failure-lifetime evidence.**
The old 17-case joint GPU gate and four model tapes establish none of those
new facts; their historical outcomes remain terminal.

## 5. Exact CPU evidence

Run `python -X utf8 -B scripts/audit_rational_feature_amp.py --write`.
The [8,792-byte artifact](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CPU.json)
records:

- 396 reachable count cuts, 2,964 complete ordered queries and 5,928 target
  alternatives under the declared small exhaustive class. The complete scalar
  comparisons cover 550,524 words including copies and 5,868 half outputs.
  Independent unsigned counts/literal world sums determine every rate/parity
  part. All primitives and returned coordinates agree with the separately
  written passive theorem schedule. Cases include C=10/S=20, C=8/S=120, C=3
  and C=4 with a 203-bit likelihood denominator.
- 248 full literal native continuation triples check every cache coordinate,
  parameter, fixed and selected gradient, commit and profile clock. Three
  80-event traces finish at cursor 78/T80; the wide-denominator trace finishes
  at cursor 6/T8. They do not claim actual device execution.
- The reachable equal-head/different-fixed-gradient witness is rejected by
  plan reconstruction, final prediction conformance, the native cache relation
  and observation replay. Every one of 11 retained readout/coefficient words,
  eight gradient words, 26 prediction operations and 56 observation operations
  is changed individually and refused. Missing/mistyped coordinates, wrong
  targets and incomplete/extra/mistyped traces also refuse.
- Output, step and insufficient 1060-bit precision refusals pass. A separate
  4096-bit decoder beneath a 32768-bit Reference contract preserves the same
  primitive words; the two resource allowances need not be equal.
- 108 synthetic scalar arrays, explicitly not asserted to be reachable count
  cuts, test zero rows, 198 zero parity parts and exponents up to 2000. Their
  additional 18,216 words satisfy both the exact schedule and the uniform error
  bounds. The output formula includes these zero cases.
- Closed contract/owner routing is inspected without constructing a device.
  Old graph or backend identities cannot adopt the new layout. Noninteger
  and oversized C refuse before device creation. A fixed zero retains its
  nonzero derivative. The S120 two-event cut in the different C=8 graph has
  native error 8950209/16471556096, within the original 1/100 tolerance; the
  historical old-graph refusal is unchanged.

No Torch import or device execution is part of this CPU audit. The unchanged-
mode complete AMP CPU suite passes after the shared routing changes. The
Reference input/plan adversaries also pass, with the old-contract attack now
explicitly attempting to reuse old physical IDs for the new descriptor. No
historical evidence artifact is regenerated.

The [21-case fresh-job protocol](../../experiments/joint_uncertainty/RATIONAL_FEATURE_AMP_CUDA_PROTOCOL.md)
and `scripts/audit_rational_feature_cuda.py` are now registered before execution
against production anchor e98065e. Each job has a fixed4-GiB host cap and
900-second deadline, with original tolerances and no within-attempt retries.
The gate includes actual paired installation, complete coefficient/part/word
binding, n64 closure, reversal and the exact-gradient precision refusal.
Every result must be retained. The partial actual outcomes in section6 are
separate from, and are not consequences of, the CPU pass.

Foundation, ERC-1 and all existing `CERTIFIED_COMPLETE` decision classes are
unchanged. A registered physical implementation is not a constructor optimum
or a full indexed release.

## 6. A1 actual outcomes and a missing complete-cache consumer

The [original A1 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A1.json)
is terminal at source e16c97619a34773a03d4c5aea05d519ea2ac8af3. Two jobs pass:

- Profiles: 58 checked phases,18 independent predictions,1,452 operation
  words and36 half outputs; cursor8 coexists with steps8/10. Every phase has
  a full literal native comparison. Peak host commitment2,229,424,128 bytes.
- Fresh install: 170 checked phases,56 independent predictions,4,592 operation
  words and112 half outputs. Admission at16, paired install at20, continued
  execution to36, alpha1/2 spent. Resident objects, arena, stream, reference
  states and phases are unchanged across the actual installation. Peak host
  commitment2,230,788,096 bytes.

Together these are 228 checked phases,74 predictions,6,044 operation words,
148 half outputs and7,450 outputs including copies. They establish these two
declared executions at that source, not the remainder of the gate or a
population-quality claim.

The third job, n64 closure, exits1 during finite-run sealing. The actual
traceback identifies `prediction_diagnostics`: its closed cache-type list
includes IndexedEvaluation and JointEvaluation but omits the new physical
DecodedPrediction. It consequently tries to read a nonexistent dense `values`
array. The job has no memory/time termination (peak2,233,233,408 bytes under
4 GiB). No independently checked phase totals from that failed job are retained,
so it is unscored. The remaining eighteen cases do not run.

This is an implementation mismatch in a complete-state consumer, not a
Foundation counterexample or numerical failure. A standalone CPU reproduction
raises the same AttributeError without Torch. The repair adds the exact new
decoded type to the existing closed activation-basis registration; it does
not add a permissive callback, pretend the basis is a dense native array,
change any numerical path or alter a resource bound.

The [focused CPU audit](../../evidence/minimal/FP_RATIONAL_FEATURE_RUN_DIAGNOSTICS.json)
compares twelve complete basis reports with full materializations, including
the original unit-feature path. n64 materialization is prohibited while its
complete basis report is checked. With q=2^200+1, the physical report correctly
has minimum nonzero activation1 while the exact Reference reports1/q; the
rounded coefficient zero cannot be silently replaced by exact Gamma.
Failed and empty prediction records remain excluded. This passive audit
does not seal a Runtime or prove repaired actual device closure.

A separate continuation attempt must fix its source before running the
failed closure and the eighteen unexecuted cases. A1 is never overwritten
or relabeled as a complete gate. The profile/install evidence remains bound
to its original source; only the closed run-report dispatch changes in the
repair, while physical phases, resources, freshness and transport are intact.

The subsequent A2 registration anchors production at dcdd3e9 and runs exactly
original cases3..21 with unchanged caps/tolerances. The runner checks the
terminal A1 evidence and that run_state.py is the only changed production
file. The two passing A1 jobs are not rerun, and their source attribution is
retained. A2 had no actual result at its registration commit; its subsequent
terminal outcome follows.

## 7. A2: actual closure passes; an arithmetic completeness expectation fails

The original [A2 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A2.json)
records execution at f298eab, under the unchanged 4-GiB/900-second limits:

- n64 C8 passes 25 phases, eight independently reconstructed predictions,
  all 12 gradient forms and `SEALED_CUDA_STREAM`, with zero constructor
  decisions. It represents K=27,670,116,110,564,327,424 hypotheses without
  expansion. Table bytes are 1,865,070; packed peak is 18,610,671.
- C8/S120 passes ten phases and three predictions at the original tolerances.
  Its declared two-event native error is exactly 8950209/16471556096.
- The C4, 203-bit-denominator case passes 25 phases/eight predictions. The
  actual coefficient 1/q rounds to zero while exact Gamma remains retained.

These three jobs total 60 phases, 19 predictions, 1,822 primitive words,
38 half outputs and 2,249 outputs including copies. Peak whole-job commitment
is 2,235,342,848 bytes. No memory/time termination occurs in any A2 job.

The precision-refusal job then returns UNRESOLVED at observation
`joint-event:41`, before its expected T=81 obstruction. Its journal reports
an integer-operation preflight refusal; it retains no detailed independent
phase summary for the failed job, so that job is unscored. The last fifteen
cases never run. **The preregistered claim that this verifier first refuses
at T=81 is falsified.** A2's source, status and original expectation remain.

An exact CPU reproduction locates the refusal in selecting the largest
gradient error, at fixed coordinate 2. The native gradient denominator has
16,734 bits; both error denominators have 16,760 bits. Raw comparison would
construct a 33,492-bit product, exceeding 32,768, even though the common
denominator cancels. The reduced products need only 16,732 bits. The error
is at most 699051/140737488355328 on the 2^-48 upper grid, far below 1/100.
This is an expensive exact verifier, not failed physical accuracy or a
counterexample to the materialized-gradient lower bound.

## 8. Paid GCD reduction: exact value/order, with a distinct resource promise

**Lemma (signed comparison).** For canonical x=a/b, y=c/d with positive
denominators, let g=gcd(b,d) and h=gcd(|a|,|c|), taking h=1 if both are zero.
The sign of x-y equals the order of the signed integers

    (a/h)*(d/g), (c/h)*(b/g).

Both ordinary cross products have been divided by the same positive factor
gh. GCD remainders and exact quotients never exceed the input integer widths.
Guard the original operands and each remaining product before evaluating it.
Success proves the order and retains the complete original operands. It does
**not** prove that an unreduced future cross multiplication fits. The old
`compare_exact` deliberately promises the latter as well, so it is unchanged.

**Lemma (canonical addition).** With g=gcd(b,d), set

    p=a*(d/g), r=c*(b/g), s=p+r, t=gcd(s,g).
    x+y = (s/t) / ((b/g)*(d/t)).

Write b=g*b', d=g*d', where gcd(b',d')=1. Coprimality of each canonical
input implies gcd(s,b')=gcd(s,d')=1. All final cancellation is consequently
gcd(s,g)=t; the displayed result is already canonical, including a zero sum.
Guard p and r, then the signed sum s, then the reduced denominator product.
No oversized b*d intermediate is required. The result is exact, with no
state quotient, dropped coordinate or semantic action.

The exact decision class is the success domain of these specified guarded
operations under a positive bit cap B. If L denotes integer bit length,
comparison checks both reduced product preflights max(L(u)+L(v),2)<=B.
Addition checks those of p,r and the final denominator; its integer sum
preflight is max(L(p),L(r),1)+2<=B. Original operand and final result guards
also apply. A refusal is UNRESOLVED, not impossibility for another solver.
For example, a zero sum of opposite large integers can still fail the
conservative numerator preflight. A canonical output wider than B, however,
cannot be returned by any materialized exact-Fraction implementation at B.
These claims do not cover arbitrary symbolic result encodings.

The new `_ReducedCheck` is used only by this rational-feature AMP relation.
It overrides comparison and addition, retaining all other shape, sign,
normalization, complete-gradient and source checks. Multiplication, native
Reference arithmetic, scalar RNE and the original unit-feature/binary64
relations stay unchanged. A comparison-only repair would fail next at T=81
prediction: adding its masses naively exceeds the cap although their sum is 4.
Both lemmas are therefore needed by the existing complete relation.

Comparison is charged 64 and addition 96 guarded integer/GCD/quotient/scalar
primitives. Comparison has two guarded operations, five guard calls and two
explicit GCDs; addition has four, ten and two, respectively. The tariffs also
cover input validation, Fraction construction, quotients, signs and scalar
control. They do not bound bigint bit-time or Python heap usage. With charges
4 for `exact` and 24 for the unchanged multiplication, a complete prediction
uses at most 592J+4504 relation arithmetic primitives and a pending state at
most 640J+72. The registered owner now prepays

    2048*(n*(n-1)/2 + 2n + 8J + 32)

for either complete relation, also covering the existing closed description,
coordinate and count validation. The old unit-feature tariff remains 512
times its same dimension. The changed work ID prevents inheriting the old
cheaper registration; bit, range, error, time and memory caps do not increase.

The [2,614-byte exact audit](../../evidence/minimal/FP_REDUCED_EXACT_RELATIONS.json)
checks 7,569 signed rational pairs at six caps for each operation: 90,828
calls, including honest refusals, all successful results exact. It checks
strict inputs, zero/coprime/overflow cases, primitive calls and closed owner
tariff dispatch. An ordered CPU continuation passes all 82 predictions and
81 observations/commits at the original 32,768 bits; the next Reference
gradient correctly refuses at its irreducible 32,863-bit denominator.
Maximum priced relation arithmetic is 5,688 against 108,544 prepaid units.
The largest accepted gradient error is at most 2796203/140737488355328.
This passive exact/RNE result does not establish actual CUDA failure lifetime.

The complete legacy unit-feature AMP and rational-feature AMP CPU gates also
pass on this implementation, as do the original exact-numerics and owned
binary64 Runtime audits. Their original retained artifacts are not rewritten.

At95ba561, a separately preregistered continuation was required to test the
new solver and fifteen unexecuted cases. The subsequent outcomes follow.
All five earlier passes retain their sources; no single-source complete
21-case gate or full release is claimed.

## 9. A3: physical precision boundary and adversaries pass; separate reader funding

The [original A3 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A3.json)
is terminal at 862e91c. Fourteen jobs pass. Their independently summarized
blocks total 566 phases, 189 predictions, 12,090 primitive words, 378 half
outputs and 15,039 outputs including copies. All 566 phases have full literal
native comparisons. These totals exclude unreported fault-preparation phases
and the failed job. Peak whole-job commitment is 2,250,600,448 bytes; no job
has a memory/time termination.

The precision case now checks 245 phases/82 predictions at the original
32,768 bits, commits 81 observations and preserves the final actual physical
prediction. The next exact Reference gradient needs 32,863 denominator bits,
so observation is UNRESOLVED **before physical observation entry**. The actual
target 0 remains retained, with zero published advances. The largest frame
is 40,626 bytes under the unchanged 65,536-byte allowance. This establishes
the predicted materialized-gradient boundary on the owned device path;
A2's earlier verifier refusal remains a separate, unchanged result.

The reversal job checks 314 phases/105 predictions. After a temporarily zero
physical excess, 52 opposite labels restore the exact half forecast at T=104;
the final target remains unrevealed. Output funding, second-lineage commit
failure, altered prediction/coefficient/gradient/operation words, stale
output extents, wrong target, root rescaling, equal-head rate-part forgery
and changed retained parts all refuse as declared. The workspace job checks
seven phases and six prepaid integer visits before its injected post-write
failure; the paid table remains owned and pinned, with no publication.

The fifteenth job, profile-refusal, fails in the independent full-state
reader. A prediction allowance Q=1 permits a forecast from T=1 and its
commit to T=2, then correctly refuses the next forecast. The old audit tries
to materialize the T=2 committed state using that same Q=1 allowance.
Its passive decoder correctly refuses the unfunded read. The original
traceback, failed status and absence of independently summarized phase totals
are retained. The final legacy-unit job never runs.

**A valid committed state need not be materializable under the allowance
that authorized its preceding prediction.** This is not permission to read
it for free or extend Runtime execution. The independent small literal audit
now explicitly uses max(Q,T) for materialization, within its separate
131,072-bit audit and the same whole-process cap/deadline. It reports both
step allowances. The live runtime still uses Q=1, and no native operation,
budget, profile, storage, solver or physical schedule changes.

The [564-byte CPU witness](../../evidence/minimal/FP_RATIONAL_FEATURE_READER_BUDGET.json)
exhausts four two-target histories. Eight complete deployed/failed-profile
states equal independent literal native execution when the passive reader
has Q=2; all eight Q=1 reads refuse. Both actual replay events remain, no
newborn is attached, and every subsequent live prediction still returns
UNRESOLVED. This exact Reference audit supplies no new device authority.

A4 was then preregistered for only original cases20/21, under unchanged production
95ba561. Its change is the passive reader allowance, explicitly recorded
before execution. The nineteen prior passing cases are not rerun or
reattributed. After these final checks, reassess ordinary next-token science
instead of extending this relation-task branch merely to add more cases.

## 10. A4 completion and the research stopping point

The [original A4 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A4.json)
records two passes at05a4c80. Production remains95ba561. The profile-refusal
case independently checks15 complete phases/four predictions/328 primitive
words, retains two replay events and publishes no newborn. It explicitly
reports live predictionQ=1 and passive materializationQ=2. The separate new
unit-feature regression checks13 phases/four predictions/156 primitive words.
Neither job hits its unchanged4-GiB/900-second limit; peak commitment is
2,229,022,720 bytes. No job remains live.

| Attempt/source | Successful original cases | Retained unexpected failure |
|---|---|---|
| A1 / e16c976 | 1–2: profiles and paired install | 3: missing complete-cache diagnostic type |
| A2 / f298eab | 3–5: n64 closure, C8/S120, wide denominator | 6: verifier comparison exceeds its bit cap atT41 |
| A3 / 862e91c | 6–19: precision, reversal, binding/resource failures | 20: independent reader lacks a fundedT2 materialization |
| A4 / 05a4c80 | 20–21: profile refusal and legacy regression | None |

The original21-case list has exactly one successful execution per case.
The three failed jobs retain their original status/source/traceback and
remain unscored. The19 earlier passes were not repeated in A4. Across all
attempts, no timeout or memory-limit termination occurs; maximum whole-job
commitment is2,250,600,448 bytes. This accounting does not merge the revisions
into one tested source or certify an unrestricted indexed Compiler.

Successfully summarized rational-feature blocks total **869 phases, 286
independent unsigned-history/RNE predictions, 20,284 primitive words, 572
half outputs and25,142 outputs including copies**. Of these,844 phases have
complete literal native comparisons; the remaining25 are the n64 unsigned
width-two audit without world expansion. Fault-preparation phases lacking
retained detailed totals and failed jobs are excluded. The separate legacy
regression adds13 phases,156 primitive words, eight half outputs and204 total
outputs; it is not counted as rational-feature evidence.

The branch has answered its concrete questions: native range need not track
the likelihood denominator; complete fixed-gradient precision still has an
exact output lower; a paid verifier can avoid redundant denominator work;
the owned physical path reaches that boundary and preserves the declared
bindings, freshness/install and failure behaviors in their executed scopes.
The evidence gives no reason to add further relation variants by default.
The next priority is the [ordinary next-token study](../../experiments/next_token/RESEARCH_ENTRY.md),
with its own native representation, information contract, competitive
baselines and source-specific bridge. Foundation and ERC-1 stay unchanged.
