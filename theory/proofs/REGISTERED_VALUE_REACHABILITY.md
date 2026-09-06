# A reachable structural witness and a zero-initialization obstruction

Status: **PROVED for the explicitly registered value dynamics below**, 2026-09-06.
This addresses value construction, not complete Runtime/AMP installation.

## 1. The registered finite profile problem

Use the unary binary sources, fixed base `(1,1)`, uniform context weighting,
target table `p^0=(1/2,1/2,3/4,1/4)`, and readout-normalizer cap `R=4` from
XVII.3. Retain a profile data set with four labels per context and class-1
counts `(2,2,3,1)`. Its ordinary mean cross-entropy is exactly this finite-table
objective. The data are **profile data**, not fresh persistence evidence.

Every trainable SUM coefficient starts at zero. Value optimization is full-batch
projected gradient descent on mean CE, direct nonnegative coefficient coordinates,
step size **16**, no momentum/weight decay, and a commit only after the full
registered batch. Each step charges one replay/forward/backward pass over the
16 retained observations. This is an explicit fixed value process, not free
optimization over all encoded coefficients or a new semantic construction action.

## 2. Two direct PRODUCTs have a certified finite value path

Construct from source references

\[
M_0=1+\theta_0 x_1z_1,\qquad
M_1=1+\theta_1 x_1z_0.
\]

There are exactly two independent trainable readout SUM slots `theta_0,theta_1`.
They are not tied: symmetry of the data and equal initialization imply equal
values along this registered trajectory. The derivative for each slot is

\[
\frac{\partial L}{\partial\theta_j}
=\frac{\theta_j-2}{16(\theta_j+1)(\theta_j+2)}.
\]

Consequently, with `theta_0=theta_1=theta`, the actual update is

\[
\boxed{\theta^{(t+1)}=\theta^{(t)}+
\frac{2-\theta^{(t)}}{(\theta^{(t)}+1)(\theta^{(t)}+2)},\quad\theta^{(0)}=0.}
\]

Projection is inactive: the first step gives 1, and subsequent steps remain
in `[1,2)`, monotonically approach 2, and keep every normalizer at most 4.
The Bayes coefficient is not silently installed at initialization.

Let `e_t=2-theta^(t)`. For `t>=1`,

\[
e_{t+1}=e_t\left[1-\frac1{(\theta^{(t)}+1)(\theta^{(t)}+2)}\right]
\le\tfrac{11}{12}e_t,
\quad e_t\le(11/12)^{t-1}.
\]

On the two bottom contexts the correct-label probability is
`q_t=(1+theta^(t))/(2+theta^(t))`, with
`3/4-q_t=e_t/[4(theta^(t)+2)]<=e_t/12`. The other two contexts are exactly
uniform. From `KL(p||q)<=(p-q)^2/[q(1-q)]` and `q_t in [2/3,3/4)`,

\[
\boxed{L_t-L_{Bayes}\le\tfrac1{54}(11/12)^{2(t-1)}.}
\]

At **21** registered steps this analytic bound is strictly below `1/1568`,
the lower bound for every at-most-one-PRODUCT model at cap 4. Thus the finite
trajectory already produces a reachable two-PRODUCT witness that strictly
beats the **entire** excluded grammar. It need not reach Bayes risk exactly.

An exact outward-rounded rational trajectory enclosure gives a tighter
certificate: **13 steps** suffice using the same KL upper bound evaluated at
the certified lower parameter endpoint. This costs 208 profile-observation
evaluations and 13 full backward/update passes, over 16 unique retained labels.
The simple analytic 21-step proof remains independent of the enclosure code.

### Finite arithmetic for the trajectory certificate

Do not expand the exact rational iterate indefinitely: numerator/denominator
sizes grow rapidly. After the exact first iterate 1, the map is increasing on
`[1,2]`; its derivative is

\[
1+\frac{\theta^2-4\theta-8}{(\theta+1)^2(\theta+2)^2}>0.
\]

Evaluate the map at both rational interval endpoints and round outwards to a
declared dyadic grid. This encloses every exact iterate by induction. The loss
upper bound depends monotonically on the lower endpoint and is compared to
`1/1568` using rational arithmetic. Float64 trajectories are a separate numerical
audit; they do not replace the exact enclosure or prove a reference/AMP bridge.

### A separately registered finite-encoded path

The same finite-step conclusion holds if each coefficient commit is
preregistered to round **down** to the `2^-32` grid:

\[
\hat\theta^{(t+1)}=2^{-32}\lfloor2^{32}f(\hat\theta^{(t)})\rfloor,
\]

where `f` is the update above. Starting at 0, this remains on `[0,2)`, is
nondecreasing, and obeys the cap. Each independent coefficient is stored as
an unsigned integer smaller than `2^33`, with the scale implicit in the claim.
The reference gradient/update uses exact rational arithmetic on these encoded
inputs, then the declared rounding; it is not an AMP kernel.

On `[1,2]`, `0<f'<=1`. Monotonicity and nonexpansion imply
`0<=theta^(t)-hat theta^(t)<=(t-1)2^-32` after the exact first step. More
directly, the audit executes the rational update/rounding rule and checks its
own loss bound: this **finite-encoded trajectory** also beats `1/1568` at step
13. A rounded midpoint of a proof enclosure is not substituted as the model;
the model follows its own preregistered rounding transition.

The observation-evaluation count is not total arithmetic work. Exact gradient,
rounding, replay storage, and graph/build/install work still require their
registered resource charges. The bounded coefficient representation avoids
silently installing a giant unrounded rational iterate while preserving an
auditable finite reachable witness.

## 3. An expressive one-PRODUCT program can be permanently unreachable

Consider the native parameterization

\[
h=(a x_0+b z_1)(c x_1+d z_0),
\quad M_0=1+e h,\quad M_1=1+u x_1+v z_0.
\]

It contains the exact one-PRODUCT witness at peak normalizer `16/3`, with
`(a,b,c,d,e,u,v)=(1,1,3,5/3,1,1/3,5/3)`. Thus its expressivity is not in doubt.
But under the same zero initializer and registered projected-gradient rule,
the set

\[
\boxed{a=b=c=d=e=0}
\]

is invariant for every sequence of profile labels and every number of updates.
At that set, `h=0`, its derivatives with respect to its four parent coefficients
vanish, and `dM_0/de=h=0`. Gradients for these five slots are exactly zero;
updating `u,v` cannot change the conclusion. The candidate remains in its
SUM-only subfamily forever. In this particular parameterization `M_0=1` and
`M_1>=1`, so it cannot even make a class-1 probability below 1/2 on the target's
bottom-right context. A good encoded parameter vector is not a reachable value
witness for this initializer/optimizer contract.

More generally, independent dormant coefficients form an invariant zero face
for a zero-preserving first-order optimizer when every mass monomial involving
each such coefficient retains another zero coefficient. Sharing with a live
route, a registered nonzero initializer, momentum state, or another registered
value operation can break that premise. It cannot be assumed away by treating
current output equality as future learner equivalence.

This does **not** prove every one-PRODUCT graph is unreachable, nor that all
initializers fail. It falsifies the inference from a valid static expressivity
construction to arbitrary zero-initialized gradient reachability. A Compiler
may supply another **registered** value constructor or return unresolved for
that candidate; an unregistered parameter kick is not a proof.

## 4. Scope of the progress

There is now a concrete finite task-loss path from a zero state to a strict
structural winner under a registered numerical cap. The comparison excludes
arbitrary SUM depth/sharing and arbitrary one-PRODUCT parents, not a weakened
baseline or a caller-selected architecture menu. Graph construction/build work,
memory ownership, fresh paired persistence and actual AMP execution still need
their own accounting and evidence.

The profile counts define the finite-prefix objective; they do not by themselves
identify a stochastic population table. Population transfer requires the finite-
information conditions in XVII.4, adjusted for this finite-step witness's error.
No theorem here silently recycles profile labels or fabricates a complete
`CERTIFIED_COMPLETE` Runtime decision.

Exact/float64 audit: `theory/numerical_checks/value_reachability_audit.py`.
