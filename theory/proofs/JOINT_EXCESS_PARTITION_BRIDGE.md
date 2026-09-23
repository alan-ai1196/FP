# Joint excess partitions and a uniform complete native readout bound

Status: **PROVED, CONDITIONAL; EXACT NATIVE AND SCALAR RNE AUDIT PASS**.
The joint unknown-noise learner admits a positive decoder through cyclic
supports and a finite basis for every native cache and gradient coordinate.
Two transient excess integers suffice for its mixed-precision prediction;
the complete counts retain the joint posterior. For the current two-rate
scale S=20, the declared half/single schedule satisfies the original 1/100
state and 1/1000 probability tolerances uniformly over histories, conditional
on exact construction, arithmetic conformance and available resources.

The proof also identifies a limit: native scale enters the error law. At
S=120, two ordinary observations give mass error greater than 1/100 despite
small forecast error. This is a different arithmetic realization from the
terminal [rational A1/A2 jobs](RATIONAL_LIKELIHOOD_RUNTIME.md). It does not
repair A1's verdict, resume either job, register a backend, or establish
Runtime ownership or actual GPU conformance.

## 1. The complete learner and its finite coordinate basis

Use the existing finite joint-noise native Program, rational rates eta_j
and positive rational prior pi_j, anchored fair worlds z_0=0, unit-rate
one-event simplex U, no grid or delayed state. Its source interface has
one categorical token per side. Pair indicators are actual native PRODUCTs.
Let S be the common rate denominator, with 3<=S<=2^24. Define

`a_j=S*eta_j`, `b_j=S*(1-eta_j)`, `a=S-2`.

For each world and label its native feature is the integer S*ell-1:
`c_(j,match)=b_j-1`, `c_(j,other)=a_j-1`. These are nonnegative, at most a,
and their two-label sum is a. The graph has one fixed feature slot t=1
and selected joint-world weights. The exact masses are

`M_y=1+SUM_(j,z) theta_(j,z)*c_(j,z,y)`, `M_0+M_1=S`.              (1)

The encoded predecessor contains all signed counts d, diagonal balance s,
ordinary cursor, optimizer-step clock T and pending event, together with
the full model identity. At an observed cut, counts and T still describe
the predecessor; only the cursor and pending event have advanced. Commit
increments T and the actual event's signed coordinate, then clears the
pending unit. Profile attachment preserves T while changing the cursor.
An externally supplied actual query/target must bind these transitions.

Let W_(j,z) be the positive integer joint weights from the
[retained-state theorem](NOISE_ACQUISITION_AND_STATE.md), with Z their sum.
The semantic parameter decoder is `theta_(j,z)=W_(j,z)/Z`, t=1. Equal
complete count encodings therefore mean exact equality of every parameter;
there is no floating master vector or accumulating rounded SGD recurrence.
An explicit parameter read still requires its own funded decoder.

A physical prediction can represent all non-head native nodes exactly from
the ordered source query and integer feature coefficients. All these values
are exactly representable in binary32 under the stated S bound. The remaining
cache basis consists of seven words: two excesses, two masses, normalizer
and two probabilities. The full observed gradient is represented by

`g_fixed = 1/M_y - 2/S`,
`g_(j,match) = a/S - (b_j-1)/M_y`,
`g_(j,other) = a/S - (a_j-1)/M_y`.                               (2)

The selected gradient mean is 1/M_y-2/S. Substituting it into the actual
unit simplex U gives `theta'_i=theta_i*(c_i+1)/M_y=theta_i*ell_i/p_y`.
The raw successor is positive and already sums to one. Thus the count
rewrite is an algebraic implementation of that U from its own predecessor
and event, not rounded SGD followed by an external reference reset.

Thus 2J+1 scalar words cover every pending native gradient coordinate, using
the actual target and original rate/world slot order. A nonloop query has
both parity classes at every rate, including extremely rare worlds. For a
diagonal, the actual target determines which class occurs. The bound below
covers every class, even the unused diagonal classes stored by this schedule.

This is a component relation for the complete native state and Evaluation,
not every possible Compiler, provenance or resource field. It extends the
[known-noise finite basis](INDEXED_PHASE_BRIDGE.md). It is not valid for any
arbitrary Program with the same expert probabilities: a different ambient
graph can have different fixed-slot gradients and caches, as already shown
by the [normalized-likelihood audit](NORMALIZED_LIKELIHOOD_CHARACTERIZATION.md).

## 2. Positive decoding across changing support

Set H=SUM_e |d_e|, A=(T+s-H)/2, B=(T-s-H)/2, and k_j=P*pi_j for a common
prior denominator P. Reachability makes A,B nonnegative integers. For an
active edge with h=|d_e|, use factors (b_j^h,a_j^h) on parity (0,1) when
d_e>0 and swap them otherwise. Retain the rate-dependent constant

`C_j=k_j*b_j^A*a_j^B`.

For every rate, positive variable elimination with the actual query endpoints
retained computes

`Z_jy = SUM_(z: query parity=y) W_(j,z)`, `Z=SUM_j,y Z_jy`.

The support, order and join geometry are shared by all rates. An edge closing
a cycle needs no new semantic operation or special native optimizer. The
same positive algorithm handles it when its declared width/work/bit limits
fit. A later cancellation changes the support while T keeps its noise cost.
The forest decoder is a separate exact oracle on its own domain, not a
different persistent learner selected by this algorithm.

Combine the unnormalized rates in host integer arithmetic:

`N_0=SUM_j [(b_j-1)Z_j0+(a_j-1)Z_j1]`,
`N_1=SUM_j [(a_j-1)Z_j0+(b_j-1)Z_j1]`.

Then `N_0+N_1=a*Z`, and the exact native excesses are

`A_y=N_y/Z=a*q_y`, `q_y=N_y/(N_0+N_1)`.                          (3)

Every contribution is nonnegative. No rate is independently normalized or
discarded. Both integers can be formed without materializing joint worlds.
The numerical theorem below needs only (3) and the canonical coefficient
bound 0<=c<=a. It applies to any such canonical binary expert graph for
which the exact joint excess integers have been constructed, not just a
forest or this particular pair-query geometry. The 2J+1 gradient-class count
still belongs specifically to the finite-rate relation family; another
expert graph needs its own complete coordinate and input binding.

**Whole construction scope.** Reuse the proved positive elimination geometry
and its supplied order. If L is the tape size, the prototype evaluates one
rate at a time with O(JL) table operations, plus
O(J(log(T+1)+SUM_e log(1+|d_e|))) power operations and O(J) final aggregation.
It retains a value per tape node: O(L+m+J) integer cells, plus the tape,
dense count scan, graph metadata and exact/rational readout work. The
geometry's smaller peak-live-table number is not this prototype's actual
numeric-vector extent or a Python heap bound.

Every constructed positive integer is bounded by
`P*2^(n-1)*S^(T+1)`. A conservative bit envelope is

`b=n+bit_length(P)+(T+1)*ceil(log2 S)`.                            (4)

Partial joins use disjoint original factors; eliminated assignment sums
account for at most the full world multiplicity. Positive rate aggregation
uses SUM k_j=P. Multiplication cost must be evaluated on these b-bit values.
For fixed rates/prior, this is O(n+T) bits, without a claim that dependence
on elimination width is polynomial. The prototype preflights integer and
scalar-rounding guards, order, geometry, tape size and the total positive
integer operation count across all rates before powers. The latter includes
binary powers, rate constants, table operations and final aggregation; the
per-rate geometry cap alone would undercount this work.
Its extra 1,024-bit rounding margin covers exact binary32 ingress/scalar
checks; it is separate from (4). No packed or whole-host ownership follows.

**These are transient response coordinates.** After just 01:label0 versus
12:label0 at n3, query 02 gives the same integers (720,720), Z=80 and all
the same current native readout values. The next query 01 gives respectively
289/400 and 1/2. Retaining only N_0,N_1,Z would therefore destroy legal
future behavior. The complete model, (T,d,s), pending event and clocks stay.

## 3. The declared half/single scalar schedule

For each positive N_y, put b_y=bit_length(N_y) and C=max_y b_y. Ingress
N_y/2^b_y in binary32, cast to binary16, widen to binary32, and multiply
by the exact binary32 power 2^(b_y-C). If b_y-C<-149 use zero for this
temporary power. A zero integer part is represented by exact zero.

Add these two scaled values in binary32. Divide each by their shared rounded
denominator. Multiply by the exactly representable integer a, add one to
each, add the resulting masses, and divide them by that actual normalizer.
Retain all seven final words. Thus the final heads and masses are single
precision; they are not the old dense native graph's half-node outputs.
This is a distinct physical schedule with its own required future identity.

Observation ingresses a/S and -2/S, computes one single-precision reciprocal
of the actual target mass, then forms (2) with separate integer-coefficient
multiplications and additions. All output copies and gradient classes stay.
Prediction uses 21+4k words including copies, where k is the number of
positive integer parts: at most 29 words and two half casts. Observation
uses 6+8J words including copies. These counts exclude exact integer work,
the complete code/state encoding and any explicit native-coordinate reads.

All operations here mean nearest/ties-even, gradual binary32 subnormals,
separate multiply/add and division, without approximate reciprocals or FMA.
Actual device conformity and complete owned execution are separate obligations.

## 4. Uniform all-coordinate rounding law

Let u=2^-24, v=2^-11 and tau=2^-150. Define

`epsilon=(1+u)(1+v)-1`, `eta=4*tau`,
`D1=2*epsilon/(1-epsilon-eta)`, `D0=eta/(1-epsilon-eta)`,
`D=D1/4+D0`, `kappa=2u/(1-u)`.

The exact scaled total is in [1/2,2). Half mantissa rounding has its usual
relative bound, and binary scaling is exact when normal, with absolute
error at most tau otherwise. Omitting a power below -149 also has absolute
error at most tau. The largest term cannot vanish. The positive ratio
argument from the [direct partition proof](DIRECT_INTEGER_PARTITION_READOUT.md)
gives, for r_y equal to the exact ratio of the two computed scaled values,

`|r_y-q_y| <= D1*q_y*(1-q_y)+D0 <= D`.                            (5)

The rounded denominator and division change r_y by at most r_y*kappa+tau.
The rounded fractions remain in [0,1]. Multiplying by a need not be exact
(unlike the earlier multiplier eight), so retain its rounding term. Put

`R=a*(kappa+tau)+(2a+1)*u+2*tau`.

R bounds the difference of each stored mass from 1+a*r_y, and also suffices
for the corresponding excess. Stored excesses stay in [0,a], masses in
[1,a+1], and the stored sum and rounded normalizer are at most 2(a+1).
If 1-aD>0 and S-2R>0, all native readout coordinates obey

`native excess/mass error <= aD+R`,
`normalizer/stored-sum error <= 2R+2(a+1)u`,
`probability error <= (a/S)D+R/(S-2R)+kappa+tau`,
`proper stored-mass probability versus rounded word <= kappa+tau`. (6)

The probability statement covers both proper normalization of the stored
masses and the actual rounded probability words. The normalizer is checked
against both exact S and the sum of actual masses, not assumed to be S.

**All ambient gradient classes.** The identity

`(1+a*q)^2 - 4(a+1)*q*(1-q) = (1-(a+2)*q)^2 >= 0`

implies `q(1-q)/(1+a*q)^2 <= 1/[4(a+1)]`. Using (5), c<=a and
`1+a*r >= (1-aD)(1+a*q)`, changing q to r changes c/(1+a*q) by at most

`a^2 * [D1/(4(a+1))+D0] / (1-aD)`.

Changing the ideal mass 1+a*r to its stored mass adds at most aR, since
both masses are at least one. One reciprocal, integer multiplication, final
addition and constant ingress add at most

`Q=(3a+1)u+a*u^2+[a(1+u)+2]*tau`.

For example, reciprocal and multiplication together contribute at most
a(2u+u^2)+[a(1+u)+1]tau; the final exact difference has magnitude at most a,
and the constant has magnitude at most one. The fixed-gradient form is
smaller and is covered by the same upper. Therefore

`every native gradient error
 <= a^2*[D1/(4(a+1))+D0]/(1-aD) + aR + Q`.                       (7)

No world-probability lower bound is used to ignore rare gradient coordinates.
Parameters and discrete phase coordinates agree exactly under their encoded
decoder and independent input bindings. Equations (6)--(7), exact non-head
coordinates and those discrete equalities yield the complete native component
relation. They do not by themselves verify the provenance of supplied integer
parts or grant an opaque helper ownership of a Runtime phase.

For the existing rates (1/10,1/4), S=20, rational evaluation rounded outward
gives:

| Complete coordinate | Sufficient upper | Original allowance |
|---|---:|---:|
| Native excesses/masses | 0.004401567 | 0.01 |
| Normalizer/stored mass sum | 0.000010968 | 0.01 |
| Probabilities, including proper masses | 0.000220198 | 0.001 |
| Every native gradient | 0.004265781 | 0.01 |

These constants are independent of n, history length, query support, posterior
range and number of worlds. Those quantities still determine whether exact
construction and the full Runtime fit their resources. Larger S can make this
sufficient bound unresolved; that is not a lower bound for every schedule.

## 5. Attack the scope: native scale matters

Use rates (1/8,1/5,1/3), prior (1/7,2/7,4/7), S=120 and n2. Observe pair 01
with label1 twice. The actual joint native continuation is positive and exact.
At the following prediction the declared scalar schedule has native error

`65863667/4117889024 > 1/100`,

although its probability error is `140494495/1054179590144 < 1/1000`.
The normalizer error is 1/131072 and the observed gradient error is smaller
than 1/100. The mass violation alone rules out the original full-state
tolerance at this reachable cut. This is an exact RNE/native counterexample,
not merely a sufficient bound that failed to prove something.

At the old two-rate A1 mathematical cut (T,d,s)=(29,29,0), cursor27, the new
schedule instead satisfies every original tolerance. The audit executes an
independent exact native prefix with the original profile clock attachment,
then checks this new rounded readout. The old dense A1 schedule still has
its proved 1/64 normalizer failure; neither old job is rerun or relabeled.

Temporary underflow also does not erase a hypothesis. With rates (1/10,1/5)
and equal priors, 1,000 repeated label0 observations make one positive excess
round to zero. After 1,000 contrary labels the exact counts have d=0,T=2000;
the readout returns (1/2,1/2), but the first-rate mass is
`9^1000/(9^1000+16^1000)`, not its prior. The audit checks these two reachable
integer/RNE snapshots, not a 2,000-event owned GPU trajectory.

## 6. Minimal evidence and remaining physical obligation

Run `python -X utf8 -B experiments/joint_uncertainty/audit_mixture_partition_bridge.py --write`.
The [minimal artifact](../../evidence/minimal/FP_MIXTURE_PARTITION_BRIDGE.json)
retains counts, bounds and directed witnesses:

- Two finite rate banks cover 1,516 reachable states at n2..4 through T=3,
  all 21,604 ordered-query partition pairs and 26,660 exact weight points.
  Independent literal world sums agree. The 20,436 forest comparisons agree
  with the earlier independent path decoder; all 1,168 formerly refused
  cyclic queries are now decoded by the same elimination algorithm.
- 566 complete native triples cover both labels/all ordered small queries,
  late birth and an 80-update profile/cycle/reversal word ending at cursor78,
  step80. The two directed witnesses add 31 full native prefix triples and
  two final full predictions/four target observations. Thus there are 597
  complete native triples, with actual fixed-slot gradients and caches.
- 3,608 scalar RNE predictions and 7,216 target observations check 288,804
  floating words including copies and 7,215 actual half-rounding operations
  in the scalar interpreter. Every error obeys its scale-specific bound.
  A pass at S=120 means its proved bound, not the rejected 1/100 tolerance.
- Four n32/n64 cyclic-band queries agree with an independent vertex/energy
  histogram oracle evaluated at every rational rate. The n64 three-rate
  case represents 3*2^63 worlds with 2,229 tape-value slots, an eight-cell
  largest join and 1,088 maximum executed integer bits. Prediction still
  uses 29 floating words; host integer work remains explicit.
- Fifteen malformed/binding/resource cases refuse, including target and
  ordered-source substitution, rate order, clocks, pending-state use, short
  numeric outputs and precision, tape/work limits and dense n16 join width.
  Input states remain unchanged. The resource limits are scoped passive
  guards, not prepaid ownership or a constructor decision class.

The mathematical numerical barrier for the S=20 complete coordinate basis
is closed under this explicit schedule. The next obligation is a distinct
owned implementation: actual G/Gamma/U/source derivation, independently bound
integer plans, paid live storage and failure lifetime, phase/device evidence,
lineage, fresh persistence and installation. A small current readout cannot
replace any of those checks. No CERTIFIED_COMPLETE, full indexed release,
model superiority or Foundation/ERC-1 change is claimed.

The subsequent [joint native indexing/storage component](JOINT_NATIVE_PARTITION_STORAGE.md)
now supplies the literal description and contiguous integer construction,
with exact native and adversarial input/extent checks. It remains unregistered
inside Runtime; paid whole-owner execution and actual device conformance are
still required.
