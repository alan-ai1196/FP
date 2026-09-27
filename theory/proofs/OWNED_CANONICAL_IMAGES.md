# Owned canonical images of immutable subtrees

Status: **IMPLEMENTED; EXACT/CPU CONTROLS PASS; PERFORMANCE NOT YET MEASURED**.
This is a token Runtime serialization refinement under frozen Foundation/ERC.
It changes no G, Gamma, U, physical arithmetic, source interface or numerical
bridge. It is not an additional semantic architecture action or a completeness
certificate. The optional registration is
`SharedReferenceContract(canonical_image_bytes=C)`, with default C=0.

## Binding rule and preservation

The eligible value algebra consists only of exact builtin None, bool, int,
str, bytes, exact Fraction, and exact tuples whose descendants are all eligible.
These values are immutable under their ordinary value APIs and legal Runtime
continuations. As in the existing closed-value model, private reflection into
Python internals is not a legal source/Compiler operation. No list, mapping,
mapping proxy or dataclass is itself eligible, including a frozen dataclass:
its descendants need not be immutable. Mutable outer records are traversed
again on every use. This avoids repeating the false frozen-wrapper premise
exposed by the public-snapshot counterexample.

For an eligible source value v, the owner computes its exact packed extent,
the original bounded walk's aggregate charge, its relative depth and largest
integer bit length. It admits a mutable image buffer before writing with the
original canonical writer. It separately admits immutable bytes before
copying, then compares every copied byte against a fresh original traversal
of v. No earlier cached image or archive-producer hint supplies that initial
comparison. Only afterward may the owner publish the strong binding

    (the actual source object v, paid immutable bytes C(v), extent/guard metrics).

Both copies coexist under compiler and deployment leases until validation and
binding publication finish. The temporary copy is then released. A failed
allocation, writer, comparison or publication cannot authorize a continuation.
New image copies/metadata receive their own prepaid work; the surrounding
bounded traversal is also paid before it executes.

**Preservation theorem.** Suppose an image passes the above binding and its
source/bytes stay immutable. A subsequent lookup requires the same source
object, not equal current predictions, an address without a retained object,
or a digest. That object's current canonical encoding remains C(v). Replacing
its serialization by those bytes therefore preserves its exact packed value.
Induction through the ordinary ordered container/dataclass/mapping writer
preserves the complete record. Mutable wrappers still supply their current
fields. Replacing such a field by a new equal or different object cannot
inherit another object's binding. Strong source retention also excludes
process-address reuse. The identity index is derived; snapshots retain the
source values, buffer identities and guard metrics needed to describe it.

The canonical codec and all type/order/Unicode distinctions remain unchanged.
An incremental UTF-8 decoder with surrogatepass supplies bounded string
fragments from the retained bytes; astral characters and explicit surrogate
pairs stay distinct. Identity hashing and spaced/nonpacked encodings use the
original path. Successful complete canonical bytes agree; fragment/page
boundaries and representation resource costs may differ.

For a cached subtree encountered at depth d, the size guard debits its entire
original aggregate traversal charge, checks d plus its stored relative depth,
and checks its maximum integer width. The subsequent exact extent sum uses
its full canonical byte size. Thus cached traversal has the same accept/refuse
class under the byte, depth and integer limits. Which error is reported first
when several limits fail need not agree. No expanded allowance is inferred
from the smaller cost of looking up a subtree.

## Runtime boundary and resource law

`canonical_images._CanonicalImages` is created by the owned shared-retention
component, not accepted from a caller. Passive encoder helpers have no Runtime
authority. `SharedReferenceSnapshot.canonical_images` exposes immutable
binding records; it is not an issuance interface. Image byte objects appear
in the ordinary paid buffer/resource snapshot, with dependency leases in both
roles. The declared cache cap is part of the Runtime manifest/provenance.

The owner admits maximal eligible subtrees of at least 8,192 encoded bytes
when they fit the remaining image allowance. It descends past ineligible or
oversized wrappers. At capacity it stops adding images and uses ordinary
traversal on misses; it never omits a value. There is no eviction, guessed
equivalence, caller cache hint or promise of optimal placement.

For I accepted images with extents B_i, steady additional reference payload
is exactly sum_i B_i <= C, with I additional immutable physical objects. A
new image of extent B temporarily adds its paid mutable B-byte copy while the
immutable B-byte copy coexists. The source/index/metrics and scalar/decoder
workspace are real Python host costs under the separate host model; this is
not a whole-heap, wall-time or allocator-fit theorem. Per-image work includes
its two original traversals, copies and current ledger metadata. The declared
work tariff remains a conservative primitive allowance, not bit-time.

Native shared allocations and complete token CUDA-frame writers may reuse
these bindings. The archive producer still receives only immutable emitted
byte pieces. The separate decoder still compares the entire expansion against
the owner's expected stream. Complete CUDA sealing still binds the record to
the original frame and retains every actual padding byte. No comparison is
replaced by a checksum or by comparing an unbound producer buffer to itself.

Every fresh predecessor, forecast, primitive-output and final-state read in
the physical executor remains. Images contain already captured immutable
host values, never device arrays, reference endpoints or live numerical
authority. The implementation does not reuse native-gradient bounds. All
unsealed failure rules, learner publication points and terminal MemoryError
handling remain. A cold cache can cost more work/memory and may encounter an
ordinary resource refusal; this optional lowering makes no dominance claim.

## Evidence and limits

`scripts/audit_canonical_images.py` passes 1,800 paired guard decisions,
142,640 uncached canonical bytes across eligible type/Unicode cases, mutable
wrapper changes and seven preserved old snapshots. A cache filled to exactly
8,192 bytes retains complete values on later misses. Both resource-role leases
are checked. Wrong initial image bytes, wrong archive bytes with a warm image,
unpaid image work, post-target ResourceExceeded and terminal MemoryError all
refuse without publishing a new learner; actual targets remain.

A paired complete Runtime comparison uses the original full-V registration
and only the already registered first 1,024 training bytes. It executes the
first two targets with CPU array/device substitution. With the owner nonce
coupled and the same registration, all five phase records/133,079,552 bytes
agree exactly. All 3,073 fresh raw calls and 154,162,696 read bytes agree in
order. The enabled path retains 216 images/65,153,526 bytes under its 64-MiB
image cap. The uncached baseline executes ordinary traversal with no per-atom
cache lookup or admission work; it is not intentionally slowed.

The first test draft incorrectly expected MemoryError to be returned as a
normal result; the existing terminal host guard correctly rethrows it. The
initial paired comparison also left owner nonces independent, so only owner
identities differed. The test now couples those nonces without changing
production behavior or weakening the byte comparison. A capacity test was
tightened to require an actual fully occupied cache, not only oversized misses.

Evidence is `FP_CANONICAL_IMAGES_CPU.json`. Default-path native retention,
17 complete/nonzero-padding frame controls and the original typed/Unicode
writer controls also pass. No Torch or CUDA context is imported by this audit.
These are value-preservation and finite Runtime checks, not a physical
qualification, measured speedup, complete update unit or language result.
Performance must be measured before this is used to justify another long
full-vocabulary run. The existing terminal GPU jobs stay terminal and retain
their original source scopes. Ordinary-text affordability remains the goal.
