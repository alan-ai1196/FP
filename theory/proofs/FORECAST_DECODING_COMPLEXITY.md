# Compact likelihood memory does not give a cheap forecast decoder

Status: **PROVED, SCOPED CONDITIONAL COMPLEXITY THEOREM; EXACT EXHAUSTIVE AUDIT**.
This is a computational consequence of the existing fair-bit, noise1/10
relation learner and its [complete count encoding](COUNT_LEARNER_ENCODING.md).
It changes neither Foundation R4, ERC-1, the native unit simplex U, nor the
current experiment. It concerns one forecast, even before paying to emit
the complete exponentially long native state.

## 1. Model, input size and claim

There are n>=2 fair latent bits. Fix z0=0 to remove the global flip, leaving
K=2^(n-1) equally weighted worlds. Every pair is a legal query. A label y on
(i,j) has likelihood9/10 if z_i XOR z_j=y and1/10 otherwise. All finite query
and label words have positive probability. For a history h, let

`p_h(i,j) = 1/10 + (4/5) Pr_h[z_i XOR z_j=1]`.

The actual unit simplex native learner has this posterior, by the earlier
complete phase simulation. Its exact native normalizer stays10 throughout;
the computational obstacle does not require growing native activations.
Committed signed counts d_e increment by1-2y.
They occupy O(n^2 log(T+1)) bits after T labels; the ordinary clocks and any
pending event remain separate. No observation, provenance, physical graph,
full reference state, or installed resource ownership is erased here.

**Theorem.** Fix any rational e with0<=e<2/5. A uniform deterministic decoder
which always returns a rational p_hat satisfying

`|p_hat - p_h(i,j)| <= e`

for every n, every legal finite history h and every pair, in time polynomial
in n+T, would imply P=NP. This includes a decoder receiving only n and the
compact counts, and a learner receiving the actual history. Any preprocessing
must be included in the polynomial bound. A promise allowing unresolved
answers on hard inputs is not the premise of this theorem.

The parameter is the **compact model family**, specified by n and its fixed
likelihood rule. The literal native world graph already has exponential size
in n. Polynomial time in that expanded graph's size is not ruled out. No
uniformly exponential time lower bound, finite-machine impossibility, or
hardness of a particular RN-5 worker follows from P!=NP.

A separate [positive partition-decoder law](POSITIVE_COUNT_PARTITION.md)
now gives an unconditional2^Theta(n) circuit bound for a narrower computation:
a fixed positive arithmetic DAG returning the exact unnormalized partition
from bounded edge factors over all finite count histories. It does not turn
this theorem into an unconditional lower bound on normalized forecasts,
approximate algorithms or finite resource contracts.

## 2. Reduction using only actual finite labels

Take an unweighted simple graph G on n vertices, with m edges. Let C(z) be
its cut size and C* its maximum. Unweighted Simple MAX CUT is NP-complete;
this restriction is essential because expanding binary-encoded edge weights
into repeated labels would not in general be polynomial. The primary result
is [Garey, Johnson and Stockmeyer, *Some simplified NP-complete graph problems*,
Theoretical Computer Science 1 (1976), 237-267](https://doi.org/10.1016/0304-3975(76)90059-1).

Put gamma=1/2-e/(4/5)>0. Choose the least integer M>=0 with

`gamma * 9^M >= 2^n`.

Integer multiplication and rational comparison find M without a floating log.
Here M=O(n+log(1/gamma)). Observe M copies of label1 on every edge of G.
After cancelling common positive factors, the actual posterior weight is

`W(z) = 9^(M*C(z))`.

For i=1,...,n-1, request the decoder's forecast at(0,i). Choose b_i=1 when
p_hat>=1/2 and b_i=0 otherwise. Then observe M copies of label b_i at(0,i).
All these are legal pair/target events in the same model, with the same U,
prior and noise. The reduction makes at most n-1 forecast requests and
uses exactly M(m+n-1) labels. An anchor pair occurs at most once as an
original edge and once as a forcing group, so every |d_e|<=2M.

This is a reduction among conditional forecast problems. It is not an
instruction to let a Runtime choose its own targets or to submit these
adaptive oracle choices as branch-invariant fresh statistical evidence.
Every queried finite history is possible; no fresh certificate is asserted.

## 3. Why every permitted decision retains a maximum cut

Suppose a prefix of s chosen anchor relations is consistent with at least
one maximum cut. This is true at s=0. Let F_s(z) count satisfied prefix
relations. The posterior weights are now exactly

`W_s(z) = 9^(M*(C(z)+F_s(z)))`.

Call a world good if it is a maximum cut satisfying all s choices. Every
good world has score C*+s. Any other world has integer score at most C*+s-1:
either its cut is smaller, or it violates a prefix relation. In particular,
no large forcing constant proportional to m is required. If a good world
exists, the total posterior mass of bad worlds is at most

`K / 9^M <= gamma/2 < gamma`.

Write r=Pr[z_i=1] for the next anchor query. Its noisy forecast is1/10+(4/5)r.
If p_hat>=1/2, the error promise implies r>=gamma. If p_hat<1/2, it implies
1-r>gamma. Thus the selected branch has mass at least gamma, strictly more
than the entire bad set. It contains a good world. Induction retains a
maximum cut at every choice, and the final n-1 bits specify one completely.

For fixed e the reduction has polynomial length and arithmetic cost. A
polynomial decoder would therefore find a maximum cut and decide its
NP-complete threshold problem in polynomial time. This proves the theorem.
The labels add positive likelihood factors only; negative signed counts do
not introduce negative SUM or PRODUCT coefficients.

A randomized decoder with a uniform per-input success probability at least
2/3 and polynomial running time has the analogous consequence NP=RP.
Repeat and take medians to make all n-1 adaptive answers accurate with
probability at least2/3. Always verify the returned cut against the requested
threshold. No negative instance can then produce a false positive.

## 4. Sharp accuracy threshold and a paid upper bound

At e=2/5 the constant decoder p_hat=1/2 works for every query and history,
because every noisy forecast lies in[1/10,9/10]. Hence the accuracy threshold
in the theorem is sharp. For example, a graph containing only edge(1,2) at
n=3 defeats the preceding algorithm with this constant decoder: its tie rule
sets both nonanchor bits to1 and returns cut0 instead of the optimum1.
This does not assert that a useful decoder with error2/5 must fail.

An exact decoder with exponential time and polynomial working space does
exist for one forecast. Set L=sum_e |d_e|<=T and c=sum_e min(d_e,0). For
each of the K worlds, compute

`a_z = SUM_e d_e*1[z_i=z_j] - c`, so `0<=a_z<=L`.

Stream the positive integer mass9^a_z into a total and a matching-parity
total, then form the noisy rational probability. Each total has O(T+n)
bits. Enumeration, fixed-base integer powers and addition take
2^n poly(n,T) bit operations with poly(n,T) working space. This is an
algorithmic upper bound, not a proof of optimal exponential time.

The distinction is now explicit: compact sufficient information can support
a polynomial-space exact decoder while a uniformly resolving polynomial-time
decoder at any error below2/5 would collapse P and NP. The full native cache
still has its own output-size cost. Neither result licenses a free decoder
inside the complete Compiler or a forecast copied into its installed state.

## 5. Exact evidence and scope boundary

Run `python -B experiments/joint_uncertainty/forecast_decoding_hardness.py`.
The [minimal report](../../evidence/minimal/FP_FORECAST_DECODING_COMPLEXITY.json)
retains aggregates, not graph datasets or posterior dumps. It checks all
1,098 simple graphs on2..5 vertices at errors0,1/1000,39/100 and399/1000.
Across32,089 adaptive states it explores **every** decision allowed by the
error interval, including the correct strict/non-strict threshold boundary.
All8,617 terminal assignments are optimal. Each state independently compares
its ordered likelihood products with the signed-count formula, verifies
the concentration inequality and checks history/count bounds.

Twenty small graph/error settings also execute183 complete native
predict/observe/commit units and36 native decision queries, checking actual
weights, empty committed gradients and both clocks. All arithmetic is exact;
native operations use the32768-bit reference guard. The proof, rather than
finite enumeration, supplies the general complexity statement.

The histories are adversarial and can be extremely unlikely. This theorem
does not establish average-case hardness, an IID score lower bound, learned
unknown-noise behavior, a matched model advantage, or a resource explanation
for the current n16 timeouts. It identifies a real worst-case computation
obstacle after information preservation has been solved. Structured solvers,
certified approximations and honest UNRESOLVED outcomes remain appropriate
without changing the FP semantics or expanding the parked static program.

The subsequent [unknown-noise theorem](UNKNOWN_NOISE_DECODING.md) removes
the supplied-rate premise for a fixed finite positive rate prior. A legal
diagonal calibration prefix protects concentration through every bounded
continuation used in the reduction. Its sharp threshold is1/2-eta_min;
the rare-history and compact-family scope restrictions remain.
