# Fresh paired log-loss evidence can have a fast rate

Status: **PROVED under the declared bounded-prediction and conditional-law
assumptions**, 2026-09-06. This derives a power bound for the existing FP linear
e-process. It introduces no new architecture action or evidence identity.

## 1. Validity and power are different statements

For one continuous, fixed candidate/base certification identity, use fresh
paired same-path log-loss gain

\[
Y_t=\log\frac{q_{C,t}(Y\mid X)}{q_{D,t}(Y\mid X)}.
\]

Both binary forecasts lie in `[1/4,3/4]` at every context, so
`|Y_t|<=log3<9/8=:B`. Preregister the constant bet `eta=1/24` and use

\[
\boxed{E_n=\prod_{t=1}^n(1+Y_t/24).}
\]

This is exactly the canonical e-process with `lambda=B/24=3/64`. Under the
mean-null `E[Y_t|F_(t-1)]<=0`, it is a nonnegative supermartingale and crossing
`1/alpha` has probability at most alpha. **This validity statement does not
assume that the candidate is Bayes or that a structural gap exists.**

The power statement below additionally assumes an explicit conditional law and
a uniform positive alternative. Profile/discovery labels have already been
consumed; none contribute fresh factors. Alpha, both lineages, forecast paths,
and state trajectories must stay bound to the same admitted identity.

## 2. A log-loss second-moment inequality

For binary distributions `p,q` in `[1/4,3/4]`,

\[
\boxed{\mathbb E_p[\log^2(p_Y/q_Y)]\le3\,KL(p\Vert q).}
\]

Here is an elementary constant-specific proof. Put `z=log(p_y/q_y)`, so
`|z|<=log3<9/8`. For negative z, `z+exp(-z)-1>=z^2/2`. For nonnegative z,
the fifth-order Taylor lower bound for `exp(-z)` gives

\[
z+e^{-z}-1\ge z^2(1/2-z/6+z^2/24-z^3/120)\ge z^2/3.
\]

The parenthesized polynomial decreases on `[0,9/8]` and at its endpoint equals
`7237/20480>1/3`. The bound `log3<9/8` follows already from the fourth-order
Taylor lower bound `exp(9/8)>=100331/32768>3`. All constants are rational.
Taking expectation uses `E_p[exp(-z)]=sum_y q_y=1`, proving the inequality.

For a candidate and comparator, define conditional excess risks relative to
the true conditional Bayes law, averaged over the fresh context:

\[
\epsilon_t=\mathbb E_X KL(p_X\Vert q_{C,t,X}),\quad
D_t=\mathbb E_X KL(p_X\Vert q_{D,t,X}),\quad
\mu_t=D_t-\epsilon_t=\mathbb E[Y_t\mid\mathcal F_{t-1}].
\]

If true conditional probabilities also lie in `[1/4,3/4]`, squaring the
difference of the two log ratios and applying the inequality yields

\[
\boxed{\mathbb E[Y_t^2\mid\mathcal F_{t-1}]
\le6(D_t+\epsilon_t)=6(\mu_t+2\epsilon_t).}
\]

This is a loss-specific variance/mean relation. The broader fast-rate connection
between Bernstein-type conditions and log loss is established in
[van Erven et al., Fast Rates in Statistical and Online Learning](https://jmlr.org/papers/v16/vanerven15a.html).
The explicit inequality and the FP persistence bound here are proved directly;
that literature is not invoked as a generic oracle for an arbitrary learner.

## 3. High-probability crossing in O(1/gap) fresh events

Assume throughout the still-live certification run that

\[
D_t\ge\Delta>0,\qquad\epsilon_t\le\Delta/6.
\]

Then `mu_t>=Delta-epsilon_t`. For `|u|<=1/2`,
`(1+u)^(-1)=1-u+u^2/(1+u)<=1-u+2u^2`. Since `|Y_t/24|<1/2`,

\[
\begin{aligned}
\mathbb E[(1+Y_t/24)^{-1}\mid\mathcal F_{t-1}]
&\le1-\mu_t/24+\mathbb E[Y_t^2\mid\mathcal F_{t-1}]/288\\
&\le1-(\mu_t-2\epsilon_t)/48\\
&\le\boxed{1-\Delta/96}.
\end{aligned}
\]

Let `tau` be the first crossing of `1/alpha`. Apply the reciprocal contraction
to `Z_n=1[tau>n]/E_n`. Setting it to zero on crossing only decreases its
conditional expectation, so `E[Z_n]<=(1-Delta/96)^n`. On `tau>n`, `Z_n>alpha`.
Consequently

\[
\boxed{P(\tau>n)\le\alpha^{-1}(1-\Delta/96)^n.}
\]

This proof only uses the candidate/base path **before** crossing. It does not
assume an uncertified post-install continuation or transfer wealth to a new
lineage. A sufficient budget for failure probability beta is
`n>=(96/Delta) log[1/(alpha beta)]`.

The improvement is conditional on a small candidate excess risk and the bounded
log-loss structure. Merely asserting a positive mean for an arbitrary bounded
statistic does not imply this rate. No claim is made that these constants are
optimal or that finite no-crossing is rejection.

## 4. Application to the registered FP value witness

Use the fresh iid uniform-context law with true target
`p^0=(1/2,1/2,3/4,1/4)`, independent of already-consumed profile information.
For any at-most-one-PRODUCT comparator under the fixed normalizer cap 4,
XVII.3 gives `D_t>=Delta=1/1568`, provided its **entire forecast function** is
chosen predictably before the fresh context. It may otherwise change using
past observations; the lower bound covers every eligible function, not a weak
hand-selected comparator.

The registered two-PRODUCT learner from XVII.5, after 32 profile steps and then
a preregistered frozen scoring phase, has `epsilon<=Delta/6`. The exact proof
and finite-encoded version both certify this. Freezing is a declared evaluation
schedule, not a retrospective change after inspecting fresh gains. The stronger
comparator class includes the same frozen schedule as a special case.

For `alpha=beta=1/20`, a conservative all-rational sufficient fresh budget is

\[
\boxed{n=9\cdot96\cdot1568=1{,}354{,}752.}
\]

Indeed `(1-c)^n<=exp(-nc)<2^{-9}`, so the no-crossing probability is below
`20/512=5/128<1/20`. This is a theoretical sufficient budget, **not** a report
of that many executed fresh events, a memory/FLOPs budget, or a complete
Runtime/AMP certification. The true future law is an assumption for power;
16 profile labels cannot establish it with certainty.

## 5. Certified lower score enclosures retain validity

Exact logarithms need not be encoded as exact real machine values. If the
registered reference calculation supplies `Y^-<=Y<=Y^-+rho` and `Y^->=-B`,
then `E^-_n=product(1+Y^-_t/24)` is still valid under the original mean-null.

For `rho<=1`, the extra reciprocal-contraction error is at most

\[
\rho/24+(2B\rho+\rho^2)/288\le\rho/16.
\]

Hence if `rho<=Delta/12`, the same argument gives the rate `1-Delta/192`.
For the FP constants, 16 terms of the rational atanh log series give a uniform
score enclosure of width below `2^-32<Delta/12` for ratios in `[1/3,3]`:
write `z=(r-1)/(r+1)` and truncate
`log r=2 sum_(k>=0) z^(2k+1)/(2k+1)` after 16 terms. The absolute remainder
is at most `2|z|^33/[33(1-z^2)]`; the symmetric interval width is at most
`1/53150220288`. Taking the maximum of its lower endpoint and `-B` preserves
the enclosure and enforces the registered bound.
The conservative sufficient budget for that **mathematical lower-score
e-process** is `2,709,504` fresh events at the same alpha/beta.

Storing or comparing accumulated wealth also needs sound arithmetic. Rounding
its product or log upward is not authorized by this score-enclosure result.
The audit does not claim a bounded-memory wealth implementation or an AMP
bridge; any such additional error needs its own composition bound.

## 6. A necessary scope check: when static gap does not transfer

If a controller sees the current context **before choosing its forecast
function**, the preceding structural-to-conditional-mean step can fail. For
example, it can select among constant mass pairs `(1,1)`, `(1,3)`, `(3,1)` to
match `p^0` at the observed context. Each chosen constant function contains
zero PRODUCTs and obeys cap 4, but the overall context-dependent controller
implements the missing interaction. Applying the static uniform-table bound
to each selected function after conditioning on its selection is unsound.

This is a counterexample to a forecast-class inference, not a certified FP
installation trace: the controller's information, value construction, costs,
ownership and install authorizations would have to be part of complete Omega.
One cannot erase them and call this a zero-PRODUCT complete self-Compiler.
Real language-model contexts often depend on already-revealed history, so the
fresh iid-context premise must not be silently imported there.

Validity of the mean-null e-process remains as stated. What fails without the
extra premise is the proposed positive-drift/power guarantee, not Ville's theorem.

Exact inequality/enclosure audit: `theory/numerical_checks/log_loss_persistence_audit.py`.
