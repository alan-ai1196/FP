# Observable PRODUCT closure on an antipodal zero face

Status: **PROVED**, 2026-09-11. Alternative coefficient lifts can be resolved
completely for this scalar mass class. Three inputs give a positive-cone
universality result; four already give a robust two-PRODUCT task. This is a
static real-arithmetic theorem, not a complete Runtime certificate.

## 1. Class and the zero-face reduction, including leaking sequences

Use the full binary cube, d>=2, with scalar unary indicators x_i and 1-x_i.
An excess mass built with at most one PRODUCT is

`g=A+UV`,

where A,U,V are nonnegative sums of these indicators. This includes arbitrary
finite SUM depth, sharing, nonnegative readout weights and SUM-only graphs.
Consider a nonnegative target f with f(0)=f(1)=0. Define the directed-cut map

`B(q)(x)=sum_(i!=j) q_ij x_i(1-x_j)`, q>=0.

Let G be the complete d-by-d bipartite graph with its diagonal removed.
Then

**Zero-face theorem.** f is in the closure of the full A+UV mass class iff
f=B(q) for a q in the visible rank-one closure on G. Exact realization holds
iff such a q has a finite nonnegative factorization.

For exact masses, A vanishes at both antipodes and therefore identically.
A nonzero nonnegative unary function cannot vanish at both antipodes. After
exchanging parents, U vanishes at 0 and V at 1, giving U=sum a_i x_i and
V=sum b_j(1-x_j), as required.

The closure argument must not assume the approximants vanish at the two
antipodes. Expand a convergent A_n+U_n V_n into its unary and ordered literal-
pair coefficients. Every visible coefficient is bounded, since its atom
equals one at some context and all contributions are nonnegative. Pass to
a common subsequence. The additive coefficients and all same-polarity pair
coefficients converge to zero, by evaluation at the antipodes.

Positive coefficients of both cross-polarity orientations cannot survive.
Indeed, if the limits of u_(i,1)v_(j,0) and u_(k,0)v_(l,1) were positive,
the exact identity

`[u_(i,1)v_(j,0)] [u_(k,0)v_(l,1)]`
`= [u_(i,1)v_(l,1)] [u_(k,0)v_(j,0)]`

would have a positive left limit and zero right limit. Both right-hand atoms
are visible, including when their coordinate indices coincide. Thus at most
one orientation survives. Its off-diagonal block is a limit of visible
rank-one matrices and gives f=B(q). The converse inserts the factor sequence
of `MASKED_PRODUCT_CLOSURE.md`. Contradictory same-coordinate atoms remain
identically zero; their coefficients need not be bounded.

## 2. Margins select exactly one closure coefficient table

For any finite bipartite mask G and feasible nonnegative margins r,c, the
transportation polytope is

`P(r,c)={q>=0 on G: sum_j q_ij=r_i, sum_i q_ij=c_j}`.

It is compact. There is **exactly one** member q* in the visible rank-one
closure. Equivalently q* uniquely maximizes

`H(q)=-sum_(ij in G) q_ij log q_ij`, with 0 log 0=0,

over this polytope. Entropy here characterizes the inverse of the margin
map. It is not added to the FP loss or used as a model regularizer.

Here is a boundary-safe proof using the previous graph criterion. Strict
concavity gives a unique entropy maximizer. Its positive support S contains
every edge positive in any feasible table: opening a missing edge along a
feasible segment gives a positive `-t log t` term that dominates the O(t)
change on the old support. Stationarity along positive alternating cycles
then gives positive-edge factor consistency.

The directed zero-edge component graph must be acyclic. Otherwise add a
small common amount on a directed cycle's zero edges and balance those
changes along positive paths inside the components. Alternating signed
changes on each such path preserve every row and column total; sufficiently
small changes keep all old positive entries nonnegative. This would open
an edge outside the maximal feasible support. The graph theorem therefore
places the maximizer in coefficient closure.

Conversely, take any closure point q in P(r,c). Its graph heights give row
potentials h_i and column potentials k_j with h_i+k_j=0 on its positive
support and h_i+k_j>0 on every visible zero. Every w in P(r,c) has the same
potential sum as q, namely zero, so w must vanish outside that support.
On the support log q_ij=log alpha_i+log beta_j. Consequently

`sum w_ij log q_ij = sum q_ij log q_ij`.

The generalized KL inequality, and equal total mass, now give H(w)<=H(q),
with equality only for w=q. This proves uniqueness, including all boundary
and zero-total cases, without assuming finite factors at a boundary point.

This is the bipartite specialization of the known toric moment-map/Birch
theorem. See Simon Telen, [Positive Toric Geometry](https://www.math.kobe-u.ac.jp/cm/koen/PTG.pdf),
Theorems 2.9 and 3.1, for the general homeomorphism and entropy interpretation.
The FP application below uses which margins the *observable mass* retains.

## 3. Complete observable criterion in every dimension

For an input table f on the declared cube, let

`r_i=f(e_i)`, `c_i=f(1-e_i)`.

If f=B(q), these are exactly the row and column margins of q. First check
P(r,c) is nonempty. Form its unique closure member q*. Then

`f is in one-PRODUCT mass closure iff B(q*)=f at every context`.

When equality holds, exact realization is equivalent to the finite-factor
support criterion for q*: every visible edge between an active row and an
active column must be positive. Thus no alternate coefficient lift is lost.
In particular, if a checked closure table has the prescribed margins but
the wrong observed mass, it rejects **every** lift, not only itself.

This is a complete mathematical characterization. A numerical entropy or
matrix-scaling residual does not by itself certify an exact decision. The
audit implements a complete rational-table decision for d=3 and a verifier
for supplied rational q* in any d. General algebraic root isolation or an
efficient complete arbitrary-d search is not implemented.

## 4. Three inputs: the entire positive cut cone is in one-PRODUCT closure

When d=3 the non-antipodal contexts are exactly the three singletons and
their complements. Margins therefore determine *the whole mass table*.
Every nonnegative directed-cut combination is in one-PRODUCT closure.

For rational f this gives a particularly small exact decision. Require
sum r=sum c. All off-diagonal tables with these margins have, for one t,

```
q_01 = t                         q_02 = r_0-t
q_12 = r_1-c_0+r_2-c_1+t         q_10 = c_0-r_2+c_1-t
q_20 = r_2-c_1+t                 q_21 = c_1-t.
```

Write the forward triple as t+a_i and the reverse triple as b_i-t. Its
feasible interval is L=max_i(-a_i), U=min_i b_i. If L>U the table is outside
even the positive cut cone, hence outside one-PRODUCT closure. The moment
imbalance sum r!=sum c also excludes closure. Equivalently cone membership
is r,c>=0, equal total W, and r_i+c_i<=W for each i; the interval gives a
direct proof in this three-by-three case.

If L<U, all six entries are positive in the open interval. The sole simple
cycle equation is

`Phi(t)=product_i(t+a_i)-product_i(b_i-t)=0`.

Phi is strictly increasing on (L,U), Phi(L)<0 and Phi(U)>0. Its unique root
lies strictly inside and gives a finite positive factorization. These exact
rational endpoints already certify existence and uniqueness of the real
root; a bisection enclosure is only a numerical approximation to its value.

If L=U, the unique feasible coefficient table is rational. Both alternating
cycle products vanish, so it lies in closure; the graph support criterion
decides whether it is exact or limit-only. This covers f=0 as well.

One originally supplied coefficient table can violate the cycle equation
while its observable table is exactly realizable by a different lift. For
example take r=(2,3,4), c=(3,3,3) and the endpoint t=0 above. Its two cycle
products are 0 and 12. The correct lift instead has t equal to the root in
(0,2) of

`2t^3-5t^2+17t-12=0`.

The rational-root theorem excludes every rational root. Thus this rational
mass table has an exact real one-PRODUCT representation but **no exact
rational-coefficient one-PRODUCT representation**. Finite rational
approximations remain possible. Real existence must not be promoted to
registered finite-encoding value reachability.

## 5. Four inputs: two independent XOR masses have a robust separation

Let

`f(x)=(x_1+x_2)(2-x_1-x_2)+(x_3+x_4)(2-x_3-x_4)`.

Each factor `2-x_i-x_j` means the native positive SUM
`(1-x_i)+(1-x_j)`. Hence f is the sum of two legal PRODUCTs, with values 0,1,2.
Its antipodal singleton/complement margins are r=c=(1,1,1,1). Their unique
closure coefficient table is q*_ij=1/3, i!=j, whose observed values are
`|x|(4-|x|)/3`. At x=1100 this is 4/3 whereas f=0. The observable criterion
therefore excludes the entire one-PRODUCT mass closure.

There is also a direct quantitative proof:

`inf_(A,U,V>=0 unary) ||A+UV-f||_infinity >= 1/7`.

Let Z={x:x_1=x_2, x_3=x_4} and suppose the displayed error is delta. At Z,
g=A+UV<=delta. In the positive literal expansion, the only visible PRODUCT
atoms identically zero on Z are the two orientations of XOR within each of
the two coordinate pairs. Call these signal atoms. Every other visible
PRODUCT atom has uniform-Z mean at least 1/4, and every unary atom has mean
1/2. Positivity thus bounds the sum of all non-signal and additive
coefficients by 4 delta. Their contribution at any context is at most
4 delta. Each individual non-signal PRODUCT coefficient is at most delta,
since its atom equals one at some Z context.

At a context where only the first pair has XOR=1, its signal coefficient
(the sum of the two ordered-parent orientations) is at least 1-5 delta.
The same is true for the second pair. If delta<1/5, select an ordered signal
coefficient from each pair of size at least (1-5 delta)/2. Rank-one
multiplication equates their product to the product of two cross-pair
coefficients. Both cross-pair atoms are visible non-signals, so

`((1-5 delta)/2)^2 <= delta^2`.

Hence delta>=1/7. If delta>=1/5 the conclusion already holds. This bound
allows all unary remainders, all parent coefficients and arbitrary SUM
graphs; it does not require exact zeros or bounded hidden coefficients.

## 6. A conditional task with a positive all-one-PRODUCT CE gap

Use uniform four-bit contexts, base (1,1), target

`p_1(x)=(1+f(x))/(2+f(x))`, final cap T<=4.

The two-PRODUCT masses (1,1+f) reach Bayes risk. Every at-most-one-PRODUCT
conditional model has

`||q_1-p_1||_infinity > 1/500`,
`L(q)-L_Bayes >= 1/2000000` nats.

The following proof retains both heads and every normalizer. Normalize the
shared product readout so that

`E_0=A_0+theta h`, `E_1=A_1+(1-theta)h`, 0<=theta<=1,

with h a PRODUCT, A_y nonnegative unary, E_y=M_y-1 and h<=2 from the cap.
For a SUM-only graph use h=0. Suppose prediction error delta<=1/500.
At D={x:x_1!=x_2,x_3!=x_4}, the target is 3/4; the cap and base give

`E_0<=4 delta`, `E_1>=2-16 delta`.

Every coordinate is balanced on both D and Z. Consequently A_0(x)<=8 delta
everywhere, and the averages of A_1 on D and Z agree. At Z the target is
1/2, so E_1<=1+4 delta. Averaging on D therefore gives

`(1-theta) average_D h >= 1-20 delta`,
`theta average_D h <= 4 delta`.

Multiply and combine to obtain theta(1-16 delta)<=4 delta, and thus

`E_0(x)<=B(delta):=8 delta+8 delta/(1-16 delta)`.

Now M_1=M_0 q_1/(1-q_1), while 1+f=p_1/(1-p_1). Since p_1<=3/4,

`||E_1-f||_infinity <=`
`[16 delta+B(delta)(3+4 delta)]/(1-4 delta)`.

The right side is increasing on [0,1/500]. Exact rational evaluation at
1/500 is less than 1/7, contradicting the scalar mass bound. Finally a
context with probability error >1/500 has Bernoulli KL >2/(500^2).
Its uniform context weight is 1/16; nonnegative KL at the other contexts
gives the stated CE lower bound. Thus the exact Bayes minimum is two, and
this time the one-PRODUCT infimum is also separated from Bayes risk.

These conservative constants are not claimed sharp. The comparison is
against the full static one-PRODUCT class, including the full SUM class.

A float64 local search was used adversarially as a proposal, then simplified
to an exact rational one-PRODUCT control. In literal order
`(1-x1),x1,(1-x2),x2,(1-x3),x3,(1-x4),x4`, it uses

```
A0 = (0,7/400,77/400,0,0,0,0,0)
A1 = (83/200,0,0,1/50,0,0,0,0)
U  = (0,1/15,1/15,0,0,13/30,0,13/30)
V  = (0,3/8,3/8,0,12/5,0,12/5,0).
```

Masses `(1+A0,1+A1+UV)` satisfy the cap exactly. Rational log enclosures
place their CE excess in `(0.00889241107354,0.00889241107355)` nats.
This is a checked feasible upper witness for the one-PRODUCT optimum;
local optimization has not certified that optimum. The substantial space
between the lower and upper bounds leaves a meaningful sharp-loss problem.

The separation is not deployment forcing without registered value construction, resource
ownership, fresh persistence, installation and the reference/AMP bridge.

Exact audit: `theory/numerical_checks/antipodal_product_mass_audit.py`.
