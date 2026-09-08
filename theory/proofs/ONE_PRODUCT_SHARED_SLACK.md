# Exact one-PRODUCT sharing, and a multiclass range obstruction

Status: **PROVED**, 2026-09-08. The mixed-difference sign invariant was only
necessary. This identifies its missing common nonnegative slack and derives
a complete static mass-table decision class without a new model action.

## 1. Exact criterion for a fixed mass table

Use two binary inputs, unary indicator sources, base 1 in each of k outputs,
fixed nonnegative SUM coefficients, at most one semantic PRODUCT, and one final
normalization. No recurrence, internal normalization or enriched source is
allowed. The input to this theorem is the **full mass table** M_xy>=1 at the
four contexts, not only its normalized probabilities.
Arithmetic nodes in this decision class are scalar. Batching several scalar
products does not identify their semantic nodes; a vector-valued primitive
with additional outputs would require a different explicit count theorem.

Let `E_y=M_y-1` and `Delta_y=E_y(00)+E_y(11)-E_y(01)-E_y(10)`.

* If all Delta_y vanish, a SUM-only realization exists.
* If nonzero Delta_y have different signs, one PRODUCT is impossible.
* Otherwise let sigma be their common sign, `d_y=sigma Delta_y>0` for active
  heads, and take `(s_0,s_1)=(00,11)` for sigma=+1 or `(01,10)` for sigma=-1.
  Define

\[
H_i=\min_{y:d_y>0}\frac{E_y(s_i)}{d_y},\quad i=0,1.
\]

Then the remaining exact criterion is

\[
\boxed{\text{one shared PRODUCT realizes M iff } H_0+H_1\ge1.}
\]

All comparisons and the construction below are rational for rational masses.
This is a complete known-mass decision, not a completeness claim for unknown
conditional scales, registered value dynamics, or physical implementation.

## 2. Necessity and a derived native normal form

Every one-PRODUCT DAG has output excess `E_y=A_y+c_y h`, where A_y is a
nonnegative unary-additive table, c_y>=0 and h>=0 is the PRODUCT's table.
Therefore `Delta_y=c_y Delta h`. On each active head,
`E_y/d_y>=h/|Delta h|` pointwise. Summing on the sign's two corners gives

\[
H_0+H_1\ge\frac{h(s_0)+h(s_1)}{|\Delta h|}\ge1.
\]

Conversely, choose any rational
`max(0,1-H_1)<=a<=min(1,H_0)`. Put h=a at s_0, h=1-a at s_1, and zero on
the other two contexts. This table is one native PRODUCT of two SUM parents:

\[
h_+=[a x_0+(1-a)z_1](x_1+z_0),\qquad
h_-=[a x_0+(1-a)z_0](x_1+z_1).
\]

Complementary indicator products vanish throughout the declared input domain.
For each active head set `c_y=d_y`; for zero-difference heads use c_y=0.
Then `A_y=E_y-c_y h` is nonnegative and has zero mixed difference. Any such
2x2 table is a nonnegative sum of row/column indicator contributions: subtract
each row minimum, leaving the same nonnegative column vector in both rows.
This constructs every output mass exactly.

The two sign cases follow from a proved invariant; they are not a handpicked
architecture menu. This normal form preserves the four mass values and final
normalizers. It does **not** preserve original provenance, optimizer derivatives,
registered value reachability, storage/sharing, build cost or legal future
continuations, and cannot authorize a runtime graph replacement by itself.

## 3. A minimal false sign certificate

Take `E_0=(1,0,0,0)` and `E_1=(0,0,0,1)`. Both mixed differences are +1,
yet both common H values are zero. Each head individually needs only one
PRODUCT; their disjoint nonlinear support cannot share that PRODUCT.

This does not exclude another SUM model with the same probabilities after
changing masses. For example the target probabilities `(1/3,1/2,1/2,2/3)`
admit constant-total SUM masses `(2-(x+z)/2,1+(x+z)/2)`. Fixed mass and
conditional representability are different decision classes.

## 4. A four-label task separates the sign relaxation from the actual class

Index the four labels by the four contexts and take

\[
p_y(x)=\frac{1+1[x=y]}5.
\]

The base is `(1,1,1,1)`, contexts are uniform, and the declared cap is T_x<=R.
All exact predictions require T_x>=5 because the three off-diagonal masses
are at least 1. Thus the unrestricted minimum range is 5.

Write `(u,b,c,v)=(T_00,T_01,T_10,T_11)` and `D=u+v-b-c`. The output mixed
differences are `(D+u,D-b,D-c,D+v)/5`. Consider the all-nonnegative sign case;
the all-nonpositive case is equivalent by a context flip and label permutation.
The sign condition requires `D>=max(b,c)` and hence `b+c<=2(u+v)/3`.
It alone has sharp minimum cap **15/2**: use u=v=15/2 and b=c=5.

For a genuine one-PRODUCT model the two diagonal-label heads also require

\[
\frac{u-5}{D+v}+\frac{v-5}{D+u}\ge1.
\]

These are upper bounds on the common H values, so the inequality is necessary.
With `S=u+v` and `D>=S/3`, clearing positive denominators yields

\[
8u^2-11uv+8v^2-75u-75v\ge0.
\]

This quadratic is convex. On `5<=u,v<=R` its maximum is attained at a rectangle
vertex. At `(5,R)` its value is `8R^2-130R-175`, whose positive root is 35/2;
at `(R,R)` it is `5R(R-30)`, and at `(5,5)` it is negative. Therefore no
one-PRODUCT realization exists for R<35/2.

The bound is attained: take `(u,b,c,v)=(5,15/2,15/2,35/2)` and M_xy=T_x p_y(x).
The output differences are `(5/2,0,0,5)` and the shared-slack criterion holds
with a=0, so h=x_1 z_1 constructs the table exactly. Consequently

\[
\boxed{R_{sign\ relaxation}=15/2\quad\text{but}\quad R_{one\ PRODUCT}=35/2.}
\]

The older unbounded one-PRODUCT universality theorem remains true; it did not
promise either of these resource costs. The range gap is a counterexample to
upgrading the necessary sign invariant into a complete candidate certificate.

## 5. At cap five, all four PRODUCT nodes are forced

At R=5 the same target forces T_x=5 everywhere, hence `E_y(x)=1[x=y]`.
Flatten only SUM paths at the readout of an arbitrary native graph with P
PRODUCT nodes. Its excess table is

\[
E=A+HC,
\]

where A is nonnegative unary-additive, H contains the tables of its PRODUCT
nodes, C>=0 contains their output coefficients, and `rank(HC)<=P`. PRODUCT
dependencies and sharing are permitted; unused columns simply have zero
output coefficients. Every unary source contributing at a label's own context
also contributes at another context, so `A_jj<=sum_(i!=j) A_ij`.

For E=I, positivity forces all off-diagonal contributions of A to zero and
therefore its diagonal to zero too. Thus HC=I and P>=4. Four direct context
indicator PRODUCTs attain the cap. The exact minimum at R=5 is therefore
**four semantic PRODUCT nodes**, despite unbounded one-PRODUCT universality.
No exact phase for two versus three PRODUCTs at intermediate caps is claimed.

The lower bound is robust. If every predicted probability is within delta of
the target at cap 5, then `T_x>=5/(1+5delta)`. Every column of E has surplus

\[
E_{jj}-\sum_{i\ne j}E_{ij}
\ge\frac{1-25\delta-75\delta^2}{1+5\delta}.
\]

At delta<=1/28 this is positive. Subtracting A cannot reduce this surplus, so
HC is nonnegative and strictly column-diagonally dominant, hence nonsingular.
(Apply the maximal-coordinate argument to `(HC)^T z=0`.) Thus P>=4 still.
For every at-most-three-PRODUCT model,

\[
\boxed{\|q-p\|_\infty\ge1/28,\qquad L(q)-L_{Bayes}\ge1/1568.}
\]

The loss bound uses uniform contexts, multinomial Pinsker, and
`||p_x-q_x||_1>=2||p_x-q_x||_infinity`. It covers arbitrary compound parents
and sharing, not merely a four-corner architecture menu.

## 6. The rank obstruction extends to arbitrary input dimension

For d>=2, N=2^d contexts and N labels, use target `(1+1[x=y])/(N+1)` and cap
N+1. The same argument forces at least N PRODUCT nodes. Unary sources support
at least two contexts, and the final excess matrix is I_N. A balanced recursive
construction of all context indicators uses `P(1)=0` and
`P(d)=2^d+P(floor(d/2))+P(ceil(d/2))`; this is an upper bound, not a sharp count
for d>2. At d=2 both bounds are four.

The general robust exclusion holds at
`delta=1/[(N+1)(N+2)]`: writing t=(N+1)delta, the diagonal surplus is bounded
below by `[1-(N+1)t-(N-1)t^2]/(1+t)>0`. Thus the excluded P<N class has CE
gap at least `2/[N(N+1)^2(N+2)^2]`. Its output alphabet grows with N and its
risk margin shrinks; this is not a dimension-independent practical LM result.

All constructions here are finite algebraic witnesses. Initializers, profile
optimization, information acquisition, physical costs, fresh persistence and
AMP installation still require their original evidence. The fixed base and
source contract cannot be silently changed to defeat these lower bounds.

Exact complete-mass enumeration and constructive audits:
`theory/numerical_checks/one_product_shared_slack_audit.py`.
