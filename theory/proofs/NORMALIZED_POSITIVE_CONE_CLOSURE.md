# Do not discard zero-normalizer contexts: a finite positive-cone closure theorem

Status: **PROVED**, 2026-09-06. This is a static, known-information consequence of
FP's native normalization and positivity, not a new semantic operation.

## 1. Declared finite problem

Let `X` be a finite set of contexts and `Y` a finite output alphabet. The claim
provides a known nonnegative rational source/feature table and a strictly
positive rational causal base `b_xy`. Flatten the allowed independent positive
SUM coefficients into finitely many nonnegative mass atoms `a_j(x,y)`.
For ordinary unary SUM each atom is one source routed to one output head.
More general fixed positive dictionaries are allowed, but unknown learned
factors or nonlinear/tied coefficient constraints are not silently relaxed as
an equality of physical classes.

The actual prediction family is

\[
M_{xy}=b_{xy}+\sum_j w_j a_j(x,y),\quad w_j\ge0\text{ finite},
\quad q_{xy}=M_{xy}/\sum_z M_{xz}.
\]

Introduce a **projective coordinate**, not a model action:

\[
v=(\lambda,w)\ge0,\quad
M(v)=\lambda b+\sum_jw_ja_j,\quad T_x(v)=\sum_yM_{xy}(v).
\]

Every `lambda>0` gives an actual finite model by division by `lambda`. The
extended cone also allows `lambda=0`; this is only a limit direction.
The target table `p_x` is a known rational probability vector. Deciding how it
was legally acquired, its uncertainty, and acquisition cost are separate.

For a nonempty residual context set `R`, define a rational linear feasibility
problem

\[
\boxed{\mathcal P_R:\ v\ge0,\quad
M_{xy}(v)-p_{xy}T_x(v)=0\ (x\in R,\ y\in Y),\quad
\sum_{x\in R}T_x(v)=1.}
\]

One redundant output equation per context may be omitted. An equality at a
context with `T_x=0` says **nothing** about its conditional distribution.

## 2. A single cone feasibility test is not a closure certificate

Use unary row/column indicator sources on a 3x3 context grid and binary base
`(1,1)`. Set `p_1=1/2` on row 0 or column 0, but on the interior 2x2 block set

\[
\begin{pmatrix}1/4&3/4\\3/4&1/4\end{pmatrix}.
\]

The limit direction with `lambda=0`, equal output weights on row-0 and column-0
indicators, and zero other weights satisfies every homogeneous prediction
equation. It has positive total mass on the outer row/column and zero on all
four interior cells. Normalize its total to 1: **the first LP is feasible**.

Nevertheless no sequence of normalized unary SUM models approaches the target:
its interior restriction is the separated noisy-XOR table already proved
outside the SUM closure. Discarding those four zero-normalizer cells is a false
positive certificate. This is the root FP principle in an elementary setting:
a smaller current observable erased the unresolved continuation.

## 3. Exact closure algorithm: retain the residual problem

Start with `R=X` and an empty sequence of mass directions. Repeat:

1. Solve `P_R` with certified rational feasibility comparisons.
2. If infeasible, return **outside closure**, with its linear alternative
   certificate. If the solver supplies no checkable certificate, return
   `UNRESOLVED`.
3. If feasible, retain any exact feasible `v_l`. Remove only the contexts
   `C_l={x in R:T_x(v_l)>0}`. Keep all zero-total contexts in the next `R`.
4. If `R` is empty, return **in closure** with the ordered directions.

At least one context is covered each successful round. The algorithm uses at
most `|X|` rational linear feasibility problems. **Any** feasible solution can
be used; maximizing support or branching over possible orders is unnecessary.
The layers are a proof of a limiting coefficient sequence, not FP architecture
actions and not simultaneous installed zero-mass conditionals.

**Theorem.** This algorithm decides exactly whether `p` belongs to the closure
of the actual finite prediction family. It is polynomial-time relative to an
explicit rational mass-atom table and polynomial-time rational LP algorithms.
This says nothing about the cost of acquiring/materializing that table, the
number of contexts in a succinct task, or full FP physical compilation.

### Necessity, including every residual step

Suppose a sequence of actual predictions converges to `p`. Restrict it to any
nonempty `R`. Scale each complete mass vector so `sum_R T=1`. Discard coefficient
coordinates whose atom is identically zero on **this restricted static table**;
they do not contribute to any of these equations. Every other coefficient is
bounded above by the reciprocal of its atom's positive total on `R`. There are
finitely many such coordinates, so a subsequence converges to a nonnegative
vector `v`. The normalization remains 1. Since `T_x<=1`, convergence of the
predictions implies convergence of every residual `M_xy-p_xy T_x` to zero.
Thus `v` solves `P_R`.

This holds for **every** nonempty residual set, independently of which feasible
directions earlier rounds selected. A truly approximable target can never get
stuck. The discarded atom coordinates are restored in the full witness vector;
this argument is not a quotient of a physical learner or its future behavior.

### Sufficiency and a finite positive-base approximation

Suppose the algorithm returns directions `v_0,...,v_(L-1)` covering all contexts.
Let `e_b=(1,0,...,0)` be the base direction and choose `0<epsilon<1`. Define

\[
\boxed{v(\epsilon)=\sum_{l=0}^{L-1}\epsilon^l v_l+\epsilon^L e_b.}
\]

Its base coefficient is positive, so division by that coefficient gives a
finite model with the **original fixed base**. At a context first covered at
level `l`, all earlier directions have zero total and, by positivity, zero
mass in every output coordinate. Level `l` has positive total and normalized
prediction exactly `p_x`. All later terms vanish relative to it. Hence the
finite model converges to `p` at every context.

This also gives an explicit rational error bound. At each context with first
level `l`, let

\[
C_x=\frac{\sum_{j>l}\max_y|M_{xy}(v_j)-p_{xy}T_x(v_j)|
+\max_y|b_{xy}-p_{xy}\sum_zb_{xz}|}{T_x(v_l)}.
\]

For `epsilon<=1`, denominator positivity and the first-level identity imply

\[
\boxed{\|q(v(\epsilon))-p\|_\infty\le\epsilon\max_x C_x.}
\]

All coefficients and this bound are rational when the inputs are rational.
Coefficient range/bit costs can grow rapidly as epsilon shrinks; the existence
of this finite approximation grants neither a resource-free endpoint nor
registered optimizer reachability.

## 4. Exact realization and separated impossibility

**Exact finite realization** is an even simpler LP: impose the target equations
on all contexts and `lambda>=1` instead of `sum T=1`. Homogeneity makes this
equivalent to existence of any `lambda>0`. With the fixed positive base every
normalizer is then positive. A successful closure computation is not a
successful exact-realization computation.

For an infeasible residual LP, write `A_R v=0` for the target equations and
`s_R^T v=1` for normalization. The standard linear theorem of alternatives
gives a rational vector `alpha` with

\[
\boxed{A_R^T\alpha\ge s_R.}
\]

Zero-total columns are identically zero in both sides and cause no obstruction.
This is a checkable certificate: for any nonnegative `v` normalized on `R`,
`alpha^T A_R v>=1`, contradicting `A_R v=0`.

It also quantifies separation. Group `alpha` by context/output and set
`C=max_(x in R) sum_y |alpha_xy|`. For every actual prediction `q`,

\[
1\le\sum_{x,y}\alpha_{xy}T_x(q_{xy}-p_{xy})
\le C\|q-p\|_\infty,
\]

so `||q-p||_infinity>=1/C`. In the 3x3 example, on the four interior cells
use only the class-1 equations and coefficients `(+4,-4,-4,+4)`.
The additive identities give `alpha^T A_R=s_R` exactly, hence distance at
least **1/4**. A uniform predictor attains that distance, so this obstruction
is sharp and cannot be explained away by a loose numerical tolerance.

The linear alternative used here is standard; see Boyd and Vandenberghe,
[Convex Optimization, duality and Farkas alternatives](https://web.stanford.edu/class/ee364a/lectures/duality.pdf).
The residual-context construction, limiting witness, and FP scope are proved
above rather than inferred from a generic solver's termination status.

## 5. What this resolves and what it does not

This gives a complete **static known-table decision procedure** for exact
SUM realization and approximation closure under the explicit finite positive
atom model. It supplies optimistic relaxation certificates for stricter native
construction classes. A resource-bounded finite decision, unknown-factor
acquisition, expected future value, optimizer trajectory, and complete
self-Compiler equivalence remain different problems.

No status from this mathematical procedure is `CERTIFIED_COMPLETE` for the
Reference Compiler. An external LP solver proposes primal or dual vectors;
the audit checks each vector with exact arithmetic. “Exact-arithmetic solver”
is itself not a proof of correct returned constraints.

Reproduction: `theory/numerical_checks/positive_cone_closure_audit.py`.
