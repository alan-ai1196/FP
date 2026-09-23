# Acquiring the noise rate does not remove worst-case forecast complexity

Status: **PROVED, SCOPED CONDITIONAL COMPLEXITY LAW; EXACT FINITE AUDIT**.
This joins the [noise acquisition/state law](NOISE_ACQUISITION_AND_STATE.md)
to the [known-rate forecast reduction](FORECAST_DECODING_COMPLEXITY.md).
The noise rate remains a latent variable throughout. Calibration uses legal
ordinary observations, and its guarantee covers every bounded future word.
No parameter is supplied by an oracle and no rate/world state is deleted.

## 1. Model and sharp error threshold

Fix a finite set of distinct rational rates

`0 < eta_0 < eta_1 < ... < eta_(r-1) < 1/2`, `r >= 2`,

and fixed positive rational prior pi on them. Independently initialize n fair
latent bits, anchored at z0=0. A pair query (i,j), including i=j, returns its
parity through conditionally independent noise at the single shared rate eta.
All finite query/label words are legal and have positive probability. This
is the existing native joint rate/world simplex learner and complete source
interface, with no new optimizer or semantic action.

Let p_h(i,j) be its joint posterior probability of the next label1. It retains
the posterior on eta as well as the conditional world posteriors.

**Theorem.** Fix rational `0 <= e < 1/2-eta_0`. If a uniform deterministic
decoder always returns a rational p_hat with

`|p_hat-p_h(i,j)| <= e`

for every n, every legal finite history h and every pair, in time polynomial
in n+|h|, then P=NP. At `e=1/2-eta_0`, the constant decoder p_hat=1/2 works.
Thus the worst-case uniform accuracy threshold is sharp, conditional on
P!=NP. For the current prior on{1/10,1/4}, the threshold is2/5.

The model family is given compactly by n and these fixed likelihood rules.
Polynomial time in its exponentially expanded native world graph is not
excluded. The rates, their separations and the positive prior are constants
of the theorem; allowing them to vary with input bit length needs a separate
bound. The theorem concerns a decoder that resolves every input, including
rare histories. It permits no hidden exponential preprocessing or unpaid
forecast oracle. A bounded solver may instead return UNRESOLVED.

## 2. A calibration prefix that survives every short continuation

Here is the elementary concentration lemma used in the reduction. Suppose
one observation c has likelihood a_j under rate j, independent of its latent
world, with `a_0 > max_(j>0) a_j > 0`. Suppose every later world-conditional
label likelihood is in[lambda,1], with lambda>0. Set

`q=max_(j>0) a_j/a_0 < 1`, `O=(1-pi_0)/pi_0`.

After R copies of c and any continuation h of length t<=L, the posterior
odds against component0 satisfy

`beta_h/(1-beta_h) <= O q^R lambda^(-t) <= O q^R lambda^(-L)`. (1)

Indeed, c multiplies each component prior by a_j^R and leaves its conditional
world prior intact. Its continuation's marginal likelihood m_j(h) is a convex
average of positive products, so `lambda^t <= m_j(h) <= 1`. Bayes' rule gives
the claimed odds bound. Query choices may depend on preceding labels: the
argument holds separately on every legal realized word, uniformly. It does
not condition a fixed-graph acquisition formula on a data-selected graph.

To ensure beta_h<=delta for every such continuation, choose R so that

`O q^R <= [delta/(1-delta)] lambda^L`. (2)

For fixed q, lambda and prior, exact rational multiplication finds such R in
`O(L+log(1/delta)+1)` iterations. The integers involved have polynomial bit
length in L plus the encoding length of delta. No float logarithm or sampling
oracle is needed. In the reduction delta is itself a fixed rational constant.

In the joint-noise learner take c to be query(0,0), label0. Its parity is
always zero, so `a_j=1-eta_j`, `q=(1-eta_1)/(1-eta_0)` and `lambda=eta_0`.
This uses the existing diagonal source; it does not grant access to eta.
Conditioned on component0, the calibration prefix leaves every anchored
world equally likely. Every subsequent joint forecast differs from its
component0 forecast by at most beta_h, since it is their convex mixture.

The bounded continuation is essential. For the equal prior on{1/10,1/4},
17 diagonal-zero observations reduce the other-rate posterior to
`762939453125/17689598897861 < 1/20`. Four subsequent diagonal-one observations
raise it to `476837158203125/747663709318901 > 1/2`. A calibrated present state
does not justify deleting that rate for unrestricted futures. The actual
implementation keeps the entire joint state; (1) is a scoped bound only.

## 3. A polynomial reduction using acquired rather than supplied noise

Take a simple unweighted graph G on n vertices, with m edges, cut size C(z)
and optimum C*. Simple unweighted MAX CUT is NP-complete; the primary source
is [Garey, Johnson and Stockmeyer (1976)](https://www.sciencedirect.com/science/article/pii/0304397576900591).
The existing known-rate reduction supplies the combinatorial step. Here the
calibration prefix makes that step valid for the actual joint learner.

Put

`rho=1-2 eta_0`, `delta=(rho/2-e)/2 > 0`,
`gamma=1/2-(e+delta)/rho = delta/rho > 0`,
`b=(1-eta_0)/eta_0 > 1`.

Choose the least M>=0 with `gamma b^M >= 2^n`, and declare
`L=M(m+n-1)`. Choose R by(2) for that L and delta. First observe R diagonal
zeros. Then observe M copies of label1 on every edge of G. At each i=1,...,n-1,
ask for the joint forecast on(0,i), choose label b_i=1 when p_hat>=1/2 and
0 otherwise, and observe M copies of that label on the same anchor pair.
There are at most L observations after calibration, on every possible branch.

All exact joint forecasts remain delta-close to the conditional component0
forecast, so the assumed decoder is an (e+delta)-accurate decoder along
this whole reduction. Its conditional world weights after s anchor choices
are exactly proportional to

`b^(M [C(z)+F_s(z)])`,

where F_s counts satisfied chosen anchor relations. Diagonal calibration
contributes a world-independent factor and therefore changes none of these
conditional odds. This cancellation is within one conditioned component;
the full joint learner never normalizes away the evidence between rates.

Assume the prefix choices agree with at least one maximum cut. A good world
has score C*+s; every other world has score at most C*+s-1. There are
K=2^(n-1) worlds, so bad conditional mass is at most

`K/b^M <= gamma/2 < gamma`. (3)

Let u be the component0 posterior mass with z_i=1. Its forecast is
eta_0+rho u. The threshold decision implies that the selected branch has
component0 mass at least gamma (strictly greater for a zero decision).
By(3) it contains a good world. Induction preserves a maximum cut, and the
final n-1 decisions specify one completely.

For fixed rates, prior and e, M=O(n), L=O(n^3), and R=O(L+1). Constructing
the actual word, all calibration arithmetic and the n-1 assumed decoder
queries therefore takes polynomial time. The output cut solves MAX CUT,
proving the theorem. This is a reduction among conditional forecast problems,
not a branch-invariant experiment protocol or permission for Runtime to
choose its own targets. Every word used is legal; none is asserted typical.

At the boundary e=rho/2, every joint forecast lies in[eta_0,1-eta_0], so1/2
is a valid constant answer. At n3 with the single edge(1,2), its tie rule
chooses z1=z2=1 and misses the optimum. The positive gamma margin cannot be
dropped. As in the known-rate proof, a randomized polynomial decoder with
uniform per-input success probability at least2/3 would imply NP=RP after
median amplification and exact verification of the returned cut.

## 4. A paid upper, and the information/computation distinction

Compact sufficient state remains the already proved(T,d,s), with
`m_z=[T+s+SUM d_ij (-1)^(z_i XOR z_j)]/2` matching labels in world z.
Choose a common likelihood denominator B for all fixed rates and a common
prior denominator P. Define positive integers

`a_j=B eta_j`, `b_j=B(1-eta_j)`, `k_j=P pi_j`.

The exact joint weights, on one common scale, are

`A_(j,z)=k_j a_j^(T-m_z) b_j^m_z`.

They have O(T+1) bits for this fixed family. Stream them into a total and
a query-weighted total, multiplying each by a_j or b_j for the requested
label. Divide the second total by B times the first. Both totals have
O(T+n+1) bits. Enumerating r2^(n-1) pairs yields an exact forecast in
`2^n poly(n,T)` bit operations and `poly(n,T)` working space. Every
rate-dependent common factor remains. This supplies a constructive upper;
P!=NP does not prove this exponential time is optimal.

The information law needs only O(n^2 log(T+1)) committed counter bits, but
uniformly resolving approximate inference below the stated threshold is
conditionally intractable. Cheap information storage, acquiring information
and decoding it are different costs. The physical general-rational component
is useful for explicit banks; it does not bypass this compact-family problem.
Complete native output size, provenance, pending gradients, host/device
ownership and precision still have separate obligations.

## 5. Exact audit and limits

Run `python -X utf8 -B experiments/joint_uncertainty/unknown_noise_decoding.py --write`.
The [minimal evidence](../../evidence/minimal/FP_UNKNOWN_NOISE_DECODING.json)
checks two rate/prior configurations, including a nonuniform three-rate prior.
All1,856 short continuation prefixes and10,854 pair forecasts satisfy the
concentration and mixture-error bounds. Ordered integer likelihood products
independently equal the(T,d,s) reconstruction at every checked state.

The reduction audit covers316 graph/error/prior settings: all simple graphs
on2..4 vertices at four errors for{1/10,1/4}, and all graphs on2..3 at two
errors for{1/8,1/5,1/3}. It explores every permitted threshold decision:
1,683 adaptive states,1,367 decisions and571 optimal terminal cuts. The
largest checked word has710 observations and largest weight4754 bits.
Two actual native trajectories execute186 complete cache/gradient/commit
triples, including176 ordinary calibration observations. These are functional
exact native executions; they issue no Runtime or physical certificate.

The unprotected-prefix counterexample is retained separately. The quantifier
over every continuation within its horizon, arbitrary n and polynomial
reduction follow from the proof, not these finite checks. No Torch/GPU,
new model run, average-case
hardness claim, all-history AMP guarantee or full indexed release is added.
The calibrated prefixes can be exceptionally unlikely. Forest information
and disjoint-cycle acquisition results retain their own different scopes.
Foundation R4 and ERC-1 are unchanged.

The subsequent [conditional-mixture update result](CONDITIONAL_MIXTURE_UPDATE.md)
attacks a proposed tractable representation. Conditional posterior closure
does not imply that replacing the Program by fixed-mass conditional blocks
preserves the native U. A paid structural decoder of the original joint
state remains a different implementation route. The subsequent
[shared-noise forest decoder](SHARED_NOISE_FACTOR_CLOSURE.md) supplies a
scoped positive exact algorithm and native relation for that route, without
Runtime ownership or an AMP backend.
