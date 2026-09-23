# Exponent histograms decode the native count learner without join tables

Status: **PROVED, SCOPED; EXACT NATIVE/RNE AND ACTUAL RTX3090 ARITHMETIC PASS;
OWNED CPU AND ACTUAL RUNTIME COMPONENT GATE PASS**.
This is another execution of the existing
[complete count representation](COUNT_LEARNER_ENCODING.md), not a new
learner, sufficient-state quotient or semantic architecture action. The
implementation in `experiments/joint_uncertainty/count_histogram.py` has no
Runtime or certificate authority. Foundation R4 and ERC-1 are unchanged.
The separate [owned realization](OWNED_HISTOGRAM_DECODER.md) now implements
paid packed traversal and complete native continuations; all17 actual
Runtime CUDA jobs pass independently of the arithmetic-only A1 below.

The result exchanges exponential assignment visits for a small positive
polynomial and a uniform mixed-precision error bound. It does not remove
the [exponential exact-decoding obstruction](POSITIVE_COUNT_PARTITION.md),
claim polynomial work in n, or change an elimination-order decision class.

## 1. A positive polynomial from actual native counts

Use the fair-prior, noise1/10, one-event unit-rate relation learner, n>=2,
K=2^(n-1), anchor z0=0 and the full signed committed counts d. Put

    H = sum_e |d_e|,
    E_d(z) = sum_e |d_e| * 1[parity_e(z) = 1[d_e<0]].

The zero-count summands contribute zero. The exponent differs from
`sum_e d_e*1[z_i=z_j]` by the common constant `sum_{d_e<0}|d_e|`.
Thus the posterior is exactly proportional to9^E_d(z), with0<=E_d(z)<=H.
For the actual ordered query(i,j), define

    h_y(k) = #{z:z0=0, E_d(z)=k, z_i XOR z_j=y},
    P_y(t) = sum_{k=0}^H h_y(k)*t^k,   Z_y=P_y(9).

These are nonnegative integer coefficients, summing across both polynomials
to K. If L is the number of nonzero coefficients,

    L <= min(K, 2(H+1)).

The native marginal is q_y=Z_y/(Z_0+Z_1), excess8q_y, mass1+8q_y,
normalizer10 and probability(1+8q_y)/10. The count theorem still decodes
every parameter, source/pair/parity cache entry, clock and pending gradient:

    G_fixed = 1/(1+8q_y)-1/5,
    G_matching = 4/5-8/(1+8q_y),   G_other=4/5.

The histograms do not replace d, the actual query/pending target, cursor,
optimizer clock, profile, raw data or provenance. Initialization and every
commit/attachment retain their existing complete native meanings. A physical
implementation must derive its own histogram from its actual predecessor;
the exact reference result is not an input to that numerical execution.

There is already a small counterexample to retaining only the current
histogram. Actual two-label0 histories on edges(01,02) and(01,12), at n3,
give the same two histograms for query(0,1). Both current forecasts are41/50.
For the next query(0,2), their forecasts are41/50 and189/250. Their complete
parameter vectors also differ. Positive grouping justifies execution of
this query; it grants no information erasure across future continuations.

## 2. Construction and the work/space exchange

A binary reflected Gray traversal enumerates all K anchored worlds while
flipping one vertex per visit. Start at all-zero bits with energy
`sum_{d_e>0}d_e`. Flipping v reverses the agreement indicator of precisely
its incident active edges. Add or subtract each corresponding |d_e| and
toggle the query parity iff v is exactly one query endpoint. Induction
maintains the exact energy and parity. Increment that histogram coefficient.

This takes K visits and at most(n-1)(K-1) incident updates, plus reading the
full edge counts and initializing2(H+1) integer cells. The mask and energy
use O(n+log(H+1)) bits; each coefficient uses at most n bits. Adjacency and
the complete input counts remain costs. No assignment or posterior table
of K floating values is needed. The Python prototype does not equate these
logical integer-cell counts with its complete heap footprint.

Horner evaluation at9 uses O(H+1) positive integer scalar operations per
partition. Since Z_0+Z_1<=K*9^H, partition integers have fewer than
`n+4H+1` bits. Multiprecision arithmetic is not a unit-cost machine claim.
The prototype preflights world/span/integer limits before enumeration or
powers, and separately preflights the floating output count before rounding.
It is not a paid Runtime tariff or a complete resource-existence solver.

The tradeoff is real even at n16. With every count+1 or every count-1,
the graph is complete. Every possible first eliminated free vertex has a
15-variable joined scope:32768 cells, above the4096-cell order allowance.
For either sign, query(0,1) or(1,2) has only17 occupied query/exponent bins.
The histogram schedule below uses170 floating output cells, including51
half outputs. Exponential enumeration is small enough to examine this
fixture, but is still exponential. Nothing follows for unrestricted n,
global n256 enumeration, or an already halted Runtime continuation.

## 3. Fixed mixed-precision schedule

Assume2<=n<=16. Let U be the largest occupied exponent and put

    t_(y,k) = h_y(k)*9^(k-U),   Zbar=sum_(y,k)t_(y,k).

At least one world has exponent U, so1<=Zbar<=K<=32768. U is computed from
the complete enumeration's occupied bins; it is not a free global energy
optimizer or the sum of possibly incompatible local maxima. Replacing it
by H is unsafe: on the n3 triangle with counts(-80,-80,-80), H=240 but
U=160. All three grouped terms scaled by9^-H round to zero even if each
exact term receives only one binary32 rounding. The correct occupied scale
retains a positive denominator and passes the full native relation.

This normalization does not require knowing either partition or its ratio.
For each occupied coefficient h at lag l=U-k, let D=9^l,
a_exp=bit_length(h), b_len=bit_length(D),

    a=h/2^a_exp,  b=2^(b_len-1)/D,  e=a_exp+1-b_len.

Then t=a*b*2^e, a in[1/2,1), b in[1/2,1], and e<=16. Perform:

1. Ingress a,b with nearest/ties-even binary32. a is exact since h<=32768.
2. Cast both to binary16, multiply in binary16 and widen exactly to binary32.
3. Multiply by the exact binary32 power2^e if e>=-149. Otherwise multiply
   by+0: the half product is at most1, so even at e=-150 its exact scaled
   value is at most half the least binary32 subnormal and rounds to+0.
4. Sum each partition with a balanced binary32 addition tree. An empty
   partition is the exact constant+0.
5. Form one shared rounded denominator, divide each partition by it, then
   perform the existing binary32 native excess/mass/normalizer/probability
   operations. Copy all seven words. Observation uses the existing three
   gradient forms and its unchanged13-output arithmetic schedule.

All rounding is nearest/ties-even with gradual binary32 subnormals and
separate operations. There is no FMA, approximate reciprocal or unverified
flush-to-zero assumption. Actual CUDA conformance is an additional gate.
Step3's zero is a proved rounded temporary, never a deleted count or world.

If b_parts is the number of nonempty partitions, the exact prediction
schedule count is

    C = 9L+21-2*b_parts,     binary16 outputs = 3L.

Each term has eight scalar outputs; the balanced sums use L-b_parts;
empty parts use2-b_parts constants; the readout uses12 operations and seven
copy cells. Thus for H<=396, C<=7163, regardless of graph/elimination width.
There are no bucket joins in this schedule. Full native materialization,
CPU enumeration, integer constants, arena ownership and retained evidence
still need their own funding. The count is not a whole-model memory bound.

## 4. Uniform precision law

Write u=2^-24, v=2^-11, tau=2^-150. For an upper bound Lstar on L, take
d=ceil(log2 Lstar) and define

    epsilon = (1+v)^3*(1+u)^(d+1)-1,
    eta = Lstar*tau*(1+u)^d,
    A = 2*epsilon/(1-epsilon-eta),
    B = eta/(1-epsilon-eta),   Dq=A/4+B.

The half operands/product stay in[1/2,1] and[1/4,1], respectively. Their
three relative errors are bounded by v. Only b's ingress needs another
relative factor(1+u). Scaling a half mantissa by a binary power is exact
when normal, and has absolute error at most tau when subnormal or zero.
Positive binary32 addition has relative error at most u even in the
subnormal case: below the normal threshold, the exact sum of two binary32
values is an integer multiple of the least subnormal and is representable.
There is no overflow: every partial sum is bounded by
`(1+epsilon)K+eta < 2K`.

Distributing the balanced-sum factors over its leaves therefore expresses
each actual partition s_y as `(1+theta_y)*Zbar_y+e_y`, with
`|theta_y|<=epsilon` and `|e_0|+|e_1|<=eta`. Its sum is positive, since
Zbar>=1 and1-epsilon-eta>0. For q=Zbar_0/Zbar and r=s_0/(s_0+s_1),

    |r-q| <= A*q*(1-q)+B <= Dq.                 (1)

This follows by cross multiplication; numerator contributions are
`q*(1-q)*(theta_0-theta_1)` and `(1-q)e_0-qe_1`, after dividing by Zbar.
Both targets obey the same bound. An arbitrarily tiny partition needs no
relative-accuracy assumption of its own.

Include the subsequent denominator, divisions and native readout. Put

    kappa=2u/(1-u),   R=8*(kappa+tau)+9u.

Each computed marginal differs from r_y by at most r_y*kappa+tau. Multiplying
by eight is exact. R bounds each stored mass's difference from1+8r_y.
The following bounds cover the actual complete-coordinate bridge:

    native excess/mass error <= 8*Dq+R,
    normalizer and stored-mass sum error <= 2*R+18u,
    probability error <= (4/5)*Dq+R/(10-2R)+kappa+tau,
    stored-mass probability versus rounded word <= kappa+tau,
    every native gradient error <=
        64*(A/36+B)/(1-8*Dq)+8*R+18u.           (2)

For the probability term, normalization of the two perturbed masses changes
their ideal ratio by at most R/(10-2R). The last two terms also include the
separately rounded normalizer and probability division.

The gradient bound is sharper than applying a global derivative to Dq.
The exact identity

    (1+8q)^2 - 36*q*(1-q) = (1-10q)^2 >= 0

gives q(1-q)/(1+8q)^2<=1/36. Also
`1+8r >= (1-8*Dq)*(1+8q)`. Apply(1) to the difference of8/(1+8r) and
8/(1+8q); this proves the first term of the gradient bound. Replacing
1+8r by its stored mass adds at most8R, since both are at least1.
Binary32 ingress of4/5, reciprocal multiplication and final addition add
less than18u. The fixed-gradient form has smaller bounds, and the remaining
form is just rounded4/5. Thus every native slot, including the fixed slot,
is covered. Exact count equality preserves every parameter and both clocks.

Finally the rounded denominator is at least each nonnegative partition,
so each rounded marginal is in[0,1]. Excesses stay in[0,8], masses in[1,9],
and their rounded normalizer and exact stored sum are at most18. These
are the existing native activation/normalizer caps; internal histogram
sums are execution coordinates with their separately proved range.

With Lstar=32768, all n<=16 histories for which the required exact integer
work is available have the following outward decimal upper bounds:

| Complete bridge coordinate | Bound | Existing allowance |
|---|---:|---:|
| Native excesses/masses |0.005877|0.01|
| Normalizer |0.000004054|0.01|
| Probabilities, including proper stored-mass probabilities |0.000587736|0.001|
| Every native gradient |0.005265784|0.01|

The precision assertion is uniform in count magnitude; resources are not.
For H<=396, Lstar=794 slightly improves these bounds. No floating error
accumulates in committed parameters: the physical count rewrite remains
exact and independently derived from actual events, as in the existing
indexed backend. This is not rounded SGD followed by a reference reset.

## 5. Exact audit and remaining owned execution

Run `python -X utf8 -B experiments/joint_uncertainty/audit_count_histogram.py --check`.
The [minimal evidence](../../evidence/minimal/FP_COUNT_HISTOGRAM.json) retains
aggregate counts, bounds and small source-reconstructible witnesses:

- All759 ternary count states for n2 through n4, at all11919 ordered
  queries including diagonals, agree with independent lexicographic world
  enumeration. The independent oracle uses signed equality scores; the
  implementation uses incident-edge updates along a Gray traversal.
- Every one of these queries also passes the existing complete native/AMP
  coordinate checker under exact scalar RNE. Dense cases, exposed cuts and
 396-span stress and the normalization counterexample give11930 predictions
  and23860 both-target observations:1067834 words including declared output
  copies,182946 binary16 words.
  Maximum probability error is about4.081e-5; maximum gradient error is
  about4.843e-4. These observed maxima do not replace the uniform proof.
- Actual literal-native evaluation/observation/commit checks1054 complete
  caches and1054 of each complete observed/committed state. This includes
  three profile/attachment continuations and a104-event late-birth reversal.
  After52 same-label events, the unlikely physical excess rounds to zero
  while its exact native excess remains positive. After52 contrary labels,
  the retained counts return to zero, the complete native weights to(1/2,1/2),
  and the rounded forecast to1/2; clocks remain(cursor,steps)=(111,104).
- All14/13 possible first eliminated vertices of the two dense query
  fixtures refuse the4096-cell join allowance. Both histogram schedules
  have17 terms,170 outputs and51 half words.
- Eleven malformed/short preflights enter no enumeration; a one-cell-short
  floating allowance enters no rounding. None issues a class certificate.

Five separately reconstructed exposed model cuts pass the passive full
native/rounding checks, with32768 assignment visits each:

| Case / cursor / query | Occupied terms | Floating output cells |
|---|---:|---:|
|c2/16 /194 /(6,9)|230|2087|
|c2/17 /332 /(8,7)|290|2627|
|c4/18 /276 /(2,5)|258|2339|
|c4/18 /372 /(15,1)|304|2753|
|c4/19 /368 /(4,13)|314|2843|

In particular the old65574-output obstruction at c4/18/276 is a restriction
of its elimination schedule class, not of this native count learner. The
histogram witness does not resume a halted Runtime or supply a model score.
This audit does not execute a new CUDA kernel or register a Runtime decoder.
Source/workspace ownership, prepaid reconstruction, retained phase evidence,
full event/lineage binding, fresh persistence and installation remain
obligations for any future owned implementation. An incomplete or unfunded
calculation must stay UNRESOLVED.

## 6. Registered actual arithmetic fixture

`scripts/audit_count_histogram_cuda.py --attempt 1` is registered before
execution: one fresh4-GiB Windows job,600-second deadline, one16-MiB CUDA
arena with32-MiB allocator cap and65536 outputs per phase. Its16 cases are
the n3 prior on an ordinary/diagonal query; n2 signed counts+/-46,+/-47,+/-48
around the single-precision subnormal boundary; count396; both dense n16
fixtures; and the five exposed cuts in section5. Each executes one prediction
and both independent target branches, for48 actual device phases.

The helper prototype now returns its actual resident output tensor as well
as the complete raw prediction. The arithmetic is unchanged. The fixture
freshly reads the endpoint after execution, compares every operation with
the independently reconstructed exact RNE schedule, and checks all native
prediction/gradient coordinates against the independent assignment oracle.
It checks arena extents and the actual RTX3090/build identity. No reference
posterior or forecast enters the numerical kernel.

The parent checks committed clean inputs and binds the source before launch;
the child starts attached to the declared job. Each completed case is retained
in the worker result before advancing. Keep every terminal failure or timeout;
do not retry silently or relax any cap. Commit inputs before execution and
keep that checkout's HEAD/input files fixed until the parent has collected
the terminal journal. Section7 records the terminal outcome.

This is an arithmetic fixture. Its host enumeration/readout/metadata are
bounded by the job, without pretending to be prepaid Runtime records.
It has no new constructor, native event admission, lineage, bridge issuance,
fresh persistence, installation, model score or complete-release authority.
Those require the owned integration described above. Existing source-bound
model work must finish before this new device job is launched; there is no
exclusive-device throughput or elapsed-time comparison.

## 7. Actual RTX3090 outcome

The registered A1 passes all16 cases and48 device phases at
`4a4e7309e44705410840977a21249ed8f25a3ded`. The
[minimal source/job-bound journal](../../evidence/minimal/FP_COUNT_HISTOGRAM_CUDA_A1.json)
retains every case's endpoint words and errors. The job exits zero with
no timeout or memory-limit termination; peak whole-job commitment is
2185007104 bytes, below4 GiB. The actual Torch/build/CUDA/RTX3090/SM tuple
matches the declaration. There is one16-MiB tensor allocation and one
16-MiB allocator segment throughout.

Actual prediction outputs total13297; both-target observations make13713
complete output words, including4341 half operations. Every intermediate
operation and fresh final output agrees with exact RNE, including the
single-precision subnormal cases. All native readout/gradient checks pass.
Maximum observed probability error is about3.179e-5 and gradient error
about1.130e-4. The five exposed cuts use the exact2087--2843 output counts
in section5; both dense fixtures use170 outputs. The uniform theorem is
unchanged by these finite hardware observations.

An independent retained-endpoint reader recomputes all208 prediction and
gradient words and their error records without executing CUDA. It is
reproducible with
`python -X utf8 -B scripts/audit_count_histogram_cuda.py --read evidence/minimal/FP_COUNT_HISTOGRAM_CUDA_A1.json`.
The actual A1 job is terminal and must not be repeated without a substantive
new registered test. This closes the numerical component question. The
owned CPU implementation and actual Runtime phase, lineage, fresh
persistence and installation gate now pass. No new model stream or
complete indexed release is inferred.
