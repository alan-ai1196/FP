# Persistence bets must respect the filtration of the null

Status: **PROVED, SCOPED; EXACT FINITE AND NATIVE FORECAST AUDITS**.
This investigates RN-5's deployment wait. It refutes a proposed shortcut,
not an issued Runtime certificate. Foundation R4, ERC-1, the registered
persistence nulls and both completed/running experiment contracts remain
unchanged. No context-dependent betting API is introduced.

## 1. The information cut that matters

For one-event epochs, write the paired log-loss gain as

`g_t(X,Y) = log(p_C,t(Y | X) / p_D,t(Y | X))`.

The [owned persistence contract](OWNED_REFERENCE_PERSISTENCE.md#2-the-actual-filtration-and-the-admitted-epoch)
conditions its mean-null on the complete history **before the next context**:

`E[g_t(X_t,Y_t) | F_(t-1)] <= 0`.

Here and below, the actual contract uses its prescribed range-safe score on
a failing attempt and zero after termination. It does not select a null
after learning which computations succeeded. The counterexample below has
no range failure, so its range-safe score equals the ordinary gain.

Sealing both forecasts before the target prevents target leakage. It does
not make a function of the new random context measurable before that
context. A bet selected after X is compatible with the different, stronger
null `E[g_t | F_(t-1), X_t] <= 0`. That condition excludes some laws admitted
by the registered pre-context null. It cannot be silently substituted to
justify faster evidence.

For example, choosing a smaller bound at an easy context can allocate more
wealth to contexts where the candidate improves, while allocating less to
contexts where it loses. A negative average gain then need not produce a
supermartingale. The schedule can be specified in advance and use no target;
the filtration still determines whether it is predictable for the claim.

## 2. A complete finite one-step validity criterion

At a fixed pre-context cut, let Omega be a finite legal outcome set. Scores
`g_omega` are fixed there and include at least one negative and one positive
value. The null family is every distribution r on Omega satisfying

`SUM r_omega g_omega <= 0`.

There is no extra restriction on the context marginal. Let e_omega be a
nonnegative proposed evidence factor. Then the following are equivalent:

1. `SUM r_omega e_omega <= 1` for every null distribution r.
2. There is **one common lambda >= 0** such that
   `e_omega <= 1 + lambda g_omega` for every legal outcome.

This characterizes validity, not just a sufficient family of bets. The
dominating line is automatically nonnegative, because e is nonnegative.
It need not satisfy Runtime's stricter bet/wealth representation bounds;
those remain separate physical and registration requirements.

**Proof.** The second statement gives the first by taking expectation.
For the converse, a point mass at any negative or zero score is a legal
null, so e<=1 there. Mix any positive-score outcome i and negative-score
outcome j with probabilities `-g_j/(g_i-g_j)` and `g_i/(g_i-g_j)`. This is
a zero-mean null. Validity on that mixture is exactly

`(e_i-1)/g_i <= (e_j-1)/g_j`.

Consequently the interval

`[max(0, max_(g_i>0) (e_i-1)/g_i), min_(g_j<0) (e_j-1)/g_j]`

is nonempty. Every lambda in it supplies the required domination, including
the already checked zero-score outcomes. This proves necessity using only
one- and two-outcome nulls. It is the elementary finite form of the usual
linear-program duality for a mean constraint. No signed native operation
or free supplied forecast table follows from this proof.

Applied conditionally at each pre-context cut, a predictable choice of such
a common line gives the existing nonnegative-supermartingale argument.
Lower log enclosures and downward wealth rounding preserve domination when
the coefficient is nonnegative. The complete lineage, alpha allocation,
failure stopping and physical ownership obligations are still needed.

## 3. Context-dependent linear bets cannot evade this condition

Suppose each active context x has both a positive and a negative possible
gain, and a proposed factor is `e(x,y)=1+lambda_x g(x,y)`, with nonnegative
factors and coefficients. Universal validity under the preceding mean-null
holds **if and only if every active context has the same coefficient**.

To see necessity, combine a positive outcome at x with a negative outcome
at z. The zero-mean mixture above requires lambda_x<=lambda_z. Reversing
their roles requires the opposite inequality. Sufficiency is the common
linear bet. An identically zero-gain context places no restriction because
its factor is always one.

Distinct strictly positive normalized candidate/base label distributions
have both signs: their ratios cannot all be above one or all below one.
Thus the condition applies directly to finite positive native forecasts at
every context where the two predictors differ.

More generally, every valid nonnegative factor is pointwise dominated by
one common linear bet in this finite mean-only model. Extra context weights
can help under additional restrictions, such as a declared context law or
a context-conditional null. Such information changes the null family and
must be part of the claim. Merely observing a context does not supply it.

## 4. A native log-loss counterexample with a full-support law

Use two complete one-hot contexts A and B, positive base (1,1), and one fixed
unit feature slot. The native candidate heads are

`M_0 = 1 + 8 x_A + 5 x_B`, `M_1 = 1 + 3 x_B`.

These are literal positive SUM incidences. The baseline has two empty
excess SUM heads and is uniform. Exact native evaluation gives

| Context | Candidate p(0), p(1) | Local absolute gain bound | Bet fraction | Coefficient |
|---|---|---:|---:|---:|
| A | 9/10, 1/10 | 2 | 3/4 | 3/8 |
| B | 3/5, 2/5 | 1/4 | 3/4 | 3 |

All four possible gains lie strictly within their listed local bounds.
Choose independent events with full-support joint probabilities

`P(A,0)=1/100, P(A,1)=11/100, P(B,0)=87/100, P(B,1)=1/100`.

The actual registered one-event learner at rate zero keeps both predictors
fixed while retaining and clearing gradients and advancing its clocks in the
ordinary way. No post-target reset supplies the construction. Exact rational
log enclosures establish

* mean true gain < 0, so the pre-context mean-null holds at every step;
* mean of the proposed context-weighted factor > 1;
* mean log factor > 1/4 and every log factor lies in (-2,2).

Thus its unrounded product crosses every finite threshold almost surely,
despite the null. There is also an explicit finite contradiction to alpha=1/4:
after 256 independent steps the log wealth has mean >64 and variance <1024.
Since log4<2, Chebyshev gives

`P(cross 4 by step 256) > 1 - 1024/62^2 = 705/961 > 1/4`.

This bound concerns the unrounded proposed process. The audit separately
calls the actual `next_wealth` helper at initial wealth one with each local
rule and grid16: its exact null-mean rounded first-step wealth is also >1.
It does not claim the same eventual-crossing law for repeated grid rounding.
The helper supplies arithmetic, not authority to choose an owned rule after
ingress. Runtime fixes the rule before the context and does not admit the
substitution, so this is not a current false persistence certificate.

The original common coefficient 1/8 has expected factor strictly below one
under this same law. The counterexample attacks the proposed shortcut rather
than the registered RN-5 evidence rule.

## 5. A legal bound improvement has to cover contexts before ingress

The separate owned likelihood learner suggests a valid direction that needs
no new evidence action. At all legal one-hot queries, its exact normalized
candidate probabilities remain in [1/10,9/10] under the registered unit
simplex update. Against the actual uniform baseline, a successful AMP mass
relation with probability error at most 1/1000 puts physical probabilities
in [99/1000,901/1000]. Monotonicity of log and exact endpoint enclosures give

`-13/8 < log(99/500) <= g_AMP <= log(901/500) < 13/8`.

This is a **common global bound**, derived from the bank and numerical
relation before a context. At bet fraction 3/4 it permits coefficient
6/13 in a future registration. Reference probabilities satisfy it too.
Every computed lower enclosure must still pass its bound check; failed
attempts must retain the existing predeclared range-safe stopping semantics.
Conditioning retrospectively on passed phases is not a validity argument.

The running n8 likelihood matrix keeps bound6 and coefficient1/8. No job is
patched or rerun, no counterfactual installation is recorded, and no power
ordering between the two coefficients is claimed. Larger bets can lose more
on adverse labels. Choosing a useful common predictable coefficient is a
statistical and resource question within the existing contract.

## 6. Evidence and relation to established statistics

Run `python -B experiments/joint_uncertainty/persistence_filtration.py --write`.
The [minimal report](../../evidence/minimal/FP_PERSISTENCE_FILTRATION_AUDIT.json)
retains the finite table/vertex counts, native forecasts, small outward exact
enclosures, actual grid16 first-step factors and global-bound witnesses.
The finite audit independently enumerates the null polytope's vertices and
compares its maximal expected factor with the domination criterion:27,725
factor tables,134,450 vertex expectations and5,890 valid tables. It also
checks256 two-context coefficient combinations and384 continuous native
units across all three-event words on the four outcomes. Log arithmetic is
exact rational, independently cross-checked with 160-digit Decimal; no GPU
or RN-5 target execution occurs.

General log-optimal e-variables and reverse information projection are
established statistical topics; see Larsson, Ramdas and Ruf,
[The numeraire e-variable and reverse information projection](https://arxiv.org/abs/2402.18810v4).
No novelty claim is made for mean-constraint duality or betting validity.
The contribution here is the explicit native counterexample, the exact
finite audit, and identifying which apparent deployment optimization would
change FP's registered null. The existing Foundation filtration survives
this attack; it prevents the invalid shortcut.
