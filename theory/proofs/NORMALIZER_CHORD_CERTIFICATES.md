# Quadratically tight normalizer bounds for global positive-cone loss

Status: **PROVED certificate family**, 2026-09-08. This strengthens the global
static solver of XVII.9 where finite normalizer bounds follow from the declared
linear coefficient domain. It changes solver bounds, not the FP class.

## 1. Keep the common masses instead of separating their predictions

Use the same rational positive mass model, counts c and total C as XVII.9.
Let `n_x=sum_y c_xy`. In a normalizer box `l_x<=T_x<=u_x`, with `l_x>0`,

\[
C L(w)=\sum_x n_x\log T_x-\sum_{xy}c_{xy}\log M_{xy}.
\]

The second term is convex in the common coefficients w. The only concave term
is the log of the shared normalizer. For l<u its chord

\[
h_{l,u}(T)=\frac{u-T}{u-l}\log l+\frac{T-l}{u-l}\log u
\]

satisfies `h<=log T`. Replacing each log T by its chord gives a **convex lower
relaxation on the original mass cone and original coefficient constraints**.
No independently chosen probability table or altered graph class is installed.

Moreover, elementary interpolation error and `|log'' T|<=1/l^2` give

\[
0\le\log T-h_{l,u}(T)\le\frac{(u-l)^2}{8l^2}.
\]

The mean-CE relaxation error is therefore at most
`sum_x (n_x/C)(u_x-l_x)^2/(8l_x^2)`. It shrinks quadratically in relative
normalizer-box width, rather than the generic likelihood box Lipschitz bound.

## 2. An entirely rational certificate

Obtain certified rational endpoint lower bounds `L_l<=log l`, `L_u<=log u`.
Their affine chord `alpha T+beta` is still below log T. If l=u, use the
constant lower bound there. At any rational support masses `s_xy>0`, convexity
gives

\[
-\log M_{xy}\ge 1-U_{s_{xy}}-M_{xy}/s_{xy},\qquad U_s\ge\log s.
\]

The support masses need not be a feasible model: they define tangent planes,
not an initializer or installed endpoint. Combining these inequalities yields

\[
C L(w)\ge k+g^T w,
\]

where k,g are reconstructed exactly from the atom/base table, counts, chord
endpoints, support masses and log enclosures. Thus a verified linear dual can
certify the convex relaxation without trusting the numerical optimizer.

Write all original and normalizer-box inequalities as `A w<=b`, w>=0. For a
rational y<=0, let `d_j=max((A^T y)_j-g_j,0)`. Every atom which is nonzero has
a proved finite coefficient upper bound

\[
W_j=\min_{x:\sum_y a_j(x,y)>0}
\frac{u_x-\sum_y b_{xy}}{\sum_y a_j(x,y)}.
\]

Positivity of all other contributions proves this bound. For an identically
zero atom whose coefficient is not bounded this way, require d_j=0 exactly;
do not erase its original constraint columns. Then

\[
\boxed{L(w)\ge [k+b^T y-\sum_j d_j W_j]/C.}
\]

Indeed `g^T w>=(A^T y)^T w-sum d_j W_j>=y^T b-sum d_j W_j`.
This is an explicit dual-residual correction, not tolerance-based acceptance.
The numerical LP need not return an exactly feasible dual for its unrounded
gradient. Every residual is charged using a justified finite bound, or the
certificate is rejected. Taking y=0 always provides a sound fallback for
these support planes. Loss nonnegativity may further raise a negative lower
bound to zero.

Omitting the correction is concretely false. With one context, masses `(1+w,1)`,
counts `(3,1)`, `0<=w<=2`, normalizer interval `[2,4]`, support masses `(1,1)`
and y=0, the uncorrected scalar bound is approximately log2. But w=2 predicts
the empirical Bayes distribution `(3/4,1/4)` with strictly smaller entropy.
The negative coefficient gradient must be minimized or charged against w<=2;
calling y a dual certificate does not remove that obligation.

## 3. Sound reference logarithms

For rational z>0, first write `z=2^k r`, `1<=r<2`. The rational atanh series

\[
\log r=2\sum_{j=0}^{m-1}\frac{t^{2j+1}}{2j+1}+e,\quad
t=(r-1)/(r+1),\quad
|e|\le\frac{2|t|^{2m+1}}{(2m+1)(1-t^2)}
\]

and the same series at 2 enclose `log z=k log2+log r`. Negative k reverses
the corresponding endpoint choice. Round the final interval outwards on a
declared dyadic grid. The actual rational enclosure is checked; float64 log
values only guide proposals. No AMP bridge follows from this reference bound.

## 4. Global search and completeness scope

The search starts from finite normalizer caps established by original linear
rows (or by an identically constant total). Each node retains all original
constraints and adds its normalizer interval inequalities. Exact primal/Farkas
checks establish finite feasibility. Convex optimization proposes support
masses; a linear LP proposes dual multipliers. The independent verifier
reconstructs and checks the complete rational lower bound above.

Keep a finite feasible witness and an outward CE upper for it. Bisect a widest
relative normalizer interval when its verified lower does not meet the declared
absolute accuracy epsilon. Every leaf must either be exactly infeasible or
have lower at least `witness_upper-epsilon`. The verifier reconstructs both
closed children and the root domain, and takes epsilon as an external argument.
It never accepts a node's stated numerical optimum or an uncorrected dual.

With certified arbitrarily accurate inner convex solves, finite termination
follows from the quadratic chord error and longest-relative-width bisection.
Such inner solves are effective: on the bounded mass intervals, replace each
`-log M` by a maximum of rational tangent lower planes on successively finer
grids, then solve the resulting rational epigraph LP. Tangent error is at most
`(M-s)^2/(2 b_xy^2)` plus its measured log-enclosure width. This supplies any
requested uniform accuracy with finitely many planes and an exact LP oracle.
Both the tangent grid and the log-series precision must be refined in that
completeness construction; a fixed 16-term/48-bit fast-path enclosure is not
an arbitrary-precision oracle.

The fast executable path uses proposed support/dual pairs instead of asserting
that a numerical convex optimizer implements that completeness oracle. Missing
certificates, unsupported finite caps or work exhaustion return UNRESOLVED.
The existing XVII.9 solver remains the independent complete approximation
construction for the broader unbounded-coefficient class.

## 5. What the comparison measures

Both solvers are checked on the identical cap-four normalized unary-SUM XOR
class, counts and positive base. The older probability-box proof requires
43,023 nodes for a CE width below 0.006 nats. The new certificate must meet
the stricter rational epsilon=1/200 while retaining the whole same class.
Node counts and exact bound widths are reported by the audit, not predicted
by this theorem. This is a solver study, not a GPU/model-science result or a
physical Compiler budget. Local proposal bounds never restrict global coverage.

The checked run closes at 87 nodes, with width below 0.00448 nats. A second
run at epsilon=1/1,000,000 closes at 551 nodes and proves the conservative
decimal interval `0.68483177<=inf L<=0.68483253`. These are full-class bounds,
not local optimizer error estimates or an exact closed-form optimum. Node
reduction is not automatically an equal factor in wall time, FLOPs or memory.

Reference implementation, independent verifier, and adversarial certificate
audit: `theory/numerical_checks/normalizer_chord_audit.py`.
