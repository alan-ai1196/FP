# Shared-noise factor closure and exact positive forest decoding

Status: **PROVED, SCOPED; EXHAUSTIVE RE-ENCODING AND EXACT NATIVE AUDITS**.
One common unknown noise rate changes the independent-factor closure law:
even a forest query family forces all its queried parities and the rate
into one categorical factor, under every fixed bijective re-encoding that
starts with a positive product prior. The sharp category requirement is
J*2^r for J distinct rates and query rank r. This does not imply expensive
decoding. Positive integer forest inference computes the original joint
learner from its retained counts with polynomial arithmetic resources.

This extends the [known-noise query-matroid law](FACTOR_QUERY_MATROID.md).
It also closes a different escape route from the
[conditional-mixture update obstruction](CONDITIONAL_MIXTURE_UPDATE.md):
changing fixed independent latent coordinates cannot eliminate the shared
rate coupling. Conditional representations remain statistically possible;
their native optimizer and their use as internal decoders are separate.
No optimizer, architecture action, physical identity or release changes.

## 1. Binary likelihood closure requires one factor per query

Let Omega be a finite world set, with a strictly positive prior. Choose any
fixed bijection Omega <-> X_1 x ... x X_m under which that prior is a product.
No linearity, locality or efficient computability is assumed. A query e has
normalized binary likelihoods L_e(omega) and 1-L_e(omega), both positive.
Every finite sequence of legal queries and both possible labels is allowed.

**Binary closure lemma.** Exact posterior closure in these same independent
factors holds iff each L_e is a function of at most one factor.

For necessity, the two one-event posteriors must be products. Dividing each
by the positive product prior shows that both L_e and 1-L_e are positive
multiplicatively separable functions. Suppose L_e varies in two factors.
Fix all others, write the resulting 2-by-2 table as C a_i b_j, and choose
a_1!=a_2 and b_1!=b_2. The complementary table has determinant

`(1-C*a1*b1)(1-C*a2*b2) - (1-C*a1*b2)(1-C*a2*b1)
 = -C*(a1-a2)*(b1-b2) != 0`.

It cannot be separable, a contradiction. For sufficiency, each observation
multiplies only one factor, which can be normalized without changing any
other. Induction handles every finite history. Necessity already holds
at the initial positive product prior.

Both labels matter. For example L_0=(1,2,2,4)/10 on a 2-by-2 product is
separable, but the determinant for L_1 is -1/10. A checker that verifies
only one realized label can incorrectly claim closure for its legal future.
Unlike the earlier two-value lemma, L_e need not have just two distinct
values across worlds. The binary restriction is on the response alphabet.

The underlying independence/transitivity phenomenon is classical; see
Geiger and Heckerman, [*Separable and Transitive Graphoids*, section 4](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/Separable-and-Transitive-Graphoids.pdf).
The elementary determinant proof above covers arbitrary finite categorical
factor alphabets for this particular normalized binary observation setting.
No new general probability calculus is claimed.

**Shared-statistic consequence.** Suppose every query in a family determines
the same nonconstant world statistic h: h(omega)=h_e(L_e(omega)). Then all
these likelihoods must belong to the same independent factor. Otherwise
h would be a function of two distinct Cartesian coordinates separately.
Varying either coordinate while holding the other fixed would make h
constant, a contradiction. The common factor must have at least as many
categories as the number of distinct joint likelihood signatures.

This consequence concerns signatures of latent worlds. It does not give an
observer access to L_e(omega), h or the true latent world.

## 2. A sharp category law for a common unknown rate

Let z be uniform in F2^d and let eta independently have a positive prior
on J>=2 distinct rates in (0,1/2). A nonempty legal query family E consists
of parity vectors v_e in F2^d, possibly including zero (a diagonal). Its
binary likelihood is

`L_e(eta,z) = 1-eta if v_e dot z=0, and eta otherwise`.

Consequently eta=min(L_e,1-L_e), and v_e dot z is determined by whether
L_e is below 1/2. Each query's likelihood therefore identifies both the
same rate and its own parity. By section 1, every fixed independent-factor
encoding with exact closure must put all these likelihoods in one factor.

Let r be the binary rank of {v_e:e in E}. There are exactly 2^r joint parity
signatures, each available at every eta. Thus the required factor has

`at least J*2^r categories`.                                      (1)

**Attainment.** Choose r independent query vectors and extend them to a
basis of F2^d. The coordinate (eta, first r parity bits) is a single factor
with J*2^r categories. The remaining basis bits are independent and fair.
Its prior is pi_eta/2^r, and every likelihood is local to that first factor.
This attains (1) and closes under every legal query history. For rational
rates and prior, the existing positive multihomogeneous native factor
construction also realizes its local Bayesian updates at the ordinary
reciprocal-block-count rate:
inactive factor sums remain in the ambient graph. This is an existence
construction, not a new production emitter or physical cost certificate.

For a pair-query forest with m edges, r=m even if the edges lie in different
connected components. Every edge and the common rate belong to one factor
of at least J*2^m categories. For a spanning tree, m=n-1: the requirement is
the entire J*2^(n-1) anchored world alphabet. No closing cycle is needed.
For diagonal-only queries r=0 and exactly J categories suffice. For an
empty query family, no rate-dependent likelihood imposes this requirement.

Contrast the assumptions carefully. One known rate is constant and does
not couple queries by the shared-statistic argument; the known-noise
forest admits separate binary edge factors. Distinct rates strictly below
1/2 make the rate/parity signature identifiable from its likelihood.
Coincident rates, a rate of 1/2, rates on both sides of 1/2, or independent
rates for separate edges need their own signature calculation. Neither
zero-probability worlds nor a change of coordinates after each observation
is covered by (1).

There is no conflict with the acquisition theorem: a single traversal of
a forest gives zero information about eta in its observed transcript, yet
conditioning on its labels couples eta with the unknown edge parities.
An unchanged rate marginal does not imply independence from the latent state.

## 3. Decode the joint state without storing that categorical table

Keep the original complete joint learner and its sufficient coordinates
(T,d,s), pending event, ordinary cursor and optimizer-step clock, as in
[the noise-state law](NOISE_ACQUISITION_AND_STATE.md). T counts actually
executed candidate updates, including profile repetitions. A replay has
its algebraic effect without becoming fresh independent noise evidence.
The following is a transient decoder, not a persistent posterior quotient.

At the current cut, suppose the nonzero signed-count support F is a forest
with m edges, c=n-m components and H=SUM_e |d_e|. It is this current support
that matters, not the graph of every edge ever observed. For this arithmetic
upper, fix rational rates and a rational prior. Put

`A=(T+s-H)/2`, `B=(T-s-H)/2`.

Reachability makes A and B nonnegative integers. Choose a common likelihood
denominator S and a common prior denominator P, and set

`a_j=S*eta_j`, `b_j=S*(1-eta_j)`, `k_j=P*pi_j`,
`C_j=k_j*b_j^A*a_j^B`.

For an edge e with h=|d_e|, define its parity-zero/one factors

`(u_je,v_je)=(b_j^h,a_j^h)` if d_e>0, and `(a_j^h,b_j^h)` otherwise.

These positive integers give the exact unnormalized anchored-world weight

`W_j(z)=C_j PRODUCT_e (u_je if z_i XOR z_j=0 else v_je)`.             (2)

The original likelihood's denominator S^T, the prior denominator P and
the uniform world prior are common to all joint worlds. The C_j are not
common across rates and **cannot be canceled separately**.

Every forest edge-parity pattern has 2^(c-1) anchored realizations. Thus

`Z_j = 2^(c-1) C_j PRODUCT_e (u_je+v_je)`, `Z=SUM_j Z_j`.           (3)

For a current query whose endpoints are in the same component, let Q be
their unique forest path, including the empty path for a diagonal. Start
(E_j,O_j)=(1,0), and for each edge on Q perform only positive arithmetic:

`(E_j,O_j) <- (E_j*u_je+O_j*v_je, E_j*v_je+O_j*u_je)`.

With `R_j=PRODUCT_(e not in Q)(u_je+v_je)`, the exact joint rate/parity
partitions are

`(Z_j0,Z_j1)=2^(c-1) C_j R_j (E_j,O_j)`.                           (4)

For endpoints in different components, their relative root flip is fair
conditional on every rate and edge parity. Since c>=2, the integer formula is

`Z_j0=Z_j1=2^(c-2) C_j PRODUCT_e (u_je+v_je)`.                     (5)

The forecast is obtained by one joint normalization:

`p_0 = [SUM_j (b_j Z_j0+a_j Z_j1)]/(S Z)`, `p_1=1-p_0`.           (6)

Also `pi'_j=Z_j/Z`, and any requested complete native world weight is
`theta_(j,z)=W_j(z)/Z`. Equations (2)--(6) follow from the bijection between
forest parities and component-root orientations. No correlation or rate
component is dropped, and no conditional optimizer is substituted for U.

**Resource upper.** Given the support and a query, path discovery and the
positive sums/products use O(J(n+m)) scalar work, plus power construction.
Binary powers add O(J(log(T+1)+SUM_e log(1+|d_e|))) multiplications. Storing
all rate-specific edge powers for subsequent point reads uses O(J(m+1))
integer cells; a forecast alone can process rates successively. Reading a
dense d costs O(n^2), and the retained complete state is additional.

Every positive intermediate is bounded by P*2^(n-1)*S^(T+1), including
the forecast numerator and denominator. Partial products use disjoint
edge factors and at most their corresponding parity multiplicity; binary
powering never needs an exponent beyond its requested value. Therefore

`b = n + bit_length(P) + (T+1)*ceil(log2 S)`                        (7)

is a conservative common integer-bit envelope. The bit-work upper replaces
each scalar multiply by its b-bit multiplication cost; additions cost O(b).
For fixed rates/prior, b=O(n+T). These are algorithmic bounds, not Python
heap accounting, a prepaid allocation, a GPU kernel count or a Runtime
resource certificate. Explicitly emitting every native world coordinate
still costs at least J*2^(n-1) output cells.

The lower (1) and upper (7) price different objects. In particular a huge
irreducible categorical factor can have an efficiently decoded exact joint
description. This is the shared-noise counterpart of the earlier known-noise
[positive frontier separation](POSITIVE_FRONTIER_DECODER.md), obtained by
retaining each rate's unnormalized evidence.

## 4. Complete native relation and the boundary after a closing observation

For the existing joint Program with bases (1,1), the coefficient for world
(j,z) and label y is S*ell_(j,z,y)-1. All one-hot left/right sources,
pair PRODUCTs and fixed-feature nodes keep their actual meanings. The
native values are the sources, their pair products, these coefficients,
and the weighted heads. Equations (2)--(6) recover those heads and masses
`M_y=S*p_y`; the exact native normalizer is S.

At an observed, uncommitted cut the full CE gradient is

`g_fixed=1/M_y-2/S`,
`g_(j,z)=(S-2)/S-(S*ell_(j,z,y)-1)/M_y`.

The pending source/target and unchanged predecessor counts determine it.
Committed gradients are zero. The ordinary unit U updates theta by the
exact likelihood, corresponding to incrementing T and the appropriate
signed coordinate. These statements use the existing complete native
construction and gradient, including its fixed-slot derivative; no cache
or readout becomes an external information source. Profile attachment
changes the ordinary cursor while preserving the actual T and optimizer
steps. The decoder must not infer T from the attached cursor.

The forest domain is a sufficient algorithmic condition, not a restriction
on future observations. Adding a closing edge may make it inapplicable.
Retain all counts and return unresolved for this decoder; a paid general
decoder can still operate. A later opposite label can cancel that signed
edge, making the forest method applicable again. Its two executed events
still contribute to T and therefore to C_j.

The exact native witness starts with label-zero edges 01,12,02. The last
edge makes the forest decoder refuse. A label-one on 02 cancels its signed
count. The forest decoder then recovers the full joint native state, whose
rate-1/10 mass is 12/37 and whose next 02 label-zero forecast is 46269/74000.
Dropping the two canceled events would instead leave equal rate weights.
This is an actual continuation of the unchanged joint U, not a resetting
or merging operation.

## 5. Evidence and remaining scope

Run `python -X utf8 -B experiments/joint_uncertainty/shared_noise_factor_closure.py --write`.
The [minimal artifact](../../evidence/minimal/FP_SHARED_NOISE_FACTOR_CLOSURE.json)
retains aggregates and selected witnesses:

- 7,915 normalized binary likelihood tensors check both labels by an
  independent joint-versus-product-of-marginals identity; 99 preserve the
  factorization. The one-label-only determinant witness is exact.
- All 40,320 bijections of eight joint worlds, two nontrivial factor shapes
  and uniform/nonuniform rate priors give 161,280 encoding/shape/prior cases.
  Full one-event posterior tensors supply 709,632 checks; all 64 declared
  query-family/shape/prior cases agree with (1). A single nonloop query
  permits 384 encodings in shape (2,4); two independent parity queries
  permit none in either (2,4) or (2,2,2).
- Two rate/prior banks, with two and three hypotheses, cover 1,436 reachable
  forest cuts at n2..4 through T=3, 20,436 ordered-query partition pairs and
  both forecasts, and 25,220 complete weight points. All agree with an
  independent all-world integer formula. The 1,168 cyclic query refusals
  agree with independent triangle detection; a bit-cap refusal precedes
  power construction.
- 267 actual native predict/observe/commit triples check full caches,
  ambient gradients, weights and clocks. Another 387 all-query caches and
  3,096 weight points match the decoder. A repeated profile attaches at
  (cursor,steps)=(2,4) and continues to (3,5), preserving decoded weights.
- Eight n64/n256 query checks agree with an independent conditional
  path-correlation identity. At n256 the forest query family alone requires
  3*2^254 factor categories (the complete pair family requires 3*2^255),
  while the largest executed positive integer has
  4,319 bits and the largest positive operation count is 6,547. Counts,
  metadata, divisions and Python storage remain additional costs.

The proofs establish the arbitrary-size results; finite exhaustive checks
audit their scope. This is neither a universal memory lower bound nor a
claim that the current Runtime has a new indexed unknown-noise backend.
The worst-case all-pair decoding obstruction remains, and the existing
conditional-mixture block optimizer remains a different learner. The next
physical step must preserve this original joint state, own the complete
decoder resources and establish its actual native-to-AMP relation.
Foundation R4 and ERC-1 are unchanged.

The subsequent [joint-excess bridge](JOINT_EXCESS_PARTITION_BRIDGE.md)
extends the decoder to ordinary positive elimination across cyclic support.
Two integer excess aggregates supply a constant-size floating prediction,
with a complete native coordinate basis and a uniform S=20 arithmetic bound.
It retains the original joint counts and every rate's evidence. Ownership,
actual device conformance and Runtime continuation remain separate.
