# When the native simplex step is a fixed likelihood update

Status: **PROVED, SCOPED; EXACT NATIVE AUDIT AND REACHABILITY COUNTEREXAMPLE**.
This sharpens the [affine-mass sufficient theorem](SIMPLEX_GRADIENT_POSTERIOR.md).
The irreducible condition for its **distribution-wide** guarantee concerns
normalized forecasts. A separate exact counterexample prevents treating that
condition as necessary on every initializer's reachable orbit. This is learner
theory and a passive polynomial audit, not a Runtime extension, new architecture
action, full-state quotient, or reopening of Foundation R4/ERC-1.

## 1. Exact scope

Fix a native positive SUM/PRODUCT Program, a source row and all unselected
parameters. There is no delayed state. Let w be K>=2 selected weights in the
interior of the probability simplex. At a complete unit boundary the gradient
accumulator is empty. Write p_y(w)=M_y(w)/T(w) for the actual native conditional
law and g_k=partial_k[-log p_y] for its **ambient** selected CE gradient.
The registered one-event simplex rule, at a common rate0<eta<=1, is

`U_eta(w)_k = w_k * (1 - eta*(g_k - SUM_j w_j*g_j))`.

Its explicit exact normalization is the identity because the raw sum is1.
It cannot repair negative coordinates. Positive native bases make the forecast
smooth and positive, including a continuous extension to all simplex vertices.
Rate0 is excluded: it freezes weights regardless of the readout and admits no
such converse.
The condition below is required at **every interior weight vector**, for every
label and every row in the declared complete source domain. It is not inferred
from a finite observed trajectory, current Gamma, or vertex forecasts alone.

A fixed likelihood update has positive, state-independent vectors ell_y and

`U_eta(w)_k = w_k * ell_yk / Z_y(w)`, where `Z_y(w)=SUM_j w_j*ell_yj`.

Multiplying all entries of one ell_y by a positive constant leaves that update
unchanged. When speaking of the expert forecast bank itself, use the actual
normalized vertex laws q_yk=p_y(e_k); each column sums to1.

## 2. Characterization and necessity of the unit rate

**Theorem.** For the positive rates supported above, the actual U is a fixed
likelihood update throughout the simplex if and only if either:

1. p_y is independent of w for every label, so the update is the identity; or
2. eta=1 and every p_y is affine on the simplex.

In the second case the unique expert forecast bank is q_yk=p_y(e_k), and
`p_y(w)=SUM_k w_k*q_yk`. The likelihood vectors of the update can differ from
these rows by positive label-wise scales. Thus an informative readout forces
eta=1 even without assuming affine **unnormalized** masses. Here informative
means dependence on the selected weights, not merely dependence on context.

**Necessity.** Divide the proposed update identity by w_k and subtract its
equation for coordinate l. The weighted mean disappears:

`eta * (partial_k - partial_l) log p_y = (ell_yk-ell_yl)/Z_y`.

The right side is the same tangent derivative of log Z_y. The interior simplex
is connected, so integration gives

`p_y(w) = c_y * Z_y(w)^a`, with `c_y>0` and `a=1/eta`.

The constants may depend on label and source row, but not on w. For any
zero-sum tangent v, differentiating the actual identity SUM_y p_y=1 twice
along v yields

`0 = a*(a-1) * SUM_y c_y*Z_y^(a-2)*(SUM_k v_k*ell_yk)^2`.

If eta<1, then a>1. Every summand is nonnegative with strictly positive
prefactor. Consequently v dot ell_y=0 for every tangent v and every label:
each ell_y is constant across worlds. Each p_y is therefore independent of w
and U is the identity. An informative fixed likelihood law requires eta=1.
Then p_y=c_y Z_y is affine; continuity to vertices gives q_yk=c_y ell_yk.
This also accounts for label-wise rescaling rather than incorrectly equating
an arbitrary update bank with the native forecast bank.

**Sufficiency.** Suppose p_y(w)=w dot q_y on the simplex. Its ambient derivative
may differ from an affine extension's derivative by a common normal component
in every selected coordinate. That component cancels in g_k-SUM_j w_j g_j.
The difference is exactly `1-q_yk/(w dot q_y)`. At eta=1 the update is the
positive normalized likelihood update. If p_y is independent of w, all tangent
derivatives vanish and every allowed eta gives the identity.

The classical connection between discrete replicator dynamics and Bayesian
updating is described by [Harper, *The Replicator Equation as an Inference
Dynamic*, arXiv:0911.1763v3 (2010)](https://arxiv.org/abs/0911.1763v3).
The calculation here supplies the scope and converse for the actual native
CE step and its normalized multiclass readout; it claims no general priority
for the connection or uniqueness among other optimizers.

## 3. Affine masses are sufficient, not necessary

For two selected weights and fixed feature parameter t=1, native positive
syntax can realize

`M_0 = 1 + 8*w1 + t*w1*w2 + 8*w1^2*w2`,
`M_1 = 1 + 8*w2 + t*w1*w2 + 8*w1*w2^2`.

At the fixed t, these are `(1+w1*w2)*(1+8*w_y)`. Both masses are nonlinear,
but their common positive factor cancels from normalized forecasts and from
every selected CE tangent. They have the same forecasts and selected unit
updates as masses(1+8w1,1+8w2). All coefficients above have literal positive
SUM/PRODUCT realizations; the source is the same constant1 and t remains fixed.

This is **not** complete learner or Compiler equivalence. The native caches,
normalizers, operation counts and fixed-parameter derivatives differ. After
one actual label0 from fair Gamma, both learners have weights(9/10,1/10).
At the next observed label0 their fixed-slot gradients are respectively0
and144/22345. The full observed states therefore differ at the same clocks.
Any lowering must retain and check those fields rather than replacing the
native graph or gradient with the expert bank.

A smaller learning rate is also not generally a different fixed noise model.
For the affine example at eta=1/2, two consecutive label0 updates from fair
Gamma go to weights7/10 and91/110. The implied likelihood odds multiplier is
7/3 at the first step and39/19 at the second. No single fixed likelihood vector
produces both. Rates above1 are already refused by the actual learner's
registration; they are not numerical commit failures in this audit.

## 4. An exact certificate on the simplex

With rational fixed parameters and source values, native masses are positive
polynomials. Obtain q_yk by actual native evaluation at each simplex vertex.
The distribution-wide condition is exactly

`M_y(w) - T(w)*SUM_k w_k*q_yk = 0` on `SUM_k w_k=1`.

Equivalently, each residual polynomial is divisible by SUM_k w_k-1. Substituting
the last selected variable as1 minus the others reduces this to an exact
polynomial identity in K-1 variables. This follows because the simplex
interior is open within that hyperplane. Checking only vertices is insufficient.

The passive audit expands those substituted polynomials with exact rational
coefficients. Negative coefficients in this **proof calculation** are not
native operations or a new signed value constructor. A production proof
procedure would have to pay for expansion, arithmetic and retained evidence;
monomial growth can be exponential and bounded failure must stay unresolved.
The current Runtime deliberately keeps its smaller affine-mass sufficient
analyzer. No experiment source or supported physical backend is expanded here.

## 5. Attack the scope: an informative reachable orbit need not be affine globally

The theorem quantifies over all interior weights. That requirement cannot be
silently imposed on every fixed-Gamma representation. Consider three worlds,
fair Gamma=(1/3,1/3,1/3), the complete single-row source domain one=1, and the
ordinary affine masses

`A_0=1+8*w1`, `A_1=1+8*(w2+w3)`.

Worlds2 and3 have identical expert laws. Their weights remain equal under
every finite label word of the unit learner. Put C=1+2*w2*w3 and h=(w2-w3)^2.
The alternative readout has masses

`M_0 = C*A_0 + h = 1+8*w1+w2^2+w3^2+16*w1*w2*w3`,
`M_1 = C*A_1 = 1+8*(w2+w3)+2*w2*w3+16*w2*w3*(w2+w3)`.

The expanded forms use only positive coefficients and the original positive
base. On the invariant w2=w3, both h and its entire selected gradient vanish.
The common C then cancels from the forecast and selected CE gradient. The
unit update agrees with the affine model, preserves w2=w3 and stays positive.
Induction proves an exact, informative Bayesian trajectory for **every finite
label word** from this actual Gamma. Its first label0 successor is(9/11,1/11,1/11).

The normalized readout is nevertheless nonlinear away from that invariant.
At(1/2,3/8,1/8), the affine and alternative label0 probabilities are1/2 and
177/352. The full-simplex polynomial criterion correctly rejects the alternative.
Thus it is not a necessary condition for an informative **reachable-orbit**
encoding. Equal selected trajectories still do not erase complete state:
the literal native realizations in the audit have initial fixed-slot gradients
0 and-8/605 after label0, as well as different caches and costs.

This counterexample prevents promoting a useful global sufficient analyzer
into an assertion that every other correct codec is impossible. A reachable
invariant needs its own proof from Gamma through every legal source/label,
profile repetition and complete state phase. The example provides a weight-
dynamics invariant; it supplies no Runtime value, physical equivalence,
class-completeness certificate or fresh installation authority.
The counterexample rejects a proposed necessity strengthening; it falsifies
neither the earlier sufficient theorem nor an issued Runtime certificate.

## 6. Exact audit coverage

Run `python -B experiments/joint_uncertainty/normalized_likelihood_law.py`.
The [minimal report](../../evidence/minimal/FP_NORMALIZED_LIKELIHOOD_LAW.json)
contains these overlapping grammar scopes at source one=1, fixed feature1,
selected slots1/2 and three positive interior weight samples:

| Complete three-slot grammar | Graphs | Normalized affine | Informative | Beyond strict mass verifier | Native unit checks | Native refusal witnesses |
|---|---:|---:|---:|---:|---:|---:|
| Nodes3, SUMs1, PRODUCTs1, edges3 |3,184|2,212|0|270|13,272|972|
| Nodes3, SUMs2, PRODUCTs1, edges3 |10,544|7,480|20|884|44,880|3,064|

The first scope is a subset of the second, not additional independent graphs.
Its lack of informative certificates motivated the larger grammar check.
The extra tiny-grammar certificates beyond the strict verifier are all
uninformative; the larger explicit common-factor example supplies the
informative extension. Each symbolic refusal has an independently evaluated
native nonaffinity witness. Each accepted case has actual native one-event
updates checked against its fixed vertex bank.

The two nonlinear constructions additionally check160 pairs of complete
native transitions each over all32 five-label words, preserving actual cursors
and optimizer steps. A four-world model checks all nine source rows and36
native units with multivariate polynomial substitution. Fixed-gradient,
off-invariant and half-rate witnesses are exact. These finite audits support
the proofs; they are neither a new GPU matrix nor a full Runtime release.
