# Exact positive partition decoding still costs exponentially many operations

Status: **PROVED, SCOPED UNCONDITIONAL CIRCUIT LAW; EXACT FINITE AUDIT**.
This is a computational companion to the
[compact count encoding](COUNT_LEARNER_ENCODING.md) and the
[conditional forecast-decoding theorem](FORECAST_DECODING_COMPLEXITY.md).
It concerns a fixed positive arithmetic decoder of a specified unnormalized
partition function. It is not a lower bound on all forecast algorithms,
finite-horizon contracts, approximate inference or a particular GPU worker.
Foundation R4, ERC-1 and all running experiments remain unchanged.

## 1. A bounded factor interface obtained from actual histories

Let n>=3, E be the unordered pairs of n vertices, D=|E|=n(n-1)/2, and
z0=0 anchor the binary worlds. Consider the actual noise1/10 relation learner
after c_e>=0 copies of label0 on each edge. Every such history is legal and
has positive probability. Cancel the common positive likelihood of agreement
on every observation. The remaining weight and its partition function are

`W_c(z) = PRODUCT_e x_e^(z_i XOR z_j)`, `x_e=9^(-c_e)`,

`Z_n(x) = SUM_{z:z0=0} PRODUCT_{e:z_i XOR z_j=1} x_e`.

All inputs x_e belong to(0,1]. The normalized posterior is W_c/Z_n, and the
actual native world-slot learner's readout total is still10. Z_n is the
decoder's partition function, not that native readout total.

Grant the decoder these D exact factor values for free. It must return Z_n
using a fixed, finite DAG of binary additions and multiplications with
nonnegative constants. Shared subexpressions and arbitrary nonnegative real
constants are allowed; branches, divisions and other primitives are outside
this circuit class. Scalar operations, not unbounded-fan-in SUM nodes, are
counted. Creating x_e, retaining counts and paying bit complexity can only
add costs to this declared computation.

Write `r_n=min{r: binom(r,2)>=ceil(D/3)}`. The circuit size s obeys

`s >= 2^(r_n-1)/(D+1) = 2^(n/sqrt(3)-O(log n))`.

An explicit sum over the2^(n-1) worlds costs O(D*2^n), giving the scoped
order **2^Theta(n)**. This law needs no P!=NP assumption. Its exactness is
uniform over all finite count histories, rather than over one finite grid.
There is no finite precision or horizon certificate in that uniform premise.

Agreement only on the actual count grid suffices for polynomial identity.
If the circuit polynomial P equals Z_n on `{9^-c:c>=0}^D`, fix all but one
coordinate: their difference is a univariate polynomial with infinitely
many distinct roots. Its coefficients vanish on the remaining grid. Repeat
inductively. Thus P=Z_n as formal polynomials. This uses a Cartesian set of
legal histories; it does not assume real-valued latent inputs or density of
the grid. The finite audit is not used to prove this infinite-grid step.

## 2. Complete every edge with at most D+1 overhead

Introduce two variables a_e0,a_e1 per edge and the completed polynomial

`F_n(a) = SUM_{z:z0=0} PRODUCT_e a_e,(z_i XOR z_j)`.

Every monomial now contains exactly one variable from every edge group and
has degree D. A size-s monotone circuit for Z_n yields a size-at-most(D+1)s
monotone circuit for F_n, as follows.

Remove useless and zero gates. Since the output Z_n is multilinear and no
coefficient can cancel, useful factors at a PRODUCT have disjoint variable
sets. For each gate g let V_g be the union of variables occurring in its
monomials. Inductively complete its polynomial by replacing each monomial
with its product of a_e1 on present edges and a_e0 on absent edges of V_g.

A variable maps to a_e1 and a constant is unchanged. At a PRODUCT the child
variable sets are disjoint, so multiply their completions. At a SUM with
children u,v and V=V_u union V_v, multiply each child's completion by
`PRODUCT_{e in V minus V_child} a_e0`, then add. This inserts at most D
multiplications at an original SUM, since the two missing sets are disjoint.
The original SUM remains one operation. No expansion into monomials is used
by the transformation, and shared gates stay shared. At the output V=E,
giving F_n with the claimed overhead.

This step is essential: independent factors for cut and non-cut edges are
not silently assumed as the count decoder's interface. The lower bound below
transfers to the single bounded factor per edge that actual label0 histories
provide.

## 3. Balanced products cover the cut words

In a monotone circuit for F_n, every useful gate has a fixed subset S of
edge groups, with exactly one variable from each group in every monomial.
To see this, choose one nonzero output context for that gate. Multiplying
any of its monomials by the context must produce a legal output monomial.
Since all output monomials have the same edge-group degrees, the gate's
group degrees cannot vary. PRODUCT children therefore partition S; SUM
children have the same S.

Every output monomial has a parse tree containing an internal gate whose
group count is greater than D/3 and at most2D/3. Descend through SUMs and
through a largest PRODUCT child while its group count exceeds2D/3. At the
first crossing the larger child has more than D/3 groups. A leaf has degree
at most1, so D>=3 ensures this chosen gate is internal.

For such a gate g, combine its monomial support with the support of its
output contexts. No parse monomial can use g twice, because S is nonempty
and output monomials use each edge only once. The resulting product support
lies inside F_n and separates S from E minus S. Taking all balanced gates
covers every output monomial, using at most the number of circuit operations.
Coefficient duplication is harmless: this is a support cover, not a claim
of unique coefficients in a decomposition.

This is the classical balanced-product method; compare
[Jukna (2015), Lemma6 and section7](https://arxiv.org/pdf/1502.01865).
Related monotone cut-polynomial bounds appear in
[Grochow (2017), section4.2](https://theoryofcomputing.org/articles/v013a018/v013a018.pdf).
The proof here is self-contained for the exact count-factor interface and
its edge-completion reduction, without a general novelty claim.

## 4. Correlation limits each positive product rectangle

Identify a monomial of F_n with its cut word
`delta(z)=(z_i XOR z_j)_(ij in E)`. These2^(n-1) words form a binary linear
space C. Fix an edge partition S,T, and let a nonempty rectangle A times B
of partial words lie inside C. Fix(a0,b0) in it. For every a in A,
`(a XOR a0,0)` belongs to C; similarly `(0,b XOR b0)` belongs to C.

Let kappa(S) be the number of connected components of(V,S), including isolated
vertices. A cut word that is zero on T comes from bits constant on each
T-component. Anchoring z0 leaves kappa(T)-1 free component bits. Hence

`|A| <= 2^(kappa(T)-1)`, `|B| <= 2^(kappa(S)-1)`,

`|A times B| <= 2^(kappa(S)+kappa(T)-2)`.

The bound is attainable: add any fixed cut word to the two independent
subspaces supported only on S and only on T. In particular, it is not
obtained by counting parameter incidences or assuming explicit world slots.

For the complete graph, at least one of(V,S),(V,T) is connected. If one is
disconnected, every edge between its components belongs to the other and
connects that other graph. A graph on n vertices with k components has at
most `binom(n-k+1,2)` edges: with a fixed component count, concentrating all
non-isolated vertices in one component maximizes this convex sum.

For a balanced partition both edge sets have at least ceil(D/3) edges. Thus
both component counts are at most n-r_n+1, and one is1. Every balanced
rectangle has at most2^(n-r_n) cut words. Covering all2^(n-1) words therefore
requires at least2^(r_n-1) balanced products. Section3 gives that lower bound
for the operation count of F_n. Section2 transfers it to Z_n divided by D+1,
which proves section1. The direct positive sum over worlds supplies its
exponential-order upper bound.

## 5. What this does and does not settle for FP

Small count memory does not make a fixed positive exact partition decoder
polynomial-size, even with bounded factor inputs and free shared subexpressions.
The [factorized learner closure theorem](FACTOR_SIMPLEX_POSTERIOR.md) addresses
a different proposed shortcut: keeping only independent marginals loses
correlation under legal coupled observations. Together they delimit two
specific simplifications without asserting that explicit world slots are
the only possible learner representation.

The circuit theorem does **not** transfer automatically through normalization.
For example, the positive masses `M_0=1+Z_n`, `M_1=1+Z_n` both contain the
hard polynomial, while their normalized forecast is exactly(1/2,1/2), which
has a constant-size native realization. This is a counterexample to the
general implication, not a statement that the actual relation forecast is
constant. Its existing all-algorithm approximate lower bound remains the
separate P!=NP-conditional theorem.

The subsequent [positive rational readout compiler](POSITIVE_RATIONAL_READOUT.md)
gives a nonconstant infinite-family separation: shifted directed-tree odds
are expensive positive polynomials, but their normalized forecasts have
polynomial-size native graphs with bases(1,1). This follows from a general
positive fraction-pair/constant-excess construction. Its particular emitter
has factorial degree growth and declared exact/binary64 refusals, so small
syntax is still not a physical resource guarantee.

The result also does not constrain a single fixed history, adaptive changes
of circuit, algorithms with other primitives, finite declared horizons or
approximate/UNRESOLVED decisions. Paying to compute likelihood powers, exact
operand bits, native full states, provenance and transport remains necessary
in real executions. A finite source/resource contract may refuse well before
the asymptotic family is relevant. No current worker failure, memory threshold,
wall-clock time, AMP error or constructor-class decision is deduced from it.
This is a decoder-complexity result, not an extension of the closed static
PRODUCT/SUM/range/precision contract study.

## 6. Exact audit

Run `python -B experiments/joint_uncertainty/positive_count_partition.py`.
The [minimal evidence](../../evidence/minimal/FP_POSITIVE_COUNT_PARTITION.json)
retains only aggregate counts, small constructions and a scope counterexample:

- All29,614 balanced edge partitions for n3 through n6 are checked against
  the independently enumerated cut compatibility relation. Its complete
  bipartite components verify the exact maximum rectangle size and cover count.
- Five actual arithmetic DAGs, n3 through n7, pass symbolic edge completion
  with exact monomial coefficients and the(D+1) overhead bound.
- 91 independent nonnegative count vectors are realized as actual native
  histories:273 unit commits and1,267 all-pair forecasts. Their selected
  states equal the bounded-factor partition oracle; native totals stay10.
- Three exact positive-base cases verify cancellation to a constant forecast.

These finite checks support the stated proof, rather than replacing its
arbitrary-n, arbitrary-circuit or infinite-history arguments. They add no
Runtime source, constructor, installation path or GPU outcome.
