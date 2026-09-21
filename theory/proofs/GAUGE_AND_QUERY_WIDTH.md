# What changing the anchor can and cannot save

Status: **proved for the declared complete binary bucket class; exact audit**.
This is a refinement of the [query-order resource law](QUERY_ORDER_RESOURCE_FRONTIER.md),
not a change to Runtime's anchor, numerical schedule or native learner.
It closes a possible overinterpretation of the old fixed-anchor lower bounds
and tests whether anchor selection alone removes the hard model cuts.

## 1. The gauge changes coordinates, not the native state

Let G be the active signed-count graph on n>=2 vertices and let the query
have distinct endpoints u,v. For an anchor a, set w_i=z_i XOR z_a. This maps
assignments with z_0=0 bijectively to assignments with w_a=0. The inverse is
z_i=w_i XOR w_0. Every edge parity and query parity is unchanged.

The positive weight

`W(z) = PRODUCT_(ij) 9^(max(d_ij,0) if z_i=z_j else max(-d_ij,0))`

is therefore unchanged term by term. Both unnormalized query partition
sums are identical under any anchor. A local vertex permutation can put
the chosen anchor at index zero, provided every edge/count address and
query endpoint is mapped consistently. The original complete count vector,
parameter interpretation, source indices, clocks and future interface stay
in their original coordinates. This argument grants no mutable alias,
unpaid search, information erasure or floating-word equality.

## 2. Exact query-width law

The decision class fixes complete binary factor tables and the original
positive bucket join/sum schedule. It allows any anchor a and any elimination
order that retains the free query endpoints until the final join. It does
not allow factoring, conditioning, streamed contractions or a different
arithmetic interpreter. Define J_a as the minimum largest joined table,
including the final query table, over all such orders at a. Other resource
caps are not imposed in this definition.

Let H be G with edge uv added if absent. Then

`J_a = 2^(tw(H-a)+1)`.

Here tw is the usual treewidth: minimum largest bag size minus one over
tree decompositions. The standard bag and elimination characterizations are
background, described by [Bodlaender and Koster](https://doi.org/10.1093/comjnl/bxm037).
The following argument explains the query and anchor specialization.

Pinning a makes its incident factors unary. Their presence affects work
and tape costs, but adds no edge among the free variables. Joining a bucket
and summing its eliminated variable makes its remaining neighbors a clique.
Thus its table has 2^(d+1) entries when it has d remaining neighbors. The
terminal table has 2^|Q| entries for Q={u,v}\{a}.

Adding edges within the retained Q does not change any earlier eliminated
variable's neighbor set: these vertices are never internal vertices of an
eliminated path. A bucket order followed by the vertices of Q consequently
gives an elimination order of H-a with width at most log2(J)-1. This proves
the lower bound in the displayed equality.

Conversely, take a minimum-width tree decomposition of H-a and root it at
a bag containing Q. Such a bag exists because Q is either a single vertex
or the endpoints of its added edge. Eliminate vertices in leaf bags that
are absent from their parent, then remove each exhausted leaf. Their later
neighbors, including any fill, stay within the corresponding bag. Repeat
toward the root and eliminate its non-Q vertices last. This leaves Q until
the end, without exceeding the decomposition's width. The corresponding
bucket tables and final query table therefore fit 2^(tw(H-a)+1), proving
attainment. This is an existence proof, not a free order-search algorithm.

Deleting one vertex decreases treewidth by at most one: deleting it from
every bag gives one inequality, and adding it to every bag of a decomposition
of H-a gives the other. Writing t=tw(H),

`2^t <= J_a <= 2^(t+1)` for every a,

and hence `max_a J_a <= 2 min_a J_a`.

The factor of two is tight. Take a K4 on vertices1,2,3,4 and connect vertex0
to1 and2, with query(0,3). Pinning0 leaves a K4 and requires a16-cell join;
pinning3 permits an8-cell order. The same graph shows that either query
endpoint need not be equally good. A complete K_n instead requires
2^(n-1) entries at every anchor. There is no general anchor choice that
removes exponential width.

This law concerns the optimum maximum joined table only. Live coexistence,
total arithmetic, syntactic power aliases, retained nodes, output words,
search work and rounded accuracy have separate costs. In particular, it
does not bound their ratios by two or certify joint feasibility.

## 3. Independent exact checks

Run `python -X utf8 -B theory/resource_checks/query_anchor.py`.
The [minimal report](../../evidence/minimal/FP_QUERY_ANCHOR_RESOURCE.json) retains:

- All 1,098 simple supports on n2 through n5 and 10,650 nonloop query
  states. Direct bucket geometry over 186,700 orders agrees with an
  independent clique-fill treewidth enumeration on all 52,812 anchor
  decisions. Every factor-two inequality passes; 8,162 query states attain
  the factor-two variation across anchors.
- All 759 ternary signed-count states on n2 through n4. The explicit gauge
  map has 23,664 checked world images and an exact inverse. Direct global
  world sums agree with all 29,664 relabeled positive partition pairs,
  including diagonal queries and negative counts.
- Every anchor at four exposed whole-program n16 query blocks. The existing
  proved subset recurrence minimizes outputs then nodes at each anchor.
  Every feasible witness is directly compiled and its full structural cost
  checked. A failed 4,096-cell class is checked again with a vacuous
  2^20-cell live allowance before reporting a join-only lower bound.

Output and node counts use the partition-only tape and fixed 38-output
preparation/readout of the query-order law.

The last relaxation is nonbinding: at most120 original factors and15
component factors give W(S)<=480+15*32768; a4,096-cell transition adds only
6,144 cells. Thus the relaxed refusal does not conceal a live-memory limit.

| Model cut / query | Anchors with no 4,096-cell order | Best output count under 4,096/32,768 caps | Consequence |
|---|---:|---:|---|
| c4/18, cursor276 / (2,5) | 6 of16 | 65,574 | Every feasible anchor still exceeds65,536 outputs; either query endpoint has no legal join order |
| c2/17, cursor332 / (8,7) | 4 of16 | 30,758 | Anchor0 refuses, but anchor1 or7 attains30,758 outputs and184,831 nodes |
| c4/18, cursor372 / (15,1) | 16 of16 | none | Minimum join over all anchors is8,192, with a checked matching anchor0 order |
| c4/19, cursor368 / (4,13) | 16 of16 | none | Minimum join over all anchors is8,192, with a checked matching anchor0 order |

These are retrospective mathematical cuts, not continued executions of
the halted workers. They falsify a general query-endpoint anchoring repair
and strengthen two old join obstructions to the entire anchor/order class.
They also show why a fixed-anchor refusal must not be advertised as an
all-anchor lower bound: the c2/17 cut has an explicit counterexample.

## 4. Consequence for the research frontier

The current native learner needs no modification. Paid order selection can
still recover some refusals, and a changed anchor is a legal exact decoder
coordinate choice. Neither alone proves completion under all the existing
caps. Deployment would need paid search, complete address binding, its own
declared rounded schedule and the normal ownership/AMP gates. This audit
adds none of those mechanisms to Runtime and supplies no new
`CERTIFIED_COMPLETE` or all-decoder impossibility claim.
