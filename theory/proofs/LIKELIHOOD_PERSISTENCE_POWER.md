# Finite fresh-evidence power for the owned likelihood learner

Status: **PROVED, SCOPED; EXACT NATIVE AND FINITE AUDIT**. This connects the existing
unit-simplex likelihood learner to the existing bounded, downward-rounded
persistence arithmetic. It changes neither the learner nor the persistence
null, bet, tolerances, source contract or running experiment. The stochastic
premises concern power, not validity. Physical completion remains a separate
obligation.

## 1. The declared alternative and the information cut

Fix the candidate after its complete profile. Its positive weights `w_h`
are the posterior over the finite known-noise relation worlds, with global
flip duplicates combined exactly as in the native graph. Under the power
alternative, draw the hidden world H with these weights. Each subsequent
label is its queried relation XOR an independent Bernoulli(1/10) error.
Queries can depend on earlier revealed observations, but their selection
must supply no extra information about H given that history and no current
target information. Fixed exogenous query orders are included.

The exact candidate continues its actual unit-rate simplex U. Its pre-target
probability p is therefore the conditional label law, always in [1/10,9/10].
The still-deployed baseline is uniform. Define

`g_t = log(2 p_t(Y_t))`, `f_t = 1 + g_t/8`, `W_t = PRODUCT_(s<=t) f_s`.

The coefficient 1/8 is the registered bet3/4 divided by bound6. The ideal
W is an analysis variable; it is not stored wealth, an authorized replacement
for physical forecasts, or an e-process under a newly substituted null.
Validity of the existing lower wealth still uses the original pre-context
mean-null, independently of the stronger alternative used here.

Let `a=log(9/5)`, `b=log(5)`, and

`u=log(1+a/8)`, `v=log(1-b/8)`, `A=(u-v)/(a+b)>0`.

The letter v in this section is a negative log factor; below the separate
multiplicative distortion is denoted r.

## 2. Learning uncertainty has an additive evidence cost

For every label sequence and every world h of initial weight w_h, ordinary
Bayesian telescoping gives

`PRODUCT p_t(Y_t) = SUM_h w_h PRODUCT p_h(Y_t)`.

Consequently, if N_h is the number of labels disagreeing with world h,

`SUM g_t >= (T-N_h)a - N_h b + log(w_h)`.

This is the finite Bayesian mixture log-loss inequality, here realized by
the actual native U. It does not discard any other world, freeze the learner
or require the posterior to have already identified H.

Concavity places `log(1+g/8)` above its endpoint chord on [-b,a]. Summing the
chord and using the preceding inequality proves the pathwise bound

`log(W_T) >= (T-N_h)u + N_h v + A log(w_h)`.                 (1)

Thus uncertainty in h contributes the additive cost `A log(1/w_h)` to this
lower bound. Zero-current-gain queries and later learning remain part of the
same trajectory. This is not a per-event positive-gap assumption. Conditional
on h under the stated alternative, N_h has the Binomial(T,1/10) law even for
the allowed adaptive query choices.

## 3. Control of downward excursions under that alternative

For z in [-log5,log(9/5)],

`z^2 <= 3 (z + exp(-z) - 1)`.

For z<=0, the exponential series gives the stronger constant2 inequality.
For 0<=z<9/8, the fifth-order lower Taylor bound for exp(-z) yields
`z+exp(-z)-1 >= z^2(1/2-z/6+z^2/24-z^3/120) >= z^2/3`;
the last polynomial decreases on [0,9/8] and is greater than1/3 there.
The elementary exponential series verifies log(9/5)<9/8 and log5<2.

Because p is the conditional law and the baseline is uniform,
`E_p exp(-g)=1`. If `mu=E_p g=KL(p||uniform)`, then
`E_p g^2 <= 3 mu`. Also f>3/4. The exact identity

`1/(1+g/8) = 1-g/8 + (g/8)^2/(1+g/8)`

therefore gives

`E_p(1/f) <= 1-mu/8+mu/16 = 1-mu/16 <= 1`.

Averaging over a legal next query retains this bound. Hence 1/W is a
nonnegative supermartingale under the power alternative, starting at1.
For any e>0,

`P(min_(s<=T) W_s < e) <= e`.                              (2)

This reciprocal statement uses the correct-posterior alternative. It is
not asserted under the original gain-mean null or under a fixed arbitrary
hidden world after conditioning away the posterior mixture.

The scope difference has a native witness. From the fair two-world learner,
one label1 at query(0,1) makes its next forecast (9/50,41/50). Conditional
on the equal-bit world, the next label law is instead (9/10,1/10), and the
inverse-factor expectation is greater than1. Under the posterior mixture
it is less than1. The audit checks both exact inequalities.

## 4. AMP, lower log scores and the actual wealth grid

Suppose a successful physical score supplies `ell_t >= g_t-rho`, with
the existing bound check also satisfied. The registered wealth recurrence is

`R_t = delta floor(R_(t-1) (1+ell_t/8)/delta)`, `R_0=1`.

Take `0<=rho<6`, `r=1-rho/6` and `delta=2^(-wealth_grid_bits)`.
Since f>3/4,

`1+ell_t/8 >= f_t-rho/8 >= r f_t`.

Induction, including the actual downward floor, yields

`R_t/(r^t W_t) >= 1-delta SUM_(s<=t) 1/(r^s W_s)`.          (3)

This inequality is used only before that path's first crossing. A crossed
identity need not be continued or reset. If every W_s>=e through T, then
the right side is at least `1-delta T/(r^T e)`. Choose any `0<kappa<1` and
set `e=delta T/(kappa r^T)`. On this common good event,

`R_t >= (1-kappa) r^t W_t`, for every still-live t<=T.        (4)

Several paths satisfying the same lower score error bound obey (4) on the
same event. There is no union penalty merely for reference and AMP paths.
If `(1-kappa) r^T W_T >= 1/alpha`, they must all have crossed by T, provided
their required calculations and premises have remained available.

The current successful AMP bridge, against the actual uniform baseline,
has `|p_AMP-p|<=1/1000`. Thus

`g_AMP >= g - log(100/99)`.

The actual stored-mass score uses `mass_y / SUM mass`, not an unverified
floating division value. Its ratio to1/2 lies in [99/500,901/500]. The
production12-term log reduction has residual in [1,2) and exponent magnitude
at most3 on this interval. Each series tail is at most

`2 (1/3)^25 / (25 (1-1/9))`.

The combined width is at most four such tails, less than2^-32. Since
`log(100/99)<1/99` and `1/99+2^-32<1/98`, both the exact-reference lower
score and a successful AMP lower score satisfy the common choice

`rho=1/98`, `r=587/588`.

This is a bound for already successful bridge and score premises. It does
not condition a statistical claim on whichever executions happen to pass.

## 5. A computable finite-horizon power bound

Let `C_T(k)=P(Binomial(T,1/10)<=k)`, with C_T(-1)=0. For each initial world
weight w_h let k_h be the largest integer in [0,T] satisfying

`(T-k_h)u+k_h v+A log(w_h) >= log(1/[alpha(1-kappa)r^T])`;

put k_h=-1 if none qualifies. Combining (1), the exact binomial law and
(2)-(4) gives

`L = max(0, SUM_h w_h C_T(k_h) - delta T/(kappa r^T))`.      (5)

If all numerical/physical premises hold throughout the required trajectory,
the paired crossing probability by T is at least L. Without that unproved
completion premise the valid statement is

`P(no operational/premise failure through T AND no paired crossing) <= 1-L`.

Equivalently, a crossing-probability lower bound subtracts the probability
of such a failure. No completion probability is supplied here. A persistence
crossing still does not by itself attest install reachability, ownership,
fresh admission, alpha allocation or full-state transport.

For the registered64-event horizon, alpha1/4, grid16, kappa1/4 and the
common AMP rho above, the drawdown allowance is less than0.004356. The
[exact audit](../../evidence/minimal/FP_LIKELIHOOD_PERSISTENCE_POWER.json)
computes (5) from the four retained training profiles:

| Initial profile | T | Lower bound L, rounded down |
|---|---:|---:|
| n8, c2, seed16 | 64 | 0.892775 |
| n8, c2, seed17 | 64 | 0.892855 |
| n8, c4, seed18 | 64 | 0.808954 |
| n8, c4, seed19 | 64 | 0.809044 |

Only the profile is used; no evaluation target or completed GPU score enters
this calculation. These are theoretical posterior-mixture
power bounds for new labels under the declared law, not empirical success
frequencies or a new prospective claim about the reused tapes.

## 6. Fixed-grid almost-sure power is false

Use the existing native relation graph at a self-pair query. Every world
predicts (9/10,1/10), so the ordinary unit-rate simplex learner keeps its
selected weights while advancing its clocks and retaining/clearing the
actual ambient gradients. Under the correct noise law, label1 has
probability1/10 on each step.

Consecutive label1 events multiply ideal wealth by `1-log5/8<1`. With
the actual grid16 floor and production12-term lower scores, exactly45 of
these events reach zero, with wealth1/65536 immediately before the last.
That event has probability10^-45, and
zero is absorbing even if all later labels favor the candidate. In contrast
the unrounded process has positive mean log increment
`(9/10)u+(1/10)v>0` and crosses any finite threshold almost surely under
this IID law. Thus an unrounded eventual-power theorem cannot be silently
transferred to the existing bounded wealth representation.

This is not a validity counterexample: floor losses only reduce evidence.
It explains why the finite T, delta and error terms in (5) are necessary.
No new precision mode, floor repair or evidence action is introduced.

## 7. Audit and relation to earlier work

Run `python -B experiments/joint_uncertainty/likelihood_persistence_power.py --write`.
The audit uses exact rational interval arithmetic with outward rounding and
the independent exact log verifier. It checks the scalar inequalities,
native continuous learner trajectories, Bayesian telescoping, the actual
wealth helper against the accumulated floor-error bound, the absorption
counterexample, and exact binomial sums for the four original profiles.
It executes no GPU worker and retains no world-weight or event-tape dump.
The complete audit checks158 interior chord inequalities,81 reciprocal
expectations, all64 six-label words with384 continuous native units,
1,536 exact mixture domination comparisons,384 actual floor compositions,
the45-unit absorption witness, the fixed-world scope counterexample and126
certified binomial cutoff comparisons. All log conclusions use exact
enclosures independently verified before outward rational interval arithmetic.

Finite Bayesian mixture regret is established background; see
[Reid et al., Generalized Mixability via Entropic Duality](https://proceedings.mlr.press/v40/Reid15.html).
The earlier FP [log-loss persistence power result](LOG_LOSS_PERSISTENCE_COST.md)
used a uniform positive alternative and explicitly left bounded wealth
composition open. The [filtration criterion](PERSISTENCE_FILTRATION_GEOMETRY.md)
rules out context-weighted shortcuts under the original null. The result
here keeps that null and actual bet, replaces the uniform-gap premise by
the owned mixture's cumulative learning bound, and accounts for the existing
AMP error and finite wealth grid. It supplies no new model outcome or
complete Runtime certificate.
