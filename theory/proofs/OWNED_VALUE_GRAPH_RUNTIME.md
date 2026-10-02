# Owned typed-value retention with bounded source facts

Status (2026-10-03): **IMPLEMENTED, DEFAULT OFF; SCOPED CPU/ACTUAL AMP QUALIFICATION CLOSED**.
The [passive theorem](OWNED_VALUE_GRAPH_RETENTION.md) now has a private Runtime
lowering. This changes storage/checking execution, not FP semantics or learner
actions. Foundation/ERC remain frozen. No trained score, full-run resource
claim or new `CERTIFIED_COMPLETE` class is inferred. The actual-device result
below is confined to its separately registered complete control.

## 1. The actual source boundary

`_ValueGraphReference` is constructed by the existing Runtime constructor
after joint detachment of all supplied declarations and selection of its own
token reference machine. Its inputs come from the existing private retention
path, including ordinary events, profiles and frozen reporting. There is no
public `retain`/ownership-assertion port, supplied reference machine, or new
installation path. Existing shared-storage/policy restrictions remain.

The private `_OwnedWalk` can bind a closed frozen FP record only when all its
children are also stable. The owner premise comes from the qualified public
copy boundary, the byte-only producer interface and trusted value transitions:
native predictions, observed learners, committed origins and changed traces
are new records. Revalidation/normalization of declarations preserves their
typed values; source-wrapper identity alone does not grant authority. Lists,
mappings, foreign records and records with extra dictionary fields still walk
afresh. Captures validate all five immutable operands before binding.

Neither a frozen annotation nor importing this private traversal proves these
conditions for caller-held objects. The passive stale-binding witness remains
valid outside the owner premise. Private Runtime mutation, trusted-code/class
replacement and arbitrary process reflection remain outside the registered
component fault model. Public constructor/getter/prediction/snapshot mutations
are inside it and remain isolated by actual transitive detachment.

## 2. Bounded memo without historical deletion

The new encoding ID is `complete-owned-typed-value-graph-u64-pages-v1`.
`SharedReferenceContract` keeps its existing fields. For this encoding,
`expression_nodes` caps each derived node index and `expression_bindings=K`
caps each source memo. Existing archive encodings and their field meanings
are unchanged; the default is still the byte archive.

The persistent memo uses deterministic FIFO replacement. Each producer or
expected traversal has a separate transient memo of at most K entries; when
that transient memo is full, the traversal continues without adding a fact.
Pure eligibility does not depend on retaining a fact. At most two such memo
maps coexist during a successful pass: the persistent map and the current
walk's proposals. Failed stacks, caller snapshots and other host state remain
subject to the actual host budget, not a claim of two-K whole-host residency.

Only independently checked proposals publish, after producer acceptance and
page-list append. Each insertion evicts the oldest fact if necessary. There
is no copy of the old page list or entire source table. The retained node
definitions/pages do not disappear. If a source is later used after eviction,
its fresh walk finds the same structural expression in the complete prefix.
Thus the passive eviction lemma applies; work can increase, while values and
canonical bytes remain complete. No optimal caching or full-horizon bound is
claimed for this fixed policy.

Snapshots expose detached source/root pairs in FIFO order, never private
mutable memo/metric wrappers. Guard lookups derive metrics from the separate
reader's verified nodes. An existing canonical-image fact can also answer a
guard, under its original exact-source rules. Native graph retention creates
no new image solely to serialize the same operands. Original phase writing
may still prepare/use canonical images; owned positive-base facts are unchanged.

## 3. Paid pages and exact decision class

All four existing workspaces remain admitted in both compiler/deployment
roles. The producer receives only immutable byte messages and its admitted
literal workspace, protected by the existing private buffer exports. It writes
new definitions into that fixed workspace, reports an extent, and writes the
separately admitted exact mutable output. The complete immutable page is also
admitted in both roles before independent parsing. A sixteen-byte root cannot
hide its dictionary in a different role's budget.

Producer and reader use separate exact indices and allowance wrappers.
CRC32/length only select candidate node definitions. Every candidate requires
full byte equality and a pre-comparison debit; collisions cannot establish
identity. Node count, page bytes, expanded/traversal/depth/integer limits,
unfolded references and comparison allowances independently bind. Integer
syntax is bounded before parsing a potentially huge integer/Fraction.

The exact class is the owner's fixed typed expression relative to the checked
prefix, within **all** these limits. Equal canonical bytes with a different
typed decomposition remain outside that class. Independent expected traversal
uses no producer proposals or handles. Runtime numerical success remains
downstream of complete retention; this layer issues no search certificate.

The conservative prepaid work tariff is the existing expression-scale tariff:

    128 E_cap + 64 R_cap + 8 A_cap + 8(L + P) + 128 K_entries,

plus the old image preparation component when enabled. Here K_entries counts
current ledger, owner, index, memo and page entries, not just the memo cap.
This is a primitive-work model, not Python allocator time, worst-case hash
table behavior or arbitrary-precision bit time. Actual host/job caps remain
independent. No work permission is inferred from a producer-declared size.

## 4. Unreachable nodes expose a necessary aggregate parser bound

Per-node expansion/reference limits do not bound the total metric work for
one page. A producer may append valid unused capture definitions and retain
an old tiny root. Each capture requires inspecting its operands and logical
input words even if the accepted root never reaches it. The passive cost law
already kept this semantic work G separate; an owned implementation must
actually bound G before doing it.

The necessity control constructs five valid unused captures. Every node has
at most 44 derived references and the selected root has one, below allowance
128. A deliberately unmetered reader performs 215 semantic traversal units.
The actual reader refuses before crossing 128. This is a design/solver bound
control, not an asserted failure of an earlier committed Runtime.

At the start of each page, the reader resets an aggregate semantic meter.
Before materializing capture operands it debits their already derived
unfolded references. After checking their shapes it debits the logical input
and tail count **before** computing rational metrics. Their total must fit
the registered reference allowance. The derived capture reference bound also
includes these logical occurrences. Resource exhaustion retains its
`ResourceExceeded` type; it is not relabeled as a malformed scalar.

Record metadata needs a related precaution: its module, qualified name and
field-name string metrics come from already parsed scalar nodes. Repeated
unused record definitions cannot force repeated scans of a huge old string
merely to recompute its size. New record processing is proportional to its
explicit field references. These checks leave ordinary numerical semantics
unchanged and refuse unsupported work rather than issue a false completion.

## 5. Full original frames remain full original frames

The format adds two internal nodes to the passive value grammar: ordered raw
byte concatenation and a frame containing its eight-byte prefix, typed body
and raw tail. Raw/frame nodes cannot masquerade as ordinary typed children;
frames cannot recursively contain frames as their body. The strict-prefix
and unfolded-reference bounds also apply to raw concatenations, including
zero-byte operands. Expanded byte count alone would not bound those visits.

The owner reads **every actual padding byte**, including nonzero padding,
into bounded immutable packets. Binary composition shares repeated byte
packets without assuming zero padding or retaining temporary packet identities
as source facts. The independent reader derives the exact whole-frame extent
and checks the prefix against the body size. It then expands and compares
**every byte with the original admitted frame**, as before.

Only the existing paid atomic relocation replaces that frame with a root.
The full original frame, mutable/immutable page copies and new root coexist
under their leases before publication. Numerical fresh reads, physical
lineage, primitive checks and learner publication are unchanged. This removes
no actual reference-to-AMP obligation and supplies no actual-device evidence.

The native wire identity `40M + 9N + A + 8E` still holds; the two new tags have
ordinary reference payloads. Workspace/root/copy costs are additional. All
producer/reader indices, parsed Python child IDs, metrics, strongly retained
sources, caller exports, Runtime history and resource metadata remain host
state. A small encoded page is not a whole-host bound.

## 6. Failure and evidence boundaries

Every fallible allocation/binding precedes numerical publication. Page and
memo publication retain their actual prefixes; eviction is allowed by the
complete-page invariant. A partial memo insertion cannot name an absent
definition. Host allocation failures follow the existing terminal guard.
Other retention faults halt the owner. Revealed targets, previous learners,
failed original frames and live generation pins remain under their existing
rules. There is no rollback or hidden retry.

`audit_owned_value_graph_runtime.py` checks typed values, canonical recovery,
small exhaustive histories, paid roles, old snapshots, public substitutions,
memo capacity/eviction, forced CRC collisions, bit variants, aggregate parser
work, raw empty expansions and terminal failures. Twenty paired CPU-tensor
histories cover full numerical bodies, raw reads, profiles, optimizer commits,
frozen reports and arena history, with complete original frames retained.
The original full train/report declaration is also exercised through two
synthetic full-V events; no corpus or score is produced.

Focused evidence is retained in `FP_OWNED_VALUE_GRAPH_RUNTIME_CPU.json` and
`FP_OWNED_VALUE_GRAPH_RUNTIME_FULL_V_CPU.json`. A separate committed-source
regression driver passes all 21 complete relevant scripts at `9fe66f1`, with
inputs unchanged throughout, including actual Windows host-allocation refusal.
`FP_OWNED_VALUE_GRAPH_REGRESSION_CPU.json` is a scoped CPU result, not a replay
or reissuance of the old whole release. The one separately preregistered
[RTX 3090 control](../../experiments/next_token/OWNED_VALUE_GRAPH_CUDA_A1.md)
passes at `e0f8d80`, with production unchanged from `9fe66f1`. It preserves
nineteen phases/6,340 primitive words and all 19,922,944 actual frame bytes
through four training events, two commits and four frozen report events.
Its 46 native records recover 273,034 canonical bytes; 1,148 memo evictions
preserve all 65 pages and exact separate indices. Public/frozen/terminal
boundaries and the single 32-MiB arena remain. The worker exits zero inside
four GiB/180 seconds with source unchanged. This scoped qualification is
closed; the original device journal is terminal and must never be replayed.
The complete ordinary-text host/execution budget remains separate.

The research target stays the trained ordinary next-token comparison. This
joint lowering is the selected candidate; no additional relation/precision
case, representation menu or shorter model score is selected. All historical
cost/device journals remain terminal.
