# Exact and limiting factorization across source annihilators

Status: **PROVED**, 2026-09-09. The one-PRODUCT border example has a complete
coefficient-level explanation. This gives a constructive closure criterion,
classifies which visibility masks are closed, and lifts it to a scoped
existential characterization of full one-PRODUCT mass/probability closure.

## 1. A declared visibility graph

Fix finite nonnegative parent atom families a_i(x), b_j(x), with compatible
SUM types and a legal scalar PRODUCT, on a completely declared finite context
domain. A single new PRODUCT of two SUMs has table

`h(x)=(sum_i u_i a_i(x))(sum_j v_j b_j(x))`, u_i,v_j>=0.

Let the bipartite visibility graph G have edge ij precisely when a_i b_j is
not identically zero on that domain. Its visible coefficient vector is
`q_ij=u_i v_j`, ij in G. Missing edges are proved annihilators, not products
that happen to vanish on an acquired sample. Omitting them is justified only
for this fixed extensional decision; it is not a learner/provenance quotient.

The input to the first theorem is a **given** nonnegative visible coefficient
table q. Observable mass tables may have multiple coefficient representations.

## 2. Positive-edge consistency

Let S={ij in G:q_ij>0}. On every connected component of S, assign positive
row and column factors alpha_i,beta_j along a spanning tree, starting one
factor at one and setting its neighbor to q_ij divided by that factor.
Every remaining positive edge must satisfy q_ij=alpha_i beta_j. Failure gives
an alternating positive-cycle product contradiction and excludes even closure.
Rational q yields rational factors and exact comparisons. Isolated vertices
receive factor one for this test.

Positive consistency alone is insufficient: the selector border example has
no positive cycle to check but its visible zero still prevents finite factors.

## 3. Complete finite factorization criterion

Call a vertex active when incident to S. Given positive consistency,

`q has a finite nonnegative factorization iff every visible edge between`
`an active row and an active column belongs to S`.

Necessity follows because active endpoint factors cannot vanish. Conversely
use the positive factors on active vertices and set inactive factors to zero.
All visible edges then agree exactly. This includes the all-zero table.

## 4. Complete closure criterion and explicit exponents

Contract every connected component of S, including isolated vertices. For
each visible zero edge ij, draw a directed edge from the component of row i
to the component of column j. Self-loops count as cycles. Then

\[
\boxed{q\in\overline{\{(u_i v_j)_{ij\in G}:u,v\ge0\}}
\iff\text{positive consistency holds and this directed graph is acyclic}.}
\]

For sufficiency, choose integer heights H_C equal to the longest directed
path from component C to a sink. Every directed edge C->D has H_C>H_D.
For rational 0<epsilon<1, set

`u_i(epsilon)=alpha_i epsilon^(H_C(i))`,
`v_j(epsilon)=beta_j epsilon^(-H_C(j))`.

Every positive edge is reproduced exactly. Every zero edge has coefficient
`alpha_i beta_j epsilon^(H_C(i)-H_C(j))`, which tends to zero. Heights are at
most the number of components minus one. Thus every accepted limit has an
explicit rational one-parameter family; negative exponents expose the
unbounded coefficient scales instead of hiding them.

For necessity, suppose a directed cycle visits components C_1,...,C_l, with
zero edges i_k j_(k+1), subscripts modulo l. Inside C_k, a positive-edge path
connects row i_k to column j_k. Along any finite factor sequence the cross
product u_(i_k)v_(j_k) equals the alternating product/quotient of the path's
positive edge values, and therefore has a finite strictly positive limit.
But

`prod_k u_(i_k)v_(j_(k+1)) = prod_k u_(i_k)v_(j_k)`.

The left side tends to zero and the right to a positive value. Clearing the
positive-path denominators gives a polynomial contradiction, so the argument
does not assume bounded hidden factors. A self-loop is the length-one case.
Inconsistent positive cycles are excluded by the same product identities.

The checker is finite graph processing and rational arithmetic for a known
q. It does not optimize unknown coefficient tables or authorize a Compiler
completion outside this decision class.

## 5. Exactly which visibility masks have closed factor images?

\[
\boxed{\text{The visible rank-one image is closed iff every nontrivial}
\text{ connected component of G is complete bipartite}.}
\]

For a complete bipartite component, two distinct active S-components would
have zero cross edges in both directions, violating acyclicity. Closure thus
forces every active row/column cross edge to be positive, which is exactly
finite factorization. Components can be handled independently.

Conversely, a connected non-complete bipartite graph contains an induced
three-edge path r_0--c_0--r_1--c_1 with missing edge r_0 c_1: take the first
four vertices of a shortest path between a nonadjacent row and column.
Put q=1 on its two outer edges and zero on every other visible edge. The two
active positive components have only the directed zero edge C_1->C_0;
inactive row vertices are sources and inactive columns are sinks. The graph
is acyclic, so the table lies in closure. Finite factorization is impossible
because the middle edge joins active endpoints but has zero coefficient.

This classifies the **coefficient** image. A linear observation map can remove
that obstruction by providing another coefficient representation. For example
the path family `(x_0+epsilon z_0)(x_1+epsilon z_0)/epsilon` has limiting
visible coefficients that fail exact factorization, but its observable limit
is `x_0 z_0+x_1 z_0=z_0`, a SUM-only table. Coefficient rejection alone must
never reject every alternative mass representation.

For the three-input selector, replacing the first tail z_0 by w_0 gives the
same induced path and the limit `x_0 z_0+x_1 w_0`. The separate zero-face and
conditional-scale proof in `ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md` establishes
that no alternative one-PRODUCT mass lift works at cap three.

## 6. Lift to the full static one-PRODUCT mass class

Fix a finite known nonnegative additive atom family d_s and k output heads
with base one. Every mass table in the class has

`M_y=1+sum_s w_(ys)d_s+c_y sum_(ij in G) q_ij a_i b_j`,

where w,c>=0 and q is finitely factorable. Normalize sum_y c_y=1 by absorbing
its scale into one PRODUCT parent; SUM-only cases use q=0 and any such c.

**Closure-lift theorem.** The closure of this mass class is exactly the same
displayed representation with w,c>=0, sum c=1, and q satisfying the graph
closure criterion above.

For necessity, a convergent mass sequence is bounded at every context.
Positivity bounds each additive coefficient belonging to a nonzero atom.
After the c normalization, the shared PRODUCT table is bounded by the sum
of excess masses. Every visible atom a_i b_j is positive at some declared
context, so its coefficient q_ij is bounded too. Take a common convergent
subsequence of these finite coefficient vectors and c. Invisible coefficients
need not be bounded and cannot be assigned invented bounds. Null additive
atoms may receive coefficient zero for this extensional existence claim;
that is not permission to erase their physical or learner state.

For sufficiency, keep w,c fixed and insert the explicit epsilon factor family.
Its mass tables converge to the desired lift.

If a uniform cap sum_y M_y<=R with R>k is imposed, any approximating mass
table can be returned inside the cap by one common scalar contraction of
all excess masses:

`lambda=min(1,(R-k)/max_x sum_y(M_y(x)-1))`.

Use lambda=1 when the denominator is zero. For a target in the cap this
lambda tends to one, preserves the base and needs no extra PRODUCT. Thus
intersection with this cap commutes with mass closure. At R=k only the base
table is possible. Arbitrary non-monotone resource constraints do not inherit
this contraction argument.

Finally, at finite cap all masses lie in a compact box. A conditional table
p lies in the probability closure iff there exist masses in the closure lift
with `M_y(x)=T_x p_y(x)` and k<=T_x<=R. This retains every normalizer and
requires an existential search over alternative mass/coefficient lifts.

For rational atoms, p and R, enumerate positive-edge support patterns with
acyclic quotient and express their positive factors, additive coefficients,
head weights and normalizers through polynomial equalities/inequalities.
This is a finite semialgebraic characterization, not an implemented efficient
global mass solver. Work/evidence failure of a numerical search remains
UNRESOLVED. The executable audit here decides only **given coefficient**
tables and checks explicit observed witnesses.

## 7. Relation to existing factorization theory

This coefficient map is a monomial model with a row/column incidence matrix.
The distinction between exact nonnegative factorization and limiting
factorization is established generally by Geiger, Meek and Sturmfels,
[On the toric algebra of graphical models](https://math.berkeley.edu/~bernd/AOS0092.pdf),
Theorems 3.1--3.2. Exact factorization additionally requires feasible support;
the nonnegative toric equations describe its closure. The elementary proof
here specializes that distinction to a directed component graph, gives
rational power-law witnesses, and connects it to FP's source annihilators,
alternative observable lifts and final-range constraints. It is not a claim
to have originated the general monomial closure theorem.

No new FP action, free initializer, registered value trajectory, install
reachability or reference/AMP bridge follows from these static constructions.

Exact graph and factor audit:
`theory/numerical_checks/masked_product_closure_audit.py`.
