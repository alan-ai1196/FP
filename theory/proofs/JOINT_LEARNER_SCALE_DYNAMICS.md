# Joint learner geometry and optimization state

Status: **scoped exact unrounded dynamics, real-parameter stationarity and
fixed-sign risk optimum**, with independent algebraic and native-graph
checks. This explains a learning mechanism in the registered v5 model; it
adds no static resource case, numerical acceptance rule, optimizer action,
or RN-5 parameter change. Grid16 and actual AMP still require their own
trajectory audits. Foundation R4 and ERC-1 remain frozen.

## 1. One mass-drift identity

For a one-hot cross-component query, let K be the number of relative
orientations in the [v5 family](JOINT_POLYNOMIAL_PROPOSAL.md). Exactly half
match either label. Let `w_H=a_H+a_H^2`, `u_H=(a_H+1/2)^2=w_H+1/4`, and
`d=1-K/8`. These are proof coordinates, not new parameters available to the
compiler. For the current target head and its opposite, write their native
masses as M and N, with `T=M+N`. Then

`M=d+SUM_matching u_H`, `N=d+SUM_opposite u_H`.

The possibly negative d is only an algebraic offset; the actual native heads
retain base one and nonnegative excesses. Their masses satisfy M,N>=1.
For CE, set `g_H=1/T-I[H matches]/M`. The actual amplitude derivative is
`(1+2*a_H)*g_H`. Before projection, an exact SGD step of rate eta gives

`u_H' = u_H*(1-2*eta*g_H)^2`.

Consequently, if

`A=d*(1/M-2/T)`,

`B=(M-d)*(1/T-1/M)^2+(N-d)/T^2`,

then the unprojected polynomial mass obeys the exact identity

`T'-T = -4*eta*A + 4*eta^2*B`.

Indeed, `SUM_H u_H*g_H=A` and `SUM_H u_H*g_H^2=B`; expansion proves the
formula. It is a single identity for the whole family, not a set of fitted
resource laws. Where the unprojected step is nonnegative, it is the actual
unrounded native update. Other states need the explicit projection below.

## 2. The registered four-component learner

For K=8, d=0 and T is the squared Euclidean norm of the shifted amplitude
vector b=a+1/2. The first-order term cancels:

`T'-T = 4*eta^2*N/(T*M) > 0`.

In continuous gradient flow this scale is constant, whereas a finite Euler
step increases it. This is the familiar norm-growth identity for a gradient
perpendicular to a scale-invariant parameter vector, applied here to the
native cross-query masses. The general mechanism is already established in
[Arora, Li and Lyu, Lemma 2.4](https://arxiv.org/pdf/1812.03981); the FP-specific
content is the shifted positive polynomial, literal base cancellation and
its projection/range implications. No novelty claim is made for that general
optimization identity, and the paper's BN convergence results are not
transferred to this constrained learner.

Projection does not defeat the conclusion when `eta<=T/2`. Matching b values
grow; an opposite b is multiplied by `1-2*eta/T>=0`. Projecting a to zero
raises every resulting b below 1/2 to 1/2 and therefore cannot lower its square.
Thus **exact unrounded nonnegative SGD** satisfies

`T_next >= T + 4*eta^2*N/(T*M) > T`.

For eta>T/2 all opposite shifted coordinates become nonpositive before
projection, so that opposite native mass becomes exactly 1. Meanwhile the
matching mass is `M*(1+2*eta*N/(T*M))^2`. Thus its total mass increase is
`4*eta*N/T+4*eta^2*N^2/(T^2*M)-(N-1)>0` as well. **Strict projected scale
growth holds for every positive rate**; the first lower bound uses eta<=T/2.

At the registered unit initialization T=18. Both stated rates 1 and 4 meet
the condition, and subsequent cross updates preserve it by increasing T.
Within-component updates only change the separate scale t, so do not alter
this cross scale. No assumption on the sequence of observed labels is used.
The first rate-1 update gives `18+2/9=164/9`, agreeing with the earlier exact
range-refusal control. That old refused endpoint is not rerun or relabelled.

If an unrounded continuation stays below a finite cap R, M<=R-1 and T<=R,
so an update with eta<=T/2 increases T by at least `4*eta^2/[R*(R-1)]`.
The complementary case increases it by more than 2. Each increase is therefore
at least `min(4*eta^2/[R*(R-1)],2)` for a fixed positive rate. An infinite
cross-query continuation cannot stay inside that cap. This is a scoped
optimizer fact; it is not a claim that the finite RN-5 tapes must hit their
registered bound. Rounding can change the identity, so no grid16 or AMP
monotonicity, crossing time or failure is inferred from it.

## 3. A normalization would change the learner

At K=8, replacing b by c*b preserves every cross-query probability whenever
the transformed a remains nonnegative. Keeping t unchanged also preserves
all within-component predictions on the one-hot domain. Nevertheless, it changes the next SGD
update: the effective rate on the normalized b direction scales as eta/T.
Current prediction equality therefore does not license erasing this scale,
transferring evidence, or inserting a post-update renormalization.

A direct native example starts with all a=1, then compares all a=5/2
(the transformation b -> 2*b). Both initially predict 1/2 on every cross
query. After the same matching label with exact rate 1, the next matching
probabilities are respectively **25/41** and **1369/2594**. The latter equals
the unscaled learner's rate-1/4 result, as the scale dependence predicts.
These are different complete learners, despite equal initial one-hot predictions.

This also explains why posterior normalization cannot simply be copied into
FP's fixed learner: the registered SGD transition must be included in an
equivalence proof. Nothing here changes the optimizer or supplies a new
semantic action. The ongoing experiment keeps both registered rates,
execution budgets and strong adaptive posterior unchanged.

Retaining this common scale is still insufficient for a current-prediction
summary to determine the next learner. The later
[factor-dynamics counterexample](JOINT_FACTOR_DYNAMICS.md) holds all one-hot
pair forecasts and the scale fixed, while a fourth-order moment changes the
next forecast. It gives the full unrounded update factor behind this effect.

## 4. Continuous mixture relaxation and first-order stationary points

This section deliberately relaxes initializer/profile reachability, the
commit grid, integer precision and resource caps. Keep the component signs
and the graph fixed, and allow arbitrary finite nonnegative **real** amplitude
values. It is not the Reference Compiler's exact decision class and cannot
supply a class certificate, construction path or installation authority.

Set `kappa=2/K`, `v_H=a_H+a_H^2+kappa`, `pi_H=v_H/T`, where `T=SUM_H v_H`.
Exactly K/2 worlds match each label on a cross query. Therefore the native
head mass is `T*SUM_matching pi_H`: its base one is exactly the contribution
of the kappa terms. Cross predictions are consequently ordinary mixtures
over the fixed relative-orientation worlds.

Conversely, for any strictly positive simplex vector pi, choose
`T>=max_H kappa/pi_H`. Then `w_H=T*pi_H-kappa>=0` and
`a_H=(sqrt(1+4*w_H)-1)/2` reproduce it in this real-parameter relaxation.
That square root need not be rational, available in Gamma, or reachable by
a registered profile. This is a characterization of relaxed values, not a
way to initialize a legal reference learner. Positive rational amplitudes
are dense in the relaxation, but no bounded-precision or legal-reachability
claim follows from that density either.

For one fixed nonnegative weighted CE objective on cross queries, its loss
L(pi) is convex: each forecast is linear in pi and negative log is convex.
It need not be strictly convex; different orientation mixtures can have
identical pair marginals.

**Theorem.** Every finite first-order stationary point for nonnegative
amplitudes a is globally optimal for this relaxed cross-query objective.
Here stationary means gradient zero on positive coordinates and gradient
nonnegative on zero coordinates, equivalently a fixed point of exact
projected full-batch gradient descent on this one fixed objective.

To prove it, consider the prediction-preserving infinitesimal direction

`r_H = v_H/(1+2*a_H) > 0`.

Scaling v changes no pi, so `SUM_H r_H * dL/da_H = 0`. At a stationary point,
every summand is zero on a positive amplitude and nonnegative on a zero
amplitude. Since every r_H is strictly positive, every coordinate gradient
must be zero, including those on the boundary. If g is the gradient of
L with respect to pi, the chain rule gives

`dL/da_H = (1+2*a_H) * [g_H-SUM_J pi_J*g_J] / T`.

Thus all g_H equal their pi-weighted average. For any other interior simplex
vector pi', `g dot (pi'-pi)=0`; the first-order convexity inequality implies
`L(pi')>=L(pi)`. This proves the theorem without assuming a unique optimum.
The separate within-component scale and its wrong-sign obstruction are not
removed by optimizing this cross-query mixture.

The positive linear term matters here because the derivative is nonzero at
zero. With pure squared amplitudes, all amplitudes zero give zero native
coordinate gradients and uniform predictions, even when a positive amplitude
strictly improves CE. The exact audit retains that counterexample. A linear
weight map also has the stationary-point property; quadratic curvature is
used for the earlier interior transitive response, not for this proof.

This excludes suboptimal first-order traps only in the stated relaxation.
The actual experiment uses stochastic single-label updates, finite grids,
reachable initializers and resource admission. None is replaced by this
convex problem. Finite-rate trajectories, a changing objective, rounding,
initialization restrictions, retained wrong internal signs and resource
refusals can still prevent useful learning. In particular this is neither
a convergence theorem nor an explanation sufficient to assign the whole
measured gap to one mechanism. It also does not authorize rescaling the
complete learner: section 3 shows that rescaling changes its next update.

## 5. The fixed-sign risk bound is attained in the real relaxation

The [empirical sign obstruction](EMPIRICAL_SIGN_OBSTRUCTION.md) gives a lower
bound by optimizing the cross-block probabilities separately. For its stated
uniform full-domain population risk, those optima are in fact jointly
attainable. Continue to use the real-parameter relaxation of section 4, now
also allowing the separate internal scale t to be any nonnegative real.
This is a value theorem about a fixed graph, not a reachable-state result.

Fix any c>=2 nonempty empirical components and any actual residual-sign
counts `(a_C,b_C)`. Write

`rho_C=(a_C-b_C)/|C|`, `s=1-2*epsilon`, with `0<epsilon<1/2`.

Consider this mathematical distribution on component signs Z_C in {-1,1}:
with mass s, draw the signs independently with means rho_C; with mass 1-s,
draw them independently and uniformly. It has

`E[Z_C*Z_D]=s*rho_C*rho_D` for C!=D.

Pass to the K=2^(c-1) relative orientations, identifying only the global
sign in this parity-value calculation. For a representative z with its first
coordinate 1, its probability is

`pi_z = s*[PROD_C [(1+rho_C*z_C)/2] + PROD_C [(1-rho_C*z_C)/2]] + 2*epsilon/K`.

Every entry is at least 2*epsilon/K. The equal-parity marginal is

`SUM_{z: z_C=z_D} pi_z = [1+s*rho_C*rho_D]/2 = q_CD`.

Thus one strictly positive mixture attains all of the independent cross-block
optima simultaneously. Set `T=1/epsilon` and
`w_z=T*pi_z-2/K>=0`. The finite real amplitudes
`a_z=(sqrt(1+4*w_z)-1)/2` give exactly those native predictions. These algebraic
amplitudes need not be rational or available to a registered reference path.

For the shared internal parameter, `q_in>=1/2` and `q_in<=1-epsilon<1`.
The finite nonnegative value

`t=(2*q_in-1)/(1-q_in)`

attains `(1+t)/(2+t)=q_in`. Hence the exact minimum of the fixed-state
uniform full-domain risk in this relaxation is

`[W*H(q_in) + SUM_{C!=D} |C|*|D|*H(q_CD)] / n^2`.

The lower bound is the earlier blockwise CE inequality; the distribution
above proves the matching upper bound. The signs s_i enter only the theorem
and its diagnostic optimum. They are not supplied to Runtime, a constructor,
or the measured learners. This is not a method for recovering unknown signs.

Joint consistency is essential: arbitrary independently chosen block
probabilities need not be feasible. For three component bits, the sum of the
three equal-parity indicators is always 1 or 3. Assigning probability 1/10
to each equality would violate that inequality. The residual-product form
above, rather than convexity alone, proves attainability here.

For the registered selected diagnostic, the optimal real values have internal
scale t=3, two orientation probabilities 17/40 and six probabilities 1/40.
At T=10, their excesses are respectively 4 and 0, so the two nonzero
amplitudes are `(sqrt(17)-1)/2`. The fixed-state risk lower bound
`H(4/5)/4 + 3*[log(2)+H(1/10)]/8` is therefore the exact relaxed minimum.
This diagnoses the limitation of the held empirical signs even after ideal
fixed-state optimization. It does not compare that optimum with a stream of
changing parameter states: the weaker prequential bound retains its separate
scope. It also does not certify the registered Gamma/profile/grid/resource
class, a model's optimization trajectory, or an AMP parameter realization.

## 6. Minimal evidence

`experiments/joint_uncertainty/scale_dynamics.py` uses the independent native
forward-gradient interpreter on synthetic 2-, 3-, 4- and 5-component graphs.
It verifies 1,008 exact mass identities, 8,352 graph gradient coordinates,
288 projected K8 strict-growth controls, 96 additional large-rate projection
controls, and the rescaling counterexample. Legal decreasing-mass examples
at K=2, K=4 and K=16 rule out extending K8 monotonicity to the whole family.
The K16 controls also cover the negative algebraic offset d; native masses
retain their positive base throughout. Another 336 exact checks verify the
strictly positive prediction-preserving direction and its zero inner product
with the native gradient. A pure-square native graph has zero gradient and
prediction (1/2,1/2) at zero amplitudes, while another parameter setting gives
(2/3,1/3) and strictly better 9:1 CE. This audits the distinction between
first-order stationarity and optimal relaxed values.
It reads no new RN-5 target labels, constructs no Runtime state and supplies
no GPU forecast, class certificate or installation evidence. Registered
model outcomes and any later rounded-scale observations remain separate.

`experiments/joint_uncertainty/sign_relaxation.py` exhausts all residual-sign
count patterns of component sizes one and two, for two through four
components and noise 1/10 or 1/4. Exact rational checks verify 1,550 joint
mixtures, 11,100 orientation probabilities and 16,600 ordered block optima,
plus 3,100 comparisons of exponentiated expected losses with uniform and
nonuniform competitors. Individual residual-bit enumeration independently
checks the block target probabilities. The three-bit consistency
counterexample and the selected diagnostic's algebraic values are retained.
These are polynomial excess/value calculations: the script does not claim
that their quadratic-root amplitudes are legal rational Runtime states.
No new target labels, GPU work, model scores or installation evidence enter.
