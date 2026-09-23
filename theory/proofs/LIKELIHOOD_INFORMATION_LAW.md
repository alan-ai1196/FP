# Likelihood coordinates, future error and causal state encodings

Status: **PROVED, SCOPED; EXACT NATIVE-LEARNER AUDIT**. For a fixed finite
positive rational likelihood bank, the exact number of reachable predictive
states at a known cut T is Theta((T+1)^rho). The exponent is the rational
affine rank of integer likelihood-ratio valuations. It need not equal the
number of free real posterior coordinates. Future approximation has a
different geometry, and a small distance between two states does not by
itself define a causal quotient. These results concern the learner and its
declared predictions, not equivalence of complete Compiler states.

## 1. Model and actual learner scope

Fix a finite world set of size K, a strictly positive rational prior pi,
a finite **complete legal query alphabet** X, and finite labels Y. Fix
positive rational likelihoods ell_(x,y)(k), summing to one over y for each
x,k. Every finite query/label word is permitted in the mathematical model.
The query is revealed before its label. The learner update is

`B_a(w)_k = w_k ell_a(k) / SUM_j w_j ell_a(j)`.

This algebraic update applies to each actual legal word. Its Bayesian
interpretation additionally requires the declared conditional observation
law and a query policy independent of the latent world given past data.
Positivity makes every finite label word possible; it does not make an
adversarial word likely. Fixed computational caps may prevent execution
of such a word. No unlimited resource allowance follows from this model.

The [simplex gradient theorem](SIMPLEX_GRADIENT_POSTERIOR.md) realizes this
update from native CE gradients when the positive heads are affine in a
selected simplex block, their expert column normalizers agree at each
query, all other parameters are fixed, and the registered U has rate 1,
one-event units and no grid. This is the implemented distinct simplex U,
not projected SGD, fractional-rate learning or a larger update unit.

In particular, every bank above has a literal native realization. Choose
a common denominator L of all likelihoods and use one-hot query sources.
For each world k and label y make a feature SUM with L ell_(x,y)(k)-1
copies of source x, each weighted by a fixed unit slot. Weight those
features by w_k and SUM them into the label's excess above base 1.
Every multiplicity is a nonnegative integer. At unit feature weight,

`M_y = L SUM_k w_k ell_(x,y)(k)`, `normalizer = L`.

Gamma is explicitly `(1,pi)` and selects only the world slots for U.
This is a finite positive SUM construction; its actual incidences, world
enumeration, initializer and decoding costs remain. No fitted likelihood
or posterior is supplied by a helper to an owned Runtime.

After T commits, if c_a counts actual candidate-executed events,

`w_k(c) proportional to pi_k PRODUCT_a ell_a(k)^c_a`, `SUM_a c_a=T`. (1)

Profile replays must have their actual multiplicity. T is the optimizer
step count, not automatically the ordinary cursor or number of unique
observations. The two clocks remain distinct after late births/profiles.

## 2. Exact ratio coordinates and matching upper/lower law

Choose a reference world 0. For every prime p occurring in a reduced
ratio ell_a(k)/ell_a(0), define the integer vector

`v_a[(k,p)] = valuation_p(ell_a(k)/ell_a(0))`, `k != 0`.

The bank is fixed, so there are finitely many rows. Unique prime
factorization and positive pi give the exact equivalence

`w(c)=w(c') iff SUM_a c_a v_a = SUM_a c'_a v_a`. (2)

Choose a reference event a0, set `D_a=v_a-v_a0`, and let
`rho=rank_Q {D_a : a in X times Y}`. At a known T, the full valuation
sum equals `T v_a0 + SUM_a c_a D_a`. Choose rho independent rows of
the matrix D. Their rho integer sums q determine all remaining rows
by a fixed rational linear map. Thus `(T,q)` decodes (1) exactly and
updates q by addition of the selected rows of D_a at every commit.

Let N(T) be the number of distinct reachable posteriors at that cut.
If each selected row has range R_i across the event alphabet, then

`N(T) <= PRODUCT_(i=1..rho) (T R_i+1)`.

For the converse choose rho independent columns D_(a1),...,D_(a_rho).
Vary each of their counts independently from 0 to floor(T/rho), and
fill the remaining events with a0. These are legal length-T words.
Column independence makes all resulting posteriors different, giving

`N(T) >= (floor(T/rho)+1)^rho`, for rho>0.

For rho=0, N(T)=1. Consequently

**`N(T)=Theta((T+1)^rho)` and `log2 N(T)=rho log2(T+1)+O(1)`.** (3)

Constants depend on the fixed bank, not T. The lower bound is abstract
fixed-cut information; the selected integer rows provide a matching
online encoding. It does not price the graph, evidence, raw data, actual
cursor, pending gradient or decoder workspace. Exact materialized weights
can still have Theta(T) integer bits per coordinate. Factorization is a
fixed-bank mathematical construction, not an efficient registration claim.
The later [coprime construction](COPRIME_LIKELIHOOD_READOUT.md) realizes the
same rank and online coordinates without prime factorization. It also gives
a jointly scaled positive-integer readout with a history-uniform selected-
weight bound. Its [owned registration](RATIONAL_LIKELIHOOD_RUNTIME.md) now
passes the CPU gate; the actual AMP/fresh/install gate remains pending.

The event affine rank is essential: with one query and world probabilities
P(y=0)=(1/3,1/2), the two ratio increments 3/2 and 3/4 have raw valuation
rank 2. At a known T only one event count is free, so rho=1 and N(T)=T+1.
Conversely, with ratios 2, 1/2, 3, 1/3 and an identity event, K=2 but
rho=2. A single real log-odds coordinate can carry two independent integer
coordinates. Real vector-space dimension is not a bit-counting argument.

For the known-noise relation bank, all nontrivial ratios are powers of 9.
The valuation rank is m=n(n-1)/2: the edge equality functions modulo a
constant are independent Walsh characters, and each has its own event.
Diagonal padding and reciprocal labels give exactly the integer L1 ball
from [the earlier proof](WHOLE_HISTORY_PREDICTIVE_STATE.md), recovering
its exact count formula as well as its leading exponent m.

## 3. Why these are exact future-prediction classes

Merge worlds only if their **entire declared likelihood signatures** are
identical. Within such a group the reachable world proportions are fixed
by pi, so its total mass determines the full reachable posterior. Let G
be the number of distinct signatures.

For any signature g and each h != g choose an event a(g,h) distinguishing
them. On the finite signature set, the polynomial

`f_g(z) = PRODUCT_(h != g)
 (ell_a(g,h)(z)-ell_a(g,h)(h))/(ell_a(g,h)(g)-ell_a(g,h)(h))`

equals one at g and zero at every other signature. It is a linear
combination of likelihood monomials of degree at most G-1. Each monomial
is the conditional joint probability of a legal word, averaged under
the starting posterior. Distinct group masses therefore differ on some
word probability of length at most G-1. If all successive conditional
forecasts along that word agreed, their products would agree, a
contradiction. Some forecast before its label must distinguish them.

The signed coefficients in this interpolation argument are a proof device,
not native negative activations. The G-1 bound concerns known fixed
signatures, not identification of unknown mixture components. It is
consistent with, but different from, grouped-mixture identifiability [1].

Thus exact equality of all legal future forecasts coincides with (2) on
the fixed-prior reachable family, and (3) is an exact predictive-state
law. Equality only of current forecasts is weaker: in the audited
three-world bank, two length-2 histories have identical forecasts for
every current query but differ by 1/120 after one common additional label.

## 4. Complete reference phases still require their actual event and clocks

For a fixed native realization above, `(q,T)` decodes theta. At a committed
boundary all gradient slots are zero. At an observed but uncommitted cut,
retain the actual query/label a and reconstruct the whole native cache and
ambient gradient at the decoded pre-commit theta. In this particular
literal realization, with target mass M and J=|Y|,

`G_fixed = 1/M - J/L`,
`G_k = (L-J)/L - (L ell_a(k)-1)/M`.

The selected weighted mean equals G_fixed. Keep the ordinary cursor,
optimizer-step count, unit count and every fixed gradient slot, exactly
as in [the relation phase encoding](COUNT_LEARNER_ENCODING.md). The
pre-target query/cache identity stays in the surrounding event state.
An arbitrary graph with the same selected affine slice requires its own
ambient-derivative/cache decoder; this formula does not cover it.

This is a complete reference learner/cache simulation for the specified
realization, not a complete Omega quotient. Histories with equal c can
have different provenance, construction cost, fresh evidence and install
rights. None of those are deleted. A physical implementation must pay for
storage and reconstruction, guard exact-integer overflow and discharge
its own bridge and installation obligations.

## 5. A uniform future error bound, with its correct geometry

For positive distributions w,u define the Hilbert projective distance

`H(w,u)=max_k log(w_k/u_k)-min_k log(w_k/u_k)`.

Every common positive likelihood update preserves H exactly: the shared
likelihood cancels in coordinate ratios and normalization adds only a
common logarithmic constant. This Bayesian update is an **isometry** here;
one may not import strict contraction from a mixing transition matrix.

With TV defined as half the L1 distance, the sharp bound is
`TV(w,u)<=tanh(H(w,u)/4)` [2, Theorem 5.1, adjusting its TV convention].
An elementary finite proof writes u as normalized r*w with m<=r<=M.
For fixed mean of r, convexity bounds the absolute deviation by its
two-endpoint distribution. Optimizing its endpoint mass gives
`(sqrt(M)-sqrt(m))/(sqrt(M)+sqrt(m))`. Here M/m=exp(H).

Let `chi=max_a (max_k ell_a(k)-min_k ell_a(k))`. Every query/label
forecast difference is at most chi*TV. Therefore the supremum d_F over
all common finite futures and final forecasts obeys

**`d_F(w,u) <= chi*tanh(H(w,u)/4)`.** (4)

This protects a fixed positive multiplicative perturbation followed by
exact common updates. It does not bound accumulated rounding errors,
ambient gradients, raw caches, cumulative loss or fresh wealth. An
absorbed zero against a positive reference has infinite H; a small
current absolute error gives no such protection. The observed
[AMP reversal failure](SIMPLEX_REVERSAL.md) is unchanged.

Consider the binary bank

| Query | P(label 0 given world 0) | P(label 0 given world 1) |
|---|---|---|
| A | 2/3 | 1/3 |
| B | 3/4 | 1/4 |
| I | 1/2 | 1/2 |

Use a fair prior and complementary label-1 probabilities. It has a native
base-1 realization with L=12, fixed feature slot 1, and simplex prior
(1/2,1/2). Its ratio increments are 2,1/2,3,1/3,1,1, so rho=2 and
`N(T)=2T^2+2T+1`. Meanwhile chi=1/2. Since log(2)/log(3) is irrational,
the attainable common log-odds shifts are dense in R. Optimizing the
two-world sigmoid separation therefore attains (4) as a supremum:

`d_F(w,u) = (1/2)*(sqrt(R)-1)/(sqrt(R)+1)`,

where R>=1 is the ratio between the two posterior odds. Finite common
words approach this optimum; an exact maximizing word is not required.

Take h as 19 A-label-0 events, and g as 12 B-label-0 events followed by
7 I events. Their same-cut odds are 2^19 and 3^12. Thus

`R=531441/524288`,
`d_F(h,g) < (R-1)/8 = 7153/4194304 < 1/500`. (5)

There is even one positive rational posterior approximating both paths:
choose the arithmetic mean of their odds. Its projective ratio to either
is at most (R+1)/2. Under all subsequent exact common updates its error
against either path is below `(R-1)/16=7153/8388608 < 1/1000`. This is a
mathematical representative, not an authorized Runtime initializer.

Pigeonhole approximation to the irrational log ratio gives arbitrarily
close distinct prime powers. Pad the shorter history with I. Thus there
is **no positive separation constant for every pair of exact classes**
in this bank. The earlier single-noise relation separation theorem does
not extend solely from positivity or rationality. This does not disprove
every approximate memory lower bound, nor construct an online codec.

## 6. Approximate pairs need not form a causal quotient

There is a stronger constraint if an implementation claims a pure,
deterministic encoding E_T of the reference learner at committed cuts:
the same reference state and clocks must give the same code, and

`E_(T+1)(B_a(w)) = U_(a,T)(E_T(w))` (6)

must hold for every reachable state and event. Its forecast decoder must
have error at most e for every legal word at every time. Codes may depend
on T; (6) does not assume stationary or clock-free storage. It does
exclude history-dependent physical lifts and external-history repair.

**Two-world reversible-bank theorem.** Suppose every event's odds ratio
has a legal inverse word and chi>0. Under (6), if e<chi/2 and all finite
continuations are covered, E_T is injective on distinct reachable
posteriors at every T. Thus its state count obeys the exact law (3).

Proof: suppose two equal-length histories h,g with likelihood odds L_h
and L_g produce one code but different posteriors. For any m, all
histories made of m blocks h or g must share one code. To replace any
one block, commute it to the beginning of the **reference** word, apply
the original code equality followed by the same suffix using (6), and
commute back. Identical complete committed reference states have one
encoding; transitivity connects all m+1 mixtures of the blocks.

For even m append a common inverse of `(hg)^(m/2)`. The two extreme
histories now have odds `O_prior*(L_h/L_g)^(m/2)` and its reciprocal
factor times O_prior. As m grows these tend to opposite worlds. Some
query/label forecast gap tends to chi, yet the shared code implies a
gap at most 2e. This contradicts e<chi/2. The argument requires the
stated arbitrary finite words; a bounded-horizon or unresolved execution
cannot be promoted to that premise.

The threshold is sharp for this prediction-only quotient class. At
e=chi/2, one code per cut with the per-query midpoint of the two expert
forecasts suffices, and its constant update obeys (6). This says nothing
about reconstructing gradients or meeting the complete physical bridge.

There is a short exact witness using (5) and e=1/1000, despite that
pair's common accurate representative. If E_19 merges h
and g, common suffixes and the full reference equality `state(hg)=state(gh)`
force `E_38(hh)=E_38(hg)=E_38(gg)`. Append the common 38-event inverse of
hg, formed by reversing each binary label. At cut 76, the extreme odds
are 1/R and R. Their B-label-0 forecast difference is

`(R-1)/(2*(R+1)) = 7153/2111458 > 1/500 = 2e`.

These later words are **not one common continuation of the original
pair**: the contradiction uses global transition consistency and
transitivity of one pure encoding. Hence it does not contradict (5).
Pairwise approximate closeness is not an equivalence relation that may
be installed as a causal quotient. This is an additional proof obligation,
not a new Foundation action, a universal bound on history-dependent
algorithms, or a claim that an approximate decoder cannot be useful.

## 7. Exact audit and open execution obligation

Run `python -B experiments/joint_uncertainty/likelihood_information.py`.
The small audit has no Torch import, physical backend or Runtime authority.
It checks:

- 2,118 exhaustive native histories across seven banks, with 2,111 full
  cache/observed-state/committed-state comparisons each; an additional
  228 complete native event comparisons verify the cut-76 witness;
- 2,408 histograms at cuts 0 through 6, independently formed product
  posteriors versus compressed-coordinate decoding in both directions;
  all rank/count bounds, duplicates, nonuniform priors, three labels and
  the raw-rank/known-clock counterexample;
- relation ranks at n=2,3,4,5; 48 future-word rows and explicit signature
  interpolation values; the 1/120 hidden-future difference;
- 5,535 positive-tilt isometries and sharp TV inequalities, checked by
  the equivalent rational inequality `((1+TV)/(1-TV))^2 <= exp(H)`;
- the exact length-19/76 counterexample and successively closer prime
  powers, including a fixed pair whose every-future gap is below 1e-5;
  510 midpoint checks at the prediction-only constant-code threshold.

This closes the scoped information/continuation question before adding
a physical codec. A paid, source-bound representation of the actual
unit learner remains the execution target. It must retain the complete
phase and provenance, account for growing exact information and decoder
work, and prove its actual reference/AMP relation. Foundation R4, ERC-1,
the existing Runtime certificates and the live RN-5 source are unchanged.

## Sources

1. Robert A. Vandermeulen and Clayton D. Scott, [On the Identifiability of
   Mixture Models from Grouped Samples](https://arxiv.org/pdf/1502.06644),
   arXiv:1502.06644v2, 2022. Background on identifying unknown mixtures
   from repeated observations; its 2m-1 result is not the known-bank
   G-1 interpolation argument proved here.
2. Samuel N. Cohen and Eliana Fausti, [Hyperbolic contractivity and the
   Hilbert metric on probability measures](https://arxiv.org/pdf/2309.02413),
   arXiv:2309.02413v2, 2024, Theorem 5.1. Source for the sharp TV/Hilbert
   bound; likelihood isometry and the FP encoding consequences above
   are derived explicitly. No novelty is claimed for that metric bound.
