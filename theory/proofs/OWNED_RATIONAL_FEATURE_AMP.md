# Owned rational-feature AMP refinement

Status (2026-09-25): **EXACT CPU PASS; A1 ACTUAL PROFILE AND PAIRED INSTALL
JOBS PASS; A1 STOPS AT n64 RUN-SEALING MISMATCH**. The missing closed cache
registration is now repaired and CPU checked. The repaired actual closure
and remaining cases are still unverified.

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
    prepaid-rational-feature-parts-coefficients-and-complete-rne-basis-v1

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
require device evidence. **A1 in section6 now supplies its declared paired
crossing/install and post-install continuation; complete failure lifetime
and the remaining cases still need evidence.**
The old 17-case joint GPU gate and four model tapes establish none of those
new facts; their historical outcomes remain terminal.

## 5. Exact CPU evidence and remaining physical gate

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
retained. A2 has no actual result at its registration commit.
