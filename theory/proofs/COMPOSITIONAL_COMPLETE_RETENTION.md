# Complete retention can be checked without repeatedly expanding old bytes

Status: **CONDITIONAL PRESERVATION THEOREM; EXACT MODEL AND FULL-V CPU RECORD AUDITS PASS**.
This is a passive research model, not an installed ReferenceCompilerRuntime
encoding, a numerical bridge, a resource certificate or a new Foundation
action. The default production path remains the qualified byte archive.
Foundation/ERC and the rational/relation branch stay closed.

The subsequent [owned realization](OWNED_COMPOSITIONAL_RETENTION.md) adds a
default-off Runtime path and complete CPU gates. It also adds an explicit
unfolded-reference cap and isolates producer/reader limit wrappers. Its actual
full-frame checks and host-state costs are additional to this passive model;
the model's result alone remains insufficient for Runtime or GPU authority.

## 1. The question left by the ordinary-token experiments

The latest fixed actual comparison takes 44.22213 seconds for sixteen ordinary
targets, despite faster exact comparisons. The current archive already shares
literal bytes and compresses its reference sequences. Its independent binding
check nevertheless expands each complete stream and compares it with another
complete expected stream. Storage sharing alone does not remove that work.

The question is whether complete recoverability requires all old immutable
bytes to pass through the checker again. It does not, under an explicit stable
source binding and a fixed compositional expression grammar. The construction
below retains every byte and checks newly composed structure. It changes the
representation of evidence, not which numerical facts require fresh checking.

This is a narrower decision problem than arbitrary compressed-string equality.
It also leaves complete source guards and mutable-field traversal in place.

## 2. Terms, pages and the exact decision class

A term is either a nonempty immutable literal of at most 8,192 bytes, or an
ordered concatenation of two strictly earlier terms. The parser derives every
term's expanded length. Its dictionary rejects duplicate literal definitions
and duplicate child-ID pairs. CRC32 only selects literal candidates; complete
byte equality decides identity. Each comparison is debited before it occurs.

An immutable page records its ordinal, the first new node, the number of new
nodes, its root and the root's expanded length. All coordinates are uint64.
The reader reconstructs its own index from these page bytes; it never copies
the producer index. Forward references, cycles, duplicate definitions, empty
literals, truncated or trailing data, and inconsistent extents refuse. The
complete ordered page prefix remains necessary for recovery.

The trusted owner builds a fixed expression for the existing typed packed
encoding. Each scalar uses the old canonical fragments, UTF-8/surrogatepass
and bounded literal splitting. Container syntax and recursively constructed
child expressions are joined using a fixed binary-carry tree. Dataclass field
order, type names, mapping order and every Unicode distinction are inherited
from the current canonical encoder. No new value equivalence is introduced.

**Exact decision class:** a page whose root is the owner's fixed expression
for the current complete value, relative to the verified retained prefix and
source bindings, within all declared limits. Literal definition order and
unreachable valid nodes may differ. Root IDs are meaningful only inside the
same dictionary prefix. This class does not include every term with the same
expanded bytes. For example,

    concat(literal("ab"), literal("c"))
    concat(literal("a"), literal("bc"))

expand identically but have different structural roots. Rejecting the latter
when the former is expected is an intentional class restriction, not proof
that the strings differ. No `CERTIFIED_COMPLETE` search result is issued.

## 3. Source stability and independent binding

Use the existing [byte-only producer fault model](BYTE_ONLY_PHASE_EVIDENCE.md).
The serialized owner and canonical traversal are trusted. A producer can alter
its own state, byte packets and returned data; it cannot inspect owner stacks,
mutate checker globals, interleave another Runtime event or write arbitrary
process memory. This is not Python isolation against unrestricted reflection.

The producer receives only literal byte packets or serialized child IDs. It
receives no source object, iterator, phase, tensor, frame or owner handle.
Therefore this proposal does not reintroduce the old record-taking compressor's
ability to change its own expected execution record.

Only the exact closed value algebra used by
[owned canonical images](OWNED_CANONICAL_IMAGES.md) can acquire persistent
source bindings: None, bool, int, Fraction, str, bytes and recursively pure
exact tuples. Immutability is relative to their ordinary value APIs and legal
continuations; private mutation of Fraction internals is outside that premise.
Dataclasses, including frozen dataclasses, mappings and lists are always
rewalked. A tuple containing one of these wrappers is also ineligible. Thus a
shared program `Term` is reread even when its current fields are scalar.

After the producer emits a page, the owner parses it into the separate reader
index. A second owner traversal finds expected literal and concatenation IDs
in that index. This traversal may use previously verified source bindings,
but receives neither the producer's proposals nor its returned intermediate
IDs. The final root and expanded extent must agree. Only then are the second
traversal's new source bindings published. Strong source references prevent
address reuse from substituting another value.

Snapshots return immutable pages, root IDs and builtin `(source, root)` tuples.
They expose no mutable index or entry wrapper. This preserves the binding
isolation missing in the earlier
[public snapshot counterexample](CANONICAL_IMAGE_SNAPSHOT_BINDING.md).

## 4. Preservation theorem

Assume the preceding source/checker boundary, sufficient declared allowances
and successful allocations,
and an initially correct retained prefix and source-binding table. If one
retention succeeds, its accepted root expands to the entire current canonical
encoding, every previous root still expands to its original bytes, and every
new source binding is correct for all legal immutable-source continuations.

**Proof.** Induction over the node order gives finite expansion and exact
lengths, because every concatenation references the strict prefix. It also
gives uniqueness of an ID for each structural term: literal candidates use
exact equality and duplicate literals refuse; equal concatenation terms have
equal child IDs by induction, and duplicate pairs refuse. This is structural
injectivity, not injectivity of expanded strings.

Next induct over the owner's value construction. Scalar fragments concatenate
to the original scalar encoding. Container syntax and children concatenate in
the original canonical order. A previously verified binding substitutes the
same expression of the same immutable source. All other fields are observed
afresh. Consequently the expected traversal constructs the canonical expression
of the complete current value.

The independent reader lookup finds precisely that expression if present.
Equality of its root with the supplied root proves equality of structural
terms and hence of all expanded bytes. The expanded-length check rules out an
inconsistent advertised extent. New bindings come from this traversal, not
from a producer assertion. Accepted prefix nodes and their bytes never change,
so prior roots remain valid. This preserves the invariant for the next page.

The ordinary producer is also complete for this **fixed expression class**
conditional on its source guards, byte/node/comparison allowances and actual
allocations succeeding: it emits each missing literal/pair in dependency order,
so the separate expected traversal finds every required term. Resource refusal
does not establish a semantic impossibility or a broader negative certificate.

The passive owner stages its accepted roots, bindings and statistics before
one publication. Failure before it preserves prior accepted roots/bindings
and forbids continuation; partial producer/reader state is diagnostic only.
This model has no target, learner or resource ledger. It does not establish
the complete Runtime's post-target failure and ownership obligations.

## 5. Resource laws and their limits

For M retained pages, L distinct literals with lengths b_i, and C distinct
concatenation nodes, the serialized payload is exactly

    P = 48 M + sum_i (5 + b_i) + 17 C.

The header contains each root; all dictionary definitions are inside P.
This is an encoded-payload identity. The Python model additionally retains
producer and reader indices, literal copies, source bindings, source objects,
temporary packets and publication copies. P is not resident host memory or
a ResourceLedger charge. No object is made free by calling an index derived.

For a root of expanded length D, nonempty literals imply at most D unfolded
leaf occurrences. The expanded binary tree has one fewer internal occurrence
than leaves. Cold recovery therefore visits at most 2D-1 node occurrences and
emits exactly D bytes. A nonempty literal's upper size bound is not sufficient
alone: permitting an empty literal and twelve repeated doublings gives 8,191
unfolded visits for zero bytes. The format explicitly excludes that case.

For an expected traversal, record the following separately:

- G: the unchanged original aggregate guard/extent work;
- V: visited source values, including fresh mutable wrappers;
- Q: literal bytes emitted by the expected traversal;
- J: concatenation lookups;
- A: exact candidate-comparison bytes, including hash collisions;
- S and M: existing source bindings and roots copied during publication.

There is no D-byte expansion inside this binding check. Its explicit work is
the original G, V source visits, Q bytes emitted, J pair lookups and the charged
literal comparisons, plus parsing new nodes and copying publication metadata.
Dictionary operations and allocation costs remain real costs. The current
Python hash tables imply no worst-case constant-time map theorem; neither
this count nor P establishes bit-time, wall-time or whole-host dominance.
In particular, copying S bindings/M roots and traversing mutable wrappers can
still grow with history. The model does not remove the old guard walk.

For a repeated immutable B-byte body in M changing bounded shells, the body
is emitted on first binding and subsequently represented by its bound root.
Its contribution to repeated expected-literal emission is B, rather than MB.
The source guard, changing shell terms, lookups, collision comparisons and
publication work are additional. This constructive separation refutes only
the claim that complete recoverability *itself* requires re-expanding every
old immutable byte at each check. It supplies no lower bound on arbitrary FP
implementations, and does not weaken any fresh device-word observation.

## 6. Exact evidence and a strong existing baseline

`theory/numerical_checks/compositional_retention_audit.py` records
`FP_COMPOSITIONAL_RETENTION_MODEL.json`. All 106 typed values/259,106 canonical
bytes agree, including all BMP codepoints, surrogate/astral distinctions and
large exact integers/Fractions. Three old snapshots rebuild solely from pages.
Binding runs with expansion disabled. Five wrapper/descendant changes rewalk;
old roots remain unchanged. Producer substitutions and allocation failures,
including independent expectation and publication failures, preserve old
accepted state and halt the passive owner. Forced CRC collisions remain exact.
All 2,400 single-bit variants and 300 truncations of the fixed attack page
refuse. Explicit malformed limits, references and extents also refuse.

The 33-record repeated-body fixture has 69,220,376 complete canonical bytes
and 9,881 model page bytes. After the first root, the expected traversal emits
3,744 literal bytes and performs 1,920 pair lookups. Every root is separately
fully expanded and compared as an audit oracle.

The baseline is the **current complete shared-reference owner**, including
exact byte comparisons, independent decoding, resource ownership and a
prewarmed image of the entire stable body. This gives favorable image placement
instead of exhausting its cache on changing parent tuples. It retains 11,313
record-page bytes and compares all 69,220,376 expanded bytes; its warm image
occupies 2,097,168 bytes. Warmup pages are excluded from that page count.
The body is deliberately periodic and highly compressible. These small page
totals demonstrate that the existing archive already compresses well; they
are not a general compression, memory or timing win. The new distinction is
the work needed to bind repeated complete records.

## 7. Five actual ordinary-token records, without replacing their owner

`scripts/audit_compositional_phase_records.py` runs the existing complete
Runtime with actual Torch CPU tensor storage substitution: V=50,257,
603,092 masters, reuse enabled, 64-MiB canonical images and 4-MiB base facts.
It reads only the already registered first 1,024 training bytes and consumes
the first two original targets. It opens no CUDA context or new data split.

All five original phases and their complete 64-MiB frames, including actual
padding, pass before the passive model consumes the finished phase records.
The model stores **phase bodies only**; their padding still belongs to those
original frames. The following are exact counts, not a substitute frame claim:

| Phase | Complete canonical bytes | Model page bytes | Expected literal bytes | Expected pair lookups |
| --- | ---: | ---: | ---: | ---: |
| Initialize | 50,502,570 | 6,305,384 | 47,588,928 | 304,376 |
| Predict 0 | 26,898,471 | 119,706 | 1,151,687 | 219,292 |
| Observe 0 | 14,347,356 | 93,753 | 1,246,453 | 117,721 |
| Predict 1 | 26,946,967 | 35,194 | 1,154,839 | 220,173 |
| Observe 1 | 14,384,076 | 92,643 | 1,250,427 | 118,561 |

All 133,079,440 canonical bytes recover exactly, including after a fresh
page-only reader rebuild. The model has 14,187 literal nodes, 33,265 pairs,
9,446 source bindings and 6,646,680 page bytes. Binding again runs with expansion
disabled. The four ordinary records emit 4,803,406 expected literal bytes for
82,576,870 complete bytes, while still making 675,747 pair lookups. Thus the
large byte reduction coexists with substantial mutable-structure work.
`FP_COMPOSITIONAL_FULL_V_RECORDS.json` retains the compact evidence.

## 8. Closure and next decision

The passive research question is closed at this scoped preservation result.
Do not deepen it into a general compressed-string theorem or another codec/
cache sweep. It is relevant because it attacks the measured ordinary-token
retention cost; it is not a reason to reopen relation tasks or static resource
special cases.

The next concrete gate is a complete owned Runtime realization of this one
candidate, with its actual resource costs. Native allocations and CUDA phase
frames both require independent binding, prepaid copies/index metadata,
dependency leases in both roles, snapshot isolation, complete failure pins
and original-target retention. The original full-frame writer/actual-padding
checks cannot simply be removed on the authority of this body-only model.
Every fresh numerical read and reference-to-AMP check remains mandatory.

Only after that gate passes should one newly registered bounded device test
decide whether the saved expansion outweighs structural/ownership work. No
existing terminal journal may be replayed. No affordable full-unit budget or
language-quality result follows yet. The objective remains ordinary next-token
learning against the already selected strong trained baselines.
