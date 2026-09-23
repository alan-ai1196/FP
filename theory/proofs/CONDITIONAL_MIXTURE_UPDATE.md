# Conditional posterior closure does not imply native learner equivalence

Status: **PROVED FOR FIXED BLOCK-SCALED PARAMETERS; EXACT NATIVE AND
BINARY64 COUNTEREXAMPLES**. This attacks a tempting use of the tractable
structure left open by the [unknown-noise hardness result](UNKNOWN_NOISE_DECODING.md).
A conditional SUM of PRODUCTs can contain the exact posterior family and
still execute the wrong update under the existing global simplex U.
This is a parameterization/learner obstruction, not missing posterior
capacity, a new semantic action or a counterexample to Foundation R4.

## 1. A statistically closed conditional family

Let J>=2 be the number of noise hypotheses, with positive gate probabilities
pi_j. Conditional on j, let m categorical factors have positive distributions
q_(j,a). The represented law is

`P(j,z) = pi_j PRODUCT_a q_(j,a)(z_a)`.

An observation of factor a has positive likelihood ell_(j,b) when z_a=b.
Write

`l_j=SUM_b q_(j,a,b) ell_(j,b)`, `p=SUM_j pi_j l_j`,
`rho_j=pi_j l_j/p`, `q*_(j,a,b)=q_(j,a,b) ell_(j,b)/l_j`. (1)

Exact Bayes replaces pi by rho and the queried conditional rows by q*,
leaving every other row unchanged. Thus this family is closed under every
finite sequence of such local observations. Noise-only diagonal observations
update pi and leave all conditional rows unchanged. For relation queries on
a forest, the conditional factors can be independent edge-parity coordinates,
as in the [query-matroid result](FACTOR_QUERY_MATROID.md). General cross-factor
queries need not have this closure. One binary factor already suffices for
the obstruction below, within the n2 unknown-noise model.

For rates eta_j, the local binary likelihood is 1-eta_j for the matching
label and eta_j otherwise. The fixed rate set and its prior are declared
model data. No trained posterior is a source and no row update in (1) is
assumed to be an authorized native operation.

## 2. What the ordinary compact native graph actually does

There are b=1+Jm categorical parameter blocks: the gate and all conditional
rows. Put them in one selected simplex with each block mass 1/b. The decoded
distributions are b times their selected parameters. Use the existing
unit-event CE simplex learner, with one scalar learning rate tau.

A positive native realization is available. Choose an integer S so that
every S ell is an integer at least one. With bases (1,1), form excess
coefficients S ell-1. For query a, each term contains a gate coordinate, a
queried conditional coordinate, and the SUM of every other conditional row.
Those inactive sums equal one but must remain in the ambient graph. Shared
prefix/suffix PRODUCTs emit them with O(Jm) graph size for fixed likelihood
coefficients. The complete one-hot source domain includes every factor query
and a diagonal query. All source, fixed-feature and selected slots are real
native coordinates, with their full caches and gradients retained.

Equivalently, introduce independent auxiliary variables X_(j,a) for every
conditional row, as well as the gate J. The graph's likelihood on their full
Cartesian product is ell_(J,X_(J,a)). It has the same current forecast as (1),
but the product parameterization contains additional auxiliary variables.
The coefficient columns sum to S-2, so the existing
[native marginal-update theorem](FACTOR_SIMPLEX_POSTERIOR.md) applies to this
actual multihomogeneous graph, including its ambient normalizer derivative.

Put alpha=b tau. Whenever the resulting native step is nonnegative, it gives

`pi'_j = (1-alpha) pi_j + alpha rho_j`,
`q'_(j,a) = q_(j,a) + alpha rho_j (q*_(j,a)-q_(j,a))`. (2)

All unqueried rows remain unchanged. At the usual tau=1/b, the gate update
is exact, but each queried conditional update is damped by rho_j. Positivity
ensures 0<rho_j<1. Unless that row's likelihood is uninformative, q' differs
from q*. For 0<=alpha<=1 positivity is automatic; larger alpha can refuse
and is not licensed by the formula alone.

For proof, the posterior marginal of auxiliary X_(j,a) is
`(1-rho_j) q_(j,a)+rho_j q*_(j,a)`: conditioned on gate j it is updated, and
conditioned on every other gate it is untouched. The native product step
retains that marginal. It loses the correlation between the gate and which
auxiliary variable was updated. This is the product projection already
derived in FP, not a new regularizer or externally added projection rule.
The broader approximation framework is classical; see
[Minka (2001), section 2](https://tminka.github.io/papers/ep/minka-ep-uai.pdf).
Here the distinction is between closure of the intended conditional family
and the actual optimizer on its chosen coordinates.

**A strict predictive discrepancy.** At alpha=1, repeat the same query and
label once. The exact conditional and native successors have forecast gap

`p_exact_next - p_native_next
 = SUM_j rho_j (1-rho_j) Var_(q_(j,a))(ell_j) / l_j`. (3)

Indeed, the component's repeated-label likelihood increases from l_j to
`SUM_b q_b ell_b^2/l_j = l_j+Var_q(ell)/l_j`. Substitute (2) into its next
forecast and subtract. Every term is nonnegative; with positive conditional
priors and informative noise it is strictly positive. This supplies a legal
next-query distinction, rather than just different hidden parameters.

## 3. Ambient graph changes and fixed block masses cannot repair the step

The preceding calculation uses a specific positive emitter. A more general
necessary condition rules out repairing its exact conditional interpretation
by changing the graph's off-invariant extension.

For one conditional factor, choose arbitrary fixed positive block masses
lambda_0,...,lambda_J summing to one. Store

`theta_(0,j)=lambda_0 pi_j`, `theta_(j,b)=lambda_j q_(j,b)`.

Suppose a differentiable native readout represents the forecast p in (1)
throughout this positive conditional-parameter manifold. Suppose its native
simplex step preserves these block masses and performs the exact updates
in (1). The actual CE gradient g then has tangent differences

`g_(0,j)-g_(0,k) = -(l_j-l_k)/(lambda_0 p)`,
`g_(j,b)-g_(j,c) = -pi_j(ell_(j,b)-ell_(j,c))/(lambda_j p)`. (4)

Only values of the readout on the manifold are used to derive (4). An
arbitrary normal derivative or common positive mass factor cannot change
these tangent differences. The full ambient derivatives still belong to the
complete learner; this argument does not erase or replace them.

The actual update multiplier is `1-tau(g_i-SUM theta g)`. Its explicit
global normalization is exactly one in exact arithmetic; negative entries
are refused, not repaired by another projection. Subtract multipliers for
two entries in the same block. Exact Bayes and (4) force

`tau=lambda_0` if the gate is informative (`l_j != l_k` for some j,k),
`lambda_j=tau rho_j` for each informative conditional row. (5)

These conditions are necessary, not a sufficiency certificate. Different
normal derivatives can also cause block-mass drift. They are independent of
the particular SUM/PRODUCT emission, provided it really represents the
conditional law on the declared positive manifold. Learning an arbitrary
finite orbit with another forecast off that orbit is a different claim;
the [reachable-orbit caveat](NORMALIZED_LIKELIHOOD_CHARACTERIZATION.md#5-attack-the-scope-an-informative-reachable-orbit-need-not-be-affine-globally)
must not be discarded.

**Two-event obstruction for every fixed choice of block masses.** Start
with equal gate weights and fair binary rows at noise rates 1/10 and 1/4.
Observe the same local label0 twice. At the first event rho=(1/2,1/2), and
both rows are informative. Equation (5) forces lambda_1=lambda_2. If the
first update is exact, the next rows are (9/10,1/10) and (3/4,1/4). Their
next likelihoods are 41/50 and 5/8, giving

`rho_after_second = (164/289,125/289)`.

Equation (5) would now require `lambda_1/lambda_2=164/125`, a contradiction.
This remains impossible even if one global tau is changed between events.
For a fixed tau, the first row conditions plus the second informative gate
also force tau=lambda_0=1/2 and lambda_1=lambda_2=1/4, whereas the second
conditional step needs masses (82/289,125/578).

Thus this fixed block-scaled conditional parameterization cannot realize
the exact two-event Bayesian continuation by any scalar-rate native step
whose readout has the stated conditional interpretation. Statistical closure
alone is not an implementation relation for the same U.

## 4. Native witnesses and the strong joint control

For equal block masses and tau=1/3, the actual positive Program after one
label0 has gate (1/2,1/2) and conditional rows

`(7/10,3/10)`, `(5/8,3/8)`.

Its next same-label forecast is 489/800. Exact joint Bayes instead has rows
`(9/10,1/10)`, `(3/4,1/4)` and forecast 289/400. The gap is 89/800, exactly (3).
Every gradient coordinate and the unfinished update are checked before the
commit. There is no arithmetic refusal or omitted fixed-feature derivative.

An increased fixed rate tau=2/3 makes the first full conditional update
exact in this fair example. It fails on the second event without leaving
the nonnegative domain: its gate becomes (367/578,211/578) rather than
(164/289,125/289). Its next forecast is 27499093/33408400 rather than 467/578.
The signed exact-minus-native gap is -506493/33408400. Fixing the first event
by increasing one learning rate does not supply a whole-history solution.

The comparator is the full joint native learner, not a weakened factor
baseline. With two conditional binary factors, every one of the 258 prefixes
of length 1..3 from the three-query/two-label alphabet agrees exactly with
the analytic conditional Bayes state. Each of these 258 actual native
predict/observe/commit triples checks full caches, all gradients, weights,
empty committed accumulators and clocks. The conditional family therefore
has the required statistical capacity on the complete declared local domain.

Two independent executed binary64 trajectories retain 13 phases in total.
Their complete-state/cache/probability relations to the exact wrong learner
pass at 1e-10 tolerance; maximum errors are 1/281474976710656 and
9/2251799813685248. The forecast discrepancies above are mathematical
learner differences and persist in ordinary finite precision.

## 5. Evidence and consequence for the compiler

Run `python -X utf8 -B experiments/joint_uncertainty/conditional_mixture_update.py --write`.
The [minimal artifact](../../evidence/minimal/FP_CONDITIONAL_MIXTURE_UPDATE.json)
retains the witnesses and aggregate evidence. In addition to the 258 exact
joint control updates and three witness updates, 672 native triples cover
two/three rates, one/two conditional factors, nonuniform priors, every local
query including the diagonal, both labels and two learning-rate scales.
An independent augmented tensor sum checks selected derivatives; forward
dual propagation checks the full fixed-feature derivative. Both complete
learner boundaries and the predictive identity (3) are checked. Total native
triples are 933. No Torch is imported and no device job is run.

The obstruction concerns this parameterization and optimizer, not every
compact encoding. Joint likelihood counts and the general rational decoder
remain valid routes to the original native trajectory. A conditional
factorization may also serve as a paid internal algorithm to decode that
trajectory if all complete-state and future-continuation obligations are
proved; it cannot silently replace the native Program and reuse its U.
No per-component learning-rate mechanism, conditional optimizer, semantic
architecture action or new physical identity is introduced here.

The next structural decoder should operate from the retained joint evidence
and prove its relation to the existing native learner. These results issue
no Runtime certificate, model superiority claim, full indexed release or
Foundation/ERC-1 change.
