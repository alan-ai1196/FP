# A general SUM cost law for fixed-PRODUCT approximation

Status: **PROVED RESOURCE LAW; EXACT CONSTRUCTION AUDIT**, 2026-09-12.
At fixed PRODUCT budget and finite normalizer cap, every conditional
closure point has a local-{1/2,1,2} approximation using O(log(1/delta))
weighted SUM nodes. With fixed algebraic source and target tables, a target
that is not exactly realizable in this local-alphabet class also requires
Omega(log(1/delta)) SUMs. Rational tables give a simpler explicit constant;
transcendental examples disprove an unrestricted-real extension.

## 1. The resource and decision class

Fix a finite complete context domain of size N, finite nonnegative source
tables, at most P scalar binary PRODUCTs, base one in each of k>=2 labels,
and one final normalization. Every finite candidate obeys T_x<=R<infinity,
with R>k. Local SUM weights belong to {1/2,1,2}; omitted terms and a zero
SUM are allowed. Let S count every weighted SUM from sources to final excess
heads. The fixed base/normalization stage is separate.

SUMs may have arbitrary finite arity and the DAG may share or square any
ancestor. The upper constructions also have O(log(1/delta)) SUM edges;
the lower bound remains valid even if arity is not charged. Neither S nor
P alone is a complete machine, acquisition, encoding or installation cost.
All errors below are for the complete declared domain.

Let S_Q(delta) be the least S achieving prediction sup error <=delta,
or infinity if no such graph exists. Let C_(P,R) be the prediction closure
with arbitrary finite SUM work and real nonnegative coefficients. The
previous `CONDITIONAL_COEFFICIENT_PATHS.md` proves that this equals the
local-alphabet closure. The classification here does not implement a
generic test for membership in that closure or for exact local realization.

## 2. Every closure point has a logarithmic construction

**Upper theorem.** For each Q in C_(P,R),

`S_Q(delta)=O_Q,P,R,sources(log(1/delta))` as delta tends to zero.

The same upper holds with a common activation cap
`A>=max(maximum_source_value,R-k)>0`. All constants may depend on the chosen
target and its complete coefficient-path witness; they are not uniform
over unknown targets, phase choices or precision/acquisition contracts.

Use the previous bounded mass lift and final excess contraction to obtain
a fixed finite graph whose prediction error is <=C_0*epsilon at the same
cap R. Apply its exact hidden-node rescaling to meet A when requested.
The graph structure stays fixed as epsilon varies. Its nonzero weights
c_i(epsilon) satisfy, for some finite C>=1 and integer K>=0,

`C^(-1)*epsilon^K <= c_i(epsilon) <= C*epsilon^(-K)`

for all sufficiently small positive epsilon. To see this, the original
weights are monomials; the cap contraction is a positive rational function;
and the rescaling uses only sums, products, ratios and maxima of finitely many
nonnegative node values. Positive quantities with upper/lower power bounds
retain such bounds under these operations. Identically zero terms are
omitted. No cancellation or unbounded oscillation is used.

For a fixed graph with S_0 weighted SUM nodes, every output monomial has
degree at most `L=max(1,S_0*2^P)` in its local coefficient slots. Unfold a
single derivation: it has at most 2^P source leaves and every SUM node
appears at most 2^P times. This retains multiplicities through sharing.

Round each c_i down to d_i=floor(2^n*c_i)/2^n. If

`2^(-n) <= eta*C^(-1)*epsilon^K`,

then `(1-eta)c_i<=d_i<=c_i`. Positivity of the graph gives, including the
fixed bases,

`(1-eta)^L*M <= M_rounded <= M`.

If L*eta<=1/2, Bernoulli's inequality and normalization imply

`||q_rounded-q||_max <= L*eta/(1-L*eta) <= 2L*eta`.

Choose epsilon=O(delta) to make the original path error <=delta/2, and
eta=delta/(4L). Then n=O(log(1/delta)); every dyadic numerator also has
O(log(1/delta)) bits by the upper power bound. Halving first and binary
Horner additions implement each d_i with O(log(1/delta)) SUMs using only
{1/2,1,2}. There are a fixed finite number of coefficient slots. No PRODUCT
is added. Downward rounding and the earlier expansion bound preserve R
and A at every finite point.

This proof includes irrational leading amplitudes. It is an existence and
resource theorem given a complete real path, not legal access to its unknown
digits. Searching for the path, acquiring values and certifying a finite
optimizer/AMP trajectory are separate problems.

## 3. A rational mesh gives a matching lower bound

Now suppose all source values are rational, with common positive integer
denominator L_s. Every node of any local-alphabet graph with budgets P,S
belongs to the lattice

`D^(-1)*Z`, where `D=L_s^(2^P)*2^(S*2^P)`.

Expand a source-to-node derivation. It has at most 2^P source occurrences,
so its source denominator divides L_s^(2^P). Every SUM contributes at
most one factor 1/2 per occurrence and occurs at most 2^P times. The local
coefficient denominator therefore divides 2^(S*2^P). Summing the finitely
many positive terms cannot increase the common denominator. Squares and
shared ancestors require the exponent 2^P: one halving followed by P squares
actually has denominator 2^(2^P).

Consequently M_(x,j)=m_(x,j)/D and T_x=t_x/D for positive integers m,t,
with t_x<=R*D. If Q is rational with common denominator B and q differs
from Q anywhere, then at some entry

`|q_(x,j)-Q_(x,j)| >= 1/(B*t_x) >= 1/(B*R*D)`.

Thus, for **every finite candidate**, either q=Q exactly or

`||q-Q||_max >= 1/[B*R*L_s^(2^P)*2^(S*2^P)]`.

This is a complete-class arithmetic bound, not a support-only argument or
a claim that all lattice points are native-realizable. It retains every
conditional normalizer and allows unbounded hidden values or SUM arity.

If Q has no exact local-alphabet realization at this P,R, a delta-accurate
candidate must therefore satisfy

`S >= 2^(-P)*log2(1/[B*R*L_s^(2^P)*delta])`.

The constant is conservative. The displayed rational mesh applies to the
exact rational data, not to arbitrary real data rounded before the claim.

## 4. Fixed algebraic data have the same lower order

Let K be the number field generated by every source and target entry, with
degree e over the rationals. These data are fixed, and the local SUM alphabet
remains {1/2,1,2}. Put d_0=2^P and t=S*d_0. Before evaluating sources, every excess
is a nonnegative polynomial of source degree <=d_0, with coefficients
`c_(j,alpha)=n_(j,alpha)/2^t`, n nonnegative integers.

There are a fixed finite number m of possible source monomials. Terms
identically zero on the complete domain contribute nothing to this static
bound. Set nu to the smaller of one and the least positive source value
(nu=1 if all sources vanish). Every visible monomial is >=nu^d_0 somewhere.
Positivity and the cap therefore give

`0<=c_(j,alpha)<=R*nu^(-d_0)`.

This coefficient bound also proves that fixed P,S,R permit only finitely
many observed mass tables even for arbitrary fixed real sources: the
finitely many visible coefficients occupy bounded dyadic lattices. No
source/provenance state is deleted by this proof about complete tables.

Write v_(x,alpha) for the source monomial values. Choose a fixed positive
integer A making all of 1, Q_(x,j), v_(x,alpha) and their products
Q_(x,j)*v_(x,alpha) algebraic integers after multiplication by A. Such an
A exists for any finite algebraic collection: if a number has an integer
minimal polynomial with leading coefficient a_d, multiplying the number
by a_d makes it integral.

If a candidate differs from Q at (x,j), the nonzero number

`zeta=A*2^t*(M_(x,j)-Q_(x,j)*T_x)`

is an algebraic integer in K. Its field norm is the product over the e
embeddings and is a nonzero integer, hence has absolute value >=1. These
standard norm facts are Theorem 4.50 and Corollary 4.52 in
[Sutherland's MIT 18.785 notes, Lecture 4](https://math.mit.edu/classes/18.785/2021fa/LectureNotes4.pdf).

Let V bound the absolute values of all embedded v, and U those of all
embedded Q. The positive coefficient bound in the original real embedding
gives, at every other embedding sigma,

`|sigma(zeta)| <= C*2^t`,
`C=A*(1+k*U)*(1+m*R*nu^(-d_0)*V)`.

The triangle inequality supplies this bound even when conjugate source
values are negative or complex. Keeping the original embedding's factor
separate in the nonzero norm then yields

`||q-Q||_max >= C_* * 2^(-e*S*2^P)`,
`C_*=1/[A*R*C^(e-1)] > 0`,

unless q=Q exactly. This is a complete-class lower bound at fixed algebraic
data, including irrational sources and targets. Constants depend on the
fixed field, all its conjugates and the complete source table. A rational
approximation to an algebraic source is a different exact claim.

## 5. A complete asymptotic trichotomy for algebraic data

For fixed algebraic sources and an algebraic target Q at finite cap R:

1. If Q is outside C_(P,R), there is a positive error gap and S_Q(delta)
   is infinite for all sufficiently small delta.
2. If Q has a finite exact local-alphabet realization, S_Q(delta) is
   eventually its minimum exact SUM count.
3. If Q belongs to C_(P,R) but has no finite exact local realization,
   `S_Q(delta)=Theta(log(1/delta))`.

For the second case, fixed P,S,R allow only finitely many observed mass
tables by the bounded visible-coefficient argument in section 4 (or the
simpler mass lattice for rational sources). This remains true with unbounded
finite SUM arity. Every smaller-than-exact SUM budget therefore has a
strictly positive distance to Q. The first case follows from the definition
of closure; the third combines the preceding upper and lower theorems.

Under uniform contexts, let excess CE be N^(-1)*sum_x KL(Q_x || q_x).
Every candidate has q_(x,j)>=1/R. The usual chi-square upper and Pinsker
lower give

`2*||q-Q||_max^2/N <= excess_CE <= k*R*||q-Q||_max^2`.

The same trichotomy holds for CE tolerance rho; its nonattained case costs
Theta(log(1/rho)). With the algebraic field degree e and constant C_* above,
its lower bound is

`S >= [e*2^(P+1)]^(-1)*log2(2*C_*^2/(N*rho))`.

For rational sources and targets, take e=1 and the sharper explicit
constant C_*=1/[B*R*L_s^(2^P)] from section 3.

The exact local-alphabet class matters. Exact realization over arbitrary
real coefficients may use irrational or otherwise nonlocal parameters;
it does not establish case 2. Conversely, an exact finite coefficient graph
must not be given a positive gap just because a different graph is singular.

There is already a one-context, zero-PRODUCT example. With source one,
target Q=(5/8,3/8) and cap R=8/3, exact prediction forces T=8/3 and excesses
(2/3,0). A single real-coefficient readout supplies them, but every finite
local-alphabet graph has dyadic excesses, even with additional PRODUCTs.
No such graph can supply 2/3 exactly. Downward dyadic approximations do
approach Q at that same cap with zero PRODUCTs and logarithmic SUM cost.
Any positive cap slack permits a dyadic T>8/3 and dyadic excesses
(5T/8-1,3T/8-1), giving finite exact zero-PRODUCT prediction. Thus exact
coefficient arithmetic alone can create an unattained minimum-cap boundary.

The cap-nine decoder at P=9,10,11 is an existing case-3 example. Its earlier
support-based lower constant is stronger, but logarithmic growth is now a
general arithmetic law rather than a special property of singleton heads.

## 6. Transcendental data can have sublogarithmic accuracy subsequences

Define the factorially sparse dyadic series

`u=sum_(m>=1) 2^(-m!)`, `u_n=sum_(m=1)^n 2^(-m!)`.

For n>=2, `0<u-u_n<2^(1-(n+1)!)` and 0<u<1. In fact u is transcendental.
If a nonzero integer polynomial F of degree d vanished at u, for all
sufficiently large n its nonzero value F(u_n) would have magnitude at least
2^(-d*n!). Bounded F' on [0,1] gives |F(u_n)|<=C_F*|u-u_n|, contradicting
the tail bound once n grows. The same applies to any nonconstant invertible
rational fractional transformation of u used below.

**Transcendental target, rational source.** On a single context with source one,
use excesses (u_n,0). They have P=0, normalizer <3, and actual local-alphabet
construction S<=2*n!+1. They approach the strictly positive target

`Q=((1+u)/(2+u),1/(2+u))`

with sup error <2^(-1-(n+1)!). Q is irrational and no finite local graph
can equal it, yet S/log(1/error) tends to zero along this sequence. A
universal Omega(log) lower bound for arbitrary real targets is false.

**Transcendental source, rational target.** Instead give the single source
a=1/(1+u) and target Q=(2/3,1/3), at cap three and P=0. Every finite local
graph has excesses (c*a,d*a), c,d nonnegative dyadics. Exact Q would imply
(c-2d)*a=1, impossible since a is irrational. Nevertheless excesses
`((1+u_n)*a,0)` have normalizer <3 and error

`a*(u-u_n)/[3*(2+(1+u_n)*a)] < 2^(1-(n+1)!)/6`.

Their SUM count is at most 2*n!+2, again sublogarithmic along the sequence.
Both examples keep every graph activation <=1. The audit encloses the
irrational quantities by exact rational intervals; it does not replace
them by rational source/target data and claim identical exactness.

## 7. Additional PRODUCTs can accelerate coefficient accuracy

The fixed-P hypothesis is also essential. Return to source one,
Q=(5/8,3/8), cap 8/3 and the missing exact dyadic excess 2/3. For n>=1,
the positive finite product

`g_n=(1/2)*product_(i=0)^(n-1) (1+4^(-2^i))`

satisfies `g_n=(2/3)*(1-4^(-2^n))`. This follows by telescoping the
geometric-product identity; the actual graph uses only positive operations.
Start g_0=1/2 and t_0=1/4 from two halving SUMs on source one. At each step
form the SUM f=(1+t)/2, the PRODUCT g*f, and the SUM 2*(g*f). Between steps,
square t with one PRODUCT. A zero SUM provides the other excess head.

The actual graph has `P=2n-1`, `S=2n+3`, local alphabet {1/2,1,2}, every
activation <=1 and normalizer <8/3. With tau=4^(-2^n), its probability
error is exactly

`delta_n=3*tau/(32-8*tau)`.

Thus both PRODUCT and SUM counts are O(log log(1/delta_n)). Exact equality
remains impossible at every finite n. This is a native tradeoff between
multiplication and value precision, not constant precision or a new source.
The exponential 2^P in the denominator bound records why fixed-P logarithmic
lower bounds permit such acceleration. The exact dyadic denominator of g_n
is 2^(2^(n+1)-1), so a direct binary significand still needs
Theta(log(1/delta_n)) bits. A small graph is not a numerical bridge or a
constant-bit-cost execution. Sharp joint (P,S) and complete-resource costs
are open.

## 8. Why the finite-cap hypothesis matters when arity is free

Use the rational source table s=(1,2) on two contexts, P=0, and the constant
positive target Q=(2/3,1/3). Only this source feeds the graph; the base one
is added at the final readout. Any finite SUM graph has excesses (c*s,d*s).
Exact realization requires `(c-2d)*s=1` at both contexts, which is impossible
even with arbitrary real coefficients.

Without a normalizer cap, set c=2n,d=n. Two SUM nodes with respectively
2n and n repeated weight-one source edges give sup error
`1/[3*(2+3n)]`, tending to zero with **constant SUM node count two**.
The normalizer maximum is 2+6n and the edge count is 3n. This falsifies
an uncapped extension with unpriced arity. A binary-SUM or edge-work budget
would charge this growth; the example is not a constant-work learner.

## 9. Audit scope and remaining research

The exact audit checks the full coefficient-perturbation inequality on shared
native graphs, rational denominator bounds with repeated squaring, exact
Q(sqrt(2)) norm bounds with irrational source/target values, explicit
same-cap local-alphabet constructions from a non-dyadic corrected decoder
path, the geometric PRODUCT precision construction, and the necessary-
hypothesis counterexamples. The specialized decoder's earlier 13k+6 SUM
upper remains stronger than the generic quantizer's constant. Supplied
graph/path verification is not complete search for the target's trichotomy branch.
Sharp constants, uniform target-dependent bounds, efficient phase/amplitude
search and registered information/value/physical/numerical paths remain open.

Audit: `theory/numerical_checks/sum_accuracy_complexity_audit.py`.
Minimal evidence: `evidence/minimal/FP_SUM_ACCURACY_COMPLEXITY_AUDIT.json`.

The follow-up `DYADIC_CAP_AND_TOTAL_COMPLEXITY.md` classifies the unrestricted-
finite-node exact/closure branches for rational targets on binary sources
and proves their sharp total-node order Theta(log log(1/error)) in the
nonattained case. Fixed-P classification and the separate-budget Pareto
frontier are not settled by that different decision class.
