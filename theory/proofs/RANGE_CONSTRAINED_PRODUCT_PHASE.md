# A sharp range-constrained PRODUCT phase, with a robust loss gap

Status: **PROVED**, 2026-09-06. This is a numerical-range-constrained static
native-program theorem, not a claim about unspecified bytes/FLOPs or a new
GPU/model-science experiment. No regularizer or architecture action is added.

## 1. Fixed task and legal class

Two binary score-time inputs have their four unary indicator sources. All
sources/SUM results have a common nonnegative scalar type with legal PRODUCT.
Graphs are finite acyclic native SUM/PRODUCT programs, with arbitrary fixed
finite nonnegative coefficients, sharing, and one final normalized readout.
The base is `(1,1)`. There is no internal normalization or adaptive recurrence.

Contexts are uniform. The strictly positive class-1 target table is

\[
p=(p_{00},p_{01},p_{10},p_{11})=(1/2,1/2,3/4,1/4).
\]

Ordinary population cross-entropy is the task objective. The **declared
numerical range constraint** is

\[
\boxed{T_{ij}=M_{0,ij}+M_{1,ij}\le R.}
\]

This cap is on the readout normalizer at the four contexts; it is not a proxy
for every intermediate activation, coefficient, memory object, or execution
cost. Each mass is at least 1. Changing the fixed base or rescaling it without
authorization changes the problem. All realization statements below still
need registered value/build/install reachability before scientific deployment.

The prior result shows this table is in the SUM-only prediction closure but
has no finite exact SUM realization. The present result resolves the finite
range cost and gives a task-forced structural property with positive margin.

## 2. Sharp SUM-only range/error tradeoff

Let `delta=||q-p||_infinity`. The least possible peak normalizer of a SUM-only
model with error at most `delta` is

\[
\boxed{
R^*_{SUM}(\delta)=
\begin{cases}
\infty,&\delta=0,\\
\dfrac{1-4\delta}{\delta(1+4\delta)},&0<\delta\le1/8,\\
\dfrac4{1+4\delta},&1/8\le\delta\le1/4,\\
2,&\delta\ge1/4.
\end{cases}}
\]

Every finite branch is attained. In particular, proximity to the closure
boundary requires an unbounded normalizer, asymptotically `R^*~1/delta`.
The ordered closure certificate is not a free bounded-range realization.

**Lower bound.** For SUM-only masses, write totals `a,b,c,d` in context order.
Both heads and their total are additive, so `a+d=b+c`. The class-1 target
residual is

\[
\tfrac12a-\tfrac12b-\tfrac34c+\tfrac14d=-\tfrac14(c+d).
\]

The actual class-1 masses have zero mixed difference. Therefore an error of
at most delta implies

\[
\delta(a+b+c+d)\ge\tfrac14(c+d),\quad
\frac{a+b}{c+d}\ge\frac{1-4\delta}{4\delta}.
\]

The minority head on each bottom context has probability at most `1/4+delta`
and mass at least 1, so `c,d>=4/(1+4delta)`. Peak normalizer is at least both
the bottom-row average and the top-row average, as well as 2. These bounds
give the displayed pieces.

**Attainment.** For `0<delta<=1/8`, put

\[
s=4/(1+4\delta),\qquad
t=s(1/4-\delta)/\delta,
\]
\[
T=(t,t,s,s),\qquad
q=(1/2+\delta,1/2-\delta,3/4-\delta,1/4+\delta).
\]

The two mass tables `T*q` and `T*(1-q)` are additive and every entry is at
least 1 (the top-row minority condition is exactly `delta<=1/8`). Subtract
the base and decompose into nonnegative row/column SUM terms. For
`1/8<=delta<=1/4`, use the same column predictions `3/4-delta,1/4+delta`
on both rows, all totals `s`. For `delta>=1/4`, the empty graph suffices.

Even this small rational-input problem can have an irrational optimal error.
For `R>=8/3`, inversion gives

\[
\delta^*_{SUM}(R)=
\frac{\sqrt{(R+4)^2+16R}-(R+4)}{8R}.
\]

At `R=4`, this is `(sqrt(2)-1)/4`. A finite encoded implementation must use
exact algebraic comparison or sound enclosures; a decimal tolerance does not
turn the irrational relaxed optimum into an exactly constructed state.

## 3. A lower bound for the entire one-PRODUCT grammar

With at most one semantic PRODUCT, its two parents contain only SUM and unary
sources. Call its nonnegative output table `h`. Arbitrarily many later SUMs,
sharing, and output routes still give

\[
M_y=1+u_y(i)+v_y(j)+c_y h_{ij},\qquad c_y\ge0.
\]

Define the mixed difference `Delta f=f_00+f_11-f_01-f_10`. Then

\[
\boxed{\Delta M_0\,\Delta M_1\ge0,}
\]

because `Delta M_y=c_y Delta h`. This necessary condition covers **every**
one-PRODUCT DAG in the contract, including PRODUCTs of cross-input SUMs. It
does not assume the PRODUCT is a particular corner indicator.

For exact target probabilities, positivity gives `a,b>=2`, `c,d>=4`. The
same-sign condition requires at least one of

\[
\Delta M_1=\tfrac12(a-b)-\tfrac34c+\tfrac14d\ge0,
\]
\[
\Delta M_0=\tfrac12(a-b)-\tfrac14c+\tfrac34d\le0.
\]

Under `a,b,c,d<=R`, the first left side is at most `3R/4-4`; the second is
at least `4-3R/4`. Consequently

\[
\boxed{\text{exact one-PRODUCT realization requires }R\ge16/3.}
\]

## 4. Native witnesses attaining both structural thresholds

Write `x_0,x_1,z_0,z_1` for the declared partition atoms.

**Two PRODUCTs, peak normalizer 4:**

\[
M_0=1+2x_1z_1,\qquad M_1=1+2x_1z_0.
\]

The mass pairs are `(1,1),(1,1),(1,3),(3,1)` and match the target exactly.
No architecture can match it with `R<4`, because the bottom minority probability
is 1/4 while its mass is at least 1.

**One PRODUCT, peak normalizer 16/3:**

\[
h=(x_0+z_1)(3x_1+\tfrac53z_0),
\]
\[
\boxed{M_0=1+h,\qquad M_1=1+\tfrac13x_1+\tfrac53z_0.}
\]

Its mass pairs are `(8/3,8/3),(1,1),(1,3),(4,4/3)`. Here `h` is one PRODUCT
of two legal positive SUMs; the partition identities make it zero at the two
off-diagonal contexts. A search restricted to corner PRODUCTs would miss this
sharp witness and report an artificially large required range.

Thus the exact minimum PRODUCT count among Bayes-optimal native realizations is

\[
\boxed{
\begin{cases}
\text{no Bayes realization},&R<4,\\
2,&4\le R<16/3,\\
1,&R\ge16/3.
\end{cases}}
\]

At `R>=16/3`, two-PRODUCT optima remain feasible too. It is the property
“every optimum has at least two PRODUCTs” that ceases to be forced. A
one-PRODUCT tie-break is not universally forced. The result provides an
explicit native example of why relaxed caps need not make required optimal
structure grow monotonically.

## 5. Positive margin, not just failure of exact attainment

For `4<=R<16/3`, every at-most-one-PRODUCT model obeys

\[
\boxed{\|q-p\|_\infty\ge d_R:=\frac{16-3R}{48+16R}>0.}
\]

To prove it, suppose the actual error is delta. The bottom totals are at least
`4/(1+4delta)`. A class-1 mixed difference differs from its target-weighted
mixed difference by at most `4R delta`. Thus the first same-sign alternative
requires

\[
0\le3R/4-1-3/(1+4\delta)+4R\delta
\le3R/4-4+(12+4R)\delta.
\]

The other alternative is symmetric. Rearrangement yields the bound. This
separation is sufficient, not asserted to be the sharp one-PRODUCT error curve.

For binary probabilities, `KL(p||q)>=2(p-q)^2` follows by integrating the
second derivative `1/[p(1-p)]>=4` in the first argument about its minimizer
`p=q`. At a context attaining the sup-norm error, uniform context weight 1/4
therefore gives excess cross-entropy at least `d_R^2/2`.

At `R=4`, `d_R=1/28`, so every at-most-one-PRODUCT model has excess loss
at least **1/1568 nats** over the two-PRODUCT Bayes witness. Hence, if that
witness is registered and reachable, every epsilon-optimal target for
`epsilon<1/1568` has at least two semantic PRODUCTs. The entire excluded
grammar is controlled, not just a finite hand-selected baseline menu.

## 6. Interpretation and audit boundary

This closes a concrete gap between unconstrained positive expressivity and a
finite registered numerical envelope. The loss-gap result survives arbitrary
SUM depth/sharing and arbitrary legal one-PRODUCT parents. It is not an
optimizer-throughput experiment, a hardware memory theorem, or proof that a
particular learner reaches either witness. The readout-normalizer cap must be
declared before evaluating the claim; it cannot be invented post hoc to rescue
an empirical architecture comparison.

Exact audit: `theory/numerical_checks/range_product_phase_audit.py`, with
symbolic identities, rational tradeoff witnesses, an algebraic optimum enclosure,
and random native PRODUCT-of-SUM controls. GPU/model science remains HOLD.
