# Proper-score transfer at the causal information cut

Status (2026-09-23): **PROVED, SCOPED; EXACT/DECIMAL CPU AUDIT PASS.**
An owned Reference continuation supplies a resource-selection counterexample.
The rounded forecast in that example is the registered exact-RNE simulation,
not an actual CUDA execution. No Foundation, ERC-1, Runtime, experiment input
or certificate class changes. This result is independent of the running
[n64 model matrix](../../experiments/joint_uncertainty/BAND_MODEL_PROTOCOL.md).

The logarithmic-score/KL and quadratic-score identities below are classical
proper scoring rules; see [Gneiting and Raftery (2007), sections 2--3](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf).
The contribution here is their explicit connection to the existing probability
bridge and causal information cut, the sharp error-only upper bound, a real
resource-dependent selection witness, and an ideal-law calculation for the
registered learning task. The finite audit is evidence for the calculations;
the proofs, rather than the grid, establish the universal statements.

## 1. The scored forecast and the law being assumed

Let F_t contain the actual past observations and the current query, before
the current target Y_t is revealed. Assume the declared generative law is
correct and that the native prediction is its posterior predictive

    p_t = P(Y_t=1 | F_t).

In the indexed known-noise model, p_t lies in [a,1-a] with a=1/10. Let q_t
be the exact normalization of the two positive stored F32 masses. It is
F_t-measurable. The existing `indexed_amp.check_prediction` explicitly
checks the proper stored-mass probabilities, as well as the separately
rounded division outputs, against the native prediction. Thus its accepted
probability relation implies

    |q_t-p_t| <= delta,       0 <= delta < a <= 1/2.                 (1)

The model reader scores this proper q_t. The two raw F32 division outputs
need not sum to one and are not substituted for a probability distribution
in this theorem. The registered tolerances give delta=1/1000.

This is a calibration premise under the ideal declared stochastic law, not
a consequence of two deterministic PRNG tapes. If the teacher or noise law
is misspecified, native Bayesian optimality does not follow. Primitive RNE,
ownership, provenance, causal updates and complete-frame conformance remain
separate obligations; a score cannot replace them.

## 2. Sharp conditional log-regret and Brier transfer

For binary log loss ell(q,Y)=-Y log q-(1-Y) log(1-q), conditional expectation
at the pre-target cut gives

    E[ell(q_t,Y_t)-ell(p_t,Y_t) | F_t]
      = D(Ber(p_t) || Ber(q_t)) >= 0.                            (2)

The sharp universal upper bound given only (1) and p in [a,1-a] is

    Psi(a,delta) = D(Ber(a) || Ber(a-delta))
      = a log(a/(a-delta))
        +(1-a) log((1-a)/(1-a+delta)).                           (3)

**Proof.** For fixed p, divergence increases as q moves away from p on
either side. It suffices to consider q=p-delta and q=p+delta. For the first,

    D(Ber(p) || Ber(p-delta))
      = integral_0^delta s / ((p-s)(1-p+s)) ds.

The function 1/(x(1-x))=1/x+1/(1-x) is convex on (0,1), so the integral
is convex in p and attains its maximum on [a,1-a] at an endpoint. For
s>=0 and a<=1/2,

    (a-s)(1-a+s) <= (1-a-s)(a+s),

so the endpoint p=a is at least as bad as p=1-a. Reflection handles the
upward perturbation. Equality is attained by the relaxed probability pair
(p,q)=(a,a-delta). This is sharpness of the probability-error class; it does
not assert that the fixed RNE kernel realizes that pair. The zero-error
case follows directly.

The same integral gives the simpler sufficient inequality

    Psi(a,delta) <= delta^2 / (2(a-delta)(1-a+delta)).             (4)

For the two-coordinate binary Brier loss B(q,Y)=2(q-Y)^2,

    E[B(q_t,Y_t)-B(p_t,Y_t) | F_t]
      = 2(q_t-p_t)^2 <= 2 delta^2.                              (5)

At the registered a=1/10 and delta=1/1000, (3) is approximately
0.00000558872972569691 nats per forecast, (4) is exactly 1/178398,
and (5) is bounded by 1/500000. These are expected excess losses under
calibration. They do not say that an individual rounded forecast cannot
score better against its realized target or against the hidden teacher.

## 3. Predictable inclusion, and the limit of that guarantee

For a finite horizon, let A_t>=0 be F_t-measurable and integrable. It may
indicate that the process is still active and a forecast has passed all
pre-target checks. Define q_t=p_t outside the included domain if necessary.
Multiplying (2)--(3) by A_t and taking expectations yields

    0 <= E sum_t A_t [ell(q_t,Y_t)-ell(p_t,Y_t)]
      <= Psi(a,delta) E sum_t A_t.                              (6)

The Brier version has upper constant 2 delta^2. A fixed horizon average
and, when its denominator is positive, the ratio of these expectations
inherit the bound. No general conclusion follows for the expectation of
the ratio with a random future-dependent denominator. Nor can a whole-run
completion event, which may depend on later targets, be used as A_t for
earlier forecasts. Post-target observation/commit acceptance can also
depend on Y_t. The theorem uses the actual causal cut, not a retrospective
label of a successful record.

For the experiment's expected score against the hidden teacher, let R_t
be its conditional noisy-label probability, either 1/10 or 9/10. The score
is CE(R_t,q_t). Since E[R_t | F_t]=p_t, equations (2) and (6) also hold
after averaging this metric over the declared teacher and history law.
They need not survive conditioning on later completion.

The exact effect of selection is visible without an asymptotic argument.
At a fixed pre-target history, let r=E[R_t | F_t,C] for any later event C
of positive conditional probability. Keeping the original p and q fixed,

    CE(r,q)-CE(r,p)
      = D(Ber(p)||Ber(q))
        +(r-p) log(p(1-q)/(q(1-p))).

The calibration term is quadratic in a small probability error, while the
selection term can have either sign and is first order. Updating the law
used to score a forecast does not retrospectively update that forecast.
This is the same need to respect the declared information cut as in the
[persistence filtration result](PERSISTENCE_FILTRATION_GEOMETRY.md).
The premise here is exact posterior calibration conditional on the current
query; it neither changes nor follows from the weaker registered persistence
mean-null before the next query.

## 4. An owned FP resource-selection counterexample

Start the ordinary n3 Reference Runtime from its uniform initialization,
empty Compiler policy, and the registered carry-free decoder with span
cap5, live-cell cap64 and arithmetic cap512. Commit these five real events:

    (0,1,0), (0,2,0), (0,2,0), (1,2,1), (1,2,1).

The complete signed count vector, ordered as (0,1),(0,2),(1,2), is
(1,2,-2), with cursor and optimizer steps both5. At the next query (0,1),
the native and registered exact-RNE proper forecasts are

    p = 15129/20050,
    q = 3164991/4194304,
    q-p = 1222167/42047897600 > 0.

All seven prediction words, the exact bridge check and the owned paths are
retained in [the compact CPU evidence](../../evidence/minimal/FP_PREDICTABLE_SCORE_TRANSFER.json).
The forecast precedes the target. Its two possible next states are:

| Scored target | Complete next counts | Span | Next query (0,1) |
|---|---|---:|---|
|0|(2,2,-2)|6|UNRESOLVED at cursor6, next target unrevealed|
|1|(0,2,-2)|4|forecast succeeds; either suffix target commits and seals at cursor7|

Thus whole-stream completion C occurs exactly when the scored target is1,
irrespective of the final target. The span refusal is legitimate for this
registered class. It is neither an all-decoder impossibility nor a new
semantic action. Both successful suffixes and the refused path are tested
through owned Reference ingress and observation.

Before the scored target, expected log excess is positive:

    D(Ber(p)||Ber(q)) = 2.28102918249523... * 10^-9.

Conditioned on completion, the scored observed target is1 and its loss
difference is instead log(p/q)=-0.00003851962555828.... This also reverses
the *hidden-noise expected* score used by the model report, not just the
realized-target metric. The posterior mean of the hidden-noise probability
conditional on C is

    r = E[R | F,C] = 2961/3362.

Consequently the selected hidden-noise CE gap equals

    r log(p/q)+(1-r) log((1-p)/(1-q))
      = -0.00001979921154401....

Its Brier gap is also strictly negative:

    2(q-p)^2+4(q-p)(p-r)
      = -21794738315218737759/1486025594613562081280000.

This falsifies an extension of predictable Bayes-regret nonnegativity to
later-completed runs. It does not falsify proper scoring or an existing
Runtime certificate. The model protocol already retains refusals and
makes no population-superiority claim. All attempts, including incomplete
ones, must remain visible when interpreting completion-conditioned scores.

## 5. An ideal-law quality prediction for the band experiment

Here is a population statement independent of its two fixed model tapes.
Assume independent uniform hidden bits, independent noise with flip
probability1/10, two training observations of each adjacent chain edge,
and both orientations of each distance-two pair evaluated once. The query
order is independent of hidden bits and target noise. Learning continues
after every forecast. The argument applies for every n>=3.

With an anchored initial bit, adjacent edge parity bits are independent
uniform bits: the map from the remaining vertex bits is a bijection.
Two training labels on one edge agree with probability41/50. In that case
the posterior parity reliability has magnitude40/41; if they conflict,
it is zero. For a distance-two parity, both edges are informative with
probability

    u = (41/50)^2 = 1681/2500.

The next noisy-label probability is then a_* or 1-a_*, where
a_*=2961/3362; otherwise it is1/2. Write h for binary entropy in nats.
The Bayes risk using only those four local training labels is

    L0 = u h(a_*)+(1-u) log 2
       = 0.47282139469214924246....

After also observing one noisy label for the same distance-two parity,
the coarse Bayes risk for the reverse orientation is

    L1 = u [a_* h((9/100)/a_*)
            +(1-a_*) h((9/100)/(1-a_*))]
         +(1-u) h(9/50)
       = 0.39446730456134185690....

Indeed P(Y1=1,Y2=0)=P(Y1=0,Y2=1)=9/100 for two independent noisy
observations of a common hidden parity, regardless of its posterior.
Conditioning on Y1 gives the two entropy arguments above.

The full joint posterior has at least this information at the first and
second orientations respectively. Conditional entropy decreases with more
information *in expectation*, so its expected initial-training-unseen CE
is at most

    (L0+L1)/2 = 0.43364434962674554968....                        (7)

The independent-pair Bayesian ablation ignores the neighboring labels.
For an initially unobserved pair it predicts1/2 on its first orientation
and uses its one own-pair label on its second. Its exact ideal-law mean is

    (log 2+h(9/50))/2 = 0.58227033368501973998....                (8)

Thus the full joint model's expected advantage over that ablation is at
least0.14862598405827419030... nats per initially unseen query. Additional
evaluation information may improve the full joint risk in expectation;
no pointwise monotonicity or superiority over the exact joint control is
claimed. The hidden-noise expected metric has the same population mean
by conditional expectation.

A complete, causally measurable approximate forecast rule satisfying (1)
adds at most Psi to (7). This statement does not condition on later Runtime
completion, or turn two fixed seeds into a population test. Host, time,
retention and conformance obligations still determine whether the actual
registered matrix completes.

## 6. Minimal evidence and scope

The CPU artifact records189 probability-grid checks of (3)--(5), all16
local four-label training patterns and32 next-label branches with exact
rational weights, and70-digit Decimal evaluations of the log/entropy
expressions. The exact probability of the informative case is1681/2500;
the enumerated risks agree with the formulas. The three real Reference
paths establish the selection event, and the passive physical schedule
supplies the rounded forecast and its accepted bridge relation.

The decimals are high-precision numerical checks, not directed-rounding
enclosures or proofs by enumeration. No actual device execution is
claimed for this counterexample. This result neither reruns nor modifies
the six registered model jobs and issues no CERTIFIED_COMPLETE claim.

Reproduce with `python -X utf8 -B theory/numerical_checks/audit_predictable_score_transfer.py`.
The default mode checks the retained artifact without overwriting it;
`--output PATH` only creates a new file.

## 7. Exact discrepancy intervals from retained hardware readouts

Let p be the exact native label-zero probability and q the exact proper
normalization of the two retained binary32 masses. For any p,q in(0,1),
put e=q-p and r(t)=p+t*e. Differentiating binary KL in its second argument
and integrating from p gives

    KL(p||q) = e^2 integral_0^1 t/[r(t)(1-r(t))] dt.

Let m and M be the minimum and maximum of r(1-r) on the interval between
p and q. Concavity gives m=min(p(1-p),q(1-q)). The maximum is1/4 if the
interval contains1/2, otherwise max(p(1-p),q(1-q)). Consequently

    e^2/(2M) <= KL(p||q) <= e^2/(2m).                         (9)

Every quantity in(9) is rational for retained binary32 masses and the exact
count posterior. This gives an enclosure without evaluating a logarithm or
subtracting nearly equal signed log terms. The interior maximum matters:
using only endpoint maxima at p=2/5,q=3/5 gives a false lower bound.
The two-coordinate conditional Brier excess remains exactly2e^2.

If both p and q lie in[a,1-a], (9) also gives

    KL(p||q) <= (p-q)^2/[2a(1-a)].                            (10)

This is a smaller hypothesis class than the sharp error-only bound(3),
which allows q outside the native interval. In the current binary readout,
stored masses in[1,9] imply their **proper** probabilities lie in[1/10,9/10].
The retained reader checks that range explicitly. It does not silently
substitute independently rounded division words for a proper distribution.

`scripts/audit_retained_partition_risk.py` reconstructs each native forecast
with the independent vertex-prefix posterior, using only earlier labels.
For each retained four-word output it checks exact probability discrepancies
and encloses(9) and2e^2 on an outward96-bit rational grid. Average intervals
are obtained by adding their integer endpoints and dividing by the exact
number of contexts. Decimal arithmetic is used only for twelve separate
checks of the interval formula, including the interior-maximum case; it
does not determine the reported model KL enclosures.

These are deterministic audits of completed, exposed evaluation paths.
Their means are not population estimates or guarantees obtained by
conditioning on future completion. Fixed-hidden-teacher CE differences
still contain the signed first-order term in section3, while reference-to-
proper-AMP KL is nonnegative. A better uniform error upper or fewer floating
operations does not imply a smaller realized discrepancy on every tape.
