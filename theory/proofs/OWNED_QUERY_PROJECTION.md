# Owned exact query projection with the complete native state

Status: **IMPLEMENTED REFERENCE REFINEMENT; EXACT AND OWNED CPU AUDITS PASS**.
The independently declared AMP schedule remains global. Its actual A5
integration audit passes all thirteen cases atae7f915; no projected physical
kernel or complete release is claimed here.

A subsequent [projected physical schedule](PROJECTED_INDEXED_AMP.md) now
shares this geometry with its own exponent guards and arithmetic identity.
Its exact CPU audit passes; actual A8 is pending. The present proof remains
the exact-reference result and does not transfer its evidence to that device
schedule.

The [boundary response theorem](QUERY_BOUNDARY_RESPONSE.md) now supplies the
prediction executor inside `ReferenceCompilerRuntime`. It changes the
arithmetic for a current query, while preserving G, Gamma, U, every source,
the complete count state, native parameter interpretation and future input
interface. Foundation R4 and ERC-1 are unchanged. There is no new semantic
architecture action, supplied execution plan or `CERTIFIED_COMPLETE` claim.

## 1. Fixed schedule and semantic refinement

The new arithmetic declaration is
`indexed-literal-count-positive-query-block-reference-v1`.
For an actual ordered query(i,j), planning scans all D=n(n-1)/2 signed
counts. An iterative block decomposition and its block/vertex incidence
forest select the unique query path. A diagonal has response(1,0);
disconnected endpoints have response(1,1). Both cases still read the full
count support, and neither deletes a state coordinate.

For each block on the path, keep its global vertices in increasing order,
anchor the first, and map the actual entry/exit vertices to local indices.
The existing positive partition evaluator runs in the corresponding natural
order, producing its two parity responses(a,b). Keeping this order means
that a whole-program block has precisely the former partition schedule.
This avoids replacing a working full-block order with an arbitrary query
anchor. Successive responses combine by positive convolution:

`(A,B) <- (A*a+B*b, A*b+B*a)`.

The first response is used directly, since it is the convolution identity's
result. The block theorem proves that(A,B) is proportional to the full
native query partitions(Z_0,Z_1), including branches containing the original
global anchor. The proof first lifts the global flip gauge; parity readouts
are invariant under that lift. Therefore the excesses8A/(A+B),8B/(A+B),
masses1+excess, normalizer10 and both noisy forecasts are exactly native.

Every prediction still stores the original complete CountState and ordered
query. All source, indicator and pair-cache coordinates decode using the
original global indices. The exact three pending gradient forms depend
only on the native target mass and actual event; the existing count update
therefore remains the complete native unit-simplex step. Induction gives
the same native parameters, caches, gradients and clocks at every completed
ordinary or profile phase. Later queries replan from every current count.

**Global theta is not normalized by(A+B).** `ReferenceView.partition` and
the full native parameter reader retain their original global normalizer
and explicit-output guards. A current forecast may be admitted while that
reader remains unfunded under its declared allowance. This is exact semantic
refinement with guarded point readers, not equivalence to a literal array
execution under identical physical resources.

## 2. Plans cannot determine their own input or funding

The Runtime obtains the query independently from its owned source row and
checks the plan's complete predecessor, ordered query and integer limit.
Before charging numerical execution, the machine reconstructs the metadata
plan from those complete inputs and compares every block, local query and
table count. Omitting a block, substituting its vertices or altering a
local query cannot pass by retaining the old aggregate resource numbers.
After execution the Runtime checks the result's full predecessor and
ordered query again before publishing a prediction.

This boundary trusts the fixed exact arithmetic implementation and the
checked graph/partition algorithms. It does not claim to sandbox arbitrary
Python changes to the exact evaluator. The independent native comparisons
audit their arithmetic refinement. The existing physical AMP endpoint and
operation checker has its separate trust boundary.

No public construction, prediction or installation action accepts one of
these passive plans. Actual source ingress, targets, role ownership, history,
profiles, lineage, fresh persistence and failed local states remain in the
same Runtime root. A failure retains received information and spent work;
it neither publishes an incorrect successor nor refunds an executed past.

## 3. Arithmetic guards and paid work

Let k be the number of selected blocks and c=max(0,k-1). For block b let
P_b,S_b be its existing exact table multiplication/addition counts. The
projected numerical plan charges

`P = SUM_b P_b + 4c`,
`S = SUM_b S_b + 2c + 1[c>0]`.

The final extra addition measures the combined partition's integer width.
A sole block returns its existing result and statistics directly. Empty
paths require two constant response cells and no table operations.
The peak table-cell envelope is the largest block's existing peak, plus
eight scalar cells when more than one block is combined. Those cells
conservatively cover the retained response and convolution intermediates.
It is a logical integer-cell envelope, not total interpreter scratch RAM.

The default4096 join cells,32768 live integer cells and2,000,000 arithmetic
operations remain fixed. Every individual block and the combined peak/work
must fit before any numerical table or power is formed. Let V be the number
of vertices on the selected block path and H the sum of its absolute
counts. The additional preflight is `V+4H+8 <= reference_integer_bits`, with
the existing32768 ceiling. For an empty path V=H=0. The positive product of
block normalizers bounds every combined integer by V+4H bits; the extra
eight bits also cover the fixed rational readout and gradient expressions.
Large irrelevant counts are still stored, but their powers are not formed.

The Runtime keeps its conservative metadata debit

`64*(n+1)^2*(D+n+1) + 128*(D+n+1)`

before support scanning, decomposition, local geometry planning and its
independent reconstruction. The total local graph sizes obey
SUM_b(|V_b|-1)<=n-1 and SUM_b|E_b|<=D. The two planning passes, bounded
scope/index visits and complete-input comparisons fit this existing coarse
tariff; it is not reduced because a particular path happens to be small.
After validation, numerical execution is prepaid separately at

`32*(n+1)*(P+S) + 64*(D+8) + 64`.

These remain declared logical work tariffs, excluding arbitrary-precision
bit/GCD complexity and interpreter heap. Packed retained buffers still use
the existing actual ownership and coexistence leases. No total-memory,
wall-time, whole-Compiler resource improvement or query-independent cheap
decoder is inferred. A hard selected block may still return `UNRESOLVED`.

## 4. Exact and actual owned results

The [new audit](../../evidence/minimal/FP_OWNED_QUERY_PROJECTION.json) checks
all1098 active supports on n2..5 against an independent exhaustive simple
path oracle:10,650 selected-edge comparisons. Every ternary count state on
n2..4 gives759 states and11,919 complete native cache comparisons against
the literal graph and full-world weight oracle.

Two actual n4 histories begin with opposite labels on(1,2). Their current
query(0,3) responses agree at1/2, while native theta_1 is9/40 versus1/40.
After the common actual suffix(0,1,0),(2,3,0), the owned pre-target query(0,3)
returns881/1250 versus369/1250. Both trajectories match every native cache,
observed state and committed state. The previously irrelevant count becomes
relevant again through ordinary learning; no recovery API or new action is
needed.

Another owned n4 trajectory performs four observations on(2,3) under a
24-bit reference allowance. The global parameter reader's conservative
preflight refuses, while actual query(0,1) predicts1/2 without invoking a
partition kernel. The full count vector(0,0,0,0,0,4) and history remain.

Nine owned binding adversaries alter the plan's query, predecessor, limit,
shape, block membership, vertex map or local query, or alter the returned
query/predecessor. All halt before publishing a prediction and retain the
actual context, prior learners and debits. A dense hard block and three
separate combined memory/work/height failures refuse before numerical calls.

The complete [indexed Runtime audit](../../evidence/minimal/FP_INDEXED_RUNTIME.json)
also passes:388 short histories/776 native phase comparisons, ordinary and
profile paths, n256 with literal builders disabled, fresh reference crossing
at20, retained alpha1/4, failure ownership and finite empty-policy closure.
Its former13-observation star refusal is now recovered: query(2,3) uses
two active edges and predicts189/250. The old full-graph16384-cell preflight
still fails and is checked independently. All13 counts are retained.
The n256 current packed root is62,469,341 bytes, without a total-RAM claim.

The unchanged exact AMP schedule audit passes270 predictions,540
observations and all endpoint/operation adversaries. This is a CPU audit.
[Actual A5](../../evidence/minimal/FP_OWNED_INDEXED_AMP_CUDA_A5.json) atae7f915
then passes all thirteen source-bound RTX3090 workers under4 GiB and900
seconds each. The successful prefixes contain222 independently checked
phases and51,146 floating words, including17,712 half words. Maximum job
peak is2,384,936,960 bytes. n256 still checks42,594 floating words with
literal builders disabled. Fresh paired evidence crosses at20; resident
installation and learning to21 pass with alpha1/2 retained and without a
historical selection proof.

The new star control checks40 successful phases/5213 floating words,
including1716 half words, before the leaf query. That query's exact
reference forecast189/250 is retained in the failed physical phase, while
global AMP preflight returns UNRESOLVED before producing floating outputs.
All13 counts remain, the target is unrevealed, and no prediction or learner
advance is published. This is an executed distinction between the two
schedules, not a projected physical decoder or a transferred A4 certificate.
The earlier A1-A4 results and failures remain retained.

The [selected complete native CPU regressions](../../evidence/minimal/FP_QUERY_PROJECTION_REGRESSIONS.json)
also pass atae7f915: context ingress, profiles and finite-run closure,
using the strict full-section/counter validator. No full release is inferred
from these selected regressions. All A5 and CPU jobs are terminal.

Run `python -X utf8 -B scripts/audit_query_projection.py --write` and
`python -X utf8 -B scripts/audit_indexed_runtime.py --write`.
The evidence retains aggregate exact checks and small causal witnesses,
without full caches, weights or datasets. Indexed native-class search and
a separately declared projected AMP schedule remain open.
