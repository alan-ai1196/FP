# Finite resources behind masked PRODUCT limits

Status: **PROVED; EXACT AUDIT**, 2026-09-11.
Base: `992d7a2328908879d2ed387940b90fee7b487e0a` (XVII.16).

The previous closure theorem answers whether a given visible coefficient table
is a limit. This continuation determines its exact finite coefficient cost,
then gives a sharp PRODUCT-count / approximation / log-loss tradeoff on an
explicit static class. It does not infer physical reachability from a limit.

## 1. Fixed coefficient problem and the resource being measured

Retain the finite, declared visibility graph G and a given nonnegative table q
from `MASKED_PRODUCT_CLOSURE.md`. Assume the positive subtable S is consistent.
On each connected component C of S choose positive factors alpha_i,beta_j with
q_ij=alpha_i beta_j. Every active component contains a row and a column. Set

`A_C=max_(row i in C) alpha_i`, `B_C=max_(column j in C) beta_j`.

A vertex with no positive incident edge is inactive. It may be set to zero
for this extensional minimization: it is not a necessary exponent-bearing
component. This is not permission to erase its learner or physical state.

For each visible zero assign a positive tolerance epsilon_ij. We require

`u_i v_j=q_ij` on S, and `0<=u_i v_j<=epsilon_ij` on visible zeros.

The minimized resource is

\[
\kappa(u,v)=\|u\|_\infty\|v\|_\infty
           =\max_{i,j}u_i v_j.
\]

The maximum includes missing/annihilated pairs. It is invariant under the
single-PRODUCT rescaling `(u,v)->(s u,v/s)`. It is **not** the final normalizer,
a minimum precision, a general DAG resource, or an unspecified hardware cost.
In the explicit one-hot construction below it is the product of the two
parent activation maxima. Any bridge to a physical contract must establish
that relationship for its actual registered realization.

## 2. Exact finite optimum, including nonzero tolerances on cycles

For every zero ij between active components C,D, draw C->D with weight

`w_ij=alpha_i beta_j/epsilon_ij`.

Parallel edges and self-loops are retained. Then:

**Theorem 1.** The fixed-positive fitting problem is feasible iff every directed
cycle has product of edge weights at most one. When feasible and S is nonempty,

\[
\boxed{\kappa_*=
 \max_{P:C_0\leadsto C_l}
 B_{C_0} A_{C_l}\prod_{e\in P}w_e.}
\]

The maximum can be taken over simple directed paths, including length zero.
For S empty, kappa_*=0. All rational inputs have a rational optimum and a
rational factor witness. An inconsistent positive subtable is rejected before
this theorem; the earlier alternating-cycle certificate covers that case.

**Proof.** All factors fitting S have the form
`u_i=alpha_i t_C`, `v_j=beta_j/t_C`, with t_C>0. Zero constraints become
`t_D>=w_ij t_C`. Multiplication around a cycle proves necessity. Normalize
`max_j v_j=1`, which changes neither coefficients nor kappa. Then t_C>=B_C.
Consequently every directed path gives

`t_(C_l)>=B_(C_0) product_(e in P) w_e`,

and hence kappa>=the displayed path value. This lower bound does not require
that a missing coefficient be observable.

If every cycle has weight at most one, removing a cycle cannot decrease a
path weight. Define t_D as the maximum of `B_(C_0) product w_e` over paths
ending at D. Simple paths suffice, so these maxima are finite. They satisfy
all zero constraints and t_D>=B_D. The resulting factors have max v<=1 and
max u<=kappa_*. The path lower bound makes the achieved product exactly
kappa_*. Set inactive factors to zero. This proves attainment and optimality.
Changing the calibration within a positive component changes path weights
and endpoint factors by cancelling ratios, so the formula is calibration
independent. QED.

Synchronous multiplicative relaxation from t=B for N-1 passes, where N is
the active-component count, computes these path maxima. A remaining violated
edge supplies a closed walk with weight greater than one. Thus an exact
checker needs only actual factors plus one maximizing path, or one violating
closed walk; it need not trust a numerical optimizer's status flag. Rational
bit growth and real work must still be charged by any Runtime integration.

A weight-one cycle is feasible at that tolerance. Rejecting every cycle for
a finite-error problem would incorrectly reuse the zero-error closure test.

## 3. Sharp cost of approaching a nonclosed point

Suppose the active-component zero graph is acyclic and all zero tolerances
are epsilon. Write

`C_P=B_(C_0) A_(C_l) product_(ij in P) alpha_i beta_j`.

Theorem 1 gives the exact finite formula

\[
\boxed{\kappa_*(\epsilon)=\max_P C_P\epsilon^{-|P|}.}
\]

If L is the longest active-component path length, then kappa_*(epsilon) is
Theta(epsilon^-L) as epsilon decreases to zero. For K>=max_C A_C B_C and L>0,
the least common zero tolerance at resource K is exactly

\[
\boxed{\epsilon_*(K)=\max_{P:|P|>0}(C_P/K)^{1/|P|}.}
\]

This gives an explicit finite resource obstruction, not just nonattainment.
The smallest maximum of the two parent coefficient maxima under balancing is
sqrt(kappa). Inactive endpoints must not increase L: positive diagonal edges
00,11 with zeros 01,20,12 have kappa_*(epsilon)=1/epsilon, not epsilon^-3.
The previous all-vertex heights remain valid existence witnesses; they were
not asserted to minimize finite coefficient range.

A bounded-kappa coefficient image is closed. For kappa<=K, a nonzero pair can
be balanced to max v=1 and max u<=K; the resulting representatives lie in a
compact box. This is an existence argument, not a complete-state quotient.
It also applies to finitely many **independent parallel** PRODUCT terms with
an individual kappa cap. It does not cover arbitrary nested PRODUCT programs
or unidentified alternative observation lifts.

## 4. An observable task, with SUM backgrounds included

Fix n>=2 and the declared context domain

`X={(i,j):1<=i<=j<=n} union {(i,*):1<=i<=n} union {(*,j):1<=j<=n}`.

Its size is N=n(n+5)/2. Row indicator a_i is one when the first coordinate is
i; column indicator b_j is one when the second coordinate is j. The star is
absence of the other family, not a target-dependent source. The guard contexts
(i,*) and (*,j) are part of the declared full domain, not fabricated queries.
Their purpose is to retain, and constrain, every nonnegative unary SUM term.

The **declared comparison class** consists of a nonnegative SUM background
and at most k independent parallel products of a row SUM and a column SUM:

\[
 h(x)=c+\sum_i r_i a_i(x)+\sum_j s_j b_j(x)
 +\sum_{t=1}^{k}\Big(\sum_i u_{ti}a_i(x)\Big)
                  \Big(\sum_j v_{tj}b_j(x)\Big),
\]

with every coefficient nonnegative. The constant is allowed, so the SUM
control is not weakened by denying a constant term. Arbitrary SUM depth and
sharing computing these parents and backgrounds are covered extensionally.
Define kappa_t=max_i u_ti max_j v_tj and require kappa_t<=K, K>=1.
A scalar head weight can be absorbed into a parent for this coefficient
problem; that re-expression is not a physical/learner equivalence theorem.

Use fixed masses `M_0=1+h`, `M_1=1`, one final normalization, and cap T<=3,
i.e. 0<=h<=1. The target is h*=1 on (i,i) and zero elsewhere, giving target
probability 2/3 on the diagonal and 1/2 elsewhere. Context weights are uniform.
These are positive conditional probabilities, not a deterministic-label limit.
The frozen second head, parent-family restrictions and parallel depth are
part of the comparison class. None may be silently removed when claiming a
lower bound for the unrestricted native grammar.

**Theorem 2 (exact versus limiting count).** In this class the exact Bayes
minimum PRODUCT count is n, attainable at K=1 and T<=3. One PRODUCT nevertheless
approaches Bayes at the same final cap when its kappa is unbounded.

**Proof.** Exact guard fits force c=r_i=s_j=0. A nonnegative PRODUCT cannot
cover two diagonal contexts i<j without also being positive at the forbidden
visible context (i,j). Since there is no cancellation, n terms are necessary.
The n terms a_i b_i suffice. For the limiting one-term witness take
`u_i=epsilon^(n-i)`, `v_i=epsilon^(-(n-i))`. Its visible diagonal entries are
one, upper entries are epsilon^(j-i), and guards are zero. It satisfies h<=1
and kappa=epsilon^(-(n-1)). QED.

The guards matter. Omitting them lets additive row/column terms fit boundary
diagonal cells. The full SUM background cannot be replaced by zero in a
necessity proof without the guard argument.

## 5. All-class approximate lower bound and matching rate

For 1<=k<n set m=ceil(n/k) and L=m-1>=1. For any member of the declared class,
let e=max_x |h(x)-h*(x)|. If e<1/3, the following exact inequality holds:

\[
\boxed{K e^{m-1}\ \ge\ \big((1-3e)/k\big)^m.}
\]

**Proof.** At each row/column guard, `c+r_i<=e` and `c+s_i<=e`, so
`c+r_i+s_i<=2e`. Each diagonal has PRODUCT contribution at least 1-3e.
Choose for each diagonal a term contributing at least (1-3e)/k. Some term
owns at least m diagonal indices i_1<...<i_m. All its visible cross entries
are at most e because the total mass there is at most e and every summand
is nonnegative. In the original factors, exactly

\[
 (u_{i_m}v_{i_1})\prod_{a=1}^{m-1}(u_{i_a}v_{i_{a+1}})
       =\prod_{a=1}^{m}(u_{i_a}v_{i_a}).
\]

The reverse pair can be invisible, but its coefficient is at most K. This
proves the inequality. No exact positive-edge fit, disjoint term allocation,
or zero SUM background was assumed. QED.

It follows that every model has

\[
 e\ge d_K:=\min\left\{\frac16,
                 ((2k)^{-m}/K)^{1/(m-1)}\right\}>0.
\]

For a matching upper rate, divide the n ordered indices into k consecutive
groups of sizes at most m. In each group use the one-term construction from
Theorem 2 with its local order, setting other factor coordinates to zero.
Every diagonal is exact, each same-group off-diagonal is at most epsilon,
and all other/guard entries vanish. The peak kappa is epsilon^-L. Choosing
epsilon=K^-1/L proves that the optimal uniform mass error is

\[
\boxed{\inf e=\Theta_{n,k}(K^{-1/(\lceil n/k\rceil-1)})\quad(K\to\infty).}
\]

The displayed construction is not a claim of exact optimal constants at
finite K. The all-class lower bound allows overlapping PRODUCT supports.

## 6. Sharp cross-entropy exponent at a fixed final cap

On [0,1], `p(h)=(1+h)/(2+h)` obeys
`|p(h)-p(h*)|=|h-h*|/[(2+h)(2+h*)]>=|h-h*|/9`.
For Bernoulli probabilities, `KL(a||b)>=2(a-b)^2`: for fixed b the second
derivative in a is 1/[a(1-a)]>=4, and the value/first derivative vanish at a=b.
At a maximum-error context this gives the explicit all-class lower bound

\[
\boxed{L(h)-L_{Bayes}\ge\frac{2}{81N}d_K^2>0.}
\]

For the grouped construction all diagonal/guard predictions are exact. At
an off-diagonal with h<=epsilon,

\[
 KL(1/2\Vert p(h))
 =\tfrac12\log\left(1+\frac{h^2}{4(1+h)}\right)
 \le h^2/8.
\]

Thus its average excess is at most epsilon^2/8. Together,

\[
\boxed{\inf_{h\in\mathcal C_{n,k}(K)}(L(h)-L_{Bayes})
 =\Theta_{n,k}\!\left(K^{-2/(\lceil n/k\rceil-1)}\right),
 \qquad 1\le k<n.}
\]

For k>=n the gap is zero at K>=1. For k=0 the guard argument gives e>=1/3
and hence excess at least 2/(729N). All these statements keep T<=3 fixed.
Consequently, an actual finite intermediate coefficient/activation constraint
can turn an exact-versus-border PRODUCT distinction into a positive loss
margin. This does not prove that an arbitrary hardware cap enforces that
constraint, or that the optimizer can construct/install the better graph.

At n=8 and epsilon=1/16, the balanced one/two/four-PRODUCT witnesses require
kappa 268435456 / 4096 / 16 respectively; eight PRODUCTs attain exact Bayes at
kappa=1. All use the same final cap three. These are audited constructions,
not exact finite-K CE optimizers.

## 7. Verification, prior work and remaining boundary

`theory/numerical_checks/masked_product_budget_audit.py` supplies a rational
fixed-coefficient optimizer and independent path/cycle verifier. An exhaustive
simple-path/cycle oracle cross-checks 71,337 small input/tolerance combinations:
60,201 optimal, 9,894 infeasible, and 1,242 rejected inconsistent-positive
inputs. There are 176 finite grouped constructions, 96 perturbed examples with
inexact diagonal fits and nonzero SUM/constant backgrounds, heterogeneous
weighted tolerances, inactive-vertex and weight-one-cycle tests, and seven
forged-certificate rejections. Log bounds use exact atanh-series remainders;
float64 numbers in the JSON are display conversions, not proof boundaries.

The earlier qualitative monomial factorization/closure distinction is not
new to FP: see Geiger, Meek and Sturmfels, *On the toric algebra of graphical
models*, [arXiv:math/0608054](https://arxiv.org/abs/math/0608054). For the
rank-one partial-matrix setting and its cycle/support criteria, see Kubjas and
Metsalampi, *Geometry of low nonnegative rank matrix completion*, Section 3.1,
[arXiv:2601.07658v1](https://arxiv.org/html/2601.07658v1). This note derives its
finite-budget path formula and guarded task rate explicitly; no claim of
priority over the broader matrix-completion literature is made.

Still open: alternative observable mass/normalizer lifts with both output
heads free; unrestricted nested/mixed-parent PRODUCT grammar; general sharp
finite-K loss constants; registered acquisition/value/build/install and the
actual reference/AMP bridge. These results neither freeze the Runtime nor
remove science HOLD, and add no FP semantic primitive or architecture action.
