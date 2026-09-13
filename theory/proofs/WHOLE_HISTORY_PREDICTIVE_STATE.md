# Whole-history predictive state and uniform-future memory

Status: **PROVED, SCOPED; EXACT EXHAUSTIVE AUDIT**. This is a model
predictive-state result. It neither changes the Foundation grammar nor
certifies a Compiler quotient, native construction, installation or AMP path.

## 1. The declared model and continuation class

There are n>=2 independent fair latent bits z_i. An ordered query (i,j)
returns y=z_i XOR z_j with independent known noise epsilon in (0,1/2).
All ordered pairs, including diagonals, are legal. Query selection is
exogenous, or its conditional law given revealed history is independent of
the latent bits and noise parameter. The result concerns the posterior
conditional on the actual queries and labels, not the state of a query policy.

A continuation is any finite common sequence of query/label observations,
followed by any queried pair. Every such label sequence has positive model
probability. A uniform guarantee must cover these continuations even when
they are very unlikely. This is stronger than an expected-risk guarantee.

For each unordered nonloop edge e={i,j}, let

`d_e = number of label0 observations - number of label1 observations`.

Both query orientations contribute to the same count. Put m=n(n-1)/2,
`r=(1-epsilon)/epsilon`, and `delta=1-2*epsilon`. The exact audits use
epsilon=1/10, so r=9 and delta=4/5. Counts are signed mathematical
coordinates; they are not newly authorized signed native sources.

## 2. Sufficient state for every model continuation

For a history h of length t, let D_diag be its diagonal label0-minus-label1
count. Its causal label likelihood is

`L_h(z,epsilon) = PROD_s P(y_s | query_s,h_<s,z,epsilon)`

`= epsilon^t * r^c * r^(SUM_e d_e 1[z_i=z_j])`,

`c = (t - SUM_e d_e + D_diag)/2`.

Here c is the number of nonloop label1 records plus diagonal label0 records,
so it is a nonnegative integer. Under the declared adaptive query rule,
the observed joint-history likelihood is Q(h)*L_h, where Q(h) is independent
of z and epsilon. Do not equate L_h with the conditional label law given
an entire adaptive query sequence: later queries may reveal earlier labels.
The parameter-independent factor cancels in the posterior at this history.
At fixed known epsilon its other two common factors also cancel. Consequently

`P_d(z) = r^(SUM_e d_e 1[z_i=z_j]) / Z_d`.

The law is unchanged by observation order, by exchanging query orientation,
by adding opposite labels on one edge, or by diagonal labels. A new nonloop
label adds +1 or -1 to one count; a diagonal leaves d unchanged. Equal d
therefore gives equal posterior laws after every common continuation, and
equal forecasts for all future pairs. The noisy label0 forecast is

`p_d(i,j) = epsilon + delta * P_d(z_i=z_j)`.

This is the complete known-noise model predictive quotient, not a permission
to remove order from SGD/profile replay or common likelihood factors from
noise inference, nor to erase the Compiler's raw observations or evidence.

## 3. Minimality and the scope of exact pair moments

Write sigma_i=(-1)^z_i and chi_e=sigma_i*sigma_j. The posterior is the
zero-field pairwise Ising exponential family, with natural parameter
`theta_e=(log r/2)*d_e`. The constant function and the m pair characters are
linearly independent: under the uniform latent law each character has mean
zero and distinct pair characters are orthogonal. Full support preserves
the absence of a constant linear combination. Global-flip symmetry does
not remove this independence.

Let mu(d) be the vector of expected pair characters. The identity

`KL(P_d || P_f) + KL(P_f || P_d)`

`= (log r/2) * (d-f) dot (mu(d)-mu(f))`

shows that equal pair moments imply equal distributions. Equality of the
distributions makes their log-density difference constant; character
independence then forces d=f. Since
`p_d(e)=(1+delta*mu_e(d))/2` and delta is nonzero, the complete vector of
**exact current pair forecasts determines d within this family**.

This mean-map uniqueness is classical for minimal exponential families;
see [Wainwright and Jordan, Proposition 3.2](https://www.cs.columbia.edu/~blei/fogm/2018F/materials/WainwrightJordan2008.pdf#page=64).
The application here identifies the actual history coordinates and their
legal future distinctions. It supplies no cheap or well-conditioned inverse.

The arbitrary orientation distributions in
[the joint-factor counterexample](JOINT_FACTOR_DYNAMICS.md#5-projection-and-missing-continuation-information)
are outside this pairwise family: their four-spin log interaction is nonzero.
Actual projected SGD can also leave the family. Those counterexamples remain
valid. Pair moments are not a sufficient state for arbitrary distributions,
and this theorem is not a complete-learner equivalence.

## 4. Exact state count at a fixed information cut

At a fixed cut t=T, the reachable signed-count vectors are exactly
`{d in Z^m : ||d||_1 <= T}`. Every history lies in this ball. Conversely,
realize each nonzero count by its signed edge labels and pad to length T
with diagonal labels. Thus the number of exact model predictive classes is

`N_m(T) = SUM_(j=0)^min(m,T) 2^j * binom(m,j) * binom(T,j)`.

Choose j nonzero coordinates, their signs, and positive magnitudes with
sum at most T. The latter choices number binom(T,j). Section 3 separates
every pair of classes already by some exact current pair forecast.

Across an isolating predictor cut, all recoverable old information must be
counted. A deterministic finite predictor needs at least N_m(T) distinct
states, hence at least `ceil(log2 N_m(T))` binary bits. Abstract encoding of
these classes attains that information bound; simple signed counters use
at most `m*ceil(log2(2T+1))` bits, with the fixed cut and model declared.

This separates model-state information from arithmetic and circuit cost.
Exponential latent-world weight storage is not an information lower bound.
The counter code supplies no native decoder, positive update graph, initialized
reachability, inference-work bound or physical byte certificate. The complete
Runtime still contains its own data, optimizer, clocks, resources and provenance.

The exact-T ball uses legal diagonal padding. With only nonloop queries,
fixed-T reachability also has a parity constraint. With a fixed preassigned
query schedule, the set can be smaller still. Do not apply this class count
to RN-5's single registered tape or frozen-state decision class.

## 5. A fixed uniform error tolerance retains every class

**Theorem.** At cut T, a deterministic predictor with absolute probability
error at most a, uniformly after every legal common continuation, needs at
least N_m(T) states whenever `a < delta^2/4`. At noise1/10 this threshold is
4/25. Thus the exact per-cut information lower bound survives fixed uniform
approximation; it is not merely a vanishing-separation exact bound.

**Proof.** Take any two different reachable vectors d,f. Let D=f-d. Pick
a vertex v incident to a nonzero D edge and an anchor r0 other than v.
Choose signs s_j for all j!=v with s_r0=1 such that

`S = SUM_(j!=v) D_{v,j} s_j`,

`|S| = SUM_(j!=v) |D_{v,j}| >= 1`.

For example, take an incident nonzero edge as anchor and align every sign
with D_{v,j}, then flip all signs if necessary to make the anchor positive.
Signs at zero D entries do not affect the sum.

Put `H_d=SUM_(j!=v) d_{v,j} s_j`. Append |H_d| labels on (v,r0), with the
orientation that adds signed count -H_d. Next, for each j other than v,r0,
append B identical labels on (r0,j) favoring
`sigma_j=s_j*sigma_r0`. This is one common future for both histories.
Define C as satisfaction of all n-2 latter constraints. Exactly four full
latent assignments satisfy C: the free bit at v and the global flip.

Conditional on C, all edges not incident to v contribute a common factor.
The remaining field on `sigma_v*sigma_r0` is zero for d and S for f.
Their next noisy (v,r0) forecasts therefore differ by at least

`delta * |r^S/(1+r^S) - 1/2| >= delta^2/2`.

The conditioning is justified by actual finite observations, not an erased
state or supplied hard constraint. Before the B-strength constraints, the
absolute sum of the signed coefficients is at most 2T for either history,
because ||d||_1,||f||_1<=T and |H_d|<=T. Each assignment outside C loses
at least B in its constraint exponent. Comparing maximum off-C weight with
minimum on-C weight gives

`P(C^c)/P(C) <= ((2^n-4)/4) * r^(2T-B)`.

Choose `B=2T+b` with `2^(n-2)*r^(-b)<=eta`. Then the off-C posterior mass
is at most eta in either history. Each actual forecast differs from its
conditional forecast by at most delta*eta. Their actual separation is at least

`delta^2/2 - 2*delta*eta`.

For any a<delta^2/4, a positive eta makes this strictly larger than 2a.
The common suffix has at most `T+(n-2)*(2T+b)` labels. All these observations
have positive probability. If the two initial histories shared the same
deterministic state at their common cut, this identical suffix and query
would give identical predicted outputs, which cannot both be within a.
All N_m(T) classes must therefore have distinct states. QED.

No fixed finite model memory supports this uniform guarantee at all horizons.
The proof does **not** rule out useful finite memory under expected risk,
a restricted future horizon/query schedule, or a probabilistic failure budget.
It does not assert that these rare separating suffixes are readily acquired
from an IID stream or that the learner may choose their labels.

A shorter special case uses counts in {0,...,L} on a fixed spanning tree,
padded to T=(n-1)L. Its edge parities are independent. Cancel the smaller
count on any differing edge with at most L contrary labels. The next forecast
gap is already at least8/25 at noise1/10. This gives (L+1)^(n-1) separated
states under a much shorter declared future bound; the full-class theorem
above also treats cyclic and frustrated histories.

## 6. Rounded confidence and unknown noise are different boundaries

For one nonloop edge with signed count k at noise1/10,

`p_k = 1/10 + (4/5)*9^k/(1+9^k)`.

Counts8 and9 have different exact forecasts but the same round-to-nearest
binary32 word, 0x3f666666. Their exact gap is
344373768/20846477662667225. Both can occur at cut9: prepend one diagonal
to eight label0 edge records, or use nine label0 edge records. Their last
eight observations coincide. After the same eight contrary edge labels,
their next forecasts are1/2 and41/50. Thus storing only the currently rounded
pair forecasts, even with that clock, loses future-useful information.
This audits rounding of ideal probabilities, not actual native GPU phases.

If epsilon is unknown, the common factor in section 2 may no longer cancel.
The tuple (d,t,D_diag) preserves the likelihood for latent bits and epsilon
up to the parameter-independent query factor; no minimality is asserted for arbitrary
restricted noise priors. The tuple (d,t) alone does not generally suffice.

For equal prior weights on epsilon in {1/10,1/4}, compare

`h_A=((0,1,0),(0,1,1))`, `h_B=((0,0,0),(0,0,0))`.

Both have d=0,t=2 and current cross forecast1/2; their diagonal balances
are0 and2. Append the same (0,1,0). Their next (0,1) forecasts are
5093/7400 and9029/12200 respectively. A fixed-known-noise latent quotient
cannot be reused for noise learning or evidence. At epsilon=1/2 all pair
forecasts are1/2 and all d are equivalent, so nonzero noise contrast is an
essential premise of the minimality and separation theorems.

## 7. Implementation consequence and minimal evidence

The research problem is affordable inference and reachable native adaptation
from the information that remains useful. It is not a need for exponentially
many stored posterior masses, nor a license to discard an older count once
its current effect rounds away. The abstract bit-coded embedding in
FP_THEORY IV.9 starts at the categorical code of its declared initial state;
the present Runtime's zero-initialized delays do not automatically provide
that code or its positive decoder. No state initializer is changed here.

Run `python -B experiments/joint_uncertainty/predictive_counts.py` from the
research checkout. It imports no Torch and emits a small exact report:

- 6,175 ordered histories,12,350 fixed/joint-noise likelihood identities,
  and6,174 append transitions;
- 846 distinct exact forecast tables across four complete count balls,
  and371 character Gram entries;
- all2,016 pairs of64 tree-count states, with exact minimum future gap8/25;
- all4,216 pairs in four complete count balls: n2,T8; n3,T2; n4,T2; n5,T1.
  Every common finite suffix attains the declared gap lower38/125, using
  off-constraint posterior mass at most1/100. The measured minimum gap is
  82356471969768/257366557712425, approximately0.3199967886; the longest
  checked suffix has19 labels;
- the binary32 collision, unknown-noise distinction and noise-half boundary.

These finite audits pressure-test the general proofs; they are not empirical
model-quality results, full Runtime audits or certificates of a new class.
No large table, dataset, weight cache or new GPU job is needed as evidence.
