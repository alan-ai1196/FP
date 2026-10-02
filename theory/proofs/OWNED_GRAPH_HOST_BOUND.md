# The complete ordinary graph exceeds its original host budget

Status (2026-10-03): **CONDITIONAL SOURCE/ABI HOST EXCLUSION; EXACT CPU AND
ORIGINAL TRAINING-CONTEXT CENSUS PASS**. The selected disjoint live allocations
require at least **108,591,184,675 bytes (101.1334217 GiB)**, exceeding the
original 96-GiB host allowance. This excludes the unchanged native graph
realization, even with its small qualification node cap hypothetically relaxed.

The subject is the native graph qualified at `9fe66f1`/`e0f8d80`, with production
unchanged at `84c118c`. The original ordinary-text trajectory, semantic update,
information interface, Foundation/ERC and closed journals remain unchanged.
We allow the qualification node cap to be relaxed *for this lower-bound
argument only*: otherwise the [node count](OWNED_GRAPH_SCHEDULE_BUDGET.md)
already excludes completion. No full attempt or new cap is registered here.

## 1. Allocation premise and the observer trap

Use the installed Windows x64 CPython 3.12.9 standard allocator. The audit
checks the actual MEM/OBJ allocator using `_PyMem_GetCurrentAllocatorName`,
which compares the allocator functions, not an environment-variable claim.
The standard Windows arena allocator uses committed private memory; arbitrary
replacement arena allocators are outside this realization premise. See the
pinned [allocator implementation](https://github.com/python/cpython/blob/v3.12.9/Objects/obmalloc.c).

On this ABI, pointers occupy eight bytes, tuple headers 40, byte-string headers
33 and compact ASCII string headers 41. Small allocations through 512 bytes
use a 16-byte quantum: a 28-byte non-small Python integer occupies at least
32 allocated bytes. The actual x64 preprocessor definition, rather than the
older explanatory table, determines that quantum in
[pycore_obmalloc.h](https://github.com/python/cpython/blob/v3.12.9/Include/internal/pycore_obmalloc.h).
Larger allocations are charged only their requested extent. Disjoint live
allocations therefore lower-bound private commitment under this premise;
paging does not remove their commitment obligation.

An ordinary managed dataclass instance occupies 48 object/preheader/GC bytes,
with separately allocated attribute-value cells. Its dictionary shell may
not exist yet. Asking for `vars(record)` can materialize it, so that observer
must not create the storage it then claims was already present. Four and six
attribute cells plus their insertion-order prefixes require at least 48 and
64 allocated bytes respectively. The split values and dictionary
materialization are separate in
[dictobject.c](https://github.com/python/cpython/blob/v3.12.9/Objects/dictobject.c);
[object.c](https://github.com/python/cpython/blob/v3.12.9/Objects/object.c)
shows the dictionary request path. Shared class keys are excluded.

The audit inspects GC referents before field access, never calls `vars` on
counted lazy metadata, and verifies that inspection does not change dictionary
presence. A separate witness proves that `vars` would change it. Actual typed
source records traverse the owner's dictionary check, except the replaced
after-target ObservationRecord; its potentially lazy dictionary is excluded.
For materialized records only the distinct 64-byte dictionary shell is added,
with value cells already charged separately.

## 2. Source counts and selected disjoint terms

Take T>0 completed native targets, update unit B, context length L, S master
coordinates, A executed arithmetic nodes per prediction and P declared report
identities. There are no additional search/profile/device/report events in
this interval. Let C=floor(T/B), r=T mod B and

    M=5T+C, O=12T+2C, I=6T+C, J=50T+9C+2,
    W=C B(B+1)/2+r(r+1)/2.

These are the [exact schedule](OWNED_GRAPH_SCHEDULE_BUDGET.md) with zero
changed-master commits. Actual changes only add the relevant pages/objects/
events; all following terms are monotone lower bounds. Initialization is
excluded except the explicitly selected train/report strings and contexts.

Let D be the number of distinct integer-only causal context tuples among
these events, and R a lower bound on child occurrences in those D tuples
whose scalar-node IDs exceed 256. The disjoint forced graph-node count is

    N = 14T + P + 2C - 1 + D.

This combines 13T+2C-1 forced new definitions, T+P distinct declared identity
strings and D context tuples. Integer-only context tuples cannot equal the
all-window pending tuples or the string-headed pre-target tuples. No other
initial nodes are credited; changing the node cap cannot invalidate an
initialization count that was not borrowed.

Write g(x)=max(0,x-257). The sum H of these terms is a host-allocation lower:

| Distinct selected allocation family | Lower bytes |
| --- | ---: |
| Pending vectors, both raw indices, parsed children and original two tuples | 197T+80W |
| Live lease/buffer indices, ObjectSpecs, leases and their mappings | 1328O+64g(O) |
| Retired-identity index | 256I+32g(I) |
| ResourceEvent shells, value arrays, log links and sequence integers | 176J+32g(J) |
| Nonempty event object-ID tuples | 48(7M+4T+1) |
| Event debit tuples and their pair members | 112(5M+7T+2C+2) |
| Forced record/pre-target/window definitions | sum (117+32k) n_k, below |
| Four private-name string definitions per event | 1108T |
| Their four original source strings | 323T |
| Declared train-name definitions | 146T |
| Page byte headers and fixed 40-byte page framing | 73M |
| Surviving 16-byte root bytearrays | 73(4T+C) |
| Retained ingress body payload | 4096T |
| Fresh committed master byte payloads | 4SC |
| Original per-event context tuples | (40+8L)T |
| Native record instances, attribute cells and existing dictionaries | 48(7T+C)+264T+24C+64(6T+C) |
| Capture and executed-tail tuple containers | (120+8A)T |
| Executed Fraction instance shells | 48AT |
| Graph-node parsed pairs, metrics, pointer slots and index integers | 216N+64g(N) |
| D context definitions and their non-small parsed child integers | 117D+32DL+32R |

The record-definition (k,n_k) pairs are (12,T) for IngressIdentity; (6,T) for
TokenContext; (10,T) for pre-target ObservationRecord; (9,T) for TokenEvaluation;
(10,T+C) for EventTrace; (6,T+C) for TokenState; (4,T) for the pre-target tuple;
and (6,T-1) for TokenWindow. Their names/type-schema children are not additionally
counted. The lower remains valid for the first window, already present initially.

Here is the allocation derivation, including potential alias boundaries:

* Each OwnedMap entry has two distinct 96-byte AVL nodes and one 64-byte
  Entry block. A weighted lease entry additionally has distinct six-element
  weight/total tuples, 96 bytes each. The lease and buffer maps have independent
  ordinal allocations, with at most 257 small cached values per map.
* Each live ObjectSpec contributes its 48-byte instance, at least 48 bytes
  of managed cells and a 48-byte mapping proxy over a distinct at-least-192-byte
  dictionary. Each lease contributes 48+48+192 bytes. Their indices contribute
  448+256 bytes. The sum is 1328 per object; numeric referents are excluded.
* Every resource event has a 48-byte instance, at least 64 bytes of cells and
  a distinct 64-byte linked-log pair. Non-small sequence integers are fresh.
  Each graph retention has seven nonempty object-ID event tuples and five
  nonempty debit tuples. Ingress, learner releases, work and the initial program
  acquisition supply the remaining terms. A debit has a 48-byte outer tuple
  and a distinct 64-byte pair; the pair's referenced numbers are excluded.
* Each graph node has its 64-byte parsed pair, a fresh 48-byte Metrics instance
  plus at least 48 bytes of cells, and seven eight-byte pointer slots: five
  top-level lists and a bucket slot in each independent index. Distinct producer
  and reader non-small index integers add 64g(N). Bucket headers, CRC keys,
  dictionary capacity, metric integer referents and list slack are excluded.
* A k-child definition occupies 9+8k bytes inside a page, two separately
  allocated raw `bytes` of at least 34+8k bytes each, and a parsed child tuple
  of at least 40+8k bytes. The sum is 117+32k before child integer objects.
  `struct.iter_unpack` separately creates every non-small child integer,
  including repeated equal IDs. Pending-window IDs all exceed 256 on this
  path. Scalar context IDs need the separate R bound below.
* A private string definition of ASCII length x contributes 118+4x across
  page extent, both raw indices and the reader's decoded string. The runtime
  name has 24 hex characters; the four ingress-derived names have minimum
  lengths 34,40,42,43. Their originals are separate strings. `train/i` has
  length at least seven. Report string payload is excluded, but its node
  metadata is included. Increasing revision/index digit counts cannot lower H.
* Every observation retains seven fresh native records with 33 attribute
  cells in total. Six have already materialized dictionaries; the observed
  target-bearing record's dictionary is excluded. A commit adds a fresh
  three-field TokenState with its own dictionary. Captures retain their actual
  five-tuple and A-result tuple. Executed Fraction results are freshly allocated
  by each arithmetic operation even when equal or zero. Each commit creates
  fresh embedding/core/output byte strings; only their total 4S payload is
  counted. None of their integer/array views or decoded graph byte values is
  charged again here.

Page headers and selected definition extents are disjoint ranges in the same
actual immutable page, not separately allocated copies. No complete page size
is also added. Likewise a parsed-node pair is counted in node metadata, while
its referenced child tuple is counted in exactly one selected definition
family. Source contexts, graph contexts and pending tuples are distinct.
The audit uses a global identity set over all selected Python objects, rejecting
any duplicate before summation. Hidden value arrays are charged only once per
distinct instance and separately from materialized dictionary shells.

## 3. Exact corpus statistic without predicting an allocation order

For the original view, T=2^20, B=L=512, S=603092, A=8 and P=16384. Let h(v)
count token v's occurrences across the D **distinct** length-L contexts,
including PAD. Distinct labels have distinct scalar graph-node IDs. At most
257 labels can have IDs in 0..256, even if every such ID were available for
the most frequent labels. Therefore

    R >= DL - sum of the 257 largest values of h.

This is a lower bound independent of the graph's actual scalar allocation
order or model weights. It is not the false assumption that every parsed
context ID is non-small. It is also not a corpus-independent D=T assumption.

The preregistered census stores exact immutable context byte strings in a
set; hash equality alone never merges contexts. For each first distinct window
it adds +1/-1 at its interval boundaries in an integer difference array. Its
prefix sum and an integer indexed accumulation produce h exactly. Runtime's
reverse-lag order is a bijection of these chronological windows, preserving
both distinctness and token multiplicity. No census result is supplied to a
learner or to Runtime; this is a conditional cost proof for a fixed original
trajectory, not legal pre-target model information.

If H exceeds 96 GiB, this unchanged realization cannot finish even after
relaxing its small node cap. If H is below the cap, feasibility remains
UNRESOLVED: the unselected bytes and transient execution have no upper bound
here. Neither outcome identifies the original interrupted worker's cause,
gives a wall-time result, rules out other lossless representations or issues
a completeness certificate.

## 4. Minimal exact evidence and next decision

`audit_owned_graph_host_bound.py` checks all sixteen four-target binary words
at units 1/2/4, plus all-zero sixteen-target histories at units 1/2/4/8:
52 complete histories, 256 targets and 208 distinct-context occurrences across
the controls. Every formula term is checked against selected actual disjoint
allocations; their aggregate is 21,335,280 bytes. A separate parser control
checks 767 distinct non-small child allocations in two length-512 contexts,
including 512 occurrences of the same ID. The explicit lazy-dictionary witness
guards against observer-created storage. The CPU receipt is
`FP_OWNED_GRAPH_HOST_BOUND_CPU.json`.

The census algorithm passes 4,368 exhaustive small words/context lengths
against an independent full-tuple/Counter oracle. All adversarial choices of
cache-resident labels verify its small-ID bound. That receipt is
`FP_OWNED_GRAPH_CONTEXT_CENSUS_CPU.json`; it contains no corpus result.

One [bounded census](../../experiments/next_token/OWNED_GRAPH_CONTEXT_CENSUS_A1.md)
was registered before accessing the original training view. Its result closes
the budget decision below, without a repeated device qualification, shortened
model score or new production variant.

## 5. Original-view result and research consequence

The one census at committed source `93f3f25` passes. Its source prefix exactly
matches the completed baseline anchor. It reads no validation data and creates
no Runtime or learner. The retained aggregates are:

| Exact coordinate | Value |
| --- | ---: |
| Distinct causal length-512 contexts D | 1,048,576 |
| Child occurrences across distinct contexts DL | 536,870,912 |
| Sum of the 257 largest label multiplicities | 269,690,660 |
| Guaranteed non-small parsed child occurrences R | 267,180,252 |
| Forced selected graph nodes N | 15,749,119 |
| Selected disjoint host-allocation lower H | 108,591,184,675 bytes |
| Original 96-GiB cap | 103,079,215,104 bytes |
| **Excess over the whole cap** | **5,511,969,571 bytes** |

All twenty exact allocation terms appear in
`FP_OWNED_GRAPH_CONTEXT_CENSUS_A1.json`. The largest selected components are
24.07685 GiB for distinct context definitions, 20.23145 GiB for pending
vectors, 16.31780 GiB for live lease/buffer metadata and 10.15981 GiB for
resource-event shells/log links. Original source contexts add 4.03906 GiB;
committed master payloads add 4.60123 GiB. These are disjoint source-derived
lower terms, not proportional extrapolations of the census worker's peak.

The disposable job exits zero without timeout, in 1.7259234 launcher seconds,
with 1,290,907,648 peak job-commit bytes inside four GiB. Both process creation
identities match; inputs stay unchanged and the worker is absent after exit.
These are census diagnostics, not FP training-time or memory observations.
The exclusive journal is terminal; no replay or full run is needed to observe
this already proved host exclusion.

This establishes **realization infeasibility**, not a Foundation information
lower bound. All ordinary causal contexts are overlapping views of the same
retained token prefix; pending windows are successive prefixes within update
units. Their distinctness does not make their information independent. The
current flat tuples and independently parsed child integers materialize those
overlaps, while complete resource histories have their own substantial object
cost. A later lossless refinement must justify the *joint* stored values,
metadata, verification and execution budget, rather than remove one selected
term and declare fit. Decoding, actual executed values, numerical/AMP evidence,
failure prefixes and legal future information remain paid obligations.

Do not launch the unchanged graph on the original full trajectory or transfer
its tiny qualification cap. Do not infer the old interrupted A1 worker's cause
or rule out a different fully accounted realization. Ordinary next-token model
science remains the objective, with no trained FP score yet; Foundation/ERC,
relation/precision, this graph's scoped qualification and all old journals stay
closed. No new semantic action or `CERTIFIED_COMPLETE` authority follows.
