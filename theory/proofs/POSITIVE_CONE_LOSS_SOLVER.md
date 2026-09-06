# Globally certified loss optimization in a known positive mass cone

Status: **PROVED finite approximation algorithm**, 2026-09-06. The executable
solver uses checked rational LP proposals and may return UNRESOLVED if an LP
certificate or its declared work budget is missing. No result is a complete
Reference Compiler installation certificate.

## 1. The exact decision class

The input is a finite rational table of nonnegative mass atoms a_j(x,y), a
strictly positive rational base b(x,y), nonnegative **integer** observation
counts c(x,y) with total C>0, and optional rational linear constraints Gw<=h.
The class contains every finite nonnegative coefficient vector w satisfying
those constraints, with

\[
M_{xy}=b_{xy}+\sum_j w_j a_j(x,y),\quad
T_x=\sum_yM_{xy},\quad q_{xy}=M_{xy}/T_x.
\]

Independent coefficient values are a declared static relaxation. Unknown atom
acquisition, nonlinear/tied value dynamics, physical ownership and registered
optimizer reachability are not smuggled into this class. A readout-normalizer
cap is a valid linear constraint; general hardware feasibility is not assumed
linear. Zero-count observations/coordinates are retained in the input.

Define the rational likelihood and ordinary mean cross-entropy by

\[
P(q)=\prod_{x,y}q_{xy}^{c_{xy}},\qquad L(q)=-C^{-1}\log P(q),
\]

where a factor with count zero is 1, including at q=0 in a bounding box.
The goal is a **finite feasible witness** and checked numbers P_low,P_high with
`P_low<=sup P<=P_high<=gamma P_low`, for any declared rational gamma>1.
This certifies `L(witness)-inf L<=log(gamma)/C`. It does not assert that the
infimum is attained or decide exact equality to an arbitrary loss threshold.

## 2. Prediction boxes have linear finite-model feasibility tests

Cover the product of probability simplexes by rational coordinate boxes
`ell_xy<=q_xy<=u_xy`. Keeping the base coefficient fixed at one, feasibility is
exactly the rational LP

\[
w\ge0,\quad Gw\le h,\quad
\ell_{xy}T_x\le M_{xy}\le u_{xy}T_x\quad\text{for every }x,y.
\]

No zero normalizer is introduced: b is strictly positive at every original
context, at every LP call. A feasible rational w is an actual finite point
inside the box. Infeasibility has a Farkas certificate. If a floating solver
proposes neither a vector nor a dual that checks in the original rational
equations, this implementation must return UNRESOLVED.

This deliberately answers finite feasibility inside each box. A closed box
can contain a closure-only point yet contain no finite model. Pruning such a
box is sound for the actual optimization class: the remaining closed children
still cover every finite model. No closure endpoint is installed, and no
zero-total context is erased. The residual closure theorem remains necessary
when closure membership itself is the question.

## 3. A sharp box-only likelihood upper bound needs no transcendental oracle

For each context independently, maximize `product_y q_y^c_y` subject to its
box and `sum q_y=1`. If the bounded simplex is empty, the full box is empty.
Otherwise this is the ordinary constrained multinomial likelihood problem.
Its optimum has rational coordinates and can be computed exactly:

* Positive-count coordinates satisfy `q_y=clip(c_y/lambda,ell_y,u_y)`.
  Breakpoints `c_y/u_y` and `c_y/ell_y` determine intervals with fixed active
  bounds. On each interval solve the normalization equation for lambda, a
  rational number, and check all bounds and the sum exactly.
* Zero-count coordinates stay at their lower bounds until all positive-count
  coordinates reach their upper bounds; any remaining probability can then be
  distributed within the zero-count bounds without changing the objective.
* If a positive count is forced to q=0, the likelihood upper is zero.

Concavity of `sum c_y log q_y` proves optimality: the free derivatives are
lambda, derivatives at upper bounds are at least lambda, and derivatives at
lower bounds are at most lambda. Every feasible displacement therefore has
nonpositive objective directional derivative. Boundary zero-count cases follow
directly. Multiplying the per-context optima gives an exact rational upper U
for the box. Ignoring mass-cone coupling here is a sound optimistic bound,
not a representability certificate.

## 4. Finite branch-and-bound despite unbounded coefficients

Start from `[0,1]` for every probability coordinate. A root LP either proves
the coefficient class empty or provides a finite witness with `P_0>0`. Keep
the best finite witness and its likelihood P_low. For an active box:

1. Compute its exact box-only upper U. If `U<=gamma P_low`, retain it as a
   likelihood-bound leaf.
2. Otherwise solve its finite feasibility LP. Retain an exactly checked
   infeasibility certificate, or use its finite primal to improve P_low.
3. If the bound still does not close, bisect a longest coordinate interval at
   its rational midpoint and keep both closed children.

A witness proposal from the empirical conditional table may improve the lower
bound, but cannot replace these covering and exclusion checks. Any feasible
proposal may be used; global validity does not depend on local optimization.

The executable solver visits the highest-upper box first. It also uses generic
float64 multistart optimization solely to propose finite coefficient witnesses;
each is rationalized and checked against the complete original inequalities
before its exact likelihood can improve the lower bound. A finite proposal
search box does not restrict the global proof class. Where an original linear
row exactly bounds a context's total mass, the fixed base supplies sound initial
probability bounds `b_xy/R<=q_xy<=1-sum_(z!=y)b_xz/R`. The verifier rederives them
from that original row; no caller-supplied probability bound is trusted.

**Termination theorem with an exact LP oracle.** This procedure closes after
finitely many nodes for every gamma>1, even if the coefficient set is unbounded
and the likelihood supremum has no finite maximizer.

Proof: on `[0,1]^(|X||Y|)`, P is a polynomial with nonnegative integer exponents.
Its coordinate derivative has magnitude at most c_xy. Consequently

\[
|P(q)-P(q')|\le C\|q-q'\|_\infty.
\]

The box optimizer and any feasible witness in a box of maximum width h thus
differ in likelihood by at most Ch. After the witness update,
`U<=P_low+Ch`. If `h<=(gamma-1)P_0/C`, the box closes. Longest-coordinate
bisection reaches this width at a finite uniformly bounded depth. The binary
tree up to that depth is finite. Empty boxes close by exact LP exclusion.
This is a termination proof, **not** a claim that the work bound is small:
P_0 may be extremely small and dimension may be large.

Every leaf either has no finite feasible model or has a checked upper at most
gamma times the final witness likelihood. The two children cover their parent
exactly, including their shared midpoint. Thus the retained tree proves the
global bound over the declared class. It does not transfer to missing atoms,
unknown information, a different coefficient domain or a reachable learner.

## 5. Evidence and honest stopping

The solver separates proposal generation from a verifier that reconstructs
each child's box, checks every Farkas certificate against original constraints,
recomputes likelihood uppers, and checks the final finite witness. A missing
child, forged split, false likelihood upper or invalid dual must fail verification.
No hash or success flag substitutes for these equations.

The requested gamma is an external verifier argument and must match the proof;
a certificate cannot weaken its own accuracy requirement. Model coefficients,
primal/dual vectors and bound values use exact rational encodings. The box
optimizer's active-set proposal is additionally checked by an independent exact
KKT condition before it can supply an upper bound.

Zero objective count is not permission to delete a context's other constraints.
The audit includes two contexts sharing masses `(1+w,1)`, counts `(3,1)` and
`(0,0)`, with a cap of 3 at the unscored context. That cap still enforces w<=1;
the exact optimum likelihood is 8/81, strictly below the unconstrained 27/256.
The solver retains the original coefficient domain while optimizing the fixed
count objective.

The executable solver has a declared node budget. Exhaustion or an unverified
LP proposal gives UNRESOLVED, with any sound incumbent/bound available; it does
not relabel a local optimizer as complete. Minimal checked-in evidence records
the audit results; full trees are regenerated and independently verified during
the audit instead of dumping solver transcripts or caches.

The research result resolves global **arbitrary-accuracy static optimization**
for this explicit finite rational class. It does not prove polynomial time,
an efficient closed form for the unary-SUM parity conjecture, exact optimum
attainment, general FP search completeness, fresh persistence or an AMP bridge.
Large but finite coefficient witnesses retain their real encoding and
construction costs; they are not automatically installable models.

Reference implementation and adversarial audit:
`theory/numerical_checks/positive_cone_loss_audit.py`.
