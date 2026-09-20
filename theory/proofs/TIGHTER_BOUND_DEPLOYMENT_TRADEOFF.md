# A tighter gain bound can delay deployment

Status: **EXACT COUNTEREXAMPLE TO RECIPROCAL-POWER TRANSFER; CONDITIONAL
RETAINED-TAPE CROSSING AND RISK PREDICTIONS**. The four-case experiment is
already fixed at `8ccacc0`. This analysis reads its previously exposed tapes
while the first job runs; it chooses no new rule and reports no new GPU result.

The owned mass-box proof solves a validity/admission problem. Keeping the
registered fraction at3/4 while changing B from6 to13/8 also increases the
actual linear coefficient from1/8 to6/13. Soundness allows that change, but
does not imply earlier crossing. Stronger bounds enlarge the allowed set of
coefficients; they do not force the learner to spend more wealth on each gain.

## 1. A precise limit of the previous power proof

For a binary correct-posterior candidate p against uniform, take p>1/2 and
write a=log(2p)>0, b=log(2(1-p))<0 and mu=p*a+(1-p)*b. For a positive
coefficient c with both factors positive, direct algebra gives

`E_p[1/(1+c*g)] - 1 = c*(c*(-a*b)-mu) / ((1+c*a)*(1+c*b))`.

Consequently the ideal reciprocal contracts **if and only if**

`c <= mu/(-a*b)`.

This criterion concerns the correct-posterior alternative used for power.
The gain-mean null and its forward nonnegative-supermartingale validity are
different statements; neither validity nor the mass-box proof fails here.

At p=9/10, the native n2 learner's self-query at Gamma realizes exactly this
distribution. Independent rational log bounds give:

| Coefficient | Ideal expected reciprocal factor | Ideal expected log factor |
|---|---:|---:|
| 1/8 | 0.963584567 | 0.041347616 |
| 6/13 | 1.096773410 | 0.080229264 |

The new expected reciprocal is strictly above109/100, although its expected
log growth is larger. The production lower log and downward wealth grid
make wealth no larger than ideal, so its expected reciprocal also exceeds1.
Both production one-step outcomes are checked exactly. The reciprocal
supermartingale in the [old finite-power proof](LIKELIHOOD_PERSISTENCE_POWER.md)
therefore cannot simply be reused for the newly registered coefficient,
even with a correct native posterior. This counterexample does not disprove
every possible finite-power bound or assert worse population power.

## 2. Apply the existing conditional envelope to the fixed new rule

Keep all premises of the [retained-tape envelope](LIKELIHOOD_DEPLOYMENT_ENVELOPE.md):
the exact continuing posterior p_t, CUDA proper-mass error at most1/1000,
12-term production log, downward grid16, alpha1/4 per path, successful owned
admission, required computations and ordinary installation gates. The tighter
procedure additionally requires each current-state proof refresh and owned
crossing retention to succeed. None of these are inferred from scalar wealth.

The existing production-score tube is still valid:

`L(2*(p_t-eta))-omega <= L(2*q_t) <= U(2*(p_t+eta))`,

where eta=1/1000 and omega=1/2353579470675. Replace the coefficient in the
wealth recurrence by6/13. Every bounding factor remains positive, so the
same monotone induction encloses wealth and first crossings. Stop each
passive path at its own first crossing. Reconstruct the exact reference
prefix separately and take the later reference/CUDA crossing. No lower
log endpoint is used as an upper bound and no grid error is ignored.

The paired cursor is unique on each of these tapes even after allowing every
permitted AMP probability perturbation. With the remaining install gates
and later predictions successful, the conditional unseen CE is:

| Case | Retained B6 install | New paired cursor | Fresh wait / remaining forecasts | Conditional deployed CE |
|---|---:|---:|---:|---:|
| c2, seed16 | 114 | 119 | 59 / 5 | [0.676416,0.676418] |
| c2, seed17 | 90 | 67 | 7 / 57 | [0.375273,0.375279] |
| c4, seed18 | 72 | 54 | 14 / 50 | [0.409450,0.409465] |
| c4, seed19 | 72 | 50 | 10 / 54 | [0.378767,0.378778] |

Displayed bounds are rounded outward. Full-domain and tighter rational
intervals are retained in the [minimal record](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_PREDICTION.json).

The first case's reference wealth reaches a minimum873/32768 at cursor84.
Rare adverse labels lose more wealth under the larger coefficient; its
later recovery does not cross until119. The new conditional unseen CE is
more than0.016 worse than the retained old deployed score, despite the same
exact posterior and the allowed small AMP error. This is a concrete failure
of pathwise earlier-deployment dominance on the already registered tapes.
The other three conditional crossings are earlier. Keep all four outcomes;
their differing behavior cannot be summarized as uniform improvement.

The score calculation uses convex binary CE envelopes and cancellation of
post-install candidate losses, exactly as in the earlier proof. Candidate
word equality across the actual old/new executions remains a separate test.
These fixed-tape calculations establish neither a prospective success rate
nor a new method selected using unseen data. A failed identity, retention,
install gate or physical job receives no hypothetical score from this table.

## 3. Reproducible exact audit

Run `python -B experiments/joint_uncertainty/likelihood_deployment_prediction.py --write`.
The script checks passive inputs against the registered8ccacc0 source and
retains all four original B6 outcomes exactly. It verifies the native
reciprocal witness,256 exact pre-target forecasts,90 actual production wealth
updates before the reference crossings, and1,964 independent rational log
enclosures. Accepted checks use at most32 terms and16,061-bit operands.
No Torch import, model worker, baseline rerun or new evidence identity occurs.

The correct next check is the fixed physical experiment, including its
possible failures. This analysis changes no running source, cap, rule or
selection. Foundation and ERC-1 remain frozen.
