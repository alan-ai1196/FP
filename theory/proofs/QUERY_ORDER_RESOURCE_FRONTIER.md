# Exact resources over the query-retaining order class

Status: **THEOREM for the declared bucket/tape class; passive exact audit**.
The complete indexed model attempt motivates this analysis. It does not
change its registered source, caps, operation order or failed outcomes.
Foundation R4 and ERC-1 remain frozen.

The earlier [positive frontier decoder](POSITIVE_FRONTIER_DECODER.md)
characterizes order width. Width alone does not decide whether an order
fits the indexed AMP tape and floating-output allowances. Here both costs
can be optimized over a finite order class without executing a posterior
or constructing every candidate tape. This is an algorithmic resource
result, not a new semantic architecture action or a Runtime certificate.

## 1. Exact decision class and subset state

Fix an active signed-count support, pin its anchor to zero, and retain
the distinct free query endpoints Q. The class contains every permutation
of the other free vertices. Each order uses the existing positive binary
bucket joins, binary sums, complete factor tables, syntactic power aliases,
partition-only tape and indexed scalar readout. It permits no factoring,
changed anchor, alternate arithmetic, zero/addition elimination, truncation,
evidence encoding change or numerical fallback. Count magnitudes affect
values and exponent guards, but not the costs below.

Let S be the eliminated vertex set in the anchored free graph. Its current
factor-scope multiset is exactly

`F(S) = A(S) disjoint-union { boundary(K) : K is a component of G[S] }`,

where A(S) contains original factor scopes disjoint from S, with their
multiplicity. Anchored edges give unary factors. A component with empty
boundary still contributes a scalar factor; it cannot silently disappear.
An isolated eliminated vertex also contributes its summed scalar factor.

Proof: initially the assertion is immediate. Eliminating v joins its
remaining original incident factors and exactly the factors of eliminated
components adjacent to v. The resulting factor has the boundary of their
merged component in S union {v}. All other factors remain. This proves the
claim inductively, including empty buckets and boundaries. In particular,
the multiset depends on S, not its internal elimination order.

Original factor entries carry a syntactic power proof. Every component
factor has undergone a binary addition and carries no such proof under
the declared interpreter. This statement concerns the fixed power tags,
not whether a particular rounded value happens to equal a radix power.

## 2. Transition and complete-tape laws

For the next vertex v, let a be its number of original bucket factors and
b its number of component bucket factors. Let X contain v and every
variable in those factors, and let j=2^|X|. The exact transition counts are

`M=(a+b)j, A=j/2, G=max(b-1,0)j`,

where M counts all positive multiplication nodes, A counts addition nodes,
and G counts products without a syntactic power operand. Every table entry
joins all a+b factors from the unit value. Only the second and later
non-power operands require general products; interspersing power operands
does not change their count. The binary elimination adds each pair once.

Write `W(S)=SUM_(f in F(S)) 2^|f|`. The logical table peak of this transition
is `W(S)+j+j/2`. At the terminal set S=V\Q, use j=2^|Q|, a=|A(S)| and b
equal to the number of components of G[S]. The final join and parity sums
instead cost

`M=(a+b)j, A=j, G=max(b-1,0)j`,

with logical peak W(S)+j. These are the existing table schedule's logical
cells, **not** the retained AMP tape, arena extent or process memory.

Let F be the total initial factor-table cells and sum the counts over
all transitions, including the terminal one. The partition-only tape has
exactly

`N = 3 + F + SUM(M+A)` nodes,

`C = 38 + 4 SUM(A) + 6 SUM(G)` floating outputs,

including `3 SUM(G)` half outputs. The three constants and the fixed
38-output preparation/readout are retained. The old global compiler's
additional two mass heads add four nodes and eight floating outputs;
neither is subtracted when analyzing that older schedule.

For the existing projected block path, optimize each local anchored block
separately. With c=max(number_of_blocks-1,0), positive convolution gives

`N = 3 + SUM_b(N_b-3) + 6c`,

`C = 38 + SUM_b(C_b-38) + 32c`.

Every local parity head has an addition tag, so each convolution has four
general products and two additions. Diagonal or disconnected responses
have no blocks, N=3 and C=38. The eight-cell logical convolution allowance
must still fit; each local search receives that reduced live-cell budget
when there is more than one block. The complete count scan and retained
global state are not removed.

## 3. Exact finite optimization, with a limited conclusion

Restrict each transition and the terminal join to the declared join and
logical live-cell caps. A subset dynamic program stores the lexicographically
least pair `(4 SUM(A)+6 SUM(G), SUM(M+A))` for each S. All future costs and
admissibility depend only on S, so replacing a prefix by its lesser pair
cannot harm any continuation. Induction over subset size proves both
attainment by the recovered order and the matching lower bound over
**all orders in this exact class**. An unreachable terminal set proves that
no class order fits those two table limits.

The terminal constants give the minimum C; among orders attaining it, N is
also minimum. Thus C above the output cap proves infeasibility even if every
order is searched. If both C and its N witness fit their respective caps,
that order witnesses all four structural limits. If C fits but this N does
not, joint feasibility is still UNRESOLVED: an order with larger C and
smaller N may fit. This algorithm must not claim a Pareto frontier or all-
decoder optimum it has not computed. Reversing the lexicographic objective
gives the exact minimum N, with C as its tie-breaker. The same proof applies.
That second objective is needed for a byte lower bound; a tape minimizing
outputs alone need not minimize its stored nodes.

The passive implementation is explicitly capped at15 free vertices.
Subset search, actual native execution, finite-mantissa error, exponent
height, work funding, phase frames and physical resource peaks remain
separate obligations. A structural witness supplies none of their authority.
Different elimination orders also have different rounded traces; deploying
one requires a declared physical schedule and independently checked bridge.

## 4. Audit and model frontier

The exact audit exhausts1,098 anchored supports through n5 and16,054
unordered query states, including diagonals. Independent compilation of
87,422 orders supplies both minima for each of64,216 join/live-limit
decisions:128,432 objective comparisons. All agree with the subset
recurrence, including30,882 empty feasible classes. Every returned order
is also checked against its directly compiled cost. This covers original
unary factors, disconnected and empty-boundary components, and the actual
tape's power tags. Both out-of-class vertex limits refuse before subset
allocation.

Run `python -X utf8 -B experiments/joint_uncertainty/query_order_resource_frontier.py --check`
to recompute the [minimal exact report](../../evidence/minimal/FP_QUERY_ORDER_RESOURCE_FRONTIER.json).
The report retains aggregate counts, selected witnesses and their model
prefix coordinates, with no posterior tables or full operation traces.

The complete passive scan covers all1,544 pre-target cuts of the four n16
model tapes. It consumes the exposed labels to construct each hypothetical
native count prefix; it does not resume any halted CUDA worker. The table
counts query cuts, not actual numerical executions or statistical trials.

| Case | All four structural limits witnessed | No join/live-feasible order | Minimum C above65536 |
|---|---:|---:|---:|
|n16/c2/16|396|0|0|
|n16/c2/17|393|3|0|
|n16/c4/18|283|89|4|
|n16/c4/19|321|55|0|

There is no cut where C fits but its minimizing tape exceeds262144 nodes.
This makes the classification complete for these four structural limits
on these tapes. It does not certify the larger Runtime decision class.
For c4/18 at cursor276, query(2,5), the exact minimum is C=65574, with
N=246407, while the phase cap is65536. A minimum-width witness alone misses
this obstruction. The existing native response remains well defined.

Selected later cuts also certify an8192-cell minimum join: c2/17 at
cursor332/query(8,7), c4/18 at372/(15,1), and c4/19 at368/(4,13).
Search with a vacuous one-million-cell live cap still finds no4096-cell
order, and directly checked8192-cell witnesses fit32768 live cells. These
are lower bounds for this anchored query-retaining order class only. The
relaxed live cap is nonbinding: with15 free vertices, at most120 original
factors and15 component factors, W(S) is at most480+15*32768; adding a
4096-cell join and its2048-cell output is still below2^20. Thus a hidden
live-cell restriction does not supply that join lower bound.

## 5. Reordering and uniform-frame enlargement are insufficient

The actual model contract retains a uniform F-byte phase frame, including
padding, for initialization and three phases per successfully learned
event. A completed T-event stream therefore retains at least(1+3T)F bytes.
The [immutable-frame law](IMMUTABLE_CUDA_EVIDENCE_FRAMES.md) permits sharing
completed frames across snapshots; it does not erase these distinct frames.

The uncompressed typed encoding stores every binary tape node. Even the smallest
`('add',0,0)` or `('mul',0,0)` node takes65 bytes. All real nonnegative operand
addresses take at least that much. Ignoring every other field, separators,
power tags and operation words gives the valid phase-frame lower bound

`F >= 8 + 65 B`,

where B is its binary tape-node count and eight bytes store the used extent.
At a fixed single whole-program block, B=N-3-F_initial. Minimize N over the
entire join/live-feasible order class before using this bound. An arbitrary
large tape would supply no lower bound over alternative orders.

All four tapes have such a whole-block cut. The directly compiled minimizing
orders establish the following exact, conservative bounds:

| Case / cursor | Minimum binary nodes B | Required uniform F, at least | Largest F allowed by8 GiB divided by phase count |
|---|---:|---:|---:|
|n16/c2/16 /366|210428|13677828|7224503|
|n16/c2/17 /328|206976|13453448|7224503|
|n16/c4/18 /276|246012|15990788|7608445|
|n16/c4/19 /297|204412|13286788|7608445|

Retained frames alone would require at least16,262,937,492;
15,996,149,672;18,053,599,652; and15,000,783,652 bytes respectively. Each
exceeds8 GiB, before other state or temporary coexistence. Thus even optimal
reordering plus a larger **uniform** frame cannot complete these streams
under that packed cap and this encoding. The node-minimizing order differs
from the output-minimizing one in c4/19, illustrating why both objectives
must be checked.

This is not a lower bound on lossless encodings, nonuniform prepaid frames,
other positive decoders, the full posterior or all Compiler implementations.
The actionable frontier is a paid representation and solver improvement
with a complete bridge, or honest UNRESOLVED. Changing the native learner,
forgetting old counts or relaxing a declared numerical relation is not
justified by these results.

## 6. Allowing a different anchor

The separate [gauge/query-width law](GAUGE_AND_QUERY_WIDTH.md) now gives
`J_a=2^(tw((G+uv)-a)+1)` for the optimum largest join at anchor a. Across
anchors this optimum varies by at most a factor of two. All52,812 small
anchor decisions agree with independent bucket/graph enumeration.
On the selected model cuts, changing the anchor recovers the c2/17 join
refusal, but cannot reduce c4/18's65,574-output minimum under the table caps.
Two later cuts still need8,192 joined cells over every anchor and order.
These findings neither change the fixed-anchor decision classes above nor
fund their search. They prevent extrapolating a fixed-anchor refusal into
an all-anchor lower bound or assuming an endpoint anchor always improves it.
