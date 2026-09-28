# Exact archive comparisons through bounded byte copies

Status: **CONDITIONAL PRESERVATION LAW; EXACT AND COMPLETE CPU CONTROLS PASS**.
This is an implementation of the same full byte comparisons. It changes no
FP semantics, codec, canonical grammar, image policy, registration option or
certificate class. Foundation/ERC and the rational/relation closure remain.

## Why this is the next ordinary-token question

The terminal current-path CPU diagnosis identifies `_compare_stream` and
`Builder._compare` among the leading self-time routines. Direct extents have
since improved the fixed actual trace, but leave these comparisons unchanged.
The producer compares an unsigned-byte `memoryview` against each candidate
piece; the owner compares independent decoded views against newly generated
expected bytes. A local component probe suggests materializing a bounded
candidate can make exact equality cheaper. That probe does not establish
whole-Runtime or device benefit.

The implementation now copies the producer's candidate immediately after
its original comparison debit, and copies each decoded piece immediately
after the reader yields it. Ordinary `bytes` equality compares the resulting
overlaps. The archive reader, expected traversal, chunk boundaries, comparison
credit, canonical writer and complete padding check remain unchanged.

## Exact class and proof

The claim concerns successful allocations on the existing serialized owner
path, with these actual source premises:

- Every producer candidate is a contiguous one-dimensional unsigned-byte
  view, of length at most `PIECE_LIMIT = 8192`, from an immutable accepted page
  or the builder's private literal workspace. No intervening call can mutate
  that workspace while the candidate is copied and compared.
- Every decoded piece is the same kind of view of an immutable retained
  page. The expected iterator is owned independently and emits immutable bytes.
- Producer and reader retain their separate indices and all original
  validation, candidate order, explicit limits and failure boundaries.

For such a view v and a bytes value b, `bytes(v)` has exactly the ordered
unsigned-byte coordinates of v. Thus `v == b` if and only if `bytes(v) == b`.
Copying an immutable decoded piece before asking for the next expected
fragment cannot change this identity later in the comparison.

At each stream-loop boundary let k be the number of compared bytes. The
two implementations have the same actual and expected iterator positions,
offsets, current expected fragment and k. They choose the same overlap length.
The coordinate identity above preserves the equality decision on that overlap.
On equality, both advance the same offsets and k; on inequality both issue the
same refusal before another iterator read. Empty chunks, final size checks
and exhaustion of the expected stream are unchanged. Induction proves the
same return/refusal and the same iterator-read trace. In particular, success
still requires equality of the complete concatenated streams and the declared
extent, independently of their partitions.

The producer's ordered candidate comparisons therefore make the same exact
interning decisions and consume the same comparison credit. It receives the
same original byte pieces, so its literal table, ordered references and
compressed page bytes remain identical. The separate reader still checks
every decoded byte against the owner's expectation. No checksum or copied
producer input replaces that expectation.

Two exclusions matter. `memoryview(b'\xff').cast('b')` compares signed -1
against 255 and is unequal to `b'\xff'`, whereas copying its raw byte is equal.
Also, an expected iterator could mutate a hypothetical mutable actual view
before comparison; copying before that mutation changes the answer. Both
are concrete counterexamples to an unrestricted conversion law. Neither is
produced by the closed archive reader or the serialized producer call sites.
This is not a new rule permitting cached reads of live physical arrays.

## Work, storage and failures

For one retained page, let D be its decoded extent and C the total length of
candidate comparisons actually charged by the producer. Producer copies add
at most C copied bytes; decoder-piece copies add D, and copied actual overlap
slices add at most another D. Expected slices already existed. Thus additional
byte movement is bounded by `C + 2D`. The registered allowances still give
`C <= comparison_cap` and `D <= expanded_cap`. Existing prepaid copy/compare
terms cover these passes: `4*comparison_cap + 32*expanded_cap` remain unchanged.
This does not reduce any abstract work charge or prove a wall-time speedup.

No new retained object or whole-record materialization is introduced. Within
these two functions the additional live copied payload is at most two pieces,
`2*PIECE_LIMIT = 16384` bytes; the producer and reader stages do not overlap.
This is a local payload bound, not a whole-Python-heap theorem. Existing
library/object overhead and actual host-job limits remain separate obligations.

The producer checks its comparison credit before making its copy. Any new
copy allocation may still fail earlier than the old implementation. Such a
MemoryError passes through the existing terminal host boundary; it is not a
successful equality result. No resource-dominance theorem is claimed. Actual
targets, old learners, workspaces, created pages and unsealed physical pins
must retain their original ownership on post-target failure.

## Controls and fixed device comparison

`scripts/audit_byte_comparisons.py` loads only the two predecessor comparison
functions from canonical commit `d37f939`. It compares all single-byte values,
comparison-credit decisions, all partitions of binary streams through length
four, exact early-refusal iterator traces, forced collisions, malformed/future
references and reconstructed old pages. Complete paired CPU-tensor Runtime
histories compare every phase body, actual archive page, learner, report,
fresh read and arena allocation/retirement count. Separate controls inject
MemoryError at each new copy in both native retention and CUDA-frame retention,
and preserve the existing work, output-corruption and relocation failures.

The audit passes 131,090 candidate decisions and 70,246 partition decisions
over 171 binary-stream variants, including identical early iterator-read
traces. Nine forced-collision pages and 44 ordered candidate comparisons are
identical. Six paired Runtime histories preserve all 129 phase bodies/
5,774,243 bytes, 50,279 checked primitive words, 45,619 raw calls/856,212 raw
bytes and 441 actual archive pages/5,457,081 page bytes. Learners, reports,
full frames and arena counts also agree. Four post-target copy MemoryErrors,
six native retention faults and eight complete-frame failure boundaries pass;
17 full synthetic frames retain every byte, including nonzero padding.
Compact counts are in `FP_BYTE_COMPARISONS_CPU.json`.

`scripts/run_byte_comparisons_cuda_a1.py` registers two fresh workers, old/copied byte
comparisons only, with the same full-V/unit512 fixture, first 16 training
targets, qualified images/base facts, region reuse and all original numerical
checks. Each original job has 240 seconds and 16 GiB; all existing 1-GiB arena,
2-GiB reference-payload, 64-MiB frame and numerical limits remain. Initialization
is separate; no inner profiler runs. After timing, the last retained phase
must equal its independently generated uncached body and complete padding.
A seventeenth original target is then observed under a deliberately corrupted
frame producer: independent comparison must refuse, retain the actual target
and old learner, and leave the Runtime terminal with its unsealed pins owned.

Commit code, evidence and registration before first launch. The exclusive
`FP_BYTE_COMPARISONS_CUDA_A1.json` must retain the first original outcome and
must never be replayed or given a raised cap. One ordered pair can establish
only its finite correctness and timing observation. Close that qualification
at its result; no comparison-variant sweep, full-unit replay or useful language
training budget follows without further evidence.
