# Exact conditional universality of a frozen positive feature bank

Status: **PROVED; EXACT SUPPORT, GRAPH, PRIMAL AND SEPARATION AUDIT**,
2026-09-11. A finite frozen nonnegative feature bank has a complete
conditional-universality criterion based only on its zero supports. A
partial coloring supplies a robust rejection certificate; exhaustive
absence of such a coloring proves exact universality at unrestricted range.

As a consequence, frozen unary-source banks on d bits need **exactly
2^d-d-1 PRODUCTs** for binary universality, and for every fixed k>=2. This
sharpens the earlier parameter-count lower bound without changing the
adaptive-feature capacity theorem.

## 1. Class and exact support criterion

Let X be a finite set of N complete contexts and let G contain known finite
nonnegative feature columns g_f. The constant one belongs to their positive
cone; include it as a redundant column if desired. Fix k>=2 labels. The
complete readout class is

`M_j=1+G*a_j`, `a_j>=0`, `q_j=M_j/sum_l M_l`.

There is one final normalization. Coefficients and finite SUM work are
unrestricted, and the numerical feature table is frozen. No controller,
new source, value trajectory or runtime equivalence is supplied by this
extensional class. Universality means every strictly positive N-by-k
conditional table, not only one sampled collection of targets.

An **obstructing partial coloring** is a map c:I->{1,...,k} for a nonempty
subset I of contexts such that, for every feature f,

`support(g_f) intersect I`

is either empty or contains at least two colors. Every colored context is
covered because the constant is available. In particular at least two
colors occur. Uncolored contexts remain in the model; they have zero weight
in this particular rejection argument.

The following three statements are equivalent:

1. the bank realizes every strictly positive k-label table exactly;
2. its prediction closure contains every such table;
3. no obstructing partial coloring exists.

Thus universal exact and approximate capabilities of a *fixed* bank coincide,
although an individual target can still distinguish exact realization from
closure. Numerical feature values affect scales, margins and readout work,
but the all-target universality decision depends only on exact supports.

## 2. A coloring gives a positive, cap-independent loss gap

For a coloring let I_j be the contexts of color j and set

`K=max_(f,j: sum_(I_j) g_f>0) [sum_(I_j) g_f / sum_(I without I_j) g_f]`.

Every denominator used here is positive by the coloring property. K is
finite and positive. Every mass column is in the positive feature cone,
including its base, so

`sum_(x in I_j) M_j(x) <= K*sum_(x in I without I_j) M_j(x)`.

Summing over labels says total correctly assigned mass on I is at most K
times total incorrectly assigned mass. Hence every readout has at least
one colored context with

`q_(c(x))(x) <= K/(K+1)`.

Set epsilon=1/[2(K+1)]. Give each colored context target probability
1-epsilon on its color and epsilon/(k-1) on each other label; give uncolored
contexts the uniform target. This is a strictly positive table with

`probability sup gap >= epsilon`,
`uniform excess CE >= 2*epsilon^2/N`.

The CE bound follows by coarsening to the correct label and Pinsker. No
normalizer or hidden coefficient is bounded in the argument. The inequality
passes to all prediction limits. A rational bank gives a rational K and
target certificate. The constants need not be sharp.

There is also an explicit exact Farkas certificate for this same target:
at a colored row use y_(c(x))=-1 and y_j=2K+1 for every other label;
use zero at uncolored rows. Each G^T*y_j is nonnegative, each target-weighted
row sum is zero, and the total sum of y is positive. This independently
checks infeasibility of the exact mass/readout equations in section 3.

## 3. Absence of a coloring proves exact universality

Fix any strictly positive target p and consider the finite linear system

`G*a_j-p_j*T=-1` for every label j, with a_j>=0 and T free.

Any solution automatically has T_x>0 because each mass is at least one.
If this system were infeasible, linear Farkas separation would provide
vectors y_j with

`G^T*y_j>=0`, `sum_j p_j(x)*y_j(x)=0` for every x,
and `sum_(x,j) y_j(x)>0`.

At every row where some y_j(x) is nonzero, strict positivity of p forces
both positive and negative entries across the labels. Let I be those rows
and choose a color c(x) with y_(c(x))(x)<0. If a feature met I in only one
color j, its inner product with y_j would be strictly negative: every
active contribution is negative and all rows outside I are zero. This
contradicts G^T*y_j>=0. Therefore the dual produces an obstructing partial
coloring, contrary to the premise.

So the system is feasible for every positive p, with finite nonnegative
coefficients. For rational G,p, a nonempty rational polyhedron has a rational
feasible point. Scaling all resulting masses by a common integer D clears
its coefficient denominators and preserves p:

`D*M_j = 1 + (D-1)*1 + G*(D*a_j)`.

This provides integer readout weights after the scale change. It does not
make irrational frozen feature values finitely encoded or make the larger
range and SUM/bit work free. Numerical LP proposals must be checked against
the exact equations; numerical failure does not disprove feasibility.

## 4. A common linear annihilator is a stronger, simpler special case

Let W be the span of all frozen features and the base. If W is proper,
choose a nonzero w orthogonal to W. Since 1 belongs to W, w has positive
and negative entries. For every nonnegative feature, exact cancellation
implies it meets the positive support of w iff it meets its negative
support. These two supports give a binary obstruction. Equivalently,
their unions of active feature indices are identical.

There is a margin independent of feature ratios. Every M_j and T is
annihilated by w. The |w_x|*T_x-weighted means of any binary prediction over
the positive and negative supports coincide. Assign target probability
1-eta to the positive side and eta to the negative side, 0<eta<1/2; choose
eta also at zero entries of w. Some prediction pair has the reversed order,
which gives

`probability sup error >= 1/2-eta`,
`uniform excess CE >= 2*[log(2)-H(eta)]/N`.

At eta=1/4 these imply the exact rational lower bounds 1/4 in probability
and 1/(4N) in CE. The latter uses the two-context squared-error bound, not
only the single worst context. The hard target uses only the two rational
probabilities 1/4 and 3/4. Consequently even universality over this finite
family of noisy Boolean tasks forces a complete frozen span.

This generalizes the parity-moment obstruction; parity is one possible
annihilator. It is stronger than counting the parameters of normalized
readouts because it retains positivity of every normalizer.

On d binary inputs the unary span has dimension d+1. P frozen PRODUCT
features can add at most P dimensions. Thus every binary-universal frozen
bank needs P>=N-d-1. The fixed monomial bank already attains this count for
every finite alphabet by positive row scaling. The same lower bound holds
for k>2: a binary partial coloring is still a permitted k-color coloring.
Hence **the exact frozen-bank universal minimum is N-d-1 for every k>=2**,
both exactly and in approximation, at unrestricted range.

This quantifier is essential: `for every proper frozen W, some target fails`.
The bad target may depend on W. It does not give one target excluding all
variable-feature P-budget programs. The adaptive fixed-label upper and lower
order Theta(min(N,sqrt(N*k))) remains valid. For binary tables, adaptive
upper versus exact frozen minimum is 3 versus 4 at d=3, 44 versus 247 at
d=8, and 3560 versus 1048555 at d=20. Some feature values must adapt at the
smaller budgets, while the construction's skeleton can stay fixed.

## 5. Full span is not sufficient: positivity and support still matter

On two binary inputs, compare one-PRODUCT features

`H_0=x_1*y_1`, `H_t=(t+x_1)*(t+y_1)`, t>0,

with all original unary readouts. Both banks span all four context tables,
because H_t=H_0+t*x_1+t*y_1+t^2. H_0 is conditionally universal for every
alphabet by the earlier monomial construction. H_t is not even binary
universal: color 00,11 alike and 01,10 the other color. Every unary feature
crosses the colors, and H_t is positive at all four contexts. This is an
obstructing full coloring.

At t=1 the largest correct/wrong feature-mass ratio is K=5/4. Therefore
some parity-correct probability is at most 5/9, at any range. The noise-1/4
XOR target has probability error at least 7/36 and uniform CE gap at least
49/2592. The unshifted one-PRODUCT bank realizes it exactly at finite range.
A linear-span-preserving positive feature shift can thus destroy conditional
universality. Signed changes of feature coordinates are not free readouts.

## 6. The number of labels and the partial domain are indispensable

On two bits, freeze the two PRODUCTs

`A=(x_1+y_1)*(x_0+y_0)`, `B=(x_0+y_1)*(x_1+y_0)`.

With all unary sources these supply the indicator of every pair of the four
contexts: the four unary pairs and the two diagonals. No proper nonempty
colored subset can obstruct, because a pair joining a colored context to
an uncolored one intersects it in a singleton. On the full domain a coloring
avoids monochromatic pairs only when all four contexts have distinct colors.
This bank is therefore universal for k=2 and k=3, and fails for every k>=4.
It has full span throughout. With four labels, K=1 for the distinct-color
obstruction. The target assigning 3/4 to its context label and 1/12 elsewhere
has probability gap at least 1/4 and uniform CE gap at least 1/32 for this
entire frozen two-PRODUCT bank. A different, single-PRODUCT bank realizes it.

Checking only full-domain colorings is unsound. On three contexts the
features 1 and (1,0,0) admit no obstructing full coloring, because the second
feature would be monochromatic. The subset {2,3}, colored differently,
is an obstruction. These two contexts cannot be discarded merely because
another feature isolates the first context.

## 7. Arbitrary finite positive validation cannot replace the criterion

Let any finite collection of strictly positive two-bit binary targets be
given. There is some rational t>0 such that the nonuniversal bank H_t in
section 5 realizes every member exactly.

For each target choose the earlier row scales C,L with strict margins:
take C at least twice the previous minimum and L=2d*(1+Gamma). Then all four
multilinear excess coefficients b_0,b_x,b_y,b_xy in each head are positive.
Replacing H_0 by H_t changes the other coefficients to

`b'_0=b_0-t^2*b_xy`, `b'_x=b_x-t*b_xy`, `b'_y=b_y-t*b_xy`.

For sufficiently small rational t all remain positive, simultaneously for
the finite target collection. The exact masses and normalizers are unchanged.
Yet every t>0 has the obstructing XOR support pattern and fails global
binary universality at sufficiently high confidence.

Thus exact success on any finite collection of interior target tables is
not a complete universality certificate. Exact zero-support information
separates t=0 from every positive t. This is not a reason to erase a small
positive tail or to treat a floating-point zero as an exact semantic zero.

The follow-up `CONDITIONAL_COEFFICIENT_PATHS.md` extends this construction
to any finite collection of positive targets with arbitrary finite label
counts. In particular, the union over t>0 is exactly universal despite its
unchanging feature-support pattern and the failure of every frozen bank.

## 8. Decision and audit scope

For a declared finite bank and k, enumerate partial colorings with an
explicit integer budget counting tested colorings. This is a solver work
unit, not complete physical resource accounting. A checked coloring proves nonuniversality with the
margin above. Exhausting every coloring with no obstruction proves exact
universality for this unrestricted-range frozen readout class. An exhausted
work budget gives UNRESOLVED. Source support is compared exactly; no
tolerance or sampled target list substitutes for the finite criterion.

The audit verifies rational graph tables, checked partial-coloring witnesses,
independent raw-color enumeration, exact LP primal reconstructions for
universal examples, arbitrary-DAG annihilators and normalizers, full-span
counterexamples, and the finite-validation construction. No certificate
here authorizes target acquisition, frozen-feature selection, value training,
resource disposal, installation, persistence or a reference/AMP bridge.
