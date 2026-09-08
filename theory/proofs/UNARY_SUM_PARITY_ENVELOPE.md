# The exact unary-SUM parity envelope in every dimension

Status: **PROVED**, 2026-09-08. This closes the former multi-input conjecture.
The proof retains the complete normalized unary-SUM family; no symmetry
restriction, local optimizer, finite architecture menu or regularizer is used.

## 1. Scope and sharp result

Let d>=2, N=2^d, chi(x)=(-1)^(sum x_i), and contexts be uniform. Binary targets
are p_1(x)=eta at even parity and 1-eta at odd parity, 0<=eta<1/2. The declared
sources are unary indicators. Any finite static scalar positive SUM DAG,
regardless of size, depth or sharing, has final masses

`M_y(x)=1+sum_i w_(i,x_i,y)`, with w>=0,

and one final normalization q_y=M_y/(M_0+M_1). The lower proof even permits
any strictly positive affine masses on the cube. No internal normalization,
recurrence, joint source or context-aware external choice is included.

Writing H for binary entropy in nats,

\[
\boxed{\inf_{SUM}L=\log2-2^{1-d}[\log2-H(\eta)].}
\]

Every finite program has strictly larger loss for d>=2 and eta<1/2. A native
SUM construction below has excess at most 2/K and final normalizer at most
`2+K+2(d-1)K^2`. Thus this is a sharp infimum, not a finite endpoint that may
be installed. At eta=1/2 the constant base attains log2. For d=1 the infimum
is H(eta), attained at finite coefficients when eta>0.

## 2. A normalized affine table has parity discrepancy less than one

**Lemma.** If f is strictly positive affine on the cube and h is affine with
`0<=h<=f` at all vertices, then for d>=2

\[
\left|\sum_x\chi(x)h(x)/f(x)\right|<1.
\]

The numerator may vanish. Flip individual input coordinates so
`f(x)=c+sum_i t_i x_i`, with c>0 and t_i>=0. This only changes the overall
sign of chi. Write h=h_0+sum_i h_i x_i. Positivity at the vertex minimizing h
and at the zero vertex gives

`sum_i max(-h_i,0)<=h_0<=c`.

Set `I=sum_x chi(x)/f(x)` and `J_i=-sum_x chi(x)x_i/f(x)`. Integrating
`1/f=int_0^infinity exp(-s f) ds` and factoring the cube sum proves

\[
I=\int_0^\infty e^{-cs}\prod_j(1-e^{-t_j s})\,ds\ge0,
\quad
J_i=\int_0^\infty e^{-(c+t_i)s}\prod_{j\ne i}(1-e^{-t_j s})\,ds\ge0.
\]

In particular

\[
I+J_i=\int_0^\infty e^{-cs}\prod_{j\ne i}(1-e^{-t_j s})\,ds<1/c.
\]

There is at least one remaining coordinate, with finite t_j; a zero slope
makes that factor zero, and a positive finite slope makes it strictly below
one. Consequently

`sum chi h/f = h_0 I - sum_i h_i J_i`
`<=h_0 I + sum_i max(-h_i,0) J_i`
`<=c(I+max_i J_i)<1`.

Apply the same argument to f-h for the opposite sign. The constant one is
sharp as a supremum: `h=1`, `f=1+K sum_i x_i` tends to a single-corner
indicator. This lemma concerns normalized affine probabilities, rather than
the parity discrepancy of arbitrary linear-threshold classifiers.

The sharpness also holds with base one in **both** outputs: choose masses
`M_1=K` and `M_0=1+K^2 sum_i x_i` and let K grow. By fixing the other inputs
and averaging this lemma, every nonempty k-coordinate Fourier coefficient of
a unary-SUM prediction satisfies `|E[chi_S q]|<=2^(-k)`, strictly at finite
positive masses; the same corner construction on those k inputs approaches
equality. For k=1 this is the elementary range bound. Higher-order coefficients
need not vanish after normalization, but their sharp amplitude decays with
interaction order. This does not erase their information or provenance.

Order geometry alone is insufficient: on four inputs take q=3/4 for Hamming
weight at most two and q=1/4 otherwise. Every threshold cut is linearly
separable, yet `sum chi q=3/2>1`; its log-odds parity contrast is three times
its oscillation. Such an ordered table cannot be substituted for affine masses.

## 3. Log-ratio parity contrast cannot exceed its oscillation

**Lemma.** For strictly positive affine A,B and z=log(A/B),

\[
\boxed{\left|\sum_x\chi(x)z(x)\right|\le\max_xz(x)-\min_xz(x).}
\]

For d>=2 the inequality is strict when A/B is nonconstant.

Let `f_t=(1-t)B+t A`, `v_t=(A-B)/f_t`, t in [0,1]. If A/B is nonconstant,
let m_t and M_t be the minimum and maximum of v_t. The affine numerator
`[(A-B)-m_t f_t]/(M_t-m_t)` lies between zero and f_t at every vertex.
The preceding lemma therefore gives

`|sum chi v_t| < M_t-m_t`.

Writing r=A/B, `v_t=(r-1)/(1+t(r-1))` is strictly increasing in r. Its extreme
vertices are independent of t. Integrate the last inequality and use
`int_0^1 v_t dt=log r`. The integral of M_t-m_t is exactly
`log r_max-log r_min`, proving the result, including strictness. If r is
constant both sides vanish. This argument does not assume that intermediate
log ratios are affine; the interpolated **masses** are affine.

## 4. Convert the contrast bound into the exact noisy-loss lower bound

Take `z=log(M_1/M_0)`, `S=sum_x chi(x)z(x)` and
`G=sum_x log cosh(z(x)/2)`. For a nonconstant z its maximum and minimum occur
at distinct vertices. Nonnegativity of all other log-cosh terms and convexity
give

\[
G\ge\log\cosh(z_{max}/2)+\log\cosh(z_{min}/2)
\ge2\log\cosh((z_{max}-z_{min})/4)
\ge2\log\cosh(|S|/4).
\]

The middle inequality follows by fixing their difference; the minimum occurs
when the two extrema are opposites. For a constant z, S=0 and the final bound
also holds. With a=1-2eta,

\[
L=\log2+(G+aS/2)/N
\ge\log2+\frac2N\{\log\cosh u-a u\},\quad u=|S|/4.
\]

The scalar infimum over u>=0 is H(eta)-log2: for eta>0 it occurs at
`u=atanh(1-2eta)`, and for eta=0 it is the limit as u tends to infinity.
This proves the all-class lower bound. For finite nonconstant masses the
strict oscillation inequality makes the loss strictly larger; a constant
predictor costs at least log2 and cannot attain it either.

Equivalently, if `U=prod_even M_0 prod_odd M_1`,
`V=prod_odd M_0 prod_even M_1` and `P=prod_x(M_0+M_1)`, the log-cosh inequality
is the algebraic statement

\[
P\ge2^{N-2}(\sqrt U+\sqrt V)^2.
\]

It can be audited with rational arithmetic by checking
`D=P-2^(N-2)(U+V)>=0` and `D^2>=4*2^(2N-4)*U*V`.

## 5. A finite unary construction approaching the envelope

Let v_0=(1-eta,eta), v_1=(eta,1-eta) in output-label order and K>=1. Use

\[
M_y(x)=1+K v_{x_1,y}+K^2\sum_{i=2}^d x_i.
\]

All terms are unary SUM contributions. The two contexts with x_2=...=x_d=0
converge to their Bayes targets, while every other context converges to the
uniform prediction. Thus the limit has two Bayes cells and N-2 uniform cells,
giving exactly the displayed envelope. The peak normalizer is
`2+K+2(d-1)K^2`.

For a root cell, q_y is at least `[K/(K+2)] v_(x_1,y)`, so its CE is at most
H(eta)+log(1+2/K). This remains valid at eta=0, ignoring zero target weights.
Outside the root pair, put s=sum_(i>=2) x_i>=1. Each predicted label mass is
at least 1+K^2 s; therefore its loss is at most
`log2+log(1+K/(2+2K^2 s))<=log2+1/(2K)`.
Together with the lower bound,

\[
0<L_K-L_{SUM}^*\le2/K.
\]

No exponential hierarchy or additional PRODUCT is required for this upper
construction. Its finite coefficients, normalizer growth and static nature
remain explicit; no registered optimizer, physical build or fresh evidence is
provided by the algebra.

## 6. What this closes and what it does not

The full degree-below-d family in `PARITY_DEGREE_ENVELOPE.md` has infimum
`H(eta)+2^(1-d)[log2-H(eta)]`. Unary SUM instead has the complementary small
gain below unigram proved here. They coincide only for two inputs or no signal.
At growing d, unary SUM's best gain is exponentially small, while allowing
degree d-1 brings the loss exponentially close to Bayes. A Bayes-capable
competitor's gap over **every unary SUM** is
`(1-2^(1-d))[log2-H(eta)]`, which does not shrink to zero.

As in the two-group theorem, arbitrary unary token coefficients do not weaken
this baseline when hidden binary-group sampling factorizes within each block:
draw one representative token per group and coordinate, apply this bound to
the resulting cube, and average. Group-constant witnesses give the reverse
infimum inequality. This does not supply the hidden groups or their acquisition
cost and is not a quotient of their complete learner states.

Nonuniform contexts, more general targets, recurrence, multiple outputs,
bounded optimal loss/range tradeoffs, registered value/install reachability and
real language-model laws remain distinct questions. The argument introduces
no semantic architecture action and leaves the Foundation and GPU HOLD intact.

Exact rational and outward-log audit:
`theory/numerical_checks/unary_sum_parity_audit.py`.
