# Complete resource transitions from local owned changes

Status (2026-10-03): **implemented; exact map/ledger/Runtime and scoped CPU
regression qualification passes; no timing or actual CUDA claim**.

The [owned-prefix refinement](OWNED_PREFIX_ADMISSION.md) removed observation
scans and unused ingress ledger clones. Allocation, sharing, release, frame
relocation and ordinary publication still scanned/copied growing object maps.
The remaining issue is a common state invariant, not a collection of cheaper
special cases. This refinement preserves every object, lease, event, byte and
mapping insertion order while changing how local successors are prepared.

## 1. The exact role-support resource law

For each live object j let b(j) be its complete nonnegative integer resource
vector. Let n(j,o) be the positive lease count of owner o, whose registered role
rho(o) never changes. Define

    S(j) = {rho(o) : n(j,o) > 0},
    w(j) = (b(j), (1[r in S(j)] b(j)) for every registered role r).

Then the exact global and per-role residency vector is W = sum_j w(j). Global
cost counts each physical object once; a role counts it once whenever at least
one of that role's owners has a live lease. Lease multiplicity and the number
of same-role owners do not multiply its physical cost.

If a checked transition changes only K object entries, write absent entries as
zero. Its exact resource law is

    W_after = W_before + sum_(j in K) (w_after(j) - w_before(j)).

This follows by cancelling unchanged summands, component by component. It is
an equality, not an estimate or regularizer. Caps are therefore decidable from
the complete new W without scanning unchanged entries, **provided the owned
state invariant establishes those entries and the stored sum**.

Totals alone do not establish admission. The original owner/type/shape checks,
fresh/nonretired identity checks, positive lease counts and original-owner
debit checks still precede publication. For example, with two compiler owners
sharing one object, dropping one owner's last lease need not reduce compiler
residency at all. An atomic transfer also cannot spend a lease acquired by a
different move in that same batch. Both are counterexamples to deciding a
transition from a naive scalar cost delta alone.

## 2. The sum is an inductive representation invariant

`owned_maps.py` implements a private map whose complete values occupy immutable
AVL nodes. Each node contains its own weight and the exact componentwise sum
of that weight and its children's sums. Node constructors compute the sum;
rotations construct new nodes with the same full entries. No caller-supplied
aggregate or cached-validity bit is accepted by Runtime.

Two indices share each full entry: one orders keys for lookup; the other orders
immutable insertion ordinals. Replacement keeps its ordinal; deletion removes
it from both indices; reinsertion receives the next ordinal. Thus dictionary
iteration order survives, including order inside public diagnostics. Equal
sorted serialization alone would not prove this observation preserved.

An update constructs only its search/rotation paths. Both complete indices are
prepared before a single version-pointer assignment. A failed node or version
allocation cannot publish one index without the other. `copy()` creates a new
publication slot sharing old immutable nodes; changes to either slot preserve
the other's full values, weights and order. Map values retain their existing
ownership protocol: ingress bytearrays remain paid mutable bytes, while ledger
entries contain owned specs and immutable lease maps.

Each ledger leaf now stores the **object and all its references together**.
`_set_lease` checks its live owners and computes w(j) from that complete entry.
All allocation, acquisition, partial/last release and atomic-transfer writers
use that construction. Owner roles remain immutable; closure first removes or
verifies the absence of every lease belonging to that owner. Closed/retired
identity sets and owner maps also use complete immutable versions. Peaks and
spent counters retain their original update rules.

The one extent writer outside the old ledger was shared CUDA-frame relocation.
It is now routed through `_shrink_object`, which preserves identity/provenance,
checks a componentwise nonincreasing extent, and rebuilds the affected leaf.
The caller still retains and independently decodes **every byte of the original
frame**, including padding, before the original root/lease publication. This
helper is an implementation of the existing machine relocation, not a semantic
architecture action or a new installation capability.

The complete ledger field guard now names `_leases`, replacing the separate
object/reference dictionaries. The full spec and every reference remain in
that field. `_objects` and `_refs` are read-only projections; they do not own a
second authoritative copy. `_residency` uses the augmentation only for paired
projections of that same private map. Its independent generic-map scanner
remains available; audits explicitly force that scanner on complete leaves.

All historical resource events remain in an immutable reverse-linked log.
Appending creates one node and a new log root. Detached transactions can share
that root without copying old history or aliasing future appends. Full forward
diagnostics still reconstruct every event in the original order when requested.

The invariant holds by induction from empty roots through every registered
writer. It uses the existing serialized trusted-code and public-value ownership
premises. It does not tolerate arbitrary direct mutation of private nodes,
spec metadata, role bindings or code. Standalone accounting helpers carry no
Compiler/install authority. No resource total supplied by a caller becomes a
Runtime certificate. This is a changed physical representation with exact
logical accounting, not identical host allocation timing or footprint.

## 3. Runtime publication preserves the complete buffer relation

Runtime buffer and ingress-identity maps use the same lossless ordered versions.
The existing complete-root publication points remain in place. Successful
ordinary allocation/retention leaves each owned buffer backed by its paid live
lease; temporary copies are removed only by their existing release protocol.

At ordinary learner publication, only the explicit release batch can remove
objects from that successful predecessor. Therefore buffer cleanup copies the
version root and tests those released IDs, deleting a buffer exactly when its
last lease disappeared. No other buffer is removed or reinterpreted. This is
equivalent to the old whole-buffer membership filter under the invariant.
Ingress and frame relocation similarly fork their complete maps and change
only the admitted entries; no old identity or old frame information is lost.

Owner closure and installation retain their full checks/diagnostics. Those
operations can still deliberately enumerate complete state. Installation still
preserves every actual learner buffer identity, fresh paired evidence, spent
alpha, failed preparation and the original single Runtime-root publication.
The refinement grants no extra continuation or installation authority.

Preparation allocations may fail at different places. New node-preparation
failures leave the predecessor version unchanged. Failures after an already
published ledger change or work debit retain that actual prefix under the
existing terminal host protocol; they are not rolled back or refunded. No
claim is made that every failed physical allocation has a completed buffer.
Target reveal remains irreversible, and a failed target cannot resume as idle.

## 4. Structural cost law and its limits

For a balanced index of M entries, the minimum node count at height h satisfies
N(h) = 1 + N(h-1) + N(h-2), giving N(h)+1 >= 2^(h/2). Lookup/path-copy height is
therefore O(log(M+1)). Rebalancing constructs a bounded number of nodes per
visited level. Two indices preserve insertion order at the same asymptotic cost.

With d resource dimensions and R roles, updating k objects touches
O(k d(R+1) log(M+1)) augmentation coordinates, plus validation of the changed
objects' actual owner lists. Complete-root copying shares immutable maps and
logs; bounded role/peak/spent dictionaries still copy their own coordinates.
Event append takes constant node work. Buffer/ingress map updates have the
same logarithmic path bound without resource weights. Comparisons, integer
bit costs and value materialization are additional; this is not a CPU-cycle law.

For a fixed ordinary registration with bounded objects/leases changed per
event, the growing-map bookkeeping is O(T log(T+1)), rather than the former
quadratic object scans/copies. Every retained value still costs actual space.
Public snapshots, old-record queries, owner-wide cleanup, installation checks,
serialization/decoding, numerical work and compiler search are outside that
bookkeeping bound and remain charged/executed. **The complete Runtime is not
proved O(T log T), and no full-training budget follows.**

The actual 64-target shared control forbids all `OwnedMap` iteration methods
and resource-log iteration during ordinary execution. It succeeds, constructs
99,086 index nodes, and retains all 781 live objects, 64 observations and 3,256
events. The previous source counted 765,780 full residency-object visits there.
These are different operation categories, not a speedup ratio. Public endpoint
checks independently scan all leaves and actual buffers after instrumentation.

## 5. Executed evidence and next decision

[`audit_owned_maps.py`](../../scripts/audit_owned_maps.py) checks the storage
invariant independently of FP accounting: 14,400 complete five-key insertion/
deletion paths, 72,600 permutation state checks, all 79 ordered three-key/two-
value states and 711 decisions. A 4,096-operation seeded control preserves 64
old versions and checks exact height/node-work bounds. All 34 selected node/
version allocation failures preserve both old indices; 1,024 full event-log
versions remain unchanged. See [receipt](../../evidence/minimal/FP_OWNED_MAPS_CPU.json).

[`audit_owned_transitions.py`](../../scripts/audit_owned_transitions.py) uses the
complete historical ledger and changed Runtime methods from Git `a694441`.
The source loader includes the old external frame-extent writer, not only a
new checker shared by both arms. Its [receipt](../../evidence/minimal/FP_OWNED_TRANSITIONS_CPU.json)
records:

- 192 legally constructed lease states and 30,720 transitions: 8,149 accepted,
  22,571 refused. Complete snapshots, object/owner/reference order, peaks,
  spent work, events, first error type/message and detached-fork behavior agree.
  Every new total is also recomputed by the original full-leaf scanner.
- 98 paired packed/shared Runtime histories, 512 targets per arm, with identical
  complete outputs, serialized snapshots, buffer bytes and insertion order.
- 35 failures at every constructed-node position in six ledger operations,
  a paired common Runtime event-append failure, and actual pre-input/post-target
  node-allocation failures. Prefix/authority controls pass.
- Six paired CPU tensor-owner histories: all 129 full phase bodies, 5,774,243
  bytes and 50,279 primitive words, frames, reads, learners, reports, allocation
  totals and retirements agree. This is no actual CUDA execution.
- The global-iteration prohibition also passes sixteen native targets/eight
  commits in packed/shared storage and four CPU tensor targets/eleven phases,
  including complete relocation of 524,789 frame bytes. It is not restricted
  to a precommit prefix.

The [scoped regression receipt](../../evidence/minimal/FP_OWNED_TRANSITIONS_REGRESSION_CPU.json)
records nineteen complete existing scripts passing, including finite searches,
profiles, fresh paired persistence, two consecutive CPU installs, public-value
attacks, real host exhaustion, shared retention and native reporting. Original
history/projection/admission scripts reproduce their recorded results with
historical ledger writers bound; no old receipt is overwritten.

One historical storage script's AST gate fails: it requires constructor/snapshot
identity with `b0c409c`. The snapshot already differs at parent `a694441` and is
unchanged by this refinement. That historical gate remains intact. Its existing
operational frame checks are factored out and pass separately: 33 full frames,
all 256 byte values, two unpaid-copy refusals and four prepublication failures.
This does not reissue that old source-identity or device qualification.

The next evidence must concern the complete ordinary-text path and its resource
budget. Do not infer wall-time gains from removed visits, reopen a static or
relation family, or replay a closed journal. The earlier negative timing result
remains unchanged. No Foundation/ERC definition or certificate class is added.
