# A simplex gradient law for positive affine readouts

Status: **PROVED, SCOPED; EXACT NATIVE-GRADIENT AUDIT**. The learner rule
below is not implemented by the current ReferenceCompilerRuntime. It is a
different U and initialization, not a change to the positive graph grammar
or a graph-only emergence result. No Runtime, class, installation or AMP
authority is obtained by the arithmetic audit.

## 1. Affine native readout and the declared weight state

Suppose a positive native Program has a selected parameter block
`w=(w_1,...,w_K)` on the probability simplex. Hold its other parameters fixed.
On every declared source context x its masses are affine in this block:

`M_y(x,w) = b_y + SUM_j w_j a_yj(x)`,

where b_y>0 and a_yj(x)>=0. Assume the complete coefficient columns have
equal totals, `SUM_y a_yj(x)=C(x)` for every j. Write B=SUM_y b_y. Then
`T(x,w)=B+C(x)` on the simplex, and the native conditional distribution is
the mixture with weights w of the fixed expert laws

`q_j(y|x) = (b_y+a_yj(x))/(B+C(x))`.

Affineness, column normalization, the selected block, its initialization and
the fixed remaining coordinates are substantive hypotheses. They are not
inferred from current forecast agreement or from arbitrary positive syntax.
They must hold on the complete declared source interface. No latent label,
posterior, signed statistic or hard constraint is supplied as a native source.

## 2. Derive the finite update from the actual native CE gradient

For one observed target y, let g_j be the ordinary ambient derivative of
`ell=log T-log M_y` computed by the native graph. Even though T is constant
on the simplex, its ambient derivative must not be erased:

`g_j = C/T - a_yj/M_y`.

Let `g_bar=SUM_j w_j g_j`. Consider the tangent update

`w_j' = w_j * [1 - eta*(g_j-g_bar)]`.

Substituting the native derivative gives

`g_j-g_bar = (SUM_i w_i a_yi-a_yj)/M_y`,

and hence, at eta=1,

`w_j' = w_j*(b_y+a_yj)/M_y = w_j*q_j(y|x)/SUM_i w_i q_i(y|x)`.

Thus the **unit step is exactly the Bayesian update**, rather than merely
its small-step approximation. Every positive weight stays positive and the
weights sum to one. No clipping, explicit renormalization, logarithm or
external posterior routine is needed in this exact gradient formula.
For 0<=eta<=1 the result is the convex combination of the old weights and
that posterior. Except at an uninformative observation, eta=1 is the unique
step size in this family that equals the full Bayesian update.

For positive weights, this direction is the negative gradient under the
categorical simplex metric `G_w(u,v)=SUM_j u_j*v_j/w_j` on zero-sum tangents.
Indeed `h_j=w_j(g_j-g_bar)` is tangent and
`G_w(h,u)=SUM_j g_j*u_j` for every tangent u. The finite rule also extends
algebraically to a simplex face, keeping its zero weights zero; the metric
itself is singular there.

The connection between Bayesian updating, discrete replicator dynamics and
categorical Fisher geometry is classical; see
[Harper, sections 2 and 4.1](https://arxiv.org/pdf/0911.1763).
The result here checks the actual FP affine masses and their ambient native
gradient, including the positive base and the hypotheses under which a unit
step is legal. It does not claim a new general natural-gradient principle.

## 3. Why this diagonal geometry respects refinement

Split one fixed expert into two identical copies, with weights a,b replacing
weight a+b. Their entire legal conditional laws are assumed identical;
their gradients at the same mixture are equal. The update above commutes
with summing the two updated weights. By induction, splitting has no effect
on model forecasts or aggregated weights under any common sequence of
observations. This is an arithmetic model relation, not physical or Compiler
equivalence: different graphs, storage, provenance and structural futures
remain different unless a stronger relation is proved.

There is a restricted converse. Consider tangent diagonal gradient rules

`Delta w_j = -eta*f(w_j)*(g_j-lambda)`,

`lambda = SUM_j f(w_j)g_j / SUM_j f(w_j)`,

using one positive function f on (0,1), independent of the number of expert
copies. Require commutation with every positive split of an identical expert.
An unsplit informative other expert has the same weight and gradient in
both descriptions. Equality of its update forces the same lambda. Equality
of the split group's aggregated update then forces

`f(a+b)=f(a)+f(b)` whenever a,b>0 and a+b<1.

The relevant gradient difference can be nonzero even in the positive
two-label affine family, by choosing distinct expert columns. Positivity
makes this additive f monotone, so the usual rational approximation argument
gives `f(w)=c*w` for a constant c>0. Absorb c into eta to recover the rule
in section 2. This is uniqueness within the stated separable diagonal class,
not among arbitrary metrics, state-dependent rules or all FP learners.

Ordinary Euclidean tangent descent fails this refinement criterion even
without clipping. With base(1,1), columns(8,0),(0,8), weights(1/2,1/2) and
target0, a Euclidean tangent step at rate1/8 gives first weight3/5. Splitting
the first expert into two copies of weight1/4 instead gives aggregated first
weight19/30. The multiplicative tangent rule commutes with this split.

This provides a model-level reason to study the new geometry. It is not a
Foundation requirement that every physical learner commute with such a
refinement. In particular, equal current experts with different later updates
or legal structural descendants do not satisfy the premise.

## 4. A native whole-history relation model with bounded masses

For the fair latent-bit, known-noise1/10 model, enumerate K=2^(n-1) latent
assignments with z_0=0. The fixed readout features are

`a_yz(i,j)=8*1[z_i XOR z_j = y]`, with base(1,1).

Every column total is8 on all n^2 ordered pair contexts. Initialize each
world weight to1/K and hold the feature unit slot at1. The resulting native
Program has masses

`M_y=1+8*SUM_(z matching y) w_z`, `T=10`.

Under the gradient rule in section 2, after each ordinary observed label,

`w_z' = w_z*(1+8*1[z matches y])/M_y`.

Starting at the declared fair prior, induction gives the exact whole-history
posterior after every finite history, including cycles, conflicting labels,
diagonals and arbitrary query orientations. Current score-time sources are
only the two ordinary one-hot query roles. The current label enters through
the subsequent CE gradient, affecting the next prediction.

The explicit graph uses the n^2 pair-indicator PRODUCTs and two positive
selected-pair SUMs per world. Each head has eight actual weight-slot incidences
per world. All native activations are at most8, all weights at most1, masses
at most9, and the normalizer is10, independently of history length and n.
The count is

`nodes = 2n+n^2+2K+2`, `edges = 2n^2+K*n^2+16K`, `slots = K+1`.

The final slot count includes one fixed unit feature slot. For n=2,3,4 the
native graphs have14/25/42 nodes and48/118/288 edges. The complete categorical
source domains have4/9/16 rows and no lag expansion or delayed queues.
The parameter state carries the model memory.

These bounded values do not give bounded whole-history physical cost.
There are exponentially many world parameters. At noise1/10 their reduced
rational numerators and denominators can require Theta(t) bits after t
records; a one-edge repeated-label posterior already exhibits that growth.
Inference and gradients traverse the actual graph and must retain their
state and evidence. The [predictive-state law](WHOLE_HISTORY_PREDICTIVE_STATE.md)
shows why a fixed finite precision cannot preserve the all-future guarantee
at all horizons. Small current parameter values cannot be discarded on
confidence alone. No finite-precision or AMP equality follows from T=10.

This model changes the actual initializer and U. In particular,1/K is not
borrowed from the old Gamma1/8 controls when absent, and the fixed feature
slot is not silently subjected to the old full-slot SGD update. The earlier
[two-step v5 calibration obstruction](JOINT_FACTOR_DYNAMICS.md) remains a
theorem for its different initialized learner. The present result is neither
a refutation of it nor a graph-only solution within RN-5's fixed class.

Profile multiplicity still matters. Replaying the same (0,1) label0 once
from the uniform prior gives next forecast41/50; replaying it twice gives
73/82. The update processes every actual replay event. A repeated training
profile is not a reset or a once-counted ordinary-data posterior. Likewise,
the fixed unit feature slot has native gradient -4/45 on an initial diagonal
label0; keeping it fixed is an actual part of the different learner, not an
automatic property of the graph. Frozen-endpoint class scores and fresh
persistence retain their original meanings.

## 5. Necessary boundaries

**Unequal expert normalizers.** Positive affine masses alone do not make
the unit tangent step nonnegative. With base(1,1), columns(0,0),(0,20),
weights(9/10,1/10) and target0, the actual native gradient gives

`w'=(27/20,-7/20)`.

There is no generic license to install this rule on every positive Program.
Changing the step or clipping the negative coordinate defines another
transition law; it cannot inherit this theorem's unit-step Bayesian
interpretation. Division by the proved exact unit total is an identity,
not a repair for this negative-successor counterexample.

**Which Fisher metric.** The categorical weight metric is not generally the
Fisher metric of the currently observable native pair predictions. For n4,
let `v_z=chi_4(z)/K` at the uniform world weights, where chi_4 is the product
of all four latent spins. This tangent has categorical squared norm1, yet
the derivative of every current pair forecast in its direction is zero.
The Fisher metric built only from those current observations has a null
direction there.

This lost direction can matter later. The two strictly positive free weight
states `w_z=(1 +/- (3/5)*chi_4(z))/K` have equal predictions on every current
pair. After the same (0,1) label0 under the exact new rule, their next (2,3)
forecasts are173/250 and77/250. These higher-order prior states are not
claimed reachable from the fair initializer by the pairwise likelihood
history; the [minimality theorem](WHOLE_HISTORY_PREDICTIVE_STATE.md#3-minimality-and-the-scope-of-exact-pair-moments)
keeps its own family scope. The metric choice is an explicit learner
coordinate, not an inference from today's output Fisher matrix.

**Runtime and lineage.** The subsequent [scoped Runtime extension](SIMPLEX_RUNTIME_CONTRACT.md)
registers `mean-ce-normalized-simplex-gradient-v1`, including an explicit
normalizing division on both exact and rounded paths. It is the identity on
the exact simplex. The extension owns the selected block, fixed coordinates,
initializer, update clock and full reference/physical transitions; the exact
theorem audit still checks that an unknown optimizer ID is refused. A
different U creates a different lineage; old profiles, class proofs, fresh
persistence and installation evidence cannot be inherited. Foundation VII
already treats U as a learner coordinate; no new architecture action is
required by this derivation.

## 6. Minimal evidence

Run `python -B experiments/joint_uncertainty/simplex_gradient.py`. Its
independent full-assignment likelihood uses neither the selected graph's
global-flip reduction nor its update formula. Actual native evaluation and
reverse-mode gradients check:

- 961 finite histories and5,955 complete-domain forecasts, with1,051 native
  gradient successors including an80-event agreement/reversal trace;
- 9,183 affine native-gradient steps, including nonuniform priors, three
  labels, unequal positive bases and the algebraic zero-weight boundary;
- 378 native split/merge gradient checks and the unclipped Euclidean
  refinement counterexample;
- the unequal-normalizer negative update, the current-output Fisher null
  direction and its two different future predictions;
- repeated-profile multiplicity and the nonzero gradient of the fixed feature
  coordinate;
- explicit rejection of an unknown optimizer ID by learner registration.

The script imports no Torch and launches no Runtime, target worker or new
experiment. It proves and audits the learner arithmetic law. The separately
registered Runtime audits have their own scope; useful resource-matched
model results and long-history AMP guarantees do not follow from this proof.
