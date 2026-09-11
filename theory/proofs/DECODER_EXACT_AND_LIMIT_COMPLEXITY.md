# All singleton outputs: exact three-bit count twelve, approximation count nine

Status: **PROVED CONSTRUCTION AND LOWER BOUNDS; EXACT FINITE ENUMERATION**,
2026-09-11. For d>=2 binary inputs and N=2^d singleton outputs, the shared
approximation PRODUCT minimum is exactly N+d-2. This remains true for the
identity-noise conditional task at its minimum normalizer cap N+1. At d=3
the exact support, mass and minimum-cap conditional PRODUCT minima are
twelve, whereas the approximation minimum is nine.

## 1. Decision classes

Use the complete d-bit cube with its 2d fixed scalar unary indicators,
arbitrary finite positive SUM/binary PRODUCT DAGs, arbitrary sharing and
finite nonnegative real coefficients. There is no recurrence or internal
normalization. PRODUCT count counts scalar graph nodes once. SUM work and
coefficient encoding are unrestricted unless explicitly bounded below.

The excess targets are all N singleton tables `E_S(T)=1[S=T]`, where a
context is its subset T of one-valued coordinates. The conditional task has
base one for each label, uniform contexts, target

`p_S(T)=(1+1[S=T])/(N+1)`,

and one final normalization capped at R=N+1. Exact prediction forces T_mass=R:
each wrong-label mass is at least one and its target probability is 1/R.
Thus exact conditional realization at this cap is exactly the identity
excess table. Approximate normalizers cannot be fixed in advance.

## 2. A complete all-dimension approximation construction

Fix 0<epsilon<1 and put c=(1-epsilon)^d. First construct

`G_empty(x)=c product_(i=1,...,d) (x_(i,0)+epsilon*x_(i,1))`.

This uses d-1 PRODUCTs; c is a fixed positive scaling. For each nonempty
subset S, choose a fixed i in S and construct recursively

`G_S = epsilon^(-1) * G_(S\{i}) * x_(i,1)`.

Order subsets so the chosen parent precedes its child. Each adds one
PRODUCT. Read out G_S as excess for label S, including S empty. The total
PRODUCT count is

`(d-1)+(2^d-1)=N+d-2`.

The full-domain source partitions imply the exact table formula

```
G_S(T) = c*epsilon^(|T|-|S|)  if S is a subset of T,
         0                   otherwise.
```

In particular, each correct excess is c and every other positive excess is
at most c*epsilon. The sum over all heads at context T is

`sum_S G_S(T)=c*(1+epsilon)^|T| <= (1-epsilon^2)^d <= 1`.

Consequently every normalizer is at most N+1, and

`||G-I_N||_infinity=1-c<=d*epsilon`.

The equality follows because c<1 and `c*epsilon<=epsilon<=1-c`. Thus every
singleton output converges simultaneously, with one common shared graph
and all readout scales retained.

[`SOURCE_INTERSECTION_PRODUCT_BOUND.md`](SOURCE_INTERSECTION_PRODUCT_BOUND.md)
already excludes every P<=N+d-3 from the joint mass closure and from
conditional Bayes closure at this cap. The construction matches it. Hence

**the all-dimension shared approximation PRODUCT minimum is N+d-2**.

This is not an exact-count theorem: finite positive epsilon leaves positive
off-diagonal tails, which are essential to the subsequent PRODUCTs.

### Conditional convergence and a loss bound

At a context T the correct mass is 1+c. Put
s_T=c*(1+epsilon)^|T|. Then

`q_T(T)=(1+c)/(N+s_T)`, `q_S(T)=(1+G_S(T))/(N+s_T)`.

Every wrong q_S is at least 1/(N+1), so the correct probability is at most
its target 2/(N+1). The wrong-label probability excesses sum to the correct
probability deficit. Since N+s_T<=N+1,

`||q-p||_infinity <= (1-c)/(N+1) <= d*epsilon/(N+1)`.

All q_S>=1/(N+1). The sum of squared errors at one context is at most twice
the squared correct-label deficit. Using `KL(p||q)<=sum_S (p_S-q_S)^2/q_S`
therefore gives the uniform bound

`L(q)-L_Bayes <= 2*d^2*epsilon^2/(N+1)` nats.

The KL inequality follows directly from log u<=u-1. Neither a numerical
optimizer nor a zero-normalizer limit is needed.

## 3. Finite local alphabet and bounded features

For epsilon=2^-k, k>=1, the construction can use only local SUM coefficients
`{1/2,1,2}`, with every source and intermediate excess feature in [0,1].

Build each `x_(i,0)+epsilon*x_(i,1)` by k halvings of x_(i,1) and one SUM.
After their d-1 PRODUCTs, apply d stages of the positive geometric scaling

`(1-epsilon)h = sum_(j=1,...,k) 2^-j h`.

Each stage uses k halvings and one SUM. This gives the common factor c
without a negative coefficient. For every nonempty S, multiply the already
scaled G_parent by x_(i,1), then double k times. Its value before doubling
is at most c*epsilon: all surviving contexts have at least that one extra
one-valued coordinate. Every amplification intermediate is therefore <=c.

The complete excess graph has

`PRODUCT nodes = N+d-2`,

`weighted SUM nodes = 2d(k+1)+k(N-1)`.

No source, weight, dataset or large graph dump is needed as evidence: the
deterministic constructor and exact table formula reproduce the witness.
The growing SUM count is real construction cost. This does not claim
arbitrary accuracy at a fixed complete physical budget or in fixed floating
arithmetic. The theorem is about exact-real semantics of each finite graph.

## 4. Exact singleton nodes can be made terminal

For exact support, unlike closure, the full graph has a much smaller search
normal form. Start with any graph realizing all singleton outputs. Flatten
only final SUM paths. A nonzero contribution to head S must itself have
support contained in {S}. No unary source has this support when d>=2.
Therefore each context requires at least one PRODUCT whose support is that
singleton. Choose the earliest such PRODUCT for each context.

Remove all uses of singleton PRODUCT features from subsequent PRODUCT
parents in the SUM-flattened graph. At the chosen earliest singleton node
for context S, every earlier singleton feature belongs to another context
and is zero at S. Removing those features, and their propagated
contributions, does not change that node's positive value at S. Its other
values cannot increase and were zero. All chosen singleton nodes therefore
remain valid, and their readouts may be positively rescaled to one.

These N nodes can now be placed at the end. The other nodes are auxiliary
PRODUCTs on sources and preceding auxiliary nodes only. For a graph of
minimum PRODUCT count, no auxiliary can be zero or a singleton: a zero
node can be omitted, and a singleton auxiliary can replace its terminal
node and remove that terminal PRODUCT. Likewise an auxiliary support already
available by a SUM can be replaced by that SUM, preserving every later
support and permitting terminal rescaling. Thus a minimum exact graph has

`N terminal singleton PRODUCTs + q nontrivial auxiliary PRODUCTs`.

Each auxiliary adds a previously unavailable non-singleton support; each
terminal singleton is the intersection of two available SUM supports. This
is an extensional exact-support normal form, not a learner equivalence or
permission to remove a small nonzero feature.

## 5. A finite exhaustive proof of the three-bit exact minimum

On three bits, encode supports by eight-bit integers. Initially available
SUM supports are all unions of the six unary half-cubes, including zero.
Call this union-closed family A; it has 28 members. One auxiliary PRODUCT
chooses a,b in A and adds support h=a&b. Its updated family is exactly

`A union {a|h: a in A}`.

Discard h already in A or of singleton support, as justified by section 4.
After q auxiliaries, a context is available for a terminal PRODUCT iff its
singleton mask equals a&b for some a,b in A. Thus P<=11 would require all
eight singleton masks after at most three auxiliaries.

The exact enumeration includes every such choice. It identifies states only
under the 48 coordinate-permutation/bit-flip automorphisms of the full cube;
each preserves the source family, union, intersection and all singleton
targets. Canonicalization therefore loses no possible continuation in this
explicit support class.

| Auxiliary PRODUCTs q | Distinct state orbits | Maximum available singleton terminals |
|---:|---:|---:|
| 0 | 1 | 0 |
| 1 | 8 | 2 |
| 2 | 266 | 4 |
| 3 | 10,835 | 6 |

No q<=3 state can supply all eight. Four auxiliary pair indicators, for
example all assignments to the first two bits, followed by their eight
products with the third-bit indicators, give a twelve-PRODUCT exact graph.
Therefore the **exact support and mass minima are twelve**. At the minimum
cap nine the exact conditional minimum is also twelve.

This is a computer-assisted finite proof for the complete stated exact
class, not an optimizer's failure to find a smaller graph. The executable
audit checks source-preserving automorphisms and cross-checks the first two
levels against ordered raw auxiliary sequences with no symmetry quotient.
The small search is regenerated; its state cache is not committed as a
research artifact. Higher-dimensional exact minima are not decided here.

## 6. Why terminalization fails for limits

The recursive nine-PRODUCT construction makes the failure concrete.
G_empty tends to the empty-set singleton, but

`epsilon^(-1) G_empty x_(i,1) = G_{i}`

tends to a different singleton. The positive tail that disappears in the
first limit becomes the next output after a legal source product and SUM
amplification. Replacing the parent by its limit first would make this
descendant zero. A node with nearly singleton support cannot be treated as
terminal without accounting for every legal future continuation.

Thus at d=3 the result is a strict shared-output separation:

`exact PRODUCT minimum = 12`,

`approximation PRODUCT minimum = 9`.

It holds even with a finite local coefficient alphabet, bounded intermediate
features, and the same minimum final-normalizer cap, when SUM construction
length is allowed to grow. The distinction is not a new semantic action;
it follows from the existing positive grammar and source annihilators.

## 7. A construction-resource phase, not just a node-count distinction

Fix d=3, cap nine and local coefficient alphabet {1/2,1,2}. Let S count
weighted SUMs in the complete source-to-excess construction, including
weighted excess readouts when present. The fixed final base/normalization
stage is separate. With at most p PRODUCTs, every positive excess value is
at least `tau=2^(-S*2^p)`, by the shared-DAG positive-value bound in
[`TWO_PRODUCT_SUPPORT_BORDER.md`](TWO_PRODUCT_SUPPORT_BORDER.md). That bound
counts repeated uses of a SUM through PRODUCT ancestors; it is not a floor
on just the final coefficient.

For p<12, exact singleton support is impossible. If some correct excess
is zero, its probability is at most 1/8 instead of 2/9, giving error at
least 7/72. Otherwise all correct excesses are positive and at least one
wrong excess must be positive. At that context, cap nine makes the wrong
probability at least `(1+tau)/9`. Consequently

`||q-p_target||_infinity >= min(7/72, 2^(-S*2^p)/9)`.

Uniform-context Pinsker also gives excess CE at least one quarter of the
square of this bound. In particular, for any fixed p in {9,10,11}, the
minimum SUM construction needed for probability accuracy delta tending to
zero is **Theta(log(1/delta))**. The lower inequality is

`S >= 2^(-p) log2(1/(9 delta))`

for sufficiently small delta. Our nine-PRODUCT construction has S=13k+6
and probability error <=2^-k/3, providing the matching logarithmic upper
rate. For excess CE tolerance rho, its upper bound is 2*2^(-2k), while the
positive-value lower bound gives

`S >= 2^(-p-1) log2(1/(324 rho))`

for sufficiently small rho. Thus the SUM cost is also Theta(log(1/rho)).
The constants are not sharp.

This proves three different resource regimes for the stated static task:

- P<=8 has a positive loss gap even with unlimited SUM construction;
- 9<=P<=11 approaches Bayes risk with logarithmically growing SUM work,
  but has no finite exact realization;
- P>=12 admits a finite exact witness with bounded SUM overhead.

The asymptotic upper family keeps every intermediate feature <=1. A fixed
floating format still cannot inherit the exact-arithmetic resource law.

## 8. Audit scope

`theory/numerical_checks/decoder_exact_limit_audit.py` performs the exact
support enumeration, constructs actual finite-alphabet graphs, evaluates
every context in its selected grids with Fraction arithmetic, checks all
head tables, node counts, intermediate bounds, normalizers and the rational
chi-square loss upper bound, and retains only aggregate evidence.

Two CPU float64 checks are deliberately separate. At sufficiently small
epsilon, rounded probabilities can equal the exact target even though
exact off-diagonal tails remain positive. At still smaller epsilon, the
common product can underflow before subsequent amplification, destroying
an output whose exact value tends to one. A bounded maximum activation
does not supply a reference/AMP bridge or a lower dynamic-range guarantee.

General exact higher-dimensional counts, optimal finite-SUM error/range
tradeoffs, registered learning and complete Runtime/value/install/persistence
and AMP evidence remain open.
