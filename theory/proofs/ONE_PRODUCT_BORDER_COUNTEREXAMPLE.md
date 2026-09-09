# One PRODUCT approaches a task whose exact minimum is two

Status: **PROVED COUNTEREXAMPLE**, 2026-09-09. A bound on semantic PRODUCT
count and final normalization range does not make the native model class
closed. Exact exclusion consequently need not give any positive loss margin.

## 1. Declared task and class

Use three binary inputs x,z,w with their six scalar unary indicator sources.
Write x_0=1[x=0], x_1=1[x=1], and similarly for z,w. Programs are finite
acyclic positive SUM and binary PRODUCT graphs with fixed nonnegative
coefficients, arbitrary sharing and one final normalization. The base is
`(1,1)`. There is no recurrence, internal normalization or enriched source.

Define the selector table

`f=x_0 z_0+x_1 w_0`.

Its values in lexicographic context order are `(1,1,0,0,1,0,1,0)`. With uniform
contexts, the binary task is

`p_1=(1+f)/(2+f)`:

probability 2/3 where f=1 and 1/2 where f=0. Impose the final-normalizer cap
T<=3. The exact result and its approximation contrast are

\[
\boxed{P_{exact\ Bayes}=2,\qquad
\inf_{P\le1,\ T\le3}L=L_{Bayes}.}
\]

The one-PRODUCT infimum is unattained. Two direct products construct f and
give masses `(1,1+f)`, so the two-PRODUCT upper bound is immediate.

## 2. The selector mass itself needs two PRODUCTs

Every one-PRODUCT scalar DAG has excess output `A+c h`, where A is
nonnegative unary-additive, c>=0, and h is a PRODUCT of two nonnegative
unary-additive parents. At every zero of f, A must vanish if A+c h=f.
Each unary indicator is positive at at least one of those zero contexts;
hence A=0. Absorb c into a parent and suppose f=UV.

The zero set of a nonnegative affine function of binary indicators is a cube
face (possibly empty or the whole cube). The four zeros of f are
`010,011,101,111`. Their only covering by two zero faces is the pair of edges
`x=0,z=1` and `x=1,w=1`, up to exchange. This can be checked directly: the
zero graph is the path `010--011--111--101`; no two-dimensional face is
contained in it, and only its two outer edges cover all four vertices.

The parents must therefore have the forms

`U=a x_1+b z_0`, `V=c x_0+d w_0`, with a,b,c,d>0.

At context 001 the equality f=UV gives bc=1. At 000 it gives b(c+d)=1,
contradicting bd>0. Thus no one-PRODUCT graph realizes the exact scalar mass f.
The Boolean support alone would not detect this obstruction: the PRODUCT
`(x_1+z_0)(x_0+w_0)` has exactly the correct support but overcounts overlaps.

## 3. Changing conditional normalization scales cannot evade the cap

The mass obstruction alone does not yet exclude a different conditional
realization. Write the two excess masses of any one-PRODUCT program as
`E_y=A_y+c_y h`.

At every f=1 context the target probability 2/3, the base bound M_0>=1 and
T<=3 force exactly `(M_0,M_1)=(1,2)`. Thus A_0 and c_0 h vanish there.
Those four contexts contain both values of each input, so nonnegative unary
A_0 must vanish everywhere.

If c_0=0, M_0=1 everywhere, and the task fixes E_1=f, contradicting the
preceding one-PRODUCT mass obstruction. If c_0>0, h=0 at all f=1 contexts.
Hence A_1=1 at 000,001,100,110. These four points affinely span the cube,
forcing the affine function A_1 to be constant one. At f=0, the target 1/2
then requires M_0=M_1>=2, violating T<=3. Both cases are impossible.

This proves the exact two-PRODUCT minimum for the **conditional** task under
the stated cap, rather than silently fixing its normalization scales.

## 4. A one-PRODUCT sequence in the same final range

For 0<epsilon<=1/2, partition exclusivity x_0 x_1=0 gives

\[
\frac{(x_0+\epsilon w_0)(x_1+\epsilon z_0)}\epsilon
=f+\epsilon z_0 w_0.
\]

Use this one PRODUCT with final excess

`e_epsilon=(1-epsilon)(f+epsilon z_0 w_0)`.

The overlap indicator z_0 w_0 can be nonzero only where f=1. Consequently
e is zero where f=0, is 1-epsilon at the two non-overlap positive contexts,
and is 1-epsilon^2 at the two overlap contexts. Thus masses `(1,1+e)` satisfy
the same T<=3 cap, and

\[
\boxed{\|q-p\|_\infty=
\frac{\epsilon}{3(3-\epsilon)}\le\epsilon/6.}
\]

For positive contexts q_1 lies in [3/5,2/3], so q_1(1-q_1)>=2/9.
The elementary Bernoulli KL upper bound
`KL(p||q)<=(p-q)^2/[q(1-q)]` and the four positive contexts give

\[
0<L(q)-L_{Bayes}\le\epsilon^2/16.
\]

Therefore the full one-PRODUCT class has zero Bayes loss gap despite exact
non-realizability. Treating exact exclusion as a robust structural certificate
would be false.

## 5. Small local coefficients and bounded activations do not repair closure

The displayed formula has an output scale growing like 1/epsilon. This is
not the only realization. Take epsilon=2^-k, integer k>=1, and use only the
fixed local coefficient alphabet `{1/2,1,2}`:

1. k successive halvings each of w_0 and z_0 form the two epsilon tails.
2. Two SUM nodes form x_0+epsilon w_0 and x_1+epsilon z_0.
3. One PRODUCT multiplies them.
4. k successive doublings recover h=f+epsilon z_0 w_0.
5. Form h/2,...,h/2^k by k halvings and sum these k terms. Their sum is
   `(1-2^-k)h=e_epsilon`.

This uses exactly one PRODUCT and 4k+3 SUM nodes before the readout. Every
source and intermediate feature lies in [0,2], both final masses are at most
2, and the final total is at most 3. All local coefficients come from a
fixed finite alphabet; no growing trained coefficient encoding is needed.
Nevertheless the class remains nonclosed because its SUM construction length
and exact intermediate precision are unbounded.

This does not contradict the finite complete-physical-state decision theorem.
PRODUCT count, a local coefficient cap and an activation cap do not bound
the complete construction work, depth, storage or numerical state. A genuine
finite machine/operation budget must account for those coordinates. At a
fixed finite graph/finite encoding decision class, ordinary finite
decidability remains intact.

There is also a simple sufficient compactness condition for a real-arithmetic
static relaxation: finitely many source/type choices, a bound on **all** nodes
and coefficient slots (including fan-in), and compact coefficient domains.
There are finitely many allowed DAGs; each has a compact parameter space and
a continuous prediction map because the readout base stays positive. Their
finite union is compact. An exactly excluded positive target then has a
strictly positive minimum CE gap. The present families violate respectively
the coefficient bound or the bound on all SUM construction nodes. This
explains precisely why a complete resource class can support a margin that
a PRODUCT-only class cannot.

The positive tails cannot be deleted because they tend to zero: the legal
later doubling chain recovers their task-relevant contribution. Conversely,
the exactly contradictory term x_0 x_1 is zero on every context in the declared
partition source domain. Its removal in this static algebraic proof is
justified by that source contract, not by a numerical threshold.

## 6. A strong zero-PRODUCT comparison still has a positive margin

The full SUM-only class has exact sup-norm distance 1/12 from the task,
including under cap 3. The positive contexts 001 and 110 and negative
contexts 010 and 101 satisfy

`001+110=010+101` as coordinate vectors.

At threshold 7/12, a predictor with error <1/12 would have the affine
function `M_1-(7/12)T` positive at the first pair and negative at the second.
The displayed affine identity forbids this. The constant prediction 7/12
attains distance 1/12 with masses `(1,7/5)` and total 12/5<=3.
Uniform-context Pinsker consequently gives an all-SUM CE gap at least 1/576.

Thus a finite one-PRODUCT witness can robustly beat **every** SUM model,
while no positive loss margin separates one PRODUCT from two. For example
k=3 already has excess <=1/1024<1/576 by the explicit bound above.
This compares complete static classes rather than a deliberately weak
constant-only baseline.

## 7. Arithmetic and certificate scope

The audit evaluates the actual local-alphabet DAG with exact fractions and
with an explicitly ordered CPU float64 path. At k=54, float64 rounds its final
excess table to f exactly, although the exact rational table still differs
by 2^-54 at the two non-overlap contexts. Thus exact equality of the floating
output cannot certify exact real-arithmetic representability by one PRODUCT.

This is not a Foundation counterexample: registered numerical arithmetic and
reference-to-AMP approximation evidence belong to the complete claim. The
counterexample rejects substituting rounded output equality for the declared
exact algebraic decision class. It performs no GPU/AMP installation audit.

Known fixed positive-cone closure results are also unaffected: this example
varies the PRODUCT parents and the construction resources, so it is not a
single preregistered fixed atom cone. Boolean support feasibility, fixed-mass
realizability, conditional exactness, approximation closure and finite-machine
reachability must keep their separate scopes.

Exact and float64 reference audit:
`theory/numerical_checks/one_product_border_audit.py`.
