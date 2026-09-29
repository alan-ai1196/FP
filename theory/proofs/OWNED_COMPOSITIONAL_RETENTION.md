# Owned byte expressions preserve complete native records and phase frames

Status: **IMPLEMENTED, DEFAULT OFF; COMPLETE CPU QUALIFICATION; FIXED CUDA PAIR REGISTERED**.
The [passive preservation theorem](COMPOSITIONAL_COMPLETE_RETENTION.md) now has
a concrete Runtime realization. Foundation, ERC-1, native learning, source
interfaces, numerical checks and the reference-to-AMP bridge are unchanged.
No `CERTIFIED_COMPLETE` class, installation authority or language score follows.

## 1. Exact registered boundary

The existing `SharedReferenceContract` can select
`complete-canonical-byte-expression-u64-pages-v1` with positive finite
`expression_nodes` and `expression_bindings` allowances. Its existing byte,
reference, comparison and workspace limits remain binding. The default selects
the previous byte archive with both new allowances zero. Inconsistent format/
allowance combinations refuse. The complete contract is retained in the run
manifest; this is a representation choice, not a semantic architecture action.

The Runtime still restricts shared retention to native token ordinary events,
profiles and their existing reporting path. This is not a new policy, search,
fresh-persistence or installation port. The registration cannot authorize a
helper to bypass the complete Runtime.

`byte_terms.py` implements the bounded producer, independent reader and trusted
canonical expression traversal. `compositional_reference.py` owns their use.
Producer and reader have separate dictionaries **and separate limit wrappers**.
A frozen dataclass's writable metadata must not be shared across this boundary.
That isolation is also applied to the passive model. The owner separately
copies its registration, and snapshots copy the diagnostic contract wrapper.

The decision class remains the owner's fixed canonical expression relative
to its retained dictionary. Equal expanded text with another decomposition
is outside that class. Exact literal comparisons decide identity; checksums
only select candidates. Each successful root recovers every original byte.
Only the previously declared immutable scalar/tuple algebra can bind a source.
Dataclasses, mappings, lists and tuples containing them are traversed afresh.

## 2. Full recovery needs its own reference bound

Unique dictionary nodes do not bound recovery occurrences. For example, one
literal and repeated doubling use only four distinct nodes to represent eight
leaf occurrences. Each derived node therefore stores both its exact expanded
byte length and its unfolded literal count. A literal contributes `(bytes, 1)`;
a concatenation adds both child coordinates. These counts are reconstructed
from page bytes, not accepted as producer claims.

Every node must fit the registered expanded-byte and reference limits; the
separate reader repeats those checks. Recovery also checks the caller's byte/
reference allowances before emitting anything. This extends the passive model
to the actual archive's bounded recovery interface. It changes no canonical
byte or numerical tolerance. A resource refusal is not a semantic lower bound.

## 3. Native records and original phase frames

Before any body traversal, the owner pays its work and runs the original
canonical guard, including existing image metrics where registered. It then
constructs the expression through byte messages, admits a mutable page copy,
and separately admits its immutable copy. A reader rebuilt from immutable
page bytes checks the expected expression by a fresh owner traversal. Producer
proposals never supply expected source bindings. Only this independent check
can publish new bindings and a sixteen-byte root.

The CUDA path retains more obligations than the passive body model:

1. The original full frame is admitted before execution and written by the
   existing trusted canonical writer. All numerical checks and fresh reads run.
2. The expression owner checks its eight-byte length and constructs a root
   containing that prefix, the complete canonical record and **every actual
   padding byte**. Padding may be nonzero; it is never assumed or trimmed.
3. The separate reader checks the owner's expression. The owner additionally
   compares its entire expansion with the actual original frame, byte for byte.
4. The original paid atomic relocation publishes the smaller root only while
   the original frame, mutable page, immutable page and root copy coexist under
   their leases. Numerical acceptance and learner publication still occur later.

Consequently the new native path avoids complete expansion during binding,
whereas **full-frame verification still expands and compares every byte**.
This is an intentional remaining cost, not a claim that the passive model has
removed the actual frame obligation. A later change would need its own proof.

## 4. Counterexample: correct bytes can occupy unpaid storage

Integration exposed an existing materialization assumption. The old owner
admitted an output of `builder.extent` bytes, passed a mutable bytearray to the
producer's writer, and copied its result without protecting that extent.
Bytearray mutability includes resizing; a byte-correct result need not have
the admitted length.

The audit loads the original `_materialize` and `_scratch_releases` methods
from canonical `a4089cb`. With the new term format, a writer adds one valid
unreferenced literal and updates the node count. The expected expression and
all its recovered bytes stay correct. Native retention returns successfully
without halting, but the retained page is **208 bytes while charged for 196**.
This is a concrete accounting mismatch, not a Foundation counterexample or a
new semantic action. The old source controls the materialization boundary;
the witness uses the new format, not an asserted historical CUDA trajectory.

The repair holds private buffer exports for all producer-accessible workspaces
and each mutable page copy. Under the existing serialized CPython component
fault model, ordinary bytearray resizing now raises `BufferError` before the
extent changes. The producer never receives the export holder and cannot
release it through its byte/workspace interface. Arbitrary stack/global/native
reflection remains outside this model, as in the existing byte-only theorem.

Page-copy exports remain held through all producer calls, including acceptance.
Successful finalization releases them before releasing the corresponding
scratch leases; failures keep all extant paid buffers. Snapshot diagnostics
list outstanding fixed copy workspaces without exporting mutable authority.
This guard applies to both archive representations. The witness now refuses
before growing the buffer, and exact buffer/residency accounting remains valid.

Independence also requires private allowance metadata: a producer may alter
its own limit wrapper, but cannot thereby change the independent reader's or
owner's limits. Explicit substitution controls check this boundary. None of
these protections treats a frozen Python dataclass as intrinsically immutable.

## 5. Resource and failure law

The implementation deliberately retains the existing four prepaid workspaces,
including the unused old program/reference workspace when expressions are
selected. It claims no unproved credit for removing them. All accepted pages
and these workspaces have both compiler and deployment dependency leases.
Optional canonical images and token base facts retain their previous costs.

For M pages, literal lengths b_i, C concatenation nodes and R live roots, the
successful expression archive's reference payload, excluding unrelated Runtime
objects and optional images/facts, is exactly

    literal_workspace + program_workspace + 65536 + 512
      + 48 M + sum_i (5 + b_i) + 17 C + 16 R.

While finalizing a B-byte page, its additional mutable B-byte copy coexists
with the retained immutable copy. A phase also retains its full original
frame and root copy until relocation. Source bindings, producer/reader indices,
derived counts, private exports and publication copies are additional Python
host state, bounded in count and subject to the actual host/job budget.
The formula is not whole-host memory. No dictionary or strong source reference
is declared free merely because the payload decoder does not need it.

The new prepaid primitive work tariff is

    128 E + 64 R_cap + 8 A_cap + 8(L + P) + 128 K,

with the existing additional image preparation tariff where enabled. E is
the expanded-byte cap, A_cap the exact-comparison cap, L/P the workspaces,
and K the counted current owner/ledger, dictionary, binding and page entries.
It pays traversal, map operations, collisions, copies and publication metadata
before the body is inspected. This is not a worst-case Python hash-table,
bit-time, wall-time or allocator theorem; actual job limits remain independent.

Source binding publication uses only a successful independent expected walk.
Failed parsing, comparison, cap admission, copy, publication or relocation
cannot publish a numerical successor. The actual target, old learner, complete
failed frames and unsealed generation pins retain their original treatment.
Resource exhaustion is honest failure/UNRESOLVED; unexpected evidence faults
halt the archive. Passive snapshot decoding supplies no continuation authority.

## 6. CPU qualification and remaining uncertainty

`scripts/audit_compositional_reference.py` writes the compact
`FP_COMPOSITIONAL_REFERENCE_CPU.json` evidence. It checks exact native retention
with expansion disabled, mutable wrappers, old snapshots, both-role leases,
public contract/binding substitution and private producer-limit substitution.
Sixty-three binary words under forced checksum collisions and 848 bit variants
exercise the exact format. The recovery-occurrence limit is checked separately
from node count. Three full frames retain nonzero padding exactly.

Twenty paired complete CPU-tensor histories preserve **340 phase bodies /
14,148,823 bytes**, 126,797 primitive words, 114,087 raw calls / 2,154,384 raw
bytes, learners, reports, profiles and arena history. Both representations use
the same numerical settings and optional lowerings. Twenty-two post-target
fault controls cover native/frame literals, handles, page copies, expectation,
acceptance, allocation/relocation, unpaid work, binding/reference limits and
attempted output/workspace resizing. Changed actual live tensor words refuse;
unfunded native work cannot inspect its source body.

The old shared-native audit still passes six histories, 526 complete roots /
4,923,198 decoded bytes and six post-target faults. Its original evidence file
is not overwritten. The original frame audit passes seventeen frames /
1,114,248 bytes and all eight failure boundaries after the common relocation
and extent-protection changes; its historical evidence also remains unchanged.

The separate `--full-v` CPU audit uses only the original 1,024 training bytes
and first two targets, with V=50,257 and 603,092 masters. Both actual owners
retain five identical phase bodies / 133,079,440 bytes and 2,619,584 primitive
words. Every original 64-MiB frame, including padding, decodes exactly. At the
qualified registration, the existing archive has 20 pages / 15,414,987 bytes
and reference peak 269,114,036; expressions have 20 pages / 12,275,343 bytes
and reference peak 266,611,908. The latter also retains **265,455 source
bindings and 348,200 terms**. These are real costs absent from a body-only
compression comparison. Whole-host cost and speedup are not established by
these payload counts. The evidence is `FP_COMPOSITIONAL_REFERENCE_FULL_V_CPU.json`.

## 7. One registered device decision

`scripts/run_compositional_reference_cuda_a1.py --run` is committed before
launch. Its exclusive journal is `FP_COMPOSITIONAL_REFERENCE_CUDA_A1.json`;
an existing journal prevents replay. It requires both completed CPU gates,
a clean canonical worktree and two fresh sequential Windows jobs attached
before their first instruction.

Both workers use the same full-V/context512, width4, eight-node, unit512
resource fixture, 603,092 masters and first sixteen original targets. Both
enable generation reuse, 64-MiB canonical images and 4-MiB base facts. Grouped
reads, native composition and historical-workspace retirement are off. The
first worker uses the current byte archive; the second selects expressions
with 2^20 nodes and 2^20 source bindings. All other numerical/resource limits
stay fixed: 240 seconds and 16 GiB host per job, 1-GiB arena/reservation, 2-GiB
reference payload, 64-MiB frames, 2^22 cells, exact-cell cap4096, state allowance
16 and probability allowance 1e-6. Both include the common extent guard.

Initialization and each ordinary prediction/observation are timed separately.
Successful execution requires 33 phases / 4,541,709 words, all sixteen original
pending records and no optimizer commit. Afterwards, an uncached complete phase
must agree with its recovered frame and all padding. A seventeenth original
target is revealed under a corrupted producer literal: independent retention
must refuse and preserve that target, learner/cursor16, failed frame and pins.
Complete current/lifetime device counters and whole-job peaks remain binding.

This one pair will decide whether reduced native expansion outweighs structural
traversal, frame recovery and binding metadata. It supplies no trained text
score or later-unit law. Close this qualification at its original outcome;
do not replay a terminal journal or use it to start a codec/cache sweep.
Ordinary next-token affordability remains the reason for this work.
