# Native joint SGD preserves pairwise factors until projection

Status: **scoped exact unrounded learner theorem and exhaustive small
native-graph controls on one-hot inputs**. This derives the finite learning strength of the
existing v5 constructor, rather than changing its model, rates or optimizer.
Foundation R4, ERC-1 and the ongoing RN-5 matrix remain unchanged. The general
factor identity allows cycles and repeated edges; the simpler path formula
requires a forest. Projection and numerical rounding delimit both.

## 1. The general unrounded update is a pairwise factor

Let K=2^(c-1) count the relative orientations of c>=2 fixed empirical
components in the [v5 family](JOINT_POLYNOMIAL_PROPOSAL.md). Use base (1,1),
shifted amplitude b_H=a_H+1/2 and cross
normalizer T. All inputs in this proof are one-hot. For any cross observation,
let Q be its current target probability, lambda=eta/T and
sigma*chi_e(H) its agreement character. The exact native gradient gives

`b_H' = b_H*[A+B*sigma*chi_e(H)]`,

`A=1-2*lambda+lambda/Q`, `B=lambda/Q`.

Indeed, the target indicator is `(1+sigma*chi_e)/2`, and the gradient is
`2*b_H*(1/T-I_target/(T*Q))`. Substitution proves the identity. It needs no
neutral forecast or acyclic observation graph.

As long as projection is inactive, b stays at least 1/2. Both parity groups
are nonempty, so the two factors A+B and A-B are positive. Starting from
constant b, its squared values therefore remain a product of positive
pairwise factors on the observed edges. Repeated edges multiply the factor
already on that edge. The normalized distribution `q_H=b_H^2/S`, where
`S=SUM b_H^2`, is a zero-field Ising model on that graph. Cycles do not destroy
this factorization, although they change its marginals and partition function.

The same update also gives the exact mass recurrence

`S_next=(A^2+B^2)*S + 2*A*B*T*(2*Q-1)`.

Here `SUM_H b_H^2*sigma*chi_e(H)=T*(2*Q-1)`: uniform offsets cancel between
the equal-size parity groups. The literal native normalizer is always
`T=S+2-K/4`. Consequently a native cross predictive contrast is S/T times
the corresponding contrast under q. At K8 they are equal; at other K the
positive base must still be accounted for.

These factors encode the exact current amplitude values; they are proof
coordinates, not available initializer coefficients or free compressed
Runtime state. General cyclic partition functions are not supplied by the
identity. It provides no algorithmic speed, resource ownership, reference/AMP
bridge, complete-state quotient or installation certificate. In particular,
an arbitrary future may require projection, which can break this pairwise form.

## 2. Exact forest factorization before the boundary

Fix c>=2 empirical components and their held representative signs h. The v5
learner has K=2^(c-1) relative orientations H. Start all its cross amplitudes
at the registered unit, and set `b_H=a_H+1/2`, so initially b_H=3/2. Internal
updates affect only the separate t and may be omitted from this cross trace.

Consider a sequence of cross observations whose component edges form a
forest, each appearing once. For edge e=(C,D), write
`chi_e(H)=(-1)^(flip_H(C) XOR flip_H(D))` and let sigma_e be the observed
label sign after accounting for h. The forest characters are independent
uniform signs under the uniform orientation measure: choose one free root
bit per tree, then its edge parities independently. Fixing a redundant global
flip does not change this independence. This is a parity-value calculation,
not a quotient of complete Runtime state.

Before an edge joins two current forest components, its parity character is
independent of all preceding characters. Thus its forecast is exactly 1/2.
For an exact unrounded step of positive rate eta_e, its native amplitude
gradient and update are

`dCE/da_H = -(1+2*a_H)*sigma_e*chi_e(H)/T_before`,

`b_H' = b_H*(1+2*lambda_e*sigma_e*chi_e(H))`,

where `lambda_e=eta_e/T_before`. Assume every resulting amplitude remains
nonnegative, so projection is inactive. Induction gives the complete shifted
amplitude vector

`b_H = (3/2)*PROD_observed_e [1+2*lambda_e*sigma_e*chi_e(H)]`.

Define the shifted squared mass and the actual native normalizer by

`S=SUM_H b_H^2`, `T=S+2-K/4`.

Character independence yields the scalar recurrences

`S_initial=9*K/4`, `S_next=S*(1+4*lambda_e^2)`.

This computes the lambda values in event order. The label signs do not change
these normalizers on this scoped trace; they change the corresponding
orientation weights. No fitted coefficient or new update rule is introduced.

## 3. A path law, including the literal positive base

Put `rho_e=4*lambda_e/(1+4*lambda_e^2)`. Expanding each squared factor gives

`[1+2*lambda_e*sigma_e*chi_e]^2`
`= (1+4*lambda_e^2)*(1+rho_e*sigma_e*chi_e)`.

For two distinct initial components C,D connected by the observed forest,
their relative-parity character is the product along its unique path P.
Orthogonality therefore gives the native predictive contrast

`p(aligned parity 0)-p(aligned parity 1)`
`= (S/T)*PROD_{e in P}(sigma_e*rho_e)`.

If they are still disconnected, the contrast is exactly zero. The alignment
is relative to the held h signs; no ground-truth sign is given to the learner.
These claims concern cross queries. The graph's original internal predictions
continue to use t.

At K=8 the offset vanishes and S/T=1. Its normalized orientation values are
exactly a zero-field forest distribution with edge reliabilities rho_e.
The general path-product property for such distributions is standard; see
[Anandkumar, Tan and Willsky, Fact 2, equations (42)-(43)](https://escholarship.org/content/qt551760x1/qt551760x1_noSplash_b85769ad145f0faf2844443def2e46e8.pdf#page=24).
The result here derives those particular reliabilities and the offset from
native SGD. It does not claim novelty for the tree correlation identity.

For other K, retain S/T. In particular it exceeds one at K>8: expressing the
orientation values as a forest distribution plus a uniform term would then
give a negative uniform coefficient. Do not describe that algebraic expression
as a convex mixture. Actual native values remain positive on the stated
nonnegative-amplitude trace.

The boundary can also be checked without enumerating worlds. Independence
allows every unfavorable edge character to occur together. Before clipping,
the minimum shifted amplitude is

`(3/2)*PROD_e (1-2*lambda_e)`.

Starting in the nonnegative amplitude domain, projection is inactive through
the prefix exactly when every step's factors are positive and every prefix
of this product is at least 1/2. A factor at most zero already violates the
domain. Equality at 1/2 is a legal zero amplitude. This criterion concerns
the unrounded trace only; it is not an AMP or resource admission certificate.

## 4. Same information, different finite evidence strength

For independent fair latent component bits and independent label noise
epsilon, the exact posterior after this forest has edge reliability
`delta=1-2*epsilon`. A new noisy query over a length-d path therefore has
aligned contrast `delta^(d+1)*PROD_{e in P} sigma_e`: d edge-likelihood factors
and one independent query-noise factor. At epsilon=1/10, two observed path
labels give matching forecast 189/250. The exact audit also checks this by
retaining and updating all 2^c assignments, including global flips.
This comparison assumes correct fixed internal signs; the exact audit uses
singleton components. It is not the full posterior for arbitrary uncertain
empirical components in RN-5.

The native law gives a different quantity, `S/T*PROD rho_e`. These are actual
finite optimization strengths, not missing representable values. For K8,
fixed eta makes T grow on each such step, so lambda and rho decrease while
lambda<1/2. Adding an independent edge then leaves the older edge's contrast
unchanged but assigns the new edge a smaller reliability. For example at
rate1, observing (0,1) then (1,2), both with label zero, leaves prediction on
(0,1) at 25/41; reversing the two observations gives 8281/13610 instead.
The exact IID posterior is invariant to that order at this information cut.

There is a stronger calibration obstruction than a small chosen rate. After
two path edges, let x,y be their signed predictive contrasts and z that of
the endpoint pair, with signs aligned to the two observed labels. The native
law forces `z=(x*y)/R`, where `R=S/T`. Under the registered unit initialization
and any two positive rates that avoid projection,

`R>=min(9*K/[8*(K+1)],1)`.

S increases at each neutral step, while the offset 2-K/4 is fixed; this proves
the inequality. For every c>=3, its right side is at least 9/10. The correct
noise-1/10 posterior instead has contrasts `(16/25,16/25,64/125)`, which would
require `R=4/5`. Thus **no choice of the two rates in this unprojected regime
can simultaneously match the posterior on all three pairs**. At K8 this
reduces to the native identity z=x*y versus the posterior's strict inequality.
Even rates chosen from the observed history do not change that identity.
This is a restriction of the two-step transition family, although arbitrary
real amplitude values can represent all three posterior forecasts. Indeed,
mixing the latent posterior with weight delta and the uniform orientation
distribution with weight 1-delta gives all noisy cross-pair marginals.
The [real-mixture preimage](JOINT_LEARNER_SCALE_DYNAMICS.md) represents that
strictly positive vector; no reachable reference state is inferred.

These singleton-component controls have no incorrect internal signs. Their
failure to calibrate therefore isolates a finite-update mechanism from the
earlier fixed-sign obstruction. Projection or further observations can leave
this two-step family; no impossibility is asserted for those continuations.

There is also dilution by unrelated components. Observe the same two edges
(0,1), (1,2), with label zero, at rate1 and the unit initialization. With
three components the next (0,2) forecast is 20289979/35917958, approximately
0.5649. Adding one otherwise unobserved fourth component changes it to
7129/13610, approximately 0.5238. The ideal same-cut posterior remains
189/250 in both cases. This compares new initialized learners; it does not
erase an existing component or transfer state/evidence between programs.

More generally, for a fixed finite forest prefix and fixed positive rate eta,
as K grows, projection is inactive eventually and

`T=2*K+O(1)`, `S/T -> 9/8`, `rho_e ~ 2*eta/K`.

The matching forecast advantage on a fixed length-d path consequently obeys

`p_matching-1/2 ~ (9/16)*(2*eta/K)^d`.

Indeed each of finitely many updates changes S by O(1/K), starting from
9*K/4, so these estimates follow from the exact recurrence. This is an
update law for this unit-initialized dense orientation parameterization,
not a resource lower bound for FP or a statistical information limit.
The asymptotic family assumes enough initializer slots and graph resources
to form each finite witness; it does not extend RN-5's fixed Gamma or grammar
budget to arbitrarily many components. An actual constructor may refuse
before such a learner exists.
It demonstrates why merely having a transitive gradient may learn too slowly.
No state-dependent rate, renormalization, alternate initializer or replacement
constructor is installed or proposed as a certified fix by this theorem.

## 5. Projection and missing continuation information

A closing cycle has a generally nonneutral forecast, so the neutral-gradient
simplification in section 2 no longer applies. The exact control closes the three-component
two-edge path and verifies that its actual successor differs from the naive
forest factor update, even with projection inactive. The general A/B factor
identity still holds, and is checked on these cycles and repeated edges.

On four components at rate4, the first two edges of a three-edge path remain
inside the nonnegative domain, but the third clips an amplitude. The actual
projected endpoint forecast differs from the unprojected product expression.
Thus a result that works through two updates cannot silently be continued
through this third update. Grid16 and actual AMP need their separate complete
trajectory audits; neither inherits these exact equalities.

In fact that projected K8 state leaves even the complete zero-field pairwise
Ising family. Let chi_4 be the product of all four component signs. Every
pairwise log density has zero coefficient on chi_4, hence

`PROD_{H: chi_4(H)=+1} b_H^2 = PROD_{H: chi_4(H)=-1} b_H^2`.

This follows by summing the log density against chi_4 and using character
orthogonality. The positive-weight product test is exact and needs no
numerical logarithm. The actual third projected update violates it. The
native graph is unchanged: an existing projected SGD transition created
this higher-order dependence. It was not an added architectural action.

Pair forecasts and total scale do not contain all the information needed
by later updates. For any current q and an unprojected factor update, put
`r=2*A*B/(A^2+B^2)`. If m_f denotes E_q[chi_f], then

`m_f_next = [m_f+r*sigma*E_q(chi_f*chi_e)] / [1+r*sigma*m_e]`.

For disjoint queried pairs e,f the numerator uses a four-component moment
that their current pair forecasts do not determine.

A direct native example keeps K8, t=8 and total cross scale T=20. In one
state choose b=2 on chi_4=+1 and b=1 on chi_4=-1; in the other state swap
these values. The amplitudes are respectively 3/2 and 1/2. Both states give
the same forecast on every one-hot pair: 1/2 across distinct components and
9/10 on the diagonal. Their scales agree, but their chi_4 moments are +3/5
and -3/5. After the same (0,1) label zero at exact unrounded rate1, no amplitude
clips, and their next (2,3) forecasts are **113/202** and **89/202**.

These are free rational parameter states, not claimed to be reached by RN-5's
Gamma/profile history. They disprove a value-level sufficiency claim even
after the common scale is retained. There is no Runtime quotient, evidence
transfer or new initializer authorization here. The actual complete Runtime
retains the amplitude state instead of replacing it by current pair forecasts.

The family restriction matters: the fixed-known-noise full posterior is a
minimal pairwise Ising exponential family, in which the complete exact pair
moment vector does determine its signed edge counts. The two free states
above have a nonzero four-spin log interaction and lie outside that family;
the projected SGD example can also leave it. See the
[whole-history predictive-state proof](WHOLE_HISTORY_PREDICTIVE_STATE.md).
Its exact mean-map uniqueness gives neither a stable finite-precision inverse
nor a quotient for this complete learner.

## 6. Minimal evidence

`experiments/joint_uncertainty/factor_dynamics.py` exhausts every ordered,
signed forest prefix on two through four singleton components at rates1/8
and1. Full signed path prefixes on five components additionally cover the
negative algebraic offset. It compares actual independent native-graph
gradients and forecasts with the closed factorization, and compares a full
assignment posterior with the noisy-query path formula. The dilution, cycle
and projection controls remain separate from RN-5 target scores. The script
constructs no Runtime state, makes no resource/class/installation claim and
imports no Torch. Its amplitudes are exact unrounded rationals, not registered
grid-profile endpoints.

The exhaustive controls cover 1,932 prefix states, 15,668 shifted-amplitude
coordinates, 11,624 native forecasts, 1,924 native gradient successors and
11,624 independent full-posterior forecasts. Additional unequal-rate controls
check the calibration identity for both label orientations; cases that clip
are explicitly kept outside that theorem's hypothesis.
There are 88 such controls and 20 excluded boundary cases. Another 1,024
native-gradient updates check the general pairwise factorization, including
448 nonneutral cycle/repeated-edge updates and 10,240 amplitude coordinates.
The projected four-spin product inequality and the equal-scale/equal-forecast
counterexample are separately verified by the independent native interpreter.
