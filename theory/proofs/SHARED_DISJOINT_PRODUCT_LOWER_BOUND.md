# Disjoint outputs force additional shared PRODUCTs, including in closure

Status: **PROVED; EXACT RATIONAL AUDIT**, 2026-09-11. A last-PRODUCT
comparison transfers scalar approximation lower bounds to shared outputs.
It closes the three-versus-four boundary for three-bit conditional parity
at its minimum final-normalizer cap. No numerical search is needed for
the transfer; the scalar separation uses the previously stored exact proof.

## 1. Static class and comparison lemma

Fix a finite context domain and any fixed nonnegative scalar sources. A
program is a finite positive SUM/binary PRODUCT DAG with arbitrary sharing,
arbitrary finite fixed nonnegative real coefficients, and k nonnegative
scalar excess outputs E_i. There is no recurrence or internal normalization.
PRODUCT count is the number of scalar nodes in this static graph. All SUM
paths may be flattened for an extensional comparison; no bound on internal
values or coefficients is assumed.

Let f_1,...,f_k be nonnegative target tables with pairwise disjoint positive
supports, and put delta_i=||E_i-f_i||_infinity. If the graph has P>=k-1
PRODUCTs, there is a scalar graph using at most P-k+1 of them, on the same
source basis, whose distance from one of the f_i is at most

`delta_1+...+delta_k`.

**One-step proof.** Topologically order the PRODUCTs and call the last H.
After flattening only SUM paths, write

`E_i=B_i+c_i H`, c_i>=0,

where each B_i uses only the preceding P-1 PRODUCTs. Choose j with maximal
c_j, discard head j for this comparison, and remove c_i H from each
remaining head i. At a context where f_i>0, disjointness implies f_j=0, so

`0<=c_i H<=c_j H<=E_j<=delta_j`.

If all c_i are zero, the same statement holds without division. At a context
where f_i=0, nonnegativity gives `0<=B_i<=E_i<=delta_i`. Thus the surviving
head's error is at most delta_i+delta_j.

**Iteration with the original errors.** Repeat on the current last PRODUCT
and current remaining heads, k-1 times. Every current output is pointwise
at most its original E_i: only nonnegative last-PRODUCT contributions have
been removed. At a positive context of the eventual surviving target, the
term removed when head j is discarded is therefore at most the *original*
delta_j. The total loss at that context is at most the sum of those errors.
At a zero context the comparison output stays between zero and the original
E_i. This proves the stated sum bound, rather than a recursively doubled
error estimate. The remaining PRODUCT prefix is an actual static graph.

The underlying argument is stronger and does not need disjoint targets:
for some surviving head i the prefix satisfies, pointwise,
`max(0,E_i-sum_(j!=i) E_j)<=B_i<=E_i`. Every removed contribution is at
most the original discarded head at the same context. Disjointness is
needed only for the stated target-error transfer. This surplus form is used
for the multi-label consequence in
[`SOURCE_INTERSECTION_PRODUCT_BOUND.md`](SOURCE_INTERSECTION_PRODUCT_BOUND.md).

This is a comparison between functions in static expressivity classes. It
does not authorize deleting Runtime state, reusing a certificate, discarding
provenance, or transporting a learner. Its graph transformations need not
preserve SUM budgets, registered values or future continuations.

## 2. A direct lower-bound consequence

Suppose r>=1 and every f_i has scalar distance at least Delta_i>0 from the
full class with at most r-1 PRODUCTs. Every joint graph with at most
r+k-2 PRODUCTs then satisfies

`sum_i ||E_i-f_i||_infinity >= min_i Delta_i`,

and in particular

`max_i ||E_i-f_i||_infinity >= (min_i Delta_i)/k`.

Apply section 1 at P=r+k-2. A graph with fewer PRODUCTs belongs to this
at-most class and can be padded with unused zero products in the comparison
normal form. Therefore the joint approximation PRODUCT minimum is at least
r+k-1. The exact-only version follows from exact scalar exclusions by
setting all delta_i=0; exact exclusions alone do not supply positive gaps.

The assumptions matter. Duplicating the same three-bit parity head allows
both copies to share an exact three-PRODUCT graph, violating a four-PRODUCT
conclusion without disjointness. For r=0, arbitrarily many disjoint source
indicators may all be read out using zero PRODUCTs. Choosing the discarded
head arbitrarily also fails: with `H=x_0*x_0`, outputs `(H,x_1+epsilon H)`
and targets `(x_0,x_1)`, discarding the smaller-coefficient second head and
removing H from the first creates error one from original total error
epsilon. The maximum-coefficient choice avoids this failure.

## 3. Three-bit complementary parity has joint minimum four

Use the complete three-bit cube with its six unary indicators. The
independently checked rejection tree in
[`PRODUCT_SUPPORT_CLOSURE.md`](PRODUCT_SUPPORT_CLOSURE.md), section 6,
proves the scalar bound

`inf_(P<=2) ||g-1_odd||_infinity >= Delta = 1/18432`.

Flipping one source coordinate gives the same bound for 1_even. Each scalar
target is exactly realized with three PRODUCTs. They have disjoint supports,
so section 2 gives, for arbitrary a>0 and any shared graph with at most
three PRODUCTs,

`max(||E_0-a*1_even||_infinity, ||E_1-a*1_odd||_infinity) >= a*Delta/2`.

Four PRODUCTs suffice simultaneously:

```
e = (x_0+y_1)(x_1+y_0)
o = (x_0+y_0)(x_1+y_1)
v_even = (e+z_1)(o+z_0)
v_odd  = (e+z_0)(o+z_1)
(E_0,E_1) = a*(v_even,v_odd).
```

The source partitions imply `eo=0` and `z_0 z_1=0` on the full declared
cube. Consequently the last two nodes are exactly the complementary parity
indicators. Both the exact and approximation joint mass minima are four.

## 4. Conditional parity: keep all normalizers

Take binary label noise eta in (0,1/2), positive readout base (1,1), and
one final normalization with `T=M_0+M_1<=R=1/eta`. Write a=R-2. The target
assigns probability `(R-1)/R` to the correct parity label and `1/R` to the
other. R is the minimum possible cap for exact Bayes prediction: both masses
are at least one, so a probability 1/R forces T>=R. At this cap an exact
Bayes realization has excesses `(a*1_even,a*1_odd)`.

For approximation we cannot assume these normalizers in advance. Let delta
be the maximum probability error over contexts and labels, and retain
every feasible T<=R. At a correct-label context for head i, with j the
other label, the base and cap give

```
0 <= E_i <= a,
E_j <= R delta,
E_i >= 1/q_j-2 >= R/(1+R delta)-2
    = a-R^2 delta/(1+R delta) >= a-R^2 delta.
```

The first lower inequality uses `M_j>=1` and
`E_i=M_j*q_i/q_j-1`. At a wrong-label context for i, `E_i<=R delta`.

For a graph with at most three PRODUCTs, decompose the two heads at the last
PRODUCT as in section 1. Discard a head j of maximal coefficient and keep
the scalar prefix B_i with at most two PRODUCTs. On the surviving head's
positive target contexts the removed term is at most E_j<=R delta. On its
zero target contexts B_i<=E_i<=R delta. It follows that

`||B_i-a*1_(parity=i)||_infinity <= R(R+1) delta`.

The scalar separation is a*Delta by free positive output scaling. Therefore
every such conditional model satisfies

`delta >= (R-2)*Delta/[R(R+1)] > 0`.

For uniform contexts, average excess cross-entropy is average Bernoulli KL.
At a context attaining delta, Pinsker's inequality gives KL>=2 delta^2;
there are eight contexts. Thus

`L(q)-L_Bayes >= ((R-2)*Delta/[R(R+1)])^2/4` nats.

At eta=1/4 and cap R=4, the explicit bounds become

`probability sup error >= 1/184320`,

`excess CE >= 1/135895449600` nats.

These are conservative separation constants, not sharp optima. The four
PRODUCT construction has masses `1+a*v_even`, `1+a*v_odd`, and T=R at
every context, so it attains Bayes risk. At every eta in (0,1/2) and its
minimum cap, **both exact and approximation conditional PRODUCT minima
are four**. The earlier stronger numerical margin for P<=2 remains valid.

## 5. Audit and limits

`theory/numerical_checks/shared_disjoint_product_audit.py` checks the full
stored scalar rejection proof with integer/Fraction arithmetic, evaluates
actual shared and nested positive DAGs, reconstructs their SUM-flattened
outputs, and verifies each discarded contribution against the original
off-support error. Cases include repeated squaring, very large hidden
features with tiny readout coefficients, zero/tied coefficients, empty
supports, the overlapping-head and wrong-head counterexamples, and arbitrary
rational conditional scales. The four-PRODUCT witnesses are evaluated
directly. Random checks exercise the theorem; the proof is the inequalities
above, not the sample count.

The result does not cover recurrence, adaptive source acquisition, registered
value construction, full physical budgets, installation, fresh persistence
or the reference/AMP bridge. Larger normalizer caps need a new argument:
their target excess supports need not remain disjoint. General higher-bit
parity scalar counts and sharp positive loss margins remain open.
