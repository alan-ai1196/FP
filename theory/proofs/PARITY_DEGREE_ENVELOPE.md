# The exact sub-parity-degree loss envelope

Status: **PROVED**, 2026-09-06. This is a static expressivity/loss theorem for
all dimensions. The distinct unary-SUM envelope was subsequently proved in
`UNARY_SUM_PARITY_ENVELOPE.md` on 2026-09-08.

## 1. The declared family and result

Let d>=2, N=2^d, and X be uniform on the binary cube. The binary target is
`P(Y=1|x)=eta` at even parity and `1-eta` at odd parity, with `0<=eta<1/2`.
Sources are unary binary indicators, the readout base is `(1,1)`, and programs
use positive SUM/PRODUCT with fixed finite coefficients and one final positive
normalization. There is no internal normalization, recurrence or enriched source.

Consider the entire family whose two output mass functions, after multilinear
reduction on the cube, have total degree at most d-1. It includes arbitrary
positive sums of all cylinder indicators fixing at most d-1 coordinates. It
does not restrict graph size or pretend that degree counts physical PRODUCTs.

Reduced mass degree is also distinct from the support of positive derivations.
Full-context indicator terms can cancel their highest signed coefficient after
algebraic reduction while retaining full positive provenance. The strict range
separation in `PARITY_PROVENANCE_RANGE.md` proves why these two classes cannot
be identified. The present lower bound covers the larger reduced-degree class.

The exact cross-entropy infimum of this family is

\[
\boxed{L_{<d}^*=H(\eta)+2^{1-d}[\log2-H(\eta)].}
\]

Every finite member has strictly larger loss. A finite native positive program
approaches the bound, with an explicit approximation/range tradeoff below.
At eta=1/2 the base attains log2 and the strict-unattainment statement does not
apply. For d=1 the degree-zero family is constant and attains log2.

For d=2 this recovers the sharp unary-SUM XOR envelope. For d>=3 it is a
**stronger comparison class** than unary SUM: the latter's now-proved infimum
is `log2-2^(1-d)[log2-H(eta)]`. The two formulas agree
only at d=2 (or no signal). Never exchange them in a certificate.

## 2. The all-class lower bound comes from a retained Fourier moment

Write `chi(x)=(-1)^sum x_i`. Every monomial of degree less than d omits some
coordinate, so summing against chi cancels in that coordinate. Consequently

\[
\sum_{x\text{ even}} M_y(x)=\sum_{x\text{ odd}} M_y(x),\quad y=0,1.
\]

This is an extensional consequence used for a lower bound, not a quotient of
physical realizations, source provenance or learner state. With `T=M_0+M_1>0`
and prediction `q=M_1/T`, the T-weighted means of q in the two parity classes
are equal. Therefore some even vertex u and odd vertex v satisfy `q_u>=q_v`.

The two targets at that pair are eta and 1-eta. Convex Bernoulli cross-entropy
under the reversed ordering `q_u>=q_v` has its unique minimum at
`q_u=q_v=1/2`, with total loss `2 log2`. Every other vertex costs at least
`H(eta)`. Dividing by N proves the displayed bound for the whole degree class.

Equality would require exactly that pair to be uniform and every other vertex
to match its target. Because d>=2, each parity side has another vertex with
positive T. Its even weighted mean is then strictly below 1/2, while its odd
weighted mean is strictly above 1/2: contradiction. Thus finite attainment is
impossible, including deterministic eta=0, where the positive base already
precludes exact zero/one predictions.

There is also a direct exact-expressivity consequence. If `q` exactly equals
the noisy parity target with eta<1/2, then

\[
M_1-M_0=-(1-2\eta)\chi T,\qquad
\sum_x\chi(M_1-M_0)=-(1-2\eta)\sum_x T\ne0.
\]

At least one mass therefore has full multilinear degree d. Positive
normalization cannot erase this required highest-order moment.

## 3. A native finite hierarchy attains the infimum in the limit

Each cube edge e has an indicator `a_e` fixing its other d-1 coordinates, a
legal PRODUCT of d-1 unary sources. Choose the edge joining `00...0` and
`10...0` as the root edge. For every other vertex x, choose its parent by
flipping the first nonzero coordinate among positions 2,...,d to zero. Its
depth ell is the number of ones in those positions. These edges and the root
edge form a spanning tree with N-1 edges and maximum depth d-1.

Let `q_e=1/2` on the root edge. On every parent/child edge set `q_e` to the
child's target probability. For a finite K>1, use root weight K^d and weight
`K^(d-ell)` on an edge whose child has depth ell. Construct the two masses

\[
M_0(x)=1+\sum_e w_e(1-q_e)a_e(x),\qquad
M_1(x)=1+\sum_e w_e q_e a_e(x).
\]

All coefficients are nonnegative. Each mass has degree at most d-1. At a
non-root vertex the parent edge dominates its children, so its prediction
converges to its own target. The two root vertices are dominated by the root
edge and converge to 1/2. Hence exactly N-2 contexts approach Bayes and the
remaining two give the necessary pooling loss.

More explicitly, let q* be that limiting table. Every vertex has at most d-1
children, every child edge is at most 1/K times its dominant edge, and the
dominant weight is at least K. The constant base contributes total 2. Thus

\[
\boxed{\|q^{(K)}-q^*\|_\infty\le(d+1)/K.}
\]

For eta>0 and `(d+1)/K<=eta/2`, the derivative of cross-entropy on the intervening
probability interval has absolute value at most `2/eta`, yielding
`0<L_K-L_<d^*<=2(d+1)/(eta K)`. For eta=0 and `(d+1)/K<=1/4`, the deterministic
loss derivative gives `0<L_K-L_<d^*<=4(d+1)/K`. These are finite approximation
bounds, not only formal zero-normalizer limits.

The graph has N-1 edge atoms, coefficients grow as K^d, and the peak final
normalizer is at most `2+K^d+(d-1)K^(d-1)`. The coefficient and resource costs
are substantive. This construction is an algebraic witness, not an initializer,
registered value trajectory, physical minimum, persistence or AMP certificate.

## 4. Consequences and limits for native interaction complexity

If every source has degree at most one, a node with at most h PRODUCTs on any
source-to-node path has degree at most 2^h, by induction through SUM and PRODUCT.
Therefore an exact noisy-parity realization needs PRODUCT depth at least
`ceil(log2 d)`, and consequently at least that many semantic PRODUCT nodes.
This is only a lower bound, not a claim of sharp PRODUCT count. Repeated
squaring and shared parents are allowed; assuming degree <= count+1 would be
wrong for a DAG. A graph may have many PRODUCTs yet remain below degree d.

The proved sub-degree risk margin above Bayes is exponentially small,
`2^(1-d)[log2-H(eta)]`. Thus exact interaction necessity alone does not imply
a dimension-independent robust loss separation. Conversely this small margin
cannot be used to dismiss unary SUM: that smaller family's complementary
exact multi-input envelope is proved in `UNARY_SUM_PARITY_ENVELOPE.md`.

Proof audit: `theory/numerical_checks/parity_degree_audit.py`. Numerical or
finite enumeration checks audit the algebra; the universal lower bound and
constructive convergence are supplied by the proof above.
