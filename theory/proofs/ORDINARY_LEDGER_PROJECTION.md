# Ordinary live-buffer projection without rebuilding the resource diagnostic

Status (2026-10-02): **implemented; exact CPU/full-V correctness checks pass;
original cost pair is slower; no actual CUDA or affordable-training claim**.

The [history-work result](NATIVE_HISTORY_WORK.md) identifies an internal
`snapshot()['objects']` call after every ordinary target. The caller uses only
membership of live object IDs, but the snapshot reconstructs and freezes the
entire resource event history. This change removes that unused derivation, not
any retained state or any input to a future continuation.

## 1. Reachable-state projection lemma

Let L be a reachable private `ResourceLedger` in the registered trusted Runtime.
Its object keys, owner IDs, role IDs and retired IDs are immutable strings;
resource vectors and reference counts are validated integer maps; events are
the complete `ResourceEvent` records appended by its fixed methods. Public
Runtime values are detached and cannot mutate these private objects.

After the unchanged `release_many` succeeds, the old ordinary path computes
`L.snapshot()['objects']`, then keeps each owned buffer exactly when its key
belongs to that map. `snapshot` begins by calling `_residency(L._objects,
L._refs)`. It then builds the diagnostic object's dictionary from every key of
`L._objects`; recursive freezing changes neither the keys nor membership.

The new path calls **the same `_residency` with the same inputs at the same
point**, then tests membership directly in `L._objects`. Under serialized calls
no ledger mutation occurs between that check and the unchanged buffer filter.
Therefore both successful paths keep the same buffer objects in the same
order, with the same leases, counters, historical events and root fields. The
subsequent candidate/device publication and return value are unchanged.
Induction over ordinary transitions gives equal complete successful states;
every subsequent legal query, profile, persistence, install or public diagnostic
therefore still has the same retained inputs. No history quotient is taken.

The reachable-state premise matters. This is not an equivalence for arbitrary
corruption of private event metadata or replacement of trusted ledger code.
The omitted recursive freezer could reject unsupported private metadata; the
registered ledger constructors/mutators cannot produce that metadata. The new
path continues to detect empty/nonpositive leases and unknown/closed owners
through exactly the old live-lease check. It grants no new resource authority:
all allocation/coexistence checks, work charges and target-retention duties
remain in their original positions. Public `snapshot()` still builds the whole
diagnostic when actually requested.

## 2. Failure and cost relation

Original and replacement paths share the actual predecessor, target reveal,
phase construction, release batch and residency check. An injected failure at
that common check therefore preserves the same failed prefix and denies the
same continuation. MemoryError still reaches the existing terminal host guard.
No check is moved past learner publication, no rollback is added and no new
helper/selector/public endpoint is introduced.

The deleted diagnostic allocations can change host allocation failure timing.
The claim is successful-state refinement under the declared physical execution,
not equal MemoryError timing or equal wall time on every input. Actual host
limits still apply to remaining operations. Original conservative work charges
are not reduced. The change deletes ordinary event-row diagnostic construction,
but keeps every live-object residency visit, ingress ledger clone, old-source
copy/check and buffer-membership iteration. It does **not** make the complete
Runtime linear in horizon or establish a full-training budget.

## 3. Executed evidence

[`ledger_projection_audit_support.py`](../../scripts/ledger_projection_audit_support.py)
loads the exact historical `observe` AST from Git source `364934d` and reapplies
the unchanged host/public-value guard. The baseline retains the original full
method; it is not a weakened learner. Both arms use actual current Runtime
registration, checks and storage, with the sole production change localized to
the internal membership computation. The historical history-count audit binds
that original method as well, so its old law remains reproducible.

[`audit_ledger_projection.py`](../../scripts/audit_ledger_projection.py) and its
[minimal receipt](../../evidence/minimal/FP_LEDGER_PROJECTION_CPU.json) establish:

- 34 paired complete histories: all sixteen binary four-target streams in
  packed/shared storage plus two 64-target/unit512 histories. Entire serialized
  snapshots agree, including buffers, learners, metadata, events and identities.
- In the 64-target shared control, 107,584 internal snapshot event rows vanish;
  all 765,780 residency object visits and 104,446 ledger-clone slots remain.
  All other counted traversals agree. The packed comparison agrees too.
- Twelve paired post-release controls cover empty/zero leases, unknown/closed
  owners, ResourceExceeded and MemoryError in both representations. They retain
  the target and prior learner, yield identical full failed diagnostics and
  forbid continuation. Synthetic invalid leases are restored only to inspect
  terminal diagnostics; neither trajectory resumes.
- Six original storage failure controls still preserve targets/prior learners.
- Six paired CPU tensor-owner histories preserve all 129 phase bodies/5,774,243
  bytes/50,279 primitive words, full frames, learners, reports, raw reads,
  allocations and retirements. No actual CUDA context is initialized.

All four existing complete native event/query, finite-run, CPU install and
caller-isolation regression scripts pass; the separate
[receipt](../../evidence/minimal/FP_LEDGER_PROJECTION_REGRESSION_CPU.json) records
960 exact gradients, 64 exhaustive context/target streams, 512 two-lineage
recurrence targets, 28 finite run streams, 2,016 lease cases, actual CPU installs
and the caller-mutation/failure controls. The new cost harness also passes.
This is scoped evidence,
not a reissue of the historical whole CPU/CUDA release. The next bounded native
[cost comparison](../../experiments/next_token/LEDGER_PROJECTION_COST_A1.md)
keeps full declarations, 256 original text targets and all byte/ownership checks.
No score comes from its incomplete training prefix.

## 4. Actual cost result: deleted visits did not yield a measured speedup

Both original 256-target workers at `bb8c900` pass the complete uncompiled
image/record oracle: 521 images and 1,285 records/15,688,733,248 decoded bytes
per arm. All paid counters agree. Ordinary time rises from 311.3773001 to
374.3902031 seconds (**20.23683%**), while job peak changes from 553,193,472 to
551,518,208 bytes. The unchanged prediction path also slows in this one ordered
pair. The cause is not isolated; no timing-variation or runtime-interaction
explanation is asserted. The negative observation remains evidence.

Keep the source-level simplification and its exact count/failure result, but
do not call it a measured acceleration or extrapolate a training budget. The
journal is closed, with no retry/variant sweep or separate device qualification
selected by this result. The source-prefix and discarded ingress-preflight
copies are the next concrete growing-history obligations; no old information
may be discarded to remove their execution cost. They are now addressed by the
separate [owned-prefix/admission refinement](OWNED_PREFIX_ADMISSION.md), with
global object work still unresolved and no new timing claim.
