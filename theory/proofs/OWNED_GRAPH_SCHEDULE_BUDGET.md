# The full native graph schedule still needs an explicit host budget

Status (2026-10-03): **SOURCE-DERIVED COUNTS AND SELECTED STORAGE LOWER; EXACT CPU PASS**.
Source: the CPU/device-qualified owned graph at `b2c5ef8`. No production,
model, encoding, Foundation/ERC or old experiment input changes here. This is
the full ordinary-text budget assessment following the closed qualification,
not another representation candidate or a new corpus attempt.

Subsequent [complete disjoint host accounting](OWNED_GRAPH_HOST_BOUND.md)
includes metadata, source values and the original corpus's exact context
counts. Its 101.1334217-GiB lower excludes the unchanged 96-GiB realization.
The schedule-only conclusion below is preserved as the earlier, insufficient
selected lower; it is not the current whole-host decision.

## 1. Scope and exact object/history counts

Consider T successfully completed ordinary native events of the single token
incumbent, with update unit B. Let C=floor(T/B), r=T mod B and Q be the number
of completed commits whose master bytes change, 0<=Q<=C. Use the actual owned
typed graph, complete source/target records and original private ingress names.
There is no profile, search, CUDA/binary64 shadow or reporting in this interval.
Optional base facts are fixed at initialization; native graph retention creates
no canonical images. Initialization, reporting, failures and diagnostics add
cost beyond this interval. The formulas do not promise that T is reachable.

Relative to the initialized owner, the **exact increments** are:

| Retained coordinate | Increment |
| --- | ---: |
| Complete graph pages M | 5T+C+Q |
| Live physical objects | 12T+2C+Q |
| Retired physical identities | 6T+C+2Q |
| Resource events | 50T+9C+10Q+2 1[T>0] |

The [complete record schedule](NATIVE_RETENTION_VOLUME.md) already gives M.
Each graph retention has three allocation events (scratch, immutable page,
root), two acquisitions, two scratch releases and one prepaid work event:
eight events, two surviving objects and one retired scratch identity. Ingress
body/control and the reserved target add three objects/allocation events per
target. Releasing the old current learner adds T retirements/events; replacing
old range evidence adds Q. Thus live objects are 2M+3T-T-Q and retired identities
are M+T+Q. These releases do not remove the graph's immutable pages.

Beyond those allocations/releases, each ordinary event has six work charges:
ingress prepayment, causal-source reading, prediction information, prediction
execution, observation and range-dependency checking. Each commit adds one
optimizer charge; each changed range adds one range-audit charge. The first
ordinary program retention adds one work and one acquisition event. Hence
resource events are 8M+3T+T+Q+6T+C+Q+2 1[T>0]. These counts follow actual
writers, not a regression of measured short-prefix sizes.

## 2. A data-independent node lower

For the original `train/i` identity schedule, the following disjoint typed
definitions are forced even if all targets and all numerical outputs repeat:

| New definition family | Count |
| --- | ---: |
| Private ingress/body/control/record name strings | 4T |
| IngressIdentity, TokenContext, pre-target ObservationRecord | 3T |
| TokenEvaluation | T |
| After-observation and committed EventTrace | T+C |
| Nonempty observed and empty committed TokenState | T+C |
| Nonempty pending-window tuple | T |
| Complete pre-target prediction tuple | T |
| Prediction TokenWindow, excluding the shared initial window | T-1 |

Therefore, for T>0, the number of **new** nodes satisfies

    N_new >= 13T + 2C - 1.

Record types distinguish the families; positions/observation IDs distinguish
events within them. Empty committed states differ from nonempty observed
states and have distinct origin clocks. Each nonempty pending-window tuple
has a distinct final window position. A pre-target tuple begins with a candidate
string, so it cannot be one of those all-window tuples. The private ingress
name family is distinct from the original declared train/report IDs. The first
prediction window may coincide with the initial origin's PAD window, which
is why it contributes no new-node credit. No numerical diversity is assumed.

For T=1,048,576 and B=512 this lower is **13,635,583 new nodes**. The focused
original-manifest control has 1,118,517 initial nodes, giving at least
**14,754,100 total nodes** for that same declared graph path. Consequently the
qualification's 2^22 node cap cannot be a successful full-run cap. This does
not falsify the completed qualification, which never declared that horizon.
Increasing a node cap alone supplies no corresponding host or time budget.

## 3. Flat pending vectors have a retained expansion cost

There is exactly one distinct nonempty `after_observe.windows` tuple per event.
Its length runs from one through B in every whole unit and one through r in
the unfinished unit. Let

    W = C B(B+1)/2 + r(r+1)/2.

The graph stores those **W child references**, despite reusing the individual
window definitions. Their exact contribution to immutable page payload is
9T+8W: eight length bytes, one tag and eight bytes per child. This differs from
the old canonical tree's repeated-window expansion; there is no claim that
the earlier 68.84-TB byte-stream lower still applies to graph retention.

The installed Windows x64 CPython 3.12.9 realization keeps further disjoint
allocations. Its ABI is checked directly by the audit; the allocation/host
interpretation is the same stated standard-allocator premise as the
[earlier liveness proof](NATIVE_PREDICTION_LIVENESS.md#2-exact-selected-object-lower-bound).

| Selected live storage | Lower bytes |
| --- | ---: |
| These definitions inside complete immutable pages | 9T+8W |
| Producer and reader raw node `bytes`, separately allocated | 68T+16W |
| Reader's parsed child-ID tuples | 40T+8W |
| Independently parsed non-small integer IDs | 28W |
| Original live `windows` and `targets` tuples in observed states | 80T+16W |
| **Disjoint selected total** | **197T+76W** |

`struct.iter_unpack` creates fresh non-small integer IDs at every stored child
occurrence on this ABI. The audit checks their actual distinct identities,
including repeated equal IDs. In the full declaration, even the initial window
node follows the million-ID manifest and lies beyond the small-integer cache;
later window nodes do too. Larger integer IDs can only increase their sizes.
Source targets are not counted as fresh integers: their referents may share.
The original observed states remain reachable through actual retained traces,
including the full pending unit after a commit. No observer reference is needed
to keep them live. Actual page extents are counted as disjoint byte ranges,
not temporary decoded/sliced copies or extra standalone allocations.

At the original full horizon, W=268,959,744. Those vectors occupy only
**2,161,115,136 encoded bytes**, but the selected disjoint live storage is at
least **20,647,510,016 bytes = 19.2294921875 GiB**. Dictionary buckets, lists,
parsed record wrappers, metrics, other definitions, allocator slack and all
resource metadata are excluded. This is **below** 96 GiB: it proves neither
whole-host fit nor whole-host exclusion. In particular one must not add an
occurrence estimate that double-counts any of these same allocations.

## 4. Complete-schedule decision and exact evidence

The same full schedule adds 5,244,928..5,246,976 pages,
12,587,008..12,589,056 live physical objects, 6,293,504..6,297,600 retired
identities and **52,447,234..52,467,714 resource events**, as Q ranges from zero
to 2,048. These are counts of retained structures, not committed-byte estimates.
All their concrete Python indices, lease records and event data still require
a budget, alongside master bytes, source contexts, arithmetic-node values,
unselected graph nodes and permitted final diagnostics.

`audit_owned_graph_schedule.py` checks all 93 binary histories through length
four at units one/two/four plus eight sixteen-target histories at units
one/two/four/eight. All 101 complete histories/422 targets/218 commits satisfy
the exact schedule formulas. Actual typed root sets verify 5,824 forced new
definitions. The 766 pending references occupy 141,350 selected disjoint
bytes, exactly matching the ABI formula in these cases. A sharing control
checks that repeated occurrences of one tuple/integer are counted only once.
The passive root lookup changes no Runtime meter, memo, lease or value.
Evidence: `FP_OWNED_GRAPH_SCHEDULE_CPU.json`.

**Decision:** scoped CPU/actual AMP correctness is closed, while the full
ordinary-text host/execution budget remains **UNRESOLVED**. Do not transfer the
small qualification cap or launch based only on encoded page size. Equally,
do not label the full 96-GiB budget impossible from this selected lower. The
next whole-budget calculation must include the complete metadata/index terms
above; no new representation is selected here. Foundation/ERC, relation/
precision, static cases and terminal journals stay closed. The full trained
next-token comparison remains the objective, without a shortened replacement.
