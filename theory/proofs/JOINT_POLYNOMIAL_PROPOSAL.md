# Native joint polynomial proposals without a shared output gate

Status: **scoped construction proof, exact audit and functional CPU/CUDA
endpoints; complete source-bound matrices pending**. This is a separately
registered solver over the existing native grammar, initializer/profile
paths and complete Runtime. Foundation R4 and ERC-1 do not change. RN-4's
committed outcomes and resource settings are not rerun or relabelled.

## 1. Remove the gate by changing the construction, not an existing learner

The earlier [curvature control](TRANSITIVE_UNCERTAINTY_LEARNING.md) uses a
shared output multiplier k. Its derivative vanishes at the two initially
neutral forecast cuts, but can be nonzero later. Removing k from a running
learner is therefore not a valid full-state quotient or evidence transfer.
After two matching labels in the n3 grid16/rate1 control, the old and new
next probabilities are respectively
605786986482207/777750761524495 and 17712419905/22813333329. Both initial
predictions were uniform; the complete learners diverge.

A new constructor can avoid that multiplier from the start. Retain the
empirical majority components and representative within-component parities
h. For c>1 components enumerate every relative orientation, fixing only the
redundant global flip in this explicit parity-value constructor. There are
`K=2^(c-1)` orientation members. This is not a quotient of complete Runtime
states, nor a latent-certainty statement about finite IID observations.

For each ordered pair form the native feature `F_ij=X_0i*X_1j`. Within an
empirical component, attach it to its representative parity head using the
separate initialized scale t. Across components, for each orientation H and
head y, let G_Hy be the sum of features whose parity under H is y.

The desired excess on a cross query is

`E_y = SUM_H (a_H+a_H^2) * G_Hy`.

Emit its linear terms directly into the final head, each with slot a_H.
Create an inner SUM with exactly the same weighted feature terms, then
attach that SUM to the head with the **same** slot a_H. This gives the
quadratic term. There is no common output slot and no assumed fixed unit.
Empty parity rows are identically zero, including all parameter derivatives,
and emit neither a SUM nor a head edge.

This identity holds for nonnegative soft sources too: it is phi(a)*G,
not the earlier square-of-G construction's one-hot-only identity. No
full-state equivalence with that older graph is asserted. The actual
parameter curvature arises from shared weights along serial SUM edges;
extra self-PRODUCT nodes are unnecessary. Native PRODUCT count and
polynomial degree in learned parameters are different quantities.

## 2. Learnable uncertainty and an actual recovery direction

Initialize every a_H at an available unit, separately from t. On a one-hot
cross query, half of the orientation members predict either parity. With
phi(a)=a+a^2, each head has mass1+K and its prediction is1/2. Within-component
predictions retain `(1+t)/(2+t)` toward the representative parity. These
initialized probabilities equal v3/v4 on the one-hot domain; their masses,
parameters, costs and complete learners differ.

At such a cross initialization, the derivative in a matching orientation
slot is `-3/(2*(1+K))`; the opposite target reverses the sign. For three
components and exact unrounded rate eta, the two-neutral-label path formula
from the earlier mixed-polynomial control still holds: with
`u=3*eta/10`, `v=eta/(10+4*u^2)`, the next matching endpoint probability is

`1/2 + 24*u*v / (2+4*(2+u^2+9*v^2+4*u^2*v^2))`.

The old k remains1 at these two cuts, explaining this scoped equality. It
must not be extended to later arbitrary histories. The complete native
endpoint at rate1/grid16 forecasts25981558417/45993308790 on the previously
unqueried component pair after those two labels, before receiving its label.

At a zero orientation amplitude on a one-hot query agreeing with that
orientation, the derivative is

`1/T - 1/M_target < 0`,

because the other head has positive base one. There is no common gate whose
zero can kill this direction. Exact unrounded positive-rate coordinate SGD
therefore revives that zero amplitude. Projection and finite grids must
still be checked, and a range/resource refusal can stop the continuation.
This is a local recovery property, not strict positivity of all weights,
a Bayesian update, a global convergence theorem or guaranteed good risk.
The owned rate4 control actually reaches two zero amplitudes after one label
and revives both after the opposite next label.

The constructor still uses empirical within-component signs. Incorrect IID
majorities can leave the true within-component relation outside this emitted
family; all original observations and other native programs remain retained
by Runtime. The solver does not certify latent recovery or discard those
alternatives from the full class. Strong adaptive controls remain necessary.

## 3. Reachable coefficients, literal costs and paid work

Register `empirical-binary-relation-joint-polynomial-v5` in the existing
relation-source coordinate. Default v3 and registered v4 keep their scopes.
No birth, merge, split, fitted coefficient or new semantic action is added.

The solver requires K distinct available unit slots plus a separate scale,
including every intervening initializer coordinate. Scale feasibility is
checked before exact likelihood comparison. A unit-valued scale itself
consumes a unit; it cannot also serve as a supposedly independent orientation
amplitude. The count/slot audit retains cases where an otherwise best scale
is infeasible but another available scalar is feasible.

If the available unit count cannot cover K, refuse before materializing the
exponential family or allocating a large shifted integer. A connected
component has no cross pairs and needs neither orientation slots nor their
SUMs. All other skipped alternatives remain in the full native class.

Let `W=SUM_C |C|^2`, `X=n^2-W`, and let q be the number of nonempty orientation/
parity rows. For c>1, `K<=q<=2K`. The emitted witness has

`nodes=2n+n^2+q+2`, `SUMs=q+2`, `PRODUCTs=n^2`,
`edges=2n^2+2*K*X+q+W`.

The same formula uses K=q=0 when c=1. Actual slot count is the highest used
initializer index plus one. These are literal witness costs, not a resource
lower law or a new static special-case study. At n3 with three singleton
components, the graph uses24 nodes,9 SUMs,9 PRODUCTs,76 edges and5 slots.
The previous mixed control used33 nodes,10 SUMs,17 PRODUCTs,77 edges and6
slots. No architectural optimum follows from this comparison.

Runtime prepays an additional `64*n^2*(1+U)` declared reference work, where
U is the length of the grammar-limited initializer prefix. This constant-time
metadata bound is computed before scanning or copying coefficient values. K
cannot exceed U on a successful proposal. Source/data scans and
scale comparison retain their existing allowance; actual construction,
profile, ownership and storage have separate charges. This is the registered
reference work metric, not elapsed bit-time or total host cost. Refusing
that prepayment cannot publish a proposal, spend alpha or issue a class bound.

A separate all-categorical empirical upper remains authoritative. The
proposal's signs and likelihood never exclude unsearched programs. Its
historical bound, when attained, concerns fixed-state empirical CE over the
full registered native grammar and initializer/profile endpoints plus the
actual baseline. Fresh installation can also occur from an unresolved class;
it binds the actually constructed continuous reference/AMP learners.

## 4. Numerical and range refusals remain distinct

Native mass growth changes the scale of absolute rounding error. The n6
transitive fixture under the previous state/native/normalizer tolerance1/100
refuses a CUDA prediction at cursor57, after a prior legitimate installation.
The CPU path completes. The failed prediction retains all its actual words;
its current target is not revealed and the failed phase receives no prefix
acceptance. The old installation and spent evidence remain historical facts.

Positive CUDA fixtures separately declare state/native/normalizer
tolerance1/16 and retain probability tolerance1/100. Every phase checks
these independently and reports measured errors. This is an explicit
per-run numerical contract, not a change to rounding or acceptance semantics.
The original1/100 refusal remains an independent control; it is not relabelled
a pass. No new model result or suitable future-model tolerance follows.

The old normalizer18 cap also has a concrete refusal. Four singleton
components have K8 and initialized cross normalizer18. At exact unrounded
rate1 the first neutral label raises it to164/9. The registered grid16
endpoint likewise exceeds18 and refuses publication of its staged update.
Other functional endpoints declare normalizer64 and activation64 before
execution. No failed case has its cap raised retrospectively.

The binary64 auditor now reads an owned pending pre-target record when a
refused prediction has executed CPU phases before entering the revealed
observation sequence. Its original full regression passes. The numerical
refusal control independently replays every actual CUDA word, including the
last completed but rejected prediction, checks its retained frame, verifies
the error against the original budget, and confirms no prefix accepts it.
This does not authorize replay of a frame-exhausted/incompletely retained
phase such as RN-4's n16 failures.

## 5. Current evidence boundary

`scripts/audit_joint_polynomial.py --exact` checks320 models,7,320 initial
predictions,25,752 independent gradient coordinates,946 zero-coordinate
recovery directions,726 coupled count/slot cases and729 soft-input polynomial
values. A counterexample distinguishes the old and new complete learners.
The existing v4 exact audit continues to pass.

The functional CPU and actual RTX3090 transitive endpoints each check542
binary64 phases; the target endpoint checks542 CUDA phases and performs
fresh installation. The CPU rate4 recovery and normalizer18 refusal controls
also pass. The complete source-bound matrices follow the committed solver:
transitive/opposite/incomplete-class installation, reachable zero recovery,
slot/work refusal, tight-range refusal and the extra CUDA precision refusal.
They do not replace the frozen31-script baseline or imply an RN-5 model result.
