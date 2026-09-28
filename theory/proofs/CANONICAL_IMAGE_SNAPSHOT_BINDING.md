# A decoded-byte comparison cannot protect a shared writable expected binding

Status: **COUNTEREXAMPLE REPRODUCED; SNAPSHOT ISOLATION REPAIRED; COMPLETE CPU PASS**.
This is an implementation mismatch under the existing ownership principle,
not a Foundation R4 counterexample or a new semantic architecture action.

## The missing premise

An owned canonical image binds an actual immutable source v to paid bytes
C(v). The archive producer emits a candidate page, an independent reader
decodes it, and the owner compares that expansion with its expected encoding.
All those mechanisms can be correct while their composition is unsound if
the source-to-bytes binding itself is writable through an exported snapshot.

Let the producer and comparison both consult a binding B. Initially B(v)=C(v).
An external write changes it to B'(v)=C(w), where C(v) != C(w), without changing
either immutable source or either immutable buffer. The independent reader
can correctly decode C(w), and the comparison correctly finds C(w)=B'(v).
Neither proves that the retained page contains C(v). Independent decoding
does not establish the integrity of a shared expected-value binding.

The old `_CanonicalImages.snapshot` returned `tuple(self.entries)`. Each
`Image` was a frozen dataclass with a writable dictionary, shared with the
private identity index. A caller could keep its source identity and replace
the returned `buffer`, `size` and guard metadata with those of another image.
All fields needed for this attack were already in the public snapshot.

This audit mutates returned diagnostic metadata. It does not mutate private
Runtime fields, trusted functions, source scalar internals or paid buffer
contents. It follows the project's existing public-snapshot substitution
controls. It does not claim protection against arbitrary reflection into the
whole Python process. In particular, the old theorem's closed immutable source
assumption is not weakened; the missing isolation is in the exported binding.

## Concrete counterexample

`scripts/audit_canonical_image_snapshots.py` loads the old snapshot method
from canonical source `075eba1da7493582665b8801a61430ac02876be6`.

First, it retains two different 8,192-byte source values A and B as paid images.
Their packed extents are both 16,400 bytes. Updating A's returned binding to
B's buffer leaves the private lookup's source identity check satisfied. The
next complete shared retention of A succeeds without halting, but its exact
independent expansion equals C(B), not C(A).

The second witness uses the complete full-V Runtime with CPU device/array
substitution, owned images and base facts. After initialization, it changes
only the returned embedding-image binding to the output-master image metadata.
The public `predict_next` call returns `PREDICTED_REFERENCE`; both phases are
`CHECKED_CUDA_PREFIX_PHASE`, and the actual original master words are unchanged.
Nevertheless, its retained frame contains 31,723,068 canonical bytes while
an uncached encoding of the actual phase has 26,898,492. The first difference
is at byte 1,630,445. The owner and its independent reader agreed on the wrong
expected stream. This is a false complete-retention result, not an issued
`CERTIFIED_COMPLETE` theorem or evidence of a numerical prediction error.

Only the previously declared first 1,024 training bytes are opened; no new
split or CUDA context is used. The original finite, unattacked device results
remain observations of their original trajectories. They did not test this
exported-binding mutation and cannot establish its safety.

## Repair and preserved boundary

Each returned image entry is now a fresh diagnostic `Image` wrapper. It copies
all six fields while retaining the identity of the already eligible immutable
source and immutable scalar metadata. The private identity index keeps its
own wrapper. No public field replacement, including replacement of every
binding field, changes the private binding or a later fresh snapshot.

There is no new cache, encoding, image-admission policy, ownership role or
continuation port. Source-to-buffer verification, guard metrics, independent
decoding and every live numerical check remain. Snapshot construction costs
O(I) wrappers for I images, under the existing actual host boundary; it is
not a new persistent reference buffer or a reduced payload charge. A snapshot
allocation failure still escapes through the terminal host guard, retaining
the prior learner and private bindings without continuation authority.

The complete repaired public-prediction control retains exactly 26,898,492
bytes equal to the uncached actual phase after the same attempted substitution.
The small artifact control again retains C(A). All-field replacement and
snapshot MemoryError controls pass. The audit also passes using the prior
committed extent calculator, so the counterexample and repair do not depend
on the separate extent optimization under development.

The compact evidence is `FP_CANONICAL_IMAGE_SNAPSHOT_CPU.json`. This proves
the finite CPU reproduction and repair, not a universal Python isolation or
new actual-device qualification. Carry the corrected boundary into the next
justified device execution; do not replay an old terminal journal. The relevant
general rule is to preserve the source-to-evidence binding itself, including
its public alias boundary, in addition to preserving both endpoint values.
