# Retain complete graph pages and reconstruct only the fields a query needs

Status (2026-10-03): **CONDITIONAL STORAGE/WORK LAW; PASSIVE COMPLETE-RUNTIME CPU
SUBSTITUTION PASSES, INCLUDING FULL VOCABULARY AND CPU TENSOR FRAMES**.
Production remains the host-excluded realization at `36dfcc1`. This model
does not establish full-host fit, actual AMP qualification or a trained score.

## 1. The information that must survive

The [host exclusion](OWNED_GRAPH_HOST_BOUND.md) counts large resident copies
of raw definitions, parsed child tuples, integers and decoded scalar values.
Their information is already in the complete immutable graph pages. Under
the existing verified-prefix and private-owner premises, every such parsed
value is a deterministic function of a retained page extent. Discarding its
materialized copy loses no value, provided every later requested field is
reconstructed from those actual bytes with its work and temporary storage paid.

This differs from forgetting a source or retaining a claimed digest. The
page bytes, every root, all original sources, native histories, numerical
results, resource histories and owner bindings remain. The wire grammar,
definition order and source/target interfaces are unchanged. The independent
reader receives actual immutable pages, not producer indices or expected values.

`page_resident_graph_model.py` implements this construction outside production.
Its `Owner` is substituted only by the audit at the existing private Runtime
owner boundary; there is no new public learner, certificate or installation
port. The original eager implementation supplies an independent value/wire
oracle and cold reconstruction from the same actual pages.

## 2. Page locators and checked metadata

Both producer and reader keep independent fixed-width locator rows:

    (page ordinal, byte offset, byte length, CRC32).

Each row has four uint64 cells. An independent open-address table stores node
IDs plus one, with zero reserved for empty slots. CRC selects possible entries;
matching length/CRC still requires full equality of actual node bytes. Probe
count and compared bytes have separate bounded counters. Resizing rebuilds a
new table from all complete locator rows before replacing the current table.
No Python tuple/key/bucket/integer object is retained per locator or hash slot.

The reader stores five uint64 coordinates per checked node: canonical size,
traversal, depth, integer bits and unfolded references. These come from the
existing complete grammar parser, including the aggregate semantic-work
guard on unused captures. Successful values must satisfy all original guards
before a checked row is published. Packed rows are allocated in 4,096-row
blocks; extending a block directory does not copy the old row contents.

While building, producer locators can refer to its already paid, append-only
workspace. Acceptance requires immutable bytes identical to its entire written
page, including framing. Locators then resolve into that same accepted page.
The reader's pending page is already immutable and separately checked. All
historical page extents remain immutable and live after workspace reuse.

Partial row/table/page publication is terminal. The reader retains its failed
pending page and refuses another append; old checked roots remain recoverable.
The Runtime owner preserves its original paid failure prefix, revealed target,
old learner and frame/generation pins. This is not rollback or a permission to
reuse partially checked new state.

## 3. Field projection is necessary to control reconstruction work

A naive lazy node table computes a complete `(tag, value)` pair at every
lookup. The existing parser often requests only `[0]`, the tag. Decoding a
large child to answer that query can multiply work by its repeated occurrence
count, even when no new payload is being materialized into the archive.

An exact necessity control has a 1,024-byte leaf and an unused eight-reference
tuple. Its maximum unfolded-reference count is only nine. A naive unmetered
lookup reconstructs **8,208 bytes** during tag checks against allowance 2,048;
the metered naive version refuses. The selected field projection answers those
same queries with **eight tag-byte reads** and accepts. The first unprojected
full-manifest control also exhausted its reconstruction allowance; the
field-projected version passes the original full declaration unchanged.

Each logical node view therefore has two fields. Reading its tag charges and
reads one byte. Reading its value charges the complete raw node extent before
constructing the exact scalar or parsed child tuple. A transient view is not
stored in the node table. Previously verified immutable bytes permit this
projection; a caller's tag/ownership claim never substitutes for those bytes.

Projection does not make value reads free. A second control has an unused
valid capture referencing an 8,192-byte operand. The eager parser accepts;
the compact reader refuses before exceeding its 2,048-byte reconstruction
allowance. This is a declared computation refusal, not malformed syntax or a
Foundation counterexample. Raising no cap is necessary for the original full
declaration's successful field-projected control.

Per page, lookup reconstruction is bounded by the existing reference allowance
R; semantic capture visits have their own original bound R. Each index bounds
probe count and actual comparison bytes separately by C. Initial node parsing
reads the page once, in addition to those metered lookups. Thus the new index/
lookup primitive work is bounded by `4C+R` for the two indices and reader,
plus page scanning, row operations and the original semantic/source/arithmetic
work. This is an abstract work account, not a Python instruction, arbitrary-
precision bit-time or wall-time bound. Merely preserving old work debits would
not fund the changed realization. Before any producer call, the model owner
adds the following explicit metadata prepayment to the original page charge:

    256C + 8R + 32L + 104B,

where L is the literal workspace and B=4096. This funds the two index probe/
comparison envelopes including fixed-width locator accesses and table growth,
the reconstruction-byte envelope, and new row-block capacity including its
rounding. A page can introduce at most L/9 nodes, so 32L exceeds their 104-byte
combined row payload, while 104B covers block rounding. Rehashing meters each
insertion probe, including those for old entries; it cannot hide a long rebuild
behind an uncharged resize. Host allocation and deadline duties remain separate.

The comparison audit checks this exact additional debit at **every** graph
work event and every affected role total; every other resource field and
complete snapshot field agrees. It does not drop resource records from the
comparison or call changed host/work behavior a complete-Compiler equivalence.

Cold recovery uses a fresh lookup allowance equal to its declared output-byte
plus visit allowances, in addition to the original byte/visit guards. Exhaustion
returns a resource refusal. The meter belongs to the **recovery continuation**.
Installing a mutable reader-wide meter for the lifetime of a generator is
incorrect: yield A, start/yield a larger-budget B, then resume A. A can now
borrow B's allowance even though both calls used valid public arguments.

An explicit control makes the ambient-meter version complete a small-budget
capture by borrowing a second call's 40,000-byte allowance for its 8,192-byte
operand. The selected reader refuses that first recovery, independently
completes the second and leaves the parser meter unchanged. No direct private
mutation or forged limit is needed to exhibit the unsafe scheduling.

The implementation activates the generator's own meter only around each
`next`/`close` step and resets it **before** yielding to its caller, including
exceptional exits. Context-local routing also separates reader threads.
Induction over any interleaving shows that each debit changes only its active
continuation's counter and stays within that continuation's fixed allowance;
a suspended continuation changes neither another recovery nor the parser.
This is a correction to the passive implementation, not a claim that the old
eager production reader or Foundation had this bug. It does not authorize any
future read for free or identify physical resource behavior across realizations.

## 4. Exact retained table capacity and a peak bound

Let P be the complete immutable page bytes, M the number of pages, N the
number of checked nodes, B=4096 and

    K = ceil(N/B),
    C(N) = max(16, least power of two at least 2N).

At an accepted prefix, both indices have the same N and hash capacity C(N).
Their two four-cell locator stores and the reader's five-cell metadata store
have the **exact committed payload capacity**

    H_tables(N) = 104 B K + 16 C(N).

This includes unused block/table slots. It is both an upper and lower identity
for those buffers, not a payload-only estimate that omits a parsed-value heap.
There is no retained raw-node or parsed-value copy. For N>0,

    H_tables(N) < 168N + 104B + 256.

During serialized growth, at most one old hash table additionally coexists
with its replacement; its size is at most 4C(N) bytes measured against the
new capacity. Hence the selected index/metric payload peak is at most

    104 B K + 20 C(N),

apart from the bounded current row/packet. During an in-progress or failed
page, N is an upper bound on both written and checked node counts, including
the pending rows; the accepted-prefix equality becomes an upper bound.
Allocation failure cannot silently
discard that temporary cost. Fixed wrappers, block headers/directories and
the page/root lists add `O(K+M)` Python metadata, with bounded-width ordinals.
They are not included in the exact buffer-capacity identity. All other Runtime
sources, resource records, workspaces and transient parser/canonical/numerical
objects remain additional obligations.

The complete retained graph therefore has a `P+O(N+M)` storage realization
without separately retained copies proportional to decoded child occurrences
or raw atomic bytes. P still contains every original flat reference and byte;
this is not compression of the wire format or an information optimum.
Hash collision work is explicitly bounded, not assumed constant in the worst
case. A physical success/refusal can differ from the eager implementation.

Capacity controls cross node counts 1,8,9,4096,4097,8193 and every intervening
hash growth. They verify the identity and growth bound on the actual buffers,
independent index objects and shared immutable page identities. A failure
after a private checked row verifies that no complete new root is granted,
another append refuses and all earlier roots still decode exactly.

## 5. Complete CPU evidence and the remaining decision

The focused audit checks 125 typed values with forced CRC collisions, 600
single-bit page corruptions, mutable/changed producer-page attacks and all
93 binary native histories through length four at units one/two/four. All
294 targets/158 commits have exactly equal original pages and complete values.
The additional metadata work is checked event by event and role by role;
all other complete snapshot fields, canonical encodings, leases and residency
totals agree. Every compact page is the actual paid Runtime buffer; independent
cold eager reconstruction agrees with all nodes and metrics.

Twenty CPU tensor-history pairs preserve 340 phases, 126,797 primitive words
and **356,515,840 original complete frame bytes**, including profiles and frozen
reports. Three nonzero-padding frames and 22 post-target failures pass; unfunded
body reads refuse and changed actual tensors cannot reuse stale evidence.
These are CPU controls, not actual-device qualification.

The original full-V/train/report declaration plus two synthetic targets passes
without corpus access. Initialization has 1,118,517 nodes and 39,259,233 page
bytes. Its compact table capacities total **183,828,480 bytes**, including all
reserved slots; pages plus those tables total 223,087,713 bytes. The two targets
add the same 89 nodes/7,957 bytes as the eager realization. All fifteen original
records recover 155,227,697 canonical bytes, and all physical buffer/lease
checks pass. These initial values are not a full-horizon slope or host peak.

Minimal receipts: `FP_PAGE_RESIDENT_GRAPH_CPU.json`,
`FP_PAGE_RESIDENT_GRAPH_FULL_V_CPU.json`, `FP_PAGE_RESIDENT_GRAPH_TENSOR_CPU.json`.

This removes the duplicated-materialization premise from the proposed graph
store. It does not yet remove the **production** host exclusion or prove the
remaining complete 96-GiB budget fits. Promotion must cover the live owner,
public cold decoder, actual host/AMP paths and bounded failure behavior together.
The whole-budget assessment must retain native histories, resource metadata,
numeric storage and transient peaks. A successful tiny control or subtraction
from the old lower cannot certify fit. Continue this one general storage
refinement toward the original full next-token run; keep the grammar,
Foundation/ERC, relation/precision and historical journals closed.
