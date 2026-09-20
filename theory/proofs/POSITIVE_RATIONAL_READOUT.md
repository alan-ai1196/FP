# One native normalization can express positive rational computations

Status: **PROVED, SCOPED; EXACT NATIVE AUDIT AND DECLARED NUMERICAL REFUSALS**.
The [positive partition lower bound](POSITIVE_COUNT_PARTITION.md) concerns
division-free computation of a particular polynomial. It cannot be promoted
to a general normalized-forecast bound. Here a constructive native compiler
makes that limitation substantive for nonconstant functions, while exposing
the degree, range and precision costs that graph size alone omits.

This adds no Foundation action or Runtime primitive. The implementation is
a passive Program builder and audit. Existing model registrations, production
constructors, full-state obligations and ERC-1 remain unchanged.

## 1. Exact scope and constructive readout theorem

Let R(theta)>0 be computed by an acyclic circuit with s binary operations
from {+, multiplication, division}. Its leaves are the constant1 and
`1+theta_i`, for d nonnegative parameters. Denominators are therefore
positive throughout this domain. There are no negative constants or
subtractions. Constants other than1 may be constructed by these operations,
with their construction counted in s.

**Theorem.** There is an ordinary positive native SUM/PRODUCT Program with
bases(1,1), d+1 parameter slots and at most `2+2d+12s` nodes whose forecast is

`p_0(theta) = R(theta)/(1+R(theta))`, `p_1(theta)=1/(1+R(theta))`.

Slot0 is a fixed feature initialized to1; the remaining slots contain theta.
The complete source domain is the single row `one=1`, or a previously proved
unit expression independent of the selected parameters and equal to1 on
another declared complete source domain. A scalar source range
[0,1] alone is insufficient. The theorem holds for all theta>=0 at this
fixed feature value, including derivatives in the selected coordinates.
It is not a claim about a source domain that was only empirically observed.

First maintain a fraction N/Q for each original circuit gate. Both N and Q
are positive-coefficient integer polynomials with constant term at least1.
For a pair of fractions, use

`N_add=N_a*Q_b+N_b*Q_a`, `Q_add=Q_a*Q_b`,
`N_mul=N_a*N_b`, `Q_mul=Q_a*Q_b`,
`N_div=N_a*Q_b`, `Q_div=Q_a*N_b`.

Sharing both components at each original gate avoids expression-tree
expansion. This classical fraction-pair conversion uses a constant number
of positive operations per original operation. It computes R=N/Q but does
not discard or divide a native intermediate value.

The positive bases require an additional step: the native heads must produce
N-1 and Q-1. Computing a huge constant coefficient and subtracting1 would
not establish the claimed native bound. Instead, maintain **(P,P-1)** for
each positive polynomial value, using only positive syntax:

`(A+B)-1 = (A-1)+B`,
`A*B-1 = (A-1)*B+(B-1)`.

The initial pairs are (1,0) and(1+theta_i,theta_i). The zero is an empty
native SUM. Every later excess has nonnegative coefficients by this
recurrence. No subtraction runs in the Program, and no large fitted
constant is introduced. Each positive addition needs at most two native
nodes; each multiplication at most three. Fraction addition requires at
most11 nodes, and fraction multiplication/division at most6. The source,
zero and shifted parameter leaves give the stated conservative node bound.
All nonempty SUMs have at most two incidences, so total incidences also grow
linearly in d+s.

With heads N-1,Q-1, the actual masses are N,Q, and the one existing readout
normalization gives N/(N+Q)=R/(1+R). The fixed feature multiplies every native
SUM as usual. Its actual derivative is not replaced by a derivative of the
abstract rational circuit, which has no such feature coordinate.

This proves a readout compilation theorem, rather than adding divisions to
FP or asserting that every scalar rational output is itself a probability.
The represented quantity R is the output odds. The paired polynomial state,
all native activations and the actual learner remain owned by the new graph.

## 2. A nonconstant exponential separation in graph size

Let phi_n(w) be the generating polynomial of directed spanning trees pointing
toward a fixed root in the complete directed graph. Each monomial is the
product of its n-1 directed edge weights. Put `w_e=1+theta_e` and
`R(theta)=phi_n(1+theta)`.

The classical directed-tree polynomial has exponential monotone arithmetic
complexity, whereas a subtraction-free circuit with division computes it
in O(n^3) operations. See [Fomin, Grigoriev and Koshevoy, Theorems2.7-2.8
and section7](https://arxiv.org/pdf/1307.8425), which state the Jerrum-Snir
lower bound and give a positive elimination algorithm. Summing over all
roots, if using that convention, changes these bounds only polynomially.

The shift by1 does not remove the polynomial lower bound. The highest
homogeneous degree n-1 of phi_n(1+theta) is phi_n(theta). Homogeneous
components through that degree can be extracted from a monotone circuit
using positive sums and truncated convolution, at O(n^2) operation overhead.
A polynomial-size monotone circuit for the shifted polynomial would thus
contradict the same exponential lower bound, up to a polynomial factor.

Apply section1 to the positive elimination circuit. The nonconstant forecast
`phi_n(1+theta)/(1+phi_n(1+theta))` has an O(n^3)-node positive native Program
with bases(1,1), although computing its displayed odds polynomial directly
by positive additions and multiplications costs exponentially many operations.
This is a stronger failure of the generic mass-to-forecast implication than
the constant-forecast common-factor counterexample. It does not give a fast
algorithm for the actual relation-task cut polynomial or its forecasts.

The audit implements positive directed elimination explicitly. Keep the root,
eliminate a nonroot vertex v, set `s_v=SUM_j w_vj`, and update each surviving
nonroot-to-other edge by

`w'_ij = w_ij + w_iv*w_vj/s_v`.

Multiply the output by s_v. The directed Laplacian's Schur complement gives
this update and its determinant multiplier; repeated elimination returns
phi_n. All weights are positive, so every pivot is positive. There are O(n^3)
operations. Independently enumerated labelled trees and their derivatives
check this specific implementation in the small exact audit.

Fraction clearing and the difficulty of lower-bounding all positive multiples
of a polynomial are discussed in [Hrubes and Yehudayoff, *Shadows of Newton
polytopes*, section6](https://iuuk.mff.cuni.cz/~koucky/EPAC/papers/TechRep-Hrubes-ECCC-TR20-189.pdf).
That report already explains why division-free lower bounds do not settle
the larger circuit class. The new FP-specific step here is the positive-base
construction and verification of the resulting native learner and costs.

## 3. The cost hidden in this compiler's shared denominators

Polynomial graph size does not give a polynomial resource contract. For the
specific elimination and fraction-clearing order above, let b_k be the degree
of each **unreduced** edge denominator when k vertices remain. In the original
edge weights w, all edge numerators are homogeneous of degree b_k+1.
Starting with b_n=0, the left-associated sum over k-1 incident fractions has
denominator degree(k-1)b_k and numerator degree1+(k-1)b_k. Cross multiplication
in the edge update yields

`b_(k-1) = 1+(k+2)*b_k`.

The output numerator's degree, also the maximum selected degree in this
actual native Program, is

`a_n = SUM_(k=2..n) [1+(k-1)*b_k]`.

There is no cancellation in these positive polynomial nodes. The recurrence
gives degrees1,3,11,57,377,2935,25955 for n2 through n8. In fact
`b_2=(SUM_(j=4..n+1) j!)/24` for n>=3. Also
`b_k<=24*b_2/(k+2)!`, so the weighted sum defining a_n is within constant
factors of b_2. Hence `a_n=Theta((n+1)!)`. This is a property of this emitter, not a necessary
degree lower bound for every representation of the forecast.

At the declared uniform simplex initializer, d=(n-1)^2 directed edge slots
have theta_e=1/d and w_e=(d+1)/d. The output numerator is a homogeneous
polynomial of degree a_n with positive integer coefficients. Consequently
its value is at least `(1+1/d)^a_n`. Its reduced rational numerator is at
least `(d+1)^a_n`, since d and d+1 are coprime and any cancellation can only
remove factors from the integer coefficient. Thus this actual node needs
at least `floor(a_n*log2(d+1))+1` numerator bits. A small rational oracle for
the **ratio** does not make those complete native values disappear.

The retained audit makes no timing or GPU claim. At n6 the native graph has
636 nodes and degree377, and the exact forward values use up to2006 numerator
or denominator bits. Its passive binary64 forward evaluation remains finite.
At n7 the graph has1075 nodes and degree2935: the full exact forward/gradient
audit returns UNRESOLVED under its32768-bit operation guard, and passive
binary64 first becomes nonfinite at node1032. The n8 case also refuses both
checks. These are actual declared numerical refusals, not a proof that the
guard is tight or that an alternative compiler must fail there. Larger rows
only construct syntax and verify degree recurrences.

This is why a division-free **semantic** action list does not by itself settle
physical inference complexity. A different solver may reduce common factors,
choose another valid graph or refuse the finite contract. It cannot replace
the compiled graph's state with the cheap rational oracle without proving the
required complete-state and bridge relation. No new architecture primitive
is justified merely by these failures.

## 4. Native gradients and legal continuation

At fixed feature1, equality holds for all nonnegative theta, so the actual
selected CE gradient for the tree readout is

`g_e = -(partial_e R)/(R*(1+R))` for label0,
`g_e = (partial_e R)/(1+R)` for label1.

Each edge occurs at most once in a tree. Therefore
`0<=partial_e R<=R/(1+theta_e)`. For either label the spread between selected
gradient coordinates is strictly below1. The existing unit-rate simplex U
preserves nonnegativity, its unit total and the fixed feature. The readout
identity therefore continues along every exactly representable legal learner
history; finite arithmetic may still return UNRESOLVED.

The abstract rational circuit is not the complete native learner. In
particular its absent feature derivative cannot replace the actual slot0
gradient, and its compact intermediate values cannot replace the native
evaluation state. The audit compares the full observed gradient accumulator
and the full committed state, including the unselected coordinate, clocks,
empty delay state and optimizer steps. It also checks two-pass profile and
clock attachment through the existing arithmetic helpers. None of those
helpers grants Runtime data, construction, persistence or install authority.

## 5. Minimal evidence

Run `python -B experiments/joint_uncertainty/positive_rational_readout.py`.
The [retained evidence](../../evidence/minimal/FP_POSITIVE_RATIONAL_READOUT.json)
contains aggregate checks, graph counts and numerical refusal boundaries:

- 100 deterministic generated rational circuits,400 native forecasts and800
 complete-gradient checks against independent rational forward derivatives.
- 25 directed-tree cases through n6, with independent labelled-tree value and
 derivative enumeration and50 full native-gradient checks.
- 27 actual observe/commit pairs and54 complete-state comparisons, including
 three two-pass profile/attachment cases.
- The syntax/degree resource sequence through n16, successful exact and passive
 binary64 rows through n6, and explicit n7/n8 refusals. A finite forward-only
 binary64 check is not an AMP bridge certificate.
- A legal-domain counterexample: source one=0 respects its scalar upper bound
 but changes the n3 forecast from75/91 to1/2. The complete unit-domain
 assumption cannot be erased.

The proof, arithmetic audits and resource observations remain separate.
No new production solver, installed candidate, complete-class decision,
model score or change to the fixed running experiments follows.
