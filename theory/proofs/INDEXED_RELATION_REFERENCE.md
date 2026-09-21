# Indexed literal code and complete reference coordinates

Status: **PROVED, SCOPED; EXACT NATIVE AND GUARDED INDEX AUDITS**.

The literal world-slot relation Program, its uniform initializer and its
selected-slot learner have a compact indexed description. The existing
[count state](COUNT_LEARNER_ENCODING.md), together with an actual ordered
categorical query, then determines every native reference learner and cache
coordinate. Neither statement requires allocating the full world table.
This removes a representational necessity for exponential admission tables;
it does not implement owned admission or make inference uniformly cheap.

This is a representation of the **same ordered finite native code**, including
all repeated incidences and slot ties. It adds no FP semantic constructor.
Foundation R4 and ERC-1 remain unchanged. No `CERTIFIED_COMPLETE`, physical
resource equivalence, AMP bridge or installation authority is issued.

## 1. Exact decision class and indexed code theorem

Fix n>=2, K=2^(n-1), and the literal builder `simplex_gradient.relation_graph`.
The primitive sources, in order, are `x0:0,...,x0:n-1,x1:0,...,x1:n-1`, each
of type mass, availability delay0 and upper1. SUM has type mass; PRODUCT
has signature(mass,mass,mass); the readout has bases(1,1). There are no
delayed states or bindings. Let A=2n+n^2.

The native world order is lexicographic on the n-1 unanchored bits. For
0<=k<K define z_0(k)=0 and

`z_i(k) = (k >> (n-1-i)) & 1`, for 1<=i<n.

The code is exactly the following indexed family:

| Node indices | Exact native node or ordered term rule |
|---|---|
|0,...,2n-1|SOURCE `x{floor(a/n)}:{a mod n}`|
|2n+i*n+j|PRODUCT(mass, i, n+j)|
|A+2k+y|SUM(mass, `(Term(2n+i*n+j,0))` over lexicographic(i,j) with z_i XOR z_j=y)|
|A+2K+y|SUM with8K terms; term t is `Term(A+2*floor(t/8)+y, floor(t/8)+1)`|

Here y is0 or1, and the last two nodes are the heads in that order. In
particular, eight equal terms remain eight actual ordered incidences. A
numeric coefficient8, reordered terms, or a different slot tie would be a
different code description, even if some exact current outputs coincided.

**Proof of code equality and typing.** The original builder emits exactly
these four consecutive blocks. Its nested pair iteration is lexicographic,
and its world iteration has the stated big-endian bit order. Each pair
parent is in the preceding source block; every indicator parent is in the
pair block; every head parent is in the indicator block. Every SUM term has
slot0 or k+1<=K, and every parent/result has type mass. Both heads exist and
match the two positive bases. Empty indicator SUMs, including the parity1
indicator of the all-zero world, are preserved. This proves literal code
equality and native well-typing for every finite n.

If k has c1 set bits, put c0=n-c1. Its indicator arities are
c0^2+c1^2 and2*c0*c1. To select a term of a particular rank, build the two
sorted vertex groups, scan row i with block size c_(z_i XOR y), and select
the residual-ranked vertex in that group. This gives the exact pair order
in O(n) index operations without enumerating n^2 pairs. Head term selection
uses integer division by8. The complete code counts are

`nodes = 2n+n^2+2K+2`, `slots = K+1`,

`SUMs = 2K+2`, `PRODUCTs = n^2`,

`SUM incidences = K*(n^2+16)`, `all edges = K*(n^2+16)+2n^2`.

The descriptor consists of a fixed schema identifier and n. Its explicit
description uses O(log n) bits, with the fixed decoder counted separately.
Derived world/node/slot indices need O(n) bits; an index operation is not
assumed to have constant bit cost. Explicit source declarations use
O(n log n) bits. This is not a lower bound on alternative descriptions.

## 2. Bind the initializer, learner and information interface

The description also fixes Gamma_0=1, Gamma_(k+1)=1/K, selected slots1..K,
learning rate1, update unit1, no commit grid and the existing
`mean-ce-normalized-simplex-gradient-v1` optimizer with its registered
event-local gradient. A selected slot has the point decoder k -> k+1;
the interval itself need not be expanded into a tuple. The unit-total
initialization identity K*(1/K)=1 follows for the schema's own Gamma.
It does not verify an arbitrary externally supplied vector by sampling it.

The finite source domain has n^2 ordered rows. Row i*n+j contains one token
at x0:i and one at x1:j, with every other source explicitly zero. A state
view binds all source declarations, types, availability delays, ranges,
bases and delayed-state declarations, then checks all2n supplied source
values and their complete key set. Soft inputs, omitted keys, extra keys
and implicit float conversion are refused. Query(i,j) is not identified
with(j,i): their head forecasts agree but their source and PRODUCT caches
generally differ.

The code indexing theorem still describes the same Program on other legal
source values. Only this particular **count/reference decoder** requires
the categorical domain. Other priors, rates, units, source domains or
delayed states are possible FP settings; refusal here does not prove them
illegal or impossible. They require their own encoding proof or a funded
fallback to the complete native state.

The descriptor `(literal-anchored-relation-index-v1,n)` is not the native
`Program.program_id`, which hashes the entire serialized code. The audit
compares complete small Programs, Gamma, U and rules structurally. It does
not replace a native code hash with a descriptor hash or assert that an
unread arbitrary graph matches the family.

## 3. Every reference coordinate has a decoder

Retain C=(n,d,alpha,c,s), with the full D=n(n-1)/2 signed nonloop count
vector, the actual pending event or empty tag, cursor and optimizer-step
clock. As in the count theorem, d counts this candidate's executed commits,
including profile repetitions. Source observation identities, provenance,
resource history and Compiler control state remain outside C and are not
discarded. Merely constructing a mathematical C does not establish that
a live Runtime candidate reached it.

Let L=SUM_e |d_e|, and for native world k set

`E(k) = SUM_e |d_e| * 1[z_i(k) XOR z_j(k) = 1[d_e<0]]`,

`W(k)=9^E(k)`, `Z_y(i,j)=SUM_k W(k)*1[z_i(k) XOR z_j(k)=y]`,

`Z=Z_0+Z_1`.

The [positive frontier theorem](POSITIVE_FRONTIER_DECODER.md) proves that
these integer weights normalize to the original count posterior. Thus
theta_0=1 and theta_(k+1)=W(k)/Z in the **native slot order**. The complete
learner has empty delayed state, cursor c and optimizer_steps s. At a
committed boundary all gradient entries and unit_count are zero.

For alpha=(u,v,y), use its own partition, not the current query's partition,
and put M=1+8*Z_y(u,v)/Z. The accumulator coordinates are

`G_0=1/M-1/5`, `G_(k+1)=4/5-8*1[z_u(k) XOR z_v(k)=y]/M`,

with unit_count1. In particular the fixed feature slot's gradient remains
present. An observed diagonal label0 has G=-4/45 in every slot even though
d and theta are unchanged. This forbids binding a view merely to the
parameter values or signed counts.

For actual ordered query(i,j), the source values are its complete two
one-hot rows; the pair node for(a,b) is1[(a,b)=(i,j)]; indicator A+2k+y is
the world's parity indicator. Head excesses are8*Z_y/Z, masses are1 plus
excess, normalizer10, probabilities mass/10, and delayed outputs are empty.
These recover every `Evaluation` field. No cache or derivative coordinate
is omitted because it is currently inactive or fixed by the learner.

The existing count proof supplies the transition induction: initialize at
Gamma; observe retains the actual query/label and increments c; commit
changes the nonloop count by1-2y, clears alpha and increments s; actual
profile attachment changes only the cursor at an empty-accumulator boundary.
Each decoded state equals the literal reference state. The indexed code
theorem additionally supplies every node, incidence and selected slot that
the previous state decoder assumed was already materialized.

This is a total mathematical decoding statement for finite states in the
declared family. It is not a whole-Compiler bisimulation. Actions that read
all slots, change U, leave the categorical domain, require a different
physical layout or inspect lineage still have their respective full costs
and proof obligations. Unsupported or unfunded execution remains UNRESOLVED.

## 4. Preflight inference and explicit output separately

A compact code coordinate is cheap to locate; a state coordinate requiring
Z can still require expensive inference. With a declared elimination order
of anchored width w, retaining at most two query endpoints gives at most
2^(w+3) cells per join and O((m+n)2^(w+3)) positive table arithmetic, where
m is the number of nonzero counts. The existing bit bound is n+4L for
partition integers. An additional eight bits conservatively cover this
decoder's fixed rational readout/gradient multipliers. Input scans, integer
powers, metadata, bit arithmetic and output are additional costs. There is
no uniform polynomial-time or physical-memory claim.

The prototype uses n<=1024 and an explicit order, natural order by default.
It performs no hidden order search. A metadata-only simulation follows the
same bucket schedule before constructing powers or numerical tables. For
each bucket it computes the join size, output size, coexistence count and
number of scalar joins/sums; it also counts the final parity sums. The
partition's declared join-cell, live-cell, arithmetic and integer allowances
must all pass. Defaults are4096 join cells,32768 live cells,2000000 table
operations and32768 integer bits. The work class is this particular schedule,
not every possible exact decoder or elimination order.

The size simulation is exact for the existing decoder's reported **logical
integer-cell and scalar-operation metrics**: its scope evolution is
independent of table values, and each enumerated assignment has the counted
operations. Python objects, factor-power work, retained query partitions,
metadata and output coexistence are not folded into those metrics. At most
the bound and pending-event partitions are cached per immutable state view.
A real owned implementation must charge them and the surrounding process.

Explicit reads have separate preflights: a full Program needs the node and
term counts above; a full selected-slot learner needs K+1 slots; a complete
reference state emits2(K+1)+3 scalar coordinates; a complete cache emits
2n+n^2+2K+9 scalars. Empty delayed/binding metadata is preserved. These
lower-bound the respective output work/storage: in particular an explicit
whole native vector retains its Omega(K) cost, and full literal code has
Theta(K*n^2+n^2) incidences. Indexing does not make those reads free.

## 5. Exact adversarial evidence and remaining admission obstruction

Run:

```text
python -X utf8 -B experiments/joint_uncertainty/indexed_relation_reference.py
```

The minimal [result](../../evidence/minimal/FP_INDEXED_RELATION_REFERENCE.json)
retains counts and a few closed-form witnesses, not full graphs or caches:

- n2 through n8:795 nodes,17116 ordered SUM terms and261 slots match the
  independent literal builder, with complete G/Gamma/U/rule comparison.
- All585 native histories through depth3 at n2 and343 through depth2 at n3:
  928 boundary states,5427 complete native caches and926 observed/926
  committed full states agree. Pending gradients are deliberately read
  through views bound to another query.
- Three one-/two-/three-pass profiles supply39 additional complete-state
  comparisons, including the ordinary cursor attachment.
- All64 active n4 graphs, all6 free-variable orders and all16 ordered
  queries:6144 exact table plans and partitions agree with the executor and
  independent full-world enumeration.
- Fourteen G/Gamma/U/interface mutations, five malformed source rows and
  four stale clock/pending/orientation bindings are refused. Five inference
  preflight failures are checked with the numerical decoder replaced by a
  sentinel that would fail if entered. Twelve invalid index/order/prototype
  cases are also refused.
- At n256 the logical code has2^256+66050 nodes and65552*2^255 SUM terms.
  The audit disables the literal builder, performs three actual count-state
  commits and a profile cursor attachment, checks37 code incidence witnesses,
  and compares selected parameter/gradient/cache coordinates to independent
  closed formulas. After one anchor observation Z=5K, weights are9/(5K) or
  1/(5K), and the anchor forecast is41/50. Its positive partition uses258-bit
  integers, two-cell joins,510 multiplications and257 additions. A later
  relative observation has Z=25K. A diagonal retains its nonzero pending
  gradient. Five explicit full-read requests refuse before materialization.

The large case is exact symbolic/reference execution of three events, not
an executed exponential native graph, GPU run or measured physical saving.
The audit imports no Torch and does not rerun any terminal model experiment.

The current production `prepare_model` still requires an exact `Program`,
explicit prior/selected-slot tuples, and dense expert increment and
reconstruction tables. The Runtime also admits literal Program objects.
Those are real integration constraints, not a theorem that semantic state
requires exponential storage. The new representation is deliberately not
passed to that API as a pretend Program. Owned indexed admission, resource
and identity binding, actual event acquisition, complete numerical phase
evidence, fresh persistence and reachable installation remain the next
implementation/bridge obligations.
