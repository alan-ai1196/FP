# Count coordinates for every phase of the unit simplex learner

Status: **PROVED, SCOPED; EXACT COMPLETE-STATE AUDIT**. The earlier
[predictive count theorem](WHOLE_HISTORY_PREDICTIVE_STATE.md) extends to all
fields of the reference learner and its native forward cache for the fixed
fair-prior, noise1/10 relation graph under the [registered simplex U](SIMPLEX_RUNTIME_CONTRACT.md)
with rate1 and one-event units. This is a mathematical representation result,
not by itself a Runtime integration, free resource quotient, new architecture action,
parameter-injection API or replacement for the failed AMP execution.

## 1. Fixed program, actual initialization and clocks

Fix n>=2, K=2^(n-1), the literal relation graph, Gamma=(1,1/K,...,1/K),
fixed feature slot0, selected slots1..K, and no delayed state. Only the
registered categorical current-pair source domain is used. Counts refer to
**events actually executed by this candidate**, including every profile
replay; they are not automatically the entire global observation history.
A newborn without a profile starts at the prior even at a late ordinary cut.

Let d be the signed unordered nonloop counts of **committed** events. Keep
the actual cursor c and optimizer step count s separately. They need not
coincide after a late birth or profile attachment. Also keep a tag alpha:
empty at a committed boundary, or the actual query/label(i,j,y) of the one
observed but uncommitted event. Define the encoding C=(d,alpha,c,s).

The pre-target query/cache and observation identity remain in their existing
surrounding event state. An observation must use the query of that actual
preceding prediction; the count representation grants no source/label
authority or permission to fabricate a different cache. Raw observations,
data-use identities, profile provenance, resource state and evidence remain
outside C and are not deleted.

## 2. Decode the complete state and cache

For each world z with z0=0, write

`a_z(d)=SUM_e d_e*1[z_i=z_j]`,
`w_z(d)=9^a_z / SUM_v 9^a_v`.

Decode theta=(1,w(d)), delayed state=(), cursor=c and optimizer_steps=s.
If alpha is empty, the full gradient accumulator is zero and unit_count=0.
If alpha=(i,j,y), put `I_z=1[z_i XOR z_j=y]`, `q=SUM_z w_z I_z`, and
`M=1+8*q`. The **actual ambient native CE gradient in every slot** is

`G_0 = 1/M - 1/5`,
`G_z = 4/5 - 8*I_z/M`.

Decode gradient_sum=(G_0,(G_z)_z), unit_count=1, and the same c,s.
To derive this, temporarily expose the feature parameter t at slot0:
`M_y=1+8*t*SUM_z w_z I_z` and `T=2+8*t*SUM_z w_z`.
Differentiate log(T)-log(M_y), then set t=SUM_z w_z=1. In particular,
`SUM_z w_z G_z = G_0`. The fixed feature derivative is the selected block's
exact weighted mean; it is not zero or disposable optimizer padding.

The full native forward cache is also determined by d and the actual query.
Its source values are the two one-hot vectors; its n^2 PRODUCT values are
the query-pair indicator; each world's two feature SUMs are its parity
indicators; the two final excesses are8*q_0,8*q_1. Masses are1+8*q_y,
normalizer10, probabilities M_y/10, and delayed outputs are empty. This
recovers every `Evaluation` field, not only the displayed probabilities.

## 3. The phase diagram commutes

Initialization sets d=0, alpha empty, c to the actual birth clock and s=0.
It decodes to the registered initializer. Prediction changes no learner
coordinate and its decoded cache equals native evaluation on the owned query.

Observation of its actual label sets alpha=(i,j,y) and increments c, while
leaving d,s unchanged. Section2 gives exactly the native observed gradient
state, including the fixed slot and the full uncommitted accumulator.

Commit increments d_{i,j} by1-2y if i!=j, leaves d unchanged on a diagonal,
clears alpha and increments s; c stays fixed. Indeed the registered exact
update is

`w'_z=w_z*(1-G_z+G_0)=w_z*(1+8*I_z)/M`.

This is exactly the posterior update represented by the count increment.
The explicit exact normalizing division is the identity. All gradient slots
clear together, and the full state equals the registered commit result.

An actual profile executes every replay through these same phases. At its
complete-unit endpoint, attachment changes only c to the ordinary birth
cursor. It preserves d, s and the empty accumulator, exactly as the reference
attachment rule requires. It cannot reset or once-count a repeated profile.

Induction therefore gives equality of every decoded reference learner state
and native cache along every legal finite continuation in this fixed family.
This is a transition simulation; C may retain redundant orientation/diagonal
event tags. No minimality of the uncommitted tag or equivalence of complete
Compiler states with different provenance/cost is asserted.

## 4. Information saved is not free decoding

For at most H committed candidate events, ||d||_1<=H. If the actual cursor
is at most Cmax, a simple abstract encoding uses at most

`m*ceil(log2(2H+1)) + ceil(log2(H+1)) + ceil(log2(Cmax+1))`
`+ ceil(log2(1+2*n^2))` bits,

with m=n(n-1)/2 and the model/layout fixed. This concerns C alone. It does
not remove stored data, graph code, physical evidence or decoder workspace.

The subsequent [forecast decoding complexity theorem](FORECAST_DECODING_COMPLEXITY.md)
now isolates a worst-case computational obstacle even for one scalar forecast:
a uniformly resolving polynomial-time decoder in n+H with error below2/5
would imply P=NP. Exact streaming enumeration has exponential time and
polynomial workspace. This is a compact-family bound, not a lower bound
polynomial in the already exponential literal graph size or on an RN-5 job.

Exact materialization can still be large. Subtract min_z a_z from every
exponent. The span is at most||d||_1, so positive integer weights lie between
1 and9^H and their sum is at most K*9^H. Exact decoded theta and gradients
need O(H+log K) bits per coordinate in the worst case. A direct decoder
enumerates K worlds, computes K*m indicator/count contributions, forms K
integer powers and normalizes them. Its exponential work and output space
are retained; neither a cheap inverse mean map nor a new FP space lower
bound follows from the count representation.

The [positive frontier decoder](POSITIVE_FRONTIER_DECODER.md) now exploits
structure within this same exact encoding. It normalizes positive edge
factors by variable elimination, then recovers the original cache and every
gradient coordinate. Its work is exponential in a witnessed anchored
elimination width, which can stay small even when the posterior has one
full-rank query component. Cycles give a linear decoder. Count input, order
search, integer bits and explicit K-entry output remain costs, and original
finite-arithmetic traces still require their own paid bridge. This is a
reference decoding improvement, not a new owned Runtime representation.

The [indexed literal reference](INDEXED_RELATION_REFERENCE.md) additionally
recovers the exact ordered Program, Gamma and selected-slot U without first
constructing their K-entry tables. Its complete point reader preserves the
same phase diagram and source orientation. Inference and full explicit
output have separate preflights; descriptor identity is not the literal
program hash, and owned Runtime admission remains a separate obligation.

A future physical lowering may retain counts and materialize rounded values
only when needed, so a temporary zero need not destroy persistent evidence.
It must bind counts to the actual Gamma, program, source events, clocks and
profile, pay for reconstruction and storage, guard count/arithmetic overflow,
and prove its own reference/AMP relation. At the initial927fb65 audit,
Runtime had no such representation or authority. The subsequent
[owned likelihood lowering](LIKELIHOOD_RUNTIME_CONTRACT.md) implements the
commensurate affine subclass with paid derivation and full phase evidence.
The [observed reversal failure](SIMPLEX_REVERSAL.md) at619e3cf remains a valid
outcome of its original persistent FP32 weights.

## 5. Boundaries and exact audits

Counts and theta alone fail at uncommitted cuts: an initial diagonal label0
does not change d or theta but creates gradient -4/45 in **every** slot,
unit_count1 and a later cursor. Omitting alpha or the two clocks is incorrect.

The ordinary signed counts also fail for other settings of the same registered
optimizer. At rate1/2 with one-event units, histories(0,1) and(1,0) on the same
nonloop query have identical d=0, cursor2 and steps2, yet first-world weights
77/170 and93/170. At rate1 with two-event units, histories(0,0,0,1) and
(0,1,0,0) have the same d=2, cursor4 and steps2, yet weights61/82 and9/10.
These are within-contract order counterexamples, not comparisons of two
different update schedules. A generic simplex learner cannot adopt C merely
because its optimizer name matches. Unknown noise, arbitrary priors/graphs,
other sources or delayed states also require their own complete proof.

Run `python -B experiments/joint_uncertainty/count_learner_encoding.py`.
The independent decoder uses integer count powers and the closed gradient/
cache formulas, while the reference side executes native evaluation,
reverse-mode observation, registered commit and profile attachment. It checks:

- all585 histories through depth3 at n2 and343 through depth2 at n3;
-32 n4 path/cycle/diagonal/reversed-query traces;
-1,146 complete native caches,1,146 full observed states and1,146 full
  committed states, including three one-/two-/three-pass profiles;
- a100-event reversal from a late birth, preserving cursor107 and steps100;
- the uncommitted diagonal gradient and both order counterexamples;
- invalid phase/attachment, world-cap and pre-power integer-budget refusals.

The audit imports no Torch and issues no Runtime or physical certificate.
