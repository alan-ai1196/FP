# Conditional deployment delay on the retained likelihood tapes

Status: **PROVED CONDITIONAL ENVELOPE; EXACT RETROSPECTIVE AUDIT**. The actual
likelihood matrix is still separate execution evidence. This analysis reads
the retained evaluation labels to predict what its original persistence rule
permits **if the required owned computations succeed**. It neither fills a
failed worker's scores nor supplies a new prospective probability statement.
No worker, baseline, bet, budget, learner or Runtime code changes here.

The question is whether removing the candidate's learning error also removes
the deployment problem. For the first n8 case the answer is already negative
under the registered rule: even an exact posterior must wait54 fresh events,
and every successful AMP realization satisfying the registered probability
relation leaves only9 or10 forecasts after paired crossing.

## 1. Premises and information cuts

Use the four cases, ordered tapes and registration of the
[likelihood model protocol](../../experiments/joint_uncertainty/LIKELIHOOD_MODEL_PROTOCOL.md)
at86083a0. The fair-prior candidate is constructed and profiled through the
actual unit-rate simplex learner. Its exact pre-target predictions equal the
adaptive known-noise posterior by the [complete phase theorem](COUNT_LEARNER_ENCODING.md).
Both fresh identities start at the training cutoff. The baseline remains
uniform; each identity has alpha1/4, coefficient(3/4)/6=1/8, the production
12-term lower log and a16-bit downward wealth grid.

Let p_t be the exact reference probability assigned to the actual next label,
and let q_t be its actual CUDA **proper stored-mass probability**. The
successful bridge requires |q_t-p_t|<=eta=1/1000, with p_t in[1/10,9/10].
Raw floating division is a separately checked value and is not substituted
for q_t. All source, profile, current-state, fresh-admission, resource and
lineage premises remain necessary; a numerical tube does not establish them.

These are deterministic statements about fixed retained tapes and all
allowed probability perturbations. They make no assumption that the
perturbations are independent, attain all endpoints, or constitute actual
GPU executions. The four tapes were already used in RN-5; their later labels
are explicitly read here, unlike the profile-only
[fresh-power theorem](LIKELIHOOD_PERSISTENCE_POWER.md).

## 2. Enclose the actual first crossings

Write L(x),U(x) for the production12-term enclosure of log(x). Throughout
x in[99/500,901/500], the proof in the fresh-power theorem gives width at most

`omega = 8*(1/3)^25 / [25*(1-1/9)] = 1/2353579470675`.

For the actual lower score ell_t=L(2q_t), define

`ell_t^- = L(2*(p_t-eta)) - omega`,

`ell_t^+ = U(2*(p_t+eta))`.

Then ell_t^- <= ell_t <= ell_t^+. This uses monotonicity of the true log
and the proved enclosure width; it does **not** assume that evaluating an
enclosure's lower endpoint at a larger argument supplies an upper bound.
Every factor1+ell/8 in these bounds is positive.

Set delta=2^-16 and F(r,ell)=delta*floor(r*(1+ell/8)/delta). For nonnegative
r and positive factors, F is increasing in both arguments. Starting all
three wealth paths at1 and iterating the same actual grid therefore gives

`R_t^- <= R_t <= R_t^+`

through every still-live prefix. Calculations may be continued passively
after a bound crosses; this does not continue or reset an actual crossed
identity. If c^+ is the first upper-envelope crossing of4 and c^- the first
lower-envelope crossing, then c^+ <= c_CUDA <= c^- whenever c^- is finite.
The exact reference first crossing c_ref is independently reconstructed
with its **actual production lower scores**. Thus the paired crossing lies in

`[max(c_ref,c^+), max(c_ref,c^-)]`.                         (1)

None of these times establishes installation. For the fixed registered
policy, an installation that passes its remaining ordinary gates occurs
at paired crossing. The score calculation below is conditional on that
installation and the required subsequent predictions completing. A failed
gate, missing identity, halt or killed worker has no score inferred here.

## 3. Enclose risk and isolate the cost of waiting

For each query, let p denote its exact probability of label0 and let a be
the true conditional probability of label0 (1/10 or9/10). The registered
descriptive expected CE is

`C_a(q) = -a*log(q) - (1-a)*log(1-q)`.

On q in[p-eta,p+eta], convexity puts its maximum at an endpoint and its
minimum at a clipped to that interval. Exact log enclosures therefore bound
each query's actual proper-mass CE. Sum these intervals over the registered
unseen or full-domain subset, with outward rational rounding.

For an install cursor I, deployment uses uniform probabilities on exactly
the queries whose **pre-target** cursor is less than I. Both forecasts use
the same continuing candidate after I. Their exact risk difference is

`CE_deployed - CE_same_candidate`

`= (1/|S|) * SUM_(t in S, cursor_t<I) [log(2)-C_(a_t)(q_t)]`. (2)

This cancellation avoids counting later AMP error twice. Enumerate the
integer interval in(1) to enclose both the deployed CE and(2). No monotonic
risk improvement from earlier installation is assumed: a candidate can
have larger true risk than uniform at individual queries. These are outer
envelopes, not claims that every cursor/risk endpoint is jointly realizable.

## 4. Retained-tape conclusions

All bounds below are rounded outward. Cursors are ordinary cuts, so a
crossing at114 after a60-event profile has consumed54 of64 fresh events.
The reference candidate CE is the same exact posterior as the retained
strong control; no baseline worker is rerun.

| n8 profile | Paired crossing cursor | Forecasts remaining | Conditional deployed unseen CE | Waiting cost in unseen CE, lower bound |
|---|---:|---:|---:|---:|
| c2, seed16 | 114-115 | 9-10 | [0.659686,0.668053] | 0.316620 |
| c2, seed17 | 90 | 34 | [0.500749,0.500753] | 0.166668 |
| c4, seed18 | 72 | 32 | [0.501447,0.501450] | 0.120500 |
| c4, seed19 | 72 | 32 | [0.516783,0.516786] | 0.166420 |

For comparison, the first case's exact candidate unseen CE is approximately
0.342961. Its allowed AMP candidate CE lies in[0.342861,0.343067]. The much
larger waiting penalty cannot be explained by that probability tolerance or
removed solely by making this candidate's posterior learning more accurate.
The original bound6 persistence rule still decides when useful predictions
can enter deployment. This is a limitation of this registered procedure on
these retained tapes, not a lower bound for every legal FP evidence strategy.

Actual execution remains a separate research test. A completed source-bound
worker should be checked against these conditional envelopes. A failure
does not violate a premise-qualified implication, prove physical success,
or acquire its hypothetical candidate/deployed scores. The matrix, earlier
failed attempt and original strong controls retain their own statuses.

## 5. Exact audit

Run `python -B experiments/joint_uncertainty/likelihood_deployment_envelope.py --write`.
The [small retained record](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_ENVELOPE.json)
contains scalar envelopes and verification counts, not world weights,
evaluation tapes, GPU words or new model-result rows.

The audit checks63 native pre-target prefixes and126 complete native units,
including self-queries and queries selected from earlier labels. It explores
all46,656 six-event label/proper-forecast paths with three perturbations per
cut and checks55,986 applications of the actual wealth helper against the
independent floor recurrence and its lower/upper envelopes. Four out-of-scope
reference probabilities are refused. This finite exploration supports the
analytic induction; it does not discretize the theorem's full allowed tube.

The four retained n8 trajectories use256 exact pre-target posterior
forecasts. Their eight exact reference CE intervals agree with the retained
binary64 control scores to the declared comparison allowance. In total1,975
exact log enclosures are independently verified; the checker needs at most
32 series terms and16,061-bit operands. Risk intervals use outward96-bit
rational arithmetic; the compact record rounds them outward to40 bits.
No Torch import, GPU phase, model worker or baseline rerun occurs.
