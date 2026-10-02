# Owned prefixes and allocation admission without discarded history copies

Status (2026-10-02): **reachable-state refinement implemented; exact finite CPU
checks pass; no actual CUDA, measured speedup or affordable-training claim**.

The [history-work result](NATIVE_HISTORY_WORK.md) found repeated complete
observation scans and a complete ledger clone whose successor is discarded.
The [ordinary ledger projection](ORDINARY_LEDGER_PROJECTION.md) removed a
separate unused diagnostic. Its negative timing result remains evidence.
Here the next two traversals are removed together, without forgetting history,
introducing a validity cache or changing the registered work allowance.

## 1. Inductive ownership replaces repeated source-prefix validation

Work in the registered, serialized Runtime with its existing inward/outward
[value isolation](PUBLIC_VALUE_OWNERSHIP.md). Private code and owned Python
metadata are trusted; arbitrary private mutation, asynchronous interruption
and concurrent calls are outside this claim. Retained physical evidence and
all existing numerical/bridge checks remain part of the execution.

Let H be the complete `_observations` list and c the ordinary cursor. At every
legal entry to ordinary prediction:

1. H has length c, with record i at position i for 0 <= i < c.
2. Each such record has cursor i and an already revealed integer target in the
   registered alphabet.
3. These records and their source contexts remain owned and unchanged. Public
   results do not furnish a mutable alias to them.

**Induction.** Construction creates the empty list at cursor zero. Prediction
creates its pending record with cursor c but appends nothing to H. The sole
append site is `observe`: it first requires the preceding prediction, checks
the target's exact integer type/range, replaces the pending record's target,
sets phase `observing`, and appends that record. Successful completion advances
c by one and restores `idle`. No other registered control, query, profile,
install or reporting operation mutates H's old records or advances this cursor.

An exception after the append can leave length c+1 with the old cursor. This is
not a successful prediction predecessor. The ordinary handler or host guard
halts; even an unexpected failure in the immediately preceding data-use record
call leaves phase `observing`, so `begin_context`/`predict_next` and a second
`observe` are denied. There is no registered resume/reset port making that
partial prefix idle. Failures exporting a completed public result also end
continuation authority. Thus none supplies a counterexample to the invariant
at a subsequent legal prediction. Invalid target submissions before append
leave the preceding valid state intact.

For the registered token source family of context width L, source extraction is
therefore exactly

    past[lag - 1] = missing_token          if lag > c
                    H[c - lag].target    otherwise,
    for lag = 1, ..., L.

The Runtime constructs the same `TokenContext` using the **owned
`data.source_reads.family` object**, preserving both value and alias topology.
Its full constructor validation and the subsequent source-domain, lineage,
range, prediction and numerical checks are unchanged. The constant-size
`len(H) == c` guard also remains. The prior successful full-prefix predicate
is entailed by the invariant and has no mutable effects; omitting its scan and
the preparatory tuple copy gives the same complete successful state.

This does not authorize taking a suffix as the complete state. Queries and
profiles can still name records older than L, with their original contexts,
targets and information-use records. All H remains stored. The standalone
`read_sources` helper still validates every supplied record, because arbitrary
caller-supplied histories do not inherit the Runtime invariant. Non-token
source extraction still uses that helper unchanged. No new bit asserts that
history is valid, and no public helper issues source or continuation authority.

The original `indexed_source_read_work` debit still precedes any context
construction or historical target read. Its conservative 2c + 3(L+1) allowance
is unchanged, as are its refusal and retained-ingress behavior. This result
does not reinterpret the experiment's paid work counter as actual CPU cycles.

## 2. Preflight is a checked decision, not an unused successor

Write A(L, owner, specs) for the existing allocation checker on a reachable
typed ledger. In its original order it:

1. checks that the owner is registered and open;
2. copies the current object/reference maps into a proposed coexistence set;
3. checks each proposed `ObjectSpec`'s complete resource dimensions and rejects
   duplicate, existing or retired identities;
4. adds the new positive lease, then checks every proposed live lease, owner,
   global dimension and role dimension against the registered limits.

The original `prepare_allocation` first checks the ledger's exact complete
field set, clones **all** ledger state, runs this allocation, updates the clone's
peaks and appends a clone-local event. In ordinary `begin_context` the returned
ledger is discarded. Its admission check precedes creation of the ingress
window, and actual allocation then runs again on the owned ledger.

For typed reachable state, the clone has identical owners, limits, IDs, objects
and leases; copying these immutable values and mutable containers introduces
no logical change. Hence A on that clone has the same successful answer or
first checked refusal as A on the predecessor. Clone-local peak/event updates
after successful checking cannot introduce another contract refusal on this
state class and are never published. They can incur host allocation failures.

`_allocation_plan` is the original checker moved into one shared implementation.
Both actual `allocate` and `check_allocation` call it. The new preflight first
applies the **same exact ledger type/field guard**, then discards the plan and
returns `None`. It changes no ledger, peak, event, debit, buffer or Runtime root.
Actual allocation still reruns A, records its peak/event, and precedes ingress
publication. No saved plan or admission token can bypass a later resource
check. `prepare_allocation` keeps its original full-successor semantics for
callers needing that result; physical transfer/install preparation is unchanged.

The exact preflight decision class is complete typed proposals against the
current reachable ledger: the named owner must be live, all IDs fresh, all
dimensions complete, all resulting leases positive, and every global/role
residency cap satisfied. This is a resource admission decision, **not** a new
`CERTIFIED_COMPLETE` search, persistence, installation or model claim.

Failures at common checks retain their original order. Deleting scratch
allocations can change where actual `MemoryError` occurs, so equal host-failure
timing is not claimed. The existing host guard still makes any such failure
terminal without a resource refund. The equivalence does not cover malicious
replacement of private typed maps/events or trusted methods. Full diagnostic
and physical-byte checks still run where the registered execution requests them.

## 3. Exact work deletion and the remaining obstruction

For T ordinary successful token predictions, the two old full-prefix traversals
each visited T(T-1)/2 slots/rows. They are now absent. The number of actual old
target reads is exactly

    sum(min(i, L) for i in range(T)),

which is T(T-1)/2 for T <= L, and LT - L(L+1)/2 for T >= L. Context construction
and validation still cost O(TL) visits; integer-bit costs are separate. For the
million-target/L512 declaration, the reads are 536,739,584, not the old
549,755,289,600 visits for each unrelated copy/check loop.

The mandatory ingress preflight no longer clones growing event, retirement,
owner, spent or peak containers. On the exact 64-target shared control, this
removes 104,446 ledger-event slots, in addition to 2,016 source-copy slots and
2,016 source-validation rows. All 64 observations and 3,256 ledger events remain.
The context reader accesses exactly 186 old targets. The earlier projection has
already removed ordinary diagnostic event materialization.

**The complete Runtime still has quadratic growing-object work.** Preflight
and actual allocation still copy all live object/reference maps and traverse
the entire proposed coexistence set. `release_many` still copies live maps and
retired IDs; ordinary publication still filters all buffers; ingress still
copies its identity map. Successful retained events add live objects. Even
one full-object check per ordinary prediction then gives a quadratic cumulative
lower law. The audit still counts **765,780 residency object visits at 64 shared
targets**, exactly the previous count. These are implementation traversal
facts, not an FP semantic lower bound or proof that a wall deadline must fail.

The clean stopping point for this refinement is source/state equivalence and
exact work deletion. Another isolated early-prefix timing pair is not selected.
The remaining growing-state operations must be addressed as a complete owned
transition problem before a new full-budget claim; an unverified running total
or omission of historical evidence would not satisfy it. Ordinary next-token
training/reporting remains the objective. Foundation/ERC and relation closure
are unchanged.

The subsequent [complete local-transition refinement](OWNED_LOCAL_TRANSITIONS.md)
implements the shared object/lease invariant, preserving full information and
order while removing those remaining ledger/buffer scans and copies. Its
bookkeeping bound and qualification are separate; this receipt retains its
original source/count scope through historical ledger binding.

## 4. Executed audit and its limits

[`owned_admission_audit_support.py`](../../scripts/owned_admission_audit_support.py)
extracts the original prediction methods from Git `571af68`, preserving real
module-global bindings and reapplying the original public/host guard. The
admission oracle separately loads that source's original `allocate` and
`prepare_allocation`, so both sides do not merely share the new checker. The
prior history/projection scripts explicitly bind their historical prediction
methods to keep the earlier claims reproducible without overwriting receipts.

[`audit_owned_admission.py`](../../scripts/audit_owned_admission.py) and the
[minimal CPU receipt](../../evidence/minimal/FP_OWNED_ADMISSION_CPU.json) report:

- 40 legally constructed lease states, including retirement, closed owners and
  sharing across resource roles; 4,000 exact decisions (336 accepted, 3,664
  refused). First error type/message and unchanged predecessor snapshots agree.
  Every accepted actual allocation matches the original complete successor.
  Unknown complete-state fields are refused before owner checking. Preflight
  executes with full-ledger cloning actively forbidden.
- 98 paired packed/shared histories, covering all binary four-target histories
  at units 1, 2 and 4, plus both 64-target/unit512 controls: 512 targets per arm.
  Complete serialized results/snapshots agree despite attacks on returned old
  records; the original source-family identity is preserved.
- The 64-target read-boundary control forbids full-history iteration and records
  every indexed access. It confirms the exact 186 reads and the counts above.
- Original queries and sixteen profiles use retained records outside the
  current lag window; 32 ordinary newborn continuations retain original contexts.
  Source funding, ingress admission and target/ingress failure controls pass.
- Four paired failures cover unfunded reads/context allocation, a selected
  missing-prefix corruption, and memory/contract exceptions immediately after
  reveal. Complete failed snapshots agree and ordinary continuation is denied.
  Three malformed caller-prefix inputs still fail the standalone helper.
- Six paired CPU tensor-owner histories preserve all 129 full phase bodies,
  5,774,243 bytes and 50,279 primitive words, frames, learners, reports, reads,
  allocation totals and retirements. No actual CUDA context is initialized.

These are finite exact controls and a conditional source-level proof, not a
whole release, arbitrary-code correctness theorem or measured performance gain.
The [separate scoped regression receipt](../../evidence/minimal/FP_OWNED_ADMISSION_REGRESSION_CPU.json)
records all seven complete scripts passing: owned token learning, indexed token
sources, ingress, reference events, finite runs, CPU installation and the public
value boundary. Assertions were enabled, production source stayed unchanged
during checks, and no historical receipt was overwritten.
