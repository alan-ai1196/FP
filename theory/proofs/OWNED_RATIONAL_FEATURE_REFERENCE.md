# Owned rational-feature reference execution and its exact-gradient boundary

Status (2026-09-25): **REGISTERED EXACT REFERENCE PATH; COMPLETE NATIVE,
OWNERSHIP AND SAME-PATH FRESHNESS AUDITS PASS**. This implements the different
G/Gamma from [the rational-feature scale law](RATIONAL_FEATURE_SCALE.md) inside
the existing `ReferenceCompilerRuntime`. It preserves every rate/parity part
needed by the fixed-slot gradients. It adds no root owner field, optimizer
action or constructor decision class. Its distinct AMP path remains unregistered.

The implementation also exposes an exact precision limit: bounded native
range can coexist with a fixed gradient whose reduced denominator is almost
twice as wide as the current posterior/readout integers. One executed case
passes prediction and returns UNRESOLVED on observation at the declared
32768-bit reference limit. This is not a Foundation failure or a reason to
delete a fixed gradient.

## 1. Complete native identity and phases

`JointRelation` now has the explicit optional rational field `feature_scale`.
None denotes the original unit-slot/integer-incidence program; its descriptor
and indexed program identity remain unchanged. An explicit Fraction C denotes
the rational-feature graph and initializer, and requires C*min(eta)>=1.
This field distinguishes complete G/Gamma. It is not an adaptive scale change
on an existing learner or an untyped architecture callback.

The rational descriptor includes a distinct schema tag, n, the ordered rates,
the ordered positive prior and C. It has 2J fixed slots followed by K selected
world slots. Native node/term readers, exact Gamma, selected U block, source
rules and full materialization all use that layout. The same numerical C as
the old S still gives a different native program because the fixed slots and
incidences differ. Changing C alone can preserve the literal graph topology
while changing Gamma and its full learner identity.

The complete native source interface remains all n^2 ordered pairs through
two categorical roles. There is no label, posterior or inferred rate input.
The same count state keeps every pair coordinate, diagonal balance, optimizer
step count T, ordinary cursor and pending event. Observation advances its
cursor and records the actual query/target; commit advances T and the signed
count and clears the unit. Profile attachment preserves T. Counts decode
the selected weights using the original likelihood scale S, while fixed slots
decode their exact rational Gamma. Nothing is converted into a floating master
parameter vector.

`JointState` stores 4J exact gradient forms for an observed rational-feature
unit. The slot decoder returns the first 2J directly and selects the correct
rate/parity class for each world slot from the remaining 2J. It retains fixed
zeros and their derivatives. `JointEvaluation` keeps all head coordinates,
the complete predecessor/query, and the unnormalized rate/parity parts and Z
needed for the new fixed gradients. Its full native materialization checks
the same source, PRODUCT, feature and head values as an independent literal
Program. Point/full materializations keep explicit output and bit allowances.

The registered machine IDs are

    packed-indexed-rational-feature-joint-noise-reference-v1
    indexed-joint-noise-rational-features-full-rate-parts-reference-v1

The immutable run manifest binds them with the exact program/initializer and
ordinary learner. The original integer-copy IDs remain for `feature_scale=None`.

## 2. Retain and price the complete integer construction

Write C=c/d in reduced positive rational form. Let a_j=S*eta_j,
b_j=S*(1-eta_j), D=d*S. The nonnegative integer feature coefficients are

    k_(j,match)=c*b_j-d*S,      k_(j,other)=c*a_j-d*S.

After the existing positive per-rate elimination gives R_j0,R_j1,

    N_y = sum_j [k_(j,match)*R_jy+k_(j,other)*R_j,1-y],
    Z = sum_j,y R_jy,
    sum_y N_y = (C-2)*D*Z,
    native excess_y = N_y/(D*Z),        normalizer = C.          (1)

All rates reuse the same table region and two local parity roots. Three
global roots hold N0,N1,Z. Rational-feature execution additionally retains
2J rate/parity roots in the **same paid extent**, outside the region cleared
before the next rate. Every numeric table/root read and write uses that
extent; it is not a second unpriced numeric tape.

For join/live/work/step/integer allowance (j,l,w,Q,I), the old layout remains
(l+5)*cell bytes. The rational-feature layout is

    (l+5+2J)*cell,
    cell=ceil(min(I,b_Q)/8),
    b_T=n+bit_length(P)+(T+1)*ceil(log2 S)
        +bit_length(c)+bit_length(d).                          (2)

P is the common prior denominator. The extra terms cover raw static
coefficient products and denominators even when cancellation makes their
final integer numerator much smaller. Positive table and aggregate values
are bounded by c*P*2^(n-1)*S^(T+1), so (2) is conservative. The reference
excess denominators D*Z also fit that envelope. Exact gradient fractions
have a separate check and can require more bits, as section 5 shows.

The same geometry, power, aggregate and step preflight runs before any
workspace write. The scalar-readout guard remains explicit beneath the
minimum of the reference and decoder integer allowances. New root copies,
metadata and static coefficient work are included in the construction tariff
and actual packed extents. Positive arithmetic counts retain their existing
table/power/aggregate scope; the tariff is a declared scalar/index/byte cost,
not a theorem about bigint wall time or total process memory.

Runtime allocates and pins the extent before execution, debits construction
before entry and then pays the exact readout step. The root's existing
retained-information owner holds it across predictions, profiles and failures.
Borrowed views cannot unpin or resize it. Retained Evaluation/plan/gradient
metadata is packed and owned through the ordinary existing record path.
No helper receives an ingress, ledger, persistence or publication capability.

## 3. Input binding must include the new parts

`prepare_bound` derives the ordered query from complete actual source values
and checks the model against the complete count predecessor. The independent
plan reader reconstructs the entire plan from those inputs, order, allowance
and exact byte extent. Its closed comparison now includes all retained parts.

There is a directed adversary on an actual reachable cut. At n3, C=10, after
two diagonal label0 observations, query01 has

    R=((648,648),(450,450)),       Z=2196.

Replacing the parts by ((653,643),(442,458)) leaves Z, both aggregate excess
integers, and every native head/mass/probability coordinate unchanged. But
the first fixed gradient for target0 changes from 0 to -1/2196. The altered
plan is refused. Its altered parts are not asserted to be reachable; the
attack is a forged decoder output at an actual reachable predecessor.

Other plan attacks remove a part, substitute a boolean, rescale every root,
change C in the predecessor, shorten the extent or change arithmetic bits.
All refuse. Actual Runtime refuses a candidate with the old feature mode,
another C or reordered rates under the current construction contract.
The actual initial diagonal label0 keeps derivative 1/20 at a fixed zero
coefficient; deleting that gradient coordinate fails the complete state schema.

The original joint AMP code is explicitly limited to the unit-feature model.
Its raw/resident states and predictions, range object and CUDA contract reject
rational features before device creation. The six audited entrypoints import
no Torch. A passive scalar theorem cannot assign the old physical layout a
new meaning. The new exact Reference path also retains the existing refusals
for an unregistered binary64 path, caller-supplied state/plan and unsupported
literal translation into a different machine.

## 4. Actual ordinary, profile and fresh-reference evidence

Run `python -X utf8 -B scripts/audit_rational_feature_runtime.py --write`.
The [7,499-byte artifact](../../evidence/minimal/FP_RATIONAL_FEATURE_REFERENCE_RUNTIME.json)
records:

- Seven complete independent literal G/Gamma/U comparisons, including
  n2..4 and noninteger C=5/2. Across 366 reachable cuts and 2,844 ordered
  queries, all exact parts/readouts and 22,632 packed-root reads agree;
  external canary bytes remain unchanged.
- All 516 two-event histories for n2/n3 default C=10, n2 three-rate C=8
  and n2 noninteger C=5/2: 1,032 owned native triples. Every cache, full
  observed gradient, committed state and ordinary target match literal
  evaluation/reverse differentiation/U.
- A C=8 profile checks four actual replay triples and fourteen ordinary
  lineage triples. Final ordinary cursor8 coexists with optimizer steps8/10.
  Candidate construction accepts no supplied theta or plan.
- An n64 three-rate C=8 root represents 3*2^63 native hypotheses. Eight
  cyclic/band/diagonal events match a separate unsigned-history recurrence,
  all 12 gradient forms and all count successors. Literal expansion is
  prohibited. It seals SEALED_REFERENCE_STREAM with zero constructor
  decisions, 39,330 actual integer-table bytes and 3,291,472 peak packed bytes.
  These are not whole-host or actual GPU measurements.
- An S with 203 bits, native C=4, completes eight additional owned native
  triples. No likelihood denominator cap is inferred from native range.
- Unfunded integer and readout kernels are never entered. A canceled signed
  count still retains T=2 and refuses a one-step decoder allowance. A physical
  post-construction fault preserves prior learners/history and the pinned
  22,194-byte scratch. A second-lineage commit failure publishes neither
  successor while retaining both observed states and the actual target.
- Two independent Runtime roots, indexed and literal, compare actual fresh
  reference statistics after candidate admission at 16, through twenty future
  events. Crossing occurs at 20 with wealth 266119/65536. Retirement leaves
  alpha 1/4 spent. A foreign-root candidate and supplied install flags cannot
  create transport or an installation certificate.

The fresh result assumes the declared external stochastic stream law; the
deterministic audit does not establish that law or population model quality.
Reference-only evidence is not paired AMP evidence. No constructor class is
searched or certified. Full indexed release remains a separate open claim.

## 5. An exact materialized-gradient precision lower

Use odd q>=3, rates (1/4,(q+1)/(4q)), equal prior, n2 and C=4. Put a=3q,
b=a-1. After T>=1 diagonal label0 observations, rate weights are proportional
to U=a^T and V=b^T. For the next diagonal label0, the low-rate fixed matching
gradient is

    g = U/[4(U+V)] - q*U/[a^(T+1)+b^(T+1)].                    (3)

Its reduced denominator is exactly

    4*(a^T+b^T)*(a^(T+1)+b^(T+1)).                            (4)

To prove no cancellation, consecutive a,b are coprime and
gcd(a^T+b^T,a^(T+1)+b^(T+1))=1: subtracting a times the first sum leaves
-b^T. Both sums are coprime to a and q, and both are odd since q is odd.
The combined numerator U*(a^(T+1)+b^(T+1)-4q*(a^T+b^T)) is odd and coprime
to both sums. Thus (4) is reduced. Its bit length is

    (2T+1)*log2(3q) + O(1),                                  (5)

while posterior and prediction integer widths are T*log2(3q)+O(log q).
The O(1) in (5) is uniform since each sum is between a^t and 2a^t. This is
an exact output-bit lower for the declared materialized Fraction gradient,
not a memory lower for every possible symbolic complete-state encoding.

With q=2^200+1, Runtime commits 81 observations under the 32768-bit reference
allowance. The following prediction passes with at most 16,532-bit native
prediction integers and normalizer4. Its next label0 produces a gradient
denominator with 32,863 bits. Observation correctly returns UNRESOLVED,
retains the actual target and prediction, and publishes no new learner state
or partial native observation trace. The independent literal observer also
refuses at 32768. A separate 131072-bit literal audit confirms the exact
gradient and cache; it does not increase the owned run's allowance. The
literal arithmetic's intermediate guards can be more conservative than the
indexed calculation, so no equality of their minimal operation budgets is
claimed.

This is a genuine limit for the registered exact materialized gradient at
this contract. It leaves room for a separately proved symbolic gradient
representation and paid point reads. It does not justify dropping a fixed
derivative, relaxing tolerances, changing the native U, or declaring a
universal impossibility from an implementation refusal.

## 6. Regression and next physical boundary

The unchanged-mode partition, full Reference Runtime and scalar AMP suites
pass on the extended source:

    python -X utf8 -B scripts/audit_joint_partition_storage.py
    python -X utf8 -B scripts/audit_joint_runtime.py
    python -X utf8 -B scripts/audit_joint_amp.py

No historical artifact is regenerated. The unknown-noise model reader still
checks its source-bound declaration and independently reconstructs all 4,000
retained words. Its read-only declaration check is now separate from the
unchanged-production **launch** guard, so future production work does not
require rerunning historical jobs to read them. The altered-word and foreign-
source tests still refuse. No launch guard or original outcome is weakened.

The next physical implementation must own this rational-feature layout,
construct both excess and rate/parity parts from actual physical state,
execute the complete new gradient schedule, independently bind all RNE
operations and complete native state, and preserve the existing paid extent,
failure lifetime, lineage and fresh installation relation. The old AMP
layout cannot supply those facts. Foundation, ERC-1 and all existing
`CERTIFIED_COMPLETE` decision classes are unchanged.
