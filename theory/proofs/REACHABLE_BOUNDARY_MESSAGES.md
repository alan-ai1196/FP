# Higher-order boundary information arises in the actual count learner

Status: **PROVED CONSTRUCTION; EXACT SYMBOLIC AND OWNED CPU AUDITS PASS**.
This strengthens the [finite-future boundary law](QUERY_BOUNDARY_RESPONSE.md).
Its strictness is not restricted to arbitrary supplied boundary tables:
legal histories of the existing uniform-prior, noise1/10, unit-simplex
relation learner realize pure higher-order boundary interactions.

The original native program, Gamma and U stay fixed. The bipartite graph
below describes the posterior's active count factors, not a newly installed
architecture. Every nonzero count is produced by one legal observation.
No parameter, message or trained endpoint is injected into Runtime.

## 1. A family of legal histories

Choose an even boundary size b>=4 and put m=2^(b-2). Use n=b+m vertices:
boundary vertices0,...,b-1 and m additional vertices. For p in{+1,-1},
form the m sign vectors

`S_p = {s in{+1,-1}^b : s_0=+1, PRODUCT_i s_i=p}`.

Associate one additional vertex h_s with each s. Observe once on each pair
(i,h_s), with label0 when s_i=+1 and label1 when s_i=-1. The two histories
use the same b*m query pairs; only labels differ. Every label word has
positive probability under the declared noisy model. All these edges have
count magnitude1, all other counts are zero, and both clocks advance by
exactly b*m. The complete [count/native phase identity](COUNT_LEARNER_ENCODING.md)
therefore proves reachability from the same uniform initializer.

These are mathematical finite histories, not a claim that all sizes fit a
fixed resource registration. The current indexed realization still has its
n<=1024 guard. The actual owned audit below uses n8; larger symbolic checks
do not claim executed large Runtime histories.

## 2. The boundary message has only one nonconstant character

Write sigma_i=(-1)^z_i for boundary spins. For a fixed s and boundary
assignment, let r count the indices with s_i=sigma_i. Summing its additional
spin out gives the positive response

`f_r = 9^r + 9^(b-r)`.

Since f_s=f_-s, the representative convention s_0=+1 does not affect the
product over sign-vector pairs. Multiplying the boundary assignment by any
even sign pattern permutes S_p modulo these pairs. The product message
M_p consequently depends only on `chi=PRODUCT_i sigma_i`. Flipping one
boundary sign exchanges M_+ and M_-. Their two parity values are swapped.

Let A be M_+ at chi=+1 and B be M_+ at chi=-1. One explicit integer formula
is: for r<b/2, include `f_r^binom(b,r)` in A for even r and B for odd r;
at r=b/2 include `f_r^(binom(b,r)/2)` in the corresponding parity product.
Thus the normalized boundary laws have the form

`mu_+ = (1+a*chi)/2^b`, `mu_- = (1-a*chi)/2^b`,
`a=(A-B)/(A+B)`.

All factors and messages are strictly positive, so |a|<1. What remains is
to prove a!=0 at the fixed, discrete likelihood ratio9; an unspecified
generic-coupling argument would not establish this learner's reachability.

## 3. A discrete nonvanishing proof

Let v3(x) be the exponent of3 in a positive integer x. Directly,

`v3(f_r) = 2*min(r,b-r)`.

This also holds at r=b/2 because f_r=2*9^(b/2). Therefore

`v3(A)-v3(B) = SUM_(r=0)^b (-1)^r binom(b,r) min(r,b-r)`
`= 2*(-1)^(b/2) binom(b-2,b/2-1) != 0`.

For completeness, set b=2k, pair terms at r and2k-r, and apply Pascal's
identity to `(2k-2r)binom(2k,r)`. The two resulting alternating partial sums
are `(-1)^(k-1)binom(2k-2,k-1)` and
`(-1)^(k-2)binom(2k-2,k-2)`. The valuation difference is minus2k times
their sum. Using the ratio(k-1)/k of the adjacent binomial coefficients
gives the displayed identity. Distinct
3-adic valuations imply A!=B. This is exact integer algebra, not a numerical
nonzero test or an added arithmetic primitive in the learner.

Hence every even b has two count-reachable boundary messages whose only
nonconstant Fourier coordinate is the full b-spin character.

Marginalizing auxiliary spins into higher-order interactions is established
background; see [Generalized Transformation for Decorated Spin Models](https://arxiv.org/abs/0809.4710).
The relevant additional obligations here are the fixed likelihood ratio9,
unit count magnitudes, legal native histories and the discrete nonvanishing
argument. General decorated-spin transformations are not claimed as novel.

## 4. A sharp native boundary horizon

By the finite-future law, the two boundary states are indistinguishable
after at most `h=b/2-2` boundary observations. Append label0 on b/2-1
disjoint boundary pairs and query the final pair. The forecasts are

`1/2 +/- a*(4/5)^(b/2)/2`.

Since a!=0, they differ. This realizes every strict horizon level using
the existing count-native family, with b=2h+4. The full native state is
not equivalent at the earlier cut: queries involving additional vertices
and explicit parameter reads can distinguish it. The equivalence statement
is confined to the declared boundary interface and horizon.

The arbitrary-message finite-grid information lower bound in the companion
proof remains separately scoped. This construction supplies two reachable
classes at each horizon; it does not show that every arbitrary table or all
independent coefficient grids are count-reachable. Nor does a higher-order
interaction require a dense table: these messages themselves have compact
symbolic descriptions. Full counts already preserve the required information.

The subsequent [independent grid construction](REACHABLE_BOUNDARY_INFORMATION.md)
attains L^D_h(b) count-reachable h-response classes using a different
exponential family. Thus the arbitrary-message lower bound's class count
is reachable, although the particular linear table grid is not asserted
reachable. That stronger result also separates response dimension from
precision using a two-path native counterexample.

## 5. Small actual owned witness

For b4 there are four additional vertices, sixteen actual observations and
n8 in the fixed native relation program. The integer message values are

`A=(9^4+1)*(2*9^2)^3 = 27,898,526,736`,
`B=(9^3+9)^4 = 296,637,086,736`.

Thus |a|=1280000/1545761. All six current boundary pair forecasts are
exactly1/2. After the same actual observation(0,1,0), the owned pre-target
forecast for(2,3) is respectively

`726561/3091522` and `2364961/3091522`.

The [exact audit](../../evidence/minimal/FP_REACHABLE_BOUNDARY_MESSAGES.json)
executes both histories through the existing `ReferenceCompilerRuntime`:
actual byte ingress, observations, independent literal native reverse
gradients, complete state comparisons and paid packed leases. Each case
checks18 full native caches,17 observed states and17 committed states,
including every parameter and gradient coordinate. The final target is
unrevealed. Each current packed root is312,911 bytes. This is a reference
execution result, not a measurement of total RAM or a GPU/model advantage.

For b4,b6,b8,b10, independent positive star sums match the closed integer
products and have exactly the stated Fourier support. Valuation differences
are4,-12,40,-140. The corresponding mathematical histories contain
16,96,512,2560 observations, always one per nonzero edge. Only the b4
histories are reported as actual owned Runtime executions.

Run `python -X utf8 -B experiments/joint_uncertainty/reachable_boundary_messages.py --write`.
Evidence retains the small sixteen-event histories, aggregate comparisons,
and nonvanishing witnesses. No full weights, cache or dataset is dumped.

The implementation consequence is precise: current pair moments on a
selected boundary cannot certify complete future response, even when the
global posterior comes from the native pairwise count learner. Current-query
projection remains valid because it retains global counts and recomputes
from the actual future input. Foundation R4 and ERC-1 are unchanged.
