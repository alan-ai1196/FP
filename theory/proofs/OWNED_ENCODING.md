# Owned source identity and admitted streaming materialization

Status: **exact historical execution counterexample, corrected Runtime,
scoped encoding/extent proofs and CPU allocation measurements.** Foundation
and ERC-1 remain frozen. Runtime is NOT FROZEN and target AMP/science HOLD.
The obligations are [FP_THEORY.md II, VII, VIII, XVIII](../../FP_THEORY.md).

## 1. A source-identity failure before cryptographic hashing

At `532d713`, names were nonempty exact Python strings. Both the one-code-point
string `"\U0001f600"` and the two-code-point string `"\ud83d\ude00"` were legal,
distinct primitive source identities. The registered source/read maps could
assign them different values. Yet `json.dumps(..., ensure_ascii=True)` turned
both into the same escaped surrogate pair. The claimed injective typed tree
encoding was therefore **not injective** on its actual supported data domain.
No SHA-256 collision search is involved: its input bytes were already equal.

The actual endpoint witness registers two mass sources a,b, two unit positive
bases and exact independent input coordinates. Deploy the legal graph
`G_a=(source(a), empty-SUM)` with its two nodes as readout heads. The next
context a=1,b=0 requires probability `(2/3,1/3)`. Construct another legal graph
`G_b=(source(b), empty-SUM)`, with no profile, optimizer step or installation.
The two graphs had identical program IDs and packed code bytes. Construction
overwrote `_programs[program_id]`; the existing deployed learner now evaluated
G_b and returned `(1/2,1/2)`. Its deployed lineage ID never changed.

`scripts/audit_owned_encoding.py` executes the original core hash, machine
and Runtime source from Git. Other unchanged dependencies are shared. The
counterexample uses registered public construction and prediction, with no
private state injection. Thus this is an implementation failure even within
the declared reference scope, not merely an unmeasured host-memory expense.
Renaming sources is harmless only when their causal read/provenance bindings
are transported too; visually similar names cannot identify different reads.

## 2. Preserve strings and check addressed code

Machine `packed-reference-payload-v4` uses typed compact JSON with raw
non-ASCII characters, encoded as UTF-8 with Python's `surrogatepass` policy.
Explicit surrogate code units remain their own three-byte sequences; an
astral character uses its four-byte sequence. No normalization, replacement
or UTF-16 combination is applied. ASCII escapes, including DEL, are retained
so wholly ASCII artifact encodings stay compatible. Non-ASCII bytes and IDs
intentionally change. Python documents the surrogate policy in its
[codec error handlers](https://docs.python.org/3.12/library/codecs.html#error-handlers).

The internal byte format is specifically UTF-8/surrogatepass. For strings
containing explicit surrogates it is not a promise of strict Unicode JSON
interchange. The audit decodes with that registered policy before JSON
parsing, recovering the exact original Python code points. Python's JSON
documentation also distinguishes its supported strings from stricter
interchange expectations in
[character encodings](https://docs.python.org/3.12/library/json.html#character-encodings).

**Encoding proposition.** On the validated native Program data domain, the
pre-hash encoding is injective. UTF-8/surrogatepass code words uniquely decode
to the original code points, and JSON escaping distinguishes literal slashes,
quotes and control characters. Tagged arrays distinguish the native dataclass,
tuple, integer and string coordinates. Their ordered fields decode uniquely.
Induction on this finite data tree recovers the complete Program, including
every repeated edge, tied slot, root and source name. The proof concerns
the fixed registered dataclass constructors; module/qualified names are not
assumed to distinguish arbitrary dynamically substituted Python classes.

A finite cryptographic digest is still not an equality theorem. Before a
constructor can reuse a program address already owned by Runtime, it now
compares the complete validated Program with the stored one. If they differ,
`IdentityUnresolved` yields UNRESOLVED while retaining paid attempt history.
It cannot overwrite the existing code or reject the legal graph as a semantic
impossibility. A later registered address scheme could resolve such a
collision without a new FP architecture primitive. The audit injects a
constant program-address function and verifies this failure boundary.

The corrected ordinary witness constructs both graphs, leaves deployment at
`(2/3,1/3)`, and separately predicts `(1/2,1/2)` for the new candidate.
This is an actual preservation test; current output equality is never used
as a substitute for complete source/program identity.

The existing 35-program ordered native class also executes with these two
source names. It attains exact likelihood 4/9 on the two logged opposite
contexts and issues its scoped current reference maximum proof. With a
forced constant address, syntax still visits all 35 programs but 34 remain
unresolved and no class proof is issued. Exhausting syntax cannot conceal
an unresolved identity comparison.

## 3. Why a paid final buffer did not bound encoding workspace

The same old encoders first expanded every value into a second tree of tagged
Python lists, then created complete JSON text and bytes. `machine.realize`
materialized those bytes before `_allocate` checked capacity. Even program
identity hashing expanded the entire tree, although only a digest was needed.

The resource witness fixes an 8,192-byte packed cap, a 100,000-edge grammar cap,
work cap 10,000,000, zero initializer and the same source/base/range contract.
A legal graph has one source, one SUM, a shared zero slot and m repeated edges,
for m=1,000,10,000,100,000. All its complete-domain predictions are uniform;
it is not rejected because of range. Its direct encoding simply cannot fit
the registered payload budget. Every construction returns UNRESOLVED with
the same recorded packed peak of 1,823 bytes, but the old freshly traced
Python allocation peak grows from roughly 0.75 MB to 62 MB before refusal.

This is an executed obstruction to extending the packed cap into a complete
physical-memory claim. The old Runtime explicitly did not claim that broader
bound. Each expanded edge creates fresh encoding-list structure, establishing
linear workspace growth of that historical implementation independent of the
diagnostic measurement's constants.

## 4. One materialization boundary for all Runtime payloads

`encoding.py` replaces the production tree-expanding encoders. Identity
hashing feeds typed fragments directly to SHA-256. `packed_size(value)`
computes exact output extent without creating escaped text, integer text,
encoded mapping keys or a second value tree. It uses the following recurrences:

- Arrays cost two delimiters, their children's byte sizes and n-1 separators
  when n>0. Dataclass and container tags are ordinary fixed encoded fields.
- Hex integers need `max(1,ceil(bit_length/4))` digits, an optional minus sign
  and two quotes. No big integer is converted to text just to find its size.
- Strings are scanned by code point: two bytes for short JSON escapes, six
  for other C0 controls or DEL, otherwise the exact one-/two-/three-/four-byte
  UTF-8/surrogatepass length, plus quotes. Mapping order cannot change size.

Induction gives the exact size of the registered encoding. No model node,
edge, parameter or metadata field disappears during sizing or writing.

`ReferenceMachineModel.realize` now returns a passive `PlannedObject` with
that extent and its value. It creates no payload or lease. The owning Runtime
rechecks the extent, admits the complete allocation batch against its actual
role/global ledger, creates the exact-size bytearray and writes typed fragments
in place. The writer checks every extent and never resizes the output.
All Runtime requests for packed code/state/proof/trace/profile/search/install
records traverse this same boundary. Raw prepaid context/control storage retains its existing
protocol. The already reserved target slot is filled in place too.

Buffers are now privately owned mutable bytearrays; serialized registered
methods control writes and public snapshots expose byte copies. CPU install
must preserve those same actual objects, not merely their numeric contents.
A planned object, producer encoder or bare byte list cannot authorize an
allocation, prediction, comparison proof or installation through a public port.

An immutable-cap refusal occurs before the writer or output allocation runs.
An admitted partial encoding failure keeps attempted costs/peak and follows
the existing failure/cleanup protocol; it cannot publish the candidate.
No callback, semantic rewrite, early incumbent release or free hidden code
copy is added to make an otherwise impossible build fit.

## 5. Exact checks, measurements and limits

Run `python -B scripts/audit_owned_encoding.py --write`; the compact
[evidence](../../evidence/minimal/FP_OWNED_ENCODING_AUDIT.json) retains:

- The old public source-alias witness and the corrected two-program forecasts,
  plus forced address-collision rejection without overwriting owned code;
  the 35-member Unicode-source class and blocked proof on 34 colliding members.
- 235 independent packed-tree and 240 identity comparisons; 233 structured
  ASCII identity cases, all 128 ASCII code points, all 65,536 single BMP code
  points and 3,072 surrogate-pair/astral boundary classes. These test both
  code-point preservation and exact byte extents, including chunk boundaries.
- Passive-plan/false-size checks, a real capacity refusal with the writer
  disabled, and paid partial materialization failure without candidate publication.
- Three matched old/current allocation measurements under the same manifest.
  The revised traced peak remains about 0.134 MB over this edge range, rather
  than growing to about 62 MB. This removes the expanded-tree/output-copy
  growth; it does **not** put the complete host heap below the 8 KiB payload cap.

The measurements cover new traced Python allocations inside construction,
after producer graphs and bootstrap exist. They exclude preexisting objects,
untraced allocations and tracing metadata. `gc.collect()` precedes each
measured interval, so the measurement also includes replenished interpreter
free lists; it is not a portable constant. See the primary
[tracemalloc API](https://docs.python.org/3.12/library/tracemalloc.html#tracemalloc.get_traced_memory).

General mapping-key sorting, scalar text conversion during actual emission,
dataclass traversal/allocator state, Runtime metadata, arithmetic scratch,
snapshots and failure records still need complete host-resource accounting.
Streaming does not certify CPU time or a liveness-optimal representation.
Foundation/ERC-1 stay frozen and static cases stay parked. Full reference
registration/accounting and gate mapping still precede actual AMP correctness
and then RTX 3090 science; this result cannot authorize a Runtime freeze.
