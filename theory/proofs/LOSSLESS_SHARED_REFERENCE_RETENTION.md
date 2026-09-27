# Lossless shared retention of complete reference records

Status: representation theorem and exact CPU/actual native Runtime controls.
This is an implementation result under frozen Foundation/ERC, not a new
semantic action, a universal memory optimum or a language-model result.

## 1. The obstruction and the chosen boundary

The actual token AMP owner A2 succeeds for eight full-vocabulary/context512
events. Its fixed64-MiB frames nevertheless forbid completing15 events under
the registered2-GiB reference-payload cap; see
[the exact counting argument](../../experiments/next_token/OWNED_TOKEN_AMP.md#6-actual-a2-result-and-the-next-resource-barrier).
Native event records independently repeat the same master origins,
definitions, predictions and earlier pending records when serialized.
Only changing a frame cap would leave that duplication in place.

The present lowering retains a lossless encoding of the same packed records.
It does not select supposedly sufficient numerical coordinates. In particular,
neither current gradients nor equal exact/current sums identify a floating
continuation forest. That counterexample remains binding.

`SharedReferenceContract` registers finite literal/program workspaces,
expanded-byte/reference/comparison allowances and the exact codec identity.
It is currently accepted only by the actual native token Runtime with its
ordinary events, profiles and existing information rules. CUDA use explicitly
refuses pending a separate transition argument. The default representation
and all old terminal experiments are unchanged.

## 2. Complete byte format and induction

The trusted canonical serializer emits immutable byte pieces of length1–8192.
Short syntax fragments are coalesced; substantial literal fragments keep
repeatable boundaries. This choice affects size, not the decoded value.
The producer receives these bytes only: no semantic record, expected iterator,
Runtime root, source object or mutable expected-state alias crosses its API.

Page i contains:

- a64-byte header with ordinal, first new piece ID, counts and exact lengths;
- each new literal as its four-byte length followed by every literal byte;
- one independent bounded zlib stream of ordered unsigned64-bit piece IDs.

An earlier literal is reused only after exact byte equality. CRC32 chooses a
lookup bucket; collisions neither prove equality nor lose data. A registered
comparison allowance charges every candidate byte comparison before it runs.
Adversarial collisions may cause UNRESOLVED. No cryptographic identity is
needed for interning, and no checksum substitutes for comparing the result.

The reader is separate from the producer index. It requires complete immutable
pages in their original order, validates every literal extent, and bounds
decompression by both the registered reference limit and the declared count.
Every reference in page i must name a piece already defined by page i.
Adding later pages cannot repair an invalid forward reference. Output byte
count, reference count, compressed EOF and absence of trailing bytes are
checked. Runtime compares every decoded byte against a new traversal of its
own canonical record before completing retention.

**Preservation theorem.** Let pages0 through i pass this comparison, with
expanded streams S0 through Si. Retain every page as immutable bytes and the
ordered page identity table. For each j<=i, the independent decoder returns
exactly Sj, including all type tags, arbitrary byte values, field/order data,
integer/fraction coordinates and physical floating words encoded as bytes.

Proof: page0 contains every referenced literal. Its checked reference program
expands to S0. Inductively, all earlier literals remain byte-identical; a new
literal is retained in full; every reference is restricted to that prefix.
Concatenation therefore reproduces the checked stream Si. Appending pages
does not change any earlier header, program, literal or allowed reference
range. Rebuilding the reader from retained pages yields the same result; the
producer index and mutable workspaces are unnecessary for decoding. QED.

This is equivalence of decoded records under a declared representation.
Physical buffer formats, allocation histories and resource outcomes differ.
It is not literal equality of raw RuntimeSnapshot buffer arrays. Native
programs, learners, original observations and causal information interfaces
are unchanged. Every supported future that reads these records can recover
the identical values, conditional on paying its decoder work and workspace.

## 3. Actual ownership and failures

Runtime retains each accepted page under its information owner and a separate
deployment dependency lease. All pages and the four reusable workspaces are
conservatively charged to both roles, even when a particular deployment does
not currently need every page. A sixteen-byte root owned by the original
candidate/data owner identifies the page. A short root does not hide its
dictionary in another role's budget. Releasing an old root never releases
page dependencies; this implementation performs no history reclamation.

Page construction uses admitted literal, compressed-program, reference-chunk
and canonical-staging buffers. After determining the exact output extent,
Runtime admits a mutable output before writing it, then separately admits the
immutable page before copying. Both copies coexist and remain paid until
successful final retention releases the mutable copy. The page/root complete
before the existing native learner publication. Initializer, observations,
source contexts, ordinary/profile clocks and numerical updates do not change.

Work for bounded traversal, compression, independent full decoding, exact
collision comparisons, copies and index/ledger metadata is charged before
serialization. A shared materialization plan initially describes only its
sixteen-byte root and complete value; it does not traverse the body to compute
the former expanded size before this payment. These are abstract primitive
tariffs; they do not bound the
whole CPython heap, library workspace or wall time. Actual process/job limits
remain a separate obligation. Decoder compression is never assumed to have
a favorable ratio.

An ordinary post-target failure retains the actual target and original source,
the complete observed native recipe, paid workspaces and any created page
copies. No native successor publishes, and the Runtime halts. Producer or
decoder failure cannot become a successful page certificate. Failed partial
outputs are retained diagnostics; builtin MemoryError keeps the existing
terminal host-failure boundary. Mutable ingress and target slots continue to
use their original direct representations and write protocol.

Public snapshot decoding is passive inspection only. It cannot feed a new
typed source, sign a bridge, provide fresh statistical evidence, construct a
candidate from trained values or install a learner.

## 4. Exact payload law and limitations

Let M be the number of accepted retained pages, R the number of their live
sixteen-byte roots, U the distinct retained literal pieces, and Zi the stored
compressed reference-program length of page i. After completed retention,
with no unfinished failed page, registered literal and program workspaces
L and P give the exact archive payload

`L + P + 65536 + 512 + 64*M + sum(u in U)(4+len(u)) + sum_i Zi + 16*R`.

Other Runtime data are additional. During finalization of a page of size Bi,
its mutable output adds a further Bi bytes while the immutable copy is live.
Both role budgets include these dependencies. Snapshot page payloads share
immutable bytes; copied sixteen-byte roots and all unrelated snapshot/host
metadata remain separate costs.

Thus repeated literal bodies pay once plus their reference programs. Distinct
origins remain distinct unless their complete literal bytes actually agree.
No bound here replaces Zi by zero, promises sublinear arbitrary histories,
or proves that every corpus fits. All-distinct data can grow linearly in the
original input and incur format overhead. The implementation also still
traverses each complete record when it verifies a page: this is a retention
improvement, not an incremental-serialization or training-throughput theorem.

## 5. Exact controls and next application

`scripts/audit_shared_token_retention.py` checks arbitrary bytes, distinct
Unicode encodings, fractions and typed containers; forced checksum collisions;
old pages after workspace overwrite and index reconstruction; malformed and
future references; and funded expansion/comparison refusal. Actual native
Runtime ordinary/profile trajectories match the unchanged learner and decode
every checked root to its original complete packed record. Post-target faults
exercise changed producer output, copy/page residency, dependency-role work
and writer failures. All72 ordinary candidate observations,24 profile events
and526 complete roots/4,921,074 decoded bytes match. The existing ordinary
event/profile and CPU installation regressions pass. Minimal counts are in
`evidence/minimal/FP_SHARED_TOKEN_RETENTION_CPU.json`.

This closes the native retention control, not the long-run training question.
Apply the same complete-byte principle to CUDA evidence with explicit frame
and failure preservation, then measure a bounded full-vocabulary owned unit.
Arena addresses and floating forests have not been retired or compressed.
No new static relation cases, device replays, persistence/install or model
quality claim follow from this result.
