# PRODUCT capacity with a fixed output alphabet

Status: **PROVED; EXACT NORMAL-FORM AND CONSTRUCTION AUDIT**, 2026-09-11.
For N=2^d binary contexts and k>=2 labels, the worst-case PRODUCT budgets
for exact and approximate strictly positive conditional universality both
have order

`Theta(min(N,sqrt(N*k)))`

uniformly over k>=2 as d grows. In particular, fixed k costs Theta(2^(d/2)),
whereas k>=N has the exact count N-d-1. These are resource-scoped static
expressivity results; normalizer range and finite SUM/encoding work are not
bounded by the PRODUCT count.

A frozen numerical feature bank has a different lower bound. For binary
universality it needs at least N/2-d PRODUCT features, even with arbitrary
readout training. The smaller universal construction must therefore adapt
some intermediate feature values to the target. Its graph skeleton can be
fixed in advance; this is not a theorem forcing a changing topology.

## 1. Declared class and finite bounds

Use all 2d unary binary indicators, nonnegative real SUM coefficients,
scalar binary PRODUCTs with arbitrary sharing, base one per label and one
final normalization. No recurrence, extra source or internal division is
available. All programs are finite. For approximation, SUM work and
coefficients may grow along the sequence. Normalizer range is unrestricted.

Let U(d,k) be the least PRODUCT budget that realizes every strictly positive
N-by-k conditional table exactly. Let A(d,k) be the corresponding budget
whose prediction closure contains every such table. Write

`m(d,k,P)=P^2+(2d+k+1)*P+k*(d+1)`, `D=N*(k-1)`.

Let P_dim be the smallest nonnegative integer P with m(d,k,P)>=D. Then

```
max(0, P_dim, min(N,k)-d-1, ceil(log2(d))) <= A(d,k) <= U(d,k)
 <= min(N-d-1,
        min_(1<=a<=d-1) [(k+1)*2^a+2^(d-a)-d-k-2]).
```

For d=1 the inner minimum is omitted and ceil(log2(d))=0. These finite
bounds are not asserted equal for every small d,k. In particular the binary
three-bit universal count lies between two and three. Exact and
approximation universality have the same proved asymptotic order, not a
proved identical count in every fixed-alphabet case.

The rank bound min(N,k)-d-1 is the complete-class bound from
`CONDITIONAL_PRODUCT_UNIVERSALITY.md`: strictly positive full-rank tables
exist. The depth bound comes from noisy d-bit parity and the sub-degree
envelope. Extra labels can have fixed positive probability while the first
two retain the parity odds; their mass moments still force full degree.
At most P PRODUCTs have degree at most 2^P, including repeated squares.

## 2. An all-class finite parameter map

The unary tables span the affine basis (1,x_1,...,x_d). Order the P PRODUCT
nodes topologically. Flatten SUM paths in each parent into an affine
combination of the d+1 source-span coordinates and the j earlier PRODUCT
features, j=0,...,P-1. There are at most

`2*sum_(j=0,...,P-1)(d+1+j) = P^2+(2d+1)*P`

parent parameters. Flattening all final SUMs adds k*(d+1+P) parameters.
The positive readout base is already in the affine span. This is m(d,k,P).

Complementary source indicators give signed affine coefficients in this
description. Allowing arbitrary real coefficients only enlarges the map;
every original nonnegative graph is retained. This use of a signed
coordinate chart is a lower-bound relaxation, not a proposed native signed
SUM implementation or a provenance-preserving runtime replacement.

Arbitrarily many SUM nodes add no extra function-table parameters once
these paths are flattened. Product topology is also covered: coefficients
of unavailable or unused features are zero, and programs with fewer
PRODUCTs can be padded with unused nodes. Thus there is one finite
polynomial mass map for the entire stated P-budget class.

As polynomials in these parameters, the jth PRODUCT table has degree at
most 2^(j+1)-2 (j starts at one), and every final mass has degree at most
B=2^(P+1)-1. Predictions are rational functions of these same m parameters.

## 3. Parameter shortage excludes approximation, not just exact equality

Keep the first k-1 probabilities in each row as independent output
coordinates. They range over a nonempty open subset of R^D. All coordinates
share the polynomial denominator Z=product_x T_x. Each numerator and Z
has parameter degree at most E=N*B.

Consider every monomial in these D prediction coordinates of total degree
at most t. Clearing the denominator Z^t turns them into polynomials in m
parameters of degree at most E*t. There are

`binom(D+t,D)` output monomials and only `binom(m+E*t,m)` parameter monomials.

If m<D, the first count exceeds the second for some finite t, since their
growth degrees in t are D and m. Hence there is a nonzero polynomial F in
the independent probability coordinates such that F(Q)=0 for every legal
program. The equality holds wherever the original positive denominators
are defined. No assumption that those denominators stay bounded is needed.

This elementary algebraic dependence proves the closure statement: F is
continuous, so every prediction limit also lies in its zero set. A nonzero
polynomial cannot vanish on a nonempty open set, by induction on the number
of variables. Therefore some strictly positive rational conditional table
has F(p)!=0 and an open neighborhood disjoint from the whole P-budget
class. It has a positive approximation gap. No explicit sharp gap constant
for every such hard table is claimed.

This proves P>=P_dim for approximate universality, with arbitrary real
coefficients, hidden scales, sharing and increasing finite SUM work. It
does not depend on a numerical Jacobian rank estimate, a sampled topology
catalog or an assumption of closed coefficient parameter sets.

## 4. Positive block factorization supplies the matching upper order

Given the complete positive target p, use the proved scaling

`M_j(T)=C*L^|T|*p_j(T)`

with C and L as in `CONDITIONAL_PRODUCT_UNIVERSALITY.md`. Its excesses have
nonnegative multilinear coefficients b_(S,j). Split the d input coordinates
into disjoint blocks of sizes a and b=d-a, with a,b>=1. Build all monomial
features within each block, costing

`(2^a-a-1)+(2^b-b-1) = 2^a+2^b-d-2`

PRODUCTs. Sources and the constant one supply the empty and singleton
monomials. For each label j, distribute its excess polynomial as

```
E_j = b_(empty,j)
      + sum_(U nonempty) b_(U,j)*phi_U
      + sum_(V nonempty) b_(V,j)*psi_V
      + sum_(U nonempty) phi_U *
          [sum_(V nonempty) b_(U union V,j)*psi_V].
```

Every bracket is a positive SUM of the already built second-block
features. Each outer cross term uses one PRODUCT, at most k*(2^a-1)
across the k heads. This proves the finite upper bound in section 1.
All parent weights are target values obtained by the declared algebraic
construction. Its topology can be fixed before the target is known.

Taking 2^a near sqrt(N/(k+1)) gives O(sqrt(N*k)) PRODUCTs. When k is large,
use the earlier N-d-1 bank instead. For 2<=k<=N, the parameter inequality
in section 3 gives Omega(sqrt(N*k)) as d grows, uniformly in k. Indeed
k<=sqrt(N*k), d/sqrt(N*k) tends uniformly to zero, and d/N tends to zero;
putting P=o(sqrt(N*k)) makes m/(N*k) tend to zero, contradicting
D/(N*k)>=1/2. The same comparison with a sufficiently small fixed constant
gives a uniform Omega bound. For k>=N, the rank lower bound and original
monomial bank give the exact answer N-d-1. This proves the stated sharp
order in all alphabet regimes.

For example, uniform conservative constants are 1/8 and 4 for d>=6.
When 2<=k<=N and P<sqrt(N*k)/8, dividing m by N*k bounds its four terms
by `1/64`, `13/64`, `8/64` and `7/64`, respectively. The bounds on the
d-dependent terms decrease from d=6. Their sum is 29/64<1/2, whereas
D/(N*k)>=1/2. For the upper bound, if k+1<=N/4 choose
`2^a in (sqrt(N/(k+1))/2, sqrt(N/(k+1))]`; the count is at most
3*sqrt(N*(k+1))<4*sqrt(N*k). Otherwise k>N/8 and the full N-d-1 bank
already satisfies the upper bound. For k>=N use the exact rank result.

For rational p, integer choices of C,L give nonnegative integer b. Binary
Horner SUMs implement all coefficients using local weights {1,2}, with
unchanged PRODUCT count. Irrational tables have only the stated
real-coefficient exact construction; rational approximation suffices for
density if the value alphabet is restricted to finite integer constructions.

The factorization still uses the full N*k coefficient table in its SUM
parents and readouts. Its range is C*L^d, and its SUM edges, bits, acquisition
and physical resources have not disappeared. This is a saving in scalar
PRODUCT count, not a sublinear information requirement or a total-cost win.

## 5. Frozen numerical features cannot achieve the same universal compression

Now fix one numerical feature table before seeing p, including the original
unary span and P PRODUCT features. Let its total linear span W have
dimension r<=d+1+P. Enlarge the readouts to arbitrary signed vectors in W.
Their k mass columns have at most k*r real coordinates.

The common positive scaling of every mass does not change probabilities.
For this lower-bound relaxation, set the total mass at one fixed context
to one. This removes one parameter because the constant table is in W.
All legal positive predictions are retained even though scaled masses may
no longer satisfy the original base constraint. The rational parameter
map thus has at most k*r-1 variables.

The same dependence argument requires

`k*r-1 >= N*(k-1)`

for exact or approximate universality. Consequently every frozen bank needs

`P >= ceil((N*(k-1)+1)/k)-d-1`.

For binary labels this is N/2-d. At d=8, the adaptive block construction
uses at most 44 PRODUCTs for every positive binary table, whereas **every**
fixed numerical bank needs at least 120. At d=20 these upper and lower
counts are 3560 and 524268. These compare universal capabilities, not a
deliberately weak handpicked baseline.

Some intermediate feature values must therefore depend on the target at
the smaller budget. A preregistered skeleton with trainable SUM weights
can do that: the theorem does not force a graph-topology change, new model
action, unregistered source or free access to p. It supplies no optimizer
reachability or installation evidence.

## 6. Audit and remaining scope

`fixed_label_product_capacity_audit.py` checks complete rational block graphs,
their exact probabilities and PRODUCT counts, integer local-alphabet
realizations, normal-form reconstruction of arbitrary original shared DAGs,
and finite integer monomial-count witnesses for the dependence argument.
It also checks an explicit frozen-bank determinant obstruction, alongside
a legal two-PRODUCT variable-feature realization of that target.

Sharp small-(d,k) universal counts, possible exact/approximation count
differences, sharp finite range and SUM/bit tradeoffs, and acquisition,
registered value, physical and AMP paths remain open. Theorems about
static numerical feature spans do not lower-bound recurrent FP state size.
