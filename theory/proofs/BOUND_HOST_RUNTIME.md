# Bind resource history to the actual Runtime process

Status: **implemented live host registration, scoped resource invariant,
actual CPU endpoint runs and a late-fence history counterexample.**
Foundation/ERC-1 stay frozen. Runtime is NOT FROZEN; target AMP/science HOLD.

## 1. A shared process arena instead of metadata multipliers

The packed ledger retains semantic object identities, references and work
roles. It does not measure every Python allocation. Machine
`packed-reference-payload-v6` now additionally accepts an immutable
`HostResourceContract` in `ReferenceCompilerRuntime(..., host=...)`.
The declared resource is **private memory commitment of the execution
process**, with its actual Windows process/job commitment fence. It is not
RSS, all physical machine memory, GPU storage or a liveness-optimal encoding.

The physical ownership rule is fixed before the run: deployment and compiler
share the entire process arena. Every byte of its measured private commitment
is charged to both roles, once globally. Thus, for global cap H_g and role
caps H_d,H_c, the registered native fence is

`H=min(H_g,H_d,H_c)`.

No action can choose a cheaper role after an outcome. This is the same shared
ownership convention already used by the packed ledger, applied to a coarser
physical resource. It can be conservative compared with a separately allocated
implementation; it makes no optimum or impossibility claim about such other
machines. Native P/S/edge budgets and packed leases remain separate coordinates.

The process's ordinary Python metadata, temporary copies, arithmetic scratch,
interpreter allocation arenas and caller/driver allocations that consume
private commitment fall under the same kernel fence. They do not need a
guessed per-record multiplier. Freed objects do not refund the lifetime peak
or CPU counters. The shared process CPU observations are also reported for
both roles; these are measured user/kernel ticks, **not a hard CPU-time cap**.
The existing registered reference-operation budgets retain their own meaning.

## 2. Runtime owns the live binding

The input contract contains caps and fixed policies only. Runtime itself
creates `_WindowsProcessHost`; no supplied PID, native handle, callback,
counter dictionary, observation object or certificate can replace it.
The backend is registered for 64-bit Windows CPython.

`QueryInformationJobObject(NULL, ...)` reads the calling process's actual
immediate job, including in a nested job hierarchy; this behavior is specified
by the [Windows API](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject).
The binding requires both commitment limits to equal H, the registered active
process limit, kill-on-close behavior and no enabled breakaway. It verifies
the live limits on every public method entry. Unsupported or unestablished
premises give `HostExecutionUnresolved`, not graph inadmissibility.

The backend also reads the current process's private commitment, its **whole
lifetime** commitment peak, and user/kernel execution times. PID and creation
time bind the resource observation to the same process lifetime. The memory
API explicitly distinguishes current private commitment from the lifetime
peak in
[PROCESS_MEMORY_COUNTERS_EX](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex).
The process timing API sums the threads' respective user/kernel times and
provides creation time in its registered 100 ns representation:
[GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes).

The host policy is included in chi; the live native binding is an owned
Runtime coordinate. `RuntimeSnapshot.host_resources` is a passive observation
of it. This field is explicitly absent for the older `host=None` reference
mode, whose results cannot establish a host-bound resource claim. There is
no unmetered fallback hidden behind a populated host declaration.

Native resource counters are live kernel state. Returned observations are
sampled projections, not a replacement for that state or a certificate that
two processes with equal counters have equivalent future behavior. Process
lifetime counters are not rebased at Runtime creation. Job aggregates are
reported separately; they concern the currently associated job and are not
used as a substitute for process-lifetime history. Observing resources itself
executes work, so repeated host snapshots need not be numerically equal even
when the learner state stays fixed.

## 3. Failure and installation

The existing host-failure boundary now closes all current continuation and
authority ports when the native resource premises cannot be established.
A precreated `host-resource` marker uses the existing terminal slots, as the
MemoryError marker already does. Restoring a failed observation backend does
not revive current proof, persistence or installation authority. Diagnostic
snapshots can still fail if the native observation itself remains unavailable.
If diagnostics subsequently fail with the other host-failure type, the first
host halt marker stays fixed. Both failure orders are exercised by the audit.

Host verification is an entry check. The fixed job enforces commitment
throughout execution; this is not polling used to prevent allocation after
the fact. No allocating post-check is added after CPU installation's unique
root publication. Its frame schema explicitly retains `_host` along with all
learner, search, evidence and resource state. The same process arena therefore
covers installation preparation, coexistence, publication and continuation.

**Scoped resource proposition.** Suppose the registered trusted launcher
installs the fixed H-byte process/job limits before worker execution, and
the registered execution performs no job-policy mutation or breakaway.
The OS commitment limit applies to every subsequent commitment request, not
only allocations with packed object specifications. Therefore the process's
private commitment remains within H and within all three declared caps.
The live binding checks the actual owning process/fence; its lifetime peak
check prevents late registration from discarding an earlier violation.
Host failure cannot turn uncertainty into resumed authority, by the terminal
boundary established in [HOST_ALLOCATION_FAILURE.md](HOST_ALLOCATION_FAILURE.md).
No new graph, source or value operation is needed.

This statement is conditional on the registered native backend/launcher. It
does not certify malicious native mutation of job policy, asynchronous crashes,
arbitrary additional processes or an external supervisor's unaccounted FP
policy. Final run publication and error ownership still need their complete
protocol; an exit status or observation record alone is not that protocol.

## 4. Executed late-fence counterexample

The audit first permits a real 80 MiB transient allocation under a 128 MiB
outer job, then frees it and attaches a new 64 MiB inner job in the **same
process**. Current commitment and the new job's peak are then about 23 MiB.
The process-lifetime peak remains above 100 MiB. All these are actual kernel
readings, not injected counter values.

Thus checking current memory and the new job's peak would falsely establish
a 64 MiB history. The new Runtime binding rejects the registration. A newly
created fence is not permission to erase the prefix it did not observe.
This is a physical-history witness, not a new static FP family or Foundation
counterexample. The old audit launcher already fenced before resumption;
the witness attacks the tempting weaker generalization of that mechanism.

## 5. Endpoint evidence and remaining contract

Run `python -B scripts/audit_bound_host_runtime.py --write`. The small
[`FP_BOUND_HOST_RUNTIME_AUDIT.json`](../../evidence/minimal/FP_BOUND_HOST_RUNTIME_AUDIT.json)
records these actual jobs:

- Unequal global/deployment/compiler registrations (128/96/64 MiB), with a
  real 64 MiB fence. Wrong live caps and four forms of supplied fake/genuine
  counter data cannot construct a host-bound Runtime. A native observation
  fault closes authority before Compiler control mutation or its work debit.
- A registered 128 MiB ingress window that the packed cap permits but the
  actual host refuses. The Runtime halts before input and retains paid work.
- The existing 35-program ordered native class, followed by four continuous
  reference/binary64 learners, fresh paired persistence, CPU installation and
  ordinary continuation, all in the same bounded process. Alpha remains spent.
- The late-fence witness above.
- A child that executes the successful installation path and writes its
  result, then exits with code 17. Its completed-looking file is not accepted
  as a successful completed run.

The audit parent holds the actual process/job handles. It independently
obtains the worker's PID/creation time and final job accounting, and compares
them with the Runtime observations after successful process exit. The output
read is bounded to 8 KiB; malformed/missing/oversized output cannot pass.
This checks the fixed audit worker, not arbitrary untrusted report content.
The precise successful reference decision class remains the existing ordered
constructor endpoints plus deployed baseline, not all parameter values or
all future resource-feasible physical programs.

The private-commitment dimension now has a live production Runtime binding;
it is no longer merely an external memory audit. Complete ERC-1 run/policy
registration, production supervision and publication after worker termination,
error ownership across terminated runs, platform/shared/device resources and
the explicit release-gate mapping remain open. The audit launcher is outside
the measured child; a complete experiment cannot put FP search, learning,
information acquisition or retained policy state there for free.

These remaining boundaries do not invalidate the scoped commitment result
or authorize Runtime freeze. Foundation/ERC-1 remain frozen, static cases
stay parked, and actual target AMP correctness still precedes RTX 3090 science.
