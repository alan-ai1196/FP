# Finite mantissas for a correlated positive frontier

Status: **PROVED, SCOPED NUMERICAL LAW; EXACT, BINARY64 AND ACTUAL AMP AUDITS**.
The fixed CUDA protocol below was committed before its sole execution,
which passes at7cb6259. This concerns a scalar decoder for the existing
[count state](COUNT_LEARNER_ENCODING.md), not a new native Program or a
complete Runtime/AMP bridge. Foundation and ERC-1 remain unchanged.

The [positive frontier decoder](POSITIVE_FRONTIER_DECODER.md) preserves
correlations with exact integers, whose bit length grows with history.
Normalizing each factor separately does not safely remove that cost:
small local entries may be the only globally compatible alternatives.
Per-entry integer exponents avoid this erasure and give a rounding bound
independent of the count magnitudes. Exponent/mantissa arithmetic is a
conventional representation; the result here is its explicit realization,
error argument and adversarial audit for this FP count decoder.

## 1. A single-forecast counterexample to local normalization

Pin z0=0 and take signed counts on edges(01,02,12) equal to(h,h,-h).
Each integer likelihood factor has entries1 and9^h. In world order
(z1,z2)=(00,01,10,11), the positive weights are(t,t,t,1), t=9^(2h).
For query(0,1), the exact probability of label0 is

`p0=(19*t+1)/(30*t+10)`, tending to19/30.

Now divide each edge table by its maximum before using finite arithmetic.
Its entries become1 and9^-h. Once the latter rounds to zero, the first
two edges require equality and the third requires inequality. No world
satisfies all three. The computed partition is zero despite strictly
positive exact mass and a nondegenerate forecast.

Even best correctly rounded scalar conversion fails at these first counts:

| Format, round to nearest with even ties | First h with rounded9^-h=0 |
|---|---:|
| binary16 |8|
| binary32 |48|
| binary64 |340|

The exact rational audit checks every preceding h and the first zero.
This does not require power-algorithm error or accumulated update drift.
It falsifies this local maximum-one normalization, not every possible shared
scale. It also does not falsify the existing [global world-score decoder](LIKELIHOOD_DECODE_ERROR.md):
subtracting the global maximum world score preserves at least one unit
world mass. Adding a positive base after losing this partition would change
the desired decoder, not prove it correct.

## 2. The declared finite decoder

The inputs and positive elimination order are those of the exact decoder.
The tape keeps all declared support edges, including those currently at
count zero. A positive cell is represented as

`x=m*9^e`, with `1<=m<9` and an exact nonnegative integer e.

Zero is represented only as(m,e)=(0,0). The integer likelihood9^d enters
as(1,d), with no floating exponentiation. Signed counts select the preferred
parity exactly as in the integer construction. The original counts, pending
event, cursor, optimizer clock and surrounding complete state remain.
Every decode starts again from those exact counts; rounded messages are
not used as the prior for a later label.

For a product, add exponents and multiply mantissas. Normalize by up to two
divisions by9, incrementing the exponent whenever the actual rounded
mantissa is at least9. Two passes cover half inputs that round up to9 and
produce81. Normalize zero's exponent back to0; otherwise a zero with a
large exponent could incorrectly suppress a positive addend.

For a sum, align to the larger exponent. Generate a fixed coefficient table
c0=1, c_(j+1)=RNE(c_j/9), for0<=j<15. If the exponent difference delta<16,
multiply the smaller mantissa by c_delta and add. If delta>=16, omit that
addend in this sum. Then normalize. This omission has a local relative
bound proved below; it neither zeros an input factor entry nor changes the
retained count coordinate. A later decode can use that coordinate again.

Two arithmetic modes are fixed:

- Binary64: actual binary64 multiplication, addition and division; every
  primitive is checked against exact rational round-to-nearest arithmetic.
- AMP: FP32 mantissa storage, alignment, sums and divisions; each wide
  product casts both input mantissas to FP16, multiplies in FP16, then casts
  its result to FP32. Actual GPU normalization predicates determine integer
  carries. Integer exponent metadata is on the host, which is explicitly
  part of this hybrid diagnostic. GPU values are not filled from an exact
  posterior, decoded probability or binary64 reference answer.

Stored positive mantissas stay in[1,9), half products are at most81, and the
smallest alignment coefficient is near9^-15, normal even in binary32.
Thus all nonzero arithmetic to which the relative-rounding bound is applied
is normal and finite. Unselected division results are also checked, though
they do not change the represented scalar.

The implementation declares exponent cap2^62-1. Before evaluating the tape
it refuses if SUM|d_e|+tape_nodes+4 exceeds this cap; sums and products also
guard their possible carries. Exponents are not free unbounded registers.
For total history H and this elimination tape they need O(log(1+H+n)) bits
(using m<=H after removing zero factors; retaining zero factors can instead
use the conservative O(log(1+H+m+n)) envelope). This concerns numerical
cells, not total native or physical evidence storage.

## 3. Local rounding law

Let u16=2^-11, u32=2^-24 and u64=2^-53. Relative roundoff is measured against
the exact operation on the *represented* inputs, not against already lost
world weights. Set epsilon=1/512 for AMP and epsilon=2^-46 for binary64.
Every wide SUM/PRODUCT has multiplicative error between1-epsilon and
1+epsilon. Zero is exact.

For an AMP product, its two half casts, half product and at most two single
normalizations give lower/upper factors

`(1 +/- u16)^3 * (1 +/- u32)^2`.

The cast of a half result back to single is exact. Binary64 has at most
three rounded operations. All these factors lie strictly within1+/-epsilon.

For an aligned sum with delta<16, the coefficient has delta division errors.
One alignment product, one addition and two possible normalizations give
at most delta+4<=19 factors1+/-u, with u=u32 or u64. Positivity bounds the
whole sum by the same envelope even when only one addend has alignment
error. These factors also lie strictly within1+/-epsilon.

If delta>=16 and the lower mantissa is positive, its exact contribution
relative to the higher one is less than9^(1-delta)<=9^-15. Keeping the
higher input is therefore at least1-9^-15 times the exact sum and at most
the exact sum. The kept mantissa is already normalized, so this branch's
selected arithmetic adds no rounding error. Zero cannot be the higher
input in this branch because its exponent is canonical0. Finally,
9^-15<2^-46<1/512. `bound_audit()` checks these inequalities exactly.

## 4. History-independent forecast error for a fixed tape

Assign an error budget b=0 to each exact input, including9=(1,1).
Set b(PRODUCT)=b_left+b_right+1 and b(SUM)=max(b_left,b_right)+1.
Induction using positivity gives, for every positive exact tape value v,

`(1-epsilon)^b * v <= decoded(v) <= (1+epsilon)^b * v`.

For this elimination tape, input factors and eliminated variables are
disjoint across messages multiplied together. Counting along an expanded
monomial gives at most m+(n-1-t) product gates from joins and n-1-t gates
from variable sums, where t<=2 query endpoints are retained. Each final
parity accumulator has at most two entries, and its noisy head adds one
product and one sum. Thus each mass head has

`B <= m+2*(n-1)+4`.

In particular B does not depend on the signed-count magnitudes. This bound
is for the declared elimination tape, not an arbitrary circuit with repeated
squaring or a discarded gradient/cache output.

Write U,V for the represented parity totals. Both approximate noisy heads
are positive: they compute9U+V and U+9V. Put R=(1+epsilon)/(1-epsilon).
Their ratio in either direction is at most9R^2. If A is the first head
and N is their rounded wide sum, exact rational inequalities give

`1 < (1-epsilon)*(1+1/(9R^2)) <= N/A`

and

`N/A <= (1+epsilon)*(1+9R^2) < 11`.

Canonical mantissas then imply an exponent difference between N and A of
0,1 or2. The final probability divides mantissas and multiplies by the
appropriate coefficient. Its coefficient uses at most two divisions, so
all final rounding contributes at most four factors1+/-u, again covered
by epsilon. Combining the head budget B, the total's one additional SUM
and the final division envelope yields

`R^(-(B+1)) <= p_computed/p_exact <= R^(B+1)`.

This is uniform over count magnitudes accepted by the exponent field. It
is neither exact equality nor a uniform0.001 error guarantee. The current
AMP envelope is deliberately conservative: B=191 gives factor2.117003
(rounded upward). A bridge needing a smaller certified tolerance must
derive a sharper bound, refine its arithmetic or return UNRESOLVED. The
same bound in binary64 is much tighter. Growing width still costs table
work; growing history still costs count/exponent bits and ingestion work.

## 5. Retained CPU evidence

Run `python -B experiments/joint_uncertainty/radix9_frontier.py`.
The [minimal report](../../evidence/minimal/FP_RADIX9_FRONTIER_EXACT.json)
keeps small output fractions, worst witnesses and aggregate checks:

| Fixed case | Forecasts | Largest exponent | Binary64 max absolute error | AMP machine max absolute error |
|---|---:|---:|---:|---:|
| Frustrated triangle, query01 |11|769|8.10e-17|6.17e-5|
| Same triangle, query12 |4|769|2.97e-17|6.60e-5|
| Same triangle, diagonal11 |4|769|8.89e-17|2.92e-5|
| Frustrated8-cycle, query02 |4|449|8.20e-16|2.23e-5|
| Frustrated64-cycle, query(0,16) |4|4,034|7.39e-16|6.06e-4|

The displayed errors are upward decimal bounds; exact output fractions and
reference comparisons are in the audit. All27 forecasts are within0.001.
Both cycle forecasts vary with count magnitude. The binary64 run checks
51,672 actual primitives; the AMP exact machine checks29,548 rounded scalar
results. An additional exhaustive triangle audit covers125 signed profiles
in{-2,-1,0,1,2}^3 and all nine ordered queries, including diagonals:1,125
forecasts and149,250 rounded scalar results. Its maximum absolute error is
53287/403701760, attained at counts(-2,1,1), query(1,2), computed546215/1048576
versus exact401/770. These finite tests do not replace the error proof.

## 6. Fixed actual CUDA protocol

Before its first GPU attempt, commit this proof, both scripts and the CPU
report. Run `python -B experiments/joint_uncertainty/run_radix9_frontier.py`.
The launcher binds the current clean source and committed reference report,
publishes the registration before starting the child, and never overwrites
an existing attempt. Its Windows job attaches before the child's first
instruction, with one active process,4 GiB process/job commit and240 seconds.
This bounds the child diagnostic; it is not an ERC manifest for a Runtime.

The fixed cases are:

- Triangle counts(h,h,-h), query01, h=0,1,7,8,16,47,48,64,339,340,384;
  queries12 and11 at h=0,1,48,384.
- Cycles n=8,64, all counts+h except edge(0,n-1) at-h, queries(0,n/4),
  h=0,1,8,64.
- All125 triangle count triples in{-2,-1,0,1,2}^3, all nine ordered queries.

Every actual floating operation result, cast, coefficient selection and
normalization selection must match its independently computed exact RNE
word. Final outputs must reproduce the already retained AMP-machine cases
and exhaustive witness, and agree with the independent integer decoder
within the registered0.001 test threshold. No posterior tensor is uploaded
to substitute for this execution. Record device/software identity, actual
process identity, completed job accounting and Torch memory peaks. Retain
failures and reader exceptions; no silent restart or retrospective threshold
change. No timing advantage or exclusive-device comparison is claimed.

The [terminal record](../../evidence/minimal/FP_RADIX9_FRONTIER_CUDA.json)
contains no weights, large table cache or full diagnostic transcript. At
this proof's initial commit the GPU outcome was pending; its completed
outcome is below. A passing diagnostic establishes this finite hybrid
decoder's arithmetic execution only. Full native operation
words, gradients, phase evidence, ownership, fresh persistence and install
reachability still require their own bridge before any Runtime substitution.

## 7. Completed actual RTX 3090 outcome

The sole registered child completes at source
`7cb6259f5132a018b67d4749d30245dcdd9ac1d0`, with clean execution dependencies
and the committed CPU reference. Device NVIDIA GeForce RTX3090, Torch
2.12.0+cu132, CUDA13.2. All27 fixed and1,125 exhaustive forecasts reproduce
the retained AMP-machine fractions and errors exactly. The5 fixed cases
check44,457 device words; the exhaustive triangle checks229,375, giving
273,832 actual floating-word checks in total. This includes178,798 rounded
scalar results and coefficient/normalization selections.

All1,152 forecasts meet the registered0.001 threshold. The largest error
is0.0006055355072021485 on the64-cycle; its largest exponent is4,034.
The exact-machine worst triangle witness also reproduces. No actual
arithmetic mismatch, timeout, job-limit termination or reader exception
occurs. Worker13036 exits0 after attachment before resume. Completed peak
process/job commit is2,231,971,840/2,233,196,544 bytes under4,294,967,296;
Torch allocated/reserved peaks are629,248/2,097,152 bytes. Host exponent
and independent exact-oracle work belong to the child diagnostic. The
launcher is outside that measured child scope. Raw accounting retains
total_processes=2 and limit_terminated_processes=0 under the one-active-
process cap; cumulative OS counts are not rewritten as a process inventory.

Only the9,958-byte terminal JSON is retained. The completed job is not a
model stream, complete native AMP bridge, timing comparison or total Runtime
resource claim. The theoretical factor2.117003 at B191 remains unchanged;
passing these cases does not strengthen it into a uniform0.001 theorem.

The [tolerance-enclosure continuation](RADIX9_ACCURACY_ENCLOSURE.md) now
certifies these27 retained GPU forecasts from the checked binary64 bound,
without replaying the diagnostic. It also supplies a256-cycle counterexample
to uniform0.001 AMP accuracy and handles large-count enclosures without
materializing huge likelihood integers. The original finite result stands.
