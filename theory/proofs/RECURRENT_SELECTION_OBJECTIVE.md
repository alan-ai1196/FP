# Endpoint fit is not causal evidence for a recurrent model

Status: **exact native counterexamples and a scoped information theorem,
with exhaustive small checks and functional CPU execution**. Foundation,
ERC-1, Runtime's objective and the existing target experiments are unchanged.
This constrains the interpretation of a future recurrent proposer; it does
not add a semantic action or invalidate the declared empirical objective.

## 1. The implemented objective has an explicit time scope

[`search.likelihood`](../../src/reference_compiler/fp_reference/search.py#L115)
evaluates every revealed historical record against the same complete frozen
learner endpoint. It does not advance that endpoint's delayed state between
records. Thus its product is

`L_endpoint = PROD_t f(theta_T,D_T,sources_t)[y_t]`.

The causal sequence product is instead

`L_sequence = PROD_t f(theta_t,D_t,sources_t)[y_t]`,

where each prediction precedes its target and its ordinary update. These
are distinct even at learning rate zero because delayed state can change.
For the known-prior posterior control within its full window, L_sequence
is the generative model's marginal likelihood. L_endpoint generally is not.

The implementation states this frozen-state objective explicitly. Its
historical search is allowed to use the already revealed training records.
There is no online lookahead bug in computing that objective after the
training cut. The error would be to relabel it as causal/Bayesian evidence,
fresh wealth, noise identification or an optimum for a different decision
class. Current prospective evidence still follows the actual fresh stream.

## 2. A two-observation native counterexample

Use the [native H2 posterior](NATIVE_RECURRENT_POSTERIOR.md) on two fair latent
bits with noise1/10, and reveal label0 twice on the same pair. Its actual
ordinary forecasts are1/2 then41/50, hence L_sequence=41/100.

At the endpoint, the lag1 state stage already contains the first label's
likelihood factor. Retrospectively evaluating the first stored source record
with that endpoint gives41/50; evaluating the second gives73/82. The
implemented frozen-endpoint likelihood is therefore73/100. All observations
were retained, all forecasts were causal when originally executed, and
theta never changed. No equality of these two score objects is available.

## 3. Forest labels contain no information about a common noise rate

Assume initially independent fair latent bits, fixed distinct undirected
off-diagonal query edges forming a forest, and one observation per edge.
Targets are independently flipped with common noise epsilon. For a forest
of m edges,

`P_epsilon(y_1,...,y_m | query forest) = 2^(-m)`

for every label vector and every epsilon in [0,1/2]. To prove this, root
each tree. The root bits and edge parities form independent fair bits under
the latent prior: assigning them determines exactly one vertex assignment.
The m queried parities are therefore uniform on all m-bit strings. XOR
with independent noise preserves that uniform distribution.

Consequently every noise hypothesis induces the same data distribution.
No decision rule based only on this information can distinguish two such
hypotheses; with any independent prior over epsilon, its posterior remains
that prior. More CPU, numerical precision or endpoint fitting cannot supply
the missing information. A claim to identify noise from these observations
must remain unresolved. This does not forbid selecting a provisional model,
reporting its actual empirical optimum or using subsequent fresh evidence.

The same conditional argument applies to a query rule that always joins
distinct current forest components and depends only on past observations
and independent randomness. It does not apply to a query choice carrying
extra information about epsilon. Repeated edges, diagonals and cycles also
fall outside the one-observation forest premise. In particular, RN-5 has
repeated training observations and is not covered by this impossibility.

## 4. Endpoint fit can prefer a noise hypothesis without identifying it

Consider n3,H2 and observations (01,0),(12,0). Use one common initializer
Gamma=(1,0,2,8), retaining every slot in every native model. Slot0 supplies
the unit. Positive readout/update terms select an available excess s from
slots1,2,3. The implied known noise is epsilon=1/(s+2), with likelihood
ratio1+s. All three initial graphs are legal in the same broad native
grammar/resource/initializer setting; only their SUM-edge slot choices
differ. The audit does not claim to have searched or certified that class.

| Selected excess s | Noise epsilon | Causal sequence likelihood | Frozen endpoint likelihood |
| --- | --- | --- | --- |
| 0 | 1/2 | 1/4 | 1/4 |
| 2 | 1/4 | 1/4 | 5/16 |
| 8 | 1/10 | 1/4 | 41/100 |

The first two queried parities are independent fair bits, so every causal
sequence likelihood is1/4. At the endpoint, the first record is reevaluated
with a state containing its label's factor. Its matching noisy probability
is `((1-epsilon)^2+epsilon^2)=(1+(1-2*epsilon)^2)/2`; the second queried
parity is still neutral. Thus L_endpoint=(1+(1-2*epsilon)^2)/4. Its strict
preference in this table is not a Bayesian noise-learning result.

This distinction matters for the next legal continuation. After those same
two labels, querying02 has probability189/250 of label0 under noise1/10,
but9/16 under noise1/4. The observed forest cannot decide which conditional
is appropriate without an additional noise premise, prior or information.
An informative future continuation can still use the distinction.

For a triangle with observed label signs sigma_e, direct latent summation
gives

`P_epsilon(labels on triangle) = [1 + PROD_e(sigma_e)*(1-2*epsilon)^3]/8`.

This follows by expanding the three factors: singleton/pair latent parity
moments vanish and the three-parity product is1. The distribution now
depends on epsilon. For three zeros, noise1/10 gives189/1000, whereas
noise1/4 gives9/64. This is distributional information, not exact recovery
or a population certificate from one observed triangle.

## 5. Evidence and implications for construction

Run `python -B experiments/joint_uncertainty/recurrent_selection.py`.
The independent full-assignment likelihood calculation checks47 forests
on n2 through n4,892 signed-forest/noise likelihoods and32 signed triangle
likelihoods. Four actual ReferenceCompilerRuntime controls execute only
ordinary contexts followed by labels. They retain all observations and all
four initializer slots, seal with28 independently replayed binary64 phases
in total, and reproduce the table and repeated-pair counterexample through
the existing search helper on the actual frozen endpoints.

The helper is used only as a read-only diagnostic and changes no Runtime
state or authority. These functional runs explicitly report their physical
host scope unresolved; they have no new source-bound host/GPU, class proof,
installation or fresh-evidence claim. The earlier source-bound posterior
control keeps its own narrower known-noise execution scope.

A proposer may use a legally acquired causal score to guide which native
program to build, while the declared search class retains its frozen-state
empirical objective. It must state those different roles. If the intended
decision class uses a trajectory objective, it needs the corresponding
explicit class definition and evidence, not a reinterpretation of the old
certificate. The known-noise initial model's successes do not establish
that the Compiler learned the noise or discovered that model from a forest.
