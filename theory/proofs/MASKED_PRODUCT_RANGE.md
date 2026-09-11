# Finite range costs of PRODUCT closure and a sharp count/loss tradeoff

Status: **PROVED under the stated static contracts**, 2026-09-11.
Parent result: `FP_THEORY.md` XVII.16 / `MASKED_PRODUCT_CLOSURE.md`.

The closure theorem tells us whether a limit exists. This note determines the
exact hidden coefficient range required to approach it. It then connects that
range to the number of actual scalar PRODUCT nodes and ordinary cross-entropy
in a complete, explicitly delimited parallel-PRODUCT class. Arbitrary mixed SUM
parents are included in the latter theorem; nested PRODUCTs are not.

## 1. Given coefficients: a finite, attained optimum

Use the declared finite source families a_i,b_j and visibility graph G of
XVII.16. A missing edge is a proved source annihilator on the entire context
domain, not an unobserved training example. Let q>=0 be a **given** coefficient
vector, S its positive edges, and suppose its positive cycle identities hold.
Choose positive factors alpha_i,beta_j with q_ij=alpha_i beta_j on S.

In this note a component means an **active connected component of S**. Inactive
rows and columns can be assigned zero factors. Including their isolated
vertices in a height count would give spurious range costs. Put

`A_C=max_{row i in C} alpha_i`, `B_C=max_{column j in C} beta_j`.

For every visible zero edge with active endpoints, draw C(i)->C(j) and assign
an externally supplied rational tolerance tau_ij>0. Define its weight

`w_e=alpha_i beta_j/tau_ij`.

Seek factors u,v>=0 that retain every positive coefficient **exactly** and
satisfy u_i v_j<=tau_ij on every visible zero. The optimized quantity is

\[
\kappa(u,v)=\|u\|_\infty\|v\|_\infty
            =\max_{\text{all }i,j}u_i v_j.
\]

The maximum includes invisible coefficients. It is invariant to the ordinary
PRODUCT rescaling (u,v)->(s u,v/s), but is neither the final readout normalizer
nor an unspecified hardware cost. Null source factors may be removed for this
extensional optimum only, not from complete learner state without congruence.

**Theorem 1.** The constraints are feasible iff every directed cycle has weight
product at most one. Subject to this condition, their attained minimum is

\[
\boxed{\kappa_{\min}=\max_{P:C_0\to\cdots\to C_l}
 B_{C_0} A_{C_l}\prod_{e\in P}w_e.} \tag{1}
\]

It is enough to consider simple directed paths, including zero-length paths
with value A_C B_C. If q is identically zero the minimum is zero. Positive-edge
inconsistency instead excludes the problem before this graph is constructed.
Self-loops are cycles; weight exactly one is feasible, not a numerical tie.

**Proof.** All positive factors on a component have the form
u_i=alpha_i t_C and v_j=beta_j/t_C with t_C>0. Thus each zero bound is exactly
`t_D>=w_e t_C`. Multiplying around a cycle proves necessity. For any feasible
factors, write U=max u and V=max v. At a path's starting component,
`t_C0>=B_C0/V`; propagating the inequalities and using
`U>=A_Cl t_Cl` proves every lower bound in (1).

Conversely set `t_D=max_{P ending at D} B_start product_e w_e`. A walk can be
reduced to a simple path without decreasing its weight when every cycle has
product <=1. These maxima are finite, t_D>=B_D, and t_D>=w_e t_C. Hence the
constructed v is at most one and u is at most the right side of (1). The
already proved lower bound forces equality for kappa. Set inactive factors
zero; all edges incident to them meet their tolerance. This proves attainment.
Under component rescaling alpha->s_C alpha, beta->beta/s_C, each path expression
in (1) is unchanged by telescoping. The answer does not depend on the chosen
spanning-tree gauge. QED.

### Exact algorithm and certificates

Initialize potentials to B_C. Perform N-1 synchronous multiplicative
Bellman-Ford passes over the N active components, retaining a maximizing path.
If an edge still violates t_D>=w_e t_C, append it to its stored path. Some
repeated-vertex segment has product >1: otherwise deleting cycles would give
a no-worse path already considered in N-1 passes. That segment certifies
infeasibility. Otherwise the potentials produce the primal factors, and a
maximizing path certifies the matching lower bound. The arithmetic is rational;
no logarithms, tolerance-based stopping or optimizer optimality flag is used.
There are O(N times number_of_arcs) rational relaxations; bit arithmetic and
certificate construction are separate work, not unit-cost hardware claims.

The independent verifier checks a primal against the caller's dimensions,
mask, q and tolerances, and checks the displayed path lower bound. A negative
certificate is either an inconsistent positive alternating-cycle identity or
a directed closed walk with weight product >1. It never accepts a status flag
as its evidence and does not invoke the optimizing algorithm.

## 2. Sharp asymptotic exponent, including perturbations of positive edges

Suppose the active directed zero graph is acyclic, and give every zero the
same tolerance epsilon. Write

`C_P=B_start A_end product_{ij in P}(alpha_i beta_j)`.

Then (1) becomes the exact finite formula

\[
\kappa_{\min}(\epsilon)=\max_P C_P\epsilon^{-|P|}.
\]

If L is the longest active directed path length, then

\[
\boxed{\kappa_{\min}(\epsilon)=\Theta(\epsilon^{-L}),\qquad
\lim_{\epsilon\downarrow0}\epsilon^L\kappa_{\min}(\epsilon)
=\max_{|P|=L} C_P.} \tag{2}
\]

For L=0, exact factorization is already possible and the minimum is constant.
For L>0 and K>=max_C A_C B_C, the least positive zero tolerance with range
budget K is exactly `max_{nonempty P}(C_P/K)^(1/|P|)`. The rational decision
problem remains (1); the inverse formula need not be rational.

The exponent is not an artifact of requiring the positive edges to stay exact.
Allow uniform error epsilon on every visible coefficient and take
`epsilon<=min_{S} q_ij/2`. For any feasible u,v, recalibrate factors alpha',beta'
on the same positive spanning forest using its actual positive edge values.
If d is the maximum forest distance from the chosen roots, each calibrated
factor changes by a ratio in [2^-d,2^d]. This follows inductively since each
edge value ratio is in [1/2,3/2], and each update divides by its parent factor.
Thus for a longest original path P, its new path constant is at least
`2^(-2d(L+1)) C_P`. Applying the lower-bound part of Theorem 1 to these actual
positive values gives

`kappa >= 2^(-2d(L+1)) C_P epsilon^(-L)`.

The exact-positive construction supplies the matching upper exponent. This
argument allows arbitrary factor perturbations; it is not a test of only the
specific epsilon curve. It still concerns a given visible coefficient target,
not rejection of all alternative observable mass lifts.

## 3. A scoped parallel-PRODUCT closure lift

Fix finitely many independent, nonnested PRODUCT slots. Slot r has finite
known parent atoms, its own visibility graph, and independently variable
parent coefficients. Add a known nonnegative additive mass dictionary and
nonnegative readout weights c_yr. The mass class has the form

`M_y=1+sum_s w_ys d_s+sum_r c_yr sum_(ij in G_r) q^r_ij a^r_i b^r_j`.

Its closure is exactly the same representation with **each** q^r in its
own XVII.16 coefficient closure. All alternative coefficients remain
existentially quantified.

For necessity, normalize each nonzero head vector by sum_y c_yr=1, absorbing
its scale into that slot's parent; zero slots may use q^r=0. Positivity bounds
each slot's mass by the sum of all excess masses along any convergent sequence.
Every visible atom is positive somewhere on the declared finite domain, so
its coefficient is bounded separately. A common subsequence of the finite
coefficient collection converges. Sufficiency adds the finitely many explicit
slot approximants. The common excess-mass contraction from XVII.16 also
preserves a finite cap R>number_of_heads and the number of PRODUCTs.

This proves a parallel independent-slot lift, not a closure theorem for tied
coefficients or nested/shared PRODUCT ancestors. It does not implement the
existential search over alternative masses or conditional normalizers. In
particular, individually factorable slots cannot be chosen independently when
a declared parameter tie couples them.

## 4. Declared source and readout contract for a count/loss theorem

Let n>=2. The context set contains pair contexts (i,j) for 1<=i<=j<=n, one
row-only guard R_i for each i, and one column-only guard C_j for each j. It has
`N=n(n+5)/2` elements. Define a_i=1 on its row and R_i, and b_j=1 on its column
and C_j; all other values are zero. These source evaluations are declared
before the current binary label. In particular a_i a_j=b_i b_j=0 for i!=j,
and a_i b_j=0 for i>j, throughout this domain.

Let f=1 on the n diagonal pair contexts and zero elsewhere. Under a uniform
context law, the binary target is `p*_0=(1+f)/(2+f)`: it is 2/3 on the diagonal
and 1/2 elsewhere. The model readout is fixed as

`M_0=1+h`, `M_1=1`, `p_0=(1+h)/(2+h)`, with total cap 3, hence 0<=h<=1.

Only the first head receives excess mass. This fixed readout is an explicit
restriction; a freely varying second head or arbitrary conditional scale is
not silently excluded from a purported full-grammar result.

The class consists of **all additive SUM contributions and at most k parallel
scalar PRODUCTs of arbitrary nonnegative SUM parents of these 2n sources**:

`h=sum_i d_i a_i+sum_j e_j b_j+sum_r F_r G_r`,

`F_r=sum_i u_ri a_i+sum_j s_rj b_j`,
`G_r=sum_i t_ri a_i+sum_j v_rj b_j`.

All coefficients are nonnegative; the parents have no PRODUCT ancestors.
Arbitrary finite linear SUM chains flatten to this class extensionally, not
as a complete-state quotient. Any nonnegative output weight on a PRODUCT is
absorbed into one parent **and charged** in the resulting coefficient bound.
For each actual PRODUCT impose

`kappa_r=max(||u_r||inf,||s_r||inf) max(||t_r||inf,||v_r||inf) <= K`, K>=1.

The max norms here mean maximum coefficient magnitude, not an infinity limit.
Each parent's maximum actual value is between its largest coefficient and
twice that coefficient. Thus the product of peak parent values is between
kappa_r and 4 kappa_r. These are comparable numerical range contracts, not
bytes, FLOPs, construction work or an authorized refactoring of an optimizer.

## 5. Exact count and approximation count are arbitrarily far apart

The source identities give the **derived** mixed-parent expansion

`F_r G_r=sum_i u_ri t_ri a_i+sum_j s_rj v_rj b_j`
`        +sum_ij (u_ri v_rj+t_ri s_rj) a_i b_j`.

Thus k actual PRODUCTs give at most 2k nonnegative rank-one cross-coefficient
terms, plus a nonnegative additive remainder. **Those 2k terms are not 2k
semantic PRODUCT nodes.** No sign cancellations or unavailable negative
sources were used.

If h=f exactly, the guard values force the entire additive remainder to zero.
Each rank-one cross term can cover at most one positive diagonal: covering
both i<j would force a positive visible off-diagonal (i,j). Consequently
`2k>=n` is necessary. It is also sufficient: pair diagonal indices i,j and use
`(a_i+b_j)(b_i+a_j)=a_i b_i+a_j b_j`. Unpaired indices use a_i b_i. All unwanted
same-type products vanish. These finite witnesses have kappa_r=1 and cap 3.
Therefore

\[
\boxed{k_{exact}=\lceil n/2\rceil.} \tag{3}
\]

Nevertheless one PRODUCT approaches f at this same final cap by taking
`u_i=epsilon^(n-i)`, `v_i=epsilon^(-(n-i))`, F=sum u_i a_i, G=sum v_i b_i.
The diagonal is exactly one, each forward off-diagonal is epsilon^(j-i), and
the guards are zero. Hence one PRODUCT has Bayes risk infimum without a range
bound, even though the exact minimum count in (3) grows without bound.

For comparison, if a separately declared type contract restricts the left
parent to A sources and the right to B sources, the exact minimum is n, not
ceil(n/2). Applying this oriented count to arbitrary mixed parents is false
already at n=2. Removing guards is another invalid shortcut: at n=2 the SUM
`a_2+b_1` matches all pair-context targets with no PRODUCT. Both scope attacks
are executable checks, not merely caveats.

## 6. Sharp finite-range CE exponent for arbitrary mixed parents

Fix `1<=k<ceil(n/2)` and put `m=ceil(n/(2k))`, `L=m-1>=1`.
Let E=max_x|h(x)-f(x)|. The guard values bound the additive remainder at each
row and column by E. At diagonal i, the sum of 2k cross contributions is
therefore at least 1-3E. If E<1/3, assign each diagonal a cross term that
contributes at least `(1-3E)/(2k)` there. One term is assigned at least m indices
`i_1<...<i_m`. Each of its forward off-diagonal coefficients is at most E by
positivity. For that rank-one term U_i V_j the exact identity is

\[
(U_{i_m}V_{i_1})\prod_{r=1}^{m-1}(U_{i_r}V_{i_{r+1}})
=\prod_{r=1}^{m}(U_{i_r}V_{i_r}).
\]

Its full coefficient range is at most its actual parent's budget K. Hence

\[
\boxed{K E^{m-1}\ge[(1-3E)/(2k)]^m.} \tag{4}
\]

This bounds every competitor, with arbitrary additive coefficients and mixed
parent supports, not only the constructive partition used below. It implies

`E>=delta(K):=min(1/6, [1/((4k)^m K)]^(1/L))`.

The probability error at a maximizing context is at least E/9 since
`|p_0-p*_0|=|h-f|/[(2+h)(2+f)]`. Bernoulli relative entropy obeys
`D(a||b)>=2(a-b)^2`: as a function of a its second derivative is
1/[a(1-a)]>=4 and its value and derivative vanish at a=b. Averaging over all
N contexts proves the explicit positive loss margin

\[
\boxed{\Delta\mathcal L\ge\frac{2}{81N}\delta(K)^2>0.} \tag{5}
\]

For the upper bound, partition indices into at most 2k balanced groups, each
of size at most m. Within a group of size s, in increasing order p=0,...,s-1,
use `U_i=epsilon^((s-1)/2-p)` and `V_i=1/U_i`. This gives one on its diagonal,
forward entries epsilon^(rank difference), and range epsilon^(-(s-1)). Pair
two disjoint groups into **one** actual mixed PRODUCT:

`(sum_group1 U_i a_i+sum_group2 V_j b_j)`
`(sum_group1 V_i b_i+sum_group2 U_j a_j)`.

The cross-group same-type products are identically zero. Each parent has
maximum coefficient epsilon^(-(max(s_1,s_2)-1)/2), so each actual PRODUCT has
kappa<=epsilon^-L. All contexts obey 0<=h<=1; diagonals are exact, and residual
off-diagonal values are at most epsilon. Choose epsilon=K^(-1/L).
At an off-diagonal context,

`D(1/2 || (1+h)/(2+h)) = (1/2)log(1+h^2/[4(1+h)]) <= h^2/8`.

Together with (5), this proves the sharp **exponent**, not sharp constants:

\[
\boxed{\inf\mathcal L-\mathcal L_{Bayes}
=\Theta\!\left(K^{-2/(\lceil n/(2k)\rceil-1)}\right).} \tag{6}
\]

At k>=ceil(n/2), Bayes is attained already at K=1. At k=0 the guard argument
gives E>=1/3, hence a positive SUM gap. At fixed finite k,K the static optimum
exists: balance each nonzero parent pair so both coefficient maxima are at
most sqrt(K), set null pairs zero, and bound the additive coefficients by one
using the guards. The resulting finite parameter set is compact and its
prediction image is unchanged. This is an extensional attainment proof,
not permission to rescale a live learner.

Under the stricter oriented-parent contract, repeat the lower argument with
k rather than 2k cross terms and use one group per PRODUCT. The exact count
is n and the CE exponent is `-2/(ceil(n/k)-1)` for k<n. The audit checks both
classes separately and tests the mixed-parent counterexample to their conflation.

## 7. What this says about finite construction, and what it does not

A local coefficient alphabet or bounded final normalizer alone does not bound
kappa after flattening long SUM chains. Suppose a **separately registered**
linear SUM realization has fan-in <=b, local weights <=a, and
`M=max(1,ba)>1`. If a PRODUCT's two parent SUM depths and its output SUM-path
depth have sum at most D, induction on the positive linear DAG gives an
effective parent/readout coefficient product at most M^D. Substituting
K=M^D into (5) supplies a valid, generally loose construction-depth margin
for that declared parallel realization. Costs hidden in long SUM chains are
not free. This does not equate D, kappa, finite precision and physical memory.

In particular, (3)--(6) are not lower bounds for nested PRODUCT DAGs, recurrent
FP, enriched sources, varying output heads or unregistered context-dependent
controllers. The independent-slot closure lift does not handle parameter
ties. Coefficient rejection still cannot discard all observable lifts.
Registered value acquisition, optimizer trajectories, physical build/install,
fresh persistence, complete Reference Compiler closure and the actual AMP
bridge remain open. No new architecture-semantic action has been introduced.

## 8. Prior work and evidence

The monomial exact-factorization/closure distinction is established in Geiger,
Meek and Sturmfels, *On the toric algebra of graphical models* (2006),
arXiv:math/0608054. The base note already locates XVII.16 relative to that work.
Rank-one completion and its support/cycle conditions are also discussed in
Kubjas and Metsalampi, *Geometry of low nonnegative rank matrix completion*,
arXiv:2601.07658v1, Section 3.1. We do not claim to originate these general
factorization facts or graph difference-constraint algorithms. The results
proved here add the exact range optimum, its path exponent, and the scoped
native PRODUCT-count/CE tradeoff; no claim of literature-wide priority is made.

Reproducible source: `theory/numerical_checks/masked_product_range_audit.py`.
Minimal output: `evidence/minimal/FP_MASKED_PRODUCT_RANGE_AUDIT.json`.
The audit compares 9,367 rational decisions with an independent max-product
Floyd-Warshall calculation on the original row/column vertices; rejects 15
forged/replayed certificates and 5 invalid exact inputs; checks 216 oriented
and 123 mixed-parent native witnesses, 1,792 mixed-parent expansion identities,
and rational outward log bounds. The independent oracle uses variables u_i
and 1/v_j, never the optimizer's component contraction or potentials.
These are theorem/algorithm audits, not GPU runs or a Runtime freeze.
