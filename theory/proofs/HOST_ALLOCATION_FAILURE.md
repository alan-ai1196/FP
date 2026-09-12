# Host allocation failure is a terminal authority boundary

Status: **historical executed fault counterexample; scoped failure invariant;
implemented public Runtime boundary; actual Windows commit-limit audit.**
Foundation/ERC-1 remain frozen. Runtime is NOT FROZEN and science HOLD.

## 1. Cleanup is not a complete-state recovery proof

At `dfa1583`, `_construct` published a new candidate, its program and attempt
before allocating its `ConstructionResult`. A `MemoryError` at that last
allocation ran the generic cleanup: the candidate owner was closed and all
its learner buffers were freed. The candidate entry itself remained. The
public method's `finally` restored the idle phase.

The audit executes this original Runtime/machine source from Git and injects
one allocation fault at the result constructor. First execute an ordinary
event on the empty-SUM baseline, retaining its code as required. Construct
another instance of that same legal native program. After the failed result
allocation, the snapshot contains the second candidate with a closed owner
and none of its learner buffers. The next public `predict_next` nevertheless
returns predictions from **both** candidates: the already retained program
reference lets the orphaned candidate pass the code-retention path. This is
an executed ownership/continuation mismatch, not a hypothetical memory estimate.

The allocation site is fault injected in trusted code; this does not pretend
that a naturally occurring CPython object allocation failed at that exact
instruction. No owned Runtime state or caller-supplied certificate is injected.
Section 4 separately exercises an actual allocation refusal from the OS.

The lesson extends beyond this publication order. Even allocating a failure
record, ledger snapshot, cleanup list or exception message can fail after the
first allocation failure. Ordinary paid `ResourceExceeded` is a checked
machine-budget outcome with an available interpreter. Host exhaustion cannot
borrow that assumption to promise rollback, cleanup or resumable authority.

## 2. One existing state coordinate closes all public authority

Machine `packed-reference-payload-v5` retains v4's encoding and v3's ingress.
`host_failure.py` registers a common boundary on all public Runtime methods.
Every internal broad exception handler first propagates `MemoryError` without
entering its allocating recovery path. The outer boundary writes a precreated
immutable host-failure marker into the existing `_halted` slot, sets the
existing phase slot to `halted`, and propagates the original exception.

Marking creates no diagnostic tuple, error string, root copy or cleanup plan.
It neither frees owned objects nor changes alpha, cursors or recorded costs.
The marker itself is created when trusted code loads. Replacing an existing
dictionary value does not require dictionary resizing in the registered
[CPython 3.12.9 implementation](https://github.com/python/cpython/blob/v3.12.9/Objects/dictobject.c).
This supports the two existing-slot writes; it is not a theorem that arbitrary
Python exception machinery, traces, caller callbacks or finalizers require
zero memory. Those are not added to the serialized trusted machine contract.

The boundary checks this marker before calling any continuation or authority
method. That includes construction, ingress/observe, queries, searches,
persistence reads/cancellation, proof verification and CPU installation.
An inner `finally` restoring its phase cannot restore public authority.
The original unguarded method is not published as `__wrapped__`.

Passive snapshots remain available **if** their own allocation and decoding
succeed. A terminal prefix can include partially staged objects or incomplete
ledger publication. It is not certified to be a valid continuation state, and
the marker does not make a general snapshot/crash-recovery guarantee. Immutable
contract/identity properties are data, not continuation tokens. Constructor
exhaustion does not return a usable Runtime.

Construction now prepares its result before publishing the candidate. This
also removes the particular old fallible-result ordering. It does not replace
the common failure rule: other allocations can fail after state changes,
including target observation, ledger history and installation preparation.

**Scoped terminal-authority proposition.** In the registered serialized
CPython Runtime, suppose a public method body raises `MemoryError` and control
reaches the common boundary. Every internal broad handler propagates it;
the two existing-slot writes install the terminal marker. Each subsequent
public continuation/authority method checks that marker before its body and
therefore cannot advance a learner, read a new event, issue/verify a current
proof, reuse persistence or install a candidate. Passive snapshots cannot
issue such authority. The marker is never reset by a legal method. Induction
on subsequent public calls establishes the claim without inspecting or
discarding the failed prefix. No inference of semantic infeasibility follows.

This does not certify arbitrary asynchronous interruption, process crashes,
malicious Python reflection or native failures that do not surface through
this exception boundary. A process that cannot unwind to the boundary must
not have its external outputs promoted into a valid completed run. Complete
process supervision and run-level publication remain separate obligations.

## 3. Audited failure prefixes and current-proof closure

`scripts/audit_host_allocation_failure.py` covers:

- The original orphaned-candidate prediction and the corrected retained,
  terminal prefix. No cleanup-after-OOM success is assumed.
- All 22 continuation/authority ports, with 352 repeated refusals that do
  not grow or rewrite owned state. The source audit checks all 20 internal
  broad handlers have an immediate `MemoryError` propagation branch.
- Allocation failures in ingress, prediction, observation and snapshot
  results, plus a ledger-event failure after a work debit. Revealed history
  and paid work remain; a completed target event is not rewound to unread.
- Every one of the four packed-writer and eleven ledger-event calls on the
  registered empty-SUM construction path, each failed in a separate run.
  Four cases retain unfinished reservations and one leaves an actual buffer
  after its ledger release. Those terminal snapshots are not treated as
  coherent continuation states. This enumerates these hook sites on this
  path, not every Python allocation instruction or every native program.
- An existing completed native search whose proof remains historical data
  after a snapshot allocation failure, while current verification is closed.
- An actual selected candidate with four continuous CPU learners and paired
  persistence, followed by failed CPU-install result allocation. Deployment,
  complete learners and persistence history stay at the old root; alpha and
  actual installation work stay spent. Neither pairing nor retry can revive
  current authority after the host failure.

An ordinary checked payload/work refusal keeps its previous semantics. It
does not automatically become a whole-Runtime host failure. Existing reference,
binary64, persistence, construction and CPU-install audits exercise these
ordinary success/failure paths as well.

## 4. Actual kernel refusal, without a packed-memory fiction

The disposable Windows audit child is created suspended and without a visible
window, attached to its own job, and resumed only after its registered limits
are read back. The job supplies a 64 MiB process/job commitment cap and an
active-process cap. Breakaway is not enabled. The launcher never assigns the
Codex/user host process to that job. All handles belong to the audit and a
failed setup cannot leave a suspended child behind.

The child executes unmodified `begin_context` with a declared 128 MiB context
window, a 1 GiB packed cap and enough reference work. Thus the abstract budget
permits the window; its actual byte allocation cannot fit the job cap.
The OS refusal raises `MemoryError`. The public boundary marks the Runtime
terminal before any input byte arrives, with the initial learner unchanged
and 536,870,993 reference work units still recorded. Packed peak remains only
1,823 bytes. The observed job commitment peak is about 28 MiB, below its
64 MiB cap, because the 128 MiB commitment was refused.

This is **not** post-hoc polling used as admission. The memory-limit mechanism
rejects a commitment that would exceed its cap; the query records its tracked
peak. These are the semantics documented in the Windows
[basic limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
and [extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).
The audit uses no memory-limit notification as a correctness premise: Windows
explicitly does not guarantee delivery of all ordinary job notifications in
its [completion-port documentation](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port).

The evidence retains aggregate user/kernel CPU time and all OS-reported
process associations rather than assuming the count equals our one explicit
launch. Even the empty-worker diagnostic on this host reports two associations;
their individual origin is not inferred. The SDK count includes failed
associations, as specified in
[job accounting](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information).
CPU time is measured here, not enforced as an exact execution-time cap.

## 5. Remaining physical closure

The compact evidence is
[`FP_HOST_ALLOCATION_FAILURE_AUDIT.json`](../../evidence/minimal/FP_HOST_ALLOCATION_FAILURE_AUDIT.json).
Run `python -B scripts/audit_host_allocation_failure.py --write` on 64-bit
Windows; the three non-OS sections are also independently runnable.

The job experiment demonstrates a central commitment bound covering allocation
sites beyond packed buffers, including ordinary interpreter workspace. It is
not yet a production Runtime manifest field, resource-role attribution,
total-machine/RSS theorem, complete process-supervision protocol or error
authority spanning terminated runs. The launcher and external producer are
outside the measured child scope; that exclusion must not become free
Compiler state in a complete experiment. Shared/platform/device resources
and installation coexistence still require the registered full machine.

This supplies a necessary failure rule for that integration: unverified
recovery cannot preserve continuation authority merely because cleanup was
attempted. It introduces no source, value or graph action and reopens no
Foundation theorem. ERC-1 stays frozen, static cases stay parked, and full
Runtime/host registration precedes target AMP correctness and RTX 3090 science.
