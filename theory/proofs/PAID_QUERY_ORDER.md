# Paid structural query-order search

Status: **packed algorithm proved and exhaustively audited; reference
Runtime prototype and passive AMP integration pass scoped CPU checks;
prototype scratch-resize counterexample reproduced; actual CUDA HOLD**.
Foundation R4 and ERC-1 are unchanged. This prototype is not a release.

## 1. A bounded representation of the existing exact DP

The [order-resource theorem](QUERY_ORDER_RESOURCE_FRONTIER.md) proves that
the factor-scope multiset and future structural costs depend on the
eliminated set S, including original-factor multiplicities and one factor
for every eliminated component, even an empty-boundary component. Thus a
lexicographically minimal prefix cost and one predecessor suffice for the
stated structural decision class. No new state quotient of the native
learner follows, and [precision feasibility does not share this quotient](ORDER_PRECISION_SEPARATION.md).

`query_order.py` implements that DP in an actual supplied byte extent. Let
m=n-1<=15 and r=m-|Q|, where Q is the set of distinct non-anchor query
vertices. Compress subset addresses onto the r eliminable vertices. This
embedding is strictly order-preserving, so increasing packed masks remain
a topological order of the same subset DAG. The table has2^r rows, each
three little-endian unsigned32 words: accumulated output cost C, tape cost
N, and the predecessor bit plus one. A zero predecessor denotes an
unreachable nonempty subset; row0 is the initial prefix.

The exact table extent is therefore **12*2^r bytes**, at most393216 bytes.
Every row is initialized in place before use, with no second exponential
zero buffer or dictionary of subset records. Graph metadata uses only
O(E+m) bounded entries. The owner may reserve a larger reusable extent;
the implementation writes only the required prefix. This is a table-payload
law, not a whole-host-memory or snapshot-copy bound.

For E<=120 and j<=2^m, a conservative count bound for all partial and final
paths is

`N <= 3+4E+(m+1)(E+m+1)2^m < 2^27`,

`C <= 38+(m+1)(4+6m)2^m < 2^27`.

It follows from at most m elimination steps plus one terminal join, at
most E+m bucket factors, and the existing M/A/G count laws. Packed32-bit
costs cannot overflow in this class; the implementation also guards every
stored cost so a future expansion cannot silently wrap. Reconstruction
follows only reachable predecessors and yields a complete permutation.

The structural result is exactly lex(C,N), or lex(N,C), over all retained-
query orders meeting the supplied join/live caps. `None` means that this
particular class is empty. An insufficient buffer, invalid input or a block
outside the15-free-vertex class raises; it cannot become a false empty-class
answer. The output and tape caps, exponent guards, numerical bridge and
full-resource execution remain separate checks.

## 2. The declared work tariff

The fixed kernel's conservative tariff is

`W = 128(2^r+1)(m+1)(E+m+1)`.

Its model counts bounded integer/bit operations, comparisons, scalar/cell
visits and fixed-width row loads/stores. Setup and reconstruction fit the
extra row allowance. At each subset, mask expansion and component discovery
visit at most m vertices; filtering and summing scopes visit at most E+m
factors; each of at most m next vertices visits at most E+m factors. Row
initialization, cost arithmetic and pack/unpack have constant bounded work.
For example the loose per-row envelope
64(m+1)+16(E+m)+m[16(E+m)+96] fits128(m+1)(E+m+1), including initialization.
Every mask is covered, whether reachable or not.

This is a prepaid algorithmic primitive tariff, not a CPU instruction,
bit-time or elapsed-time bound. It applies to the registered implementation,
not arbitrary replacement Python code. The Windows whole-process job limit
remains necessary for actual physical runs. No physical-work lower bound or
total-process resource advantage is inferred from W.

## 3. Runtime wiring and exact decision boundary

The explicit `ConstructionContract.indexed_order_search` flag selects this
solver for the existing complete indexed native family. The corresponding
AMP contract's `order_search` flag must agree. False retains the fixed
natural schedule. True minimizes the structural pair separately in each
reference/projected block, reserving eight convolution cells when needed;
the global AMP lowering searches its whole anchored free graph. A global
n>16 search is unresolved; projected n256 can still use small local blocks.
All global count coordinates remain retained in either case.

Runtime reserves one actual reusable DP payload before construction and
CUDA binding, of12*2^min(n-1,15) bytes. Each search debit uses its actual local
n/E/query and occurs before the first DP entry. Reference and physical
searches are paid separately in their fixed event roles. The table bytes
are the algorithm's real working storage, not an unused accounting dummy.
Failure retains the received context/target, paid work, workspace and all
previous native state. The current unpinned extent defect is given below.

Only an immutable order proposal reaches the complete builder. Its
permutation, joins/live cells, arithmetic, integer/exponent envelope,
compiled tape and output extent are independently reconstructed. Claimed
costs on the solver result are not resource authority. The accepted plan
records all orders; the AMP checker rebuilds the complete tape for those
orders against private actual inputs. It does not need another search or
an optimality claim to establish native arithmetic refinement. Wrong order
metadata attached to an old tape is rejected.

The fixed natural class rejects a complete alternate-order plan. The
expanded class accepts a valid one only subject to the same full RNE,
endpoint/native bridge, arena, retention, lineage and fresh/install gates.
The reference model ID is v3; the expanded global/projected physical
forward IDs and added search work identity distinguish the new realization.
Numeric kernel and observation/commit semantics are unchanged.

No `CERTIFIED_COMPLETE` token is minted by this search. In particular,
numerical failure of its selected order stays UNRESOLVED for the larger
order-existence question. A minimum C above its output cap can establish a
scoped structural obstruction mathematically, but this Runtime prototype
does not expose that as an optimization-class or installation certificate.

## 4. CPU evidence and an actual native recovery

`FP_QUERY_ORDER_STORAGE.json` compares the packed kernel with complete
independent tape enumeration:1098 supports,16054 queries,87422 orders,
64216 cap decisions and128432 lexicographic comparisons, including30882
empty join/live classes. Both objectives agree. Dirty buffer reuse and
outside-prefix canaries pass. Nine malformed/extent cases refuse before
any scratch write. Maximum-class empty, chain and dense cases agree with
the older passive DP, including all32768 rows and245760 transitions.

`FP_PAID_QUERY_ORDER_CPU.json` passes all388 owned small histories/776 native
phase comparisons, profiles, n256, ordinary closure and same-path fresh
reference persistence against its full literal control. The literal
non-indexed control has its indexed-only search flag disabled. Actual work
refusal occurs before the solver is entered, with old state, context and
scratch retained. Valid proposals with bogus zero costs cannot suppress
independent numerical funding. Mutating an old returned order record on a
later solver call cannot change accepted native history.

On K(2,14), anchor0, both fixed and searched runs learn the same28 actual
events. The next query(2,3) makes fixed-order Runtime refuse at the unchanged
join cap. Paid search returns
33405247401130534720401/37929227217792351257122, equal to an independent exact
sum over32768 worlds. All120 counts remain; the next target is unrevealed.
Search work actually paid is1866985728 units. The two retained packed sizes
are1032587 and1432542 bytes; their final states differ because only one
query completed, so this is not an isolated memory-performance comparison.

`FP_PAID_ORDER_AMP_CPU.json` checks11919 complete projected tapes against
exact native world sums. Global and projected selected schedules each pass
280 exact RNE predictions and560 complete-coordinate observations under the
unchanged1/100 state and1/1000 probability tolerances. Selected orders differ
from natural in112 and24 cases, respectively. All16 order/tape substitutions
refuse, while a fully rebuilt alternative passes only the expanded class.
Separate fixed-schedule regressions remain retained. No device run is
inferred from these passive arithmetic checks.

## 5. The prototype's remaining counterexample: mutable extent authority

`audit_order_workspace_frame.py --expect unbounded` reproduces a real CPU
Runtime mismatch in this prototype. The solver receives Runtime's actual
`bytearray`, extends it by one byte, and returns the honest order. During
the next solver call, it resizes the retained old backing handle again.
Both native predictions and the intervening native update are correct;
the old snapshot remains immutable. Nevertheless the ledger still bills
48 bytes for a50-byte payload. `FP_ORDER_WORKSPACE_RESIZE_CPU.json` retains
this exact two-byte accounting discrepancy.

Thus prepaying the initial extent is insufficient if the supplied scratch
also grants later resize authority. Rejecting a result after the resize
would not restore the already violated residency/peak claim. This is an
implementation mismatch with resource ownership, not an FP Foundation
counterexample. Correct numerical output does not repair it. Actual CUDA
use of the new solver remains HOLD until its extent boundary is repaired.

The intended repair keeps an owner-private, lifetime-long buffer export
and supplies a separate writable view. The solver may write scratch, but
cannot release the owner's export or resize the backing bytearray, even
through a retained handle after its own view ends. Snapshots must copy the
scratch into immutable bytes. The Python3.12 documentation specifies the
resize restriction while views are held and explains that releasing a view
removes its restriction; therefore an owner-held export must survive the
helper's view. [Python memoryview documentation](https://docs.python.org/3.12/library/stdtypes.html#memoryview.release).

The claim will be scoped to the supplied-view/backing-handle operations,
excluding arbitrary process-memory access and owner introspection. It will
not be a Python sandbox or a total-host-heap theorem. No semantic resize
action, new native state or weakened numerical limit is justified.
