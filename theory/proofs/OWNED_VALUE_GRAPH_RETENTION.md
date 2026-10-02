# Complete native records as a typed value graph

Status (2026-10-03): **CONDITIONAL PRESERVATION AND COST LAWS; EXACT PASSIVE CPU AUDIT PASSES**.
Runtime source observed: `680d9c5`. Production is unchanged. This is a
research model of the ordinary-text retention problem, not an installed
archive, resource certificate, AMP bridge or trained model result.
Foundation/ERC and the relation/precision branch remain closed.

## 1. The representation question

The [whole-schedule law](NATIVE_RETENTION_VOLUME.md) gives at least 68.84 TB
in each of three complete canonical streams for the original text schedule.
The existing byte-expression theorem removes mandatory byte expansion, but
its implementation still rewalks record wrappers, binds individual ID
strings, copies growing publication tables, and represents captured input
values through their expanded rational encodings.

The [captured-value proof](CAPTURED_TOKEN_VALUES.md) already establishes a
complete representation of those inputs by their actual immutable embedding
bytes, width, lag tuple and grid. Every executed node result remains in its
explicit tail. Serializing the capture need not undo that representation.

Use a **typed value graph**, retaining child references and scalar payloads.
Its decoder recovers the existing canonical bytes; its internal nodes need
not themselves be substrings of that encoding. The capture node uses the
already justified decoder, without rerunning SUM/PRODUCT arithmetic. This
addresses record traversal, input expansion, dictionary growth and
publication in one construction. It does not change any learner action.

The implementation is
`theory/numerical_checks/owned_value_graph_model.py`. It is deliberately outside
`fp_reference`: no public Runtime port can select it or borrow its results.

## 2. Ownership, rather than a frozen annotation, permits reuse

Exact immutable scalars, bytes, recursively immutable tuples and validated
`CapturedTokenValues` retain the existing closed value assumptions. A record
wrapper needs an additional premise:

1. Every path by which an untrusted caller or delegated producer could obtain
   a mutable alias to it is closed by the owner's actual boundary.
2. Every legal internal continuation leaves its canonical fields and trusted
   class metadata unchanged. Successors are new records.
3. Every descendant admitted as stable satisfies the same conditions or is
   in the existing immutable scalar/tuple algebra.

These conditions concern the actual source identity. Equal foreign objects
cannot inherit its fact. Strong references prevent address reuse while a fact
is retained. A frozen dataclass with a writable dictionary does not establish
any of these conditions by itself.

For the observed ordinary native path, constructor declarations and public
returns cross the qualified [detached-value boundary](PUBLIC_VALUE_OWNERSHIP.md).
The byte-only producer receives no source wrapper or iterator. The native
source inspection finds new `TokenWindow`, `TokenEvaluation`, `TokenState`
and `EventTrace` records at their respective transitions; commits construct
new origins. The old fields are not changed. Prediction-cache recomputation,
range checks and target ownership remain in the original Runtime. The audit
also mutates returned probability origins through their dictionaries and
checks that complete private continuations stay identical.

This is **not** a general theorem that every FP dataclass in every future port
is stable. The model's `owned_records=True` states the premise; it cannot
prove ownership. Its default refuses to bind record wrappers. An explicit
negative control asserts ownership over a caller-held `TokenSources`, changes
its dictionary, and obtains a stale cached root. The same mutation under the
default mode is reread correctly. Any production lowering must derive the
premise inside the already isolated owner and prove it for the supported
continuations; exposing this boolean as an authorization port would be wrong.

## 3. Format, independent binding and exact decision class

Each node is an immutable tagged byte payload. Atomic nodes represent None,
bool, signed integer, reduced Fraction, UTF-8/surrogatepass string, or raw
bytes. Composite nodes contain uint64 references to strictly earlier nodes:

- tuple, list, and ordered key/value mapping;
- record module, qualified name, ordered field-name tuple and field values;
- capture's five physical operands: embedding bytes, width, lag tuple, grid,
  and explicit executed-value tail.

Integers and Fraction coordinates use canonical hexadecimal text in this
model. Bytes remain raw. The record decoder emits the old dataclass grammar
directly and does not invoke a constructor. Mapping order is the existing
packed-key sort. The capture decoder independently validates operand types,
uint32 byte layout, width, token indices, power-of-two grid and rational tail.
It reconstructs only the exact input rationals from their captured operands.

The page header is forty bytes: magic, ordinal, first new node, number of new
nodes, and root. Each new payload has an eight-byte length. The reader rejects
invalid tags, noncanonical atoms, undefined children, duplicate definitions,
missing/trailing bytes and inconsistent page prefixes. Exact byte-key equality
decides node identity. Python hashing is an index mechanism, not a digest
certificate or a worst-case constant-time assumption.

The producer receives only node byte messages and returns eight-byte handles.
After it emits a page, a separate reader parses the actual page bytes. A
second owner walk looks up its independently generated node messages in that
reader; it receives neither producer bindings nor intermediate handles. Old
source facts may skip stable subtrees in both walks. Only the second walk's
proposals become source facts, after its root agrees with the parsed root.
Producer, reader and owner do not share allowance wrappers.

**Exact decision class:** the owner's fixed typed expression for the current
complete source, relative to the verified prefix and valid source facts,
within all declared model allowances. A capture and its expanded ordinary
tuple have equal canonical bytes but different typed roots. Substituting one
root for the other refuses. This class is not arbitrary graph or compressed
string equivalence, and issues no `CERTIFIED_COMPLETE` result.

## 4. Preservation and canonical guard theorem

Assume the stability premise for every source fact, the stated component
boundary, a correct retained prefix, and successful bounded operations.
Successful retention preserves every previous decoded value and adds a root
whose expansion is exactly the current complete canonical encoding.

**Proof.** Strict earlier-node references give a finite DAG. Induction over
its nodes establishes each scalar value and each composite's complete
decoding. For captures, the stored embedding bytes and indices determine
exactly the original input Fractions by the captured-value theorem; the
stored tail supplies actual executed node results, not recomputed results.
Record and container rules then reproduce every old syntax and field byte.

The dictionary is structurally injective: distinct byte payloads retain
distinct entries, and duplicate definitions refuse. Induct over the owner's
fresh walk. Each new message represents the actual source fields and earlier
child IDs; a reused source fact represents the same stable source. The second
walk therefore finds the expected structural root in the separate reader.
Root equality proves complete canonical equality. Immutable prior node bytes
and their strict dependencies preserve every old root. New facts are derived
from this checked traversal and the source-stability premise. QED.

The reader also derives four original guard coordinates: expanded size,
aggregate traversal debit, maximum logical depth, and maximum integer bit
length. For an atomic value these are the original scalar formulas. For a
container, traversal is one plus child traversals, depth is the maximum child
depth plus one, and the integer coordinate is the child maximum. Record
module/name/field-name strings contribute exactly the original guard's
metadata visits. Syntax supplies the original exact size. A capture sums the
metrics of its logical rational inputs and tail; its physical embedding byte
length is not confused with its logical tuple size.

Thus each derived root metric equals the original recursive canonical guard
coordinate. A valid fact can answer a later guard without repeating its source
walk. The passive reader additionally bounds **every physical graph node**;
this can be stricter than bounding only a logical root. In particular a large
capture operand may fail a node allowance even when its selected logical
tuple is small. Completeness is conditional on these explicit additional
limits. The model does not preserve every historical refusal's timing/order.

Cold recovery remains an expanded computation, with explicit output-byte and
visit limits. No claim says that printing all historical canonical bytes is
cheap. Ordinary retention need not perform that cold recovery every time.

## 5. Joint resource law and publication

Let M be retained pages, N distinct nodes, A their total atomic payload bytes
excluding one-byte tags, and E the total number of stored child references.
The model's complete serialized payload is **exactly**

    P = 40 M + 9 N + A + 8 E.

This is both an upper and lower identity for this format, not an
information-theoretic optimum over all decoders. Every node definition and
dependency is inside these pages. The independent parser processes this
payload; rebuilding does not require source facts or producer indices.

Let V be source values visited by one owner walk over the whole schedule, Q
the total node-message bytes it constructs, and J the dictionary lookup and
exact-key comparison work. Let G include the decoder's extra semantic metric
work, chiefly the input words inspected for **new distinct capture nodes**.
The construction performs O(M+V+Q+P+G) non-dictionary primitive work plus J.
Scalar arithmetic calls are counted separately from their bit cost; this is
not a bound on arbitrary-precision division/GCD time or Python elapsed time.
It does not contain a repeated full-canonical-volume term D. For a stable
source graph, every bound composite's fields are walked only on its first
encounter, separately by producer and expected traversal; later occurrences
are identity lookups. Mutable/ineligible structures still contribute their
fresh visits to V. Atomic values are not given source bindings merely because
they occur as leaves; large immutable byte sources are bound directly.

Source facts and page/root tables publish by append and insertion of the new
delta. There is no explicit copy of the prior page list or binding table.
Ordinary list/dictionary resizing and allocation remain real costs; no
worst-case hash-table or Python wall-time theorem is inferred. Publication
failure is terminal. The reader already owns the checked page before a new
root is appended; bindings publish only after that append. A partial binding
update therefore refers only to present node definitions. Old roots and
bindings remain; a failed transition cannot continue. This is an actual-prefix
argument, not rollback, and supplies no missing Runtime ledger/frame duty.

The wire identity is not a host-memory bound. The model additionally holds
two indices, parsed nodes and metrics, Python integers/tuples, source facts,
strongly retained sources, page/root containers, producer packets and scratch.
Decoded child-ID tuples alone can substantially exceed their eight-byte wire
slots. Runtime histories, resource metadata, images and numerical workspace
are additional. No 96-GiB/two-hour conclusion follows from P.

### Native schedule consequences

For T completed ordinary targets, unit B, C=floor(T/B) and r=T mod B, there
are at most C+1 committed origins. Their selected distinct master payload is
at most 4S(C+1), rather than the old repeated 8S(8T+5C) canonical master bytes.

Each after-observation `TokenState` creates a windows tuple and a targets
tuple of length j+1 within its unit; the commit state has empty pending tuples.
All after-observation states are retained, including the full unit at commit.
The total pending child-slot count before value interning is exactly

    2 [ C B(B+1)/2 + r(r+1)/2 ].

Interning can reduce stored slots, so eight times this count is a selected
wire upper, not a whole-payload formula. For the original million-target
declaration it is 4,303,355,904 bytes; the master upper is 4,942,942,032 bytes.
Context/lag tuples, captured tails, definitions, other nodes and pages are
additional. Captures have five physical child references instead of LD
rational input children. Their original source/operand information remains.
The current metric implementation still inspects up to TLD input words; it
does not assert constant work per capture.

The initial full manifest still contains its million distinct ID strings as
actual graph data. Removing their **source bindings** does not remove their
nodes or payload. Successful full execution would also exceed the passive
model's current 2^20 binding allowance if every fact were retained forever:
the T after-observation states, T captures and two T nonempty pending tuples
already supply at least 4T distinct source identities. This is a capacity
limit of that policy, not an information lower bound or a full-run result.

### Source facts can be forgotten without forgetting values

A useful distinction is that a source fact is an optimization, while the
page prefix supplies complete historical decoding. Suppose any subset of
valid source facts is removed and the original source values remain available
when later operations actually use them. Rewalking a formerly bound source
produces the same structural expression. All of its old definitions are
already in the exact dictionary, so no extra definition or changed root is
introduced. Induction over subsequent messages gives the same new page bytes
and roots, conditional on successful operations. Metrics likewise agree.

This proves that source facts need not be immortal for retention correctness.
Removing them can increase source work or cause a later resource refusal;
the lemma is not equivalence of resource usage or a cache policy. It does not
permit deleting pages, actual causal records, live source values, numerical
evidence or any semantic authority. No Runtime eviction policy is installed.
The audit checks all pages/roots/derived nodes across 360 retentions with warm
facts versus clearing facts before every retention. Peaks are 145 versus
four source facts; source visits rise from 696 to 1,386.

## 6. Exact evidence and stopping point

`scripts/audit_owned_value_graph.py` and
`evidence/minimal/FP_OWNED_VALUE_GRAPH_MODEL.json` retain minimal exact evidence:

- 120 value cases and 750 canonical guard boundary checks, including Unicode,
  surrogate distinctions, mutable containers and extreme uint32/grid inputs;
- 1,184 single-bit page variants, all refused in this fixture; changed source
  payloads, forward references, malformed capture operands and wrong structural
  roots; six resource-cap refusals and three terminal publication failures;
- 93 complete native histories, 294 targets and 158 commits: 2,239 full
  records/13,976,026 canonical bytes recover from 1,583,132 graph-page bytes;
- fifteen complete Runtime snapshot pairs agree under the observer and public
  origin mutations; every retained small-history source fact is rechecked;
- the **original full training/reporting declaration**, V50,257/S603,092,
  followed by two synthetic targets, with the ordinary byte archive intact.

In that full-declaration control the manifest/initial state needs 1,118,517
nodes, 6,225 source facts and 39,259,286 page bytes. The two actual ordinary
events add **89 nodes, 32 source facts and 7,957 page bytes**, while their
complete canonical records exceed 103 MB. All fifteen initial/ordinary roots
recover 155,227,742 canonical bytes. Capture metric validation reads 4,096
input words; separate full recovery reads another 8,192. These coordinates
are kept distinct. A new reader rebuilt solely from all page bytes agrees
with every derived node and metric. All actual Runtime buffer/role totals pass.

These are source/value counts, not timings, host peaks or a prefix extrapolation
to a successful million-token run. The passive model's node allowance is
2^22 and binding allowance 2^20; neither is a proposed complete-run registration.
Its objects are observer workspace, not paid Runtime artifacts. The ownership
counterexample is a premise boundary, not a newly demonstrated failure of the
unchanged production Runtime.

**Decision:** ordinary next-token learning remains the scientific target. This
joint representation has enough exact evidence to make an owned lowering the
next concrete question; another static relation case or local byte-codec timing
variant is not needed. Establish the real owner-derived source boundary,
complete resource/failure accounting and total dictionary/memo/host budget
before a new full trial. Actual AMP frames retain all original fresh-read,
padding and bridge obligations; this native graph model waives none of them.
The old text attempt and every terminal cost/device journal stay closed.
No shorter score is substituted for the original full training comparison.

The subsequent [owned Runtime lowering](OWNED_VALUE_GRAPH_RUNTIME.md) supplies
the private source boundary, bounded FIFO memo and complete frame/failure
protocol. Its scoped CPU evidence is separate from this unchanged passive
model; actual-device and full-run budget duties remain explicit.
