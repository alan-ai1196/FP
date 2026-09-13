# Balanced positive evidence retains learnable uncertainty

Status: **scoped proof; exact and source-bound CPU/CUDA audits at `803cdc2`**.
This attacks RN-3's fixed-graph learning obstruction without changing
Foundation R4 or ERC-1. It proposes another registered search algorithm over
the existing native syntax, initializer/profile endpoints and full class.

## 1. Prediction equality does not determine parameter directions

With positive base one, write the binary masses as `M_y = 1+e_y(theta,x)`.
At a uniform endpoint `M_0=M_1=M`, the target0 loss derivative is
`(grad e_1 - grad e_0)/(2M)`; target1 reverses its sign. Thus equal initialized
evidence is compatible with nonzero, label-sensitive derivatives. If the
heads have identical parameter derivatives, or both are the zero polynomial
on the query, first-order learning cannot distinguish the labels there.
Feasible projected directions and numerical/resource admission still matter.

RN-3's component-only graph is identically zero across original components.
Deleting the evidence made its uncertainty permanent under ordinary value
learning. The alternative below keeps separate balanced positive readouts.

## 2. A native construction from the same revealed constraints

Retain v3's empirical components and representative parity assignment `h`.
For each ordered token pair form the parameter-free native PRODUCT
`X_0i * X_1j`. On a one-hot query exactly one of these features is one.
There is no learned internal group-SUM scale.

Within one component, attach that feature to head `h_i xor h_j` using the
available initialized scale `a`. For each unordered pair of components
`{k,l}`, allocate two distinct available unit-initialized slots `u_kl,v_kl`,
separate from the within-component scale. Across these components, attach
the active feature to both heads: head y uses the coefficient indexed by
`y xor h_i xor h_j`. All terms and sharing use existing native SUM slots.

Initially the within-component masses are `(1+a,1)` up to parity, and the
cross-component masses are `(2,2)`. Therefore every initialized one-hot
prediction equals v3, including uniform cross uncertainty. The masses,
parameters, resource use and full learners are different; no equivalence
quotient or inherited evidence is authorized.

An initial cross observation with adjusted target0 has derivatives
`dL/du=-1/4`, `dL/dv=1/4`, with all other readout derivatives zero. A unit1
SGD step at rate1/8 gives `(u,v)=(33/32,31/32)`, hence probability65/128
on another query in the same component pair with matching adjusted parity.
The opposite target reverses the movement. Other component pairs and
within-component predictions are unaffected by this first update. This is
ordinary registered learning, not a Bayesian posterior update: after one
label the known diagnostic posterior would predict41/50, not65/128.

The explicit witness has `2n+n^2+2` nodes, two SUMs, `n^2` PRODUCTs and
`4n^2 - SUM_k |C_k|^2` edges. It needs `c(c-1)` distinct unit coefficients
plus a separate within scale, including every intervening initializer slot.
These are costs of one witness, not a lower bound or architectural optimum.
The original grammar already admits dense token-pair lookup products;
additional independent slots must actually be present in the declared
prefix. Insufficient slots or graph resources return unresolved, not a
weaker hidden parameter sharing rule or an exclusion of the full class.

The same exact reachable-scale likelihood comparison applies: initialized
cross predictions are uniform independently of `a`. Balanced intra-component
counts remain in the likelihood; source distinctions remain in the separate
categorical upper. The all-tied baseline can still close that upper without
constructing this alternative. Inconsistent strict cycles remain unresolved.

Scale feasibility and independent-slot allocation must be checked together.
For example, in prefix `(1,8,1)` with two components, reserving scale1 leaves
only one other unit, while scale8 leaves two. The solver must compare only
feasible choices; an infeasible best scalar fit cannot hide the available
scale8 construction. The audit checks 484 count/slot combinations, including
this coupling. A connected dense graph needs only its scale, not a unit slot.

## 3. Scope and resource pressure

The solver identity is `empirical-binary-relation-balanced-readout-v4` in
the existing immutable relation-source registration. The default remains v3
so historical and sparse-solver scopes do not change silently. These are
registered search algorithms, not new architecture actions: the same full
native grammar, constructor, initializer/profile paths and separate upper
remain authoritative. Runtime must prepay the quadratic emission work.

Nonzero learning also needs a declared feasible range. At scale8, a correct
within-component label has derivative `-1/90`; a positive step immediately
exceeds the old normalizer10 boundary. This is a resource/value-path refusal,
not a reason to bypass range checks or alter FP semantics. Endpoint audits
must retain that tight-cap failure and separately register any larger range
before executing the corresponding learner. ERC-1 explicitly makes numeric
budgets immutable per-run parameters rather than universal fixed constants.

Pairwise readout coefficients are not a posterior over latent global flips.
They need not satisfy all multi-component posterior consistency relations.
Finite data, slot/work/range caps, numerical projection and fresh evidence
can limit adaptive model quality. Actual owned construction, reference and
AMP trajectories, paired persistence and installation require their own
endpoint evidence; model-quality claims require strong adaptive controls
with matching revealed information. No such model result is asserted here.

## 4. Exact and owned endpoint checks

The exact audit covers 320 models, 7,320 initialized one-hot predictions,
7,072 cross-label derivative directions and 7,072 exact one-step responses.
It checks separate parameter coordinates across component pairs and retention
of the within-component scale. The default v3 exact suite still passes.

The CPU/CUDA endpoint cases cover both revealed orientations, installation
from an unresolved class, missing coefficient slots, prepaid quadratic work
refusal, and the old normalizer10 boundary. Positive cases use update unit1,
rate1/8, grid16, activation16 and normalizer18, with declared state/probability
tolerances1/100 on the separately executed numerical paths. Source-bound
full matrices follow the committed implementation; no endpoint pass implies
a new full 31-script baseline release or a model-quality result.

The tight-cap case exposes an audit limitation, not a Runtime loophole.
Runtime computes and retains both optimizer successors, then refuses their
publication when range fails. The old binary64 replayer incorrectly compared
the published root to the last computed phase. It now independently replays
all phases and checks the failed observation's published state against its
owned pre-target prediction cut. A forged promotion of staged successors is
rejected. Both CPU/CUDA tight-cap checks and the original full binary64 audit
pass; no unsafe successor is installed or discarded from the retained prefix.

The complete source-bound matrices at `803cdc2` pass six workers per path:
[CPU record](../../evidence/minimal/FP_BALANCED_UNCERTAINTY_CPU_AUDIT.json) and
[CUDA record](../../evidence/minimal/FP_BALANCED_UNCERTAINTY_CUDA_AUDIT.json).
Each replays1,960 binary64 phases, and the target matrix also replays1,960
actual CUDA phases. Observed binary64 state/probability maxima are about
4.58e-17/5.51e-17. CUDA maxima are5.31e-5 in state,0.003769 in native masses
and normalizers,5.54e-5 in normalized probabilities, and2.98e-8 in division.
These are measured errors, separately below the declared1/100 tolerance.
Maximum completed-job commits are41,385,984 CPU and2,393,673,728 CUDA bytes.
The two journals total25,883 bytes and retain no bulk phase history.

RN-4's committed runner registers all thirty attempts before new seed labels
are inspected. The exact adaptive posterior is checked against48 independent
full-joint conditional forecasts, including cycles and initially excluded
assignments under the conditioned law. Its Brier summaries enclose exact
per-query losses on a fixed48-bit grid rather than retaining a growing global
common denominator. These checks validate an experimental comparison; target
model execution and adaptive quality still require their own outcomes.
