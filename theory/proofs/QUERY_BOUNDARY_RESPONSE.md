# Query projection and the exact information exposed by a finite future

Status: **PROVED, SCOPED; EXACT EXHAUSTIVE AUDITS PASS**. These are
predictive-response and decoder results. The complete CountState, literal
native parameter meaning, observation history and Compiler resources remain
unchanged. The subsequent [owned reference integration](OWNED_QUERY_PROJECTION.md)
now implements the projection with complete state and resource checks.
No new AMP schedule or Foundation action follows from this mathematical
proof. Foundation R4 and ERC-1 remain frozen.

The existing [query-matroid theorem](FACTOR_QUERY_MATROID.md) identifies
cycle blocks for a fixed family of legal queries. Here the active count
support is used only to plan a current forecast, while every future pair
remains legal and the full count vector is retained. This difference in
quantifiers is essential.

## 1. Positive boundary responses

Use the existing fair-prior relation model with independent observation
noise1/10. Write sigma_v=(-1)^z_v. An observed pair e={u,v} and label y has
likelihood `(1 + delta*(-1)^y*sigma_u*sigma_v)/2`, with delta=4/5.
Equivalently, its positive integer likelihood factor is9 on a matching
parity and1 otherwise. The character expression is proof notation, not a
signed native source or a new execution primitive.

Let B contain b>=2 boundary vertices. Sum any hidden interior out of a
positive zero-field pair-factor system, obtaining a strictly positive
message M(sigma_B). Simultaneous sign flip leaves M unchanged. Its overall
positive scale cancels from boundary conditional forecasts, so normalize
it to a distribution mu. Equivalently fix one boundary spin and use the
2^(b-1) anchored assignments. This local gauge is only a computation; the
original native world/parameter indexing is preserved in the complete state.

The continuation class in this section consists of at most h>=0 common
pair/label observations wholly inside B, followed by any queried pair in B.
All such finite labels have positive probability. No query may inspect the
eliminated interior or add a new edge to it. This is a model-response class,
not a claim of equality of complete Compiler histories or resource states.

## 2. Finite-future moment law

For S subset of B let `chi_S=PRODUCT_(v in S) sigma_v`. Odd moments vanish
under flip symmetry. Define h-equivalence as equality of every noisy pair
forecast after every common continuation in the class above.

**Theorem.** Two positive flip-symmetric boundary distributions are
h-equivalent iff their even moments agree for every nonempty S with

`|S| <= min(2h+2, b)`.

Thus one set of independent linear response coordinates has size

`D_h(b) = SUM_(k=1)^min(h+1,floor(b/2)) binom(b,2k)`.

**Sufficiency.** The probability of a t-observation word is the expectation
of a product of t positive likelihoods. Expand each likelihood into its
constant and pair character. A product of t pair characters is an even
character involving at most2t vertices; repeated vertices cancel. Hence
all joint word probabilities for t<=h+1 depend only on the stated moments.
The next conditional forecast is a ratio of the corresponding joint word
probability to its strictly positive prefix probability. Equal moments
therefore give all the required forecasts.

**Necessity.** Equality of conditional forecasts through h observations
determines equal joint label laws for every sequence of at most h+1 fixed
queries, by multiplying conditional probabilities. For an even set S of
size2k<=2h+2, partition S into k disjoint pairs and query those pairs.
Conditional independence of the known observation noises gives

`E[PRODUCT_(t=1)^k (-1)^Y_t] = delta^k E_mu[chi_S]`.

The joint label law determines the left side, and delta is nonzero.
Consequently the moment agrees. This proves both directions. QED.

This is a linear response-coordinate count, not an unrestricted lower
bound on the number of arbitrary infinite-precision real registers. The
coordinates are independently variable in an open neighborhood of the
uniform distribution: small Fourier perturbations of the selected even
characters preserve strict positivity. Any exact *linear* summary of all
these response classes therefore needs rank at least D_h(b). A finite
message family gives an ordinary information lower bound as well. For
L>=2, independently choose each coefficient t_S in{0,...,L-1} and use

`mu_t(sigma) = 2^-b [1 + SUM_S t_S*chi_S/(2*D_h(b)*L)]`.

Every distribution is positive and has distinct selected moments. These
L^D_h(b) h-response classes require at least ceil(log2(L^D_h(b))) bits in a
deterministic code across an isolating cut, counting all recoverable side
information. This finite family concerns arbitrary boundary messages;
reachability of every member from the fixed count initializer is not claimed.

The later [reachable information law](REACHABLE_BOUNDARY_INFORMATION.md)
attains the same L^D_h(b) class count with a different, count-reachable
exponential family at common queries and clock. Its isolated code bound
has a matching upper. It also falsifies a universal O(T^D_h(b)) bound on
all count-reachable boundary classes: dimension alone is not precision.

## 3. The horizon bound is sharp

Once `h >= floor(b/2)-1`, every even moment is included. The even characters
form a basis for functions on anchored assignments, so the full normalized
message is determined. Equivalently, equality under all boundary futures
means that the original positive messages are proportional.

The hierarchy before this point is strict. Choose a set S with2h+4 vertices
and `0<a<1`, and put `mu_+=(1+a*chi_S)/2^b`,
`mu_-=(1-a*chi_S)/2^b`. Their moments through order2h+2 agree, so all
h-future forecasts agree. Observe label0 on h+1 disjoint pairs in S and
query the last pair. The forecasts are

`1/2 +/- a*delta^(h+2)/2`.

They differ by the positive amount a*delta^(h+2). For b4,h0,a1/2 all current
pair forecasts are1/2, but one common label0 observation produces next
forecasts33/50 and17/50. Arbitrary boundary messages need not remain in
the original pairwise exponential family after marginalization, so the
[full count-family mean-map theorem](WHOLE_HISTORY_PREDICTIVE_STATE.md)
does not identify these two distributions from their current pair moments.
The audit does not assert count-family reachability of these particular
tables. It tests the broader boundary-response theorem exactly.

The subsequent [reachable-message construction](REACHABLE_BOUNDARY_MESSAGES.md)
closes that escape route for strictness itself: legal unit-count histories
produce a nonzero pure b-spin boundary character for every even b. A
3-adic identity proves nonvanishing at likelihood ratio9, and two n8 owned
Runtime histories exhibit the one-step separation. Their coefficient differs
from the convenient a1/2 tables above; arbitrary-grid reachability is still
not claimed.

For b0 or b1 a flip-symmetric message has only a common positive scale.
Such a branch is invisible to all continuations confined to its unchanged
boundary. For b2 a message is exactly a two-entry parity response. This
explains both the cancellation and the retained two-value object below.

## 4. Current-query block projection

For complete signed counts d, form the graph of nonzero nonloop counts.
Each edge has positive factor

`phi_e(parity) = 9^max(d_e,0)` for parity0,
`phi_e(parity) = 9^max(-d_e,0)` for parity1.

Their product has the same normalized posterior as the full native count
decoder. Temporarily release the global z0=0 gauge; every assignment and
its global flip have equal weight and equal queried parity, so this doubles
both numerator and denominator without changing the forecast.

Use the standard block/vertex incidence forest: blocks are maximal cycle
blocks, with each bridge a block of its own. Original vertices join the
blocks containing them. If queried i,j are disconnected, component flip
symmetry makes their parity uniform. If i=j, parity0 is certain. Otherwise
take the unique incidence-forest path from i to j. Every block off this
path meets the retained path through at most one boundary vertex. Sum its
interior out from the leaves inward. The b1 response is a positive constant
independent of that boundary spin, so it cancels from the normalized query.
Only the blocks on the path need arithmetic evaluation.

For each retained block with entry u and exit v, sum its factors with u
anchored to0, obtaining parity weights (a,b). Flip symmetry makes these
the same conditional response for either entry orientation. Along the
path compose the responses using only positive SUM/PRODUCT:

`(A,B) starts at (1,0)`;
`(A,B) <- (A*a+B*b, A*b+B*a)`.

The latent equal-parity probability is A/(A+B). The native excesses are
`8A/(A+B), 8B/(A+B)`, masses are one plus those excesses, normalizer10,
and the two noisy forecasts are `(9A+B)/(10(A+B))` and
`(A+9B)/(10(A+B))`. The existing finite-cache/gradient basis then applies.
This supplies a single general projection law; it is not an architecture
menu for separately handwritten graph shapes.

Small-separator decomposition in zero-field Ising inference is established
related work; see [Likhosherstov, Maximov and Chertkov (2019)](https://arxiv.org/abs/1906.06431).
The FP-specific claims here are the declared continuation class, the finite
future law, the current-query scope, and preservation of complete native
state and physical schedule obligations. General Ising factorization is
not claimed as a new discovery.

## 5. Resource consequence and limits

Let C be the union of retained path blocks, H_C=sum_(e in C)|d_e|,
and k the number of those blocks. The complete input counts still cost D
coordinates. An active-support scan and block decomposition require
O(D+n+m) discrete work and O(n+m) graph workspace. This work is paid even
when the query subsequently has a constant answer.

For a block with v_B vertices and e_B edges, straightforward streamed
enumeration uses2^(v_B-1) assignments and O(e_B*2^(v_B-1)) positive
arithmetic, in addition to forming its edge powers. Compose k responses
with four products and two sums per block. A variable-elimination solver
can instead use its separately guarded block table widths. This is an
arithmetic upper construction, not a RAM, time or optimality certificate.

The final unnormalized response has at most2^(|V(C)|-1) summands bounded
by9^H_C. Intermediate block and convolution integers therefore have
O(|V(C)|+H_C) bits. With the existing conservative factor4 per count, a
bound of `|V(C)|+4H_C+8` suffices for the response and fixed readout/gradient
rational operations. Outside counts need no powers for this query. Their
own storage and scanning costs do not disappear. Explicit native theta
coordinates still depend on global normalization and have their existing
output/height costs. Hard biconnected blocks retain the earlier worst-case
forecast-decoding obstruction; this is not a universal cheap decoder.

Nor is C a replacement learner state. At n4, counts d12=+1 or-1 both give
current query(0,3) probability1/2, but their first native world weights are
already9/40 and1/40. After common observations(0,1,0),(2,3,0), the same
query forecasts881/1250 and369/1250. Deleting an off-path count loses legal
future information. The projection is recomputed from the retained full
counts; it grants no quotient of states, histories, clocks or resources.

Finally, exact algebraic cancellation does not preserve a fixed floating
schedule. Two triangles sharing vertex0, with counts(-2,-2,-2) on the
queried triangle and(-2,-2,-1) on the other, have exact latent query(1,2)
probability3281/9842 with or without the other triangle. The existing
radix9 RNE simulation nevertheless gives different readout words. In
particular probability word1052491594 becomes1052491593. A projected AMP
implementation needs its own declared schedule and actual verification;
the repaired A4 certificate cannot be transferred by algebra alone.

## 6. Minimal exact evidence

Run `python -X utf8 -B experiments/joint_uncertainty/query_block_projection.py --write`.
[The retained evidence](../../evidence/minimal/FP_QUERY_BLOCK_PROJECTION.json)
contains aggregate counts and small separating examples:

- All1098 graph supports for n2 through n5 match an independent exhaustive
  simple-path edge-union oracle for every pair.
- All59,808 ternary signed-count states and1,488,144 ordered queries match
  independent anchored full-world enumeration exactly. 658,642 queries use
  strictly fewer edges than the active support.
- Positive boundary messages on b2 through b7 are recovered exactly from
  their positive star-observation response tables. The inverse is used only
  for an identifiability audit, not as a native signed arithmetic operation.
- Strict h0/h1/h2 examples on b4/b6/b8 pass all89,875 available
  history/next-pair comparisons within their indistinguishable horizons;
  each separates at the next horizon with the proved forecast values.
- The full-state/future counterexample and unequal fixed-AMP words are
  retained explicitly. No cache, weights, dataset or new GPU job is dumped.

These audits support the arbitrary-b,h and arbitrary-graph proofs; they do
not replace their quantifiers. Production reference projection and a new
physical lowering remain implementation work, with complete state, paid
planning, actual inputs, lineage and conformance checks still required.
