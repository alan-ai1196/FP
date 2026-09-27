# Incremental token gradients need complete floating continuation state

The next owned AMP integration exposed two concrete constraints. The passive
Torch schedule creates allocations outside the existing fixed CUDA arena;
merely registering it cannot meet that arena's contract. Its observation
kernel also recomputes every revealed prefix. The new incremental schedule
removes repeated derivative evaluation, while retaining the floating state
that later updates actually use. It remains a component awaiting arena and
Runtime integration, not a new release or a language-model result.

## 1. The old schedule cannot silently become an event accumulator

The v1 physical kernel reduces each core-edge gradient across events before
combining tied slots. Its embedding reduction orders occurrences by lag,
then by event. Computing a one-event gradient first and then accumulating
events changes association and sometimes order. Floating addition is not
associative, so this would change the physical learner even when its real
arithmetic formula is unchanged.

The new, separately named schedule is
`token-half-core-event-gradient-sparse-balanced-carry-integer-grid-v2`.
It reuses the complete half/single one-event forward and reverse operations.
For each event it produces a core gradient, readout common/correction vectors,
and a gradient for each embedding row occurring in that context. It then
reduces those vectors in event order, using the balanced reduction specified
below. Correction rows receive leaves only on their actual target events;
embedding rows receive leaves on their actual context occurrences after the
complete one-event tied derivative. A present row is retained even when its
computed derivative is zero. Earlier inactive-row gradients remain stored.

All native parameters and all original source/target records remain. In exact
real arithmetic, these leaves sum to the same native gradient: event-local
derivatives add while the unit's masters are fixed. The forward operations,
straight-through cast derivative and integer-grid commit formula are unchanged.
In finite arithmetic this is a new lowering; old device journals and bridge
claims do not authorize it. In the small audit, 73 of 384 prefixes actually
have different gradient words from v1. This is a measured difference, not an
assumed equivalence or a Foundation counterexample.

## 2. Exact reduction law, including the ragged right spine

Fix finite binary32 vectors and a registered RNE32 addition operation. A
balanced reduction adds adjacent pairs at each level and carries an unpaired
last vector unchanged. After n append operations, retain perfect subtrees
whose sizes are the set bits of n, in decreasing order. Appending a leaf
merges only consecutive equal-sized trees, as in a binary counter.

**Theorem, conditional on the specified finite RNE32 operations.** Every
retained block equals the perfect balanced tree over its consecutive leaves.
The full prefix result is obtained by folding the blocks **from the right**.
Consequently it is bit-for-bit identical to the registered balanced reducer,
including signed zeros. A left fold is not the same tree in general.

Proof: the append step preserves consecutive intervals and replaces two
adjacent perfect trees of size 2^k with exactly their common parent. Induction
establishes every block. The balanced reduction's largest perfect left subtree
has size equal to the largest set bit of n; its remaining right subtree is the
same reduction on the suffix. Recursing on that suffix gives the right fold.
Only equality of the executed expression trees is used, not associativity.

For one coordinate stream of N leaves:

- Carry maintenance uses exactly `N - popcount(N)` additions in total.
- A prefix root read uses exactly `popcount(n) - 1` additions.
- The current frontier stores `popcount(n)` vectors, at most
  `floor(log2(n)) + 1`; an append has at most `floor(log2(n))` merges.
- Reading every prefix therefore costs O(N log N) additions, compared with
  `N(N-1)/2` when independently rebuilding all balanced reductions.

This is an exact operation law for this reducer, not a universal lower bound
for FP or a total-memory theorem. Each perfect tree needs one evaluation per
internal addition node under the registered tree evaluator; carry maintenance
attains that count. Immutable historical states, event workspaces, row keys,
metadata copies, source records and future diagnostic accesses have separate
costs. The implementation currently copies/sorts sparse row metadata and an
explicit diagnostic view materializes all old event columns. No linear bound
for the whole process or isolated wall-time speedup is claimed.

The derivative schedule evaluates one new event per observation, N per full
unit. The old prefix recomputation evaluates `N(N+1)/2` derivative columns.
Its batched vectorization and the new schedule's launch overhead mean that
this arithmetic reduction alone is not a GPU throughput comparison.

## 3. A current sum is not the complete continuation state

**Exact binary32 counterexample.** Consider three leaves

`A = (-2, -1, 1)` and `B = (-2, -2, 2)`.

Both exact sums and both current balanced floating results are -2. Their
frontiers are respectively `(-3, 1)` and `(-4, 2)`. Append the same leaf
`delta = 2^-23`. The next balanced results are

`RNE32(-3 + RNE32(1 + delta)) = -2 + delta`,

`RNE32(-4 + RNE32(2 + delta)) = -2`.

The second inner addition is a half-ULP tie at 2 and rounds back to 2. Thus
even the pair (exact current sum, physical current sum) cannot replace the
frontier for arbitrary future appends. This is a counterexample to a reducer
state quotient; it does not assert these triples are particular token losses.

The token audit also performs a direct cache attack. At a real three-event
prefix it replaces the two core frontier values by `(current_root, 0)`, keeping
their sizes 2 and 1. Every current ordinary parameter/gradient coordinate is
unchanged, so the old basis-only numerical predicate passes. Independent
complete cache replay rejects the substitution. The old predicate's original
scope is unaffected; it cannot validate these new continuation caches.

## 4. What an owner must prove

The physical state is the independent AMP origin, all event records and
workspaces, plus every core/common/sparse-row frontier. A materialized
`Basis`, or an old-format diagnostic `amp.Pending`, lacks those future-used
frontiers and must not become the live state or an issued complete bridge.

The invariant suitable for an efficient owner is stronger than root closeness:
each block has its declared leaf interval and contains the RNE32 tree value
for the actual retained one-event derivatives. It can be maintained by
induction if the owner:

1. Binds each one-event execution to the actual independent AMP masters,
   original causal context, pre-target forecast and revealed target.
2. Keeps previous blocks and event records in immutable owned storage.
3. Executes and checks every new carry merge, in the declared order, into a
   fresh admitted extent; it never overwrites an old block.
4. Uses the right-fold decoder for gradient coordinates and the declared
   integer-grid update only at a complete unit boundary.

Under that invariant, records and clocks plus the old numerical coordinate
predicate can support the new complete state relation. Without it, a root
comparison is insufficient. The current `audit_cache` checks the invariant by
independent CPU replay of every event and every block; that diagnostic replay
is deliberately not advertised as an affordable online checker. Failure after
target reveal retains the previous complete state, forecast, actual source,
new target and any completed one-event derivative workspace.

The necessary next implementation is the array event executor inside the
existing owned arena, followed by the inductive cache/coordinate relation in
ReferenceCompilerRuntime. The existing arena already has admitted immutable
float32 outputs for addition; indexed reads, integer masters and complete
token phase binding still need their registered lowering. No allocation
monitor is disabled and no passive Torch allocation is accepted as owned.

## 5. Evidence and scope

`scripts/audit_streaming_token_amp.py` and the compact
`evidence/minimal/FP_STREAMING_TOKEN_AMP_CPU.json` establish:

- All 257 prefixes of an eight-coordinate dyadic fixture match an independent
  balanced reducer: 255 carry additions plus 770 root additions, versus
  32,896 full-prefix additions per coordinate. Maximum live frontier: eight
  blocks. Exact primitive checks include the continuation counterexample.
- Ninety-six token histories pass 384 observations, 768 pre-target label
  checks, 144 independent AMP commits and native complete-coordinate bounds
  under the unchanged small-fixture tolerance 1/4. Each observation computes
  one new derivative; every retained leaf and frontier is replay checked.
- The exact CPU oracle verifies 386,094 event/control primitive words,
  including 52,608 half words. The maximum audited pending-coordinate error
  is `6177854496051201/4722366482869645213696` (about 1.31e-6); the separate
  maximum committed-master error is 1/32, one small-fixture grid unit. Small
  pending error therefore does not imply an identical floor-grid commit.
- Sixty-four reversed/repeated profile events preserve original source
  positions and the separate learner clock. Forged current-sum caches and
  wrong predecessor identities refuse; a forced carry failure retains the
  new target and the completed event workspace.

No corpus, Torch, GPU, model score or old terminal job is used by this audit.
This addresses a specific online arithmetic and completeness obstacle. It
does not reopen the relation-task branch or authorize more static readout
variants; ordinary text training remains the objective.
