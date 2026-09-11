# Arbitrarily small normalizer slack changes exact decoder complexity

Status: **PROVED; EXACT CONSTRUCTION AND SCALE AUDIT**, 2026-09-11. On the
three-bit eight-label identity-noise task, exact PRODUCT minimum jumps from
twelve at cap nine to nine immediately above it. Nine is proved minimal
through the open interval `9<R<243/26`. This upper endpoint is a certified
exclusion boundary, not a claimed sharp transition to eight PRODUCTs.

## 1. Static contract and the question being changed

Use the full d-bit cube, its 2d unary indicators, finite positive SUM/binary
PRODUCT DAGs with arbitrary sharing and fixed nonnegative real coefficients,
and base one for each of N=2^d output labels. There is one final
normalization. Contexts are uniform and

`p_j(T)=(1+1[j=T])/(N+1)`.

The minimum possible exact normalizer cap is R_0=N+1. At that cap the excess
matrix is forced to be the identity. With cap R>R_0, the allowed exact
excesses instead include

`E_j(T)=(s-1)+s*1[j=T]`, where `1<s<=R/R_0`.

Their common normalizer is R_0*s. The small positive off-diagonal mass is
part of the permitted scale, not a change to the target probabilities.

## 2. A positive readout of the same shared approximate basis

For 0<epsilon<1 form the uncontracted subset basis

```
B_empty = product_i (x_(i,0)+epsilon*x_(i,1))
B_S = epsilon^(-1)*B_(S without i)*x_(i,1).
```

As in `DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`, it uses N+d-2 PRODUCTs and

`B_S(T)=epsilon^(|T|-|S|)` when S is contained in T, and zero otherwise.

For each label j use the readout coefficients

`b_(S,j)=(s-1)*(1-epsilon)^|S| + s*1[j subset S]*(-epsilon)^|S without j|`.

If

`(s-1)*(1-epsilon)^d >= s*epsilon`,

all b_(S,j) are nonnegative. Even powers add positive terms; an odd-power
subtraction is at most s*epsilon, while its baseline is at least
(s-1)*(1-epsilon)^d. At any fixed s>1 the condition holds for sufficiently
small epsilon.

Two finite binomial identities verify the readout exactly:

```
sum_(S subset T) epsilon^|T without S| * (1-epsilon)^|S| = 1,
sum_(j subset S subset T) epsilon^|T without S| * (-epsilon)^|S without j|
    = 1[j=T].
```

Therefore `sum_S b_(S,j) B_S(T)=(s-1)+s*1[j=T]`. The alternating signs
occur in a proof of the coefficient formula; every actual FP coefficient
after combining its two terms is nonnegative. This is finite exact
realization, not equality only at epsilon=0.

Thus **every R>N+1 permits exact identity-noise prediction with N+d-2
PRODUCTs**, in the complete static class. This does not by itself prove
minimality at larger caps.

## 3. The exact witness can use the finite local alphabet

Given any positive slack h=R-R_0 sufficiently small, choose
`sigma=2^-m<=h/R_0<2*sigma`, set s=1+sigma, and choose
`epsilon=2^-k`, `k=m+ceil(log2(4d))`. Then sigma<=1, s<=2,
d*epsilon<=sigma/4, and

`sigma*(1-epsilon)^d >= 3*sigma/4 >= s*epsilon`.

Every b_(S,j) is a nonnegative dyadic rational. The source-to-basis graph
uses d(k+1)+k(N-1) weighted SUMs and N+d-2 PRODUCTs. A dyadic coefficient
`b=a/2^ell` can be applied by ell halvings followed by binary Horner SUMs
for the positive integer a, using only weights {1/2,1,2}. No additional
PRODUCT is introduced.

The denominator exponent ell is at most m+d*k and b<=3, so each coefficient
needs at most `2(m+d*k)+1` SUMs. Including the N final readout SUMs gives
the conservative complete excess-construction bound

`S <= d(k+1)+k(N-1)+N^2*(2(m+d*k)+1)+N`.

All basis features are <=1. Halving first and then building the integer
coefficient keeps every scaling intermediate at most max(1,b*B_S).
Since each contribution is bounded by its complete positive readout,
every intermediate excess feature is <=2s-1. The final normalizer is
exactly R_0*s<=R. For fixed d the SUM cost is O(log(1/h)). This is an
explicit finite graph, not a supplied negative readout or an uncharged
infinite-precision primitive. Registered value construction remains separate.

## 4. A stronger scalar obstruction below the shared count

On three bits every scalar at-most-one-PRODUCT excess g has distance at
least 1/4 from any singleton mass. To prove it, flip coordinates so that
the target point is 111, then set to zero the coefficients of source
literals that vanish at 111. This keeps g(111) unchanged and can only
decrease every other value, so cannot worsen the singleton error.

The remaining function has the form

`g'=sum_i a_i*x_i + sum_(i<j) b_ij*x_i*x_j`, a_i,b_ij>=0.

This follows by expanding C+U*V and using x_i^2=x_i. Its values at the three
neighbors of 111 sum to `2*sum a_i+sum b_ij>=g'(111)`. If its sup error is
delta, this implies `3*delta>=1-delta`, hence delta>=1/4.

The bound is sharp for the larger positive quadratic cone, whose witness
is `(x_1*x_2+x_1*x_3+x_2*x_3)/4`. That witness is not asserted to have one
PRODUCT. The exact optimum within the one-PRODUCT class is not determined.

## 5. Nine is still necessary on a positive cap interval

Now fix d=3, N=8 and R=9+h, with `0<=h<9/26`. Suppose an at-most-eight
PRODUCT model has probability sup error delta. The pointwise surplus lemma
from `SHARED_DISJOINT_PRODUCT_LOWER_BOUND.md` gives, for one head i, a
scalar prefix B_i with at most one PRODUCT and

`max(0,E_i-sum_(j!=i)E_j)<=B_i<=E_i`.

All models under this cap have `q_i<=1-7/R<1/2`. At head i's correct
context, therefore,

```
E_i-sum_(j!=i)E_j = (2q_i-1)T_mass+6
                 >= (2q_i-1)R+6
                 >= 1-5h/9-2R*delta = L.
```

Everywhere, B_i<=E_i<=1+h=U. At its wrong contexts,
`B_i<=E_i<=h/9+R*delta=W`. If L>0, rescale the comparison by 2/(U+L).
Since 2W<=U-L, its singleton error is at most

`(U-L)/(U+L) = (14h/9+2R*delta)/(2+4h/9-2R*delta)`.

The scalar 1/4 lower bound consequently gives

`delta >= (9-26h)/(45*(9+h))`.

For rigor it suffices to assume delta is strictly below this expression:
then L>3U/5>0 and the displayed rescaled error is strictly below 1/4,
a contradiction. Thus no positivity or denominator condition is assumed
outside its proved range. Uniform-context excess CE is at least one
quarter of this probability bound squared.

At h=0 this improves the earlier at-most-eight probability bound to 1/45
and its CE gap to 1/8100. At every `9<R<243/26`, the exact construction
in section 2 and the positive lower bound prove **exact minimum nine**.
Approximation minimum is nine throughout `9<=R<243/26`. At R=9 itself,
the exact minimum remains twelve by the separate exact support proof.

The endpoint 243/26 is not claimed to be attainable with eight PRODUCTs.
The lower-bound constants are conservative.

## 6. A joint slack/accuracy construction law

Fix d=3 and a PRODUCT budget p in {9,10,11}, with local coefficient alphabet
{1/2,1,2}. Let S count all weighted SUMs in the source-to-excess construction.
The final positive base and normalization are fixed task overhead.

The earlier positive-value theorem supplies
`tau=2^(-S*2^p)` as a lower bound for every nonzero excess. If probability
error delta<7/72, all correct excesses must be positive: a zero correct
excess would give q_i<=1/8 instead of 2/9. Exact singleton support is
impossible with fewer than twelve PRODUCTs, so some wrong excess is
positive. At cap R=9+h,

`tau <= E_wrong <= R*(1/9+delta)-1 = h/9+R*delta`.

This proves one lower bound retaining both resources:

`h/9+(9+h)*delta >= 2^(-S*2^p)`.

At zero error, S is at least `2^(-p)*log2(9/h)`; section 3 gives the matching
logarithmic upper rate. At zero slack, the earlier approximate decoder gives
S=13k+6 and delta<=2^-k/3. Using whichever positive allowance is larger
therefore gives, as h,delta tend to zero with h+delta>0,

`minimum SUM cost = Theta(log(1/(h+delta)))`.

For a CE excess tolerance rho, uniform-context Pinsker implies
delta<=2*sqrt(rho), and the approximate decoder has CE excess <=2*2^(-2k).
The corresponding joint law is

`minimum SUM cost = Theta(log(1/(h+sqrt(rho))))`.

These are fixed-p asymptotic rates with non-sharp constants. At h=delta=0
there is no finite realization in these PRODUCT classes. Fixed floating
formats or registered optimizers do not inherit the exact-arithmetic rate.

## 7. Evidence and remaining scope

`normalizer_slack_decoder_audit.py` evaluates actual dyadic SUM/PRODUCT
graphs, verifies every output and its common normalizer, checks nonnegative
coefficients and exact construction counts, audits the scalar source pruning
and neighbor inequality, and checks the cap/surplus/rescaling algebra with
arbitrary rational normalizers. Invalid readout coefficients are rejected.

The result changes no FP primitive and assumes no erasure of a small tail.
Larger-cap transitions to eight or fewer PRODUCTs, sharp one-PRODUCT scalar
distance, optimal SUM constants, and full physical/value/Runtime/AMP paths
remain separate problems.
