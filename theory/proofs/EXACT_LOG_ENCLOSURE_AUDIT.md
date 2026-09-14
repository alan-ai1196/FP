# An independent exact log audit replaces the fixed Decimal comparison

Status: **PROVED SCALAR VERIFIER; EXACT ADVERSARIAL AUDIT; ORIGINAL GPU
ATTEMPT RETAINED AS FAILED**. Runtime's log calculation, U, persistence
rule and numerical tolerances are unchanged. This repairs an independent
auditor, not Foundation R4 or ERC-1.

## 1. The actual obstruction

The first n8 likelihood worker at90f3883 exits1 inside the inherited
`audit_reference_persistence.check_gain`. Its100-digit Decimal comparison
asserts that a Decimal logarithm lies between Decimal conversions of two
exact rational endpoints. The driver stops before the other three workers.
The [original journal](../../evidence/minimal/FP_LIKELIHOOD_MODEL_AUDITOR_FAILURE.json)
retains the job and traceback: no timeout, attachment before execution and
peak commitment15,474,765,824 bytes within the original16GiB cap. It contains
no valid model score, installation, seal or complete independent phase count.

There are two distinct defects in the scalar comparison. Rounding a rational
probability before taking its log can perturb the result outside a much
narrower correct interval. Conversely, rounding both claimed endpoints can
collapse an incorrect interval to the same Decimal value as the check.
Increasing a fixed digit constant does not make this an exact verifier.

The exact posterior reconstruction for the first registered case at cursor65
and label0 gives candidate probability

`1436234048776862726818201 / 2872468070873849901111602`

against baseline1/2. Runtime's12-term rational interval is correct; the old
100-digit check rejects it. The new checker proves it in16 terms, using at
most2674-bit operands. The original failed job did not retain the offending
event, so this reproduction is not a recovered CUDA record or new model score.

For the opposite failure, set the claimed interval for log(3/2) to a single
rational point equal to its100-digit Decimal approximation. The old checker
accepts this zero-width claim. The independent exact enclosure is disjoint
from it and rejects it. This supplies a finite rational counterexample;
no assumption about an uncomputed transcendental endpoint is needed.

## 2. Independent rational construction

For a positive rational x, write `x=2^e r` with
`3/4 <= r < 3/2`. This differs from the producer's residual in[1,2).
For any positive v, let `z=(v-1)/(v+1)`. Then

`log(v)=2 SUM_(j>=0) z^(2j+1)/(2j+1)`.

For N terms, all remaining terms have the sign of z and their absolute sum
is at most

`2 |z|^(2N+1) / ((2N+1)(1-z^2))`.

This follows by bounding each remaining denominator below by2N+1 and
summing the geometric tail. It yields rational lower and upper bounds for
both signs of z. For the residual above, |z|<=1/5.

The independent checker obtains log2 as

`log(3/2)+log(4/3)`,

using z=1/5 and1/7. The producer instead uses z=1/3 directly. Signed interval
multiplication by e and addition of the residual enclosure give a proved
interval J for log(x). The implementation neither calls the production
`log_enclosure` function nor compares rounded decimal endpoints.

## 3. Exact decision scope and finite budgets

The inputs are positive rational numerator/denominator and a claimed rational
interval I=[L,U]. The checker has three outcomes:

* If its proved interval J is contained in I, it returns scalar audit metadata.
  This proves `log(numerator/denominator) in I`.
* If J and I are disjoint, it rejects the claim.
* If they overlap without containment, it increases N from8 through16,32,64
  and128. Inconclusive refinement or an arithmetic allowance failure raises
  `LogAuditUnresolved`, never a successful comparison.

The exact ratio one is handled as log1=0. Reversed intervals and invalid
positive/type premises are rejected. All rationals are exact Fractions;
operand sizes and conservative cross-product/shift sizes are checked before
the corresponding arithmetic. Defaults are128 series terms and262,144 bits
for operands/preflights. These bound the passive auditor. They do not raise
Runtime's32768-bit allowance or any worker's host/time cap.

The returned record attests only to this scalar containment. It is not a
complete decision procedure for arbitrary rational intervals at these finite
budgets. Nor does it attest that the supplied probabilities belong to a
current candidate/base pair, actual pre-target forecasts or fresh labels.
The existing Runtime and surrounding independent trajectory auditor retain
those lineage, source, wealth, alpha, bridge and installation checks.

## 4. Evidence

Run `python -B scripts/audit_log_enclosures.py --write`. The
[minimal audit](../../evidence/minimal/FP_EXACT_LOG_AUDIT.json) retains:

* 1024 positive rational grid/producer-term checks,14 near-one cases and21
  power-of-two scale cases;
* the concrete correct-interval false rejection and wrong-interval false
  acceptance of the old checker;
* 512 label checks from the four retained n8 exact posterior trajectories,
  without executing or rescoring a model worker;
* five rejection/budget checks, including an inconclusive series budget and
  a refused integer operation allowance.

All1572 valid intervals pass; accepted cases use at most32 terms and8103-bit
operands. Legacy false rejections include actual-target reference forecasts
at case0/cursor65 and case2/cursor50. Those are passive reproductions, not
additional failed GPU attempts or recovered installation records.

Full reference persistence, paired CPU persistence and owned compiler policy
regressions pass with the new checker. The last includes all64 six-label
streams and256 independent gain/wealth checks, yielding32 baseline,30
unresolved and2 installed CPU outcomes. The [bounded development CUDA regression](../../evidence/minimal/FP_EXACT_LOG_CUDA_REGRESSION.json) seals
and installs at cursor22, independently checking286 CUDA and286 binary64
phases and40 fresh scores. It is a small regression, not a replacement n8
outcome or a new complete release. Original source-bound results remain tied
to their original code.

## 5. Corrected model execution

The [protocol correction](../../experiments/joint_uncertainty/LIKELIHOOD_MODEL_PROTOCOL.md#auditor-correction-after-the-original-stopped-attempt)
registers a new immutable execution source after this verifier is committed
and tested. Before launching a corrected worker, the driver requires the
entire original model/resource registration dictionary to be identical.
It links the separately retained original failure in the new journal.

The four cases, original order, data, Gamma/U, native graph class, profile,
baseline references, bound6/bet3/4, alpha, all numerical tolerances and fixed
16GiB/two-hour envelope stay unchanged. The old failed attempt is never
converted to a successful run. The new jobs must earn every reported model,
phase, freshness and installation result under their own actual execution.
