# PRODUCT beliefs under the native simplex gradient

Status: **PROVED, SCOPED; EXACT NATIVE AUDIT AND COUNTEREXAMPLES**.
This is a learner law for a different parameterization of a product belief.
It uses the existing positive SUM/PRODUCT grammar and registered simplex U.
It changes neither Foundation R4 nor ERC-1, and issues no Runtime, AMP,
installation or complete-class certificate. The running model protocols
remain unchanged.

The [world-slot incidence lower bound](POSITIVE_PAIR_MARGINAL_CIRCUIT.md)
does not prohibit alternative learners with fewer parameters. Here such a
learner is exact for an observation family that preserves independence.
The same calculation identifies precisely the correlation it loses outside
that family. In particular, it cannot replace the current all-pair learner.

## 1. Declared state and native masses

There are m>=1 categorical factors with sizes k_1,...,k_m. All selected
parameters belong to **one** registered simplex, as the existing U requires.
Partition them into blocks theta_j, initialize each block with mass1/m, and
write `q_jb = m*theta_jb`. Thus every q_j is a categorical distribution and
the represented joint law is `Q(z)=PRODUCT_j q_j,z_j`. Unselected feature
parameters are fixed. There is no delayed state, the update unit is1, and
the gradient accumulator is empty at each complete unit boundary.

For a legal source row x, suppose the actual native excess heads are the
multilinear polynomial

`A_y(theta) = SUM_z c_y(z;x) * PRODUCT_j q_j,z_j`,

with fixed nonnegative coefficients, and the actual readout is
`M_y=beta_y+A_y`, beta_y>0. Assume the complete coefficient columns satisfy
`SUM_y c_y(z;x)=C(x)` independently of z. Put B=SUM_y beta_y. On the block
invariant the total mass is B+C and the forecast is the mixture under Q of
the fixed normalized expert likelihoods

`ell_y(z;x) = [beta_y+c_y(z;x)] / [B+C(x)]`.

These are substantive hypotheses about the Program and its **complete legal
source domain**. Coefficients are not supplied posterior values or free
numeric sources. Section4 constructs an actual compact native example.
The theorem does not assert that an arbitrary dense tensor can be emitted
or evaluated with a small graph.

## 2. Derive the update, including the ambient normalizer

Fix an observation y and suppress x. Let A=A_y and
`A_jb=SUM_{z_-j} c_y(b,z_-j)*PRODUCT_{i!=j} q_i,z_i`.
This polynomial definition also works when q_jb=0; it never divides by a
zero marginal. Define `h=C/(B+C)-A/M_y`.

The actual ambient CE gradient in selected slot(j,b) is

`G_jb = m * [C/(B+C) - A_jb/M_y]`.

Indeed, off the block invariant the total mass is
`B+C*PRODUCT_j S_j`, where `S_j=SUM_b q_jb`. Its ambient derivative at
S_j=1 is mC, even though its value along the invariant is constant. Also
`SUM_b q_jb*A_jb=A`, so the existing global weighted mean is

`mu = SUM_jb theta_jb*G_jb = m*h`.

**Native marginal-update theorem.** At rate eta=1/m the existing U gives

`theta'_jb = theta_jb * [beta_y+A_jb] / M_y`.

This follows by substituting G and mu in
`theta'_jb=theta_jb*[1-eta*(G_jb-mu)]`. All coordinates are nonnegative,
each block still sums to1/m, and the actual global normalization is exactly1.
Consequently

`q'_jb = Pr_{P}[Z_j=b]`,

where `P(z)=Q(z)*ell_y(z)/SUM_v Q(v)*ell_y(v)` is the exact joint posterior
formed from the **current product prior**. This is not a claim that Q was
the exact posterior of all earlier observations.

More generally, for 0<=eta<=1/m the same calculation gives
`q'_j=(1-m*eta)*q_j + m*eta*P_j`. Thus an informative event forces eta=1/m
if its full marginal update is required. The rate is derived from the
parameterization, rather than selected by a posterior helper.

The equal block masses are also meaningful. In the analogous fixed scaling
`q_j=theta_j/lambda_j`, lambda_j>0 and SUM_j lambda_j=1, subtracting the
update multipliers for two informative values in block j forces
`eta/lambda_j=1`. If every block has a legal informative query, one global
rate therefore forces all lambda_j=eta=1/m. This is a uniqueness statement
within this parameterization and this U, not among other possible learners.

This does not contradict the [distribution-wide unit-rate characterization](NORMALIZED_LIKELIHOOD_CHARACTERIZATION.md).
Here the claim holds on the proper invariant with each block mass1/m,
rather than throughout the global selected simplex, and the slots represent
factor marginals rather than separate joint-world probabilities.

## 3. Exactness boundary and the lost information

For positive factor priors the product of the posterior marginals is the
unique product distribution R minimizing `KL(P || R)`. In fact

`KL(P || PRODUCT_j r_j) = KL(P || PRODUCT_j P_j) + SUM_j KL(P_j || r_j)`.

Expanding the finite sums proves this identity. This describes what the
native update already does; no KL penalty or projection routine is added.
It is classical assumed-density filtering with a product approximation;
see [Minka (2001), sections2 and4](https://tminka.github.io/papers/ep/minka-ep-uai.pdf).
The contribution here is its derivation from the actual FP ambient CE
gradient, one global simplex, block scaling and finite native step.

**Closure theorem.** For a positive product prior, the exact posterior P
factorizes across the same blocks iff the positive likelihood tensor for
that event is multiplicatively separable across them:

`ell_y(z;x) = a * PRODUCT_j f_j(z_j)`, a>0, f_j>0.

Sufficiency follows by multiplying factors. For necessity divide a proposed
product P by the strictly positive product Q; their ratio, up to the
normalizing scalar, is ell_y. Therefore, from a positive product initializer,
the native learner retains the exact **joint** posterior after every legal
finite history iff every legal observation likelihood has this property.
Single-factor observations suffice, but the statement also allows general
separable likelihoods. On a simplex face the condition concerns its support.
It is not a necessity theorem for arbitrary forecast-equivalent encodings.

The update is also a classical positive-polynomial growth transformation.
The homogeneous polynomial
`L(q)=SUM_z [beta_y+c_y(z)]*PRODUCT_j q_j,z_j`
has block-normalized derivative update `q'_jb=q_jb*(partial_jb L)/L` on
the product simplex, exactly the formula above. See
[Baum and Sell (1968), section1](https://msp.org/pjm/1968/27-2/pjm-v27-n2-p01-p.pdf).
This connection gives no full-history inference guarantee: maximizing one
event likelihood and preserving its joint posterior are different claims.

**Two-factor counterexample.** Start with two independent fair bits and
observe equality with noise1/10. The posterior, in00/01/10/11 order, is
`(9/20,1/20,1/20,9/20)`. Both marginals stay fair. The native product learner
therefore remains at its initializer and forecasts1/2 on the next same query;
whole-history Bayes forecasts41/50. In the audited tensor Program the entire
gradient is zero, so changing the learning rate cannot repair this step.
The failure is correlation loss, not arithmetic uncertainty or search cost.

**Consequence for the present relation task.** Fix the original anchored
coordinates z_1,...,z_(n-1), and consider any product over disjoint blocks of
those coordinates. A legal noisy pair query between coordinates in different
blocks has the likelihood slice `[[9,1],[1,9]]` up to a common scalar. Its
determinant80 is nonzero, so it cannot separate. All non-anchor pairs are
legal in the current full domain. For n>=3, exact joint closure in this
fixed-coordinate product family therefore requires one block containing all
n-1 bits, with2^(n-1) categorical entries. More generally the connected
components of the query graph on the free coordinates must each lie in a
block; queries incident to the fixed anchor are already local. This is about all permitted
future queries, not just edges already observed. It supplies no lower bound
against different coordinates, compressed histories or arbitrary learners.

The separate [query-matroid theorem](FACTOR_QUERY_MATROID.md) now extends
this closure obstruction to every fixed bijection into categorical product
factors, including nonlinear coordinates. The complete all-pair family still
forces one2^(n-1)-category factor. Restricted query families behave differently:
forest edge-parity coordinates remain independent, and the irreducible ranks
are cycle-matroid component ranks. This extension still supplies no lower
bound against compact encoded factors or arbitrary nonproduct learners.

## 4. A linear-size positive native realization

For m independent binary factors, let the complete source domain consist of
the m one-hot rows x_j, selecting a factor to observe through noise1/10.
Use bases(1,1), fixed feature slot t=1,2m selected slots, and Gamma_jb=q_jb/m.
The Program constructs L=SUM_j t*x_j, hence L=1 on this domain. A SUM of
m copies of L constructs m; three doubling SUMs construct8. Selected
singleton SUMs construct q_jb=m*theta_jb. Define S_j=q_j0+q_j1 using native
SUMs and build all leave-one-out products from shared prefix/suffix PRODUCTs.
The excess heads, at t=1, are

`A_y = 8 * SUM_j x_j*q_jy*PRODUCT_{i!=j} S_i`.

On the invariant they give `M_y=1+8*q_jy` for selected j. They also retain
the degree-m ambient polynomial required in section2. No fitted initializer,
latent target, parameter-valued input, explicit posterior or new optimizer
action enters the construction. Each observation updates only the selected
factor's represented distribution; the others remain unchanged.

The concrete shared implementation in the audit uses:

| Native quantity | Count |
| --- | ---: |
| selected parameters, plus fixed feature |2m+1|
| nodes |11m+9|
| SUMs |3m+7|
| PRODUCTs |7m+2|
| SUM incidences |8m+6|
| all incidences |22m+10|

It represents2^m joint worlds with linear graph size for this observation
family. These are actual graph counts, not constant runtime or precision
costs. The complete gradients, numeric bit lengths, resource ownership and
future construction obligations still belong to the learner. The graph is
not asserted count-optimal; no static PRODUCT/range study is reopened.

## 5. A value-one factor cannot be erased from this learner

Every inactive S_i equals1 along the intact invariant. Deleting them would
preserve all current forecasts there. Nevertheless it changes the ambient
gradient and thus the actual future U, because U is defined on one global
simplex, rather than separately projecting each block.

With query j, the intact inactive selected gradients are m*h, exactly their
global mean. After deleting the inactive factors they are0; the new global
mean is h. At rate1/m, every inactive theta is multiplied by `1+h/m`, so
its block mass drifts whenever h!=0. At a fair initializer h=0, hiding the
error through the first complete commit.

The exact two-factor witness observes label0 of factor0 twice. Both graphs
forecast1/2 then41/50 and have identical complete state after the first
commit. On the second event the intact selected gradient is
`(-72/205,8/5,-32/205,-32/205)`, while the erased graph has
`(-72/205,8/5,0,0)`. After committing, its block masses are
`(213/410,197/410)` instead of(1/2,1/2). Its third forecast is9413/10570
instead of the exact73/82. Fixed-slot gradients are also retained and checked
for each actual graph, rather than replaced with tangent derivatives.

Thus agreement of functions on a reachable invariant does not alone prove
equivalence of gradient-based learners. This is an instance of FP's existing
future-information principle, not a counterexample to Foundation R4.

## 6. Exact evidence and limits

Run `python -B experiments/joint_uncertainty/factor_simplex_posterior.py`.
The retained [minimal audit](../../evidence/minimal/FP_FACTOR_SIMPLEX_POSTERIOR.json)
contains counts and the counterexamples, without trajectory dumps:

- 294 native marginal updates for varied tensor columns, binary/ternary
 factors, nonuniform bases, positive priors and every joint vertex.
- 1,348 further native updates exhausting81 two-bit coefficient tables and
 256 three-bit tables, both labels and two positive priors. All closure
 decisions agree with independently computed flattening minors;92 of these
 posterior cases factorize and1,256 retain correlations.
- 1,254 native observe/commit pairs along exhaustive single-factor histories
 and six two-pass profile/clock-attachment cases. An independent full-joint
 Bayesian oracle agrees throughout. All2,896 updates in these three groups
 check both complete learner boundaries, including every gradient coordinate;
 the fixed-slot derivative uses independent forward dual propagation.
- 36 additional native checks verify the derived damped updates and rate.
- Both explicit failure witnesses and actual graph counts through m64.

These exact Fraction checks use the registered32768-bit native bound. They
are arithmetic evidence for the proved claims, not physical execution or
Compiler equivalence. Nothing is installed or erased from a Runtime. The
current all-pair CPU/AMP learners, strong controls and model runs retain their
complete states and their existing decision-class status.
