# Complete CUDA evidence with one retained immutable payload

Status: **IMPLEMENTED; EXACT, BOUNDED HOST AND CUDA AUDITS PASS**.
Two earlier host report failures remain retained as described below.
Foundation R4, ERC-1, numerical semantics and the running
`8ccacc0` likelihood matrix are unchanged.

## 1. The cost is copying, not missing information

At `b0c409c`, each CUDA phase owns a fixed-size bytearray. Its first eight
bytes encode the used length; the remaining extent contains the complete
typed phase record and padding. The complete Runtime snapshot converts every
bytearray to bytes on every call. A completed frame has no subsequent writer,
but its mutable representation causes repeated copies of the whole history.
For the 748-phase n8 case with four-MiB frames, one full copy of the frame
history alone is 3,137,339,392 bytes. This arithmetic identifies a cost; it
does not attribute the whole model worker's observed peak to that cost.

The change retains the entire extent as immutable bytes immediately after
the final successful write. It keeps every record field, native intermediate,
gradient, padding byte, frame label and reference/AMP relation. There is no
compression, truncation, history quotient, smaller reservation or new model
action. The existing snapshot implementation is unchanged.

## 2. Preservation argument and its domain

The registered Runtime API is serialized. Its public snapshots contain bytes
already; they expose explicit object labels and values, not mutable frame
handles. Python object addresses and `is` comparisons across snapshots are
not an information interface or a resource certificate. Trusted private
implementations are not an adversarial Python sandbox.

In `_cuda_execute`, the only frame writer finishes before finalization. Its
captured `frame` variable is then set to None, so neither the outer local nor
the writer closure can retain a mutable alias through a later traceback.
The CUDA executor receives the separate owned raw-readout workspace, never
the evidence frame. Finalization requires an exact bytearray, a complete
matching extent, the Runtime provenance, the evidence-frame kind and exactly
one data-owner lease. Other mutable buffers, including ingress, stay mutable.

For an F-byte exact bytearray b, `bytes(b)` has exactly the same F byte values.
After the final writer, every registered future observation of this frame
therefore returns the same explicit label, length and byte sequence. Future
CUDA phases use new labels and do not write this frame. Induction over the
registered continuation preserves all frame observations, while all other
semantic and numerical state is carried through unchanged. Learner buffers
are not replaced; installation's learner-object and native-storage identity
checks still apply.

This is a value-preservation argument, not equality of complete resource
histories: the new copy and transaction have real paid costs. Conclusions
about a continuation remain conditional on its resource gates succeeding.
No current-output equivalence substitutes for retained causal information.

## 3. Own both copies, then publish once

Before conversion, Runtime charges F bytes of copy work plus a conservative
64-times-entry allowance for its detached ledger and root preparation. The
entry envelope uses live objects, possible owner references, owners, resource
events, retired IDs and root/buffer entries. These are abstract primitive
charges, not a bit-time or total Python-heap theorem.

It next reserves one additional F-byte physical extent and only then creates
the immutable copy. Until publication the old frame label owns the original
bytearray and the temporary label owns the new bytes. The existing detached
ledger transaction prepares retirement of the temporary extent. A prepared
root puts the immutable payload under the unchanged evidence-frame label,
with updated resource routers. One root assignment publishes the relocation
and releases the original mutable storage. No local holds that old storage.
This is an internal packed-buffer relocation with equal contents, not a
replacement of an installed learner's physical identity.

Work or coexistence refusal occurs before copying. A failure after the copy
but before publication leaves both distinct actual buffers in the live root,
with both leases. No finally block releases either on that failure. A builtin
allocation MemoryError follows the existing terminal host-failure rule; its
partially materialized diagnostic prefix has no continuation authority.
The CUDA phase is accepted only after final retention succeeds. Existing
unexpected-executor-error priority over secondary retention failure remains.
Successfully retained failed-execution records may also become immutable;
failed final writes retain their original mutable diagnostic frame.

## 4. Exact payload law, not a whole-process bound

Let N successfully finalized frames have lengths F_i. Suppose S simultaneous
complete snapshots observe those completed frames. Under the former mutable
representation, these frame payloads occupy

`(S + 1) * sum_i F_i`

distinct live payload bytes. With immutable completed frames they occupy

`sum_i F_i`.

During finalization of a new F-byte frame, its original and copy coexist,
adding one F-byte temporary extent beyond the retained frame history. For
equal F and two simultaneous snapshots, the completed-frame payload drops
from 3NF to NF. Previously exposed failed mutable frames and their snapshots
are outside this completed-frame sublaw. All unrelated metadata, tensor
arenas, allocators, external observations and other buffers remain costs.

The detached ledger copy can add CPU and metadata costs. This result proves
neither whole-process peak nor wall-time improvement, n16 recovery, optimal
representation, or broader class completeness. Tight caps can now refuse the
extra temporary extent or work; the outcome is UNRESOLVED.

## 5. Audits and fixed bounded comparison

Run `python -B scripts/audit_cuda_frame_storage.py --write` for exact checks.
The initial audit compares all 17,904 bytes of 33 frames, includes every byte
value and nonzero padding, checks old snapshots after another frame, refuses
work and residency before copy, and retains both real buffers after expected
and unexpected failures in release preparation and router preparation.

The bounded host fixture fixes 128 one-MiB frames, two simultaneous complete
snapshots, a 512-MiB job commit cap and a 60-second deadline per representation.
It compares every frame byte, uses the actual Runtime snapshot method and
checks its AST and constructor against `b0c409c`. The legacy fixture retains
the actual former mutable representation. It is a synthetic storage fixture,
not a replayed model or an intentionally weakened baseline.

The separately bounded actual CUDA fixtures use the existing simplex profile
and n3 likelihood profile/install auditors, plus selected execution-failure
checks, with four-GiB/180-second jobs. During every finalization an observer
compares the whole old/new extent while both are owned; it retains no mutable
alias after successful publication. Existing independent arithmetic, bridge,
persistence and installation checks supply their own authority obligations.
Source, job identity, failed attempts and measured peaks belong in the
[minimal evidence](../../evidence/minimal/FP_CUDA_FRAME_STORAGE_AUDIT.json).
Neither fixture alters the fixed n8 matrix or upgrades any old n16 failure.

At `c133008`, both actual profile fixtures seal and install at cursor22,
with566 independently checked CUDA and566 binary64 phases in total,80 fresh
score checks and94 likelihood commit-operation tapes. Their whole-frame
comparisons cover148,373,504 bytes. Both constructor classes stay UNRESOLVED.
Six additional CUDA failure workers pass: the existing frame-cap/combined
faults and new expected/unexpected publication, copy-MemoryError and original
executor-error precedence checks. The new cases retain the received target
and prevent failed-phase acceptance. Both actual copies stay paid except for
the terminal, only partly materialized MemoryError diagnostic prefix.

The two initial host jobs fail while serializing a read-only peak mapping,
after the storage routine returns. Their jobs and counters remain retained
without scored fixture results. A two-frame diagnostic reproduces
`TypeError: Object of type mappingproxy is not JSON serializable`.
The correction converts only the report mapping to dict; Runtime, counts,
caps and deadlines are unchanged. Repeat only these host jobs. Model worker
6920 was observed live during and after the CUDA batch; no exclusive-device
throughput or timing claim is made.

The corrected host jobs at `5d58bc2` both finish within the unchanged caps.
Each compares268,435,456 frame bytes across its two complete snapshots.
The legacy fixture retains384 distinct one-MiB payloads; the immutable one
retains128. Their job peaks are432,934,912 and163,622,912 bytes respectively,
a269,312,000-byte reduction (62.2%) in this fixed fixture. The registered
packed peak increases by exactly one MiB, from134,222,983 to135,271,559 bytes,
because copy coexistence is paid even though actual host use falls. This
distinction between an honest owned reservation and physical snapshot cost
is part of the result. It does not establish whole-model memory or time.
