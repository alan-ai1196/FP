# Repeated evidence: false factor certainty and exponential rational height

Status: **PROVED, SCOPED; EXACT NATIVE AND CHECKED BINARY64 AUDITS**.
This is a dynamic failure of the product-belief learner derived in
[FACTOR_SIMPLEX_POSTERIOR.md](FACTOR_SIMPLEX_POSTERIOR.md). It uses the
existing positive SUM/PRODUCT grammar and global simplex U. Foundation R4
and ERC-1 are unchanged. The audit is passive and gives no Runtime proposal,
resource certificate, AMP relation, installation or new model outcome.

There are two distinct conclusions. Repeated projection can manufacture
certainty between worlds that the observations cannot distinguish. The same
fixed, bounded-range learner can require exponentially many bits in its
explicit reduced rational parameters as the history grows. A native full-
posterior control avoids both failures on the same legal history.

The approximation mechanism is classical assumed-density filtering, whose
loss of information across sequential projections is discussed by
[Minka (2001), sections1-2](https://tminka.github.io/papers/ep/minka-ep-uai.pdf).
Its update is also a positive-polynomial growth transformation; see
[Baum and Sell (1968), section1](https://msp.org/pjm/1968/27-2/pjm-v27-n2-p01-p.pdf).
We do not claim either mechanism as new. The results below identify its
complete native realization, fixed-point failure, exact rational-height
law and actual arithmetic refusal in FP.

## 1. The information a relative observation cannot change

Let the anchored binary worlds be z=(z1,z2), with z0=0, and write
Xj=(-1)^zj. A noisy label0 on the relative query(1,2) has likelihood

`ell(z) = (1 + rho*X1*X2)/2`, with `rho=4/5`.

Its values are9/10 on00 and11, and1/10 on01 and10. These are distinct
fresh observations with positive conditional probability, not repeated use
of one observed event. Any finite all-label0 sequence is legal.

For any positive prior P, the exact Bayes odds P(00)/P(11) remain unchanged
under every such relative observation, regardless of its label. This follows
immediately by canceling equal likelihoods. The worlds are still legally
distinguishable by a later anchor query, so this conditional information
cannot be discarded for a claim about all future forecasts.

The exact sufficient moments of a two-bit law are

`u=E[X1]`, `v=E[X2]`, `c=E[X1*X2]`.

One label0 updates them to

`u'=(u+rho*v)/(1+rho*c)`,
`v'=(v+rho*u)/(1+rho*c)`,
`c'=(c+rho)/(1+rho*c)`.

An independent-factor state restricts c=uv. Its native U computes the
correct one-event marginals from that product prior, then represents the
successor with c'=u'v'. The missing correlation changes the prior used at
the next event. The first event's marginals can be exactly right even while
the represented00:11 odds are already wrong.

## 2. Native dynamics and why constant damping cannot repair it

Use two binary factor blocks with selected theta_jb=q_jb/2, total selected
mass1, fixed feature parameter1, positive bases(1,1), and rate eta=1/2.
The query sources select one of(0,1),(0,2),(1,2); no posterior value is an
input. The existing native graph constructs excesses

`A_y = 8 * SUM_z 1[query(z)=y] * q_1,z1 * q_2,z2`,

including every inactive factor sum in its ambient polynomial. All complete
fixed-feature gradients remain part of the learner state. The previous
factor theorem gives exactly

`u'=(u+rho*v)/(1+rho*u*v)`,
`v'=(v+rho*u)/(1+rho*u*v)`.

At any fixed native rate `0<eta<=1/2`, put alpha=2eta. The successor is the
convex combination of the old biases and these two expressions, with weights
1-alpha and alpha. This is the actual existing U, not an added projection
or damping action.

**Attractor theorem.** For any strictly positive product initializer,
u,v in(-1,1), repeated label0 equality observations have the following limits
for every fixed alpha in(0,1]:

- If u+v>0, the factor law converges to the point mass at00.
- If u+v<0, it converges to the point mass at11.
- If u+v=0, both biases converge to0 and the represented law converges to
  independent fair bits.

To prove this put s=u+v, d=u-v and p=uv. The actual recurrence gives

`s'=s * [1+alpha*rho*(1-p)/(1+rho*p)]`,
`d'=d * [1-alpha*rho*(1+p)/(1+rho*p)]`.

The bracket for s is greater than1 in the strict interior, while the bracket
for d lies strictly between0 and1. The interior is preserved, since each
update is a positive posterior marginal, possibly mixed with the old one.
If s is nonzero, its sign is fixed, |s| increases and is bounded by2; d
also converges with fixed sign. At the limit the s increment must vanish.
Since its limit is nonzero, p must approach1. Thus both biases approach
the same endpoint with the sign of s. If s=0, v=-u and

`u'=u * [1-alpha*rho*(1-u^2)/(1-rho*u^2)]`.

Its magnitude decreases. Any nonzero limit below1 would have a strictly
positive decrement, so the limit is0. This proves all three cases.

In contrast, full Bayes tends to the prior conditioned on{00,11}. Its limiting
common marginal bias is `(u+v)/(1+uv)`, strictly between-1 and1. The initial
00:11 odds persist. In the s=0 case both limiting marginals are fair, but
the full law is correlated: its next equality-label0 forecast tends to9/10,
whereas the product learner's tends to1/2.

Thus every positive constant damping rate retains this structural failure.
Rate0 suppresses learning. Reducing a fixed positive rate changes convergence
time, not the limiting law. This statement does not cover every possible
adaptive rate schedule or every approximation family.

For symmetric initial biases u=v=epsilon>0, the product learner eventually
forecasts9/10 on an anchor, whereas full Bayes tends to
`1/2 + rho*epsilon/(1+epsilon^2)`. Across positive rational product
initializers the discrepancy approaches2/5 as epsilon tends to0. This is
a family of declared initializers, not a claim that every such initializer
is reached by the particular fixed-Gamma history below.

## 3. A legal fixed-Gamma witness

Start from the uniform four-world prior and observe label0 once on(0,1),
then once on(0,2). Both native factor learning and full Bayes give independent
q1=q2=(9/10,1/10). Now take k further fresh label0 observations on(1,2).
At the undamped native rate1/2, both factor biases equal m_k with

`m_0=4/5`, `m_(k+1)=9*m_k/(5+4*m_k^2)`.

For0<m<1 the increment is `4*m*(1-m^2)/(5+4*m^2)>0`; hence m_k tends to1.
The first values are4/5,20/21,756/761,5177844/5181749.

Full Bayes instead has the exact00/01/10/11 law

`P_k = (81*9^k, 9, 9, 9^k) / (82*9^k+18)`.

Its marginal bias is `40*9^k/(41*9^k+9)`, tending to40/41. For k=0 and1
the factor marginals still agree with these full-posterior marginals. The
factor law nevertheless changes the00:11 odds from81 to1681 at k=1; the
true odds stay81. The next projection uses this false new prior, and the
marginal biases differ from k=2 onward. Indeed, full Bayes has strictly
positive covariance after k>=1, so its next marginal update is strictly
less than f(m)=(1+rho)m/(1+rho*m^2). This f is strictly increasing on(0,1),
which preserves the strict comparison with the projected recurrence.

Consequently a subsequent anchor-label0 forecast has limits

`native factor: 9/10`, `full Bayes: 73/82`, `gap: 2/205`.

No numerical error, negative mass, extra optimizer action or weakened
baseline is needed. The approximation discards correlation and repeatedly
changes conditional odds that its new observations do not identify.

## 4. Exact rational height grows exponentially in the history length

Write m_k=a_k/b_k in lowest terms. The scalar recurrence is

`a_(k+1) = 9*a_k*b_k/g_k`,
`b_(k+1) = (5*b_k^2+4*a_k^2)/g_k`,

where g_k is the gcd of the two raw integers. The first reductions have
g_0=9 and g_1=5, giving (a_2,b_2)=(756,761).

**No further cancellation.** At k=2, a is even, divisible by3 and not by5;
b is odd and divisible by neither3 nor5. These conditions persist. With
gcd(a,b)=1, a common divisor of a and5b^2+4a^2 must divide5, and a common
divisor of b and that denominator must divide4. Both are excluded by these
conditions. The denominator is also nonzero modulo3. Hence

`gcd(9ab,5b^2+4a^2)=1` for every k>=2.

In particular

`5*b_k^2 < b_(k+1) < 9*b_k^2`.

Taking base2 logarithms and iterating proves **log2(b_k)=Theta(2^k)**.
The actual selected native parameters are `(b_k+a_k)/(4*b_k)` and
`(b_k-a_k)/(4*b_k)`, each repeated in the other block. Since a is even,
b is odd and gcd(a,b)=1, their denominators reduce to exactly4b_k. Thus
the explicit reduced rational learner state also uses Theta(2^k) bits.

This happens in a fixed44-node/77-incidence Program with only four learned
slots. Its selected degree is2; all internal values stay in[0,8], masses
in[1,9] and normalizer exactly10. The cause is repeated nonlinear updating,
not increasing graph size or exploding real-valued range.

For the same history, every component of P_k has O(k) numerator/denominator
bits. The off-diagonal component, for k>=1, is exactly
`1/[2*(41*9^(k-1)+1)]`, giving a matching Theta(k) lower bound. A native
single four-category factor at rate1 retains this full posterior. It has
the same four learned slots and a38-node/70-incidence graph in this witness.
There is no parameter-count advantage for the two-factor representation
on this smallest example; its purpose is to isolate the dynamic failure.

These are laws for **explicit reduced rational scalars**. The tuple
(recurrence,k) is a short symbolic description of m_k, so there is no
information-theoretic lower bound on arbitrary encodings. Decoding it into
the stated explicit scalar still has the proved output size. No analogous
height law is claimed here for every damped rate or every approximate backend.

## 5. Actual arithmetic pressure and minimal evidence

Run `python -B experiments/joint_uncertainty/factor_repetition_dynamics.py`.
The retained result is
[`FP_FACTOR_REPETITION_DYNAMICS.json`](../../evidence/minimal/FP_FACTOR_REPETITION_DYNAMICS.json).
It contains bit counts and short witnesses rather than enormous fractions.

| Equality repetitions k | Factor parameter denominator bits | Full-posterior maximum parameter bits |
|---:|---:|---:|
|0|5|7|
|2|12|10|
|5|101|20|
|10|3,260|35|
|11|6,521|39|
|12|13,042|42|
|14|52,171|48|
|15|104,343|51|

The integer recurrence is independently checked through k=15 under a declared
131,072-bit oracle ceiling. The actual native path uses the unchanged
32,768-bit reference guard. It checks13 complete units (two anchors plus11
repetitions), including full fixed-feature gradients and both observed and
committed states. The next gradient attempt returns `UNRESOLVED` before a
new observed/committed boundary. This conservative arithmetic refusal does
not prove that every arithmetic schedule must fail at k=12. By k=14, however,
even a reduced endpoint parameter exceeds the32,768-bit representation cap.

The full-joint native control passes130 complete units under the same guard,
including128 repetitions and129 independent subsequent anchor readouts.
Its final parameter maximum is409 bits. A separate25 asymmetric signed-prior
pairs, four fixed rates and both labels check200 native units against the
two-bias recurrence and its sum/difference identities. In total the exact
audit checks343 native units and686 complete-state boundaries.

The actual ordered CPU binary64 learner also executes66 complete units
(two anchors plus64 repetitions), with25,450 primitive results individually
checked against exact rounding. On the13-unit affordable exact-native prefix,
all native values, probabilities, full gradients and committed parameters
have absolute errors below10^-12. Later units are checked binary64 executions,
not certified continuations of the refused exact reference path. Its final
anchor probability is the binary64 encoding of0.9, while full Bayes gives
about0.8902439024; the exact decoded gap exceeds9/1000. Every selected
parameter is still strictly positive. Finite arithmetic therefore does not
explain or cure the observed inference error, and a displayed0.9 is not a
license to replace the complete state with a point mass.

The result rules out treating local posterior-marginal correctness, constant
parameter count or bounded native range as sufficient for faithful and cheap
long-history inference. It calls for retaining the missing correlation or
declaring a justified approximation. It does not call for a new semantic
architecture action, reopening static ERC cases, or changing the completed
model experiments.
