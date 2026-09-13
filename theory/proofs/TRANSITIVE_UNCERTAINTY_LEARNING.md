# Learnability needs propagation of relation moments

Status: **scoped proofs and exact/binary64/rounded-interpreter controls**.
No Foundation or ERC-1 definition changes. These are model/learner controls,
not new static resource laws, registered RN-4 workers, owned constructor
certificates or actual CUDA execution. The complete RN-4 matrix keeps its
original constructor, rates, budgets and all outcomes.

## 1. Two labels can identify a third relation without observing it

Take three empirically disconnected components with independent fair latent
orientations. Representatives have bits `z0,z1,z2`. A pair label equals their
XOR with independent flip probability1/10. Conditioned9:1 diagonal training
is a legal uninformative prefix: it fixes no relative orientation.

Observe labels `a` on(0,1), then `b` on(1,2), after forecasting each. The
posterior correlation of the latent endpoint parity is `(4/5)^2` toward
`a xor b`. Including the next independent label noise gives

`P(Y02=a xor b | Y01=a,Y12=b) = (1+(4/5)^3)/2 = 189/250`.

This is an exact finite conditional statement under the declared ideal law;
it does not follow from a PRNG tape. Before the second label, the second
pair's prediction is still uniform. Thus two currently neutral labels can
create information for a later query.

The v4 pair-local native graph keeps distinct coefficient pairs for each
unordered empirical component pair. A one-hot label on one pair has zero
derivatives in the other pairs' coordinates. With initialized units and
ordinary coordinate SGD, no observation of(0,1) or(1,2) changes the unused
(0,2) pair. Its next prediction remains1/2, regardless of the positive rate,
as long as this fixed learner legally continues. Initial exact units also
stay fixed under the registered projection and grid. This does not say that
Runtime has lost the labels: they remain available to other legal owned
construction strategies.

## 2. A full assignment mixture can have the same learning obstruction

Represent all four relative assignments `h=(0,z1,z2)`. This is an explicit
value constructor invariant under the redundant global flip, not a quotient
of complete FP states. On cross-component queries use positive masses

`M_y = 1 + k * SUM_h w_h * 1[parity_h(query)=y]`.

Start every `w_h=k=1`. Within-component evidence uses its separate scale8.
All initial cross probabilities are uniform. The complete mixture can
represent correlations that the pair-local graph lacks.

Nevertheless, while projection is inactive and exact steps are unrounded,
the gradient in the **linear** weights for a queried parity character
`chi_e(h)=(-1)^parity_h(e)` lies in the span of the constant character and
`chi_e`. Consequently the weight vector stays in the linear span of the
initial constant and the individually queried characters. Walsh characters
are orthogonal on the four assignments. Querying only distinct edges e,f
therefore cannot create the unqueried character `chi_e*chi_f`. Its predictive
contrast remains zero. This argument is a property of the parameterization
and registered additive gradient update, not a lack of representable values.

For the two-event control, both queried pairs are uniform at their forecast
cuts, so the shared output coefficient k has zero derivative and stays1.
At rate `0<eta<3`, the successive linear weights are
`1+(eta/6)*s_a*chi_e+(eta/6)*s_b*chi_f`, where `s_y=(-1)^y`.
They stay positive and still predict1/2 on the endpoint pair. The general
span claim does not cover clipping or arbitrary rounding; the concrete
registered-grid and rounded-path controls are checked separately.

## 3. Native multiplication creates the missing moment

Keep the same positive evidence but parameterize `w_h=a_h^2`, with all
`a_h=1`. This needs only existing SUM slots and a self-PRODUCT. The actual
native graph includes the shared, learnable unit output slot k; it is not
silently fixed. Its derivative is zero at both uniform forecast cuts below.

Let `t=eta/3`, `s=eta/(3+2*t^2)`, with `0<eta<3`. Exact unrounded ordinary
SGD on the two labels gives

`a_h(after two) = (1+t*s_a*chi_e(h)) * (1+s*s_b*chi_f(h))`.

All these amplitudes stay positive. Squaring creates the previously absent
path character, with coefficient `4*t*s*s_a*s_b`. Summing over the four
assignments yields the next matching-parity probability

`1/2 + 8*t*s / (2+4*(1+t^2)*(1+s^2)) > 1/2`.

This is a constructive learning direction across previously unqueried
component pairs. It is not the exact Bayesian likelihood update, an optimal
learning rate, a population risk theorem or an installed FP model. At eta1
its exact value is32273/52018, about0.62042, still short of189/250. At eta1/8
it is650951857/1295924834, about0.50231. Merely making a direction nonzero
can leave its finite learning speed inadequate.

The relevant distinction is closure under products of observed relation
characters. Posterior likelihood multiplication creates these products.
Pair-local coordinates cannot propagate them. Linear assignment coordinates
can represent them but additive SGD need not generate them. The explicit
quadratic native parameterization generates them through ordinary gradients.
This explains a possible next model direction without adding a semantic
architecture action or supplying free fitted posterior coefficients.

## 4. The local propagation coefficient is curvature

The same calculation covers a positive polynomial `w_h=phi(a_h)` at a
common positive initialization a0. Keep k=1 and the two neutral forecast cuts.
Write `d=phi'(a0)`, `D=phi''(a0)`, `M=1+2*phi(a0)`. For small exact unrounded
steps, with projection inactive, the next matching endpoint probability is

`1/2 + eta^2 * d^2*D / (2*M^3) + O(eta^3)`.

To see this, the first amplitude shift is `delta=eta*d/(2*M)` times the
first signed character. The second target is still uniform; its mass is
`M+O(eta^2)`. Expanding its gradient introduces the mixed amplitude term
`eta*delta*D/(2*M)` times the path character. Applying phi contributes one
mixed term from this shift and one from the square of the first-order
shifts. Their sum is `2*D*delta^2`. Four-assignment summation and native
normalization give the coefficient above. The signs combine to `a xor b`;
the argument uses no current target before forecasting it.

Thus degree-one evidence has no such propagation; positive polynomial
curvature supplies it. This is a local learner law, not a resource law or a
claim about every parameterization with PRODUCTs. Representation of a joint
distribution alone does not establish that a specified optimizer will learn
its correlations.

## 5. Attack the square: zero can be absorbing

For pure square weights, `phi'(0)=0`. If projection sets an amplitude to
zero, every later ordinary gradient in that coordinate is zero. At rate4,
the first label in the explicit square graph eliminates two assignments;
an immediately opposite noisy label cannot revive them. A positive-noise
posterior would give every initially possible assignment positive weight.
The shared output coefficient can also move, so this is a coordinate/learner
obstruction, not a claim that the next normalized prediction must be wrong
on every continuation.

The native positive polynomial `phi(a)=a+a^2` has both positive curvature and
`phi'(0)=1`. Its linear term supplies a recovery direction at a zero
amplitude whenever the relevant output multiplier is positive; its quadratic
term supplies moment propagation. Removing either term removes the
corresponding property. Degree two is the smallest polynomial degree with
both properties; no uniqueness, globally nonabsorbing learner or optimality
claim is made. Shared multipliers, projection, range and complete state
still matter. This is an algebraic use of existing native SUM/PRODUCT, not
an external regularizer, positive clipping floor or an architecture menu.

For `a_h=1` and the two-event control, let `t=3*eta/10`,
`s=eta/(10+4*t^2)`. At rates small enough that projection is inactive,

`P(matching endpoint) = 1/2 + 24*t*s /
  (2+4*(2+t^2+9*s^2+4*t^2*s^2))`.

The first amplitude is `1+t*s_a*chi_e`; the second adds
`s*(3+2*t*s_a*chi_e)*s_b*chi_f`. Applying `a+a^2` gives the path coefficient
`12*t*s*s_a*s_b`, proving the formula. At eta1 this predicts
20289979/35917958, about0.56490. The pure-square value is larger in this
control; a recovery direction alone does not imply better risk. A separate
rate4 projection control eliminates two amplitudes and revives both on the
next opposite label. This establishes that concrete recovery, not a global
escape theorem.

## 6. Minimal audit and its actual boundary

Run
`python -B experiments/adaptive_uncertainty/correlation_control.py`.
The control explicitly validates all four native graphs, differentiates
with an independent forward-mode oracle and checks all four two-label
histories at rates1/8 and1, both unrounded and grid16:64 combinations, plus two projection controls.
A separate scalar binary64 graph interpreter and exact half/single rounded
graph interpreter check their corresponding arithmetic trajectories. No Torch import or target
worker is needed or claimed.

For labels(0,0), the grid16 quadratic predictions are:

| Rate | Exact reference | Rounded AMP stored-mass probability |
|---|---|---|
| 1/8 | 6487064613/12914455511 | 773/1539 |
| 1 | 18312805197/29516729138 | 2183/3519 |

The mixed-polynomial grid16 control predicts21546918333/42997186630 at
rate1/8 and25981558417/45993308790 at rate1, with rounded AMP probabilities
2568/5125 and1549/2742. Pair-local and linear controls remain exactly1/2 in
all checked cases. The
small exact conditional posterior check gives189/250 after both labels,
including either orientation. The code retains no weights or bulk history.

The explicit n3 graphs have the following sizes, including every native SUM
coefficient. These are costs of these witnesses, not resource lower bounds.

| Graph | Nodes | SUMs | PRODUCTs | Edges | Slots |
|---|---:|---:|---:|---:|---:|
| Pair-local v4 | 17 | 2 | 9 | 33 | 7 |
| Linear assignment mixture | 25 | 10 | 9 | 53 | 6 |
| Quadratic assignment mixture | 33 | 10 | 17 | 69 | 6 |
| Linear-plus-quadratic mixture | 33 | 10 | 17 | 77 | 6 |

The mixture controls exceed the corresponding RN-4 node cap. No resource
admission, legal installed state, broad soft-context identity or exponential
family feasibility is inferred from these scalar checks. An experiment must
separately register an owned reachable construction, complete learner,
range/AMP bridge and immutable resource envelope before inspecting its new
outcomes. RN-4 is not retuned or selectively replaced by this control.
