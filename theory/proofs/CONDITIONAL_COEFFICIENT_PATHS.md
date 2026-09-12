# Complete coefficient paths for conditional closure

Status: **PROVED CHARACTERIZATION; EXACT NATIVE-PATH AUDIT**, 2026-09-12.
Every fixed-PRODUCT conditional prediction limit at unrestricted range has
a monomial coefficient path. At a fixed finite normalizer cap, one final
positive excess-readout contraction suffices to restore that same cap
without increasing PRODUCT count. Pure monomial paths alone can fail to
describe the constrained closure.

These statements concern the complete static function class below. They
provide no registered coefficient acquisition, optimizer path, physical
construction budget or reference/AMP bridge.

## 1. Class and the positive mass map

Fix a finite complete context domain and finite nonnegative source tables.
Use scalar nonnegative SUM/binary PRODUCT DAGs with arbitrary sharing,
at most P PRODUCTs, fixed base one in each of k output labels, and one final
normalization. There is no recurrence or acquired additional source.
Coefficient values and finite SUM work are unrestricted unless stated.

Flatten only SUM paths into the sources and all earlier PRODUCT features.
For fixed P this gives one finite nonnegative coefficient orthant, covering
the whole static class including zero slots and unused nodes. The masses
are positive polynomials in its coefficients z:

`M_(x,j)(z)=1+sum_alpha c_(x,j,alpha)*z^alpha`, c>=0.

Source partitions can remove a term only when it vanishes on the entire
declared domain. Shared ancestors and squares retain their multiplicities.
The full-mass theorem in `PRODUCT_SUPPORT_CLOSURE.md` states that every
finite limit of any positive polynomial map has a path

`z_i(epsilon)=a_i*epsilon^w_i`, a_i>0, w_i integer,

that reproduces that exact limit. Negative w_i permit hidden coefficients
to diverge. The theorem applies on the full nonnegative orthant; additional
resource constraints need a separate argument.

## 2. Unrestricted conditional closure has a complete monomial-path lift

Let q_n=M(z_n)/T(z_n) tend to Q, where T_x=sum_j M_(x,j). Introduce auxiliary
positive coordinates r_(n,x)=1/T_x(z_n), solely for this proof. The vector

`F_(x,j)(z,r)=r_x*M_(x,j)(z)`

is a positive polynomial map and tends to Q along the given sequence.
The full-mass theorem supplies a monomial path in (z,r) with F tending to Q.
Because every row of Q sums to one, along this path

`M_(x,j)(z)/sum_l M_(x,l)(z) = F_(x,j)(z,r)/sum_l F_(x,l)(z,r) -> Q_(x,j)`.

Discarding the proof coordinates r leaves the required monomial path in
the **original** native coefficients. No reciprocal or internal normalization
has been inserted into the model. Conversely any such path consists of
finite legal programs and therefore supplies a conditional closure point.

Explicitly, include the base monomial of exponent zero in every head and set

`mu_x=min_(j,alpha visible at x,j) alpha.w`,
`L_(x,j)=sum_(alpha.w=mu_x) c_(x,j,alpha)*a^alpha`.

Then mu_x<=0, every row has positive L_x=sum_j L_(x,j), and

`Q_(x,j)=L_(x,j)/L_x`.

This is a complete characterization, including limits with zero predicted
probabilities and different diverging normalizers at different contexts.
All tied leading contributions are retained. A zero probability at x
requires mu_x<0 because every label's base is visible at exponent zero.

Let D_x be the total coefficient of terms strictly above mu_x after the
row is rescaled by epsilon^(-mu_x). Integer exponent gaps are at least one.
For 0<epsilon<=1, the exact prediction error is bounded by

`max_j |q_(x,j)(epsilon)-Q_(x,j)| <= epsilon*D_x/L_x`.

There is no numerical cancellation in this bound: the rescaled masses are
L_(x,j) plus nonnegative tails, whose row sum is at most epsilon*D_x.

## 3. What is finite linear, and what remains an algebraic value problem

For conditional **support** existence, choose a leading term for every
desired positive head in every row. Introduce one row order mu_x and require

```
alpha.w >= mu_x       for every visible term, including every base;
alpha.w >= mu_x+1     for every term in a desired zero head;
alpha.w  = mu_x       for each selected positive-head term.
```

There are finitely many branches and each is a rational linear feasibility
problem. A feasible rational solution can be rescaled to integer exponents;
unit leading amplitudes already construct some limit with that support.
This is complete for support existence, not for prescribed probabilities.

For full prescribed Q, the selected leading sets must additionally satisfy
the positive-amplitude equations

`sum_(alpha.w=mu_x) c_(x,j,alpha)*a^alpha
 = Q_(x,j)*sum_(l,alpha.w=mu_x) c_(x,l,alpha)*a^alpha`, a_i>0.

These are a finite family of real algebraic feasibility problems after
leading-pattern enumeration. Constants a_i need not be rational. An
exponent witness with incorrect leading amplitudes is a false value
certificate even if it has the correct support. The audit implements exact
verification of rational paths, not a complete generic amplitude solver or
a generic rejection search over every phase.

## 4. Complete closure at the same finite normalizer cap

Impose T_x<=R on every finite candidate. If R<k the class is empty. If R=k,
the only prediction is uniform, with all excesses zero. Assume R>k.

Any convergent prediction sequence has a subsequence whose complete masses
converge, because 1<=M_(x,j)<=R. Call that limit M*, with T*<=R and
Q=M*/T*. Apply the mass-path theorem to obtain a monomial coefficient path
whose masses tend to M*. Every visible monomial on this path has nonnegative
exponent, so

`M_(x,j)(epsilon)=M*_(x,j)+r_(x,j)(epsilon)`, r>=0.

Let D be the maximum, across contexts, of the sum of positive-exponent
coefficients in the total excess polynomial. Then sum_j r_(x,j)<=D*epsilon
for 0<epsilon<=1. Define

`beta(epsilon)=(R-k)/(R-k+D*epsilon)`,
`M'_(x,j)=1+beta(epsilon)*(M_(x,j)(epsilon)-1)`.

Since the total excess is at most R-k+D*epsilon,

`sum_j M'_(x,j) <= k+beta*(R-k+D*epsilon)=R`.

Also beta tends to one, so M' tends to M* and q' tends to Q. The contraction
is an ordinary positive SUM coefficient on each final excess readout. It
adds no PRODUCT. Attach those readouts after the original graph; do not
modify a shared feature or an intermediate readout used by a descendant.

Writing a=R-k, each head difference is

`M'_j-M*_j = beta*r_j-(1-beta)*(M*_j-1)`.

Both nonnegative terms are at most beta*D*epsilon, because M*_j-1<=a.
The same reasoning bounds the total-mass difference. Consequently

`||M'-M*||_max <= D*epsilon`,
`||q'-Q||_max <= 2*D*epsilon/k`.

Every finite q'_j>=1/R. The chi-square upper bound then gives uniform CE
excess at most `4*R*D^2*epsilon^2/k`. These constants are conservative.
If D=0, the path is already exact and beta=1.

Thus Q is in this finite-cap closure **iff** some monomial mass path has a
finite mass limit M* with sum_j M*_j<=R and Q=M*/T*. The displayed final
contraction turns every such formal lift into actual finite candidates at
the same cap. No extra normalizer slack is assumed. For prescribed Q this
still requires the amplitude/scale feasibility equations; support alone
does not decide them.

## 5. A pure monomial path can be excluded while constrained closure exists

Take the three-bit, eight-label identity-noise task at cap nine. Exact
prediction forces every normalizer to nine and every excess to its singleton
indicator. The proved exact PRODUCT minimum is twelve, while nine PRODUCTs
approach it at that same cap; see `DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`.

Suppose a pure monomial coefficient path with at most eleven PRODUCTs stayed
at cap nine and approached this target. Bounded masses force all visible
term exponents nonnegative. Each mass is its limit plus a nonnegative sum
of positive-exponent terms. Every limiting row total is already nine.
The cap therefore forces every tail in every row to vanish identically.
The path would realize the exact target at every finite epsilon, contradicting
the twelve-PRODUCT lower bound. Thus no such pure path exists.

The missing correction is visible in the nine-PRODUCT subset basis

`B_S(T)=epsilon^(|T|-|S|)` for S contained in T, zero otherwise.

Its total excess is (1+epsilon)^|T|, so it tends to the identity excess but
exceeds the cap on every nonempty T. Here D=7, and the final scale
`beta=1/(1+7*epsilon)` keeps every finite normalizer at most nine and retains
the correct limit. The earlier dyadic scale (1-epsilon)^3 is another legal
correction. Excluding the uncorrected monomial paths would be a false
completeness claim about the constrained closure.

## 6. Hidden activation growth can be removed when SUM scaling is free

There is also a complete static rescaling statement. Let A>0 bound every
source and every final excess output of a given finite graph on the complete
domain. Then an equivalent graph has the same PRODUCT count and **every**
source/SUM/PRODUCT activation at most A, including the final excess heads.
No original bound on hidden activations is needed.

Put b=min(1,A). Represent each original node v by a normalized node
u_v=v/gamma_v with a finite gamma_v>0. For sources and SUM outputs, choose
gamma_v=max(1,max_x v(x)/b). A source gets an ordinary scaling SUM. A SUM
v=sum_p c_p*p becomes the SUM with weights c_p*gamma_p/gamma_v on u_p.
For a PRODUCT v=l*r, choose gamma_v=gamma_l*gamma_r and use u_v=u_l*u_r.
Inductively all normalized nodes are at most b: a PRODUCT is at most
b^2<=b, and the other cases follow from their chosen scales. Original
sources remain present and bounded by A. Finally append a SUM with weight
gamma_h on each output u_h; its value is the original excess, bounded by A.
Shared ancestors and readouts reused by descendants are left intact.

This construction is finite and exact over the given real coefficients.
Its SUM weights can be very large or very small. In particular, at final
normalizer cap R>k, every excess is at most R-k. Whenever
`A>=max(maximum_source_value,R-k)` and A>0, imposing the hidden-activation
cap A changes neither the exact nor the approximate prediction class at
fixed PRODUCT budget and unrestricted finite SUM/scaling work.

This does not provide the unknown node maxima for free under an information
contract, preserve a registered parameter trajectory, control minimum
nonzero magnitudes, or establish a floating-point error bound. It identifies
which static resource distinction disappears when those costs are omitted.

## 7. A finite local coefficient alphabet has the same closure when SUM work is free

There is a separate monotonicity argument that does not rely on solving
the amplitude equations. In any fixed finite native graph, replace every
coefficient c by a dyadic approximation from below,

`c_n=floor(2^n*c)/2^n`.

All node values are nondecreasing functions of nonnegative coefficients.
Thus the rounded graph converges pointwise to the original graph, every
node value is no larger, and every original upper bound on total normalizer
or a common maximum activation is retained. The positive base makes
predictions continuous.

Each dyadic coefficient can be implemented with SUM weights {1/2,1,2} by
halving the parent first and then using binary Horner additions/doublings.
No PRODUCT is added. Each new intermediate value is at most the larger of
the parent and its weighted contribution. The latter is at most the original
nonnegative SUM output. Hence a common peak-activation upper bound is also
preserved by the expanded graph, not just by the rounded original nodes.

It follows that arbitrary-real-coefficient and local-{1/2,1,2} classes have
the **same prediction closure at fixed PRODUCT budget**, including at the
same finite normalizer cap and common activation cap, when arbitrary finite
SUM construction work is allowed. This is not equality of exact realization
classes or of classes with a fixed SUM/node/bit budget. The decoder's proved
SUM lower bounds already show why that resource qualifier is necessary.
Nor does an existential rounding sequence give legal access to unknown
coefficient values, or an AMP execution guarantee.

Combining this density with section 6, at
`A>=max(maximum_source_value,R-k)>0` the complete arbitrary-real class at
normalizer cap R has the same closure as the class with that cap, activation
cap A and local alphabet {1/2,1,2}. The cost can move into SUM construction,
encoding length and small intermediate values. Bounding only the maximum
activation and local alphabet therefore does not restore closure.

## 8. A constant support pattern does not make a variable bank nonuniversal

The frozen shifted two-bit bank H_t=(t+x)*(t+y), t>0, fails binary universality
for every t, and has the same support pattern for every such t. Nevertheless
their union is exactly universal for every fixed finite number of labels.

For any given positive table, apply the strict positive monomial-coefficient
construction from `FROZEN_FEATURE_UNIVERSALITY.md`. Replacing xy by H_t
subtracts t*b_xy from the two linear coefficients and t^2*b_xy from the
constant coefficient. Some finite positive t keeps every head coefficient
positive and preserves the exact target. The same t can serve any finite
collection of positive tables, including multiple finite label alphabets.

Thus `for every frozen t, some target fails` cannot be exchanged with
`some target fails for every t`. The frozen coloring is valid throughout,
but its ratio-dependent margin can tend to zero. Neither the support
pattern alone nor a certificate at one numerical bank excludes the full
variable-value class.

## 9. Audit and open decision work

The audit evaluates leading exponents/amplitudes independently of complete
Laurent expansion and actual rational native execution, retains tied heads
and context-dependent normalizers, checks the finite-cap contraction,
rescales arbitrary hidden nodes, reconstructs dyadic SUM graphs with peak
bounds, and rejects false cap, support and amplitude claims. It checks 625
small exponent configurations, 64 shared/nested/squared rational paths and
their cap corrections, 38 exact activation rescalings, 144 expanded dyadic
graphs, and one common shifted bank fitting 30 targets across 2/3/5 labels.
Complete generic phase/amplitude search,
sharp complete-resource costs and registered information/value/physical
paths remain open. All closure claims are for the declared static grammar.

Audit: `theory/numerical_checks/conditional_coefficient_paths_audit.py`.
Minimal evidence: `evidence/minimal/FP_CONDITIONAL_COEFFICIENT_PATHS_AUDIT.json`.

`SUM_ACCURACY_COMPLEXITY.md` quantifies this density: fixed-P finite-cap
closure points have O(log(1/error)) local SUM constructions, with a matching
lower order for nonexact local realization on fixed algebraic data.
