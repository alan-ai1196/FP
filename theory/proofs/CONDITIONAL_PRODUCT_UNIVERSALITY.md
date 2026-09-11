# Exact PRODUCT cost of positive conditional universality

Status: **PROVED; EXACT RATIONAL CONSTRUCTION AND RANK AUDIT**, 2026-09-11.
On the full d-bit cube, d>=1, the worst-case PRODUCT count needed to realize
every strictly positive finite conditional table, when the final normalizer
is unrestricted, is exactly `2^d-d-1`. A fixed monomial feature bank attains
this count. The full-rank identity-noise table supplies the matching lower
bound even for approximation with unbounded normalizers.

For three-bit identity noise, four PRODUCTs attain exact prediction at cap
108; no three-PRODUCT graph can approach the target at any cap. Cap 108 is
also proved optimal within this fixed four-monomial bank, but is only an
upper bound on the minimum range of the full variable-parent four-PRODUCT
class.

## 1. Class and normalized rank bound

Use N=2^d complete binary contexts, the 2d scalar unary indicators, arbitrary
finite positive SUM/binary PRODUCT DAGs, fixed finite nonnegative real
coefficients and base one per output label. There is one final normalization,
no recurrence, and no context-dependent controller or acquired extra source.
PRODUCT count is the number of scalar nodes, with sharing counted once.

The source table spans exactly the (d+1)-dimensional affine space on the
cube. Flattening only final SUM paths expresses every mass column as a
linear combination of those sources and the P PRODUCT feature columns.
The constant readout base already belongs to the source span. Hence

`rank(M)<=d+1+P`.

Row normalization is multiplication on the left by a positive invertible
diagonal matrix. Therefore the prediction table Q also satisfies

`rank(Q)<=d+1+P`.

This bound survives arbitrary prediction limits: all minors of larger
order remain zero, even when the underlying normalizers diverge. It is a
static output-table rank bound, not a recurrent state-coordinate or general
FP memory bound.

Take N output labels and target

`Pi=(I_N+1*1^T)/(N+1)`.

It has rank N. Thus both exact realization and arbitrary approximation
require P>=N-d-1. The argument uses the full native static class, not the
monomial bank used for the upper construction.

There is an explicit cap-independent gap below this count. If rank(Q)<N,
choose a left-null vector w with ||w||_1=1. Since Q is row-stochastic,
`w^T*1=w^T*Q*1=0`, so

`w^T*(Pi-Q)=w^T/(N+1)`.

Consequently

`||Q-Pi||_max >= ||w||_infinity/(N+1) >= 1/[N(N+1)]`.

With uniform contexts, excess CE is at least
`2/[N^3(N+1)^2]` nats. This follows by Bernoulli coarsening at an entry
attaining the sup error, Pinsker and averaging over N contexts.

The probability constant is sharp for the larger rank-deficient stochastic
matrix class. For a balanced vector v with entries +1 and -1, the positive
row-stochastic matrix `Pi-v*v^T/[N(N+1)]` has rank N-1 and attains the
distance. Its membership in the smaller native PRODUCT class is not claimed.

## 2. A fixed bank with exactly N-d-1 PRODUCTs

For every subset S of coordinates let

`phi_S(x)=product_(i in S) x_(i,1)`.

The empty product is the constant one, available as a SUM of a unary
partition. Singleton subsets are already source indicators. For every
|S|>=2, choose one i in S and form phi_S=phi_(S without i)*x_(i,1), in an
order where its parent is available. Each such subset needs one PRODUCT.
The total count is

`sum_(j=2,...,d) binom(d,j)=N-d-1`.

Every bank feature is exactly zero or one. The bank's topology is independent
of the target probabilities; only the positive readout coefficients change.

## 3. Positive conditional tables admit positive coefficients after row scaling

Let p_j(T)>0 be any known finite conditional table, with any finite output
alphabet and sum_j p_j(T)=1 at every context. Define

`Gamma=max_j [max_T p_j(T)/min_T p_j(T)]`,

choose `L>=d*(1+Gamma)`, and choose `C>=max_j 1/p_j(empty)`.
Assign normalizers and masses

`T_mass(T)=C*L^|T|`, `M_j(T)=C*L^|T|*p_j(T)`.

Use the unique multilinear coefficients of E_j=M_j-1 in the phi_S basis.
The constant coefficient is `C*p_j(empty)-1>=0`. For nonempty S, the
constant minus one cancels in the alternating subset sum, leaving

`b_(S,j)=C*sum_(U subset S) (-1)^|S without U| * L^|U| * p_j(U)`.

Write s=|S|. Its leading term is positive, and bounding all proper-subset
terms by their absolute values gives

```
b_(S,j) >= C*L^s * [p_(j,min)
                    -p_(j,max)*((1+1/L)^s-1)].
```

For s<=d, the binomial expansion is bounded by a geometric series:

`(1+1/L)^s-1 <= sum_(r>=1)(d/L)^r = d/(L-d) <= 1/Gamma`.

Thus every coefficient is nonnegative. The positive readout reproduces all
M_j exactly by finite subset inversion, and its sum is the chosen normalizer.
In particular, each mass is at least one; this follows from the actual
nonnegative excess expansion, not a separate assumption about p away from
the empty context. The maximum normalizer is bounded by C*L^d.

Combined with section 1, this proves **exact worst-case conditional
universality count N-d-1**, and the same worst-case count for approximation.
Universality here ranges over finite output alphabets; the lower witness
uses N labels. This is not a sharp count theorem for every target or for
every fixed smaller output alphabet.

The construction assumes the complete target table is known. It supplies no
legal acquisition transcript, trained initializer, optimizer reachability,
persistence evidence or automatic install permission.

## 4. Rational inputs permit finite integer construction

If p is rational, choose C to be a common multiple of all probability
denominators, and choose an integer L>=d*(1+Gamma). Then all masses and
multilinear excess coefficients are nonnegative integers. C*p_j(empty)>=1
holds automatically. Positive integer coefficients can be implemented by
binary Horner SUMs with local weights {1,2}, without adding a PRODUCT.

This gives a finite encoded graph for rational data. Its normalizer and
SUM/bit costs can be large and are genuine resources; no finite-cap or
fixed-arithmetic guarantee follows just from the PRODUCT count. Irrational
input tables are covered only by the stated real-coefficient theorem.

## 5. A four-PRODUCT three-bit identity witness at cap 108

Use the four higher monomials xy,xz,yz,xyz, with the triple sharing one
pair. Let u_t depend on context Hamming weight t:

`(u_0,u_1,u_2,u_3)=(1,5/3,4,12)`.

Set `M_j(T)=u_|T|*(1+1[j=T])`. The normalizers are
`9,15,36,108`, so the cap is 108.

For the degree-two monomial S the baseline coefficient is
`u_2-2u_1+u_0=5/3`; for the degree-three monomial it is
`u_3-3u_2+3u_1-u_0=4`. Add the label-specific term
`1[j subset S]*(-1)^|S without j|*u_|j|` to each coefficient. All are
nonnegative. In particular, the potentially negative pair/singleton and
triple/pair terms are exactly zero.

The remaining affine parts use the full unary basis. For label 000 the
remainder is `(x_0+y_0+z_0)/3`. For a singleton label with its one-coordinate
i it is `(7/3)*x_(i,1)+(2/3)*sum_(j!=i)x_(j,1)`. For the other labels it
is `(2/3)*(x_1+y_1+z_1)`. These are nonnegative native SUMs, not signed
linear terms supplied to the model.

Therefore the full variable-parent native class has exact and approximation
PRODUCT minima **four at every cap R>=108**. For every P<=3, section 1
gives probability error >=1/72 and CE gap >=1/20736 at every cap, including
unbounded range.

Multiplying every mass of this witness by three preserves probabilities and
gives integer excess coefficients after adjusting the base. It yields a
{1,2}-coefficient implementation with four PRODUCTs and cap 324. This is a
finite-alphabet upper witness, not a sharp finite-alphabet range theorem.

## 6. Cap 108 is optimal for this fixed monomial bank

This section fixes the bank xy,xz,yz,xyz while retaining arbitrary positive
unary readouts and all normalizers. It does not fix a hand-selected readout
or require nonnegative one-sided affine slopes.

An exact identity prediction has masses u_T*(1+1[j=T]), with u_T>=1.
Averaging over the six coordinate permutations preserves this fixed cone
and cannot increase the maximum normalizer. Relabel outputs by the same
permutation. Thus it suffices to consider u_0,u_1,u_2,u_3 depending on
Hamming weight. This convexity argument is not available for averaging
arbitrary variable-parent four-PRODUCT graphs.

Nonnegative higher-degree coefficients and the affine remainder of head
000 at 111 imply

```
e_0 = u_0-1 >= 0,
e_a = 3u_1-4u_0-1 >= 0,
e_2 = u_2-3u_1+u_0 >= 0,
e_3 = u_3-4u_2+3u_1-u_0 >= 0.
```

The exact nonnegative combination

`u_3-12 = e_3+4e_2+3e_a+9e_0`

proves cap R>=9u_3>=108. The witness in section 5 attains equality. This
is a complete lower bound for the declared fixed feature bank. The minimum
range of the full variable-parent four-PRODUCT class could be smaller and
is not decided by this certificate.

## 7. What this says about the earlier decoder phases

For three-bit identity noise, the canonical results now establish:

- at cap nine, exact minimum twelve and approximation minimum nine;
- immediately above nine, through 9<R<243/26, exact and approximation minima nine;
- at cap 108 and above, exact and approximation minima four;
- at any cap, three or fewer have a positive loss gap.

The intermediate thresholds are open. The result demonstrates why a PRODUCT
count without its normalization/resource contract is incomplete: the same
target has different forced structure at different caps. All normalizer
choices in these statements remain explicit.

## 8. Audit scope

`conditional_product_universality_audit.py` verifies exact feature counts,
rational positive-target constructions, integer local-alphabet graphs,
original-DAG and normalized-table ranks, exact left-null witnesses, the
rank-relaxation equality examples, every entry of the cap-108 and cap-324
graphs, and the fixed-bank linear identity. Rejection by this fixed bank
is deliberately separated from rejection by the complete native class.

No generic recurrent-state rank claim, unregistered target information,
free normalizer/bit budget, value-path guarantee or reference/AMP bridge is
introduced.
