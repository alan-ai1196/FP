# Source-compiled canonical stream execution

Status (2026-10-02): **conditional preservation and finite CPU/full-V controls
pass; modest measured cost gain; candidate parked without production/device authority**.

The closed [native cost diagnostic](../../experiments/next_token/NATIVE_TEXT_COST_A1.md)
puts 91.36134% of four profiled early-prefix calls inside complete reference
retention. The candidate compiles the existing serializer and its two stream
consumers. It changes neither the grammar nor the archive, and introduces no
new persistent cache, numerical operator, search action or certificate class.
This is a bounded attempt to make the ordinary-text experiment affordable.

## 1. The preservation obligation is a trace, not just a final byte string

For a canonical traversal, retain the ordered field/mapping/image observations,
each emitted fragment and the terminal return or refusal. A caller may mutate
an exposed value between yields; a fragment boundary also affects how
`_packed_parts` coalesces bytes. Equality of concatenated bytes alone therefore
does not establish equivalent retained pages, allocation debits or refusal order.
The relevant component relation preserves observations and yields at every
continuation, for the closed supported value interface and fixed trusted code.

**Conditional claim.** Suppose a replacement `fragments` preserves this trace,
including exceptions, and replacements of `_packed_parts` and `_compare_stream`
preserve their iterator-read/output/refusal traces. With the same input value,
owned images, workspace and archive predecessor, a successful original and
replacement retention step produce identical page bytes, roots and resource
events, up to independently chosen Runtime identities.

Proof: by induction on serializer yields, the coalescer receives the same byte
fragment in the same state. Its staging writes, flushes and large-piece splits
agree. The unchanged producer consequently receives the same pieces and takes
the same exact interning, compression and quota decisions. The unchanged extent
and guard walks precede this work in both executions. Independent reader output
and fresh expected traversal agree at each comparison step, so acceptance and
all ledger/page/root publications agree. Induction over successful Runtime
transitions then preserves complete state, including pending targets and old
learners. No numerical relation, fresh evidence, search or install authority is
created by this argument.

This is not a theorem that Cython preserves arbitrary Python. Introspection of
generator frames, replacement of trusted code, process-memory attacks and
wall-clock observations are outside the stated component relation. Compilation
can change host allocation size/order and thus which transition reaches a cap.
We do not claim equal MemoryError timing or equal host peaks. The actual host
cap and terminal failure protocol still apply to the realized path; an earlier
failure must preserve its actual revealed/published prefix, not fabricate the
unexecuted original continuation.

## 2. One authored algorithm, an explicit executable artifact

[`build_native_streams.py`](../../scripts/build_native_streams.py) compiles the
canonical `encoding.py` unchanged. It extracts the exact AST source segments of
`_packed_parts` and `_compare_stream` from `shared_reference.py`, adding only
their imports, and compiles these into a second module. There is no hand-written
second codec. The control binds only these three functions; Python guard/extent
walks, the byte-only producer interface, independent decoder, ownership ledger,
numerical code and public boundary stay in place.

The build uses Cython 3.1.8, CPython 3.12.9 x64 and MSVC 14.51.36231. Type inference
and annotation typing are disabled; overflow, bounds, wraparound, initialization
and None checks are enabled. These choices avoid requesting unsafe unboxed
integer shortcuts, but are not a universal compiler correctness proof. See the
[official Cython directives](https://cython.readthedocs.io/en/3.1.x/src/userguide/source_files_and_compilation.html#compiler-directives).

Source and native-artifact digests bind the particular executable being tested.
Generated C, binaries and build tools remain under ignored `build/`; the small
manifest is retained in the CPU evidence. The explicit audit context installs
the functions before root construction and restores imported aliases afterward.
It is not a production selector and is never switched during a live trajectory.
The compiler's temporary heap and native module heap remain physical host cost.

## 3. Finite executable evidence

[`audit_native_streams.py`](../../scripts/audit_native_streams.py) and its
[minimal receipt](../../evidence/minimal/FP_NATIVE_STREAM_COMPONENTS_CPU.json)
establish the following finite checks:

- 2,184 typed/mode cases, 15,852 exact fragments, all 65,536 BMP code points and
  3,072 surrogate-pair classes; cyclic/foreign/nonfinite and packed float/Enum
  refusals preserve fragment prefixes and error messages.
- Sixteen yield-by-yield field, mapping, image and interleaved-mutation traces.
- 326 identical producer pieces/140,151 bytes across three staging capacities;
  5,870 partition/corruption/iterator-read decisions, including all binary words
  of length at most four, empty pieces, changed sizes and trailing bytes.
- Sixteen paired four-target/two-commit/three-report histories: complete
  snapshots and 1,120 decoded records/7,168,198 bytes agree. Only these isolated
  CPU controls fix root nonces to compare all identity-bearing bytes.
- Six paired CPU tensor-owner histories: 129 complete phase bodies/5,774,243
  bytes/50,279 primitive words, with equal frames, learners, reports, raw reads,
  allocations and retirements. This is no actual CUDA execution.
- Six post-target storage failures and five image/failure controls retain the
  target and prior learner, with terminal refusal and no partial publication.

These controls support the trace premise on the enumerated cases; they do not
prove all Python behavior or a speedup. A full-V cost control must separately
validate cached images against an uncompiled, uncached source traversal, then
all retained pages against the independent uncompiled expected traversal. That
avoids using the same compiled error on both sides as the sole acceptance test.

## 4. Cost result and stopping point

The [original bounded pair](../../experiments/next_token/NATIVE_STREAM_COST_A1.md)
at `426a13d` passes both workers. Each independently validates 41 uncached images/
45,954,147 bytes and 85 complete records/890,797,166 bytes. Ordinary sixteen-target
time falls from 15.3455167 to 12.7106703 seconds (17.17014%); peak job commitment
rises from 551,292,928 to 553,775,104 bytes. Paid resource counters agree exactly.
No profiler runs inside the ordinary calls. The journal is terminal.

This modest gain does not establish an affordable trained trajectory, commit
cost or later-history scaling. Park the candidate as a scoped CPU control,
without a production selector, compiler-flag sweep or device qualification.
The growing-history transition cost is the next concrete question. Foundation/
ERC and the relation/precision closure remain; no smaller-prefix model score
replaces the ordinary-text objective.
