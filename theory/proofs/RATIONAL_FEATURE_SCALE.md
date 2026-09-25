# The likelihood floor, native range and fixed rational coefficients

Status: **PROVED, SCOPED; COMPLETE EXACT NATIVE AND SCALAR RNE AUDIT PASS**.
For a finite positive likelihood bank and fixed positive readout bases, the
optimal all-history supremum of the native normalizer is

    C* = max_(query x, label y, hypothesis h) b_y / ell_(x,y)(h).

It is attained by ordinary positive SUMs with fixed rational coefficient
slots and the existing unit simplex U. A common denominator need not set the
native range or multiply the graph's incidences. It still contributes to
exact input and inference bit costs. This is a range optimum, not a universal
optimum for graph size, memory, time, complete state or experiment resources.

The construction changes G/Gamma and the ambient gradients. It preserves
the selected Bayesian update but is not a full-state quotient of the existing
integer-copy program. A separate all-coordinate scalar RNE law below covers
this new binary relation realization. No owned Runtime, device conformance,
lineage transport, fresh installation or constructor authority follows.

## 1. A sharp range law, including a fixed positive prior

Fix a finite nonempty complete query alphabet X, a finite hypothesis bank H,
positive rational prior pi, and strictly positive rational likelihoods
ell_(x,y)(h) normalized over a finite label alphabet. Every finite query/label
word is legal in the mathematical model. Fix the native readout bases b_y>0;
write B=sum_y b_y. Require exact Bayesian forecasts after every legal word.
The computational contract can refuse a word when resources do not fit;
such a limited implementation has not assumed this all-history premise.

Every positive native program has M_y>=b_y. If its native normalizer is Z
and its forecast is p_y, it therefore obeys

    Z >= b_y / p_y.                                           (1)

This statement does not assume affine masses or a constant normalizer.
To obtain the all-history lower from the fixed prior, choose a hypothesis h.
Let L clear the denominators of its likelihoods. Form a legal calibration
block containing, for every x,y, exactly L*ell_(x,y)(h) copies of event (x,y).
Its order can be fixed in advance. For any hypothesis k the block likelihood
ratio satisfies

    log(Likelihood_k / Likelihood_h)
      = -L * sum_x KL(ell_x(h) || ell_x(k)) <= 0.                (2)

The inequality follows directly from log t<=t-1. Equality holds exactly
when the two hypotheses have identical complete likelihood signatures.
Repeat the block r times. Every distinct-signature ratio decays geometrically;
positive pi makes the posterior concentrate on h's signature group. It need
not concentrate on an individual member of an identical-signature group.
Every next-query forecast tends to ell_(x,y)(h). Equation (1) then gives

    sup_(legal histories and next queries) Z >= C*.              (3)

This lower applies even to a nonconstant normalizer or a realization valid
only on the fixed-prior reachable orbit, provided that orbit covers every
finite legal word and its forecasts are exact. The supremum need not occur
at a finite history. It is not a lower at one bounded horizon, on a restricted
query policy, or on approximate forecasts. With only absolute forecast error
epsilon, the same argument yields b_y/(ell_(x,y)(h)+epsilon), not (3).
Changing the positive bases changes the law; they are fixed here.

The calibration argument concerns legal continuations, not their frequency.
It does not assume that a sampled history is typical or that the bank contains
the actual data-generating law. The Bayesian statistical interpretation of
the updates retains its separate observation-law and causal-policy premises.

## 2. Attain the lower with native rational feature slots

For any rational C>=C*, set

    gamma_(x,y,h) = C*ell_(x,y)(h) - b_y >= 0.

Use ordinary one-hot query sources. A feature SUM for (h,y) contains one
incidence of source x using fixed slot gamma_(x,y,h), for each x. A label
head SUM weights these features with selected simplex coordinates w_h.
Initialize all gamma slots explicitly and w=pi. Only w belongs to U's
selected block. The source interface is the complete declared one-hot query
alphabet, not arbitrary simultaneous activations of its source rows.

On that interface and the simplex,

    M_y = b_y + sum_h w_h*gamma_(x,y,h)
        = C * sum_h w_h*ell_(x,y)(h),       sum_y M_y = C.        (4)

The coefficient column sums are C-B, so the existing
[simplex gradient theorem](SIMPLEX_GRADIENT_POSTERIOR.md) applies. In detail,
the actual ambient selected derivative and its weighted mean are

    g_h = (C-B)/C - (C*ell_(x,y)(h)-b_y)/M_y,
    g_bar = b_y/M_y - B/C.

The existing one-event, unit-rate, ungridded normalized simplex U gives

    w'_h = w_h*(1-g_h+g_bar) = w_h*ell_(x,y)(h)/p_y.             (5)

The raw successor is positive and sums to one; U's explicit normalizing
division is the identity in exact arithmetic. All fixed slots stay fixed,
but their ordinary ambient derivatives remain in the observed native state.
This construction introduces no new native node type or optimizer action.
It is a direct corollary of the existing affine-gradient law, not a new
general natural-gradient principle.

Taking C=C* attains (3). Thus C* is the exact minimum of the all-history
normalizer supremum over such native realizations. If the physical schedule
requires an integer C, the smallest admissible one is ceil(C*). Rational
noninteger C* remains valid for exact native semantics.

Since every coefficient column is nonnegative and sums to C-B, feature/head
values are at most C-B and M_y<=C-sum_(v!=y)b_v. Actual fixed-coefficient
storage, bit precision, world enumeration, source rows, graph structure and
decoding costs remain. Equal selected statistical continuations are not an
identity of programs, initializers, caches, gradients or structural futures.

## 3. The joint relation bank: a complete different G/Gamma

For rates eta_j in (0,1/2), positive pi_j and n anchored latent bits, put
K=J*2^(n-1). Use the existing 2n categorical sources and n^2 pair PRODUCTs.
Choose C>=1/min_j eta_j. Two fixed slots per rate suffice:

    gamma_(j,match) = C*(1-eta_j)-1,
    gamma_(j,other) = C*eta_j-1.                               (6)

For each rate/world/label, its feature SUM has one term per ordered pair,
using the matching or other slot according to the world's pair parity.
Each label head then has one incidence per world on its selected world slot.
The initializer is the 2J fixed coefficients followed by pi_j/2^(n-1).
The selected block begins at slot 2J. Zero fixed coefficients are included.

    nodes          = 2n+n^2+2K+2,
    slots          = K+2J,
    SUM incidences = 2K*(n^2+1).                              (7)

The old integer-copy program instead has K+1 slots and
K*((S-2)*n^2+2) SUM incidences, where S is the common rate denominator.
Neither expression includes the 2n^2 PRODUCT incidences. The new program
exchanges coefficient sharing/storage for repeated integer incidences; (7)
is a construction count, not a minimum over all native graphs.

For an actual query and target y define

    u_j = sum_z w_(j,z),
    v_jy = sum_(z: queried parity=y) w_(j,z),    M=M_y.

The complete fixed-slot gradient is

    g_(j,match,fixed) = u_j/C - v_jy/M,
    g_(j,other,fixed) = u_j/C - (u_j-v_jy)/M.                   (8)

Selected world gradients have the two classes per rate

    g_(j,match,selected) = (C-2)/C - gamma_(j,match)/M,
    g_(j,other,selected) = (C-2)/C - gamma_(j,other)/M.          (9)

Thus 4J scalar coordinates suffice for the full gradient, with the actual
ordered query, target and native slot mapping. This is an upper basis size,
not a minimality theorem. Seven head/mass/normalizer/probability coordinates,
the query, and the fixed coefficient metadata decode the complete Evaluation.
The model, all (T,d,s), ordinary and optimizer clocks, pending event and unit
remain. The exact posterior decoder is unchanged because (5) is unchanged.
Profile multiplicity and phase boundaries still have their original meaning.

At the default prior, C=10, an initial diagonal label0 has derivative 1/20
at the low-rate **fixed coefficient zero**. Deleting that coordinate would
already change the observed native state. Also, two free positive simplex
states with rate/parity integer parts ((30,10),(20,20)) and ((25,15),(28,12))
have Z=80, identical head coordinates and identical excess integers (8000,4800),
yet their first fixed gradients differ by -1/96. These free states are not
claimed reachable from the fixed prior. They refute a general full-simplex
gradient reconstruction from those two excesses alone.

## 4. Denominator-independent range does not mean free precision

For q>=2 take rates

    (1/4, (q+1)/(4q)),      equal prior,       C=4.

The common denominator is S=4q, but the fixed coefficients are

    (2, 0, 2-1/q, 1/q).

The graph count is independent of q, native features/heads are at most 2,
masses at most 3, and normalizer exactly 4. The all-history lower in section 1
makes 4 optimal. Hence unbounded rational denominators do not impose an
unbounded native normalizer or integer-copy incidence count. The fixed
rational coefficient 1/q still requires Theta(log q) bits in this literal
encoding; no denominator-independent exact storage theorem follows.

To reuse positive joint inference, retain the original likelihood integers
a_j=S*eta_j, b_j=S*(1-eta_j), full unnormalized rate/parity parts R_jy and
Z=sum_j,y R_jy. For integer native scale C form

    E_y = sum_j [(C*b_j-S)*R_jy + (C*a_j-S)*R_j,1-y] >= 0,
    E_0+E_1 = (C-2)*S*Z,
    native excess_y = E_y/(S*Z) = (C-2)*E_y/(E_0+E_1).          (10)

The rates are never normalized separately. Existing positive elimination
geometry and all retained evidence still determine the R_jy. Static integer
coefficients in (10) are nonnegative; integer arithmetic, including their
construction, is paid work. This is not an external probability input.

With common prior denominator P, all positive integers in this construction
are bounded conservatively by (C-2)*P*2^(n-1)*S^(T+1). A sufficient bit envelope
adds ceil(log2(C-2)) to n+bit_length(P)+(T+1)*ceil(log2 S). The coefficient input
bits, elimination workspace/order, arithmetic count, actual bigint costs and
complete retained history do not disappear. A fixed 32768-bit audit does not
execute every q or every T. Mathematical bounds are conditional on funding
the exact integer construction and its independent input bindings.

## 5. Complete scalar rounding law for the new binary program

This section fixes a distinct passive schedule, with integer 3<=C<=2^24.
R32/R16 mean nearest/ties-even, gradual subnormals, separate multiply/add,
and ordinary division. The exact program still allows noninteger C; that
case has no authority under this particular scalar schedule.

Apply the existing two-excess half-mantissa/single readout equations to E_0,E_1
from (10), using **C-2**, not S-2, as excess amplitude. Ingress each positive
E_y/2^bit_length(E_y) in single, cast to half and back, multiply by its common
binary scale (zero below exponent -149), add the two values, divide by that
actual rounded denominator, multiply by C-2, add one, sum actual masses and
divide. Retain the seven outputs. Prediction uses at most 29 words including
copies and two half casts, just as the old scalar construction.

Observation uses the actual target mass's rounded reciprocal. For (9),
ingress the rational coefficient in single, multiply and subtract from the
single-rounded constant (C-2)/C. Rational coefficient ingress now matters.
For each fixed gradient in (8), compute u_j and each v_jy from its own exact
integer numerator N and common Z. Ingress N and Z as single mantissas, divide,
then multiply by 2^(bit_length(N)-bit_length(Z)); truncate a power below -149
to zero. A zero numerator yields zero. These ratio calculations use single
precision throughout. Compute u_j/C-v_jy/M with separate operations. No rate
posterior, native gradient or reference probability is uploaded by this law.

The full observation has at most 6+29J words including 4J gradient copies.
This includes all three auxiliary ratios per rate and all fixed slots, even
when their coefficient is zero. Persistent parameters decode exactly from
the complete rational model and counts; count commit is the exact algebraic
implementation of (5), not an accumulating rounded weight recurrence. For
non-head cache coordinates, decode the coefficient in single on an active
pair and zero otherwise. Its error is bounded below. Actual execution still
needs paid point decoders and complete phase/state ownership.

Here is an explicit uniform bound, independent of the integer denominator,
history length, number of worlds and number of rates. Put a=C-2,
u=2^-24, v=2^-11, tau=2^-150 and

    epsilon = (1+u)*(1+v)-1,
    D1 = 2*epsilon/(1-epsilon-4*tau),
    D0 = 4*tau/(1-epsilon-4*tau),       D=D1/4+D0,
    kappa = 2u/(1-u),
    R = a*(kappa+tau)+(2a+1)*u+2*tau.

Assume 1-aD>0 and C-2R>0. The
[two-excess proof](JOINT_EXCESS_PARTITION_BRIDGE.md#4-uniform-all-coordinate-rounding-law)
uses only nonnegative excesses summing to aZ', not integral native features.
It therefore gives unchanged readout bounds with C in place of S:

    E_mass = aD+R,
    E_norm = 2R+2(a+1)u,
    E_prob = (a/C)D+R/(C-2R)+kappa+tau,
    E_division = kappa+tau.                                   (11)

These cover both proper stored-mass probabilities and rounded words, and
both the stored mass sum and rounded normalizer. Physical masses lie in
[1,C-1]; the stored sum and rounded normalizer are at most 2(C-1).

For the auxiliary ratio N/Z in [0,1], the two mantissa ingresses and one
division give relative error at most (3u+u^2)/(1-u). Binary scaling adds at
most tau, or at most 2tau if its power is omitted. Thus the absolute error is

    F0 = (3u+u^2)/(1-u)+2tau,                                 (12)

and the physical ratio stays in [0,1]. The latter follows from monotonic
rounding when the exponents agree; otherwise the mantissa quotient is at
most 2 and the power at most 1/2.

Changing u_j,v_jy in (8) contributes at most (1+1/C)F0; changing the target
mass contributes at most E_mass because both exact and stored masses are
at least one and v_jy<=1. Constant/reciprocal ingress, the two products and
the subtraction add at most

    Q_fixed = (1+1/C)*(2u+u^2)+u+3tau.

The explicit multiplication by -1 is exact. Therefore

    E_fixed_gradient <= (1+1/C)F0 + E_mass + Q_fixed.            (13)

For selected gradients, the original sensitivity proof uses only 0<=gamma<=a:
the identity (1+aq)^2-4(a+1)q(1-q)=(1-(a+2)q)^2 controls inverse-mass
sensitivity even in a rare gradient class. Rational coefficient ingress has
error at most a*u+tau. Rounded reciprocal and coefficient magnitudes stay
at most 1 and a; their product also stays at most a. Ingress, multiplication
and final subtraction consequently add at most (4a+1)u+3tau. Hence

    E_selected_gradient <=
      a^2*(D1/(4(a+1))+D0)/(1-aD) + aR + (4a+1)u+3tau.         (14)

The non-head coefficient cache error is at most a*u+tau. Source/pair values,
exact parameter decoding and discrete clocks/units agree under the declared
component decoder. These bounds include every ambient gradient coordinate;
none is discarded because its weight or fixed coefficient is small.

Outward rounded sufficient bounds are:

| Coordinate | C=4 | C=8 | C=10 |
|---|---:|---:|---:|
| Native excess/mass | 0.000489115919 | 0.001467228548 | 0.001956284862 |
| Normalizer/stored sum | 0.000001430512 | 0.000003814698 | 0.000005006791 |
| Probability | 0.000122398190 | 0.000183522778 | 0.000195747696 |
| Fixed gradient | 0.000489548053 | 0.001467623429 | 0.001956672292 |
| Selected gradient | 0.000327488195 | 0.001268622220 | 0.001758275688 |

Thus the default bank (S=20,C=10) and the three-rate bank (S=120,C=8) both
meet the original 1/100 state and 1/1000 probability allowances under this
complete scalar law. The bounds do not claim that integer inference, metadata,
retention or a whole device job fits its resources. Primitive conformance
and plan provenance are hypotheses, not conclusions from these inequalities.

## 6. Counterexample boundary, audit and remaining execution obligation

At the original S=120 witness, two pair01 label1 observations, the old native
program/schedule has mass error 65863667/4117889024>1/100. The **different**
C=8 program has the same exact Bayesian forecast but a different native mass
and gradient state. Its declared new scalar schedule has native error
8950209/16471556096<1/100; both target observations satisfy every new bound.
The old actual UNRESOLVED result remains correct and terminal. No historical
job is rerun, repaired, or relabeled by changing its native program afterward.

Run:

    python -X utf8 -B experiments/joint_uncertainty/audit_rational_feature_scale.py --write

The [minimal artifact](../../evidence/minimal/FP_RATIONAL_FEATURE_SCALE.json)
contains counts, outward bounds and the short counterexamples, not caches
or full weights. Its exact native checks cover all two-event words at n2/n3,
all first events at n4, six 80-event profile traces, four members of the
unbounded-denominator family, and a noninteger C=5/2 example. The general
three-label, unequal-base audit additionally checks duplicate likelihood
signatures, every two-event word and the fixed-prior calibration argument.
Boundary integer parts include zeros and exponent separations through 4000.
There are 1,676 complete binary native triples plus 42 three-label triples;
1,102 nonzero derivatives occur at fixed zero coefficients. The main rounding
audit checks 3,376 predictions/observations, 362,366 scalar words including
copies, 6,736 half casts and 20 distinct coefficient-cache roundings. There
are 858 boundary part arrays. The exact witness comparison is retained
separately from those main rounding totals. The two largest denominator-family
cases have 32-bit and 203-bit S while C remains 4 and native graph size stays
fixed. A too-small C, an unfunded literal expansion, and a noninteger C under
the integer-only scalar schedule refuse.
All arithmetic audits use exact rationals and an exact RNE interpreter;
they import no Torch and execute no device job.

The remaining obligation is an owned implementation for this new G/Gamma:
complete native indexing, fixed-slot mapping, input-derived integer plans,
funded bit/work/storage bounds, all 4J gradient coordinates, failure lifetime,
lineage and independent actual RNE evidence. Any paired fresh installation
must preserve those complete coordinates. The existing integer-copy Runtime
and its completed model experiment are unchanged. Foundation, ERC-1 and all
`CERTIFIED_COMPLETE` decision classes remain unchanged; this result establishes
neither an extra semantic action nor a constructor certificate.

The subsequent [owned reference refinement](OWNED_RATIONAL_FEATURE_REFERENCE.md)
now closes native indexing, full exact phases, paid rate-part storage and
same-path reference freshness for this G/Gamma. It also proves and executes
an exact-gradient denominator obstruction despite native C=4: prediction fits
while a materialized fixed gradient exceeds the reference bit limit. The
Runtime retains the target and predecessor and returns UNRESOLVED. That
boundary does not contradict the range optimum or conditional scalar bounds
here. The new physical path remains unregistered.
