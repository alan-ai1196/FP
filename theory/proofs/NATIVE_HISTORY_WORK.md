# Retaining history and repeatedly traversing history are different obligations

Status (2026-10-02): **source-derived quadratic lower laws; finite actual-Runtime
count audit passes; no elapsed-time, full-budget or replacement-runtime claim**.

This concerns the complete ordinary token path at production source `2e5f4f6`.
The closed [source-compilation pair](../../experiments/next_token/NATIVE_STREAM_COST_A1.md)
reduces early sixteen-target time by 17.17014%, but says nothing about growing
history. The following obstruction follows from the actual implementation,
independently of vocabulary size, serializer speed or a presumed profiler share.

## 1. Exact source-history law

Consider T successful consecutive ordinary predictions/observations from cursor
zero, with the fixed token source reader and no intervention replacing the
Runtime implementation. At prediction i, `_observations` contains exactly i
revealed records. `_predict_received` passes `tuple(self._observations)` to
`read_sources`, which verifies each record's cursor and revealed target before
selecting the fixed L-token lag window.

The tuple conversion copies exactly i reference slots. Since the valid-prefix
test succeeds, its `any(...)` visits all i records; it cannot short-circuit on
the successful path. Consequently these two loops separately perform

    sum(i for i in range(T)) = T(T - 1)/2

reference copies and row checks. The context-window work is additional. At the
declared T=1,048,576, **549,755,289,600 copied slots and the same number of checked
rows** follow from source. This is not a million-target execution measurement.
The existing `indexed_source_read_work` explicitly prepays the cursor-dependent
work; a large paid work cap does not make its actual execution constant-time.

Every old observation remains relevant to possible legal future queries/profile
construction. Truncating the stored history to the current lag window is not a
solution. The issue is repeated derivation of an already owned complete prefix,
not proof that the rest of that prefix may be forgotten.

## 2. Two separate ledger-history lower laws

Let E0 be the initial live ledger event count. Each successful `begin_context`
appends an information-work event before calling `prepare_allocation`.
`prepare_allocation` calls `_detached`; its `list(self._events)` copies the full
event list. Completed ordinary transitions retain every event. Thus its one
mandatory clone at prediction i copies at least E0+i+1 event slots. Across T
events this is at least

    T(E0 + 1) + T(T - 1)/2.

Other clones and the copying of object maps, reference maps, retired identities
and owner metadata only add cost. The source-compiled stream candidate does
not change any of these operations.

After an ordinary observation, Runtime releases retired learner leases, calls
`self._ledger.snapshot()['objects']`, and filters `_buffers` by these keys.
The snapshot first checks all live leases, then materializes and recursively
freezes **all** ledger events, objects, owner assignments, retired identities,
work and peak counters. Only the object keys are used at this call site. It
visits at least E0+i+1 events per observation, giving the same cumulative lower
bound on event-row materialization alone. The diagnostic does not grant
feasibility or publication authority; it nevertheless performs a valuable
live-lease consistency check that an optimized path must preserve.

These are lower bounds on different traversals, not an additive wall-time
profile or an FP semantic lower bound. Both hold for any successful prefix in
the stated implementation, including before its first optimizer commit. They
do not claim that all actual runtime cost is quadratic, that every family
performs exactly these counts, or that a particular wall deadline must fail.

## 3. Exact finite audit of the real call graph

[`audit_native_history_work.py`](../../scripts/audit_native_history_work.py)
wraps actual `_detached`, `_residency`, `snapshot` and `read_sources` calls, records
their input cardinalities and delegates to the original functions unchanged.
It does not replace a check with a counter or time a reduced surrogate learner.
Diagnostic endpoint snapshots occur outside the observer.

All sixteen binary four-target histories, in packed and shared storage, give
identical complete serialized snapshots with/without instrumentation. Two
additional paired 64-target histories retain the update-unit512 declaration.
The **34 paired histories** agree in complete learners, bytes, sources, event
traces, resource events and identities. The nonce is fixed only inside these
isolated CPU comparison roots. Their declared allowance is 128 MiB reference
payload and 10^15 work per role; the ordinary toy helper's smaller work cap was
insufficient for the shared 64-event counting control. No corpus or Torch is
opened, and this is not a performance/budget experiment.

The [minimal receipt](../../evidence/minimal/FP_NATIVE_HISTORY_WORK_CPU.json)
records the packed controls too. The shared 64-event path gives:

| Completed targets | Source slots copied (also rows checked) | Ledger event slots cloned | Ledger event rows snapshotted | Live-object residency visits |
| --- | ---: | ---: | ---: | ---: |
| 8 | 28 | 1,854 | 2,248 | 15,100 |
| 16 | 120 | 6,910 | 7,696 | 53,220 |
| 32 | 496 | 26,622 | 28,192 | 198,580 |
| 64 | 2,016 | 104,446 | 107,584 | 765,780 |

At 64 targets the owner still retains all 3,256 resource events and 781 live
objects. Exactly 64 mandatory clones originate in `prepare_allocation`; exactly
64 internal snapshots originate in `observe`. No externally requested public
snapshot is counted. These finite values corroborate the source-derived laws;
their coefficients are not extrapolated to the full-V/commit path.

## 4. What this licenses, and what remains to prove

The frozen Foundation permits changing how complete information is represented
or inspected, with its changed physical costs declared. It does not require
reconstructing a complete diagnostic value each time one internal projection
is needed. The immediate narrow candidate is to obtain live buffer membership
without materializing the unused event diagnostic, while preserving the same
live-lease check, publication order, retained events and public snapshots.
That projection must be proved equivalent on the reachable trusted ledger
state and tested against complete snapshots and terminal failures before use.

Removing that one traversal would not solve the source-history, ingress-clone,
object-map or live-residency terms above. Further changes need an owned complete
state invariant, not an unchecked cached total or a retained suffix. No new
semantic architecture action, information interface, numerical shortcut or
certificate class is licensed. The goal remains an affordable complete ordinary
next-token learner; relation/precision and compiler-flag branches stay closed.

Subsequent implemented refinements: [ordinary ledger projection](ORDINARY_LEDGER_PROJECTION.md)
removes the diagnostic event traversal; [owned prefix/admission](OWNED_PREFIX_ADMISSION.md)
removes the two source-prefix traversals and discarded ingress clone. The
remaining full-object scans/copies still give growing-state lower laws. This
audit explicitly binds its historical prediction/observe methods when rerun;
its original receipt remains evidence about that source, not a current count.
