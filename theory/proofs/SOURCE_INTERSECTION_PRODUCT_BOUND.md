# Native source intersections survive PRODUCT mass limits

Status: **PROVED; EXACT RATIONAL AUDIT**, 2026-09-11. A globally consistent
choice of one term in each SUM gives a small source-support witness, even
when PRODUCT ancestors are shared. A quantitative version survives arbitrary
coefficient limits. Single-face mass has exact and approximation PRODUCT
minimum equal to its codimension minus one. Shared identity outputs then
require more PRODUCTs than the earlier rank bound alone established.

## 1. Complete static source contract

Fix a finite domain X and finitely many fixed, finite nonnegative scalar
source tables a_1,...,a_n. Include any permitted constant among these sources.
Allow arbitrary finite positive SUM/binary PRODUCT DAGs with fixed finite
nonnegative real coefficients and one scalar excess readout g. P counts
scalar PRODUCT nodes, including shared ancestors only once. There is no
internal normalization, recurrence, adaptive source acquisition or physical
cost restriction. The final positive readout base is not part of g.

Fix x with g(x)>0. Let s=s(x) count sources positive at x; necessarily s>=1.
Define

```
mu_x = min({1} union {a_i(y)/a_i(x): a_i(x)>0, a_i(y)>0, y in X}),
K(s,P) = (s+P) product_(j=1,...,P) (s+j-1)^(2^(P-j+1)).
```

The empty product is one, so K(s,0)=s. Since the source tables and domain
are fixed and finite, mu_x>0. No floor on graph coefficients or cap on
internal activations enters either constant.

## 2. A retained monomial with at most P+1 distinct sources

There is a nonzero monomial of the form

`m(y)=c product_i a_i(y)^e_i`, c>0,

with at most P+1 distinct sources and total source degree at most 2^P, such
that

`0<=m(y)<=g(y)` on the whole domain, and `m(x)>=g(x)/K(s,P)`.

**Proof.** Topologically order the PRODUCTs h_1,...,h_P. Flatten only SUM
paths to express each PRODUCT parent as a nonnegative linear combination
of sources and preceding PRODUCTs, and the readout as another such
combination. At the chosen x, each parent of h_j has at most s+j-1 positive
terms, and the readout has at most s+P.

At each of these affine combinations, retain one term of largest *original*
value at x. Make this choice once per combination. Use the same retained
definition of each earlier PRODUCT wherever it is shared. Positivity makes
the resulting function pointwise no larger than the original. After SUM
choices become scalar multipliers, it is a single source monomial. Every
source in its ancestry is positive at x.

For the quantitative estimate let B_0=1 and

`B_j=(s+j-1)^2 B_(j-1)^2`.

By induction every retained h_j at x is at least its original value divided
by B_j: each selected parent contribution loses at most s+j-1 from its
affine selection and at most B_(j-1) from its chosen feature. The readout
loses at most s+P more. Thus its total loss factor is exactly the stated
upper bound `(s+P)B_P=K(s,P)`. Zero-valued unused parents do not affect a
positive retained output.

For the support count, contract all chosen SUM paths. The reachable graph
has p<=P binary internal nodes and l distinct source leaves. Its connected
underlying graph has at least p+l-1 edges and at most 2p edges, giving
l<=p+1<=P+1. Unfolding at most P binary PRODUCTs gives at most 2^P source
occurrences. Shared subgraphs use the same retained definition, so this
argument does not count an ancestor's repeated use as a new binary node.

Let C be the intersection of the positive supports of the retained sources.
It contains x. For every y in C, the source-ratio floor gives

`g(y)>=m(y)>=mu_x^(2^P) m(x)>=mu_x^(2^P) g(x)/K(s,P)`.

This is a static comparison monomial. Its existence grants no Runtime
erasure, new source access, registered value transport or free SUM refactor.

## 3. Consequences for limits and for uniform error

Every finite mass limit f of the at-most-P class satisfies the following:
at each x with f(x)>0, there is an intersection C of at most P+1 positive
source supports, containing x, such that

`f(y)>=mu_x^(2^P) f(x)/K(s(x),P)>0` for every y in C.

Indeed the finitely many possible source intersections permit a subsequence
with constant C. The quantitative bound above then passes to the limit. It
does not assume a limit for hidden features or coefficients. The same bound
applies to graphs with fewer PRODUCTs: K(s,P) is nondecreasing in P, while
mu_x^(2^P) is nonincreasing.

There is a finite-error statement as well. Suppose f(x)=gamma>0 and every
such intersection C containing x meets a zero of f. Writing
beta=mu_x^(2^P), every at-most-P graph satisfies

`||g-f||_infinity >= gamma*beta/[K(s(x),P)+beta]`.

If g(x)=0 the assertion is immediate. Otherwise the retained C contains a
zero y of f. With error delta, the comparison gives
`delta>=g(y)>=beta*(gamma-delta)/K`, which rearranges to the bound.

This is a necessary source-support condition, not a complete closure
decision. Three-bit parity has a singleton face through every positive point,
so it passes the P=2 condition; the stored full exponent certificate still
excludes its two-PRODUCT closure. Different pointwise choices need not arise
from one common coefficient system.

## 4. Binary faces have exact and approximation minimum m-1

On the complete d-bit cube with its 2d unary indicators, s(x)=d and mu_x=1.
An intersection of at most P+1 compatible source supports is a coordinate
face fixing at most P+1 bits. Therefore every positive point of a mass
limit must lie in such a face contained in its positive support.

Let f be gamma>0 times the indicator of a coordinate face of codimension
m>=2. Every face through a positive point fixing at most m-1 coordinates
contains a zero of f. Thus for P=m-2,

`inf_(products<=m-2) ||g-f||_infinity >= gamma/[K(d,m-2)+1] > 0`.

Multiplying its m fixed literals realizes f with m-1 PRODUCTs. Hence both
exact and arbitrarily accurate PRODUCT minima are **m-1**. A codimension-one
face is already a source and uses zero; a constant face also uses zero.
In particular, a d-bit singleton mass has exact and approximation minimum
d-1, with

`Delta_d = 1/[K(d,d-2)+1]`

as a conservative unit-mass gap below that count, for d>=2.

The proof does not claim that *every* monomial of a P-PRODUCT graph has only
P+1 distinct sources. For example `(x_1+x_2+x_3+x_4)^4` uses two repeated
squares and contains `24*x_1*x_2*x_3*x_4`. Choosing independently in every
copy of an unfolded ancestor would destroy the shared-graph argument. A
single consistent choice retains a much smaller-support monomial instead.

There is also no dimension-independent approximation margin. With P=d-2,
D=2^(d-2), the repeated-square graph

`g=(sum_(i=1,...,d) x_i)^D/[d^D+(d-1)^D]`

has singleton sup error exactly

`(d-1)^D/[d^D+(d-1)^D]`.

The all-one point and its neighbors attain the error; monotonicity bounds
all remaining contexts. This tends rapidly to zero as d grows, while the
fixed-dimension positive separation above remains valid. The lower bound
and this upper family are not claimed to have matching constants or rates.

## 5. All singleton outputs: a stronger shared lower bound

For d>=2 let N=2^d and prescribe all N singleton excesses simultaneously.
Each scalar target has approximation minimum r=d-1, and the supports are
disjoint. The last-PRODUCT comparison in
[`SHARED_DISJOINT_PRODUCT_LOWER_BOUND.md`](SHARED_DISJOINT_PRODUCT_LOWER_BOUND.md)
therefore proves the joint exact and approximation lower bound

`P >= N+d-2`.

This strengthens the earlier N-node rank bound for d>=3. It is a lower
bound, not a sharp higher-dimensional count. The balanced exact construction
still gives `U(1)=0`, `U(d)=2^d+U(floor(d/2))+U(ceil(d/2))`:

| d | Lower bound, exact and approximation | Exact construction |
|---|---:|---:|
| 2 | 4 | 4 |
| 3 | 9 | 12 |
| 4 | 18 | 24 |
| 5 | 35 | 48 |
| 6 | 68 | 88 |

The later [`DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`](DECODER_EXACT_AND_LIMIT_COMPLEXITY.md)
attains every lower bound in approximation, including at the minimum
conditional cap, and proves the exact three-bit minimum is twelve.

The same exclusion has a conditional margin at the minimum cap. Take base
one for every label, uniform contexts, target
`p_i(x)=(1+1[x=i])/(N+1)` and cap T<=R=N+1. Exact target prediction forces
T=R and hence the identity excess table. Approximate normalizers are retained
in the following bound.

The underlying last-PRODUCT argument supplies something stronger than an
error bound: for some head i it constructs a prefix B_i with P-N+1
PRODUCTs and, pointwise,

`max(0,E_i-sum_(j!=i) E_j)<=B_i<=E_i`.

Each removed contribution is bounded by the original discarded head at the
same context, so summing those bounds proves this inequality without any
disjoint-support assumption. Disjointness is used only when relating it to
the target.

Let delta=||q-p||_infinity. Since all other masses are at least one and
T<=N+1, every q_i<=2/R<=1/2. At the surviving head's correct context,

```
E_i-sum_(j!=i) E_j = (2q_i-1)T+N-2
                     >= (2q_i-1)R+N-2
                     >= 1-2R delta.
```

Also E_i<=1 everywhere, and at its wrong contexts E_i<=R delta. Thus the
scalar comparison has singleton error at most 2R delta. Every model with
P<=N+d-3 satisfies

`delta >= Delta_d/[2(N+1)]`,

`L(q)-L_Bayes >= Delta_d^2/[2N(N+1)^2]` nats.

The latter uses a context attaining the probability error, Bernoulli
coarsening of that label, Pinsker, and uniform context averaging. At d=3,
Delta_3=1/37: **all at-most-eight-PRODUCT models have probability error
>=1/666 and excess CE >=1/1774224**. The matching nine-PRODUCT limiting construction is
given in the later decoder theorem above. The earlier stronger exclusion for the
smaller class P<N remains valid. At d=2 its earlier margin is also stronger.

## 6. What the audit establishes

`theory/numerical_checks/source_intersection_product_audit.py` evaluates
actual DAGs and their retained monomials using exact rational arithmetic,
including non-indicator sources with positive ratios below one, zeros,
shared ancestors and squaring. It checks the full-domain monomial dominance,
the P+1 distinct-source count, the quantitative constants, direct face and
decoder constructions, and all normalizers of its finite rational samples.
The known two-PRODUCT support border and the excluded parity support guard
against confusing this necessary condition with an exact-support oracle or
a sufficient closure decision.

Complete source tables are essential. Positivity on an acquired subset
cannot establish these full-domain support intersections. Recurrence,
physical encoding/construction budgets, registered learning, installation,
fresh persistence and AMP remain separate. Exact higher-dimensional shared
counts and sharp approximation margins remain open.

The later [`NORMALIZER_SLACK_DECODER.md`](NORMALIZER_SLACK_DECODER.md)
improves the three-bit scalar one-PRODUCT singleton lower bound to 1/4 and
the cap-nine at-most-eight probability/CE bounds to 1/45 and 1/8100. It
also proves an exact nine-PRODUCT interval immediately above cap nine.
