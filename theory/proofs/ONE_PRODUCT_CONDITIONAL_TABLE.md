# One PRODUCT is universal for a positive 2x2 conditional table

Status: **PROVED**, 2026-09-06. This extends the static normalization result in
`NORMALIZED_SUM_XOR.md`; `FP_THEORY.md` XVII.1 remains the normative summary.

For exact fixed-mass sharing and sharp range obstructions, see the later
`ONE_PRODUCT_SHARED_SLACK.md`. Unbounded conditional universality does not
assert a one-PRODUCT realization at an arbitrary fixed normalization scale.

## Contract and statement

Inputs are two binary variables with their declared unary partition indicators.
There are `k>=2` output labels, fixed strictly positive base `b_y=1`, positive
SUM, and one final native normalization. Coefficients are fixed finite
nonnegative numbers. An output-appropriate PRODUCT type rule is declared.
There is no input-dependent base, internal normalization, or recurrence.

**Theorem.** Every strictly positive table

\[
p_{ij}\in\operatorname{int}\Delta_k,\quad i,j\in\{0,1\},
\]

has a finite native realization with **at most one semantic PRODUCT**, shared
across output heads. At most `k-1` heads need a nonzero edge from the PRODUCT.
For rational target probabilities, every coefficient in the construction is
rational. The result is about semantic PRODUCT count, not total physical cost.

## Constructive proof

All inequalities below are coordinatewise. Choose finite scales and masses

\[
C_{00}=\max_y\frac1{p_{00,y}},\quad A=C_{00}p_{00}\ge\mathbf1,
\]
\[
C_{01}=\max_y\frac{A_y}{p_{01,y}},\quad B=C_{01}p_{01}\ge A,
\]
\[
C_{10}=\max_y\frac{A_y}{p_{10,y}},\quad C=C_{10}p_{10}\ge A.
\]

Set `D=B+C-A>0`, then

\[
C_{11}=\max_y\frac{D_y}{p_{11,y}},\qquad
E=C_{11}p_{11}-D\ge0.
\]

At least one coordinate of `E` is zero because a maximizing ratio is attained.
Let `x,z` be the declared one-indicator sources. Define

\[
\boxed{M(x,z)=A+(C-A)x+(B-A)z+E\,xz.}
\]

All coefficients are nonnegative; all four masses are at least the positive
base. The constant evidence `A-1` is implemented by SUM over either declared
binary partition, not an additional primitive source. The only semantic
PRODUCT is `xz`. At the four contexts the mass vectors are
`C_00 p_00`, `C_01 p_01`, `C_10 p_10`, `C_11 p_11`, so normalization returns
the target table exactly. This proves the theorem, including rationality.

For binary noisy XOR, these same max-ratio steps yield the previous explicit
formula `M_0=r+2r(r^2-1)xz`, `M_1=1+(r^2-1)(x+z)`. Thus the one-PRODUCT XOR
witness is a specialization of a general positive construction, not a
hand-written parity-only architecture.

## Exact minimal PRODUCT count

The zero-PRODUCT criterion also extends to vector-valued output distributions:

\[
\operatorname{ri}\operatorname{conv}\{p_{00},p_{11}\}
\cap
\operatorname{ri}\operatorname{conv}\{p_{01},p_{10}\}\ne\varnothing.
\]

Necessity follows from the same two additive mass identities, now for every
output coordinate with common strictly positive denominator weights.
Sufficiency constructs denominator weights at the segment intersection,
rescales above the base, and decomposes each additive mass into positive SUM.
The proof is identical in vector form and does not introduce independent
per-label denominator choices.

Therefore for the stated unrestricted finite-coefficient static class:

\[
\boxed{\min\#PRODUCT=\begin{cases}
0&\text{if those relative interiors intersect},\\
1&\text{otherwise}.
\end{cases}}
\]

This counts semantic PRODUCT operations; multiplying by a fixed SUM coefficient
is not an extra semantic PRODUCT. A backend may fuse `xz` away or use additional
hardware multiplies without changing this count. No claim is made that one
PRODUCT minimizes SUM nodes, coefficient precision, peak memory, training work,
or build/install cost. More PRODUCTs with smaller masses can still be physically
preferable. The vector-segment criterion must not be replaced by separate
coordinatewise interval tests.

## Boundary versus robust forcing

For binary outputs, a strict relative-interior failure may occur even though
the closed intervals touch. Then no finite zero-PRODUCT realization is exact,
but zero-PRODUCT graphs approximate the target arbitrarily closely. Example:

\[
(p_{00},p_{01},p_{10},p_{11})=(1/2,1/2,3/4,1/4).
\]

Here `min #PRODUCT=1` for exact realization, but the SUM log-loss infimum is
Bayes risk. An engineering tie-break or a finite numerical equality test cannot
turn this exact count into positive-margin epsilon-optimal PRODUCT forcing.
For binary targets with **disjoint** closed intervals, the strictly positive
weighted entropy gap in `NORMALIZED_SUM_XOR.md` supplies that robustness.

For multiple output labels, vector segments can be disjoint even if every
coordinate's scalar intervals overlap. The binary four-pooling likelihood
formula is not asserted for this higher-dimensional geometry.

## Information, construction, and resources

The input to this algebraic construction is an identified conditional table.
The theorem does not grant its acquisition through an illegal query, free noisy
probability oracle, or validation data. Likewise, displaying these rational
coefficients does not make them reachable under an arbitrary fixed optimizer.
To use the witness in FP's truth objective, a registered profile/value operation
must construct it and pay its work/precision/state cost; the machine must build
and install it within the declared resources. Any missing premise remains
`UNRESOLVED`. This is a derived proposal and a semantic expressivity theorem,
not a complete Reference Compiler implementation.

Exact audit: `theory/numerical_checks/one_product_table_audit.py`. It constructs
all 256 positive binary tables on the four-point rational grid and randomized
positive rational tables with 2--8 output labels, verifies each returned mass
against the target, and checks a multiclass coordinatewise-overlap counterexample.
